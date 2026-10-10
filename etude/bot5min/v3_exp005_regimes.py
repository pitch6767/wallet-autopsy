"""BOT95 V3 — expérience 005 MATRICE DES RÉGIMES (hors ligne).
7 stratégies × régimes mesurés AU MOMENT DE LA DÉCISION (ou au début du cycle pour la tendance), seuils fixés sur l'apprentissage seulement.
Exécution réaliste principale : délai 0,5 s demandé (~0,6 s réel), meilleur vendeur seul, quantité affichée, prix ≤ prix de décision, frais, 50 $ max.
Stabilité apprentissage → validation : accord de signe et corrélation de rang (Spearman) des espérances par case (cases ≥ 10 achats des deux côtés).
Intérêt ouvert : absent des données."""
exec(open("etude/bot5min/v3_commun.py").read())
DELAI = 0.5
def edge_fn(model, st):
    cache = {}
    def e(k, up):
        r = C[st][k]; a = r[4] if up else r[6]
        if a is None or not (0.02 <= a <= 0.98): return None
        p = r[2] if model == "O8" else proba("H1", st, k, cache)
        if p is None: return None
        return (p if up else 1 - p) - a
    return e
def age_ep(st, s, model):
    e = edge_fn(model, st); R_ = C[st]; i = s["i"]; j = i
    while j - 1 >= 0 and R_[j][0] - R_[j - 1][0] < 1.0:
        x = e(j - 1, s["up"])
        if x is None or x < 0.20: break
        j -= 1
    return R_[i][0] - R_[j][0]
def mv(st, t, col, a, b):
    """mouvement de la colonne col entre t−a et t−b (lignes enregistrées, dernière valeur connue)"""
    T_ = TT[st]; R_ = C[st]
    k1 = bisect.bisect_right(T_, t - b) - 1; k0 = bisect.bisect_right(T_, t - a) - 1
    if k0 < 0 or k1 < 0 or not R_[k1][col] or not R_[k0][col]: return None
    return R_[k1][col] - R_[k0][col]
# ---------- variables brutes par signal
RAW = {}
for n in NOMS7:
    for st, s in STRATS[n].items():
        r = C[st][s["i"]]; up = s["up"]; t = s["t"]; sg = 1 if up else -1
        bid = r[3] if up else r[5]; z = (r[8] if up else r[10]) or 0
        m5, m10 = mv(st, t, 11, 5, 0), mv(st, t, 11, 10, 5)
        RAW[(n, st)] = dict(h=time.gmtime(t + 7200).tm_hour, vol=vol(int(t)), acc=None if m5 is None or m10 is None else abs(m5) - abs(m10),
                            tend=RG[st]["tend"], taille=z, spread=None if bid is None else round(100 * (s["a"] - bid)), tl=s["tl"], up=up,
                            age=age_ep(st, s, "H1" if "H1" in n else "O8"))
APP_K = [k for k in RAW if PER(k[1]) == "apprentissage"]
VOL_MED = float(np.median([RAW[k]["vol"] for k in APP_K if RAW[k]["vol"] is not None]))
TAI_MED = float(np.median([RAW[k]["taille"] for k in APP_K]))
DIMS = [("Bloc horaire (heure suisse)", lambda x: ["00-06 h", "06-12 h", "12-18 h", "18-24 h"][x["h"] // 6]),
        ("Jour / nuit (nuit = 22-08 h suisse, fixé d'avance)", lambda x: "nuit" if (x["h"] >= 22 or x["h"] < 8) else "jour"),
        (f"Volatilité BTC (écart type du perp 1 s sur 5 min ; seuil = médiane app. {str(round(VOL_MED, 2)).replace('.', ',')} $/s)", lambda x: None if x["vol"] is None else ("vol. haute" if x["vol"] >= VOL_MED else "vol. basse")),
        ("Accélération (|perp 5 dernières s| contre |perp 5 s d'avant|)", lambda x: None if x["acc"] is None else ("accélère" if x["acc"] > 0 else "ralentit")),
        ("Tendance / range (15 min avant le cycle, seuil = médiane app., cf. META-ROUTER)", lambda x: x["tend"]),
        (f"Liquidité Polymarket affichée (taille au meilleur vendeur ; seuil = médiane app. {TAI_MED:.0f} parts)", lambda x: "taille ≥ médiane" if x["taille"] >= TAI_MED else "taille < médiane"),
        ("Écart acheteur-vendeur de notre côté", lambda x: None if x["spread"] is None else ("1 c" if x["spread"] <= 1 else "≥ 2 c")),
        ("Phase du cycle (temps restant)", lambda x: "> 180 s" if x["tl"] > 180 else ("60-180 s" if x["tl"] > 60 else "< 60 s")),
        ("Côté acheté", lambda x: "Up" if x["up"] else "Down"),
        ("Désaccord récent / persistant (âge de l'épisode ≥ 0,20)", lambda x: "récent (< 1 s)" if x["age"] < 1 else "persistant (≥ 1 s)")]
TRD = {dl: {(n, st): exe(st, s, dl) for n in NOMS7 for st, s in STRATS[n].items()} for dl in (0, DELAI)}
out = ["# BOT95 V3 — Expérience 005 : matrice stratégies × régimes", "", ENTETE, "",
       f"Exécution : délai {DELAI} s demandé (~0,6 s réel), meilleur vendeur seul, quantité affichée, prix ≤ prix de décision, frais, 50 $ max. "
       "Régimes mesurés à l'instant de la décision (sauf tendance : 15 min avant le début du cycle). Tous les seuils viennent de l'apprentissage ou sont fixés d'avance ; rien n'est réglé sur validation ou inédit. "
       "**Intérêt ouvert (open interest) : non disponible dans les données.**", "",
       "Chaque case : résultat net (nombre d'achats). Une case de moins de 10 achats ne dit rien.", ""]
CELL = {}
for titre, f in DIMS:
    niv = sorted({f(RAW[k]) for k in RAW if f(RAW[k]) is not None})
    out += [f"## {titre}", "", "| Stratégie | " + " | ".join(f"{v} : app. | valid. | inédit" for v in niv) + " |", "|---|" + "---|" * (3 * len(niv))]
    for n in NOMS7:
        cel = []
        for v in niv:
            for p in PERS:
                L = [TRD[DELAI][(n, st)] for st in STRATS[n] if PER(st) == p and f(RAW[(n, st)]) == v]
                L = [x for x in L if x]; CELL[(titre, n, v, p, DELAI)] = L
                L0 = [TRD[0][(n, st)] for st in STRATS[n] if PER(st) == p and f(RAW[(n, st)]) == v]; CELL[(titre, n, v, p, 0)] = [x for x in L0 if x]
                cel.append(f"{f0(sum(x['pn'] for x in L))} ({len(L)})")
        out.append(f"| {COURT[n]} | " + " | ".join(cel) + " |")
    out.append("")
# ---------- stabilité
def ranks(x):
    o = np.argsort(x); r = np.empty(len(x)); r[o] = np.arange(len(x)); return r
def spear(a, b): return float(np.corrcoef(ranks(np.array(a)), ranks(np.array(b)))[0, 1]) if len(a) >= 3 else float("nan")
out += ["## Stabilité apprentissage → validation", "",
        "Pour chaque case (stratégie × niveau de régime) ayant au moins 10 achats en apprentissage ET en validation : espérance par achat dans chaque période. "
        "Accord de signe = part des cases dont l'espérance a le même signe ; Spearman = corrélation de rang des espérances. Hasard pur ≈ 50 % d'accord et Spearman ≈ 0.", ""]
for dl in (DELAI, 0):
    out += [f"### Exécution délai {str(dl).replace('.', ',')} s", "", "| Dimension | Cases comparables | Accord de signe | Spearman | Cases positives en app. restées positives en valid. |", "|---|---|---|---|---|"]
    allA, allV = [], []
    for titre, f in DIMS:
        A, V = [], []
        niv = sorted({f(RAW[k]) for k in RAW if f(RAW[k]) is not None})
        for n in NOMS7:
            for v in niv:
                La, Lv = CELL[(titre, n, v, "apprentissage", dl)], CELL[(titre, n, v, "validation", dl)]
                if len(La) >= 10 and len(Lv) >= 10:
                    A.append(np.mean([x["pn"] for x in La])); V.append(np.mean([x["pn"] for x in Lv]))
        allA += A; allV += V
        acc = sum(1 for a, b in zip(A, V) if (a > 0) == (b > 0)); pos = [(a, b) for a, b in zip(A, V) if a > 0]
        out.append(f"| {titre.split(' (')[0]} | {len(A)} | {acc}/{len(A)} ({100 * acc / max(1, len(A)):.0f} %) | {spear(A, V):+.2f} | {sum(1 for a, b in pos if b > 0)}/{len(pos)} |")
    acc = sum(1 for a, b in zip(allA, allV) if (a > 0) == (b > 0))
    out += [f"| **toutes dimensions** | {len(allA)} | {acc}/{len(allA)} ({100 * acc / max(1, len(allA)):.0f} %) | {spear(allA, allV):+.2f} | "
            f"{sum(1 for a, b in zip(allA, allV) if a > 0 and b > 0)}/{sum(1 for a in allA if a > 0)} |", ""]
# mêmes chiffres sans l'effet « stratégie » : on retire à chaque case l'espérance de sa stratégie dans la période
out += ["### Effet du régime seul (on retire à chaque case l'espérance moyenne de la stratégie dans la même période), délai 0,5 s", "",
        "Sans cette correction, une stratégie bonne partout ferait croire à des régimes stables. Ici on ne compare que l'écart case − moyenne de la stratégie.", "",
        "| Dimension | Cases | Accord de signe | Spearman |", "|---|---|---|---|"]
moy = {(n, p): np.mean([x["pn"] for x in [TRD[DELAI][(n, st)] for st in STRATS[n] if PER(st) == p] if x] or [0]) for n in NOMS7 for p in PERS}
gA, gV = [], []
for titre, f in DIMS:
    A, V = [], []
    niv = sorted({f(RAW[k]) for k in RAW if f(RAW[k]) is not None})
    for n in NOMS7:
        for v in niv:
            La, Lv = CELL[(titre, n, v, "apprentissage", DELAI)], CELL[(titre, n, v, "validation", DELAI)]
            if len(La) >= 10 and len(Lv) >= 10:
                A.append(np.mean([x["pn"] for x in La]) - moy[(n, "apprentissage")]); V.append(np.mean([x["pn"] for x in Lv]) - moy[(n, "validation")])
    gA += A; gV += V; acc = sum(1 for a, b in zip(A, V) if (a > 0) == (b > 0))
    out.append(f"| {titre.split(' (')[0]} | {len(A)} | {acc}/{len(A)} ({100 * acc / max(1, len(A)):.0f} %) | {spear(A, V):+.2f} |")
acc = sum(1 for a, b in zip(gA, gV) if (a > 0) == (b > 0))
out += [f"| **toutes dimensions** | {len(gA)} | {acc}/{len(gA)} ({100 * acc / max(1, len(gA)):.0f} %) | {spear(gA, gV):+.2f} |", ""]
# cases les plus « prometteuses » de l'apprentissage et ce qu'elles deviennent
out += ["### Les 10 meilleures cases de l'apprentissage (≥ 20 achats) et ce qu'elles deviennent (délai 0,5 s)", "",
        "| Dimension | Stratégie | Niveau | app. : achats · espérance · résultat | valid. : achats · espérance · résultat | inédit : achats · résultat |", "|---|---|---|---|---|---|"]
cand = []
for titre, f in DIMS:
    niv = sorted({f(RAW[k]) for k in RAW if f(RAW[k]) is not None})
    for n in NOMS7:
        for v in niv:
            La = CELL[(titre, n, v, "apprentissage", DELAI)]
            if len(La) >= 20: cand.append((np.mean([x["pn"] for x in La]), titre, n, v))
for e, titre, n, v in sorted(cand, reverse=True)[:10]:
    La, Lv, Li = (CELL[(titre, n, v, p, DELAI)] for p in PERS)
    out.append(f"| {titre.split(' (')[0]} | {COURT[n]} | {v} | {len(La)} · {fe(e)} · {f0(sum(x['pn'] for x in La))} | "
               f"{len(Lv)} · {fe(np.mean([x['pn'] for x in Lv])) if Lv else '—'} · {f0(sum(x['pn'] for x in Lv))} | {len(Li)} · {f0(sum(x['pn'] for x in Li))} |")
out += ["", "Rappel : test inédit = 40 cycles ; les cases y contiennent 0 à 15 achats.", ""]
open("etude/bot5min/resultat_v3_exp005.md", "w").write("\n".join(out)); print("\n".join(out))
