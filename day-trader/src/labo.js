// Règles JOURNALIÈRES sur 1 an (barres journalières) : les 5 figures du scanner (leurs) et l'achat après
// de bons résultats trimestriels (leur outil Analyste), avec les mêmes filtres Bot95 (nos).
// Achat à l'ouverture du lendemain du signal, sortie après N jours à la clôture, ou au stop (2 × ATR).
import { figures } from "./scanner.js";
import { GLISSEMENT } from "./regles.js";

const FIG = ["breakout_20d", "bull_flag", "reclaim_ma20", "oversold", "oversold_bounce"];
const NOMS_FIG = { breakout_20d: "cassure du plus haut 20 j", bull_flag: "drapeau haussier", reclaim_ma20: "retour au-dessus de la MA20", oversold: "survendu (RSI < 30)", oversold_bounce: "rebond après survente" };
export const BASES_J = [
  ...FIG.flatMap((f) => [1, 3, 5].map((h) => ({ id: `j-${f}-${h}j`, type: "fig", fig: f, h, nom: `${NOMS_FIG[f]}, garder ${h} jour${h > 1 ? "s" : ""}` }))),
  { id: "res-5j", type: "res", h: 5, nom: "après de bons résultats (CA +10 % sur un an et BPA en hausse), garder 5 jours" },
  { id: "res-20j", type: "res", h: 20, nom: "après de bons résultats (CA +10 % sur un an et BPA en hausse), garder 20 jours" },
];
export const FILTRES_J = [
  { id: "aucun", camp: "leur", nom: "règle seule" },
  { id: "consensus", camp: "nous", nom: "+ consensus : au moins 2 de leurs signaux le même jour" },
  { id: "marche", camp: "nous", nom: "+ élan du marché : QQQ au-dessus de sa moyenne 20 jours" },
  { id: "liquide", camp: "nous", nom: "+ écart serré : seulement les 25 plus grosses" },
  { id: "sortie", camp: "nous", nom: "+ sortie anticipée si QQQ clôture sous sa moyenne 20 jours" },
  { id: "x2", camp: "nous", nom: "+ mise ×2 quand le consensus est fort" },
  { id: "tout", camp: "nous", nom: "+ consensus + élan + écart serré ensemble" },
];
export const REGLES_J = BASES_J.flatMap((b) => FILTRES_J.map((f) => ({ id: `${b.id}:${f.id}`, base: b, filtre: f, famille: b.type === "res" ? "résultats" : "journalier" })));

function atr(J, t, n = 14) {
  if (t < n) return null; let s = 0;
  for (let i = t - n + 1; i <= t; i++) s += Math.max(J[i].h - J[i].l, Math.abs(J[i].h - J[i - 1].c), Math.abs(J[i].l - J[i - 1].c));
  return s / n;
}

// J : barres journalières complètes [{d,o,h,l,c}] ; qqq : {date: {c, ma20}} ; res : dates de bons résultats (Set de dates de signal)
export function strategiesJour(J, { qqq = {}, liquide = false, resultats = new Set() } = {}) {
  const tags = J.map((_, t) => (t >= 30 ? figures(J.slice(0, t + 1).map((x) => x.c)).tags : []));
  const trades = [];
  for (const r of REGLES_J) {
    let libreA = -1; // pas deux trades ouverts en même temps pour la même règle
    for (let t = 30; t < J.length - 1; t++) {
      if (t <= libreA) continue;
      const d = J[t].d; const tg = tags[t];
      const sig = r.base.type === "fig" ? tg.includes(r.base.fig) : resultats.has(d);
      if (!sig) continue;
      const nbSignaux = tg.length + (resultats.has(d) ? 1 : 0);
      const consensus = nbSignaux >= 2;
      const q = qqq[d]; const marche = !!(q && q.ma20 && q.c > q.ma20);
      const f = r.filtre.id;
      if (f === "consensus" && !consensus) continue;
      if (f === "marche" && !marche) continue;
      if (f === "liquide" && !liquide) continue;
      if (f === "tout" && !(consensus && marche && liquide)) continue;
      const a = atr(J, t); if (!a) continue;
      const entree = J[t + 1].o * (1 + GLISSEMENT); const stop = entree - 2 * a;
      let sortie = null, issue = null, j = t + 1; const finJ = Math.min(J.length - 1, t + r.base.h);
      for (; j <= finJ; j++) {
        const b = J[j];
        if (j > t + 1 && b.o <= stop) { sortie = b.o * (1 - GLISSEMENT); issue = "stop"; break; }
        if (b.l <= stop) { sortie = stop * (1 - GLISSEMENT); issue = "stop"; break; }
        if (f === "sortie" && j < finJ) { const qj = qqq[b.d]; if (qj && qj.ma20 && qj.c < qj.ma20) { sortie = b.c * (1 - GLISSEMENT); issue = "sortie anticipée (marché)"; break; } }
      }
      if (sortie == null) { j = finJ; sortie = J[finJ].c * (1 - GLISSEMENT / 2); issue = "fin de durée"; }
      if (t + r.base.h > J.length - 1) continue; // trade pas encore terminé à la fin des données
      trades.push({ rid: r.id, d: J[t + 1].d, pct: (sortie - entree) / entree, R: (sortie - entree) / (entree - stop), w: f === "x2" && consensus ? 2 : 1 });
      libreA = j;
    }
  }
  return trades;
}

export function barresJour(s, aujourdHuiNY) {
  const out = [];
  for (let i = 0; i < s.t.length; i++) {
    const o = s.o?.[i], h = s.h?.[i], l = s.l?.[i], c = s.c[i], v = s.v?.[i] || 0;
    if ([o, h, l, c].some((x) => x == null)) continue;
    const d = new Date(s.t[i] * 1000 - 4 * 3600e3).toISOString().slice(0, 10);
    if (d >= aujourdHuiNY) continue; // seulement les journées terminées
    out.push({ d, o, h, l, c, v });
  }
  return out;
}

export function qqqJour(J) {
  const m = {};
  for (let i = 0; i < J.length; i++) { const s = J.slice(Math.max(0, i - 19), i + 1); m[J[i].d] = { c: J[i].c, ma20: s.length === 20 ? s.reduce((a, x) => a + x.c, 0) / 20 : null }; }
  return m;
}

// Bons résultats : chaque trimestre déposé à la SEC avec CA +10 % sur un an et BPA en hausse sur un an.
// Signal = le jour du dépôt (achat à l'ouverture suivante). Deux petites requêtes SEC par société.
const CA = ["RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues", "SalesRevenueNet"];
export async function datesBonsResultats(cik, ua) {
  const get = async (c) => { const r = await fetch(`https://data.sec.gov/api/xbrl/companyconcept/CIK${cik}/us-gaap/${c}.json`, { headers: { "User-Agent": ua } }); return r.status === 200 ? r.json() : null; };
  const trim = (j, unite) => {
    const out = {}; if (!j) return out;
    for (const f of (j.units?.[unite] || [])) {
      if (!f.start || !f.filed || !/^10-[QK]/.test(f.form || "")) continue;
      const jours = (Date.parse(f.end) - Date.parse(f.start)) / 864e5; if (jours < 80 || jours > 100) continue;
      if (!out[f.end] || f.filed < out[f.end].filed) out[f.end] = { v: f.val, filed: f.filed }; // première publication
    }
    return out;
  };
  let ca = {}; for (const c of CA) { ca = trim(await get(c), "USD"); if (Object.keys(ca).length >= 5) break; }
  const bpa = trim(await get("EarningsPerShareDiluted"), "USD/shares");
  const ilYaUnAn = (serie, fin) => { const c = Date.parse(fin) - 365 * 864e5; let best = null; for (const e of Object.keys(serie)) { const g = Math.abs(Date.parse(e) - c) / 864e5; if (g <= 12 && (!best || g < best[0])) best = [g, e]; } return best ? serie[best[1]] : null; };
  const dates = new Set();
  for (const [fin, x] of Object.entries(ca)) {
    const a = ilYaUnAn(ca, fin); const e = bpa[fin], ea = ilYaUnAn(bpa, fin);
    if (!a || !a.v || !e || !ea) continue;
    if (x.v / a.v - 1 >= 0.10 && e.v > ea.v) dates.add(x.filed);
  }
  return dates;
}
