import json, urllib.request, time
u="https://gamma-api.polymarket.com/events?slug=btc-updown-5m-%d" % (int(time.time())//300*300-300)
d=json.loads(urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"x"}),timeout=30).read())
print(d[0]["description"]); print("\nRESOLUTION SOURCE:", d[0].get("resolutionSource"), d[0]["markets"][0].get("resolutionSource"))
