// Peptides — sert les fichiers de l'app, toujours sans cache (l'iPhone ne garde jamais une ancienne version)
export default {
  async fetch(req, env) {
    const r = await env.ASSETS.fetch(req);
    const h = new Headers(r.headers);
    h.set("cache-control", "no-store, max-age=0");
    return new Response(r.body, { status: r.status, statusText: r.statusText, headers: h });
  },
};
