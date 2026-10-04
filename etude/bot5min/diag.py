import json, urllib.request
A="https://api.limitless.exchange"
def g(p):
    try:
        r=urllib.request.urlopen(urllib.request.Request(A+p,headers={"User-Agent":"etude","Accept":"application/json"}),timeout=40)
        return r.read().decode()
    except Exception as e:
        return "ERR "+str(e)
s=g("/markets/active?limit=25&page=1")
print("ACTIVE", s[:1500])
try:
    d=json.loads(s); L=d.get("data", d) if isinstance(d,dict) else d
except Exception: L=[]
btc=[m for m in L if "btc" in (m.get("slug","")+m.get("title","")).lower()]
print("\nBTC actifs:", [(m.get("slug"), m.get("title"), m.get("expirationTimestamp") or m.get("deadline")) for m in btc][:20])
sl=g("/markets/active/slugs"); print("\nSLUGS", sl[:2500])
slug = btc[0]["slug"] if btc else ""
for p in [f"/markets/{slug}", f"/markets/{slug}/historical-price?interval=1h", f"/markets/{slug}/get-feed-events?page=1&limit=10",
          f"/markets/{slug}/events?page=1&limit=10", f"/markets/{slug}/trades", f"/markets/{slug}/orderbook",
          "/markets/search?query=btc&limit=10", "/markets?status=RESOLVED&limit=5", "/markets/resolved?limit=5", "/categories"]:
    print("\n==", p); print(g(p)[:1800])
