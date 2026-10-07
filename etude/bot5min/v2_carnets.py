"""Les variantes V2 / V5 / V6 rejouees sur les VRAIS carnets (enregistreur du bot, 48 h) — 07.10.2026.
L'historique 12 jours (prix des echanges) donne +29 $/trade pour le desaccord 20 BTC, mais en direct il a perdu : on juge donc ici,
au meilleur vendeur reel, avec la taille reellement affichee (si le vendeur n'a pas 50 $, on prend ce qu'il y a).
"""
import json, sys, time, statistics, collections
sys.path.insert(0, "etude/bot5min")
from sauvetage import charger, resultat, RES, FEE

OUT = "etude/bot5min/"
# rec : t start pu ub ua db da ubs uas dbs das perp okx cb bn cl strike


def main():
    rap = ["# Variantes V2 / V5 / V6 sur les vrais carnets du bot (48 h)", "",
           "Achat au meilleur vendeur reel, limite a la taille affichee (max 50 $), garde jusqu'au resultat officiel. 1 achat par cycle et par variante.", ""]
    for A in ("BTC", "ETH"):
        C = charger(A); sts = sorted(C)
        for st in sts: resultat(A, st)
        mi = sts[len(sts) // 2]
        P = collections.defaultdict(list)
        for st in sts:
            R = C[st]; g = RES.get((A, st))
            if g is None: continue
            fait = set()
            for i, r in enumerate(R):
                tl = st + 300 - r[0]
                if tl < 5: break
                def back(n):
                    j = i
                    while j > 0 and r[0] - R[j][0] < n: j -= 1
                    return R[j] if r[0] - R[j][0] >= n - 0.5 else None
                h1, h3, h5 = back(1), back(3), back(5)
                for up in (True, False):
                    ask = r[4] if up else r[6]; taille = (r[8] if up else r[10]) or 0
                    fair = r[2] if up else 1 - r[2]; sg = 1 if up else -1
                    if ask is None or not (0.02 <= ask <= 0.97): continue
                    edge = fair - ask
                    E = lambda x: ((x[2] - x[4]) if up else ((1 - x[2]) - x[6])) if x and x[4] is not None and x[6] is not None else None
                    mid = lambda x: ((x[3] + x[4]) / 2 if up else (x[5] + x[6]) / 2) if x else None
                    dsrc = lambda x, c: (r[c] - x[c]) * sg if x and x[c] is not None and r[c] is not None else None
                    parts = min(50 / ask, taille)
                    if parts < 5: continue
                    gm = g if up else (not g)
                    pnl = parts * ((1 if gm else 0) - ask - FEE(ask))
                    perp5 = dsrc(h5, 11)
                    d3 = [dsrc(h3, c) for c in (11, 12, 13, 14)]
                    vetos = [h3 and E(h3) is not None and edge - E(h3) < -0.02, (dsrc(h3, 14) or 0) < 0, (dsrc(h3, 11) or 0) < 0 and (dsrc(h3, 12) or 0) < 0,
                             60 <= tl < 90, h5 and mid(h5) is not None and mid(r) - mid(h5) >= max(0.05, edge / 2), taille < 20]
                    regles = {}
                    if edge >= 0.20:
                        regles.update({
                            "A desaccord 20": True,
                            "B hors 60-89 s": not (60 <= tl < 90),
                            "C perp": perp5 is not None and perp5 >= 0,
                            "D perp + 120-269 s": perp5 is not None and perp5 >= 0 and 120 <= tl <= 269,
                            "E persistant": h1 is not None and E(h1) is not None and E(h1) >= 0.20 and (back(1.5) is not None and E(back(1.5)) is not None and E(back(1.5)) >= 0.20),
                            "F ecart qui grandit": h3 is not None and E(h3) is not None and edge - E(h3) >= 0.03,
                            "G jury": all(v is not None and v >= 0 for v in d3) and any((v or 0) > 0 for v in d3) and h3 is not None and mid(h3) is not None and (fair - (h3[2] if up else 1 - h3[2])) - (mid(r) - mid(h3)) >= 0.03,
                            "H veto complet": not any(vetos),
                            "C+F perp + grandit": perp5 is not None and perp5 >= 0 and h3 is not None and E(h3) is not None and edge - E(h3) >= 0.03})
                    regles["V5 gain attendu >= 50 %"] = fair / ask - 1 >= 0.5 and edge >= 0.05
                    regles["V6 loterie"] = ask <= 0.10 and fair >= 2 * ask
                    for nom, ok in regles.items():
                        if ok and nom not in fait:
                            fait.add(nom); P[nom].append((st, pnl, gm, ask))
        rap += [f"## {A} — {len(sts)} cycles ({time.strftime('%d.%m %H:%M', time.gmtime(sts[0] + 7200))} → {time.strftime('%d.%m %H:%M', time.gmtime(sts[-1] + 7500))})", "",
                "| Variante | Trades | Gagnes | 1re moitie | 2e moitie | **Total** | Gain moyen / trade |", "|---|---|---|---|---|---|---|"]
        for nom, L in P.items():
            a_ = sum(p for s, p, g, k in L if s < mi); b_ = sum(p for s, p, g, k in L if s >= mi)
            rap.append(f"| {nom} | {len(L)} | {sum(1 for x in L if x[2])} | {a_:+.0f} $ | {b_:+.0f} $ | **{a_ + b_:+.0f} $** | {(a_ + b_) / len(L):+.2f} $ |")
        rap.append("")
        open(OUT + "resultat_v2_carnets.md", "w").write("\n".join(rap))
    print("\n".join(rap))


if __name__ == "__main__":
    main()
