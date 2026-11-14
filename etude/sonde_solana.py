# 14.11.2026 soir (Pitch : « résultats probables des stratégies avant les changements d'hier ») — collecte lecture seule
import json, urllib.request, gzip, subprocess, os, time
def get(u, t=280):
    for k in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers={"user-agent": "analyse"}), timeout=t) as r: return json.loads(r.read())
        except Exception as e: err = str(e); time.sleep(3)
    return {"erreur": err}
os.makedirs("etude/analyse", exist_ok=True)
d = get("https://72-11-157-70.sslip.io/api/bot/banc/trades?depuis=2026-11-12T00:00:00Z&plafond=100")
print("banc", d.get("depuis"), len(d.get("trades") or []), d.get("erreur", ""))
with gzip.open("etude/analyse/banc_14soir.json.gz", "wt") as f: json.dump(d, f)
K = []; t = int(time.mktime(time.strptime("2026-11-12 00:00", "%Y-%m-%d %H:%M"))) * 1000; fin = int(time.time() * 1000)
while t < fin:
    k = get(f"https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=1m&startTime={t}&limit=1000")
    if not isinstance(k, list) or not k: break
    K += [[x[0], float(x[1]), float(x[4])] for x in k]; t = k[-1][0] + 60000
print("bougies", len(K))
with gzip.open("etude/analyse/bougies_14soir.json.gz", "wt") as f: json.dump(K, f)
subprocess.run(["git", "add", "etude/analyse"])
