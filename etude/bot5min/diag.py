import json, urllib.request
s="sol-updown-5m-1791154800"
d=json.loads(urllib.request.urlopen(urllib.request.Request("https://gamma-api.polymarket.com/events?slug="+s,headers={"User-Agent":"x"}),timeout=30).read())[0]
m=d["markets"][0]; meta=d.get("eventMetadata") or m.get("eventMetadata")
print(s, "outcomes", m["outcomes"], "prices", m["outcomePrices"], "meta", meta)
