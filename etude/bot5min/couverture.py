"""Idee 6 (ChatGPT, 08.10.2026) : au moment de la sortie -10, acheter le cote inverse (paire Up + Down = 1 $ a la fin) au lieu de revendre.
Strategie : zone + Binance et perp + sortie modele -10. Vrais carnets du bot (48 h, 4 mesures/s), BTC.
Couverture : on achete autant de jetons inverses que de jetons detenus au meilleur vendeur d'en face, si la paire coute <= seuil frais compris
et si ce vendeur a au moins la moitie des jetons voulus ; sinon on fait la sortie de repli.
"""
import sys, time
sys.path.insert(0, "etude/bot5min")
import zone as Z
from sauvetage import resultat, RES, FEE
from proche import charger_brut

OUT = "etude/bot5min/"


def sim(ev, pt, seuil_paire=None, repli="vendre"):
    up = ev["up"]; R = ev["R"]; p = pt["ask"]; parts = 50 / p
    garde = parts * ((1 if ev["gm"] else 0) - p - FEE(p))
    for x in R[pt["i"] + 1:]:
        tl = ev["st"] + 300 - x[0]
        if tl < 2: break
        fair = x[2] if up else 1 - x[2]
        if fair > pt["fair"] - 0.10: continue
        bid = x[3] if up else x[5]; bz = (x[7] if up else x[9]) or 0
        oa = x[6] if up else x[4]; oz = (x[10] if up else x[8]) or 0
        if seuil_paire is not None and oa is not None and p + oa + FEE(p) + FEE(oa) <= seuil_paire and oz >= parts / 2:
            return parts * (1 - p - oa - FEE(p) - FEE(oa)), "couvert"
        if repli == "vendre" and bid is not None and bid >= 0.05:
            bx = bid if bz >= parts / 2 else bid - 0.01
            return parts * (bx - FEE(bx)) - parts * (p + FEE(p)), "vendu"
        if repli == "garder": return garde, "garde"
    return garde, "fin"


def main():
    A = "BTC"
    C = charger_brut(A); sts = sorted(C)
    for st in sts: resultat(A, st)
    EV = Z.points(A, C)
    q = [sts[int(len(sts) * k / 4)] for k in (1, 2, 3)]
    quart = lambda st: sum(st >= x for x in q)
    T = sorted(Z.trades(EV, Z.BASES["ecart >= 0,30 · 0,15-0,35 · > 60 s"], [Z.FILTRES["Binance >= 0"], Z.FILTRES["perp >= 0"]]), key=lambda z: z[1]["t"])
    V = {"revendre (actuel)": (None, "vendre"), "garder (jamais rien)": (None, "garder"),
         "couvrir si paire <= 1,00, sinon revendre": (1.00, "vendre"), "couvrir si paire <= 0,98, sinon revendre": (0.98, "vendre"),
         "couvrir si paire <= 0,95, sinon revendre": (0.95, "vendre"), "couvrir si paire <= 1,00, sinon garder": (1.00, "garder"),
         "couvrir si paire <= 0,98, sinon garder": (0.98, "garder")}
    rap = [f"# Couvrir avec le cote inverse au lieu de revendre (sortie -10) — BTC, vrais carnets ({time.strftime('%d.%m %H:%M', time.gmtime(sts[0] + 7200))} -> {time.strftime('%d.%m %H:%M', time.gmtime(sts[-1] + 7500))})", "",
           f"{len(T)} trades « zone + Binance et perp ». Couverture = acheter autant de jetons inverses, garder les deux jusqu'a la fin (la paire vaut 1 $).", "",
           "| Gestion au moment du -10 | Couverts | Revendus | Perdants | Q1 | Q2 | Q3 | Q4 | **Total** | Sans top 3 | Creux |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for nom, (sp, rp) in V.items():
        res = [(ev, sim(ev, pt, sp, rp)) for ev, pt in T]
        pn = [r[0] for _, r in res]; P = sorted(pn, reverse=True)
        cum = pk = cr = 0.0
        for x in pn: cum += x; pk = max(pk, cum); cr = min(cr, cum - pk)
        Q = [sum(r[0] for ev, r in res if quart(ev["st"]) == k) for k in range(4)]
        rap.append(f"| {nom} | {sum(1 for _, r in res if r[1] == 'couvert')} | {sum(1 for _, r in res if r[1] == 'vendu')} | {sum(1 for x in pn if x < 0)} | " +
                   " | ".join(f"{x:+.0f}" for x in Q) + f" | **{sum(pn):+.0f} $** | {sum(P[3:]):+.0f} $ | {cr:+.0f} $ |")
    # combien de fois une couverture etait-elle possible au moment du -10, et a quel prix de paire
    paires = []
    for ev, pt in T:
        up = ev["up"]
        for x in ev["R"][pt["i"] + 1:]:
            if ev["st"] + 300 - x[0] < 2: break
            if (x[2] if up else 1 - x[2]) <= pt["fair"] - 0.10:
                oa = x[6] if up else x[4]
                if oa is not None: paires.append(pt["ask"] + oa + FEE(pt["ask"]) + FEE(oa))
                break
    if paires:
        paires.sort()
        rap += ["", f"Au moment du -10 ({len(paires)} cas) : prix de la paire (notre achat + cote inverse, frais compris) — minimum {paires[0]:.2f}, mediane {paires[len(paires) // 2]:.2f}, maximum {paires[-1]:.2f} ; "
                f"<= 1,00 dans {sum(1 for x in paires if x <= 1.0)} cas, <= 0,98 dans {sum(1 for x in paires if x <= 0.98)} cas."]
    open(OUT + "resultat_couverture.md", "w").write("\n".join(rap))
    print("\n".join(rap))


if __name__ == "__main__":
    main()
