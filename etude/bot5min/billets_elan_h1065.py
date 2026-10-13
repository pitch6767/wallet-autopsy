"""BOT95 — H1065 : quand un petit billet (≤ 0,20) gagne-t-il ? (Pitch, 13.10.2026 20:14 « Regarde aussi nos trades gagnantes et perdantes sur
les trades très petites »). PROTOCOLE PRÉ-ENREGISTRÉ avant le calcul de la validation. Hors ligne ; aucun ordre ; aucun fantôme modifié.

DONNÉES : tous les achats ≤ 0,20 $ des stratégies du bot (bot95/sauvegarde), dédoublonnés par (cycle, côté) : premier achat, prix minimum.
EXPLORATION (06.10 → 11.10, Binance 1 s, 993 billets, 137 gagnants, prix moyen 0,114, ROI +9 %) :
  le billet gagne nettement plus quand l'ÉLAN DU FAVORI S'EST ARRÊTÉ. m30 ≤ 0 : 17,1 % de gagnants pour 0,117 payé (ROI +42 %) contre 11,6 %
  pour 0,112 (−14 %). Agresseurs Binance pas pour le favori sur 30 s : +35 % contre −6 %. Favori qui a reculé de son plus haut : +48 % contre −20 %.
  Même sens sur les 30 jours de Binance pour TOUTES les fenêtres (H1065 scan : m30, tbi30 et fade, deux sous-périodes de 20 et 10 jours).
RÈGLES FIGÉES (le favori = l'opposé du billet ; σ = écart-type des variations 1 s de Binance sur 300 s ; K = prix d'exercice du cycle) :
  R1 : m30 = (prix − prix 30 s avant) dans le sens du favori ≤ 0.
  R2 : tbi30 = (achats agressifs − ventes agressives) / volume sur Binance 30 s, dans le sens du favori ≤ 0.
  R3 : fade = (plus grand écart favorable au favori depuis le début du cycle − écart actuel) / (σ × √(temps restant)) ≥ 0,1.
CRITÈRE (validation = billets du 12.10, carnet Dublin, jamais regardés) : ROI des billets filtrés > ROI des billets écartés, ET ROI filtré > 0,
  ET IC 90 % par cycles (bootstrap) de la différence > 0. Confirmation ≥ 13.10 plus tard, une fois. Aucun fantôme sans accord de Pitch.
Usage : python3 etude/bot5min/billets_elan_h1065.py dossier_cycles_dublin petits_uniq.pkl"""
import os, sys, numpy as np, pandas as pd
ICI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, ICI)
import liquidite_h833 as L
SORTIE = os.path.join(ICI, "resultat_billets_elan_h1065.md"); RNG = np.random.default_rng(1065)
G, cyc = L.grille(sys.argv[1]); U = pd.read_pickle(sys.argv[2])
U = U[(U.st2 >= 1791763200) & (U.st2 < 1791849600)]
bn = pd.Series(G["bn"]).ffill().values; d = np.diff(bn, prepend=np.nan); v300 = pd.Series(d).rolling(300, min_periods=200).std().values
rows = []
for r in U.itertuples():
    st = int(r.st2)
    if st not in cyc or not cyc[st]["strike"]: continue
    i = int(r.tt) - G["t0"]; s0 = st - G["t0"]; rest = 300 - (int(r.tt) - st)
    if not (0 < rest < 300) or i < 30 or not np.isfinite(bn[i]) or not np.isfinite(v300[i]): continue
    K = cyc[st]["strike"]; lead = -1 if r.cote == "Up" else 1
    fav = lead * (bn[s0:i + 1] - K); fav = fav[np.isfinite(fav)]
    agb = np.nansum(G["agb"][i - 29:i + 1]); ags = np.nansum(G["ags"][i - 29:i + 1])
    rows.append(dict(st=st, win=r.win, prix=r.prix, m30=lead * (bn[i] - bn[i - 30]), tbi30=lead * (agb - ags) / (agb + ags + 1e-9),
                     fade=(fav.max() - fav[-1]) / (v300[i] * np.sqrt(rest) + 1e-9)))
B = pd.DataFrame(rows); B["roi"] = B.win / (B.prix * (1 + 0.07 * (1 - B.prix))) - 1
o = ["# Bot95 — H1065 : petits billets, élan du favori — VALIDATION (billets du 12.10)\n",
     f"{len(B)} billets uniques (cycle, côté), {int(B.win.sum())} gagnants, prix moyen {B.prix.mean():.3f}, ROI {100 * B.roi.mean():+.0f} %. Aucun ordre.\n",
     "| Règle | Billets gardés | Gagnants | Prix | ROI gardés | Billets écartés | ROI écartés | Différence | IC 90 % par cycles | Verdict |", "|---|---|---|---|---|---|---|---|---|---|"]
for nom, m in (("R1 élan 30 s arrêté", B.m30 <= 0), ("R2 agresseurs pas pour le favori", B.tbi30 <= 0), ("R3 favori a reculé", B.fade >= 0.1)):
    a, b = B[m], B[~m]; cy = B.st.unique(); bs = []
    for _ in range(4000):
        s = set(RNG.choice(cy, len(cy))); w = B.st.map(pd.Series(RNG.choice(cy, len(cy))).value_counts()).fillna(0)
        A_, B_ = w[m], w[~m]
        if A_.sum() == 0 or B_.sum() == 0: continue
        bs.append((B.roi[m] * A_).sum() / A_.sum() - (B.roi[~m] * B_).sum() / B_.sum())
    lo, hi = np.percentile(bs, [5, 95]); diff = a.roi.mean() - b.roi.mean()
    ok = diff > 0 and a.roi.mean() > 0 and lo > 0
    o.append(f"| {nom} | {len(a)} | {int(a.win.sum())} | {a.prix.mean():.3f} | {100 * a.roi.mean():+.0f} % | {len(b)} | {100 * b.roi.mean():+.0f} % | {100 * diff:+.0f} pts | [{100 * lo:+.0f} ; {100 * hi:+.0f}] | {'validé (confirmation ≥ 13.10 à faire)' if ok else 'non validé'} |")
open(SORTIE, "w").write("\n".join(o) + "\n"); print("\n".join(o))
