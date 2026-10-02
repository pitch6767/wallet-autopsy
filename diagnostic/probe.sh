echo "################ POLYMARKET 60 JOURS"
timeout 2400 python3 etude/quasi_certains.py 60 &
P=$!
timeout 2400 python3 etude/kalshi.py 30 > /tmp/kalshi.txt 2>&1
wait $P
echo; echo "################ KALSHI 30 JOURS"
cat /tmp/kalshi.txt
