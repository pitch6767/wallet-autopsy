"""BOT95 HEDGE LAB V1 — socle de données (hors ligne, aucune modification du bot).
Charge v3_commun (lignes 0,3 s, règlements, modèle reconstruit), construit les tableaux numpy par cycle, le modèle corrigé
reconstruit à 0,015 % (sdRel = 1.5e-4, méthode X d'attribution_001), les trois cohortes d'entrée A / B / C, les photos 100 ms
(lead.json.gz) et le flux agrégé 1 s (sig_BTC). Usage : exec(open("etude/bot5min/hedge_lab_commun.py").read())"""
import time as _time
_T0 = _time.time()
exec(open("etude/bot5min/v3_commun.py").read())
import warnings
warnings.filterwarnings("ignore")
from statistics import NormalDist
_ND = NormalDist()
SD15 = 1.5e-4

# ---------------------------------------------------------------- tableaux numpy par cycle (lignes filtrées par meta_router : modèle + 4 prix présents)
A_ = {}
def arr(st):
    if st in A_: return A_[st]
    R_ = C[st]
    T = np.array([r[0] for r in R_], float)
    g = lambda c: np.array([(r[c] if r[c] is not None else np.nan) for r in R_], float)
    X = np.stack([g(c) for c in (11, 12, 13, 14, 15)], 1)
    for j in range(X.shape[1]):                       # report de la dernière valeur connue (jamais de valeur future)
        col = X[:, j]; m = np.isnan(col)
        if m.any() and not m.all():
            idx = np.where(~m, np.arange(len(col)), 0); np.maximum.accumulate(idx, out=idx); col[:] = col[idx]
    # modèle corrigé reconstruit 0,015 % (X15) et moteur du bot ramené à 0,015 % (H15, = calcul du fantôme réel « corrigé »)
    P15 = np.full(len(R_), np.nan); H15 = np.full(len(R_), np.nan)
    for i, r in enumerate(R_):
        x = parts_r(r, st)
        if x:
            dd, v, S = x
            P15[i] = phi(dd / math.sqrt(v + (SD15 * S) ** 2))
            if r[2] is not None:
                z8 = _ND.inv_cdf(min(0.9999, max(0.0001, r[2])))
                H15[i] = phi(z8 * math.sqrt(v + (8e-4 * S) ** 2) / math.sqrt(v + (SD15 * S) ** 2))
    d = dict(T=T, P=g(2), P15=P15, H15=H15, UB=g(3), UA=g(4), DB=g(5), DA=g(6), UBZ=np.nan_to_num(g(7)), UAZ=np.nan_to_num(g(8)),
             DBZ=np.nan_to_num(g(9)), DAZ=np.nan_to_num(g(10)), X=X, K=g(16), end=st + 300)
    A_[st] = d; return d
def cote(d, up, mod="P"):
    """vues du point de vue de la position : o* = notre côté, p* = côté opposé. Carnets miroirs : pb = 1 − oa, pbz = oaz."""
    f = d[mod] if up else 1 - d[mod]
    if up: return dict(oa=d["UA"], oaz=d["UAZ"], ob=d["UB"], obz=d["UBZ"], pa=d["DA"], paz=d["DAZ"], pb=d["DB"], pbz=d["DBZ"], fair=f, sg=1.0)
    return dict(oa=d["DA"], oaz=d["DAZ"], ob=d["DB"], obz=d["DBZ"], pa=d["UA"], paz=d["UAZ"], pb=d["UB"], pbz=d["UBZ"], fair=f, sg=-1.0)
le = lambda T, t: np.searchsorted(T, t, "right") - 1    # dernière ligne d'horodatage <= t
ge = lambda T, t: np.searchsorted(T, t, "left")         # première ligne d'horodatage >= t
for st in valides: arr(st)
print("tableaux + modèle corrigé", f"{_time.time() - _T0:.0f} s", flush=True)

# ---------------------------------------------------------------- cohortes
def gagne(st, up): y = O[f"BTC:{st}"]["gagnant"] == "Up"; return y if up else not y
COH = {"A": {}, "B": {}, "C": {}}
for st in valides:
    if (st, "Zone 30 + modèle monte") in SIG:                      # A : identique à meta_router (modèle du bot r[2])
        i, up = SIG[(st, "Zone 30 + modèle monte")]; r = C[st][i]
        COH["A"][st] = dict(i=i, t=r[0], up=up, a=r[4] if up else r[6], fair=r[2] if up else 1 - r[2], mod="P")
    if ("O8", st) in SIGV:                                           # C : V2-F original (r[2])
        s = SIGV[("O8", st)]; COH["C"][st] = dict(i=s["i"], t=s["t"], up=s["up"], a=s["a"], fair=s["fair"], mod="P")
    d = arr(st); T = d["T"]; P = d["P15"]                           # B : V2-F avec le modèle reconstruit 0,015 %
    for i in range(len(T)):
        if d["end"] - T[i] < 5: break
        j3 = int(le(T, T[i] - 3))
        if j3 < 0 or not np.isfinite(P[i]) or not np.isfinite(P[j3]): continue
        hit = None
        for up in (True, False):
            a = d["UA"][i] if up else d["DA"][i]; a3 = d["UA"][j3] if up else d["DA"][j3]
            if not (np.isfinite(a) and np.isfinite(a3)) or not (0.03 <= a <= 0.97): continue
            f0_, f3_ = (P[i], P[j3]) if up else (1 - P[i], 1 - P[j3])
            if f0_ - a >= 0.20 and (f0_ - a) - (f3_ - a3) >= 0.03: hit = (up, f0_, a); break
        if hit:
            COH["B"][st] = dict(i=i, t=T[i], up=hit[0], a=hit[2], fair=hit[1], mod="P15"); break
COHN = {"A": "A · désaccord 30 zone + modèle monte", "B": "B · V2-F corrigé 0,015 %", "C": "C · V2-F original (diagnostic)"}
print("cohortes", {k: len(v) for k, v in COH.items()}, f"{_time.time() - _T0:.0f} s", flush=True)

# ---------------------------------------------------------------- accord B ↔ fantôme réel « corrigé : V2-F ecart qui grandit »
def accord_live():
    x = json.load(open("bot95/sauvegarde/corrige_V2-F_ecart_qui_grandit_BTC.json"))
    L = {}
    for v in x["trades"].values():
        import calendar; t = calendar.timegm(time.strptime(v["heure"][:19], "%Y-%m-%dT%H:%M:%S")) + float("0." + v["heure"][20:23])
        L.setdefault(v["start"], (t, v["cote"] == "Up", v["prix"]))
    # H15 : même règle avec le moteur du bot ramené à 0,015 % (diagnostic)
    H = {}
    for st in valides:
        d = arr(st); T = d["T"]; P = d["H15"]
        for i in range(len(T)):
            if d["end"] - T[i] < 5: break
            j3 = int(le(T, T[i] - 3))
            if j3 < 0 or not np.isfinite(P[i]) or not np.isfinite(P[j3]): continue
            hit = None
            for up in (True, False):
                a = d["UA"][i] if up else d["DA"][i]; a3 = d["UA"][j3] if up else d["DA"][j3]
                if not (0.03 <= a <= 0.97): continue
                f0_, f3_ = (P[i], P[j3]) if up else (1 - P[i], 1 - P[j3])
                if f0_ - a >= 0.20 and (f0_ - a) - (f3_ - a3) >= 0.03: hit = up; break
            if hit is not None: H[st] = (T[i], hit); break
    lo, hi = min(L), max(L)
    cyc = [st for st in valides if lo <= st <= hi]
    res = {}
    for nom, S_ in (("B (reconstruit X15)", {st: (COH["B"][st]["t"], COH["B"][st]["up"]) for st in COH["B"]}), ("moteur du bot ramené à 0,015 % (H15)", H)):
        both = [st for st in cyc if st in S_ and st in L]; ss = [st for st in both if S_[st][1] == L[st][1]]
        dt = [S_[st][0] - L[st][0] for st in ss]
        res[nom] = dict(ncyc=len(cyc), nlive=sum(1 for st in cyc if st in L), nrep=sum(1 for st in cyc if st in S_), both=len(both), same=len(ss),
                        near=sum(1 for x in dt if abs(x) <= 1), med=float(np.median(dt)) if dt else float("nan"))
    return res, lo, hi
ACC, ACC_LO, ACC_HI = accord_live()
print("accord fantôme réel", ACC, flush=True)

# ---------------------------------------------------------------- photos 100 ms et flux agrégé 1 s
LEAD = {}
for x in json.load(gzip.open("bot95/lead.json.gz", "rt")):
    ci = x["colonnes"]; ix = {k: ci.index(k) for k in ("pm_up_achats_top3", "pm_up_ventes_top3", "pm_down_achats_top3", "pm_down_ventes_top3")}
    fu = [k for k in ci if k.startswith("pm_up_flux")][0]; fd = "pm_down_flux[idem]"
    for l in x["lignes"]:
        LEAD.setdefault(x["start"], {})[l[0]] = (l[ix["pm_up_ventes_top3"]], l[ix["pm_down_ventes_top3"]], l[ix["pm_up_achats_top3"]], l[ix["pm_down_achats_top3"]], l[ci.index(fu)], l[ci.index(fd)])
for st in list(LEAD):
    LEAD[st] = sorted(LEAD[st].items())
SIGF = {}            # seconde -> (up echange_achat, up echange_vente, down echange_achat, down echange_vente) en $
_sigcols = None
for f in sorted(glob.glob("bot95/donnees/*/sig_BTC.json.gz")):
    for doc in json.load(gzip.open(f, "rt")).values():
        c = doc["colonnes"]; ii = [c.index(k) for k in ("pm_up_echange_achat", "pm_up_echange_vente", "pm_down_echange_achat", "pm_down_echange_vente", "start")]
        for r in doc["lignes"]: SIGF[int(r[0])] = tuple((r[k] or 0) for k in ii)
print("photos 100 ms", len(LEAD), "· secondes de flux 1 s", len(SIGF), f"{_time.time() - _T0:.0f} s", flush=True)
