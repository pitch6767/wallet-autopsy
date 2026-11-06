// « Décortiquer » un portefeuille Polymarket BTC Up/Down.
// Méthode inspirée de 0xArchiveIO/0xarchive-quant (licence MIT) : 1) son vrai bilan,
// 2) talent ou chance (signal inversé, côté au hasard, mauvais moment),
// 3) ses règles : ce qui déclenche ses entrées comparé aux moments ordinaires,
// puis une règle candidate et la part de ses trades qu'elle reproduit.
// Tous les tirages sont déterministes (graine = adresse) : le même calcul redonne le même résultat.

import { chargerMarches } from "./etude.js";

const DATA = "https://data-api.polymarket.com";
const GAMMA = "https://gamma-api.polymarket.com";
const DUREE = { "5m": 300, "15m": 900 };
const N_TIRAGES = 500;
const MAX_SES_MARCHES = 50, MAX_AUTRES = 30, MOMENTS_PAR_MARCHE = 5, PAS_SCAN = 5;
const CACHE_S = 6 * 3600;
const VERSION = 3; // un résultat gardé en mémoire par une version plus ancienne est recalculé

// ─── outils ───
const usd = (x) => (x < 0 ? "−" : "") + "$" + Math.abs(x).toLocaleString("fr-CH", { maximumFractionDigits: Math.abs(x) >= 100 ? 0 : 2 });
const pc = (x) => (x == null || !isFinite(x) ? "—" : x === 0 ? "0 %" : (Math.abs(x) < 0.1 ? (x * 100).toFixed(1).replace(".", ",") : Math.round(x * 100)) + " %");
const px = (x) => (x == null ? "—" : x.toFixed(2).replace(".", ",") + " $");
const dur = (s) => { if (s == null) return "—"; const a = Math.abs(s); return a < 60 ? Math.round(a) + " s" : a < 3600 ? Math.round(a / 60) + " min" : (a / 3600).toFixed(1) + " h"; };
const pct = (x, d = 3) => (x == null ? "—" : Math.abs(x) < 0.5 * 10 ** -d ? (0).toFixed(d).replace(".", ",") + " %" : (x >= 0 ? "+" : "−") + Math.abs(x).toFixed(d).replace(".", ",") + " %");
const q = (a, f) => { if (!a.length) return null; const s = [...a].sort((x, y) => x - y); return s[Math.min(s.length - 1, Math.max(0, Math.floor(f * (s.length - 1) + 0.5)))]; };
const med = (a) => q(a, 0.5);
const somme = (a) => a.reduce((x, y) => x + y, 0);
const cts = (x) => (x == null ? "—" : (x >= 0 ? "+" : "−") + Math.abs(Math.round(x * 100)) + " c");
const heureZ = (ts) => Number(new Date(ts * 1000).toLocaleString("en-GB", { hour: "2-digit", hour12: false, timeZone: "Europe/Zurich" }));
const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

function rng(graine) { // mulberry32
  let a = 0;
  for (const c of graine) a = (Math.imul(a, 31) + c.charCodeAt(0)) | 0;
  return () => { a = (a + 0x6d2b79f5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
}

async function getJSON(u) {
  for (let e = 0; ; e++) {
    const r = await fetch(u, { headers: { accept: "application/json", "user-agent": "wallet-autopsy/1.0" } });
    if (r.ok) return r.json();
    if ((r.status === 429 || r.status >= 500) && e < 3) { await new Promise((ok) => setTimeout(ok, 800 * (e + 1))); continue; }
    throw new Error(`${new URL(u).host} a répondu ${r.status}`);
  }
}
async function pool(items, n, fn) {
  const out = new Array(items.length); let i = 0;
  await Promise.all(Array.from({ length: Math.min(n, items.length) }, async () => { while (i < items.length) { const k = i++; try { out[k] = await fn(items[k]); } catch (e) { out[k] = { erreur: String(e.message || e) }; } } }));
  return out;
}

// ─── données de contexte ───
async function prixABattre(type, start) {
  const meta = async (st) => {
    const ev = await getJSON(`${GAMMA}/events?slug=btc-updown-${type}-${st}`);
    const e = ev && ev[0], m = e && e.markets && e.markets[0];
    if (!e) return {};
    let x = e.eventMetadata || (m && m.eventMetadata) || {};
    if (typeof x === "string") { try { x = JSON.parse(x); } catch { x = {}; } }
    return x || {};
  };
  const m0 = await meta(start);
  if (+m0.priceToBeat > 0) return +m0.priceToBeat;
  const m1 = await meta(start - DUREE[type]);
  if (+m1.finalPrice > 0) return +m1.finalPrice;
  return null;
}

async function tradesMarche(cid) {
  const rows = [];
  for (let off = 0; off < 3000; off += 1000) {
    const r = await getJSON(`${DATA}/trades?market=${cid}&limit=1000&offset=${off}&takerOnly=true`);
    if (!Array.isArray(r) || !r.length) break;
    rows.push(...r);
    if (r.length < 1000) break;
  }
  // prix du côté 0 (Up) à chaque trade
  return rows.map((t) => { const p = Number(t.price) || 0; return { ts: Number(t.timestamp) || 0, p0: Number(t.outcomeIndex) === 1 ? 1 - p : p }; })
    .filter((t) => t.ts && t.p0 > 0 && t.p0 < 1).sort((a, b) => a.ts - b.ts);
}
// Dernier prix connu du côté « cote » au plus tard à t (aucune information future)
function prixA(trs, cote, t) {
  let lo = 0, hi = trs.length - 1, k = -1;
  while (lo <= hi) { const m = (lo + hi) >> 1; if (trs[m].ts <= t) { k = m; lo = m + 1; } else hi = m - 1; }
  if (k < 0) return null;
  return cote === 0 ? trs[k].p0 : 1 - trs[k].p0;
}

// Bougies BTC 1 min (Coinbase, sinon Bitstamp). Prix à t = clôture de la dernière minute TERMINÉE avant t.
async function bougies(minutesVoulues) {
  const blocs = [...new Set(minutesVoulues.map((m) => Math.floor(m / 18000) * 18000))];
  const close = new Map();
  let source = "Coinbase";
  await pool(blocs, 6, async (b) => {
    try {
      const r = await getJSON(`https://api.exchange.coinbase.com/products/BTC-USD/candles?granularity=60&start=${new Date(b * 1000).toISOString()}&end=${new Date((b + 18000) * 1000).toISOString()}`);
      for (const c of r) close.set(c[0], c[4]);
    } catch {
      source = "Bitstamp";
      const r = await getJSON(`https://www.bitstamp.net/api/v2/ohlc/btcusd/?step=60&limit=310&start=${b}`);
      for (const c of (r.data && r.data.ohlc) || []) close.set(Number(c.timestamp), Number(c.close));
    }
  });
  return { prix: (t) => { const m = Math.floor(t / 60) * 60 - 60; return close.get(m) ?? close.get(m - 60) ?? null; }, source, n: close.size };
}

// ─── calcul principal ───
export async function decortiquer(env, addr, refaire) {
  addr = String(addr || "").toLowerCase();
  if (!/^0x[0-9a-f]{40}$/.test(addr)) throw new Error("Adresse invalide.");
  try { await env.DB.prepare("CREATE TABLE IF NOT EXISTS decortiques (wallet TEXT PRIMARY KEY, ts INTEGER, json TEXT)").run(); } catch {}
  if (!refaire) {
    const c = await env.DB.prepare("SELECT ts, json FROM decortiques WHERE wallet=?").bind(addr).first();
    if (c && Date.now() / 1000 - c.ts < CACHE_S) { const j = JSON.parse(c.json); if (j.version === VERSION) return { ...j, cache: true }; }
  }
  const { marches: ms, meta } = await chargerMarches(env, addr);
  const out = { adresse: addr, version: VERSION, calcule: Math.floor(Date.now() / 1000), sections: [], limites: [] };
  if (ms.length < 5) {
    out.titre = "Pas assez de marchés BTC résolus";
    out.sections.push({ titre: "Bilan", lignes: [`Seulement ${ms.length} marché(s) BTC résolu(s) dans son historique téléchargeable : impossible de décortiquer sérieusement.`] });
    return out;
  }
  const R = rng(addr);
  bilan(out, ms, meta);
  talent(out, ms, R);
  style(out, ms);
  await regles(out, env, ms, R);
  conclureTalent(out, out._mm || null); delete out._mm;
  out.limites.push("Polymarket ne dit pas s'il attend dans le carnet ou s'il prend le prix affiché, ni ce qu'il fait ailleurs (Binance, autres plateformes) : ces gestes restent invisibles.");
  if (meta.tronque) out.limites.push("Historique limité par Polymarket aux 10 000 derniers trades.");
  try { await env.DB.prepare("INSERT OR REPLACE INTO decortiques (wallet, ts, json) VALUES (?,?,?)").bind(addr, out.calcule, JSON.stringify(out)).run(); } catch {}
  return out;
}

// 1. Son vrai bilan
function bilan(out, ms, meta) {
  const pnl = somme(ms.map((m) => m.pnl)), cout = somme(ms.map((m) => m.cout));
  let cum = 0, haut = 0, creux = 0;
  for (const m of ms) { cum += m.pnl; haut = Math.max(haut, cum); creux = Math.min(creux, cum - haut); }
  const jours = new Map();
  for (const m of ms) { const j = Math.floor(m.ts / 86400); jours.set(j, (jours.get(j) || 0) + m.pnl); }
  const dj = [...jours.values()];
  const moy = somme(dj) / dj.length;
  const j0 = Math.floor(ms[0].ts / 86400), j1 = Math.floor(ms[ms.length - 1].ts / 86400);
  const cal = []; for (let j = j0; j <= j1; j++) cal.push(jours.get(j) || 0); // jours sans trade = 0
  const mc = somme(cal) / cal.length, sd = Math.sqrt(somme(cal.map((x) => (x - mc) ** 2)) / Math.max(1, cal.length - 1));
  // intervalle de confiance du ROI par tirage avec remise des marchés
  const R = rng(out.adresse + "ic"), rois = [];
  for (let k = 0; k < 500; k++) { let p = 0, c = 0; for (let i = 0; i < ms.length; i++) { const m = ms[Math.floor(R() * ms.length)]; p += m.pnl; c += m.cout; } rois.push(p / c); }
  const span = Math.max(1, (ms[ms.length - 1].ts - ms[0].ts) / 86400);
  out.bilan = { marches: ms.length, pnl, cout, roi: pnl / cout, creux, joursActifs: dj.length, gainJour: moy, sharpeJour: sd && cal.length >= 7 ? (mc / sd) * Math.sqrt(365) : null };
  out.titre = `${ms.length} marchés BTC, ${usd(pnl)} (ROI ${pc(pnl / cout)})`;
  out.sections.push({
    titre: "1. Son vrai bilan",
    lignes: [
      `<b>${usd(pnl)}</b> de gain net pour ${usd(cout)} misés sur ${ms.length} marchés BTC résolus, du ${new Date(ms[0].ts * 1000).toLocaleDateString("fr-CH")} au ${new Date(ms[ms.length - 1].ts * 1000).toLocaleDateString("fr-CH")} (${Math.max(1, Math.round(span))} jour${Math.round(span) > 1 ? "s" : ""}) : ROI <b>${pc(pnl / cout)}</b>, intervalle de confiance 95 % de ${pc(q(rois, 0.025))} à ${pc(q(rois, 0.975))}.`,
      `${ms.filter((m) => m.gagne).length} marchés gagnants sur ${ms.length}. Pire creux depuis un sommet : <b>${usd(creux)}</b>. Gain moyen par jour actif : ${usd(moy)} sur ${dj.length} jours` + (out.bilan.sharpeJour != null ? `, ratio de Sharpe annualisé (jours calendaires) ${out.bilan.sharpeJour.toFixed(2).replace(".", ",")}.` : "."),
      (q(rois, 0.025) > 0 ? "Même dans le bas de la fourchette, il reste gagnant." : q(rois, 0.975) < 0 ? "Même dans le haut de la fourchette, il reste perdant." : "La fourchette passe par zéro : son résultat peut encore s'expliquer par la chance.")
        + ` Gain calculé trade par trade avec les prix réellement payés ; d'éventuels frais de preneur facturés en plus ne sont pas visibles dans ces données.` + (meta.nonResolus ? ` ${meta.nonResolus} marchés non résolus ou introuvables sont exclus.` : ""),
    ],
  });
}

// 2. Son style
function style(out, ms) {
  const e = ms.filter((m) => m.e1prix != null);
  const av = e.filter((m) => m.avantFin != null).map((m) => m.avantFin);
  const tr = [[Infinity, 180, "plus de 3 min avant la fin"], [180, 60, "1 à 3 min"], [60, 30, "30 à 60 s"], [30, 10, "10 à 30 s"], [10, 0, "dernières 10 s"], [0, -Infinity, "après la fin"]];
  const repAv = tr.map(([h, b, lib]) => ({ lib, n: av.filter((x) => x <= h && x > b || (b === 0 && x === 0)).length })).filter((x) => x.n);
  const prix = e.map((m) => m.e1prix);
  const trP = [[0, 0.1], [0.1, 0.3], [0.3, 0.5], [0.5, 0.7], [0.7, 0.9], [0.9, 1.01]];
  const repP = trP.map(([a, b]) => ({ lib: `${a.toFixed(1).replace(".", ",")}–${Math.min(b, 1).toFixed(1).replace(".", ",")} $`, n: prix.filter((p) => p >= a && p < b).length })).filter((x) => x.n);
  const up = e.filter((m) => m.e1cote === 0).length;
  const mises = ms.map((m) => m.cout);
  // Renforcements : achats du même côté après le premier
  const ecarts = [], tailles = [];
  let nRenf = 0;
  for (const m of e) {
    const l = m.achats.filter((a) => a.i === m.e1cote).sort((a, b) => a.ts - b.ts);
    if (l.length < 2) continue;
    const t0 = l[0].ts, p0 = m.e1prix;
    const ajouts = l.filter((a) => a.ts > t0 + 10);
    if (!ajouts.length) continue;
    nRenf++;
    let tenu = l.filter((a) => a.ts <= t0 + 10).reduce((x, a) => x + a.sz, 0);
    for (const a of ajouts) { ecarts.push(a.p - p0); tailles.push(tenu ? a.sz / tenu : 1); tenu += a.sz; }
  }
  const deux = ms.filter((m) => m.deux).length, rev = ms.filter((m) => m.revend).length;
  const blocs = [[0, 6, "nuit 0–6 h"], [6, 12, "matin 6–12 h"], [12, 18, "après-midi 12–18 h"], [18, 24, "soir 18–24 h"]]
    .map(([a, b, lib]) => { const l = ms.filter((m) => { const h = heureZ(m.ts); return h >= a && h < b; }); return { lib, n: l.length, p: somme(l.map((m) => m.pnl)) }; }).filter((x) => x.n);
  const types = {}; for (const m of ms) types[m.type] = (types[m.type] || 0) + 1;
  out.style = { avantMed: med(av), av10: q(av, 0.1), av90: q(av, 0.9), prixMed: med(prix), p10: q(prix, 0.1), p90: q(prix, 0.9), partUp: e.length ? up / e.length : null };
  const lignes = [
    `<b>Quand il entre</b> (premier achat) : médiane ${dur(med(av))} avant la fin, 80 % de ses entrées ${q(av, 0.9) - q(av, 0.1) < 5 ? `à ${dur(q(av, 0.1))}` : `entre ${dur(q(av, 0.9))} et ${dur(q(av, 0.1))}`}. Répartition : ${repAv.map((x) => `${x.lib} ${pc(x.n / av.length)}`).join(", ")}.`,
    `<b>À quel prix</b> : médiane ${px(med(prix))}, 80 % entre ${px(q(prix, 0.1))} et ${px(q(prix, 0.9))}. Répartition : ${repP.map((x) => `${x.lib} ${pc(x.n / prix.length)}`).join(", ")}.`,
    `<b>Quel côté</b> : Up ${pc(up / e.length)}, Down ${pc(1 - up / e.length)}` + (Math.max(up, e.length - up) >= 0.65 * e.length ? " : il a un côté préféré, ses gains dépendent donc de la tendance du BTC." : " : pas de côté préféré."),
    `<b>Mises</b> : médiane ${usd(med(mises))} par marché, 90 % sous ${usd(q(mises, 0.9))}.`,
    nRenf
      ? `<b>Renforcements</b> : sur ${nRenf} marchés (${pc(nRenf / e.length)}) il rachète le même côté après son entrée, en médiane à ${(med(ecarts) >= 0 ? "+" : "−") + Math.abs(med(ecarts) * 100).toFixed(0)} centimes de son premier prix (${med(ecarts) > 0.005 ? "il suit le mouvement" : med(ecarts) < -0.005 ? "il moyenne à la baisse" : "au même prix"}), chaque rachat valant en médiane ${pc(med(tailles) || 0)} de ce qu'il tenait déjà.` + (q(ecarts, 0.25) != null && Math.abs(q(ecarts, 0.75) - q(ecarts, 0.25)) < 0.03 && ecarts.length >= 10 ? " Écarts très réguliers : c'est une règle fixe (échelle), pas une habitude." : "")
      : "<b>Renforcements</b> : il ne rachète presque jamais après son entrée.",
    `<b>Autres gestes</b> : il achète les deux côtés sur ${pc(deux / ms.length)} des marchés, revend avant la fin sur ${pc(rev / ms.length)}.`,
    `<b>Heures (Suisse)</b> : ${blocs.map((b) => `${b.lib} ${b.n} marché${b.n > 1 ? "s" : ""} (${usd(b.p)})`).join(", ")}.`,
    `<b>Durées de marché</b> : ${Object.entries(types).map(([t, n]) => `${t} ${n}`).join(", ")}.`,
  ];
  out.sections.push({ titre: "3. Ses règles — son style", lignes });
}

// 3. Talent ou chance : son choix de côté à l'entrée, comparé à trois tirages
function talent(out, ms, R) {
  const e = ms.filter((m) => m.e1prix != null && m.e1prix > 0.005 && m.e1prix < 0.995 && m.avantFin != null && m.avantFin >= 0);
  const lignes = [];
  if (e.length < 20) {
    lignes.push(`Seulement ${e.length} marchés avec une entrée avant la fin : trop peu pour séparer le talent de la chance.`);
    out.sections.push({ titre: "2. Talent ou chance ?", lignes }); out.talent = null; return;
  }
  // Modèle : sa première entrée, mise = tout ce qu'il a misé sur ce marché, gardée jusqu'au résultat
  const g = (cote, prix, gagnant, mise) => (cote === gagnant ? mise * (1 / prix - 1) : -mise);
  const modele = somme(e.map((m) => g(m.e1cote, m.e1prix, m.gagnant, m.cout)));
  const reel = somme(e.map((m) => m.pnl));
  const inverse = somme(e.map((m) => g(1 - m.e1cote, 1 - m.e1prix, m.gagnant, m.cout)));
  let hasardMieux = 0;
  const hs = [];
  for (let k = 0; k < N_TIRAGES; k++) {
    let h = 0;
    for (const m of e) { const c = R() < 0.5 ? 0 : 1; h += g(c, c === m.e1cote ? m.e1prix : 1 - m.e1prix, m.gagnant, m.cout); }
    hs.push(h); if (h >= modele) hasardMieux++;
  }
  const pH = (hasardMieux + 1) / (N_TIRAGES + 1);
  const coutE = somme(e.map((m) => m.cout));
  out.talent = { marches: e.length, modele, reel, inverse, pHasard: pH, pMoment: null };
  out.talentVerdict = modele <= 0 || inverse >= modele || pH > 0.05 ? "chance" : "a_confirmer";
  lignes.push(
    `Test sur ses ${e.length} marchés avec entrée avant la fin, en gardant <b>seulement sa première entrée jusqu'au résultat</b> (mise identique) : ${usd(modele)} (ROI ${pc(modele / coutE)}). Son résultat réel sur ces marchés, avec tout ce qu'il fait ensuite : ${usd(reel)} ; ses gestes après l'entrée ${reel >= modele ? "ajoutent" : "coûtent"} ${usd(Math.abs(reel - modele))}.`,
    `<b>Signal inversé</b> (l'autre côté, au prix complémentaire) : ${usd(inverse)}.`,
    `<b>Côté au hasard</b> (${N_TIRAGES} tirages, mêmes marchés, mêmes mises) : médiane ${usd(med(hs))} ; le hasard fait aussi bien ou mieux que lui dans ${pc(pH)} des tirages.`,
  );
  out.sections.push({ titre: "2. Talent ou chance ?", lignes });
  out._talent = { lignes, modele, inverse, pH }; // le test « mauvais moment » et le verdict sont ajoutés par regles()
}

// Verdict de la partie 2, une fois le test « mauvais moment » fait (ou impossible)
function conclureTalent(out, mm) {
  const T = out._talent; delete out._talent;
  if (!T) return;
  const { modele, inverse, pH } = T;
  if (mm) T.lignes.push(`<b>Mauvais moment</b> (${N_TIRAGES} tirages sur ses ${mm.n} derniers marchés ${mm.type} : ses propres choix de côté, pris dans d'autres fenêtres, appliqués à chaque marché au même instant que son entrée et <b>au vrai prix du jeton à cet instant</b>) : médiane ${usd(mm.med)} contre ${usd(mm.modele)} pour lui (mêmes prix de référence) ; aussi bien ou mieux dans ${pc(mm.p)} des tirages.`);
  else T.lignes.push("<b>Mauvais moment</b> : pas testé, faute de marchés 5 min ou 15 min avec leurs prix minute par minute.");
  if (out.talent) out.talent.pMoment = mm ? mm.p : null;
  let verdict;
  if (modele <= 0) { verdict = "<b>Pas de talent visible à l'entrée</b> : en gardant simplement son premier choix jusqu'au résultat, il perdrait de l'argent."; out.talentVerdict = "chance"; }
  else if (inverse >= modele) { verdict = "<b>Pas de direction</b> : faire l'inverse de lui rapporterait autant."; out.talentVerdict = "chance"; }
  else if (pH > 0.05) { verdict = "<b>Chance probable</b> : des côtés tirés au hasard font aussi bien que lui trop souvent."; out.talentVerdict = "chance"; }
  else if (!mm) { verdict = "<b>Bon choix de côté</b> : il bat le signal inversé et le hasard ; son timing n'a pas pu être testé."; out.talentVerdict = "cote"; }
  else if (mm.p > 0.05) { verdict = "<b>Penchant, pas de timing prouvé</b> : il bat l'inverse et le hasard, mais ses choix de côté pris à d'autres moments font aussi bien trop souvent. Son gain vient surtout de son penchant général (côté ou niveau de prix), pas d'une lecture de chaque marché."; out.talentVerdict = "cote"; }
  else { verdict = "<b>Talent probable</b> : il bat le signal inversé, le hasard et le mauvais moment. Il lit chaque marché au bon moment : ce n'est pas de la chance."; out.talentVerdict = "timing"; }
  T.lignes.push(verdict + " (seuil : 5 %).");
}

// 4. Ses règles : ce qui déclenche ses entrées, puis une règle candidate et sa reproduction
async function regles(out, env, ms, R) {
  const lignes = [];
  const ok = ms.filter((m) => DUREE[m.type] && m.e1prix != null && m.avantFin != null && m.avantFin >= 0).slice(-MAX_SES_MARCHES);
  if (ok.length < 15) {
    lignes.push(`Seulement ${ok.length} marchés 5 min ou 15 min avec une entrée avant la fin : trop peu pour chercher ses règles.`);
    out.sections.push({ titre: "4. Ce qui déclenche ses entrées", lignes }); return;
  }
  const typeP = ok.filter((m) => m.type === "5m").length >= ok.length / 2 ? "5m" : "15m";
  const D = DUREE[typeP];
  const ses = ok.filter((m) => m.type === typeP);
  const deb = Math.min(...ses.map((m) => m.fin)), fin = Math.max(...ses.map((m) => m.fin));
  const pris = new Set(ms.map((m) => m.cid));
  let autres = [];
  try {
    const { results } = await env.DB.prepare("SELECT cid, slug, end_ts, gagnant FROM markets WHERE type=? AND end_ts BETWEEN ? AND ? AND gagnant IS NOT NULL ORDER BY end_ts LIMIT 2000").bind(typeP, deb, fin).all();
    const cand = results.filter((r) => !pris.has(r.cid));
    for (let i = cand.length - 1; i > 0; i--) { const j = Math.floor(R() * (i + 1)); [cand[i], cand[j]] = [cand[j], cand[i]]; } // tirage reproductible (graine = adresse)
    autres = cand.slice(0, MAX_AUTRES).map((r) => ({ cid: r.cid, slug: r.slug, fin: r.end_ts, gagnant: r.gagnant, type: typeP, autre: true }));
  } catch {}
  const tous = [...ses.map((m) => ({ ...m })), ...autres];
  for (const m of tous) m.start = m.fin - D;

  // Contexte : prix à battre officiel, trades du marché, BTC minute par minute
  const ctx = await pool(tous, 8, async (m) => ({ k: await prixABattre(typeP, m.start), trs: await tradesMarche(m.cid) }));
  tous.forEach((m, i) => { const c = ctx[i] || {}; m.k = c.k || null; m.trs = c.trs || []; });
  const minutes = [];
  for (const m of tous) for (let t = m.start - 60; t <= m.fin; t += 60) minutes.push(t);
  let B;
  try { B = await bougies(minutes); } catch (e) { B = { prix: () => null, source: "aucune", n: 0 }; }
  const dist = (m, t) => { const b = B.prix(t); return b && m.k ? ((b - m.k) / m.k) * 100 : null; };

  // Ses entrées
  const E = [];
  for (const m of tous.filter((x) => !x.autre)) {
    const t = m.fin - m.avantFin, d = dist(m, t);
    if (d == null) continue;
    const sd = m.e1cote === 0 ? d : -d;
    const p30 = prixA(m.trs, m.e1cote, t - 30);
    const p0 = prixA(m.trs, m.e1cote, t - 1);
    E.push({ sec: m.avantFin, sd, ad: Math.abs(d), prix: p0, dp30: p0 != null && p30 != null ? p0 - p30 : null, cote: m.e1cote, t: m.fin - m.avantFin, m });
  }
  // Moments ordinaires (mêmes marchés + marchés qu'il n'a pas joués), côté tiré au hasard
  const O = [];
  for (const m of tous) for (let k = 0; k < MOMENTS_PAR_MARCHE; k++) {
    const t = m.start + 5 + Math.floor(R() * (D - 6)), d = dist(m, t);
    if (d == null) continue;
    const c = R() < 0.5 ? 0 : 1, p = prixA(m.trs, c, t), p30 = prixA(m.trs, c, t - 30);
    O.push({ sec: m.fin - t, sd: c === 0 ? d : -d, ad: Math.abs(d), prix: p, dp30: p != null && p30 != null ? p - p30 : null });
  }
  out.regles = { marchesSes: E.length, marchesAutres: autres.length, sourceBTC: B.source, type: typeP };
  // Mauvais moment (test « signal périmé ») : ses choix de côté pris dans D'AUTRES fenêtres, appliqués à ce marché,
  // au même instant que son entrée et au vrai prix du jeton à cet instant. Garde son penchant (Up/Down), casse le lien avec le moment.
  {
    const g = (c, p, gagnant, mise) => (c === gagnant ? mise * (1 / p - 1) : -mise);
    const base = E.filter((x) => x.prix != null && x.prix > 0.01 && x.prix < 0.99);
    if (base.length >= 15) {
      const pxCote = (x, c) => { if (c === x.cote) return x.prix; const p = prixA(x.m.trs, c, x.t - 1); return p != null && p > 0.01 && p < 0.99 ? p : 1 - x.prix; };
      const mod = somme(base.map((x) => g(x.cote, x.prix, x.m.gagnant, x.m.cout)));
      const tir = []; let mieux = 0;
      for (let k = 0; k < N_TIRAGES; k++) {
        const cotes = base.map((x) => x.cote);
        for (let i = cotes.length - 1; i > 0; i--) { const j = Math.floor(R() * (i + 1)); [cotes[i], cotes[j]] = [cotes[j], cotes[i]]; }
        let s = 0;
        base.forEach((x, i) => { s += g(cotes[i], pxCote(x, cotes[i]), x.m.gagnant, x.m.cout); });
        tir.push(s); if (s >= mod) mieux++;
      }
      out._mm = { n: base.length, type: typeP, modele: mod, med: med(tir), p: (mieux + 1) / (N_TIRAGES + 1) };
    }
  }
  if (E.length < 15) {
    lignes.push(`Contexte BTC trouvé pour seulement ${E.length} de ses marchés (source ${B.source}) : trop peu pour chercher ses règles.`);
    out.sections.push({ titre: "4. Ce qui déclenche ses entrées", lignes }); return;
  }
  const fav = E.filter((x) => x.sd > 0).length / E.length;
  const favO = O.filter((x) => x.sd > 0).length / O.length;
  const v = (l, k) => l.map((x) => x[k]).filter((x) => x != null);
  const lignesT = [
    ["Secondes avant la fin", dur(med(v(E, "sec"))), dur(med(v(O, "sec")))],
    ["Achète le côté que le BTC favorise déjà", pc(fav), pc(favO)],
    ["Écart du BTC au prix à battre, vers son côté", pct(med(v(E, "sd"))), pct(med(v(O, "sd")))],
    ["Écart du BTC au prix à battre (taille)", pct(med(v(E, "ad"))).replace("+", ""), pct(med(v(O, "ad"))).replace("+", "")],
    ["Prix du jeton juste avant (dernier trade)", px(med(v(E, "prix"))), px(med(v(O, "prix")))],
    ["Variation du jeton dans les 30 s avant", cts(med(v(E, "dp30"))), cts(med(v(O, "dp30")))],
  ];
  lignes.push(`Ses ${E.length} dernières entrées sur les marchés ${typeP}, comparées à ${O.length} moments ordinaires tirés au hasard (sur ses marchés et sur ${autres.length} marchés qu'il n'a pas joués, côté tiré au hasard). Prix à battre officiel Polymarket ; BTC minute par minute (${B.source}, dernière minute terminée avant l'instant, donc sans information future).`);
  out.sections.push({ titre: "4. Ce qui déclenche ses entrées", lignes, table: { cols: ["", "Lui, à l'entrée (médiane)", "Moments ordinaires (médiane)"], rows: lignesT } });

  // Règle candidate : construite sur la moitié la plus ancienne de ses entrées, jugée sur la plus récente (jamais vue)
  E.sort((a, b) => a.t - b.t);
  const Eb = E.slice(0, Math.ceil(E.length / 2)), recents = new Set(E.slice(Math.ceil(E.length / 2)).map((x) => x.m.cid));
  const s10 = q(v(Eb, "sec"), 0.1), s90 = q(v(Eb, "sec"), 0.9), p10 = q(v(Eb, "prix"), 0.05), p90 = q(v(Eb, "prix"), 0.95);
  const favB = Eb.filter((x) => x.sd > 0).length / Eb.length;
  let modeCote = null, dMin = 0;
  if (favB >= 0.65) { modeCote = "favori"; dMin = q(Eb.filter((x) => x.sd > 0).map((x) => x.ad), 0.1) || 0; }
  else if (favB <= 0.35) { modeCote = "contre"; dMin = q(Eb.filter((x) => x.sd < 0).map((x) => x.ad), 0.1) || 0; }
  else { const up = Eb.filter((x) => x.cote === 0).length / Eb.length; if (up >= 0.65) modeCote = "up"; else if (up <= 0.35) modeCote = "down"; }
  const l2 = [];
  if (!modeCote) {
    l2.push(`<b>Aucune règle simple trouvée</b> : dans la moitié ancienne de ses entrées, il achète le côté favorisé par le BTC dans ${pc(favB)} des cas (contre ${pc(favO)} au hasard) et n'a pas de côté préféré. ` + (out.talentVerdict === "chance" ? "Avec le verdict de la partie 2, son choix de côté ressemble à du hasard." : "Pourtant la partie 2 montre un vrai avantage sur le hasard : il s'appuie sur quelque chose que ces données ne montrent pas (carnet d'ordres, autres plateformes, information plus rapide)."));
    out.sections.push({ titre: "5. Sa règle probable et ce qu'elle reproduit", lignes: l2 }); return;
  }
  const libCote = { favori: `le côté que le BTC favorise déjà, quand l'écart au prix à battre dépasse ${dMin.toFixed(3).replace(".", ",")} %`, contre: `le côté contre le BTC, quand l'écart au prix à battre dépasse ${dMin.toFixed(3).replace(".", ",")} %`, up: "toujours Up", down: "toujours Down" }[modeCote];
  const quand = s90 - s10 < 5 ? `À ${dur(s10)} de la fin` : `Entre ${dur(s90)} et ${dur(s10)} avant la fin`;
  const regle = `${quand}, acheter ${libCote}, si le jeton coûte entre ${px(p10)} et ${px(p90)}. Une seule entrée par marché, gardée jusqu'au résultat.`;
  const declenche = (m) => {
    for (let t = Math.max(m.start + 5, m.fin - s90); t <= m.fin - s10; t += PAS_SCAN) {
      const d = dist(m, t);
      let c;
      if (modeCote === "up") c = 0; else if (modeCote === "down") c = 1;
      else { if (d == null || Math.abs(d) < dMin || d === 0) continue; c = (d > 0) === (modeCote === "favori") ? 0 : 1; }
      const p = prixA(m.trs, c, t);
      if (p == null || p < p10 || p > p90) continue;
      return { c, p, t };
    }
    return null;
  };
  let meme = 0, oppose = 0, rien = 0, nS = 0, firesA = 0, pnlR = 0, coutR = 0, nR = 0;
  for (const m of tous) {
    if (!m.trs.length || (modeCote !== "up" && modeCote !== "down" && !m.k)) continue;
    const f = declenche(m);
    if (!m.autre) { if (!recents.has(m.cid)) continue; nS++; if (!f) rien++; else if (f.c === m.e1cote) meme++; else oppose++; }
    else if (f) firesA++;
    if (f) { nR++; coutR += 1; pnlR += f.c === m.gagnant ? 1 / f.p - 1 : -1; }
  }
  const nA = tous.filter((m) => m.autre && m.trs.length).length;
  out.regles.regle = regle;
  out.regles.reproduction = { memeCote: nS ? meme / nS : null, autreCote: nS ? oppose / nS : null, rien: nS ? rien / nS : null, declencheAilleurs: nA ? firesA / nA : null, roi: coutR ? pnlR / coutR : null, n: nR };
  l2.push(`<b>Règle candidate</b> (écrite à partir de la moitié la plus ancienne de ses entrées, 1 seul essai) : ${regle}`);
  l2.push(`<b>Ce qu'elle reproduit</b> sur ses ${nS} marchés les plus récents (jamais utilisés pour l'écrire) : même côté que lui <b>${meme} fois (${pc(meme / nS)})</b>, côté opposé ${oppose} fois, ne se déclenche pas ${rien} fois.`
    + (meme / nS >= 0.7 ? " Elle colle bien à sa façon de faire." : meme / nS >= 0.4 ? " Elle explique une partie de ses choix, pas tout." : " Elle n'explique pas ses choix : il utilise autre chose."));
  if (nA) l2.push(`Sur ${nA} marchés qu'il n'a <b>pas</b> joués, la règle se déclenche dans ${pc(firesA / nA)} des cas` + (firesA / nA > 0.5 ? " : il est bien plus sélectif que la règle, il filtre avec quelque chose d'invisible ici." : "."));
  if (nR >= 10) l2.push(`Résultat fantôme de la règle (1 $ par marché, prix du dernier trade à l'instant du signal, sans écart ni frais en plus) : ROI <b>${pc(pnlR / coutR)}</b> sur ${nR} déclenchements. Avant toute décision, elle doit passer les 6 marches de vérification (étude fantôme complète).`);
  out.sections.push({ titre: "5. Sa règle probable et ce qu'elle reproduit", lignes: l2 });
  out.limites.push(`Contexte calculé sur ses ${E.length} dernières entrées ${typeP} au maximum, BTC à la minute (${B.source}) : un trader qui réagit à la seconde est vu avec un léger retard.`);
}
