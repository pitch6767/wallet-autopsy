"""QUI CONVERGE VERS QUI (WHO BLINKS FIRST) — vrais carnets du bot, 48 h, ~1 mesure/s (07.10.2026).
A chaque premier desaccord >= 0,20 du cycle et du cote (modele - meilleur vendeur), on regarde 1, 3 et 10 s plus tard :
  - POLY REJOINT    : le milieu Polymarket monte de >= 3 c vers le modele, le modele ne retombe pas de >= 3 c
  - MODELE RETOMBE  : le modele baisse de >= 3 c, Polymarket ne monte pas de >= 3 c
  - LES DEUX        : les deux se rapprochent
  - RIEN            : aucun ne bouge de 3 c
Puis : resultat de chaque famille (achat a l'entree, garde jusqu'a la fin, 50 $),
       strategie causale « attendre h s, acheter seulement si POLY REJOINT » (au meilleur vendeur a t+h),
       peut-on PREVOIR la famille a l'entree (bourses dans les 3 s avant) ? LightGBM 1re moitie -> 2e moitie,
       et tests en retirant une source a la fois (Binance, Bybit perp, OKX, Coinbase, Chainlink, carnet Poly).
"""
import sys, statistics, collections
import numpy as np
sys.path.insert(0, "etude/bot5min")
from sauvetage import charger, resultat, RES, FEE

OUT = "etude/bot5min/"
E = 0.20; S = 0.03
FAM = ["POLY REJOINT", "MODELE RETOMBE", "LES DEUX", "RIEN"]


def famille(df, dm):
    p, m = dm >= S, df <= -S
    return "LES DEUX" if p and m else "POLY REJOINT" if p else "MODELE RETOMBE" if m else "RIEN"


def evenements(A, C):
    out = []
    for st in sorted(C):
        R = C[st]; g = RES.get((A, st))
        if g is None: continue
        for up in (True, False):
            for i, r in enumerate(R):
                tl = st + 300 - r[0]
                if tl < 12: break
                ask = r[4] if up else r[6]; bid = r[3] if up else r[5]
                fair = r[2] if up else 1 - r[2]
                if ask is None or bid is None or not (0.03 <= ask <= 0.97) or fair - ask < E: continue
                sg = 1 if up else -1
                mid = lambda x: (x[3] + x[4]) / 2 if up else (x[5] + x[6]) / 2
                fr = lambda x: x[2] if up else 1 - x[2]
                def at(dt, sens=1):
                    j = i
                    if sens > 0:
                        while j < len(R) - 1 and R[j][0] - r[0] < dt: j += 1
                        return R[j] if R[j][0] - r[0] >= dt - 0.6 and R[j][0] - r[0] <= dt + 2 else None
                    while j > 0 and r[0] - R[j][0] < dt: j -= 1
                    return R[j] if r[0] - R[j][0] >= dt - 0.6 else None
                gm = g if up else (not g)
                pnl = lambda p: (50 / p) * ((1 if gm else 0) - p - FEE(p))
                e = {"st": st, "tl": tl, "ask": ask, "edge": fair - ask, "gagne": gm, "pnl": pnl(ask),
                     "taille": (r[8] if up else r[10]) or 0, "spread": ask - bid}
                for h in (1, 3, 10):
                    x = at(h)
                    if x is None: e[f"f{h}"] = None; continue
                    e[f"f{h}"] = famille(fr(x) - fair, mid(x) - mid(r))
                    a2 = x[4] if up else x[6]
                    e[f"pnl_att{h}"] = pnl(a2) if a2 and 0.03 <= a2 <= 0.97 else None
                h3, h5 = at(3, -1), at(5, -1)
                d = lambda x, c: ((r[c] - x[c]) / x[c] * 1e4 * sg) if x and x[c] and r[c] else 0.0
                e.update({"bn3": d(h3, 14), "perp3": d(h3, 11), "okx3": d(h3, 12), "cb3": d(h3, 13), "cl3": d(h3, 15),
                          "bn5": d(h5, 14), "perp5": d(h5, 11), "okx5": d(h5, 12), "cb5": d(h5, 13), "cl5": d(h5, 15),
                          "mkt3": (mid(r) - mid(h3)) if h3 else 0.0, "mkt5": (mid(r) - mid(h5)) if h5 else 0.0,
                          "v3": (fair - ask) - ((fr(h3) - (h3[4] if up else h3[6])) if h3 and (h3[4] if up else h3[6]) is not None else fair - ask),
                          "dfair3": (fair - fr(h3)) if h3 else 0.0})
                out.append(e)
                break
    return out


GROUPES = {"Binance": ["bn3", "bn5"], "Bybit perp": ["perp3", "perp5"], "OKX": ["okx3", "okx5"], "Coinbase": ["cb3", "cb5"],
           "Chainlink": ["cl3", "cl5"], "carnet Poly": ["mkt3", "mkt5", "taille", "spread"]}
BASE = ["tl", "ask", "edge", "v3", "dfair3"]


def auc(y, p):
    from sklearn.metrics import roc_auc_score
    try: return roc_auc_score(y, p)
    except Exception: return float("nan")


def main():
    import lightgbm as lgb
    rap = ["# Qui converge vers qui ? — desaccords >= 0,20, vrais carnets du bot (48 h)", "",
           "Familles a +1 / +3 / +10 s : POLY REJOINT = Polymarket monte de >= 3 c vers le modele (modele stable) ; MODELE RETOMBE = le modele baisse de >= 3 c (Poly stable) ; LES DEUX ; RIEN.",
           "Resultat : achat 50 $ au meilleur vendeur a l'entree, garde jusqu'a la fin, frais compris.", ""]
    for A in ("BTC", "ETH"):
        C = charger(A); sts = sorted(C)
        for st in sts: resultat(A, st)
        EV = evenements(A, C)
        if len(EV) < 40: rap += [f"## {A} — trop peu de desaccords ({len(EV)})", ""]; continue
        mi = sts[len(sts) // 2]
        rap += [f"## {A} — {len(EV)} desaccords >= 0,20", ""]
        for h in (1, 3, 10):
            X = [e for e in EV if e.get(f"f{h}")]
            rap += [f"### Apres {h} s", "", "| Famille | Desaccords | Part | Gagnes a la fin | Resultat (achat a l'entree) | Gain / trade | « Attendre et acheter seulement si POLY REJOINT » |", "|---|---|---|---|---|---|---|"]
            for f in FAM:
                Y = [e for e in X if e[f"f{h}"] == f]
                if not Y: rap.append(f"| {f} | 0 | — | — | — | — | — |"); continue
                att = ""
                if f == "POLY REJOINT":
                    Z = [e[f"pnl_att{h}"] for e in Y if e.get(f"pnl_att{h}") is not None]
                    za = [e[f"pnl_att{h}"] for e in Y if e.get(f"pnl_att{h}") is not None and e["st"] < mi]
                    zb = [e[f"pnl_att{h}"] for e in Y if e.get(f"pnl_att{h}") is not None and e["st"] >= mi]
                    att = f"{len(Z)} trades · {sum(Z):+.0f} $ (1re moitie {sum(za):+.0f} / 2e {sum(zb):+.0f})" if Z else "—"
                rap.append(f"| {f} | {len(Y)} | {100 * len(Y) / len(X):.0f} % | {100 * statistics.mean(1 if e['gagne'] else 0 for e in Y):.0f} % | {sum(e['pnl'] for e in Y):+.0f} $ | {statistics.mean(e['pnl'] for e in Y):+.1f} $ | {att} |")
            rap.append(f"| **tous** | {len(X)} | 100 % | {100 * statistics.mean(1 if e['gagne'] else 0 for e in X):.0f} % | **{sum(e['pnl'] for e in X):+.0f} $** | {statistics.mean(e['pnl'] for e in X):+.1f} $ | |")
            rap.append("")
        # famille a 3 s selon la direction de chaque bourse dans les 3 s avant
        X = [e for e in EV if e.get("f3")]
        rap += ["### Ce qui annonce la famille a 3 s (bourses dans les 3 s AVANT l'entree)", "", "| Signal | Sens | Desaccords | POLY REJOINT | MODELE RETOMBE | Resultat |", "|---|---|---|---|---|---|"]
        for nom, k in (("Binance", "bn3"), ("Bybit perp", "perp3"), ("OKX", "okx3"), ("Coinbase", "cb3"), ("Chainlink", "cl3"), ("Polymarket", "mkt3")):
            for sens, fl in (("contre nous", lambda v: v < 0), ("neutre", lambda v: v == 0), ("avec nous", lambda v: v > 0)):
                Y = [e for e in X if fl(e[k])]
                if len(Y) < 5: continue
                rap.append(f"| {nom} | {sens} | {len(Y)} | {100 * statistics.mean(1 if e['f3'] == 'POLY REJOINT' else 0 for e in Y):.0f} % | {100 * statistics.mean(1 if e['f3'] == 'MODELE RETOMBE' else 0 for e in Y):.0f} % | {sum(e['pnl'] for e in Y):+.0f} $ |")
        # prevision + ablations
        a_ = [e for e in X if e["st"] < mi]; b_ = [e for e in X if e["st"] >= mi]
        rap.append("")
        if len(a_) >= 40 and len(b_) >= 25:
            par = dict(n_estimators=200, learning_rate=0.03, num_leaves=7, min_child_samples=15, verbose=-1)
            rap += ["### Peut-on prevoir a l'entree ? (appris 1re moitie, juge 2e moitie — AUC : 0,50 = hasard, 1 = parfait)", "",
                    "| Variables | AUC « POLY REJOINT » a 3 s | AUC « MODELE RETOMBE » a 3 s | AUC gagnant a la fin |", "|---|---|---|---|"]
            tous = BASE + [c for g in GROUPES.values() for c in g]
            for lab, F in [("toutes les sources", tous)] + [(f"sans {g}", [c for c in tous if c not in cs]) for g, cs in GROUPES.items()] + [("seulement temps/prix/ecart", BASE)]:
                Xa = np.array([[e[c] for c in F] for e in a_], float); Xb = np.array([[e[c] for c in F] for e in b_], float)
                res = []
                for y in (lambda e: e["f3"] == "POLY REJOINT", lambda e: e["f3"] == "MODELE RETOMBE", lambda e: e["gagne"]):
                    ya = [y(e) for e in a_]; yb = [y(e) for e in b_]
                    if len(set(ya)) < 2: res.append("—"); continue
                    m = lgb.LGBMClassifier(**par).fit(Xa, ya)
                    res.append(f"{auc(yb, m.predict_proba(Xb)[:, 1]):.2f}")
                rap.append(f"| {lab} | " + " | ".join(res) + " |")
            rap.append("")
        else:
            rap += [f"Prevision : pas assez de desaccords ({len(a_)} / {len(b_)}).", ""]
        open(OUT + "resultat_blink.md", "w").write("\n".join(rap))
    print("\n".join(rap))


if __name__ == "__main__":
    main()
