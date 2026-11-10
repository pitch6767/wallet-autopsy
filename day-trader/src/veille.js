// Nouvelles en direct : le flux des dépôts 8-K de la SEC, lu toutes les 5 secondes.
// Un 8-K est la façon officielle dont une société cotée annonce un événement important
// (résultats 2.02, départ ou arrivée d'un dirigeant 5.02, accord important 1.01, rachat 2.01…).
// On note le prix au moment de la nouvelle, puis on suit : si la tendance part, achat papier.
import { graphique } from "./donnees.js";
import { local, seance, MARCHES, versUtc, jourOuvre, hhmm } from "./temps.js";
import { GLISSEMENT } from "./regles.js";

export const ITEMS = {
  "1.01": "accord important", "1.02": "fin d'un accord important", "1.03": "faillite", "2.01": "achat ou vente d'actifs",
  "2.02": "résultats", "2.03": "nouvelle dette", "2.05": "restructuration", "2.06": "dépréciation", "3.01": "risque de radiation de la cote",
  "3.02": "émission d'actions", "4.01": "changement d'auditeur", "4.02": "comptes à corriger", "5.01": "changement de contrôle",
  "5.02": "départ ou arrivée d'un dirigeant", "5.03": "statuts modifiés", "5.07": "vote des actionnaires", "7.01": "communication (Reg FD)",
  "8.01": "autre événement", "9.01": "documents joints",
};
export const SEUILS = [0.5, 1]; // Pitch 10.11 : pas plus de 1 %, après c'est trop tard // % de hausse depuis le prix de la nouvelle qui « lance la tendance »

// Pitch 11.11 : toutes les news ne font pas bouger -> on classe chaque news par type et on mesure, type par type.
// Règle « news choisies » : achat (hausse de 1 % dans les 30 min) seulement si, sur les news PASSÉES du même type
// (au moins 10, actions à 1 $ ou plus), la hausse max moyenne en 30 min est d'au moins 2 % et le mouvement moyen à 60 min est positif.
export const CHOIX = { min: 10, max30: 2, m60: 0 };
export function categorie(n) {
  if (n.source === "prnewswire") {
    const t = n.titre || "";
    const c = /\bFDA\b|approv|clearance|phase [123]|clinical|trial/i.test(t) ? "santé / FDA" : /acqui|merger|to be acquired|buyout|takeover/i.test(t) ? "rachat / fusion"
      : /results|earnings|quarter|\bQ[1-4]\b|revenue/i.test(t) ? "résultats" : /offering|private placement|pricing of/i.test(t) ? "émission d'actions"
      : /dividend|buyback|repurchase/i.test(t) ? "dividende / rachat d'actions" : /contract|award|partnership|agreement|order|collaborat/i.test(t) ? "contrat / partenariat" : "autre communiqué";
    return "PR Newswire · " + c;
  }
  const it = (n.items || "").split(",");
  for (const k of ["1.03", "2.02", "2.01", "1.01", "3.02", "5.02", "2.05", "4.02", "7.01", "8.01"]) if (it.includes(k)) return `8-K · ${ITEMS[k]}`;
  return "8-K · " + (it.filter((x) => x && x !== "9.01").map((x) => ITEMS[x] || x).join(" + ") || "autre");
}
function statsCategories(hist, avant) {
  const m = {};
  for (const h of hist) { if (avant != null && h.quand >= avant) continue; const c = categorie(h); const x = (m[c] = m[c] || { categorie: c, nb: 0, s30: 0, s60: 0, n60: 0, fort2: 0 }); x.nb++; x.s30 += h.max30; if (h.max30 >= 2) x.fort2++; if (h.m60 != null) { x.s60 += h.m60; x.n60++; } }
  for (const x of Object.values(m)) { x.max30 = +(x.s30 / x.nb).toFixed(2); x.m60 = x.n60 ? +(x.s60 / x.n60).toFixed(2) : null; x.choisie = x.nb >= CHOIX.min && x.max30 >= CHOIX.max30 && x.m60 != null && x.m60 > CHOIX.m60; }
  return m;
}
const HIST = "SELECT source, titre, items, quand, max30, m60 FROM news WHERE fini = 1 AND max30 IS NOT NULL AND prix0 >= 1";

const FLUX = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=8-K&company=&dateb=&owner=include&start=0&count=40&output=atom";
const dec = (s) => String(s || "").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&amp;/g, "&").replace(/&quot;/g, '"').replace(/&#39;/g, "'");

export function lireFlux(xml) {
  const out = [];
  for (const e of xml.split("<entry>").slice(1)) {
    const titre = dec((/<title>([\s\S]*?)<\/title>/.exec(e) || [])[1] || "");
    const cik = (/\((\d{10})\)/.exec(titre) || [])[1];
    const acc = (/accession-number=([\d-]+)/.exec(e) || [])[1];
    const lien = (/<link[^>]*href="([^"]+)"/.exec(e) || [])[1];
    const quand = Date.parse((/<updated>([^<]+)<\/updated>/.exec(e) || [])[1] || "");
    const resume = dec((/<summary[^>]*>([\s\S]*?)<\/summary>/.exec(e) || [])[1] || "");
    const items = [...new Set([...resume.matchAll(/Item\s+(\d\.\d\d)/g)].map((m) => m[1]))];
    const forme = (/term="([^"]+)"/.exec(e) || [])[1] || "";
    if (!cik || !acc || !/^8-K/.test(forme || titre)) continue;
    out.push({ id: acc, cik, nom: titre.replace(/^8-K\S*\s*-\s*/, "").replace(/\s*\(\d{10}\).*$/, ""), lien, quand, items });
  }
  return out;
}

// Prix des actions tokenisées 24 h/24 : Hyperliquid (marchés « xyz ») et Kraken (perpétuels xStocks)
export async function prixTokens() {
  const out = { hl: {}, kf: {} };
  try {
    const r = await fetch("https://api.hyperliquid.xyz/info", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ type: "allMids", dex: "xyz" }) });
    const j = await r.json(); for (const [k, v] of Object.entries(j || {})) if (k.startsWith("xyz:")) out.hl[k.slice(4)] = +v;
  } catch (e) {}
  try {
    const j = await (await fetch("https://futures.kraken.com/derivatives/api/v3/tickers")).json();
    for (const t of j.tickers || []) { const m = /^PF_([A-Z]+)XUSD$/.exec(t.symbol || ""); if (m && t.markPrice) out.kf[m[1]] = +t.markPrice; }
  } catch (e) {}
  return out;
}

const PRN = "https://www.prnewswire.com/rss/news-releases-list.rss";
const BOURSE = /\((?:NYSE American|NYSE|NASDAQ|Nasdaq|AMEX|Cboe)\s*:\s*([A-Z]{1,5}(?:\.[A-Z])?)\)/g;
export function lirePrn(xml) {
  const out = [];
  for (const it of xml.split("<item>").slice(1)) {
    const g = (b) => dec(((new RegExp(`<${b}[^>]*>([\\s\\S]*?)</${b}>`)).exec(it) || [])[1] || "").replace(/<!\[CDATA\[|\]\]>/g, "").trim();
    const titre = g("title"), lien = g("link"), desc = g("description"), quand = Date.parse(g("pubDate"));
    const syms = [...new Set([...(titre + " " + desc).matchAll(BOURSE)].map((m) => m[1].replace(".", "-")))];
    if (!lien || !syms.length) continue;
    out.push({ id: "prn:" + lien.replace(/^https?:\/\/[^/]+/, "").slice(0, 180), titre, lien, quand, syms });
  }
  return out;
}

export class Veilleur {
  constructor(state, env) { this.state = state; this.env = env; this.s = state.storage; }
  async fetch(req) {
    const u = new URL(req.url);
    if (u.pathname === "/demarrer") { const a = await this.s.getAlarm(); if (!a) await this.s.setAlarm(Date.now() + 1000); return Response.json({ alarme: a || "posée" }); }
    if (u.pathname === "/etat") return Response.json({ dernierTour: await this.s.get("dernierTour"), erreur: await this.s.get("erreur"), erreurPrn: await this.s.get("erreurPrn"), alarme: await this.s.getAlarm() });
    return new Response("?", { status: 404 });
  }
  async alarm() {
    try { await this.tour(); await this.s.delete("erreur"); }
    catch (e) { await this.s.put("erreur", { quand: new Date().toISOString(), texte: String(e.message || e) }); }
    try { await this.tourPrn(); await this.s.delete("erreurPrn"); }
    catch (e) { await this.s.put("erreurPrn", { quand: new Date().toISOString(), texte: String(e.message || e) }); }
    await this.s.setAlarm(Date.now() + 5000);
  }
  async ua() { const l = await this.env.DB.prepare("SELECT valeur FROM config WHERE cle = 'contact_sec'").first(); return l ? l.valeur : ""; }
  async tickers(ua) {
    let t = await this.s.get("tickers");
    if (!t || Date.now() - t.le > 864e5) {
      const r = await fetch("https://www.sec.gov/files/company_tickers.json", { headers: { "User-Agent": ua } });
      if (r.status !== 200) throw new Error("liste des tickers SEC : HTTP " + r.status);
      const j = await r.json(); const m = {};
      for (const v of Object.values(j)) { const c = String(v.cik_str).padStart(10, "0"); if (!m[c]) m[c] = String(v.ticker).toUpperCase(); }
      t = { le: Date.now(), m }; await this.s.put("tickers", t);
    }
    return t.m;
  }
  async tour() {
    const ua = await this.ua(); if (!ua) throw new Error("pas de contact SEC");
    const r = await fetch(FLUX, { headers: { "User-Agent": ua, Accept: "application/atom+xml" } });
    if (r.status !== 200) throw new Error("flux 8-K : HTTP " + r.status);
    const ent = lireFlux(await r.text());
    const vus = new Set((await this.s.get("vus")) || []);
    const nouveaux = ent.filter((e) => !vus.has(e.id));
    await this.s.put("dernierTour", { quand: new Date().toISOString(), lus: ent.length, nouveaux: nouveaux.length });
    if (!nouveaux.length) return;
    const tk = await this.tickers(ua);
    const a = nouveaux.map((e) => ({ id: e.id, sym: tk[e.cik], cik: e.cik, nom: e.nom, quand: e.quand, items: e.items.join(","), lien: e.lien, source: "sec", titre: "8-K" }));
    nouveaux.forEach((e) => vus.add(e.id));
    await this.enregistrer(a.filter((x) => x.sym));
    await this.s.put("vus", [...vus].slice(-800));
  }
  async tourPrn() {
    const r = await fetch(PRN, { headers: { "User-Agent": "Mozilla/5.0 (compatible; day-trader-app)" } });
    if (r.status !== 200) throw new Error("PR Newswire : HTTP " + r.status);
    const ent = lirePrn(await r.text());
    const vus = new Set((await this.s.get("vusPrn")) || []);
    const nouveaux = ent.filter((e) => !vus.has(e.id)); nouveaux.forEach((e) => vus.add(e.id));
    await this.s.put("vusPrn", [...vus].slice(-800));
    const premierTour = !(await this.s.get("prnPret")); if (premierTour) { await this.s.put("prnPret", 1); return; } // pas d'ancien stock au démarrage
    await this.enregistrer(nouveaux.flatMap((e) => e.syms.slice(0, 2).map((sym) => ({ id: e.id + "|" + sym, sym, cik: null, nom: "", quand: e.quand || Date.now(), items: "", lien: e.lien, source: "prnewswire", titre: e.titre.slice(0, 300) }))));
  }
  async enregistrer(liste) {
    if (!liste.length) return;
    const vu = Date.now(); const tok = await prixTokens(); const st = [];
    for (const e of liste) {
      let prix0 = null, enSeance = 0, debut = e.quand;
      try { const s = await graphique(e.sym, "1d", "1m"); prix0 = s.meta.regularMarketPrice ?? null; } catch (x) { continue; } // symbole inconnu de Yahoo
      const l = local(e.quand, MARCHES.actions); const se = seance(l.date, MARCHES.actions);
      if (se && l.min >= se[0] && l.min < se[1]) enSeance = 1; else debut = prochaineOuverture(e.quand);
      st.push(this.env.DB.prepare("INSERT OR IGNORE INTO news (id, cik, sym, nom, quand, items, lien, en_seance, prix0, debut_suivi, maj, source, titre, vu, hl0, kf0) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)")
        .bind(e.id, e.cik, e.sym, e.nom, e.quand, e.items, e.lien, enSeance, prix0, debut, new Date().toISOString(), e.source, e.titre, vu, tok.hl[e.sym] ?? null, tok.kf[e.sym] ?? null));
    }
    if (st.length) await this.env.DB.batch(st);
  }
}

export function prochaineOuverture(ms) {
  const m = MARCHES.actions; let l = local(ms, m); let d = l.date;
  const se = seance(d, m); if (se && l.min < se[0]) return versUtc(d, se[0], m);
  for (let i = 0; i < 10; i++) { d = new Date(Date.parse(d + "T12:00:00Z") + 864e5).toISOString().slice(0, 10); if (jourOuvre(d, m)[0]) return versUtc(d, m.ouverture, m); }
  return ms;
}

// Suivi (chaque minute) : mouvements à +5/+15/+60 min et trades papier « news » si la tendance part
export async function photosJetons(env, maintenantMs = Date.now()) {
  const db = env.DB;
  const l = (await db.prepare(`SELECT id, sym, quand, debut_suivi, hl0, kf0, hl5, hl15, hl60, hlouv, kf5, kf15, kf60, kfouv FROM news
    WHERE quand >= ? AND (hl0 IS NOT NULL OR kf0 IS NOT NULL) AND (hl60 IS NULL OR hlouv IS NULL OR kf60 IS NULL OR kfouv IS NULL) LIMIT 200`).bind(maintenantMs - 4 * 864e5).all()).results;
  const dues = []; 
  for (const n of l) for (const [col, t] of [["5", n.quand + 5 * 60e3], ["15", n.quand + 15 * 60e3], ["60", n.quand + 60 * 60e3], ["ouv", n.debut_suivi]])
    for (const src of ["hl", "kf"]) if (n[src + "0"] != null && n[src + col] == null && maintenantMs >= t && maintenantMs < t + 10 * 60e3) dues.push([n, src + col, src]);
  if (!dues.length) return 0;
  const tok = await prixTokens(); const st = [];
  for (const [n, col, src] of dues) { const v = tok[src][n.sym]; if (v != null) st.push(db.prepare(`UPDATE news SET ${col} = ? WHERE id = ?`).bind(v, n.id)); }
  if (st.length) await db.batch(st);
  return st.length;
}

export async function suiviNews(env, maintenantMs = Date.now()) {
  const db = env.DB;
  const ouverts = (await db.prepare("SELECT * FROM news WHERE fini = 0 AND prix0 IS NOT NULL AND debut_suivi <= ? AND debut_suivi >= ? ORDER BY quand LIMIT 40").bind(maintenantMs - 60e3, maintenantMs - 3 * 864e5).all()).results;
  const st = []; let traites = 0;
  const hist = ouverts.length ? (await db.prepare(HIST).all()).results : [];
  for (const n of ouverts) {
    let s; try { s = await graphique(n.sym, "5d", "1m"); } catch (e) { continue; }
    traites++;
    const t = s.t; const pts = [];
    for (let i = 0; i < t.length; i++) if (s.c[i] != null && t[i] * 1000 >= n.debut_suivi) pts.push({ ms: t[i] * 1000, o: s.o[i], h: s.h[i], l: s.l[i], c: s.c[i] });
    if (!pts.length) continue;
    const a = (min) => { const p = pts.find((x) => x.ms >= n.debut_suivi + min * 60e3); return p ? (p.c / n.prix0 - 1) * 100 : null; };
    const fen30 = pts.filter((x) => x.ms < n.debut_suivi + 30 * 60e3);
    const max30 = fen30.length ? (Math.max(...fen30.map((x) => x.h)) / n.prix0 - 1) * 100 : null;
    const m60 = a(60);
    // trades papier : seuil franchi dans les 30 min -> achat à l'ouverture de la minute suivante
    const date = local(n.debut_suivi, MARCHES.actions).date; const se = seance(date, MARCHES.actions);
    const finMs = versUtc(date, se ? se[1] - 5 : 955, MARCHES.actions); // sortie au plus tard 15 h 55
    const cat = categorie(n); const sc = statsCategories(hist, n.quand)[cat];
    const regles = SEUILS.map((x) => [x, `news-${x}`]); if (sc && sc.choisie) regles.push([1, "news-choisies"]);
    for (const [seuil, rid] of regles) {
      if (n.prix0 < 1) continue; // Pitch 11.11 : pas d'achat sur les actions à moins de 1 $
      const i = pts.findIndex((x) => x.ms < n.debut_suivi + 30 * 60e3 && x.c >= n.prix0 * (1 + seuil / 100));
      if (i < 0 || !pts[i + 1]) continue;
      const entree = pts[i + 1].o * (1 + GLISSEMENT);
      const basDepuis = Math.min(...pts.slice(0, i + 1).map((x) => x.l));
      let stop = Math.min(basDepuis, n.prix0); // plus d'arrondi au centime (AITX à 0,0005 $ donnait stop = 0)
      if (entree - stop < entree * 0.003) stop = entree * 0.997; // stop d'au moins 0,3 %
      const cible = entree + 2 * (entree - stop);
      let sortie = null, issue = null, j = i + 1;
      for (j = i + 1; j < pts.length && pts[j].ms <= finMs; j++) {
        const b = pts[j];
        if (j > i + 1 && b.o <= stop) { sortie = b.o * (1 - GLISSEMENT); issue = "stop"; break; }
        if (j > i + 1 && b.o >= cible) { sortie = b.o; issue = "cible"; break; }
        if (b.l <= stop) { sortie = stop * (1 - GLISSEMENT); issue = "stop"; break; }
        if (b.h >= cible) { sortie = cible; issue = "cible"; break; }
      }
      let statut = "ferme";
      if (sortie == null) { const der = pts[Math.min(j, pts.length) - 1]; sortie = der.c; if (maintenantMs < finMs + 5 * 60e3) { statut = "ouvert"; issue = "en cours"; } else issue = "fin de séance"; }
      const hm = (ms) => hhmm(local(ms, MARCHES.actions).min);
      st.push(db.prepare("INSERT OR REPLACE INTO papier VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)").bind(date, rid, n.sym, statut, hm(pts[i + 1].ms), entree, stop, cible, statut === "ferme" ? hm(pts[Math.min(j, pts.length - 1)].ms) : null, sortie, issue + " · " + cat, (sortie - entree) / entree, (sortie - entree) / (entree - stop), new Date(maintenantMs).toISOString()));
    }
    const fini = maintenantMs > Math.max(n.debut_suivi + 65 * 60e3, finMs + 5 * 60e3) ? 1 : 0;
    st.push(db.prepare("UPDATE news SET m5 = ?, m15 = ?, m60 = ?, max30 = ?, fini = ?, maj = ? WHERE id = ?").bind(a(5), a(15), m60, max30, fini, new Date(maintenantMs).toISOString(), n.id));
  }
  if (st.length) await db.batch(st);
  return { suivis: traites };
}

export async function statsNews(db) {
  const l = (await db.prepare("SELECT * FROM news ORDER BY COALESCE(vu, quand) DESC LIMIT 600").all()).results;
  const parItem = {};
  for (const n of l) for (const it of (n.items || "").split(",").filter((x) => x && x !== "9.01")) {
    const p = (parItem[it] = parItem[it] || { item: it, nom: ITEMS[it] || "", nb: 0, avec15: 0, somme15: 0, hausses30: 0 });
    p.nb++; if (n.m15 != null) { p.avec15++; p.somme15 += Math.abs(n.m15); } if (n.max30 != null && n.max30 >= 1) p.hausses30++;
  }
  // Course : même société, annonce vue par deux sources à moins de 2 h d'écart -> qui l'a eue en premier ?
  const parSym = {}; for (const n of l) if (n.vu) (parSym[n.sym] = parSym[n.sym] || []).push(n);
  const paires = [];
  for (const arr of Object.values(parSym)) for (const a of arr) if (a.source === "prnewswire") {
    const b = arr.filter((x) => x.source === "sec" && Math.abs(x.vu - a.vu) < 2 * 3600e3).sort((x, y) => Math.abs(x.vu - a.vu) - Math.abs(y.vu - a.vu))[0];
    if (b) paires.push({ sym: a.sym, titre: a.titre, prn: a.vu, sec: b.vu, premier: a.vu <= b.vu ? "PR Newswire" : "SEC 8-K", avanceSec: Math.round(Math.abs(a.vu - b.vu) / 1000) });
  }
  const course = { paires: paires.length, prnPremier: paires.filter((p) => p.premier === "PR Newswire").length, secPremier: paires.filter((p) => p.premier === "SEC 8-K").length,
    avanceMediane: paires.length ? paires.map((p) => p.avanceSec).sort((a, b) => a - b)[Math.floor(paires.length / 2)] : null, exemples: paires.slice(0, 20) };
  const parCategorie = Object.values(statsCategories((await db.prepare(HIST).all()).results)).map(({ s30, s60, n60, ...x }) => x).sort((a, b) => b.max30 - a.max30);
  const parSource = {}; for (const n of l) parSource[n.source || "sec"] = (parSource[n.source || "sec"] || 0) + 1;
  return { course, parCategorie, choix: CHOIX, parSource, dernieres: l.slice(0, 80).map((n) => ({ ...n, itemsNoms: (n.items || "").split(",").filter(Boolean).map((i) => `${i} ${ITEMS[i] || ""}`.trim()) })), parItem: Object.values(parItem).map((p) => ({ ...p, moyAbs15: p.avec15 ? +(p.somme15 / p.avec15).toFixed(2) : null })).sort((a, b) => b.nb - a.nb) };
}
