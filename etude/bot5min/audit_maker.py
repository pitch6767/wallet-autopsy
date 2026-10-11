"""BOT95 — AUDIT COMPLÉMENTAIRE MAKER (M4a/M4b/M4c, contrefactuels, M6, file d'attente, M8, délai preneur, comparaison des moteurs).
Cahier des charges de Pitch du 11.10.2026 15:30 (12 sections). Hors ligne : AUCUN fantôme, paramètre ou bot modifié ; aucun ordre.
Période réservée (≥ 13.10.2026 00:00 UTC) non lue, sauf --hors-echantillon (verdict du 15.10, une seule fois).
Statut de chaque chiffre : MESURE (heures, files affichées, transactions, prix), SIMULATION (remplissages et résultats en $),
CONTREFACTUEL (hors ligne, jamais présenté comme des remplissages réels), INSUFFISANT (< 30 remplissages).
Usage : python3 etude/bot5min/audit_maker.py dossier_des_cycles [--hors-echantillon] → etude/bot5min/resultat_audit_maker[_hors_echantillon].md"""
import gzip, json, os, sys, glob, bisect, collections, time, random
import numpy as np

ICI = os.path.dirname(os.path.abspath(__file__)); RACINE = os.path.abspath(os.path.join(ICI, "..", ".."))
sys.path.insert(0, ICI)
import queue_race_phase12 as Q
import fast_fenetre as FF
import verifications_h559 as VH

HORS_ECH = 1791849600
HORS = "--hors-echantillon" in sys.argv
SORTIE = os.path.join(ICI, "resultat_audit_maker_hors_echantillon.md" if HORS else "resultat_audit_maker.md")
garde = lambda st: (st >= HORS_ECH) == HORS
PAUSE = 2000.0
mil = lambda p: int(round(p * 1000))
BORNES = ("prudent", "proportionnel", "optimiste")
JACKPOT = 0.25                                   # jackpot = position achetée ≤ 0,25 qui gagne


def ic(par_cycle, n=2000, seed=3):
    v = np.array(list(par_cycle.values()), dtype=float)
    if len(v) < 3: return None
    rng = np.random.default_rng(seed); b = [v[rng.integers(0, len(v), len(v))].sum() for _ in range(n)]
    return np.percentile(b, [5, 95])


def fic(x): return f"[{x[0]:+.0f} ; {x[1]:+.0f}]" if x is not None else "[—]"


def creux(par_cycle):
    if not par_cycle: return 0.0
    c = np.cumsum([par_cycle[k] for k in sorted(par_cycle)]); pic = np.maximum.accumulate(np.concatenate([[0.0], c]))[1:]
    return float(np.min(np.minimum(c - pic, 0)))


def pire_serie(pnls):
    m = s = 0
    for x in pnls:
        s = s + 1 if x < 0 else 0; m = max(m, s)
    return m


def declencheurs(ser, up):
    """heures (réception Dublin) où chaque condition de M4 se déclenche, calculées comme M4 : a, b, c"""
    ex, fx, tr = ser; sens = 1 if up else -1; out = {"a": [], "b": [], "c": []}
    Et = [x[0] for x in ex]
    for j, (tj, pj) in enumerate(ex):
        k = bisect.bisect_right(Et, tj - 300) - 1
        if k >= 0 and sens * (pj - ex[k][1]) <= -10: out["a"].append(tj)
    Ft = [x[0] for x in fx]; cum = np.cumsum([0.0] + [x[1] for x in fx])
    for j, (tj, v) in enumerate(fx):
        k0 = bisect.bisect_left(Ft, tj - 250)
        if sens * (cum[j + 1] - cum[k0]) <= -250000: out["b"].append(tj)
    mine = [(t, z) for t, tok, z in tr if tok == (0 if up else 1)]; Mt = [x[0] for x in mine]; cm = np.cumsum([0.0] + [x[1] for x in mine])
    for j, (tj, z) in enumerate(mine):
        k0 = bisect.bisect_left(Mt, tj - 500)
        if cm[j + 1] - cm[k0] >= 100: out["c"].append(tj)
    return out


def actif(L, t, lat, d=0.0):
    """une condition déclenchée à τ fait annuler l'offre à τ + d + lat (effectif chez Polymarket) et la tient retirée jusqu'à τ + d + 2 s"""
    i = bisect.bisect_right(L, t - d - lat) - 1
    return i >= 0 and L[i] >= t - d - PAUSE


def main():
    dossier = [a for a in sys.argv[1:] if not a.startswith("--")][0]
    MKR = json.load(open(os.path.join(RACINE, "bot95", "rapide_maker.json")))
    MKR = [x for x in MKR if x.get("type") != "resume" and x.get("resultat") and garde(x["start"])]
    V = collections.defaultdict(list)
    for x in MKR: V[x["variante"]].append(x)
    SIG = json.load(open(os.path.join(RACINE, "bot95", "rapide.json")))["signaux"]
    SIGc = collections.defaultdict(list)
    for S in SIG:
        if S.get("gagnant") and S.get("tDecision") and garde(S["start"]): SIGc[S["start"]].append(S)
    GAGN = {x["start"]: x["gagnant"] for x in MKR if x.get("gagnant")}
    GAGN.update({S["start"]: S["gagnant"] for L in SIGc.values() for S in L})
    # ------------------------------------------------ lecture des cycles
    POSE = collections.defaultdict(list); DECL = {}; TRR = {}; CYC = []; SIGcyc = collections.Counter(); TOUR = collections.defaultdict(list)
    v_m8 = min((x["start"] for x in MKR if x["variante"].startswith("M8")), default=None)
    for fn in sorted(glob.glob(os.path.join(dossier, "**", "*.json.gz"), recursive=True)):
        st = int(os.path.basename(fn).split(".")[0])
        if not garde(st): continue
        R = json.load(gzip.open(fn)); mk = R.get("mk") or []
        if not mk or len(mk[0]) < 22: continue
        CYC.append(st); ser = VH.series_cycle(R)
        DECL[st] = {True: declencheurs(ser, True), False: declencheurs(ser, False)}
        TRR[st] = [(e[1], e[3], e[4], e[5], e[6]) for e in R.get("ev", []) if e[0] == "T"]
        for r in mk: POSE[r[0]].append([st] + r)
        if v_m8 and st >= v_m8: SIGcyc[st] = len(R.get("sig") or [])
        sigs = SIGc.get(st, [])
        if sigs:
            C = FF.normaliser(fn)
            for dl in (0.0, 50.0, 150.0, 250.0):                  # délai preneur : plusieurs scénarios (150 ms = hypothèse documentée)
                FF.DELAI_PRENEUR = dl
                for x in FF.tournoi_signaux(C, sigs): x["start"] = st; TOUR[dl].append(x)
            FF.DELAI_PRENEUR = 150.0
    cyc = set(CYC)
    o = []; w = o.append
    w("# Bot95 — Audit complémentaire maker (M4a/b/c, M6, M8, file d'attente) — DIAGNOSTIC, pas un verdict\n")
    w(f"Généré le {time.strftime('%d.%m.%Y %H:%M', time.gmtime())} UTC. {len(CYC)} cycles enregistrés avec la version du 11.10 14:55, "
      f"{'HORS ÉCHANTILLON' if HORS else 'avant la période réservée (13.10.2026 00:00 UTC)'}. Aucun fantôme, paramètre ou bot modifié ; aucun ordre.\n")
    w("**Statut** — MESURE : heures, files affichées, transactions, prix. SIMULATION : remplissages (3 bornes de file) et résultats. "
      "CONTREFACTUEL : recalcul hors ligne, jamais des remplissages réels. HYPOTHÈSE : retard preneur 150 ms (documentation, non mesuré). "
      "Intervalles à 90 % par rééchantillonnage des CYCLES. Moins de 30 remplissages = INSUFFISANT.\n")

    # ================================================ 2. huit combinaisons sur les MÊMES opportunités (offres de M2 marge 5 c, même prix que M4)
    w("## 2. M4 — les huit combinaisons a / b / c sur les mêmes opportunités\n")
    w("Base commune : chaque offre posée par M2 marge 5 c (même prix que M4, aucun retrait) est une opportunité. Pour chaque REMPLISSAGE de M2, on regarde quelles "
      "conditions l'auraient évité (déclenchée entre 2 s et le trajet de l'annulation avant le remplissage), avec les seules données reçues avant. "
      "Les 8 lignes partitionnent donc les mêmes remplissages : aucune comparaison entre fantômes différents.\n")
    base = [x for x in V.get("M2 cotation marge 5 c", []) if x["start"] in cyc]
    combos = collections.defaultdict(lambda: dict(fills=0, parts=0.0, pnl=0.0, gagnes=0.0, mo=collections.defaultdict(lambda: [0.0, 0.0]), pc=collections.defaultdict(float)))
    opp = collections.Counter(); act = collections.Counter()
    for r in POSE.get("M2 cotation marge 5 c", []):
        st = r[0]; up = r[2] == "Up"; D = DECL[st][up]; lat = r[5] or 15
        k = "".join(c for c in "abc" if actif(D[c], r[4], lat)) or "aucune"; opp[k] += 1
        if r[6] != "rejetee": act[k] += 1
    FILLS = []                                                                   # (st, up, t_fill, parts, gain par part, combo, ordre)
    for x in base:
        up = x["cote"] == "Up"; D = DECL[x["start"]][up]; lat = x.get("lat_ms") or 15; g = 1.0 if x.get("gagne") else 0.0
        for ms, k_, q in x.get("rempl") or []:
            if k_ != "p": continue
            tf = x["tPose"] + ms; k = "".join(c for c in "abc" if actif(D[c], tf, lat)) or "aucune"
            FILLS.append((x["start"], up, tf, q, g - x["prix"], k, x))
            C = combos[k]; C["fills"] += 1; C["parts"] += q; C["pnl"] += q * (g - x["prix"]); C["gagnes"] += q * g; C["pc"][x["start"]] += q * (g - x["prix"])
            for h in ("1", "3", "5", "10"):
                a = (x.get("mo") or {}).get("p", {}).get(h)
                if a and a[1]: C["mo"][h][0] += q * a[0] / a[1]; C["mo"][h][1] += q
    w("| a | b | c | Opportunités (offres posées) | Cotations actives | Remplissages | Parts | Sélection adverse +1/+3/+5/+10 s (c/part) | Victoire finale | Résultat | IC 90 % | Bons remplissages perdus si on retire |")
    w("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for k in ("aucune", "a", "b", "c", "ab", "ac", "bc", "abc"):
        C = combos.get(k); fl = lambda c, k=k: "Oui" if (k != "aucune" and c in k) else "Non"
        if not C:
            w(f"| {fl('a')} | {fl('b')} | {fl('c')} | {opp[k]} | {act[k]} | 0 | — | — | — | — | — | — |"); continue
        mo = " / ".join(f"{100 * C['mo'][h][0] / C['mo'][h][1]:+.1f}" if C["mo"][h][1] else "—" for h in ("1", "3", "5", "10"))
        bons = sum(1 for f in FILLS if f[5] == k and f[4] > 0)
        w(f"| {fl('a')} | {fl('b')} | {fl('c')} | {opp[k]} | {act[k]} | {C['fills']} | {C['parts']:.0f} | {mo} | {100 * C['gagnes'] / C['parts']:.0f} % | {C['pnl']:+.0f} $ | {fic(ic(C['pc']))} | {bons if k != 'aucune' else '—'} |")
    w(f"\nRemplissages de M2 marge 5 c analysés : {len(FILLS)} — " + ("**INSUFFISANT** pour séparer les combinaisons." if len(FILLS) < 30 else "à lire avec prudence.") + "\n")
    # effet marginal et interactions
    w("**Effet marginal de chaque condition** (sur les mêmes remplissages : résultat des remplissages qu'elle seule ferait éviter, et ceux évités par elle quelle que soit la combinaison) :\n")
    for c in "abc":
        seul = [f for f in FILLS if f[5] == c]; tous = [f for f in FILLS if f[5] != "aucune" and c in f[5]]
        w(f"- {c} : seule → {len(seul)} remplissages évités, {sum(f[3] * f[4] for f in seul):+.0f} $ ; au total → {len(tous)} remplissages évités, {sum(f[3] * f[4] for f in tous):+.0f} $ "
          f"(dont {sum(1 for f in tous if f[4] > 0)} gagnants perdus).")
    w("\nInteraction = résultat des lignes à plusieurs conditions comparé à la somme des lignes à une condition. Une condition active sur un remplissage gagnant ou perdant "
      "ne prouve rien à elle seule : seul l'écart contre le contrefactuel aléatoire (section 3) mesure une capacité de prédiction.\n")
    w("**Comparaison directe des fantômes** (même prix, mêmes cycles, chacun simulé seul) :\n")
    w("| Fantôme | Remplissages | Parts | Résultat prudent | IC 90 % | Sélection adverse +3 s |\n|---|---|---|---|---|---|")
    for v in ("M2 cotation marge 5 c", "M4 retrait toxique", "M4a seul bourses -10 $", "M4b seul flux agressif", "M4c seul ventes Polymarket", "M0 temoin aleatoire"):
        X = [x for x in V.get(v, []) if x["start"] in cyc]; pc = collections.defaultdict(float)
        for x in X: pc[x["start"]] += x["resultat"]["prudent"]
        a = sum((x.get("mo") or {}).get("p", {}).get("3", [0, 0])[0] for x in X); b = sum((x.get("mo") or {}).get("p", {}).get("3", [0, 0])[1] for x in X)
        w(f"| {v} | {len(X)} | {sum(x['remplP'] for x in X):.0f} | {sum(pc.values()):+.0f} $ | {fic(ic(pc))} | {(100 * a / b if b else float('nan')):+.1f} c |")

    # ================================================ 3. contrefactuels
    w("\n## 3. Contrôles contre les faux gains (CONTREFACTUELS hors ligne, base : remplissages de M2 marge 5 c)\n")
    tot_pnl = sum(f[3] * f[4] for f in FILLS); tot_q = sum(f[3] for f in FILLS)
    def garde_si(pred):
        K = [f for f in FILLS if not pred(f)]; return len(K), sum(f[3] for f in K), sum(f[3] * f[4] for f in K)
    lignes = []
    lignes.append(("B. M4 sans annulations (= M2 marge 5 c)", len(FILLS), tot_q, tot_pnl))
    lignes.append(("A. M4 complet (recalculé)", *garde_si(lambda f: f[5] != "aucune")))
    for d in (100, 300, 1000):
        def pr(f, d=d):
            D = DECL[f[0]][f[1]]; lat = (f[6].get("lat_ms") or 15)
            return any(actif(D[c], f[2], lat, d) for c in "abc")
        lignes.append((f"C. M4 annulations retardées de {d} ms", *garde_si(pr)))
    # temps retiré réel de M4 (fraction du temps de pose en pause), pour D et E
    frac = []
    for r in POSE.get("M2 cotation marge 5 c", []):
        frac.append(1.0 if any(actif(DECL[r[0]][r[2] == "Up"][c], r[4], r[5] or 15) for c in "abc") else 0.0)
    p_retire = float(np.mean(frac)) if frac else 0.0
    rng = random.Random(9); simD, simE = [], []
    nde = {(st, up): sum(len(DECL[st][up][c]) for c in "abc") for st in DECL for up in (True, False)}
    for _ in range(300):
        K = [f for f in FILLS if rng.random() >= p_retire]; simD.append(sum(f[3] * f[4] for f in K))
        fen = {k: sorted(st * 1000 + rng.random() * 300000 for _ in range(n)) for k, n in nde.items() for st in [k[0]]}
        K = [f for f in FILLS if not actif(fen[(f[0], f[1])], f[2], f[6].get("lat_ms") or 15)]; simE.append(sum(f[3] * f[4] for f in K))
    w("| Contrefactuel | Remplissages gardés | Parts | Résultat |\n|---|---|---|---|")
    for nom, n, q, r in lignes: w(f"| {nom} | {n} | {q:.0f} | {r:+.0f} $ |")
    if simD:
        w(f"| D. Annulations aléatoires, même fréquence de retrait ({100 * p_retire:.0f} % des poses) — 300 tirages | — | — | médiane {np.median(simD):+.0f} $ [p5 {np.percentile(simD, 5):+.0f} ; p95 {np.percentile(simD, 95):+.0f}] |")
        w(f"| E. Même durée de présence : mêmes nombres de pauses de 2 s placées au hasard — 300 tirages | — | — | médiane {np.median(simE):+.0f} $ [p5 {np.percentile(simE, 5):+.0f} ; p95 {np.percentile(simE, 95):+.0f}] |")
    w("| F. Mêmes horaires, autres prix de cotation | — | — | NON CALCULABLE de façon fiable hors ligne : la file aux autres prix n'est enregistrée qu'à ±3 c du meilleur prix (proposé comme fantôme après le verdict) |")
    A = lignes[1][3]
    if simE:
        rang = sum(1 for x in simE if x >= A) / len(simE)
        w(f"\n**Lecture** : M4 recalculé garde {A:+.0f} $ ; des retraits au hasard de même durée gardent {np.median(simE):+.0f} $ en médiane. "
          f"Part des tirages aléatoires au moins aussi bons que M4 : {100 * rang:.0f} %. "
          + ("Si cette part est faible (< 5 %), M4 prédit vraiment la toxicité ; sinon son avantage peut venir d'une simple exposition réduite." ))
    w("\nValidation de la méthode : le résultat « A recalculé » doit être proche du fantôme M4 réel (section 2) ; un écart signale une différence de calcul des conditions.\n")

    # ================================================ 4. M6
    w("## 4. M6 — durée de vie des cotations\n")
    w("| Variante | Ordres posés | Remplacements | Temps réellement actif (min) | Attente d'annulation (s) | Délai confirmation → nouvelle pose (médiane ms) | Remplissages pendant l'annulation (parts) | Remplissages partiels | Parts | Résultat prudent | par ordre posé | par minute d'exposition | par $ exécuté | Capital immobilisé moyen ($ posés) | Bons remplissages manqués vs M2 |")
    w("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    ref_bons = sum(1 for x in V.get("M2 cotation marge 5 c", []) if x["start"] in cyc and x.get("gagne") and x["remplP"] > 0)
    for v in ["M2 cotation marge 5 c"] + [f"M6 duree de vie {L} ms" for L in (100, 250, 500, 1000)]:
        P = sorted(POSE.get(v, []), key=lambda r: (r[0], r[2], r[4])); actif_ms = 0.0; attente = 0.0; rempl_ann = 0.0; nrep = 0; gaps = []; notion = []
        for i, r in enumerate(P):
            lat = r[5] or 15
            if r[16]: actif_ms += max(0.0, r[16] - (r[4] + lat)); notion.append(50.0)
            if r[17] == "duree de vie":
                nrep += 1; attente += 2 * lat
                if i + 1 < len(P) and P[i + 1][0] == r[0] and P[i + 1][2] == r[2]: gaps.append(P[i + 1][4] - (r[16] + 2 * lat))
            rempl_ann += r[20] or 0
        X = [x for x in V.get(v, []) if x["start"] in cyc]; parts = sum(x["remplP"] for x in X); usd = sum(x["remplP"] * x["prix"] for x in X)
        res = sum(x["resultat"]["prudent"] for x in X); part_ = sum(1 for x in X if 0 < x["remplP"] < x["parts"] - 0.05)
        bons = sum(1 for x in X if x.get("gagne") and x["remplP"] > 0); mins = actif_ms / 60000
        cap = (sum(notion) * (actif_ms / max(len(notion), 1)) / max(len(CYC) * 300000, 1)) if notion else 0
        w(f"| {v} | {len(P)} | {nrep} | {mins:.1f} | {attente / 1000:.1f} | {np.median(gaps) if gaps else float('nan'):.0f} | {rempl_ann:.0f} | {part_} | {parts:.0f} | {res:+.0f} $ | "
          f"{(res / len(P) if P else float('nan')):+.3f} $ | {(res / mins if mins else float('nan')):+.2f} $ | {(res / usd if usd else float('nan')):+.2f} | {cap:.1f} $ | {max(0, ref_bons - bons) if v != 'M2 cotation marge 5 c' else '—'} |")
    w("\nUne durée courte n'est pas meilleure parce qu'elle évite des remplissages toxiques : il faut regarder le résultat par minute d'exposition et les bons remplissages manqués. "
      "La perte de priorité par remplacement est détaillée dans resultat_verifications_h559.md (section 2).\n")

    # ================================================ 5. file d'attente : 8 contrôles
    w("## 5. File d'attente — huit contrôles\n")
    ctl = collections.Counter(); indet = 0
    for v, X in V.items():
        for x in X:
            if x.get("mode") == "preneur" or x["start"] not in cyc: continue
            p_, c_, o_ = x["remplP"], x["remplR"], x.get("remplO", None)
            ctl["offres contrôlées"] += 1
            if p_ > c_ + 0.5: ctl["1. prudent > central"] += 1
            if o_ is not None and c_ > o_ + 0.5: ctl["2. central > optimiste"] += 1
            fp = sorted(ms for ms, k, q in x.get("rempl") or [] if k == "p"); fr = sorted(ms for ms, k, q in x.get("rempl") or [] if k == "r")
            if fp and fr and fp[0] + 1 < fr[0] and p_ <= c_ + 0.5: pass
            if fp and fr and fr[0] > fp[0] + 1: ctl["3. 1er remplissage prudent AVANT le central (ordre de priorité)"] += 1
            lat = x.get("lat_ms") or 15; arr = (x.get("tArrivee") or (x["tPose"] + lat)) - x["tPose"]
            if any(ms < arr - 0.5 for ms, k, q in x.get("rempl") or []): ctl["6. remplissage avant l'arrivée de l'offre"] += 1
            if x.get("tAnnulee"):
                fin = x["tAnnulee"] - x["tPose"]
                if any(ms > fin + 0.5 for ms, k, q in x.get("rempl") or []): ctl["8. remplissage après l'annulation effective"] += 1
            if x.get("tAnnulDemande") and not x.get("tAnnulee") and x.get("etat") == "annulee": ctl["7. annulée sans heure effective"] += 1
            if x["start"] in TRR:
                t0 = x.get("tArrivee") or x["tPose"] + lat; t1 = x.get("tAnnulee") or (x["start"] + 300) * 1000
                vol, trav = VH.volume_niveau(TRR[x["start"]], x["cote"] == "Up", x["prix"], t0 - 50, t1 + 50)
                if not trav and (o_ if o_ is not None else c_) > vol + 0.5: ctl["5. parts remplies > volume échangé à notre prix"] += 1
            else: indet += 1
    w(f"Offres remplies contrôlées : {ctl['offres contrôlées']} (indéterminées faute de transactions enregistrées : {indet}).\n")
    for k in ("1. prudent > central", "2. central > optimiste", "3. 1er remplissage prudent AVANT le central (ordre de priorité)", "5. parts remplies > volume échangé à notre prix",
              "6. remplissage avant l'arrivée de l'offre", "7. annulée sans heure effective", "8. remplissage après l'annulation effective"):
        w(f"- {k} : **{ctl[k]}**")
    w("- 4. double comptage d'un retrait entre fantômes : corrigé dans le code le 11.10 à 14:55 (une seule attribution transaction / retrait par baisse du niveau, partagée par tous les fantômes) ; "
      "les remplissages d'avant ne sont pas utilisés ici. Les fantômes restent simulés SEULS face au carnet : leurs résultats ne s'additionnent pas.")
    w("\nDéfaut connu (contrôle 1) : seule la borne prudente est plafonnée à la quantité affichée ; la centrale et l'optimiste ne le sont pas. Fantômes gelés : pas de correction avant le verdict. "
      "Annulation : effective chez Polymarket après le trajet simple (≈ 15 ms) ; un remplissage entre la demande et cet instant est compté (comme en réel). Aucune de ces bornes n'est notre position réelle dans la file.\n")

    # ================================================ 6. M8
    w("## 6. M8 — routeur maker / preneur\n")
    w("Formule actuelle (code gelé) — PRENEUR : parts disponibles au prix vu (50 $) × probabilité du modèle − coût frais compris ; le retard de 150 ms et la disparition de l'offre "
      "n'entrent PAS dans la décision (seulement dans l'exécution simulée). MAKER : parts attendues en 10 s × (probabilité du modèle − prix − 2 c) ; ce n'est PAS « probabilité de "
      "remplissage × gain conditionnel au remplissage » : la sélection adverse est une constante (2 c) au lieu de la probabilité de victoire SACHANT le remplissage. "
      "Abstention : oui, si aucune voie n'a une espérance positive (preneur) ou ≥ 0,50 $ (maker). **Non conforme à la formule demandée** ; version conforme proposée après le verdict, M8 actuel inchangé.\n")
    m8 = [x for v, X in V.items() if v.startswith("M8") for x in X if x["start"] in cyc]
    nsig = sum(SIGcyc.values())
    w("| Décision | Nombre | Remplies | Parts | Résultat prudent | Jackpots (≤ 0,25 gagnés) | Creux |\n|---|---|---|---|---|---|---|")
    for mode in ("preneur", "maker"):
        X = [x for x in m8 if (x.get("mode") or "maker") == mode]; pc = collections.defaultdict(float)
        for x in X: pc[x["start"]] += x["resultat"]["prudent"]
        w(f"| {mode} | {len(X)} | {sum(1 for x in X if x['remplP'] > 0)} | {sum(x['remplP'] for x in X):.0f} | {sum(pc.values()):+.0f} $ | {sum(1 for x in X if x['remplP'] > 0 and x['prix'] <= JACKPOT and x.get('gagne'))} | {creux(pc):+.0f} $ |")
    w(f"| abstention | {max(0, nsig - len(m8))} (signaux sans décision M8) | — | — | — | — | — |")

    # ================================================ 7 + 8. comparaison des moteurs, délai preneur
    w("\n## 7–8. Comparaison des moteurs sur les mêmes cycles (délai preneur : plusieurs scénarios)\n")
    tous_cyc = sorted(cyc & set(SIGc.keys()))
    w(f"Cycles communs : {len(tous_cyc)}. FAST / SLOW / HYBRID : achat preneur de 50 $ au prix du signal ou mieux, frais 0,07·p·(1−p), aux délais 0 / 50 / 150 / 250 ms (150 = HYPOTHÈSE documentée).\n")
    def lignes_moteur(nom, pos):
        # pos : liste de (start, mise $, résultat $, gagné bool, prix, frais, restant_s, markout3 c/part ou None)
        pc = collections.defaultdict(float)
        for p in pos: pc[p[0]] += p[2]
        r = sum(pc.values()); mise = sum(p[1] for p in pos); jack = sum(1 for p in pos if p[4] is not None and p[4] <= JACKPOT and p[3])
        mo = [p[7] for p in pos if p[7] is not None]
        return (f"| {nom} | {len(pos)} | {mise:.0f} $ | {np.mean([p[4] for p in pos if p[4] is not None]) if pos else float('nan'):.3f} | {sum(p[5] for p in pos):.0f} $ | {r:+.0f} $ | {fic(ic(pc))} | "
                f"{(np.mean(mo) if mo else float('nan')):+.1f} | {creux(pc):+.0f} $ | {pire_serie([p[2] for p in sorted(pos)])} | {jack} |"), pc
    w("| Moteur | Positions | $ engagés (capital) | Prix moyen | Frais | Résultat | IC 90 % | Sélection adverse +3 s (c/part) | Creux max | Pire série de pertes | Jackpots |\n|---|---|---|---|---|---|---|---|---|---|---|")
    PCS = {}
    for dl in (0.0, 50.0, 150.0, 250.0):
        for k in ("FAST", "SLOW", "HYBRID"):
            pos = []
            for x in TOUR[dl]:
                if x["start"] not in tous_cyc or x[k][0] <= 0: continue
                q, c, r = x[k]; pos.append((x["start"], c, r, r > 0, c / q if q else None, q * 0.07 * (c / q) * (1 - c / q) if q else 0, None, None))
            if dl == 150.0 or k == "FAST":
                L, pc = lignes_moteur(f"{k} (délai {dl:.0f} ms)", pos); w(L); PCS[f"{k} {dl:.0f}"] = pc
    for nom, pre in (("M0 témoin", "M0"), ("M1 maker sur signal", "M1"), ("M2 marge 5 c", "M2 cotation marge 5 c"), ("M4", "M4 retrait toxique"), ("M4a", "M4a"), ("M4b", "M4b"),
                     ("M4c", "M4c"), ("M6 100 ms", "M6 duree de vie 100 ms"), ("M6 250 ms", "M6 duree de vie 250 ms"), ("M6 500 ms", "M6 duree de vie 500 ms"),
                     ("M6 1000 ms", "M6 duree de vie 1000 ms"), ("M8 routeur", "M8")):
        pos = []
        for v, X in V.items():
            if not v.startswith(pre): continue
            for x in X:
                if x["start"] not in tous_cyc or x["remplP"] <= 0: continue
                mise = x.get("cout") or x["remplP"] * x["prix"]; a = (x.get("mo") or {}).get("p", {}).get("3")
                pos.append((x["start"], mise, x["resultat"]["prudent"], bool(x.get("gagne")), x["prix"], (x.get("cout", 0) - x["remplP"] * x["prix"]) if x.get("mode") == "preneur" else 0.0,
                            x.get("restantPose_s"), (100 * a[0] / a[1]) if a and a[1] else None))
        L, pc = lignes_moteur(nom + " (prudent)", pos); w(L); PCS[nom] = pc
    w("\n**Résultat marginal contre M4 et contre M0 (différence par cycle, IC 90 %)** :\n")
    for nom in [k for k in PCS if k not in ("M4", "M0 témoin")]:
        for ref in ("M4", "M0 témoin"):
            d = {c: PCS[nom].get(c, 0.0) - PCS.get(ref, {}).get(c, 0.0) for c in tous_cyc}
            w(f"- {nom} − {ref} : {sum(d.values()):+.0f} $ {fic(ic(d))}")
    w("\n**Par temps restant à la pose (makers, prudent)** :\n")
    w("| Moteur | 180–300 s | 60–180 s | 0–60 s |\n|---|---|---|---|")
    for nom, pre in (("M0", "M0"), ("M1", "M1"), ("M2 5 c", "M2 cotation marge 5 c"), ("M4", "M4 retrait toxique"), ("M5", "M5"), ("M6 1000 ms", "M6 duree de vie 1000 ms"), ("M8", "M8")):
        cells = []
        for lo, hi in ((180, 301), (60, 180), (0, 60)):
            X = [x for v, L in V.items() if v.startswith(pre) for x in L if x["start"] in tous_cyc and x["remplP"] > 0 and x.get("restantPose_s") is not None and lo <= x["restantPose_s"] < hi]
            n = len(X); cells.append(f"{sum(x['resultat']['prudent'] for x in X):+.0f} $ ({n}{' — insuffisant' if n < 30 else ''})")
        w(f"| {nom} | " + " | ".join(cells) + " |")
    w("\n## 9–10. Limites\n- Données d'une seule journée pour la version du 11.10 14:55 : la plupart des lignes sont INSUFFISANTES.\n"
      "- Remplissages simulés (trois bornes), jamais des exécutions réelles ; retard preneur de 150 ms non mesuré (test réel de 1 $ soumis à ton accord).\n"
      "- Les fantômes sont simulés seuls : leurs résultats ne s'additionnent pas.\n- Aucune règle n'a été réglée sur ces chiffres ; la période réservée du 13.10 n'est pas lue.\n")
    open(SORTIE, "w").write("\n".join(o)); print("\n".join(o))


if __name__ == "__main__":
    main()
