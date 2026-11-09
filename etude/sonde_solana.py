# 10.11.2026 00 h 42 (Pitch : « aucun trade, je ne crois pas ça ») : la ligne 600005 du banc depuis 20 h 45 (Paris) — lecture seule
import json, urllib.request
with urllib.request.urlopen(urllib.request.Request("https://72-11-157-70.sslip.io/api/bot/banc/trades?depuis=2026-11-09T19:45:00Z&plafond=200", headers={"user-agent": "analyse"}), timeout=180) as r: T = json.load(r)["trades"]
print("dernier trade réglé du banc :", max((t["ouvert"] for t in T), default=None))
for n in [600005, 600009, 2171, 2172, 101, 105]:
    X = sorted([t for t in T if t["num"] == n], key=lambda t: t["ouvert"])
    print(n, len(X), "trades", round(sum(t["pnl"] for t in X)), "$ :", [(t["ouvert"][11:19], t["side"], round(t["prix"], 2), round(t["pnl"])) for t in X][:12])
