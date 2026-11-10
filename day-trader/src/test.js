// Banc d'essai : chaque règle rejouée sur 60 jours de barres 5 min, action par action.
// Méthode Bot95 : on choisit sur la période A, on vérifie sur la période B (jamais vue au moment du choix).
import { graphique, sparkTout, barres, parLots } from "./donnees.js";
import { marcheDe, estBtc, local } from "./temps.js";
import { REGLES, simulerSeance, figureALaCloture } from "./regles.js";
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

export async function demarrer(env, symboles) {
  await schema(env.DB);
  await env.DB.batch([env.DB.prepare("DELETE FROM bt"), env.DB.prepare("DELETE FROM bt_jour")]);
  // coupure A/B : milieu des séances de QQQ
  const q = seancesCompletes(await graphique("QQQ", "60d", "5m"), "QQQ").map((x) => x[0]);
  const coupure = q[Math.floor(q.length / 2)];
  const etat = { gen: crypto.randomUUID(), liste: symboles, pos: 0, debut: new Date().toISOString(), coupure, premiere: q[0], derniere: q[q.length - 1], seances: q.length, fini: false, echecs: 0 };
  await ecrireEtat(env.DB, "test", etat);
  return etat;
}

// Traite le lot suivant (appelé chaque minute par la tâche planifiée)
export async function lotSuivant(env, taille = 40) {
  const etat = await lireEtat(env.DB, "test");
  if (!etat || etat.fini) return etat;
  if (etat.verrou && Date.now() - etat.verrou < 240e3) return { ...etat, occupe: true }; // un lot déjà en cours : pas de double comptage
  etat.verrou = Date.now(); await ecrireEtat(env.DB, "test", etat);
  const lot = etat.liste.slice(etat.pos, etat.pos + taille);
  if (!lot.length) { etat.fini = true; etat.finLe = new Date().toISOString(); await ecrireEtat(env.DB, "test", etat); return etat; }
  const qqqS = seancesCompletes(await graphique("QQQ", "60d", "5m"), "QQQ");
  const qqq = Object.fromEntries(qqqS);
  const { data: jour } = await sparkTout(lot, "1y", "1d");
  const res = await parLots(lot, 8, async (sym) => {
    const ses = seancesCompletes(await graphique(sym, "60d", "5m"), sym);
    const cl = jour[sym] ? cloturesJour(jour[sym], sym, Date.now()) : [];
    const m = marcheDe(sym); const nRange = 3; const btc = estBtc(sym);
    const fin = btc ? 287 : 76; // sortie forcée : 15 h 55 New York (barre de 15 h 50) / fin de journée UTC
    const parRegle = {};
    for (const [d, D] of ses) {
      const prec = cl.filter((x) => x[0] < d).map((x) => x[1]);
      const t = simulerSeance(sym, D, { qqq: qqq[d] || null, figureVeille: figureALaCloture(prec), nRange, finIndex: fin });
      for (const [rid, tr] of Object.entries(t)) {
        if (!tr || tr.statut === "annule") continue;
        (parRegle[rid] = parRegle[rid] || []).push({ d, per: d < etat.coupure ? "A" : "B", pct: tr.pct, R: tr.R });
      }
    }
    return parRegle;
  });
  const st = [];
  res.forEach((parRegle, i) => {
    const sym = lot[i];
    if (!parRegle || parRegle.erreur) { etat.echecs++; return; }
    for (const [rid, trades] of Object.entries(parRegle)) {
      for (const per of ["A", "B"]) {
        const t = trades.filter((x) => x.per === per); if (!t.length) continue;
        st.push(env.DB.prepare("INSERT OR REPLACE INTO bt VALUES (?,?,?,?,?,?,?,?)").bind(rid, sym, per, t.length, t.filter((x) => x.pct > 0).length, t.reduce((a, x) => a + x.pct, 0), t.reduce((a, x) => a + x.R, 0), creux(t.map((x) => x.pct))));
      }
      const parJour = {};
      for (const x of trades) { const pj = (parJour[x.d] = parJour[x.d] || [0, 0]); pj[0]++; pj[1] += x.pct; }
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
