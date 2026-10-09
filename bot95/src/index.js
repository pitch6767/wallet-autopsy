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
  // désaccord modèle / marché (analyse du 06.10 : écart >= 0,10 → le modèle a raison 61 %, +0,07 $/part sur 12 jours) : achat taker au meilleur vendeur, gardé jusqu'à la fin
  // 07.10.2026 (décision de Pitch) : on ne garde que V1, assurance et désaccord 20 — tout le reste est arrêté (résultats figés sur la page)
  // 07.10.2026 (décision de Pitch) : on oublie ETH — plus aucun trade ETH (les données ETH restent enregistrées)
  TRADE: ["BTC"],
  CORRIGE_ACTIFS: ["BTC", "ETH"],                // cohorte « corrigé » aussi testée sur ETH (09.10.2026)
  ACTIVES: ["desaccord 20 sans nuit", "desaccord confirme perp", "V2-B hors 60-89 s", "V2-C perp", "V2-D perp 120-269 s", "V2-E persistant", "V2-F ecart qui grandit", "V2-F + pas les deux baissent", "V2-F + plus de 120 s", "V2-G jury des bourses", "V2-H veto complet", "desaccord 20 Poly rejoint 10 s sans nuit", "desaccord 20 Binance avec nous", "desaccord 20 Binance avec nous sans nuit", "desaccord 20 Binance ou perp avec nous", "desaccord 20 Binance ou perp avec nous sans nuit", "desaccord 30 zone 0,15-0,35", "desaccord 30 zone 0,15-0,35 + Binance et perp", "desaccord 30 zone + sortie modele -10", "desaccord 30 zone + Binance et perp + sortie modele -10", "desaccord 30 0,15-0,60 + perp + ecart qui grandit", "desaccord 30 zone + modele monte", "desaccord 30 zone + Binance et perp + sortie modele -10 + pas Poly qui baisse", "desaccord 30 zone + Binance et perp + sortie modele -10 + pas Poly qui baisse + taille 25/50", "corrige : V2-F + garde-fou", "TWAP fin", "corrige marge mesuree : V2-F", "corrige : desaccord 20", "corrige : V2-F ecart qui grandit", "corrige : V2-F + pas les deux baissent", "corrige : zone + Binance et perp + sortie -10"],
  // 09.10.2026 : stratégies à plus de 500 $ de pertes (et leurs lignes sœurs) — supprimées du bot et de la page ; trades sauvés dans bot95/sauvegarde sur GitHub
  SUPPRIMEES: ["V5 gain attendu BTC", "V5 gain attendu ETH", "V6 loterie BTC", "V6 loterie ETH", "desaccord 10 +convergence BTC", "desaccord 10 +convergence ETH", "desaccord 10 +demi ETH", "desaccord 10 +freeroll BTC", "desaccord 10 +freeroll ETH", "desaccord 10 +validation ETH", "desaccord 10 +validation+inversion ETH", "desaccord 10 +verrou BTC", "desaccord 10 +verrou ETH", "desaccord 10 ETH", "desaccord 15 +convergence BTC", "desaccord 15 +convergence ETH", "desaccord 15 +demi ETH", "desaccord 15 +freeroll BTC", "desaccord 15 +freeroll ETH", "desaccord 15 +validation ETH", "desaccord 15 +validation+inversion ETH", "desaccord 15 +verrou BTC", "desaccord 15 +verrou ETH", "desaccord 15 ETH", "desaccord 20 +convergence BTC", "desaccord 20 +convergence ETH", "desaccord 20 +demi BTC", "desaccord 20 +demi ETH", "desaccord 20 +freeroll BTC", "desaccord 20 +freeroll ETH", "desaccord 20 +validation BTC", "desaccord 20 +validation ETH", "desaccord 20 +validation+inversion BTC", "desaccord 20 +validation+inversion ETH", "desaccord 20 +verrou BTC", "desaccord 20 +verrou ETH", "desaccord 20 ETH", "desaccord 20 Poly rejoint 3 s BTC", "desaccord 20 Poly rejoint 3 s sans nuit BTC", "desaccord combine 2.5 +convergence BTC", "desaccord combine 2.5 +convergence ETH", "desaccord combine 2.5 +freeroll ETH", "desaccord combine 2.5 +validation+inversion ETH", "desaccord combine 2.5 +verrou BTC", "desaccord combine 2.5 +verrou ETH", "desaccord combine 2.5 ETH", "desaccord combine 4 +convergence BTC", "desaccord combine 4 +convergence ETH", "desaccord combine 4 +freeroll ETH", "desaccord combine 4 +validation+inversion ETH", "desaccord combine 4 +verrou ETH", "desaccord combine 4 ETH", "desaccord confirme BTC", "desaccord confirme ETH", "desaccord croise 10 +convergence BTC", "desaccord croise 10 +convergence ETH", "desaccord croise 10 +freeroll BTC", "desaccord croise 10 +freeroll ETH", "desaccord croise 10 +validation+inversion ETH", "desaccord croise 10 +verrou BTC", "desaccord croise 10 +verrou ETH", "desaccord croise 10 ETH", "desaccord maker 10 +convergence BTC", "desaccord maker 10 +freeroll BTC", "desaccord maker 10 +validation+inversion BTC", "desaccord maker 10 +verrou BTC", "desaccord maker 10 BTC", "inverse desaccord 10 BTC", "inverse desaccord 15 BTC", "V2-F + pas les deux baissent + volatilite >= 2 BTC", "desaccord 20 aucune bourse contre + sortie 10 s BTC", "desaccord 20 aucune bourse contre + sortie 10 s sans nuit BTC", "desaccord 20 Poly rejoint 10 s BTC", "assurance 6/9/12 BTC", "assurance 6/9/12 ETH", "assurance 4/7/10 BTC", "assurance 4/7/10 ETH", "desaccord 20 BTC"],
  // 07.10.2026 : désaccord CONFIRMÉ (analyse sur les vrais carnets) : écart >= 0,20 (BTC) / 0,10 (ETH) repéré, on attend 20 s,
  // on n'achète que si notre côté a déjà monté de 3 cents vers le modèle et que le modèle garde 3 cents d'avance ; gardé jusqu'à la fin.
  CONFIRME: { ECART: { BTC: 0.20, ETH: 0.10 }, ATTENTE_S: 20, HAUSSE: 0.03, AVANCE_MIN: 0.03, MISE: 50 },
  DESACCORD: { VARIANTES: { "desaccord 20": 0.20, "desaccord 20 sans nuit": 0.20 }, NUIT: { "desaccord 20 sans nuit": [0, 8] }, MISE: 50, TMIN: 5, ARRETES: true,
    // gestion après l'entrée (06.10) : copies de chaque désaccord gérées autrement, pour comparer
    GESTIONS: ["validation", "validation+inversion", "convergence", "verrou", "demi", "freeroll"], FENETRE_S: 20, MIN_S: 3,
    // nouvelles entrées (06.10 soir) : valeur combinée marché+modèle, maker, confirmation croisée BTC/ETH ; gestions testées sur ces entrées
    COMBINE: { "desaccord combine 2.5": 0.025, "desaccord combine 4": 0.04 },
    // poids (marché, modèle) en logit selon le temps restant — appris sur 12 jours (analyse calib du 06.10)
    POIDS: { BTC: [[60, 0.90, 0.45], [180, 0.75, 0.25], [301, 0.80, 0.20]], ETH: [[60, 0.85, 0.45], [180, 0.60, 0.40], [301, 0.65, 0.30]] },
    MAKER: { nom: "desaccord maker 10", ecart: 0.10, retrait: 0.04, duree_s: 30 },
    CROISE: { nom: "desaccord croise 10", ecart: 0.10, autre: 0.05 },
    GESTIONS_NOUVELLES: ["validation+inversion", "freeroll", "verrou", "convergence"] },
  FIN: { BTC: { W: 180, LO: 0.70, HI: 0.85, SEUIL: 0.95 }, ETH: { W: 90, LO: 0.70, HI: 0.90, SEUIL: 0.93 }, MISE: 50 },
  MM: { ACTIFS: [], ARRET_S: 10, MAXI: 100,                    // teneur de marché : 3 versions en parallèle (06.10.2026)
    VARIANTES: {                                                            // « actuel » et « pencher » arrêtés le 06.10.2026 (perdants en direct)
      "mm prudent": { MARGE: 0.12, DESEQ: 10, PAQUET: 10, PENCHER: 0.04, RETRAIT_PB: 2 } } },
};
const EVT_SRC = { perp: "p", okx: "o", bn: "n", cb: "c", cl: "l" };   // B/E + source ; carnet : BU/BD/EU/ED (meilleur achat, meilleure vente) ; échanges : BUt/BDt/EUt/EDt (prix, ±taille)
const SIG_COLS = ["t", "start", "prix_a_battre", "proba_up_modele", "bybit_perp", "okx_perp", "binance_spot", "coinbase", "chainlink", "bybit_meilleur_achat", "bybit_meilleure_vente",
  "prof_achat_1pb", "prof_vente_1pb", "prof_achat_3pb", "prof_vente_3pb", "prof_achat_5pb", "prof_vente_5pb", "prof_achat_10pb", "prof_vente_10pb",
  "perp_achats_usd", "perp_ventes_usd", "perp_plus_gros_achat", "perp_plus_grosse_vente", "perp_nb_echanges", "liq_longs_usd", "liq_courts_usd",
  "pm_up_achat", "pm_up_vente", "pm_up_achat_taille", "pm_up_vente_taille",
  "pm_up_retrait_achat", "pm_up_retrait_vente", "pm_up_ajout_achat", "pm_up_ajout_vente", "pm_up_echange_achat", "pm_up_echange_vente",
  "pm_down_retrait_achat", "pm_down_retrait_vente", "pm_down_ajout_achat", "pm_down_ajout_vente", "pm_down_echange_achat", "pm_down_echange_vente",
  "bybit_interet_ouvert", "bybit_financement", "bybit_base_pb", "deribit_perp", "deribit_interet_ouvert"];
const REC_COLS = ["t", "start", "proba_up_modele", "up_achat", "up_vente", "down_achat", "down_vente", "up_achat_taille", "up_vente_taille", "down_achat_taille", "down_vente_taille",
  "bybit_perp", "okx_perp", "coinbase", "binance_spot", "chainlink", "prix_a_battre"];
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
  SD_CORRIGE: 1.5e-4,          // modèle corrigé (09.10.2026) : la marge 0,08 % était un écart MAXIMUM, pas une incertitude ; 0,015 % est la plus précise sur 3 677 situations
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
      // stockage découpé (une valeur ne doit pas dépasser 128 Ko) : nv:base, nv:strat:<nom>, nv:ordres, nv:audit
      const base = await this.state.storage.get("nv:base");
      if (base) {
        this.N = { ...base, strats: {} };
        const st2 = await this.state.storage.list({ prefix: "nv:strat:" });
        for (const [k, v] of st2) this.N.strats[k.slice(9)] = v;
        this.N.ordres = (await this.state.storage.get("nv:ordres")) || [];
        this.N.audit = { fait: base.auditFait || {}, lignes: (await this.state.storage.get("nv:audit")) || [] };
      } else this.N = (await this.state.storage.get("nouveaux")) || { depuis: now(), strats: {}, ouvertes: [], attente: [] };
      for (const [ancien, neuf] of [["assurance", "assurance 6/9/12"], ["mm", "mm actuel"]]) {
        for (const k of Object.keys(this.N.strats)) if (k.startsWith(ancien + " ") && k.split(" ").length === 2) { this.N.strats[neuf + " " + k.split(" ")[1]] = this.N.strats[k]; delete this.N.strats[k]; }
        for (const P of [...this.N.ouvertes, ...this.N.attente]) if (P.strat === ancien) P.strat = neuf;
      }
      for (const k of NV.SUPPRIMEES) { delete this.N.strats[k]; await this.state.storage.delete(["nv:strat:" + k, "hist:" + k]); }
      const garde = (P) => !NV.SUPPRIMEES.includes(P.strat + " " + P.actif);
      this.N.ouvertes = (this.N.ouvertes || []).filter(garde); this.N.attente = (this.N.attente || []).filter(garde);
      this.BL = (await this.state.storage.get("blink")) || { depuis: now(), evts: [] };
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
    if (u.pathname === "/api/reglements") { const RG = this.RG || (await this.state.storage.get("regl")) || { lignes: [], attente: {} }; return json(RG); }
    if (u.pathname === "/api/hist") {
      const nom = u.searchParams.get("s") || "", S2 = this.N.strats[nom];
      return json({ nom, resume: S2 ? { depuis: S2.depuis, n: S2.n, gains: S2.gains, pertes: S2.pertes, pnl: S2.pnl } : null, archive: (await this.state.storage.get("hist:" + nom)) || [], derniers: S2 ? S2.trades : [] });
    }
    if (u.pathname === "/api/latence") {
      // mesure SANS ordre réel : aller-retour HTTP vers le carnet Polymarket (GET /time) et vers la porte des ordres (POST /order vide, refusé)
      const n = Math.min(30, +(u.searchParams.get("n") || 15)), mes = { time: [], order: [] }, codes = {};
      for (let k = 0; k < n; k++) {
        let t0 = Date.now(); try { await (await fetch(`${C}/time`, { cf: { cacheTtl: 0 } })).text(); mes.time.push(Date.now() - t0); } catch (_) {}
        t0 = Date.now();
        try { const r = await fetch(`${C}/order`, { method: "POST", headers: { "content-type": "application/json" }, body: "{}" }); await r.text(); mes.order.push(Date.now() - t0); codes[r.status] = (codes[r.status] || 0) + 1; } catch (_) {}
      }
      const q = (L, x) => { if (!L.length) return null; const b = [...L].sort((a2, b2) => a2 - b2); return b[Math.min(b.length - 1, Math.floor(b.length * x))]; };
      let trace = ""; try { trace = await (await fetch("https://www.cloudflare.com/cdn-cgi/trace")).text(); } catch (_) {}
      const qs = (L) => (L.length ? +q(L, 0.5).toFixed(3) : null);
      return json({ ms_time: { med: q(mes.time, 0.5), p90: q(mes.time, 0.9), min: Math.min(...mes.time) }, ms_order: { med: q(mes.order, 0.5), p90: q(mes.order, 0.9), min: Math.min(...mes.order) }, codes_order: codes,
        ws_message_s: { med: qs(this.latPoly), p90: this.latPoly.length ? +q(this.latPoly, 0.9).toFixed(3) : null }, decision_s: { med: qs(this.latDec), p90: this.latDec.length ? +q(this.latDec, 0.9).toFixed(3) : null },
        sortie_cloudflare: (trace.match(/colo=(\w+)/) || [])[1] || null, entree: (req.cf || {}).colo || null });
    }
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
    if (u.pathname === "/api/evt") {
      const n = Math.min(80, +(u.searchParams.get("n") || 40)), apres = u.searchParams.get("apres");
      const m = await this.state.storage.list({ prefix: "evt:", limit: n, ...(apres ? { startAfter: apres } : {}) });
      const ks = [...m.keys()];
      return json({ cles: ks, docs: [...m.values()], suivant: ks.length ? ks[ks.length - 1] : null });
    }
    if (u.pathname === "/api/rec") {
      const a = u.searchParams.get("a") || "BTC", n = Math.min(60, +(u.searchParams.get("n") || 30)), apres = u.searchParams.get("apres");
      const m = await this.state.storage.list({ prefix: `rec:${a}:`, limit: n, ...(apres ? { startAfter: apres } : {}) });
      const ks = [...m.keys()];
      return json({ cles: ks, docs: [...m.values()], suivant: ks.length ? ks[ks.length - 1] : null });
    }
    if (u.pathname === "/api/sig") {
      const a = u.searchParams.get("a") || "BTC", n = Math.min(120, +(u.searchParams.get("n") || 60)), apres = u.searchParams.get("apres");
      const m = await this.state.storage.list({ prefix: `sig:${a}:`, limit: n, ...(apres ? { startAfter: apres } : {}) });
      const ks = [...m.keys()];
      return json({ cles: ks, docs: [...m.values()], suivant: ks.length ? ks[ks.length - 1] : null });
    }
    if (u.pathname === "/api/lead") {
      const n = Math.min(40, +(u.searchParams.get("n") || 20)), apres = u.searchParams.get("apres");
      const m = await this.state.storage.list({ prefix: "lead:", limit: n, ...(apres ? { startAfter: apres } : {}) });
      const ks = [...m.keys()];
      return json({ cles: ks, docs: [...m.values()], suivant: ks.length ? ks[ks.length - 1] : null });
    }
    if (u.pathname === "/api/m97") {
      const n = Math.min(60, +(u.searchParams.get("n") || 30)), apres = u.searchParams.get("apres");
      const m = await this.state.storage.list({ prefix: "m97:", limit: n, ...(apres ? { startAfter: apres } : {}) });
      const ks = [...m.keys()];
      return json({ cles: ks, docs: [...m.values()], suivant: ks.length ? ks[ks.length - 1] : null });
    }
    if (u.pathname === "/api/m97/compte") { const m = await this.state.storage.list({ prefix: "m97:", limit: 20000 }); return json({ n: m.size }); }
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
    if (u.pathname === "/api/nouveaux") return json({ ...this.nVue(), pv: PAGE_N_V });
    if (u.pathname === "/nouveaux") return new Response(PAGE_N.replace("__PV__", PAGE_N_V), { headers: { "content-type": "text/html; charset=utf-8", "cache-control": "no-store" } });
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
  // enregistreur (≈ 4 fois par seconde) : modèle, carnet Polymarket, bourses — par minute dans le stockage, gardé 48 h
  enregistrer(t) {
    if (t - (this._recT || 0) < 0.25) return; this._recT = t;
    for (const a of V1.ACTIFS) {
      const mk = this.mk[a]; if (!mk || !mk.up || !mk.strike) continue;
      let pu = null; try { pu = this.probaV1(a, mk); } catch (_) {}
      const b = (id, c) => (this.livreTrie(id, c)[0] || [null, null]);
      const [ub, ubs] = b(mk.up, "bids"), [ua, uas] = b(mk.up, "asks"), [db, dbs] = b(mk.down, "bids"), [da, das] = b(mk.down, "asks");
      const px = (src) => (this.f[a][src] ? +this.f[a][src].p : null);
      const r4 = (x) => (x == null ? null : +x.toFixed(4));
      const ligne = [+t.toFixed(2), mk.start, r4(pu), ub, ua, db, da, ubs && Math.round(ubs), uas && Math.round(uas), dbs && Math.round(dbs), das && Math.round(das),
        px("perp"), px("okx"), px("cb"), px("bn"), px("cl"), +(+mk.strike).toFixed(4)];
      const minute = Math.floor(t / 60);
      const R = ((this._rec = this._rec || {})[a] = this._rec[a] || { minute, lignes: [] });
      if (R.minute !== minute) {
        if (R.lignes.length) this.state.storage.put(`rec:${a}:${R.minute}`, { colonnes: REC_COLS, lignes: R.lignes }).catch(() => {});
        R.minute = minute; R.lignes = [];
        if (minute % 30 === 0) this.state.storage.list({ prefix: `rec:${a}:`, limit: 200 }).then((m2) => { const ks = [...m2.keys()].filter((k) => +k.split(":")[2] < minute - 2880).slice(0, 120); if (ks.length) this.state.storage.delete(ks); }).catch(() => {});
      }
      R.lignes.push(ligne);
    }
  }
  // ---- moments « 97 c » (07.10.2026, demande de Pitch) : le favori se vend 0,93-0,985 entre 150 et 10 s de la fin.
  // On photographie tout ce qui pourrait prédire un retournement : 10 s de boîte noire (prix, carnet Bybit, flux, liquidations, carnets et retraits Polymarket),
  // carnets profonds Bybit perp + Binance spot (mur entre le prix et le prix à battre), intérêt ouvert Bybit, options Deribit (intérêt ouvert par prix d'exercice).
  // Deux photos max par cycle et par crypto : à l'entrée dans la zone, puis vers 30 s de la fin. Le résultat officiel est lu ensuite par l'analyse.
  m97(a, mk, pu, tleft) {
    if (!V1.ACTIFS.includes(a) || !mk.up || !mk.strike || tleft > 150 || tleft < 10) return;
    const fa = [["Up", mk.up], ["Down", mk.down]].map(([c, id]) => [c, id, (this.livreTrie(id, "asks")[0] || [null])[0]]).filter((x) => x[2] != null && x[2] >= 0.93 && x[2] <= 0.985);
    if (!fa.length) return;
    const Z = ((this._m97 = this._m97 || {})[a] = this._m97[a] && this._m97[a].start === mk.start ? this._m97[a] : { start: mk.start, n: 0, enCours: false });
    const phase = Z.n === 0 ? "entree" : (Z.n === 1 && tleft <= 35 ? "30s" : null);
    if (!phase || Z.enCours) return;
    Z.enCours = true; Z.n++;
    const [cote, , ask] = fa[0], t = now(), px = (src) => (this.f[a][src] ? +this.f[a][src].p : null);
    const doc = { actif: a, start: mk.start, slug: mk.slug, phase, t: +t.toFixed(2), tleft: +tleft.toFixed(1), cote, ask, proba_modele: pu, strike: +mk.strike,
      perp: px("perp"), chainlink: px("cl"), spot_binance: px("bn"), coinbase: px("cb"),
      liq_30s: (this.liq[a] || []).map((x) => [+(x.t - t).toFixed(1), x.cote, Math.round(x.usd)]),
      boite: { colonnes: BB_COLONNES, lignes: ((this.bbR || {})[a] || []).slice() } };
    const sym = ACTIFS[a].bybit, ref = doc.perp || doc.spot_binance;
    const tranches = (cote2, niveaux) => {          // liquidité en $ par tranche de distance au prix (pb)
      const B = [2, 5, 10, 20, 50, 100, 200], out = B.map(() => 0);
      for (const [p, q] of niveaux) { const d = Math.abs(p / ref - 1) * 1e4; const i = B.findIndex((x) => d <= x); if (i >= 0) out[i] += p * q; }
      return out.map(Math.round);
    };
    const prend = async (url) => { try { const r = await fetch(url, { headers: { "User-Agent": "bot95" } }); return r.ok ? await r.json() : null; } catch (_) { return null; } };
    (async () => {
      const [bb, bn, oi, dr] = await Promise.all([
        prend(`https://api.bybit.com/v5/market/orderbook?category=linear&symbol=${sym}&limit=500`),
        prend(`https://data-api.binance.vision/api/v3/depth?symbol=${sym}&limit=5000`),
        prend(`https://api.bybit.com/v5/market/open-interest?category=linear&symbol=${sym}&intervalTime=5min&limit=6`),
        prend(`https://www.deribit.com/api/v2/public/get_book_summary_by_currency?currency=${a}&kind=option`)]);
      if (ref) {
        const r2 = bb && bb.result; if (r2) doc.bybit_prof = { tranches_pb: [2, 5, 10, 20, 50, 100, 200], achat: tranches("b", (r2.b || []).map(([p, q]) => [+p, +q])), vente: tranches("a", (r2.a || []).map(([p, q]) => [+p, +q])),
          entre_prix_et_strike_achat: Math.round((r2.b || []).filter(([p]) => +p >= Math.min(ref, doc.strike) && +p <= Math.max(ref, doc.strike)).reduce((s2, [p, q]) => s2 + p * q, 0)),
          entre_prix_et_strike_vente: Math.round((r2.a || []).filter(([p]) => +p >= Math.min(ref, doc.strike) && +p <= Math.max(ref, doc.strike)).reduce((s2, [p, q]) => s2 + p * q, 0)) };
        if (bn && bn.bids) doc.binance_prof = { achat: tranches("b", bn.bids.map(([p, q]) => [+p, +q])), vente: tranches("a", bn.asks.map(([p, q]) => [+p, +q])),
          entre_prix_et_strike_achat: Math.round(bn.bids.filter(([p]) => +p >= Math.min(ref, doc.strike)).reduce((s2, [p, q]) => s2 + p * q, 0)),
          entre_prix_et_strike_vente: Math.round(bn.asks.filter(([p]) => +p <= Math.max(ref, doc.strike)).reduce((s2, [p, q]) => s2 + p * q, 0)) };
      }
      if (oi && oi.result) doc.interet_ouvert = (oi.result.list || []).map((x) => [+x.timestamp, +x.openInterest]);
      if (dr && dr.result && ref) {                 // options : intérêt ouvert par prix d'exercice proche (±3 %), échéances des 2 prochains jours
        const lim = Date.now() + 2 * 86400e3, S = {};
        for (const o of dr.result) {
          const [, exp, k, cp] = (o.instrument_name || "").split("-"); const K = +k;
          if (!K || Math.abs(K / ref - 1) > 0.03) continue;
          const e = Date.parse(exp.replace(/(\d+)([A-Z]+)(\d+)/, "$1 $2 20$3") + " 08:00 UTC"); if (!(e <= lim)) continue;
          const z = (S[K] = S[K] || [0, 0]); z[cp === "C" ? 0 : 1] += +o.open_interest || 0;
        }
        doc.options_oi = Object.entries(S).map(([k, v]) => [+k, +v[0].toFixed(1), +v[1].toFixed(1)]).sort((x, y) => x[0] - y[0]);
      }
      await this.state.storage.put("m97:" + Math.floor(t * 1000).toString().padStart(14, "0") + ":" + a, doc);
      this.m97N = (this.m97N || 0) + 1;
      if (this.m97N % 100 === 0) { const m = await this.state.storage.list({ prefix: "m97:", limit: 20000 }); const ks = [...m.keys()]; if (ks.length > 8000) await this.state.storage.delete(ks.slice(0, Math.min(128, ks.length - 8000))); }
    })().catch((err) => this.erreur("moments 97", err)).finally(() => { Z.enCours = false; });
  }

  sigB(a) { return ((this._sgB = this._sgB || {})[a] = this._sgB[a] || { ach: 0, ven: 0, max_ach: 0, max_ven: 0, n: 0, liq_longs: 0, liq_courts: 0 }); }
  sigP(id) { return ((this._sgP = this._sgP || {})[id] = this._sgP[id] || { retrait_achat: 0, retrait_vente: 0, ajout_achat: 0, ajout_vente: 0, echange_achat: 0, echange_vente: 0 }); }
  // ---- signaux en continu, 1 ligne par seconde et par crypto (07.10.2026) : pour construire le meilleur prédicteur à 1 minute et le comparer au prix Polymarket.
  // Gardé 4 jours. Intérêt ouvert / financement Bybit et perp Deribit lus toutes les 15 s (REST).
  signaux(t) {
    if (t - (this._sgT || 0) < 1) return; this._sgT = t;
    if (t - (this._sgX || 0) >= 15) { this._sgX = t; this.sigExterne().catch(() => {}); }
    for (const a of V1.ACTIFS) {
      const L = this.livre[a], mk = this.mk[a] || {};
      const b = [...L.b].map(([p, q2]) => [+p, q2]).sort((x, y) => y[0] - x[0]), k = [...L.a].map(([p, q2]) => [+p, q2]).sort((x, y) => x[0] - y[0]);
      const mid = b.length && k.length ? (b[0][0] + k[0][0]) / 2 : null;
      const prof = (cote, bps) => mid ? Math.round(cote.filter(([p]) => Math.abs(p / mid - 1) * 1e4 <= bps).reduce((s2, [p, q2]) => s2 + p * q2, 0)) : null;
      const px = (src) => (this.f[a][src] ? +this.f[a][src].p : null);
      let pu = null; try { if (mk.up && mk.strike) pu = this.probaV1(a, mk); } catch (_) {}
      const bk = (id, c) => (id ? (this.livreTrie(id, c)[0] || [null, null]) : [null, null]);
      const [ub, ubs] = bk(mk.up, "bids"), [ua, uas] = bk(mk.up, "asks");
      const sg = this.sigB(a), fl = (id) => { if (!id) return [null, null, null, null, null, null]; const z = this.sigP(id), r = Object.values(z).map(Math.round); for (const kk of Object.keys(z)) z[kk] = 0; return r; };
      const X = (this._sgE || {})[a] || {};
      const ligne = [Math.floor(t), mk.start || null, mk.strike ? +(+mk.strike).toFixed(4) : null, pu == null ? null : +pu.toFixed(4),
        px("perp"), px("okx"), px("bn"), px("cb"), px("cl"), b.length ? b[0][0] : null, k.length ? k[0][0] : null,
        prof(b, 1), prof(k, 1), prof(b, 3), prof(k, 3), prof(b, 5), prof(k, 5), prof(b, 10), prof(k, 10),
        Math.round(sg.ach), Math.round(sg.ven), Math.round(sg.max_ach), Math.round(sg.max_ven), sg.n, Math.round(sg.liq_longs), Math.round(sg.liq_courts),
        ub, ua, ubs == null ? null : Math.round(ubs), uas == null ? null : Math.round(uas), ...fl(mk.up), ...fl(mk.down),
        X.oi ?? null, X.funding ?? null, X.basis ?? null, X.deribit ?? null, X.deribit_oi ?? null];
      for (const kk of Object.keys(sg)) sg[kk] = 0;
      const minute = Math.floor(t / 60);
      const R = ((this._sgR = this._sgR || {})[a] = this._sgR[a] || { minute, lignes: [] });
      if (R.minute !== minute) {
        if (R.lignes.length) this.state.storage.put(`sig:${a}:${R.minute}`, { colonnes: SIG_COLS, lignes: R.lignes }).catch(() => {});
        R.minute = minute; R.lignes = [];
        if (minute % 30 === 0) this.state.storage.list({ prefix: `sig:${a}:`, limit: 300 }).then((m2) => { const ks = [...m2.keys()].filter((kk) => +kk.split(":")[2] < minute - 5760).slice(0, 120); if (ks.length) this.state.storage.delete(ks); }).catch(() => {});
      }
      R.lignes.push(ligne);
    }
  }
  async sigExterne() {
    const prend = async (url) => { try { const r = await fetch(url, { headers: { "User-Agent": "bot95" } }); return r.ok ? await r.json() : null; } catch (_) { return null; } };
    for (const a of V1.ACTIFS) {
      const [by, dr] = await Promise.all([prend(`https://api.bybit.com/v5/market/tickers?category=linear&symbol=${ACTIFS[a].bybit}`), prend(`https://www.deribit.com/api/v2/public/ticker?instrument_name=${a}-PERPETUAL`)]);
      const X = ((this._sgE = this._sgE || {})[a] = this._sgE[a] || {});
      const y = by && by.result && (by.result.list || [])[0];
      if (y) { X.oi = +y.openInterest; X.funding = +y.fundingRate; X.basis = y.indexPrice ? +((+y.markPrice / +y.indexPrice - 1) * 1e4).toFixed(3) : null; }
      if (dr && dr.result) { X.deribit = +dr.result.last_price || +dr.result.mark_price; X.deribit_oi = +dr.result.open_interest; }
    }
  }

  echantillonner() {
    const t = now();
    try { this.enregistrer(t); } catch (_) {}
    try { this.signaux(t); } catch (err) { this.erreur("signaux", err); }
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
    // 09.10.2026 : on ne relance que si le flux entier est muet 20 s (avant : dès qu'UNE petite crypto n'avait pas de trade depuis 20 s → coupure toutes les 20-30 s)
    const muet = (k) => t - (this.ws[k + "_msg"] || this.ws[k + "_ouvert"] || 0);
    if (!this.ws.perp || (muet("perp") > 20 && depuis("perp") > 20)) {
      for (const a of LISTE) this.livre[a] = { b: new Map(), a: new Map() };
      const args = LISTE.flatMap((a) => [`publicTrade.${ACTIFS[a].bybit}`, `orderbook.50.${ACTIFS[a].bybit}`, `allLiquidation.${ACTIFS[a].bybit}`]);
      this.connecter("perp", "https://stream.bybit.com/v5/public/linear", [JSON.stringify({ op: "subscribe", args })], (m) => this.surPerp(m), JSON.stringify({ op: "ping" }), 10000);
    }
    if (!this.ws.cb || (muet("cb") > 30 && depuis("cb") > 30)) {
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
    if (!this.ws.cl || (muet("cl") > 20 && depuis("cl") > 20)) this.connecter("cl", "https://ws-live-data.polymarket.com",
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
        this.ws[nom + "_msg"] = now();
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

  // enregistreur au message près : [ms, code, valeur1, valeur2] ; actif 10 min par heure ; blocs de 15 s « evt:<bloc> », gardés 24 h
  evt(code, x, y) {
    const ms = Date.now(), min = Math.floor(ms / 60000);
    if (min % 60 >= 10) { if (this._evB && this._evB.l.length) this.evtFlush(); return; }
    const bloc = Math.floor(ms / 15000);
    if (!this._evB || this._evB.bloc !== bloc) { if (this._evB && this._evB.l.length) this.evtFlush(); this._evB = { bloc, l: [] }; }
    this._evB.l.push(y === undefined ? [ms, code, x] : [ms, code, x, y]);
  }
  evtFlush() {
    const B = this._evB; this._evB = null; if (!B) return;
    this.state.storage.put("evt:" + B.bloc, B.l).catch(() => {});
    if (B.bloc % 40 === 0) this.state.storage.list({ prefix: "evt:", limit: 400 }).then((m2) => { const ks = [...m2.keys()].filter((k) => +k.slice(4) < B.bloc - 5760).slice(0, 120); if (ks.length) this.state.storage.delete(ks); }).catch(() => {});
  }
  noter(a, k, p, t) {
    if (V1.ACTIFS.includes(a) && EVT_SRC[k]) { const last = (this._evL = this._evL || {})[a + k]; if (last !== p) { this._evL[a + k] = p; this.evt(a[0] + EVT_SRC[k], p); } }
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
      if (V1.ACTIFS.includes(a)) { const sg = this.sigB(a); for (const y of m.data || []) { const u2 = +y.v * +y.p; sg.n++; if (y.S === "Buy") { sg.ach += u2; sg.max_ach = Math.max(sg.max_ach, u2); } else { sg.ven += u2; sg.max_ven = Math.max(sg.max_ven, u2); } } }
      if (V1.ACTIFS.includes(a)) { const ac = this.bbAcc(a); for (const y of m.data || []) { const u2 = +y.v * +y.p; ac.n++; if (y.S === "Buy") { ac.ach += u2; ac.max_ach = Math.max(ac.max_ach, u2); } else { ac.ven += u2; ac.max_ven = Math.max(ac.max_ven, u2); } } }
      const x = (m.data || []).slice(-1)[0];
      if (x) { this.noter(a, "perp", +x.p, t); if (V1.ACTIFS.includes(a)) this.v1Declencher(a, "perp", +x.T / 1000, t); }
    }
    else if (tp.startsWith("allLiquidation")) {
      for (const x of m.data || []) this.liq[a].push({ t, cote: x.S === "Buy" ? "SELL" : "BUY", usd: (+x.v) * (+x.p) });   // Buy = position longue liquidée
      if (V1.ACTIFS.includes(a)) { const sg = this.sigB(a); for (const x of m.data || []) { if (x.S === "Buy") sg.liq_longs += (+x.v) * (+x.p); else sg.liq_courts += (+x.v) * (+x.p); } }
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
    // horodatages bruts du flux (audit du 09.10.2026) : heure de l'observation (p.timestamp), du message (m.timestamp), de réception
    if (sym === "BTC" || sym === "ETH") {
      const B = ((this._clBrut = this._clBrut || {})[sym] = this._clBrut[sym] || []);
      B.push([+(p.timestamp || 0) / 1000, +(m.timestamp || 0) / 1000, now(), +p.value]);
      while (B.length && now() - B[0][2] > 420) B.shift();
    }
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
  async prixABattreOfficiel(a, mk) {
    // 1) priceToBeat officiel du cycle (publié tard) ; 2) sinon finalPrice officiel du cycle précédent (= prix à battre de celui-ci)
    const meta = async (st) => {
      const ev = await (await fetch(`${G}/events?slug=${a.toLowerCase()}-updown-5m-${st}`)).json();
      const e = ev && ev[0], m = e && e.markets && e.markets[0]; if (!e) return {};
      let x = e.eventMetadata || (m && m.eventMetadata) || {}; if (typeof x === "string") x = JSON.parse(x); return x || {};
    };
    let k = null, src = null;
    const m0 = await meta(mk.start); if (+m0.priceToBeat > 0) { k = +m0.priceToBeat; src = "priceToBeat"; }
    if (k == null) { const m1 = await meta(mk.start - 300); if (+m1.finalPrice > 0) { k = +m1.finalPrice; src = "finalPrice du cycle précédent"; } }
    if (k == null) return;
    mk.ptbOff = true; mk.ptbOfficiel = k;
    if (mk.twapK) return;
    if (mk.strike && Math.abs(mk.strike - k) > 0.01) mk.strikeAvant = mk.strike;
    mk.strike = k; mk.strikeSrc = src; mk.ptbVu = +(now() - mk.start).toFixed(1);
  }
  async ouvertureOfficielle(a, mk) {
    const iso = (t) => new Date(t * 1000).toISOString().replace(".000", "");
    const r = await fetch(`https://polymarket.com/api/crypto/crypto-price?symbol=${a}&eventStartTime=${iso(mk.start)}&variant=fiveminute&endDate=${iso(mk.end)}`, { headers: { "User-Agent": "Mozilla/5.0", Accept: "application/json" } });
    if (!r.ok) throw new Error(a + " prix d'ouverture HTTP " + r.status);
    const d = await r.json();
    if (d && +d.openPrice > 0) { mk.strikeSite = +d.openPrice; if (!mk.twapK) mk.strike = +d.openPrice; }
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
        if (mk) { (this._kPrec = this._kPrec || {})[a + mk.start] = { k: mk.strike ?? null, src: mk.strikeSrc || null, vu: mk.ptbVu ?? null, avant: mk.strikeAvant ?? null, serie: mk.kSerie || null, site: mk.strikeSite ?? null }; this.finFenetre(a, mk); }
        mk = this.mk[a] = (V1.ACTIFS.includes(a) && this.mkNx[a] && this.mkNx[a].start === start) ? { ...this.mkNx[a] } : { start, end: start + 300 };
      }
      try {
        if (!mk.slug && t - (mk.essai || 0) > 10) { mk.essai = t; Object.assign(mk, await this.chargerMarche(a, start)); }
        // PRIX À BATTRE = MOYENNE CHAINLINK DES 60 SECONDES AVANT LE DÉBUT (découvert le 09.10.2026 : colle au prix officiel à 0,19 $ près en médiane,
        // sur 710 cycles ; le chiffre affiché par le site est le prix instantané, faux de 10 $ en médiane). Calculé dès la 2e seconde du cycle.
        if (!mk.twapK && t >= start + 2) {
          const v = []; for (let s2 = start - 60; s2 <= start - 1; s2++) { const o2 = this.sec[a].get(s2); if (o2 && o2.cl != null) v.push(o2.cl); }
          if (v.length >= 40) { if (mk.strike) mk.strikeSite = mk.strike; mk.strike = v.reduce((x, y) => x + y, 0) / v.length; mk.twapK = true; mk.strikeSrc = "moyenne Chainlink 60 s"; mk.ptbVu = +(t - start).toFixed(1); }
        }
        // prix à battre OFFICIEL : priceToBeat de la fiche du marché (API Polymarket), relu toutes les 3 s tant qu'il manque (09.10.2026)
        if (!mk.ptbOff && ["BTC", "ETH"].includes(a) && t - (mk.essaiPtb || 0) > (t - start < 60 ? 5 : 15)) { mk.essaiPtb = t; await this.prixABattreOfficiel(a, mk); }
        // secours seulement si la fiche ne le donne pas encore après 20 s
        // prix d'ouverture Polymarket (celui affiché sur le site) : relu toutes les 5 s pendant les 2 premières minutes (BTC, ETH), chaque valeur notée (09.10.2026)
        if (["BTC", "ETH"].includes(a) && !mk.ptbOff && t - start < 120 && t - (mk.essaiOff || 0) > 5) {
          mk.essaiOff = t; const avant = mk.strike;
          try { await this.ouvertureOfficielle(a, mk); } catch (err) { (mk.kSerie = mk.kSerie || []).push([+(t - start).toFixed(1), "err " + String(err.message || err).slice(-3)]); throw err; }
          if (mk.strike) { if (!mk.twapK) mk.strikeSrc = "crypto-price"; const L2 = (mk.kSerie = mk.kSerie || []); if (!L2.length || L2[L2.length - 1][1] !== mk.strike) L2.push([+(t - start).toFixed(1), mk.strike]); if (avant && avant !== mk.strike) mk.strikeAvant = avant; }
        } else if (!mk.strike && !["BTC", "ETH"].includes(a) && t - (mk.essaiOff || 0) > 15) { mk.essaiOff = t; await this.ouvertureOfficielle(a, mk); if (mk.strike) mk.strikeSrc = "crypto-price"; }
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
        { const z = this.pmAcc(c.asset_id), cs = c.side === "BUY" ? "achat" : "vente"; if (apres < avant) z["retrait_" + cs] += (avant - apres) * +c.price; else z["ajout_" + cs] += (apres - avant) * +c.price;
          const z2 = this.sigP(c.asset_id); if (apres < avant) z2["retrait_" + cs] += (avant - apres) * +c.price; else z2["ajout_" + cs] += (apres - avant) * +c.price; }
        apres ? cote.set(+c.price, apres) : cote.delete(+c.price);
      }
    } else if (ev === "last_trade_price") {
      this.noterFlux(m.asset_id, "echange_" + (m.side === "BUY" ? "achat" : "vente"), +m.price * +m.size, t);
      this.pmAcc(m.asset_id)["echange_" + (m.side === "BUY" ? "achat" : "vente")] += +m.price * +m.size;
      this.sigP(m.asset_id)["echange_" + (m.side === "BUY" ? "achat" : "vente")] += +m.price * +m.size;
      this.v1Echange(m.asset_id, m.side, +m.price, +m.size);
    } else return;
    // enregistreur au message près : meilleur prix de chaque jeton des cycles en cours, et échanges
    try {
      const ids = ev === "price_change" ? [...new Set((m.price_changes || []).map((c) => c.asset_id))] : [m.asset_id];
      for (const jid of ids) {
        const a2 = this.actifDuJeton(jid); if (!a2) continue;
        const code = a2[0] + (this.mk[a2].up === jid ? "U" : "D");
        if (ev === "last_trade_price") { this.evt(code + "t", +m.price, (m.side === "BUY" ? 1 : -1) * Math.round(+m.size)); continue; }
        const b = (this.livreTrie(jid, "bids")[0] || [null])[0], k2 = (this.livreTrie(jid, "asks")[0] || [null])[0], cle = b + "/" + k2;
        if ((this._evT = this._evT || {})[jid] !== cle) { this._evT[jid] = cle; this.evt(code, b, k2); }
      }
    } catch (_) {}
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
    if (!NV.TRADE.includes(a) && !this.v1Etat(a).pos) return;          // plus de nouvelle entrée hors BTC (une position ouverte va jusqu'au bout)
    if (t - (this._v1t[a] || 0) <= 0.2) return;
    this._v1t[a] = t;
    try { this.v1Eval(source, ts, a); } catch (err) { this.erreur("V1 " + a, err); }
  }

  probaV1(a, mk, sdRel = CFG.SD_ECART_REL) {
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
    const sg = sgc.v, ts = Math.floor(t), deb = mk.end - 60;          // règlement = moyenne Chainlink des secondes fin-60 … fin-1 (vérifié le 09.10.2026)
    let E, v;
    if (ts >= deb) {
      const connus = []; for (let s2 = deb; s2 <= Math.min(ts, mk.end - 1); s2++) { const x = this.prixA(a, "cl", s2); if (x) connus.push(x); }
      const nr = Math.max(1, mk.end - 1 - ts);
      E = (connus.reduce((x, y) => x + y, 0) + nr * S) / (connus.length + nr); v = (sg * S) ** 2 * nr ** 3 / 3 / 3600;
    } else { E = S; v = (sg * S) ** 2 * ((deb - ts) + 20); }
    return phi((E - K) / Math.sqrt(v + (sdRel * S) ** 2));
  }

  // marge d'erreur MESURÉE (09.10.2026) : écart type entre notre prix à battre et l'officiel, et entre notre Chainlink de fin et le prix final officiel,
  // sur les 50 derniers cycles réglés de cet actif ; 12 $ (BTC) / 0,6 $ (ETH) tant qu'il y a moins de 10 cycles
  margeMesuree(a) {
    const RG = this.RG; const L = RG ? RG.lignes.filter((x) => x.a === a && x.ptb && x.notreK).slice(0, 50) : [];
    const defaut = a === "BTC" ? 12 : a === "ETH" ? 0.6 : null;
    if (L.length < 10) return defaut;
    const eK = L.map((x) => x.notreK - x.ptb).filter((e) => Math.abs(e) < 200);
    const suiv = new Map(RG.lignes.filter((x) => x.a === a && x.ptb).map((x) => [x.start, x.ptb]));
    const eF = L.filter((x) => x.notreClFin && suiv.has(x.start + 300)).map((x) => x.notreClFin - suiv.get(x.start + 300)).filter((e) => Math.abs(e) < 200);
    const rms = (v) => (v.length ? Math.sqrt(v.reduce((s2, e) => s2 + e * e, 0) / v.length) : 0);
    return Math.sqrt(rms(eK) ** 2 + rms(eF) ** 2) || defaut;
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
        try { this.nTenter("V1", a, mk, up, V1.PMAX, V.pos.mise, fair); } catch (_) {}
        try { this.nInverse("V1", a, mk, up, V.pos.mise); this.nSauver(); } catch (_) {}
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
  nSauver() {
    if (this._nsv) return;
    this._nsv = setTimeout(() => {
      this._nsv = null;
      const N = this.N, put = (k, v) => this.state.storage.put(k, v).catch((err) => this.erreur("sauvegarde " + k, err));
      put("nv:base", { depuis: N.depuis, ouvertes: N.ouvertes, attente: N.attente, manq: N.manq, auditFait: (N.audit || {}).fait || {}, ordAgg: N.ordAgg || {}, markout: N.markout || {} });
      for (const [k, v] of Object.entries(N.strats)) put("nv:strat:" + k, v);
      // ordres : non réglés + 250 derniers réglés (les compteurs sont cumulés à part)
      const O = N.ordres || [], nonRegles = O.filter((x) => x.gagne == null), regles = O.filter((x) => x.gagne != null);
      N.ordres = [...regles.slice(-250), ...nonRegles];
      put("nv:ordres", N.ordres);
      put("nv:audit", ((N.audit || {}).lignes || []).slice(0, 150));
    }, 1000);
  }
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
    if (!S2.rq || !S2.rq.hist) S2.rq = nRisqueDepuis(S2.trades);
    nRisquePas(S2.rq, P.net);
    S2.n++; S2.pnl += P.net; if (P.net >= 0) S2.gains++; else S2.pertes++;
    (S2.issues[issue] = S2.issues[issue] || { n: 0, pnl: 0 }).n++; S2.issues[issue].pnl += P.net;
    P.journal = P.journal.slice(-6);
    S2.trades.unshift(P); S2.trades.length = Math.min(S2.trades.length, 60);
    // archive compacte de TOUS les trades (09.10.2026) : [heure, côté, prix, net, issue, modèle, secondes restantes]
    const kh = "hist:" + P.strat + " " + P.actif, ligne = [P.heure, P.cote || null, P.prix ?? null, P.net, issue, P.proba0 ?? null, P.restant_s ?? null];
    this.state.storage.get(kh).then((L) => { L = L || []; L.push(ligne); if (L.length > 1500) L.splice(0, L.length - 1500); return this.state.storage.put(kh, L); }).catch((err) => this.erreur("archive " + kh, err));
    this.N.ouvertes = this.N.ouvertes.filter((x) => x !== P);
    this.nSauver();
  }

  // ---- 1. V1 avec assurance graduée à la place du stop : même entrée que V1
  gOuvrir(a, mk, vpos) {
    const up = vpos.cote === "Up";
    for (const [nom, niveaux] of Object.entries(NV.ASSUR.VARIANTES)) {
      if (!NV.ACTIVES.includes(nom)) continue;
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
    try { this.m97(a, mk, pu, tleft); } catch (err) { this.erreur("moments 97", err); }
    for (const P of this.N.ouvertes) if (P.strat.startsWith("assurance") && P.actif === a && P.start === mk.start && !P.fini) this.gGerer(P, pu);
    for (const P of this.N.ouvertes) if (P.famille === "desaccordG" && P.actif === a && P.start === mk.start) { try { this.dGerer(P, pu); } catch (_) {} }
    // ---- 2. fin de cycle : acheter 0,70-0,90 quand le modèle est très sûr, garder jusqu'à la fin
    const F = NV.ACTIVES.includes("fin") ? NV.FIN[a] : null;
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
        try { this.nTenter(P.strat, a, mk, up, P.strat === "fin" ? NV.FIN[a].HI : ask[0] + 0.01, r.cout, fair); } catch (_) {}
        try { this.nInverse(P.strat, a, mk, up, r.cout); } catch (_) {}
        try { if (P.famille === "desaccord") { P.type = this.dType(a, up, tleft, ask[0]); this.dCopies(P, ecart, a, mk, up, r); } } catch (err) { this.erreur("désaccord copies", err); }
        this.nSauver();
        break;
      }
    }
    if (!NV.TRADE.includes(a)) {                                        // ETH : enregistrement + cohorte « corrigé » seulement (09.10.2026)
      if ((NV.CORRIGE_ACTIFS || []).includes(a)) { try { this.dV2(a, mk, pu, tleft, true); } catch (err) { this.erreur("corrigé " + a, err); } }
      return;
    }
    try { this.dV2(a, mk, pu, tleft); } catch (err) { this.erreur("désaccord V2", err); }
    try { this.dConfirme(a, mk, pu, tleft); } catch (err) { this.erreur("désaccord confirmé", err); }
    // ---- 4. désaccord : le modèle donne au moins X de plus que le meilleur vendeur → achat, une fois par cycle et par variante
    if (tleft >= NV.DESACCORD.TMIN && !NV.DESACCORD.ARRETES) { try { this.dNouvelles(a, mk, pu, tleft); } catch (err) { this.erreur("désaccords nouveaux", err); } }
    if (tleft >= NV.DESACCORD.TMIN) for (const [nom, ecart] of Object.entries(NV.DESACCORD.VARIANTES)) {
      if (!NV.ACTIVES.includes(nom)) continue;
      if (this.N.ouvertes.some((P) => P.strat === nom && P.actif === a && P.start === mk.start) || ((this._dsF || {})[nom + a] === mk.start)) continue;
      const nuit = (NV.DESACCORD.NUIT || {})[nom];
      if (nuit) { const hz = +new Intl.DateTimeFormat("en-GB", { timeZone: "Europe/Zurich", hour: "2-digit", hour12: false }).format(new Date()) % 24; if (hz >= nuit[0] && hz < nuit[1]) continue; }
      for (const up of [true, false]) {
        const id = up ? mk.up : mk.down, ask = this.livreTrie(id, "asks")[0], fair = up ? pu : 1 - pu;
        if (!ask || ask[0] < 0.03 || ask[0] > 0.97 || fair - ask[0] < ecart) continue;
        const r = this.nAcheter(id, NV.DESACCORD.MISE / ask[0], ask[0] + 0.01);
        if (r.parts < 1) continue;
        (this._dsF = this._dsF || {})[nom + a] = mk.start;
        const P = this.nPos(nom, a, mk, { famille: "desaccord", cote: up ? "Up" : "Down", prix: +(r.cout / r.parts).toFixed(4), parts: +r.parts.toFixed(2), proba0: +fair.toFixed(3), restant_s: +tleft.toFixed(0) });
        P.cash = -r.cout; if (up) P.U = r.parts; else P.D = r.parts;
        this.nNote(P, `achat ${P.cote} ${r.parts.toFixed(1)} parts à ${P.prix} (modèle ${P.proba0}, ${P.restant_s} s restantes)`);
        try { this.nTenter(P.strat, a, mk, up, P.strat === "fin" ? NV.FIN[a].HI : ask[0] + 0.01, r.cout, fair); } catch (_) {}
        try { this.nInverse(P.strat, a, mk, up, r.cout); } catch (_) {}
        try { if (P.famille === "desaccord") { P.type = this.dType(a, up, tleft, ask[0]); this.dCopies(P, ecart, a, mk, up, r); } } catch (err) { this.erreur("désaccord copies", err); }
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
    try { this.dMakerEchange(id, side, p, size); } catch (_) {}
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
        try {
          const jid = cle === "U" ? q.up : q.down, nomS = nom + " " + a;
          const mid = () => { const b = this.livreTrie(jid, "bids")[0], x = this.livreTrie(jid, "asks")[0]; return b && x ? (b[0] + x[0]) / 2 : null; };
          const MK = ((this.N.markout = this.N.markout || {})[nomS] = this.N.markout[nomS] || { n: 0, "0.1s": 0, "0.5s": 0, "1s": 0, "3s": 0, "10s": 0, nOk: { "0.1s": 0, "0.5s": 0, "1s": 0, "3s": 0, "10s": 0 } });
          MK.n++;
          for (const [lab, ms] of [["0.1s", 100], ["0.5s", 500], ["1s", 1000], ["3s", 3000], ["10s", 10000]]) setTimeout(() => { const v = mid(); if (v != null) { MK[lab] += (v - bid) * k; MK.nOk[lab] += k; } }, ms);
        } catch (_) {}
        this.nNote(P, `achat ${cle === "U" ? "Up" : "Down"} ${k.toFixed(1)} à ${bid}`); this.nSauver();
      }
    }
  }

  // ================= désaccords : type de configuration + gestions après l'entrée
  // Type = temps restant × prix acheté × sens du perp (5 s) × sens du marché Polymarket (10 s) par rapport à notre côté
  dType(a, up, tleft, ask) {
    const T2 = tleft > 240 ? "début (>4 min)" : tleft > 120 ? "milieu" : "fin (<2 min)";
    const Pz = ask < 0.3 ? "bon marché (<0,30)" : ask < 0.5 ? "0,30-0,50" : "cher (>0,50)";
    const el = this.elanV1(a), perp = el == null ? "perp ?" : (el * (up ? 1 : -1) > 0 ? "perp avec nous" : "perp contre nous");
    const R = ((this._rec || {})[a] || {}).lignes || [], n = R.length;
    let mkt = "marché ?";
    if (n > 40) { const m0 = R[n - 41], m1 = R[n - 1], mid = (r) => (r[3] != null && r[4] != null ? (r[3] + r[4]) / 2 : null); const a0 = mid(m0), a1 = mid(m1);
      if (a0 != null && a1 != null) { const d = (a1 - a0) * (up ? 1 : -1); mkt = d > 0.02 ? "marché vers nous" : d < -0.02 ? "marché contre nous" : "marché stable"; } }
    const ac = this.dAutre(a, up), autreC = ac == null ? "autre crypto ?" : ac ? "autre crypto d'accord" : "autre crypto pas d'accord";
    return [T2, Pz, perp, mkt, autreC].join(" | ");
  }
  // valeur combinée marché + modèle (logit pondéré)
  dCombinee(a, tleft, fair, mid) {
    const L = (x) => { x = Math.min(Math.max(x, 0.005), 0.995); return Math.log(x / (1 - x)); };
    const w = NV.DESACCORD.POIDS[a].find((z) => tleft <= z[0]) || NV.DESACCORD.POIDS[a][2];
    return 1 / (1 + Math.exp(-(w[1] * L(mid) + w[2] * L(fair))));
  }
  // un désaccord dans le même sens sur l'autre crypto ? (+1 : oui, 0 : non, null : inconnu)
  dAutre(a, up) {
    const b2 = a === "BTC" ? "ETH" : "BTC", mk2 = this.mk[b2], pu2 = this._puA && this._puA[b2];
    if (!mk2 || !mk2.up || pu2 == null) return null;
    const id2 = up ? mk2.up : mk2.down, k2 = this.livreTrie(id2, "asks")[0];
    if (!k2) return null;
    return ((up ? pu2 : 1 - pu2) - k2[0] >= NV.DESACCORD.CROISE.autre) ? 1 : 0;
  }
  // entrée taker générique pour les nouvelles variantes
  dEntrer(nom, a, mk, up, tleft, fair, ask, ecart, gestions, extra) {
    const id = up ? mk.up : mk.down;
    const r = this.nAcheter(id, NV.DESACCORD.MISE / ask, ask + 0.01);
    if (r.parts < 1) return false;
    (this._dsF = this._dsF || {})[nom + a] = mk.start;
    const P = this.nPos(nom, a, mk, { famille: "desaccord", cote: up ? "Up" : "Down", prix: +(r.cout / r.parts).toFixed(4), parts: +r.parts.toFixed(2), proba0: +fair.toFixed(3), restant_s: +tleft.toFixed(0), ...(extra || {}) });
    P.cash = -r.cout; if (up) P.U = r.parts; else P.D = r.parts;
    this.nNote(P, `achat ${P.cote} ${r.parts.toFixed(1)} parts à ${P.prix} (modèle ${P.proba0}${extra && extra.combinee != null ? ", combinée " + extra.combinee : ""}, ${P.restant_s} s)`);
    try { this.nTenter(nom, a, mk, up, ask + 0.01, r.cout, fair); } catch (_) {}
    P.type = this.dType(a, up, tleft, ask);
    this.dCopies(P, ecart, a, mk, up, r, gestions);
    this.nSauver();
    return true;
  }
  dNouvelles(a, mk, pu, tleft) {
    const deja = (nom) => this.N.ouvertes.some((P) => P.strat === nom && P.actif === a && P.start === mk.start) || ((this._dsF || {})[nom + a] === mk.start);
    for (const up of [true, false]) {
      const id = up ? mk.up : mk.down, k = this.livreTrie(id, "asks")[0], b = this.livreTrie(id, "bids")[0], fair = up ? pu : 1 - pu;
      if (!k || !b || k[0] < 0.03 || k[0] > 0.97) continue;
      const mid = (k[0] + b[0]) / 2;
      // valeur combinée marché + modèle
      const comb = this.dCombinee(a, tleft, fair, mid);
      for (const [nom, seuil] of Object.entries(NV.DESACCORD.COMBINE))
        if (!deja(nom) && comb - k[0] >= seuil) this.dEntrer(nom, a, mk, up, tleft, fair, k[0], seuil, NV.DESACCORD.GESTIONS_NOUVELLES, { combinee: +comb.toFixed(3) });
      // confirmation croisée : désaccord ici ET dans le même sens sur l'autre crypto
      const C = NV.DESACCORD.CROISE;
      if (!deja(C.nom) && fair - k[0] >= C.ecart && this.dAutre(a, up) === 1) this.dEntrer(C.nom, a, mk, up, tleft, fair, k[0], C.ecart, NV.DESACCORD.GESTIONS_NOUVELLES, { croise: true });
    }
    // maker : offre d'achat sous la valeur du modèle, retirée si l'avantage fond ou après 30 s
    const MK = NV.DESACCORD.MAKER, cle = MK.nom + a, Q = (this._mkQ = this._mkQ || {});
    if (Q[cle] && Q[cle].start !== mk.start) delete Q[cle];
    if (deja(MK.nom)) return;
    if (Q[cle]) {
      const q = Q[cle], fair = q.up ? pu : 1 - pu;
      if (fair - q.bid < MK.retrait || now() - q.posee > MK.duree_s) { delete Q[cle]; (this._mkFait = this._mkFait || {})[cle] = (this._mkFait[cle] || 0) + 1; }
      else q.fair = fair;
      return;
    }
    for (const up of [true, false]) {
      const id = up ? mk.up : mk.down, k = this.livreTrie(id, "asks")[0], b = this.livreTrie(id, "bids")[0], fair = up ? pu : 1 - pu;
      if (!k || !b || k[0] < 0.03 || k[0] > 0.97 || fair - k[0] < MK.ecart) continue;
      const bid = Math.min(+(b[0] + 0.01).toFixed(2), +(k[0] - 0.01).toFixed(2), Math.floor((fair - 0.06) * 100) / 100);
      if (bid < 0.02) continue;
      Q[cle] = { start: mk.start, up, id, bid, ameliore: bid > b[0] + 1e-9, posee: now(), fair, parts: 0, cout: 0, tleft };
      return;
    }
  }
  // remplissage de l'offre maker (prudent : un vendeur passe sous notre prix, ou à notre prix si nous étions seuls au meilleur prix)
  dMakerEchange(id, side, p, size) {
    const MK = NV.DESACCORD.MAKER;
    for (const a of V1.ACTIFS) {
      const cle = MK.nom + a, q = (this._mkQ || {})[cle]; if (!q || q.id !== id || side !== "SELL") continue;
      if (!(p < q.bid - 1e-9 || (q.ameliore && Math.abs(p - q.bid) < 1e-9))) continue;
      const mk = this.mk[a]; if (!mk || mk.start !== q.start) continue;
      const voulu = NV.DESACCORD.MISE / q.bid - q.parts, k2 = Math.min(size, voulu);
      if (k2 <= 0) continue;
      q.parts += k2; q.cout += k2 * q.bid;
      if (q.parts >= NV.DESACCORD.MISE / q.bid - 1e-6) {
        delete this._mkQ[cle]; (this._dsF = this._dsF || {})[cle] = mk.start;
        const tleft = mk.end - now();
        const P = this.nPos(MK.nom, a, mk, { famille: "desaccord", cote: q.up ? "Up" : "Down", prix: q.bid, parts: +q.parts.toFixed(2), proba0: +q.fair.toFixed(3), restant_s: +tleft.toFixed(0) });
        P.cash = -q.cout; if (q.up) P.U = q.parts; else P.D = q.parts;
        this.nNote(P, `offre maker servie : ${q.parts.toFixed(1)} parts à ${q.bid} (sans frais)`);
        P.type = this.dType(a, q.up, tleft, q.bid);
        this.dCopies(P, MK.ecart, a, mk, q.up, { parts: q.parts, cout: q.cout }, NV.DESACCORD.GESTIONS_NOUVELLES);
        this.nSauver();
      }
    }
  }
  // ---- moteur fantôme V2 (07.10.2026, paramètres FIGÉS avant toute mesure) : désaccord >= 0,20 + un filtre ou un veto, 50 $, gardé jusqu'à la fin.
  // QUI CONVERGE VERS QUI (07.10.2026, mesure seulement, aucun achat) : à chaque 1er désaccord >= 0,20 du cycle et du côté,
  // 1, 3 et 10 s plus tard : POLY REJOINT (milieu Poly +3 c vers le modèle, modèle stable) / MODÈLE RETOMBE (modèle -3 c, Poly stable) / LES DEUX / RIEN.
  blinkSuivre(a, mk, pu, tleft, ua, da, H) {
    const t = now(), L = this.BL.evts, last = H.r[H.r.length - 1]; if (!last) return;
    const fam = (df, dm) => { const p = dm >= 0.03, m = df <= -0.03; return p && m ? "LES DEUX" : p ? "POLY REJOINT" : m ? "MODELE RETOMBE" : "RIEN"; };
    for (const e of L) {
      if (e.a !== a || e.st !== mk.start || e.f10) continue;
      const up = e.cote === "Up", fair = up ? pu : 1 - pu, mid = up ? last.um : last.dm;
      for (const h of [1, 3, 10]) if (!e["f" + h] && t - e.t0 >= h) {
        e["f" + h] = fam(fair - e.fair0, mid - e.mid0);
        if (h === 3) e.ask3 = up ? ua[0] : da[0];
        if (h === 10 && e["f10"] !== "POLY REJOINT") for (const P of this.N.ouvertes.filter((x) => x.actif === a && x.start === mk.start && x.cote === e.cote && x.strat.startsWith("desaccord 20 aucune bourse contre"))) {
          const parts = e.cote === "Up" ? P.U : P.D; if (!(parts > 0)) continue;
          const v = this.nVendre(e.cote === "Up" ? mk.up : mk.down, parts); if (v.vendu <= 0) continue;
          P.cash += v.recu; if (e.cote === "Up") P.U -= v.vendu; else P.D -= v.vendu;
          this.nNote(P, `10 s après : Polymarket n'a pas rejoint le modèle (${e.f10}) → revente de ${v.vendu.toFixed(1)} parts pour ${v.recu.toFixed(2)} $`); this.nSauver();
        }
        if (h !== 1 && e["f" + h] === "POLY REJOINT" && tleft >= 3) this.blinkAcheter(a, mk, e, h, up ? mk.up : mk.down, up ? ua : da, fair, tleft);
        this.blkSauver();
      }
    }
    if (tleft < 12) return;
    for (const up of [true, false]) {
      const k = up ? ua : da, fair = up ? pu : 1 - pu, cote = up ? "Up" : "Down";
      if (k[0] < 0.03 || k[0] > 0.97 || fair - k[0] < 0.20) continue;
      if (L.some((e) => e.a === a && e.st === mk.start && e.cote === cote)) continue;
      let h3 = null; for (let i = H.r.length - 1; i >= 0; i--) if (t - H.r[i].t >= 3) { h3 = H.r[i]; break; }
      const sg = up ? 1 : -1, d = (src) => (h3 && h3[src] && last[src] ? +((last[src] - h3[src]) / h3[src] * 1e4 * sg).toFixed(2) : null);
      L.push({ a, st: mk.start, slug: mk.slug, cote, t0: +t.toFixed(2), reste: Math.round(tleft), ask: k[0], fair0: +fair.toFixed(3), mid0: up ? last.um : last.dm,
        bn3: d("bn"), perp3: d("perp"), okx3: d("okx"), cb3: d("cb"), mkt3: h3 ? +((up ? last.um - h3.um : last.dm - h3.dm)).toFixed(3) : null });
      while (L.length > 350) L.shift();
      try { this.filtreBourses(a, mk, L[L.length - 1], up ? mk.up : mk.down, k, fair, tleft); } catch (err) { this.erreur("filtre bourses", err); }
      this.blkSauver();
    }
  }
  // fantômes du 07.10.2026 (figés) : désaccord 20, attendre 3 s ou 10 s, acheter 50 $ au meilleur vendeur SEULEMENT si Polymarket a rejoint le modèle ; variantes sans la nuit (00h-08h suisse)
  blinkAcheter(a, mk, e, h, id, k, fair, tleft) {
    const hz = +new Intl.DateTimeFormat("en-GB", { timeZone: "Europe/Zurich", hour: "2-digit", hour12: false }).format(new Date()) % 24;
    for (const nom of [`desaccord 20 Poly rejoint ${h} s`, `desaccord 20 Poly rejoint ${h} s sans nuit`]) {
      if (!NV.ACTIVES.includes(nom) || (nom.endsWith("sans nuit") && hz < 8)) continue;
      if (k[0] < 0.03 || k[0] > 0.97) continue;
      if (this.N.ouvertes.some((P) => P.strat === nom && P.actif === a && P.start === mk.start)) continue;
      const r = this.nAcheter(id, 50 / k[0], k[0] + 0.01); if (r.parts < 1) continue;
      const P = this.nPos(nom, a, mk, { famille: "desaccord", cote: e.cote, prix: +(r.cout / r.parts).toFixed(4), parts: +r.parts.toFixed(2), proba0: +fair.toFixed(3), restant_s: +tleft.toFixed(0) });
      P.cash = -r.cout; if (e.cote === "Up") P.U = r.parts; else P.D = r.parts;
      this.nNote(P, `désaccord 20 vu à ${e.ask} (modèle ${e.fair0}) ; ${h} s plus tard Polymarket a rejoint le modèle → achat à ${P.prix}, ${tleft.toFixed(0)} s restantes`);
      this.nSauver();
    }
  }
  // fantômes du 07.10.2026 soir (figés) : désaccord 20 + bourses dans notre sens sur les 3 s AVANT l'entrée, achat immédiat 50 $ ; variantes sans la nuit
  filtreBourses(a, mk, e, id, k, fair, tleft) {
    const hz = +new Intl.DateTimeFormat("en-GB", { timeZone: "Europe/Zurich", hour: "2-digit", hour12: false }).format(new Date()) % 24;
    const v = (x) => x || 0, bn = v(e.bn3), pe = v(e.perp3);
    const R = { "desaccord 20 Binance avec nous": bn > 0, "desaccord 20 Binance ou perp avec nous": bn > 0 || pe > 0,
      "desaccord 20 aucune bourse contre + sortie 10 s": Math.min(bn, pe, v(e.okx3), v(e.cb3)) >= 0 };
    for (const [base, ok] of Object.entries(R)) for (const nom of [base, base + " sans nuit"]) {
      if (!ok || !NV.ACTIVES.includes(nom) || (nom.endsWith("sans nuit") && hz < 8)) continue;
      if (this.N.ouvertes.some((P) => P.strat === nom && P.actif === a && P.start === mk.start)) continue;
      const r = this.nAcheter(id, 50 / k[0], k[0] + 0.01); if (r.parts < 1) continue;
      const P = this.nPos(nom, a, mk, { famille: "desaccord", cote: e.cote, prix: +(r.cout / r.parts).toFixed(4), parts: +r.parts.toFixed(2), proba0: +fair.toFixed(3), restant_s: +tleft.toFixed(0) });
      P.cash = -r.cout; if (e.cote === "Up") P.U = r.parts; else P.D = r.parts;
      this.nNote(P, `désaccord 20 (modèle ${e.fair0}, vendeur ${e.ask}) ; 3 s avant : Binance ${e.bn3} pb, perp ${e.perp3} pb, OKX ${e.okx3} pb, Coinbase ${e.cb3} pb (+ = dans notre sens) → achat à ${P.prix}`);
      this.nSauver();
    }
  }
  blkSauver() {
    if (this._bsv) return;
    this._bsv = setTimeout(() => { this._bsv = null; this.state.storage.put("blink", this.BL).catch((err) => this.erreur("sauvegarde blink", err)); }, 2000);
  }
  async blkRegler() {
    const t = now(), cache = {}, fee = (p) => 0.072 * p * (1 - p);
    let ch = false;
    for (const e of this.BL.evts) {
      if (e.g != null || t < e.st + 320 || !e.slug) continue;
      try {
        if (!(e.slug in cache)) {
          const ev = await (await fetch(`${G}/events?slug=${e.slug}`)).json();
          const m = ev[0].markets[0], px = JSON.parse(m.outcomePrices || "[]").map(Number), outs = JSON.parse(m.outcomes || "[]");
          cache[e.slug] = (px.includes(1) && px.includes(0)) ? String(outs[px.indexOf(1)]) : null;
        }
        const w = cache[e.slug]; if (!w) continue;
        e.g = w === e.cote ? 1 : 0;
        e.pnl = +((50 / e.ask) * (e.g - e.ask - fee(e.ask))).toFixed(2);
        if (e.ask3 && e.ask3 >= 0.03 && e.ask3 <= 0.97) e.pnl3 = +((50 / e.ask3) * (e.g - e.ask3 - fee(e.ask3))).toFixed(2);
        ch = true;
      } catch (_) {}
    }
    if (ch) this.blkSauver();
  }
  blkVue() {
    const E = this.BL.evts.filter((e) => e.g != null), FAM = ["POLY REJOINT", "MODELE RETOMBE", "LES DEUX", "RIEN"], r2 = (x) => +x.toFixed(0);
    const res = (X) => ({ n: X.length, g: X.filter((e) => e.g).length, pnl: r2(X.reduce((s2, e) => s2 + e.pnl, 0)) });
    const parH = {};
    for (const h of [1, 3, 10]) {
      const X = E.filter((e) => e["f" + h]);
      parH[h] = { tous: res(X), fam: Object.fromEntries(FAM.map((f) => [f, res(X.filter((e) => e["f" + h] === f))])) };
    }
    const PR = E.filter((e) => e.f3 === "POLY REJOINT" && e.pnl3 != null);
    const sens = {};
    for (const [nom, k] of [["Binance", "bn3"], ["Bybit perp", "perp3"], ["OKX", "okx3"], ["Coinbase", "cb3"], ["Polymarket", "mkt3"]]) {
      sens[nom] = {};
      for (const [s2, fl] of [["contre nous", (v) => v < 0], ["neutre", (v) => v === 0], ["avec nous", (v) => v > 0]]) {
        const X = E.filter((e) => e.f3 && e[k] != null && fl(e[k]));
        sens[nom][s2] = { ...res(X), pr: X.filter((e) => e.f3 === "POLY REJOINT").length, mr: X.filter((e) => e.f3 === "MODELE RETOMBE").length };
      }
    }
    return { depuis: this.BL.depuis, n: this.BL.evts.length, regles: E.length, parH, attendre3: { n: PR.length, g: PR.filter((e) => e.g).length, pnl: r2(PR.reduce((s2, e) => s2 + e.pnl3, 0)) }, sens };
  }

  // COHORTE « MODÈLE CORRIGÉ » (09.10.2026, figée) : mêmes règles que les meilleures stratégies, mais avec la probabilité corrigée (marge 0,015 %).
  dCorrige(a, mk, tleft, ua, da, H, px) {
    const last = H.r[H.r.length - 1]; if (!last || last.pu2 == null) return;
    const t = now(), pu2 = last.pu2;
    const ilya = (sec) => { for (let i = H.r.length - 1; i >= 0; i--) if (t - H.r[i].t >= sec) return H.r[i]; return null; };
    // carnet complet (8 niveaux de vendeurs) à l'achat puis 1, 3 et 10 s après — enregistrement seulement (09.10.2026)
    const niveaux = (idv) => this.livreTrie(idv, "asks").slice(0, 8).map(([p, z]) => [p, Math.round(z)]);
    for (const P of this.N.ouvertes) {
      if (P.actif !== a || P.start !== mk.start || !P.carnet || !P.t0) continue;
      for (const d of [1, 3, 10]) if (!P.carnet[d] && t - P.t0 >= d) P.carnet[d] = niveaux(P.cote === "Up" ? mk.up : mk.down);
    }
    // sortie -10 sur le modèle corrigé (avec plancher)
    for (const P of this.N.ouvertes) {
      if (P.actif !== a || P.start !== mk.start || !P.strat.startsWith("corrige :") || !P.strat.includes("sortie -10")) continue;
      const parts = P.cote === "Up" ? P.U : P.D; if (!(parts > 0)) continue;
      const fair = P.cote === "Up" ? pu2 : 1 - pu2; if (fair > P.proba0 - 0.10) continue;
      const idv = P.cote === "Up" ? mk.up : mk.down, B = this.livreTrie(idv, "bids"); if (!B.length) continue;
      const plancher = Math.max(0.05, B[0][0] - 0.02); let reste = parts, recu = 0;
      for (const [pb, sz] of B) { if (pb < plancher) break; const q2 = Math.min(sz, reste); recu += q2 * pb - q2 * CFG.FEE_RATE * pb * (1 - pb); reste -= q2; if (reste <= 1e-9) break; }
      if (parts - reste <= 1e-9) continue;
      P.cash += recu; if (P.cote === "Up") P.U = reste; else P.D = reste;
      this.nNote(P, `modèle corrigé passé de ${P.proba0} à ${fair.toFixed(3)} → revente de ${(parts - reste).toFixed(1)} parts pour ${recu.toFixed(2)} $`); this.nSauver();
    }
    // ---- TWAP FIN (09.10.2026) : moteur de règlement (moyennes Chainlink 60 s, prix à battre reconstruit), achat si moteur − prix ≥ 0,20
    // entre 90 et 20 s de la fin ; 50 $ au meilleur vendeur seulement (quantité affichée) ; un achat par cycle ; gardé jusqu'au règlement. BTC.
    if (a === "BTC" && mk.twapK && tleft <= 90 && tleft >= 20 && !H.fait["TWAP fin"] && NV.ACTIVES.includes("TWAP fin")) {
      let p4 = null; try { p4 = this.probaV1(a, mk, 0.5 / (this.prixRapide(a) || 1e9)); } catch (_) {}
      if (p4 != null) for (const up of [true, false]) {
        const k = up ? ua : da, fair = up ? p4 : 1 - p4;
        if (!k || k[0] < 0.02 || k[0] > 0.98 || fair - k[0] < 0.20) continue;
        const r = this.nAcheter(up ? mk.up : mk.down, 50 / k[0], k[0]); if (r.parts < 1) continue;
        H.fait["TWAP fin"] = true;
        const B0 = ((this._clBrut || {})[a] || []).slice(-1)[0] || [];
        const P = this.nPos("TWAP fin", a, mk, { famille: "twap", cote: up ? "Up" : "Down", prix: +(r.cout / r.parts).toFixed(4), parts: +r.parts.toFixed(2), proba0: +fair.toFixed(3), restant_s: +tleft.toFixed(0),
          tAchat: +now().toFixed(3), tailleAffichee: k[1], prixABattre: +mk.strike.toFixed(2), clObs: B0[0] ?? null, clRecu: B0[2] ?? null, clDernier: B0[3] ?? null, btc: +(this.prixRapide(a) || 0).toFixed(2) });
        P.cash = -r.cout; if (up) P.U = r.parts; else P.D = r.parts;
        this.nNote(P, `moteur TWAP ${fair.toFixed(3)}, vendeur ${k[0]}, ${tleft.toFixed(0)} s restantes → achat ${P.cote} ${r.parts.toFixed(1)} parts`);
        this.nSauver(); break;
      }
    }
    if (tleft < 5) return;
    const h3 = ilya(3);
    for (const up of [true, false]) {
      const k = up ? ua : da, fair = up ? pu2 : 1 - pu2, edge = fair - k[0], sg = up ? 1 : -1;
      if (k[0] < 0.03 || k[0] > 0.97) continue;
      const e3 = h3 && h3.pu2 != null ? (up ? h3.pu2 - h3.ua : (1 - h3.pu2) - h3.da) : null;
      const grandit = e3 != null && edge - e3 >= 0.03;
      const dmo = h3 && h3.pu2 != null ? fair - (up ? h3.pu2 : 1 - h3.pu2) : 0, dpo = h3 ? k[0] - (up ? h3.ua : h3.da) : 0;
      const deuxBaissent = !!h3 && dmo < 0 && dpo < dmo && !(Math.abs(dmo) < 0.02 && dpo <= -0.02);
      const dz = (src) => (h3 && h3[src] && last[src] ? (last[src] - h3[src]) * sg : 0);
      // garde-fou (09.10.2026) : pas d'achat si le BTC est à moins de 20 $ (ETH 1 $) du prix à battre ET si notre côté est à 5 c ou moins
      const Sx = this.prixRapide(a), dist = Sx != null && mk.strike ? Math.abs(Sx - mk.strike) : null;
      const garde = !(dist != null && dist < (a === "ETH" ? 1 : 20) && k[0] <= 0.05);
      // marge mesurée : même règle V2-F avec la probabilité calculée sur l'erreur mesurée
      const pu3 = last.pu3, f3m = pu3 == null ? null : (up ? pu3 : 1 - pu3), e3m = h3 && h3.pu3 != null ? (up ? h3.pu3 - h3.ua : (1 - h3.pu3) - h3.da) : null;
      const grandit3 = f3m != null && f3m - k[0] >= 0.20 && e3m != null && (f3m - k[0]) - e3m >= 0.03;
      const W = { "corrige : V2-F + garde-fou": grandit && garde, "corrige marge mesuree : V2-F": grandit3,
        "corrige : desaccord 20": true, "corrige : V2-F ecart qui grandit": grandit, "corrige : V2-F + pas les deux baissent": grandit && !deuxBaissent,
        "corrige : zone + Binance et perp + sortie -10": k[0] >= 0.15 && k[0] < 0.35 && edge >= 0.30 && tleft > 60 && dz("bn") >= 0 && dz("perp") >= 0 };
      for (const [nom, ok] of Object.entries(W)) {
        if (!ok || H.fait[nom] || !NV.ACTIVES.includes(nom)) continue;
        if (nom !== "corrige marge mesuree : V2-F" && edge < 0.20) continue;
        const r = this.nAcheter(up ? mk.up : mk.down, 50 / k[0], k[0] + 0.01); if (r.parts < 1) continue;
        H.fait[nom] = true;
        const P = this.nPos(nom, a, mk, { famille: "desaccord", cote: up ? "Up" : "Down", prix: +(r.cout / r.parts).toFixed(4), parts: +r.parts.toFixed(2), proba0: +(nom === "corrige marge mesuree : V2-F" ? f3m : fair).toFixed(3), restant_s: +tleft.toFixed(0) });
        P.cash = -r.cout; if (up) P.U = r.parts; else P.D = r.parts;
        P.t0 = t; P.carnet = { 0: niveaux(up ? mk.up : mk.down), achat: [+r.parts.toFixed(2), +r.cout.toFixed(2)] };
        this.nNote(P, `modèle corrigé ${fair.toFixed(3)} (ancien ${(up ? last.pu : 1 - last.pu).toFixed(3)}), vendeur ${k[0]}, écart ${edge.toFixed(2)}, ${tleft.toFixed(0)} s restantes → achat ${P.cote} ${r.parts.toFixed(1)} parts à ${P.prix}`);
        this.nSauver();
      }
    }
  }

  dV2(a, mk, pu, tleft, seulCorrige = false) {
    const t = now(), px = (src) => (this.f[a][src] ? +this.f[a][src].p : null);
    const ub = this.livreTrie(mk.up, "bids")[0], ua = this.livreTrie(mk.up, "asks")[0], db = this.livreTrie(mk.down, "bids")[0], da = this.livreTrie(mk.down, "asks")[0];
    if (!ub || !ua || !db || !da) return;
    const H = ((this._v2h = this._v2h || {})[a] = this._v2h[a] && this._v2h[a].start === mk.start ? this._v2h[a] : { start: mk.start, r: [], fait: {} });
    if (!H.r.length || t - H.r[H.r.length - 1].t >= 0.25) {
      let pu2 = null; try { pu2 = this.probaV1(a, mk, CFG.SD_CORRIGE); } catch (_) {}
      let pu3 = null; try { const m$ = this.margeMesuree(a), S0 = this.prixRapide(a); if (m$ && S0) pu3 = this.probaV1(a, mk, m$ / S0); } catch (_) {}
      H.r.push({ t, pu, pu2, pu3, um: (ub[0] + ua[0]) / 2, dm: (db[0] + da[0]) / 2, ua: ua[0], da: da[0], perp: px("perp"), okx: px("okx"), bn: px("bn"), cb: px("cb") });
      while (H.r.length && t - H.r[0].t > 12) H.r.shift();
      // volatilité du perp sur 60 s (09.10.2026)
      const VRr = ((this._vr = this._vr || {})[a] = this._vr[a] || []);
      if (px("perp")) { VRr.push({ t, p: px("perp") }); while (VRr.length && t - VRr[0].t > 60) VRr.shift(); }
    }
    if (seulCorrige) { this.dCorrige(a, mk, tleft, ua, da, H, px); return; }
    try { this.blinkSuivre(a, mk, pu, tleft, ua, da, H); } catch (err) { this.erreur("qui converge", err); }
    try { this.dCorrige(a, mk, tleft, ua, da, H, px); } catch (err) { this.erreur("modèle corrigé", err); }
    // sortie « modèle -10 pts » (08.10.2026) : revente au meilleur acheteur si le modèle a perdu 10 pts depuis l'entrée
    for (const P of this.N.ouvertes) {
      if (P.actif !== a || P.start !== mk.start || !P.strat.includes("sortie modele -10")) continue;
      const parts = P.cote === "Up" ? P.U : P.D; if (!(parts > 0)) continue;
      const fair = P.cote === "Up" ? pu : 1 - pu;
      if (fair > P.proba0 - 0.10) continue;
      // plancher (08.10.2026, correction) : jamais sous 0,05 $ ni à plus de 2 c sous le meilleur acheteur ; sinon on garde jusqu'au résultat
      const idv = P.cote === "Up" ? mk.up : mk.down, B = this.livreTrie(idv, "bids"); if (!B.length) continue;
      const plancher = Math.max(0.05, B[0][0] - 0.02); let reste = parts, recu = 0;
      for (const [pb, sz] of B) { if (pb < plancher) break; const q2 = Math.min(sz, reste); recu += q2 * pb - q2 * CFG.FEE_RATE * pb * (1 - pb); reste -= q2; if (reste <= 1e-9) break; }
      const v = { vendu: parts - reste, recu }; if (v.vendu <= 1e-9) continue;
      P.cash += v.recu; if (P.cote === "Up") P.U -= v.vendu; else P.D -= v.vendu;
      this.nNote(P, `le modèle est passé de ${P.proba0} à ${fair.toFixed(3)} → revente de ${v.vendu.toFixed(1)} parts pour ${v.recu.toFixed(2)} $ (${tleft.toFixed(0)} s restantes)`); this.nSauver();
    }
    if (tleft < 5) return;
    try { this.leadPhoto(a, mk, pu, tleft, ua, da); } catch (_) {}
    const il_y_a = (sec) => { for (let i = H.r.length - 1; i >= 0; i--) if (t - H.r[i].t >= sec) return H.r[i]; return null; };
    // V5 / V6 (07.10.2026, figés) : gain attendu par dollar au prix EXÉCUTABLE pour 50 $ (carnet jusqu'à +5 c), au lieu d'un écart fixe.
    // V5 : gain attendu >= +50 % par dollar et modèle >= prix + 5 c. V6 loterie : prix exécutable <= 0,10 et modèle >= 2 × prix.
    for (const up of [true, false]) {
      const id = up ? mk.up : mk.down, k = up ? ua : da, fair = up ? pu : 1 - pu;
      if (k[0] < 0.02 || k[0] > 0.90) continue;
      const r = this.nAcheter(id, 50 / k[0], k[0] + 0.05); if (r.parts < 5) continue;
      const vwap = r.cout / r.parts, gain = fair / vwap - 1;
      const W = { "V5 gain attendu": gain >= 0.5 && fair - vwap >= 0.05, "V6 loterie": vwap <= 0.10 && fair >= 2 * vwap };
      for (const [nom, ok] of Object.entries(W)) {
        if (!ok || H.fait[nom] || !NV.ACTIVES.includes(nom)) continue;
        H.fait[nom] = true;
        const P = this.nPos(nom, a, mk, { famille: "desaccord", cote: up ? "Up" : "Down", prix: +vwap.toFixed(4), parts: +r.parts.toFixed(2), proba0: +fair.toFixed(3), restant_s: +tleft.toFixed(0) });
        P.cash = -r.cout; if (up) P.U = r.parts; else P.D = r.parts;
        this.nNote(P, `prix exécutable ${vwap.toFixed(3)} pour ${r.cout.toFixed(0)} $, modèle ${fair.toFixed(3)}, gain attendu ${(100 * gain).toFixed(0)} % par $, ${tleft.toFixed(0)} s restantes`);
        this.nSauver();
      }
    }
    // ZONE (08.10.2026, figés) : écart >= 30 pts, jeton entre 0,15 et 0,35, plus de 60 s restantes ; variante + Binance et perp >= 0 sur 3 s
    if (tleft > 60) for (const up of [true, false]) {
      const k = up ? ua : da, fair = up ? pu : 1 - pu, sg = up ? 1 : -1;
      if (k[0] < 0.15 || k[0] >= 0.60 || fair - k[0] < 0.30) continue;
      const h3 = il_y_a(3), last = H.r[H.r.length - 1], dz = (src) => (h3 && h3[src] && last[src] ? (last[src] - h3[src]) * sg : 0);
      const zone = k[0] < 0.35, bp = dz("bn") >= 0 && dz("perp") >= 0;
      const grandit = h3 ? (fair - k[0]) - (up ? h3.pu - h3.ua : (1 - h3.pu) - h3.da) > 0 : false;
      const W = { "desaccord 30 zone 0,15-0,35": zone, "desaccord 30 zone 0,15-0,35 + Binance et perp": zone && bp,
        "desaccord 30 zone + sortie modele -10": zone, "desaccord 30 zone + Binance et perp + sortie modele -10": zone && bp,
        "desaccord 30 0,15-0,60 + perp + ecart qui grandit": dz("perp") >= 0 && grandit,
        "desaccord 30 zone + modele monte": zone && !!h3 && fair - (up ? h3.pu : 1 - h3.pu) >= 0.03,
        "desaccord 30 zone + Binance et perp + sortie modele -10 + pas Poly qui baisse": zone && bp && !(h3 && (k[0] - (up ? h3.ua : h3.da)) <= -0.03 && fair - (up ? h3.pu : 1 - h3.pu) < 0.03),
        "desaccord 30 zone + Binance et perp + sortie modele -10 + pas Poly qui baisse + taille 25/50": zone && bp && !(h3 && (k[0] - (up ? h3.ua : h3.da)) <= -0.03 && fair - (up ? h3.pu : 1 - h3.pu) < 0.03) };
      const modeleMonte = !!h3 && fair - (up ? h3.pu : 1 - h3.pu) >= 0.03;
      for (const [nom, ok] of Object.entries(W)) {
        if (!ok || H.fait[nom] || !NV.ACTIVES.includes(nom)) continue;
        const mise = nom.endsWith("taille 25/50") && !modeleMonte ? 25 : 50;
        const id = up ? mk.up : mk.down, r = this.nAcheter(id, mise / k[0], k[0] + 0.01); if (r.parts < 1) continue;
        H.fait[nom] = true;
        const P = this.nPos(nom, a, mk, { famille: "desaccord", cote: up ? "Up" : "Down", prix: +(r.cout / r.parts).toFixed(4), parts: +r.parts.toFixed(2), proba0: +fair.toFixed(3), restant_s: +tleft.toFixed(0) });
        P.cash = -r.cout; if (up) P.U = r.parts; else P.D = r.parts;
        this.nNote(P, `écart ${(fair - k[0]).toFixed(2)} (modèle ${fair.toFixed(3)}, vendeur ${k[0]}), ${tleft.toFixed(0)} s restantes ; 3 s avant : Binance ${dz("bn").toFixed(1)}, perp ${dz("perp").toFixed(1)} (+ = dans notre sens)`);
        this.nSauver();
      }
    }
    for (const up of [true, false]) {
      const k = up ? ua : da, fair = up ? pu : 1 - pu, edge = fair - k[0], sg = up ? 1 : -1;
      if (k[0] < 0.03 || k[0] > 0.97 || edge < 0.20) continue;
      const edgeDe = (x) => (up ? x.pu - x.ua : (1 - x.pu) - x.da), midDe = (x) => (up ? x.um : x.dm);
      const h3 = il_y_a(3), h5 = il_y_a(5);
      const dir = (src, ago) => { const x = il_y_a(ago); return x && x[src] && px(src) ? (px(src) - x[src]) * sg : null; };
      const perp5 = dir("perp", 5);
      const recents = H.r.filter((x) => t - x.t <= 1.5);
      const persistant = recents.length >= 4 && recents.every((x) => edgeDe(x) >= 0.20) && t - H.r[0].t >= 1.5;
      const grandit = h3 ? edge - edgeDe(h3) >= 0.03 : false;
      const dmo = h3 ? fair - (up ? h3.pu : 1 - h3.pu) : 0, dpo = h3 ? k[0] - (up ? h3.ua : h3.da) : 0;
      const deuxBaissent = !!h3 && dmo < 0 && dpo < dmo && !(Math.abs(dmo) < 0.02 && dpo <= -0.02);
      const VR = (this._vr = this._vr || {})[a] || [];
      let vol60 = null; if (VR.length > 20) { const d = []; for (let q = 1; q < VR.length; q++) d.push(VR[q].p - VR[q - 1].p); const m = d.reduce((x, y) => x + y, 0) / d.length; vol60 = Math.sqrt(d.reduce((x, y) => x + (y - m) ** 2, 0) / d.length) * 2; }
      const d3 = ["perp", "okx", "bn", "cb"].map((src) => dir(src, 3));
      const jury = d3.every((v) => v != null && v >= 0) && d3.some((v) => v > 0) && h3 && (fair - (up ? h3.pu : 1 - h3.pu)) - (midDe(H.r[H.r.length - 1]) - midDe(h3)) >= 0.03;
      const vetos = [
        h3 && edge - edgeDe(h3) < -0.02,                                   // l'écart fond
        (dir("bn", 3) ?? 0) < 0,                                          // Binance part contre nous
        (dir("perp", 3) ?? 0) < 0 && (dir("okx", 3) ?? 0) < 0,            // Bybit et OKX contre nous
        tleft >= 60 && tleft < 90,                                        // 60-89 s
        h5 && midDe(H.r[H.r.length - 1]) - midDe(h5) >= Math.max(0.05, edge / 2),   // Polymarket est déjà en train de corriger
        k[1] < 20];                                                       // vendeur trop mince (< 20 parts)
      const V = {
        "V2-B hors 60-89 s": !(tleft >= 60 && tleft < 90),
        "V2-C perp": perp5 != null && perp5 >= 0,
        "V2-D perp 120-269 s": perp5 != null && perp5 >= 0 && tleft >= 120 && tleft <= 269,
        "V2-E persistant": persistant,
        "V2-F ecart qui grandit": grandit,
        "V2-G jury des bourses": !!jury,
        "V2-H veto complet": !vetos.some(Boolean),
        // 09.10.2026 (figés) : V2-F sans « les deux baissent, Polymarket plus fort », et la même + volatilité perp >= 2 $/s sur 60 s
        "V2-F + pas les deux baissent": grandit && !deuxBaissent,
        "V2-F + pas les deux baissent + volatilite >= 2": grandit && !deuxBaissent && vol60 != null && vol60 >= 2,
        "V2-F + plus de 120 s": grandit && tleft >= 120 };
      for (const [nom, ok] of Object.entries(V)) {
        if (!ok || H.fait[nom] || !NV.ACTIVES.includes(nom)) continue;
        const r = this.nAcheter(up ? mk.up : mk.down, 50 / k[0], k[0] + 0.01); if (r.parts < 1) continue;
        H.fait[nom] = true;
        const P = this.nPos(nom, a, mk, { famille: "desaccord", cote: up ? "Up" : "Down", prix: +(r.cout / r.parts).toFixed(4), parts: +r.parts.toFixed(2), proba0: +fair.toFixed(3), restant_s: +tleft.toFixed(0) });
        P.cash = -r.cout; if (up) P.U = r.parts; else P.D = r.parts;
        this.nNote(P, `écart ${edge.toFixed(2)}, ${tleft.toFixed(0)} s restantes → achat ${P.cote} ${r.parts.toFixed(1)} parts à ${P.prix} (modèle ${fair.toFixed(3)})`);
        this.nSauver();
      }
    }
  }
  // ---- « qui a bougé en premier » (07.10.2026) : au 1er désaccord >= 0,20 du cycle, on sauve la boîte noire (10 s à 100 ms :
  // Bybit, OKX, Binance, Coinbase, Chainlink, carnet Bybit, flux, liquidations, carnets et retraits Polymarket), puis 10 s après.
  leadPhoto(a, mk, pu, tleft, ua, da) {
    const L = ((this._lead = this._lead || {})[a] = this._lead[a] && this._lead[a].start === mk.start ? this._lead[a] : { start: mk.start, fait: false });
    const sauver = (phase, extra) => {
      const R = (this.bbR || {})[a]; if (!R || !R.length) return;
      const t = now();
      this.state.storage.put("lead:" + Math.floor(t * 1000).toString().padStart(14, "0") + ":" + a + ":" + phase,
        { actif: a, start: mk.start, slug: mk.slug, phase, t: +t.toFixed(3), ...extra, colonnes: BB_COLONNES, lignes: R.slice() }).catch(() => {});
    };
    if (!L.fait) {
      for (const up of [true, false]) {
        const k = up ? ua : da, fair = up ? pu : 1 - pu;
        if (k[0] >= 0.03 && k[0] <= 0.97 && fair - k[0] >= 0.20) {
          L.fait = true; L.t = now(); L.info = { cote: up ? "Up" : "Down", ask: k[0], taille: k[1], modele: +fair.toFixed(4), ecart: +(fair - k[0]).toFixed(4), reste_s: +tleft.toFixed(1), strike: +mk.strike };
          sauver("avant", L.info); break;
        }
      }
    } else if (!L.apres && now() - L.t >= 10) { L.apres = true; sauver("apres", L.info); }
  }
  dConfirme(a, mk, pu, tleft) {
    const C = NV.CONFIRME, E = C.ECART[a]; if (!E || tleft < 5) return;
    const Z = ((this._dcf = this._dcf || {})[a] = this._dcf[a] && this._dcf[a].start === mk.start ? this._dcf[a] : { start: mk.start, det: {}, fait: {} });
    for (const up of [true, false]) {
      const id = up ? mk.up : mk.down, b = this.livreTrie(id, "bids")[0], k = this.livreTrie(id, "asks")[0], fair = up ? pu : 1 - pu;
      if (!b || !k) continue;
      const mid = (b[0] + k[0]) / 2, cle = up ? "U" : "D";
      if (!Z.det[cle]) { if (k[0] >= 0.03 && k[0] <= 0.97 && fair - k[0] >= E && tleft >= 25) Z.det[cle] = { t: now(), mid, perp: this.prixA(a, "perp", Math.floor(now())) }; continue; }
      const d = Z.det[cle]; if (d.fini || now() - d.t < C.ATTENTE_S) continue;
      d.fini = true;                                   // une seule décision, 20 s après la détection
      if (mid - d.mid < C.HAUSSE || fair - k[0] < C.AVANCE_MIN || k[0] > 0.97) continue;
      const p1 = this.prixA(a, "perp", Math.floor(now())), p0 = this.prixA(a, "perp", Math.floor(now()) - 5);
      const perpOk = p1 && p0 ? (p1 - p0) * (up ? 1 : -1) >= 0 : false;
      for (const nom of ["desaccord confirme", "desaccord confirme perp"]) {
        if (nom.endsWith("perp") && !perpOk) continue;
        if (Z.fait[nom] || !NV.ACTIVES.includes(nom)) continue;
        const r = this.nAcheter(id, C.MISE / k[0], k[0] + 0.01); if (r.parts < 1) continue;
        Z.fait[nom] = true;
        const P = this.nPos(nom, a, mk, { famille: "desaccord", cote: up ? "Up" : "Down", prix: +(r.cout / r.parts).toFixed(4), parts: +r.parts.toFixed(2), proba0: +fair.toFixed(3), restant_s: +tleft.toFixed(0) });
        P.cash = -r.cout; if (up) P.U = r.parts; else P.D = r.parts;
        this.nNote(P, `désaccord repéré à ${d.mid.toFixed(3)} il y a ${(now() - d.t).toFixed(0)} s, marché monté à ${mid.toFixed(3)} → achat ${P.cote} ${r.parts.toFixed(1)} parts à ${P.prix} (modèle ${fair.toFixed(3)})`);
        this.nSauver();
      }
    }
  }
  dCopies(P0, ecart, a, mk, up, r, gestions) {
    if (NV.DESACCORD.ARRETES) return;
    for (const g of (gestions || NV.DESACCORD.GESTIONS)) {
      const demi = g === "demi", parts = demi ? r.parts / 2 : r.parts, cout = demi ? r.cout / 2 : r.cout;
      const P = this.nPos(P0.strat + " +" + g, a, mk, { famille: "desaccordG", gestion: g, ecart, cote: P0.cote, prix: P0.prix, parts: +parts.toFixed(2), proba0: P0.proba0, restant_s: P0.restant_s,
        t0: now(), type: P0.type, etatSignal: "en attente", fini2: false, ajout: false });
      P.cash = -cout; if (up) P.U = parts; else P.D = parts;
      this.nNote(P, `entrée ${P.cote} ${parts.toFixed(1)} parts à ${P.prix} (${g})`);
    }
  }
  // états : CONFIRMÉ (le marché va vers nous), PAS DE SUITE (rien ne se passe), SIGNAL RATÉ (le marché va contre nous et le modèle lâche),
  // VRAI RETOURNEMENT (signal raté + le modèle voit maintenant un avantage de l'autre côté). Seul le vrai retournement autorise l'inversion.
  dGerer(P, pu) {
    if (P.fini2) return;
    if (Math.min(P.U, P.D) > 0 && Math.abs(P.U - P.D) < 1e-6 && P.gestion !== "verrou") { P.fini2 = true; return; }
    const up = P.cote === "Up", id = up ? P.up : P.down, autre = up ? P.down : P.up, t = now(), age = t - P.t0;
    const fair = up ? pu : 1 - pu, b = this.livreTrie(id, "bids")[0], k = this.livreTrie(id, "asks")[0], ko = this.livreTrie(autre, "asks")[0];
    if (!b || !k) return;
    const mid = (b[0] + k[0]) / 2, main = up ? P.U : P.D, opp = up ? P.D : P.U;
    // sortie au meilleur des deux : vendre notre côté, ou acheter l'autre côté (la paire vaut 1 $ à la fin)
    const vendre = (raison, q) => {
      const n = q || main, v = this.nVendre(id, n), r2 = this.nAcheter(autre, n, 0.99);
      const viaAutre = r2.parts >= n - 1e-6 ? n - r2.cout : -1;
      if (viaAutre > v.recu + 1e-9) { P.cash -= r2.cout; if (up) P.D += r2.parts; else P.U += r2.parts; this.nNote(P, raison + ` : sortie par l'autre côté (${(r2.cout / r2.parts).toFixed(3)}), meilleure de ${(viaAutre - v.recu).toFixed(2)} $`); return true; }
      if (v.vendu <= 0) return false; P.cash += v.recu; if (up) P.U -= v.vendu; else P.D -= v.vendu; this.nNote(P, raison + ` : vente ${v.vendu.toFixed(1)} à ${(v.recu / v.vendu).toFixed(3)}`); return true; };
    // classement du signal pendant la fenêtre de validation
    if (P.etatSignal === "en attente" && age >= NV.DESACCORD.MIN_S) {
      if (mid >= P.prix + 0.02) P.etatSignal = "CONFIRMÉ";
      else if (mid <= P.prix - 0.03 && fair - mid < P.ecart / 2) {
        P.etatSignal = (ko && (1 - fair) - ko[0] >= P.ecart / 2) ? "VRAI RETOURNEMENT" : "SIGNAL RATÉ";
      } else if (age >= NV.DESACCORD.FENETRE_S) P.etatSignal = "PAS DE SUITE";
      if (P.etatSignal !== "en attente") this.nNote(P, "état : " + P.etatSignal + ` (marché ${mid.toFixed(3)}, modèle ${fair.toFixed(3)})`);
    }
    const g = P.gestion;
    if ((g === "validation" || g === "validation+inversion") && (P.etatSignal === "SIGNAL RATÉ" || P.etatSignal === "VRAI RETOURNEMENT") && main > 0) {
      if (vendre("signal raté → fermeture")) {
        if (g === "validation+inversion" && P.etatSignal === "VRAI RETOURNEMENT" && ko) {
          const r2 = this.nAcheter(autre, (P.parts * P.prix) / ko[0], ko[0] + 0.01);
          if (r2.parts > 0) { P.cash -= r2.cout; if (up) P.D += r2.parts; else P.U += r2.parts; this.nNote(P, `INVERSION : achat ${up ? "Down" : "Up"} ${r2.parts.toFixed(1)} à ${(r2.cout / r2.parts).toFixed(3)}`); }
        }
        P.fini2 = true; this.nSauver();
      }
      return;
    }
    if (g === "convergence" && main > 0 && mid >= P.proba0 - 0.02) { if (vendre("le marché a rejoint le modèle → gain encaissé")) { P.fini2 = true; this.nSauver(); } return; }
    if (g === "verrou" && main > 0 && opp < main - 1e-6 && ko && P.prix + ko[0] + 0.072 * ko[0] * (1 - ko[0]) <= 0.97) {
      const r2 = this.nAcheter(autre, main - opp, ko[0] + 0.005);
      if (r2.parts > 0) { P.cash -= r2.cout; if (up) P.D += r2.parts; else P.U += r2.parts; this.nNote(P, `paire verrouillée : achat ${up ? "Down" : "Up"} ${r2.parts.toFixed(1)} à ${(r2.cout / r2.parts).toFixed(3)}`); this.nSauver(); }
      return;
    }
    if (g === "freeroll" && !P.roll && main > 0 && b[0] >= 2 * P.prix && P.prix <= 0.45) {
      if (vendre("prix doublé → la moitié revendue, le reste court gratuitement", main / 2)) { P.roll = true; this.nSauver(); }
      return;
    }
    if (g === "demi" && !P.ajout && P.etatSignal === "CONFIRMÉ" && fair - k[0] >= P.ecart / 2) {
      const r2 = this.nAcheter(id, P.parts, k[0] + 0.01);
      if (r2.parts > 0) { P.cash -= r2.cout; if (up) P.U += r2.parts; else P.D += r2.parts; P.ajout = true; this.nNote(P, `confirmé → 2e moitié ${r2.parts.toFixed(1)} à ${(r2.cout / r2.parts).toFixed(3)}`); this.nSauver(); }
    }
  }
  dTypesResume() {
    const R = {};
    for (const [k, v] of Object.entries(this.N.strats)) {
      for (const T2 of v.trades) {
        if (!T2.type || !k.startsWith("desaccord")) continue;
        const nom = k.slice(0, k.lastIndexOf(" ")), gest = nom.includes("+") ? nom.slice(nom.indexOf("+") + 1) : "simple";
        const z = ((R[T2.type] = R[T2.type] || {})[gest] = R[T2.type][gest] || { n: 0, g: 0, pnl: 0, etats: {} });
        z.n++; if (T2.net >= 0) z.g++; z.pnl = +(z.pnl + T2.net).toFixed(2);
        if (T2.etatSignal) z.etats[T2.etatSignal] = (z.etats[T2.etatSignal] || 0) + 1;
      }
    }
    return R;
  }

  // ================= stratégies « inverses » : au même instant, acheter l'autre côté au meilleur vendeur, même montant, gardé jusqu'à la fin
  nInverse(strat, a, mk, upOrig, usd) {
    if (NV.DESACCORD.ARRETES) return;
    const up = !upOrig, id = up ? mk.up : mk.down, ask = this.livreTrie(id, "asks")[0];
    if (!ask || ask[0] > 0.97) return;
    const r = this.nAcheter(id, usd / ask[0], ask[0] + 0.01);
    if (r.parts < 1) return;
    const P = this.nPos("inverse " + strat, a, mk, { famille: "inverse", cote: up ? "Up" : "Down", prix: +(r.cout / r.parts).toFixed(4), parts: +r.parts.toFixed(2), restant_s: +(mk.end - now()).toFixed(0) });
    P.cash = -r.cout; if (up) P.U = r.parts; else P.D = r.parts;
    this.nNote(P, `inverse de ${strat} : achat ${P.cote} ${r.parts.toFixed(1)} parts à ${P.prix}`);
  }

  // ================= ordres fantômes avec le délai taker de Polymarket (50 ms et 250 ms) + « inverse »
  // À la décision : prix limite et montant. 50 / 250 ms plus tard : quelle quantité le carnet sert encore à ce prix ou mieux ?
  // Au même instant : prix du côté opposé (pour tester « acheter l'inverse quand on est servi »). Puis valeur 1 s et 5 s après.
  nTenter(strat, a, mk, up, limite, usd, fair) {
    const id = up ? mk.up : mk.down, autre = up ? mk.down : mk.up, t0 = now();
    const O = { strat, a, start: mk.start, end: mk.end, slug: mk.slug, cote: up ? "Up" : "Down", limite: +(+limite).toFixed(3), usd: +(+usd).toFixed(2), fair: +(+fair).toFixed(3), t0: +t0.toFixed(2),
      ask0: (this.livreTrie(id, "asks")[0] || [null])[0], restant: +(mk.end - t0).toFixed(0) };
    const servi = () => { let parts = 0, cout = 0, reste = O.usd; for (const [p, sz] of this.livreTrie(id, "asks")) { if (p > O.limite + 1e-9 || reste < 0.01) break; const k = Math.min(sz, reste / p); parts += k; cout += k * p; reste -= k * p; } return { parts: +parts.toFixed(2), prix: parts ? +(cout / parts).toFixed(4) : null }; };
    const opp = () => (this.livreTrie(autre, "asks")[0] || [null])[0];
    const mid = () => { const b = this.livreTrie(id, "bids")[0], k = this.livreTrie(id, "asks")[0]; return b && k ? +((b[0] + k[0]) / 2).toFixed(3) : null; };
    setTimeout(() => { try { O.f50 = servi(); O.opp50 = opp(); } catch (_) {} }, 50);
    setTimeout(() => { try { O.f250 = servi(); O.opp250 = opp(); } catch (_) {} }, 250);
    setTimeout(() => { try { O.mid1s = mid(); } catch (_) {} }, 1000);
    setTimeout(() => { try { O.mid5s = mid(); } catch (_) {} }, 5000);
    (this.N.ordres = this.N.ordres || []).push(O);
    if (this.N.ordres.length > 3000) this.N.ordres.shift();
  }
  nOrdresResume() {
    const R = {};
    for (const [k, z] of Object.entries(this.N.ordAgg || {})) R[k] = Object.fromEntries(Object.entries(z).map(([x, v]) => [x, +(+v).toFixed(2)]));
    return R;
  }
  nOrdreCumul(O) {
    const R = (this.N.ordAgg = this.N.ordAgg || {});
    {
      const k = O.strat + " " + O.a, z = (R[k] = R[k] || { essais: 0, gagnants: 0, s50: 0, s250: 0, g50: 0, g250: 0, pnl50: 0, pnl250: 0, parts50: 0, parts250: 0, nonServisGagnants: 0, nonServis: 0, inv50: 0, invN: 0, pnlParfait: 0 });
      z.essais++; if (O.gagne) z.gagnants++;
      const fee = (p) => 0.072 * p * (1 - p);
      if (O.ask0 != null) z.pnlParfait += ((O.gagne ? 1 : 0) - O.ask0 - fee(O.ask0)) * (O.usd / O.ask0);
      for (const [d, f] of [["50", O.f50], ["250", O.f250]]) {
        if (f && f.parts > 0) { z["s" + d]++; if (O.gagne) z["g" + d]++; z["pnl" + d] += f.parts * ((O.gagne ? 1 : 0) - f.prix - fee(f.prix)); z["parts" + d] += f.parts; }
      }
      if (O.f50 && O.f50.parts > 0 && O.opp50 != null) { z.invN++; z.inv50 += (O.usd / O.opp50) * ((O.gagne ? 0 : 1) - O.opp50 - fee(O.opp50)); }
      if (!(O.f50 && O.f50.parts > 0)) { z.nonServis++; if (O.gagne) z.nonServisGagnants++; }
    }
  }

  // ================= audit de la règle de résolution : notre moyenne Chainlink 60 s contre le prix à battre et le prix final officiels
  async nAudit() {
    const t = now(), A = (this.N.audit = this.N.audit || { fait: {}, lignes: [] });
    for (const a of V1.ACTIFS) {
      const st = Math.floor(t / 300) * 300 - 300;               // dernier cycle terminé
      if (t < st + 300 + 25 || A.fait[a] === st) continue;
      A.fait[a] = st;
      const moy = (a2, b2) => { const v = []; for (let s2 = a2; s2 <= b2; s2++) { const x = this.prixA(a, "cl", s2); if (x) v.push(x); } return v.length ? { m: v.reduce((x, y) => x + y, 0) / v.length, n: v.length } : null; };
      try {
        const ev = await (await fetch(`${G}/events?slug=${a.toLowerCase()}-updown-5m-${st}`)).json();
        const e = ev[0], m = e.markets[0], meta = (typeof e.eventMetadata === "string" ? JSON.parse(e.eventMetadata) : e.eventMetadata) || (typeof m.eventMetadata === "string" ? JSON.parse(m.eventMetadata) : m.eventMetadata) || {};
        const px = JSON.parse(m.outcomePrices || "[]").map(Number), outs = JSON.parse(m.outcomes || "[]");
        const deb = moy(st - 59, st), fin2 = moy(st + 241, st + 300), fin3 = moy(st + 240, st + 299);
        A.lignes.unshift({ a, start: st, ptb: meta.priceToBeat ?? null, final: meta.finalPrice ?? null, notreDebut: deb && +deb.m.toFixed(4), nDebut: deb && deb.n,
          notreFin: fin2 && +fin2.m.toFixed(4), nFin: fin2 && fin2.n, notreFinDecale: fin3 && +fin3.m.toFixed(4), gagnant: px.includes(1) ? outs[px.indexOf(1)] : null });
        A.lignes.length = Math.min(A.lignes.length, 600);
      } catch (err) { this.erreur("audit", err); }
    }
  }

  // ================= règlement officiel de chaque cycle (09.10.2026) : prix à battre et prix final officiels + gagnant, contre nos données
  // (enregistrement seulement ; on réessaie jusqu'à 15 min après la fin, toutes les 30 s au plus)
  async nReglements() {
    const t = now(), cur = Math.floor(t / 300) * 300;
    if (t - (this._rgT || 0) < 30) return; this._rgT = t;
    const RG = (this.RG = this.RG || (await this.state.storage.get("regl")) || { lignes: [], attente: {} });
    for (const a of ["BTC", "ETH"]) {
      const st = cur - 300, k = a + st;
      if (!RG.attente[k] && !RG.lignes.some((x) => x.a === a && x.start === st)) {
        const B = (this._clBrut || {})[a] || [], fen = (c) => B.filter((x) => Math.abs(x[0] - c) <= 15).map((x) => [+(x[0] - c).toFixed(3), +(x[1] - c).toFixed(3), +(x[2] - c).toFixed(3), x[3]]);
        RG.attente[k] = { a, start: st, obsDebut: fen(st), obsFin: fen(st + 300), notreK: ((this._kPrec || {})[a + st] || {}).k ?? null, sourceK: ((this._kPrec || {})[a + st] || {}).src ?? null, kVuApres_s: ((this._kPrec || {})[a + st] || {}).vu ?? null, kAvant: ((this._kPrec || {})[a + st] || {}).avant ?? null, kSerie: ((this._kPrec || {})[a + st] || {}).serie ?? null, kSite: ((this._kPrec || {})[a + st] || {}).site ?? null, notreClDebut: this.prixA(a, "cl", st), notreClFin: this.prixA(a, "cl", st + 300), notrePerpFin: this.prixA(a, "perp", st + 300) };
      }
    }
    let n = 0;
    for (const [k, L] of Object.entries(RG.attente)) {
      if (t > L.start + 300 + 900) { RG.lignes.unshift({ ...L, gagnant: null, ptb: null, final: null, abandon: true }); delete RG.attente[k]; continue; }
      if (n++ >= 2) break;
      try {
        const ev = await (await fetch(`${G}/events?slug=${L.a.toLowerCase()}-updown-5m-${L.start}`)).json();
        const e = ev[0], m = e.markets[0];
        let meta = e.eventMetadata || m.eventMetadata || {}; if (typeof meta === "string") meta = JSON.parse(meta);
        const px = JSON.parse(m.outcomePrices || "[]").map(Number), outs = JSON.parse(m.outcomes || "[]");
        if (!(px.includes(1) && px.includes(0))) continue;
        let cp = null, op = null;
        try {
          const iso = (x) => new Date(x * 1000).toISOString().replace(".000", "");
          const r2 = await fetch(`https://polymarket.com/api/crypto/crypto-price?symbol=${L.a}&eventStartTime=${iso(L.start)}&variant=fiveminute&endDate=${iso(L.start + 300)}`, { headers: { "User-Agent": "Mozilla/5.0", Accept: "application/json" } });
          if (r2.ok) { const d2 = await r2.json(); op = d2.openPrice != null ? +d2.openPrice : null; cp = d2.closePrice != null ? +d2.closePrice : null; L.brut = JSON.stringify(d2).slice(0, 300); }
        } catch (_) {}
        const fin = meta.finalPrice != null ? +meta.finalPrice : cp;
        if (fin == null && t < L.start + 300 + 300) continue;
        RG.lignes.unshift({ ...L, gagnant: outs[px.indexOf(1)], ptb: meta.priceToBeat != null ? +meta.priceToBeat : op, final: fin, ouvertureApi: op, clotureApi: cp, vu: Math.round(t - L.start - 300) });
        delete RG.attente[k];
      } catch (_) {}
    }
    RG.lignes.length = Math.min(RG.lignes.length, 2500);
    this.state.storage.put("regl", RG).catch((err) => this.erreur("sauvegarde regl", err));
  }

  // ---- règlement : résultat officiel Polymarket (20 s après la fin)
  async nRegler() {
    try { await this.nAudit(); } catch (_) {}
    try { await this.nReglements(); } catch (err) { this.erreur("règlements", err); }
    // résultat des ordres fantômes
    const cacheG = this._cacheG = this._cacheG || {};
    for (const O of (this.N.ordres || [])) {
      if (O.gagne != null || now() < O.end + 25) continue;
      try {
        if (!(O.slug in cacheG)) {
          const ev = await (await fetch(`${G}/events?slug=${O.slug}`)).json();
          const m = ev[0].markets[0], px = JSON.parse(m.outcomePrices || "[]").map(Number), outs = JSON.parse(m.outcomes || "[]");
          cacheG[O.slug] = (px.includes(1) && px.includes(0)) ? String(outs[px.indexOf(1)]) : null;
        }
        if (cacheG[O.slug]) { O.gagne = cacheG[O.slug] === O.cote; this.nOrdreCumul(O); }
      } catch (_) {}
    }
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
          : P.famille === "desaccordG" ? ((P.U === 0 && P.D === 0) ? "fermé avant la fin" : (P.U > 0 && P.D > 0 ? "paire / inversé" : ((g === "Up" ? P.U : P.D) > 0 ? "gagné" : "perdu")))
          : (P.strat === "fin" || P.strat.startsWith("desaccord") || P.strat.startsWith("inverse")) ? (g === P.cote ? "gagné" : "perdu") : (P.U > 0 && P.D > 0 ? "paires + reste" : "une seule jambe");
        this.nClore(P, issue);
      } catch (err) { garder.push(P); this.erreur("fantômes règlement", err); }
    }
    this.N.attente = garder;
    this.nSauver();
    try { await this.blkRegler(); } catch (err) { this.erreur("qui converge règlement", err); }
  }

  nVue() {
    // V1 actuel (avec stop) sur la même période, pour comparer
    const v1 = {};
    if (NV.ACTIVES.includes("V1 actuel (avec stop)")) for (const [a, V] of [["BTC", this.e.V1], ["ETH", this.e.V1x.ETH]]) {
      const T2 = (V.trades || []).filter((x) => x.heure && Date.parse(x.heure) / 1000 >= this.N.depuis && x.net != null);
      v1["V1 actuel (avec stop) " + a] = { depuis: this.N.depuis, n: T2.length, pnl: T2.reduce((s2, x) => s2 + x.net, 0), gains: T2.filter((x) => x.net >= 0).length, pertes: T2.filter((x) => x.net < 0).length,
        pertesTot: T2.filter((x) => x.net < 0).reduce((s2, x) => s2 + x.net, 0), pire: T2.length ? Math.min(...T2.map((x) => x.net)) : 0, ...nRisqueVue(nRisqueDepuis(T2)) };
    }
    const resume = Object.fromEntries(Object.entries(this.N.strats).map(([k, v]) => [k, { depuis: v.depuis, n: v.n, pnl: v.pnl, gains: v.gains, pertes: v.pertes,
      pertesTot: v.trades.filter((x) => x.net < 0).reduce((s2, x) => s2 + x.net, 0), pire: v.trades.length ? Math.min(...v.trades.map((x) => x.net)) : 0, ...nRisqueVue(v.rq && v.rq.hist ? v.rq : nRisqueDepuis(v.trades)) }]));
    return { depuis: this.N.depuis, typesDesaccord: this.dTypesResume(), markout: Object.fromEntries(Object.entries(this.N.markout || {}).map(([k, v]) => [k, { remplissages: v.n, ...Object.fromEntries(["0.1s", "0.5s", "1s", "3s", "10s"].map((h) => [h, v.nOk[h] ? +(100 * v[h] / v.nOk[h]).toFixed(2) : null])) }])), ordres: this.nOrdresResume(), audit: ((this.N.audit || {}).lignes || []).slice(0, 200), manquees: this.N.manq || {}, resume: { ...v1, ...resume }, reglages: NV, strats: Object.fromEntries(Object.entries(this.N.strats).map(([k, v]) => [k, { depuis: v.depuis, n: v.n, gains: v.gains, pertes: v.pertes, pnl: v.pnl, issues: v.issues, trades: v.trades.slice(0, 25).map((t) => ({ heure: t.heure, cote: t.cote, U: t.U, D: t.D, issue: t.issue, net: t.net, prix: t.prix, type: t.type, etatSignal: t.etatSignal, journal: (t.journal || []).slice(-4) })) }])),
      blink: this.blkVue(), actives: NV.ACTIVES, ouvertes: this.N.ouvertes, attente: this.N.attente.length, offresMM: this._mmQ || {} };
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
h1{font-size:20px;margin:0 0 4px}a{color:var(--ac)}.mu{color:var(--mu);font-size:13px}.card{background:var(--card);border:1px solid var(--bd);border-radius:12px;padding:14px;margin:12px 0;overflow-x:hidden}
.g{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}.k{font-size:12px;color:var(--mu)}.v{font-size:20px;font-weight:600;font-variant-numeric:tabular-nums}
.ok{color:var(--ok)}.ko{color:var(--ko)}.wa{color:var(--wa)}table{width:100%;border-collapse:collapse;font-size:13px;font-variant-numeric:tabular-nums}td,th{padding:6px 4px;border-bottom:1px solid var(--bd);text-align:left;white-space:normal;overflow-wrap:break-word}
button{background:var(--ac);color:#fff;border:0;border-radius:8px;padding:10px 14px;font-size:15px;width:100%;margin-top:8px}.badge{display:inline-block;padding:2px 8px;border-radius:99px;font-size:12px;background:var(--bd)}
@media(max-width:420px){.g{grid-template-columns:repeat(2,1fr)}}
@media(max-width:700px){table,tbody,tr,td{display:block;width:100%}tr:first-child:has(th){display:none}tr{border:1px solid var(--bd);border-radius:8px;margin:8px 0;padding:4px 8px}td{border:0;padding:3px 0;max-width:none!important}td[data-l]::before{content:attr(data-l)" : ";color:var(--mu);font-size:12px}}</style>
<script>(()=>{const lab=()=>{for(const t of document.querySelectorAll("table")){const h=[...(t.rows[0]?t.rows[0].cells:[])].map(c=>c.tagName==="TH"?c.textContent.trim():"");if(!h.some(x=>x))continue;for(let i=1;i<t.rows.length;i++){const r=t.rows[i];for(let j=0;j<r.cells.length;j++){const c=r.cells[j];if(h[j]&&!c.hasAttribute("data-l"))c.setAttribute("data-l",h[j]);}}}};const go=()=>{lab();new MutationObserver(lab).observe(document.body,{childList:true,subtree:true});};document.readyState==="loading"?document.addEventListener("DOMContentLoaded",go):go();})();</script>`;

const PAGE = `<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Bot 95</title>${STYLE}</head><body>
<h1>Bot 95 <span class="badge">mode fantôme</span></h1><div class="mu">7 cryptos 5 min Polymarket — achat immédiat (A) + V1 paires BTC — aucun argent réel</div>
<div style="margin-top:8px"><a href="/rapport">→ Rapport détaillé des refus</a> · <a href="/nouveaux">→ Nouvelles stratégies fantômes (assurance, fin de cycle, teneur de marché)</a></div>
<div id="app" class="mu" style="margin-top:12px">Chargement…</div>
<script>
const $=s=>document.querySelector(s);const f=(x,d=2)=>x==null?'—':Number(x).toFixed(d);const usd=x=>(x>=0?'+':'')+f(x)+' $';
async function rep(){await fetch('/api/reprendre',{method:'POST'});go()}
async function go(){try{const d=await (await fetch('/api/etat')).json();const e=d.e;
const pa=[...d.actifs].sort((x,y)=>((e.parActif[y.a]||{}).pnl||0)-((e.parActif[x.a]||{}).pnl||0)).map(x=>{const s=e.parActif[x.a]||{trades:0,gains:0,pertes:0,pnl:0};const v=e.vetos[x.a]||{};const top=Object.entries(v).sort((p,q)=>q[1]-p[1])[0];
return '<tr><td><b>'+x.a+'</b></td><td>'+(e.candidats[x.a]||0)+'</td><td>'+s.trades+'</td><td>'+s.gains+'</td><td>'+s.pertes+'</td><td class="'+(s.pnl>=0?'ok':'ko')+'">'+usd(s.pnl)+'</td><td class=mu>'+(top?top[0]+' ('+top[1]+')':'—')+'</td></tr>'}).join('');
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
return bandeau+'<div class=card><b>V1 — paires BTC (jambe 55 filtrée)</b> <span class=mu>'+(R.actif?'RÉEL':'fantôme')+' · </span> <span class=mu>temps réel'+(V.polyOk?'':' — <span class=ko>carnet en direct déconnecté</span>')+'</span><div class=g style="margin-top:8px"><div><div class=k>Capital</div><div class=v>'+f(V.capital)+' $</div></div><div><div class=k>Gain</div><div class="v '+(V.pnl>=0?'ok':'ko')+'">'+usd(V.pnl)+'</div></div><div><div class=k>Gagnés / perdus</div><div class=v>'+V.gains+' / '+V.pertes+'</div></div></div>'+
'<div class=mu style="margin-top:6px">Réglage A : élan 5 s + stop à −15 points · entrées refusées par l\'élan : '+(V.refusElan||0)+' · source la plus rapide : '+Object.entries(V.sources||{}).map(([k,n])=>k+' '+n).join(', ')+'</div><div class=mu>Issues : '+it+'</div><div class=mu>Réaction : message Polymarket reçu en '+f(V.latPolyMed,3)+' s (90 % sous '+f(V.latPolyP90,3)+' s) · décisions en '+f(V.latDecMed,3)+' s (90 % sous '+f(V.latDecP90,3)+' s)</div>'+p+
'<table style="margin-top:8px"><tr><th>Heure UTC</th><th>Jambe</th><th>Prix</th><th>Proba</th><th>Autre jambe</th><th>Issue</th><th>Net</th></tr>'+tv+'</table></div>'})()+
(()=>{const V=d.v1.eth;if(!V)return '';const it=Object.entries(V.issues||{}).map(([k,x])=>k+' '+x.n+' ('+usd(x.pnl)+')').join(' · ')||'—';
const tv=V.trades.map(t=>'<tr><td>'+t.heure.slice(5,16).replace('T',' ')+'</td><td>'+t.cote+'</td><td>'+f(t.prix,3)+'</td><td>'+f(t.proba,2)+'</td><td>'+(t.B&&t.B.parts?f(t.B.parts,0)+' à '+f(t.B.cout/t.B.parts,2):'—')+'</td><td>'+t.issue+'</td><td class="'+(t.net>=0?'ok':'ko')+'">'+usd(t.net)+'</td></tr>').join('')||'<tr><td colspan=7 class=mu>Aucun trade encore</td></tr>';
const p=V.pos?'<div style="margin-top:8px">En cours : '+V.pos.cote+' à '+f(V.pos.prix,3)+' · proba '+f(V.pos.probaActuelle,2)+' · offre opposée '+f(V.pos.offre,2)+'</div>':'';
return '<div class=card><b>V1 — paires ETH (jambe 55 filtrée)</b> <span class=mu>fantôme</span><div class=g style="margin-top:8px"><div><div class=k>Capital</div><div class=v>'+f(V.capital)+' $</div></div><div><div class=k>Gain</div><div class="v '+(V.pnl>=0?'ok':'ko')+'">'+usd(V.pnl)+'</div></div><div><div class=k>Gagnés / perdus</div><div class=v>'+V.gains+' / '+V.pertes+'</div></div></div><div class=mu style="margin-top:6px">Entrées refusées par l\'élan : '+(V.refusElan||0)+' · Issues : '+it+'</div>'+p+
'<table style="margin-top:8px"><tr><th>Heure UTC</th><th>Jambe</th><th>Prix</th><th>Proba</th><th>Autre jambe</th><th>Issue</th><th>Net</th></tr>'+tv+'</table></div>'})()+
'<div class=card><b>Par crypto</b><table><tr><th>Crypto</th><th>Candidats</th><th>Trades</th><th>Gagnés</th><th>Perdus</th><th>Gain</th><th>Refus le plus fréquent</th></tr>'+pa+'</table></div>'+
'<div class=card><b>Trades</b><table><tr><th>Heure UTC</th><th>Crypto</th><th>Côté</th><th>Prix</th><th>z</th><th>Résultat</th><th>Net</th></tr>'+tr+'</table></div>'+
'<div class=card><b>Flux</b> <span class=mu>(prix et âge de la dernière mise à jour)</span><table><tr><th>Crypto</th><th>Chainlink</th><th>Perp Bybit</th><th>Spot Coinbase</th><th>Prix d\\'exercice</th></tr>'+fl+'</table></div>'+
(d.diag.erreurs.length?'<div class=card><b>Journal technique</b><div class=mu>'+d.diag.erreurs.join('<br>')+'</div></div>':'');
}catch(err){$('#app').textContent='Erreur de chargement : '+err}}
go();setInterval(go,3000);
</script></body></html>`;

// risque : pertes de suite (en cours et max), creux max (plus grosse baisse depuis un sommet), capital conseillé = 2 × creux + 2 mises
function nRisquePas(r, net) { r.hist = r.hist || {}; if (net >= 0 && r.serie > 0) r.hist[r.serie] = (r.hist[r.serie] || 0) + 1; r.serie = net < 0 ? r.serie + 1 : 0; r.serieMax = Math.max(r.serieMax, r.serie); r.cum += net; r.pic = Math.max(r.pic, r.cum); r.creux = Math.min(r.creux, r.cum - r.pic); }
function nRisqueDepuis(trades) { const r = { serie: 0, serieMax: 0, cum: 0, pic: 0, creux: 0, hist: {} }; const T = [...(trades || [])].filter((x) => x.net != null).sort((a, b) => Date.parse(a.heure) - Date.parse(b.heure)); for (const x of T) nRisquePas(r, x.net); return r; }
function nRisqueVue(r) { const h = { ...(r.hist || {}) }; if (r.serie > 0) h[r.serie] = (h[r.serie] || 0) + 1; return { serie: r.serie, serieMax: r.serieMax, series: h, creux: +r.creux.toFixed(2), capital: Math.round((2 * -r.creux + 2 * 50) / 50) * 50 }; }

const PAGE_N = `<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Fantômes</title>${STYLE}</head><body>
<h1>Nouvelles stratégies — mode fantôme</h1>
<div class="mu">Aucun argent réel. Depuis le 07.10 à 15h, seulement sur BTC (ETH abandonné, ses anciens résultats restent visibles) : V1, V1 + assurance (6/9/12 et 4/7/10), désaccord 20 et ses variantes (V2 B à H…). Le 09.10, les stratégies à plus de 500 $ de pertes ont été supprimées (trades sauvés sur GitHub). Toutes les autres stratégies sont arrêtées ; leurs résultats restent visibles, figés, dans « Stratégies arrêtées ».</div>
<div style="margin-top:8px"><a href="/">← Tableau de bord</a></div><div id="app" style="margin-top:12px">Chargement…</div>
<script>
const f=(x)=>(x>=0?"+":"")+x.toFixed(2)+" $";const fc=(x)=>"<span class='"+(x>=0?"ok":"ko")+"'>"+f(x)+"</span>";
const ser=(h)=>{const e=Object.entries(h||{}).map(([l,n])=>[+l,n]).sort((a,b)=>b[0]-a[0]);return e.length?e.map(([l,n])=>l+" de suite : "+n+" fois").join(" · "):"aucune perte";};
const ENTREE={"V1 actuel (avec stop)":"V1 d'origine : achète la jambe à 0,55–0,56 quand le modèle donne ≥ 0,63 et que le prix monte dans ce sens ; offre en face pour faire une paire ; sortie à 0,90 ; stop si le modèle perd 15 points.",
"assurance 6/9/12":"Mêmes entrées que V1, mais SANS stop : quand le modèle baisse de 6 / 9 / 12 points, on achète l'autre côté pour couvrir 25 / 50 / 100 %.",
"assurance 4/7/10":"Mêmes entrées que V1, SANS stop : couverture par l'autre côté plus tôt, à 4 / 7 / 10 points de baisse (25 / 50 / 100 %).",
"fin":"Fin de cycle : dans les dernières 90–180 s, achète à 0,70–0,90 quand le modèle est sûr à ≥ 93–95 %, garde jusqu'à la fin.",
"desaccord 10":"Désaccord 10 : achète le côté que le modèle estime à au moins 10 points de plus que le prix du meilleur vendeur, garde jusqu'à la fin.",
"desaccord 15":"Désaccord 15 : achète le côté que le modèle estime à au moins 15 points de plus que le prix du meilleur vendeur, garde jusqu'à la fin.",
"V5 gain attendu":"V5 : n'achète que si le gain attendu dépasse +50 % par dollar misé, calculé au prix réellement payable pour 50 $ (en descendant dans le carnet), et si le modèle dépasse ce prix d'au moins 5 c. Remplace le seuil fixe de 20 points.",
"V6 loterie":"V6 LOTERIE : jetons à 0,10 $ ou moins (prix payable pour 50 $), seulement si le modèle leur donne au moins 2 fois ce prix. Gagne rarement, paie très gros.",
"V2-B hors 60-89 s":"V2-B : désaccord 20, sauf entre 60 et 89 s de la fin.",
"V2-C perp":"V2-C : désaccord 20 seulement si le perp Bybit va dans notre sens sur 5 s.",
"V2-D perp 120-269 s":"V2-D : désaccord 20 + perp avec nous + entre 120 et 269 s de la fin.",
"V2-E persistant":"V2-E : désaccord 20 seulement s'il tient au moins 1,5 s (pas un éclair).",
"V2-F ecart qui grandit":"V2-F : désaccord 20 seulement si l'écart a grandi d'au moins 3 pts sur 3 s.","V2-F + plus de 120 s":"V2-F + PLUS DE 120 S : comme V2-F, mais seulement s'il reste au moins 120 secondes dans le cycle (les achats de fin de cycle perdent).","V2-F + pas les deux baissent":"V2-F SANS « LES DEUX BAISSENT » : comme V2-F, mais pas d'achat quand, sur les 3 s, le modèle ET le prix Polymarket ont baissé et que Polymarket a baissé plus fort (16 % de gagnants seulement dans l'historique).","V2-F + pas les deux baissent + volatilite >= 2":"V2-F SANS « LES DEUX BAISSENT » + MARCHÉ ACTIF : comme la précédente, et seulement si le perp BTC bouge d'au moins 2 $ par seconde en moyenne sur 60 s (pas de marché calme).",
"V2-G jury des bourses":"V2-G : désaccord 20 seulement si Bybit, OKX, Binance et Coinbase vont tous dans notre sens sur 3 s ET que Polymarket a moins suivi que le modèle (en retard).",
"V2-H veto complet":"V2-H : désaccord 20 sauf veto : écart qui fond, Binance contre nous, Bybit+OKX contre nous, 60-89 s, Polymarket déjà en train de corriger, vendeur < 20 parts.",
"desaccord confirme":"Désaccord CONFIRMÉ : le modèle a 20 pts d'avance (BTC) ou 10 pts (ETH) ; on attend 20 s et on n'achète que si le marché est déjà monté de 3 cents vers le modèle (il garde 3 cents d'avance). Gardé jusqu'à la fin.",
"desaccord confirme perp":"Désaccord CONFIRMÉ + PERP : pareil, et en plus le perp Bybit doit aller dans notre sens sur les 5 dernières secondes.",
"TWAP fin":"TWAP FIN : moteur de règlement exact (prix à battre = moyenne Chainlink des 60 s avant le début ; fin = moyenne des 60 dernières secondes). Achat si sa probabilité dépasse le prix de 20 pts, entre 90 et 20 s de la fin, 50 $ au meilleur vendeur seulement, gardé jusqu'au règlement.","corrige : V2-F + garde-fou":"V2-F avec le modèle corrigé (0,015 %), mais pas d'achat si le BTC est à moins de 20 $ du prix à battre ET si notre côté coûte 5 cents ou moins (le carnet sait probablement mieux que nous).","corrige marge mesuree : V2-F":"V2-F avec une marge d'erreur MESURÉE : écart réel entre notre prix à battre / notre Chainlink et les valeurs officielles du règlement, recalculé sur les 50 derniers cycles (12 $ au départ).","desaccord 20 Binance avec nous":"Désaccord 20 + BINANCE AVEC NOUS : modèle ≥ meilleur vendeur + 20 pts ET Binance a bougé dans notre sens sur les 3 s avant → achat immédiat 50 $, garde jusqu'à la fin.","desaccord 20 Binance avec nous sans nuit":"Désaccord 20 + BINANCE AVEC NOUS : modèle ≥ meilleur vendeur + 20 pts ET Binance a bougé dans notre sens sur les 3 s avant → achat immédiat 50 $, garde jusqu'à la fin. SANS LA NUIT : aucun achat entre 00h et 08h (heure suisse).","desaccord 20 Binance ou perp avec nous":"Désaccord 20 + BINANCE OU PERP AVEC NOUS : pareil, il suffit que Binance OU le perp Bybit ait bougé dans notre sens sur 3 s.","desaccord 20 Binance ou perp avec nous sans nuit":"Désaccord 20 + BINANCE OU PERP AVEC NOUS : pareil, il suffit que Binance OU le perp Bybit ait bougé dans notre sens sur 3 s. SANS LA NUIT : aucun achat entre 00h et 08h (heure suisse).","desaccord 20 aucune bourse contre + sortie 10 s":"Désaccord 20 + AUCUNE BOURSE CONTRE NOUS (Binance, perp, OKX, Coinbase sur 3 s) → achat immédiat ; 10 s après, si Polymarket n'a pas rejoint le modèle, revente au meilleur acheteur, sinon garde jusqu'à la fin.","desaccord 20 aucune bourse contre + sortie 10 s sans nuit":"Désaccord 20 + AUCUNE BOURSE CONTRE NOUS (Binance, perp, OKX, Coinbase sur 3 s) → achat immédiat ; 10 s après, si Polymarket n'a pas rejoint le modèle, revente au meilleur acheteur, sinon garde jusqu'à la fin. SANS LA NUIT : aucun achat entre 00h et 08h (heure suisse).","desaccord 30 zone + Binance et perp + sortie modele -10 + pas Poly qui baisse + taille 25/50":"COMBINÉ : zone + Binance et perp + sortie -10 + pas « Polymarket qui baisse », et mise de 25 $ seulement si le modèle n'a pas monté d'au moins 3 pts dans les 3 s avant (50 $ sinon).","desaccord 30 zone + Binance et perp + sortie modele -10 + pas Poly qui baisse":"ZONE + BINANCE ET PERP + SORTIE -10 + PAS « POLYMARKET QUI BAISSE » : comme zone + Binance et perp + sortie -10, mais on n'achète pas si le désaccord vient d'un vendeur Polymarket qui a baissé son prix d'au moins 3 c en 3 s sans que le modèle monte. Revente plafonnée (jamais sous 0,05 $ ni 2 c sous le meilleur acheteur).","corrige : desaccord 20":"MODÈLE CORRIGÉ — DÉSACCORD 20 : comme désaccord 20, mais avec la probabilité du modèle corrigé (marge d'incertitude 0,015 % au lieu de 0,08 %, qui gonflait les chances des outsiders).","corrige : V2-F ecart qui grandit":"MODÈLE CORRIGÉ — V2-F : désaccord 20 qui grandit d'au moins 3 pts en 3 s, calculé avec le modèle corrigé.","corrige : V2-F + pas les deux baissent":"MODÈLE CORRIGÉ — V2-F sans « les deux baissent, Polymarket plus fort ».","corrige : zone + Binance et perp + sortie -10":"MODÈLE CORRIGÉ — ZONE : écart >= 30 pts, jeton 0,15-0,35 $, > 60 s, Binance et perp pas contre nous ; revente (plancher 0,05 $) si le modèle corrigé perd 10 pts.","desaccord 30 zone + modele monte":"ZONE + LE MODÈLE A MONTÉ : zone (écart >= 30 pts, 0,15-0,35 $, > 60 s) et le désaccord vient du modèle qui a monté d'au moins 3 pts sur les 3 dernières secondes (le BTC a bougé, Polymarket pas encore). Garde jusqu'à la fin.","desaccord 30 zone + sortie modele -10":"ZONE + SORTIE MODÈLE -10 : comme Désaccord 30 zone 0,15-0,35, mais on revend au meilleur acheteur dès que le modèle a perdu 10 pts par rapport à l'entrée.","desaccord 30 zone + Binance et perp + sortie modele -10":"ZONE + BINANCE ET PERP + SORTIE MODÈLE -10 : zone, Binance et perp pas contre nous sur 3 s, et revente si le modèle perd 10 pts.","desaccord 30 0,15-0,60 + perp + ecart qui grandit":"DÉSACCORD 30 LARGE + PERP + ÉCART QUI GRANDIT : écart >= 30 pts, jeton entre 0,15 et 0,60 $, plus de 60 s, perp pas contre nous sur 3 s et écart plus grand qu'il y a 3 s. Garde jusqu'à la fin.","desaccord 30 zone 0,15-0,35":"Désaccord 30 ZONE 0,15-0,35 : modèle ≥ meilleur vendeur + 30 pts, jeton vendu entre 0,15 et 0,35 $, plus de 60 s restantes → achat 50 $, garde jusqu'à la fin. Zone robuste trouvée le 08.10 (positive sur les 4 quarts des 48 h).","desaccord 30 zone 0,15-0,35 + Binance et perp":"Désaccord 30 ZONE 0,15-0,35 + BINANCE ET PERP : pareil, et Binance et le perp Bybit ne vont pas contre nous sur les 3 s avant.","desaccord 20 Poly rejoint 3 s":"Désaccord 20 POLY REJOINT 3 s : quand le modèle dépasse le meilleur vendeur de 20 pts, on attend 3 s ; on achète 50 $ seulement si Polymarket a monté d'au moins 3 c vers le modèle (et le modèle n'a pas baissé de 3 c). Garde jusqu'à la fin.","desaccord 20 Poly rejoint 10 s":"Désaccord 20 POLY REJOINT 10 s : pareil, mais on attend 10 s avant de vérifier que Polymarket a rejoint le modèle.","desaccord 20 Poly rejoint 3 s sans nuit":"Désaccord 20 POLY REJOINT 3 s SANS LA NUIT : comme « Poly rejoint 3 s », aucun achat entre 00h et 08h (heure suisse).","desaccord 20 Poly rejoint 10 s sans nuit":"Désaccord 20 POLY REJOINT 10 s SANS LA NUIT : comme « Poly rejoint 10 s », aucun achat entre 00h et 08h (heure suisse).","desaccord 20 sans nuit":"Désaccord 20 SANS LA NUIT : exactement comme Désaccord 20, mais aucun achat entre 00h et 08h (heure suisse).","desaccord 20":"Désaccord 20 : achète le côté que le modèle estime à au moins 20 points de plus que le prix du meilleur vendeur, garde jusqu'à la fin.",
"desaccord combine 2.5":"Valeur combinée 2,5 : on mélange le prix du marché (≈70 %) et notre modèle (≈30 %) ; achète si cette valeur combinée dépasse le vendeur d'au moins 2,5 points.",
"desaccord combine 4":"Valeur combinée 4 : on mélange le prix du marché (≈70 %) et notre modèle (≈30 %) ; achète si cette valeur combinée dépasse le vendeur d'au moins 4 points.",
"desaccord maker 10":"Maker : quand le modèle voit 10 points d'avantage, on POSE une offre d'achat (sans frais) au lieu d'acheter au vendeur ; retirée si l'avantage fond ou après 30 s.",
"desaccord croise 10":"Croisé : désaccord 10, mais seulement si l'autre crypto (BTC ↔ ETH) montre un désaccord dans le même sens au même moment.",
"mm prudent":"Teneur de marché prudente : offres d'achat Up et Down à la valeur du modèle − 12 cents, 10 parts max, retirées si le prix bouge vite."};
const GEST={"validation":"Gestion VALIDATION : après l'entrée, si le prix va contre nous de 3 cents et que le modèle lâche (signal raté), on ferme tout de suite.",
"validation+inversion":"Gestion VALIDATION + INVERSION : comme validation, et si en plus le modèle voit un avantage de l'autre côté (vrai retournement), on achète l'autre côté.",
"convergence":"Gestion CONVERGENCE : dès que le prix du marché rejoint ce que disait le modèle, on revend et on encaisse le gain.",
"verrou":"Gestion VERROU : si notre côté monte et que l'autre côté devient assez bon marché (paire ≤ 0,97 $), on l'achète : gain garanti quel que soit le résultat.",
"demi":"Gestion DEMI : on achète la moitié à l'entrée, et la 2e moitié seulement si le prix confirme dans les 20 s.",
"freeroll":"Gestion FREE ROLL : si le prix double, on revend la moitié (la mise est remboursée) et le reste court gratuitement."};
const expl=(st)=>{let inv=false;if(st.startsWith("inverse ")){inv=true;st=st.slice(8);}let g=null;const i=st.indexOf(" +");if(i>0){g=st.slice(i+2);st=st.slice(0,i);}let t=ENTREE[st]||st;if(g)t+=" "+(GEST[g]||g);else if(st.startsWith("desaccord"))t+=" Gestion SIMPLE : rien après l'entrée, on garde jusqu'à la fin.";if(inv)t="INVERSE : au même moment, achète l'AUTRE côté (même montant), garde jusqu'à la fin. Stratégie d'origine → "+t;return t;};
async function maj(){try{const d=await (await fetch("/api/nouveaux",{cache:"no-store"})).json();if(d.pv&&d.pv!=="__PV__"){location.reload();return;}let h="<div class='mu'>Depuis "+new Date(d.depuis*1000).toLocaleString("fr-CH")+" · "+d.ouvertes.length+" position(s) ouverte(s), "+d.attente+" en attente du résultat</div>";
const noms={"desaccord combine 2.5":"Désaccord VALEUR COMBINÉE ≥ 2,5 pts","desaccord combine 4":"Désaccord VALEUR COMBINÉE ≥ 4 pts","desaccord maker 10":"Désaccord MAKER (offre posée, sans frais)","desaccord croise 10":"Désaccord 10 CONFIRMÉ par l'autre crypto","desaccord 10 +validation":"Désaccord 10 + validation (fermer si signal raté)","desaccord 10 +validation+inversion":"Désaccord 10 + validation + inversion si vrai retournement","desaccord 10 +convergence":"Désaccord 10 + encaisser quand le marché rejoint le modèle","desaccord 10 +verrou":"Désaccord 10 + verrouiller la paire si ≤ 0,97","desaccord 10 +demi":"Désaccord 10 + moitié puis 2e moitié si confirmé","inverse V1":"↔ INVERSE de V1","inverse fin":"↔ INVERSE de fin de cycle","inverse desaccord 10":"↔ INVERSE de désaccord ≥ 10","inverse desaccord 15":"↔ INVERSE de désaccord ≥ 15","inverse desaccord 20":"↔ INVERSE de désaccord ≥ 20","desaccord 10":"Désaccord modèle/marché ≥ 10 pts","desaccord 15":"Désaccord ≥ 15 pts","desaccord 20":"Désaccord ≥ 20 pts","desaccord 20 sans nuit":"Désaccord ≥ 20 pts SANS LA NUIT (pas d'achat 00h-08h)","assurance 6/9/12":"V1 + assurance 6/9/12 (sans stop)","assurance 4/7/10":"V1 + assurance 4/7/10 (sans stop)","fin":"Fin de cycle 0,70–0,90","mm actuel":"Teneur de marché — actuel","mm pencher":"Teneur de marché — pencher 4 cents","mm prudent":"Teneur de marché — prudent (retrait + pencher + petit)"};
const cles=Object.keys(d.strats).sort((x,y)=>((d.strats[y]||{}).pnl||0)-((d.strats[x]||{}).pnl||0));
const R=d.resume||{},base=(k)=>k.replace(/^inverse /,"").replace(/^V1 actuel \(avec stop\)/,"V1"),rk=Object.keys(R).sort((x,y)=>((R[y]||{}).pnl||0)-((R[x]||{}).pnl||0));
const act=(k)=>(d.actives||[]).includes(k.slice(0,k.lastIndexOf(" ")));
h+="<div class='card'><h2>Stratégies actives — classées par résultat en $</h2><table><tr><th>Stratégie</th><th>Ce qu'elle fait</th><th>Depuis</th><th>Trades</th><th>Gagnés / perdus</th><th>Résultat</th><th>Pertes totales</th><th>Pire trade</th><th>Pertes de suite (max / en cours)</th><th>Combien de fois</th><th>Creux max</th><th>Capital conseillé</th></tr>"+rk.filter(act).map(k=>{const x=R[k],st=k.slice(0,k.lastIndexOf(" ")),a=k.slice(k.lastIndexOf(" ")+1);return "<tr><td>"+(noms[st]||st)+" — "+a+"</td><td class='mu' style='font-size:11px;max-width:420px'>"+expl(st.replace(/^V1 actuel \(avec stop\)$/,"V1 actuel (avec stop)"))+"</td><td>"+new Date(x.depuis*1000).toLocaleString("fr-CH",{day:"2-digit",month:"2-digit",hour:"2-digit",minute:"2-digit"})+"</td><td>"+x.n+"</td><td>"+x.gains+" / "+x.pertes+"</td><td><b>"+fc(x.pnl)+"</b></td><td>"+f(x.pertesTot)+"</td><td>"+f(x.pire)+"</td><td><b>"+(x.serieMax??"—")+"</b> / "+(x.serie??"—")+"</td><td class='mu' style='font-size:11px'>"+ser(x.series)+"</td><td>"+(x.creux!=null?f(x.creux):"—")+"</td><td><b>"+(x.capital!=null?x.capital+" $":"—")+"</b></td></tr>"}).join("")+"</table></div>";
const BK=d.blink;if(BK){const FM=[["POLY REJOINT","Polymarket rejoint le modèle"],["MODELE RETOMBE","Le modèle retombe vers Polymarket"],["LES DEUX","Les deux se rapprochent"],["RIEN","Rien ne bouge (moins de 3 c)"]];const cel=(z)=>z&&z.n?z.n+" · "+Math.round(100*z.g/z.n)+" % gagnés · <b>"+fc(z.pnl)+"</b>":"—";h+="<div class='card'><h2>Qui converge vers qui ? (BTC, mesure en direct, aucun achat)</h2><div class='mu'>À chaque 1er désaccord ≥ 20 pts du cycle : 1, 3 et 10 s plus tard, est-ce Polymarket qui rejoint le modèle (désaccord vrai) ou le modèle qui retombe (désaccord faux) ? Chaque case : désaccords · % gagnés à la fin · résultat si on avait acheté 50 $ à l'entrée. Depuis "+new Date(BK.depuis*1000).toLocaleString("fr-CH",{day:"2-digit",month:"2-digit",hour:"2-digit",minute:"2-digit"})+" · "+BK.n+" désaccords, "+BK.regles+" réglés.</div><table><tr><th>Famille</th><th>Après 1 s</th><th>Après 3 s</th><th>Après 10 s</th></tr>"+FM.map(([k,l])=>"<tr><td>"+l+"</td>"+[1,3,10].map(x=>"<td>"+cel((BK.parH[x]||{fam:{}}).fam[k])+"</td>").join("")+"</tr>").join("")+"<tr><td><b>Tous</b></td>"+[1,3,10].map(x=>"<td>"+cel((BK.parH[x]||{}).tous)+"</td>").join("")+"</tr></table><div style='margin-top:6px'>Attendre 3 s et n'acheter que si Polymarket rejoint le modèle : <b>"+cel(BK.attendre3)+"</b></div><table style='margin-top:8px'><tr><th>Bourse (3 s avant)</th><th>Contre nous</th><th>Neutre</th><th>Avec nous</th></tr>"+Object.entries(BK.sens||{}).map(([nm,z])=>"<tr><td>"+nm+"</td>"+["contre nous","neutre","avec nous"].map(s=>{const c=z[s];return "<td>"+(c&&c.n?cel(c)+"<br><span class='mu' style='font-size:10px'>Poly rejoint "+c.pr+" · modèle retombe "+c.mr+"</span>":"—")+"</td>"}).join("")+"</tr>").join("")+"</table></div>";}
h+="<div class='card'><details><summary><b>Stratégies arrêtées le 07.10 (résultats figés)</b></summary><table><tr><th>Stratégie</th><th>Ce qu'elle fait</th><th>Depuis</th><th>Trades</th><th>Gagnés / perdus</th><th>Résultat</th><th>Pertes totales</th><th>Pire trade</th><th>Pertes de suite (max / en cours)</th><th>Combien de fois</th><th>Creux max</th><th>Capital conseillé</th></tr>"+rk.filter(k=>!act(k)).map(k=>{const x=R[k],st=k.slice(0,k.lastIndexOf(" ")),a=k.slice(k.lastIndexOf(" ")+1);return "<tr><td>"+(noms[st]||st)+" — "+a+"</td><td class='mu' style='font-size:11px;max-width:420px'>"+expl(st.replace(/^V1 actuel \(avec stop\)$/,"V1 actuel (avec stop)"))+"</td><td>"+new Date(x.depuis*1000).toLocaleString("fr-CH",{day:"2-digit",month:"2-digit",hour:"2-digit",minute:"2-digit"})+"</td><td>"+x.n+"</td><td>"+x.gains+" / "+x.pertes+"</td><td><b>"+fc(x.pnl)+"</b></td><td>"+f(x.pertesTot)+"</td><td>"+f(x.pire)+"</td><td><b>"+(x.serieMax??"—")+"</b> / "+(x.serie??"—")+"</td><td class='mu' style='font-size:11px'>"+ser(x.series)+"</td><td>"+(x.creux!=null?f(x.creux):"—")+"</td><td><b>"+(x.capital!=null?x.capital+" $":"—")+"</b></td></tr>"}).join("")+"</table></details></div>";
const TY=d.typesDesaccord||{};if(Object.keys(TY).length){const G=["simple","validation","validation+inversion","convergence","verrou","demi","freeroll"];h+="<div class='card'><h2>Désaccords : résultat par type de configuration et par gestion</h2><div class='mu'>Type = moment du cycle | prix acheté | sens du perp | sens du marché. Chaque case : trades, gagnés, résultat. États du signal : CONFIRMÉ / PAS DE SUITE / SIGNAL RATÉ / VRAI RETOURNEMENT (seul ce dernier autorise l'inversion).</div><table><tr><th>Type</th>"+G.map(g=>"<th>"+g+"</th>").join("")+"</tr>"+Object.entries(TY).sort((x,y)=>((y[1].simple||{}).n||0)-((x[1].simple||{}).n||0)).map(([t,z])=>"<tr><td style='font-size:11px'>"+t+"</td>"+G.map(g=>{const c=z[g];return "<td>"+(c?c.n+" · "+c.g+" G · <b>"+fc(c.pnl)+"</b>"+(c.etats&&Object.keys(c.etats).length?"<br><span class='mu' style='font-size:10px'>"+Object.entries(c.etats).map(([e,n])=>e+" "+n).join(", ")+"</span>":""):"—")+"</td>"}).join("")+"</tr>").join("")+"</table></div>";}
const OR=d.ordres||{};if(Object.keys(OR).length){h+="<div class='card'><h2>Ordres fantômes avec le délai de Polymarket</h2><div class='mu'>Essais = moments où la stratégie voulait acheter. Servi = le vendeur était encore là 50 ms / 250 ms après. Résultat par stratégie si on n'achète QUE ce qui est servi, et si on achète l'inverse quand on est servi.</div><table><tr><th>Stratégie</th><th>Essais</th><th>Gagnants (tous)</th><th>Servis 50 ms</th><th>Gagnants si servi</th><th>Gagnants si PAS servi</th><th>Résultat servi 50 ms</th><th>Résultat servi 250 ms</th><th>Résultat « inverse »</th><th>Résultat si tout servi (simulation)</th></tr>"+Object.entries(OR).sort().map(([k,z])=>"<tr><td>"+k+"</td><td>"+z.essais+"</td><td>"+z.gagnants+"</td><td>"+z.s50+" ("+(z.essais?Math.round(100*z.s50/z.essais):0)+" %)</td><td>"+z.g50+" / "+z.s50+"</td><td>"+z.nonServisGagnants+" / "+z.nonServis+"</td><td>"+f(z.pnl50)+"</td><td>"+f(z.pnl250)+"</td><td>"+f(z.inv50)+"</td><td>"+f(z.pnlParfait)+"</td></tr>").join("")+"</table></div>";}
const MO=d.markout||{};if(Object.keys(MO).length){h+="<div class='card'><h2>Teneur de marché : valeur juste après avoir été servi (cents par part)</h2><div class='mu'>Positif = le prix est monté après notre achat (bon remplissage). Négatif = on a été servi juste avant une baisse (sélection adverse).</div><table><tr><th>Stratégie</th><th>Remplissages</th><th>0,1 s</th><th>0,5 s</th><th>1 s</th><th>3 s</th><th>10 s</th></tr>"+Object.entries(MO).map(([k,v])=>"<tr><td>"+k+"</td><td>"+v.remplissages+"</td>"+["0.1s","0.5s","1s","3s","10s"].map(x=>"<td>"+(v[x]==null?"—":v[x])+"</td>").join("")+"</tr>").join("")+"</table></div>";}
const AU=d.audit||[];if(AU.length){const ok=AU.filter(x=>x.ptb&&x.notreDebut);h+="<div class='card'><h2>Audit de la règle de résolution</h2><div class='mu'>Notre moyenne Chainlink 60 s contre le prix à battre et le prix final officiels de Polymarket.</div><table><tr><th>Cycle</th><th>Crypto</th><th>Prix à battre officiel</th><th>Notre moyenne début</th><th>Final officiel</th><th>Notre moyenne fin</th><th>Gagnant</th></tr>"+AU.slice(0,20).map(x=>"<tr><td>"+new Date(x.start*1000).toLocaleTimeString("fr-CH")+"</td><td>"+x.a+"</td><td>"+x.ptb+"</td><td>"+x.notreDebut+" ("+x.nDebut+" s)</td><td>"+x.final+"</td><td>"+x.notreFin+" ("+x.nFin+" s)</td><td>"+x.gagnant+"</td></tr>").join("")+"</table></div>";}
const MQ=d.manquees||{};for(const a of ["BTC","ETH"]){const m=MQ[a];if(!m)continue;for(const [st,titre] of [["v1","V1 — quand le modèle donne ≥ 0,63"],["fin","Fin de cycle — quand le modèle est très sûr"]]){const o=m[st]||{},tot=o["secondes modèle OK"]||0;if(!tot)continue;h+="<div class='card'><h2>Occasions — "+titre+" — "+a+"</h2><table><tr><th>Ce qu'il y avait</th><th>Secondes / échanges</th><th>Part</th></tr>"+Object.entries(o).map(([k,v])=>"<tr><td>"+k+"</td><td>"+v+"</td><td>"+(k.startsWith("meilleure")?(100*v/tot).toFixed(1)+" %":"")+"</td></tr>").join("")+"</table></div>";}}
if(!cles.length)h+="<p>Aucun trade terminé pour l'instant.</p>";
for(const k of cles.filter(act)){const S=d.strats[k],st=k.slice(0,k.lastIndexOf(" ")),a=k.slice(k.lastIndexOf(" ")+1);h+="<div class='card' style='margin-top:12px'><h2><span class='badge' style='font-size:15px;font-weight:700;background:"+(a==="BTC"?"#f7931a":"#627eea")+";color:#fff'>"+a+"</span> "+(noms[st]||st)+"</h2><div class='mu' style='margin-bottom:6px'>"+expl(st)+"</div><div>Trades : <b>"+S.n+"</b> · gagnés "+S.gains+" · perdus "+S.pertes+" · résultat <b>"+fc(S.pnl)+"</b></div>"+(R[k]&&R[k].serieMax!=null?"<div>Pertes de suite : <b>"+R[k].serieMax+"</b> max, "+R[k].serie+" en cours</div><div class='mu'>Séries de pertes : "+ser(R[k].series)+"</div><div>Creux max <b class='ko'>"+f(R[k].creux)+"</b> · capital conseillé <b>"+R[k].capital+" $</b></div>":"")+"<div class='mu'>"+Object.entries(S.issues).map(([i,v])=>i+" : "+v.n+" ("+f(v.pnl)+")").join(" · ")+"</div>";
h+="<div style='margin-top:6px'>"+S.trades.slice(0,25).map(T=>"<div style='border-top:1px solid var(--bd);padding:6px 0'><b>"+new Date(T.heure).toLocaleTimeString("fr-CH")+"</b> · "+a+" · "+(T.cote||"Up "+(T.U||0).toFixed(0)+" / Down "+(T.D||0).toFixed(0))+" · "+T.issue+" · <b class='"+(T.net>=0?"ok":"ko")+"'>"+f(T.net)+"</b><div class='mu' style='font-size:12px'>"+T.journal.slice(-4).join(" · ")+"</div></div>").join("")+"</div></div>";}
if(d.ouvertes.length)h+="<div class='card' style='margin-top:12px'><h2>Positions ouvertes</h2>"+d.ouvertes.map(P=>"<div>"+(noms[P.strat]||P.strat)+" "+P.actif+" — "+P.journal.slice(-3).join(" · ")+"</div>").join("")+"</div>";
document.getElementById("app").innerHTML=h;}catch(e){document.getElementById("app").textContent="Erreur : "+e;}}
maj();setInterval(maj,5000);
</script></body></html>`;
const PAGE_N_V = (() => { let h = 5381; for (let i = 0; i < PAGE_N.length; i++) h = ((h * 33) ^ PAGE_N.charCodeAt(i)) >>> 0; return h.toString(36); })();
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
