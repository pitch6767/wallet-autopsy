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


def preparer(prefixe, sym, jours, debut, fin, coupe):
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

    out = {}
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
        sp = np.array([prix(m["start"] + k) or np.nan for k in range(300)])
        out[m["start"]] = {"up": up, "vu": vu, "bu": bu, "bd": bd, "pm": pm, "sp": sp, "g": 1 if m["up_gagne"] else 0}
    print(prefixe, "pret", len(out), "(%.0fs)" % (time.time() - t0)); sys.stdout.flush()
    return out


def episodes(D, A, autre, coupe, seuil=0.10):
    """premier instant de chaque episode de desaccord >= seuil ; caracteristiques ; gain realiste du cote modele"""
    E = []
    for st, c in D[A].items():
        o = D[autre].get(st)
        k = 5
        while k < 290:
            up, pm, vu = c["up"], c["pm"], c["vu"]
            if vu[k] < k - 3 or np.isnan(pm[k]) or np.isnan(up[k]): k += 1; continue
            ec = pm[k] - up[k]
            if abs(ec) < seuil: k += 1; continue
            j = k
            while j < 295 and not np.isnan(pm[j]) and abs(pm[j] - up[j]) >= seuil / 2: j += 1
            cote_up = ec > 0
            prixm = (up[k] if cote_up else 1 - up[k]) + 0.01
            X = c["bu"] if cote_up else c["bd"]
            f_ = min(X[k + 1], X[k + 2])
            if f_ <= prixm + 1e-9:
                tl = 300 - k
                s = 1 if cote_up else -1
                perp = (c["sp"][k] - c["sp"][k - 5]) * s if not np.isnan(c["sp"][k - 5]) else 0
                mk10 = (up[k] - up[k - 10]) * s if k >= 10 else 0
                if o is not None and not np.isnan(o["pm"][k]) and o["vu"][k] >= k - 3:
                    eo = (o["pm"][k] - o["up"][k]) * s
                    acc = "autre d'accord" if eo >= 0.05 else ("autre contre" if eo <= -0.05 else "autre neutre")
                else: acc = "autre ?"
                gagne = (c["g"] == 1) == cote_up
                E.append({"st": st, "test": st >= coupe,
                          "temps": "debut >4min" if tl > 240 else ("milieu" if tl > 120 else ("fin <2min" if tl > 30 else "dernieres 30s")),
                          "prix": "<0.30" if f_ < 0.30 else ("0.30-0.50" if f_ < 0.5 else ">0.50"),
                          "perp": "perp avec" if perp > 0 else ("perp contre" if perp < 0 else "perp plat"),
                          "marche": "marche vers nous" if mk10 > 0.02 else ("marche contre" if mk10 < -0.02 else "marche stable"),
                          "autre": acc, "ecart": "ecart>=0.20" if abs(ec) >= 0.2 else ("0.15-0.20" if abs(ec) >= 0.15 else "0.10-0.15"),
                          "pnl": float((1 if gagne else 0) - f_ - 0.072 * f_ * (1 - f_)), "g": float(gagne)})
            k = j + 1
    return E


def main():
    t0 = time.time()
    fin = int(time.time()) // 86400 * 86400 - 300
    debut = fin + 300 - JOURS * 86400
    jours = sorted({datetime.fromtimestamp(t, timezone.utc).strftime("%Y-%m-%d") for t in range(debut - 3700, fin + 600, 3600)})
    jours = [j for j in jours if j < datetime.now(timezone.utc).strftime("%Y-%m-%d")]
    coupe = debut + int(JOURS * 2 / 3) * 86400
    D = {"btc": preparer("btc", "BTCUSDT", jours, debut, fin, coupe), "eth": preparer("eth", "ETHUSDT", jours, debut, fin, coupe)}
    import itertools
    rap = [f"# Desaccords modele/marche : quelles combinaisons gagnent ? — {JOURS} jours ({jours[1]} -> {jours[-1]})",
           "Episode = premier instant ou |modele - marche| >= 0,10 ; achat du cote du modele seulement si un vrai acheteur a paye ce prix (+1 cent) dans les 2 s ; garde jusqu'a la fin ; gain par part, frais compris.",
           "Combinaisons choisies sur les jours 1-8 (au moins 60 episodes), verifiees sur les jours 9-12.\n"]
    for A, B in (("btc", "eth"), ("eth", "btc")):
        E = episodes(D, A, B, coupe)
        a_ = [e for e in E if not e["test"]]; b_ = [e for e in E if e["test"]]
        rap += [f"\n## {A.upper()} — {len(E)} episodes achetables (j1-8 : {len(a_)}, j9-12 : {len(b_)})\n",
                f"Tous : gain/part j1-8 {statistics.mean(e['pnl'] for e in a_):+.3f} $, **j9-12 {statistics.mean(e['pnl'] for e in b_):+.3f} $**\n"]
        crit = ["temps", "prix", "perp", "marche", "autre", "ecart"]
        # 1. chaque critere seul
        rap += ["### Chaque critere seul\n", "| Critere | Valeur | Episodes j1-8 | Gagne | Gain/part j1-8 | Episodes j9-12 | **Gain/part j9-12** |", "|---|---|---|---|---|---|---|"]
        for c_ in crit:
            for v in sorted({e[c_] for e in E}):
                xa = [e for e in a_ if e[c_] == v]; xb = [e for e in b_ if e[c_] == v]
                if len(xa) >= 30:
                    rap.append(f"| {c_} | {v} | {len(xa)} | {100 * statistics.mean(e['g'] for e in xa):.0f} % | {statistics.mean(e['pnl'] for e in xa):+.3f} $ | {len(xb)} | **{(statistics.mean(e['pnl'] for e in xb) if xb else float('nan')):+.3f} $** |")
        # 2. combinaisons de 2 et 3 criteres
        res = []
        for r_ in (2, 3):
            for cs in itertools.combinations(crit, r_):
                groupes = collections.defaultdict(lambda: ([], []))
                for e in a_: groupes[tuple(e[c] for c in cs)][0].append(e)
                for e in b_: groupes[tuple(e[c] for c in cs)][1].append(e)
                for key, (xa, xb) in groupes.items():
                    if len(xa) < 60 or len(xb) < 20: continue
                    ga = statistics.mean(e["pnl"] for e in xa); gb = statistics.mean(e["pnl"] for e in xb)
                    res.append((ga, gb, " + ".join(f"{c}={v}" for c, v in zip(cs, key)), len(xa), len(xb), statistics.mean(e["g"] for e in xa), statistics.mean(e["g"] for e in xb)))
        res.sort(key=lambda x: -x[0])
        rap += ["\n### Meilleures combinaisons (choisies j1-8)\n", "| Combinaison | Episodes j1-8 | Gagne j1-8 | Gain/part j1-8 | Episodes j9-12 | Gagne j9-12 | **Gain/part j9-12** |", "|---|---|---|---|---|---|---|"]
        for ga, gb, nom, na, nb, wa, wb in res[:25]:
            rap.append(f"| {nom} | {na} | {100 * wa:.0f} % | {ga:+.3f} $ | {nb} | {100 * wb:.0f} % | **{gb:+.3f} $** |")
        rap += ["\n### Pires combinaisons (a eviter, choisies j1-8)\n", "| Combinaison | Episodes j1-8 | Gain/part j1-8 | Episodes j9-12 | **Gain/part j9-12** |", "|---|---|---|---|---|"]
        for ga, gb, nom, na, nb, wa, wb in sorted(res, key=lambda x: x[0])[:12]:
            rap.append(f"| {nom} | {na} | {ga:+.3f} $ | {nb} | **{gb:+.3f} $** |")
        top = res[:25]
        if top: rap.append(f"\nLes 25 meilleures (j1-8) en moyenne : j1-8 {statistics.mean(x[0] for x in top):+.3f} $ -> **j9-12 {statistics.mean(x[1] for x in top):+.3f} $** ; restent positives sur j9-12 : {sum(1 for x in top if x[1] > 0)}/25")
        open(OUT + "resultat_combinaisons.md", "w").write("\n".join(rap))
    rap.append(f"\nDuree : {time.time() - t0:.0f} s")
    open(OUT + "resultat_combinaisons.md", "w").write("\n".join(rap))
    print("\n".join(rap))


if __name__ == "__main__":
    main()
