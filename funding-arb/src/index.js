// Arbitrage de prix entre plateformes — mode FANTÔME (aucun ordre réel).
// Chaque minute : lit les perpétuels sur Bybit, OKX, Hyperliquid, Deribit (Binance bloqué), compare les prix du même actif,
// achète (en simulation) là où c'est le moins cher et vend là où c'est le plus cher, seulement si le gain attendu
// après tous les frais atteint l'objectif, avec des prix pris dans les vrais carnets d'ordres pour la mise complète.
import { DurableObject } from "cloudflare:workers";
import { tickComptant, etatComptant, lireComptant, carnetC, fermerManuel } from "./comptant.js";
import { etatComptes } from "./comptes.js";
const VERSION = "2.9.0"
const REGLES_ID = "2.1";;

// Règles (Pitch décide — modifiables ici)
const REGLES = {
  notional: 10000,         // $ par jambe (choix de Pitch)
  gainMin: 50,             // $ net après tous les frais (choix de Pitch : « 50 $ de gain »)
  ecartMaxPrix: 0.10,      // au-delà de 10 % d'écart, ce ne sont pas les mêmes contrats (ex. 1000PEPE) → ignoré
  volumeMin: 1e6,          // E : volume échangé sur 24 h ≥ 1 M$ sur chacune des 2 plateformes
  heuresFunding: 8,        // D : funding défavorable compté sur 8 h de tenue à l'entrée
};
// Frais taker de base (estimés, palier standard)
const FRAIS = { binance: 0.0005, bybit: 0.00055, okx: 0.0005, hyperliquid: 0.00045, deribit: 0.0005 };

const H = 3600e3;
const num = (x) => { const v = parseFloat(x); return Number.isFinite(v) ? v : null; };
async function j(url, init) {
  const r = await fetch(url, { ...init, headers: { "user-agent": "price-arb/1", "content-type": "application/json", ...(init?.headers || {}) } });
  const t = await r.text();
  if (!r.ok) throw new Error(`HTTP ${r.status} ${t.slice(0, 120)}`);
  return JSON.parse(t);
}
const prochaineHeure = (now) => Math.ceil((now + 1) / H) * H;

// ---------- Lecteurs par plateforme : {ex, base, sym, rate, intH, next, cont, mark, bid, ask, stock}
async function binance(env) {
  // Binance refuse tous les serveurs Cloudflare : lecture via le serveur de Dublin (relais en lecture seule, cache 60 s)
  const r = await j("https://72-11-157-70.sslip.io/api/public/binance-funding");
  if (r.erreurs || !Array.isArray(r.premiumIndex) || !r.premiumIndex.length || !Array.isArray(r.bookTicker)) throw new Error("relais Dublin : " + JSON.stringify(r.erreurs || r).slice(0, 150));
  const pi = r.premiumIndex, fi = Array.isArray(r.fundingInfo) ? r.fundingInfo : [], bt = r.bookTicker;
  const iv = Object.fromEntries(fi.map((x) => [x.symbol, num(x.fundingIntervalHours)]));
  const bk = Object.fromEntries(bt.map((x) => [x.symbol, x]));
  return pi.filter((x) => x.symbol.endsWith("USDT") && x.nextFundingTime > 0).map((x) => ({
    ex: "binance", sym: x.symbol, base: x.symbol.slice(0, -4), rate: num(x.lastFundingRate), intH: iv[x.symbol] || 8,
    next: +x.nextFundingTime, mark: num(x.markPrice), bid: num(bk[x.symbol]?.bidPrice), ask: num(bk[x.symbol]?.askPrice),
  }));
}
async function bybit() {
  const [tk, ins] = await Promise.all([
    j("https://api.bybit.com/v5/market/tickers?category=linear"),
    j("https://api.bybit.com/v5/market/instruments-info?category=linear&limit=1000").catch(() => null),
  ]);
  const iv = {};
  for (const x of ins?.result?.list || []) iv[x.symbol] = num(x.fundingInterval) / 60;
  return (tk.result?.list || []).filter((x) => x.symbol.endsWith("USDT") && x.fundingRate !== "").map((x) => ({
    ex: "bybit", sym: x.symbol, base: x.symbol.slice(0, -4), rate: num(x.fundingRate),
    intH: num(x.fundingIntervalHour) || iv[x.symbol] || 8, next: +x.nextFundingTime,
    mark: num(x.markPrice), bid: num(x.bid1Price), ask: num(x.ask1Price), vol: num(x.turnover24h),
  }));
}
async function okx() {
  const [fr, tk] = await Promise.all([
    j("https://www.okx.com/api/v5/public/funding-rate?instId=ANY"),
    j("https://www.okx.com/api/v5/market/tickers?instType=SWAP"),
  ]);
  if (fr.code !== "0") throw new Error("okx funding " + fr.code + " " + fr.msg);
  const bk = Object.fromEntries((tk.data || []).map((x) => [x.instId, x]));
  return (fr.data || []).filter((x) => x.instId.endsWith("-USDT-SWAP")).map((x) => {
    const b = bk[x.instId] || {}, nt = +x.fundingTime, nn = +x.nextFundingTime;
    const bid = num(b.bidPx), ask = num(b.askPx);
    return { ex: "okx", sym: x.instId, base: x.instId.split("-")[0], rate: num(x.fundingRate),
      intH: nn > nt ? (nn - nt) / H : 8, next: nt, mark: bid && ask ? (bid + ask) / 2 : num(b.last), bid, ask, vol: num(b.volCcy24h) * num(b.last) || null };
  });
}
async function hyperliquid() {
  const url = "https://api.hyperliquid.xyz/info";
  const dexs = await j(url, { method: "POST", body: JSON.stringify({ type: "perpDexs" }) }).catch(() => [null]);
  const noms = [null, ...dexs.filter(Boolean).map((d) => d.name)];
  const out = [], now = Date.now();
  await Promise.all(noms.map(async (dex) => {
    const body = dex ? { type: "metaAndAssetCtxs", dex } : { type: "metaAndAssetCtxs" };
    const [meta, ctx] = await j(url, { method: "POST", body: JSON.stringify(body) }).catch(() => [null, null]);
    if (!meta) return;
    meta.universe.forEach((u, i) => {
      const c = ctx[i]; if (!c || u.isDelisted) return;
      const nom = u.name.includes(":") ? u.name.split(":")[1] : u.name;
      out.push({ ex: "hyperliquid", sym: u.name, base: nom, rate: num(c.funding), intH: 1, next: prochaineHeure(now),
        mark: num(c.markPx), bid: num(c.impactPxs?.[0]), ask: num(c.impactPxs?.[1]), vol: num(c.dayNtlVlm), stock: !!dex });
    });
  }));
  if (!out.length) throw new Error("aucune donnée Hyperliquid");
  // un seul par actif : on garde le dex principal s'il existe
  const vu = new Map();
  for (const x of out) if (!vu.has(x.base) || (vu.get(x.base).stock && !x.stock)) vu.set(x.base, x);
  return [...vu.values()];
}
async function deribit() {
  const lots = await Promise.all(["BTC", "ETH", "USDC", "USDT"].map((c) =>
    j(`https://www.deribit.com/api/v2/public/get_book_summary_by_currency?currency=${c}&kind=future`).then((r) => r.result || [])));
  const vu = new Map();
  for (const x of lots.flat()) {
    if (!x.instrument_name.endsWith("PERPETUAL") || x.funding_8h == null) continue;
    const base = x.instrument_name.split(/[-_]/)[0];
    if (vu.has(base) && x.instrument_name.includes("_")) continue; // préférer le perp principal
    vu.set(base, { ex: "deribit", sym: x.instrument_name, base, rate: num(x.funding_8h), intH: 8, cont: true,
      next: null, mark: num(x.mark_price), bid: num(x.bid_price), ask: num(x.ask_price), vol: num(x.volume_usd) ?? (num(x.volume) * num(x.mark_price) || null) });
  }
  return [...vu.values()];
}
const LECTEURS = { binance, bybit, okx, hyperliquid, deribit };

// Binance et Bybit bloquent les serveurs Cloudflare situés aux États-Unis :
// on les lit depuis un Durable Object placé en Europe (indice de lieu), d'abord Europe de l'Ouest, sinon Europe de l'Est.
const VIA_EUROPE = ["bybit"];
export class Relais extends DurableObject {
  async lire(nom) {
    let lieu = null;
    try { const t = await (await fetch("https://www.cloudflare.com/cdn-cgi/trace")).text(); lieu = (t.match(/colo=(\w+)/) || [])[1] + "/" + (t.match(/loc=(\w+)/) || [])[1]; } catch (e) {}
    try { return { ok: true, lignes: await LECTEURS[nom](), lieu }; }
    catch (e) { return { ok: false, err: String(e.message || e).slice(0, 200), lieu }; }
  }
}
Relais.prototype.carnetBybit = async function (sym) {
  const r = await j(`https://api.bybit.com/v5/market/orderbook?category=linear&symbol=${sym}&limit=100`);
  const f = (l) => (l || []).map((v) => [num(v[0]), num(v[1])]);
  return { bids: f(r.result?.b), asks: f(r.result?.a) };
};
Relais.prototype.carnetOkx = async function (sym) { return carnetOkxDirect(sym); };
Relais.prototype.lireComptant = async function (ex) { return lireComptant(ex); };
Relais.prototype.carnetComptant = async function (x) { return carnetC(x); };
Relais.prototype.comptes = async function () { return etatComptes(this.env); };
Relais.prototype.fermer = async function (id) { return fermerManuel(this.env, id); };

async function lireEurope(env, nom) {
  let dernier = null;
  for (const hint of ["weur", "eeur"]) {
    const stub = env.RELAIS.get(env.RELAIS.idFromName("relais-" + hint), { locationHint: hint });
    const r = await stub.lire(nom);
    if (r.ok) return r;
    dernier = r;
  }
  throw new Error(dernier.err + " (depuis " + dernier.lieu + ")");
}

async function toutLire(env) {
  const statut = {}, lignes = [];
  await Promise.all(Object.entries(LECTEURS).map(async ([nom, f]) => {
    const t0 = Date.now();
    try {
      let lieu = null, l;
      if (VIA_EUROPE.includes(nom) && env.RELAIS) { const r = await lireEurope(env, nom); l = r.lignes; lieu = r.lieu; }
      else {
        try { l = await f(env); }
        catch (e) { // OKX limite les demandes par adresse (429) : on réessaie depuis le module Europe, autre adresse
          if (nom === "okx" && env.RELAIS && /429/.test(String(e.message))) { const r = await lireEurope(env, nom); l = r.lignes; lieu = "relais " + r.lieu; }
          else throw e;
        }
      }
      l = l.filter((x) => x.mark > 0 || (x.bid > 0 && x.ask > 0));
      lignes.push(...l); statut[nom] = { ok: true, n: l.length, ms: Date.now() - t0, ...(lieu ? { lieu } : {}) };
    } catch (e) { statut[nom] = { ok: false, err: String(e.message || e).slice(0, 200) }; }
  }));
  return { statut, lignes };
}

// ---------- Carnets d'ordres : {bids:[[px, qté base]], asks:[[px, qté base]]}
let ctValOkx = null;
async function carnetOkxDirect(sym) {
  if (!ctValOkx) { const r = await j("https://www.okx.com/api/v5/public/instruments?instType=SWAP"); ctValOkx = Object.fromEntries((r.data || []).map((i) => [i.instId, num(i.ctVal)])); }
  const r = await j(`https://www.okx.com/api/v5/market/books?instId=${sym}&sz=100`); const b = r.data?.[0]; const cv = ctValOkx[sym] || 1;
  const f = (l) => (l || []).map((v) => [num(v[0]), num(v[1]) * cv]);
  return { bids: f(b?.bids), asks: f(b?.asks) };
}
async function carnet(env, x) {
  if (x.ex === "bybit") return env.RELAIS.get(env.RELAIS.idFromName("relais-weur"), { locationHint: "weur" }).carnetBybit(x.sym);
  if (x.ex === "okx") {
    try { return await carnetOkxDirect(x.sym); }
    catch (e) { if (env.RELAIS && /429/.test(String(e.message))) return env.RELAIS.get(env.RELAIS.idFromName("relais-weur"), { locationHint: "weur" }).carnetOkx(x.sym); throw e; }
  }
  if (x.ex === "hyperliquid") {
    const r = await j("https://api.hyperliquid.xyz/info", { method: "POST", body: JSON.stringify({ type: "l2Book", coin: x.sym }) });
    const f = (l) => (l || []).map((v) => [num(v.px), num(v.sz)]);
    return { bids: f(r.levels?.[0]), asks: f(r.levels?.[1]) };
  }
  if (x.ex === "deribit") {
    const r = await j(`https://www.deribit.com/api/v2/public/get_order_book?instrument_name=${x.sym}&depth=100`);
    const inverse = !x.sym.includes("_"); // BTC-PERPETUAL : quantité en USD
    const f = (l) => (l || []).map((v) => [v[0], inverse ? v[1] / v[0] : v[1]]);
    return { bids: f(r.result?.bids), asks: f(r.result?.asks) };
  }
  throw new Error("carnet indisponible");
}
// prix moyen pour exécuter une QUANTITÉ de pièces ; null si le carnet n'est pas assez profond
function prixMoyenQ(niveaux, qte) {
  let reste = qte, cout = 0;
  for (const [px, q] of niveaux) {
    if (!(px > 0) || !(q > 0)) continue;
    const pris = Math.min(reste, q); cout += pris * px; reste -= pris;
    if (reste <= qte * 1e-9) return cout / qte;
  }
  return null;
}
const demiSpread = (x) => (x.ask - x.bid) / (x.ask + x.bid);
const fraisAR = (a, b, N) => 2 * N * (FRAIS[a.ex] + FRAIS[b.ex]);

// pour chaque actif : acheter au meilleur prix vendeur (A), vendre au meilleur prix acheteur (B)
function ecarts(lignes) {
  const par = new Map();
  for (const x of lignes) { if (!(x.bid > 0 && x.ask > 0 && x.ask >= x.bid)) continue; if (!(x.vol >= REGLES.volumeMin)) continue; if (!par.has(x.base)) par.set(x.base, []); par.get(x.base).push(x); }
  const N = REGLES.notional, res = [];
  for (const [base, l] of par) {
    if (l.length < 2) continue;
    let best = null; // toutes les paires de plateformes, on garde la plus rentable
    for (const a of l) for (const b of l) {
      if (a.ex === b.ex) continue;
      const ecart = b.bid / a.ask - 1;
      if (ecart > REGLES.ecartMaxPrix) continue;
      const gain = N * ecart - N * (demiSpread(a) + demiSpread(b)) - fraisAR(a, b, N); // au sommet du carnet, sortie à prix égaux
      if (!best || gain > best.gain) best = { base, a, b, ecart, gain, stock: !!(a.stock || b.stock) };
    }
    if (best) res.push(best);
  }
  return res.sort((x, y) => y.gain - x.gain);
}

// ---------- Moteur fantôme
async function tick(env) {
  const now = Date.now(), N = REGLES.notional;
  const { statut, lignes } = await toutLire(env);
  const idx = new Map(lignes.map((x) => [x.ex + "|" + x.base, x]));
  const liste = ecarts(lignes);
  const db = env.DB, st = [];

  // positions ouvertes (B, C) : jamais de sortie forcée ni de prix inventé — on ferme seulement si la sortie
  // au vrai carnet, pour toute la quantité des 2 jambes, donne un résultat net ≥ objectif
  const ouvertes = (await db.prepare("SELECT * FROM positions WHERE statut='ouvert'").all()).results;
  const actifsOuverts = new Set(ouvertes.map((p) => p.base));
  for (const p of ouvertes) {
    const s = idx.get(p.short + "|" + p.base), l = idx.get(p.long + "|" + p.base); // short = jambe vendue (B), long = jambe achetée (A)
    const qL = p.qte_l ?? N / p.px_l_in, qS = p.qte_s ?? N / p.px_s_in;
    let fund = p.fund, ns = p.next_s, nl = p.next_l;
    const dtH = (now - p.dernier) / H;
    const nS = qS * (s?.mark || p.px_s_in), nL = qL * (l?.mark || p.px_l_in);
    if (p.cont_s) fund += p.rate_s / 8 * dtH * nS; else if (ns && now >= ns) { fund += p.rate_s * nS; ns = s?.next || ns + H; }
    if (p.cont_l) fund -= p.rate_l / 8 * dtH * nL; else if (nl && now >= nl) { fund -= p.rate_l * nL; nl = l?.next || nl + H; }
    let vL = null, vS = null;
    if (s && l) {
      try { const [cl, cs] = await Promise.all([carnet(env, l), carnet(env, s)]);
        vL = prixMoyenQ(cl.bids, qL); vS = prixMoyenQ(cs.asks, qS); } catch (e) {}
    }
    let net = p.net, raison = null, frais = p.frais;
    if (vL && vS) {
      const pnl = qL * (vL - p.px_l_in) + qS * (p.px_s_in - vS);
      frais = p.frais + qL * vL * FRAIS[p.long] + qS * vS * FRAIS[p.short];
      net = pnl + fund - frais;
      if (net >= REGLES.gainMin) raison = "objectif atteint";
    }
    if (raison) st.push(db.prepare("UPDATE positions SET statut='fermé', ferme=?, px_s_out=?, px_l_out=?, fund=?, frais=?, net=?, raison=?, dernier=? WHERE id=?").bind(now, vS, vL, fund, frais, net, raison, now, p.id));
    else st.push(db.prepare("UPDATE positions SET fund=?, next_s=?, next_l=?, rate_s=?, rate_l=?, dernier=?, last_l_bid=?, last_s_ask=?, net=?, vu=? WHERE id=?")
      .bind(fund, ns, nl, s?.rate ?? p.rate_s, l?.rate ?? p.rate_l, now, vL ?? p.last_l_bid, vS ?? p.last_s_ask, net, vL && vS ? now : p.vu, p.id));
  }

  // entrées (A, C, D) : même quantité de pièces sur les 2 jambes, prix moyens réels du carnet pour toute la quantité,
  // coût de sortie réel (profondeur des carnets) et funding défavorable sur 8 h déduits
  const verifies = {};
  for (const c of liste.filter((c) => c.gain >= REGLES.gainMin && !actifsOuverts.has(c.base)).slice(0, 8)) {
    try {
      const [ca, cb] = await Promise.all([carnet(env, c.a), carnet(env, c.b)]);
      const Q = N / c.a.ask;
      const vA = prixMoyenQ(ca.asks, Q), vB = prixMoyenQ(cb.bids, Q);           // entrée : achat sur A, vente sur B
      const sA = prixMoyenQ(ca.bids, Q), sB = prixMoyenQ(cb.asks, Q);           // sortie : revente sur A, rachat sur B
      if (!vA || !vB || !sA || !sB) { verifies[c.base] = "carnet trop mince pour " + N + " $"; continue; }
      const coutSortie = Q * ((vA - sA) / 2 + (sB - vB) / 2) ; // à prix rejoints : demi-écart de profondeur de chaque carnet
      const fraisTot = 2 * Q * (vA * FRAIS[c.a.ex] + vB * FRAIS[c.b.ex]);
      const fundH = Q * vB * (c.b.rate ?? 0) / (c.b.intH || 8) - Q * vA * (c.a.rate ?? 0) / (c.a.intH || 8); // par heure, + = reçu
      const fundTenue = Math.min(0, fundH * REGLES.heuresFunding);
      const gain = Q * (vB - vA) - coutSortie - fraisTot + fundTenue;
      verifies[c.base] = Math.round(gain * 100) / 100;
      if (gain < REGLES.gainMin) continue;
      const fraisIn = Q * (vA * FRAIS[c.a.ex] + vB * FRAIS[c.b.ex]);
      st.push(db.prepare(`INSERT INTO positions (base,short,long,notional,ouvert,px_s_in,px_l_in,fund,frais,rate_s,rate_l,next_s,next_l,cont_s,cont_l,dernier,cout_est,spread_in,statut,last_l_bid,last_s_ask,vu,net,qte_l,qte_s,regles)
        SELECT ?,?,?,?,?,?,?,0,?,?,?,?,?,?,?,?,?,?,'ouvert',?,?,?,?,?,?,? WHERE NOT EXISTS (SELECT 1 FROM positions WHERE base=? AND statut='ouvert')`).bind(
        c.base, c.b.ex, c.a.ex, Q * vA, now, vB, vA, fraisIn, c.b.rate, c.a.rate, c.b.next, c.a.next,
        c.b.cont ? 1 : 0, c.a.cont ? 1 : 0, now, gain, vB / vA - 1, sA, sB, now, Q * (sA - vA) + Q * (vB - sB) - fraisIn - Q * (sA * FRAIS[c.a.ex] + sB * FRAIS[c.b.ex]), Q, Q, REGLES_ID, c.base));
      actifsOuverts.add(c.base);
    } catch (e) { verifies[c.base] = "carnet illisible : " + String(e.message || e).slice(0, 60); }
  }

  const top = liste.slice(0, 60).map((c) => ({ base: c.base, stock: c.stock, achat: c.a.ex, ask: c.a.ask, vente: c.b.ex, bid: c.b.bid,
    ecart: c.ecart, gain: c.gain, verif: verifies[c.base] ?? null }));
  st.push(db.prepare("INSERT OR REPLACE INTO etat (id,t,json) VALUES (1,?,?)").bind(now, JSON.stringify({ statut, top, nActifs: liste.length })));
  for (let i = 0; i < st.length; i += 90) await db.batch(st.slice(i, i + 90));
  return { statut, nActifs: liste.length };
}

// ---------- HTTP
const JSONH = { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" };
// Moteur : un Durable Object en Europe qui scanne toutes les 10 s (alarme) ; la tâche Cloudflare de chaque minute ne fait que le réveiller
const PAS_MS = 10000;
export class Moteur extends DurableObject {
  async armer() { if (!(await this.ctx.storage.getAlarm())) await this.ctx.storage.setAlarm(Date.now() + 1000); return true; }
  async alarm() {
    // 18.11.2026 : Pitch « Que arbitrage » — les perpétuels ne tournent plus, seul l'arbitrage au comptant
    try { await tickComptant(this.env); } catch (e) {
      try { await this.env.DB.prepare("INSERT OR REPLACE INTO etat (id,t,json) VALUES (3,?,?)").bind(Date.now(), JSON.stringify({ err: String(e.stack || e).slice(0, 600) })).run(); } catch (e2) {}
    }
    await this.ctx.storage.setAlarm(Date.now() + PAS_MS);
  }
}
export default {
  async scheduled(ev, env, ctx) { ctx.waitUntil(env.MOTEUR.get(env.MOTEUR.idFromName("moteur"), { locationHint: "weur" }).armer()); },
  async fetch(req, env) {
    const u = new URL(req.url);
    if (u.pathname === "/api/version") return new Response(JSON.stringify({ version: VERSION }), { headers: JSONH });
    if (u.pathname === "/api/sonde") {
      const { statut, lignes } = await toutLire(env);
      const p = ecarts(lignes).slice(0, 5).map((x) => ({ base: x.base, achat: x.a.ex, vente: x.b.ex, ecart: x.ecart, gain: x.gain }));
      return new Response(JSON.stringify({ app: "funding-arb-app", type: "arbitrage-prix", version: VERSION, statut, top: p }), { headers: JSONH });
    }
    if (u.pathname === "/api/fermer" && req.method === "POST") {
      const id = parseInt(u.searchParams.get("id"), 10);
      if (!(id > 0)) return new Response(JSON.stringify({ ok: false, err: "id invalide" }), { status: 400, headers: JSONH });
      return new Response(JSON.stringify(await env.RELAIS.get(env.RELAIS.idFromName("relais-weur"), { locationHint: "weur" }).fermer(id)), { headers: JSONH });
    }
    if (u.pathname === "/api/comptes") return new Response(JSON.stringify(await env.RELAIS.get(env.RELAIS.idFromName("relais-weur"), { locationHint: "weur" }).comptes()), { headers: JSONH });
    if (u.pathname === "/api/comptant") { const er = await env.DB.prepare("SELECT * FROM etat WHERE id=3").first(); return new Response(JSON.stringify({ version: VERSION, erreur: er ? { t: er.t, ...JSON.parse(er.json) } : null, ...(await etatComptant(env)) }), { headers: JSONH }); }
    if (u.pathname === "/comptant") {
      const r = await env.ASSETS.fetch(new Request(new URL("/comptant.tpl", u)));
      return new Response((await r.text()).replaceAll("__VERSION__", VERSION), { headers: { "content-type": "text/html; charset=utf-8", "cache-control": "no-store, max-age=0" } });
    }
    if (u.pathname === "/api/etat") {
      const e = await env.DB.prepare("SELECT * FROM etat WHERE id=1").first();
      const ouv = (await env.DB.prepare("SELECT * FROM positions WHERE statut='ouvert' ORDER BY ouvert DESC").all()).results;
      const fer = (await env.DB.prepare("SELECT * FROM positions WHERE statut='fermé' ORDER BY ferme DESC LIMIT 300").all()).results;
      const tot = await env.DB.prepare("SELECT COUNT(*) n, SUM(net) net, SUM(CASE WHEN net>0 THEN 1 ELSE 0 END) g, SUM(fund) fund, SUM(frais) frais, MIN(ouvert) debut FROM positions WHERE statut='fermé' AND regles=?").bind(REGLES_ID).first();
      const anc = await env.DB.prepare("SELECT COUNT(*) n, SUM(net) net FROM positions WHERE statut='fermé' AND (regles IS NULL OR regles<>?)").bind(REGLES_ID).first();
      return new Response(JSON.stringify({ version: VERSION, regles: REGLES, frais: FRAIS, t: e?.t, scan: e ? JSON.parse(e.json) : null, ouvertes: ouv, fermees: fer, total: tot, anciennes: anc, reglesId: REGLES_ID }), { headers: JSONH });
    }
    if (u.pathname === "/" || u.pathname === "/index.html") {
      const r = await env.ASSETS.fetch(new Request(new URL("/comptant.tpl", u)));
      return new Response((await r.text()).replaceAll("__VERSION__", VERSION), { headers: { "content-type": "text/html; charset=utf-8", "cache-control": "no-store, max-age=0" } });
    }
    return env.ASSETS.fetch(req);
  },
};
