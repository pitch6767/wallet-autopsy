"""Strategies separees (idees 29 et 30) — 12 jours, retard 1 s, 100 parts.
30 : fin de cycle, acheter a 0,70-0,90 quand le modele donne >= 0,93/0,95/0,97, garder jusqu'a la fin (aucun stop).
29 : teneur de marche des deux cotes au prix du modele (offres d'achat Up et Down a valeur - marge, frais maker 0),
     paires fusionnees, inventaire limite, garde jusqu'a la fin. Remplissage prudent : un vendeur doit passer 1 cent SOUS notre offre.
     Nos offres sont recalculees chaque seconde avec la proba d'il y a 1 s (plus lent que le vrai bot : 0,1 s).
"""
import sys, math, time, statistics, collections
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
sys.path.insert(0, "etude/bot5min")
import test as T
import paires as P
import solutions as S
from sorties import spot_jour, charger, dernier

JOURS = int(sys.argv[1]) if len(sys.argv) > 1 else 12
L = 1
N = 100.0
FEE = lambda p: T.FEE_RATE * p * (1 - p)
OUT = "etude/bot5min/"


def stats(R, coupe, jours_a, jours_b):
    if not R: return None
    R = sorted(R, key=lambda x: x[0])
    cum = pic = dd = 0
    for x in R:
        cum += x[1]; pic = max(pic, cum); dd = max(dd, pic - cum)
    return {"n": len(R), "net": sum(x[1] for x in R), "pertes": sum(x[1] for x in R if x[1] < 0), "nperd": sum(1 for x in R if x[1] < 0), "dd": dd,
            "ga": sum(x[1] for x in R if x[0] < coupe) / jours_a, "gb": sum(x[1] for x in R if x[0] >= coupe) / jours_b}


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

    def proba_up(m, ts):
        cache = m.setdefault("cache", {})
        if ts in cache: return cache[ts]
        r = None; P0 = prix(ts); sgk = ("sg", ts // 15)
        if sgk not in cache: cache[sgk] = T.sigma_s(SPx, ts)
        sg = cache[sgk]
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

    # ---------------- idee 30 : zone 0,70-0,90 en fin de cycle
    def fin_cycle(m, W, lo, hi, seuil):
        for (ts, up, p, size, side) in m["tr"]:
            if ts < m["end"] - W or ts > m["end"] - 1: continue
            if side != "BUY" or not (lo <= p <= hi): continue
            if seuil is not None:
                pu = proba_up(m, ts - L)
                if pu is None: continue
                if (pu if up else 1 - pu) < seuil: continue
            g = up == m["up_gagne"]
            return (m["start"], N * ((1 if g else 0) - p - FEE(p)), g)
        return None

    # ---------------- idee 29 : teneur de marche des deux cotes
    def mm(m, marge, desequilibre, arret_s, maxi):
        inv = {True: 0.0, False: 0.0}; cout = {True: 0.0, False: 0.0}
        for (ts, up, p, size, side) in m["tr"]:
            if ts < m["start"] or ts > m["end"] - arret_s: continue
            pu = proba_up(m, ts - L)
            if pu is None: continue
            # le vendeur de ce trade vend le jeton X au prix px
            if side == "SELL": X, px = up, p
            else: X, px = (not up), 1 - p
            valeur = pu if X else 1 - pu
            offre = math.floor((valeur - marge) * 100) / 100
            if offre < 0.02 or px > offre - 0.01 + 1e-9: continue
            if inv[X] - inv[not X] >= desequilibre or inv[X] >= maxi: continue
            k = min(size, maxi - inv[X], desequilibre - (inv[X] - inv[not X]))
            if k <= 0: continue
            inv[X] += k; cout[X] += k * offre
        if inv[True] + inv[False] < 1e-9: return None
        paires = min(inv[True], inv[False])
        g = m["up_gagne"]
        pnl = inv[True] * (1 if g else 0) + inv[False] * (0 if g else 1) - cout[True] - cout[False]
        return (m["start"], pnl, paires, abs(inv[True] - inv[False]))

    jours_a = (coupe - debut) / 86400; jours_b = (fin - coupe) / 86400
    rap = [f"\n## {prefixe.upper()} — {len(M)} cycles\n", "### Idee 30 — acheter en fin de cycle entre 0,70 et 0,90, garder jusqu'a la fin\n",
           "| Variante | Trades | Perdus | Gain net | Gain/jour | Pertes | Pire baisse | Gain/jour jours 1-8 | **Gain/jour jours 9-12** |", "|---|---|---|---|---|---|---|---|---|"]
    V30 = [("90 dernieres s, 0,70-0,85, SANS modele (controle)", 90, 0.70, 0.85, None)]
    for (lo, hi) in ((0.70, 0.80), (0.80, 0.85), (0.85, 0.90), (0.70, 0.85), (0.70, 0.90)):
        for se in (0.93, 0.95, 0.97):
            V30.append((f"90 dernieres s, {lo:.2f}-{hi:.2f}, modele >= {se:.2f}", 90, lo, hi, se))
    for W in (60, 120, 180):
        V30.append((f"{W} dernieres s, 0,70-0,85, modele >= 0,95", W, 0.70, 0.85, 0.95))
    for nom, W, lo, hi, se in V30:
        R = [x for x in (fin_cycle(m, W, lo, hi, se) for m in M) if x]
        r = stats(R, coupe, jours_a, jours_b)
        if r: rap.append(f"| {nom} | {r['n']} | {sum(1 for x in R if not x[2])} | {r['net']:+.0f} $ | {r['net'] / JOURS:+.0f} $ | {r['pertes']:+.0f} $ | -{r['dd']:.0f} $ | {r['ga']:+.0f} $ | **{r['gb']:+.0f} $** |")
        else: rap.append(f"| {nom} | 0 | | | | | | | |")
        print(rap[-1]); sys.stdout.flush()
    rap += ["\n### Idee 29 — teneur de marche des deux cotes au prix du modele (aucun frais, paires fusionnees)\n",
            "| Variante | Cycles servis | Cycles perdants | Gain net | Gain/jour | Pertes | Pire baisse | Paires moy. | Parts seules moy. | **Gain/jour jours 9-12** |", "|---|---|---|---|---|---|---|---|---|---|"]
    for marge in (0.03, 0.05, 0.08, 0.12):
        for deseq, arret in ((50, 10), (100, 10), (50, 60), (25, 10)):
            R = [x for x in (mm(m, marge, deseq, arret, 100) for m in M) if x]
            r = stats(R, coupe, jours_a, jours_b)
            nom = f"marge {marge:.2f}, desequilibre max {deseq} parts, arret {arret} s avant la fin"
            if r: rap.append(f"| {nom} | {r['n']} | {r['nperd']} | {r['net']:+.0f} $ | {r['net'] / JOURS:+.0f} $ | {r['pertes']:+.0f} $ | -{r['dd']:.0f} $ | {statistics.mean(x[2] for x in R):.0f} | {statistics.mean(x[3] for x in R):.0f} | **{r['gb']:+.0f} $** |")
            else: rap.append(f"| {nom} | 0 | | | | | | | | |")
            print(rap[-1]); sys.stdout.flush()
    return rap


def main():
    t0 = time.time()
    fin = int(time.time()) // 300 * 300 - 900
    debut = fin - JOURS * 86400
    jours = sorted({datetime.fromtimestamp(t, timezone.utc).strftime("%Y-%m-%d") for t in range(debut - 3700, fin + 600, 3600)})
    jours = [j for j in jours if j < datetime.now(timezone.utc).strftime("%Y-%m-%d")]
    fin = min(fin, int(datetime.strptime(jours[-1], "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp()) + 86400 - 300)
    coupe = debut + int(JOURS * 2 / 3) * 86400
    rap = [f"# Strategies separees (idees 29 et 30) — {JOURS} jours ({jours[0]} -> {jours[-1]})", "100 parts. Retard 1 s. Aucun stop."]
    for prefixe, sym in (("btc", "BTCUSDT"), ("eth", "ETHUSDT"), ("sol", "SOLUSDT"), ("xrp", "XRPUSDT")):
        try: rap += etudier(prefixe, sym, jours, debut, fin, coupe)
        except Exception as err: rap.append(f"\n{prefixe} : echec {err}")
        open(OUT + "resultat_strats.md", "w").write("\n".join(rap))
    rap.append(f"\nDuree : {time.time() - t0:.0f} s")
    open(OUT + "resultat_strats.md", "w").write("\n".join(rap))
    print("\n".join(rap))


if __name__ == "__main__":
    main()
