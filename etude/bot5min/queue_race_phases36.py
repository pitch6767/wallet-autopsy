"""BOT95 — QUEUE RACE ENGINE, PHASES 3 à 6 (14.10.2026). Hors ligne : aucun bot, aucun fantôme, aucun paramètre modifié, aucun ordre.
Phase 3 : deux modèles simples et séparés (régression logistique, 10 variables FIXÉES À L'AVANCE) — « retrait vendeur » et « consommation
acheteuse » de la meilleure offre dans les h ms qui suivent notre délai. Découpage chronologique par cycle : apprentissage 50 % / validation 25 % /
test 25 %. Phase 4 : course avec nos délais réels. Phase 5 : fantômes R / S / RS simulés hors ligne contre le moteur C sur les MÊMES signaux.
Phase 6 : synthèse (écrite dans le .md).
Entrées : résumés par cycle produits par queue_race_phases.py (QR_FEAT) + fichiers bruts (QR_CACHE) pour la profondeur du carnet aux signaux.
Usage : QR_CACHE=<cycles> QR_FEAT=<résumés> python3 etude/bot5min/queue_race_phases36.py → etude/bot5min/resultat_queue_race_phases36.md"""
import os, sys, json, math, time, collections, bisect
import numpy as np

T0 = time.time()
ICI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, ICI)
import queue_race_phases as Q                     # normaliser, Livre, etats_aux_instants (aucune modification de ce module)

RACINE = Q.RACINE
SORTIE = os.path.join(RACINE, "etude", "bot5min", "resultat_queue_race_phases36.md")
FEAT = Q.FEAT
rng = np.random.default_rng(36)

# ---------------------------------------------------------------- paramètres FIXÉS AVANT tout calcul de résultat
PAS = 250                 # ms : grille d'instants « éligibles » dans chaque cycle (0 → 300 s), les deux côtés
POLY_DUBLIN = 8.6; CALCUL = 0.1; ALLER = 14.0; RTT = 28.0
DELTA = POLY_DUBLIN + CALCUL + ALLER              # 22,7 ms : un événement plus proche que ça ne peut pas être devancé
H = 500                   # ms : horizon principal de prédiction (après DELTA) ; sensibilité 200 ms
H2 = 200
PART = (0.50, 0.75)       # découpage chronologique des cycles : apprentissage < 50 % ≤ validation < 75 % ≤ test
ALERTE_Q = 0.95           # phase 4 : alerte = probabilité ≥ 95e centile des probabilités de VALIDATION (top 5 %)
BUDGET = 50.0             # $ par signal
FEE = lambda p: 0.07 * p * (1 - p)
GRILLE = (0.5, 0.6, 0.7, 0.8, 0.9)   # phase 5 : seuils candidats = ces centiles de la probabilité sur les signaux refusés par C (apprentissage+validation)
NB_BOOT = 10000
VARS = ["déséquilibre du microprix vers l'offre", "log taille de l'offre", "écart acheteur-vendeur (‰)", "variation log taille de l'offre 200 ms",
        "variation log taille d'en face 200 ms", "log âge du meilleur prix (ms)", "logit du prix de l'offre", "mouvement du perp Bybit 500 ms ($, sens favorable)",
        "flux agressif net 500 ms (k$, sens favorable)", "log volume exécuté sur l'offre 500 ms"]


def charger():
    fs = sorted(f for f in os.listdir(FEAT) if f.endswith(".npz"))
    out = []
    for f in fs:
        z = np.load(os.path.join(FEAT, f)); out.append({k: z[k] for k in z.files})
    return out


# ---------------------------------------------------------------- variables à des instants donnés (tout ce qui est connu à l'heure de réception T)
def prep(D):
    S = D["serie"]; P = {}
    if len(S) == 0: return None
    for s in (0, 1):
        own = S[:, 3] if s == 1 else S[:, 1]
        ch = np.ones(len(S), bool); ch[1:] = own[1:] != own[:-1]
        li = np.maximum.accumulate(np.where(ch, np.arange(len(S)), 0)); P[("tchg", s)] = S[li, 0]
    tr = D["trades"]; T_ = {}
    for s in (0, 1):
        m = tr[:, 2] == s
        for c in np.unique(tr[m, 3]):
            mm = m & (tr[:, 3] == c); o = np.argsort(tr[mm, 0]); tt = tr[mm, 0][o]; cs = np.concatenate([[0], np.cumsum(tr[mm, 4][o])])
            T_[(s, c)] = (tt, cs)
    P["tr"] = T_
    fx = D["fx"]; P["fx"] = (fx[:, 0], np.concatenate([[0], np.cumsum(fx[:, 1])])) if len(fx) else None
    B = D["baisses"]; F = {}; A = {}
    for s in (0, 1):
        for c in np.unique(B[B[:, 2] == s, 3]):
            m = (B[:, 2] == s) & (B[:, 3] == c)
            A[(s, c)] = B[m]
            mf = m & (B[:, 6] > 0); F[(s, c)] = B[mf]
    P["full"] = F; P["all"] = A
    return P


def at(S, T):
    i = np.searchsorted(S[:, 0], T, "right") - 1
    ok = i >= 0; i = np.maximum(i, 0); return S[i], ok


def features(D, P, T, s):
    """T : tableau d'heures (réception, ms) ; s : 1 = offre Up, 0 = offre Down (= demande Up par miroir)"""
    S = D["serie"]; a, ok = at(S, T); b, okb = at(S, T - 200)
    bb, bz, ba, az = a[:, 1], a[:, 2], a[:, 3], a[:, 4]
    spread = ba - bb; mid = (bb + ba) / 2
    with np.errstate(invalid="ignore", divide="ignore"):
        micro = np.where(bz + az > 0, (bb * az + ba * bz) / np.maximum(bz + az, 1e-9), mid)
        tilt = np.where(spread > 0, (micro - mid) / (spread / 2), 0.0)
    if s == 1: own_p, own_z, face_z, own_z_b, face_z_b, sg = ba, az, bz, b[:, 4], b[:, 2], 1.0
    else: own_p, own_z, face_z, own_z_b, face_z_b, sg, tilt = bb, bz, az, b[:, 2], b[:, 4], -1.0, -tilt
    ptok = (own_p if s == 1 else 1000 - own_p) / 1000.0
    i = np.maximum(np.searchsorted(S[:, 0], T, "right") - 1, 0); age = T - P[("tchg", s)][i]
    pe = D["perp"]
    if len(pe):
        j1 = np.searchsorted(pe[:, 0], T, "right") - 1; j0 = np.searchsorted(pe[:, 0], T - 500, "right") - 1
        dp = np.where((j1 >= 0) & (j0 >= 0), pe[np.maximum(j1, 0), 1] - pe[np.maximum(j0, 0), 1], 0.0) * sg
    else: dp = np.zeros(len(T))
    if P["fx"] is not None:
        ft, cs = P["fx"]; fxv = (cs[np.searchsorted(ft, T, "right")] - cs[np.searchsorted(ft, T - 500, "right")]) / 1000.0 * sg
    else: fxv = np.zeros(len(T))
    vex = np.zeros(len(T))
    for k in range(len(T)):
        x = P["tr"].get((s, own_p[k]))
        if x is not None: tt, cs = x; vex[k] = cs[np.searchsorted(tt, T[k], "right")] - cs[np.searchsorted(tt, T[k] - 500, "right")]
    X = np.column_stack([tilt, np.log1p(own_z), spread, np.log1p(own_z) - np.log1p(own_z_b), np.log1p(face_z) - np.log1p(face_z_b),
                         np.log1p(np.maximum(age, 0)), np.log(np.clip(ptok, 1e-3, 1 - 1e-3) / (1 - np.clip(ptok, 1e-3, 1 - 1e-3))), dp, fxv, np.log1p(vex)])
    valide = ok & okb & np.isfinite(X).all(1) & (ptok >= 0.03) & (ptok <= 0.97) & (own_z > 0)
    return X, valide, own_p


def evenements(D, P, T, s, own_p):
    """prochaine disparition complète du niveau visé (même côté, même prix) après T : délai (réception), heure Polymarket, cause ;
    1re baisse quelconque de ce niveau après T (heure Polymarket) ; niveau encore achetable à T + 28 ms ; valeur à 5 s (‰)."""
    n = len(T); dt = np.full(n, np.inf); ts = np.full(n, np.nan); cause = np.zeros(n); ts1 = np.full(n, np.nan)
    for k in range(n):
        Fk = P["full"].get((s, own_p[k]))
        if Fk is not None and len(Fk):
            i = np.searchsorted(Fk[:, 0], T[k], "right")
            if i < len(Fk): dt[k] = Fk[i, 0] - T[k]; ts[k] = Fk[i, 1]; cause[k] = Fk[i, 7]
        Ak = P["all"].get((s, own_p[k]))
        if Ak is not None and len(Ak):
            i = np.searchsorted(Ak[:, 0], T[k], "right")
            if i < len(Ak): ts1[k] = Ak[i, 1]
    S = D["serie"]; a28, _ = at(S, T + RTT); a5, _ = at(S, T + 5000)
    if s == 1: encore = (a28[:, 3] <= own_p) & (a28[:, 4] >= 1); val5 = (a5[:, 1] + a5[:, 3]) / 2 - own_p
    else: encore = (a28[:, 1] >= own_p) & (a28[:, 2] >= 1); val5 = own_p - (a5[:, 1] + a5[:, 3]) / 2
    return dt, ts, cause, ts1, encore, val5


def jeu(DS):
    """grille d'instants éligibles pour tous les cycles"""
    rows = []
    for ci, D in enumerate(DS):
        st, coupe, tfin = D["meta"][0] * 1000, D["meta"][1], D["meta"][2]
        P = prep(D)
        if P is None: continue
        T = st + PAS / 2 + np.arange(0, 300000, PAS, dtype=float)
        if coupe: T = T[T + DELTA + H <= tfin]
        if len(T) == 0: continue
        for s in (0, 1):
            X, v, own = features(D, P, T, s)
            T_, X, own = T[v], X[v], own[v]
            if len(T_) == 0: continue
            dt, ts, cause, ts1, encore, val5 = evenements(D, P, T_, s, own)
            ptok = (own if s == 1 else 1000 - own) / 1000.0
            rows.append(dict(ci=np.full(len(T_), ci), side=np.full(len(T_), s), T=T_, X=X, dt=dt, ts=ts, cause=cause, ts1=ts1, encore=encore, val5=val5, p=ptok))
        D["_P"] = P
    return {k: np.concatenate([r[k] for r in rows]) for k in rows[0]}


def labels(J, h):
    dans = (J["dt"] > DELTA) & (J["dt"] <= DELTA + h)
    trop_tot = J["dt"] <= DELTA
    indet = dans & (J["cause"] == 0)
    yr = dans & np.isin(J["cause"], (3, 4)); yc = dans & np.isin(J["cause"], (1, 2))
    garde = ~trop_tot & ~indet
    return yr, yc, garde, trop_tot


# ---------------------------------------------------------------- outils statistiques
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score


def auc_ic(y, p, g, nb=200):
    """AUC et IC 90 % par bootstrap des cycles"""
    a = roc_auc_score(y, p); u, inv = np.unique(g, return_inverse=True); idx = [np.where(inv == k)[0] for k in range(len(u))]; v = []
    for _ in range(nb):
        k = rng.integers(0, len(u), len(u)); ii = np.concatenate([idx[j] for j in k])
        if y[ii].min() == y[ii].max(): continue
        v.append(roc_auc_score(y[ii], p[ii]))
    return a, np.percentile(v, 5), np.percentile(v, 95)


def brier(y, p): return float(np.mean((p - y) ** 2))


def boot_cycles(d_par_cycle, nb=NB_BOOT, alpha=(0.10,)):
    v = np.array(list(d_par_cycle.values())); n = len(v)
    if n == 0: return {a: (0.0, 0.0) for a in alpha}
    tot = v[rng.integers(0, n, (nb, n))].sum(1)
    return {a: (float(np.percentile(tot, 100 * a / 2)), float(np.percentile(tot, 100 * (1 - a / 2)))) for a in alpha}


fr = lambda x, d=1: "—" if x is None or (isinstance(x, float) and (math.isnan(x) or math.isinf(x))) else f"{x:,.{d}f}".replace(",", " ").replace(".", ",")
pc = lambda a, b: "—" if not b else f"{100 * a / b:.1f} %".replace(".", ",")
sgn = lambda x: ("+" if x >= 0 else "−") + fr(abs(x), 0) + " $"
JOUR = lambda st: time.strftime("%d.%m %H:%M", time.gmtime(st + 7200))


# ---------------------------------------------------------------- phase 5 : simulation d'un achat à cours limité contre le carnet reconstruit
def achetable(L, up, cap, budget=BUDGET):
    """parts et coût (frais compris) au prix plafond ou mieux, profondeur reconstruite (jeton acheté : Up = offres Up ; Down = miroir des demandes Up)"""
    if up: niv = sorted((c / 1000.0, z) for c, z in L.a.items())
    else: niv = sorted(((1000 - c) / 1000.0, z) for c, z in L.b.items())
    q = c_ = 0.0
    for p, z in niv:
        if p > cap + 1e-9: break
        k = min(z, (budget - c_) / (p + FEE(p)))
        if k <= 0: break
        q += k; c_ += k * (p + FEE(p))
    return q, c_


def main():
    DS = charger(); nc = len(DS)
    starts = np.array([D["meta"][0] for D in DS])
    b1, b2 = int(nc * PART[0]), int(nc * PART[1])
    per = np.array(["app"] * b1 + ["val"] * (b2 - b1) + ["test"] * (nc - b2))
    print("cycles", nc, f"{time.time() - T0:.0f} s", flush=True)
    J = jeu(DS); print("instants", len(J["T"]), f"{time.time() - T0:.0f} s", flush=True)
    perJ = per[J["ci"]]
    md = []; w = md.append
    RES = {}
    # ================================================= PHASE 3
    M = {}
    for h in (H, H2):
        yr, yc, garde, trop = labels(J, h)
        for nom, y in (("retrait", yr), ("consommation", yc)):
            tr_ = garde & (perJ == "app")
            sc = StandardScaler().fit(J["X"][tr_]); m = LogisticRegression(max_iter=2000, C=1.0).fit(sc.transform(J["X"][tr_]), y[tr_])
            p = m.predict_proba(sc.transform(J["X"]))[:, 1]
            r = dict(m=m, sc=sc, p=p, y=y, garde=garde, base=float(y[tr_].mean()))
            for per_ in ("val", "test"):
                k = garde & (perJ == per_)
                a, lo, hi = auc_ic(y[k].astype(int), p[k], J["ci"][k]) if h == H else (roc_auc_score(y[k], p[k]), None, None)
                r[per_] = dict(n=int(k.sum()), pos=int(y[k].sum()), auc=a, lo=lo, hi=hi, brier=brier(y[k], p[k]), brier0=brier(y[k], np.full(k.sum(), r["base"])))
                if h == H:
                    q = np.quantile(p[k], np.linspace(0, 1, 11)); b = np.clip(np.searchsorted(q, p[k], "right") - 1, 0, 9)
                    r[per_]["cal"] = [(float(p[k][b == i].mean()), float(y[k][b == i].mean()), int((b == i).sum())) for i in range(10)]
                    r[per_]["uni"] = [roc_auc_score(y[k], J["X"][k][:, j]) for j in range(J["X"].shape[1])]
            M[(nom, h)] = r
        M[("trop", h)] = (int(trop.sum()), len(trop))
        print("phase 3", h, f"{time.time() - T0:.0f} s", flush=True)
    # H545 : le modèle retrait prédit-il la consommation aussi bien que le modèle consommation ? (et un modèle unique « disparition »)
    yr, yc, garde, _ = labels(J, H)
    k = garde & (perJ == "test")
    h545 = dict(ret_sur_cons=roc_auc_score(yc[k], M[("retrait", H)]["p"][k]), cons_sur_ret=roc_auc_score(yr[k], M[("consommation", H)]["p"][k]))
    tr_ = garde & (perJ == "app"); yd = yr | yc
    sc = StandardScaler().fit(J["X"][tr_]); mu = LogisticRegression(max_iter=2000).fit(sc.transform(J["X"][tr_]), yd[tr_]); pu = mu.predict_proba(sc.transform(J["X"]))[:, 1]
    h545["unique_sur_ret"] = roc_auc_score(yr[k], pu[k]); h545["unique_sur_cons"] = roc_auc_score(yc[k], pu[k])
    # ================================================= PHASE 4 : course
    P4 = {}
    for nom, causes in (("retrait", (3, 4)), ("consommation", (1, 2))):
        r = M[(nom, H)]; p = r["p"]
        kv = (perJ == "val") & r["garde"]; seuil = float(np.quantile(p[kv], ALERTE_Q))
        base = (perJ == "test")                                       # tous les instants de test (y compris « trop tôt ») : la course se juge sur tout
        al = base & (p >= seuil)
        def mesures(m):
            ev = m & np.isin(J["cause"], causes) & (J["dt"] <= DELTA + H)          # le niveau disparaît (par cette cause) dans l'horizon
            n_ev = int(ev.sum())
            dem = ev & (J["T"] + CALCUL + ALLER < J["ts"]); rtt = ev & (J["T"] + CALCUL + RTT < J["ts"])
            av1 = m & np.isfinite(J["ts1"]) & (J["dt"] <= DELTA + H) & np.isin(J["cause"], causes); av1o = av1 & (J["T"] + CALCUL + ALLER < J["ts1"])
            enc = m & J["encore"]
            fee = 1000 * 0.07 * J["p"] * (1 - J["p"])
            v5 = J["val5"][enc] - fee[enc]; g5 = J["ci"][enc]; ok5 = np.isfinite(v5); v5b, g5b = v5[ok5], g5[ok5]
            u, inv = np.unique(g5b, return_inverse=True); sm = np.bincount(inv, v5b); ct = np.bincount(inv)
            kk = rng.integers(0, len(u), (2000, len(u))); bm = sm[kk].sum(1) / ct[kk].sum(1)
            return dict(v5_ic=(float(np.percentile(bm, 5)), float(np.percentile(bm, 95))), n=int(m.sum()), n_ev=n_ev, dem=int(dem.sum()), rtt=int(rtt.sum()), av1=int(av1.sum()), av1o=int(av1o.sum()), enc=int(enc.sum()),
                        v5=float(np.nanmean(v5)) if len(v5) else None, v5_med=float(np.nanmedian(v5)) if len(v5) else None)
        P4[nom] = dict(seuil=seuil, alerte=mesures(al), hasard=mesures(base))
    print("phase 4", f"{time.time() - T0:.0f} s", flush=True)
    # ================================================= PHASE 5 : signaux du bot (cohortes A/B, moteur C enregistré)
    rap = json.load(open(os.path.join(RACINE, "bot95", "rapide.json")))["signaux"]
    pos = {int(st): i for i, st in enumerate(starts)}
    SIG = [s for s in rap if s.get("moteurC") and "envoie" in s["moteurC"] and int(s["start"]) in pos and s.get("gagnant")]
    TOUS = [s for s in rap if int(s["start"]) in pos and s.get("gagnant")]
    par_cycle = collections.defaultdict(list)
    for s in TOUS: par_cycle[int(s["start"])].append(s)
    lignes = []
    for st, L in sorted(par_cycle.items()):
        ci = pos[st]; D = DS[ci]; P = D.get("_P") or prep(D)
        path = os.path.join(Q.CACHE, f"{st}.json.gz")
        C = Q.normaliser(path)
        inst = sorted(set([s["tDecision"] + RTT for s in L]))
        E = Q.etats_aux_instants(C, inst)
        for s in L:
            up = s["cote"] == "Up"; side = 1 if up else 0
            X, v, own = features(D, P, np.array([s["tDecision"]]), side)
            pr = M[("retrait", H)]["m"].predict_proba(M[("retrait", H)]["sc"].transform(X))[0, 1] if v[0] else np.nan
            pcs = M[("consommation", H)]["m"].predict_proba(M[("consommation", H)]["sc"].transform(X))[0, 1] if v[0] else np.nan
            ptok_vu = (own[0] if up else 1000 - own[0]) / 1000.0
            Lb = E[s["tDecision"] + RTT][0]
            g = s["gagnant"] == s["cote"]
            mc = s.get("moteurC") or {}
            if Lb is None: qa = ca = qc = cc = 0.0
            else:
                qa, ca = achetable(Lb, up, s["a0"])                                   # achat immédiat au prix du signal (limite = prix du signal)
                qc, cc = achetable(Lb, up, mc["plafond"]) if mc.get("envoie") and mc.get("plafond") else (0.0, 0.0)
            pn = lambda q, c: (q - c if g else -c) if q >= 1 else 0.0
            lat = [v_ for k_, v_ in (mc.get("resultat") or {}).items() if k_.startswith("latence")]
            lignes.append(dict(start=st, per=per[ci], nom=s["nom"], coh=s["nom"].startswith("cohorte"), tD=s["tDecision"], up=up, a0=s["a0"], vu=ptok_vu, gagne=g,
                               pr=pr, pc=pcs, envoie=bool(mc.get("envoie")), pnA=pn(qa, ca), cA=ca if qa >= 1 else 0.0, qA=qa, pnC=pn(qc, cc), cC=cc if qc >= 1 else 0.0, qC=qc,
                               pnC_bot=lat[0] if lat else None, mc=bool(mc and "envoie" in mc)))
    print("phase 5 signaux", len(lignes), f"{time.time() - T0:.0f} s", flush=True)
    LC = [l for l in lignes if l["mc"]]
    ref = [l for l in LC if l["per"] in ("app", "val") and not l["envoie"] and not math.isnan(l["pr"])]
    def choisir(cle):
        vals = np.array([l[cle] for l in ref]); cands = [(None, 0.0)]
        for qq in GRILLE:
            s_ = float(np.quantile(vals, qq)); cands.append((s_, sum(l["pnA"] for l in ref if l[cle] >= s_)))
        best = max(cands, key=lambda x: x[1]); return best, cands
    (sR, gR), candR = choisir("pr"); (sS, gS), candS = choisir("pc")
    def ajout(l, var):
        if l["envoie"] or math.isnan(l["pr"]): return False
        r_ = sR is not None and l["pr"] >= sR; s_ = sS is not None and l["pc"] >= sS
        return {"R": r_, "S": s_, "RS": r_ or s_}[var]
    def strat(L, var):
        """P&L, coût, jackpot par signal (ordre chronologique)"""
        out = []
        for l in sorted(L, key=lambda x: x["tD"]):
            if var == "C" or not ajout(l, var): pn, c = (l["pnC"], l["cC"]) if l["envoie"] else (0.0, 0.0)
            else: pn, c = l["pnA"], l["cA"]
            out.append((l["start"], pn, c, c > 0 and pn >= 4 * c, c > 0))
        return out
    def dd(v):
        cum = np.cumsum([x[1] for x in v]) if v else np.array([0.0]); pk = np.maximum.accumulate(np.concatenate([[0], cum]))
        return float((pk - np.concatenate([[0], cum])).max())
    P5 = {}
    for per_ in ("app", "val", "test"):
        L = [l for l in LC if l["per"] == per_]
        base = strat(L, "C"); P5[(per_, "C")] = dict(pn=sum(x[1] for x in base), c=sum(x[2] for x in base), jp=sum(x[3] for x in base), n=sum(x[4] for x in base), dd=dd(base), nsig=len(L))
        for var in ("R", "S", "RS"):
            v = strat(L, var); d = collections.defaultdict(float)
            for (st, pn, *_), (_, pnb, *_) in zip(v, base): d[st] += pn - pnb
            for st in set(l["start"] for l in L): d.setdefault(st, 0.0)
            ci_ = boot_cycles(d, alpha=(0.10, 0.10 / 3))
            ajoutes = [l for l in L if ajout(l, var)]
            P5[(per_, var)] = dict(pn=sum(x[1] for x in v), c=sum(x[2] for x in v), jp=sum(x[3] for x in v), n=sum(x[4] for x in v), dd=dd(v), delta=sum(d.values()), ic=ci_[0.10], icb=ci_[0.10 / 3],
                                    nadd=len(ajoutes), nadd_fill=sum(1 for l in ajoutes if l["cA"] > 0), jp_add=sum(1 for l in ajoutes if l["cA"] > 0 and l["pnA"] >= 4 * l["cA"]),
                                    perte_add=sum(l["pnA"] for l in ajoutes if l["pnA"] < 0), gain_add=sum(l["pnA"] for l in ajoutes if l["pnA"] > 0), c_add=sum(l["cA"] for l in ajoutes),
                                    cmax=max((sum(x[2] for x in v if x[0] == st) for st in set(x[0] for x in v)), default=0.0))
    # exploratoire (PAS un verdict) : toute la grille sur le test
    EXPL = []
    T_ = [l for l in LC if l["per"] == "test" and not l["envoie"] and not math.isnan(l["pr"])]
    for cle, cand in (("pr", candR), ("pc", candS)):
        for s_, g_ in cand:
            if s_ is None: continue
            sel = [l for l in T_ if l[cle] >= s_]
            EXPL.append((cle, s_, g_, len(sel), sum(1 for l in sel if l["cA"] > 0), sum(l["pnA"] for l in sel)))
    # diagnostic sur tous les signaux : les offres à fort risque de retrait gagnent-elles plus souvent ? (sélection adverse)
    DIAG = {}
    for per_ in ("val", "test"):
        L = [l for l in lignes if l["per"] == per_ and not math.isnan(l["pr"])]
        y = np.array([l["gagne"] for l in L]);
        if len(set(y)) > 1:
            DIAG[per_] = dict(n=len(L), auc_r=roc_auc_score(y, [l["pr"] for l in L]), auc_c=roc_auc_score(y, [l["pc"] for l in L]),
                              auc_prix=roc_auc_score(y, [-l["a0"] for l in L]))
    # contrôles
    ctrl_prix = sum(1 for l in lignes if abs(l["vu"] - l["a0"]) < 0.0015); ctrl_bot = [(l["pnC"], l["pnC_bot"]) for l in LC if l["envoie"] and l["pnC_bot"] is not None]
    print("phase 5", f"{time.time() - T0:.0f} s", flush=True)

    # ================================================= RAPPORT (les chiffres ; la synthèse en tête est écrite à partir d'eux)
    n_per = collections.Counter(per)
    lim = lambda p_: (JOUR(starts[per == p_].min()), JOUR(starts[per == p_].max() + 300))
    w("<!-- DETAIL -->")
    w("## Données et découpage")
    w("")
    w(f"- {nc} cycles BTC 5 min (résumés produits par `queue_race_phases.py`). Découpage **chronologique** par cycle : apprentissage {n_per['app']} cycles ({lim('app')[0]} → {lim('app')[1]}), "
      f"validation {n_per['val']} ({lim('val')[0]} → {lim('val')[1]}), **test {n_per['test']}** ({lim('test')[0]} → {lim('test')[1]}), heure suisse. Aucun paramètre n'est choisi sur le test.")
    yr, yc, garde, trop = labels(J, H)
    w(f"- Instants éligibles : grille de {PAS} ms sur chaque cycle, les deux offres (Up et Down), prix entre 0,03 et 0,97 : **{fr(len(J['T']), 0)} instants**. "
      f"Exclus des modèles : niveau disparu avant notre délai ({fr(DELTA, 1)} ms) {fr(int(trop.sum()), 0)} ({pc(int(trop.sum()), len(trop))}) ; disparition « indéterminée » dans l'horizon {fr(int((~garde & ~trop).sum()), 0)}.")
    w(f"- **Délai** : Polymarket → Dublin {fr(POLY_DUBLIN, 1)} ms + calcul {fr(CALCUL, 1)} ms + aller simple {fr(ALLER, 0)} ms = **{fr(DELTA, 1)} ms**. Variables calculées avec ce qui est reçu à Dublin à l'instant T ; "
      f"l'événement à prédire doit arriver entre T + {fr(DELTA, 1)} ms et T + {fr(DELTA, 1)} + {H} ms (sensibilité {H2} ms).")
    w("")
    w("## Phase 3 — deux modèles séparés : retrait vendeur et consommation acheteuse")
    w("")
    w("Régression logistique, 10 variables fixées avant tout calcul (les mêmes pour les deux modèles) : " + " ; ".join(f"({i + 1}) {v}" for i, v in enumerate(VARS)) + ". "
      "« Sens favorable » = sens qui rend l'offre trop bon marché (BTC monte pour l'offre Up, baisse pour l'offre Down). Flux agressifs absents avant le 12.10 (mis à 0).")
    w("")
    w(f"| Modèle (horizon) | Période | Instants | Événements | Taux | AUC [IC 90 % par cycle] | Brier | Brier sans modèle (taux d'apprentissage) |")
    w("|---|---|---|---|---|---|---|---|")
    for nom in ("retrait", "consommation"):
        for h in (H, H2):
            r = M[(nom, h)]
            for per_ in ("val", "test"):
                x = r[per_]
                ic = f"{fr(x['auc'], 3)} [{fr(x['lo'], 3)} ; {fr(x['hi'], 3)}]" if x["lo"] is not None else fr(x["auc"], 3)
                w(f"| {nom} ({h} ms) | {per_ if per_ == 'test' else 'validation'} | {fr(x['n'], 0)} | {fr(x['pos'], 0)} | {pc(x['pos'], x['n'])} | {ic} | {fr(x['brier'], 4)} | {fr(x['brier0'], 4)} |")
    w("")
    for nom in ("retrait", "consommation"):
        r = M[(nom, H)]
        w(f"**Calibration — {nom} ({H} ms)** (déciles de probabilité prédite : prédit moyen → observé)")
        w("")
        w("| Décile | " + " | ".join(str(i + 1) for i in range(10)) + " |")
        w("|---|" + "---|" * 10)
        for per_ in ("val", "test"):
            w(f"| {'validation' if per_ == 'val' else 'test'} | " + " | ".join(f"{pc(a, 1)} → {pc(b, 1)}" for a, b, n in r[per_]["cal"]) + " |")
        w("")
    w("**AUC de chaque variable seule (test, horizon 500 ms)** et coefficient standardisé du modèle")
    w("")
    w("| Variable | AUC retrait | coef. retrait | AUC consommation | coef. consommation |")
    w("|---|---|---|---|---|")
    for j, v in enumerate(VARS):
        w(f"| {v} | {fr(M[('retrait', H)]['test']['uni'][j], 3)} | {fr(float(M[('retrait', H)]['m'].coef_[0][j]), 2)} | {fr(M[('consommation', H)]['test']['uni'][j], 3)} | {fr(float(M[('consommation', H)]['m'].coef_[0][j]), 2)} |")
    w("")
    w(f"**H545 — retraits et consommations ont-ils des précurseurs différents ?** (test) : le modèle retrait classe les consommations avec AUC {fr(h545['ret_sur_cons'], 3)} "
      f"(modèle consommation : {fr(M[('consommation', H)]['test']['auc'], 3)}) ; le modèle consommation classe les retraits avec AUC {fr(h545['cons_sur_ret'], 3)} (modèle retrait : {fr(M[('retrait', H)]['test']['auc'], 3)}). "
      f"Un modèle unique « disparition » : AUC {fr(h545['unique_sur_ret'], 3)} sur les retraits, {fr(h545['unique_sur_cons'], 3)} sur les consommations.")
    w("")
    w("## Phase 4 — course avec nos délais réels")
    w("")
    w(f"Alerte = probabilité ≥ 95e centile de la validation (seuil fixé sur la validation, mesuré sur le test). Ordre parti à T + {fr(CALCUL, 1)} ms, arrivé chez Polymarket à T + {fr(CALCUL + ALLER, 1)} ms (aller simple) "
      f"ou T + {fr(CALCUL + RTT, 1)} ms (aller-retour complet), comparé à l'heure Polymarket de la disparition. « Encore achetable » = le niveau est encore au meilleur prix avec ≥ 1 part dans le carnet reçu à T + 28 ms. "
      "Valeur à 5 s = milieu du carnet 5 s plus tard − prix payé − frais (‰ par part, 1 ‰ = 0,1 c).")
    w("")
    w("| Modèle | Instants | Seuil | Disparition (cette cause) ≤ " + str(int(DELTA + H)) + " ms | Arrivé avant la disparition : aller simple · aller-retour | Arrivé avant la 1re baisse | Encore achetable à +28 ms | Valeur à 5 s (‰/part) moy. [IC 90 % par cycle] · méd. |")
    w("|---|---|---|---|---|---|---|---|")
    for nom in ("retrait", "consommation"):
        for lab, k in (("alerte (test)", "alerte"), ("instants au hasard (test)", "hasard")):
            x = P4[nom][k]
            w(f"| {nom} — {lab} | {fr(x['n'], 0)} | {fr(P4[nom]['seuil'], 3) if k == 'alerte' else '—'} | {fr(x['n_ev'], 0)} ({pc(x['n_ev'], x['n'])}) | {pc(x['dem'], x['n_ev'])} · {pc(x['rtt'], x['n_ev'])} | "
              f"{pc(x['av1o'], x['av1'])} | {pc(x['enc'], x['n'])} | {fr(x['v5'], 1)} [{fr(x['v5_ic'][0], 1)} ; {fr(x['v5_ic'][1], 1)}] · {fr(x['v5_med'], 1)} |")
    w("")
    RES["P4"] = P4; RES["M"] = M
    w("## Phase 5 — fantômes R, S, RS contre le moteur C (mêmes signaux, simulation hors ligne)")
    w("")
    nLC = collections.Counter(l["per"] for l in LC)
    w(f"Signaux : cohortes A et B de `rapide.json` (les seules où le moteur C est calculé), réglés, dont le cycle est enregistré : {len(LC)} (apprentissage {nLC['app']}, validation {nLC['val']}, test {nLC['test']}). "
      f"Moteur C = décision enregistrée en direct (« envoie », plafond) ; exécution simulée sur le carnet reconstruit reçu à T + {fr(RTT, 0)} ms (aller-retour), {fr(BUDGET, 0)} $ par signal, frais 0,07·p·(1−p) par part, règlement par `gagnant`. "
      f"**R** = C + achat immédiat (limite = prix du signal) des signaux REFUSÉS par C quand P(retrait) ≥ seuil ; **S** = idem avec P(consommation) ; **RS** = l'un ou l'autre. Seuils choisis sur apprentissage + validation seulement "
      f"(centiles {', '.join(str(int(100 * g)) for g in GRILLE)} % des probabilités des signaux refusés, ou « jamais ») : R {('jamais' if sR is None else fr(sR, 3))} (gain apprentissage+validation {sgn(gR)}), "
      f"S {('jamais' if sS is None else fr(sS, 3))} ({sgn(gS)}). Jackpot = gain ≥ 4 × la mise. IC par bootstrap des cycles ({NB_BOOT} tirages) ; Bonferroni sur 3 variantes = IC à 96,7 %.")
    w("")
    w("| Période | Stratégie | P&L | Δ contre C [IC 90 %] | IC Bonferroni 96,7 % | Achats | Jackpots | Signaux ajoutés (exécutés) | Gains · pertes des ajouts | Jackpots ajoutés | Perte max. (drawdown) | Capital engagé (max par cycle) |")
    w("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for per_ in ("app", "val", "test"):
        c = P5[(per_, "C")]
        w(f"| {per_ if per_ == 'test' else ('apprentissage' if per_ == 'app' else 'validation')} | moteur C | {sgn(c['pn'])} | — | — | {c['n']} | {c['jp']} | — | — | — | {fr(c['dd'], 0)} $ | {fr(c['c'], 0)} $ |")
        for var in ("R", "S", "RS"):
            x = P5[(per_, var)]
            w(f"| | {var} | {sgn(x['pn'])} | {sgn(x['delta'])} [{sgn(x['ic'][0])} ; {sgn(x['ic'][1])}] | [{sgn(x['icb'][0])} ; {sgn(x['icb'][1])}] | {x['n']} | {x['jp']} | {x['nadd']} ({x['nadd_fill']}) | {sgn(x['gain_add'])} · {sgn(x['perte_add'])} | {x['jp_add']} | {fr(x['dd'], 0)} $ | {fr(x['c'], 0)} $ ({fr(x['cmax'], 0)} $) |")
    w("")
    w("**Exploratoire (pas un verdict)** — sur le test, ajouts des signaux refusés par C pour chaque seuil de la grille :")
    w("")
    w("| Probabilité | Seuil | Gain app.+val. | Signaux ajoutés test | exécutés | P&L test des ajouts |")
    w("|---|---|---|---|---|---|")
    for cle, s_, g_, n_, nf_, pn_ in EXPL:
        w(f"| {'retrait' if cle == 'pr' else 'consommation'} | {fr(s_, 3)} | {sgn(g_)} | {n_} | {nf_} | {sgn(pn_)} |")
    w("")
    if DIAG:
        w("**Diagnostic sur tous les signaux du bot (toutes règles)** — la probabilité de retrait / consommation de l'offre visée annonce-t-elle un signal gagnant ? "
          + " ; ".join(f"{'validation' if k == 'val' else 'test'} ({v['n']} signaux) : AUC retrait {fr(v['auc_r'], 3)}, consommation {fr(v['auc_c'], 3)}, prix seul (bas = gagne) {fr(v['auc_prix'], 3)}" for k, v in DIAG.items()) + ".")
        w("")
    ec = [abs(a - b) for a, b in ctrl_bot]
    w(f"Contrôles : prix du meilleur vendeur reconstruit = prix du signal pour {ctrl_prix}/{len(lignes)} signaux ; P&L simulé du moteur C contre le P&L enregistré en direct par le bot (même signal) : écart médian {fr(float(np.median(ec)) if ec else None, 2)} $, "
      f"total simulé {sgn(sum(a for a, b in ctrl_bot))} contre {sgn(sum(b for a, b in ctrl_bot))} enregistré ({len(ctrl_bot)} envois ; le bot utilise des frais 0,072·p·(1−p) et son aller-retour mesuré ~30–36 ms).")
    w("")
    w(f"Durée d'exécution : {time.time() - T0:.0f} s.")
    json.dump(dict(sR=sR, sS=sS, P5={f"{a}|{b}": v for (a, b), v in P5.items()}, P4=P4, h545=h545, DIAG=DIAG,
                   P3={f"{a}|{b}": {k: v[k] for k in ("val", "test", "base")} for (a, b), v in M.items() if a != "trop"}),
              open(os.environ.get("QR_JSON", "/dev/null"), "w"), default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o), ensure_ascii=False, indent=1)
    entete = os.environ.get("QR_ENTETE")
    txt = (open(entete).read() if entete and os.path.exists(entete) else "# BOT95 — QUEUE RACE ENGINE · phases 3 à 6\n\n(synthèse à écrire)\n") + "\n" + "\n".join(md) + "\n"
    open(SORTIE, "w").write(txt)
    print("écrit", SORTIE, f"{time.time() - T0:.1f} s")


if __name__ == "__main__":
    main()
