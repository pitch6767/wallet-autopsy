"""BOT95 — Étude de calibration (Pitch, 11.10.2026 22:00, point 5). PRÉ-ENREGISTREMENT : ce fichier, tel que committé avant le 13.10.2026.
Étude distincte de H816 / H821 ; H816 n'est pas modifié ; aucun ordre ; aucun bot ni fantôme modifié.

QUESTION : une calibration de la probabilité Bot95, apprise UNIQUEMENT sur les données antérieures au 13.10.2026, prédit-elle le résultat
mieux que le prix du marché (prix payé a0) sur la période réservée ?

DONNÉES : bot95/rapide.json, signaux réglés (toutes variantes, tous prix, marchés BTC 5 min). Décisions uniques : premier signal par cycle et par
  côté (tri start, côté, tDecision, nom). Variables enregistrées au signal : modele (probabilité Bot95), a0 (prix payé), restant_s.
APPRENTISSAGE : toutes les décisions uniques de cycles < 13.10.2026 00:00 UTC (1791849600). Rien de la période réservée.
CANDIDATS (fixés maintenant, régression logistique, pénalité L2 = 0,5 hors constante, contreparties_h724.ajuster) :
  C1 : logit(Bot95)                         (recalibrage de Bot95 seul)
  C2 : logit(Bot95) + logit(a0)             (combinaison modèle + marché)
  C3 : logit(Bot95) + logit(a0) + restant/300
  logit borné à [0,001 ; 0,999]. Références : Bot95 brut, prix a0.
  Coefficients indicatifs au moment de l'enregistrement (144 décisions, 107 cycles) :
    C1 [−0,565 ; +1,228]   C2 [+1,386 ; −0,599 ; +1,930]   C3 [+0,711 ; −0,551 ; +1,853 ; +0,871]
  Le script réapprend ces coefficients au lancement, avec la même procédure, sur toutes les décisions antérieures au 13.10 disponibles.
ÉVALUATION : décisions uniques de la période réservée (≥ 13.10.2026) ; aussi le sous-ensemble prix 0,20–0,50 (plage H816), à titre descriptif.
  Brier et log loss de chaque estimateur ; différence de Brier (candidat − prix a0) avec IC par rééchantillonnage des CYCLES (5 000, graine 822),
  IC corrigé de Bonferroni pour 3 candidats (niveau 1 − 0,10/3) ; calibration par tranche de probabilité et par temps restant.
CRITÈRE : un candidat « bat le marché » si sa différence de Brier avec a0 est < 0 avec l'IC corrigé entièrement < 0.
  Sinon : aucune calibration retenue, rien n'est ajusté. Un succès ne change pas H816 ; il justifierait seulement un futur protocole distinct.
Usage : python3 etude/bot5min/calibration_bot95.py [--hors-echantillon] → etude/bot5min/resultat_calibration_bot95[_hors_echantillon].md
  Sans le drapeau : contrôle du code par validation croisée chronologique sur la période antérieure (1re moitié → 2e moitié) ; pas un verdict."""
import json, os, sys, math, time
import numpy as np

ICI = os.path.dirname(os.path.abspath(__file__)); RACINE = os.path.abspath(os.path.join(ICI, "..", ".."))
sys.path.insert(0, ICI)
import contreparties_h724 as CH
HORS_ECH = 1791849600; HE = "--hors-echantillon" in sys.argv
SORTIE = os.path.join(ICI, "resultat_calibration_bot95" + ("_hors_echantillon" if HE else "") + ".md")
L2 = 0.5; B = 5000; ALPHA = 0.10; NC = 3
rng = np.random.default_rng(822)
lg = lambda p: math.log(min(max(p, 1e-3), 1 - 1e-3) / (1 - min(max(p, 1e-3), 1 - 1e-3)))
CAND = {"C1 logit(Bot95)": lambda s: [lg(s["modele"])],
        "C2 logit(Bot95) + logit(prix)": lambda s: [lg(s["modele"]), lg(s["a0"])],
        "C3 C2 + temps restant": lambda s: [lg(s["modele"]), lg(s["a0"]), s["restant_s"] / 300]}


def uniques(SIG):
    SIG = sorted(SIG, key=lambda s: (s["start"], s["cote"], s["tDecision"], s["nom"])); U = {}
    for s in SIG: U.setdefault((s["start"], s["cote"]), s)
    return list(U.values())


def sq(p, y): return (np.asarray(p) - np.asarray(y)) ** 2
def ll(p, y):
    p = np.clip(np.asarray(p, float), 1e-3, 1 - 1e-3); y = np.asarray(y, float); return -(y * np.log(p) + (1 - y) * np.log(1 - p))


def ic_cycles(st, v, alpha):
    cyc = sorted(set(st)); G = [np.array([v[i] for i in range(len(v)) if st[i] == c]) for c in cyc]
    S = np.array([g.sum() for g in G]); N = np.array([len(g) for g in G])
    if len(S) < 3: return (float("nan"), float("nan"))
    idx = rng.integers(0, len(S), (B, len(S))); m = S[idx].sum(1) / N[idx].sum(1)
    return float(np.percentile(m, 100 * alpha / 2)), float(np.percentile(m, 100 * (1 - alpha / 2)))


def main():
    ALL = [s for s in json.load(open(os.path.join(RACINE, "bot95", "rapide.json")))["signaux"] if s.get("gagnant")]
    PRE = uniques([s for s in ALL if s["start"] < HORS_ECH])
    if HE: APP, EVA = PRE, uniques([s for s in ALL if s["start"] >= HORS_ECH])
    else:
        cyc = sorted({s["start"] for s in PRE}); coupe = cyc[len(cyc) // 2]
        APP, EVA = [s for s in PRE if s["start"] < coupe], [s for s in PRE if s["start"] >= coupe]
    y = lambda Z: np.array([1.0 if s["gagne"] else 0.0 for s in Z])
    coef = {k: CH.ajuster(np.array([f(s) for s in APP]), y(APP), L2) for k, f in CAND.items()}
    o = []; w = o.append
    w(f"# Bot95 — Étude de calibration ({'PÉRIODE RÉSERVÉE' if HE else 'CONTRÔLE DU CODE sur la période antérieure — pas un verdict'})\n")
    w(f"Généré le {time.strftime('%d.%m.%Y %H:%M', time.gmtime())} UTC. Apprentissage : {len(APP)} décisions uniques ({len({s['start'] for s in APP})} cycles). "
      f"Évaluation : {len(EVA)} décisions ({len({s['start'] for s in EVA})} cycles). Aucun ordre ; H816 inchangé.\n")
    w("Coefficients appris : " + " ; ".join(f"{k} [{', '.join(f'{v:+.3f}' for v in b)}]" for k, b in coef.items()) + "\n")
    for titre, Z in (("Toutes les décisions uniques", EVA), ("Plage H816 (prix 0,20–0,50), descriptif", [s for s in EVA if 0.20 - 1e-9 <= s["a0"] <= 0.50 + 1e-9])):
        if len(Z) < 3: w(f"## {titre}\nTrop peu de décisions ({len(Z)}).\n"); continue
        yz = y(Z); st = [s["start"] for s in Z]
        P = {"Bot95 brut": np.array([s["modele"] for s in Z]), "prix a0 (marché)": np.array([s["a0"] for s in Z])}
        for k, f in CAND.items(): P[k] = CH.predire(coef[k], np.array([f(s) for s in Z]))
        w(f"## {titre} ({len(Z)} décisions, {len(set(st))} cycles)\n")
        w(f"| Estimateur | Brier | Log loss | Brier − prix a0 | IC 90 % | IC corrigé (3 candidats) | Bat le marché ? |\n|---|---|---|---|---|---|---|")
        ref = sq(P["prix a0 (marché)"], yz)
        for k, p in P.items():
            e = sq(p, yz); d = e - ref
            if k == "prix a0 (marché)": w(f"| {k} | {e.mean():.4f} | {ll(p, yz).mean():.4f} | — | — | — | référence |"); continue
            c1 = ic_cycles(st, d, ALPHA); c2 = ic_cycles(st, d, ALPHA / NC)
            bat = ("oui" if c2[1] < 0 else "non") if k in CAND else "—"
            w(f"| {k} | {e.mean():.4f} | {ll(p, yz).mean():.4f} | {d.mean():+.4f} | [{c1[0]:+.4f} ; {c1[1]:+.4f}] | [{c2[0]:+.4f} ; {c2[1]:+.4f}] | {bat} |")
        w("\n| Temps restant | Décisions | Victoire | Bot95 | Prix a0 | C2 |\n|---|---|---|---|---|---|")
        for lo, hi in ((0, 60), (60, 120), (120, 180), (180, 240), (240, 301)):
            m = np.array([lo <= s["restant_s"] < hi for s in Z])
            if m.any(): w(f"| {lo}–{hi} s | {m.sum()} | {100 * yz[m].mean():.0f} % | {P['Bot95 brut'][m].mean():.2f} | {P['prix a0 (marché)'][m].mean():.2f} | {P['C2 logit(Bot95) + logit(prix)'][m].mean():.2f} |")
        w("")
    w("## Critère\nUn candidat bat le marché si l'IC corrigé de la différence de Brier est entièrement < 0. Sinon, aucune calibration n'est retenue.\n")
    open(SORTIE, "w").write("\n".join(o)); print("\n".join(o))


if __name__ == "__main__":
    main()
