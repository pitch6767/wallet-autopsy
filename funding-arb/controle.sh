#!/bin/bash
U=$1
echo "--- version"; curl -sS -m 20 "$U/api/version"; echo
echo "--- bilan"; curl -sS -m 30 "$U/api/etat" | python3 -c "
import json,sys;d=json.load(sys.stdin);print('total',d['total']);print('anciennes',d.get('anciennes'));print('ouvertes',len(d['ouvertes']))
for p in d['ouvertes'][:15]:print(' O',p['base'],'regles',p.get('regles'),'qte_l',p.get('qte_l'),'qte_s',p.get('qte_s'),'carnet lu il y a',round((d['t']-(p.get('vu') or 0))/6e4),'min','achat',p['long'],p['px_l_in'],'vente',p['short'],p['px_s_in'],'attendu',round(p['cout_est'],2),'provisoire',round(p['net'] or 0,2))
for p in d['fermees'][:25]:print(' F',p['base'],p['long'],p['short'],round((p['ferme']-p['ouvert'])/6e4),'min net',round(p['net'],2),p['raison'],'| achat in',p['px_l_in'],'out',p['px_l_out'],'| vente in',p['px_s_in'],'out',p['px_s_out'],'| fund',round(p['fund'],2),'att',round(p['cout_est'],2))
sc=d.get('scan') or {}
for p in (sc.get('top') or [])[:8]:print(' T',p['base'],p['achat'],p['ask'],p['vente'],p['bid'],round(p['ecart']*100,3),'%',round(p['gain'],2),'verif',p['verif'])"
echo "--- page"; curl -sS -m 20 -D - "$U/" | grep -iE "^cache-control|<h1|<h2|Version|<title" | sed 's/<[^>]*>/ /g' | head -20
echo "--- etat brut (début)"; curl -sS -m 30 "$U/api/etat" | head -c 1500; echo
echo "--- statut plateformes x5 (toutes les 60 s)"; for k in 1 2 3 4 5; do curl -sS -m 30 "$U/api/etat" | python3 -c "
import json,sys;d=json.load(sys.stdin);s=(d.get('scan') or {}).get('statut',{});import time
print(round((time.time()*1000-(d.get('t') or 0))/1000),'s', {k:(v['ok'], v.get('n'), v.get('ms'), (v.get('err') or '')[:90]) for k,v in s.items()})"; sleep 60; done
