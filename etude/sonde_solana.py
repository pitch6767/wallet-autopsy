# 13.11.2026 : remise à zéro + 2162 active ? + règles (lecture seule)
import json, urllib.request
with urllib.request.urlopen(urllib.request.Request("https://72-11-157-70.sslip.io/api/bot/banc/etat", headers={"user-agent": "analyse"}), timeout=60) as r: e = json.loads(r.read())
for k in ["version", "actives", "activesDepuis", "choisies"]: print(k, ":", json.dumps(e.get(k), ensure_ascii=False))
g = e.get("regles", {}); print("règles :", {k: g.get(k) for k in ["depuis", "vus", "doubles", "doublesF2", "sansEcart", "sansMesureF", "refuses"]}); print("derniers :", (g.get("derniers") or [])[:3])
with urllib.request.urlopen(urllib.request.Request("https://72-11-157-70.sslip.io/api/bot/banc/decisions?depuis=2026-11-13T09:00:00Z", headers={"user-agent": "analyse"}), timeout=120) as r: d = json.loads(r.read())
tp = d.get("tradesPaper") or []
print("onglet Trades depuis 10 h UTC :", len(tp), "trades ; lignes", sorted({x.get("n") for x in tp}))
