"""B realiste (file d'attente) + idees A (plus tot / moins cher / distance plus grande). Regle TWAP 60 s."""
import sys, math, statistics, time, json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
sys.path.insert(0, "etude/bot5min")
import test as T
import solutions as S

JOURS = int(sys.argv[1]) if len(sys.argv) > 1 else 7
ACTIFS = [("btc", "BTCUSDT"), ("eth", "ETHUSDT"), ("sol", "SOLUSDT"), ("xrp", "XRPUSDT"), ("doge", "DOGEUSDT"), ("bnb", "BNBUSDT"), ("hype", "HYPEUSDT")]


def trades200(m):
    res = []
    for off in range(0, 3000, 500):
        lot = T.get(f"{T.D}/trades?market={m['cid']}&limit=500&offset={off}&takerOnly=true")
        if not lot: break
        for t in lot:
            ts = int(t["timestamp"])
            if m["end"] - 200 <= ts <= m["end"]:
                p = float(t["price"]); up = (t.get("outcome") or "").lower() == "up"
                res.append((ts, p if up else 1 - p, float(t["size"]), up, t.get("side")))
        desc = int(lot[0]["timestamp"]) >= int(lot[-1]["timestamp"])
        if len(lot) < 500 or (desc and int(lot[-1]["timestamp"]) < m["end"] - 200): break
    res.sort(); return res


def etudier(prefixe, sym, jours, debut, fin):
    PX = T.binance(sym, jours)
    with ThreadPoolExecutor(12) as ex:
        M = sorted([m for m in ex.map(lambda s: S.marche(prefixe, s), range(debut, fin, 300)) if m], key=lambda m: m["start"])
    if not M: return [f"| {prefixe.upper()} | aucun marche 5 min |"], []
    def tr(m):
        try: m["tr"] = trades200(m)
        except Exception: m["tr"] = []
        return m
    with ThreadPoolExecutor(10) as ex:
        M = list(ex.map(tr, M))
    hist, derives = [], []
    for m in M:
        kp = float(m["strike"]) if m["strike"] is not None else None
        tb = S.twap(PX, m["start"] - 59, m["start"]); tf = S.twap(PX, m["end"] - 59, m["end"])
        m["base"] = statistics.median(hist[-12:]) if len(hist) >= 3 else 0
        if kp and tb: hist.append(tb - kp)
        m["K"] = (kp + m["base"]) if kp else None
        fo = float(m["final"]) if m.get("final") is not None else None
        m["sd_b"] = statistics.pstdev(derives[-50:]) if len(derives) >= 10 else None
        if tf and tb and fo and kp: derives.append((tf - tb) - (fo - kp))
    print(prefixe, len(M), "marches"); sys.stdout.flush()

    cache = {}
    def z_de(m, ts, fav_up):
        cle = (m["start"], ts, fav_up)
        if cle not in cache: cache[cle] = z_calc(m, ts, fav_up)
        return cache[cle]

    def z_calc(m, ts, fav_up):
        K = m["K"]; P = T.prix(PX, ts); sg = T.sigma_s(PX, ts)
        if not (K and P and sg and m["sd_b"]): return None
        a = m["end"] - 59
        connus = [x for x in (T.prix(PX, s) for s in range(a, ts + 1)) if x] if ts >= a else []
        nr = m["end"] - max(ts, a - 1)
        E = (sum(connus) + nr * P) / (len(connus) + nr)
        sd = math.sqrt((sg * P * math.sqrt(nr ** 3 / 3) / 60) ** 2 + m["sd_b"] ** 2)
        return ((E - K) / sd) * (1 if fav_up else -1)

    # ---- A : vrais achats du favori
    A = []
    for W in ((30, 60, 90, 120, 180) if "--sans-A" not in sys.argv else ()):
        for (pmin, pmax) in ((0.95, 0.999), (0.90, 0.95), (0.85, 0.90)):
            for zmin in (2.5, 3, 4, 5, 6):
                L = []
                for m in M:
                    for (ts, pup, size, up, side) in m["tr"]:
                        if ts < m["end"] - W or ts > m["end"] - 1: continue
                        fav_up = pup >= 0.5; pf = pup if fav_up else 1 - pup
                        if not (side == "BUY" and up == fav_up and pmin <= pf <= pmax): continue
                        z = z_de(m, ts, fav_up)
                        if z is not None and z >= zmin:
                            L.append((pf, fav_up == m["up_gagne"])); break
                if not L: continue
                g = sum(((50 / p) * (1 - p) if ok else -50) - (50 / p) * T.FEE_RATE * p * (1 - p) for p, ok in L)
                A.append((prefixe, W, pmin, pmax, zmin, len(L), sum(1 for x in L if not x[1]), g))

    # ---- B : offre posee a T0, servie si un vendeur frappe (optimiste : prix <= offre ; prudent : prix < offre)
    B = []
    for T0 in (120, 90, 60, 30):
        for P in (0.95, 0.97, 0.98, 0.99):
            for zmin in (2.5, 3, 4):
                Lo, Lp = [], []
                for m in M:
                    t0 = m["end"] - T0
                    avant = [x for x in m["tr"] if x[0] <= t0]
                    if not avant: continue
                    fav_up = avant[-1][1] >= 0.5
                    z = z_de(m, t0, fav_up)
                    if z is None or z < zmin: continue
                    servi_o = servi_p = None
                    for (ts, pup, size, up, side) in m["tr"]:
                        if ts <= t0 or ts > m["end"] - 1: continue
                        zz = z_de(m, ts, fav_up)
                        if zz is None or zz < zmin: break            # offre annulee
                        pf = pup if fav_up else 1 - pup          # prix du favori (corrige)
                        if side == "SELL" and up == fav_up:
                            if servi_o is None and pf <= P: servi_o = ts
                            if servi_p is None and pf < P - 0.0005: servi_p = ts
                        if servi_p: break
                    ok = fav_up == m["up_gagne"]
                    if servi_o: Lo.append(ok)
                    if servi_p: Lp.append(ok)
                g = lambda L: sum(((50 / P) * (1 - P)) if ok else -50 for ok in L)
                B.append((prefixe, T0, P, zmin, len(Lo), Lo.count(False), g(Lo), len(Lp), Lp.count(False), g(Lp)))
    return A, B


def main():
    t0 = time.time()
    fin = int(time.time()) // 300 * 300 - 600
    debut = fin - JOURS * 86400
    jours = sorted({datetime.fromtimestamp(t, timezone.utc).strftime("%Y-%m-%d") for t in range(debut - 600, fin + 600, 3600)})
    jours = [j for j in jours if j < datetime.now(timezone.utc).strftime("%Y-%m-%d")]
    fin = min(fin, int(datetime.strptime(jours[-1], "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp()) + 86400 - 300)
    TA, TB, info = [], [], []
    for prefixe, sym in ACTIFS:
        try:
            a, b = etudier(prefixe, sym, jours, debut, fin)
            TA += a if isinstance(a, list) and a and isinstance(a[0], tuple) else []
            TB += b
            if a and isinstance(a[0], str): info += a
        except Exception as e:
            info.append(f"{prefixe.upper()} : erreur {str(e)[:100]}")
    rap = [f"# Pistes A et B realistes (B corrige) — {JOURS} jours ({jours[0]} -> {jours[-1]}), regle TWAP 60 s\n"] + info
    rap += ["\n## A — configurations SANS perte, classees par trades/jour (top 40)\n",
            "| Actif | Fenetre | Prix | Distance | Trades | Gain 7 j | Trades/jour |", "|---|---|---|---|---|---|---|"]
    for r in sorted([r for r in TA if r[6] == 0], key=lambda r: -r[5])[:40]:
        rap.append(f"| {r[0].upper()} | {r[1]} s | {r[2]}-{r[3]} | {r[4]} | {r[5]} | {r[7]:+.0f} $ | {r[5] / JOURS:.1f} |")
    rap += ["\n## A — configurations avec 1 a 3 pertes, top 20 par gain\n",
            "| Actif | Fenetre | Prix | Distance | Trades | Pertes | Gain 7 j | Trades/jour |", "|---|---|---|---|---|---|---|---|"]
    for r in sorted([r for r in TA if 1 <= r[6] <= 3], key=lambda r: -r[7])[:20]:
        rap.append(f"| {r[0].upper()} | {r[1]} s | {r[2]}-{r[3]} | {r[4]} | {r[5]} | {r[6]} | {r[7]:+.0f} $ | {r[5] / JOURS:.1f} |")
    rap += ["\n## B — offre posee, version PRUDENTE (servie seulement si un vendeur passe SOUS notre prix), sans perte, top 40\n",
            "| Actif | Posee a | Prix offre | Distance | Servies | Gain 7 j | Servies/jour | (optimiste : servies / pertes) |", "|---|---|---|---|---|---|---|---|"]
    for r in sorted([r for r in TB if r[8] == 0 and r[7] > 0], key=lambda r: -r[7])[:40]:
        rap.append(f"| {r[0].upper()} | T-{r[1]} s | {r[2]} | {r[3]} | {r[7]} | {r[9]:+.0f} $ | {r[7] / JOURS:.1f} | {r[4]} / {r[5]} |")
    rap += ["\n## B — tout le tableau (prudent / optimiste)\n", "| Actif | Posee a | Prix | Distance | Prudent servies | pertes | gain | Optimiste servies | pertes | gain |", "|---|---|---|---|---|---|---|---|---|---|"]
    for r in TB:
        rap.append(f"| {r[0].upper()} | T-{r[1]} | {r[2]} | {r[3]} | {r[7]} | {r[8]} | {r[9]:+.0f} | {r[4]} | {r[5]} | {r[6]:+.0f} |")
    rap.append(f"\nDuree : {time.time() - t0:.0f} s")
    open("etude/bot5min/resultat_pistes2.md", "w").write("\n".join(rap))
    print("\n".join(rap))


if __name__ == "__main__":
    main()
