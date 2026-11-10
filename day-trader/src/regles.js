// Règles INTRADAY (barres 5 min, actions US). Une seule fonction simule une séance :
// le banc d'essai et le paper l'utilisent toutes les deux, donc le paper ne peut pas diverger du test.
//  - « leurs » idées (dépôt day-trader-skill) : cassure du range d'ouverture, clôture au-dessus du haut
//    de la veille, figure journalière du scanner, filtre Time Machine
//  - « nos » idées (leçons Bot95) : consensus, élan du marché, bonnes heures, liquidité / écart serré,
//    sortie anticipée quand le marché se retourne, mise ×2 quand le consensus est fort
import { figures } from "./scanner.js";
import { HasardPython } from "./hasard.js";

export const BASES = [
  { id: "orb-mid1", type: "orb", stop: "mid", R: 1, nom: "cassure du range d'ouverture 15 min, stop milieu du range, cible 1R" },
  { id: "orb-low2", type: "orb", stop: "low", R: 2, nom: "cassure du range d'ouverture 15 min, stop bas du range, cible 2R" },
  { id: "orb-lowF", type: "orb", stop: "low", R: null, nom: "cassure du range d'ouverture 15 min, stop bas du range, sortie 15 h 55" },
  { id: "veille-2R", type: "veille", stop: "pct1", R: 2, nom: "clôture 5 min au-dessus du plus haut de la veille, stop 1 %, cible 2R" },
];
export const FILTRES = [
  { id: "aucun", camp: "leur", nom: "règle seule" },
  { id: "figure", camp: "leur", nom: "+ figure journalière la veille (scanner)" },
  { id: "tm", camp: "leur", nom: "+ Time Machine : les replays donnent la cible plus souvent qu'il ne faut" },
  { id: "consensus", camp: "nous", nom: "+ consensus : au moins 2 de leurs signaux d'accord (ORB, haut de la veille, figure)" },
  { id: "marche", camp: "nous", nom: "+ élan du marché : QQQ au-dessus de son ouverture" },
  { id: "heure", camp: "nous", nom: "+ bonnes heures : entrée avant 11 h New York" },
  { id: "liquide", camp: "nous", nom: "+ écart serré : seulement les 25 plus grosses" },
  { id: "sortie", camp: "nous", nom: "+ sortie anticipée si QQQ repasse sous son ouverture" },
  { id: "x2", camp: "nous", nom: "+ mise ×2 quand le consensus est fort" },
  { id: "tout", camp: "nous", nom: "+ consensus + élan + écart serré ensemble" },
];
export const REGLES = BASES.flatMap((b) => FILTRES.filter((f) => !(f.id === "tm" && !b.R)).map((f) => ({ id: `${b.id}:${f.id}`, base: b, filtre: f, famille: "intraday" })));
export const REGLE = Object.fromEntries(REGLES.map((r) => [r.id, r]));

export const GLISSEMENT = 0.0005;          // 0,05 % payé à l'entrée et sur un stop (estimation prudente)
const sousCentime = (x) => Math.floor(Math.round(x * 1e6) / 1e4) / 100;
const OUV = 9 * 60 + 30;

// ctx : { qqq: barres QQQ du jour, figureVeille, hautVeille, liquide, pool (séances précédentes pour la Time Machine), finIndex, dernierePossible }
export function simulerSeance(sym, D, ctx = {}, regles = REGLES) {
  const { qqq = null, figureVeille = false, hautVeille = null, liquide = false, pool = null, nRange = 3 } = ctx;
  const n = D.length; if (n <= nRange + 1 || D.slice(0, nRange).some((b) => !b)) return {};
  const oh = Math.max(...D.slice(0, nRange).map((b) => b.h)), ol = Math.min(...D.slice(0, nRange).map((b) => b.l));
  const fin = ctx.finIndex != null ? Math.min(ctx.finIndex, n - 1) : n - 1;
  const derniere = ctx.dernierePossible != null ? ctx.dernierePossible : fin - 1;
  const marcheOk = (k) => !!(qqq && qqq[k] && qqq[0] && qqq[k].c > qqq[0].o);
  // premier signal de chaque type de base
  const premier = { orb: null, veille: null };
  for (let k = nRange; k <= Math.min(derniere, n - 2); k++) {
    const b = D[k]; if (!b || !D[k + 1]) continue;
    if (b.min + 5 < 9 * 60 + 45 || b.min + 5 > 15 * 60 + 30) continue; // fenêtre d'entrée du dépôt d'origine
    if (premier.orb == null && b.c > oh) premier.orb = k;
    if (premier.veille == null && hautVeille && b.c > hautVeille) premier.veille = k;
  }
  const out = {};
  const tmCache = {};
  for (const r of regles) {
    const k = premier[r.base.type]; if (k == null) continue;
    const b = D[k];
    const autres = [premier.orb != null && premier.orb <= k, premier.veille != null && premier.veille <= k, !!figureVeille].filter(Boolean).length;
    const consensus = autres >= 2;
    const f = r.filtre.id;
    if (f === "figure" && !figureVeille) continue;
    if (f === "consensus" && !consensus) continue;
    if (f === "marche" && !marcheOk(k)) continue;
    if (f === "heure" && b.min + 5 > 11 * 60) continue;
    if (f === "liquide" && !liquide) continue;
    if (f === "tout" && !(consensus && marcheOk(k) && liquide)) continue;
    const t = executer(D, k, r.base, { oh, ol, fin, qqq: f === "sortie" ? qqq : null });
    if (t.statut === "annule") continue;
    if (f === "tm") {
      if (!pool) continue;
      const cle = r.base.id;
      if (tmCache[cle] === undefined) tmCache[cle] = tmFavorable(pool, t, k, fin);
      if (!tmCache[cle]) continue;
    }
    t.w = f === "x2" && consensus ? 2 : 1;
    out[r.id] = t;
  }
  return out;
}

export function executer(D, k, base, { oh, ol, fin, qqq = null }) {
  const e0 = D[k + 1].o;
  const entree = e0 * (1 + GLISSEMENT);
  const stop = sousCentime(base.stop === "mid" ? (oh + ol) / 2 : base.stop === "low" ? ol : entree * 0.99);
  if (!(entree > stop)) return { k, statut: "annule" };
  const risque = entree - stop;
  const cible = base.R ? Math.round((entree + base.R * risque) * 100) / 100 : null;
  let sortie = null, issue = null, j = k + 1;
  for (; j <= fin; j++) {
    const b = D[j]; if (!b) continue;
    if (j > k + 1 && b.o <= stop) { sortie = b.o * (1 - GLISSEMENT); issue = "stop"; break; }
    if (cible && j > k + 1 && b.o >= cible) { sortie = b.o; issue = "cible"; break; }
    if (b.l <= stop) { sortie = stop * (1 - GLISSEMENT); issue = "stop"; break; }
    if (cible && b.h >= cible) { sortie = cible; issue = "cible"; break; }
    if (qqq && qqq[j] && qqq[0] && qqq[j].c < qqq[0].o) { sortie = b.c * (1 - GLISSEMENT); issue = "sortie anticipée (marché)"; break; }
  }
  let ouvert = false;
  if (sortie == null) {
    if (D.length - 1 < fin) { ouvert = true; j = D.length - 1; sortie = D[j].c; issue = "en cours"; }
    else { j = fin; sortie = D[fin].c; issue = "fin de séance"; }
  }
  return { k, j, statut: ouvert ? "ouvert" : "ferme", entree: +entree.toFixed(4), stop, cible, sortie: +sortie.toFixed(4), issue, pct: (sortie - entree) / entree, R: (sortie - entree) / risque };
}

// Filtre Time Machine (leur outil) : 300 replays sur les séances précédentes ; on garde le trade si la cible
// arrive en premier plus souvent que l'équilibre 1 / (1 + R). Même graine 19 que l'original.
export function tmFavorable(pool, t, k, fin, replays = 300) {
  if (!t.cible) return false;
  const rng = new HasardPython(19); const nb = pool.length;
  let pc = 0, ps = 0;
  for (let n = 0; n < replays; n++) {
    let p = t.entree, issue = null;
    for (let i = k + 1; i <= fin && !issue; i++) {
      const j = Math.min(nb - 1, Math.max(1, i + rng.entier(-2, 2)));
      if (!pool[j] || !pool[j].length) continue;
      const [, h, l, c] = rng.choix(pool[j]);
      if (p * l <= t.stop) issue = "s"; else if (p * h >= t.cible) issue = "c";
      p *= c;
    }
    if (issue === "c") pc++; else if (issue === "s") ps++;
  }
  if (pc + ps === 0) return false;
  const R = (t.cible - t.entree) / (t.entree - t.stop);
  return pc / (pc + ps) > 1 / (1 + R);
}

// Construit le réservoir de la Time Machine depuis des séances complètes : pool[i] = [[o,h,l,c] relatifs]
export function construirePool(seances) {
  const nb = 78; const pool = Array.from({ length: nb }, () => []);
  for (const D of seances) for (let i = 1; i < nb; i++) { const pc = D[i - 1].c; pool[i].push([D[i].o / pc, D[i].h / pc, D[i].l / pc, D[i].c / pc]); }
  return pool;
}

export function figureALaCloture(cloturesJusqua) {
  if (cloturesJusqua.length < 30) return false;
  return figures(cloturesJusqua).tags.length > 0;
}
