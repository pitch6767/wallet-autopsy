U=https://wallet-autopsy.pitch67.workers.dev
curl -sS -m 20 "$U/?x=$RANDOM" | grep -o "gains sont rares\|rendreEtude\|Tueurs à copier" | sort | uniq -c
curl -sS -m 60 "$U/api/btc/classement" | python3 -c "
import json,sys,re; d=json.load(sys.stdin)
print('etudes',d['etudesFaites'],'copiables',d['etudesCopiables'])
for w in d['tueurs']: print(w['wallet'], (w['nom'] or '')[:18], w['cible'], round(w['marge']*100),'pts', round(w['roiCible']*100,1),'%', w['nCible'],'/',w['n_marches'], 'avant', w['avant'], 'pnl', round(w['pnl']))"
