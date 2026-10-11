"""BOT95 — ALPHA EXÉCUTABLE (demande de Pitch, 11.10.2026). Hors ligne, aucune modification du bot.
Quelle part de l'avantage théorique au signal existe encore quand un ordre peut réellement être exécuté ? Tout est « mesuré à 0,3 s »
(lignes enregistrées ~0,3 s ; photos 100 ms là où elles couvrent). Les enregistrements 50 ms de Dublin n'existent pas encore.
Paramètres (calibration, marge, N, seuils de sélection) appris sur l'apprentissage seulement ; validation et test sans réoptimisation.
Usage : python3 etude/bot5min/alpha_executable.py → etude/bot5min/resultat_alpha_executable.md"""
exec(open("etude/bot5min/hedge_lab.py").read().split("# ================================================================ variables pour les modèles")[0])
from sklearn.linear_model import LogisticRegression, Ridge
CP = ("A", "B")
lg = lambda x: math.log(min(0.999, max(0.001, x)) / (1 - min(0.999, max(0.001, x))))
DELS = (0.3, 0.6, 0.9, 1.5, 3.0)

# ================================================================ informations par signal (connues au signal) + futur pour la mesure
SIGS = []
for coh in CP:
    thr = 0.30 if coh == "A" else 0.20
    for st in sorted(COH[coh]):
        s = COH[coh][st]; d = arr(st); v = cote(d, s["up"], s["mod"]); T = d["T"]; i = s["i"]; end = d["end"]
        a0, z0 = v["oa"][i], v["oaz"][i]; q0 = min(50 / (a0 + FEE(a0)), z0)
        if q0 < 1: continue
        i30 = int(ge(T, T[i] - 30)); X0 = d["X"][i30:i + 1, 0]
        vol = float(np.nanstd(np.diff(X0))) if len(X0) > 5 else 0.0
        SIGS.append(dict(coh=coh, st=st, per=PER(st), d=d, v=v, T=T, i=i, end=end, a0=a0, z0=z0, q0=q0, fair=s["fair"], w=gagne(st, s["up"]), thr=thr, up=s["up"],
                         mid=(a0 + v["ob"][i]) / 2, spr=a0 - v["ob"][i], vol=vol, tl=end - T[i], t0=T[i]))
print("signaux", collections.Counter((x["coh"], x["per"]) for x in SIGS), flush=True)
def row(x, dl):
    j = int(ge(x["T"], x["t0"] + dl)); return j if j < len(x["T"]) and x["T"][j] < x["end"] else None

# ================================================================ E2 : probabilité prudente (calibration sur l'apprentissage) et prix maximal
def fcal(x): return [lg(x["fair"]), lg(x["mid"]), 1.0 if x["coh"] == "B" else 0.0]
TRN = [x for x in SIGS if x["per"] == "apprentissage"]
CAL = LogisticRegression(C=1.0, max_iter=500).fit(np.array([fcal(x) for x in TRN]), np.array([x["w"] for x in TRN]))
for x in SIGS: x["pp"] = float(CAL.predict_proba(np.array([fcal(x)]))[0, 1])
def cap_of(p, m):
    r = p - m
    if r <= 0.01: return 0.0
    c = (1.072 - math.sqrt(1.072 ** 2 - 4 * 0.072 * r)) / (2 * 0.072)
    return math.floor(c * 100 + 1e-9) / 100

# ================================================================ exécutions
def fill(x, j, lim, qf):
    """achat preneur au meilleur vendeur de la ligne j si ≤ lim ; quantité affichée × qf ; 50 $ max"""
    if j is None: return None
    a = x["v"]["oa"][j]; z = x["v"]["oaz"][j] * qf
    if not np.isfinite(a) or a > lim + 1e-9: return None
    q = min(50 / (a + FEE(a)), z)
    return (q, a, FEE(a), j) if q >= 1 else None
def pol(x, kind, dl=0.3, m=0.0, N=0.0, qf=None):
    qf = (1.0 if dl < 0.5 else 0.5) if qf is None else qf
    cap = cap_of(x["pp"], m)
    if kind == "signal": return fill(x, x["i"], x["a0"], 1.0)
    if kind == "actuel": return fill(x, row(x, dl), x["a0"], qf)                 # limite = prix vu au signal (règle actuelle du laboratoire)
    if kind == "marché": return fill(x, row(x, dl), 1.0, qf)                      # meilleur vendeur après le délai, quel que soit le prix
    if kind == "plafond": return fill(x, row(x, dl), cap, qf)                     # (2) limite agressive au prix maximal (meilleur niveau seulement)
    if kind == "abandon": return fill(x, row(x, dl), x["a0"], qf) if x["a0"] <= cap + 1e-9 else None   # (3) on n'envoie rien si le prix du signal > plafond
    if kind == "seconde":                                                          # (4) plafond, puis on surveille N s une nouvelle offre ≤ plafond
        r = fill(x, row(x, dl), cap, qf)
        if r or N <= 0: return r
        T = x["T"]; oa = x["v"]["oa"]; j0 = row(x, dl)
        if j0 is None: return None
        j1 = int(le(T, min(x["t0"] + dl + N, x["end"] - 1)))
        for k in range(j0 + 1, j1 + 1):
            if np.isfinite(oa[k]) and oa[k] <= cap + 1e-9:
                r = fill(x, int(ge(T, T[k] + dl)) if int(ge(T, T[k] + dl)) < len(T) and T[int(ge(T, T[k] + dl))] < x["end"] else None, cap, qf)
                if r: return r
        return None
    if kind in ("passif optimiste", "passif pessimiste"):                         # (5) bornes : ordre passif à min(plafond, prix du signal − 1 c), 30 s
        L = round(min(cap, x["a0"] - 0.01), 2); j0 = row(x, dl)
        if L < 0.01 or j0 is None: return None
        T = x["T"]; oa = x["v"]["oa"]; oaz = x["v"]["oaz"]; j1 = int(le(T, min(x["t0"] + dl + 30, x["end"] - 1)))
        for k in range(j0 + 1, j1 + 1):
            if kind == "passif optimiste" and oa[k] <= L + 1e-9: return (50 / L, L, 0.0, k)
            if kind == "passif pessimiste" and k + 1 <= j1 and oa[k] <= L - 0.01 + 1e-9 and oa[k + 1] <= L - 0.01 + 1e-9:
                q = min(50 / L, oaz[k] * 0.5)
                if q >= 1: return (q, L, 0.0, k)
        return None
def pn(x, r): return 0.0 if r is None else r[0] * ((1 if x["w"] else 0) - r[1] - r[2])

# ---- paramètres sur l'apprentissage
def tot(coh, fn): return sum(pn(x, fn(x)) for x in SIGS if x["coh"] == coh and x["per"] == "apprentissage")
MARG, NSEC = {}, {}
for coh in CP:
    g = {m: tot(coh, lambda x, m=m: pol(x, "plafond", m=m)) for m in (0.0, 0.02, 0.05, 0.10, 0.15)}; MARG[coh] = (max(g, key=g.get), g)
    g2 = {N: tot(coh, lambda x, N=N: pol(x, "seconde", m=MARG[coh][0], N=N)) for N in (1, 3, 5, 10, 30)}; NSEC[coh] = (max(g2, key=g2.get), g2)
print("marge", MARG, "N", NSEC, flush=True)

# ================================================================ H158-H164 : sélection avec des variables connues à la décision
def fsel(x): return [x["fair"] - x["a0"], math.log1p(x["z0"]), math.log1p(x["z0"] / x["q0"]), x["vol"], x["tl"], x["a0"], x["spr"], x["pp"] - x["a0"], 1.0 if x["coh"] == "B" else 0.0]
FN_SEL = ["écart modèle − prix", "log taille affichée", "log taille / parts voulues", "volatilité perp 30 s", "temps restant", "prix", "écart vendeur-acheteur", "proba prudente − prix", "cohorte B"]
for x in SIGS: x["surv"] = pol(x, "actuel") is not None
Ftr = np.array([fsel(x) for x in TRN]); MUs, SDs = Ftr.mean(0), Ftr.std(0) + 1e-9
MSURV = LogisticRegression(C=1.0, max_iter=500).fit((Ftr - MUs) / SDs, np.array([x["surv"] for x in TRN]))
MPNL = Ridge(alpha=10.0).fit((Ftr - MUs) / SDs, np.array([pn(x, pol(x, "actuel")) for x in TRN]))
for x in SIGS:
    f_ = (np.array(fsel(x)) - MUs) / SDs
    x["psurv"] = float(MSURV.predict_proba(f_[None])[0, 1]); x["ppnl"] = float(MPNL.predict(f_[None])[0])
THS = {}
for coh in CP:
    g = {th: tot(coh, lambda x, th=th: pol(x, "actuel") if x["psurv"] >= th else None) for th in (0.0, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8)}; THS[coh] = (max(g, key=g.get), g)
AUCS = {}
from sklearn.metrics import roc_auc_score
for per in PERS:
    Y = [x for x in SIGS if x["per"] == per]; yy = np.array([x["surv"] for x in Y])
    AUCS[per] = roc_auc_score(yy, [x["psurv"] for x in Y]) if 0 < yy.sum() < len(yy) else float("nan")
print("sélection", THS, AUCS, flush=True)

POLS = {"actuel (limite = prix du signal, 0,3 s)": lambda x: pol(x, "actuel"),
        "(1) marché après 0,3 s (sans limite)": lambda x: pol(x, "marché"),
        "(2) limite agressive au plafond": lambda x: pol(x, "plafond", m=MARG[x["coh"]][0]),
        "(3) abandon si prix du signal > plafond": lambda x: pol(x, "abandon", m=MARG[x["coh"]][0]),
        "(4) seconde chance N s au plafond": lambda x: pol(x, "seconde", m=MARG[x["coh"]][0], N=NSEC[x["coh"]][0]),
        "(5) passif borne optimiste": lambda x: pol(x, "passif optimiste", m=MARG[x["coh"]][0]),
        "(5) passif borne pessimiste": lambda x: pol(x, "passif pessimiste", m=MARG[x["coh"]][0]),
        "H163 sélection : P(offre encore là à 0,3 s) ≥ seuil": lambda x: pol(x, "actuel") if x["psurv"] >= THS[x["coh"]][0] else None,
        "H163 sélection : P&L prédit > 0 (ridge, app.)": lambda x: pol(x, "actuel") if x["ppnl"] > 0 else None,
        "actuel à 0,6 s (moitié de la taille)": lambda x: pol(x, "actuel", dl=0.6),
        "(2) plafond à 0,6 s": lambda x: pol(x, "plafond", dl=0.6, m=MARG[x["coh"]][0])}
RES = {nm: [(x, f(x)) for x in SIGS] for nm, f in POLS.items()}
SIG0 = [(x, pol(x, "signal")) for x in SIGS]
def ic(diffs, per):
    H_ = collections.defaultdict(float)
    for st in CYC[per]: H_[st // 3600] += 0.0
    for st, v_ in diffs: H_[st // 3600] += v_
    hv = np.array(list(H_.values())); sims = hv[RNG.integers(0, len(hv), (2000, len(hv)))].sum(1); return np.percentile(sims, [5, 95])
def bil(nm, coh, per):
    L = [(x, r) for x, r in RES[nm] if x["coh"] == coh and x["per"] == per]; B = {x["st"]: r for x, r in RES["actuel (limite = prix du signal, 0,3 s)"] if x["coh"] == coh and x["per"] == per}
    tot_ = sum(pn(x, r) for x, r in L); base = sum(pn(x, B[x["st"]]) for x, _ in L)
    lo, hi = ic([(x["st"], pn(x, r) - pn(x, B[x["st"]])) for x, r in L], per)
    n = sum(1 for _, r in L if r); part = sum(1 for x, r in L if r and r[0] < 50 / (r[1] + r[2]) - 1e-6)
    jk = [x for x, r0 in SIG0 if x["coh"] == coh and x["per"] == per and r0 and pn(x, r0) >= 4 * r0[0] * (r0[1] + r0[2])]
    R_ = {x["st"]: r for x, r in L}
    miss = sum(1 for x in jk if R_[x["st"]] is None); fees = sum(r[0] * r[2] for _, r in L if r)
    pnl_ = np.array([pn(x, r) for x, r in L]); c_ = np.cumsum(pnl_) if len(pnl_) else np.zeros(1)
    dd = float(min(0.0, np.min(c_ - np.maximum.accumulate(np.concatenate([[0], c_]))[1:]))) if len(pnl_) else 0.0
    return dict(N=len(L), n=n, part=part, pnl=tot_, d=tot_ - base, lo=lo, hi=hi, fees=fees, miss=miss, jk=len(jk), dd=dd)

# ================================================================ E1 : durée de vie des signaux
def vie(x):
    T, oa, oaz, fair = x["T"], x["v"]["oa"], x["v"]["oaz"], x["v"]["fair"]; i, end = x["i"], x["end"]; t0 = x["t0"]
    cap = cap_of(x["pp"], MARG[x["coh"]][0])
    def dur(cond):
        k = i
        while k + 1 < len(T) and T[k + 1] < end and cond(k + 1): k += 1
        return (T[k + 1] if k + 1 < len(T) else end) - t0
    lo_, hi_ = (0.15, 0.35) if x["coh"] == "A" else (0.03, 0.97)
    d_cond = dur(lambda k: np.isfinite(oa[k]) and lo_ <= oa[k] <= hi_ and fair[k] - oa[k] >= x["thr"])
    d_offre = dur(lambda k: np.isfinite(oa[k]) and oa[k] <= x["a0"] + 1e-9 and oaz[k] >= 1)
    d_eco = dur(lambda k: np.isfinite(oa[k]) and fair[k] - oa[k] - FEE(oa[k]) >= 0.10)
    over = [T[k] - t0 for k in range(i + 1, len(T)) if T[k] < end and np.isfinite(oa[k]) and oa[k] > cap + 1e-9]
    qd = {}
    for dl in DELS:
        j = row(x, dl); qd[dl] = (min(x["q0"], oaz[j]) / x["q0"] if j is not None and oa[j] <= x["a0"] + 1e-9 else 0.0)
    # secondes fenêtres : après la disparition de l'offre initiale, retour à un prix ≤ prix du signal (taille ≥ 1) / ≤ plafond
    k = i
    while k + 1 < len(T) and T[k + 1] < end and np.isfinite(oa[k + 1]) and oa[k + 1] <= x["a0"] + 1e-9 and oaz[k + 1] >= 1: k += 1
    n2 = n2c = 0; prev = False; prevc = False
    for kk in range(k + 1, len(T)):
        if T[kk] >= end: break
        ok_ = np.isfinite(oa[kk]) and oa[kk] <= x["a0"] + 1e-9 and oaz[kk] >= 1; okc = np.isfinite(oa[kk]) and oa[kk] <= cap + 1e-9 and oaz[kk] >= 1
        n2 += ok_ and not prev; n2c += okc and not prevc; prev, prevc = ok_, okc
    # photos 100 ms
    ph = {}
    if x["st"] in LEAD:
        L_ = LEAD[x["st"]]; lt = np.array([t_ for t_, _ in L_])
        k0 = int(np.searchsorted(lt, t0)) - 1
        if 0 <= k0 and t0 - lt[k0] <= 0.15:
            for dl in (0.1, 0.2, 0.3):
                kk = int(np.searchsorted(lt, t0 + dl))
                if kk < len(lt) and lt[kk] - (t0 + dl) <= 0.15:
                    asks = L_[kk][1][0] if x["up"] else L_[kk][1][1]
                    ph[dl] = min(x["q0"], sum(sz for p_, sz in (asks or []) if p_ <= x["a0"] + 1e-9)) / x["q0"]
    return dict(d_cond=d_cond, d_offre=d_offre, d_eco=d_eco, over=(over[0] if over else None), qd=qd, n2=n2, n2c=n2c, ph=ph, cap=cap)
for x in SIGS: x["vie"] = vie(x)
print("E1", f"{_time.time() - _T0:.0f} s", flush=True)

# ================================================================ rédaction
q_ = lambda a, v: f2(np.percentile(a, v)) if len(a) else "—"
out = ["# BOT95 — ALPHA EXÉCUTABLE : quelle part de l'avantage au signal survit à notre délai réel ?", "",
       f"Étude hors ligne du {_time.strftime('%d.%m.%Y')} — aucun bot, aucun workflow modifié, rien publié. Cohortes A et B (mêmes entrées que le Hedge Lab). "
       f"Apprentissage < {hs(CUT)} · validation → {hs(MATIN0)} · test inédit après. **Tout est mesuré à 0,3 s** (lignes enregistrées toutes les ~0,3 s ; photos 100 ms seulement là où elles couvrent le signal). "
       "Les enregistrements 50 ms du VPS de Dublin ne sont **pas encore disponibles** : une section 50 ms sera ajoutée plus tard.", ""]
VERD = len(out)
# ---- cascade
out += ["## 1. Cascade de l'avantage (mesuré à 0,3 s)", "",
        "Avantage théorique = Σ parts × (proba du modèle − prix − frais) ; réalisé = Σ parts × (issue − prix − frais). Au signal : prix et taille de la ligne du signal. "
        "À 0,3 / 0,6 s : ordre au meilleur vendeur de la ligne exécutée (marché, sans limite ; 0,6 s : moitié de la taille). "
        "(a) **modèle faux** = avantage théorique au signal − P&L réalisé au signal ; (b) **offre disparue** = P&L au signal des parts qu'on n'a plus pu acheter ; (c) **payé trop cher** = surcoût (prix + frais) sur les parts achetées ; autre = parts en plus (prix plus bas).", "",
        "| Cohorte | Période | Signaux | Avantage théorique au signal | à 0,3 s | à 0,6 s | P&L réalisé au signal | (a) modèle faux | à 0,3 s (marché) | (b) offre disparue | (c) payé trop cher | autre | à 0,3 s, règle actuelle (limite = prix du signal) | à 0,6 s (marché) |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
WF = {}
for coh in CP:
    for per in PERS:
        X = [x for x in SIGS if x["coh"] == coh and x["per"] == per]
        th0 = sum(x["q0"] * (x["fair"] - x["a0"] - FEE(x["a0"])) for x in X)
        def th(dl):
            s_ = 0.0
            for x in X:
                r = pol(x, "marché", dl=dl)
                if r: s_ += r[0] * (x["fair"] - r[1] - r[2])
            return s_
        r0 = sum(pn(x, pol(x, "signal")) for x in X)
        b = c = o = 0.0
        for x in X:
            r = pol(x, "marché"); u0 = (1 if x["w"] else 0) - x["a0"] - FEE(x["a0"])
            qd_ = r[0] if r else 0.0; qm = min(qd_, x["q0"])
            b += (x["q0"] - qm) * u0
            if r: c -= qm * ((r[1] + r[2]) - (x["a0"] + FEE(x["a0"]))); o += (qd_ - qm) * ((1 if x["w"] else 0) - r[1] - r[2])
        r3 = sum(pn(x, pol(x, "marché")) for x in X); r3a = sum(pn(x, pol(x, "actuel")) for x in X); r6 = sum(pn(x, pol(x, "marché", dl=0.6)) for x in X)
        WF[(coh, per)] = dict(th0=th0, r0=r0, r3=r3, r3a=r3a, b=-b, c=c)
        out.append(f"| {coh} | {per} | {len(X)} | {f0(th0)} | {f0(th(0.3))} | {f0(th(0.6))} | **{f0(r0)}** | {f0(r0 - th0)} | **{f0(r3)}** | {f0(-b)} | {f0(c)} | {f0(o)} | {f0(r3a)} | {f0(r6)} |")
out += ["", "Contrôle : P&L au signal + (b) + (c) + autre = P&L à 0,3 s (marché).", ""]
# ---- E1
out += ["## 2. E1 — Durée de vie des signaux (mesuré à 0,3 s)", "",
        "Durées depuis la ligne du signal jusqu'à la première ligne où : la condition d'écart n'est plus vraie (écart modèle − prix ≥ seuil dans la bande de prix) ; l'offre initiale n'est plus là (prix ≤ prix du signal avec ≥ 1 part) ; "
        "l'avantage économique (modèle − prix − frais ≥ 0,10) n'est plus là. Une durée de 0,3 s = disparue dès la ligne suivante (résolution). **Une offre qui disparaît n'est pas un avantage qui disparaît** : comparer les colonnes.", "",
        "| Cohorte | Période | Signaux | Condition (s) : 10 % · méd. · 90 % | Offre initiale (s) : 10 % · méd. · 90 % | Avantage ≥ 0,10 (s) : méd. | Prix > plafond pour la 1re fois (s) : méd. · jamais | "
        "Part de la quantité voulue encore au prix du signal à 0,3 · 0,6 · 0,9 · 1,5 · 3 s (moyenne) | Signaux avec une 2e fenêtre ≤ prix du signal · ≤ plafond | Photos 100 ms : n · part à 0,1 · 0,2 · 0,3 s |",
        "|---|---|---|---|---|---|---|---|---|---|"]
for coh in CP:
    for per in PERS:
        X = [x for x in SIGS if x["coh"] == coh and x["per"] == per]
        dc = np.array([x["vie"]["d_cond"] for x in X]); do = np.array([x["vie"]["d_offre"] for x in X]); de = np.array([x["vie"]["d_eco"] for x in X])
        ov = [x["vie"]["over"] for x in X if x["vie"]["over"] is not None]
        P_ = [x for x in X if x["vie"]["ph"]]
        phs = " · ".join(pc(np.mean([x["vie"]["ph"][dl] for x in P_ if dl in x["vie"]["ph"]])) if any(dl in x["vie"]["ph"] for x in P_) else "—" for dl in (0.1, 0.2, 0.3))
        out.append(f"| {coh} | {per} | {len(X)} | {q_(dc, 10)} · {q_(dc, 50)} · {q_(dc, 90)} | {q_(do, 10)} · {q_(do, 50)} · {q_(do, 90)} | {q_(de, 50)} | {q_(np.array(ov), 50)} · {pc(1 - len(ov) / len(X))} | "
                   + " · ".join(pc(np.mean([x["vie"]["qd"][dl] for x in X])) for dl in DELS) + f" | {pc(np.mean([x['vie']['n2'] > 0 for x in X]))} · {pc(np.mean([x['vie']['n2c'] > 0 for x in X]))} | {len(P_)} · {phs} |")
out += ["", "Les quantités à 0,1 / 0,2 s viennent des photos 100 ms (3 meilleurs niveaux, quantité à un prix ≤ prix du signal) ; elles ne couvrent qu'une partie des signaux.", ""]
# ---- grand mais bref / modéré mais persistant
out += ["### H160 — grand mais bref contre modéré mais persistant (classé avec l'information du signal seulement)", "",
        "Classes fixées sur l'apprentissage : écart modèle − prix au-dessus / au-dessous de sa médiane d'apprentissage ; taille affichée au-dessus / au-dessous de sa médiane d'apprentissage.", "",
        "| Cohorte | Écart au signal | Taille affichée | Période | Signaux | Offre encore là à 0,3 s | Durée médiane de l'offre (s) | P&L au signal | P&L à 0,3 s (règle actuelle) |", "|---|---|---|---|---|---|---|---|---|"]
for coh in CP:
    tr_ = [x for x in SIGS if x["coh"] == coh and x["per"] == "apprentissage"]
    me = np.median([x["fair"] - x["a0"] for x in tr_]); mz = np.median([x["z0"] for x in tr_])
    for ge_ in (True, False):
        for gz in (True, False):
            for per in PER2:
                X = [x for x in SIGS if x["coh"] == coh and x["per"] == per and ((x["fair"] - x["a0"]) >= me) == ge_ and (x["z0"] >= mz) == gz]
                if not X: continue
                out.append(f"| {coh} | {'grand' if ge_ else 'modéré'} | {'grande' if gz else 'petite'} | {per} | {len(X)} | {pc(np.mean([x['surv'] for x in X]))} | {q_(np.array([x['vie']['d_offre'] for x in X]), 50)} | "
                           f"{f0(sum(pn(x, pol(x, 'signal')) for x in X))} | {f0(sum(pn(x, pol(x, 'actuel')) for x in X))} |")
out.append("")
# ---- E2
out += ["## 3. E2 — Prix maximal exécutable et politiques d'exécution (mesuré à 0,3 s)", "",
        f"Probabilité prudente = régression logistique sur l'apprentissage (A + B réunis) de l'issue sur logit(proba du modèle), logit(milieu Polymarket) et la cohorte ; coefficients {', '.join(f2(c) for c in CAL.coef_[0])}, constante {f2(CAL.intercept_[0])}. "
        "Plafond = plus haut prix c tel que c + frais(c) ≤ proba prudente − marge (arrondi au cent inférieur). "
        "Marge et N choisis sur l'apprentissage : " + " · ".join(f"{coh} marge {f2(MARG[coh][0])} (" + ", ".join(f"{f2(m)} → {f0(v_)}" for m, v_ in MARG[coh][1].items()) + f"), N = {NSEC[coh][0]} s (" + ", ".join(f"{k} s → {f0(v_)}" for k, v_ in NSEC[coh][1].items()) + ")" for coh in CP) + ".", "",
        "**Profondeur inconnue** : seul le meilleur niveau existe dans les lignes ; la « limite agressive » (2) ne prend donc que le meilleur niveau, et (2) = (3) à ceci près que (3) garde la limite au prix du signal. "
        "(5) est une borne : ordre passif à min(plafond, prix du signal − 1 c) pendant 30 s, optimiste = rempli dès que le vendeur touche (50 $ entiers), pessimiste = traversée d'1 c tenue 2 lignes, moitié de la taille.", "",
        "| Cohorte | Politique | Période | Signaux | Entrées (participation) | Partielles | Frais | P&L net | Δ vs actuel [IC 90 %] | Jackpots du signal manqués | Creux |", "|---|---|---|---|---|---|---|---|---|---|---|"]
BIL = {}
for coh in CP:
    for nm in POLS:
        for per in PERS:
            b_ = bil(nm, coh, per); BIL[(coh, nm, per)] = b_
            out.append(f"| {coh} | {nm} | {per} | {b_['N']} | {b_['n']} ({pc(b_['n'] / max(1, b_['N']))}) | {b_['part']} | {f0(b_['fees'])} | {f0(b_['pnl'])} | "
                       + ("—" if nm.startswith("actuel (") else f"**{f0(b_['d'])}** [{f0(b_['lo'])} ; {f0(b_['hi'])}]") + f" | {b_['miss']}/{b_['jk']} | {f0(b_['dd'])} |")
out += ["", f"Sélection H163 : modèle « offre encore là à 0,3 s » (logistique, apprentissage, variables : {', '.join(FN_SEL)}) — AUC " + " · ".join(f"{per} {f2(a_)}" for per, a_ in AUCS.items())
        + " ; seuil choisi sur l'apprentissage : " + " · ".join(f"{coh} {f2(THS[coh][0])}" for coh in CP) + ". Le modèle « P&L prédit » est une régression ridge sur l'apprentissage (mêmes variables).", "",
        f"Durée de calcul : {_time.time() - _T0:.0f} s."]
# ---- verdict
V = ["## Réponse courte (en tête) — mesuré à 0,3 s", ""]
for coh in CP:
    cel = []
    for per in PERS:
        w_ = WF[(coh, per)]
        cel.append(f"{per} : théorique {f0(w_['th0'])} → réalisé au signal {f0(w_['r0'])} → 0,3 s marché {f0(w_['r3'])} (offre disparue {f0(w_['b'])}, payé trop cher {f0(w_['c'])}) → règle actuelle {f0(w_['r3a'])}")
    V.append(f"- **Cascade {coh}** : " + " ; ".join(cel) + ".")
for coh in CP:
    X = [x for x in SIGS if x["coh"] == coh and x["per"] != "apprentissage"]
    V.append(f"- **Durée de vie {coh}** (valid. + test) : offre initiale médiane {q_(np.array([x['vie']['d_offre'] for x in X]), 50)} s ; quantité voulue encore au prix du signal à 0,3 s : {pc(np.mean([x['vie']['qd'][0.3] for x in X]))} en moyenne, "
             f"à 0,6 s : {pc(np.mean([x['vie']['qd'][0.6] for x in X]))} ; condition d'écart médiane {q_(np.array([x['vie']['d_cond'] for x in X]), 50)} s ; seconde fenêtre au prix du signal dans {pc(np.mean([x['vie']['n2'] > 0 for x in X]))} des signaux.")
gagn = []
for coh in CP:
    for nm in POLS:
        if nm.startswith("actuel (") or "passif" in nm: continue
        v_, t_ = BIL[(coh, nm, "validation")], BIL[(coh, nm, "inédit")]
        if v_["lo"] > 0 and t_["lo"] > 0: gagn.append(f"{coh} {nm}")
best = {coh: sorted([nm for nm in POLS if not nm.startswith("actuel (") and "passif" not in nm and "0,6" not in nm], key=lambda nm: -BIL[(coh, nm, "validation")]["d"])[:3] for coh in CP}
for coh in CP:
    V.append(f"- **Politiques {coh}** (Δ vs actuel, valid. → test) : " + " ; ".join(f"{nm} {f0(BIL[(coh, nm, 'validation')]['d'])} [{f0(BIL[(coh, nm, 'validation')]['lo'])} ; {f0(BIL[(coh, nm, 'validation')]['hi'])}] → {f0(BIL[(coh, nm, 'inédit')]['d'])} [{f0(BIL[(coh, nm, 'inédit')]['lo'])} ; {f0(BIL[(coh, nm, 'inédit')]['hi'])}]" for nm in best[coh])
             + f". Passif (bornes) valid. : {f0(BIL[(coh, '(5) passif borne optimiste', 'validation')]['d'])} / {f0(BIL[(coh, '(5) passif borne pessimiste', 'validation')]['d'])}.")
V.append("- **Réponse à Pitch** : " + ("sélectionner les opportunités dont l'avantage survit au délai n'améliore PAS la performance de façon démontrée : aucune politique n'a un IC 90 % entièrement positif à la fois en validation et en test." if not gagn else
                                     "amélioration démontrée (IC 90 % > 0 en validation ET en test) pour : " + ", ".join(gagn) + " — à reconfirmer avec les données 50 ms de Dublin."))
V.append("")
out[VERD:VERD] = V
open("etude/bot5min/resultat_alpha_executable.md", "w").write("\n".join(out))
print("\n".join(V)); print(f"fini en {_time.time() - _T0:.0f} s")
