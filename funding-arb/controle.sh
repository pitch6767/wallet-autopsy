#!/bin/bash
U=$1
echo "--- version"; curl -sS -m 20 "$U/api/version"; echo
echo "--- bilan"; curl -sS -m 30 "$U/api/etat" | python3 -c "
import json,sys;d=json.load(sys.stdin);print('total',d['total']);print('ouvertes',len(d['ouvertes']))
for p in d['ouvertes'][:15]:print(' O',p['base'],p['short'],p['long'],round((p['dernier']-p['ouvert'])/3.6e6,1),'h fund',round(p['fund'],2),'frais',round(p['frais'],2))
for p in d['fermees'][:25]:print(' F',p['base'],p['short'],p['long'],round((p['ferme']-p['ouvert'])/3.6e6,1),'h fund',round(p['fund'],2),'frais',round(p['frais'],2),'net',round(p['net'],2),p['raison'])
print({k:(v['ok'],v.get('n')) for k,v in d['scan']['statut'].items()})"
