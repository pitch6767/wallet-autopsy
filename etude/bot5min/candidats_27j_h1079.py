"""BOT95 — H1079 : les deux candidates au réel (« désaccord 30 zone + modèle monte » et « TWAP fin ») rejouées sur les jours de transactions
publiques Polymarket + Binance 1 s (Pitch, 14.10.2026 01:35 « Je dois avoir plus de jours »). Écrit avant de lancer. Aucun ordre.
APPROXIMATIONS (à dire) : prix d'exercice = moyenne Binance 60 s avant le début (le vrai = Chainlink) ; modèle = probabilité gaussienne que la
  moyenne des 60 dernières secondes dépasse le prix d'exercice, σ = écart-type des variations 1 s de Binance sur 1 h ; « prix vendeur » au moment t =
  médiane des achats du côté dans [t−3, t] ; prix PAYÉ = médiane des achats du côté dans (t, t+6] + frais ; un seul achat par cycle et par règle.
D30M : plus de 60 s restantes, vendeur 0,15–0,35, modèle − vendeur ≥ 0,30, et le modèle a monté d'au moins 0,03 en 3 s.
TWAPF : entre 90 et 20 s restantes, modèle − vendeur ≥ 0,20.
Usage : python3 etude/bot5min/candidats_27j_h1079.py btc1s.npz polytrades_*.json.gz"""
import sys, json, gzip, os, math, numpy as np, pandas as pd
ICI = os.path.dirname(os.path.abspath(__file__)); RNG = np.random.default_rng(1079)
fee = lambda p: 0.07 * p * (1 - p); Phi = lambda x: 0.5 * (1 + math.erf(x / math.sqrt(2)))
z = np.load(sys.argv[1]); t = z["t"]; c = z["c"].astype(float); t0 = t[0]
cs = lambda x: np.concatenate([[0], np.cumsum(x)]); Cc = cs(c); Cd2 = cs(np.diff(c, prepend=c[0]) ** 2)
def proba_up(s0, tt, K, sig):
    i = s0 + tt; p = c[i]
    if tt < 240: mu = p; var = sig ** 2 * ((240 - tt) + 20)
    else:
        n = tt - 240; obs = (Cc[i + 1] - Cc[s0 + 240]) if n > 0 else 0.0; L = 60 - n
        mu = (obs + L * p) / 60; var = sig ** 2 * (L ** 3 / 3) / 3600
    return Phi((mu - K) / max(math.sqrt(var), 1e-6))
rows = []
for f in sorted(sys.argv[2:]):
    for st_, m in json.load(gzip.open(f))["marches"].items():
        st = int(st_); r = m.get("resultat") or {}
        if r.get("Up") not in (0.0, 1.0): continue
        s0 = st - t0
        if s0 < 3700 or s0 + 300 >= len(c): continue
        T = np.array([(x[0] - st, 1 if x[3] == "Up" else 0, x[4]) for x in m["trades"] if x[0] is not None and x[4] and 0 < x[4] < 1 and x[2] == "BUY"], float)
        if len(T) < 20: continue
        K = (Cc[s0] - Cc[s0 - 60]) / 60; sig = math.sqrt((Cd2[s0 + 1] - Cd2[s0 - 3599]) / 3600); upw = int(r["Up"] == 1.0)
        P = {tt: proba_up(s0, tt, K, sig) for tt in range(27, 281)}
        fait = set()
        for tt in range(30, 281):
            for side in (1, 0):
                w = T[(T[:, 0] >= tt - 3) & (T[:, 0] <= tt) & (T[:, 1] == side)][:, 2]
                if not len(w): continue
                ask = float(np.median(w)); pr = P[tt] if side else 1 - P[tt]; pr3 = P[tt - 3] if side else 1 - P[tt - 3]
                for regle, ok in (("D30M", tt < 240 and 0.15 <= ask <= 0.35 and pr - ask >= 0.30 and pr - pr3 >= 0.03),
                                  ("TWAPF", 210 <= tt <= 280 and pr - ask >= 0.20)):
                    if not ok or regle in fait: continue
                    nx = T[(T[:, 0] > tt) & (T[:, 0] <= tt + 6) & (T[:, 1] == side)][:, 2]
                    if not len(nx): continue
                    fait.add(regle); px = float(np.median(nx)); win = int(upw == side)
                    rows.append(dict(st=st, regle=regle, t=tt, ask=ask, px=px, win=win, pnl=win / (px + fee(px)) - 1, jour=pd.to_datetime(st, unit="s").strftime("%d.%m")))
D = pd.DataFrame(rows); D.to_pickle("/tmp/h1079.pkl")
o = ["# Bot95 — H1079 : les deux candidates rejouées sur les jours de transactions publiques\n", "Approximations : voir l'en-tête du script. Résultat par dollar engagé (mise fixe). Aucun ordre.\n"]
for k in ("D30M", "TWAPF"):
    x = D[D.regle == k]; nc = D.st.nunique()
    bs = [x.pnl.values[RNG.integers(0, len(x), len(x))].mean() for _ in range(3000)] if len(x) else [0]
    lo, hi = np.percentile(bs, [5, 95])
    o.append(f"## {k} : {len(x)} achats, {int(x.win.sum())} gagnants, prix moyen {x.px.mean():.3f}, ROI {100 * x.pnl.mean():+.1f} % (IC 90 % [{100 * lo:+.1f} ; {100 * hi:+.1f}] %)\n")
    J = x.groupby("jour").agg(achats=("pnl", "size"), gagnants=("win", "sum"), roi=("pnl", lambda s: round(100 * s.mean(), 1)), gain_pour_10_dollars=("pnl", lambda s: round(10 * s.sum(), 1)))
    o.append(J.to_markdown()); o.append(f"\nJours positifs : {(J.roi > 0).sum()} sur {len(J)}.\n")
open(os.path.join(ICI, "resultat_candidats_27j_h1079.md"), "w").write("\n".join(o) + "\n"); print("\n".join(o))
