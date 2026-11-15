# 15.11.2026 soir : analyse de la ligne 800005 (lecture seule)
import json, urllib.request, gzip, subprocess, os, time
print("lu à", time.strftime("%H:%M:%S"))
g = lambda u: json.loads(urllib.request.urlopen(urllib.request.Request(u, headers={"user-agent": "analyse"}), timeout=250).read())
T = g("https://72-11-157-70.sslip.io/api/bot/banc/trades?depuis=2026-11-15T07:00:00Z&plafond=100")["trades"]
P = g("https://72-11-157-70.sslip.io/api/bot/paires")
os.makedirs("etude/analyse", exist_ok=True)
with gzip.open("etude/analyse/paires_15soir.json.gz", "wt") as f: json.dump({"banc": [t for t in T if 800000 <= t["num"] < 900000 or t["num"] in (600013, 5600013)], "paires": P}, f)
for k in ["v1", "v2", "v3", "v4", "v5", "v6"]:
    v = P.get(k) or {}; print(k, v.get("numero"), {z: v.get(z) for z in ["cycles", "gain", "mise", "rendementPct", "cyclesPositifs", "creux", "sommeMedianePaire", "cyclesEquilibres", "cyclesDesequilibres"]})
subprocess.run(["git", "add", "etude/analyse"])
