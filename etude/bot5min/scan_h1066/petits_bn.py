import numpy as np, pandas as pd
z = np.load("../btc/btc1s.npz"); t = z["t"]; c = z["c"].astype(float); v = z["v"]; vb = z["vb"]; t0 = t[0]
cs = lambda x: np.concatenate([[0], np.cumsum(x)]); Cc, Cv, Cvb = cs(c), cs(v), cs(vb); d1 = np.diff(c, prepend=c[0]); Cd2 = cs(d1 ** 2)
avg = lambda a, b: (Cc[b] - Cc[a]) / (b - a)
U = pd.read_pickle("petits_uniq.pkl"); U = U[(U.st2 < 1791849600) & U.tt.notna()]
rows = []
for r in U.itertuples():
    s0 = int(r.st2 - t0); i = int(r.tt - t0)
    if i + 1 >= len(c) or s0 < 3600 or i < 0: continue
    K = avg(s0 - 60, s0); p = c[i]; tt = i - s0; rest = 300 - tt
    if not (0 < tt < 300): continue
    lead = -1 if r.cote == "Up" else 1          # le favori = l'opposé de notre billet
    sd30 = np.sqrt((Cd2[i + 1] - Cd2[i - 29]) / 30); sd300 = np.sqrt((Cd2[i + 1] - Cd2[i - 299]) / 300); sd1h = np.sqrt((Cd2[i + 1] - Cd2[i - 3599]) / 3600)
    seg = c[s0:i + 1]; fav = lead * (seg - K)
    rows.append(dict(st=r.st2, win=r.win, prix=r.prix, tt=tt, z=lead * (p - K) / (sd300 * np.sqrt(rest) + 1e-9), v300r=sd300 / sd1h, v30r=sd30 / sd300,
                     m10=lead * (p - c[i - 10]) / (sd300 * np.sqrt(10)), m30=lead * (p - c[i - 30]) / (sd300 * np.sqrt(30)), m60=lead * (p - c[i - 60]) / (sd300 * np.sqrt(60)),
                     tbi30=lead * (2 * (Cvb[i + 1] - Cvb[i - 29]) / (Cv[i + 1] - Cv[i - 29] + 1e-12) - 1),
                     vol30r=((Cv[i + 1] - Cv[i - 29]) / 30) / ((Cv[i + 1] - Cv[i - 3599]) / 3600),
                     fade=(fav.max() - fav[-1]) / (sd300 * np.sqrt(rest)), crosses=int(np.sum(np.diff(np.sign(seg - K)) != 0)),
                     rnd100=float(((min(p, K) // 100 + 1) * 100) < max(p, K)), hour=(int(r.st2) // 3600) % 24))
B = pd.DataFrame(rows); B.to_pickle("petits_bn.pkl")
print(len(B), "gagnants", B.win.sum(), "prix moyen", B.prix.mean().round(3))
pd.set_option("display.width", 200)
out = []
for k in ["z", "tt", "prix", "v300r", "v30r", "m10", "m30", "m60", "tbi30", "vol30r", "fade", "crosses", "rnd100", "hour"]:
    g, p_ = B[B.win == 1][k], B[B.win == 0][k]
    q = np.nanquantile(B[k], [1 / 3, 2 / 3]); lo = B[B[k] <= q[0]]; hi = B[B[k] >= q[1]]
    out.append((k, g.median(), p_.median(), (g.mean() - p_.mean()) / (B[k].std() + 1e-9), lo.win.mean(), lo.prix.mean(), hi.win.mean(), hi.prix.mean(), len(lo), len(hi)))
print(pd.DataFrame(out, columns=["var", "méd gagnants", "méd perdants", "écart (σ)", "taux bas tiers", "prix bas", "taux haut tiers", "prix haut", "n bas", "n haut"]).round(3).to_string(index=False))
