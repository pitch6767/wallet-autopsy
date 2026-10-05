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
const V1 = { ACTIF: "BTC", MARGE: 0.08, PMIN: 0.55, PMAX: 0.56, OPP_MAX: 0.43, STOP_REL: 0.15, ELAN_S: 5, TP: 0.90, CAPITAL: 200, MISE: 50 };
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
    this.ready = this.state.blockConcurrencyWhile(async () => {
      this.e = (await this.state.storage.get("etat2")) || {
        capital: CFG.CAPITAL, mise: CFG.MISE, reserve: 0, pnl: 0, gains: 0, pertes: 0, pause: false,
        positions: [], attente: [], trades: [], vetos: {}, candidats: {}, parActif: {}, refus: [], verif: [], depuis: now(),
      };
      this.e.pause = false;   // plus de pause après perte (décision du 05.10.2026)
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
        derniers: this.polyRaw || [], proba: mb.up ? this.probaV1(mb) : null, sg: this._sg || null });
    }
    if (u.pathname === "/api/rapport") return json({ refus: this.e.refus });
    if (u.pathname === "/rapport") return new Response(RAPPORT, { headers: { "content-type": "text/html; charset=utf-8" } });
    return new Response(PAGE, { headers: { "content-type": "text/html; charset=utf-8" } });
  }

  demarrer() {
    this.ouvrirFlux();
    this.state.storage.getAlarm().then((a) => { if (!a || a < Date.now() - 5000) this.state.storage.setAlarm(Date.now() + 1000); });
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
    if (!this.ws.perp || (this.ageMax("perp") > 20 && depuis("perp") > 20)) {
      for (const a of LISTE) this.livre[a] = { b: new Map(), a: new Map() };
      const args = LISTE.flatMap((a) => [`publicTrade.${ACTIFS[a].bybit}`, `orderbook.50.${ACTIFS[a].bybit}`, `allLiquidation.${ACTIFS[a].bybit}`]);
      this.connecter("perp", "https://stream.bybit.com/v5/public/linear", [JSON.stringify({ op: "subscribe", args })], (m) => this.surPerp(m), JSON.stringify({ op: "ping" }), 10000);
    }
    if (!this.ws.cb || (this.ageMax("cb") > 30 && depuis("cb") > 30)) {
      const ids = LISTE.map((a) => ACTIFS[a].spot).filter(Boolean);
      this.connecter("cb", "https://advanced-trade-ws.coinbase.com", [JSON.stringify({ type: "subscribe", product_ids: ids, channel: "ticker" })], (m) => this.surCb(m));
    }
    const ageOkx = this.f.BTC.okx ? t - this.f.BTC.okx.t : 1e9;
    if (!this.ws.okx || (ageOkx > 20 && depuis("okx") > 20))
      this.connecter("okx", "https://ws.okx.com:8443/ws/v5/public", [JSON.stringify({ op: "subscribe", args: [{ channel: "trades", instId: "BTC-USDT-SWAP" }] })], (m) => {
        const ch = (m.arg || {}).channel, x = (m.data || []).slice(-1)[0];
        if (ch === "trades" && x) { const tt = now(); this.noter("BTC", "okx", +x.px, tt); if (tt - (this._v1t || 0) > 0.2) { this._v1t = tt; try { this.v1Eval("okx", +x.ts / 1000); } catch (err) { this.erreur("V1", err); } } }
      }, "ping", 20000);
    const mb = this.mk.BTC;
    const jetons = [];
    if (mb && mb.up) jetons.push(mb.up, mb.down);
    if (this.mkNext && this.mkNext.up && (!mb || this.mkNext.start > mb.start)) jetons.push(this.mkNext.up, this.mkNext.down);
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
      const x = (m.data || []).slice(-1)[0];
      if (x) { this.noter(a, "perp", +x.p, t); if (a === V1.ACTIF && t - (this._v1t || 0) > 0.2) { this._v1t = t; try { this.v1Eval("perp", +x.T / 1000); } catch (err) { this.erreur("V1", err); } } }
    }
    else if (tp.startsWith("allLiquidation")) {
      for (const x of m.data || []) this.liq[a].push({ t, cote: x.S === "Buy" ? "SELL" : "BUY", usd: (+x.v) * (+x.p) });   // Buy = position longue liquidée
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
        mk = this.mk[a] = (a === V1.ACTIF && this.mkNext && this.mkNext.start === start) ? { ...this.mkNext } : { start, end: start + 300 };
      }
      try {
        if (!mk.slug && t - (mk.essai || 0) > 10) { mk.essai = t; Object.assign(mk, await this.chargerMarche(a, start)); }
        if (!mk.strike && t - (mk.essaiOff || 0) > 15) { mk.essaiOff = t; await this.ouvertureOfficielle(a, mk); }
      } catch (err) { if (tleft < 200) this.erreur(a, err); }
    }));
    // V1 : préchargement du cycle BTC suivant (carnet en direct prêt dès la première seconde)
    const nx = start + 300;
    if (tleft < 150 && (!this.mkNext || this.mkNext.start !== nx) && t - (this._nxEssai || 0) > 10) {
      this._nxEssai = t;
      try { this.mkNext = { start: nx, end: nx + 300, ...(await this.chargerMarche(V1.ACTIF, nx)) }; } catch (_) {}
    }
    for (const p of this.e.positions.filter((x) => x.end <= t)) this.e.attente.push(p);
    this.e.positions = this.e.positions.filter((x) => x.end > t);
    await this.resoudre();
    if (t - (this._v1r || 0) > 15 || (this.e.V1.pos && t >= this.e.V1.pos.end)) { this._v1r = t; await this.v1Regler(); }
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
      for (const c of ch) { const L = livre(c.asset_id), cote = c.side === "BUY" ? L.bids : L.asks; +c.size ? cote.set(+c.price, +c.size) : cote.delete(+c.price); }
    } else if (ev === "last_trade_price") {
      this.v1Echange(m.asset_id, m.side, +m.price, +m.size);
    } else return;
    try { this.v1Eval("poly", ts || t); } catch (err) { this.erreur("V1", err); }
  }

  probaV1(mk) {
    const a = V1.ACTIF, K = mk.strike, perp = this.f[a].perp, cl = this.f[a].cl;
    if (!K || !perp || !cl) return null;
    const t = now();
    if (!this._sg || t - this._sg.t > 5) {
      const ser = this.serie(a, "perp", 300);
      if (ser.length < 60) return null;
      const r = []; for (let i = 1; i < ser.length; i++) r.push(Math.log(ser[i][1] / ser[i - 1][1]));
      const mo = r.reduce((x, y) => x + y, 0) / r.length;
      const base = med(this.serie(a, "perp", 120).map(([s2, p]) => { const c = this.prixA(a, "cl", s2); return c ? p - c : null; }).filter((x) => x != null));
      this._sg = { t, v: Math.sqrt(r.reduce((x, y) => x + (y - mo) ** 2, 0) / r.length) || 1e-6, base };
    }
    if (this._sg.base == null) return null;
    const S = this.prixRapide();                             // prix le plus récent (Bybit ou OKX), ramené au niveau Chainlink
    if (S == null) return null;
    const sg = this._sg.v, ts = Math.floor(t), deb = mk.end - 59;
    let E, v;
    if (ts >= deb) {
      const connus = []; for (let s2 = deb; s2 <= ts; s2++) { const x = this.prixA(a, "cl", s2); if (x) connus.push(x); }
      const nr = Math.max(1, mk.end - ts);
      E = (connus.reduce((x, y) => x + y, 0) + nr * S) / (connus.length + nr); v = (sg * S) ** 2 * nr ** 3 / 3 / 3600;
    } else { E = S; v = (sg * S) ** 2 * ((deb - ts) + 20); }
    return phi((E - K) / Math.sqrt(v + (CFG.SD_ECART_REL * S) ** 2));
  }

  prixRapide() {
    const a = V1.ACTIF, b = this.f[a].perp, o = this.f[a].okx;
    if (o && this._sgOkx == null || (o && now() - (this._sgOkxT || 0) > 5)) {
      this._sgOkxT = now();
      this._sgOkx = med(this.serie(a, "okx", 120).map(([s2, p]) => { const c = this.prixA(a, "cl", s2); return c ? p - c : null; }).filter((x) => x != null));
    }
    const cands = [];
    if (b && this._sg && this._sg.base != null) cands.push([b.t, b.p - this._sg.base, "bybit"]);
    if (o && this._sgOkx != null) cands.push([o.t, o.p - this._sgOkx, "okx"]);
    if (!cands.length) return null;
    cands.sort((x, y) => y[0] - x[0]);
    this.sourceRapide = cands[0][2]; (this.compteSource = this.compteSource || {})[cands[0][2]] = (this.compteSource[cands[0][2]] || 0) + 1;
    return cands[0][1];
  }

  // élan : variation du prix rapide sur les 5 dernières secondes (positif = hausse)
  elanV1() {
    const a = V1.ACTIF, ts = Math.floor(now());
    const p0 = this.prixA(a, "perp", ts), p5 = this.prixA(a, "perp", ts - V1.ELAN_S);
    const o0 = this.prixA(a, "okx", ts), o5 = this.prixA(a, "okx", ts - V1.ELAN_S);
    if (o0 && o5 && this.sourceRapide === "okx") return o0 - o5;
    return p0 && p5 ? p0 - p5 : null;
  }

  livreTrie(id, cote) { const L = this.pb[id]; if (!L) return []; return [...L[cote]].filter((x) => x[1] > 0).sort((x, y) => (cote === "asks" ? x[0] - y[0] : y[0] - x[0])); }

  v1Eval(source, tsSource) {
    const V = this.e.V1, mk = this.mk[V1.ACTIF];
    if (!V || !mk || !mk.up || !mk.strike) return;
    const t = now();
    if (t < mk.start || t > mk.end - 1) return;
    const pu = this.probaV1(mk);
    if (pu == null) return;
    const delai = tsSource ? t - tsSource : null;
    let pos = V.pos && V.pos.start === mk.start && !V.pos.fini ? V.pos : null;
    if (!pos) {
      if (V.dernierCycle === mk.start) return;            // une seule entrée par cycle
      for (const up of [true, false]) {
        const id = up ? mk.up : mk.down, asks = this.livreTrie(id, "asks"), fair = up ? pu : 1 - pu;
        if (!asks.length || asks[0][0] < V1.PMIN || asks[0][0] > V1.PMAX || fair < V1.PMIN + V1.MARGE) continue;
        const el = this.elanV1(); if (el == null || el * (up ? 1 : -1) <= 0) { V.refusElan = (V.refusElan || 0) + 1; continue; }
        const mise = Math.min(V.mise, V.capital - V.reserve);
        let reste = mise, parts = 0, cout = 0;
        for (const [p, sz] of asks) { if (p > V1.PMAX) break; const k = Math.min(sz, reste / p); parts += k; cout += k * p; reste -= k * p; if (reste < 0.01) break; }
        if (reste >= 0.01 || parts <= 0) continue;
        const pm = cout / parts;
        V.dernierCycle = mk.start; V.entrees++;
        V.pos = { start: mk.start, end: mk.end, slug: mk.slug, cote: up ? "Up" : "Down", token: id, autre: up ? mk.down : mk.up, prix: +pm.toFixed(4), parts: +parts.toFixed(2),
          mise: +cout.toFixed(2), frais: +(parts * CFG.FEE_RATE * pm * (1 - pm)).toFixed(3), proba: +fair.toFixed(3), heure: new Date().toISOString(),
          delai: delai != null ? +delai.toFixed(3) : null, source, B: { parts: 0, cout: 0 }, offre: null };
        this.notelat(delai); this.sauver();
        return;
      }
      return;
    }
    const up = pos.cote === "Up", fairA = up ? pu : 1 - pu;
    pos.offre = Math.min(Math.floor(((1 - fairA) - V1.MARGE) * 100) / 100, V1.OPP_MAX);
    pos.probaActuelle = +fairA.toFixed(3);
    const bids = this.livreTrie(pos.token, "bids");
    if (fairA < pos.proba - V1.STOP_REL) { this.v1Vendre(pos, bids, "stop", delai); return; }
    if (pos.B.parts < 1e-9 && bids.length && bids[0][0] >= V1.TP) this.v1Vendre(pos, bids, "sortie 90", delai);
  }

  // un vendeur de l'autre côté passe au moins 1 cent sous notre offre => offre servie (version prudente)
  v1Echange(id, side, p, size) {
    const V = this.e.V1, pos = V && V.pos;
    if (!pos || pos.fini || pos.offre == null || pos.offre < 0.02) return;
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
    const V = this.e.V1;
    pos.fini = true; pos.issue = issue;
    pos.net = +(paires + produit - pos.mise - pos.B.cout - pos.frais).toFixed(2);
    V.capital += pos.net; V.pnl += pos.net;
    (V.issues[issue] = V.issues[issue] || { n: 0, pnl: 0 }).n++; V.issues[issue].pnl += pos.net;
    if (pos.net >= 0) { V.gains++; V.reserve += pos.net * CFG.PART_RESERVE; V.mise += pos.net * CFG.PART_REINVEST; } else V.pertes++;
    V.mise = Math.min(V.mise, Math.max(0, V.capital - V.reserve));
    V.trades.unshift(pos); V.trades.length = Math.min(V.trades.length, 300);
    V.pos = null;
  }

  notelat(d) { if (d == null) return; this.latDec.push(d); if (this.latDec.length > 200) this.latDec.shift(); }

  async v1Regler() {
    const V = this.e.V1, t = now();
    if (V.pos && t >= V.pos.end && !V.pos.fini) { V.attente.push(V.pos); V.pos = null; }
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
          polyOk: !!this.ws.poly, sources: this.compteSource || {}, okxOk: !!this.ws.okx, livre: this.mk.BTC && this.mk.BTC.up ? { up: (this.livreTrie(this.mk.BTC.up, "asks")[0] || [null])[0], down: (this.livreTrie(this.mk.BTC.down, "asks")[0] || [null])[0] } : null };
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
<div style="margin-top:8px"><a href="/rapport">→ Rapport détaillé des refus</a></div>
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
return '<div class=card><b>V1 — paires BTC (jambe 55 filtrée)</b> <span class=mu>temps réel'+(V.polyOk?'':' — <span class=ko>carnet en direct déconnecté</span>')+'</span><div class=g style="margin-top:8px"><div><div class=k>Capital</div><div class=v>'+f(V.capital)+' $</div></div><div><div class=k>Gain</div><div class="v '+(V.pnl>=0?'ok':'ko')+'">'+usd(V.pnl)+'</div></div><div><div class=k>Gagnés / perdus</div><div class=v><span class=ok>'+V.gains+'</span> / <span class=ko>'+V.pertes+'</span></div></div></div>'+
'<div class=mu style="margin-top:6px">Réglage A : élan 5 s + stop à −15 points · entrées refusées par l\'élan : '+(V.refusElan||0)+' · source la plus rapide : '+Object.entries(V.sources||{}).map(([k,n])=>k+' '+n).join(', ')+'</div><div class=mu>Issues : '+it+'</div><div class=mu>Réaction : message Polymarket reçu en '+f(V.latPolyMed,3)+' s (90 % sous '+f(V.latPolyP90,3)+' s) · décisions en '+f(V.latDecMed,3)+' s (90 % sous '+f(V.latDecP90,3)+' s)</div>'+p+
'<table style="margin-top:8px"><tr><th>Heure UTC</th><th>Jambe</th><th>Prix</th><th>Proba</th><th>Autre jambe</th><th>Issue</th><th>Net</th></tr>'+tv+'</table></div>'})()+
'<div class=card><b>Par crypto</b><table><tr><th>Crypto</th><th>Candidats</th><th>Trades</th><th>Gagnés</th><th>Perdus</th><th>Gain</th><th>Refus le plus fréquent</th></tr>'+pa+'</table></div>'+
'<div class=card><b>Trades</b><table><tr><th>Heure UTC</th><th>Crypto</th><th>Côté</th><th>Prix</th><th>z</th><th>Résultat</th><th>Net</th></tr>'+tr+'</table></div>'+
'<div class=card><b>Flux</b> <span class=mu>(prix et âge de la dernière mise à jour)</span><table><tr><th>Crypto</th><th>Chainlink</th><th>Perp Bybit</th><th>Spot Coinbase</th><th>Prix d\\'exercice</th></tr>'+fl+'</table></div>'+
(d.diag.erreurs.length?'<div class=card><b>Journal technique</b><div class=mu>'+d.diag.erreurs.join('<br>')+'</div></div>':'');
}catch(err){$('#app').textContent='Erreur de chargement : '+err}}
go();setInterval(go,3000);
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
