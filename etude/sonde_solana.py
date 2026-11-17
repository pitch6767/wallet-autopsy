# Lecture seule — trades réglés du banc d'essai réel (96 h, plafond 100) — temporaire, 19:50 UTC
import json, urllib.request, time, gzip, base64
print("lu à", time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()))
dep = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() - 96*3600 + 120))
try:
    raw = urllib.request.urlopen(urllib.request.Request("https://72-11-157-70.sslip.io/api/bot/banc/trades?plafond=100&depuis=" + dep, headers={"user-agent": "verif"}), timeout=400).read()
    d = json.loads(raw); print("N", len(d.get("trades", [])), d.get("depuis"), d.get("prix"), d.get("plafond"))
    print("B64GZ", base64.b64encode(gzip.compress(raw, 9)).decode())
except Exception as e: print("ERREUR", e)
