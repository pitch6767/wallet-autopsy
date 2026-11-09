# 09.11.2026 22 h : 600005 / 600009 / 600010 depuis la remise à zéro (08.11 16 h) — lecture seule, plafond 200 $
import json, urllib.request, collections
with urllib.request.urlopen(urllib.request.Request("https://72-11-157-70.sslip.io/api/bot/banc/trades?depuis=2026-11-08T15:00:00Z&plafond=200", headers={"user-agent": "analyse"}), timeout=180) as r: T = json.load(r)["trades"]
for n in [600005, 600009, 600010, 2171, 2172]:
    X = [t for t in T if t["num"] == n]
    print(n, len(X), "trades", round(sum(t["pnl"] for t in X)), "$", "premier :", min((t["ouvert"] for t in X), default=None))
