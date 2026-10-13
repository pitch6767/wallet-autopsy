"""Prix Polymarket (transactions publiques) à des instants fixes + mesures Binance 1 s, pour tester si Polymarket intègre les régularités BTC."""
import sys, json, gzip, glob, numpy as np, pandas as pd
z = np.load("../btc/btc1s.npz"); t = z["t"]; c = z["c"].astype(float); v = z["v"]; vb = z["vb"]; t0 = t[0]
cs = lambda x: np.concatenate([[0], np.cumsum(x)]); Cc, Cv, Cvb = cs(c), cs(v), cs(vb); d1 = np.diff(c, prepend=c[0]); Cd2 = cs(d1 ** 2)
sd = lambda i, w: np.sqrt((Cd2[i + 1] - Cd2[i + 1 - w]) / w)
rows = []
for f in sorted(sys.argv[2:]):
    M = json.load(gzip.open(f))["marches"]
    for st_, m in M.items():
        st = int(st_); r = m.get("resultat") or {}
        if r.get("Up") not in (0.0, 1.0): continue
        s0 = st - t0
        if s0 < 3700 or s0 + 300 >= len(c): continue
        T = np.array([(x[0] - st, x[4] if x[3] == "Up" else 1 - x[4], x[4] * x[5]) for x in m["trades"] if x[0] is not None and x[4] and 0 < x[4] < 1 and x[2] == "BUY"], float)
        if len(T) < 20: continue
        K = (Cc[s0] - Cc[s0 - 60]) / 60
        for tt in (60, 90, 120, 150, 180, 210, 240, 260):
            w = T[(T[:, 0] > tt - 6) & (T[:, 0] <= tt)]
            if len(w) < 2: continue
            pu = np.median(w[:, 1]); i = s0 + tt; p = c[i]; lead = 1 if pu >= 0.5 else -1; rest = 300 - tt
            seg = c[s0:i + 1]
            rows.append(dict(st=st, t=tt, pu=pu, fp=max(pu, 1 - pu), lost=int((r["Up"] == 1.0) != (lead > 0)),
                             zb=lead * (p - K) / (sd(i, 300) * np.sqrt(rest)), zh=lead * (p - K) / (sd(i, 3600) * np.sqrt(rest)), v300r=sd(i, 300) / sd(i, 3600),
                             m10=lead * (p - c[i - 10]) / (sd(i, 3600) * np.sqrt(10)), m30=lead * (p - c[i - 30]) / (sd(i, 3600) * np.sqrt(30)),
                             ml1=lead * (c[i - 10] - c[i - 40]) / (sd(i, 3600) * np.sqrt(30)), ml2=lead * (c[i - 20] - c[i - 80]) / (sd(i, 3600) * np.sqrt(60)),
                             ml3=lead * (c[i - 5] - c[i - 15]) / (sd(i, 3600) * np.sqrt(10)), tbil=lead * (2 * (Cvb[i - 9] - Cvb[i - 39]) / (Cv[i - 9] - Cv[i - 39] + 1e-12) - 1),
                             tbi30=lead * (2 * (Cvb[i + 1] - Cvb[i - 29]) / (Cv[i + 1] - Cv[i - 29] + 1e-12) - 1),
                             fade=(lead * (seg - K)).max() - lead * (p - K), rnd100=float(((min(p, K) // 100 + 1) * 100) < max(p, K)),
                             minute=(st // 60) % 60, hour=(st // 3600) % 24, vol=w[:, 2].sum()))
D = pd.DataFrame(rows); D.to_pickle(sys.argv[1]); print("FIN", D.shape, D.st.nunique())
