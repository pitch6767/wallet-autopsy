# 12.11.2026 : vérification garde-fous 3 (santé du moteur) — lecture seule
import json, urllib.request
def get(u):
    try:
        with urllib.request.urlopen(urllib.request.Request(u, headers={"user-agent": "analyse"}), timeout=60) as r: return json.loads(r.read())
    except Exception as e: return {"erreur": str(e)}
e = get("https://72-11-157-70.sslip.io/api/bot/banc/etat")
for k in ["version", "mode", "enMarche", "actives", "activesDepuis", "dernierSignal", "sourceSignaux", "moteur"]: print(k, ":", json.dumps(e.get(k), ensure_ascii=False))
