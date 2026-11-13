# 13.11.2026 : part « preneur » exacte de 3 portefeuilles (API v2 : taker_only=true ne renvoie que le côté preneur) — lecture seule
import json, urllib.request, time
W = {"0xc53375ff94e96100f2b30a4b5775db35218d69a9": "c533", "0x0ca4e9d27ff826a109ecbf74754fb66b93f277a6": "0ca4", "0xeebde7a0e019a63e6b476eb425505b7b3e6eba30": "eebd"}
def get(u):
    for k in range(4):
        try: return json.loads(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "etude-btc5m"}), timeout=60).read())
        except Exception as e: time.sleep(3)
    return None
def tout(cid, taker):
    T, cur = [], None
    for _ in range(80):
        r = get(f"https://data-api.polymarket.com/v2/trades?condition={cid}&limit=1000&taker_only={'true' if taker else 'false'}&filter_amount=0" + (f"&cursor={cur}" if cur else ""))
        if not r or not r.get("data"): break
        T += r["data"]; cur = (r.get("pagination") or {}).get("next_cursor")
        if not cur: break
    return T
fin = int(time.time()) // 300 * 300 - 900
tot = {w: [0, 0, 0.0, 0.0] for w in W}
for st in range(fin - 300 * 24, fin, 300):   # 24 cycles des 2 dernières heures
    ev = get(f"https://gamma-api.polymarket.com/events?slug=btc-updown-5m-{st}")
    if not ev: continue
    cid = ev[0]["markets"][0]["conditionId"]
    A, P = tout(cid, False), tout(cid, True)
    for x in A:
        w = x.get("proxy_wallet")
        if w in tot and x.get("side") == "BUY": tot[w][0] += 1; tot[w][2] += float(x["price"]) * float(x["size"])
    for x in P:
        w = x.get("proxy_wallet")
        if w in tot and x.get("side") == "BUY": tot[w][1] += 1; tot[w][3] += float(x["price"]) * float(x["size"])
for w, (n, nt, v, vt) in tot.items():
    print(W[w], f"achats {n}, dont comme PRENEUR {nt} ({100*nt/max(1,n):.0f} %) ; en $ : {v:.0f}, preneur {vt:.0f} ({100*vt/max(1,v):.0f} %) → ordres posés (maker) {100-100*vt/max(1,v):.0f} % des $")
