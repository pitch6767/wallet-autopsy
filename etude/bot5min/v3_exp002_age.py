"""BOT95 V3 — expérience 002 MICRO-ÂGE du désaccord (hors ligne).
Âge = temps écoulé depuis que l'écart (modèle − meilleur vendeur, même côté, même modèle que la stratégie) a franchi 0,20 pour la dernière fois
(épisode continu : toutes les lignes ≥ 0,20, pas de trou > 1 s). Résolution = intervalle entre lignes enregistrées (~0,3 s) : le vrai franchissement
a eu lieu entre la ligne précédente et la ligne où on le voit ; les fenêtres 0-50 / 50-100 ms ne sont PAS mesurables (VPS de Dublin, rapide.js).
Seuils de tranches fixés d'avance par le plan (0-250, 250-500, 500-1000, > 1000 ms) — aucun réglage."""
exec(open("etude/bot5min/v3_commun.py").read())
def edge_fn(model, st):
    cache = {}
    def e(k, up):
        r = C[st][k]; a = r[4] if up else r[6]
        if a is None or not (0.03 <= a <= 0.97): return None
        p = r[2] if model == "O8" else proba("H1", st, k, cache)
        if p is None: return None
        return (p if up else 1 - p) - a
    return e
def age(st, s, model):
    e = edge_fn(model, st); R_ = C[st]; i = s["i"]; up = s["up"]; j = i
    while j - 1 >= 0 and R_[j][0] - R_[j - 1][0] < 1.0:
        x = e(j - 1, up)
        if x is None or x < 0.20: break
        j -= 1
    k0 = next((k for k in range(0, i + 1) if (e(k, up) or -1) >= 0.20), i)
    return R_[i][0] - R_[j][0], R_[i][0] - R_[k0][0], k0 == j
TR_ = [(0, 0.25, "0-250 ms (vu à la ligne même du franchissement)"), (0.25, 0.5, "250-500 ms (1 ligne plus tard)"), (0.5, 1.0, "500-1000 ms (2-3 lignes)"), (1.0, 1e9, "> 1000 ms")]
def tranche(a):
    for lo, hi, n in TR_:
        if lo - 1e-6 <= a < hi - 1e-6: return n
out = ["# BOT95 V3 — Expérience 002 : micro-âge du désaccord", "", ENTETE, "",
       "**Résolution** : les lignes enregistrées arrivent toutes les ~0,3 s (voir l'audit). Un âge mesuré de 0 veut dire « franchi depuis la ligne précédente », c'est-à-dire entre 0 et ~300 ms ; "
       "0,3 s mesuré = 300-600 ms réels, etc. Les tranches 0-250 / 250-500 ms sont donc approximatives, et **les fenêtres 0-50 ms et 50-100 ms ne sont pas mesurables avec les données actuelles** : "
       "le nouveau programme du VPS de Dublin (`bot95/rapide/rapide.js`) les mesurera à la milliseconde.", "",
       "Exécution : meilleur vendeur seul, quantité affichée, prix ≤ prix de décision, 50 $ max, frais inclus ; délai 0 (ligne de décision) et délai 0,5 s demandé (~0,6 s réel).", ""]
# ---------- A. âge des signaux V2-F
out += ["## A. Âge du désaccord au moment des signaux V2-F", "",
        "« Nouveau » = l'épisode en cours est le premier du cycle de ce côté ; « reprise » = un écart ≥ 0,20 de ce côté avait déjà existé puis disparu dans le cycle.", ""]
AGES = {}
for nom, model in (("V2-F original (O8)", "O8"), ("V2-F 0,01 % (H1)", "H1")):
    S = STRATS[nom]; A = {st: age(st, s, model) for st, s in S.items()}; AGES[nom] = A
    for per_nom, filt in (("toutes périodes", lambda st: True), ("apprentissage", lambda st: PER(st) == "apprentissage"),
                          ("validation", lambda st: PER(st) == "validation"), ("inédit", lambda st: PER(st) == "inédit")):
        cyc = [st for st in valides if filt(st)]
        out += [f"### {nom} — {per_nom}", "", hdr("Âge de l'épisode").split("\n")[0] + " Signaux | Prix payé moyen | Taille affichée médiane (parts) | Écart médian | Résultat délai 0,5 s |",
                "|---" * 17 + "|"]
        for lo, hi, tn in TR_:
            L = [st for st in S if filt(st) and tranche(A[st][0]) == tn]
            tr = [exe(st, S[st]) for st in L]; b = bilan(tr, cyc); ok = [x for x in tr if x]
            z = [(C[st][S[st]["i"]][8] if S[st]["up"] else C[st][S[st]["i"]][10]) or 0 for st in L]
            out.append(lig(tn, b) + f" {len(L)} | {np.mean([x['a'] for x in ok]) if ok else float('nan'):.2f} | {np.median(z) if z else 0:.0f} | "
                       f"{np.median([S[st]['fair'] - S[st]['a'] for st in L]) if L else float('nan'):.2f} | {f0(sum((exe(st, S[st], 0.5) or {}).get('pn', 0) for st in L))} |")
        for lab, f_ in (("nouveau (1er épisode du cycle)", lambda st: A[st][2]), ("reprise (épisode déjà vu puis disparu)", lambda st: not A[st][2])):
            L = [st for st in S if filt(st) and f_(st)]; tr = [exe(st, S[st]) for st in L]; b = bilan(tr, cyc); ok = [x for x in tr if x]
            z = [(C[st][S[st]["i"]][8] if S[st]["up"] else C[st][S[st]["i"]][10]) or 0 for st in L]
            out.append(lig(lab, b) + f" {len(L)} | {np.mean([x['a'] for x in ok]) if ok else float('nan'):.2f} | {np.median(z) if z else 0:.0f} | "
                       f"{np.median([S[st]['fair'] - S[st]['a'] for st in L]) if L else float('nan'):.2f} | {f0(sum((exe(st, S[st], 0.5) or {}).get('pn', 0) for st in L))} |")
        out.append("")
    al = np.array([A[st][0] for st in S]); out += [f"Répartition des âges ({nom}, {len(al)} signaux) : médiane {np.median(al):.1f} s, 75 % {np.percentile(al, 75):.1f} s, 90 % {np.percentile(al, 90):.1f} s ; "
                                                     f"âge depuis le 1er franchissement du cycle : médiane {np.median([A[st][1] for st in S]):.1f} s.", ""]
# ---------- B. désaccord 20 : même opportunité, décision prise à des âges différents
out += ["## B. Premier désaccord ≥ 0,20 du cycle (modèle du bot O8) : décider à 0, 0,25, 0,5, 1 ou 2 s d'âge", "",
        "Pour le signal « désaccord 20 » l'âge au signal est 0 par construction (premier franchissement du cycle). On mesure donc ce que vaut la MÊME opportunité si on décide plus tard : "
        "à l'âge X, on regarde la première ligne à t0 + X ou après ; si l'écart est resté ≥ 0,20 sans interruption, on achète au meilleur vendeur de CETTE ligne (nouvelle décision, prix du moment). "
        "« Mêmes cycles à l'âge 0 » = résultat de ces mêmes cycles achetés au franchissement : la différence isole l'effet du temps (prix et sélection des épisodes qui survivent).", ""]
eO8 = {}
for per_nom, filt in (("toutes périodes", lambda st: True), ("apprentissage", lambda st: PER(st) == "apprentissage"), ("validation", lambda st: PER(st) == "validation"), ("inédit", lambda st: PER(st) == "inédit")):
    cyc = [st for st in valides if filt(st)]; base = {st: s for st, s in D20.items() if filt(st)}
    out += [f"### {per_nom} ({len(base)} premiers désaccords)", "", hdr("Âge de décision").split("\n")[0] + " Épisodes encore vivants | Âge réel médian | Prix payé moyen | Taille affichée médiane | Mêmes cycles à l'âge 0 | Délai d'exécution 0,5 s |",
            "|---" * 18 + "|"]
    for X in (0, 0.25, 0.5, 1.0, 2.0):
        sel = {}
        for st, s in base.items():
            if st not in eO8: eO8[st] = edge_fn("O8", st)
            e = eO8[st]; R_ = C[st]; T_ = TT[st]; k = bisect.bisect_left(T_, s["t"] + X - 1e-6)
            if k >= len(R_) or R_[k][0] >= st + 295: continue
            vivant = all((e(j, s["up"]) or -1) >= 0.20 for j in range(s["i"], k + 1)) and all(R_[j][0] - R_[j - 1][0] < 1.0 for j in range(s["i"] + 1, k + 1))
            if vivant: sel[st] = dict(i=k, t=R_[k][0], up=s["up"], a=R_[k][4] if s["up"] else R_[k][6], tl=st + 300 - R_[k][0], fair=None, t0=s["t"])
        tr = [exe(st, x) for st, x in sel.items()]; b = bilan(tr, cyc); ok = [x for x in tr if x]
        z = [(C[st][x["i"]][8] if x["up"] else C[st][x["i"]][10]) or 0 for st, x in sel.items()]
        same0 = sum((exe(st, base[st]) or {}).get("pn", 0) for st in sel)
        out.append(lig(f"{X:g} s", b) + f" {len(sel)} ({100 * len(sel) / max(1, len(base)):.0f} %) | {np.median([x['t'] - x['t0'] for x in sel.values()]) if sel else 0:.2f} s | "
                   f"{np.mean([x['a'] for x in ok]) if ok else float('nan'):.2f} | {np.median(z) if z else 0:.0f} | {f0(same0)} | {f0(sum((exe(st, x, 0.5) or {}).get('pn', 0) for st, x in sel.items()))} |")
    out.append("")
out += ["## Ce qu'on ne peut pas mesurer ici", "",
        "- L'âge exact sous 300 ms (les tranches 0-50 et 50-100 ms du plan) : il faut l'horodatage à la milliseconde du programme `rapide.js` (VPS de Dublin).",
        "- La file d'attente au meilleur vendeur et qui nous devance sur l'offre : aucune donnée de transactions Polymarket dans les lignes.", ""]
open("etude/bot5min/resultat_v3_exp002.md", "w").write("\n".join(out)); print("\n".join(out))
