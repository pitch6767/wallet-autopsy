// BOT95 RAPIDE — VPS de Dublin (10.10.2026). FANTÔME UNIQUEMENT : aucun ordre, aucune clé de portefeuille.
// 11.10.2026 : identifiants API Polymarket (lecture seule pour le flux PolyBolt ; ils ne permettent pas de signer un ordre) servis par le bot Cloudflare.
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
const CHG = {};                     // dernier CHANGEMENT de prix par source (indicateur d'âge utilisé à l'apprentissage du moteur C)
function noter(src, p, tsSrc) {
  const t = now(); if (!f[src] || f[src].p !== p) CHG[src] = t; f[src] = { p, t, tsSrc: tsSrc || null };
  const s = Math.floor(t); let o = sec.get(s);
  if (!o) { o = {}; sec.set(s, o); if (sec.size > 800) sec.delete(sec.keys().next().value); }
  o[src] = p;
  if (src === "perp" || src === "okx") evaluer(src);
}
// Chainlink arrive par deux flux (11.10.2026) : RTDS (ancien, public) et PolyBolt (nouveau, identifiants API). On garde l'observation la plus récente.
const CLS = { publication: [], transport: [], boucle: [], delai: { rtds: [], pb: [] }, premier: { rtds: 0, pb: 0 }, avance: [], vu: new Map(), dernObs: { rtds: null, pb: null }, n: { rtds: 0, pb: 0 }, pbAuth: false, pbErreur: null, source: null, twap: [] };
function chainlink(feed, v, obsMs) {
  if (!(v > 0) || !(obsMs > 0)) return;
  const t = nowMs(); CLS.n[feed]++; CLS.dernObs[feed] = obsMs;
  const D = CLS.delai[feed]; D.push(t - obsMs); if (D.length > 2000) D.shift();
  const e = CLS.vu.get(obsMs);
  if (!e) { CLS.vu.set(obsMs, { feed, t }); if (CLS.vu.size > 400) CLS.vu.delete(CLS.vu.keys().next().value); }
  else if (!e.deux && e.feed !== feed) { e.deux = true; CLS.premier[e.feed]++; CLS.avance.push([e.feed, +(t - e.t).toFixed(1)]); if (CLS.avance.length > 2000) CLS.avance.shift(); }
  try { recDe(Math.floor(t / 300000) * 300).cl2.push([+t.toFixed(1), feed === "pb" ? 1 : 0, obsMs, v]); } catch (_) {}
  if (!f.cl || !f.cl.tsSrc || obsMs > f.cl.tsSrc) noter("cl", v, obsMs);
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

// ---------------------------------------------------------------- ENREGISTREUR DE CYCLE (11.10.2026, demandé par Pitch) — aucun ordre
// Par cycle : tous les messages Polymarket des 2 jetons (carnet complet, changements de niveau, transactions) avec heure de réception (VPS, NTP)
// et heure Polymarket ; prix des 5 sources toutes les 50 ms (si changés) avec leur heure source ; carnet 5 niveaux chaque seconde ;
// signaux des cohortes A et B ; journal des décisions. Écrit sur le disque du VPS et envoyé au bot Cloudflare.
const zlib = require("zlib");
const REC = {};
const recDe = (start) => (REC[start] = REC[start] || { start, version: VERSION, ev: [], ex: [], snap: [], sig: [], dec: [], cl2: [], tw: [], mk: [], nEv: 0, coupe: false });
const tokIdx = (id) => { for (const s of Object.keys(M)) { const m = M[s]; if (m.up === id) return [+s, 0]; if (m.down === id) return [+s, 1]; } return [null, null]; };
// Volume mesuré le 11.10 : ~700 messages/s. Les carnets Up et Down sont miroirs (vérifié sur 100 % des lignes) : on garde le carnet Up seulement,
// les changements de niveau à 3 c ou moins du meilleur prix, un carnet complet toutes les 10 s, et TOUTES les transactions des deux jetons.
const PRES = 0.03;
function recEv(id, row) {
  const [st, k] = tokIdx(id); if (st == null) return; const R = recDe(st); R.nEv++;
  if (row[0] !== "T") {
    if (k !== 0) return;
    if (row[0] === "B") { if (R.dernierB && row[1] - R.dernierB < 10000) return; R.dernierB = row[1]; }
    if (row[0] === "P") {
      const L = livres[id]; if (L) {
        const side = row[3], p = row[4];
        const best = side === 0 ? Math.max(0, ...[...L.bids].filter((x) => x[1] > 0).map((x) => x[0])) : Math.min(1, ...[...L.asks].filter((x) => x[1] > 0).map((x) => x[0]));
        if ((side === 0 ? best - p : p - best) > PRES + 1e-9) return;
      }
    }
  }
  if (R.ev.length >= 120000) { R.coupe = true; return; }
  row.splice(3, 0, k); R.ev.push(row);
}
// flux agressifs par source (12.10.2026, H527-H530) : volume acheteur / vendeur (côté preneur) et nombre de transactions par tranche de 50 ms ;
// liquidations Bybit. Coinbase : canal market_trades (côté preneur fourni). Aucune donnée inventée : une source sans côté n'est pas comptée.
const FLOW = {};
function flux50(src, cote, q, p) { const F = (FLOW[src] = FLOW[src] || { a: 0, v: 0, n: 0 }); if (cote === "a") F.a += q * p; else F.v += q * p; F.n++;
  if (src !== "liq_bybit" && typeof FLOW2 !== "undefined") FLOW2.net += (cote === "a" ? 1 : -1) * q * p; }
let exDernier = "";
setInterval(() => {                                   // prix des sources toutes les 50 ms (seulement si un prix a changé)
  const t = nowMs(), start = Math.floor(t / 300000) * 300;
  const v = ["perp", "okx", "bn", "cb", "cl"].map((k) => (f[k] ? [f[k].p, f[k].tsSrc || null, +f[k].t.toFixed(3)] : null));
  const fl = Object.keys(FLOW).length ? Object.fromEntries(Object.entries(FLOW).map(([k, x]) => [k, [Math.round(x.a), Math.round(x.v), x.n]])) : null;
  for (const k of Object.keys(FLOW)) delete FLOW[k];
  if (fl) recDe(start).fx = (recDe(start).fx || []), recDe(start).fx.push([+t.toFixed(1), fl]);
  const cle = JSON.stringify(v.map((x) => x && x[0])); if (cle === exDernier) return; exDernier = cle;
  recDe(start).ex.push([+t.toFixed(1), ...v]);
}, 50);
setInterval(() => {                                   // carnet 5 niveaux des 2 jetons chaque seconde (contrôle de la reconstruction)
  const t = nowMs(), start = Math.floor(t / 300000) * 300, mk = M[start]; if (!mk || !mk.up) return;
  const top = (id, c) => { const L = livres[id]; if (!L) return []; return [...L[c]].filter((x) => x[1] > 0).sort((a, b) => (c === "asks" ? a[0] - b[0] : b[0] - a[0])).slice(0, 5); };
  recDe(start).snap.push([+t.toFixed(1), top(mk.up, "bids"), top(mk.up, "asks"), top(mk.down, "bids"), top(mk.down, "asks")]);
}, 1000);
function recFinir() {                                 // cycles terminés depuis plus de 10 s : compression, disque, envoi
  const t = now();
  for (const s of Object.keys(REC)) {
    const R = REC[s]; if (t < +s + 310) continue; delete REC[s];
    const m = M[s] || {}; R.marche = { slug: m.slug || null, up: m.up || null, down: m.down || null, strike: m.strike || null, strikeTwap: m.strikeTwap || null };
    R.formatCl2 = "cl2=[reception_ms, flux 0 RTDS/1 PolyBolt, observation_ms, prix] ; tw=[reception_ms, observation_ms, moyenne 60 s officielle PolyBolt]";
    // encodage compact : P = [écart en ms depuis le P précédent, retard Polymarket ms, côté 0 achat/1 vente, prix en cents, taille ×100]
    let prev = 0; const P = [], autres = [];
    for (const e of R.ev) {
      if (e[0] === "P") { const t = Math.round(e[1]); P.push([t - prev, e[2] ? Math.round(e[1] - e[2]) : null, e[4], Math.round(e[5] * 1000), Math.round(e[6] * 100)]); prev = t; }
      else autres.push(e);
    }
    R.ev = autres; R.p = P; R.format = "p=[dt_ms,retard_ms,cote,prix_en_milliemes,taille*100] (jeton Up, ±3 c du meilleur) ; ev = B (carnet complet Up /10 s) et T (transactions des 2 jetons)";
    let gz; try { gz = zlib.gzipSync(JSON.stringify(R)); } catch (e) { log("compression", e.message); continue; }
    STAT.dernierCycle = { start: +s, ev: R.nEv, ex: R.ex.length, octets: gz.length, coupe: R.coupe };
    try { const d = new Date(+s * 1000).toISOString().slice(0, 10), dir = DIR + "/cycles/" + d; fs.mkdirSync(dir, { recursive: true }); fs.writeFileSync(dir + "/" + s + ".json.gz", gz); } catch (e) { log("disque", e.message); }
    envoyerCycle(+s, gz).catch(() => {});
  }
  try { const base = DIR + "/cycles", lim = new Date(Date.now() - 14 * 86400000).toISOString().slice(0, 10);   // on garde 14 jours sur le disque
    for (const d of fs.existsSync(base) ? fs.readdirSync(base) : []) if (d < lim) fs.rmSync(base + "/" + d, { recursive: true, force: true }); } catch (_) {}
}
async function envoyerCycle(start, gz) {
  for (let essai = 0; essai < 3; essai++) {
    try { const r = await fetch(`${U}/api/rapide/cycle?start=${start}`, { method: "POST", headers: { "content-type": "application/octet-stream", "x-rapide": TOKEN }, body: gz });
      if (r.ok) return; log("cycle HTTP", r.status); } catch (e) { log("cycle", e.message); }
    await new Promise((res) => setTimeout(res, 5000));
  }
}
setInterval(recFinir, 5000);

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
  if (m.event_type === "last_trade_price") { recEv(m.asset_id, ["T", +tR.toFixed(1), ts, m.side === "BUY" ? 1 : 0, +m.price, +m.size]); try { makerTransaction(m.asset_id, m.side, +m.price, +m.size); } catch (_) {} return; }
  if (m.event_type === "book") {
    recEv(m.asset_id, ["B", +tR.toFixed(1), ts, (m.bids || []).map((x) => [+x.price, +x.size]), (m.asks || []).map((x) => [+x.price, +x.size])]);
    const B = L(m.asset_id);
    try { for (const x of m.bids || []) makerNiveau(m.asset_id, +x.price, B.bids.get(+x.price) || 0, +x.size); } catch (_) {}
    B.bids = new Map((m.bids || []).map((x) => [+x.price, +x.size])); B.asks = new Map((m.asks || []).map((x) => [+x.price, +x.size]));
    B.tRecu = tR; B.tsPoly = ts; touches.add(m.asset_id);
  } else if (m.event_type === "price_change") {
    for (const c of m.price_changes || []) { recEv(c.asset_id, ["P", +tR.toFixed(1), ts, c.side === "BUY" ? 0 : 1, +c.price, +c.size]); const B = L(c.asset_id), cote = c.side === "BUY" ? B.bids : B.asks;
      const avant = cote.get(+c.price) || 0; +c.size ? cote.set(+c.price, +c.size) : cote.delete(+c.price); B.tRecu = tR; B.tsPoly = ts; touches.add(c.asset_id);
      if (c.side === "BUY") { try { makerNiveau(c.asset_id, +c.price, avant, +c.size); } catch (_) {} } }
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
  const pu = proba(mk, 8e-4), pu01 = proba(mk, 1e-4), pu015 = proba(mk, 1.5e-4); if (pu == null) return;
  STAT.evaluations++;
  const h = (H[start] = H[start] || { r: [], fait: {} });
  if (!h.r.length || t - h.r[h.r.length - 1].t >= 0.25) { const ub = (livres[mk.up] && [...livres[mk.up].bids].filter((x) => x[1] > 0).sort((x, y) => y[0] - x[0])[0]) || null, db = (livres[mk.down] && [...livres[mk.down].bids].filter((x) => x[1] > 0).sort((x, y) => y[0] - x[0])[0]) || null;
    h.r.push({ t, pu, pu01, pu015, ua: ua[0], da: da[0], uz: ua[1], dz: da[1], ub: ub ? ub[0] : null, db: db ? db[0] : null, perp: f.perp ? f.perp.p : null }); while (h.r.length && t - h.r[0].t > 35) h.r.shift(); }
  const ilya = (s) => { for (let i = h.r.length - 1; i >= 0; i--) if (t - h.r[i].t >= s) return h.r[i]; return null; };
  const h3 = ilya(3);
  try { makerEvaluer(mk, tleft, ua, da, { pu, pu01, pu015 }); } catch (e) { log("maker", e.message); }
  for (const up of [true, false]) {
    const k = up ? ua : da, a = k[0];
    const regle = (nom, ok, fair) => { if (ok && !h.fait[nom]) { h.fait[nom] = true; signal(nom, mk, up, k, fair, tleft, source, tMsg, t0); } };
    const fair = up ? pu : 1 - pu, edge = fair - a;
    if (a >= 0.03 && a <= 0.97 && edge >= 0.20 && h3) regle("V2-F ecart qui grandit", edge - ((up ? h3.pu : 1 - h3.pu) - (up ? h3.ua : h3.da)) >= 0.03, fair);
    if (pu01 != null && a >= 0.03 && a <= 0.97 && h3 && h3.pu01 != null) {
      const f1 = up ? pu01 : 1 - pu01, e1 = f1 - a;
      if (e1 >= 0.20) regle("V2-F incertitude 0,01 %", e1 - ((up ? h3.pu01 : 1 - h3.pu01) - (up ? h3.ua : h3.da)) >= 0.03, f1);
    }
    // cohorte A « désaccord 30 zone + modèle monte » : plus de 60 s, vendeur 0,15-0,35, écart >= 0,30, modèle +3 c en 3 s
    if (h3 && tleft > 60 && a >= 0.15 && a < 0.35 && edge >= 0.30) regle("cohorte A : zone + modele monte", fair - (up ? h3.pu : 1 - h3.pu) >= 0.03, fair);
    // cohorte B « V2-F corrigé 0,015 % » : règle V2-F avec l'incertitude 0,015 %
    if (pu015 != null && h3 && h3.pu015 != null && a >= 0.03 && a <= 0.97) {
      const f2 = up ? pu015 : 1 - pu015, e2 = f2 - a;
      if (e2 >= 0.20) regle("cohorte B : V2-F corrige 0,015 %", e2 - ((up ? h3.pu015 : 1 - h3.pu015) - (up ? h3.ua : h3.da)) >= 0.03, f2);
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
// ---------------------------------------------------------------- MOTEUR C « alpha exécutable » (fantôme, 11.10.2026) — modèles FIGÉS appris hors ligne
// sur l'apprentissage (etude/bot5min/moteurs_abc.py) : P(offre encore là à 0,3 s) et P(gain | offre encore là) ; on « envoie » si
// P(survie)·[P(gain|survie) − prix − frais] > marge, ordre fictif limite au plafond, quantité ≤ affichée. Aucun ordre réel.
const MC = {"cal":{"coef":[0.9244235812176818,0.27602482707792353,-0.021744561149625693],"b":-0.1762806018018177},"mu":[-0.36344294487808804,-1.0864788816204833,4.512328041445113,0.1400463476718737,-0.012983818770226536,-0.018456310679611655,-1.4343161425288484,0.08584867100316922,0.5417391585763599,3.0248077550672683,0.011553398058252356,0.5316181260019445,0.46663430207755574,0.5964724909526244,0.8381877022653722],"sd":[0.8219272073564333,0.7579978471798069,1.761848678124931,0.056882502084362394,0.0824317108766244,0.10067302197747924,2.1309662686017217,0.1139736290544038,0.2527161622233942,2.8372939385239824,0.0064452819891619,1.6649823769361907,1.4866226598280357,1.1816250345831294,0.3682785342278673],"ms":{"coef":[-0.10060373160731688,0.13560946304689556,1.1499631282121094,0.08630792400577919,-0.21652985374826889,0.3837073973660029,0.061850920954721465,-0.4032959193365681,-0.4295665123718461,-0.10484678229431471,-0.12228782756988432,0.7966583850931037,0.10230560323091692,-0.22883859401613924,0.025901940641459658],"b":-0.010643952749869066},"mw":{"coef":[0.4935246767575995,0.5523711015383109,-0.0491518168093895,0.17548678952728694,0.39306440423514516,-0.31804659219683823,0.10964877708352119,0.09437941565056567,-0.07961591872262912,0.1436164652142183,-0.2208102065097406,-0.04811377689801466,-0.11638393235033473,0.005134536887688822,-0.007303985908691757],"b":-0.5075233192556861},"marge":0.01,"variables":["logit proba calibr\u00e9e","logit prix","log taille affich\u00e9e","\u00e9cart calibr\u00e9 \u2212 prix","variation du prix 1 s","variation du prix 3 s","variation de taille 1 s","variation du mod\u00e8le 3 s","temps restant","volatilit\u00e9 Bybit 30 s","\u00e9cart vendeur-acheteur","\u00e2ge Bybit (ind.)","\u00e2ge OKX (ind.)","\u00e2ge Chainlink (ind.)","cohorte B"]};
const lgt = (p) => { const q = Math.min(1 - 1e-4, Math.max(1e-4, p)); return Math.log(q / (1 - q)); };
const sigm = (x) => 1 / (1 + Math.exp(-x));
const lin = (m, v) => m.b + m.coef.reduce((a, c, i) => a + c * v[i], 0);
function plafondC(p, m) { const r = p - m; if (r <= 0.01) return 0; const c = (1.072 - Math.sqrt(1.072 ** 2 - 4 * 0.072 * r)) / (2 * 0.072); return Math.floor(c * 100 + 1e-9) / 100; }
function moteurC(nom, mk, up, k, fair) {
  const t = now(), h = H[mk.start]; if (!h) return null;
  const coh = nom.startsWith("cohorte B") ? "B" : "A";
  const at = (s) => { for (let i = h.r.length - 1; i >= 0; i--) if (t - h.r[i].t >= s) return h.r[i]; return null; };
  const r1 = at(1), r3 = at(3), a0 = k[0], z0 = k[1];
  const B = livres[up ? mk.up : mk.down]; const b0 = B ? Math.max(0, ...[...B.bids].filter((x) => x[1] > 0).map((x) => x[0])) : 0;
  const mid = b0 > 0 ? (a0 + b0) / 2 : a0;
  const pc = sigm(MC.cal.b + MC.cal.coef[0] * lgt(fair) + MC.cal.coef[1] * lgt(mid) + MC.cal.coef[2] * (coh === "B" ? 1 : 0));
  const askDe = (r) => (r ? (up ? r.ua : r.da) : null), zDe = (r) => (r ? (up ? r.uz : r.dz) : null);
  const fairDe = (r) => { if (!r) return null; const p = coh === "B" ? r.pu015 : r.pu; return p == null ? null : (up ? p : 1 - p); };
  const pts = h.r.filter((r) => t - r.t <= 30 && r.perp != null).map((r) => r.perp); let vol = 0;
  if (pts.length > 5) { const d = []; for (let i = 1; i < pts.length; i++) d.push(pts[i] - pts[i - 1]); const m = d.reduce((a, b) => a + b, 0) / d.length; vol = Math.sqrt(d.reduce((a, b) => a + (b - m) ** 2, 0) / d.length); }
  const ag = (src) => Math.min(10, CHG[src] ? t - CHG[src] : 10);
  const a1 = askDe(r1), a3 = askDe(r3), z1 = zDe(r1), f3 = fairDe(r3);
  const v = [lgt(pc), lgt(a0), Math.log1p(z0), pc - a0, a1 != null ? a0 - a1 : 0, a3 != null ? a0 - a3 : 0, z1 != null ? Math.log1p(z0) - Math.log1p(z1) : 0,
    f3 != null ? fair - f3 : 0, (mk.end - t) / 300, vol, b0 > 0 ? a0 - b0 : 0.05, ag("perp"), ag("okx"), ag("cl"), coh === "B" ? 1 : 0];
  const zn = v.map((x, i) => (x - MC.mu[i]) / MC.sd[i]);
  const ps = sigm(lin(MC.ms, zn)), pw = sigm(lin(MC.mw, zn));
  const ev = ps * (pw - a0 - FEE(a0)), envoie = ev > MC.marge, cap = envoie ? Math.max(a0, plafondC(pw, MC.marge)) : null;
  return { coh, pc: +pc.toFixed(4), ps: +ps.toFixed(4), pw: +pw.toFixed(4), ev: +ev.toFixed(4), envoie, plafond: cap, variables: v.map((x) => +(+x).toFixed(4)) };
}
function achetableJusqua(id, cap, budget = 50) {          // ordre fictif limite au plafond : parts et coût sur toute la profondeur ≤ plafond
  let q = 0, c = 0; for (const [p, sz] of asksTries(id)) { if (p > cap + 1e-9) break; const k = Math.min(sz, (budget - c) / (p + FEE(p))); if (k <= 0) break; q += k; c += k * p + k * FEE(p); }
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
  if (nom.startsWith("cohorte")) {
    try {
      const C = moteurC(nom, mk, up, k, fair); S.moteurC = C;
      if (C && C.envoie) {
        const rtt = med(STAT.rttClob) || 30, lat = Math.round(rtt);   // ordre fictif « envoyé » maintenant, arrivé après l'aller-retour mesuré vers Polymarket
        S.moteurC.remplissage = {};
        for (const d of [lat, 100, 300]) setTimeout(() => { S.moteurC.remplissage[d === lat ? "latence_" + lat + "ms" : d + "ms"] = achetableJusqua(id, C.plafond); }, d);
      }
    } catch (e) { S.moteurC = { erreur: e.message }; }
  }
  try { makerSurSignal(S, mk, up, nom); } catch (e) { log("maker", e.message); }
  SIGNAUX.push(S);
  try { const R = recDe(mk.start); R.sig.push({ nom, cote: S.cote, tDecision: S.tDecision, a0: S.a0, q0: S.q0, modele: S.modele, ecart: S.ecart, restant_s: S.restant_s, declencheur: source });
    R.dec.push([S.tDecision, nom, "signal", S.cote, S.a0]); } catch (_) {}
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

// ---------------------------------------------------------------- FANTÔMES MAKER (11.10.2026, demandés par Pitch) — AUCUN ORDRE
// Une offre d'achat est « posée » dans le carnet (jamais exécutée tout de suite : rejetée si elle croiserait le meilleur vendeur, comme un ordre
// « post only »). Elle arrive chez Polymarket après le trajet simple mesuré (moitié de l'aller-retour), une annulation aussi. Les ordres posés ne
// subissent pas le retard de 150 ms des preneurs. Place dans la file : on se met derrière tout ce qui est affiché à ce prix (ou seul au prix si on
// améliore le meilleur acheteur). Les carnets Up et Down sont miroirs : une vente de Up à p ou un achat de Down à 1 − p consomment le même niveau.
//   remplissage PRUDENT : seules les transactions nous font avancer ; la file devant nous ne dépasse jamais la taille affichée.
//   remplissage PROPORTIONNEL : en plus, les retraits sans transaction (300 ms autour) libèrent la file au prorata de notre place.
// Aucun remplissage n'est certain : ce sont deux estimations, toutes deux rapportées. Aucun frais pour les offres posées ; la ristourne maker
// n'est pas comptée. Sélection adverse : milieu du carnet et modèle à +1, +3, +5, +10 s après chaque remplissage. Résultat au règlement.
// Tous les paramètres ci-dessous sont FIXÉS AVANT la mesure (aucun ajustement sur les résultats).
const OFFRES = [], MAKER_FINIS = [], MSTAT = {}, TRX = []; let oidN = 0;
const LAT = () => Math.max(5, Math.round((med(STAT.rttClob) || 30) / 2));
const r2 = (x) => Math.round(x * 100) / 100;
const DP = {};                                                              // dernière probabilité du modèle par cycle (pour les mesures)
function meilleurAcheteur(id) { const L = livres[id]; let b = 0; if (L) for (const [p, z] of L.bids) if (z > 0 && p > b) b = p; return b; }
function milieu(id) { const b = meilleurAcheteur(id), a = asksTries(id)[0]; return b > 0 && a ? (b + a[0]) / 2 : null; }
function autreJeton(id) { const [st, k] = tokIdx(id); if (st == null) return null; return k === 0 ? M[st].down : M[st].up; }
function mstat(v) { return (MSTAT[v] = MSTAT[v] || { posees: 0, rejetees: 0, annulees: 0, remplies: 0, retraitsToxiques: 0 }); }
function fairDe(O) { const d = DP[O.start]; return d && d.pu != null ? +(O.cote === "Up" ? d.pu : 1 - d.pu).toFixed(4) : null; }
function poser(variante, mk, up, prix, budget, info) {
  const id = up ? mk.up : mk.down, t = nowMs(), bb = meilleurAcheteur(id), as0 = asksTries(id)[0];
  const O = { oid: `${mk.start}:${++oidN}`, variante, start: mk.start, cote: up ? "Up" : "Down", id, prix, parts: +(budget / prix).toFixed(2), tPose: +t.toFixed(1), lat_ms: LAT(),
    restantPose_s: +(mk.end - t / 1000).toFixed(2), acheteurPose: bb, vendeurPose: as0 ? as0[0] : null, niveauPose: livres[id] ? +(livres[id].bids.get(prix) || 0).toFixed(2) : 0,
    etat: "envoi", qDevant: null, qp: null, qr: null, remplP: 0, remplR: 0, premierRempl_ms: null, rempl: [], mo: { p: {}, r: {} }, moModele: { p: {}, r: {} }, ...info };
  OFFRES.push(O); mstat(variante).posees++;
  setTimeout(() => {
    if (O.etat !== "envoi") return;
    const as = asksTries(id)[0];
    if (as && as[0] <= prix + 1e-9) { O.etat = "rejetee"; O.raison = "croiserait le vendeur (post only)"; mstat(variante).rejetees++; return; }
    const b = meilleurAcheteur(id), q = prix > b + 1e-9 || !livres[id] ? 0 : (livres[id].bids.get(prix) || 0);
    O.qDevant = +q.toFixed(2); O.qp = q; O.qr = q; O.etat = "posee"; O.tArrivee = +nowMs().toFixed(1);
  }, O.lat_ms);
  try { if (variante.startsWith("M1") || variante.startsWith("M0")) recDe(mk.start).dec.push([+t.toFixed(1), variante, "offre posee", O.cote, prix]); } catch (_) {}
  return O;
}
function annuler(O, raison) {
  if (O.tAnnulDemande || !(O.etat === "envoi" || O.etat === "posee")) return;
  O.tAnnulDemande = +nowMs().toFixed(1); O.raison = raison;
  setTimeout(() => { if (O.etat === "posee" || O.etat === "envoi") { O.etat = "annulee"; O.tAnnulee = +nowMs().toFixed(1); mstat(O.variante).annulees++; } }, LAT());
}
function remplir(O, k, n) {
  const cle = k === "p" ? "remplP" : "remplR", reste = O.parts - O[cle]; if (reste <= 1e-9 || n <= 0) return;
  const x = Math.min(reste, n); O[cle] = +(O[cle] + x).toFixed(4);
  if (O.premierRempl_ms == null) { O.premierRempl_ms = +(nowMs() - O.tPose).toFixed(1); O.qDevantAuRempl = { p: O.qp, r: O.qr }; O.fairAuRempl = fairDe(O); mstat(O.variante).remplies++; }
  if (O.rempl.length < 40) O.rempl.push([+(nowMs() - O.tPose).toFixed(1), k, +x.toFixed(2)]);
  for (const h of [1, 3, 5, 10]) setTimeout(() => {                         // sélection adverse : où en est le carnet (et le modèle) h secondes plus tard ?
    const m = milieu(O.id), f = fairDe(O);
    if (m != null) { const a = (O.mo[k][h] = O.mo[k][h] || [0, 0]); a[0] += x * (m - O.prix); a[1] += x; }
    if (f != null) { const a = (O.moModele[k][h] = O.moModele[k][h] || [0, 0]); a[0] += x * (f - O.prix); a[1] += x; }
  }, h * 1000);
}
function makerTransaction(tok, side, q, v) {               // vente sur ce jeton à q → acheteurs de ce jeton à q ; achat → acheteurs de l'autre jeton à 1 − q
  const bidTok = side === "SELL" ? tok : autreJeton(tok); if (!bidTok) return;
  const pb = side === "SELL" ? q : Math.round((1 - q) * 1000) / 1000, t = nowMs();
  TRX.push({ tok: bidTok, p: pb, v, t, u: 0 }); while (TRX.length && t - TRX[0].t > 30000) TRX.shift();
  for (const O of OFFRES) {
    if (O.etat !== "posee" || O.id !== bidTok) continue;
    if (pb < O.prix - 1e-9) { remplir(O, "p", Infinity); remplir(O, "r", Infinity); continue; }   // niveau traversé : tout notre prix est parti
    if (Math.abs(pb - O.prix) > 1e-9) continue;
    O.qp -= v; O.qr -= v;
    if (O.qp < 0) { remplir(O, "p", -O.qp); O.qp = 0; }
    if (O.qr < 0) { remplir(O, "r", -O.qr); O.qr = 0; }
  }
}
function makerNiveau(tok, p, avant, apres) {
  for (const O of OFFRES) {
    if (O.etat !== "posee" || O.id !== tok || Math.abs(p - O.prix) > 1e-9) continue;
    O.qp = Math.min(O.qp, apres);                                         // prudent : la file devant nous ne dépasse jamais l'affiché
    const d = avant - apres; if (d <= 1e-9 || avant <= 0) continue;
    const frac = Math.min(1, O.qr / avant), t = nowMs();
    setTimeout(() => {                                                    // proportionnel : retrait sans transaction → part devant nous
      let reste = d; for (const x of TRX) { if (x.tok !== tok || Math.abs(x.p - p) > 1e-9 || Math.abs(x.t - t) > 300) continue; const u = Math.min(reste, x.v - x.u); x.u += u; reste -= u; if (reste <= 1e-9) break; }
      if (reste > 1e-9 && O.etat === "posee") O.qr = Math.max(0, O.qr - reste * frac);
    }, 300);
  }
}
// ---- mouvements et flux agressifs des bourses (pour M4), toutes les 50 ms ; aucune donnée n'est réutilisée par les règles existantes
const MOV = [], FLOW2 = { net: 0 };
setInterval(() => {
  const t = now(), px = ["perp", "okx", "bn", "cb"].filter((k) => f[k] && t - f[k].t < 2).map((k) => f[k].p);
  MOV.push([t, px.length ? med(px) : null, FLOW2.net]); FLOW2.net = 0; while (MOV.length > 200) MOV.shift();
}, 50);
function mouvement(ms) { const t = now(); let p0 = null, fl = 0; const p1 = MOV.length ? MOV[MOV.length - 1][1] : null;
  for (let i = MOV.length - 1; i >= 0; i--) { if (t - MOV[i][0] > ms / 1000) { p0 = MOV[i][1]; break; } fl += MOV[i][2]; }
  return { dp: p0 != null && p1 != null ? p1 - p0 : 0, flux: fl }; }
// ---- probabilité avec un prix BTC imposé (copie de proba(), pour M3 : « ce que dirait le marché s'il ne regardait que le dernier Chainlink »)
function probaAvecS(mk, sdRel, S) {
  if (!mk || !mk.strike || !f.cl || !sgc) return null;
  const sg = sgc.v, t = now(), ts = Math.floor(t), deb = mk.end - 60; let E, v;
  if (ts >= deb) { const connus = []; for (let s2 = deb; s2 <= Math.min(ts, mk.end - 1); s2++) { const x = prixA("cl", s2); if (x) connus.push(x); }
    const nr = Math.max(1, mk.end - 1 - ts); E = (connus.reduce((x, y) => x + y, 0) + nr * S) / (connus.length + nr); v = (sg * S) ** 2 * nr ** 3 / 3 / 3600; }
  else { E = S; v = (sg * S) ** 2 * ((deb - ts) + 20); }
  return phi((E - mk.strike) / Math.sqrt(v + (sdRel * S) ** 2));
}
const MODELE_REGLE = (nom) => (nom.includes("0,01 %") ? "pu01" : nom.startsWith("cohorte B") ? "pu015" : "pu");
// M1 : sur chaque signal des règles de Dublin, au lieu d'acheter le vendeur, on pose une offre d'achat 1 c au-dessus du meilleur acheteur
// (ou au meilleur acheteur si l'écart vendeur-acheteur est de 1 c). 50 $. Annulée si le modèle de la règle ne dépasse plus notre prix de 5 c,
// après 30 s, ou à 5 s de la fin.
function prixAmeliore(id, a0) { const bb = meilleurAcheteur(id); if (!bb) return null; let p = r2(bb + 0.01); if (p >= a0 - 1e-9) p = r2(bb); return p < 0.04 || p > 0.96 ? null : p; }
function makerSurSignal(S, mk, up, nom) {
  const p = prixAmeliore(up ? mk.up : mk.down, S.a0); if (p == null) return;
  poser("M1 " + nom, mk, up, p, 50, { modeleCle: MODELE_REGLE(nom), modele: S.modele, a0: S.a0, annulModele: 0.05 });
}
// M0 TÉMOIN SANS SIGNAL : deux offres par cycle, à des instants et sur un côté tirés au hasard (entre 270 et 30 s de la fin), même prix et mêmes
// annulations que M1 (30 s, 5 s de la fin), sans condition de modèle. Sert de comparaison à M1 et à toutes les variantes.
// M2 : cotation permanente des deux côtés au prix du modèle moins une marge (5 c ou 10 c), arrondi au cent inférieur, toujours sous le vendeur.
// Re-cotée dès que le prix voulu change (annulation + nouvelle offre en fin de file). 50 $ au plus par côté et par cycle. De 290 à 10 s de la fin.
// M3 ANTICIPATION CHAINLINK : quand la probabilité calculée avec le prix des bourses (Chainlink prévu) dépasse d'au moins 3 c celle calculée avec le
// dernier Chainlink publié, on pose une offre sur le côté favorisé 1 c au-dessus du meilleur acheteur (au plus modèle − 2 c), avant la publication.
// Annulée 1 s après la publication d'un Chainlink plus récent, après 10 s, si l'écart passe sous 1 c, ou à 5 s de la fin. 50 $ par côté et par cycle.
// M4 RETRAIT TOXIQUE : exactement M2 marge 5 c, mais l'offre est retirée et le côté mis en pause 2 s dès qu'un signal toxique apparaît :
//   (a) prix médian des bourses −10 $ (ou +10 $ pour Down) en 300 ms ; (b) flux agressif net contre nous ≥ 250 000 $ en 250 ms (Bybit, OKX, Binance,
//   Coinbase) ; (c) au moins 100 parts vendues sur les acheteurs de notre jeton en 500 ms.
// M5 REMPLISSAGE ATTENDU (modèle de file a priori, sans apprentissage) : pour chaque prix possible (du meilleur acheteur jusqu'à modèle − 3 c, sous le
// vendeur), parts remplies attendues en 10 s = min(notre taille, max(0, ventes sur les acheteurs de ce jeton au rythme des 30 dernières secondes × 10 s
// − file devant nous)) ; espérance = parts attendues × (modèle − prix − 2 c de sélection adverse). On cote le prix qui maximise l'espérance,
// seulement si elle dépasse 0,50 $. Re-coté quand le meilleur prix change. 50 $ par côté et par cycle.
const M2 = [["M2 cotation marge 5 c", 0.05], ["M2 cotation marge 10 c", 0.10]];
const QS = {};
function coter(Q, v, mk, up, px, ok, info, t) {                          // gestion commune d'une offre permanente (M2, M3, M4, M5)
  const k = v + (up ? "U" : "D"), S2 = (Q[k] = Q[k] || { depense: 0, O: null, t: 0 });
  const cur = S2.O && (S2.O.etat === "posee" || S2.O.etat === "envoi") && !S2.O.tAnnulDemande ? S2.O : null;
  if (S2.O && S2.O !== cur) { S2.depense += S2.O.remplR * S2.O.prix; S2.O = cur; }
  const budget = 50 - S2.depense - (cur ? cur.remplR * cur.prix : 0);
  ok = ok && budget >= 1 && px != null && px >= 0.04 && px <= 0.96;
  if (cur && (!ok || Math.abs(cur.prix - px) > 1e-9)) { if (t - S2.t < 50 && ok) return S2; annuler(cur, ok ? "re-cotation" : (info && info.raisonHors) || "hors zone"); S2.depense += cur.remplR * cur.prix; S2.O = null; }
  if (!S2.O && ok && t - S2.t >= 50) { S2.O = poser(v, mk, up, px, budget, info); S2.t = t; }
  return S2;
}
function makerEvaluer(mk, tleft, ua, da, P) {
  const t = nowMs(), ts = t / 1000;
  DP[mk.start] = { pu: P.pu, t: ts }; for (const s of Object.keys(DP)) if (+s < mk.start - 600) delete DP[s];
  for (const O of OFFRES) {                                               // annulations M0 / M1 / M3
    if (O.start !== mk.start || !(O.etat === "posee" || O.etat === "envoi") || O.tAnnulDemande) continue;
    const v = O.variante;
    if (v.startsWith("M1") || v.startsWith("M0")) {
      const pk = O.modeleCle ? P[O.modeleCle] : null, fair = pk == null ? null : (O.cote === "Up" ? pk : 1 - pk);
      if (tleft < 5) annuler(O, "5 s de la fin"); else if (t - O.tPose > 30000) annuler(O, "30 s");
      else if (O.annulModele && fair != null && fair - O.prix < O.annulModele) annuler(O, "modele a moins de 5 c");
    }
  }
  const Q = (QS[mk.start] = QS[mk.start] || {});
  // M0 témoin
  if (!Q.m0) Q.m0 = [0, 1].map(() => ({ t: mk.start + 30 + Math.random() * 240, up: Math.random() < 0.5, fait: false }));
  for (const x of Q.m0) if (!x.fait && ts >= x.t) { x.fait = true; const id = x.up ? mk.up : mk.down, a = (x.up ? ua : da)[0], p = prixAmeliore(id, a);
    if (p != null) poser("M0 temoin aleatoire", mk, x.up, p, 50, { a0: a }); }
  const sides = [true, false];
  // M2
  for (const [v, marge] of M2) for (const up of sides) {
    const fair = up ? P.pu : 1 - P.pu, ask = (up ? ua : da)[0];
    const px = Math.min(Math.floor((fair - marge) * 100 + 1e-9) / 100, r2(ask - 0.01));
    coter(Q, v, mk, up, px, tleft > 10 && tleft < 290, { modele: +fair.toFixed(4), a0: ask }, t);
  }
  // M3
  const pcl = f.cl ? probaAvecS(mk, 8e-4, f.cl.p) : null;
  if (pcl != null) for (const up of sides) {
    const fair = up ? P.pu : 1 - P.pu, stale = up ? pcl : 1 - pcl, ecart = fair - stale, id = up ? mk.up : mk.down, ask = (up ? ua : da)[0];
    const k = "M3" + (up ? "U" : "D"), st = (Q[k + "etat"] = Q[k + "etat"] || { actif: false, obs: null, tDeb: 0 });
    if (!st.actif && ecart >= 0.03 && tleft > 10) { st.actif = true; st.obs = f.cl.tsSrc; st.tDeb = t; st.tPub = null; }
    if (st.actif) {
      if (st.tPub == null && f.cl.tsSrc > st.obs) st.tPub = t;
      const fin = tleft < 5 || t - st.tDeb > 10000 || ecart < 0.01 || (st.tPub != null && t - st.tPub > 1000);
      if (fin) st.actif = false;
      const p = prixAmeliore(id, ask), px = p == null ? null : Math.min(p, Math.floor((fair - 0.02) * 100 + 1e-9) / 100);
      coter(Q, "M3 anticipation Chainlink", mk, up, px, !fin, { modele: +fair.toFixed(4), modeleChainlinkSeul: +stale.toFixed(4), a0: ask, raisonHors: "Chainlink publie / fin" }, t);
    }
  }
  // M4
  const m300 = mouvement(300), m250 = mouvement(250);
  for (const up of sides) {
    const k = "M4" + (up ? "U" : "D"), id = up ? mk.up : mk.down, sens = up ? 1 : -1;
    let tox = null;
    if (sens * m300.dp <= -10) tox = "bourses -10 $ en 300 ms";
    else if (sens * m250.flux <= -250000) tox = "flux agressif contre nous";
    else { let vv = 0; for (let i = TRX.length - 1; i >= 0 && t - TRX[i].t <= 500; i--) if (TRX[i].tok === id) vv += TRX[i].v; if (vv >= 100) tox = "100 parts vendues en 500 ms"; }
    const S4 = Q[k + "pause"] || 0;
    if (tox && t >= S4) { Q[k + "pause"] = t + 2000; Q[k + "derniere"] = tox; const cur = Q["M4 retrait toxique" + (up ? "U" : "D")]; if (cur && cur.O && cur.O.etat === "posee") mstat("M4 retrait toxique").retraitsToxiques++; }
    const fair = up ? P.pu : 1 - P.pu, ask = (up ? ua : da)[0];
    const px = Math.min(Math.floor((fair - 0.05) * 100 + 1e-9) / 100, r2(ask - 0.01));
    coter(Q, "M4 retrait toxique", mk, up, px, tleft > 10 && tleft < 290 && t >= (Q[k + "pause"] || 0), { modele: +fair.toFixed(4), a0: ask, raisonHors: "toxique : " + (Q[k + "derniere"] || "") }, t);
  }
  // M5
  for (const up of sides) {
    const id = up ? mk.up : mk.down, fair = up ? P.pu : 1 - P.pu, ask = (up ? ua : da)[0], bb = meilleurAcheteur(id);
    let vol = 0; for (let i = TRX.length - 1; i >= 0 && t - TRX[i].t <= 30000; i--) if (TRX[i].tok === id) vol += TRX[i].v;
    const rythme10 = vol / 30 * 10; let best = null;
    if (bb > 0) for (let p = bb; p <= Math.min(ask - 0.01, fair - 0.03) + 1e-9; p = r2(p + 0.01)) {
      const q = p > bb + 1e-9 ? 0 : (livres[id].bids.get(p) || 0), taille = 50 / p, att = Math.min(taille, Math.max(0, rythme10 - q));
      const ev = att * (fair - p - 0.02); if (!best || ev > best.ev) best = { p: r2(p), ev, att, q };
    }
    const ok = tleft > 10 && tleft < 290 && best && best.ev >= 0.5;
    coter(Q, "M5 remplissage attendu", mk, up, ok ? best.p : null, ok, ok ? { modele: +fair.toFixed(4), a0: ask, evAttendue: +best.ev.toFixed(2), partsAttendues: +best.att.toFixed(1), rythme10s: +rythme10.toFixed(1) } : { raisonHors: "esperance < 0,50 $" }, t);
  }
}
function makerMenage(t) {                                                 // fin de vie des offres : enregistrement compact de TOUTES les offres dans le fichier du cycle
  for (let i = OFFRES.length - 1; i >= 0; i--) {
    const O = OFFRES[i];
    if (t > O.start + 300 && (O.etat === "posee" || O.etat === "envoi")) { O.etat = "fin du cycle"; }
    const fini = !(O.etat === "posee" || O.etat === "envoi");
    if (fini && !O.rec) { O.rec = true; try { if (REC[O.start]) REC[O.start].mk.push([O.variante, O.cote, O.prix, O.tPose, O.lat_ms, O.etat, O.qDevant, O.remplP, O.remplR, O.premierRempl_ms, O.restantPose_s, O.modele ?? null, O.acheteurPose, O.vendeurPose, O.niveauPose, O.tAnnulDemande || null, O.raison || null, O.evAttendue ?? null]); } catch (_) {} }
    if (fini && O.remplR <= 0 && O.remplP <= 0 && !(O.variante.startsWith("M1") || O.variante.startsWith("M0"))) { OFFRES.splice(i, 1); continue; }
    if (fini && t > O.start + 300) { OFFRES.splice(i, 1); MAKER_FINIS.push(O); }
  }
  for (const s of Object.keys(QS)) if (+s < t - 900) delete QS[s];
}
async function makerReglements() {
  const t = now(); makerMenage(t);
  for (const O of MAKER_FINIS) {
    if (O.resultat || t < O.start + 360) continue;
    const g = await gagnantDe(O.start); if (g == null) continue;
    O.gagnant = g; O.gagne = g === O.cote;
    O.resultat = { prudent: +(O.remplP * ((O.gagne ? 1 : 0) - O.prix)).toFixed(2), proportionnel: +(O.remplR * ((O.gagne ? 1 : 0) - O.prix)).toFixed(2) };
  }
}
setInterval(() => { try { makerMenage(now()); } catch (_) {} }, 2000);
const RESUMES = [];
setInterval(() => {                                                       // résumé par variante (compteurs), envoyé avec les offres réglées
  const t = now(); if (!Object.keys(MSTAT).length) return;
  RESUMES.push({ oid: "resume:" + Math.floor(t), start: Math.floor(t / 300) * 300, type: "resume", tPose: Math.floor(t * 1000), compteurs: JSON.parse(JSON.stringify(MSTAT)) });
  for (const k of Object.keys(MSTAT)) delete MSTAT[k];
}, 3600000);

// ---------------------------------------------------------------- CARNETS DES BOURSES (11.10.2026, H563-H586) — enregistrement seulement
// Binance spot (20 niveaux toutes les 100 ms) et Bybit perp (carnet 50 niveaux, mises à jour) : toutes les 100 ms, meilleur acheteur/vendeur, tailles,
// quantités cumulées à 5, 10, 20 et 50 $ du milieu, et (Bybit) baisses / ajouts de quantité à 20 $ du milieu depuis la dernière photo.
const OB = { bn: { b: new Map(), a: new Map(), dec: [0, 0], add: [0, 0], t: 0 }, by: { b: new Map(), a: new Map(), dec: [0, 0], add: [0, 0], t: 0 } };
function obAppliquer(o, cote, p, q, delta) {
  const m = cote === 0 ? o.b : o.a, avant = m.get(p) || 0;
  if (delta) { const d = q - avant; if (d < 0) o.dec[cote] -= d; else o.add[cote] += d; }
  if (q > 0) m.set(p, q); else m.delete(p);
}
function obPhoto(o) {
  let bb = 0, ba = Infinity; for (const p of o.b.keys()) if (p > bb) bb = p; for (const p of o.a.keys()) if (p < ba) ba = p;
  if (!bb || ba === Infinity) return null; const mid = (bb + ba) / 2, c = [5, 10, 20, 50], B = [0, 0, 0, 0], A = [0, 0, 0, 0];
  for (const [p, q] of o.b) for (let i = 0; i < 4; i++) if (mid - p <= c[i]) B[i] += q;
  for (const [p, q] of o.a) for (let i = 0; i < 4; i++) if (p - mid <= c[i]) A[i] += q;
  const r = (x) => +x.toFixed(4);
  return [bb, ba, r(o.b.get(bb)), r(o.a.get(ba)), ...B.map(r), ...A.map(r), r(o.dec[0]), r(o.dec[1]), r(o.add[0]), r(o.add[1])];
}
setInterval(() => {
  const t = nowMs(), start = Math.floor(t / 300000) * 300; const R = recDe(start); R.ob = R.ob || { format: "[reception_ms, age_ms, acheteur, vendeur, taille1 acheteur, taille1 vendeur, cumul acheteur 5/10/20/50 $, cumul vendeur 5/10/20/50 $, baisses acheteur, baisses vendeur, ajouts acheteur, ajouts vendeur] en BTC", bn: [], by: [] };
  for (const k of ["bn", "by"]) { const o = OB[k]; if (!o.t || t - o.t > 3000) continue; const ph = obPhoto(o); if (ph) R.ob[k].push([+t.toFixed(1), +(t - o.t).toFixed(1), ...ph]); o.dec = [0, 0]; o.add = [0, 0]; }
}, 100);

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
  if (muet("perp")) connecter("perp", "wss://stream.bybit.com/v5/public/linear", [JSON.stringify({ op: "subscribe", args: ["publicTrade.BTCUSDT", "allLiquidation.BTCUSDT"] })],
    (m) => { const tp = m.topic || "";
      if (tp.startsWith("allLiquidation")) { for (const y of m.data || []) flux50("liq_bybit", y.S === "Buy" ? "v" : "a", +y.v, +y.p); return; }   // Buy = position longue liquidée → vente forcée
      if (!tp.startsWith("publicTrade")) return; for (const y of m.data || []) flux50("perp", y.S === "Buy" ? "a" : "v", +y.v, +y.p);
      const x = (m.data || []).slice(-1)[0]; if (x) noter("perp", +x.p, +x.T); }, JSON.stringify({ op: "ping" }), 15000);
  if (muet("okx")) connecter("okx", "wss://ws.okx.com:8443/ws/v5/public", [JSON.stringify({ op: "subscribe", args: [{ channel: "trades", instId: "BTC-USDT-SWAP" }] })],
    (m) => { if (!(m.arg && m.arg.channel === "trades")) return; for (const y of m.data || []) flux50("okx", y.side === "buy" ? "a" : "v", +y.sz * 0.01, +y.px);
      const x = (m.data || []).slice(-1)[0]; if (x) noter("okx", +x.px, +x.ts); }, "ping", 20000);
  if (muet("bn")) connecter("bn", "wss://stream.binance.com:9443/ws/btcusdt@trade", [], (m) => { if (+m.p > 0) { flux50("bn", m.m ? "v" : "a", +m.q, +m.p); noter("bn", +m.p, +m.T); } });
  if (muet("cb")) connecter("cb", "wss://advanced-trade-ws.coinbase.com", [JSON.stringify({ type: "subscribe", product_ids: ["BTC-USD"], channel: "ticker" }), JSON.stringify({ type: "subscribe", product_ids: ["BTC-USD"], channel: "market_trades" })],
    (m) => { if (m.channel === "market_trades") { for (const ev of m.events || []) for (const y of ev.trades || []) flux50("cb", y.side === "BUY" ? "a" : "v", +y.size, +y.price); return; }
      if (m.channel !== "ticker") return; for (const ev of m.events || []) for (const x of ev.tickers || []) if (x.product_id === "BTC-USD" && x.price) noter("cb", +x.price, Date.parse(m.timestamp)); });
  if (muet("cl")) connecter("cl", "wss://ws-live-data.polymarket.com", [JSON.stringify({ action: "subscribe", subscriptions: [{ topic: "crypto_prices_chainlink", type: "*", filters: "" }] })],
    (m) => { if (m.topic !== "crypto_prices_chainlink") return; const p = m.payload || {}; if ((p.symbol || "").toUpperCase().startsWith("BTC") && +p.value > 0) {
      const tR = nowMs(), pub = +m.timestamp;                             // RTDS : payload.timestamp = observation Chainlink ; timestamp = envoi par l'éditeur
      if (pub > 0) { CLS.publication.push(pub - +p.timestamp); CLS.transport.push(tR - pub); if (CLS.publication.length > 2000) { CLS.publication.shift(); CLS.transport.shift(); } }
      chainlink("rtds", +p.value, +p.timestamp); } }, "PING", 5000);
  if (muet("bnd")) connecter("bnd", "wss://stream.binance.com:9443/ws/btcusdt@depth20@100ms", [], (m) => { if (!m.bids) return; const o = OB.bn;
      o.b = new Map(m.bids.map((x) => [+x[0], +x[1]])); o.a = new Map(m.asks.map((x) => [+x[0], +x[1]])); o.t = nowMs(); });
  if (muet("byob")) connecter("byob", "wss://stream.bybit.com/v5/public/linear", [JSON.stringify({ op: "subscribe", args: ["orderbook.50.BTCUSDT"] })], (m) => {
      if (!(m.topic || "").startsWith("orderbook")) return; const o = OB.by, d = m.data || {};
      if (m.type === "snapshot") { o.b = new Map(); o.a = new Map(); }
      for (const x of d.b || []) obAppliquer(o, 0, +x[0], +x[1], m.type === "delta"); for (const x of d.a || []) obAppliquer(o, 1, +x[0], +x[1], m.type === "delta"); o.t = nowMs(); }, JSON.stringify({ op: "ping" }), 15000);
  if (PB && muet("pb")) { CLS.pbAuth = false; connecter("pb", "wss://ws-live-v2.polymarket.com/ws", [JSON.stringify({ op: "auth", rid: "a1", auth: PB })], surPB, JSON.stringify({ op: "ping" }), 20000); }
}
// ---------------------------------------------------------------- PolyBolt (wss://ws-live-v2.polymarket.com/ws) : Chainlink BTC/USD et moyenne 60 s officielle
let PB = null, pbDemande = 0;
// traitement : retard de la boucle d'événements de Node (temps entre l'arrivée d'un message et son traitement), mesuré toutes les 100 ms
let bouclePrec = nowMs(); setInterval(() => { const t = nowMs(); CLS.boucle.push(Math.max(0, t - bouclePrec - 100)); if (CLS.boucle.length > 2000) CLS.boucle.shift(); bouclePrec = t; }, 100);
async function identifiantsPB() {
  if (PB || now() - pbDemande < 60) return; pbDemande = now();
  try { const d = await getJSON(`${U}/api/rapide/polycreds`, { headers: { "x-rapide": TOKEN } }); if (d && d.apiKey) { PB = d; log("PolyBolt : identifiants reçus"); } else CLS.pbErreur = "identifiants : " + JSON.stringify(d).slice(0, 200); }
  catch (e) { CLS.pbErreur = "identifiants : " + e.message; }
}
const tsMs = (x) => (typeof x === "number" ? (x < 1e12 ? x * 1000 : x) : Date.parse(x));
function surPB(m) {
  if (m.op === "authed") { CLS.pbAuth = true; CLS.pbErreur = null;
    WS.pb.ws.send(JSON.stringify({ op: "subscribe", rid: "s1", subscriptions: [{ channel: "price.crypto", filter: { symbol: "btcusd" } }, { channel: "price.crypto.twap", filter: { symbol: "btcusd", window_seconds: 60 } }] })); return; }
  if (m.op && m.op !== "pong" && m.op !== "subscribed") { CLS.pbErreur = JSON.stringify(m).slice(0, 300); return; }
  if (m.op === "subscribed") { (CLS.pbAbos = CLS.pbAbos || []).push(JSON.stringify(m).slice(0, 200)); return; }
  if ((CLS.exemples = CLS.exemples || []).length < 6) CLS.exemples.push(JSON.stringify(m).slice(0, 600));
  const P = m.payload || m.data || {}, top = String(m.topic || m.channel || "").replace(/^prices\./, "price."), typ = m.type || m.event || "update";
  if (typ === "subscribe" || m.snapshot) return;
  const sym = String(P.symbol || m.symbol || (m.filter && m.filter.symbol) || "btcusd").toLowerCase(); if (sym !== "btcusd") return;
  if (P.source || m.source) CLS.source = P.source || m.source;
  const v = +(P.full_accuracy_value || P.value || P.price), obs = tsMs(P.timestamp || P.ts || m.timestamp);
  if (top === "price.crypto") chainlink("pb", v, obs);
  else if (top === "price.crypto.twap") {
    const t = nowMs(); CLS.twap.push(t - obs); if (CLS.twap.length > 2000) CLS.twap.shift();
    try { recDe(Math.floor(t / 300000) * 300).tw.push([+t.toFixed(1), obs, v]); } catch (_) {}
    const st = Math.round(obs / 1000); if (st % 300 === 0 && M[st] && !M[st].strikeTwap) M[st].strikeTwap = v;      // moyenne officielle à l'instant du début (à comparer à notre prix à battre)
  }
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
  identifiantsPB().catch(() => {});
  for (const s of Object.keys(H)) if (+s < start - 600) delete H[s];
  for (const s of Object.keys(M)) if (+s < start - 900) delete M[s];
  flux();
}
// ---------------------------------------------------------------- résultat des cycles, latence vers Polymarket, envoi au bot Cloudflare
const RES = {};
async function gagnantDe(start) {
  if (RES[start] !== undefined && RES[start] !== null) return RES[start];
  try { const ev = await getJSON(`${G}/events?slug=btc-updown-5m-${start}`); const m = ev[0].markets[0];
    const px = JSON.parse(m.outcomePrices || "[]").map(Number), outs = JSON.parse(m.outcomes || "[]");
    const g = px.includes(1) ? outs[px.indexOf(1)] : null; if (g != null) RES[start] = g; return g; } catch (_) { return null; }
}
async function reglements() {
  await makerReglements().catch((e) => log("maker reglements", e.message));
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
    if (S.moteurC && S.moteurC.remplissage) S.moteurC.resultat = Object.fromEntries(Object.entries(S.moteurC.remplissage).map(([k2, x]) => [k2, pn(x)]));
    FINIS.push(S); S.envoye = true;
  }
  for (let i = SIGNAUX.length - 1; i >= 0; i--) if (SIGNAUX[i].envoye || now() - SIGNAUX[i].tDecision / 1000 > 1800) SIGNAUX.splice(i, 1);
}
async function sonde() {                       // aller-retour HTTP vers le serveur de Polymarket
  try { const t0 = nowMs(); await fetch(`${CLOB}/time`).then((r) => r.text()); STAT.rttClob.push(+(nowMs() - t0).toFixed(2)); if (STAT.rttClob.length > 500) STAT.rttClob.shift(); } catch (_) {}
}
async function envoyer() {
  const regles = []; for (let i = MAKER_FINIS.length - 1; i >= 0; i--) if (MAKER_FINIS[i].resultat) { const { id, ...o } = MAKER_FINIS[i]; regles.push(o); MAKER_FINIS.splice(i, 1); }
  regles.push(...RESUMES.splice(0, RESUMES.length));
  const qd = (L) => ({ med: med(L), p10: qtl(L, 0.1), p90: qtl(L, 0.9), n: L.length });
  const enCours = {}; for (const O of OFFRES) { const e = (enCours[O.variante] = enCours[O.variante] || { posees: 0, remplies: 0 }); if (O.etat === "posee") e.posees++; if (O.remplR > 0) e.remplies++; }
  const corps = { version: VERSION, t: now(), signaux: FINIS.splice(0, FINIS.length).map(({ id, fini, envoye, ...s }) => s), maker: regles, makerEnCours: { offres: enCours, compteurs: MSTAT },
    chainlink: { decomposition_rtds_ms: { publication: qd(CLS.publication), transport: qd(CLS.transport), traitement_boucle: qd(CLS.boucle) }, rtds_ms: qd(CLS.delai.rtds), polybolt_ms: qd(CLS.delai.pb), twap_ms: qd(CLS.twap), premier: CLS.premier, avanceDuPremier_ms: { rtds: med(CLS.avance.filter((x) => x[0] === "rtds").map((x) => x[1])), polybolt: med(CLS.avance.filter((x) => x[0] === "pb").map((x) => x[1])) },
      messages: CLS.n, exemples: CLS.exemples || [], abonnements: CLS.pbAbos || [], polyboltConnecte: CLS.pbAuth, polyboltErreur: CLS.pbErreur, source: CLS.source, identifiants: !!PB },
    latence: { rttClob_ms: { med: med(STAT.rttClob), p10: qtl(STAT.rttClob, 0.1), p90: qtl(STAT.rttClob, 0.9), n: STAT.rttClob.length },
      polyVersNous_ms: { med: med(STAT.retardPoly), p10: qtl(STAT.retardPoly, 0.1), p90: qtl(STAT.retardPoly, 0.9) },
      calcul_us: { med: med(STAT.decisionUs), p90: qtl(STAT.decisionUs, 0.9) }, evaluations: STAT.evaluations },
    systeme: (() => { const m = process.memoryUsage(); let disque = null; try { const d = fs.statfsSync(DIR); disque = { libre_Mo: Math.round(d.bavail * d.bsize / 1e6), total_Mo: Math.round(d.blocks * d.bsize / 1e6) }; } catch (_) {}
      return { rss_Mo: Math.round(m.rss / 1e6), tas_Mo: Math.round(m.heapUsed / 1e6), disque, dernierCycle: STAT.dernierCycle || null }; })(),
    flux: Object.fromEntries(["perp", "okx", "bn", "cb", "cl", "pb", "bnd", "byob", "poly"].map((k) => [k, WS[k] ? { muet_s: +(now() - WS[k].msg).toFixed(1), reconnexions: WS[k].n } : null])) };
  try {
    const r = await fetch(`${U}/api/rapide/donnees`, { method: "POST", headers: { "content-type": "application/json", "x-rapide": TOKEN }, body: JSON.stringify(corps) });
    if (!r.ok) { log("envoi HTTP", r.status); FINIS.unshift(...corps.signaux); MAKER_FINIS.push(...corps.maker.filter((x) => x.type !== "resume")); }
  } catch (e) { log("envoi", e.message); FINIS.unshift(...corps.signaux); MAKER_FINIS.push(...corps.maker.filter((x) => x.type !== "resume")); }
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
