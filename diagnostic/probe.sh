U=https://wallet-autopsy.pitch67.workers.dev
echo "=== page"; curl -sS -m 20 $U/ | grep -c "Tueurs à copier"
echo "=== etat"; curl -sS -m 30 $U/api/btc/etat
echo; echo "=== classement"; curl -sS -m 60 "$U/api/btc/classement" | python3 -c "
import json,sys; d=json.load(sys.stdin)
print('erreur' in d and d, 'total',d.get('total'),'tueurs',len(d.get('tueurs',[])), 'px_dir' in (d.get('perf') or [{}])[0])"
