// Règles de trading testées : « leurs » (ORB du dépôt d'origine) et « nos » filtres tirés de Bot95.
// UNE seule fonction simule un trade sur une séance : le test historique et le paper l'utilisent
// toutes les deux, donc le paper ne peut pas diverger du test.
import { estBtc } from "./temps.js";
import { figures } from "./scanner.js";

export const BASES = [
  { id: "mid1", stop: "mid", R: 1, nom: "stop milieu du range, cible 1R" },
  { id: "mid2", stop: "mid", R: 2, nom: "stop milieu du range, cible 2R" },
  { id: "midF", stop: "mid", R: null, nom: "stop milieu du range, sortie en fin de séance" },
  { id: "low1", stop: "low", R: 1, nom: "stop bas du range, cible 1R" },
  { id: "low2", stop: "low", R: 2, nom: "stop bas du range, cible 2R" },
  { id: "lowF", stop: "low", R: null, nom: "stop bas du range, sortie en fin de séance" },
];
// « aucun » = leur règle telle quelle. Les autres = nos filtres (leçons Bot95).
export const FILTRES = [
  { id: "aucun", camp: "leur", nom: "ORB seul (leur règle)" },
  { id: "heure", camp: "nous", nom: "bonnes heures (Bot95 : actions avant 11 h NY ; BTC 10 h–18 h suisses)" },
  { id: "volume", camp: "nous", nom: "volume : barre de cassure ≥ 1,5 × la moyenne" },
  { id: "marche", camp: "nous", nom: "élan du marché : QQQ au-dessus de son ouverture (Bot95 : élan du perp)" },
  { id: "vwap", camp: "nous", nom: "prix au-dessus du VWAP de la séance" },
  { id: "figure", camp: "nous", nom: "figure journalière la veille (scanner)" },
  { id: "consensus", camp: "nous", nom: "consensus : au moins 3 des 5 filtres d'accord (Bot95 : consensus des stratégies)" },
  { id: "tout", camp: "nous", nom: "volume + marché + VWAP ensemble" },
];
export const REGLES = BASES.flatMap((b) => FILTRES.map((f) => ({ id: `${b.id}-${f.id}`, base: b, filtre: f })));
export const REGLE = Object.fromEntries(REGLES.map((r) => [r.id, r]));

export const GLISSEMENT = 0.0005;          // 0,05 % payé à l'entrée et sur un stop (estimation prudente)
export const FRAIS_BTC = 0.001;            // 0,1 % par côté sur le BTC (frais preneur courants)
const sousCentime = (x) => Math.floor(Math.round(x * 1e6) / 1e4) / 100;

// Contexte d'une séance : barres (indexées par créneau), QQQ (même créneaux), figure de la veille.
// Renvoie, pour chaque règle demandée, le trade (ou null) simulé avec une exécution réaliste.
export function simulerSeance(sym, D, { qqq = null, figureVeille = false, nRange = 3, dernierePossible = null, finIndex = null } = {}, regles = REGLES) {
  const btc = estBtc(sym);
  const n = D.length; if (n <= nRange + 1) return {};
  if (D.slice(0, nRange).some((b) => !b)) return {};
  const oh = Math.max(...D.slice(0, nRange).map((b) => b.h)), ol = Math.min(...D.slice(0, nRange).map((b) => b.l));
  const fin = finIndex != null ? Math.min(finIndex, n - 1) : n - 1;          // dernière barre de la séance (sortie forcée)
  const derniere = dernierePossible != null ? dernierePossible : fin - 1;    // dernière barre où un signal peut tomber
  // VWAP et volume moyen cumulés
  let pv = 0, vv = 0; const vwap = [], volMoy = [];
  let sv = 0;
  for (let i = 0; i < n; i++) { const b = D[i]; if (!b) { vwap.push(null); volMoy.push(null); continue; } pv += ((b.h + b.l + b.c) / 3) * (b.v || 0); vv += b.v || 0; vwap.push(vv ? pv / vv : b.c); volMoy.push(i ? sv / i : null); sv += b.v || 0; }
  // premier signal par filtre
  const premier = {};
  for (let k = nRange; k <= Math.min(derniere, n - 2); k++) {
    const b = D[k]; if (!b || !D[k + 1]) continue;
    if (!(b.c > oh)) continue;
    if (!btc && (b.min + 5 < 9 * 60 + 45 || b.min + 5 > 15 * 60 + 30)) continue; // fenêtre d'entrée du dépôt d'origine
    const f = {
      heure: btc ? (b.min >= 9 * 60 && b.min < 17 * 60) : b.min + 5 <= 11 * 60,
      volume: volMoy[k] ? (b.v || 0) >= 1.5 * volMoy[k] : false,
      marche: btc ? true : !!(qqq && qqq[k] && qqq[0] && qqq[k].c > qqq[0].o),
      vwap: vwap[k] != null && b.c > vwap[k],
      figure: !!figureVeille,
    };
    f.consensus = [f.heure, f.volume, f.marche, f.vwap, f.figure].filter(Boolean).length >= 3;
    f.tout = f.volume && f.marche && f.vwap;
    f.aucun = true;
    for (const id of Object.keys(f)) if (f[id] && premier[id] == null) premier[id] = k;
  }
  const out = {};
  for (const r of regles) {
    const k = premier[r.filtre.id]; if (k == null) continue;
    out[r.id] = executer(D, k, r.base, { oh, ol, fin, btc });
  }
  return out;
}

export function executer(D, k, base, { oh, ol, fin, btc }) {
  const frais = btc ? FRAIS_BTC : 0;
  const e0 = D[k + 1].o;
  const entree = e0 * (1 + GLISSEMENT);
  const stop = sousCentime(base.stop === "mid" ? (oh + ol) / 2 : ol);
  if (!(entree > stop)) return { k, statut: "annule", raison: "ouverture déjà sous le stop" };
  const risque = entree - stop;
  const cible = base.R ? Math.round((entree + base.R * risque) * 100) / 100 : null;
  let sortie = null, issue = null, j = k + 1;
  for (; j <= fin; j++) {
    const b = D[j]; if (!b) continue;
    if (j > k + 1 && b.o <= stop) { sortie = b.o * (1 - GLISSEMENT); issue = "stop"; break; }       // gap sous le stop
    if (cible && j > k + 1 && b.o >= cible) { sortie = b.o; issue = "cible"; break; }               // gap au-dessus de la cible
    if (b.l <= stop) { sortie = stop * (1 - GLISSEMENT); issue = "stop"; break; }                  // stop d'abord si les deux
    if (cible && b.h >= cible) { sortie = cible; issue = "cible"; break; }
  }
  let ouvert = false;
  if (sortie == null) {
    const der = D[Math.min(fin, D.length - 1)];
    if (D.length - 1 < fin) { ouvert = true; j = D.length - 1; sortie = D[j].c; issue = "en cours"; }
    else { j = fin; sortie = der.c; issue = "fin de séance"; }
  }
  const pct = (sortie * (1 - frais) - entree * (1 + frais)) / entree;
  return { k, j, statut: ouvert ? "ouvert" : "ferme", entree: +entree.toFixed(4), stop, cible, sortie: +sortie.toFixed(4), issue, pct, R: (sortie - entree) / risque };
}

// Figure journalière à la clôture d'un jour donné (clôtures jusqu'à ce jour inclus)
export function figureALaCloture(cloturesJusqua) {
  if (cloturesJusqua.length < 30) return false;
  return figures(cloturesJusqua).tags.length > 0;
}
