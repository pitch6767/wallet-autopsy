# 12.11.2026 (lecture immédiate) : rejeu (3e passage) + contrôle Trades = banc pour la 600005 pendant la panne (lecture seule ; boucle 9 min au plus)
import json, urllib.request, time
def get(u):
    try:
        with urllib.request.urlopen(urllib.request.Request(u, headers={"user-agent": "analyse"}), timeout=60) as r: return json.loads(r.read())
    except Exception as e: return {"erreur": str(e)}
B = "https://72-11-157-70.sslip.io/api/bot"
for k in range(1):
    e = get(B + "/banc/etat"); r = e.get("rejeu") or {}
    if "(3)" in str(e.get("version")) and r.get("fini") and r.get("lance", "") > "2026-11-12T15:05": break
    time.sleep(30)
for k in ["version", "actives", "dernierSignal", "moteur", "rejeu"]: print(k, ":", json.dumps(e.get(k), ensure_ascii=False))
D, F = "2026-11-12T03:53:00Z", "2026-11-12T14:02:30"
t = get(B + "/banc/trades?plafond=100&depuis=" + D).get("trades") or []
b = sorted([(x["ouvert"][:19], x["side"], round(x["mise"], 2), round(x["pnl"], 2)) for x in t if x["num"] == 600005 and x["ouvert"] < F])
d = get(B + "/banc/decisions?depuis=" + D)
p = sorted([(x["ouvert"][:19], x["cote"], round(x["mise"], 2), round(x.get("gain") or 0, 2)) for x in (d.get("tradesPaper") or []) if x.get("n") == 600005 and x["ouvert"] < F])
print("banc 600005 (100 $/cycle) pendant la panne :", len(b), "trades, gain", round(sum(x[3] for x in b), 2))
print("onglet Trades 600005 pendant la panne     :", len(p), "trades, gain", round(sum(x[3] for x in p), 2))
print("identiques :", b == p)
if b != p: print("banc seul :", [x for x in b if x not in p][:10]); print("Trades seul :", [x for x in p if x not in b][:10])
for x in b: print("  ", x)
time.sleep(1)   # le miroir refait les trades réglés à l'envers (toutes les 10 s) — relecture
d = get(B + "/banc/decisions?depuis=" + D); t = get(B + "/banc/trades?plafond=100&depuis=" + D).get("trades") or []
b = sorted([(x["ouvert"][:19], x["side"], round(x["mise"], 2), round(x["pnl"], 2)) for x in t if x["num"] == 600005 and x["ouvert"] < F])
p = sorted([(x["ouvert"][:19], x["cote"], round(x["mise"], 2), round(x.get("gain") or 0, 2)) for x in (d.get("tradesPaper") or []) if x.get("n") == 600005 and x["ouvert"] < F])
print("RELECTURE 1 min après — banc", len(b), round(sum(x[3] for x in b), 2), "| Trades", len(p), round(sum(x[3] for x in p), 2), "| identiques :", b == p)
