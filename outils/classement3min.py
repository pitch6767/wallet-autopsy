# 06.11.2026 (Pitch : « Go pour tout ») : classement des stratégies du banc d'essai réel (VRAIS remplissages, +5 c, 200 $ par cycle
# frais compris) si on ne garde QUE les achats des 3 premières minutes du cycle. Comparé au gain sans ce filtre.
import json, sys, urllib.request, collections, datetime as dt
VPS = sys.argv[1]; DEP = "2026-11-04T14:38:10Z"
with urllib.request.urlopen(urllib.request.Request(f"{VPS}/api/bot/banc/trades?depuis={DEP}&plafond=200", headers={"cache-control": "no-store"}), timeout=180) as r: T = json.load(r)["trades"]
S = collections.defaultdict(lambda: {"tout": 0.0, "n": 0, "g": 0, "w": 0, "avant": 0.0, "auj": 0.0, "jours": collections.defaultdict(float), "mise": 0.0})
for t in T:
    s = S[t["num"]]; s["tout"] += t["pnl"]
    debut = (dt.datetime.fromisoformat(t["ouvert"].replace("Z", "+00:00")).timestamp() - (t["endTs"] / 1000 - 300)) < 180
    if not debut: continue
    j = (dt.datetime.fromtimestamp(t["endTs"] / 1000, dt.timezone.utc) + dt.timedelta(hours=1)).strftime("%m-%d")
    s["n"] += 1; s["g"] += t["pnl"]; s["w"] += t["gagne"]; s["jours"][j] += t["pnl"]; s["mise"] = max(s["mise"], t["mise"])
    s["avant" if j < "11-06" else "auj"] += t["pnl"]
L = sorted(((k, v) for k, v in S.items() if v["n"] >= 15), key=lambda x: -x[1]["g"])
print(f"trades {len(T)} ; stratégies avec au moins 15 trades dans les 3 premières minutes : {len(L)}")
print("rang | n° | trades 3 min | gagnés | gain 3 min | avant 06.11 | 06.11 | jours négatifs | gain SANS filtre")
for i, (k, v) in enumerate(L[:30], 1):
    neg = sum(1 for x in v["jours"].values() if x < 0)
    print(f"{i:2d} | {k} | {v['n']} | {round(100 * v['w'] / v['n'])} % | {v['g']:+.0f} $ | {v['avant']:+.0f} $ | {v['auj']:+.0f} $ | {neg}/{len(v['jours'])} | {v['tout']:+.0f} $")
pos = sum(1 for k, v in L if v["avant"] > 0 and v["auj"] > 0)
print(f"positives avant ET le 06.11 : {pos} sur {len(L)}")
print("FIN")
