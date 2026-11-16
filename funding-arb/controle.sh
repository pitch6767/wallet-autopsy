#!/bin/bash
U=$1
echo "--- version"; curl -sS -m 20 "$U/api/version"; echo
echo "--- bilan"; curl -sS -m 30 "$U/api/etat" | python3 -c "
import json,sys;d=json.load(sys.stdin);print('total',d['total']);print('ouvertes',len(d['ouvertes']))
for p in d['ouvertes'][:15]:print(' O',p['base'],'achat',p['long'],p['px_l_in'],'vente',p['short'],p['px_s_in'],'attendu',round(p['cout_est'],2),'provisoire',round(p['net'] or 0,2))
for p in d['fermees'][:25]:print(' F',p['base'],p['long'],p['short'],round((p['ferme']-p['ouvert'])/6e4),'min net',round(p['net'],2),p['raison'],'| achat in',p['px_l_in'],'out',p['px_l_out'],'| vente in',p['px_s_in'],'out',p['px_s_out'],'| fund',round(p['fund'],2),'att',round(p['cout_est'],2))
sc=d.get('scan') or {}
for p in (sc.get('top') or [])[:8]:print(' T',p['base'],p['achat'],p['ask'],p['vente'],p['bid'],round(p['ecart']*100,3),'%',round(p['gain'],2),'verif',p['verif'])"
echo "--- page"; curl -sS -m 20 -D - "$U/" | grep -iE "^cache-control|<h1|<h2|Version|<title" | sed 's/<[^>]*>/ /g' | head -20
echo "--- etat brut (début)"; curl -sS -m 30 "$U/api/etat" | head -c 1500; echo
echo "--- deribit CASHCAT"; curl -sS -m 20 "https://www.deribit.com/api/v2/public/get_instruments?currency=USDC&kind=future" | python3 -c "
import json,sys;d=json.load(sys.stdin)['result']
for i in d:
  if 'CASHCAT' in i['instrument_name'] or 'GIGA' in i['instrument_name'] or i['instrument_name'].startswith('SOL_'):print({k:i.get(k) for k in ['instrument_name','contract_size','tick_size','min_trade_amount','settlement_currency','base_currency']})"
curl -sS -m 20 "https://www.deribit.com/api/v2/public/get_order_book?instrument_name=CASHCAT_USDC-PERPETUAL&depth=5" | head -c 600; echo
