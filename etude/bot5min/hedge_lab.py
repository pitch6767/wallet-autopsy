"""BOT95 HEDGE LAB V1 — demande de Pitch (11.10.2026). Hors ligne : aucun bot, aucun fichier du bot, aucun workflow modifié.
Deux cohortes d'entrée (A désaccord 30 zone + modèle monte ; B V2-F corrigé 0,015 %) + C diagnostic (V2-F original).
24 couvertures H01-H24 (fonctions indépendantes), mêmes entrées que la référence GARDER, trois scénarios d'exécution
(idéal / prudent / pessimiste), portefeuille partagé de 250 $ par cohorte et par période (classement) + version indépendante 50 $.
Seuils et modèles ajustés sur l'apprentissage SEULEMENT ; validation et test inédit rapportés séparément ; IC 90 % par blocs d'une heure.
Usage : python3 etude/bot5min/hedge_lab.py (depuis /home/claude/wallet-autopsy) → etude/bot5min/resultat_hedge_lab.md"""
exec(open("etude/bot5min/hedge_lab_commun.py").read())
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

pc = lambda x: f"{100 * x:.1f} %".replace(".", ",") if x == x else "—"
f2 = lambda x: f"{x:.2f}".replace(".", ",").replace("-", "−") if x == x else "—"
f3 = lambda x: f"{x:.3f}".replace(".", ",").replace("-", "−") if x == x else "—"
FEEV = lambda x: 0.072 * x * (1 - x)
MAKER_FEE = 0.0          # hypothèse NON vérifiée : frais teneur d'ordre = 0
SCEN = {"idéal": dict(lat=0.0, qf=None, mk="touche"), "prudent": dict(lat=0.3, qf=1.0, mk="traverse"), "pessimiste": dict(lat=0.6, qf=0.5, mk="traverse2")}
SCN = list(SCEN)
PER2 = ("validation", "inédit")
BANK0 = 250.0
TH = {}                  # seuils appris sur l'apprentissage (remplis plus bas)

# ================================================================ moteur de position
class Pos:
    """une position (entrée de la cohorte) + les ordres d'une couverture. Carnet au meilleur niveau, lignes 0,3 s.
    trade() : ordre preneur à cours limité au prix vu à la décision (ligne k), exécuté à la ligne k + délai ; sinon rien (la couverture peut réessayer).
    maker() : ordre passif d'achat du côté opposé ; règle de remplissage du scénario (file d'attente : nous sommes DERNIERS)."""
    def __init__(s, st, sig, sc, budget=50.0, bank=float("inf")):
        d = arr(st); v = cote(d, sig["up"], sig["mod"]); s.d, s.v, s.T, s.end = d, v, d["T"], d["end"]
        s.sc = sc; cf = SCEN[sc]; s.lat, s.qf, s.mk = cf["lat"], cf["qf"], cf["mk"]
        s.sig, s.st, s.w = sig, st, gagne(st, sig["up"]); s.ok = False; s.why = None
        s.used = {}; s.trig = None; s.att = False; s.rejh = 0; s.notes = {}; s.lastfill = None
        s.kend = int(le(s.T, s.end - 1)) + 1
        s.capcap = float("inf")
        j = s.row(sig["i"])
        if j is None: s.why = "fin"; return
        a = v["oa"][j]
        if not np.isfinite(a) or a > sig["a"] + 1e-9: s.why = "prix"; return
        z = v["oaz"][j] * (0.5 if sc == "pessimiste" else 1.0)
        q = min(budget / (a + FEE(a)), z)
        if q < 1: s.why = "capital" if budget / (a + FEE(a)) < 1 else "quantité"; return
        s.q0 = s.qo = q; s.a = a; s.C0 = q * (a + FEE(a)); s.qp = 0.0; s.cash = -s.C0; s.bank = bank; s.mcred = 0.0; s.merged = 0.0
        s.peak = s.C0; s.je = j; s.ok = True; s.used[(j, "own", "buy")] = q
        s.own_cost, s.own_qb, s.opp_cost, s.opp_costnf, s.opp_qb, s.sell_q = s.C0, q, 0.0, 0.0, 0.0, 0.0
        s.budget = budget
    def row(s, k):
        if k is None or k >= len(s.T): return None
        j = k if s.lat == 0 else int(ge(s.T, s.T[k] + s.lat))
        return j if j < len(s.T) and s.T[j] < s.end else None
    def free(s): return s.bank - (-s.cash - s.mcred)
    def mark(s, k):
        if s.trig is None: s.trig = k; s.att = True
    def _merge(s):
        if s.sc == "idéal":                                   # fusion Up + Down = 1 $ tout de suite (idéal seulement)
            pr = min(s.qo, s.qp)
            if pr > s.merged: s.mcred += pr - s.merged; s.merged = pr
        imm = -s.cash - s.mcred
        if imm > s.peak: s.peak = imm
    def trade(s, k, tok, side, want, limit=None):
        j = s.row(k)
        if j is None or want < 1: return 0.0
        v = s.v
        P, Z = {("own", "buy"): ("oa", "oaz"), ("own", "sell"): ("ob", "obz"), ("opp", "buy"): ("pa", "paz"), ("opp", "sell"): ("pb", "pbz")}[(tok, side)]
        px = v[P][j]; lim = v[P][k] if limit is None else limit
        if not np.isfinite(px) or not np.isfinite(lim): return 0.0
        if side == "buy" and px > lim + 1e-9: return 0.0
        if side == "sell" and px < lim - 1e-9: return 0.0
        key = (j, tok, side)
        avail = float("inf") if s.qf is None else v[Z][j] * s.qf - s.used.get(key, 0.0)
        qty = min(want, avail)
        fee = FEE(px)
        if side == "buy":
            cap = min(s.free(), s.capcap - (-s.cash))
            if qty * (px + fee) > cap + 1e-9:
                qty = max(0.0, cap / (px + fee)); s.rejh += 1
        else:
            qty = min(qty, s.qo if tok == "own" else s.qp)          # idéal : une paire fusionnée peut être « défusionnée » (neutre en P&L)
        if qty < 1: return 0.0
        s.used[key] = s.used.get(key, 0.0) + qty
        if side == "buy":
            s.cash -= qty * (px + fee)
            if tok == "own": s.qo += qty; s.own_cost += qty * (px + fee); s.own_qb += qty
            else: s.qp += qty; s.opp_cost += qty * (px + fee); s.opp_costnf += qty * px; s.opp_qb += qty
        else:
            s.cash += qty * (px - fee)
            if tok == "own": s.qo -= qty; s.sell_q += qty
            else: s.qp -= qty; s.notes["revendu"] = s.notes.get("revendu", 0.0) + qty
            pr = min(s.qo, s.qp)
            if pr < s.merged: s.mcred -= s.merged - pr; s.merged = pr
        s.lastfill = j; s._merge(); return qty
    def maker(s, k, L, want, t_exp):
        """achat passif du côté opposé à L (≤ vendeur − 1 c), valable jusqu'à t_exp. Renvoie la quantité remplie."""
        j = s.row(k); L = round(L, 2)
        if j is None or L < 0.01 or want < 1: return 0.0
        want = min(want, max(0.0, s.free() / max(L, 1e-9)), max(0.0, (s.capcap - (-s.cash)) / L))
        if want < 1: s.rejh += 1; return 0.0
        m1 = min(int(le(s.T, min(t_exp, s.end - 1e-6))), len(s.T) - 1)
        if m1 <= j: return 0.0
        pa, paz = s.v["pa"], s.v["paz"]; seg = pa[j + 1:m1 + 2]
        if s.mk == "touche": cond = seg[:m1 - j] <= L + 1e-9
        elif s.mk == "traverse": cond = seg[:m1 - j] <= L - 0.01 + 1e-9
        else:
            c = seg <= L - 0.01 + 1e-9
            if len(c) < m1 - j + 1: c = np.append(c, False)
            cond = c[:m1 - j] & c[1:m1 - j + 1]
        s.notes["maker_pose"] = s.notes.get("maker_pose", 0) + 1
        got = 0.0
        for idx in np.where(cond)[0]:
            m = j + 1 + int(idx); rem = want - got
            if rem < 1: break
            q = rem if s.qf is None else min(rem, paz[m] * s.qf - s.used.get((m, "opp", "mk"), 0.0))
            if q < 1: continue
            s.used[(m, "opp", "mk")] = s.used.get((m, "opp", "mk"), 0.0) + q
            got += q; s.qp += q; c_ = q * (L + MAKER_FEE * FEE(L)); s.cash -= c_; s.opp_cost += c_; s.opp_costnf += q * L; s.opp_qb += q
            s.lastfill = m; s._merge()
        if got >= 1: s.notes["maker_rempli"] = s.notes.get("maker_rempli", 0.0) + got
        return got
    def loop(s, rows, tok, side, target_fn, limit_fn=None):
        """réessaie aux lignes données (ordre renouvelé au prix du moment) tant que target_fn() ≥ 1 part"""
        for k in rows:
            k = int(k)
            if k >= s.kend: break
            w = target_fn()
            if w < 1: break
            s.trade(k, tok, side, w, None if limit_fn is None else limit_fn(k))
    def rows_from(s, k): return range(k, s.kend)
    def pnl(s): return s.qo * s.w + s.qp * (1 - s.w) + s.cash
    def worst(s): return min(s.qo, s.qp) + s.cash
    def best(s): return max(s.qo, s.qp) + s.cash
    # --------------- déclencheurs communs (vectorisés)
    def k_m10(s):
        if "m10" not in s.notes:
            f = s.v["fair"]; k0 = s.je + 1; r = None
            if k0 < s.kend:
                w = np.where((f[k0:s.kend] <= s.sig["fair"] - 0.10) & (s.T[k0:s.kend] <= s.end - 2))[0]
                r = k0 + int(w[0]) if len(w) else None
            s.notes["m10"] = r
        return s.notes["m10"]
    def pcost(s):
        pa = s.v["pa"][s.je + 1:s.kend]
        return s.a + FEE(s.a) + pa + FEEV(pa)
    def cand(s, mask): return s.je + 1 + np.where(mask)[0]

# ================================================================ variables pour les modèles (connues à la décision)
FNOMS = ["temps restant", "vendeur opposé", "log taille opposée", "vendeur de notre côté", "proba modèle notre côté",
         "variation vendeur opposé 1 s", "variation vendeur opposé 3 s"] + [f"{b} 1 s" for b in ("Bybit", "OKX", "Coinbase", "Binance", "Chainlink")] + \
        [f"{b} 3 s" for b in ("Bybit", "OKX", "Coinbase", "Binance", "Chainlink")] + ["écart vendeur-acheteur", "distance au prix d'exercice (Chainlink)", "distance au prix d'exercice (perp)"]
def feats(d, v, td):
    T = d["T"]; k = le(T, td); k1 = np.maximum(le(T, td - 1), 0); k3 = np.maximum(le(T, td - 3), 0)
    pa = v["pa"]; sg = v["sg"]; X = d["X"]
    return np.column_stack([d["end"] - td, pa[k], np.log1p(v["paz"][k]), v["oa"][k], v["fair"][k], pa[k] - pa[k1], pa[k] - pa[k3],
                            (X[k] - X[k1]) * sg, (X[k] - X[k3]) * sg, d["UA"][k] - d["UB"][k], (X[k, 4] - d["K"][k]) * sg, (X[k, 0] - d["K"][k]) * sg]), k
def feat1(p, k): F, _ = feats(p.d, p.v, np.array([p.T[k]])); return F

# ---------------- jeu d'apprentissage : chaque seconde après chaque entrée (positions de l'apprentissage des 3 cohortes)
DEC = {}
for c, S_ in COH.items():
    for st, s in S_.items():
        d = arr(st); v = cote(d, s["up"], s["mod"]); end = st + 300
        for kk in range(1, int(end - s["t"])):
            td = s["t"] + kk
            if end - td < 1.25: break
            DEC.setdefault((st, s["up"], s["mod"], int(td)), td)
ROWS = collections.defaultdict(list)
for (st, up, mod, _), td in DEC.items(): ROWS[(st, up, mod)].append(td)
FX, YD, YR, YF, OFF, PX, VAL, STX = [], [], [], [], [], [], [], []
HD = [1, 3, 5, 10]; KF = [1, 2, 3, 5]
for (st, up, mod), tds in sorted(ROWS.items()):
    d = arr(st); v = cote(d, up, mod); T = d["T"]; td = np.array(sorted(tds)); F, k = feats(d, v, td); pa = v["pa"]; o0 = pa[k]
    yd = np.zeros((len(td), 4), bool); yr = np.zeros(len(td), bool); yf = np.zeros((len(td), 4), bool); of = np.full((len(td), 4), np.nan); ok = np.zeros((len(td), 4), bool)
    for n in range(len(td)):
        j0 = k[n] + 1
        for h, H in enumerate(HD):
            jh = le(T, td[n] + H); ok[n, h] = td[n] + H <= d["end"] - 1
            if jh >= j0: yd[n, h] = np.nanmin(pa[j0:jh + 1]) <= o0[n] - 0.01 + 1e-9
        j3 = le(T, td[n] + 3)
        if j3 >= j0: yr[n] = pa[j3] >= o0[n] + 0.02 - 1e-9
        j10 = le(T, min(td[n] + 10, d["end"] - 1))
        if j10 >= j0:
            mn = np.nanmin(pa[j0:j10 + 1])
            for c_, kk in enumerate(KF):
                yf[n, c_] = mn <= o0[n] - kk / 100 - 0.01 + 1e-9
                of[n, c_] = pa[j10] - o0[n]
    FX.append(F); YD.append(yd); YR.append(yr); YF.append(yf); OFF.append(of); VAL.append(ok); PX += [PER(st)] * len(td); STX += [st] * len(td)
FX = np.vstack(FX); YD = np.concatenate(YD); YR = np.concatenate(YR); YF = np.concatenate(YF); OFF = np.concatenate(OFF); VAL = np.concatenate(VAL); PX = np.array(PX)
good = np.all(np.isfinite(FX), 1); TRN = (PX == "apprentissage") & good
MU = FX[TRN].mean(0); SD = FX[TRN].std(0) + 1e-9
Zs = lambda F: (F - MU) / SD
lr = lambda X_, y_: LogisticRegression(C=1.0, max_iter=400).fit(Zs(X_), y_)
MD = {H: lr(FX[TRN & VAL[:, h]], YD[TRN & VAL[:, h], h]) for h, H in enumerate(HD)}
MRISE = lr(FX[TRN], YR[TRN])
MFP = {kk: lr(FX[TRN], YF[TRN, c_]) for c_, kk in enumerate(KF)}
MOFF = {kk: float(np.nanmean(OFF[TRN & ~YF[:, c_], c_])) for c_, kk in enumerate(KF)}       # hausse moyenne du vendeur opposé à 10 s si non rempli (app.)
AUCS = {}
for per in PER2:
    m_ = (PX == per) & good
    def au(y, M):
        pr = M.predict_proba(Zs(FX[m_]))[:, 1]; return roc_auc_score(y, pr) if 0 < y.sum() < len(y) else float("nan")
    AUCS[per] = {**{f"baisse ≥ 1 c en {H} s (H13-H16)": au(YD[m_, h], MD[H]) for h, H in enumerate(HD)}, "hausse ≥ 2 c en 3 s (H12)": au(YR[m_], MRISE),
                 **{f"traversée de vendeur − {kk} c en 10 s (H17/H20)": au(YF[m_, c_], MFP[kk]) for c_, kk in enumerate(KF)}}
print("modèles 1-10 s", len(FX), f"{_time.time() - _T0:.0f} s", flush=True)

# ---------------- seuils H11 (90e centile des mouvements défavorables sur 3 s, apprentissage)
def sig11(p):
    T = p.T; k0 = p.je + 1; ks = np.arange(k0, p.kend)
    if not len(ks): return None
    j3 = np.maximum(le(T, T[ks] - 3), 0); f = p.v["fair"]; X0 = p.d["X"][:, 0]; ob = p.v["ob"]
    return ks, f[j3] - f[ks], -p.v["sg"] * (X0[ks] - X0[j3]) / X0[ks], ob[j3] - ob[ks]
_s = [[], [], []]
for c, S_ in COH.items():
    for st, s in S_.items():
        if PER(st) != "apprentissage": continue
        p = Pos(st, s, "idéal")
        if not p.ok: continue
        x = sig11(p)
        if x is None: continue
        for n in range(3): _s[n].append(x[n + 1])
TH["H11"] = [float(np.nanpercentile(np.concatenate(_s[n]), 90)) for n in range(3)]
# ---------------- H18 : modèle à l'entrée — P(paire ≤ 0,95 frais compris avant la fin − 5 s, règle « traversée »)
def L18(a): return math.floor((0.95 - a - FEE(a)) * 100 + 1e-9) / 100
def y18(st, s):
    d = arr(st); v = cote(d, s["up"], s["mod"]); T = d["T"]; L = L18(v["oa"][s["i"]]); k1 = int(le(T, d["end"] - 5))
    if L < 0.01 or k1 <= s["i"]: return False
    return bool(np.nanmin(v["pa"][s["i"] + 1:k1 + 1]) <= L - 0.01 + 1e-9)
F18, Y18, P18x = [], [], []
for c, S_ in COH.items():
    for st, s in S_.items():
        d = arr(st); v = cote(d, s["up"], s["mod"]); F, _ = feats(d, v, np.array([s["t"]]))
        F18.append(np.append(F[0], v["oa"][s["i"]])); Y18.append(y18(st, s)); P18x.append(PER(st))
F18 = np.array(F18); Y18 = np.array(Y18); P18x = np.array(P18x); g18 = np.all(np.isfinite(F18), 1)
t18 = (P18x == "apprentissage") & g18; MU18 = F18[t18].mean(0); SD18 = F18[t18].std(0) + 1e-9
M18 = LogisticRegression(C=1.0, max_iter=400).fit((F18[t18] - MU18) / SD18, Y18[t18])
for per in PER2:
    m_ = (P18x == per) & g18; y = Y18[m_]
    AUCS[per]["paire ≤ 0,95 avant la fin (H18)"] = roc_auc_score(y, M18.predict_proba((F18[m_] - MU18) / SD18)[:, 1]) if 0 < y.sum() < len(y) else float("nan")
RATE18 = {per: float(Y18[(P18x == per) & g18].mean()) for per in PERS}

# ================================================================ les 24 couvertures (fonctions indépendantes)
def taker_now(p, k, target):          # achat preneur du côté opposé jusqu'à qp ≥ target, renouvelé ligne après ligne
    p.loop(p.rows_from(k), "opp", "buy", lambda: target - p.qp)
def H01(p, frac=1.0):
    pcs = p.pcost(); c = p.cand(pcs < 1)
    if not len(c): return
    p.mark(int(c[0])); p.loop(c, "opp", "buy", lambda: frac * p.q0 - p.qp)
def H02(p): H01(p, 0.25)
def H03(p): H01(p, 0.50)
def H04(p, after=None):
    pcs = p.pcost(); c = p.cand(pcs < 1)
    if after is not None: c = c[c >= after]
    pa = p.v["pa"]
    for k in c:
        k = int(k); C_ = -p.cash
        if p.qp - C_ >= 0: break
        u = pa[k] + FEE(pa[k]); xn = (C_ - p.qp) / (1 - u); xm = (p.qo - C_) / u
        if xn <= xm and xn >= 1: p.mark(k); p.trade(k, "opp", "buy", xn)
def H05(p):
    pcs = p.pcost(); c = p.cand(pcs < 1)
    if not len(c): return
    k = int(c[0]); u = p.v["pa"][k] + FEE(p.v["pa"][k]); x = min(p.q0, 0.3 * (p.q0 - p.C0) / u)
    p.mark(k); p.loop(c, "opp", "buy", lambda: x - p.qp)
def H06(p):
    pcs = p.pcost(); c = p.cand(pcs < 1)
    if not len(c): return
    p.mark(int(c[0])); pa = p.v["pa"]
    for k in c:
        k = int(k); u = p.a + FEE(p.a) + pa[k] + FEE(pa[k]); n = sum(1 for th in (1.0, 0.98, 0.96, 0.94) if u < th)
        w = 0.25 * n * p.q0 - p.qp
        if w >= 1: p.trade(k, "opp", "buy", w)
def _stop(p, cap):
    ob = p.v["ob"][p.je + 1:p.kend]; c = p.cand(p.q0 * ob - p.C0 <= -cap)
    if not len(c): return
    p.mark(int(c[0])); pa = p.v["pa"]
    for k in c:
        k = int(k); C_ = -p.cash; vo = p.qp - C_
        if vo >= -cap or p.qo - p.qp < 1: break
        u = pa[k] + FEE(pa[k]); x = (-cap - vo) / (1 - u) if 1 - u > 1e-6 else p.qo - p.qp
        p.trade(k, "opp", "buy", min(x, p.qo - p.qp))
def H07(p): _stop(p, 25.0)
def H08(p): _stop(p, 10.0)
def H09(p):
    k = p.k_m10()
    if k is None: return
    p.mark(k); H04(p, after=k)
    if p.qp < 1: p.notes["infaisable"] = 1
def H10(p):
    k = p.k_m10()
    if k is None: return
    p.mark(k); o, b = p.v["pa"][k], p.v["ob"][k]
    adv = (1 - o - FEE(o)) - (b - FEE(b)); p.notes["adv"] = adv
    if adv > 1e-9: p.notes["branche"] = "acheter l'opposé"; taker_now(p, k, p.q0)
    else: p.notes["branche"] = "vendre"; p.loop(p.rows_from(k), "own", "sell", lambda: p.q0 - p.sell_q)
def H11(p):
    x = sig11(p)
    if x is None: return
    ks, s1, s2, s3 = x; t1, t2, t3 = TH["H11"]
    n = (s1 >= t1).astype(int) + (s2 >= t2).astype(int) + (s3 >= t3).astype(int)
    w = np.where((n >= 2) & (p.T[ks] <= p.end - 2))[0]
    if not len(w): return
    k = int(ks[w[0]]); p.mark(k); taker_now(p, k, 0.25 * p.q0)
def H12(p):
    k = p.k_m10()
    if k is None: return
    p.mark(k); F = feat1(p, k)
    pr = MRISE.predict_proba(Zs(F))[0, 1] if np.all(np.isfinite(F)) else 1.0
    if pr >= TH.get("H12", 0.0): p.notes["branche"] = "immédiat"; taker_now(p, k, p.q0)
    else: p.notes["branche"] = "attendre 3 s"; taker_now(p, int(ge(p.T, p.T[k] + 3)), p.q0)
def _pred(p, H, name):
    k = p.k_m10()
    if k is None: return
    p.mark(k); F = feat1(p, k)
    pr = MD[H].predict_proba(Zs(F))[0, 1] if np.all(np.isfinite(F)) else 0.0
    if pr > TH.get(name, 1.01): p.notes["branche"] = "attendre"; taker_now(p, int(ge(p.T, p.T[k] + H)), p.q0)
    else: p.notes["branche"] = "immédiat"; taker_now(p, k, p.q0)
def H13(p): _pred(p, 1, "H13")
def H14(p): _pred(p, 3, "H14")
def H15(p): _pred(p, 5, "H15")
def H16(p): _pred(p, 10, "H16")
def H17(p):
    k = p.k_m10()
    if k is None: return
    p.mark(k); F = feat1(p, k); o = p.v["pa"][k]
    best = (0.0, None)
    if np.all(np.isfinite(F)):
        for kk in KF:
            pr = MFP[kk].predict_proba(Zs(F))[0, 1]; ev = pr * (kk / 100 + FEE(o) - MAKER_FEE * FEE(o - kk / 100)) - (1 - pr) * MOFF[kk]
            if ev > best[0]: best = (ev, kk)
    if best[1] is None: p.notes["branche"] = "immédiat"; taker_now(p, k, p.q0); return
    tx = min(p.T[k] + 10, p.end - 1); p.notes["branche"] = f"limite −{best[1]} c"
    p.maker(k, o - best[1] / 100, p.q0, tx)
    if p.q0 - p.qp >= 1: taker_now(p, int(ge(p.T, tx)), p.q0)
def H18(p):
    F, _ = feats(p.d, p.v, np.array([p.T[p.sig["i"]]])); F = np.append(F[0], p.v["oa"][p.sig["i"]])
    if not np.all(np.isfinite(F)): return
    pr = M18.predict_proba(((F - MU18) / SD18)[None])[0, 1]
    if pr <= TH.get("H18", 1.01): return
    L = L18(p.a)
    if L < 0.01: return
    p.mark(p.je); p.maker(p.je, L, p.q0, p.end - 5)
def H19(p):
    k = p.k_m10()
    if k is None: return
    p.mark(k); p.maker(k, p.v["pa"][k] - 0.01, p.q0, min(p.T[k] + 10, p.end - 1))
def H20(p):
    k = p.k_m10()
    if k is None: return
    p.mark(k); F = feat1(p, k)
    pr = MFP[1].predict_proba(Zs(F))[0, 1] if np.all(np.isfinite(F)) else 0.0
    if pr > TH.get("H20", 1.01):
        tx = min(p.T[k] + 10, p.end - 1); p.notes["branche"] = "passif"
        p.maker(k, p.v["pa"][k] - 0.01, p.q0, tx)
        if p.q0 - p.qp >= 1: taker_now(p, int(ge(p.T, tx)), p.q0)
    else: p.notes["branche"] = "immédiat"; taker_now(p, k, p.q0)
def H21(p):
    k = p.k_m10()
    if k is None: return
    p.mark(k); T = p.T; pa = p.v["pa"]; i1 = int(ge(T, T[k] - 1))
    ref = float(np.nanmin(pa[i1:k])) if k > i1 else pa[k]
    if pa[k] - ref >= 0.02 - 1e-9:
        p.notes["trou"] = 1; kd = min(int(ge(T, T[k] + 5)), p.kend)
        c = k + 1 + np.where(pa[k + 1:kd + 1] <= ref + 1e-9)[0]
        if len(c): p.notes["recharge"] = 1
        p.loop(c[c < kd], "opp", "buy", lambda: p.q0 - p.qp)
        if p.q0 - p.qp >= 1: taker_now(p, kd, p.q0)
    else: taker_now(p, k, p.q0)
def H22(p):
    k = p.k_m10()
    if k is None: return
    p.mark(k); o = p.v["pa"][k]; tx = min(p.T[k] + 10, p.end - 1)
    taker_now(p, k, 0.5 * p.q0)
    p.maker(k, o - 0.01, p.q0 - p.qp, tx)
    if p.q0 - p.qp >= 1: taker_now(p, int(ge(p.T, tx)), p.q0)
def H23(p):
    pcs = p.pcost(); c = p.cand(pcs < 1)
    if not len(c): return
    p.mark(int(c[0])); p.loop(c, "opp", "buy", lambda: p.q0 - p.qp)
    if p.qp < 1: return
    avg = p.opp_costnf / p.opp_qb; f0r = p.lastfill
    pb = p.v["pb"]; ks = np.arange(f0r + 1, p.kend)
    c2 = ks[pb[ks] >= avg + 0.05 - 1e-9] if len(ks) else ks
    if len(c2): p.notes["revente_possible"] = 1
    p.loop(c2, "opp", "sell", lambda: p.qp)
def H24(p):
    p.capcap = p.C0 + 50.0                           # au plus 50 $ de plus engagés dans le cycle
    pa, oa = p.v["pa"], p.v["oa"]; oe = pa[p.je]; ks = np.arange(p.je + 1, p.kend)
    if not len(ks) or not np.isfinite(oe): return
    m = (pa[ks] <= oe - 0.05 + 1e-9) | (oa[ks] <= p.a - 0.05 + 1e-9)
    c = ks[m]
    if not len(c): return
    p.mark(int(c[0])); nown = 0.0
    for k in c:
        k = int(k)
        n_o = sum(1 for n in range(2) if pa[k] <= oe - 0.05 * (n + 1) + 1e-9)
        w = 0.25 * n_o * p.q0 - p.qp
        if w >= 1: p.trade(k, "opp", "buy", w)
        n_w = sum(1 for n in range(2) if oa[k] <= p.a - 0.05 * (n + 1) + 1e-9)
        w = p.q0 + 0.25 * n_w * p.q0 - p.qo
        w = min(w, 1.5 * p.q0 - (p.qo - p.qp))       # exposition nette ≤ 1,5 × la position d'entrée
        if w >= 1: p.trade(k, "own", "buy", w)
def SELL(p, frac, k):
    if k is None: return
    p.mark(k); p.loop(p.rows_from(k), "own", "sell", lambda: frac * p.q0 - p.sell_q)

HEDGES = {f"H{n:02d}": globals()[f"H{n:02d}"] for n in range(1, 25)}
HNOM = {"H01": "verrouillage paire complète (coût < 1)", "H02": "verrouillage partiel 25 %", "H03": "verrouillage partiel 50 %", "H04": "plancher de profit (les 2 issues ≥ 0)",
        "H05": "réserve jackpot (≥ 70 % gardé)", "H06": "échelle de paires (4 tranches)", "H07": "pire perte limitée à −25 $", "H08": "pire perte limitée à −10 $",
        "H09": "pire issue à 0 dans le budget (après modèle −10)", "H10": "couvrir ou vendre (avantage net)", "H11": "alerte précoce (2 signaux sur 3) 25 %",
        "H12": "horloge de risque (immédiat / attendre 3 s)", "H13": "prédictive 1 s", "H14": "prédictive 3 s", "H15": "prédictive 5 s", "H16": "prédictive 10 s",
        "H17": "premier passage (limite si EV > immédiat)", "H18": "fenêtre de conversion prédite (paire ≤ 0,95) — inactive si seuil appris = jamais", "H19": "sauvetage passif (vendeur − 1 c, 10 s)",
        "H20": "prédicteur de file (traversée) passif sinon immédiat", "H21": "recharge du carnet", "H22": "hybride 50 % immédiat + 50 % passif",
        "H23": "boomerang (revente de l'opposé +5 c)", "H24": "moteur d'inventaire deux jambes"}
TRIGN = {**{h: "paire < 1" for h in ("H01", "H02", "H03", "H04", "H05", "H06", "H23")}, "H07": "perte latente −25 $", "H08": "perte latente −10 $",
         **{h: "modèle −10" for h in ("H09", "H10", "H12", "H13", "H14", "H15", "H16", "H17", "H19", "H20", "H21", "H22")}, "H11": "2 alertes sur 3",
         "H18": "à l'entrée (prédiction)", "H24": "oscillation ±5 c"}
NONTEST = {"H20": "partiellement : la vraie position dans la file n'est pas observable (aucun événement d'ordre individuel) ; testé seulement comme prédicteur de « traversée » du prix",
           "H21": "partiellement : recharge mesurée sur les lignes 0,3 s (meilleur niveau) ; à 100 ms seulement dans les photos (~20 s par cycle)"}

# ================================================================ simulation
def sim(st, sig, sc, pol, budget=50.0, bank=float("inf"), k_sell=None):
    p = Pos(st, sig, sc, budget, bank)
    if not p.ok: return p
    if pol == "HOLD": pass
    elif pol in ("SELL50", "SELL100"): SELL(p, 0.5 if pol == "SELL50" else 1.0, k_sell)
    else: HEDGES[pol](p)
    return p
def rec(p, per):
    if not p.ok: return dict(st=p.st, per=per, ok=False, why=p.why)
    pr = min(p.qo, p.qp)
    lk = pr * (1 - p.own_cost / p.own_qb - p.opp_cost / p.opp_qb) if pr >= 1 and p.opp_qb > 0 else 0.0
    ex = p.opp_qb >= 1 or p.sell_q >= 1 or p.own_qb > p.q0 + 1e-6
    return dict(st=p.st, per=per, ok=True, pnl=p.pnl(), stake=p.C0, q0=p.q0, att=p.att, exe=ex, oppq=p.opp_qb, oppnf=p.opp_costnf, sellq=p.sell_q,
                cov=(p.opp_qb + p.sell_q) / p.q0, pairs=pr, locked=lk, worst=p.worst(), best=p.best(), peak=p.peak, rejh=p.rejh, trig=p.trig,
                net=(p.qo - p.qp) / p.q0, notes=dict(p.notes), budget=p.budget, w=p.w, a=p.a)
def run_indep(coh, sc, pol, per=None, ksell=None):
    out = {}
    for st in sorted(COH[coh]):
        if per and PER(st) != per: continue
        out[st] = rec(sim(st, COH[coh][st], sc, pol, k_sell=(ksell or {}).get(st)), PER(st))
    return out
def run_cap(coh, sc, pol, per, ksell=None):
    """portefeuille partagé de 250 $, chronologique ; une position à la fois (un signal par cycle, cycles successifs)"""
    bank = BANK0; out = {}; nred = nrej = 0
    for st in sorted(COH[coh]):
        if PER(st) != per: continue
        budget = min(50.0, bank)
        if budget < 50 - 1e-9: nred += 1
        if budget < 1: nrej += 1; out[st] = dict(st=st, per=per, ok=False, why="capital"); continue
        p = sim(st, COH[coh][st], sc, pol, budget=budget, bank=bank, k_sell=(ksell or {}).get(st))
        r = rec(p, per); out[st] = r
        if r["ok"]: bank += r["pnl"]
        elif r.get("why") == "capital": nrej += 1
    return out, nred, nrej

# ---------------- seuils appris sur l'apprentissage (scénario prudent, version indépendante, 3 cohortes réunies)
GRID = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5, 0.6, 0.8, 1.01]
TH_GRID = {}
def choisir(name):
    best = None; TH_GRID[name] = {}
    for th in GRID:
        TH[name] = th; tot = 0.0
        for coh in COH:
            for st, s in COH[coh].items():
                if PER(st) != "apprentissage": continue
                p = sim(st, s, "prudent", name)
                if p.ok: tot += p.pnl()
        TH_GRID[name][th] = tot
        if best is None or tot > best[1] + 1e-9: best = (th, tot)
    TH[name] = best[0]; return best
TH["H12"] = 0.0
for nm in ("H12", "H13", "H14", "H15", "H16", "H18", "H20"): choisir(nm)
print("seuils (apprentissage)", TH, f"{_time.time() - _T0:.0f} s", flush=True)

# ---------------- toutes les simulations
POLS = ["HOLD"] + list(HEDGES)
RI, RC, NRC = {}, {}, {}
for coh in COH:
    for sc in SCN:
        for pol in POLS: RI[(coh, sc, pol)] = run_indep(coh, sc, pol)
        for h in HEDGES:
            ks = {st: r.get("trig") for st, r in RI[(coh, sc, h)].items() if r["ok"]}
            for sp in ("SELL50", "SELL100"): RI[(coh, sc, h, sp)] = run_indep(coh, sc, sp, ksell=ks)
        for per in PERS:
            for pol in POLS:
                r_, a_, b_ = run_cap(coh, sc, pol, per); RC[(coh, sc, pol, per)] = r_; NRC[(coh, sc, pol, per)] = (a_, b_)
            for h in HEDGES:
                ks = {st: r.get("trig") for st, r in RI[(coh, sc, h)].items() if r["ok"]}
                for sp in ("SELL50", "SELL100"):
                    r_, a_, b_ = run_cap(coh, sc, sp, per, ksell=ks); RC[(coh, sc, h, sp, per)] = r_; NRC[(coh, sc, h, sp, per)] = (a_, b_)
        print("simulé", coh, sc, f"{_time.time() - _T0:.0f} s", flush=True)

# ================================================================ statistiques
def blocs(diffs, per):
    H_ = collections.defaultdict(float)
    for st in CYC[per]: H_[st // 3600] += 0.0
    for st, x in diffs.items(): H_[st // 3600] += x
    hv = np.array(list(H_.values())); sims = hv[RNG.integers(0, len(hv), (2000, len(hv)))].sum(1)
    return np.percentile(sims, [5, 95])
def stats(R, Rh, per, Rs50=None, Rs100=None):
    L = [R[st] for st in sorted(R) if R[st]["per"] == per and R[st]["ok"]]
    Lh = {st: r for st, r in Rh.items() if r["per"] == per and r["ok"]}
    pn = np.array([x["pnl"] for x in L]) if L else np.zeros(0)
    tot = float(pn.sum()); toth = sum(r["pnl"] for r in Lh.values())
    diffs = collections.defaultdict(float)
    for x in L: diffs[x["st"]] += x["pnl"]
    for st, r in Lh.items(): diffs[st] -= r["pnl"]
    lo, hi = blocs(diffs, per)
    cum = np.cumsum(pn) if len(pn) else np.zeros(1)
    dd = float(min(0.0, np.min(cum - np.maximum.accumulate(np.concatenate([[0], cum]))[1:]))) if len(pn) else 0.0
    streak = mx = 0
    for v_ in pn:
        streak = streak + 1 if v_ < 0 else 0; mx = max(mx, streak)
    att = [x for x in L if x["att"]]; exe = [x for x in L if x["exe"]]
    oq = sum(x["oppq"] for x in L); onf = sum(x["oppnf"] for x in L)
    jk = [st for st, r in Lh.items() if r["pnl"] >= 4 * r["stake"]]
    Rd = {x["st"]: x for x in L}
    kept = sum(1 for st in jk if st in Rd and Rd[st]["pnl"] >= 4 * Rd[st]["stake"])
    sac = sum(Lh[st]["pnl"] - Rd[st]["pnl"] for st in jk if st in Rd)
    s_ = lambda R2: (sum(r["pnl"] for r in R2.values() if r["per"] == per and r["ok"]) if R2 is not None else float("nan"))
    return dict(n=len(L), att=len(att), exe=len(exe), fr=(len(exe) / len(att) if att else float("nan")), px=(onf / oq if oq >= 1 else float("nan")),
                cov=(float(np.mean([x["cov"] for x in exe])) if exe else float("nan")), pnl=tot, d=tot - toth, lo=lo, hi=hi, dd=dd,
                maxloss=float(pn.min()) if len(pn) else 0.0, streak=mx, jk=len(jk), kept=kept, sac=sac, locked=sum(x["locked"] for x in L),
                unc=sum(x["pnl"] for x in L if not x["exe"]), peak=max([x["peak"] for x in L], default=0.0), rejh=sum(x["rejh"] for x in L),
                worst=float(np.mean([x["worst"] for x in L])) if L else float("nan"), best=float(np.mean([x["best"] for x in L])) if L else float("nan"),
                net=float(np.mean([x["net"] for x in L])) if L else float("nan"), npairs=sum(1 for x in L if x["pairs"] >= 1),
                d50=tot - s_(Rs50), d100=tot - s_(Rs100), hold=toth)
ST = {}
for coh in COH:
    for sc in SCN:
        for per in PERS:
            Rh = RC[(coh, sc, "HOLD", per)]
            ST[("cap", coh, sc, "HOLD", per)] = stats(Rh, Rh, per)
            ST[("ind", coh, sc, "HOLD", per)] = stats(RI[(coh, sc, "HOLD")], RI[(coh, sc, "HOLD")], per)
            for h in HEDGES:
                ST[("cap", coh, sc, h, per)] = stats(RC[(coh, sc, h, per)], Rh, per, RC[(coh, sc, h, "SELL50", per)], RC[(coh, sc, h, "SELL100", per)])
                ST[("ind", coh, sc, h, per)] = stats(RI[(coh, sc, h)], RI[(coh, sc, "HOLD")], per, RI[(coh, sc, h, "SELL50")], RI[(coh, sc, h, "SELL100")])
print("statistiques", f"{_time.time() - _T0:.0f} s", flush=True)

# ================================================================ diagnostics d'audit
def audit_lignes():
    T = np.array(sorted(r[0] for st in valides for r in C[st])); dt = np.diff(T)
    return len(T), np.percentile(dt, [5, 50, 95, 99])
NROW, DTQ = audit_lignes()
MIR = [0, 0]
for st in valides:
    d = arr(st); ok = np.isfinite(d["UB"]) & np.isfinite(d["DA"])
    MIR[0] += int(ok.sum()); MIR[1] += int((ok & (np.abs(d["DA"] - (1 - d["UB"])) < 1e-9) & (np.abs(d["DAZ"] - d["UBZ"]) < 1e-6)).sum())
LEADN = len(LEAD); LEADT = (min(LEAD), max(LEAD))
_lt = [t for st in LEAD for (t, _) in LEAD[st]]
_lflux = np.array([sum(x[1][4][4:6]) + sum(x[1][5][4:6]) for st in LEAD for x in LEAD[st] if x[1][4] and x[1][5]])
SIGT = (min(SIGF), max(SIGF)); _sf = np.array([v_[1] + v_[0] for v_ in SIGF.values()])
TW = json.load(open("bot95/twap_carnets.json")); TWT = (min(x["t0"] for x in TW), max(x["t0"] for x in TW))
RAP = json.load(open("bot95/rapide.json"))
# file d'attente : ordres passifs H19 (scénario prudent, cohortes A+B, validation + test) — règle « traversée » contre flux agrégé 1 s et 100 ms
def diag_file():
    out = dict(n=0, touche=0, traverse=0, traverse2=0, flux1s_v=0, flux1s_tous=0, n100=0, tr100=0, fl100=0)
    for coh in ("A", "B"):
        for st, s in COH[coh].items():
            if PER(st) == "apprentissage": continue
            p = Pos(st, s, "prudent")
            if not p.ok: continue
            k = p.k_m10()
            if k is None: continue
            j = p.row(k)
            if j is None: continue
            T = p.T; pa, paz, pb, pbz = p.v["pa"], p.v["paz"], p.v["pb"], p.v["pbz"]
            L = round(pa[k] - 0.01, 2); tx = min(T[k] + 10, p.end - 1); m1 = int(le(T, tx))
            if m1 <= j or L < 0.01: continue
            seg = pa[j + 1:m1 + 1]; out["n"] += 1
            out["touche"] += bool((seg <= L + 1e-9).any()); out["traverse"] += bool((seg <= L - 0.01 + 1e-9).any())
            c = pa[j + 1:m1 + 2] <= L - 0.01 + 1e-9; out["traverse2"] += bool((c[:-1] & c[1:]).any()) if len(c) > 1 else False
            ahead = (pbz[j] if abs(pb[j] - L) < 1e-9 else (0.0 if pb[j] < L - 1e-9 else pbz[j] * 2)) + p.q0       # volume à écouler avant d'être servi entièrement
            up_opp = not s["up"]
            sv = [SIGF.get(int(t_)) for t_ in range(int(T[j]) + 1, int(tx) + 1)]
            if all(x is not None for x in sv) and sv:
                vend = sum((x[1] if up_opp else x[3]) for x in sv) / L
                tous = sum((x[1] + x[0]) if up_opp else (x[3] + x[2]) for x in sv) / L
                out["flux1s_v"] += vend >= ahead; out["flux1s_tous"] += tous >= ahead
            if st in LEAD:
                lt = np.array([t_ for t_, _ in LEAD[st]])
                if lt[0] <= T[j] and lt[-1] >= tx:
                    out["n100"] += 1; fl = 0.0; tr = False
                    for t_, x in LEAD[st]:
                        if T[j] < t_ <= tx:
                            asks = x[0] if up_opp else x[1]; fx = x[4] if up_opp else x[5]
                            if asks and asks[0][0] <= L - 0.01 + 1e-9: tr = True
                            if fx: fl += fx[5] / L
                    out["tr100"] += tr; out["fl100"] += fl >= ahead
    return out
DF = diag_file()
# H21 à 100 ms : après un saut ≥ 2 c du meilleur vendeur (photos), le prix revient-il au niveau d'avant en 0,5 / 1 / 2 / 5 s ?
def diag_recharge():
    n = 0; back = collections.Counter()
    for st, L_ in LEAD.items():
        t = np.array([x[0] for x in L_])
        for side in (0, 1):
            a = np.array([(x[1][side][0][0] if x[1][side] else np.nan) for x in L_])
            for i in range(10, len(a)):
                if not np.isfinite(a[i]) or not np.isfinite(a[i - 1]) or a[i] - a[i - 1] < 0.02 - 1e-9: continue
                if t[-1] < t[i] + 5: continue
                n += 1; ref = a[i - 1]
                for H in (0.5, 1, 2, 5):
                    w = (t > t[i]) & (t <= t[i] + H)
                    if np.any(a[w] <= ref + 1e-9): back[H] += 1
    return n, back
NREC, BACK = diag_recharge()
print("diagnostics", f"{_time.time() - _T0:.0f} s", flush=True)

# ================================================================ rédaction
f0s = lambda x: f0(x) if x == x else "—"
def ci(s): return f"**{f0(s['d'])}** [{f0(s['lo'])} ; {f0(s['hi'])}]"
def ligne_full(h, s, nr):
    nm = "GARDER (référence)" if h == "HOLD" else f"{h} {HNOM[h]}"
    if h == "HOLD":
        return (f"| {nm} | {s['n']} | — | — | — | — | — | {f0(s['pnl'])} | 0 | — | — | {f0(s['dd'])} | {f0(s['maxloss'])} | {s['streak']} | {s['kept']}/{s['jk']} | 0 $ | 0 $ | "
                f"{f0(s['unc'])} | {f0(s['peak'])} | {nr[0]}/{nr[1]} |")
    return (f"| {nm} | {s['n']} | {s['att']} | {s['exe']} | {pc(s['fr'])} | {f2(s['px'])} | {pc(s['cov'])} | {f0(s['pnl'])} | {ci(s)} | {f0s(s['d50'])} | {f0s(s['d100'])} | "
            f"{f0(s['dd'])} | {f0(s['maxloss'])} | {s['streak']} | {s['kept']}/{s['jk']} | {f0(s['sac'])} | {f0(s['locked'])} | {f0(s['unc'])} | {f0(s['peak'])} | {nr[0]}/{nr[1]} |")
HDRF = ("| Couverture | Positions | Tentées | Exécutées | Taux d'exécution | Prix moyen opposé | Quantité couverte moy. | P&L net | Δ vs GARDER [IC 90 %] | Δ vs VENDRE 50 % | Δ vs VENDRE 100 % "
        "| Creux max | Perte max (1 position) | Plus longue série perdante | Jackpots gardés | Profit sacrifié (jackpots) | Profit verrouillé (paires) | P&L des positions non couvertes "
        "| Capital immobilisé max | Entrées réduites / refusées |\n" + "|---" * 20 + "|")
rank = {}
for coh in ("A", "B", "C"):
    rank[coh] = sorted(HEDGES, key=lambda h: -ST[("cap", coh, "prudent", h, "validation")]["d"])

out = ["# BOT95 HEDGE LAB V1 — 24 couvertures contre GARDER, deux cohortes, trois scénarios d'exécution", "",
       f"Étude hors ligne du {_time.strftime('%d.%m.%Y')} — aucun bot, aucun workflow, aucun fichier du bot modifié ; rien n'est publié. " + ENTETE.replace(" — le test est minuscule, aucun verdict ne peut s'y appuyer seul.", "."), ""]
VERD = len(out)

# ---------------- AUDIT
out += ["## 1. Audit des données et de la simulation « teneur d'ordre » (maker)", "",
        "| Donnée | État | Période | Résolution / détail |", "|---|---|---|---|",
        f"| Carnets Up + Down synchronisés (même ligne) | **disponible** | {hs(valides[0])} → {hs(valides[-1] + 300)} | {NROW} lignes ; intervalle 5 % {f2(DTQ[0])} s · médiane {f2(DTQ[1])} s · 95 % {f2(DTQ[2])} s · 99 % {f2(DTQ[3])} s. Up et Down sont dans la MÊME ligne (même horodatage de réception). |",
        f"| Meilleur acheteur / meilleur vendeur | **disponible** | idem | r[3]-r[6], à chaque ligne. Carnets **miroirs** : vendeur Down = 1 − acheteur Up et même taille sur {pc(MIR[1] / MIR[0])} des {MIR[0]} lignes vérifiées (miroir fait par Polymarket ou par l'enregistreur : non distinguable ; toutes les couvertures en dépendent). |",
        "| Quantité au meilleur niveau | **disponible** | idem | r[7]-r[10] (parts). |",
        f"| Profondeur par niveau | **partielle** | photos 100 ms : {LEADN} cycles, {hs(LEADT[0])} → {hs(LEADT[1] + 300)} ; carnets 8 niveaux : {len(TW)} signaux TWAP, {hs(TWT[0])} → {hs(TWT[1])} | 3 meilleurs niveaux des deux côtés seulement dans les photos 100 ms (~10 s avant → 10 s après le premier désaccord de chaque cycle) ; 8 niveaux seulement aux signaux TWAP (autres stratégies). Au-delà du meilleur niveau : **absent** pour nos positions. |",
        f"| Transactions et annulations | **partielles (agrégées)** | flux 1 s : {hs(SIGT[0])} → {hs(SIGT[1])} (sig_BTC) ; flux 100 ms : photos | Sommes en $ par jeton et par intervalle : retraits / ajouts côté acheteur et vendeur, échanges côté « achat » et « vente » (côté du message last_trade_price). **Ni prix, ni taille individuelle, ni identité de l'ordre**. On peut en déduire : qu'il y a eu des échanges (et combien de $) dans la seconde ou les 100 ms ; si un niveau a été vidé par des retraits plutôt que par des échanges. On ne peut PAS en déduire : à quel prix l'échange a eu lieu, s'il a touché NOTRE niveau, la position dans la file, ni si un ordre précis a été servi. Seulement {pc((_sf > 0).mean())} des secondes ont un échange côté Up (médiane des secondes non nulles : {np.median(_sf[_sf > 0]):.0f} $) ; photos 100 ms : {pc((_lflux > 0).mean())} des pas ont un échange. |",
        "| Horodatage de réception local | **disponible** | tout | heure de réception par le bot (Cloudflare), pour toutes les sources. |",
        "| Horodatage de l'échange (bourse / Polymarket) | **absent** | — | non enregistré dans les lignes ; impossible de séparer latence réseau et mouvement réel. |",
        "| Frais preneur | **connus** | — | 0,072 · p · (1 − p) par part, à l'achat ET à la vente au meilleur acheteur (symétrique : identique pour p et 1 − p). |",
        "| Frais teneur d'ordre | **non vérifiés** | — | supposés 0 (hypothèse de Pitch) ; non vérifiés sur les marchés crypto 5 min. |",
        "| Remplissages initiaux (exécution réelle) | **absents** | — | les fantômes réels « achètent » au prix vu ; aucun remplissage réel sur le carnet. |",
        "| Résultats officiels | **disponibles** | 1146 cycles | officiels.json (cycles sans résultat exclus). |",
        "| Fusion Up + Down → 1 $ (merge) | **non observable** | — | transaction on-chain CTF, absente des données ; comptée 1 $ au règlement ; capital libéré plus tôt seulement dans le scénario idéal. |",
        "| Historique des prix des bourses | **disponible** | tout | Bybit, OKX, Coinbase, Binance, Chainlink à chaque ligne 0,3 s (100 ms dans les photos ; changements réels tous les ~0,4-0,9 s). |",
        "| Probabilités du modèle corrigé (0,015 %) | **reconstruites** | tout | X15 = modèle reconstruit (méthode X d'attribution_001, sdRel = 1,5e-4) ; le fantôme réel calcule H15 (moteur du bot, même sdRel) ; accord ci-dessous. |",
        f"| Latence VPS Dublin (bot95/rapide.json) | **pas encore** | — | fichier présent mais vide ({len(RAP.get('signaux') or [])} signal, état {RAP.get('etat')}). |", ""]
acc = ACC
out += [f"**Accord de la cohorte B avec le fantôme réel « corrige : V2-F ecart qui grandit » BTC** (cycles réglés {hs(ACC_LO)} → {hs(ACC_HI)}) :", "",
        "| Reconstruction | Cycles de la période | Achats fantôme réel | Achats rejeu | Cycles communs | Même côté | Même côté à 1 s près | Décalage médian (rejeu − réel) |", "|---|---|---|---|---|---|---|---|"]
for nm, a_ in acc.items():
    out.append(f"| {nm} | {a_['ncyc']} | {a_['nlive']} | {a_['nrep']} | {a_['both']} | {a_['same']} | {a_['near']} | {f2(a_['med'])} s |")
out += ["", "La cohorte B (X15, définition imposée) ne recoupe le fantôme réel qu'en partie : le fantôme réel déclenche dans plus de cycles et souvent à un autre instant ; le moteur du bot ramené à 0,015 % (H15) est plus proche. "
        "B est donc une **simulation** de la règle corrigée, pas le relevé du fantôme réel.", ""]
out += ["### Une simulation « teneur d'ordre » crédible est-elle possible ? **Non — seulement des bornes.**", "",
        "- La position dans la file n'est **pas observable** (aucun événement d'ordre individuel, seulement des sommes agrégées). "
        "Les échanges sont petits (voir ci-dessus) : la plupart des mouvements du meilleur niveau viennent d'ajouts / retraits de teneurs d'ordre, pas d'échanges.",
        "- Modèle de file **pessimiste** utilisé (nous sommes DERNIERS dans la file) : l'ordre passif d'achat du côté opposé à L n'est rempli que si le meilleur vendeur opposé passe **strictement sous L** (≤ L − 1 c) sur une ligne "
        "(prudent), pour la taille affichée de cette ligne ; pessimiste : il doit y rester au moins 2 lignes de suite, moitié de la taille. Idéal (borne haute, jamais atteignable) : rempli dès que le vendeur touche L, quantité entière.",
        "- Variante « file agrégée » (diagnostic seulement, étiquetée) : rempli si la somme des échanges du jeton opposé pendant la vie de l'ordre ≥ (taille affichée devant nous + notre quantité). "
        "Elle surestime : les échanges agrégés peuvent avoir eu lieu à d'autres prix que le nôtre.", "",
        f"Ordres passifs « sauvetage » (vendeur opposé − 1 c, 10 s, au déclencheur modèle −10 ; cohortes A + B, validation + test ; {DF['n']} ordres) — part qui aurait été remplie :", "",
        "| Règle | Ordres | Remplis |", "|---|---|---|",
        f"| idéal : le vendeur touche notre prix | {DF['n']} | {pc(DF['touche'] / max(1, DF['n']))} |",
        f"| prudent : le vendeur passe 1 c sous notre prix | {DF['n']} | {pc(DF['traverse'] / max(1, DF['n']))} |",
        f"| pessimiste : 1 c sous notre prix, 2 lignes de suite | {DF['n']} | {pc(DF['traverse2'] / max(1, DF['n']))} |",
        f"| file agrégée 1 s (échanges « vente » du jeton opposé ≥ file + nous) | {DF['n']} | {pc(DF['flux1s_v'] / max(1, DF['n']))} |",
        f"| file agrégée 1 s (tous échanges du jeton opposé) — borne très optimiste | {DF['n']} | {pc(DF['flux1s_tous'] / max(1, DF['n']))} |",
        f"| sous-ensemble couvert par une photo 100 ms : traversée à 100 ms | {DF['n100']} | {pc(DF['tr100'] / max(1, DF['n100']))} |",
        f"| sous-ensemble photo 100 ms : file agrégée 100 ms (échanges « vente ») | {DF['n100']} | {pc(DF['fl100'] / max(1, DF['n100']))} |", "",
        "L'écart entre ces lignes EST l'incertitude sur le remplissage passif : aucune n'est une mesure. Tous les résultats « passifs » ci-dessous sont donnés pour les trois scénarios ; seul le prudent sert au classement.", ""]

# ---------------- définitions
out += ["## 2. Définitions (fixées avant les calculs)", "",
        "**Entrées** (inchangées, identiques pour GARDER et pour chaque couverture) : premier signal du cycle, achat au seul meilleur vendeur, quantité affichée, au plus 50 $ frais compris "
        "(scénario prudent : décision exécutée sur la première ligne ≥ signal + 0,3 s, au prix vu ou mieux, sinon pas d'entrée ; pessimiste : + 0,6 s et moitié de la quantité affichée ; idéal : 0 s).", "",
        "- **A · désaccord 30 zone + modèle monte** : > 60 s restantes, vendeur de notre côté dans [0,15 ; 0,35), modèle du bot (r[2]) − vendeur ≥ 0,30, modèle de notre côté monté d'au moins 3 c en 3 s.",
        "- **B · V2-F corrigé 0,015 %** : vendeur 0,03-0,97, écart ≥ 0,20 qui a grandi d'au moins 3 c en 3 s, avec le modèle reconstruit à sdRel = 1,5e-4.",
        "- **C · V2-F original** (diagnostic) : même règle avec r[2].", "",
        "| Cohorte | apprentissage | validation | test inédit |", "|---|---|---|---|"]
for coh in COH: out.append(f"| {COHN[coh]} | " + " | ".join(str(sum(1 for st in COH[coh] if PER(st) == per)) for per in PERS) + " |")
out += ["", "**Scénarios d'exécution** (frais preneur sur chaque achat / vente au marché) :", "",
        "- **idéal** (borne haute, JAMAIS atteignable) : délai 0, meilleur niveau disponible en quantité illimitée pour les couvertures, ordre passif rempli dès que le prix touche, fusion des paires (capital libéré tout de suite).",
        "- **prudent** (classement) : délai 0,3 s, quantité affichée de la ligne d'exécution, ordre passif rempli seulement sur traversée (vendeur ≤ limite − 1 c).",
        "- **pessimiste** : délai 0,6 s, moitié de la quantité affichée, ordre passif seulement si la traversée dure ≥ 2 lignes.",
        "- Ordre preneur = ordre à cours limité au prix vu à la décision, exécuté sur la ligne décision + délai ; s'il est parti, la couverture réessaie à la ligne suivante au nouveau prix tant que sa condition tient.", "",
        "**Capital** : un portefeuille de 250 $ par cohorte et par période, rejoué dans l'ordre chronologique. Un signal par cycle et des cycles successifs : une seule position ouverte à la fois. "
        "Entrée ≤ min(50 $, capital) ; chaque couverture doit tenir dans le capital libre (capital − argent engagé − ordres passifs posés), sinon elle est réduite (comptée). "
        "Le capital revient au règlement (fusion anticipée seulement en idéal). Classement sur cette version ; la version « 50 $ indépendants » (capital illimité) est donnée à côté.", "",
        "**Déclencheurs** : *modèle −10* = première ligne où le modèle de la cohorte, de notre côté, est ≥ 10 points sous sa valeur au signal (≥ 2 s avant la fin) ; *paire < 1* = prix d'entrée + frais + vendeur opposé + frais < 1 ; "
        "*perte latente* = parts × meilleur acheteur de notre côté − coût ≤ −25 $ / −10 $.", "",
        "| Couverture | Déclencheur | Règle |", "|---|---|---|"]
REGLE = {"H01": "achète l'opposé jusqu'à autant de parts que la position, tant que la paire coûte < 1", "H02": "idem jusqu'à 25 % de la position", "H03": "idem jusqu'à 50 %",
         "H04": "plus petite quantité opposée qui rend les deux issues ≥ 0 (si le carnet et le capital le permettent)", "H05": "x = min(position, 0,3 × jackpot théorique / coût unitaire) : garde ≥ 70 % du jackpot, la pire issue s'améliore",
         "H06": "tranches de 25 % quand la paire coûte < 1,00 / 0,98 / 0,96 / 0,94", "H07": "achète l'opposé pour que la pire issue ≥ −25 $ (au plus la paire complète)", "H08": "idem −10 $",
         "H09": "après modèle −10 : rend la pire issue ≥ 0 si c'est faisable dans le budget (sinon rien — « infaisable »)",
         "H10": "avantage net = (1 − vendeur opposé − frais) − (acheteur de notre côté − frais) ; > 0 → acheter l'opposé, sinon vendre la position au meilleur acheteur",
         "H11": "2 des 3 alertes sur 3 s (baisse du modèle, perp contre nous, acheteur de notre côté qui baisse ; seuils = 90e centile de l'apprentissage) → opposé 25 %",
         "H12": "P(vendeur opposé + 2 c en 3 s) ≥ seuil → immédiat, sinon attendre 3 s puis acheter", "H13": "P(baisse ≥ 1 c en 1 s) > seuil → attendre 1 s, sinon immédiat",
         "H14": "idem 3 s", "H15": "idem 5 s", "H16": "idem 10 s",
         "H17": "pour k = 1, 2, 3, 5 c : EV = P(traversée de vendeur − k en 10 s) × (k + frais évités) − (1 − P) × hausse moyenne si non rempli (app.) ; meilleure EV > 0 → ordre passif 10 s puis immédiat, sinon immédiat",
         "H18": "à l'entrée : P(paire ≤ 0,95 frais compris avant la fin) > seuil → ordre passif opposé au prix qui fait 0,95, jusqu'à la fin − 5 s",
         "H19": "ordre passif opposé à vendeur − 1 c pendant 10 s, pas de repli", "H20": "P(traversée de vendeur − 1 c en 10 s) > seuil → passif 10 s puis immédiat, sinon immédiat",
         "H21": "si le vendeur opposé vient de sauter ≥ 2 c (dernière seconde) : attendre ≤ 5 s qu'il revienne au niveau d'avant, sinon immédiat ; pas de saut → immédiat",
         "H22": "50 % immédiat + 50 % passif à vendeur − 1 c (10 s), puis immédiat", "H23": "comme H01, puis revend l'opposé au meilleur acheteur s'il monte de 5 c (garde la 1re jambe)",
         "H24": "achète 25 % d'opposé à chaque baisse de 5 c du vendeur opposé (2 tranches) et 25 % de notre côté à chaque baisse de 5 c de notre vendeur (2 tranches) ; ≤ 50 $ de plus, exposition nette ≤ 1,5 ×"}
for h in HEDGES: out.append(f"| {h} {HNOM[h]} | {TRIGN[h]} | {REGLE[h]} |")
out += ["", "**Comparaisons** : VENDRE 50 % / 100 % = vente de la première jambe au meilleur acheteur au MÊME instant que le premier déclenchement de la couverture (mêmes délais, mêmes frais). "
        "Toutes les positions comptent dans tous les totaux, couvertes ou non. Jackpot = gain ≥ 4 × la mise en gardant.", "",
        "**Appris sur l'apprentissage seulement** (scénario prudent, 3 cohortes réunies) : " + " ; ".join(f"{k} seuil {f2(v_)}" for k, v_ in TH.items() if k != "H11")
        + f" ; H11 seuils : baisse du modèle {f3(TH['H11'][0])}, perp contre nous {TH['H11'][1] * 1e4:.1f} pb, acheteur qui baisse {f3(TH['H11'][2])}. Seuil 1,01 = « jamais » (la règle retombe sur l'immédiat).", "",
        "Grille des seuils (Σ P&L apprentissage, prudent, 3 cohortes) : " + " · ".join(f"{nm} : " + ", ".join(f"{f2(th)} → {f0(v_)}" for th, v_ in g_.items()) for nm, g_ in TH_GRID.items()) + ".", "",
        "Qualité des modèles figés (AUC) : " + " · ".join(f"{per} : " + ", ".join(f"{k} {f2(v_)}" for k, v_ in AUCS[per].items()) for per in PER2) + ".", ""]

# ---------------- classement
rank_i = {coh: sorted(HEDGES, key=lambda h: -ST[("ind", coh, "prudent", h, "validation")]["d"]) for coh in COH}
def ruine(coh, sc, pol, per):
    R = RC[(coh, sc, pol, per)]; nb = sum(1 for r in R.values() if r["ok"]); rf = sum(1 for r in R.values() if not r["ok"] and r.get("why") == "capital")
    return nb, rf
def classement(coh):
    o = [f"### {COHN[coh]} — portefeuille 250 $ (classement imposé)", "",
         "| Rang | Couverture | Δ vs GARDER valid. prudent [IC 90 %] | positions jouées / refusées faute de capital (valid.) | Δ test prudent [IC 90 %] | positions jouées / refusées (test) | valid. idéal | valid. pessimiste | test idéal | test pessimiste | Jackpots gardés valid. |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    for n, h in enumerate(rank[coh], 1):
        v_, t_ = ST[("cap", coh, "prudent", h, "validation")], ST[("cap", coh, "prudent", h, "inédit")]
        rv, rt = ruine(coh, "prudent", h, "validation"), ruine(coh, "prudent", h, "inédit")
        o.append(f"| {n} | {h} {HNOM[h]} | {ci(v_)} | {rv[0]} / {rv[1]} | {ci(t_)} | {rt[0]} / {rt[1]} | {f0(ST[('cap', coh, 'idéal', h, 'validation')]['d'])} | {f0(ST[('cap', coh, 'pessimiste', h, 'validation')]['d'])} | "
                 f"{f0(ST[('cap', coh, 'idéal', h, 'inédit')]['d'])} | {f0(ST[('cap', coh, 'pessimiste', h, 'inédit')]['d'])} | {v_['kept']}/{v_['jk']} |")
    hv, ht = ST[("cap", coh, "prudent", "HOLD", "validation")], ST[("cap", coh, "prudent", "HOLD", "inédit")]
    rv, rt = ruine(coh, "prudent", "HOLD", "validation"), ruine(coh, "prudent", "HOLD", "inédit")
    o += ["", f"Référence GARDER (prudent, 250 $) : validation {rv[0]} positions jouées, {rv[1]} refusées faute de capital, {f0(hv['pnl'])}, creux {f0(hv['dd'])} · "
          f"test {rt[0]} jouées, {rt[1]} refusées, {f0(ht['pnl'])}, creux {f0(ht['dd'])}.", ""]
    o += [f"### {COHN[coh]} — 50 $ indépendants (chaque position seule, capital illimité ; informatif)", "",
          "| Rang | Couverture | Δ vs GARDER valid. prudent [IC 90 %] | Δ test prudent [IC 90 %] | Δ app. prudent | valid. idéal | valid. pessimiste | test idéal | test pessimiste | Δ vs VENDRE 50 % (valid. / test) | Δ vs VENDRE 100 % (valid. / test) | Jackpots gardés (valid.) | Profit sacrifié jackpots (valid.) |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for n, h in enumerate(rank_i[coh], 1):
        v_, t_ = ST[("ind", coh, "prudent", h, "validation")], ST[("ind", coh, "prudent", h, "inédit")]
        o.append(f"| {n} | {h} {HNOM[h]} | {ci(v_)} | {ci(t_)} | {f0(ST[('ind', coh, 'prudent', h, 'apprentissage')]['d'])} | {f0(ST[('ind', coh, 'idéal', h, 'validation')]['d'])} | "
                 f"{f0(ST[('ind', coh, 'pessimiste', h, 'validation')]['d'])} | {f0(ST[('ind', coh, 'idéal', h, 'inédit')]['d'])} | {f0(ST[('ind', coh, 'pessimiste', h, 'inédit')]['d'])} | "
                 f"{f0s(v_['d50'])} / {f0s(t_['d50'])} | {f0s(v_['d100'])} / {f0s(t_['d100'])} | {v_['kept']}/{v_['jk']} | {f0(v_['sac'])} |")
    hv, ht = ST[("ind", coh, "prudent", "HOLD", "validation")], ST[("ind", coh, "prudent", "HOLD", "inédit")]
    hi_, hp_ = ST[("ind", coh, "idéal", "HOLD", "validation")], ST[("ind", coh, "pessimiste", "HOLD", "validation")]
    o += ["", f"Référence GARDER (50 $ indépendants) : validation prudent {hv['n']} positions {f0(hv['pnl'])} (idéal {hi_['n']} positions {f0(hi_['pnl'])}, pessimiste {hp_['n']} positions {f0(hp_['pnl'])}) · "
          f"test prudent {ht['n']} positions {f0(ht['pnl'])} (idéal {f0(ST[('ind', coh, 'idéal', 'HOLD', 'inédit')]['pnl'])}, pessimiste {f0(ST[('ind', coh, 'pessimiste', 'HOLD', 'inédit')]['pnl'])}).", ""]
    return o
out += ["## 3. Classement — Δ P&L contre GARDER, scénario prudent (validation puis test)", "",
        "Classé par Δ sur la validation (prudent). Un Δ positif dont l'IC 90 % contient 0 n'est PAS démontré. Le taux de réussite n'entre pas dans le classement.", "",
        "**Attention — le portefeuille de 250 $ est ruiné.** Avec un délai de 0,3 s, GARDER perd plus de 250 $ (creux) sur la validation comme sur le test pour A et B : le portefeuille tombe à 0 et les entrées suivantes sont refusées. "
        "Le classement « 250 $ » imposé ne mesure alors presque que le moment de la ruine (Δ ≈ 0 quand les deux finissent à −250 $). Le classement « 50 $ indépendants » est donné juste après : c'est lui qui porte l'information sur les couvertures.", ""]
for coh in ("A", "B", "C"): out += classement(coh)

# ---------------- focus (50 $ indépendants : le portefeuille 250 $ est ruiné, voir section 3)
def RIp(coh, sc, h, per): return {st: r for st, r in RI[(coh, sc, h)].items() if r["per"] == per}
def foc(coh, h, per="validation", sc="prudent"):
    L = [r for r in RIp(coh, sc, h, per).values() if r["ok"] and r["att"]]
    br = collections.Counter(r["notes"].get("branche") for r in L)
    mp = sum(r["notes"].get("maker_pose", 0) for r in L); mr = sum(1 for r in L if r["notes"].get("maker_rempli", 0) >= 1)
    return L, br, mp, mr
def sI(coh, h, per, sc="prudent"): return ST[("ind", coh, sc, h, per)]
out += ["## 4. Les quatre candidates de Pitch : pourquoi elles gagnent ou perdent (mécanique, chiffres)", "",
        "Chiffres en « 50 $ indépendants » (le portefeuille de 250 $ est ruiné, section 3), scénario prudent sauf mention.", ""]
advs = np.array([r["notes"]["adv"] for coh in ("A", "B", "C") for r in RI[(coh, "idéal", "H10")].values() if r["ok"] and "adv" in r["notes"]])
out += ["### H10 — couvrir ou vendre", "",
        f"- Sur {len(advs)} déclenchements (A + B + C, toutes périodes), l'avantage brut 1 − vendeur opposé − acheteur de notre côté vaut **exactement 0** dans {pc(np.mean(np.abs(advs) < 1e-9))} des cas "
        f"(médiane {f3(np.median(advs))}, min {f3(advs.min())}, max {f3(advs.max())}) : le carnet Down est le miroir du carnet Up (vendeur Down = 1 − acheteur Up, même taille). "
        "Les frais sont symétriques (0,072·p·(1−p) est le même pour p et 1 − p) : l'avantage net est nul aussi. Acheter l'opposé = vendre sa position au même prix, mêmes frais, même quantité disponible — "
        "mais en immobilisant le capital jusqu'au règlement. La règle « neutraliser seulement si c'est mieux » choisit donc (presque) toujours **vendre**, et à égalité vendre est meilleur (capital libéré).",
        "- Vérification : H10 et VENDRE 100 % au même instant donnent le même P&L (Δ vs VENDRE 100 % : " + " · ".join(f"{coh} valid. {f0s(sI(coh, 'H10', 'validation')['d100'])}, test {f0s(sI(coh, 'H10', 'inédit')['d100'])}" for coh in ("A", "B")) +
        ") ; la couverture immédiate au marché (H13 avec seuil « jamais attendre » ou H20 branche immédiate) donne aussi le même P&L à la ligne près.",
        "- Ce qui décide du résultat n'est donc pas « couvrir ou vendre » mais « sortir ou garder » après modèle −10 : " + " · ".join(
            f"{coh} Δ vs GARDER valid. {f0(sI(coh, 'H10', 'validation')['d'])} [{f0(sI(coh, 'H10', 'validation')['lo'])} ; {f0(sI(coh, 'H10', 'validation')['hi'])}], test {f0(sI(coh, 'H10', 'inédit')['d'])} "
            f"[{f0(sI(coh, 'H10', 'inédit')['lo'])} ; {f0(sI(coh, 'H10', 'inédit')['hi'])}], jackpots gardés valid. {sI(coh, 'H10', 'validation')['kept']}/{sI(coh, 'H10', 'validation')['jk']}" for coh in ("A", "B")) +
        ". Le signe change entre validation et test : pas d'avantage stable.", ""]
out += ["### H17 — premier passage (ordre passif seulement si son espérance bat l'achat immédiat)", "",
        "Hausse moyenne du vendeur opposé 10 s après la décision quand l'ordre n'est pas rempli (apprentissage) : " + ", ".join(f"−{kk} c : {f2(100 * MOFF[kk])} c" for kk in KF) + "."]
for coh in ("A", "B"):
    for per in PER2:
        L, br, mp, mr = foc(coh, "H17", per); s_ = sI(coh, "H17", per)
        out.append(f"- {coh} {per} : {len(L)} déclenchements ; décisions {dict(br)} ; ordres passifs posés {mp}, remplis (au moins en partie) {mr} ; prix moyen opposé {f2(s_['px'])} ; "
                   f"Δ vs GARDER {f0(s_['d'])} [{f0(s_['lo'])} ; {f0(s_['hi'])}] ; Δ vs VENDRE 100 % au même instant {f0s(s_['d100'])} ; idéal {f0(sI(coh, 'H17', per, 'idéal')['d'])}, pessimiste {f0(sI(coh, 'H17', per, 'pessimiste')['d'])}.")
out += ["- Mécanique : l'EV n'est positive que si P(traversée) est élevée, or juste après le déclencheur modèle −10 le vendeur opposé a tendance à **monter** (notre côté baisse) : la règle choisit presque toujours l'immédiat, "
        "donc H17 ≈ vendre au déclencheur. Les rares ordres passifs posés ne sont pas servis assez souvent (file inconnue, traversée exigée) pour compenser la hausse payée au repli.", ""]
out += ["### H21 — recharge du carnet", "",
        f"- Photos 100 ms (toutes les photos, les deux jetons) : {NREC} sauts ≥ 2 c du meilleur vendeur ; retour au niveau d'avant en 0,5 s : {pc(BACK[0.5] / max(1, NREC))}, 1 s : {pc(BACK[1] / max(1, NREC))}, "
        f"2 s : {pc(BACK[2] / max(1, NREC))}, 5 s : {pc(BACK[5] / max(1, NREC))}. Les lignes 0,3 s ne voient pas les recharges plus rapides que ~0,3 s."]
for coh in ("A", "B"):
    for per in PER2:
        L = [r for r in RIp(coh, "prudent", "H21", per).values() if r["ok"] and r["att"]]
        tr = sum(1 for r in L if r["notes"].get("trou")); rc_ = sum(1 for r in L if r["notes"].get("recharge")); s_ = sI(coh, "H21", per)
        out.append(f"- {coh} {per} : {len(L)} déclenchements, saut ≥ 2 c dans la seconde précédente dans {tr} cas, retour au niveau d'avant dans les 5 s dans {rc_} ; prix moyen opposé {f2(s_['px'])} ; "
                   f"Δ vs GARDER {f0(s_['d'])} [{f0(s_['lo'])} ; {f0(s_['hi'])}] ; Δ vs VENDRE 100 % au même instant {f0s(s_['d100'])} ; idéal {f0(sI(coh, 'H21', per, 'idéal')['d'])}.")
out += ["- Mécanique : sans saut, H21 EST la couverture immédiate, donc une vente au prix miroir. Juste après le déclencheur modèle −10, un saut du vendeur opposé ne revient presque jamais au niveau d'avant dans les 5 s "
        "(chiffres ci-dessus), alors qu'au hasard des photos 100 ms il revient dans ~37 % des cas : à ce moment-là le saut est un vrai mouvement du marché (notre côté baisse), pas un trou de liquidité. "
        "Attendre la recharge revient donc à vendre plus tard, souvent plus bas ; et la cadence 0,3 s + délai ne permet pas de saisir les recharges à 100 ms.", ""]
out += ["### H23 — boomerang", ""]
for coh in ("A", "B"):
    for per in PER2:
        L = [r for r in RIp(coh, "prudent", "H23", per).values() if r["ok"] and r["att"]]
        rv = [r for r in L if r["notes"].get("revendu", 0) >= 1]; s_ = sI(coh, "H23", per); s1 = sI(coh, "H01", per)
        out.append(f"- {coh} {per} : paire < 1 atteinte dans {len(L)} positions ; opposé acheté dans {sum(1 for r in L if r['oppq'] >= 1)} ; revendu (+5 c) dans {len(rv)} ; "
                   f"P&L {f0(s_['pnl'])} contre {f0(s1['pnl'])} en gardant la couverture (H01) et {f0(sI(coh, 'HOLD', per)['pnl'])} en gardant sans couvrir ; Δ vs GARDER {f0(s_['d'])} [{f0(s_['lo'])} ; {f0(s_['hi'])}] ; "
                   f"Δ vs VENDRE 100 % au même instant {f0s(s_['d100'])} ; jackpots gardés {s_['kept']}/{s_['jk']}.")
out += ["- Mécanique : la paire < 1 n'arrive que quand notre côté a monté (miroir : paire < 1 ⇔ acheteur de notre côté > prix d'entrée + frais) — c'est une prise de bénéfice. "
        "La revente de l'opposé à +5 c redonne l'exposition au moment où notre côté redescend : le boomerang est un pari sur le retour de notre côté, pas une couverture ; "
        "il récupère une partie des jackpots que H01 sacrifie, mais paie deux fois l'écart et les frais.", ""]

# ---------------- tableaux complets
out += ["## 5. Tableaux complets (portefeuille 250 $, chronologique)", "",
        "Δ vs GARDER : somme sur TOUTES les positions (couvertes ou non) du P&L avec la couverture − P&L en gardant, frais compris ; IC 90 % par bootstrap de blocs d'une heure. "
        "Δ vs VENDRE : P&L couverture − P&L de la vente (50 % ou 100 %) au même instant ; positif = la couverture fait mieux que vendre. "
        "Quantité couverte = (parts opposées achetées + parts vendues) / parts d'entrée, sur les positions où la couverture a exécuté. Entrées réduites / refusées = faute de capital dans le portefeuille de 250 $.", ""]
for coh in ("A", "B", "C"):
    for sc in (SCN if coh != "C" else ["prudent"]):
        for per in PER2:
            out += [f"### {COHN[coh]} — {sc} — {per}", "", HDRF]
            out.append(ligne_full("HOLD", ST[("cap", coh, sc, "HOLD", per)], NRC[(coh, sc, "HOLD", per)]))
            for h in HEDGES: out.append(ligne_full(h, ST[("cap", coh, sc, h, per)], NRC[(coh, sc, h, per)]))
            out.append("")
out += ["### Exposition après couverture (prudent, validation) — moyennes par position", "", "| Couverture | A pire issue moy. | A gain max restant moy. | A exposition nette finale (× entrée) | A positions avec paires | B pire issue moy. | B gain max restant moy. | B exposition nette | B positions avec paires |", "|---|---|---|---|---|---|---|---|---|"]
for h in ["HOLD"] + list(HEDGES):
    cel = []
    for coh in ("A", "B"):
        s_ = ST[("cap", coh, "prudent", h, "validation")]; cel.append(f"{f0(s_['worst'])} | {f0(s_['best'])} | {f2(s_['net'])} | {s_['npairs']}")
    out.append(f"| {h if h != 'HOLD' else 'GARDER'} | " + " | ".join(cel) + " |")
out.append("")
out += ["### Apprentissage (pour mémoire, prudent, Δ vs GARDER)", "", "| Couverture | A | B | C |", "|---|---|---|---|"]
for h in HEDGES: out.append(f"| {h} {HNOM[h]} | " + " | ".join(f0(ST[('cap', coh, 'prudent', h, 'apprentissage')]['d']) for coh in ("A", "B", "C")) + " |")
out.append("")
# stabilité par jour
def jour(st): return time.strftime("%d.%m", time.gmtime(st + 7200))
JOURS = sorted({jour(st) for st in valides if PER(st) != "apprentissage"}, key=lambda x: (x[3:], x[:2]))
out += ["## 6. Stabilité par jour (prudent, Δ vs GARDER, validation + test, portefeuille 250 $ par période)", ""]
for coh in ("A", "B"):
    out += [f"### {COHN[coh]}", "", "| Couverture | " + " | ".join(JOURS) + " | jours positifs |", "|---" * (len(JOURS) + 2) + "|"]
    for h in rank[coh]:
        dj = collections.defaultdict(float)
        for per in PER2:
            Rh = RC[(coh, "prudent", "HOLD", per)]; R = RC[(coh, "prudent", h, per)]
            for st, r in R.items():
                if r["ok"]: dj[jour(st)] += r["pnl"]
            for st, r in Rh.items():
                if r["ok"]: dj[jour(st)] -= r["pnl"]
        out.append(f"| {h} | " + " | ".join(f0(dj[j_]) for j_ in JOURS) + f" | {sum(1 for j_ in JOURS if dj[j_] > 0.5)}/{len(JOURS)} |")
    out.append("")
out += ["## 7. Non testable ou testable seulement en partie", ""]
for h, why in NONTEST.items(): out.append(f"- **{h} {HNOM[h]}** — {why}.")
out += ["- **Fusion anticipée** (capital libéré avant le règlement) — non observable : seulement dans le scénario idéal.",
        "- **Remplissage passif réel** — non observable (file d'attente) : toutes les couvertures passives (H17-H20, H22) sont des bornes selon le scénario, pas des mesures.",
        "- **Latence réelle Dublin** — pas encore de données (rapide.json vide).",
        "Aucune couverture n'a été déclarée « non testable » en entier : toutes ont des résultats, avec les réserves ci-dessus.", "",
        f"Durée de calcul : {_time.time() - _T0:.0f} s."]

# ---------------- verdict (calculé, placé en tête)
V = ["## Verdict (en tête)", ""]
def gagnants(coh, mode):
    return [h for h in HEDGES if ST[(mode, coh, "prudent", h, "validation")]["lo"] > 0 and ST[(mode, coh, "prudent", h, "inédit")]["d"] > 0]
V.append(f"- **Audit / teneur d'ordre** : une simulation passive crédible n'est **pas possible** — position dans la file non observable, transactions seulement agrégées (1 s partout, 100 ms dans ~20 s de photo par cycle), "
         f"pas d'horodatage Polymarket. Selon l'hypothèse, {pc(DF['traverse2'] / max(1, DF['n']))} (pessimiste) à {pc(DF['touche'] / max(1, DF['n']))} (idéal) des ordres passifs de sauvetage seraient servis : "
         "les résultats passifs sont des bornes, pas des mesures. Latence Dublin : pas encore de données.")
V.append("- **Structure décisive** : les carnets Up et Down sont miroirs (vendeur opposé = 1 − acheteur de notre côté, même taille) et les frais sont symétriques. Acheter l'opposé = vendre sa position au même prix, "
         "en immobilisant le capital jusqu'au règlement. Toute couverture « au marché » est une sortie partielle déguisée : elle ne crée pas d'espérance, elle échange du gain potentiel (jackpots) contre une perte plus petite. "
         "Une « paire < 1 » n'existe que quand notre côté a déjà monté : c'est une prise de bénéfice.")
for coh in ("A", "B"):
    hv, ht = ST[("ind", coh, "prudent", "HOLD", "validation")], ST[("ind", coh, "prudent", "HOLD", "inédit")]
    rv, rt = ruine(coh, "prudent", "HOLD", "validation"), ruine(coh, "prudent", "HOLD", "inédit")
    gi, gc = gagnants(coh, "ind"), gagnants(coh, "cap")
    V.append(f"- **{COHN[coh]}** — GARDER prudent (délai 0,3 s) : validation {f0(hv['pnl'])} sur {hv['n']} positions, test {f0(ht['pnl'])} sur {ht['n']} "
             f"(idéal : {f0(ST[('ind', coh, 'idéal', 'HOLD', 'validation')]['pnl'])} / {f0(ST[('ind', coh, 'idéal', 'HOLD', 'inédit')]['pnl'])}). "
             f"Portefeuille 250 $ : ruiné en validation après {rv[0]} positions et en test après {rt[0]} — le classement 250 $ imposé (top 5 : "
             + ", ".join(f"{h} {f0(ST[('cap', coh, 'prudent', h, 'validation')]['d'])}" for h in rank[coh][:5]) + ") ne mesure que la date de la ruine. "
             "Classement 50 $ indépendants (top 5, Δ valid. [IC 90 %] → test) : " + " ; ".join(
                 f"{h} {f0(ST[('ind', coh, 'prudent', h, 'validation')]['d'])} [{f0(ST[('ind', coh, 'prudent', h, 'validation')]['lo'])} ; {f0(ST[('ind', coh, 'prudent', h, 'validation')]['hi'])}] → {f0(ST[('ind', coh, 'prudent', h, 'inédit')]['d'])}" for h in rank_i[coh][:5]) + ". "
             + ("**Aucune couverture ne bat GARDER de façon démontrée** (IC 90 % validation entièrement > 0 ET test > 0), ni en 250 $ ni en 50 $ indépendants." if not gi and not gc else
                f"Critère (IC 90 % validation > 0 et test > 0) rempli par : 50 $ indépendants {', '.join(gi) or 'aucune'} ; 250 $ {', '.join(gc) or 'aucune'}."))
V.append("- **Les quatre candidates (prudent, 50 $ indépendants, Δ vs GARDER valid. → test)** : " + " ; ".join(
    f"{h} A {f0(ST[('ind', 'A', 'prudent', h, 'validation')]['d'])} → {f0(ST[('ind', 'A', 'prudent', h, 'inédit')]['d'])}, "
    f"B {f0(ST[('ind', 'B', 'prudent', h, 'validation')]['d'])} → {f0(ST[('ind', 'B', 'prudent', h, 'inédit')]['d'])}" for h in ("H10", "H17", "H21", "H23"))
    + ". H10 = vendre (miroir) ; H17 et H21 retombent presque toujours sur l'immédiat (= vendre au déclencheur) ; H23 = prise de bénéfice puis pari sur le retour. Détail section 4.")
V.append("- Sorties après « modèle −10 » (H10, H12-H17, H20-H22) : négatives sur la validation, positives sur le test pour B — le signe s'inverse d'une période à l'autre : rien de stable. "
         "Ne jamais lire une baisse du creux comme une victoire : chaque ligne donne aussi les jackpots gardés et le profit sacrifié.")
V.append("")
out[VERD:VERD] = V
open("etude/bot5min/resultat_hedge_lab.md", "w").write("\n".join(out))
print("\n".join(V))
print(f"fini en {_time.time() - _T0:.0f} s")
import os, pickle
if os.environ.get("HL_DUMP"): pickle.dump(dict(ST=ST, NRC=NRC, TH=TH), open(os.environ["HL_DUMP"], "wb"))
