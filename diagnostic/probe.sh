U=https://bot95.pitch67.workers.dev
curl -sS -m 30 "$U/api/etat" -o /tmp/e.json
python3 - <<'PY'
import json,time
d=json.load(open('/tmp/e.json'));e=d['e']
print("now",time.strftime('%Y-%m-%d %H:%M:%S',time.gmtime()),"UTC")
for k in ['capital','mise','reserve','pnl','gains','pertes','pause','depuis','vetos','candidats','parActif','positions','attente']:
  print(k,json.dumps(e.get(k),ensure_ascii=False))
print("ntrades",len(e['trades']))
for t in e['trades'][:60]: print(json.dumps(t,ensure_ascii=False))
for a in d['actifs']: print(json.dumps(a,ensure_ascii=False))
print(json.dumps(d['diag'],ensure_ascii=False))
PY
echo "=== rapport refus"
curl -sS -m 30 "$U/api/rapport" | python3 -c "
import json,sys,collections;r=json.load(sys.stdin)['refus'];print('n',len(r));c=collections.Counter()
for x in r: c[(x.get('a'),x.get('raison') or x.get('motif'))]+=1
[print(k,v) for k,v in c.most_common(40)];print(json.dumps(r[:5],ensure_ascii=False))"
