"""H1089 complément : pente logistique (fréquence ~ logit du prix), poids du modèle Binance Φ(z) ajouté au prix, et Brier marché − modèle,
par type de marché (5m / 15m / 1h), période et zone de la fenêtre ; IC 90 % par marchés (200 tirages). Descriptif, pas de règle.
Usage : python3 autres_marches_h1089_pentes.py <dossier avec data/autres_btc-*> <dossier avec btc/btc1s.npz, scan/p27, p0913>"""
import sys, glob, json, numpy as np, pandas as pd
sys.path.insert(0, "/home/claude/wallet-autopsy/etude/bot5min")
import autres_marches_h1089 as A
S, P = sys.argv[1], sys.argv[2]; NPZ = P + "/btc/btc1s.npz"
F5 = [f"{P}/scan/p27/polytrades_2026-{d}.json.gz" for d in "09-29 09-30 10-01 10-02 10-03 10-04 10-05 10-06 10-07 10-08".split()] + [f"{P}/p0913/polytrades_2026-10-{d}.json.gz" for d in ("09", "10", "11")]
def logit_fit(X, y):
    b = np.zeros(X.shape[1])
    for _ in range(30):
        q = 1 / (1 + np.exp(-X @ b)); W = q * (1 - q) + 1e-9
        b = b + np.linalg.solve(X.T @ (X * W[:, None]) + 1e-6 * np.eye(X.shape[1]), X.T @ (y - q))
    return b
rng = np.random.default_rng(7); out = {}
for typ, fs in [("5m", F5), ("15m", glob.glob(S + "/data/autres_btc-15m_*")), ("1h", glob.glob(S + "/data/autres_btc-1h_*"))]:
    D, T, M = A.construire(NPZ, typ, fs)
    for pa in ("exploration", "validation", "tout"):
        for zone, (lo, hi) in {"debut_milieu (>=15 % restant)": (.15, 1.01), "fin (<15 % restant)": (0, .15)}.items():
            g = D[(D.reste > lo) & (D.reste <= hi)] if pa == "tout" else D[(D.part == pa) & (D.reste > lo) & (D.reste <= hi)]
            p = g.pu.clip(.005, .995).values; y = g.upw.values; ph = A.PHI(g.z.clip(-8, 8)).clip(.005, .995)
            lp = np.log(p / (1 - p)); lz = np.log(ph / (1 - ph)); st = g.st.values
            u, inv = np.unique(st, return_inverse=True); grp = [np.where(inv == k)[0] for k in range(len(u))]
            def stats(ix):
                b1 = logit_fit(np.column_stack([np.ones(len(ix)), lp[ix]]), y[ix]); b2 = logit_fit(np.column_stack([np.ones(len(ix)), lp[ix], lz[ix]]), y[ix])
                return b1[1], b2[2], ((p[ix] - y[ix]) ** 2).mean() - ((ph[ix] - y[ix]) ** 2).mean()
            base = stats(np.arange(len(y))); B = []
            for _ in range(200):
                ix = np.concatenate([grp[k] for k in rng.integers(0, len(grp), len(grp))]); B.append(stats(ix))
            B = np.array(B); q = np.percentile(B, [5, 95], axis=0)
            out[f"{typ}|{pa}|{zone}"] = dict(marches=len(u), lignes=len(y), pente=round(base[0], 3), pente_ic90=[round(x, 3) for x in q[:, 0]],
                poids_modele=round(base[1], 3), poids_ic90=[round(x, 3) for x in q[:, 1]], brier_marche_moins_modele=round(base[2], 4), brier_ic90=[round(x, 4) for x in q[:, 2]])
            print(typ, pa, zone, out[f"{typ}|{pa}|{zone}"], flush=True)
json.dump(out, open(S + "/pentes.json", "w"), ensure_ascii=False, indent=1)
