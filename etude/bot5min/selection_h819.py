"""BOT95 — H819 / H820 / H821 (Pitch, 11.10.2026 21:53). Hors ligne ; aucun ordre ; H816, R4, fantômes inchangés ; période réservée non lue.
PROTOCOLE VERSIONNÉ AVANT CALCUL (ce fichier tel que committé).
Univers : décisions uniques (premier signal par cycle et côté, tous prix) sur les cycles enregistrés à Dublin ; sous-ensemble H816 (0,20–0,50).
Exécution : 20 $ au prix ≤ a0, carnet de Dublin à décision + 164 ms, frais 0,07·p·(1−p) ; conservation jusqu'au règlement.
Variables (toutes connues à la décision) : probabilité Bot95 (modèle de la règle), prix payé, milieu Polymarket, temps restant, distance au prix à battre
(Chainlink, en $ et en écarts-types), tendance BTC 10 s et 30 s (Bybit), volatilité 60 s, écart modèle − marché, profondeur vendeuse ≤ a0 ($),
déséquilibre acheteurs / vendeurs, flux preneur 10 s vers notre côté, déclencheur.
H819 calibration (Brier, log loss) Bot95 / marché / combinaison logistique apprise sur la 1re moitié, mesurée sur la 2e ; aussi sur toutes les décisions
uniques de bot95/rapide.json (Bot95 contre prix payé a0).
H820 gagnants contre perdants : effet de chaque variable à prix et temps restant égaux (logistique), IC par cycles, correction de Bonferroni.
H821 règles simples d'exclusion « une variable, un seuil » (seuils = terciles de l'apprentissage, sens libre) choisies sur l'apprentissage,
mesurées une fois sur le test ; jackpot = gain réalisé ≥ 2× la mise.
Usage : python3 etude/bot5min/selection_h819.py dossier_cycles → etude/bot5min/resultat_selection_h819.md"""
import json, os, sys, glob, math, time, collections, bisect
import numpy as np

ICI = os.path.dirname(os.path.abspath(__file__)); RACINE = os.path.abspath(os.path.join(ICI, "..", ".."))
sys.path.insert(0, ICI)
import latence_h766 as LH, modele_dublin as MD, queue_race_phase12 as Q, contreparties_h724 as CH
HORS_ECH = 1791849600; SORTIE = os.path.join(ICI, "resultat_selection_h819.md")
MISE = 20.0; EXEC = 164
fee = lambda p: 0.07 * p * (1 - p)
rng = np.random.default_rng(819)
lg = lambda p: math.log(min(max(p, 1e-3), 1 - 1e-3) / (1 - min(max(p, 1e-3), 1 - 1e-3)))


def acheter(L, X, lim, mise):
    q = c = 0.0
    for p, sz in LH.vendeurs(L, X):
        if p > lim: break
        pp = p / 1000; u = pp + fee(pp); k = min(sz, (mise - c) / u)
        if k <= 1e-9: break
        q += k; c += k * u
    return q, c


def ic(G, fn, n=2000, alpha=0.10):
    G = [g for g in G if g]
    if len(G) < 3: return (float("nan"), float("nan"))
    v = []
    for _ in range(n):
        try:
            r = fn([x for i in rng.integers(0, len(G), len(G)) for x in G[i]])
            if r is not None and not math.isnan(r): v.append(r)
        except Exception: pass
    return (float(np.percentile(v, 100 * alpha / 2)), float(np.percentile(v, 100 * (1 - alpha / 2)))) if v else (float("nan"), float("nan"))


def brier(p, y): return float(np.mean((np.asarray(p) - np.asarray(y)) ** 2))
def logloss(p, y):
    p = np.clip(np.asarray(p, float), 1e-3, 1 - 1e-3); y = np.asarray(y, float); return float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))


VARS = ["ecart_mm", "dist_sigma", "dist_usd", "tend10", "tend30", "vol60", "prof_a", "desequ", "flux10", "poly"]
NOMS = {"ecart_mm": "écart modèle − marché", "dist_sigma": "distance au prix à battre (écarts-types)", "dist_usd": "distance au prix à battre ($, signée)",
        "tend10": "tendance BTC 10 s (pb, vers nous)", "tend30": "tendance BTC 30 s (pb)", "vol60": "volatilité BTC 60 s (pb)", "prof_a": "profondeur vendeuse ≤ a0 ($)",
        "desequ": "déséquilibre acheteurs / vendeurs", "flux10": "flux preneur 10 s vers nous (parts)", "poly": "déclenché par le carnet (1/0)"}


def main():
    dossier = sys.argv[1]
    F = {int(os.path.basename(f).split(".")[0]): f for f in glob.glob(os.path.join(dossier, "**", "*.json.gz"), recursive=True)}
    F = {k: v for k, v in F.items() if k < HORS_ECH}
    ALL = sorted([s for s in json.load(open(os.path.join(RACINE, "bot95", "rapide.json")))["signaux"] if s.get("gagnant") and s["start"] < HORS_ECH],
                 key=lambda s: (s["start"], s["cote"], s["tDecision"], s["nom"]))
    UNI = {}
    for s in ALL: UNI.setdefault((s["start"], s["cote"]), s)
    UNI_ALL = list(UNI.values())
    D = [s for s in UNI_ALL if s["start"] in F]
    cycles = sorted({s["start"] for s in D}); coupe = cycles[len(cycles) // 2]
    R = []
    for st in cycles:
        cy = LH.Cycle(F[st]); S_ = Q.rejouer(cy.C)["serie"]
        prev = F.get(st - 300); ex = MD.charger_ex([f for f in (prev, F[st]) if f]); Mo = MD.Modele(ex, cy.strike, st + 300)
        for s in [x for x in D if x["start"] == st]:
            t0 = s["tDecision"]; X = s["cote"]; sens = 1 if X == "Up" else -1; a0m = int(round(s["a0"] * 1000)); y = 1.0 if s["gagne"] else 0.0
            E = cy.etats([t0, t0 + EXEC]); L0 = E[t0]
            q, c = acheter(E[t0 + EXEC], X, a0m, MISE)
            i = np.searchsorted(S_[:, 0], t0, "right") - 1
            mid = None
            if i >= 0 and not np.isnan(S_[i, 1]) and not np.isnan(S_[i, 3]): m = (S_[i, 1] + S_[i, 3]) / 2000; mid = m if X == "Up" else 1 - m
            def px(src, t):
                r = Mo.dernier(src, t / 1000); return r[1] if r else None
            p0, p10, p30 = px("perp", t0), px("perp", t0 - 10000), px("perp", t0 - 30000)
            cl = px("cl", t0)
            ser = [px("perp", t0 - 1000 * k) for k in range(0, 61, 2)]; ser = [v for v in ser if v]
            rets = np.diff(np.log(ser)) if len(ser) > 3 else np.array([0.0])
            vol = float(np.std(rets) * 1e4); tl = s["restant_s"]
            dist = (cl - cy.strike) * sens if (cl and cy.strike) else None
            sig_ = (vol / 1e4) * (cl or 1) * math.sqrt(max(tl, 1) / 2) if cl else None
            vv = LH.vendeurs(L0, X) if L0 else []; bb = LH.acheteurs(L0, X) if L0 else []
            pa = sum(sz * p / 1000 for p, sz in vv if p <= a0m); db = sum(sz for p, sz in bb[:3]); da = sum(sz for p, sz in vv[:3])
            j0 = bisect.bisect_left(cy.trT, t0 - 10000); j1 = bisect.bisect_left(cy.trT, t0)
            # flux : achats preneurs consommant les vendeurs de notre côté (+) moins ventes consommant nos acheteurs (−)
            side_a = 1 if X == "Up" else 0
            fl = sum((x[3] if x[1] == side_a else -x[3]) for x in cy.tr[j0:j1])
            R.append(dict(st=st, s=s, y=y, X=X, a0=s["a0"], mod=s["modele"], mid=mid, q=q, c=c, rest=tl, h816=0.20 <= s["a0"] <= 0.50,
                          v=dict(ecart_mm=(s["modele"] - mid) if mid is not None else 0.0, dist_sigma=(dist / sig_) if (dist is not None and sig_) else 0.0,
                                 dist_usd=dist or 0.0, tend10=((p0 - p10) / p10 * 1e4 * sens) if (p0 and p10) else 0.0,
                                 tend30=((p0 - p30) / p30 * 1e4 * sens) if (p0 and p30) else 0.0, vol60=vol, prof_a=pa,
                                 desequ=(db - da) / max(db + da, 1), flux10=fl, poly=1.0 if s["declencheur"] == "poly" else 0.0)))
    tr = [x for x in R if x["st"] < coupe]; te = [x for x in R if x["st"] >= coupe]
    par_cy = lambda X_: list({x["st"]: [m for m in X_ if m["st"] == x["st"]] for x in X_}.values())
    pnl = lambda x: x["q"] * x["y"] - x["c"]
    o = []; w = o.append
    w("# Bot95 — H819 / H820 / H821 : calibration, gagnants contre perdants, préservation des jackpots — PRÉLIMINAIRE (hors ligne)\n")
    w(f"Généré le {time.strftime('%d.%m.%Y %H:%M', time.gmtime())} UTC. Décisions uniques sur cycles Dublin : {len(R)} ({sum(x['h816'] for x in R)} dans H816) sur {len(cycles)} cycles ; "
      f"apprentissage {len(tr)} / test {len(te)} (coupure {time.strftime('%H:%M', time.gmtime(coupe))} UTC). Exécution 20 $, 164 ms. Aucun ordre ; H816, R4, fantômes inchangés.\n")

    # ===== H819
    w("## 1. H819 — Calibration au règlement\n")
    w("**A. Toutes les décisions uniques de bot95/rapide.json (cycles sans carnet compris) : probabilité Bot95 contre prix payé a0**\n")
    UA = [s for s in UNI_ALL]
    ya = [1.0 if s["gagne"] else 0.0 for s in UA]
    w(f"{len(UA)} décisions sur {len({s['start'] for s in UA})} cycles. Brier : Bot95 {brier([s['modele'] for s in UA], ya):.3f} ; prix a0 {brier([s['a0'] for s in UA], ya):.3f}. "
      f"Log loss : Bot95 {logloss([s['modele'] for s in UA], ya):.3f} ; prix a0 {logloss([s['a0'] for s in UA], ya):.3f}.\n")
    w("| Tranche de probabilité | Décisions | Bot95 moyen | Prix a0 moyen | Victoire observée |\n|---|---|---|---|---|")
    for lo, hi in ((0, .2), (.2, .3), (.3, .4), (.4, .5), (.5, .7), (.7, 1.01)):
        Z = [s for s in UA if lo <= s["modele"] < hi]
        if Z: w(f"| Bot95 {lo:.1f}–{min(hi, 1):.1f} | {len(Z)} | {np.mean([s['modele'] for s in Z]):.2f} | {np.mean([s['a0'] for s in Z]):.2f} | {100 * np.mean([s['gagne'] for s in Z]):.0f} % |")
    w("\n| Temps restant | Décisions | Bot95 moyen | Prix a0 moyen | Victoire observée | Brier Bot95 / prix |\n|---|---|---|---|---|---|")
    for lo, hi in ((0, 60), (60, 120), (120, 180), (180, 240), (240, 301)):
        Z = [s for s in UA if lo <= s["restant_s"] < hi]
        if Z:
            yz = [1.0 if s["gagne"] else 0.0 for s in Z]
            w(f"| {lo}–{hi} s | {len(Z)} | {np.mean([s['modele'] for s in Z]):.2f} | {np.mean([s['a0'] for s in Z]):.2f} | {100 * np.mean(yz):.0f} % | {brier([s['modele'] for s in Z], yz):.3f} / {brier([s['a0'] for s in Z], yz):.3f} |")
    w("\n**B. Cycles Dublin : Bot95 / milieu Polymarket / prix payé / combinaison (logistique sur logit Bot95 + logit milieu, apprise sur l'apprentissage)**\n")
    RM = [x for x in R if x["mid"] is not None]
    trm = [x for x in RM if x["st"] < coupe]; tem = [x for x in RM if x["st"] >= coupe]
    Xt = np.array([[lg(x["mod"]), lg(x["mid"])] for x in trm]); b = CH.ajuster(Xt, np.array([x["y"] for x in trm]), 0.5)
    comb = lambda Z: CH.predire(b, np.array([[lg(x["mod"]), lg(x["mid"])] for x in Z]))
    w("| Estimateur | Brier test | Log loss test | Brier apprentissage |\n|---|---|---|---|")
    for nom, f in (("Bot95", lambda Z: [x["mod"] for x in Z]), ("milieu Polymarket", lambda Z: [x["mid"] for x in Z]), ("prix payé a0", lambda Z: [x["a0"] for x in Z]),
                   ("combinaison (apprise)", comb)):
        w(f"| {nom} | {brier(f(tem), [x['y'] for x in tem]):.3f} | {logloss(f(tem), [x['y'] for x in tem]):.3f} | {brier(f(trm), [x['y'] for x in trm]):.3f} |")
    w(f"\nPoids de la combinaison (logit) : constante {b[0]:+.2f}, Bot95 {b[1]:+.2f}, milieu {b[2]:+.2f}. Test : {len(tem)} décisions — petit échantillon.\n")

    # ===== H820
    w("## 2. H820 — Gagnants contre perdants, à prix et temps restant égaux\n")
    w(f"Logistique « gagné ~ logit(prix) + temps restant + variable », variable standardisée, IC 90 % par cycles et IC corrigé de Bonferroni ({len(VARS)} variables). Toutes les décisions Dublin ({len(R)}).\n")
    w("| Variable | Gagnants (médiane) | Perdants (médiane) | Coefficient | IC 90 % | IC corrigé | Verdict |\n|---|---|---|---|---|---|---|")
    yv = np.array([x["y"] for x in R]); a = 0.10 / len(VARS)
    for k in VARS:
        vals = np.array([x["v"][k] for x in R]); m_, s_ = vals.mean(), vals.std() or 1
        def fit(Z):
            Xz = np.array([[lg(x["a0"]), x["rest"] / 300, (x["v"][k] - m_) / s_] for x in Z]); return CH.ajuster(Xz, np.array([x["y"] for x in Z]), 0.5)[3]
        b3 = fit(R); c1 = ic(par_cy(R), fit, 600); c2 = ic(par_cy(R), fit, 600, alpha=a)
        verdict = "significatif (corrigé)" if (c2[0] > 0 or c2[1] < 0) else ("indice non corrigé" if (c1[0] > 0 or c1[1] < 0) else "rien")
        w(f"| {NOMS[k]} | {np.median([x['v'][k] for x in R if x['y'] == 1]):+.2f} | {np.median([x['v'][k] for x in R if x['y'] == 0]):+.2f} | {b3:+.2f} | "
          f"[{c1[0]:+.2f} ; {c1[1]:+.2f}] | [{c2[0]:+.2f} ; {c2[1]:+.2f}] | {verdict} |")

    # ===== H821
    w("\n## 3. H821 — Règles simples d'exclusion qui épargnent les jackpots\n")
    REG = []
    for k in VARS:
        qs = np.percentile([x["v"][k] for x in tr], [33.3, 66.7])
        for thr in sorted(set(qs)):
            REG.append((k, ">", thr)); REG.append((k, "<", thr))
    exclu = lambda x, r: (x["v"][r[0]] > r[2]) if r[1] == ">" else (x["v"][r[0]] < r[2])
    jack = lambda x: pnl(x) >= 2 * MISE
    def score(Z, r):
        garde = [x for x in Z if not exclu(x, r)]
        if len(garde) < 0.5 * len(Z) or any(jack(x) and exclu(x, r) for x in Z): return -1e9      # règle admissible : ne supprime aucun jackpot de l'apprentissage, garde ≥ 50 %
        return sum(pnl(x) for x in garde) - sum(pnl(x) for x in Z)
    best = max(REG, key=lambda r: score(tr, r))
    w(f"{len(REG)} règles candidates (une variable, seuil = tercile de l'apprentissage, deux sens). Admissibles : ne suppriment aucun jackpot de l'apprentissage et gardent ≥ 50 % des signaux. "
      f"**Retenue sur l'apprentissage : exclure si {NOMS[best[0]]} {best[1]} {best[2]:+.3f}** (gain d'apprentissage {score(tr, best):+.0f} $).\n")
    w("| Échantillon | Politique | Signaux gardés | Perdants évités | Gagnants perdus | Jackpots perdus | P&L ($) | Marginal vs H816/base ($) | IC 90 % du marginal (par signal) | Drawdown | 5 meilleurs / total |\n|---|---|---|---|---|---|---|---|---|---|---|")
    def ligne(lab, Z, r):
        garde = [x for x in Z if r is None or not exclu(x, r)]; ex_ = [x for x in Z if r is not None and exclu(x, r)]
        P = sum(pnl(x) for x in garde); base = sum(pnl(x) for x in Z)
        cm = ic(par_cy(Z), lambda z: float(np.mean([(0 if (r is not None and exclu(x, r)) else pnl(x)) - pnl(x) for x in z]))) if r is not None else (0, 0)
        cum = np.cumsum([pnl(x) for x in sorted(garde, key=lambda x: x["s"]["tDecision"])]); dd = float(np.max(np.maximum.accumulate(np.concatenate([[0], cum]))[1:] - cum)) if len(cum) else 0
        top = sorted([pnl(x) for x in garde], reverse=True)[:5]
        w(f"| {lab} | {'base' if r is None else 'avec la règle'} | {len(garde)} / {len(Z)} | {sum(1 for x in ex_ if x['y'] == 0)} | {sum(1 for x in ex_ if x['y'] == 1)} | {sum(1 for x in ex_ if jack(x))} | "
          f"{P:+.0f} | {P - base:+.0f} | [{cm[0]:+.2f} ; {cm[1]:+.2f}] | {dd:.0f} | {100 * sum(top) / P if P > 0 else float('nan'):.0f} % |")
    for lab, Z in (("TEST — toutes", te), ("TEST — H816", [x for x in te if x["h816"]]), ("apprentissage — toutes", tr)):
        ligne(lab, Z, None); ligne(lab, Z, best)
    # meilleures règles par variable (description, apprentissage) pour transparence
    w("\n**Les 5 meilleures règles sur l'apprentissage et leur résultat sur le test** (lecture : un écart apprentissage → test = sur-apprentissage)\n")
    w("| Règle | Gain apprentissage ($) | Gain test ($) |\n|---|---|---|")
    for r in sorted(REG, key=lambda r: -score(tr, r))[:5]:
        g_te = sum(pnl(x) for x in te if not exclu(x, r)) - sum(pnl(x) for x in te)
        w(f"| exclure si {NOMS[r[0]]} {r[1]} {r[2]:+.3f} | {score(tr, r):+.0f} | {g_te:+.0f} |")
    w("\n## 4. Verdict\n- Une variante future n'est proposée que si la règle retenue améliore le P&L sur le TEST avec un IC par cycles > 0, sans perdre de jackpot.\n")
    w("## Limites\n- Une journée ; ~40 décisions de test : très faible puissance.\n- Modèle Bot95 = probabilité enregistrée au signal ; milieu Polymarket reconstruit (±3 c, photos 10 s).\n")
    open(SORTIE, "w").write("\n".join(o)); print("\n".join(o))


if __name__ == "__main__":
    main()
