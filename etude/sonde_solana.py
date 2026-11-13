# 13.11.2026 (Pitch : analyse des performances de chaque stratégie du banc d'essai réel) — collecte en lecture seule
import json, urllib.request, gzip, os, subprocess, time
def get(u, t=120):
    for k in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers={"user-agent": "analyse"}), timeout=t) as r: return json.loads(r.read())
        except Exception as e: err = str(e); time.sleep(3)
    return {"erreur": err}
os.makedirs("etude/analyse", exist_ok=True)
d = get("https://72-11-157-70.sslip.io/api/bot/banc/trades?depuis=2026-11-01T00:00:00Z&plafond=100", 300)
print("banc : depuis", d.get("depuis"), "| trades", len(d.get("trades") or []), d.get("erreur", ""))
with gzip.open("etude/analyse/banc.json.gz", "wt") as f: json.dump(d, f)
r = get("https://72-11-157-70.sslip.io/api/bot/banc/resume?depuis=2026-11-08T15:00:00Z", 300)
with gzip.open("etude/analyse/resume.json.gz", "wt") as f: json.dump(r, f)
print("résumé :", str(r)[:300])
K = []; t = int(time.mktime(time.strptime("2026-11-09 04:00", "%Y-%m-%d %H:%M"))) * 1000; fin = int(time.time() * 1000)
while t < fin:
    k = get(f"https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=1m&startTime={t}&limit=1000")
    if not isinstance(k, list) or not k: print("binance", k); break
    K += [[x[0], float(x[1]), float(x[2]), float(x[3]), float(x[4]), float(x[5])] for x in k]; t = k[-1][0] + 60000
print("bougies 1 min :", len(K))
with gzip.open("etude/analyse/bougies.json.gz", "wt") as f: json.dump(K, f)
subprocess.run(["git", "add", "etude/analyse"])
