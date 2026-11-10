// Banc d'essai : chaque règle rejouée sur 60 jours de barres 5 min, action par action.
// Méthode Bot95 : on choisit sur la période A, on vérifie sur la période B (jamais vue au moment du choix).
import { graphique, sparkTout, barres, parLots } from "./donnees.js";
import { marcheDe, estBtc, local } from "./temps.js";
import { REGLES, simulerSeance, figureALaCloture, construirePool } from "./regles.js";
import { REGLES_J, strategiesJour, barresJour, qqqJour, datesBonsResultats } from "./labo.js";
import { cloturesJour } from "./scanner.js";

export const SCHEMA = [
  "CREATE TABLE IF NOT EXISTS bt (regle TEXT, sym TEXT, per TEXT, n INTEGER, g INTEGER, spct REAL, sr REAL, creux REAL, PRIMARY KEY (regle, sym, per))",
  "CREATE TABLE IF NOT EXISTS bt_jour (regle TEXT, date TEXT, n INTEGER, spct REAL, PRIMARY KEY (regle, date))",
  "CREATE TABLE IF NOT EXISTS etat (cle TEXT PRIMARY KEY, valeur TEXT)",
  "CREATE TABLE IF NOT EXISTS papier (date TEXT, regle TEXT, sym TEXT, statut TEXT, entree_h TEXT, entree REAL, stop REAL, cible REAL, sortie_h TEXT, sortie REAL, issue TEXT, pct REAL, r REAL, maj TEXT, PRIMARY KEY (date, regle, sym))",
  "CREATE TABLE IF NOT EXISTS news (id TEXT PRIMARY KEY, cik TEXT, sym TEXT, nom TEXT, quand INTEGER, items TEXT, lien TEXT, en_seance INTEGER, prix0 REAL, debut_suivi INTEGER, m5 REAL, m15 REAL, m60 REAL, max30 REAL, fini INTEGER DEFAULT 0, maj TEXT, source TEXT DEFAULT 'sec', titre TEXT, vu INTEGER, hl0 REAL, hl5 REAL, hl15 REAL, hl60 REAL, hlouv REAL, kf0 REAL, kf5 REAL, kf15 REAL, kf60 REAL, kfouv REAL)",
  "CREATE INDEX IF NOT EXISTS news_quand ON news (quand)",
];
export async function schema(db) { for (const s of SCHEMA) await db.prepare(s).run(); }
export async function lireEtat(db, cle) { const r = await db.prepare("SELECT valeur FROM etat WHERE cle = ?").bind(cle).first(); return r ? JSON.parse(r.valeur) : null; }
export async function ecrireEtat(db, cle, v) { await db.prepare("INSERT OR REPLACE INTO etat (cle, valeur) VALUES (?, ?)").bind(cle, JSON.stringify(v)).run(); }

// Séances complètes d'une série 5 min -> [[date, D[]]] (D indexé par créneau)
export function seancesCompletes(s, sym) {
  const m = marcheDe(sym); const nb = (m.fermeture - m.ouverture) / 5;
  const j = {};
  for (const b of barres(s, sym, Date.now())) (j[b.date] = j[b.date] || [])[b.slot] = b;
  return Object.keys(j).sort().filter((d) => j[d].length === nb && j[d].every(Boolean)).map((d) => [d, j[d]]);
}

function creux(pcts) { let c = 0, pic = 0, pire = 0; for (const p of pcts) { c += p; pic = Math.max(pic, c); pire = Math.min(pire, c - pic); } return pire; }

export const NB_GROSSES = 25, NB_VOLATILES = 75;
// Univers choisi par Pitch (10.11) : les 25 plus grosses + les plus volatiles (pas les 1 600)
export async function choisirUnivers(liquides) {
  const l = liquides.filter((x) => x !== "BTC");
  const grosses = l.slice(0, NB_GROSSES);
  const reste = l.slice(NB_GROSSES);
  const { data } = await sparkTout(reste, "3mo", "1d");
  const vol = [];
  for (const sym of reste) {
    const c = (data[sym]?.c || []).filter((x) => x != null); if (c.length < 40) continue;
    const r = []; for (let i = 1; i < c.length; i++) r.push(Math.log(c[i] / c[i - 1]));
    const m = r.reduce((a, x) => a + x, 0) / r.length; const sd = Math.sqrt(r.reduce((a, x) => a + (x - m) ** 2, 0) / r.length);
    vol.push([sym, sd]);
  }
  vol.sort((a, b) => b[1] - a[1]);
  const volatiles = vol.slice(0, NB_VOLATILES).map((x) => x[0]);
  return { grosses, volatiles, volatilite: Object.fromEntries(vol.slice(0, NB_VOLATILES).map(([s, v]) => [s, +(100 * v).toFixed(2)])) };
}

export async function demarrer(env, liquides) {
  await schema(env.DB);
  await env.DB.batch([env.DB.prepare("DELETE FROM bt"), env.DB.prepare("DELETE FROM bt_jour")]);
  const u = await choisirUnivers(liquides);
  const symboles = [...u.grosses, ...u.volatiles];
  const qJ = barresJour(await graphique("QQQ", "1y", "1d"), local(Date.now(), marcheDe("QQQ")).date).map((x) => x.d);
  // coupure A/B : milieu des séances de QQQ
  const q = seancesCompletes(await graphique("QQQ", "60d", "5m"), "QQQ").map((x) => x[0]);
  const coupure = q[Math.floor(q.length / 2)];
  const coupureJ = qJ[Math.floor(qJ.length / 2)];
  const etat = { gen: crypto.randomUUID(), liste: symboles, grosses: u.grosses, volatiles: u.volatiles, volatilite: u.volatilite, pos: 0, debut: new Date().toISOString(), coupure, premiere: q[0], derniere: q[q.length - 1], seances: q.length,
    coupureJ, premiereJ: qJ[31], derniereJ: qJ[qJ.length - 1], joursJ: qJ.length, fini: false, echecs: 0 };
  await ecrireEtat(env.DB, "test", etat);
  return etat;
}

// Traite le lot suivant (appelé chaque minute par la tâche planifiée)
export async function lotSuivant(env, taille = 12) {
  const etat = await lireEtat(env.DB, "test");
  if (!etat || etat.fini) return etat;
  if (etat.verrou && Date.now() - etat.verrou < 240e3) return { ...etat, occupe: true }; // un lot déjà en cours : pas de double comptage
  etat.verrou = Date.now(); await ecrireEtat(env.DB, "test", etat);
  const lot = etat.liste.slice(etat.pos, etat.pos + taille);
  if (!lot.length) { etat.fini = true; etat.finLe = new Date().toISOString(); await ecrireEtat(env.DB, "test", etat); return etat; }
  const qqqS = seancesCompletes(await graphique("QQQ", "60d", "5m"), "QQQ");
  const qqq = Object.fromEntries(qqqS);
  const aujNY = local(Date.now(), marcheDe("QQQ")).date;
  const qqqJ = qqqJour(barresJour(await graphique("QQQ", "1y", "1d"), aujNY));
  const grosses = new Set(etat.grosses || []);
  const uaL = await env.DB.prepare("SELECT valeur FROM config WHERE cle = 'contact_sec'").first(); const ua = uaL ? uaL.valeur : "";
  let ciks = {};
  if (ua) { try { const j = await (await fetch("https://www.sec.gov/files/company_tickers.json", { headers: { "User-Agent": ua } })).json(); for (const v of Object.values(j)) ciks[String(v.ticker).toUpperCase()] = String(v.cik_str).padStart(10, "0"); } catch (e) {} }
  const res = await parLots(lot, 4, async (sym) => {
    const liquide = grosses.has(sym);
    const J = barresJour(await graphique(sym, "1y", "1d"), aujNY);
    const cl = J.map((x) => [x.d, x.c]);
    const hautDe = Object.fromEntries(J.map((x, i) => [x.d, i]));
    const trades = [];
    // 1) intraday sur 60 jours
    const ses = seancesCompletes(await graphique(sym, "60d", "5m"), sym);
    for (let i = 0; i < ses.length; i++) {
      const [d, D] = ses[i];
      const prec = cl.filter((x) => x[0] < d);
      const veille = prec.length ? J[hautDe[prec[prec.length - 1][0]]] : null;
      const pool = i >= 20 ? construirePool(ses.slice(Math.max(0, i - 40), i).map((x) => x[1])) : null;
      const t = simulerSeance(sym, D, { qqq: qqq[d] || null, figureVeille: figureALaCloture(prec.map((x) => x[1])), hautVeille: veille ? veille.h : null, liquide, pool, finIndex: 76 });
      for (const [rid, tr] of Object.entries(t)) if (tr && tr.statut === "ferme") trades.push({ rid, d, per: d < etat.coupure ? "A" : "B", pct: tr.pct, R: tr.R, w: tr.w || 1 });
    }
    // 2) journalier sur 1 an (+ résultats SEC)
    let resultats = new Set();
    if (ua && ciks[sym]) { try { const dates = [...(await datesBonsResultats(ciks[sym], ua))].sort(); for (const dd of dates) { const x = J.find((b) => b.d >= dd); if (x) resultats.add(x.d); } } catch (e) {} }
    for (const tr of strategiesJour(J, { qqq: qqqJ, liquide, resultats })) trades.push({ ...tr, per: tr.d < etat.coupureJ ? "A" : "B" });
    const parRegle = {}; for (const x of trades) (parRegle[x.rid] = parRegle[x.rid] || []).push(x);
    return parRegle;
  });
  const st = [];
  res.forEach((parRegle, i) => {
    const sym = lot[i];
    if (!parRegle || parRegle.erreur) { etat.echecs++; etat.erreurs = [...(etat.erreurs || []), `${sym} : ${parRegle ? parRegle.erreur : "vide"}`].slice(-15); return; }
    for (const [rid, trades] of Object.entries(parRegle)) {
      for (const per of ["A", "B"]) {
        const t = trades.filter((x) => x.per === per); if (!t.length) continue;
        st.push(env.DB.prepare("INSERT OR REPLACE INTO bt VALUES (?,?,?,?,?,?,?,?)").bind(rid, sym, per, t.length, t.filter((x) => x.pct > 0).length, t.reduce((a, x) => a + x.pct * (x.w || 1), 0), t.reduce((a, x) => a + x.R, 0), creux(t.map((x) => x.pct * (x.w || 1)))));
      }
      const parJour = {};
      for (const x of trades) { const pj = (parJour[x.d] = parJour[x.d] || [0, 0]); pj[0]++; pj[1] += x.pct * (x.w || 1); }
      for (const [d, [n, s]] of Object.entries(parJour)) st.push(env.DB.prepare("INSERT INTO bt_jour VALUES (?,?,?,?) ON CONFLICT (regle, date) DO UPDATE SET n = n + excluded.n, spct = spct + excluded.spct").bind(rid, d, n, s));
    }
  });
  const cur = await lireEtat(env.DB, "test");
  if (!cur || cur.gen !== etat.gen) return cur; // le test a été relancé pendant ce lot : on jette ce lot
  for (let i = 0; i < st.length; i += 400) await env.DB.batch(st.slice(i, i + 400));
  etat.pos += lot.length; etat.verrou = null;
  if (etat.pos >= etat.liste.length) { etat.fini = true; etat.finLe = new Date().toISOString(); }
  await ecrireEtat(env.DB, "test", etat);
  return etat;
}

// Classement : par règle (A et B), et le test honnête « meilleurs couples choisis sur A -> résultat sur B »
export async function classement(db, mise = 1000) {
  const etat = await lireEtat(db, "test");
  const parRegle = (await db.prepare("SELECT regle, per, SUM(n) n, SUM(g) g, SUM(spct) spct, SUM(sr) sr, COUNT(DISTINCT sym) syms FROM bt GROUP BY regle, per").all()).results;
  const jours = (await db.prepare("SELECT regle, date, n, spct FROM bt_jour ORDER BY date").all()).results;
  const creuxR = {}; const parJourR = {};
  for (const j of jours) (parJourR[j.regle] = parJourR[j.regle] || []).push(j);
  for (const [r, l] of Object.entries(parJourR)) creuxR[r] = creux(l.map((x) => x.spct)) * mise;
  const regles = {};
  for (const x of parRegle) {
    const r = (regles[x.regle] = regles[x.regle] || { regle: x.regle });
    r[x.per] = { trades: x.n, gagnants: x.n ? +(100 * x.g / x.n).toFixed(1) : null, moyPct: x.n ? +(100 * x.spct / x.n).toFixed(3) : null, gain: Math.round(x.spct * mise), rMoyen: x.n ? +(x.sr / x.n).toFixed(3) : null, actions: x.syms };
  }
  for (const r of Object.values(regles)) {
    r.creuxTotal = Math.round(creuxR[r.regle] || 0);
    const l = parJourR[r.regle] || []; r.joursPositifs = l.filter((x) => x.spct > 0).length; r.jours = l.length;
    r.tient = !!(r.A && r.B && r.A.moyPct > 0 && r.B.moyPct > 0);
  }
  // Choisis sur A (au moins 5 trades, meilleur gain moyen), vérifiés sur B
  const couples = (await db.prepare(`SELECT a.regle, a.sym, a.n an, a.spct aspct, a.g ag, b.n bn, b.spct bspct, b.g bg, b.creux bcreux
    FROM bt a LEFT JOIN bt b ON b.regle = a.regle AND b.sym = a.sym AND b.per = 'B'
    WHERE a.per = 'A' AND a.n >= 5 AND a.spct > 0 ORDER BY a.spct / a.n DESC LIMIT 2000`).all()).results;
  const top = (k) => couples.slice(0, k);
  const verifie = (l) => { const avec = l.filter((x) => x.bn); const n = avec.reduce((a, x) => a + x.bn, 0); const s = avec.reduce((a, x) => a + x.bspct, 0); return { couples: l.length, avecTradesB: avec.length, tradesB: n, gainB: Math.round(s * mise), moyPctB: n ? +(100 * s / n).toFixed(3) : null, gainA: Math.round(l.reduce((a, x) => a + x.aspct, 0) * mise) }; };
  const deuxFois = (await db.prepare(`SELECT a.regle, a.sym, a.n an, a.spct aspct, b.n bn, b.spct bspct, b.creux bcreux FROM bt a JOIN bt b ON b.regle = a.regle AND b.sym = a.sym AND b.per = 'B'
    WHERE a.per = 'A' AND a.n >= 4 AND b.n >= 4 AND a.spct > 0 AND b.spct > 0 ORDER BY (a.spct + b.spct) DESC LIMIT 60`).all()).results;
  return { etat, mise, regles: Object.values(regles), choixSurA: { top20: verifie(top(20)), top100: verifie(top(100)), top500: verifie(top(500)) }, gagnentDeuxFois: deuxFois.map((x) => ({ ...x, gainA: Math.round(x.aspct * mise), gainB: Math.round(x.bspct * mise), creuxB: Math.round(x.bcreux * mise) })) };
}
