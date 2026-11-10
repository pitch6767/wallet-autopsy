// Moteur de combinaisons (Pitch 10.11 : « bien plus de combinaisons, plus de 2 filtres, pas obligé d'avoir un truc à eux »).
// Chaque jour et chaque action, 16 conditions vraies/fausses à la clôture. Une règle = 1, 2 ou 3 conditions
// ensemble + une durée (1, 3 ou 5 jours). Achat à l'ouverture du lendemain, stop 2 × ATR, sortie à la clôture du dernier jour.
// Chaque trade est comparé au QQQ sur exactement la même fenêtre (« aurait-on fait mieux en gardant le Nasdaq ? »).
import { figures, rsi } from "./scanner.js";
import { GLISSEMENT } from "./regles.js";

export const CONDITIONS = [
  { id: "f20", camp: "leur", nom: "cassure du plus haut 20 j" },
  { id: "drapeau", camp: "leur", nom: "drapeau haussier" },
  { id: "ma20", camp: "leur", nom: "retour au-dessus MA20" },
  { id: "rsi30", camp: "leur", nom: "survendu RSI < 30" },
  { id: "rebond", camp: "leur", nom: "rebond après survente" },
  { id: "res", camp: "leur", nom: "bons résultats SEC (5 derniers jours)" },
  { id: "consensus", camp: "nous", nom: "consensus : ≥ 2 de leurs signaux" },
  { id: "marche", camp: "nous", nom: "élan du marché : QQQ > MA20" },
  { id: "contre", camp: "nous", nom: "marché faible : QQQ < MA20" },
  { id: "grosse", camp: "nous", nom: "écart serré : 25 plus grosses" },
  { id: "volatile", camp: "autre", nom: "75 plus volatiles" },
  { id: "volume", camp: "autre", nom: "volume ≥ 1,5 × moyenne 20 j" },
  { id: "tendance", camp: "autre", nom: "au-dessus de la MA50" },
  { id: "hautjour", camp: "autre", nom: "clôture dans le haut de la journée" },
  { id: "elan5", camp: "autre", nom: "+5 % ou plus en 5 jours" },
  { id: "chute5", camp: "autre", nom: "−5 % ou plus en 5 jours" },
];
export const DUREES = [1, 3, 5];
const NB = CONDITIONS.length;

// Toutes les combinaisons de 1 à 3 conditions (sans les contradictions évidentes)
const CONTRA = [["marche", "contre"], ["elan5", "chute5"], ["grosse", "volatile"]];
export const COMBOS = [];
for (let a = 0; a < NB; a++) { COMBOS.push([a]); for (let b = a + 1; b < NB; b++) { COMBOS.push([a, b]); for (let c = b + 1; c < NB; c++) COMBOS.push([a, b, c]); } }
const ok = (c) => !CONTRA.some(([x, y]) => c.some((i) => CONDITIONS[i].id === x) && c.some((i) => CONDITIONS[i].id === y));
export const COMBOS_OK = COMBOS.filter(ok);
export const idCombo = (c, h) => `${h}j:${c.map((i) => CONDITIONS[i].id).join("+")}`;
export const nomRegle = (id) => { const [h, cs] = id.split(":"); return `${cs.split("+").map((x) => (CONDITIONS.find((k) => k.id === x) || {}).nom || x).join(" + ")}, garder ${h.replace("j", "")} j`; };
export const NB_REGLES = COMBOS_OK.length * DUREES.length;

function atr(J, t, n = 14) { if (t < n) return null; let s = 0; for (let i = t - n + 1; i <= t; i++) s += Math.max(J[i].h - J[i].l, Math.abs(J[i].h - J[i - 1].c), Math.abs(J[i].l - J[i - 1].c)); return s / n; }
const moy = (a) => a.reduce((x, y) => x + y, 0) / a.length;

// Masque des conditions vraies à la clôture du jour t
export function conditionsDuJour(J, t, { qqq = {}, grosse = false, volatile = false, resultats = new Set() } = {}) {
  if (t < 50) return null;
  const c = J.slice(0, t + 1).map((x) => x.c);
  const tags = figures(c).tags;
  const q = qqq[J[t].d];
  const res = J.slice(Math.max(0, t - 4), t + 1).some((x) => resultats.has(x.d));
  const nbLeurs = tags.length + (res ? 1 : 0);
  const v20 = J.slice(t - 20, t).map((x) => x.v || 0);
  const vrai = {
    f20: tags.includes("breakout_20d"), drapeau: tags.includes("bull_flag"), ma20: tags.includes("reclaim_ma20"),
    rsi30: tags.includes("oversold"), rebond: tags.includes("oversold_bounce"), res, consensus: nbLeurs >= 2,
    marche: !!(q && q.ma20 && q.c > q.ma20), contre: !!(q && q.ma20 && q.c < q.ma20), grosse, volatile,
    volume: (J[t].v || 0) >= 1.5 * moy(v20) && moy(v20) > 0, tendance: J[t].c > moy(c.slice(-50)),
    hautjour: J[t].h > J[t].l && (J[t].c - J[t].l) / (J[t].h - J[t].l) >= 0.75,
    elan5: J[t].c / J[t - 5].c - 1 >= 0.05, chute5: J[t].c / J[t - 5].c - 1 <= -0.05,
  };
  let m = 0; CONDITIONS.forEach((k, i) => { if (vrai[k.id]) m |= 1 << i; });
  return m;
}

// Résultat d'un achat le lendemain de t, gardé h jours (stop 2 × ATR) ; null si pas encore terminé
export function issue(J, t, h) {
  if (t + h > J.length - 1) return null;
  const a = atr(J, t); if (!a) return null;
  const entree = J[t + 1].o * (1 + GLISSEMENT), stop = entree - 2 * a;
  for (let j = t + 1; j <= t + h; j++) {
    const b = J[j];
    if (j > t + 1 && b.o <= stop) return { pct: b.o * (1 - GLISSEMENT) / entree - 1, fin: j, issue: "stop" };
    if (b.l <= stop) return { pct: stop * (1 - GLISSEMENT) / entree - 1, fin: j, issue: "stop" };
  }
  return { pct: J[t + h].c * (1 - GLISSEMENT / 2) / entree - 1, fin: t + h, issue: "durée" };
}

// Accumule les trades de toutes les combinaisons pour une action -> { regle|per : [n, g, s, s2, sx, gx] }
export function accumulerAction(J, ctx, qqqJ, coupure, acc) {
  const qIdx = Object.fromEntries((ctx.qqqBarres || []).map((x, i) => [x.d, i]));
  for (let t = 50; t < J.length - 1; t++) {
    const m = conditionsDuJour(J, t, ctx); if (!m) continue;
    const bits = []; for (let i = 0; i < NB; i++) if (m & (1 << i)) bits.push(i);
    if (!bits.length) continue;
    const per = J[t + 1].d < coupure ? "A" : "B";
    for (const h of DUREES) {
      const r = issue(J, t, h); if (!r) continue;
      // même fenêtre sur le QQQ : ouverture du lendemain -> clôture du jour de sortie
      const qi = qIdx[J[t + 1].d], qf = qIdx[J[r.fin].d];
      const qPct = qi != null && qf != null ? ctx.qqqBarres[qf].c / ctx.qqqBarres[qi].o - 1 : 0;
      const x = r.pct - qPct;
      const sous = [];
      for (let a = 0; a < bits.length; a++) { sous.push([bits[a]]); for (let b = a + 1; b < bits.length; b++) { sous.push([bits[a], bits[b]]); for (let c = b + 1; c < bits.length; c++) sous.push([bits[a], bits[b], bits[c]]); } }
      for (const s of sous) {
        if (!ok(s)) continue;
        const k = idCombo(s, h) + "|" + per;
        const v = acc[k] || (acc[k] = [0, 0, 0, 0, 0, 0]);
        v[0]++; if (r.pct > 0) v[1]++; v[2] += r.pct; v[3] += r.pct * r.pct; v[4] += x; if (x > 0) v[5]++;
      }
    }
  }
}

export const SCHEMA_COMBO = "CREATE TABLE IF NOT EXISTS bt_combo (regle TEXT, per TEXT, n INTEGER, g INTEGER, s REAL, s2 REAL, sx REAL, gx INTEGER, PRIMARY KEY (regle, per))";

export async function ecrireAcc(db, acc) {
  const st = Object.entries(acc).map(([k, v]) => { const [regle, per] = k.split("|"); return db.prepare("INSERT INTO bt_combo VALUES (?,?,?,?,?,?,?,?) ON CONFLICT (regle, per) DO UPDATE SET n = n + excluded.n, g = g + excluded.g, s = s + excluded.s, s2 = s2 + excluded.s2, sx = sx + excluded.sx, gx = gx + excluded.gx").bind(regle, per, ...v); });
  for (let i = 0; i < st.length; i += 500) await db.batch(st.slice(i, i + 500));
}

// Critère « tient » (affiché tel quel) : au moins 30 trades sur A et sur B, gagne sur A et B,
// bat le QQQ sur A et B, et t-stat ≥ 2 sur B (gain moyen nettement au-dessus de zéro, pas un coup de chance isolé)
export async function classementCombos(db, mise = 1000, tous = false) {
  const l = (await db.prepare("SELECT * FROM bt_combo").all()).results;
  const m = {};
  for (const x of l) {
    const r = (m[x.regle] = m[x.regle] || { regle: x.regle });
    const moyP = x.s / x.n, sd = Math.sqrt(Math.max(0, x.s2 / x.n - moyP * moyP));
    r[x.per] = { trades: x.n, gagnants: +(100 * x.g / x.n).toFixed(1), gain: Math.round(x.s * mise), moyPct: +(100 * moyP).toFixed(3), contreQqq: Math.round(x.sx * mise), batQqq: +(100 * x.gx / x.n).toFixed(1), t: sd > 0 ? +(moyP / (sd / Math.sqrt(x.n))).toFixed(2) : 0 };
  }
  const toutes = Object.values(m);
  for (const r of toutes) r.tient = !!(r.A && r.B && r.A.trades >= 30 && r.B.trades >= 30 && r.A.gain > 0 && r.B.gain > 0 && r.A.contreQqq > 0 && r.B.contreQqq > 0 && r.B.t >= 2);
  const tiennent = toutes.filter((r) => r.tient).sort((a, b) => b.B.contreQqq - a.B.contreQqq);
  const assez = toutes.filter((r) => r.A && r.B && r.A.trades >= 30 && r.B.trades >= 30);
  // Contrôle du hasard : combien passeraient si on inversait A et B (même exigence) ? Doit être du même ordre.
  if (tous) return { mise, toutes: assez.sort((a, b) => (b.tient - a.tient) || (b.B.contreQqq - a.B.contreQqq)).map((r) => ({ ...r, nom: nomRegle(r.regle) })) };
  return { mise, totalRegles: toutes.length, avecAssezDeTrades: assez.length, tiennent: tiennent.length, top: tiennent.slice(0, 150).map((r) => ({ ...r, nom: nomRegle(r.regle) })),
    meilleuresSurB: assez.sort((a, b) => b.B.contreQqq - a.B.contreQqq).slice(0, 30).map((r) => ({ ...r, nom: nomRegle(r.regle) })) };
}
