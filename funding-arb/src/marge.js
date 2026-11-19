// Emprunt (vente à découvert au comptant) : quelles cryptos sont empruntables sur chaque plateforme,
// à quel taux (par heure) et jusqu'à quelle quantité. Données publiques, relues toutes les 10 minutes.
const num = (x) => { const v = parseFloat(x); return Number.isFinite(v) ? v : null; };
async function j(url) {
  const r = await fetch(url, { headers: { "user-agent": "price-arb/1" } });
  const t = await r.text();
  if (!r.ok) throw new Error(`HTTP ${r.status} ${t.slice(0, 80)}`);
  return JSON.parse(t);
}
// Taux par défaut quand la plateforme ne publie pas le taux de la crypto (estimé, prudent) : 0,01 % par heure ≈ 88 % par an
export const TAUX_DEFAUT_H = 0.0001;

const SOURCES = {
  async bybit() {
    const r = await j("https://api.bybit.com/v5/spot-margin-trade/data");
    const lots = r.result?.vipCoinList || [];
    const l = (lots.find((v) => /no vip/i.test(v.vipLevel || "")) || lots[0])?.list || [];
    const m = {};
    for (const x of l) if (x.borrowable) m[x.currency] = { taux: num(x.hourlyBorrowRate) ?? TAUX_DEFAUT_H, tauxPublie: num(x.hourlyBorrowRate) != null, max: num(x.maxBorrowingAmount) };
    return m;
  },
  async okx() {
    const [q, ins] = await Promise.all([j("https://www.okx.com/api/v5/public/interest-rate-loan-quota"), j("https://www.okx.com/api/v5/public/instruments?instType=MARGIN")]);
    const quota = Object.fromEntries((q.data?.[0]?.basic || []).map((x) => [x.ccy, x]));
    const m = {};
    for (const x of ins.data || []) {
      if (x.state !== "live" || !["USDT", "USDC"].includes(x.quoteCcy)) continue;
      const b = quota[x.baseCcy];
      m[x.baseCcy] = { taux: b ? num(b.rate) / 24 : TAUX_DEFAUT_H, tauxPublie: !!b, max: b ? num(b.quota) : null }; // OKX publie un taux par jour
    }
    return m;
  },
  async gate() {
    const [p, lend, cross] = await Promise.all([j("https://api.gateio.ws/api/v4/margin/uni/currency_pairs"), j("https://api.gateio.ws/api/v4/earn/uni/currencies"),
      j("https://api.gateio.ws/api/v4/margin/cross/currencies").catch(() => [])]);
    const taux = Object.fromEntries((lend || []).map((x) => [x.currency, num(x.max_rate)])); // taux horaire maximum du marché de prêt (prudent)
    const cr = Object.fromEntries((cross || []).map((x) => [x.name, x]));
    const m = {};
    for (const x of p || []) {
      if (x.status !== "enabled") continue;
      const [b] = x.currency_pair.split("_");
      const c = cr[b];
      m[b] = { taux: taux[b] ?? TAUX_DEFAUT_H, tauxPublie: taux[b] != null, max: c && c.loanable ? num(c.user_max_borrow_amount) : null };
    }
    return m;
  },
  async kucoin() {
    const r = await j("https://api.kucoin.com/api/v1/margin/config");
    const m = {};
    for (const c of r.data?.currencyList || []) m[c] = { taux: TAUX_DEFAUT_H, tauxPublie: false, max: null };
    return m;
  },
};

let cache = null;
export async function lireMarge(db) {
  const now = Date.now();
  if (cache && now - cache.t < 600e3) return cache;
  const ancien = await db.prepare("SELECT t, json FROM etat WHERE id=4").first();
  if (ancien && now - ancien.t < 600e3) { cache = { t: ancien.t, ...JSON.parse(ancien.json) }; return cache; }
  const plat = {}, statut = {};
  await Promise.all(Object.entries(SOURCES).map(async ([ex, f]) => {
    try { plat[ex] = await f(); statut[ex] = { ok: true, n: Object.keys(plat[ex]).length }; }
    catch (e) { statut[ex] = { ok: false, err: String(e.message || e).slice(0, 120) }; if (cache?.plat?.[ex]) plat[ex] = cache.plat[ex]; }
  }));
  cache = { t: now, plat, statut };
  await db.prepare("INSERT OR REPLACE INTO etat (id,t,json) VALUES (4,?,?)").bind(now, JSON.stringify({ plat, statut })).run();
  return cache;
}
// La crypto peut-elle être empruntée sur cette plateforme pour cette quantité ? → {taux par heure, tauxPublie} ou null
export function emprunt(marge, ex, base, qte) {
  const e = marge?.plat?.[ex]?.[base];
  if (!e) return null;
  if (e.max != null && e.max < qte) return null;
  return e;
}
