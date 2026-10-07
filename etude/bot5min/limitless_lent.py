"""Limitless BTC 5 min : son prix reste-t-il en retard sur le BTC et sur Polymarket, et combien gagnerait-on en achetant
le bon cote sur Limitless a l'ancien prix (un seul achat, garde jusqu'au resultat — pas d'arbitrage) ? (07.10.2026)
Modes : « sonde » (montre les reponses de l'API Limitless) ; « mesure N » (N minutes, chaque seconde).
"""
import json, sys, time, re, statistics, urllib.request, collections

OUT = "etude/bot5min/"
L = "https://api.limitless.exchange"


def get(url, t=8):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "etude", "Accept": "application/json"}), timeout=t) as r: return json.loads(r.read())
    except Exception as e:
        return {"_erreur": str(e)[:200]}


def log(*a): print(*a, flush=True)


def actifs_btc5():
    data = []
    for url in (f"{L}/markets/active", f"{L}/markets/active?page=2", f"{L}/markets/active?limit=25&page=1", f"{L}/markets/active?limit=25&page=2", f"{L}/markets/active?limit=25&page=3"):
        r = get(url)
        data += (r.get("data") if isinstance(r, dict) else r) or []
    out = []; vus = set()
    for m in data:
        if not isinstance(m, dict) or m.get("slug") in vus: continue
        vus.add(m.get("slug"))
        s = m.get("slug") or ""
        if re.match(r"btc-up-or-down-5-min-", s): out.append(m)
    return out


def sonde():
    r = get(f"{L}/markets/active")
    log("cles reponse", list(r.keys()) if isinstance(r, dict) else type(r), "total", r.get("totalMarketsCount") if isinstance(r, dict) else None)
    d = (r.get("data") if isinstance(r, dict) else r) or []
    log("slugs", [m.get("slug") for m in d][:60])
    A = actifs_btc5()
    log("BTC 5 min actifs :", [m.get("slug") for m in A])
    if A:
        m = A[0]; log(json.dumps(m)[:3000])
        s = m["slug"]
        log("--- detail", json.dumps(get(f"{L}/markets/{s}"))[:3000])
        log("--- carnet", json.dumps(get(f"{L}/markets/{s}/orderbook"))[:2000])


def prix_limitless(slug):
    d = get(f"{L}/markets/{slug}")
    ob = get(f"{L}/markets/{slug}/orderbook")
    p = None
    try: p = float(d["prices"][0]); p = p / 100 if p > 1 else p
    except Exception: pass
    bid = ask = taille_ask = None
    try:
        bids = ob.get("bids") or []; asks = ob.get("asks") or []
        if bids: bid = max(float(x["price"]) for x in bids)
        if asks:
            a0 = min(asks, key=lambda x: float(x["price"])); ask = float(a0["price"]); taille_ask = float(a0.get("size") or 0) / 1e6
        if bid and bid > 1: bid /= 100
        if ask and ask > 1: ask /= 100
    except Exception: pass
    return p, bid, ask, taille_ask, d


POLY = {}
def poly(now):
    st = int(now) // 300 * 300
    if POLY.get("st") != st:
        ev = get(f"https://gamma-api.polymarket.com/events?slug=btc-updown-5m-{st}")
        try: m = ev[0]["markets"][0]; toks = json.loads(m["clobTokenIds"]); outs = json.loads(m["outcomes"]); POLY.update(st=st, tok=toks[outs.index("Up")])
        except Exception: POLY.update(st=st, tok=None)
    if not POLY.get("tok"): return None
    b = get(f"https://clob.polymarket.com/book?token_id={POLY['tok']}")
    try: return (max(float(x["price"]) for x in b["bids"]) + min(float(x["price"]) for x in b["asks"])) / 2
    except Exception: return None


def mesure(minutes):
    S = []; infos = {}; t_fin = time.time() + 60 * minutes; cur = None; t_liste = 0
    while time.time() < t_fin:
        t0 = time.time()
        if not cur or t0 - t_liste > 20:
            t_liste = t0; A = actifs_btc5()
            if A:
                A.sort(key=lambda m: m.get("expirationTimestamp") or m.get("deadline") or 0)
                cur = A[0]["slug"]
        btc = get("https://data-api.binance.vision/api/v3/ticker/price?symbol=BTCUSDT")
        pm = poly(t0)
        lp = lb = la = lt = None
        if cur:
            lp, lb, la, lt, d = prix_limitless(cur)
            if cur not in infos and isinstance(d, dict) and "_erreur" not in d:
                infos[cur] = {k: d.get(k) for k in ("title", "description", "expirationTimestamp", "expirationDate", "createdAt", "status", "outcomeTokens", "volume", "liquidity")}
        S.append((round(t0, 1), float(btc["price"]) if isinstance(btc, dict) and "price" in btc else None, pm, cur, lp, lb, la, lt, POLY.get("st")))
        time.sleep(max(0, 1 - (time.time() - t0)))
    # resultats officiels Limitless
    res = {}
    for s in infos:
        d = get(f"{L}/markets/{s}")
        res[s] = {k: d.get(k) for k in ("status", "winningOutcomeIndex", "winningIndex", "resolution", "prices")} if isinstance(d, dict) else None
    json.dump({"S": S, "infos": infos, "res": res}, open(OUT + "limitless_brut.json", "w"))
    analyser(S, infos, res)


def analyser(S, infos, res):
    rap = [f"# Limitless BTC 5 min — {len(S)} secondes, {len(infos)} marches", ""]
    ex = next(iter(infos.values()), {})
    rap += ["Exemple de marche : " + json.dumps(ex, ensure_ascii=False)[:600], "", "Resultats lus : " + json.dumps(list(res.items())[:3], ensure_ascii=False)[:600], ""]
    def gagnant(s):
        r = res.get(s) or {}
        for k in ("winningOutcomeIndex", "winningIndex"):
            if r.get(k) is not None: return int(r[k]) == 0   # 0 = Oui/Up (a verifier dans l'exemple ci-dessus)
        p = r.get("prices")
        try: return float(p[0]) > float(p[1])
        except Exception: return None
    for seuil in (3, 5, 8):
        T = []; dernier = -99
        for i in range(3, len(S) - 1):
            b0, b1 = S[i - 3][1], S[i][1]
            if not b0 or not b1 or S[i][3] != S[i - 3][3] or not S[i][3]: continue
            mv = (b1 / b0 - 1) * 1e4
            if abs(mv) < seuil or i - dernier < 10: continue
            lp0, lp1 = S[i - 3][4], S[i][4]
            if lp0 is None or lp1 is None: continue
            up = mv > 0
            if (lp1 - lp0) * (1 if up else -1) >= 0.02: continue          # Limitless a deja bouge
            dernier = i
            # achat du bon cote a l'ancien prix : Up a l'ask ; Down ~ 1 - bid Up
            prix = S[i][6] if up else (1 - S[i][5] if S[i][5] else None)
            if prix is None or not (0.03 < prix < 0.97): continue
            g = gagnant(S[i][3])
            # combien de secondes avant que Limitless suive
            suit = next((h for h in range(1, 60) if i + h < len(S) and S[i + h][3] == S[i][3] and S[i + h][4] is not None and (S[i + h][4] - lp0) * (1 if up else -1) >= 0.02), None)
            T.append({"prix": prix, "taille": S[i][7], "g": None if g is None else (g if up else not g), "suit": suit})
        E = [x for x in T if x["g"] is not None]
        if not T: rap.append(f"- Mouvement BTC ≥ {seuil} pb en 3 s avec Limitless immobile : 0"); continue
        gain = [(1 if x["g"] else 0) - x["prix"] for x in E]
        sui = [x["suit"] for x in T if x["suit"] is not None]
        rap.append(f"- Mouvement BTC ≥ {seuil} pb en 3 s avec Limitless immobile : **{len(T)}** fois · Limitless suit en {statistics.median(sui) if sui else '—'} s (median) · "
                   f"achat du bon cote a l'ancien prix : gagne {100 * statistics.mean(1 if x['g'] else 0 for x in E) if E else 0:.0f} % (prix moyen {statistics.mean(x['prix'] for x in E) if E else 0:.2f}) · "
                   f"**{statistics.mean(gain) if gain else 0:+.3f} $ par part** · taille dispo mediane {statistics.median([x['taille'] or 0 for x in T]):.0f} parts")
    open(OUT + "resultat_limitless.md", "w").write("\n".join(rap))
    print("\n".join(rap))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "sonde": sonde()
    else: mesure(int(sys.argv[2]) if len(sys.argv) > 2 else 150)
