// Arbitrage AU COMPTANT — mode FANTÔME (aucun ordre réel).
// Principe : on suppose des pièces et des dollars déjà déposés sur chaque plateforme. Quand un actif s'achète
// moins cher sur A que ce qu'il se vend sur B, on achète sur A et on vend sur B dans la même seconde :
// le gain est acquis immédiatement (pas de position à fermer plus tard).
// Tourne dans le Moteur (Durable Object en Europe), après le scan des perpétuels.

import { lireMarge, emprunt, TAUX_DEFAUT_H } from "./marge.js";
import { lireTransferts, transfertsOk } from "./transferts.js";
export const REGLES_ID_C = "3";
export const REGLES_C = {
  mise: 5000,           // $ de chaque côté : 5 000 $ achetés sur A, 5 000 $ vendus sur B (choix de Pitch, 18.11.2026)
  gainMin: 50,          // $ net après frais des 2 achats/ventes
  ecartMaxPrix: 0.10,   // au-delà de 10 % ce n'est probablement pas le même jeton → ignoré
  volumeMin: 1e6,       // $ échangés sur 24 h sur chacune des 2 plateformes
  pauseMemeActifS: 60,  // stratégie 1 : un même actif ne compte qu'une fois par minute (le carnet doit se reconstituer)
  ecartSuspect: 0.05,   // A : un écart > 5 % (1 % jusqu'au 21.11.2026, relevé par Pitch, choix 3)…
  dureeSuspectS: 300,   // …qui dure plus de 5 min = jeton différent ou retraits bloqués → actif ignoré. 20.11.2026 (Pitch, option A) : décision à l'entrée seulement, une position prise n'est plus jamais annulée
  sorties: [5, 10],
  entreeMin2: 25,       // stratégie 2 : gain à l'entrée ≥ 25 $ après frais d'entrée (Pitch, 19.11.2026)
  empruntObligatoire: true, // la crypto vendue doit être empruntable sur la plateforme de vente (vente à découvert au comptant)
  heuresEmpruntS1: 1,
  plateformes: ["gate", "bybit", "okx", "kucoin", "aster"], // 19.11.2026 : plateformes prévues pour le réel ; 20.11.2026 : + Aster (DEX) en fantôme
  shortSeul: ["aster"],  // 20.11.2026 (Pitch) : Aster sert seulement de côté « vente à découvert » (perpétuel), l'achat reste au comptant sur les 4 plateformes
  maxOuvertes: 5,       // stratégie 2 : au plus 5 positions ouvertes en même temps par variante (hypothèse, Pitch n'a pas fixé)   // stratégie 1 : intérêts comptés 1 h (le temps de virer les pièces achetées pour rendre l'emprunt)     // stratégie 2 : clôture quand l'écart inverse rapporte au moins 5 $ (variante 5) ou 10 $ (variante 10)
};
// Frais « preneur » au comptant, palier de base (estimés, prudents)
export const LECT_EXPORT = () => LECT;
export const FRAIS_C = { aster: 0.0004, bybit: 0.001, okx: 0.001, kucoin: 0.001, gate: 0.002, mexc: 0.0005, bitget: 0.001, kraken: 0.008, coinbase: 0.012 };

const num = (x) => { const v = parseFloat(x); return Number.isFinite(v) ? v : null; };
async function j(url) {
  const r = await fetch(url, { headers: { "user-agent": "price-arb/1" } });
  const t = await r.text();
  if (!r.ok) throw new Error(`HTTP ${r.status} ${t.slice(0, 100)}`);
  return JSON.parse(t);
}
const QUOTES = ["USDT", "USDC"];
const splitSym = (s) => { for (const q of QUOTES) if (s.endsWith(q) && s.length > q.length) return [s.slice(0, -q.length), q]; return null; };
const KRAKEN_ALIAS = { XBT: "BTC", XDG: "DOGE" };

// ---------- Prix : {ex, base, quote, sym, bid, ask, vol}
let krakenPaires = null;
const LECT = {
  async bybit() {
    const r = await j("https://api.bybit.com/v5/market/tickers?category=spot");
    return (r.result?.list || []).map((x) => { const p = splitSym(x.symbol); return p && { sym: x.symbol, base: p[0], quote: p[1], bid: num(x.bid1Price), ask: num(x.ask1Price), vol: num(x.turnover24h) }; });
  },
  async okx() {
    const r = await j("https://www.okx.com/api/v5/market/tickers?instType=SPOT");
    return (r.data || []).map((x) => { const [b, q] = x.instId.split("-"); return QUOTES.includes(q) && { sym: x.instId, base: b, quote: q, bid: num(x.bidPx), ask: num(x.askPx), vol: num(x.volCcy24h) }; });
  },
  async kucoin() {
    const r = await j("https://api.kucoin.com/api/v1/market/allTickers");
    return (r.data?.ticker || []).map((x) => { const [b, q] = x.symbol.split("-"); return QUOTES.includes(q) && { sym: x.symbol, base: b, quote: q, bid: num(x.buy), ask: num(x.sell), vol: num(x.volValue) }; });
  },
  async gate() {
    const r = await j("https://api.gateio.ws/api/v4/spot/tickers");
    return (r || []).map((x) => { const [b, q] = x.currency_pair.split("_"); return QUOTES.includes(q) && { sym: x.currency_pair, base: b, quote: q, bid: num(x.highest_bid), ask: num(x.lowest_ask), vol: num(x.quote_volume) }; });
  },
  async aster() { // perpétuels USDT d'Aster (DEX) : sert seulement au short ; préfixes 1000/k (prix multipliés) exclus
    const [bt, h] = await Promise.all([j("https://fapi.asterdex.com/fapi/v1/ticker/bookTicker"), j("https://fapi.asterdex.com/fapi/v1/ticker/24hr")]);
    const v = Object.fromEntries((h || []).map((x) => [x.symbol, num(x.quoteVolume)]));
    return (bt || []).map((x) => { const p = splitSym(x.symbol); return p && p[1] === "USDT" && !/^(1000|1M|k[A-Z])/.test(p[0]) && { sym: x.symbol, base: p[0], quote: p[1], bid: num(x.bidPrice), ask: num(x.askPrice), vol: v[x.symbol], perp: true }; });
  },
  async mexc() {
    const [bt, h] = await Promise.all([j("https://api.mexc.com/api/v3/ticker/bookTicker"), j("https://api.mexc.com/api/v3/ticker/24hr")]);
    const v = Object.fromEntries((h || []).map((x) => [x.symbol, num(x.quoteVolume)]));
    return (bt || []).map((x) => { const p = splitSym(x.symbol); return p && { sym: x.symbol, base: p[0], quote: p[1], bid: num(x.bidPrice), ask: num(x.askPrice), vol: v[x.symbol] }; });
  },
  async bitget() {
    const r = await j("https://api.bitget.com/api/v2/spot/market/tickers");
    return (r.data || []).map((x) => { const p = splitSym(x.symbol); return p && { sym: x.symbol, base: p[0], quote: p[1], bid: num(x.bidPr), ask: num(x.askPr), vol: num(x.quoteVolume) }; });
  },
  async kraken() {
    if (!krakenPaires) {
      const r = await j("https://api.kraken.com/0/public/AssetPairs");
      krakenPaires = {};
      for (const [k, v] of Object.entries(r.result || {})) {
        if (!v.wsname) continue; const [b, q] = v.wsname.split("/");
        if (QUOTES.includes(q)) krakenPaires[k] = { base: KRAKEN_ALIAS[b] || b, quote: q, alt: v.altname };
      }
    }
    const r = await j("https://api.kraken.com/0/public/Ticker");
    return Object.entries(r.result || {}).map(([k, x]) => { const p = krakenPaires[k]; return p && { sym: p.alt, base: p.base, quote: p.quote, bid: num(x.b?.[0]), ask: num(x.a?.[0]), vol: num(x.v?.[1]) * num(x.c?.[0]) }; });
  },
  async coinbase() { // pas de meilleur prix achat/vente en lecture groupée : on prend le dernier prix, le carnet tranche ensuite
    const r = await j("https://api.coinbase.com/api/v3/brokerage/market/products?product_type=SPOT&limit=1000");
    return (r.products || []).map((x) => { const [b, q] = (x.product_id || "").split("-"); const px = num(x.price);
      return QUOTES.includes(q) && !x.trading_disabled && { sym: x.product_id, base: b, quote: q, bid: px, ask: px, vol: num(x.volume_24h) * px, approx: true }; });
  },
};

// ---------- Carnets : {bids:[[px,q]], asks:[[px,q]]}, quantités en pièces
const paires = (l) => (l || []).map((v) => [num(v[0]), num(v[1])]);
async function carnetC(x) {
  switch (x.ex) {
    case "bybit": { const r = await j(`https://api.bybit.com/v5/market/orderbook?category=spot&symbol=${x.sym}&limit=200`); return { bids: paires(r.result?.b), asks: paires(r.result?.a) }; }
    case "okx": { const r = await j(`https://www.okx.com/api/v5/market/books?instId=${x.sym}&sz=100`); return { bids: paires(r.data?.[0]?.bids), asks: paires(r.data?.[0]?.asks) }; }
    case "kucoin": { const r = await j(`https://api.kucoin.com/api/v1/market/orderbook/level2_100?symbol=${x.sym}`); return { bids: paires(r.data?.bids), asks: paires(r.data?.asks) }; }
    case "gate": { const r = await j(`https://api.gateio.ws/api/v4/spot/order_book?currency_pair=${x.sym}&limit=100`); return { bids: paires(r.bids), asks: paires(r.asks) }; }
    case "aster": { const r = await j(`https://fapi.asterdex.com/fapi/v1/depth?symbol=${x.sym}&limit=100`); return { bids: paires(r.bids), asks: paires(r.asks) }; }
    case "mexc": { const r = await j(`https://api.mexc.com/api/v3/depth?symbol=${x.sym}&limit=100`); return { bids: paires(r.bids), asks: paires(r.asks) }; }
    case "bitget": { const r = await j(`https://api.bitget.com/api/v2/spot/market/orderbook?symbol=${x.sym}&type=step0&limit=100`); return { bids: paires(r.data?.bids), asks: paires(r.data?.asks) }; }
    case "kraken": { const r = await j(`https://api.kraken.com/0/public/Depth?pair=${x.sym}&count=100`); const b = Object.values(r.result || {})[0] || {}; return { bids: paires(b.bids), asks: paires(b.asks) }; }
    case "coinbase": { const r = await j(`https://api.coinbase.com/api/v3/brokerage/market/product_book?product_id=${x.sym}&limit=100`);
      const f = (l) => (l || []).map((v) => [num(v.price), num(v.size)]); return { bids: f(r.pricebook?.bids), asks: f(r.pricebook?.asks) }; }
  }
  throw new Error("carnet indisponible");
}
function prixMoyenQ(niveaux, qte) {
  let reste = qte, cout = 0;
  for (const [px, q] of niveaux) { if (!(px > 0) || !(q > 0)) continue; const pris = Math.min(reste, q); cout += pris * px; reste -= pris; if (reste <= qte * 1e-9) return cout / qte; }
  return null;
}

// Coût de portage : intérêts d'emprunt (comptant) ou funding réellement versé sur Aster depuis l'ouverture
// (short : funding positif = reçu → coût négatif). Historique public des taux, montant ≈ quantité × prix de vente.
async function coutPortage(p, now, symB) {
  if (p.vente_ex !== "aster") return p.taux ? p.qte * p.px_vente * p.taux * (now - p.ouvert) / 3600e3 : 0;
  const l = await j(`https://fapi.asterdex.com/fapi/v1/fundingRate?symbol=${symB}&startTime=${p.ouvert}&limit=1000`);
  return -(l || []).filter((x) => x.fundingTime > p.ouvert && x.fundingTime <= now).reduce((t, x) => t + (num(x.fundingRate) || 0), 0) * p.qte * p.px_vente;
}
export async function lireComptant(ex) { return (await LECT[ex]()).filter(Boolean); }
export { carnetC };
// B : OKX / KuCoin refusent parfois (429, trop de demandes) → nouvel essai par le module Europe (autre adresse)
const relais = (env, hint) => env.RELAIS.get(env.RELAIS.idFromName("relais-" + hint), { locationHint: hint });
async function avecRelais(env, f, viaRelais) {
  try { return await f(); }
  catch (e) {
    if (!env.RELAIS || !/429/.test(String(e.message))) throw e;
    let der = e;
    for (const h of ["eeur", "weur"]) { try { return await viaRelais(relais(env, h)); } catch (e2) { der = e2; } }
    throw der;
  }
}
const carnetR = (env, x) => avecRelais(env, () => carnetC(x), (st) => st.carnetComptant(x));

// ---------- Scan
export async function tickComptant(env) {
  const now = Date.now(), N = REGLES_C.mise, db = env.DB;
  const statut = {}, lignes = [];
  await Promise.all(Object.entries(LECT).filter(([ex]) => REGLES_C.plateformes.includes(ex)).map(async ([ex, f]) => {
    const t0 = Date.now();
    try { const l = (await avecRelais(env, f, (st) => st.lireComptant(ex))).filter((x) => x && x.bid > 0 && x.ask > 0 && x.ask >= x.bid).map((x) => ({ ...x, ex }));
      lignes.push(...l); statut[ex] = { ok: true, n: l.length, ms: Date.now() - t0 }; }
    catch (e) { statut[ex] = { ok: false, err: String(e.message || e).slice(0, 160) }; }
  }));
  // candidats : même jeton, même monnaie de cotation, toutes les paires de plateformes
  const par = new Map();
  for (const x of lignes) { if (!(x.vol >= REGLES_C.volumeMin)) continue; const k = x.base + "/" + x.quote; if (!par.has(k)) par.set(k, []); par.get(k).push(x); }
  let marge = null; try { marge = await lireMarge(db); } catch (e) { try { await db.prepare("INSERT OR REPLACE INTO etat (id,t,json) VALUES (5,?,?)").bind(now, JSON.stringify({ err: String(e.stack || e).slice(0, 500) })).run(); } catch (e2) {} }
  const cands = [];
  for (const [k, l] of par) {
    let best = null;
    for (const a of l) for (const b of l) {
      if (a.ex === b.ex || REGLES_C.shortSeul.includes(a.ex)) continue;
      const ecart = b.bid / a.ask - 1;
      if (ecart <= 0 || ecart > REGLES_C.ecartMaxPrix) continue;
      const gain = N * ecart - N * (FRAIS_C[a.ex] + FRAIS_C[b.ex]);
      if (!best || gain > best.gain) best = { k, a, b, ecart, gain };
    }
    if (best) cands.push(best);
  }
  cands.sort((x, y) => y.gain - x.gain);
  const st = [], verifies = {};

  // A : suivi des écarts > 1 % (depuis quand ils durent)
  const lignesS = (await db.prepare("SELECT cle, depuis, vu FROM ecarts_suspects").all()).results;
  const suivis = new Map(lignesS.map((r) => [r.cle, r.depuis])), vus = new Map(lignesS.map((r) => [r.cle, r.vu || r.depuis]));
  const suspectsMaintenant = new Set();
  for (const [k0, l] of par) for (const a of l) for (const b of l) { // toutes les paires de plateformes, pas seulement la meilleure
    if (a.ex === b.ex || !(b.bid / a.ask - 1 > REGLES_C.ecartSuspect)) continue;
    const k = k0 + "|" + a.ex + ">" + b.ex; suspectsMaintenant.add(k);
    if (!suivis.has(k)) { suivis.set(k, now); st.push(db.prepare("INSERT OR REPLACE INTO ecarts_suspects (cle, depuis, vu) VALUES (?,?,?)").bind(k, now, now)); }
    else st.push(db.prepare("UPDATE ecarts_suspects SET vu=? WHERE cle=?").bind(now, k));
  }
  // l'écart n'est considéré comme disparu que si les 2 plateformes ont bien été lues et qu'on ne l'a plus vu depuis 60 s
  for (const k of [...suivis.keys()]) {
    if (suspectsMaintenant.has(k)) continue;
    const [, exs] = k.split("|"), [exA, exB] = exs.split(">");
    if (!(statut[exA]?.ok && statut[exB]?.ok) || now - (vus.get(k) || 0) < 60000) continue;
    suivis.delete(k); st.push(db.prepare("DELETE FROM ecarts_suspects WHERE cle=?").bind(k));
  }
  const permanent = (c) => { const d = suivis.get(c.k + "|" + c.a.ex + ">" + c.b.ex); return d != null && now - d > REGLES_C.dureeSuspectS * 1000; };
  // trades en attente de validation : annulés si leur écart a duré plus de 5 min, validés sinon
  const attente = (await db.prepare("SELECT id, cle, achat_ex, vente_ex, t FROM comptant WHERE statut='attente'").all()).results;
  for (const r of attente) {
    const k = r.cle + "|" + r.achat_ex + ">" + r.vente_ex, d = suivis.get(k);
    if (d != null && now - d > REGLES_C.dureeSuspectS * 1000) st.push(db.prepare("UPDATE comptant SET statut='annulé' WHERE id=?").bind(r.id));
    else if (d == null && now - r.t > REGLES_C.dureeSuspectS * 1000) st.push(db.prepare("UPDATE comptant SET statut='validé' WHERE id=?").bind(r.id));
  }

  // ---------- Stratégie 1 : retirée par Pitch le 19.11.2026 (ancien code laissé désactivé)
  if (false) {
  const recents = new Set((await db.prepare("SELECT cle FROM comptant WHERE t > ?").bind(now - REGLES_C.pauseMemeActifS * 1000).all()).results.map((r) => r.cle));
  for (const c of cands.filter((c) => c.gain >= REGLES_C.gainMin && !permanent(c)).slice(0, 8)) {
    if (recents.has(c.k)) { verifies[c.k] = "déjà pris il y a moins d'une minute"; continue; }
    try {
      const [ca, cb] = await Promise.all([carnetR(env, c.a), carnetR(env, c.b)]);
      const Q = N / c.a.ask;
      const em = emprunt(marge, c.b.ex, c.b.base, Q);
      if (!em) { verifies[c.k] = c.b.base + " pas empruntable sur " + c.b.ex + " pour cette quantité"; continue; }
      const vA = prixMoyenQ(ca.asks, Q), vB = prixMoyenQ(cb.bids, Q);
      if (!vA || !vB) { verifies[c.k] = "carnet trop mince pour " + N + " $"; continue; }
      const interet = Q * vB * em.taux * REGLES_C.heuresEmpruntS1;
      const net = Q * vB * (1 - FRAIS_C[c.b.ex]) - Q * vA * (1 + FRAIS_C[c.a.ex]) - interet;
      verifies[c.k] = Math.round(net * 100) / 100;
      if (net < REGLES_C.gainMin) continue;
      st.push(db.prepare("INSERT INTO comptant (t, cle, base, quote, achat_ex, vente_ex, qte, px_achat, px_vente, frais, net, statut, interet, taux, regles) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)")
        .bind(now, c.k, c.a.base, c.a.quote, c.a.ex, c.b.ex, Q, vA, vB, Q * vA * FRAIS_C[c.a.ex] + Q * vB * FRAIS_C[c.b.ex], net, c.ecart > REGLES_C.ecartSuspect ? "attente" : "validé", interet, em.taux, REGLES_ID_C));
    } catch (e) { verifies[c.k] = "carnet illisible : " + String(e.message || e).slice(0, 60); }
  }

  }

  // ---------- Stratégie 2 : achat sur A + vente sur B, puis clôture quand l'écart s'inverse (vente sur A + achat sur B)
  const idx = new Map(lignes.map((x) => [x.ex + "|" + x.base + "/" + x.quote, x]));
  const ouvertes = (await db.prepare("SELECT * FROM comptant_pos WHERE statut='ouvert'").all()).results;
  const carnets = new Map(); const carnetCache = (x) => { const c = x.ex + "|" + x.sym; if (!carnets.has(c)) carnets.set(c, carnetR(env, x)); return carnets.get(c); };
  for (const p of ouvertes) {
    const a = idx.get(p.achat_ex + "|" + p.cle), b = idx.get(p.vente_ex + "|" + p.cle);
    if (!a || !b) continue;
    const fA = FRAIS_C[p.achat_ex], fB = FRAIS_C[p.vente_ex];
    let interet; try { interet = await coutPortage(p, now, b.sym); } catch (e) { interet = p.interet || 0; } // intérêts d'emprunt ou funding courus
    // 20.11.2026 (Pitch) : « net si on clôture maintenant » calculé comme la vraie clôture — vrais carnets pour toute la quantité,
    // frais et intérêts/funding compris (carnets lus une fois par scan et par marché, partagés entre les variantes)
    try {
      const [ca, cb] = await Promise.all([carnetCache(a), carnetCache(b)]);
      const sA = prixMoyenQ(ca.bids, p.qte), sB = prixMoyenQ(cb.asks, p.qte);
      if (!sA || !sB) { st.push(db.prepare("UPDATE comptant_pos SET interet=?, sortie_now=NULL, frais_sortie_now=NULL, maj=? WHERE id=?").bind(interet, now, p.id)); continue; } // carnet trop mince pour toute la quantité
      const fraisS = p.qte * sA * fA + p.qte * sB * fB;
      const sortie = p.qte * sA * (1 - fA) - p.qte * sB * (1 + fB) - interet;
      st.push(db.prepare("UPDATE comptant_pos SET interet=?, sortie_now=?, frais_sortie_now=?, maj=? WHERE id=?").bind(interet, sortie, fraisS, now, p.id));
      if (sortie < p.variante) continue;
      st.push(db.prepare("UPDATE comptant_pos SET statut='fermé', ferme=?, px_sortie_vente=?, px_sortie_achat=?, frais=frais+?, interet=?, net=entree+? WHERE id=? AND statut='ouvert'").bind(now, sA, sB, fraisS, interet, sortie, p.id));
    } catch (e) {}
  }
  let transf = null; try { transf = await lireTransferts(); } catch (e) {}
  const dejaOuv = new Set(ouvertes.map((p) => p.variante + "|" + p.cle));
  const nOuv = {}; for (const p of ouvertes) if (p.regles === REGLES_ID_C) nOuv[p.variante] = (nOuv[p.variante] || 0) + 1;
  // option A : un écart > 5 % n'est jamais pris tant qu'il dure (au-delà de 5 min il est ignoré) ; on n'entre qu'une fois revenu sous 5 %
  for (const c of cands.filter((c) => c.gain >= REGLES_C.entreeMin2 && c.ecart <= REGLES_C.ecartSuspect && !permanent(c)).slice(0, 6)) {
    const libres = REGLES_C.sorties.filter((v) => !dejaOuv.has(v + "|" + c.k) && (nOuv[v] || 0) < REGLES_C.maxOuvertes);
    if (!libres.length) continue;
    if (!transfertsOk(transf, c.a.ex, c.a.base) || !transfertsOk(transf, c.b.ex, c.b.base)) continue; // dépôts ou retraits suspendus (Gate/KuCoin)
    try {
      const [ca, cb] = await Promise.all([carnetR(env, c.a), carnetR(env, c.b)]);
      const Q = N / c.a.ask;
      const em = REGLES_C.shortSeul.includes(c.b.ex) ? { taux: 0 } : emprunt(marge, c.b.ex, c.b.base, Q); // Aster : short en perpétuel, pas d'emprunt
      if (!em) continue;
      const vA = prixMoyenQ(ca.asks, Q), vB = prixMoyenQ(cb.bids, Q);
      if (!vA || !vB) continue;
      const entree = Q * vB * (1 - FRAIS_C[c.b.ex]) - Q * vA * (1 + FRAIS_C[c.a.ex]);
      if (entree < REGLES_C.entreeMin2) continue;
      for (const v of libres) {
        st.push(db.prepare("INSERT INTO comptant_pos (variante, cle, base, quote, achat_ex, vente_ex, qte, px_achat, px_vente, ouvert, entree, frais, statut, taux, regles) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,'ouvert',?,?)")
          .bind(v, c.k, c.a.base, c.a.quote, c.a.ex, c.b.ex, Q, vA, vB, now, entree, Q * vA * FRAIS_C[c.a.ex] + Q * vB * FRAIS_C[c.b.ex], em.taux, REGLES_ID_C));
        dejaOuv.add(v + "|" + c.k); nOuv[v] = (nOuv[v] || 0) + 1;
      }
    } catch (e) {}
  }

  const top = cands.slice(0, 40).map((c) => ({ cle: c.k, achat: c.a.ex, ask: c.a.ask, vente: c.b.ex, bid: c.b.bid, ecart: c.ecart, gain: c.gain, approx: !!(c.a.approx || c.b.approx),
    permanent: permanent(c), transfertsFermes: !(transfertsOk(transf, c.a.ex, c.a.base) && transfertsOk(transf, c.b.ex, c.b.base)), verif: verifies[c.k] ?? null }));
  st.push(db.prepare("INSERT OR REPLACE INTO etat (id,t,json) VALUES (2,?,?)").bind(now, JSON.stringify({ statut, top, nActifs: par.size, transferts: transf?.statut || null })));
  for (let i = 0; i < st.length; i += 90) await db.batch(st.slice(i, i + 90));
}

export async function etatComptant(env) {
  const e = await env.DB.prepare("SELECT * FROM etat WHERE id=2").first();
  const trades = (await env.DB.prepare("SELECT * FROM comptant ORDER BY t DESC LIMIT 200").all()).results;
  const R = REGLES_ID_C;
  const tot = await env.DB.prepare("SELECT COUNT(*) n, SUM(net) net, SUM(frais) frais, SUM(interet) interet, MIN(t) debut FROM comptant WHERE statut='validé' AND regles=?").bind(R).first();
  const avant = await env.DB.prepare("SELECT (SELECT COUNT(*) FROM comptant WHERE statut='validé' AND (regles IS NULL OR regles<>?)) n1, (SELECT SUM(net) FROM comptant WHERE statut='validé' AND (regles IS NULL OR regles<>?)) net1, (SELECT COUNT(*) FROM comptant_pos WHERE statut='fermé' AND (regles IS NULL OR regles<>?)) n2, (SELECT SUM(net) FROM comptant_pos WHERE statut='fermé' AND (regles IS NULL OR regles<>?)) net2").bind(R, R, R, R).first();
  const marge = await env.DB.prepare("SELECT t, json FROM etat WHERE id=4").first();
  const att = await env.DB.prepare("SELECT COUNT(*) n, SUM(net) net FROM comptant WHERE statut='attente' AND regles=?").bind(R).first();
  const ann = await env.DB.prepare("SELECT COUNT(*) n, SUM(net) net FROM comptant WHERE statut='annulé' AND regles=?").bind(R).first();
  const pos = (await env.DB.prepare("SELECT * FROM comptant_pos ORDER BY COALESCE(ferme, ouvert) DESC LIMIT 300").all()).results;
  const tot2 = (await env.DB.prepare("SELECT variante, COUNT(*) n, SUM(net) net, SUM(frais) frais, SUM(interet) interet, AVG(ferme-ouvert) duree FROM comptant_pos WHERE statut='fermé' AND regles=? GROUP BY variante").bind(R).all()).results;
  const ouv2 = (await env.DB.prepare("SELECT variante, COUNT(*) n FROM comptant_pos WHERE statut='ouvert' AND regles=? GROUP BY variante").bind(R).all()).results;
  const mj = marge ? JSON.parse(marge.json) : null;
  return { reglesId: R, avant, empruntStatut: mj?.statut || null, tauxDefautH: TAUX_DEFAUT_H, regles: REGLES_C, frais: FRAIS_C, t: e?.t, scan: e ? JSON.parse(e.json) : null, trades, total: tot, attente: att, annules: ann, positions: pos, total2: tot2, ouvertes2: ouv2 };
}

// Clôture manuelle (bouton de la page) : sortie au vrai carnet pour toute la quantité, frais et intérêts compris
export async function fermerManuel(env, id) {
  const db = env.DB, now = Date.now();
  const p = await db.prepare("SELECT * FROM comptant_pos WHERE id=? AND statut='ouvert'").bind(id).first();
  if (!p) return { ok: false, err: "position introuvable ou déjà fermée" };
  const symA = (await lireComptant(p.achat_ex)).find((x) => x.base === p.base && x.quote === p.quote)?.sym;
  const symB = (await lireComptant(p.vente_ex)).find((x) => x.base === p.base && x.quote === p.quote)?.sym;
  if (!symA || !symB) return { ok: false, err: "marché introuvable" };
  const [ca, cb] = await Promise.all([carnetC({ ex: p.achat_ex, sym: symA }), carnetC({ ex: p.vente_ex, sym: symB })]);
  const sA = prixMoyenQ(ca.bids, p.qte), sB = prixMoyenQ(cb.asks, p.qte);
  if (!sA || !sB) return { ok: false, err: "carnet trop mince pour clôturer toute la quantité maintenant" };
  const fA = FRAIS_C[p.achat_ex], fB = FRAIS_C[p.vente_ex];
  const interet = await coutPortage(p, now, symB);
  const fraisS = p.qte * sA * fA + p.qte * sB * fB;
  const sortie = p.qte * sA * (1 - fA) - p.qte * sB * (1 + fB) - interet;
  const r = await db.prepare("UPDATE comptant_pos SET statut='fermé', ferme=?, px_sortie_vente=?, px_sortie_achat=?, frais=frais+?, interet=?, net=entree+?, raison='manuelle' WHERE id=? AND statut='ouvert'")
    .bind(now, sA, sB, fraisS, interet, sortie, id).run();
  if (!r.meta?.changes) return { ok: false, err: "la position venait d'être fermée automatiquement" };
  return { ok: true, net: p.entree + sortie, fraisSortie: fraisS, interet };
}
