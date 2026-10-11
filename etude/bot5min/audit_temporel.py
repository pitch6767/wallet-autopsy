"""BOT95 — GRAND AUDIT TEMPOREL (hypothèses H186-H280 de Pitch, 11.10.2026). Hors ligne : aucun bot, aucun workflow, rien publié.
Lancer depuis la racine du dépôt : python3 etude/bot5min/audit_temporel.py  → écrit etude/bot5min/resultat_audit_temporel.md

Principes : (1) aucune donnée future — toute valeur à l'instant t est la dernière ligne enregistrée ≤ t (bisect « right » − 1) ;
(2) apprentissage < CUT (≈ 08.10 22:00), validation CUT → MATIN0 (10.10 10:25), test après (jusqu'à la fin des lignes, 11.10 ~07:50) ;
(3) exécution = meilleur vendeur seul, quantité affichée, prix ≤ prix de décision, 50 $, frais 0,072·p·(1−p) par part ;
(4) toute comparaison se fait contre GARDER (HOLD) = la règle actuelle, position gardée jusqu'au règlement.
Les lignes rec_BTC n'ont PAS l'horodatage des sources : l'« âge » d'une source dans les lignes est un INDICATEUR (temps depuis le dernier
CHANGEMENT de valeur vu par le bot), pas l'âge vrai (temps depuis le dernier message). Les âges vrais n'existent que dans bot95/vitesse.json.

Modèles comparés (même règle V2-F : écart ≥ 0,20 qui a grandi de 3 c en 3 s, vendeur 0,03-0,97, premier signal du cycle, ≥ 5 s restantes) :
  O8 = probabilité ENREGISTRÉE par le bot (r[2]) — le jumeau A « tel que le bot l'a vu » ;
  R8 = reconstruction « à la date » (données ≤ t) du code probaV1 du bot : σ et écart Bybit→Chainlink en cache 5 s, écart OKX en cache 5 s,
       série remplie par la dernière valeur (serie), prix rapide = source la plus récemment reçue (indicateur), prixA regarde 6 s en arrière ;
  F8 = R8 + POLITIQUE DE FRAÎCHEUR fixée maintenant : σ sur les seules secondes où le prix a changé (pas de remplissage), écarts recalculés à
       chaque seconde, toute source plus vieille que 1 s exclue du prix rapide, Bybit ET OKX plus vieux que 1 s → pas de décision.
       Composantes isolées : R8+σ, R8+écarts, R8+exclusion."""
import json, gzip, glob, math, time, collections, calendar, hashlib, sys
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view as swv
T0 = time.time()
def log(*a): print(f"[{time.time() - T0:5.0f} s]", *a, flush=True)
FEE = lambda p: 0.072 * p * (1 - p)
SQ2 = math.sqrt(2)
try:
    from scipy.special import erf as _erf
    PHI = lambda x: 0.5 * (1 + _erf(x / SQ2))
except Exception:
    _verf = np.vectorize(math.erf)
    PHI = lambda x: 0.5 * (1 + _verf(np.asarray(x) / SQ2))
hs = lambda t: time.strftime("%d.%m %H:%M", time.gmtime(t + 7200))
hss = lambda t: time.strftime("%d.%m %H:%M:%S", time.gmtime(t + 7200))
f0 = lambda x: (f"+{x:,.0f} $" if x >= 0 else f"−{-x:,.0f} $").replace(",", " ")
pc = lambda a, b: f"{100 * a / b:.0f} %" if b else "—"
fr = lambda x, d=2: (f"{x:.{d}f}".replace(".", ",").replace("-", "−")) if x == x else "—"
MATIN0 = 1791620700; NUIT0 = 1791581760

# ===================================================================== 0. chargement
rows = {}
for f in sorted(glob.glob("bot95/donnees/*/rec_BTC.json.gz")):
    for doc in json.load(gzip.open(f, "rt")).values():
        for r in doc["lignes"]: rows[r[0]] = r
rows = sorted(rows.values(), key=lambda r: r[0])
N = len(rows)
col = lambda c: np.array([(r[c] if r[c] is not None else np.nan) for r in rows], float)
T = col(0); ST = np.array([r[1] for r in rows], np.int64); P2 = col(2)
UB, UA, DB, DA = col(3), col(4), col(5), col(6); UBZ, UAZ, DBZ, DAZ = col(7), col(8), col(9), col(10)
K = col(16)
SRC = {"bybit": 11, "okx": 12, "coinbase": 13, "binance": 14, "chainlink": 15}
RAW = {k: col(c) for k, c in SRC.items()}
del rows
O = json.load(open("bot95/officiels.json"))
log("lignes", N, hss(T[0]), "→", hss(T[-1]))

# report de la dernière valeur connue (passé seulement) + heure du dernier CHANGEMENT (indicateur de réception)
X, CHG = {}, {}
for k, v in RAW.items():
    v = v.copy(); m = np.isnan(v)
    idx = np.where(~m, np.arange(N), 0); np.maximum.accumulate(idx, out=idx); v = v[idx]; v[:np.argmax(~m)] = np.nan
    ch = np.ones(N, bool); ch[1:] = v[1:] != v[:-1]; ch &= ~np.isnan(v)
    ci = np.where(ch, np.arange(N), 0); np.maximum.accumulate(ci, out=ci)
    X[k] = v; CHG[k] = T[ci]
AGE = {k: T - CHG[k] for k in X}           # âge INDICATEUR à chaque ligne

# cycles, périodes
CI = {}
_srt = np.argsort(ST, kind="stable")
_u, _f, _c = np.unique(ST[_srt], return_index=True, return_counts=True)
for st, a, c in zip(_u, _f, _c): CI[int(st)] = np.sort(_srt[a:a + c])
valides_all = [st for st in sorted(CI) if (O.get(f"BTC:{st}") or {}).get("gagnant")]
avant = [st for st in valides_all if st < NUIT0]; CUT = avant[int(len(avant) * 0.6)]
PER = lambda st: "apprentissage" if st < CUT else ("validation" if st < MATIN0 else "test")
PERS = ("apprentissage", "validation", "test")
GAGN = {st: O[f"BTC:{st}"]["gagnant"] == "Up" for st in valides_all}
log("cycles réglés", len(valides_all), "CUT", hs(CUT), {p: sum(1 for s in valides_all if PER(s) == p) for p in PERS})

# lignes « décidables » (carnet complet + prix d'exercice), comme les études précédentes
OKROW = ~(np.isnan(UB) | np.isnan(UA) | np.isnan(DB) | np.isnan(DA) | np.isnan(K))
FI = np.nonzero(OKROW)[0]                           # indices globaux des lignes filtrées
TF = T[FI]; STF = ST[FI]
J3 = np.searchsorted(TF, TF - 3, "right") - 1       # dernière ligne filtrée ≤ t − 3
J3ok = (J3 >= 0) & (STF[np.maximum(J3, 0)] == STF)

# ===================================================================== 1. séries à la seconde (valeur en fin de seconde = dernière ligne < s+1)
S0 = int(T[0]) - 400; NS = int(T[-1]) - S0 + 3
SECS = S0 + np.arange(NS)
IEND = np.searchsorted(T, SECS + 1, "left") - 1
okend = IEND >= 0; IEc = np.maximum(IEND, 0)
def sec_end(v): o = v[IEc].copy(); o[~okend] = np.nan; return o
XE = {k: sec_end(X[k]) for k in X}
LCH = {k: np.floor(sec_end(CHG[k])) for k in X}      # seconde du dernier changement connu en fin de seconde s
CLA = np.where(SECS - LCH["chainlink"] <= 5, XE["chainlink"], np.nan)      # prixA(cl, s) : 6 s de recul
OKXA = XE["okx"]; BYE = XE["bybit"]
TS = np.floor(T).astype(np.int64); KS = TS - S0     # indice de la seconde de chaque ligne

def asof_vals(src, delay=0.0):
    """valeur, heure de changement d'une source à t − delay pour toutes les lignes (jamais de futur)"""
    if delay <= 0: return X[src], CHG[src]
    j = np.searchsorted(T, T - delay, "right") - 1; j = np.maximum(j, 0)
    return X[src][j], CHG[src][j]

def win_sorted(d, w=120):
    """fenêtres triées de w secondes COMPLÈTES [k−w, k−1] pour chaque seconde k (NaN rangés à la fin), et nombre de valeurs valides"""
    V = swv(d.astype(np.float32), w)
    Ws = np.full((NS, w), np.nan, np.float32); Ws[w:] = np.sort(V[:NS - w], axis=1)
    n = np.zeros(NS, np.int64); n[w:] = (~np.isnan(V[:NS - w])).sum(1)
    return Ws, n
def base_rows(pv, clv_ok, d_sec, w=120, WS=None):
    """médiane de (prix − Chainlink) sur [ts−120, ts−1] (secondes complètes) + la valeur courante à la date (comme serie(…,120), 121 valeurs)"""
    Ws, n = WS if WS is not None else win_sorted(d_sec, w)
    x = (pv - clv_ok); k = KS; nk = n[k]; has = ~np.isnan(x)
    m = nk + has                                    # nombre de valeurs de l'union
    r = np.zeros(len(k), np.int64)                  # rang d'insertion de x (par paquets pour la mémoire)
    for c0 in range(0, len(k), 100000):
        sl = slice(c0, c0 + 100000)
        r[sl] = (Ws[k[sl]] < x[sl, None].astype(np.float32)).sum(1)
    r[~has] = 0
    def val(q):
        q = np.clip(q, 0, w)                        # q-ième valeur (0-based) de l'union
        a = np.where(has & (q == r), x, np.nan)
        qi = np.where(has & (q > r), q - 1, q); qi = np.clip(qi, 0, w - 1)
        b = Ws[k, qi].astype(float)
        return np.where(has & (q == r), a, b)
    q1 = (m - 1) // 2; q2 = m // 2
    out = 0.5 * (val(q1) + val(q2))
    out[m == 0] = np.nan
    return out
def cl_cur(delay=0.0):
    v, c = asof_vals("chainlink", delay)
    tt = T - delay
    return np.where(np.floor(tt) - np.floor(c) <= 5, v, np.nan)

NMIN_FRESH = 20     # minimum de rendements « changés » sur 300 s pour la σ fraîche (choix de méthode, à valider par Pitch : 60 rend la σ incalculable 64 % du temps le week-end)
LPB = np.log(BYE); RB = np.full(NS, np.nan); RB[1:] = LPB[1:] - LPB[:-1]
def sigma_rows(pv, fresh=False, nmin=None):
    """σ du bot : écart type des 300 rendements log de serie(perp, 300) = 299 secondes complètes + rendement courant (à la date).
    fresh=True : seulement les secondes où le prix a CHANGÉ (rendement ≠ 0), pas de remplissage ; ≥ 60 rendements exigés."""
    r = np.nan_to_num(RB); m = (r != 0) if fresh else np.ones(NS, bool)
    c1 = np.concatenate([[0], np.cumsum(r * m)]); c2 = np.concatenate([[0], np.cumsum(r * r * m)]); cn = np.concatenate([[0], np.cumsum(m)])
    k = KS; a = np.maximum(k - 299, 0)
    s1 = c1[k] - c1[a]; s2 = c2[k] - c2[a]; n = (cn[k] - cn[a]).astype(float)
    rc = np.log(pv) - LPB[np.maximum(k - 1, 0)]; rc = np.nan_to_num(rc)
    inc = (rc != 0) if fresh else np.ones(len(k), bool)
    s1 = s1 + rc * inc; s2 = s2 + rc * rc * inc; n = n + inc
    mo = s1 / np.maximum(n, 1); var = s2 / np.maximum(n, 1) - mo * mo
    sg = np.sqrt(np.maximum(var, 0)); sg[sg == 0] = 1e-6
    sg[n < (nmin if nmin else (NMIN_FRESH if fresh else 60))] = np.nan
    return sg

# grille de rafraîchissement des caches de 5 s (émulation : premier passage plus de 5 s après le précédent)
REF = np.zeros(N, np.int64); last = -1e18; li = 0
for i in range(N):
    if T[i] - last > 5: last = T[i]; li = i
    REF[i] = li
log("séries à la seconde")

# ---- ingrédients
CLC0 = cl_cur(0.0)
D_BY = BYE - CLA; D_OK = OKXA - CLA
BASE_B_ASOF = base_rows(X["bybit"], CLC0, D_BY)
BASE_O_ASOF = base_rows(X["okx"], CLC0, D_OK)
SIG_ASOF = sigma_rows(X["bybit"]); SIG_FRESH = sigma_rows(X["bybit"], fresh=True)
SIG_BOT = SIG_ASOF[REF]; BASE_B_BOT = BASE_B_ASOF[REF]; BASE_O_BOT = BASE_O_ASOF[REF]
CLA_c = np.nan_to_num(CLA); CLA_n = (~np.isnan(CLA)).astype(float)
CC1 = np.concatenate([[0], np.cumsum(CLA_c)]); CCN = np.concatenate([[0], np.cumsum(CLA_n)])
log("σ / écarts")

def proba(sig, bb, bo, by_v, by_t, ok_v, ok_t, clc, excl=False, sdrel=8e-4, now=None):
    """probaV1 vectorisé sur toutes les lignes. by_t / ok_t = heure de réception (indicateur : dernier changement)."""
    now = T if now is None else now
    cb = by_v - bb; co = ok_v - bo
    vb = ~np.isnan(cb); vo = ~np.isnan(co)
    if excl:
        vb &= (now - by_t) <= 1.0; vo &= (now - ok_t) <= 1.0
    useb = vb & (~vo | (by_t >= ok_t))
    S = np.where(useb, cb, np.where(vo, co, np.nan))
    end = (ST + 300).astype(float); deb = end - 60; ts = TS.astype(float)
    inw = ts >= deb
    kd = (deb - S0).astype(np.int64); kt = np.minimum(TS, (end - 1).astype(np.int64)) - S0
    kd = np.clip(kd, 0, NS - 1); kt = np.clip(kt, 0, NS - 1)
    s_sum = CC1[kt] - CC1[kd]; s_n = CCN[kt] - CCN[kd]            # secondes complètes [deb, ts−1]
    cur = inw & (TS <= end - 1) & ~np.isnan(clc)
    s_sum = s_sum + np.where(cur, np.nan_to_num(clc), 0); s_n = s_n + cur
    nr = np.maximum(1, end - 1 - ts)
    E = np.where(inw, (s_sum + nr * S) / (s_n + nr), S)
    v = np.where(inw, (sig * S) ** 2 * nr ** 3 / 3 / 3600, (sig * S) ** 2 * ((deb - ts) + 20))
    p = PHI((E - K) / np.sqrt(v + (sdrel * S) ** 2))
    return np.where(np.isnan(S) | np.isnan(sig) | np.isnan(K), np.nan, p), useb, S

BYV, BYT = X["bybit"], CHG["bybit"]; OKV, OKT = X["okx"], CHG["okx"]
# prix d'exercice « moyenne Chainlink 60 s » calculable à la date (secondes [début−60, début−1], disponible dès début + 2 s, ≥ 40 secondes reçues)
K60 = {}; KN = {}
for st in CI:
    ks = np.arange(st - 60, st) - S0
    if ks[0] < 0: continue
    v = XE["chainlink"][ks]; rec = LCH["chainlink"][ks] == SECS[ks]
    KN[st] = int(rec.sum()); K60[st] = float(np.nanmean(v)) if np.isfinite(v).sum() >= 40 else np.nan
K60R = np.array([K60.get(int(s), np.nan) for s in ST]); K60R = np.where((T >= ST + 2) & np.isfinite(K60R), K60R, K)
def with_K(Kx, f):
    global K
    K0 = K; K = Kx
    try: return f()
    finally: K = K0
MOD = {}
MOD["O8"] = P2
MOD["R8"], USEB_R8, S_R8 = proba(SIG_BOT, BASE_B_BOT, BASE_O_BOT, BYV, BYT, OKV, OKT, CLC0)
MOD["R8+σ"] = proba(SIG_FRESH, BASE_B_BOT, BASE_O_BOT, BYV, BYT, OKV, OKT, CLC0)[0]
MOD["R8+écarts"] = proba(SIG_BOT, BASE_B_ASOF, BASE_O_ASOF, BYV, BYT, OKV, OKT, CLC0)[0]
MOD["R8+exclusion"] = proba(SIG_BOT, BASE_B_BOT, BASE_O_BOT, BYV, BYT, OKV, OKT, CLC0, excl=True)[0]
MOD["F8"], USEB_F8, S_F8 = proba(SIG_FRESH, BASE_B_ASOF, BASE_O_ASOF, BYV, BYT, OKV, OKT, CLC0, excl=True)
MOD["F8 (σ : 60 rendements changés exigés)"] = proba(sigma_rows(X["bybit"], fresh=True, nmin=60), BASE_B_ASOF, BASE_O_ASOF, BYV, BYT, OKV, OKT, CLC0, excl=True)[0]
MOD["R8+σ sans cache"] = proba(SIG_ASOF, BASE_B_BOT, BASE_O_BOT, BYV, BYT, OKV, OKT, CLC0)[0]
MOD["R8+K 60 s"] = with_K(K60R, lambda: proba(SIG_BOT, BASE_B_BOT, BASE_O_BOT, BYV, BYT, OKV, OKT, CLC0)[0])
log("modèles O8 / R8 / F8")

# ===================================================================== 2. rejeu V2-F et exécution
def signaux(P, lo=0.03, hi=0.97, seuil=0.20, croiss=0.03):
    """premier signal V2-F de chaque cycle : dict st -> (indice global, up, ask, fair)"""
    p = P[FI]; p3 = np.where(J3ok, p[np.maximum(J3, 0)], np.nan)
    ua, da = UA[FI], DA[FI]; ua3 = np.where(J3ok, ua[np.maximum(J3, 0)], np.nan); da3 = np.where(J3ok, da[np.maximum(J3, 0)], np.nan)
    tl = STF + 300 - TF
    with np.errstate(invalid="ignore"):
        eu = p - ua; ed = (1 - p) - da
        cu = (ua >= lo) & (ua <= hi) & (eu >= seuil) & (eu - (p3 - ua3) >= croiss) & (tl >= 5)
        cd = (da >= lo) & (da <= hi) & (ed >= seuil) & (ed - ((1 - p3) - da3) >= croiss) & (tl >= 5)
    hit = np.nonzero(cu | cd)[0]
    out = {}
    for j in hit:
        st = int(STF[j])
        if st in out or st not in GAGN: continue
        up = bool(cu[j]); out[st] = (int(FI[j]), up, float(ua[j] if up else da[j]), float(p[j] if up else 1 - p[j]))
    return out
_o = np.argsort(STF, kind="stable"); _u2, _f2, _c2 = np.unique(STF[_o], return_index=True, return_counts=True)
CFI = {int(s): np.sort(_o[a:a + c]) for s, a, c in zip(_u2, _f2, _c2)}      # positions dans FI par cycle
def execu(st, sig, delay=0.3):
    i, up, a0, fair = sig
    pos = CFI[st]; tt = TF[pos]
    k = np.searchsorted(tt, T[i] + delay - 1e-9, "left")
    if k >= len(pos) or tt[k] >= st + 300: return None
    g = FI[pos[k]]; a = UA[g] if up else DA[g]; z = (UAZ[g] if up else DAZ[g])
    if not np.isfinite(a) or a > a0 + 1e-9: return None
    q = min(50 / a, z if np.isfinite(z) else 0)
    if q < 1: return None
    gm = GAGN[st] if up else not GAGN[st]
    return dict(pn=q * ((1 if gm else 0) - a - FEE(a)), mise=q * a, gm=gm, a=a, q=q, g=g)
def pnl(S, delay=0.3, per=None):
    tot = 0.0; n = 0; w = 0
    for st, s in S.items():
        if per and PER(st) != per: continue
        x = execu(st, s, delay)
        if x: tot += x["pn"]; n += 1; w += x["gm"]
    return tot, n, w
RNG = np.random.default_rng(20261011)
def boot_delta(SA, SB, per, delay=0.3, B=4000):
    """Δ = B − A par cycle, sommé par heure, bootstrap des heures (IC 90 %)"""
    cyc = [st for st in valides_all if PER(st) == per]
    H = collections.defaultdict(float)
    for st in cyc:
        a = execu(st, SA[st], delay) if st in SA else None; b = execu(st, SB[st], delay) if st in SB else None
        H[st // 3600] += (b["pn"] if b else 0) - (a["pn"] if a else 0)
    hv = np.array(list(H.values()))
    if len(hv) < 2: return float(hv.sum()), float("nan"), float("nan")
    sims = hv[RNG.integers(0, len(hv), (B, len(hv)))].sum(1)
    return float(hv.sum()), float(np.percentile(sims, 5)), float(np.percentile(sims, 95))

SIGS = {m: signaux(MOD[m]) for m in MOD}
log("signaux", {m: len(v) for m, v in SIGS.items()})

out = []
def add(*l): out.extend(l)

# ===================================================================== 3. fantôme réel V2-F et vitesse.json
def tparse(h): return calendar.timegm(time.strptime(h[:19], "%Y-%m-%dT%H:%M:%S")) + float("0." + h[20:23])
LIVE = sorted(json.load(open("bot95/sauvegarde/V2-F_ecart_qui_grandit_BTC.json"))["trades"].values(), key=lambda x: x["heure"])
for x in LIVE: x["t"] = tparse(x["heure"]); x["perdu"] = x["net"] < 0
VIT = json.load(open("bot95/vitesse.json"))
VV2F = {e["start"]: e for e in VIT if e["nom"] == "V2-F ecart qui grandit"}
# gagnant de chaque cycle : officiels, sinon règlements, sinon fichiers de fantômes (pour les décisions après les officiels)
WIN = {st: GAGN[st] for st in GAGN}
for e in json.load(open("bot95/reglements.json")):
    if e.get("a") == "BTC" and e.get("gagnant") and e["start"] not in WIN: WIN[e["start"]] = e["gagnant"] == "Up"
for f in glob.glob("bot95/sauvegarde/*_BTC.json"):
    for v in json.load(open(f)).get("trades", {}).values():
        if v.get("gagnant") in ("Up", "Down") and v.get("start") and v["start"] not in WIN: WIN[v["start"]] = v["gagnant"] == "Up"

# série noire : plus longue suite de pertes, et épisode élargi
best = (0, 0, 0); c = 0
for i, x in enumerate(LIVE):
    c = c + 1 if x["perdu"] else 0
    if c > best[0]: best = (c, i - c + 1, i)
SN = LIVE[best[1]:best[2] + 1]
# fenêtre la plus courte contenant 27 pertes
Lidx = [i for i, x in enumerate(LIVE) if x["perdu"]]
w27 = min(((Lidx[j + 26] - Lidx[j], Lidx[j], Lidx[j + 26]) for j in range(len(Lidx) - 26)))
EP27 = LIVE[w27[1]:w27[2] + 1]
log("série noire", best[0], LIVE[best[1]]["heure"], "· 27 pertes en", len(EP27), "trades", EP27[0]["heure"], EP27[-1]["heure"])

def row_at(t):
    i = np.searchsorted(T, t, "right") - 1
    return int(i) if i >= 0 and t - T[i] < 2 else None
TMAX = T[-1]
def etat(t):
    """tout ce qu'on sait à la ligne ≤ t"""
    i = row_at(t)
    if i is None: return None
    return dict(i=i, P2=P2[i], R8=MOD["R8"][i], F8=MOD["F8"][i], sig=MOD["R8+σ"][i], bas=MOD["R8+écarts"][i], exc=MOD["R8+exclusion"][i], k60=MOD["R8+K 60 s"][i],
                aBy=AGE["bybit"][i], aOk=AGE["okx"][i], aCl=AGE["chainlink"][i], aBn=AGE["binance"][i], aCb=AGE["coinbase"][i],
                src="Bybit" if USEB_R8[i] else "OKX", sgr=SIG_FRESH[i] / SIG_BOT[i] if SIG_BOT[i] else np.nan)
def raison(e, up):
    if e is None: return "pas de ligne enregistrée (après 11.10 07:51)"
    f = (lambda p: p if up else 1 - p)
    if not np.isfinite(e["F8"]):
        if e["aBy"] > 1 and e["aOk"] > 1: return "politique : Bybit et OKX > 1 s (indicateur) → pas de décision"
        return f"σ fraîche incalculable (< {NMIN_FRESH} secondes changées sur 300 s) → pas de décision"
    d = {"σ (secondes changées)": abs(e["sig"] - e["R8"]), "écarts recalculés": abs(e["bas"] - e["R8"]), "source > 1 s exclue": abs(e["exc"] - e["R8"])}
    if abs(e["F8"] - e["R8"]) < 0.02: return "pas de divergence temporelle (|F8 − R8| < 0,02)"
    k = max(d, key=d.get); return f"{k} ({fr(f(e['F8']) - f(e['R8']))})"
def kflag(e, up, prix, cle="k60"):
    """écart (au prix réellement payé) du jumeau avec le K « moyenne 60 s » (cle k60) ou le K enregistré (cle R8)"""
    if e is None or not np.isfinite(e[cle]): return None
    return (e[cle] if up else 1 - e[cle]) - prix

# ---- âge indicateur contre âge vrai (vitesse.json)
cmp = collections.defaultdict(list)
for e in VIT:
    i = row_at(e["t0"])
    if i is None: continue
    for k, kk in (("bybit", "agePerp"), ("okx", "ageOkx"), ("chainlink", "ageCl"), ("binance", "ageBn"), ("coinbase", "ageCb")):
        if e.get(kk) is not None: cmp[k].append((e["t0"] - CHG[k][i], e[kk]))

# ===================================================================== 4. RÉDACTION
nper = {p: sum(1 for s in valides_all if PER(s) == p) for p in PERS}
# ---------- A
LIVE_ROWS = [x for x in LIVE if x["t"] <= TMAX]
def ligneA(x):
    up = x["cote"] == "Up"; e = etat(x["t"]); v = VV2F.get(x["start"]); f = (lambda p: p if up else 1 - p)
    tv = (f"{fr(v['agePerp'], 1)} / {fr(v['ageOkx'], 1)} / {fr(v['ageCl'], 1)}" if v and abs(v["t0"] - x["t"]) < 2 else "—")
    px = (f"{fr(e['aBy'], 1)} / {fr(e['aOk'], 1)} / {fr(e['aCl'], 1)}" if e else "—")
    a_row = ((UA if up else DA)[e["i"]] if e else np.nan)
    kk = kflag(e, up, x["prix"]); kc = "—" if kk is None else (f"{fr(f(e['k60']))} (écart {fr(kk)})")
    ke = FR.get(x["start"]); ke = fr(ke["err"], 1) if ke else "—"
    return (f"| {hss(x['t'])} | {x['cote']} | {fr(x['net'], 0)} | {ke} | {tv} | {px} | {fr(x['proba0'])} | {fr(f(e['P2'])) if e else '—'} | "
            f"{fr(f(e['R8'])) if e else '—'} | {fr(f(e['F8'])) if e and np.isfinite(e['F8']) else ('pas de décision' if e else '—')} | {fr(x['prix'])} / {fr(a_row)} | {raison(e, up)} | {kc} |")

# contrôle : groupes de comparaison sur tous les trades réels couverts par les lignes
def grp_stats(L):
    E = [(x, etat(x["t"])) for x in L]; E = [(x, e) for x, e in E if e]
    if not E: return None
    up = lambda x: x["cote"] == "Up"; f = lambda x, p: p if up(x) else 1 - p
    d = np.array([f(x, e["F8"]) - f(x, e["R8"]) if np.isfinite(e["F8"]) else np.nan for x, e in E])
    rr = np.array([f(x, e["R8"]) - f(x, e["P2"]) for x, e in E])
    st1 = np.array([e["aBy"] > 1 for x, e in E]); st2 = np.array([e["aBy"] > 1 and e["aOk"] > 1 for x, e in E])
    flip = sum(1 for (x, e) in E if np.isfinite(e["F8"]) and (f(x, e["F8"]) - (UA if up(x) else DA)[e["i"]]) < 0.20)
    return dict(n=len(E), stale1=st1.mean(), stale2=st2.mean(), nod=int(np.sum(np.isnan(d))), dmed=np.nanmedian(d), dabs=np.nanmedian(np.abs(d)),
                below=flip, rrec=np.median(np.abs(rr)), net=sum(x["net"] for x, e in E), sgr=np.nanmedian([e["sgr"] for x, e in E]))

# ---------- B : jumeaux et politique
B_rows = []
for m in ("R8+σ sans cache", "R8+σ", "R8+écarts", "R8+exclusion", "F8", "F8 (σ : 60 rendements changés exigés)", "R8+K 60 s"):
    for p in PERS:
        A = {s: v for s, v in SIGS["R8"].items() if PER(s) == p}; Bm = {s: v for s, v in SIGS[m].items() if PER(s) == p}
        sk_l = sk_w = fl = mv = new = 0; sk_pl = 0.0
        for s, a in A.items():
            xa = execu(s, a)
            if s not in Bm:
                if xa: sk_l += not xa["gm"]; sk_w += xa["gm"]; sk_pl += xa["pn"]
            elif Bm[s][1] != a[1]: fl += 1
            elif abs(T[Bm[s][0]] - T[a[0]]) > 0.5: mv += 1
        new = sum(1 for s in Bm if s not in A)
        d, lo, hi = boot_delta(A, Bm, p)
        d0 = boot_delta(A, Bm, p, delay=0.0, B=10)[0]
        B_rows.append((m, p, len(A), len(Bm), sk_l, sk_w, sk_pl, fl, mv, new, pnl(A)[0], pnl(Bm)[0], d, lo, hi, d0))
log("B")

# ---------- C : gel des sources
def mod_delay(src, d):
    if src == "bybit":
        v, c = asof_vals("bybit", d); return proba(SIG_BOT, BASE_B_BOT, BASE_O_BOT, v, c, OKV, OKT, CLC0)[0]
    if src == "okx":
        v, c = asof_vals("okx", d); return proba(SIG_BOT, BASE_B_BOT, BASE_O_BOT, BYV, BYT, v, c, CLC0)[0]
    if src == "chainlink":
        return proba(SIG_BOT, BASE_B_BOT, BASE_O_BOT, BYV, BYT, OKV, OKT, cl_cur(d))[0]
C_rows = []
sig_rows = np.array([s[0] for s in SIGS["R8"].values()])
valid_mask = np.isin(ST, [s for s in valides_all]) & OKROW
samp = np.nonzero(valid_mask)[0]
for src in ("bybit", "okx", "chainlink"):
    for d in (0.1, 0.5, 1.0):
        Pd = mod_delay(src, d); dP = np.abs(Pd - MOD["R8"])
        Sd = signaux(Pd); A = SIGS["R8"]
        lost = sum(1 for s in A if s not in Sd); flip = sum(1 for s in A if s in Sd and Sd[s][1] != A[s][1])
        moved = sum(1 for s in A if s in Sd and Sd[s][1] == A[s][1] and abs(T[Sd[s][0]] - T[A[s][0]]) > 0.5)
        new = sum(1 for s in Sd if s not in A)
        dpl = {p: pnl({s: v for s, v in Sd.items() if PER(s) == p})[0] - pnl({s: v for s, v in A.items() if PER(s) == p})[0] for p in PERS}
        frag = (lost + flip + moved + new) / max(1, len(A))
        C_rows.append((src, d, np.nanmedian(dP[samp]), np.nanpercentile(dP[samp], 99), np.nanmedian(dP[sig_rows]), lost, flip, moved, new, frag, dpl))
log("C")

# ---------- D : sauts de probabilité (O8 enregistrée), règle pré-enregistrée
pf = P2[FI]; same = np.zeros(len(FI), bool); same[1:] = (STF[1:] == STF[:-1]) & (TF[1:] - TF[:-1] <= 0.5)
dp = np.full(len(FI), np.nan); dp[1:] = pf[1:] - pf[:-1]
D_rows = {}
prev = np.zeros(len(FI), np.int64); prev[1:] = FI[:-1]; prev[0] = FI[0]
chB = np.r_[False, X["bybit"][FI][1:] != X["bybit"][prev[1:]]]; chO = np.r_[False, X["okx"][FI][1:] != X["okx"][prev[1:]]]
agB = AGE["bybit"][prev]; agO = AGE["okx"][prev]
chC = np.r_[False, X["chainlink"][FI][1:] != X["chainlink"][prev[1:]]]; chK = np.r_[False, K[FI][1:] != K[prev[1:]]]
def classe_saut(j):
    if chB[j] and agB[j] > 1 or chO[j] and agO[j] > 1: return "rattrapage (source > 1 s puis mise à jour)"
    if chB[j] or chO[j]: return "information nouvelle (source fraîche)"
    if chK[j]: return "prix d'exercice changé"
    if chC[j]: return "Chainlink seul"
    return "aucune source changée (cache σ/écart, horloge)"
for th in (0.05, 0.10):
    J = np.nonzero(same & (np.abs(np.nan_to_num(dp)) >= th))[0]
    cnt = collections.Counter(classe_saut(j) for j in J)
    # retour en arrière dans les 3 s ?
    rev = collections.defaultdict(list)
    for j in J:
        k = np.searchsorted(TF, TF[j] + 3, "right") - 1
        if STF[k] != STF[j] or not np.isfinite(pf[k]): continue
        rev[classe_saut(j)].append((pf[k] - pf[j]) * np.sign(dp[j]) / abs(dp[j]))
    D_rows[th] = (len(J), cnt, {k: np.median(v) for k, v in rev.items()})
# signaux V2-F (O8) : la croissance de 3 s contient-elle un rattrapage ? la source était-elle vieille au signal ?
D_sig = collections.defaultdict(lambda: [0, 0, 0.0])
for st, s in SIGS["O8"].items():
    g = s[0]; pos = np.searchsorted(FI, g); lo_ = np.searchsorted(TF, TF[pos] - 3, "left")
    win = range(max(lo_, 1), pos + 1)
    cls = "sans saut ≥ 0,05"
    big = [j for j in win if same[j] and abs(np.nan_to_num(dp[j])) >= 0.05]
    if big: cls = "rattrapage dans les 3 s" if any(classe_saut(j).startswith("rattrapage") for j in big) else "saut d'information nouvelle"
    x = execu(st, s)
    if x: D_sig[(PER(st), cls)][0] += 1; D_sig[(PER(st), cls)][1] += x["gm"]; D_sig[(PER(st), cls)][2] += x["pn"]
log("D")

# ---------- E : instantanés Frankenstein (désaccord ≥ 0,30, O8)
def desacc30(P, lo=0.02, hi=0.98):
    p = P[FI]; ua, da = UA[FI], DA[FI]; tl = STF + 300 - TF
    with np.errstate(invalid="ignore"):
        cu = (ua >= lo) & (ua <= hi) & (p - ua >= 0.30) & (tl >= 5); cd = (da >= lo) & (da <= hi) & ((1 - p) - da >= 0.30) & (tl >= 5)
    o = {}
    for j in np.nonzero(cu | cd)[0]:
        st = int(STF[j])
        if st in o or st not in GAGN: continue
        up = bool(cu[j]); o[st] = (int(FI[j]), up, float(ua[j] if up else da[j]), float(p[j] if up else 1 - p[j]))
    return o
D30 = desacc30(P2)
def disp(i, srcs): a = [AGE[k][i] for k in srcs]; return max(a) - min(a)
E_rows = {}
for nom, srcs in (("Bybit / OKX / Chainlink (sources du modèle)", ("bybit", "okx", "chainlink")), ("5 sources", tuple(SRC))):
    W, L = [], []
    for st, s in D30.items():
        (W if (GAGN[st] == s[1]) else L).append(disp(s[0], srcs))
    W, L = np.array(W), np.array(L)
    allv = np.r_[W, L]; obs = np.median(L) - np.median(W); cntp = 0
    for _ in range(2000):
        RNG.shuffle(allv); cntp += (np.median(allv[:len(L)]) - np.median(allv[len(L):])) >= obs
    E_rows[nom] = (len(L), len(W), np.median(L), np.median(W), np.mean(L > 1), np.mean(W > 1), cntp / 2000)
# âges vrais : décisions réelles « desaccord 30 » de vitesse.json
EV = {"perdu": [], "gagné": []}
for e in VIT:
    if e["nom"] != "desaccord 30" or e["start"] not in WIN: continue
    up = e["cote"] == "Up"; gm = WIN[e["start"]] == up
    a = [e["agePerp"], e["ageOkx"], e["ageCl"]]
    EV["gagné" if gm else "perdu"].append((max(a) - min(a), max(e["agePerp"], e["ageOkx"]) > 1, min(e["agePerp"], e["ageOkx"]) > 1))
log("E")

# ---------- F : prix d'exercice et fenêtre Chainlink
F_rows = []
for st in valides_all:
    o = O[f"BTC:{st}"]; idx = CI[st]
    late = idx[T[idx] >= st + 10]
    if not len(late) or not o.get("ptb"): continue
    k_used = K[late[0]]
    # nombre de secondes Chainlink « reçues » (changement de valeur) dans [st−60, st−1] — indicateur du compte du bot
    ks = np.arange(st - 60, st) - S0
    if ks[0] < 0: continue
    nchg = int(np.sum(LCH["chainlink"][ks] == SECS[ks]))
    kfirst = K[idx[0]]; ksw = np.nonzero(K[idx] != kfirst)[0]
    t_final = T[idx[ksw[0]]] - st if len(ksw) else 0.0
    # fin de cycle : moyenne « secondes reçues seulement » (méthode connus du bot) contre moyenne 60 s remplie, contre officiel
    ke = np.arange(st + 240, st + 300) - S0
    fe = o.get("final")
    if ke[-1] < NS and fe:
        m_all = np.nanmean(XE["chainlink"][ke]); m_kn = np.nanmean(CLA[ke])
        ch_ = LCH["chainlink"][ke] == SECS[ke]; m_chg = np.nanmean(XE["chainlink"][ke][ch_]) if ch_.any() else np.nan
        nfin = int(ch_.sum())
    else: m_all = m_kn = m_chg = np.nan; nfin = -1
    F_rows.append(dict(st=st, err=k_used - o["ptb"], n=nchg, twap=bool(np.isfinite(K60.get(st, np.nan)) and abs(k_used - K60[st]) < 0.5), e60=K60.get(st, np.nan) - o["ptb"], tfin=t_final, ef_all=(m_all - fe) if fe else np.nan, ef_chg=(m_chg - fe) if fe else np.nan, nfin=nfin))
FR = {r["st"]: r for r in F_rows}
_tw = [r for r in F_rows if r["twap"]]
# bascule : premier cycle à partir duquel ≥ 95 % des cycles suivants utilisent la moyenne 60 s
SWITCH = next((r["st"] for j, r in enumerate(F_rows) if np.mean([x["twap"] for x in F_rows[j:]]) >= 0.80), None)
log("F")

# ---------- G : causalité / déterminisme / fuite des anciens chargeurs
G_hash = []
for rep in range(2):
    S_ = signaux(proba(SIG_FRESH, BASE_B_ASOF, BASE_O_ASOF, BYV, BYT, OKV, OKT, CLC0, excl=True)[0])
    G_hash.append(hashlib.sha256(json.dumps(sorted((k, v[0], v[1]) for k, v in S_.items())).encode()).hexdigest()[:16])
H_A = hashlib.sha256(json.dumps(sorted((k, v[0], v[1]) for k, v in signaux(proba(SIG_BOT, BASE_B_BOT, BASE_O_BOT, BYV, BYT, OKV, OKT, CLC0)[0]).items())).encode()).hexdigest()[:16]
H_A0 = hashlib.sha256(json.dumps(sorted((k, v[0], v[1]) for k, v in SIGS["R8"].items())).encode()).hexdigest()[:16]
mono = bool(np.all(np.diff(T) > 0)); incyc = float(np.mean((T >= ST) & (T < ST + 300)))
# fuite de meta_router.parts_r : P1[s] / CL1[s] = valeur en FIN de seconde (jusqu'à 0,999 s après la ligne de décision)
P1v = np.where(np.isnan(RAW["bybit"]), RAW["okx"], RAW["bybit"])
P1v = np.where(np.isnan(P1v), np.nan, P1v)
P1f = P1v.copy(); m_ = np.isnan(P1f); ii_ = np.where(~m_, np.arange(N), 0); np.maximum.accumulate(ii_, out=ii_); P1f = P1f[ii_]
P1E = P1f[IEc]; CL1E = XE["chainlink"]
def parts_model(leak, sd=8e-4):
    cur_p = P1E[KS] if leak else P1f; cur_c = CL1E[KS] if leak else X["chainlink"]
    lp = np.log(P1E); r = np.full(NS, np.nan); r[1:] = lp[1:] - lp[:-1]; r = np.nan_to_num(r)
    c1 = np.r_[0, np.cumsum(r)]; c2 = np.r_[0, np.cumsum(r * r)]
    k = KS; a = np.maximum(k - 299, 0)
    rc = np.nan_to_num(np.log(cur_p) - lp[np.maximum(k - 1, 0)])
    s1 = c1[k] - c1[a] + rc; s2 = c2[k] - c2[a] + rc * rc; n = 300.0
    sg = np.sqrt(np.maximum(s2 / n - (s1 / n) ** 2, 0)); sg[sg == 0] = 1e-6
    b = base_rows(cur_p, cur_c, P1E - CL1E)
    p = np.where(np.isnan(RAW["bybit"]), RAW["okx"], RAW["bybit"]); S = p - b
    end = (ST + 300).astype(float); deb = end - 59; s = TS.astype(float); inw = s >= deb
    cc1 = np.r_[0, np.cumsum(np.nan_to_num(CL1E))]; ccn = np.r_[0, np.cumsum(~np.isnan(CL1E))]
    kd = np.clip((deb - S0).astype(np.int64), 0, NS - 1); kt = np.clip(KS, 0, NS - 1)
    ssum = cc1[kt] - cc1[kd] + np.where(inw, np.nan_to_num(cur_c), 0); sn = ccn[kt] - ccn[kd] + inw
    nr = np.maximum(1, end - s)
    E = np.where(inw, (ssum + nr * S) / (sn + nr), S); v = np.where(inw, (sg * S) ** 2 * nr ** 3 / 3 / 3600, (sg * S) ** 2 * ((deb - s) + 20))
    return np.where(np.isnan(S) | np.isnan(K), np.nan, PHI((E - K) / np.sqrt(v + (sd * S) ** 2)))
G_leak = {}
for nom, sd in (("X8 (0,08 %)", 8e-4), ("X15 (0,015 %, cohorte B du Hedge Lab)", 1.5e-4)):
    PL, PA = parts_model(True, sd), parts_model(False, sd)
    SL, SA_ = signaux(PL), signaux(PA)
    ch = sum(1 for s in set(SL) | set(SA_) if (s in SL) != (s in SA_) or (s in SL and s in SA_ and (SL[s][0] != SA_[s][0] or SL[s][1] != SA_[s][1])))
    G_leak[nom] = (np.nanmedian(np.abs(PL - PA)[samp]), np.nanpercentile(np.abs(PL - PA)[samp], 99), len(SL), len(SA_), ch,
                   {p: (pnl({s: v for s, v in SL.items() if PER(s) == p})[0], pnl({s: v for s, v in SA_.items() if PER(s) == p})[0]) for p in PERS})
log("G")

# ---------- H : rejet par le marché
H_res = {}
sigO = SIGS["O8"]
def dF3(st, s):
    g = s[0]; pos = np.searchsorted(FI, g); j = J3[pos]
    if not J3ok[pos]: return np.nan
    f = (lambda p: p if s[1] else 1 - p); return f(P2[g]) - f(P2[FI[j]])
def ask_at(st, s, k):
    pos = CFI[st]; tt = TF[pos]; j = np.searchsorted(tt, T[s[0]] + k, "left")
    if j >= len(pos) or tt[j] >= st + 300: return None, None, None
    g = FI[pos[j]]; return (UA[g] if s[1] else DA[g]), (UB[g] if s[1] else DB[g]), (UBZ[g] if s[1] else DBZ[g])
Xh = np.nanmedian([dF3(st, s) for st, s in sigO.items() if PER(st) == "apprentissage"])
for k in (1, 2, 3):
    agg = collections.defaultdict(lambda: [0, 0, 0.0, 0.0])
    for st, s in sigO.items():
        d = dF3(st, s)
        if not (d >= Xh): continue
        a1, b1, bz = ask_at(st, s, k)
        if a1 is None or not np.isfinite(a1): continue
        cls = "le marché suit (+1 c ou plus)" if a1 - s[2] >= 0.01 - 1e-9 else "le marché ne suit pas (rejet)"
        x = execu(st, s)
        if not x: continue
        alt = x["pn"]
        if cls.startswith("le marché ne suit") and np.isfinite(b1) and T[x["g"]] < T[s[0]] + k:
            qv = min(x["q"], bz if np.isfinite(bz) else 0)        # sortie au meilleur acheteur à t + k (quantité affichée)
            gm = x["gm"]; alt = qv * (b1 - FEE(b1) - x["a"] - FEE(x["a"])) + (x["q"] - qv) * ((1 if gm else 0) - x["a"] - FEE(x["a"]))
        A_ = agg[(PER(st), cls)]; A_[0] += 1; A_[1] += x["gm"]; A_[2] += x["pn"]; A_[3] += alt
    H_res[k] = agg
log("H")

# ---------- I : conservation
with np.errstate(invalid="ignore"):
    cu1 = np.abs(UB + DA - 1); cu2 = np.abs(UA + DB - 1); sa = UA + DA; sb = UB + DB
    zz1 = np.abs(UBZ - DAZ); zz2 = np.abs(UAZ - DBZ)
okb = OKROW
I_res = dict(n=int(okb.sum()), c1=np.nanmax(cu1[okb]), c1n=int(np.sum(cu1[okb] > 1e-6)), c2=np.nanmax(cu2[okb]), c2n=int(np.sum(cu2[okb] > 1e-6)),
             sa_lt1=int(np.sum(sa[okb] < 1 - 1e-9)), sb_gt1=int(np.sum(sb[okb] > 1 + 1e-9)), sa_med=np.nanmedian(sa[okb]),
             z1=int(np.sum(zz1[okb] > 1e-6)), z2=int(np.sum(zz2[okb] > 1e-6)), pnan=int(np.sum(np.isnan(P2[okb]))),
             prange=(np.nanmin(P2), np.nanmax(P2)))
log("I")

# ===================================================================== 5. fichier résultat
# chiffres de tête
rr = MOD["R8"][samp] - P2[samp]; ok_ = np.isfinite(rr)
corrRO = np.corrcoef(MOD["R8"][samp][ok_], P2[samp][ok_])[0, 1]
liveO = {x["start"]: x for x in LIVE}
def accord(S):
    cyc = [s for s in S if s in liveO]; both = [s for s in cyc if (liveO[s]["cote"] == "Up") == S[s][1]]
    near = [s for s in both if abs(T[S[s][0]] - liveO[s]["t"]) <= 1]
    lo, hi = min(x["t"] for x in LIVE), TMAX
    nl = sum(1 for x in LIVE if x["t"] <= hi and x["start"] in GAGN); ns = sum(1 for s in S if lo - 300 <= s <= hi)
    return nl, ns, len(cyc), len(both), len(near)
ACC = {m: accord(SIGS[m]) for m in ("O8", "R8", "F8")}
# B totaux hors apprentissage pour F8
Bf = {r[1]: r for r in B_rows if r[0] == "F8"}
# part des fausses alertes attribuable
def flags_live(x):
    e = etat(x["t"]); up = x["cote"] == "Up"
    if not e: return None
    f = (lambda p: p if up else 1 - p); a = (UA if up else DA)[e["i"]]
    fl = {}
    fl["source du prix rapide > 1 s (indicateur)"] = (e["aBy"] if e["src"] == "Bybit" else e["aOk"]) > 1
    fl["politique F8 : plus de signal (écart < 0,20 ou pas de décision)"] = (not np.isfinite(e["F8"])) or (f(e["F8"]) - a < 0.20)
    fr_ = FR.get(x["start"]); fl["erreur de K > 2 $ en faveur de notre côté"] = bool(fr_ and (-fr_["err"] if up else fr_["err"]) > 2)
    pos = np.searchsorted(FI, e["i"]); lo_ = np.searchsorted(TF, TF[min(pos, len(FI) - 1)] - 3, "left")
    fl["rattrapage de flux dans les 3 s"] = any(same[j] and abs(np.nan_to_num(dp[j])) >= 0.05 and classe_saut(j).startswith("rattrapage") for j in range(max(lo_, 1), min(pos, len(FI) - 1) + 1))
    fl["au moins un des drapeaux"] = any(fl.values())
    return fl
FL = {"perdu": collections.Counter(), "gagné": collections.Counter()}; NFL = {"perdu": 0, "gagné": 0}
for x in LIVE_ROWS:
    fl = flags_live(x)
    if fl is None: continue
    g = "perdu" if x["perdu"] else "gagné"; NFL[g] += 1
    for k, v in fl.items(): FL[g][k] += v
# même chose sur le rejeu O8 (toutes périodes) : désaccords ≥ 0,30 perdants
def flags_sig(st, s):
    e = etat(T[s[0]] + 1e-6); up = s[1]; f = (lambda p: p if up else 1 - p)
    fl = {"source du prix rapide > 1 s (indicateur)": (e["aBy"] if e["src"] == "Bybit" else e["aOk"]) > 1,
          "politique F8 : plus de signal (écart < 0,20 ou pas de décision)": (not np.isfinite(e["F8"])) or (f(e["F8"]) - s[2] < 0.20),
          "erreur de K > 2 $ en faveur de notre côté": bool(FR.get(st) and (-FR[st]["err"] if up else FR[st]["err"]) > 2)}
    pos = np.searchsorted(FI, s[0]); lo_ = np.searchsorted(TF, TF[pos] - 3, "left")
    fl["rattrapage de flux dans les 3 s"] = any(same[j] and abs(np.nan_to_num(dp[j])) >= 0.05 and classe_saut(j).startswith("rattrapage") for j in range(max(lo_, 1), pos + 1))
    fl["au moins un des drapeaux"] = any(fl.values()); return fl
FL30 = {"perdu": collections.Counter(), "gagné": collections.Counter()}; NF30 = {"perdu": 0, "gagné": 0}
for st, s in D30.items():
    g = "gagné" if GAGN[st] == s[1] else "perdu"; NF30[g] += 1
    for k, v in flags_sig(st, s).items(): FL30[g][k] += v
anyL, anyW = FL30["perdu"]["au moins un des drapeaux"] / max(1, NF30["perdu"]), FL30["gagné"]["au moins un des drapeaux"] / max(1, NF30["gagné"])

# ----------------------------------------------------------------- verdict
add("# BOT95 — GRAND AUDIT TEMPOREL (hypothèses H186-H280)", "",
    f"Étude hors ligne du 11.10.2026 — aucun bot, aucun workflow modifié, rien publié. {len(valides_all)} cycles BTC réglés ({hs(valides_all[0])} → {hs(valides_all[-1] + 300)}, heure suisse) : "
    f"apprentissage {nper['apprentissage']} (< {hs(CUT)}) · validation {nper['validation']} (→ {hs(MATIN0)}) · test {nper['test']} (→ {hs(valides_all[-1] + 300)}). "
    f"Lignes enregistrées jusqu'au {hss(TMAX)}. Le test a déjà été regardé par d'autres études pour la période 10.10 10:25-13:45 : il est **exploratoire**.", "",
    "## Verdict (en tête)", "")
add("@@VERDICT@@", "")

# ----------------------------------------------------------------- jumeau R8 : fidélité
add("## 0. Fidélité du jumeau du bot (R8) et de l'indicateur d'âge", "",
    f"- R8 (reconstruction à la date du code probaV1) contre la probabilité enregistrée O8 sur {ok_.sum()} lignes : corrélation {fr(corrRO, 3)}, écart absolu médian {fr(np.median(np.abs(rr[ok_])), 3)}, "
    f"90 % {fr(np.percentile(np.abs(rr[ok_]), 90), 3)}, 99 % {fr(np.percentile(np.abs(rr[ok_]), 99), 3)}. Le jumeau n'est donc PAS identique au bot (caches de phase inconnue, indicateur de réception, "
    "prixA reconstruit) : toute comparaison de politique se fait R8 contre F8 (même code, une seule chose change).",
    "", "| Rejeu | Trades réels (cycles réglés couverts) | Signaux du rejeu (même période) | Cycles communs | Même côté | Même côté à 1 s près |", "|---|---|---|---|---|---|")
for m, (nl, ns, nc, nb, nn) in ACC.items(): add(f"| {m} | {nl} | {ns} | {nc} | {nb} | {nn} |")
add("", "Âge INDICATEUR (temps depuis le dernier changement de valeur dans les lignes) contre âge VRAI (vitesse.json, temps depuis le dernier message) aux mêmes décisions :", "",
    "| Source | Décisions | Âge vrai médian | Indicateur médian | Corrélation | Vrai > 1 s | Indicateur > 1 s | Accord sur « > 1 s » |", "|---|---|---|---|---|---|---|---|")
for k, L in cmp.items():
    a = np.array(L)
    if len(a) < 5: continue
    add(f"| {k} | {len(a)} | {fr(np.median(a[:, 1]))} s | {fr(np.median(a[:, 0]))} s | {fr(np.corrcoef(a[:, 0], a[:, 1])[0, 1])} | {pc(np.sum(a[:, 1] > 1), len(a))} | {pc(np.sum(a[:, 0] > 1), len(a))} | {pc(np.sum((a[:, 0] > 1) == (a[:, 1] > 1)), len(a))} |")
add("", "Binance et Coinbase ne sont PAS utilisés par probaV1 (seulement Bybit, OKX, Chainlink) : leur fraîcheur ne peut pas changer la probabilité du bot.", "")

# ----------------------------------------------------------------- A
add("## A. La série noire V2-F et ses groupes de contrôle", "",
    f"Fichier `bot95/sauvegarde/V2-F_ecart_qui_grandit_BTC.json` : {len(LIVE)} trades réels ({hss(LIVE[0]['t'])} → {hss(LIVE[-1]['t'])}), {sum(x['perdu'] for x in LIVE)} perdus. "
    f"Âges vrais (vitesse.json) disponibles pour {sum(1 for x in LIVE if x['start'] in VV2F)} trades (depuis le 10.10 14:17). "
    "Colonnes : âges Bybit / OKX / Chainlink en s ; probabilités pour NOTRE côté ; « prix » = prix réel payé / meilleur vendeur de la ligne enregistrée ≤ décision.", "",
    f"### Série noire : {best[0]} pertes de suite", "",
    "| Décision | Côté | Net $ | Erreur K $ | Âges vrais | Âges indicateurs | Proba réelle (proba0) | O8 ligne | R8 à la date | F8 fraîcheur | Prix réel / ligne | Raison de la divergence (fraîcheur) | R8 avec K 60 s (écart au prix payé) |",
    "|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for x in SN: add(ligneA(x))
add("", f"### Épisode élargi : 27 pertes en {len(EP27)} trades", "",
    "| Décision | Côté | Net $ | Erreur K $ | Âges vrais | Âges indicateurs | Proba réelle (proba0) | O8 ligne | R8 à la date | F8 fraîcheur | Prix réel / ligne | Raison de la divergence (fraîcheur) | R8 avec K 60 s (écart au prix payé) |",
    "|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for x in EP27:
    if x not in SN: add(ligneA(x))
def kres(L):
    d = []
    for x in L:
        e = etat(x["t"]); kk = kflag(e, x["cote"] == "Up", x["prix"]); kr = kflag(e, x["cote"] == "Up", x["prix"], "R8")
        if kk is None or kr is None: continue
        d.append(kk - kr)
    d = np.array(d); return len(d), (np.median(d) if len(d) else np.nan), (np.mean(d <= -0.05) if len(d) else np.nan)
_kL, _kW = kres([x for x in EP27 if x["perdu"]]), kres([x for x in EP27 if not x["perdu"]])
_aL = kres([x for x in LIVE_ROWS if x["perdu"] and x["t"] < (SWITCH or 0)]); _aW = kres([x for x in LIVE_ROWS if not x["perdu"] and x["t"] < (SWITCH or 0)])
add("", f"**Prix d'exercice dans l'épisode** (avant la bascule du {hs(SWITCH) if SWITCH else '—'}) : avec le K « moyenne 60 s » (calculable à la date), notre probabilité (notre côté) change en médiane de "
    f"{fr(_kL[1])} pour les {_kL[0]} perdants de l'épisode (baisse ≥ 0,05 : {pc(_kL[2] * _kL[0], _kL[0])}) et de {fr(_kW[1])} pour ses {_kW[0]} gagnants ; "
    f"sur tous les trades réels avant la bascule : {fr(_aL[1])} pour {_aL[0]} perdants (baisse ≥ 0,05 : {pc(_aL[2] * _aL[0], _aL[0])}) contre {fr(_aW[1])} pour {_aW[0]} gagnants (baisse ≥ 0,05 : {pc(_aW[2] * _aW[0], _aW[0])}). "
    "(Le jumeau garde son propre instant : le trade réel aurait pu se déclencher plus tard avec un autre K — voir la ligne « R8+K 60 s » de B pour l'effet sur la règle complète.)", "")
# âges vrais : série contre contrôles
def vstat(L):
    a = np.array([[v["agePerp"], v["ageOkx"], v["ageCl"]] for v in L]) if L else np.zeros((0, 3))
    if not len(a): return "| 0 | — | — | — | — | — |"
    return (f"| {len(a)} | {fr(np.median(a[:, 0]))} / {fr(np.median(a[:, 1]))} / {fr(np.median(a[:, 2]))} | {fr(np.percentile(a[:, 0], 90))} / {fr(np.percentile(a[:, 1], 90))} | "
            f"{pc(np.sum(a[:, 0] > 1), len(a))} | {pc(np.sum((a[:, 0] > 1) & (a[:, 1] > 1)), len(a))} | {pc(np.sum(np.maximum(a[:, 0], a[:, 1]) - np.minimum(a[:, 0], a[:, 1]) > 1), len(a))} |")
snS = {x["start"] for x in SN}
gv = {"série de 18 pertes (11.10)": [], "autres perdants": [], "gagnants": []}
for x in LIVE:
    v = VV2F.get(x["start"])
    if not v or abs(v["t0"] - x["t"]) > 2: continue
    gv["série de 18 pertes (11.10)" if (x["start"] in snS and x["perdu"]) else ("autres perdants" if x["perdu"] else "gagnants")].append(v)
add("", "### Âges VRAIS au moment de la décision (vitesse.json) : série contre contrôles", "",
    "| Groupe | Trades | Âge médian Bybit / OKX / Chainlink (s) | 90 % Bybit / OKX | Bybit > 1 s | Bybit ET OKX > 1 s (politique : pas de décision) | Écart d'âge Bybit−OKX > 1 s |", "|---|---|---|---|---|---|---|")
for k, L in gv.items(): add(f"| {k} " + vstat(L))
# politique appliquée aux âges vrais sur tous les trades réels couverts par vitesse
sk = [x for x in LIVE if x["start"] in VV2F and abs(VV2F[x["start"]]["t0"] - x["t"]) < 2 and VV2F[x["start"]]["agePerp"] > 1 and VV2F[x["start"]]["ageOkx"] > 1]
add("", f"Politique appliquée aux âges VRAIS (seule partie de F8 calculable sans prix) : {len(sk)} trades réels auraient été sautés (Bybit et OKX > 1 s) : "
    f"{sum(x['perdu'] for x in sk)} perdants, {sum(not x['perdu'] for x in sk)} gagnants, résultat réel de ces trades {f0(sum(x['net'] for x in sk))} "
    f"(les sauter = {f0(-sum(x['net'] for x in sk))} contre GARDER).", "")
add("### Groupes de contrôle sur tous les trades réels couverts par les lignes", "",
    "| Groupe | Trades | Résultat réel | Prix rapide Bybit > 1 s (ind.) | Bybit et OKX > 1 s (ind.) | F8 sans décision | médiane F8 − R8 (notre côté) | médiane |F8 − R8| | F8 : écart < 0,20 | médiane |R8 − O8| | σ fraîche / σ bot (médiane) |",
    "|---|---|---|---|---|---|---|---|---|---|---|")
for nom, L in (("série (27 pertes, si couverte)", [x for x in EP27 if x["perdu"]]), ("tous les perdants", [x for x in LIVE_ROWS if x["perdu"]]), ("tous les gagnants", [x for x in LIVE_ROWS if not x["perdu"]]),
               ("perdants 11.10", [x for x in LIVE_ROWS if x["perdu"] and x["t"] >= 1791676800 - 7200]), ("gagnants 11.10", [x for x in LIVE_ROWS if not x["perdu"] and x["t"] >= 1791676800 - 7200])):
    g = grp_stats(L)
    if not g: add(f"| {nom} | 0 (hors lignes) | — | — | — | — | — | — | — | — | — |"); continue
    add(f"| {nom} | {g['n']} | {f0(g['net'])} | {pc(g['stale1'] * g['n'], g['n'])} | {pc(g['stale2'] * g['n'], g['n'])} | {g['nod']} | {fr(g['dmed'], 3)} | {fr(g['dabs'], 3)} | {g['below']} | {fr(g['rrec'], 3)} | {fr(g['sgr'])} |")
add("", "Lecture : σ fraîche / σ bot > 1 = la politique « secondes changées seulement » GONFLE σ (elle retire les rendements nuls, y compris les vrais) → probabilités moins extrêmes. "
    "Remarque de méthode : une variance réalisée par unité de temps n'est PAS biaisée par le remplissage tant que le rattrapage (le saut à la reprise du flux) est dans la fenêtre ; "
    "le biais du remplissage n'existe que pendant une coupure EN COURS au moment de la décision.", "")

# ----------------------------------------------------------------- B
add("## B. Politique de fraîcheur : décisions changées et P&L contre GARDER (règle V2-F, tous les cycles)", "",
    "Référence = jumeau R8 (règle actuelle, position gardée jusqu'au règlement). Chaque ligne change UNE composante (ou toutes : F8). Exécution 0,3 s (meilleur vendeur, ≤ prix de décision, 50 $). "
    "« Sautés » = trades de R8 que la variante ne prend plus ; perdants / gagnants évalués à l'exécution 0,3 s.", "",
    "| Variante | Période | Signaux R8 | Signaux variante | Perdants sautés | Gagnants sautés | Résultat des sautés (R8) | Côté inversé | Instant déplacé > 0,5 s | Cycles nouveaux | R8 | Variante | Δ vs GARDER (0,3 s) [IC 90 % blocs 1 h] | Δ délai 0 |",
    "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for r in B_rows:
    add(f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5]} | {f0(r[6])} | {r[7]} | {r[8]} | {r[9]} | {f0(r[10])} | {f0(r[11])} | **{f0(r[12])}** [{f0(r[13])} ; {f0(r[14])}] | {f0(r[15])} |")
add("", "Pour mémoire, la règle sur la probabilité ENREGISTRÉE (O8, jumeau A « tel que vu par le bot ») : " +
    " ; ".join(f"{p} {pnl({s: v for s, v in SIGS['O8'].items() if PER(s) == p})[1]} achats {f0(pnl({s: v for s, v in SIGS['O8'].items() if PER(s) == p})[0])}" for p in PERS) + ".", "")

# ----------------------------------------------------------------- C
add("## C. Test de gel des sources (une source retardée à la fois, jumeau R8)", "",
    "La source est lue à t − délai (valeur ET heure de réception), les autres à t. **+100 ms est approximatif** : les lignes sont espacées de 0,3 s, donc t − 0,1 s tombe "
    "sur la ligne précédente dans environ 1 cas sur 3 seulement. Binance et Coinbase n'entrent pas dans probaV1 : effet nul par construction (non testés). "
    "Fragilité = (signaux perdus + inversés + déplacés > 0,5 s + nouveaux) / signaux R8.", "",
    "| Source | Délai | |ΔP| médian (toutes lignes) | |ΔP| 99 % | |ΔP| médian aux signaux | Signaux perdus | Inversés | Déplacés | Nouveaux | Fragilité | ΔP&L app. | ΔP&L valid. | ΔP&L test |",
    "|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for r in C_rows:
    add(f"| {r[0]} | +{fr(r[1], 1)} s | {fr(r[2], 4)} | {fr(r[3], 4)} | {fr(r[4], 4)} | {r[5]} | {r[6]} | {r[7]} | {r[8]} | **{fr(100 * r[9], 0)} %** | {f0(r[10]['apprentissage'])} | {f0(r[10]['validation'])} | {f0(r[10]['test'])} |")
add("")

# ----------------------------------------------------------------- D
add("## D. Sauts de probabilité : information nouvelle ou rattrapage de flux ?", "",
    "Règle pré-enregistrée (avant de regarder les résultats) : un saut de la probabilité ENREGISTRÉE entre deux lignes consécutives (≤ 0,5 s) est un **rattrapage** si Bybit ou OKX "
    "change de valeur à cette ligne alors que son âge (indicateur) dépassait 1 s à la ligne précédente. « Retour à 3 s » = mouvement 3 s plus tard rapporté au saut (médiane ; 0 = le saut tient, −1 = entièrement défait).", "")
for th, (n, cnt, rev) in D_rows.items():
    add(f"Seuil |ΔP| ≥ {fr(th)} : {n} sauts.", "", "| Classe | Sauts | Part | Retour à 3 s (médiane) |", "|---|---|---|---|")
    for k, v in cnt.most_common(): add(f"| {k} | {v} | {pc(v, n)} | {fr(rev.get(k, float('nan')))} |")
    add("")
add("Signaux V2-F (O8) selon ce qui s'est passé dans les 3 s de croissance de l'écart (exécution 0,3 s) :", "", "| Période | Classe | Achats | Gagnés | Résultat |", "|---|---|---|---|---|")
for (p, c), v in sorted(D_sig.items()): add(f"| {p} | {c} | {v[0]} | {pc(v[1], v[0])} | {f0(v[2])} |")
add("")

# ----------------------------------------------------------------- E
add("## E. Instantanés « Frankenstein » : les faux désaccords ≥ 0,30 viennent-ils de sources d'âges très différents ?", "",
    f"Premier désaccord ≥ 0,30 de chaque cycle sur la probabilité enregistrée (vendeur 0,02-0,98, ≥ 5 s restantes) : {len(D30)} cycles. Dispersion = âge max − âge min (indicateur). "
    "p = test de permutation unilatéral (perdants plus dispersés que gagnants), 2 000 tirages.", "",
    "| Sources | Perdants | Gagnants | Dispersion médiane perdants | gagnants | Dispersion > 1 s perdants | gagnants | p |", "|---|---|---|---|---|---|---|---|")
for k, v in E_rows.items(): add(f"| {k} | {v[0]} | {v[1]} | {fr(v[2])} s | {fr(v[3])} s | {pc(v[4] * v[0], v[0])} | {pc(v[5] * v[1], v[1])} | {fr(v[6], 3)} |")
add("", "Âges VRAIS (vitesse.json, décisions réelles « desaccord 30 », Bybit / OKX / Chainlink) :", "",
    "| Issue | Décisions | Dispersion médiane | Dispersion > 1 s | Bybit ou OKX > 1 s | Bybit ET OKX > 1 s |", "|---|---|---|---|---|---|")
for k, L in EV.items():
    a = np.array(L, float) if L else np.zeros((0, 3))
    add(f"| {k} | {len(a)} | {fr(np.median(a[:, 0])) if len(a) else '—'} s | {pc(np.sum(a[:, 0] > 1), len(a))} | {pc(np.sum(a[:, 1]), len(a))} | {pc(np.sum(a[:, 2]), len(a))} |")
add("")

# ----------------------------------------------------------------- F
err = np.array([r["err"] for r in F_rows]); nn = np.array([r["n"] for r in F_rows]); e60 = np.array([r["e60"] for r in F_rows])
apres = np.array([SWITCH is not None and r["st"] >= SWITCH for r in F_rows])
add("## F. Fenêtre Chainlink et prix à battre", "",
    f"{len(F_rows)} cycles. Notre K = prix d'exercice enregistré à la première ligne ≥ début + 10 s ; officiel = priceToBeat (officiels.json). "
    "« Secondes reçues » = secondes de [début − 60, début − 1] où la valeur Chainlink a changé (indicateur du compte du bot, qui exige ≥ 40). "
    f"**Le bot a basculé du prix « site » au prix « moyenne Chainlink 60 s » le {hs(SWITCH) if SWITCH else '—'}** (premier cycle à partir duquel ≥ 80 % des cycles suivants utilisent la moyenne, |K − moyenne 60 s recalculée| < 0,5 $) : "
    "avant, K était le prix instantané du site, faux de plusieurs dollars.", "",
    "| Régime | Cycles | |erreur K| médiane | 90 % | 99 % | max | > 2 $ | > 10 $ |", "|---|---|---|---|---|---|---|---|")
for nom, m in (("avant la bascule (K du site)", ~apres), ("après la bascule (K = moyenne 60 s)", apres)):
    if m.any(): add(f"| {nom} | {int(m.sum())} | {fr(np.median(np.abs(err[m])))} $ | {fr(np.percentile(np.abs(err[m]), 90))} $ | {fr(np.percentile(np.abs(err[m]), 99))} $ | {fr(np.max(np.abs(err[m])))} $ | {int(np.sum(np.abs(err[m]) > 2))} | {int(np.sum(np.abs(err[m]) > 10))} |")
ok60 = np.isfinite(e60)
add(f"| moyenne 60 s recalculée sur les lignes (tous cycles) | {int(ok60.sum())} | {fr(np.median(np.abs(e60[ok60])))} $ | {fr(np.percentile(np.abs(e60[ok60]), 90))} $ | {fr(np.percentile(np.abs(e60[ok60]), 99))} $ | {fr(np.max(np.abs(e60[ok60])))} $ | {int(np.sum(np.abs(e60[ok60]) > 2))} | {int(np.sum(np.abs(e60[ok60]) > 10))} |")
ap = [r for r in F_rows if SWITCH is not None and r["st"] >= SWITCH]; apx = [r for r in ap if abs(r["err"]) > 2]
if ap:
    add("", f"Après la bascule, {len(apx)} cycles sur {len(ap)} ont encore |erreur K| > 2 $ ; secondes Chainlink reçues dans ces cycles (indicateur) : médiane {fr(np.median([r['n'] for r in apx]) if apx else float('nan'), 0)} "
        f"(contre {fr(np.median([r['n'] for r in ap]), 0)} pour tous les cycles après bascule) ; parmi eux {sum(1 for r in apx if r['n'] < 40)} ont < 40 secondes reçues (le bot garde alors un autre prix). "
        f"Erreurs : " + ", ".join(f"{hs(r['st'])} {fr(r['err'], 1)} $ ({r['n']} s)" for r in apx[:15]) + ".", "")
add("", "Hypothèse 5 (K calculé avec 40-59 secondes) — erreur de la moyenne 60 s selon le nombre de secondes reçues :", "",
    "| Secondes reçues (indicateur) | Cycles | |erreur moyenne 60 s| médiane | 90 % | > 2 $ |", "|---|---|---|---|---|")
for lo, hi, nom in ((60, 61, "60"), (50, 60, "50-59"), (40, 50, "40-49"), (0, 40, "< 40")):
    m = (nn >= lo) & (nn < hi) & ok60
    add(f"| {nom} | {int(m.sum())} | {fr(np.median(np.abs(e60[m]))) if m.any() else '—'} $ | {fr(np.percentile(np.abs(e60[m]), 90)) if m.any() else '—'} $ | {int(np.sum(np.abs(e60[m]) > 2))} |")
efa = np.array([r["ef_all"] for r in F_rows]); efc = np.array([r["ef_chg"] for r in F_rows])
add("", f"Fin de cycle (hypothèse 4) : moyenne des 60 secondes REMPLIES contre prix final officiel : |écart| médian {fr(np.nanmedian(np.abs(efa)))} $ (90 % {fr(np.nanpercentile(np.abs(efa), 90))} $) ; "
    f"moyenne des seules secondes REÇUES (pondération du bot) : {fr(np.nanmedian(np.abs(efc)))} $ (90 % {fr(np.nanpercentile(np.abs(efc), 90))} $). "
    f"La moyenne remplie reproduit mieux l'officiel dans {pc(np.sum(np.abs(efa) < np.abs(efc)), np.sum(np.isfinite(efa) & np.isfinite(efc)))} des cycles.", "")
# corrélation avec les faux désaccords
bins = [(0, 0.5), (0.5, 2), (2, 1e9)]
add("Faux désaccords selon l'erreur de K **dans notre sens** (= de combien notre K faux rendait NOTRE côté plus probable qu'avec le K officiel : (officiel − K) pour Up, (K − officiel) pour Down) :", "",
    "| Signaux | Régime | Erreur dans notre sens | Signaux | Perdus | Taux de perte | Résultat (exécution 0,3 s) |", "|---|---|---|---|---|---|---|")
for nomS, SS in (("désaccord ≥ 0,30 (O8)", D30), ("V2-F (O8)", SIGS["O8"])):
    for reg, cond in (("avant bascule", lambda st: SWITCH is None or st < SWITCH), ("après bascule", lambda st: SWITCH is not None and st >= SWITCH)):
        for lo, hi, nb in ((-1e9, -2, "< −2 $ (contre nous)"), (-2, 2, "−2 à +2 $"), (2, 10, "+2 à +10 $"), (10, 1e9, "> +10 $ (pour nous)")):
            L = [(st, x) for st, x in SS.items() if st in FR and cond(st) and lo <= (-FR[st]["err"] if x[1] else FR[st]["err"]) < hi]
            if not L: continue
            nl = sum(1 for st, x in L if GAGN[st] != x[1])
            add(f"| {nomS} | {reg} | {nb} | {len(L)} | {nl} | {pc(nl, len(L))} | {f0(sum((execu(st, x) or {'pn': 0})['pn'] for st, x in L))} |")
# K provisoire
prov = [(st, s) for st, s in SIGS["O8"].items() if T[s[0]] - st < (FR[st]["tfin"] if st in FR else 0)]
add("", f"Signaux V2-F (O8) pris AVANT que K ne passe à la moyenne Chainlink (K provisoire du site) : {len(prov)} ; résultat {f0(sum((execu(st, s) or {'pn': 0})['pn'] for st, s in prov))}.", "")

# ----------------------------------------------------------------- G
add("## G. Causalité et déterminisme", "",
    f"- Lignes strictement croissantes dans le temps : {'oui' if mono else 'NON'} ; lignes dans leur cycle [début, début + 300) : {100 * incyc:.2f} %.",
    "- Ce fichier : toute valeur à t = dernière ligne ≤ t (`searchsorted(..., 'right') − 1`) ; exécution = première ligne ≥ t + délai (`'left'`) ; 3 s avant = dernière ligne ≤ t − 3 ; "
    "séries à la seconde = secondes COMPLÈTES ≤ ts − 1 + valeur à la date pour la seconde courante.",
    f"- Déterminisme : deux passes du rejeu F8 → empreintes {G_hash[0]} / {G_hash[1]} ; deux passes de R8 → {H_A0} / {H_A} : {'identiques' if G_hash[0] == G_hash[1] and H_A == H_A0 else 'DIFFÉRENTES'}.",
    "- Anciens chargeurs audités :",
    "  - `robustesse_E.py` : `sec(nom, s) = der(nom, s + 0,999)` n'est utilisé que pour des secondes < seconde de décision (σ, écart, fenêtre `range(deb, s)`) → **pas de fuite**.",
    "  - `meta_router.py` (`P1`, `CL1`, `volr`, `baser`) repris par `attribution_001.parts_r` et `hedge_lab_commun` (X8, X1, H1, X15/P15/H15, cohorte B) : la seconde COURANTE "
    "est lue en fin de seconde (`range(s − 300, s + 1)`, `range(deb, s + 1)`) → **fuite jusqu'à 0,999 s** dans σ, l'écart et la moyenne Chainlink de la fenêtre.",
    "  - `v3_commun.exe` / `attribution_001.execu` : exécution à la première ligne ≥ t + délai, prix ≤ prix de décision → pas de fuite ; `J3` = dernière ligne ≤ t − 3 → pas de fuite.",
    "  - `hedge_lab_commun.arr` : report de la dernière valeur connue (passé seulement) → pas de fuite.",
    "  - Sélection des cycles par l'existence d'un résultat officiel : n'utilise pas l'issue pour décider → pas de fuite de décision.", "",
    "Impact mesuré de la fuite de `parts_r` (même modèle calculé avec la fin de seconde = « fuite », puis avec la valeur à la date) :", "",
    "| Modèle | |ΔP| médian | |ΔP| 99 % | Signaux V2-F avec fuite | sans fuite | Cycles dont le signal change | P&L app. fuite → sans | valid. | test |", "|---|---|---|---|---|---|---|---|---|---|")
for k, v in G_leak.items():
    add(f"| {k} | {fr(v[0], 4)} | {fr(v[1], 3)} | {v[2]} | {v[3]} | {v[4]} | {f0(v[5]['apprentissage'][0])} → {f0(v[5]['apprentissage'][1])} | {f0(v[5]['validation'][0])} → {f0(v[5]['validation'][1])} | {f0(v[5]['test'][0])} → {f0(v[5]['test'][1])} |")
add("")

# ----------------------------------------------------------------- H
add("## H. Rejet par le marché (H186/H187, version rapide)", "",
    f"Signaux V2-F (O8). Mouvement du modèle pour notre côté sur les 3 s ≥ X, X = médiane de l'apprentissage = {fr(Xh, 3)}. « Le marché suit » = notre meilleur vendeur a monté d'au moins 1 c "
    "à t + k. Résultat = entrée au signal (exécution 0,3 s) gardée jusqu'au règlement (GARDER) ; variante exécutable = si rejet, revendre au meilleur acheteur à t + k (quantité affichée).", "",
    "| k | Période | Classe | Achats | Gagnés | GARDER | Sortie si rejet | Δ |", "|---|---|---|---|---|---|---|---|")
for k, agg in H_res.items():
    for (p, c), v in sorted(agg.items()):
        add(f"| {k} s | {p} | {c} | {v[0]} | {pc(v[1], v[0])} | {f0(v[2])} | {f0(v[3])} | {f0(v[3] - v[2])} |")
add("")

# ----------------------------------------------------------------- I
add("## I. Conservation des probabilités et complémentarité des carnets", "",
    f"- P(Down) = 1 − P(Up) **par construction** dans le code (le bot n'enregistre que P(Up) ; toutes les règles utilisent 1 − p) : conservation exacte, rien à tester numériquement. "
    f"P(Up) enregistrée dans [{fr(I_res['prange'][0], 4)} ; {fr(I_res['prange'][1], 4)}].",
    f"- Carnets ({I_res['n']} lignes complètes) : Up acheteur + Down vendeur = 1 → écarts > 1e-6 : {I_res['c1n']} (max {fr(I_res['c1'], 4)}) ; Up vendeur + Down acheteur = 1 → {I_res['c2n']} (max {fr(I_res['c2'], 4)}). "
    f"Tailles miroirs différentes : {I_res['z1']} / {I_res['z2']} lignes. Les deux carnets sont donc le MÊME carnet vu des deux côtés (Polymarket croise Up et Down).",
    f"- Somme des deux meilleurs vendeurs : médiane {fr(I_res['sa_med'])} ; lignes où Up vendeur + Down vendeur < 1 (arbitrage apparent = instantané incohérent) : {I_res['sa_lt1']} ; "
    f"Up acheteur + Down acheteur > 1 : {I_res['sb_gt1']}.", "")

# ----------------------------------------------------------------- J
add("## J. Jumeau causal (hors ligne) : A = R8 (comme le bot), B = F8 (fraîcheur)", "",
    "Chaque divergence (cycle où A et B ne font pas la même chose), avec le P&L marginal B − A (exécution 0,3 s).", "",
    "| Cycle | Période | A : côté · instant · prix | B : côté · instant · prix | Type | A P&L | B P&L | B − A |", "|---|---|---|---|---|---|---|---|")
SA, SB = SIGS["R8"], SIGS["F8"]; tot = collections.Counter(); totpl = collections.defaultdict(float)
for st in sorted(set(SA) | set(SB)):
    a, b = SA.get(st), SB.get(st)
    if a and b and a[1] == b[1] and abs(T[a[0]] - T[b[0]]) <= 0.5: continue
    xa = execu(st, a) if a else None; xb = execu(st, b) if b else None
    typ = "B saute" if not b else ("B seul" if not a else ("côté inversé" if a[1] != b[1] else "instant déplacé"))
    pa, pb = (xa["pn"] if xa else 0.0), (xb["pn"] if xb else 0.0); tot[typ] += 1; totpl[typ] += pb - pa
    fa = (lambda s: f"{'Up' if s[1] else 'Down'} · {int(T[s[0]] - st)} s · {fr(s[2])}")
    add(f"| {hs(st)} | {PER(st)} | {fa(a) if a else '—'} | {fa(b) if b else '—'} | {typ} | {f0(pa)} | {f0(pb)} | {f0(pb - pa)} |")
add("", "Total des divergences : " + " ; ".join(f"{k} {v} ({f0(totpl[k])})" for k, v in tot.most_common()) + ".", "")

# ----------------------------------------------------------------- conclusion et verdict
gB = lambda m, p: [r for r in B_rows if r[0] == m and r[1] == p][0]
def cls_B(m):
    v, t = gB(m, "validation"), gB(m, "test")
    if v[13] > 0 and t[13] > 0: return "hypothèse prometteuse"
    if v[14] < 0 or t[14] < 0: return "résultat négatif (IC entièrement négatif sur une période)"
    return "résultat négatif (aucun gain démontré)"
PAB = {"apprentissage": "app.", "validation": "valid.", "test": "test"}
def txtB(m): return " ; ".join(f"{PAB[p]} {f0(gB(m, p)[12])} [{f0(gB(m, p)[13])} ; {f0(gB(m, p)[14])}]" for p in PERS)
ep_L = [x for x in EP27 if x["perdu"]]; ep_e = [(x, etat(x["t"])) for x in ep_L]
ep_nodiv = sum(1 for x, e in ep_e if e is not None and raison(e, x["cote"] == "Up").startswith("pas de divergence"))
vL = [v for k in ("série de 18 pertes (11.10)", "autres perdants") for v in gv[k]]; vW = gv["gagnants"]
rl = np.mean([v["agePerp"] > 1 for v in vL]); rw = np.mean([v["agePerp"] > 1 for v in vW])
d30L = np.mean([x[1] for x in EV["perdu"]]) if EV["perdu"] else np.nan; d30W = np.mean([x[1] for x in EV["gagné"]]) if EV["gagné"] else np.nan
ex_hi = max(0.0, rl - rw)
Dc = collections.defaultdict(float)
for (p_, c), v in D_sig.items():
    if c.startswith("rattrapage"): Dc[p_] += v[2]
a_px = np.array(cmp["bybit"])
VERD = [
    f"- **La « série de ~27 pertes »** : aucune suite ininterrompue de 27 pertes dans `V2-F_ecart_qui_grandit_BTC.json`. Ce qui s'en approche : **27 pertes en {len(EP27)} trades** "
    f"({hss(EP27[0]['t'])} → {hss(EP27[-1]['t'])}, {f0(sum(x['net'] for x in EP27))}, période de validation, AVANT la bascule du prix d'exercice) ; la plus longue suite ininterrompue = {best[0]} pertes "
    f"({hss(SN[0]['t'])} → {hss(SN[-1]['t'])}), dont {sum(1 for x in SN if x['t'] <= TMAX)} seulement couvertes par les lignes enregistrées (fin le {hss(TMAX)}).",
    f"- **Dans l'épisode des 27 pertes, le temps n'explique presque rien** : pour {ep_nodiv} des {len(ep_L)} perdants, la politique de fraîcheur change notre probabilité de moins de 0,02 ; "
    f"le K faux (prix du site, |erreur| jusqu'à {fr(max(abs(FR[x['start']]['err']) for x in EP27 if x['start'] in FR), 0)} $) baisse notre probabilité de {fr(_kL[1])} en médiane chez les perdants, mais aussi de {fr(_kW[1])} chez les gagnants (sur tous les trades d'avant la bascule : "
    f"{fr(_aL[1])} contre {fr(_aW[1])}) → le K faux a fabriqué des signaux, sans distinguer perdants et gagnants.",
    f"- **Politique de fraîcheur complète (F8) contre le jumeau du bot (R8)**, règle V2-F, exécution 0,3 s, Δ vs GARDER : {txtB('F8')} → **{cls_B('F8')}**. "
    f"Composantes : σ « secondes changées » {txtB('R8+σ')} → **{cls_B('R8+σ')}** (elle gonfle σ d'un facteur ≈ 2 par marché calme) ; σ sans cache {txtB('R8+σ sans cache')} ; "
    f"écarts recalculés chaque seconde {txtB('R8+écarts')} ; exclusion des sources > 1 s (indicateur) {txtB('R8+exclusion')}. "
    f"Variante « 60 rendements changés exigés » : {txtB('F8 (σ : 60 rendements changés exigés)')} — le gain du test vient de ne plus trader quand le marché est calme, pas de la fraîcheur, et la validation est négative → **résultat négatif**.",
    f"- **L'âge « indicateur » des lignes 0,3 s ne mesure pas la fraîcheur** : Bybit médiane {fr(np.median(a_px[:, 0]))} s contre {fr(np.median(a_px[:, 1]))} s d'âge vrai, corrélation {fr(np.corrcoef(a_px[:, 0], a_px[:, 1])[0, 1])} "
    "(un marché calme ressemble à un flux coupé). Tout ce qui repose sur cet indicateur (exclusion, rattrapage, Frankenstein) est au mieux une **hypothèse**, jamais une preuve.",
    f"- **Âges VRAIS (vitesse.json, {len(vL) + len(vW)} trades V2-F réels depuis le 10.10 14:17)** : Bybit > 1 s chez {pc(rl * len(vL), len(vL))} des perdants contre {pc(rw * len(vW), len(vW))} des gagnants ; "
    f"la règle « Bybit ET OKX > 1 s → pas de décision » aurait sauté {len(sk)} trades ({sum(x['perdu'] for x in sk)} perdants, {sum(not x['perdu'] for x in sk)} gagnants, {f0(-sum(x['net'] for x in sk))} contre GARDER) → "
    "**hypothèse prometteuse, données insuffisantes** (14 trades). Sur les décisions réelles « desaccord 30 », c'est l'inverse (Bybit ou OKX > 1 s : "
    f"{pc(d30L * len(EV['perdu']), len(EV['perdu']))} des perdants contre {pc(d30W * len(EV['gagné']), len(EV['gagné']))} des gagnants).",
    f"- **Prix d'exercice** : jusqu'au {hs(SWITCH) if SWITCH else '—'} le bot utilisait le prix instantané du site (|erreur| médiane {fr(np.median(np.abs(err[~apres])))} $, 90 % {fr(np.percentile(np.abs(err[~apres]), 90))} $) ; "
    f"depuis, la moyenne Chainlink 60 s ({fr(np.median(np.abs(err[apres])))} $) → **correction technique prouvée, déjà en place**. Il reste {len(apx)} cycles sur {len(ap)} à plus de 2 $ après la bascule "
    f"(dont {sum(1 for r in apx if r['n'] < 40)} avec < 40 secondes Chainlink reçues) : **hypothèse prometteuse** (hypothèse 5) à suivre. Rejeu « R8 + K 60 s » : {txtB('R8+K 60 s')}.",
    f"- **Fuite de données dans les études précédentes** : `meta_router.parts_r` (X8/X1/H1, cohorte B du Hedge Lab) lit la seconde courante en FIN de seconde (jusqu'à 0,999 s de futur) → "
    f"**correction technique prouvée** ; impact faible ({G_leak['X8 (0,08 %)'][4]} et {G_leak['X15 (0,015 %, cohorte B du Hedge Lab)'][4]} cycles changent). Ce fichier : pas de fuite, deux passes identiques.",
    f"- **Rattrapage de flux (D)** : les signaux V2-F dont la croissance de 3 s contient un saut « rattrapage » perdent dans les trois périodes "
    f"(app. {f0(Dc['apprentissage'])}, valid. {f0(Dc['validation'])}, test {f0(Dc['test'])}) → **hypothèse prometteuse** (petits effectifs, indicateur d'âge). "
    "Rejet par le marché (H) : signes opposés entre apprentissage et validation → **résultat négatif**. Conservation (I) : carnets Up/Down parfaitement miroirs, P(Down) = 1 − P(Up) par construction → rien à corriger.",
    f"- **Conclusion chiffrée** : parmi les faux désaccords ≥ 0,30 du rejeu, {pc(FL30['perdu']['au moins un des drapeaux'], NF30['perdu'])} portent un drapeau temporel, mais {pc(FL30['gagné']['au moins un des drapeaux'], NF30['gagné'])} des gagnants aussi : "
    f"**part attribuable démontrée ≈ 0 %** ; borne haute avec les âges vrais (excès de « Bybit > 1 s » chez les perdants V2-F) ≈ **{100 * ex_hi:.0f} %**. "
    f"**Au moins {100 - 100 * ex_hi:.0f} % des fausses alertes restent inexpliquées** par les défauts temporels mesurables à 0,3 s : le problème principal est ailleurs (modèle / sélection des signaux).",
]
i_v = out.index("@@VERDICT@@"); out[i_v:i_v + 1] = VERD
add("## Conclusion chiffrée et classement", "",
    "| Constat | Classement |", "|---|---|",
    "| Fuite de 0 à 0,999 s dans `meta_router.parts_r` (X8/X1/H1, cohorte B) | **correction technique prouvée** (à corriger dans les études ; impact faible, section G) |",
    f"| K = prix du site jusqu'au {hs(SWITCH) if SWITCH else '—'} | **correction technique prouvée, déjà en place** (F) |",
    f"| (1) σ et écart perp → Chainlink en cache 5 s | σ sans cache : {cls_B('R8+σ sans cache')} ; écarts sans cache : {cls_B('R8+écarts')} |",
    f"| (2) série remplie → σ sous-estimée | σ « secondes changées » : {cls_B('R8+σ')} ; la variance par unité de temps n'est pas biaisée par le remplissage si le rattrapage est dans la fenêtre |",
    f"| (3) prix rapide = source reçue la plus récente | exclusion > 1 s sur l'indicateur : {cls_B('R8+exclusion')} ; âges vrais : hypothèse prometteuse, **données insuffisantes** (14 trades) |",
    f"| (4) pondération des secondes Chainlink manquantes dans E | moyenne remplie plus proche de l'officiel dans {pc(np.sum(np.abs(efa) < np.abs(efc)), np.sum(np.isfinite(efa) & np.isfinite(efc)))} des cycles → **hypothèse prometteuse** (correction possible : remplir les secondes manquantes) |",
    f"| (5) K avec 40-59 secondes | 40-59 s : erreur médiane ≈ 0,1 $ → **résultat négatif** ; < 40 s : {fr(np.median(np.abs(e60[(nn < 40) & ok60])))} $ → **hypothèse prometteuse** |",
    "| (6) prixA 6 s de recul / gel Chainlink ≤ 1 s | |ΔP| ≤ 0,0001 → **résultat négatif** (Chainlink n'entre que par des moyennes) |",
    "| Gel Bybit / OKX (C) | fragilité 8-40 % des signaux déplacés, ΔP&L de signe instable → **résultat négatif** (pas de sensibilité systématique) |",
    "| Rattrapage de flux avant le signal (D) | **hypothèse prometteuse** (indicateur) |",
    f"| Frankenstein (E) | indicateur : perdants plus dispersés (p = {fr(E_rows['Bybit / OKX / Chainlink (sources du modèle)'][6], 3)}) ; âges vrais : l'inverse → **données insuffisantes** |",
    "| Rejet par le marché H186/H187 (H) | **résultat négatif** |",
    "| Conservation des probabilités / carnets (I) | rien à corriger |",
    f"| Part des faux désaccords potentiellement temporelle | démontrée ≈ 0 % ; borne haute ≈ {100 * ex_hi:.0f} % ; inexpliqué ≥ {100 - 100 * ex_hi:.0f} % |", "",
    "Détail des drapeaux (désaccords ≥ 0,30 du rejeu, probabilité enregistrée) :", "", "| Drapeau | Perdants | Gagnants |", "|---|---|---|")
for k in FL30["perdu"]:
    add(f"| {k} | {pc(FL30['perdu'][k], NF30['perdu'])} | {pc(FL30['gagné'][k], NF30['gagné'])} |")
add("", f"Mêmes drapeaux sur les trades RÉELS V2-F couverts par les lignes ({NFL['perdu']} perdants, {NFL['gagné']} gagnants) :", "", "| Drapeau | Perdants | Gagnants |", "|---|---|---|")
for k in FL["perdu"]:
    add(f"| {k} | {pc(FL['perdu'][k], NFL['perdu'])} | {pc(FL['gagné'][k], NFL['gagné'])} |")
add("", "### Ce que l'enregistreur de Dublin permettra de vérifier", "",
    "- **Âge vrai de chaque source à chaque instant** (dernier prix + horodatage de la SOURCE toutes les 50 ms) : remplace l'indicateur « dernier changement », qui confond un marché calme "
    "et un flux coupé ; permet de rejouer F8 exactement et de séparer latence réseau et avance réelle.",
    "- **Carnet Polymarket avec horodatages Polymarket** : mesurer si le carnet a bougé AVANT notre flux (le vrai test de H186/H187 et du rattrapage, section D), à 50 ms au lieu de 0,3 s ; "
    "rendre exact le +100 ms de la section C.",
    "- **Transactions** : savoir si une offre a disparu par exécution (quelqu'un l'a prise) ou par retrait (le teneur de marché a reculé) — la cause des « offres disparues ».",
    "- **Limite actuelle** : branche `donnees-rapide` avec très peu de cycles : aucune conclusion statistique possible avant plusieurs centaines de cycles.", "")
open("etude/bot5min/resultat_audit_temporel.md", "w").write("\n".join(out))
log("écrit etude/bot5min/resultat_audit_temporel.md", len(out), "lignes")
