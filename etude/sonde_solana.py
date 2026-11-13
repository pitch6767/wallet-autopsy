# 13.11.2026 : vérification de la mise en ligne (version, stratégie active) — lecture seule
import json, urllib.request
e = json.loads(urllib.request.urlopen(urllib.request.Request("https://72-11-157-70.sslip.io/api/bot/banc/etat", headers={"user-agent": "analyse"}), timeout=60).read())
for k in ["version", "actives", "activesDepuis", "mode"]: print(k, ":", json.dumps(e.get(k), ensure_ascii=False))
