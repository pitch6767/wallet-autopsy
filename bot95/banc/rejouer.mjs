// Rejoue des enregistrements réels (rec_BTC : ~3 lignes/s, haut du carnet Polymarket + prix des bourses + Chainlink)
// à travers le moteur en mode signaux (MOTEUR=signaux), horloge simulée. Capture tous les signaux diffusés,
// les noms visibles produits à chaque achat (slNoms) et le temps de calcul par message.
// usage : node run.mjs <bundle.mjs> <fichier rec_BTC.json.gz> <sortie.json> [minutes max]
import fs from "node:fs";
import zlib from "node:zlib";
import { performance } from "node:perf_hooks";

const [bundle, recFile, outFile, maxMin] = process.argv.slice(2);
// ---- horloge simulée
let NOW = 0;
const RealDate = Date;
class FakeDate extends RealDate { constructor(...a) { if (a.length === 0) super(NOW); else super(...a); } static now() { return NOW; } }
globalThis.Date = FakeDate;
// ---- hasard reproductible
let seed = 12345; Math.random = () => { seed = (seed * 1103515245 + 12345) % 2147483648; return seed / 2147483648; };
// ---- minuteries : désactivées (le moteur en mode signaux n'en a pas besoin pour décider)
globalThis.setTimeout = () => 0; globalThis.setInterval = () => 0; globalThis.clearInterval = () => {}; globalThis.clearTimeout = () => {};
globalThis.fetch = async () => { throw new Error("hors ligne (banc d'essai)"); };

const M = await import(bundle);
const store = new Map();
const state = {
  storage: { get: async (k) => store.get(k), put: async (k, v) => { if (typeof k === "object") for (const [a, b] of Object.entries(k)) store.set(a, b); else store.set(k, v); }, list: async () => new Map(), delete: async () => {}, getAlarm: async () => null, setAlarm: async () => {} },
  blockConcurrencyWhile: (fn) => fn(), getWebSockets: () => [],
};
const env = { MOTEUR: "signaux", SIGNAL_FLUX: "oui", MODE_REEL: "non", SIGNAL_NUMS: "101,105,107,112,109,120,121,31,127,129,35,32,201,28,119" };
const bot = new M.Bot(state, env);
await bot.ready;
const signaux = [], noms = [];
bot.slDiffuser = (c) => { signaux.push(c); return 1; };
const slNoms0 = bot.slNoms.bind(bot);
bot.slNoms = (P) => { const r = slNoms0(P); if (r.length) noms.push([P.strat, P.heure, P.cote, P.prix, r.map((x) => x.nom + "×" + x.mult).join(";")]); return r; };
// compteur par cycle et par côté (CONSENSUS 6/8, « + idées » ≥ 10) relevé après chaque achat qui l'a fait bouger
const comptes = [], slEmettre0 = bot.slEmettre.bind(bot);
bot.slEmettre = (P, mk) => { const av = ((bot._slT || {})[P.start] || {})[P.cote] || 0; slEmettre0(P, mk); const ap = ((bot._slT || {})[P.start] || {})[P.cote] || 0; if (ap !== av) comptes.push([P.start, P.cote, P.heure, ap]); };

// ---- données
const D = JSON.parse(zlib.gunzipSync(fs.readFileSync(recFile)).toString());
const lignes = []; for (const k of Object.keys(D).sort((a, b) => +a.split(":")[2] - +b.split(":")[2])) for (const l of D[k].lignes) lignes.push(l);
lignes.sort((a, b) => a[0] - b[0]);
const C = Object.fromEntries(D[Object.keys(D)[0]].colonnes.map((c, i) => [c, i]));
const lim = maxMin ? lignes[0][0] + 60 * +maxMin : Infinity;

const temps = { poly: [], perp: [], okx: [], cb: [], bn: [], cl: [] };
const mesure = (k, f) => { const t0 = performance.now(); f(); temps[k].push(performance.now() - t0); };
let prev = {}, nMsg = 0, cycleCour = null, dernierTick = 0;
for (const l of lignes) {
  const t = l[C.t]; if (t > lim) break;
  NOW = Math.round(t * 1000);
  const st = l[C.start];
  if (st !== cycleCour) {   // nouveau cycle : fiche de marché (comme chargerMarche) + prix à battre enregistré
    cycleCour = st;
    bot.mk.BTC = { start: st, end: st + 300, slug: "btc-updown-5m-" + st, up: "U" + st, down: "D" + st, marketId: "m" + st, conditionId: "c" + st };
    prev.pab = null; prev.u = null; prev.d = null;
  }
  const mk = bot.mk.BTC;
  if (l[C.prix_a_battre] != null && mk.strike == null && t >= st + 2) { mk.strike = +l[C.prix_a_battre]; mk.twapK = true; mk.strikeSrc = "moyenne Chainlink 60 s"; }
  if (Math.floor(t) !== dernierTick) {   // une fois par seconde : ce que fait tick() pour les fantômes (DUO, contrarien, positions échues)
    dernierTick = Math.floor(t);
    try { bot.duoMinute(); } catch (_) {} try { bot.contraTick(); } catch (_) {}
    bot.N.ouvertes = bot.N.ouvertes.filter((P) => t < P.end);
  }
  try { bot.echantillonner(); } catch (_) {}
  const ch = (k) => l[C[k]] != null && l[C[k]] !== prev[k];
  if (ch("chainlink")) { nMsg++; mesure("cl", () => bot.surCl({ topic: "crypto_prices_chainlink", payload: { symbol: "btc/usd", value: l[C.chainlink], timestamp: NOW - 800 }, timestamp: NOW - 700 })); }
  if (ch("binance_spot")) { nMsg++; mesure("bn", () => bot.noter("BTC", "bn", +l[C.binance_spot], NOW / 1000)); }
  if (ch("coinbase")) { nMsg++; mesure("cb", () => bot.surCb({ channel: "ticker", events: [{ tickers: [{ product_id: "BTC-USD", price: String(l[C.coinbase]) }] }] })); }
  if (ch("okx_perp")) { nMsg++; mesure("okx", () => { const tt = NOW / 1000; bot.noter("BTC", "okx", +l[C.okx_perp], tt); bot.v1Declencher("BTC", "okx", tt - 0.05, tt); }); }
  if (ch("bybit_perp")) { nMsg++; const up = prev.bybit_perp == null || l[C.bybit_perp] >= prev.bybit_perp;
    mesure("perp", () => bot.surPerp({ topic: "publicTrade.BTCUSDT", data: [{ T: NOW - 30, p: String(l[C.bybit_perp]), v: "0.05", S: up ? "Buy" : "Sell" }] })); }
  // carnet Polymarket (haut du carnet seulement) : instantané au 1er message du cycle, puis variations ; échanges déduits d'une taille qui baisse au même prix
  for (const [tok, cb, ca, cbs, cas, key] of [[mk.up, "up_achat", "up_vente", "up_achat_taille", "up_vente_taille", "u"], [mk.down, "down_achat", "down_vente", "down_achat_taille", "down_vente_taille", "d"]]) {
    const b = l[C[cb]], a = l[C[ca]], bs = l[C[cbs]], as = l[C[cas]], p = prev[key];
    const cur = { b, a, bs, as };
    if (!p) {
      nMsg++; mesure("poly", () => bot.surPoly({ event_type: "book", asset_id: tok, bids: b != null ? [{ price: String(b), size: String(bs || 0) }] : [], asks: a != null ? [{ price: String(a), size: String(as || 0) }] : [], timestamp: String(NOW - 120) }));
    } else {
      const chg = [];
      if (p.b !== b) { if (p.b != null) chg.push({ asset_id: tok, price: String(p.b), size: "0", side: "BUY" }); if (b != null) chg.push({ asset_id: tok, price: String(b), size: String(bs || 0), side: "BUY" }); }
      else if (p.bs !== bs && b != null) chg.push({ asset_id: tok, price: String(b), size: String(bs || 0), side: "BUY" });
      if (p.a !== a) { if (p.a != null) chg.push({ asset_id: tok, price: String(p.a), size: "0", side: "SELL" }); if (a != null) chg.push({ asset_id: tok, price: String(a), size: String(as || 0), side: "SELL" }); }
      else if (p.as !== as && a != null) chg.push({ asset_id: tok, price: String(a), size: String(as || 0), side: "SELL" });
      if (p.a === a && a != null && as < p.as) { nMsg++; mesure("poly", () => bot.surPoly({ event_type: "last_trade_price", asset_id: tok, price: String(a), size: String(p.as - as), side: "BUY", timestamp: String(NOW - 150) })); }
      if (p.b === b && b != null && bs < p.bs) { nMsg++; mesure("poly", () => bot.surPoly({ event_type: "last_trade_price", asset_id: tok, price: String(b), size: String(p.bs - bs), side: "SELL", timestamp: String(NOW - 150) })); }
      if (chg.length) { nMsg++; mesure("poly", () => bot.surPoly({ event_type: "price_change", price_changes: chg, timestamp: String(NOW - 120) })); }
    }
    prev[key] = cur;
  }
  for (const k of ["chainlink", "binance_spot", "coinbase", "okx_perp", "bybit_perp"]) if (l[C[k]] != null) prev[k] = l[C[k]];
}
const q = (v, p) => { if (!v.length) return null; const s = [...v].sort((a, b) => a - b); return s[Math.min(s.length - 1, Math.floor(p * s.length))]; };
const perf = Object.fromEntries(Object.entries(temps).map(([k, v]) => [k, { n: v.length, moy_ms: v.length ? +(v.reduce((a, b) => a + b, 0) / v.length).toFixed(4) : null, p99_ms: v.length ? +q(v, 0.99).toFixed(4) : null, total_ms: +v.reduce((a, b) => a + b, 0).toFixed(1) }]));
const tot = Object.values(temps).flat();
const sortie = { messages: nMsg, perf, total_ms: +tot.reduce((a, b) => a + b, 0).toFixed(1), moy_ms: +(tot.reduce((a, b) => a + b, 0) / tot.length).toFixed(4), p99_ms: +q(tot, 0.99).toFixed(4),
  signaux: signaux.map((c) => ({ ...c })), noms, comptes, journal: (bot._slJ || []).map((x) => ({ ...x, clients: undefined })), erreurs: bot.diag.erreurs, cy: bot._slT, statut: (() => { try { return bot.sgStatut().perf || null; } catch (e) { return String(e); } })() };
fs.writeFileSync(outFile, JSON.stringify(sortie));
console.log(JSON.stringify({ messages: nMsg, signaux: signaux.length, noms: noms.length, total_ms: sortie.total_ms, moy_ms: sortie.moy_ms, p99_ms: sortie.p99_ms, perf, erreurs: bot.diag.erreurs.slice(0, 5) }, null, 0));
