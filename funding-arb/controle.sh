#!/bin/bash
U=$1
echo "--- version"; curl -sS -m 20 "$U/api/version"; echo
echo "--- bilan"; curl -sS -m 30 "$U/api/etat" | python3 -c "
import json,sys;d=json.load(sys.stdin);print('total',d['total']);print('ouvertes',len(d['ouvertes']))
for p in d['ouvertes'][:15]:print(' O',p['base'],'achat',p['long'],p['px_l_in'],'vente',p['short'],p['px_s_in'],'attendu',round(p['cout_est'],2),'provisoire',round(p['net'] or 0,2))
for p in d['fermees'][:25]:print(' F',p['base'],p['long'],p['short'],round((p['ferme']-p['ouvert'])/6e4),'min net',round(p['net'],2),p['raison'])
sc=d.get('scan') or {}
for p in (sc.get('top') or [])[:8]:print(' T',p['base'],p['achat'],p['ask'],p['vente'],p['bid'],round(p['ecart']*100,3),'%',round(p['gain'],2),'verif',p['verif'])"
