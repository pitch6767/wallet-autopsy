U=https://wallet-autopsy.pitch67.workers.dev
echo "=== etat"; curl -sS -m 30 $U/api/btc/etat
echo; echo "=== classement tous (meilleur coup)"; curl -sS -m 60 "$U/api/btc/classement?tri=best_roi" | python3 -c "
import json,sys
d=json.load(sys.stdin)
if 'erreur' in d: print(d); sys.exit()
print('total',d['total'])
for w in d['table'][:8]: print(w['wallet'][:10], (w['nom'] or '')[:18], 'n',w['n_marches'], 'pnl',round(w['pnl'],1), 'best x',round(1+w['best_roi'],1))
print('copier:',[ (w['nom'] or w['wallet'][:8], round(w['regularite'],1)) for w in d['copier'][:5]])"
