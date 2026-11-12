# 12.11.2026 : vérification de la mise en ligne des garde-fous — état en lecture seule (/api/bot/banc/etat) — lecture seule
import json, urllib.request
try:
    with urllib.request.urlopen(urllib.request.Request("https://72-11-157-70.sslip.io/api/bot/banc/etat", headers={"user-agent": "analyse"}), timeout=60) as r: print(json.dumps(json.load(r), ensure_ascii=False, indent=1))
except Exception as e: print("état", repr(e))
