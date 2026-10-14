"""BOT95 — H1080 : ETH (Bybit perp) en avance sur BTC. RÈGLE FIGÉE le 14.10.2026 05:20 (heure suisse), avant tout calcul sur les cycles ≥ 14.10 :
ETH Bybit bouge d au moins 0,03 % en 300 ms (30–280 s, pause 5 s) alors que BTC Bybit n a pas bougé de 2 $ dans le même sens → achat 10 $ du côté
BTC correspondant à +164 ms (vendeur 0,40–0,70, limite + 1 c), gardé jusqu au règlement. Exploration (12.10 après-midi, 7 cas seulement) : BTC suit dans
86 % des cas (+14,5 $ en 2 s), ROI +27 %. Jugement : cycles ≥ 14.10 quand au moins 300 cas seront réunis ; ROI > 0 et IC 90 % par cycles > 0.
Aucun fantôme sans accord de Pitch (14.10 05:00 : « touche à rien »)."""
import sys, json, gzip, numpy as np, pandas as pd
sys.path.insert(0, "/home/claude/wallet-autopsy/etude/bot5min")
import liquidite_h833 as L, latence_h766 as LH, dpe_h841 as DP, reversal_h1003 as RV
from jambe_couverture_h1058 import achat_d
G, cyc = L.grille("../rev_all"); Y = L.resultats_officiels(cyc)
cycles = sorted(s for s in cyc if s in Y); dev = [s for s in cycles if s < RV.DEV_FIN]; tr = set(dev[:len(dev) * 2 // 3]); va = set(dev[len(dev) * 2 // 3:])
part = lambda s: "A" if s in tr else ("V" if s in va else "T"); out = []
for st in cycles:
    try: R = json.load(gzip.open(cyc[st]["f"]))
    except Exception: continue
    t2 = R.get("trx2") or {}; tx = R.get("trx") or {}
    if not t2.get("eth_by"): continue
    E = np.array([(r[0], r[3]) for r in sorted(t2["eth_by"], key=lambda r: r[0])], float); B = np.array([(r[0], r[3]) for r in sorted(tx.get("by", []), key=lambda r: r[0])], float)
    if len(E) < 50 or len(B) < 50: continue
    def px(a, t): i = np.searchsorted(a[:, 0], t, "right") - 1; return a[i, 1] if i >= 0 else np.nan
    trig = []; last = -1e18; j0 = 0
    for i in range(len(E)):
        t = E[i, 0]
        while E[j0, 0] < t - 300: j0 += 1
        if not (st * 1000 + 30000 <= t <= st * 1000 + 280000) or t - last < 5000: continue
        d = E[i, 1] / E[j0, 1] - 1
        if abs(d) >= 0.0003:
            db = px(B, t) - px(B, t - 300)
            if np.sign(d) * db < 2: trig.append((int(t), d)); last = t   # BTC n'a pas (encore) suivi
    if not trig: continue
    T = sorted({t for t, _ in trig} | {t + 164 for t, _ in trig})
    try: Es = {k: DP.compact(v) for k, v in LH.Cycle(cyc[st]["f"]).etats(T).items()}
    except Exception: continue
    for t, d in trig:
        X = "Up" if d > 0 else "Down"; a = DP.meilleur(Es.get(t), X, "a")
        if not a or not (400 <= a <= 700): continue
        q, c = achat_d(Es.get(t + 164), X, a + 10)
        if q <= 0 or c < 5: continue
        win = int((Y[st] == 1.0) == (X == "Up")); bf = np.sign(d) * (px(B, t + 2000) - px(B, t))
        out.append(dict(st=st, part=part(st), d=d, hold=q * win - c, c=c, win=win, btc_suit_2s=bf))
D = pd.DataFrame(out); print(len(D), D.groupby("part").apply(lambda g: pd.Series(dict(n=len(g), roi=round(100 * g.hold.sum() / g.c.sum(), 1), btc2s=round(g.btc_suit_2s.mean(), 1), suit=round((g.btc_suit_2s > 0).mean(), 2)))).to_string())
