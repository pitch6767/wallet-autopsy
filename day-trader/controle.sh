#!/bin/bash
U=$1
echo "--- relance du test"; curl -sS -m 300 -X POST "$U/api/test/demarrer" | jq -c "{n: (.liste|length)}"
sleep 600
echo "--- test"; curl -sS -m 60 "$U/api/test" | jq -c '{pos: .etat.pos, fini: .etat.fini, echecs: .etat.echecs, erreurs: .etat.erreurs}'
echo "--- combos"; curl -sS -m 120 "$U/api/combos" | jq -c '{nbRegles, totalRegles, avecAssezDeTrades, tiennent, top: [.top[0:8][]|{regle, A: .A.contreQqq, B: .B.contreQqq, tB: .B.t, nB: .B.trades}]}'
echo "--- excel"; curl -sS -m 120 -o /tmp/x.xlsx -w "%{http_code} %{content_type} %{size_download}\n" "$U/excel"; python3 -c "import zipfile; print(zipfile.ZipFile('/tmp/x.xlsx').namelist())"
