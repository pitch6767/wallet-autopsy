"""BOT95 — VALIDATION INDÉPENDANTE H821 (Pitch, 11.10.2026 22:00). PRÉ-ENREGISTREMENT : ce fichier, tel que committé avant le 13.10.2026,
est le protocole. Hors ligne ; aucun ordre ; aucun bot actif, R4, H816 ni fantôme modifié ; aucun nouveau fantôme.

RÈGLES FIGÉES
  Univers de marchés : marchés BTC 5 min Up/Down de Polymarket ; signaux Bot95 réglés de bot95/rapide.json (toutes variantes), sur les cycles
    disposant d'un fichier de carnet Dublin (branche donnees-rapide, cycles/AAAA-MM-JJ/<start>.json.gz). Exactement l'univers de H816.
  H816 (inchangé, importé de robustesse_bot95.py, commit 56ef5e2) :
    prix a0 entre 0,20 et 0,50 $ inclus ; puis une décision par cycle et par côté = la première par tDecision (égalité → nom de variante) ;
    mise 20 $ frais compris ; ordre preneur limité à a0 exécuté contre le carnet Dublin à décision + 164 ms (200 / 250 / 500 ms en diagnostic) ;
    quantité affichée ≤ a0 seulement ; frais preneur 0,07·p·(1−p) ; aucune relance ; conservation jusqu'au règlement.
  H816 + H821 : les mêmes décisions H816, dont on RETIRE (sans remplacement par un signal suivant) celles où
    dist_sigma > SEUIL, SEUIL = −0,09045519908382879 (tercile exact de l'apprentissage H821, affiché −0,090 dans le rapport, commit 42eb8ac).
    Aucun autre filtre.
  Définition de dist_sigma (copie exacte de selection_h819.py, commit ad2208f) :
    Modèle Dublin chargé sur les fichiers du cycle et du cycle précédent ; t0 = tDecision (ms) ; sens = +1 pour Up, −1 pour Down ;
    cl = dernier prix Chainlink connu à t0 ; dist = (cl − prix à battre du cycle) × sens ;
    vol = écart-type des rendements logarithmiques du perp Bybit échantillonné toutes les 2 s sur les 60 s précédant t0 (31 points), × 1e4 ;
    sigma = (vol / 1e4) × cl × √(max(temps restant en s, 1) / 2) ; dist_sigma = dist / sigma.
    Donnée manquante (pas de Chainlink, pas de prix à battre, sigma nul) → dist_sigma = 0, comme dans l'étude (donc signal exclu) ; compté à part.
  P&L : parts × 1 si gagné − coût frais compris ; non exécuté = 0 $. Jackpot = P&L ≥ 2 × mise (40 $) à 164 ms.
  Budget de référence : 20 $ par décision ; capital engagé = somme des coûts.
  Différence par cycle = P&L(H816 + H821) − P&L(H816) = − P&L des décisions retirées du cycle.
  IC : 90 % bilatéral, 5 000 rééchantillonnages des cycles ayant au moins une décision H816, graine 821.
CRITÈRE DE RÉUSSITE (164 ms) : P&L total de la variante > P&L total de H816 ET IC 90 % de la différence totale entièrement > 0.
  Échec → la variante est abandonnée, son seuil n'est pas modifié. Le résultat ne vaut que comme confirmation partielle : la règle a été choisie
  parmi 38 après plusieurs recherches (H717–H821) sur une seule journée de données.
VALIDATION : seulement sur la période réservée (cycles ≥ 13.10.2026 00:00 UTC), lancée avec --hors-echantillon après la fin de la période,
  au même moment que le verdict H816. Sans ce drapeau, le script ne lit que la période antérieure (contrôle du code).
Usage : python3 etude/bot5min/validation_h821.py dossier_cycles [--hors-echantillon] → etude/bot5min/resultat_validation_h821[_hors_echantillon].md"""
import json, os, sys, glob, math, time
import numpy as np

ICI = os.path.dirname(os.path.abspath(__file__)); RACINE = os.path.abspath(os.path.join(ICI, "..", ".."))
sys.path.insert(0, ICI)
import latence_h766 as LH, modele_dublin as MD
import robustesse_bot95 as H816          # décisions, achat, univers : exactement H816

HE = H816.HE; dans = H816.dans
SORTIE = os.path.join(ICI, "resultat_validation_h821" + ("_hors_echantillon" if HE else "") + ".md")
SEUIL = -0.09045519908382879
MISE = H816.MISE; DELAIS = H816.DELAIS; EXEC = 164
B = 5000
rng = np.random.default_rng(821)


def dist_sigma(Mo, cy, s):
    """copie exacte de la définition de selection_h819.py ; renvoie (valeur, donnée_manquante)"""
    t0 = s["tDecision"]; X = s["cote"]; sens = 1 if X == "Up" else -1
    def px(src, t):
        r = Mo.dernier(src, t / 1000); return r[1] if r else None
    cl = px("cl", t0)
    ser = [px("perp", t0 - 1000 * k) for k in range(0, 61, 2)]; ser = [v for v in ser if v]
    rets = np.diff(np.log(ser)) if len(ser) > 3 else np.array([0.0])
    vol = float(np.std(rets) * 1e4); tl = s["restant_s"]
    dist = (cl - cy.strike) * sens if (cl and cy.strike) else None
    sig_ = (vol / 1e4) * (cl or 1) * math.sqrt(max(tl, 1) / 2) if cl else None
    if dist is not None and sig_: return dist / sig_, False
    return 0.0, True


def pnl(x, d=EXEC): return x[d][0] * x["y"] - x[d][1]


def mesures(X_, d):
    X_ = sorted(X_, key=lambda x: x["t0"]); ex = [x for x in X_ if x[d][0] > 0]
    pn = [pnl(x, d) for x in X_]; tot = sum(pn); eng = sum(x[d][1] for x in X_)
    cum = np.cumsum(pn) if pn else np.array([0.0])
    dd = float(np.max(np.maximum.accumulate(np.concatenate([[0], cum]))[1:] - cum)) if pn else 0.0
    # pire série de pertes : décisions exécutées consécutives perdantes (ordre chronologique)
    best_n = best_s = cur_n = cur_s = 0.0
    for x in ex:
        v = pnl(x, d)
        if v < 0: cur_n += 1; cur_s += v
        else: cur_n = cur_s = 0.0
        best_n = max(best_n, cur_n); best_s = min(best_s, cur_s)
    top = sorted(pn, reverse=True)[:5]
    return dict(n=len(X_), ex=len(ex), g=np.mean([x["y"] for x in ex]) if ex else float("nan"), tot=tot, eng=eng,
                pd=tot / eng if eng else float("nan"), dd=dd, serie_n=int(best_n), serie_s=best_s,
                top5=100 * sum(top) / tot if tot > 0 else float("nan"), jack=sum(1 for v in pn if v >= 2 * MISE))


def ic_diff(par_cy, d):
    """IC 90 % de la différence totale et par décision H816 (rééchantillonnage des cycles)"""
    D = np.array([sum(-pnl(x, d) for x in g if x["exclu"]) for g in par_cy]); N = np.array([len(g) for g in par_cy])
    if len(D) < 3: return (float("nan"),) * 4
    idx = rng.integers(0, len(D), (B, len(D))); tot = D[idx].sum(1); per = tot / N[idx].sum(1)
    return (float(np.percentile(tot, 5)), float(np.percentile(tot, 95)), float(np.percentile(per, 5)), float(np.percentile(per, 95)))


def main():
    dossier = sys.argv[1]
    F = {int(os.path.basename(f).split(".")[0]): f for f in glob.glob(os.path.join(dossier, "**", "*.json.gz"), recursive=True)}
    F_tous = dict(F)                                    # le cycle précédent sert seulement à charger les prix (comme l'étude)
    F = {k: v for k, v in F.items() if dans(k)}
    TOUS = [s for s in json.load(open(os.path.join(RACINE, "bot95", "rapide.json")))["signaux"] if s.get("gagnant") and dans(s["start"])]
    SIG = [s for s in TOUS if s["start"] in F]
    DEC = H816.decisions(SIG)
    cycles = sorted({s["start"] for s in DEC})
    L = []
    for st in cycles:
        cy = LH.Cycle(F[st]); S = [s for s in DEC if s["start"] == st]
        prev = F_tous.get(st - 300); ex = MD.charger_ex([f for f in (prev, F[st]) if f]); Mo = MD.Modele(ex, cy.strike, st + 300)
        E = cy.etats([s["tDecision"] + d for s in S for d in DELAIS])
        for s in S:
            a0m = int(round(s["a0"] * 1000)); t0 = s["tDecision"]; ds, manq = dist_sigma(Mo, cy, s)
            x = dict(st=st, y=1.0 if s["gagne"] else 0.0, t0=t0, a0=s["a0"], ds=ds, manq=manq, exclu=ds > SEUIL)
            x.update({d: H816.acheter_mise(E[t0 + d], s["cote"], a0m, MISE) for d in DELAIS}); L.append(x)
    V = [x for x in L if not x["exclu"]]; R = [x for x in L if x["exclu"]]
    par_cy = [[x for x in L if x["st"] == st] for st in cycles]
    o = []; w = o.append
    w(f"# Bot95 — Validation H821 : H816 contre H816 + filtre H821 ({'PÉRIODE RÉSERVÉE' if HE else 'CONTRÔLE DU CODE, avant le 13.10 — pas une validation'})\n")
    w(f"Généré le {time.strftime('%d.%m.%Y %H:%M', time.gmtime())} UTC. Cycles avec décisions H816 : {len(cycles)} ; décisions H816 : {len(L)} ; "
      f"retirées par le filtre (dist_sigma > {SEUIL:.4f}) : {len(R)} dont {sum(x['manq'] for x in R)} par donnée manquante. Mise 20 $, IC 90 % par cycles. Aucun ordre.\n")
    w("## 1. Résultat principal (164 ms) et sensibilité à la latence\n")
    w("| Délai | Politique | Décisions | Exécutées | Taux de gain | Capital engagé ($) | P&L net ($) | P&L par $ | Drawdown ($) | Pire série de pertes | Jackpots | 5 meilleures / total |\n"
      "|---|---|---|---|---|---|---|---|---|---|---|---|")
    for d in DELAIS:
        for nom, X_ in (("H816", L), ("H816 + H821", V)):
            r = mesures(X_, d)
            w(f"| {d} ms{' (critère)' if d == EXEC else ''} | {nom} | {r['n']} | {r['ex']} | {100 * r['g']:.0f} % | {r['eng']:.0f} | {r['tot']:+.0f} | {100 * r['pd']:+.1f} % | "
              f"{r['dd']:.0f} | {r['serie_n']} pertes, {r['serie_s']:+.0f} $ | {r['jack']} | {r['top5']:.0f} % |")
    w("\n## 2. Différence variante − H816 et filtre\n")
    w("| Délai | Perdants évités | Gagnants supprimés | Jackpots supprimés | Différence de P&L ($) | IC 90 % total ($) | IC 90 % par décision H816 ($) |\n|---|---|---|---|---|---|---|")
    for d in DELAIS:
        Rx = [x for x in R if x[d][0] > 0]
        c = ic_diff(par_cy, d)
        w(f"| {d} ms | {sum(1 for x in Rx if x['y'] == 0)} | {sum(1 for x in Rx if x['y'] == 1)} | {sum(1 for x in Rx if pnl(x, d) >= 2 * MISE)} | "
          f"{sum(-pnl(x, d) for x in R):+.0f} | [{c[0]:+.0f} ; {c[1]:+.0f}] | [{c[2]:+.2f} ; {c[3]:+.2f}] |")
    w(f"\n(Perdants / gagnants / jackpots comptés parmi les décisions retirées qui auraient été exécutées ; {len(R) - sum(1 for x in R if x[EXEC][0] > 0)} retirées n'auraient pas été exécutées à 164 ms.)\n")
    r16, rv = mesures(L, EXEC), mesures(V, EXEC); c = ic_diff(par_cy, EXEC)
    ok = rv["tot"] > r16["tot"] and c[0] > 0
    w("## 3. Verdict selon le critère pré-enregistré\n")
    if not HE: w("**Contrôle du code uniquement (données déjà utilisées pour choisir la règle) : aucun verdict.**\n")
    else: w(f"**{'RÉUSSITE' if ok else 'ÉCHEC'}** — différence {rv['tot'] - r16['tot']:+.0f} $, IC 90 % [{c[0]:+.0f} ; {c[1]:+.0f}] $. "
            + ("Confirmation partielle seulement (voir limites)." if ok else "La variante est abandonnée ; le seuil n'est pas modifié.") + "\n")
    w("## Limites\n- La règle a été choisie parmi 38 candidates, après de nombreuses recherches sur une seule journée de données ; un succès reste une "
      "confirmation partielle.\n- Peu de cycles : faible puissance ; un échec n'exclut pas un petit effet, un succès peut tenir à quelques trades.\n"
      "- Une donnée manquante (Chainlink, prix à battre) exclut le signal, comme dans l'étude ; leur nombre est indiqué plus haut.\n")
    open(SORTIE, "w").write("\n".join(o)); print("\n".join(o))


if __name__ == "__main__":
    main()
