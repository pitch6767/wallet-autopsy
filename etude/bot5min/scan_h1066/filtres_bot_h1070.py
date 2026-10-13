import numpy as np, pandas as pd
T = pd.read_pickle("trades_bot.pkl"); P = pd.read_pickle("panel.pkl")
parts = P.groupby("st").part.first()
T = T[T.st.isin(parts.index) & T.rest.notna()].copy(); T["part"] = T.st.map(parts)
T["s"] = (300 - T.rest).round().astype(int); T = T[(T.s >= 31) & (T.s <= 299)]
T["c"] = T.prix * T.parts
Pi = P.set_index(["st", "s"]); F = pd.read_pickle("feats.pkl").set_index(["st", "t"])
g = lambda col, ds=0: Pi[col].reindex(pd.MultiIndex.from_arrays([T.st, T.s - ds])).values
sx = np.where(T.cote == "Up", 1, -1)
T["m30"] = sx * (g("perp", 1) - g("perp", 31)); T["m10"] = sx * (g("perp", 1) - g("perp", 11))
T["vr"] = F.v300r.reindex(pd.MultiIndex.from_arrays([T.st, T.s])).values
T["pimb"] = sx * (g("udb", 1) - g("uda", 1)) / (g("udb", 1) + g("uda", 1))
T["bimb"] = sx * (g("cb10", 1) - g("ca10", 1)) / (g("cb10", 1) + g("ca10", 1))
T["poly5"] = sx * (g("um", 1) - g("um", 6))
T["m00"] = ((T.st // 60) % 60).isin([0, 30])
# saut Bybit vu en premier dans notre sens dans les 10 s avant l'achat
D = pd.read_pickle("premier.pkl"); B = D[(D.place == "by") & (D.nconf3 == 0)][["st", "t", "X"]]
bj = {}
for r in B.itertuples(): bj.setdefault(r.st, []).append((r.t / 1000 - r.st, 1 if r.X == "Up" else -1))
T["by10"] = [any(0 <= s - ts <= 10 and sg == x for ts, sg in bj.get(st, [])) for st, s, x in zip(T.st, T.s, sx)]
T["by10c"] = [any(0 <= s - ts <= 10 and sg == -x for ts, sg in bj.get(st, [])) for st, s, x in zip(T.st, T.s, sx)]
T.to_pickle("trades_feats.pkl")
print(len(T), T.nom.nunique(), T.groupby("part").size().to_dict())
f = lambda x: 100 * x.net.sum() / x.c.sum() if len(x) else np.nan
def show(nom, m):
    r = [f"{p} gardés {int((m & (T.part == p)).sum()):5d} {f(T[m & (T.part == p)]):+6.1f}% / écartés {f(T[~m & (T.part == p)]):+6.1f}%" for p in "AVT"]
    print(f"{nom:36s}", " | ".join(r))
show("tous", T.s >= 0)
show("élan perp 30 s POUR nous", T.m30 > 0); show("élan perp 30 s CONTRE nous", T.m30 < 0)
show("élan perp 10 s POUR nous", T.m10 > 0)
show("marché calme (vr<1)", T.vr < 1)
show("carnet Poly POUR nous", T.pimb > 0); show("carnet Binance POUR nous", T.bimb > 0)
show("Poly a monté pour nous 5 s", T.poly5 > 0); show("Poly a baissé contre nous 5 s", T.poly5 < 0)
show("fenêtre :00/:30", T.m00)
show("saut Bybit POUR nous < 10 s", T.by10); show("saut Bybit CONTRE nous < 10 s", T.by10c)
