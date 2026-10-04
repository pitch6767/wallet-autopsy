"""Tests du bot « 95 % dans les dernieres secondes » sur les marches BTC Up/Down 5 min de Polymarket.

Donnees : marches resolus Polymarket (gamma), executions (data-api), prix BTC/ETH/SOL a la seconde (Binance).
Strategie de base : dans les W dernieres secondes, des que l'issue favorite s'execute entre PMIN et PMAX,
on achete 50 $ a ce prix et on garde jusqu'a la fin. Puis on ajoute les filtres un par un.
"""
import json, time, math, io, zipfile, sys, csv, statistics, urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone, timedelta
from collections import defaultdict

G = "https://gamma-api.polymarket.com"
D = "https://data-api.polymarket.com"
JOURS = int(sys.argv[1]) if len(sys.argv) > 1 else 10
MISE = 50.0
FEE_RATE = 0.072          # frais taker crypto : parts x 0,072 x p x (1-p)
OUT = "etude/bot5min/"
ACHAT_REEL = True


def get(url, tries=5, raw=False):
    err = None
    for k in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "etude"}), timeout=60) as r:
                b = r.read()
                return b if raw else json.loads(b)
        except Exception as e:
            err = e
            if "404" in str(e):
                break
            time.sleep(8 if "429" in str(e) else 1.5 * (k + 1))
    raise err


# ---------------------------------------------------------------- Binance 1 s
def binance_jour(sym, jour):
    url = f"https://data.binance.vision/data/spot/daily/klines/{sym}/1s/{sym}-1s-{jour}.zip"
    z = zipfile.ZipFile(io.BytesIO(get(url, raw=True)))
    out = {}
    for ligne in z.read(z.namelist()[0]).decode().splitlines():
        c = ligne.split(",")
        t = int(c[0])
        if t > 1e14:      # microsecondes
            t //= 1000
        out[t // 1000] = (float(c[1]), float(c[4]))   # open, close
    return out


def binance(sym, jours):
    px = {}
    with ThreadPoolExecutor(4) as ex:
        for d in ex.map(lambda j: binance_jour(sym, j), jours):
            px.update(d)
    return px


def prix(px, t):
    for k in range(6):
        if t - k in px:
            return px[t - k][1]
    return None


# ---------------------------------------------------------------- Polymarket
def marche(start):
    try:
        ev = get(f"{G}/events?slug=btc-updown-5m-{start}")
    except Exception:
        return None
    if not ev:
        return None
    e = ev[0]
    m = (e.get("markets") or [None])[0]
    if not m:
        return None
    try:
        out = json.loads(m.get("outcomes") or "[]")
        px = [float(x) for x in json.loads(m.get("outcomePrices") or "[]")]
    except Exception:
        return None
    if sorted(px) != [0.0, 1.0]:
        return None
    meta = e.get("eventMetadata") or m.get("eventMetadata") or {}
    if isinstance(meta, str):
        try:
            meta = json.loads(meta)
        except Exception:
            meta = {}
    gagnant = out[px.index(1.0)]            # "Up" ou "Down"
    return {"start": start, "end": start + 300, "cid": m["conditionId"], "up_gagne": gagnant.lower() == "up",
            "strike": meta.get("priceToBeat"), "final": meta.get("finalPrice"), "meta_keys": list(meta.keys())}


def trades(m):
    """executions des 120 dernieres secondes, prix exprime en prix de UP"""
    res = []
    for off in range(0, 3000, 500):
        lot = get(f"{D}/trades?market={m['cid']}&limit=500&offset={off}&takerOnly=true")
        if not lot:
            break
        for t in lot:
            ts = int(t["timestamp"])
            if m["end"] - 120 <= ts <= m["end"]:
                p = float(t["price"])
                up = (t.get("outcome") or "").lower() == "up"
                res.append((ts, p if up else 1 - p, float(t["size"]), t.get("proxyWallet"), up, t.get("side")))
        desc = int(lot[0]["timestamp"]) >= int(lot[-1]["timestamp"])
        if len(lot) < 500 or (desc and int(lot[-1]["timestamp"]) < m["end"] - 120):
            break
    res.sort()
    return res


# ---------------------------------------------------------------- modele
def sigma_s(px, t, n=300):
    r = []
    for k in range(t - n, t):
        a, b = prix(px, k - 1), prix(px, k)
        if a and b:
            r.append(math.log(b / a))
    return statistics.pstdev(r) if len(r) > 30 else None


def phi(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def analyser(m, BTC, ETH, SOL, W, PMIN, PMAX):
    tr = m["trades"]
    K = m["strike_ok"]
    entree = None
    for (ts, pup, size, wal, up, side) in tr:
        if ts < m["end"] - W or ts > m["end"] - 1:
            continue
        fav_up = pup >= 0.5
        pf = pup if fav_up else 1 - pup
        if ACHAT_REEL and not (side == "BUY" and up == fav_up):
            continue            # seulement un vrai achat du favori a ce prix
        if PMIN <= pf <= PMAX:
            entree = (ts, pf, fav_up)
            break
    if not entree:
        return None
    ts, p, fav_up = entree
    gagne = (fav_up == m["up_gagne"])
    tleft = m["end"] - ts
    P = prix(BTC, ts)
    sg = sigma_s(BTC, ts)
    f = {"start": m["start"], "ts": ts, "tleft": tleft, "p": p, "fav": "Up" if fav_up else "Down", "gagne": gagne}
    if P and sg and K:
        d = math.log(P / K) * (1 if fav_up else -1)          # distance signee (positive = favorable)
        z = d / (sg * math.sqrt(max(tleft, 1)))
        f["dist_usd"] = round((P - K) * (1 if fav_up else -1), 1)
        f["z"] = round(z, 2)
        f["proba_modele"] = round(phi(z), 4)
        P5 = prix(BTC, ts - 5)
        v = (P - P5) / 5 * (1 if fav_up else -1) if P5 else 0      # $/s, negatif = va vers le strike
        f["vitesse"] = round(v, 2)
        f["t_strike"] = round(f["dist_usd"] / -v, 1) if v < 0 else 999
        f["vol_s"] = round(sg * 1e4, 3)
        # ETH / SOL sur 10 s contre la direction du favori
        def ret(px, n=10):
            a, b = prix(px, ts - n), prix(px, ts)
            return math.log(b / a) * (1 if fav_up else -1) if a and b else 0
        se, ss = sigma_s(ETH, ts) or 1, sigma_s(SOL, ts) or 1
        f["eth_z"] = round(ret(ETH) / (se * math.sqrt(10)), 2)
        f["sol_z"] = round(ret(SOL) / (ss * math.sqrt(10)), 2)
        f["btc10_z"] = round(ret(BTC) / (sg * math.sqrt(10)), 2)
        # sortie a T-5 : proba modele a T-5
        t5 = m["end"] - 5
        if t5 > ts:
            P_5 = prix(BTC, t5)
            if P_5:
                z5 = math.log(P_5 / K) * (1 if fav_up else -1) / (sg * math.sqrt(5))
                f["proba_T5"] = round(phi(z5), 4)
                avant = [x for x in tr if x[0] <= t5]
                if avant:
                    f["px_T5"] = round(avant[-1][1] if fav_up else 1 - avant[-1][1], 3)
    # prix max atteint par le favori apres l'entree (pour la revente a 0,99)
    apres = [(x[1] if fav_up else 1 - x[1]) for x in tr if x[0] > ts]
    f["max_apres"] = max(apres) if apres else p
    f["min_apres"] = min(apres) if apres else p
    # gros ordres d'en face dans les 60 s avant l'entree
    contre = [x[2] * (x[1] if x[4] else 1 - x[1]) for x in tr if ts - 60 <= x[0] <= ts and x[4] != fav_up and x[5] == "BUY"]
    f["gros_contre"] = round(max(contre), 0) if contre else 0
    return f


def pnl(p, gagne, sortie=None):
    parts = MISE / p
    frais = parts * FEE_RATE * p * (1 - p)
    if sortie is not None:
        return parts * (sortie - p) - frais - parts * FEE_RATE * sortie * (1 - sortie)
    return (parts * (1 - p) if gagne else -MISE) - frais


def resume(nom, L, fn=None):
    if not L:
        return f"| {nom} | 0 | - | - | - | - | - | - |"
    res = [fn(x) if fn else pnl(x["p"], x["gagne"]) for x in L]
    pertes = sum(1 for r in res if r < 0)
    cum = pic = dd = 0.0
    for x, r in sorted(zip(L, res), key=lambda z: z[0]["ts"]):
        cum += r; pic = max(pic, cum); dd = max(dd, pic - cum)
    return "| %s | %d | %d | %.2f %% | %+.0f $ | %+.2f $ | %.1f | -%.0f $ |" % (
        nom, len(L), pertes, 100 * (1 - pertes / len(L)), sum(res), statistics.mean(res), len(L) / JOURS, dd)


def main():
    t0 = time.time()
    fin = int(time.time()) // 300 * 300 - 600
    debut = fin - JOURS * 86400
    jours = sorted({datetime.fromtimestamp(t, timezone.utc).strftime("%Y-%m-%d") for t in range(debut - 600, fin + 600, 3600)})
    jours = [j for j in jours if j < datetime.now(timezone.utc).strftime("%Y-%m-%d")]   # fichiers du jour pas encore publies
    fin = min(fin, int(datetime.strptime(jours[-1], "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp()) + 86400 - 300)
    log = []
    print("Binance...", jours[0], "->", jours[-1]); sys.stdout.flush()
    BTC, ETH, SOL = binance("BTCUSDT", jours), binance("ETHUSDT", jours), binance("SOLUSDT", jours)
    print("  BTC secondes :", len(BTC), "(%.0fs)" % (time.time() - t0)); sys.stdout.flush()

    starts = list(range(debut, fin, 300))
    with ThreadPoolExecutor(12) as ex:
        M = [m for m in ex.map(marche, starts) if m]
    print("marches resolus :", len(M), "/", len(starts), "(%.0fs)" % (time.time() - t0))
    if M:
        print("  cles metadata exemple :", M[0]["meta_keys"], "strike", M[0]["strike"]); sys.stdout.flush()

    def avec_trades(m):
        try:
            m["trades"] = trades(m)
        except Exception:
            m["trades"] = []
        return m
    with ThreadPoolExecutor(10) as ex:
        M = list(ex.map(avec_trades, M))
    print("executions chargees (%.0fs)" % (time.time() - t0)); sys.stdout.flush()

    # strike : priceToBeat de Polymarket si dispo, sinon ouverture Binance a la seconde du debut
    M.sort(key=lambda m: m["start"])
    hist = []
    for m in M:
        kb = BTC.get(m["start"], (None,))[0]
        try:
            kp = float(m["strike"]) if m["strike"] is not None else None
        except Exception:
            kp = None
        m["base"] = statistics.median(hist[-12:]) if len(hist) >= 3 else 0.0
        if kb and kp:
            hist.append(kb - kp)
    accord = desac = 0
    for m in M:
        kb = BTC.get(m["start"], (None,))[0]
        k = m["strike"]
        try:
            k = float(k) if k is not None else None
        except Exception:
            k = None
        m["strike_ok"] = (k + m["base"]) if k else kb   # strike exprime en prix Binance
        m["strike_src"] = "polymarket" if k else "binance"
        fb = prix(BTC, m["end"])
        if m["strike_ok"] and fb:
            if (fb > m["strike_ok"]) == m["up_gagne"]:
                accord += 1
            else:
                desac += 1
    sources = defaultdict(int)
    for m in M:
        sources[m["strike_src"]] += 1

    L = []
    rap = []
    rap.append(f"# Tests bot BTC 5 min (ACHATS REELS du favori seulement) — {len(M)} marches sur {JOURS} jours ({jours[0]} -> {jours[-1]})\n")
    rap.append(f"Strike : {dict(sources)}. Binance (strike corrige de l'ecart USDT/USD) donne le bon gagnant dans {accord}/{accord + desac} marches "
               f"({100 * accord / max(1, accord + desac):.2f} %) — le reste = ecart Binance/Chainlink.\n")
    rap.append(f"Mise {MISE:.0f} $, frais taker {FEE_RATE} x p x (1-p) par part.\n")

    # ---- grille de base
    rap.append("\n## 1. Strategie de base (acheter le favori, garder jusqu'a la fin)\n")
    rap.append("| Fenetre / prix | Trades | Pertes | Reussite | PnL total | PnL moyen | Trades/jour | Pire baisse |\n|---|---|---|---|---|---|---|---|")
    grille = {}
    for W in (60, 30):
        for (a, b) in ((0.90, 0.99), (0.93, 0.99), (0.95, 0.99), (0.95, 0.97), (0.97, 0.99)):
            R = [x for x in (analyser(m, BTC, ETH, SOL, W, a, b) for m in M if m["trades"]) if x]
            grille[(W, a, b)] = R
            rap.append(resume(f"{W}s, {a:.2f}-{b:.2f}", R))
    TOUS = []
    for WB in (60, 30):
        base = grille[(WB, 0.95, 0.99)]

        # ---- filtres
        B = [x for x in base if "z" in x]
        rap.append(f"\n## 2.{WB}s Filtres (base : {WB} s, 0,95-0,99 ; {len(B)} trades avec donnees completes)\n")
        rap.append("| Filtre | Trades | Pertes | Reussite | PnL total | PnL moyen | Trades/jour | Pire baisse |\n|---|---|---|---|---|---|---|---|")
        rap.append(resume("Base", B))
        F = {
            "6 modele >= prix + 1 pt": lambda x: x["proba_modele"] >= x["p"] + 0.01,
            "6 modele >= prix + 2 pts": lambda x: x["proba_modele"] >= x["p"] + 0.02,
            "3 z >= 2,5": lambda x: x["z"] >= 2.5,
            "3 z >= 3": lambda x: x["z"] >= 3,
            "19 pas de course vers le strike (t_strike > 2x temps restant)": lambda x: x["t_strike"] > 2 * x["tleft"],
            "23 ETH et SOL pas contre (z > -1,5)": lambda x: not (x["eth_z"] < -1.5 and x["sol_z"] < -1.5),
            "BTC 10 s pas contre (z > -1,5)": lambda x: x["btc10_z"] > -1.5,
            "22 pas de gros achat en face (< 500 $ / 60 s)": lambda x: x["gros_contre"] < 500,
            "17 nuit/week-end seulement": lambda x: (datetime.fromtimestamp(x["ts"], timezone.utc).weekday() >= 5 or datetime.fromtimestamp(x["ts"], timezone.utc).hour < 6),
            "17 hors nuit/week-end": lambda x: not (datetime.fromtimestamp(x["ts"], timezone.utc).weekday() >= 5 or datetime.fromtimestamp(x["ts"], timezone.utc).hour < 6),
        }
        for nom, fn in F.items():
            rap.append(resume(nom, [x for x in B if fn(x)]))

        # ---- sorties
        rap.append(f"\n## 3.{WB}s Sorties (sur la base)\n")
        rap.append("| Sortie | Trades | Pertes | Reussite | PnL total | PnL moyen | Trades/jour | Pire baisse |\n|---|---|---|---|---|---|---|---|")
        rap.append(resume("Garder jusqu'a la fin", B))

        def s99(x):
            return pnl(x["p"], x["gagne"], 0.99) if (x["max_apres"] >= 0.99 and x["p"] < 0.985) else pnl(x["p"], x["gagne"])
        rap.append(resume("8 revente a 0,99 si atteint", B, s99))

        def t5(seuil):
            def f(x):
                if x.get("proba_T5") is not None and x.get("px_T5") and x["proba_T5"] < seuil:
                    return pnl(x["p"], x["gagne"], x["px_T5"])
                return pnl(x["p"], x["gagne"])
            return f
        for s in (0.90, 0.80):
            rap.append(resume(f"20 sortie T-5 s si modele < {s:.2f}", B, t5(s)))

        # ---- combinaison
        combo = lambda x: (x["proba_modele"] >= x["p"] + 0.01 and x["t_strike"] > 2 * x["tleft"]
                           and not (x["eth_z"] < -1.5 and x["sol_z"] < -1.5) and x["btc10_z"] > -1.5)
        C = [x for x in B if combo(x)]
        rap.append(f"\n## 4.{WB}s Combinaison 6 + 19 + 23 + BTC 10 s\n")
        rap.append("| Version | Trades | Pertes | Reussite | PnL total | PnL moyen | Trades/jour | Pire baisse |\n|---|---|---|---|---|---|---|---|")
        rap.append(resume("Combinaison, garder", C))
        rap.append(resume("Combinaison + revente 0,99", C, s99))
        rap.append(resume("Combinaison + sortie T-5 (<0,90)", C, t5(0.90)))

        # ---- autopsie des pertes (18)
        P = [x for x in B if not x["gagne"]]
        G_ = [x for x in B if x["gagne"]]
        rap.append(f"\n## 5.{WB}s Autopsie des pertes (18) : {len(P)} pertes contre {len(G_)} gains\n")
        rap.append("| Indicateur (mediane) | Gains | Pertes |\n|---|---|---|")
        for k in ("tleft", "p", "dist_usd", "z", "proba_modele", "vitesse", "vol_s", "btc10_z", "eth_z", "sol_z", "gros_contre"):
            a = [x[k] for x in G_ if k in x]; b = [x[k] for x in P if k in x]
            if a and b:
                rap.append(f"| {k} | {statistics.median(a)} | {statistics.median(b)} |")
        rap.append("\n### Detail des pertes\n")
        rap.append("| Debut (UTC) | Temps restant | Prix | Favori | Distance $ | z | Proba modele | Vitesse $/s | ETH z | SOL z |\n|---|---|---|---|---|---|---|---|---|---|")
        for x in sorted(P, key=lambda x: x["ts"]):
            rap.append("| %s | %d s | %.3f | %s | %s | %s | %s | %s | %s | %s |" % (
                datetime.fromtimestamp(x["start"], timezone.utc).strftime("%m-%d %H:%M"), x["tleft"], x["p"], x["fav"],
                x.get("dist_usd"), x.get("z"), x.get("proba_modele"), x.get("vitesse"), x.get("eth_z"), x.get("sol_z")))

        TOUS += B
    rap.append(f"\nDuree du calcul : {time.time() - t0:.0f} s")
    open(OUT + "resultat_achats_reels.md", "w").write("\n".join(rap))
    with open(OUT + "trades.csv", "w", newline="") as fh:
        cols = sorted({k for x in TOUS for k in x})
        w = csv.DictWriter(fh, cols)
        w.writeheader()
        for x in TOUS:
            w.writerow(x)
    print("\n".join(rap))


if __name__ == "__main__":
    main()
