# 15.11.2026 : vérification version I + stratégie active 600005 + délai d'achat (lecture seule)
import json, urllib.request
g = lambda u: json.loads(urllib.request.urlopen(urllib.request.Request(u, headers={"user-agent": "analyse"}), timeout=200).read())
e = g("https://72-11-157-70.sslip.io/api/bot/banc/etat"); print("version :", e.get("version")); print("actives :", e.get("actives"), "mode :", e.get("mode"), "depuis :", e.get("activesDepuis"))
p = g("https://72-11-157-70.sslip.io/api/bot/paires"); print("paires :", p.get("numeros"))
T = g("https://72-11-157-70.sslip.io/api/bot/banc/trades?depuis=2026-11-15T06:00:00Z&plafond=100")["trades"]
import datetime
d = []
for t in T:
    if t["num"] >= 1000: continue
    try: ts = datetime.datetime.fromisoformat(t["id"].split("|")[-1].replace("Z", "+00:00")); d.append((datetime.datetime.fromisoformat(t["ouvert"].replace("Z", "+00:00")) - ts).total_seconds())
    except Exception: pass
d.sort(); print("délai signal → achat (lignes de base, depuis 07 h) :", len(d), "trades ; médiane", d[len(d)//2] if d else None)
# 1
# 2
# r1
