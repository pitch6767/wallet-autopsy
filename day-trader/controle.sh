#!/bin/bash
# Contrôles après déploiement (résultats raccourcis)
U=$1
c() { echo "--- $1"; shift; curl -sS -m 300 "$@" | head -c 1500; echo; }
c etat "$U/api/etat"
c trade-TSLA -X POST -H "content-type: application/json" -d '{"symbol":"TSLA","cible":"1R"}' "$U/api/trade"
c trade-BTC -X POST -H "content-type: application/json" -d '{"symbol":"BTC"}' "$U/api/trade"
c nouvelles "$U/api/nouvelles?symbols=TSLA,BTC&heures=24"
c congres "$U/api/congres?membre=pelosi"
echo "--- analyste"; curl -sS -m 120 "$U/api/analyste?symbol=AAPL" | jq -c "{nom, erreur, l: [.lignes[0:2][]? | {fin, revenu, bpa, revenuSurUnAn}]}"
echo "--- 8-K"; curl -sS -m 120 "$U/api/nouvelles?symbols=AAPL&heures=720" | jq -c "[.[] | {depots, erreurs}]"
echo "--- scan-jour (comptes)"; curl -sS -m 300 -X POST "$U/api/scan-jour" | jq -c '{duree, comptes, nb: (.hits|length), btc: [.hits[]|select(.symbol=="BTC")]}'
c orb -X POST -H "content-type: application/json" -d '{}' "$U/api/orb"
