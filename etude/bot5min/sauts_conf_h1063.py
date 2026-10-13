"""Sauts du perp ≥ 5 $ en 300 ms : confirmation par les autres bourses et état de Polymarket au moment du saut."""
import sys, json, gzip, pickle
import numpy as np
sys.path.insert(0, "/home/claude/wallet-autopsy/etude/bot5min")
import liquidite_h833 as L, latence_h766 as LH, dpe_h841 as DP
from jambe_couverture_h1058 import achat_d
G, cyc = L.grille(sys.argv[1]); Y = L.resultats_officiels(cyc); out = []
SRC = ["perp", "okx", "bn", "cb", "cl"]
for st in sorted(s for s in cyc if s in Y):
    try: R = json.load(gzip.open(cyc[st]["f"]))
    except Exception: continue
    rows = sorted(R.get("ex", []), key=lambda r: r[0])
    ser = {k: [] for k in SRC}
    for r in rows:
        for k, v in zip(SRC, r[1:]):
            if v and v[0]: ser[k].append((r[0], v[0]))
    if len(ser["perp"]) < 100: continue
    A = {k: (np.array([x[0] for x in v], float), np.array([x[1] for x in v], float)) for k, v in ser.items() if v}
    def mv(k, t0, t1):
        if k not in A: return np.nan
        tt, pp = A[k]; i0 = np.searchsorted(tt, t0, "right") - 1; i1 = np.searchsorted(tt, t1, "right") - 1
        return pp[i1] - pp[i0] if i0 >= 0 and i1 >= 0 else np.nan
    tt, px = A["perp"]; trig = []; last = -1e18; j0 = 0
    for k in range(len(tt)):
        t = tt[k]
        while tt[j0] < t - 300: j0 += 1
        if not (st * 1000 + 30000 <= t <= st * 1000 + 280000) or t - last < 5000: continue
        d = px[k] - px[j0]
        if abs(d) >= 5: trig.append((int(t), d)); last = t
    if not trig: continue
    T = []
    for t, d in trig: T += [t - 1000, t, t + 164]
    try: E = {k: DP.compact(v) for k, v in LH.Cycle(cyc[st]["f"]).etats(sorted(set(T))).items()}
    except Exception: continue
    for t, d in trig:
        X = "Up" if d > 0 else "Down"; sg = 1 if d > 0 else -1
        a = DP.meilleur(E.get(t), X, "a"); b = DP.meilleur(E.get(t), X, "b"); a1 = DP.meilleur(E.get(t - 1000), X, "a"); b1 = DP.meilleur(E.get(t - 1000), X, "b")
        if not a or not (400 <= a <= 700): continue
        q, c = achat_d(E.get(t + 164), X, a + 10)
        if q <= 0 or c < 5: continue
        win = int((Y[st] == 1.0) == (X == "Up"))
        f = dict(st=st, t=t, X=X, d=abs(d), ask=a / 1000, pe=c / q, c=c, win=win, hold=q * win - c, rest=st + 300 - t / 1000,
                 poly1=((a + b) - (a1 + b1)) / 2000 if a and b and a1 and b1 else np.nan)
        for k in ("okx", "bn", "cb", "cl"): f[k] = sg * mv(k, t - 300, t)
        f["perp1s"] = sg * mv("perp", t - 1300, t - 300)                      # le perp avait-il déjà bougé dans la seconde d'avant ?
        f["nconf"] = sum(1 for k in ("okx", "bn", "cb") if np.isfinite(f[k]) and f[k] >= 2)
        out.append(f)
pickle.dump(out, open(sys.argv[2], "wb")); print("FIN", len(out))
