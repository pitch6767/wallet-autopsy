"""BOT95 — H1092 « le carnet comme signal seul » (Polymarket BTC 5 min Up/Down). Hors ligne, aucun ordre, aucun bot modifié.
IDÉE : en direct, les stratégies semblaient mieux marcher quand le carnet (5 meilleurs niveaux) penchait de notre côté (filtre « + carnet »).
  Le déséquilibre du carnet, PRIS SEUL, prédit-il le gagnant au-delà du prix (milieu) et au-delà du modèle de règlement ?
MESURES (jeton Up ; le carnet Down est le miroir exact du carnet Up : acheteur Down à x = vendeur Up à 1 − x, mêmes tailles) :
  I5   = (Σ tailles acheteurs − Σ tailles vendeurs) / total, 5 meilleurs niveaux de chaque côté (> 0 = carnet penché vers Up) ;
  I1   = même chose au seul meilleur niveau ; micro = microprix − milieu = (vendeur·T_ach + acheteur·T_vend)/(T_ach + T_vend) − milieu ;
  Iloin = déséquilibre des niveaux 3 à 5 seulement (profondeur loin du milieu) ;
  W5   = log(Σach_t / Σach_{t−5}) − log(Σvend_t / Σvend_{t−5}) (retrait soudain d'un côté : W5 < 0 = les acheteurs Up se retirent) ;
  Nniv = nb de niveaux acheteurs − nb de niveaux vendeurs à 5 c ou moins du milieu.
  p = probabilité de Up du modèle de règlement H1090/H1091 (k = 1,8 figé, Coinbase ajusté) — repris tel quel de surreaction_poly_h1091.py.
DESCRIPTIF : aux instants t = 30, 60, …, 270 s : (gagnant − milieu) par décile de I5 (déciles fixés sur l'exploration), IC 90 % par cycles.
LOGISTIQUE : logit P(Up) = a + b·logit(milieu) [M0] contre M0 + c·I5 + d·micro + e·Iloin + f·W5 + g·Nniv [M1] ;
  et a + b·logit(milieu) + h·logit(p) [M2] contre M2 + mêmes mesures [M3]. Ajustés sur l'exploration (instants 30…270 s regroupés),
  appliqués tels quels à la validation ; différence de Brier (M1 − M0, M3 − M2) avec IC 90 % par cycles (< 0 = le carnet apporte quelque chose).
DÉCOUPAGE : exploration = cycles du 11.10 + 12.10 (UTC) ; validation = cycles ≥ 13.10 00:00 jusqu'au dernier exporté (13.10 = réservé).
EXÉCUTION SIMULÉE : décision sur la photo de la seconde t ; achat au meilleur vendeur de la photo SUIVANTE (≈ t + 1 s), limité à la taille
  affichée, 10 $ maximum ; frais 0,07·p·(1−p) par part ; gardé jusqu'au règlement ; un achat par cycle et par règle (premier déclenchement).
CRITÈRE : borne basse de l'IC 90 % corrigé Bonferroni (nb de règles figées ; bootstrap par cycles, 10 000 tirages, tous les cycles de la
  période comptés, 0 $ sans achat) du P&L de validation > 0. Aucun fantôme sans accord de Pitch.
Usage : python3 etude/bot5min/carnet_signal_h1092.py --extraire <dossier cycles> <cache.json.gz>
        python3 etude/bot5min/carnet_signal_h1092.py <cache.json.gz> [--validation]"""
import sys, os, json, gzip, glob, math, collections
import numpy as np

ICI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, ICI)
import surreaction_poly_h1091 as H91                                   # extraction de base + modèle de règlement (k = 1,8)

J11, J13 = H91.J11, H91.J13
H91.J15 = 1792108800                                                   # validation ouverte jusqu'au 16.10 00:00 (dernier exporté)
fee = H91.fee; MISE = 10.0
GRILLE = list(range(30, 271, 30))
MESURES = ("I5", "micro", "Iloin", "W5", "Nniv")


def extraire_un(f):
    c = H91.extraire_un(f)
    if c is None: return None
    R = json.load(gzip.open(f)); T0 = R["start"] * 1000.0; lv = []
    for s in R.get("snap") or []:
        ub, ua = s[1], s[2]
        lv.append([round((s[0] - T0) / 1000, 3), [[x[0], round(x[1], 1)] for x in (ub or [])[:5]],
                   [[x[0], round(x[1], 1)] for x in (ua or [])[:5]]])
    c["lv"] = lv
    return c


def mesures_carnet(ub, ua):
    if not ub or not ua: return None
    B = [x[1] for x in ub]; A = [x[1] for x in ua]; sb, sa = sum(B), sum(A)
    if sb + sa <= 0 or B[0] + A[0] <= 0: return None
    mid = (ub[0][0] + ua[0][0]) / 2
    micro = (ua[0][0] * B[0] + ub[0][0] * A[0]) / (B[0] + A[0]) - mid
    fb, fa = sum(B[2:]), sum(A[2:])
    return dict(I5=(sb - sa) / (sb + sa), I1=(B[0] - A[0]) / (B[0] + A[0]), micro=micro,
                Iloin=(fb - fa) / (fb + fa) if fb + fa > 0 else 0.0, sb=sb, sa=sa,
                Nniv=sum(1 for x in ub if mid - x[0] <= 0.05 + 1e-9) - sum(1 for x in ua if x[0] - mid <= 0.05 + 1e-9),
                ub=ub[0][0], ubz=B[0], ua=ua[0][0], uaz=A[0])


def preparer(cache):
    series, acc, nb = H91.preparer(cache)
    for c in json.load(gzip.open(cache)):
        if c["st"] not in series: continue
        R = series[c["st"]]["rows"]; vu = set()
        for t, ub, ua in c["lv"]:
            if t < 0 or t >= 300: continue
            sec = int(round(t))
            if sec in vu: continue
            vu.add(sec)
            if sec in R:
                m = mesures_carnet(ub, ua)
                if m: R[sec].update(m); R[sec]["ok"] = True
        for sec, r in R.items():
            a = R.get(sec - 5)
            r["W5"] = (math.log(r["sb"] / a["sb"]) - math.log(r["sa"] / a["sa"])) if (r.get("ok") and a and a.get("ok")
                                                                                     and a["sb"] > 0 and a["sa"] > 0 and r["sb"] > 0 and r["sa"] > 0) else 0.0
    return series, acc, nb


def points(series, grille=GRILLE):
    P = []
    for st, C in series.items():
        R = C["rows"]
        for t in grille:
            r = R.get(t)
            if not r or not r.get("ok"): continue
            if r["ua"] - r["ub"] > 0.03 or not (0.02 <= r["mid"] <= 0.98): continue
            P.append(dict(st=st, t=t, y=C["y"], mid=r["mid"], p=min(max(r["p"], 1e-4), 1 - 1e-4), **{k: r[k] for k in MESURES + ("I1",)}))
    return P


def boot_moy(vals, cyc, rng, B=2000):
    if len(vals) < 5: return None
    g = collections.defaultdict(list)
    for v, c in zip(vals, cyc): g[c].append(v)
    S = np.array([sum(v) for v in g.values()]); N = np.array([len(v) for v in g.values()])
    idx = rng.integers(0, len(S), (B, len(S))); m = S[idx].sum(1) / N[idx].sum(1)
    return [round(float(np.sum(S) / np.sum(N)), 4), round(float(np.percentile(m, 5)), 4), round(float(np.percentile(m, 95)), 4), int(len(vals)), int(len(S))]


def deciles(P, bornes, rng, cle="I5"):
    out = []
    v = np.array([p[cle] for p in P]); d = np.searchsorted(bornes, v, side="right")
    for k in range(10):
        sel = [p for p, dd in zip(P, d) if dd == k]
        out.append(dict(decile=k + 1, I_moy=round(float(np.mean([p[cle] for p in sel])), 3) if sel else None,
                        mid_moy=round(float(np.mean([p["mid"] for p in sel])), 3) if sel else None,
                        gagnant_moins_mid=boot_moy([p["y"] - p["mid"] for p in sel], [p["st"] for p in sel], rng),
                        gagnant_moins_modele=boot_moy([p["y"] - p["p"] for p in sel], [p["st"] for p in sel], rng)))
    return out


# ------------------------------------------------------------------ logistique (Newton, petite pénalité ridge pour la stabilité)
lg = lambda x: math.log(min(max(x, 0.005), 0.995) / (1 - min(max(x, 0.005), 0.995)))
def X_de(P, modele):
    cols = [[1.0] * len(P), [lg(p["mid"]) for p in P]]
    if modele in ("M2", "M3"): cols.append([lg(p["p"]) for p in P])
    if modele in ("M1", "M3"):
        for k in MESURES: cols.append([p[k] for p in P])
    return np.array(cols).T


def ajuster(X, y, lam=1e-3):
    w = np.zeros(X.shape[1])
    for _ in range(50):
        z = np.clip(X @ w, -30, 30); q = 1 / (1 + np.exp(-z))
        g = X.T @ (q - y) + lam * w; H = (X * (q * (1 - q))[:, None]).T @ X + lam * np.eye(len(w))
        dw = np.linalg.solve(H, g); w -= dw
        if np.max(np.abs(dw)) < 1e-9: break
    return w


def predire(X, w): return 1 / (1 + np.exp(-np.clip(X @ w, -30, 30)))


def brier_diff(P, q_a, q_b, rng, B=4000):
    """Brier(b) − Brier(a), IC 90 % par cycles"""
    y = np.array([p["y"] for p in P]); d = (q_b - y) ** 2 - (q_a - y) ** 2; cy = np.array([p["st"] for p in P])
    uc, inv = np.unique(cy, return_inverse=True); S = np.bincount(inv, d); N = np.bincount(inv)
    idx = rng.integers(0, len(uc), (B, len(uc))); m = S[idx].sum(1) / N[idx].sum(1)
    return [float(d.mean()), float(np.percentile(m, 5)), float(np.percentile(m, 95)), len(P), len(uc)]


def logistique(Pex, Pval, rng):
    out = {}; yex = np.array([p["y"] for p in Pex])
    W = {m: ajuster(X_de(Pex, m), yex) for m in ("M0", "M1", "M2", "M3")}
    out["coefficients_exploration"] = {m: [round(float(x), 4) for x in w] for m, w in W.items()}
    # exploration : validation croisée 5 blocs par cycles
    cyc = sorted({p["st"] for p in Pex}); bloc = {c: i % 5 for i, c in enumerate(cyc)}
    qcv = {m: np.zeros(len(Pex)) for m in W}
    for b in range(5):
        tr = [i for i, p in enumerate(Pex) if bloc[p["st"]] != b]; te = [i for i, p in enumerate(Pex) if bloc[p["st"]] == b]
        for m in W:
            Xm = X_de(Pex, m); w = ajuster(Xm[tr], yex[tr]); qcv[m][te] = predire(Xm[te], w)
    out["exploration_cv"] = dict(M1_moins_M0=brier_diff(Pex, qcv["M0"], qcv["M1"], rng), M3_moins_M2=brier_diff(Pex, qcv["M2"], qcv["M3"], rng),
                                 brier_mid=float(np.mean([(p["mid"] - p["y"]) ** 2 for p in Pex])), brier_M0=float(np.mean((qcv["M0"] - yex) ** 2)))
    if Pval:
        yv = np.array([p["y"] for p in Pval]); qv = {m: predire(X_de(Pval, m), W[m]) for m in W}
        out["validation"] = dict(M1_moins_M0=brier_diff(Pval, qv["M0"], qv["M1"], rng), M3_moins_M2=brier_diff(Pval, qv["M2"], qv["M3"], rng),
                                 brier_mid=float(np.mean([(p["mid"] - p["y"]) ** 2 for p in Pval])), brier_M0=float(np.mean((qv["M0"] - yv) ** 2)),
                                 brier_M1=float(np.mean((qv["M1"] - yv) ** 2)))
    return out


# ------------------------------------------------------------------ règles
def executer(series, regle, cycles_periode):
    """regle = (mesure, seuil, côté 'tous'/'moins_cher', t min, t max, prix min, prix max) : mesure ≥ seuil → Up ; ≤ −seuil → Down"""
    k, X, cote, tmin, tmax, pmin, pmax = regle; achats = {}
    for st in cycles_periode:
        R = series[st]["rows"]; y = series[st]["y"]
        for sec in range(tmin, tmax + 1):
            r = R.get(sec)
            if not r or not r.get("ok") or r["ua"] - r["ub"] > 0.03: continue
            v = r[k]
            if v >= X: up = True
            elif v <= -X: up = False
            else: continue
            if cote == "moins_cher" and ((up and r["mid"] > 0.5) or ((not up) and r["mid"] < 0.5)): continue
            nx = R.get(sec + 1)
            if not nx or not nx.get("ok"): continue
            a, z = (nx["ua"], nx["uaz"]) if up else (round(1 - nx["ub"], 4), nx["ubz"])
            if not z or not (pmin <= a <= pmax): continue
            q = min(MISE / a, z); gm = y == (1 if up else 0)
            achats[st] = dict(st=st, sec=sec, up=up, a=a, q=q, mise=q * a, gm=gm, pn=q * ((1 if gm else 0) - a - fee(a)),
                              p=r["p"] if up else 1 - r["p"])
            break
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
# (mesure, seuil, côté, t min, t max, prix d'achat min, prix d'achat max)
# Exploration (405 cycles utilisables, 11–12.10) : (gagnant − milieu) par décile de I5 sans pente (−4 c à +2,5 c, tous les IC contiennent 0,
# les deux extrêmes négatifs) ; logistique en validation croisée : Brier M1 − M0 = +0,00004 [−0,0008 ; +0,0008] (rien ajouté au milieu),
# M3 − M2 = +0,00006 [−0,0008 ; +0,0009]. Nniv quasi toujours 0 (5 niveaux à 1 c d'écart) sauf carnet troué d'un côté.
# Balayage de 208 règles : 59 positives seulement (pire que le hasard) ; I5 « tous côtés » 1/24 positive. Les trois retenues sont les
# meilleures par borne basse de l'IC 90 %, une par famille (biais de sélection assumé) :
REGLES = {"R1 niveaux : ≥ 2 niveaux de plus du côté acheté à ≤ 5 c, 120–240 s, prix 0,05–0,95": ("Nniv", 2, "tous", 120, 240, 0.05, 0.95),
          # exploration : 237 achats, 159 gagnés, prix 0,61, ROI +11,0 %, +246 $, IC 90 % [−6 ; +505]
          "R2 meilleur niveau penché ≥ 0,5 de notre côté, 60–240 s, prix 0,20–0,80": ("I1", 0.5, "tous", 60, 240, 0.20, 0.80),
          # exploration : 352 achats, 189 gagnés, prix 0,51, ROI +7,8 %, +257 $, IC 90 % [−104 ; +617]
          "R3 retrait : l'autre côté se vide (W5 ≥ 1,5), côté le moins cher, 240–285 s, prix 0,20–0,80": ("W5", 1.5, "moins_cher", 240, 285, 0.20, 0.80)}
          # exploration : 52 achats, 17 gagnés, prix 0,31, ROI +26,1 %, +117 $, IC 90 % [−84 ; +329]


if __name__ == "__main__":
    if sys.argv[1] == "--extraire":
        from multiprocessing import Pool
        fs = sorted(glob.glob(os.path.join(sys.argv[2], "*", "*.json.gz")))
        with Pool(2) as Po: out = [x for x in Po.imap(extraire_un, fs, chunksize=4) if x]
        json.dump(out, gzip.open(sys.argv[3], "wt")); print(len(out)); sys.exit()
    VALID = "--validation" in sys.argv
    series_all, acc, nb = preparer(sys.argv[1]); rng = np.random.default_rng(1092)
    part = "validation" if VALID else "exploration"
    SE = {k: v for k, v in series_all.items() if v["part"] == "exploration"}
    SP = {k: v for k, v in series_all.items() if v["part"] == part}
    cyc = sorted(SP)
    res = dict(periode=part, cycles=len(cyc), cycles_totaux_periode=nb[(part, "tous")], accord_gagnant_officiel_vs_cycle_suivant=acc,
               premier=min(cyc), dernier=max(cyc))
    Pex = points(SE); Pp = points(SP)
    bornes = np.percentile([p["I5"] for p in Pex], range(10, 100, 10))
    res["bornes_deciles_I5"] = bornes.round(3).tolist()
    res["deciles_I5"] = deciles(Pp, bornes, rng)
    res["deciles_I5_par_moment"] = {f"{a}-{b}s": deciles([p for p in Pp if a <= p["t"] <= b], bornes, rng) for a, b in ((30, 90), (120, 180), (210, 270))}
    for k in ("micro", "Iloin", "W5", "Nniv", "I1"):
        bk = np.percentile([p[k] for p in Pex], range(10, 100, 10)); res[f"deciles_{k}"] = dict(bornes=np.round(bk, 4).tolist(), tab=deciles(Pp, bk, rng, k))
    res["correlation_I5_milieu"] = float(np.corrcoef([p["I5"] for p in Pp], [p["mid"] for p in Pp])[0, 1])
    res["logistique"] = logistique(Pex, Pp if VALID else None, rng)
    if not VALID:
        sc = []
        for k, seuils in (("I5", (0.3, 0.5, 0.7)), ("I1", (0.5, 0.8)), ("micro", (0.003, 0.006)), ("Iloin", (0.5, 0.7)), ("W5", (0.7, 1.5)), ("Nniv", (2, 4))):
            for X in seuils:
                for cote in ("tous", "moins_cher"):
                    for (tmin, tmax) in ((30, 120), (60, 240), (120, 240), (240, 285)):
                        for (pmin, pmax) in ((0.05, 0.95), (0.20, 0.80)):
                            rg = (k, X, cote, tmin, tmax, pmin, pmax)
                            A, v = executer(SP, rg, cyc); r = resume(A, v, 3, rng); r["regle"] = rg; sc.append(r)
        res["balayage"] = sc
    else:
        assert REGLES, "règles non figées"
        res["regles"] = {}
        jours = sorted({(s - J11) // 86400 for s in cyc})
        for nom, rg in REGLES.items():
            A, v = executer(SP, rg, cyc); r = resume(A, v, len(REGLES), rng)
            for j in jours:
                d0 = J11 + j * 86400; cj = [s for s in cyc if d0 <= s < d0 + 86400]; Aj = [a for a in A if d0 <= a["st"] < d0 + 86400]
                r[f"{11 + j}.10"] = resume(Aj, np.array([sum(a["pn"] for a in Aj if a["st"] == s) for s in cj]), len(REGLES), rng)
            res["regles"][nom] = r
    s = json.dumps(res, ensure_ascii=False, indent=1, default=str)
    open(os.path.join(ICI, f"carnet_signal_h1092_{part}.json"), "w").write(s)
    print(s[:1500])
