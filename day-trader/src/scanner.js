// Scanner de graphiques (trader-scanner) : figures journalières et cassures du range d'ouverture.
// « Un scan est une liste de graphiques qui remplissent une règle, pas une liste d'actions à acheter. »
import { local, seance, marcheDe, hhmm, estBtc } from "./temps.js";
import { sparkTout, graphique, barres, parLots } from "./donnees.js";

export const FIGURES = {
  breakout_20d: "cassure du plus haut de clôture 20 jours",
  bull_flag: "drapeau haussier",
  reclaim_ma20: "repasse au-dessus de la moyenne 20 jours",
  oversold: "survendu (RSI sous 30)",
  oversold_bounce: "rebond après survente",
};

export function rsi(c, n = 14) {
  if (c.length < n + 1) return null;
  const g = [], b = [];
  for (let i = 1; i < c.length; i++) { g.push(Math.max(0, c[i] - c[i - 1])); b.push(Math.max(0, c[i - 1] - c[i])); }
  let ag = g.slice(0, n).reduce((a, x) => a + x, 0) / n, al = b.slice(0, n).reduce((a, x) => a + x, 0) / n;
  for (let i = n; i < g.length; i++) { ag = (ag * (n - 1) + g[i]) / n; al = (al * (n - 1) + b[i]) / n; }
  return al ? 100 - 100 / (1 + ag / al) : 100;
}

// Clôtures journalières COMPLÈTES : la barre du jour n'est gardée qu'après la clôture.
export function cloturesJour(s, sym, maintenantMs) {
  const m = marcheDe(sym); const now = local(maintenantMs, m);
  const se = seance(now.date, m);
  const finie = !se || now.min >= se[1];
  const out = new Map();
  for (let i = 0; i < s.t.length; i++) {
    const c = s.c[i]; if (c == null) continue;
    const d = local(s.t[i] * 1000, m).date;
    if (d > now.date || (d === now.date && !finie)) continue;
    out.set(d, +c);
  }
  return [...out.keys()].sort().map((d) => [d, out.get(d)]);
}

export function figures(c) {
  const last = c[c.length - 1];
  const sl = (a, b) => c.slice(a < 0 ? c.length + a : a, b === undefined ? undefined : c.length + b);
  const hi20 = Math.max(...sl(-21, -1));
  const ma20 = sl(-20).reduce((a, x) => a + x, 0) / 20;
  const ma20p = sl(-21, -1).reduce((a, x) => a + x, 0) / 20;
  const run = c[c.length - 6] / c[c.length - 16] - 1;
  const r5 = sl(-5); const rng5 = (Math.max(...r5) - Math.min(...r5)) / last;
  const r = rsi(c), rp = rsi(c.slice(0, -1));
  const t = [];
  if (last > hi20) t.push("breakout_20d");
  if (run > 0.10 && rng5 < 0.05) t.push("bull_flag");
  if (c[c.length - 2] < ma20p && last > ma20) t.push("reclaim_ma20");
  if (r != null && r < 30) t.push("oversold");
  if (rp != null && rp < 30 && last > c[c.length - 2]) t.push("oversold_bounce");
  return { tags: t, rsi: r, ma20, hi20 };
}

// Scan journalier (avant l'ouverture). min_price 5 $, min_volume 1 000 000 comme l'original.
export async function scanJour(symboles, maintenantMs, { prixMin = 5, volumeMin = 1e6 } = {}) {
  const { data, echecs } = await sparkTout(symboles, "3mo", "1d");
  const hits = []; const comptes = { demandes: symboles.length, recus: 0, illiquides: 0, courts: 0, scannes: 0 };
  const liquides = [];
  for (const sym of symboles) {
    const s = data[sym]; if (!s) continue; comptes.recus++;
    const bars = cloturesJour(s, sym, maintenantMs);
    let prix = s.meta.regularMarketPrice; if (prix == null && bars.length) prix = bars[bars.length - 1][1];
    const vol = s.meta.regularMarketVolume;
    const btc = estBtc(sym);
    if (!btc && (prix == null || prix < prixMin || vol == null || vol < volumeMin)) { comptes.illiquides++; continue; }
    liquides.push([sym, (prix || 0) * (vol || 0)]);
    if (bars.length < 30) { comptes.courts++; continue; }
    comptes.scannes++;
    const c = bars.map((b) => b[1]);
    const f = figures(c);
    if (f.tags.length) hits.push({ symbol: sym, figures: f.tags, prix: +c[c.length - 1].toFixed(2), date: bars[bars.length - 1][0], rsi: +f.rsi.toFixed(1), volume: vol ?? null });
  }
  hits.sort((a, b) => (b.prix * (b.volume || 0)) - (a.prix * (a.volume || 0)) || a.symbol.localeCompare(b.symbol));
  comptes.trouves = hits.length; comptes.echecs = Object.keys(echecs).length;
  liquides.sort((a, b) => b[1] - a[1]);
  return { hits, comptes, liquides: liquides.map((x) => x[0]) };
}

// ------------------------------------------------------------- cassure du range d'ouverture (ORB)
export function barresSeance(s, sym, jour, coupureMin) {
  return barres(s, sym, Date.now() + 864e5).filter((b) => b.date === jour && b.min + 5 <= coupureMin);
}
export function utilisable(bars, jour, sym, coupureMin, nRange) {
  const m = marcheDe(sym); const se = seance(jour, m); if (!se) return false;
  const voulu = Math.min(Math.floor((coupureMin - se[0]) / 5), Math.floor((se[1] - se[0]) / 5));
  if (voulu < nRange || bars.length !== voulu) return false;
  return bars.every((b, k) => b.slot === k);
}
export function candidatOrb(bars, n) { const top = Math.max(...bars.slice(0, n).map((b) => b.c)); return bars.slice(n).some((b) => b.c >= top); }
export function cassureOrb(bars, n) {
  const r = bars.slice(0, n);
  if (r.some((b) => b.h == null || b.l == null)) return null;
  const oh = Math.max(...r.map((b) => b.h)), ol = Math.min(...r.map((b) => b.l));
  for (let k = n; k < bars.length; k++) {
    const b = bars[k];
    if (b.c > oh) return { prix: +b.c.toFixed(2), a: hhmm(b.min + 5), barre: hhmm(b.min), indice: k, haut: +oh.toFixed(2), bas: +ol.toFixed(2), pctAuDessus: +((b.c / oh - 1) * 100).toFixed(2) };
  }
  return null;
}

// Fenêtre de l'ORB : le jour et l'heure de coupure, ou un message clair
export function fenetreOrb(sym, maintenantMs, minutesRange = 15, aMin = null, jourForce = null) {
  const m = marcheDe(sym); const now = local(maintenantMs, m);
  const jour = jourForce || now.date;
  const se = seance(jour, m);
  if (!se) return { erreur: `Pas de séance le ${jour} : le marché est fermé.` };
  const finRange = se[0] + minutesRange, premiere = finRange + 5;
  let coupure = aMin != null ? aMin : (jour === now.date ? now.min : se[1]);
  if (jour === now.date && coupure > now.min) coupure = now.min;
  if (coupure > se[1]) coupure = se[1];
  if (coupure < premiere) return { erreur: `Il est ${hhmm(coupure)} (${m.tz}) : le range de ${minutesRange} min va de ${hhmm(se[0])} à ${hhmm(finRange)} et la première barre après se termine à ${hhmm(premiere)}. Relance après ${hhmm(premiere)}.` };
  return { jour, coupure, seance: se };
}

export async function scanOrb(symboles, maintenantMs, { minutesRange = 15, prixMin = 5, maxConfirm = 200 } = {}) {
  const n = minutesRange / 5;
  const out = { hits: [], comptes: { demandes: symboles.length, recus: 0, inutilisables: 0, illiquides: 0, scannes: 0, candidats: 0, confirmes: 0, nonConfirmes: 0 }, echecs: {} };
  const parMarche = { actions: symboles.filter((s) => !estBtc(s)), btc: symboles.filter(estBtc) };
  const cands = [];
  for (const [cle, syms] of Object.entries(parMarche)) {
    if (!syms.length) continue;
    const f = fenetreOrb(syms[0], maintenantMs, minutesRange);
    if (f.erreur) { out[cle === "btc" ? "messageBtc" : "message"] = f.erreur; continue; }
    out[cle === "btc" ? "coupureBtc" : "coupure"] = hhmm(f.coupure) + (cle === "btc" ? " UTC" : " New York"); out.jour = out.jour || f.jour;
    const { data } = await sparkTout(syms, "1d", "5m");
    for (const sym of syms) {
      const s = data[sym]; if (!s) continue; out.comptes.recus++;
      const bars = barresSeance(s, sym, f.jour, f.coupure);
      if (!utilisable(bars, f.jour, sym, f.coupure, n)) { out.comptes.inutilisables++; continue; }
      const vol = s.v ? bars.reduce((a, b) => a + b.v, 0) : (s.meta.regularMarketVolume || 0);
      if (!estBtc(sym) && bars[bars.length - 1].c < prixMin) { out.comptes.illiquides++; continue; }
      out.comptes.scannes++;
      if (candidatOrb(bars, n)) cands.push({ sym, jour: f.jour, coupure: f.coupure, poids: bars[bars.length - 1].c * vol });
    }
  }
  out.comptes.candidats = cands.length;
  cands.sort((a, b) => b.poids - a.poids);
  if (cands.length > maxConfirm) { out.comptes.nonConfirmes = cands.length - maxConfirm; cands.length = maxConfirm; }
  const res = await parLots(cands, 8, async (c) => {
    const s2 = await graphique(c.sym, "1d", "5m");
    const full = barresSeance(s2, c.sym, c.jour, c.coupure);
    if (!utilisable(full, c.jour, c.sym, c.coupure, n)) return { erreur: "une barre manque dans le graphique" };
    return { hit: cassureOrb(full, n) };
  });
  res.forEach((r, i) => {
    if (r.erreur) { out.echecs[cands[i].sym] = r.erreur; return; }
    out.comptes.confirmes++;
    if (r.hit) out.hits.push({ symbol: cands[i].sym, ...r.hit });
  });
  out.hits.sort((a, b) => a.a.localeCompare(b.a) || a.symbol.localeCompare(b.symbol));
  out.comptes.trouves = out.hits.length;
  return out;
}
