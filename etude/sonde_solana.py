# 12.11.2026 12 h 45 : 600013 dans la réponse de /api/bot/banc (ce que lit l'onglet) ? — lecture seule
import urllib.request, json
try:
    with urllib.request.urlopen(urllib.request.Request("https://72-11-157-70.sslip.io/api/bot/banc", headers={"user-agent": "analyse"}), timeout=180) as r: d = json.load(r)
    S = d.get("strategies", []); print("lignes :", len(S), "| depuis :", d.get("depuis"))
    for x in S:
        if x["num"] in (600005, 600013): print(x["num"], x.get("nom"), x["trades"], round(x["gain"]))
    print("600013 présente :", any(x["num"] == 600013 for x in S))
except Exception as e: print(repr(e))
