U=https://wallet-autopsy.pitch67.workers.dev
sleep 120
for A in 0x3750aa21fd677f569b63fde892f773ee7dd02c42 $(curl -sS -m 60 "$U/api/btc/classement" | python3 -c "
import json,sys; d=json.load(sys.stdin); print(' '.join(w['wallet'] for w in d['tueurs'][:3]))"); do
echo "################ $A"
curl -sS -m 90 "$U/api/etude?addr=$A" | python3 -c "
import json,sys,re; e=json.load(sys.stdin)
if 'erreur' in e: print(e); sys.exit()
print('#',e['titre'],'| marches',e['marches'],e['meta'])
for c in e['constats']: print(' -',re.sub('<[^>]+>','',c['texte']))
print(' =>',e['verdict'])"
done
