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

    # flux perp signe sur k secondes (pour confirmer un retournement)
    def flux_perp(t, k, d):
        b_ = somme(PE, t - k + 1, t, 1); s_ = somme(PE, t - k + 1, t, 2)
        return d * (b_ - s_) / (b_ + s_) if b_ + s_ > 0 else 0

    def sim(m, v):
        cache = m.setdefault("cache", {}); A = None; invB = [0.0, 0.0]; pnl = 0.0; etat = "rien"; dern = {True: 0.5, False: 0.5}; sous = 0
        for (ts, up, p, size, side) in m["tr"]:
            if ts < m["start"] or ts > m["end"] - 1: continue
            dern[up] = p; dern[not up] = 1 - p
            pu = proba_up(m, ts - L, cache)
            if pu is None: continue
            if A is None:
                if ts - m["start"] < v.get("entree_min_s", 0): continue
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
                offre = min(math.floor(((1 - fairA) - v.get("marge_offre", 0.08)) * 100) / 100, v.get("offre_max", 0.43))
                if offre >= 0.02 and q <= offre - 0.01 + 1e-9:
                    k = min(size, A["q"] - invB[0]); invB[0] += k; invB[1] += k * offre
            if invB[0] >= A["q"] - 1e-9:
                pnl += A["q"] * (1 - A["prix"]) - invB[1]; etat = "paire"; A["fini"] = True; break
            # --- regle de stop
            st = v.get("stop")
            declenche = False
            if st is not None and ts - A["ts"] >= v.get("protection_s", 0):
                if v.get("type") == "prix": cond = dern[c] <= A["prix"] - st
                else: cond = fairA < A["fair0"] - st
                if cond and v.get("confirm_flux") is not None and flux_perp(ts - L, 10, 1 if c else -1) > v["confirm_flux"]: cond = False
                sous = sous + 1 if cond else 0
                declenche = cond and sous >= v.get("persiste", 1)
            if declenche:
                pv = max(0.01, dern[c] - 0.01); qa = A["q"] - invB[0]
                pnl += qa * (pv - FEE(pv)) - qa * A["prix"] + invB[0] * (1 - A["prix"]) - invB[1]
                etat = "stop"; A["fini"] = True; A["stop_aurait"] = (A["cote"] == m["up_gagne"]); break
            if up == c and p >= v.get("tp", 0.90) and invB[0] < 1e-9:
                tp = v.get("tp", 0.90); pnl += A["q"] * (tp - FEE(tp) - A["prix"]); etat = "sortie"; A["fini"] = True; break
        if A is None: return None
        if not A.get("fini"):
            g = A["cote"] == m["up_gagne"]; qa = A["q"] - invB[0]
            pnl += qa * ((1 if g else 0) - A["prix"]) + invB[0] * (1 - A["prix"]) - invB[1]
            etat = "fin " + ("gagnee" if g else "perdue")
        return pnl, etat, A.get("stop_aurait")

    variantes = [
        ("Reference : stop proba -15 pts", {"stop": 0.15}),
        ("Aucun stop (garder jusqu'a 0,90 ou la fin)", {"stop": None}),
        ("Stop proba -10 pts", {"stop": 0.10}),
        ("Stop proba -20 pts", {"stop": 0.20}),
        ("Stop proba -25 pts", {"stop": 0.25}),
        ("Stop proba -30 pts", {"stop": 0.30}),
        ("Stop -15 pts confirme 3 s", {"stop": 0.15, "persiste": 3}),
        ("Stop -15 pts confirme 5 s", {"stop": 0.15, "persiste": 5}),
        ("Stop -15 pts seulement si le perp vend (flux 10 s < 0)", {"stop": 0.15, "confirm_flux": 0.0}),
        ("Stop -15 pts seulement si le perp vend fort (flux 10 s < -0,3)", {"stop": 0.15, "confirm_flux": -0.3}),
        ("Stop -20 pts confirme 3 s", {"stop": 0.20, "persiste": 3}),
        ("Stop -20 pts si le perp vend", {"stop": 0.20, "confirm_flux": 0.0}),
        ("Pas de stop pendant 10 s apres l'entree, puis -15 pts", {"stop": 0.15, "protection_s": 10}),
        ("Pas de stop pendant 20 s apres l'entree, puis -15 pts", {"stop": 0.15, "protection_s": 20}),
        ("Stop sur le prix : 0,55 -> 0,40", {"stop": 0.15, "type": "prix"}),
        ("Stop sur le prix : 0,55 -> 0,35", {"stop": 0.20, "type": "prix"}),
        ("Stop -15 pts + entree apres 30 s de cycle", {"stop": 0.15, "entree_min_s": 30}),
        ("Stop -15 pts + entree apres 60 s de cycle", {"stop": 0.15, "entree_min_s": 60}),
        ("Stop -15 pts + offre opposee plus genereuse (marge 0,05, max 0,45)", {"stop": 0.15, "marge_offre": 0.05, "offre_max": 0.45}),
        ("Stop -15 pts + sortie a 0,85", {"stop": 0.15, "tp": 0.85}),
        ("Stop -15 pts + sortie a 0,95", {"stop": 0.15, "tp": 0.95}),
    ]
    rap = [f"\n## {prefixe.upper()} — variantes de sortie ({len(M)} cycles, {JOURS} jours, 100 parts, retard 1 s)\n",
           "| Variante | Trades | Gain net | Gain/jour | Pertes totales | Stops | Stops qui auraient gagne | Pire baisse |", "|---|---|---|---|---|---|---|---|"]
    for nom, v in variantes:
        R = [x for x in (sim(m, v) for m in M) if x]
        cum = pic = dd = 0
        for p_, _, _ in R:
            cum += p_; pic = max(pic, cum); dd = max(dd, pic - cum)
        stops = [x for x in R if x[1] == "stop"]
        aur = sum(1 for x in stops if x[2])
        rap.append(f"| {nom} | {len(R)} | {sum(x[0] for x in R):+.0f} $ | {sum(x[0] for x in R) / JOURS:+.0f} $ | {sum(x[0] for x in R if x[0] < 0):+.0f} $ | {len(stops)} | {aur} ({100 * aur / max(1, len(stops)):.0f} %) | -{dd:.0f} $ |")
        print(rap[-1]); sys.stdout.flush()
    return rap


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
    rap = [f"# Variantes de sortie de V1 (reglage A, retard 1 s) — {JOURS} jours ({jours[0]} -> {jours[-1]})"]
    for prefixe, sym, autre in (("btc", "BTCUSDT", "ETHUSDT"), ("eth", "ETHUSDT", "BTCUSDT")):
        rap += etudier(prefixe, sym, autre, jours, debut, fin)
        open(OUT + "resultat_sorties.md", "w").write("\n".join(rap))
    rap.append(f"\nDuree : {time.time() - t0:.0f} s")
    open(OUT + "resultat_sorties.md", "w").write("\n".join(rap))
    print("\n".join(rap))


if __name__ == "__main__":
    main()
