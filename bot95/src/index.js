// bot95 — paris quasi sûrs dans les 30 dernières secondes des marchés BTC 5 min de Polymarket.
// MODE FANTÔME : aucun ordre réel, aucune clé. Le bot note ce qu'il aurait fait.

const CFG = {
  FENETRE: 30,                 // s avant la fin
  PRIX_MIN: 0.95, PRIX_MAX: 0.99,
  Z_MIN_HAUT: 1.5,             // distance mini (écarts-types) si prix >= 0,97 (option A validée : 1,5)
  Z_MIN_BAS: 3.0,              // distance mini si prix < 0,97 (on risque plus)
  MARGE_MODELE: 0.01,          // proba calculée >= prix + 1 pt
  COURSE_FACTEUR: 2,           // temps pour atteindre le strike > 2 x temps restant
  FRAICHEUR_S: 5,              // une source plus vieille que 5 s = pas de trade (validé le 04.10.2026)
  ECART_MAX: 0.02,             // écart achat/vente maxi
  LIQ_CONTRE_USD: 250000,      // liquidations contre nous sur 10 s
  DESEQ_CONTRE: 0.6,           // déséquilibre carnet perp contre nous (top 5)
  SORTIE_Z: 1.0,               // sortie d'urgence si la distance passe sous 1 écart-type
  FEE_RATE: 0.072,             // frais taker : parts x 0,072 x p x (1-p)
  B_PRIX_MIN: 0.94,            // option B : offre d'achat posée entre 0,94 et 0,99
  CAPITAL: 200, MISE: 50, PART_REINVEST: 1 / 3, PART_RESERVE: 2 / 3,
  // annonces : jours ouvrés, heures UTC [début, fin] en minutes
  ANNONCES: [[12 * 60 + 28, 12 * 60 + 40], [13 * 60 + 58, 14 * 60 + 10], [17 * 60 + 58, 18 * 60 + 10]],
};

const G = "https://gamma-api.polymarket.com";
const C = "https://clob.polymarket.com";
const D = "https://data-api.polymarket.com";
const TOP_N = 10;            // nombre de gros traders suivis
const MEMOIRE_MARCHES = 12;  // volume calculé sur les 12 derniers marchés (1 h)

export default {
  async fetch(req, env) {
    return stub(env).fetch(req);
  },
  async scheduled(_e, env, ctx) {
    ctx.waitUntil(stub(env).fetch("https://bot95/api/reveil"));
  },
};
const stub = (env) => env.BOT.get(env.BOT.idFromName("bot95"), { locationHint: "weur" });

const phi = (x) => 0.5 * (1 + erf(x / Math.SQRT2));
function erf(x) {
  const s = Math.sign(x); x = Math.abs(x);
  const t = 1 / (1 + 0.3275911 * x);
  const y = 1 - (((((1.061405429 * t - 1.453152027) * t) + 1.421413741) * t - 0.284496736) * t + 0.254829592) * t * Math.exp(-x * x);
  return s * y;
}
const med = (a) => { if (!a.length) return null; const b = [...a].sort((x, y) => x - y); return b[Math.floor(b.length / 2)]; };
const now = () => Date.now() / 1000;

export class Bot {
  constructor(state, env) {
    this.state = state; this.env = env;
    this.f = { perp: null, cb: null, cl: null };          // {p, t}
    this.sec = new Map();                                  // seconde -> {perp, cb, cl}
    this.liq = [];                                         // {t, cote, usd}
    this.deseq = 0;                                        // (bids - asks) / total, top 5 perp
    this.ws = {};
    this.mkt = null;
    this.diag = { reconnexions: {}, erreurs: [] };
    this.vol = [];          // [{start, parWallet:{w:usd}}] des derniers marchés
    this.vus = new Set();   // trades déjà traités
    this.gros = { liste: [], positions: {}, evenements: [], dernierPoll: 0 };
    this.ready = this.state.blockConcurrencyWhile(async () => {
      this.e = (await this.state.storage.get("etat")) || {
        capital: CFG.CAPITAL, mise: CFG.MISE, reserve: 0, pnl: 0, gains: 0, pertes: 0,
        pause: false, position: null, attente: [], trades: [], vetos: {}, fenetres: 0, depuis: now(),
      };
      if (!this.e.B) this.e.B = { capital: CFG.CAPITAL, mise: CFG.MISE, reserve: 0, pnl: 0, gains: 0, pertes: 0, pause: false, position: null, vetos: {}, offres: 0, remplies: 0 };
    });
  }

  // ------------------------------------------------------------------ HTTP
  async fetch(req) {
    await this.ready;
    this.demarrer();
    const u = new URL(req.url);
    if (u.pathname === "/api/etat") return Response.json(this.vue(), { headers: { "cache-control": "no-store" } });
    if (u.pathname === "/api/reprendre" && req.method === "POST") {
      if (u.searchParams.get("s") === "B") this.e.B.pause = false; else this.e.pause = false;
      await this.sauver();
      return Response.json({ ok: true });
    }
    if (u.pathname === "/api/reveil") return Response.json({ ok: true });
    if (u.pathname === "/api/verif") return Response.json({ verif: this.e.verif || [] }, { headers: { "cache-control": "no-store" } });
    if (u.pathname === "/api/rapport") return Response.json({ rapport: this.e.rapport || [], encours: this.mkt ? { slug: this.mkt.slug, refus: this.mkt.refus || null, comptes: this.mkt.comptes || null } : null }, { headers: { "cache-control": "no-store" } });
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
    this.diag.erreurs.unshift(`${new Date().toISOString().slice(11, 19)} ${ou}: ${String(err && err.message || err).slice(0, 140)}`);
    this.diag.erreurs.length = Math.min(this.diag.erreurs.length, 15);
  }
  async sauver() { await this.state.storage.put("etat", this.e); }

  // ------------------------------------------------------------------ flux
  ouvrirFlux() {
    const t = now();
    const age = (k) => (this.f[k] ? t - this.f[k].t : 1e9);
    const depuis = (k) => t - (this.ws[k + "_ouvert"] || 0);
    // perp : Binance, sinon Bybit, sinon OKX (bascule si rien reçu en 15 s)
    if (!this.ws.perp || (age("perp") > 15 && depuis("perp") > 15)) {
      const srcs = ["binance", "bybit", "okx"];
      if (this.ws.perp_ouvert && age("perp") > 15) this.perpIdx = ((this.perpIdx || 0) + 1) % srcs.length;
      this.perpSrc = srcs[this.perpIdx || 0];
      const P = {
        binance: ["https://fstream.binance.com/stream?streams=btcusdt@aggTrade/btcusdt@forceOrder/btcusdt@depth5@100ms", null, null],
        bybit: ["https://stream.bybit.com/v5/public/linear", JSON.stringify({ op: "subscribe", args: ["publicTrade.BTCUSDT", "orderbook.50.BTCUSDT", "allLiquidation.BTCUSDT"] }), JSON.stringify({ op: "ping" })],
        okx: ["https://ws.okx.com:8443/ws/v5/public", JSON.stringify({ op: "subscribe", args: [{ channel: "trades", instId: "BTC-USDT-SWAP" }, { channel: "books5", instId: "BTC-USDT-SWAP" }, { channel: "liquidation-orders", instType: "SWAP" }] }), "ping"],
      }[this.perpSrc];
      this.livre = { b: new Map(), a: new Map() };
      this.connecter("perp", P[0], P[1], (m) => this.surPerp(m), P[2], 20000);
    }
    // deuxième source spot : Coinbase (Advanced Trade), sinon Coinbase Exchange, sinon Kraken
    if (!this.ws.cb || (age("cb") > 30 && depuis("cb") > 30)) {
      const srcs = ["coinbase", "coinbase-ex", "kraken"];
      if (this.ws.cb_ouvert && age("cb") > 30) this.cbIdx = ((this.cbIdx || 0) + 1) % srcs.length;
      this.cbSrc = srcs[this.cbIdx || 0];
      const P = {
        coinbase: ["https://advanced-trade-ws.coinbase.com", JSON.stringify({ type: "subscribe", product_ids: ["BTC-USD"], channel: "ticker" })],
        "coinbase-ex": ["https://ws-feed.exchange.coinbase.com", JSON.stringify({ type: "subscribe", channels: [{ name: "ticker", product_ids: ["BTC-USD"] }] })],
        kraken: ["https://ws.kraken.com/v2", JSON.stringify({ method: "subscribe", params: { channel: "ticker", symbol: ["BTC/USD"], event_trigger: "trades" } })],
      }[this.cbSrc];
      this.connecter("cb", P[0], P[1], (m) => this.surCb(m));
    }
    if (!this.ws.cl || (age("cl") > 15 && depuis("cl") > 15)) this.connecter("cl", "https://ws-live-data.polymarket.com",
      JSON.stringify({ action: "subscribe", subscriptions: [{ topic: "crypto_prices_chainlink", type: "*", filters: "" }] }), (m) => this.surCl(m), "PING", 5000);
  }

  async connecter(nom, url, abonnement, surMsg, ping, periode) {
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
      ws.addEventListener("close", fin); ws.addEventListener("error", fin);
      if (abonnement) ws.send(abonnement);
      if (ping) ws.pinger = setInterval(() => { try { ws.send(ping); } catch (_) { clearInterval(ws.pinger); } }, periode || 5000);
      ws.addEventListener("close", (ev) => { clearInterval(ws.pinger); this.erreur("flux " + nom + " fermé", "code " + ev.code + " " + (ev.reason || "")); });
      this.ws[nom] = ws; this.ws[nom + "_ouvert"] = now();
      this.diag.reconnexions[nom] = (this.diag.reconnexions[nom] || 0) + 1;
    } catch (err) {
      this.erreur("flux " + nom + (nom === "perp" ? " " + this.perpSrc : nom === "cb" ? " " + this.cbSrc : ""), err);
      if (nom === "perp") this.perpIdx = ((this.perpIdx || 0) + 1) % 3;   // essayer la source suivante
      if (nom === "cb") this.cbIdx = ((this.cbIdx || 0) + 1) % 3;
    }
    this.ws[nom + "_en_cours"] = false;
  }

  noter(k, p, t) {
    this.f[k] = { p, t };
    const s = Math.floor(t);
    let o = this.sec.get(s);
    if (!o) { o = {}; this.sec.set(s, o); if (this.sec.size > 700) this.sec.delete(this.sec.keys().next().value); }
    o[k] = p;
  }

  surPerp(m) {
    const t = now();
    const liq = (cote, usd) => { this.liq.push({ t, cote, usd }); this.liq = this.liq.filter((x) => x.t > t - 30); };
    const deseq = (bids, asks) => {
      const b = bids.slice(0, 5).reduce((s, x) => s + +x[1], 0), a = asks.slice(0, 5).reduce((s, x) => s + +x[1], 0);
      if (a + b > 0) this.deseq = (b - a) / (a + b);
    };
    if (this.perpSrc === "binance") {
      const d = m.data || m, st = m.stream || "";
      if (st.includes("aggTrade")) this.noter("perp", +d.p, t);
      else if (st.includes("forceOrder")) { const o = d.o || {}; liq(o.S, (+o.q) * (+o.ap)); }  // SELL = longs liquidés
      else if (st.includes("depth")) deseq(d.b || [], d.a || []);
    } else if (this.perpSrc === "bybit") {
      const tp = m.topic || "";
      if (tp.startsWith("publicTrade")) { const x = (m.data || []).slice(-1)[0]; if (x) this.noter("perp", +x.p, t); }
      else if (tp.startsWith("allLiquidation")) for (const x of m.data || []) liq(x.S === "Buy" ? "SELL" : "BUY", (+x.v) * (+x.p)); // Buy = long liquidé
      else if (tp.startsWith("orderbook")) {
        const d = m.data || {};
        if (m.type === "snapshot") this.livre = { b: new Map(), a: new Map() };
        for (const [p, q] of d.b || []) +q ? this.livre.b.set(p, +q) : this.livre.b.delete(p);
        for (const [p, q] of d.a || []) +q ? this.livre.a.set(p, +q) : this.livre.a.delete(p);
        // retirer les niveaux périmés (croisés avec le dernier prix échangé)
        const px = this.f.perp ? this.f.perp.p : null;
        if (px) { for (const k of [...this.livre.b.keys()]) if (+k > px + 1) this.livre.b.delete(k); for (const k of [...this.livre.a.keys()]) if (+k < px - 1) this.livre.a.delete(k); }
        deseq([...this.livre.b].sort((x, y) => y[0] - x[0]), [...this.livre.a].sort((x, y) => x[0] - y[0]));
      }
    } else if (this.perpSrc === "okx") {
      const ch = (m.arg || {}).channel;
      if (ch === "trades") { const x = (m.data || []).slice(-1)[0]; if (x) this.noter("perp", +x.px, t); }
      else if (ch === "books5") { const d = (m.data || [])[0]; if (d) deseq(d.bids || [], d.asks || []); }
      else if (ch === "liquidation-orders") for (const d of m.data || []) if (d.instId === "BTC-USDT-SWAP")
        for (const x of d.details || []) liq(x.posSide === "long" || x.side === "sell" ? "SELL" : "BUY", (+x.sz) * 100 * 0.0001 * (+x.bkPx)); // 1 contrat = 0,01 BTC
    }
  }
  surCb(m) {
    const t = now();
    if (this.cbSrc === "coinbase" && m.channel === "ticker") { for (const ev of m.events || []) for (const x of ev.tickers || []) if (x.price) this.noter("cb", +x.price, t); }
    else if (this.cbSrc === "coinbase-ex" && m.type === "ticker" && m.price) this.noter("cb", +m.price, t);
    else if (this.cbSrc === "kraken" && m.channel === "ticker") { const x = (m.data || [])[0]; if (x && x.last) this.noter("cb", +x.last, t); }
  }
  surCl(m) {
    if (m.topic !== "crypto_prices_chainlink") return;
    const p = m.payload || {};
    if ((p.symbol || "").toLowerCase() !== "btc/usd" || !(+p.value > 0)) return;
    this.noter("cl", +p.value, now());
    const ts = (+p.timestamp || Date.now()) / 1000, debut = Math.floor(ts / 300) * 300;
    if (this.mkt && this.mkt.start === debut && !this.mkt.ouvCl) this.mkt.ouvCl = +p.value;
  }

  serie(k, n) {   // dernières n valeurs par seconde (remplissage avec la précédente)
    const t = Math.floor(now()), out = []; let last = null;
    for (let s = t - n; s <= t; s++) { const o = this.sec.get(s); if (o && o[k] != null) last = o[k]; if (last != null) out.push([s, last]); }
    return out;
  }
  prixA(k, s) { for (let i = 0; i < 6; i++) { const o = this.sec.get(s - i); if (o && o[k] != null) return o[k]; } return null; }

  // ------------------------------------------------------------------ marché
  async chargerMarche(start) {
    const ev = await (await fetch(`${G}/events?slug=btc-updown-5m-${start}`)).json();
    const e = ev && ev[0], m = e && e.markets && e.markets[0];
    if (!m) throw new Error("marché introuvable " + start);
    const outs = JSON.parse(m.outcomes || "[]"), toks = JSON.parse(m.clobTokenIds || "[]");
    let meta = e.eventMetadata || m.eventMetadata || {};
    if (typeof meta === "string") try { meta = JSON.parse(meta); } catch (_) { meta = {}; }
    const iUp = outs.findIndex((o) => String(o).toLowerCase() === "up");
    return { start, end: start + 300, slug: e.slug, cid: m.conditionId, up: toks[iUp], down: toks[1 - iUp], strike: meta.priceToBeat ? +meta.priceToBeat : null };
  }

  async carnet(token) {
    const b = await (await fetch(`${C}/book?token_id=${token}`)).json();
    const asks = (b.asks || []).map((x) => [+x.price, +x.size]).sort((x, y) => x[0] - y[0]);
    const bids = (b.bids || []).map((x) => [+x.price, +x.size]).sort((x, y) => y[0] - x[0]);
    return { asks, bids };
  }

  // ------------------------------------------------------------------ boucle
  async tick() {
    const t = now(), start = Math.floor(t / 300) * 300, tleft = start + 300 - t;
    if (!this.mkt || this.mkt.start !== start) {
      if (this.mkt) this.finFenetre();
      this.mkt = { start, end: start + 300, charge: false, raison: null, candidat: false };
      this.vol.push({ start, parWallet: {} }); if (this.vol.length > MEMOIRE_MARCHES) this.vol.shift();
      this.gros.positions = {}; this.vus = new Set();
    }
    if (!this.mkt.charge || (!this.mkt.strike && tleft < 45 && !this.mkt.essai45)) {
      if (tleft < 45) this.mkt.essai45 = true;
      try { Object.assign(this.mkt, await this.chargerMarche(start), { charge: true }); } catch (err) { if (tleft < 40) this.erreur("marché", err); }
    }
    await this.resoudre();
    try { await this.suivreGros(tleft); } catch (err) { this.erreur("gros traders", err); }
    const pos = this.e.position, posB = this.e.B.position;
    if (pos && pos.start === start) await this.surveiller(pos, tleft);
    if (posB && posB.start === start) await this.surveiller(posB, tleft);
    if (tleft <= CFG.FENETRE && tleft >= 1 && this.mkt.charge && (!this.mkt.entre || !this.mkt.entreB)) await this.decider(tleft);
    if (this.mkt.offre) try { await this.remplirOffre(); } catch (err) { this.erreur("offre B", err); }
    if (tleft < 1 && this.mkt.offre) this.figerOffre();
  }

  calcul(tleft, favUp) {
    const K = this.mkt.strike || this.mkt.ouvCl;
    const S = this.f.cl && this.f.cl.p;
    const perp = this.serie("perp", 300);
    if (!K || !S || perp.length < 60) return null;
    const r = [];
    for (let i = 1; i < perp.length; i++) r.push(Math.log(perp[i][1] / perp[i - 1][1]));
    const m = r.reduce((a, b) => a + b, 0) / r.length;
    const sg = Math.sqrt(r.reduce((a, b) => a + (b - m) ** 2, 0) / r.length) || 1e-6;
    const dir = favUp ? 1 : -1;
    const z = (Math.log(S / K) * dir) / (sg * Math.sqrt(Math.max(tleft, 1)));
    const ts = Math.floor(now());
    const p0 = this.prixA("perp", ts), p5 = this.prixA("perp", ts - 5);
    const v = p0 && p5 ? ((p0 - p5) / 5) * dir : 0;          // $/s, négatif = vers le strike
    const dist = (S - K) * dir;
    // base perp/coinbase vs chainlink (médiane 120 s)
    const base = (k) => med(this.serie(k, 120).map(([s, p]) => { const c = this.prixA("cl", s); return c ? p - c : null; }).filter((x) => x != null));
    const bp = base("perp"), bc = base("cb");
    const cote = (p, b) => (p == null || b == null ? null : ((p - b - K) * dir > 0));
    return {
      K, S, z, proba: phi(z), dist, v, tStrike: v < 0 ? dist / -v : 999, sg,
      accordPerp: cote(this.f.perp && this.f.perp.p, bp), accordCb: cote(this.f.cb && this.f.cb.p, bc),
    };
  }

  // contrôles communs ; renvoie la raison du refus ou null
  protections(tleft, favUp, prix, c) {
    const t = now(), age = (k) => (this.f[k] ? t - this.f[k].t : 1e9), r1 = (x) => Math.round(x * 10) / 10;
    const X = (txt) => { this._expl = txt; };
    this._expl = "";
    const ages = { Chainlink: age("cl"), "perp": age("perp"), "spot": age("cb") };
    const vieilles = Object.entries(ages).filter(([, a]) => a > CFG.FRAICHEUR_S);
    if (vieilles.length) { X(vieilles.map(([k, a]) => `${k} sans nouveau prix depuis ${a > 1e8 ? "toujours" : r1(a) + " s"}`).join(", ") + ` (maximum autorisé ${CFG.FRAICHEUR_S} s).`); return "source figée ou absente"; }
    const minute = new Date().getUTCHours() * 60 + new Date().getUTCMinutes(), jour = new Date().getUTCDay();
    if (jour >= 1 && jour <= 5 && CFG.ANNONCES.some(([a, b]) => minute >= a && minute <= b)) { X("Créneau d'annonce économique américaine (jours ouvrés, 12h28-12h40, 13h58-14h10 ou 17h58-18h10 UTC)."); return "annonce économique"; }
    if (!c) { X("Pas encore assez d'historique de prix (5 minutes de perp ou prix d'exercice manquants)."); return "données insuffisantes"; }
    if (c.accordPerp !== true || c.accordCb !== true) {
      const cote = favUp ? "au-dessus" : "en dessous";
      const k = [];
      if (c.accordPerp !== true) k.push("le perp (corrigé de son écart habituel avec Chainlink) " + (c.accordPerp == null ? "n'a pas d'écart mesurable" : "n'est pas " + cote));
      if (c.accordCb !== true) k.push("le spot (corrigé) " + (c.accordCb == null ? "n'a pas d'écart mesurable" : "n'est pas " + cote));
      X(`Chainlink est ${r1(Math.abs(c.dist))} $ ${cote} du prix d'exercice, mais ${k.join(" et ")}.`); return "sources pas d'accord";
    }
    const zmin = prix < 0.97 ? CFG.Z_MIN_BAS : CFG.Z_MIN_HAUT;
    if (c.z < zmin) { X(`BTC est à ${r1(c.dist)} $ du prix d'exercice, soit ${c.z.toFixed(2)} écart-type compte tenu de la volatilité et des ${Math.round(tleft)} s restantes ; il en faut au moins ${zmin} à un prix de ${prix}.`); return "distance trop faible"; }
    if (c.proba < prix + CFG.MARGE_MODELE) { X(`Probabilité calculée ${(c.proba * 100).toFixed(1)} % ; il faut au moins le prix + 1 point, soit ${((prix + CFG.MARGE_MODELE) * 100).toFixed(1)} %.`); return "modèle pas assez sûr"; }
    if (c.tStrike <= CFG.COURSE_FACTEUR * tleft) { X(`BTC se rapproche du prix d'exercice à ${r1(-c.v)} $/s : il l'atteindrait en ${r1(c.tStrike)} s, alors qu'il reste ${Math.round(tleft)} s (il faut plus du double).`); return "course vers le strike"; }
    const contre = this.liq.filter((x) => x.t > t - 10 && (favUp ? x.cote === "SELL" : x.cote === "BUY")).reduce((s, x) => s + x.usd, 0);
    if (contre >= CFG.LIQ_CONTRE_USD) { X(`${Math.round(contre).toLocaleString("fr-CH")} $ de liquidations contre le favori en 10 s (seuil ${CFG.LIQ_CONTRE_USD.toLocaleString("fr-CH")} $).`); return "liquidations contre nous"; }
    const dq = favUp ? -this.deseq : this.deseq;
    if (dq >= CFG.DESEQ_CONTRE) { X(`Le carnet du perp penche à ${Math.round(dq * 100)} % contre le favori sur les 5 premiers niveaux (seuil ${CFG.DESEQ_CONTRE * 100} %).`); return "carnet perp contre nous"; }
    return null;
  }

  // mémorise un refus détaillé pour le rapport
  noterRefus(strat, raison, extra) {
    const mk = this.mkt; if (!mk) return;
    mk.refus = mk.refus || {}; mk.comptes = mk.comptes || { A: {}, B: {} };
    mk.comptes[strat][raison] = (mk.comptes[strat][raison] || 0) + 1;
    mk.refus[strat] = { raison, explication: extra || this._expl || "", ...(mk.dernier || {}) };
  }

  async decider(tleft) {
    const mk = this.mkt, B = this.e.B;
    const [bu, bd] = await Promise.all([this.carnet(mk.up), this.carnet(mk.down)]);
    const askU = bu.asks[0] ? bu.asks[0][0] : 1, askD = bd.asks[0] ? bd.asks[0][0] : 1;
    const bidU = bu.bids[0] ? bu.bids[0][0] : 0, bidD = bd.bids[0] ? bd.bids[0][0] : 0;
    const favUp = bidU + (askU < 1 ? askU : bidU) >= bidD + (askD < 1 ? askD : bidD);   // favori = côté le plus cher
    const bk = favUp ? bu : bd, ask = favUp ? askU : askD, bid = favUp ? bidU : bidD;
    (this.diag.vus || (this.diag.vus = [])).unshift(mk.slug.slice(-10) + " T-" + Math.round(tleft) + " Up " + bidU + "/" + askU + " Down " + bidD + "/" + askD);
    this.diag.vus.length = Math.min(this.diag.vus.length, 35);
    const candA = !mk.entre && ask >= CFG.PRIX_MIN && ask <= CFG.PRIX_MAX;
    const tick = bid >= 0.96 ? 0.001 : 0.01;
    const prixB = +Math.min(CFG.PRIX_MAX, bid + tick).toFixed(3);
    const candB = !mk.entreB && bid >= CFG.B_PRIX_MIN && prixB <= CFG.PRIX_MAX;
    if (!candA && !candB) { this.annulerOffre(); return; }
    mk.candidat = true;
    const c = this.calcul(tleft, favUp);
    if (c) mk.dernier = { tleft: Math.round(tleft), ask, bid, fav: favUp ? "Up" : "Down", z: +c.z.toFixed(2), proba: +c.proba.toFixed(4), dist: +c.dist.toFixed(1) };

    // ---- option B : offre d'achat posée (fantôme : remplie si un vendeur frappe à notre prix)
    if (candB) {
      const r = B.pause ? "pause après perte (à reprendre)" : this.protections(tleft, favUp, prixB, c);
      if (r) { this.annulerOffre(); mk.raisonB = r; this.noterRefus("B", r); }
      else {
        const mise = Math.min(B.mise, B.capital - B.reserve);
        if (mise < 1) { this.annulerOffre(); mk.raisonB = "capital épuisé"; this.noterRefus("B", "capital épuisé", "Plus de capital disponible hors réserve."); }
        else if (!mk.offre || mk.offre.prix !== prixB || mk.offre.fav !== (favUp ? "Up" : "Down")) {
          const deja = mk.offre ? mk.offre.rempli : 0, cout = mk.offre ? mk.offre.cout : 0;
          if (!mk.offre) B.offres++;
          mk.offre = { prix: prixB, fav: favUp ? "Up" : "Down", token: favUp ? mk.up : mk.down, mise, rempli: deja, cout, depuis: now(),
            tleft: Math.round(tleft), z: c ? +c.z.toFixed(2) : null, proba: c ? +c.proba.toFixed(4) : null, dist: c ? +c.dist.toFixed(1) : null };
        }
      }
    }

    // ---- option A : achat immédiat au prix affiché
    if (!candA) {
      if (!mk.entre && bid >= CFG.PRIX_MIN) { mk.raison = "aucun vendeur à 0,99 ou moins"; this.noterRefus("A", mk.raison, `Le favori ${favUp ? "Up" : "Down"} n'a aucun vendeur entre ${CFG.PRIX_MIN} et ${CFG.PRIX_MAX} (meilleur vendeur : ${ask >= 1 ? "aucun" : ask}, meilleur acheteur : ${bid}).`); }
      return;
    }
    const refusA = (r, txt) => { this.veto(r); this.noterRefus("A", r, txt); };
    if (this.e.pause) return refusA("pause après perte (à reprendre)", "Une perte a eu lieu : le bot attend que tu cliques sur « Reprendre A ».");
    const r = this.protections(tleft, favUp, ask, c);
    if (r) return refusA(r);
    if (ask - bid > CFG.ECART_MAX) return refusA("écart achat/vente trop large", `Vendeur à ${ask}, acheteur à ${bid} : écart de ${(ask - bid).toFixed(3)}, maximum ${CFG.ECART_MAX}.`);
    const mise = Math.min(this.e.mise, this.e.capital - this.e.reserve);
    if (mise < 1) return refusA("capital épuisé", "Plus de capital disponible hors réserve.");
    let reste = mise, parts = 0, cout = 0;
    for (const [p, sz] of bk.asks) {
      if (p > CFG.PRIX_MAX) break;
      const prendre = Math.min(sz, reste / p);
      parts += prendre; cout += prendre * p; reste -= prendre * p;
      if (reste < 0.01) break;
    }
    if (reste >= 0.01) return refusA("pas assez de parts au prix", `Seulement ${parts.toFixed(1)} parts disponibles jusqu'à ${CFG.PRIX_MAX} pour une mise de ${mise.toFixed(2)} $ (achat « tout ou rien »).`);
    const pm = cout / parts;
    mk.entre = true;
    this.e.position = {
      strat: "A", start: mk.start, end: mk.end, slug: mk.slug, fav: favUp ? "Up" : "Down", token: favUp ? mk.up : mk.down,
      prix: +pm.toFixed(4), parts: +parts.toFixed(2), mise: +cout.toFixed(2), frais: +(parts * CFG.FEE_RATE * pm * (1 - pm)).toFixed(3),
      tleft: Math.round(tleft), z: +c.z.toFixed(2), proba: +c.proba.toFixed(4), dist: +c.dist.toFixed(1), heure: new Date().toISOString(),
    };
    await this.sauver();
  }

  annulerOffre() { const mk = this.mkt; if (mk && mk.offre && !mk.offre.rempli) mk.offre = null; else if (mk && mk.offre) this.figerOffre(); }

  // l'offre (partiellement) remplie devient la position B
  figerOffre() {
    const mk = this.mkt, o = mk && mk.offre;
    if (!o || !o.rempli) { if (mk) mk.offre = null; return; }
    mk.entreB = true; mk.offre = null;
    this.e.B.remplies++;
    this.e.B.position = {
      strat: "B", start: mk.start, end: mk.end, slug: mk.slug, fav: o.fav, token: o.token,
      prix: +(o.cout / o.rempli).toFixed(4), parts: +o.rempli.toFixed(2), mise: +o.cout.toFixed(2), frais: 0,
      tleft: o.tleft, z: o.z, proba: o.proba, dist: o.dist, heure: new Date().toISOString(),
    };
    this.sauver();
  }

  // remplissage fantôme : un vendeur (taker) du favori à un prix <= notre offre
  async remplirOffre() {
    const mk = this.mkt, o = mk && mk.offre;
    if (!o || !mk.cid) return;
    const lot = await (await fetch(`${D}/trades?market=${mk.cid}&limit=200&takerOnly=true`)).json();
    if (!Array.isArray(lot)) return;
    this.vusB = this.vusB || new Set();
    for (const x of lot) {
      const cle = (x.transactionHash || "") + x.asset + x.side + x.size;
      if (this.vusB.has(cle)) continue;
      this.vusB.add(cle);
      if (+x.timestamp < o.depuis - 1 || x.side !== "SELL" || String(x.outcome) !== o.fav || +x.price > o.prix) continue;
      const voulu = o.mise / o.prix - o.rempli;
      if (voulu <= 0) break;
      const v = Math.min(+x.size, voulu);
      o.rempli += v; o.cout += v * o.prix;
    }
    if (o.rempli >= o.mise / o.prix - 0.01) this.figerOffre();
  }

  veto(raison) { if (this.mkt) this.mkt.raison = raison; }

  // ---------------------------------------------- surveillance des gros traders du 5 min
  async suivreGros(tleft) {
    const mk = this.mkt, t = now();
    if (!mk || !mk.cid) return;
    const pas = tleft <= 60 ? 2 : 5;
    if (t - this.gros.dernierPoll < pas) return;
    this.gros.dernierPoll = t;
    const lot = await (await fetch(`${D}/trades?market=${mk.cid}&limit=500&takerOnly=false`)).json();
    if (!Array.isArray(lot)) return;
    const volMk = this.vol[this.vol.length - 1].parWallet;
    const nouveaux = [];
    for (const x of lot.slice().reverse()) {
      const cle = (x.transactionHash || "") + x.asset + x.side + x.size + x.proxyWallet;
      if (this.vus.has(cle)) continue;
      this.vus.add(cle);
      const w = x.proxyWallet; if (!w) continue;
      const usd = (+x.size) * (+x.price);
      volMk[w] = (volMk[w] || 0) + usd;
      const p = this.gros.positions[w] || (this.gros.positions[w] = { Up: 0, Down: 0, nom: x.pseudonym || x.name || "" });
      const issue = String(x.outcome) === "Up" ? "Up" : "Down";
      const avant = p[issue];
      p[issue] += x.side === "BUY" ? +x.size : -x.size;
      nouveaux.push({ w, issue, side: x.side, size: +x.size, prix: +x.price, usd, avant, t: +x.timestamp });
    }
    // classement : volume cumulé sur les derniers marchés
    const tot = {};
    for (const v of this.vol) for (const [w, u] of Object.entries(v.parWallet)) tot[w] = (tot[w] || 0) + u;
    this.gros.liste = Object.entries(tot).sort((a, b) => b[1] - a[1]).slice(0, TOP_N).map(([w, u]) => ({ w, vol: Math.round(u) }));
    const top = new Set(this.gros.liste.map((x) => x.w));
    for (const n of nouveaux) {
      if (!top.has(n.w)) continue;
      if (n.size < 1) continue;
      let type = null;
      if (n.side === "SELL" && n.avant > 0) type = "SORT (vend " + n.issue + ")";
      else if (n.side === "BUY") type = "achète " + n.issue;
      if (!type) continue;
      this.gros.evenements.unshift({ heure: new Date(n.t * 1000).toISOString().slice(11, 19), w: n.w, nom: (this.gros.positions[n.w] || {}).nom,
        type, parts: Math.round(n.size), prix: n.prix, reste: Math.round(mk.end - n.t), alerte: type.startsWith("SORT") });
    }
    this.gros.evenements.length = Math.min(this.gros.evenements.length, 40);
    // alerte si un gros trader sort du côté de notre position
    const pos = this.e.position;
    if (pos && pos.start === mk.start) {
      for (const n of nouveaux) if (top.has(n.w) && n.side === "SELL" && n.issue === pos.fav && n.avant > 0) pos.alerteGros = (pos.alerteGros || 0) + 1;
    }
  }

  finFenetre() {
    const mk = this.mkt;
    if (mk && mk.slug) {
      this.e.verif = this.e.verif || [];
      const s0 = mk.start, cl0 = this.prixA("cl", s0) , clF = this.prixA("cl", mk.end);
      this.e.verif.unshift({ start: s0, slug: mk.slug, kBot: mk.strike || mk.ouvCl || null, kSrc: mk.strike ? "polymarket au chargement" : "1er prix Chainlink reçu",
        clDebut: cl0, clFin: clF, perpFin: this.prixA("perp", mk.end), dernierBid: mk.dernier ? { fav: mk.dernier.fav, bid: mk.dernier.bid } : null, fait: false });
      this.e.verif.length = Math.min(this.e.verif.length, 100);
    }
    if (mk && mk.offre && !mk.offre.rempli) { mk.refus = mk.refus || {}; mk.comptes = mk.comptes || { A: {}, B: {} };
      mk.refus.B = { raison: "offre non remplie", explication: `Offre d'achat ${mk.offre.fav} à ${mk.offre.prix} posée, mais aucun vendeur n'a frappé à ce prix avant la fin.`, ...(mk.dernier || {}) }; }
    if (mk && mk.offre) this.figerOffre();
    if (mk && mk.candidat && (mk.refus && (mk.refus.A || mk.refus.B))) {
      this.e.rapport = this.e.rapport || [];
      this.e.rapport.unshift({ heure: new Date(mk.start * 1000).toISOString(), slug: mk.slug, strike: mk.strike || mk.ouvCl || null,
        A: mk.entre ? { raison: "acheté" } : (mk.refus.A || null), B: mk.entreB ? { raison: "offre remplie" } : (mk.refus.B || null), comptes: mk.comptes });
      this.e.rapport.length = Math.min(this.e.rapport.length, 300);
    }
    if (mk && mk.candidat && !mk.entre && mk.raison) {
      this.e.vetos[mk.raison] = (this.e.vetos[mk.raison] || 0) + 1;
    }
    if (mk && mk.candidat && !mk.entreB && mk.raisonB) this.e.B.vetos[mk.raisonB] = (this.e.B.vetos[mk.raisonB] || 0) + 1;
    const pb = this.e.B.position;
    if (pb && pb.start === (mk && mk.start)) { this.e.attente.push(pb); this.e.B.position = null; }
    if (mk && mk.candidat) this.e.fenetres++;
    const pos = this.e.position;
    if (pos && pos.start === (mk && mk.start)) { this.e.attente.push(pos); this.e.position = null; }
    this.sauver();
  }

  async surveiller(pos, tleft) {
    if (tleft < 1 || pos.sorti) return;
    const c = this.calcul(tleft, pos.fav === "Up");
    if (!c || c.z >= CFG.SORTIE_Z) return;
    const bk = await this.carnet(pos.token);
    let reste = pos.parts, recu = 0;
    for (const [p, s] of bk.bids) { const v = Math.min(s, reste); recu += v * p; reste -= v; if (reste <= 0) break; }
    if (reste > 0) return; // pas assez d'acheteurs : on garde
    const ps = recu / pos.parts;
    const fraisS = pos.parts * CFG.FEE_RATE * ps * (1 - ps);
    pos.sorti = { prix: +ps.toFixed(4), z: +c.z.toFixed(2), tleft: Math.round(tleft) };
    pos.net = +(recu - pos.mise - pos.frais - fraisS).toFixed(2);
    this.cloturer(pos, "sortie d'urgence");
    if (pos.strat === "B") this.e.B.position = null; else this.e.position = null;
    await this.sauver();
  }

  async resoudre() {
    const t = now();
    if ((!this.e.attente.length && !(this.e.verif || []).some((v) => !v.fait)) || (this.dernierCheck && t - this.dernierCheck < 15)) return;
    this.dernierCheck = t;
    const garder = [];
    for (const pos of this.e.attente) {
      if (t < pos.end + 20) { garder.push(pos); continue; }
      try {
        const ev = await (await fetch(`${G}/events?slug=${pos.slug}`)).json();
        const m = ev[0].markets[0];
        const px = JSON.parse(m.outcomePrices || "[]").map(Number), outs = JSON.parse(m.outcomes || "[]");
        if (px.sort().join() !== "0,1" && !(px.includes(1) && px.includes(0))) { garder.push(pos); continue; }
        const px2 = JSON.parse(m.outcomePrices).map(Number);
        const gagnant = outs[px2.indexOf(1)];
        const gagne = String(gagnant).toLowerCase() === pos.fav.toLowerCase();
        pos.net = +((gagne ? pos.parts - pos.mise : -pos.mise) - pos.frais).toFixed(2);
        this.cloturer(pos, gagne ? "gagné" : "perdu");
      } catch (err) { garder.push(pos); this.erreur("résolution", err); }
    }
    this.e.attente = garder;
    for (const v of (this.e.verif || []).filter((v) => !v.fait && t > v.start + 300 + 60).slice(0, 3)) {
      try {
        const ev = await (await fetch(`${G}/events?slug=${v.slug}`)).json();
        const e0 = ev[0], m = e0.markets[0];
        let meta = e0.eventMetadata || m.eventMetadata || {}; if (typeof meta === "string") meta = JSON.parse(meta);
        const px = JSON.parse(m.outcomePrices || "[]").map(Number), outs = JSON.parse(m.outcomes || "[]");
        if (!(px.includes(1) && px.includes(0)) || meta.priceToBeat == null) continue;
        v.kOfficiel = +meta.priceToBeat; v.finOfficiel = meta.finalPrice != null ? +meta.finalPrice : null;
        v.gagnant = outs[px.indexOf(1)];
        v.ecartK = v.kBot ? +(v.kBot - v.kOfficiel).toFixed(2) : null;
        v.ecartFin = v.clFin && v.finOfficiel ? +(v.clFin - v.finOfficiel).toFixed(2) : null;
        v.botAuraitDit = v.kBot && v.clFin ? (v.clFin >= v.kBot ? "Up" : "Down") : null;
        v.fait = true;
      } catch (err) { this.erreur("vérif", err); }
    }
    await this.sauver();
  }

  cloturer(pos, resultat) {
    const e = pos.strat === "B" ? this.e.B : this.e;
    pos.resultat = resultat;
    e.capital += pos.net; e.pnl += pos.net;
    if (pos.net >= 0) {
      e.gains++;
      e.reserve += pos.net * CFG.PART_RESERVE;
      e.mise += pos.net * CFG.PART_REINVEST;
    } else {
      e.pertes++;
      e.pause = true;                         // pause jusqu'à ta validation
    }
    e.mise = Math.min(e.mise, Math.max(0, e.capital - e.reserve));
    this.e.trades.unshift(pos);
    this.e.trades.length = Math.min(this.e.trades.length, 300);
  }

  vue() {
    const t = now(), age = (k) => (this.f[k] ? +(t - this.f[k].t).toFixed(1) : null);
    const mk = this.mkt || {};
    return {
      mode: "fantôme", e: { ...this.e, trades: this.e.trades.slice(0, 50) },
      flux: { perp: { p: this.f.perp && this.f.perp.p, age: age("perp"), src: this.perpSrc }, coinbase: { p: this.f.cb && this.f.cb.p, age: age("cb"), src: this.cbSrc },
        chainlink: { p: this.f.cl && this.f.cl.p, age: age("cl") }, deseq: +this.deseq.toFixed(2),
        liq10s: Math.round(this.liq.filter((x) => x.t > t - 10).reduce((s, x) => s + x.usd, 0)) },
      marche: { slug: mk.slug, strike: mk.strike || mk.ouvCl || null, reste: Math.round((mk.end || 0) - t), raison: mk.raison, raisonB: mk.raisonB, dernier: mk.dernier, entre: !!mk.entre, offre: mk.offre || null },
      gros: { liste: this.gros.liste.map((g) => ({ ...g, nom: (this.gros.positions[g.w] || {}).nom || "", Up: Math.round((this.gros.positions[g.w] || {}).Up || 0), Down: Math.round((this.gros.positions[g.w] || {}).Down || 0) })),
        evenements: this.gros.evenements.slice(0, 25) },
      regles: CFG, diag: this.diag,
    };
  }
}

const PAGE = `<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Bot 95</title><style>
:root{--bg:#f6f7f9;--card:#fff;--tx:#14171c;--mu:#667085;--bd:#e4e7ec;--ok:#12805c;--ko:#c0362c;--ac:#2f5bea}
@media (prefers-color-scheme:dark){:root{--bg:#0f1115;--card:#171a21;--tx:#e8eaee;--mu:#98a2b3;--bd:#262b35;--ok:#3ccf91;--ko:#f0705f;--ac:#7c9cff}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--tx);font:15px/1.45 -apple-system,system-ui,sans-serif;padding:16px;max-width:760px;margin:auto}
h1{font-size:20px;margin:0 0 4px}.mu{color:var(--mu);font-size:13px}.card{background:var(--card);border:1px solid var(--bd);border-radius:12px;padding:14px;margin:12px 0}
.g{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}.k{font-size:12px;color:var(--mu)}.v{font-size:20px;font-weight:600;font-variant-numeric:tabular-nums}
.ok{color:var(--ok)}.ko{color:var(--ko)}table{width:100%;border-collapse:collapse;font-size:13px;font-variant-numeric:tabular-nums}td,th{padding:6px 4px;border-bottom:1px solid var(--bd);text-align:left}
button{background:var(--ac);color:#fff;border:0;border-radius:8px;padding:10px 14px;font-size:15px;width:100%;margin-top:8px}
.badge{display:inline-block;padding:2px 8px;border-radius:99px;font-size:12px;background:var(--bd)}
@media(max-width:420px){.g{grid-template-columns:repeat(2,1fr)}}
</style></head><body>
<h1>Bot 95 <span class="badge">mode fantôme</span></h1><div class="mu">BTC 5 min Polymarket — 30 dernières secondes — aucun argent réel</div>
<div style="margin-top:8px"><a href="/rapport" style="color:var(--ac)">→ Rapport détaillé des refus</a></div>
<div id="app" class="mu" style="margin-top:12px">Chargement…</div>
<script>
const $=s=>document.querySelector(s);const f=(x,d=2)=>x==null?'—':Number(x).toFixed(d);const usd=x=>(x>=0?'+':'')+f(x)+' $';
async function rep(x){await fetch('/api/reprendre'+(x?'?s='+x:''),{method:'POST'});go()}
function bloc(t,e,x,extra){return (e.pause?'<div class=card style="border-color:var(--ko)"><b class=ko>'+t+' en pause après une perte.</b><br>Plus aucun trade jusqu\'à ce que tu valides.<button onclick="rep(\''+x+'\')">Reprendre '+t+'</button></div>':'')+
'<div class=card><b>'+t+'</b>'+(extra||'')+'<div class=g style="margin-top:8px"><div><div class=k>Capital</div><div class=v>'+f(e.capital)+' $</div></div><div><div class=k>Réserve (2/3)</div><div class=v>'+f(e.reserve)+' $</div></div><div><div class=k>Mise</div><div class=v>'+f(e.mise)+' $</div></div>'+
'<div><div class=k>Gain total</div><div class="v '+(e.pnl>=0?'ok':'ko')+'">'+usd(e.pnl)+'</div></div><div><div class=k>Gagnés</div><div class="v ok">'+e.gains+'</div></div><div><div class=k>Perdus</div><div class="v ko">'+e.pertes+'</div></div></div>'+
(e.position?'<div style="margin-top:8px">Position : '+e.position.fav+' à '+f(e.position.prix,3)+' — '+f(e.position.parts,1)+' parts'+(e.position.alerteGros?' <b class=ko>⚠️ '+e.position.alerteGros+' sortie(s) de gros traders</b>':'')+'</div>':'')+'</div>'}
async function go(){try{const d=await (await fetch('/api/etat')).json();const e=d.e,m=d.marche,F=d.flux;
const vt=Object.entries(e.vetos).sort((a,b)=>b[1]-a[1]).map(([k,v])=>'<tr><td>'+k+'</td><td>'+v+'</td></tr>').join('')||'<tr><td colspan=2 class=mu>Aucun encore</td></tr>';
const tr=e.trades.map(t=>'<tr><td>'+(t.strat||'A')+' '+t.heure.slice(5,16).replace('T',' ')+'</td><td>'+t.fav+'</td><td>'+f(t.prix,3)+'</td><td>'+f(t.z)+'</td><td>'+t.resultat+'</td><td class="'+(t.net>=0?'ok':'ko')+'">'+usd(t.net)+'</td></tr>').join('')||'<tr><td colspan=6 class=mu>Aucun trade encore</td></tr>';
const pos=e.position?'<div class=card><b>Position en cours</b><br>'+e.position.fav+' à '+f(e.position.prix,3)+' — '+f(e.position.parts,1)+' parts — z '+f(e.position.z)+'</div>':'';
$('#app').className='';$('#app').innerHTML=
bloc('A — achat immédiat',e,'A')+bloc('B — offre posée',e.B,'B','<span class=mu> — '+e.B.offres+' offres, '+e.B.remplies+' remplies</span>')+
'<div class=card><b>Marché en cours</b><br><span class=mu>'+(m.slug||'—')+' — fin dans '+m.reste+' s — prix d\\'exercice '+f(m.strike)+'</span>'+
(m.dernier?'<br>Favori '+m.dernier.fav+' à '+m.dernier.ask+' — distance '+m.dernier.dist+' $ — z '+m.dernier.z+' — proba '+m.dernier.proba:'')+(m.raison?'<br>Dernier refus A : <b>'+m.raison+'</b>':'')+(m.raisonB?'<br>Dernier refus B : <b>'+m.raisonB+'</b>':'')+(m.offre?'<br>Offre B posée : '+m.offre.fav+' à '+m.offre.prix+' — rempli '+f(m.offre.rempli,1)+' parts':'')+'</div>'+
'<div class=card><b>Flux</b><table><tr><td>Chainlink</td><td>'+f(F.chainlink.p)+'</td><td>'+f(F.chainlink.age,1)+' s</td></tr><tr><td>Perp '+(F.perp.src||'')+'</td><td>'+f(F.perp.p)+'</td><td>'+f(F.perp.age,1)+' s</td></tr><tr><td>Spot '+(F.coinbase.src||'')+'</td><td>'+f(F.coinbase.p)+'</td><td>'+f(F.coinbase.age,1)+' s</td></tr><tr><td>Déséquilibre carnet</td><td colspan=2>'+F.deseq+'</td></tr><tr><td>Liquidations 10 s</td><td colspan=2>'+F.liq10s+' $</td></tr></table></div>'+
'<div class=card><b>Gros traders du 5 min</b> <span class=mu>(top 10 en volume sur la dernière heure — positions sur le marché en cours)</span><table><tr><th>Trader</th><th>Volume 1 h</th><th>Up</th><th>Down</th></tr>'+
(d.gros.liste.map(g=>'<tr><td>'+(g.nom||g.w.slice(0,8)+'…')+'</td><td>'+g.vol+' $</td><td>'+g.Up+'</td><td>'+g.Down+'</td></tr>').join('')||'<tr><td colspan=4 class=mu>En cours de collecte</td></tr>')+'</table>'+
'<table style="margin-top:8px"><tr><th>Heure</th><th>Trader</th><th>Action</th><th>Parts</th><th>Prix</th><th>Fin dans</th></tr>'+
(d.gros.evenements.map(x=>'<tr'+(x.alerte?' class=ko':'')+'><td>'+x.heure+'</td><td>'+(x.nom||x.w.slice(0,8)+'…')+'</td><td>'+(x.alerte?'⚠️ ':'')+x.type+'</td><td>'+x.parts+'</td><td>'+x.prix+'</td><td>'+x.reste+' s</td></tr>').join('')||'<tr><td colspan=6 class=mu>Aucun mouvement encore</td></tr>')+'</table></div>'+
'<div class=card><b>Trades</b><table><tr><th>Heure UTC</th><th>Côté</th><th>Prix</th><th>z</th><th>Résultat</th><th>Net</th></tr>'+tr+'</table></div>'+
'<div class=card><b>Occasions refusées A</b> <span class=mu>('+e.fenetres+' marchés candidats)</span><table>'+vt+'</table></div>'+
'<div class=card><b>Occasions refusées B</b><table>'+(Object.entries(e.B.vetos).sort((a,b)=>b[1]-a[1]).map(([k,v])=>'<tr><td>'+k+'</td><td>'+v+'</td></tr>').join('')||'<tr><td class=mu>Aucun encore</td></tr>')+'</table></div>'+
(d.diag.erreurs.length?'<div class=card><b>Journal technique</b><div class=mu>'+d.diag.erreurs.join('<br>')+'</div></div>':'');
}catch(err){$('#app').textContent='Erreur de chargement : '+err}}
go();setInterval(go,2000);
</script></body></html>`;

const RAPPORT = `<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Rapport des refus</title><style>
:root{--bg:#f6f7f9;--card:#fff;--tx:#14171c;--mu:#667085;--bd:#e4e7ec;--ok:#12805c;--ko:#c0362c;--ac:#2f5bea;--wa:#b54708}
@media (prefers-color-scheme:dark){:root{--bg:#0f1115;--card:#171a21;--tx:#e8eaee;--mu:#98a2b3;--bd:#262b35;--ok:#3ccf91;--ko:#f0705f;--ac:#7c9cff;--wa:#f5a524}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--tx);font:15px/1.45 -apple-system,system-ui,sans-serif;padding:16px;max-width:760px;margin:auto}
h1{font-size:20px;margin:0 0 4px}a{color:var(--ac)}.mu{color:var(--mu);font-size:13px}.card{background:var(--card);border:1px solid var(--bd);border-radius:12px;padding:14px;margin:12px 0}
.l{margin-top:8px;padding-left:10px;border-left:3px solid var(--bd)}.r{font-weight:600}.ok{color:var(--ok)}.wa{color:var(--wa)}.chips{font-size:12px;color:var(--mu);margin-top:4px}
</style></head><body><h1>Rapport des refus</h1><div class="mu">Un bloc par marché où le favori était entre 0,94 et 0,99 dans les 30 dernières secondes. Pour chaque option, le dernier refus avec ses chiffres, puis le nombre de secondes bloquées par motif.</div>
<div style="margin-top:8px"><a href="/">← Tableau de bord</a></div><div id="app" class="mu" style="margin-top:12px">Chargement…</div>
<script>
const nb=c=>c?Object.entries(c).sort((a,b)=>b[1]-a[1]).map(([k,v])=>k+' : '+v+' s').join(' · '):'';
function opt(n,x,c){if(!x)return '<div class=l><span class=mu>'+n+' : pas concerné</span></div>';
const ok=x.raison==='acheté'||x.raison==='offre remplie';
return '<div class=l><span class="r '+(ok?'ok':'wa')+'">'+n+' — '+x.raison+'</span>'+(x.explication?'<br>'+x.explication:'')+
(x.fav?'<div class=chips>Favori '+x.fav+' · vendeur '+x.ask+' · acheteur '+x.bid+' · T-'+x.tleft+' s · distance '+x.dist+' $ · z '+x.z+' · proba '+(x.proba*100).toFixed(1)+' %</div>':'')+
(c&&Object.keys(c).length?'<div class=chips>Secondes bloquées : '+nb(c)+'</div>':'')+'</div>'}
async function go(){const d=await (await fetch('/api/rapport')).json();
document.getElementById('app').className='';
document.getElementById('app').innerHTML=(d.rapport.length?d.rapport.map(m=>'<div class=card><b>'+new Date(m.heure).toLocaleString('fr-CH',{weekday:'short',hour:'2-digit',minute:'2-digit'})+'</b> <span class=mu>'+m.slug+(m.strike?' · prix d\\'exercice '+Number(m.strike).toFixed(2):'')+'</span>'+
opt('A (achat immédiat)',m.A,m.comptes&&m.comptes.A)+opt('B (offre posée)',m.B,m.comptes&&m.comptes.B)+'</div>').join(''):'<div class=card>Aucun marché candidat enregistré depuis la mise en route du rapport.</div>')}
go();setInterval(go,10000);
</script></body></html>`;
