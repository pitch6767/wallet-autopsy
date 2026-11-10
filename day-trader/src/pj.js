// Paper JOURNALIER : chaque soir après la clôture de New York, les combinaisons qui « tiennent » (A, B, battent le QQQ,
// t ≥ 2) cherchent leurs signaux sur les 100 actions ; achat papier à l'ouverture du lendemain, stop 2 × ATR, sortie après N jours.
// La liste des combinaisons est figée au premier soir (pas de triche : on ne la change pas après coup).
import { graphique, parLots } from "./donnees.js";
import { local, seance, MARCHES } from "./temps.js";
import { barresJour, qqqJour, datesBonsResultats } from "./labo.js";
import { conditionsDuJour, CONDITIONS } from "./combos.js";
import { classementCap } from "./paraction.js";
import { GLISSEMENT } from "./regles.js";
import { lireEtat, ecrireEtat } from "./test.js";

const BIT = Object.fromEntries(CONDITIONS.map((k, i) => [k.id, 1 << i]));
const masqueRegle = (id) => id.split(":")[1].split("+").reduce((m, x) => m | BIT[x], 0);

function suivre(J, t0, h) {
  if (!J[t0 + 1]) return { statut: "attente" };
  const a = (() => { let s = 0; for (let i = t0 - 13; i <= t0; i++) s += Math.max(J[i].h - J[i].l, Math.abs(J[i].h - J[i - 1].c), Math.abs(J[i].l - J[i - 1].c)); return s / 14; })();
  const entree = J[t0 + 1].o * (1 + GLISSEMENT), stop = entree - 2 * a;
  for (let j = t0 + 1; j <= Math.min(t0 + h, J.length - 1); j++) {
    const b = J[j];
    if (j > t0 + 1 && b.o <= stop) return { statut: "ferme", entree, stop, j, sortie: b.o * (1 - GLISSEMENT), issue: "stop (gap)" };
    if (b.l <= stop) return { statut: "ferme", entree, stop, j, sortie: stop * (1 - GLISSEMENT), issue: "stop" };
  }
  if (t0 + h <= J.length - 1) return { statut: "ferme", entree, stop, j: t0 + h, sortie: J[t0 + h].c * (1 - GLISSEMENT / 2), issue: `${h} jour(s) écoulé(s)` };
  const der = J.length - 1; return { statut: "ouvert", entree, stop, j: der, sortie: J[der].c, issue: "en cours" };
}

export async function tourPapierJour(env, maintenantMs = Date.now()) {
  const db = env.DB;
  const etat = await lireEtat(db, "test"); if (!etat || !etat.fini) return "test pas fini";
  const pa = await lireEtat(db, "paraction"); if (!pa || !pa.fini || pa.mesure !== "capital égal") return "classement à capital égal pas fini";
  let g = await lireEtat(db, "gagnants_papier");
  // figée une fois, depuis le classement À CAPITAL ÉGAL (combinaisons qui gagnent sur A et B et battent le QQQ avec le même capital)
  if (!g) { const c = await classementCap(db); g = { le: new Date().toISOString(), mesure: "capital égal", regles: c.top.map((r) => r.regle).filter((id) => /^\d+j:/.test(id)) }; await ecrireEtat(db, "gagnants_papier", g); }
  if (!g.regles.length) return "aucune combinaison ne tient";
  const l = local(maintenantMs, MARCHES.actions); const se = seance(l.date, MARCHES.actions);
  const coupe = se && l.min >= se[1] + 5 ? "9999" : l.date; // après la clôture, la journée du jour compte
  const qqqBarres = barresJour(await graphique("QQQ", "1y", "1d"), coupe); const qqqJ = qqqJour(qqqBarres);
  const qIdx = Object.fromEntries(qqqBarres.map((x, i) => [x.d, i]));
  const uaL = await db.prepare("SELECT valeur FROM config WHERE cle = 'contact_sec'").first(); const ua = uaL ? uaL.valeur : "";
  let ciks = {}; if (ua) { try { const j = await (await fetch("https://www.sec.gov/files/company_tickers.json", { headers: { "User-Agent": ua } })).json(); for (const v of Object.values(j)) ciks[String(v.ticker).toUpperCase()] = String(v.cik_str).padStart(10, "0"); } catch (e) {} }
  const ouverts = (await db.prepare("SELECT * FROM papier_j WHERE statut != 'ferme'").all()).results;
  const grosses = new Set(etat.grosses || []), volatiles = new Set(etat.volatiles || []);
  const st = []; const maj = new Date(maintenantMs).toISOString(); let nouveaux = 0;
  await parLots(etat.liste, 4, async (sym) => {
    const J = barresJour(await graphique(sym, "1y", "1d"), coupe); if (J.length < 60) return;
    const idx = Object.fromEntries(J.map((x, i) => [x.d, i]));
    let resultats = new Set();
    if (ua && ciks[sym]) { try { for (const dd of [...(await datesBonsResultats(ciks[sym], ua))].sort()) { const x = J.find((b) => b.d >= dd); if (x) resultats.add(x.d); } } catch (e) {} }
    // 1) nouveaux signaux à la dernière clôture
    const t = J.length - 1;
    const m = conditionsDuJour(J, t, { qqq: qqqJ, grosse: grosses.has(sym), volatile: volatiles.has(sym), resultats });
    // capital égal : pas de nouveau trade pour une combinaison + action tant que le précédent n'est pas fermé
    const occupe = new Set(ouverts.filter((x) => x.sym === sym).map((x) => x.regle));
    if (m) for (const id of g.regles) { const mk = masqueRegle(id); if (!occupe.has(id) && (m & mk) === mk) { nouveaux++; st.push(db.prepare("INSERT OR IGNORE INTO papier_j (date_signal, regle, sym, h, statut, maj) VALUES (?,?,?,?,?,?)").bind(J[t].d, id, sym, +id.split("j:")[0], "attente", maj)); } }
    // 2) suivi des trades en cours
    for (const o of ouverts.filter((x) => x.sym === sym)) {
      const t0 = idx[o.date_signal]; if (t0 == null) continue;
      const r = suivre(J, t0, o.h); if (r.statut === "attente") continue;
      const qi = qIdx[J[t0 + 1].d], qf = qIdx[J[r.j].d];
      const qPct = qi != null && qf != null ? qqqBarres[qf].c / qqqBarres[qi].o - 1 : null;
      st.push(db.prepare("UPDATE papier_j SET entree_d = ?, entree = ?, stop = ?, sortie_d = ?, sortie = ?, issue = ?, pct = ?, qqq_pct = ?, statut = ?, maj = ? WHERE date_signal = ? AND regle = ? AND sym = ?")
        .bind(J[t0 + 1].d, r.entree, r.stop, J[r.j].d, r.sortie, r.issue, r.sortie / r.entree - 1, qPct, r.statut, maj, o.date_signal, o.regle, o.sym));
    }
  });
  for (let i = 0; i < st.length; i += 400) await db.batch(st.slice(i, i + 400));
  return { regles: g.regles.length, nouveaux, suivis: ouverts.length };
}

export async function resumePJ(db, mise = 1000) {
  const g = await lireEtat(db, "gagnants_papier");
  const l = (await db.prepare("SELECT * FROM papier_j ORDER BY date_signal DESC").all()).results;
  const par = {};
  for (const x of l) {
    const r = (par[x.regle] = par[x.regle] || { regle: x.regle, signaux: 0, fermes: 0, ouverts: 0, gain: 0, contreQqq: 0, gagnants: 0, parAction: {} });
    const a = (r.parAction[x.sym] = r.parAction[x.sym] || { sym: x.sym, gain: 0, trades: 0, ouvert: false, attente: false });
    a.trades++; if (x.pct != null) a.gain += x.pct * mise; if (x.statut === "ouvert") a.ouvert = true; if (x.statut === "attente") a.attente = true;
    r.signaux++; if (x.statut === "ouvert") r.ouverts++;
    if (x.pct != null) { r.gain += x.pct * mise; if (x.qqq_pct != null) r.contreQqq += (x.pct - x.qqq_pct) * mise; }
    if (x.statut === "ferme") { r.fermes++; if (x.pct > 0) r.gagnants++; }
  }
  for (const r of Object.values(par)) { r.gain = Math.round(r.gain); r.contreQqq = Math.round(r.contreQqq); r.actions = Object.values(r.parAction).map((a) => ({ ...a, gain: Math.round(a.gain) })).sort((a, b) => b.gain - a.gain); delete r.parAction; }
  return { figeeLe: g && g.le, regles: g ? g.regles : [], parRegle: Object.values(par).sort((a, b) => b.gain - a.gain), derniers: l.slice(0, 150).map((x) => ({ ...x, gain: x.pct != null ? Math.round(x.pct * mise * 100) / 100 : null })) };
}
