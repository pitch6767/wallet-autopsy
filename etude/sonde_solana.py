# 13.11.2026 11 h : remise à zéro + 2162 active + règles F en service ? (lecture seule)
import json, urllib.request
def get(u):
    try:
        with urllib.request.urlopen(urllib.request.Request(u, headers={"user-agent": "analyse"}), timeout=120) as r: return json.loads(r.read())
    except Exception as e: return {"erreur": str(e)}
e = get("https://72-11-157-70.sslip.io/api/bot/banc/etat")
for k in ["version", "mode", "enMarche", "choisies", "actives", "activesDepuis", "dernierSignal", "regles"]: print(k, ":", json.dumps(e.get(k), ensure_ascii=False))
d = get("https://72-11-157-70.sslip.io/api/bot/banc/decisions?depuis=2026-11-13T09:00:00Z")
tp = d.get("tradesPaper") or []
print("onglet Trades depuis 10 h :", len(tp), "trades ; lignes", sorted({x.get("n") for x in tp}), "; avant 11 h :", sum(1 for x in tp if x.get("ouvert", "") < "2026-11-13T10:00"))
