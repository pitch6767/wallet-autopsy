"""Etude : acheter l'issue « quasi-certaine » sur Polymarket (14 derniers jours, lecture seule).

Pour chaque marche resolu : on cherche les executions entre 0,90 et 0,997 sur l'une des issues,
  - AVANT le moment ou le resultat est connu, et
  - APRES (evenement termine, en attente de resolution officielle).
On regarde si l'issue achetee a gagne, combien de temps l'argent est bloque, et quel volume etait disponible.
"""
import json, time, urllib.request, urllib.parse, statistics, re, sys
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

G = "https://gamma-api.polymarket.com"
D = "https://data-api.polymarket.com"
JOURS = 14
NOW = time.time()
DEBUT = NOW - JOURS * 86400
VOL_MIN = 2000
TRANCHES = [(0.90, 0.95), (0.95, 0.97), (0.97, 0.98), (0.98, 0.99), (0.99, 0.9975)]


def get(url, tries=4):
    for k in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "etude"}), timeout=40) as r:
                return json.loads(r.read())
        except Exception as e:
            err = e
            time.sleep(10 if "429" in str(e) else 2 * (k + 1))
    raise err


def ts(s):
    if not s:
        return None
    s = s.replace(" ", "T").replace("+00", "+00:00") if "+00" in s and "+00:" not in s else s.replace(" ", "T")
    s = s.replace("Z", "+00:00")
    try:
        d = datetime.fromisoformat(s)
        if d.tzinfo is None:
            d = d.replace(tzinfo=timezone.utc)
        return d.timestamp()
    except Exception:
        return None


def categorie(m):
    q = m.get("question", "").lower()
    if "up or down" in q:
        return "crypto 5-15 min"
    if m.get("gameStartTime") or m.get("sportsMarketType"):
        return "sport"
    if re.search(r"temperature|°|precipitation|rain|snow|hurricane|weather|highest temp", q):
        return "meteo"
    if re.search(r"bitcoin|ethereum|solana|xrp|btc|eth |crypto|price of", q):
        return "crypto prix"
    if re.search(r"cpi|inflation|fed |interest rate|jobs|unemployment|gdp|payroll|bps", q):
        return "economie"
    if re.search(r"election|president|senate|governor|vote|trump|minister|parliament|mayor", q):
        return "politique"
    if re.search(r"openrouter|netflix|spotify|youtube|billboard|box office|tweet|post", q):
        return "classements/medias"
    return "autre"


def marches():
    out, off, n_updown = [], 0, 0
    while off < 120000:
        lot = get(f"{G}/markets?closed=true&limit=500&offset={off}&order=closedTime&ascending=false")
        if not lot:
            break
        fin = False
        for m in lot:
            R = ts(m.get("closedTime"))
            if R is None:
                continue
            if R < DEBUT:
                fin = True
                continue
            if (m.get("volumeNum") or 0) < VOL_MIN:
                continue
            try:
                px = [float(x) for x in json.loads(m.get("outcomePrices") or "[]")]
                toks = json.loads(m.get("clobTokenIds") or "[]")
            except Exception:
                continue
            if len(px) != 2 or sorted(px) != [0.0, 1.0] or len(toks) != 2:
                continue
            cat = categorie(m)
            if cat == "crypto 5-15 min":
                n_updown += 1
                if n_updown > 400:      # echantillon suffisant pour cette categorie
                    continue
            E = ts(m.get("endDate")) or R
            K = E
            gs = ts(m.get("gameStartTime"))
            if cat == "sport" and gs:
                K = gs + 3.5 * 3600
            out.append({"cid": m["conditionId"], "q": m.get("question", "")[:80], "cat": cat,
                        "gagnant": px.index(1.0), "R": R, "K": min(K, R), "frais": bool(m.get("feesEnabled"))})
        off += 500
        if fin:
            break
    return out


def etudier(m):
    trades, debut_fenetre = [], m["K"] - 72 * 3600
    for off in range(0, 3500, 500):
        lot = get(f"{D}/trades?market={m['cid']}&limit=500&offset={off}&takerOnly=true")
        if not lot:
            break
        trades += lot
        if lot[-1].get("timestamp", 0) < debut_fenetre or len(lot) < 500:
            break
    res = []
    for phase in ("avant", "apres"):
        for (a, b) in TRANCHES:
            sel = []
            for t in trades:
                t0 = t.get("timestamp", 0)
                if t0 > m["R"]:
                    continue
                if phase == "apres" and t0 < m["K"]:
                    continue
                if phase == "avant" and not (debut_fenetre <= t0 < m["K"]):
                    continue
                p = float(t["price"])
                if a <= p < b:
                    sel.append(t)
            if not sel:
                continue
            sel.sort(key=lambda t: t["timestamp"])
            # meme issue que la premiere execution de la tranche
            idx = int(sel[0].get("outcomeIndex", 0))
            meme = [t for t in sel if int(t.get("outcomeIndex", -1)) == idx]
            p0 = float(meme[0]["price"])
            dispo = sum(float(t["size"]) * float(t["price"]) for t in meme)
            res.append({"phase": phase, "tranche": (a, b), "p": p0, "gagne": idx == m["gagnant"],
                        "heures": (m["R"] - meme[0]["timestamp"]) / 3600, "dispo": dispo,
                        "jour": int(meme[0]["timestamp"] // 86400)})
    return res


def main():
    t0 = time.time()
    M = marches()
    par_cat = defaultdict(int)
    for m in M:
        par_cat[m["cat"]] += 1
    print("marches resolus etudies (%d jours, volume >= %d $) : %d  (%.0fs)" % (JOURS, VOL_MIN, len(M), time.time() - t0))
    print("par categorie :", dict(sorted(par_cat.items(), key=lambda x: -x[1])))

    def sur(m):
        try:
            return m, etudier(m)
        except Exception:
            return m, None

    R = []
    with ThreadPoolExecutor(8) as ex:
        for m, r in ex.map(sur, M):
            if r:
                for x in r:
                    x.update({"cat": m["cat"], "q": m["q"]})
                    R.append(x)
    print("analyse terminee en %.0fs\n" % (time.time() - t0))

    def bloc(lignes, titre):
        if not lignes:
            return
        n = len(lignes)
        g = sum(1 for x in lignes if x["gagne"])
        pm = statistics.mean(x["p"] for x in lignes)
        rend = statistics.mean((1 / x["p"] - 1) if x["gagne"] else -1 for x in lignes)
        h = statistics.median(x["heures"] for x in lignes)
        jours = len(set(x["jour"] for x in lignes)) or 1
        dispo = statistics.median(x["dispo"] for x in lignes)
        print("%-34s n=%5d | gagne %6.2f %% | prix moyen %.3f | gain moyen/trade %+6.2f %% | bloque med. %6.1f h | %5.1f occasions/jour | dispo med. %7.0f $" % (
            titre, n, 100 * g / n, pm, 100 * rend, h, n / JOURS, dispo))

    for phase, nom in (("apres", "APRES la fin de l'evenement (resultat connu)"), ("avant", "AVANT la fin (72 h max)")):
        print("=" * 30, nom)
        for (a, b) in TRANCHES:
            L = [x for x in R if x["phase"] == phase and x["tranche"] == (a, b)]
            print("\n-- tranche %.3f - %.4f" % (a, b))
            bloc(L, "TOUTES categories")
            cats = defaultdict(list)
            for x in L:
                cats[x["cat"]].append(x)
            for c, l in sorted(cats.items(), key=lambda x: -len(x[1])):
                bloc(l, "  " + c)
        print()
    print("=" * 30, "PERTES apres la fin (issue achetee >= 0,95 qui a perdu)")
    P = [x for x in R if x["phase"] == "apres" and not x["gagne"] and x["p"] >= 0.95]
    for x in sorted(P, key=lambda x: -x["p"])[:25]:
        print("  %.3f | %-18s | bloque %5.1f h | %s" % (x["p"], x["cat"], x["heures"], x["q"]))
    print("nombre total :", len(P))


if __name__ == "__main__":
    main()
