"""Fiabilité de l'avantage, urgence d'exécution, faux cadeaux, anatomie des désaccords, TWAP contrefactuel (demande ChatGPT 10.10.2026 11:09).
Signal = modèle E (tables du bot), premier du cycle, avantage ≥ 0,20, 90-20 s, quantité affichée, frais compris. Écart exchange → Chainlink recalculé
à chaque seconde. Apprentissage / validation / nuit comme robustesse_E.py ; seuils et corrections appris sur l'apprentissage seulement. Diagnostic."""
import sys
sys.path.insert(0, "etude/bot5min")
exec(open("etude/bot5min/pression_reglement.py").read().split("GH = (")[0])
for nom, i in (("okx", 12), ("cb", 13), ("bn", 14)): SER[nom] = ([r[0] for r in rows if r[i]], [r[i] for r in rows if r[i]])
BX = {}
def baseX(nom, s):
    k = (nom, s)
    if k not in BX:
        d = [sec(nom, x) - sec("cl", x) for x in range(s - 120, s) if sec(nom, x) and sec("cl", x)]
        BX[k] = float(np.median(d)) if len(d) > 30 else None
    return BX[k]
def levX(nom, t):
    p = der(nom, t); b = baseX(nom, int(t)) if nom != "perp" else base(int(t))
    return p - b if p is not None and b is not None else None
def mesure(st, t, R, T_):
    c = coeur(st, t)
    if not c: return None
    p = prob(c)
    c2 = coeur(st, t - 2); S2 = c2["S"] if c2 else c["S"]
    pnc = prob(c, S2)                                         # sans le mouvement des 2 dernières secondes (monde « sans choc »)
    cl = der("cl", t); pcl = prob(c, cl) if cl else p          # dernier Chainlink prolongé
    L4 = [x for x in (levX(n, t) for n in ("perp", "okx", "bn", "cb")) if x is not None]
    pco = prob(c, float(np.median(L4))) if len(L4) >= 2 else p  # consensus des 4 exchanges
    saut = abs(c["S"] - S2) >= max(3, 4 * c["sg"] * math.sqrt(2))
    return dict(p=p, pnc=pnc, pcl=pcl, pco=pco, S=c["S"], saut=saut, rg=c["rg"], cl=cl)
def row_at(R, T_, t):
    j = bisect.bisect_left(T_, t); return R[j] if j < len(R) else None
SIGS = {}
for st in valides:
    R = C[st]; T_ = [r[0] for r in R]; y = O[f"BTC:{st}"]["gagnant"] == "Up"; end = st + 300
    hist = []                                                   # (t, p, ua, da) une fois par ligne pour âge / origine
    for i, r in enumerate(R):
        t = r[0]; tl = end - t
        if tl > 95 or tl < 20: continue
        m = mesure(st, t, R, T_) if tl <= 90 else None
        c0 = coeur(st, t); p0 = prob(c0) if c0 else None
        hist.append((t, p0, r[4], r[6], der("cl", t)))
        if not m or st in SIGS: continue
        for up in (True, False):
            a = r[4] if up else r[6]; z = (r[8] if up else r[10]) or 0
            if a is None or not (0.02 <= a <= 0.98) or z <= 0: continue
            pr = m["p"] if up else 1 - m["p"]
            if pr - a < 0.20: continue
            sd_ = lambda x: x if up else 1 - x
            # passé (1 s et 3 s avant), âge du désaccord, nombre de valeurs Chainlink nouvelles depuis la naissance
            def h_at(dt):
                c_ = [h for h in hist if h[0] <= t - dt]; return c_[-1] if c_ else None
            h1, h3 = h_at(1), h_at(3)
            dp1 = (pr - sd_(h1[1])) if h1 and h1[1] is not None else None; da1 = (a - (h1[2] if up else h1[3])) if h1 and (h1[2] if up else h1[3]) is not None else None
            dp3 = (pr - sd_(h3[1])) if h3 and h3[1] is not None else None; da3 = (a - (h3[2] if up else h3[3])) if h3 and (h3[2] if up else h3[3]) is not None else None
            naiss = None
            for h in reversed(hist[:-1]):
                ah = h[2] if up else h[3]
                if h[1] is None or ah is None: continue
                if sd_(h[1]) - ah < 0.05: naiss = h[0]; break
            age = t - naiss if naiss else 99
            ncl = len({h[4] for h in hist if naiss and h[0] > naiss and h[4] is not None}) - 1 if naiss else 0
            cl1 = h1[4] if h1 else None; newcl = cl1 is not None and m["cl"] is not None and m["cl"] != cl1
            # retrait de liquidité 0,5 s
            r05 = row_at(R, T_, t - 0.5); z05 = (r05[8] if up else r05[10]) if r05 else None; a05 = (r05[4] if up else r05[6]) if r05 else None
            retrait = (1 - z / z05) if (z05 and a05 == a and z05 > 0) else 0.0
            gm = y if up else not y; q = min(50 / a, z)
            # exécution différée (urgence)
            def plus_tard(d):
                rr = row_at(R, T_, t + d)
                if not rr: return None
                aa = rr[4] if up else rr[6]; zz = (rr[8] if up else rr[10]) or 0
                if aa is None or zz <= 0 or not (0.02 <= aa <= 0.98): return None
                mm = mesure(st, rr[0], R, T_)
                if not mm or (sd_(mm["p"]) - aa) < 0.20: return None
                qq = min(50 / aa, zz); return (qq * ((1 if gm else 0) - aa - FEE(aa)), qq * aa, gm, aa)
            SIGS[st] = dict(st=st, up=up, gm=gm, a=a, pr=pr, edge=pr - a, it=(q * ((1 if gm else 0) - a - FEE(a)), q * a, gm), tl=tl,
                            dp1=dp1, da1=da1, dp3=dp3, da3=da3, age=age, ncl=ncl, newcl=newcl, retrait=retrait, saut=m["saut"], rg=m["rg"],
                            pnc=sd_(m["pnc"]), pcl=sd_(m["pcl"]), pco=sd_(m["pco"]), dS1=None,
                            tard={d: plus_tard(d) for d in (0.25, 0.5, 1.0)})
            break
def stats(L_):
    if not L_: return "0 | — | — | — | —"
    pn = [l[0] for l in L_]; cum = pk = cr = 0.0
    for v in pn: cum += v; pk = max(pk, cum); cr = min(cr, cum - pk)
    return f"{len(L_)} | {100 * sum(l[2] for l in L_) / len(L_):.0f} % | **{f0(sum(pn))}** | {f0(cr)} | {sum(1 for l in L_ if l[0] >= 4 * l[1])}"
HH = "| Groupe | Apprentissage (achats / gagnés / résultat / creux / jackpots) | Validation + nuit |\n|---|---|---|"
def g2(nom, f):
    a = [v["it"] for st, v in SIGS.items() if per(st) == "apprentissage" and f(v)]; b = [v["it"] for st, v in SIGS.items() if per(st) != "apprentissage" and f(v)]
    return f"| {nom} | {stats(a).replace(' | ', ' / ')} | {stats(b).replace(' | ', ' / ')} |"
out = [f"# Fiabilité de l'avantage, urgence, faux cadeaux, origine des désaccords, TWAP contrefactuel — BTC, {len(valides)} cycles", "",
       f"{len(SIGS)} premiers signaux E (avantage ≥ 0,20). Apprentissage avant le {hs(CUT)} ; validation + nuit après. Seuils fixés sur l'apprentissage.", "", "## Référence", "", HH, g2("tous les signaux E", lambda v: True)]
# ---------- A. retrait conditionne a l'avantage (4) et urgence (5)
out += ["", "## Partie A — Retrait de liquidité et urgence d'exécution (idées 2-7)", "", "### Idée 4 : au moment du signal, le prix vendeur monte-t-il d'au moins 2 c dans la seconde ?", "",
        "| Groupe | Signaux | Prix vendeur +2 c en 1 s | Variation moyenne du prix en 1 s |", "|---|---|---|---|"]
def mont(v):
    rr = v["tard"].get(1.0); return None
U = collections.defaultdict(list)
for st, v in SIGS.items():
    R = C[st]; T_ = [r[0] for r in R]; rr = row_at(R, T_, (st + 300 - v["tl"]) + 1)
    if not rr: continue
    a1 = rr[4] if v["up"] else rr[6]
    if a1 is None: continue
    d = a1 - v["a"]
    for k in (("retrait fort (≥ 50 %)" if v["retrait"] >= 0.5 else "pas de retrait fort"),
              ("avantage 20-30 pts" if v["edge"] < 0.30 else "avantage ≥ 30 pts") + (" + retrait fort" if v["retrait"] >= 0.5 else ""),
              ("après saut" if v["saut"] else "sans saut") + (" + retrait fort" if v["retrait"] >= 0.5 else ""),
              "régime " + v["rg"] + (" + retrait fort" if v["retrait"] >= 0.5 else "")):
        U[k].append(d)
for k in sorted(U):
    a = np.array(U[k]); out.append(f"| {k} | {len(a)} | {100 * np.mean(a >= 0.02):.0f} % | {100 * a.mean():+.1f} c |")
out += ["", "### Idée 5 : acheter tout de suite seulement si le carnet se vide, sinon attendre un peu (délais fixés d'avance)", "", HH]
out.append(g2("A — acheter tout de suite (référence)", lambda v: True))
for d in (0.25, 0.5, 1.0):
    def pol(v, d=d):
        return v["it"] if v["retrait"] >= 0.5 else v["tard"][d]
    a = [pol(v) for st, v in SIGS.items() if per(st) == "apprentissage" and pol(v)]; b = [pol(v) for st, v in SIGS.items() if per(st) != "apprentissage" and pol(v)]
    out.append(f"| B — retrait fort : tout de suite ; sinon attendre {d} s (acheter si l'avantage est encore ≥ 0,20) | {stats(a).replace(' | ', ' / ')} | {stats(b).replace(' | ', ' / ')} |")
# ---------- 3. avantage fiable : correction apprise
TRS = [v for st, v in SIGS.items() if per(st) == "apprentissage"]
def cle(v): return (v["rg"], v["saut"], v["age"] < 3)
corr = {}
for k in {cle(v) for v in TRS}:
    S_ = [v for v in TRS if cle(v) == k]
    if len(S_) >= 8: corr[k] = float(np.mean([v["pr"] - (1 if v["gm"] else 0) for v in S_]))
cg = float(np.mean([v["pr"] - (1 if v["gm"] else 0) for v in TRS]))
for v in SIGS.values(): v["fiable"] = v["edge"] - max(0.0, corr.get(cle(v), cg))
out += ["", "### Idée 3 : avantage « fiable » = avantage − surestimation apprise (par régime, saut récent, âge du désaccord)", "",
        "Surestimations apprises (probabilité annoncée − taux de gain réel, signaux d'apprentissage) : " + ", ".join(f"{k[0]}, {'saut' if k[1] else 'sans saut'}, {'né < 3 s' if k[2] else 'mûr'} : {v:+.2f}" for k, v in corr.items()) + f" ; global {cg:+.2f}.", "", HH,
        g2("avantage fiable ≥ 0,20", lambda v: v["fiable"] >= 0.20), g2("avantage fiable ≥ 0,10", lambda v: v["fiable"] >= 0.10), g2("avantage fiable < 0,10", lambda v: v["fiable"] < 0.10)]
out += ["", "### Idée 6 : carte avantage × fiabilité × retrait (validation + nuit)", "", "| Avantage | Fiabilité | Retrait fort | Achats / gagnés / résultat / creux / jackpots |", "|---|---|---|---|"]
for e0, e1, en in ((0.2, 0.3, "20-30 pts"), (0.3, 9, "≥ 30 pts")):
    for fi in (True, False):
        for rt in (True, False):
            Ls = [v["it"] for st, v in SIGS.items() if per(st) != "apprentissage" and e0 <= v["edge"] < e1 and (v["fiable"] >= 0.10) == fi and (v["retrait"] >= 0.5) == rt]
            if Ls: out.append(f"| {en} | {'fiable' if fi else 'peu fiable'} | {'oui' if rt else 'non'} | {stats(Ls).replace(' | ', ' / ')} |")
# ---------- B. faux cadeaux
GX = [v for st, v in SIGS.items() if per(st) != "apprentissage" and v["edge"] >= 0.30]
out += ["", f"## Partie B — Les faux cadeaux : les {len(GX)} signaux à 30 points d'avantage ou plus, hors apprentissage (idées 8-9)", "",
        "| Heure | Côté | Prix | Proba E | Avantage | Restant | Régime | Saut récent | Âge du désaccord | Prix vendeur 3 s avant | Proba sans le dernier choc | Gagnant | Net |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
for v in sorted(GX, key=lambda v: v["st"]):
    out.append(f"| {hs(v['st'] + 300 - v['tl'])} | {'Up' if v['up'] else 'Down'} | {v['a']:.2f} | {v['pr']:.2f} | {v['edge']:.2f} | {v['tl']:.0f} s | {v['rg']} | {'oui' if v['saut'] else 'non'} | {v['age']:.1f} s | {(v['a'] - v['da3']) if v['da3'] is not None else float('nan'):.2f} | {v['pnc']:.2f} | {'oui' if v['gm'] else 'non'} | {f0(v['it'][0])} |")
if GX:
    out += ["", f"- Après un saut des exchanges : {sum(v['saut'] for v in GX)} sur {len(GX)} ; régime calme : {sum(v['rg'] == 'calme' for v in GX)} ; désaccord né il y a moins de 3 s : {sum(v['age'] < 3 for v in GX)} ; "
            f"prix vendeur en chute d'au moins 5 c en 3 s : {sum(1 for v in GX if v['da3'] is not None and v['da3'] <= -0.05)} ; gagnants : {sum(v['gm'] for v in GX)} (dont jackpots : {sum(1 for v in GX if v['it'][0] >= 4 * v['it'][1])}).",
            f"- Les 3 plus grosses pertes font {f0(sum(sorted(v['it'][0] for v in GX)[:3]))} sur un total de {f0(sum(v['it'][0] for v in GX))}."]
# ---------- C. anatomie
def origine(v):
    if v["dp1"] is None or v["da1"] is None: return "inconnue"
    dp, da = v["dp1"], v["da1"]
    if dp >= 0.03 and abs(da) < 0.02: return "1. E monte, prix stable"
    if abs(dp) < 0.03 and da <= -0.02: return "2. E stable, prix baisse"
    if dp >= 0.03 and da <= -0.02: return "3. E monte et prix baisse"
    if dp >= 0.03 and da >= 0.02: return "4. E monte, prix monte moins vite"
    if dp <= -0.03 and da <= -0.02: return "5. E baisse, prix baisse plus vite"
    return "6. petits mouvements (< 3 pts / 2 c)"
out += ["", "### Idées 8-9, 21 : le prix Polymarket s'est-il effondré juste avant le signal ? (prix vendeur de notre côté, 3 s avant → au signal)", "", HH,
        g2("avantage 20-30 pts", lambda v: v["edge"] < 0.30), g2("avantage ≥ 30 pts", lambda v: v["edge"] >= 0.30),
        g2("prix vendeur effondré d'au moins 30 c en 3 s", lambda v: v["da3"] is not None and v["da3"] <= -0.30),
        g2("prix vendeur en baisse de 10 à 30 c en 3 s", lambda v: v["da3"] is not None and -0.30 < v["da3"] <= -0.10),
        g2("prix vendeur stable ou en hausse (moins de 10 c de baisse)", lambda v: v["da3"] is None or v["da3"] > -0.10),
        g2("effondré ≥ 30 c ET proba E quasi inchangée (moins de 5 pts en 3 s)", lambda v: v["da3"] is not None and v["da3"] <= -0.30 and v["dp3"] is not None and abs(v["dp3"]) < 0.05)]
out += ["", "## Partie C — D'où vient l'avantage ? (idées 10-14, sur la seconde avant le signal)", "", HH]
for k in sorted({origine(v) for v in SIGS.values()}): out.append(g2(k, lambda v, k=k: origine(v) == k))
out += ["", "Idée 12 — signaux de 30 à 50 points d'avantage seulement :", "", HH]
for k in sorted({origine(v) for v in SIGS.values()}): out.append(g2(k, lambda v, k=k: origine(v) == k and 0.30 <= v["edge"] < 0.50))
def info(v):
    if v["newcl"]: return "A — nouvelle valeur Chainlink dans la dernière seconde"
    if v["saut"]: return "B — mouvement des exchanges sans nouveau Chainlink"
    if v["da1"] is not None and v["da1"] <= -0.02: return "C — baisse du prix Polymarket"
    return "D — autre / mixte"
out += ["", "### Idée 14 : origine de l'information", "", HH] + [g2(k, lambda v, k=k: info(v) == k) for k in sorted({info(v) for v in SIGS.values()})]
# ---------- D. maturite
out += ["", "## Partie D — Maturité et origine (idées 16-23)", "", HH]
for o_ in ("A — nouvelle valeur Chainlink dans la dernière seconde", "B — mouvement des exchanges sans nouveau Chainlink", "C — baisse du prix Polymarket", "D — autre / mixte"):
    for mat in (True, False):
        out.append(g2(f"{o_} — {'mûr (désaccord né il y a ≥ 3 s)' if mat else 'récent (< 3 s)'}", lambda v, o_=o_, mat=mat: info(v) == o_ and (v["age"] >= 3) == mat))
out += ["", "Idée 18 — nombre de nouvelles valeurs Chainlink depuis la naissance du désaccord :", "", HH]
for a_, b_, n_ in ((0, 1, "0"), (1, 2, "1"), (2, 99, "2 ou plus")): out.append(g2(n_, lambda v, a_=a_, b_=b_: a_ <= v["ncl"] < b_))
# ---------- E. contrefactuel
SDR = lambda v: abs(v["pr"] - v["pnc"]) / (abs(v["edge"]) + 0.01)
mS = float(np.median([SDR(v) for v in TRS]))
out += ["", "## Partie E — TWAP contrefactuel (idées 24-27)", "",
        f"SDR = |proba E − proba E sans le mouvement des 2 dernières secondes| / avantage. Médiane d'apprentissage : {mS:.2f}.", "", HH,
        g2(f"SDR faible (≤ {mS:.2f}) : le signal ne dépend pas du dernier choc", lambda v: SDR(v) <= mS), g2("SDR fort : le signal dépend du dernier choc", lambda v: SDR(v) > mS),
        g2("SDR > 1 : sans le dernier choc, il n'y aurait plus d'avantage", lambda v: SDR(v) > 1)]
def mondes(v):
    return sum(1 for p in (v["pr"], v["pcl"], v["pco"]) if p - v["a"] >= 0.20)
out += ["", "Idée 27 — consensus de trois mondes (E actuel ; dernier Chainlink prolongé ; consensus des 4 exchanges), avantage ≥ 0,20 :", "", HH]
for n_ in (1, 2, 3): out.append(g2(f"{n_} monde(s) sur 3 voient l'avantage", lambda v, n_=n_: mondes(v) == n_))
open("etude/bot5min/resultat_contrefactuel.md", "w").write("\n".join(out)); print("\n".join(out))
