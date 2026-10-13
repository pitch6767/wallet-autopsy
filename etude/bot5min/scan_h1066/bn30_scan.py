import numpy as np, pandas as pd
D = pd.read_pickle("bn30.pkl"); D = D[D.z < 3].copy()
D["zb"] = pd.cut(D.z, [0, .1, .2, .3, .45, .6, .8, 1, 1.3, 1.7, 2.2, 3])
base = D[D.part == "E"].groupby(["t", "zb"], observed=True).rev.mean().rename("base")
D = D.join(base, on=["t", "zb"]); D["ex"] = D.rev - D.base
print("renversement global", D.groupby("part").rev.mean().round(3).to_dict())
rng = np.random.default_rng(3); rows = []
for c in ["v30r", "v300r", "vol30r", "tbi30", "tbi120", "m10", "m30", "m60", "fade", "maxz", "crosses", "tsince", "prevw", "prevz", "h1", "rnd100", "rnd500", "dist100", "dfund", "hour", "dow", "minute"]:
    E = D[(D.part == "E") & np.isfinite(D[c])]
    if E[c].nunique() <= 2: q = (0.5, 0.5); lo = lambda Z: Z[Z[c] < 0.5]; hi = lambda Z: Z[Z[c] >= 0.5]
    else:
        q = np.nanquantile(E[c], [0.2, 0.8]); lo = lambda Z: Z[Z[c] <= q[0]]; hi = lambda Z: Z[Z[c] >= q[1]]
    dd = lambda Z: hi(Z).ex.mean() - lo(Z).ex.mean()
    cy = E.st.unique(); idx = {s: i for i, s in enumerate(cy)}; gi = E.st.map(idx).values
    bs = []
    for _ in range(150):
        w = np.bincount(rng.integers(0, len(cy), len(cy)), minlength=len(cy))[gi]
        Z = E.assign(w=w); h = hi(Z); l = lo(Z)
        bs.append((h.ex * h.w).sum() / h.w.sum() - (l.ex * l.w).sum() / l.w.sum())
    C = D[(D.part == "C") & np.isfinite(D[c])]
    rows.append((c, 100 * dd(E), dd(E) / np.std(bs), 100 * dd(C), 100 * hi(E).ex.mean(), 100 * lo(E).ex.mean(), 100 * hi(C).ex.mean(), 100 * lo(C).ex.mean()))
R = pd.DataFrame(rows, columns=["var", "E_pts", "zE", "C_pts", "E_haut", "E_bas", "C_haut", "C_bas"]); R["coh"] = np.sign(R.E_pts) == np.sign(R.C_pts)
pd.set_option("display.width", 200); print(R.sort_values("zE", key=abs, ascending=False).round(2).to_string(index=False))
