G=https://gamma-api.polymarket.com
D=https://data-api.polymarket.com
echo "=== séries par slug"
for q in btc-up-or-down-5m btc-up-or-down-15m btc-up-or-down-hourly bitcoin-up-or-down-hourly btc-up-or-down-1h btc-up-or-down-4h btc-up-or-down-daily btc-up-or-down-weekly; do curl -sS "$G/series?slug=$q" | python3 -c "
import json,sys
d=json.load(sys.stdin)
print('$q ->', [(s['id'],s.get('recurrence'),s.get('closed')) for s in d] if isinstance(d,list) else d)"; done
echo "=== toutes séries paginées"
for o in 0 50 100 150 200 250 300 350 400 450 500 550 600 650 700; do curl -sS "$G/series?limit=50&offset=$o" | python3 -c "
import json,sys
d=json.load(sys.stdin)
for s in d:
  t=(s.get('slug','')+' '+s.get('title','')).lower()
  if ('btc' in t or 'bitcoin' in t) and ('up or down' in t or 'updown' in t or 'up-or-down' in t): print(s['id'],s['slug'],'|',s.get('title'),'|',s.get('recurrence'),'| closed',s.get('closed'))
if not d: print('fin offset $o')"; done
echo "=== nb events par série sur 1 jour (2026-09-29)"
for id in 10684 41; do curl -sS "$G/events?series_id=$id&closed=true&end_date_min=2026-09-29T00:00:00Z&end_date_max=2026-09-30T00:00:00Z&limit=500" | python3 -c "
import json,sys
d=json.load(sys.stdin); print('$id', len(d), d[0]['slug'] if d else '')"; done
echo "=== trades d'un 5m via events?slug, side filtre"
CID=$(curl -sS "$G/events?slug=btc-updown-5m-1790840700" | python3 -c "import json,sys;print(json.load(sys.stdin)[0]['markets'][0]['conditionId'])")
for p in "side=BUY" "side=SELL" "x=1"; do N=0; for o in $(seq 0 500 9500); do c=$(curl -sS "$D/trades?market=$CID&limit=500&offset=$o&takerOnly=false&$p" | python3 -c "import json,sys;d=json.load(sys.stdin);print(len(d) if isinstance(d,list) else -1)"); N=$((N+c)); [ "$c" -lt 500 ] && break; done; echo "$p total $N"; done
echo "=== taille d'un marché daily"
DC=$(curl -sS "$G/events?series_id=41&closed=true&order=endDate&ascending=false&limit=1" | python3 -c "import json,sys;e=json.load(sys.stdin)[0];print(e['markets'][0]['conditionId']);print(e['slug'],e['markets'][0].get('volume'),file=sys.stderr)")
c=$(curl -sS "$D/trades?market=$DC&limit=500&offset=9500&takerOnly=false" | python3 -c "import json,sys;d=json.load(sys.stdin);print(len(d) if isinstance(d,list) else -1)"); echo "daily offset 9500 -> $c"
