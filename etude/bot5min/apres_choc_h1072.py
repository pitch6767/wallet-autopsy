"""BOT95 — H1072 : le cycle d'APRÈS un choc. PRÉ-ENREGISTRÉ le 13.10.2026 ~22:15, AVANT le téléchargement des 27 jours (12.09 → 08.10).
IDÉE : la volatilité arrive en grappes (H1066 : sauts 4–5 fois plus fréquents après 30 s agitées). Si Polymarket fixe le prix du cycle suivant
  sans en tenir compte, les billets du cycle qui suit un choc sont trop bon marché.
CHOC (cycle précédent, Binance 1 s) : |prix final moyen 60 s − prix d'exercice| ≥ 2 × σ_1h × √300, OU renversement (le favori Polymarket à 240 s
  ≥ 0,80 a perdu).
RÈGLE CH1 : dans le cycle suivant un choc, au premier instant parmi 120, 150, 180, 210, 240 s où le favori est entre 0,80 et 0,95 → acheter le billet
  (prix = médiane des achats du billet dans (t+1, t+6], + frais). Témoin CH0 : même règle dans les cycles qui ne suivent PAS un choc.
CRITÈRE : ROI CH1 > 0 et > ROI CH0 en exploration (12.09–30.09) ET en validation (01.10–08.10), IC 90 % par cycles de CH1 en validation > 0.
Usage : python3 etude/bot5min/apres_choc_h1072.py btc1s.npz polytrades_*.json.gz"""
import sys, json, gzip, os, numpy as np, pandas as pd
ICI = os.path.dirname(os.path.abspath(__file__)); RNG = np.random.default_rng(1072); FIN_EXPLO = 1790812800
fee = lambda p: 0.07 * p * (1 - p)
z = np.load(sys.argv[1]); t = z["t"]; c = z["c"].astype(float); t0 = t[0]
cs = lambda x: np.concatenate([[0], np.cumsum(x)]); Cc = cs(c); Cd2 = cs(np.diff(c, prepend=c[0]) ** 2)
sd = lambda i, w: np.sqrt((Cd2[i + 1] - Cd2[i + 1 - w]) / w)
info = {}
for f in sorted(sys.argv[2:]):
    for st_, m in json.load(gzip.open(f))["marches"].items():
        st = int(st_); r = m.get("resultat") or {}
        if r.get("Up") not in (0.0, 1.0) or st >= 1791590400: continue
        s0 = st - t0
        if s0 < 3700 or s0 + 300 >= len(c): continue
        T = np.array([(x[0] - st, x[4] if x[3] == "Up" else 1 - x[4], 1 if x[3] == "Up" else 0, x[4]) for x in m["trades"]
                      if x[0] is not None and x[4] and 0 < x[4] < 1 and x[2] == "BUY"], float)
        if len(T) < 20: continue
        K = (Cc[s0] - Cc[s0 - 60]) / 60; Fv = (Cc[s0 + 300] - Cc[s0 + 240]) / 60
        upw = int(r["Up"] == 1.0); big = abs(Fv - K) >= 2 * sd(s0, 3600) * np.sqrt(300)
        w240 = T[(T[:, 0] > 234) & (T[:, 0] <= 240)]; rev = False
        if len(w240) >= 2:
            pu = np.median(w240[:, 1]); rev = (pu >= 0.80 and not upw) or (pu <= 0.20 and upw)
        achat = None
        for tt in (120, 150, 180, 210, 240):
            w = T[(T[:, 0] > tt - 6) & (T[:, 0] <= tt)]
            if len(w) < 2: continue
            pu = np.median(w[:, 1]); fp = max(pu, 1 - pu)
            if not (0.80 <= fp <= 0.95): continue
            tic = 0 if pu >= 0.5 else 1; nx = T[(T[:, 0] > tt) & (T[:, 0] <= tt + 6) & (T[:, 2] == tic)][:, 3]
            if len(nx): px = float(np.median(nx)); achat = (px, int((upw == 1) == (tic == 1))); break
        info[st] = dict(choc=bool(big or rev), achat=achat)
rows = []
for st, v in info.items():
    p = info.get(st - 300)
    if p is None or v["achat"] is None: continue
    px, w = v["achat"]; rows.append(dict(st=st, regle="CH1 après choc" if p["choc"] else "CH0 témoin", px=px, w=w, pnl=w / (px + fee(px)) - 1))
D = pd.DataFrame(rows); D["part"] = np.where(D.st < FIN_EXPLO, "exploration", "validation")
o = ["# Bot95 — H1072 : billets du cycle qui suit un choc (27 jours)\n", "Aucun ordre.\n", "| Règle | Période | Achats | Gagnants | Prix moyen | ROI | IC 90 % par cycles |", "|---|---|---|---|---|---|---|"]
V = {}
for k in ("CH1 après choc", "CH0 témoin"):
    for pa in ("exploration", "validation"):
        x = D[(D.regle == k) & (D.part == pa)]
        bs = x.pnl.values[RNG.integers(0, len(x), (4000, len(x)))].mean(1) if len(x) else np.zeros(1); lo, hi = np.percentile(bs, [5, 95])
        o.append(f"| {k} | {pa} | {len(x)} | {int(x.w.sum())} | {x.px.mean():.3f} | {100 * x.pnl.mean():+.1f} % | [{100 * lo:+.1f} ; {100 * hi:+.1f}] % |"); V[(k, pa)] = (x.pnl.mean(), lo)
ok = all(V[("CH1 après choc", p)][0] > 0 and V[("CH1 après choc", p)][0] > V[("CH0 témoin", p)][0] for p in ("exploration", "validation")) and V[("CH1 après choc", "validation")][1] > 0
o.append(f"\n**Verdict (critère figé)** : {'candidat (proposition à Pitch)' if ok else 'abandon'}")
open(os.path.join(ICI, "resultat_apres_choc_h1072.md"), "w").write("\n".join(o) + "\n"); print("\n".join(o))
