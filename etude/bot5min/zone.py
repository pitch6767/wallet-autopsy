"""ZONE (desaccord >= 30 pts, jeton 0,15-0,35, > 60 s) — 08.10.2026, vrais carnets du bot (48 h, 4 mesures/s).
1. Liste complete des trades (zone, et zone + Binance et perp >= 0).
2. Reduire les pertes : sorties (stop sous l'entree, modele qui baisse, plus d'ecart, sortie a T s si perdant), verrou de la paire.
3. Combinaisons plus profondes : 8 zones de base x (aucun / 1 / 2 filtres parmi 22), robustes = 4 quarts positifs + sans top 3 positif.
Sorties : resultat_zone.md + zone.json (pour le PDF).
"""
import sys, json, itertools, statistics, time
sys.path.insert(0, "etude/bot5min")
from sauvetage import resultat, RES, FEE
from proche import charger_brut

OUT = "etude/bot5min/"


def points(A, C):
    """tous les instants achetables (ecart >= 0,10) avec variables ; garde la reference au chemin pour simuler les sorties"""
    out = []
    for st in sorted(C):
        R = C[st]; g = RES.get((A, st))
        if g is None: continue
        hz = ((st // 3600) + 2) % 24
        for up in (True, False):
            sg = 1 if up else -1; L = []
            for i, r in enumerate(R):
                tl = st + 300 - r[0]
                if tl < 10: break
                ask = r[4] if up else r[6]; bid = r[3] if up else r[5]; fair = r[2] if up else 1 - r[2]
                if not (0.02 <= ask <= 0.97) or fair - ask < 0.10: continue
                def back(n):
                    j = i
                    while j > 0 and r[0] - R[j][0] < n: j -= 1
                    return R[j] if r[0] - R[j][0] >= n - 0.5 else None
                h3, h5 = back(3), back(5)
                d = lambda h, c: ((r[c] - h[c]) * sg) if h and h[c] and r[c] else 0.0
                mid = lambda x: (x[3] + x[4]) / 2 if up else (x[5] + x[6]) / 2
                fr = lambda x: x[2] if up else 1 - x[2]
                ed = lambda x: fr(x) - (x[4] if up else x[6])
                L.append({"i": i, "t": r[0], "tl": tl, "ask": ask, "fair": fair, "edge": fair - ask, "spread": ask - bid if bid else 0.05,
                          "taille": (r[8] if up else r[10]) or 0, "bn": d(h3, 14), "perp": d(h3, 11), "okx": d(h3, 12), "cb": d(h3, 13), "cl": d(h3, 15),
                          "mkt5": (mid(r) - mid(h5)) if h5 else 0.0, "v3": (fair - ask - ed(h3)) if h3 else 0.0, "dfair3": (fair - fr(h3)) if h3 else 0.0})
            if L: out.append({"st": st, "hz": hz, "up": up, "gm": g if up else (not g), "R": R, "pts": L})
    return out


def pnl_tenir(p, gm): return (50 / p) * ((1 if gm else 0) - p - FEE(p))


def sim_sortie(ev, pt, regle):
    """regle(etat) -> None (garder) / 'vendre' / 'verrou' ; etat = dict de l'instant ; renvoie le resultat"""
    up = ev["up"]; R = ev["R"]; p = pt["ask"]; parts = 50 / p
    for x in R[pt["i"] + 1:]:
        tl = ev["st"] + 300 - x[0]
        if tl < 2: break
        bid = x[3] if up else x[5]; bz = (x[7] if up else x[9]) or 0; oa = x[6] if up else x[4]
        fair = x[2] if up else 1 - x[2]
        if bid is None: continue
        e = {"dt": x[0] - pt["t"], "tl": tl, "bid": bid, "fair": fair, "f0": pt["fair"], "p": p, "oa": oa}
        a = regle(e)
        if a == "vendre":
            bx = bid if bz >= parts / 2 else bid - 0.01; bx = max(bx, 0.0)
            return parts * (bx - FEE(bx)) - parts * (p + FEE(p)), "vendu"
        if a == "verrou" and oa is not None:
            return parts * (1 - p - oa - FEE(p) - FEE(oa)), "verrouille"
    return pnl_tenir(p, ev["gm"]), "fin"


SORTIES = {
    "garder jusqu'a la fin (reference)": lambda e: None,
    "stop : meilleur acheteur <= entree - 5 c": lambda e: "vendre" if e["bid"] <= e["p"] - 0.05 else None,
    "stop : meilleur acheteur <= entree - 10 c": lambda e: "vendre" if e["bid"] <= e["p"] - 0.10 else None,
    "stop : meilleur acheteur <= entree - 15 c": lambda e: "vendre" if e["bid"] <= e["p"] - 0.15 else None,
    "stop : meilleur acheteur <= moitie de l'entree": lambda e: "vendre" if e["bid"] <= e["p"] / 2 else None,
    "sortie si le modele perd 10 pts": lambda e: "vendre" if e["fair"] <= e["f0"] - 0.10 else None,
    "sortie si le modele perd 20 pts": lambda e: "vendre" if e["fair"] <= e["f0"] - 0.20 else None,
    "sortie si le modele passe sous le prix d'achat": lambda e: "vendre" if e["fair"] < e["p"] else None,
    "sortie si le modele passe sous le meilleur acheteur": lambda e: "vendre" if e["fair"] < e["bid"] else None,
    "a 60 s de la fin : vendre si perdant": lambda e: "vendre" if e["tl"] <= 60 and e["bid"] < e["p"] else None,
    "a 30 s de la fin : vendre si perdant": lambda e: "vendre" if e["tl"] <= 30 and e["bid"] < e["p"] else None,
    "a 60 s : vendre si le modele < 0,30": lambda e: "vendre" if e["tl"] <= 60 and e["fair"] < 0.30 else None,
    "verrou : acheter l'autre cote si paire <= 0,97": lambda e: "verrou" if e["oa"] is not None and e["p"] + e["oa"] + FEE(e["p"]) + FEE(e["oa"]) <= 0.97 else None,
    "verrou si paire <= 0,90 (gain assure 10 c)": lambda e: "verrou" if e["oa"] is not None and e["p"] + e["oa"] + FEE(e["p"]) + FEE(e["oa"]) <= 0.90 else None,
    "modele -20 pts OU stop -15 c": lambda e: "vendre" if (e["fair"] <= e["f0"] - 0.20 or e["bid"] <= e["p"] - 0.15) else None,
}

BASES = {
    "ecart >= 0,30 · 0,15-0,35 · > 60 s": (0.30, 0.15, 0.35, 60, 300),
    "ecart >= 0,25 · 0,15-0,35 · > 60 s": (0.25, 0.15, 0.35, 60, 300),
    "ecart >= 0,30 · 0,15-0,35 · tout temps": (0.30, 0.15, 0.35, 10, 300),
    "ecart >= 0,25 · 0,15-0,35 · tout temps": (0.25, 0.15, 0.35, 10, 300),
    "ecart >= 0,20 · 0,15-0,35 · > 60 s": (0.20, 0.15, 0.35, 60, 300),
    "ecart >= 0,15 · 0,35-0,60 · 30-120 s": (0.15, 0.35, 0.60, 30, 120),
    "ecart >= 0,20 · 0,35-0,60 · > 60 s": (0.20, 0.35, 0.60, 60, 300),
    "ecart >= 0,30 · 0,15-0,60 · > 60 s": (0.30, 0.15, 0.60, 60, 300),
}
FILTRES = {
    "Binance >= 0": lambda p, ev: p["bn"] >= 0, "perp >= 0": lambda p, ev: p["perp"] >= 0, "OKX >= 0": lambda p, ev: p["okx"] >= 0,
    "Coinbase >= 0": lambda p, ev: p["cb"] >= 0, "Chainlink >= 0": lambda p, ev: p["cl"] >= 0, "Binance contre": lambda p, ev: p["bn"] < 0,
    "Poly monte (5 s)": lambda p, ev: p["mkt5"] > 0, "Poly baisse (5 s)": lambda p, ev: p["mkt5"] < 0, "Poly immobile (5 s)": lambda p, ev: p["mkt5"] == 0,
    "ecart qui grandit (3 s)": lambda p, ev: p["v3"] > 0, "ecart qui retrecit (3 s)": lambda p, ev: p["v3"] < 0,
    "modele monte (3 s)": lambda p, ev: p["dfair3"] > 0, "modele baisse (3 s)": lambda p, ev: p["dfair3"] < 0,
    "spread 1 c": lambda p, ev: p["spread"] <= 0.011, "spread > 1 c": lambda p, ev: p["spread"] > 0.011,
    "vendeur >= 200 parts": lambda p, ev: p["taille"] >= 200, "vendeur < 200 parts": lambda p, ev: p["taille"] < 200,
    "sans nuit": lambda p, ev: ev["hz"] >= 8, "nuit seulement": lambda p, ev: ev["hz"] < 8,
    "cote Up": lambda p, ev: ev["up"], "cote Down": lambda p, ev: not ev["up"],
    "modele >= 0,55": lambda p, ev: p["fair"] >= 0.55,
}


_CACHE = {}
def trades(EV, base, filtres=()):
    if base not in _CACHE:
        e0, p0, p1, t0, t1 = base
        _CACHE[base] = [(ev, [pt for pt in ev["pts"] if pt["edge"] >= e0 and p0 <= pt["ask"] < p1 and t0 < pt["tl"] <= t1]) for ev in EV]
    T = []
    for ev, L in _CACHE[base]:
        for pt in L:
            if all(f(pt, ev) for f in filtres):
                T.append((ev, pt)); break
    return T


def stats(T, pnls, q):
    quart = lambda st: sum(st >= x for x in q)
    Q = [sum(p for (ev, pt), p in zip(T, pnls) if quart(ev["st"]) == k) for k in range(4)]
    P = sorted(pnls, reverse=True)
    cum = pk = cr = 0.0
    for (ev, pt), p in sorted(zip(T, pnls), key=lambda z: z[0][1]["t"]):
        cum += p; pk = max(pk, cum); cr = min(cr, cum - pk)
    return {"n": len(T), "tot": sum(pnls), "q": Q, "sans3": sum(P[3:]), "creux": cr, "pire": min(pnls) if pnls else 0, "gagnes": sum(1 for p in pnls if p > 0)}


def main():
    A = "BTC"
    C = charger_brut(A); sts = sorted(C)
    for st in sts: resultat(A, st)
    EV = points(A, C)
    q = [sts[int(len(sts) * k / 4)] for k in (1, 2, 3)]
    J = {"periode": [sts[0], sts[-1] + 300], "quarts": q}
    rap = [f"# Zone desaccord 30 · 0,15-0,35 — vrais carnets du bot, BTC ({time.strftime('%d.%m %H:%M', time.gmtime(sts[0] + 7200))} -> {time.strftime('%d.%m %H:%M', time.gmtime(sts[-1] + 7500))}, heure suisse)", ""]
    # 1. trades
    base = BASES["ecart >= 0,30 · 0,15-0,35 · > 60 s"]
    J["trades"] = {}
    for nom, fl in (("zone", ()), ("zone + Binance et perp >= 0", (FILTRES["Binance >= 0"], FILTRES["perp >= 0"]))):
        T = trades(EV, base, fl); L = []
        for ev, pt in sorted(T, key=lambda z: z[1]["t"]):
            L.append({"t": pt["t"], "cote": "Up" if ev["up"] else "Down", "prix": pt["ask"], "modele": round(pt["fair"], 3), "ecart": round(pt["edge"], 3),
                      "reste": round(pt["tl"]), "bn": round(pt["bn"], 1), "perp": round(pt["perp"], 1), "gagne": bool(ev["gm"]), "pnl": round(pnl_tenir(pt["ask"], ev["gm"]), 2)})
        J["trades"][nom] = L
    # 2. sorties
    J["sorties"] = {}
    rap += ["## Reduire les pertes sur la zone (ecart >= 0,30 · 0,15-0,35 · > 60 s)", "",
            "| Gestion | Trades | Gagnes | Q1 | Q2 | Q3 | Q4 | **Total** | Sans top 3 | Creux max | Pire trade |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for zn, fl in (("zone", ()), ("zone + Binance et perp >= 0", (FILTRES["Binance >= 0"], FILTRES["perp >= 0"]))):
        T = trades(EV, base, fl)
        rap.append(f"| **{zn}** | | | | | | | | | | |")
        J["sorties"][zn] = {}
        for sn, rg in SORTIES.items():
            pn = [sim_sortie(ev, pt, rg)[0] for ev, pt in T]
            s = stats(T, pn, q); J["sorties"][zn][sn] = s
            rap.append(f"| {sn} | {s['n']} | {s['gagnes']} | " + " | ".join(f"{x:+.0f}" for x in s["q"]) + f" | **{s['tot']:+.0f} $** | {s['sans3']:+.0f} $ | {s['creux']:+.0f} $ | {s['pire']:+.0f} $ |")
    # 3. combinaisons
    res = []
    noms = list(FILTRES)
    for bn_, b in BASES.items():
        for k in (0, 1, 2):
            for combo in itertools.combinations(noms, k):
                T = trades(EV, b, [FILTRES[c] for c in combo])
                if len(T) < 25: continue
                pn = [pnl_tenir(pt["ask"], ev["gm"]) for ev, pt in T]
                s = stats(T, pn, q); s["nom"] = bn_ + ("" if not combo else " · " + " · ".join(combo)); s["k"] = k
                res.append(s)
    rob = [r for r in res if min(r["q"]) > 0 and r["sans3"] > 0]
    J["combis"] = {"teste": len(res), "robustes": sorted(rob, key=lambda r: -min(r["q"]))[:60]}
    rap += ["", f"## Combinaisons plus profondes — {len(res)} testees (>= 25 trades), {len(rob)} robustes", "",
            "| Combinaison | Trades | Q1 | Q2 | Q3 | Q4 | **Total** | Par trade | Sans top 3 | Creux max |", "|---|---|---|---|---|---|---|---|---|---|"]
    for r in J["combis"]["robustes"][:40]:
        rap.append(f"| {r['nom']} | {r['n']} | " + " | ".join(f"{x:+.0f}" for x in r["q"]) + f" | **{r['tot']:+.0f} $** | {r['tot'] / r['n']:+.1f} $ | {r['sans3']:+.0f} $ | {r['creux']:+.0f} $ |")
    # frequence des filtres chez les robustes
    fr = []
    for f in noms:
        a = sum(1 for r in rob if f in r["nom"]); b = sum(1 for r in res if f in r["nom"])
        fr.append((f, a, b, (a / max(1, len(rob))) / max(1e-9, b / max(1, len(res)))))
    J["filtres"] = fr
    rap += ["", "### Filtres : presence chez les robustes / chez toutes (> 1 = aide, < 1 = nuit)", "", "| Filtre | Robustes | Toutes | Rapport |", "|---|---|---|---|"]
    for f, a, b, rt in sorted(fr, key=lambda z: -z[3]):
        rap.append(f"| {f} | {a} | {b} | {rt:.2f} |")
    open(OUT + "resultat_zone.md", "w").write("\n".join(rap))
    json.dump(J, open(OUT + "zone.json", "w"), ensure_ascii=False)
    print("\n".join(rap))


if __name__ == "__main__":
    main()
