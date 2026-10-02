"""Etude Kalshi : acheter l'issue quasi-certaine en fin de vie du marche (lecture seule).

Pour chaque marche regle des N derniers jours : executions a un prix >= 0,90 sur OUI ou NON,
classees selon le temps restant avant la cloture (derniere heure, 1-6 h, 6-72 h).
On regarde si l'issue achetee a gagne, apres frais Kalshi (0,07 x p x (1-p) par contrat).
"""
import json, time, urllib.request, statistics, sys
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

K = "https://api.elections.kalshi.com/trade-api/v2"
JOURS = int(sys.argv[1]) if len(sys.argv) > 1 else 30
NOW = time.time()
DEBUT = NOW - JOURS * 86400
VOL_MIN = 2000
MAX_MARCHES = 4000
TRANCHES = [(0.90, 0.95), (0.95, 0.97), (0.97, 0.98), (0.98, 0.99), (0.99, 0.9975)]
PHASES = [("derniere heure", 0, 1), ("1-6 h avant", 1, 6), ("6-72 h avant", 6, 72)]


def get(url, tries=5):
    for k in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "etude", "Accept": "application/json"}), timeout=40) as r:
                return json.loads(r.read())
        except Exception as e:
            err = e
            time.sleep(8 if "429" in str(e) else 2 * (k + 1))
    raise err


def ts(s):
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()
    except Exception:
        return None


def prix_oui(t):
    if t.get("yes_price_dollars") is not None:
        return float(t["yes_price_dollars"])
    if t.get("yes_price") is not None:
        v = float(t["yes_price"])
        return v / 100 if v > 1 else v
    return None


def marches():
    out, cur, montre = [], "", False
    for _ in range(400):
        url = f"{K}/markets?status=settled&limit=1000&min_close_ts={int(DEBUT)}" + (f"&cursor={cur}" if cur else "")
        d = get(url)
        lot = d.get("markets", [])
        if lot and not montre:
            print("exemple de marche :", {k: lot[0].get(k) for k in list(lot[0].keys())[:40]})
            montre = True
        for m in lot:
            res = (m.get("result") or "").lower()
            if res not in ("yes", "no"):
                continue
            vol = float(m.get("volume_fp") or m.get("volume") or 0)
            if vol < VOL_MIN:
                continue
            C = ts(m.get("close_time"))
            if not C or C < DEBUT:
                continue
            out.append({"ticker": m["ticker"], "serie": (m.get("event_ticker") or m["ticker"]).split("-")[0],
                        "titre": (m.get("title") or "")[:70] + " | " + (m.get("yes_sub_title") or "")[:30],
                        "oui_gagne": res == "yes", "C": C, "vol": vol})
        cur = d.get("cursor") or ""
        if not cur or not lot:
            break
    return out


def etudier(m):
    trades, cur = [], ""
    for _ in range(6):
        d = get(f"{K}/markets/trades?ticker={m['ticker']}&limit=1000" + (f"&cursor={cur}" if cur else ""))
        lot = d.get("trades", [])
        trades += lot
        cur = d.get("cursor") or ""
        if not cur or not lot or ts(lot[-1].get("created_time")) < m["C"] - 72 * 3600:
            break
    res = []
    for nom, h0, h1 in PHASES:
        for (a, b) in TRANCHES:
            sel = []
            for t in trades:
                t0 = ts(t.get("created_time"))
                p = prix_oui(t)
                if t0 is None or p is None:
                    continue
                reste = (m["C"] - t0) / 3600
                if not (h0 <= reste < h1):
                    continue
                if a <= p < b:
                    sel.append((t0, p, True, t))
                elif a <= 1 - p < b:
                    sel.append((t0, 1 - p, False, t))
            if not sel:
                continue
            sel.sort(key=lambda x: x[0])
            t0, p, cote_oui, _ = sel[0]
            gagne = cote_oui == m["oui_gagne"]
            frais = 0.07 * p * (1 - p)
            dispo = sum(float(x[3].get("count_fp") or x[3].get("count") or 0) * x[1] for x in sel if x[2] == cote_oui)
            gain = ((1 - p - frais) / (p + frais)) if gagne else -1
            res.append({"phase": nom, "tranche": (a, b), "p": p, "gagne": gagne, "gain": gain,
                        "heures": (m["C"] - t0) / 3600, "dispo": dispo, "serie": m["serie"], "titre": m["titre"]})
    return res


def main():
    t0 = time.time()
    M = marches()
    print("marches regles (%d jours, volume >= %d contrats) : %d (%.0fs)" % (JOURS, VOL_MIN, len(M), time.time() - t0))
    M.sort(key=lambda m: -m["vol"])
    M = M[:MAX_MARCHES]
    print("etudies (les plus gros) :", len(M))
    par_serie = defaultdict(int)
    for m in M:
        par_serie[m["serie"]] += 1
    print("series principales :", sorted(par_serie.items(), key=lambda x: -x[1])[:25])

    def sur(m):
        try:
            return etudier(m)
        except Exception as e:
            return None

    R = []
    with ThreadPoolExecutor(6) as ex:
        for r in ex.map(sur, M):
            if r:
                R += r
    print("analyse terminee en %.0fs\n" % (time.time() - t0))

    def bloc(L, titre):
        if not L:
            return
        n = len(L)
        g = sum(1 for x in L if x["gagne"])
        print("%-30s n=%5d | gagne %6.2f %% | prix moy %.3f | gain moyen/trade apres frais %+6.2f %% | %5.1f occ/jour | dispo med %7.0f $" % (
            titre, n, 100 * g / n, statistics.mean(x["p"] for x in L), 100 * statistics.mean(x["gain"] for x in L),
            n / JOURS, statistics.median(x["dispo"] for x in L)))

    for nom, _, _ in PHASES:
        print("=" * 25, nom.upper(), "avant la cloture")
        for tr in TRANCHES:
            L = [x for x in R if x["phase"] == nom and x["tranche"] == tr]
            print("\n-- tranche %.3f - %.4f" % tr)
            bloc(L, "TOUTES series")
            S = defaultdict(list)
            for x in L:
                S[x["serie"]].append(x)
            for s, l in sorted(S.items(), key=lambda x: -len(x[1]))[:8]:
                bloc(l, "  " + s)
        print()
    # meilleures series toutes tranches >= 0,95, toutes phases
    print("=" * 25, "SERIES : resultat cumule (prix >= 0,95, toutes phases)")
    S = defaultdict(list)
    for x in R:
        if x["p"] >= 0.95:
            S[x["serie"]].append(x)
    for s, l in sorted(S.items(), key=lambda x: -sum(y["gain"] for y in x[1]))[:20]:
        bloc(l, "  " + s)
    print("\n... pires series")
    for s, l in sorted(S.items(), key=lambda x: sum(y["gain"] for y in x[1]))[:10]:
        bloc(l, "  " + s)
    print("\nPERTES a >= 0,97 dans la derniere heure :")
    for x in [x for x in R if x["phase"] == "derniere heure" and x["p"] >= 0.97 and not x["gagne"]][:20]:
        print("  %.3f | %s | %s" % (x["p"], x["serie"], x["titre"]))


if __name__ == "__main__":
    main()
