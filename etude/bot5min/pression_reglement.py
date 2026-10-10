"""Settlement pressure, grecques du règlement, réévaluations Polymarket, liquidité et balayage du carnet (demande ChatGPT 10.10.2026 10:46).
Partie A : carnets enregistrés 4×/s (1 niveau), modèle E (tables du bot), écart Bybit→Chainlink recalculé à chaque seconde.
Partie B : carnets 8 niveaux enregistrés aux signaux TWAP fin depuis le 10.10 01:22 (bot95/twap_carnets.json).
Apprentissage / validation / nuit comme robustesse_E.py. Diagnostic seulement : aucune stratégie modifiée."""
import sys
sys.path.insert(0, "etude/bot5min")
exec(open("etude/bot5min/robustesse_E.py").read().split("def rejouer(delta):")[0])
SIG1 = 1.83          # erreur type de la prévision du prochain Chainlink à 1 s (mesurée ce matin, « Chainlink + 0,24 × écart »)
def coeur(st, ti):
    end = st + 300; deb = end - 60; s = int(ti)
    K = [sec("cl", x) for x in range(st - 60, st)]; K = [x for x in K if x is not None]
    if len(K) < 40: return None
    sg = vol(s); b = base(s); p = der("perp", ti)
    if not sg or b is None or p is None: return None
    con = [sec("cl", j) for j in range(deb, s)] if s >= deb else []; con = [x for x in con if x is not None]
    return dict(K=sum(K) / len(K), sg=sg, S=p - b, s=s, deb=deb, end=end, ks=sum(con), nk=len(con), rg="calme" if sg < 2 else "agité")
def prob(c, S=None, extra=0):
    """probabilité E (tables du bot) ; extra = secondes qui passent, fixées au prix prévu S (dans la fenêtre)"""
    S = c["S"] if S is None else S; s = c["s"] + extra
    if s >= c["deb"]:
        add = extra if c["s"] >= c["deb"] else max(0, s - c["deb"])
        nk = c["nk"] + add; ks = c["ks"] + add * S; rem = max(1, 60 - nk)
        E = (ks + rem * S) / 60; v = c["sg"] ** 2 * rem ** 3 / 3 / 3600; bk = "45-60 s restantes" if rem > 45 else "30-45 s" if rem > 30 else "15-30 s" if rem > 15 else "< 15 s"
    else: E = S; v = c["sg"] ** 2 * ((c["deb"] - s) + 20); bk = "avant la fenêtre"
    sd = math.sqrt(v + 0.25); z = (E - c["K"]) / sd
    pe = survie(f"{bk}|{c['rg']}" if f"{bk}|{c['rg']}" in QT else f"{bk}|*", -z)
    return pe if pe is not None else phi(z)
GH = ((-2, 0.054), (-1, 0.242), (0, 0.4), (1, 0.242), (2, 0.054))
L = []          # une ligne par seconde, 90-20 s
for st in valides:
    R = C[st]; T_ = [r[0] for r in R]; y = O[f"BTC:{st}"]["gagnant"] == "Up"; end = st + 300; prev = None
    for sec_ in range(end - 90, end - 19):
        j = bisect.bisect_right(T_, sec_ + 0.999) - 1
        if j < 0 or R[j][0] < sec_: continue
        r = R[j]; t = r[0]; c = coeur(st, t)
        if not c: continue
        p = prob(c); d = (prob(c, c["S"] + 0.5) - prob(c, c["S"] - 0.5)); g = prob(c, c["S"] + 1) - 2 * p + prob(c, c["S"] - 1)
        th = prob(c, extra=1) - p
        ig = sum(w * abs(prob(c, c["S"] + k * SIG1) - p) for k, w in GH) / 0.992
        bar = (60 * c["K"] - c["ks"]) / max(1, 60 - c["nk"]) if c["s"] >= c["deb"] else None
        def apres(dt, k_):
            jj = bisect.bisect_left(T_, t + dt)
            return R[jj][k_] if jj < len(R) else None
        mid = (r[3] + r[4]) / 2 if r[3] is not None and r[4] is not None else None
        m2 = apres(2, 3), apres(2, 4); mid2 = (m2[0] + m2[1]) / 2 if None not in m2 else None
        m5 = apres(5, 3), apres(5, 4); mid5 = (m5[0] + m5[1]) / 2 if None not in m5 else None
        j05 = bisect.bisect_left(T_, t - 0.5)
        x = dict(st=st, t=t, tl=end - t, y=y, p=p, d=d, g=g, th=th, ig=ig, bar=bar, S=c["S"], rg=c["rg"], sg=c["sg"],
                 ua=r[4], da=r[6], ub=r[3], db=r[5], uz=r[8] or 0, dz=r[10] or 0, mid=mid, mid2=mid2, mid5=mid5,
                 ua1=apres(1, 4), da1=apres(1, 6), uz05=R[j05][8] if j05 < len(R) else None, dz05=R[j05][10] if j05 < len(R) else None,
                 ua05=R[j05][4] if j05 < len(R) else None, da05=R[j05][6] if j05 < len(R) else None)
        if prev and prev["st"] == st and t - prev["t"] < 1.6:
            x["dp"] = p - prev["p"]; x["dS"] = c["S"] - prev["S"]; x["dmid"] = (mid - prev["mid"]) if mid is not None and prev["mid"] is not None else None
            x["thp"] = prev["th"]; x["dbar"] = (bar - prev["bar"]) if bar is not None and prev["bar"] is not None else None
            x["acc"] = (x["dbar"] - prev["dbar"]) if x["dbar"] is not None and prev.get("dbar") is not None else None
        L.append(x); prev = x
out = [f"# Pression de règlement, grecques, réévaluations et carnet — BTC, {len(valides)} cycles ({hs(valides[0])} → {hs(valides[-1] + 300)})", "",
       f"{len(L)} mesures (une par seconde, 90-20 s). Probabilité = modèle E (tables du bot). Apprentissage avant le {hs(CUT)}, validation jusqu'au {hs(NUIT0)}, nuit du 10.10 à part.", ""]
# ---------- signaux E (premier par cycle) et caractéristiques au signal
SG = {}
for x in L:
    if x["st"] in SG: continue
    for up in (True, False):
        a = x["ua"] if up else x["da"]; z = x["uz"] if up else x["dz"]
        if a is None or not (0.02 <= a <= 0.98) or z <= 0: continue
        pr = x["p"] if up else 1 - x["p"]
        if pr - a >= 0.20:
            gm = x["y"] if up else not x["y"]; q = min(50 / a, z); sg_ = 1 if up else -1
            SG[x["st"]] = dict(x=x, up=up, it=(q * ((1 if gm else 0) - a - FEE(a)), q * a, gm)); break
def stats(Lst):
    if not Lst: return "0 | — | — | —"
    pn = [l[0] for l in Lst]; return f"{len(Lst)} | {100 * sum(l[2] for l in Lst) / len(Lst):.0f} % | **{f0(sum(pn))}** | {sum(1 for l in Lst if l[0] >= 4 * l[1])}"
TRS = [v for st, v in SG.items() if per(st) == "apprentissage"]
med = lambda k: float(np.median([abs(v["x"].get(k) or 0) for v in TRS]))
seuils = {k: med(k) for k in ("d", "g", "ig", "th")}
out += ["## Partie 1-4. Les grecques du règlement apportent-elles quelque chose au signal E ? (premier signal E du cycle, seuils = médianes de l'apprentissage)", "",
        "| Groupe au moment du signal | Apprentissage (achats / gagnés / résultat / jackpots) | Validation | Nuit 10.10 |", "|---|---|---|---|"]
def grp(nom, f):
    cel = []
    for g in ("apprentissage", "validation", "nuit 10.10"):
        cel.append(stats([v["it"] for st, v in SG.items() if per(st) == g and f(v)]).replace(" | ", " / "))
    out.append(f"| {nom} | " + " | ".join(cel) + " |")
grp("tous les signaux E", lambda v: True)
grp(f"delta fort (≥ {seuils['d']:.3f} par $)", lambda v: abs(v["x"]["d"]) >= seuils["d"])
grp("delta faible", lambda v: abs(v["x"]["d"]) < seuils["d"])
grp(f"réévaluation attendue forte (gamma d'information ≥ {seuils['ig']:.3f})", lambda v: v["x"]["ig"] >= seuils["ig"])
grp("réévaluation attendue faible", lambda v: v["x"]["ig"] < seuils["ig"])
grp("convexité forte (|gamma| ≥ médiane)", lambda v: abs(v["x"]["g"]) >= seuils["g"])
grp("le temps qui passe joue pour nous (thêta > 0)", lambda v: (v["x"]["th"] > 0) == v["up"])
grp("le temps qui passe joue contre nous", lambda v: (v["x"]["th"] > 0) != v["up"])
grp("barrière qui s'éloigne en notre faveur (dernière seconde)", lambda v: v["x"].get("dbar") is not None and ((v["x"]["dbar"] < 0) == v["up"]))
grp("barrière qui se rapproche contre nous", lambda v: v["x"].get("dbar") is not None and ((v["x"]["dbar"] < 0) != v["up"]))
grp("idée 3 : E monte, barrière favorable, carnet immobile (< 2 c)", lambda v: v["x"].get("dp") is not None and (v["x"]["dp"] > 0) == v["up"] and v["x"].get("dbar") is not None and ((v["x"]["dbar"] < 0) == v["up"]) and v["x"].get("dmid") is not None and abs(v["x"]["dmid"]) < 0.02)
grp("idée 19 : révision E ≥ 10 pts alors que les exchanges ont bougé < 1 $ (fixation pure)", lambda v: v["x"].get("dp") is not None and abs(v["x"]["dp"]) >= 0.10 and abs(v["x"].get("dS") or 9) < 1)
out += ["", "Carte de l'idée 13 (avantage E × réévaluation attendue), toutes périodes hors apprentissage :", "", "| Avantage au signal | Réévaluation attendue | Achats / gagnés / résultat / jackpots |", "|---|---|---|"]
for ea, eb, en in ((0.20, 0.30, "0,20-0,30"), (0.30, 9, "≥ 0,30")):
    for hi in (True, False):
        Ls = [v["it"] for st, v in SG.items() if per(st) != "apprentissage" and ea <= ((v["x"]["p"] if v["up"] else 1 - v["x"]["p"]) - (v["x"]["ua"] if v["up"] else v["x"]["da"])) < eb and (v["x"]["ig"] >= seuils["ig"]) == hi]
        out.append(f"| {en} | {'forte' if hi else 'faible'} | {stats(Ls).replace(' | ', ' / ')} |")
# ---------- attribution des variations de probabilité (14, 16, 20)
A = [x for x in L if x.get("dp") is not None]
tot = np.sum(np.abs([x["dp"] for x in A])); temps = np.sum(np.abs([x["thp"] for x in A]))
out += ["", "## Idées 14, 16, 20. D'où viennent les variations de probabilité d'une seconde à l'autre ?", "",
        f"Sur {len(A)} variations d'une seconde : part « temps qui passe + fixation d'une seconde au prix prévu » ≈ **{100 * temps / tot:.0f} %** de l'amplitude totale ; le reste (≈ {100 - 100 * temps / tot:.0f} %) vient des nouveaux prix (exchanges et Chainlink). "
        f"Corrélation entre la variation prévue par le thêta et la variation réelle : {np.corrcoef([x['thp'] for x in A], [x['dp'] for x in A])[0, 1]:+.2f}."]
# ---------- reaction du marche (26-33)
out += ["", "## Idées 26-33. Comment Polymarket réagit-il à une révision de E ?", ""]
R1 = [x for x in A if x.get("dmid") is not None and abs(x["dp"]) >= 0.05 and x.get("mid2") is not None and x["mid"] is not None]
TRr = [x for x in R1 if per(x["st"]) == "apprentissage"]
k_ = float(np.sum([x["dp"] * x["dmid"] for x in TRr]) / np.sum([x["dp"] ** 2 for x in TRr]))
out.append(f"Réaction normale apprise (idée 30) : le milieu du carnet bouge en moyenne de **{k_:.2f}** × la révision de E dans la même seconde ({len(TRr)} révisions ≥ 5 pts, apprentissage).")
out += ["", "| Réaction dans la même seconde | Révisions | Le carnet continue dans le sens de E dans les 2 s suivantes | dans les 5 s | Le côté de la révision gagne |", "|---|---|---|---|---|"]
for nom, f in (("sous-réaction (< 1/3 de la normale)", lambda x: x["dmid"] * np.sign(x["dp"]) < abs(x["dp"]) * k_ / 3),
               ("réaction normale", lambda x: abs(x["dp"]) * k_ / 3 <= x["dmid"] * np.sign(x["dp"]) <= abs(x["dp"]) * k_ * 2),
               ("sur-réaction (> 2× la normale)", lambda x: x["dmid"] * np.sign(x["dp"]) > abs(x["dp"]) * k_ * 2)):
    S_ = [x for x in R1 if per(x["st"]) != "apprentissage" and f(x)]
    if not S_: continue
    c2 = np.mean([(x["mid2"] - x["mid"]) * np.sign(x["dp"]) > 0.005 for x in S_]); c5 = np.mean([(x["mid5"] - x["mid"]) * np.sign(x["dp"]) > 0.005 for x in S_ if x["mid5"] is not None])
    w = np.mean([x["y"] == (x["dp"] > 0) for x in S_])
    out.append(f"| {nom} | {len(S_)} | {100 * c2:.0f} % | {100 * c5:.0f} % | {100 * w:.0f} % |")
# double cible : le prix vendeur du côté de la révision monte-t-il dans 1 s ? (AUC de chaque variable, validation + nuit)
def auc(sc, yy):
    sc = np.array(sc, float); yy = np.array(yy, bool); o = np.argsort(sc); rk = np.empty(len(sc)); rk[o] = np.arange(1, len(sc) + 1)
    n1 = yy.sum(); n0 = len(yy) - n1
    return (rk[yy].sum() - n1 * (n1 + 1) / 2) / (n1 * n0) if n1 and n0 else float("nan")
D_ = []
for x in A:
    if abs(x["dp"]) < 0.02: continue
    up = x["dp"] > 0; a0 = x["ua"] if up else x["da"]; a1 = x["ua1"] if up else x["da1"]; z0 = x["uz"] if up else x["dz"]; z05 = x["uz05"] if up else x["dz05"]; a05 = x["ua05"] if up else x["da05"]
    if a0 is None or a1 is None: continue
    retrait = (1 - z0 / z05) if (z05 and a05 == a0 and z05 > 0) else 0.0
    sp = a0 - ((x["ub"] if up else x["db"]) or a0)
    D_.append((per(x["st"]), a1 - a0 >= 0.02, abs(x["dp"]), x["ig"], abs(x["d"]), retrait, sp, (x["p"] if up else 1 - x["p"]) - a0))
out += ["", "### Idées 10, 26, 38 : prévoir que le prix vendeur du côté de la révision monte d'au moins 2 c dans la seconde (AUC : 0,5 = hasard, 1 = parfait)", "",
        "| Variable | AUC apprentissage | AUC validation + nuit |", "|---|---|---|"]
for i, nom in ((2, "taille de la révision de E"), (3, "gamma d'information"), (4, "delta"), (5, "retrait de quantité au meilleur prix sur 0,5 s (idée 35)"), (6, "spread"), (7, "avantage E − prix")):
    tr = [d for d in D_ if d[0] == "apprentissage"]; te = [d for d in D_ if d[0] != "apprentissage"]
    out.append(f"| {nom} | {auc([d[i] for d in tr], [d[1] for d in tr]):.2f} | {auc([d[i] for d in te], [d[1] for d in te]):.2f} |")
out.append(f"\nTaux de base : le prix vendeur monte d'au moins 2 c dans la seconde après une révision ≥ 2 pts dans {100 * np.mean([d[1] for d in D_]):.0f} % des cas ({len(D_)} révisions).")
# liquidite cachee (34, 37, 39)
H_ = collections.defaultdict(list)
for x in L:
    for up in (True, False):
        a0, a05 = (x["ua"], x["ua05"]) if up else (x["da"], x["da05"]); z0, z05 = (x["uz"], x["uz05"]) if up else (x["dz"], x["dz05"]); a1 = x["ua1"] if up else x["da1"]
        if a0 is None or a1 is None or a05 != a0 or not z05: continue
        k = "quantité au meilleur prix divisée par 2 ou plus en 0,5 s (prix inchangé)" if z0 <= z05 / 2 else "quantité stable ou en hausse"
        H_[k].append(a1 - a0 >= 0.02)
out += ["", "### Idées 34, 37, 39 : le carnet se vide-t-il avant que le prix monte ?", "", "| Situation | Mesures | Le prix vendeur monte d'au moins 2 c dans la seconde |", "|---|---|---|"]
for k, v in H_.items(): out.append(f"| {k} | {len(v)} | {100 * np.mean(v):.1f} % |")
# ---------- PARTIE B : carnet 8 niveaux
out += ["", "## Partie 8-10. Balayer le carnet (8 niveaux enregistrés aux signaux depuis le 10.10 01:22)", ""]
try:
    J = json.load(open("bot95/twap_carnets.json"))
    vu = {};
    for s_ in sorted(J, key=lambda s_: s_["t0"]):
        if s_["start"] not in vu and (O.get(f"BTC:{s_['start']}") or {}).get("gagnant"): vu[s_["start"]] = s_
    SS = list(vu.values())
    out.append(f"{len(SS)} cycles avec signal et résultat officiel (premier signal TWAP fin du cycle, toutes variantes confondues). Petit échantillon : à lire comme une première mesure.")
    def bal(s_, lim, cap=50.0, snap="0", prud=0.0):
        p = s_["proba"] - prud; gm = O[f"BTC:{s_['start']}"]["gagnant"] == s_["cote"]; q = mi = pn = 0.0
        for pr_, z in s_["asks"].get(snap, []):
            if p - pr_ < lim or mi >= cap: break
            qq = min(z, (cap - mi) / pr_); q += qq; mi += qq * pr_; pn += qq * ((1 if gm else 0) - pr_ - FEE(pr_))
        return pn, mi, gm
    out += ["", "| Politique (50 $ max par cycle) | Cycles achetés | Capital engagé | Résultat | Jackpots |", "|---|---|---|---|---|"]
    def best_only(s_):
        lv = s_["asks"].get("0", [])
        if not lv: return (0, 0, False)
        pr_, z = lv[0]; gm = O[f"BTC:{s_['start']}"]["gagnant"] == s_["cote"]
        if s_["proba"] - pr_ < 0.20: return (0, 0, gm)
        q = min(z, 50 / pr_); return (q * ((1 if gm else 0) - pr_ - FEE(pr_)), q * pr_, gm)
    for nom, f in (("meilleur vendeur seul (actuel)", best_only),
                   ("balayer tant que l'avantage ≥ 20 pts", lambda s_: bal(s_, 0.20)),
                   ("balayer tant que l'avantage ≥ 15 pts", lambda s_: bal(s_, 0.15)),
                   ("balayer tant que l'avantage ≥ 10 pts", lambda s_: bal(s_, 0.10)),
                   ("balayer tant que l'avantage net > 0", lambda s_: bal(s_, 0.0)),
                   ("balayer prudent (proba − 10 pts, avantage ≥ 10 pts)", lambda s_: bal(s_, 0.10, prud=0.10)),
                   ("balayer ≥ 20 pts, jusqu'à 100 $", lambda s_: bal(s_, 0.20, cap=100.0))):
        R_ = [f(s_) for s_ in SS]; R_ = [r for r in R_ if r[1] > 0]
        out.append(f"| {nom} | {len(R_)} | {sum(r[1] for r in R_):.0f} $ | **{f0(sum(r[0] for r in R_))}** | {sum(1 for r in R_ if r[0] >= 4 * r[1])} |")
    cap = {lim: [] for lim in (0.20, 0.10, 0.0)}
    for s_ in SS:
        for lim in cap:
            m_ = sum(min(z, 1e9) * pr_ for pr_, z in s_["asks"].get("0", []) if s_["proba"] - pr_ >= lim); cap[lim].append(m_)
    out += ["", "Idée 62 — capacité totale dans les 8 premiers niveaux au moment du signal (médiane / moyenne, en $) :", ""]
    for lim, v in cap.items(): out.append(f"- avantage ≥ {int(lim * 100)} pts : médiane {np.median(v):.0f} $, moyenne {np.mean(v):.0f} $ ; ≥ 50 $ disponibles dans {sum(1 for x in v if x >= 50)} cycles sur {len(v)}.")
    first = [s_["asks"]["0"][0][1] * s_["asks"]["0"][0][0] for s_ in SS if s_["asks"].get("0")]
    out.append(f"- au seul meilleur vendeur : médiane {np.median(first):.0f} $.")
    # reconstitution (64-67)
    out += ["", "Idées 64-67 — reconstitution : après le signal, le meilleur prix du signal est-il encore disponible (sans tenir compte de notre propre achat, qui n'a pas eu lieu en vrai) ?", "",
            "| Délai | Meilleur vendeur au même prix ou moins cher | Quantité médiane à ce prix ou moins cher | Capacité ≥ 20 pts d'avantage (médiane) |", "|---|---|---|---|"]
    for d_ in ("0.25", "0.5", "1", "2", "5"):
        ok = []; qq = []; cc = []
        for s_ in SS:
            a0 = s_["asks"].get("0"); a1 = s_["asks"].get(d_)
            if not a0 or not a1: continue
            p0 = a0[0][0]; ok.append(a1[0][0] <= p0 + 1e-9); qq.append(sum(z for pr_, z in a1 if pr_ <= p0 + 1e-9))
            cc.append(sum(z * pr_ for pr_, z in a1 if s_["proba"] - pr_ >= 0.20))
        if ok: out.append(f"| {d_} s | {100 * np.mean(ok):.0f} % ({len(ok)}) | {np.median(qq):.0f} jetons | {np.median(cc):.0f} $ |")
    # execution patiente (68)
    pat = []
    for s_ in SS:
        gm = O[f"BTC:{s_['start']}"]["gagnant"] == s_["cote"]; p = s_["proba"]; mi = pn = 0.0
        for snap in ("0", "1", "2"):
            lv = s_["asks"].get(snap) or []
            if not lv: continue
            pr_, z = lv[0]
            if p - pr_ < 0.20 or mi >= 50: continue
            qq = min(z, (50 - mi) / pr_); mi += qq * pr_; pn += qq * ((1 if gm else 0) - pr_ - FEE(pr_))
        if mi > 0: pat.append((pn, mi, gm))
    out.append(f"\nIdée 68 — exécution patiente (meilleur vendeur à 0 s, puis encore au meilleur vendeur à 1 s et 2 s si l'avantage reste ≥ 20 pts, 50 $ max) : {len(pat)} cycles, capital {sum(r[1] for r in pat):.0f} $, résultat **{f0(sum(r[0] for r in pat))}**.")
except Exception as e:
    out.append(f"(journal des carnets indisponible : {e})")
open("etude/bot5min/resultat_pression_reglement.md", "w").write("\n".join(out)); print("\n".join(out))
