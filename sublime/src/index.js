// Sublime — serveur : comptes (prénom + PIN) et sauvegarde de la progression
import { DurableObject } from "cloudflare:workers";

const json = (d, s = 200) =>
  new Response(JSON.stringify(d), { status: s, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" } });

async function hache(texte) {
  const b = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(texte));
  return [...new Uint8Array(b)].map((x) => x.toString(16).padStart(2, "0")).join("");
}

const cle = (nom) => "u:" + nom.trim().toLowerCase();

function publique(u) {
  return { nom: u.nom, niveau: u.niveau, chats: u.chats, astuces: u.astuces, partie: u.partie || null, stats: u.stats || {} };
}

export class Coffre extends DurableObject {
  async fetch(req) {
    const url = new URL(req.url);
    const corps = req.method === "POST" ? await req.json().catch(() => ({})) : {};
    const st = this.ctx.storage;

    if (url.pathname === "/api/inscription" || url.pathname === "/api/connexion") {
      const nom = String(corps.nom || "").trim().slice(0, 20);
      const pin = String(corps.pin || "");
      if (!nom) return json({ erreur: "Entre ton prénom." }, 400);
      if (!/^\d{4}$/.test(pin)) return json({ erreur: "Le code PIN doit avoir 4 chiffres." }, 400);
      let u = await st.get(cle(nom));
      if (url.pathname === "/api/inscription") {
        if (u) return json({ erreur: "Ce prénom existe déjà. Connecte-toi." }, 409);
        const sel = crypto.randomUUID();
        u = { nom, sel, pin: await hache(sel + pin), niveau: 1, chats: 0, astuces: 0, partie: null, stats: { reussis: 0, parfaits: 0 }, cree: Date.now() };
      } else {
        if (!u) return json({ erreur: "Prénom inconnu. Crée ton compte." }, 404);
        if ((await hache(u.sel + pin)) !== u.pin) return json({ erreur: "Code PIN incorrect." }, 401);
      }
      const jeton = crypto.randomUUID() + crypto.randomUUID();
      await st.put("t:" + jeton, cle(nom));
      await st.put(cle(nom), u);
      return json({ jeton, profil: publique(u) });
    }

    const jeton = (req.headers.get("authorization") || "").replace("Bearer ", "");
    const k = jeton ? await st.get("t:" + jeton) : null;
    const u = k ? await st.get(k) : null;
    if (!u) return json({ erreur: "Session expirée." }, 401);

    if (url.pathname === "/api/profil") return json({ profil: publique(u) });

    if (url.pathname === "/api/sauver" && req.method === "POST") {
      const ent = (v, d) => (Number.isInteger(v) && v >= 0 && v < 100000 ? v : d);
      u.niveau = Math.max(1, ent(corps.niveau, u.niveau));
      u.chats = ent(corps.chats, u.chats);
      u.astuces = ent(corps.astuces, u.astuces);
      if (corps.stats && typeof corps.stats === "object") u.stats = { reussis: ent(corps.stats.reussis, 0), parfaits: ent(corps.stats.parfaits, 0) };
      u.partie = corps.partie && JSON.stringify(corps.partie).length < 20000 ? corps.partie : null;
      u.maj = Date.now();
      await st.put(k, u);
      return json({ ok: true });
    }

    if (url.pathname === "/api/deconnexion" && req.method === "POST") {
      await st.delete("t:" + jeton);
      return json({ ok: true });
    }
    return json({ erreur: "inconnu" }, 404);
  }
}

export default {
  async fetch(req, env) {
    const url = new URL(req.url);
    if (url.pathname.startsWith("/api/")) {
      const id = env.COFFRE.idFromName("sublime");
      return env.COFFRE.get(id).fetch(req);
    }
    return env.ASSETS.fetch(req);
  },
};
