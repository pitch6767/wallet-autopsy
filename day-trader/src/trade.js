// Le parcours d'un trade : entrée -> sortie -> Time Machine -> taille -> contrôle du risque.
// Côté achat seulement, comme l'original. Rien ici ne passe d'ordre.
import { local, seance, marcheDe, hhmm, lireHeure, estBtc, jourOuvre, NYSE_FERMETURE_13H } from "./temps.js";
import { graphique, barres } from "./donnees.js";
import { HasardPython } from "./hasard.js";

export const REGLAGES_DEFAUT = {
  budget: 5000, cash_buffer_pct: 10, max_position_pct: 75, max_order_usd: 4000, min_order_usd: 5,
  max_loss_per_trade_usd: 50, max_daily_loss_usd: 150, max_trades_per_day: 3, min_reward_risk: 1.0,
  no_entries_before: "09:45", no_entries_after: "15:30", flat_by: "15:55", blocked: [],
  btc_decimales: 4,
};
const r2 = (x) => Math.round(x * 100 + 1e-9) / 100;           // arrondi au centime, demi vers le haut
const sousCentime = (x) => Math.floor(Math.round(x * 1e6) / 1e4) / 100; // un stop d'achat s'arrondit vers le bas

// Le dernier jour de séance déjà ouvert (aujourd'hui s'il a ouvert, sinon le précédent)
export function jourParDefaut(sym, maintenantMs) {
  const m = marcheDe(sym); const now = local(maintenantMs, m);
  let d = now.date; const se = seance(d, m);
  if (se && now.min >= se[0] + 5) return d;
  for (let i = 0; i < 10; i++) {
    d = new Date(Date.parse(d + "T12:00:00Z") - 864e5).toISOString().slice(0, 10);
    if (jourOuvre(d, m)[0]) return d;
  }
  return d;
}

// ------------------------------------------------------------- 1. minuteur d'entrée (trader-entry)
export function entree(bars, sym, jour, maintenantMs, { setup = "orb", minutesRange = 15, niveau = null, reglages = REGLAGES_DEFAUT } = {}) {
  const m = marcheDe(sym); const btc = estBtc(sym);
  const now = local(maintenantMs, m);
  const se = seance(jour, m);
  const res = { symbol: sym.toUpperCase(), setup, jour, statut: "attente", raison: "", range: null, niveau: null, declenchement: null, derniere: null, tz: m.tz };
  if (!se) return { ...res, statut: "pas-de-donnees", raison: `Le marché est fermé le ${jour} (${jourOuvre(jour, m)[1]}).` };
  const nowMin = jour < now.date ? 24 * 60 : jour > now.date ? -1 : now.min;
  const avant = btc ? se[0] : lireHeure(reglages.no_entries_before);
  let apres = btc ? se[1] : lireHeure(reglages.no_entries_after);
  if (!btc && NYSE_FERMETURE_13H[jour]) apres -= 180; // fermeture à 13 h : la limite avance de 3 heures
  const finRange = se[0] + minutesRange;
  const b = bars.filter((x) => x.date === jour && x.min + 5 <= nowMin);
  res.barresFermees = b.length;
  if (nowMin < se[0]) return { ...res, raison: `Le marché ouvre à ${hhmm(se[0])} (${m.tz}).` };
  const n = minutesRange / 5;
  const rb = b.filter((x) => x.slot < n);
  if (rb.length) res.range = { haut: r2(Math.max(...rb.map((x) => x.h))), bas: r2(Math.min(...rb.map((x) => x.l))), minutes: minutesRange, complet: nowMin >= finRange };
  let lvl;
  if (setup === "orb") {
    if (nowMin < finRange) return { ...res, raison: `${rb.length} barre(s) du range sur ${n} ; le range est fixé à ${hhmm(finRange)}.` };
    if (!rb.length) return { ...res, statut: "pas-de-donnees", raison: "Yahoo n'a envoyé aucune barre pour le range d'ouverture." };
    lvl = Math.max(...rb.map((x) => x.h));
  } else {
    if (!(niveau > 0)) return { ...res, statut: "erreur", raison: "Le setup « niveau » demande un prix." };
    lvl = +niveau;
  }
  res.niveau = r2(lvl);
  const premier = setup === "orb" ? n : 0;
  const trig = b.find((x) => x.slot >= premier && x.min + 5 >= avant && x.min + 5 <= apres && x.c > lvl);
  const der = b[b.length - 1];
  if (der) res.derniere = { barre: hhmm(der.min), cloture: r2(der.c), ecartPct: r2(100 * (der.c / lvl - 1)) };
  if (trig) {
    return { ...res, statut: "declenche", raison: `La barre de ${hhmm(trig.min)} a clôturé au-dessus ${setup === "orb" ? "du haut du range" : "du niveau"}.`,
      declenchement: { heure: hhmm(trig.min + 5), barre: hhmm(trig.min), indice: trig.slot, prix: r2(trig.c), pctAuDessus: r2(100 * (trig.c / lvl - 1)) } };
  }
  if (!der) return { ...res, statut: "pas-de-donnees", raison: `Yahoo n'a encore envoyé aucune barre pour le ${jour}.` };
  const quoi = setup === "orb" ? `clôture au-dessus du haut du range ${r2(lvl)}` : `clôture au-dessus de ${r2(lvl)}`;
  if (nowMin >= apres) return { ...res, statut: "expire", raison: `Pas de ${quoi} avant ${hhmm(apres)}, l'heure limite pour une nouvelle entrée.` };
  const ecart = lvl - der.c;
  return { ...res, raison: `Dernière clôture ${r2(der.c)} (barre de ${hhmm(der.min)}), ${Math.abs(ecart).toFixed(2)} ${ecart >= 0 ? "sous" : "au-dessus de"} ${setup === "orb" ? "le haut du range" : "le niveau"} ${r2(lvl)}.` };
}

// ------------------------------------------------------------- 2. plan de sortie (trader-exit)
export function planSortie({ symbol, jour, entree: e, setup = "orb", range = null, stop = "or-mid", cible = "2R", indice = null, heure = null, reglages = REGLAGES_DEFAUT, barresJour = [] }) {
  e = +e; if (!(e > 0)) return { erreur: "Il faut un prix d'entrée." };
  let s, regle;
  const st = String(stop).toLowerCase().trim();
  if (st === "or-mid" || st === "or-low") {
    if (!range) return { erreur: "Un setup « niveau » n'a pas de range d'ouverture : donne un stop (prix ou %)." };
    s = sousCentime(st === "or-mid" ? (range.haut + range.bas) / 2 : range.bas); regle = st === "or-mid" ? "or_mid" : "or_low";
  } else if (st.startsWith("price:")) { s = sousCentime(+st.slice(6)); regle = "pct"; }
  else if (st.startsWith("pct:")) { s = sousCentime(e * (1 - +st.slice(4) / 100)); regle = "pct"; }
  else if (st.startsWith("atr:")) {
    const k = +st.slice(4); const b = barresJour.filter((x) => indice == null || x.slot <= indice);
    if (b.length < 2) return { erreur: "Pas assez de barres pour l'ATR." };
    const tr = b.slice(1).map((x, i) => Math.max(x.h - x.l, Math.abs(x.h - b[i].c), Math.abs(x.l - b[i].c)));
    const der = tr.slice(-14); const atr = der.reduce((a, x) => a + x, 0) / der.length;
    s = sousCentime(e - k * atr); regle = "pct";
  } else return { erreur: "Stop inconnu : or-mid, or-low, price:X, pct:X ou atr:K." };
  if (!(s > 0) || s >= e) return { erreur: `Le stop ${s} n'est pas sous l'entrée ${e}.` };
  const risque = r2(e - s);
  if (e - s < e * 0.0005) return { erreur: `Le stop est à ${risque} sous l'entrée, moins de 0,05 % du prix : trop serré pour survivre au spread.` };
  let t, rCible;
  const ct = String(cible).toLowerCase().trim();
  if (ct.startsWith("price:")) { t = r2(+ct.slice(6)); rCible = (t - e) / (e - s); }
  else { const R = parseFloat(ct); if (!(R > 0)) return { erreur: "Cible inconnue : 1R, 1.5R, 2R... ou price:X." }; t = r2(e + R * (e - s)); rCible = R; }
  if (t <= e) return { erreur: `La cible ${t} n'est pas au-dessus de l'entrée ${e}.` };
  const btc = estBtc(symbol);
  let flat = btc ? null : reglages.flat_by;
  if (flat && NYSE_FERMETURE_13H[jour]) flat = hhmm(lireHeure(flat) - 180);
  const avert = [];
  if (rCible < reglages.min_reward_risk) avert.push(`Rendement/risque ${rCible.toFixed(2)} sous ton minimum ${reglages.min_reward_risk} : le contrôle du risque le bloquera.`);
  return { symbol: symbol.toUpperCase(), jour, setup, cote: "achat", entree: e, stop: s, cible: t, risqueParPart: risque, rCible: Math.round(rCible * 1e4) / 1e4, regleStop: regle, range, indice, heure, flatBy: flat, avertissements: avert };
}

// ------------------------------------------------------------- 3. Time Machine (trader-timemachine)
function pct(a, q) { return a[Math.min(a.length - 1, Math.floor(q * a.length))]; }

export function simuler(pool, nb, entree, stop, cible, k, dernier, replays = 10000, graine = 19, fenetre = 2) {
  const risque = entree - stop; const rT = Math.round(((cible - entree) / risque) * 1e4) / 1e4;
  const rng = new HasardPython(graine);
  const slotDe = (i) => fenetre === 0 ? i : Math.min(nb - 1, Math.max(1, i + rng.entier(-fenetre, fenetre)));
  const issues = [], clotures = [], chemins = [];
  for (let n = 0; n < replays; n++) {
    let p = entree, issue = null; const garde = n < 30; const ch = [entree];
    for (let i = k + 1; i <= dernier; i++) {
      const j = slotDe(i); const [, h, l, c] = rng.choix(pool[j]);
      const hi = p * h, lo = p * l;
      if (issue === null) { if (lo <= stop) issue = "stop"; else if (hi >= cible) issue = "cible"; }
      p = p * c; if (garde) ch.push(r2(p));
    }
    issues.push(issue || "cloture"); clotures.push(p); if (garde) chemins.push(ch);
  }
  const cnt = { cible: 0, stop: 0, cloture: 0 }; issues.forEach((x) => cnt[x]++);
  let vert = 0, sommeR = 0;
  issues.forEach((o, i) => {
    if (o === "cible" || (o === "cloture" && clotures[i] > entree)) vert++;
    sommeR += o === "cible" ? rT : o === "stop" ? -1 : (clotures[i] - entree) / risque;
  });
  const tri = [...clotures].sort((a, b) => a - b);
  // éventail : 2 000 chemins, même graine
  const rng2 = new HasardPython(graine); const tous = [];
  const slot2 = (i) => fenetre === 0 ? i : Math.min(nb - 1, Math.max(1, i + rng2.entier(-fenetre, fenetre)));
  for (let n = 0; n < 2000; n++) { let p = entree; const ch = [entree]; for (let i = k + 1; i <= dernier; i++) { const j = slot2(i); p *= rng2.choix(pool[j])[3]; ch.push(p); } tous.push(ch); }
  const bandes = [];
  for (let j = 0; j <= dernier - k; j++) { const col = tous.map((c) => c[j]).sort((a, b) => a - b); bandes.push([0.05, 0.25, 0.5, 0.75, 0.95].map((q) => r2(pct(col, q)))); }
  const r4 = (x) => Math.round(x * 1e4) / 1e4;
  return { replays, graine, fenetre, barresRestantes: dernier - k, pCible: r4(cnt.cible / replays), pStop: r4(cnt.stop / replays), pNi: r4(cnt.cloture / replays), pVert: r4(vert / replays),
    medianeCloture: r2(pct(tri, 0.5)), p5: r2(pct(tri, 0.05)), p95: r2(pct(tri, 0.95)), rMoyen: Math.round((sommeR / replays) * 1e3) / 1e3, rCible: rT, bandes, chemins };
}

export function historique(seances, regle, dernier, nRange) {
  const trades = [];
  for (const [d, D] of seances) {
    const rb = D.slice(0, nRange); const oh = Math.max(...rb.map((b) => b.h)), ol = Math.min(...rb.map((b) => b.l));
    let kk = null; for (let i = nRange; i <= dernier; i++) if (D[i].c > oh) { kk = i; break; }
    if (kk === null) continue;
    const e = r2(D[kk].c);
    const s = regle.stop === "or_mid" ? sousCentime((oh + ol) / 2) : regle.stop === "or_low" ? sousCentime(ol) : sousCentime(e * (1 - regle.stopPct / 100));
    const risque = e - s; if (risque <= 0) continue;
    const t = r2(e + regle.rCible * risque);
    let oc = null;
    for (const b of D.slice(kk + 1, dernier + 1)) { if (b.l <= s) { oc = "stop"; break; } if (b.h >= t) { oc = "cible"; break; } }
    const cl = D[dernier].c;
    const R = oc === "cible" ? (t - e) / risque : oc === "stop" ? -1 : (cl - e) / risque;
    trades.push({ date: d, heure: hhmm(D[kk].min + 5), entree: e, stop: s, cible: t, issue: oc || "cloture", R: r2(R) });
  }
  const c = (x) => trades.filter((t) => t.issue === x).length;
  return { seances: seances.length, declenches: trades.length, cible: c("cible"), stop: c("stop"), cloture: c("cloture"), verts: trades.filter((t) => t.R > 0).length,
    rMoyen: trades.length ? Math.round((trades.reduce((a, t) => a + t.R, 0) / trades.length) * 1e3) / 1e3 : null, regle, trades };
}

export function verdict(mc, finTxt) {
  const pt = mc.pCible, ps = mc.pStop;
  if (pt + ps <= 0) return `Aucun replay n'a touché la cible ni le stop avant ${finTxt} : le prix à ${finTxt} décide de tout.`;
  const r = mc.rCible || 1; const part = pt / (pt + ps), equi = 1 / (1 + r); const d = part - equi;
  const unR = Math.abs(r - 1) < 0.005;
  const tete = Math.abs(d) < 0.05 ? (unR ? "Proche d'un pile ou face" : "Proche de l'équilibre") : Math.abs(d) < 0.15 ? (d > 0 ? "Penche vers la cible" : "Penche vers le stop") : (d > 0 ? "Nettement vers la cible" : "Nettement vers le stop");
  const cotes = `cible d'abord ${(100 * pt).toFixed(1)} % contre stop d'abord ${(100 * ps).toFixed(1)} %`;
  if (unR) return `${tete} : ${cotes}.`;
  return `${tete} : à ${+r.toFixed(2)}R, la cible doit arriver en premier dans ${(100 * equi).toFixed(0)} % des replays qui touchent un côté ; c'est le cas dans ${(100 * part).toFixed(0)} % (${cotes}).`;
}

export async function timeMachine(plan, opts = {}) {
  const s = await graphique(plan.symbol, "60d", "5m");
  return tmCoeur(s, plan, opts, Date.now());
}
export function tmCoeur(s, plan, { replays = 10000, graine = 19, fenetre = 2, jusqua = null } = {}, maintenantMs = Date.now()) {
  const sym = plan.symbol; const m = marcheDe(sym); const btc = estBtc(sym);
  const bars = barres(s, sym, maintenantMs);
  if (!bars.length) throw new Error(`aucune barre 5 minutes complète pour ${sym}`);
  const se = seance(plan.jour, m); if (!se) throw new Error(`pas de séance le ${plan.jour}`);
  const nb = (se[1] - se[0]) / 5; const nbPlein = (m.fermeture - m.ouverture) / 5;
  const finMin = jusqua != null ? jusqua : se[1];
  if ((finMin - se[0]) % 5 || finMin > se[1]) throw new Error(`l'heure de fin doit être sur la grille de 5 min et au plus ${hhmm(se[1])}`);
  const dernier = (finMin - se[0]) / 5 - 1;
  const jours = {}; for (const b of bars) (jours[b.date] = jours[b.date] || {})[b.slot] = b;
  const jourE = jours[plan.jour] || {};
  const k = plan.indice;
  if (k == null || !jourE[k]) throw new Error(`l'entrée n'est pas dans les données : pas de barre complète n°${k} le ${plan.jour}`);
  if (dernier <= k) throw new Error("rien à rejouer après l'entrée");
  const seances = [], courtes = [];
  for (const d of Object.keys(jours).sort()) {
    if (d >= plan.jour) continue;
    const D = jours[d];
    if (Object.keys(D).length === nbPlein) seances.push([d, Array.from({ length: nbPlein }, (_, i) => D[i])]); else courtes.push({ date: d, barres: Object.keys(D).length });
  }
  if (seances.length < 20) throw new Error(`seulement ${seances.length} séance(s) complète(s) avant le ${plan.jour} ; il en faut au moins 20`);
  const pool = Array.from({ length: nbPlein }, () => []);
  for (const [, D] of seances) for (let i = 1; i < nbPlein; i++) { const pc = D[i - 1].c; pool[i].push([D[i].o / pc, D[i].h / pc, D[i].l / pc, D[i].c / pc]); }
  const mc = simuler(pool, nbPlein, plan.entree, plan.stop, plan.cible, k, dernier, replays, graine, fenetre);
  const finTxt = hhmm(finMin) + (btc ? " UTC" : "");
  let hist = null;
  if (plan.setup === "orb" && plan.range) {
    let regle = plan.regleStop;
    if (regle !== "or_mid" && regle !== "or_low") regle = "pct";
    hist = historique(seances, { stop: regle, rCible: plan.rCible, stopPct: 100 * plan.risqueParPart / plan.entree }, dernier, (plan.range.minutes || 15) / 5);
  }
  const notes = [];
  if (mc.pNi > 0.4 && mc.pCible + mc.pStop > 0) notes.push(`${(100 * mc.pNi).toFixed(1)} % des replays ne touchent ni l'un ni l'autre avant ${finTxt} ; c'est le prix à ${finTxt} qui les décide.`);
  return { plan, mc: { ...mc, jusqua: finTxt, seancesPool: seances.length, du: seances[0][0], au: seances[seances.length - 1][0], heures: Array.from({ length: dernier - k + 1 }, (_, j) => hhmm(se[0] + 5 * (k + 1 + j))) },
    historique: hist, verdict: verdict(mc, finTxt), notes, courtesEcartees: courtes,
    note: `Simulation construite sur les ${seances.length} dernières séances complètes de ${sym}. Ce n'est pas une prédiction : résultats, nouvelles et suspensions peuvent faire ce que ces séances n'ont jamais fait. Même graine, mêmes chiffres.` };
}

// ------------------------------------------------------------- 4. taille de position (trader-budget)
export function taille(plan, reglages = REGLAGES_DEFAUT, prixFrais = null) {
  const btc = estBtc(plan.symbol);
  let e = plan.entree; let ref = "l'entrée du plan";
  if (prixFrais && prixFrais > e) { e = prixFrais; ref = "le dernier prix (plus haut que l'entrée)"; }
  const risque = e - plan.stop;
  if (risque <= 0) return { erreur: "Le prix est déjà au stop ou en dessous : pas d'ordre." };
  const budget = +reglages.budget; const tampon = budget * reglages.cash_buffer_pct / 100;
  const lim = {
    "perte max": reglages.max_loss_per_trade_usd / risque,
    "plafond position": budget * reglages.max_position_pct / 100 / e,
    "ordre max": reglages.max_order_usd / e,
    "liquidités": (budget - tampon) / e,
  };
  const qui = Object.entries(lim).sort((a, b) => a[1] - b[1])[0];
  const pas = btc ? Math.pow(10, -(reglages.btc_decimales ?? 4)) : 1;
  const qte = Math.floor(qui[1] / pas + 1e-9) * pas;
  const q = btc ? +qte.toFixed(reglages.btc_decimales ?? 4) : qte;
  if (!(q > 0)) return { erreur: `Zéro ${btc ? "BTC" : "action"} : le stop est trop loin pour ta perte max de ${reglages.max_loss_per_trade_usd} $ (risque ${risque.toFixed(2)} $ par ${btc ? "BTC" : "action"}).`, limites: lim };
  const rr = (plan.cible - e) / risque;
  if (rr < reglages.min_reward_risk) return { erreur: `Rendement/risque ${rr.toFixed(2)} sous ton minimum ${reglages.min_reward_risk} (le prix a couru vers la cible depuis le plan).` };
  return { symbol: plan.symbol, quantite: q, unite: btc ? "BTC" : "actions", prixEntree: r2(e), reference: ref, montant: r2(q * e), perteAuStop: r2(q * risque), gainALaCible: r2(q * (plan.cible - e)),
    stop: plan.stop, cible: plan.cible, limitante: qui[0], limites: Object.fromEntries(Object.entries(lim).map(([k, v]) => [k, Math.round(v * 1e4) / 1e4])) };
}

// ------------------------------------------------------------- 5. contrôle du risque (trader-risk)
export function risque(plan, ordre, reglages = REGLAGES_DEFAUT, maintenantMs = Date.now(), journal = []) {
  const btc = estBtc(plan.symbol); const m = marcheDe(plan.symbol); const now = local(maintenantMs, m);
  const regles = [];
  const ok = (nom, passe, detail) => regles.push({ nom, passe, detail });
  if (ordre.erreur) { ok("taille", false, ordre.erreur); return { verdict: "BLOQUÉ", regles }; }
  const bloques = (reglages.blocked || []).map((x) => String(x).toUpperCase());
  ok("liste noire", !bloques.includes(plan.symbol.toUpperCase()), bloques.includes(plan.symbol.toUpperCase()) ? "ce symbole est sur ta liste noire" : "pas sur ta liste noire");
  ok("taille", ordre.montant >= reglages.min_order_usd && ordre.montant <= reglages.max_order_usd + 0.005, `${ordre.montant} $ (min ${reglages.min_order_usd}, max ${reglages.max_order_usd})`);
  ok("position", ordre.montant <= reglages.budget * reglages.max_position_pct / 100 + 0.005, `${(100 * ordre.montant / reglages.budget).toFixed(1)} % du compte (max ${reglages.max_position_pct} %)`);
  const dispo = reglages.budget * (1 - reglages.cash_buffer_pct / 100);
  ok("liquidités", ordre.montant <= dispo + 0.005, `${ordre.montant} $ sur ${dispo.toFixed(2)} $ disponibles (tampon ${reglages.cash_buffer_pct} % gardé)`);
  ok("stop", plan.stop > 0 && plan.stop < ordre.prixEntree, `stop ${plan.stop} sous l'entrée ${ordre.prixEntree}`);
  ok("perte", ordre.perteAuStop <= reglages.max_loss_per_trade_usd + 0.005, `${ordre.perteAuStop} $ au stop (max ${reglages.max_loss_per_trade_usd} $)`);
  const rr = (plan.cible - ordre.prixEntree) / (ordre.prixEntree - plan.stop);
  ok("rendement/risque", rr >= reglages.min_reward_risk - 1e-9, `${rr.toFixed(2)} (min ${reglages.min_reward_risk})`);
  const duJour = journal.filter((j) => j.date === now.date);
  const perteJour = duJour.reduce((a, j) => a + (j.perteMax || 0), 0) + ordre.perteAuStop;
  ok("perte du jour", perteJour <= reglages.max_daily_loss_usd + 0.005, `${perteJour.toFixed(2)} $ en comptant les trades notés aujourd'hui (max ${reglages.max_daily_loss_usd} $)`);
  ok("trades du jour", duJour.length < reglages.max_trades_per_day, `${duJour.length} trade(s) noté(s) aujourd'hui (max ${reglages.max_trades_per_day})`);
  if (btc) ok("fenêtre", true, "le BTC se traite 24 h/24");
  else {
    const se = seance(now.date, m);
    const avant = lireHeure(reglages.no_entries_before); let apres = lireHeure(reglages.no_entries_after);
    if (NYSE_FERMETURE_13H[now.date]) apres -= 180;
    if (!se) ok("fenêtre", false, `marché fermé aujourd'hui (${jourOuvre(now.date, m)[1]})`);
    else if (plan.jour !== now.date) ok("fenêtre", false, `le plan date du ${plan.jour}, pas d'aujourd'hui (${now.date})`);
    else ok("fenêtre", now.min >= avant && now.min <= apres, `il est ${hhmm(now.min)} à New York (entrées de ${hhmm(avant)} à ${hhmm(apres)})`);
  }
  return { verdict: regles.every((r) => r.passe) ? "OK" : "BLOQUÉ", regles };
}

export async function parcours(q, reglages, journal) {
  const sym = (q.symbol || "").trim().toUpperCase(); if (!sym) throw new Error("Donne un symbole (ex. TSLA ou BTC).");
  const now = Date.now();
  const jour = q.jour || jourParDefaut(sym, now);
  const plage = jour === local(now, marcheDe(sym)).date ? "1d" : "60d";
  const s = await graphique(sym, plage, "5m");
  const bars = barres(s, sym, now);
  const out = { symbol: sym, jour, nom: s.meta.longName || s.meta.shortName || sym, dernierPrix: s.meta.regularMarketPrice, devise: s.meta.currency };
  out.entree = entree(bars, sym, jour, now, { setup: q.setup || "orb", minutesRange: +(q.minutesRange || 15), niveau: q.niveau ? +q.niveau : null, reglages });
  const d = out.entree.declenchement;
  if (!d && !q.prixEntree) return out;
  const pe = q.prixEntree ? +q.prixEntree : d.prix;
  const idx = q.prixEntree && q.heureEntree ? (lireHeure(q.heureEntree) - 5 - seance(jour, marcheDe(sym))[0]) / 5 : d ? d.indice : null;
  out.plan = planSortie({ symbol: sym, jour, entree: pe, setup: q.setup || "orb", range: out.entree.range, stop: q.stop || (q.setup === "level" ? "pct:1" : "or-mid"), cible: q.cible || "2R", indice: idx, heure: d ? d.heure : q.heureEntree, reglages, barresJour: bars.filter((b) => b.date === jour) });
  if (out.plan.erreur) return out;
  try { out.tm = await timeMachine(out.plan, { replays: Math.min(+(q.replays || 10000), 50000), graine: +(q.graine || 19), jusqua: q.jusqua ? lireHeure(q.jusqua) : null }); }
  catch (e) { out.tm = { erreur: String(e.message || e) }; }
  out.ordre = taille(out.plan, reglages, out.dernierPrix && jour === local(now, marcheDe(sym)).date ? out.dernierPrix : null);
  out.risque = risque(out.plan, out.ordre, reglages, now, journal);
  return out;
}
