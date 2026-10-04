import json, time, urllib.request
from datetime import datetime, timezone
def g(u):
    try:
        r=urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"Mozilla/5.0","Accept":"application/json"}),timeout=30)
        return r.status, r.read().decode()[:1500]
    except Exception as e: return "ERR", str(e)[:300]
now=int(time.time()); st=now//300*300; prev=st-300
iso=lambda t: datetime.fromtimestamp(t,timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
for s0 in (st, prev):
    print("\n#### fenetre", s0, iso(s0), "maintenant", iso(now))
    for u in [f"https://polymarket.com/api/crypto/crypto-price?symbol=BTC&eventStartTime={iso(s0)}&variant=fiveminute&endDate={iso(s0+300)}",
              f"https://polymarket.com/api/crypto/crypto-price?symbol=BTC&eventStartTime={iso(s0)}&variant=fiveminute",
              f"https://gamma-api.polymarket.com/events?slug=btc-updown-5m-{s0}"]:
        c,b=g(u); 
        if "gamma" in u:
            try: d=json.loads(b) if c==200 else None
            except Exception: d=None
            print("GAMMA", c, (d[0].get("eventMetadata") if d else b[:300]))
        else: print(c, u[:110], "->", b[:600])
