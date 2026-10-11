"""BOT95 — H559–H564 : décomposition de M4, durée de vie des cotations, début de cycle, file d'attente à 3 bornes, hybride maker/preneur.
Demande de Pitch, 11.10.2026 14:45. Hors ligne, aucun bot modifié, aucun ordre. Période réservée (≥ 13.10.2026 00:00 UTC) non lue,
sauf avec --hors-echantillon (verdict). Usage : python3 etude/bot5min/maker_h559.py dossier_des_cycles [--hors-echantillon]
→ etude/bot5min/resultat_maker_h559.md (ou resultat_maker_h559_hors_echantillon.md)"""
import gzip, json, os, sys, glob, collections, time
import numpy as np

ICI = os.path.dirname(os.path.abspath(__file__)); RACINE = os.path.abspath(os.path.join(ICI, "..", ".."))
HORS_ECH = 1791849600
HORS = "--hors-echantillon" in sys.argv
SORTIE = os.path.join(ICI, "resultat_maker_h559_hors_echantillon.md" if HORS else "resultat_maker_h559.md")
garde = lambda st: (st >= HORS_ECH) == HORS
BORNES = (("prudent", "remplP"), ("proportionnel", "remplR"), ("optimiste", "remplO"))


def ic_blocs(par_cycle, n=2000):
    v = np.array(list(par_cycle.values()), dtype=float)
    if len(v) < 3: return None
    rng = np.random.default_rng(3); b = [v[rng.integers(0, len(v), len(v))].sum() for _ in range(n)]
    return np.percentile(b, [5, 95])


def creux(par_cycle):
    if not par_cycle: return 0.0
    c = np.cumsum([par_cycle[k] for k in sorted(par_cycle)]); return float(np.min(c - np.maximum.accumulate(np.concatenate([[0], c]))[1:]))


def main():
    dossier = [a for a in sys.argv[1:] if not a.startswith("--")][0]
    # offres posées (toutes, y compris non remplies) depuis les cycles
    POSE = collections.defaultdict(lambda: collections.Counter()); ncy = 0; cycles = set()
    for fn in sorted(glob.glob(os.path.join(dossier, "**", "*.json.gz"), recursive=True)):
        st = int(os.path.basename(fn).split(".")[0])
        if not garde(st): continue
        R = json.load(gzip.open(fn)); ncy += 1
        for r in R.get("mk", []):
            v = r[0]; c = POSE[v]; c["offres"] += 1; c["rejetees"] += r[5] == "rejetee"; cycles.add(st)
            c["remplies_p"] += (r[7] or 0) > 0; c["remplies_r"] += (r[8] or 0) > 0; c["remplies_o"] += (len(r) > 18 and (r[18] or 0) > 0)
            if len(r) > 19: c["pendant_annulation_parts"] += r[19] or 0
    MK = json.load(open(os.path.join(RACINE, "bot95", "rapide_maker.json")))
    MK = [x for x in MK if x.get("type") != "resume" and x.get("resultat") and garde(x["start"])]
    V = collections.defaultdict(list)
    for x in MK: V[x["variante"]].append(x)
    o = []; w = o.append
    w("# Bot95 — H559–H564 : makers (diagnostic PRÉLIMINAIRE, non validé statistiquement)\n")
    w(f"Généré le {time.strftime('%d.%m.%Y %H:%M', time.gmtime())} UTC. {ncy} cycles {'HORS ÉCHANTILLON (≥ 13.10.2026 00:00 UTC)' if HORS else 'avant la période réservée'}. "
      "Remplissages SIMULÉS selon trois bornes de file d'attente (prudente, centrale, optimiste) : aucun n'est une exécution garantie.\n")

    def table(noms, titre):
        w(f"### {titre}\n")
        w("| Variante | Offres posées | Remplies (prudent / central / optimiste) | Parts remplies prudent | $ exécutés prudent | Résultat prudent [IC 90 %] | Central | Optimiste | par $ (prudent) | Creux max (prudent) | Sélection adverse +1 / +3 / +5 / +10 s (c/part, prudent) | Parts remplies pendant l'annulation |")
        w("|---|---|---|---|---|---|---|---|---|---|---|---|")
        for v in noms:
            X = V.get(v, []); P = POSE.get(v, collections.Counter())
            parts = sum(x["remplP"] for x in X); usd = sum(x["remplP"] * x["prix"] for x in X) if not v.startswith("M8") else sum((x.get("cout") or x["remplP"] * x["prix"]) for x in X)
            res = {}
            for nom, _ in BORNES: res[nom] = sum((x["resultat"].get(nom) or 0) for x in X)
            pc = collections.defaultdict(float)
            for x in X: pc[x["start"]] += x["resultat"]["prudent"]
            ic = ic_blocs(pc); mo = []
            for h in ("1", "3", "5", "10"):
                a = sum((x.get("mo") or {}).get("p", {}).get(h, [0, 0])[0] for x in X); b = sum((x.get("mo") or {}).get("p", {}).get(h, [0, 0])[1] for x in X)
                mo.append(f"{100 * a / b:+.1f}" if b else "—")
            ann = sum(x.get("annulP", 0) or 0 for x in X)
            w(f"| {v} | {P['offres'] or '—'} | {P['remplies_p']} / {P['remplies_r']} / {P['remplies_o']} | {parts:.0f} | {usd:.0f} $ | {res['prudent']:+.0f} $ "
              + (f"[{ic[0]:+.0f} ; {ic[1]:+.0f}]" if ic is not None else "[—]") + f" | {res['proportionnel']:+.0f} $ | {res['optimiste']:+.0f} $ | {(res['prudent'] / usd if usd else float('nan')):+.2f} | {creux(pc):+.0f} $ | {' / '.join(mo)} | {ann:.0f} |")
        w("")
    w("## 1. Décomposition de M4 (retrait sur flux toxique)\n")
    w("M4a, M4b, M4c gardent UNE seule des trois conditions de M4 (a : bourses −10 $ en 300 ms ; b : flux agressif net ≥ 250 000 $ contre nous en 250 ms ; "
      "c : ≥ 100 parts vendues sur nos acheteurs en 500 ms). Même prix que M2 marge 5 c ; seule la règle de retrait change.\n")
    table(["M0 temoin aleatoire", "M2 cotation marge 5 c", "M4 retrait toxique", "M4a seul bourses -10 $", "M4b seul flux agressif", "M4c seul ventes Polymarket"], "Comparaison directe (fantômes en parallèle sur les mêmes cycles)")
    # remplissages M2 5 c selon les conditions actives au moment du remplissage
    G = collections.defaultdict(lambda: [0.0, 0.0, 0])
    for x in V.get("M2 cotation marge 5 c", []):
        g1 = 1.0 if x.get("gagne") else 0.0
        for q, fl in x.get("toxRempl") or []:
            for k in (["aucune"] if not fl else list(fl)):
                G[k][0] += q; G[k][1] += q * (g1 - x["prix"]); G[k][2] += 1
    if G:
        w("**Remplissages de M2 marge 5 c selon la condition toxique active au moment du remplissage (2 s)** — ce que chaque condition aurait évité :\n")
        w("| Condition active | Remplissages | Parts | Résultat de ces parts | par part |\n|---|---|---|---|---|")
        for k in ("aucune", "a", "b", "c"):
            if k in G: q, r, n = G[k]; w(f"| {k} | {n} | {q:.0f} | {r:+.0f} $ | {(100 * r / q if q else float('nan')):+.1f} c |")
        w("(une part peut compter dans plusieurs conditions ; mesure disponible depuis la version du 11.10 14:50)\n")
    w("## 2. Durée de vie des cotations (M6)\n")
    w("M2 marge 5 c dont chaque offre est annulée après L ms ; la suivante n'est posée qu'après confirmation de l'annulation (aller-retour mesuré). "
      "Les parts remplies pendant le trajet de l'annulation sont comptées (dernière colonne).\n")
    table(["M2 cotation marge 5 c"] + [f"M6 duree de vie {L} ms" for L in (100, 250, 500, 1000)], "Durées de vie")
    w("## 3. Début de cycle (180–300 s restantes) contre le reste\n")
    w("| Variante | Temps restant à la pose | Offres remplies | $ exécutés | Résultat prudent [IC 90 %] | par $ |\n|---|---|---|---|---|---|")
    for v in ("M2 cotation marge 5 c", "M4 retrait toxique", "M5 remplissage attendu", "M0 temoin aleatoire"):
        for lo, hi in ((180, 301), (60, 180), (0, 60)):
            X = [x for x in V.get(v, []) if x.get("restantPose_s") is not None and lo <= x["restantPose_s"] < hi]
            usd = sum(x["remplP"] * x["prix"] for x in X); r = sum(x["resultat"]["prudent"] for x in X)
            pc = collections.defaultdict(float)
            for x in X: pc[x["start"]] += x["resultat"]["prudent"]
            ic = ic_blocs(pc)
            w(f"| {v} | {lo}–{min(hi, 300)} s | {len(X)} | {usd:.0f} $ | {r:+.0f} $ " + (f"[{ic[0]:+.0f} ; {ic[1]:+.0f}]" if ic is not None else "[—]") + f" | {(r / usd if usd else float('nan')):+.2f} |")
    w("\nAucune conclusion à ce stade (trop peu de remplissages).\n")
    w("## 4. File d'attente : trois bornes\n")
    w("Prudente : seules les transactions nous font avancer. Centrale : un retrait sans transaction libère la file au prorata de notre place. "
      "Optimiste : tout retrait sans transaction vient de devant nous. Les trois colonnes de résultat des tableaux ci-dessus correspondent à ces bornes.\n")
    table(["M2 cotation marge 10 c", "M3 anticipation Chainlink", "M5 remplissage attendu"], "Autres variantes permanentes")
    w("## 5. Hybride maker / preneur (M8) contre M1 sur les mêmes signaux\n")
    m8 = [v for v in V if v.startswith("M8")]; m1 = [v for v in V if v.startswith("M1")]
    for grp, nom in ((m1, "M1 (toujours maker)"), (m8, "M8 hybride")):
        X = [x for v in grp for x in V[v]]; pr = [x for x in X if x.get("mode") == "preneur"]; mk = [x for x in X if x.get("mode") != "preneur"]
        pc = collections.defaultdict(float)
        for x in X: pc[x["start"]] += x["resultat"]["prudent"]
        ic = ic_blocs(pc); r = sum(pc.values())
        w(f"- {nom} : {len(X)} positions ({len(pr)} preneur, {len(mk)} maker), résultat prudent {r:+.0f} $ " + (f"[IC 90 % {ic[0]:+.0f} ; {ic[1]:+.0f}]" if ic is not None else "") + f", creux {creux(pc):+.0f} $")
    w("\nLe tournoi FAST / SLOW / HYBRID (preneur) sur les mêmes signaux est dans resultat_fast_fenetre.md, section 6.\n")
    w("## 6. Retard preneur\nLe retard de 150 ms vient de la documentation Polymarket (changelog du 04.09.2026) et du drapeau itode=true de nos marchés ; "
      "il n'est PAS mesuré sur notre infrastructure. M8 et FAST l'utilisent comme hypothèse. Seul un ordre réel (test de 1 $, en attente de l'accord de Pitch) peut le mesurer.\n")
    w("## 7. Validation\nPériode réservée : cycles à partir du 13.10.2026 00:00 UTC, jamais utilisée pour régler une règle. Verdict avec --hors-echantillon après plusieurs jours.\n")
    open(SORTIE, "w").write("\n".join(o)); print("\n".join(o))


if __name__ == "__main__":
    main()
