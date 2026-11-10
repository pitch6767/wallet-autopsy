#!/bin/bash
U=$1
echo "--- reponse brute"; curl -sS -m 30 -i "$U/api/sonde" | head -30
