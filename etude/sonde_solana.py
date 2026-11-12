# 12.11.2026 : rejeu de la panne inséré ? Trades = banc pour la 600005 ? (lecture seule ; boucle 8 min au plus)
import json, urllib.request, time
def get(u):
    try:
        with urllib.request.urlopen(urllib.request.Request(u, headers={"user-agent": "analyse"}), timeout=60) as r: return json.loads(r.read())
    except Exception as e: return {"erreur": str(e)}
B = "https://72-11-157-70.sslip.io/api/bot"
for k in range(16):
    e = get(B + "/banc/etat")
    if (e.get("rejeu") or {}).get("fini"): break
    time.sleep(30)
for k in ["version", "actives", "dernierSignal", "moteur", "rejeu"]: print(k, ":", json.dumps(e.get(k), ensure_ascii=False))
t = get(B + "/banc/trades?depuis=2026-11-12T03:50:00Z").get("trades") or []
rj = [x for x in t if x.get("rejoue")]
print("banc : trades rejoués réglés", len(rj), "| dont 600005 :", len([x for x in t if x["num"] == 600005 and x.get("rejoue")]))
d = get(B + "/banc/decisions?depuis=2026-11-12T03:50:00Z")
tp = [x for x in (d.get("tradesPaper") or []) if x.get("n") == 600005]
print("onglet Trades 600005 depuis 04 h 50 :", len(tp), "réglés", sum(1 for x in tp if x.get("statut") == "settled"), "gain", round(sum(x.get("gain") or 0 for x in tp), 2))
L = [x for x in t if x["num"] == 600005]
print("banc 600005 (sans plafond) depuis 04 h 50 :", len(L), "gain", round(sum(x["pnl"] for x in L), 2))
