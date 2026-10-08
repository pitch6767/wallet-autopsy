"""Recherche d'une ZONE robuste (pas d'un point chanceux) sur les vrais carnets du bot (48 h, 4 mesures/s) — 08.10.2026.
Grille : ecart minimum x regle bourses x zone de prix x temps restant x nuit. Achat 50 $ au meilleur vendeur a l'instant du 1er desaccord
du cycle et du cote qui remplit TOUTES les conditions, garde jusqu'a la fin. Frais compris.
Robuste = positif sur les 4 quarts de la periode ET sans les 3 meilleurs trades, avec au moins 25 trades.
On classe par le PIRE des 4 quarts (ce qui protege contre la chance), pas par le total.
"""
import sys, itertools, statistics
sys.path.insert(0, "etude/bot5min")
from sauvetage import resultat, RES, FEE
from proche import charger_brut

OUT = "etude/bot5min/"
ECARTS = (0.10, 0.15, 0.20, 0.25, 0.30)
BOURSES = {
    "toutes": lambda b: True,
    "aucune contre (4 bourses >= 0)": lambda b: min(b) >= 0,
    "jury (4 >= 0, au moins 1 > 0)": lambda b: min(b) >= 0 and max(b) > 0,
    "Binance >= 0": lambda b: b[0] >= 0,
    "perp >= 0": lambda b: b[1] >= 0,
    "Binance et perp >= 0": lambda b: b[0] >= 0 and b[1] >= 0,
    "au plus 1 bourse contre": lambda b: sum(x < 0 for x in b) <= 1,
}
PRIX = {"tous prix": (0.0, 1.0), "< 0,15": (0.0, 0.15), "0,15-0,35": (0.15, 0.35), "0,35-0,60": (0.35, 0.60), "< 0,35": (0.0, 0.35)}
TEMPS = {"tout temps": (10, 300), "> 120 s": (120, 300), "30-120 s": (30, 120), "> 60 s": (60, 300)}
NUIT = {"jour et nuit": lambda h: True, "sans nuit": lambda h: h >= 8}


def evenements(A, C):
    """pour chaque cycle et cote : liste chronologique des instants achetables avec leurs variables"""
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
                ask = r[4] if up else r[6]; fair = r[2] if up else 1 - r[2]
                if not (0.02 <= ask <= 0.97) or fair - ask < 0.10: continue
                j = i
                while j > 0 and r[0] - R[j][0] < 3: j -= 1
                h = R[j] if r[0] - R[j][0] >= 2.5 else None
                b = tuple(((r[c] - h[c]) * sg) if h and h[c] and r[c] else 0.0 for c in (14, 11, 12, 13))
                L.append((tl, ask, fair - ask, b))
            if L: out.append({"st": st, "hz": hz, "gm": g if up else (not g), "pts": L})
    return out


def main():
    rap = ["# Recherche d'une zone robuste — vrais carnets du bot (48 h)", "",
           "Robuste = positif sur chacun des 4 quarts de la periode ET sans les 3 meilleurs trades (au moins 25 trades). Classement par le PIRE quart.", ""]
    for A in ("BTC",):
        C = charger_brut(A); sts = sorted(C)
        for st in sts: resultat(A, st)
        EV = evenements(A, C)
        q = [sts[int(len(sts) * k / 4)] for k in (1, 2, 3)]
        quart = lambda st: sum(st >= x for x in q)
        res = []
        for (e, (bn, bf), (pn, (p0, p1)), (tn, (t0, t1)), (nn, nf)) in itertools.product(ECARTS, BOURSES.items(), PRIX.items(), TEMPS.items(), NUIT.items()):
            T = []
            for ev in EV:
                if not nf(ev["hz"]): continue
                for tl, ask, edge, b in ev["pts"]:
                    if edge >= e and p0 <= ask < p1 and t0 <= tl <= t1 and bf(b):
                        T.append((ev["st"], (50 / ask) * ((1 if ev["gm"] else 0) - ask - FEE(ask)))); break
            if len(T) < 25: continue
            Q = [sum(p for s, p in T if quart(s) == k) for k in range(4)]
            P = sorted((p for s, p in T), reverse=True)
            res.append({"nom": f"ecart >= {e:.2f} · {bn} · {pn} · {tn} · {nn}", "n": len(T), "tot": sum(P), "q": Q, "sans3": sum(P[3:]), "pire": min(Q)})
        rob = [r for r in res if r["pire"] > 0 and r["sans3"] > 0]
        rap += [f"## {A} — {len(res)} combinaisons testees (>= 25 trades), **{len(rob)} robustes** ({100 * len(rob) / max(1, len(res)):.0f} %)", "",
                "| Combinaison | Trades | Q1 | Q2 | Q3 | Q4 | **Total** | Par trade | Sans top 3 |", "|---|---|---|---|---|---|---|---|---|"]
        for r in sorted(rob, key=lambda r: -r["pire"])[:40]:
            rap.append(f"| {r['nom']} | {r['n']} | " + " | ".join(f"{x:+.0f}" for x in r["q"]) + f" | **{r['tot']:+.0f} $** | {r['tot'] / r['n']:+.1f} $ | {r['sans3']:+.0f} $ |")
        # quel ingredient revient le plus dans les robustes, compare a sa frequence dans toutes les combinaisons
        rap += ["", "### Ingredients les plus frequents dans les combinaisons robustes (vs toutes)", "", "| Ingredient | Part chez les robustes | Part chez toutes |", "|---|---|---|"]
        for groupe in (ECARTS, BOURSES, PRIX, TEMPS, NUIT):
            for k in groupe:
                lab = f"ecart >= {k:.2f}" if isinstance(k, float) else k
                f_r = sum(1 for r in rob if f" {lab} " in f" {r['nom']} ".replace("·", " ")) / max(1, len(rob))
                f_a = sum(1 for r in res if f" {lab} " in f" {r['nom']} ".replace("·", " ")) / max(1, len(res))
                rap.append(f"| {lab} | {100 * f_r:.0f} % | {100 * f_a:.0f} % |")
        rap.append("")
    open(OUT + "resultat_robuste.md", "w").write("\n".join(rap))
    print("\n".join(rap))


if __name__ == "__main__":
    main()
