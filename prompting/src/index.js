// Prompting — serveur minimal : fichiers statiques, HTML jamais mis en cache, numéro de version
const VERSION = "1.0.0";

export default {
  async fetch(req, env) {
    const url = new URL(req.url);
    if (url.pathname === "/api/version") {
      return new Response(JSON.stringify({ version: VERSION }), {
        headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" },
      });
    }
    const rep = await env.ASSETS.fetch(req);
    const type = rep.headers.get("content-type") || "";
    if (type.includes("text/html") || type.includes("javascript") || type.includes("css")) {
      const r = new Response(rep.body, rep);
      r.headers.set("cache-control", "no-store, max-age=0");
      return r;
    }
    return rep;
  },
};
