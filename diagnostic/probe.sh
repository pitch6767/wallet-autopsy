G=https://gamma-api.polymarket.com
D=https://data-api.polymarket.com
echo "=== séries BTC"
for q in "btc-up-or-down" "bitcoin-up-or-down" "btc"; do curl -sS "$G/series?limit=200&slug=$q" | python3 -c "
import json,sys
for s in json.load(sys.stdin): print(s['id'],s['slug'],s.get('recurrence'),s.get('closed'))" ; done
curl -sS "$G/series?limit=1000" | python3 -c "
import json,sys
d=json.load(sys.stdin); print('nb series',len(d))
for s in d:
  t=(s.get('slug','')+' '+s.get('title','')).lower()
  if ('btc' in t or 'bitcoin' in t) and ('up' in t): print(s['id'],s['slug'],'|',s.get('title'),'|',s.get('recurrence'),'| closed',s.get('closed'))"
echo "=== events d'une série, ordre et pagination"
curl -sS "$G/events?series_id=10684&closed=true&order=endDate&ascending=false&limit=3" | python3 -c "
import json,sys
d=json.load(sys.stdin); print(len(d)); [print(e['slug'],e.get('endDate'),len(e.get('markets',[])), e['markets'][0].get('outcomePrices') if e.get('markets') else None) for e in d]"
curl -sS "$G/events?series_id=10684&closed=true&order=endDate&ascending=false&limit=500&offset=25000" | python3 -c "
import json,sys
d=json.load(sys.stdin); print('offset 25000 ->',len(d) if isinstance(d,list) else d, d[0]['slug'] if isinstance(d,list) and d else '')"
curl -sS "$G/events?series_id=10684&closed=true&end_date_min=2026-07-01T00:00:00Z&end_date_max=2026-07-01T01:00:00Z&limit=50" | python3 -c "
import json,sys
d=json.load(sys.stdin); print('fenetre date ->',len(d),[e['slug'] for e in d[:4]])"
echo "=== trades: filtres side / start"
CID=$(curl -sS "$G/markets?slug=btc-updown-5m-1790840700" | python3 -c "import json,sys;d=json.load(sys.stdin);print(d[0]['conditionId'] if d else '')")
echo "cid=$CID"
for p in "side=BUY" "side=SELL"; do N=0; for o in $(seq 0 500 6000); do c=$(curl -sS "$D/trades?market=$CID&limit=500&offset=$o&takerOnly=false&$p" | python3 -c "import json,sys;d=json.load(sys.stdin);print(len(d) if isinstance(d,list) else -1)"); N=$((N+c)); [ "$c" -lt 500 ] && break; done; echo "$p total $N"; done
