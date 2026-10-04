"""Re-test avec la VRAIE regle : moyenne Chainlink 60 s a la fin >= moyenne 60 s au debut.
Distance calculee sur la moyenne attendue (partie deja connue + partie restante), Binance 1 s comme approximation de Chainlink."""
import sys, math, statistics, time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
sys.path.insert(0, "etude/bot5min")
import test as T

JOURS = int(sys.argv[1]) if len(sys.argv) > 1 else 14
OUT = "etude/bot5min/"


def twap(px, a, b):
    v = [T.prix(px, s) for s in range(a, b + 1)]
    v = [x for x in v if x]
    return sum(v) / len(v) if v else None


def main():
    t0 = time.time()
    fin = int(time.time()) // 300 * 300 - 600
    debut = fin - JOURS * 86400
    jours = sorted({datetime.fromtimestamp(t, timezone.utc).strftime("%Y-%m-%d") for t in range(debut - 600, fin + 600, 3600)})
    jours = [j for j in jours if j < datetime.now(timezone.utc).strftime("%Y-%m-%d")]
    fin = min(fin, int(datetime.strptime(jours[-1], "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp()) + 86400 - 300)
    BTC = T.binance("BTCUSDT", jours)
    with ThreadPoolExecutor(12) as ex:
        M = sorted([m for m in ex.map(T.marche, range(debut, fin, 300)) if m], key=lambda m: m["start"])
    def tr(m):
        try: m["trades"] = T.trades(m)
        except Exception: m["trades"] = []
        return m
    with ThreadPoolExecutor(10) as ex:
        M = list(ex.map(tr, M))
    print("marches", len(M), "(%.0fs)" % (time.time() - t0)); sys.stdout.flush()

    # ecart Binance(USDT) / Chainlink(USD) mesure sur les moyennes d'ouverture des marches precedents
    hist, ok, ko = [], 0, 0
    for m in M:
        kp = float(m["strike"]) if m["strike"] is not None else None
        tb = twap(BTC, m["start"] - 59, m["start"])
        m["base"] = statistics.median(hist[-12:]) if len(hist) >= 3 else 0
        if kp and tb:
            hist.append(tb - kp)
        m["K"] = (kp + m["base"]) if kp else None
        tf = twap(BTC, m["end"] - 59, m["end"])
        if m["K"] and tf:
            if (tf >= m["K"]) == m["up_gagne"]: ok += 1
            else: ko += 1

    def entrees(m, W, reel):
        out = []
        for (ts, pup, size, wal, up, side) in m["trades"]:
            if ts < m["end"] - W or ts > m["end"] - 1:
                continue
            fav_up = pup >= 0.5
            pf = pup if fav_up else 1 - pup
            if reel and not (side == "BUY" and up == fav_up):
                continue
            if not reel and not (side == "SELL" and up == fav_up):   # offre posee : un vendeur frappe
                continue
            if 0.94 <= pf <= 0.99:
                out.append((ts, pf, fav_up))
        return out

    def eval_z(m, ts, fav_up):
        K = m["K"]; P = T.prix(BTC, ts); sg = T.sigma_s(BTC, ts)
        if not (K and P and sg):
            return None
        a = m["end"] - 59
        connus = [T.prix(BTC, s) for s in range(a, ts + 1)] if ts >= a else []
        connus = [x for x in connus if x]
        nr = m["end"] - max(ts, a - 1)
        E = (sum(connus) + nr * P) / (len(connus) + nr)
        sd = sg * P * math.sqrt(nr ** 3 / 3) / 60
        return ((E - K) / sd) * (1 if fav_up else -1)

    rap = [f"# Re-test REGLE TWAP 60 s — {len(M)} marches, {JOURS} jours ({jours[0]} -> {jours[-1]})\n",
           f"Controle : la moyenne Binance 60 s (corrigee) donne le bon gagnant dans {ok}/{ok + ko} marches ({100 * ok / max(1, ok + ko):.2f} %).\n",
           "Gain avec mise fixe 50 $ ; colonne « avec 1/3 réinvesti » = capital 200 $, 1/3 du gain ajouté à la mise, 2/3 en réserve.\n"]
    for nom, reel in (("A — vrais achats du favori (prix vendeur)", True), ("B — offre posée remplie par un vendeur", False)):
        for W in (30, 60):
            rap.append(f"\n## {nom}, {W} dernieres secondes\n")
            rap.append("| Distance mini (TWAP) | Trades | Pertes | Gain mise fixe | Gain avec 1/3 réinvesti | Trades/jour |\n|---|---|---|---|---|---|")
            for zmin in (1.0, 1.5, 2.0, 2.5, 3.0, 4.0):
                L = []
                for m in M:
                    for (ts, p, fav_up) in entrees(m, W, reel):
                        z = eval_z(m, ts, fav_up)
                        if z is not None and z >= zmin and T.phi(z) >= p + 0.01:
                            L.append((ts, p, fav_up == m["up_gagne"], reel)); break
                fixe = 0; cap, mise, res = 200, 50, 0
                for (ts, p, g, r) in sorted(L):
                    f = (50 / p) * T.FEE_RATE * p * (1 - p) if r else 0
                    fixe += ((50 / p) * (1 - p) if g else -50) - f
                    mm = min(mise, cap - res); parts = mm / p
                    net = (parts * (1 - p) if g else -mm) - (parts * T.FEE_RATE * p * (1 - p) if r else 0)
                    cap += net
                    if net >= 0: res += net * 2 / 3; mise += net / 3
                    mise = min(mise, cap - res)
                rap.append("| %.1f | %d | %d | %+.0f $ | %+.0f $ | %.1f |" % (zmin, len(L), sum(1 for x in L if not x[2]), fixe, cap - 200, len(L) / JOURS))
    rap.append(f"\nDuree : {time.time() - t0:.0f} s")
    open(OUT + "resultat_twap.md", "w").write("\n".join(rap))
    print("\n".join(rap))


if __name__ == "__main__":
    main()
