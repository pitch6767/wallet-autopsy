# 13.11.2026 : banc sans plafond par cycle (pour tester d'autres plafonds) — lecture seule
import json, urllib.request, gzip, subprocess
with urllib.request.urlopen(urllib.request.Request("https://72-11-157-70.sslip.io/api/bot/banc/trades?depuis=2026-11-01T00:00:00Z", headers={"user-agent": "analyse"}), timeout=300) as r: d = json.loads(r.read())
T = [t for t in d["trades"] if t["num"] in (2162, 2172, 600005, 600006, 2171, 105, 101)]
print("sans plafond :", len(T), "trades des lignes principales depuis", d["depuis"])
with gzip.open("etude/analyse/banc_sans_plafond.json.gz", "wt") as f: json.dump(T, f)
subprocess.run(["git", "add", "etude/analyse/banc_sans_plafond.json.gz"])
