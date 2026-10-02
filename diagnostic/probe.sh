G=https://gamma-api.polymarket.com; D=https://data-api.polymarket.com
curl -sS -m 60 "$G/markets?closed=true&limit=5&order=closedTime&ascending=false&volume_num_min=20000" | python3 -c "
import json,sys; d=json.load(sys.stdin); print(len(d))
for m in d[:5]:
  e=(m.get('events') or [{}])[0]
  print({k:m.get(k) for k in ['question','conditionId','outcomes','outcomePrices','endDate','closedTime','gameStartTime','sportsMarketType','umaEndDate','volumeNum','category']}, '| event tags:', [t.get('label') for t in (e.get('tags') or [])][:5], 'ecat', e.get('category'))
"
echo; C=$(curl -sS -m 60 "$G/markets?closed=true&limit=1&order=closedTime&ascending=false&volume_num_min=20000" | python3 -c "import json,sys;print(json.load(sys.stdin)[0]['conditionId'])")
curl -sS -m 60 "$D/trades?market=$C&limit=3&takerOnly=false" | head -c 1500
