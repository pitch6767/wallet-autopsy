"""Diagnostic des sources de données pour H681–H710 (lecture seule) : sous-graphe Goldsky de Polymarket (OrderFilled), limite d'offset de l'API Data, /activity."""
import json, time, urllib.request
def req(url, data=None):
    r = urllib.request.Request(url, data=json.dumps(data).encode() if data else None, headers={"User-Agent": "bot95-etude", "Content-Type": "application/json"})
    with urllib.request.urlopen(r, timeout=60) as f: return json.loads(f.read())
out = {}
G = "https://gamma-api.polymarket.com"; D = "https://data-api.polymarket.com"
st = int(time.time()) // 300 * 300 - 1800
ev = req(f"{G}/events?slug=btc-updown-5m-{st}")[0]; m = ev["markets"][0]; toks = json.loads(m["clobTokenIds"]); cid = m["conditionId"]
out["marche"] = {"slug": ev["slug"], "cid": cid, "toks": toks}
for nom, url in [("orderbook", "https://api.goldsky.com/api/public/project_cl6mb8i9h0003e201j6li0diw/subgraphs/orderbook-subgraph/0.0.1/gn"),
                 ("orderbook_prod", "https://api.goldsky.com/api/public/project_cl6mb8i9h0003e201j6li0diw/subgraphs/orderbook-subgraph/prod/gn")]:
    try:
        q = {"query": "{ orderFilledEvents(first: 5, orderBy: timestamp, orderDirection: desc, where: {makerAssetId: \"%s\"}) { id transactionHash timestamp maker taker makerAssetId takerAssetId makerAmountFilled takerAmountFilled fee } }" % toks[0]}
        out[nom] = req(url, q)
    except Exception as e: out[nom] = str(e)[:300]
for off in (3000, 5000, 9500, 10000, 20000):
    try: out[f"offset_{off}"] = len(req(f"{D}/trades?market={cid}&limit=500&offset={off}&takerOnly=false"))
    except Exception as e: out[f"offset_{off}"] = str(e)[:200]
try:
    t = req(f"{D}/trades?market={cid}&limit=3&takerOnly=false"); out["trade_exemple"] = t
    w = t[0]["proxyWallet"]; out["activity_exemple"] = req(f"{D}/activity?user={w}&limit=5")
except Exception as e: out["activity"] = str(e)[:200]
json.dump(out, open("bot95/diag_sources_makers.json", "w"), indent=1)
print(json.dumps(out, indent=1)[:4000])
