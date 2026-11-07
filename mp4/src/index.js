// Convertisseur YouTube → MP4 de Pitch (07.11.2026).
// YouTube bloque tous les serveurs (GitHub, Cloudflare, Piped, Invidious : testé le 07.11.2026),
// donc le téléchargement est fait par un module Apify. La clé Apify est collée dans l'app et gardée
// dans le Durable Object (jamais dans le code). Chaque appareil s'identifie une fois avec cette clé
// et reçoit un cookie d'accès : sans lui, personne ne peut dépenser le crédit Apify ni voir les fichiers.
const VERSION = "1.1.0";
const API = "https://api.apify.com/v2";
// Clé publique de Claude : signe les requêtes de test lancées depuis GitHub Actions (aucun secret ici)
const ADMIN_JWK = { kty: "EC", crv: "P-256", x: "qHxOme14PLpJvoFAVS56fwXobWwBtQtUxrCz2655BDo", y: "HGUc5w5DlL_4nn5qgI47CDFx6yDEXzfh8alXgN9i0mk" };

// Module Apify utilisé et construction de son entrée
const MODULE = {
  acteur: "streamers~youtube-video-downloader",
  entree: (url, q) => ({ videos: [{ url }], storeInKVStore: true, preferredQuality: q + "p", preferredFormat: "mp4" }),
};

const json = (o, s = 200, h = {}) => new Response(JSON.stringify(o), { status: s, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store", ...h } });

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

function idYouTube(s) {
  let t = String(s || "").trim();
  if (/^[\w-]{11}$/.test(t)) return t;
  if (!/^https?:\/\//i.test(t)) t = "https://" + t;
  try {
    const u = new URL(t);
    const h = u.hostname.replace(/^(www|m|music)\./, "");
    let id = null;
    if (h === "youtu.be") id = u.pathname.split("/")[1];
    else if (h === "youtube.com" || h === "youtube-nocookie.com") {
      id = u.searchParams.get("v");
      if (!id) { const m = u.pathname.match(/^\/(shorts|live|embed|v)\/([^/?#]+)/); if (m) id = m[2]; }
    }
    return id && /^[\w-]{11}$/.test(id) ? id : null;
  } catch { return null; }
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

function francais(message, statut) {
  const m = String(message || "");
  if (/NO_RESULTS|No results/i.test(m)) return "Vidéo introuvable : vérifie le lien (vidéo privée, supprimée ou réservée aux membres ?).";
  if (/not found/i.test(m)) return "Conversion introuvable.";
  if (/token|auth|401|403/i.test(m)) return "Apify refuse la clé enregistrée.";
  if (/limit|credit|usage|402/i.test(m)) return "Crédit Apify épuisé pour ce mois.";
  if (statut === "TIMED-OUT") return "La conversion a pris trop de temps (vidéo trop longue ?).";
  return "La conversion a échoué. Réessaie, ou essaie une qualité plus basse.";
}

const b64u = (s) => Uint8Array.from(atob(s.replace(/-/g, "+").replace(/_/g, "/") + "===".slice((s.length + 3) % 4)), (c) => c.charCodeAt(0));

export class Coffre {
  constructor(ctx, env) { this.ctx = ctx; this.env = env; this.s = ctx.storage; }

  async apify(chemin, init = {}) {
    const cle = await this.s.get("cle");
    if (!cle) throw new Error("Clé Apify absente");
    const sep = chemin.includes("?") ? "&" : "?";
    const r = await fetch(`${API}${chemin}${sep}token=${encodeURIComponent(cle)}`, init);
    const t = await r.text(); let j; try { j = JSON.parse(t); } catch { j = { brut: t.slice(0, 300) }; }
    if (!r.ok) throw new Error((j.error && (j.error.type || j.error.message)) || `Apify HTTP ${r.status}`);
    return j.data !== undefined ? j.data : j;
  }

  // Requête de test signée par Claude (horodatage valable 10 min)
  async estAdmin(req) {
    const ts = req.headers.get("x-admin-ts"), sig = req.headers.get("x-admin-sig");
    if (!ts || !sig || Math.abs(Date.now() - Number(ts)) > 600_000) return false;
    try {
      const k = await crypto.subtle.importKey("jwk", ADMIN_JWK, { name: "ECDSA", namedCurve: "P-256" }, false, ["verify"]);
      return await crypto.subtle.verify({ name: "ECDSA", hash: "SHA-256" }, k, b64u(sig), new TextEncoder().encode("mp4-admin|" + ts));
    } catch { return false; }
  }

  async estConnecte(req) {
    const c = (req.headers.get("cookie") || "").match(/(?:^|;\s*)mp4acces=([\w-]+)/);
    if (c && (await this.s.get("acces:" + c[1]))) return true;
    return this.estAdmin(req);
  }

  async ouvrirSession() {
    const t = [...crypto.getRandomValues(new Uint8Array(24))].map((x) => x.toString(16).padStart(2, "0")).join("");
    await this.s.put("acces:" + t, Date.now());
    return `mp4acces=${t}; Path=/; Max-Age=315360000; HttpOnly; Secure; SameSite=Lax`;
  }

  // Met à jour une conversion auprès d'Apify (appelée par le suivi ET à l'ouverture de l'app)
  async rafraichir(runId) {
    const run = await this.apify(`/actor-runs/${encodeURIComponent(runId)}`);
    const out = { statut: run.status };
    if (run.status === "SUCCEEDED") {
      const items = await this.apify(`/datasets/${run.defaultDatasetId}/items?clean=1&limit=5`);
      const it = (Array.isArray(items) ? items : [])[0] || {};
      const lien = it.error ? null : trouverLien(it);
      out.item = it;
      out.titre = (await this.s.get("titre:" + runId)) || it.title || String(it.fileKey || "").replace(/^[\w-]{11}_/, "").replace(/\.mp4$/i, "") || "";
      out.pret = !!lien;
      if (!lien) out.message = francais(it.error || it.note || "NO_RESULTS");
      await this.s.put("lien:" + runId, { lien, titre: out.titre });
    } else if (["FAILED", "ABORTED", "TIMED-OUT"].includes(run.status)) out.message = francais(run.statusMessage, run.status);
    const liste = (await this.s.get("liste")) || [];
    const e = liste.find((x) => x.run === runId);
    if (e) {
      e.statut = run.status === "SUCCEEDED" ? (out.pret ? "prêt" : "échec") : (run.status === "RUNNING" || run.status === "READY" ? "en cours" : "échec");
      if (out.titre) e.titre = out.titre;
      if (out.message) e.message = out.message;
      await this.s.put("liste", liste);
    }
    return out;
  }

  async lancer(acteur, entree, id, qualite) {
    const run = await this.apify(`/acts/${acteur}/runs`, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(entree) });
    let titre = "";
    if (id) try { const o = await fetch(`https://www.youtube.com/oembed?format=json&url=${encodeURIComponent("https://www.youtube.com/watch?v=" + id)}`); if (o.ok) titre = (await o.json()).title || ""; } catch {}
    if (titre) await this.s.put("titre:" + run.id, titre);
    const liste = (await this.s.get("liste")) || [];
    liste.unshift({ run: run.id, id, qualite, t: Date.now(), statut: "en cours", titre });
    await this.s.put("liste", liste.slice(0, 50));
    return run.id;
  }

  async fetch(req) {
    const u = new URL(req.url);
    try {
      const admin = await this.estAdmin(req);
      const cle = await this.s.get("cle");

      if (u.pathname === "/api/etat") {
        const connecte = await this.estConnecte(req);
        const base = { app: "mp4-app", version: VERSION, cle: !!cle, connecte };
        if (!connecte) return json(base);
        const liste = (await this.s.get("liste")) || [];
        for (const x of liste.filter((x) => x.statut === "en cours").slice(0, 5)) { try { await this.rafraichir(x.run); } catch {} }
        return json({ ...base, liste: ((await this.s.get("liste")) || []).slice(0, 20) });
      }

      if (u.pathname === "/api/cle" && req.method === "POST") {
        const b = await req.json().catch(() => ({}));
        const donnee = String(b.cle || "").trim();
        if (cle && donnee === cle) return json({ ok: true }, 200, { "set-cookie": await this.ouvrirSession() }); // connexion d'un appareil
        if (cle && String(b.ancienne || "").trim() !== cle) return json({ erreur: "Ce n'est pas la clé enregistrée. Pour en mettre une nouvelle, colle aussi l'ancienne." }, 403);
        if (donnee.length < 20 || /\s/.test(donnee)) return json({ erreur: "Ce n'est pas une clé Apify complète." }, 400);
        const r = await fetch(`${API}/users/me?token=${encodeURIComponent(donnee)}`);
        if (!r.ok) return json({ erreur: "Apify refuse cette clé (vérifie que tu as copié toute la clé)." }, 400);
        await this.s.put("cle", donnee);
        return json({ ok: true }, 200, { "set-cookie": await this.ouvrirSession() });
      }

      if (!(await this.estConnecte(req))) return json({ erreur: "Cet appareil n'est pas reconnu : colle ta clé Apify une fois." }, 401);

      if (u.pathname === "/api/lancer" && req.method === "POST") {
        const b = await req.json().catch(() => ({}));
        const id = idYouTube(b.url);
        if (!id) return json({ erreur: "Ce n'est pas un lien YouTube valable." }, 400);
        const q = ["360", "480", "720", "1080"].includes(String(b.qualite).replace("p", "")) ? String(b.qualite).replace("p", "") : "720";
        const run = await this.lancer(MODULE.acteur, MODULE.entree(`https://www.youtube.com/watch?v=${id}`, q), id, q + "p");
        return json({ run });
      }

      // Test d'un autre module Apify (Claude seulement)
      if (u.pathname === "/api/essai" && req.method === "POST" && admin) {
        const b = await req.json().catch(() => ({}));
        return json({ run: await this.lancer(b.acteur, b.entree, b.id || null, "essai") });
      }

      if (u.pathname === "/api/suivi") {
        const out = await this.rafraichir(u.searchParams.get("run"));
        if (!admin) delete out.item;
        return json(out);
      }

      if (u.pathname === "/api/fichier") {
        const runId = u.searchParams.get("run");
        const f = await this.s.get("lien:" + runId);
        if (!f || !f.lien) return json({ erreur: "Fichier introuvable (les fichiers sont effacés après ~3 jours)." }, 404);
        let src = f.lien;
        if (src.includes("api.apify.com")) src += (src.includes("?") ? "&" : "?") + "token=" + encodeURIComponent(cle);
        return this.servir(req, src, f.titre, !!u.searchParams.get("voir"));
      }

      return json({ erreur: "Adresse inconnue." }, 404);
    } catch (e) {
      return json({ erreur: francais(e.message) }, 500);
    }
  }

  // Sert le fichier en respectant les demandes partielles (Range) qu'exige la lecture vidéo sur iPhone
  async servir(req, src, titre, voir) {
    const range = req.headers.get("range");
    const r = await fetch(src, { headers: range ? { range } : {} });
    if (!r.ok && r.status !== 206) return json({ erreur: "Le fichier n'est plus disponible." }, 502);
    const nom = ((titre || "video").replace(/[\\/:*?"<>|]+/g, " ").trim().slice(0, 120) || "video") + ".mp4";
    const h = new Headers({ "content-type": "video/mp4", "accept-ranges": "bytes", "cache-control": "private, max-age=3600",
      "content-disposition": `${voir ? "inline" : "attachment"}; filename="video.mp4"; filename*=UTF-8''${encodeURIComponent(nom)}` });
    const total = Number(r.headers.get("content-length") || 0);
    const m = range && range.match(/^bytes=(\d*)-(\d*)$/);
    if (r.status === 206 || !m || !total) {
      for (const k of ["content-length", "content-range"]) if (r.headers.get(k)) h.set(k, r.headers.get(k));
      return new Response(r.body, { status: r.status, headers: h });
    }
    // La source a renvoyé le fichier entier : on découpe nous-mêmes la tranche demandée
    let debut = m[1] === "" ? Math.max(0, total - Number(m[2])) : Number(m[1]);
    let fin = m[1] === "" || m[2] === "" ? total - 1 : Math.min(Number(m[2]), total - 1);
    if (debut > fin || debut >= total) { r.body.cancel(); return new Response(null, { status: 416, headers: { "content-range": `bytes */${total}` } }); }
    h.set("content-range", `bytes ${debut}-${fin}/${total}`); h.set("content-length", String(fin - debut + 1));
    let pos = 0;
    const tranche = new TransformStream({
      transform(chunk, ctl) {
        const a = pos, b = pos + chunk.byteLength; pos = b;
        if (b <= debut || a > fin) { if (a > fin) ctl.terminate(); return; }
        ctl.enqueue(chunk.subarray(Math.max(0, debut - a), Math.min(chunk.byteLength, fin - a + 1)));
      },
    });
    return new Response(r.body.pipeThrough(tranche), { status: 206, headers: h });
  }
}
