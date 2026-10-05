"""Reduction des pertes de V1 (paires BTC 5 min) — (05.10.2026) — vrais echanges Polymarket + Binance 1 s, regle TWAP 60 s.
V1 (Pitch filtre) : jambe 1 achetee (taker) a 0,55-0,56 seulement si proba calculee >= 0,55 + M ; offre maker sur l'autre cote a min(proba - M, 0,43) ;
    sortie si proba de la jambe < 0,50 ; sortie a 0,90 si jambe seule ; fusion si paire.
V2 (valeur seule) : offres maker des deux cotes a proba - M, deplacees en continu ; fusion si paire ; jambe seule gardee (ou sortie 0,90).
Remplissage PRUDENT : un vendeur doit passer au moins 1 cent SOUS notre offre (on n'est pas forcement premier dans la file).
"""
import sys, math, time, statistics, json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
sys.path.insert(0, "etude/bot5min")
import test as T
import paires as P

JOURS = int(sys.argv[1]) if len(sys.argv) > 1 else 7
N = 100.0
FEE = lambda p: T.FEE_RATE * p * (1 - p)


def twap(px, a, b):
    v = [x for x in (T.prix(px, s) for s in range(a, b + 1)) if x]
    return sum(v) / len(v) if v else None


def main():
    t0 = time.time()
    fin = int(time.time()) // 300 * 300 - 900
    debut = fin - JOURS * 86400
    jours = sorted({datetime.fromtimestamp(t, timezone.utc).strftime("%Y-%m-%d") for t in range(debut - 600, fin + 600, 3600)})
    jours = [j for j in jours if j < datetime.now(timezone.utc).strftime("%Y-%m-%d")]
    fin = min(fin, int(datetime.strptime(jours[-1], "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp()) + 86400 - 300)
    BTC = T.binance("BTCUSDT", jours)
    with ThreadPoolExecutor(12) as ex:
        M = sorted([m for m in ex.map(P.marche, range(debut, fin, 300)) if m], key=lambda m: m["start"])
    # prix d'exercice et prix final officiels
    def meta(m):
        try:
            e = T.get(f"{T.G}/events?slug=btc-updown-5m-{m['start']}")[0]
            mt = e.get("eventMetadata") or e["markets"][0].get("eventMetadata") or {}
            if isinstance(mt, str): mt = json.loads(mt)
            m["kp"] = float(mt["priceToBeat"]); m["fo"] = float(mt["finalPrice"])
        except Exception:
            m["kp"] = None
        try: m["tr"], _ = P.echanges(m)
        except Exception: m["tr"] = []
        return m
    with ThreadPoolExecutor(10) as ex:
        M = [m for m in ex.map(meta, M) if m["kp"] and m["tr"]]
    print("cycles", len(M), "(%.0fs)" % (time.time() - t0)); sys.stdout.flush()

    hist, derives = [], []
    for m in M:
        tb = twap(BTC, m["start"] - 59, m["start"]); tf = twap(BTC, m["end"] - 59, m["end"])
        m["base"] = statistics.median(hist[-12:]) if len(hist) >= 3 else 0
        if tb: hist.append(tb - m["kp"])
        m["K"] = m["kp"] + m["base"]
        m["sd_b"] = statistics.pstdev(derives[-50:]) if len(derives) >= 10 else None
        if tf and tb: derives.append((tf - tb) - (m["fo"] - m["kp"]))

    def proba_up(m, ts, cache):
        if ts in cache: return cache[ts]
        r = None
        P0 = T.prix(BTC, ts)
        sgk = ts // 15
        if ("sg", sgk) not in cache: cache[("sg", sgk)] = T.sigma_s(BTC, ts)
        sg = cache[("sg", sgk)]
        if P0 and sg and m["sd_b"]:
            a = m["end"] - 59
            if ts >= a:
                connus = [x for x in (T.prix(BTC, s) for s in range(a, ts + 1)) if x]
                nr = m["end"] - ts
                E = (sum(connus) + nr * P0) / (len(connus) + nr)
                var = (sg * P0) ** 2 * nr ** 3 / 3 / 3600
            else:
                E = P0
                var = (sg * P0) ** 2 * ((a - ts) + 60 / 3)
            sd = math.sqrt(var + m["sd_b"] ** 2)
            r = T.phi((E - m["K"]) / sd)
        cache[ts] = r
        return r

    def v1g(m, Mg, stop, tp, fen, mom, L=2):
        cache = m.setdefault("cache%d" % L, {})
        A = None; invB = [0.0, 0.0]; pnl = 0.0; etat = "rien"; dernier = {True: 0.5, False: 0.5}
        for (ts, up, p, size, side) in m["tr"]:
            if ts < m["start"] or ts > m["end"] - 1: continue
            dernier[up] = p; dernier[not up] = 1 - p
            pu = proba_up(m, ts - L, cache)
            if pu is None: continue
            if A is None:
                el = ts - m["start"]
                if fen == "debut" and el > 120: continue
                if fen == "fin" and el <= 120: continue
                if side == "BUY" and 0.55 <= p <= 0.56:
                    fair = pu if up else 1 - pu
                    if fair >= 0.55 + Mg:
                        if mom:
                            a0, b0 = T.prix(BTC, ts - L - 5), T.prix(BTC, ts - L)
                            if not (a0 and b0 and ((b0 - a0) * (1 if up else -1)) > 0): continue
                        A = {"cote": up, "prix": p, "q": N, "fair0": fair}; pnl -= N * FEE(p); etat = "jambe"
                continue
            if A.get("fini"): break
            c = A["cote"]; fairA = pu if c else 1 - pu
            if side == "SELL": O, q = up, p
            elif side == "BUY": O, q = (not up), 1 - p
            else: O = None
            if O is not None and O != c and invB[0] < A["q"]:
                offre = min(math.floor(((1 - fairA) - Mg) * 100) / 100, 0.43)
                if offre >= 0.02 and q <= offre - 0.01 + 1e-9:
                    k = min(size, A["q"] - invB[0]); invB[0] += k; invB[1] += k * offre
            if invB[0] >= A["q"] - 1e-9:
                pnl += A["q"] * (1 - A["prix"]) - invB[1]; etat = "paire"; A["fini"] = True; invB = [0.0, 0.0]; break
            seuil = stop[1] if stop[0] == "abs" else A["fair0"] - stop[1]
            if fairA < seuil:
                pv = max(0.01, dernier[c] - 0.01); qa = A["q"] - invB[0]
                pnl += qa * (pv - FEE(pv)) - qa * A["prix"] + invB[0] * (1 - A["prix"]) - invB[1]
                etat = "stop"; A["fini"] = True; invB = [0.0, 0.0]; break
            if up == c and p >= tp and invB[0] < 1e-9:
                pnl += A["q"] * (tp - FEE(tp) - A["prix"]); etat = "sortie"; A["fini"] = True; break
        if A and not A.get("fini"):
            g = A["cote"] == m["up_gagne"]; qa = A["q"] - invB[0]
            pnl += qa * ((1 if g else 0) - A["prix"]) + invB[0] * (1 - A["prix"]) - invB[1]
            etat = "fin " + ("gagnee" if g else "perdue")
        return pnl, etat

    rap = [f"# Reduire les pertes de V1 — {len(M)} cycles BTC 5 min, {JOURS} jours, retard de reaction 2 s, remplissage prudent\n",
           "| Marge entree | Stop | Sortie | Moment d'entree | Elan Binance | Trades/j | Gain/j | Cycles perdants | Pertes totales | Perte moyenne | Pire baisse |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    res = []
    for Mg in (0.08, 0.12):
        for stop in (("abs", 0.50), ("abs", 0.45), ("abs", 0.40), ("rel", 0.15)):
            for tp in (0.80, 0.85, 0.90):
                for fen in ("tout", "debut", "fin"):
                    for mom in (False, True):
                        R = [v1g(m, Mg, stop, tp, fen, mom) for m in M]
                        R2 = [p for p, e in R if e != "rien"]
                        cum = pic = dd = 0
                        for p, _ in R:
                            cum += p; pic = max(pic, cum); dd = max(dd, pic - cum)
                        perd = [p for p in R2 if p < 0]
                        res.append((Mg, stop, tp, fen, mom, len(R2), sum(R2), len(perd), sum(perd), dd))
    ref = [r for r in res if r[0] == 0.08 and r[1] == ("abs", 0.50) and r[2] == 0.90 and r[3] == "tout" and not r[4]]
    def lg(r):
        st = (f"proba < {r[1][1]:.2f}" if r[1][0] == "abs" else f"proba - {r[1][1]:.2f} depuis l'entree")
        n = r[5] or 1
        return f"| {r[0]:.2f} | {st} | {r[2]:.2f} | {r[3]} | {'oui' if r[4] else 'non'} | {r[5] / JOURS:.0f} | {r[6] / JOURS:+.0f} $ | {100 * r[7] / n:.0f} % | {r[8]:+.0f} $ | {(r[8] / r[7] if r[7] else 0):+.1f} $ | -{r[9]:.0f} $ |"
    rap.append("**Reference (version actuelle du bot)**")
    rap += [lg(r) for r in ref]
    rap.append("\n**Top 25 par gain**\n")
    rap += ["| Marge entree | Stop | Sortie | Moment d'entree | Elan Binance | Trades/j | Gain/j | Cycles perdants | Pertes totales | Perte moyenne | Pire baisse |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    rap += [lg(r) for r in sorted(res, key=lambda r: -r[6])[:25]]
    rap.append("\n**Top 25 par meilleur rapport gain / pire baisse (au moins 50 trades/jour)**\n")
    rap += ["| Marge entree | Stop | Sortie | Moment d'entree | Elan Binance | Trades/j | Gain/j | Cycles perdants | Pertes totales | Perte moyenne | Pire baisse |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    rap += [lg(r) for r in sorted([r for r in res if r[5] / JOURS >= 50 and r[6] > 0], key=lambda r: -r[6] / max(r[9], 1))[:25]]
    rap.append(f"\nDuree : {time.time() - t0:.0f} s")
    open("etude/bot5min/resultat_paires3.md", "w").write("\n".join(rap))
    print("\n".join(rap))


if __name__ == "__main__":
    main()
