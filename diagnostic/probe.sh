U=https://wallet-autopsy.pitch67.workers.dev
sleep 30
for i in 1 2 3; do curl -sS -m 120 $U/api/btc/etudes; echo; done
curl -sS -m 60 "$U/api/btc/classement" | python3 -c "
import json,sys,re; d=json.load(sys.stdin)
print('etudes',d['etudesFaites'],'copiables',d['etudesCopiables'])
for w in d['tueurs']: print(w['nom'] or w['wallet'][:10], w['cible'], round(w['marge']*100), 'pts', round(w['roiCible']*100,1),'%', w['nCible'], re.sub('<[^>]+>','',w['verdict'])[:300])"
