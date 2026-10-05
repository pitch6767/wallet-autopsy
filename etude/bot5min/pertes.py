"""Autopsie des pertes de V1 (reglage A) — BTC et ETH, 12 jours.
Pour chaque trade : tous les signaux disponibles AVANT l'entree (retard de reaction 1 s), puis recherche de ce qui annonce une perte.
Sources historiques : Binance spot 1 s (prix, volume, achats agressifs, nombre d'echanges), Binance perp (tous les echanges),
echanges Polymarket du marche, autre crypto. (Liquidations et retraits d'ordres du carnet : pas d'historique public -> enregistres en direct.)
"""
import sys, io, json, math, time, zipfile, statistics, csv
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
sys.path.insert(0, "etude/bot5min")
import test as T
import paires as P
import solutions as S

JOURS = int(sys.argv[1]) if len(sys.argv) > 1 else 12
L = 1
N = 100.0
FEE = lambda p: T.FEE_RATE * p * (1 - p)
OUT = "etude/bot5min/"


# ------------------------------------------------------------- donnees Binance
def spot_jour(sym, jour):
    url = f"https://data.binance.vision/data/spot/daily/klines/{sym}/1s/{sym}-1s-{jour}.zip"
    z = zipfile.ZipFile(io.BytesIO(T.get(url, raw=True)))
    out = {}
    for ligne in z.read(z.namelist()[0]).decode().splitlines():
        c = ligne.split(",")
        if not c[0].isdigit(): continue
        t = int(c[0]); t = t // 1000 if t > 1e14 else t
        out[t // 1000] = (float(c[4]), float(c[5]), float(c[9]), int(c[8]))   # close, volume, achats agressifs, nb echanges
    return out


def perp_jour(sym, jour):
    import pandas as pd
    url = f"https://data.binance.vision/data/futures/um/daily/aggTrades/{sym}/{sym}-aggTrades-{jour}.zip"
    try:
        z = zipfile.ZipFile(io.BytesIO(T.get(url, raw=True)))
    except Exception as e:
        print("perp absent", sym, jour, str(e)[:60]); return {}
    nom = z.namelist()[0]
    with z.open(nom) as fh:
        tete = fh.readline().decode()
    entete = 0 if not tete.split(",")[0].strip().isdigit() else None
    with z.open(nom) as fh:
        df = pd.read_csv(fh, header=entete, usecols=[1, 2, 5, 6], names=None if entete == 0 else ["a", "price", "qty", "f", "l", "tt", "bm"][:7])
    df.columns = ["price", "qty", "tt", "bm"]
    tt = df["tt"].astype("int64")
    df["s"] = (tt // 1000000) if tt.iloc[0] > 1e14 else (tt // 1000)
    bm = df["bm"].astype(str).str.lower().eq("true")
    usd = df["price"] * df["qty"]
    df["b"] = usd.where(~bm, 0.0); df["v"] = usd.where(bm, 0.0)
    g = df.groupby("s").agg(p=("price", "last"), b=("b", "sum"), v=("v", "sum"), n=("price", "size"), mb=("b", "max"), mv=("v", "max"))
    return {int(i): [r.p, r.b, r.v, int(r.n), r.mb, r.mv] for i, r in zip(g.index, g.itertuples(index=False))}


def charger(fn, sym, jours):
    d = {}
    with ThreadPoolExecutor(3) as ex:
        for x in ex.map(lambda j: fn(sym, j), jours): d.update(x)
    return d


def dernier(d, t, k=0, maxback=6):
    for i in range(maxback):
        o = d.get(t - i)
        if o is not None: return o[k]
    return None


def somme(d, a, b, k):
    return sum(d[s][k] for s in range(a, b + 1) if s in d)


# ------------------------------------------------------------- etude d'un actif
def etudier(prefixe, sym, autre_sym, jours, debut, fin):
    t0 = time.time()
    SP = charger(spot_jour, sym, jours)
    SPx = {s: (v[0], v[0]) for s, v in SP.items()}     # format attendu par T.prix / T.sigma_s (ouverture, cloture)
    PE = charger(perp_jour, sym, jours)
    AU = charger(spot_jour, autre_sym, jours)
    print(prefixe, "binance charge", len(SP), len(PE), "(%.0fs)" % (time.time() - t0)); sys.stdout.flush()
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

    def proba_up(m, ts, cache):
        if ts in cache: return cache[ts]
        r = None; P0 = prix(ts); sgk = ts // 15
        if ("sg", sgk) not in cache: cache[("sg", sgk)] = T.sigma_s(SPx, ts)
        sg = cache[("sg", sgk)]
        if P0 and sg and m["sd_b"]:
            a = m["end"] - 59
            if ts >= a:
                connus = [x for x in (prix(s) for s in range(a, ts + 1)) if x]
                nr = m["end"] - ts
                E = (sum(connus) + nr * P0) / (len(connus) + nr); var = (sg * P0) ** 2 * nr ** 3 / 3 / 3600
            else:
                E = P0; var = (sg * P0) ** 2 * ((a - ts) + 20)
            r = T.phi((E - m["K"]) / math.sqrt(var + m["sd_b"] ** 2))
        cache[ts] = r
        return r

    lignes = []
    for m in M:
        cache = {}; A = None; invB = [0.0, 0.0]; pnl = 0.0; etat = "rien"; dern = {True: 0.5, False: 0.5}
        for (ts, up, p, size, side) in m["tr"]:
            if ts < m["start"] or ts > m["end"] - 1: continue
            dern[up] = p; dern[not up] = 1 - p
            pu = proba_up(m, ts - L, cache)
            if pu is None: continue
            if A is None:
                if side == "BUY" and 0.55 <= p <= 0.56:
                    fair = pu if up else 1 - pu
                    if fair >= 0.63:
                        a0, b0 = prix(ts - L - 5), prix(ts - L)
                        if not (a0 and b0 and ((b0 - a0) * (1 if up else -1)) > 0): continue
                        A = {"cote": up, "prix": p, "q": N, "fair0": fair, "ts": ts}; pnl -= N * FEE(p); etat = "jambe"
                continue
            if A.get("fini"): break
            c = A["cote"]; fairA = pu if c else 1 - pu
            if side == "SELL": O, q = up, p
            elif side == "BUY": O, q = (not up), 1 - p
            else: O = None
            if O is not None and O != c and invB[0] < A["q"]:
                offre = min(math.floor(((1 - fairA) - 0.08) * 100) / 100, 0.43)
                if offre >= 0.02 and q <= offre - 0.01 + 1e-9:
                    k = min(size, A["q"] - invB[0]); invB[0] += k; invB[1] += k * offre
            if invB[0] >= A["q"] - 1e-9:
                pnl += A["q"] * (1 - A["prix"]) - invB[1]; etat = "paire"; A["fini"] = True; break
            if fairA < A["fair0"] - 0.15:
                pv = max(0.01, dern[c] - 0.01); qa = A["q"] - invB[0]
                pnl += qa * (pv - FEE(pv)) - qa * A["prix"] + invB[0] * (1 - A["prix"]) - invB[1]
                etat = "stop"; A["fini"] = True; A["ts_fin"] = ts; break
            if up == c and p >= 0.90 and invB[0] < 1e-9:
                pnl += A["q"] * (0.90 - FEE(0.90) - A["prix"]); etat = "sortie90"; A["fini"] = True; break
        if A is None: continue
        if not A.get("fini"):
            g = A["cote"] == m["up_gagne"]; qa = A["q"] - invB[0]
            pnl += qa * ((1 if g else 0) - A["prix"]) + invB[0] * (1 - A["prix"]) - invB[1]
            etat = "fin " + ("gagnee" if g else "perdue")
        # ---------------- signaux AVANT l'entree (te = instant de decision)
        te = A["ts"] - L; d = 1 if A["cote"] else -1
        f = {"actif": prefixe, "start": m["start"], "te": te, "pnl": round(pnl, 2), "issue": etat, "perte": int(pnl < 0)}
        def ret(k, src=prix):
            a, b = src(te - k), src(te)
            return d * math.log(b / a) * 1e4 if a and b else None     # en points de base
        for k in (2, 5, 10, 15, 30, 60, 120): f[f"spot_r{k}"] = ret(k)
        r5p = ret(5); a5 = prix(te - 10); b5 = prix(te - 5)
        f["spot_accel"] = (r5p - d * math.log(b5 / a5) * 1e4) if (r5p is not None and a5 and b5) else None
        rr = [math.log(prix(s) / prix(s - 1)) for s in range(te - 299, te + 1) if prix(s) and prix(s - 1)]
        f["vol60_vs300"] = (statistics.pstdev(rr[-60:]) / statistics.pstdev(rr)) if len(rr) > 100 and statistics.pstdev(rr) > 0 else None
        f["vol300_bp"] = statistics.pstdev(rr) * 1e4 if len(rr) > 100 else None
        for k in (10, 30, 60):
            v = somme(SP, te - k + 1, te, 1); tb = somme(SP, te - k + 1, te, 2)
            f[f"spot_flux{k}"] = d * (2 * tb / v - 1) if v > 0 else None
        v30 = somme(SP, te - 29, te, 1); v300 = somme(SP, te - 299, te, 1)
        f["spot_volume_pic30"] = (v30 / (v300 / 10)) if v300 > 0 else None
        n30 = somme(SP, te - 29, te, 3); n300 = somme(SP, te - 299, te, 3)
        f["spot_echanges_pic30"] = (n30 / (n300 / 10)) if n300 > 0 else None
        pp = lambda t: dernier(PE, t, 0)
        for k in (2, 5, 15, 30): f[f"perp_r{k}"] = ret(k, pp)
        f["perp_avance5"] = (f["perp_r5"] - f["spot_r5"]) if f["perp_r5"] is not None and f["spot_r5"] is not None else None
        f["perp_avance2"] = (f["perp_r2"] - f["spot_r2"]) if f["perp_r2"] is not None and f["spot_r2"] is not None else None
        bs = lambda t: ((pp(t) - prix(t)) / prix(t) * 1e4) if pp(t) and prix(t) else None
        f["base_bp"] = bs(te)
        f["base_var30"] = d * (bs(te) - bs(te - 30)) if bs(te) is not None and bs(te - 30) is not None else None
        for k in (5, 10, 30, 60):
            b_ = somme(PE, te - k + 1, te, 1); s_ = somme(PE, te - k + 1, te, 2)
            f[f"perp_flux{k}"] = d * (b_ - s_) / (b_ + s_) if b_ + s_ > 0 else None
        pv30 = somme(PE, te - 29, te, 1) + somme(PE, te - 29, te, 2); pv300 = somme(PE, te - 299, te, 1) + somme(PE, te - 299, te, 2)
        f["perp_volume_pic30"] = (pv30 / (pv300 / 10)) if pv300 > 0 else None
        gros_pour = max([PE[s][4 if d > 0 else 5] for s in range(te - 59, te + 1) if s in PE] or [0])
        gros_contre = max([PE[s][5 if d > 0 else 4] for s in range(te - 59, te + 1) if s in PE] or [0])
        f["perp_gros_contre60_k$"] = gros_contre / 1000
        f["perp_gros_ratio60"] = (gros_contre / gros_pour) if gros_pour > 0 else None
        ap = lambda t: dernier(AU, t, 0)
        for k in (15, 60): f[f"autre_r{k}"] = ret(k, ap)
        # Polymarket : echanges du marche avant l'entree
        avant = [x for x in m["tr"] if m["start"] <= x[0] <= te]
        def notre_prix(x): return x[2] if x[1] == A["cote"] else 1 - x[2]
        f["pm_n30"] = sum(1 for x in avant if x[0] > te - 30)
        flux = 0.0; gros_c = 0.0
        for x in avant:
            if x[0] <= te - 30: continue
            usd = x[2] * x[3]
            pour = (x[4] == "BUY") == (x[1] == A["cote"])          # achat de notre jambe ou vente de l'autre
            flux += usd if pour else -usd
            if not pour: gros_c = max(gros_c, usd)
        f["pm_flux30_$"] = flux; f["pm_gros_contre30_$"] = gros_c
        p30 = [notre_prix(x) for x in avant if te - 35 <= x[0] <= te - 25]
        f["pm_vitesse30"] = (A["prix"] - p30[-1]) if p30 else None
        prem = next((x[0] for x in avant if notre_prix(x) >= 0.55), None)
        f["pm_depuis_055_s"] = (te - prem) if prem else None
        f["pm_prix_entree"] = A["prix"]; f["proba_entree"] = round(A["fair0"], 4)
        f["temps_ecoule_s"] = te - m["start"]; f["temps_restant_s"] = m["end"] - te
        K = m["K"]; Pt = prix(te)
        f["distance_bp"] = d * (Pt - K) / K * 1e4 if Pt else None
        f["heure_utc"] = datetime.fromtimestamp(te, timezone.utc).hour
        f["weekend"] = int(datetime.fromtimestamp(te, timezone.utc).weekday() >= 5)
        f["cycle_r"] = d * math.log(Pt / prix(m["start"])) * 1e4 if Pt and prix(m["start"]) else None
        lignes.append(f)
    print(prefixe, "trades", len(lignes), "(%.0fs)" % (time.time() - t0)); sys.stdout.flush()
    return lignes


def analyse(R, titre):
    rap = [f"\n## {titre} — {len(R)} trades, {sum(r['perte'] for r in R)} perdants, net {sum(r['pnl'] for r in R):+.0f} $ (100 parts)\n"]
    rap.append("Issues : " + ", ".join(f"{k} {sum(1 for r in R if r['issue'] == k)} ({sum(r['pnl'] for r in R if r['issue'] == k):+.0f} $)" for k in sorted({r['issue'] for r in R})))
    feats = [k for k in R[0] if k not in ("actif", "start", "te", "pnl", "issue", "perte")]
    base_net = sum(r["pnl"] for r in R); base_pertes = sum(r["pnl"] for r in R if r["pnl"] < 0)
    # 1. signal par signal : perdants vs gagnants
    rap += ["\n### Ce qui distingue les perdants (medianes)\n", "| Signal | Gagnants | Perdants | Ecart (en ecarts-types) |", "|---|---|---|---|"]
    ecarts = []
    for k in feats:
        g = [r[k] for r in R if r[k] is not None and not r["perte"]]; p = [r[k] for r in R if r[k] is not None and r["perte"]]
        if len(g) < 20 or len(p) < 10: continue
        sd = statistics.pstdev(g + p) or 1
        ecarts.append((abs(statistics.median(p) - statistics.median(g)) / sd, k, statistics.median(g), statistics.median(p)))
    for e, k, mg, mp in sorted(ecarts, reverse=True)[:25]:
        rap.append(f"| {k} | {mg:.3g} | {mp:.3g} | {e:.2f} |")
    # 2. filtres simples : on refuse le trade si signal du mauvais cote d'un seuil ; choix du seuil sur les 2/3 premiers jours, verification sur le dernier tiers
    R = sorted(R, key=lambda r: r["te"]); cut = R[int(len(R) * 0.66)]["te"]
    A_, B_ = [r for r in R if r["te"] < cut], [r for r in R if r["te"] >= cut]
    res = []
    for k in feats:
        vals = sorted(r[k] for r in A_ if r[k] is not None)
        if len(vals) < 50: continue
        for q in (0.05, 0.1, 0.15, 0.2, 0.3):
            for sens in ("bas", "haut"):
                th = vals[int(len(vals) * q)] if sens == "bas" else vals[int(len(vals) * (1 - q)) - 1]
                refuse = (lambda r, th=th, sens=sens: r[k] is not None and (r[k] < th if sens == "bas" else r[k] > th))
                gA = sum(r["pnl"] for r in A_ if not refuse(r)) - sum(r["pnl"] for r in A_)
                gB = sum(r["pnl"] for r in B_ if not refuse(r)) - sum(r["pnl"] for r in B_)
                pB = sum(r["pnl"] for r in B_ if not refuse(r) and r["pnl"] < 0) - sum(r["pnl"] for r in B_ if r["pnl"] < 0)
                nB = sum(1 for r in B_ if refuse(r))
                res.append((gA, gB, pB, nB, k, sens, th, q))
    rap += ["\n### Meilleurs filtres (seuil choisi sur la periode 1, VERIFIE sur la periode 2 jamais vue)\n",
            "| Refuser si | Seuil | Gain net periode 1 | **Gain net periode 2** | Pertes evitees periode 2 | Trades refuses periode 2 |", "|---|---|---|---|---|---|"]
    for gA, gB, pB, nB, k, sens, th, q in sorted([x for x in res if x[0] > 0], key=lambda x: -x[0])[:20]:
        rap.append(f"| {k} {'<' if sens == 'bas' else '>'} | {th:.3g} | {gA:+.0f} $ | **{gB:+.0f} $** | {pB:+.0f} $ | {nB} / {len(B_)} |")
    # 3. modele combine (arbre de decision boosté), appris periode 1, teste periode 2
    try:
        from sklearn.ensemble import GradientBoostingClassifier
        X = lambda S_: [[(r[k] if r[k] is not None else -999) for k in feats] for r in S_]
        clf = GradientBoostingClassifier(n_estimators=150, max_depth=3, learning_rate=0.05, subsample=0.8, random_state=1)
        clf.fit(X(A_), [r["perte"] for r in A_])
        pr = clf.predict_proba(X(B_))[:, 1]
        rap += ["\n### Modele combine (appris periode 1, teste periode 2)\n", "| Refuser si risque de perte > | Trades refuses | Gain net periode 2 (avant -> apres) | Pertes periode 2 (avant -> apres) |", "|---|---|---|---|"]
        avant_g = sum(r["pnl"] for r in B_); avant_p = sum(r["pnl"] for r in B_ if r["pnl"] < 0)
        for th in (0.5, 0.6, 0.7, 0.8):
            garde = [r for r, x in zip(B_, pr) if x <= th]
            rap.append(f"| {th:.1f} | {len(B_) - len(garde)} / {len(B_)} | {avant_g:+.0f} -> {sum(r['pnl'] for r in garde):+.0f} $ | {avant_p:+.0f} -> {sum(r['pnl'] for r in garde if r['pnl'] < 0):+.0f} $ |")
        imp = sorted(zip(clf.feature_importances_, feats), reverse=True)[:12]
        rap.append("\nSignaux les plus utiles au modele : " + ", ".join(f"{k} ({v:.2f})" for v, k in imp))
    except Exception as e:
        rap.append(f"\n(modele non calcule : {e})")
    return rap


def main():
    t0 = time.time()
    fin = int(time.time()) // 300 * 300 - 900
    debut = fin - JOURS * 86400
    jours = sorted({datetime.fromtimestamp(t, timezone.utc).strftime("%Y-%m-%d") for t in range(debut - 600, fin + 600, 3600)})
    jours = [j for j in jours if j < datetime.now(timezone.utc).strftime("%Y-%m-%d")]
    fin = min(fin, int(datetime.strptime(jours[-1], "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp()) + 86400 - 300)
    tout = []
    rap = [f"# Autopsie des pertes de V1 (reglage A, retard 1 s) — {JOURS} jours ({jours[0]} -> {jours[-1]})"]
    for prefixe, sym, autre in (("btc", "BTCUSDT", "ETHUSDT"), ("eth", "ETHUSDT", "BTCUSDT")):
        R = etudier(prefixe, sym, autre, jours, debut, fin)
        tout += R
        with open(OUT + "pertes_trades.csv", "w", newline="") as fh:
            w = csv.DictWriter(fh, list(tout[0].keys())); w.writeheader(); [w.writerow(r) for r in tout]
        rap += analyse(R, prefixe.upper())
        open(OUT + "resultat_pertes.md", "w").write("\n".join(rap))
    rap.append(f"\nDuree : {time.time() - t0:.0f} s")
    open(OUT + "resultat_pertes.md", "w").write("\n".join(rap))
    print("\n".join(rap))


if __name__ == "__main__":
    main()
