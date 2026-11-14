#!/bin/bash
U=$1
echo "--- version"; curl -sS -m 20 "$U/api/version"; echo
echo "--- etat"; curl -sS -m 30 "$U/api/etat" | head -c 600; echo
echo "--- relais Dublin"; curl -sS -m 30 https://72-11-157-70.sslip.io/api/public/binance-funding | python3 -c "import json,sys;d=json.load(sys.stdin);print({k:(len(v) if isinstance(v,list) else v) for k,v in d.items()});[print(k, json.dumps(v[:1])[:300]) for k,v in d.items() if isinstance(v,list)]"
