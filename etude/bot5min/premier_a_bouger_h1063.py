"""BOT95 — H1063 : le perp « premier à bouger » (Pitch, 13.10.2026 19:53 « Cherche encore »). PROTOCOLE PRÉ-ENREGISTRÉ avant le calcul
de la validation et du test. Hors ligne ; aucun ordre ; aucun fantôme ni stratégie modifié.

ÉVÉNEMENTS : les 603 sauts du perp de H1058/H1062 (≥ 5 $ en 300 ms, 30–280 s, pause 5 s, côté X vendeur 0,40–0,70, achat 10 $ preneur à
  +164 ms, gardé jusqu'au règlement = colonne « hold »). Pour chaque saut, sur les 300 ms précédentes : mouvement signé (dans le sens du
  saut) de Binance spot, OKX, Coinbase, Chainlink ; nconf = nombre de bourses (OKX/Binance/Coinbase) ayant bougé ≥ 2 $ dans le même sens ;
  poly1s = variation signée du milieu Polymarket de X sur la seconde précédente.
IDÉE DE DÉPART : un vrai saut serait confirmé par les autres bourses. EXPLORATION (apprentissage seulement, 153 sauts) : c'est l'inverse.
  Quand le perp bouge SEUL (nconf = 0) : +15 % ; confirmé : −2 %. Quand Chainlink a déjà bougé : −11 %. Quand Polymarket a déjà bougé
  CONTRE nous : −3 % ; sinon +18 %. Lecture : l'avantage existe tant que le perp est le premier ; quand le reste a déjà suivi, c'est payé.
RÈGLES FIGÉES :
  PB1 = sauts où Polymarket n'a pas bougé contre X dans la seconde précédente (poly1s ≥ 0).
  PB2 = PB1 ET perp seul (nconf = 0).
  Témoin : tous les sauts (même achat).
CRITÈRE : ROI > 0 en validation ET sur le test, et IC 90 % par cycles (corrigé pour 2 règles → 95 % bilatéral) > 0 sur le test. Sinon abandon.
  Bootstrap sur les cycles ayant au moins un saut (ceux sans saut de la règle comptent 0). Aucun fantôme sans accord de Pitch. Période ≥ 13.10 non utilisée.
Usage : python3 etude/bot5min/premier_a_bouger_h1063.py sauts_conf_df.pkl"""
import os, sys, time
import numpy as np, pandas as pd

ICI = os.path.dirname(os.path.abspath(__file__))
SORTIE = os.path.join(ICI, "resultat_premier_a_bouger_h1063.md")
RNG = np.random.default_rng(1063)
NOMS = {"A": "apprentissage", "V": "validation", "T": "test"}


def main():
    d = pd.read_pickle(sys.argv[1]); d = d[d.part.isin(["A", "V", "T"]) & (d.st < 1791849600)]
    R = {"PB1": d[d.poly1s >= 0], "PB2": d[(d.poly1s >= 0) & (d.nconf == 0)], "témoin (tous)": d}
    o = ["# Bot95 — H1063 : le perp premier à bouger\n",
         f"Généré le {time.strftime('%d.%m.%Y %H:%M', time.gmtime())} UTC. 10 $ par saut, preneur 164 ms, gardé jusqu'au règlement. Aucun ordre.\n",
         "| Règle | Période | Sauts | Gagnants | P&L ($) | ROI | IC 90 % corrigé (2 règles) |", "|---|---|---|---|---|---|---|"]
    V = {}
    for k, x0 in R.items():
        for p in "AVT":
            x = x0[x0.part == p]; nc = d[d.part == p].st.nunique()
            g = x.groupby("st").hold.sum().values
            vv = np.concatenate([g if len(g) else np.zeros(1), np.zeros(max(nc - max(len(g), 1), 0))])
            bs = vv[RNG.integers(0, len(vv), (4000, len(vv)))].sum(1); lo, hi = np.percentile(bs, [2.5, 97.5])
            pnl = x.hold.sum(); roi = 100 * pnl / max(x.c.sum(), 1)
            o.append(f"| {k} | {NOMS[p]} | {len(x)} | {int(x.win.sum())} | {pnl:+.0f} | {roi:+.1f} % | [{lo:+.0f} ; {hi:+.0f}] |")
            V[(k, p)] = (pnl, lo)
    o.append("\n**Verdict (critère figé)**\n")
    for k in ("PB1", "PB2"):
        ok = V[(k, "V")][0] > 0 and V[(k, "T")][0] > 0 and V[(k, "T")][1] > 0
        o.append(f"- {k} : {'candidat (proposition à Pitch, confirmation ≥ 13.10)' if ok else 'abandon'}")
    open(SORTIE, "w").write("\n".join(o) + "\n"); print("\n".join(o))


if __name__ == "__main__":
    main()
