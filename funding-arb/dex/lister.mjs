// Liste ce qu'on peut vendre à découvert sur les DEX (perpétuels + emprunt Kamino). Lecture publique uniquement.
import fs from "node:fs";
const NOS = ["MMT","ICNT","PIEVERSE","LUNC","PI","EVAA","PEPE","PUMP","LIT","NIGHT","GRASS","FIL","ARB","XLM","ZEC","VVV","HBAR","BTC","ETH","SOL","XRP","HYPE"];
const out = [];
async function j(url, opt) { const r = await fetch(url, { ...opt, signal: AbortSignal.timeout(20000) }); if (!r.ok) throw new Error("HTTP " + r.status); return r.json(); }
const norm = (s) => String(s).toUpperCase().replace(/^K(?=PEPE|BONK|SHIB|FLOKI|LUNC)/, "").replace(/^1000/, "").replace(/[-_/]?(USDT|USDC|USD|PERP)$/, "");
const sources = {
  "Hyperliquid (perps)": async () => (await j("https://api.hyperliquid.xyz/info", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ type: "meta" }) })).universe.filter((u) => !u.isDelisted).map((u) => u.name),
  "Aster (perps)": async () => (await j("https://fapi.asterdex.com/fapi/v1/exchangeInfo")).symbols.filter((s) => s.status === "TRADING").map((s) => s.baseAsset),
  "Lighter (perps)": async () => (await j("https://mainnet.zklighter.elliot.ai/api/v1/orderBooks")).order_books.filter((o) => o.status === "active" && (o.market_type || "perp") === "perp").map((o) => o.symbol),
  "dYdX (perps)": async () => Object.values((await j("https://indexer.dydx.trade/v4/perpetualMarkets")).markets).filter((m) => m.status === "ACTIVE").map((m) => m.ticker),
  "Kamino (emprunt Solana)": async () => (await j("https://api.kamino.finance/kamino-market/7u3HeHxYDLhnCoErrtycNokbQYbWGzLs6JSDqGAv5PfF/reserves/metrics")).map((r) => r.liquidityToken),
};
for (const [nom, f] of Object.entries(sources)) {
  try {
    const l = [...new Set((await f()).map(norm))].sort();
    out.push("=== " + nom + " : " + l.length + " marchés");
    out.push("nos jetons présents : " + (NOS.filter((t) => l.includes(t)).join(", ") || "aucun"));
    out.push("nos jetons absents : " + NOS.filter((t) => !l.includes(t)).join(", "));
    out.push("liste : " + l.join(" "));
  } catch (e) { out.push("=== " + nom + " : ERREUR " + e.message); }
}
fs.writeFileSync("funding-arb/dex/resultat.txt", new Date().toISOString() + "\n" + out.join("\n") + "\n");
