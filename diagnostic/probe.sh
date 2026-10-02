echo "################ N°3 FINANCEMENT HYPERLIQUID"
timeout 1200 python3 etude/funding.py
echo; echo "################ N°5 LIQUIDATIONS AAVE V3"
timeout 1500 python3 etude/liquidations.py
