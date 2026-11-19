#!/bin/bash
U=$1
echo "--- version"; curl -sS -m 20 "$U/api/version"; echo
echo "--- page"; curl -sS -m 20 -D - "$U/" -o /tmp/p.html | grep -i "^cache-control"; grep -o "barrieres-app" /tmp/p.html | head -1; grep -o "version [0-9.]*" /tmp/p.html | head -1
echo "--- etat"; curl -sS -m 60 "$U/api/etat" | python3 -c "
import json,sys;d=json.load(sys.stdin);dl=d.get('dernier',{})
print('journal',dl.get('journal'));L=dl.get('lignes',[]);print('lignes',len(L))
for l in sorted([x for x in L if 'pm' in x],key=lambda x:-max(x.get('na') or -9,x.get('nv') or -9))[:25]:
  print(l['actif'],l['sens'],l['niveau'],'bid/ask',l['yesBid'],l['yesAsk'],'NONask',l['noAsk'],'p_opt',round(l['po'],3),'p_mod',round(l['pm'],3),'gainOUI',None if l['na'] is None else round(l['na']*1000),'gainNON',None if l['nv'] is None else round(l['nv']*1000),l['ech'],l['k'],'dec',round(l['dec']))
for l in [x for x in L if 'raison' in x][:15]:print(' X',l['actif'],l['sens'],l['niveau'],l['raison'])
print('positions',len(d['positions']))
for p in d['positions'][:10]:print(' P',p['actif'],p['sens'],p['niveau'],p['cote'],p['px_poly'],p['contrats'],p['echeance'],p['k_bas'],p['k_haut'],'prime',round(p['prime_couv']),'frais',round(p['frais_couv']),'attendu',round(p['net_attendu']))
print('bilan',d['bilan'])"
