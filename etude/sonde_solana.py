# 13.11.2026 : remise à zéro + 2162 active ? (lecture seule)
import json, urllib.request
with urllib.request.urlopen(urllib.request.Request("https://72-11-157-70.sslip.io/api/bot/banc/etat", headers={"user-agent": "analyse"}), timeout=60) as r: e = json.loads(r.read())
for k in ["version", "actives", "activesDepuis", "choisies"]: print(k, ":", json.dumps(e.get(k), ensure_ascii=False))
print("règles :", {k: e.get("regles", {}).get(k) for k in ["vus", "doubles", "doublesF2", "sansEcart", "refuses"]})
