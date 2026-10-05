"""Paires BTC 5 min, version « a valeur » (05.10.2026) — vrais echanges Polymarket + Binance 1 s, regle TWAP 60 s.
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

    def v2(m, Mg, sortie90, prudent=True):
        cache = {}
        inv = {True: [0.0, 0.0], False: [0.0, 0.0]}     # parts, cout
        pnl, etat, fini = 0.0, "rien", False
        dec = 0.01 if prudent else 0.0
        for (ts, up, p, size, side) in m["tr"]:
            if ts < m["start"] or ts > m["end"] - 1 or fini: continue
            pu = proba_up(m, ts, cache)
            if pu is None: continue
            # vendeur de l'issue O a prix q
            if side == "SELL": O, q = up, p
            elif side == "BUY": O, q = (not up), 1 - p
            else: continue
            fair = pu if O else 1 - pu
            offre = math.floor((fair - Mg) * 100) / 100
            if offre >= 0.02 and q <= offre - dec + 1e-9 and inv[O][0] < N:
                k = min(size, N - inv[O][0]); inv[O][0] += k; inv[O][1] += k * offre
                etat = "jambe"
            k = min(inv[True][0], inv[False][0])
            if k > 1e-9:
                for c in (True, False):
                    cu = inv[c][1] / inv[c][0]; pnl -= cu * k; inv[c][0] -= k; inv[c][1] -= cu * k
                pnl += k; etat = "paire"
            if sortie90:
                for c in (True, False):
                    if inv[c][0] > 1e-9 and inv[not c][0] < 1e-9 and up == c and p >= 0.90:
                        pnl += inv[c][0] * (0.90 - FEE(0.90)) - inv[c][1]; inv[c] = [0.0, 0.0]; etat += "+90"; fini = True
        for c in (True, False):
            if inv[c][0] > 1e-9:
                g = c == m["up_gagne"]
                pnl += (inv[c][0] if g else 0) - inv[c][1]; etat += "+seule " + ("gagnee" if g else "perdue")
        return pnl, etat

    def v1(m, Mg, prudent=True):
        cache = {}
        dec = 0.01 if prudent else 0.0
        A = None; invB = [0.0, 0.0]; pnl = 0.0; etat = "rien"; dernier = {True: 0.5, False: 0.5}
        for (ts, up, p, size, side) in m["tr"]:
            if ts < m["start"] or ts > m["end"] - 1: continue
            dernier[up] = p; dernier[not up] = 1 - p
            pu = proba_up(m, ts, cache)
            if pu is None: continue
            if A is None:
                if side == "BUY" and 0.55 <= p <= 0.56:
                    fair = pu if up else 1 - pu
                    if fair >= 0.55 + Mg:
                        A = {"cote": up, "prix": p, "q": N}; pnl -= N * FEE(p); etat = "jambe"
                continue
            if A.get("fini"): break
            c = A["cote"]; fairA = pu if c else 1 - pu
            # offre maker sur l'autre cote
            if side == "SELL": O, q = up, p
            elif side == "BUY": O, q = (not up), 1 - p
            else: O = None
            if O is not None and O != c and invB[0] < A["q"]:
                offre = min(math.floor(((1 - fairA) - Mg) * 100) / 100, 0.43)
                if offre >= 0.02 and q <= offre - dec + 1e-9:
                    k = min(size, A["q"] - invB[0]); invB[0] += k; invB[1] += k * offre
            if invB[0] >= A["q"] - 1e-9:
                pnl += A["q"] * (1 - A["prix"]) - invB[1]; etat = "paire"; A["fini"] = True; invB = [0.0, 0.0]; break
            # sortie si le calcul se retourne
            if fairA < 0.50:
                pv = max(0.01, dernier[c] - 0.01)
                qa = A["q"] - invB[0]
                pnl += qa * (pv - FEE(pv)) - qa * A["prix"] + invB[0] * (1 - A["prix"]) - invB[1]
                etat = "stop" + ("+paire partielle" if invB[0] else ""); A["fini"] = True; invB = [0.0, 0.0]; break
            if up == c and p >= 0.90 and invB[0] < 1e-9:
                pnl += A["q"] * (0.90 - FEE(0.90) - A["prix"]); etat = "sortie 90"; A["fini"] = True; break
        if A and not A.get("fini"):
            g = A["cote"] == m["up_gagne"]
            qa = A["q"] - invB[0]
            pnl += qa * ((1 if g else 0) - A["prix"]) + invB[0] * (1 - A["prix"]) - invB[1]
            etat = "fin " + ("gagnee" if g else "perdue")
        return pnl, etat

    rap = [f"# Paires BTC 5 min « a valeur » — {len(M)} cycles, {JOURS} jours ({jours[0]} -> {jours[-1]})\n",
           "100 parts par jambe. Remplissage prudent sauf mention. Frais taker 0,072 x p x (1-p) ; maker 0.\n",
           "| Strategie | Marge | Cycles trades | Paires | Gain total | Gain/jour | Gain moyen/cycle trade | Pire cycle | Pire baisse |", "|---|---|---|---|---|---|---|---|---|"]
    detail = []
    def ligne(nom, Mg, R):
        R2 = [(p, e) for p, e in R if e != "rien"]
        cum = pic = dd = 0
        for p, _ in R:
            cum += p; pic = max(pic, cum); dd = max(dd, pic - cum)
        tot = sum(p for p, _ in R)
        n = len(R2)
        rap.append(f"| {nom} | {Mg:.2f} | {n} ({n / JOURS:.0f}/j) | {sum(1 for _, e in R2 if 'paire' in e)} | {tot:+.0f} $ | {tot / JOURS:+.0f} $ | {(tot / n if n else 0):+.2f} $ | {min((p for p, _ in R), default=0):+.0f} $ | -{dd:.0f} $ |")
        par = {}
        for p, e in R2: par.setdefault(e, []).append(p)
        detail.append(f"- {nom}, marge {Mg} : " + " ; ".join(f"{k} {len(L)} ({statistics.mean(L):+.2f} $)" for k, L in sorted(par.items(), key=lambda x: -len(x[1]))))
    for Mg in (0.05, 0.08, 0.10, 0.15):
        ligne("V1 Pitch filtre (55 si proba >= 55+marge, offre opposee a valeur <= 43)", Mg, [v1(m, Mg) for m in M])
    for Mg in (0.05, 0.08, 0.10, 0.15):
        ligne("V2 offres a valeur des 2 cotes, jambe gardee", Mg, [v2(m, Mg, False) for m in M])
        ligne("V2 offres a valeur, sortie 90", Mg, [v2(m, Mg, True) for m in M])
    for Mg in (0.08,):
        ligne("V2 offres a valeur, OPTIMISTE (premier dans la file)", Mg, [v2(m, Mg, False, prudent=False) for m in M])
        ligne("V1 Pitch filtre, OPTIMISTE", Mg, [v1(m, Mg, prudent=False) for m in M])
    rap += ["\n## Detail par issue\n"] + detail + [f"\nDuree : {time.time() - t0:.0f} s"]
    open("etude/bot5min/resultat_paires2.md", "w").write("\n".join(rap))
    print("\n".join(rap))


if __name__ == "__main__":
    main()
