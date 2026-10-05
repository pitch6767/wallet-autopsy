"""Moteur de danger + assurances pour V1 (reglage A) — BTC et ETH, 12 jours, retard 1 s, 100 parts.
1. Capteurs seconde par seconde pendant chaque position : fragilite (chute de la proba si le prix bouge de 1/3/5 pb), convexite,
   flux agressif du perp (OFI) et ses derivees, volume, gros ordres, ecart perp-spot, pression Polymarket, evolution de la proba.
2. Modele « stop dans les 1 / 3 / 5 prochaines secondes » appris sur les jours 1-8, juge sur les jours 9-12 (AUC).
3. Politiques de protection (assurance temporaire, graduee, paire anticipee, monetisation, sans stop) et combinaisons.
Comptabilite : tresorerie + paiement final (une paire Up+Down vaut 1 $). Prix Polymarket = dernier echange -/+ 1 cent, frais taker.
"""
import sys, math, time, statistics, collections
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
sys.path.insert(0, "etude/bot5min")
import test as T
import paires as P
import solutions as S
from sorties import spot_jour, perp_jour, charger, dernier

JOURS = int(sys.argv[1]) if len(sys.argv) > 1 else 12
REGLE = len(sys.argv) > 2 and sys.argv[2] == "regle"
L = 1
N = 100.0
FEE = lambda p: T.FEE_RATE * p * (1 - p)
OUT = "etude/bot5min/"


def q(vals, x):
    v = sorted(vals)
    return v[min(len(v) - 1, max(0, int(len(v) * x)))] if v else None


def auc(y, s):
    y = np.asarray(y); s = np.asarray(s)
    if y.sum() == 0 or y.sum() == len(y): return float("nan")
    o = np.argsort(s, kind="mergesort"); r = np.empty(len(s)); r[o] = np.arange(1, len(s) + 1)
    # rangs moyens pour les egalites
    _, inv, cnt = np.unique(s, return_inverse=True, return_counts=True)
    somme = np.bincount(inv, weights=r); r = (somme / cnt)[inv]
    n1 = y.sum(); n0 = len(y) - n1
    return float((r[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


def etudier(prefixe, sym, jours, debut, fin, coupe):
    t0 = time.time()
    SP = charger(spot_jour, sym, jours)
    SPx = {s: (v[0], v[0]) for s, v in SP.items()}
    PE = charger(perp_jour, sym, jours)
    # tableaux par seconde (sommes cumulees pour des fenetres en temps constant)
    b0 = min(SP); n = max(SP) - b0 + 2
    PB = np.zeros(n); PV = np.zeros(n); MB = np.zeros(n); MV = np.zeros(n); PP = np.full(n, np.nan); SPT = np.full(n, np.nan)
    for s, r in PE.items():
        i = s - b0
        if 0 <= i < n: PP[i], PB[i], PV[i], MB[i], MV[i] = r[0], r[1], r[2], r[4], r[5]
    for s, r in SP.items(): SPT[s - b0] = r[0]
    for A_ in (PP, SPT):
        for i in range(1, n):
            if np.isnan(A_[i]): A_[i] = A_[i - 1]
    CB = np.concatenate([[0], np.cumsum(PB)]); CV = np.concatenate([[0], np.cumsum(PV)])
    def som(C, a, b):                 # somme sur les secondes [a, b]
        i, j = a - b0, b - b0 + 1
        if i < 0 or j > n: return 0.0
        return C[j] - C[i]
    def mx(Arr, a, b):
        i, j = max(0, a - b0), min(n, b - b0 + 1)
        return float(Arr[i:j].max()) if j > i else 0.0
    del PE
    print(prefixe, "binance charge (%.0fs)" % (time.time() - t0)); sys.stdout.flush()
    with ThreadPoolExecutor(12) as ex:
        M = sorted([m for m in ex.map(lambda st: S.marche(prefixe, st), range(debut, fin, 300)) if m], key=lambda m: m["start"])
    def tr(m):
        try: m["tr"], _ = P.echanges(m)
        except Exception: m["tr"] = []
        return m
    with ThreadPoolExecutor(10) as ex:
        M = [m for m in ex.map(tr, M) if m["tr"] and m.get("strike") is not None]
    print(prefixe, "marches", len(M), "(%.0fs)" % (time.time() - t0)); sys.stdout.flush()
    prix = lambda t: dernier(SP, t, 0)
    hist, derives = [], []
    for m in M:
        kp = float(m["strike"]); fo = float(m["final"]) if m.get("final") is not None else None
        tb = S.twap(SPx, m["start"] - 59, m["start"]); tf = S.twap(SPx, m["end"] - 59, m["end"])
        m["base"] = statistics.median(hist[-12:]) if len(hist) >= 3 else 0
        if tb: hist.append(tb - kp)
        m["K"] = kp + m["base"]
        m["sd_b"] = statistics.pstdev(derives[-50:]) if len(derives) >= 10 else None
        if tf and tb and fo: derives.append((tf - tb) - (fo - kp))
        # ruban Polymarket par seconde : dernier prix Up, pressions acheteuses vers Up / vers Down (parts)
        up = np.full(301, np.nan); pu_ = np.zeros(301); pd_ = np.zeros(301)
        for (ts, u, p, size, side) in m["tr"]:
            k = ts - m["start"]
            if 0 <= k <= 300:
                up[k] = p if u else 1 - p
                if (side == "BUY") == u: pu_[k] += size
                else: pd_[k] += size
        for k in range(1, 301):
            if np.isnan(up[k]): up[k] = up[k - 1]
        m["pm_up"] = up; m["cpu"] = np.concatenate([[0], np.cumsum(pu_)]); m["cpd"] = np.concatenate([[0], np.cumsum(pd_)])

    def proba_up(m, ts, cache, choc=0.0):
        key = (ts, choc)
        if key in cache: return cache[key]
        r = None; P0 = prix(ts); sgk = ("sg", ts // 15)
        if sgk not in cache: cache[sgk] = T.sigma_s(SPx, ts)
        sg = cache[sgk]
        if P0 and sg and m["sd_b"]:
            P0 = P0 * (1 + choc)
            a = m["end"] - 59
            if ts >= a:
                ck = ("cn", ts)
                if ck not in cache:
                    c_ = [x for x in (prix(s) for s in range(a, ts + 1)) if x]; cache[ck] = (sum(c_), len(c_))
                sc, nc = cache[ck]
                nr = m["end"] - ts
                E = (sc + nr * P0) / (nc + nr); var = (sg * P0) ** 2 * nr ** 3 / 3 / 3600
            else:
                E = P0; var = (sg * P0) ** 2 * ((a - ts) + 20)
            r = T.phi((E - m["K"]) / math.sqrt(var + m["sd_b"] ** 2))
        cache[key] = r
        return r

    def fair(m, s, d, choc=0.0):
        pu = proba_up(m, s, m.setdefault("cache", {}), choc)
        return None if pu is None else (pu if d > 0 else 1 - pu)

    def ofi(s, k, d):
        b_, v_ = som(CB, s - k + 1, s), som(CV, s - k + 1, s)
        return d * (b_ - v_) / (b_ + v_) if b_ + v_ > 0 else 0.0

    NOMS = ["temps_restant", "depuis_entree", "proba", "baisse_proba", "pente_proba_3s", "frag1", "frag3", "frag5", "convexite",
            "ofi1", "ofi3", "ofi10", "d_ofi3", "d2_ofi3", "ofi10_moins_ofi3", "volume_rel", "gros_contre", "gros_pour",
            "ecart_perp_spot", "ret_spot_3s", "ret_perp_1s", "notre_prix", "var_notre_prix_3s", "pression_opposee_3s", "pression_opposee_10s", "pression_nette_10s"]

    def feat(m, s, d, fair0, te):
        k = ("f", s, d, round(fair0, 4), te)
        c = m.setdefault("fc", {})
        if k in c: return c[k]
        f0 = fair(m, s, d)
        if f0 is None: c[k] = None; return None
        f3 = fair(m, s - 3, d) or f0
        fr = [f0 - (fair(m, s, d, -d * x * 1e-4) or f0) for x in (1, 3, 5)]
        cv = (fair(m, s, d, d * 1e-4) or f0) + (fair(m, s, d, -d * 1e-4) or f0) - 2 * f0
        o3 = ofi(s, 3, d); o3a = ofi(s - 1, 3, d); o3b = ofi(s - 2, 3, d)
        vol3 = som(CB, s - 2, s) + som(CV, s - 2, s); vol300 = (som(CB, s - 299, s) + som(CV, s - 299, s)) / 100
        i = s - b0
        bas = (PP[i] / SPT[i] - 1) * 1e4 if 0 <= i < n and SPT[i] > 0 and PP[i] > 0 else 0.0
        bas_ref = np.nanmedian([(PP[j] / SPT[j] - 1) * 1e4 for j in range(max(0, i - 300), max(1, i - 10), 15)]) if i > 300 else 0.0
        rs = d * (SPT[i] / SPT[i - 3] - 1) * 1e4 if i >= 3 and SPT[i - 3] > 0 else 0.0
        rp = d * (PP[i] / PP[i - 1] - 1) * 1e4 if i >= 1 and PP[i - 1] > 0 else 0.0
        kk = s - m["start"]
        kk = min(max(kk, 0), 300)
        notre = m["pm_up"][kk] if d > 0 else 1 - m["pm_up"][kk]
        av = m["pm_up"][max(0, kk - 3)]; av = av if d > 0 else 1 - av
        cpo, cpn = (m["cpd"], m["cpu"]) if d > 0 else (m["cpu"], m["cpd"])
        po3 = cpo[kk + 1] - cpo[max(0, kk - 2)]; po10 = cpo[kk + 1] - cpo[max(0, kk - 9)]; pn10 = cpn[kk + 1] - cpn[max(0, kk - 9)]
        x = [m["end"] - s, s - te, f0, fair0 - f0, f0 - f3, fr[0], fr[1], fr[2], cv,
             ofi(s, 1, d), o3, ofi(s, 10, d), o3 - o3a, (o3 - o3a) - (o3a - o3b), ofi(s, 10, d) - o3, vol3 / 3 / (vol300 / 3 + 1e-9) if vol300 > 0 else 1.0,
             mx(MV if d > 0 else MB, s - 1, s), mx(MB if d > 0 else MV, s - 1, s), d * (bas - (bas_ref if bas_ref == bas_ref else 0)), rs, rp,
             notre if notre == notre else 0.5, (notre - av) if (notre == notre and av == av) else 0.0, po3, po10, pn10 - po10]
        c[k] = x
        return x

    # --------------------------------------------------------------- simulation d'un cycle
    def sim(m, v, score=None):
        cache = m.setdefault("cache", {}); A = None; dern = {True: 0.5, False: 0.5}
        for (ts, up, p, size, side) in m["tr"]:
            if ts > m["end"] - 1: break
            if ts < m["start"]: continue
            dern[up] = p; dern[not up] = 1 - p
            pu = proba_up(m, ts - L, cache)
            if pu is None: continue
            if A is None:
                if side == "BUY" and 0.55 <= p <= 0.56:
                    fr_ = pu if up else 1 - pu
                    if fr_ >= 0.63:
                        a0, b0_ = prix(ts - L - 5), prix(ts - L)
                        if not (a0 and b0_ and ((b0_ - a0) * (1 if up else -1)) > 0): continue
                        d = 1 if up else -1
                        if "refuser" in v and v["refuser"](m, ts - L, d, fr_): continue
                        w = v["mise"](m, ts - L, d, fr_, p) if "mise" in v else 1.0
                        A = {"c": up, "d": d, "prix": p, "q": N * w, "fair0": fr_, "te": ts - L, "ts": ts,
                             "cash": -N * w * (p + FEE(p)), "O": 0.0, "B": 0.0, "H": 0.0, "Hcout": 0.0, "main": N * w, "calme": 0, "fini": False, "etat": "fin"}
                        A["sorties"] = []
                continue
            c = A["c"]; fairA = pu if c else 1 - pu
            if A["fini"]: break
            # offre maker opposee de V1
            if side == "SELL": O_, qq = up, p
            elif side == "BUY": O_, qq = (not up), 1 - p
            else: O_ = None
            if O_ is not None and O_ != c and A["O"] < A["main"]:
                offre = min(math.floor(((1 - fairA) - 0.08) * 100) / 100, 0.43)
                if offre >= 0.02 and qq <= offre - 0.01 + 1e-9:
                    k = min(size, A["main"] - A["O"]); A["O"] += k; A["B"] += k; A["cash"] -= k * offre
            if A["O"] >= A["main"] - 1e-9:
                A["etat"] = "paire"; A["fini"] = True; break
            s = ts - L
            opp_ask = min(0.99, 1 - dern[c] + 0.01); opp_bid = max(0.01, 1 - dern[c] - 0.01)
            # --- protection
            if "couv" in v and s > A["te"]:
                sc = score(m, s, A)
                pol = v["couv"]
                if sc is not None:
                    cible = 0.0
                    for (th, frac) in pol["niveaux"]:
                        if sc >= th: cible = max(cible, frac)
                    voulu = cible * A["main"] - A["O"]
                    if pol.get("cap") is not None and opp_ask > pol["cap"]: voulu = 0
                    if voulu > 1e-6:
                        A["cash"] -= voulu * (opp_ask + FEE(opp_ask)); A["O"] += voulu; A["H"] += voulu; A["Hcout"] += voulu * opp_ask
                        A["etat"] = "couvert"
                        if A["O"] >= A["main"] - 1e-9: A["etat"] = "paire anticipee"; A["fini"] = True; break
                    # retrait de l'assurance si l'alerte retombe
                    if A["H"] > 0 and pol.get("retrait") is not None:
                        A["calme"] = A["calme"] + 1 if sc < pol["retrait"] else 0
                        if A["calme"] >= pol.get("calme_s", 2):
                            A["cash"] += A["H"] * (opp_bid - FEE(opp_bid)); A["O"] -= A["H"]; A["H"] = 0; A["Hcout"] = 0; A["calme"] = 0
                    # monetiser : l'assurance a pris de la valeur -> on la revend, la position continue
                    if A["H"] > 0 and pol.get("monet") is not None and opp_bid >= A["Hcout"] / A["H"] + pol["monet"]:
                        A["cash"] += A["H"] * (opp_bid - FEE(opp_bid)); A["O"] -= A["H"]; A["H"] = 0; A["Hcout"] = 0
            # --- stop de V1 (sauf variante sans stop) : on vend la part non appariee
            if v.get("stop", True) and fairA < A["fair0"] - 0.15:
                pv = max(0.01, dern[c] - 0.01); k = max(0.0, A["main"] - A["O"])
                A["cash"] += k * (pv - FEE(pv)); A["main"] -= k
                A["etat"] = "stop"; A["fini"] = True; break
            # --- sortie 0,90 (si aucune offre maker servie, comme V1) : on revend aussi l'assurance
            if up == c and p >= 0.90 and A["B"] < 1e-9:
                A["cash"] += A["main"] * (0.90 - FEE(0.90)); A["main"] = 0
                if A["O"] > 0: A["cash"] += A["O"] * (opp_bid - FEE(opp_bid)); A["O"] = 0
                A["etat"] = "sortie"; A["fini"] = True; A["tsortie"] = ts; break
        if A is None: return None
        gc = (A["c"] == m["up_gagne"])
        pnl = A["cash"] + A["main"] * (1 if gc else 0) + A["O"] * (0 if gc else 1)
        return {"pnl": pnl, "etat": A["etat"], "ts": A["ts"], "te": A["te"], "d": A["d"], "fair0": A["fair0"], "q": A["q"], "gc": gc,
                "tstop": ts if A["etat"] == "stop" else None, "tfin": ts}

    # --------------------------------------------------------------- 1. reference et jeu de donnees
    REF = {}
    for m in M:
        r = sim(m, {})
        if r: REF[m["start"]] = r
    print(prefixe, "reference", len(REF), "(%.0fs)" % (time.time() - t0)); sys.stdout.flush()
    Mi = {m["start"]: m for m in M}
    X, Y1, Y3, Y5, Tm = [], [], [], [], []
    for st, r in REF.items():
        m = Mi[st]
        fin_s = (r["tfin"] - L) if r["tfin"] else m["end"] - 1
        for s in range(r["te"] + 1, min(fin_s, m["end"] - 2)):
            x = feat(m, s, r["d"], r["fair0"], r["te"])
            if x is None: continue
            dt = (r["tstop"] - s) if r["tstop"] else 999
            X.append(x); Y1.append(1 < dt <= 2); Y3.append(1 < dt <= 4); Y5.append(1 < dt <= 6); Tm.append(st)
    X = np.array(X, dtype=float); Y1, Y3, Y5, Tm = np.array(Y1), np.array(Y3), np.array(Y5), np.array(Tm)
    X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)
    ia, ib = Tm < coupe, Tm >= coupe
    print(prefixe, "lignes", len(X), "stops 3 s", int(Y3.sum()), "(%.0fs)" % (time.time() - t0)); sys.stdout.flush()
    from sklearn.ensemble import HistGradientBoostingClassifier
    modeles, rap_auc = {}, []
    for nom_y, Y in (("1 s", Y1), ("3 s", Y3), ("5 s", Y5)):
        clf = HistGradientBoostingClassifier(max_iter=300, learning_rate=0.05, max_leaf_nodes=31, min_samples_leaf=100, l2_regularization=1.0, random_state=1)
        clf.fit(X[ia], Y[ia]); pb = clf.predict_proba(X[ib])[:, 1]
        modeles[nom_y] = clf
        rap_auc.append(f"| stop dans les {nom_y} | {int(Y[ia].sum())} / {int(ia.sum())} | {int(Y[ib].sum())} / {int(ib.sum())} | **{auc(Y[ib], pb):.3f}** |")
    # capteurs seuls (sens choisi sur 1-8)
    seuls = []
    for j, nm in enumerate(NOMS):
        a1 = auc(Y3[ia], X[ia, j]); sg = 1 if a1 >= 0.5 else -1
        seuls.append((auc(Y3[ib], sg * X[ib, j]), nm, "haut" if sg > 0 else "bas"))
    clf3 = modeles["3 s"]
    sc_a = clf3.predict_proba(X[ia])[:, 1]
    th = {k: q(list(sc_a), 1 - k) for k in (0.20, 0.10, 0.05, 0.02, 0.01)}
    cs = {}
    def score(m, s, A):
        k = (m["start"], s, A["d"], A["te"])
        if k in cs: return cs[k]
        x = feat(m, s, A["d"], A["fair0"], A["te"])
        r = None if x is None else float(clf3.predict_proba(np.nan_to_num(np.array([x], dtype=float)))[0, 1])
        cs[k] = r
        return r
    # declencheurs simples (sans modele) : seuils des jours 1-8
    J = {nm: j for j, nm in enumerate(NOMS)}
    qa = lambda nm, x: q(list(X[ia, J[nm]]), x)
    frag95, frag90, dofi05, gros90, press90 = qa("frag3", .95), qa("frag3", .90), qa("d_ofi3", .05), qa("gros_contre", .90), qa("pression_opposee_3s", .90)
    def simple(fn):
        def f(m, s, A):
            x = feat(m, s, A["d"], A["fair0"], A["te"])
            return None if x is None else (1.0 if fn(x) else 0.0)
        return f
    sc_frag = simple(lambda x: x[J["frag3"]] >= frag95)
    sc_ofi = simple(lambda x: x[J["d_ofi3"]] <= dofi05)
    sc_baisse = simple(lambda x: x[J["baisse_proba"]] >= 0.07)
    sc_aval = simple(lambda x: (x[J["frag3"]] >= frag90) + (x[J["d_ofi3"]] <= dofi05) + (x[J["gros_contre"]] >= gros90) + (x[J["pression_opposee_3s"]] >= press90) >= 2)
    # fragilite a l'entree (jours 1-8)
    fe_ent = []
    for st, r in REF.items():
        if st < coupe:
            x = feat(Mi[st], r["te"], r["d"], r["fair0"], r["te"])
            if x: fe_ent.append(x[J["frag3"]])
    fe80, fe90, fe_moy = q(fe_ent, .8), q(fe_ent, .9), statistics.mean(fe_ent)
    av_med = statistics.median([r["fair0"] - 0.555 for st, r in REF.items() if st < coupe])
    def frag_ent(m, s, d, f):
        x = feat(m, s, d, f, s)
        return x[J["frag3"]] if x else None
    ref_frag = lambda lim: (lambda m, s, d, f: (frag_ent(m, s, d, f) or 0) > lim)
    mise15 = lambda m, s, d, f, p: 0.5 if (f - p) < av_med else 1.5
    mise_frag = lambda m, s, d, f, p: min(2.0, max(0.25, fe_moy / max(1e-4, frag_ent(m, s, d, f) or fe_moy)))

    def niv(*paires): return [(th[k], fr) for k, fr in paires]
    G = {"niveaux": niv((0.10, 0.25), (0.05, 0.5), (0.02, 1.0)), "retrait": th[0.20], "calme_s": 2}
    variantes = [
        ("Reference V1", {}, None),
        ("Entree : refuser si fragilite 3 pb > 20 % haut", {"refuser": ref_frag(fe80)}, None),
        ("Entree : refuser si fragilite > 10 % haut", {"refuser": ref_frag(fe90)}, None),
        ("Entree : mise inverse a la fragilite", {"mise": mise_frag}, None),
        ("Mise 0,5x / 1,5x selon l'avance (retenue)", {"mise": mise15}, None),
        ("Assurance temporaire 30 % si danger top 5 %, retiree quand ca se calme", {"couv": {"niveaux": niv((0.05, 0.3)), "retrait": th[0.20], "calme_s": 2}}, score),
        ("Assurance temporaire 50 % si danger top 5 %", {"couv": {"niveaux": niv((0.05, 0.5)), "retrait": th[0.20], "calme_s": 2}}, score),
        ("Assurance temporaire 30 % si danger top 2 %", {"couv": {"niveaux": niv((0.02, 0.3)), "retrait": th[0.20], "calme_s": 2}}, score),
        ("Assurance 30 % top 10 %, retiree apres 3 s calmes", {"couv": {"niveaux": niv((0.10, 0.3)), "retrait": th[0.20], "calme_s": 3}}, score),
        ("Assurance graduee 25 / 50 / 100 % (danger top 10 / 5 / 2 %)", {"couv": G}, score),
        ("Assurance graduee, jamais retiree", {"couv": {"niveaux": G["niveaux"]}}, score),
        ("Paire anticipee 100 % si danger top 5 % et oppose <= 0,45", {"couv": {"niveaux": niv((0.05, 1.0)), "cap": 0.45}}, score),
        ("Paire anticipee 100 % si danger top 2 % et oppose <= 0,48", {"couv": {"niveaux": niv((0.02, 1.0)), "cap": 0.48}}, score),
        ("Assurance 30 % top 5 % + revendue si elle gagne 8 cents (monetiser)", {"couv": {"niveaux": niv((0.05, 0.3)), "retrait": th[0.20], "calme_s": 2, "monet": 0.08}}, score),
        ("Assurance 50 % top 5 % + monetiser 5 cents", {"couv": {"niveaux": niv((0.05, 0.5)), "retrait": th[0.20], "calme_s": 2, "monet": 0.05}}, score),
        ("SANS STOP + assurance graduee", {"stop": False, "couv": G}, score),
        ("SANS STOP + paire anticipee top 5 % (oppose <= 0,48)", {"stop": False, "couv": {"niveaux": niv((0.05, 1.0)), "cap": 0.48}}, score),
        ("SANS STOP + graduee + paire complete top 1 %", {"stop": False, "couv": {"niveaux": niv((0.10, 0.25), (0.05, 0.5), (0.01, 1.0)), "retrait": th[0.20], "calme_s": 2}}, score),
        ("Simple : assurance 30 % si fragilite top 5 %", {"couv": {"niveaux": [(0.5, 0.3)], "retrait": 0.5, "calme_s": 2}}, sc_frag),
        ("Simple : assurance 30 % si acceleration du flux contre nous (5 % bas)", {"couv": {"niveaux": [(0.5, 0.3)], "retrait": 0.5, "calme_s": 2}}, sc_ofi),
        ("Simple : assurance 30 % si la proba a deja perdu 7 pts", {"couv": {"niveaux": [(0.5, 0.3)], "retrait": 0.5, "calme_s": 2}}, sc_baisse),
        ("Simple : avalanche (2 signaux sur 4) -> assurance 50 %", {"couv": {"niveaux": [(0.5, 0.5)], "retrait": 0.5, "calme_s": 2}}, sc_aval),
        ("Combo : fragilite 10 % refusee + assurance graduee", {"refuser": ref_frag(fe90), "couv": G}, score),
        ("Combo : mise 1,5x + assurance graduee", {"mise": mise15, "couv": G}, score),
        ("Combo : mise 1,5x + assurance 30 % top 5 % + monetiser", {"mise": mise15, "couv": {"niveaux": niv((0.05, 0.3)), "retrait": th[0.20], "calme_s": 2, "monet": 0.08}}, score),
        ("Combo : mise 1,5x + fragilite refusee + graduee + monetiser", {"mise": mise15, "refuser": ref_frag(fe90), "couv": dict(G, monet=0.08)}, score),
        ("Combo : mise 1,5x + SANS STOP + graduee", {"mise": mise15, "stop": False, "couv": G}, score),
    ]
    if REGLE:
        def sc_drop(m, s, A):
            f_ = fair(m, s, A["d"])
            return None if f_ is None else A["fair0"] - f_
        def RG(a_, b_, c_, retrait=0.03):
            return {"niveaux": [(a_, 0.25), (b_, 0.5), (c_, 1.0)], "retrait": retrait, "calme_s": 2}
        variantes = [("Reference V1", {}, None)]
        for (a_, b_, c_) in ((0.05, 0.08, 0.11), (0.06, 0.09, 0.12), (0.07, 0.10, 0.13), (0.08, 0.11, 0.14), (0.04, 0.07, 0.10)):
            variantes.append((f"Regle simple sans stop : baisse {int(a_*100)}/{int(b_*100)}/{int(c_*100)} pts -> 25/50/100 %, retrait < 3 pts", {"stop": False, "couv": RG(a_, b_, c_)}, sc_drop))
        variantes.append(("Regle 6/9/12 sans retrait, sans stop", {"stop": False, "couv": {"niveaux": RG(0.06, 0.09, 0.12)["niveaux"]}}, sc_drop))
        variantes.append(("Regle 6/9/12 AVEC le stop -15 en plus", {"couv": RG(0.06, 0.09, 0.12)}, sc_drop))
        variantes.append(("Mise 1,5x + regle 6/9/12 sans stop", {"mise": mise15, "stop": False, "couv": RG(0.06, 0.09, 0.12)}, sc_drop))
        variantes.append(("Modele de danger (pour comparer) : graduee sans stop", {"stop": False, "couv": G}, score))
    jours_a = (coupe - debut) / 86400; jours_b = (fin - coupe) / 86400
    rap = [f"\n## {prefixe.upper()} — {len(M)} cycles, {len(REF)} trades V1\n",
           "### Peut-on voir venir le stop ? (modele appris jours 1-8, juge jours 9-12 ; AUC 0,5 = hasard, 1 = parfait)\n",
           "| Cible | Stops / lignes jours 1-8 | Stops / lignes jours 9-12 | AUC jours 9-12 |", "|---|---|---|---|"] + rap_auc
    rap += ["\n### Chaque capteur seul (stop dans les 3 s, AUC jours 9-12)\n", "| Capteur | Danger quand il est | AUC |", "|---|---|---|"]
    for a_, nm, sens in sorted(seuls, reverse=True):
        rap.append(f"| {nm} | {sens} | {a_:.3f} |")
    imp = sorted(zip(np.abs(np.array([a - 0.5 for a, _, _ in seuls])), [nm for _, nm, _ in seuls]), reverse=True)
    rap += ["\n### Strategies (gains pour 100 parts ≈ 55 $ ; entre parentheses : ecart avec la reference)\n",
            "| Strategie | Trades | Gain net | Gain/jour | Pertes totales | Trades perdants | Pire baisse | Gain/jour jours 1-8 | **Gain/jour jours 9-12 (jamais vus)** | Issues |",
            "|---|---|---|---|---|---|---|---|---|---|"]
    ref = None
    for nom, v, scf in variantes:
        R = list(REF.values()) if not v else [x for x in (sim(m, v, scf) for m in M) if x]
        cum = pic = dd = 0
        for x in sorted(R, key=lambda x: x["ts"]):
            cum += x["pnl"]; pic = max(pic, cum); dd = max(dd, pic - cum)
        net = sum(x["pnl"] for x in R); per = sum(x["pnl"] for x in R if x["pnl"] < 0); npe = sum(1 for x in R if x["pnl"] < 0)
        ga = sum(x["pnl"] for x in R if x["ts"] < coupe) / jours_a; gb = sum(x["pnl"] for x in R if x["ts"] >= coupe) / jours_b
        if ref is None: ref = (net, per, ga, gb, npe)
        iss = collections.Counter(x["etat"] for x in R)
        rap.append(f"| {nom} | {len(R)} | {net:+.0f} $ ({net - ref[0]:+.0f}) | {net / JOURS:+.0f} $ | {per:+.0f} $ ({per - ref[1]:+.0f}) | {npe} ({npe - ref[4]:+d}) | -{dd:.0f} $ | {ga:+.0f} $ ({ga - ref[2]:+.0f}) | **{gb:+.0f} $ ({gb - ref[3]:+.0f})** | "
                   + ", ".join(f"{k} {c_}" for k, c_ in iss.most_common()) + " |")
        print(rap[-1]); sys.stdout.flush()
    return rap


def main():
    t0 = time.time()
    fin = int(time.time()) // 300 * 300 - 900
    debut = fin - JOURS * 86400
    jours = sorted({datetime.fromtimestamp(t, timezone.utc).strftime("%Y-%m-%d") for t in range(debut - 3700, fin + 600, 3600)})
    jours = [j for j in jours if j < datetime.now(timezone.utc).strftime("%Y-%m-%d")]
    fin = min(fin, int(datetime.strptime(jours[-1], "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp()) + 86400 - 300)
    coupe = debut + int(JOURS * 2 / 3) * 86400
    rap = [f"# Moteur de danger + assurances pour V1 — {JOURS} jours ({jours[0]} -> {jours[-1]})",
           "Tout est choisi sur les jours 1-8 ; les jours 9-12 servent de juge. Prix Polymarket = dernier echange +/- 1 cent, frais taker, retard 1 s."]
    for prefixe, sym in (("btc", "BTCUSDT"), ("eth", "ETHUSDT")):
        rap += etudier(prefixe, sym, jours, debut, fin, coupe)
        open(OUT + ("resultat_danger_regle.md" if REGLE else "resultat_danger.md"), "w").write("\n".join(rap))
    rap.append(f"\nDuree : {time.time() - t0:.0f} s")
    open(OUT + ("resultat_danger_regle.md" if REGLE else "resultat_danger.md"), "w").write("\n".join(rap))
    print("\n".join(rap))


if __name__ == "__main__":
    main()
