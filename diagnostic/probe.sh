U=https://wallet-autopsy.pitch67.workers.dev
c(){ curl -sS -m 60 "$U/api/btc/classement" | python3 -c "import json,sys; d=json.load(sys.stdin); print('etudes',d['etudesFaites'],'copiables',d['etudesCopiables'])"; }
c; sleep 300; c
npm i -g wrangler@4 >/dev/null 2>&1; wrangler triggers deploy 2>&1 | tail -4
