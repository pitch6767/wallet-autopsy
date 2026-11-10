#!/bin/bash
U=$1
echo "--- ok"; curl -sS -m 30 "$U/api/sonde" | head -c 200
