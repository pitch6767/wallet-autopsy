# 12.11.2026 13 h 50 : la 600005 est-elle de nouveau recopiée dans l'onglet Trades ? (trades PAPER publiés par /bot/banc/decisions) — lecture seule
import json, urllib.request, collections
def get(u):
    with urllib.request.urlopen(urllib.request.Request(u, headers={"user-agent": "analyse"}), timeout=180) as r: return json.load(r)
dep = "2026-11-09T23:49:26Z"
P = get(f"https://72-11-157-70.sslip.io/api/bot/banc/decisions?depuis={dep}").get("tradesPaper", [])
B = [t for t in get(f"https://72-11-157-70.sslip.io/api/bot/banc/trades?depuis={dep}&plafond=100")["trades"] if t["num"] == 600005]
print("onglet Trades par n° :", dict(collections.Counter(t["n"] for t in P)))
P5 = [t for t in P if t["n"] == 600005 and t["statut"] == "settled"]
print("600005 onglet Trades :", len(P5), "réglés, gain", round(sum(t["gain"] or 0 for t in P5), 2), "| dernier :", max((t["ouvert"] for t in P5), default=None))
print("600005 banc          :", len(B), "réglés, gain", round(sum(t["pnl"] for t in B), 2), "| dernier :", max((t["ouvert"] for t in B), default=None))
