"""Analyse de l'enregistreur en direct du bot (4 mesures/s) : modele, carnet Polymarket reel, bourses.
1. Qui mene : le prix Polymarket (milieu du carnet) suit-il le perp Bybit / Binance / Coinbase / notre modele, avec quel retard ?
2. Occasions reelles : combien de temps le meilleur vendeur est-il SOUS la valeur du modele (de 3, 5, 8 cents), et combien de temps ca dure.
3. Gain realiste de ces occasions (achat au meilleur vendeur, frais, garde jusqu'a la fin, resultat officiel).
4. Calibration du marche contre le modele sur la periode enregistree.
"""
import json, sys, math, time, statistics, collections, urllib.request
import numpy as np

U = "https://bot95.pitch67.workers.dev"
OUT = "etude/bot5min/"
FEE = lambda p: 0.072 * p * (1 - p)


def get(url):
    for k in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "analyse"}), timeout=60) as r: return json.loads(r.read())
        except Exception as e:
            err = e; time.sleep(2)
    raise err


def charger(a):
    lignes, apres = [], None
    while True:
        d = get(f"{U}/api/rec?a={a}&n=60" + (f"&apres={apres}" if apres else ""))
        for doc in d["docs"]: lignes += doc["lignes"]
        if not d["cles"] or len(d["cles"]) < 60: break
        apres = d["suivant"]
    return lignes


def resultat(prefixe, start, cache):
    if start in cache: return cache[start]
    r = None
    try:
        ev = get(f"https://gamma-api.polymarket.com/events?slug={prefixe}-updown-5m-{start}")
        m = ev[0]["markets"][0]; px = [float(x) for x in json.loads(m["outcomePrices"])]; outs = json.loads(m["outcomes"])
        if sorted(px) == [0.0, 1.0]: r = outs[px.index(1.0)].lower() == "up"
    except Exception: pass
    cache[start] = r
    return r


def logit(x): x = min(max(x, 1e-3), 1 - 1e-3); return math.log(x / (1 - x))


def etudier(a):
    L = charger(a)
    rap = [f"\n## {a} — {len(L)} mesures ({len(L) / 4 / 3600:.1f} h)\n"]
    if len(L) < 2000: return rap + ["Pas assez de donnees."]
    L.sort(key=lambda r: r[0])
    # colonnes : t start pu ub ua db da ubs uas dbs das perp okx cb bn cl strike
    cyc = collections.defaultdict(list)
    for r in L: cyc[r[1]].append(r)
    # ---- 1. qui mene (variations sur 250 ms, decalage en pas de 250 ms)
    series = {"modele": [], "bybit_perp": [], "binance_spot": [], "coinbase": [], "okx_perp": [], "chainlink": []}
    marche = []
    idx = {"modele": 2, "bybit_perp": 11, "okx_perp": 12, "coinbase": 13, "binance_spot": 14, "chainlink": 15}
    for st, R in cyc.items():
        R = [r for r in R if r[3] is not None and r[4] is not None]
        if len(R) < 100: continue
        mid = [logit((r[3] + r[4]) / 2) for r in R]
        dm = np.diff(mid)
        marche.append(dm)
        for k, i in idx.items():
            v = [r[i] for r in R]
            if any(x is None for x in v): series[k].append(None); continue
            x = np.array([logit(z) for z in v]) if k == "modele" else np.log(np.array(v, dtype=float))
            series[k].append(np.diff(x))
    rap += ["### 1. Qui mene le prix Polymarket ?\n", "Correlation entre la variation du prix Polymarket a l'instant t et la variation de la source a t - d. d > 0 : la source bouge AVANT Polymarket.\n",
            "| Source | d = -1 s | -0,5 s | 0 | +0,25 s | +0,5 s | +0,75 s | +1 s | +2 s | +3 s | Avance la plus forte |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for k in idx:
        res = {}
        for d in (-4, -2, 0, 1, 2, 3, 4, 8, 12):
            xs, ys = [], []
            for dm, ds in zip(marche, series[k]):
                if ds is None: continue
                n = min(len(dm), len(ds))
                for t in range(max(0, d), min(n, n + d)):
                    if 0 <= t - d < n: xs.append(dm[t]); ys.append(ds[t - d])
            res[d] = np.corrcoef(xs, ys)[0, 1] if len(xs) > 200 and np.std(ys) > 0 else float("nan")
        best = max(res, key=lambda d: res[d] if res[d] == res[d] else -9)
        rap.append(f"| {k} | " + " | ".join(f"{res[d]:.3f}" for d in (-4, -2, 0, 1, 2, 3, 4, 8, 12)) + f" | {best * 0.25:+.2f} s |")
    # ---- 2 & 3. occasions reelles
    cache = {}
    pref = a.lower()
    rap += ["\n### 2. Occasions reelles : meilleur vendeur SOUS la valeur du modele\n",
            "| Avance du modele sur le vendeur | Part du temps | Episodes | Duree mediane | Achat au 1er instant : gagne | Gain/part (frais compris) |", "|---|---|---|---|---|---|"]
    for marge in (0.03, 0.05, 0.08, 0.12):
        n_tot = n_occ = 0; ep = []
        for st, R in cyc.items():
            g = resultat(pref, st, cache)
            for cote in ("up", "down"):
                en_cours = None
                for r in R:
                    pu, ask = r[2], (r[4] if cote == "up" else r[6])
                    if pu is None or ask is None: en_cours = None; continue
                    tl = st + 300 - r[0]
                    if tl < 3: continue
                    n_tot += 1
                    fair = pu if cote == "up" else 1 - pu
                    if fair - ask >= marge and 0.03 <= ask <= 0.97:
                        n_occ += 1
                        if en_cours is None: en_cours = {"t0": r[0], "ask": ask, "fair": fair, "tl": tl, "g": None if g is None else ((g and cote == "up") or (not g and cote == "down"))}
                        en_cours["t1"] = r[0]
                    elif en_cours is not None:
                        ep.append(en_cours); en_cours = None
                if en_cours is not None: ep.append(en_cours)
        if not ep: rap.append(f"| >= {marge:.2f} | {100 * n_occ / max(1, n_tot / 2):.2f} % | 0 | | | |"); continue
        E = [e for e in ep if e["g"] is not None]
        pnl = [(1 if e["g"] else 0) - e["ask"] - FEE(e["ask"]) for e in E]
        rap.append(f"| >= {marge:.2f} | {100 * n_occ / max(1, n_tot):.2f} % | {len(ep)} | {statistics.median(e['t1'] - e['t0'] for e in ep):.2f} s | {100 * statistics.mean(1 if e['g'] else 0 for e in E):.1f} % (prix moyen {statistics.mean(e['ask'] for e in E):.2f}) | {statistics.mean(pnl):+.3f} $ |" if E else f"| >= {marge:.2f} | | {len(ep)} | | | |")
    rap += ["\n#### Occasions >= 0,05 qui durent au moins 0,5 s (le temps de les prendre)\n", "| Temps restant | Episodes | Gagne | Gain/part |", "|---|---|---|---|"]
    ep5 = []
    for st, R in cyc.items():
        g = resultat(pref, st, cache)
        for cote in ("up", "down"):
            en = None
            for r in R:
                pu, ask = r[2], (r[4] if cote == "up" else r[6])
                if pu is None or ask is None: en = None; continue
                fair = pu if cote == "up" else 1 - pu
                if fair - ask >= 0.05 and 0.03 <= ask <= 0.97 and st + 300 - r[0] >= 3:
                    if en is None: en = {"t0": r[0], "ask": ask, "tl": st + 300 - r[0], "g": None if g is None else ((g and cote == "up") or (not g and cote == "down")), "prix05": None}
                    en["t1"] = r[0]
                    if en["prix05"] is None and r[0] - en["t0"] >= 0.5: en["prix05"] = ask
                elif en is not None: ep5.append(en); en = None
    for (lo, hi) in ((0, 60), (60, 180), (180, 300)):
        E = [e for e in ep5 if e["prix05"] is not None and e["g"] is not None and lo <= e["tl"] < hi]
        if E: rap.append(f"| {lo}-{hi} s | {len(E)} | {100 * statistics.mean(1 if e['g'] else 0 for e in E):.1f} % | {statistics.mean((1 if e['g'] else 0) - e['prix05'] - FEE(e['prix05']) for e in E):+.3f} $ |")
    # ---- 4. calibration
    xs = []
    for st, R in cyc.items():
        g = resultat(pref, st, cache)
        if g is None: continue
        for r in R[::4]:
            if r[2] is None or r[3] is None or r[4] is None: continue
            xs.append(((r[3] + r[4]) / 2, r[2], 1 if g else 0, st + 300 - r[0]))
    if xs:
        X = np.array(xs); ll = lambda p, y: float(-np.mean(y * np.log(np.clip(p, 0.005, 0.995)) + (1 - y) * np.log(1 - np.clip(p, 0.005, 0.995))))
        rap += ["\n### 3. Qui predit le mieux (periode enregistree)\n", "| Temps restant | Secondes | Erreur marche | Erreur modele |", "|---|---|---|---|"]
        for lo, hi in ((0, 60), (60, 120), (120, 180), (180, 240), (240, 300)):
            s = (X[:, 3] >= lo) & (X[:, 3] < hi)
            if s.sum() > 50: rap.append(f"| {lo}-{hi} s | {int(s.sum())} | {ll(X[s, 0], X[s, 2]):.4f} | {ll(X[s, 1], X[s, 2]):.4f} |")
    return rap


def main():
    rap = ["# Enregistreur en direct : modele contre carnet Polymarket reel"]
    for a in ("BTC", "ETH"):
        try: rap += etudier(a)
        except Exception as e: rap.append(f"\n{a} : erreur {e}")
        open(OUT + "resultat_rec.md", "w").write("\n".join(rap))
    print("\n".join(rap))


if __name__ == "__main__":
    main()
