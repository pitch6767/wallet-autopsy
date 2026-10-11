"""HEDGE PRICE PREDICTOR — demande de Pitch (11.10.2026). Hors ligne, aucune modification du bot.
Question : une position Up ou Down est ouverte ; peut-on acheter le côté OPPOSÉ moins cher dans les 0,25 / 0,5 / 1 / 3 / 5 / 10 s ?
1. Jeu de décisions : chaque seconde après chaque entrée (4 stratégies rejouées), côté opposé : meilleur vendeur + taille affichée.
2. Régressions logistiques pré-enregistrées (apprentissage seulement) : P(baisse >= 1/2/3/5/10 c dans H) et P(prix plus haut à H).
3. Contrôle sous-seconde avec les photos 100 ms (lead.json.gz).
4-8. Politiques de couverture à budget identique, déclencheurs pré-enregistrés, délai 0 / 0,3 s, IC bootstrap par blocs d'une heure.
Usage : python3 etude/bot5min/hedge_predictor.py (depuis /home/claude/wallet-autopsy)"""
import time as _time
_T0 = _time.time()
exec(open("etude/bot5min/v3_commun.py").read())
import warnings
warnings.filterwarnings("ignore")
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

HS = [0.25, 0.5, 1, 3, 5, 10]
CS = [1, 2, 3, 5, 10]
fH = lambda h: (f"{h:g} s").replace(".", ",")
pc = lambda x: f"{100 * x:.1f} %".replace(".", ",")
f2 = lambda x: f"{x:.2f}".replace(".", ",").replace("-", "−")
f3 = lambda x: f"{x:.3f}".replace(".", ",").replace("-", "−")
PER3 = ("apprentissage", "validation", "inédit")

# ---------------------------------------------------------------- tableaux numpy par cycle
A = {}
def arr(st):
    if st in A: return A[st]
    R_ = C[st]
    T = np.array([r[0] for r in R_], float)
    g = lambda c: np.array([(r[c] if r[c] is not None else np.nan) for r in R_], float)
    X = np.stack([g(c) for c in (11, 12, 13, 14, 15)], 1)
    for j in range(X.shape[1]):                       # report de la dernière valeur connue (jamais de valeur future)
        col = X[:, j]; m = np.isnan(col)
        if m.any() and not m.all():
            idx = np.where(~m, np.arange(len(col)), 0); np.maximum.accumulate(idx, out=idx); col[:] = col[idx]
    d = dict(T=T, P=g(2), UB=g(3), UA=g(4), DB=g(5), DA=g(6), UBZ=np.nan_to_num(g(7)), UAZ=np.nan_to_num(g(8)),
             DBZ=np.nan_to_num(g(9)), DAZ=np.nan_to_num(g(10)), X=X, K=g(16), end=st + 300)
    A[st] = d; return d
def cote(d, up):
    """vues du point de vue de la position : own = notre côté, opp = côté opposé ; sg = +1 si Up"""
    if up: return dict(oa=d["UA"], ob=d["UB"], obz=d["UBZ"], pa=d["DA"], paz=d["DAZ"], fair=d["P"], sg=1.0)
    return dict(oa=d["DA"], ob=d["DB"], obz=d["DBZ"], pa=d["UA"], paz=d["UAZ"], fair=1 - d["P"], sg=-1.0)
le = lambda T, t: np.searchsorted(T, t, "right") - 1    # dernière ligne d'horodatage <= t
ge = lambda T, t: np.searchsorted(T, t, "left")         # première ligne d'horodatage >= t

FNOMS = ["temps restant", "vendeur opposé", "log taille opposée", "vendeur de notre côté", "proba modèle notre côté",
         "variation vendeur opposé 1 s", "variation vendeur opposé 3 s"] + \
        [f"{b} 1 s" for b in ("Bybit", "OKX", "Coinbase", "Binance", "Chainlink")] + \
        [f"{b} 3 s" for b in ("Bybit", "OKX", "Coinbase", "Binance", "Chainlink")] + \
        ["écart vendeur-acheteur", "distance au prix d'exercice (Chainlink)", "distance au prix d'exercice (perp)"]
def feats(d, s, td):
    """td : instants de décision (array). Uniquement des lignes d'horodatage <= td."""
    T = d["T"]; k = le(T, td); k1 = np.maximum(le(T, td - 1), 0); k3 = np.maximum(le(T, td - 3), 0)
    pa = s["pa"]; sg = s["sg"]; X = d["X"]
    F = np.column_stack([d["end"] - td, pa[k], np.log1p(s["paz"][k]), s["oa"][k], s["fair"][k], pa[k] - pa[k1], pa[k] - pa[k3],
                         (X[k] - X[k1]) * sg, (X[k] - X[k3]) * sg, d["UA"][k] - d["UB"][k],
                         (X[k, 4] - d["K"][k]) * sg, (X[k, 0] - d["K"][k]) * sg])
    return F, k

# ---------------------------------------------------------------- positions : 4 stratégies
def v1_like(st):
    """V1 du bot : vendeur 0,55-0,56, modèle >= 0,63 (PMIN + MARGE), élan perp Bybit 5 s dans notre sens, 1 entrée par cycle"""
    R_ = C[st]; T_ = TT[st]; end = st + 300
    for i, r in enumerate(R_):
        if end - r[0] < 5: break
        j5 = bisect.bisect_right(T_, r[0] - 5) - 1
        if j5 < 0 or not r[11] or not R_[j5][11]: continue
        el = r[11] - R_[j5][11]
        for up in (True, False):
            a = r[4] if up else r[6]; fair = r[2] if up else 1 - r[2]
            if a is None or not (0.55 <= a <= 0.56) or fair < 0.63 or el * (1 if up else -1) <= 0: continue
            return dict(i=i, t=r[0], up=up, a=a, tl=end - r[0], fair=fair)
    return None
POS_STRATS = {"désaccord 20": D20, "V2-F original": STRATS["V2-F original (O8)"], "désaccord 30": STRATS["désaccord 30"],
              "V1 (0,55-0,56)": {st: x for st in valides for x in [v1_like(st)] if x}}
for nom, S_ in POS_STRATS.items():
    for st, s in S_.items():
        if "fair" not in s: s["fair"] = C[st][s["i"]][2] if s["up"] else 1 - C[st][s["i"]][2]
POS = {}                                           # nom -> liste de positions exécutées
for nom, S_ in POS_STRATS.items():
    L = []
    for st in sorted(S_):
        s = S_[st]; e = exe(st, s)
        if e: L.append(dict(st=st, s=s, e=e, per=PER(st)))
    POS[nom] = L
print("positions", {k: len(v) for k, v in POS.items()}, f"{_time.time() - _T0:.0f} s", flush=True)

# ---------------------------------------------------------------- 1-2. jeu de décisions (chaque seconde après l'entrée)
DEC = {}                                            # (st, up, seconde entière) -> une seule fois même si plusieurs stratégies
for nom, L in POS.items():
    for p in L:
        st, s = p["st"], p["s"]; end = st + 300
        for kk in range(1, int(end - s["t"])):
            td = s["t"] + kk
            if end - td < 1.25: break
            DEC.setdefault((st, s["up"], int(td)), td)
ROWS = collections.defaultdict(list)
for (st, up, _), td in DEC.items(): ROWS[(st, up)].append(td)
FX, Y, YR, VALID, PERX, STX, META = [], [], [], [], [], [], []
for (st, up), tds in sorted(ROWS.items()):
    d = arr(st); s = cote(d, up); T = d["T"]; td = np.array(sorted(tds))
    F, k = feats(d, s, td); pa = s["pa"]; o0 = pa[k]
    y = np.zeros((len(td), len(HS), len(CS)), bool); yr = np.zeros((len(td), len(HS)), bool); ok = np.zeros((len(td), len(HS)), bool)
    kmax = le(T, td + max(HS))
    for n in range(len(td)):
        j0 = k[n] + 1; j1 = kmax[n]
        for h, H in enumerate(HS):
            jh = le(T, td[n] + H)
            ok[n, h] = td[n] + H <= d["end"] - 1
            if jh >= j0:
                m = np.nanmin(pa[j0:jh + 1])
                for c, cc in enumerate(CS): y[n, h, c] = m <= o0[n] - cc / 100 + 1e-9
                yr[n, h] = pa[jh] > o0[n] + 1e-9
    FX.append(F); Y.append(y); YR.append(yr); VALID.append(ok); PERX += [PER(st)] * len(td); STX += [st] * len(td)
FX = np.vstack(FX); Y = np.concatenate(Y); YR = np.concatenate(YR); VALID = np.concatenate(VALID); PERX = np.array(PERX); STX = np.array(STX)
good = np.all(np.isfinite(FX), 1)
print("décisions", len(FX), "finies", int(good.sum()), f"{_time.time() - _T0:.0f} s", flush=True)
TRN = (PERX == "apprentissage") & good
MU = FX[TRN].mean(0); SD = FX[TRN].std(0) + 1e-9
Z = lambda F: (F - MU) / SD
MOD, MODR, BASE, BASER = {}, {}, {}, {}
for h, H in enumerate(HS):
    m_ = TRN & VALID[:, h]
    for c, cc in enumerate(CS):
        yy = Y[m_, h, c]; BASE[(h, c)] = yy.mean()
        MOD[(h, c)] = LogisticRegression(C=1.0, max_iter=300).fit(Z(FX[m_]), yy) if 0 < yy.sum() < len(yy) else None
    yy = YR[m_, h]; BASER[h] = yy.mean()
    MODR[h] = LogisticRegression(C=1.0, max_iter=300).fit(Z(FX[m_]), yy)
print("modèles ajustés", f"{_time.time() - _T0:.0f} s", flush=True)

def evalue(pred, yy, base):
    n = len(yy)
    if n == 0: return dict(n=0)
    auc = roc_auc_score(yy, pred) if 0 < yy.sum() < n else float("nan")
    return dict(n=n, taux=yy.mean(), auc=auc, brier=float(np.mean((pred - yy) ** 2)), brier0=float(np.mean((base - yy) ** 2)))
EV = {}
for h, H in enumerate(HS):
    for per in PER3:
        m_ = (PERX == per) & good & VALID[:, h]
        for c, cc in enumerate(CS):
            M = MOD[(h, c)]
            pr = M.predict_proba(Z(FX[m_]))[:, 1] if M else np.full(m_.sum(), BASE[(h, c)])
            EV[(h, c, per)] = evalue(pr, Y[m_, h, c], BASE[(h, c)])
        EV[(h, "r", per)] = evalue(MODR[h].predict_proba(Z(FX[m_]))[:, 1], YR[m_, h], BASER[h])

# ---------------------------------------------------------------- 3. contrôle sous-seconde (photos 100 ms)
LEAD = collections.defaultdict(list)
for x in json.load(gzip.open("bot95/lead.json.gz", "rt")):
    ci = x["colonnes"]; iu, idn = ci.index("pm_up_ventes_top3"), ci.index("pm_down_ventes_top3")
    for l in x["lignes"]:
        u, dn = l[iu], l[idn]
        if u and dn: LEAD[x["start"]].append((l[0], u[0][0], dn[0][0]))
for st in list(LEAD):
    v = sorted(set(LEAD[st])); LEAD[st] = np.array(v)
LH = [0.25, 0.5, 1, 3, 5]
LC = {h: collections.defaultdict(list) for h in LH}
for (st, up, _), td in DEC.items():
    if st not in LEAD: continue
    L_ = LEAD[st]; lt = L_[:, 0]; lpa = L_[:, 2] if up else L_[:, 1]
    k0 = le(lt, td)
    if k0 < 0 or td - lt[k0] > 0.15 or lt[-1] < td + 0.25: continue
    d = arr(st); s = cote(d, up); T = d["T"]
    F, k = feats(d, s, np.array([td]))
    if not np.all(np.isfinite(F)): continue
    o_l = lpa[k0]; o_r = s["pa"][k[0]]
    for H in LH:
        kh = le(lt, td + H)
        if lt[-1] < td + H or np.any(np.diff(lt[k0:kh + 1]) > 0.35) or kh <= k0: continue
        jh = le(T, td + H)
        for c in (1, 2):
            yl = np.min(lpa[k0 + 1:kh + 1]) <= o_l - c / 100 + 1e-9
            yrr = (np.min(s["pa"][k[0] + 1:jh + 1]) <= o_r - c / 100 + 1e-9) if jh > k[0] else False
            h = HS.index(H); M = MOD[(h, CS.index(c))]
            pr = M.predict_proba(Z(F))[0, 1]
            LC[H][c].append((yl, yrr, pr))
        LC[H]["r"].append((lpa[kh] > o_l + 1e-9, (s["pa"][jh] > o_r + 1e-9) if jh > k[0] else False, MODR[HS.index(H)].predict_proba(Z(F))[0, 1]))
print("contrôle 100 ms", {H: len(LC[H][1]) for H in LH}, f"{_time.time() - _T0:.0f} s", flush=True)

# ---------------------------------------------------------------- 4-7. politiques de couverture
PRC = {}
def gagne(st, up): y = O[f"BTC:{st}"]["gagnant"] == "Up"; return y if up else not y
def declencheurs(p):
    st, s = p["st"], p["s"]; d = arr(st); sd = cote(d, s["up"]); T = d["T"]; out = {}
    i0 = s["i"]; f = sd["fair"]
    w = np.where((np.arange(len(T)) > i0) & (f <= s["fair"] - 0.10) & (T <= d["end"] - 2))[0]
    out["modèle −10"] = int(w[0]) if len(w) else None
    k = int(ge(T, s["t"] + 30)); out["entrée + 30 s"] = k if k < len(T) and T[k] <= d["end"] - 2 else None
    return out
def couvrir(p, k, lat, pol, H=None, kc=None, repli=None, theta=None, leger=False):
    """renvoie dict(pn=P&L de la position avec la politique, qh=parts couvertes, prix=prix payé, o_dec, rempli, partiel)
    pol : 'b' immédiat, 'c' ordre passif à o_dec − kc, 'd' attente H si P(baisse >= 1 c) > theta, 'e' vente de la moitié"""
    st, s, e = p["st"], p["s"], p["e"]; d = arr(st); sd = cote(d, s["up"]); T = d["T"]; end = d["end"]
    q = e["q"]; base = e["pn"]; w = gagne(st, s["up"]); wo = 0.0 if w else 1.0
    td = T[k]; o_dec = sd["pa"][k]; R = dict(pn=base, qh=0.0, prix=None, o_dec=o_dec, rempli=False, partiel=False, essai=True)
    def achat(j, prix=None, qmax=None):
        if j >= len(T) or T[j] >= end: return 0.0, None
        o = sd["pa"][j] if prix is None else prix; z = sd["paz"][j] if qmax is None else qmax
        qh = min(q, z)
        return (qh, o) if qh >= 1 else (0.0, None)
    if pol == "e":
        j = k if lat == 0 else int(ge(T, td + lat))
        if j >= len(T) or T[j] >= end: return R
        b = sd["ob"][j]; qs = min(q / 2, sd["obz"][j])
        if qs < 1 or not np.isfinite(b): return R
        R.update(pn=base + qs * (b - FEE(b) - (1.0 if w else 0.0)), qh=qs, prix=b, rempli=True, partiel=qs < q / 2 - 1e-6, vente=True); return R
    if pol == "b":
        j = k if lat == 0 else int(ge(T, td + lat)); qh, o = achat(j)
    elif pol == "d":
        ck = (st, s["up"], k, H)
        if ck not in PRC:
            F, _ = feats(d, sd, np.array([td])); PRC[ck] = MOD[(HS.index(H), 0)].predict_proba(Z(F))[0, 1] if np.all(np.isfinite(F)) else 0.0
        pr = PRC[ck]
        R["attente"] = pr > theta
        j = int(ge(T, td + lat + H)) if pr > theta else (k if lat == 0 else int(ge(T, td + lat)))
        qh, o = achat(j)
    elif pol == "c":
        L = round(o_dec - kc / 100, 2)
        qh = 0.0; o = None
        if L >= 0.01:
            j0 = int(le(T, td + lat)) + 1; j1 = int(le(T, min(td + lat + H, end - 1e-6)))
            for j in range(j0, j1 + 1):
                if (sd["pa"][j] <= L + 1e-9) if leger else (sd["pa"][j] <= L - 0.01 + 1e-9):
                    qh = min(q, sd["paz"][j]); o = L
                    if qh < 1: qh, o = 0.0, None; continue
                    break
        R["rempli"] = qh >= 1
        pn = base + (qh * (wo - o - FEE(o)) if qh >= 1 else 0.0)
        cost = qh * o if qh >= 1 else 0.0; fees = qh * FEE(o) if qh >= 1 else 0.0; qtot = qh
        if repli == "immédiat" and q - qh >= 1:
            j = int(ge(T, td + lat + H)); q2, o2 = achat(j)
            q2 = min(q2, q - qh)
            if q2 >= 1: pn += q2 * (wo - o2 - FEE(o2)); cost += q2 * o2; fees += q2 * FEE(o2); qtot += q2
        R.update(pn=pn, qh=qtot, prix=(cost / qtot if qtot >= 1 else None), partiel=0 < qtot < q - 1e-6, fees=fees)
        return R
    if qh >= 1:
        R.update(pn=base + qh * (wo - o - FEE(o)), qh=qh, prix=o, rempli=True, partiel=qh < q - 1e-6, fees=qh * FEE(o))
    return R

# seuil theta de la politique d : choisi sur l'apprentissage seulement (prix moyen payé, toutes positions déclenchées)
TRIG = {nom: [(p, declencheurs(p)) for p in L] for nom, L in POS.items()}
GRID = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.01]
THETA = {}
for H in HS:
    best = None
    for th in GRID:
        gains = []
        for nom in POS:
            for p, tg in TRIG[nom]:
                if p["per"] != "apprentissage": continue
                for tn, k in tg.items():
                    if k is None: continue
                    r = couvrir(p, k, 0, "d", H=H, theta=th)
                    gains.append((r["o_dec"] - r["prix"]) if r["prix"] is not None else 0.0)
        g = float(np.mean(gains))
        if best is None or g > best[1] + 1e-12: best = (th, g)
    THETA[H] = best
print("theta", THETA, f"{_time.time() - _T0:.0f} s", flush=True)

POLS = [("a", "(a) garder sans couvrir", {}), ("b", "(b) couverture immédiate", {}), ("e", "(e) vente immédiate de la moitié", {})]
POLSH = []
for kc in (1, 2, 3):
    POLSH.append((f"c{kc}i", f"(c) ordre passif −{kc} c, sinon immédiat", dict(kc=kc, repli="immédiat")))
    POLSH.append((f"c{kc}n", f"(c) ordre passif −{kc} c, sinon rien", dict(kc=kc, repli="rien")))
POLSH.append(("d", "(d) attente si P(baisse ≥ 1 c) > seuil", {}))
def run(code, kw, H, lat, trig, leger=False):
    """une ligne de résultat par position (TOUTES les positions de chaque stratégie, déclenchées ou non)"""
    out = []
    for nom in POS:
        for p, tg in TRIG[nom]:
            k = tg[trig]; base = p["e"]["pn"]
            if k is None or code == "a": out.append(dict(nom=nom, st=p["st"], per=p["per"], pn=base, base=base, mise=p["e"]["mise"], trig=False, r=None, p=p)); continue
            if code == "b": r = couvrir(p, k, lat, "b")
            elif code == "e": r = couvrir(p, k, lat, "e")
            elif code == "d": r = couvrir(p, k, lat, "d", H=H, theta=THETA[H][0])
            else: r = couvrir(p, k, lat, "c", H=H, leger=leger, **kw)
            out.append(dict(nom=nom, st=p["st"], per=p["per"], pn=r["pn"], base=base, mise=p["e"]["mise"], trig=True, r=r, p=p))
    return out
def stats(rows, per):
    R_ = sorted([x for x in rows if x["per"] == per], key=lambda x: x["st"])
    ex = np.array([x["pn"] - x["base"] for x in R_]); pn = np.array([x["pn"] for x in R_])
    tr = [x for x in R_ if x["trig"]]; fil = [x for x in tr if x["r"]["qh"] >= 1]
    drop = [100 * (x["r"]["o_dec"] - x["r"]["prix"]) for x in fil if x["r"]["prix"] is not None and not x["r"].get("vente")]
    cum = np.cumsum(pn); dd = float(min(0.0, np.min(cum - np.maximum.accumulate(np.concatenate([[0], cum]))[1:]))) if len(pn) else 0.0
    H_ = collections.defaultdict(float)
    for st in CYC[per]: H_[st // 3600] += 0.0
    for x in R_: H_[x["st"] // 3600] += x["pn"] - x["base"]
    hv = np.array(list(H_.values())); sims = hv[RNG.integers(0, len(hv), (2000, len(hv)))].sum(1); lo, hi = np.percentile(sims, [5, 95])
    sac = sum(max(0.0, x["base"] - x["pn"]) for x in R_ if x["base"] > 0)
    jk = sum(1 for x in R_ if x["base"] >= 4 * x["mise"] and x["pn"] < 4 * x["mise"])
    prot = sum(x["pn"] - x["base"] for x in R_ if x["base"] < 0)
    return dict(n=len(R_), ntr=len(tr), nfil=len(fil), npart=sum(1 for x in fil if x["r"]["partiel"]), drop=(float(np.mean(drop)) if drop else float("nan")),
                ex=float(ex.sum()), sans5=float(ex.sum() - np.sort(ex)[::-1][:5].sum()) if len(ex) else 0.0, lo=lo, hi=hi, dd=dd, sac=sac, jk=jk, prot=prot,
                pn=float(pn.sum()), att=sum(1 for x in tr if x["r"].get("attente")))
RES = {}
for trig in ("modèle −10", "entrée + 30 s"):
    for lat in (0, 0.3):
        for code, lab, kw in POLS: RES[(trig, lat, code, None)] = run(code, kw, None, lat, trig)
        for H in HS:
            for code, lab, kw in POLSH: RES[(trig, lat, code, H)] = run(code, kw, H, lat, trig)
    print("politiques", trig, f"{_time.time() - _T0:.0f} s", flush=True)
LEG = {H: run("c1i", dict(kc=1, repli="immédiat"), H, 0, "modèle −10", leger=True) for H in HS}

# ---------------------------------------------------------------- rédaction
ENTETE = ENTETE.replace("seulement (après", "(après").replace(" — le test est minuscule, aucun verdict ne peut s'y appuyer seul.", f" — environ {len(CYC['inédit']) * 5 / 60:.0f} h de marché, plus court que la validation.")
out = ["# HEDGE PRICE PREDICTOR — peut-on acheter le côté opposé moins cher dans les secondes qui suivent ?", "",
       f"Étude hors ligne du {_time.strftime('%d.%m.%Y')} — aucun bot, aucun fichier du bot modifié. " + ENTETE, ""]
VERD = len(out)
out += ["## Définitions (pré-enregistrées avant tout calcul)", "",
        "**Positions** (premier signal du cycle, achat au seul meilleur vendeur de la ligne enregistrée, quantité affichée, 50 $ max, frais 0,072·p·(1−p) par part) :", "",
        "- **désaccord 20** : premier instant où proba du modèle du bot (r[2]) − vendeur ≥ 0,20, vendeur 0,02-0,98, ≥ 5 s restantes.",
        "- **V2-F original** : écart ≥ 0,20 qui a grandi d'au moins 3 c en 3 s, vendeur 0,03-0,97 (définition O8 inchangée).",
        "- **désaccord 30** : premier écart ≥ 0,30, vendeur 0,02-0,98.",
        "- **V1 (0,55-0,56)** : copie de la règle V1 du bot (bot95/src/index.js, `v1Eval`) : meilleur vendeur entre 0,55 et 0,56, modèle de notre côté ≥ 0,63 (PMIN + MARGE), "
        "élan du perp Bybit sur 5 s dans notre sens. Différence : le bot exige 50 $ remplis jusqu'à 0,56 sur plusieurs niveaux ; ici seul le meilleur niveau est connu → quantité affichée.", "",
        "| Stratégie | Positions app. | valid. | test |", "|---|---|---|---|"]
for nom, L in POS.items():
    out.append(f"| {nom} | " + " | ".join(str(sum(1 for p in L if p["per"] == per)) for per in PER3) + " |")
out += ["", "Les quatre stratégies achètent souvent le même cycle (désaccord 20 et V2-F surtout) : elles sont traitées comme quatre portefeuilles fantômes séparés et leurs résultats sont **additionnés** dans les tableaux.", "",
        "**Déclencheurs de la couverture** (un seul moment par position) :", "",
        "- **modèle −10** : première ligne après l'entrée où la proba du modèle de notre côté est ≥ 10 points sous celle de l'entrée (comme la « sortie modèle −10 »), au moins 2 s avant la fin.",
        "- **entrée + 30 s** : première ligne à l'entrée + 30 s ou après (au moins 2 s avant la fin).",
        "- Position sans déclencheur : aucune action, résultat = garder. **Toutes les positions comptent dans tous les totaux**, déclenchées ou non.", "",
        "**Politiques**, même budget pour toutes : au plus autant de parts opposées que de parts détenues (couverture « verrouillée »), au seul meilleur vendeur, quantité affichée :", "",
        "- (a) garder sans couvrir.",
        "- (b) couverture immédiate au meilleur vendeur opposé (quantité affichée ; le reste n'est pas couvert, faute de profondeur connue).",
        "- (c) ordre passif à vendeur opposé − k c (k = 1, 2, 3), valable H secondes. **Hypothèse : nous sommes derniers dans la file d'attente** ; l'ordre n'est rempli que si le "
        "meilleur vendeur enregistré descend **au moins 1 c sous notre prix** (≤ limite − 0,01) sur une ligne, pour la quantité affichée de cette ligne. "
        "Les frais preneur sont comptés aussi sur l'ordre passif (prudent : Polymarket ne fait pas payer le teneur d'ordre). Non rempli → deux variantes : achat immédiat au vendeur à la fin de l'attente, ou rien.",
        "- (d) attente prédictive : si le modèle « baisse ≥ 1 c dans H » donne une probabilité > seuil, on attend H puis on achète au meilleur vendeur du moment (même s'il a monté) ; sinon achat immédiat. "
        "Seuil choisi sur l'apprentissage seulement (celui qui maximise la baisse moyenne obtenue sur toutes les positions déclenchées).",
        "- (e) vente immédiate de la moitié de la position au meilleur acheteur de notre côté (quantité affichée), frais compris.",
        "- Délai d'exécution : 0 s (principal) et 0,3 s (variante : l'ordre part sur la première ligne ≥ décision + 0,3 s).", "",
        "**Remarque de structure importante** : sur Polymarket, le carnet Down est le miroir du carnet Up (vendeur Down = 1 − acheteur Up : vérifié, les colonnes manquantes coïncident exactement). "
        "Acheter le côté opposé au prix o revient donc à revendre notre côté à 1 − o, frais identiques (0,072·p·(1−p) est symétrique). "
        "La « couverture immédiate » (b) a le même effet économique qu'une **vente** de la position au meilleur acheteur — mais elle immobilise du capital jusqu'au règlement.", ""]

# --- 1. ce qu'on observe
out += ["## 1. Ce que montre le carnet opposé après une entrée (taux bruts)", "",
        f"{len(FX)} instants de décision (une par seconde après chaque entrée, jusqu'à la fin du cycle ; dédoublonnés quand deux stratégies tiennent le même côté du même cycle à la même seconde). "
        "Seul le **meilleur niveau** du carnet est enregistré (prix + taille) : la profondeur au-delà n'existe pas dans les lignes.", ""]
for per in PER3:
    m_ = (PERX == per) & good
    out.append(f"- {per} : {int(m_.sum())} décisions · vendeur opposé médian {f2(np.median(FX[m_, 1]))} · taille affichée médiane {np.median(np.expm1(FX[m_, 2])):.0f} parts "
               f"(10 % des cas < {np.percentile(np.expm1(FX[m_, 2]), 10):.0f} parts)")
out += ["", "Fréquence observée (apprentissage + validation + test) de « le meilleur vendeur opposé descend d'au moins X c dans les H secondes » et « il est plus cher au bout de H » :", "",
        "| Horizon | n | ≥ 1 c | ≥ 2 c | ≥ 3 c | ≥ 5 c | ≥ 10 c | plus cher à H |", "|---|---|---|---|---|---|---|---|"]
for h, H in enumerate(HS):
    m_ = good & VALID[:, h]
    out.append(f"| {fH(H)} | {int(m_.sum())} | " + " | ".join(pc(Y[m_, h, c].mean()) for c in range(len(CS))) + f" | {pc(YR[m_, h].mean())} |")
out += ["", "Les lignes arrivent toutes les ~0,3 s : l'horizon 0,25 s contient 0 ou 1 nouvelle ligne (fenêtre sans ligne = « pas de baisse observée »), l'horizon 0,5 s une ou deux. "
        "Ces deux horizons ne sont mesurés qu'**approximativement** ; voir le contrôle à 100 ms (section 3).", ""]

# --- 2. modèles
def tab_ev(hs_, titre):
    o = [f"### {titre}", "", "| Horizon | Cible | Taux app. | Valid. : n · taux · AUC · Brier modèle / naïf | Test : n · taux · AUC · Brier modèle / naïf |", "|---|---|---|---|---|"]
    for H in hs_:
        h = HS.index(H)
        for c in list(range(len(CS))) + ["r"]:
            lab = f"baisse ≥ {CS[c]} c" if c != "r" else "plus cher à H"
            b0 = BASE[(h, c)] if c != "r" else BASER[h]
            cel = []
            for per in ("validation", "inédit"):
                e = EV[(h, c, per)]
                cel.append(f"{e['n']} · {pc(e['taux'])} · {f2(e['auc'])} · {f3(e['brier'])} / {f3(e['brier0'])}" if e["n"] else "—")
            o.append(f"| {fH(H)} | {lab} | {pc(b0)} | " + " | ".join(cel) + " |")
    return o + [""]
out += ["## 2. Prédire la baisse du côté opposé — régression logistique figée sur l'apprentissage", "",
        "Une régression logistique par horizon et par seuil (30 modèles) + une par horizon pour « plus cher à H » (6), ajustées sur l'apprentissage SEULEMENT, variables centrées-réduites sur l'apprentissage, "
        "aucune variable choisie après coup. 19 variables, toutes connues à la décision (lignes d'horodatage ≤ instant de décision) : " + ", ".join(FNOMS) + ". "
        "Mouvements des bourses comptés positivement quand ils vont dans notre sens (donc vers un côté opposé moins cher).", "",
        "« Brier naïf » = prédire toujours le taux de l'apprentissage. Le modèle n'apporte quelque chose que si son Brier est **plus bas** que le naïf et son AUC nettement > 0,5. "
        "Les instants d'une même position se suivent seconde par seconde : ils ne sont pas indépendants, les AUC sont donc plus précises en apparence qu'en réalité.", ""]
out += tab_ev([0.25, 0.5], "Horizons < 1 s (mesure approximative, cadence 0,3 s)")
out += tab_ev([1, 3, 5, 10], "Horizons 1-10 s")
ACT = (FX[:, 1] >= 0.10) & (FX[:, 1] <= 0.90) & (FX[:, 0] > 30)
out += ["### Le modèle sur les seuls moments « vivants »", "",
        "Une grande partie des décisions tombe dans des carnets morts (côté opposé à 0,95-0,99 ou presque plus de temps) où rien ne bouge : facile à prédire, mais inutile pour couvrir. "
        "Même évaluation limitée aux instants où le vendeur opposé est entre 0,10 et 0,90 et où il reste plus de 30 s :", "",
        "| Horizon | Valid. : n · taux baisse ≥ 1 c · AUC · Brier modèle / naïf | Test : n · taux · AUC · Brier modèle / naïf |", "|---|---|---|"]
for h, H in enumerate(HS):
    cel = []
    for per in ("validation", "inédit"):
        m_ = (PERX == per) & good & VALID[:, h] & ACT
        e = evalue(MOD[(h, 0)].predict_proba(Z(FX[m_]))[:, 1], Y[m_, h, 0], BASE[(h, 0)])
        EV[(h, "act", per)] = e
        cel.append(f"{e['n']} · {pc(e['taux'])} · {f2(e['auc'])} · {f3(e['brier'])} / {f3(e['brier0'])}")
    out.append(f"| {fH(H)} | " + " | ".join(cel) + " |")
out += ["", "Attention : le Brier « naïf » de ce tableau reste le taux global de l'apprentissage (plus bas que le taux de ces moments vivants), ce qui avantage le modèle ; l'AUC est la mesure à lire ici.", ""]
out += ["### Calibration sur la validation (baisse ≥ 1 c)", ""]
for H in (1, 3, 10):
    h = HS.index(H); m_ = (PERX == "validation") & good & VALID[:, h]
    pr = MOD[(h, 0)].predict_proba(Z(FX[m_]))[:, 1]; yy = Y[m_, h, 0]
    qs = np.unique(np.percentile(pr, np.linspace(0, 100, 11)))
    out += [f"Horizon {fH(H)} :", "", "| Prédit (tranche) | n | Prédit moyen | Observé |", "|---|---|---|---|"]
    b = np.clip(np.searchsorted(qs, pr, "right") - 1, 0, len(qs) - 2)
    for j in range(len(qs) - 1):
        w = b == j
        if w.sum(): out.append(f"| {f2(qs[j])}-{f2(qs[j + 1])} | {int(w.sum())} | {pc(pr[w].mean())} | {pc(yy[w].mean())} |")
    out.append("")
M3 = MOD[(HS.index(3), 0)]
co = sorted(zip(FNOMS, M3.coef_[0]), key=lambda x: -abs(x[1]))
out += ["Poids du modèle « baisse ≥ 1 c en 3 s » (variables centrées-réduites, les 8 plus forts) : " + " ; ".join(f"{n} {f2(c)}" for n, c in co[:8]) + ".", ""]

# --- 3. contrôle 100 ms
out += ["## 3. Contrôle sous-seconde avec les photos 100 ms (lead.json.gz)", "",
        "Sous-ensemble : instants de décision qui tombent dans une photo (≈ 10 s avant → 10 s après le premier désaccord ≥ 0,20 vu par le bot en direct), fenêtre entièrement couverte. "
        "Même instant de décision, même côté opposé ; la cible est mesurée deux fois : sur les lignes 0,3 s et sur les photos 100 ms. Les prédictions viennent des modèles ajustés sur les lignes 0,3 s.", "",
        "| Horizon | Cible | n | Taux mesuré 0,3 s | Taux mesuré 100 ms | Accord des deux mesures | AUC du modèle (cible 0,3 s) | AUC du modèle (cible 100 ms) |", "|---|---|---|---|---|---|---|---|"]
for H in LH:
    for c in (1, 2, "r"):
        v = LC[H][c]
        if not v: continue
        yl = np.array([x[0] for x in v]); yr_ = np.array([x[1] for x in v]); pr = np.array([x[2] for x in v])
        au = lambda yy: f2(roc_auc_score(yy, pr)) if 0 < yy.sum() < len(yy) else "—"
        out.append(f"| {fH(H)} | {'baisse ≥ %d c' % c if c != 'r' else 'plus cher à H'} | {len(v)} | {pc(yr_.mean())} | {pc(yl.mean())} | {pc(np.mean(yl == yr_))} | {au(yr_)} | {au(yl)} |")
out += ["", "Toutes périodes confondues (les photos ne couvrent que ~20 s par cycle, autour du premier désaccord). Les horodatages restent l'heure de réception par le bot.", ""]

# --- 4-5. politiques
def ligne(lab, R, H=None):
    cel = []
    for per in ("validation", "inédit"):
        s = stats(R, per)
        fr = (f"{s['nfil']}/{s['ntr']}" + (f" ({pc(s['nfil'] / s['ntr'])})" if s["ntr"] else "") + (f" · attend {s['att']}" if s["att"] else ""))
        cel.append(f"{'—' if s['drop'] != s['drop'] else f2(s['drop'])} | {fr} | **{f0(s['ex'])}** [{f0(s['lo'])} ; {f0(s['hi'])}] | {f0(s['sans5'])} | {f0(s['dd'])} | {f0(s['sac'])} ({s['jk']})")
    return f"| {fH(H) if H else 'tous'} | {lab} | " + " | ".join(cel) + " |"
HDR2 = ("| Horizon | Politique | Valid. : baisse captée (c) | remplis / déclenchés | P&L net en plus vs garder [IC 90 %] | sans top 5 | creux max (portefeuille) | gains sacrifiés (jackpots perdus) "
        "| Test : baisse captée (c) | remplis / déclenchés | P&L en plus vs garder [IC 90 %] | sans top 5 | creux max | gains sacrifiés (jackpots) |\n|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
def bloc(trig, lat):
    o = [HDR2]
    for code, lab, kw in POLS: o.append(ligne(lab, RES[(trig, lat, code, None)]))
    for H in HS:
        for code, lab, kw in POLSH:
            o.append(ligne(lab + (f" (seuil {f2(THETA[H][0])})" if code == "d" else ""), RES[(trig, lat, code, H)], H))
    return o
ref = {per: stats(RES[("modèle −10", 0, "a", None)], per) for per in PER3}
out += ["## 4. Politiques de couverture — TABLEAU FINAL", "",
        "Lecture : **baisse captée** = vendeur opposé au moment de la décision − prix réellement payé (moyenne des couvertures exécutées, en cents ; négatif = payé plus cher). "
        "**P&L en plus** = somme sur TOUTES les positions de (résultat avec la politique − résultat en gardant), frais compris ; IC 90 % par bootstrap de blocs d'une heure. "
        "**sans top 5** = même somme sans les 5 positions où la politique a le plus rapporté. **creux max** = plus forte baisse du portefeuille (positions + couvertures) dans l'ordre chronologique. "
        "**gains sacrifiés** = ce que la couverture a coûté sur les positions qui auraient gagné ; entre parenthèses, nombre de jackpots (gain ≥ 4× la mise) perdus.", "",
        "Référence « garder » (4 stratégies additionnées) : " + " · ".join(f"{per} {ref[per]['n']} positions, {f0(ref[per]['pn'])}, creux {f0(ref[per]['dd'])}" for per in PER3) + ".", ""]
for trig in ("modèle −10", "entrée + 30 s"):
    nt = {per: stats(RES[(trig, 0, "b", None)], per)["ntr"] for per in PER3}
    out += [f"### Déclencheur « {trig} » — délai 0 s", "", "Positions déclenchées : " + " · ".join(f"{per} {nt[per]}/{ref[per]['n']}" for per in PER3) + ".", ""] + bloc(trig, 0) + [""]
for trig in ("modèle −10", "entrée + 30 s"):
    out += [f"### Déclencheur « {trig} » — délai d'exécution 0,3 s", ""] + bloc(trig, 0.3) + [""]
def vs_b(R, Rb, per):
    P_ = [(x, y) for x, y in zip(R, Rb) if x["per"] == per]
    H_ = collections.defaultdict(float)
    for st in CYC[per]: H_[st // 3600] += 0.0
    for x, y in P_: H_[x["st"] // 3600] += x["pn"] - y["pn"]
    hv = np.array(list(H_.values())); sims = hv[RNG.integers(0, len(hv), (2000, len(hv)))].sum(1); lo, hi = np.percentile(sims, [5, 95])
    dp = [100 * (y["r"]["prix"] - x["r"]["prix"]) for x, y in P_ if x["trig"] and x["r"]["prix"] is not None and y["r"]["prix"] is not None]
    eff = 0.0
    for x, y in P_:
        if x["trig"] and x["r"]["prix"] is not None and y["r"]["prix"] is not None:
            fx = x["r"]["fees"] / x["r"]["qh"]; fy = y["r"]["fees"] / y["r"]["qh"]
            eff += min(x["r"]["qh"], y["r"]["qh"]) * ((y["r"]["prix"] + fy) - (x["r"]["prix"] + fx))
    return sum(x["pn"] - y["pn"] for x, y in P_), lo, hi, (float(np.mean(dp)) if dp else float("nan")), len(dp), (float(np.mean(np.array(dp) > 0)) if dp else float("nan")), eff
VSB = {}
out += ["### Attendre plutôt que couvrir tout de suite : gain par rapport à (b) immédiat", "",
        "Comparaison directe sur les MÊMES positions et le même moment de déclenchement : la seule différence est l'attente. "
        "« Prix payé en moins » = prix de (b) − prix payé par la politique (moyenne, en cents, sur les positions couvertes par les deux ; positif = moins cher). "
        "Les ordres non remplis sont achetés au vendeur de la fin de l'attente (variantes « sinon immédiat » seulement : les variantes « sinon rien » ne couvrent presque pas et ne sont pas comparables).", "",
        "« dont effet prix » = la part de Δ P&L due au seul prix payé (frais compris) sur les parts couvertes par les deux ; le reste vient de positions couvertes par l'une et pas l'autre "
        "(fin du cycle atteinte pendant l'attente, quantité affichée différente) — c'est-à-dire du hasard du résultat des positions laissées ouvertes, pas d'un achat moins cher.", "",
        "| Déclencheur | Délai | Horizon | Politique | Valid. : prix payé en moins (c) · % moins cher · n | Δ P&L vs (b) [IC 90 %] | dont effet prix | Test : prix payé en moins (c) · % moins cher · n | Δ P&L vs (b) [IC 90 %] | dont effet prix |", "|---|---|---|---|---|---|---|---|---|---|"]
for trig in ("modèle −10", "entrée + 30 s"):
    for lat in (0, 0.3):
        Rb = RES[(trig, lat, "b", None)]
        for H in HS:
            for code in ("c1i", "c2i", "c3i", "d"):
                cel = []
                for per in ("validation", "inédit"):
                    v = vs_b(RES[(trig, lat, code, H)], Rb, per); VSB[(trig, lat, code, H, per)] = v
                    cel.append(f"{f2(v[3])} · {pc(v[5]) if v[5] == v[5] else '—'} · {v[4]} | **{f0(v[0])}** [{f0(v[1])} ; {f0(v[2])}] | {f0(v[6])}")
                lab = {"c1i": "(c) −1 c", "c2i": "(c) −2 c", "c3i": "(c) −3 c", "d": f"(d) seuil {f2(THETA[H][0])}"}[code]
                out.append(f"| {trig} | {fH(lat)} | {fH(H)} | {lab} | " + " | ".join(cel) + " |")
out.append("")
out += ["### Sensibilité : règle de remplissage moins prudente (ordre −1 c, sinon immédiat, déclencheur modèle −10, délai 0)", "",
        "Rempli dès que le meilleur vendeur enregistré touche notre prix (≤ limite) au lieu de passer 1 c dessous. C'est optimiste : il suppose que nous sommes servis dès que le prix touche, malgré la file d'attente.", "", HDR2]
for H in HS: out.append(ligne("(c) −1 c, sinon immédiat — remplissage optimiste", LEG[H], H))
out.append("")
# par stratégie (validation) — politiques sans horizon et meilleures variantes
out += ["### Par stratégie — validation, délai 0 (P&L en plus vs garder)", "", "| Stratégie | Déclencheur | Garder | (b) immédiat | (e) vendre la moitié | (c) −1 c 3 s sinon immédiat | (d) prédictif 3 s |", "|---|---|---|---|---|---|---|"]
for nom in POS:
    for trig in ("modèle −10", "entrée + 30 s"):
        g = lambda R: sum(x["pn"] - x["base"] for x in R if x["nom"] == nom and x["per"] == "validation")
        base = sum(x["base"] for x in RES[(trig, 0, "a", None)] if x["nom"] == nom and x["per"] == "validation")
        out.append(f"| {nom} | {trig} | {f0(base)} | {f0(g(RES[(trig, 0, 'b', None)]))} | {f0(g(RES[(trig, 0, 'e', None)]))} | {f0(g(RES[(trig, 0, 'c1i', 3)]))} | {f0(g(RES[(trig, 0, 'd', 3)]))} |")
out.append("")

# --- 6. coût Up + Down
out += ["## 5. Coût total Up + Down des paires couvertes et profits verrouillés", "",
        "Coût de la paire = prix d'entrée + prix payé pour le côté opposé (par part). Si < 1, la paire rapporte à coup sûr parts × (1 − coût) − frais des deux jambes ; si > 1 elle perd à coup sûr. "
        "Toutes stratégies additionnées, délai 0.", "",
        "| Déclencheur | Politique | Période | Paires | Coût 10 % | médiane | 90 % | Paires < 1 | Profit verrouillé (paires < 1) | Perte verrouillée (paires > 1) | Net verrouillé |", "|---|---|---|---|---|---|---|---|---|---|---|"]
for trig in ("modèle −10", "entrée + 30 s"):
    for code, H, lab in (("b", None, "(b) immédiat"), ("c1i", 3, "(c) −1 c 3 s, sinon immédiat"), ("c3i", 10, "(c) −3 c 10 s, sinon immédiat"), ("d", 3, "(d) prédictif 3 s")):
        R = RES[(trig, 0, code, H)]
        for per in PER3:
            P_ = []
            for x in R:
                if x["per"] != per or not x["trig"] or x["r"]["qh"] < 1 or x["r"]["prix"] is None: continue
                p = x["p"]
                a = p["e"]["a"]; cost = a + x["r"]["prix"]; qh = x["r"]["qh"]
                P_.append((cost, qh * (1 - cost) - qh * FEE(a) - x["r"].get("fees", qh * FEE(x["r"]["prix"]))))
            if not P_: out.append(f"| {trig} | {lab} | {per} | 0 | — | — | — | — | — | — | — |"); continue
            c_ = np.array([u[0] for u in P_]); l_ = np.array([u[1] for u in P_])
            out.append(f"| {trig} | {lab} | {per} | {len(P_)} | {f2(np.percentile(c_, 10))} | {f2(np.median(c_))} | {f2(np.percentile(c_, 90))} | {int((c_ < 1).sum())} ({pc((c_ < 1).mean())}) | "
                       f"{f0(l_[c_ < 1].sum())} | {f0(l_[c_ > 1].sum())} | **{f0(l_.sum())}** |")
out.append("")
out += ["Ce tableau ne compte que la partie couverte ; la partie non couverte (quantité affichée insuffisante) reste exposée et figure dans le P&L de la section 4.", ""]

# --- verdict (calculé, placé en tête)
def ex(trig, code, H, per, lat=0): return stats(RES[(trig, lat, code, H)], per)
e3 = EV[(HS.index(3), 0, "validation")]; e1 = EV[(HS.index(1), 0, "validation")]
a1 = EV[(HS.index(1), "act", "validation")]; a3 = EV[(HS.index(3), "act", "validation")]
lv = LC[1][1]; lauc = roc_auc_score([x[0] for x in lv], [x[2] for x in lv]) if lv else float("nan")
gagnants = [(k, v) for k, v in VSB.items() if k[4] == "validation" and v[1] > 0]
confirmes = [(k, v) for k, v in gagnants if VSB[k[:4] + ("inédit",)][0] > 0]
perdants = [(k, v) for k, v in VSB.items() if k[4] == "validation" and v[2] < 0]
dpv = [v[3] for k, v in VSB.items() if k[4] == "validation" and k[0] == "modèle −10" and k[1] == 0]
lat_b = {t: stats(RES[(t, 0.3, "b", None)], "validation")["drop"] for t in ("modèle −10", "entrée + 30 s")}
def nomk(k): return f"{k[0]}, délai {fH(k[1])}, {fH(k[3])}, " + {"c1i": "ordre −1 c", "c2i": "ordre −2 c", "c3i": "ordre −3 c", "d": "attente prédictive"}[k[2]]
V = ["## Verdict (honnête, en tête)", ""]
V.append(f"- **Prévisibilité : faible là où elle servirait.** Sur toutes les décisions, le modèle logistique (figé sur l'apprentissage) fait mieux que le taux naïf : "
         f"baisse ≥ 1 c en 1 s, AUC {f2(e1['auc'])} (Brier {f3(e1['brier'])} contre {f3(e1['brier0'])}) ; en 3 s, AUC {f2(e3['auc'])}. "
         f"Mais cet avantage vient surtout des carnets « morts » (rien ne bouge) : limité aux moments vivants (vendeur opposé 0,10-0,90, > 30 s restantes) l'AUC tombe à {f2(a1['auc'])} (1 s) et {f2(a3['auc'])} (3 s), "
         f"et sur les photos 100 ms autour des désaccords à {f2(lauc)} (1 s, {len(lv)} décisions). La probabilité est mal calibrée aux extrêmes (voir section 2).")
sg_ex = sum(v[0] for k, v in gagnants); sg_eff = sum(v[6] for k, v in gagnants)
pc_ok = [(k, v) for k, v in gagnants if v[6] > 100 and v[3] > 0 and VSB[k[:4] + ("inédit",)][6] > 0]
V.append(f"- **Attendre pour acheter l'opposé moins cher ne paie pas.** Après le déclencheur « modèle −10 », toutes les variantes d'attente (ordres −1/−2/−3 c sinon immédiat, attente prédictive ; 0,25 à 10 s) "
         f"paient en moyenne entre {f2(min(dpv))} et {f2(max(dpv))} c de moins que l'achat immédiat (négatif = plus cher) sur la validation : le côté opposé a tendance à **monter** juste après ce déclencheur. "
         f"Sur les {sum(1 for k in VSB if k[4] == 'validation')} combinaisons testées contre (b), {len(gagnants)} ont un Δ P&L dont l'IC 90 % validation est entièrement positif "
         f"({len(confirmes)} restent positives sur le test) ; mais le prix payé n'explique que {f0(sg_eff)} sur {f0(sg_ex)} de ces gains : le reste vient de positions **laissées non couvertes** "
         f"(cycle terminé pendant l'attente, quantités différentes) qui ont ensuite gagné — du hasard de résultat, pas un achat moins cher. {len(perdants)} combinaisons sont entièrement négatives.")
if pc_ok:
    V.append("- **Seule piste où le prix payé est meilleur en validation (> 100 $ d'effet prix) et pas pire sur le test** : " + " ; ".join(
        f"{nomk(k)} — validation {f2(v[3])} c par paire (effet prix {f0(v[6])}), test {f2(VSB[k[:4] + ('inédit',)][3])} c (effet prix {f0(VSB[k[:4] + ('inédit',)][6])})" for k, v in pc_ok)
        + ". Quelques dixièmes de cent par paire au mieux ; sur le test l'effet prix pondéré par les parts reste un peu positif mais la moyenne par paire est négative : signal trop faible et non confirmé, à revoir seulement avec des données plus fines.")
V.append(f"- **Le délai d'exécution coûte** : avec 0,3 s de retard, la couverture immédiate paie en moyenne {f2(-lat_b['modèle −10'])} c de plus que le prix vu au déclencheur « modèle −10 » "
         f"(validation : le prix monte juste après ce déclencheur), contre {f2(-lat_b['entrée + 30 s'])} c au déclencheur « entrée + 30 s » (moment neutre).")
for t in ("modèle −10", "entrée + 30 s"):
    bv_, ev_, bt_ = ex(t, "b", None, "validation"), ex(t, "e", None, "validation"), ex(t, "b", None, "inédit")
    V.append(f"- **Couvrir contre garder ({t})** : couverture immédiate {f0(bv_['ex'])} sur la validation [IC 90 % {f0(bv_['lo'])} ; {f0(bv_['hi'])}], "
             f"{f0(bt_['ex'])} sur le test ; {bv_['jk']} jackpots (≥ 4× la mise) sacrifiés sur la validation, gains sacrifiés {f0(bv_['sac'])}. "
             f"Vendre la moitié : {f0(ev_['ex'])} [{f0(ev_['lo'])} ; {f0(ev_['hi'])}]. Rien de démontré : la couverture change la forme du risque, pas l'espérance.")
PCV = {}
for t in ("modèle −10", "entrée + 30 s"):
    c_ = [x["p"]["e"]["a"] + x["r"]["prix"] for x in RES[(t, 0, "b", None)] if x["per"] == "validation" and x["trig"] and x["r"]["qh"] >= 1]
    PCV[t] = (len(c_), float(np.median(c_)), float(np.mean(np.array(c_) < 1)))
V.append(f"- **Coût Up + Down** : une paire couverte coûte en médiane {f2(PCV['modèle −10'][1])} au déclencheur « modèle −10 » (seulement {pc(PCV['modèle −10'][2])} des {PCV['modèle −10'][0]} paires < 1) "
         f"et {f2(PCV['entrée + 30 s'][1])} à « entrée + 30 s » ({pc(PCV['entrée + 30 s'][2])} des {PCV['entrée + 30 s'][0]} paires < 1) : on « verrouille » surtout des pertes (section 5).")
V.append("- **Conclusion** : avec les données actuelles (meilleur niveau seulement, 0,3 s), il n'existe pas de prédicteur de prix de couverture exploitable ; "
         "la règle la plus simple — couvrir tout de suite, ou ne pas couvrir — n'est battue par aucune attente de façon confirmée. Ce que le VPS de Dublin devrait enregistrer pour trancher est en section 6.")
V.append("")
out[VERD:VERD] = V

# --- limites
out += ["## 6. Ce qui ne peut pas être mesuré avec les données actuelles", "",
        "- **Profondeur du carnet opposé** : seuls le meilleur prix et sa taille sont enregistrés (r[6]/r[10] ou r[4]/r[8]). Impossible de savoir à quel prix moyen on couvrirait 80-100 parts quand le meilleur niveau n'en affiche que 20.",
        "- **File d'attente et transactions réelles** : aucune transaction Polymarket (prix, taille, côté) ni position dans la file ; le remplissage d'un ordre passif est donc déduit du seul meilleur vendeur — d'où la règle prudente « 1 c dessous ».",
        "- **Sous-seconde** : cadence réelle 0,3 s ; les horizons 0,25 s et 0,5 s sont approximatifs. Les photos 100 ms ne couvrent que ~20 s autour du premier désaccord de chaque cycle.",
        "- **Heure des événements** : toutes les lignes sont horodatées à la réception par le bot ; la latence propre à chaque source n'est pas séparable.",
        "- **Notre propre impact** : un achat de couverture retire la liquidité affichée ; le rejeu suppose qu'elle était toute disponible pour nous.",
        "- **Frais teneur d'ordre** : comptés comme frais preneur (prudent).", "",
        "### Ce que le programme du VPS de Dublin (bot95/rapide/rapide.js) devrait enregistrer en direct", "",
        "1. Après chaque position ouverte (réelle ou fantôme) : **le carnet complet du côté opposé** (tous les niveaux vendeurs et acheteurs, prix + taille) **toutes les 50 ms** jusqu'à la fin du cycle, horodaté à la réception ET avec l'horodatage du message Polymarket.",
        "2. **Toutes les transactions** Polymarket des deux jetons du cycle (prix, taille, côté preneur, horodatage du serveur) — indispensable pour savoir si un ordre passif aurait été servi.",
        "3. Les **événements du carnet** (ajout / retrait / modification à chaque niveau) pour reconstruire la file d'attente à notre prix.",
        "4. Pour un vrai test : un **ordre passif fantôme** posé en direct (1 part, côté opposé, vendeur − 1 c) et son sort réel (rempli / quand / combien), plus le temps aller-retour de nos ordres.",
        "5. Les mêmes 5 prix de bourses au même rythme 50 ms pendant ces fenêtres (pour les variables de décision).", "",
        f"Durée de calcul : {_time.time() - _T0:.0f} s."]
open("etude/bot5min/resultat_hedge_predictor.md", "w").write("\n".join(out))
print("\n".join(out[:40]))
print(f"fini en {_time.time() - _T0:.0f} s")
