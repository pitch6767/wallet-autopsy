# 13.11.2026 : vérification — règles du 13.11 en service, bot passé sur la 2162 (lecture seule)
import json, urllib.request
def get(u):
    try:
        with urllib.request.urlopen(urllib.request.Request(u, headers={"user-agent": "analyse"}), timeout=120) as r: return json.loads(r.read())
    except Exception as e: return {"erreur": str(e)}
e = get("https://72-11-157-70.sslip.io/api/bot/banc/etat")
for k in ["version", "mode", "enMarche", "choisies", "actives", "activesDepuis", "dernierSignal", "regles"]: print(k, ":", json.dumps(e.get(k), ensure_ascii=False))
print("moteur ok :", (e.get("moteur") or {}).get("ok"), "| source :", (e.get("sourceSignaux") or {}).get("connecte"))
