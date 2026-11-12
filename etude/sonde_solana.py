# 12.11.2026 12 h 36 : la ligne 600013 existe-t-elle sur le banc ? — lecture seule
import json, urllib.request
with urllib.request.urlopen(urllib.request.Request("https://72-11-157-70.sslip.io/api/bot/banc/trades?depuis=2026-11-08T15:00:00Z&plafond=100", headers={"user-agent": "analyse"}), timeout=180) as r: T = json.load(r)["trades"]
for n in (600005, 600013):
    X = [t for t in T if t["num"] == n]; print(n, len(X), "trades", round(sum(t["pnl"] for t in X)), "$")
