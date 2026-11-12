# 12.11.2026 : après le redémarrage du moteur de signaux de Dublin — les signaux reviennent-ils ? (lecture seule)
import json, urllib.request
def get(u):
    try:
        with urllib.request.urlopen(urllib.request.Request(u, headers={"user-agent": "analyse"}), timeout=60) as r: return json.loads(r.read())
    except Exception as e: return {"erreur": str(e)}
e = get("https://72-11-157-70.sslip.io/api/bot/banc/etat")
print("version", e.get("version"), "| actives", e.get("actives"), "| mode", e.get("mode"))
print("dernierSignal", e.get("dernierSignal")); print("sourceSignaux", e.get("sourceSignaux"))
t = get("https://72-11-157-70.sslip.io/api/bot/banc/trades?depuis=2026-11-12T13:30:00Z")
from collections import Counter
L = t.get("trades") or []; print("trades réglés du banc depuis 14 h 30 :", len(L), Counter(x.get("num") or x.get("n") for x in L).most_common(15))
# 2e lecture 14:02
