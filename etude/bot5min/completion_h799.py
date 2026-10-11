"""BOT95 — H799 / H800 (Pitch, 11.10.2026 17:42) : compléter après un fill partiel. Hors ligne ; R4 vivant et fantômes gelés inchangés ; aucun ordre.
Période réservée (≥ 13.10) jamais lue. Seuils choisis UNIQUEMENT sur l'apprentissage (1re moitié des cycles), mesurés une fois sur le test (2e moitié).

Base commune (règles de R4) : 1re tentative à la décision, exécutée 164 ms plus tard, plafond prix + 2 c, probabilité recalculée − prix − frais ≥ 0,05,
budget 50 $. Complément = tentatives suivantes toutes les 500 ms pendant 5 s, seulement si la 1re tentative a eu un fill partiel.
  D   aucune relance          B0  compléter après tout fill partiel
  B1  compléter si la profondeur au signal (en $ au prix du signal, mesurée à Dublin) ≥ seuil (seuil choisi sur apprentissage)
  B2  à chaque relance : compléter si profondeur ≤ plafond à l'envoi ≥ P $ ET probabilité recalculée − meilleur prix − frais ≥ m (P, m choisis sur apprentissage)
H800 compléments plafonnés à 25 / 50 / 75 / 100 % du budget restant après le 1er fill (total toujours ≤ 50 $).
Reconstruction depuis le fantôme vivant R4 : chaque tentative y est enregistrée (heure, probabilité, plafond, meilleur vendeur et sa taille, parts, coût),
donc D, B0, B1, B2 et H800 se recalculent sans nouveau fantôme (approximation documentée pour H800 quand le fill de R4 était limité par le budget).
Usage : python3 etude/bot5min/completion_h799.py dossier_cycles → etude/bot5min/resultat_completion_h799.md"""
import json, os, sys, glob, math, time, itertools
import numpy as np

ICI = os.path.dirname(os.path.abspath(__file__)); RACINE = os.path.abspath(os.path.join(ICI, "..", ".."))
sys.path.insert(0, ICI)
import latence_h766 as LH, modele_dublin as MD
HORS_ECH = 1791849600; SORTIE = os.path.join(ICI, "resultat_completion_h799.md")
BUDGET = 50.0; CAP = 20; MARGE = 0.05
rng = np.random.default_rng(799)
SEUILS_B1 = (0, 10, 25, 50, 100, 200)                   # $ affichés au prix du signal
GRILLE_B2 = list(itertools.product((0, 10, 25, 50), (0.05, 0.10, 0.15, 0.20)))
FRACS = (0.25, 0.5, 0.75, 1.0)


def fee_f(mult): return lambda p: mult * 0.07 * p * (1 - p)


def acheter(L, X, lim, budget, fee):
    q = c = 0.0
    for p, sz in LH.vendeurs(L, X):
        if p > lim: break
        pp = p / 1000; u = pp + fee(pp); k = min(sz, (budget - c) / u)
        if k <= 1e-9: break
        q += k; c += k * u
    return q, c


def limite(prob, a0m, fee, marge=MARGE):
    lim = a0m + CAP
    if prob is None: return -1
    while lim > 5 and prob - lim / 1000 - fee(lim / 1000) < marge: lim -= 10
    return lim


def ic(G, fn, n=2000, alpha=0.10):
    G = [g for g in G if g]
    if len(G) < 3: return (float("nan"), float("nan"))
    v = [fn([x for i in rng.integers(0, len(G), len(G)) for x in G[i]]) for _ in range(n)]
    return (float(np.percentile(v, 100 * alpha / 2)), float(np.percentile(v, 100 * (1 - alpha / 2))))


def simuler(E, t0, X, a0m, probs, exec_ms, fee, regle, frac=1.0, b2=None):
    """rend (parts 1re, coût 1re, parts compl., coût compl.) ; regle(premier_q) → compléter ?"""
    lim0 = limite(probs[0], a0m, fee)
    q1, c1 = acheter(E[t0 + exec_ms], X, lim0, BUDGET, fee) if lim0 > 0 else (0.0, 0.0)
    qc = cc = 0.0
    if q1 > 0 and BUDGET - c1 > 0.01 and regle():
        plaf = frac * (BUDGET - c1)
        for k in range(1, 10):
            if plaf - cc <= 0.01: break
            pr = probs[k]
            if b2 is not None:
                P, m = b2; Ls = E[t0 + 500 * k]
                v = LH.vendeurs(Ls, X)
                if pr is None or not v: continue
                prof = sum(sz * p / 1000 for p, sz in v if p <= a0m + CAP)
                best = v[0][0] / 1000
                if prof < P or pr - best - fee(best) < m: continue
            lim = limite(pr, a0m, fee)
            if lim <= 0: continue
            dq, dc = acheter(E[t0 + 500 * k + exec_ms], X, lim, plaf - cc, fee); qc += dq; cc += dc
    return q1, c1, qc, cc


def main():
    dossier = sys.argv[1]
    F = {int(os.path.basename(f).split(".")[0]): f for f in glob.glob(os.path.join(dossier, "**", "*.json.gz"), recursive=True)}
    F = {k: v for k, v in F.items() if k < HORS_ECH}
    SIG = sorted([s for s in json.load(open(os.path.join(RACINE, "bot95", "rapide.json")))["signaux"] if s.get("gagnant") and s["start"] in F and s["start"] < HORS_ECH], key=lambda s: s["tDecision"])
    cycles = sorted({s["start"] for s in SIG}); coupe = cycles[len(cycles) // 2]
    LIG = []
    POL = {"D": None, "B0": None}
    for th in SEUILS_B1: POL[f"B1≥{th}$"] = th
    for g in GRILLE_B2: POL[f"B2 P≥{g[0]}$ m≥{g[1]:.2f}"] = g
    for fr in FRACS: POL[f"H800 {int(fr * 100)} %"] = fr
    for st in cycles:
        cy = LH.Cycle(F[st]); prev = F.get(st - 300)
        Mo = MD.Modele(MD.charger_ex([f for f in (prev, F[st]) if f]), cy.strike, st + 300)
        S = [s for s in SIG if s["start"] == st]
        inst = []
        for s in S:
            t0 = s["tDecision"]; inst += [t0 + 500 * k + e for k in range(10) for e in (0, 164, 250, 500)]
        E = cy.etats(inst)
        for s in S:
            t0 = s["tDecision"]; X = s["cote"]; a0m = int(round(s["a0"] * 1000)); y = 1.0 if s["gagne"] else 0.0
            probs = []
            for k in range(10):
                p = Mo.proba((t0 + 500 * k) / 1000)
                f = None if p is None else LH.fair_regle(s["nom"], p); probs.append(None if f is None else (f if X == "Up" else 1 - f))
            prof0 = (s.get("achetable0") or {}).get("q", 0) * s["a0"]          # $ affichés au prix du signal (Dublin), plafonné par le budget
            prof0 = (s.get("q0") or 0) * s["a0"]                                 # profondeur affichée au meilleur vendeur au signal (non plafonnée)
            r = dict(s=s, st=st, y=y, prof0=prof0, res={})
            fee1 = fee_f(1.0)
            for nom, prm in POL.items():
                if nom == "D": regle, fr, b2 = (lambda: False), 1.0, None
                elif nom == "B0": regle, fr, b2 = (lambda: True), 1.0, None
                elif nom.startswith("B1"): regle, fr, b2 = (lambda th=prm: prof0 >= th), 1.0, None
                elif nom.startswith("B2"): regle, fr, b2 = (lambda: True), 1.0, prm
                else: regle, fr, b2 = (lambda: True), prm, None
                r["res"][nom] = simuler(E, t0, X, a0m, probs, 164, fee1, regle, fr, b2)
            # sensibilité frais / latence pour D et B0
            for mult in (1.5, 2.0):
                for nom, rg in (("D", lambda: False), ("B0", lambda: True)):
                    r["res"][f"{nom} frais ×{mult}"] = simuler(E, t0, X, a0m, probs, 164, fee_f(mult), rg)
            for ex in (250, 500):
                for nom, rg in (("D", lambda: False), ("B0", lambda: True)):
                    r["res"][f"{nom} latence {ex} ms"] = simuler(E, t0, X, a0m, probs, ex, fee1, rg)
            LIG.append(r)
    par_cy = lambda X_: list({l["st"]: [m for m in X_ if m["st"] == l["st"]] for l in X_}.values())
    tr = [l for l in LIG if l["st"] < coupe]; te = [l for l in LIG if l["st"] >= coupe]
    pn = lambda l, k: (l["res"][k][0] + l["res"][k][2]) * l["y"] - l["res"][k][1] - l["res"][k][3]
    pc = lambda l, k: l["res"][k][2] * l["y"] - l["res"][k][3]                # P&L des compléments seuls
    # sélection sur apprentissage
    best_b1 = max([k for k in POL if k.startswith("B1")], key=lambda k: sum(pn(l, k) for l in tr))
    best_b2 = max([k for k in POL if k.startswith("B2")], key=lambda k: sum(pn(l, k) for l in tr))
    o = []; w = o.append
    w("# Bot95 — H799 / H800 : compléter après un fill partiel — PRÉLIMINAIRE (hors ligne)\n")
    w(f"Généré le {time.strftime('%d.%m.%Y %H:%M', time.gmtime())} UTC. {len(LIG)} signaux, {len(cycles)} cycles. Apprentissage {len(tr)} signaux / "
      f"{len({l['st'] for l in tr})} cycles (avant {time.strftime('%H:%M', time.gmtime(coupe))} UTC) ; test {len(te)} signaux / {len({l['st'] for l in te})} cycles. "
      f"Règles R4 (+2 c, recalcul, marge 0,05, 164 ms, 50 $). Seuils choisis sur l'apprentissage : **B1 = {best_b1}**, **B2 = {best_b2}** "
      f"(parmi {len(SEUILS_B1)} et {len(GRILLE_B2)} réglages). Toutes les parts comptées sont exécutables contre le carnet enregistré à l'instant d'exécution "
      "(quantité affichée, budget restant, frais).\n")

    def ligne(nom, k, X_):
        base = sum(pn(l, "D") for l in X_); b0 = sum(pn(l, "B0") for l in X_)
        tot = sum(pn(l, k) for l in X_); comp = sum(pc(l, k) for l in X_); prem = tot - comp
        cm = ic(par_cy(X_), lambda s: float(np.mean([pn(l, k) - pn(l, "D") for l in s])))
        cmb = ic(par_cy(X_), lambda s: float(np.mean([pn(l, k) - pn(l, "B0") for l in s])))
        cq = sum(l["res"][k][2] for l in X_); cc = sum(l["res"][k][3] for l in X_)
        ns = [l for l in X_ if l["res"][k][2] > 0]
        jk = sum(1 for l in ns if l["y"] == 1 and l["res"][k][3] / max(l["res"][k][2], 1e-9) <= 0.25)
        cum = np.cumsum([pn(l, k) for l in sorted(X_, key=lambda l: l["s"]["tDecision"])]); ddv = float(np.max(np.maximum.accumulate(np.concatenate([[0], cum]))[1:] - cum))
        cs = sorted([pc(l, k) for l in X_], reverse=True); conc = 100 * sum(cs[:5]) / comp if comp > 0 else float("nan")
        return (f"| {nom} | {tot:+.0f} | {prem:+.0f} | {comp:+.0f} | {cq:.0f} | {cq and cc / cq or 0:.3f} | {tot - base:+.0f} [{cm[0]:+.2f} ; {cm[1]:+.2f}] | "
                f"{tot - b0:+.0f} [{cmb[0]:+.2f} ; {cmb[1]:+.2f}] | {sum(1 for l in ns if l['y'] == 1)} / {sum(1 for l in ns if l['y'] == 0)} | {jk} | {ddv:.0f} | {conc:.0f} % |")
    ENT = ("| Politique | P&L total ($) | dont 1res parts | dont compléments | Parts compl. | Prix moyen compl. | vs D ($, IC 90 % / signal) | vs B0 ($, IC 90 % / signal) | "
           "Signaux complétés G / P | Jackpots compl. | Drawdown | 5 meilleurs compl. / total compl. |\n|---|---|---|---|---|---|---|---|---|---|---|---|")
    for titre, X_ in (("TEST (2e moitié, cycles non vus)", te), ("APPRENTISSAGE (1re moitié)", tr), ("TOUT", LIG)):
        w(f"## 1. Tableau B0 / B1 / B2 — {titre} (livrables 1, 3, 4, 5, 6)\n"); w(ENT)
        for nom in ("D", "B0", best_b1, best_b2): w(ligne(nom, nom, X_))
        w("")
    w("**Tous les réglages B1 (pour transparence ; la sélection ne regarde que l'apprentissage)**\n")
    w("| Réglage | Apprentissage ($) | Test ($) |\n|---|---|---|")
    for k in [k for k in POL if k.startswith("B1")]: w(f"| {k} | {sum(pn(l, k) for l in tr):+.0f} | {sum(pn(l, k) for l in te):+.0f} |")
    w("\n**Tous les réglages B2**\n\n| Réglage | Apprentissage ($) | Test ($) |\n|---|---|---|")
    for k in [k for k in POL if k.startswith("B2")]: w(f"| {k} | {sum(pn(l, k) for l in tr):+.0f} | {sum(pn(l, k) for l in te):+.0f} |")
    w("\n## 2. H800 — Taille du complément (livrable 2)\n"); w(ENT)
    for fr in FRACS: w(ligne(f"compléments ≤ {int(fr * 100)} % du restant (test)", f"H800 {int(fr * 100)} %", te))
    for fr in FRACS: w(ligne(f"compléments ≤ {int(fr * 100)} % du restant (tout)", f"H800 {int(fr * 100)} %", LIG))
    w("\n## 3. Sensibilité aux frais et à la latence (livrable 7) — tout l'échantillon\n")
    w("| Hypothèse | D ($) | B0 ($) | B0 − D ($) | IC 90 % / signal |\n|---|---|---|---|---|")
    for h, kd, kb in (("frais normaux, 164 ms", "D", "B0"), ("frais × 1,5", "D frais ×1.5", "B0 frais ×1.5"), ("frais × 2", "D frais ×2.0", "B0 frais ×2.0"),
                      ("latence 250 ms", "D latence 250 ms", "B0 latence 250 ms"), ("latence 500 ms", "D latence 500 ms", "B0 latence 500 ms")):
        d_ = sum(pn(l, kd) for l in LIG); b_ = sum(pn(l, kb) for l in LIG)
        c_ = ic(par_cy(LIG), lambda s: float(np.mean([pn(l, kb) - pn(l, kd) for l in s])))
        w(f"| {h} | {d_:+.0f} | {b_:+.0f} | {b_ - d_:+.0f} | [{c_[0]:+.2f} ; {c_[1]:+.2f}] |")
    # verdict avec correction de sélection multiple (Bonferroni sur les comparaisons testées au test)
    comps = [("B0", "D"), (best_b1, "D"), (best_b2, "D")] + [(f"H800 {int(fr * 100)} %", "D") for fr in FRACS]
    a = 0.10 / len(comps)
    w(f"\n## 4. Verdict sur les cycles de test (livrable 8) — correction de Bonferroni pour {len(comps)} comparaisons (IC à {100 * (1 - a):.1f} %)\n")
    w("| Comparaison (test) | Écart moyen / signal | IC 90 % simple | IC corrigé | Verdict |\n|---|---|---|---|---|")
    for k, ref in comps:
        f = lambda s: float(np.mean([pn(l, k) - pn(l, ref) for l in s]))
        c1 = ic(par_cy(te), f); c2 = ic(par_cy(te), f, alpha=a)
        v = "positif (corrigé)" if c2[0] > 0 else ("positif non corrigé seulement" if c1[0] > 0 else "non démontré")
        w(f"| {k} − {ref} | {f(te):+.2f} $ | [{c1[0]:+.2f} ; {c1[1]:+.2f}] | [{c2[0]:+.2f} ; {c2[1]:+.2f}] | {v} |")
    w("\nLes « cycles nouveaux » ici sont la 2e moitié de la journée. La vraie validation reste le fantôme R4 vivant (cycles postérieurs au 11.10 15:30 UTC), "
      "dont chaque tentative est enregistrée, puis la période réservée du 13.10.\n")
    w("## Limites\n- Une journée ; ~15 cycles de test ; gains concentrés.\n- Modèle recalculé hors ligne (fidèle à ±0,005 pour ~3/4 des signaux).\n"
      "- Reconstruction H800 depuis R4 vivant : approximative quand un fill de R4 a été limité par le budget (quantité réellement disponible inconnue au-delà).\n")
    open(SORTIE, "w").write("\n".join(o)); print("\n".join(o))


if __name__ == "__main__":
    main()
