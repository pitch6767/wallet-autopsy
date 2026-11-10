#!/bin/bash
U=$1
sleep 240
echo "--- news"; curl -sS -m 60 "$U/api/news" | jq -c '{veilleur, parSource, course: (.course|{paires, prnPremier, secPremier, avanceMediane}), ex: [.dernieres[0:6][]|{source, sym, prix0, hl0, kf0, titre: (.titre // "" | .[0:60])}]}'
echo "--- taches"; curl -sS -m 60 "$U/api/etat" | jq -c '.taches | with_entries(select(.key|test("erreur|jetons|test")))'
