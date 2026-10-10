"""BOT95 V3 — expérience 004 SURVIE DE L'OFFRE (FILL SURVIVAL), hors ligne.
Pour chaque signal des 7 stratégies : l'offre vue à la décision est-elle encore là après 0 / 0,25 / 0,5 / 1 s ? à quel prix, quelle quantité ?
Variantes de tolérance : on accepte de payer le prix de décision (0), +1 c, +2 c. Meilleur vendeur seul (les lignes enregistrées ne donnent que le meilleur niveau),
quantité affichée, frais inclus, 50 $ max. Délais : la première ligne enregistrée à t + délai ou après (lignes ~0,3 s : 0,25 → ~0,3 s ; 0,5 → ~0,6 s ; 1 → ~1,2 s).
Complément 100 ms : les photos /api/lead (premier désaccord ≥ 0,20 du cycle, vu en direct) donnent le carnet Polymarket à 3 niveaux toutes les 100 ms après le signal.
Maker : pas mesurable (voir le texte)."""
exec(open("etude/bot5min/v3_commun.py").read())
DELAIS = (0, 0.25, 0.5, 1.0); TOLS = (0, 0.01, 0.02)
out = ["# BOT95 V3 — Expérience 004 : l'offre est-elle encore là ? (FILL SURVIVAL)", "", ENTETE, "",
       "**Exécution simulée** (pas théorique) : à t + délai, on achète au seul meilleur vendeur de la ligne enregistrée, dans la quantité affichée, si son prix ≤ prix de décision + tolérance. "
       "Délai 0 = la ligne même de la décision (latence nulle : borne optimiste). Les lignes arrivent toutes les ~0,3 s : **les délais 50 ms et 100 ms ne sont pas mesurables** avec les lignes ; "
       "délai réel ≈ 0,3 / 0,6 / 1,2 s pour 0,25 / 0,5 / 1 s demandés. Les lignes ne donnent que le MEILLEUR niveau : avec +1 c / +2 c, on ne prend que le meilleur vendeur du moment "
       "s'il est dans la tolérance — la profondeur des niveaux suivants est inconnue (achat partiel possible alors qu'en réalité on aurait pu compléter au niveau suivant).", ""]
SYN = {}
for n in NOMS7:
    S = STRATS[n]
    out += [f"## {n} — {len(S)} signaux", "",
            "| Délai demandé | Tolérance | Exécutés | Offre partie (prix monté) | Quantité < 1 part | Délai réel médian | Prix payé moyen | Glissement moyen | Achats partiels (< 50 $) | Mise moyenne | Frais totaux | "
            "Résultat net | sans top 5 | Espérance / achat | IC 90 % | valid. | inédit |", "|---" * 17 + "|"]
    for dl in DELAIS:
        for tol in TOLS:
            R = {st: exe(st, s, dl, tol, detail=True) for st, s in S.items()}
            ok = [x for x in R.values() if isinstance(x, dict)]
            b = bilan(ok, valides); SYN[(n, dl, tol)] = b
            bv = sum(x["pn"] for x in ok if PER(x["st"]) == "validation"); bi = sum(x["pn"] for x in ok if PER(x["st"]) == "inédit")
            SYN[(n, dl, tol, "v")] = bv; SYN[(n, dl, tol, "a")] = sum(x["pn"] for x in ok if PER(x["st"]) == "apprentissage"); SYN[(n, dl, tol, "i")] = bi
            nr = collections.Counter(x for x in R.values() if isinstance(x, str))
            out.append(f"| {dl:g} s | +{100 * tol:.0f} c | {len(ok)} ({100 * len(ok) / len(S):.0f} %) | {nr['prix']} | {nr['quantite']} | "
                       f"{np.median([x['dt'] for x in ok]) if ok else 0:.2f} s | {np.mean([x['a'] for x in ok]):.3f} | {100 * np.mean([x['slip'] for x in ok]):+.2f} c | "
                       f"{sum(x['partiel'] for x in ok)} ({100 * sum(x['partiel'] for x in ok) / max(1, len(ok)):.0f} %) | {np.mean([x['mise'] for x in ok]):.1f} $ | {f0(sum(x['fee'] for x in ok))} | "
                       f"**{f0(b['pnl'])}** | {f0(b['sans'][5])} | {fe(b['esp'])} | [{f0(b['lo'])} ; {f0(b['hi'])}] | {f0(bv)} | {f0(bi)} |")
    out.append("")
# ---------- synthèse compacte
out += ["## Synthèse : résultat net selon le délai (tolérance 0 c) et coût de la latence", "",
        "| Stratégie | 0 s | 0,25 s | 0,5 s | 1 s | Perte 0 → 0,5 s | Meilleure tolérance à 0,5 s (app. seulement) | Résultat à 0,5 s avec cette tolérance : valid. · inédit |", "|---|---|---|---|---|---|---|---|"]
for n in NOMS7:
    tb = max(TOLS, key=lambda t: SYN[(n, 0.5, t, "a")])
    out.append(f"| {n} | " + " | ".join(f0(SYN[(n, dl, 0)]["pnl"]) for dl in DELAIS) + f" | {f0(SYN[(n, 0.5, 0)]['pnl'] - SYN[(n, 0, 0)]['pnl'])} | +{100 * tb:.0f} c | "
               f"{f0(SYN[(n, 0.5, tb, 'v')])} · {f0(SYN[(n, 0.5, tb, 'i')])} |")
out += ["", "La tolérance « choisie » ne l'est que sur l'apprentissage, puis lue sur validation et inédit (aucun choix sur ces périodes).", ""]
# ---------- complément 100 ms : photos lead
DL = json.load(gzip.open("bot95/lead.json.gz", "rt"))
AV, AP = {}, collections.defaultdict(list)
for d in sorted(DL, key=lambda x: x["t"]):
    if d["phase"] == "avant": AV.setdefault(d["start"], d)
    else: AP[d["start"]].append(d)
DL100 = (0, 0.1, 0.2, 0.3, 0.5, 1.0)
res = {(dl, tol): [] for dl in DL100 for tol in TOLS}; nsig = 0; cnt = collections.Counter()
for st, d in AV.items():
    g = (O.get(f"BTC:{st}") or {}).get("gagnant"); apr = min(AP.get(st, []), key=lambda x: abs(x["t"] - 10 - d["t"]), default=None)
    if not g or not apr or abs(apr["t"] - 10 - d["t"]) >= 1: continue
    nsig += 1; up = d["cote"] == "Up"; gm = (g == "Up") == up; kb = apr["colonnes"].index(f"pm_{'up' if up else 'down'}_ventes_top3")
    for dl in DL100:
        l = next((x for x in apr["lignes"] if x[0] >= d["t"] + dl - 0.03), None)
        for tol in TOLS:
            if l is None: continue
            q = cout = fee = 0.0
            for p, z in l[kb] or []:
                if p > d["ask"] + tol + 1e-9: break
                x = min(z, (50 - cout) / p)
                if x <= 0: break
                q += x; cout += x * p; fee += x * FEE(p)
            if q >= 1: res[(dl, tol)].append(dict(st=st, pn=q * (1 if gm else 0) - cout - fee, mise=cout, gm=gm, a=cout / q, slip=cout / q - d["ask"], partiel=cout < 50 - 1e-6, top=d["ask"]))
out += ["## Complément à 100 ms : premier désaccord ≥ 0,20 vu par le bot en direct (photos /api/lead)", "",
        f"{nsig} signaux avec photo « après » et résultat officiel (07.10 15:43 → 10.10 13:45). Carnet Polymarket à 3 niveaux toutes les 100 ms ; on balaie les niveaux ≤ prix du signal + tolérance jusqu'à 50 $. "
        "C'est la seule mesure à 100 ms disponible ; elle ne concerne que le signal « désaccord 20 » (premier franchissement du cycle), pas les 7 stratégies. "
        "50 ms : pas mesurable (photos à 100 ms).", "",
        "| Délai | Tolérance | Exécutés | Part des signaux | Prix moyen | Glissement moyen | Achats partiels | Résultat net | sans top 5 | Espérance / achat | IC 90 % | app. · valid. · inédit |", "|---" * 12 + "|"]
cycL = sorted(AV)
for dl in DL100:
    for tol in TOLS:
        L = res[(dl, tol)]; b = bilan(L, cycL)
        pp = " · ".join(f0(sum(x["pn"] for x in L if PER(x["st"]) == p)) for p in PERS)
        out.append(f"| {dl:g} s | +{100 * tol:.0f} c | {len(L)} | {100 * len(L) / max(1, nsig):.0f} % | {np.mean([x['a'] for x in L]):.3f} | {100 * np.mean([x['slip'] for x in L]):+.2f} c | "
                   f"{100 * sum(x['partiel'] for x in L) / max(1, len(L)):.0f} % | **{f0(b['pnl'])}** | {f0(b['sans'][5])} | {fe(b['esp'])} | [{f0(b['lo'])} ; {f0(b['hi'])}] | {pp} |")
out += ["", "## Ordres passifs (maker)", "",
        "**Non mesurable honnêtement avec les données actuelles.** Pour simuler un ordre posé au meilleur acheteur, il faudrait (1) notre position dans la file d'attente au prix posé, "
        "(2) les transactions qui ont réellement eu lieu à ce prix (qui a vendu, combien), (3) savoir si l'exécution arrive surtout quand le prix part contre nous (sélection adverse). "
        "Les lignes enregistrées n'ont que le meilleur niveau ; les photos lead ont des flux agrégés (retraits / ajouts / échanges) sans prix ni ordre d'arrivée. "
        "Toute hypothèse de file (« on est servi quand la taille devant nous a été échangée ») serait inventée ; nous ne publions donc aucun chiffre maker.", ""]
open("etude/bot5min/resultat_v3_exp004.md", "w").write("\n".join(out)); print("\n".join(out))
