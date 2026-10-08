"""3 dernieres idees (ChatGPT, 08.10.2026) sur « zone + Binance et perp + sortie -10 », vrais carnets du bot (48 h, 4 mesures/s), BTC :
n6 temps utile : distance Chainlink - seuil / (volatilite 1 s x racine du temps restant), signee (+ = notre cote gagne deja)
n4 forme du chemin (60 s avant) : traversees du seuil, part du temps de notre cote, acceleration recente dans notre sens
n10 passage de cycle : resultat du cycle precedent (meme sens que nous ou non)
Chaque variable : tiers bas / milieu / haut, puis meilleurs filtres et mise 25/50 selon la variable, jugement par quarts et sans top 3.
"""
import sys, math, time, statistics
import numpy as np
sys.path.insert(0, "etude/bot5min")
import zone as Z
from sauvetage import resultat, RES, FEE
from proche import charger_brut
from experiences import sim, SORTIES

OUT = "etude/bot5min/"


def variables(ev, pt):
    R = ev["R"]; i = pt["i"]; up = ev["up"]; sg = 1 if up else -1; t0 = R[i][0]
    W = [x for x in R[:i + 1] if t0 - x[0] <= 60 and x[15] and x[16]]
    if len(W) < 20: return None
    cl = np.array([x[15] for x in W]); k = W[-1][16]
    pp = np.array([x[11] for x in W if x[11]])
    d = np.diff(pp) if len(pp) > 5 else np.array([0.0])
    sig = float(np.std(d)) * math.sqrt(4) or 1e-9                      # ~4 mesures/s -> ecart-type par seconde
    dist = (cl[-1] - k) * sg
    s = np.sign((cl - k) * sg)
    trav = int(np.sum(s[1:] != s[:-1]))
    cote = float(np.mean(s > 0))
    def mv(a, b):
        A_ = [x[15] for x in W if t0 - b <= t0 - x[0] < t0 - a or (a <= t0 - x[0] < b)]
        return (A_[0] - A_[-1]) * sg if len(A_) > 1 else 0.0
    r10 = (cl[-1] - next((x[15] for x in W if t0 - x[0] <= 10), cl[-1])) * sg
    r20 = (next((x[15] for x in W if t0 - x[0] <= 10), cl[-1]) - next((x[15] for x in W if t0 - x[0] <= 20), cl[-1])) * sg
    prec = RES.get(("BTC", ev["st"] - 300))
    return {"z": dist / (sig * math.sqrt(max(pt["tl"], 1))), "trav": trav, "cote": cote, "acc": r10 - r20, "r10": r10,
            "prec": None if prec is None else (prec == up)}


def main():
    A = "BTC"
    C = charger_brut(A); sts = sorted(C)
    for st in sts: resultat(A, st)
    for st in sts: resultat(A, st - 300)
    EV = Z.points(A, C)
    q = [sts[int(len(sts) * k / 4)] for k in (1, 2, 3)]
    quart = lambda st: sum(st >= x for x in q)
    T = sorted(Z.trades(EV, Z.BASES["ecart >= 0,30 · 0,15-0,35 · > 60 s"], [Z.FILTRES["Binance >= 0"], Z.FILTRES["perp >= 0"]]), key=lambda z: z[1]["t"])
    act = SORTIES["revente si modele -10 (actuel)"]
    D = []
    for ev, pt in T:
        v = variables(ev, pt)
        if v is None: continue
        r = sim(ev, pt, act); D.append((ev, pt, v, r[0]))
    def stats(X, mise=None):
        if mise:
            pn = [sim(ev, pt, act, mise=mise(v))[0] for ev, pt, v, p in X]; engage = sum(mise(v) for ev, pt, v, p in X)
        else:
            pn = [p for ev, pt, v, p in X]; engage = 50.0 * len(X)
        P = sorted(pn, reverse=True); cum = pk = cr = 0.0
        for x in pn: cum += x; pk = max(pk, cum); cr = min(cr, cum - pk)
        Q = [sum(p for (ev, *_), p in zip(X, pn) if quart(ev["st"]) == k) for k in range(4)]
        return len(X), sum(1 for x in pn if x < 0), Q, sum(pn), sum(P[3:]), cr, sum(pn) / max(1, engage)
    lig = lambda nom, s: f"| {nom} | {s[0]} | {s[1]} | " + " | ".join(f"{x:+.0f}" for x in s[2]) + f" | **{s[3]:+.0f} $** | {s[4]:+.0f} $ | {s[5]:+.0f} $ | {100 * s[6]:+.0f} % |"
    H = "| Regle | Trades | Perdants | Q1 | Q2 | Q3 | Q4 | **Total** | Sans top 3 | Creux | Rendement / $ |\n|---|---|---|---|---|---|---|---|---|---|---|"
    rap = [f"# Temps utile, forme du chemin, passage de cycle — BTC, vrais carnets ({time.strftime('%d.%m %H:%M', time.gmtime(sts[0] + 7200))} -> {time.strftime('%d.%m %H:%M', time.gmtime(sts[-1] + 7500))})", "",
           f"{len(D)} trades « zone + Binance et perp + sortie -10 » (plancher 0,05 $).", "", "## Chaque variable en trois tiers", "", H]
    ref = stats(D); rap.append(lig("REFERENCE", ref))
    noms = {"z": "temps utile (distance / volatilite, + = on gagne deja)", "trav": "traversees du seuil (60 s)", "cote": "part du temps de notre cote (60 s)",
            "acc": "acceleration Chainlink dans notre sens (10 s vs 10 s avant)", "r10": "mouvement Chainlink 10 s dans notre sens"}
    seuils = {}
    for k, lab in noms.items():
        vals = np.array([v[k] for _, _, v, _ in D]); a, b = np.percentile(vals, [33, 67]); seuils[k] = (a, b)
        for nm, f in ((f"tiers bas (< {a:.2f})", lambda x: x < a), (f"tiers milieu", lambda x: a <= x < b), (f"tiers haut (>= {b:.2f})", lambda x: x >= b)):
            X = [d for d in D if f(d[2][k])]
            if X: rap.append(lig(f"{lab} — {nm}", stats(X)))
    for nm, f in (("cycle precedent gagne dans NOTRE sens", lambda v: v["prec"] is True), ("cycle precedent gagne dans l'autre sens", lambda v: v["prec"] is False)):
        X = [d for d in D if f(d[2])]
        if X: rap.append(lig(nm, stats(X)))
    # filtres simples et mise 25/50 : on garde ceux qui ne perdent pas plus de 5 % du gain
    rap += ["", "## Filtres et mises 25/50 testes (garde : total >= 95 % de la reference, ou rendement / $ nettement meilleur)", "", H, lig("REFERENCE", ref)]
    cand = []
    for k, lab in noms.items():
        a, b = seuils[k]
        for nm, f in ((f"sans le tiers bas de « {lab} »", lambda v, k=k, a=a: v[k] >= a), (f"sans le tiers haut de « {lab} »", lambda v, k=k, b=b: v[k] < b)):
            X = [d for d in D if f(d[2])]; s = stats(X); cand.append((nm, s))
            m = lambda v, f=f: 50.0 if f(v) else 25.0
            cand.append((nm.replace("sans", "25 $ sur") + ", 50 $ sinon", stats(D, m)))
    for nm, f in (("sans « cycle precedent dans l'autre sens »", lambda v: v["prec"] is not False), ("sans « cycle precedent dans notre sens »", lambda v: v["prec"] is not True)):
        X = [d for d in D if f(d[2])]; cand.append((nm, stats(X)))
        cand.append((nm.replace("sans", "25 $ sur") + ", 50 $ sinon", stats(D, lambda v, f=f: 50.0 if f(v) else 25.0)))
    bons = [(n, s) for n, s in cand if min(s[2]) > 0 and (s[3] >= 0.95 * ref[3] or s[6] >= ref[6] + 0.15)]
    for n, s in sorted(bons, key=lambda z: -z[1][3]): rap.append(lig(n, s))
    if not bons: rap.append("| aucun | | | | | | | | | | |")
    open(OUT + "resultat_chemin.md", "w").write("\n".join(rap))
    print("\n".join(rap))


if __name__ == "__main__":
    main()
