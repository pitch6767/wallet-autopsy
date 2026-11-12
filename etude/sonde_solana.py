# 12.11.2026 : après le 2e redémarrage du moteur (correction) — les signaux arrivent-ils ? (lecture seule)
import json, urllib.request
def get(u):
    try:
        with urllib.request.urlopen(urllib.request.Request(u, headers={"user-agent": "analyse"}), timeout=60) as r: return json.loads(r.read())
    except Exception as e: return {"erreur": str(e)}
e = get("https://72-11-157-70.sslip.io/api/bot/banc/etat")
print("version", e.get("version"), "| actives", e.get("actives"), "| mode", e.get("mode"))
print("dernierSignal", e.get("dernierSignal")); print("sourceSignaux", e.get("sourceSignaux"))
t = get("https://72-11-157-70.sslip.io/api/bot/banc/trades?depuis=2026-11-12T13:55:00Z"); L = t.get("trades") or []
from collections import Counter
print("trades réglés du banc depuis 14 h 55 :", len(L), Counter(x["num"] for x in L if x["num"] < 2000).most_common(12))
print("600005 :", [(x["ouvert"][11:19], x["side"], x["prix"], x["mise"], x["pnl"]) for x in L if x["num"] == 600005])
