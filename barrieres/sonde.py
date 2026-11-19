import json, urllib.request, urllib.parse
def g(u):
    try:
        return json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent":"Mozilla/5.0"}), timeout=30))
    except Exception as e: return {"erreur": str(e)}
out=[]
for s in ["what-price-will-bitcoin-hit-in-november-2026","what-price-will-ethereum-hit-in-november-2026","what-price-will-bitcoin-hit-in-november","what-price-will-ethereum-hit-in-november"]:
    e=g("https://gamma-api.polymarket.com/events?slug="+s)
    out.append("=== "+s)
    if isinstance(e,list) and e:
        ev=e[0]; out.append(json.dumps({k:ev.get(k) for k in ["id","slug","title","endDate","description","resolutionSource"]})[:3000])
        for m in ev.get("markets",[])[:40]:
            out.append(json.dumps({k:m.get(k) for k in ["question","slug","endDate","bestBid","bestAsk","outcomePrices","clobTokenIds","closed","liquidityNum","volumeNum","orderMinSize","feesEnabled","takerBaseFee","makerBaseFee","feeSchedule"]}))
    else: out.append(str(e)[:300])
# recherche de secours
r=g("https://gamma-api.polymarket.com/public-search?q="+urllib.parse.quote("Bitcoin dip November"))
out.append("=== recherche"); out.append(json.dumps([ (x.get("slug"),x.get("title")) for x in (r.get("events") or [])][:15]) if isinstance(r,dict) else str(r)[:300])
d=g("https://www.deribit.com/api/v2/public/get_book_summary_by_currency?currency=BTC&kind=option")
res=d.get("result",[]) if isinstance(d,dict) else []
exp=sorted(set(x["instrument_name"].split("-")[1] for x in res))
out.append("=== deribit BTC echeances "+" ".join(exp))
out.append(json.dumps([x for x in res if "-P" in x["instrument_name"][-2:] or x["instrument_name"].endswith("-P")][:3])[:1500])
t=g("https://www.deribit.com/api/v2/public/ticker?instrument_name="+(res[0]["instrument_name"] if res else "BTC-PERPETUAL"))
out.append(json.dumps(t)[:1500])
c=g("https://www.deribit.com/api/v2/public/get_tradingview_chart_data?instrument_name=BTC-PERPETUAL&resolution=1&start_timestamp=0&end_timestamp=9999999999999")
out.append("=== chart keys "+str(list(c.get("result",{}).keys()) if isinstance(c,dict) and c.get("result") else c)[:300])
open("barrieres/sonde.txt","w").write("\n".join(out))
