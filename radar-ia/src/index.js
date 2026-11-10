// Radar IA — la planète IA, deux fois par jour (édition du matin et du soir, heure suisse)
// Collecte horaire des sources, édition fabriquée à l'heure choisie, résumés en français par Workers AI.
// v1.1 : doublons éliminés sur toute l'édition et sur 7 jours, articles lus en entier, nouveaux modèles,
// modèles non censurés, dépôts GitHub classés par vitesse d'étoiles, Hacker News, newsletters, abonnements YouTube.
import { DurableObject } from "cloudflare:workers";
import { SOURCES, MOTS_IA, MOTS_DEPOT, TYPES_MODELE, RUBRIQUES, POIDS_RUBRIQUES } from "./sources.js";

const VERSION = "1.1.3";
const MODELE = "@cf/meta/llama-3.3-70b-instruct-fp8-fast";
const UA = "Mozilla/5.0 (compatible; RadarIA/1.1; +https://radar-ia.pitch67.workers.dev)";
const FUSEAU = "Europe/Zurich";
const H = 3600e3;
const J = 24 * H;
// Taille de l'édition (le tri : on ne garde que le meilleur)
const TAILLE = { une: 5, parRubrique: 4, videos: 5, depots: 10, modeles: 6, libres: 4, lectureComplete: 16 };

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
    const texte = sansHtml(balise(b, "description") || balise(b, "summary") || balise(b, "media:description") || balise(b, "content:encoded") || balise(b, "content")).slice(0, 900);
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
    const periode = +((art.match(/([\d,]+)\s+stars? (?:today|this week)/) || [])[1] || "0").replace(/,/g, "");
    const total = +((art.match(/href="\/[^"]+\/stargazers"[^>]*>[\s\S]*?([\d,]+)\s*<\/a>/) || [])[1] || "0").replace(/,/g, "");
    out.push({ nom: nom.trim(), desc, langage, periode, total });
  }
  return out;
}

// Texte principal d'une page web (paragraphes de l'article)
export function texteArticle(html) {
  const zone = (html.match(/<article[\s\S]*?<\/article>/i) || html.match(/<main[\s\S]*?<\/main>/i) || [html])[0];
  const paras = (zone.match(/<p[\s>][\s\S]*?<\/p>/gi) || []).map(sansHtml).filter((p) => p.length > 60);
  return paras.join("\n").slice(0, 7000);
}

// Taille d'un modèle d'après son nom (ex. « Qwen3-32B », « 8x7B », « 30B-A3B ») → milliards de paramètres
export function tailleModele(nom) {
  const n = String(nom);
  const moe = n.match(/(\d+)x(\d+(?:\.\d+)?)b/i);
  if (moe) return +moe[1] * +moe[2];
  const m = [...n.matchAll(/(?:^|[^a-z0-9.])(\d+(?:\.\d+)?)\s?b(?![a-z])/gi)].map((x) => +x[1]).filter((x) => x > 0.1 && x < 3000);
  return m.length ? Math.max(...m) : null;
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

// exécute des tâches avec au plus n en parallèle
async function parPaquets(liste, n, f) {
  const res = new Array(liste.length);
  let i = 0;
  await Promise.all(Array.from({ length: Math.min(n, liste.length) }, async () => { while (i < liste.length) { const k = i++; try { res[k] = await f(liste[k], k); } catch (e) { res[k] = null; } } }));
  return res;
}

function lireJson(txt, ouvrant = "[") {
  const fermant = ouvrant === "[" ? "]" : "}";
  const a = txt.indexOf(ouvrant), b = txt.lastIndexOf(fermant);
  if (a < 0 || b < a) throw new Error("pas de JSON");
  return JSON.parse(txt.slice(a, b + 1).replace(/[\u0000-\u001f]+/g, " "));
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
    // suivi des dépôts GitHub (étoiles relevées chaque heure → vitesse)
    this.sql.exec(`CREATE TABLE IF NOT EXISTS depots(nom TEXT PRIMARY KEY, descr TEXT, langage TEXT, licence TEXT, etoiles INTEGER, hist TEXT,
      premier INTEGER, cree INTEGER, periode INTEGER, signal TEXT, montre TEXT)`);
    // sujets déjà publiés (7 jours) pour ne jamais resservir la même nouvelle
    this.sql.exec(`CREATE TABLE IF NOT EXISTS sujets(id TEXT PRIMARY KEY, titre TEXT, ts INTEGER)`);
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
        // la fabrication prend plusieurs minutes : elle tourne en arrière-plan (alarme), la réponse est immédiate
        this.ecrire("a_fabriquer", { creneau: corps.creneau || null, refaire: corps.refaire || null, demande: Date.now() });
        await this.ctx.storage.setAlarm(Date.now() + 1000);
        return json({ ok: true, lance: true, note: "fabrication lancée en arrière-plan, voir /api/etat → derniere_edition" });
      }
      if (p === "/api/editions") return json(this.sql.exec(`SELECT id, cree FROM editions ORDER BY cree DESC LIMIT 60`).toArray());
      if (p === "/api/edition") {
        const id = url.searchParams.get("id");
        const r = (id ? this.sql.exec(`SELECT contenu FROM editions WHERE id=?`, id) : this.sql.exec(`SELECT contenu FROM editions ORDER BY cree DESC LIMIT 1`)).toArray()[0];
        if (!r) return json({ vide: true, etat: this.etat() });
        const e = JSON.parse(r.contenu);
        e.favoris = this.sql.exec(`SELECT id FROM favoris`).toArray().map((x) => x.id);
        return json(e);
      }
      if (p === "/api/favoris") {
        if (req.method === "POST") {
          if (corps.retirer) this.sql.exec(`DELETE FROM favoris WHERE id=?`, String(corps.id));
          else if (corps.carte?.id) this.sql.exec(`INSERT OR REPLACE INTO favoris(id,ts,carte) VALUES(?,?,?)`, String(corps.carte.id), Date.now(), JSON.stringify(corps.carte).slice(0, 12000));
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
      depots_suivis: this.sql.exec(`SELECT COUNT(*) n FROM depots`).toArray()[0]?.n || 0,
      sources: this.lire("etat_sources", {}), canaux: this.lire("canaux", {}),
      derniere_collecte: this.lire("derniere_collecte", null), derniere_edition: this.lire("derniere_edition", null),
      derniere_erreur_ia: this.lire("derniere_erreur_ia", null), derniere_fabrication: this.lire("derniere_fabrication", null),
      editions: this.sql.exec(`SELECT id, cree FROM editions ORDER BY cree DESC LIMIT 5`).toArray(),
    };
  }

  // fabrication en arrière-plan
  async alarm() {
    const t = this.lire("a_fabriquer", null);
    if (!t) return;
    this.ecrire("a_fabriquer", null);
    try {
      if (t.refaire) {
        const ref = String(t.refaire);
        this.sql.exec(`UPDATE items SET edition=NULL WHERE edition=? OR edition=?`, ref, ref + ":doublon");
        this.sql.exec(`UPDATE depots SET montre=NULL WHERE montre=?`, ref);
        this.sql.exec(`DELETE FROM sujets WHERE id LIKE ?`, ref + ":%");
      }
      await this.collecter();
      const r = await this.fabriquer(t.creneau);
      this.ecrire("derniere_fabrication", { ...r, demande: t.demande, fini: Date.now() });
    } catch (e) {
      this.ecrire("derniere_fabrication", { erreur: String(e?.stack || e).slice(0, 600), demande: t.demande, fini: Date.now() });
    }
  }

  // appelé chaque heure par le cron
  async tic() {
    const col = await this.collecter();
    const { jour, heure } = heureLocale();
    const pr = this.prefs();
    let fab = null;
    const creneau = heure === pr.heures[0] ? "matin" : heure === pr.heures[1] ? "soir" : null;
    if (creneau && !this.sql.exec(`SELECT 1 FROM editions WHERE id=?`, `${jour}-${creneau}`).toArray().length) {
      this.ecrire("a_fabriquer", { creneau, refaire: null, demande: Date.now() });
      await this.ctx.storage.setAlarm(Date.now() + 1000);
      fab = "lancée";
    }
    // nettoyage : 10 jours d'articles, 7 jours de sujets, 30 jours de dépôts non montrés, 90 éditions
    this.sql.exec(`DELETE FROM items WHERE ajoute < ?`, Date.now() - 10 * J);
    this.sql.exec(`DELETE FROM sujets WHERE ts < ?`, Date.now() - 7 * J);
    this.sql.exec(`DELETE FROM depots WHERE montre IS NULL AND premier < ?`, Date.now() - 30 * J);
    this.sql.exec(`DELETE FROM editions WHERE id NOT IN (SELECT id FROM editions ORDER BY cree DESC LIMIT 90)`);
    return { col, fab };
  }

  // ---------- collecte ----------
  async collecter() {
    const etat = this.lire("etat_sources", {});
    const pr = this.prefs();
    const actives = SOURCES.filter((s) => !pr.masques.includes(s.id));
    const res = await parPaquets(actives, 12, async (s) => {
      try { return { ok: true, v: await this.collecterSource(s) }; } catch (e) { return { ok: false, e }; }
    });
    let ajoutes = 0;
    res.forEach((r, i) => {
      const s = actives[i];
      if (r?.ok) { etat[s.id] = { ok: true, lus: r.v.lus, nouveaux: r.v.nouveaux, quand: Date.now(), note: r.v.note || "" }; ajoutes += r.v.nouveaux; }
      else etat[s.id] = { ...(etat[s.id] || {}), ok: false, erreur: String(r?.e?.message || r?.e || "échec").slice(0, 160), quand: Date.now() };
    });
    this.ecrire("etat_sources", etat);
    this.ecrire("derniere_collecte", { quand: Date.now(), ajoutes });
    return { ajoutes, sources: actives.length };
  }

  async ajouter(s, genre, x, cle) {
    if (!x.url || !x.titre) return 0;
    const propre = x.url.replace(/#.*$/, "").replace(/([?&])(utm_[^&=]*|ref|source)=[^&]*/g, "$1").replace(/[?&]+$/, "").replace(/\/$/, "");
    const id = await hacher(cle || (propre + (genre === "version" ? x.titre : "")));
    if (this.sql.exec(`SELECT 1 FROM items WHERE id=?`, id).toArray().length) {
      // déjà connu : on rafraîchit seulement les chiffres (votes, points, tendance)
      if (x.extra) this.sql.exec(`UPDATE items SET extra=? WHERE id=? AND edition IS NULL`, JSON.stringify(x.extra), id);
      return 0;
    }
    this.sql.exec(`INSERT INTO items(id,source,famille,genre,titre,url,texte,date,extra,ajoute,edition) VALUES(?,?,?,?,?,?,?,?,?,?,NULL)`,
      id, s.id, s.famille, genre, x.titre, x.url, x.texte || "", x.date || Date.now(), JSON.stringify(x.extra || {}), Date.now());
    return 1;
  }

  // relève les étoiles d'un dépôt (historique horaire sur 3 jours)
  suivreDepot(d) {
    const r = this.sql.exec(`SELECT * FROM depots WHERE nom=?`, d.nom).toArray()[0];
    const now = Date.now();
    if (!r) {
      this.sql.exec(`INSERT INTO depots(nom,descr,langage,licence,etoiles,hist,premier,cree,periode,signal,montre) VALUES(?,?,?,?,?,?,?,?,?,?,NULL)`,
        d.nom, d.desc || "", d.langage || "", d.licence || null, d.etoiles || 0, JSON.stringify(d.etoiles ? [[now, d.etoiles]] : []), now, d.cree || null, d.periode || 0, d.signal || "");
      return 1;
    }
    let hist = JSON.parse(r.hist || "[]");
    if (d.etoiles && (!hist.length || now - hist[hist.length - 1][0] > 50 * 60e3)) hist.push([now, d.etoiles]);
    hist = hist.filter((h) => now - h[0] < 3 * J);
    this.sql.exec(`UPDATE depots SET descr=COALESCE(NULLIF(?,''),descr), langage=COALESCE(NULLIF(?,''),langage), licence=COALESCE(?,licence), etoiles=MAX(etoiles,?), hist=?, cree=COALESCE(cree,?), periode=MAX(?,0), signal=COALESCE(NULLIF(?,''),signal) WHERE nom=?`,
      d.desc || "", d.langage || "", d.licence || null, d.etoiles || 0, JSON.stringify(hist), d.cree || null, d.periode || 0, d.signal || "", d.nom);
    return 0;
  }

  async collecterSource(s) {
    const limite = Date.now() - 4 * J;
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
        if (x.date && x.date < Date.now() - 3 * J) continue;
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
        nouveaux += await this.ajouter(s, "papier", { titre: pp.title || x.title, url: `https://huggingface.co/papers/${pp.id}`, texte: String(pp.summary || "").slice(0, 900), date: Date.parse(x.publishedAt || pp.publishedAt) || Date.now(), extra: { votes: pp.upvotes || 0, arxiv: `https://arxiv.org/abs/${pp.id}` } });
      }
    } else if (s.type === "hn") {
      // histoires des dernières 36 h avec au moins 80 points, dont le titre parle d'IA
      const depuis = Math.floor((Date.now() - 36 * H) / 1000);
      const r = await (await chercher(`${s.url}?tags=story&numericFilters=created_at_i>${depuis},points>80&hitsPerPage=100`)).json();
      for (const h of r.hits || []) {
        if (!MOTS_IA.test(h.title || "") && !MOTS_DEPOT.test(h.title || "")) continue;
        lus++;
        const fil = `https://news.ycombinator.com/item?id=${h.objectID}`;
        nouveaux += await this.ajouter(s, "article", { titre: h.title, url: h.url || fil, texte: sansHtml(h.story_text || "").slice(0, 900), date: (h.created_at_i || 0) * 1000, extra: { points: h.points || 0, commentaires: h.num_comments || 0, hn: fil } }, "hn:" + h.objectID);
      }
    } else if (s.type === "hfmodeles" || s.type === "hflibres") {
      const urls = s.type === "hfmodeles" ? [s.url] : ["abliterated", "uncensored", "heretic"].map((q) => `${s.url}?search=${q}&sort=trendingScore&limit=40`);
      const vus = new Set();
      for (const u of urls) {
        const liste = await (await chercher(u)).json();
        for (const m of liste || []) {
          if (!m.id || vus.has(m.id)) continue;
          vus.add(m.id);
          const cree = Date.parse(m.createdAt || "") || 0;
          // seulement les modèles récents (30 jours ; 60 pour les non censurés)
          if (!cree || cree < Date.now() - (s.type === "hfmodeles" ? 30 : 60) * J) continue;
          if (s.type === "hflibres" && (m.trendingScore || 0) < 3 && (m.likes || 0) < 20) continue;
          lus++;
          const params = tailleModele(m.id);
          const type = TYPES_MODELE[m.pipeline_tag] || (m.pipeline_tag ? m.pipeline_tag : "Autre");
          const extra = { modele: m.id, auteur: m.id.split("/")[0], pipeline: m.pipeline_tag || "", type, likes: m.likes || 0, telechargements: m.downloads || 0, tendance: m.trendingScore || 0, params, gguf: (m.tags || []).includes("gguf") || /gguf/i.test(m.id), cree };
          const libre = s.type === "hflibres" || /abliterat|uncensor|heretic|unfilter|nsfw/i.test(m.id);
          nouveaux += await this.ajouter(s, libre ? "libre" : "modele", { titre: m.id, url: `https://huggingface.co/${m.id}`, texte: `Type : ${type}. Bibliothèque : ${m.library_name || "?"}. Étiquettes : ${(m.tags || []).filter((t) => !/^(region|license|arxiv|base_model|dataset):/.test(t)).slice(0, 15).join(", ")}`, date: cree, extra }, "hf:" + m.id);
        }
      }
    } else if (s.type === "trending") {
      const html = await (await chercher(s.url)).text();
      const liste = lireTrending(html);
      if (!liste.length) throw new Error("page Trending illisible");
      const semaine = /weekly/.test(s.url);
      for (const r of liste) {
        if (!MOTS_DEPOT.test(`${r.nom.replace(/[-_/]/g, " ")} ${r.desc}`)) continue;
        lus++;
        nouveaux += this.suivreDepot({ nom: r.nom, desc: r.desc, langage: r.langage, etoiles: r.total, periode: semaine ? Math.round(r.periode / 7) : r.periode, signal: semaine ? "tendance de la semaine" : "tendance du jour" });
      }
    } else if (s.type === "ghsearch") {
      // nouveaux dépôts (7 jours) et dépôts récents (30 jours) qui décollent
      for (const [jours, mini] of [[7, 30], [30, 400]]) {
        const d = new Date(Date.now() - jours * J).toISOString().slice(0, 10);
        const q = `created:>=${d} stars:>${mini}`;
        const r = await (await chercher(`${s.url}?q=${encodeURIComponent(q)}&sort=stars&order=desc&per_page=50`, { headers: { accept: "application/vnd.github+json" } })).json();
        for (const x of r.items || []) {
          if (!MOTS_DEPOT.test(`${x.full_name.replace(/[-_/]/g, " ")} ${x.description || ""} ${(x.topics || []).join(" ")}`)) continue;
          lus++;
          nouveaux += this.suivreDepot({ nom: x.full_name, desc: x.description || "", langage: x.language || "", licence: x.license?.spdx_id || null, etoiles: x.stargazers_count, cree: Date.parse(x.created_at) || null, signal: "nouveau dépôt qui décolle" });
        }
      }
    }
    return { lus, nouveaux, note };
  }

  // vitesse d'un dépôt en étoiles par jour
  vitesse(d) {
    const hist = JSON.parse(d.hist || "[]");
    let v = 0;
    if (hist.length >= 2) {
      const [t0, s0] = hist[0], [t1, s1] = hist[hist.length - 1];
      if (t1 - t0 >= 4 * H) v = ((s1 - s0) / (t1 - t0)) * J;
    }
    if (d.periode) v = Math.max(v, d.periode);
    if (d.cree && d.etoiles) v = Math.max(v, d.etoiles / Math.max(1, (Date.now() - d.cree) / J));
    return Math.round(v);
  }

  // ---------- fabrication d'une édition ----------
  async fabriquer(creneauForce) {
    const t0 = Date.now();
    const { jour, heure, joli } = heureLocale();
    const pr = this.prefs();
    const creneau = creneauForce || (heure < 13 ? "matin" : "soir");
    const id = `${jour}-${creneau}`;
    const depuis = Date.now() - 36 * H;
    // les modèles non censurés arrivés par la liste « tendance » vont dans leur rubrique
    for (const m of ["%abliterat%", "%uncensor%", "%heretic%", "%unfilter%", "%nsfw%"]) this.sql.exec(`UPDATE items SET genre='libre' WHERE genre='modele' AND lower(titre) LIKE ?`, m);
    const src = Object.fromEntries(SOURCES.map((s) => [s.id, s]));
    const prendre = (genres, apres = depuis) => this.sql.exec(
      `SELECT * FROM items WHERE edition IS NULL AND date >= ? AND genre IN (${genres.map(() => "?").join(",")}) ORDER BY date DESC LIMIT 600`, apres, ...genres)
      .toArray().filter((x) => !pr.masques.includes(x.source)).map((x) => ({ ...x, extra: JSON.parse(x.extra || "{}") }));
    const prescore = (x) => {
      const age = Math.max(0, (Date.now() - x.date) / H);
      const e = x.extra || {};
      let bonus = 1;
      if (x.genre === "papier") bonus = Math.min(1.5, 0.6 + (e.votes || 0) / 40);
      else if (x.genre === "modele" || x.genre === "libre") bonus = Math.min(2, 0.5 + (e.tendance || 0) / 40 + (e.likes || 0) / 400);
      else if (e.points) bonus = Math.min(2, 0.8 + e.points / 300);
      const frais = x.genre === "modele" || x.genre === "libre" ? 1 : 1.2 - Math.min(1, age / 36);
      return (src[x.source]?.poids || 1) * (pr.sources[x.source] || 1) * bonus * frais;
    };
    // premier regroupement grossier par titres proches (même langue)
    const regrouper = (liste) => {
      const groupes = [];
      for (const x of liste.sort((a, b) => prescore(b) - prescore(a))) {
        const m = motsTitre(x.titre);
        const g = groupes.find((g) => jaccard(g.mots, m) >= 0.45);
        if (g) g.autres.push(x); else groupes.push({ tete: x, mots: m, autres: [] });
      }
      return groupes;
    };
    const articles = regrouper(prendre(["article", "papier", "version"])).slice(0, 60);
    const videos = regrouper(prendre(["video"])).slice(0, 30);
    const modeles = regrouper(prendre(["modele"], 0)).slice(0, 16);
    const libres = regrouper(prendre(["libre"], 0)).slice(0, 10);
    // dépôts : jamais montrés, classés par vitesse d'étoiles
    const depotsBruts = this.sql.exec(`SELECT * FROM depots WHERE montre IS NULL`).toArray()
      .map((d) => ({ ...d, v: this.vitesse(d) })).filter((d) => d.v >= 20).sort((a, b) => b.v - a.v).slice(0, 18);
    const depots = depotsBruts.map((d) => ({ tete: { id: "gh:" + d.nom, source: "trending", famille: "GitHub", genre: "depot", titre: d.nom, url: `https://github.com/${d.nom}`, texte: d.descr || "", date: d.premier, extra: { depot: d.nom, langage: d.langage, licence: d.licence, etoiles: d.etoiles, vitesse: d.v, signal: d.signal } }, autres: [] }));
    const tous = [...articles, ...videos, ...modeles, ...libres, ...depots];
    if (!tous.length) return { id, vide: true, note: "aucune nouveauté depuis la dernière édition" };

    const analyses = await this.analyser(tous.map((g) => g.tete));
    let cartes = [];
    tous.forEach((g, i) => {
      const a = analyses[i];
      if (!a) return;
      const x = g.tete;
      const rub = ["modeles", "idees", "local", "recherche"].includes(a.rubrique) ? a.rubrique : "recherche";
      let imp = Math.max(1, Math.min(5, +a.importance || 2));
      if (x.genre === "video" && /promo/i.test(a.type_video || "")) imp = Math.min(imp, 1);
      let score = imp * (POIDS_RUBRIQUES[rub] || 1) * (pr.rubriques[rub] || 1) * prescore(x);
      if (x.genre === "depot") score = imp * Math.log10(10 + (x.extra.vitesse || 0));
      const autres = g.autres.slice(0, 6).map((o) => ({ source: src[o.source]?.nom || o.source, url: o.url, titre: o.titre }));
      cartes.push({
        id: x.id, genre: x.genre, rubrique: rub, importance: imp, score: +score.toFixed(3),
        titre: a.titre || x.titre, titre_original: x.titre, resume: a.resume || "", pourquoi: a.pourquoi || "", statut: a.statut || "",
        type_video: a.type_video || "", essai: a.essai || "",
        source: src[x.source]?.nom || x.source, source_id: x.source, famille: x.famille, url: x.url, date: x.date,
        extra: x.extra, autres, _membres: [x, ...g.autres],
      });
    });

    // élimination des doublons sur toute l'édition + sujets déjà publiés ces 7 derniers jours
    cartes = await this.dedoublonner(cartes);

    const actives = cartes.filter((c) => !c.deja_vu);
    const choisir = (filtre, n) => actives.filter(filtre).sort((a, b) => b.score - a.score).slice(0, n);
    const estInfo = (c) => ["article", "papier", "version"].includes(c.genre);
    const infos = actives.filter((c) => estInfo(c) && c.importance >= 2).sort((a, b) => b.score - a.score);
    const une = [];
    const parSource = {};
    for (const c of infos) {
      if (une.length >= TAILLE.une) break;
      if ((parSource[c.source_id] || 0) >= 2) continue;
      parSource[c.source_id] = (parSource[c.source_id] || 0) + 1;
      une.push(c);
    }
    const reste = infos.filter((c) => !une.includes(c));
    const rubriques = RUBRIQUES.map((r) => ({ id: r.id, titre: r.titre, cartes: reste.filter((c) => c.rubrique === r.id).slice(0, TAILLE.parRubrique) })).filter((r) => r.cartes.length);
    const sections = {
      modeles: choisir((c) => c.genre === "modele", TAILLE.modeles),
      libres: choisir((c) => c.genre === "libre", TAILLE.libres),
      videos: choisir((c) => c.genre === "video" && c.importance >= 2, TAILLE.videos),
      depots: choisir((c) => c.genre === "depot", TAILLE.depots),
    };
    const retenues = [...une, ...rubriques.flatMap((r) => r.cartes), ...sections.modeles, ...sections.libres, ...sections.videos, ...sections.depots];

    // lecture complète des sujets retenus les plus importants → résumé plus riche
    const aLire = [...[...une, ...rubriques.flatMap((r) => r.cartes)].slice(0, TAILLE.lectureComplete), ...sections.modeles, ...sections.libres, ...sections.depots];
    await this.approfondir(aLire);

    // marquer comme publiés : seulement ce qui est montré (le reste peut revenir s'il reste frais)
    for (const c of retenues) {
      if (c.genre === "depot") this.sql.exec(`UPDATE depots SET montre=? WHERE nom=?`, id, c.extra.depot);
      for (const o of c._membres || []) if (o.id && !String(o.id).startsWith("gh:")) this.sql.exec(`UPDATE items SET edition=? WHERE id=?`, id, o.id);
      this.sql.exec(`INSERT OR REPLACE INTO sujets(id,titre,ts) VALUES(?,?,?)`, `${id}:${c.id}`, c.titre, Date.now());
    }
    // les éléments écartés comme doublons d'un sujet passé ne reviennent pas
    for (const c of cartes.filter((c) => c.deja_vu)) for (const o of c._membres || []) if (o.id && !String(o.id).startsWith("gh:")) this.sql.exec(`UPDATE items SET edition=? WHERE id=?`, id + ":doublon", o.id);
    const propre = (c) => { const { _membres, ...r } = c; return r; };
    const edition = {
      id, creneau, jour, titre: `Édition du ${creneau} — ${joli}`, cree: Date.now(), version: VERSION,
      une: une.map(propre), rubriques: rubriques.map((r) => ({ ...r, cartes: r.cartes.map(propre) })),
      modeles: sections.modeles.map(propre), libres: sections.libres.map(propre), videos: sections.videos.map(propre), depots: sections.depots.map(propre),
      stats: { candidats: tous.length, retenus: retenues.length, doublons_retires: cartes.filter((c) => c.deja_vu).length + (this._fusions || 0), duree_s: 0, modele: MODELE },
    };
    edition.stats.duree_s = Math.round((Date.now() - t0) / 1000);
    this.sql.exec(`INSERT OR REPLACE INTO editions(id,cree,contenu) VALUES(?,?,?)`, id, Date.now(), JSON.stringify(edition));
    this.ecrire("derniere_edition", { id, quand: Date.now(), retenus: edition.stats.retenus, duree_s: edition.stats.duree_s });
    return { id, retenus: edition.stats.retenus, candidats: tous.length, doublons_retires: edition.stats.doublons_retires, duree_s: edition.stats.duree_s };
  }

  async ia(messages, max = 3000) {
    const r = await this.env.AI.run(MODELE, { messages, max_tokens: max, temperature: 0.2 });
    return typeof r?.response === "string" ? r.response : JSON.stringify(r?.response ?? r);
  }

  // Une seule passe sur toute l'édition : regroupe les mêmes événements (toutes langues, toutes sources)
  // et repère ce qui a déjà été publié ces 7 derniers jours.
  async dedoublonner(cartes) {
    this._fusions = 0;
    const infos = cartes.filter((c) => ["article", "papier", "version", "video"].includes(c.genre));
    if (infos.length < 2) return cartes;
    const passes = this.sql.exec(`SELECT titre FROM sujets ORDER BY ts DESC LIMIT 400`).toArray().map((r) => r.titre);
    const liste = infos.map((c, i) => `${i}. ${c.titre} — ${c.titre_original}`).join("\n");
    const anciens = passes.map((t, i) => `P${i}. ${t}`).join("\n");
    const consigne = `Tu es l'éditeur d'une revue de presse IA. Voici les sujets candidats de l'édition, puis les sujets déjà publiés ces 7 derniers jours.
1) Regroupe les candidats qui parlent du même sujet : même annonce, même produit, même modèle, même étude — y compris tous les articles et vidéos sur la sortie d'un même modèle (tests, classements, conseils, démonstrations, avis sur ce modèle vont TOUS dans le groupe de cette sortie), même s'ils sont dans des langues différentes ou viennent de sources différentes. Le lecteur ne veut voir qu'une seule carte par sujet.
2) Liste les candidats qui répètent un sujet déjà publié, SAUF s'ils apportent un fait nouveau important (nouvelle version, chiffres nouveaux, disponibilité réelle).
Réponds UNIQUEMENT par un objet JSON : {"groupes": [[numéros], ...], "deja_publies": [numéros]}. Ne mets dans "groupes" que les groupes d'au moins 2 numéros.`;
    let r;
    try {
      r = lireJson(await this.ia([{ role: "system", content: consigne }, { role: "user", content: `CANDIDATS :\n${liste}\n\nDÉJÀ PUBLIÉS :\n${anciens || "(aucun)"}` }], 1500), "{");
    } catch (e) { this.ecrire("derniere_erreur_ia", { quand: Date.now(), etape: "doublons", erreur: String(e).slice(0, 300) }); return cartes; }
    const retirer = new Set();
    for (const g of r.groupes || []) {
      const membres = [...new Set((g || []).map((n) => infos[+n]).filter(Boolean))];
      if (membres.length < 2) continue;
      membres.sort((a, b) => (a.genre === "video") - (b.genre === "video") || b.score - a.score);
      const chef = membres[0];
      for (const m of membres.slice(1)) {
        if (retirer.has(m)) continue;
        chef.autres.push({ source: m.genre === "video" ? `${m.extra?.chaine || m.source} (vidéo)` : m.source, url: m.url, titre: m.titre_original });
        chef._membres.push(...(m._membres || []));
        chef.score += 0.15 * m.score; // un sujet repris partout est plus important
        retirer.add(m);
        this._fusions++;
      }
    }
    for (const n of r.deja_publies || []) { const c = infos[+n]; if (c && !retirer.has(c)) { c.deja_vu = true; } }
    return cartes.filter((c) => !retirer.has(c) && !c.deja_vu).concat(cartes.filter((c) => c.deja_vu));
  }

  // Lit la page complète (article, page du modèle) et refait un résumé plus riche
  async approfondir(cartes) {
    const consigne = `Tu es le rédacteur de « Radar IA », une veille en français pour un lecteur suisse qui teste l'IA chez lui et crée des apps.
À partir du texte fourni, écris UNIQUEMENT un objet JSON : {"titre": "...", "resume": "...", "pourquoi": "..."}.
- "titre" : titre informatif en français correct, 7 à 14 mots, qui dit ce que c'est et ce que ça apporte (pour un dépôt ou un modèle : son nom suivi de ce qu'il fait).
- "resume" : 4 à 5 phrases en français, avec les faits concrets du texte (chiffres, noms, prix, dates, disponibilité, taille du modèle, licence). Rédige avec tes propres mots, ne recopie pas de longues phrases, n'invente rien.
- "pourquoi" : une phrase sur ce que cela change concrètement pour lui (tester chez soi, matériel nécessaire, créer une app) ; vide si rien.`;
    await parPaquets(cartes, 6, async (c) => {
      let texte = "";
      try {
        if (c.genre === "modele" || c.genre === "libre") {
          const md = await (await chercher(`https://huggingface.co/${c.extra.modele}/raw/main/README.md`, {}, 12000)).text();
          texte = md.replace(/^---[\s\S]*?---/, "").replace(/<[^>]+>/g, " ").replace(/!\[[^\]]*\]\([^)]*\)/g, "").replace(/\s+/g, " ").slice(0, 6000);
        } else if (c.genre === "depot") {
          const md = await (await chercher(`https://raw.githubusercontent.com/${c.extra.depot}/HEAD/README.md`, {}, 12000)).text();
          texte = md.replace(/<[^>]+>/g, " ").replace(/!\[[^\]]*\]\([^)]*\)/g, "").replace(/\s+/g, " ").slice(0, 6000);
        } else if (c.genre === "article" && !/youtube\.com|reddit\.com/.test(c.url)) {
          const html = await (await chercher(c.url, { headers: { accept: "text/html" } }, 12000)).text();
          texte = texteArticle(html);
        }
      } catch (e) { texte = ""; }
      if (texte.length < 400) return;
      try {
        const r = lireJson(await this.ia([{ role: "system", content: consigne }, { role: "user", content: `Titre : ${c.titre_original}\n\nTexte :\n${texte}` }], 700), "{");
        if (r.resume && r.resume.length > 80) { c.resume = r.resume; c.lu = true; }
        if (r.pourquoi) c.pourquoi = r.pourquoi;
        if (r.titre && r.titre.length > 10 && (c.genre === "depot" || c.genre === "modele" || c.genre === "libre")) c.titre = r.titre;
      } catch (e) { this.ecrire("derniere_erreur_ia", { quand: Date.now(), etape: "lecture", erreur: String(e).slice(0, 300) }); }
    });
  }

  // Résumé, traduction et classement en français par Workers AI, par paquets de 8
  async analyser(items) {
    const res = new Array(items.length).fill(null);
    const PAQUET = 8;
    const consigne = `Tu es le rédacteur exigeant de « Radar IA », une veille en français sur l'intelligence artificielle pour un lecteur suisse curieux et pragmatique (modèles, IA locale sur son ordinateur, matériel, agents, création d'apps).
Pour chaque élément reçu, réponds UNIQUEMENT par un tableau JSON, un objet par élément, dans le même ordre, avec ces clés :
- "n" : le numéro de l'élément
- "titre" : titre informatif en français correct (majuscule initiale, accents, noms propres en majuscule), 7 à 14 mots, qui dit ce qui se passe — par exemple « Anthropic publie une étude sur la fiabilité des agents de codage ». Pour un modèle : son nom, son type et ce qu'il apporte.
- "resume" : 2 à 3 phrases en français, factuelles, rédigées avec tes propres mots ; n'invente rien qui ne figure pas dans le texte
- "pourquoi" : une phrase : ce que cela change concrètement pour un utilisateur qui teste l'IA chez lui ou crée des apps (vide si rien)
- "rubrique" : "modeles" (sortie ou mise à jour de modèle, benchmark), "idees" (outils, usages, agents, automatisation, création d'apps, dépôts), "local" (IA sur son ordinateur, GPU, puces, matériel, prix), "recherche" (papiers, robotique, entreprises, régulation, sécurité, société)
- "importance" : 1 à 5. Sois SÉVÈRE : 5 = rare, nouveauté majeure qui change ce qu'on peut faire ; 4 = vraie nouveauté utile ; 3 = intéressant ; 2 = secondaire ; 1 = anecdotique, promotionnel, tutoriel générique, titre racoleur, « devenir riche avec l'IA », récapitulatif sans fait nouveau.
- "statut" : "annoncé", "disponible", "testé", "préliminaire" ou "rumeur"
- pour une vidéo seulement, "type_video" : "test", "démo", "tutoriel", "analyse", "actualité" ou "promotion"
- pour un dépôt GitHub seulement, "essai" : "lecture seule", "installation simple", "environnement isolé conseillé" ou "préparation avancée"
Aucun texte hors du tableau JSON.`;
    const noms = { article: "article", papier: "papier de recherche", version: "nouvelle version logicielle", video: "vidéo YouTube", depot: "dépôt GitHub", modele: "nouveau modèle sur Hugging Face", libre: "modèle non censuré sur Hugging Face" };
    const debuts = [];
    for (let i = 0; i < items.length; i += PAQUET) debuts.push(i);
    await parPaquets(debuts, 3, async (i) => {
      const lot = items.slice(i, i + PAQUET);
      const entree = lot.map((x, k) => {
        const e = x.extra || {};
        let plus = "";
        if (x.genre === "depot") plus = ` | langage ${e.langage || "?"} | ${e.etoiles || 0} étoiles, +${e.vitesse || 0} par jour`;
        else if (x.genre === "video") plus = ` | chaîne ${e.chaine || ""}`;
        else if (x.genre === "modele" || x.genre === "libre") plus = ` | ${e.type} | ${e.params ? e.params + " milliards de paramètres | " : ""}${e.likes} likes, ${e.telechargements} téléchargements`;
        else if (e.points) plus = ` | ${e.points} points et ${e.commentaires} commentaires sur Hacker News`;
        return `#${i + k} [${noms[x.genre] || x.genre} — ${SOURCES.find((s) => s.id === x.source)?.nom || x.source}${plus}]\nTitre : ${x.titre}\nTexte : ${(x.texte || "").slice(0, 700)}`;
      }).join("\n\n");
      let tableau = null;
      for (let essai = 0; essai < 2 && !tableau; essai++) {
        try {
          tableau = lireJson(await this.ia([{ role: "system", content: consigne }, { role: "user", content: entree }], 3500), "[");
          if (!Array.isArray(tableau)) tableau = null;
        } catch (e) { this.ecrire("derniere_erreur_ia", { quand: Date.now(), etape: "analyse", erreur: String(e).slice(0, 300) }); }
      }
      for (const a of tableau || []) {
        const n = parseInt(a?.n, 10);
        if (n >= i && n < i + lot.length) res[n] = a;
      }
      // si l'IA a échoué, on garde l'élément brut plutôt que de le perdre
      lot.forEach((x, k) => { if (!res[i + k]) res[i + k] = { titre: x.titre, resume: (x.texte || "").slice(0, 280), rubrique: x.genre === "depot" ? "idees" : x.genre === "modele" || x.genre === "libre" ? "modeles" : "recherche", importance: 2, statut: "", brut: true }; });
    });
    return res;
  }
}
