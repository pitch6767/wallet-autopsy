# 13.11.2026 : diagnostic de l'API publique des transactions Polymarket (lecture seule)
import json, urllib.request, time
def get(u):
    try:
        with urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "etude-btc5m"}), timeout=30) as r: return r.status, r.read()[:400]
    except Exception as e: return "ERR", str(e)[:300]
st = int(time.time()) // 300 * 300 - 3600
s, b = get(f"https://gamma-api.polymarket.com/events?slug=btc-updown-5m-{st}"); print("gamma", s, b[:200])
try:
    ev = json.loads(urllib.request.urlopen(urllib.request.Request(f"https://gamma-api.polymarket.com/events?slug=btc-updown-5m-{st}", headers={"User-Agent": "x"}), timeout=30).read())
    m = ev[0]["markets"][0]; cid = m["conditionId"]; print("conditionId", cid)
    for q in [f"market={cid}&limit=5", f"market={cid}&limit=5&takerOnly=false", f"market={cid}&limit=5&offset=0&takerOnly=true", f"market={cid}&limit=500&offset=0&takerOnly=false"]:
        s, b = get(f"https://data-api.polymarket.com/trades?{q}"); print("data-api", q[-40:], s, b[:300])
except Exception as e: print("erreur", e)
