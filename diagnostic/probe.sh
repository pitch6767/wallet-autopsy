# Etude teneur de marche Polymarket - etape 1 : forme des donnees
G=https://gamma-api.polymarket.com; C=https://clob.polymarket.com; D=https://data-api.polymarket.com
echo "=== gamma marches recompenses"
curl -sS -m 60 "$G/markets?active=true&closed=false&limit=3&order=volume24hr&ascending=false" | python3 -c "
import json,sys; d=json.load(sys.stdin)
for m in d[:2]:
  print({k:m.get(k) for k in ['question','conditionId','clobTokenIds','rewardsMinSize','rewardsMaxSpread','clobRewards','volume24hr','liquidity','spread','bestBid','bestAsk','endDate','negRisk']})
print(sorted(d[0].keys()))"
echo; echo "=== clob rewards current"
curl -sS -m 60 "$C/rewards/markets/current" | head -c 1500
echo; echo "=== clob sampling-markets"
curl -sS -m 60 "$C/sampling-markets" | head -c 1500
