"""Analyse profonde : notre modele contre le marche Polymarket — BTC et ETH, 12 jours, seconde par seconde.
1. Qui predit le mieux le resultat (erreur log), selon le temps restant ; combinaison des deux (apprise jours 1-8, jugee 9-12).
2. Calibration : quand le marche affiche X, combien de fois ca gagne vraiment (le marche est-il trop sur de lui ?).
3. Qui mene : correlation des variations seconde par seconde avec decalage (modele en avance ou en retard sur le marche).
4. Desaccords : quand modele et marche divergent, qui a raison, combien de temps ca dure, et gain realiste
   (achat au prix d'un vrai acheteur dans les 2 s, frais compris, garde jusqu'a la fin).
"""
import sys, math, time, statistics, collections
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
sys.path.insert(0, "etude/bot5min")
import test as T
import paires as P
import solutions as S
from sorties import spot_jour, charger, dernier

JOURS = int(sys.argv[1]) if len(sys.argv) > 1 else 12
FEE = lambda p: T.FEE_RATE * p * (1 - p)
OUT = "etude/bot5min/"
TB = [(0, 30), (30, 60), (60, 120), (120, 180), (180, 240), (240, 300)]      # temps restant (s)


def logit(x): x = min(max(x, 1e-4), 1 - 1e-4); return math.log(x / (1 - x))


def etudier(prefixe, sym, jours, debut, fin, coupe):
    t0 = time.time()
    SP = charger(spot_jour, sym, jours)
    SPx = {s: (v[0], v[0]) for s, v in SP.items()}
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
        r = None; P0 = prix(ts); sgk = ("sg", ts // 15)
        if sgk not in cache: cache[sgk] = T.sigma_s(SPx, ts)
        sg = cache[sgk]
        if P0 and sg and m["sd_b"]:
            a = m["end"] - 59
            if ts >= a:
                ck = ("cn", ts)
                connus = [x for x in (prix(s) for s in range(a, ts + 1)) if x]
                nr = m["end"] - ts
                E = (sum(connus) + nr * P0) / (len(connus) + nr); var = (sg * P0) ** 2 * nr ** 3 / 3 / 3600
            else:
                E = P0; var = (sg * P0) ** 2 * ((a - ts) + 20)
            r = T.phi((E - m["K"]) / math.sqrt(var + m["sd_b"] ** 2))
        cache[ts] = r
        return r

    # ---- series par seconde : prix marche (Up), fraicheur, plus bas prix paye par un acheteur Up / Down, modele
    lignes = []          # (start, k, tleft, marche, modele, gagne_up, jour_test)
    dis = []             # desaccords
    lead = collections.defaultdict(list)
    for m in M:
        up = np.full(300, np.nan); vu = np.full(300, -99); bu = np.full(302, np.inf); bd = np.full(302, np.inf)
        for (ts, u, p, size, side) in m["tr"]:
            k = ts - m["start"]
            if 0 <= k < 300: up[k] = p if u else 1 - p; vu[k] = k
            if 0 <= k < 302 and side == "BUY":
                if u: bu[k] = min(bu[k], p)
                else: bd[k] = min(bd[k], p)
        for k in range(1, 300):
            if np.isnan(up[k]): up[k] = up[k - 1]; vu[k] = vu[k - 1]
        cache = {}
        pm = np.array([proba_up(m, m["start"] + k, cache) or np.nan for k in range(300)])
        g = 1 if m["up_gagne"] else 0
        test = m["start"] >= coupe
        for k in range(5, 296):
            if vu[k] < k - 3 or np.isnan(up[k]) or np.isnan(pm[k]): continue
            lignes.append((m["start"], k, 300 - k, up[k], pm[k], g, test))
        # avance / retard : variations par seconde (logit), decalage d (d>0 : le modele bouge AVANT le marche)
        ok = [k for k in range(6, 295) if vu[k] >= k - 1 and not np.isnan(pm[k]) and not np.isnan(pm[k - 1]) and not np.isnan(up[k - 1])]
        dm = {k: logit(up[k]) - logit(up[k - 1]) for k in ok}
        dp = {k: logit(pm[k]) - logit(pm[k - 1]) for k in range(1, 300) if not np.isnan(pm[k]) and not np.isnan(pm[k - 1])}
        for d in range(-5, 6):
            for k in ok:
                if (k - d) in dp: lead[d].append((dm[k], dp[k - d]))
        # desaccords : premier instant de chaque episode ou |modele - marche| >= seuil
        for seuil in (0.05, 0.10, 0.15, 0.20):
            k = 5
            while k < 290:
                if vu[k] < k - 3 or np.isnan(pm[k]) or np.isnan(up[k]): k += 1; continue
                ecart = pm[k] - up[k]
                if abs(ecart) < seuil: k += 1; continue
                # duree de l'episode (le marche rattrape-t-il le modele ou l'inverse ?)
                j = k
                while j < 295 and not np.isnan(pm[j]) and abs(pm[j] - up[j]) >= seuil / 2: j += 1
                cote_modele = ecart > 0                   # True : le modele trouve Up sous-evalue
                # achat realiste du cote du modele : un vrai acheteur a paye <= prix marche + 1 cent dans les 2 s (signal vu a k, ordre a k+1)
                X = bu if cote_modele else bd
                prix_m = (up[k] if cote_modele else 1 - up[k]) + 0.01
                f_ = min(X[k + 1], X[k + 2])
                execu = f_ <= prix_m + 1e-9
                gagne_modele = (g == 1) == cote_modele
                pa = f_ if execu else prix_m
                Y = bd if cote_modele else bu         # cote du marche (contraire)
                prix_c = (1 - up[k] if cote_modele else up[k]) + 0.01
                fc = min(Y[k + 1], Y[k + 2]); execc = fc <= prix_c + 1e-9
                dis.append({"seuil": seuil, "tleft": 300 - k, "duree": int(j - k), "gagne_modele": float(gagne_modele), "execu": bool(execu),
                            "pnl_modele": float((1 if gagne_modele else 0) - pa - FEE(pa)), "pa": pa, "execc": bool(execc),
                            "pnl_marche": float((0 if gagne_modele else 1) - fc - FEE(fc)) if execc else None,
                            "test": test, "marche_cote": float(up[k] if cote_modele else 1 - up[k]), "modele_cote": float(pm[k] if cote_modele else 1 - pm[k])})
                k = j + 1
    print(prefixe, "lignes", len(lignes), "desaccords", len(dis), "(%.0fs)" % (time.time() - t0)); sys.stdout.flush()

    rap = [f"\n## {prefixe.upper()} — {len(M)} cycles, {len(lignes)} secondes observees\n"]
    L = np.array([(tl, mk, mo, g, te) for (_, _, tl, mk, mo, g, te) in lignes], dtype=float)
    TL, MK, MO, G, TE = L[:, 0], np.clip(L[:, 1], 0.005, 0.995), np.clip(L[:, 2], 0.005, 0.995), L[:, 3], L[:, 4] > 0.5
    ll = lambda p, y: float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))
    # 1. qui predit le mieux
    from sklearn.linear_model import LogisticRegression
    rap += ["### 1. Qui predit le mieux le resultat ? (erreur log : plus bas = meilleur ; jours 9-12 jamais vus pour la combinaison)\n",
            "| Temps restant | Secondes | Erreur marche | Erreur notre modele | Erreur combinaison (jours 9-12) | Poids marche / modele dans la combinaison |", "|---|---|---|---|---|---|"]
    for (a_, b_) in TB:
        sel = (TL > a_) & (TL <= b_)
        if sel.sum() < 500: continue
        Xa = np.c_[np.vectorize(logit)(MK[sel & ~TE]), np.vectorize(logit)(MO[sel & ~TE])]; ya = G[sel & ~TE]
        Xb = np.c_[np.vectorize(logit)(MK[sel & TE]), np.vectorize(logit)(MO[sel & TE])]; yb = G[sel & TE]
        lr = LogisticRegression(C=10).fit(Xa, ya); pb = lr.predict_proba(Xb)[:, 1]
        rap.append(f"| {a_}-{b_} s | {int(sel.sum())} | {ll(MK[sel & TE], yb):.4f} | {ll(MO[sel & TE], yb):.4f} | {ll(pb, yb):.4f} | {lr.coef_[0][0]:.2f} / {lr.coef_[0][1]:.2f} |")
    # 2. calibration du marche et du modele
    rap += ["\n### 2. Calibration : quand le prix affiche X, combien de fois Up gagne vraiment (toutes secondes, 12 jours)\n",
            "| Prix Up | Marche : secondes | Marche : Up gagne | Modele : secondes | Modele : Up gagne |", "|---|---|---|---|---|"]
    for lo in np.arange(0.0, 1.0, 0.1):
        sm = (MK >= lo) & (MK < lo + 0.1); so = (MO >= lo) & (MO < lo + 0.1)
        rap.append(f"| {lo:.1f}-{lo + 0.1:.1f} | {int(sm.sum())} | {100 * G[sm].mean():.1f} % | {int(so.sum())} | {100 * G[so].mean():.1f} % |" if sm.sum() and so.sum() else f"| {lo:.1f}-{lo + 0.1:.1f} | | | | |")
    rap += ["\n#### Favoris extremes selon le temps restant (le marche est-il trop sur de lui ?)\n",
            "| Temps restant | Marche donne au favori | Secondes | Le favori gagne vraiment | Modele moyen pour ce favori |", "|---|---|---|---|---|"]
    FAV = np.maximum(MK, 1 - MK); GF = np.where(MK >= 0.5, G, 1 - G); MOF = np.where(MK >= 0.5, MO, 1 - MO)
    for (a_, b_) in TB:
        for lo, hi in ((0.70, 0.80), (0.80, 0.90), (0.90, 0.95), (0.95, 0.99)):
            sel = (TL > a_) & (TL <= b_) & (FAV >= lo) & (FAV < hi)
            if sel.sum() >= 200:
                rap.append(f"| {a_}-{b_} s | {lo:.2f}-{hi:.2f} | {int(sel.sum())} | {100 * GF[sel].mean():.1f} % | {100 * MOF[sel].mean():.1f} % |")
    # 3. qui mene
    rap += ["\n### 3. Qui mene ? correlation entre variation du marche (seconde t) et variation du modele (seconde t - d)\n",
            "d > 0 : le modele a bouge AVANT le marche (le modele mene). d < 0 : le marche a bouge avant le modele.\n",
            "| Decalage d (s) | Correlation |", "|---|---|"]
    for d in range(-5, 6):
        v = np.array(lead[d])
        if len(v) > 100: rap.append(f"| {d:+d} | {np.corrcoef(v[:, 0], v[:, 1])[0, 1]:.3f} |")
    # 4. desaccords
    rap += ["\n### 4. Quand modele et marche ne sont pas d'accord\n",
            "Gain par part, achat au prix d'un vrai acheteur (<= prix affiche + 1 cent) dans les 2 s, frais compris, garde jusqu'a la fin.\n",
            "| Ecart | Episodes | Duree mediane (s) | Le modele a raison | Achat possible (cote modele) | Gain/part cote modele | Gain/part cote modele jours 9-12 | Gain/part cote marche |", "|---|---|---|---|---|---|---|---|"]
    for seuil in (0.05, 0.10, 0.15, 0.20):
        D = [x for x in dis if x["seuil"] == seuil]
        if not D: continue
        E_ = [x for x in D if x["execu"]]; Et = [x for x in E_ if x["test"]]; C_ = [x for x in D if x["execc"]]
        rap.append(f"| >= {seuil:.2f} | {len(D)} | {statistics.median(x['duree'] for x in D):.0f} | {100 * statistics.mean(x['gagne_modele'] for x in D):.1f} % | {100 * len(E_) / len(D):.0f} % | "
                   f"{(statistics.mean(x['pnl_modele'] for x in E_) if E_ else float('nan')):+.3f} $ | {(statistics.mean(x['pnl_modele'] for x in Et) if Et else float('nan')):+.3f} $ | {(statistics.mean(x['pnl_marche'] for x in C_) if C_ else float('nan')):+.3f} $ |")
    rap += ["\n#### Desaccords >= 0,10 selon le temps restant et le prix du cote choisi par le modele\n",
            "| Temps restant | Prix marche du cote modele | Episodes achetables | Le modele a raison | Gain/part | Gain/part jours 9-12 |", "|---|---|---|---|---|---|"]
    D = [x for x in dis if x["seuil"] == 0.10 and x["execu"]]
    for (a_, b_) in TB:
        for lo, hi in ((0.0, 0.3), (0.3, 0.5), (0.5, 0.7), (0.7, 1.0)):
            G_ = [x for x in D if a_ < x["tleft"] <= b_ and lo <= x["marche_cote"] < hi]
            Gt = [x for x in G_ if x["test"]]
            if len(G_) >= 30:
                rap.append(f"| {a_}-{b_} s | {lo:.1f}-{hi:.1f} | {len(G_)} | {100 * statistics.mean(x['gagne_modele'] for x in G_):.1f} % | {statistics.mean(x['pnl_modele'] for x in G_):+.3f} $ | {(statistics.mean(x['pnl_modele'] for x in Gt) if Gt else float('nan')):+.3f} $ |")
    print("\n".join(rap)); sys.stdout.flush()
    return rap


def main():
    t0 = time.time()
    fin = int(time.time()) // 86400 * 86400 - 300
    debut = fin + 300 - JOURS * 86400
    jours = sorted({datetime.fromtimestamp(t, timezone.utc).strftime("%Y-%m-%d") for t in range(debut - 3700, fin + 600, 3600)})
    jours = [j for j in jours if j < datetime.now(timezone.utc).strftime("%Y-%m-%d")]
    coupe = debut + int(JOURS * 2 / 3) * 86400
    rap = [f"# Notre modele contre le marche Polymarket — {JOURS} jours ({jours[1]} -> {jours[-1]})",
           "Prix marche = dernier echange (moins de 3 s). Modele = celui de V1 (Binance spot 1 s, prix a battre Polymarket, moyenne 60 s)."]
    for prefixe, sym in (("btc", "BTCUSDT"), ("eth", "ETHUSDT")):
        rap += etudier(prefixe, sym, jours, debut, fin, coupe)
        open(OUT + "resultat_calib.md", "w").write("\n".join(rap))
    rap.append(f"\nDuree : {time.time() - t0:.0f} s")
    open(OUT + "resultat_calib.md", "w").write("\n".join(rap))


if __name__ == "__main__":
    main()
