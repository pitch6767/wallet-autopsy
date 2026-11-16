# 16.11.2026 : trades du banc d'essai (plafond 100 $) depuis le 11.11 pour les lignes principales, pour l'étude des heures (lecture seule)
import json, urllib.request, time, gzip, subprocess
print("lu à", time.strftime("%H:%M:%S"))
g = lambda u: json.loads(urllib.request.urlopen(urllib.request.Request(u, headers={"user-agent": "verif"}), timeout=280).read())
T = g("https://72-11-157-70.sslip.io/api/bot/banc/trades?depuis=2026-11-11T00:00:00Z&plafond=100")["trades"]
G = {600013, 600005, 2162, 101, 105, 6, 5600013, 5002162, 700001, 800005, 800007, 800008, 2165, 106, 206}
K = [t for t in T if t["num"] in G]
json.dump(K, gzip.open("etude/analyse/banc_heures_16.json.gz", "wt"))
subprocess.run(["git", "add", "etude/analyse/banc_heures_16.json.gz"])
print("trades", len(T), "gardés", len(K))
