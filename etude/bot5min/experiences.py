"""Experiences proposees par ChatGPT (08.10.2026) sur « zone + Binance et perp + sortie modele -10 » — vrais carnets du bot (48 h, 4 mesures/s), BTC.
1/8 sorties intelligentes (sauvetage des faux perdants, sortie selon la valeur attendue) · 3 confirmation 1-2 s · 5 situations irrecuperables
6 contradictions multi-bourses · 7 taille adaptative (25 $ / 50 $).
Mesures : trades, perdants, gagnants sacrifies, resultat, sans top 3, creux, plus longue serie de pertes, gains perdus par sorties prematurees,
resultat par quart, et rendement par dollar engage (pour la taille adaptative).
"""
import sys, json, itertools, time
sys.path.insert(0, "etude/bot5min")
import zone as Z
from sauvetage import resultat, RES, FEE
from proche import charger_brut

OUT = "etude/bot5min/"


def sim(ev, pt, regle, mise=50.0, retard=0):
    """achat (eventuellement retard lignes plus tard si l'ecart tient), sortie selon regle(etat) ; renvoie (pnl, sortie, pnl_si_garde, mise)"""
    up = ev["up"]; R = ev["R"]; i = pt["i"]; p = pt["ask"]
    if retard:
        if i + retard >= len(R): return None
        x = R[i + retard]; a2 = x[4] if up else x[6]; f2 = x[2] if up else 1 - x[2]
        if a2 is None or not (0.15 <= a2 < 0.37) or f2 - a2 < 0.28: return None
        i, p = i + retard, a2
    parts = mise / p; garde = parts * ((1 if ev["gm"] else 0) - p - FEE(p))
    for x in R[i + 1:]:
        tl = ev["st"] + 300 - x[0]
        if tl < 2: break
        bid = x[3] if up else x[5]; bz = (x[7] if up else x[9]) or 0; fair = x[2] if up else 1 - x[2]
        mid = ((x[3] + x[4]) / 2 if up else (x[5] + x[6]) / 2) if None not in (x[3], x[4], x[5], x[6]) else None
        if bid is None: continue
        e = {"tl": tl, "bid": bid, "fair": fair, "f0": pt["fair"], "p": p, "mid": mid}
        if regle(e):
            if bid < 0.05: continue                                          # plancher (correction du 08.10)
            bx = bid if bz >= parts / 2 else bid - 0.01
            return parts * (bx - FEE(bx)) - parts * (p + FEE(p)), "vendu", garde, mise
    return garde, "fin", garde, mise


SORTIES = {
    "revente si modele -10 (actuel)": lambda e: e["fair"] <= e["f0"] - 0.10,
    "garder toujours": lambda e: False,
    "sauvetage : -10 seulement si le modele est tombe sous 0,25": lambda e: e["fair"] <= e["f0"] - 0.10 and e["fair"] < 0.25,
    "sauvetage : -10 seulement si modele < 0,30 et < 120 s": lambda e: e["fair"] <= e["f0"] - 0.10 and e["fair"] < 0.30 and e["tl"] < 120,
    "valeur : vendre si acheteur >= modele (vente > garde attendue)": lambda e: e["bid"] >= e["fair"],
    "valeur corrigee : vendre si acheteur >= 0,7 x modele": lambda e: e["bid"] >= 0.7 * e["fair"],
    "valeur Polymarket : -10 ET acheteur >= milieu - 1 c": lambda e: e["fair"] <= e["f0"] - 0.10 and e["mid"] is not None and e["bid"] >= e["mid"] - 0.01,
}


def serie_max(pn):
    m = c = 0
    for p in pn:
        c = c + 1 if p < 0 else 0; m = max(m, c)
    return m


def main():
    A = "BTC"
    C = charger_brut(A); sts = sorted(C)
    for st in sts: resultat(A, st)
    EV = Z.points(A, C)
    q = [sts[int(len(sts) * k / 4)] for k in (1, 2, 3)]
    quart = lambda st: sum(st >= x for x in q)
    base = Z.BASES["ecart >= 0,30 · 0,15-0,35 · > 60 s"]
    bp = [Z.FILTRES["Binance >= 0"], Z.FILTRES["perp >= 0"]]
    T0 = sorted(Z.trades(EV, base, bp), key=lambda z: z[1]["t"])
    pasbaisse = lambda p, ev: not ((p["dfair3"] - p["v3"]) <= -0.03 and p["dfair3"] < 0.03)
    J = {}; rap = [f"# Experiences ChatGPT — zone + Binance et perp + sortie -10 — BTC, vrais carnets ({time.strftime('%d.%m %H:%M', time.gmtime(sts[0] + 7200))} -> {time.strftime('%d.%m %H:%M', time.gmtime(sts[-1] + 7500))})", "",
                   "Toutes les reventes avec plancher 0,05 $. « Gagnants sacrifies » = trades de la reference gagnants a la fin qui ne le sont plus (non achetes ou revendus).", ""]
    H = "| Regle | Trades | Perdants | Gagnants sacrifies | Q1 | Q2 | Q3 | Q4 | **Total** | Sans top 3 | Creux | Serie de pertes max | Gains perdus par reventes | Rendement / $ engage |\n|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"

    def mesure(nom, R_):
        R_ = [(ev, pt, r) for ev, pt, r in R_ if r is not None]
        pn = [r[0] for _, _, r in R_]; P = sorted(pn, reverse=True)
        cum = pk = cr = 0.0
        for p in pn: cum += p; pk = max(pk, cum); cr = min(cr, cum - pk)
        Q = [sum(r[0] for ev, pt, r in R_ if quart(ev["st"]) == k) for k in range(4)]
        gagn_ref = {(ev["st"], ev["up"]) for ev, pt in T0 if ev["gm"]}
        gagn_ici = {(ev["st"], ev["up"]) for ev, pt, r in R_ if ev["gm"] and r[1] == "fin"}
        perdu_rev = sum(r[2] - r[0] for ev, pt, r in R_ if r[1] == "vendu" and ev["gm"])
        mises = sum(r[3] for _, _, r in R_)
        s = {"nom": nom, "n": len(R_), "perdants": sum(1 for p in pn if p < 0), "sacrifies": len(gagn_ref - gagn_ici), "q": Q, "tot": sum(pn), "sans3": sum(P[3:]),
             "creux": cr, "serie": serie_max(pn), "perdu_rev": perdu_rev, "rdt": sum(pn) / max(1, mises)}
        return s
    ligne = lambda s: (f"| {s['nom']} | {s['n']} | {s['perdants']} | {s['sacrifies']} | " + " | ".join(f"{x:+.0f}" for x in s["q"]) +
                       f" | **{s['tot']:+.0f} $** | {s['sans3']:+.0f} $ | {s['creux']:+.0f} $ | {s['serie']} | {s['perdu_rev']:+.0f} $ | {100 * s['rdt']:+.1f} % |")
    blocs = []
    # 1/8 sorties
    L = [mesure(sn, [(ev, pt, sim(ev, pt, rg)) for ev, pt in T0]) for sn, rg in SORTIES.items()]
    blocs.append(("1 et 8. Sorties intelligentes (memes entrees)", L))
    act = SORTIES["revente si modele -10 (actuel)"]
    # 2 rappel + 3 confirmation
    T1 = sorted(Z.trades(EV, base, bp + [pasbaisse]), key=lambda z: z[1]["t"])
    L = [mesure("reference (achat immediat)", [(ev, pt, sim(ev, pt, act)) for ev, pt in T0]),
         mesure("pas « Polymarket qui baisse » (fantome lance)", [(ev, pt, sim(ev, pt, act)) for ev, pt in T1])]
    for k, lab in ((2, "0,5 s"), (4, "1 s"), (8, "2 s")):
        L.append(mesure(f"confirmation : acheter {lab} plus tard si l'ecart tient encore", [(ev, pt, sim(ev, pt, act, retard=k)) for ev, pt in T0]))
    blocs.append(("2 et 3. Faux desaccords et confirmation", L))
    # 5 irrecuperables (a l'entree)
    L = [mesure("reference", [(ev, pt, sim(ev, pt, act)) for ev, pt in T0])]
    for nom, f in (("modele >= 0,45", lambda p, ev: p["fair"] >= 0.45), ("modele >= 0,50", lambda p, ev: p["fair"] >= 0.50),
                   ("pas (prix < 0,18 et < 90 s)", lambda p, ev: not (p["ask"] < 0.18 and p["tl"] < 90)), ("pas (modele < 0,48 et < 120 s)", lambda p, ev: not (p["fair"] < 0.48 and p["tl"] < 120))):
        L.append(mesure(nom, [(ev, pt, sim(ev, pt, act)) for ev, pt in sorted(Z.trades(EV, base, bp + [f]), key=lambda z: z[1]["t"])]))
    blocs.append(("5. Situations presque irrecuperables (a l'entree)", L))
    # 6 contradictions
    L = [mesure("reference", [(ev, pt, sim(ev, pt, act)) for ev, pt in T0])]
    for nom, f in (("OKX pas contre", lambda p, ev: p["okx"] >= 0), ("Coinbase pas contre", lambda p, ev: p["cb"] >= 0), ("Chainlink pas contre", lambda p, ev: p["cl"] >= 0),
                   ("au plus 1 contre parmi OKX/Coinbase/Chainlink", lambda p, ev: sum(x < 0 for x in (p["okx"], p["cb"], p["cl"])) <= 1),
                   ("pas les 3 contre (OKX, Coinbase, Chainlink)", lambda p, ev: not all(x < 0 for x in (p["okx"], p["cb"], p["cl"])))):
        L.append(mesure(nom, [(ev, pt, sim(ev, pt, act)) for ev, pt in sorted(Z.trades(EV, base, bp + [f]), key=lambda z: z[1]["t"])]))
    blocs.append(("6. Contradictions multi-bourses", L))
    # 7 taille adaptative
    L = [mesure("reference : 50 $ partout", [(ev, pt, sim(ev, pt, act)) for ev, pt in T0])]
    douteux = {"Polymarket qui baisse": lambda p, ev: not pasbaisse(p, ev), "le modele n'a pas monte": lambda p, ev: p["dfair3"] < 0.03,
               "prix < 0,18": lambda p, ev: p["ask"] < 0.18, "nuit": lambda p, ev: ev["hz"] < 8, "OKX ou Coinbase contre": lambda p, ev: p["okx"] < 0 or p["cb"] < 0,
               "moins de 90 s": lambda p, ev: p["tl"] < 90}
    for k in (1, 2):
        for combo in itertools.combinations(douteux, k):
            for petite in (25.0, 15.0):
                L.append(mesure(f"{int(petite)} $ si " + " ou ".join(combo) + ", 50 $ sinon",
                                [(ev, pt, sim(ev, pt, act, mise=petite if any(douteux[c](pt, ev) for c in combo) else 50.0)) for ev, pt in T0]))
    blocs.append(("7. Taille adaptative (memes trades, mise reduite sur les douteux)", L))
    for titre, L in blocs:
        rap += [f"## {titre}", "", H] + [ligne(s) for s in L] + [""]
    J["blocs"] = [(t, L) for t, L in blocs]
    open(OUT + "resultat_experiences.md", "w").write("\n".join(rap))
    json.dump(J, open(OUT + "experiences.json", "w"), ensure_ascii=False, default=str)
    print("\n".join(rap))


if __name__ == "__main__":
    main()
