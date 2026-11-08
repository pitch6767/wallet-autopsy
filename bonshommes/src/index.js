// App « Bonshommes » de Pitch (08.11.2026) : un sujet → une vidéo MP4 de bonshommes bâtons (images, voix, sous-titres).
// Le Worker garde la clé Gemini, la liste des vidéos et les fichiers finis (Durable Object « Coffre »).
// Le rendu (Gemini + ffmpeg) tourne dans le conteneur Cloudflare « Atelier » (dossier container/).
import { Container, getContainer } from "@cloudflare/containers";

const VERSION = "1.0.0";
const MORCEAU = 1024 * 1024; // les vidéos finies sont rangées par tranches de 1 Mo
// Clé publique de Claude : signe les requêtes de test lancées depuis GitHub Actions (aucun secret ici)
const ADMIN_JWK = { kty: "EC", crv: "P-256", x: "qHxOme14PLpJvoFAVS56fwXobWwBtQtUxrCz2655BDo", y: "HGUc5w5DlL_4nn5qgI47CDFx6yDEXzfh8alXgN9i0mk" };

export class Atelier extends Container {
  defaultPort = 8080;
  sleepAfter = "30m";
}

const json = (o, s = 200) => new Response(JSON.stringify(o), { status: s, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" } });

export default {
  async fetch(req, env) {
    const u = new URL(req.url);
    if (!u.pathname.startsWith("/api/")) {
      const r = await env.ASSETS.fetch(req);
      if (u.pathname === "/" || u.pathname.endsWith(".html")) {
        const h = new Headers(r.headers); h.set("cache-control", "no-store, max-age=0");
        return new Response(r.body, { status: r.status, headers: h });
      }
      return r;
    }
    return env.COFFRE.get(env.COFFRE.idFromName("unique")).fetch(req);
  },
};

const b64u = (s) => Uint8Array.from(atob(s.replace(/-/g, "+").replace(/_/g, "/") + "===".slice((s.length + 3) % 4)), (c) => c.charCodeAt(0));
const msg = (e) => String(e && e.message || e);

export class Coffre {
  constructor(ctx, env) { this.ctx = ctx; this.env = env; this.s = ctx.storage; }

  atelier() { return getContainer(this.env.ATELIER, "atelier"); }
  async appelAtelier(chemin, init) {
    const r = await this.atelier().fetch(new Request("http://atelier" + chemin, init));
    return r;
  }

  async estAdmin(req) {
    const ts = req.headers.get("x-admin-ts"), sig = req.headers.get("x-admin-sig");
    if (!ts || !sig || Math.abs(Date.now() - Number(ts)) > 600_000) return false;
    try {
      const k = await crypto.subtle.importKey("jwk", ADMIN_JWK, { name: "ECDSA", namedCurve: "P-256" }, false, ["verify"]);
      return await crypto.subtle.verify({ name: "ECDSA", hash: "SHA-256" }, k, b64u(sig), new TextEncoder().encode("mp4-admin|" + ts));
    } catch { return false; }
  }

  async liste() { return (await this.s.get("liste")) || []; }
  async majListe(id, champs) { const l = await this.liste(); const e = l.find((x) => x.id === id); if (e) { Object.assign(e, champs); await this.s.put("liste", l); } return e; }

  // Interroge l'atelier ; quand la vidéo est prête, la rapatrie ici (l'atelier peut s'endormir et tout oublier)
  async suivre(id) {
    const e = (await this.liste()).find((x) => x.id === id);
    if (!e) return { erreur: "Vidéo inconnue." };
    if (e.statut !== "en cours") return e;
    let r;
    try { r = await this.appelAtelier("/etat?id=" + encodeURIComponent(id)); }
    catch (x) { return { ...e, etape: "Démarrage de l'atelier…" }; }
    if (r.status === 404) return this.majListe(id, { statut: "échec", message: "L'atelier a redémarré pendant le travail. Relance la vidéo." });
    const t = await r.json().catch(() => ({}));
    if (t.erreur) {
      let m = t.erreur;
      if (/HTTP 429|quota|RESOURCE_EXHAUSTED/i.test(m)) m = "Gemini refuse : quota ou crédit épuisé. Vérifie la facturation sur https://aistudio.google.com/apikey";
      else if (/refuse la clé|HTTP 400|HTTP 403|API key/i.test(m)) m = "Google refuse la clé Gemini enregistrée.";
      else if (/image/i.test(m) && /refus|contenu/i.test(m)) m = "Gemini a refusé de dessiner une scène. Reformule le sujet et relance.";
      else m = "La fabrication a échoué : " + m.slice(0, 200);
      return this.majListe(id, { statut: "échec", message: m, cout: t.cout });
    }
    if (!t.pret) return this.majListe(id, { etape: t.etape, pct: t.pct, titre: t.titre || e.titre });
    // rapatriement du fichier
    const f = await this.appelAtelier("/fichier?id=" + encodeURIComponent(id));
    if (!f.ok) return { ...e, etape: "Récupération du fichier…" };
    const buf = new Uint8Array(await f.arrayBuffer());
    const n = Math.ceil(buf.length / MORCEAU);
    for (let i = 0; i < n; i++) await this.s.put(`f:${id}:${i}`, buf.slice(i * MORCEAU, (i + 1) * MORCEAU));
    await this.appelAtelier("/oublier?id=" + encodeURIComponent(id), { method: "POST" }).catch(() => {});
    return this.majListe(id, { statut: "prête", etape: "Prête", pct: 100, titre: t.titre, narration: t.narration, taille: buf.length, morceaux: n, secondes: t.secondes, cout: Math.round(t.cout * 100) / 100 });
  }

  async alarm() { // continue le suivi même si la page est fermée
    const enCours = (await this.liste()).filter((x) => x.statut === "en cours");
    for (const e of enCours) { try { await this.suivre(e.id); } catch {} }
    if ((await this.liste()).some((x) => x.statut === "en cours")) await this.s.setAlarm(Date.now() + 20_000);
  }

  async fetch(req) {
    const u = new URL(req.url);
    try {
      const cle = await this.s.get("cle");
      const admin = await this.estAdmin(req);

      if (u.pathname === "/api/etat") {
        const l = await this.liste();
        for (const e of l.filter((x) => x.statut === "en cours").slice(0, 3)) { try { await this.suivre(e.id); } catch {} }
        return json({ app: "bonshommes-app", version: VERSION, cle: !!cle, liste: (await this.liste()).slice(0, 30).map(({ narration, ...x }) => x) });
      }

      if (u.pathname === "/api/cle" && req.method === "POST") {
        const b = await req.json().catch(() => ({}));
        const nouvelle = String(b.cle || "").trim();
        if (cle && String(b.ancienne || "").trim() !== cle) return json({ erreur: "Une clé est déjà enregistrée. Pour la remplacer, colle aussi l'ancienne." }, 403);
        if (nouvelle.length < 20 || /\s/.test(nouvelle)) return json({ erreur: "Ce n'est pas une clé Gemini complète." }, 400);
        const r = await fetch("https://generativelanguage.googleapis.com/v1beta/models?pageSize=5", { headers: { "x-goog-api-key": nouvelle } });
        if (!r.ok) return json({ erreur: "Google refuse cette clé (vérifie que tu as copié toute la clé)." }, 400);
        await this.s.put("cle", nouvelle);
        return json({ ok: true });
      }

      if (u.pathname === "/api/lancer" && req.method === "POST") {
        if (!cle) return json({ erreur: "Colle d'abord ta clé Gemini." }, 401);
        const b = await req.json().catch(() => ({}));
        const sujet = String(b.sujet || "").trim();
        if (sujet.length < 3) return json({ erreur: "Écris un sujet." }, 400);
        if ((await this.liste()).some((x) => x.statut === "en cours")) return json({ erreur: "Une vidéo est déjà en fabrication. Attends qu'elle soit finie." }, 409);
        const id = crypto.randomUUID().slice(0, 12);
        const job = { id, cle, sujet, style: b.style, duree: Number(b.duree) || 60, format: b.format === "9:16" ? "9:16" : "16:9", voix: b.voix, langue: "français" };
        let r;
        try { r = await this.appelAtelier("/job", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(job) }); }
        catch (x) { return json({ erreur: "L'atelier de rendu ne répond pas : " + msg(x).slice(0, 150) }, 502); }
        if (!r.ok) return json({ erreur: "L'atelier a refusé la demande." }, 502);
        const l = await this.liste();
        l.unshift({ id, sujet: sujet.slice(0, 160), style: job.style, duree: job.duree, format: job.format, t: Date.now(), statut: "en cours", etape: "Démarrage", pct: 0 });
        await this.s.put("liste", l.slice(0, 60));
        await this.s.setAlarm(Date.now() + 20_000);
        return json({ id });
      }

      if (u.pathname === "/api/suivi") return json(await this.suivre(u.searchParams.get("id")));

      if (u.pathname === "/api/supprimer" && req.method === "POST") {
        const id = u.searchParams.get("id"); const l = await this.liste(); const e = l.find((x) => x.id === id);
        if (e?.morceaux) await this.s.delete(Array.from({ length: e.morceaux }, (_, i) => `f:${id}:${i}`));
        await this.s.put("liste", l.filter((x) => x.id !== id));
        return json({ ok: true });
      }

      if (u.pathname === "/api/fichier") return this.servir(req, u.searchParams.get("id"), !!u.searchParams.get("voir"));

      if (u.pathname === "/api/sante" && admin) { const r = await this.appelAtelier("/sante"); return json({ atelier: await r.json() }); }

      return json({ erreur: "Adresse inconnue." }, 404);
    } catch (e) { return json({ erreur: "Erreur : " + msg(e).slice(0, 200) }, 500); }
  }

  // Lecture par tranches (Range) : indispensable pour la lecture vidéo sur iPhone
  async servir(req, id, voir) {
    const e = (await this.liste()).find((x) => x.id === id);
    if (!e || e.statut !== "prête") return json({ erreur: "Vidéo introuvable." }, 404);
    const total = e.taille, m = (req.headers.get("range") || "").match(/^bytes=(\d*)-(\d*)$/);
    let debut = 0, fin = total - 1, statut = 200;
    if (m) {
      statut = 206;
      if (m[1] === "") { debut = Math.max(0, total - Number(m[2])); }
      else { debut = Number(m[1]); if (m[2] !== "") fin = Math.min(Number(m[2]), total - 1); }
      if (debut > fin || debut >= total) return new Response(null, { status: 416, headers: { "content-range": `bytes */${total}` } });
    }
    const nom = ((e.titre || "video").replace(/[\\/:*?"<>|]+/g, " ").trim().slice(0, 100) || "video") + ".mp4";
    const h = new Headers({ "content-type": "video/mp4", "accept-ranges": "bytes", "content-length": String(fin - debut + 1), "cache-control": "private, max-age=3600",
      "content-disposition": `${voir ? "inline" : "attachment"}; filename="video.mp4"; filename*=UTF-8''${encodeURIComponent(nom)}` });
    if (statut === 206) h.set("content-range", `bytes ${debut}-${fin}/${total}`);
    const s = this.s, a = Math.floor(debut / MORCEAU), b = Math.floor(fin / MORCEAU);
    const corps = new ReadableStream({
      async pull(c) {
        if (this.i === undefined) this.i = a;
        if (this.i > b) { c.close(); return; }
        const morceau = await s.get(`f:${id}:${this.i}`);
        const o = this.i * MORCEAU, x = Math.max(0, debut - o), y = Math.min(morceau.length, fin - o + 1);
        c.enqueue(morceau.subarray(x, y)); this.i++;
      },
    });
    return new Response(corps, { status: statut, headers: h });
  }
}
