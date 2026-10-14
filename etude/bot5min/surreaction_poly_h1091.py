"""BOT95 — H1091 « surréaction de Polymarket » (Polymarket BTC 5 min Up/Down). Hors ligne, aucun ordre, aucun bot modifié.
IDÉE : quand le milieu du carnet Up bouge fort en quelques secondes SANS mouvement correspondant du BTC (c.-à-d. sans que la probabilité
  du modèle de règlement bouge autant), est-ce du flux d'ordres pur qui revient ensuite (acheter le côté poussé vers le bas), ou une
  information que les bourses ne montrent pas encore (suivre) ?
RÉSIDU : r(t, w) = [mid(t) − mid(t − w)] − [p(t) − p(t − w)], w = 3 / 5 / 10 s ; mid = (meilleur acheteur + meilleur vendeur Up) / 2 ;
  p = probabilité de Up du modèle de règlement de H1090 (k = 1,8 figé sur 11–12.10), calculée avec le prix BTC le plus frais :
  Coinbase reçu − écart médian (Coinbase − Chainlink) du cycle précédent (Chainlink arrive avec ~1,7 s de retard), à défaut Chainlink.
  Après : Δmid à +10 / +30 / +60 s, Δ(résidu) aux mêmes horizons, et gagnant final contre le prix au moment du signal.
MODÈLE (étendu à tout le cycle) : règlement = moyenne Chainlink des secondes 240–299 contre K = strikeTwap (moyenne des 60 s avant le début).
  t < 240 : moyenne attendue S, variance (σk)²·[(240 − t) + m(m+1)(2m+1)/(6·3600)] avec m = 60 (≈ 240 − t + 20,5) ;
  t ≥ 240 : n observations Chainlink déjà connues (moyenne A), m = 60 − n restantes : moyenne attendue (n·A + m·S)/60,
  variance (σk)²·m(m+1)(2m+1)/(6·3600). σ = écart-type des variations Chainlink 1 s du cycle précédent.
DONNÉES : enregistreur de Dublin, branche donnees-rapide (cycles/AAAA-MM-JJ/<début>.json.gz), photos du carnet chaque seconde (snap).
  Gagnant = bot95/officiels.json, sinon prix à battre du cycle suivant.
DÉCOUPAGE : exploration = cycles du 11.10 + 12.10 (UTC) ; validation = 13.10 + 14.10 (13.10 = jour réservé, lu une fois après le gel).
EXÉCUTION SIMULÉE : décision sur la photo t ; achat au meilleur vendeur de la photo SUIVANTE (≈ t + 1 s), limité à la taille affichée,
  10 $ maximum ; frais 0,07·p·(1−p) par part ; gardé jusqu'au règlement ; un achat par cycle et par règle (premier déclenchement).
CRITÈRE : borne basse de l'IC 90 % corrigé Bonferroni (nombre de règles figées ; bootstrap par cycles, 10 000 tirages, tous les cycles
  de la période comptés, 0 $ sans achat) du P&L de validation > 0. Aucun fantôme sans accord de Pitch.
Usage : python3 etude/bot5min/surreaction_poly_h1091.py --extraire <dossier cycles> <cache.json.gz>
        python3 etude/bot5min/surreaction_poly_h1091.py <cache.json.gz> [--validation]"""
import sys, os, json, gzip, glob, math, bisect, collections
import numpy as np

ICI = os.path.dirname(os.path.abspath(__file__)); RACINE = os.path.abspath(os.path.join(ICI, "..", ".."))
J11, J13, J15 = 1791676800, 1791849600, 1792022400          # 11.10, 13.10, 15.10 00:00 UTC
fee = lambda p: 0.07 * p * (1 - p)
PHI = lambda x: 0.5 * (1 + math.erf(x / math.sqrt(2)))
MISE = 10.0
K_FIGE = 1.8                                                  # H1090, ajusté sur 11–12.10
FENETRES = (3, 5, 10)
HORIZONS = (10, 30, 60)


# ------------------------------------------------------------------ extraction compacte
def extraire_un(f):
    try:
        R = json.load(gzip.open(f))
    except Exception:
        return None
    st = R["start"]; m = R.get("marche") or {}; T0 = st * 1000.0
    cl = [(round((x[0] - T0) / 1000, 3), round((x[2] - T0) / 1000), x[3]) for x in (R.get("cl2") or []) if x[3]]
    cb = []; bn = []
    for e in R.get("ex") or []:
        tr = round((e[0] - T0) / 1000, 3)
        if len(e) > 4 and e[4] and e[4][0] is not None: cb.append((tr, e[4][0]))
        if len(e) > 3 and e[3] and e[3][0] is not None: bn.append((tr, e[3][0]))
    snap = []
    for s in R.get("snap") or []:
        ub, ua, db, da = s[1:5]
        snap.append([round((s[0] - T0) / 1000, 3), ub[0][0] if ub else None, ua[0][0] if ua else None, ua[0][1] if ua else None,
                     db[0][0] if db else None, da[0][0] if da else None, da[0][1] if da else None])
    return dict(st=st, strikeTwap=m.get("strikeTwap"), coupe=bool(R.get("coupe")), cl=cl, cb=cb, bn=bn, snap=snap)


# ------------------------------------------------------------------ préparation : une série par cycle, une ligne par photo
def preparer(cache):
    CY = {c["st"]: c for c in json.load(gzip.open(cache))}
    O = json.load(open(os.path.join(RACINE, "bot95", "officiels.json")))
    acc = [0, 0]; sig_dernier = None; series = {}; nb = collections.Counter()
    for st in sorted(CY):
        c = CY[st]; K = c["strikeTwap"]
        o = (O.get(f"BTC:{st}") or {}).get("gagnant"); nx = CY.get(st + 300); g2 = None
        if nx and nx.get("strikeTwap") and K: g2 = "Up" if nx["strikeTwap"] >= K else "Down"
        if o and g2: acc[0] += 1; acc[1] += (o == g2)
        gagnant = o or g2
        pv = CY.get(st - 300); sig = None; base = None
        if pv:
            obs = {}
            for _, s, p in pv["cl"]: obs[s] = p
            ks = sorted(s for s in obs if 0 <= s < 300)
            d = [obs[b] - obs[a] for a, b in zip(ks, ks[1:]) if b - a == 1]
            if len(d) > 150: sig = float(np.std(d))
            cbs = {}
            for tr, px in pv["cb"]: cbs[int(tr // 1)] = px
            dd = [cbs[s] - obs[s] for s in ks if s in cbs]
            if len(dd) > 100: base = float(np.median(dd))
        if sig: sig_dernier = sig
        else: sig = sig_dernier
        part = "exploration" if J11 <= st < J13 else ("validation" if J13 <= st < J15 else None)
        if part is None: continue
        nb[(part, "tous")] += 1
        if not (K and gagnant and sig and len(c["snap"]) > 200 and not c["coupe"]): continue
        nb[(part, "ok")] += 1
        y = 1 if gagnant == "Up" else 0
        clr = [x[0] for x in c["cl"]]; cbr = [x[0] for x in c["cb"]]; bnr = [x[0] for x in c["bn"]]
        sd = sig * K_FIGE
        rows = {}
        for s in c["snap"]:
            t, ub, ua, uaz, db, da, daz = s
            if t < 0 or t >= 300 or ub is None or ua is None: continue
            sec = int(round(t))
            if sec in rows: continue
            j = bisect.bisect_right(clr, t) - 1
            if j < 0: continue
            Scl = c["cl"][j][2]
            jb = bisect.bisect_right(cbr, t) - 1
            S = (c["cb"][jb][1] - base) if (jb >= 0 and base is not None and t - c["cb"][jb][0] < 3) else Scl
            jn = bisect.bisect_right(bnr, t) - 1
            BN = c["bn"][jn][1] if jn >= 0 and t - c["bn"][jn][0] < 3 else None
            # partie déjà connue de la moyenne finale (observations Chainlink 240–299 reçues avant t)
            vu = {}
            if t >= 240:
                for r_, o_, p_ in c["cl"][: j + 1]:
                    if 240 <= o_ < 300: vu[o_] = p_
            n = len(vu); mm = 60 - n
            if mm <= 0: p = 1.0 if (sum(vu.values()) / 60 >= K) else 0.0
            else:
                mu = (sum(vu.values()) + mm * S) / 60
                var = mm * (mm + 1) * (2 * mm + 1) / 6 / 3600
                if t < 240: var += 240 - t
                p = PHI((mu - K) / (sd * math.sqrt(var)))
            rows[sec] = dict(t=t, mid=(ub + ua) / 2, ub=ub, ua=ua, uaz=uaz, db=db, da=da, daz=daz, p=p, S=S, BN=BN)
        series[st] = dict(part=part, y=y, rows=rows, sig=sig)
    return series, acc, nb


# ------------------------------------------------------------------ événements : chaque seconde d'un cycle où le résidu est mesurable
def evenements(series, w, tmin=10, tmax=270):
    E = []
    for st, C in series.items():
        R = C["rows"]
        for sec in range(tmin, tmax):
            a, b = R.get(sec - w), R.get(sec)
            if not a or not b: continue
            if b["ua"] - b["ub"] > 0.03 or a["ua"] - a["ub"] > 0.03: continue         # carnet trop large : milieu non fiable
            if not (0.05 <= b["mid"] <= 0.95): continue
            dm = b["mid"] - a["mid"]; dp = b["p"] - a["p"]
            fut = {}
            for h in HORIZONS:
                f = R.get(sec + h)
                if f and f["ua"] - f["ub"] <= 0.03: fut[h] = (f["mid"] - b["mid"], (f["mid"] - b["mid"]) - (f["p"] - b["p"]))
            dbn = (b["BN"] - a["BN"]) if (a["BN"] and b["BN"]) else None
            E.append(dict(st=st, part=C["part"], sec=sec, w=w, dm=dm, dp=dp, r=dm - dp, mid=b["mid"], p=b["p"], y=C["y"], fut=fut,
                          dbn=dbn, sig=C["sig"]))
    return E


def boot_moy(vals, cyc, rng, B=2000):
    """moyenne + IC 90 % par bootstrap sur les cycles"""
    if len(vals) < 5: return None
    g = collections.defaultdict(list)
    for v, c in zip(vals, cyc): g[c].append(v)
    S = np.array([sum(v) for v in g.values()]); N = np.array([len(v) for v in g.values()])
    idx = rng.integers(0, len(S), (B, len(S)))
    m = S[idx].sum(1) / N[idx].sum(1)
    return [float(np.sum(S) / np.sum(N)), float(np.percentile(m, 5)), float(np.percentile(m, 95)), int(len(vals)), int(len(S))]


def descriptif(series, rng):
    out = {}
    for w in FENETRES:
        E = evenements(series, w)
        out[f"w{w}"] = d = {}
        d["n_secondes"] = len(E)
        d["r_quantiles"] = np.percentile([e["r"] for e in E], [1, 5, 25, 50, 75, 95, 99]).round(4).tolist()
        d["dm_quantiles"] = np.percentile([e["dm"] for e in E], [1, 5, 50, 95, 99]).round(4).tolist()
        d["dp_quantiles"] = np.percentile([e["dp"] for e in E], [1, 5, 50, 95, 99]).round(4).tolist()
        # pente : mouvement futur du milieu sur le résidu (positif = continue, négatif = revient)
        for h in HORIZONS:
            X = [(e["r"], e["fut"][h][0], e["fut"][h][1], e["st"]) for e in E if h in e["fut"]]
            r = np.array([x[0] for x in X]); f = np.array([x[1] for x in X]); fr = np.array([x[2] for x in X]); cy = np.array([x[3] for x in X])
            uc = np.unique(cy); pos = {c: np.where(cy == c)[0] for c in uc}
            bs = []; bsr = []
            for _ in range(500):
                ii = np.concatenate([pos[c] for c in rng.choice(uc, len(uc))])
                bs.append(np.polyfit(r[ii], f[ii], 1)[0]); bsr.append(np.polyfit(r[ii], fr[ii], 1)[0])
            d[f"pente_h{h}"] = [float(np.polyfit(r, f, 1)[0]), float(np.percentile(bs, 5)), float(np.percentile(bs, 95)), len(X)]
            d[f"pente_resid_h{h}"] = [float(np.polyfit(r, fr, 1)[0]), float(np.percentile(bsr, 5)), float(np.percentile(bsr, 95))]
        # tableau par seuil : |r| ≥ X et |Δp| petit (BTC calme) → suite signée (positif = continue dans le sens du résidu)
        tab = []
        for X in (0.03, 0.05, 0.08, 0.12):
            for calme in (None, 0.02):
                sel = [e for e in E if abs(e["r"]) >= X and (calme is None or abs(e["dp"]) <= calme)]
                ligne = dict(seuil=X, dp_max=calme, n=len(sel), cycles=len({e["st"] for e in sel}),
                             r_moy_abs=float(np.mean([abs(e["r"]) for e in sel])) if sel else None)
                for h in HORIZONS:
                    s2 = [e for e in sel if h in e["fut"]]
                    ligne[f"suite_mid_h{h}"] = boot_moy([math.copysign(1, e["r"]) * e["fut"][h][0] for e in s2], [e["st"] for e in s2], rng)
                    ligne[f"suite_resid_h{h}"] = boot_moy([math.copysign(1, e["r"]) * e["fut"][h][1] for e in s2], [e["st"] for e in s2], rng)
                # au règlement : gagnant (côté poussé vers le haut) moins milieu au signal ; et moins proba modèle
                ligne["final_moins_mid"] = boot_moy([(e["y"] - e["mid"]) * math.copysign(1, e["r"]) for e in sel], [e["st"] for e in sel], rng)
                ligne["final_moins_modele"] = boot_moy([(e["y"] - e["p"]) * math.copysign(1, e["r"]) for e in sel], [e["st"] for e in sel], rng)
                tab.append(ligne)
        d["par_seuil"] = tab
    return out


# ------------------------------------------------------------------ règles
_EV = {}
def executer(series, regle, cycles_periode):
    """regle = (w, seuil r, |Δp| max, sens 'revenir'/'suivre', t min, t max, prix min, prix max)"""
    w, X, dpmax, sens, tmin, tmax, pmin, pmax = regle; achats = {}
    cle = (id(series), w)
    if cle not in _EV: _EV[cle] = evenements(series, w, 10, 290)
    E = [e for e in _EV[cle] if tmin <= e["sec"] < tmax and abs(e["r"]) >= X and abs(e["dp"]) <= dpmax]
    E.sort(key=lambda e: (e["st"], e["sec"]))
    for e in E:
        if e["st"] in achats: continue
        R = series[e["st"]]["rows"]; nx = R.get(e["sec"] + 1)
        if not nx: continue
        up = (e["r"] < 0) if sens == "revenir" else (e["r"] > 0)
        a, z = (nx["ua"], nx["uaz"]) if up else (nx["da"], nx["daz"])
        if a is None or not z or not (pmin <= a <= pmax): continue
        q = min(MISE / a, z); gm = e["y"] == (1 if up else 0)
        achats[e["st"]] = dict(st=e["st"], sec=e["sec"], up=up, a=a, q=q, mise=q * a, gm=gm, pn=q * ((1 if gm else 0) - a - fee(a)),
                               p=e["p"] if up else 1 - e["p"], r=e["r"])
    vec = np.array([achats[s]["pn"] if s in achats else 0.0 for s in cycles_periode])
    return list(achats.values()), vec


def resume(A, vec, nreg, rng):
    if not A: return dict(achats=0)
    bs = vec[rng.integers(0, len(vec), (10000, len(vec)))].sum(1)
    lo, hi = 100 * 0.05 / nreg, 100 - 100 * 0.05 / nreg
    mise = sum(a["mise"] for a in A); pn = float(vec.sum())
    return dict(achats=len(A), gagnes=int(sum(a["gm"] for a in A)), prix=float(np.mean([a["a"] for a in A])),
                proba_modele=float(np.mean([a["p"] for a in A])), mise=float(mise), pnl=pn, roi=pn / mise if mise else None,
                part_up=float(np.mean([a["up"] for a in A])), ic90=np.percentile(bs, [5, 95]).tolist(),
                ic_bonf=np.percentile(bs, [lo, hi]).tolist(), cycles=len(vec))


# RÈGLES FIGÉES (remplies après l'exploration, avant toute lecture de la validation)
# (fenêtre s, |résidu| min, |Δp| max, sens, t min, t max, prix d'achat min, prix d'achat max)
# Exploration (405 cycles utilisables, 11–12.10) : le milieu ne revient presque pas (pente Δmid futur / résidu ≈ −0,01 à −0,03) ;
# c'est surtout le modèle qui rattrape le carnet (pente du résidu futur ≈ −0,45) ; gagnant − milieu au signal ≈ 0 (pas d'erreur au règlement).
# Balayage de 720 combinaisons : 170 / 638 positives ; avec BTC calme, « revenir » fait mieux que « suivre » en début (10–150 s) et en fin
# (240–285 s), « suivre » perd presque partout sauf un îlot à 150–240 s. Les trois retenues sont les meilleures plausibles (biais de sélection).
REGLES = {"R1 revenir 10–150 s, 5 s, résidu ≥ 0,08, BTC calme (|Δp| ≤ 0,01), prix 0,20–0,80": (5, 0.08, 0.01, "revenir", 10, 150, 0.20, 0.80),
          # exploration : 228 achats, 113 gagnés, prix 0,45, ROI +8,3 %, +182 $, IC 90 % [−105 ; +472]
          "R2 revenir 240–285 s, 5 s, résidu ≥ 0,10, BTC calme (|Δp| ≤ 0,03), prix 0,20–0,80": (5, 0.10, 0.03, "revenir", 240, 285, 0.20, 0.80),
          # exploration : 36 achats, 19 gagnés, prix 0,39, ROI +56,5 %, +174 $, IC 90 % [+12 ; +350]
          "R3 suivre 150–240 s, 10 s, résidu ≥ 0,06, BTC calme (|Δp| ≤ 0,01), prix 0,05–0,95": (10, 0.06, 0.01, "suivre", 150, 240, 0.05, 0.95)}
          # exploration : 201 achats, 128 gagnés, prix 0,57, ROI +15,4 %, +299 $, IC 90 % [−5 ; +622]


if __name__ == "__main__":
    if sys.argv[1] == "--extraire":
        from multiprocessing import Pool
        fs = sorted(glob.glob(os.path.join(sys.argv[2], "*", "*.json.gz")))
        with Pool(2) as P: out = [x for x in P.imap(extraire_un, fs, chunksize=4) if x]
        json.dump(out, gzip.open(sys.argv[3], "wt")); print(len(out)); sys.exit()
    VALID = "--validation" in sys.argv
    series_all, acc, nb = preparer(sys.argv[1]); rng = np.random.default_rng(1091)
    part = "validation" if VALID else "exploration"
    SP = {k: v for k, v in series_all.items() if v["part"] == part}
    cyc = sorted(SP)
    res = dict(periode=part, cycles=len(cyc), cycles_totaux_periode=nb[(part, "tous")], accord_gagnant_officiel_vs_cycle_suivant=acc)
    res["descriptif"] = descriptif(SP, rng)
    if not VALID:
        sc = []
        for w in FENETRES:
            for X in (0.04, 0.06, 0.08, 0.10, 0.15):
                for dpmax in (0.01, 0.03, 1.0):
                    for sens in ("revenir", "suivre"):
                        for (tmin, tmax) in ((10, 150), (150, 240), (10, 240), (240, 285)):
                            for (pmin, pmax) in ((0.05, 0.95), (0.20, 0.80)):
                                rg = (w, X, dpmax, sens, tmin, tmax, pmin, pmax)
                                A, v = executer(SP, rg, cyc)
                                r = resume(A, v, 3, rng); r["regle"] = rg; sc.append(r)
        res["balayage"] = sc
    else:
        assert REGLES, "règles non figées"
        res["regles"] = {}
        for nom, rg in REGLES.items():
            A, v = executer(SP, rg, cyc)
            r = resume(A, v, len(REGLES), rng)
            for jour, (d0, d1) in (("13.10", (J13, J13 + 86400)), ("14.10", (J13 + 86400, J15))):
                cj = [s for s in cyc if d0 <= s < d1]; Aj = [a for a in A if d0 <= a["st"] < d1]
                r[jour] = resume(Aj, np.array([sum(a["pn"] for a in Aj if a["st"] == s) for s in cj]), len(REGLES), rng)
            res["regles"][nom] = r
    s = json.dumps(res, ensure_ascii=False, indent=1, default=str)
    open(os.path.join(ICI, f"surreaction_poly_h1091_{part}.json"), "w").write(s)
    print(s[:2000])
