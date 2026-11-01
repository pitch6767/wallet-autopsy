export default {
  async fetch(req, env) {
    const u = new URL(req.url);
    if (u.pathname === '/api/brut') {
      const d = u.searchParams.get('d') || '30-10-2026';
      const r = await fetch('https://www.euro-millions.com/fr/resultats/' + d, { headers: { 'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 Safari/604.1', 'accept-language': 'fr-CH,fr' } });
      return new Response(await r.text(), { status: r.status, headers: { 'content-type': 'text/plain; charset=utf-8' } });
    }
    return env.ASSETS.fetch(req);
  }
};
