// « Une ligne par action, avec sa meilleure stratégie » (Pitch 10.11).
// Pour chacune des 100 actions : toutes les stratégies testées (les ~1 950 combinaisons + les 158 règles leurs/nôtres)
// sont comparées SUR CETTE ACTION SEULE. Meilleure = le plus gros gain total sur l'année parmi celles qui gagnent
// à la fois sur A et sur B (au moins 3 trades sur chaque période). Sinon : la meilleure tout court, marquée « ne tient pas ».
import { graphique, parLots } from "./donnees.js";
import { local, marcheDe } from "./temps.js";
import { barresJour, qqqJour, datesBonsResultats, REGLES_J } from "./labo.js";
import { accumulerAction, nomRegle, issue } from "./combos.js";
import { REGLES } from "./regles.js";
import { lireEtat, ecrireEtat } from "./test.js";

export const SCHEMA_PA = "CREATE TABLE IF NOT EXISTS par_action (sym TEXT PRIMARY KEY, groupe TEXT, regle TEXT, nom TEXT, tient INTEGER, an INTEGER, ag INTEGER, ga REAL, bn INTEGER, bg INTEGER, gb REAL, xqqq REAL, candidats INTEGER, deuxieme TEXT, maj TEXT, garder REAL, edge REAL)";
const NOMS = Object.fromEntries([...REGLES, ...REGLES_J].map((r) => [r.id, `${r.base.nom} ${r.filtre.id === "aucun" ? "" : r.filtre.nom}`.trim()]));
const nom = (id) => NOMS[id] || nomRegle(id);

export async function demarrerPA(env) {
  const t = await lireEtat(env.DB, "test"); if (!t || !t.fini) return "test pas fini";
  await env.DB.prepare("DROP TABLE IF EXISTS par_action").run(); await env.DB.prepare(SCHEMA_PA).run();
  const e = { liste: t.liste, grosses: t.grosses, volatiles: t.volatiles, coupureJ: t.coupureJ, pos: 0, fini: false, debut: new Date().toISOString() };
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
  const st = []; const maj = new Date().toISOString();
  await parLots(lot, 4, async (sym) => {
    // candidats = combinaisons recalculées pour cette action + règles déjà testées (table bt)
    const J = barresJour(await graphique(sym, "1y", "1d"), aujNY);
    let resultats = new Set();
    if (ua && ciks[sym]) { try { for (const dd of [...(await datesBonsResultats(ciks[sym], ua))].sort()) { const x = J.find((b) => b.d >= dd); if (x) resultats.add(x.d); } } catch (x) {} }
    const acc = {}; accumulerAction(J, { qqq: qqqJ, qqqBarres, grosse: grosses.has(sym), volatile: volatiles.has(sym), resultats }, qqqJ, e.coupureJ, acc);
    const c = {};
    for (const [k, v] of Object.entries(acc)) { const [regle, per] = k.split("|"); (c[regle] = c[regle] || {})[per] = { n: v[0], g: v[1], s: v[2], x: v[4] }; }
    for (const r of (await db.prepare("SELECT regle, per, n, g, spct FROM bt WHERE sym = ?").bind(sym).all()).results) (c[r.regle] = c[r.regle] || {})[r.per] = { n: r.n, g: r.g, s: r.spct, x: null };
    // Pitch 10.11 : on retire les stratégies « toujours vraies » pour une action (grosse seule, volatile seule) = garder l'action en permanence
    for (const k of Object.keys(c)) if (/^\d+j:(grosse|volatile)$/.test(k)) delete c[k];
    // Référence : acheter cette action un jour AU HASARD et la garder h jours (même stop, même exécution) -> gain moyen par trade
    const base = {};
    const moyBase = (h, per) => {
      const k = h + per; if (base[k] !== undefined) return base[k];
      let s = 0, n = 0;
      for (let t = 50; t < J.length - 1; t++) { const p = J[t + 1].d < e.coupureJ ? "A" : "B"; if (p !== per) continue; const r = issue(J, t, h); if (r) { s += r.pct; n++; } }
      return (base[k] = n ? s / n : null);
    };
    const dureeDe = (id) => { const m = /^(\d+)j:/.exec(id) || /-(\d+)j(?::|$)/.exec(id); return m ? +m[1] : null; };
    const liste = Object.entries(c).map(([regle, p]) => ({ regle, A: p.A || { n: 0, g: 0, s: 0, x: null }, B: p.B || { n: 0, g: 0, s: 0, x: null } }))
      .map((r) => ({ ...r, tot: r.A.s + r.B.s, tient: r.A.n >= 3 && r.B.n >= 3 && r.A.s > 0 && r.B.s > 0 }));
    const ok = liste.filter((r) => r.tient).sort((a, b) => b.tot - a.tot);
    const pool = ok.length ? ok : liste.filter((r) => r.A.n + r.B.n >= 5).sort((a, b) => b.tot - a.tot);
    const m = pool[0];
    const groupe = grosses.has(sym) ? "25 plus grosses" : "75 plus volatiles";
    if (!m) { st.push(db.prepare("INSERT OR REPLACE INTO par_action (sym, groupe, candidats, maj) VALUES (?,?,?,?)").bind(sym, groupe, liste.length, maj)); return; }
    const xq = m.A.x != null && m.B.x != null ? Math.round((m.A.x + m.B.x) * 1000) : null;
    const h = dureeDe(m.regle);
    const edge = h ? Math.round(["A", "B"].reduce((a, per) => { const b = moyBase(h, per); return b == null ? a : a + (m[per].s - b * m[per].n); }, 0) * 1000) : null;
    const garder = J.length > 52 ? +(100 * (J[J.length - 1].c / J[51].o - 1)).toFixed(1) : null;
    st.push(db.prepare("INSERT OR REPLACE INTO par_action VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)").bind(sym, groupe, m.regle, nom(m.regle), ok.length ? 1 : 0,
      m.A.n, m.A.g, Math.round(m.A.s * 1000), m.B.n, m.B.g, Math.round(m.B.s * 1000), xq, liste.length, pool[1] ? `${pool[1].regle} (${Math.round(pool[1].tot * 1000)} $)` : null, maj, garder, edge));
  });
  for (let i = 0; i < st.length; i += 100) await db.batch(st.slice(i, i + 100));
  e.pos += lot.length; e.verrou = null; if (e.pos >= e.liste.length) { e.fini = true; e.finLe = new Date().toISOString(); }
  await ecrireEtat(db, "paraction", e); return { pos: e.pos, total: e.liste.length };
}

export async function lirePA(db) {
  await db.prepare(SCHEMA_PA).run();
  const e = await lireEtat(db, "paraction"); const t = await lireEtat(db, "test");
  const l = (await db.prepare("SELECT * FROM par_action ORDER BY tient DESC, (COALESCE(ga,0) + COALESCE(gb,0)) DESC").all()).results;
  return { etat: e && { pos: e.pos, total: e.liste.length, fini: e.fini, finLe: e.finLe }, periodes: t && { premiereJ: t.premiereJ, coupureJ: t.coupureJ, derniereJ: t.derniereJ, premiere: t.premiere, coupure: t.coupure, derniere: t.derniere }, lignes: l };
}
