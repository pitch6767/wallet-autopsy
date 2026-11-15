# 15.11.2026 soir : vérifie le plafond de 200 $ par cycle sur toutes les lignes (lecture seule)
import json, urllib.request, time, collections
print("lu à", time.strftime("%H:%M:%S"))
g = lambda u: json.loads(urllib.request.urlopen(urllib.request.Request(u, headers={"user-agent": "verif"}), timeout=250).read())
T = g("https://72-11-157-70.sslip.io/api/bot/banc/trades?depuis=2026-11-13T00:00:00Z&plafond=100")["trades"]
C = collections.defaultdict(float)
for t in T: C[(t["num"], t["endTs"])] += t["mise"]
M = collections.defaultdict(float)
for (n, e), v in C.items(): M[n] = max(M[n], v)
print("trades", len(T), "mise max par cycle, toutes lignes :", round(max(M.values()), 2))
print({n: round(M[n], 2) for n in (700001, 700007, 600013, 2162) if n in M})
P = g("https://72-11-157-70.sslip.io/api/bot/paires"); print("v7", (P.get("v7") or {}).get("cycles"), "v8", (P.get("v8") or {}).get("cycles"))
