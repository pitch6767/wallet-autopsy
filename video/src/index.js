// video — Gemini regarde les vidéos YouTube pour Claude
// La clé Gemini n'est jamais en clair : elle est chiffrée avec la clé publique du coffre (Durable Object)
import { DurableObject } from "cloudflare:workers";

const VERSION = "1.1.0";
const MORCEAU = 300; // secondes par morceau analysé (5 min : plus de détail par minute)
const GEMINI = "https://generativelanguage.googleapis.com/v1beta";

const b64 = (buf) => btoa(String.fromCharCode(...new Uint8Array(buf)));
const deb64 = (s) => Uint8Array.from(atob(s), (c) => c.charCodeAt(0));
const hms = (s) => {
  s = Math.max(0, Math.round(s));
  const h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60), x = s % 60;
  const p = (n) => String(n).padStart(2, "0");
  return h ? `${h}:${p(m)}:${p(x)}` : `${p(m)}:${p(x)}`;
};
const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const json = (o, st = 200) =>
  new Response(JSON.stringify(o, null, 1), { status: st, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" } });

function idYoutube(u) {
  if (!u) return null;
  u = String(u).trim();
  if (/^[\w-]{11}$/.test(u)) return u;
  const m = u.match(/(?:youtu\.be\/|[?&]v=|\/shorts\/|\/live\/|\/embed\/)([\w-]{11})/);
  return m ? m[1] : null;
}
const tempsEnSec = (t) => {
  if (t == null || t === "") return null;
  if (/^\d+$/.test(t)) return +t;
  const p = String(t).split(":").map(Number);
  if (p.some(isNaN)) return null;
  return p.reduce((a, b) => a * 60 + b, 0);
};

export default {
  async fetch(req, env) {
    const url = new URL(req.url);
    const p = url.pathname;
    const coffre = env.COFFRE.get(env.COFFRE.idFromName("principal"));
    if (p === "/" || p === "/index.html") {
      const r = await env.ASSETS.fetch(new Request(new URL("/index.html", url)));
      return new Response(r.body, { headers: { "content-type": "text/html; charset=utf-8", "cache-control": "no-store, max-age=0" } });
    }
    if (p.startsWith("/api/") || p.startsWith("/r/")) {
      const r = await coffre.fetch(req);
      return r;
    }
    return env.ASSETS.fetch(req);
  },
};

export class Coffre extends DurableObject {
  constructor(ctx, env) {
    super(ctx, env);
    this.sql = ctx.storage.sql;
    this.sql.exec(`CREATE TABLE IF NOT EXISTS kv(k TEXT PRIMARY KEY, v TEXT)`);
    this.sql.exec(`CREATE TABLE IF NOT EXISTS jobs(id TEXT PRIMARY KEY, url TEXT, titre TEXT, auteur TEXT, statut TEXT, duree INTEGER,
      total INTEGER, faits INTEGER DEFAULT 0, fps REAL, resume TEXT, modele TEXT, cree INTEGER, maj INTEGER, erreur TEXT, essais INTEGER DEFAULT 0)`);
    try { this.sql.exec(`ALTER TABLE jobs ADD COLUMN source_duree TEXT`); } catch {}
    this.sql.exec(`CREATE TABLE IF NOT EXISTS morceaux(job TEXT, idx INTEGER, debut INTEGER, fin INTEGER, texte TEXT, PRIMARY KEY(job, idx))`);
    this.sql.exec(`CREATE TABLE IF NOT EXISTS questions(qid INTEGER PRIMARY KEY AUTOINCREMENT, job TEXT, q TEXT, debut INTEGER, fin INTEGER, fps REAL,
      reponse TEXT, statut TEXT, cree INTEGER, erreur TEXT, essais INTEGER DEFAULT 0)`);
  }
  get(k) { const r = this.sql.exec(`SELECT v FROM kv WHERE k=?`, k).toArray(); return r.length ? r[0].v : null; }
  set(k, v) { this.sql.exec(`INSERT OR REPLACE INTO kv(k,v) VALUES(?,?)`, k, v); }
  un(q, ...a) { const r = this.sql.exec(q, ...a).toArray(); return r[0] || null; }
  tous(q, ...a) { return this.sql.exec(q, ...a).toArray(); }

  // ---------- clés ----------
  async clePublique() {
    let pub = this.get("pub");
    if (!pub) {
      const kp = await crypto.subtle.generateKey({ name: "ECDH", namedCurve: "P-256" }, true, ["deriveBits"]);
      const priv = await crypto.subtle.exportKey("jwk", kp.privateKey);
      const pubj = await crypto.subtle.exportKey("jwk", kp.publicKey);
      this.set("priv", JSON.stringify(priv));
      pub = JSON.stringify({ kty: "EC", crv: "P-256", x: pubj.x, y: pubj.y });
      this.set("pub", pub);
    }
    return JSON.parse(pub);
  }
  async cleGemini() {
    if (this._cle) return this._cle;
    const chiffre = this.env.GEMINI_CHIFFRE;
    const privS = this.get("priv");
    if (!chiffre || !privS) return null;
    const c = JSON.parse(chiffre);
    const priv = await crypto.subtle.importKey("jwk", JSON.parse(privS), { name: "ECDH", namedCurve: "P-256" }, false, ["deriveBits"]);
    const epk = await crypto.subtle.importKey("jwk", c.epk, { name: "ECDH", namedCurve: "P-256" }, false, []);
    const bits = await crypto.subtle.deriveBits({ name: "ECDH", public: epk }, priv, 256);
    const h = await crypto.subtle.digest("SHA-256", bits);
    const k = await crypto.subtle.importKey("raw", h, "AES-GCM", false, ["decrypt"]);
    const clair = await crypto.subtle.decrypt({ name: "AES-GCM", iv: deb64(c.iv) }, k, deb64(c.ct));
    this._cle = new TextDecoder().decode(clair);
    return this._cle;
  }

  // ---------- Gemini ----------
  async modeles(force) {
    const cache = this.get("modeles");
    if (cache && !force) { const c = JSON.parse(cache); if (Date.now() - c.t < 6 * 3600e3) return c.liste; }
    const cle = await this.cleGemini();
    if (!cle) throw new Error("clé Gemini absente");
    const r = await fetch(`${GEMINI}/models?pageSize=1000`, { headers: { "x-goog-api-key": cle } });
    const j = await r.json();
    if (!r.ok) throw new Error(`liste des modèles : ${r.status} ${JSON.stringify(j).slice(0, 300)}`);
    const num = (n) => parseFloat((n.match(/gemini-(\d+(?:\.\d+)?)/) || [])[1] || 0);
    const ok = (j.models || [])
      .filter((m) => (m.supportedGenerationMethods || []).includes("generateContent"))
      .map((m) => m.name.replace("models/", ""))
      .filter((n) => /^gemini-\d+(\.\d+)?-flash$/.test(n) || /^gemini-\d+(\.\d+)?-pro$/.test(n));
    // flash d'abord (quota gratuit plus large), du plus récent au plus ancien, puis pro
    const flash = ok.filter((n) => n.endsWith("-flash")).sort((a, b) => num(b) - num(a));
    const pro = ok.filter((n) => n.endsWith("-pro")).sort((a, b) => num(b) - num(a));
    const liste = [...flash, ...pro];
    if (!liste.length) liste.push("gemini-2.5-flash");
    this.set("modeles", JSON.stringify({ t: Date.now(), liste }));
    return liste;
  }
  async gemini(parts, maxTokens = 32768) {
    const cle = await this.cleGemini();
    if (!cle) throw new Error("clé Gemini absente");
    const liste = await this.modeles();
    let derniere;
    for (const modele of liste.slice(0, 4)) {
      const r = await fetch(`${GEMINI}/models/${modele}:generateContent`, {
        method: "POST",
        headers: { "content-type": "application/json", "x-goog-api-key": cle },
        body: JSON.stringify({ contents: [{ role: "user", parts }], generationConfig: { temperature: 0.2, maxOutputTokens: maxTokens } }),
      });
      const j = await r.json().catch(() => ({}));
      if (r.ok) {
        const texte = (j.candidates?.[0]?.content?.parts || []).map((x) => x.text || "").join("").trim();
        if (texte) return { texte, modele };
        const raison = j.candidates?.[0]?.finishReason || j.promptFeedback?.blockReason || "?";
        derniere = `réponse vide (${raison})`;
        if (/RECITATION|SAFETY|PROHIBITED|BLOCK/i.test(raison)) break; // refus lié au contenu : un autre modèle refusera aussi
        continue;
      }
      derniere = `${modele} : ${r.status} ${JSON.stringify(j.error || j).slice(0, 400)}`;
      if (r.status === 400 && !/model/i.test(derniere)) break; // erreur sur la vidéo elle-même : inutile d'essayer d'autres modèles
    }
    throw new Error(derniere || "Gemini indisponible");
  }
  partVideo(url, debut, fin, fps) {
    const vm = {};
    if (debut != null) vm.startOffset = `${debut}s`;
    if (fin != null) vm.endOffset = `${fin}s`;
    if (fps) vm.fps = fps;
    const p = { fileData: { fileUri: url } };
    if (Object.keys(vm).length) p.videoMetadata = vm;
    return p;
  }

  // ---------- travail en arrière-plan ----------
  async relancer() { await this.ctx.storage.setAlarm(Date.now() + 500); }
  async alarm() {
    const fin = Date.now() + 12 * 60e3;
    try {
      while (Date.now() < fin) { if (!(await this.etape())) return; }
      await this.relancer();
    } catch (e) {
      this.set("derniere_erreur", String(e).slice(0, 500));
      await this.ctx.storage.setAlarm(Date.now() + 20e3);
    }
  }
  async etape() {
    const now = Date.now();
    const q = this.un(`SELECT * FROM questions WHERE statut='attente' AND essais<3 ORDER BY qid LIMIT 1`);
    if (q) {
      const job = this.un(`SELECT * FROM jobs WHERE id=?`, q.job);
      try {
        const prompt = `Question sur cette vidéo YouTube : ${q.q}
Réponds en français, précisément, en donnant les minutages. Recopie exactement tout texte affiché à l'écran qui sert la réponse (chiffres, code, tableaux, URL). Si la réponse n'est pas dans la vidéo, dis-le clairement. N'invente rien.`;
        const r = await this.gemini([this.partVideo(job.url, q.debut, q.fin, q.fps), { text: prompt }], 16384);
        this.sql.exec(`UPDATE questions SET reponse=?, statut='fait', erreur=NULL WHERE qid=?`, r.texte, q.qid);
      } catch (e) {
        this.sql.exec(`UPDATE questions SET essais=essais+1, erreur=?, statut=CASE WHEN essais+1>=3 THEN 'erreur' ELSE 'attente' END WHERE qid=?`, String(e).slice(0, 600), q.qid);
        await this.ctx.storage.setAlarm(Date.now() + 30e3); // pause avant de réessayer (quota Gemini)
        return false;
      }
      return true;
    }
    const j = this.un(`SELECT * FROM jobs WHERE statut IN ('attente','en cours') ORDER BY cree LIMIT 1`);
    if (!j) return false;
    // ---- 1) durée : d'abord la vraie durée publiée par YouTube, Gemini seulement en secours
    if (j.duree == null) {
      let d = null, source = null;
      try {
        const r = await fetch(`https://www.youtube.com/watch?v=${j.id}`, { headers: { "accept-language": "fr,en;q=0.8", "user-agent": "Mozilla/5.0" } });
        const h = await r.text();
        const m = h.match(/"lengthSeconds":"(\d+)"/) || h.match(/itemprop="duration" content="PT(?:(\d+)H)?(\d+)M(\d+)S"/);
        if (m) { d = m.length === 2 ? +m[1] : (+(m[1] || 0)) * 3600 + +m[2] * 60 + +m[3]; source = "YouTube"; }
      } catch {}
      if (!d) {
        try {
          const r = await this.gemini([this.partVideo(j.url, null, null, 0.2), { text: "Quelle est la durée totale exacte de cette vidéo ? Réponds uniquement au format H:MM:SS." }], 200);
          const m = r.texte.match(/(\d+:)?\d{1,2}:\d{2}/);
          d = m ? tempsEnSec(m[0]) : null; source = "estimée par Gemini";
        } catch (e) {
          this.sql.exec(`UPDATE jobs SET essais=essais+1, erreur=?, maj=?, statut=CASE WHEN essais+1>=3 THEN 'erreur' ELSE statut END WHERE id=?`, `durée : ${String(e).slice(0, 500)}`, now, j.id);
          await this.ctx.storage.setAlarm(Date.now() + 30e3);
          return false;
        }
      }
      if (!d) {
        this.sql.exec(`UPDATE jobs SET statut='erreur', erreur='durée introuvable', maj=? WHERE id=?`, now, j.id);
        return true;
      }
      this.sql.exec(`UPDATE jobs SET duree=?, source_duree=?, total=?, statut='en cours', maj=?, erreur=NULL, essais=0 WHERE id=?`, d, source, Math.max(1, Math.ceil(d / MORCEAU)), now, j.id);
      return true;
    }
    // ---- 2) chaque morceau de 5 min : 3 façons de demander, puis on passe au suivant sans bloquer la vidéo
    if (j.faits < j.total) {
      const idx = j.faits, debut = idx * MORCEAU, finM = Math.min(j.duree, debut + MORCEAU);
      const mode = j.essais; // 0 = complet, 1 = paroles reformulées (refus « récitation »), 2 = écran surtout
      const paroles = [
        "- PAROLES : transcription fidèle de ce qui est dit, dans la langue d'origine, en indiquant qui parle.",
        "- PAROLES : contenu détaillé de ce qui est dit, reformulé fidèlement en français (PAS de transcription mot pour mot ; citations de quelques mots maximum), en indiquant qui parle.",
        "- PAROLES : idée principale de ce qui est dit, en une phrase, reformulée en français.",
      ][Math.min(mode, 2)];
      const prompt = `Tu regardes l'extrait ${hms(debut)} → ${hms(finM)} d'une vidéo YouTube (durée totale ${hms(j.duree)}). Utilise des minutages ABSOLUS, comptés depuis le début de la vidéo.
Décris cet extrait de façon EXHAUSTIVE, en français, sous forme de chronologie. Une entrée OBLIGATOIRE toutes les 10 secondes (${hms(debut)}, ${hms(debut + 10)}, ${hms(debut + 20)}…) jusqu'à ${hms(finM)}, plus une entrée à chaque changement de plan :
[MM:SS]
- ÉCRAN : ce qui est montré, précisément (personnes, lieu, interface, site, graphique, diapositive, code…).
- TEXTE À L'ÉCRAN : recopie exacte de tout texte lisible (titres, chiffres, prix, tableaux, lignes de code, URL, noms de comptes, réglages). Écris [illisible] si tu ne peux pas lire.
${paroles}
N'invente rien : si tu n'es pas sûr d'un détail, écris [incertain]. Ne saute aucun intervalle de 10 secondes.`;
      try {
        const r = await this.gemini([this.partVideo(j.url, debut, finM, j.fps), { text: prompt }], 32768);
        const note = mode >= 1 ? `(Paroles reformulées : Gemini refuse de les recopier mot pour mot.)\n` : "";
        this.sql.exec(`INSERT OR REPLACE INTO morceaux(job,idx,debut,fin,texte) VALUES(?,?,?,?,?)`, j.id, idx, debut, finM, note + r.texte);
        this.sql.exec(`UPDATE jobs SET faits=faits+1, modele=?, maj=?, erreur=NULL, essais=0 WHERE id=?`, r.modele, now, j.id);
        return true;
      } catch (e) {
        const err = String(e).slice(0, 500);
        if (j.essais + 1 >= 4) {
          this.sql.exec(`INSERT OR REPLACE INTO morceaux(job,idx,debut,fin,texte) VALUES(?,?,?,?,?)`, j.id, idx, debut, finM, `[MORCEAU NON ANALYSÉ — ${err}]`);
          this.sql.exec(`UPDATE jobs SET faits=faits+1, maj=?, erreur=?, essais=0 WHERE id=?`, now, `morceau ${hms(debut)} non analysé : ${err}`, j.id);
          return true;
        }
        this.sql.exec(`UPDATE jobs SET essais=essais+1, erreur=?, maj=? WHERE id=?`, err, now, j.id);
        if (/RECITATION|SAFETY|PROHIBITED|BLOCK/i.test(err)) return true; // on reformule tout de suite
        await this.ctx.storage.setAlarm(Date.now() + 30e3); // quota ou panne : pause avant de réessayer
        return false;
      }
    }
    // ---- 3) synthèse
    const ms = this.tous(`SELECT texte FROM morceaux WHERE job=? ORDER BY idx`, j.id);
    const manquants = ms.filter((x) => x.texte.startsWith("[MORCEAU NON ANALYSÉ")).length;
    try {
      const r = await this.gemini([{ text: `Voici le compte rendu chronologique complet d'une vidéo YouTube${j.titre ? ` intitulée « ${j.titre} »` : ""}.
Écris en français :
1) RÉSUMÉ : 10 lignes maximum.
2) POINTS CLÉS : méthode, chiffres, affirmations importantes, chacun avec son minutage.
3) OUTILS, SITES, LIENS, COMPTES ET NOMS cités, avec minutage.
4) AFFIRMATIONS NON PROUVÉES OU PROMOTIONNELLES repérées (liens d'affiliation, gains invérifiables…).
N'invente rien.${manquants ? ` Attention : ${manquants} morceau(x) n'ont pas pu être analysés, signale-le.` : ""}

${ms.map((x) => x.texte).join("\n\n")}` }], 8192);
      this.sql.exec(`UPDATE jobs SET resume=?, statut='fait', maj=?, essais=0 WHERE id=?`, r.texte, now, j.id);
    } catch (e) {
      if (j.essais + 1 >= 3) this.sql.exec(`UPDATE jobs SET resume=?, statut='fait', maj=? WHERE id=?`, `[Synthèse indisponible : ${String(e).slice(0, 300)}]`, now, j.id);
      else { this.sql.exec(`UPDATE jobs SET essais=essais+1, erreur=? WHERE id=?`, String(e).slice(0, 500), j.id); await this.ctx.storage.setAlarm(Date.now() + 30e3); return false; }
    }
    return true;
  }

  // ---------- pages ----------
  texteJob(id) {
    const j = this.un(`SELECT * FROM jobs WHERE id=?`, id);
    if (!j) return null;
    const ms = this.tous(`SELECT * FROM morceaux WHERE job=? ORDER BY idx`, id);
    const qs = this.tous(`SELECT * FROM questions WHERE job=? ORDER BY qid`, id);
    let t = `VIDÉO : ${j.titre || id}${j.auteur ? ` — ${j.auteur}` : ""}\nLIEN : ${j.url}\nSTATUT : ${j.statut}${j.total ? ` (${j.faits}/${j.total} morceaux de 5 min)` : ""}${j.duree ? `\nDURÉE : ${hms(j.duree)}${j.source_duree ? ` (${j.source_duree})` : ""}` : ""}${ms.some((m) => m.texte.startsWith("[MORCEAU NON ANALYSÉ")) ? `\nMORCEAUX NON ANALYSÉS : ${ms.filter((m) => m.texte.startsWith("[MORCEAU NON ANALYSÉ")).map((m) => hms(m.debut)).join(", ")}` : ""}${j.modele ? `\nREGARDÉE PAR : ${j.modele}` : ""}${j.erreur ? `\nDERNIÈRE ERREUR : ${j.erreur}` : ""}\n`;
    if (j.resume) t += `\n==================== SYNTHÈSE ====================\n${j.resume}\n`;
    if (ms.length) t += `\n==================== CHRONOLOGIE COMPLÈTE ====================\n` + ms.map((m) => `----- ${hms(m.debut)} → ${hms(m.fin)} -----\n${m.texte}`).join("\n\n") + "\n";
    if (qs.length) t += `\n==================== QUESTIONS ====================\n` + qs.map((q) => `Q${q.qid} [${q.statut}]${q.debut != null ? ` (${hms(q.debut)}→${q.fin != null ? hms(q.fin) : "fin"})` : ""} : ${q.q}\n${q.reponse || q.erreur || "(en attente)"}`).join("\n\n") + "\n";
    return { j, t };
  }
  pageJob(id) {
    const r = this.texteJob(id);
    if (!r) return new Response("Vidéo inconnue", { status: 404 });
    const { j, t } = r;
    const encours = j.statut === "attente" || j.statut === "en cours" || this.un(`SELECT 1 x FROM questions WHERE job=? AND statut='attente'`, id);
    const html = `<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>${esc(j.titre || id)} — Vidéo</title>${encours ? `<meta http-equiv="refresh" content="10">` : ""}
<style>body{font:15px/1.5 -apple-system,system-ui,sans-serif;margin:0;background:#f6f6f4;color:#1b1b1b}main{max-width:860px;margin:0 auto;padding:16px}
a{color:#0b57d0}pre{white-space:pre-wrap;word-wrap:break-word;background:#fff;border:1px solid #ddd;border-radius:10px;padding:14px;font:14px/1.5 ui-monospace,Menlo,monospace}
form{display:flex;flex-direction:column;gap:8px;background:#fff;border:1px solid #ddd;border-radius:10px;padding:14px;margin:14px 0}
input,button{font:inherit;padding:10px;border-radius:8px;border:1px solid #bbb}button{background:#1b1b1b;color:#fff;border:0}.r{display:flex;gap:8px}.r input{flex:1;min-width:0}
@media(prefers-color-scheme:dark){body{background:#151515;color:#eee}pre,form{background:#1f1f1f;border-color:#333}input{background:#111;color:#eee;border-color:#444}a{color:#8ab4f8}button{background:#eee;color:#111}}</style></head>
<body data-app="video-app"><main><p><a href="/">← Accueil</a> · <a href="/r/${id}.txt">version texte</a> · <a href="${esc(j.url)}" target="_blank">ouvrir sur YouTube</a></p>
<h1 style="font-size:20px">${esc(j.titre || id)}</h1>${encours ? `<p>⏳ Gemini regarde la vidéo… cette page se met à jour toute seule.</p>` : ""}
<form action="/api/question" method="get"><input type="hidden" name="id" value="${id}"><input type="hidden" name="page" value="1">
<b>Poser une question sur la vidéo</b><input name="q" required placeholder="Ex. : que montre l'écran à 12:34 ?">
<div class="r"><input name="debut" placeholder="Début MM:SS"><input name="fin" placeholder="Fin MM:SS"></div><button>Demander</button></form>
<pre>${esc(t)}</pre></main></body></html>`;
    return new Response(html, { headers: { "content-type": "text/html; charset=utf-8", "cache-control": "no-store" } });
  }

  async fetch(req) {
    const url = new URL(req.url);
    const p = url.pathname, s = url.searchParams;
    const base = url.origin;
    try {
      if (p === "/api/cle-publique") return json(await this.clePublique());
      if (p === "/api/etat") {
        const etat = { app: "video-app", version: VERSION, cle_chiffree_presente: !!this.env.GEMINI_CHIFFRE, cle_publique_prete: !!this.get("pub") };
        try { etat.cle_ok = !!(await this.cleGemini()); } catch (e) { etat.cle_ok = false; etat.cle_erreur = String(e).slice(0, 200); }
        if (etat.cle_ok) { try { etat.modeles = await this.modeles(s.get("force") === "1"); } catch (e) { etat.modeles_erreur = String(e).slice(0, 400); } }
        etat.derniere_erreur = this.get("derniere_erreur");
        etat.en_attente = this.un(`SELECT COUNT(*) n FROM jobs WHERE statut IN ('attente','en cours')`).n;
        return json(etat);
      }
      if (p === "/api/analyser") {
        const id = idYoutube(s.get("url"));
        if (!id) return json({ erreur: "lien YouTube non reconnu" }, 400);
        const fps = Math.min(5, Math.max(0, parseFloat(s.get("fps") || "0"))) || null;
        const ex = this.un(`SELECT * FROM jobs WHERE id=?`, id);
        if (!ex || s.get("refaire") === "1" || ex.statut === "erreur") {
          let titre = null, auteur = null;
          try {
            const o = await fetch(`https://www.youtube.com/oembed?format=json&url=${encodeURIComponent("https://www.youtube.com/watch?v=" + id)}`);
            if (o.ok) { const oj = await o.json(); titre = oj.title; auteur = oj.author_name; }
          } catch {}
          this.sql.exec(`DELETE FROM morceaux WHERE job=?`, id);
          this.sql.exec(`INSERT OR REPLACE INTO jobs(id,url,titre,auteur,statut,duree,total,faits,fps,resume,modele,cree,maj,erreur,essais) VALUES(?,?,?,?,'attente',NULL,NULL,0,?,NULL,NULL,?,?,NULL,0)`,
            id, `https://www.youtube.com/watch?v=${id}`, titre, auteur, fps, Date.now(), Date.now());
          await this.relancer();
        }
        if (s.get("page") === "1") return Response.redirect(`${base}/r/${id}`, 303);
        return json({ id, page: `${base}/r/${id}`, texte: `${base}/r/${id}.txt`, statut: this.un(`SELECT statut FROM jobs WHERE id=?`, id).statut });
      }
      if (p === "/api/question") {
        const id = idYoutube(s.get("id")) || s.get("id");
        const job = this.un(`SELECT * FROM jobs WHERE id=?`, id);
        if (!job) return json({ erreur: "lance d'abord l'analyse de cette vidéo (/api/analyser)" }, 404);
        const q = (s.get("q") || "").trim();
        if (!q) return json({ erreur: "question vide" }, 400);
        const fps = Math.min(5, Math.max(0, parseFloat(s.get("fps") || "0"))) || null;
        this.sql.exec(`INSERT INTO questions(job,q,debut,fin,fps,statut,cree) VALUES(?,?,?,?,?,'attente',?)`, id, q, tempsEnSec(s.get("debut")), tempsEnSec(s.get("fin")), fps, Date.now());
        const qid = this.un(`SELECT last_insert_rowid() n`).n;
        await this.relancer();
        if (s.get("page") === "1") return Response.redirect(`${base}/r/${id}`, 303);
        return json({ qid, page: `${base}/r/${id}`, texte: `${base}/r/${id}.txt` });
      }
      if (p === "/api/liste") {
        return json(this.tous(`SELECT id,titre,auteur,statut,duree,faits,total,maj FROM jobs ORDER BY cree DESC LIMIT 50`).map((x) => ({ ...x, page: `${base}/r/${x.id}` })));
      }
      const m = p.match(/^\/r\/([\w-]{11})(\.txt)?$/);
      if (m) {
        if (m[2]) {
          const r = this.texteJob(m[1]);
          return new Response(r ? r.t : "Vidéo inconnue", { status: r ? 200 : 404, headers: { "content-type": "text/plain; charset=utf-8", "cache-control": "no-store" } });
        }
        return this.pageJob(m[1]);
      }
      return json({ erreur: "inconnu" }, 404);
    } catch (e) {
      return json({ erreur: String(e).slice(0, 500) }, 500);
    }
  }
}
