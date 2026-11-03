var __defProp = Object.defineProperty;
var __name = (target, value) => __defProp(target, "name", { value, configurable: true });

// src/index.js
import { DurableObject } from "cloudflare:workers";
var VERSION = "1.0.0";
var MORCEAU = 600;
var GEMINI = "https://generativelanguage.googleapis.com/v1beta";
var deb64 = /* @__PURE__ */ __name((s) => Uint8Array.from(atob(s), (c) => c.charCodeAt(0)), "deb64");
var hms = /* @__PURE__ */ __name((s) => {
  s = Math.max(0, Math.round(s));
  const h = Math.floor(s / 3600), m = Math.floor(s % 3600 / 60), x = s % 60;
  const p = /* @__PURE__ */ __name((n) => String(n).padStart(2, "0"), "p");
  return h ? `${h}:${p(m)}:${p(x)}` : `${p(m)}:${p(x)}`;
}, "hms");
var esc = /* @__PURE__ */ __name((s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]), "esc");
var json = /* @__PURE__ */ __name((o, st = 200) => new Response(JSON.stringify(o, null, 1), { status: st, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" } }), "json");
function idYoutube(u) {
  if (!u) return null;
  u = String(u).trim();
  if (/^[\w-]{11}$/.test(u)) return u;
  const m = u.match(/(?:youtu\.be\/|[?&]v=|\/shorts\/|\/live\/|\/embed\/)([\w-]{11})/);
  return m ? m[1] : null;
}
__name(idYoutube, "idYoutube");
var tempsEnSec = /* @__PURE__ */ __name((t) => {
  if (t == null || t === "") return null;
  if (/^\d+$/.test(t)) return +t;
  const p = String(t).split(":").map(Number);
  if (p.some(isNaN)) return null;
  return p.reduce((a, b) => a * 60 + b, 0);
}, "tempsEnSec");
var src_default = {
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
  }
};
var Coffre = class extends DurableObject {
  static {
    __name(this, "Coffre");
  }
  constructor(ctx, env) {
    super(ctx, env);
    this.sql = ctx.storage.sql;
    this.sql.exec(`CREATE TABLE IF NOT EXISTS kv(k TEXT PRIMARY KEY, v TEXT)`);
    this.sql.exec(`CREATE TABLE IF NOT EXISTS jobs(id TEXT PRIMARY KEY, url TEXT, titre TEXT, auteur TEXT, statut TEXT, duree INTEGER,
      total INTEGER, faits INTEGER DEFAULT 0, fps REAL, resume TEXT, modele TEXT, cree INTEGER, maj INTEGER, erreur TEXT, essais INTEGER DEFAULT 0)`);
    this.sql.exec(`CREATE TABLE IF NOT EXISTS morceaux(job TEXT, idx INTEGER, debut INTEGER, fin INTEGER, texte TEXT, PRIMARY KEY(job, idx))`);
    this.sql.exec(`CREATE TABLE IF NOT EXISTS questions(qid INTEGER PRIMARY KEY AUTOINCREMENT, job TEXT, q TEXT, debut INTEGER, fin INTEGER, fps REAL,
      reponse TEXT, statut TEXT, cree INTEGER, erreur TEXT, essais INTEGER DEFAULT 0)`);
  }
  get(k) {
    const r = this.sql.exec(`SELECT v FROM kv WHERE k=?`, k).toArray();
    return r.length ? r[0].v : null;
  }
  set(k, v) {
    this.sql.exec(`INSERT OR REPLACE INTO kv(k,v) VALUES(?,?)`, k, v);
  }
  un(q, ...a) {
    const r = this.sql.exec(q, ...a).toArray();
    return r[0] || null;
  }
  tous(q, ...a) {
    return this.sql.exec(q, ...a).toArray();
  }
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
    if (cache && !force) {
      const c = JSON.parse(cache);
      if (Date.now() - c.t < 6 * 36e5) return c.liste;
    }
    const cle = await this.cleGemini();
    if (!cle) throw new Error("cl\xE9 Gemini absente");
    const r = await fetch(`${GEMINI}/models?pageSize=1000`, { headers: { "x-goog-api-key": cle } });
    const j = await r.json();
    if (!r.ok) throw new Error(`liste des mod\xE8les : ${r.status} ${JSON.stringify(j).slice(0, 300)}`);
    const num = /* @__PURE__ */ __name((n) => parseFloat((n.match(/gemini-(\d+(?:\.\d+)?)/) || [])[1] || 0), "num");
    const ok = (j.models || []).filter((m) => (m.supportedGenerationMethods || []).includes("generateContent")).map((m) => m.name.replace("models/", "")).filter((n) => /^gemini-\d+(\.\d+)?-flash$/.test(n) || /^gemini-\d+(\.\d+)?-pro$/.test(n));
    const flash = ok.filter((n) => n.endsWith("-flash")).sort((a, b) => num(b) - num(a));
    const pro = ok.filter((n) => n.endsWith("-pro")).sort((a, b) => num(b) - num(a));
    const liste = [...flash, ...pro];
    if (!liste.length) liste.push("gemini-2.5-flash");
    this.set("modeles", JSON.stringify({ t: Date.now(), liste }));
    return liste;
  }
  async gemini(parts, maxTokens = 32768) {
    const cle = await this.cleGemini();
    if (!cle) throw new Error("cl\xE9 Gemini absente");
    const liste = await this.modeles();
    let derniere;
    for (const modele of liste.slice(0, 4)) {
      const r = await fetch(`${GEMINI}/models/${modele}:generateContent`, {
        method: "POST",
        headers: { "content-type": "application/json", "x-goog-api-key": cle },
        body: JSON.stringify({ contents: [{ role: "user", parts }], generationConfig: { temperature: 0.2, maxOutputTokens: maxTokens } })
      });
      const j = await r.json().catch(() => ({}));
      if (r.ok) {
        const texte = (j.candidates?.[0]?.content?.parts || []).map((x) => x.text || "").join("").trim();
        if (texte) return { texte, modele };
        derniere = `r\xE9ponse vide (${j.candidates?.[0]?.finishReason || j.promptFeedback?.blockReason || "?"})`;
        continue;
      }
      derniere = `${modele} : ${r.status} ${JSON.stringify(j.error || j).slice(0, 400)}`;
      if (r.status === 400 && !/model/i.test(derniere)) break;
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
  async relancer() {
    await this.ctx.storage.setAlarm(Date.now() + 500);
  }
  async alarm() {
    const fin = Date.now() + 12 * 6e4;
    try {
      while (Date.now() < fin) {
        if (!await this.etape()) return;
      }
      await this.relancer();
    } catch (e) {
      this.set("derniere_erreur", String(e).slice(0, 500));
      await this.ctx.storage.setAlarm(Date.now() + 2e4);
    }
  }
  async etape() {
    const now = Date.now();
    const q = this.un(`SELECT * FROM questions WHERE statut='attente' AND essais<3 ORDER BY qid LIMIT 1`);
    if (q) {
      const job = this.un(`SELECT * FROM jobs WHERE id=?`, q.job);
      try {
        const prompt = `Question sur cette vid\xE9o YouTube : ${q.q}
R\xE9ponds en fran\xE7ais, pr\xE9cis\xE9ment, en donnant les minutages. Recopie exactement tout texte affich\xE9 \xE0 l'\xE9cran qui sert la r\xE9ponse (chiffres, code, tableaux, URL). Si la r\xE9ponse n'est pas dans la vid\xE9o, dis-le clairement. N'invente rien.`;
        const r = await this.gemini([this.partVideo(job.url, q.debut, q.fin, q.fps), { text: prompt }], 16384);
        this.sql.exec(`UPDATE questions SET reponse=?, statut='fait', erreur=NULL WHERE qid=?`, r.texte, q.qid);
      } catch (e) {
        this.sql.exec(`UPDATE questions SET essais=essais+1, erreur=?, statut=CASE WHEN essais+1>=3 THEN 'erreur' ELSE 'attente' END WHERE qid=?`, String(e).slice(0, 600), q.qid);
        await this.ctx.storage.setAlarm(Date.now() + 3e4);
        return false;
      }
      return true;
    }
    const j = this.un(`SELECT * FROM jobs WHERE statut IN ('attente','en cours') AND essais<3 ORDER BY cree LIMIT 1`);
    if (!j) return false;
    try {
      if (j.duree == null) {
        const r2 = await this.gemini([this.partVideo(j.url, null, null, 0.2), { text: "Quelle est la dur\xE9e totale exacte de cette vid\xE9o ? R\xE9ponds uniquement au format H:MM:SS." }], 200);
        const m = r2.texte.match(/(\d+:)?\d{1,2}:\d{2}/);
        const d = m ? tempsEnSec(m[0]) : null;
        if (!d) throw new Error(`dur\xE9e illisible : ${r2.texte.slice(0, 100)}`);
        const total = Math.max(1, Math.ceil(d / MORCEAU));
        this.sql.exec(`UPDATE jobs SET duree=?, total=?, statut='en cours', modele=?, maj=?, erreur=NULL WHERE id=?`, d, total, r2.modele, now, j.id);
        return true;
      }
      if (j.faits < j.total) {
        const idx = j.faits, debut = idx * MORCEAU, finM = Math.min(j.duree, debut + MORCEAU);
        const prompt = `Tu regardes l'extrait ${hms(debut)} \u2192 ${hms(finM)} d'une vid\xE9o YouTube (dur\xE9e totale ${hms(j.duree)}). Utilise des minutages ABSOLUS, compt\xE9s depuis le d\xE9but de la vid\xE9o.
D\xE9cris cet extrait de fa\xE7on EXHAUSTIVE, en fran\xE7ais, sous forme de chronologie. Une entr\xE9e \xE0 chaque changement de plan, et au minimum toutes les 15 secondes :
[MM:SS]
- \xC9CRAN : ce qui est montr\xE9, pr\xE9cis\xE9ment (personnes, lieu, interface, site, graphique, diapositive, code\u2026).
- TEXTE \xC0 L'\xC9CRAN : recopie exacte de tout texte lisible (titres, chiffres, prix, tableaux, lignes de code, URL, noms de comptes, r\xE9glages). \xC9cris [illisible] si tu ne peux pas lire.
- PAROLES : transcription fid\xE8le de ce qui est dit, dans la langue d'origine, en indiquant qui parle.
N'invente rien, ne r\xE9sume pas, ne saute rien.`;
        const r2 = await this.gemini([this.partVideo(j.url, debut, finM, j.fps), { text: prompt }], 32768);
        this.sql.exec(`INSERT OR REPLACE INTO morceaux(job,idx,debut,fin,texte) VALUES(?,?,?,?,?)`, j.id, idx, debut, finM, r2.texte);
        this.sql.exec(`UPDATE jobs SET faits=faits+1, modele=?, maj=?, erreur=NULL, essais=0 WHERE id=?`, r2.modele, now, j.id);
        return true;
      }
      const chrono = this.tous(`SELECT texte FROM morceaux WHERE job=? ORDER BY idx`, j.id).map((x) => x.texte).join("\n\n");
      const r = await this.gemini([{ text: `Voici le compte rendu chronologique complet d'une vid\xE9o YouTube${j.titre ? ` intitul\xE9e \xAB ${j.titre} \xBB` : ""}.
\xC9cris en fran\xE7ais :
1) R\xC9SUM\xC9 : 10 lignes maximum.
2) POINTS CL\xC9S : m\xE9thode, chiffres, affirmations importantes, chacun avec son minutage.
3) OUTILS, SITES, LIENS, COMPTES ET NOMS cit\xE9s, avec minutage.
4) AFFIRMATIONS NON PROUV\xC9ES OU PROMOTIONNELLES rep\xE9r\xE9es (liens d'affiliation, gains inv\xE9rifiables\u2026).
N'invente rien.

${chrono}` }], 8192);
      this.sql.exec(`UPDATE jobs SET resume=?, statut='fait', maj=?, erreur=NULL WHERE id=?`, r.texte, now, j.id);
      return true;
    } catch (e) {
      this.sql.exec(`UPDATE jobs SET essais=essais+1, erreur=?, maj=?, statut=CASE WHEN essais+1>=3 THEN 'erreur' ELSE statut END WHERE id=?`, String(e).slice(0, 600), now, j.id);
      await this.ctx.storage.setAlarm(Date.now() + 3e4);
      return false;
    }
  }
  // ---------- pages ----------
  texteJob(id) {
    const j = this.un(`SELECT * FROM jobs WHERE id=?`, id);
    if (!j) return null;
    const ms = this.tous(`SELECT * FROM morceaux WHERE job=? ORDER BY idx`, id);
    const qs = this.tous(`SELECT * FROM questions WHERE job=? ORDER BY qid`, id);
    let t = `VID\xC9O : ${j.titre || id}${j.auteur ? ` \u2014 ${j.auteur}` : ""}
LIEN : ${j.url}
STATUT : ${j.statut}${j.total ? ` (${j.faits}/${j.total} morceaux de 10 min)` : ""}${j.duree ? `
DUR\xC9E : ${hms(j.duree)}` : ""}${j.modele ? `
REGARD\xC9E PAR : ${j.modele}` : ""}${j.erreur ? `
DERNI\xC8RE ERREUR : ${j.erreur}` : ""}
`;
    if (j.resume) t += `
==================== SYNTH\xC8SE ====================
${j.resume}
`;
    if (ms.length) t += `
==================== CHRONOLOGIE COMPL\xC8TE ====================
` + ms.map((m) => `----- ${hms(m.debut)} \u2192 ${hms(m.fin)} -----
${m.texte}`).join("\n\n") + "\n";
    if (qs.length) t += `
==================== QUESTIONS ====================
` + qs.map((q) => `Q${q.qid} [${q.statut}]${q.debut != null ? ` (${hms(q.debut)}\u2192${q.fin != null ? hms(q.fin) : "fin"})` : ""} : ${q.q}
${q.reponse || q.erreur || "(en attente)"}`).join("\n\n") + "\n";
    return { j, t };
  }
  pageJob(id) {
    const r = this.texteJob(id);
    if (!r) return new Response("Vid\xE9o inconnue", { status: 404 });
    const { j, t } = r;
    const encours = j.statut === "attente" || j.statut === "en cours" || this.un(`SELECT 1 x FROM questions WHERE job=? AND statut='attente'`, id);
    const html = `<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>${esc(j.titre || id)} \u2014 Vid\xE9o</title>${encours ? `<meta http-equiv="refresh" content="10">` : ""}
<style>body{font:15px/1.5 -apple-system,system-ui,sans-serif;margin:0;background:#f6f6f4;color:#1b1b1b}main{max-width:860px;margin:0 auto;padding:16px}
a{color:#0b57d0}pre{white-space:pre-wrap;word-wrap:break-word;background:#fff;border:1px solid #ddd;border-radius:10px;padding:14px;font:14px/1.5 ui-monospace,Menlo,monospace}
form{display:flex;flex-direction:column;gap:8px;background:#fff;border:1px solid #ddd;border-radius:10px;padding:14px;margin:14px 0}
input,button{font:inherit;padding:10px;border-radius:8px;border:1px solid #bbb}button{background:#1b1b1b;color:#fff;border:0}.r{display:flex;gap:8px}.r input{flex:1;min-width:0}
@media(prefers-color-scheme:dark){body{background:#151515;color:#eee}pre,form{background:#1f1f1f;border-color:#333}input{background:#111;color:#eee;border-color:#444}a{color:#8ab4f8}button{background:#eee;color:#111}}</style></head>
<body data-app="video-app"><main><p><a href="/">\u2190 Accueil</a> \xB7 <a href="/r/${id}.txt">version texte</a> \xB7 <a href="${esc(j.url)}" target="_blank">ouvrir sur YouTube</a></p>
<h1 style="font-size:20px">${esc(j.titre || id)}</h1>${encours ? `<p>\u23F3 Gemini regarde la vid\xE9o\u2026 cette page se met \xE0 jour toute seule.</p>` : ""}
<form action="/api/question" method="get"><input type="hidden" name="id" value="${id}"><input type="hidden" name="page" value="1">
<b>Poser une question sur la vid\xE9o</b><input name="q" required placeholder="Ex. : que montre l'\xE9cran \xE0 12:34 ?">
<div class="r"><input name="debut" placeholder="D\xE9but (MM:SS, facultatif)"><input name="fin" placeholder="Fin (MM:SS, facultatif)"></div><button>Demander</button></form>
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
        try {
          etat.cle_ok = !!await this.cleGemini();
        } catch (e) {
          etat.cle_ok = false;
          etat.cle_erreur = String(e).slice(0, 200);
        }
        if (etat.cle_ok) {
          try {
            etat.modeles = await this.modeles(s.get("force") === "1");
          } catch (e) {
            etat.modeles_erreur = String(e).slice(0, 400);
          }
        }
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
            if (o.ok) {
              const oj = await o.json();
              titre = oj.title;
              auteur = oj.author_name;
            }
          } catch {
          }
          this.sql.exec(`DELETE FROM morceaux WHERE job=?`, id);
          this.sql.exec(
            `INSERT OR REPLACE INTO jobs(id,url,titre,auteur,statut,duree,total,faits,fps,resume,modele,cree,maj,erreur,essais) VALUES(?,?,?,?,'attente',NULL,NULL,0,?,NULL,NULL,?,?,NULL,0)`,
            id,
            `https://www.youtube.com/watch?v=${id}`,
            titre,
            auteur,
            fps,
            Date.now(),
            Date.now()
          );
          await this.relancer();
        }
        if (s.get("page") === "1") return Response.redirect(`${base}/r/${id}`, 303);
        return json({ id, page: `${base}/r/${id}`, texte: `${base}/r/${id}.txt`, statut: this.un(`SELECT statut FROM jobs WHERE id=?`, id).statut });
      }
      if (p === "/api/question") {
        const id = idYoutube(s.get("id")) || s.get("id");
        const job = this.un(`SELECT * FROM jobs WHERE id=?`, id);
        if (!job) return json({ erreur: "lance d'abord l'analyse de cette vid\xE9o (/api/analyser)" }, 404);
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
          return new Response(r ? r.t : "Vid\xE9o inconnue", { status: r ? 200 : 404, headers: { "content-type": "text/plain; charset=utf-8", "cache-control": "no-store" } });
        }
        return this.pageJob(m[1]);
      }
      return json({ erreur: "inconnu" }, 404);
    } catch (e) {
      return json({ erreur: String(e).slice(0, 500) }, 500);
    }
  }
};

// ../../.npm/_npx/c943b712072b77c4/node_modules/wrangler/templates/middleware/middleware-ensure-req-body-drained.ts
var drainBody = /* @__PURE__ */ __name(async (request, env, _ctx, middlewareCtx) => {
  try {
    return await middlewareCtx.next(request, env);
  } finally {
    try {
      if (request.body !== null && !request.bodyUsed) {
        const reader = request.body.getReader();
        while (!(await reader.read()).done) {
        }
      }
    } catch (e) {
      console.error("Failed to drain the unused request body.", e);
    }
  }
}, "drainBody");
var middleware_ensure_req_body_drained_default = drainBody;

// ../../.npm/_npx/c943b712072b77c4/node_modules/wrangler/templates/middleware/middleware-miniflare3-json-error.ts
function reduceError(e) {
  return {
    name: e?.name,
    message: e?.message ?? String(e),
    stack: e?.stack,
    cause: e?.cause === void 0 ? void 0 : reduceError(e.cause)
  };
}
__name(reduceError, "reduceError");
var jsonError = /* @__PURE__ */ __name(async (request, env, _ctx, middlewareCtx) => {
  try {
    return await middlewareCtx.next(request, env);
  } catch (e) {
    const error = reduceError(e);
    const body = JSON.stringify(error);
    const headers = {
      "Content-Type": "application/json",
      "MF-Experimental-Error-Stack": "true"
    };
    const encoded = encodeURIComponent(body);
    if (encoded.length <= 8192) {
      headers["MF-Experimental-Error-Stack-Payload"] = encoded;
    }
    return new Response(body, { status: 500, headers });
  }
}, "jsonError");
var middleware_miniflare3_json_error_default = jsonError;

// .wrangler/tmp/bundle-D9FABh/middleware-insertion-facade.js
var __INTERNAL_WRANGLER_MIDDLEWARE__ = [
  middleware_ensure_req_body_drained_default,
  middleware_miniflare3_json_error_default
];
var middleware_insertion_facade_default = src_default;

// ../../.npm/_npx/c943b712072b77c4/node_modules/wrangler/templates/middleware/common.ts
var __facade_middleware__ = [];
function __facade_register__(...args) {
  __facade_middleware__.push(...args.flat());
}
__name(__facade_register__, "__facade_register__");
function __facade_invokeChain__(request, env, ctx, dispatch, middlewareChain) {
  const [head, ...tail] = middlewareChain;
  const middlewareCtx = {
    dispatch,
    next(newRequest, newEnv) {
      return __facade_invokeChain__(newRequest, newEnv, ctx, dispatch, tail);
    }
  };
  return head(request, env, ctx, middlewareCtx);
}
__name(__facade_invokeChain__, "__facade_invokeChain__");
function __facade_invoke__(request, env, ctx, dispatch, finalMiddleware) {
  return __facade_invokeChain__(request, env, ctx, dispatch, [
    ...__facade_middleware__,
    finalMiddleware
  ]);
}
__name(__facade_invoke__, "__facade_invoke__");

// .wrangler/tmp/bundle-D9FABh/middleware-loader.entry.ts
var __Facade_ScheduledController__ = class ___Facade_ScheduledController__ {
  constructor(scheduledTime, cron, noRetry) {
    this.scheduledTime = scheduledTime;
    this.cron = cron;
    this.#noRetry = noRetry;
  }
  scheduledTime;
  cron;
  static {
    __name(this, "__Facade_ScheduledController__");
  }
  #noRetry;
  noRetry() {
    if (!(this instanceof ___Facade_ScheduledController__)) {
      throw new TypeError("Illegal invocation");
    }
    this.#noRetry();
  }
};
function wrapExportedHandler(worker) {
  if (__INTERNAL_WRANGLER_MIDDLEWARE__ === void 0 || __INTERNAL_WRANGLER_MIDDLEWARE__.length === 0) {
    return worker;
  }
  for (const middleware of __INTERNAL_WRANGLER_MIDDLEWARE__) {
    __facade_register__(middleware);
  }
  const fetchDispatcher = /* @__PURE__ */ __name(function(request, env, ctx) {
    if (worker.fetch === void 0) {
      throw new Error("Handler does not export a fetch() function.");
    }
    return worker.fetch(request, env, ctx);
  }, "fetchDispatcher");
  return {
    ...worker,
    fetch(request, env, ctx) {
      const dispatcher = /* @__PURE__ */ __name(function(type, init) {
        if (type === "scheduled" && worker.scheduled !== void 0) {
          const controller = new __Facade_ScheduledController__(
            Date.now(),
            init.cron ?? "",
            () => {
            }
          );
          return worker.scheduled(controller, env, ctx);
        }
      }, "dispatcher");
      return __facade_invoke__(request, env, ctx, dispatcher, fetchDispatcher);
    }
  };
}
__name(wrapExportedHandler, "wrapExportedHandler");
function wrapWorkerEntrypoint(klass) {
  if (__INTERNAL_WRANGLER_MIDDLEWARE__ === void 0 || __INTERNAL_WRANGLER_MIDDLEWARE__.length === 0) {
    return klass;
  }
  for (const middleware of __INTERNAL_WRANGLER_MIDDLEWARE__) {
    __facade_register__(middleware);
  }
  return class extends klass {
    #fetchDispatcher = /* @__PURE__ */ __name((request, env, ctx) => {
      this.env = env;
      this.ctx = ctx;
      if (super.fetch === void 0) {
        throw new Error("Entrypoint class does not define a fetch() function.");
      }
      return super.fetch(request);
    }, "#fetchDispatcher");
    #dispatcher = /* @__PURE__ */ __name((type, init) => {
      if (type === "scheduled" && super.scheduled !== void 0) {
        const controller = new __Facade_ScheduledController__(
          Date.now(),
          init.cron ?? "",
          () => {
          }
        );
        return super.scheduled(controller);
      }
    }, "#dispatcher");
    fetch(request) {
      return __facade_invoke__(
        request,
        this.env,
        this.ctx,
        this.#dispatcher,
        this.#fetchDispatcher
      );
    }
  };
}
__name(wrapWorkerEntrypoint, "wrapWorkerEntrypoint");
var WRAPPED_ENTRY;
if (typeof middleware_insertion_facade_default === "object") {
  WRAPPED_ENTRY = wrapExportedHandler(middleware_insertion_facade_default);
} else if (typeof middleware_insertion_facade_default === "function") {
  WRAPPED_ENTRY = wrapWorkerEntrypoint(middleware_insertion_facade_default);
}
var middleware_loader_entry_default = WRAPPED_ENTRY;
export {
  Coffre,
  __INTERNAL_WRANGLER_MIDDLEWARE__,
  middleware_loader_entry_default as default
};
//# sourceMappingURL=index.js.map
