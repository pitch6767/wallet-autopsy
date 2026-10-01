U=https://wallet-autopsy.pitch67.workers.dev
curl -sS -m 60 "$U/api/btc/classement" | python3 -c "
import json,sys; d=json.load(sys.stdin)
for w in d['tueurs'][:20]:
  print((w['nom'] or w['wallet'][:10])[:16].ljust(16),'z',round(w['confiance'],1),'av',round(w['avantage']*100),'pts','n',w['n_marches'],'simple',w['nSimple'],'justes',w['justes'],'att',round(w['attendus'],1),'snip',w['sniper'],'lot',w['loterie'],'dir',w['dir'],'roi',round(w['roi']*100,1),'pnl',round(w['pnl']),'ord',round(w['ordresParMarche'],1),w['types'])"
