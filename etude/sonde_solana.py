# 15.11.2026 : contrôle 25 $ par côté + délai d'achat (lecture seule)
import json, urllib.request, datetime, time
print("lu à", time.strftime("%H:%M:%S"))
g = lambda u: json.loads(urllib.request.urlopen(urllib.request.Request(u, headers={"user-agent": "analyse"}), timeout=200).read())
e = g("https://72-11-157-70.sslip.io/api/bot/banc/etat"); print("version :", e.get("version")); print("actives :", e.get("actives"), "mode :", e.get("mode"))
try: print("binance-funding :", urllib.request.urlopen(urllib.request.Request("https://72-11-157-70.sslip.io/api/public/binance-funding", headers={"user-agent": "analyse"}), timeout=60).status)
except Exception as x: print("binance-funding :", x)
T = g("https://72-11-157-70.sslip.io/api/bot/banc/trades?depuis=2026-11-15T07:40:00Z&plafond=100")["trades"]
d = []
for t in T:
    if t["num"] >= 1000: continue
    try: d.append((datetime.datetime.fromisoformat(t["ouvert"].replace("Z", "+00:00")) - datetime.datetime.fromisoformat(t["id"].split("|")[-1].replace("Z", "+00:00"))).total_seconds())
    except Exception: pass
d.sort(); print("délai signal → achat depuis 08 h 40 :", len(d), "trades ; médiane", d[len(d)//2] if d else None, "; 90 %", d[int(len(d)*.9)] if d else None)
p = g("https://72-11-157-70.sslip.io/api/bot/paires")
for k in ["v1", "v2", "v3", "v4", "v5", "v6"]:
    v = p.get(k) or {}; print(k, v.get("numero"), (v.get("parametres") or {}).get("budgetCote"), {z: v.get(z) for z in ["cycles", "gain", "mise", "cyclesPositifs"]})
# u1
