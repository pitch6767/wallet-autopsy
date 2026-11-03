// Radar IA — la planète IA, deux fois par jour (édition du matin et du soir, heure suisse)
// Collecte horaire des sources, édition fabriquée à l'heure choisie, résumés en français par Workers AI.
import { DurableObject } from "cloudflare:workers";
import { SOURCES, MOTS_IA, RUBRIQUES, POIDS_RUBRIQUES } from "./sources.js";

const VERSION = "1.0.1";
const MODELE = "@cf/meta/llama-3.3-70b-instruct-fp8-fast";
const UA = "Mozilla/5.0 (compatible; RadarIA/1.0; +https://radar-ia.pitch67.workers.dev)";
const FUSEAU = "Europe/Zurich";
const H = 3600e3;

const json = (o, st = 200) =>
  new Response(JSON.stringify(o), { status: st, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" } });

// ---------- outils texte ----------
const ENTITES = { amp: "&", lt: "<", gt: ">", quot: '"', apos: "'", nbsp: " ", rsquo: "’", lsquo: "‘", rdquo: "”", ldquo: "“", hellip: "…", ndash: "–", mdash: "—", eacute: "é", egrave: "è", agrave: "à", ccedil: "ç", ecirc: "ê", ocirc: "ô", icirc: "î", ucirc: "û" };
export function decode(s) {
  return String(s ?? "")
    .replace(/<!\[CDATA\[([\s\S]*?)\]\]>/g, "$1")
    .replace(/&#x([0-9a-f]+);/gi, (_, h) => String.fromCodePoint(parseInt(h, 16)))
    .replace(/&#(\d+);/g, (_, d) => String.fromCodePoint(+d))
    .replace(/&([a-z]+);/gi, (m, n) => ENTITES[n.toLowerCase()] ?? m);
}
export const sansHtml = (s) => decode(decode(s)).replace(/<script[\s\S]*?<\/script>|<style[\s\S]*?<\/style>/gi, " ").replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim();
const balise = (bloc, nom) => {
  const m = bloc.match(new RegExp(`<${nom}(?:\\s[^>]*)?>([\\s\\S]*?)</${nom}>`, "i"));
  return m ? m[1] : "";
};

// Lit un flux RSS ou Atom → [{titre, url, date, texte, auteur, video}]
export function lireFlux(xml) {
  const out = [];
  const blocs = xml.match(/<item[\s>][\s\S]*?<\/item>/gi) || xml.match(/<entry[\s>][\s\S]*?<\/entry>/gi) || [];
  for (const b of blocs) {
    let url = sansHtml(balise(b, "link"));
    if (!/^https?:/.test(url)) {
      const alt = b.match(/<link[^>]*rel=["']alternate["'][^>]*href=["']([^"']+)["']/i) || b.match(/<link[^>]*href=["']([^"']+)["']/i);
      url = alt ? decode(alt[1]) : "";
    }
    if (!url) { const g = sansHtml(balise(b, "guid")); if (/^https?:/.test(g)) url = g; }
    const dateTxt = sansHtml(balise(b, "pubDate") || balise(b, "published") || balise(b, "updated") || balise(b, "dc:date"));
    const date = Date.parse(dateTxt) || 0;
    const texte = sansHtml(balise(b, "description") || balise(b, "summary") || balise(b, "media:description") || balise(b, "content:encoded") || balise(b, "content")).slice(0, 700);
    const video = sansHtml(balise(b, "yt:videoId"));
    const auteur = sansHtml(balise(balise(b, "author"), "name") || balise(b, "dc:creator") || balise(b, "author"));
    out.push({ titre: sansHtml(balise(b, "title")).slice(0, 300), url, date, texte, auteur, video });
  }
  return out.filter((x) => x.titre && x.url);
}

// GitHub Trending (page HTML) → dépôts
export function lireTrending(html) {
  const out = [];
  for (const art of html.split(/<article class="Box-row/).slice(1)) {
    const nom = (art.match(/<h2[\s\S]*?href="\/([^"\/]+\/[^"\/]+)"/) || [])[1];
    if (!nom) continue;
    const desc = sansHtml((art.match(/<p class="col-9[^"]*">([\s\S]*?)<\/p>/) || [])[1] || "");
    const langage = sansHtml((art.match(/itemprop="programmingLanguage">([^<]*)</) || [])[1] || "");
    const auj = +((art.match(/([\d,]+)\s+stars? today/) || [])[1] || "0").replace(/,/g, "");
    const total = +((art.match(/href="\/[^"]+\/stargazers"[^>]*>[\s\S]*?([\d,]+)\s*<\/a>/) || [])[1] || "0").replace(/,/g, "");
    out.push({ nom: nom.trim(), desc, langage, auj, total });
  }
  return out;
}

const motsTitre = (t) => new Set(String(t).toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "").split(/[^a-z0-9]+/).filter((w) => w.length > 3));
const jaccard = (a, b) => { let i = 0; for (const x of a) if (b.has(x)) i++; return i / Math.max(1, a.size + b.size - i); };

async function hacher(s) {
  const d = await crypto.subtle.digest("SHA-1", new TextEncoder().encode(s));
  return [...new Uint8Array(d)].slice(0, 10).map((b) => b.toString(16).padStart(2, "0")).join("");
}

function heureLocale(ts = Date.now()) {
  const p = Object.fromEntries(new Intl.DateTimeFormat("fr-CH", { timeZone: FUSEAU, year: "numeric", month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit", hourCycle: "h23" }).formatToParts(new Date(ts)).map((x) => [x.type, x.value]));
  return { jour: `${p.year}-${p.month}-${p.day}`, heure: +p.hour, minute: +p.minute, joli: `${p.day}.${p.month}.${p.year}` };
}

async function chercher(url, opts = {}, ms = 20000) {
  const ctl = new AbortController();
  const t = setTimeout(() => ctl.abort(), ms);
  try {
    const r = await fetch(url, { ...opts, signal: ctl.signal, headers: { "user-agent": UA, accept: "*/*", ...(opts.headers || {}) } });
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    return r;
  } finally { clearTimeout(t); }
}

// ---------- Worker ----------
export default {
  async fetch(req, env) {
    const url = new URL(req.url);
    const p = url.pathname;
    if (p === "/" || p === "/index.html") {
      const r = await env.ASSETS.fetch(new Request(new URL("/index.html", url)));
      return new Response(r.body, { headers: { "content-type": "text/html; charset=utf-8", "cache-control": "no-store, max-age=0" } });
    }
    if (p.startsWith("/api/")) return env.RADAR.get(env.RADAR.idFromName("principal")).fetch(req);
    return env.ASSETS.fetch(req);
  },
  async scheduled(evt, env, ctx) {
    const radar = env.RADAR.get(env.RADAR.idFromName("principal"));
    await radar.fetch(new Request("https://radar/api/tic", { method: "POST" }));
  },
};

export class Radar extends DurableObject {
  constructor(ctx, env) {
    super(ctx, env);
    this.env = env;
    this.sql = ctx.storage.sql;
    this.sql.exec(`CREATE TABLE IF NOT EXISTS kv(k TEXT PRIMARY KEY, v TEXT)`);
    this.sql.exec(`CREATE TABLE IF NOT EXISTS items(id TEXT PRIMARY KEY, source TEXT, famille TEXT, genre TEXT, titre TEXT, url TEXT, texte TEXT,
      date INTEGER, extra TEXT, ajoute INTEGER, edition TEXT)`);
    this.sql.exec(`CREATE INDEX IF NOT EXISTS items_date ON items(date)`);
    this.sql.exec(`CREATE TABLE IF NOT EXISTS editions(id TEXT PRIMARY KEY, cree INTEGER, contenu TEXT)`);
    this.sql.exec(`CREATE TABLE IF NOT EXISTS favoris(id TEXT PRIMARY KEY, ts INTEGER, carte TEXT)`);
  }
  lire(k, def = null) { const r = this.sql.exec(`SELECT v FROM kv WHERE k=?`, k).toArray()[0]; return r ? JSON.parse(r.v) : def; }
  ecrire(k, v) { this.sql.exec(`INSERT OR REPLACE INTO kv(k,v) VALUES(?,?)`, k, JSON.stringify(v)); }
  prefs() {
    return { heures: [7, 19], masques: [], sources: {}, rubriques: {}, ...this.lire("prefs", {}) };
  }

  async fetch(req) {
    const url = new URL(req.url);
    const p = url.pathname;
    const corps = req.method === "POST" ? await req.json().catch(() => ({})) : {};
    try {
      if (p === "/api/tic") return json(await this.tic());
      if (p === "/api/etat") return json(this.etat());
      if (p === "/api/collecter" && req.method === "POST") return json(await this.collecter());
      if (p === "/api/fabriquer" && req.method === "POST") {
        const der = this.lire("derniere_fab_manuelle", 0);
        if (Date.now() - der < 20 * 60e3) return json({ erreur: "Une édition vient d'être fabriquée, réessaie dans 20 minutes." }, 429);
        this.ecrire("derniere_fab_manuelle", Date.now());
        if (corps.refaire) this.sql.exec(`UPDATE items SET edition=NULL WHERE edition=?`, String(corps.refaire));
        await this.collecter();
        return json(await this.fabriquer(corps.creneau || null));
      }
      if (p === "/api/editions") return json(this.sql.exec(`SELECT id, cree FROM editions ORDER BY cree DESC LIMIT 60`).toArray());
      if (p === "/api/edition") {
        const id = url.searchParams.get("id");
        const r = (id ? this.sql.exec(`SELECT contenu FROM editions WHERE id=?`, id) : this.sql.exec(`SELECT contenu FROM editions ORDER BY cree DESC LIMIT 1`)).toArray()[0];
        if (!r) return json({ vide: true, etat: this.etat() });
        const e = JSON.parse(r.contenu);
        const fav = new Set(this.sql.exec(`SELECT id FROM favoris`).toArray().map((x) => x.id));
        e.favoris = [...fav];
        return json(e);
      }
      if (p === "/api/favoris") {
        if (req.method === "POST") {
          if (corps.retirer) this.sql.exec(`DELETE FROM favoris WHERE id=?`, String(corps.id));
          else if (corps.carte?.id) this.sql.exec(`INSERT OR REPLACE INTO favoris(id,ts,carte) VALUES(?,?,?)`, String(corps.carte.id), Date.now(), JSON.stringify(corps.carte).slice(0, 8000));
          return json({ ok: true });
        }
        return json(this.sql.exec(`SELECT carte FROM favoris ORDER BY ts DESC`).toArray().map((r) => JSON.parse(r.carte)));
      }
      if (p === "/api/prefs") {
        if (req.method === "POST") {
          const pr = this.prefs();
          if (corps.heures && corps.heures.length === 2) {
            const h = corps.heures.map((x) => Math.max(0, Math.min(23, parseInt(x, 10))));
            if (h.every((x) => !isNaN(x)) && h[0] !== h[1]) pr.heures = h.sort((a, b) => a - b);
          }
          if (corps.source) {
            const s = String(corps.source);
            if (corps.sens === "masquer") pr.masques = [...new Set([...pr.masques, s])];
            else if (corps.sens === "afficher") pr.masques = pr.masques.filter((x) => x !== s);
            else pr.sources[s] = Math.max(0.4, Math.min(2, (pr.sources[s] || 1) * (corps.sens > 0 ? 1.15 : 0.85)));
          }
          if (corps.rubrique) pr.rubriques[corps.rubrique] = Math.max(0.4, Math.min(2, (pr.rubriques[corps.rubrique] || 1) * (corps.sens > 0 ? 1.15 : 0.85)));
          if (corps.reinitialiser) { pr.sources = {}; pr.rubriques = {}; pr.masques = []; }
          this.ecrire("prefs", pr);
          return json(pr);
        }
        return json({ ...this.prefs(), liste: SOURCES.map((s) => ({ id: s.id, nom: s.nom, famille: s.famille })), poidsDepart: POIDS_RUBRIQUES, rubriques_noms: RUBRIQUES });
      }
      return json({ erreur: "inconnu" }, 404);
    } catch (e) {
      return json({ erreur: String(e?.stack || e).slice(0, 800) }, 500);
    }
  }

  etat() {
    const n = this.sql.exec(`SELECT genre, COUNT(*) n FROM items GROUP BY genre`).toArray();
    return {
      version: VERSION, prefs: this.prefs(), items: n,
      sources: this.lire("etat_sources", {}), canaux: this.lire("canaux", {}),
      derniere_collecte: this.lire("derniere_collecte", null), derniere_edition: this.lire("derniere_edition", null),
      editions: this.sql.exec(`SELECT id, cree FROM editions ORDER BY cree DESC LIMIT 5`).toArray(),
    };
  }

  // appelé chaque heure par le cron
  async tic() {
    const col = await this.collecter();
    const { jour, heure } = heureLocale();
    const pr = this.prefs();
    let fab = null;
    const creneau = heure === pr.heures[0] ? "matin" : heure === pr.heures[1] ? "soir" : null;
    if (creneau && !this.sql.exec(`SELECT 1 FROM editions WHERE id=?`, `${jour}-${creneau}`).toArray().length) fab = await this.fabriquer(creneau);
    // nettoyage : on garde 10 jours d'articles et 90 éditions
    this.sql.exec(`DELETE FROM items WHERE ajoute < ?`, Date.now() - 10 * 24 * H);
    this.sql.exec(`DELETE FROM editions WHERE id NOT IN (SELECT id FROM editions ORDER BY cree DESC LIMIT 90)`);
    return { col, fab };
  }

  // ---------- collecte ----------
  async collecter() {
    const etat = this.lire("etat_sources", {});
    const pr = this.prefs();
    const actives = SOURCES.filter((s) => !pr.masques.includes(s.id));
    const res = await Promise.allSettled(actives.map((s) => this.collecterSource(s)));
    let ajoutes = 0;
    res.forEach((r, i) => {
      const s = actives[i];
      if (r.status === "fulfilled") { etat[s.id] = { ok: true, lus: r.value.lus, nouveaux: r.value.nouveaux, quand: Date.now(), note: r.value.note || "" }; ajoutes += r.value.nouveaux; }
      else etat[s.id] = { ...(etat[s.id] || {}), ok: false, erreur: String(r.reason?.message || r.reason).slice(0, 160), quand: Date.now() };
    });
    this.ecrire("etat_sources", etat);
    this.ecrire("derniere_collecte", { quand: Date.now(), ajoutes });
    return { ajoutes, sources: actives.length };
  }

  async ajouter(s, genre, x) {
    if (!x.url || !x.titre) return 0;
    const propre = x.url.replace(/#.*$/, "").replace(/([?&])(utm_[^&=]*|ref|source)=[^&]*/g, "$1").replace(/[?&]+$/, "").replace(/\/$/, "");
    const id = await hacher(propre + (genre === "version" ? x.titre : ""));
    const avant = this.sql.exec(`SELECT 1 FROM items WHERE id=?`, id).toArray().length;
    if (avant) return 0;
    this.sql.exec(`INSERT INTO items(id,source,famille,genre,titre,url,texte,date,extra,ajoute,edition) VALUES(?,?,?,?,?,?,?,?,?,?,NULL)`,
      id, s.id, s.famille, genre, x.titre, x.url, x.texte || "", x.date || Date.now(), JSON.stringify(x.extra || {}), Date.now());
    return 1;
  }

  async collecterSource(s) {
    const limite = Date.now() - 4 * 24 * H;
    let lus = 0, nouveaux = 0, note = "";
    if (s.type === "rss" || s.type === "release") {
      const xml = await (await chercher(s.url)).text();
      const liste = lireFlux(xml).slice(0, s.type === "release" ? 3 : 40);
      for (const x of liste) {
        if (x.date && x.date < limite) continue;
        if (s.filtre && !MOTS_IA.test(x.titre + " " + x.texte)) continue;
        lus++;
        if (s.type === "release") x.titre = `${s.nom} ${x.titre}`;
        nouveaux += await this.ajouter(s, s.type === "release" ? "version" : "article", x);
      }
    } else if (s.type === "yt" || s.type === "ytnom") {
      let canal = s.canal;
      if (!canal) {
        const canaux = this.lire("canaux", {});
        canal = canaux[s.id]?.canal;
        if (!canal) {
          const html = await (await chercher(`https://www.youtube.com/results?search_query=${encodeURIComponent(s.recherche)}&sp=EgIQAg%253D%253D`, { headers: { "accept-language": "fr-CH,fr;q=0.9", cookie: "CONSENT=YES+1" } })).text();
          canal = (html.match(/"channelId":"(UC[\w-]{22})"/) || [])[1];
          if (!canal) throw new Error("chaîne introuvable");
          canaux[s.id] = { canal, trouve: Date.now() };
          this.ecrire("canaux", canaux);
        }
      }
      const xml = await (await chercher(`https://www.youtube.com/feeds/videos.xml?channel_id=${canal}`)).text();
      const liste = lireFlux(xml).slice(0, 8);
      const nomFlux = sansHtml(balise(xml.split(/<entry/)[0], "title"));
      if (s.type === "ytnom") { const c = this.lire("canaux", {}); c[s.id] = { ...(c[s.id] || {}), canal, nom_trouve: nomFlux }; this.ecrire("canaux", c); }
      note = nomFlux;
      for (const x of liste) {
        if (x.date && x.date < limite) continue;
        if (/\/shorts\//.test(x.url)) continue;
        lus++;
        x.extra = { chaine: nomFlux || s.nom, video: x.video };
        nouveaux += await this.ajouter(s, "video", x);
      }
    } else if (s.type === "hfpapers") {
      const liste = await (await chercher(s.url)).json();
      for (const x of (liste || []).slice(0, 30)) {
        const pp = x.paper || {};
        if (!pp.id) continue;
        lus++;
        nouveaux += await this.ajouter(s, "papier", { titre: pp.title || x.title, url: `https://huggingface.co/papers/${pp.id}`, texte: String(pp.summary || "").slice(0, 700), date: Date.parse(x.publishedAt || pp.publishedAt) || Date.now(), extra: { votes: pp.upvotes || 0, arxiv: `https://arxiv.org/abs/${pp.id}` } });
      }
    } else if (s.type === "trending") {
      const html = await (await chercher(s.url)).text();
      const liste = lireTrending(html);
      if (!liste.length) throw new Error("page Trending illisible");
      for (const r of liste) {
        if (!MOTS_IA.test(`${r.nom} ${r.desc}`) && !/\b(rag|mcp|vlm|tts|asr|lora|gguf|embedding)/i.test(`${r.nom} ${r.desc}`)) continue;
        lus++;
        // un même dépôt peut revenir un autre jour : on l'identifie par nom + jour
        const { jour } = heureLocale();
        nouveaux += await this.ajouter(s, "depot", { titre: r.nom, url: `https://github.com/${r.nom}#${jour}`, texte: r.desc, date: Date.now(), extra: { langage: r.langage, etoiles_jour: r.auj, etoiles: r.total, depot: r.nom, signal: "tendance du jour" } });
      }
    } else if (s.type === "ghsearch") {
      const d = new Date(Date.now() - 7 * 24 * H).toISOString().slice(0, 10);
      const q = `llm OR agent OR "ai" OR mcp in:name,description,topics created:>=${d} stars:>30`;
      const r = await (await chercher(`${s.url}?q=${encodeURIComponent(q)}&sort=stars&order=desc&per_page=20`, { headers: { accept: "application/vnd.github+json" } })).json();
      for (const x of r.items || []) {
        lus++;
        nouveaux += await this.ajouter(s, "depot", { titre: x.full_name, url: x.html_url, texte: x.description || "", date: Date.parse(x.created_at) || Date.now(), extra: { langage: x.language, etoiles: x.stargazers_count, licence: x.license?.spdx_id || null, maj: x.pushed_at, depot: x.full_name, signal: "nouveau dépôt qui monte" } });
      }
    }
    return { lus, nouveaux, note };
  }

  // ---------- fabrication d'une édition ----------
  async fabriquer(creneauForce) {
    const t0 = Date.now();
    const { jour, heure, joli } = heureLocale();
    const pr = this.prefs();
    const creneau = creneauForce || (heure < 13 ? "matin" : "soir");
    const id = `${jour}-${creneau}`;
    const depuis = Date.now() - 36 * H;
    const prendre = (genres, n) => this.sql.exec(
      `SELECT * FROM items WHERE edition IS NULL AND date >= ? AND genre IN (${genres.map(() => "?").join(",")}) ORDER BY date DESC LIMIT 400`, depuis, ...genres)
      .toArray().filter((x) => !pr.masques.includes(x.source)).map((x) => ({ ...x, extra: JSON.parse(x.extra || "{}") }));
    const src = Object.fromEntries(SOURCES.map((s) => [s.id, s]));
    const prescore = (x) => {
      const age = Math.max(0, (Date.now() - x.date) / H);
      const e = x.extra || {};
      const bonus = x.genre === "papier" ? Math.min(1.5, 0.6 + (e.votes || 0) / 40) : x.genre === "depot" ? Math.min(1.6, 0.6 + (e.etoiles_jour || e.etoiles || 0) / 300) : 1;
      return (src[x.source]?.poids || 1) * (pr.sources[x.source] || 1) * bonus * (1.2 - Math.min(1, age / 36));
    };
    // regroupement des doublons par titres proches
    const regrouper = (liste) => {
      const groupes = [];
      for (const x of liste.sort((a, b) => prescore(b) - prescore(a))) {
        const m = motsTitre(x.titre);
        const g = groupes.find((g) => jaccard(g.mots, m) >= 0.45);
        if (g) g.autres.push(x); else groupes.push({ tete: x, mots: m, autres: [] });
      }
      return groupes;
    };
    const articles = regrouper(prendre(["article", "papier", "version"])).slice(0, 45);
    const videos = regrouper(prendre(["video"])).slice(0, 12);
    const depots = regrouper(prendre(["depot"])).slice(0, 14);
    const tous = [...articles, ...videos, ...depots];
    if (!tous.length) return { id, vide: true, note: "aucune nouveauté depuis la dernière édition" };

    const analyses = await this.analyser(tous.map((g) => g.tete));
    const cartes = [];
    tous.forEach((g, i) => {
      const a = analyses[i];
      if (!a) return;
      const x = g.tete;
      const rub = ["modeles", "idees", "local", "recherche"].includes(a.rubrique) ? a.rubrique : "recherche";
      const imp = Math.max(1, Math.min(5, +a.importance || 2));
      const score = imp * (POIDS_RUBRIQUES[rub] || 1) * (pr.rubriques[rub] || 1) * prescore(x);
      const autres = g.autres.slice(0, 5).map((o) => ({ source: src[o.source]?.nom || o.source, url: o.url, titre: o.titre }));
      cartes.push({
        id: x.id, genre: x.genre, rubrique: rub, importance: imp, score: +score.toFixed(3), doublon_de: a.doublon_de ?? null,
        titre: a.titre || x.titre, titre_original: x.titre, resume: a.resume || "", pourquoi: a.pourquoi || "", statut: a.statut || "",
        type_video: a.type_video || "", essai: a.essai || "",
        source: src[x.source]?.nom || x.source, source_id: x.source, famille: x.famille, url: x.url.replace(/#\d{4}-\d{2}-\d{2}$/, ""), date: x.date,
        extra: x.extra, autres,
      });
      for (const o of [x, ...g.autres]) this.sql.exec(`UPDATE items SET edition=? WHERE id=?`, id, o.id);
    });
    // doublons signalés par l'IA (ex. même nouvelle en français et en anglais)
    const parId = Object.fromEntries(cartes.map((c) => [c.id, c]));
    const finales = [];
    for (const c of cartes.sort((a, b) => b.score - a.score)) {
      const maitre = c.doublon_de && parId[c.doublon_de];
      if (maitre && maitre !== c && finales.includes(maitre)) { maitre.autres.push({ source: c.source, url: c.url, titre: c.titre_original }); continue; }
      finales.push(c);
    }
    const art = finales.filter((c) => c.genre !== "video" && c.genre !== "depot");
    const une = [];
    const parSource = {};
    for (const c of art) {
      if (une.length >= 5) break;
      if ((parSource[c.source_id] || 0) >= 2) continue;
      parSource[c.source_id] = (parSource[c.source_id] || 0) + 1;
      une.push(c);
    }
    const reste = art.filter((c) => !une.includes(c));
    const edition = {
      id, creneau, jour, titre: `Édition du ${creneau} — ${joli}`, cree: Date.now(), version: VERSION,
      une,
      rubriques: RUBRIQUES.map((r) => ({ id: r.id, titre: r.titre, cartes: reste.filter((c) => c.rubrique === r.id).slice(0, 5) })).filter((r) => r.cartes.length),
      videos: finales.filter((c) => c.genre === "video").slice(0, 3),
      depots: finales.filter((c) => c.genre === "depot").slice(0, 5),
      stats: { candidats: tous.length, retenus: 0, duree_s: 0, modele: MODELE },
    };
    edition.stats.retenus = edition.une.length + edition.rubriques.reduce((a, r) => a + r.cartes.length, 0) + edition.videos.length + edition.depots.length;
    edition.stats.duree_s = Math.round((Date.now() - t0) / 1000);
    this.sql.exec(`INSERT OR REPLACE INTO editions(id,cree,contenu) VALUES(?,?,?)`, id, Date.now(), JSON.stringify(edition));
    this.ecrire("derniere_edition", { id, quand: Date.now(), retenus: edition.stats.retenus, duree_s: edition.stats.duree_s });
    return { id, retenus: edition.stats.retenus, candidats: tous.length, duree_s: edition.stats.duree_s };
  }

  // Résumé, traduction et classement en français par Workers AI, par paquets de 8
  async analyser(items) {
    const res = new Array(items.length).fill(null);
    const PAQUET = 8;
    const consigne = `Tu es le rédacteur de « Radar IA », une veille en français sur l'intelligence artificielle pour un lecteur suisse curieux et pragmatique (modèles, IA locale sur son ordinateur, matériel, agents, création d'apps).
Pour chaque élément reçu, réponds UNIQUEMENT par un tableau JSON, un objet par élément, dans le même ordre, avec ces clés :
- "n" : le numéro de l'élément
- "titre" : titre informatif en français correct (majuscule initiale, accents, noms propres en majuscule), 7 à 14 mots, qui dit ce qui se passe — par exemple « Anthropic publie une étude sur la fiabilité des agents de codage »
- "resume" : 2 à 3 phrases en français, factuelles, rédigées avec tes propres mots ; n'invente rien qui ne figure pas dans le texte
- "pourquoi" : une phrase : ce que cela change concrètement pour un utilisateur qui teste l'IA chez lui ou crée des apps (vide si rien)
- "rubrique" : "modeles" (sortie ou mise à jour de modèle, benchmark), "idees" (outils, usages, agents, automatisation, création d'apps, dépôts), "local" (IA sur son ordinateur, GPU, puces, matériel, prix), "recherche" (papiers, robotique, entreprises, régulation, sécurité, société)
- "importance" : 1 à 5 (5 = nouveauté majeure qui change ce qu'on peut faire ; 1 = anecdotique ou promotionnel)
- "statut" : "annoncé", "disponible", "testé", "préliminaire" ou "rumeur"
- "doublon_de" : le numéro d'un élément précédent de cette liste qui traite exactement du même événement, sinon null
- pour une vidéo seulement, "type_video" : "test", "démo", "tutoriel", "analyse", "actualité" ou "promotion"
- pour un dépôt GitHub seulement, "essai" : "lecture seule", "installation simple", "environnement isolé conseillé" ou "préparation avancée"
Aucun texte hors du tableau JSON.`;
    for (let i = 0; i < items.length; i += PAQUET) {
      const lot = items.slice(i, i + PAQUET);
      const entree = lot.map((x, k) => {
        const e = x.extra || {};
        const genre = { article: "article", papier: "papier de recherche", version: "nouvelle version logicielle", video: "vidéo YouTube", depot: "dépôt GitHub" }[x.genre] || x.genre;
        const plus = x.genre === "depot" ? ` | langage ${e.langage || "?"} | ${e.etoiles_jour ? e.etoiles_jour + " étoiles aujourd'hui" : (e.etoiles || 0) + " étoiles"}` : x.genre === "video" ? ` | chaîne ${e.chaine || ""}` : "";
        return `#${i + k} [${genre} — ${SOURCES.find((s) => s.id === x.source)?.nom || x.source}${plus}]\nTitre : ${x.titre}\nTexte : ${(x.texte || "").slice(0, 600)}`;
      }).join("\n\n");
      let tableau = null;
      for (let essai = 0; essai < 2 && !tableau; essai++) {
        try {
          const r = await this.env.AI.run(MODELE, { messages: [{ role: "system", content: consigne }, { role: "user", content: entree }], max_tokens: 3500, temperature: 0.2 });
          const txt = typeof r?.response === "string" ? r.response : JSON.stringify(r?.response ?? r);
          const m = txt.match(/\[[\s\S]*\]/);
          tableau = JSON.parse(m ? m[0] : txt);
          if (!Array.isArray(tableau)) tableau = null;
        } catch (e) { this.ecrire("derniere_erreur_ia", { quand: Date.now(), erreur: String(e).slice(0, 300) }); }
      }
      for (const a of tableau || []) {
        const n = parseInt(a?.n, 10);
        if (n >= i && n < i + lot.length) {
          const d = parseInt(a.doublon_de, 10);
          res[n] = { ...a, doublon_de: Number.isInteger(d) && d >= 0 && d < items.length && d !== n ? items[d].id : null };
        }
      }
      // si l'IA a échoué, on garde l'élément brut plutôt que de le perdre
      lot.forEach((x, k) => { if (!res[i + k]) res[i + k] = { titre: x.titre, resume: (x.texte || "").slice(0, 280), rubrique: x.genre === "depot" ? "idees" : x.genre === "papier" ? "recherche" : "recherche", importance: 2, statut: "", brut: true }; });
    }
    return res;
  }
}
