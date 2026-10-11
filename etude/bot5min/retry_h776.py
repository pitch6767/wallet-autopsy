"""BOT95 — R4 / H776–H778 (Pitch, 11.10.2026 17:25) : relances après disparition d'une offre. Hors ligne, aucun ordre, aucun fantôme gelé touché.
Période réservée (≥ 13.10 00:00 UTC) jamais lue ; aucun paramètre choisi sur elle. Le verdict hors échantillon se fera sur le fantôme R4 vivant.

Simulation : envoi à la décision puis toutes les 500 ms pendant la durée D ; chaque envoi est exécuté contre le carnet 164 ms plus tard (14 ms de trajet
+ 150 ms de retard preneur). Avant chaque envoi : probabilité recalculée avec les seules données reçues à cet instant (modèle de Dublin recalculé) ;
on n'achète que les niveaux où probabilité − prix − frais ≥ 0,05, au plus au plafond. Budget 50 $ par signal, fills partiels cumulés.
H776  Réapparition après disparition : délai, prix, quantité, profondeur, probabilité recalculée, résultat.
H777  Relance systématique (sans condition) contre conditionnelle (avantage net ; probabilité de réapparition apprise sur la 1re moitié).
H778  Durées 1/2/3/5 s × plafonds +0/+1/+2/+3 c ; recalcul contre modèle figé.
Usage : python3 etude/bot5min/retry_h776.py dossier_cycles → etude/bot5min/resultat_retry_h776.md"""
import json, os, sys, glob, collections, math, time
import numpy as np

ICI = os.path.dirname(os.path.abspath(__file__)); RACINE = os.path.abspath(os.path.join(ICI, "..", ".."))
sys.path.insert(0, ICI)
import latence_h766 as LH, modele_dublin as MD
HORS_ECH = 1791849600; SORTIE = os.path.join(ICI, "resultat_retry_h776.md")
EXEC = 164; MARGE = 0.05; BUDGET = 50.0
DUREES = (0, 1, 2, 3, 5)               # 0 = une seule tentative
PLAFONDS = (0, 10, 20, 30)
fee = lambda p: 0.07 * p * (1 - p)
rng = np.random.default_rng(776)


def ic(G, fn, n=1500):
    G = [g for g in G if g]
    if len(G) < 3: return (float("nan"), float("nan"))
    v = []
    for _ in range(n):
        s = [x for i in rng.integers(0, len(G), len(G)) for x in G[i]]
        r = fn(s)
        if r is not None: v.append(r)
    return (float(np.percentile(v, 5)), float(np.percentile(v, 95)))


def acheter_lim(L, X, lim, budget):
    q = c = 0.0
    for p, sz in LH.vendeurs(L, X):
        if p > lim: break
        pp = p / 1000; u = pp + fee(pp); k = min(sz, (budget - c) / u)
        if k <= 1e-9: break
        q += k; c += k * u
    return q, c


def limite(prob, a0m, cap, cond):
    lim = a0m + cap
    if cond:
        if prob is None: return -1
        while lim > 5 and prob - lim / 1000 - fee(lim / 1000) < MARGE: lim -= 10
    return lim


def main():
    dossier = sys.argv[1]
    F = {int(os.path.basename(f).split(".")[0]): f for f in glob.glob(os.path.join(dossier, "**", "*.json.gz"), recursive=True)}
    F = {k: v for k, v in F.items() if k < HORS_ECH}
    SIG = sorted([s for s in json.load(open(os.path.join(RACINE, "bot95", "rapide.json")))["signaux"] if s.get("gagnant") and s["start"] in F and s["start"] < HORS_ECH], key=lambda s: s["tDecision"])
    MK = [x for x in json.load(open(os.path.join(RACINE, "bot95", "rapide_maker.json"))) if x.get("type") != "resume" and x.get("resultat") and x["start"] in F]
    cycles = sorted({s["start"] for s in SIG}); coupe = cycles[len(cycles) // 2]
    LIG = []
    for st in cycles:
        cy = LH.Cycle(F[st]); prev = F.get(st - 300)
        Mo = MD.Modele(MD.charger_ex([f for f in (prev, F[st]) if f]), cy.strike, st + 300)
        S = [s for s in SIG if s["start"] == st]
        inst = []
        for s in S:
            t0 = s["tDecision"]; inst += [t0 + 500 * k + EXEC for k in range(10)] + [t0 + 25 * j for j in range(1, 201)]
        E = cy.etats(inst)
        for s in S:
            t0 = s["tDecision"]; X = s["cote"]; a0m = int(round(s["a0"] * 1000)); y = 1.0 if s["gagne"] else 0.0
            probs = []
            for k in range(10):
                p = Mo.proba((t0 + 500 * k) / 1000)
                f = None if p is None else LH.fair_regle(s["nom"], p); probs.append(None if f is None else (f if X == "Up" else 1 - f))
            r = dict(s=s, st=st, X=X, y=y, a0=s["a0"], probs=probs, pol={})
            # politiques : (durée, plafond, condition, recalcul)
            for D in DUREES:
                nk = 1 if D == 0 else 2 * D
                for cap in PLAFONDS:
                    for cond, recal in ((True, True), (True, False), (False, False)):
                        if D == 0 and cond: continue
                        budget = BUDGET; q = c = 0.0; first_k = None; fills = []
                        for k in range(nk):
                            if budget <= 0.01: break
                            prob = (probs[k] if recal else s["modele"])
                            lim = limite(prob, a0m, cap, cond)
                            if lim <= 0: continue
                            dq, dc = acheter_lim(E[t0 + 500 * k + EXEC], X, lim, budget)
                            if dq > 0:
                                q += dq; c += dc; budget -= dc; fills.append((k, dq, dc))
                                if first_k is None: first_k = k
                        r["pol"][(D, cap, cond, recal)] = dict(q=q, c=c, pnl=q * y - c, k1=first_k, fills=fills)
            # H776 : réapparition
            q0 = LH.acheter(E[t0 + EXEC], X, a0m, 1e9)[0]
            dis = None; ret = {}
            for j in range(1, 201):
                t = t0 + 25 * j; L = E[t]
                qa = LH.acheter(L, X, a0m, 1e9)[0]
                if dis is None:
                    if qa < 1: dis = 25 * j
                    continue
                for cap in (0, 10, 20):
                    if cap in ret: continue
                    qq = LH.acheter(L, X, a0m + cap, 1e9)[0]
                    if qq >= 1:
                        v = LH.vendeurs(L, X); prof = sum(sz for p, sz in v if p <= v[0][0] + 30) if v else 0
                        pr = Mo.proba(t / 1000); f = None if pr is None else LH.fair_regle(s["nom"], pr)
                        ret[cap] = dict(ms=25 * j - dis, prix=v[0][0] / 1000 if v else None, q=qq, prof=prof, prob=None if f is None else (f if X == "Up" else 1 - f))
            r["disp"] = dis; r["ret"] = ret
            LIG.append(r)

    o = []; w = o.append
    par_cy = lambda X_: list({l["st"]: [m for m in X_ if m["st"] == l["st"]] for l in X_}.values())
    w("# Bot95 — R4 « retry engine », H776–H778 — PRÉLIMINAIRE (hors ligne)\n")
    w(f"Généré le {time.strftime('%d.%m.%Y %H:%M', time.gmtime())} UTC. {len(SIG)} signaux réglés sur {len(cycles)} cycles enregistrés à Dublin (avant le 13.10). "
      f"IC 90 % par rééchantillonnage de cycles ; 1re moitié = cycles < {time.strftime('%H:%M', time.gmtime(coupe))} UTC. Envoi à la décision puis toutes les 500 ms, "
      f"exécution 164 ms après chaque envoi, budget 50 $, frais preneur. Condition R4 : probabilité recalculée − prix − frais ≥ {MARGE}. "
      "Le fantôme R4 vivant (déployé à Dublin le 11.10 vers 15:30 UTC) donnera la mesure réellement hors échantillon.\n")
    BASE = (0, 0, False, False); R4 = (5, 20, True, True)
    def stat(k, X_=None):
        X_ = X_ or LIG; pn = [l["pol"][k]["pnl"] for l in X_]
        return dict(pnl=sum(pn), moy=float(np.mean(pn)), ci=ic(par_cy(X_), lambda s: float(np.mean([l["pol"][k]["pnl"] for l in s]))),
                    fills=sum(1 for l in X_ if l["pol"][k]["q"] > 0), q=sum(l["pol"][k]["q"] for l in X_), c=sum(l["pol"][k]["c"] for l in X_),
                    h1=float(np.mean([l["pol"][k]["pnl"] for l in X_ if l["st"] < coupe])), h2=float(np.mean([l["pol"][k]["pnl"] for l in X_ if l["st"] >= coupe])))
    def dd(k, X_):
        cum = np.cumsum([l["pol"][k]["pnl"] for l in sorted(X_, key=lambda l: l["s"]["tDecision"])])
        return float(np.max(np.maximum.accumulate(np.concatenate([[0], cum]))[1:] - cum)) if len(cum) else 0.0
    jack = lambda l, k: l["pol"][k]["q"] > 0 and l["y"] == 1 and l["pol"][k]["c"] / l["pol"][k]["q"] <= 0.25
    w("## 1. R4 contre Bot95 actuel et les relances demandées (livrables 1 à 6)\n")
    w("| Politique | Signaux remplis | Parts | Prix moyen | P&L ($) | / signal (IC 90 %) | P&L marginal vs Bot95 | 1re / 2e moitié | Drawdown | Jackpots | Offres récupérées | Nouveaux perdants |\n|---|---|---|---|---|---|---|---|---|---|---|---|")
    POL = [("Bot95 preneur immédiat (164 ms, prix du signal)", BASE), ("relance 5 s au prix initial", (5, 0, True, True)), ("relance 5 s, +1 c", (5, 10, True, True)),
           ("**R4 : relance 5 s, +2 c, recalcul**", R4), ("relance 5 s, +2 c, modèle figé", (5, 20, True, False)), ("relance 5 s, +2 c, sans condition", (5, 20, False, False))]
    b = stat(BASE)
    for nom, k in POL:
        s_ = stat(k); rec = [l for l in LIG if l["pol"][BASE]["q"] <= 0 and l["pol"][k]["q"] > 0]
        w(f"| {nom} | {s_['fills']} | {s_['q']:.0f} | {s_['c'] / s_['q'] if s_['q'] else 0:.3f} | {s_['pnl']:+.0f} | {s_['moy']:+.2f} [{s_['ci'][0]:+.2f} ; {s_['ci'][1]:+.2f}] | "
          f"{s_['pnl'] - b['pnl']:+.0f} | {s_['h1']:+.2f} / {s_['h2']:+.2f} | {dd(k, LIG):.0f} | {sum(1 for l in LIG if jack(l, k))} | {len(rec)} | {sum(1 for l in rec if l['y'] == 0)} |")
    # détail R4
    rec = [l for l in LIG if l["pol"][BASE]["q"] <= 0 and l["pol"][R4]["q"] > 0]
    plus = [l for l in LIG if l["pol"][R4]["q"] > l["pol"][BASE]["q"] + 1e-6]
    extra_q = sum(l["pol"][R4]["q"] - l["pol"][BASE]["q"] for l in plus); extra_c = sum(l["pol"][R4]["c"] - l["pol"][BASE]["c"] for l in plus)
    gm = {k: [] for k in ("R4", "base")}
    G = collections.defaultdict(list)
    for l in LIG: G[l["st"]].append(l["pol"][R4]["pnl"] - l["pol"][BASE]["pnl"])
    cm = ic(list(G.values()), lambda s: float(np.sum(s)) / max(1, len(s)))
    w(f"\n- **Offres récupérées** (Bot95 n'a rien eu, R4 a acheté) : {len(rec)} signaux ; gagnants {sum(1 for l in rec if l['y'] == 1)}, perdants {sum(1 for l in rec if l['y'] == 0)} ; "
      f"jackpots récupérés (gain à prix ≤ 0,25) : {sum(1 for l in rec if jack(l, R4))}.")
    w(f"- **Quantité récupérée** (parts achetées en plus de Bot95, tous signaux) : {extra_q:.0f} parts pour {extra_c:.0f} $ (**coût des relances**) ; résultat de ces parts : "
      f"{sum(l['pol'][R4]['pnl'] - l['pol'][BASE]['pnl'] for l in plus):+.0f} $.")
    lost = [l for l in LIG if l["pol"][BASE]["q"] > 0 and l["pol"][R4]["q"] < l["pol"][BASE]["q"] - 1e-6]
    w(f"- Signaux où R4 achète MOINS que Bot95 (la condition d'avantage recalculée refuse) : {len(lost)} ; P&L laissé : {sum(l['pol'][BASE]['pnl'] - l['pol'][R4]['pnl'] for l in lost):+.0f} $ "
      f"(gagnants {sum(1 for l in lost if l['y'] == 1)}, perdants {sum(1 for l in lost if l['y'] == 0)}).")
    w(f"- P&L marginal R4 − Bot95 par signal : {np.mean([x for v in G.values() for x in v]):+.2f} $, IC 90 % [{cm[0]:+.2f} ; {cm[1]:+.2f}].")
    vu = {}
    for l in LIG: vu.setdefault((l["st"], l["X"]), l)
    U = list(vu.values())
    for nom, k in (("Bot95", BASE), ("R4", R4)):
        s_ = stat(k, U); w(f"- Décisions uniques (1 par cycle et côté, {len(U)}) — {nom} : {s_['pnl']:+.0f} $, {s_['moy']:+.2f} / décision [{s_['ci'][0]:+.2f} ; {s_['ci'][1]:+.2f}].")
    w("")

    w("## 2. H778 — Résultats par durée de relance et par plafond (livrables 7, 8) — avec condition et recalcul\n")
    w("| Durée | +0 c | +1 c | +2 c | +3 c |\n|---|---|---|---|---|")
    for D in DUREES[1:]:
        cells = []
        for cap in PLAFONDS:
            s_ = stat((D, cap, True, True)); cells.append(f"{s_['pnl']:+.0f} $ ({s_['fills']} remplis ; 2e m. {s_['h2']:+.1f})")
        w(f"| {D} s | " + " | ".join(cells) + " |")
    w("\n| Une seule tentative (164 ms), sans condition | " + " | ".join(f"{stat((0, cap, False, False))['pnl']:+.0f} $" for cap in PLAFONDS) + " |")
    w("\nLecture : la grille est descriptive ; aucun paramètre n'est choisi sur elle (R4 = 5 s, +2 c fixé par Pitch avant la mesure).\n")

    w("## 3. Effet du recalcul du modèle (livrable 9)\n")
    w("| Durée / plafond | recalcul | modèle figé au signal | sans condition |\n|---|---|---|---|")
    for D, cap in ((1, 20), (2, 20), (5, 0), (5, 20)):
        w(f"| {D} s, +{cap // 10} c | {stat((D, cap, True, True))['pnl']:+.0f} $ | {stat((D, cap, True, False))['pnl']:+.0f} $ | {stat((D, cap, False, False))['pnl']:+.0f} $ |")
    pr = [(l["probs"][k] - l["s"]["modele"]) for l in LIG for k in range(1, 10) if l["probs"][k] is not None]
    w(f"\nDérive de la probabilité recalculée par rapport à celle du signal pendant les 5 s : médiane {np.median(pr):+.3f}, 10e/90e centiles {np.percentile(pr, 10):+.3f} / {np.percentile(pr, 90):+.3f}. "
      "(Modèle recalculé fidèle à ±0,005 pour ~3/4 des signaux.)\n")

    w("## 4. H776 — Réapparition des offres après disparition\n")
    D_ = [l for l in LIG if l["disp"] is not None]
    w(f"Offre au prix du signal disparue dans les 5 s : {len(D_)} / {len(LIG)} signaux.\n")
    w("| Retour | Signaux | Délai médian (ms) | Prix médian au retour | Quantité médiane | Profondeur médiane (≤ +3 c) | Probabilité recalculée médiane − prix | Taux de gain |\n|---|---|---|---|---|---|---|---|")
    for cap in (0, 10, 20):
        R_ = [l for l in D_ if cap in l["ret"]]
        if not R_: w(f"| ≤ prix + {cap // 10} c | 0 | — | — | — | — | — | — |"); continue
        e = [l["ret"][cap]["prob"] - l["ret"][cap]["prix"] for l in R_ if l["ret"][cap]["prob"] is not None and l["ret"][cap]["prix"] is not None]
        w(f"| ≤ prix + {cap // 10} c | {len(R_)} | {np.median([l['ret'][cap]['ms'] for l in R_]):.0f} | {np.median([l['ret'][cap]['prix'] for l in R_ if l['ret'][cap]['prix']]):.2f} | "
          f"{np.median([l['ret'][cap]['q'] for l in R_]):.0f} | {np.median([l['ret'][cap]['prof'] for l in R_]):.0f} | {np.median(e) if e else float('nan'):+.3f} | {100 * np.mean([l['y'] for l in R_]):.0f} % |")
    NR = [l for l in D_ if 20 not in l["ret"]]
    w(f"| jamais revenue (≤ +2 c) | {len(NR)} | — | — | — | — | — | {100 * np.mean([l['y'] for l in NR]) if NR else float('nan'):.0f} % |\n")

    w("## 5. H777 — Relance systématique contre conditionnelle\n")
    # probabilité de réapparition (≤ +2 c en 5 s) apprise sur la 1re moitié par tranche de prix, appliquée sur la 2e
    tr = [l for l in D_ if l["st"] < coupe]; te = [l for l in LIG if l["st"] >= coupe]
    tranche = lambda a: 0 if a < 0.15 else (1 if a < 0.30 else 2)
    pret = {t: (np.mean([20 in l["ret"] for l in tr if tranche(l["a0"]) == t]) if any(tranche(l["a0"]) == t for l in tr) else 0.5) for t in range(3)}
    w(f"Probabilité de réapparition (≤ +2 c en 5 s) apprise sur la 1re moitié : prix < 0,15 → {pret[0]:.2f} ; 0,15–0,30 → {pret[1]:.2f} ; ≥ 0,30 → {pret[2]:.2f}.\n")
    def cond_reap(l):
        return l["pol"][R4] if pret[tranche(l["a0"])] >= 0.5 else l["pol"][(0, 20, False, False)]
    w("| Politique (2e moitié seulement) | Remplis | P&L ($) | / signal | IC 90 % |\n|---|---|---|---|---|")
    for nom, f in (("Bot95 immédiat", lambda l: l["pol"][BASE]), ("relance systématique 5 s +2 c (sans condition)", lambda l: l["pol"][(5, 20, False, False)]),
                   ("relance conditionnelle à l'avantage net (R4)", lambda l: l["pol"][R4]), ("relance si réapparition probable (≥ 0,5)", cond_reap)):
        pn = [f(l)["pnl"] for l in te]
        c_ = ic(par_cy(te), lambda s: float(np.mean([f(l)["pnl"] for l in s])))
        w(f"| {nom} | {sum(1 for l in te if f(l)['q'] > 0)} | {sum(pn):+.0f} | {np.mean(pn):+.2f} | [{c_[0]:+.2f} ; {c_[1]:+.2f}] |")
    w("")

    w("## 6. Comparaison avec M4 et M8 (mêmes cycles, fantômes vivants)\n")
    cyc_mk = sorted({x["start"] for x in MK} & set(cycles))
    if cyc_mk:
        lc = [l for l in LIG if l["st"] in set(cyc_mk)]
        w(f"{len(cyc_mk)} cycles communs.\n\n| Moteur | P&L ($) |\n|---|---|")
        for fam in ("M4", "M8"):
            X_ = [x for x in MK if x["variante"].split()[0] == fam and x["start"] in set(cyc_mk)]
            w(f"| {fam} (vivant, prudent / proportionnel) | {sum(x['resultat']['prudent'] for x in X_):+.0f} / {sum(x['resultat']['proportionnel'] for x in X_):+.0f} |")
        w(f"| Bot95 immédiat (simulé) | {sum(l['pol'][BASE]['pnl'] for l in lc):+.0f} |\n| R4 (simulé) | {sum(l['pol'][R4]['pnl'] for l in lc):+.0f} |\n")

    w("## 7. Verdict statistique (livrable 10)\n")
    s0, s4 = stat(BASE), stat(R4)
    sig = cm[0] > 0
    w(f"- R4 {s4['pnl']:+.0f} $ contre Bot95 {s0['pnl']:+.0f} $ ; différence {s4['pnl'] - s0['pnl']:+.0f} $ ; IC 90 % de la différence par signal [{cm[0]:+.2f} ; {cm[1]:+.2f}] → "
      f"**{'amélioration significative sur cet échantillon' if sig else 'amélioration NON démontrée (l’IC contient 0)'}**.")
    w(f"- 1re moitié : Bot95 {s0['h1']:+.2f} / R4 {s4['h1']:+.2f} par signal ; 2e moitié : Bot95 {s0['h2']:+.2f} / R4 {s4['h2']:+.2f}.")
    w("- Quelle que soit l'issue ici, seule la mesure du fantôme R4 vivant sur des cycles nouveaux (et la période réservée du 13.10) compte comme validation.\n")
    w("## Limites\n- Une journée, peu de cycles, résultats portés par quelques gros gains.\n- Modèle recalculé hors ligne (fidèle à ±0,005 pour ~3/4 des signaux).\n"
      "- Carnet suivi à ±3 c du meilleur prix entre deux photos complètes.\n- La relance n'affecte pas le carnet (fantôme) : en réel, nos achats déplaceraient le prix.\n")
    open(SORTIE, "w").write("\n".join(o)); print("\n".join(o))


if __name__ == "__main__":
    main()
