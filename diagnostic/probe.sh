U=https://wallet-autopsy.pitch67.workers.dev
echo "=== page"; curl -sS -m 20 $U/ | grep -c "BTC historique"
echo "=== versions"; npm i -g wrangler@4 >/dev/null 2>&1; wrangler deployments list --name wallet-autopsy 2>&1 | grep -E "Created|Message|Version" | tail -9
echo "=== etat"; curl -sS -m 30 $U/api/btc/etat; sleep 90
echo; echo "=== etat 90 s"; curl -sS -m 30 $U/api/btc/etat
echo; echo "=== classement"; curl -sS -m 60 "$U/api/btc/classement" | head -c 600
