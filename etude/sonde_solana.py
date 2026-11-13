# 13.11.2026 : autres sources publiques des transactions Polymarket (lecture seule)
import json, urllib.request, time
W = "0x3048d65321be3497164cdfc2996f94f98a2e7537"
def get(u, data=None):
    try:
        req = urllib.request.Request(u, data=data, headers={"User-Agent": "etude-btc5m", "Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as r: return r.status, r.read()[:500]
    except Exception as e: return "ERR", str(e)[:200]
for u in [f"https://data-api.polymarket.com/activity?user={W}&limit=3", f"https://data-api.polymarket.com/trades?user={W}&limit=3", f"https://data-api.polymarket.com/positions?user={W}&limit=3",
          f"https://data-api.polymarket.com/value?user={W}", f"https://data-api.polymarket.com/v1/trades?user={W}&limit=3", f"https://data-api.polymarket.com/closed-positions?user={W}&limit=3",
          "https://data-api.polymarket.com/v1/leaderboard?category=CRYPTO&timePeriod=DAY&orderBy=PNL&limit=5", "https://lb-api.polymarket.com/profit?window=1d&limit=5"]:
    s, b = get(u); print(u.split(".com")[1][:70], s, b[:300]); print()
q = json.dumps({"query": "{ orderFilledEvents(first: 3, orderBy: timestamp, orderDirection: desc) { timestamp maker taker makerAssetId takerAssetId makerAmountFilled takerAmountFilled } }"}).encode()
for u in ["https://api.goldsky.com/api/public/project_cl6mb8i9h0003e201j6li0diw/subgraphs/orderbook-subgraph/0.0.1/gn",
          "https://api.goldsky.com/api/public/project_cl6mb8i9h0003e201j6li0diw/subgraphs/activity-subgraph/0.0.4/gn"]:
    s, b = get(u, q); print("subgraph", u[-40:], s, b[:400]); print()
