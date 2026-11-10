#!/bin/bash
# Contrôles après déploiement (résultats raccourcis)
U=$1
echo "--- scan-jour (liste triée)"; curl -sS -m 300 -X POST "$U/api/scan-jour" | jq -c '{duree, comptes, top: [.hits[0:3][].symbol]}'
echo "--- regles"; curl -sS -m 60 "$U/api/regles" | jq -c '{n: (.regles|length), news: (.news|length)}'
sleep 100
echo "--- etat taches"; curl -sS -m 60 "$U/api/etat" | jq -c '.taches'
echo "--- test"; curl -sS -m 120 "$U/api/test" | jq -c '{etat: (.etat|{pos, total: (.liste|length), coupure, seances, fini}), regles: (.regles|length), top: [.regles|sort_by(-(.B.gain // -1e9))|.[0:5][]|{regle, A: .A.gain, B: .B.gain}], choix: .choixSurA}'
echo "--- papier"; curl -sS -m 60 "$U/api/papier" | jq -c '{depuis, jusqua, n: (.regles|length), top: [.regles[0:5][]|{regle, trades, gain}]}'
echo "--- news"; curl -sS -m 60 "$U/api/news" | jq -c '{veilleur, n: (.dernieres|length), ex: [.dernieres[0:3][]|{sym, items, prix0, en_seance}]}'
