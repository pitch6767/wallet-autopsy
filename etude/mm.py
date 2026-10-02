"""Etude : teneur de marche Polymarket pour les recompenses de liquidite.

Pour chaque marche recompense, estime sur les 7 derniers jours :
  - la recompense quotidienne qu'on toucherait avec S parts par cote
  - le cout de la selection adverse sur les executions (markout a 1 h)
Aucun ordre, lecture seule.
"""
import json, time, urllib.request, urllib.parse, statistics, sys, bisect
from concurrent.futures import ThreadPoolExecutor

C = "https://clob.polymarket.com"
D = "https://data-api.polymarket.com"
S = 200            # parts par cote (~200 $ de capital par marche)
DIST = 0.5         # on cote a la moitie de l'ecart max autorise
HORIZON = 3600     # markout a 1 h
JOURS = 7
NOW = int(time.time())
DEBUT = NOW - JOURS * 86400


def get(url, tries=3):
    for k in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "etude-mm"})
            with urllib.request.urlopen(req, timeout=40) as r:
                return json.loads(r.read())
        except Exception as e:
            err = e
            time.sleep(1.5 * (k + 1))
    raise err


def pages(path):
    out, cur = [], ""
    for _ in range(200):
        d = get(f"{C}{path}?next_cursor={urllib.parse.quote(cur)}" if cur else f"{C}{path}")
        out += d.get("data", [])
        cur = d.get("next_cursor") or ""
        if not cur or cur == "LTE=":
            break
    return out


def score_cote(niveaux, mid, v, cote):
    """Somme des parts * ((v-d)/v)^2 pour les ordres a moins de v centimes du milieu."""
    q = 0.0
    for n in niveaux:
        p, t = float(n["price"]), float(n["size"])
        d = (mid - p) * 100 if cote == "bid" else (p - mid) * 100
        if 0 <= d < v:
            q += t * ((v - d) / v) ** 2
    return q


def profondeur_avant(niveaux, mid, dist, cote):
    tot = 0.0
    for n in niveaux:
        p, t = float(n["price"]), float(n["size"])
        d = mid - p if cote == "bid" else p - mid
        if 0 <= d <= dist:
            tot += t
    return tot


def etudier(m):
    tok = m["yes"]
    v = m["v"]
    book = get(f"{C}/book?token_id={tok}")
    bids, asks = book.get("bids", []), book.get("asks", [])
    if not bids or not asks:
        return None
    bb = max(float(b["price"]) for b in bids)
    ba = min(float(a["price"]) for a in asks)
    mid = (bb + ba) / 2
    if not 0.10 <= mid <= 0.90:
        return None
    # concurrence (approximation agregee de la formule Polymarket, c = 3)
    qb, qa = score_cote(bids, mid, v, "bid"), score_cote(asks, mid, v, "ask")
    comp = max(min(qb, qa), max(qb, qa) / 3)
    nous = S * (1 - DIST) ** 2
    part = nous / (nous + comp)
    recompense = part * m["rate"]

    # historique des prix (milieu) pour le markout
    h = get(f"{C}/prices-history?market={tok}&startTs={DEBUT - 3600}&endTs={NOW}&fidelity=5").get("history", [])
    if len(h) < 20:
        h = get(f"{C}/prices-history?market={tok}&interval=1w&fidelity=5").get("history", [])
    if len(h) < 20:
        return None
    ts = [x["t"] for x in h]
    ps = [float(x["p"]) for x in h]

    def prix(t):
        i = bisect.bisect_right(ts, t) - 1
        return ps[max(i, 0)]

    # executions des 7 derniers jours (cote preneur)
    trades = []
    for off in range(0, 3000, 500):
        lot = get(f"{D}/trades?market={m['cid']}&limit=500&offset={off}&takerOnly=true")
        if not lot:
            break
        trades += [t for t in lot if t.get("timestamp", 0) >= DEBUT]
        if lot[-1].get("timestamp", 0) < DEBUT:
            break
    dist = v / 100 * DIST
    prof_b = profondeur_avant(bids, mid, dist, "bid")
    prof_a = profondeur_avant(asks, mid, dist, "ask")
    pnl = 0.0
    parts_exec = 0.0
    n_ok = 0
    for t in trades:
        ts0 = t["timestamp"]
        if ts0 + HORIZON > NOW:
            continue
        p = float(t["price"])
        taille = float(t["size"])
        oui = t.get("asset") == tok or str(t.get("outcomeIndex")) == "0"
        side = t["side"]
        if not oui:  # ramener en prix du OUI
            p = 1 - p
            side = "SELL" if side == "BUY" else "BUY"
        m0 = prix(ts0)
        m1 = prix(ts0 + HORIZON)
        if side == "SELL":   # preneur vend -> notre achat a m0 - dist
            q = m0 - dist
            if p > q + 1e-9:
                continue
            f = S / (S + prof_b)
            fill = taille * f
            pnl += fill * (m1 - q)
        else:                # preneur achete -> notre vente a m0 + dist
            q = m0 + dist
            if p < q - 1e-9:
                continue
            f = S / (S + prof_a)
            fill = taille * f
            pnl += fill * (q - m1)
        parts_exec += fill
        n_ok += 1
    pnl_jour = pnl / JOURS
    net = recompense + pnl_jour
    return {
        "question": m["q"][:70], "rate": m["rate"], "v": v, "mid": round(mid, 3),
        "part": round(part, 3), "recompense": round(recompense, 2),
        "trades7j": len(trades), "exec7j": n_ok, "parts_exec_jour": round(parts_exec / JOURS, 1),
        "markout_jour": round(pnl_jour, 2), "net_jour": round(net, 2),
        "rend_annuel_pct": round(net * 365 / S * 100, 0), "fin": m["fin"],
    }


def main():
    t0 = time.time()
    rec = {r["condition_id"]: r for r in pages("/rewards/markets/current")}
    print("marches recompenses :", len(rec))
    tot = sum(r.get("total_daily_rate") or 0 for r in rec.values())
    print("total recompenses / jour : %.0f $" % tot)
    mk = pages("/sampling-markets")
    print("sampling-markets :", len(mk))
    cands = []
    for x in mk:
        r = rec.get(x.get("condition_id"))
        if not r or not x.get("accepting_orders") or x.get("closed"):
            continue
        toks = x.get("tokens") or []
        if len(toks) != 2:
            continue
        fin = x.get("end_date_iso") or ""
        try:
            tf = time.mktime(time.strptime(fin[:19], "%Y-%m-%dT%H:%M:%S")) if fin else 0
        except Exception:
            tf = 0
        if tf and tf < NOW + 2 * 86400:
            continue
        rate = r.get("total_daily_rate") or 0
        if rate < 5 or (r.get("rewards_min_size") or 0) > S:
            continue
        yes = next((t["token_id"] for t in toks if str(t.get("outcome", "")).lower() == "yes"), toks[0]["token_id"])
        cands.append({"cid": x["condition_id"], "yes": yes, "q": x.get("question", ""),
                      "rate": rate, "v": r.get("rewards_max_spread") or 3, "fin": fin[:10]})
    cands.sort(key=lambda c: -c["rate"])
    cands = cands[:250]
    print("candidats etudies :", len(cands), "(recompense >= 5 $/jour, fin > 2 jours, min_size <= %d)" % S)
    res, err = [], 0
    def sur(c):
        try:
            return etudier(c)
        except Exception as e:
            return {"erreur": str(e)[:80]}
    with ThreadPoolExecutor(8) as ex:
        for r in ex.map(sur, cands):
            if r is None:
                continue
            if "erreur" in r:
                err += 1
                continue
            res.append(r)
    print("analyses :", len(res), "erreurs :", err, "duree %.0fs" % (time.time() - t0))
    if not res:
        return
    pos = [r for r in res if r["net_jour"] > 0]
    print("\nmarches nets positifs : %d / %d" % (len(pos), len(res)))
    print("somme recompenses estimees /jour : %.1f $" % sum(r["recompense"] for r in res))
    print("somme markout /jour : %.1f $" % sum(r["markout_jour"] for r in res))
    print("somme nette /jour (tous) : %.1f $  | positifs seulement : %.1f $" % (
        sum(r["net_jour"] for r in res), sum(r["net_jour"] for r in pos)))
    print("capital si on prend tous les positifs : ~%d $" % (len(pos) * S))
    print("mediane markout par marche /jour : %.2f $" % statistics.median(r["markout_jour"] for r in res))
    print("\nTOP 30 par gain net / jour (S=%d parts par cote, cote a %.0f%% de l'ecart max, markout 1 h)" % (S, DIST * 100))
    print("net$/j | recomp | markout | part | rate | exec7j | mid | fin | question")
    for r in sorted(res, key=lambda r: -r["net_jour"])[:30]:
        print("%6.2f | %6.2f | %7.2f | %4.2f | %4.0f | %6d | %.2f | %s | %s" % (
            r["net_jour"], r["recompense"], r["markout_jour"], r["part"], r["rate"], r["exec7j"], r["mid"], r["fin"], r["question"]))
    print("\nPIRES 10")
    for r in sorted(res, key=lambda r: r["net_jour"])[:10]:
        print("%6.2f | %6.2f | %7.2f | %4.2f | %4.0f | %6d | %.2f | %s | %s" % (
            r["net_jour"], r["recompense"], r["markout_jour"], r["part"], r["rate"], r["exec7j"], r["mid"], r["fin"], r["question"]))
    json.dump(res, open("diagnostic/etude_mm.json", "w"), indent=0)


if __name__ == "__main__":
    main()
