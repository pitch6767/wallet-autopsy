"""Idee 1 — valeur relative entre cryptos sur les marches 5 min Polymarket.
Structure : acheter Up d'une crypto A + Down d'une crypto B (ou l'inverse) dans le MEME cycle, garder jusqu'a la fin (pas de stop).
Paiement : 1 $ si les deux vont dans le meme sens, 2 $ si A monte et B baisse, 0 $ seulement si A baisse et B monte.
Prix d'achat estime prudemment : dernier prix echange (moins de 3 s) + 1 cent, plus frais taker, execution 1 s apres le signal.
"""
import sys, math, time, statistics, itertools
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
sys.path.insert(0, "etude/bot5min")
import test as T
import paires as P
import solutions as S
from sorties import spot_jour, charger, dernier

JOURS = int(sys.argv[1]) if len(sys.argv) > 1 else 12
N = 100.0
FEE = lambda p: T.FEE_RATE * p * (1 - p)
OUT = "etude/bot5min/"
ACTIFS = [("btc", "BTCUSDT"), ("eth", "ETHUSDT"), ("sol", "SOLUSDT"), ("xrp", "XRPUSDT"), ("doge", "DOGEUSDT"), ("bnb", "BNBUSDT")]


def preparer(prefixe, sym, jours, debut, fin):
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

    def proba_up(m, ts, sgc):
        P0 = prix(ts); k = ts // 15
        if k not in sgc: sgc[k] = T.sigma_s(SPx, ts)
        sg = sgc[k]
        if not (P0 and sg and m["sd_b"]): return np.nan
        a = m["end"] - 59
        if ts >= a:
            connus = [x for x in (prix(s) for s in range(a, ts + 1)) if x]
            nr = m["end"] - ts
            E = (sum(connus) + nr * P0) / (len(connus) + nr); var = (sg * P0) ** 2 * nr ** 3 / 3 / 3600
        else:
            E = P0; var = (sg * P0) ** 2 * ((a - ts) + 20)
        return T.phi((E - m["K"]) / math.sqrt(var + m["sd_b"] ** 2))

    out = {}
    for m in M:
        up = np.full(300, np.nan); vu = np.full(300, -99)
        for (ts, u, p, size, side) in m["tr"]:
            k = ts - m["start"]
            if 0 <= k < 300: up[k] = p if u else 1 - p; vu[k] = k
        # report du dernier prix connu et de l'instant ou il a ete vu
        for k in range(1, 300):
            if np.isnan(up[k]): up[k] = up[k - 1]; vu[k] = vu[k - 1]
        sgc = {}
        pm = np.array([proba_up(m, m["start"] + k - 1, sgc) for k in range(300)])
        out[m["start"]] = {"up": up, "vu": vu, "pm": pm, "gagne": m["up_gagne"]}
    print(prefixe, "pret", len(out), "cycles (%.0fs)" % (time.time() - t0)); sys.stdout.flush()
    return out


def simuler(A, B, v, coupe):
    """renvoie la liste des trades (ts, pnl, paiement, cout) pour un couple"""
    R = []
    for st in sorted(set(A) & set(B)):
        a, b = A[st], B[st]
        k0, k1 = v.get("fenetre", (5, 290))
        for k in range(k0, k1):
            if v.get("fixe") is not None and k != v["fixe"]: continue
            if a["vu"][k] < k - 3 or b["vu"][k] < k - 3: continue
            ua, ub = a["up"][k], b["up"][k]
            if not (0.03 < ua < 0.97 and 0.03 < ub < 0.97): continue
            # deux sens possibles : (A Up + B Down) ou (A Down + B Up)
            sens = 1 if ua <= ub else -1
            pa = ua if sens == 1 else 1 - ua; pb = (1 - ub) if sens == 1 else ub
            cout_sig = pa + pb + 0.02 + FEE(pa + 0.01) + FEE(pb + 0.01)
            if v.get("fixe") is None and cout_sig > 1 - v["marge"]: continue
            if "modele" in v:
                ma, mb = a["pm"][k], b["pm"][k]
                if np.isnan(ma) or np.isnan(mb): continue
                val = (ma if sens == 1 else 1 - ma) + ((1 - mb) if sens == 1 else mb)
                if val < cout_sig + v["modele"]: continue
            # execution 1 s plus tard, au prix d'alors
            e = k + 1
            ea = a["up"][e] if sens == 1 else 1 - a["up"][e]; eb = (1 - b["up"][e]) if sens == 1 else b["up"][e]
            ea += 0.01; eb += 0.01
            cout = ea + eb + FEE(ea) + FEE(eb)
            gA = a["gagne"] if sens == 1 else not a["gagne"]; gB = (not b["gagne"]) if sens == 1 else b["gagne"]
            paie = int(gA) + int(gB)
            pnl = N * (paie - cout); issue = "fin"
            if "sortie" in v:                   # revendre les deux jambes si la structure vaut cout + x
                for j in range(e + 1, 299):
                    if a["vu"][j] < j - 3 or b["vu"][j] < j - 3: continue
                    va = (a["up"][j] if sens == 1 else 1 - a["up"][j]) - 0.01; vb = ((1 - b["up"][j]) if sens == 1 else b["up"][j]) - 0.01
                    net = va + vb - FEE(va) - FEE(vb)
                    if net >= cout + v["sortie"]:
                        pnl = N * (net - cout); issue = "sortie"; break
            R.append((st, pnl, paie, cout, issue))
            break
    return R


def resume(R, coupe, jours_a, jours_b):
    if not R: return None
    R = sorted(R)
    cum = pic = dd = 0
    for x in R:
        cum += x[1]; pic = max(pic, cum); dd = max(dd, pic - cum)
    fins = [x for x in R if x[4] == "fin"]
    return {"n": len(R), "net": sum(x[1] for x in R), "pertes": sum(x[1] for x in R if x[1] < 0), "nperd": sum(1 for x in R if x[1] < 0),
            "p0": sum(1 for x in fins if x[2] == 0), "p1": sum(1 for x in fins if x[2] == 1), "p2": sum(1 for x in fins if x[2] == 2),
            "cout": statistics.mean(x[3] for x in R), "dd": dd,
            "ga": sum(x[1] for x in R if x[0] < coupe) / jours_a, "gb": sum(x[1] for x in R if x[0] >= coupe) / jours_b}


def main():
    t0 = time.time()
    fin = int(time.time()) // 300 * 300 - 900
    debut = fin - JOURS * 86400
    jours = sorted({datetime.fromtimestamp(t, timezone.utc).strftime("%Y-%m-%d") for t in range(debut - 3700, fin + 600, 3600)})
    jours = [j for j in jours if j < datetime.now(timezone.utc).strftime("%Y-%m-%d")]
    fin = min(fin, int(datetime.strptime(jours[-1], "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp()) + 86400 - 300)
    coupe = debut + int(JOURS * 2 / 3) * 86400
    jours_a = (coupe - debut) / 86400; jours_b = (fin - coupe) / 86400
    D = {}
    for prefixe, sym in ACTIFS:
        try: D[prefixe] = preparer(prefixe, sym, jours, debut, fin)
        except Exception as err: print("echec", prefixe, err)
    variantes = [
        ("Sans condition (a 60 s du debut, sens le moins cher) — controle", {"fixe": 60}),
        ("Structure a moins de 1,00 $ (frais compris)", {"marge": 0.0}),
        ("Structure a moins de 0,97 $", {"marge": 0.03}),
        ("Structure a moins de 0,94 $", {"marge": 0.06}),
        ("Structure a moins de 0,90 $", {"marge": 0.10}),
        ("Structure a moins de 0,85 $", {"marge": 0.15}),
        ("Moins de 0,97 $ ET le modele dit qu'elle vaut 5 cents de plus", {"marge": 0.03, "modele": 0.05}),
        ("Moins de 0,97 $ ET le modele dit qu'elle vaut 10 cents de plus", {"marge": 0.03, "modele": 0.10}),
        ("Moins de 1,00 $ ET le modele dit 10 cents de plus", {"marge": 0.0, "modele": 0.10}),
        ("Moins de 0,94 $, revendue si elle gagne 8 cents", {"marge": 0.06, "sortie": 0.08}),
        ("Moins de 0,94 $, seulement entre 30 s et 4 min 30 de cycle", {"marge": 0.06, "fenetre": (30, 270)}),
        ("Moins de 0,94 $, seulement dans les 2 dernieres minutes", {"marge": 0.06, "fenetre": (180, 290)}),
    ]
    rap = [f"# Idee 1 — valeur relative entre cryptos (Up d'une + Down de l'autre, meme cycle) — {JOURS} jours ({jours[0]} -> {jours[-1]})",
           "100 parts par jambe. Prix = dernier echange + 1 cent + frais taker, execution 1 s apres le signal. Une structure par couple et par cycle, gardee jusqu'a la fin (aucun stop).",
           "Paiement par part : 0 $ (A et B ont diverge dans le mauvais sens), 1 $ (meme sens), 2 $ (diverge dans le bon sens).\n"]
    couples = list(itertools.combinations([p for p, _ in ACTIFS if p in D], 2))
    rap += ["## Tous les couples ensemble\n",
            "| Variante | Structures | Gain net | Gain/jour | Pertes | Structures perdantes | Paiement 0 / 1 / 2 | Cout moyen | Pire baisse | Gain/jour jours 1-8 | **Gain/jour jours 9-12** |",
            "|---|---|---|---|---|---|---|---|---|---|---|"]
    detail = {}
    for nom, v in variantes:
        tout = []
        for (x, y) in couples:
            R = simuler(D[x], D[y], v, coupe)
            detail[(nom, x, y)] = resume(R, coupe, jours_a, jours_b)
            tout += R
        r = resume(tout, coupe, jours_a, jours_b)
        if r:
            rap.append(f"| {nom} | {r['n']} | {r['net']:+.0f} $ | {r['net'] / JOURS:+.0f} $ | {r['pertes']:+.0f} $ | {r['nperd']} ({100 * r['nperd'] / r['n']:.0f} %) | {r['p0']} / {r['p1']} / {r['p2']} | {r['cout']:.3f} $ | -{r['dd']:.0f} $ | {r['ga']:+.0f} $ | **{r['gb']:+.0f} $** |")
        else:
            rap.append(f"| {nom} | 0 | | | | | | | | | |")
        print(rap[-1]); sys.stdout.flush()
    for nom, _ in variantes[1:]:
        rap += [f"\n## Par couple — {nom}\n", "| Couple | Structures | Gain net | Gain/jour | Perdantes | Paiement 0 / 1 / 2 | Gain/jour jours 9-12 |", "|---|---|---|---|---|---|---|"]
        for (x, y) in couples:
            r = detail[(nom, x, y)]
            if r: rap.append(f"| {x.upper()}/{y.upper()} | {r['n']} | {r['net']:+.0f} $ | {r['net'] / JOURS:+.0f} $ | {r['nperd']} ({100 * r['nperd'] / r['n']:.0f} %) | {r['p0']} / {r['p1']} / {r['p2']} | {r['gb']:+.0f} $ |")
    rap.append(f"\nDuree : {time.time() - t0:.0f} s")
    open(OUT + "resultat_rv.md", "w").write("\n".join(rap))
    print("\n".join(rap))


if __name__ == "__main__":
    main()
