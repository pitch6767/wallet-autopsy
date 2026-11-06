// Adaptateur Polymarket Data API v1 → v2.
// Polymarket a retiré l'API v1 le 02.11.2026 (réponse 410). Tout le code de l'app parle encore v1 :
// au lieu de réécrire chaque appel, on intercepte fetch() et on traduit à la source :
//   chemins  /trades /activity /holders → /v2/… ; /closed-positions → /v2/positions?status=CLOSED
//   paramètres market→condition, takerOnly→taker_only ; offset émulé en suivant le curseur (pages de 1000)
//   réponse {data, pagination} snake_case → tableau v1 camelCase (les deux noms sont gardés)
// Format vérifié en direct le 07.11.2026 (trades, activity, holders, positions, curseur « cursor »).

const HOTE = "data-api.polymarket.com";
const CHEMINS = { "/trades": "/v2/trades", "/activity": "/v2/activity", "/holders": "/v2/holders", "/closed-positions": "/v2/positions" };
const ALIAS = {
  token_id: "asset", condition_id: "conditionId", outcome_index: "outcomeIndex", proxy_wallet: "proxyWallet",
  transaction_hash: "transactionHash", event_slug: "eventSlug", usdc_size: "usdcSize", profile_image: "profileImage",
  avg_price: "avgPrice", realized_pnl: "realizedPnl", total_size: "totalBought", current_price: "curPrice",
  current_value: "currentValue", current_size: "size", entry_cost_usdc: "initialValue", total_pnl: "cashPnl",
  percent_pnl: "percentPnl", percent_realized_pnl: "percentRealizedPnl", end_date: "endDate", event_id: "eventId",
};
const camel = (k) => k.replace(/_([a-z])/g, (_, c) => c.toUpperCase());

function versV1(o) {
  if (Array.isArray(o)) return o.map(versV1);
  if (!o || typeof o !== "object") return o;
  const r = {};
  for (const [k, v] of Object.entries(o)) {
    const val = versV1(v);
    r[k] = val;
    const c = camel(k); if (c !== k && !(c in r)) r[c] = val;
    if (ALIAS[k] && !(ALIAS[k] in o)) r[ALIAS[k]] = val;
  }
  if (o.token_id != null && o.holders) r.token = o.token_id; // /holders v1 : { token, holders }
  return r;
}

const cache = new Map(); // requête de base → { rows, curseur, fini, t }

export function estV1(u) {
  try { const x = new URL(String(u)); return x.hostname === HOTE && !x.pathname.startsWith("/v2/") && CHEMINS[x.pathname] != null; } catch { return false; }
}

export async function v1ViaV2(u, init, brut) {
  const x = new URL(String(u));
  const p = new URLSearchParams(x.search);
  const offset = Number(p.get("offset") || 0), limit = Math.max(1, Math.min(1000, Number(p.get("limit") || 100)));
  p.delete("offset"); p.delete("limit"); p.delete("sizeThreshold");
  if (p.has("market")) { p.set("condition", p.get("market")); p.delete("market"); }
  if (p.has("takerOnly")) { p.set("taker_only", p.get("takerOnly")); p.delete("takerOnly"); }
  if (x.pathname === "/closed-positions") p.set("status", "CLOSED");
  const base = `https://${HOTE}${CHEMINS[x.pathname]}?${p}`;
  const parPage = x.pathname === "/holders" ? limit : 1000;
  let e = cache.get(base);
  if (!e || Date.now() - e.t > 60_000) { e = { rows: [], curseur: null, fini: false, t: Date.now() }; cache.set(base, e); }
  while (!e.fini && e.rows.length < offset + limit) {
    const url = `${base}&limit=${parPage}` + (e.curseur ? `&cursor=${encodeURIComponent(e.curseur)}` : "");
    const r = await brut(url, init);
    if (!r.ok) {
      if (e.rows.length > offset) break; // on rend ce qu'on a déjà
      return new Response(await r.text(), { status: r.status, headers: { "content-type": "application/json" } });
    }
    const j = await r.json();
    const data = Array.isArray(j) ? j : (j && j.data) || [];
    e.rows.push(...data);
    const pg = j && j.pagination;
    e.curseur = pg && pg.next_cursor;
    if (!pg || !pg.has_more || !e.curseur || !data.length || x.pathname === "/holders") e.fini = true;
  }
  if (cache.size > 200) for (const k of [...cache.keys()].slice(0, 100)) cache.delete(k);
  const lot = versV1(e.rows.slice(offset, offset + limit));
  return new Response(JSON.stringify(lot), { status: 200, headers: { "content-type": "application/json" } });
}

export function installer() {
  if (globalThis.__v1v2) return;
  const brut = globalThis.fetch.bind(globalThis);
  globalThis.fetch = (u, init) => (estV1(typeof u === "string" ? u : u && u.url) ? v1ViaV2(typeof u === "string" ? u : u.url, init, brut) : brut(u, init));
  globalThis.__v1v2 = true;
}
