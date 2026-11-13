# 13.11.2026 : 2162 active + Trades remis à 11 h ? (lecture seule)
import json, urllib.request
def get(u):
    with urllib.request.urlopen(urllib.request.Request(u, headers={"user-agent": "analyse"}), timeout=120) as r: return json.loads(r.read())
e = get("https://72-11-157-70.sslip.io/api/bot/banc/etat")
for k in ["version", "actives", "activesDepuis", "choisies"]: print(k, ":", json.dumps(e.get(k), ensure_ascii=False))
g = e.get("regles", {}); print("règles :", {k: g.get(k) for k in ["vus", "doubles", "doublesF2", "sansEcart", "refuses"]})
for a in (g.get("acceptes") or [])[:5]: print("  accepté :", a)
tp = get("https://72-11-157-70.sslip.io/api/bot/banc/decisions?depuis=2026-11-01T00:00:00Z").get("tradesPaper") or []
print("onglet Trades :", len(tp), "trades ; lignes", sorted({x.get("n") for x in tp}), "; avant 11 h :", sum(1 for x in tp if x.get("ouvert", "") < "2026-11-13T10:00"))
