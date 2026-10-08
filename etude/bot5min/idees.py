"""7 idees testees sur la ZONE (ecart >= 0,30, jeton 0,15-0,35, > 60 s) — 08.10.2026, vrais carnets du bot (48 h, 4 mesures/s), BTC.
1 juges (modele + prix Polymarket melanges, appris sur la 1re moitie) · 2 calibration selon le temps restant · 5 horloge elastique (mouvements / volatilite)
6 execution (achat 0,25 / 0,5 / 1 s plus tard, taille au vendeur) · 7 origine du desaccord · 8 tendance du BTC (15 et 60 min)
9 bilan de chaque filtre : pertes evitees contre gagnants perdus.
Sorties : resultat_idees.md + idees.json.
"""
import sys, json, math, bisect, statistics, collections
import numpy as np
sys.path.insert(0, "etude/bot5min")
from sauvetage import resultat, RES, FEE
from proche import charger_brut

OUT = "etude/bot5min/"
lg = lambda p: math.log(max(1e-4, min(1 - 1e-4, p)) / (1 - max(1e-4, min(1 - 1e-4, p))))
pnl = lambda p, g: (50 / p) * ((1 if g else 0) - p - FEE(p))


def main():
    A = "BTC"
    C = charger_brut(A); sts = sorted(C)
    for st in sts: resultat(A, st)
    mi = sts[len(sts) // 2]
    # serie globale du perp pour la tendance et la volatilite
    serie = sorted((r[0], r[11]) for st in sts for r in C[st] if r[11])
    ts = [x[0] for x in serie]; ps = [x[1] for x in serie]
    def px_at(t):
        k = bisect.bisect_right(ts, t) - 1
        return ps[k] if k >= 0 and t - ts[k] < 30 else None
    def vol60(t):
        k1 = bisect.bisect_right(ts, t); k0 = bisect.bisect_left(ts, t - 60)
        v = ps[k0:k1]
        if len(v) < 20: return None
        d = np.diff(np.array(v)); return float(np.std(d)) or None
    # evenements : 1er instant zone par cycle et cote ; et 1er desaccord >= 0,10 (pour calibration et juges)
    Z, CAL = [], []
    for st in sts:
        R = C[st]; g = RES.get((A, st))
        if g is None: continue
        for up in (True, False):
            sg = 1 if up else -1; gm = g if up else (not g); deja_cal = False
            for i, r in enumerate(R):
                tl = st + 300 - r[0]
                if tl < 10: break
                ask = r[4] if up else r[6]; fair = r[2] if up else 1 - r[2]
                bid = r[3] if up else r[5]
                if ask is None or bid is None: continue
                mid = (ask + bid) / 2
                if not deja_cal and fair - ask >= 0.10 and 0.03 <= ask <= 0.97:
                    CAL.append({"st": st, "tl": tl, "fair": fair, "mid": mid, "ask": ask, "gm": gm}); deja_cal = True
                if not (0.15 <= ask < 0.35 and fair - ask >= 0.30 and tl > 60): continue
                def back(n):
                    j = i
                    while j > 0 and r[0] - R[j][0] < n: j -= 1
                    return R[j] if r[0] - R[j][0] >= n - 0.5 else None
                h3 = back(3)
                d3 = lambda c: ((r[c] - h3[c]) * sg) if h3 and h3[c] and r[c] else 0.0
                vv = vol60(r[0])
                p15, p60, p0 = px_at(r[0] - 900), px_at(r[0] - 3600), r[11]
                ask3 = (h3[4] if up else h3[6]) if h3 else None; fair3 = (h3[2] if up else 1 - h3[2]) if h3 else None
                # execution : prix au vendeur 1 / 2 / 4 lignes plus tard (~0,25 / 0,5 / 1 s), rempli seulement si <= ask + 0,01
                ex = {}
                for k, lab in ((1, "0,25 s"), (2, "0,5 s"), (4, "1 s")):
                    if i + k < len(R):
                        a2 = R[i + k][4] if up else R[i + k][6]
                        ex[lab] = a2 if a2 is not None and a2 <= ask + 0.01 else None
                    else: ex[lab] = None
                Z.append({"st": st, "t": r[0], "up": up, "gm": gm, "tl": tl, "ask": ask, "fair": fair, "mid": mid, "edge": fair - ask,
                          "taille": (r[8] if up else r[10]) or 0, "bn": d3(14), "perp": d3(11), "okx": d3(12), "cb": d3(13),
                          "zbn": d3(14) / (vv * math.sqrt(3)) if vv else 0.0, "zperp": d3(11) / (vv * math.sqrt(3)) if vv else 0.0,
                          "tr15": ((p0 - p15) * sg) if p15 and p0 else 0.0, "tr60": ((p0 - p60) * sg) if p60 and p0 else 0.0,
                          "dask3": (ask - ask3) if ask3 is not None else 0.0, "dfair3": (fair - fair3) if fair3 is not None else 0.0,
                          "ex": ex, "pnl": pnl(ask, gm)})
                break
    J = {"n_zone": len(Z), "n_cal": len(CAL)}
    rap = [f"# 7 idees testees sur la zone — BTC, vrais carnets ({len(Z)} trades zone, {len(CAL)} desaccords >= 0,10 pour la calibration)", ""]
    ligne = lambda nom, X: (f"| {nom} | {len(X)} | {sum(1 for e in X if e['gm'])} | {sum(e['p'] for e in X if e['st'] < mi):+.0f} $ | {sum(e['p'] for e in X if e['st'] >= mi):+.0f} $ | **{sum(e['p'] for e in X):+.0f} $** | {sum(e['p'] for e in X) / max(1, len(X)):+.1f} $ |")
    H = "| Regle | Trades | Gagnes | 1re moitie | 2e moitie | **Total** | Par trade |\n|---|---|---|---|---|---|---|"
    for e in Z: e["p"] = e["pnl"]
    base = Z
    # ---- 1. juges : regression logistique sur la 1re moitie (y = gagne ; x = logit modele, logit milieu Poly)
    from sklearn.linear_model import LogisticRegression
    tr = [c for c in CAL if c["st"] < mi]
    Xtr = np.array([[lg(c["fair"]), lg(c["mid"])] for c in tr]); ytr = np.array([c["gm"] for c in tr])
    m = LogisticRegression(C=1.0).fit(Xtr, ytr)
    J["juges_coef"] = {"modele": float(m.coef_[0][0]), "poly": float(m.coef_[0][1]), "const": float(m.intercept_[0])}
    for e in Z: e["pj"] = float(m.predict_proba([[lg(e["fair"]), lg(e["mid"])]])[0][1])
    def brier(X, k): return statistics.mean((x[k] - (1 if x["gm"] else 0)) ** 2 for x in X)
    te = [c for c in CAL if c["st"] >= mi]
    for c in te: c["pj"] = float(m.predict_proba([[lg(c["fair"]), lg(c["mid"])]])[0][1])
    rap += ["## 1. Les deux juges (modele + prix Polymarket)", "",
            f"Appris sur la 1re moitie : poids du modele **{m.coef_[0][0]:.2f}**, poids du prix Polymarket **{m.coef_[0][1]:.2f}** (en echelle logit).",
            f"Precision sur la 2e moitie (Brier, plus bas = mieux) : modele seul {brier(te, 'fair'):.3f} · Polymarket seul {brier(te, 'mid'):.3f} · **melange {brier(te, 'pj'):.3f}**", "", H]
    rap.append(ligne("zone (reference)", base))
    for x in (0.0, 0.03, 0.05, 0.10):
        rap.append(ligne(f"zone + juge : proba melangee >= prix + {round(100 * x)} c", [e for e in base if e["pj"] - e["ask"] >= x]))
    # ---- 2. calibration selon le temps restant
    rap += ["", "## 2. Calibration du modele selon le temps restant (desaccords >= 0,10)", "", "| Temps restant | Desaccords | Modele moyen | Prix Polymarket moyen | **Gagnes en vrai** |", "|---|---|---|---|---|"]
    J["calib"] = []
    for a, b in ((10, 60), (60, 120), (120, 200), (200, 300)):
        X = [c for c in CAL if a <= c["tl"] < b]
        if X:
            row = (f"{a}-{b} s", len(X), statistics.mean(c["fair"] for c in X), statistics.mean(c["mid"] for c in X), statistics.mean(1 if c["gm"] else 0 for c in X))
            J["calib"].append(row); rap.append(f"| {row[0]} | {row[1]} | {row[2]:.2f} | {row[3]:.2f} | **{row[4]:.2f}** |")
    rap += ["", "| Modele dit | Desaccords | **Gagnes en vrai** | Prix Polymarket moyen |", "|---|---|---|---|"]
    for a, b in ((0.1, 0.3), (0.3, 0.45), (0.45, 0.6), (0.6, 0.8), (0.8, 1.0)):
        X = [c for c in CAL if a <= c["fair"] < b]
        if X: rap.append(f"| {a:.2f}-{b:.2f} | {len(X)} | **{statistics.mean(1 if c['gm'] else 0 for c in X):.2f}** | {statistics.mean(c['mid'] for c in X):.2f} |")
    # ---- 5. horloge elastique
    rap += ["", "## 5. Horloge elastique : mouvements divises par la volatilite de la derniere minute", "", H]
    rap.append(ligne("zone (reference)", base))
    rap.append(ligne("Binance et perp >= 0 (brut)", [e for e in base if e["bn"] >= 0 and e["perp"] >= 0]))
    for s_ in (-0.5, -1.0):
        rap.append(ligne(f"Binance et perp >= {s_} ecart-type (elastique)", [e for e in base if e["zbn"] >= s_ and e["zperp"] >= s_]))
    rap.append(ligne("Binance et perp >= +0,5 ecart-type (vraiment avec nous)", [e for e in base if e["zbn"] >= 0.5 and e["zperp"] >= 0.5]))
    # ---- 6. execution
    rap += ["", "## 6. Execution reelle : et si l'ordre arrive 0,25 / 0,5 / 1 s plus tard ?", "",
            "Ordre a cours limite = prix vu + 1 c. Rempli seulement si le vendeur est encore la a ce prix.", "",
            "| Delai | Remplis | Non remplis | Resultat des remplis | Par trade | Gain perdu vs instantane |", "|---|---|---|---|---|---|"]
    tot0 = sum(e["pnl"] for e in base)
    rap.append(f"| instantane (reference) | {len(base)} | 0 | {tot0:+.0f} $ | {tot0 / max(1, len(base)):+.1f} $ | — |")
    J["exec"] = {}
    for lab in ("0,25 s", "0,5 s", "1 s"):
        X = [(e, e["ex"][lab]) for e in base if e["ex"][lab] is not None]
        t = sum(pnl(p, e["gm"]) for e, p in X)
        nf = len(base) - len(X); nfw = sum(1 for e in base if e["ex"][lab] is None and e["gm"])
        J["exec"][lab] = (len(X), nf, t)
        rap.append(f"| {lab} | {len(X)} | {nf} (dont {nfw} gagnants) | {t:+.0f} $ | {t / max(1, len(X)):+.1f} $ | {t - tot0:+.0f} $ |")
    petits = [e for e in base if e["taille"] < 50 / e["ask"]]
    rap.append(f"\nTaille : le meilleur vendeur avait moins que les parts voulues (50 $) dans **{len(petits)} / {len(base)}** cas ; ces trades font {sum(e['pnl'] for e in petits):+.0f} $.")
    # ---- 7. origine
    def origine(e):
        mo, pb = e["dfair3"] >= 0.03, e["dask3"] <= -0.03
        return "les deux" if mo and pb else "le modele monte" if mo else "Polymarket baisse" if pb else "deja la (rien n'a bouge en 3 s)" if abs(e["dfair3"]) < 0.03 and abs(e["dask3"]) < 0.03 else "autre"
    rap += ["", "## 7. D'ou vient le desaccord (3 s avant l'achat) ?", "", H]
    for o in ("le modele monte", "Polymarket baisse", "les deux", "deja la (rien n'a bouge en 3 s)", "autre"):
        rap.append(ligne(o, [e for e in base if origine(e) == o]))
    # ---- 8. tendance
    rap += ["", "## 8. Tendance du BTC (perp) avant l'achat — dans le sens du trade ou contre", "", H]
    for k, lab in (("tr15", "15 min"), ("tr60", "60 min")):
        rap.append(ligne(f"tendance {lab} DANS notre sens", [e for e in base if e[k] > 0]))
        rap.append(ligne(f"tendance {lab} CONTRE nous", [e for e in base if e[k] < 0]))
    rap.append(ligne("cote Up (pour comparer)", [e for e in base if e["up"]]))
    rap.append(ligne("cote Down (pour comparer)", [e for e in base if not e["up"]]))
    # ---- 9. bilan des filtres
    F = {"Binance et perp >= 0": lambda e: e["bn"] >= 0 and e["perp"] >= 0, "perp >= 0": lambda e: e["perp"] >= 0,
         "juge >= prix": lambda e: e["pj"] >= e["ask"], "juge >= prix + 5 c": lambda e: e["pj"] >= e["ask"] + 0.05,
         "pas « Polymarket baisse »": lambda e: origine(e) != "Polymarket baisse", "pas « modele monte »": lambda e: origine(e) != "le modele monte",
         "tendance 15 min >= 0": lambda e: e["tr15"] >= 0, "tendance 60 min >= 0": lambda e: e["tr60"] >= 0,
         "elastique Binance et perp >= -0,5": lambda e: e["zbn"] >= -0.5 and e["zperp"] >= -0.5}
    rap += ["", "## 9. Chaque filtre : pertes evitees contre gagnants perdus", "",
            "| Filtre | Trades ecartes | Perdants ecartes | Gagnants ecartes | Pertes evitees | Gains perdus | **Net du filtre** | Net 1re moitie | Net 2e moitie |", "|---|---|---|---|---|---|---|---|---|"]
    J["filtres"] = []
    for nom, f in F.items():
        out = [e for e in base if not f(e)]
        perd = [e for e in out if not e["gm"]]; gagn = [e for e in out if e["gm"]]
        ev, gp = -sum(e["pnl"] for e in perd), sum(e["pnl"] for e in gagn)
        n1 = -sum(e["pnl"] for e in out if e["st"] < mi); n2 = -sum(e["pnl"] for e in out if e["st"] >= mi)
        J["filtres"].append((nom, len(out), len(perd), len(gagn), ev, gp, ev - gp, n1, n2))
        rap.append(f"| {nom} | {len(out)} | {len(perd)} | {len(gagn)} | {ev:+.0f} $ | {gp:+.0f} $ | **{ev - gp:+.0f} $** | {n1:+.0f} $ | {n2:+.0f} $ |")
    open(OUT + "resultat_idees.md", "w").write("\n".join(rap))
    json.dump(J, open(OUT + "idees.json", "w"), ensure_ascii=False, default=str)
    print("\n".join(rap))


if __name__ == "__main__":
    main()
