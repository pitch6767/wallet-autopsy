// Convertisseur YouTube → MP4 de Pitch (07.11.2026).
// YouTube bloque tous les serveurs (GitHub, Cloudflare, Piped, Invidious : testé le 07.11.2026),
// donc le téléchargement est fait par le module Apify « streamers/youtube-video-downloader ».
// La clé Apify est collée une fois dans l'app et gardée dans le Durable Object (jamais dans le code).
const VERSION = "1.0.0";
const ACTEUR = "streamers~youtube-video-downloader";
const API = "https://api.apify.com/v2";

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
    const coffre = env.COFFRE.get(env.COFFRE.idFromName("unique"));
    return coffre.fetch(req);
  },
};

function idYouTube(s) {
  try {
    const u = new URL(String(s).trim());
    if (u.hostname === "youtu.be") return u.pathname.slice(1, 12);
    if (/(^|\.)youtube\.com$/.test(u.hostname)) {
      if (u.searchParams.get("v")) return u.searchParams.get("v").slice(0, 11);
      const m = u.pathname.match(/\/(shorts|live|embed)\/([\w-]{11})/); if (m) return m[2];
    }
  } catch {}
  return null;
}

// Cherche dans un élément du dataset le lien du fichier vidéo, quel que soit le nom du champ
function trouverLien(o) {
  let best = null;
  const voir = (v) => {
    if (typeof v === "string" && /^https?:\/\//.test(v)) {
      if (/key-value-stores\/.+\/records\//.test(v) || /\.(mp4|mov|mkv|webm)(\?|$)/i.test(v)) { if (!best || /records/.test(v)) best = v; }
    } else if (v && typeof v === "object") for (const x of Object.values(v)) voir(x);
  };
  voir(o);
  return best;
}

export class Coffre {
  constructor(ctx, env) { this.ctx = ctx; this.env = env; this.s = ctx.storage; }

  async apify(chemin, init = {}) {
    const cle = await this.s.get("cle");
    if (!cle) throw new Error("Clé Apify absente");
    const sep = chemin.includes("?") ? "&" : "?";
    const r = await fetch(`${API}${chemin}${sep}token=${encodeURIComponent(cle)}`, init);
    const t = await r.text(); let j; try { j = JSON.parse(t); } catch { j = { brut: t.slice(0, 300) }; }
    if (!r.ok) throw new Error((j.error && j.error.message) || `Apify HTTP ${r.status}`);
    return j.data !== undefined ? j.data : j;
  }

  async fetch(req) {
    const u = new URL(req.url);
    try {
      if (u.pathname === "/api/etat") {
        const cle = await this.s.get("cle");
        const liste = (await this.s.get("liste")) || [];
        return json({ app: "mp4-app", version: VERSION, cle: !!cle, liste: liste.slice(0, 20) });
      }

      if (u.pathname === "/api/cle" && req.method === "POST") {
        const b = await req.json().catch(() => ({}));
        const nouvelle = String(b.cle || "").trim(), ancienne = await this.s.get("cle");
        if (ancienne && String(b.ancienne || "").trim() !== ancienne) return json({ erreur: "Une clé est déjà enregistrée. Pour la remplacer, colle aussi l'ancienne." }, 403);
        if (nouvelle.length < 20 || /\s/.test(nouvelle)) return json({ erreur: "Ce n'est pas une clé Apify complète." }, 400);
        const r = await fetch(`${API}/users/me?token=${encodeURIComponent(nouvelle)}`);
        if (!r.ok) return json({ erreur: "Apify refuse cette clé (vérifie que tu as copié toute la clé)." }, 400);
        await this.s.put("cle", nouvelle);
        return json({ ok: true });
      }

      if (u.pathname === "/api/lancer" && req.method === "POST") {
        const b = await req.json().catch(() => ({}));
        const id = idYouTube(b.url);
        if (!id) return json({ erreur: "Ce n'est pas un lien YouTube valable." }, 400);
        const qualite = ["360p", "480p", "720p", "1080p"].includes(b.qualite) ? b.qualite : "720p";
        const run = await this.apify(`/acts/${ACTEUR}/runs`, {
          method: "POST", headers: { "content-type": "application/json" },
          body: JSON.stringify({ videos: [{ url: `https://www.youtube.com/watch?v=${id}` }], storeInKVStore: true, preferredQuality: qualite, preferredFormat: "mp4" }),
        });
        const liste = (await this.s.get("liste")) || [];
        liste.unshift({ run: run.id, id, qualite, t: Date.now(), statut: "en cours" });
        await this.s.put("liste", liste.slice(0, 50));
        return json({ run: run.id });
      }

      if (u.pathname === "/api/suivi") {
        const runId = u.searchParams.get("run");
        const run = await this.apify(`/actor-runs/${encodeURIComponent(runId)}`);
        const out = { statut: run.status, message: run.statusMessage || "", cout: run.usageTotalUsd ?? null };
        if (run.status === "SUCCEEDED") {
          const items = await this.apify(`/datasets/${run.defaultDatasetId}/items?clean=1&limit=5`);
          const it = (Array.isArray(items) ? items : [])[0] || {};
          const lien = trouverLien(it);
          out.titre = it.title || it.videoTitle || it.name || "";
          out.pret = !!lien;
          if (!lien) out.message = "Apify a fini sans fichier : " + JSON.stringify(it).slice(0, 300);
          await this.s.put("lien:" + runId, { lien, titre: out.titre });
        }
        const liste = (await this.s.get("liste")) || [];
        const e = liste.find((x) => x.run === runId);
        if (e) { e.statut = run.status === "SUCCEEDED" ? (out.pret ? "prêt" : "sans fichier") : (run.status === "RUNNING" || run.status === "READY" ? "en cours" : "échec"); if (out.titre) e.titre = out.titre; await this.s.put("liste", liste); }
        return json(out);
      }

      if (u.pathname === "/api/fichier") {
        const runId = u.searchParams.get("run");
        const f = await this.s.get("lien:" + runId);
        if (!f || !f.lien) return json({ erreur: "Fichier introuvable (les fichiers Apify sont effacés après ~3 jours)." }, 404);
        const cle = await this.s.get("cle");
        let src = f.lien;
        if (src.includes("api.apify.com")) src += (src.includes("?") ? "&" : "?") + "token=" + encodeURIComponent(cle);
        const h = {}; const range = req.headers.get("range"); if (range) h.range = range;
        const r = await fetch(src, { headers: h });
        if (!r.ok && r.status !== 206) return json({ erreur: `Téléchargement refusé (HTTP ${r.status})` }, 502);
        const nom = ((f.titre || "video").replace(/[\\/:*?"<>|]+/g, " ").trim().slice(0, 120) || "video") + ".mp4";
        const out = new Headers();
        for (const k of ["content-length", "content-range", "accept-ranges"]) if (r.headers.get(k)) out.set(k, r.headers.get(k));
        out.set("content-type", "video/mp4");
        out.set("content-disposition", `${u.searchParams.get("voir") ? "inline" : "attachment"}; filename="video.mp4"; filename*=UTF-8''${encodeURIComponent(nom)}`);
        return new Response(r.body, { status: r.status, headers: out });
      }

      return json({ erreur: "inconnu" }, 404);
    } catch (e) {
      return json({ erreur: String(e.message || e) }, 500);
    }
  }
}
