// day-trader-app — sonde de départ
const UA = "Mozilla/5.0 (compatible; day-trader-app; pitch67@users.noreply.github.com)";
async function essai(url, h = {}) {
  const t = Date.now();
  try {
    const r = await fetch(url, { headers: { "User-Agent": UA, Accept: "*/*", ...h } });
    const txt = await r.text();
    return { url, code: r.status, ms: Date.now() - t, debut: txt.slice(0, 160) };
  } catch (e) { return { url, err: String(e) }; }
}
export default {
  async fetch(req, env) {
    const u = new URL(req.url);
    if (u.pathname === "/api/sonde") {
      const r = await Promise.all([
        essai("https://query2.finance.yahoo.com/v8/finance/chart/TSLA?range=1d&interval=5m"),
        essai("https://query1.finance.yahoo.com/v8/finance/chart/BTC-USD?range=1d&interval=5m"),
        essai("https://query2.finance.yahoo.com/v7/finance/spark?symbols=AAPL,MSFT&range=3mo&interval=1d"),
        essai("https://query2.finance.yahoo.com/v1/finance/search?q=TSLA&newsCount=3&quotesCount=0"),
        essai("https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt"),
        essai("https://data.sec.gov/submissions/CIK0001318605.json"),
        essai("https://www.sec.gov/files/company_tickers.json"),
        essai("https://disclosures-clerk.house.gov/public_disc/financial-pdfs/2026FD.zip"),
        essai("https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=5m&limit=3"),
        essai("https://api.exchange.coinbase.com/products/BTC-USD/candles?granularity=300"),
      ]);
      return Response.json(r);
    }
    return env.ASSETS.fetch(req);
  },
};
