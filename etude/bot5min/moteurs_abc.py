"""BOT95 — TROIS MOTEURS FANTÔMES SUR LES MÊMES SIGNAUX (demande de Pitch, 11.10.2026). Hors ligne : aucun bot, aucun workflow, rien publié.
Lancer depuis la racine : python3 etude/bot5min/moteurs_abc.py → etude/bot5min/resultat_moteurs_abc.md

Univers de signaux (identique pour les 3 moteurs) : premier signal du cycle de la cohorte A « désaccord 30 zone + modèle monte » (probabilité
enregistrée du bot) et de la cohorte B « V2-F corrigé 0,015 % » (modèle reconstruit À LA DATE, fuite de parts_r corrigée : la seconde courante
n'est jamais lue en fin de seconde) ; V2-F original (O8) en diagnostic. Chaque signal = une position indépendante de 50 $ (aucun plafond de capital).
  A  désaccord brut      : règle actuelle, on envoie tous les signaux (limite = prix vu au signal).
  B  désaccord corrigé   : probabilité recalibrée sur l'apprentissage (logistique sur logit(proba modèle), logit(milieu Polymarket), cohorte) ;
                           on envoie si proba calibrée − prix − frais > marge (marge choisie sur l'apprentissage).
  C  alpha exécutable    : P(offre encore là après notre délai) et P(gain | offre encore là), deux logistiques apprises sur l'apprentissage avec des
                           variables connues au signal ; valeur attendue d'ENVOYER = P(survie)·[P(gain|survie) − prix − frais] ; on envoie si > marge ;
                           limite = prix maximal (plafond) tiré de P(gain|survie) − marge ; quantité ≤ taille affichée.
Exécution : meilleur niveau seulement, quantité affichée, frais 0,072·p·(1−p) par part, 50 $ (frais compris). Idéale 0 s (ligne du signal),
PRUDENTE 0,3 s (première ligne ≥ t + 0,3 s, résultat principal), pessimiste 0,6 s (moitié de la taille affichée). Tout paramètre est appris sur
l'apprentissage puis figé pour validation et test."""
import sys, json, glob, math, time, collections
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
_src = open("etude/bot5min/audit_temporel.py").read()
exec(_src.split("# ===================================================================== 3. fantôme réel")[0])
_g = "P1v = " + _src.split("\nP1v = ", 1)[1].split("G_leak = {}")[0]
exec(_g)
log("socle audit_temporel chargé")
lgt = lambda x: math.log(min(0.999, max(0.001, x)) / (1 - min(0.999, max(0.001, x))))
fq = lambda a: 50 / (a + FEE(a))

# ===================================================================== signaux
X15 = parts_model(False, 1.5e-4)                 # cohorte B : modèle reconstruit 0,015 %, valeur À LA DATE de la seconde courante
log("modèle X15 sans fuite")
def zone_monte(P):
    """cohorte A : 60 s restantes au moins, vendeur 0,15-0,35, écart ≥ 0,30, modèle monté d'au moins 3 c en 3 s (meta_router « Zone 30 + modèle monte »)"""
    p = P[FI]; p3 = np.where(J3ok, p[np.maximum(J3, 0)], np.nan); tl = STF + 300 - TF; o = {}
    with np.errstate(invalid="ignore"):
        cu = (UA[FI] >= 0.15) & (UA[FI] < 0.35) & (p - UA[FI] >= 0.30) & (p - p3 >= 0.03) & (tl > 60)
        cd = (DA[FI] >= 0.15) & (DA[FI] < 0.35) & ((1 - p) - DA[FI] >= 0.30) & ((1 - p) - (1 - p3) >= 0.03) & (tl > 60)
    for j in np.nonzero(cu | cd)[0]:
        st = int(STF[j])
        if st in o or st not in GAGN: continue
        up = bool(cu[j]); o[st] = (int(FI[j]), up, float(UA[FI[j]] if up else DA[FI[j]]), float(p[j] if up else 1 - p[j]))
    return o
def premier_regle(P, f):
    p = P[FI]; tl = STF + 300 - TF; o = {}
    with np.errstate(invalid="ignore"):
        cu = (UA[FI] >= 0.02) & (UA[FI] <= 0.98) & f(p - UA[FI], tl); cd = (DA[FI] >= 0.02) & (DA[FI] <= 0.98) & f((1 - p) - DA[FI], tl)
    for j in np.nonzero(cu | cd)[0]:
        st = int(STF[j])
        if st in o or st not in GAGN: continue
        up = bool(cu[j]); o[st] = (int(FI[j]), up, float(UA[FI[j]] if up else DA[FI[j]]), float(p[j] if up else 1 - p[j]))
    return o
COH = {"A": zone_monte(P2), "B": signaux(X15), "V2-F O8": SIGS["O8"]}
EXTRA = {"désaccord 30": premier_regle(P2, lambda e, tl: (e >= 0.30) & (tl >= 5)),
         "désaccord 20 60-180 s": premier_regle(P2, lambda e, tl: (e >= 0.20) & (tl > 60) & (tl <= 180))}
log("cohortes", {k: len(v) for k, v in COH.items()})

# ===================================================================== exécution
def ligne_apres(st, t, d):
    pos = CFI[st]; tt = TF[pos]; k = np.searchsorted(tt, t + d - 1e-9, "left")
    return None if k >= len(pos) or tt[k] >= st + 300 else int(FI[pos[k]])
def remplir(s, d, lim, qf=1.0):
    """s : dict du signal. Achat preneur au meilleur vendeur de la ligne d'exécution si ≤ lim ; quantité affichée × qf ; 50 $ frais compris."""
    g = s["g"] if d <= 0 else ligne_apres(s["st"], s["t"], d)
    if g is None: return None
    a = UA[g] if s["up"] else DA[g]; z = (UAZ[g] if s["up"] else DAZ[g]) * qf
    if not np.isfinite(a) or a > lim + 1e-9 or not np.isfinite(z): return None
    q = min(fq(a), z)
    if q < 1: return None
    return dict(q=q, a=a, pn=q * ((1 if s["w"] else 0) - a - FEE(a)), mise=q * (a + FEE(a)), partiel=q < fq(a) - 1e-6)
MODES = {"idéale 0 s": (0.0, 1.0), "prudente 0,3 s": (0.3, 1.0), "pessimiste 0,6 s": (0.6, 0.5)}

# ===================================================================== variables connues au signal
def val_at(arr_, t):
    i = np.searchsorted(T, t, "right") - 1
    return arr_[i] if i >= 0 else np.nan
SIG = []
for coh, D in COH.items():
    for st, (g, up, a0, fair) in sorted(D.items()):
        t = T[g]; side_a = UA if up else DA; side_z = UAZ if up else DAZ; side_b = UB if up else DB
        z0 = side_z[g]
        if not np.isfinite(z0) or min(fq(a0), z0) < 1: continue
        b0 = side_b[g]; mid = (a0 + b0) / 2 if np.isfinite(b0) else a0
        i30 = np.searchsorted(T, t - 30, "left"); xb = X["bybit"][i30:g + 1]
        vol = float(np.nanstd(np.diff(xb))) if len(xb) > 5 else 0.0
        a1, a3 = val_at(side_a, t - 1), val_at(side_a, t - 3); z1 = val_at(side_z, t - 1)
        mod = P2 if coh != "B" else X15; f3 = val_at(mod, t - 3); f3 = (f3 if up else 1 - f3) if np.isfinite(f3) else fair
        SIG.append(dict(coh=coh, st=st, per=PER(st), g=g, t=t, up=up, a0=a0, z0=z0, fair=fair, w=GAGN[st] == up, mid=mid,
                        spr=(a0 - b0) if np.isfinite(b0) else 0.05, tl=st + 300 - t, vol=vol,
                        da1=a0 - a1 if np.isfinite(a1) else 0.0, da3=a0 - a3 if np.isfinite(a3) else 0.0,
                        dz1=math.log1p(z0) - math.log1p(z1) if np.isfinite(z1) else 0.0, df3=fair - f3,
                        agB=min(AGE["bybit"][g], 10), agO=min(AGE["okx"][g], 10), agC=min(AGE["chainlink"][g], 10),
                        jour=time.strftime("%d.%m", time.gmtime(st + 7200))))
for s in SIG:
    s["ideal"] = remplir(s, 0, s["a0"]); s["surv"] = remplir(s, 0.3, s["a0"]) is not None
    s["jackpot"] = bool(s["ideal"] and s["ideal"]["pn"] >= 4 * s["ideal"]["mise"])
U = [s for s in SIG if s["coh"] in ("A", "B")]; DIAG = [s for s in SIG if s["coh"] == "V2-F O8"]
log("signaux", collections.Counter((s["coh"], s["per"]) for s in SIG))

# ===================================================================== sélection adverse : offre encore là à 0,3 s
def adverse(D):
    res = {}
    for p in PERS + ("toutes",):
        L = [(st, x) for st, x in D.items() if p == "toutes" or PER(st) == p]
        sv = [(st, x) for st, x in L if remplir(dict(st=st, g=x[0], t=T[x[0]], up=x[1], w=GAGN[st] == x[1]), 0.3, x[2]) is not None]
        ns = [(st, x) for st, x in L if (st, x) not in sv]
        wr = lambda M: (sum(GAGN[st] == x[1] for st, x in M), len(M))
        res[p] = (wr(sv), wr(ns))
    return res
ADV = {k: adverse(v) for k, v in list(COH.items()) + list(EXTRA.items())}
# même mesure sur le direct (vitesse.json : offre au prix encore achetable 0,25 s après)
WIN = dict(GAGN)
for e in json.load(open("bot95/reglements.json")):
    if e.get("a") == "BTC" and e.get("gagnant") and e["start"] not in WIN: WIN[e["start"]] = e["gagnant"] == "Up"
VIT = json.load(open("bot95/vitesse.json"))
LIVEADV = collections.defaultdict(lambda: [0, 0, 0, 0])
for e in VIT:
    if e["start"] not in WIN or "0.25" not in e.get("apres", {}): continue
    gm = WIN[e["start"]] == (e["cote"] == "Up"); ok = e["apres"]["0.25"].get("partsAuPrix", 0) > 0
    for k in (e["nom"], "tous"):
        L_ = LIVEADV[k]; L_[0 if ok else 2] += 1; L_[1 if ok else 3] += gm
log("sélection adverse")

# ===================================================================== modèles appris sur l'apprentissage
TR = [s for s in U if s["per"] == "apprentissage"]
def fcal(s): return [lgt(s["fair"]), lgt(s["mid"]), 1.0 if s["coh"] == "B" else 0.0]
CAL = LogisticRegression(C=1.0, max_iter=1000).fit(np.array([fcal(s) for s in TR]), np.array([s["w"] for s in TR]))
for s in SIG: s["pc"] = float(CAL.predict_proba(np.array([fcal(s)]))[0, 1])
FN = ["logit proba calibrée", "logit prix", "log taille affichée", "écart calibré − prix", "variation du prix 1 s", "variation du prix 3 s", "variation de taille 1 s",
      "variation du modèle 3 s", "temps restant", "volatilité Bybit 30 s", "écart vendeur-acheteur", "âge Bybit (ind.)", "âge OKX (ind.)", "âge Chainlink (ind.)", "cohorte B"]
def feat(s): return [lgt(s["pc"]), lgt(s["a0"]), math.log1p(s["z0"]), s["pc"] - s["a0"], s["da1"], s["da3"], s["dz1"], s["df3"], s["tl"] / 300, s["vol"], s["spr"],
                     s["agB"], s["agO"], s["agC"], 1.0 if s["coh"] == "B" else 0.0]
Ftr = np.array([feat(s) for s in TR]); MU, SD = Ftr.mean(0), Ftr.std(0) + 1e-9
nz = lambda s: (np.array(feat(s)) - MU) / SD
MS = LogisticRegression(C=0.5, max_iter=2000).fit((Ftr - MU) / SD, np.array([s["surv"] for s in TR]))
TRs = [s for s in TR if s["surv"]]
MW = LogisticRegression(C=0.5, max_iter=2000).fit(np.array([nz(s) for s in TRs]), np.array([s["w"] for s in TRs]))
for s in SIG:
    f_ = nz(s)[None]; s["ps"] = float(MS.predict_proba(f_)[0, 1]); s["pw"] = float(MW.predict_proba(f_)[0, 1])
def auc(L, k, y):
    yy = np.array([s[y] for s in L])
    return roc_auc_score(yy, [s[k] for s in L]) if 0 < yy.sum() < len(yy) else float("nan")
AUC = {p: (auc([s for s in U if s["per"] == p], "ps", "surv"), auc([s for s in U if s["per"] == p and s["surv"]], "pw", "w"),
           auc([s for s in U if s["per"] == p], "pc", "w"), auc([s for s in U if s["per"] == p], "fair", "w")) for p in PERS}
def plafond(p, m):
    r = p - m
    if r <= 0.01: return 0.0
    c = (1.072 - math.sqrt(1.072 ** 2 - 4 * 0.072 * r)) / (2 * 0.072)
    return math.floor(c * 100 + 1e-9) / 100

# ---- moteurs : décision (envoyer ? limite ?)
def dec_A(s, prm): return s["a0"]
def dec_B(s, prm):
    return s["a0"] if s["pc"] - s["a0"] - FEE(s["a0"]) > prm else None
def dec_C(s, prm):
    ev = s["ps"] * (s["pw"] - s["a0"] - FEE(s["a0"]))
    if ev <= prm: return None
    return max(s["a0"], plafond(s["pw"], prm))           # limite = plafond (jamais sous le prix vu)
DEC = {"A désaccord brut": dec_A, "B désaccord corrigé": dec_B, "C alpha exécutable": dec_C}
# diagnostics : séparer l'effet « sélection » de l'effet « plafond de prix » dans C
def dec_Csel(s, prm):
    return s["a0"] if s["ps"] * (s["pw"] - s["a0"] - FEE(s["a0"])) > prm else None
def dec_Apl(s, prm): return max(s["a0"], plafond(s["pw"], PRM["C alpha exécutable"]))
DIAGD = {"C sélection seule (limite = prix du signal)": (dec_Csel, "C alpha exécutable"), "A + plafond de C (tout envoyer, limite = plafond)": (dec_Apl, "C alpha exécutable")}
def jouer(eng, prm, L, mode="prudente 0,3 s"):
    d, qf = MODES[mode]; o = []
    for s in L:
        lim = DEC[eng](s, prm)
        o.append((s, lim is not None, remplir(s, d, lim, qf) if lim is not None else None))
    return o
GRID = {"A désaccord brut": [None], "B désaccord corrigé": [0.0, 0.05, 0.10, 0.15, 0.20, 0.25], "C alpha exécutable": [-0.02, 0.0, 0.01, 0.02, 0.05]}
PRM, GRIDRES = {}, {}
for e in DEC:
    g = {m: sum(x["pn"] for _, _, x in jouer(e, m, TR) if x) for m in GRID[e]}
    PRM[e] = max(g, key=g.get); GRIDRES[e] = g
log("paramètres", PRM)
for nm, (f, base) in DIAGD.items(): DEC[nm] = f; PRM[nm] = PRM[base]

# ===================================================================== bilans
RNG = np.random.default_rng(20261011)
def stats(R):
    T_ = [x for _, _, x in sorted(R, key=lambda r: r[0]["t"]) if x]; pn = np.array([x["pn"] for x in T_]) if T_ else np.zeros(0)
    cum = np.cumsum(pn) if len(pn) else np.zeros(1); dd = float(min(0, np.min(cum - np.maximum.accumulate(np.r_[0, cum])[1:]))) if len(pn) else 0.0
    st_ = mx = 0
    for x in T_: st_ = 0 if x["pn"] > 0 else st_ + 1; mx = max(mx, st_)
    jk = [r for r in R if r[0]["jackpot"]]
    return dict(n=len(R), env=sum(1 for r in R if r[1]), fill=len(T_), part=sum(1 for x in T_ if x["partiel"]), pnl=float(pn.sum()),
                win=sum(1 for x in T_ if x["pn"] > 0), dd=dd, serie=mx, jk=sum(1 for r in jk if r[2] and r[2]["pn"] > 0), njk=len(jk))
def boot(RA, RE):
    H = collections.defaultdict(float)
    for (s, _, xa), (_, _, xe) in zip(RA, RE): H[s["st"] // 3600] += (xe["pn"] if xe else 0) - (xa["pn"] if xa else 0)
    hv = np.array(list(H.values()))
    if len(hv) < 2: return float(hv.sum()), float("nan"), float("nan")
    rg = np.random.default_rng(20261011); sims = hv[rg.integers(0, len(hv), (4000, len(hv)))].sum(1)
    return float(hv.sum()), float(np.percentile(sims, 5)), float(np.percentile(sims, 95))
RES = {}
for e in DEC:
    for mode in MODES:
        for p in PERS:
            L = [s for s in U if s["per"] == p]
            RES[(e, mode, p)] = jouer(e, PRM[e], L, mode)
log("rejeux")

# ===================================================================== rédaction
out = []; add = lambda *l: out.extend(l)
EN = [e for e in DEC if e not in DIAGD]
def dl(e, p, mode="prudente 0,3 s"): return boot(RES[("A désaccord brut", mode, p)], RES[(e, mode, p)])
gagnant = [e for e in EN[1:] if dl(e, "validation")[0] > 0 and dl(e, "test")[0] > 0]
adv_all = ADV["A"]["toutes"], ADV["B"]["toutes"], ADV["V2-F O8"]["toutes"]
lv = LIVEADV["tous"]
add("# BOT95 — Trois moteurs fantômes sur les mêmes signaux (A brut · B corrigé · C alpha exécutable)", "",
    f"Étude hors ligne du 11.10.2026 — aucun bot, aucun workflow modifié, rien publié. {len(valides_all)} cycles BTC réglés ({hs(valides_all[0])} → {hs(valides_all[-1] + 300)}, heure suisse) : "
    f"apprentissage < {hs(CUT)} · validation → {hs(MATIN0)} · test après (déjà en partie regardé par d'autres études : **exploratoire**). "
    "Positions indépendantes de 50 $ (frais compris), aucun plafond de capital. Résultat principal = exécution PRUDENTE 0,3 s ; référence = moteur A (= GARDER chaque signal tel qu'aujourd'hui). "
    "Fuite de `parts_r` corrigée : la cohorte B utilise le modèle 0,015 % calculé avec la valeur À LA DATE de la seconde courante.", "",
    "## Verdict (en tête)", "")
for e in EN[1:]:
    v, t = dl(e, "validation"), dl(e, "test")
    add(f"- **{e}** contre A (prudente 0,3 s) : validation {f0(v[0])} [IC 90 % {f0(v[1])} ; {f0(v[2])}] · test {f0(t[0])} [{f0(t[1])} ; {f0(t[2])}] → "
        + ("**amélioration nette sur les deux périodes**" + (" (IC encore à cheval sur 0 : à confirmer en direct)" if v[1] <= 0 or t[1] <= 0 else "") if e in gagnant else "**pas d'amélioration nette sur les deux périodes**") + ".")
pP = lambda e, p: stats(RES[(e, "prudente 0,3 s", p)])
add(f"- **Résultats absolus (prudente 0,3 s)** : " + " ; ".join(f"{e.split(' ')[0]} " + " / ".join(f0(pP(e, p)['pnl']) for p in PERS) for e in EN) + " (apprentissage / validation / test). "
    f"C participe à {pc(pP('C alpha exécutable', 'validation')['env'], pP('C alpha exécutable', 'validation')['n'])} des signaux en validation et {pc(pP('C alpha exécutable', 'test')['env'], pP('C alpha exécutable', 'test')['n'])} en test : "
    "il **perd moins** que A, il n'est **pas rentable** en test.",
    f"- **B = A** : la marge choisie sur l'apprentissage ({fr(PRM['B désaccord corrigé'])}) laisse passer tous les signaux (la calibration ne trie rien : toutes les probabilités calibrées restent au-dessus du prix + frais).",
    f"- **D'où vient l'écart de C** : la sélection seule (limite = prix du signal) fait validation {f0(dl('C sélection seule (limite = prix du signal)', 'validation')[0])}, test {f0(dl('C sélection seule (limite = prix du signal)', 'test')[0])} ; "
    f"le plafond de prix seul (tout envoyer) fait {f0(dl('A + plafond de C (tout envoyer, limite = plafond)', 'validation')[0])} / {f0(dl('A + plafond de C (tout envoyer, limite = plafond)', 'test')[0])}.")
add(f"- **Gagnant déclaré : {', '.join(gagnant) if gagnant else 'aucun'}** (règle : amélioration nette en validation ET en test).",
    f"- **Sélection adverse confirmée sur les lignes 0,3 s** (toutes périodes) : cohorte A — offre encore là à 0,3 s : {pc(adv_all[0][0][0], adv_all[0][0][1])} gagnés ({adv_all[0][0][1]}), disparue : {pc(adv_all[0][1][0], adv_all[0][1][1])} ({adv_all[0][1][1]}) ; "
    f"cohorte B : {pc(adv_all[1][0][0], adv_all[1][0][1])} ({adv_all[1][0][1]}) contre {pc(adv_all[1][1][0], adv_all[1][1][1])} ({adv_all[1][1][1]}) ; V2-F original : {pc(adv_all[2][0][0], adv_all[2][0][1])} ({adv_all[2][0][1]}) contre {pc(adv_all[2][1][0], adv_all[2][1][1])} ({adv_all[2][1][1]}). "
    f"En direct (vitesse.json, 0,25 s, tous fantômes) : {pc(lv[1], lv[0])} ({lv[0]}) contre {pc(lv[3], lv[2])} ({lv[2]}).",
    f"- **Pourquoi C ne peut pas faire mieux que « choisir ce qui reste »** : P(survie) est bien prévisible (AUC validation {fr(AUC['validation'][0])}, test {fr(AUC['test'][0])}), "
    f"mais P(gain | offre encore là) ne l'est presque pas (AUC validation {fr(AUC['validation'][1])}, test {fr(AUC['test'][1])}) ; la probabilité du modèle seule : AUC {fr(AUC['validation'][3])} / {fr(AUC['test'][3])}.", "")

# ---- 1. sélection adverse
add("## 1. Sélection adverse : l'offre encore achetable après notre délai gagne-t-elle moins souvent ?", "",
    "Offre « encore là » = à la première ligne ≥ signal + 0,3 s, le meilleur vendeur est ≤ prix du signal avec ≥ 1 part. Taux de gain du côté acheté (issue officielle).", "",
    "| Signaux | Période | Offre encore là : gagnés | n | Offre disparue : gagnés | n |", "|---|---|---|---|---|---|")
for k, R in ADV.items():
    for p, ((w1, n1), (w2, n2)) in R.items(): add(f"| {k} | {p} | {pc(w1, n1)} | {n1} | {pc(w2, n2)} | {n2} |")
add("", "Direct (vitesse.json, offre au prix encore achetable 0,25 s après le signal, cycles réglés) :", "", "| Fantôme | Encore là : gagnés | n | Disparue : gagnés | n |", "|---|---|---|---|---|")
for k, v in sorted(LIVEADV.items(), key=lambda x: -(x[1][0] + x[1][2])): add(f"| {k} | {pc(v[1], v[0])} | {v[0]} | {pc(v[3], v[2])} | {v[2]} |")
add("", "Lecture : quand l'offre disparaît, c'est souvent qu'un autre acheteur mieux informé (ou plus rapide) l'a prise — nous n'obtenons que les offres que personne ne voulait.", "")

# ---- 2. paramètres
add("## 2. Modèles et paramètres (appris sur l'apprentissage, figés ensuite)", "",
    f"- Signaux d'apprentissage : {len(TR)} (A {sum(1 for s in TR if s['coh'] == 'A')}, B {sum(1 for s in TR if s['coh'] == 'B')}) ; offre encore là à 0,3 s : {sum(s['surv'] for s in TR)}.",
    f"- Calibration (moteur B) : logistique sur logit(proba du modèle), logit(milieu Polymarket), cohorte → coefficients {', '.join(fr(c, 2) for c in CAL.coef_[0])}, constante {fr(CAL.intercept_[0], 2)}.",
    f"- Moteur C : variables = {', '.join(FN)} (âges = indicateur « dernier changement », pas l'âge vrai).",
    "", "| Période | AUC P(survie) | AUC P(gain | survie) | AUC proba calibrée → gain | AUC proba du modèle → gain |", "|---|---|---|---|---|")
for p in PERS: add(f"| {p} | {fr(AUC[p][0])} | {fr(AUC[p][1])} | {fr(AUC[p][2])} | {fr(AUC[p][3])} |")
add("", "Marge choisie sur l'apprentissage (P&L prudent d'apprentissage par marge) :", "")
for e in EN[1:]: add(f"- {e} : **{fr(PRM[e])}** — " + " · ".join(f"{fr(m)} → {f0(v)}" for m, v in GRIDRES[e].items()))
add("")

# ---- 3. bilans
add("## 3. Bilans par moteur et par période", "",
    "Participation = ordres envoyés / signaux disponibles. Remplis = achats réellement faits (partiels inclus). Jackpots = signaux qui rapportent ≥ 4× la mise à l'exécution idéale ; « gardés » = gagnés par le moteur.", "")
for p in PERS:
    add(f"### {p}", "", "| Moteur | Exécution | Signaux | Envoyés | Remplis (partiels) | Gagnés | P&L net | Δ vs A [IC 90 % blocs 1 h] | Jackpots gardés / manqués | Pire suite de pertes | Creux max |",
        "|---|---|---|---|---|---|---|---|---|---|---|")
    for e in EN:
        for mode in MODES:
            S_ = stats(RES[(e, mode, p)]); d_ = boot(RES[("A désaccord brut", mode, p)], RES[(e, mode, p)])
            dtxt = "—" if e == "A désaccord brut" else f"{f0(d_[0])} [{f0(d_[1])} ; {f0(d_[2])}]"
            b = "**" if mode.startswith("prudente") else ""
            add(f"| {e} | {mode} | {S_['n']} | {S_['env']} ({pc(S_['env'], S_['n'])}) | {S_['fill']} ({S_['part']}) | {pc(S_['win'], S_['fill'])} | {b}{f0(S_['pnl'])}{b} | {dtxt} | "
                f"{S_['jk']} / {S_['njk'] - S_['jk']} | {S_['serie']} | {f0(S_['dd'])} |")
    add("")
# par cohorte (prudente)
add("### Par cohorte (prudente 0,3 s)", "", "| Moteur | Cohorte | apprentissage | validation | test |", "|---|---|---|---|---|")
for e in EN:
    for c in ("A", "B"):
        add(f"| {e} | {c} | " + " | ".join(f"{f0(sum(x['pn'] for s, _, x in RES[(e, 'prudente 0,3 s', p)] if x and s['coh'] == c))} ({sum(1 for s, _, x in RES[(e, 'prudente 0,3 s', p)] if x and s['coh'] == c)})" for p in PERS) + " |")
add("")
add("### Diagnostic : d'où vient l'écart de C ? (Δ vs A, prudente 0,3 s)", "", "| Variante | apprentissage | validation | test |", "|---|---|---|---|")
for e in list(DIAGD) + ["C alpha exécutable"]:
    add(f"| {e} | " + " | ".join(f"{f0(dl(e, p)[0])} [{f0(dl(e, p)[1])} ; {f0(dl(e, p)[2])}]" for p in PERS) + " |")
add("")
# par jour
add("## 4. Par jour (prudente 0,3 s, heure suisse)", "", "| Jour | Signaux | " + " | ".join(EN) + " |", "|---|---|" + "---|" * len(EN))
jours = sorted({s["jour"] for s in U}, key=lambda j: (j[3:], j[:2]))
for j in jours:
    cells = []
    for e in EN:
        tot = sum(x["pn"] for p in PERS for s, _, x in RES[(e, "prudente 0,3 s", p)] if x and s["jour"] == j)
        cells.append(f0(tot))
    add(f"| {j} | {sum(1 for s in U if s['jour'] == j)} | " + " | ".join(cells) + " |")
add("")
# diagnostic V2-F original
add("## 5. Diagnostic : V2-F original (O8), mêmes moteurs appliqués sans réapprentissage", "",
    "Les modèles B et C ont été appris sur les cohortes A et B ; on les applique tels quels aux signaux V2-F original (cohorte « B » = 0 dans les variables). Diagnostic seulement.", "",
    "| Moteur | apprentissage | validation | test |", "|---|---|---|---|")
for e in EN:
    add(f"| {e} | " + " | ".join(f"{f0(stats(jouer(e, PRM[e], [s for s in DIAG if s['per'] == p]))['pnl'])}" for p in PERS) + " |")
add("")
# ---- 6. ce qu'il faut pour C en direct
add("## 6. Faire tourner le moteur C comme fantôme en direct : ce qu'il faut à l'enregistreur de Dublin (branche donnees-rapide)", "",
    "Le moteur C a besoin, AU MOMENT du signal, des mêmes variables qu'ici, calculées exactement comme dans ce fichier, puis de l'issue de l'ordre :", "",
    "- **À la décision (signal A ou B)** : heure locale et heure Polymarket ; côté ; meilleur vendeur et sa taille, meilleur acheteur ; vendeur et taille 1 s et 3 s avant ; "
    "probabilité du modèle (r[2] pour A, modèle 0,015 % à la date pour B) et sa valeur 3 s avant ; temps restant ; volatilité Bybit 30 s ; "
    "**âge VRAI** de Bybit, OKX, Chainlink (horodatage source, pas l'indicateur « dernier changement ») ; P(survie), P(gain|survie), valeur attendue, plafond, décision C (envoyer oui/non).",
    "- **Après la décision** : carnet Up complet ±3 c toutes les 50 ms pendant 3 s (pour savoir si l'offre est restée, à quel prix et quelle quantité était achetable à 0,1 / 0,25 / 0,3 / 0,6 s) ; "
    "**transactions Polymarket** sur notre jeton dans ces 3 s (qui a pris l'offre : distinguer « prise par un autre acheteur » de « retirée par le vendeur ») ; carnet Down idem (miroir).",
    "- **Fantôme C** : ordre fictif limite au plafond, envoyé au temps réel mesuré Cloudflare → Polymarket (aller-retour noté), rempli seulement si une ligne ≥ envoi + latence montre un vendeur ≤ plafond ; "
    "quantité ≤ taille affichée ; noter remplissage, prix, partiel, et l'issue officielle du cycle.",
    "- **Volume nécessaire** : les modèles sont appris sur ~" + str(len(TR)) + " signaux d'apprentissage ; il faut au moins autant de signaux enregistrés à 50 ms avec âges vrais pour réapprendre P(survie) et P(gain|survie) "
    "sur les données de Dublin, puis une période de validation de taille comparable avant tout passage en réel.", "")
open("etude/bot5min/resultat_moteurs_abc.md", "w").write("\n".join(out))
log("écrit etude/bot5min/resultat_moteurs_abc.md", len(out), "lignes")
