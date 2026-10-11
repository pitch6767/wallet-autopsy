"""BOT95 — expériences A (double ordre passif), B (survie du capital), C (qualité des entrées). Demande de Pitch, 11.10.2026.
Hors ligne, aucune modification du bot. Mêmes cohortes A / B que le Hedge Lab. Seuils / régimes fixés sur l'apprentissage seulement.
Usage : python3 etude/bot5min/experiences_abc.py → etude/bot5min/resultat_experiences_ABC.md"""
exec(open("etude/bot5min/hedge_lab.py").read().split("# ================================================================ variables pour les modèles")[0])
CP = ("A", "B")
COHC = {"A": "cohorte A (désaccord 30 zone + modèle monte)", "B": "cohorte B (V2-F corrigé 0,015 %)"}
def jour(st): return time.strftime("%d.%m", time.gmtime(st + 7200))
JOURS = sorted({jour(st) for st in valides}, key=lambda x: (x[3:], x[:2]))
q_ = lambda x, v: f2(np.percentile(x, v)) if len(x) else "—"

# ================================================================ EXPÉRIENCE A — double ordre passif (bornes seulement)
def dual(st, t0, k, fen, regle, lat):
    d = arr(st); T = d["T"]; end = d["end"]
    j0 = int(ge(T, t0 + lat))
    if j0 >= len(T) or T[j0] >= end - 6: return None
    ub, db = d["UB"][j0], d["DB"][j0]
    if not (np.isfinite(ub) and np.isfinite(db)): return None
    Lu, Ld = round(ub - k / 100, 2), round(db - k / 100, 2)
    if Lu < 0.01 or Ld < 0.01 or Lu + Ld >= 1 - 1e-9: return None
    q = 50.0 / (Lu + Ld); t_exp = end - 5 if fen is None else min(end - 5, T[j0] + fen)
    m1 = int(le(T, t_exp))
    if m1 <= j0: return None
    def leg(A_, Z_, L):
        seg = A_[j0 + 1:m1 + 2]
        if regle == "optimiste":
            w = np.where(seg[:m1 - j0] <= L + 1e-9)[0]
            return (q, T[j0 + 1 + int(w[0])]) if len(w) else (0.0, None)
        c = seg <= L - 0.01 + 1e-9
        if len(c) < m1 - j0 + 1: c = np.append(c, False)
        cond = c[:m1 - j0] & c[1:m1 - j0 + 1]; got = 0.0; tf = None
        for idx in np.where(cond)[0]:
            m = j0 + 1 + int(idx); got += min(q - got, Z_[m])
            if tf is None: tf = T[m]
            if got >= q - 1e-9: break
        return (got if got >= 1 else 0.0), tf
    qu, tu = leg(d["UA"], d["UAZ"], Lu); qd, td = leg(d["DA"], d["DAZ"], Ld)
    wU = O[f"BTC:{st}"]["gagnant"] == "Up"
    pn = qu * ((1 if wU else 0) - Lu) + qd * ((0 if wU else 1) - Ld)
    pr = min(qu, qd)
    return dict(per=PER(st), both=qu >= 1 and qd >= 1, one=(qu >= 1) != (qd >= 1), none=qu < 1 and qd < 1, pn=pn, cost=Lu + Ld,
                pair_pn=pr * (1 - Lu - Ld), single_pn=(pn - pr * (1 - Lu - Ld)), dly=(abs(tu - td) if (tu is not None and td is not None) else None), cap=q * (Lu + Ld), st=st)
EXA = {}
MOMENTS = {"signaux A": [(st, COH["A"][st]["t"]) for st in COH["A"]], "signaux B": [(st, COH["B"][st]["t"]) for st in COH["B"]],
           "chaque cycle, ouverture + 10 s": [(st, st + 10) for st in valides]}
for nm, L_ in MOMENTS.items():
    for k in (0, 1, 2):
        for fen in (60, None):
            for regle, lat in (("optimiste", 0.0), ("pessimiste", 0.3)):
                EXA[(nm, k, fen, regle)] = [x for x in (dual(st, t0, k, fen, regle, lat) for st, t0 in L_) if x]
print("expérience A", f"{_time.time() - _T0:.0f} s", flush=True)

# ================================================================ EXPÉRIENCE B — survie du capital
MISES = (5, 10, 15, 25, 50)
PN_ = {}                      # (coh, mise, st) -> rec à mise pleine (prudent), pour mesurer ce que la ruine fait manquer
for coh in CP:
    for m in MISES:
        for st in COH[coh]:
            p = Pos(st, COH[coh][st], "prudent", budget=float(m))
            PN_[(coh, m, st)] = dict(pn=p.pnl(), stake=p.C0) if p.ok else None
def survie(coh, m, sts):
    bank = BANK0; tr = []; rmin = None; r0 = None; miss_j = 0; miss_jd = 0.0; refus = reduit = 0; cum = []
    for st in sts:
        full = PN_[(coh, m, st)]
        if full is None: continue
        b_ = min(float(m), bank)
        if b_ < 1:
            refus += 1
            if r0 is None: r0 = st
            if full["pn"] >= 4 * full["stake"]: miss_j += 1; miss_jd += full["pn"]
            continue
        if b_ < m - 1e-9:
            reduit += 1
            if rmin is None: rmin = st
        p = Pos(st, COH[coh][st], "prudent", budget=b_)
        if not p.ok: continue
        x = p.pnl(); bank += x; tr.append((st, x, p.C0)); cum.append(bank)
        if b_ < m - 1e-9 and full["pn"] >= 4 * full["stake"]: miss_j += 1; miss_jd += full["pn"] - x
    pn = np.array([x for _, x, _ in tr]); c_ = np.cumsum(pn) if len(pn) else np.zeros(1)
    dd = float(min(0.0, np.min(c_ - np.maximum.accumulate(np.concatenate([[0], c_]))[1:]))) if len(pn) else 0.0
    streaks = []; s_ = 0
    for v_ in pn:
        if v_ < 0: s_ += 1
        else:
            if s_: streaks.append(s_)
            s_ = 0
    if s_: streaks.append(s_)
    dj = collections.defaultdict(float)
    for st, x, _ in tr: dj[jour(st)] += x
    return dict(n=len(tr), pnl=float(pn.sum()), bank=bank, dd=dd, rmin=rmin, r0=r0, refus=refus, reduit=reduit, miss_j=miss_j, miss_jd=miss_jd,
                streaks=collections.Counter(streaks), maxs=max(streaks, default=0), dj=dj, minbank=min(cum, default=BANK0))
EXB = {}
for coh in CP:
    for m in MISES:
        for per in PERS: EXB[(coh, m, per)] = survie(coh, m, [st for st in sorted(COH[coh]) if PER(st) == per])
        EXB[(coh, m, "tout")] = survie(coh, m, sorted(COH[coh]))
# illustration seulement : bootstrap de blocs d'une heure sur l'apprentissage, horizon 24 h
def ruine_illus(coh, m, base_pers, B=2000, H=24):
    hv = collections.defaultdict(list)
    for st in sorted(COH[coh]):
        if PER(st) in base_pers and PN_[(coh, m, st)]: hv[st // 3600].append(PN_[(coh, m, st)]["pn"])
    for st in valides:
        if PER(st) in base_pers: hv.setdefault(st // 3600, [])
    blocs = list(hv.values()); rng = np.random.default_rng(7); n_r = 0
    for _ in range(B):
        bank = BANK0; ruin = False
        for b in rng.integers(0, len(blocs), H):
            for x in blocs[b]:
                f_ = min(1.0, bank / m) if bank >= 1 else 0.0
                bank += x * f_
                if bank < m: ruin = True
            if ruin: break
        n_r += ruin
    return n_r / B
ILL = {(coh, m): (ruine_illus(coh, m, ("apprentissage",)), ruine_illus(coh, m, PERS)) for coh in CP for m in MISES}
print("expérience B", f"{_time.time() - _T0:.0f} s", flush=True)

# ================================================================ EXPÉRIENCE C — qualité des entrées
def entree(coh, st):
    s = COH[coh][st]; d = arr(st); v = cote(d, s["up"], s["mod"]); T = d["T"]; i = s["i"]; w = gagne(st, s["up"])
    a = v["oa"][i]; z = v["oaz"][i]; q = min(50 / (a + FEE(a)), z)
    if q < 1: return None
    mid = (v["oa"][i] + v["ob"][i]) / 2; pa = v["pa"][i]
    qo = min(50 / (pa + FEE(pa)), v["paz"][i]) if np.isfinite(pa) else 0.0
    i5 = int(ge(T, T[i] - 5)); amin5 = float(np.nanmin(v["oa"][i5:i + 1]))
    # « presque vrai » plus tôt (rétrospectif) : premier instant du cycle, même côté, où l'écart du modèle ≥ seuil − 0,05
    thr = 0.30 if coh == "A" else 0.20
    e_ = v["fair"][:i] - v["oa"][:i]; w_ = np.where(e_ >= thr - 0.05)[0]
    if len(w_): ie = int(w_[0]); ae = v["oa"][ie]; qe = min(50 / (ae + FEE(ae)), v["oaz"][ie]); pe = qe * ((1 if w else 0) - ae - FEE(ae)) if qe >= 1 else 0.0; dte = T[i] - T[ie]
    else: pe = None; dte = None
    i30 = int(ge(T, T[i] - 30)); jmin = i30 + int(np.nanargmin(v["oa"][i30:i + 1])); am = v["oa"][jmin]; qm = min(50 / (am + FEE(am)), v["oaz"][jmin])
    pm30 = qm * ((1 if w else 0) - am - FEE(am)) if qm >= 1 else 0.0
    ex = {}
    for sc in SCN:
        p = Pos(st, s, sc); ex[sc] = (p.pnl(), True) if p.ok else (0.0, False)
    rg = RG[st]
    return dict(st=st, per=PER(st), w=w, a=a, q=q, fair=s["fair"], mid=mid, pn=q * ((1 if w else 0) - a - FEE(a)),
                skill=q * ((1 if w else 0) - mid), spread=-q * (a - mid), fee=-q * FEE(a), opp=(qo * ((0 if w else 1) - pa - FEE(pa)) if qo >= 1 else 0.0),
                prix5=-q * (a - amin5), early=pe, dte=dte, min30=pm30, ex=ex, vol=rg["vol"], tend=rg["tend"], bloc=rg["bloc"], tl=s.get("tl", st + 300 - s["t"]))
EXC = {coh: [x for x in (entree(coh, st) for st in sorted(COH[coh])) if x] for coh in CP}
print("expérience C", f"{_time.time() - _T0:.0f} s", flush=True)

# ================================================================ rédaction
out = ["# BOT95 — Expériences A (double ordre passif), B (survie du capital), C (qualité des entrées)", "",
       f"Étude hors ligne du {_time.strftime('%d.%m.%Y')} — aucun bot, aucun workflow modifié, rien publié. Cohortes A et B du Hedge Lab, mêmes entrées. "
       f"Apprentissage < {hs(CUT)} · validation → {hs(MATIN0)} · test inédit après (jusqu'au {hs(valides[-1] + 300)}).", ""]
VERD = len(out)
out += ["## 0. Diagnostic de faisabilité (avant tout résultat)", "",
        "| Expérience | Ce que les données actuelles permettent | Ce qui n'est qu'une borne | Ce qui exige l'enregistreur de Dublin |", "|---|---|---|---|",
        "| A — double ordre passif | savoir si le meilleur vendeur de chaque jeton a TOUCHÉ ou TRAVERSÉ nos prix (lignes 0,3 s), délai entre les deux, résultat officiel | tout remplissage : borne optimiste (rempli dès que le vendeur touche notre prix, quantité entière) et borne pessimiste (traversée d'1 c tenue ≥ 2 lignes, quantité affichée) | position dans la file d'attente, transactions individuelles à notre prix (prix, taille, côté, heure Polymarket), annulations / ajouts à notre niveau, carnet complet à 50 ms ; idéalement un vrai ordre de 1 part de chaque côté |",
        "| B — survie du capital | rejeu chronologique exact des signaux, quantité affichée au meilleur niveau, délai 0,3 s, frais, capital partagé | taille au-delà du meilleur niveau (une mise de 50 $ peut dépasser la taille affichée : comptée au meilleur niveau seulement) ; probabilité de ruine (quelques jours seulement : illustration) | profondeur réelle pour les grosses mises ; plus de jours pour une vraie probabilité de ruine |",
        "| C — qualité des entrées | décomposition exacte du P&L (côté, écart au milieu du carnet, frais), comparaison au côté opposé au même instant, régimes fixés sur l'apprentissage, effet du délai (0 / 0,3 / 0,6 s), calibration | « signal trop tard » et « moins cher dans les 30 s d'avant » sont RÉTROSPECTIFS (diagnostic, pas une stratégie) | heure Polymarket des carnets pour séparer retard réseau et retard du signal |", "",
        "**Aucun résultat fiable de teneur d'ordre (maker) ne peut être annoncé avec les données actuelles** : l'expérience A ne donne que des bornes.", ""]

# ---- A
out += ["## A. Double ordre passif Up + Down (bornes seulement)", "",
        "Au moment donné : ordre passif d'achat Up au meilleur acheteur Up − k c et ordre passif d'achat Down au meilleur acheteur Down − k c, même nombre de parts, 50 $ au total. "
        "Coût de la paire = (acheteur Up − k) + (acheteur Down − k) = 1 − écart vendeur-acheteur − 2k (carnets miroirs) : toujours < 1 ; frais teneur d'ordre supposés 0 (non vérifiés). "
        "Valable 60 s ou jusqu'à la fin − 5 s ; un ordre servi reste ; l'autre est annulé à l'échéance ; la jambe seule est gardée jusqu'au règlement. "
        "**Borne optimiste** : délai 0, rempli dès que le vendeur du jeton touche notre prix, quantité entière. **Borne pessimiste** : pose après 0,3 s, rempli seulement si le vendeur passe ≥ 1 c sous notre prix 2 lignes de suite, quantité affichée.", "",
        "| Moments | k | Durée | Borne | Période | Essais | Coût paire médian | Les 2 jambes | 1 seule | Aucune | Délai entre jambes (médiane, s) | P&L paires complètes | P&L jambes seules | P&L total (tous essais) | Capital immobilisé moyen |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
for (nm, k, fen, regle), L in EXA.items():
    for per in PERS:
        X = [x for x in L if x["per"] == per]
        if not X: continue
        dl = [x["dly"] for x in X if x["both"] and x["dly"] is not None]
        out.append(f"| {nm} | {k} c | {'60 s' if fen else 'fin − 5 s'} | {regle} | {per} | {len(X)} | {f2(np.median([x['cost'] for x in X]))} | {pc(np.mean([x['both'] for x in X]))} | "
                   f"{pc(np.mean([x['one'] for x in X]))} | {pc(np.mean([x['none'] for x in X]))} | {f2(np.median(dl)) if dl else '—'} | {f0(sum(x['pair_pn'] for x in X))} | "
                   f"{f0(sum(x['single_pn'] for x in X))} | **{f0(sum(x['pn'] for x in X))}** | {f0(np.mean([x['cap'] for x in X]))} |")
out += ["", "Lecture : l'écart entre la borne optimiste et la borne pessimiste EST l'incertitude ; la vraie valeur est quelque part entre les deux (ou en dessous si nous sommes servis surtout quand le prix part contre nous — sélection adverse, non mesurable ici).",
        "Attention : ce sont des bornes sur le REMPLISSAGE, pas sur le P&L — la borne « pessimiste » peut perdre moins que l'« optimiste », car une jambe seule est presque toujours celle dont le prix est parti contre nous "
        "(le vendeur ne descend jusqu'à notre prix que quand ce jeton perd de la valeur) : les jambes seules portent toute la perte, les paires complètes ne rapportent que l'écart (~1 c par paire).",
        "", "**Données live nécessaires pour un vrai résultat** : (1) chaque transaction des deux jetons (prix, taille, côté preneur, heure Polymarket) ; (2) les événements du carnet à notre niveau (ajout / retrait / taille avant-après) pour suivre la file devant nous ; "
        "(3) carnet complet des deux jetons à 50 ms ; (4) idéalement un ordre réel de 1 part de chaque côté et son sort (rempli, quand, combien) ; (5) frais teneur d'ordre réellement facturés.", ""]

# ---- B
out += ["## B. Survie du capital — 250 $ partagés, rejeu chronologique, prudent (0,3 s, meilleur niveau, frais)", "",
        "Entrée = min(mise, capital) ; capital < 1 $ → entrée refusée. « Sous la mise » = premier moment où le capital tombe sous la mise initiale (entrées réduites). Jackpots manqués = positions qui auraient rapporté ≥ 4 × la mise "
        "avec la mise pleine mais ont été réduites ou refusées faute de capital (en $ : gain manqué). Chaque période repart de 250 $ ; « tout » = un seul portefeuille du 07.10 au 11.10.", ""]
for coh in CP:
    out += [f"### {COHC[coh]}", "", "| Mise | Période | Positions jouées | P&L | Capital final | Capital le plus bas | Creux max | Sous la mise le | Ruine (capital < 1 $) le | Entrées réduites / refusées | Jackpots manqués (n · $) | Plus longue série perdante |",
            "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for m in MISES:
        for per in PERS + ("tout",):
            x = EXB[(coh, m, per)]
            out.append(f"| {m} $ | {per} | {x['n']} | {f0(x['pnl'])} | {f0(x['bank'])} | {f0(x['minbank'])} | {f0(x['dd'])} | {hs(x['rmin']) if x['rmin'] else '—'} | {hs(x['r0']) if x['r0'] else '—'} | "
                       f"{x['reduit']} / {x['refus']} | {x['miss_j']} · {f0(x['miss_jd'])} | {x['maxs']} |")
    out += ["", "Distribution des séries perdantes (portefeuille « tout », longueur : nombre de séries) :", ""]
    for m in MISES:
        c_ = EXB[(coh, m, "tout")]["streaks"]; out.append(f"- mise {m} $ : " + ", ".join(f"{L} → {n}" for L, n in sorted(c_.items())))
    out += ["", "P&L par jour (calendrier suisse, portefeuille « tout ») :", "", "| Mise | " + " | ".join(JOURS) + " |", "|---" * (len(JOURS) + 1) + "|"]
    for m in MISES:
        x = EXB[(coh, m, "tout")]; out.append(f"| {m} $ | " + " | ".join(f0(x["dj"].get(j_, 0.0)) for j_ in JOURS) + " |")
    out.append("")
out += ["**Probabilité de ruine — ILLUSTRATION SEULEMENT, pas une estimation fiable** (quelques jours de données, régimes changeants) : tirage de 24 blocs d'une heure ; part des tirages où le capital passe sous la mise en 24 h.", "",
        "| Cohorte | Mise | Blocs de l'apprentissage seulement | Blocs de toutes les périodes |", "|---|---|---|---|"]
for (coh, m), (a_, b_) in ILL.items(): out.append(f"| {coh} | {m} $ | {pc(a_)} | {pc(b_)} |")
out.append("")

# ---- C
def agg(X, key): return sum(x[key] for x in X)
out += ["## C. Qualité des entrées — d'où viennent les pertes ?", "",
        "Décomposition exacte, entrée au signal (délai 0, meilleur vendeur, quantité affichée, 50 $) : **P&L = choix du côté + écart payé + frais**, avec "
        "choix du côté = parts × (issue − milieu du carnet) [le milieu = probabilité implicite de Polymarket] ; écart payé = − parts × (prix payé − milieu) ; frais = − parts × frais. "
        "Puis : côté opposé acheté au même instant (même règle de taille) ; prix vs meilleur vendeur des 5 s précédentes (connu à la décision, mais la règle n'était pas vraie) ; "
        "« presque vrai plus tôt » et « moins cher dans les 30 s d'avant » = **RÉTROSPECTIF** ; exécution réelle (idéal 0 s / prudent 0,3 s / pessimiste 0,6 s).", "",
        "| Cohorte | Période | Positions | Gagnées | P&L au signal | (1) choix du côté vs milieu | (2) écart payé | frais | Côté opposé même instant | Prix vs min. 5 s avant | Rétro : presque vrai plus tôt (n · P&L) | Rétro : min. 30 s avant | (5) idéal · prudent · pessimiste (entrées) |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
for coh in CP:
    for per in PERS:
        X = [x for x in EXC[coh] if x["per"] == per]
        if not X: continue
        ea = [x for x in X if x["early"] is not None]
        exs = " · ".join(f"{f0(sum(x['ex'][sc][0] for x in X))} ({sum(x['ex'][sc][1] for x in X)})" for sc in SCN)
        out.append(f"| {coh} | {per} | {len(X)} | {pc(np.mean([x['w'] for x in X]))} | **{f0(agg(X, 'pn'))}** | {f0(agg(X, 'skill'))} | {f0(agg(X, 'spread'))} | {f0(agg(X, 'fee'))} | {f0(agg(X, 'opp'))} | "
                   f"{f0(agg(X, 'prix5'))} | {len(ea)} · {f0(sum(x['early'] for x in ea))} | {f0(agg(X, 'min30'))} | {exs} |")
out += ["", "### (4) Régimes (fixés à l'avance / sur l'apprentissage : volatilité perp < 2 $/s = calme ; tendance 15 min ≥ médiane de l'apprentissage = directionnel ; bloc de 6 h UTC)", "",
        "| Cohorte | Régime | app. : n · P&L | valid. : n · P&L | test : n · P&L |", "|---|---|---|---|---|"]
for coh in CP:
    for key, vals in (("vol", ("calme", "agité")), ("tend", ("directionnel", "oscillant")), ("bloc", ("00-06 UTC", "06-12 UTC", "12-18 UTC", "18-24 UTC"))):
        for v_ in vals:
            cel = []
            for per in PERS:
                X = [x for x in EXC[coh] if x["per"] == per and x[key] == v_]; cel.append(f"{len(X)} · {f0(agg(X, 'pn'))}")
            out.append(f"| {coh} | {v_} | " + " | ".join(cel) + " |")
out += ["", "### Calibration à l'entrée : le modèle a-t-il un avantage réel ?", "",
        "| Cohorte | Période | Tranche de proba du modèle (notre côté) | n | Proba modèle moyenne | Prix payé moyen | Milieu moyen (Polymarket) | Taux de gain réel | Gain réel − prix payé − frais (par part) |", "|---|---|---|---|---|---|---|---|---|"]
for coh in CP:
    for per in PERS:
        X = [x for x in EXC[coh] if x["per"] == per]
        for lo, hi in ((0, 0.45), (0.45, 0.55), (0.55, 0.65), (0.65, 1.01)):
            Y = [x for x in X if lo <= x["fair"] < hi]
            if not Y: continue
            wr = np.mean([x["w"] for x in Y]); ap = np.mean([x["a"] for x in Y])
            out.append(f"| {coh} | {per} | {f2(lo)}-{f2(min(hi, 1))} | {len(Y)} | {f2(np.mean([x['fair'] for x in Y]))} | {f2(ap)} | {f2(np.mean([x['mid'] for x in Y]))} | {pc(wr)} | {f3(wr - ap - np.mean([FEE(x['a']) for x in Y]))} |")
        if X:
            wr = np.mean([x["w"] for x in X]); ap = np.mean([x["a"] for x in X])
            out.append(f"| {coh} | {per} | **toutes** | {len(X)} | {f2(np.mean([x['fair'] for x in X]))} | {f2(ap)} | {f2(np.mean([x['mid'] for x in X]))} | **{pc(wr)}** | **{f3(wr - ap - np.mean([FEE(x['a']) for x in X]))}** |")
out.append("")
# facteur dominant
DOM = {}
for coh in CP:
    for per in PERS:
        X = [x for x in EXC[coh] if x["per"] == per]
        if not X: continue
        lat = sum(x["ex"]["prudent"][0] for x in X) - agg(X, "pn")
        f_ = {"choix du côté": agg(X, "skill"), "écart payé": agg(X, "spread"), "frais": agg(X, "fee"), "délai 0,3 s (prudent − signal)": lat}
        DOM[(coh, per)] = (min(f_, key=f_.get), f_)
out += ["### Quel facteur domine ?", "", "| Cohorte | Période | Choix du côté | Écart payé | Frais | Délai 0,3 s | Plus grand poste négatif |", "|---|---|---|---|---|---|---|"]
for (coh, per), (k_, f_) in DOM.items():
    out.append(f"| {coh} | {per} | {f0(f_['choix du côté'])} | {f0(f_['écart payé'])} | {f0(f_['frais'])} | {f0(f_['délai 0,3 s (prudent − signal)'])} | **{k_}** |")
out += ["", "Le « choix du côté » mesure l'avantage réel du signal par rapport au prix du marché (milieu) : positif = le modèle bat Polymarket ; il est très bruité (issue binaire, peu de positions). "
        "Le délai 0,3 s mélange entrées perdues (le prix est parti — souvent les meilleures) et entrées faites au même prix.", "", f"Durée de calcul : {_time.time() - _T0:.0f} s."]

# ---- verdict
V = ["## Réponse courte (en tête)", ""]
for nm in ("signaux A", "signaux B", "chaque cycle, ouverture + 10 s"):
    o_ = EXA[(nm, 0, None, "optimiste")]; p_ = EXA[(nm, 0, None, "pessimiste")]
    V.append(f"- **A double passif ({nm}, k = 0, jusqu'à la fin)** : les deux jambes servies dans {pc(np.mean([x['both'] for x in o_]))} (borne optimiste) à {pc(np.mean([x['both'] for x in p_]))} (pessimiste) des {len(o_)} essais ; "
             f"P&L total {f0(sum(x['pn'] for x in o_))} (optimiste) / {f0(sum(x['pn'] for x in p_))} (pessimiste), dont jambes seules {f0(sum(x['single_pn'] for x in o_))} / {f0(sum(x['single_pn'] for x in p_))}. "
             "Bornes seulement : aucun résultat maker fiable.")
for coh in CP:
    s_ = " · ".join(f"{m} $ : {f0(EXB[(coh, m, 'tout')]['pnl'])}, creux {f0(EXB[(coh, m, 'tout')]['dd'])}, " + (f"ruine le {hs(EXB[(coh, m, 'tout')]['r0'])}" if EXB[(coh, m, 'tout')]['r0'] else (f"sous la mise le {hs(EXB[(coh, m, 'tout')]['rmin'])}" if EXB[(coh, m, 'tout')]['rmin'] else "jamais sous la mise")) for m in MISES)
    V.append(f"- **B survie ({coh}, 250 $, 07.10 → 11.10, prudent)** : {s_}.")
for coh in CP:
    cel = []
    for per in PERS:
        X = [x for x in EXC[coh] if x["per"] == per]
        if X: cel.append(f"{per} : côté {f0(agg(X, 'skill'))}, écart {f0(agg(X, 'spread'))}, frais {f0(agg(X, 'fee'))}, délai {f0(DOM[(coh, per)][1]['délai 0,3 s (prudent − signal)'])} → {DOM[(coh, per)][0]}")
    V.append(f"- **C qualité ({coh})** : " + " ; ".join(cel) + ".")
V.append("- Les estimations de ruine sont des **illustrations** (bootstrap de quelques jours), pas des probabilités fiables.")
V.append("")
out[VERD:VERD] = V
open("etude/bot5min/resultat_experiences_ABC.md", "w").write("\n".join(out))
print("\n".join(V)); print(f"fini en {_time.time() - _T0:.0f} s")
