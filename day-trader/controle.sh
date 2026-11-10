#!/bin/bash
U=$1
echo "--- regles"; curl -sS -m 60 "$U/api/regles" | jq -c '{n: (.regles|length), familles: ([.regles[].famille]|group_by(.)|map({(.[0]): length})|add)}'
sleep 150
echo "--- etat taches"; curl -sS -m 60 "$U/api/etat" | jq -c '.taches | with_entries(select(.key|test("test|papier")))'
echo "--- test"; curl -sS -m 120 "$U/api/test" | jq -c '{pos: .etat.pos, regles: (.regles|length), tiennent: [.regles[]|select(.tient)|.regle][0:10], ex: [.regles[]|select(.regle|test("res-|veille|tm"))|{regle, A: .A.trades, B: .B.trades}][0:8]}'
echo "--- erreurs"; curl -sS -m 60 "$U/api/test" | jq -c "{pos: .etat.pos, echecs: .etat.echecs, erreurs: .etat.erreurs}"
