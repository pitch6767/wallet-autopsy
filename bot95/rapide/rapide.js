// BOT95 RAPIDE — VPS de Dublin (10.10.2026). FANTÔME UNIQUEMENT : aucun ordre, aucune clé de portefeuille.
// But : mesurer au millième de seconde si nous arrivons à temps sur les offres Polymarket que nos stratégies visent.
// Le code est servi par https://bot95.pitch67.workers.dev (mise à jour automatique : si la version change, le programme s'arrête et systemd le relance).
"use strict";
const fs = require("fs");
const VERSION = "__VERSION__";
const U = process.env.BOT95_URL || "https://bot95.pitch67.workers.dev";
const TOKEN = process.env.BOT95_RAPIDE_TOKEN || "";
const G = "https://gamma-api.polymarket.com", CLOB = "https://clob.polymarket.com";
const DIR = process.env.BOT95_DIR || __dirname;
const nowMs = () => performance.timeOrigin + performance.now();          // horloge murale à la microseconde
const now = () => nowMs() / 1000;
const log = (...x) => console.log(new Date().toISOString(), ...x);
const med = (L) => { if (!L.length) return null; const b = [...L].sort((a, c) => a - c); return b[Math.floor(b.length / 2)]; };
const qtl = (L, q) => { if (!L.length) return null; const b = [...L].sort((a, c) => a - c); return b[Math.min(b.length - 1, Math.floor(b.length * q))]; };
const phi = (x) => { const t = 1 / (1 + 0.2316419 * Math.abs(x)), d = 0.3989422804014327 * Math.exp(-x * x / 2);
  const p = d * t * (0.31938153 + t * (-0.356563782 + t * (1.781477937 + t * (-1.821255978 + t * 1.330274429)))); return x >= 0 ? 1 - p : p; };
const FEE = (p) => 0.072 * p * (1 - p);

// ---------------------------------------------------------------- prix des bourses et Chainlink
const f = {};                       // dernier prix : f[src] = { p, t, tsSrc }
const sec = new Map();              // seconde -> { perp, okx, bn, cb, cl }
function noter(src, p, tsSrc) {
  const t = now(); f[src] = { p, t, tsSrc: tsSrc || null };
  const s = Math.floor(t); let o = sec.get(s);
  if (!o) { o = {}; sec.set(s, o); if (sec.size > 800) sec.delete(sec.keys().next().value); }
  o[src] = p;
  if (src === "perp" || src === "okx") evaluer(src);
}
const prixA = (k, s) => { for (let i = 0; i < 6; i++) { const o = sec.get(s - i); if (o && o[k] != null) return o[k]; } return null; };
function serie(k, n) { const t = Math.floor(now()), out = []; let last = null;
  for (let s = t - n; s <= t; s++) { const o = sec.get(s); if (o && o[k] != null) last = o[k]; if (last != null) out.push([s, last]); } return out; }

// ---------------------------------------------------------------- modèle (copie exacte de probaV1 du bot Cloudflare)
let sgc = null, okxB = null;
function prixRapide() {
  const t = now();
  if (!sgc || t - sgc.t > 1) {
    const ser = serie("perp", 300);
    if (ser.length >= 60) {
      const r = []; for (let i = 1; i < ser.length; i++) r.push(Math.log(ser[i][1] / ser[i - 1][1]));
      const mo = r.reduce((x, y) => x + y, 0) / r.length;
      const base = med(serie("perp", 120).map(([s2, p]) => { const c = prixA("cl", s2); return c ? p - c : null; }).filter((x) => x != null));
      sgc = { t, v: Math.sqrt(r.reduce((x, y) => x + (y - mo) ** 2, 0) / r.length) || 1e-6, base };
    }
  }
  if (!okxB || t - okxB.t > 1) okxB = { t, v: med(serie("okx", 120).map(([s2, p]) => { const c = prixA("cl", s2); return c ? p - c : null; }).filter((x) => x != null)) };
  const c = [];
  if (f.perp && sgc && sgc.base != null) c.push([f.perp.t, f.perp.p - sgc.base, "bybit"]);
  if (f.okx && okxB.v != null) c.push([f.okx.t, f.okx.p - okxB.v, "okx"]);
  if (!c.length) return null;
  c.sort((x, y) => y[0] - x[0]); return c[0];
}
function proba(mk, sdRel) {
  if (!mk || !mk.strike || !f.cl) return null;
  const pr = prixRapide(); if (!pr || !sgc) return null;
  const S = pr[1], sg = sgc.v, t = now(), ts = Math.floor(t), deb = mk.end - 60;
  let E, v;
  if (ts >= deb) {
    const connus = []; for (let s2 = deb; s2 <= Math.min(ts, mk.end - 1); s2++) { const x = prixA("cl", s2); if (x) connus.push(x); }
    const nr = Math.max(1, mk.end - 1 - ts);
    E = (connus.reduce((x, y) => x + y, 0) + nr * S) / (connus.length + nr); v = (sg * S) ** 2 * nr ** 3 / 3 / 3600;
  } else { E = S; v = (sg * S) ** 2 * ((deb - ts) + 20); }
  return phi((E - mk.strike) / Math.sqrt(v + (sdRel * S) ** 2));
}

// ---------------------------------------------------------------- marchés et carnets Polymarket
const M = {};                       // start -> marché { start, end, slug, up, down, strike }
const livres = {};                  // token -> { asks: Map, bids: Map, tRecu, tsPoly }
async function getJSON(url, opt) { const r = await fetch(url, opt); if (!r.ok) throw new Error(url + " HTTP " + r.status); return r.json(); }
async function chargerMarche(start) {
  if (M[start] && M[start].up) return M[start];
  const ev = await getJSON(`${G}/events?slug=btc-updown-5m-${start}`);
  const e = ev && ev[0], m = e && e.markets && e.markets[0]; if (!m) return null;
  const outs = JSON.parse(m.outcomes || "[]"), toks = JSON.parse(m.clobTokenIds || "[]"), iUp = outs.findIndex((o) => String(o).toLowerCase() === "up");
  M[start] = { ...(M[start] || {}), start, end: start + 300, slug: e.slug, up: toks[iUp], down: toks[1 - iUp] };
  return M[start];
}
const asksTries = (id) => { const L = livres[id]; return L ? [...L.asks].filter((x) => x[1] > 0).sort((a, b) => a[0] - b[0]) : []; };
function surPoly(m) {
  if (Array.isArray(m)) { for (const x of m) surPoly(x); return; }
  const tR = nowMs(), ts = +m.timestamp > 1e12 ? +m.timestamp : (+m.timestamp ? +m.timestamp * 1000 : null);
  const L = (id) => (livres[id] = livres[id] || { asks: new Map(), bids: new Map() });
  const touches = new Set();
  if (m.event_type === "book") {
    const B = L(m.asset_id); B.bids = new Map((m.bids || []).map((x) => [+x.price, +x.size])); B.asks = new Map((m.asks || []).map((x) => [+x.price, +x.size]));
    B.tRecu = tR; B.tsPoly = ts; touches.add(m.asset_id);
  } else if (m.event_type === "price_change") {
    for (const c of m.price_changes || []) { const B = L(c.asset_id), cote = c.side === "BUY" ? B.bids : B.asks; +c.size ? cote.set(+c.price, +c.size) : cote.delete(+c.price); B.tRecu = tR; B.tsPoly = ts; touches.add(c.asset_id); }
  } else return;
  if (ts) { STAT.retardPoly.push(tR - ts); if (STAT.retardPoly.length > 2000) STAT.retardPoly.shift(); }
  for (const id of touches) suivreSurvie(id);
  evaluer("poly", tR);
}

// ---------------------------------------------------------------- règles (premier signal du cycle, mêmes règles que les fantômes Cloudflare)
const H = {};                       // start -> { r: [...échantillons 250 ms], fait: {} }
const SIGNAUX = [], FINIS = [];
const STAT = { retardPoly: [], rttClob: [], decisionUs: [], evaluations: 0 };
function evaluer(source, tMsg) {
  const t0 = process.hrtime.bigint();
  const t = now(), start = Math.floor(t / 300) * 300, mk = M[start];
  if (!mk || !mk.up || !mk.strike) return;
  const tleft = mk.end - t; if (tleft < 5) return;
  const ua = asksTries(mk.up)[0], da = asksTries(mk.down)[0]; if (!ua || !da) return;
  const pu = proba(mk, 8e-4), pu01 = proba(mk, 1e-4); if (pu == null) return;
  STAT.evaluations++;
  const h = (H[start] = H[start] || { r: [], fait: {} });
  if (!h.r.length || t - h.r[h.r.length - 1].t >= 0.25) { h.r.push({ t, pu, pu01, ua: ua[0], da: da[0] }); while (h.r.length && t - h.r[0].t > 12) h.r.shift(); }
  const ilya = (s) => { for (let i = h.r.length - 1; i >= 0; i--) if (t - h.r[i].t >= s) return h.r[i]; return null; };
  const h3 = ilya(3);
  for (const up of [true, false]) {
    const k = up ? ua : da, a = k[0];
    const regle = (nom, ok, fair) => { if (ok && !h.fait[nom]) { h.fait[nom] = true; signal(nom, mk, up, k, fair, tleft, source, tMsg, t0); } };
    const fair = up ? pu : 1 - pu, edge = fair - a;
    if (a >= 0.03 && a <= 0.97 && edge >= 0.20 && h3) regle("V2-F ecart qui grandit", edge - ((up ? h3.pu : 1 - h3.pu) - (up ? h3.ua : h3.da)) >= 0.03, fair);
    if (pu01 != null && a >= 0.03 && a <= 0.97 && h3 && h3.pu01 != null) {
      const f1 = up ? pu01 : 1 - pu01, e1 = f1 - a;
      if (e1 >= 0.20) regle("V2-F incertitude 0,01 %", e1 - ((up ? h3.pu01 : 1 - h3.pu01) - (up ? h3.ua : h3.da)) >= 0.03, f1);
    }
    if (a >= 0.02 && a <= 0.98) {
      regle("desaccord 30", edge >= 0.30, fair);
      regle("desaccord 20 60-180 s", edge >= 0.20 && tleft > 60 && tleft <= 180, fair);
      regle("desaccord 20 jeton 0,35-0,65", edge >= 0.20 && a >= 0.35 && a < 0.65, fair);
    }
  }
}
const DELAIS = [1, 2, 5, 10, 25, 50, 100, 250, 500, 1000, 2000];
function achetable(id, a0, budget = 50) {          // parts et coût au prix vu ou mieux, quantité affichée, 50 $ max
  let q = 0, c = 0;
  for (const [p, sz] of asksTries(id)) { if (p > a0 + 1e-9) break; const k = Math.min(sz, budget / a0 - q); if (k <= 0) break; q += k; c += k * p + k * FEE(p); }
  return { q: +q.toFixed(2), c: +c.toFixed(2) };
}
function signal(nom, mk, up, k, fair, tleft, source, tMsg, t0) {
  const id = up ? mk.up : mk.down, B = livres[id] || {}, tD = nowMs();
  const decisionUs = Number(process.hrtime.bigint() - t0) / 1000;
  STAT.decisionUs.push(decisionUs); if (STAT.decisionUs.length > 500) STAT.decisionUs.shift();
  const age = (x) => (x ? +(now() - x.t).toFixed(3) : null);
  const S = { nom, start: mk.start, cote: up ? "Up" : "Down", id, a0: k[0], q0: +k[1].toFixed(2), modele: +fair.toFixed(4), ecart: +(fair - k[0]).toFixed(4), restant_s: +tleft.toFixed(2),
    declencheur: source, tDecision: +tD.toFixed(3), msgVersDecision_ms: tMsg ? +(tD - tMsg).toFixed(3) : null, calcul_us: +decisionUs.toFixed(1),
    carnetAge_ms: B.tRecu ? +(tD - B.tRecu).toFixed(3) : null, carnetPolyVersNous_ms: B.tRecu && B.tsPoly ? +(B.tRecu - B.tsPoly).toFixed(1) : null,
    agePerp: age(f.perp), ageOkx: age(f.okx), ageBn: age(f.bn), ageCb: age(f.cb), ageCl: age(f.cl),
    achetable0: achetable(id, k[0]), apres: {}, premiereBaisse_ms: null, disparu_ms: null };
  SIGNAUX.push(S);
  for (const d of DELAIS) setTimeout(() => { S.apres[d] = { ...achetable(id, S.a0), reel_ms: +(nowMs() - S.tDecision).toFixed(2) }; }, d);
  setTimeout(() => { S.fini = true; }, 2100);
}
function suivreSurvie(id) {                    // au message près : quand l'offre vue a-t-elle commencé à fondre, puis disparu ?
  const t = nowMs();
  for (const S of SIGNAUX) {
    if (S.fini || S.id !== id || S.disparu_ms != null) continue;
    const x = achetable(id, S.a0);
    if (S.premiereBaisse_ms == null && x.q < S.achetable0.q - 1e-6) S.premiereBaisse_ms = +(t - S.tDecision).toFixed(3);
    if (x.q < 1) S.disparu_ms = +(t - S.tDecision).toFixed(3);
  }
}

// ---------------------------------------------------------------- flux WebSocket (reconnexion si muet 20 s)
const WS = {};
function connecter(nom, url, abos, surMsg, ping, periode) {
  try { WS[nom] && WS[nom].ws && WS[nom].ws.close(); } catch (_) {}
  const ws = new WebSocket(url); const st = (WS[nom] = { ws, ouvert: now(), msg: now(), n: (WS[nom] ? WS[nom].n : 0) + 1 });
  ws.addEventListener("open", () => { for (const a of abos) ws.send(a); if (ping) st.pinger = setInterval(() => { try { ws.send(ping); } catch (_) {} }, periode || 10000); });
  ws.addEventListener("message", (ev) => {
    st.msg = now(); const d = typeof ev.data === "string" ? ev.data : ev.data.toString();
    if (d === "PONG" || d === "pong" || d === "PING") return;
    try { surMsg(JSON.parse(d)); } catch (_) {}
  });
  ws.addEventListener("close", () => { clearInterval(st.pinger); });
  ws.addEventListener("error", () => {});
}
function flux() {
  const muet = (k) => !WS[k] || now() - WS[k].msg > 20 || WS[k].ws.readyState > 1;
  if (muet("perp")) connecter("perp", "wss://stream.bybit.com/v5/public/linear", [JSON.stringify({ op: "subscribe", args: ["publicTrade.BTCUSDT"] })],
    (m) => { const x = (m.data || []).slice(-1)[0]; if ((m.topic || "").startsWith("publicTrade") && x) noter("perp", +x.p, +x.T); }, JSON.stringify({ op: "ping" }), 15000);
  if (muet("okx")) connecter("okx", "wss://ws.okx.com:8443/ws/v5/public", [JSON.stringify({ op: "subscribe", args: [{ channel: "trades", instId: "BTC-USDT-SWAP" }] })],
    (m) => { const x = (m.data || []).slice(-1)[0]; if (m.arg && m.arg.channel === "trades" && x) noter("okx", +x.px, +x.ts); }, "ping", 20000);
  if (muet("bn")) connecter("bn", "wss://stream.binance.com:9443/ws/btcusdt@trade", [], (m) => { if (+m.p > 0) noter("bn", +m.p, +m.T); });
  if (muet("cb")) connecter("cb", "wss://advanced-trade-ws.coinbase.com", [JSON.stringify({ type: "subscribe", product_ids: ["BTC-USD"], channel: "ticker" })],
    (m) => { if (m.channel !== "ticker") return; for (const ev of m.events || []) for (const x of ev.tickers || []) if (x.product_id === "BTC-USD" && x.price) noter("cb", +x.price, Date.parse(m.timestamp)); });
  if (muet("cl")) connecter("cl", "wss://ws-live-data.polymarket.com", [JSON.stringify({ action: "subscribe", subscriptions: [{ topic: "crypto_prices_chainlink", type: "*", filters: "" }] })],
    (m) => { if (m.topic !== "crypto_prices_chainlink") return; const p = m.payload || {}; if ((p.symbol || "").toUpperCase().startsWith("BTC") && +p.value > 0) noter("cl", +p.value, +p.timestamp); }, "PING", 5000);
}
let polyCle = "";
async function cycle() {
  const t = now(), start = Math.floor(t / 300) * 300;
  try { await chargerMarche(start); if (start + 300 - t < 40) await chargerMarche(start + 300); } catch (e) { log("marché", e.message); }
  const mk = M[start];
  if (mk && !mk.strike && t >= start + 2) {                 // prix à battre = moyenne Chainlink des 60 s avant le début (règle du bot)
    const v = []; for (let s2 = start - 60; s2 <= start - 1; s2++) { const o = sec.get(s2); if (o && o.cl != null) v.push(o.cl); }
    if (v.length >= 40) mk.strike = v.reduce((x, y) => x + y, 0) / v.length;
  }
  const jetons = [start, start + 300].map((s) => M[s]).filter((m) => m && m.up).flatMap((m) => [m.up, m.down]);
  const cle = jetons.join(",");
  if (jetons.length && (cle !== polyCle || !WS.poly || now() - WS.poly.msg > 20 || WS.poly.ws.readyState > 1)) {
    polyCle = cle; for (const id of Object.keys(livres)) if (!jetons.includes(id)) delete livres[id];
    connecter("poly", "wss://ws-subscriptions-clob.polymarket.com/ws/market", [JSON.stringify({ assets_ids: jetons, type: "market" })], surPoly, "PING", 10000);
  }
  for (const s of Object.keys(H)) if (+s < start - 600) delete H[s];
  for (const s of Object.keys(M)) if (+s < start - 900) delete M[s];
  flux();
}
// ---------------------------------------------------------------- résultat des cycles, latence vers Polymarket, envoi au bot Cloudflare
const RES = {};
async function reglements() {
  const t = now();
  for (const S of SIGNAUX) {
    if (!S.fini || S.envoye || t < S.start + 300 + 60) continue;
    if (RES[S.start] === undefined) {
      try {
        const ev = await getJSON(`${G}/events?slug=btc-updown-5m-${S.start}`); const m = ev[0].markets[0];
        const px = JSON.parse(m.outcomePrices || "[]").map(Number), outs = JSON.parse(m.outcomes || "[]");
        RES[S.start] = px.includes(1) ? outs[px.indexOf(1)] : null;
      } catch (_) { RES[S.start] = null; }
      if (RES[S.start] == null) { delete RES[S.start]; continue; }
    }
    S.gagnant = RES[S.start]; S.gagne = S.gagnant === S.cote;
    const pn = (x) => (x && x.q >= 1 ? +((S.gagne ? x.q : 0) - x.c).toFixed(2) : 0);
    S.resultat = { 0: pn(S.achetable0), ...Object.fromEntries(DELAIS.map((d) => [d, pn(S.apres[d])])) };
    FINIS.push(S); S.envoye = true;
  }
  for (let i = SIGNAUX.length - 1; i >= 0; i--) if (SIGNAUX[i].envoye || now() - SIGNAUX[i].tDecision / 1000 > 1800) SIGNAUX.splice(i, 1);
}
async function sonde() {                       // aller-retour HTTP vers le serveur de Polymarket
  try { const t0 = nowMs(); await fetch(`${CLOB}/time`).then((r) => r.text()); STAT.rttClob.push(+(nowMs() - t0).toFixed(2)); if (STAT.rttClob.length > 500) STAT.rttClob.shift(); } catch (_) {}
}
async function envoyer() {
  const corps = { version: VERSION, t: now(), signaux: FINIS.splice(0, FINIS.length).map(({ id, fini, envoye, ...s }) => s),
    latence: { rttClob_ms: { med: med(STAT.rttClob), p10: qtl(STAT.rttClob, 0.1), p90: qtl(STAT.rttClob, 0.9), n: STAT.rttClob.length },
      polyVersNous_ms: { med: med(STAT.retardPoly), p10: qtl(STAT.retardPoly, 0.1), p90: qtl(STAT.retardPoly, 0.9) },
      calcul_us: { med: med(STAT.decisionUs), p90: qtl(STAT.decisionUs, 0.9) }, evaluations: STAT.evaluations },
    flux: Object.fromEntries(["perp", "okx", "bn", "cb", "cl", "poly"].map((k) => [k, WS[k] ? { muet_s: +(now() - WS[k].msg).toFixed(1), reconnexions: WS[k].n } : null])) };
  try {
    const r = await fetch(`${U}/api/rapide/donnees`, { method: "POST", headers: { "content-type": "application/json", "x-rapide": TOKEN }, body: JSON.stringify(corps) });
    if (!r.ok) { log("envoi HTTP", r.status); FINIS.unshift(...corps.signaux); }
  } catch (e) { log("envoi", e.message); FINIS.unshift(...corps.signaux); }
  try { fs.writeFileSync(DIR + "/dernier_envoi.json", JSON.stringify(corps)); } catch (_) {}
}
async function versionDistante() {
  try { const d = await getJSON(`${U}/api/rapide/version`, { headers: { "x-rapide": TOKEN } }); if (d.version && d.version !== VERSION) { log("nouvelle version", d.version, "→ redémarrage"); await envoyer(); process.exit(0); } } catch (_) {}
}
log("bot95 rapide", VERSION, "démarre — fantôme uniquement, aucun ordre");
flux(); cycle();
setInterval(cycle, 1000);
setInterval(() => reglements().catch(() => {}), 10000);
setInterval(sonde, 15000);
setInterval(envoyer, 60000);
setInterval(versionDistante, 60000);
