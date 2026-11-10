#!/bin/bash
U=$1
echo "--- sonde2"; curl -sS -m 120 "$U/api/sonde2" | jq -c '.[] | {nom, code, ms, err, debut: (.debut // "" | .[0:600])}'
