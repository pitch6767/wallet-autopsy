import numpy as np, pandas as pd, sys
F = pd.read_pickle("feats.pkl")
lo_, hi_ = float(sys.argv[1]), float(sys.argv[2]); tset = [int(x) for x in sys.argv[3].split(",")]
X = F[F.t.isin(tset) & (F.fp >= lo_) & (F.fp <= hi_)].copy()
X["ex"] = X.lost - (1 - X.fp)
print("échantillon", X.groupby("part").size().to_dict(), "taux renversement", X.groupby("part").lost.mean().round(3).to_dict(), "attendu", X.groupby("part").fp.mean().rsub(1).round(3).to_dict())
skip = {"st", "t", "part", "fp", "sg", "lost", "acc10", "acc10s", "ex"}
rng = np.random.default_rng(1)
res = []
for c in [c for c in X.columns if c not in skip]:
    A = X[(X.part == "A") & np.isfinite(X[c])]
    if A[c].nunique() < 3 or len(A) < 100: continue
    qs = np.nanquantile(A[c], [0.2, 0.8])
    def d(Z):
        Z = Z[np.isfinite(Z[c])]; lo = Z[Z[c] <= qs[0]]; hi = Z[Z[c] >= qs[1]]
        return hi.ex.mean() - lo.ex.mean(), len(lo), len(hi), hi.lost.mean(), lo.lost.mean()
    dA = d(A)
    # bootstrap par cycle sur A
    cy = A.st.unique(); g = {s: A[A.st == s] for s in cy}; bs = []
    for _ in range(200):
        Z = pd.concat([g[s] for s in rng.choice(cy, len(cy))]); bs.append(d(Z)[0])
    se = np.nanstd(bs)
    dV = d(X[X.part == "V"]); dT = d(X[X.part == "T"])
    res.append((c, dA[0], dA[0] / se if se > 0 else 0, dV[0], dT[0], dA[3], dA[4], dV[3], dV[4], dT[3], dT[4]))
R = pd.DataFrame(res, columns=["var", "A", "zA", "V", "T", "A_haut", "A_bas", "V_haut", "V_bas", "T_haut", "T_bas"])
R["coh"] = (np.sign(R.A) == np.sign(R.V)) & (np.sign(R.A) == np.sign(R["T"]))
pd.set_option("display.width", 250); print(R.sort_values("zA", key=abs, ascending=False).round(3).to_string(index=False))
