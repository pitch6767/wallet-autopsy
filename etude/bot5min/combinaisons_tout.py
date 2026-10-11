"""BOT95 — « COMBINE TOUT, ESSAIE TOUT AVEC TOUT » (demande de Pitch, 11.10.2026 15:51). Hors ligne, aucun bot modifié, aucun ordre.
Données : TOUS les trades fantômes sauvegardés (bot95/sauvegarde/*.json, BTC), chaque stratégie, plus un portefeuille « TOUS » (premier trade de
chaque cycle et côté, toutes stratégies confondues). Filtres combinés (1, 2 ou 3 conditions) : prix d'achat, temps restant, écart modèle − prix,
côté, heure suisse, jour/nuit. Sélection sur la période d'APPRENTISSAGE (60 % les plus anciens), contrôle sur la VALIDATION (40 % suivants) ;
la période réservée (≥ 13.10.2026 00:00 UTC) n'est pas lue. TÉMOIN : même procédure avec les résultats mélangés au hasard (combien de « gagnants »
le hasard fabrique). Usage : python3 etude/bot5min/combinaisons_tout.py → etude/bot5min/resultat_combinaisons_tout.md"""
import json, glob, os, itertools, collections, random, time
import numpy as np

ICI = os.path.dirname(os.path.abspath(__file__)); RACINE = os.path.abspath(os.path.join(ICI, "..", ".."))
SORTIE = os.path.join(ICI, "resultat_combinaisons_tout.md"); HORS_ECH = 1791849600
random.seed(4)


def charger():
    T = []
    for f in glob.glob(os.path.join(RACINE, "bot95", "sauvegarde", "*_BTC.json")):
        d = json.load(open(f)); L = d["trades"]; L = list(L.values()) if isinstance(L, dict) else L
        nom = os.path.basename(f)[:-9]
        for t in L:
            if not all(k in t for k in ("start", "cote", "prix", "net", "gagnant")) or t.get("prix") in (None, 0): continue
            if t["start"] >= HORS_ECH or not t.get("parts"): continue
            mise = t["prix"] * t["parts"]
            if mise <= 0: continue
            T.append(dict(strat=nom, start=t["start"], cote=t["cote"], prix=t["prix"], net=t["net"], mise=mise,
                          rest=t.get("restant_s"), edge=(t["proba0"] - t["prix"]) if t.get("proba0") is not None else None,
                          heure=(time.gmtime(t["start"] + 7200).tm_hour)))
    return T


def conditions():
    C = []
    for lo, hi in ((0, .15), (.15, .35), (.35, .5), (.5, .65), (.65, .85), (.85, 1.01)): C.append((f"prix {lo:.2f}–{min(hi, 1):.2f}", lambda t, lo=lo, hi=hi: lo <= t["prix"] < hi))
    for lo, hi in ((0, 60), (60, 120), (120, 180), (180, 240), (240, 301)): C.append((f"restant {lo}–{hi} s", lambda t, lo=lo, hi=hi: t["rest"] is not None and lo <= t["rest"] < hi))
    for lo, hi in ((-1, .1), (.1, .2), (.2, .3), (.3, 1.1)): C.append((f"écart {lo if lo > -1 else '<'}–{hi if hi < 1 else '+'}", lambda t, lo=lo, hi=hi: t["edge"] is not None and lo <= t["edge"] < hi))
    C.append(("côté Up", lambda t: t["cote"] == "Up")); C.append(("côté Down", lambda t: t["cote"] == "Down"))
    for lo, hi, nom in ((0, 8, "nuit 0–8 h"), (8, 14, "matin 8–14 h"), (14, 20, "après-midi 14–20 h"), (20, 24, "soir 20–24 h")):
        C.append((nom, lambda t, lo=lo, hi=hi: lo <= t["heure"] < hi))
    return C


def stats(L):
    if not L: return 0, 0.0, 0.0
    n = len(L); net = sum(t["net"] for t in L); mise = sum(t["mise"] for t in L); return n, net, net / mise


def chercher(groupes, C, coupe, melange=False):
    res = []
    for g, L in groupes.items():
        A = [t for t in L if t["start"] < coupe]; V = [t for t in L if t["start"] >= coupe]
        if melange:                                                     # témoin : résultats permutés au sein de chaque stratégie
            nets = [t["net"] / t["mise"] for t in L]; random.shuffle(nets)
            L2 = [dict(t, net=nets[i] * t["mise"]) for i, t in enumerate(L)]; A = [t for t in L2 if t["start"] < coupe]; V = [t for t in L2 if t["start"] >= coupe]
        for k in (1, 2, 3):
            for combo in itertools.combinations(range(len(C)), k):
                noms = [C[i][0] for i in combo]
                if len({n.split()[0] for n in noms}) < k: continue          # une seule condition par famille (prix, restant, écart…)
                fA = [t for t in A if all(C[i][1](t) for i in combo)]
                if len(fA) < 40: continue
                nA, rA, pA = stats(fA)
                fV = [t for t in V if all(C[i][1](t) for i in combo)]
                nV, rV, pV = stats(fV)
                res.append((g, " + ".join(noms), nA, rA, pA, nV, rV, pV))
    return res


def main():
    T = charger(); T.sort(key=lambda t: t["start"])
    starts = sorted({t["start"] for t in T}); coupe = starts[int(len(starts) * 0.6)]
    groupes = collections.defaultdict(list)
    for t in T: groupes[t["strat"]].append(t)
    vu = set(); tous = []
    for t in T:
        k = (t["start"], t["cote"])
        if k not in vu: vu.add(k); tous.append(t)
    groupes["TOUS (premier trade du cycle et du côté)"] = tous
    C = conditions()
    R = chercher(groupes, C, coupe)
    top = sorted([r for r in R if r[5] >= 20], key=lambda r: -r[4])[:300]
    surv = [r for r in top if r[7] > 0 and r[6] > 0]
    Rm = chercher(groupes, C, coupe, melange=True)
    topm = sorted([r for r in Rm if r[5] >= 20], key=lambda r: -r[4])[:300]; survm = [r for r in topm if r[7] > 0 and r[6] > 0]
    o = []; w = o.append
    w("# Bot95 — Tout combiné avec tout (PRÉLIMINAIRE, non validé statistiquement)\n")
    w(f"Généré le {time.strftime('%d.%m.%Y %H:%M', time.gmtime())} UTC. {len(T)} trades fantômes BTC de {len(groupes) - 1} stratégies (+ portefeuille TOUS : {len(tous)} trades), "
      f"du {time.strftime('%d.%m %H:%M', time.gmtime(starts[0]))} au {time.strftime('%d.%m %H:%M', time.gmtime(starts[-1]))} UTC. "
      f"Apprentissage avant le {time.strftime('%d.%m %H:%M', time.gmtime(coupe))} UTC, validation après. Période réservée (≥ 13.10) non lue.\n")
    w(f"Combinaisons testées : {len(R)} (1 à 3 filtres, au moins 40 trades en apprentissage et 20 en validation pour le classement).\n")
    w("## Le contrôle qui compte : combien de « gagnants » le hasard fabrique-t-il ?\n")
    w(f"- Données réelles : parmi les 300 meilleures combinaisons en apprentissage, **{len(surv)}** restent positives en validation.")
    w(f"- Résultats mélangés au hasard (aucun vrai signal) : **{len(survm)}** sur 300 restent positives en validation.")
    w("- Si les deux nombres sont proches, les « meilleures combinaisons » sont surtout du hasard sélectionné après coup.\n")
    w("## Les 30 meilleures combinaisons en apprentissage, et ce qu'elles font ensuite\n")
    w("| Stratégie | Filtres | Trades appr. | Résultat appr. | par $ | Trades valid. | Résultat valid. | par $ valid. |\n|---|---|---|---|---|---|---|---|")
    for g, f, nA, rA, pA, nV, rV, pV in top[:30]:
        w(f"| {g} | {f} | {nA} | {rA:+.0f} $ | {pA:+.2f} | {nV} | {rV:+.0f} $ | {pV:+.2f} |")
    w("\n## Les combinaisons positives sur les DEUX périodes, triées par la validation (au moins 30 trades dans chaque)\n")
    deux = sorted([r for r in R if r[2] >= 30 and r[5] >= 30 and r[4] > 0 and r[7] > 0], key=lambda r: -min(r[4], r[7]))[:30]
    w("| Stratégie | Filtres | Trades appr. | par $ appr. | Trades valid. | par $ valid. | Résultat total |\n|---|---|---|---|---|---|---|")
    for g, f, nA, rA, pA, nV, rV, pV in deux:
        w(f"| {g} | {f} | {nA} | {pA:+.2f} | {nV} | {pV:+.2f} | {rA + rV:+.0f} $ |")
    # filtres qui reviennent souvent parmi les survivants (robustesse transversale)
    cpt = collections.Counter()
    for r in deux:
        for x in r[1].split(" + "): cpt[x] += 1
    w("\n**Filtres qui reviennent le plus souvent dans les combinaisons positives sur les deux périodes** : " + ", ".join(f"{k} ({v})" for k, v in cpt.most_common(10)) + "\n")
    w("## Limites\n- Beaucoup de combinaisons testées : certaines « marchent » par chance (voir le témoin mélangé).\n- Les trades fantômes supposent l'achat au prix vu (pas de retard de 150 ms, pas de file).\n"
      "- Seul le test sur la période réservée (cycles ≥ 13.10) peut confirmer un filtre ; aucun filtre n'est ajouté sans ton accord.\n")
    open(SORTIE, "w").write("\n".join(o)); print("\n".join(o))


if __name__ == "__main__":
    main()
