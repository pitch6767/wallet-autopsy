// Pitch 11.11 : pour chaque figure du scanner — la date de la figure, le rendement depuis l'achat, et quand on vend.
// Règle (la même que dans le banc d'essai) : achat à l'ouverture du jour suivant la figure (+0,05 % de glissement),
// stop 2 × ATR(14) sous le prix d'achat, sinon vente à la clôture du N-ième jour. N = la durée (1, 3 ou 5 jours)
// qui a le mieux marché pour cette figure dans le classement à capital égal.
import { graphique, parLots } from "./donnees.js";
import { barresJour } from "./labo.js";
import { seance, versUtc, MARCHES } from "./temps.js";
import { lireEtat } from "./test.js";
import { GLISSEMENT } from "./regles.js";

export const SCHEMA_SUIVI = [
  "CREATE TABLE IF NOT EXISTS figures_hist (date_fig TEXT, sym TEXT, figures TEXT, prix_fig REAL, PRIMARY KEY (date_fig, sym))",
  "CREATE TABLE IF NOT EXISTS figures_suivi (date_fig TEXT, sym TEXT, figures TEXT, duree INTEGER, achat_d TEXT, achat REAL, stop REAL, vente_d TEXT, vente REAL, statut TEXT, raison TEXT, rendement REAL, maj TEXT, PRIMARY KEY (date_fig, sym))",
  "ALTER TABLE figures_suivi ADD COLUMN jeton INTEGER", "ALTER TABLE figures_suivi ADD COLUMN achat_h TEXT", "ALTER TABLE figures_suivi ADD COLUMN vente_h TEXT",
];
const NOMS = { breakout_20d: "cassure 20 j", bull_flag: "drapeau", reclaim_ma20: "repasse MA20", oversold: "survendu", oversold_bounce: "rebond survente" };

async function schema(db) { for (const q of SCHEMA_SUIVI) { try { await db.prepare(q).run(); } catch (e) {} } }
const HEURE = (ms) => new Date(ms).toLocaleTimeString("fr-CH", { timeZone: "Europe/Zurich", hour: "2-digit", minute: "2-digit" });
const JOUR = (ms) => new Date(ms - 0).toLocaleDateString("sv-SE", { timeZone: "Europe/Zurich" });
// Pitch 11.11 : une action qui existe en jeton s'achète tout de suite, à la clôture de la figure (bougies 5 min Hyperliquid)
async function bougies(sym, debut, fin) {
  const r = await fetch("https://api.hyperliquid.xyz/info", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ type: "candleSnapshot", req: { coin: "xyz:" + sym, interval: "5m", startTime: debut, endTime: fin } }) });
  if (!r.ok) return [];
  return ((await r.json()) || []).map((b) => ({ t: b.t, o: +b.o, h: +b.h, l: +b.l, c: +b.c }));
}
export async function enregistrerFigures(db, hits) {
  await schema(db);
  const st = hits.map((h) => db.prepare("INSERT OR IGNORE INTO figures_hist VALUES (?,?,?,?)").bind(h.date, h.symbol, h.figures.join(","), h.prix));
  for (let i = 0; i < st.length; i += 400) await db.batch(st.slice(i, i + 400));
}

// Durée de détention par figure : la meilleure des trois (1, 3, 5 jours) au classement à capital égal (A + B)
async function durees(db) {
  const out = {};
  try {
    const l = (await db.prepare("SELECT regle, SUM(s) s FROM bt_cap WHERE regle LIKE 'j-%-%j:aucun' GROUP BY regle").all()).results;
    for (const x of l) { const m = /^j-(.+)-(\d)j:aucun$/.exec(x.regle); if (!m) continue; const o = out[m[1]]; if (!o || x.s > o.s) out[m[1]] = { h: +m[2], s: x.s }; }
  } catch (e) {}
  return Object.fromEntries(Object.entries(out).map(([k, v]) => [k, v.h]));
}

// Ajoute n jours de bourse à une date (jours fériés de New York respectés)
function plusJours(d, n) { let x = new Date(d + "T12:00:00Z"); let k = 0; while (k < n) { x = new Date(x.getTime() + 864e5); if (seance(x.toISOString().slice(0, 10), MARCHES.actions)) k++; } return x.toISOString().slice(0, 10); }

export async function tourSuivi(env) {
  const db = env.DB; await schema(db);
  const dur = await durees(db);
  const ja = await lireEtat(db, "jetons_actions"); const jetons = new Set(((ja && ja.garde) || []).filter((k) => k.startsWith("hl:")).map((k) => k.slice(3)));
  const depuis = new Date(Date.now() - 20 * 864e5).toISOString().slice(0, 10);
  const l = (await db.prepare("SELECT h.* FROM figures_hist h LEFT JOIN figures_suivi s ON s.date_fig = h.date_fig AND s.sym = h.sym WHERE h.date_fig >= ? AND (s.statut IS NULL OR s.statut != 'vendu')").bind(depuis).all()).results.filter((f) => jetons.has(f.sym)); // Pitch 11.11 : actions tokenisées seulement
  const maj = new Date().toISOString(); const st = [];
  await parLots(l, 8, async (f) => {
    const s = await graphique(f.sym, "3mo", "1d"); const J = barresJour(s, "9999");
    const i = J.findIndex((b) => b.d === f.date_fig); if (i < 14) return;
    const figs = f.figures.split(",");
    const h = Math.max(...figs.map((x) => dur[x] || 3));
    const achatPrevu = plusJours(f.date_fig, 1), ventePrevue = plusJours(f.date_fig, h);
    let row;
    if (jetons.has(f.sym)) {
      // jeton : achat à la première bougie qui suit la clôture du jour de la figure ; vente à la clôture du N-ième jour ; stop surveillé 24 h/24
      const se = seance(f.date_fig, MARCHES.actions); const t0 = versUtc(f.date_fig, se ? se[1] : 960, MARCHES.actions);
      const seV = seance(ventePrevue, MARCHES.actions); const tV = versUtc(ventePrevue, seV ? seV[1] : 960, MARCHES.actions);
      const B = await bougies(f.sym, t0, Math.min(Date.now(), tV + 5 * 60e3));
      let a = 0; for (let k = i - 13; k <= i; k++) a += Math.max(J[k].h - J[k].l, Math.abs(J[k].h - J[k - 1].c), Math.abs(J[k].l - J[k - 1].c)); a /= 14;
      if (B.length) {
        const achat = B[0].o * (1 + 0.001), stop = achat - 2 * a; // jeton : 0,1 % d'écart + frais
        row = { jeton: 1, duree: h, achat_d: JOUR(B[0].t), achat_h: HEURE(B[0].t), achat, stop, vente_d: ventePrevue, vente_h: HEURE(tV), vente: null, statut: "en cours", raison: `jeton : vente le ${ventePrevue} à ${HEURE(tV)}, ou avant si le prix touche ${stop.toFixed(2)}`, rendement: null };
        for (const b of B.slice(1)) {
          if (b.l <= stop) { Object.assign(row, { vente_d: JOUR(b.t), vente_h: HEURE(b.t), vente: Math.min(stop, b.o) * (1 - 0.001), statut: "vendu", raison: "stop touché (jeton)" }); break; }
          if (b.t + 5 * 60e3 >= tV && Date.now() >= tV) { Object.assign(row, { vente_d: JOUR(b.t), vente_h: HEURE(b.t + 5 * 60e3), vente: b.c * (1 - 0.001), statut: "vendu", raison: `${h} jour${h > 1 ? "s" : ""} écoulé${h > 1 ? "s" : ""} (jeton)` }); break; }
        }
        row.rendement = (row.vente ?? B[B.length - 1].c) / achat - 1;
      }
    }
    if (row) {}
    else if (!J[i + 1]) row = { duree: h, achat_d: achatPrevu, achat: null, stop: null, vente_d: ventePrevue, vente: null, statut: "attente", raison: "achat à l'ouverture", rendement: null };
    else {
      let a = 0; for (let k = i - 13; k <= i; k++) a += Math.max(J[k].h - J[k].l, Math.abs(J[k].h - J[k - 1].c), Math.abs(J[k].l - J[k - 1].c)); a /= 14;
      const achat = J[i + 1].o * (1 + GLISSEMENT), stop = achat - 2 * a;
      row = { duree: h, achat_d: J[i + 1].d, achat, stop, vente_d: ventePrevue, vente: null, statut: "en cours", raison: `vente prévue à la clôture du ${ventePrevue}, ou avant si le prix touche ${stop.toFixed(2)}`, rendement: null };
      for (let k = i + 1; k <= Math.min(i + h, J.length - 1); k++) {
        const b = J[k];
        if (k > i + 1 && b.o <= stop) { Object.assign(row, { vente_d: b.d, vente: b.o * (1 - GLISSEMENT), statut: "vendu", raison: "stop (ouverture sous le stop)" }); break; }
        if (b.l <= stop) { Object.assign(row, { vente_d: b.d, vente: stop * (1 - GLISSEMENT), statut: "vendu", raison: "stop touché" }); break; }
        if (k === i + h && b.d < new Date(Date.now() - 4 * 3600e3).toISOString().slice(0, 10)) { Object.assign(row, { vente_d: b.d, vente: b.c * (1 - GLISSEMENT / 2), statut: "vendu", raison: `${h} jour${h > 1 ? "s" : ""} écoulé${h > 1 ? "s" : ""}` }); break; }
      }
      const actuel = row.vente ?? (s.meta && s.meta.regularMarketPrice) ?? J[J.length - 1].c;
      row.rendement = actuel / achat - 1;
    }
    st.push(db.prepare("INSERT OR REPLACE INTO figures_suivi (date_fig, sym, figures, duree, achat_d, achat, stop, vente_d, vente, statut, raison, rendement, maj, jeton, achat_h, vente_h) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)").bind(f.date_fig, f.sym, f.figures, row.duree, row.achat_d, row.achat, row.stop, row.vente_d, row.vente, row.statut, row.raison, row.rendement, maj, row.jeton || 0, row.achat_h || null, row.vente_h || null));
  });
  for (let i = 0; i < st.length; i += 400) await db.batch(st.slice(i, i + 400));
  return { suivis: l.length, ecrits: st.length };
}

export async function lireSuivi(db) {
  await schema(db);
  const l = (await db.prepare("SELECT * FROM figures_suivi ORDER BY date_fig DESC, rendement DESC").all()).results;
  const ja = await lireEtat(db, "jetons_actions");
  return { jetons: ((ja && ja.garde) || []).filter((k) => k.startsWith("hl:")).map((k) => k.slice(3)), lignes: l.filter((x) => x.jeton).map((x) => ({ ...x, figures: x.figures.split(",").map((f) => NOMS[f] || f) })), dureesParFigure: await durees(db) };
}
