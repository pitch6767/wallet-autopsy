U=https://wallet-autopsy.pitch67.workers.dev
echo "=== html"; curl -sSI -m 20 $U/ | grep -i "cache-control\|etag"; curl -sS -m 20 $U/ | grep -o "Chasseur de cotes\|Chasseur d'outsiders\|Tueurs à copier" | sort | uniq -c
echo "=== etat"; curl -sS -m 30 $U/api/btc/etat | python3 -c "
import json,sys; e=json.load(sys.stdin); print('traites',sum(r['traites'] or 0 for r in e['parType']),'attente',sum(r['attente'] or 0 for r in e['parType']),'wallets',e['portefeuilles'], e['dernierTour'])"
A=0x3750aa21fd677f569b63
echo "=== wallet trades sample"
W=$(curl -sS -m 60 "$U/api/btc/classement?tri=best_roi" | python3 -c "
import json,sys; d=json.load(sys.stdin)
for w in d['table']:
  if w['wallet'].startswith('0x3750'): print(w['wallet']); break")
echo "wallet $W"
curl -sS "https://data-api.polymarket.com/trades?user=$W&limit=40&takerOnly=false" | python3 -c "
import json,sys
for t in json.load(sys.stdin): print(t['side'],t['outcome'],t['size'],t['price'],t['timestamp'],t['slug'])"
curl -sS "https://gamma-api.polymarket.com/markets?condition_ids=0xbfa3f97cb8e62d3f2b8096baf02589937f11081e14c8f551854bde53b20dff6a&condition_ids=0x2885ae4442ef79e0977772e9e8d5c16830ac0f34e7d9a9cfaefadf1420350d20" | python3 -c "
import json,sys; d=json.load(sys.stdin); print('gamma multi', len(d), [(m['slug'], m.get('endDate'), m.get('outcomePrices')) for m in d])"
