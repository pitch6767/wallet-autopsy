"""BOT95 — H1069 : COMBINAISON (Pitch, 13.10.2026 21:19 « Et si tu combines 1 ou 2 de tes trouvailles ? »). Règle BY1 (H1068) + C1 : le saut va
CONTRE l'élan des 30 s précédentes du perp (perp à s−1 moins perp à s−31, dans le sens du saut, < 0) + C2 : marché calme (σ 300 s / σ 3 600 s des
variations 1 s du perp < 1). Choisie parmi ~15 combinaisons en regardant les TROIS périodes (aucune valeur de preuve) : +29 % / +36 % / +25 %
(41 / 21 / 78 entrées, IC 90 % > 0 dans les trois). Figée le 13.10.2026 ~21:35 ; seule preuve : cycles ≥ 13.10, une fois (--confirmation).
---- texte d'origine de H1068 ----
BOT95 — H1068 : saut vu sur CHAQUE transaction Bybit (le flux « perp » du bot), avant que OKX / Binance / Coinbase ne bougent.
Exploration du 13.10.2026 soir (apprentissage, validation ET test regardés : aucune valeur de preuve) ; la règle est FIGÉE ici le
13.10.2026 ~21:20, avant tout calcul sur les cycles ≥ 13.10, qui serviront de seule confirmation (--confirmation, une fois).
Note : le « perp » du bot EST Bybit BTCUSDT ; les études H1058–H1063 le lisaient échantillonné (~3 fois/s) ; ici chaque transaction.
RÈGLE BY1 : prix Bybit (transactions) bouge ≥ 5 $ en 300 ms (30–280 s, pause 5 s), OKX swap, Binance spot et Coinbase n'ont PAS bougé
  de 2 $ dans le même sens sur ces 300 ms ; côté du saut au meilleur vendeur 0,40–0,70 ; achat preneur à +164 ms, limite vendeur + 1 c,
  10 $ et 100 $ ; gardé jusqu'au règlement.
EXPLORATION (10 $) : +12 % / +19 % / +7 % (160 / 100 / 265 entrées) ; 100 $ : +13,5 % / +15,8 % / +7,6 % ; IC test contient 0.
  Sauts Bybit déjà confirmés par une autre place : −5 % / +6 % / −12 %.
CRITÈRE DE CONFIRMATION : ROI > 0 et IC 90 % par cycles > 0 (10 $). Sinon pas démontré.
Usage : python3 etude/bot5min/premier_bybit_h1068.py dossier_cycles [--confirmation]"""
import os, sys, json, gzip, numpy as np, pandas as pd
ICI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, ICI)
import liquidite_h833 as L, latence_h766 as LH, dpe_h841 as DP, reversal_h1003 as RV
from jambe_couverture_h1058 import achat_d
CONF = "--confirmation" in sys.argv
if CONF: L.RESERVE = 10 ** 12
TEST1 = 1791849600; RNG = np.random.default_rng(1068)
G, cyc = L.grille(sys.argv[1]); Y = L.resultats_officiels(cyc)
_dp = pd.Series(G["perp"]).diff(); V300 = _dp.rolling(300, min_periods=200).std().values; V3600 = _dp.rolling(3600, min_periods=1800).std().values
cycles = sorted(s for s in cyc if s in Y)
if CONF: cycles = [s for s in cycles if s >= TEST1]; part = lambda s: "confirmation"
else:
    dev = [s for s in cycles if s < RV.DEV_FIN]; tr = set(dev[:len(dev) * 2 // 3]); va = set(dev[len(dev) * 2 // 3:]); cycles = [s for s in cycles if s < TEST1]
    part = lambda s: "apprentissage" if s in tr else ("validation" if s in va else "test")
out = []
for st in cycles:
    try: R = json.load(gzip.open(cyc[st]["f"]))
    except Exception: continue
    rows = sorted(R.get("ex", []), key=lambda r: r[0]); tx = R.get("trx") or {}
    S = {k: np.array([(r[0], r[j][0]) for r in rows if r[j] and r[j][0]], float) for k, j in (("okx", 2), ("cb", 4))}
    S["bn"] = np.array([(r[0], r[3]) for r in sorted(tx.get("bn", []), key=lambda r: r[0])], float)
    by = np.array([(r[0], r[3]) for r in sorted(tx.get("by", []), key=lambda r: r[0])], float)
    if len(by) < 50 or any(len(v) < 20 for v in S.values()): continue
    def px(k, t):
        a = S[k]; i = np.searchsorted(a[:, 0], t, "right") - 1; return a[i, 1] if i >= 0 else np.nan
    trig = []; last = -1e18; j0 = 0
    for i in range(len(by)):
        t = by[i, 0]
        while by[j0, 0] < t - 300: j0 += 1
        if not (st * 1000 + 30000 <= t <= st * 1000 + 280000) or t - last < 5000: continue
        d = by[i, 1] - by[j0, 1]
        if abs(d) >= 5: trig.append((int(t), d)); last = t
    if not trig: continue
    T = sorted({t for t, _ in trig} | {t + 164 for t, _ in trig})
    try: E = {k: DP.compact(v) for k, v in LH.Cycle(cyc[st]["f"]).etats(T).items()}
    except Exception: continue
    for t, d in trig:
        sg = 1 if d > 0 else -1; X = "Up" if d > 0 else "Down"
        if sum(1 for k in S if sg * (px(k, t) - px(k, t - 300)) >= 2): continue
        a = DP.meilleur(E.get(t), X, "a")
        if not a or not (400 <= a <= 700): continue
        i = int(t // 1000) - G["t0"]
        if not (sg * (G["perp"][i - 1] - G["perp"][i - 31]) < 0 and V300[i] / V3600[i] < 1): continue
        win = int((Y[st] == 1.0) == (X == "Up"))
        for usd in (10, 100):
            q, c = achat_d(E.get(t + 164), X, a + 10, usd)
            if q > 0 and c >= usd / 2: out.append((part(st), st, usd, c, q * win - c, win))
D = pd.DataFrame(out, columns=["part", "st", "usd", "c", "pnl", "win"])
parts = ["confirmation"] if CONF else ["apprentissage", "validation", "test"]
o = [f"# Bot95 — H1068 : saut Bybit vu en premier + contre l'élan + calme (H1069){' — CONFIRMATION (≥ 13.10)' if CONF else ' (exploration)'}\n", "Aucun ordre.\n",
     "| Taille | Période | Cycles | Entrées | Gagnantes | Engagé moyen | P&L ($) | ROI | IC 90 % par cycles |", "|---|---|---|---|---|---|---|---|---|"]
for usd in (10, 100):
    for pa in parts:
        x = D[(D.usd == usd) & (D.part == pa)]; nc = len([s for s in cycles if part(s) == pa]); g = x.groupby("st").pnl.sum().values
        vv = np.concatenate([g if len(g) else np.zeros(1), np.zeros(max(nc - max(len(g), 1), 0))]); lo, hi = np.percentile(vv[RNG.integers(0, len(vv), (4000, len(vv)))].sum(1), [5, 95])
        o.append(f"| {usd} $ | {pa} | {nc} | {len(x)} | {int(x.win.sum())} | {x.c.mean():.1f} | {x.pnl.sum():+.0f} | {100 * x.pnl.sum() / max(x.c.sum(), 1):+.1f} % | [{lo:+.0f} ; {hi:+.0f}] |")
if CONF:
    x = D[D.usd == 10]; o.append(f"\nVerdict (10 $) : {'confirmé' if x.pnl.sum() > 0 and lo > 0 else 'pas démontré'}")
f = os.path.join(ICI, "resultat_combi_h1069" + ("_confirmation" if CONF else "") + ".md"); open(f, "w").write("\n".join(o) + "\n"); print("\n".join(o))
