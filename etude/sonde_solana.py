# 16.11.2026 : TOUS les trades du banc sur petits tickets (signal ≤ 0,15), toutes les lignes, depuis 96 h (lecture seule)
import json, urllib.request, time, gzip, subprocess
print("lu à", time.strftime("%H:%M:%S"), time.time())
g = lambda u: json.loads(urllib.request.urlopen(urllib.request.Request(u, headers={"user-agent": "verif"}), timeout=280).read())
T = g("https://72-11-157-70.sslip.io/api/bot/banc/trades?depuis=2026-11-12T00:00:00Z&plafond=100")["trades"]
K = [t for t in T if t["prixSignal"] <= 0.15]
json.dump(K, gzip.open("etude/analyse/banc_petits_16.json.gz", "wt")); subprocess.run(["git", "add", "etude/analyse/banc_petits_16.json.gz"])
print("trades", len(T), "petits", len(K), "lignes", len({t["num"] for t in K}))
