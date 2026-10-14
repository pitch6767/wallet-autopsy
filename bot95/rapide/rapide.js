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
  if (src === "okx" || src === "bn" || src === "cb") { const H = (HMS[src] = HMS[src] || []), tm = nowMs(); H.push([tm, p]); while (H.length && H[0][0] < tm - 2000) H.shift(); }
  if (src === "perp") { try { cpSurPerp(p); } catch (_) {} try { cp5SurPerp(p); } catch (_) {} }
  if (src === "perp" || src === "okx") evaluer(src);
}
// ---------------------------------------------------------------- FANTÔME CP10 « jambe + couverture posée » (H1059, accord de Pitch 13.10.2026 12:01)
// Le perp bouge d'au moins 10 $ en 300 ms (30 à 280 s écoulées, pause 5 s) ; côté X du mouvement au meilleur vendeur 0,40–0,70 ; achat fictif
// preneur 10 $ sur le carnet vu à +164 ms (limite + 1 c) ; au même instant, achat fictif POSÉ de l'opposé au prix b = 1 − 0,06 − prix payé
// (arrondi inférieur au centime) : exécuté tout de suite si le vendeur de l'opposé est déjà ≤ b (preneur), sinon rempli (prudent) quand le
// vendeur de l'opposé descend à b − 1 c dans les 10 s (optimiste : touche b) ; sinon X gardé jusqu'au règlement. Enregistré dans le
// fichier du cycle (clé « cp »). AUCUN ORDRE RÉEL.
// ---- FANTÔMES FG150 / FG300 « contre les gros preneurs » (H1060, accord de Pitch 13.10.2026 15:41 « Oui 150 et 300 $ ») : une transaction
// Polymarket d'au moins 150 $ (FG150) ou 300 $ (FG300), 30 à 280 s écoulées, pause 3 s par cycle (comptée sur 150 $) ; côté poussé X =
// acheté par le preneur ; si le meilleur vendeur de X est entre 0,40 et 0,70 : achat fictif de l'AUTRE côté, 10 $, carnet vu à +164 ms,
// limite + 1 c, gardé jusqu'au règlement. Enregistré dans le fichier du cycle (clé « fg »). AUCUN ORDRE RÉEL.
// 13.10.2026 15:51 : règlement des fantômes de Dublin et envoi au bot Cloudflare pour le classement (clé « fantomes » de l'envoi).
const FANT = [], FANT_REGLES = [];
async function fantReglements() {
  const t = now();
  for (let i = FANT.length - 1; i >= 0; i--) {
    const E = FANT[i];
    if (t < E.start + 330) continue;
    if (!(E.q > 0) || E.c < (E.montant ? E.montant / 2 : 5)) { FANT.splice(i, 1); continue; }
    const g = await gagnantDe(E.start); if (g == null) { if (t > E.start + 3600) FANT.splice(i, 1); continue; }
    const win = g === E.cote ? 1 : 0, q = E.q, c = E.c, garde = q * win - c, h = new Date(E.t).toISOString();
    const L = (nom, net, detail) => FANT_REGLES.push({ id: nom + "|" + E.start + "|" + Math.round(E.t), nom, actif: "BTC", start: E.start, heure: h, cote: E.cote, prix: +(c / q).toFixed(4), parts: q, net: +net.toFixed(2), issue: detail.split(" ")[0], detail });
    const couv = (x) => x ? (x.mode === "preneur" ? q - c - q * (x.px + FEE7(x.px)) : q - c - q * x.px) : null;
    if (E.regle === "CP10") { const v = couv(E.couv); L("CP10 couverture posee", v ?? garde, v != null ? "couvert à " + E.couv.px : "gardé, " + (win ? "gagné" : "perdu")); }
    else if (E.regle === "JC5/CP5") {
      const vj = E.jc5 ? E.jc5.q - c - E.jc5.c + (q - E.jc5.q) * win : null; L("JC5 couverture preneur", vj ?? garde, vj != null ? "couvert à " + E.jc5.px : "gardé, " + (win ? "gagné" : "perdu"));
      // 14.10.2026 09:26 (Pitch : « oui rajoute svp ») : JC10 (H1058) = mêmes entrées que JC5 quand le saut du perp est ≥ 10 $. AUCUN ORDRE RÉEL.
      if (Math.abs(E.d || 0) >= 10) L("JC10 couverture preneur", vj ?? garde, vj != null ? "couvert à " + E.jc5.px : "gardé, " + (win ? "gagné" : "perdu"));
      const vc = couv(E.cp5); L("CP5 couverture posee", vc ?? garde, vc != null ? "couvert à " + E.cp5.px : "gardé, " + (win ? "gagné" : "perdu"));
    } else if (E.regle && E.regle.startsWith("billet")) {
      const f = E.fav && E.fav.q > 0 ? E.fav.q * (1 - win) - E.fav.c : 0; L("billet + favori si recul 20 c", garde + f, (E.fav ? "couvert, " : "") + (win ? "billet gagné" : "billet perdu"));
    } else if (E.nomFant) L(E.nomFant, garde, (win ? "gagné" : "perdu") + (E.montant ? ", " + E.montant + " $" : ""));
    else if (E.regle === "PB") { for (const nom of E.regles || []) L(nom, garde, win ? "gagné" : "perdu"); }
    else if (E.regles) { for (const nom of E.regles) L(nom + " contre les gros", garde, (win ? "gagné" : "perdu") + " contre " + E.montant.toFixed(0) + " $"); }
    else if (["SA10", "SA10-5", "SAsig"].includes(E.regle)) L({ "SA10": "petit a petit 10 $", "SA10-5": "petit a petit 10 puis 5 $", "SAsig": "petit a petit selon le saut" }[E.regle], garde, (win ? "gagné" : "perdu") + ", " + E.montant + " $");
    FANT.splice(i, 1);
  }
}
const FGD = {};
function fgSurTrade(id, side, px, sz, tR) {
  const v = px * sz; if (!(v >= 150)) return;
  const [st, k] = tokIdx(id); if (st == null) return;
  const el = tR / 1000 - st; if (el < 30 || el > 280) return;
  if (FGD[st] && tR - FGD[st] < 3000) return;
  FGD[st] = tR; for (const s2 of Object.keys(FGD)) if (+s2 < st - 900) delete FGD[s2];
  const mk = M[st]; if (!mk || !mk.up || !mk.down) return;
  const X = side === "BUY" ? (k === 0 ? "Up" : "Down") : (k === 0 ? "Down" : "Up"), O = X === "Up" ? "Down" : "Up";
  const idX = X === "Up" ? mk.up : mk.down, idO = O === "Up" ? mk.up : mk.down;
  const a = asksTries(idX)[0], ao = asksTries(idO)[0];
  const E = { regles: v >= 300 ? ["FG150", "FG300"] : ["FG150"], t: +tR.toFixed(1), start: st, montant: +v.toFixed(2), pousse: X, cote: O, aX: a ? a[0] : null, aO: ao ? ao[0] : null, statut: "en cours" };
  const R = recDe(st); (R.fg = R.fg || []).push(E); FANT.push(E);
  if (!a || a[0] < 0.40 - 1e-9 || a[0] > 0.70 + 1e-9 || !ao) { E.statut = "hors zone"; return; }
  setTimeout(() => {
    let q = 0, c = 0;
    for (const [p2, z] of asksTries(idO)) { if (p2 > ao[0] + 0.01 + 1e-9) break; const u = p2 + FEE7(p2); const kk = Math.min(z, (10 - c) / u); if (kk <= 1e-9) break; q += kk; c += kk * u; }
    E.q = +q.toFixed(3); E.c = +c.toFixed(4); E.statut = q > 0 && c >= 5 ? "ouvert" : "non rempli";
  }, 164);
}
const CPH = []; let cpDernier = 0;
// ---- FANTÔMES JC5 et CP5 (H1058 / H1059, accord de Pitch 13.10.2026 14:36 « En fantôme svp ») : même entrée que CP10 mais saut du perp ≥ 5 $
// en 300 ms (pause 5 s propre à ce détecteur). Une seule jambe fictive (10 $, +164 ms), deux couvertures suivies en parallèle :
//   JC5 : toutes les 250 ms pendant 5 s, si prix payé + vendeur de l'opposé + frais ≤ 0,98 → achat preneur de l'opposé 250 ms plus tard ;
//   CP5 : couverture posée à 1 − 0,06 − prix payé, comme CP10 (prudent : vendeur ≤ b − 1 c ; optimiste : touche b), 10 s.
// Enregistré dans le fichier du cycle (clé « cp5 »). AUCUN ORDRE RÉEL.
// ---- FANTÔMES « petit à petit » (H1062, accord de Pitch 13.10.2026 19:30) : à chaque saut du perp ≥ 5 $ en 300 ms (même détecteur que JC5/CP5,
// côté 0,40–0,70), achat fictif preneur à +164 ms (limite + 1 c), gardé jusqu'au règlement, au plus 50 $ par cycle et par règle :
//   SA10 = 10 $ à chaque saut ; SA10-5 = 10 $ au 1er saut du cycle puis 5 $ ; SAsig = 5 $ si saut 5–10 $, 10 $ si saut ≥ 10 $.
// Enregistré dans le fichier du cycle (clé « sa »). AUCUN ORDRE RÉEL.
// ---- FANTÔMES « premier à bouger » (H1063, accord de Pitch 13.10.2026 20:05 « Go ») : même saut que JC5/CP5 (perp ≥ 5 $ en 300 ms, côté
// 0,40–0,70), achat fictif preneur 10 $ à +164 ms (limite + 1 c), gardé jusqu'au règlement, SEULEMENT si :
//   PB seul = aucune des bourses OKX / Binance / Coinbase n'a bougé de 2 $ ou plus dans le même sens sur les 300 ms (le perp bouge seul) ;
//   PB seul + Poly immobile = en plus, milieu Polymarket inchangé par rapport à 1 s avant.
// Enregistré dans le fichier du cycle (clé « pb »). AUCUN ORDRE RÉEL.
const HMS = {}, MIDH = [];
setInterval(() => { try { const t = nowMs(), start = Math.floor(t / 300000) * 300, mk = M[start]; if (!mk || !mk.up) return;
  const a = asksTries(mk.up)[0], L = livres[mk.up]; let b = null; if (L) for (const [px, z] of L.bids) if (z > 0 && (b == null || px > b)) b = px;
  if (a && b != null) { MIDH.push([t, start, +((a[0] + b) / 2).toFixed(4)]); while (MIDH.length && MIDH[0][0] < t - 10000) MIDH.shift(); } } catch (_) {} }, 100);
function mvMs(src, t) { const H = HMS[src]; if (!H || !H.length) return null; let p0 = null; for (const [tt, p] of H) { if (tt <= t - 300) p0 = p; else break; } return p0 == null ? null : H[H.length - 1][1] - p0; }
function pbSurSaut(start, X, idX, a0, d, t) {
  const sg = d > 0 ? 1 : -1, nconf = ["okx", "bn", "cb"].filter((k) => { const m = mvMs(k, t); return m != null && sg * m >= 2; }).length;
  let m1 = null, m0 = null; for (const [tt, s2, v] of MIDH) { if (s2 !== start) continue; if (tt <= t - 1000) m1 = v; m0 = v; }
  const immobile = m1 != null && m0 != null && Math.abs(m0 - m1) < 1e-9;
  const regles = nconf === 0 ? (immobile ? ["PB seul", "PB seul + Poly immobile"] : ["PB seul"]) : [];
  const E = { regle: "PB", regles, t: +t.toFixed(1), start, d: +d.toFixed(2), cote: X, a0, nconf, immobile, statut: regles.length ? "achat" : "filtré" };
  const R = recDe(start); (R.pb = R.pb || []).push(E); if (!regles.length) return; FANT.push(E);
  setTimeout(() => { let q = 0, c = 0;
    for (const [px, sz] of asksTries(idX)) { if (px > a0 + 0.01 + 1e-9) break; const u = px + FEE7(px); const k = Math.min(sz, (10 - c) / u); if (k <= 1e-9) break; q += k; c += k * u; }
    E.q = +q.toFixed(3); E.c = +c.toFixed(4); E.statut = q > 0 && c >= 5 ? "ouvert" : "non rempli"; if (E.statut !== "ouvert") E.q = 0; }, 164);
}
const SAB = {};
function saSurSaut(start, X, idX, a0, dAbs, t) {
  const B = (SAB[start] = SAB[start] || { "SA10": 0, "SA10-5": 0, "SAsig": 0, n: 0 });
  for (const s2 of Object.keys(SAB)) if (+s2 < start - 900) delete SAB[s2];
  const tailles = { "SA10": 10, "SA10-5": B.n === 0 ? 10 : 5, "SAsig": dAbs >= 10 ? 10 : 5 }; B.n++;
  for (const [regle, m] of Object.entries(tailles)) {
    if (B[regle] + m > 50 + 1e-9) continue;
    B[regle] += m;
    const E = { regle, t: +t.toFixed(1), start, d: +dAbs.toFixed(2), cote: X, a0, montant: m, statut: "achat" };
    const R = recDe(start); (R.sa = R.sa || []).push(E); FANT.push(E);
    setTimeout(() => { let q = 0, c = 0;
      for (const [px, sz] of asksTries(idX)) { if (px > a0 + 0.01 + 1e-9) break; const u = px + FEE7(px); const k = Math.min(sz, (m - c) / u); if (k <= 1e-9) break; q += k; c += k * u; }
      E.q = +q.toFixed(3); E.c = +c.toFixed(4); E.statut = q > 0 && c >= m / 2 ? "ouvert" : "non rempli"; if (E.statut !== "ouvert") E.q = 0; }, 164);
  }
}
const CP5H = []; let cp5Dernier = 0;
function cp5SurPerp(p) {
  const t = nowMs(); CP5H.push([t, p]); while (CP5H.length && CP5H[0][0] < t - 1000) CP5H.shift();
  let p0 = null; for (const [tt, pp] of CP5H) if (tt >= t - 300) { p0 = pp; break; }
  if (p0 == null) return;
  const d = p - p0;
  if (Math.abs(d) < 5 || t - cp5Dernier < 5000) return;
  const start = Math.floor(t / 300000) * 300, el = t / 1000 - start;
  if (el < 30 || el > 280) return;
  const mk = M[start]; if (!mk || !mk.up || !mk.down) return;
  cp5Dernier = t;
  const X = d > 0 ? "Up" : "Down", idX = X === "Up" ? mk.up : mk.down, idO = X === "Up" ? mk.down : mk.up;
  const a0 = asksTries(idX)[0];
  const E = { regle: "JC5/CP5", t: +t.toFixed(1), start, d: +d.toFixed(2), cote: X, a0: a0 ? a0[0] : null, statut: "en cours" };
  const R = recDe(start); (R.cp5 = R.cp5 || []).push(E); FANT.push(E);
  if (!a0 || a0[0] < 0.40 - 1e-9 || a0[0] > 0.70 + 1e-9) { E.statut = "hors zone"; return; }
  try { saSurSaut(start, X, idX, a0[0], Math.abs(d), t); } catch (_) {}
  try { pbSurSaut(start, X, idX, a0[0], d, t); } catch (_) {}
  setTimeout(() => {
    let q = 0, c = 0;
    for (const [px, sz] of asksTries(idX)) { if (px > a0[0] + 0.01 + 1e-9) break; const u = px + FEE7(px); const k = Math.min(sz, (10 - c) / u); if (k <= 1e-9) break; q += k; c += k * u; }
    E.q = +q.toFixed(3); E.c = +c.toFixed(4);
    if (q <= 0 || c < 5) { E.statut = "non rempli"; return; }
    E.statut = "ouvert";
    const pe = c / q, b = Math.floor((1 - 0.06 - pe) * 100 + 1e-9) / 100; E.b = b;
    const oa0 = asksTries(idO)[0];
    if (oa0 && oa0[0] <= b + 1e-9) { E.cp5 = { mode: "preneur", px: oa0[0], ms: 164 }; E.cp5opt = E.cp5; }
    let n = 0, jcFini = false;
    const iv = setInterval(() => {
      n++; const o = asksTries(idO)[0];
      if (!E.cp5) {
        if (o && !E.cp5opt && o[0] <= b + 1e-9) E.cp5opt = { mode: "posé", px: b, ms: 164 + 250 * n };
        if (o && o[0] <= b - 0.01 + 1e-9) E.cp5 = { mode: "posé", px: b, ms: 164 + 250 * n };
      }
      if (!jcFini && n <= 20 && o && pe + o[0] + FEE7(o[0]) <= 0.98 + 1e-9) {
        jcFini = true; const lim = o[0] + 0.01, nn = n;
        setTimeout(() => { let q2 = 0, c2 = 0; for (const [px, sz] of asksTries(idO)) { if (px > lim + 1e-9) break; const k = Math.min(sz, q - q2); if (k <= 1e-9) break; q2 += k; c2 += k * (px + FEE7(px)); }
          if (q2 >= 0.95 * q) E.jc5 = { px: o[0], q: +q2.toFixed(3), c: +c2.toFixed(4), ms: 164 + 250 * (nn + 1) }; }, 250);
      }
      if (n > 20) jcFini = true;
      if ((E.cp5 || n >= 40) && jcFini) { E.statut = "fini"; clearInterval(iv); }
    }, 250);
  }, 164);
}
function cpSurPerp(p) {
  const t = nowMs(); CPH.push([t, p]); while (CPH.length && CPH[0][0] < t - 1000) CPH.shift();
  let p0 = null; for (const [tt, pp] of CPH) if (tt >= t - 300) { p0 = pp; break; }
  if (p0 == null) return;
  const d = p - p0;
  if (Math.abs(d) < 10 || t - cpDernier < 5000) return;
  const start = Math.floor(t / 300000) * 300, el = t / 1000 - start;
  if (el < 30 || el > 280) return;
  const mk = M[start]; if (!mk || !mk.up || !mk.down) return;
  cpDernier = t;
  const X = d > 0 ? "Up" : "Down", idX = X === "Up" ? mk.up : mk.down, idO = X === "Up" ? mk.down : mk.up;
  const a0 = asksTries(idX)[0];
  const E = { regle: "CP10", t: +t.toFixed(1), start, d: +d.toFixed(2), cote: X, a0: a0 ? a0[0] : null, v0: asksTries(idX).slice(0, 3), statut: "en cours" };
  const R = recDe(start); (R.cp = R.cp || []).push(E); FANT.push(E);
  if (!a0 || a0[0] < 0.40 - 1e-9 || a0[0] > 0.70 + 1e-9) { E.statut = "hors zone"; return; }
  setTimeout(() => {
    let q = 0, c = 0;
    for (const [px, sz] of asksTries(idX)) { if (px > a0[0] + 0.01 + 1e-9) break; const u = px + FEE7(px); const k = Math.min(sz, (10 - c) / u); if (k <= 1e-9) break; q += k; c += k * u; }
    E.q = +q.toFixed(3); E.c = +c.toFixed(4); E.v164 = asksTries(idX).slice(0, 3); E.o164 = asksTries(idO).slice(0, 2);
    if (q <= 0 || c < 5) { E.statut = "non rempli"; return; }
    const b = Math.floor((1 - 0.06 - c / q) * 100 + 1e-9) / 100; E.b = b;
    const oa = asksTries(idO)[0];
    if (oa && oa[0] <= b + 1e-9) { E.couv = { mode: "preneur", px: oa[0], ms: 164 }; E.couvOpt = E.couv; E.statut = "couvert"; return; }
    let n = 0;
    const iv = setInterval(() => {
      n++; const o = asksTries(idO)[0];
      if (o && !E.couvOpt && o[0] <= b + 1e-9) E.couvOpt = { mode: "posé", px: b, ms: 164 + 250 * n };
      if (o && o[0] <= b - 0.01 + 1e-9) { E.couv = { mode: "posé", px: b, ms: 164 + 250 * n }; E.statut = "couvert"; clearInterval(iv); return; }
      if (n >= 40) { E.statut = "gardé"; clearInterval(iv); }
    }, 250);
  }, 164);
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
  if (R.ev.length >= 1000000) { R.coupe = true; return; }   // 12.10 : plafond 120 000 → 1 000 000 (10 cycles sur 362 tronqués ; Pitch : aucun cycle tronqué)
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
  if (m.event_type === "last_trade_price") { recEv(m.asset_id, ["T", +tR.toFixed(1), ts, m.side === "BUY" ? 1 : 0, +m.price, +m.size]); try { makerTransaction(m.asset_id, m.side, +m.price, +m.size); } catch (_) {} try { fgSurTrade(m.asset_id, m.side, +m.price, +m.size, tR); } catch (_) {} return; }
  if (m.event_type === "book") {
    recEv(m.asset_id, ["B", +tR.toFixed(1), ts, (m.bids || []).map((x) => [+x.price, +x.size]), (m.asks || []).map((x) => [+x.price, +x.size])]);
    const B = L(m.asset_id);
    try { for (const x of m.bids || []) makerNiveau(m.asset_id, +x.price, B.bids.get(+x.price) || 0, +x.size); } catch (_) {}
    B.bids = new Map((m.bids || []).map((x) => [+x.price, +x.size])); B.asks = new Map((m.asks || []).map((x) => [+x.price, +x.size]));
    B.tRecu = tR; B.tsPoly = ts; touches.add(m.asset_id);
  } else if (m.event_type === "price_change") {
    for (const c of m.price_changes || []) { recEv(c.asset_id, ["P", +tR.toFixed(1), ts, c.side === "BUY" ? 0 : 1, +c.price, +c.size]); const B = L(c.asset_id), cote = c.side === "BUY" ? B.bids : B.asks;
      const avant = cote.get(+c.price) || 0; +c.size ? cote.set(+c.price, +c.size) : cote.delete(+c.price); B.tRecu = tR; B.tsPoly = ts; touches.add(c.asset_id);
      try { PCH.push([tR, c.asset_id, c.side === "BUY" ? 0 : 1, +c.size - avant]); while (PCH.length && PCH[0][0] < tR - 4000) PCH.shift(); } catch (_) {}
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
// ---------------------------------------------------------------- R4 « RETRY ENGINE » (accord de Pitch, 11.10.2026 17:25) — FANTÔME, AUCUN ORDRE
// Sur chaque signal Bot95 (mêmes signaux, rien de changé dans leurs règles) : tentative « envoyée » à la décision, exécutée contre le carnet après
// trajet simple + 150 ms (retard preneur Polymarket). Sans exécution complète : nouvelle tentative toutes les 500 ms pendant 5 s (envois à 0, 0,5 … 4,5 s).
// Avant CHAQUE envoi : probabilité recalculée avec les données reçues à cet instant (même modèle que la règle) ; on n'achète que les niveaux où
// probabilité − prix − frais ≥ 0,05, au plus au plafond. Budget 50 $ par signal, fills partiels cumulés, jamais au-delà du budget.
// Variantes mesurées sur les MÊMES signaux (comparaisons demandées) : R4 (+2 c, recalcul), +1 c, prix initial, +2 c sans recalcul (modèle figé
// au signal), preneur immédiat (une seule tentative, prix du signal, sans condition = Bot95 actuel). Paramètres fixés avant la mesure.
// « doublon » : une variante du même cycle et du même côté a déjà exécuté → la position n'est pas comptée deux fois dans le résultat officiel.
const R4_VAR = [["R4", 0.02, true, true], ["R4 +1 c", 0.01, true, true], ["R4 prix initial", 0, true, true], ["R4 +2 c sans recalcul", 0.02, false, true], ["preneur immediat", 0, false, false]];
const R4_DEJA = {};                                                      // "start|cote|variante" → déjà exécuté
const SD_REGLE = { pu: 8e-4, pu01: 1e-4, pu015: 1.5e-4 };
function retrySurSignal(S, mk, up, nom) {
  const id = up ? mk.up : mk.down, a0 = S.a0, sd = SD_REGLE[MODELE_REGLE(nom)] || 8e-4;
  S.r4 = {};
  for (const [v, plaf, recalc, relance] of R4_VAR) {
    const cle = mk.start + "|" + S.cote + "|" + v, R = (S.r4[v] = { plafond: +(a0 + plaf).toFixed(3), q: 0, c: 0, tentatives: [], doublon: !!R4_DEJA[cle] });
    let budget = 50;
    const tenter = (k) => {
      if (budget <= 0.01 || (k > 0 && !relance)) return;
      const tEnvoi = nowMs();
      let p = null; try { const pp = recalc ? proba(mk, sd) : null; p = pp == null ? null : (up ? pp : 1 - pp); } catch (_) {}
      const prob = recalc ? p : S.modele;
      let lim = a0 + plaf;
      if (relance && prob != null) { while (lim > 0.005 && prob - lim - FEE(lim) < 0.05) lim = +(lim - 0.01).toFixed(2); }
      if (relance && prob == null) lim = -1;                                  // pas de modèle : pas d'achat
      const vu = asksTries(id)[0], lat = LAT();
      setTimeout(() => { try {
        const x = lim > 0 ? achetableJusqua(id, lim, budget) : { q: 0, c: 0 };
        if (x.q > 0) { R.q = +(R.q + x.q).toFixed(2); R.c = +(R.c + x.c).toFixed(2); budget -= x.c; if (!R.premier_ms) R.premier_ms = +(nowMs() - S.tDecision).toFixed(1); R4_DEJA[cle] = true; }
        R.tentatives.push([k, +(tEnvoi - S.tDecision).toFixed(1), prob == null ? null : +prob.toFixed(4), +lim.toFixed(3), vu ? vu[0] : null, vu ? +vu[1].toFixed(2) : null, x.q, x.c]);
        if (k < 9 && budget > 0.01 && relance) setTimeout(() => { try { tenter(k + 1); } catch (e) { log("r4", e.message); } }, Math.max(0, 500 * (k + 1) - (nowMs() - S.tDecision)));
      } catch (e) { log("r4", e.message); } }, lat + 150);
    };
    tenter(0);
  }
  // H776 : réapparition d'une offre ≤ prix du signal (et ≤ +2 c) après sa disparition, pendant 5 s
  S.r4req = { disparu_ms: null, retour_ms: null, retourPrix: null, retourQ: null, retour2c_ms: null, retour2cPrix: null, retour2cQ: null, probRetour: null };
  const t0 = S.tDecision, ech = () => { try {
    const dt = nowMs() - t0; if (dt > 5000) return;
    const a = achetable(id, a0), b = achetableJusqua(id, a0 + 0.02), Q = S.r4req;
    if (Q.disparu_ms == null) { if (a.q < 1) Q.disparu_ms = +dt.toFixed(1); }
    else {
      if (Q.retour_ms == null && a.q >= 1) { Q.retour_ms = +dt.toFixed(1); Q.retourPrix = asksTries(id)[0] ? asksTries(id)[0][0] : null; Q.retourQ = a.q; try { const pp = proba(mk, sd); Q.probRetour = pp == null ? null : +(up ? pp : 1 - pp).toFixed(4); } catch (_) {} }
      if (Q.retour2c_ms == null && b.q >= 1) { Q.retour2c_ms = +dt.toFixed(1); Q.retour2cPrix = asksTries(id)[0] ? asksTries(id)[0][0] : null; Q.retour2cQ = b.q; }
    }
    setTimeout(ech, 25);
  } catch (e) { log("r4req", e.message); } };
  setTimeout(ech, 1);
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
  try { retrySurSignal(S, mk, up, nom); } catch (e) { log("r4", e.message); }
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
    etat: "envoi", qDevant: null, qp: null, qr: null, qo: null, remplP: 0, remplR: 0, remplO: 0, annulP: 0, annulR: 0, premierRempl_ms: null, rempl: [], mo: { p: {}, r: {}, o: {} }, moModele: { p: {}, r: {}, o: {} }, toxRempl: [], ...info };
  OFFRES.push(O); mstat(variante).posees++;
  setTimeout(() => {
    if (O.etat !== "envoi") return;
    const as = asksTries(id)[0];
    if (as && as[0] <= prix + 1e-9) { O.etat = "rejetee"; O.raison = "croiserait le vendeur (post only)"; mstat(variante).rejetees++; return; }
    const b = meilleurAcheteur(id), q = prix > b + 1e-9 || !livres[id] ? 0 : (livres[id].bids.get(prix) || 0);
    O.qDevant = +q.toFixed(2); O.qp = q; O.qr = q; O.qo = q; O.etat = "posee"; O.tArrivee = +nowMs().toFixed(1);
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
  const cle = k === "p" ? "remplP" : k === "r" ? "remplR" : "remplO", reste = O.parts - O[cle]; if (reste <= 1e-9 || n <= 0) return;
  const x = Math.min(reste, n); O[cle] = +(O[cle] + x).toFixed(4);
  if (O.tAnnulDemande && k !== "o") { const c2 = k === "p" ? "annulP" : "annulR"; O[c2] = +(O[c2] + x).toFixed(4); }   // rempli APRÈS la demande d'annulation (pendant son trajet)
  if (k === "p" && O.toxRempl.length < 40) O.toxRempl.push([+x.toFixed(2), toxActifs(O)]);
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
    if (pb < O.prix - 1e-9) { remplir(O, "p", Infinity); remplir(O, "r", Infinity); remplir(O, "o", Infinity); continue; }   // niveau traversé : tout notre prix est parti
    if (Math.abs(pb - O.prix) > 1e-9) continue;
    O.qp -= v; O.qr -= v; O.qo -= v;
    if (O.qp < 0) { remplir(O, "p", -O.qp); O.qp = 0; }
    if (O.qr < 0) { remplir(O, "r", -O.qr); O.qr = 0; }
    if (O.qo < 0) { remplir(O, "o", -O.qo); O.qo = 0; }
  }
}
// File d'attente, trois bornes (aucune n'est certaine) :
//   PRUDENTE : seules les transactions nous font avancer ; file devant ≤ quantité affichée.
//   CENTRALE (proportionnelle) : un retrait sans transaction libère la file au prorata de notre place.
//   OPTIMISTE : tout retrait sans transaction vient de devant nous.
function makerNiveau(tok, p, avant, apres) {
  const d = avant - apres, t = nowMs(), vis = [];
  for (const O of OFFRES) {
    if (O.etat !== "posee" || O.id !== tok || Math.abs(p - O.prix) > 1e-9) continue;
    O.qp = Math.min(O.qp, apres);
    if (d > 1e-9 && avant > 0) vis.push([O, Math.min(1, O.qr / avant)]);
  }
  if (!vis.length) return;
  setTimeout(() => {                                                      // une seule attribution transaction / retrait par baisse (300 ms autour)
    let reste = d; for (const x of TRX) { if (x.tok !== tok || Math.abs(x.p - p) > 1e-9 || Math.abs(x.t - t) > 300) continue; const u = Math.min(reste, x.v - x.u); x.u += u; reste -= u; if (reste <= 1e-9) break; }
    if (reste <= 1e-9) return;
    for (const [O, frac] of vis) if (O.etat === "posee") { O.qr = Math.max(0, O.qr - reste * frac); O.qo = Math.max(0, O.qo - reste); }
  }, 300);
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
// ---- conditions toxiques (M4) mesurées en continu pour chaque jeton : dernière heure où chacune s'est déclenchée
const TOX = {};                                                           // id du jeton → { a, b, c } (ms)
function toxMesurer(mk, up, t) {
  const id = up ? mk.up : mk.down, sens = up ? 1 : -1, m300 = mouvement(300), m250 = mouvement(250), X = (TOX[id] = TOX[id] || { a: 0, b: 0, c: 0 });
  if (sens * m300.dp <= -10) X.a = t;
  if (sens * m250.flux <= -250000) X.b = t;
  let vv = 0; for (let i = TRX.length - 1; i >= 0 && t - TRX[i].t <= 500; i--) if (TRX[i].tok === id) vv += TRX[i].v; if (vv >= 100) X.c = t;
  return X;
}
function toxActifs(O) { const X = TOX[O.id]; if (!X) return ""; const t = nowMs(); return ["a", "b", "c"].filter((k) => t - X[k] <= 2000).join(""); }
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
  hybride(S, mk, up, nom);
  try { hybrideB(S, mk, up, nom); } catch (e) { log("M8b", e.message); }
}
// M8 HYBRIDE MAKER / PRENEUR (11.10.2026) : sur chaque signal, espérance preneur = parts disponibles au prix vu (50 $) × (modèle − prix − frais) ;
// espérance maker = parts attendues en 10 s (modèle de file de M5) × (modèle − prix maker − 2 c). On prend la plus grande si elle est positive
// (preneur : au moins 5 parts ; maker : au moins 0,50 $). Preneur exécuté après trajet simple + 150 ms (retard DOCUMENTÉ, non mesuré), au prix vu ou mieux.
const FEE7 = (p) => 0.07 * p * (1 - p);
function hybride(S, mk, up, nom) {
  const id = up ? mk.up : mk.down, fair = S.modele, a0 = S.a0, t = nowMs();
  let qT = 0, cT = 0; for (const [pp, z] of asksTries(id)) { if (pp > a0 + 1e-9) break; const x = Math.min(z, (50 - cT) / (pp + FEE7(pp))); if (x <= 0) break; qT += x; cT += x * (pp + FEE7(pp)); }
  const evT = qT >= MIN_PARTS_H ? qT * fair - cT : -Infinity;
  const pm = prixAmeliore(id, a0), bb = meilleurAcheteur(id); let evM = -Infinity, att = 0;
  if (pm != null) { let vol = 0; for (let i = TRX.length - 1; i >= 0 && t - TRX[i].t <= 30000; i--) if (TRX[i].tok === id) vol += TRX[i].v;
    const q = pm > bb + 1e-9 ? 0 : ((livres[id] && livres[id].bids.get(pm)) || 0); att = Math.min(50 / pm, Math.max(0, vol / 3 - q)); evM = att * (fair - pm - 0.02); }
  const v = "M8 hybride " + nom;
  if (evT > 0 && evT >= evM) {
    const O = { oid: `${mk.start}:${++oidN}`, variante: v, mode: "preneur", start: mk.start, cote: up ? "Up" : "Down", id, prix: a0, parts: 0, tPose: +t.toFixed(1), lat_ms: LAT(), etat: "envoi",
      remplP: 0, remplR: 0, remplO: 0, annulP: 0, annulR: 0, rempl: [], mo: { p: {}, r: {}, o: {} }, moModele: { p: {}, r: {}, o: {} }, toxRempl: [], evPreneur: +evT.toFixed(2), evMaker: isFinite(evM) ? +evM.toFixed(2) : null,
      modele: fair, a0, restantPose_s: +(mk.end - t / 1000).toFixed(2), qDevant: 0 };
    OFFRES.push(O); mstat(v).posees++;
    setTimeout(() => {                                                      // exécution au prix vu ou mieux, quantité alors affichée
      let q = 0, c = 0; for (const [pp, z] of asksTries(id)) { if (pp > a0 + 1e-9) break; const x = Math.min(z, (50 - c) / (pp + FEE7(pp))); if (x <= 0) break; q += x; c += x * (pp + FEE7(pp)); }
      if (q < MIN_PARTS_H) { O.etat = "manquee"; O.raison = "offre partie avant execution"; return; }
      O.parts = +q.toFixed(2); O.remplP = O.remplR = O.remplO = O.parts; O.cout = +c.toFixed(4); O.prix = +(c / q).toFixed(4); O.etat = "executee"; O.premierRempl_ms = +(nowMs() - O.tPose).toFixed(1); mstat(v).remplies++;
      for (const h of [1, 3, 5, 10]) setTimeout(() => { const m = milieu(id); if (m != null) for (const k of ["p", "r", "o"]) O.mo[k][h] = [q * (m - O.prix), q]; }, h * 1000);
    }, O.lat_ms + 150);
  } else if (evM >= 0.5) poser(v, mk, up, pm, 50, { mode: "maker", modeleCle: MODELE_REGLE(nom), modele: S.modele, a0, annulModele: 0.05, evPreneur: isFinite(evT) ? +evT.toFixed(2) : null, evMaker: +evM.toFixed(2) });
}
const MIN_PARTS_H = 5;
// M8b ROUTEUR CORRIGÉ (11.10.2026 15:47, demandé par Pitch) — constantes FIXÉES sur les données d'avant le 13.10 (jamais sur la période réservée) :
//   maker : E[gain] = parts attendues en 10 s (même modèle de file que M5 : P(remplissage) = parts attendues / taille) × (modèle − SÉLECTION ADVERSE MESURÉE − prix)
//           sélection adverse mesurée sur M1 (offres posées au signal) à +10 s : −0,85 c → 1 c ; aucun frais maker, ristourne non comptée ;
//   preneur : E[gain] = SURVIE MESURÉE de la quantité 164 ms après le signal (0,73, entre 0,77 à 100 ms et 0,68 à 250 ms) × (parts × modèle − coût frais compris) ;
//   abstention si aucune voie n'atteint son seuil (preneur > 0 avec ≥ 5 parts ; maker ≥ 0,50 $). Exécution simulée identique à M8.
const M8B = { adverse: 0.01, survie: 0.73 };
function hybrideB(S, mk, up, nom) {
  const id = up ? mk.up : mk.down, fair = S.modele, a0 = S.a0, t = nowMs();
  let qT = 0, cT = 0; for (const [pp, z] of asksTries(id)) { if (pp > a0 + 1e-9) break; const x = Math.min(z, (50 - cT) / (pp + FEE7(pp))); if (x <= 0) break; qT += x; cT += x * (pp + FEE7(pp)); }
  const evT = qT >= MIN_PARTS_H ? M8B.survie * (qT * fair - cT) : -Infinity;
  const pm = prixAmeliore(id, a0), bb = meilleurAcheteur(id); let evM = -Infinity;
  if (pm != null) { let vol = 0; for (let i = TRX.length - 1; i >= 0 && t - TRX[i].t <= 30000; i--) if (TRX[i].tok === id) vol += TRX[i].v;
    const q = pm > bb + 1e-9 ? 0 : ((livres[id] && livres[id].bids.get(pm)) || 0), att = Math.min(50 / pm, Math.max(0, vol / 3 - q)); evM = att * (fair - M8B.adverse - pm); }
  const v = "M8b routeur corrige " + nom;
  if (evT > 0 && evT >= evM) {
    const O = { oid: `${mk.start}:${++oidN}`, variante: v, mode: "preneur", start: mk.start, cote: up ? "Up" : "Down", id, prix: a0, parts: 0, tPose: +t.toFixed(1), lat_ms: LAT(), etat: "envoi",
      remplP: 0, remplR: 0, remplO: 0, annulP: 0, annulR: 0, rempl: [], mo: { p: {}, r: {}, o: {} }, moModele: { p: {}, r: {}, o: {} }, toxRempl: [], evPreneur: +evT.toFixed(2), evMaker: isFinite(evM) ? +evM.toFixed(2) : null,
      modele: fair, a0, restantPose_s: +(mk.end - t / 1000).toFixed(2), qDevant: 0 };
    OFFRES.push(O); mstat(v).posees++;
    setTimeout(() => {
      let q = 0, c = 0; for (const [pp, z] of asksTries(id)) { if (pp > a0 + 1e-9) break; const x = Math.min(z, (50 - c) / (pp + FEE7(pp))); if (x <= 0) break; q += x; c += x * (pp + FEE7(pp)); }
      if (q < MIN_PARTS_H) { O.etat = "manquee"; O.raison = "offre partie avant execution"; return; }
      O.parts = +q.toFixed(2); O.remplP = O.remplR = O.remplO = O.parts; O.cout = +c.toFixed(4); O.prix = +(c / q).toFixed(4); O.etat = "executee"; O.premierRempl_ms = +(nowMs() - O.tPose).toFixed(1); mstat(v).remplies++;
      for (const h of [1, 3, 5, 10]) setTimeout(() => { const m = milieu(id); if (m != null) for (const k of ["p", "r", "o"]) O.mo[k][h] = [q * (m - O.prix), q]; }, h * 1000);
    }, O.lat_ms + 150);
  } else if (evM >= 0.5) poser(v, mk, up, pm, 50, { mode: "maker", modeleCle: MODELE_REGLE(nom), modele: S.modele, a0, annulModele: 0.05, evPreneur: isFinite(evT) ? +evT.toFixed(2) : null, evMaker: +evM.toFixed(2) });
  else { mstat(v).abstentions = (mstat(v).abstentions || 0) + 1; try { recDe(mk.start).dec.push([+t.toFixed(1), v, "abstention", up ? "Up" : "Down", a0]); } catch (_) {} }
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
function coterX(Q, v, mk, up, px, ok, info, t, pmax) {                   // comme coter(), avec un prix maximal propre (M9 : jusqu'à 0,98)
  const k = v + (up ? "U" : "D"), S2 = (Q[k] = Q[k] || { depense: 0, O: null, t: 0 });
  const cur = S2.O && (S2.O.etat === "posee" || S2.O.etat === "envoi") && !S2.O.tAnnulDemande ? S2.O : null;
  if (S2.O && S2.O !== cur) { S2.depense += S2.O.remplR * S2.O.prix; S2.O = cur; }
  const budget = 50 - S2.depense - (cur ? cur.remplR * cur.prix : 0);
  ok = ok && budget >= 1 && px != null && px >= 0.04 && px <= pmax;
  if (cur && (!ok || Math.abs(cur.prix - px) > 1e-9)) { if (t - S2.t < 50 && ok) return S2; annuler(cur, ok ? "re-cotation" : "hors zone"); S2.depense += cur.remplR * cur.prix; S2.O = null; }
  if (!S2.O && ok && t - S2.t >= 50) { S2.O = poser(v, mk, up, px, budget, info); S2.t = t; }
  return S2;
}
function makerEvaluer(mk, tleft, ua, da, P) {
  const t = nowMs(), ts = t / 1000;
  DP[mk.start] = { pu: P.pu, t: ts }; for (const s of Object.keys(DP)) if (+s < mk.start - 600) delete DP[s];
  for (const O of OFFRES) {                                               // annulations M0 / M1 / M3
    if (O.start !== mk.start || !(O.etat === "posee" || O.etat === "envoi") || O.tAnnulDemande) continue;
    const v = O.variante;
    if (v.startsWith("M1") || v.startsWith("M0") || v.startsWith("M8")) {   // (M8b inclus : même préfixe)
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
  // M4a / M4b / M4c : M4 avec UNE SEULE condition (décomposition, 11.10.2026)
  for (const up of sides) {
    const X = toxMesurer(mk, up, t), k = up ? "U" : "D", fair = up ? P.pu : 1 - P.pu, ask = (up ? ua : da)[0];
    const px = Math.min(Math.floor((fair - 0.05) * 100 + 1e-9) / 100, r2(ask - 0.01));
    for (const [c, nom] of [["a", "M4a seul bourses -10 $"], ["b", "M4b seul flux agressif"], ["c", "M4c seul ventes Polymarket"]])
      coter(Q, nom, mk, up, px, tleft > 10 && tleft < 290 && t - X[c] > 2000, { modele: +fair.toFixed(4), a0: ask, raisonHors: "toxique " + c }, t);
  }
  // M6 durée de vie : M2 marge 5 c, mais chaque offre est annulée après L ms ; la nouvelle n'est posée qu'après CONFIRMATION de l'annulation
  // (aller-retour mesuré) ; les remplissages pendant le trajet de l'annulation sont comptés.
  for (const L of [100, 250, 500, 1000]) for (const up of sides) {
    const v = "M6 duree de vie " + L + " ms", k2 = v + (up ? "U" : "D"), S6 = Q[k2], fair = up ? P.pu : 1 - P.pu, ask = (up ? ua : da)[0];
    if (S6 && S6.O && S6.O.etat === "posee" && !S6.O.tAnnulDemande && t - S6.O.tPose >= L) { annuler(S6.O, "duree de vie"); S6.depense += S6.O.remplR * S6.O.prix; S6.O = null; S6.attente = t + 2 * LAT(); }
    const px = Math.min(Math.floor((fair - 0.05) * 100 + 1e-9) / 100, r2(ask - 0.01));
    coter(Q, v, mk, up, px, tleft > 10 && tleft < 290 && t >= ((S6 && S6.attente) || 0), { modele: +fair.toFixed(4), a0: ask }, t);
  }
  // M9 FIN DE CYCLE, CÔTÉ PRESQUE ACQUIS (11.10.2026 15:47, idée de Claude validée par Pitch) : de 30 à 3 s de la fin, si le milieu du carnet d'un côté
  // est ≥ 0,90, offre d'achat sur ce côté 1 c au-dessus du meilleur acheteur (ou au meilleur acheteur), jamais au-dessus de 0,98 ni au niveau du vendeur.
  // Retirée si le milieu repasse sous 0,85. 50 $ par cycle.
  for (const up of sides) {
    const id = up ? mk.up : mk.down, ask = (up ? ua : da)[0], bb = meilleurAcheteur(id), m = bb > 0 ? (bb + ask) / 2 : null;
    let px = null; if (bb > 0) { px = r2(bb + 0.01); if (px >= ask - 1e-9) px = r2(bb); px = Math.min(px, 0.98); }
    const S9 = Q["M9 fin de cycle cote acquis" + (up ? "U" : "D")], deja = S9 && S9.O && !S9.O.tAnnulDemande;
    const ok = tleft <= 30 && tleft > 3 && m != null && (m >= 0.90 || (deja && m >= 0.85)) && px != null && px >= 0.90;
    coterX(Q, "M9 fin de cycle cote acquis", mk, up, px, ok, { modele: +(up ? P.pu : 1 - P.pu).toFixed(4), a0: ask, milieu: m != null ? +m.toFixed(3) : null }, t, 0.99);
  }
  // M10 DOUBLE MAKER AU MEILLEUR PRIX + RETRAIT TOXIQUE (11.10.2026 15:47) : une offre au meilleur acheteur de CHAQUE côté (Up et Down : écart capturé si les
  // deux sont remplies) ; chaque côté est retiré 2 s dès qu'une des trois conditions de M4 se déclenche contre lui. 50 $ par côté et par cycle, de 290 à 10 s.
  for (const up of sides) {
    const id = up ? mk.up : mk.down, ask = (up ? ua : da)[0], bb = meilleurAcheteur(id), X = TOX[id] || { a: 0, b: 0, c: 0 };
    const tox = t - Math.max(X.a, X.b, X.c) <= 2000;
    coter(Q, "M10 double maker meilleur prix", mk, up, bb > 0 && bb < ask - 1e-9 ? r2(bb) : null, tleft > 10 && tleft < 290 && !tox, { modele: +(up ? P.pu : 1 - P.pu).toFixed(4), a0: ask, raisonHors: tox ? "toxique" : "hors zone" }, t);
  }
  // M11 ZONE MAKER (11.10.2026 15:53, idée de Claude validée par Pitch) : la seule famille positive sur les deux périodes de l'étude « tout combiné »
  // (désaccord 30, zone 0,15–0,35) jouée en MAKER : si le vendeur du côté est entre 0,15 et 0,35 et que le modèle le dépasse d'au moins 30 c, plus de
  // 60 s restantes, offre d'achat 1 c au-dessus du meilleur acheteur (ou au meilleur acheteur), toujours sous le vendeur ; retirée 2 s dès qu'une des
  // trois conditions toxiques de M4 se déclenche contre ce côté, ou quand la zone / l'écart disparaît. 50 $ par côté et par cycle.
  for (const up of sides) {
    const id = up ? mk.up : mk.down, ask = (up ? ua : da)[0], fair = up ? P.pu : 1 - P.pu, X = TOX[id] || { a: 0, b: 0, c: 0 };
    const tox = t - Math.max(X.a, X.b, X.c) <= 2000, zone = ask >= 0.15 && ask < 0.35 && fair - ask >= 0.30;
    coter(Q, "M11 zone maker", mk, up, zone ? prixAmeliore(id, ask) : null, zone && !tox && tleft > 60 && tleft < 290,
      { modele: +fair.toFixed(4), a0: ask, raisonHors: tox ? "toxique" : "hors zone" }, t);
  }
  // M21 MAKER DU FAVORI (11.10.2026 16:22, accord de Pitch) — tiré de l'autopsie des makers réels : l'écart gagnants / perdants vient de l'endroit où
  // ils achètent (le favori, pas l'outsider ; pas la 1re minute). Offre au MEILLEUR ACHETEUR (on rejoint la file) uniquement sur le côté dont le milieu
  // du carnet est entre 0,50 et 0,90, de 60 à 240 s après le début du cycle ; retirée 2 s dès qu'une condition toxique de M4 apparaît contre ce côté.
  // Jamais sur l'outsider. 50 $ par côté et par cycle. Aucun modèle Bot95 dans la décision (règle de marché pure).
  for (const up of sides) {
    const id = up ? mk.up : mk.down, ask = (up ? ua : da)[0], bb = meilleurAcheteur(id), m = bb > 0 ? (bb + ask) / 2 : null, X = TOX[id] || { a: 0, b: 0, c: 0 };
    const tox = t - Math.max(X.a, X.b, X.c) <= 2000, ecoule = 300 - tleft;
    const ok = m != null && m >= 0.50 && m <= 0.90 && ecoule >= 60 && ecoule <= 240 && !tox && bb < ask - 1e-9;
    coter(Q, "M21 maker du favori", mk, up, ok ? r2(bb) : null, ok, { modele: +(up ? P.pu : 1 - P.pu).toFixed(4), a0: ask, milieu: m != null ? +m.toFixed(3) : null, raisonHors: tox ? "toxique" : "hors zone" }, t);
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
    if (fini && !O.rec) { O.rec = true; try { if (REC[O.start]) REC[O.start].mk.push([O.variante, O.cote, O.prix, O.tPose, O.lat_ms, O.etat, O.qDevant, O.remplP, O.remplR, O.premierRempl_ms, O.restantPose_s, O.modele ?? null, O.acheteurPose, O.vendeurPose, O.niveauPose, O.tAnnulDemande || null, O.raison || null, O.evAttendue ?? null, O.remplO, O.annulP, O.annulR, O.mode || null]); } catch (_) {} }
    if (fini && O.remplR <= 0 && O.remplP <= 0 && O.remplO <= 0 && !(O.variante.startsWith("M1") || O.variante.startsWith("M0") || O.variante.startsWith("M8"))) { OFFRES.splice(i, 1); continue; }
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
    const g1 = O.gagne ? 1 : 0;
    O.resultat = O.mode === "preneur" ? { prudent: +(O.remplP * g1 - (O.cout || 0)).toFixed(2), proportionnel: +(O.remplP * g1 - (O.cout || 0)).toFixed(2), optimiste: +(O.remplP * g1 - (O.cout || 0)).toFixed(2) }
      : { prudent: +(O.remplP * (g1 - O.prix)).toFixed(2), proportionnel: +(O.remplR * (g1 - O.prix)).toFixed(2), optimiste: +(O.remplO * (g1 - O.prix)).toFixed(2) };
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
const nouveauLivre = () => ({ b: new Map(), a: new Map(), dec: [0, 0], add: [0, 0], t: 0 });
// 12.10.2026 (accord de Pitch) : + Coinbase BTC/USD (level2), ETH et SOL Binance spot (20 niveaux / 100 ms) — enregistrement seulement
const OB = { bn: nouveauLivre(), by: nouveauLivre(), cb: nouveauLivre(), eth: nouveauLivre(), sol: nouveauLivre() };
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
  R.ob.format2 = "colonnes ajoutées en fin de ligne : sequence (Binance lastUpdateId / Bybit u / Coinbase sequence_num), heure source ms (Bybit), fiable 1/0 ; cb = Coinbase BTC/USD, eth / sol = Binance spot ETHUSDT / SOLUSDT (cumuls en unités de l'actif, bandes en $)";
  for (const k of Object.keys(OB)) { const o = OB[k]; if (!o.t || t - o.t > 3000) continue; const ph = obPhoto(o); R.ob[k] = R.ob[k] || []; if (ph) R.ob[k].push([+t.toFixed(1), +(t - o.t).toFixed(1), ...ph, o.seq ?? null, o.ts ?? null, o.fiable === false ? 0 : 1]); o.dec = [0, 0]; o.add = [0, 0]; }
}, 100);
setInterval(() => {                                                       // carnet complet 10 niveaux de chaque côté, chaque seconde
  const t = nowMs(), R = recDe(Math.floor(t / 300000) * 300); R.obSnap = R.obSnap || { format: "[reception_ms, sequence, acheteurs [[prix, BTC]...10], vendeurs [[prix, BTC]...10]]", bn: [], by: [] };
  for (const k of ["bn", "by", "cb"]) { const o = OB[k]; if (!o.t || t - o.t > 3000) continue; R.obSnap[k] = R.obSnap[k] || [];
    const b = [...o.b].sort((x, y) => y[0] - x[0]).slice(0, 10), a = [...o.a].sort((x, y) => x[0] - y[0]).slice(0, 10);
    R.obSnap[k].push([+t.toFixed(1), o.seq ?? null, b.map((x) => [x[0], +x[1].toFixed(4)]), a.map((x) => [x[0], +x[1].toFixed(4)])]); }
}, 1000);
function obTrou(k, raison, detail) { try { const t = nowMs(); const R = recDe(Math.floor(t / 300000) * 300); (R.obTrous = R.obTrous || []).push([+t.toFixed(1), k, raison, String(detail)]); } catch (_) {} }
function trade2(k, tsSrc, achat, p, q) {                                  // transactions ETH / SOL (12.10.2026, enregistrement seulement)
  try { const t = nowMs(), R = recDe(Math.floor(t / 300000) * 300); R.trx2 = R.trx2 || { format: "[reception_ms, heure source ms, 1 achat agressif / 0 vente, prix, quantite] ; eth_bn / sol_bn = Binance spot, eth_by / sol_by = Bybit perp" };
    (R.trx2[k] = R.trx2[k] || []).push([+t.toFixed(1), tsSrc, achat, p, q]); } catch (_) {}
}
const MOIS_DRB = { JAN: 0, FEB: 1, MAR: 2, APR: 3, MAY: 4, JUN: 5, JUL: 6, AUG: 7, SEP: 8, OCT: 9, NOV: 10, DEC: 11 };
async function sondeOI() {                                               // open interest des options BTC Deribit par prix d'exercice, chaque minute (12.10.2026)
  try {
    const t = nowMs(), r = await fetch("https://www.deribit.com/api/v2/public/get_book_summary_by_currency?currency=BTC&kind=option").then((x) => x.json());
    const L = (r && r.result) || [], out = [];
    for (const y of L) {
      const p = (y.instrument_name || "").split("-"); if (p.length < 4) continue;
      const e = p[1], ech = Date.UTC(2000 + +e.slice(-2), MOIS_DRB[e.slice(-5, -2)], +e.slice(0, -5), 8), K = +p[2], S = +y.underlying_price || +y.estimated_delivery_price;
      if (!(ech > t) || ech - t > 8 * 86400000 || !S || Math.abs(Math.log(K / S)) > 0.10) continue;
      out.push([y.instrument_name, +y.open_interest, +y.mark_iv, +y.mark_price, y.bid_price == null ? null : +y.bid_price, y.ask_price == null ? null : +y.ask_price, +y.volume]);
    }
    const R = recDe(Math.floor(t / 300000) * 300); R.deribitOI = R.deribitOI || { format: "[reception_ms, [[instrument, open interest (BTC), mark iv, mark price, meilleur acheteur, meilleur vendeur, volume 24 h], ...]] ; options BTC à moins de 8 jours et à moins de 10 % du prix" , d: [] };
    R.deribitOI.d.push([+t.toFixed(1), out]);
  } catch (_) {}
}
setInterval(sondeOI, 60000);
const DERIV = {};
function deriv(k, row) {                                                  // dérivés BTC (12.10.2026, enregistrement seulement)
  try { const t = nowMs(), R = recDe(Math.floor(t / 300000) * 300);
    R.deriv = R.deriv || { format: "by_ticker = [reception_ms, heure source ms, dernier, mark, index, open interest (BTC), funding, meilleur acheteur, meilleur vendeur, instantane 1/0] (Bybit BTCUSDT, etat complet a chaque message) ; bn_mark = [reception_ms, heure source ms, mark, index, funding] (Binance perp, 1 s) ; bn_liq = [reception_ms, heure ms, cote de l'ordre force, quantite, prix, prix moyen, statut, quantite executee] (Binance forceOrder : au plus une par seconde, echantillonne) ; bn_perp_tx = [reception_ms, heure ms, 1 achat agressif / 0 vente, prix, quantite] ; bn_oi = [reception_ms, heure ms, open interest BTC] (REST toutes les 5 s)" };
    (R.deriv[k] = R.deriv[k] || []).push([+t.toFixed(1), ...row]); } catch (_) {}
}
async function sondeOIbn() {
  try { const r = await fetch("https://fapi.binance.com/fapi/v1/openInterest?symbol=BTCUSDT").then((x) => x.json()); if (r && r.openInterest) { deriv("bn_oi", [+r.time, +r.openInterest]); OIH.push([+r.time, +r.openInterest]); while (OIH.length && OIH[0][0] < +r.time - 900000) OIH.shift(); } } catch (_) {}
}
setInterval(sondeOIbn, 5000);
const TRADE_ID = {};
function obTrade(k, tsSrc, achat, p, q, id) {                              // transactions brutes Binance spot et Bybit perp ; trou si l'identifiant Binance saute
  try { const t = nowMs(), R = recDe(Math.floor(t / 300000) * 300); R.trx = R.trx || { format: "[reception_ms, heure source ms, 1 achat agressif / 0 vente, prix, quantite BTC]", bn: [], by: [] };
    if (k === "bn" && TRADE_ID.bn && id !== TRADE_ID.bn + 1 && id > TRADE_ID.bn) obTrou("bn", "transactions manquantes", (id - TRADE_ID.bn - 1) + " id");
    if (k === "bn") TRADE_ID.bn = id;
    R.trx[k].push([+t.toFixed(1), tsSrc, achat, p, q]); } catch (_) {}
  if (k === "by") { try { by1SurTrade(p); } catch (_) {} }
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
  if (muet("perp")) connecter("perp", "wss://stream.bybit.com/v5/public/linear", [JSON.stringify({ op: "subscribe", args: ["publicTrade.BTCUSDT", "allLiquidation.BTCUSDT"] })],
    (m) => { const tp = m.topic || "";
      if (tp.startsWith("allLiquidation")) { for (const y of m.data || []) flux50("liq_bybit", y.S === "Buy" ? "v" : "a", +y.v, +y.p); return; }   // Buy = position longue liquidée → vente forcée
      if (!tp.startsWith("publicTrade")) return; for (const y of m.data || []) { flux50("perp", y.S === "Buy" ? "a" : "v", +y.v, +y.p); obTrade("by", +y.T, y.S === "Buy" ? 1 : 0, +y.p, +y.v, y.i); }
      const x = (m.data || []).slice(-1)[0]; if (x) noter("perp", +x.p, +x.T); }, JSON.stringify({ op: "ping" }), 15000);
  if (muet("okx")) connecter("okx", "wss://ws.okx.com:8443/ws/v5/public", [JSON.stringify({ op: "subscribe", args: [{ channel: "trades", instId: "BTC-USDT-SWAP" }] })],
    (m) => { if (!(m.arg && m.arg.channel === "trades")) return; for (const y of m.data || []) flux50("okx", y.side === "buy" ? "a" : "v", +y.sz * 0.01, +y.px);
      const x = (m.data || []).slice(-1)[0]; if (x) noter("okx", +x.px, +x.ts); }, "ping", 20000);
  if (muet("bn")) connecter("bn", "wss://stream.binance.com:9443/ws/btcusdt@trade", [], (m) => { if (+m.p > 0) { flux50("bn", m.m ? "v" : "a", +m.q, +m.p); noter("bn", +m.p, +m.T); obTrade("bn", +m.T, m.m ? 0 : 1, +m.p, +m.q, +m.t); } });
  if (muet("cb")) connecter("cb", "wss://advanced-trade-ws.coinbase.com", [JSON.stringify({ type: "subscribe", product_ids: ["BTC-USD"], channel: "ticker" }), JSON.stringify({ type: "subscribe", product_ids: ["BTC-USD"], channel: "market_trades" })],
    (m) => { if (m.channel === "market_trades") { for (const ev of m.events || []) for (const y of ev.trades || []) flux50("cb", y.side === "BUY" ? "a" : "v", +y.size, +y.price); return; }
      if (m.channel !== "ticker") return; for (const ev of m.events || []) for (const x of ev.tickers || []) if (x.product_id === "BTC-USD" && x.price) noter("cb", +x.price, Date.parse(m.timestamp)); });
  if (muet("cl")) connecter("cl", "wss://ws-live-data.polymarket.com", [JSON.stringify({ action: "subscribe", subscriptions: [{ topic: "crypto_prices_chainlink", type: "*", filters: "" }] })],
    (m) => { if (m.topic !== "crypto_prices_chainlink") return; const p = m.payload || {}; if ((p.symbol || "").toUpperCase().startsWith("BTC") && +p.value > 0) {
      const tR = nowMs(), pub = +m.timestamp;                             // RTDS : payload.timestamp = observation Chainlink ; timestamp = envoi par l'éditeur
      if (pub > 0) { CLS.publication.push(pub - +p.timestamp); CLS.transport.push(tR - pub); if (CLS.publication.length > 2000) { CLS.publication.shift(); CLS.transport.shift(); } }
      chainlink("rtds", +p.value, +p.timestamp); } }, "PING", 5000);
  if (muet("bnd")) connecter("bnd", "wss://stream.binance.com:9443/ws/btcusdt@depth20@100ms", [], (m) => { if (!m.bids) return; const o = OB.bn, t = nowMs();
      if (o.seq && +m.lastUpdateId <= o.seq) obTrou("bn", "lastUpdateId en arriere", o.seq + " -> " + m.lastUpdateId);
      if (o.t && t - o.t > 500) obTrou("bn", "silence", Math.round(t - o.t) + " ms");
      const nb = new Map(m.bids.map((x) => [+x[0], +x[1]])), na = new Map(m.asks.map((x) => [+x[0], +x[1]]));
      for (const [p, q] of o.b) { const q2 = nb.get(p) || 0; if (q2 < q) o.dec[0] += q - q2; } for (const [p, q] of nb) { const q0 = o.b.get(p) || 0; if (q > q0) o.add[0] += q - q0; }
      for (const [p, q] of o.a) { const q2 = na.get(p) || 0; if (q2 < q) o.dec[1] += q - q2; } for (const [p, q] of na) { const q0 = o.a.get(p) || 0; if (q > q0) o.add[1] += q - q0; }
      o.b = nb; o.a = na; o.seq = +m.lastUpdateId; o.ts = null; o.t = t; });
  if (muet("byob")) connecter("byob", "wss://stream.bybit.com/v5/public/linear", [JSON.stringify({ op: "subscribe", args: ["orderbook.50.BTCUSDT"] })], (m) => {
      if (!(m.topic || "").startsWith("orderbook")) return; const o = OB.by, d = m.data || {}, t = nowMs();
      if (m.type === "snapshot") { o.b = new Map(); o.a = new Map(); o.fiable = true; }
      else if (o.seq != null && +d.u !== o.seq + 1) { obTrou("by", "sequence u", o.seq + " -> " + d.u); o.fiable = false; o.nTrous = (o.nTrous || 0) + 1; if (o.nTrous <= 3) { try { WS.byob.ws.close(); } catch (_) {} } }   // trou : carnet non fiable ; reconnexion (3 fois au plus) → carnet complet
      if (o.t && t - o.t > 1000) obTrou("by", "silence", Math.round(t - o.t) + " ms");
      o.seq = +d.u; o.seqSrc = +d.seq; o.ts = +m.ts;
      for (const x of d.b || []) obAppliquer(o, 0, +x[0], +x[1], m.type === "delta"); for (const x of d.a || []) obAppliquer(o, 1, +x[0], +x[1], m.type === "delta"); o.t = t; }, JSON.stringify({ op: "ping" }), 15000);
  // ---- 12.10.2026 (accord de Pitch) : Coinbase level2, ETH / SOL (Binance spot carnet + transactions, Bybit perp transactions) — lecture seule
  if (muet("cbob")) connecter("cbob", "wss://advanced-trade-ws.coinbase.com", [JSON.stringify({ type: "subscribe", product_ids: ["BTC-USD"], channel: "level2" }), JSON.stringify({ type: "subscribe", product_ids: ["BTC-USD"], channel: "heartbeats" })],
    (m) => { if (m.channel !== "l2_data") return; const o = OB.cb, t = nowMs();
      if (m.sequence_num != null) o.seq = +m.sequence_num;
      for (const ev of m.events || []) { if (ev.type === "snapshot") { o.b = new Map(); o.a = new Map(); }
        for (const u of ev.updates || []) obAppliquer(o, u.side === "bid" ? 0 : 1, +u.price_level, +u.new_quantity, ev.type === "update"); }
      if (o.t && t - o.t > 1000) obTrou("cb", "silence", Math.round(t - o.t) + " ms"); o.t = t; });
  if (muet("xbn")) connecter("xbn", "wss://stream.binance.com:9443/stream?streams=ethusdt@trade/solusdt@trade/ethusdt@depth20@100ms/solusdt@depth20@100ms", [], (m) => {
      const st = m.stream || "", d = m.data || {}, k = st.startsWith("eth") ? "eth" : "sol";
      if (st.endsWith("@trade")) { trade2(k + "_bn", +d.T, d.m ? 0 : 1, +d.p, +d.q); return; }
      if (!d.bids) return; const o = OB[k], t = nowMs();
      const nb = new Map(d.bids.map((x) => [+x[0], +x[1]])), na = new Map(d.asks.map((x) => [+x[0], +x[1]]));
      for (const [p, q] of o.b) { const q2 = nb.get(p) || 0; if (q2 < q) o.dec[0] += q - q2; } for (const [p, q] of nb) { const q0 = o.b.get(p) || 0; if (q > q0) o.add[0] += q - q0; }
      for (const [p, q] of o.a) { const q2 = na.get(p) || 0; if (q2 < q) o.dec[1] += q - q2; } for (const [p, q] of na) { const q0 = o.a.get(p) || 0; if (q > q0) o.add[1] += q - q0; }
      o.b = nb; o.a = na; o.seq = +d.lastUpdateId; o.t = t; });
  if (muet("xby")) connecter("xby", "wss://stream.bybit.com/v5/public/linear", [JSON.stringify({ op: "subscribe", args: ["publicTrade.ETHUSDT", "publicTrade.SOLUSDT"] })],
    (m) => { const tp = m.topic || ""; if (!tp.startsWith("publicTrade")) return; const k = tp.includes("ETH") ? "eth_by" : "sol_by";
      for (const y of m.data || []) trade2(k, +y.T, y.S === "Buy" ? 1 : 0, +y.p, +y.v); }, JSON.stringify({ op: "ping" }), 15000);
  // ---- 12.10.2026 16:21 (GO de Pitch, H994-H1002) : Bybit ticker BTCUSDT (mark, index, OI, funding) ; Binance perp BTCUSDT (mark/index 1 s, liquidations, transactions)
  // 12.10.2026 21:44 (GO de Pitch) : flux public RTDS « activity / trades » de Polymarket, avec les portefeuilles, marchés BTC 5 min seulement.
  // Enregistrement seulement (étude H1054 : mesurer le vrai retard pour « jouer contre l'argent bête ») ; aucun ordre.
  if (muet("act")) connecter("act", "wss://ws-live-data.polymarket.com", [JSON.stringify({ action: "subscribe", subscriptions: [{ topic: "activity", type: "trades" }] })],
    (m) => { if (m.topic !== "activity") return; const p = m.payload || {}, sl = p.eventSlug || p.slug || "";
      if (!sl.startsWith("btc-updown-5m")) return;
      try { const t = nowMs(), R = recDe(Math.floor(t / 300000) * 300);
        R.act = R.act || { format: "[reception_ms, envoi RTDS ms, heure transaction (payload.timestamp), portefeuille, BUY/SELL, outcome, prix, parts, slug, transaction]", l: [] };
        R.act.l.push([+t.toFixed(1), +m.timestamp || null, p.timestamp ?? null, p.proxyWallet || null, p.side || null, p.outcome || null, +p.price || null, +p.size || null, sl, (p.transactionHash || "").slice(0, 18)]); } catch (_) {} },
    "PING", 5000);
  if (muet("byt")) connecter("byt", "wss://stream.bybit.com/v5/public/linear", [JSON.stringify({ op: "subscribe", args: ["tickers.BTCUSDT"] })], (m) => {
      if (!(m.topic || "").startsWith("tickers")) return; const d = m.data || {}, S = (DERIV.by = DERIV.by || {});
      for (const k of ["lastPrice", "markPrice", "indexPrice", "openInterest", "fundingRate", "bid1Price", "ask1Price"]) if (d[k] != null && d[k] !== "") S[k] = +d[k];
      deriv("by_ticker", [+m.ts || null, S.lastPrice ?? null, S.markPrice ?? null, S.indexPrice ?? null, S.openInterest ?? null, S.fundingRate ?? null, S.bid1Price ?? null, S.ask1Price ?? null, m.type === "snapshot" ? 1 : 0]); },
    JSON.stringify({ op: "ping" }), 15000);
  if (muet("bnf")) connecter("bnf", "wss://fstream.binance.com/market/stream?streams=btcusdt@markPrice@1s/btcusdt@forceOrder/btcusdt@aggTrade", [], (m) => {
      const d = m.data || {}, e = d.e;
      if (e === "markPriceUpdate") deriv("bn_mark", [+d.E, +d.p, +d.i, +d.r]);
      else if (e === "forceOrder") { const x = d.o || {}; deriv("bn_liq", [+x.T || +d.E, x.S, +x.q, +x.p, +x.ap, x.X, +x.l || null]); }
      else if (e === "aggTrade") deriv("bn_perp_tx", [+d.T, d.m ? 0 : 1, +d.p, +d.q]); });
  if (muet("drb")) connecter("drb", "wss://www.deribit.com/ws/api/v2",              // Deribit (lecture seule, accord de Pitch 12.10) : indice, perpétuel, DVOL
    [JSON.stringify({ jsonrpc: "2.0", id: 1, method: "public/subscribe", params: { channels: ["deribit_price_index.btc_usd", "ticker.BTC-PERPETUAL.100ms", "deribit_volatility_index.btc_usd", "trades.option.BTC.100ms"] } })],
    (m) => { if (m.method !== "subscription" || !m.params) return; const ch = m.params.channel || "", x = m.params.data || {}, t = nowMs();
      const R = recDe(Math.floor(t / 300000) * 300); R.deribit = R.deribit || { format: "[reception_ms, heure source ms, type, ...] ; i = indice BTC/USD [prix] ; p = BTC-PERPETUAL [dernier, mark, meilleur acheteur, meilleur vendeur, open interest USD, funding 8 h] ; v = DVOL [volatilite] ; o = transaction d'option [instrument, cote preneur, prix BTC, quantite, iv, indice, bloc 1/0]", d: [] };
      if (ch.startsWith("deribit_price_index")) R.deribit.d.push([+t.toFixed(1), +x.timestamp, "i", +x.price]);
      else if (ch.startsWith("ticker.BTC-PERPETUAL")) R.deribit.d.push([+t.toFixed(1), +x.timestamp, "p", +x.last_price, +x.mark_price, +x.best_bid_price, +x.best_ask_price, +x.open_interest, +x.funding_8h]);
      else if (ch.startsWith("deribit_volatility_index")) R.deribit.d.push([+t.toFixed(1), +x.timestamp, "v", +x.volatility]);
      else if (ch.startsWith("trades.option")) for (const y of (Array.isArray(x) ? x : [])) R.deribit.d.push([+t.toFixed(1), +y.timestamp, "o", y.instrument_name, y.direction, +y.price, +y.amount, +y.iv, +y.index_price, y.block_trade_id ? 1 : 0]); },
    JSON.stringify({ jsonrpc: "2.0", id: 9, method: "public/test", params: {} }), 10000);
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
  await fantReglements().catch((e) => log("fantomes reglements", e.message));
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
  const fantomes = FANT_REGLES.splice(0, FANT_REGLES.length);
  const corps = { version: VERSION, t: now(), fantomes, signaux: FINIS.splice(0, FINIS.length).map(({ id, fini, envoye, ...s }) => s), maker: regles, makerEnCours: { offres: enCours, compteurs: MSTAT },
    chainlink: { decomposition_rtds_ms: { publication: qd(CLS.publication), transport: qd(CLS.transport), traitement_boucle: qd(CLS.boucle) }, rtds_ms: qd(CLS.delai.rtds), polybolt_ms: qd(CLS.delai.pb), twap_ms: qd(CLS.twap), premier: CLS.premier, avanceDuPremier_ms: { rtds: med(CLS.avance.filter((x) => x[0] === "rtds").map((x) => x[1])), polybolt: med(CLS.avance.filter((x) => x[0] === "pb").map((x) => x[1])) },
      messages: CLS.n, exemples: CLS.exemples || [], abonnements: CLS.pbAbos || [], polyboltConnecte: CLS.pbAuth, polyboltErreur: CLS.pbErreur, source: CLS.source, identifiants: !!PB },
    latence: { rttClob_ms: { med: med(STAT.rttClob), p10: qtl(STAT.rttClob, 0.1), p90: qtl(STAT.rttClob, 0.9), n: STAT.rttClob.length },
      polyVersNous_ms: { med: med(STAT.retardPoly), p10: qtl(STAT.retardPoly, 0.1), p90: qtl(STAT.retardPoly, 0.9) },
      calcul_us: { med: med(STAT.decisionUs), p90: qtl(STAT.decisionUs, 0.9) }, evaluations: STAT.evaluations },
    systeme: (() => { const m = process.memoryUsage(); let disque = null; try { const d = fs.statfsSync(DIR); disque = { libre_Mo: Math.round(d.bavail * d.bsize / 1e6), total_Mo: Math.round(d.blocks * d.bsize / 1e6) }; } catch (_) {}
      return { rss_Mo: Math.round(m.rss / 1e6), tas_Mo: Math.round(m.heapUsed / 1e6), disque, dernierCycle: STAT.dernierCycle || null }; })(),
    flux: Object.fromEntries(["perp", "okx", "bn", "cb", "cl", "pb", "bnd", "byob", "poly", "drb", "cbob", "xbn", "xby", "byt", "bnf", "act"].map((k) => [k, WS[k] ? { muet_s: +(now() - WS[k].msg).toFixed(1), reconnexions: WS[k].n } : null])) };
  try {
    const r = await fetch(`${U}/api/rapide/donnees`, { method: "POST", headers: { "content-type": "application/json", "x-rapide": TOKEN }, body: JSON.stringify(corps) });
    if (!r.ok) { log("envoi HTTP", r.status); FANT_REGLES.unshift(...corps.fantomes); FINIS.unshift(...corps.signaux); MAKER_FINIS.push(...corps.maker.filter((x) => x.type !== "resume")); }
  } catch (e) { log("envoi", e.message); FANT_REGLES.unshift(...corps.fantomes); FINIS.unshift(...corps.signaux); MAKER_FINIS.push(...corps.maker.filter((x) => x.type !== "resume")); }
  try { fs.writeFileSync(DIR + "/dernier_envoi.json", JSON.stringify(corps)); } catch (_) {}
}
async function versionDistante() {
  try { const d = await getJSON(`${U}/api/rapide/version`, { headers: { "x-rapide": TOKEN } }); if (d.version && d.version !== VERSION) { log("nouvelle version", d.version, "→ redémarrage"); await envoyer(); process.exit(0); } } catch (_) {}
}
log("bot95 rapide", VERSION, "démarre — fantôme uniquement, aucun ordre");
// 13.10.2026 15:53 (Pitch : « je veux TOUT sur le bot ») : au démarrage, relecture des fichiers de cycle déjà écrits (12 et 13.10 et suivants, 3 jours)
// pour remettre dans la file de règlement tous les trades des fantômes de Dublin ; le bot Cloudflare ignore ceux qu'il a déjà (identifiant).
try {
  const base = DIR + "/cycles", lim = new Date(Date.now() - 3 * 86400000).toISOString().slice(0, 10); let n = 0;
  for (const d of fs.existsSync(base) ? fs.readdirSync(base) : []) {
    if (d < lim) continue;
    for (const f of fs.readdirSync(base + "/" + d)) {
      try { const R = JSON.parse(zlib.gunzipSync(fs.readFileSync(base + "/" + d + "/" + f)));
        for (const k of ["cp", "cp5", "bf", "fg", "sa", "pb", "nv"]) for (const E of R[k] || []) if (E && E.q > 0) { FANT.push(E); n++; } } catch (_) {}
    }
  }
  log("fantômes relus sur le disque", n);
} catch (e) { log("relecture fantômes", e.message); }
flux(); cycle();
setInterval(cycle, 1000);
// ---------------------------------------------------------------- FANTÔMES « trouvailles du 13.10 » (accord de Pitch 13.10.2026 21:08 « fait des fantômes
// de toutes tes trouvailles »). AUCUN ORDRE RÉEL. Achat fictif preneur sur le carnet vu à +164 ms, limite meilleur vendeur + 1 c, gardé jusqu'au
// règlement. Enregistré dans le fichier du cycle (clé « nv »).
//   BY1 (H1068) : chaque transaction Bybit ; saut ≥ 5 $ en 300 ms (30–280 s, pause 5 s), OKX / Binance / Coinbase pas bougé de 2 $ dans le même sens,
//     côté du saut 0,40–0,70 → 10 $ et 100 $.
//   BT (H1065 bis) : billet 0,02–0,20 (60–280 s, un par cycle) quand l'élan du favori se retourne : milieu Polymarket du favori en baisse sur 5 s,
//     perp contre le favori sur 30 s, carnet Binance (cumul 10 $) penché contre le favori → 10 $.
//   E1–E4 (H1067, verdict sur 27 jours en attente) aux instants 60, 90, …, 240, 260 s, une fois par cycle et par règle, 10 $ :
//     E1 favori 0,60–0,95 et élan Binance 10 s (/ σ 1 h) ≥ 0,32 → favori ; E2 même zone et élan < 0 → billet ;
//     E3 favori 0,60–0,95 et σ 300 s / σ 3 600 s ≥ 1,2 → favori ; E4 fenêtre commençant à :00 ou :30, favori 0,65–0,95 → billet.
//   OI : entre 2 et 10 s du début du cycle, open interest Binance en hausse ≥ 17,75 pb sur 5 min → Up, 10 $.
function fantAchat(start, nom, X, dollars, info) {
  const mk = M[start]; if (!mk) return; const id = X === "Up" ? mk.up : mk.down, a = asksTries(id)[0];
  const E = { nomFant: nom, start, cote: X, t: Math.round(nowMs()), a0: a ? a[0] : null, montant: dollars, statut: "achat", ...(info || {}) };
  const R = recDe(start); (R.nv = R.nv || []).push(E);
  if (!a) { E.statut = "pas de vendeur"; return; }
  FANT.push(E);
  setTimeout(() => { let q = 0, c = 0;
    for (const [px, sz] of asksTries(id)) { if (px > a[0] + 0.01 + 1e-9) break; const u = px + FEE7(px); const k = Math.min(sz, (dollars - c) / u); if (k <= 1e-9) break; q += k; c += k * u; }
    E.q = +q.toFixed(3); E.c = +c.toFixed(4); E.statut = q > 0 && c >= dollars / 2 ? "ouvert" : "non rempli"; if (E.statut !== "ouvert") E.q = 0; }, 164);
}
const BYH = [], PCH = []; let by1Dernier = 0;
function by1SurTrade(p) {
  const t = nowMs(); BYH.push([t, p]); while (BYH.length && BYH[0][0] < t - 1000) BYH.shift();
  let p0 = null; for (const [tt, pp] of BYH) if (tt >= t - 300) { p0 = pp; break; }
  if (p0 == null) return; const d = p - p0;
  if (Math.abs(d) < 5 || t - by1Dernier < 5000) return;
  const start = Math.floor(t / 300000) * 300, el = t / 1000 - start; if (el < 30 || el > 280) return;
  const mk = M[start]; if (!mk || !mk.up || !mk.down) return;
  by1Dernier = t; const sg = d > 0 ? 1 : -1, X = d > 0 ? "Up" : "Down";
  const conf = ["okx", "bn", "cb"].filter((k) => { const m = mvMs(k, t); return m != null && sg * m >= 2; }).length;
  const a = asksTries(X === "Up" ? mk.up : mk.down)[0];
  if (conf > 0 || !a || a[0] < 0.40 - 1e-9 || a[0] > 0.70 + 1e-9) return;
  fantAchat(start, "BY1 Bybit premier 10 $", X, 10, { d: +d.toFixed(2) }); fantAchat(start, "BY1 Bybit premier 100 $", X, 100, { d: +d.toFixed(2) });
  // H1073 (accord de Pitch 13.10.2026 21:08 « fantômes de toutes tes trouvailles ») : BY1 quand les ordres du carnet Polymarket (jeton Up, 3 s)
  // poussaient CONTRE le saut (renfort net acheteurs − renfort net vendeurs, signé pour le côté du saut, < 0).
  { const tt = nowMs(); let ab = 0, db = 0, aa = 0, da = 0;
    for (const [t2, id, sd, dq] of PCH) { if (t2 < tt - 3000 || id !== mk.up) continue; if (sd === 0) { if (dq > 0) ab += dq; else db -= dq; } else { if (dq > 0) aa += dq; else da -= dq; } }
    const tot = ab + db + aa + da;
    if (tot > 0) { const pr = sg * ((ab - db) - (aa - da)) / (tot + 1); if (pr < 0) fantAchat(start, "BY1 pression contre 10 $", X, 10, { d: +d.toFixed(2), pr: +pr.toFixed(3) }); } }
  // H1069 (accord de Pitch 13.10.2026 21:19 « combines ») : en plus, saut CONTRE l'élan des 30 s du perp et marché calme (σ 300 s / σ 3 600 s < 1)
  const n = PERP1H.length;
  if (n >= 1800) { const m30 = sg * (PERP1H[n - 1] - PERP1H[n - 31]), s1h = sdDiff(PERP1H), s300 = sdDiff(PERP1H.slice(-301));
    if (m30 < 0 && s1h && s300 / s1h < 1) { const info = { d: +d.toFixed(2), m30: +m30.toFixed(1), vr: +(s300 / s1h).toFixed(3) };
      fantAchat(start, "BY1 contre-elan calme 10 $", X, 10, info); fantAchat(start, "BY1 contre-elan calme 100 $", X, 100, info); } }
}
const BN1H = [], PERP1H = [];                                                          // prix Binance spot chaque seconde, 1 h
const OIH = [];                                                           // [t, open interest] Binance
const NVF = {};                                                           // "start|règle" → déjà décidé
function sdDiff(L) { if (L.length < 3) return null; const d = []; for (let i = 1; i < L.length; i++) d.push(L[i] - L[i - 1]); const m = d.reduce((a, b) => a + b, 0) / d.length; return Math.sqrt(d.reduce((a, b) => a + (b - m) * (b - m), 0) / d.length); }
setInterval(() => {
  try {
    const t = now(); if (f.bn) { BN1H.push(f.bn.p); if (BN1H.length > 3600) BN1H.shift(); }
    if (f.perp) { PERP1H.push(f.perp.p); if (PERP1H.length > 3600) PERP1H.shift(); }
    const start = Math.floor(t / 300) * 300, el = t - start, mk = M[start]; if (!mk || !mk.up || !mk.down) return;
    const fait = (r) => NVF[start + "|" + r], marque = (r) => { NVF[start + "|" + r] = 1; };
    for (const k of Object.keys(NVF)) if (+k.split("|")[0] < start - 900) delete NVF[k];
    const aU = asksTries(mk.up)[0], bU = meilleurAcheteur(mk.up); if (!aU || !(bU > 0)) return;
    const um = (aU[0] + bU) / 2, sg = um >= 0.5 ? 1 : -1, fp = sg > 0 ? um : 1 - um, FAV = sg > 0 ? "Up" : "Down", TIC = sg > 0 ? "Down" : "Up";
    if (el >= 2 && el <= 10 && !fait("OI") && OIH.length) {
      const o1 = OIH[OIH.length - 1]; let o0 = null; for (const x of OIH) if (x[0] <= o1[0] - 300000) o0 = x;
      if (o0) { marque("OI"); const doi = (o1[1] / o0[1] - 1) * 1e4; if (doi >= 17.75) fantAchat(start, "OI monte Up", "Up", 10, { doi: +doi.toFixed(1) }); }
    }
    if (el >= 60 && el <= 280 && !fait("BT")) {
      const aT = asksTries(TIC === "Up" ? mk.up : mk.down)[0];
      if (aT && aT[0] >= 0.02 && aT[0] <= 0.20 + 1e-9) {
        let m5 = null; for (const [tt, s2, v] of MIDH) if (s2 === start && tt <= nowMs() - 5000) m5 = v;
        const p30 = prixA("perp", Math.floor(t) - 30), ph = OB.bn ? obPhoto(OB.bn) : null;
        if (m5 != null && f.perp && p30 && ph) {
          const t1 = sg * (um - m5) < 0, t2 = sg * (f.perp.p - p30) < 0, t3 = sg * (ph[5] - ph[9]) < 0;
          if (t1 && t2 && t3) { marque("BT"); fantAchat(start, "billet elan retourne", TIC, 10, { fp: +fp.toFixed(3) }); }
        }
      }
    }
    // H1083 X2 (accord de Pitch 14.10.2026 11:55 « go ») : à 10 s du début, BTC Binance en baisse sur 30 min (≤ −1,018 σ) ET sur 5 min (< 0) → Up, 10 $.
    // σ = écart-type des variations 1 s sur 1 h ; prix de référence = prix Binance à l'ouverture du cycle. Une fois par cycle. AUCUN ORDRE RÉEL.
    if (el >= 10 && el < 12 && !fait("X2") && BN1H.length >= 3600) {
      marque("X2"); const n = BN1H.length, k0 = n - 1 - Math.round(el), s1h = sdDiff(BN1H);
      if (s1h && k0 - 1800 >= 0) { const p0 = BN1H[k0], r30 = (p0 - BN1H[k0 - 1800]) / (s1h * Math.sqrt(1800)), r5 = (p0 - BN1H[k0 - 300]) / (s1h * Math.sqrt(300));
        if (r30 <= -1.018 && r5 < 0) fantAchat(start, "X2 baisse 30 min et 5 min Up", "Up", 10, { r30: +r30.toFixed(3), r5: +r5.toFixed(3) }); }
    }
    const inst = [60, 90, 120, 150, 180, 210, 240, 260].find((x) => el >= x && el < x + 1);
    if (inst != null && BN1H.length >= 1800) {
      const s1h = sdDiff(BN1H), s300 = sdDiff(BN1H.slice(-301)), n = BN1H.length, m10 = s1h ? sg * (BN1H[n - 1] - BN1H[n - 11]) / (s1h * Math.sqrt(10)) : null;
      if (fp >= 0.60 && fp <= 0.95 && m10 != null) {
        if (!fait("E1") && m10 >= 0.319) { marque("E1"); fantAchat(start, "E1 elan frais favori", FAV, 10, { m10: +m10.toFixed(3) }); }
        if (!fait("E2") && m10 < 0) { marque("E2"); fantAchat(start, "E2 elan contraire billet", TIC, 10, { m10: +m10.toFixed(3) }); }
        if (!fait("E3") && s1h && s300 / s1h >= 1.199) { marque("E3"); fantAchat(start, "E3 volatilite haute favori", FAV, 10, { vr: +(s300 / s1h).toFixed(3) }); }
      }
      if (!fait("E4") && (start / 60) % 30 === 0 && fp >= 0.65 && fp <= 0.95) { marque("E4"); fantAchat(start, "E4 fenetre 00 et 30 billet", TIC, 10, { fp: +fp.toFixed(3) }); }
    }
  } catch (_) {}
}, 1000);
// ---------------------------------------------------------------- FANTÔME « billet bas + favori si recul 20 c » (accord de Pitch 13.10.2026 13:26)
// Par cycle et par côté : premier instant (60 à 240 s écoulées, contrôle chaque seconde) où le meilleur vendeur est entre 0,10 et 0,45 →
// achat fictif preneur 10 $ sur le carnet vu à +164 ms (limite + 1 c). Ensuite, chaque seconde jusqu'à 298 s : si le meilleur acheteur du
// billet ≤ prix payé − 0,20, achat fictif du favori (l'opposé), à +164 ms, limite meilleur vendeur + 2 c, de y = 0,5 × coût du billet /
// (1 − prix − frais) parts (moitié de la perte couverte). Une seule couverture. Enregistré dans le fichier du cycle (clé « bf »). AUCUN ORDRE RÉEL.
const BF = {};                                                            // "start|cote" → position
function bfAchat(id, lim, dollars, parts) {
  let q = 0, c = 0;
  for (const [px, sz] of asksTries(id)) { if (px > lim + 1e-9) break; const u = px + FEE7(px); const k = parts != null ? Math.min(sz, parts - q) : Math.min(sz, (dollars - c) / u); if (k <= 1e-9) break; q += k; c += k * u; }
  return { q: +q.toFixed(3), c: +c.toFixed(4) };
}
setInterval(() => {
  try {
    const t = now(), start = Math.floor(t / 300) * 300, el = t - start, mk = M[start];
    if (!mk || !mk.up || !mk.down) return;
    for (const X of ["Up", "Down"]) {
      const k = start + "|" + X, idX = X === "Up" ? mk.up : mk.down, idO = X === "Up" ? mk.down : mk.up;
      let P = BF[k];
      if (!P) {
        if (el < 60 || el > 240) continue;
        const a = asksTries(idX)[0];
        if (!a || a[0] < 0.10 - 1e-9 || a[0] > 0.45 + 1e-9) continue;
        P = BF[k] = { regle: "billet + favori 50 % si recul 20 c", start, cote: X, t: Math.round(t * 1000), a0: a[0], statut: "achat" };
        const R = recDe(start); (R.bf = R.bf || []).push(P); FANT.push(P);
        setTimeout(() => { const f = bfAchat(idX, a[0] + 0.01, 10); P.q = f.q; P.c = f.c; P.statut = f.q > 0 && f.c >= 5 ? "ouvert" : "non rempli"; }, 164);
        continue;
      }
      if (P.statut !== "ouvert" || el > 298) continue;
      const bb = meilleurAcheteur(idX), p0 = P.c / P.q;
      if (bb > 0 && bb <= p0 - 0.20 + 1e-9) {
        P.statut = "couverture"; P.tCouv = Math.round(t * 1000); P.bidCouv = bb;
        setTimeout(() => {
          const o = asksTries(idO)[0];
          if (!o) { P.statut = "ouvert sans couverture"; return; }
          const g = 1 - o[0] - FEE7(o[0]);
          if (g <= 0.005) { P.statut = "ouvert sans couverture"; return; }
          const y = 0.5 * P.c / g, f = bfAchat(idO, o[0] + 0.02, null, y);
          P.fav = { prix: o[0], visees: +y.toFixed(3), q: f.q, c: f.c }; P.statut = f.q >= 0.9 * y ? "couvert" : "couverture partielle";
        }, 164);
      }
    }
    for (const k of Object.keys(BF)) if (+k.split("|")[0] < start - 600) delete BF[k];
  } catch (_) {}
}, 1000);
setInterval(() => reglements().catch(() => {}), 10000);
setInterval(sonde, 15000);
setInterval(envoyer, 60000);
setInterval(versionDistante, 60000);
