# 14.11.2026 : vérification du teneur de paires simulé (lecture seule)
import json, urllib.request
g = lambda u: json.loads(urllib.request.urlopen(urllib.request.Request(u, headers={"user-agent": "analyse"}), timeout=60).read())
e = g("https://72-11-157-70.sslip.io/api/bot/banc/etat"); print("version :", e.get("version")); print("actives :", e.get("actives"), "mode :", e.get("mode"))
try: p = g("https://72-11-157-70.sslip.io/api/bot/paires"); print(json.dumps({k: p.get(k) for k in ["cycles", "gain", "mise", "rendementPct", "cyclesPositifs", "creux", "sommeMedianePaire", "enCours", "enAttente", "derniers"]}, ensure_ascii=False)[:3000])
except Exception as x: print("paires :", x)
