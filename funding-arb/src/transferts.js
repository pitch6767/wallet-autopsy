// Dépôts et retraits par crypto (21.11.2026, choix 3 de Pitch) : on n'entre pas si les dépôts OU les retraits
// sont suspendus sur Gate ou KuCoin (données publiques, relues toutes les 10 minutes).
// OKX et Bybit ne publient pas cette information sans clé → non contrôlés pour l'instant. Aster (perpétuel) : sans objet.
async function j(url) {
  const r = await fetch(url, { headers: { "user-agent": "price-arb/1" } });
  if (!r.ok) throw new Error("HTTP " + r.status);
  return r.json();
}
const SOURCES = {
  async gate() {
    const m = {};
    for (const c of (await j("https://api.gateio.ws/api/v4/spot/currencies")) || []) {
      const base = String(c.currency || "").toUpperCase();
      const chaines = Array.isArray(c.chains) && c.chains.length ? c.chains : [c];
      const ok = !c.delisted && chaines.some((x) => !x.deposit_disabled && !x.withdraw_disabled);
      m[base] = m[base] || ok; // une seule chaîne ouverte dans les deux sens suffit
    }
    return m;
  },
  async kucoin() {
    const m = {};
    for (const c of (await j("https://api.kucoin.com/api/v3/currencies")).data || []) {
      const ch = c.chains || [];
      m[String(c.currency).toUpperCase()] = ch.some((x) => x.isDepositEnabled && x.isWithdrawEnabled);
    }
    return m;
  },
};
let cache = { t: 0, plat: {} };
export async function lireTransferts() {
  const now = Date.now();
  if (now - cache.t < 600e3) return cache;
  const plat = {}, statut = {};
  await Promise.all(Object.entries(SOURCES).map(async ([ex, f]) => {
    try { plat[ex] = await f(); statut[ex] = { ok: true, n: Object.keys(plat[ex]).length }; }
    catch (e) { plat[ex] = cache.plat[ex] || null; statut[ex] = { ok: false, err: String(e.message || e).slice(0, 80) }; }
  }));
  cache = { t: now, plat, statut };
  return cache;
}
// true = transferts ouverts ou non contrôlables (OKX, Bybit, Aster, lecture impossible) ; false = suspendus (ou crypto absente de la liste)
export function transfertsOk(t, ex, base) {
  const m = t?.plat?.[ex];
  if (!m) return true;
  return m[base] === true;
}
