# 08.11.2026 : quelles lignes du banc ont des trades réglés depuis 16 h (Paris) ? lecture seule de la route publique /api/bot/banc/trades
import json, urllib.request, collections
def get(u):
    with urllib.request.urlopen(urllib.request.Request(u, headers={"user-agent": "analyse"}), timeout=120) as r: return r.status, json.load(r)
for u in ["https://72-11-157-70.sslip.io/api/bot/banc/trades?depuis=2026-11-08T15:00:00Z", "https://72-11-157-70.sslip.io/api/bot/banc"]:
    try:
        s, d = get(u); print(u, "HTTP", s)
        if "trades" in d:
            T = d["trades"]; c = collections.Counter(t["num"] for t in T)
            print("trades réglés depuis 16 h :", len(T), "; lignes :", len(c))
            print("séries ≥ 400000 :", sorted((n, k) for n, k in c.items() if 400000 <= n < 1000000))
            print("bases :", {n: c.get(n, 0) for n in [1114, 2125, 2171, 2172, 12112, 313, 2112, 7, 5]})
            print("3 idées (≥ 1 000 000) :", sum(1 for n in c if n >= 1000000), "lignes")
            print("dernier trade :", max((t["ouvert"] for t in T), default=None))
        else: print(str(d)[:300])
    except Exception as e: print(u, repr(e))
