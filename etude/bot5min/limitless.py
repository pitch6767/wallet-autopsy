"""95 c sur Polymarket + couverture sur Limitless (BTC 5 min). Lecture seule."""
import json, sys, time, statistics, urllib.request
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, "etude/bot5min")
import test as T

A = "https://api.limitless.exchange"
JOURS = int(sys.argv[1]) if len(sys.argv) > 1 else 7
OUT = "etude/bot5min/"


def lmt(start):
    slug = f"btc-up-or-down-5-min-{start}"
    try:
        m = T.get(f"{A}/markets/{slug}")
        h = T.get(f"{A}/markets/{slug}/historical-price?interval=1h")
    except Exception:
        return start, None
    return start, {"m": m, "px": sorted((int(p["timestamp"]) // 1000, float(p["price"])) for p in h.get("prices", []))}


def gagnant_lmt(m):
    for k in ("winningOutcomeIndex", "winning_outcome_index"):
        if m.get(k) is not None:
            return int(m[k]) == 0          # index 0 = Up (a verifier dans les cles affichees)
    for k in ("outcome", "result", "resolvedOutcome"):
        v = m.get(k)
        if isinstance(v, str) and v.lower() in ("up", "yes", "down", "no"):
            return v.lower() in ("up", "yes")
    return None


def main():
    t0 = time.time()
    fin = int(time.time()) // 300 * 300 - 900
    debut = fin - JOURS * 86400
    starts = list(range(debut, fin, 300))
    with ThreadPoolExecutor(12) as ex:
        P = {m["start"]: m for m in ex.map(T.marche, starts) if m}
    with ThreadPoolExecutor(8) as ex:
        L = {s: d for s, d in ex.map(lmt, starts) if d}
    ex1 = next(iter(L.values()))["m"]
    print("cles marche Limitless :", sorted(ex1.keys()))
    print("exemple :", {k: ex1.get(k) for k in ex1 if "win" in k.lower() or "outcome" in k.lower() or "status" in k.lower() or "resol" in k.lower()})
    print("Polymarket", len(P), "| Limitless", len(L), "(%.0fs)" % (time.time() - t0)); sys.stdout.flush()

    communs = [s for s in starts if s in P and s in L and gagnant_lmt(L[s]["m"]) is not None]
    diff = [s for s in communs if gagnant_lmt(L[s]["m"]) != P[s]["up_gagne"]]
    print("marches communs resolus :", len(communs), "| gagnant different :", len(diff),
          "(%.2f %%)" % (100 * len(diff) / max(1, len(communs)))); sys.stdout.flush()

    with ThreadPoolExecutor(10) as ex:
        M = [m for m in ex.map(lambda s: dict(P[s], trades=T.trades(P[s])), communs)]
    print("executions Polymarket chargees (%.0fs)" % (time.time() - t0)); sys.stdout.flush()

    rap = [f"# 95 c Polymarket + couverture Limitless — {len(communs)} marches 5 min ({JOURS} jours)\n",
           f"Limitless se regle sur la moyenne Chainlink 60 s (TWAP), Polymarket sur le prix Chainlink a l'instant.",
           f"**Gagnant different entre les deux : {len(diff)} / {len(communs)} ({100 * len(diff) / max(1, len(communs)):.2f} %)**\n",
           "Prix Limitless : point de prix historique (1 par minute environ) juste avant l'entree — indicatif, le carnet reel n'est pas archive.\n"]
    for (W, a, b) in ((30, 0.95, 0.97), (30, 0.95, 0.99), (60, 0.95, 0.97)):
        rap.append(f"\n## Entree Polymarket {W} s, {a:.2f}-{b:.2f}\n")
        rap.append("| Version | Trades | Pertes | PnL total | PnL moyen | Pire perte | Deux jambes perdantes |\n|---|---|---|---|---|---|---|")
        lignes = {}
        for m in M:
            tr = [x for x in m["trades"] if m["end"] - W <= x[0] <= m["end"] - 1]
            e = None
            for (ts, pup, *_r) in tr:
                fav_up = pup >= 0.5
                pf = pup if fav_up else 1 - pup
                if a <= pf <= b:
                    e = (ts, pf, fav_up); break
            if not e:
                continue
            ts, p, fav_up = e
            pts = [q for (t, q) in L[m["start"]]["px"] if t <= ts]
            if not pts:
                continue
            up_l = pts[-1]
            h = (1 - up_l) if fav_up else up_l          # prix de l'issue opposee chez Limitless
            g_poly = fav_up == m["up_gagne"]
            g_lmt_opp = (not fav_up) == gagnant_lmt(L[m["start"]]["m"])
            parts = T.MISE / p
            fp = parts * T.FEE_RATE * p * (1 - p)
            base = (parts * (1 - p) if g_poly else -T.MISE) - fp
            lignes.setdefault("Sans couverture", []).append((base, False))
            for cap in (0.02, 0.03, 0.05, 0.08):
                if h <= cap:
                    hedge = parts * ((1 - h) if g_lmt_opp else -h) - parts * h * 0.01
                    r = base + hedge
                    lignes.setdefault(f"Couvert si NON Limitless <= {cap:.2f}", []).append((r, not g_poly and not g_lmt_opp))
                else:
                    lignes.setdefault(f"Couvert si NON Limitless <= {cap:.2f}", []).append((base, False))
            hedge = parts * ((1 - h) if g_lmt_opp else -h) - parts * h * 0.01
            lignes.setdefault("Toujours couvert (au prix Limitless)", []).append((base + hedge, not g_poly and not g_lmt_opp))
        for nom, v in lignes.items():
            r = [x for x, _ in v]
            rap.append("| %s | %d | %d | %+.0f $ | %+.2f $ | %.0f $ | %d |" % (
                nom, len(r), sum(1 for x in r if x < 0), sum(r), statistics.mean(r), min(r), sum(1 for _, d in v if d)))
        # prix du NON Limitless observe
        hs = []
        for m in M:
            pts = L[m["start"]]["px"]
            if pts:
                pass
    rap.append(f"\nDuree : {time.time() - t0:.0f} s")
    open(OUT + "resultat_limitless.md", "w").write("\n".join(rap))
    print("\n".join(rap))


if __name__ == "__main__":
    main()
