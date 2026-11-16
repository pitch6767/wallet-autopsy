# 16.11.2026 : journal des décisions des portefeuilles (2162 = 101 + 105) sur 7 jours — pris / refusé + raison (lecture seule)
import json, urllib.request, time, gzip, subprocess, collections
print("lu à", time.strftime("%H:%M:%S"))
g = lambda u: json.loads(urllib.request.urlopen(urllib.request.Request(u, headers={"user-agent": "verif"}), timeout=280).read())
D = g("https://72-11-157-70.sslip.io/api/bot/banc/decisions?depuis=2026-11-09T00:00:00Z")
json.dump(D, gzip.open("etude/analyse/decisions_16.json.gz", "wt")); subprocess.run(["git", "add", "etude/analyse/decisions_16.json.gz"])
dec = D.get("decisions", []); print("décisions", len(dec), "exemple", json.dumps(dec[:2])[:600] if dec else "")
print("tradesPaper", len(D.get("tradesPaper", [])))
