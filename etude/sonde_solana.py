# 15.11.2026 soir : vérifie que 800007 / 800008 tournent après le déploiement (lecture seule)
import json, urllib.request, time
print("lu à", time.strftime("%H:%M:%S"))
g = lambda u: json.loads(urllib.request.urlopen(urllib.request.Request(u, headers={"user-agent": "verif"}), timeout=120).read())
P = g("https://72-11-157-70.sslip.io/api/bot/paires")
for k in ["v5", "v7", "v8"]:
    v = P.get(k) or {}; print(k, v.get("numero"), "cycles", v.get("cycles"), "gain", v.get("gain"), "enCours", json.dumps(v.get("enCours"))[:200], "param orph", (v.get("parametres") or {}).get("orphDelaiMs"), (v.get("parametres") or {}).get("orphMode"))
try: print("version", g("https://72-11-157-70.sslip.io/api/healthz"))
except Exception as e: print("healthz", e)
