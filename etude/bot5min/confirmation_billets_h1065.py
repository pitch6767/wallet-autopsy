"""BOT95 — H1065 bis : petits billets (≤ 0,20) et élan du favori vu DEPUIS Polymarket / Dublin. PRÉ-ENREGISTRÉ le 13.10.2026 ~21:00,
avant tout calcul sur les cycles ≥ 13.10. Hors ligne ; aucun ordre ; aucun fantôme modifié.
HISTORIQUE : H1065 (règles mesurées sur Binance spot : m30, tbi30, fade) NON validé sur les billets du 12.10 (sens inverse, 24 gagnants).
  Sur les billets du 11.10 et du 12.10 (Dublin, 335 billets, 49 gagnants), ces mesures prises côté Polymarket / perp / carnet Binance vont,
  les DEUX jours, dans le sens « le billet gagne plus quand l'élan du favori se retourne » — regardées après coup, donc sans valeur de preuve.
RÈGLES FIGÉES (favori = côté dont le milieu Polymarket ≥ 0,5 à l'instant d'achat ; billet = l'autre côté) :
  T1 : le milieu Polymarket du favori a baissé sur les 5 dernières secondes.
  T2 : le perp a bougé contre le favori sur les 30 dernières secondes.
  T3 : le carnet Binance (cumul 10 $ acheteur − vendeur) penche contre le favori.
CRITÈRE (cycles ≥ 13.10, une seule fois) : ROI gardés > 0, ROI gardés > ROI écartés, IC 90 % par cycles de la différence > 0 (corrigé 3 règles :
  IC 96,7 %). Sinon pas démontré.
Usage : python3 etude/bot5min/confirmation_billets_h1065.py dossier_cycles  (lit bot95/sauvegarde)"""
import os, sys, json, gzip, glob, numpy as np, pandas as pd
ICI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, ICI)
import liquidite_h833 as L
L.RESERVE = 10 ** 12; RNG = np.random.default_rng(10651); TEST1 = 1791849600
rows = []
for f in glob.glob(os.path.join(ICI, "..", "..", "bot95", "sauvegarde", "*.json")):
    try: d = json.load(open(f))
    except Exception: continue
    for x in (d.get("trades") or {}).values():
        if isinstance(x, dict) and x.get("prix") is not None and x["prix"] <= 0.20 and x.get("gagnant") and x.get("start") and x.get("restant_s") is not None:
            rows.append(dict(st=x["start"], cote=x["cote"], prix=x["prix"], win=int(x["gagnant"] == x["cote"]), rest=x["restant_s"]))
U = pd.DataFrame(rows); U = U[U.st >= TEST1].groupby(["st", "cote"]).agg(prix=("prix", "min"), win=("win", "first"), rest=("rest", "median")).reset_index()
G, cyc = L.grille(sys.argv[1]); out = []
for r in U.itertuples():
    if r.st not in cyc: continue
    try: R = json.load(gzip.open(cyc[r.st]["f"]))
    except Exception: continue
    um = {}
    for s in R.get("snap", []):
        if s[1] and s[2]: um[int(s[0] // 1000) - r.st] = (s[1][0][0] + s[2][0][0]) / 2
    t = int(300 - r.rest); u0 = next((um[k] for k in range(t, t - 4, -1) if k in um), None); u5 = next((um[k] for k in range(t - 5, t - 9, -1) if k in um), None)
    i = r.st + t - G["t0"]
    if u0 is None or u5 is None or i < 30: continue
    sg = 1 if u0 >= 0.5 else -1
    out.append(dict(st=r.st, win=r.win, prix=r.prix, T1=sg * (u0 - u5) < 0, T2=sg * (G["perp"][i] - G["perp"][i - 30]) < 0, T3=sg * (G["cb10"][i] - G["ca10"][i]) < 0))
B = pd.DataFrame(out); B["roi"] = B.win / (B.prix * (1 + 0.07 * (1 - B.prix))) - 1
o = ["# Bot95 — H1065 bis : petits billets, confirmation (cycles ≥ 13.10)\n", f"{len(B)} billets, {int(B.win.sum())} gagnants, ROI {100 * B.roi.mean():+.0f} %. Aucun ordre.\n",
     "| Règle | Gardés | Gagnants | ROI gardés | Écartés | ROI écartés | Différence | IC 96,7 % | Verdict |", "|---|---|---|---|---|---|---|---|---|"]
for k in ("T1", "T2", "T3"):
    m = B[k].values.astype(bool); cy = B.st.unique(); bs = []
    for _ in range(4000):
        w = B.st.map(pd.Series(RNG.choice(cy, len(cy))).value_counts()).fillna(0).values
        if w[m].sum() and w[~m].sum(): bs.append((B.roi.values[m] * w[m]).sum() / w[m].sum() - (B.roi.values[~m] * w[~m]).sum() / w[~m].sum())
    lo, hi = np.percentile(bs, [100 / 60, 100 - 100 / 60]); a, b = B.roi[m].mean(), B.roi[~m].mean()
    o.append(f"| {k} | {m.sum()} | {int(B.win[m].sum())} | {100 * a:+.0f} % | {(~m).sum()} | {100 * b:+.0f} % | {100 * (a - b):+.0f} pts | [{100 * lo:+.0f} ; {100 * hi:+.0f}] | {'confirmé' if a > 0 and a > b and lo > 0 else 'pas démontré'} |")
open(os.path.join(ICI, "resultat_confirmation_billets_h1065.md"), "w").write("\n".join(o) + "\n"); print("\n".join(o))
