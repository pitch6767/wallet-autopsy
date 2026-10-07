"""Modele de MOUVEMENT et « mort a l'arrivee » — vrais carnets du bot (48 h, 1 mesure/s), 07.10.2026.
Pour chaque desaccord (modele - meilleur vendeur >= 0,10, premier achetable du cycle et du cote) :
  - MOUVEMENT = le meilleur acheteur atteint >= 1,5 x le prix paye ET >= prix + 5 c avant la fin (on aurait pu revendre +50 %)
  - MORT A L'ARRIVEE = le meilleur acheteur ne depasse jamais le prix paye + 1 c
Variables connues a l'achat : temps restant, prix, modele, ecart, vitesse de l'ecart, perp / OKX / Binance / Coinbase sur 3 et 5 s,
mouvement du marche sur 5 s, taille au vendeur, ecart achat/vente. Appris sur la 1re moitie, juge sur la 2e.
Routeur teste : garder jusqu'a la fin si P(gain final) haute ; revendre a +50 % si seulement P(mouvement) haute ; sinon rien.
"""
import json, sys, time, statistics, collections
import numpy as np
sys.path.insert(0, "etude/bot5min")
from sauvetage import charger, resultat, RES, FEE

OUT = "etude/bot5min/"


def evenements(A, C, E=0.10):
    out = []
    for st in sorted(C):
        R = C[st]; g = RES.get((A, st))
        if g is None: continue
        for up in (True, False):
            for i, r in enumerate(R):
                tl = st + 300 - r[0]
                if tl < 10: break
                ask = r[4] if up else r[6]; bid = r[3] if up else r[5]; taille = (r[8] if up else r[10]) or 0
                fair = r[2] if up else 1 - r[2]
                if ask is None or bid is None or not (0.03 <= ask <= 0.90) or fair - ask < E: continue
                sg = 1 if up else -1
                def back(n):
                    j = i
                    while j > 0 and r[0] - R[j][0] < n: j -= 1
                    return R[j] if r[0] - R[j][0] >= n - 0.5 else None
                h3, h5 = back(3), back(5)
                d = lambda x, c: ((r[c] - x[c]) / x[c] * 1e4 * sg) if x and x[c] and r[c] else 0.0
                ed = lambda x: ((x[2] - x[4]) if up else ((1 - x[2]) - x[6])) if x and x[4] is not None and x[6] is not None else None
                mid = lambda x: ((x[3] + x[4]) / 2 if up else (x[5] + x[6]) / 2) if x and None not in (x[3], x[4], x[5], x[6]) else None
                bids = [(R[j][3] if up else R[j][5]) for j in range(i + 1, len(R))]
                bids = [b for b in bids if b is not None]
                if not bids: break
                mx = max(bids)
                gm = g if up else (not g)
                parts = 50 / ask
                # sortie a +50 % : premier instant ou le meilleur acheteur >= cible
                cible = max(1.5 * ask, ask + 0.05)
                vente = next((b for b in bids if b >= cible), None)
                pnl_tenir = parts * ((1 if gm else 0) - ask - FEE(ask))
                pnl_mvt = parts * ((vente - FEE(vente)) if vente else (1 if gm else 0)) - parts * (ask + FEE(ask))
                out.append({"st": st, "tl": tl, "ask": ask, "fair": fair, "edge": fair - ask, "taille": taille, "spread": ask - bid,
                            "v3": (fair - ask) - (ed(h3) if ed(h3) is not None else fair - ask), "perp3": d(h3, 11), "perp5": d(h5, 11), "okx3": d(h3, 12),
                            "cb3": d(h3, 13), "bn3": d(h3, 14), "mkt5": (mid(r) - mid(h5)) if mid(h5) is not None and mid(r) is not None else 0.0,
                            "mouvement": vente is not None, "mort": mx <= ask + 0.01, "gagne": gm, "pnl_tenir": pnl_tenir, "pnl_mvt": pnl_mvt})
                break
    return out


def main():
    rap = ["# Modele de mouvement / mort a l'arrivee — vrais carnets du bot", ""]
    import lightgbm as lgb
    F = ["tl", "ask", "fair", "edge", "taille", "spread", "v3", "perp3", "perp5", "okx3", "cb3", "bn3", "mkt5"]
    for A in ("BTC", "ETH"):
        C = charger(A); sts = sorted(C)
        for st in sts: resultat(A, st)
        E = evenements(A, C); mi = sts[len(sts) // 2]
        a_ = [e for e in E if e["st"] < mi]; b_ = [e for e in E if e["st"] >= mi]
        if len(a_) < 50 or len(b_) < 30: continue
        tot = lambda X, k: f"{sum(x[k] for x in X):+.0f} $ ({len(X)})"
        rap += [f"## {A} — {len(E)} desaccords (ecart >= 0,10)", "",
                f"- Mouvement +50 % atteint : **{100 * statistics.mean(1 if e['mouvement'] else 0 for e in E):.0f} %** · gagnant a la fin : {100 * statistics.mean(1 if e['gagne'] else 0 for e in E):.0f} % · **mort a l'arrivee : {100 * statistics.mean(1 if e['mort'] else 0 for e in E):.0f} %**",
                f"- Tous, garder jusqu'a la fin : 1re moitie {tot(a_, 'pnl_tenir')} · 2e moitie {tot(b_, 'pnl_tenir')}",
                f"- Tous, revendre a +50 % (sinon garder) : 1re moitie {tot(a_, 'pnl_mvt')} · 2e moitie {tot(b_, 'pnl_mvt')}", ""]
        # ce qui annonce un mort a l'arrivee (1 variable a la fois, sur tout)
        rap += ["Taux de « mort a l'arrivee » selon chaque variable (tiers bas / milieu / haut) :", ""]
        for f in F:
            v = np.array([e[f] for e in E], dtype=float); q1, q2 = np.nanpercentile(v, [33, 67])
            grp = [[e for e in E if e[f] <= q1], [e for e in E if q1 < e[f] <= q2], [e for e in E if e[f] > q2]]
            rap.append(f"- {f} : " + " · ".join(f"{100 * statistics.mean(1 if e['mort'] else 0 for e in g):.0f} %" if g else "—" for g in grp) + f"  (seuils {q1:.3g} / {q2:.3g})")
        Xa = np.array([[e[f] for f in F] for e in a_], dtype=float); Xb = np.array([[e[f] for f in F] for e in b_], dtype=float)
        par = dict(n_estimators=200, learning_rate=0.03, num_leaves=7, min_child_samples=25, verbose=-1)
        mm = lgb.LGBMClassifier(**par).fit(Xa, [e["mouvement"] for e in a_])
        mg = lgb.LGBMClassifier(**par).fit(Xa, [e["gagne"] for e in a_])
        md = lgb.LGBMClassifier(**par).fit(Xa, [e["mort"] for e in a_])
        pm_, pg_, pd_ = mm.predict_proba(Xb)[:, 1], mg.predict_proba(Xb)[:, 1], md.predict_proba(Xb)[:, 1]
        rap += ["", "### 2e moitie (jamais vue) — routeur", "", "| Regle | Trades | Resultat |", "|---|---|---|"]
        rap.append(f"| tout acheter, garder | {len(b_)} | {sum(e['pnl_tenir'] for e in b_):+.0f} $ |")
        for sd in (0.5, 0.6, 0.7):
            keep = [e for e, p in zip(b_, pd_) if p < sd]
            rap.append(f"| ecarter si P(mort) >= {sd} , garder | {len(keep)} | {sum(e['pnl_tenir'] for e in keep):+.0f} $ |")
        for sg_, sm_ in ((0.35, 0.5), (0.4, 0.55), (0.3, 0.6)):
            res = 0.0; n = 0
            for e, pg, pmv in zip(b_, pg_, pm_):
                if pg * 1.0 > e["ask"] + 0.05 and pg >= sg_: res += e["pnl_tenir"]; n += 1          # gain final attendu > prix : on garde
                elif pmv >= sm_: res += e["pnl_mvt"]; n += 1                                          # seulement mouvement : revente +50 %
            rap.append(f"| routeur (garder si P(gain) >= {sg_} et > prix ; sinon revendre +50 % si P(mvt) >= {sm_}) | {n} | {res:+.0f} $ |")
        imp = sorted(zip(F, md.feature_importances_), key=lambda z: -z[1])
        rap += ["", "Variables les plus utilisees pour reconnaitre un « mort a l'arrivee » : " + " · ".join(f"{n} {v}" for n, v in imp[:8]), ""]
        open(OUT + "resultat_mouvement.md", "w").write("\n".join(rap))
    print("\n".join(rap))


if __name__ == "__main__":
    main()
