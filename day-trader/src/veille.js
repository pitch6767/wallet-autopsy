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
export const SEUILS = [0.5, 1, 2]; // % de hausse depuis le prix de la nouvelle qui « lance la tendance »

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

export class Veilleur {
  constructor(state, env) { this.state = state; this.env = env; this.s = state.storage; }
  async fetch(req) {
    const u = new URL(req.url);
    if (u.pathname === "/demarrer") { const a = await this.s.getAlarm(); if (!a) await this.s.setAlarm(Date.now() + 1000); return Response.json({ alarme: a || "posée" }); }
    if (u.pathname === "/etat") return Response.json({ dernierTour: await this.s.get("dernierTour"), erreur: await this.s.get("erreur"), alarme: await this.s.getAlarm() });
    return new Response("?", { status: 404 });
  }
  async alarm() {
    try { await this.tour(); await this.s.delete("erreur"); }
    catch (e) { await this.s.put("erreur", { quand: new Date().toISOString(), texte: String(e.message || e) }); }
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
    const st = [];
    for (const e of nouveaux) {
      vus.add(e.id);
      const sym = tk[e.cik]; if (!sym) continue; // pas une société cotée connue
      let prix0 = null, enSeance = 0, debut = e.quand;
      try { const s = await graphique(sym, "1d", "1m"); prix0 = s.meta.regularMarketPrice ?? null; } catch (x) {}
      const l = local(e.quand, MARCHES.actions); const se = seance(l.date, MARCHES.actions);
      if (se && l.min >= se[0] && l.min < se[1]) enSeance = 1; else debut = prochaineOuverture(e.quand);
      st.push(this.env.DB.prepare("INSERT OR IGNORE INTO news (id, cik, sym, nom, quand, items, lien, en_seance, prix0, debut_suivi, maj) VALUES (?,?,?,?,?,?,?,?,?,?,?)")
        .bind(e.id, e.cik, sym, e.nom, e.quand, e.items.join(","), e.lien, enSeance, prix0, debut, new Date().toISOString()));
    }
    if (st.length) await this.env.DB.batch(st);
    await this.s.put("vus", [...vus].slice(-800));
  }
}

export function prochaineOuverture(ms) {
  const m = MARCHES.actions; let l = local(ms, m); let d = l.date;
  const se = seance(d, m); if (se && l.min < se[0]) return versUtc(d, se[0], m);
  for (let i = 0; i < 10; i++) { d = new Date(Date.parse(d + "T12:00:00Z") + 864e5).toISOString().slice(0, 10); if (jourOuvre(d, m)[0]) return versUtc(d, m.ouverture, m); }
  return ms;
}

// Suivi (chaque minute) : mouvements à +5/+15/+60 min et trades papier « news » si la tendance part
export async function suiviNews(env, maintenantMs = Date.now()) {
  const db = env.DB;
  const ouverts = (await db.prepare("SELECT * FROM news WHERE fini = 0 AND prix0 IS NOT NULL AND debut_suivi <= ? AND debut_suivi >= ? ORDER BY quand LIMIT 40").bind(maintenantMs - 60e3, maintenantMs - 3 * 864e5).all()).results;
  const st = []; let traites = 0;
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
    for (const seuil of SEUILS) {
      const i = pts.findIndex((x) => x.ms < n.debut_suivi + 30 * 60e3 && x.c >= n.prix0 * (1 + seuil / 100));
      if (i < 0 || !pts[i + 1]) continue;
      const entree = pts[i + 1].o * (1 + GLISSEMENT);
      const basDepuis = Math.min(...pts.slice(0, i + 1).map((x) => x.l));
      let stop = Math.floor(Math.min(basDepuis, n.prix0) * 100) / 100;
      if (entree - stop < entree * 0.003) stop = Math.floor(entree * 0.997 * 100) / 100; // stop d'au moins 0,3 %
      const cible = Math.round((entree + 2 * (entree - stop)) * 100) / 100;
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
      st.push(db.prepare("INSERT OR REPLACE INTO papier VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)").bind(date, `news-${seuil}`, n.sym, statut, hm(pts[i + 1].ms), +entree.toFixed(4), stop, cible, statut === "ferme" ? hm(pts[Math.min(j, pts.length - 1)].ms) : null, +sortie.toFixed(4), issue + " · 8-K " + (n.items || ""), (sortie - entree) / entree, (sortie - entree) / (entree - stop), new Date(maintenantMs).toISOString()));
    }
    const fini = maintenantMs > Math.max(n.debut_suivi + 65 * 60e3, finMs + 5 * 60e3) ? 1 : 0;
    st.push(db.prepare("UPDATE news SET m5 = ?, m15 = ?, m60 = ?, max30 = ?, fini = ?, maj = ? WHERE id = ?").bind(a(5), a(15), m60, max30, fini, new Date(maintenantMs).toISOString(), n.id));
  }
  if (st.length) await db.batch(st);
  return { suivis: traites };
}

export async function statsNews(db) {
  const l = (await db.prepare("SELECT * FROM news ORDER BY quand DESC LIMIT 300").all()).results;
  const parItem = {};
  for (const n of l) for (const it of (n.items || "").split(",").filter((x) => x && x !== "9.01")) {
    const p = (parItem[it] = parItem[it] || { item: it, nom: ITEMS[it] || "", nb: 0, avec15: 0, somme15: 0, hausses30: 0 });
    p.nb++; if (n.m15 != null) { p.avec15++; p.somme15 += Math.abs(n.m15); } if (n.max30 != null && n.max30 >= 1) p.hausses30++;
  }
  return { dernieres: l.slice(0, 80).map((n) => ({ ...n, itemsNoms: (n.items || "").split(",").filter(Boolean).map((i) => `${i} ${ITEMS[i] || ""}`.trim()) })), parItem: Object.values(parItem).map((p) => ({ ...p, moyAbs15: p.avec15 ? +(p.somme15 / p.avec15).toFixed(2) : null })).sort((a, b) => b.nb - a.nb) };
}
