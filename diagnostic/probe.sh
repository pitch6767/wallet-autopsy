echo "################ N°3 FINANCEMENT HYPERLIQUID"
timeout 1800 python3 etude/funding.py
echo; echo "################ N°5 LIQUIDATIONS AAVE V3 - Ethereum"
timeout 600 python3 etude/liquidations.py Ethereum
