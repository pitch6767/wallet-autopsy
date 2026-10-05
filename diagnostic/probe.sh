curl -sS -m 30 https://bot95.pitch67.workers.dev/api/etat | python3 -c "
import json,sys;d=json.load(sys.stdin);e=d['e']
print({k:e[k] for k in ['capital','mise','reserve','pnl','gains','pertes','pause']});print('positions',e['positions']);print('attente',[p['slug'] for p in e['attente']])
print([(t['actif'],t['heure'],t.get('resultat'),t.get('net')) for t in e['trades'][:3]]);print(e['parActif']);print(d['diag'])"
