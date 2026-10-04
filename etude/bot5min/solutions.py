"""Pistes pour plus de trades (regle TWAP 60 s, incertitude Binance/Chainlink incluse) :
fenetre plus longue, prix max jusqu'a 0,999, autres cryptos (ETH, SOL, XRP 5 min)."""
import sys, math, statistics, time, json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
sys.path.insert(0, "etude/bot5min")
import test as T

JOURS = int(sys.argv[1]) if len(sys.argv) > 1 else 7
ACTIFS = [("btc", "BTCUSDT"), ("eth", "ETHUSDT"), ("sol", "SOLUSDT"), ("xrp", "XRPUSDT")]


def marche(prefixe, start):
    try:
        ev = T.get(f"{T.G}/events?slug={prefixe}-updown-5m-{start}")
    except Exception:
        return None
    if not ev: return None
    e = ev[0]; m = (e.get("markets") or [None])[0]
    if not m: return None
    try:
        out = json.loads(m.get("outcomes") or "[]"); px = [float(x) for x in json.loads(m.get("outcomePrices") or "[]")]
    except Exception: return None
    if sorted(px) != [0.0, 1.0]: return None
    meta = e.get("eventMetadata") or m.get("eventMetadata") or {}
    if isinstance(meta, str):
        try: meta = json.loads(meta)
        except Exception: meta = {}
    return {"start": start, "end": start + 300, "cid": m["conditionId"], "up_gagne": out[px.index(1.0)].lower() == "up",
            "strike": meta.get("priceToBeat"), "final": meta.get("finalPrice")}


def twap(px, a, b):
    v = [x for x in (T.prix(px, s) for s in range(a, b + 1)) if x]
    return sum(v) / len(v) if v else None


def etudier(prefixe, sym, jours, debut, fin):
    t0 = time.time()
    PX = T.binance(sym, jours)
    with ThreadPoolExecutor(12) as ex:
        M = sorted([m for m in ex.map(lambda s: marche(prefixe, s), range(debut, fin, 300)) if m], key=lambda m: m["start"])
    def tr(m):
        try: m["trades"] = T.trades(m)
        except Exception: m["trades"] = []
        return m
    with ThreadPoolExecutor(10) as ex:
        M = list(ex.map(tr, M))
    hist, derives = [], []
    for m in M:
        kp = float(m["strike"]) if m["strike"] is not None else None
        tb = twap(PX, m["start"] - 59, m["start"]); tf = twap(PX, m["end"] - 59, m["end"])
        m["base"] = statistics.median(hist[-12:]) if len(hist) >= 3 else 0
        if kp and tb: hist.append(tb - kp)
        m["K"] = (kp + m["base"]) if kp else None
        fo = float(m["final"]) if m.get("final") is not None else None
        m["sd_b"] = statistics.pstdev(derives[-50:]) if len(derives) >= 10 else None
        if tf and tb and fo and kp: derives.append((tf - tb) - (fo - kp))
    print(prefixe, "marches", len(M), "(%.0fs)" % (time.time() - t0)); sys.stdout.flush()

    def z_de(m, ts, fav_up):
        K = m["K"]; P = T.prix(PX, ts); sg = T.sigma_s(PX, ts)
        if not (K and P and sg and m["sd_b"]): return None
        a = m["end"] - 59
        connus = [x for x in (T.prix(PX, s) for s in range(a, ts + 1)) if x] if ts >= a else []
        nr = m["end"] - max(ts, a - 1)
        E = (sum(connus) + nr * P) / (len(connus) + nr)
        sd = math.sqrt((sg * P * math.sqrt(nr ** 3 / 3) / 60) ** 2 + m["sd_b"] ** 2)
        return ((E - K) / sd) * (1 if fav_up else -1)

    def run(W, pmax, zmin, reel):
        L = []
        for m in M:
            for (ts, pup, size, wal, up, side) in m["trades"]:
                if ts < m["end"] - W or ts > m["end"] - 1: continue
                fav_up = pup >= 0.5; pf = pup if fav_up else 1 - pup
                if reel and not (side == "BUY" and up == fav_up): continue
                if not reel and not (side == "SELL" and up == fav_up): continue
                if not (0.94 <= pf <= pmax): continue
                z = z_de(m, ts, fav_up)
                if z is not None and z >= zmin and T.phi(z) >= pf + (0.01 if pf <= 0.985 else (1 - pf) / 2):
                    L.append((pf, fav_up == m["up_gagne"], reel)); break
        g = 0
        for (p, ok, r) in L:
            parts = 50 / p
            g += (parts * (1 - p) if ok else -50) - (parts * T.FEE_RATE * p * (1 - p) if r else 0)
        return len(L), sum(1 for x in L if not x[1]), g

    lignes = []
    for reel, nom in ((True, "A"), (False, "B")):
        for W in (30, 60, 90, 120):
            for pmax in (0.99, 0.995, 0.999):
                for zmin in (2.5, 3.0):
                    n, pe, g = run(W, pmax, zmin, reel)
                    lignes.append(f"| {prefixe.upper()} | {nom} | {W} s | {pmax} | {zmin} | {n} | {pe} | {g:+.0f} $ | {n / JOURS:.1f} |")
    return lignes


def main():
    t0 = time.time()
    fin = int(time.time()) // 300 * 300 - 600
    debut = fin - JOURS * 86400
    jours = sorted({datetime.fromtimestamp(t, timezone.utc).strftime("%Y-%m-%d") for t in range(debut - 600, fin + 600, 3600)})
    jours = [j for j in jours if j < datetime.now(timezone.utc).strftime("%Y-%m-%d")]
    fin = min(fin, int(datetime.strptime(jours[-1], "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp()) + 86400 - 300)
    rap = [f"# Pistes pour plus de trades — {JOURS} jours ({jours[0]} -> {jours[-1]}), regle TWAP 60 s\n",
           "A = vrai achat au prix vendeur (frais inclus) ; B = offre posee remplie par un vendeur (sans frais). Mise fixe 50 $.\n",
           "| Actif | Option | Fenetre | Prix max | Distance mini | Trades | Pertes | Gain | Trades/jour |", "|---|---|---|---|---|---|---|---|---|"]
    for prefixe, sym in ACTIFS:
        try:
            rap += etudier(prefixe, sym, jours, debut, fin)
        except Exception as e:
            rap.append(f"| {prefixe.upper()} | erreur : {str(e)[:80]} |")
        open("etude/bot5min/resultat_solutions.md", "w").write("\n".join(rap))
    rap.append(f"\nDuree : {time.time() - t0:.0f} s")
    open("etude/bot5min/resultat_solutions.md", "w").write("\n".join(rap))
    print("\n".join(rap))


if __name__ == "__main__":
    main()
