"""BOT95 — H1081 : grand balayage des sous-jacents qui pourraient MENER le BTC (Pitch, 14.10.2026 05:12 « EUR/USD, or, pétrole, Nasdaq future…
essaie avec des centaines d'idées »). Tourne dans GitHub Actions (accès réseau), lecture seule, aucune donnée payante. Période ≤ 12.10 (le 13.10
est réservé). Aucun ordre, aucun fantôme.

A. Minute (1 m), 15.09 → 12.10 : BTC = Binance BTCUSDT 1 m. Candidats :
   - Yahoo Finance 1 m (indices, futures, devises, matières premières, actions crypto, ETF) — 7 jours par requête, 30 jours au plus ;
   - Binance spot 1 m : toutes les paires USDT les plus échangées (~150) + PAXG (or), EUR ;
   - Binance futures 1 m : toutes les paires perpétuelles USDT (y compris or/argent/actions si elles existent).
   Mesure : part de variance du BTC des 1 et 5 minutes suivantes expliquée en plus du passé du BTC (appris sur les 2/3, mesuré sur le dernier 1/3),
   et corrélation « X maintenant → BTC à la minute suivante ».
B. Seconde (1 s), 05.10 → 11.10 : les 40 cryptos spot les plus échangées + PAXG + EUR (Binance). Même mesure à 10 s, 30 s, 60 s.
Résultats : etude/bot5min/resultat_sousjacents_h1081.md (+ CSV)."""
import io, os, sys, json, time, gzip, zipfile, datetime, urllib.request
import numpy as np, pandas as pd

ICI = os.path.dirname(os.path.abspath(__file__))
UA = {"User-Agent": "Mozilla/5.0 bot95-etude"}
def get(url, t=60):
    for k in range(4):
        try: return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=t).read()
        except Exception as e:
            if "404" in str(e): return None
            time.sleep(2 + 3 * k)
    return None
J0, J1 = datetime.date(2026, 9, 15), datetime.date(2026, 10, 12)
S0, S1 = datetime.date(2026, 10, 5), datetime.date(2026, 10, 11)
assert J1 < datetime.date(2026, 10, 13) and S1 < datetime.date(2026, 10, 13)
LOG = []
def log(*a): s = " ".join(str(x) for x in a); print(s, flush=True); LOG.append(s)

# ------------------------------------------------------------------ téléchargements
def binance_klines(sym, interval, d0, d1, fut=False):
    out = []; d = d0
    while d <= d1:
        base = "futures/um" if fut else "spot"
        raw = get(f"https://data.binance.vision/data/{base}/daily/klines/{sym}/{interval}/{sym}-{interval}-{d}.zip", 120)
        if raw:
            z = zipfile.ZipFile(io.BytesIO(raw)); df = pd.read_csv(z.open(z.namelist()[0]), header=None, usecols=[0, 4])
            df = df[pd.to_numeric(df[0], errors="coerce").notna()]
            t = df[0].astype("int64").values; t = np.where(t > 1e14, t // 1000, t) // 1000
            out.append(pd.Series(df[4].astype(float).values, index=t))
        d += datetime.timedelta(days=1)
    return pd.concat(out).sort_index() if out else None

def yahoo_1m(tk):
    out = []
    for a, b in ((J0, J0 + datetime.timedelta(7)), (J0 + datetime.timedelta(7), J0 + datetime.timedelta(14)), (J0 + datetime.timedelta(14), J0 + datetime.timedelta(21)), (J0 + datetime.timedelta(21), J1 + datetime.timedelta(1))):
        p1 = int(datetime.datetime(a.year, a.month, a.day, tzinfo=datetime.timezone.utc).timestamp()); p2 = int(datetime.datetime(b.year, b.month, b.day, tzinfo=datetime.timezone.utc).timestamp())
        raw = get(f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(tk)}?interval=1m&period1={p1}&period2={p2}")
        if not raw: continue
        try:
            r = json.loads(raw)["chart"]["result"][0]; ts = r["timestamp"]; c = r["indicators"]["quote"][0]["close"]
            out.append(pd.Series(c, index=ts, dtype=float).dropna())
        except Exception: pass
    return pd.concat(out).sort_index() if out else None

import urllib.parse
YAHOO = ["NQ=F", "ES=F", "YM=F", "RTY=F", "CL=F", "BZ=F", "NG=F", "GC=F", "SI=F", "HG=F", "PL=F", "ZN=F", "ZB=F", "ZF=F", "6E=F", "6J=F", "6B=F", "6A=F",
         "DX-Y.NYB", "EURUSD=X", "USDJPY=X", "GBPUSD=X", "AUDUSD=X", "USDCHF=X", "USDCNH=X", "USDMXN=X", "^VIX", "^TNX", "^IRX", "^GSPC", "^NDX", "^DJI", "^RUT", "^N225", "^HSI",
         "^STOXX50E", "^GDAXI", "^FTSE", "BTC=F", "MBT=F", "ETH=F", "BTC-USD", "ETH-USD", "IBIT", "FBTC", "GBTC", "ARKB", "BITO", "ETHA", "MSTR", "COIN", "MARA", "RIOT", "CLSK",
         "HUT", "HOOD", "SQ", "PYPL", "NVDA", "TSLA", "AAPL", "MSFT", "AMZN", "META", "GOOGL", "AMD", "SMCI", "PLTR", "QQQ", "SPY", "IWM", "TLT", "HYG", "GLD", "SLV", "USO",
         "UUP", "FXE", "FXY", "XLK", "XLF", "SOXX", "ARKK", "TQQQ", "SQQQ", "UVXY", "VXX", "KRE", "GDX", "COPX", "URA", "LIT", "CIBR", "BLOK", "BKCH", "DAPP", "WGMI", "CONL", "MSTU", "BITX"]

# ------------------------------------------------------------------ mesure
def mesure(btc, X, horizons, lags_in):
    """btc, X : séries alignées (même index régulier) de prix. Retourne R² hors échantillon de BTC futur avec / sans X."""
    rb = np.log(btc).diff(); rx = np.log(X).diff()
    F = pd.DataFrame({"b1": rb, "x1": rx})
    for k in lags_in: F[f"b{k}"] = rb.rolling(k).sum(); F[f"x{k}"] = rx.rolling(k).sum()
    res = {}
    for h in horizons:
        F["y"] = rb[::-1].rolling(h).sum()[::-1].shift(-1)
        G = F.replace([np.inf, -np.inf], np.nan).dropna()
        G = G[(G.x1 != 0) | (G.b1 != 0)]
        if len(G) < 2000: return None
        n = len(G) * 2 // 3; tr, te = G.iloc[:n], G.iloc[n:]
        cb = ["b1"] + [f"b{k}" for k in lags_in]; cx = cb + ["x1"] + [f"x{k}" for k in lags_in]
        def r2(cols):
            A = np.column_stack([np.ones(len(tr))] + [tr[c].values for c in cols]); b = np.linalg.lstsq(A, tr.y.values, rcond=None)[0]
            Ae = np.column_stack([np.ones(len(te))] + [te[c].values for c in cols]); e = te.y.values - Ae @ b; return 1 - e.var() / te.y.values.var()
        a, b2 = r2(cb), r2(cx)
        res[h] = (a, b2, np.corrcoef(G.x1, G.y)[0, 1], len(G))
    return res

rows = []
def ajoute(nom, source, res, horizons):
    if not res: log("  pas assez de données", nom); return
    d = {"nom": nom, "source": source, "n": res[horizons[0]][3]}
    for h in horizons: a, b, c, n = res[h]; d[f"gain_{h}"] = 100 * (b - a); d[f"r2btc_{h}"] = 100 * a; d[f"corr_{h}"] = c
    rows.append(d)

t_go = time.time()
# ===== A. minute =====
log("A. BTC 1 m"); B1 = binance_klines("BTCUSDT", "1m", J0, J1)
idx = pd.RangeIndex(int(B1.index.min()), int(B1.index.max()) + 60, 60); B1 = B1.reindex(idx).ffill()
HA = (1, 5)
for tk in YAHOO:
    try:
        s = yahoo_1m(tk)
        if s is None or len(s) < 500: log("  yahoo vide", tk); continue
        s.index = (np.array(s.index) // 60) * 60; s = s[~s.index.duplicated(keep="last")]
        X = s.reindex(idx).ffill(limit=5)   # pas de prolongation au-delà de 5 min (marchés fermés : pas de signal)
        m = X.notna(); r = mesure(B1[m], X[m], HA, (5,)); ajoute(tk, "Yahoo 1 m", r, HA); log("  ok", tk, len(s))
    except Exception as e: log("  erreur", tk, e)
try:
    info = json.loads(get("https://api.binance.com/api/v3/ticker/24hr") or b"[]")
    spot = [x["symbol"] for x in sorted(info, key=lambda x: -float(x.get("quoteVolume", 0))) if x["symbol"].endswith("USDT") and x["symbol"] != "BTCUSDT"][:150]
except Exception as e: spot = []; log("ticker spot", e)
for extra in ("PAXGUSDT", "EURUSDT", "XAUTUSDT"):
    if extra not in spot: spot.append(extra)
for sym in spot:
    try:
        s = binance_klines(sym, "1m", J0, J1)
        if s is None: continue
        X = s.reindex(idx).ffill(limit=5); m = X.notna(); ajoute(sym, "Binance spot 1 m", mesure(B1[m], X[m], HA, (5,)), HA)
    except Exception as e: log("  erreur", sym, e)
try:
    fi = json.loads(get("https://fapi.binance.com/fapi/v1/exchangeInfo") or b"{}")
    futs = [x["symbol"] for x in fi.get("symbols", []) if x.get("contractType") == "PERPETUAL" and x["symbol"].endswith("USDT")]
    tfi = [s for s in futs if any(k in s for k in ("XAU", "XAG", "PAXG", "EUR", "OIL", "WTI", "SPX", "NDX", "TSLA", "NVDA", "AAPL", "MSTR", "COIN", "QQQ", "SPY", "GLD"))]
    futs = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT", "DOGEUSDT"] + tfi
except Exception as e: futs = []; log("futures info", e)
for sym in futs:
    try:
        s = binance_klines(sym, "1m", J0, J1, fut=True)
        if s is None: continue
        X = s.reindex(idx).ffill(limit=5); m = X.notna(); ajoute(sym + " perp", "Binance futures 1 m", mesure(B1[m], X[m], HA, (5,)), HA)
    except Exception as e: log("  erreur", sym, e)
A = pd.DataFrame(rows); A.to_csv(os.path.join(ICI, "resultat_sousjacents_h1081_minute.csv"), index=False); rows = []
log("A fini", round(time.time() - t_go), "s")

# ===== B. seconde =====
log("B. BTC 1 s"); Bs = binance_klines("BTCUSDT", "1s", S0, S1)
idx2 = pd.RangeIndex(int(Bs.index.min()), int(Bs.index.max()) + 1, 1); Bs = Bs.reindex(idx2).ffill()
HB = (10, 30, 60)
top = [s for s in spot[:40]] + ["PAXGUSDT", "EURUSDT"]
for sym in top:
    try:
        s = binance_klines(sym, "1s", S0, S1)
        if s is None: continue
        X = s.reindex(idx2).ffill(limit=30); m = X.notna(); ajoute(sym, "Binance spot 1 s", mesure(Bs[m], X[m], HB, (10,)), HB); log("  ok 1s", sym)
    except Exception as e: log("  erreur 1s", sym, e)
Bd = pd.DataFrame(rows); Bd.to_csv(os.path.join(ICI, "resultat_sousjacents_h1081_seconde.csv"), index=False)

# ------------------------------------------------------------------ rapport
o = ["# Bot95 — H1081 : quels sous-jacents mènent le BTC ? (balayage large, lecture seule)\n",
     f"Généré le {datetime.datetime.utcnow():%d.%m.%Y %H:%M} UTC dans GitHub Actions. Période minute {J0:%d.%m}–{J1:%d.%m}, seconde {S0:%d.%m}–{S1:%d.%m} (13.10 réservé, non utilisé).",
     "« Gain » = points de % de variance du BTC FUTUR expliqués EN PLUS du passé du BTC, mesuré sur le dernier tiers (appris sur les deux premiers).",
     "Un gain ≤ 0 = rien de plus que le BTC lui-même. Aucun ordre.\n"]
if len(A):
    o.append(f"## A. Minute — {len(A)} séries testées, classées par gain sur la minute suivante\n")
    A2 = A.sort_values("gain_1", ascending=False)
    o.append(A2[["nom", "source", "n", "gain_1", "gain_5", "corr_1", "corr_5"]].head(40).round(4).to_markdown(index=False))
    o.append(f"\nSéries avec un gain > 0 à 1 min ET à 5 min : {int(((A.gain_1 > 0) & (A.gain_5 > 0)).sum())} sur {len(A)}.\n")
if len(Bd):
    o.append(f"## B. Seconde — {len(Bd)} séries testées, classées par gain à 30 s\n")
    o.append(Bd.sort_values("gain_30", ascending=False)[["nom", "n", "gain_10", "gain_30", "gain_60", "corr_10", "corr_30"]].head(40).round(4).to_markdown(index=False))
o.append("\n## Journal\n\n```\n" + "\n".join(LOG[-80:]) + "\n```\n")
open(os.path.join(ICI, "resultat_sousjacents_h1081.md"), "w").write("\n".join(o))
log("FIN", round(time.time() - t_go), "s")
