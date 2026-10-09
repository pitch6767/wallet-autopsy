"""La serie de 27 pertes de V2-F « ecart qui grandit » (BTC) — 09.10.2026.
Les trades d'origine sont effaces (le bot ne gardait que les 60 derniers) : on rejoue la regle exacte sur les vrais carnets (48 h, 4 mesures/s).
Le cycle et son resultat sont fiables ; le prix d'achat exact peut differer un peu du direct.
1. Trouver la plus longue serie de pertes du rejeu ; la comparer aux 16 trades d'avant, aux 14 d'apres et a tous les trades.
2. Pour chaque entree : qui a cree l'ecart qui grandit (modele monte / Polymarket baisse / les deux / les deux baissent, Poly plus) ;
   probabilite annoncee, resultat, volatilite, temps restant, distance Chainlink - seuil (en ecarts-types), cote, tendance 15 min.
3. Statistique : une serie de 27 est-elle normale avec 24 % de gagnants ? Et avec les probabilites du modele / du prix Polymarket ?
4. Test decisif : un signal connu AVANT l'achat aurait-il evite une partie de la serie sans enlever les gros gagnants du reste ?
"""
import sys, json, math, time, random, statistics, bisect
import numpy as np
sys.path.insert(0, "etude/bot5min")
from sauvetage import resultat, RES, FEE
from proche import charger_brut

OUT = "etude/bot5min/"


def main():
    A = "BTC"
    C = charger_brut(A); sts = sorted(C)
    for st in sts: resultat(A, st)
    serie = sorted((r[0], r[11]) for st in sts for r in C[st] if r[11])
    ts = [x[0] for x in serie]; ps = [x[1] for x in serie]
    def px(t):
        k = bisect.bisect_right(ts, t) - 1
        return ps[k] if k >= 0 and t - ts[k] < 30 else None
    T = []
    for st in sts:
        R = C[st]; g = RES.get((A, st))
        if g is None: continue
        done = False
        for i, r in enumerate(R):
            tl = st + 300 - r[0]
            if tl < 5: break
            j = i
            while j > 0 and r[0] - R[j][0] < 3: j -= 1
            h3 = R[j] if r[0] - R[j][0] >= 2.5 else None
            if h3 is None: continue
            for up in (True, False):
                ask = r[4] if up else r[6]; fair = r[2] if up else 1 - r[2]
                a3 = h3[4] if up else h3[6]; f3 = h3[2] if up else 1 - h3[2]
                if ask is None or a3 is None or not (0.03 <= ask <= 0.97): continue
                if fair - ask >= 0.20 and (fair - ask) - (f3 - a3) >= 0.03:
                    sg = 1 if up else -1; gm = g if up else (not g)
                    dm, da = fair - f3, ask - a3
                    if dm >= 0.02 and abs(da) < 0.02: orig = "le modele monte, Poly stable"
                    elif da <= -0.02 and abs(dm) < 0.02: orig = "Poly baisse, modele stable"
                    elif dm >= 0.02 and da <= -0.02: orig = "modele monte ET Poly baisse"
                    elif dm < 0 and da < dm: orig = "les deux baissent, Poly plus"
                    else: orig = "autre"
                    W = [x for x in R[:i + 1] if r[0] - x[0] <= 60 and x[11]]
                    d = np.diff([x[11] for x in W]) if len(W) > 5 else np.array([0.0])
                    sig = max(float(np.std(d)) * 2, 0.5)
                    cl, k = r[15], r[16]
                    z = ((cl - k) * sg) / (sig * math.sqrt(max(tl, 1))) if cl and k else 0.0
                    p15 = px(r[0] - 900)
                    T.append({"t": r[0], "st": st, "cote": "Up" if up else "Down", "prix": ask, "modele": round(fair, 3), "ecart": round(fair - ask, 3),
                              "dmod": round(dm, 3), "dpoly": round(da, 3), "origine": orig, "reste": round(tl), "vol": round(sig, 2), "z": round(z, 2),
                              "tend15": round(((r[11] - p15) * sg) if p15 and r[11] else 0.0, 1), "gagne": bool(gm), "oa": (r[6] if up else r[4]), "pmid": round(((r[3] + r[4]) / 2 if up else (r[5] + r[6]) / 2), 3) if None not in (r[3], r[4], r[5], r[6]) else None,
                              "pnl": round((50 / ask) * ((1 if gm else 0) - ask - FEE(ask)), 2)})
                    done = True; break
            if done: break
    # plus longue serie de pertes
    best = c = s0 = 0
    for i, t in enumerate(T):
        c = c + 1 if not t["gagne"] else 0
        if c > best: best, s0 = c, i - c + 1
    S = T[s0:s0 + best]; AV = T[max(0, s0 - 16):s0]; AP = T[s0 + best:s0 + best + 14]
    hs = lambda t: time.strftime("%d.%m %H:%M", time.gmtime(t + 7200))
    rap = [f"# La serie de pertes de V2-F — rejeu sur les vrais carnets ({hs(sts[0])} -> {hs(sts[-1] + 300)})", "",
           f"{len(T)} trades rejoues, {sum(t['gagne'] for t in T)} gagnes ({100 * statistics.mean(t['gagne'] for t in T):.1f} %). "
           f"Plus longue serie de pertes : **{best}** du {hs(S[0]['t'])} au {hs(S[-1]['t'])}.", ""]
    def resume(nom, X):
        if not X: return f"| {nom} | 0 |" + " |" * 11
        o = lambda k: sum(1 for t in X if t["origine"] == k)
        return (f"| {nom} | {len(X)} | {sum(t['gagne'] for t in X)} | {statistics.mean(t['modele'] for t in X):.2f} | {statistics.mean(t['prix'] for t in X):.2f} | "
                f"{statistics.mean(t['ecart'] for t in X):.2f} | {statistics.mean(t['reste'] for t in X):.0f} s | {statistics.mean(t['vol'] for t in X):.1f} | "
                f"{statistics.median(t['z'] for t in X):+.2f} | {sum(t['cote'] == 'Up' for t in X)}/{sum(t['cote'] == 'Down' for t in X)} | {statistics.mean(t['tend15'] for t in X):+.0f} | "
                f"{o('le modele monte, Poly stable')} / {o('Poly baisse, modele stable')} / {o('modele monte ET Poly baisse')} / {o('les deux baissent, Poly plus')} / {o('autre')} |")
    rap += ["## 1. La serie comparee aux autres trades", "",
            "| Groupe | Trades | Gagnes | Modele moyen | Prix moyen | Ecart | Reste | Volatilite ($/s) | Distance Chainlink (mediane, ecarts-types, + = on gagne deja) | Up/Down | Tendance BTC 15 min ($, + = notre sens) | Origine : modele monte / Poly baisse / les deux / les deux baissent / autre |",
            "|---|---|---|---|---|---|---|---|---|---|---|---|",
            resume(f"16 trades avant", AV), resume(f"**la serie ({best})**", S), resume("14 trades apres", AP), resume("tous les trades", T), ""]
    # gagnants par origine sur tous
    rap += ["## 2. Qui a cree l'ecart qui grandit — sur tous les trades", "", "| Origine | Trades | Gagnes | % gagnes | Resultat rejoue |", "|---|---|---|---|---|"]
    for o in ("le modele monte, Poly stable", "Poly baisse, modele stable", "modele monte ET Poly baisse", "les deux baissent, Poly plus", "autre"):
        X = [t for t in T if t["origine"] == o]
        if X: rap.append(f"| {o} | {len(X)} | {sum(t['gagne'] for t in X)} | {100 * statistics.mean(t['gagne'] for t in X):.0f} % | {sum(t['pnl'] for t in X):+.0f} $ |")
    # 3. statistique
    p = statistics.mean(t["gagne"] for t in T); N = 430
    random.seed(1); sims = 20000; hit = 0
    for _ in range(sims):
        c = m = 0
        for _ in range(N):
            c = 0 if random.random() < p else c + 1; m = max(m, c)
        if m >= best: hit += 1
    lp_m = sum(math.log(1 - t["modele"]) for t in S); lp_p = sum(math.log(1 - t["prix"]) for t in S)
    attendu_m = sum(t["modele"] for t in S); attendu_p = sum(t["prix"] for t in S)
    rap += ["", "## 3. Une serie de " + str(best) + " est-elle normale ?", "",
            f"- Avec {100 * p:.1f} % de gagnants et {N} trades (V2-F en direct), une serie d'au moins {best} pertes arrive dans **{100 * hit / sims:.1f} %** des simulations ({sims} tirages).",
            f"- Selon **notre modele**, ces {best} trades devaient gagner {attendu_m:.1f} fois en moyenne ; probabilite de tous les perdre = {math.exp(lp_m):.2e}.",
            f"- Selon **le prix Polymarket**, ils devaient gagner {attendu_p:.1f} fois ; probabilite de tous les perdre = {math.exp(lp_p):.2e}.", ""]
    # 4. test decisif : signaux avant l'achat
    cand = {
        "pas « Poly baisse, modele stable »": lambda t: t["origine"] != "Poly baisse, modele stable",
        "seulement « le modele monte »": lambda t: t["origine"] in ("le modele monte, Poly stable", "modele monte ET Poly baisse"),
        "distance Chainlink < 0 (on perd encore)": lambda t: t["z"] < 0,
        "distance Chainlink < -0,3": lambda t: t["z"] < -0.3,
        "tendance 15 min >= 0": lambda t: t["tend15"] >= 0,
        "prix >= 0,10": lambda t: t["prix"] >= 0.10,
        "pas « les deux baissent, Poly plus »": lambda t: t["origine"] != "les deux baissent, Poly plus",
        "volatilite >= 2 $/s": lambda t: t["vol"] >= 2.0,
        "volatilite >= 3 $/s": lambda t: t["vol"] >= 3.0,
        "pas « les deux baissent » ET volatilite >= 2": lambda t: t["origine"] != "les deux baissent, Poly plus" and t["vol"] >= 2.0,
        "reste >= 60 s": lambda t: t["reste"] >= 60,
        "modele <= 0,60": lambda t: t["modele"] <= 0.60,
    }
    gros = sorted(T, key=lambda t: -t["pnl"])[:10]
    rap += ["## 4. Test decisif : un signal connu avant l'achat aurait-il evite une partie de la serie ?", "",
            "| Signal (on achete seulement si…) | Pertes de la serie evitees | Trades gardes (tous) | Gagnes gardes | Des 10 plus gros gagnants, gardes | Resultat rejoue (tous) |", "|---|---|---|---|---|---|",
            f"| (aucun filtre) | 0 / {best} | {len(T)} | {sum(t['gagne'] for t in T)} | 10 / 10 | {sum(t['pnl'] for t in T):+.0f} $ |"]
    for nom, f in cand.items():
        X = [t for t in T if f(t)]
        rap.append(f"| {nom} | {sum(1 for t in S if not f(t))} / {best} | {len(X)} | {sum(t['gagne'] for t in X)} | {sum(1 for t in gros if f(t))} / 10 | {sum(t['pnl'] for t in X):+.0f} $ |")
    J = {"serie": S, "avant": AV, "apres": AP, "n": len(T), "best": best}
    json.dump(J, open(OUT + "serie.json", "w"), ensure_ascii=False)
    json.dump(T, open(OUT + "v2f_tous.json", "w"), ensure_ascii=False)
    rap += ["", "## Annexe — les trades de la serie", "", "| # | Heure | Cote | Prix | Modele | Ecart | dModele 3 s | dPoly 3 s | Origine | Reste | Distance | Gagne |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for i, t in enumerate(AV + S + AP, 1):
        tag = "avant" if t in AV else ("SERIE" if t in S else "apres")
        rap.append(f"| {i} {tag} | {hs(t['t'])} | {t['cote']} | {t['prix']:.2f} | {t['modele']:.2f} | {t['ecart']:.2f} | {t['dmod']:+.2f} | {t['dpoly']:+.2f} | {t['origine']} | {t['reste']} s | {t['z']:+.2f} | {'oui' if t['gagne'] else 'non'} |")
    open(OUT + "resultat_serie.md", "w").write("\n".join(rap))
    print("\n".join(rap))


if __name__ == "__main__":
    main()
