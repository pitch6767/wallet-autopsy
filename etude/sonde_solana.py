# 15.11.2026 : contrôle après déploiement I (lecture seule)
import json, urllib.request, datetime, time
print("lu à", time.strftime("%H:%M:%S"))
g = lambda u: json.loads(urllib.request.urlopen(urllib.request.Request(u, headers={"user-agent": "analyse"}), timeout=200).read())
try: f = urllib.request.urlopen(urllib.request.Request("https://72-11-157-70.sslip.io/api/public/binance-funding", headers={"user-agent": "analyse"}), timeout=60); print("binance-funding :", f.status)
except Exception as e: print("binance-funding :", e)
T = g("https://72-11-157-70.sslip.io/api/bot/banc/trades?depuis=2026-11-15T07:40:00Z&plafond=100")["trades"]
d = []
for t in T:
    if t["num"] >= 1000: continue
    try: d.append((datetime.datetime.fromisoformat(t["ouvert"].replace("Z", "+00:00")) - datetime.datetime.fromisoformat(t["id"].split("|")[-1].replace("Z", "+00:00"))).total_seconds())
    except Exception: pass
d.sort(); print("délai signal → achat depuis 08 h 40 :", len(d), "trades ; médiane", d[len(d)//2] if d else None)
print("600013 :", sum(1 for t in T if t["num"] == 600013), "trades ; 5600013 :", sum(1 for t in T if t["num"] == 5600013))
