// Paper automatique : toutes les 5 minutes, les 48 règles tournent sur les actions les plus échangées + BTC.
// Même fonction de simulation que le banc d'essai : le paper ne peut pas diverger du test.
import { graphique, barres, parLots } from "./donnees.js";
import { local, seance, marcheDe, estBtc, hhmm, MARCHES, NYSE_FERMETURE_13H } from "./temps.js";
import { REGLES, simulerSeance, construirePool } from "./regles.js";
import { seancesCompletes } from "./test.js";

export async function tourPapier(env, univers, figuresVeille, maintenantMs = Date.now(), grosses = new Set()) {
  const lA = local(maintenantMs, MARCHES.actions); const seA = seance(lA.date, MARCHES.actions);
  const actionsActives = seA && lA.min >= seA[0] + 20 && lA.min <= seA[1] + 15;
  const syms = actionsActives ? univers.filter((x) => x !== "BTC") : []; // BTC retiré (Pitch 10.11 : un autre bot s'en occupe)
  if (!syms.length) return { symboles: 0, lignes: 0 };
  const qqq = actionsActives ? jourIndexe(await graphique("QQQ", "1d", "5m"), "QQQ", lA.date) : null;
  const st = []; const maj = new Date(maintenantMs).toISOString();
  const taches = syms.map((x) => [x, local(maintenantMs, marcheDe(x)).date]);
  await parLots(taches, 8, async ([sym, date]) => {
    const m = marcheDe(sym); const l = { date };
    const s60 = await graphique(sym, "60d", "5m");
    const D = jourIndexe(s60, sym, l.date);
    if (!D.length) return;
    const avant = seancesCompletes(s60, sym).filter(([d]) => d < l.date);
    const pool = avant.length >= 20 ? construirePool(avant.slice(-40).map((x) => x[1])) : null;
    const veille = avant.length ? avant[avant.length - 1][1] : null;
    const hautVeille = veille ? Math.max(...veille.map((b) => b.h)) : null;
    const se = seance(l.date, m);
    const fin = estBtc(sym) ? 287 : (se[1] - 5 - se[0]) / 5 - 1; // sortie à 15 h 55 (12 h 55 les jours courts)
    const t = simulerSeance(sym, D, { qqq, figureVeille: figuresVeille.has(sym), hautVeille, liquide: grosses.has(sym), pool, nRange: 3, finIndex: fin, dernierePossible: estBtc(sym) ? fin - 1 : (NYSE_FERMETURE_13H[l.date] ? 35 : 72) });
    for (const [rid, tr] of Object.entries(t)) {
      if (!tr || tr.statut === "annule") continue;
      const hE = hhmm(se[0] + 5 * (tr.k + 1)); const hS = tr.statut === "ferme" ? hhmm(se[0] + 5 * tr.j + (tr.issue === "fin de séance" ? 5 : 0)) : null;
      st.push(env.DB.prepare("INSERT OR REPLACE INTO papier VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)").bind(l.date, rid, sym, tr.statut, hE, tr.entree, tr.stop, tr.cible, hS, tr.sortie, tr.issue, tr.pct, tr.R, maj));
    }
  });
  for (let i = 0; i < st.length; i += 400) await env.DB.batch(st.slice(i, i + 400));
  return { symboles: syms.length, lignes: st.length };
}

// Barres du jour indexées par créneau (trous = undefined)
function jourIndexe(s, sym, date) {
  const D = [];
  for (const b of barres(s, sym, Date.now())) if (b.date === date) D[b.slot] = b;
  return D;
}

export async function resume(db, { mise = 1000, depuis = "" } = {}) {
  const lignes = (await db.prepare("SELECT * FROM papier WHERE date >= ? ORDER BY date, regle").bind(depuis || "0000").all()).results;
  const parRegle = {};
  for (const x of lignes) {
    const r = (parRegle[x.regle] = parRegle[x.regle] || { regle: x.regle, trades: 0, gagnants: 0, ouverts: 0, gain: 0, gainJour: 0, jours: {}, parAction: {} });
    const a = (r.parAction[x.sym] = r.parAction[x.sym] || { sym: x.sym, gain: 0, trades: 0, ouvert: false });
    a.gain += x.pct * mise; a.trades++; if (x.statut === "ouvert") a.ouvert = true;
    r.trades++; if (x.pct > 0) r.gagnants++; if (x.statut === "ouvert") r.ouverts++;
    r.gain += x.pct * mise; r.jours[x.date] = (r.jours[x.date] || 0) + x.pct * mise;
  }
  const auj = lignes.length ? lignes[lignes.length - 1].date : null;
  for (const r of Object.values(parRegle)) {
    let c = 0, pic = 0, pire = 0;
    for (const d of Object.keys(r.jours).sort()) { c += r.jours[d]; pic = Math.max(pic, c); pire = Math.min(pire, c - pic); }
    r.creux = Math.round(pire); r.gain = Math.round(r.gain); r.gainJour = Math.round(r.jours[auj] || 0); r.nbJours = Object.keys(r.jours).length; delete r.jours;
    r.actions = Object.values(r.parAction).map((a) => ({ ...a, gain: Math.round(a.gain) })).sort((a, b) => b.gain - a.gain); delete r.parAction;
  }
  return { mise, depuis: lignes.length ? lignes[0].date : null, jusqua: auj, regles: Object.values(parRegle).sort((a, b) => b.gain - a.gain) };
}

export async function tradesPapier(db, { regle = "", date = "" } = {}, mise = 1000) {
  const q = (await db.prepare("SELECT * FROM papier WHERE (? = '' OR regle = ?) AND (? = '' OR date = ?) ORDER BY date DESC, entree_h DESC LIMIT 500").bind(regle, regle, date, date).all()).results;
  return q.map((x) => ({ ...x, gain: Math.round(x.pct * mise * 100) / 100 }));
}
