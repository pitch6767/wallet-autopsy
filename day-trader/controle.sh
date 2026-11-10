#!/bin/bash
U=$1
echo "--- papier"; curl -sS -m 60 "$U/api/papier" | jq -c '[.regles[0:3][]|{regle, gain, actions: [.actions[0:5][]|"\(.sym) \(.gain)"]}]'
echo "--- page"; curl -sS -m 30 "$U/" | grep -c ligneActions
