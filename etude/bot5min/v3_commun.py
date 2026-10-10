"""BOT95 V3 — socle commun des expériences 001-006 (hors ligne, aucune modification du bot).
Charge les lignes enregistrées 4×/s (rec_BTC), les règlements officiels, les signaux déjà définis dans attribution_001.py / meta_router.py,
et fournit : les 7 stratégies principales, une exécution réaliste paramétrable (délai, tolérance de prix), et les statistiques imposées
(sans les meilleurs trades, creux, facteur de profit, espérance, intervalle à 90 % par blocs d'une heure).
Usage : exec(open("etude/bot5min/v3_commun.py").read())"""
import sys
sys.path.insert(0, "etude/bot5min")
exec(open("etude/bot5min/attribution_001.py").read().split("cyc = {p:")[0])
TT = {st: [r[0] for r in C[st]] for st in valides}
CYC = {p: [st for st in valides if PER(st) == p] for p in PERS}
PCOURT = {"apprentissage": "app.", "validation": "valid.", "inédit": "inédit"}
hsec = lambda t: time.strftime("%d.%m %H:%M:%S", time.gmtime(t + 7200))

def premier(st, regle, lo=0.02, hi=0.98):
    """copie de diversite.premier : premier instant du cycle où regle(r, up, fair, a, tl) est vraie (modèle du bot enregistré, O8)"""
    R_ = C[st]; end = st + 300
    for i, r in enumerate(R_):
        tl = end - r[0]
        if tl < 5: break
        for up in (True, False):
            a = r[4] if up else r[6]
            if a is None or not (lo <= a <= hi): continue
            fair = r[2] if up else 1 - r[2]
            if regle(r, up, fair, a, tl): return dict(i=i, t=r[0], up=up, a=a, tl=tl, fair=fair)
    return None

def depuis_sig(st, nom):
    i, up = SIG[(st, nom)]; r = C[st][i]
    return dict(i=i, t=r[0], up=up, a=r[4] if up else r[6], tl=st + 300 - r[0], fair=r[2] if up else 1 - r[2])

# ---------- les 7 stratégies principales (définitions inchangées, reprises des études précédentes)
STRATS = {}
STRATS["V2-F original (O8)"] = {st: SIGV[("O8", st)] for st in valides if ("O8", st) in SIGV}
STRATS["V2-F 0,01 % (H1)"] = {st: SIGV[("H1", st)] for st in valides if ("H1", st) in SIGV}
STRATS["V2-D perp 120-269 s"] = {st: depuis_sig(st, "V2-D perp 120-269 s") for st in valides if (st, "V2-D perp 120-269 s") in SIG}
STRATS["V2-G jury des bourses"] = {st: depuis_sig(st, "V2-G jury des bourses") for st in valides if (st, "V2-G jury des bourses") in SIG}
for nom, regle in (("désaccord 30", lambda r, up, f, a, tl: f - a >= 0.30),
                   ("désaccord 20 60-180 s", lambda r, up, f, a, tl: f - a >= 0.20 and 60 < tl <= 180),
                   ("désaccord 20 jeton 0,35-0,65", lambda r, up, f, a, tl: f - a >= 0.20 and 0.35 <= a < 0.65)):
    STRATS[nom] = {}
    for st in valides:
        s = premier(st, regle)
        if s: STRATS[nom][st] = s
D20 = {}
for st in valides:
    s = premier(st, lambda r, up, f, a, tl: f - a >= 0.20)
    if s: D20[st] = s
NOMS7 = list(STRATS)
COURT = {"V2-F original (O8)": "V2-F O8", "V2-F 0,01 % (H1)": "V2-F H1", "V2-D perp 120-269 s": "V2-D", "V2-G jury des bourses": "V2-G",
         "désaccord 30": "D30", "désaccord 20 60-180 s": "D20 60-180", "désaccord 20 jeton 0,35-0,65": "D20 0,35-0,65"}

def exe(st, s, delai=0.0, tol=0.0, budget=50.0, detail=False):
    """Exécution réaliste au SEUL meilleur vendeur du carnet enregistré (4×/s), quantité affichée, frais inclus, 50 $ max.
    délai = temps entre décision et achat : on prend la première ligne enregistrée à t + délai ou après (délai réel ≥ délai demandé).
    tol = on accepte de payer jusqu'à prix de décision + tol (0, 1 c, 2 c) ; au-delà : pas d'achat (offre partie)."""
    R_ = C[st]; T_ = TT[st]
    k = s["i"] if delai <= 0 else bisect.bisect_left(T_, s["t"] + delai - 1e-6)
    if k >= len(R_) or R_[k][0] >= st + 300: return ("fin" if detail else None)
    r = R_[k]; a = r[4] if s["up"] else r[6]; z = (r[8] if s["up"] else r[10]) or 0
    if a is None: return ("vide" if detail else None)
    if a > s["a"] + tol + 1e-9: return ("prix" if detail else None)
    q = min(budget / a, z)
    if q < 1: return ("quantite" if detail else None)
    y = O[f"BTC:{st}"]["gagnant"] == "Up"; gm = y if s["up"] else not y
    return dict(st=st, pn=q * ((1 if gm else 0) - a - FEE(a)), mise=q * a, gm=gm, a=a, q=q, slip=a - s["a"], fee=q * FEE(a),
                partiel=q < budget / a - 1e-6, dt=r[0] - s["t"], up=s["up"])

# ---------- statistiques imposées
RNG = np.random.default_rng(20261010)
def bilan(trades, cycles, B=2000):
    """trades : liste de dict (pn, mise, gm, st) ou None ; cycles : cycles de la période (pour les blocs d'une heure, cycles sans achat = 0)"""
    T = sorted([x for x in trades if x], key=lambda x: x["st"]); n = len(T)
    pn = np.array([x["pn"] for x in T]) if n else np.zeros(0)
    cum = np.cumsum(pn) if n else np.zeros(1); dd = float(np.min(cum - np.maximum.accumulate(np.concatenate([[0], cum]))[1:])) if n else 0.0
    dd = min(0.0, dd)
    g = float(pn[pn > 0].sum()); l = float(-pn[pn < 0].sum())
    srt = np.sort(pn)[::-1]
    sans = {k: float(pn.sum() - srt[:k].sum()) for k in (1, 3, 5, 10)}
    # bootstrap par blocs d'une heure (heure UTC du début de cycle)
    H = collections.defaultdict(float)
    for st in cycles: H[st // 3600] += 0.0
    for x in T: H[x["st"] // 3600] += x["pn"]
    hv = np.array(list(H.values())); nb = len(hv)
    if nb >= 2:
        sims = hv[RNG.integers(0, nb, (B, nb))].sum(axis=1); lo, hi = np.percentile(sims, [5, 95]); pz = float(np.mean(sims <= 0))
    else: lo = hi = float(hv.sum()) if nb else 0.0; pz = float("nan")
    return dict(n=n, pnl=float(pn.sum()), win=100 * sum(x["gm"] for x in T) / n if n else 0.0, esp=float(pn.mean()) if n else 0.0,
                pf=(g / l if l > 0 else float("inf")) if n else float("nan"), dd=dd, sans=sans, lo=float(lo), hi=float(hi), pz=pz,
                mise=sum(x["mise"] for x in T), nh=nb)
fe = lambda x: f"{x:+.2f} $".replace("-", "−").replace(".", ",")
fpf = lambda x: "∞" if x == float("inf") else ("—" if x != x else f"{x:.2f}".replace(".", ","))
HDR = ("| {k} | Achats | Gagnés | Résultat net | Espérance / achat | sans top 1 | sans top 3 | sans top 5 | sans top 10 | Creux max | Facteur de profit | IC 90 % (blocs 1 h) |\n"
       "|---|---|---|---|---|---|---|---|---|---|---|---|")
def hdr(k="Stratégie"): return HDR.replace("{k}", k)
def lig(nom, b):
    if b["n"] == 0: return f"| {nom} | 0 | — | 0 $ | — | — | — | — | — | — | — | — |"
    return (f"| {nom} | {b['n']} | {b['win']:.0f} % | **{f0(b['pnl'])}** | {fe(b['esp'])} | {f0(b['sans'][1])} | {f0(b['sans'][3])} | {f0(b['sans'][5])} | "
            f"{f0(b['sans'][10])} | {f0(b['dd'])} | {fpf(b['pf'])} | [{f0(b['lo'])} ; {f0(b['hi'])}] |")
ENTETE = (f"{len(valides)} cycles BTC 5 min réglés ({hs(valides[0])} → {hs(valides[-1] + 300)}, heure suisse). "
          f"Apprentissage {len(CYC['apprentissage'])} cycles (< {hs(CUT)}) · validation {len(CYC['validation'])} (→ {hs(MATIN0)}) · "
          f"test inédit {len(CYC['inédit'])} cycles seulement (après {hs(MATIN0)}) — le test est minuscule, aucun verdict ne peut s'y appuyer seul.")
