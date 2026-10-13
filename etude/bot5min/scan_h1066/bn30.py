import numpy as np, pandas as pd
z = np.load("../btc/btc1s.npz"); t = z["t"]; c = z["c"].astype(float); v = z["v"]; vb = z["vb"]
assert np.all(np.diff(t) == 1)
n = len(t); t0 = t[0]; off = (300 - t0 % 300) % 300
cs = lambda x: np.concatenate([[0], np.cumsum(x)])
Cc, Cv, Cvb = cs(c), cs(v), cs(vb); d1 = np.diff(c, prepend=c[0]); Cd2 = cs(d1 ** 2)
avg = lambda a, b: (Cc[b] - Cc[a]) / (b - a)
rows = []; prevmove = None
starts = list(range(off + 300, n - 360, 300))
for s0 in starts:
    K = avg(s0 - 60, s0); Fv = avg(s0 + 240, s0 + 300); y = 1 if Fv > K else -1
    st = int(t[s0]); mv = Fv - K
    for tt in (60, 120, 180, 210, 240, 270):
        i = s0 + tt; p = c[i]; rest = 300 - tt
        sd30 = np.sqrt((Cd2[i + 1] - Cd2[i - 29]) / 30); sd300 = np.sqrt((Cd2[i + 1] - Cd2[i - 299]) / 300); sd1h = np.sqrt((Cd2[i + 1] - Cd2[max(i - 3599, 0)]) / min(3600, i))
        lead = 1 if p > K else -1; zz = (p - K) / (sd300 * np.sqrt(rest) + 1e-9)
        seg = c[s0:i + 1]; fav = lead * (seg - K)
        f = dict(st=st, t=tt, z=abs(zz), rev=int(y != lead), v30r=sd30 / (sd300 + 1e-9), v300r=sd300 / (sd1h + 1e-9),
                 vol30r=((Cv[i + 1] - Cv[i - 29]) / 30) / ((Cv[i + 1] - Cv[max(i - 3599, 0)]) / min(3600, i) + 1e-12),
                 tbi30=lead * (2 * (Cvb[i + 1] - Cvb[i - 29]) / (Cv[i + 1] - Cv[i - 29] + 1e-12) - 1),
                 tbi120=lead * (2 * (Cvb[i + 1] - Cvb[i - 119]) / (Cv[i + 1] - Cv[i - 119] + 1e-12) - 1),
                 m10=lead * (p - c[i - 10]) / (sd300 * np.sqrt(10) + 1e-9), m30=lead * (p - c[i - 30]) / (sd300 * np.sqrt(30) + 1e-9),
                 m60=lead * (p - c[i - 60]) / (sd300 * np.sqrt(60) + 1e-9),
                 fade=(fav.max() - fav[-1]) / (sd300 * np.sqrt(rest) + 1e-9), maxz=fav.max() / (sd300 * np.sqrt(rest) + 1e-9),
                 crosses=int(np.sum(np.diff(np.sign(seg - K)) != 0)),
                 tsince=tt - (np.where(np.sign(seg - K) != lead)[0].max() if np.any(np.sign(seg - K) != lead) else -1),
                 prevw=(np.nan if prevmove is None else lead * np.sign(prevmove)), prevz=(np.nan if prevmove is None else lead * prevmove / (sd300 * np.sqrt(300) + 1e-9)),
                 h1=lead * (p - c[max(i - 3600, 0)]) / (sd1h * 60 + 1e-9),
                 hour=(st // 3600) % 24, dow=((st // 86400) + 4) % 7, minute=(st // 60) % 60,
                 rnd100=float(((min(p, K) // 100 + 1) * 100) < max(p, K)), rnd500=float(((min(p, K) // 500 + 1) * 500) < max(p, K)),
                 dist100=lead * (((p // 100 + (1 if lead < 0 else 0)) * 100) - p) / (sd300 * np.sqrt(rest) + 1e-9),
                 dfund=min((st % 28800), 28800 - st % 28800) / 60)
        rows.append(f)
    prevmove = mv
D = pd.DataFrame(rows); D["jour"] = (D.st - D.st.min()) // 86400; D["part"] = np.where(D.jour < 20, "E", "C")
D.to_pickle("bn30.pkl"); print("FIN", D.shape, D.st.nunique(), D.groupby("part").st.nunique().to_dict())
