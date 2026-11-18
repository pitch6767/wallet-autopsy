// Arbitrage AU COMPTANT — mode FANTÔME (aucun ordre réel).
// Principe : on suppose des pièces et des dollars déjà déposés sur chaque plateforme. Quand un actif s'achète
// moins cher sur A que ce qu'il se vend sur B, on achète sur A et on vend sur B dans la même seconde :
// le gain est acquis immédiatement (pas de position à fermer plus tard).
// Tourne dans le Moteur (Durable Object en Europe), après le scan des perpétuels.

export const REGLES_C = {
  mise: 10000,          // $ par trade (même mise que les perpétuels)
  gainMin: 50,          // $ net après frais des 2 achats/ventes
  ecartMaxPrix: 0.10,   // au-delà de 10 % ce n'est probablement pas le même jeton → ignoré
  volumeMin: 1e6,       // $ échangés sur 24 h sur chacune des 2 plateformes
  pauseMemeActifS: 60,  // un même actif ne compte qu'une fois par minute (le carnet doit se reconstituer)
};
// Frais « preneur » au comptant, palier de base (estimés, prudents)
export const FRAIS_C = { bybit: 0.001, okx: 0.001, kucoin: 0.001, gate: 0.002, mexc: 0.0005, bitget: 0.001, kraken: 0.008, coinbase: 0.012 };

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

// ---------- Scan
export async function tickComptant(env) {
  const now = Date.now(), N = REGLES_C.mise, db = env.DB;
  const statut = {}, lignes = [];
  await Promise.all(Object.entries(LECT).map(async ([ex, f]) => {
    const t0 = Date.now();
    try { const l = (await f()).filter((x) => x && x.bid > 0 && x.ask > 0 && x.ask >= x.bid).map((x) => ({ ...x, ex }));
      lignes.push(...l); statut[ex] = { ok: true, n: l.length, ms: Date.now() - t0 }; }
    catch (e) { statut[ex] = { ok: false, err: String(e.message || e).slice(0, 160) }; }
  }));
  // candidats : même jeton, même monnaie de cotation, toutes les paires de plateformes
  const par = new Map();
  for (const x of lignes) { if (!(x.vol >= REGLES_C.volumeMin)) continue; const k = x.base + "/" + x.quote; if (!par.has(k)) par.set(k, []); par.get(k).push(x); }
  const cands = [];
  for (const [k, l] of par) {
    let best = null;
    for (const a of l) for (const b of l) {
      if (a.ex === b.ex) continue;
      const ecart = b.bid / a.ask - 1;
      if (ecart <= 0 || ecart > REGLES_C.ecartMaxPrix) continue;
      const gain = N * ecart - N * (FRAIS_C[a.ex] + FRAIS_C[b.ex]);
      if (!best || gain > best.gain) best = { k, a, b, ecart, gain };
    }
    if (best) cands.push(best);
  }
  cands.sort((x, y) => y.gain - x.gain);
  const recents = new Set((await db.prepare("SELECT cle FROM comptant WHERE t > ?").bind(now - REGLES_C.pauseMemeActifS * 1000).all()).results.map((r) => r.cle));
  const verifies = {}, st = [];
  for (const c of cands.filter((c) => c.gain >= REGLES_C.gainMin).slice(0, 8)) {
    if (recents.has(c.k)) { verifies[c.k] = "déjà pris il y a moins d'une minute"; continue; }
    try {
      const [ca, cb] = await Promise.all([carnetC(c.a), carnetC(c.b)]);
      const Q = N / c.a.ask;
      const vA = prixMoyenQ(ca.asks, Q), vB = prixMoyenQ(cb.bids, Q);
      if (!vA || !vB) { verifies[c.k] = "carnet trop mince pour " + N + " $"; continue; }
      const achat = Q * vA * (1 + FRAIS_C[c.a.ex]), vente = Q * vB * (1 - FRAIS_C[c.b.ex]);
      const net = vente - achat;
      verifies[c.k] = Math.round(net * 100) / 100;
      if (net < REGLES_C.gainMin) continue;
      st.push(db.prepare("INSERT INTO comptant (t, cle, base, quote, achat_ex, vente_ex, qte, px_achat, px_vente, frais, net) VALUES (?,?,?,?,?,?,?,?,?,?,?)")
        .bind(now, c.k, c.a.base, c.a.quote, c.a.ex, c.b.ex, Q, vA, vB, Q * vA * FRAIS_C[c.a.ex] + Q * vB * FRAIS_C[c.b.ex], net));
    } catch (e) { verifies[c.k] = "carnet illisible : " + String(e.message || e).slice(0, 60); }
  }
  const top = cands.slice(0, 40).map((c) => ({ cle: c.k, achat: c.a.ex, ask: c.a.ask, vente: c.b.ex, bid: c.b.bid, ecart: c.ecart, gain: c.gain, approx: !!(c.a.approx || c.b.approx), verif: verifies[c.k] ?? null }));
  st.push(db.prepare("INSERT OR REPLACE INTO etat (id,t,json) VALUES (2,?,?)").bind(now, JSON.stringify({ statut, top, nActifs: par.size })));
  for (let i = 0; i < st.length; i += 90) await db.batch(st.slice(i, i + 90));
}

export async function etatComptant(env) {
  const e = await env.DB.prepare("SELECT * FROM etat WHERE id=2").first();
  const trades = (await env.DB.prepare("SELECT * FROM comptant ORDER BY t DESC LIMIT 300").all()).results;
  const tot = await env.DB.prepare("SELECT COUNT(*) n, SUM(net) net, SUM(frais) frais, MIN(t) debut FROM comptant").first();
  // pièces et dollars déplacés par plateforme (à rééquilibrer en réel)
  const mouv = (await env.DB.prepare("SELECT achat_ex ex, base, quote, SUM(qte) q, SUM(qte*px_achat) d FROM comptant GROUP BY achat_ex, base, quote UNION ALL SELECT vente_ex, base, quote, -SUM(qte), -SUM(qte*px_vente) FROM comptant GROUP BY vente_ex, base, quote").all()).results;
  return { regles: REGLES_C, frais: FRAIS_C, t: e?.t, scan: e ? JSON.parse(e.json) : null, trades, total: tot, mouvements: mouv };
}
