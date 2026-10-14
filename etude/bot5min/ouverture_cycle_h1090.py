"""BOT95 — H1090 « l'ouverture du cycle » (Polymarket BTC 5 min Up/Down). Hors ligne, aucun ordre, aucun bot modifié.
IDÉE : le prix à battre K est la MOYENNE Chainlink des 60 s avant le début (= strikeTwap enregistré = « ptb » officiel), et le règlement
  compare la moyenne Chainlink des 60 dernières secondes. Au début du cycle, le prix Chainlink du moment S n'est donc pas égal à K : il a
  déjà une « avance » (S − K) mesurable. La vraie probabilité de Up dans les 30 premières secondes n'est pas 0,50. Le carnet Polymarket
  en tient-il compte tout de suite, ou reste-t-il collé à 0,50 ?
MODÈLE (fixé avant toute lecture des résultats) : à t secondes après le début (t < 240), moyenne finale attendue = S ; écart-type
  = σ · k · √(260 − t) (marche aléatoire : (240 − t) s jusqu'à la fenêtre + 60/3 pour la moyenne de la fenêtre) ; P(Up) = Φ((S − K) / écart-type).
  σ = écart-type des variations Chainlink d'une seconde sur le cycle PRÉCÉDENT (passé seulement ; à défaut, le dernier σ connu).
  S_cl = dernier prix Chainlink reçu à l'instant t (cl2) ; S_cb = Coinbase reçu à t − écart médian (Coinbase − Chainlink) du cycle précédent
  (Chainlink arrive avec 1–2 s de retard). k = 1 par défaut ; k ajusté sur l'exploration seulement (maximum de vraisemblance) et figé.
DONNÉES : enregistreur de Dublin, branche donnees-rapide (cycles/AAAA-MM-JJ/<début>.json.gz) ; photos 5 niveaux Up/Down chaque seconde
  (snap) ; gagnant = bot95/officiels.json, sinon prix à battre du cycle suivant (= moyenne finale de celui-ci ; vérifié sur le recouvrement).
DÉCOUPAGE CHRONOLOGIQUE : exploration = cycles commençant le 11.10 et le 12.10 (UTC) ; validation = 13.10 + 14.10 (13.10 = jour réservé,
  lu UNE seule fois après le gel des règles).
EXÉCUTION SIMULÉE : décision sur la photo du carnet à l'instant t, achat au meilleur prix vendeur de cette photo, 10 $ maximum,
  limité à la taille affichée au meilleur prix ; frais 0,07·p·(1−p) par part ; gardé jusqu'au règlement ; un seul achat par cycle et par règle
  (première photo qui déclenche). Variante pessimiste : même décision, achat au meilleur prix vendeur de la photo SUIVANTE (≈ +1 s).
CRITÈRE : borne basse de l'IC 90 % corrigé Bonferroni (3 règles → percentiles 1,67 / 98,33 ; bootstrap par cycles, 10 000 tirages,
  tous les cycles de la période comptés, 0 $ sans achat) du P&L de validation > 0. Aucun fantôme sans accord de Pitch.
Usage : python3 etude/bot5min/ouverture_cycle_h1090.py --extraire <dossier cycles> <cache.json.gz>
        python3 etude/bot5min/ouverture_cycle_h1090.py <cache.json.gz> [--validation]"""
import sys, os, json, gzip, glob, math, bisect, collections
import numpy as np

ICI = os.path.dirname(os.path.abspath(__file__)); RACINE = os.path.abspath(os.path.join(ICI, "..", ".."))
J11, J13, J15 = 1791676800, 1791849600, 1792022400          # 11.10, 13.10, 15.10 00:00 UTC
fee = lambda p: 0.07 * p * (1 - p)
PHI = lambda x: 0.5 * (1 + math.erf(x / math.sqrt(2)))
MISE = 10.0


# ------------------------------------------------------------------ extraction compacte (une lecture des gros fichiers)
def extraire_un(f):
    try:
        R = json.load(gzip.open(f))
    except Exception:
        return None
    st = R["start"]; m = R.get("marche") or {}; T0 = st * 1000.0
    cl = [(round((x[0] - T0) / 1000, 3), round((x[2] - T0) / 1000), x[3]) for x in (R.get("cl2") or []) if x[3]]
    tw = [(round((x[0] - T0) / 1000, 3), round((x[1] - T0) / 1000), x[2]) for x in (R.get("tw") or [])]
    cbs = {}; cbf = []
    for e in R.get("ex") or []:
        if len(e) < 5 or not e[4] or e[4][0] is None: continue
        tr = (e[0] - T0) / 1000; px = e[4][0]
        cbs[int(tr // 1)] = px
        if tr < 40: cbf.append((round(tr, 3), px))
    snap = [[round((s[0] - T0) / 1000, 3)] + s[1:5] for s in R.get("snap") or [] if (s[0] - T0) / 1000 < 40]
    return dict(st=st, strike=m.get("strike"), strikeTwap=m.get("strikeTwap"), coupe=bool(R.get("coupe")), version=R.get("version"),
                cl=cl, tw=tw, cbs=sorted(cbs.items()), cbf=cbf, snap=snap, nsnap=len(R.get("snap") or []))


# ------------------------------------------------------------------ préparation : une ligne par photo du carnet, t ∈ [0, 35)
def preparer(cache):
    CY = {c["st"]: c for c in json.load(gzip.open(cache))}
    O = json.load(open(os.path.join(RACINE, "bot95", "officiels.json")))
    acc = [0, 0]; sig_dernier = None; lignes = []; cycles = {}
    for st in sorted(CY):
        c = CY[st]; K = c["strikeTwap"]
        # gagnant
        o = (O.get(f"BTC:{st}") or {}).get("gagnant"); nx = CY.get(st + 300)
        g2 = None
        if nx and nx.get("strikeTwap") and K: g2 = "Up" if nx["strikeTwap"] >= K else "Down"
        if o and g2: acc[0] += 1; acc[1] += (o == g2)
        gagnant = o or g2
        # σ et écart Coinbase du cycle précédent (passé seulement)
        pv = CY.get(st - 300); sig = None; base = None
        if pv:
            obs = {}
            for _, s, p in pv["cl"]: obs[s] = p
            ks = sorted(s for s in obs if 0 <= s < 300)
            d = [obs[b] - obs[a] for a, b in zip(ks, ks[1:]) if b - a == 1]
            if len(d) > 150: sig = float(np.std(d))
            cbs = dict(pv["cbs"]); dd = [cbs[s] - obs[s] for s in ks if s in cbs]
            if len(dd) > 100: base = float(np.median(dd))
        if sig: sig_dernier = sig
        else: sig = sig_dernier
        part = "exploration" if J11 <= st < J13 else ("validation" if J13 <= st < J15 else None)
        ok = bool(K and gagnant and sig and c["snap"] and not c["coupe"])
        cycles[st] = dict(part=part, ok=ok, gagnant=gagnant, sig=sig, base=base)
        if not ok or part is None: continue
        y = 1 if gagnant == "Up" else 0
        clr = [x[0] for x in c["cl"]]; cbr = [x[0] for x in c["cbf"]]
        tw0 = [x[0] for x in c["tw"] if x[1] == 0]; k_connu = tw0[0] if tw0 else None
        for i, s in enumerate(c["snap"]):
            t = s[0]
            if t < 0 or t >= 35: continue
            j = bisect.bisect_right(clr, t) - 1
            if j < 0: continue
            Scl = c["cl"][j][2]; age_cl = t - c["cl"][j][1]
            jb = bisect.bisect_right(cbr, t) - 1
            Scb = (c["cbf"][jb][1] - base) if (jb >= 0 and base is not None and t - c["cbf"][jb][0] < 3) else None
            ub, ua, db, da = s[1], s[2], s[3], s[4]
            if not ub or not ua or not da: continue
            nxt = c["snap"][i + 1] if i + 1 < len(c["snap"]) else None
            lignes.append(dict(st=st, part=part, y=y, t=t, K=K, Scl=Scl, Scb=Scb, sig=sig, age_cl=age_cl, k_connu=k_connu,
                               ub=ub[0][0], ua=ua[0][0], uaz=ua[0][1], uad=sum(p * z for p, z in ua), ubd=sum(p * z for p, z in ub),
                               da=da[0][0], daz=da[0][1], dad=sum(p * z for p, z in da),
                               ua1=(nxt[2][0][0], nxt[2][0][1]) if nxt and nxt[2] else None,
                               da1=(nxt[4][0][0], nxt[4][0][1]) if nxt and nxt[4] else None))
    return lignes, cycles, acc


def proba(x, k=1.0, src="cl"):
    S = x["Scl"] if src == "cl" else x["Scb"]
    if S is None: return None
    sd = x["sig"] * k * math.sqrt(max(1.0, 260 - x["t"]))
    return PHI((S - x["K"]) / sd)


def ajuster_k(L):
    """maximum de vraisemblance de k (une photo par cycle, la plus proche de t = 10 s), exploration seulement"""
    par = {}
    for x in L:
        if abs(x["t"] - 10) < abs(par.get(x["st"], {"t": 99})["t"] - 10): par[x["st"]] = x
    X = list(par.values()); best = None
    for k in np.arange(0.5, 2.51, 0.05):
        ll = 0
        for x in X:
            p = min(1 - 1e-6, max(1e-6, proba(x, k))); ll += math.log(p if x["y"] else 1 - p)
        if best is None or ll > best[1]: best = (float(k), ll)
    return round(best[0], 2), len(X)


# ------------------------------------------------------------------ règles
def executer(L, regle, k, cycles_periode, pessimiste=False):
    """regle = (tmin, tmax, src, seuil) ; renvoie la liste des achats (un par cycle) et le vecteur P&L par cycle"""
    tmin, tmax, src, X = regle; achats = {}
    for x in L:
        if x["st"] in achats or not (tmin <= x["t"] < tmax): continue
        p = proba(x, k, src)
        if p is None: continue
        for up in (True, False):
            a = x["ua"] if up else x["da"]; z = x["uaz"] if up else x["daz"]
            if not (0.02 <= a <= 0.98) or z <= 0: continue
            if (p if up else 1 - p) - a - fee(a) >= X:
                if pessimiste:
                    n1 = x["ua1"] if up else x["da1"]
                    if not n1 or not (0.02 <= n1[0] <= 0.98) or n1[1] <= 0: achats[x["st"]] = None; break
                    a, z = n1
                q = min(MISE / a, z); gm = x["y"] == (1 if up else 0)
                achats[x["st"]] = dict(st=x["st"], t=x["t"], up=up, a=a, q=q, mise=q * a, gm=gm, pn=q * ((1 if gm else 0) - a - fee(a)),
                                       p=p if up else 1 - p)
                break
    achats = {k_: v for k_, v in achats.items() if v}
    vec = np.array([achats[s]["pn"] if s in achats else 0.0 for s in cycles_periode])
    return list(achats.values()), vec


def resume(A, vec, nreg, rng):
    if not A: return dict(achats=0)
    bs = vec[rng.integers(0, len(vec), (10000, len(vec)))].sum(1)
    lo, hi = 100 * 0.05 / nreg, 100 - 100 * 0.05 / nreg
    mise = sum(a["mise"] for a in A); pn = float(vec.sum())
    return dict(achats=len(A), gagnes=int(sum(a["gm"] for a in A)), prix=float(np.mean([a["a"] for a in A])),
                proba_modele=float(np.mean([a["p"] for a in A])), mise=float(mise), pnl=pn, roi=pn / mise if mise else None,
                part_up=float(np.mean([a["up"] for a in A])), taille_moy=float(np.mean([a["mise"] for a in A])),
                ic90=np.percentile(bs, [5, 95]).tolist(), ic_bonf=np.percentile(bs, [lo, hi]).tolist(), cycles=len(vec))


# RÈGLES FIGÉES (remplies après l'exploration, avant toute lecture de la validation) : (t min, t max, source du prix, avantage minimal net de frais)
# Exploration (405 cycles utilisables, 11–12.10) : k ajusté = 1,8 (le σ Chainlink 1 s du cycle précédent sous-estime le risque) ;
# avec k = 1,8 le carnet suit le modèle avec une pente ≈ 1,0 dès t = 0 et prédit au moins aussi bien (Brier carnet ≤ modèle) : pas de retard visible.
# Balayage de 168 combinaisons : la plupart négatives ; les trois retenues sont les meilleures plausibles, donc exposées au hasard (biais de sélection).
K_FIGE = 1.8
REGLES = {"R1 ouverture 0–5 s, Chainlink, avantage ≥ 0,06": (0, 5, "cl", 0.06),        # exploration : 121 achats, +4,2 %, +47 $
          "R2 5–15 s, Coinbase ajusté, avantage ≥ 0,08": (5, 15, "cb", 0.08),         # exploration : 94 achats, +10,1 %, +92 $
          "R3 15–30 s, Chainlink, avantage ≥ 0,10": (15, 30, "cl", 0.10)}             # exploration : 120 achats, +13,2 %, +155 $


def descriptif(L, k):
    out = {}
    # 1. avance au début : distance S − K ($) et en σ, à t ≈ 0 / 10 / 30 s (photo la plus proche, une par cycle)
    for t0 in (0, 10, 30):
        par = {}
        for x in L:
            if abs(x["t"] - t0) <= 1.0 and abs(x["t"] - t0) < abs(par.get(x["st"], {"t": 99})["t"] - t0): par[x["st"]] = x
        X = list(par.values())
        d = np.array([x["Scl"] - x["K"] for x in X]); z = np.array([(x["Scl"] - x["K"]) / (x["sig"] * k * math.sqrt(260 - x["t"])) for x in X])
        p = np.array([proba(x, k) for x in X]); mid = np.array([(x["ub"] + x["ua"]) / 2 for x in X]); y = np.array([x["y"] for x in X])
        pcb = np.array([proba(x, k, "cb") if x["Scb"] is not None else np.nan for x in X])
        sl = float(np.polyfit(p - 0.5, mid - 0.5, 1)[0]) if len(X) > 10 else None
        # régression du gagnant sur (modèle, carnet) : qui apporte l'information ?
        out[f"t{t0}"] = dict(n=len(X), d_q=np.percentile(d, [5, 25, 50, 75, 95]).round(2).tolist(), d_abs_moy=float(np.mean(np.abs(d))),
                             z_q=np.percentile(z, [5, 25, 50, 75, 95]).round(3).tolist(), z_abs_moy=float(np.mean(np.abs(z))),
                             part_p_hors_045_055=float(np.mean(np.abs(p - 0.5) > 0.05)), part_p_hors_040_060=float(np.mean(np.abs(p - 0.5) > 0.10)),
                             mid_moy_abs_ecart=float(np.mean(np.abs(mid - 0.5))), p_moy_abs_ecart=float(np.mean(np.abs(p - 0.5))),
                             pente_mid_sur_modele=sl, corr=float(np.corrcoef(p, mid)[0, 1]),
                             brier_modele=float(np.mean((p - y) ** 2)), brier_carnet=float(np.mean((mid - y) ** 2)), brier_05=0.25,
                             brier_cb=float(np.nanmean((pcb - y) ** 2)), freq_up=float(y.mean()),
                             age_cl_med=float(np.median([x["age_cl"] for x in X])),
                             k_connu_med=float(np.median([x["k_connu"] for x in X if x["k_connu"] is not None])) if any(x["k_connu"] is not None for x in X) else None)
    # 2. calibration : modèle contre milieu du carnet contre fréquence réelle, par tranche de probabilité modèle (t ∈ [5, 30), une photo / cycle / 5 s)
    cal = collections.defaultdict(list); vu = set()
    for x in L:
        if not (5 <= x["t"] < 30): continue
        key = (x["st"], int(x["t"] // 5))
        if key in vu: continue
        vu.add(key); p = proba(x, k); b = min(9, int(p * 10)); cal[b].append((p, (x["ub"] + x["ua"]) / 2, x["y"], x["st"]))
    out["calibration"] = [dict(tranche=f"{b / 10:.1f}–{(b + 1) / 10:.1f}", n=len(v), cycles=len({w[3] for w in v}), modele=float(np.mean([w[0] for w in v])),
                               carnet=float(np.mean([w[1] for w in v])), freq_up=float(np.mean([w[2] for w in v]))) for b, v in sorted(cal.items())]
    # 3. état du carnet seconde par seconde (0–30 s)
    et = collections.defaultdict(list)
    for x in L:
        s = int(x["t"])
        if s <= 30: et[s].append(x)
    out["carnet"] = [dict(t=s, n=len(v), ecart_med=float(np.median([x["ua"] - x["ub"] for x in v])),
                          part_ecart_1c=float(np.mean([x["ua"] - x["ub"] <= 0.0105 for x in v])),
                          taille_meilleur_vendeur_usd_med=float(np.median([x["uaz"] * x["ua"] for x in v])),
                          profondeur_5_niveaux_usd_med=float(np.median([x["uad"] for x in v])),
                          mid_abs_ecart_05=float(np.mean([abs((x["ub"] + x["ua"]) / 2 - 0.5) for x in v])),
                          p_abs_ecart_05=float(np.mean([abs(proba(x, k) - 0.5) for x in v])),
                          avantage_max_moy=float(np.mean([max(proba(x, k) - x["ua"], 1 - proba(x, k) - x["da"]) for x in v])))
                     for s, v in sorted(et.items())]
    return out


if __name__ == "__main__":
    if sys.argv[1] == "--extraire":
        from multiprocessing import Pool
        fs = sorted(glob.glob(os.path.join(sys.argv[2], "*", "*.json.gz")))
        with Pool(2) as P: out = [x for x in P.imap(extraire_un, fs, chunksize=4) if x]
        json.dump(out, gzip.open(sys.argv[3], "wt")); print(len(out)); sys.exit()
    VALID = "--validation" in sys.argv
    L, CYC, acc = preparer(sys.argv[1]); rng = np.random.default_rng(1090)
    part = "validation" if VALID else "exploration"
    LP = [x for x in L if x["part"] == part]
    cyc = sorted({x["st"] for x in LP})
    res = dict(periode=part, cycles=len(cyc), cycles_totaux_periode=sum(1 for v in CYC.values() if v["part"] == part),
               accord_gagnant_officiel_vs_cycle_suivant=acc)
    if not VALID:
        k, n = ajuster_k(LP); res["k_ajuste"] = k; res["k_n"] = n
        res["descriptif_k1"] = descriptif(LP, 1.0); res["descriptif_kfit"] = descriptif(LP, k)
        # balayage d'exploration
        sc = []
        for src in ("cl", "cb"):
            for kk in (1.0, k):
                for (a, b) in ((0, 5), (2, 10), (5, 15), (5, 30), (10, 30), (15, 30)):
                    for X in (0.0, 0.02, 0.04, 0.06, 0.08, 0.10, 0.15):
                        A, v = executer(LP, (a, b, src, X), kk, cyc)
                        r = resume(A, v, 3, rng); r.update(src=src, k=kk, tmin=a, tmax=b, seuil=X)
                        Ap, vp = executer(LP, (a, b, src, X), kk, cyc, pessimiste=True)
                        r["pnl_pess"] = float(vp.sum()); r["achats_pess"] = len(Ap)
                        sc.append(r)
        res["balayage"] = sc
    else:
        assert REGLES and K_FIGE, "règles non figées"
        res["k_fige"] = K_FIGE; res["descriptif"] = descriptif(LP, K_FIGE); res["regles"] = {}
        for nom, rg in REGLES.items():
            A, v = executer(LP, rg, K_FIGE, cyc); Ap, vp = executer(LP, rg, K_FIGE, cyc, pessimiste=True)
            r = resume(A, v, len(REGLES), rng); r["pessimiste"] = resume(Ap, vp, len(REGLES), rng)
            for jour, (d0, d1) in (("13.10", (J13, J13 + 86400)), ("14.10", (J13 + 86400, J15))):
                cj = [s for s in cyc if d0 <= s < d1]; Aj = [a for a in A if d0 <= a["st"] < d1]
                r[jour] = resume(Aj, np.array([sum(a["pn"] for a in Aj if a["st"] == s) for s in cj]), len(REGLES), rng)
            res["regles"][nom] = r
    s = json.dumps(res, ensure_ascii=False, indent=1, default=str)
    open(os.path.join(ICI, f"ouverture_cycle_h1090_{part}.json"), "w").write(s)
    print(s[:3000])
