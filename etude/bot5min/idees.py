"""Idees pour eviter les pertes de V1 (reglage A) — BTC et ETH, 12 jours, retard 1 s, 100 parts.
Idee 3 : perp trop cher / pas assez cher par rapport au spot (ecart perp-spot anormal)
Idee 4 : tres gros ordres sur le perp Binance
Idee 5 : regime du marche (tendance ou allers-retours), ratio de variance sur 30 min
Idee 6 : mise selon l'avance du modele
Idee 7 : encaisser une partie en route / stop suiveur
Idee 1 (approximation avec les echanges Polymarket) : achats agressifs du cote oppose
Seuils choisis sur les jours 1-8 seulement ; colonne « jours 9-12 » = periode jamais vue.
"""
import sys, math, time, statistics, collections
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
sys.path.insert(0, "etude/bot5min")
import test as T
import paires as P
import solutions as S
from sorties import spot_jour, perp_jour, charger, dernier

JOURS = int(sys.argv[1]) if len(sys.argv) > 1 else 12
L = 1
N = 100.0
FEE = lambda p: T.FEE_RATE * p * (1 - p)
OUT = "etude/bot5min/"


def q(vals, x):
    v = sorted(vals)
    return v[min(len(v) - 1, max(0, int(len(v) * x)))] if v else None


def etudier(prefixe, sym, jours, debut, fin, coupe):
    t0 = time.time()
    SP = charger(spot_jour, sym, jours)
    SPx = {s: (v[0], v[0]) for s, v in SP.items()}
    PE = charger(perp_jour, sym, jours)
    print(prefixe, "binance charge", len(SP), len(PE), "(%.0fs)" % (time.time() - t0)); sys.stdout.flush()
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
        r = None; P0 = prix(ts); sgk = ts // 15
        if ("sg", sgk) not in cache: cache[("sg", sgk)] = T.sigma_s(SPx, ts)
        sg = cache[("sg", sgk)]
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

    # ---------- signaux
    def basis(t):
        s_ = dernier(SP, t, 0, 3); p_ = dernier(PE, t, 0, 3)
        return (p_ / s_ - 1) * 1e4 if s_ and p_ else None
    cb = {}
    def exces(t):                                  # ecart perp-spot (points de base) moins sa mediane des 5 dernieres minutes
        if t in cb: return cb[t]
        b = basis(t); ref = [x for x in (basis(x) for x in range(t - 300, t - 10, 10)) if x is not None]
        cb[t] = (b - statistics.median(ref)) if b is not None and len(ref) > 5 else None
        return cb[t]
    def gros(t, d, k, contre):                     # plus gros echange unique (USD) sur k secondes, contre nous ou pour nous
        col = (5 if d > 0 else 4) if contre else (4 if d > 0 else 5)
        v = [PE[s][col] for s in range(t - k + 1, t + 1) if s in PE]
        return max(v) if v else 0
    cv = {}
    def vr(t, h=15, fen=1800):                     # ratio de variance : >1 tendance, <1 allers-retours
        k = (t // 60, h, fen)
        if k in cv: return cv[k]
        p_ = [prix(s) for s in range(t - fen, t + 1)]
        p_ = [x for x in p_ if x]
        r = None
        if len(p_) > fen * 0.8:
            r1 = [math.log(p_[i + 1] / p_[i]) for i in range(len(p_) - 1)]
            rh = [math.log(p_[i + h] / p_[i]) for i in range(0, len(p_) - h, h)]
            v1 = statistics.pvariance(r1)
            r = statistics.pvariance(rh) / (h * v1) if v1 > 0 else None
        cv[k] = r
        return r

    def sim(m, v):
        cache = m.setdefault("cache", {}); A = None; invB = [0.0, 0.0]; pnl = 0.0; etat = "rien"; dern = {True: 0.5, False: 0.5}
        ruban = collections.deque()                # (ts, pression_vers_up, parts)
        def pression(up_, a, b):
            return sum(x[2] for x in ruban if a <= x[0] <= b and x[1] == up_)
        for (ts, up, p, size, side) in m["tr"]:
            if ts > m["end"] - 1: break
            ruban.append((ts, (side == "BUY") == up, size))
            while ruban and ruban[0][0] < ts - 30: ruban.popleft()
            if ts < m["start"]: continue
            dern[up] = p; dern[not up] = 1 - p
            pu = proba_up(m, ts - L, cache)
            if pu is None: continue
            if A is None:
                if side == "BUY" and 0.55 <= p <= 0.56:
                    fair = pu if up else 1 - pu
                    if fair >= 0.63:
                        a0, b0 = prix(ts - L - 5), prix(ts - L)
                        if not (a0 and b0 and ((b0 - a0) * (1 if up else -1)) > 0): continue
                        d = 1 if up else -1
                        f = v.get("refuser")
                        if f and f(ts - L, d, up, pression): continue
                        w = v["mise"](fair - p) if "mise" in v else 1.0
                        A = {"cote": up, "prix": p, "q": N * w, "q0": N * w, "fair0": fair, "ts": ts, "max": p, "d": d}
                        pnl -= A["q"] * FEE(p); etat = "jambe"
                        if "noter" in v: v["noter"](m, ts - L, d, fair - p)
                continue
            c = A["cote"]; fairA = pu if c else 1 - pu
            A["max"] = max(A["max"], dern[c])
            if side == "SELL": O, qq = up, p
            elif side == "BUY": O, qq = (not up), 1 - p
            else: O = None
            if O is not None and O != c and invB[0] < A["q"]:
                offre = min(math.floor(((1 - fairA) - 0.08) * 100) / 100, 0.43)
                if offre >= 0.02 and qq <= offre - 0.01 + 1e-9:
                    k = min(size, A["q"] - invB[0]); invB[0] += k; invB[1] += k * offre
            if invB[0] >= A["q"] - 1e-9:
                pnl += A["q"] * (1 - A["prix"]) - invB[1]; etat = "paire"; A["fini"] = True; break
            # --- alarmes de sortie (signal vu a ts - L, ou ruban Polymarket deja vu avant ts - L)
            alarme = False
            if "alarme" in v and ts - L > A["ts"]:
                alarme = v["alarme"](ts - L, A["d"], c, pression, A["ts"])
            if fairA < A["fair0"] - 0.15 or alarme:
                pv = max(0.01, dern[c] - 0.01); qa = A["q"] - invB[0]
                pnl += qa * (pv - FEE(pv)) - qa * A["prix"] + invB[0] * (1 - A["prix"]) - invB[1]
                etat = "alarme" if alarme and not fairA < A["fair0"] - 0.15 else "stop"; A["fini"] = True; A["aurait"] = (c == m["up_gagne"]); break
            # --- encaissement partiel / stop suiveur
            if "partiel" in v and not A.get("partiel") and up == c and p >= v["partiel"][0] and invB[0] < 1e-9:
                lv, fr = v["partiel"]; k = A["q"] * fr
                pnl += k * (lv - FEE(lv) - A["prix"]); A["q"] -= k; A["partiel"] = True
            if "suiveur" in v and A["max"] >= v["suiveur"] and dern[c] <= A["prix"] + 0.01 and invB[0] < 1e-9:
                pv = max(0.01, dern[c] - 0.01); qa = A["q"]
                pnl += qa * (pv - FEE(pv) - A["prix"]); etat = "suiveur"; A["fini"] = True; break
            if up == c and p >= 0.90 and invB[0] < 1e-9:
                pnl += A["q"] * (0.90 - FEE(0.90) - A["prix"]); etat = "sortie"; A["fini"] = True; break
        if A is None: return None
        if not A.get("fini"):
            g = A["cote"] == m["up_gagne"]; qa = A["q"] - invB[0]
            pnl += qa * ((1 if g else 0) - A["prix"]) + invB[0] * (1 - A["prix"]) - invB[1]
            etat = "fin " + ("gagnee" if g else "perdue")
        return {"pnl": pnl, "etat": etat, "aurait": A.get("aurait"), "ts": A["ts"], "max": A["max"], "q0": A["q0"]}

    # ---------- passe de reference : distribution des signaux a l'entree (jours 1-8 pour les seuils)
    F = {"exces": [], "vr": [], "vr60": [], "avance": [], "gros_contre": [], "gros_pour": []}
    def noter(m, t, d, av):
        if t >= coupe: return
        e = exces(t); r = vr(t); r6 = vr(t, 60, 3600)
        if e is not None: F["exces"].append(d * e)
        if r is not None: F["vr"].append(r)
        if r6 is not None: F["vr60"].append(r6)
        F["avance"].append(av); F["gros_contre"].append(gros(t, d, 5, True)); F["gros_pour"].append(gros(t, d, 10, False))
    REF = [x for x in (sim(m, {"noter": noter}) for m in M) if x]
    print(prefixe, "reference", len(REF), "(%.0fs)" % (time.time() - t0)); sys.stdout.flush()
    Q = lambda k, x: q(F[k], x)
    ex67, ex80, ex90, ex20 = Q("exces", .67), Q("exces", .80), Q("exces", .90), Q("exces", .20)
    exabs90 = q([abs(x) for x in F["exces"]], .90)
    vr20, vr33, vr50, vr80 = Q("vr", .2), Q("vr", .33), Q("vr", .5), Q("vr", .8)
    v6_20, v6_33 = Q("vr60", .2), Q("vr60", .33)
    g67, g80, g90 = Q("gros_contre", .67), Q("gros_contre", .80), Q("gros_contre", .90)
    gp50 = Q("gros_pour", .5)
    moy_av = statistics.mean(F["avance"]); med_av = statistics.median(F["avance"])
    moy_av2 = statistics.mean(a * a for a in F["avance"])
    k_ = lambda x: f"{x / 1000:.0f} k$"

    def ex_ok(t): return exces(t)
    variantes = [
        ("Reference V1 (stop -15 pts, sortie 0,90)", {}),
        # idee 3
        (f"3. Refuser si perp en avance dans notre sens > {ex67:.2f} pb (tiers haut)", {"refuser": lambda t, d, up, pr: (exces(t) is not None and d * exces(t) > ex67)}),
        (f"3. Refuser si perp en avance > {ex80:.2f} pb (20 % haut)", {"refuser": lambda t, d, up, pr: (exces(t) is not None and d * exces(t) > ex80)}),
        (f"3. Refuser si perp en avance > {ex90:.2f} pb (10 % haut)", {"refuser": lambda t, d, up, pr: (exces(t) is not None and d * exces(t) > ex90)}),
        (f"3. Refuser si perp en retard < {ex20:.2f} pb (20 % bas)", {"refuser": lambda t, d, up, pr: (exces(t) is not None and d * exces(t) < ex20)}),
        (f"3. Sortir si l'ecart perp-spot passe contre nous de {exabs90:.2f} pb", {"alarme": lambda t, d, c, pr, te: (exces(t) is not None and d * exces(t) < -exabs90)}),
        # idee 4
        (f"4. Refuser si gros ordre perp contre nous (5 s) > {k_(g67)}", {"refuser": lambda t, d, up, pr: gros(t, d, 5, True) > g67}),
        (f"4. Refuser si gros ordre contre > {k_(g80)}", {"refuser": lambda t, d, up, pr: gros(t, d, 5, True) > g80}),
        (f"4. Refuser si gros ordre contre > {k_(g90)}", {"refuser": lambda t, d, up, pr: gros(t, d, 5, True) > g90}),
        (f"4. Exiger un gros ordre pour nous (10 s) > {k_(gp50)}", {"refuser": lambda t, d, up, pr: gros(t, d, 10, False) <= gp50}),
        (f"4. Sortir si gros ordre contre nous > {k_(g80)} pendant le trade", {"alarme": lambda t, d, c, pr, te: gros(t, d, 2, True) > g80}),
        (f"4. Sortir si gros ordre contre nous > {k_(g90)} pendant le trade", {"alarme": lambda t, d, c, pr, te: gros(t, d, 2, True) > g90}),
        # idee 5
        (f"5. Refuser si allers-retours (ratio 30 min < {vr20:.2f}, 20 % bas)", {"refuser": lambda t, d, up, pr: (vr(t) is not None and vr(t) < vr20)}),
        (f"5. Refuser si ratio 30 min < {vr33:.2f} (tiers bas)", {"refuser": lambda t, d, up, pr: (vr(t) is not None and vr(t) < vr33)}),
        (f"5. Refuser si ratio 30 min < {vr50:.2f} (moitie basse)", {"refuser": lambda t, d, up, pr: (vr(t) is not None and vr(t) < vr50)}),
        (f"5. Refuser si forte tendance (ratio > {vr80:.2f}, controle)", {"refuser": lambda t, d, up, pr: (vr(t) is not None and vr(t) > vr80)}),
        (f"5. Refuser si ratio 1 h (pas 60 s) < {v6_20:.2f}", {"refuser": lambda t, d, up, pr: (vr(t, 60, 3600) is not None and vr(t, 60, 3600) < v6_20)}),
        (f"5. Refuser si ratio 1 h < {v6_33:.2f}", {"refuser": lambda t, d, up, pr: (vr(t, 60, 3600) is not None and vr(t, 60, 3600) < v6_33)}),
        # idee 6
        ("6. Mise proportionnelle a l'avance du modele (meme mise moyenne)", {"mise": lambda av: max(0.25, av / moy_av)}),
        ("6. Mise selon l'avance au carre (meme mise moyenne)", {"mise": lambda av: max(0.25, av * av / moy_av2)}),
        ("6. Demi-mise si avance < mediane, 1,5x sinon", {"mise": lambda av: 0.5 if av < med_av else 1.5}),
        # idee 7
        ("7. Vendre la moitie a 0,70, le reste a 0,90", {"partiel": (0.70, 0.5)}),
        ("7. Vendre la moitie a 0,75, le reste a 0,90", {"partiel": (0.75, 0.5)}),
        ("7. Vendre 1/3 a 0,70, le reste a 0,90", {"partiel": (0.70, 1 / 3)}),
        ("7. Moitie a 0,70 + reste sorti a 0,56 s'il redescend", {"partiel": (0.70, 0.5), "suiveur": 0.70}),
        ("7. Stop suiveur seul : apres 0,75, sortir a 0,56 s'il redescend", {"suiveur": 0.75}),
        ("7. Stop suiveur seul : apres 0,70, sortir a 0,56 s'il redescend", {"suiveur": 0.70}),
        # idee 1 approximee par les echanges Polymarket
        ("1. Sortir si achats agressifs du cote oppose > 100 parts en 3 s", {"alarme": lambda t, d, c, pr, te: pr(not c, t - 2, t) > 100}),
        ("1. Sortir si achats agressifs du cote oppose > 250 parts en 3 s", {"alarme": lambda t, d, c, pr, te: pr(not c, t - 2, t) > 250}),
        ("1. Sortir si achats agressifs du cote oppose > 500 parts en 3 s", {"alarme": lambda t, d, c, pr, te: pr(not c, t - 2, t) > 500}),
        ("1. Refuser si achats du cote oppose > 250 parts dans les 10 s avant", {"refuser": lambda t, d, up, pr: pr(not up, t - 9, t) > 250}),
    ]
    jours_a = (coupe - debut) / 86400; jours_b = (fin - coupe) / 86400
    rap = [f"\n## {prefixe.upper()} — {len(M)} cycles, {JOURS} jours, 100 parts, retard 1 s\n",
           f"Seuils choisis sur les jours 1-{jours_a:.0f} ; les jours {jours_a + 1:.0f}-{JOURS} n'ont jamais servi a les choisir.\n",
           "| Idee | Trades | Gain net | Gain/jour | Pertes totales | Pire baisse | Gain/jour jours 1-8 | **Gain/jour jours 9-12 (jamais vus)** | Mise moy. |",
           "|---|---|---|---|---|---|---|---|---|"]
    ref = None
    for nom, v in variantes:
        R = REF if not v else [x for x in (sim(m, v) for m in M) if x]
        cum = pic = dd = 0
        for x in sorted(R, key=lambda x: x["ts"]):
            cum += x["pnl"]; pic = max(pic, cum); dd = max(dd, pic - cum)
        net = sum(x["pnl"] for x in R); per = sum(x["pnl"] for x in R if x["pnl"] < 0)
        ga = sum(x["pnl"] for x in R if x["ts"] < coupe) / jours_a; gb = sum(x["pnl"] for x in R if x["ts"] >= coupe) / jours_b
        if ref is None: ref = (net, per, ga, gb)
        rap.append(f"| {nom} | {len(R)} | {net:+.0f} $ ({net - ref[0]:+.0f}) | {net / JOURS:+.0f} $ | {per:+.0f} $ ({per - ref[1]:+.0f}) | -{dd:.0f} $ | {ga:+.0f} $ ({ga - ref[2]:+.0f}) | **{gb:+.0f} $ ({gb - ref[3]:+.0f})** | {statistics.mean(x['q0'] for x in R) * 0.55:.0f} $ |")
        print(rap[-1]); sys.stdout.flush()
    # diagnostic idee 7 : jusqu'ou montent les trades avant de mal finir
    rap += ["\n### Idee 7 — jusqu'ou le jeton est monte avant la sortie (reference)\n", "| Issue | Trades | a touche 0,65 | 0,70 | 0,75 | 0,80 |", "|---|---|---|---|---|---|"]
    for et in sorted({x["etat"] for x in REF}):
        G = [x for x in REF if x["etat"] == et]
        rap.append(f"| {et} | {len(G)} | " + " | ".join(f"{sum(1 for x in G if x['max'] >= lv)} ({100 * sum(1 for x in G if x['max'] >= lv) / len(G):.0f} %)" for lv in (0.65, 0.70, 0.75, 0.80)) + " |")
    rap.append(f"\nReperes (jours 1-8) : ecart perp-spot a l'entree mediane {Q('exces', .5):.2f} pb ; plus gros ordre contre nous (5 s) median {k_(Q('gros_contre', .5))} ; ratio de variance 30 min median {vr50:.2f}, 1 h median {Q('vr60', .5):.2f} ; avance moyenne du modele {moy_av:.3f}.")
    return rap


def main():
    t0 = time.time()
    fin = int(time.time()) // 300 * 300 - 900
    debut = fin - JOURS * 86400
    jours = sorted({datetime.fromtimestamp(t, timezone.utc).strftime("%Y-%m-%d") for t in range(debut - 3700, fin + 600, 3600)})
    jours = [j for j in jours if j < datetime.now(timezone.utc).strftime("%Y-%m-%d")]
    fin = min(fin, int(datetime.strptime(jours[-1], "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp()) + 86400 - 300)
    coupe = debut + int(JOURS * 2 / 3) * 86400
    rap = [f"# Idees anti-pertes pour V1 — {JOURS} jours ({jours[0]} -> {jours[-1]})",
           "Entre parentheses : difference avec la reference. Gains pour 100 parts par trade (environ 55 $ de mise)."]
    for prefixe, sym in (("btc", "BTCUSDT"), ("eth", "ETHUSDT")):
        rap += etudier(prefixe, sym, jours, debut, fin, coupe)
        open(OUT + "resultat_idees.md", "w").write("\n".join(rap))
    rap.append(f"\nDuree : {time.time() - t0:.0f} s")
    open(OUT + "resultat_idees.md", "w").write("\n".join(rap))
    print("\n".join(rap))


if __name__ == "__main__":
    main()
