"""BOT95 — Test de robustesse (Pitch, 11.10.2026 21:25 ; appelé « H811 » par Pitch, renommé H816 pour ne pas le confondre avec l'étude
d'annulation H811). PROTOCOLE FIGÉ AVANT TOUT RÉSULTAT (ce fichier, tel que committé, est le pré-enregistrement) :
  1. Univers : tous les signaux Bot95 réglés (bot95/rapide.json), toutes variantes confondues.
  2. Prix d'entrée : seulement les signaux dont le prix vu a0 est entre 0,20 et 0,50 $ INCLUS.
  3. Une seule décision par cycle et par côté : parmi les signaux admissibles (étape 2) du même cycle et du même côté, le PREMIER par heure de
     décision (tDecision) ; égalité parfaite → ordre alphabétique du nom de variante.
  4. Mise identique : 20 $ par décision (coût frais compris), quel que soit le prix.
  5. Exécution : ordre preneur limité au prix a0, exécuté contre le carnet enregistré à Dublin à décision + d ms (d = 164 ; 200, 250, 500 en
     diagnostic seulement) ; seulement la quantité réellement affichée ≤ a0 ; frais preneur 0,07·p·(1−p) ; rien si l'offre a disparu.
  6. Aucune relance, aucun plafond au-dessus de a0, aucun seuil ajusté après observation.
  7. Comparaison : stratégie actuelle (tous les signaux, 50 $ par signal, même modèle d'exécution) sur les mêmes cycles.
  8. Validation : période réservée (≥ 13.10.2026 00:00 UTC), mêmes paramètres, lancée seulement avec --hors-echantillon.
Mesures : P&L, P&L par $ engagé, P&L par jeton, décisions exécutées, taux de gain, médiane, part des 5 meilleures, drawdown,
IC 90 % par rééchantillonnage de CYCLES, moitiés chronologiques. Hors ligne ; aucun ordre ; R4 et fantômes inchangés.
Usage : python3 etude/bot5min/robustesse_bot95.py dossier_cycles [--hors-echantillon] → etude/bot5min/resultat_robustesse_bot95[_hors_echantillon].md"""
import json, os, sys, glob, math, time, collections
import numpy as np

ICI = os.path.dirname(os.path.abspath(__file__)); RACINE = os.path.abspath(os.path.join(ICI, "..", ".."))
sys.path.insert(0, ICI)
import latence_h766 as LH
HORS_ECH = 1791849600; HE = "--hors-echantillon" in sys.argv
SORTIE = os.path.join(ICI, "resultat_robustesse_bot95" + ("_hors_echantillon" if HE else "") + ".md")
PMIN, PMAX, MISE = 0.20, 0.50, 20.0
DELAIS = (164, 200, 250, 500)
fee = lambda p: 0.07 * p * (1 - p)
rng = np.random.default_rng(816)
dans = lambda st: (st >= HORS_ECH) == HE


def acheter_mise(L, X, lim, mise):
    """parts et coût (frais compris) au prix ≤ lim, jusqu'à `mise` $"""
    q = c = 0.0
    for p, sz in LH.vendeurs(L, X):
        if p > lim: break
        pp = p / 1000; u = pp + fee(pp); k = min(sz, (mise - c) / u)
        if k <= 1e-9: break
        q += k; c += k * u
    return q, c


def decisions(SIG):
    adm = [s for s in SIG if PMIN - 1e-9 <= s["a0"] <= PMAX + 1e-9]
    adm.sort(key=lambda s: (s["start"], s["cote"], s["tDecision"], s["nom"]))
    D = {}
    for s in adm: D.setdefault((s["start"], s["cote"]), s)
    return list(D.values())


def ic(G, fn, n=3000):
    G = [g for g in G if g]
    if len(G) < 3: return (float("nan"), float("nan"))
    v = []
    for _ in range(n):
        try:
            r = fn([x for i in rng.integers(0, len(G), len(G)) for x in G[i]])
            if r is not None and not math.isnan(r): v.append(r)
        except Exception: pass
    return (float(np.percentile(v, 5)), float(np.percentile(v, 95))) if v else (float("nan"), float("nan"))


def stats(X_, cle):
    par_cy = list({x["st"]: [m for m in X_ if m["st"] == x["st"]] for x in X_}.values())
    ex = [x for x in X_ if x[cle][0] > 0]
    pn = [x[cle][0] * x["y"] - x[cle][1] for x in X_]
    tot = sum(pn); eng = sum(x[cle][1] for x in X_); jet = sum(x[cle][0] for x in X_)
    cum = np.cumsum([x[cle][0] * x["y"] - x[cle][1] for x in sorted(X_, key=lambda x: x["t0"])])
    dd = float(np.max(np.maximum.accumulate(np.concatenate([[0], cum]))[1:] - cum)) if len(cum) else 0.0
    top = sorted(pn, reverse=True)[:5]
    f_d = lambda z: sum(x[cle][0] * x["y"] - x[cle][1] for x in z) / max(sum(x[cle][1] for x in z), 1e-9)
    f_j = lambda z: sum(x[cle][0] * x["y"] - x[cle][1] for x in z) / max(sum(x[cle][0] for x in z), 1e-9)
    return dict(n=len(X_), ex=len(ex), tot=tot, pd=tot / eng if eng else float("nan"), pj=tot / jet if jet else float("nan"),
                icd=ic(par_cy, f_d), icj=ic(par_cy, f_j), g=np.mean([x["y"] for x in ex]) if ex else float("nan"),
                prix=np.mean([x[cle][1] / x[cle][0] for x in ex]) if ex else float("nan"), med=float(np.median(pn)) if pn else float("nan"),
                top5=100 * sum(top) / tot if tot > 0 else float("nan"), dd=dd, eng=eng, cyc=len(par_cy))


def main():
    dossier = sys.argv[1]
    F = {int(os.path.basename(f).split(".")[0]): f for f in glob.glob(os.path.join(dossier, "**", "*.json.gz"), recursive=True)}
    F = {k: v for k, v in F.items() if dans(k)}
    TOUS = [s for s in json.load(open(os.path.join(RACINE, "bot95", "rapide.json")))["signaux"] if s.get("gagnant") and dans(s["start"])]
    SIG = [s for s in TOUS if s["start"] in F]
    DEC = decisions(SIG)
    cycles = sorted({s["start"] for s in SIG}); coupe = cycles[len(cycles) // 2] if cycles else 0
    LIG_N = []; LIG_A = []
    for st in cycles:
        cy = LH.Cycle(F[st]); S = [s for s in SIG if s["start"] == st]
        E = cy.etats([s["tDecision"] + d for s in S for d in DELAIS])
        for s in S:
            a0m = int(round(s["a0"] * 1000)); y = 1.0 if s["gagne"] else 0.0; t0 = s["tDecision"]
            base = dict(st=st, y=y, t0=t0, a0=s["a0"])
            # stratégie actuelle : 50 $ par signal (budget de Dublin en parts : 50 / a0), au prix du signal
            x = dict(base); x.update({d: LH.acheter(E[t0 + d], s["cote"], a0m, 50.0 / s["a0"]) for d in DELAIS}); LIG_A.append(x)
            if s in DEC: x = dict(base); x.update({d: acheter_mise(E[t0 + d], s["cote"], a0m, MISE) for d in DELAIS}); LIG_N.append(x)
    o = []; w = o.append
    w(f"# Bot95 — Test de robustesse H816 ({'PÉRIODE RÉSERVÉE' if HE else 'avant le 13.10'}) — protocole figé\n")
    w(f"Généré le {time.strftime('%d.%m.%Y %H:%M', time.gmtime())} UTC. Cycles avec carnet Dublin : {len(cycles)} ; signaux réglés : {len(SIG)} ; "
      f"décisions du protocole (prix 0,20–0,50, une par cycle et côté, la première) : **{len(LIG_N)}** sur {len({x['st'] for x in LIG_N})} cycles. "
      f"Mise 20 $ par décision. IC 90 % par cycles. Aucun ordre ; R4 et fantômes inchangés.\n")
    ENT = ("| Stratégie | Délai | Décisions | Exécutées | Taux de gain | Prix moyen payé | P&L ($) | P&L par $ engagé (IC 90 %) | P&L par jeton (c, IC 90 %) | Médiane ($) | 5 meilleures / total | Drawdown ($) |\n"
           "|---|---|---|---|---|---|---|---|---|---|---|---|")
    def ligne(nom, X_, d):
        r = stats(X_, d)
        w(f"| {nom} | {d} ms{' (protocole)' if d == 164 else ' (diagnostic)'} | {r['n']} | {r['ex']} | {100 * r['g']:.0f} % | {r['prix']:.3f} | {r['tot']:+.0f} | "
          f"{100 * r['pd']:+.1f} % [{100 * r['icd'][0]:+.1f} ; {100 * r['icd'][1]:+.1f}] | {100 * r['pj']:+.1f} [{100 * r['icj'][0]:+.1f} ; {100 * r['icj'][1]:+.1f}] | "
          f"{r['med']:+.2f} | {r['top5']:.0f} % | {r['dd']:.0f} |")
    w("## 1. Résultat principal et sensibilité à la latence\n"); w(ENT)
    for d in DELAIS: ligne("protocole H816 (20 $, 0,20–0,50, 1 décision)", LIG_N, d)
    for d in DELAIS: ligne("stratégie actuelle (tous signaux, 50 $)", LIG_A, d)
    w("\n## 2. Stabilité chronologique (protocole, 164 ms)\n"); w(ENT)
    if cycles:
        ligne("1re moitié des cycles", [x for x in LIG_N if x["st"] < coupe], 164); ligne("2e moitié des cycles", [x for x in LIG_N if x["st"] >= coupe], 164)
    w("\n## 3. Contrôle sur tous les cycles (mesure directe de Dublin, sans reconstruction du carnet)\n")
    w("Achetable mesuré par Dublin au prix du signal à 100 / 250 / 500 ms (champ « apres », budget 50 $) ramené à une mise de 20 $ "
      "(si le coût Dublin dépasse 20 $, quantité réduite proportionnellement). Tous les cycles, y compris ceux sans fichier de carnet.\n")
    D2 = decisions(TOUS); L2 = []
    for s in D2:
        x = dict(st=s["start"], y=1.0 if s["gagne"] else 0.0, t0=s["tDecision"], a0=s["a0"])
        for d in ("100", "250", "500"):
            a = (s.get("apres") or {}).get(d) or {}; q_, c_ = a.get("q") or 0.0, a.get("c") or 0.0
            if c_ > MISE: q_, c_ = q_ * MISE / c_, MISE
            x[int(d)] = (q_, c_)
        L2.append(x)
    w(ENT.replace("| Délai |", "| Délai |"))
    for d in (100, 250, 500):
        r = stats(L2, d)
        w(f"| protocole, tous cycles | {d} ms | {r['n']} | {r['ex']} | {100 * r['g']:.0f} % | {r['prix']:.3f} | {r['tot']:+.0f} | "
          f"{100 * r['pd']:+.1f} % [{100 * r['icd'][0]:+.1f} ; {100 * r['icd'][1]:+.1f}] | {100 * r['pj']:+.1f} [{100 * r['icj'][0]:+.1f} ; {100 * r['icj'][1]:+.1f}] | "
          f"{r['med']:+.2f} | {r['top5']:.0f} % | {r['dd']:.0f} |")
    w(f"\n({len(D2)} décisions sur {len({x['st'] for x in L2})} cycles.)\n")
    w("## Lecture\n- Par $ engagé = rendement de la mise ; par jeton = gain moyen par part achetée (une mise fixe achète plus de jetons quand le prix est bas).\n"
      "- Fragilité : si le résultat devient nul ou négatif dès 200 ms, la stratégie est jugée extrêmement fragile, même si 164 ms est positif.\n"
      "- Le verdict se fera sur la période réservée (--hors-echantillon), mêmes paramètres, sans aucun ajustement.\n")
    open(SORTIE, "w").write("\n".join(o)); print("\n".join(o))


if __name__ == "__main__":
    main()
