"""Carte de fiabilite (idee 4 de ChatGPT) — ancienne entete : Analyse profonde : notre modele contre le marche Polymarket — BTC et ETH, 12 jours, seconde par seconde.
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

    # ---- etats par seconde : temps restant, prix du favori, distance en sigma, volatilite, mouvement recent
    rows = []
    for m in M:
        up = np.full(300, np.nan); vu = np.full(300, -99)
        for (ts, u, p, size, side) in m["tr"]:
            k = ts - m["start"]
            if 0 <= k < 300: up[k] = p if u else 1 - p; vu[k] = k
        for k in range(1, 300):
            if np.isnan(up[k]): up[k] = up[k - 1]; vu[k] = vu[k - 1]
        cache = {}
        g = 1 if m["up_gagne"] else 0
        for k in range(10, 297, 3):
            if vu[k] < k - 3 or np.isnan(up[k]) or np.isnan(up[k - 10]): continue
            pu = proba_up(m, m["start"] + k, cache)
            sg = cache.get(("sg", (m["start"] + k) // 15))
            if pu is None or not sg: continue
            fav_up = up[k] >= 0.5
            pf = up[k] if fav_up else 1 - up[k]
            if pf < 0.5 or pf > 0.99: continue
            z = abs(statistics.NormalDist().inv_cdf(min(max(pu, 1e-6), 1 - 1e-6)))
            mouv = (up[k] - up[k - 10]) * (1 if fav_up else -1)
            rows.append((m["start"], 300 - k, pf, z, sg, mouv, 1 if (g == 1) == fav_up else 0, m["start"] >= coupe))
    print(prefixe, "etats", len(rows), "(%.0fs)" % (time.time() - t0)); sys.stdout.flush()
    R = np.array([r[1:] for r in rows], dtype=float)
    TL, PF, Z, SG, MV, W, TE = R[:, 0], R[:, 1], R[:, 2], R[:, 3], R[:, 4], R[:, 5], R[:, 6] > 0.5
    v1, v2 = np.quantile(SG[~TE], [1 / 3, 2 / 3])
    cuts = {"temps": [(0, 30), (30, 60), (60, 120), (120, 180), (180, 300)],
            "prix": [(0.5, 0.6), (0.6, 0.7), (0.7, 0.8), (0.8, 0.9), (0.9, 0.95), (0.95, 0.99)],
            "dist": [(0, 0.5), (0.5, 1), (1, 2), (2, 99)],
            "vol": [(0, v1), (v1, v2), (v2, 9)],
            "mouv": [(-9, -0.03), (-0.03, 0.03), (0.03, 9)]}
    noms_m = {(-9, -0.03): "favori en baisse", (-0.03, 0.03): "stable", (0.03, 9): "favori en hausse"}
    noms_v = ["vol basse", "vol moyenne", "vol haute"]
    def frais(p): return 0.072 * p * (1 - p)
    res = []
    for ti in cuts["temps"]:
        for pi in cuts["prix"]:
            for di in cuts["dist"]:
                for vi_, vi in enumerate(cuts["vol"]):
                    for mi in cuts["mouv"]:
                        sel = (TL > ti[0]) & (TL <= ti[1]) & (PF >= pi[0]) & (PF < pi[1]) & (Z >= di[0]) & (Z < di[1]) & (SG >= vi[0]) & (SG < vi[1]) & (MV >= mi[0]) & (MV < mi[1])
                        a_, b_ = sel & ~TE, sel & TE
                        na, nb = int(a_.sum()), int(b_.sum())
                        if na < 300: continue
                        pa = PF[a_].mean() + 0.01; wa = W[a_].mean()
                        ea = wa - pa - frais(pa)                      # acheter le favori
                        eu = (1 - wa) - (1 - pa + 0.02) - frais(1 - pa + 0.02)   # acheter l'outsider
                        se = math.sqrt(wa * (1 - wa) / (na / 20))     # ~20 secondes correlees par cycle
                        best = max(("favori", ea), ("outsider", eu), key=lambda x: x[1])
                        if best[1] < 0.02 or best[1] < 2 * se: continue
                        if nb >= 50:
                            pb = PF[b_].mean() + 0.01; wb = W[b_].mean()
                            eb = (wb - pb - frais(pb)) if best[0] == "favori" else ((1 - wb) - (1 - pb + 0.02) - frais(1 - pb + 0.02))
                        else: eb, wb = float("nan"), float("nan")
                        res.append((best[1], f"{ti[0]}-{ti[1]} s", f"{pi[0]:.2f}-{pi[1]:.2f}", f"{di[0]}-{di[1] if di[1] < 99 else '+'} sigma", noms_v[vi_], noms_m[mi], best[0], na, wa, nb, wb, eb))
    res.sort(key=lambda x: -x[0])
    rap = [f"\n## {prefixe.upper()} — {len(rows)} etats (une mesure toutes les 3 s)\n",
           "Cases choisies sur les jours 1-8 (au moins 300 mesures, avantage >= 2 cents et >= 2 erreurs-types), verifiees sur les jours 9-12.\n",
           "| Temps restant | Prix du favori | Distance au prix a battre | Volatilite | Mouvement 10 s | Acheter | Mesures j1-8 | Favori gagne j1-8 | Avantage j1-8 | Mesures j9-12 | Favori gagne j9-12 | **Avantage j9-12** |",
           "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in res[:40]:
        rap.append(f"| {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5]} | {r[6]} | {r[7]} | {100 * r[8]:.1f} % | {100 * r[0]:+.1f} c | {r[9]} | {100 * r[10]:.1f} % | **{100 * r[11]:+.1f} c** |")
    tenu = [r for r in res if r[11] == r[11]]
    if tenu:
        rap.append(f"\nCases retenues : {len(res)} ; verifiables sur j9-12 : {len(tenu)} ; avantage moyen j1-8 {100 * statistics.mean(r[0] for r in tenu):+.1f} c -> **j9-12 {100 * statistics.mean(r[11] for r in tenu):+.1f} c** ; part qui reste positive : {100 * sum(1 for r in tenu if r[11] > 0) / len(tenu):.0f} %")
    print("\n".join(rap)); sys.stdout.flush()
    return rap


def main():
    t0 = time.time()
    fin = int(time.time()) // 86400 * 86400 - 300
    debut = fin + 300 - JOURS * 86400
    jours = sorted({datetime.fromtimestamp(t, timezone.utc).strftime("%Y-%m-%d") for t in range(debut - 3700, fin + 600, 3600)})
    jours = [j for j in jours if j < datetime.now(timezone.utc).strftime("%Y-%m-%d")]
    coupe = debut + int(JOURS * 2 / 3) * 86400
    rap = [f"# Carte de fiabilite du marche — {JOURS} jours ({jours[1]} -> {jours[-1]})",
           "Pour chaque etat (temps restant, prix du favori, distance au prix a battre en ecarts-types, volatilite, mouvement des 10 dernieres secondes) : le favori gagne-t-il plus ou moins souvent que son prix ?",
           "Avantage = frequence de gain - prix paye (dernier echange + 1 cent, outsider + 2 cents) - frais. Les remplissages restent optimistes : a confirmer avec les ordres fantomes en direct."]
    for prefixe, sym in (("btc", "BTCUSDT"), ("eth", "ETHUSDT")):
        rap += etudier(prefixe, sym, jours, debut, fin, coupe)
        open(OUT + "resultat_surface.md", "w").write("\n".join(rap))
    rap.append(f"\nDuree : {time.time() - t0:.0f} s")
    open(OUT + "resultat_surface.md", "w").write("\n".join(rap))


if __name__ == "__main__":
    main()
