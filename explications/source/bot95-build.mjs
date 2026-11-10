// Fig — « Comment bot95 choisit un trade » (règles de base), pour Pitch, 10.11.2026.
// La machine : un banc de tri. Le chariot éclairé = le prix BTC (Chainlink) qui glisse sur une règle graduée en écart au prix à battre.
// Un bloc central = la marge de sécurité (±0,08 %) : tant que le chariot est dessus, rien ne passe.
// Le cadran = le prix du billet Polymarket (aiguille, butée à 0,97). Les deux mâchoires = l'écart acheteur/vendeur du carnet (butée 1 c).
// Quand les trois verrous sont ouverts, le clapet du bon côté se lève et un jeton tombe dans le bac Up ou Down.
// Chiffres réels : marge 0,08 % (bot95, 05.10.2026), billet entre 0,03 et 0,97 (code bot95), écart ≤ 1 c (règle H1074),
// mise 50 $, frais taker 0,072 × p × (1 − p) par part, un billet gagnant paie 1 $.
import { writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import * as k from "../../kit/iso-kit.mjs";
import { kitScript } from "../../scripts/inline-kit.mjs";

const HERE = dirname(fileURLToPath(import.meta.url));
const theme = process.argv.includes("--light") ? "light" : "dark";
const WIDTH = 600, HEIGHT = 400;

// ---- modèle (pur, partagé avec la page) ----
const MODELE = { MARGE: 0.08, PMAX: 0.97, PMIN: 0.03, ECART: 0.01, MISE: 50, FRAIS: 0.072, PCT_UNIT: 400 };
// 1 % d'écart BTC ↔ 400 unités de règle : ±0,30 % ↔ ±120

const PLATE = { x: -150, y: -78, w: 300, d: 156, r: 8 };
const PLATE_H = 12, FOOT_H = 5;
const RAIL_Y = 6, RAIL_FROM = -128, RAIL_TO = 128;
const ZONE = MODELE.MARGE * MODELE.PCT_UNIT; // 32
const CAR = { w: 22, d: 30 };
const CAR_Z = 4, CAR_TOP = 10;
const DIAL = [-72, -44], DIAL_R = 22, DIAL_Z = 32, DIAL_H = 8, DIAL_TOP = DIAL_Z + DIAL_H;
const JAW = { x0: 52, y: -50, z: 0 };
const TRAY_DOWN = { x: -128, y: 42, w: 60, d: 28, r: 3 }, TRAY_UP = { x: 68, y: 42, w: 60, d: 28, r: 3 };

const P = k.fitProjection(
  [...k.boxCorners(PLATE, -PLATE_H - FOOT_H, 0), [DIAL[0], DIAL[1], DIAL_TOP + 4], [JAW.x0 + 60, JAW.y, 30]],
  WIDTH, HEIGHT, { pad: 26, azimuth: 40 },
);
const at = (p) => k.iso(p, P);
const S = (paths, style) => k.solidSvg(paths, style);
const L = (d, style) => k.lineSvg(d, style);
const D = (pts, style) => k.dotsSvg(pts, style);
const byDepth = (pts) => [...pts].sort((a, b) => k.depthOf([a[0], a[1], 0], P) - k.depthOf([b[0], b[1], 0], P));

function socle() {
  const out = [`<path class="iso-halo" d="${k.haloOf(PLATE, -PLATE_H - FOOT_H, PLATE_H, P)}"/>`];
  for (const [x, y] of byDepth(k.corners(PLATE, 22))) {
    out.push(S(k.cylinder(x, y, 7, -PLATE_H - FOOT_H, 1.6, P, 28), { tone: "lo" }));
    out.push(S(k.cylinder(x, y, 5.4, -PLATE_H - FOOT_H + 1.6, FOOT_H - 1.6, P, 28), { tone: "mid" }));
  }
  out.push(S(k.slabOf(PLATE, -PLATE_H, PLATE_H, P, 8, 1.6), { tone: "mid" }));
  out.push(L(k.planOutline(k.insetPlan(PLATE, 5), 0, P), { tone: "lo" }));
  const vis = k.corners(PLATE, 10);
  out.push(L(vis.map(([x, y]) => k.ring(x, y, 2.2, 0, P, 16)).join(""), { tone: "lo" }));
  out.push(D(vis.map(([x, y]) => at([x, y, 0])), { size: 0.5 }));
  // plaque signalétique
  const plaque = { x: -24, y: PLATE.y + PLATE.d - 16, w: 48, d: 9, r: 1 };
  out.push(S(k.slabOf(plaque, 0, 0.6, P, 3), { tone: "lo", crease: "none" }));
  out.push(k.faceTextSvg(k.topMatrix([0, plaque.y + 6], 0.6, P, "x"), "bot95", { size: 4, tone: "mid", anchor: "middle" }));
  out.push(D([at([plaque.x + 2, plaque.y + 4.5, 0.6]), at([plaque.x + plaque.w - 2, plaque.y + 4.5, 0.6])], { size: 0.4 }));
  return out.join("");
}

function bacs() {
  const out = [];
  for (const t of [TRAY_DOWN, TRAY_UP]) {
    out.push(S(k.slabOf(t, 0, 7, P, 4, 0.6), { tone: "mid" }));
    out.push(S(k.slabOf(k.insetPlan(t, 2.4), 3, 4.2, P, 4, 0.3), { tone: "lo", flat: true }));
    out.push(L(k.planOutline(k.insetPlan(t, 2.4), 7, P, 4), { tone: "lo" }));
    out.push(D(k.corners(t, 2.2).map(([x, y]) => at([x, y, 7])), { size: 0.4 }));
  }
  out.push(k.faceTextSvg(k.topMatrix([TRAY_DOWN.x + 30, TRAY_DOWN.y + TRAY_DOWN.d + 7], 0, P, "x"), "Down", { size: 4.2, tone: "mid", anchor: "middle" }));
  out.push(k.faceTextSvg(k.topMatrix([TRAY_UP.x + 30, TRAY_UP.y + TRAY_UP.d + 7], 0, P, "x"), "Up", { size: 4.2, tone: "mid", anchor: "middle" }));
  return out.join("");
}

function regle() {
  const out = [];
  // deux rails + butées
  for (const y of [RAIL_Y - 13, RAIL_Y + 9]) {
    out.push(S(k.slabOf({ x: RAIL_FROM, y, w: RAIL_TO - RAIL_FROM, d: 4, r: 1 }, 0, 3, P, 3, 0.4), { tone: "mid" }));
    out.push(D([RAIL_FROM + 5, 0, RAIL_TO - 5].map((x) => at([x, y + 2, 3])), { size: 0.4 }));
  }
  for (const x of [RAIL_FROM - 6, RAIL_TO + 1]) {
    out.push(S(k.slabOf({ x, y: RAIL_Y - 16, w: 5, d: 32, r: 1.2 }, 0, 8, P, 3, 0.5), { tone: "mid" }));
    out.push(D([at([x + 2.5, RAIL_Y - 11, 8]), at([x + 2.5, RAIL_Y + 11, 8])], { size: 0.45 }));
  }
  // règle graduée devant les rails : un tic par 0,01 %, majeur tous les 0,05 %
  const strip = { x: RAIL_FROM, y: RAIL_Y + 16, w: RAIL_TO - RAIL_FROM, d: 8, r: 1 };
  out.push(S(k.slabOf(strip, 0, 0.8, P, 3), { tone: "lo", crease: "none" }));
  const ticks = k.topTicks(-120, 120, 4, 5, strip.y + 0.6, 0.8, [2.2, 4.2], P);
  out.push(L(ticks.minor, { tone: "lo" }), L(ticks.major, { tone: "mid" }));
  out.push(L(k.lineOnTop([0, strip.y + 0.4], [0, strip.y + strip.d - 0.4], 0.8, P), { tone: "hi" }));
  out.push(D([at([strip.x + 2, strip.y + 4, 0.8]), at([strip.x + strip.w - 2, strip.y + 4, 0.8])], { size: 0.4 }));
  for (const [x, t] of [[-120, "−0,30 %"], [-60, "−0,15 %"], [0, "prix à battre"], [60, "+0,15 %"], [120, "+0,30 %"]])
    out.push(k.faceTextSvg(k.topMatrix([x, strip.y + strip.d + 6], 0, P, "x"), t, { size: 3.4, tone: x === 0 ? "hi" : "lo", anchor: "middle" }));
  // bloc de la marge de sécurité ±0,08 %
  const zone = { x: -ZONE, y: RAIL_Y - 9, w: ZONE * 2, d: 18, r: 1.5 };
  out.push(S(k.slabOf(zone, 0, 2.2, P, 3, 0.4), { tone: "lo" }));
  for (let x = -ZONE + 4; x < ZONE; x += 6) out.push(L(k.lineOnTop([x, zone.y + 2], [x + 3, zone.y + zone.d - 2], 2.2, P), { tone: "faint" }));
  out.push(D([at([zone.x + 2, zone.y + 2, 2.2]), at([zone.x + zone.w - 2, zone.y + 2, 2.2]), at([zone.x + 2, zone.y + zone.d - 2, 2.2]), at([zone.x + zone.w - 2, zone.y + zone.d - 2, 2.2])], { size: 0.4 }));
  return out.join("");
}

function chariot() { // posé à x = 0, déplacé par translateAlong
  const plan = { x: -CAR.w / 2, y: RAIL_Y - CAR.d / 2, w: CAR.w, d: CAR.d, r: 3 };
  const out = [`<path class="iso-halo" d="${k.haloOf(k.insetPlan(plan, 3), CAR_Z, 0.1, P)}" style="filter:blur(4px)"/>`];
  out.push(S(k.slabOf(plan, CAR_Z, CAR_TOP - CAR_Z, P, 5, 0.6), { tone: "mid" }));
  out.push(D([[-7, RAIL_Y - 12], [7, RAIL_Y - 12], [-7, RAIL_Y + 12], [7, RAIL_Y + 12]].map(([x, y]) => at([x, y, CAR_TOP])), { size: 0.45, tone: "lo" }));
  out.push(S(k.cylinder(0, RAIL_Y, 8, CAR_TOP, 7, P, 40, 0.6), { tone: "hi", lit: true }));
  out.push(L(k.ring(0, RAIL_Y, 5.2, CAR_TOP + 7, P, 32), { tone: "lo" }));
  out.push(k.faceTextSvg(k.topMatrix([0, RAIL_Y + 1.6], CAR_TOP + 7, P, "x"), "BTC", { size: 3.2, tone: "lo", anchor: "middle" }));
  // index vers la règle
  out.push(S(k.slabOf({ x: -1.2, y: RAIL_Y + 15, w: 2.4, d: 7, r: 0.6 }, CAR_Z, 2, P, 2), { tone: "hi", lit: true }));
  return out.join("");
}

// ---- cadran du prix du billet : 0,50 en bas à gauche, 1,00 à droite, sur 270° ----
const A0 = -Math.PI * 0.75, SPAN = Math.PI * 1.5;
const angDe = (p) => A0 + ((Math.max(0.5, Math.min(1, p)) - 0.5) / 0.5) * SPAN;
function cadran() {
  const [x, y] = DIAL, out = [];
  out.push(S(k.cylinder(x, y, 9, 0, 3, P, 28), { tone: "lo" }));
  out.push(S(k.cylinder(x, y, 3, 3, DIAL_Z - 3, P, 20), { tone: "mid", crease: "none" }));
  out.push(L([16, 34].map((z) => k.sideArc(x, y, 3, z, P, 12)).join(""), { tone: "faint" }));
  out.push(S(k.cylinder(x, y, DIAL_R, DIAL_Z, DIAL_H, P, 64, 0.8), { tone: "hi", crease: "lo" }));
  out.push(L(k.knurl(x, y, DIAL_R, DIAL_TOP - 3, DIAL_TOP, 80, P, 0.3), { tone: "lo" }));
  out.push(L(k.ring(x, y, DIAL_R - 2.2, DIAL_TOP, P, 64), { tone: "lo" }));
  const T = k.radialTicks(x, y, DIAL_R - 3, 50, 5, DIAL_TOP, [1.3, 2.8], P, A0, SPAN);
  out.push(L(T.minor, { tone: "lo" }), L(T.major, { tone: "mid" }));
  // butée 0,97 : tic éclairé
  const a = angDe(MODELE.PMAX), r1 = DIAL_R - 7, r2 = DIAL_R - 2.4;
  out.push(L(k.lineOnTop([x + Math.sin(a) * r1, y - Math.cos(a) * r1], [x + Math.sin(a) * r2, y - Math.cos(a) * r2], DIAL_TOP + 0.1, P), { tone: "lit" }));
  out.push(L(k.ring(x, y, 1.6, DIAL_TOP, P, 16), { tone: "mid" }));
  out.push(k.faceTextSvg(k.topMatrix([x, y + 10], DIAL_TOP, P, "x"), "billet", { size: 2.6, tone: "lo", anchor: "middle" }));
  return out.join("");
}
const aiguille = (p) => {
  const a = angDe(p), [x, y] = DIAL;
  return k.lineOnTop([x - Math.sin(a) * 3.4, y + Math.cos(a) * 3.4], [x + Math.sin(a) * (DIAL_R - 4), y - Math.cos(a) * (DIAL_R - 4)], DIAL_TOP + 0.2, P);
};

// ---- mâchoires de l'écart du carnet : 1 c = 10 unités ----
const PAR_CENT = 10;
function machoiresFixes() {
  const out = [];
  const banc = { x: JAW.x0 - 6, y: JAW.y - 12, w: 76, d: 24, r: 2 };
  out.push(S(k.slabOf(banc, 0, 5, P, 4, 0.5), { tone: "mid" }));
  out.push(L(k.lineOnTop([banc.x + 4, JAW.y], [banc.x + banc.w - 4, JAW.y], 5, P), { tone: "faint" }));
  out.push(D(k.corners(banc, 2.4).map(([x, y]) => at([x, y, 5])), { size: 0.4 }));
  // mâchoire fixe (acheteur) + butée à 1 c
  out.push(S(k.slabOf({ x: JAW.x0, y: JAW.y - 8, w: 8, d: 16, r: 1 }, 5, 16, P, 3, 0.5), { tone: "mid" }));
  out.push(S(k.slabOf({ x: JAW.x0 + 8 + PAR_CENT, y: JAW.y + 8.5, w: 2, d: 3, r: 0.5 }, 5, 10, P, 2), { tone: "hi", lit: true }));
  const T = k.topTicks(JAW.x0 + 8, JAW.x0 + 8 + 40, 2, 5, JAW.y - 11.4, 5, [1.4, 2.6], P);
  out.push(L(T.minor, { tone: "lo" }), L(T.major, { tone: "mid" }));
  out.push(k.faceTextSvg(k.topMatrix([JAW.x0 + 30, JAW.y + 16.5], 5, P, "x"), "écart", { size: 2.8, tone: "lo", anchor: "middle" }));
  return out.join("");
}
function machoireMobile() { // posée à écart 0, déplacée en x
  return S(k.slabOf({ x: JAW.x0 + 8, y: JAW.y - 8, w: 8, d: 16, r: 1 }, 5, 16, P, 3, 0.5), { tone: "hi" })
    + L(k.knurl(JAW.x0 + 12, JAW.y, 2.4, 21, 24, 14, P), { tone: "lo" })
    + S(k.cylinder(JAW.x0 + 12, JAW.y, 2.4, 21, 3, P, 18), { tone: "mid" });
}

// ---- clapets et jeton ----
const CLAPET = (x0) => ({ x: x0, y: 32, w: 30, d: 3, r: 0.6 });
function clapet(x0) { return S(k.slabOf(CLAPET(x0), 0, 9, P, 2, 0.3), { tone: "mid" }) + D([at([x0 + 3, 33.5, 9]), at([x0 + 27, 33.5, 9])], { size: 0.4 }); }
function jeton() { return S(k.cylinder(0, 0, 5, 0, 2.2, P, 32, 0.4), { tone: "hi", lit: true }) + L(k.ring(0, 0, 3.2, 2.2, P, 24), { tone: "lo" }); }

const svg = k.figureSvg({
  width: WIDTH, height: HEIGHT,
  label: "Un banc de tri qui montre les règles de base de bot95 : le chariot BTC glisse sur une règle graduée en écart au prix à battre ; une zone centrale de ±0,08 % bloque tout ; un cadran montre le prix du billet Polymarket avec une butée à 0,97 ; deux mâchoires montrent l'écart du carnet avec une butée à 1 centime. Quand les trois conditions sont réunies, un clapet s'ouvre et un jeton tombe dans le bac Up ou Down.",
  body: [
    socle(), cadran(),
    `<path data-part="aiguille" class="iso-line" data-tone="lit" data-free="start" d="${aiguille(0.95)}" style="stroke-width:1.1"/>`,
    machoiresFixes(),
    `<g data-part="machoire">${machoireMobile()}</g>`,
    regle(),
    `<g data-part="chariot">${chariot()}</g>`,
    bacs(),
    `<g data-part="clapet-down">${clapet(-113)}</g>`,
    `<g data-part="clapet-up">${clapet(83)}</g>`,
    `<g data-part="jeton" style="opacity:0">${jeton()}</g>`,
  ],
});

const live = `
const P = ${JSON.stringify(P)};
const M = ${JSON.stringify(MODELE)};
const DIAL = ${JSON.stringify(DIAL)}, DIAL_R = ${DIAL_R}, DIAL_TOP = ${DIAL_TOP}, PAR_CENT = ${PAR_CENT};
const A0 = ${A0}, SPAN = ${SPAN};
const angDe = ${angDe.toString()};
const aiguille = ${aiguille.toString().replace(/k\.lineOnTop/g, "lineOnTop")};
const stage = document.querySelector(".iso-stage"), svg = stage.querySelector("svg");
const $ = (n) => svg.querySelector('[data-part="' + n + '"]');
const chariot = $("chariot"), aig = $("aiguille"), mach = $("machoire"), cD = $("clapet-down"), cU = $("clapet-up"), jet = $("jeton");
const readout = document.querySelector("[data-readout]"), detail = document.querySelector("[data-detail]");
const still = matchMedia("(prefers-reduced-motion: reduce)");
const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
const fr = (v, d = 2) => v.toFixed(d).replace(".", ",");
// scénarios de la visite : écart BTC (%), prix du billet, écart du carnet ($)
const VISITE = [
  { d: 0.04, p: 0.80, e: 0.01 }, { d: 0.12, p: 0.95, e: 0.01 }, { d: 0.12, p: 0.95, e: 0.03 },
  { d: 0.26, p: 0.99, e: 0.01 }, { d: -0.15, p: 0.96, e: 0.01 },
];
function decide(s) {
  const cote = s.d > 0 ? "Up" : "Down";
  if (Math.abs(s.d) < M.MARGE) return { ok: false, pourquoi: "trop près du prix à battre (< 0,08 %)" };
  if (s.p > M.PMAX) return { ok: false, pourquoi: "billet trop cher (> 0,97)" };
  if (s.p < M.PMIN) return { ok: false, pourquoi: "billet hors limites" };
  if (s.e > M.ECART + 1e-9) return { ok: false, pourquoi: "écart du carnet > 1 c" };
  const parts = M.MISE / s.p, frais = parts * M.FRAIS * s.p * (1 - s.p);
  return { ok: true, cote, gain: parts * (1 - s.p) - frais, perte: M.MISE + frais };
}
let cur = { ...VISITE[0] }, but = { ...VISITE[0] }, pas = 0, horloge = 0, visite = true, visible = false, img = 0, last = 0, attente = 0, chute = 0, decTxt = "";
function dessiner() {
  chariot.setAttribute("transform", translateAlong(P, [clamp(cur.d, -0.3, 0.3) * M.PCT_UNIT, 0, 0]));
  aig.setAttribute("d", aiguille(cur.p));
  mach.setAttribute("transform", translateAlong(P, [cur.e * 100 * PAR_CENT, 0, 0]));
  const r = decide(but);
  const ouvre = (c) => r.ok && r.cote === c ? 1 : 0;
  cD.setAttribute("transform", translateAlong(P, [0, 0, 10 * ouvreD]));
  cU.setAttribute("transform", translateAlong(P, [0, 0, 10 * ouvreU]));
  if (r.ok) {
    const x0 = r.cote === "Up" ? 98 : -98, xc = clamp(but.d, -0.3, 0.3) * M.PCT_UNIT;
    const t = Math.min(1, chute), x = xc + (x0 - xc) * t, y = 6 + (56 - 6) * t, z = 20 * (1 - t) * (1 - t) + 4 * t;
    jet.setAttribute("transform", translateAlong(P, [x, y, z])); jet.style.opacity = String(Math.min(1, chute * 4));
  } else jet.style.opacity = "0";
  const court = r.ok ? "ACHAT " + r.cote : "pas d'achat";
  const txt = "BTC " + (but.d > 0 ? "+" : "") + fr(but.d) + " % · billet " + fr(but.p) + " · écart " + Math.round(but.e * 100) + " c → "
    + (r.ok ? "ACHAT " + r.cote + " : +" + fr(r.gain) + " $ si gagné, −" + fr(r.perte) + " $ si perdu" : "pas d'achat : " + r.pourquoi);
  if (readout.textContent !== court) readout.textContent = court;
  if (detail.textContent !== txt) { detail.textContent = txt; detail.dataset.ok = r.ok ? "1" : "0"; }
  stage.setAttribute("aria-valuetext", txt);
}
let ouvreD = 0, ouvreU = 0;
function tick(now) {
  const dt = last ? Math.min((now - last) / 1000, 1 / 30) : 1 / 60; last = now;
  const calme = still.matches;
  if (visite) { horloge += dt; const i = Math.floor(horloge / 3.4) % VISITE.length; if (i !== pas) { pas = i; but = { ...VISITE[i] }; chute = 0; } }
  const f = calme ? 1 : 1 - Math.exp(-dt / 0.25);
  cur.d += (but.d - cur.d) * f; cur.p += (but.p - cur.p) * f; cur.e += (but.e - cur.e) * f;
  const r = decide(but), proche = Math.abs(cur.d - but.d) < 0.004 && Math.abs(cur.p - but.p) < 0.004 && Math.abs(cur.e - but.e) < 0.0004;
  const vD = r.ok && r.cote === "Down" && proche ? 1 : 0, vU = r.ok && r.cote === "Up" && proche ? 1 : 0;
  ouvreD += (vD - ouvreD) * (calme ? 1 : 1 - Math.exp(-dt / 0.15)); ouvreU += (vU - ouvreU) * (calme ? 1 : 1 - Math.exp(-dt / 0.15));
  if (r.ok && proche) chute = calme ? 1 : Math.min(1, chute + dt / 0.9);
  dessiner();
  img = visible ? requestAnimationFrame(tick) : 0;
}
const lancer = () => { if (!img && visible) { last = 0; img = requestAnimationFrame(tick); } };
const piloter = (s) => { visite = false; but = s; chute = 0; clearTimeout(attente); attente = setTimeout(() => { visite = !still.matches; horloge = 0; pas = -1; lancer(); }, 5000); lancer(); };
new IntersectionObserver((e) => { visible = e[e.length - 1].isIntersecting; if (visible) lancer(); }, { rootMargin: "120px 0px" }).observe(stage);
if (still.matches) visite = false;
stage.addEventListener("pointermove", (ev) => {
  const b = svg.getBoundingClientRect(), part = clamp((ev.clientX - b.left) / b.width, 0, 1);
  piloter({ ...but, d: Math.round((-0.3 + part * 0.6) * 100) / 100 });
});
stage.addEventListener("keydown", (ev) => {
  let s = { ...but };
  if (ev.key === "ArrowRight") s.d = clamp(+(s.d + 0.01).toFixed(2), -0.3, 0.3);
  else if (ev.key === "ArrowLeft") s.d = clamp(+(s.d - 0.01).toFixed(2), -0.3, 0.3);
  else if (ev.key === "ArrowUp") s.p = clamp(+(s.p + 0.01).toFixed(2), 0.5, 1);
  else if (ev.key === "ArrowDown") s.p = clamp(+(s.p - 0.01).toFixed(2), 0.5, 1);
  else if (ev.key === "e" || ev.key === "E") s.e = s.e > 0.015 ? 0.01 : 0.03;
  else return;
  ev.preventDefault(); piloter(s);
});
dessiner();
`;

const body = k.plateHtml({
  fig: "Fig 1",
  title: "Comment bot95 choisit un trade",
  hint: "Glisse : prix BTC",
  readout: "pas d'achat",
  keys: [
    { mark: "lit", label: "Le chariot BTC (prix Chainlink) et ce qui décide : butée 0,97 du cadran, butée 1 c de l'écart, le jeton acheté" },
    { mark: "raised", label: "La zone de sécurité ±0,08 % autour du prix à battre : rien ne passe dessus" },
  ],
  caption: "Les règles de base de bot95 sur un marché BTC 5 minutes, en fin de cycle : acheter le côté où se trouve le prix seulement s'il a franchi le prix à battre d'au moins 0,08 %, si le billet coûte au plus 0,97 et si l'écart du carnet est d'1 centime au plus. Mise 50 $, frais Polymarket 0,072 × p × (1 − p) par billet, un billet gagnant paie 1 $. Le compteur montre le vrai déséquilibre : à 0,95, on gagne environ 2,45 $ si le pari passe et on perd environ 50 $ s'il rate. Les stratégies réelles ajoutent d'autres filtres (consensus, élan du perp Bybit…).",
  body: `<div class="iso-stage" tabindex="0" role="slider" aria-label="Banc de tri de bot95 : flèches gauche et droite pour le prix BTC, haut et bas pour le prix du billet, E pour l'écart" aria-valuetext="">${svg}</div>`,
});

const nom0 = 0;
const nom = theme === "light" ? "bot95-light.html" : "bot95.html";
const detailHtml = `<p data-detail style="max-width:650px;margin:10px auto 0;font:15px/1.5 -apple-system,system-ui,sans-serif;padding:10px 14px;border-radius:10px;border:1px solid rgba(128,128,128,.35)">BTC +0,04 % · billet 0,80 · écart 1 c → pas d'achat : trop près du prix à battre (< 0,08 %)</p>
<p style="max-width:650px;margin:8px auto 0;font:14px/1.5 -apple-system,system-ui,sans-serif;opacity:.75">Sur ordinateur : flèches ← → pour le prix BTC, ↑ ↓ pour le prix du billet, E pour l'écart du carnet. Sinon la machine passe seule en revue 5 cas.</p>`;
writeFileSync(join(HERE, nom), k.pageHtml({ title: "Comment bot95 choisit un trade", theme, body: body.replace(/(<\/figure>|<\/div>\s*)$/, "$1") + detailHtml, script: kitScript() + live }));
console.log("wrote", nom);
