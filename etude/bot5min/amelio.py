"""Ameliorer « desaccord 30 zone + Binance et perp + sortie modele -10 » sans perdre de gain, en reduisant les trades perdants — 08.10.2026.
Vrais carnets du bot (48 h, 4 mesures/s), BTC. Base = zone (ecart >= 0,30, 0,15-0,35, > 60 s) + Binance et perp >= 0 sur 3 s + revente si le modele perd 10 pts.
Teste : filtres a l'entree (seuls et par deux) et variantes de sortie. Pour chaque regle : trades, perdants, resultat, 4 quarts, sans top 3.
"""
import sys, json, itertools, time
sys.path.insert(0, "etude/bot5min")
import zone as Z
from sauvetage import resultat, RES, FEE
from proche import charger_brut

OUT = "etude/bot5min/"


def sortie(seuil=0.10, tl_min=0, plancher=0.0):
    def r(e):
        if e["fair"] <= e["f0"] - seuil and e["tl"] > tl_min and e["bid"] >= plancher: return "vendre"
        return None
    return r


SORTIES = {
    "revente si modele -10 (actuel)": sortie(0.10),
    "revente si modele -10, seulement s'il reste > 60 s": sortie(0.10, 60),
    "revente si modele -10, seulement si acheteur >= 0,05": sortie(0.10, 0, 0.05),
    "revente si modele -10, > 60 s ET acheteur >= 0,05": sortie(0.10, 60, 0.05),
    "revente si modele -15": sortie(0.15),
    "revente si modele -15, > 60 s ET acheteur >= 0,05": sortie(0.15, 60, 0.05),
    "jamais de revente (garder)": lambda e: None,
}
F = {
    "le modele a monte (>= 3 pts en 3 s)": lambda p, ev: p["dfair3"] >= 0.03,
    "pas « Polymarket qui baisse »": lambda p, ev: not ((p["dfair3"] - p["v3"]) <= -0.03 and p["dfair3"] < 0.03),
    "ecart qui grandit": lambda p, ev: p["v3"] > 0,
    "plus de 120 s restantes": lambda p, ev: p["tl"] > 120,
    "plus de 90 s restantes": lambda p, ev: p["tl"] > 90,
    "prix >= 0,18": lambda p, ev: p["ask"] >= 0.18,
    "prix >= 0,20": lambda p, ev: p["ask"] >= 0.20,
    "modele >= 0,50": lambda p, ev: p["fair"] >= 0.50,
    "ecart >= 0,33": lambda p, ev: p["edge"] >= 0.33,
    "vendeur assez gros pour 50 $": lambda p, ev: p["taille"] >= 50 / p["ask"],
    "spread 1 c": lambda p, ev: p["spread"] <= 0.011,
    "Polymarket monte (5 s)": lambda p, ev: p["mkt5"] > 0,
    "OKX >= 0": lambda p, ev: p["okx"] >= 0,
    "Coinbase >= 0": lambda p, ev: p["cb"] >= 0,
    "sans nuit": lambda p, ev: ev["hz"] >= 8,
}


def main():
    A = "BTC"
    C = charger_brut(A); sts = sorted(C)
    for st in sts: resultat(A, st)
    EV = Z.points(A, C)
    q = [sts[int(len(sts) * k / 4)] for k in (1, 2, 3)]
    base = Z.BASES["ecart >= 0,30 · 0,15-0,35 · > 60 s"]
    bp = [Z.FILTRES["Binance >= 0"], Z.FILTRES["perp >= 0"]]
    rap = [f"# Ameliorer « zone + Binance et perp + sortie modele -10 » — BTC, vrais carnets ({time.strftime('%d.%m %H:%M', time.gmtime(sts[0] + 7200))} -> {time.strftime('%d.%m %H:%M', time.gmtime(sts[-1] + 7500))})", ""]
    J = {}
    H = "| Regle | Trades | Perdants | Q1 | Q2 | Q3 | Q4 | **Total** | Par trade | Sans top 3 | Creux |\n|---|---|---|---|---|---|---|---|---|---|---|"
    def eval_(T, rg):
        pn = [Z.sim_sortie(ev, pt, rg)[0] for ev, pt in T]
        s = Z.stats(T, pn, q); s["perdants"] = sum(1 for p in pn if p < 0); return s
    def ligne(nom, s):
        return f"| {nom} | {s['n']} | {s['perdants']} | " + " | ".join(f"{x:+.0f}" for x in s["q"]) + f" | **{s['tot']:+.0f} $** | {s['tot'] / max(1, s['n']):+.1f} $ | {s['sans3']:+.0f} $ | {s['creux']:+.0f} $ |"
    T0 = Z.trades(EV, base, bp)
    rap += ["## 1. Sorties (memes entrees)", "", H]
    J["sorties"] = {}
    for sn, rg in SORTIES.items():
        s = eval_(T0, rg); J["sorties"][sn] = s; rap.append(ligne(sn, s))
    ref = J["sorties"]["revente si modele -10 (actuel)"]
    rap += ["", "## 2. Filtres a l'entree (sortie actuelle), seuls et par deux", "",
            "Garde = total >= 95 % de la reference ET moins de perdants ET les 4 quarts positifs.", "", H]
    rap.append(ligne("REFERENCE", ref))
    res = []
    for k in (1, 2):
        for combo in itertools.combinations(F, k):
            T = Z.trades(EV, base, bp + [F[c] for c in combo])
            if len(T) < 15: continue
            s = eval_(T, SORTIES["revente si modele -10 (actuel)"]); s["nom"] = " + ".join(combo); res.append(s)
    bons = [s for s in res if s["tot"] >= 0.95 * ref["tot"] and s["perdants"] < ref["perdants"] and min(s["q"]) > 0]
    for s in sorted(bons, key=lambda s: (s["perdants"] / s["n"], -s["tot"]))[:25]:
        rap.append(ligne(s["nom"], s))
    rap += ["", "### Tous les filtres seuls", "", H]
    for s in [s for s in res if " + " not in s["nom"]]:
        rap.append(ligne(s["nom"], s))
    J["bons"] = sorted(bons, key=lambda s: (s["perdants"] / s["n"], -s["tot"]))[:25]
    J["seuls"] = [s for s in res if " + " not in s["nom"]]
    J["ref"] = ref
    # trades de la reference (pour le PDF)
    L = []
    for ev, pt in sorted(T0, key=lambda z: z[1]["t"]):
        p, how = Z.sim_sortie(ev, pt, SORTIES["revente si modele -10 (actuel)"])
        L.append({"t": pt["t"], "cote": "Up" if ev["up"] else "Down", "prix": pt["ask"], "modele": round(pt["fair"], 3), "ecart": round(pt["edge"], 3), "reste": round(pt["tl"]),
                  "bn": round(pt["bn"], 1), "perp": round(pt["perp"], 1), "gagne": bool(ev["gm"]), "sortie": how, "pnl": round(p, 2)})
    J["trades_hist"] = L
    open(OUT + "resultat_amelio.md", "w").write("\n".join(rap))
    json.dump(J, open(OUT + "amelio.json", "w"), ensure_ascii=False, default=str)
    print("\n".join(rap))


if __name__ == "__main__":
    main()
