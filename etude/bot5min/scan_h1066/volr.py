import sys, numpy as np, pandas as pd
sys.path.insert(0, "/home/claude/wallet-autopsy/etude/bot5min"); import liquidite_h833 as L
G, cyc = L.grille("../rev_all"); p = pd.Series(G["perp"]); d = p.diff()
v300 = d.rolling(300, min_periods=200).std().values; v3600 = d.rolling(3600, min_periods=1800).std().values
bnv = pd.Series(G["agb"] + G["ags"]); tb = pd.Series(G["agb"] - G["ags"])
F = pd.read_pickle("feats.pkl"); i = (F.st - G["t0"] + F.t).values
F["v300r"] = v300[i] / v3600[i]; F["v300"] = v300[i]
F["tbi30"] = F.sg * tb.rolling(30, min_periods=10).sum().values[i] / (bnv.rolling(30, min_periods=10).sum().values[i] + 1e-9)
F.to_pickle("feats.pkl"); print(F[["v300r", "tbi30"]].describe())
