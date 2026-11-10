#!/bin/bash
U=$1
sleep 700
echo "--- par action"; curl -sS -m 60 "$U/api/par-action" | jq -c '{etat, n: (.lignes|length), tiennent: ([.lignes[]|select(.tient==1)]|length), ex: [.lignes[0:6][]|{sym, regle, an, ga, bn, gb}]}'
echo "--- excel"; curl -sS -m 120 -o /tmp/x.xlsx -w "%{http_code} %{size_download}\n" "$U/excel"
