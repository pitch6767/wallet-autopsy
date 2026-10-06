import { Reel } from "./reel.js";
// bot95 v2 — option A sur les 7 cryptos 5 min de Polymarket (BTC, ETH, SOL, XRP, DOGE, BNB, HYPE).
// MODE FANTÔME : aucun ordre réel, aucune clé. Le bot note ce qu'il aurait fait.
// Règle Polymarket : Up si moyenne Chainlink 60 s à la fin >= moyenne 60 s au début (prix d'exercice publié par Polymarket).

const ACTIFS = {
  // règles validées le 04.10.2026 (test 7 jours, zéro perte) : fenêtre (s avant la fin), prix du favori, distance mini (écarts-types)
  BTC: { bybit: "BTCUSDT", spot: "BTC-USD", regles: [{ W: 90, pmin: 0.95, pmax: 0.999, z: 6 }] },
  ETH: { bybit: "ETHUSDT", spot: "ETH-USD", regles: [{ W: 120, pmin: 0.95, pmax: 0.999, z: 6 }] },
  SOL: { bybit: "SOLUSDT", spot: "SOL-USD", regles: [{ W: 90, pmin: 0.95, pmax: 0.999, z: 4 }] },
  XRP: { bybit: "XRPUSDT", spot: "XRP-USD", regles: [{ W: 30, pmin: 0.95, pmax: 0.999, z: 2.5 }] },
  DOGE: { bybit: "DOGEUSDT", spot: "DOGE-USD", regles: [{ W: 90, pmin: 0.95, pmax: 0.999, z: 4 }] },
  BNB: { bybit: "BNBUSDT", spot: null, regles: [{ W: 30, pmin: 0.95, pmax: 0.999, z: 2.5 }] },
  HYPE: { bybit: "HYPEUSDT", spot: null, regles: [{ W: 60, pmin: 0.95, pmax: 0.999, z: 3 }] },
};
const LISTE = Object.keys(ACTIFS);
// ---- stratégies fantômes ajoutées le 05.10.2026 (idées 19-25, 29, 30), aucun argent réel
const NV = {
  ASSUR: { RETRAIT: 0.03, CALME_S: 2, OPP_MAX: 0.95,                       // assurance graduée à la place du stop (baisse de proba -> part couverte)
    VARIANTES: { "assurance 6/9/12": [[0.06, 0.25], [0.09, 0.5], [0.12, 1.0]], "assurance 4/7/10": [[0.04, 0.25], [0.07, 0.5], [0.10, 1.0]] } },
  FIN: { BTC: { W: 180, LO: 0.70, HI: 0.85, SEUIL: 0.95 }, ETH: { W: 90, LO: 0.70, HI: 0.90, SEUIL: 0.93 }, MISE: 50 },
  MM: { ACTIFS: ["BTC", "ETH"], ARRET_S: 10, MAXI: 100,                    // teneur de marché : 3 versions en parallèle (06.10.2026)
    VARIANTES: {                                                            // « actuel » et « pencher » arrêtés le 06.10.2026 (perdants en direct)
      "mm prudent": { MARGE: 0.12, DESEQ: 10, PAQUET: 10, PENCHER: 0.04, RETRAIT_PB: 2 } } },
};
const BB_COLONNES = ["t", "bybit_perp", "okx_perp", "coinbase", "binance_spot", "chainlink", "bybit_meilleur_achat", "bybit_meilleure_vente",
  "prof_achat_1pb", "prof_vente_1pb", "prof_achat_3pb", "prof_vente_3pb", "prof_achat_5pb", "prof_vente_5pb", "prof_achat_10pb", "prof_vente_10pb", "niveaux_achat", "niveaux_vente",
  "perp_achats_usd", "perp_ventes_usd", "perp_plus_gros_achat", "perp_plus_grosse_vente", "perp_nb_echanges", "liq_longs_usd", "liq_courts_usd",
  "pm_up_achats_top3", "pm_up_ventes_top3", "pm_down_achats_top3", "pm_down_ventes_top3",
  "pm_up_flux[retrait_achat,retrait_vente,ajout_achat,ajout_vente,echange_achat,echange_vente]", "pm_down_flux[idem]"];

const CFG = {
  MARGE_MODELE: 0.01,          // proba calculée >= prix + 1 pt (au-dessus de 0,98 : prix + la moitié de ce qui reste jusqu'à 1)
  COURSE_FACTEUR: 2,           // temps pour que la moyenne atteigne le prix d'exercice > 2 x temps restant
  FRAICHEUR_S: 5,              // une source plus vieille que 5 s = pas de trade
  ECART_MAX: 0.02,             // écart achat/vente maxi
  LIQ_CONTRE_USD: 250000,      // liquidations contre nous sur 10 s
  DESEQ_CONTRE: 0.6,           // déséquilibre du carnet perp contre nous (5 premiers niveaux)
  SD_ECART_REL: 8e-4,          // incertitude du prix d'exercice publié en direct par Polymarket : écart max mesuré 0,08 % (validé le 05.10.2026)
  SORTIE_Z: 1.0,               // sortie d'urgence si la distance passe sous 1 écart-type
  FEE_RATE: 0.072,             // frais taker : parts x 0,072 x p x (1-p)
  CAPITAL: 200, MISE: 50, PART_REINVEST: 1 / 3, PART_RESERVE: 2 / 3,
  ANNONCES: [[12 * 60 + 28, 12 * 60 + 40], [13 * 60 + 58, 14 * 60 + 10], [17 * 60 + 58, 18 * 60 + 10]],  // jours ouvrés, UTC
};
// V1 — stratégie de Pitch filtrée (validée le 05.10.2026) : jambe à 0,55–0,56 si proba >= 0,55 + marge, offre opposée à valeur (<= 0,43),
// stop si la proba de la jambe passe sous 0,50, sortie à 0,90 si jambe seule, fusion si paire. BTC 5 min, décisions à chaque message (temps réel).
// Réglage A (validé le 05.10.2026) : élan du perp sur 5 s dans le sens de la jambe + stop si la proba perd 15 points depuis l'entrée.
const V1 = { ACTIFS: ["BTC", "ETH"], REEL: ["BTC"], OKX: { BTC: "BTC-USDT-SWAP", ETH: "ETH-USDT-SWAP" }, ACTIF: "BTC", MARGE: 0.08, PMIN: 0.55, PMAX: 0.56, OPP_MAX: 0.43, STOP_REL: 0.15, ELAN_S: 5, TP: 0.90, CAPITAL: 200, MISE: 50 };
const WMAX = (a) => Math.max(...ACTIFS[a].regles.map((r) => r.W));

const G = "https://gamma-api.polymarket.com";
const C = "https://clob.polymarket.com";

export default {
  async fetch(req, env) { return stub(env).fetch(req); },
  async scheduled(_e, env, ctx) { ctx.waitUntil(stub(env).fetch("https://bot95/api/reveil")); },
};
const stub = (env) => env.BOT.get(env.BOT.idFromName("bot95"), { locationHint: "weur" });

const phi = (x) => 0.5 * (1 + erf(x / Math.SQRT2));
function erf(x) {
  const s = Math.sign(x); x = Math.abs(x);
  const t = 1 / (1 + 0.3275911 * x);
  return s * (1 - (((((1.061405429 * t - 1.453152027) * t) + 1.421413741) * t - 0.284496736) * t + 0.254829592) * t * Math.exp(-x * x));
}
const med = (a) => { if (!a.length) return null; const b = [...a].sort((x, y) => x - y); return b[Math.floor(b.length / 2)]; };
const now = () => Date.now() / 1000;
const r1 = (x) => Math.round(x * 10) / 10;
const fmt = (x, p) => (Math.abs(p) >= 100 ? x.toFixed(2) : Math.abs(p) >= 1 ? x.toFixed(4) : x.toFixed(6));

// temps d'aller-retour (ms) vers Polymarket depuis l'endroit où tourne le code
async function mesurerLatence() {
  const cibles = { carnet: `${C}/time`, gamma: `${G}/events?limit=1` };
  const out = {};
  for (const [k, url] of Object.entries(cibles)) {
    const v = [];
    for (let i = 0; i < 6; i++) { const t0 = Date.now(); try { await (await fetch(url, { headers: { "User-Agent": "sonde" } })).text(); v.push(Date.now() - t0); } catch (_) {} }
    v.sort((x, y) => x - y);
    out[k] = { min: v[0], mediane: v[Math.floor(v.length / 2)], max: v[v.length - 1] };
  }
  try { const cf = await (await fetch("https://cloudflare.com/cdn-cgi/trace")).text(); out.lieu = (cf.match(/colo=(\w+)/) || [])[1]; } catch (_) {}
  return out;
}

// idée 2 : Binance accepte-t-il Cloudflare par ses flux publics ? Et qui est en avance sur qui (Binance, Bybit, OKX) ?
async function sondeBinance(duree = 20) {
  const out = { http: {}, flux: {}, avance_sur_bybit_ms: {} };
  const http = { "api.binance.com (spot)": "https://api.binance.com/api/v3/time", "data-api.binance.vision (spot)": "https://data-api.binance.vision/api/v3/time",
    "fapi.binance.com (perp)": "https://fapi.binance.com/fapi/v1/time", "api.binance.us": "https://api.binance.us/api/v3/time" };
  for (const [k, u] of Object.entries(http)) { try { const r = await fetch(u); out.http[k] = r.status + " " + (await r.text()).slice(0, 80); } catch (err) { out.http[k] = "erreur " + String(err.message || err).slice(0, 80); } }
  const flux = {
    binance_spot_vision: ["https://data-stream.binance.vision/ws/btcusdt@trade", null],
    binance_spot: ["https://stream.binance.com:9443/ws/btcusdt@trade", null],
    binance_spot_443: ["https://stream.binance.com:443/ws/btcusdt@trade", null],
    binance_perp: ["https://fstream.binance.com/ws/btcusdt@aggTrade", null],
    binance_us: ["https://stream.binance.us:9443/ws/btcusd@trade", null],
    bybit_perp: ["https://stream.bybit.com/v5/public/linear", JSON.stringify({ op: "subscribe", args: ["publicTrade.BTCUSDT"] })],
    bybit_spot: ["https://stream.bybit.com/v5/public/spot", JSON.stringify({ op: "subscribe", args: ["publicTrade.BTCUSDT"] })],
    okx_perp: ["https://ws.okx.com:8443/ws/v5/public", JSON.stringify({ op: "subscribe", args: [{ channel: "trades", instId: "BTC-USDT-SWAP" }] })],
    coinbase: ["https://ws-feed.exchange.coinbase.com", JSON.stringify({ type: "subscribe", product_ids: ["BTC-USD"], channels: ["matches"] })],
  };
  const arr = {}, lag = {}, ouverts = [];
  await Promise.all(Object.entries(flux).map(async ([k, [u, abo]]) => {
    try {
      const r = await fetch(u, { headers: { Upgrade: "websocket" } });
      if (!r.webSocket) { out.flux[k] = "refusé HTTP " + r.status + " " + (await r.text().catch(() => "")).slice(0, 100); return; }
      const ws = r.webSocket; ws.accept(); ouverts.push(ws); arr[k] = []; lag[k] = [];
      ws.addEventListener("message", (ev) => {
        const t = Date.now(); let m; try { m = JSON.parse(ev.data); } catch (_) { return; }
        let L = [];
        if (m.e === "trade" || m.e === "aggTrade") L = [[+m.p, +m.T]];
        else if (Array.isArray(m.data) && m.topic) L = m.data.map((x) => [+x.p, +x.T]);
        else if (Array.isArray(m.data) && m.arg) L = m.data.map((x) => [+x.px, +x.ts]);
        else if (m.type === "match" || m.type === "last_match") L = [[+m.price, Date.parse(m.time)]];
        for (const [p, te] of L) { if (p) { arr[k].push([t, p]); if (te) lag[k].push(t - te); } }
      });
      if (abo) ws.send(abo);
      out.flux[k] = "connecté";
    } catch (err) { out.flux[k] = "erreur " + String(err.message || err).slice(0, 100); }
  }));
  await new Promise((r) => setTimeout(r, duree * 1000));
  for (const ws of ouverts) { try { ws.close(); } catch (_) {} }
  const t0 = Math.max(...Object.values(arr).filter((a) => a.length).map((a) => a[0][0]));
  const pas = 50, n = Math.floor((duree * 1000 - 2000) / pas);
  const grille = (a) => { const g = []; let i = 0, last = null; for (let j = 0; j < n; j++) { const tt = t0 + j * pas; while (i < a.length && a[i][0] <= tt) last = a[i++][1]; g.push(last); } return g; };
  const ret = (g) => g.map((x, i) => (i && x && g[i - 1] ? Math.log(x / g[i - 1]) : 0));
  const corr = (a, b, d) => { let sab = 0, saa = 0, sbb = 0; for (let i = Math.max(0, d); i < a.length && i - d < b.length; i++) { if (i - d < 0) continue; sab += a[i] * b[i - d]; saa += a[i] ** 2; sbb += b[i - d] ** 2; } return saa && sbb ? sab / Math.sqrt(saa * sbb) : 0; };
  const rb = arr.bybit_perp && arr.bybit_perp.length > 20 ? ret(grille(arr.bybit_perp)) : null;
  for (const [k, a] of Object.entries(arr)) {
    const lg = lag[k].slice().sort((x, y) => x - y);
    out.flux[k] = { messages: a.length, retard_median_ms: lg.length ? lg[Math.floor(lg.length / 2)] : null };
    if (rb && k !== "bybit_perp" && a.length > 20) {
      const rx = ret(grille(a)); let best = [0, -1];
      for (let d = -40; d <= 40; d++) { const c = corr(rb, rx, d); if (c > best[1]) best = [d * pas, c]; }   // d>0 : k bouge avant Bybit
      out.avance_sur_bybit_ms[k] = { avance_ms: best[0], correlation: +best[1].toFixed(2) };
    }
  }
  try { const cf = await (await fetch("https://cloudflare.com/cdn-cgi/trace")).text(); out.lieu = (cf.match(/colo=(\w+)/) || [])[1]; } catch (_) {}
  return out;
}

export class Sonde {
  constructor(state, env) { this.state = state; }
  async fetch() { return Response.json(await mesurerLatence()); }
}

export class Bot {
  constructor(state, env) {
    this.state = state; this.env = env;
    this.f = {}; this.sec = {}; this.liq = {}; this.deseq = {}; this.livre = {}; this.mk = {};
    for (const a of LISTE) { this.f[a] = {}; this.sec[a] = new Map(); this.liq[a] = []; this.deseq[a] = 0; this.livre[a] = { b: new Map(), a: new Map() }; }
    this.ws = {};
    this.diag = { reconnexions: {}, erreurs: [] };
    this.pb = {}; this.latPoly = []; this.latDec = [];
    this.reel = new Reel(env);
    this._v1t = {}; this._sgA = {}; this._okxB = {}; this.mkNx = {};
    this.ready = this.state.blockConcurrencyWhile(async () => {
      this.N = (await this.state.storage.get("nouveaux")) || { depuis: now(), strats: {}, ouvertes: [], attente: [] };
      for (const [ancien, neuf] of [["assurance", "assurance 6/9/12"], ["mm", "mm actuel"]]) {
        for (const k of Object.keys(this.N.strats)) if (k.startsWith(ancien + " ") && k.split(" ").length === 2) { this.N.strats[neuf + " " + k.split(" ")[1]] = this.N.strats[k]; delete this.N.strats[k]; }
        for (const P of [...this.N.ouvertes, ...this.N.attente]) if (P.strat === ancien) P.strat = neuf;
      }
      this.e = (await this.state.storage.get("etat2")) || {
        capital: CFG.CAPITAL, mise: CFG.MISE, reserve: 0, pnl: 0, gains: 0, pertes: 0, pause: false,
        positions: [], attente: [], trades: [], vetos: {}, candidats: {}, parActif: {}, refus: [], verif: [], depuis: now(),
      };
      this.e.pause = false;   // plus de pause après perte (décision du 05.10.2026)
      if (!this.e.V1x) this.e.V1x = {};
      for (const a of ["ETH"]) if (!this.e.V1x[a]) this.e.V1x[a] = { capital: V1.CAPITAL, mise: V1.MISE, reserve: 0, pnl: 0, gains: 0, pertes: 0, entrees: 0, pos: null, attente: [], trades: [], issues: {}, depuis: now() };
      if (!this.e.V1) this.e.V1 = { capital: V1.CAPITAL, mise: V1.MISE, reserve: 0, pnl: 0, gains: 0, pertes: 0, entrees: 0, pos: null, attente: [], trades: [], issues: {}, depuis: now() };
    });
  }

  // ------------------------------------------------------------------ HTTP
  async fetch(req) {
    await this.ready;
    this.demarrer();
    const u = new URL(req.url);
    const json = (x) => Response.json(x, { headers: { "cache-control": "no-store" } });
    if (u.pathname === "/api/etat") return json(this.vue());
    if (u.pathname === "/api/reprendre" && req.method === "POST") { this.e.pause = false; await this.sauver(); return json({ ok: true }); }
    if (u.pathname === "/api/reveil") return json({ ok: true });
    if (u.pathname === "/api/verif") return json({ verif: this.e.verif });
    if (u.pathname === "/api/v1/trades") return json({ BTC: this.e.V1.trades, ETH: this.e.V1x.ETH.trades });
    if (u.pathname === "/api/reel/etat") {
      const r = { configure: this.reel.configure(), modeReel: this.reel.modeReel(), arret: !!this.e.reelStop, mise: +this.env.MISE_REEL || null,
        signataire: this.reel.signataire || null, portefeuille: this.env.POLY_ADRESSE_PORTEFEUILLE || null, journal: this.reel.journal.slice(0, 20) };
      if (r.configure) { try { r.solde = await this.reel.solde(); } catch (err) { r.erreurSolde = String(err.message || err).slice(0, 200); } }
      return json(r);
    }
    if (u.pathname === "/api/reel/test" && req.method === "POST") {
      if (!this.reel.configure()) return json({ ok: false, erreur: "clés absentes" });
      const mb = this.mk.BTC; if (!mb || !mb.up) return json({ ok: false, erreur: "marché BTC pas encore chargé" });
      return json(await this.reel.test(mb.up));
    }
    if (u.pathname === "/api/reel/arret" && req.method === "POST") {
      this.e.reelStop = true; await this.sauver();
      let r = null; try { if (this.reel.configure()) r = await this.reel.toutAnnuler(); } catch (err) { r = String(err); }
      return json({ ok: true, arret: true, annulation: r });
    }
    if (u.pathname === "/api/reel/reprise" && req.method === "POST") { this.e.reelStop = false; await this.sauver(); return json({ ok: true, arret: false }); }
    if (u.pathname === "/api/binance") return json(await sondeBinance(Math.min(60, +(u.searchParams.get("s") || 20))));
    if (u.pathname === "/api/sondes") {
      const regions = ["weur", "eeur", "enam", "wnam", "apac"];
      const r = await Promise.all(regions.map(async (rg) => {
        try { return [rg, await (await this.env.SONDE.get(this.env.SONDE.idFromName("sonde-" + rg), { locationHint: rg }).fetch("https://sonde/")).json()]; }
        catch (err) { return [rg, { erreur: String(err) }]; }
      }));
      r.push(["bot actuel", await mesurerLatence()]);
      return json(Object.fromEntries(r));
    }
    if (u.pathname === "/api/v1debug") {
      const mb = this.mk.BTC || {};
      return json({ maintenant: now(), polyCycle: this.polyCycle, mk: { start: mb.start, slug: mb.slug, up: mb.up, down: mb.down, strike: mb.strike }, wsPoly: !!this.ws.poly, ouvert: this.ws.poly_ouvert,
        livres: Object.fromEntries(Object.keys(this.pb).map((id) => [id.slice(0, 8), { bids: this.livreTrie(id, "bids").slice(0, 4), asks: this.livreTrie(id, "asks").slice(0, 4) }])),
        derniers: this.polyRaw || [], proba: mb.up ? this.probaV1("BTC", mb) : null, sg: this._sg || null });
    }
    if (u.pathname === "/api/boite") {
      const n = Math.min(40, +(u.searchParams.get("n") || 20)), apres = u.searchParams.get("apres");
      const m = await this.state.storage.list({ prefix: "bb:", limit: n, ...(apres ? { startAfter: apres } : {}) });
      const ks = [...m.keys()];
      return json({ cles: ks, docs: [...m.values()], suivant: ks.length ? ks[ks.length - 1] : null });
    }
    if (u.pathname === "/api/boite/compte") {
      const m = await this.state.storage.list({ prefix: "bb:", limit: 5000 }), par = {};
      for (const k of m.keys()) { const [, , a, ty] = k.split(":"); par[a + " " + ty] = (par[a + " " + ty] || 0) + 1; }
      return json({ total: m.size, par, echantillons_en_memoire: Object.fromEntries(Object.entries(this.bbR || {}).map(([a, R]) => [a, R.length])), derniere_ligne: this.bbR && this.bbR.BTC ? this.bbR.BTC.slice(-1)[0] : null });
    }
    if (u.pathname === "/api/nouveaux") return json(this.nVue());
    if (u.pathname === "/nouveaux") return new Response(PAGE_N, { headers: { "content-type": "text/html; charset=utf-8" } });
    if (u.pathname === "/api/rapport") return json({ refus: this.e.refus });
    if (u.pathname === "/rapport") return new Response(RAPPORT, { headers: { "content-type": "text/html; charset=utf-8" } });
    return new Response(PAGE, { headers: { "content-type": "text/html; charset=utf-8" } });
  }

  demarrer() {
    this.ouvrirFlux();
    this.state.storage.getAlarm().then((a) => { if (!a || a < Date.now() - 5000) this.state.storage.setAlarm(Date.now() + 1000); });
  }
  // ------------------------------------------------------------------ boîte noire (enregistrement seulement)
  // toutes les 100 ms : prix de chaque bourse, carnet Bybit (profondeur à 1/3/5/10 pb), flux et liquidations, carnets et flux Polymarket.
  // On garde 10 s en mémoire ; sauvegarde à l'entrée, à la première alerte (proba -8 pts) et au stop de chaque trade V1.
  bbAcc(a) { return ((this.bbA = this.bbA || {})[a] = this.bbA[a] || { ach: 0, ven: 0, max_ach: 0, max_ven: 0, n: 0, liq_longs: 0, liq_courts: 0 }); }
  pmAcc(id) { return ((this.pmA = this.pmA || {})[id] = this.pmA[id] || { retrait_achat: 0, retrait_vente: 0, ajout_achat: 0, ajout_vente: 0, echange_achat: 0, echange_vente: 0 }); }
  echantillonner() {
    const t = now();
    for (const a of V1.ACTIFS) {
      const L = this.livre[a], mk = this.mk[a] || {};
      const b = [...L.b].map(([p, q2]) => [+p, q2]).sort((x, y) => y[0] - x[0]), k = [...L.a].map(([p, q2]) => [+p, q2]).sort((x, y) => x[0] - y[0]);
      const mid = b.length && k.length ? (b[0][0] + k[0][0]) / 2 : null;
      const prof = (cote, bps) => mid ? Math.round(cote.filter(([p]) => Math.abs(p / mid - 1) * 1e4 <= bps).reduce((s2, [p, q2]) => s2 + p * q2, 0)) : null;
      const px = (src) => (this.f[a][src] ? this.f[a][src].p : null);
      const ac = this.bbAcc(a);
      const pmTop = (id, cote) => this.livreTrie(id, cote).slice(0, 3).map(([p, s2]) => [p, Math.round(s2)]);
      const pmF = (id) => { if (!id) return null; const z = this.pmAcc(id), r = Object.values(z).map(Math.round); for (const kk of Object.keys(z)) z[kk] = 0; return r; };
      const ligne = [+t.toFixed(2), px("perp"), px("okx"), px("cb"), px("bn"), px("cl"),
        b.length ? b[0][0] : null, k.length ? k[0][0] : null, prof(b, 1), prof(k, 1), prof(b, 3), prof(k, 3), prof(b, 5), prof(k, 5), prof(b, 10), prof(k, 10), b.length, k.length,
        Math.round(ac.ach), Math.round(ac.ven), Math.round(ac.max_ach), Math.round(ac.max_ven), ac.n, Math.round(ac.liq_longs), Math.round(ac.liq_courts),
        mk.up ? pmTop(mk.up, "bids") : null, mk.up ? pmTop(mk.up, "asks") : null, mk.down ? pmTop(mk.down, "bids") : null, mk.down ? pmTop(mk.down, "asks") : null,
        pmF(mk.up), pmF(mk.down)];
      for (const kk of Object.keys(ac)) ac[kk] = 0;
      const R = ((this.bbR = this.bbR || {})[a] = this.bbR[a] || []);
      R.push(ligne); if (R.length > 100) R.shift();
    }
  }
  bbSauver(pos, type) {
    try {
      const a = pos.actif || "BTC", R = (this.bbR || {})[a];
      if (!R || !R.length) return;
      const t = now(), cle = "bb:" + Math.floor(t * 1000).toString().padStart(14, "0") + ":" + a + ":" + type;
      const doc = { actif: a, type, t, start: pos.start, cote: pos.cote, prixEntree: pos.prix, probaEntree: pos.proba, probaActuelle: pos.probaActuelle, heure: pos.heure,
        colonnes: BB_COLONNES, lignes: R.slice() };
      this.state.storage.put(cle, doc).catch(() => {});
      this.bbN = (this.bbN || 0) + 1;
      if (this.bbN % 50 === 0) this.state.storage.list({ prefix: "bb:", limit: 5000 }).then((m) => { const ks = [...m.keys()]; if (ks.length > 3000) this.state.storage.delete(ks.slice(0, ks.length - 3000).slice(0, 128)); }).catch(() => {});
    } catch (err) { this.erreur("boîte noire", err); }
  }

  async alarm() {
    await this.ready;
    try { await this.tick(); } catch (err) { this.erreur("tick", err); }
    this.ouvrirFlux();
    await this.state.storage.setAlarm(Date.now() + 1000);
  }
  erreur(ou, err) {
    this.diag.erreurs.unshift(`${new Date().toISOString().slice(11, 19)} ${ou}: ${String((err && err.message) || err).slice(0, 140)}`);
    this.diag.erreurs.length = Math.min(this.diag.erreurs.length, 20);
  }
  async sauver() { await this.state.storage.put("etat2", this.e); }

  // ------------------------------------------------------------------ flux
  ageMax(src) { const t = now(); let m = 0; for (const a of LISTE) { const x = this.f[a][src]; if (src === "cb" && !ACTIFS[a].spot) continue; m = Math.max(m, x ? t - x.t : 1e9); } return m; }
  ouvrirFlux() {
    const t = now(), depuis = (k) => t - (this.ws[k + "_ouvert"] || 0);
    if (!this.bbI) this.bbI = setInterval(() => { try { this.echantillonner(); } catch (_) {} }, 100);
    const ageBn = Math.max(...V1.ACTIFS.map((a) => (this.f[a].bn ? t - this.f[a].bn.t : 1e9)));
    if (!this.ws.bn || (ageBn > 30 && depuis("bn") > 30))
      this.connecter("bn", "https://stream.binance.com:443/stream?streams=" + V1.ACTIFS.map((a) => a.toLowerCase() + "usdt@trade").join("/"), [], (m) => {
        const d = m.data || {}, a = V1.ACTIFS.find((k) => k + "USDT" === d.s);
        if (a && +d.p > 0) this.noter(a, "bn", +d.p, now());
      });
    if (!this.ws.perp || (this.ageMax("perp") > 20 && depuis("perp") > 20)) {
      for (const a of LISTE) this.livre[a] = { b: new Map(), a: new Map() };
      const args = LISTE.flatMap((a) => [`publicTrade.${ACTIFS[a].bybit}`, `orderbook.50.${ACTIFS[a].bybit}`, `allLiquidation.${ACTIFS[a].bybit}`]);
      this.connecter("perp", "https://stream.bybit.com/v5/public/linear", [JSON.stringify({ op: "subscribe", args })], (m) => this.surPerp(m), JSON.stringify({ op: "ping" }), 10000);
    }
    if (!this.ws.cb || (this.ageMax("cb") > 30 && depuis("cb") > 30)) {
      const ids = LISTE.map((a) => ACTIFS[a].spot).filter(Boolean);
      this.connecter("cb", "https://advanced-trade-ws.coinbase.com", [JSON.stringify({ type: "subscribe", product_ids: ids, channel: "ticker" })], (m) => this.surCb(m));
    }
    const ageOkx = Math.max(...V1.ACTIFS.map((a) => (this.f[a].okx ? t - this.f[a].okx.t : 1e9)));
    if (!this.ws.okx || (ageOkx > 20 && depuis("okx") > 20))
      this.connecter("okx", "https://ws.okx.com:8443/ws/v5/public", [JSON.stringify({ op: "subscribe", args: V1.ACTIFS.map((a) => ({ channel: "trades", instId: V1.OKX[a] })) })], (m) => {
        const arg = m.arg || {}, x = (m.data || []).slice(-1)[0], a = V1.ACTIFS.find((k) => V1.OKX[k] === arg.instId);
        if (arg.channel === "trades" && x && a) { const tt = now(); this.noter(a, "okx", +x.px, tt); this.v1Declencher(a, "okx", +x.ts / 1000, tt); }
      }, "ping", 20000);
    const mb = this.mk.BTC;
    const jetons = [];
    for (const a of V1.ACTIFS) {
      const mc = this.mk[a], nx = this.mkNx[a];
      if (mc && mc.up) jetons.push(mc.up, mc.down);
      if (nx && nx.up && (!mc || nx.start > mc.start)) jetons.push(nx.up, nx.down);
    }
    const cle = jetons.join(",");
    if (jetons.length && (this.polyCle !== cle || (!this.ws.poly && depuis("poly") > 3))) {
      this.polyCle = cle; this.polyCycle = mb && mb.start;
      for (const id of Object.keys(this.pb)) if (!jetons.includes(id)) delete this.pb[id];
      this.connecter("poly", "https://ws-subscriptions-clob.polymarket.com/ws/market", [JSON.stringify({ assets_ids: jetons, type: "market" })], (m) => this.surPoly(m), "PING", 10000);
    }
    if (!this.ws.cl || (this.ageMax("cl") > 20 && depuis("cl") > 20)) this.connecter("cl", "https://ws-live-data.polymarket.com",
      [JSON.stringify({ action: "subscribe", subscriptions: [{ topic: "crypto_prices_chainlink", type: "*", filters: "" }] })], (m) => this.surCl(m), "PING", 5000);
  }

  async connecter(nom, url, abos, surMsg, ping, periode) {
    if (this.ws[nom + "_en_cours"]) return;
    this.ws[nom + "_en_cours"] = true;
    try {
      try { this.ws[nom] && this.ws[nom].close(); } catch (_) {}
      this.ws[nom] = null;
      const r = await fetch(url, { headers: { Upgrade: "websocket" } });
      const ws = r.webSocket;
      if (!ws) throw new Error("pas de websocket (HTTP " + r.status + ")");
      ws.accept();
      ws.addEventListener("message", (ev) => {
        if (typeof ev.data !== "string" || ev.data === "PONG" || ev.data === "PING" || ev.data === "pong") return;
        try { surMsg(JSON.parse(ev.data)); } catch (_) {}
      });
      const fin = () => { if (this.ws[nom] === ws) this.ws[nom] = null; };
      ws.addEventListener("close", (ev) => { clearInterval(ws.pinger); fin(); this.erreur("flux " + nom + " fermé", "code " + ev.code); });
      ws.addEventListener("error", fin);
      for (const a of abos || []) ws.send(a);
      if (ping) ws.pinger = setInterval(() => { try { ws.send(ping); } catch (_) { clearInterval(ws.pinger); } }, periode || 5000);
      this.ws[nom] = ws; this.ws[nom + "_ouvert"] = now();
      this.diag.reconnexions[nom] = (this.diag.reconnexions[nom] || 0) + 1;
    } catch (err) { this.erreur("flux " + nom, err); }
    this.ws[nom + "_en_cours"] = false;
  }

  noter(a, k, p, t) {
    this.f[a][k] = { p, t };
    const s = Math.floor(t), m = this.sec[a];
    let o = m.get(s);
    if (!o) { o = {}; m.set(s, o); if (m.size > 700) m.delete(m.keys().next().value); }
    o[k] = p;
  }
  actifBybit(sym) { return LISTE.find((a) => ACTIFS[a].bybit === sym); }

  surPerp(m) {
    const tp = m.topic || "", t = now();
    const a = this.actifBybit(tp.split(".").pop());
    if (!a) return;
    if (tp.startsWith("publicTrade")) {
      if (V1.ACTIFS.includes(a)) { const ac = this.bbAcc(a); for (const y of m.data || []) { const u2 = +y.v * +y.p; ac.n++; if (y.S === "Buy") { ac.ach += u2; ac.max_ach = Math.max(ac.max_ach, u2); } else { ac.ven += u2; ac.max_ven = Math.max(ac.max_ven, u2); } } }
      const x = (m.data || []).slice(-1)[0];
      if (x) { this.noter(a, "perp", +x.p, t); if (V1.ACTIFS.includes(a)) this.v1Declencher(a, "perp", +x.T / 1000, t); }
    }
    else if (tp.startsWith("allLiquidation")) {
      for (const x of m.data || []) this.liq[a].push({ t, cote: x.S === "Buy" ? "SELL" : "BUY", usd: (+x.v) * (+x.p) });   // Buy = position longue liquidée
      if (V1.ACTIFS.includes(a)) { const ac = this.bbAcc(a); for (const x of m.data || []) { if (x.S === "Buy") ac.liq_longs += (+x.v) * (+x.p); else ac.liq_courts += (+x.v) * (+x.p); } }
      this.liq[a] = this.liq[a].filter((x) => x.t > t - 30);
    } else if (tp.startsWith("orderbook")) {
      const d = m.data || {}, L = m.type === "snapshot" ? (this.livre[a] = { b: new Map(), a: new Map() }) : this.livre[a];
      for (const [p, q] of d.b || []) +q ? L.b.set(p, +q) : L.b.delete(p);
      for (const [p, q] of d.a || []) +q ? L.a.set(p, +q) : L.a.delete(p);
      const px = this.f[a].perp ? this.f[a].perp.p : null;
      if (px) { for (const k of [...L.b.keys()]) if (+k > px * 1.0002) L.b.delete(k); for (const k of [...L.a.keys()]) if (+k < px * 0.9998) L.a.delete(k); }
      const bs = [...L.b].sort((x, y) => y[0] - x[0]).slice(0, 5).reduce((s, x) => s + x[1], 0);
      const as = [...L.a].sort((x, y) => x[0] - y[0]).slice(0, 5).reduce((s, x) => s + x[1], 0);
      if (as + bs > 0) this.deseq[a] = (bs - as) / (as + bs);
    }
  }
  surCb(m) {
    if (m.channel !== "ticker") return;
    for (const ev of m.events || []) for (const x of ev.tickers || []) {
      const a = LISTE.find((k) => ACTIFS[k].spot === x.product_id);
      if (a && x.price) this.noter(a, "cb", +x.price, now());
    }
  }
  surCl(m) {
    if (m.topic !== "crypto_prices_chainlink") return;
    const p = m.payload || {}, sym = (p.symbol || "").toUpperCase().split("/")[0];
    if (!ACTIFS[sym] || !(+p.value > 0)) return;
    this.noter(sym, "cl", +p.value, now());
  }

  serie(a, k, n) {
    const t = Math.floor(now()), out = []; let last = null;
    for (let s = t - n; s <= t; s++) { const o = this.sec[a].get(s); if (o && o[k] != null) last = o[k]; if (last != null) out.push([s, last]); }
    return out;
  }
  prixA(a, k, s) { for (let i = 0; i < 6; i++) { const o = this.sec[a].get(s - i); if (o && o[k] != null) return o[k]; } return null; }
  moyenne(a, k, de, a2) { const v = []; for (let s = de; s <= a2; s++) { const x = this.prixA(a, k, s); if (x) v.push(x); } return v.length ? v.reduce((x, y) => x + y, 0) / v.length : null; }

  // ------------------------------------------------------------------ marchés
  async chargerMarche(a, start) {
    const ev = await (await fetch(`${G}/events?slug=${a.toLowerCase()}-updown-5m-${start}`)).json();
    const e = ev && ev[0], m = e && e.markets && e.markets[0];
    if (!m) throw new Error(a + " marché introuvable " + start);
    const outs = JSON.parse(m.outcomes || "[]"), toks = JSON.parse(m.clobTokenIds || "[]");
    const iUp = outs.findIndex((o) => String(o).toLowerCase() === "up");
    return { slug: e.slug, up: toks[iUp], down: toks[1 - iUp] };
  }
  async ouvertureOfficielle(a, mk) {
    const iso = (t) => new Date(t * 1000).toISOString().replace(".000", "");
    const r = await fetch(`https://polymarket.com/api/crypto/crypto-price?symbol=${a}&eventStartTime=${iso(mk.start)}&variant=fiveminute&endDate=${iso(mk.end)}`, { headers: { "User-Agent": "Mozilla/5.0", Accept: "application/json" } });
    if (!r.ok) throw new Error(a + " prix d'ouverture HTTP " + r.status);
    const d = await r.json();
    if (d && +d.openPrice > 0) mk.strike = +d.openPrice;
  }
  async carnets(tokens) {
    const r = await fetch(`${C}/books`, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(tokens.map((t) => ({ token_id: t }))) });
    if (!r.ok) throw new Error("carnets HTTP " + r.status);
    const out = {};
    for (const b of await r.json()) out[b.asset_id] = {
      asks: (b.asks || []).map((x) => [+x.price, +x.size]).sort((x, y) => x[0] - y[0]),
      bids: (b.bids || []).map((x) => [+x.price, +x.size]).sort((x, y) => y[0] - x[0]),
    };
    return out;
  }

  // ------------------------------------------------------------------ boucle
  async tick() {
    const t = now(), start = Math.floor(t / 300) * 300, tleft = start + 300 - t;
    await Promise.all(LISTE.map(async (a) => {
      let mk = this.mk[a];
      if (!mk || mk.start !== start) {
        if (mk) this.finFenetre(a, mk);
        mk = this.mk[a] = (V1.ACTIFS.includes(a) && this.mkNx[a] && this.mkNx[a].start === start) ? { ...this.mkNx[a] } : { start, end: start + 300 };
      }
      try {
        if (!mk.slug && t - (mk.essai || 0) > 10) { mk.essai = t; Object.assign(mk, await this.chargerMarche(a, start)); }
        if (!mk.strike && t - (mk.essaiOff || 0) > 15) { mk.essaiOff = t; await this.ouvertureOfficielle(a, mk); }
      } catch (err) { if (tleft < 200) this.erreur(a, err); }
    }));
    // V1 : préchargement du cycle BTC suivant (carnet en direct prêt dès la première seconde)
    const nx = start + 300;
    if (tleft < 150 && t - (this._nxEssai || 0) > 10) {
      this._nxEssai = t;
      for (const a of V1.ACTIFS) if (!this.mkNx[a] || this.mkNx[a].start !== nx) { try { this.mkNx[a] = { start: nx, end: nx + 300, ...(await this.chargerMarche(a, nx)) }; } catch (_) {} }
    }
    for (const p of this.e.positions.filter((x) => x.end <= t)) this.e.attente.push(p);
    this.e.positions = this.e.positions.filter((x) => x.end > t);
    await this.resoudre();
    if (this.enReel()) {
      if (t - (this._chaud || 0) > 20) { this._chaud = t; this.reel.rechauffer(); }
      const pv = this.e.V1.pos; if (pv && pv.reel && pv.offreId) this.v1SuivreOffre(pv);
    }
    if (t - (this._nr || 0) > 15) { this._nr = t; await this.nRegler(); }
    if (t - (this._v1r || 0) > 15 || V1.ACTIFS.some((a) => { const P = this.v1Etat(a).pos; return P && t >= P.end; })) { this._v1r = t; for (const a of V1.ACTIFS) await this.v1Regler(a); }
    // carnets des marchés dans leur fenêtre d'achat ou avec une position ouverte
    const actifs = LISTE.filter((a) => { const mk = this.mk[a]; return mk.slug && tleft >= 1 && (tleft <= WMAX(a) || this.e.positions.some((p) => p.actif === a && p.start === start)); });
    if (!actifs.length) return;
    let books;
    try { books = await this.carnets(actifs.flatMap((a) => [this.mk[a].up, this.mk[a].down])); } catch (err) { this.erreur("carnets", err); return; }
    for (const a of actifs) {
      const mk = this.mk[a], bu = books[mk.up], bd = books[mk.down];
      if (!bu || !bd) continue;
      const pos = this.e.positions.find((p) => p.actif === a && p.start === start);
      if (pos) this.surveiller(a, pos, tleft, pos.fav === "Up" ? bu : bd);
      else if (!mk.entre) this.decider(a, mk, tleft, bu, bd);
    }
    await this.sauver();
  }

  calcul(a, mk, tleft, favUp) {
    const K = mk.strike, cl = this.f[a].cl, S = cl && cl.p;
    const perp = this.serie(a, "perp", 300);
    if (!K || !S || perp.length < 60) return null;
    const r = [];
    for (let i = 1; i < perp.length; i++) r.push(Math.log(perp[i][1] / perp[i - 1][1]));
    const mo = r.reduce((x, y) => x + y, 0) / r.length;
    const sg = Math.sqrt(r.reduce((x, y) => x + (y - mo) ** 2, 0) / r.length) || 1e-6;
    const dir = favUp ? 1 : -1, ts = Math.floor(now()), deb = mk.end - 59;
    const connus = [];
    for (let s = deb; s <= ts; s++) { const v = this.prixA(a, "cl", s); if (v) connus.push(v); }
    const nr = Math.max(1, mk.end - Math.max(ts, deb - 1));
    const somme = connus.reduce((x, y) => x + y, 0), n = connus.length + nr;
    const E = (somme + nr * S) / n;
    const sd = Math.sqrt((sg * S * Math.sqrt(nr ** 3 / 3) / 60) ** 2 + (CFG.SD_ECART_REL * S) ** 2);
    const z = ((E - K) * dir) / sd;
    const p0 = this.prixA(a, "perp", ts), p5 = this.prixA(a, "perp", ts - 5);
    const v = p0 && p5 ? ((p0 - p5) / 5) * dir : 0, vE = v * nr / 60, dist = (E - K) * dir;
    const base = (k) => med(this.serie(a, k, 120).map(([s2, p]) => { const c = this.prixA(a, "cl", s2); return c ? p - c : null; }).filter((x) => x != null));
    const cote = (src) => { const x = this.f[a][src]; const b = base(src); return x == null || b == null ? null : (((somme + nr * (x.p - b)) / n - K) * dir > 0); };
    return { K, S, E, z, proba: phi(z), dist, v, tStrike: vE < 0 ? dist / -vE : 999, accordPerp: cote("perp"), accordSpot: ACTIFS[a].spot ? cote("cb") : true };
  }

  protections(a, mk, tleft, favUp, prix, c) {
    const t = now(), age = (k) => (this.f[a][k] ? t - this.f[a][k].t : 1e9);
    const X = (raison, explication) => ({ raison, explication });
    const sources = [["Chainlink", "cl"], ["perp Bybit", "perp"]].concat(ACTIFS[a].spot ? [["spot Coinbase", "cb"]] : []);
    const vieilles = sources.filter(([, k]) => age(k) > CFG.FRAICHEUR_S);
    if (vieilles.length) return X("source figée ou absente", vieilles.map(([n, k]) => `${n} sans nouveau prix depuis ${age(k) > 1e8 ? "toujours" : r1(age(k)) + " s"}`).join(", ") + ` (maximum ${CFG.FRAICHEUR_S} s).`);
    const minute = new Date().getUTCHours() * 60 + new Date().getUTCMinutes(), jour = new Date().getUTCDay();
    if (jour >= 1 && jour <= 5 && CFG.ANNONCES.some(([x, y]) => minute >= x && minute <= y)) return X("annonce économique", "Créneau d'annonce économique américaine.");
    if (!c) return X("données insuffisantes", mk.strike ? "Pas encore 5 minutes d'historique du perp." : "Prix d'exercice Polymarket pas encore reçu.");
    if (c.accordPerp !== true || c.accordSpot !== true) return X("sources pas d'accord", `Moyenne attendue ${r1(Math.abs(c.dist))} ${favUp ? "au-dessus" : "en dessous"} du prix d'exercice selon Chainlink, mais ${c.accordPerp !== true ? "le perp" : ""}${c.accordPerp !== true && c.accordSpot !== true ? " et " : ""}${c.accordSpot !== true ? "le spot" : ""} ne confirme pas.`);
    const marge = Math.min(CFG.MARGE_MODELE, (1 - prix) / 2);
    if (c.proba < prix + marge) return X("modèle pas assez sûr", `Probabilité calculée ${(c.proba * 100).toFixed(2)} %, il faut au moins ${((prix + marge) * 100).toFixed(2)} %.`);
    if (c.tStrike <= CFG.COURSE_FACTEUR * tleft) return X("course vers le prix d'exercice", `Le prix va vers le prix d'exercice : la moyenne l'atteindrait en ${r1(c.tStrike)} s, il reste ${Math.round(tleft)} s.`);
    const contre = this.liq[a].filter((x) => x.t > t - 10 && (favUp ? x.cote === "SELL" : x.cote === "BUY")).reduce((s, x) => s + x.usd, 0);
    if (contre >= CFG.LIQ_CONTRE_USD) return X("liquidations contre nous", `${Math.round(contre).toLocaleString("fr-CH")} $ liquidés contre le favori en 10 s.`);
    const dq = favUp ? -this.deseq[a] : this.deseq[a];
    if (dq >= CFG.DESEQ_CONTRE) return X("carnet perp contre nous", `Le carnet du perp penche à ${Math.round(dq * 100)} % contre le favori.`);
    return null;
  }

  refuser(a, mk, raison, explication, d) {
    mk.raison = raison;
    mk.refus = { raison, explication, ...d };
    (mk.comptes = mk.comptes || {})[raison] = (mk.comptes[raison] || 0) + 1;
  }

  decider(a, mk, tleft, bu, bd) {
    const e = this.e;
    const askU = bu.asks[0] ? bu.asks[0][0] : 1, askD = bd.asks[0] ? bd.asks[0][0] : 1;
    const bidU = bu.bids[0] ? bu.bids[0][0] : 0, bidD = bd.bids[0] ? bd.bids[0][0] : 0;
    const favUp = bidU + (askU < 1 ? askU : bidU) >= bidD + (askD < 1 ? askD : bidD);
    const bk = favUp ? bu : bd, ask = favUp ? askU : askD, bid = favUp ? bidU : bidD;
    // règles de l'actif applicables à ce moment
    const regles = ACTIFS[a].regles.filter((r) => tleft <= r.W);
    const enBande = regles.filter((r) => ask >= r.pmin && ask <= r.pmax);
    if (!regles.some((r) => bid >= r.pmin || ask <= r.pmax && ask >= r.pmin)) return;   // pas de favori dans nos bandes de prix
    mk.candidat = true;
    const c = this.calcul(a, mk, tleft, favUp);
    const d = c ? { tleft: Math.round(tleft), ask, bid, fav: favUp ? "Up" : "Down", z: +c.z.toFixed(2), proba: +c.proba.toFixed(4), dist: c.dist } : { tleft: Math.round(tleft), ask, bid, fav: favUp ? "Up" : "Down" };
    if (!enBande.length) return this.refuser(a, mk, "aucun vendeur dans la bande de prix", `Favori ${favUp ? "Up" : "Down"} : meilleur vendeur ${ask >= 1 ? "aucun" : ask}, meilleur acheteur ${bid}. Bandes : ${regles.map((r) => r.pmin + "–" + r.pmax).join(", ")}.`, d);
    const p = this.protections(a, mk, tleft, favUp, ask, c);
    if (p) return this.refuser(a, mk, p.raison, p.explication, d);
    const regle = enBande.find((r) => c.z >= r.z);
    if (!regle) { const r0 = enBande[0]; return this.refuser(a, mk, "distance trop faible", `Moyenne attendue à ${fmt(c.dist, c.S)} du prix d'exercice, soit ${c.z.toFixed(2)} écart-type ; il en faut ${enBande.map((r) => r.z).join(" ou ")} (fenêtre ${r0.W} s, prix ${ask}).`, d); }
    if (ask - bid > CFG.ECART_MAX) return this.refuser(a, mk, "écart achat/vente trop large", `Vendeur ${ask}, acheteur ${bid}.`, d);
    const engage = e.positions.reduce((s, x) => s + x.mise, 0);
    const mise = Math.min(e.mise, e.capital - e.reserve - engage);
    if (mise < 5) return this.refuser(a, mk, "capital déjà engagé", `Capital disponible ${(e.capital - e.reserve - engage).toFixed(2)} $ (d'autres positions sont ouvertes).`, d);
    let reste = mise, parts = 0, cout = 0;
    for (const [px, sz] of bk.asks) {
      if (px > regle.pmax) break;
      const prendre = Math.min(sz, reste / px);
      parts += prendre; cout += prendre * px; reste -= prendre * px;
      if (reste < 0.01) break;
    }
    if (reste >= 0.01) return this.refuser(a, mk, "pas assez de parts au prix", `Seulement ${parts.toFixed(1)} parts jusqu'à ${regle.pmax} pour ${mise.toFixed(2)} $.`, d);
    const pm = cout / parts;
    mk.entre = true;
    e.positions.push({
      actif: a, start: mk.start, end: mk.end, slug: mk.slug, fav: favUp ? "Up" : "Down", token: favUp ? mk.up : mk.down,
      prix: +pm.toFixed(4), parts: +parts.toFixed(2), mise: +cout.toFixed(2), frais: +(parts * CFG.FEE_RATE * pm * (1 - pm)).toFixed(3),
      tleft: Math.round(tleft), z: +c.z.toFixed(2), regle: `${regle.W} s, ${regle.pmin}–${regle.pmax}, z ${regle.z}`, heure: new Date().toISOString(),
    });
  }

  surveiller(a, pos, tleft, bk) {
    if (tleft < 1 || pos.sorti) return;
    const c = this.calcul(a, this.mk[a], tleft, pos.fav === "Up");
    if (!c || c.z >= CFG.SORTIE_Z) return;
    let reste = pos.parts, recu = 0;
    for (const [p, s] of bk.bids) { const v = Math.min(s, reste); recu += v * p; reste -= v; if (reste <= 0) break; }
    if (reste > 0) return;
    const ps = recu / pos.parts;
    pos.sorti = { prix: +ps.toFixed(4), z: +c.z.toFixed(2), tleft: Math.round(tleft) };
    pos.net = +(recu - pos.mise - pos.frais - pos.parts * CFG.FEE_RATE * ps * (1 - ps)).toFixed(2);
    this.e.positions = this.e.positions.filter((x) => x !== pos);
    this.cloturer(pos, "sortie d'urgence");
  }

  finFenetre(a, mk) {
    const e = this.e;
    if (mk.candidat) {
      e.candidats[a] = (e.candidats[a] || 0) + 1;
      if (!mk.entre && mk.raison) { (e.vetos[a] = e.vetos[a] || {})[mk.raison] = (e.vetos[a][mk.raison] || 0) + 1; }
      if (!mk.entre && mk.refus) {
        e.refus.unshift({ actif: a, heure: new Date(mk.start * 1000).toISOString(), slug: mk.slug, strike: mk.strike || null, ...mk.refus, comptes: mk.comptes || {} });
        e.refus.length = Math.min(e.refus.length, 300);
      }
    }
    for (const p of e.positions.filter((x) => x.actif === a && x.start === mk.start)) e.attente.push(p);
    e.positions = e.positions.filter((x) => !(x.actif === a && x.start === mk.start));
    if (mk.slug) {
      e.verif.unshift({ actif: a, slug: mk.slug, start: mk.start, k: mk.strike || null, fin: this.moyenne(a, "cl", mk.end - 59, mk.end), fait: false });
      e.verif.length = Math.min(e.verif.length, 150);
    }
  }

  async resoudre() {
    const t = now();
    if (this.dernierCheck && t - this.dernierCheck < 15) return;
    this.dernierCheck = t;
    const lire = async (slug) => {
      const ev = await (await fetch(`${G}/events?slug=${slug}`)).json();
      const e0 = ev[0], m = e0.markets[0];
      let meta = e0.eventMetadata || m.eventMetadata || {}; if (typeof meta === "string") meta = JSON.parse(meta);
      const px = JSON.parse(m.outcomePrices || "[]").map(Number), outs = JSON.parse(m.outcomes || "[]");
      if (!(px.includes(1) && px.includes(0))) return null;
      return { gagnant: outs[px.indexOf(1)], k: meta.priceToBeat != null ? +meta.priceToBeat : null, fin: meta.finalPrice != null ? +meta.finalPrice : null };
    };
    const garder = [];
    for (const pos of this.e.attente) {
      if (t < pos.end + 20) { garder.push(pos); continue; }
      try {
        const r = await lire(pos.slug);
        if (!r) { garder.push(pos); continue; }
        const gagne = String(r.gagnant).toLowerCase() === pos.fav.toLowerCase();
        pos.net = +((gagne ? pos.parts - pos.mise : -pos.mise) - pos.frais).toFixed(2);
        this.cloturer(pos, gagne ? "gagné" : "perdu");
      } catch (err) { garder.push(pos); this.erreur("résolution", err); }
    }
    this.e.attente = garder;
    for (const v of this.e.verif.filter((v) => !v.fait && t > v.start + 360).slice(0, 4)) {
      try {
        const r = await lire(v.slug);
        if (!r || r.k == null) continue;
        Object.assign(v, { kOff: r.k, finOff: r.fin, gagnant: r.gagnant, ecartK: v.k ? +(v.k - r.k).toPrecision(4) : null, ecartFin: v.fin && r.fin ? +(v.fin - r.fin).toPrecision(4) : null, fait: true });
      } catch (err) { this.erreur("vérif", err); }
    }
  }

  cloturer(pos, resultat) {
    const e = this.e;
    pos.resultat = resultat;
    e.capital += pos.net; e.pnl += pos.net;
    const pa = (e.parActif[pos.actif] = e.parActif[pos.actif] || { trades: 0, gains: 0, pertes: 0, pnl: 0 });
    pa.trades++; pa.pnl += pos.net;
    if (pos.net >= 0) { e.gains++; pa.gains++; e.reserve += pos.net * CFG.PART_RESERVE; e.mise += pos.net * CFG.PART_REINVEST; }
    else { e.pertes++; pa.pertes++; }
    e.mise = Math.min(e.mise, Math.max(0, e.capital - e.reserve));
    e.trades.unshift(pos);
    e.trades.length = Math.min(e.trades.length, 400);
  }

  // ------------------------------------------------------------------ V1 temps réel
  surPoly(m) {
    if (Array.isArray(m)) { for (const x of m) this.surPoly(x); return; }
    (this.polyRaw = this.polyRaw || []).unshift(JSON.stringify(m).slice(0, 300)); this.polyRaw.length = Math.min(this.polyRaw.length, 6);
    const t = now(), ts = +m.timestamp > 1e12 ? +m.timestamp / 1000 : +m.timestamp;
    if (ts) { this.latPoly.push(t - ts); if (this.latPoly.length > 400) this.latPoly.shift(); }
    const livre = (id) => (this.pb[id] = this.pb[id] || { bids: new Map(), asks: new Map() });
    const ev = m.event_type;
    if (ev === "book") {
      const L = livre(m.asset_id); L.bids = new Map((m.bids || []).map((x) => [+x.price, +x.size])); L.asks = new Map((m.asks || []).map((x) => [+x.price, +x.size]));
    } else if (ev === "price_change") {
      const ch = m.price_changes || (m.changes || []).map((c) => ({ ...c, asset_id: m.asset_id }));
      for (const c of ch) {
        const L = livre(c.asset_id), cote = c.side === "BUY" ? L.bids : L.asks, avant = cote.get(+c.price) || 0, apres = +c.size;
        if (apres < avant) this.noterFlux(c.asset_id, "retrait_" + (c.side === "BUY" ? "achat" : "vente"), (avant - apres) * +c.price, t);
        { const z = this.pmAcc(c.asset_id), cs = c.side === "BUY" ? "achat" : "vente"; if (apres < avant) z["retrait_" + cs] += (avant - apres) * +c.price; else z["ajout_" + cs] += (apres - avant) * +c.price; }
        apres ? cote.set(+c.price, apres) : cote.delete(+c.price);
      }
    } else if (ev === "last_trade_price") {
      this.noterFlux(m.asset_id, "echange_" + (m.side === "BUY" ? "achat" : "vente"), +m.price * +m.size, t);
      this.pmAcc(m.asset_id)["echange_" + (m.side === "BUY" ? "achat" : "vente")] += +m.price * +m.size;
      this.v1Echange(m.asset_id, m.side, +m.price, +m.size);
    } else return;
    const id = m.asset_id || ((m.price_changes || [])[0] || {}).asset_id;
    const a = this.actifDuJeton(id);
    if (a) try { this.v1Eval("poly", ts || t, a); } catch (err) { this.erreur("V1", err); }
  }

  // flux du carnet Polymarket par jeton (10 dernières secondes) : retraits d'ordres et échanges
  noterFlux(id, type, usd, t) {
    const L = ((this.fluxPm = this.fluxPm || {})[id] = this.fluxPm[id] || []);
    L.push([t, type, usd]);
    while (L.length && L[0][0] < t - 30) L.shift();
  }
  sommeFlux(id, type, sec) { const t = now(); return (((this.fluxPm || {})[id]) || []).filter((x) => x[1] === type && x[0] > t - sec).reduce((a2, x) => a2 + x[2], 0); }

  // photo des signaux non historisés au moment d'une entrée (pour l'analyse ultérieure)
  signauxEntree(a, up, id, autre) {
    const t = now(), d = up ? 1 : -1;
    const liq = (sec, contre) => this.liq[a].filter((x) => x.t > t - sec && (contre ? (up ? x.cote === "SELL" : x.cote === "BUY") : (up ? x.cote === "BUY" : x.cote === "SELL"))).reduce((s2, x) => s2 + x.usd, 0);
    const prof = (jid, cote, n) => this.livreTrie(jid, cote).slice(0, n).reduce((s2, x) => s2 + x[0] * x[1], 0);
    const r = (x) => Math.round(x);
    return {
      liq10_contre: r(liq(10, true)), liq10_pour: r(liq(10, false)), liq30_contre: r(liq(30, true)),
      deseq_perp: +(d * this.deseq[a]).toFixed(2),
      pm_notre_achats_5niv: r(prof(id, "bids", 5)), pm_notre_ventes_5niv: r(prof(id, "asks", 5)),
      pm_autre_achats_5niv: r(prof(autre, "bids", 5)), pm_autre_ventes_5niv: r(prof(autre, "asks", 5)),
      pm_retraits_achat_notre10: r(this.sommeFlux(id, "retrait_achat", 10)), pm_retraits_vente_notre10: r(this.sommeFlux(id, "retrait_vente", 10)),
      pm_retraits_achat_autre10: r(this.sommeFlux(autre, "retrait_achat", 10)), pm_retraits_vente_autre10: r(this.sommeFlux(autre, "retrait_vente", 10)),
      pm_achats_notre10: r(this.sommeFlux(id, "echange_achat", 10)), pm_achats_autre10: r(this.sommeFlux(autre, "echange_achat", 10)),
      source_rapide: (this.sourceRapideA || {})[a] || null,
    };
  }

  // idée 1 : pendant le trade, note le premier moment où les teneurs de marché retirent leurs achats sur notre jeton
  // (retraits hors échanges), où le côté opposé est acheté fort, où notre meilleur prix d'achat recule — enregistrement seulement
  v1Alertes(pos) {
    const t = now(), bids = this.livreTrie(pos.token, "bids"), bb = bids.length ? bids[0][0] : null;
    if (bb == null) return;
    const al = (pos.alertes = pos.alertes || {}), t0 = Date.parse(pos.heure) / 1000;
    pos.bidMax = Math.max(pos.bidMax || 0, bb);
    const retr = Math.max(0, this.sommeFlux(pos.token, "retrait_achat", 3) - this.sommeFlux(pos.token, "echange_vente", 3));
    const opp = this.sommeFlux(pos.autre, "echange_achat", 3) + this.sommeFlux(pos.token, "echange_vente", 3);
    const note = (k) => { if (!al[k]) al[k] = { s: +(t - t0).toFixed(1), bid: bb, proba: pos.probaActuelle }; };
    for (const x of [50, 100, 250, 500]) if (retr >= x) note("retrait_achats_3s_" + x + "usd");
    for (const x of [50, 100, 250]) if (opp >= x) note("achats_opposes_3s_" + x + "usd");
    for (const x of [2, 3, 5]) if (pos.bidMax - bb >= x / 100 - 1e-9) note("recul_bid_" + x + "c");
  }

  actifDuJeton(id) { return V1.ACTIFS.find((a) => { const m = this.mk[a]; return m && (m.up === id || m.down === id); }) || null; }
  v1Etat(a) { return a === "BTC" ? this.e.V1 : this.e.V1x[a]; }
  v1Declencher(a, source, ts, t) {
    if (t - (this._v1t[a] || 0) <= 0.2) return;
    this._v1t[a] = t;
    try { this.v1Eval(source, ts, a); } catch (err) { this.erreur("V1 " + a, err); }
  }

  probaV1(a, mk) {
    const K = mk.strike, perp = this.f[a].perp, cl = this.f[a].cl;
    if (!K || !perp || !cl) return null;
    const t = now();
    let sgc = this._sgA[a];
    if (!sgc || t - sgc.t > 5) {
      const ser = this.serie(a, "perp", 300);
      if (ser.length < 60) return null;
      const r = []; for (let i = 1; i < ser.length; i++) r.push(Math.log(ser[i][1] / ser[i - 1][1]));
      const mo = r.reduce((x, y) => x + y, 0) / r.length;
      const base = med(this.serie(a, "perp", 120).map(([s2, p]) => { const c = this.prixA(a, "cl", s2); return c ? p - c : null; }).filter((x) => x != null));
      sgc = this._sgA[a] = { t, v: Math.sqrt(r.reduce((x, y) => x + (y - mo) ** 2, 0) / r.length) || 1e-6, base };
      if (a === "BTC") this._sg = sgc;
    }
    if (sgc.base == null) return null;
    const S = this.prixRapide(a);                             // prix le plus récent (Bybit ou OKX), ramené au niveau Chainlink
    if (S == null) return null;
    const sg = sgc.v, ts = Math.floor(t), deb = mk.end - 59;
    let E, v;
    if (ts >= deb) {
      const connus = []; for (let s2 = deb; s2 <= ts; s2++) { const x = this.prixA(a, "cl", s2); if (x) connus.push(x); }
      const nr = Math.max(1, mk.end - ts);
      E = (connus.reduce((x, y) => x + y, 0) + nr * S) / (connus.length + nr); v = (sg * S) ** 2 * nr ** 3 / 3 / 3600;
    } else { E = S; v = (sg * S) ** 2 * ((deb - ts) + 20); }
    return phi((E - K) / Math.sqrt(v + (CFG.SD_ECART_REL * S) ** 2));
  }

  prixRapide(a) {
    const b = this.f[a].perp, o = this.f[a].okx, ob = (this._okxB[a] = this._okxB[a] || {});
    if (o && (ob.v == null || now() - (ob.t || 0) > 5)) {
      ob.t = now();
      ob.v = med(this.serie(a, "okx", 120).map(([s2, p]) => { const c = this.prixA(a, "cl", s2); return c ? p - c : null; }).filter((x) => x != null));
    }
    const sgc = this._sgA[a], cands = [];
    if (b && sgc && sgc.base != null) cands.push([b.t, b.p - sgc.base, "bybit"]);
    if (o && ob.v != null) cands.push([o.t, o.p - ob.v, "okx"]);
    if (!cands.length) return null;
    cands.sort((x, y) => y[0] - x[0]);
    (this.sourceRapideA = this.sourceRapideA || {})[a] = cands[0][2]; this.sourceRapide = cands[0][2]; (this.compteSource = this.compteSource || {})[cands[0][2]] = (this.compteSource[cands[0][2]] || 0) + 1;
    return cands[0][1];
  }

  // élan : variation du prix rapide sur les 5 dernières secondes (positif = hausse)
  elanV1(a) {
    const ts = Math.floor(now());
    const p0 = this.prixA(a, "perp", ts), p5 = this.prixA(a, "perp", ts - V1.ELAN_S);
    const o0 = this.prixA(a, "okx", ts), o5 = this.prixA(a, "okx", ts - V1.ELAN_S);
    if (o0 && o5 && (this.sourceRapideA || {})[a] === "okx") return o0 - o5;
    return p0 && p5 ? p0 - p5 : null;
  }

  livreTrie(id, cote) { const L = this.pb[id]; if (!L) return []; return [...L[cote]].filter((x) => x[1] > 0).sort((x, y) => (cote === "asks" ? x[0] - y[0] : y[0] - x[0])); }

  v1Eval(source, tsSource, a = "BTC") {
    const V = this.v1Etat(a), mk = this.mk[a];
    if (!V || !mk || !mk.up || !mk.strike) return;
    const t = now();
    if (t < mk.start || t > mk.end - 1) return;
    const pu = this.probaV1(a, mk);
    if (pu == null) return;
    try { this.nEval(a, mk, pu); } catch (err) { this.erreur("fantômes", err); }
    const delai = tsSource ? t - tsSource : null;
    let pos = V.pos && V.pos.start === mk.start && !V.pos.fini ? V.pos : null;
    if (!pos) {
      if (V.dernierCycle === mk.start) return;            // une seule entrée par cycle
      for (const up of [true, false]) {
        const id = up ? mk.up : mk.down, asks = this.livreTrie(id, "asks"), fair = up ? pu : 1 - pu;
        if (!asks.length || asks[0][0] < V1.PMIN || asks[0][0] > V1.PMAX || fair < V1.PMIN + V1.MARGE) continue;
        const el = this.elanV1(a); if (el == null || el * (up ? 1 : -1) <= 0) { V.refusElan = (V.refusElan || 0) + 1; continue; }
        const mise = V1.MISE;                              // 50 $ par pari, fixe (décision de Pitch) — la réserve bloquait la mise à 0 depuis le 05.10 au soir
        let reste = mise, parts = 0, cout = 0;
        for (const [p, sz] of asks) { if (p > V1.PMAX) break; const k = Math.min(sz, reste / p); parts += k; cout += k * p; reste -= k * p; if (reste < 0.01) break; }
        if (reste >= 0.01 || parts <= 0) continue;
        const pm = cout / parts;
        if (this.enReel(a)) { V.dernierCycle = mk.start; this.v1EntreeReelle(a, mk, up, id, fair, delai, source); return; }
        V.dernierCycle = mk.start; V.entrees++;
        V.pos = { signaux: this.signauxEntree(a, up, id, up ? mk.down : mk.up), actif: a, start: mk.start, end: mk.end, slug: mk.slug, cote: up ? "Up" : "Down", token: id, autre: up ? mk.down : mk.up, prix: +pm.toFixed(4), parts: +parts.toFixed(2),
          mise: +cout.toFixed(2), frais: +(parts * CFG.FEE_RATE * pm * (1 - pm)).toFixed(3), proba: +fair.toFixed(3), heure: new Date().toISOString(),
          delai: delai != null ? +delai.toFixed(3) : null, source, B: { parts: 0, cout: 0 }, offre: null };
        try { this.gOuvrir(a, mk, V.pos); } catch (err) { this.erreur("assurance", err); }
        this.notelat(delai); this.sauver();
        return;
      }
      return;
    }
    const up = pos.cote === "Up", fairA = up ? pu : 1 - pu;
    pos.offre = Math.min(Math.floor(((1 - fairA) - V1.MARGE) * 100) / 100, V1.OPP_MAX);
    pos.probaActuelle = +fairA.toFixed(3);
    try { this.v1Alertes(pos); } catch (_) {}
    if (pos.reel) this.v1OffreReelle(pos);
    const bids = this.livreTrie(pos.token, "bids");
    if (!pos.bbEntree) { pos.bbEntree = true; this.bbSauver(pos, "entree"); }
    if (!pos.bbAlerte && fairA < pos.proba - 0.08) { pos.bbAlerte = true; this.bbSauver(pos, "alerte"); }
    if (fairA < pos.proba - V1.STOP_REL) { if (!pos.bbStop) { pos.bbStop = true; this.bbSauver(pos, "stop"); } this.v1Vendre(pos, bids, "stop", delai); return; }
    if (pos.B.parts < 1e-9 && bids.length && bids[0][0] >= V1.TP) this.v1Vendre(pos, bids, "sortie 90", delai);
  }

  // un vendeur de l'autre côté passe au moins 1 cent sous notre offre => offre servie (version prudente)
  v1Echange(id, side, p, size) {
    try { this.nEchange(id, side, p, size); } catch (_) {}
    const a = V1.ACTIFS.find((k) => { const P = this.v1Etat(k).pos; return P && (P.token === id || P.autre === id); });
    if (!a) return;
    const V = this.v1Etat(a), pos = V && V.pos;
    if (!pos || pos.fini || pos.offre == null || pos.offre < 0.02) return;
    if (pos.reel) { if (pos.offreId && Math.min(p, 1 - p) <= pos.offre + 0.01) this.v1SuivreOffre(pos); return; }
    let q = null;
    if (id === pos.autre && side === "SELL") q = p;            // vendeur de l'autre côté
    else if (id === pos.token && side === "BUY") q = 1 - p;     // acheteur de notre côté = vendeur de l'autre (appariement)
    if (q == null || q > pos.offre - 0.01 + 1e-9) return;
    const k = Math.min(size, pos.parts - pos.B.parts);
    if (k <= 0) return;
    pos.B.parts += k; pos.B.cout += k * pos.offre;
    if (pos.B.parts >= pos.parts - 1e-6) this.v1Clore(pos, pos.parts, 0, "paire");
    this.sauver();
  }

  v1Vendre(pos, bids, issue, delai) {
    if (pos.reel) { this.v1VenteReelle(pos, bids, issue, delai); return; }
    const q = pos.parts - pos.B.parts;
    let reste = q, recu = 0, frais = 0;
    for (const [p, sz] of bids) { const k = Math.min(sz, reste); recu += k * p; frais += k * CFG.FEE_RATE * p * (1 - p); reste -= k; if (reste <= 1e-9) break; }
    if (reste > 1e-6) return;                                   // pas assez d'acheteurs : on réessaie au prochain message
    pos.sortie = { prix: +(recu / q).toFixed(4), delai: delai != null ? +delai.toFixed(3) : null };
    this.notelat(delai);
    this.v1Clore(pos, pos.B.parts, recu - frais, issue);
    this.sauver();
  }

  // net = fusions (1 $ par paire) + produit des ventes - coûts
  v1Clore(pos, paires, produit, issue) {
    const V = this.v1Etat(pos.actif || "BTC");
    pos.fini = true; pos.issue = issue;
    pos.net = +(paires + produit - pos.mise - pos.B.cout - pos.frais).toFixed(2);
    V.capital += pos.net; V.pnl += pos.net;
    (V.issues[issue] = V.issues[issue] || { n: 0, pnl: 0 }).n++; V.issues[issue].pnl += pos.net;
    if (pos.net >= 0) { V.gains++; V.reserve += pos.net * CFG.PART_RESERVE; V.mise += pos.net * CFG.PART_REINVEST; } else V.pertes++;
    V.mise = Math.min(V.mise, Math.max(0, V.capital - V.reserve));
    V.trades.unshift(pos); V.trades.length = Math.min(V.trades.length, 300);
    V.pos = null;
  }

  enReel(a = "BTC") { return V1.REEL.includes(a) && this.reel.modeReel() && !this.e.reelStop && +this.env.MISE_REEL > 0; }

  async v1EntreeReelle(a, mk, up, id, fair, delai, source) {
    const V = this.v1Etat(a);
    if (this.v1Occupe) return; this.v1Occupe = true;
    try {
      const r = await this.reel.acheter(id, V1.PMAX, +this.env.MISE_REEL);
      if (!(r.parts > 0)) { V.reelRates = (V.reelRates || 0) + 1; return; }
      V.entrees++;
      V.pos = { signaux: this.signauxEntree(a, up, id, up ? mk.down : mk.up), reel: true, actif: a, start: mk.start, end: mk.end, slug: mk.slug, cote: up ? "Up" : "Down", token: id, autre: up ? mk.down : mk.up,
        prix: +(r.usd / r.parts).toFixed(4), parts: +r.parts.toFixed(2), mise: +r.usd.toFixed(2), frais: 0, proba: +fair.toFixed(3), heure: new Date().toISOString(),
        delai: delai != null ? +delai.toFixed(3) : null, msOrdre: r.ms, source, B: { parts: 0, cout: 0 }, offre: null, offreId: null, offrePrix: null };
      this.notelat(delai); await this.sauver();
    } catch (err) { this.erreur("réel achat", err); }
    finally { this.v1Occupe = false; }
  }

  // garde l'offre réelle sur l'autre côté alignée sur pos.offre (remplacement au plus une fois par seconde)
  async v1OffreReelle(pos) {
    const voulu = pos.offre != null && pos.offre >= 0.02 ? pos.offre : null, reste = pos.parts - pos.B.parts;
    if (pos.offrePrix === voulu || this.offreOccupee || now() - (pos.offreT || 0) < 1) return;
    this.offreOccupee = true; pos.offreT = now();
    try {
      if (pos.offreId) { await this.v1SuivreOffre(pos); await this.reel.annuler(pos.offreId); pos.offreId = null; pos.offrePrix = null; }
      if (voulu != null && reste >= 5 && !pos.fini) { const o = await this.reel.poserOffre(pos.autre, voulu, reste); if (o.id) { pos.offreId = o.id; pos.offrePrix = voulu; pos.offreDeja = 0; } }
    } catch (err) { this.erreur("réel offre", err); }
    finally { this.offreOccupee = false; }
  }

  // lit la quantité servie de l'offre réelle
  async v1SuivreOffre(pos) {
    if (!pos.offreId || this.suiviOccupe) return; this.suiviOccupe = true;
    try {
      const o = await this.reel.etatOrdre(pos.offreId);
      const servi = +(o && (o.size_matched || o.sizeMatched) || 0), neuf = servi - (pos.offreDeja || 0);
      if (neuf > 0) { pos.offreDeja = servi; pos.B.parts += neuf; pos.B.cout += neuf * pos.offrePrix; }
      if (pos.B.parts >= pos.parts - 0.01 && !pos.fini) { pos.offreId = null; this.v1Clore(pos, pos.parts, 0, "paire"); }
      await this.sauver();
    } catch (err) { this.erreur("réel suivi offre", err); }
    finally { this.suiviOccupe = false; }
  }

  async v1VenteReelle(pos, bids, issue, delai) {
    if (this.venteOccupee || pos.fini) return; this.venteOccupee = true;
    try {
      if (pos.offreId) { await this.v1SuivreOffre(pos); try { await this.reel.annuler(pos.offreId); } catch (_) {} pos.offreId = null; }
      const q = pos.parts - pos.B.parts;
      const plancher = Math.max(0.01, Math.floor(((bids[0] && bids[0][0]) || 0.02) * 100) / 100 - 0.03);
      const r = await this.reel.vendre(pos.token, plancher, q);
      if (!(r.parts > 0)) return;                        // rien de vendu : on réessaie au prochain message
      pos.vendu = (pos.vendu || 0) + r.parts; pos.venteUsd = (pos.venteUsd || 0) + r.usd;
      pos.sortie = { prix: +(pos.venteUsd / pos.vendu).toFixed(4), delai: delai != null ? +delai.toFixed(3) : null, ms: r.ms };
      this.notelat(delai);
      if (pos.vendu < pos.parts - pos.B.parts - 0.01) { pos.parts = +(pos.parts - r.parts).toFixed(2); pos.mise = +(pos.mise * (pos.parts / (pos.parts + r.parts))).toFixed(2); await this.sauver(); return; }   // vente partielle : le reste au prochain message
      this.v1Clore(pos, pos.B.parts, pos.venteUsd, issue);
      await this.sauver();
    } catch (err) { this.erreur("réel vente", err); }
    finally { this.venteOccupee = false; }
  }

  notelat(d) { if (d == null) return; this.latDec.push(d); if (this.latDec.length > 200) this.latDec.shift(); }

  // ================================================================== stratégies fantômes (aucun argent réel)
  // Une position = parts Up (U) et Down (D) détenues + trésorerie (cash). Règlement : cash + U si Up gagne, + D si Down gagne.
  nStrat(k) { return (this.N.strats[k] = this.N.strats[k] || { depuis: now(), pnl: 0, n: 0, gains: 0, pertes: 0, issues: {}, trades: [] }); }
  nSauver() { if (!this._nsv) { this._nsv = setTimeout(() => { this._nsv = null; this.state.storage.put("nouveaux", this.N).catch(() => {}); }, 1000); } }
  // achat fantôme en remontant le carnet (frais taker), au plus `maxParts` et jusqu'à `maxPrix`
  nAcheter(id, maxParts, maxPrix) {
    let parts = 0, cout = 0;
    for (const [p, sz] of this.livreTrie(id, "asks")) { if (p > maxPrix + 1e-9) break; const k = Math.min(sz, maxParts - parts); if (k <= 0) break; parts += k; cout += k * p + k * CFG.FEE_RATE * p * (1 - p); }
    return { parts, cout };
  }
  nVendre(id, parts) {
    let reste = parts, recu = 0;
    for (const [p, sz] of this.livreTrie(id, "bids")) { const k = Math.min(sz, reste); recu += k * p - k * CFG.FEE_RATE * p * (1 - p); reste -= k; if (reste <= 1e-9) break; }
    return { vendu: parts - reste, recu };
  }
  nPos(strat, a, mk, extra) {
    const P = { strat, actif: a, start: mk.start, end: mk.end, slug: mk.slug, up: mk.up, down: mk.down, U: 0, D: 0, cash: 0, heure: new Date().toISOString(), journal: [], ...extra };
    this.N.ouvertes.push(P); return P;
  }
  nNote(P, x) { P.journal.push((now() - P.start).toFixed(1) + "s " + x); if (P.journal.length > 30) P.journal.shift(); }
  nClore(P, issue) {
    P.fini = true; P.issue = issue; P.net = +P.cash.toFixed(2);
    const S2 = this.nStrat(P.strat + " " + P.actif);
    S2.n++; S2.pnl += P.net; if (P.net >= 0) S2.gains++; else S2.pertes++;
    (S2.issues[issue] = S2.issues[issue] || { n: 0, pnl: 0 }).n++; S2.issues[issue].pnl += P.net;
    S2.trades.unshift(P); S2.trades.length = Math.min(S2.trades.length, 120);
    this.N.ouvertes = this.N.ouvertes.filter((x) => x !== P);
    this.nSauver();
  }

  // ---- 1. V1 avec assurance graduée à la place du stop : même entrée que V1
  gOuvrir(a, mk, vpos) {
    const up = vpos.cote === "Up";
    for (const [nom, niveaux] of Object.entries(NV.ASSUR.VARIANTES)) {
      const P = this.nPos(nom, a, mk, { famille: "assurance", niveaux, cote: vpos.cote, prix: vpos.prix, parts: vpos.parts, proba0: vpos.proba, H: 0, B: 0, calmeDepuis: null, offre: null });
      if (up) P.U = vpos.parts; else P.D = vpos.parts;
      P.cash = -(vpos.mise + vpos.frais);
      this.nNote(P, `entrée ${vpos.cote} ${vpos.parts.toFixed(1)} parts à ${vpos.prix} (proba ${vpos.proba})`);
    }
    this.nSauver();
  }
  gGerer(P, pu) {
    const up = P.cote === "Up", fair = up ? pu : 1 - pu, d = P.proba0 - fair, nous = up ? P.up : P.down, autre = up ? P.down : P.up;
    const main = up ? P.U : P.D, opp = up ? P.D : P.U;
    P.offre = Math.min(Math.floor(((1 - fair) - V1.MARGE) * 100) / 100, V1.OPP_MAX);
    P.probaActuelle = +fair.toFixed(3);
    if (opp >= main - 1e-6) return;                                   // paire complète : rien à faire jusqu'à la fin
    // sortie à 0,90 si aucune offre maker servie (comme V1) : on revend aussi l'assurance
    const bb = this.livreTrie(nous, "bids")[0];
    if (P.B < 1e-9 && bb && bb[0] >= V1.TP) {
      const v = this.nVendre(nous, main); if (v.vendu < main - 1e-6) return;
      P.cash += v.recu; if (up) P.U = 0; else P.D = 0;
      if (opp > 0) { const w = this.nVendre(autre, opp); P.cash += w.recu; if (up) P.D -= w.vendu; else P.U -= w.vendu; }
      this.nNote(P, "sortie 0,90"); this.nClore(P, "sortie 90"); return;
    }
    // assurance graduée
    let cible = 0; for (const [seuil, fr] of (P.niveaux || NV.ASSUR.VARIANTES["assurance 6/9/12"])) if (d >= seuil) cible = fr;
    const manque = cible * main - opp;
    if (manque > 0.5) {
      const r = this.nAcheter(autre, manque, NV.ASSUR.OPP_MAX);
      if (r.parts > 0) { P.cash -= r.cout; P.H += r.parts; if (up) P.D += r.parts; else P.U += r.parts; this.nNote(P, `assurance +${r.parts.toFixed(1)} à ${(r.cout / r.parts).toFixed(3)} (baisse ${(100 * d).toFixed(0)} pts)`); this.nSauver(); }
    }
    // retrait de l'assurance quand l'alerte retombe
    if (P.H > 0 && d < NV.ASSUR.RETRAIT) {
      if (P.calmeDepuis == null) P.calmeDepuis = now();
      else if (now() - P.calmeDepuis >= NV.ASSUR.CALME_S) {
        const w = this.nVendre(autre, P.H);
        if (w.vendu > 0) { P.cash += w.recu; P.H -= w.vendu; if (up) P.D -= w.vendu; else P.U -= w.vendu; this.nNote(P, `assurance retirée ${w.vendu.toFixed(1)} parts`); this.nSauver(); }
        P.calmeDepuis = null;
      }
    } else P.calmeDepuis = null;
  }

  // ---- évaluation à chaque message (après la proba de V1)
  // relevé des « occasions manquées » : une fois par seconde, ce que le carnet offrait quand le modèle voulait entrer
  nManq(a, mk, pu, t, tleft) {
    const sec = Math.floor(t); if ((this._mqT = this._mqT || {})[a] === sec) return; this._mqT[a] = sec;
    const M2 = ((this.N.manq = this.N.manq || { depuis: now() })[a] = this.N.manq[a] || { v1: {}, fin: {} });
    const inc = (o, k) => { o[k] = (o[k] || 0) + 1; };
    const bucket = (ask, bornes) => { if (ask == null) return "carnet vide"; for (const [lim, nom] of bornes) if (ask < lim) return nom; return bornes[bornes.length - 1][1]; };
    for (const up of [true, false]) {
      const id = up ? mk.up : mk.down, ask = (this.livreTrie(id, "asks")[0] || [null])[0], fair = up ? pu : 1 - pu;
      if (fair >= V1.PMIN + V1.MARGE) {                                    // V1 : le modèle donne >= 0,63
        inc(M2.v1, "secondes modèle OK");
        inc(M2.v1, "meilleure vente " + bucket(ask, [[0.55, "< 0,55"], [0.565, "0,55-0,56 (entrée possible)"], [0.60, "0,57-0,59"], [0.70, "0,60-0,69"], [2, ">= 0,70"]]));
      }
      const F = NV.FIN[a];
      if (F && tleft <= F.W && tleft >= 1 && fair >= F.SEUIL) {           // fin de cycle : le modèle est très sûr
        inc(M2.fin, "secondes modèle OK");
        inc(M2.fin, "meilleure vente " + bucket(ask, [[F.LO, "< " + F.LO], [F.HI + 0.005, F.LO + "-" + F.HI + " (achat possible)"], [0.95, "jusqu'à 0,95"], [0.99, "0,95-0,98"], [2, ">= 0,99"]]));
      }
    }
  }
  // échanges vus dans la zone d'achat quand le modèle était OK (= quelqu'un a été servi avant nous)
  nManqEchange(id, side, p) {
    for (const a of V1.ACTIFS) {
      const mk = this.mk[a]; if (!mk || (id !== mk.up && id !== mk.down)) continue;
      const pu = this._puA && this._puA[a]; if (pu == null) continue;
      const up = id === mk.up, fair = up ? pu : 1 - pu, M2 = this.N.manq && this.N.manq[a]; if (!M2 || side !== "BUY") continue;
      const tleft = mk.end - now(), F = NV.FIN[a];
      if (fair >= V1.PMIN + V1.MARGE && p >= V1.PMIN && p <= V1.PMAX) M2.v1["échanges à 0,55-0,56 (pris par d'autres)"] = (M2.v1["échanges à 0,55-0,56 (pris par d'autres)"] || 0) + 1;
      if (F && tleft <= F.W && fair >= F.SEUIL && p >= F.LO && p <= F.HI) M2.fin["échanges dans la zone (pris par d'autres)"] = (M2.fin["échanges dans la zone (pris par d'autres)"] || 0) + 1;
    }
  }

  nEval(a, mk, pu) {
    const t = now(), tleft = mk.end - t;
    (this._puA = this._puA || {})[a] = pu;
    try { this.nManq(a, mk, pu, t, tleft); } catch (_) {}
    for (const P of this.N.ouvertes) if (P.strat.startsWith("assurance") && P.actif === a && P.start === mk.start && !P.fini) this.gGerer(P, pu);
    // ---- 2. fin de cycle : acheter 0,70-0,90 quand le modèle est très sûr, garder jusqu'à la fin
    const F = NV.FIN[a];
    if (F && tleft <= F.W && tleft >= 1 && !this.N.ouvertes.some((P) => P.strat === "fin" && P.actif === a && P.start === mk.start)
        && (this._finFait || {})[a] !== mk.start) {
      for (const up of [true, false]) {
        const id = up ? mk.up : mk.down, ask = this.livreTrie(id, "asks")[0], fair = up ? pu : 1 - pu;
        if (!ask || ask[0] < F.LO || ask[0] > F.HI || fair < F.SEUIL) continue;
        const r = this.nAcheter(id, NV.FIN.MISE / ask[0], F.HI);
        if (r.parts < 1) continue;
        (this._finFait = this._finFait || {})[a] = mk.start;
        const P = this.nPos("fin", a, mk, { cote: up ? "Up" : "Down", prix: +(r.cout / r.parts).toFixed(4), parts: +r.parts.toFixed(2), proba0: +fair.toFixed(3), restant_s: +tleft.toFixed(0) });
        P.cash = -r.cout; if (up) P.U = r.parts; else P.D = r.parts;
        this.nNote(P, `achat ${P.cote} ${r.parts.toFixed(1)} parts à ${P.prix} (modèle ${P.proba0}, ${P.restant_s} s restantes)`);
        this.nSauver();
        break;
      }
    }
    // ---- 3. teneur de marché : offres d'achat Up et Down à valeur - marge (mises à jour à chaque message)
    if (NV.MM.ACTIFS.includes(a)) {
      const ts = Math.floor(t), p1 = this.prixA(a, "perp", ts), p0 = this.prixA(a, "perp", ts - 1);
      const bouge = p1 && p0 ? Math.abs(p1 / p0 - 1) * 1e4 : 0;
      for (const [nom, V2] of Object.entries(NV.MM.VARIANTES)) {
        const P = this.N.ouvertes.find((x) => x.strat === nom && x.actif === a && x.start === mk.start);
        let bidU = Math.floor((pu - V2.MARGE) * 100) / 100, bidD = Math.floor((1 - pu - V2.MARGE) * 100) / 100;
        if (V2.PENCHER && P && Math.abs(P.U - P.D) > 1e-6) {              // pencher : retirer l'offre du côté en trop, remonter l'autre
          if (P.U > P.D) { bidU = -1; bidD = +(bidD + V2.PENCHER).toFixed(2); } else { bidD = -1; bidU = +(bidU + V2.PENCHER).toFixed(2); }
        }
        const retire = V2.RETRAIT_PB != null && bouge > V2.RETRAIT_PB;
        ((this._mmQ = this._mmQ || {})[nom] = this._mmQ[nom] || {})[a] = { start: mk.start, up: mk.up, down: mk.down, actif: tleft > NV.MM.ARRET_S && !retire, bidU, bidD };
      }
    }
  }

  // ---- échanges Polymarket : remplissage prudent des offres maker (un vendeur doit passer 1 cent sous notre offre)
  nEchange(id, side, p, size) {
    try { this.nManqEchange(id, side, p); } catch (_) {}
    // vendeur du jeton X au prix px (une vente de X, ou un achat de l'autre jeton apparié)
    const vendeur = (X, autre) => (id === X && side === "SELL" ? p : id === autre && side === "BUY" ? 1 - p : null);
    for (const P of this.N.ouvertes) {
      if (!P.strat.startsWith("assurance") || P.fini || P.offre == null || P.offre < 0.02) continue;
      const up = P.cote === "Up", X = up ? P.down : P.up, Y = up ? P.up : P.down, px = vendeur(X, Y);
      if (px == null || px > P.offre - 0.01 + 1e-9) continue;
      const main = up ? P.U : P.D, opp = up ? P.D : P.U, k = Math.min(size, main - opp);
      if (k <= 0) continue;
      P.cash -= k * P.offre; P.B += k; if (up) P.D += k; else P.U += k;
      this.nNote(P, `offre opposée servie ${k.toFixed(1)} à ${P.offre}`); this.nSauver();
    }
    for (const [nom, V2] of Object.entries(NV.MM.VARIANTES)) for (const a of NV.MM.ACTIFS) {
      const q = ((this._mmQ || {})[nom] || {})[a]; if (!q || !q.actif || (id !== q.up && id !== q.down)) continue;
      const mk = this.mk[a]; if (!mk || mk.start !== q.start) continue;
      let P = this.N.ouvertes.find((x) => x.strat === nom && x.actif === a && x.start === q.start);
      for (const [X, Y, bid, cle] of [[q.up, q.down, q.bidU, "U"], [q.down, q.up, q.bidD, "D"]]) {
        const px = vendeur(X, Y);
        if (px == null || bid < 0.02 || px > bid - 0.01 + 1e-9) continue;
        const inv = P ? P[cle] : 0, autreInv = P ? P[cle === "U" ? "D" : "U"] : 0;
        const k = Math.min(size, V2.PAQUET, NV.MM.MAXI - inv, V2.DESEQ - (inv - autreInv));
        if (k <= 0) continue;
        if (!P) P = this.nPos(nom, a, mk, { famille: "mm" });
        P[cle] += k; P.cash -= k * bid;
        this.nNote(P, `achat ${cle === "U" ? "Up" : "Down"} ${k.toFixed(1)} à ${bid}`); this.nSauver();
      }
    }
  }

  // ---- règlement : résultat officiel Polymarket (20 s après la fin)
  async nRegler() {
    const t = now();
    for (const P of this.N.ouvertes.filter((x) => t >= x.end)) { this.N.ouvertes = this.N.ouvertes.filter((x) => x !== P); this.N.attente.push(P); }
    const garder = [], cache = {};
    for (const P of this.N.attente) {
      if (t < P.end + 20 || !P.slug) { garder.push(P); continue; }
      try {
        if (!(P.slug in cache)) {
          const ev = await (await fetch(`${G}/events?slug=${P.slug}`)).json();
          const m = ev[0].markets[0], px = JSON.parse(m.outcomePrices || "[]").map(Number), outs = JSON.parse(m.outcomes || "[]");
          cache[P.slug] = (px.includes(1) && px.includes(0)) ? String(outs[px.indexOf(1)]) : null;
        }
        const g = cache[P.slug];
        if (!g) { garder.push(P); continue; }
        P.cash += g === "Up" ? P.U : P.D; P.gagnant = g;
        const issue = P.strat.startsWith("assurance") ? ((P.U > 0 && P.D > 0 && Math.min(P.U, P.D) >= Math.max(P.U, P.D) - 1e-6) ? "paire" : (P.H > 0 ? "fin couverte" : (g === P.cote ? "fin gagnée" : "fin perdue")))
          : P.strat === "fin" ? (g === P.cote ? "gagné" : "perdu") : (P.U > 0 && P.D > 0 ? "paires + reste" : "une seule jambe");
        this.nClore(P, issue);
      } catch (err) { garder.push(P); this.erreur("fantômes règlement", err); }
    }
    this.N.attente = garder;
    this.nSauver();
  }

  nVue() {
    // V1 actuel (avec stop) sur la même période, pour comparer
    const v1 = {};
    for (const [a, V] of [["BTC", this.e.V1], ["ETH", this.e.V1x.ETH]]) {
      const T2 = (V.trades || []).filter((x) => x.heure && Date.parse(x.heure) / 1000 >= this.N.depuis && x.net != null);
      v1["V1 actuel (avec stop) " + a] = { depuis: this.N.depuis, n: T2.length, pnl: T2.reduce((s2, x) => s2 + x.net, 0), gains: T2.filter((x) => x.net >= 0).length, pertes: T2.filter((x) => x.net < 0).length,
        pertesTot: T2.filter((x) => x.net < 0).reduce((s2, x) => s2 + x.net, 0), pire: T2.length ? Math.min(...T2.map((x) => x.net)) : 0 };
    }
    const resume = Object.fromEntries(Object.entries(this.N.strats).map(([k, v]) => [k, { depuis: v.depuis, n: v.n, pnl: v.pnl, gains: v.gains, pertes: v.pertes,
      pertesTot: v.trades.filter((x) => x.net < 0).reduce((s2, x) => s2 + x.net, 0), pire: v.trades.length ? Math.min(...v.trades.map((x) => x.net)) : 0 }]));
    return { depuis: this.N.depuis, manquees: this.N.manq || {}, resume: { ...v1, ...resume }, reglages: NV, strats: Object.fromEntries(Object.entries(this.N.strats).map(([k, v]) => [k, { ...v, trades: v.trades.slice(0, 60) }])),
      ouvertes: this.N.ouvertes, attente: this.N.attente.length, offresMM: this._mmQ || {} };
  }

  async v1Regler(a = "BTC") {
    const V = this.v1Etat(a), t = now();
    if (V.pos && t >= V.pos.end && !V.pos.fini) {
      if (V.pos.reel && V.pos.offreId) { try { await this.v1SuivreOffre(V.pos); await this.reel.annuler(V.pos.offreId); } catch (_) {} V.pos.offreId = null; }
      if (V.pos && !V.pos.fini) { V.attente.push(V.pos); V.pos = null; }
    }
    const garder = [];
    for (const pos of V.attente) {
      if (t < pos.end + 20) { garder.push(pos); continue; }
      try {
        const ev = await (await fetch(`${G}/events?slug=${pos.slug}`)).json();
        const m = ev[0].markets[0], px = JSON.parse(m.outcomePrices || "[]").map(Number), outs = JSON.parse(m.outcomes || "[]");
        if (!(px.includes(1) && px.includes(0))) { garder.push(pos); continue; }
        const gagne = String(outs[px.indexOf(1)]) === pos.cote;
        this.v1Clore(pos, pos.B.parts, gagne ? pos.parts - pos.B.parts : 0, gagne ? "fin gagnée" : "fin perdue");
      } catch (err) { garder.push(pos); this.erreur("V1 règlement", err); }
    }
    V.attente = garder;
  }

  vue() {
    const t = now(), start = Math.floor(t / 300) * 300;
    const age = (a, k) => (this.f[a][k] ? +(t - this.f[a][k].t).toFixed(1) : null);
    return {
      mode: "fantôme", reste: Math.round(start + 300 - t),
      e: { ...this.e, trades: this.e.trades.slice(0, 60), refus: undefined, verif: undefined },
      actifs: LISTE.map((a) => {
        const mk = this.mk[a] || {};
        return { a, regles: ACTIFS[a].regles, strike: mk.strike || null, cl: this.f[a].cl && this.f[a].cl.p, ageCl: age(a, "cl"), perp: this.f[a].perp && this.f[a].perp.p, agePerp: age(a, "perp"),
          spot: ACTIFS[a].spot ? (this.f[a].cb && this.f[a].cb.p) : "—", ageSpot: ACTIFS[a].spot ? age(a, "cb") : null, deseq: +this.deseq[a].toFixed(2), raison: mk.raison || null };
      }),
      v1: (() => {
        const V = this.e.V1, q = (L, x) => { if (!L.length) return null; const b = [...L].sort((a2, b2) => a2 - b2); return +b[Math.min(b.length - 1, Math.floor(b.length * x))].toFixed(3); };
        return { ...V, trades: V.trades.slice(0, 40), latPolyMed: q(this.latPoly, 0.5), latPolyP90: q(this.latPoly, 0.9), latDecMed: q(this.latDec, 0.5), latDecP90: q(this.latDec, 0.9),
          reel: { configure: this.reel.configure(), actif: this.enReel(), arret: !!this.e.reelStop, mise: +this.env.MISE_REEL || null },
          polyOk: !!this.ws.poly, sources: this.compteSource || {}, eth: { ...this.e.V1x.ETH, trades: this.e.V1x.ETH.trades.slice(0, 40) }, okxOk: !!this.ws.okx, livre: this.mk.BTC && this.mk.BTC.up ? { up: (this.livreTrie(this.mk.BTC.up, "asks")[0] || [null])[0], down: (this.livreTrie(this.mk.BTC.down, "asks")[0] || [null])[0] } : null };
      })(),
      diag: this.diag,
    };
  }
}

const STYLE = `<style>
:root{--bg:#f6f7f9;--card:#fff;--tx:#14171c;--mu:#667085;--bd:#e4e7ec;--ok:#12805c;--ko:#c0362c;--ac:#2f5bea;--wa:#b54708}
@media (prefers-color-scheme:dark){:root{--bg:#0f1115;--card:#171a21;--tx:#e8eaee;--mu:#98a2b3;--bd:#262b35;--ok:#3ccf91;--ko:#f0705f;--ac:#7c9cff;--wa:#f5a524}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--tx);font:15px/1.45 -apple-system,system-ui,sans-serif;padding:16px;max-width:820px;margin:auto}
h1{font-size:20px;margin:0 0 4px}a{color:var(--ac)}.mu{color:var(--mu);font-size:13px}.card{background:var(--card);border:1px solid var(--bd);border-radius:12px;padding:14px;margin:12px 0;overflow-x:auto}
.g{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}.k{font-size:12px;color:var(--mu)}.v{font-size:20px;font-weight:600;font-variant-numeric:tabular-nums}
.ok{color:var(--ok)}.ko{color:var(--ko)}.wa{color:var(--wa)}table{width:100%;border-collapse:collapse;font-size:13px;font-variant-numeric:tabular-nums}td,th{padding:6px 4px;border-bottom:1px solid var(--bd);text-align:left;white-space:nowrap}
button{background:var(--ac);color:#fff;border:0;border-radius:8px;padding:10px 14px;font-size:15px;width:100%;margin-top:8px}.badge{display:inline-block;padding:2px 8px;border-radius:99px;font-size:12px;background:var(--bd)}
@media(max-width:420px){.g{grid-template-columns:repeat(2,1fr)}}</style>`;

const PAGE = `<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Bot 95</title>${STYLE}</head><body>
<h1>Bot 95 <span class="badge">mode fantôme</span></h1><div class="mu">7 cryptos 5 min Polymarket — achat immédiat (A) + V1 paires BTC — aucun argent réel</div>
<div style="margin-top:8px"><a href="/rapport">→ Rapport détaillé des refus</a> · <a href="/nouveaux">→ Nouvelles stratégies fantômes (assurance, fin de cycle, teneur de marché)</a></div>
<div id="app" class="mu" style="margin-top:12px">Chargement…</div>
<script>
const $=s=>document.querySelector(s);const f=(x,d=2)=>x==null?'—':Number(x).toFixed(d);const usd=x=>(x>=0?'+':'')+f(x)+' $';
async function rep(){await fetch('/api/reprendre',{method:'POST'});go()}
async function go(){try{const d=await (await fetch('/api/etat')).json();const e=d.e;
const pa=d.actifs.map(x=>{const s=e.parActif[x.a]||{trades:0,gains:0,pertes:0,pnl:0};const v=e.vetos[x.a]||{};const top=Object.entries(v).sort((p,q)=>q[1]-p[1])[0];
return '<tr><td><b>'+x.a+'</b></td><td>'+(e.candidats[x.a]||0)+'</td><td>'+s.trades+'</td><td class=ok>'+s.gains+'</td><td class=ko>'+s.pertes+'</td><td class="'+(s.pnl>=0?'ok':'ko')+'">'+usd(s.pnl)+'</td><td class=mu>'+(top?top[0]+' ('+top[1]+')':'—')+'</td></tr>'}).join('');
const fl=d.actifs.map(x=>'<tr><td>'+x.a+'</td><td>'+(x.cl?Number(x.cl).toPrecision(7):'—')+' <span class=mu>'+f(x.ageCl,1)+' s</span></td><td>'+(x.perp?Number(x.perp).toPrecision(7):'—')+' <span class=mu>'+f(x.agePerp,1)+' s</span></td><td>'+(x.spot==='—'?'—':(x.spot?Number(x.spot).toPrecision(7):'—')+' <span class=mu>'+f(x.ageSpot,1)+' s</span>')+'</td><td>'+(x.strike?Number(x.strike).toPrecision(7):'—')+'</td></tr>').join('');
const tr=e.trades.map(t=>'<tr><td>'+t.heure.slice(5,16).replace('T',' ')+'</td><td>'+t.actif+'</td><td>'+t.fav+'</td><td>'+f(t.prix,3)+'</td><td>'+f(t.z)+'</td><td>'+t.resultat+'</td><td class="'+(t.net>=0?'ok':'ko')+'">'+usd(t.net)+'</td></tr>').join('')||'<tr><td colspan=7 class=mu>Aucun trade encore</td></tr>';
const pos=e.positions.concat(e.attente).map(p=>p.actif+' '+p.fav+' à '+f(p.prix,3)+' ('+f(p.mise)+' $)').join(' · ');
$('#app').className='';$('#app').innerHTML=
(e.pause?'<div class=card style="border-color:var(--ko)"><b class=ko>En pause après une perte.</b><br>Plus aucun trade jusqu\\'à ce que tu valides.<button onclick="rep()">Reprendre</button></div>':'')+
'<div class=card><div class=g><div><div class=k>Capital</div><div class=v>'+f(e.capital)+' $</div></div><div><div class=k>Réserve (2/3)</div><div class=v>'+f(e.reserve)+' $</div></div><div><div class=k>Mise</div><div class=v>'+f(e.mise)+' $</div></div>'+
'<div><div class=k>Gain total</div><div class="v '+(e.pnl>=0?'ok':'ko')+'">'+usd(e.pnl)+'</div></div><div><div class=k>Gagnés</div><div class="v ok">'+e.gains+'</div></div><div><div class=k>Perdus</div><div class="v ko">'+e.pertes+'</div></div></div>'+
(pos?'<div style="margin-top:8px">En cours : '+pos+'</div>':'')+'<div class=mu style="margin-top:6px">Fin du marché en cours dans '+d.reste+' s</div></div>'+
(()=>{const V=d.v1;const it=Object.entries(V.issues||{}).map(([k,x])=>k+' '+x.n+' ('+usd(x.pnl)+')').join(' · ')||'—';
const tv=V.trades.map(t=>'<tr><td>'+t.heure.slice(5,16).replace('T',' ')+'</td><td>'+t.cote+'</td><td>'+f(t.prix,3)+'</td><td>'+f(t.proba,2)+'</td><td>'+(t.B&&t.B.parts?f(t.B.parts,0)+' à '+f(t.B.cout/t.B.parts,2):'—')+'</td><td>'+t.issue+'</td><td class="'+(t.net>=0?'ok':'ko')+'">'+usd(t.net)+'</td></tr>').join('')||'<tr><td colspan=7 class=mu>Aucun trade encore</td></tr>';
const p=V.pos?'<div style="margin-top:8px">En cours : '+V.pos.cote+' à '+f(V.pos.prix,3)+' · proba '+f(V.pos.probaActuelle,2)+' · offre opposée '+f(V.pos.offre,2)+' · servie '+f(V.pos.B.parts,0)+'/'+f(V.pos.parts,0)+'</div>':'';
const R=V.reel||{};const bandeau=R.actif?'<div class=card style="border-color:var(--ko)"><b class=ko>ARGENT RÉEL ACTIF</b> — mise '+R.mise+' $ par entrée<button onclick="fetch(\'/api/reel/arret\',{method:\'POST\'}).then(go)">ARRÊT D\'URGENCE</button></div>':(R.arret?'<div class=card><b>Réel à l\'arrêt</b><button onclick="fetch(\'/api/reel/reprise\',{method:\'POST\'}).then(go)">Reprendre le réel</button></div>':'');
return bandeau+'<div class=card><b>V1 — paires BTC (jambe 55 filtrée)</b> <span class=mu>'+(R.actif?'RÉEL':'fantôme')+' · </span> <span class=mu>temps réel'+(V.polyOk?'':' — <span class=ko>carnet en direct déconnecté</span>')+'</span><div class=g style="margin-top:8px"><div><div class=k>Capital</div><div class=v>'+f(V.capital)+' $</div></div><div><div class=k>Gain</div><div class="v '+(V.pnl>=0?'ok':'ko')+'">'+usd(V.pnl)+'</div></div><div><div class=k>Gagnés / perdus</div><div class=v><span class=ok>'+V.gains+'</span> / <span class=ko>'+V.pertes+'</span></div></div></div>'+
'<div class=mu style="margin-top:6px">Réglage A : élan 5 s + stop à −15 points · entrées refusées par l\'élan : '+(V.refusElan||0)+' · source la plus rapide : '+Object.entries(V.sources||{}).map(([k,n])=>k+' '+n).join(', ')+'</div><div class=mu>Issues : '+it+'</div><div class=mu>Réaction : message Polymarket reçu en '+f(V.latPolyMed,3)+' s (90 % sous '+f(V.latPolyP90,3)+' s) · décisions en '+f(V.latDecMed,3)+' s (90 % sous '+f(V.latDecP90,3)+' s)</div>'+p+
'<table style="margin-top:8px"><tr><th>Heure UTC</th><th>Jambe</th><th>Prix</th><th>Proba</th><th>Autre jambe</th><th>Issue</th><th>Net</th></tr>'+tv+'</table></div>'})()+
(()=>{const V=d.v1.eth;if(!V)return '';const it=Object.entries(V.issues||{}).map(([k,x])=>k+' '+x.n+' ('+usd(x.pnl)+')').join(' · ')||'—';
const tv=V.trades.map(t=>'<tr><td>'+t.heure.slice(5,16).replace('T',' ')+'</td><td>'+t.cote+'</td><td>'+f(t.prix,3)+'</td><td>'+f(t.proba,2)+'</td><td>'+(t.B&&t.B.parts?f(t.B.parts,0)+' à '+f(t.B.cout/t.B.parts,2):'—')+'</td><td>'+t.issue+'</td><td class="'+(t.net>=0?'ok':'ko')+'">'+usd(t.net)+'</td></tr>').join('')||'<tr><td colspan=7 class=mu>Aucun trade encore</td></tr>';
const p=V.pos?'<div style="margin-top:8px">En cours : '+V.pos.cote+' à '+f(V.pos.prix,3)+' · proba '+f(V.pos.probaActuelle,2)+' · offre opposée '+f(V.pos.offre,2)+'</div>':'';
return '<div class=card><b>V1 — paires ETH (jambe 55 filtrée)</b> <span class=mu>fantôme</span><div class=g style="margin-top:8px"><div><div class=k>Capital</div><div class=v>'+f(V.capital)+' $</div></div><div><div class=k>Gain</div><div class="v '+(V.pnl>=0?'ok':'ko')+'">'+usd(V.pnl)+'</div></div><div><div class=k>Gagnés / perdus</div><div class=v><span class=ok>'+V.gains+'</span> / <span class=ko>'+V.pertes+'</span></div></div></div><div class=mu style="margin-top:6px">Entrées refusées par l\'élan : '+(V.refusElan||0)+' · Issues : '+it+'</div>'+p+
'<table style="margin-top:8px"><tr><th>Heure UTC</th><th>Jambe</th><th>Prix</th><th>Proba</th><th>Autre jambe</th><th>Issue</th><th>Net</th></tr>'+tv+'</table></div>'})()+
'<div class=card><b>Par crypto</b><table><tr><th>Crypto</th><th>Candidats</th><th>Trades</th><th>Gagnés</th><th>Perdus</th><th>Gain</th><th>Refus le plus fréquent</th></tr>'+pa+'</table></div>'+
'<div class=card><b>Trades</b><table><tr><th>Heure UTC</th><th>Crypto</th><th>Côté</th><th>Prix</th><th>z</th><th>Résultat</th><th>Net</th></tr>'+tr+'</table></div>'+
'<div class=card><b>Flux</b> <span class=mu>(prix et âge de la dernière mise à jour)</span><table><tr><th>Crypto</th><th>Chainlink</th><th>Perp Bybit</th><th>Spot Coinbase</th><th>Prix d\\'exercice</th></tr>'+fl+'</table></div>'+
(d.diag.erreurs.length?'<div class=card><b>Journal technique</b><div class=mu>'+d.diag.erreurs.join('<br>')+'</div></div>':'');
}catch(err){$('#app').textContent='Erreur de chargement : '+err}}
go();setInterval(go,3000);
</script></body></html>`;

const PAGE_N = `<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Fantômes</title>${STYLE}</head><body>
<h1>Nouvelles stratégies — mode fantôme</h1>
<div class="mu">Aucun argent réel. Toutes les versions tournent en même temps sur les mêmes marchés pour être comparées. Assurance = V1 sans stop : on achète l'autre côté par paliers quand la proba baisse (6/9/12 ou 4/7/10 pts → 25/50/100 %). Fin de cycle = achat 0,70–0,90 quand le modèle est très sûr. Teneur de marché prudente = offres Up et Down au prix du modèle moins 12 cents, côté acheté retiré et l'autre remonté de 4 cents, 10 parts max, retrait si le prix bouge vite (les versions « actuel » et « pencher » ont été arrêtées le 06.10, perdantes en direct). Les tableaux « Occasions » montrent ce que le carnet offrait vraiment quand le modèle voulait entrer.</div>
<div style="margin-top:8px"><a href="/">← Tableau de bord</a></div><div id="app" style="margin-top:12px">Chargement…</div>
<script>
const f=(x)=>(x>=0?"+":"")+x.toFixed(2)+" $";
async function maj(){try{const d=await (await fetch("/api/nouveaux",{cache:"no-store"})).json();let h="<div class='mu'>Depuis "+new Date(d.depuis*1000).toLocaleString("fr-CH")+" · "+d.ouvertes.length+" position(s) ouverte(s), "+d.attente+" en attente du résultat</div>";
const noms={"assurance 6/9/12":"V1 + assurance 6/9/12 (sans stop)","assurance 4/7/10":"V1 + assurance 4/7/10 (sans stop)","fin":"Fin de cycle 0,70–0,90","mm actuel":"Teneur de marché — actuel","mm pencher":"Teneur de marché — pencher 4 cents","mm prudent":"Teneur de marché — prudent (retrait + pencher + petit)"};
const cles=Object.keys(d.strats).sort();
const R=d.resume||{},rk=Object.keys(R).sort();
h+="<div class='card'><h2>Comparaison</h2><table><tr><th>Stratégie</th><th>Depuis</th><th>Trades</th><th>Gagnés / perdus</th><th>Résultat</th><th>Pertes totales</th><th>Pire trade</th></tr>"+rk.map(k=>{const x=R[k],st=k.slice(0,k.lastIndexOf(" ")),a=k.slice(k.lastIndexOf(" ")+1);return "<tr><td>"+(noms[st]||st)+" — "+a+"</td><td>"+new Date(x.depuis*1000).toLocaleString("fr-CH",{day:"2-digit",month:"2-digit",hour:"2-digit",minute:"2-digit"})+"</td><td>"+x.n+"</td><td>"+x.gains+" / "+x.pertes+"</td><td><b>"+f(x.pnl)+"</b></td><td>"+f(x.pertesTot)+"</td><td>"+f(x.pire)+"</td></tr>"}).join("")+"</table></div>";
const MQ=d.manquees||{};for(const a of ["BTC","ETH"]){const m=MQ[a];if(!m)continue;for(const [st,titre] of [["v1","V1 — quand le modèle donne ≥ 0,63"],["fin","Fin de cycle — quand le modèle est très sûr"]]){const o=m[st]||{},tot=o["secondes modèle OK"]||0;if(!tot)continue;h+="<div class='card'><h2>Occasions — "+titre+" — "+a+"</h2><table><tr><th>Ce qu'il y avait</th><th>Secondes / échanges</th><th>Part</th></tr>"+Object.entries(o).map(([k,v])=>"<tr><td>"+k+"</td><td>"+v+"</td><td>"+(k.startsWith("meilleure")?(100*v/tot).toFixed(1)+" %":"")+"</td></tr>").join("")+"</table></div>";}}
if(!cles.length)h+="<p>Aucun trade terminé pour l'instant.</p>";
for(const k of cles){const S=d.strats[k],st=k.slice(0,k.lastIndexOf(" ")),a=k.slice(k.lastIndexOf(" ")+1);h+="<div class='card' style='margin-top:12px'><h2>"+(noms[st]||st)+" — "+a+"</h2><div>Trades : <b>"+S.n+"</b> · gagnés "+S.gains+" · perdus "+S.pertes+" · résultat <b>"+f(S.pnl)+"</b></div><div class='mu'>"+Object.entries(S.issues).map(([i,v])=>i+" : "+v.n+" ("+f(v.pnl)+")").join(" · ")+"</div>";
h+="<table style='margin-top:6px'><tr><th>Heure</th><th>Côté</th><th>Issue</th><th>Résultat</th><th>Détail</th></tr>"+S.trades.slice(0,25).map(T=>"<tr><td>"+new Date(T.heure).toLocaleTimeString("fr-CH")+"</td><td>"+(T.cote||"Up "+(T.U||0).toFixed(0)+" / Down "+(T.D||0).toFixed(0))+"</td><td>"+T.issue+"</td><td>"+f(T.net)+"</td><td class='mu' style='font-size:11px'>"+T.journal.slice(-4).join(" · ")+"</td></tr>").join("")+"</table></div>";}
if(d.ouvertes.length)h+="<div class='card' style='margin-top:12px'><h2>Positions ouvertes</h2>"+d.ouvertes.map(P=>"<div>"+(noms[P.strat]||P.strat)+" "+P.actif+" — "+P.journal.slice(-3).join(" · ")+"</div>").join("")+"</div>";
document.getElementById("app").innerHTML=h;}catch(e){document.getElementById("app").textContent="Erreur : "+e;}}
maj();setInterval(maj,5000);
</script></body></html>`;
const RAPPORT = `<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Rapport des refus</title>${STYLE}</head><body>
<h1>Rapport des refus</h1><div class="mu">Un bloc par marché candidat non tradé : le dernier refus avec ses chiffres, puis le nombre de secondes bloquées par motif.</div>
<div style="margin-top:8px"><a href="/">← Tableau de bord</a></div><div id="app" class="mu" style="margin-top:12px">Chargement…</div>
<script>
const nb=c=>Object.entries(c||{}).sort((a,b)=>b[1]-a[1]).map(([k,v])=>k+' : '+v+' s').join(' · ');
async function go(){const d=await (await fetch('/api/rapport')).json();const el=document.getElementById('app');el.className='';
el.innerHTML=d.refus.length?d.refus.map(r=>'<div class=card><b>'+r.actif+'</b> · '+new Date(r.heure).toLocaleString('fr-CH',{weekday:'short',hour:'2-digit',minute:'2-digit'})+' <span class=mu>'+(r.slug||'')+'</span><br><span class=wa><b>'+r.raison+'</b></span><br>'+r.explication+
'<div class=mu>Favori '+r.fav+' · vendeur '+r.ask+' · acheteur '+r.bid+' · T-'+r.tleft+' s'+(r.z!=null?' · z '+r.z+' · proba '+(r.proba*100).toFixed(2)+' %':'')+'</div><div class=mu>Secondes bloquées : '+nb(r.comptes)+'</div></div>').join(''):'<div class=card>Aucun refus enregistré pour l\\'instant.</div>'}
go();setInterval(go,10000);
</script></body></html>`;
