#!/bin/bash
U=$1
echo "--- version"; curl -sS -m 20 "$U/api/version"; echo
echo "--- etat"; curl -sS -m 30 "$U/api/etat" | head -c 600; echo
echo "--- sonde binance"; curl -sS -m 90 "$U/api/sonde-binance"; echo
