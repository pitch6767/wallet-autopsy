# 15.11.2026 : délai signal → achat sur les 20 dernières minutes (lecture seule)
import json, urllib.request, datetime, time
print("lu à", time.strftime("%H:%M:%S"))
g = lambda u: json.loads(urllib.request.urlopen(urllib.request.Request(u, headers={"user-agent": "analyse"}), timeout=200).read())
e = g("https://72-11-157-70.sslip.io/api/bot/banc/etat"); print("actives :", e.get("actives"), "mode :", e.get("mode"))
dep = (datetime.datetime.utcnow() - datetime.timedelta(minutes=25)).strftime("%Y-%m-%dT%H:%M:%SZ")
T = g(f"https://72-11-157-70.sslip.io/api/bot/banc/trades?depuis={dep}&plafond=100")["trades"]
d = []
for t in T:
    if t["num"] >= 1000: continue
    try: d.append((datetime.datetime.fromisoformat(t["ouvert"].replace("Z", "+00:00")) - datetime.datetime.fromisoformat(t["id"].split("|")[-1].replace("Z", "+00:00"))).total_seconds())
    except Exception: pass
d.sort(); print("délai 25 dernières min :", len(d), "trades ; médiane", round(d[len(d)//2], 3) if d else None, "; 90 %", round(d[int(len(d)*.9)], 3) if d else None)
# v1
# v2
# v3
# v4
# v5
# v6
# v7
# v8
# v9
# v10
# v11
# v12
