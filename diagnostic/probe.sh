G=https://gamma-api.polymarket.com
D=https://data-api.polymarket.com
echo "=== markets fermés sur 3h hier, filtrés Bitcoin Up or Down"
curl -sS "$G/markets?closed=true&end_date_min=2026-09-30T00:00:00Z&end_date_max=2026-09-30T03:00:00Z&limit=500" | python3 -c "
import json,sys,collections
d=json.load(sys.stdin); print('total renvoyes',len(d))
b=[m for m in d if 'bitcoin up or down' in (m.get('question') or '').lower()]
print('btc updown',len(b))
c=collections.Counter()
for m in b:
  s=m['slug']; c[s.rsplit('-',1)[0] if s.split('-')[-1].isdigit() else s[:30]]+=1
print(c.most_common(20))
for m in b[:3]: print({k:m.get(k) for k in ['slug','question','startDate','endDate','outcomePrices','closed','volume','umaResolutionStatus']})
for m in b:
  if not m['slug'].split('-')[-1].isdigit(): print('NONNUM', m['slug'], m.get('startDate'), m.get('endDate')); break
"
echo "=== pagination offset: markets 2026-07-03"
curl -sS "$G/markets?closed=true&end_date_min=2026-07-03T00:00:00Z&end_date_max=2026-07-03T02:00:00Z&limit=500" | python3 -c "
import json,sys; d=json.load(sys.stdin); b=[m for m in d if 'bitcoin up or down' in (m.get('question') or '').lower()]; print(len(d), len(b), [m['slug'] for m in b[:6]])"
echo "=== events series"
curl -sS "$G/series?slug=btc-up-or-down-5m" | head -c 400; echo
curl -sS "$G/events?series_slug=btc-up-or-down-5m&closed=true&limit=3" | head -c 400; echo
echo "=== offset cap trades"
CID=$(curl -sS "$G/markets?slug=btc-updown-5m-1790840700" | python3 -c "import json,sys;print(json.load(sys.stdin)[0]['conditionId'])")
for o in 9500 10000 10500 15000; do echo -n "offset $o: "; curl -sS "$D/trades?limit=500&offset=$o&takerOnly=false" | head -c 150; echo; done
echo "=== un marché 1h : nb trades"
H=$(curl -sS "$G/markets?closed=true&end_date_min=2026-09-30T00:00:00Z&end_date_max=2026-09-30T03:00:00Z&limit=500" | python3 -c "
import json,sys
for m in json.load(sys.stdin):
  q=(m.get('question') or '').lower()
  if 'bitcoin up or down' in q and not m['slug'].split('-')[-1].isdigit(): print(m['conditionId']); break")
N=0; for o in $(seq 0 500 12000); do c=$(curl -sS "$D/trades?market=$H&limit=500&offset=$o&takerOnly=false" | python3 -c "import json,sys;d=json.load(sys.stdin);print(len(d) if isinstance(d,list) else -1)"); [ "$c" -le 0 ] && { echo "arret offset $o code $c"; break; }; N=$((N+c)); [ "$c" -lt 500 ] && break; done; echo "trades 1h: $N"
