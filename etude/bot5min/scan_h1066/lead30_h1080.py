import numpy as np, pandas as pd, glob
z = np.load("../btc/btc1s.npz"); B = pd.Series(z["c"].astype(float), index=z["t"])
def load(sym):
    fs = sorted(glob.glob(f"../btc/autres/{sym}/*.csv.gz")); D = pd.concat([pd.read_csv(f, usecols=["t", "c"]) for f in fs]); return D.set_index("t").c.astype(float)
E, S = load("ETHUSDT"), load("SOLUSDT")
df = pd.DataFrame({"btc": B, "eth": E, "sol": S}).dropna()
r = np.log(df).diff()
X = pd.DataFrame(index=df.index)
for n, s in r.items():
    for k in (1, 3, 10): X[f"{n}_{k}"] = s.rolling(k).sum()
for h in (1, 3, 10, 30): X[f"y{h}"] = r.btc[::-1].rolling(h).sum()[::-1].shift(-1)
X = X.dropna(); half = len(X) * 2 // 3
import numpy.linalg as la
def r2(cols, y, tr, te):
    A = np.column_stack([np.ones(len(tr))] + [tr[c] for c in cols]); b = la.lstsq(A, tr[y], rcond=None)[0]
    Ae = np.column_stack([np.ones(len(te))] + [te[c] for c in cols]); e = te[y] - Ae @ b; return 1 - e.var() / te[y].var(), b
tr, te = X.iloc[:half], X.iloc[half:]
for h in (1, 3, 10, 30):
    y = f"y{h}"; base = ["btc_1", "btc_3", "btc_10"]
    a, _ = r2(base, y, tr, te); b_, coef = r2(base + ["eth_1", "eth_3", "eth_10", "sol_1", "sol_3", "sol_10"], y, tr, te)
    print(f"BTC dans les {h:2d} s suivantes : R² contrôle BTC seul {100*a:.3f} % | + ETH et SOL {100*b_:.3f} %")
# événements : ETH (ou SOL) bouge fort sur 3 s alors que BTC ne bouge presque pas
for n in ("eth", "sol"):
    sd = X[f"{n}_3"].std(); sdb = X.btc_3.std()
    for part, P in (("exploration", tr), ("contrôle", te)):
        m = (P[f"{n}_3"].abs() > 4 * sd) & (P.btc_3.abs() < 0.5 * sdb)
        sg = np.sign(P[f"{n}_3"][m])
        print(f"{n.upper()} saute (> 4σ en 3 s), BTC immobile — {part}: {m.sum()} cas ; BTC ensuite dans le même sens : 10 s {np.mean(sg*P.y10[m]>0)*100:.0f} % (moy. {1e4*np.mean(sg*P.y10[m]):+.2f} pb), 30 s {np.mean(sg*P.y30[m]>0)*100:.0f} % (moy. {1e4*np.mean(sg*P.y30[m]):+.2f} pb)")
print("--- sans la dernière seconde (anti-décalage d'horodatage) ---")
for n in ("btc", "eth", "sol"):
    X[f"{n}_lag"] = X[f"{n}_10"] - X[f"{n}_1"]   # mouvement de t-10 à t-1
tr, te = X.iloc[:half], X.iloc[half:]
for h in (3, 10, 30):
    y = f"y{h}"; a, _ = r2(["btc_lag", "btc_1"], y, tr, te); b_, _ = r2(["btc_lag", "btc_1", "eth_lag", "sol_lag"], y, tr, te)
    print(f"BTC {h:2d} s : R² contrôle BTC {100*a:.3f} % | + ETH/SOL (t-10 à t-1) {100*b_:.3f} %")
