"""Kalshi et Limitless bougent-ils plus vite que Polymarket ? (07.10.2026, question de Pitch)
Pendant N minutes, chaque seconde : prix BTC (Binance spot), milieu Polymarket BTC Up/Down 15 min, milieu Kalshi BTC 15 min (KXBTC15M),
et les marches BTC courts de Limitless s'il y en a. Puis : apres un mouvement du BTC, combien de secondes avant que chaque place reagisse,
et quelle place bouge avant l'autre.
"""
import json, sys, time, math, statistics, urllib.request, collections

OUT = "etude/bot5min/"


def get(url, t=8):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "etude", "Accept": "application/json"}), timeout=t) as r: return json.loads(r.read())
    except Exception as e:
        return None


def log(*a): print(*a, flush=True)


POLY = {}
def poly_up(now):
    st = int(now) // 900 * 900
    if POLY.get("st") != st:
        ev = get(f"https://gamma-api.polymarket.com/events?slug=btc-updown-15m-{st}")
        try:
            m = ev[0]["markets"][0]; toks = json.loads(m["clobTokenIds"]); outs = json.loads(m["outcomes"])
            POLY.update(st=st, tok=toks[outs.index("Up")])
        except Exception: POLY.update(st=st, tok=None)
    if not POLY.get("tok"): return None, st
    b = get(f"https://clob.polymarket.com/book?token_id={POLY['tok']}")
    try:
        bid = max(float(x["price"]) for x in b["bids"]); ask = min(float(x["price"]) for x in b["asks"]); return (bid + ask) / 2, st
    except Exception: return None, st


KAL = {}
def kalshi(now):
    if not KAL.get("tk") or now > KAL.get("fin", 0):
        r = get("https://api.elections.kalshi.com/trade-api/v2/markets?series_ticker=KXBTC15M&status=open&limit=20")
        try:
            M = sorted(r["markets"], key=lambda m: m["close_time"])
            m = M[0]; KAL.update(tk=m["ticker"], fin=time.mktime(time.strptime(m["close_time"][:19], "%Y-%m-%dT%H:%M:%S")) - time.timezone, titre=m.get("title"))
        except Exception: KAL.update(tk=None, fin=now + 30)
    if not KAL.get("tk"): return None
    r = get(f"https://api.elections.kalshi.com/trade-api/v2/markets/{KAL['tk']}")
    try:
        m = r["market"]; yb = m.get("yes_bid_dollars") or (m.get("yes_bid", 0) / 100); ya = m.get("yes_ask_dollars") or (m.get("yes_ask", 0) / 100)
        yb, ya = float(yb), float(ya)
        return (yb + ya) / 2 if ya > 0 else None
    except Exception: return None


LIM = {}
def limitless(now):
    if "liste" not in LIM or now - LIM.get("t", 0) > 300:
        LIM["t"] = now; LIM["liste"] = []
        for url in ("https://api.limitless.exchange/markets/active", "https://api.limitless.exchange/markets/active?limit=100"):
            r = get(url)
            data = (r or {}).get("data") if isinstance(r, dict) else r
            for m in data or []:
                ti = (m.get("title") or "") + " " + (m.get("slug") or "")
                if re.search(r"btc|bitcoin", ti, re.I) and re.search(r"15|min|hour|1h", ti, re.I): LIM["liste"].append(m.get("slug"))
            if LIM["liste"]: break
        LIM["liste"] = LIM["liste"][:1]
    if not LIM["liste"]: return None
    r = get(f"https://api.limitless.exchange/markets/{LIM['liste'][0]}")
    try:
        p = r.get("prices") or r.get("price")
        return float(p[0]) / (100 if float(p[0]) > 1 else 1)
    except Exception: return None


import re


def main():
    duree = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    S = []
    t_fin = time.time() + 60 * duree
    while time.time() < t_fin:
        t0 = time.time()
        btc = get("https://data-api.binance.vision/api/v3/ticker/price?symbol=BTCUSDT")
        p, st = poly_up(t0); k = kalshi(t0); l = limitless(t0)
        S.append((round(t0), float(btc["price"]) if btc else None, p, k, l, st))
        time.sleep(max(0, 1 - (time.time() - t0)))
    log("points", len(S), "kalshi", KAL.get("titre"), "limitless", LIM.get("liste"))
    rap = [f"# Vitesse des places — {len(S)} secondes", "", f"Kalshi : {KAL.get('titre')} · Limitless : {LIM.get('liste') or 'aucun marche BTC court trouve'}", ""]
    noms = {2: "Polymarket 15 min", 3: "Kalshi 15 min", 4: "Limitless"}
    # 1. reaction apres un mouvement du BTC (>= 5 pb en 3 s)
    rap += ["## Apres un mouvement du BTC (≥ 5 pb en 3 s) : secondes avant que la place bouge d'au moins 1 cent dans le bon sens", "",
            "| Place | Mouvements | Reagit dans 1 s | dans 3 s | dans 10 s | Delai median |", "|---|---|---|---|---|---|"]
    for j, nom in noms.items():
        D = []; n = 0; dernier = -99
        for i in range(3, len(S) - 15):
            if not S[i][1] or not S[i - 3][1] or S[i][5] != S[i - 3][5]: continue
            mv = (S[i][1] / S[i - 3][1] - 1) * 1e4
            if abs(mv) < 5 or i - dernier < 10: continue
            dernier = i
            p0 = S[i - 3][j]
            if p0 is None: continue
            n += 1; d = None
            for h in range(-3, 15):
                ph = S[i + h][j]
                if ph is not None and S[i + h][5] == S[i][5] and (ph - p0) * mv > 0 and abs(ph - p0) >= 0.01: d = h + 3; break
            D.append(d)
        if n:
            ok = lambda s: 100 * sum(1 for d in D if d is not None and d <= s) / n
            med = statistics.median([d for d in D if d is not None]) if any(d is not None for d in D) else None
            rap.append(f"| {nom} | {n} | {ok(1):.0f} % | {ok(3):.0f} % | {ok(10):.0f} % | {med} s |")
    # 2. qui mene entre places : correlation des variations a decalage
    rap += ["", "## Qui mene ? correlation des variations (1 s) de A a l'instant t avec B a t + d", "", "| A -> B | d=-3 | -2 | -1 | 0 | +1 | +2 | +3 |", "|---|---|---|---|---|---|---|---|"]
    def dif(j):
        return [None if (S[i][j] is None or S[i - 1][j] is None or S[i][5] != S[i - 1][5]) else S[i][j] - S[i - 1][j] for i in range(1, len(S))]
    for a, b in ((2, 3), (2, 4), (3, 4)):
        A, B = dif(a), dif(b); cs = []
        for d in range(-3, 4):
            X = [(A[i], B[i + d]) for i in range(max(0, -d), min(len(A), len(B) - d)) if A[i] is not None and B[i + d] is not None]
            if len(X) < 100: cs.append("—"); continue
            xa = [x for x, _ in X]; xb = [y for _, y in X]
            try: cs.append(f"{statistics.correlation(xa, xb):.2f}")
            except Exception: cs.append("—")
        rap.append(f"| {noms[a]} -> {noms[b]} | " + " | ".join(cs) + " |")
    rap += ["", "Lecture : si la correlation est la plus forte a d = +1 ou +2, A bouge avant B (B suit A avec ce retard)."]
    open(OUT + "resultat_vitesse_places.md", "w").write("\n".join(rap))
    json.dump(S, open(OUT + "vitesse_places_brut.json", "w"))
    print("\n".join(rap))


if __name__ == "__main__":
    main()
