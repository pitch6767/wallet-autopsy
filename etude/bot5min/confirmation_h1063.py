"""BOT95 — H1063 bis : CONFIRMATION pré-enregistrée (13.10.2026 20:20, avant tout calcul sur les cycles ≥ 13.10).
Correction : dans premier_a_bouger_h1063.py, la variable poly1s était signée deux fois (poly1 était déjà dans le sens du saut) : PB1/PB2 ne
testaient donc pas « Polymarket pas contre nous » pour les sauts vers le bas. Les règles corrigées ci-dessous ont été regardées APRÈS la
validation et le test (non pré-enregistrées) ; leur seule preuve propre sera la période réservée ≥ 13.10, évaluée UNE fois par ce script.
RÈGLES FIGÉES : PS = perp seul (nconf = 0) ; PI = Polymarket immobile (milieu de X identique 1 s avant) ; PSI = PS et PI. Témoin : tous.
CRITÈRE : ROI > 0 et IC 95 % par cycles > 0 sur la confirmation (seuil corrigé pour 3 règles). Sinon pas démontré.
Usage : python3 etude/bot5min/sauts_conf_h1063.py dossier_cycles sauts_13.pkl --confirmation ; python3 etude/bot5min/confirmation_h1063.py sauts_13.pkl"""
import os, sys, time, numpy as np, pandas as pd
d = pd.DataFrame(pd.read_pickle(sys.argv[1])); d = d[d.st >= 1791849600]; RNG = np.random.default_rng(10631)
R = {"PS perp seul": d.nconf == 0, "PI Poly immobile": d.poly1 == 0, "PSI les deux": (d.nconf == 0) & (d.poly1 == 0), "témoin": d.nconf >= 0}
o = ["# Bot95 — H1063 bis : confirmation (cycles ≥ 13.10)\n", f"Généré le {time.strftime('%d.%m.%Y %H:%M', time.gmtime())} UTC. 10 $ par saut, gardé. Aucun ordre.\n",
     "| Règle | Sauts | Gagnants | P&L ($) | ROI | IC 98,3 % (corrigé, 3 règles) | Verdict |", "|---|---|---|---|---|---|---|"]
nc = d.st.nunique()
for k, m in R.items():
    x = d[m]; g = x.groupby("st").hold.sum().values; vv = np.concatenate([g if len(g) else np.zeros(1), np.zeros(max(nc - max(len(g), 1), 0))])
    lo, hi = np.percentile(vv[RNG.integers(0, len(vv), (4000, len(vv)))].sum(1), [100 / 120, 100 - 100 / 120]); pnl = x.hold.sum()
    o.append(f"| {k} | {len(x)} | {int(x.win.sum())} | {pnl:+.0f} | {100 * pnl / max(x.c.sum(), 1):+.1f} % | [{lo:+.0f} ; {hi:+.0f}] | {'confirmé' if pnl > 0 and lo > 0 else 'pas démontré'} |")
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "resultat_confirmation_h1063.md"), "w").write("\n".join(o) + "\n"); print("\n".join(o))
