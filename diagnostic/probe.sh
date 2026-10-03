U=https://wallet-autopsy.pitch67.workers.dev
sleep 150
# Remise à jour accélérée des études copiables (4 files en parallèle, ~45 min)
for o in 0 4 8 12; do ( for i in $(seq 1 60); do curl -sS -m 120 -A curl "$U/api/btc/etudes?off=$o" >/dev/null; done ) & done; wait
curl -sS -m 60 -A curl "$U/api/btc/conseils" | python3 -c "
import json,sys; d=json.load(sys.stdin); print('candidats',d['candidats'],'etudies',d['etudies'])
for w in d['choix']: print(w['wallet'], (w['nom'] or '')[:16], w['cible'], round(w['marge']*100),'pts', w['n'], round(w['roi']*100,1),'%', int(w['avant']),'s', round(w['r1']*100,1), round(w['r2']*100,1), round(w['recent']*100,1), 'mise', round(w['mise'] or 0), 'clones', w['clones'])"
