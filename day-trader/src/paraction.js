// « Une ligne par action, avec sa meilleure stratégie » — À CAPITAL ÉGAL (Pitch 10.11).
// Mesure unique : 1 000 $ par action, UNE seule position à la fois (signal ignoré tant qu'on est investi).
// Comparé à 1 000 $ achetés et gardés dans l'action, et à 1 000 $ achetés et gardés dans le QQQ, même période.
// Meilleure = plus gros gain total parmi celles qui gagnent sur A ET sur B (au moins 3 trades sur chacune).
// Barres journalières sur 1 an (les règles intraday, 60 jours seulement, ne sont pas comparables ici).
import { graphique, parLots } from "./donnees.js";
import { local, marcheDe } from "./temps.js";
import { barresJour, qqqJour, datesBonsResultats, REGLES_J, strategiesJour } from "./labo.js";
import { nomRegle, issue, conditionsDuJour, COMBOS_OK, DUREES, idCombo } from "./combos.js";
import { lireEtat, ecrireEtat } from "./test.js";

export const SCHEMA_PA = "CREATE TABLE IF NOT EXISTS par_action (sym TEXT PRIMARY KEY, groupe TEXT, regle TEXT, nom TEXT, tient INTEGER, an INTEGER, ga REAL, bn INTEGER, gb REAL, strat REAL, garder REAL, qqq REAL, garder_a REAL, garder_b REAL, qqq_a REAL, qqq_b REAL, du TEXT, coupure TEXT, au TEXT, candidats INTEGER, maj TEXT)";
export const SCHEMA_CAP = "CREATE TABLE IF NOT EXISTS bt_cap (regle TEXT, per TEXT, n INTEGER, g INTEGER, s REAL, actions INTEGER, PRIMARY KEY (regle, per))";
export const SCHEMA_BENCH = "CREATE TABLE IF NOT EXISTS bt_bench (sym TEXT PRIMARY KEY, garder_a REAL, garder_b REAL, qqq_a REAL, qqq_b REAL)";
const NOMS = Object.fromEntries(REGLES_J.map((r) => [r.id, `${r.base.nom} ${r.filtre.id === "aucun" ? "" : r.filtre.nom}`.trim()]));
export const nom = (id) => NOMS[id] || nomRegle(id);
const TOUJOURS = /^\d+j:(grosse|volatile)$/; // toujours vraies pour une action = garder l'action en permanence

// Toutes les stratégies d'une action, à capital égal : { regle: { A: {n,g,s}, B: {n,g,s} } } (s = fraction de 1 000 $)
export function capitalEgal(J, ctx, coupure) {
  const masques = J.map((_, t) => (t >= 50 && t < J.length - 1 ? conditionsDuJour(J, t, ctx) : 0));
  const iss = {}; for (const h of DUREES) iss[h] = J.map((_, t) => (masques[t] ? issue(J, t, h) : null));
  const out = {};
  const ajoute = (regle, d, pct) => { const o = (out[regle] = out[regle] || { A: { n: 0, g: 0, s: 0 }, B: { n: 0, g: 0, s: 0 } })[d < coupure ? "A" : "B"]; o.n++; if (pct > 0) o.g++; o.s += pct; };
  for (const c of COMBOS_OK) {
    const mk = c.reduce((a, i) => a | (1 << i), 0);
    for (const h of DUREES) {
      const id = idCombo(c, h); if (TOUJOURS.test(id)) continue;
      let libre = -1;
      for (let t = 50; t < J.length - 1; t++) {
        if (t <= libre || (masques[t] & mk) !== mk) continue;
        const r = iss[h][t]; if (!r) continue;
        ajoute(id, J[t + 1].d, r.pct); libre = r.fin;
      }
    }
  }
  // leurs règles journalières (déjà une position à la fois) ; « mise ×2 » exclue : pas de sens à capital égal
  for (const x of strategiesJour(J, { qqq: ctx.qqq, liquide: ctx.grosse, resultats: ctx.resultats })) if (!x.rid.endsWith(":x2")) ajoute(x.rid, x.d, x.pct);
  return out;
}

// Garder 1 000 $ : rendement sur A, sur B et sur toute la période
function garderAB(B, du, coupure, au) {
  const i0 = B.findIndex((x) => x.d >= du), iC = B.findIndex((x) => x.d >= coupure);
  let iF = B.length - 1; while (iF > 0 && B[iF].d > au) iF--;
  if (i0 < 0 || iC <= i0 || iF < iC) return null;
  return { a: B[iC - 1].c / B[i0].o - 1, b: B[iF].c / B[iC].o - 1, tout: B[iF].c / B[i0].o - 1 };
}

export async function demarrerPA(env) {
  const t = await lireEtat(env.DB, "test"); if (!t || !t.fini) return "test pas fini";
  for (const x of ["par_action", "bt_cap", "bt_bench"]) await env.DB.prepare(`DROP TABLE IF EXISTS ${x}`).run();
  for (const s of [SCHEMA_PA, SCHEMA_CAP, SCHEMA_BENCH]) await env.DB.prepare(s).run();
  const e = { liste: t.liste, grosses: t.grosses, volatiles: t.volatiles, coupureJ: t.coupureJ, pos: 0, fini: false, debut: new Date().toISOString(), mesure: "capital égal" };
  await ecrireEtat(env.DB, "paraction", e); return e;
}

export async function lotPA(env, taille = 10) {
  const db = env.DB; const e = await lireEtat(db, "paraction");
  if (!e || e.fini) return e;
  if (e.verrou && Date.now() - e.verrou < 240e3) return { occupe: true };
  e.verrou = Date.now(); await ecrireEtat(db, "paraction", e);
  const lot = e.liste.slice(e.pos, e.pos + taille);
  const aujNY = local(Date.now(), marcheDe("QQQ")).date;
  const qqqBarres = barresJour(await graphique("QQQ", "1y", "1d"), aujNY); const qqqJ = qqqJour(qqqBarres);
  const uaL = await db.prepare("SELECT valeur FROM config WHERE cle = 'contact_sec'").first(); const ua = uaL ? uaL.valeur : "";
  let ciks = {}; if (ua) { try { const j = await (await fetch("https://www.sec.gov/files/company_tickers.json", { headers: { "User-Agent": ua } })).json(); for (const v of Object.values(j)) ciks[String(v.ticker).toUpperCase()] = String(v.cik_str).padStart(10, "0"); } catch (x) {} }
  const grosses = new Set(e.grosses || []), volatiles = new Set(e.volatiles || []);
  const st = []; const maj = new Date().toISOString(); const agg = {};
  await parLots(lot, 4, async (sym) => {
    const J = barresJour(await graphique(sym, "1y", "1d"), aujNY); if (J.length < 80) return;
    let resultats = new Set();
    if (ua && ciks[sym]) { try { for (const dd of [...(await datesBonsResultats(ciks[sym], ua))].sort()) { const x = J.find((b) => b.d >= dd); if (x) resultats.add(x.d); } } catch (x) {} }
    const ctx = { qqq: qqqJ, grosse: grosses.has(sym), volatile: volatiles.has(sym), resultats };
    const c = capitalEgal(J, ctx, e.coupureJ);
    for (const [regle, p] of Object.entries(c)) for (const per of ["A", "B"]) {
      if (!p[per].n) continue; const a = (agg[regle + "|" + per] = agg[regle + "|" + per] || [0, 0, 0, 0]);
      a[0] += p[per].n; a[1] += p[per].g; a[2] += p[per].s; a[3]++;
    }
    const du = J[51].d, au = J[J.length - 1].d;
    const gA = garderAB(J, du, e.coupureJ, au), qA = garderAB(qqqBarres, du, e.coupureJ, au);
    if (gA && qA) st.push(db.prepare("INSERT OR REPLACE INTO bt_bench VALUES (?,?,?,?,?)").bind(sym, gA.a, gA.b, qA.a, qA.b));
    const liste = Object.entries(c).map(([regle, p]) => ({ regle, ...p, tot: p.A.s + p.B.s, tient: p.A.n >= 3 && p.B.n >= 3 && p.A.s > 0 && p.B.s > 0 }));
    const ok = liste.filter((r) => r.tient).sort((a, b) => b.tot - a.tot);
    const m = ok[0] || liste.filter((r) => r.A.n + r.B.n >= 5).sort((a, b) => b.tot - a.tot)[0];
    const groupe = grosses.has(sym) ? "25 plus grosses" : "75 plus volatiles";
    const r$ = (x) => (x == null ? null : Math.round(x * 1000));
    st.push(db.prepare("INSERT OR REPLACE INTO par_action VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)").bind(sym, groupe, m ? m.regle : null, m ? nom(m.regle) : null, m && ok.length ? 1 : 0,
      m ? m.A.n : 0, m ? r$(m.A.s) : null, m ? m.B.n : 0, m ? r$(m.B.s) : null, m ? r$(m.tot) : null,
      gA ? r$(gA.tout) : null, qA ? r$(qA.tout) : null, gA ? r$(gA.a) : null, gA ? r$(gA.b) : null, qA ? r$(qA.a) : null, qA ? r$(qA.b) : null, du, e.coupureJ, au, liste.length, maj));
  });
  for (const [k, v] of Object.entries(agg)) { const [regle, per] = k.split("|"); st.push(db.prepare("INSERT INTO bt_cap VALUES (?,?,?,?,?,?) ON CONFLICT (regle, per) DO UPDATE SET n = n + excluded.n, g = g + excluded.g, s = s + excluded.s, actions = actions + excluded.actions").bind(regle, per, ...v)); }
  for (let i = 0; i < st.length; i += 400) await db.batch(st.slice(i, i + 400));
  e.pos += lot.length; e.verrou = null; if (e.pos >= e.liste.length) { e.fini = true; e.finLe = new Date().toISOString(); }
  await ecrireEtat(db, "paraction", e); return { pos: e.pos, total: e.liste.length };
}

export async function lirePA(db) {
  for (const s of [SCHEMA_PA, SCHEMA_CAP, SCHEMA_BENCH]) await db.prepare(s).run();
  const e = await lireEtat(db, "paraction");
  const l = (await db.prepare("SELECT * FROM par_action").all()).results.map((x) => ({ ...x, mieux: x.strat != null && x.garder != null && x.qqq != null ? x.strat - Math.max(x.garder, x.qqq) : null }));
  l.sort((a, b) => (b.mieux ?? -1e9) - (a.mieux ?? -1e9));
  return { etat: e && { pos: e.pos, total: e.liste.length, fini: e.fini, finLe: e.finLe, mesure: e.mesure }, lignes: l };
}

// Classement global à capital égal : 1 000 $ par action (100 actions = 100 000 $), une position à la fois par action.
// Comparé à 100 000 $ gardés dans les mêmes actions, et à 100 000 $ gardés dans le QQQ, sur A et sur B.
export async function classementCap(db, tous = false) {
  for (const s of [SCHEMA_CAP, SCHEMA_BENCH]) await db.prepare(s).run();
  const b = (await db.prepare("SELECT COUNT(*) n, SUM(garder_a) ga, SUM(garder_b) gb, SUM(qqq_a) qa, SUM(qqq_b) qb FROM bt_bench").first()) || {};
  const bench = { actions: b.n || 0, capital: (b.n || 0) * 1000, garderA: Math.round((b.ga || 0) * 1000), garderB: Math.round((b.gb || 0) * 1000), qqqA: Math.round((b.qa || 0) * 1000), qqqB: Math.round((b.qb || 0) * 1000) };
  const m = {};
  for (const x of (await db.prepare("SELECT * FROM bt_cap").all()).results) (m[x.regle] = m[x.regle] || { regle: x.regle, nom: nom(x.regle) })[x.per] = { trades: x.n, gagnants: +(100 * x.g / x.n).toFixed(1), gain: Math.round(x.s * 1000), actions: x.actions };
  const toutes = Object.values(m).filter((r) => r.A && r.B && r.A.trades >= 30 && r.B.trades >= 30);
  for (const r of toutes) {
    r.batQqq = r.A.gain > bench.qqqA && r.B.gain > bench.qqqB;
    r.batGarder = r.A.gain > bench.garderA && r.B.gain > bench.garderB;
    r.tient = r.A.gain > 0 && r.B.gain > 0 && r.batQqq;
  }
  toutes.sort((a, b) => (b.tient - a.tient) || (b.A.gain + b.B.gain - a.A.gain - a.B.gain));
  return { bench, total: toutes.length, tiennent: toutes.filter((r) => r.tient).length, battentAussiGarder: toutes.filter((r) => r.tient && r.batGarder).length, top: toutes.filter((r) => r.tient), regles: tous ? toutes : toutes.slice(0, 80) };
}
