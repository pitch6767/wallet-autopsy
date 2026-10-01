U=https://wallet-autopsy.pitch67.workers.dev
echo "=== etat"; curl -sS -m 30 $U/api/btc/etat
echo; echo "=== tail 150 s"
npm i -g wrangler@4 >/dev/null 2>&1
timeout 150 wrangler tail wallet-autopsy --format json > /tmp/tail.json 2>/tmp/tail.err
python3 - <<'PY'
import json
n=0
for line in open('/tmp/tail.json'):
  pass
txt=open('/tmp/tail.json').read()
dec=json.JSONDecoder(); i=0
while i < len(txt):
  try:
    o,j=dec.raw_decode(txt,i); i=j
  except Exception:
    i+=1; continue
  ev=o.get('event') or {}
  if 'cron' in json.dumps(ev) or o.get('scriptName'):
    n+=1
    print('--', o.get('outcome'), 'cpu', o.get('cpuTime'), 'wall', o.get('wallTime'), str(ev)[:120])
    for l in o.get('logs',[]): print('  log', str(l.get('message'))[:300])
    for e in o.get('exceptions',[]): print('  EXC', e.get('name'), str(e.get('message'))[:300])
print('evenements', n)
PY
tail -5 /tmp/tail.err
echo "=== etat apres"; curl -sS -m 30 $U/api/btc/etat
