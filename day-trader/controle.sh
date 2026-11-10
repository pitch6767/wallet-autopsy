#!/bin/bash
U=$1
sleep 780
echo "--- par action"; curl -sS -m 60 "$U/api/par-action" | jq -c '{etat, n: (.lignes|length), tiennent: ([.lignes[]|select(.tient==1)]|length), edgePos: ([.lignes[]|select(.edge>0)]|length), toujours: ([.lignes[]|select(.regle|test("^[0-9]j:(grosse|volatile)$"))]|length), ex: [.lignes[0:8][]|{sym, regle, ga, gb, edge, garder}]}'
