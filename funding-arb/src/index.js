// Funding Arb — mode FANTÔME (aucun ordre réel).
// Toutes les 5 min : lit les taux de financement des perpétuels sur Binance, Bybit, OKX, Hyperliquid, Deribit,
// trouve pour chaque actif la meilleure paire (short là où le funding est le plus haut, long là où il est le plus bas),
// mesure combien de temps l'écart dure, et simule des trades seulement s'il dure et reste rentable après frais.
import { DurableObject } from "cloudflare:workers";
const VERSION = "1.1.1";

// Règles proposées (Pitch décide — modifiables ici)
const REGLES = {
  notional: 1000,          // $ par jambe
  persistanceMin: 60,      // minutes : l'écart doit durer au moins 1 h avant d'entrer
  horizonH: 24,            // le funding attendu sur 24 h…
  multipleCout: 2,         // …doit couvrir au moins 2× le coût aller-retour estimé
  sortieTicks: 1,          // sortie dès que l'écart de la paire passe ≤ 0
  maxDonneesManquantesMin: 30,
};
// Frais taker de base (estimés, palier standard)
const FRAIS = { binance: 0.0005, bybit: 0.00055, okx: 0.0005, hyperliquid: 0.00045, deribit: 0.0005 };

const H = 3600e3;
const num = (x) => { const v = parseFloat(x); return Number.isFinite(v) ? v : null; };
async function j(url, init) {
  const r = await fetch(url, { ...init, headers: { "user-agent": "funding-arb/1", "content-type": "application/json", ...(init?.headers || {}) } });
  const t = await r.text();
  if (!r.ok) throw new Error(`HTTP ${r.status} ${t.slice(0, 120)}`);
  return JSON.parse(t);
}
const prochaineHeure = (now) => Math.ceil((now + 1) / H) * H;

// ---------- Lecteurs par plateforme : {ex, base, sym, rate, intH, next, cont, mark, bid, ask, stock}
async function binance(env) {
  const [pi, fi, bt] = await Promise.all([
    j("https://fapi.binance.com/fapi/v1/premiumIndex"),
    j("https://fapi.binance.com/fapi/v1/fundingInfo").catch(() => []),
    j("https://fapi.binance.com/fapi/v1/ticker/bookTicker"),
  ]);
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
    mark: num(x.markPrice), bid: num(x.bid1Price), ask: num(x.ask1Price),
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
      intH: nn > nt ? (nn - nt) / H : 8, next: nt, mark: bid && ask ? (bid + ask) / 2 : num(b.last), bid, ask };
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
        mark: num(c.markPx), bid: num(c.impactPxs?.[0]), ask: num(c.impactPxs?.[1]), stock: !!dex });
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
      next: null, mark: num(x.mark_price), bid: num(x.bid_price), ask: num(x.ask_price) });
  }
  return [...vu.values()];
}
const LECTEURS = { binance, bybit, okx, hyperliquid, deribit };

// Binance et Bybit bloquent les serveurs Cloudflare situés aux États-Unis :
// on les lit depuis un Durable Object placé en Europe (indice de lieu), d'abord Europe de l'Ouest, sinon Europe de l'Est.
const VIA_EUROPE = ["binance", "bybit"];
export class Relais extends DurableObject {
  async lire(nom) {
    let lieu = null;
    try { const t = await (await fetch("https://www.cloudflare.com/cdn-cgi/trace")).text(); lieu = (t.match(/colo=(\w+)/) || [])[1] + "/" + (t.match(/loc=(\w+)/) || [])[1]; } catch (e) {}
    try { return { ok: true, lignes: await LECTEURS[nom](), lieu }; }
    catch (e) { return { ok: false, err: String(e.message || e).slice(0, 200), lieu }; }
  }
}
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
      else l = await f(env);
      l = l.filter((x) => x.rate != null && x.mark > 0);
      lignes.push(...l); statut[nom] = { ok: true, n: l.length, ms: Date.now() - t0, ...(lieu ? { lieu } : {}) };
    } catch (e) { statut[nom] = { ok: false, err: String(e.message || e).slice(0, 200) }; }
  }));
  return { statut, lignes };
}

// ---------- Paires
const parHeure = (x) => x.rate / x.intH;
function cout(a, b) { // coût aller-retour estimé, en fraction du notional : frais 2 jambes × entrée+sortie + fourchette b/a de chaque jambe
  const fr = 2 * (FRAIS[a.ex] + FRAIS[b.ex]);
  const sa = a.bid && a.ask ? (a.ask - a.bid) / ((a.ask + a.bid) / 2) : null;
  const sb = b.bid && b.ask ? (b.ask - b.bid) / ((b.ask + b.bid) / 2) : null;
  if (sa == null || sb == null || sa < 0 || sb < 0) return null;
  return fr + sa + sb;
}
function meilleuresPaires(lignes) {
  const par = new Map();
  for (const x of lignes) { if (!par.has(x.base)) par.set(x.base, []); par.get(x.base).push(x); }
  const res = [];
  for (const [base, l] of par) {
    if (l.length < 2) continue;
    const tri = [...l].sort((p, q) => parHeure(q) - parHeure(p));
    const s = tri[0], lo = tri[tri.length - 1];
    if (Math.abs(s.mark / lo.mark - 1) > 0.03) continue; // prix incohérents (contrats différents) → ignoré
    const sh = parHeure(s) - parHeure(lo);
    res.push({ base, s, l: lo, sh, cout: cout(s, lo), stock: !!(s.stock || lo.stock) });
  }
  return res.sort((a, b) => b.sh - a.sh);
}

// ---------- Moteur fantôme
async function tick(env) {
  const now = Date.now();
  const { statut, lignes } = await toutLire(env);
  const idx = new Map(lignes.map((x) => [x.ex + "|" + x.base, x]));
  const paires = meilleuresPaires(lignes);
  const db = env.DB;

  // persistance de la meilleure paire par actif
  const anc = new Map((await db.prepare("SELECT * FROM paires").all()).results.map((r) => [r.base, r]));
  const st = [];
  const persist = {};
  for (const p of paires) {
    const a = anc.get(p.base);
    let depuis = now;
    if (p.sh > 0 && a && a.short === p.s.ex && a.long === p.l.ex && a.depuis) depuis = a.depuis;
    persist[p.base] = p.sh > 0 ? depuis : null;
    st.push(db.prepare("INSERT OR REPLACE INTO paires (base,short,long,depuis,maj) VALUES (?,?,?,?,?)").bind(p.base, p.s.ex, p.l.ex, p.sh > 0 ? depuis : null, now));
  }
  st.push(db.prepare("DELETE FROM paires WHERE maj < ?").bind(now - 6 * H));

  // positions ouvertes
  const ouvertes = (await db.prepare("SELECT * FROM positions WHERE statut='ouvert'").all()).results;
  const actifsOuverts = new Set(ouvertes.map((p) => p.base));
  for (const p of ouvertes) {
    const s = idx.get(p.short + "|" + p.base), l = idx.get(p.long + "|" + p.base);
    let fund = p.fund, ns = p.next_s, nl = p.next_l, raison = null;
    const dtH = (now - p.dernier) / H;
    // jambe short : reçoit le funding si positif
    if (p.cont_s) fund += p.rate_s / 8 * dtH * p.notional; else if (ns && now >= ns) { fund += p.rate_s * p.notional; ns = s?.next || ns + H; }
    // jambe long : paie le funding si positif
    if (p.cont_l) fund -= p.rate_l / 8 * dtH * p.notional; else if (nl && now >= nl) { fund -= p.rate_l * p.notional; nl = l?.next || nl + H; }
    if (s && l) {
      if (parHeure(s) - parHeure(l) <= 0) raison = "écart ≤ 0";
    } else if (now - p.vu > REGLES.maxDonneesManquantesMin * 60e3) raison = "données manquantes";
    const sBid = s?.bid ?? p.last_s_bid, sAsk = s?.ask ?? p.last_s_ask, lBid = l?.bid ?? p.last_l_bid, lAsk = l?.ask ?? p.last_l_ask;
    if (raison && sAsk && lBid) {
      const pnlS = p.notional / p.px_s_in * (p.px_s_in - sAsk);
      const pnlL = p.notional / p.px_l_in * (lBid - p.px_l_in);
      const frais = p.frais + p.notional * (FRAIS[p.short] + FRAIS[p.long]);
      const net = fund + pnlS + pnlL - frais;
      st.push(db.prepare("UPDATE positions SET statut='fermé', ferme=?, px_s_out=?, px_l_out=?, fund=?, frais=?, net=?, raison=?, dernier=? WHERE id=?")
        .bind(now, sAsk, lBid, fund, frais, net, raison, now, p.id));
    } else {
      st.push(db.prepare("UPDATE positions SET fund=?, next_s=?, next_l=?, rate_s=?, rate_l=?, dernier=?, last_s_bid=?, last_s_ask=?, last_l_bid=?, last_l_ask=?, vu=? WHERE id=?")
        .bind(fund, ns, nl, s?.rate ?? p.rate_s, l?.rate ?? p.rate_l, now, sBid, sAsk, lBid, lAsk, s && l ? now : p.vu, p.id));
    }
  }

  // entrées
  const N = REGLES.notional;
  for (const p of paires) {
    if (p.sh <= 0 || p.cout == null || actifsOuverts.has(p.base)) continue;
    const dureeMin = persist[p.base] ? (now - persist[p.base]) / 60e3 : 0;
    if (dureeMin < REGLES.persistanceMin) continue;
    if (p.sh * REGLES.horizonH < REGLES.multipleCout * p.cout) continue;
    const fraisIn = N * (FRAIS[p.s.ex] + FRAIS[p.l.ex]);
    st.push(db.prepare(`INSERT INTO positions (base,short,long,notional,ouvert,px_s_in,px_l_in,fund,frais,rate_s,rate_l,next_s,next_l,cont_s,cont_l,dernier,cout_est,spread_in,statut,last_s_bid,last_s_ask,last_l_bid,last_l_ask,vu)
      VALUES (?,?,?,?,?,?,?,0,?,?,?,?,?,?,?,?,?,?,'ouvert',?,?,?,?,?)`).bind(
      p.base, p.s.ex, p.l.ex, N, now, p.s.bid, p.l.ask, fraisIn, p.s.rate, p.l.rate, p.s.next, p.l.next,
      p.s.cont ? 1 : 0, p.l.cont ? 1 : 0, now, p.cout, p.sh, p.s.bid, p.s.ask, p.l.bid, p.l.ask, now));
  }

  // instantané pour la page
  const top = paires.slice(0, 60).map((p) => ({
    base: p.base, stock: p.stock, short: p.s.ex, long: p.l.ex, rs: p.s.rate, is: p.s.intH, rl: p.l.rate, il: p.l.intH,
    sh: p.sh, cout: p.cout, depuis: persist[p.base],
  }));
  st.push(db.prepare("INSERT OR REPLACE INTO etat (id,t,json) VALUES (1,?,?)").bind(now, JSON.stringify({ statut, top, nPaires: paires.length })));
  for (let i = 0; i < st.length; i += 90) await db.batch(st.slice(i, i + 90));
  return { statut, nPaires: paires.length };
}

// ---------- HTTP
const JSONH = { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" };
export default {
  async scheduled(ev, env, ctx) { ctx.waitUntil(tick(env)); },
  async fetch(req, env) {
    const u = new URL(req.url);
    if (u.pathname === "/api/version") return new Response(JSON.stringify({ version: VERSION }), { headers: JSONH });
    if (u.pathname === "/api/sonde") {
      const { statut, lignes } = await toutLire(env);
      const p = meilleuresPaires(lignes).slice(0, 5).map((x) => ({ base: x.base, short: x.s.ex, long: x.l.ex, spreadH: x.sh, cout: x.cout }));
      return new Response(JSON.stringify({ app: "funding-arb-app", version: VERSION, statut, top: p }), { headers: JSONH });
    }
    if (u.pathname === "/api/etat") {
      const e = await env.DB.prepare("SELECT * FROM etat WHERE id=1").first();
      const ouv = (await env.DB.prepare("SELECT * FROM positions WHERE statut='ouvert' ORDER BY ouvert DESC").all()).results;
      const fer = (await env.DB.prepare("SELECT * FROM positions WHERE statut='fermé' ORDER BY ferme DESC LIMIT 300").all()).results;
      const tot = await env.DB.prepare("SELECT COUNT(*) n, SUM(net) net, SUM(CASE WHEN net>0 THEN 1 ELSE 0 END) g, SUM(fund) fund, SUM(frais) frais, MIN(ouvert) debut FROM positions WHERE statut='fermé'").first();
      return new Response(JSON.stringify({ version: VERSION, regles: REGLES, frais: FRAIS, t: e?.t, scan: e ? JSON.parse(e.json) : null, ouvertes: ouv, fermees: fer, total: tot }), { headers: JSONH });
    }
    if (u.pathname === "/" || u.pathname === "/index.html") {
      const r = await env.ASSETS.fetch(new Request(new URL("/page.tpl", u)));
      return new Response((await r.text()).replaceAll("__VERSION__", VERSION), { headers: { "content-type": "text/html; charset=utf-8", "cache-control": "no-store, max-age=0" } });
    }
    return env.ASSETS.fetch(req);
  },
};
