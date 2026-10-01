U=https://wallet-autopsy.pitch67.workers.dev
curl -sS -m 30 $U/api/btc/etat | python3 -c "
import json,sys; e=json.load(sys.stdin); print('traites',sum(r['traites'] or 0 for r in e['parType']),'attente',sum(r['attente'] or 0 for r in e['parType']),'wallets',e['portefeuilles'], e['dernierTour'])"
curl -sS -m 60 "$U/api/btc/classement" | python3 -c "
import json,sys; d=json.load(sys.stdin)
print('erreur' in d and d, 'tueurs', len(d['tueurs']))
for w in d['tueurs'][:20]:
  print((w['nom'] or w['wallet'][:10])[:16].ljust(16),'z',round(w['confiance'],1),'av',round(w['avantage']*100),'n',w['n_marches'],'justes',w['justes'],'att',round(w['attendus'],1),'snip',w['sniper'],'lot',w['loterie'],'dir',w['dir'],'scalp',w['scalp'],'avant',round(w['avantFinMoyen'] or 0),'roi',round(w['roi']*100,1),'pnl',round(w['pnl']),'ord',round(w['ordresParMarche'],1),w['types'])"
