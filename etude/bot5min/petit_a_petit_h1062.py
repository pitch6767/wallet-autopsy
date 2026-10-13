"""BOT95 — H1062 : construire la position petit à petit, 10 $ par trade, 50 $ au plus par cycle (Pitch, 13.10.2026 19:26). PROTOCOLE FIGÉ avant
calcul ; règles fixées a priori (pas de réglage) ; apprentissage, validation et test rapportés séparément. Hors ligne ; aucun ordre.

DONNÉES : jeux déjà construits depuis les cycles Dublin (carnet rejoué, preneur 164 ms, frais 0,07·p·(1−p)) :
  - famille SAUT : chaque saut du perp ≥ 5 $ en 300 ms (pause 5 s), côté 0,40–0,70, achat 10 $ (jeu fastlock5, champ « hold ») ;
  - famille FAVORI : points toutes les 2 s où un côté est vendu 0,55–0,90 (20–200 s restantes), achat 10 $ (jeu fav, champ « pnl »).
RÈGLES (chaque achat = 10 $ ; au plus 5 achats = 50 $ par cycle) :
  SAUT  S1 = 1er saut seulement (10 $) ; S50 = 1er saut, 50 $ d'un coup (5 × le même achat) ;
        SP = pyramide : 1er saut, puis +10 $ à chaque nouveau saut DANS LE MÊME SENS ; SA = tous les sauts (les deux sens), 5 premiers.
  FAVORI F1 = 1er point (10 $) ; F50 = 1er point × 5 ;
        FM = monter : +10 $ chaque fois que le prix du même côté a monté de 5 c depuis le dernier achat (renfort dans la force) ;
        FD = moyenne à la baisse : +10 $ chaque fois qu'il a baissé de 5 c (tant qu'il reste ≥ 0,55) ;
        FT = étalé : +10 $ toutes les 30 s tant que le côté reste favori 0,55–0,90.
Usage : python3 etude/bot5min/petit_a_petit_h1062.py fastlock5_df.pkl fav_df.pkl"""
import sys, os, numpy as np, pandas as pd
RNG = np.random.default_rng(1062)
S = pd.read_pickle(sys.argv[1]); F = pd.read_pickle(sys.argv[2])
nom = {"A": "apprentissage", "V": "validation", "T": "test"}
def ic(g):
    v = np.array(list(g.values()) or [0.0]); b = v[RNG.integers(0, len(v), (4000, len(v)))].sum(1); return np.percentile(b, [5, 95])
res = []
for pa in "AVT":
    x = S[S.part == pa].sort_values(["st", "t"])
    R = {k: {} for k in ("S1", "S50", "SP", "SA")}; C = {k: {} for k in R}
    for st, g in x.groupby("st"):
        g = g.reset_index(drop=True); f = g.iloc[0]
        R["S1"][st] = f.hold; C["S1"][st] = f.c
        R["S50"][st] = 5 * f.hold; C["S50"][st] = 5 * f.c
        sp = g[g.X == f.X].head(5); R["SP"][st] = sp.hold.sum(); C["SP"][st] = sp.c.sum()
        sa = g.head(5); R["SA"][st] = sa.hold.sum(); C["SA"][st] = sa.c.sum()
    for k in R: res.append(("SAUT", k, nom[pa], len(R[k]), sum(R[k].values()), sum(C[k].values()), ic(R[k])))
    y = F[F.part == pa].sort_values(["st", "s"])
    R = {k: {} for k in ("F1", "F50", "FM", "FD", "FT")}; C = {k: {} for k in R}
    for st, g in y.groupby("st"):
        f = g.iloc[0]; h = g[g.X == f.X]
        R["F1"][st] = f.pnl; C["F1"][st] = f.c; R["F50"][st] = 5 * f.pnl; C["F50"][st] = 5 * f.c
        for k, cond in (("FM", lambda p, last, s, ls: p >= last + 0.05), ("FD", lambda p, last, s, ls: p <= last - 0.05), ("FT", lambda p, last, s, ls: s >= ls + 30)):
            last, ls, n, pn, cc = f.ask, f.s, 1, f.pnl, f.c
            for _, r in h.iterrows():
                if n >= 5: break
                if r.s <= f.s: continue
                if cond(r.ask, last, r.s, ls): last, ls, n, pn, cc = r.ask, r.s, n + 1, pn + r.pnl, cc + r.c
            R[k][st] = pn; C[k][st] = cc
    for k in R: res.append(("FAVORI", k, nom[pa], len(R[k]), sum(R[k].values()), sum(C[k].values()), ic(R[k])))
o = ["# Bot95 — H1062 : construire la position petit à petit (10 $ par achat, 50 $ au plus)\n",
     "| Famille | Règle | Période | Cycles | P&L ($) | Mise totale ($) | ROI | IC 90 % par cycles |", "|---|---|---|---|---|---|---|---|"]
for fam, k, pa, n, p, c, (lo, hi) in res: o.append(f"| {fam} | {k} | {pa} | {n} | {p:+.0f} | {c:.0f} | {100 * p / max(c, 1):+.1f} % | [{lo:+.0f} ; {hi:+.0f}] |")
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "resultat_petit_a_petit_h1062.md"), "w").write("\n".join(o)); print("\n".join(o))
