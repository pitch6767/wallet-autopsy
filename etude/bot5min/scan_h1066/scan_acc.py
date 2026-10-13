import numpy as np, pandas as pd
F = pd.read_pickle("feats.pkl"); X = F[(F.t % 5 == 0) & (F.t >= 30) & (F.t <= 280) & np.isfinite(F.acc10)].copy()
X["big"] = (X.acc10.abs() >= 0.10).astype(int)
print("n", X.groupby("part").size().to_dict(), "taux accél ≥10 c en 10 s", X.groupby("part").big.mean().round(3).to_dict())
skip = {"st", "t", "part", "sg", "lost", "acc10", "acc10s", "big"}
rows = []
for c in [c for c in X.columns if c not in skip]:
    A = X[(X.part == "A") & np.isfinite(X[c])]
    if A[c].nunique() < 3: continue
    q = np.nanquantile(A[c], [0.2, 0.8]); out = [c]
    for p in "AVT":
        Z = X[(X.part == p) & np.isfinite(X[c])]; lo = Z[Z[c] <= q[0]]; hi = Z[Z[c] >= q[1]]
        out += [hi.big.mean() - lo.big.mean(), 100 * (hi.acc10s.mean() - lo.acc10s.mean())]
    rows.append(out)
R = pd.DataFrame(rows, columns=["var", "A_big", "A_dir_c", "V_big", "V_dir_c", "T_big", "T_dir_c"])
R["coh_big"] = (np.sign(R.A_big) == np.sign(R.V_big)) & (np.sign(R.A_big) == np.sign(R.T_big))
R["coh_dir"] = (np.sign(R.A_dir_c) == np.sign(R.V_dir_c)) & (np.sign(R.A_dir_c) == np.sign(R.T_dir_c))
pd.set_option("display.width", 250)
print("== qui annonce une ACCÉLÉRATION (taille) ==")
print(R.sort_values("A_big", key=abs, ascending=False).round(3).head(20).to_string(index=False))
print("== qui annonce la DIRECTION (vers le favori, en centimes sur 10 s) ==")
print(R.sort_values("A_dir_c", key=abs, ascending=False).round(3).head(20).to_string(index=False))
