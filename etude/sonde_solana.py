# 15.11.2026 matin (Pitch : « check all the result, terrible again ») — lecture seule
import json, urllib.request, gzip, subprocess, os, time, collections
def get(u, t=280):
    for k in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers={"user-agent": "analyse"}), timeout=t) as r: return json.loads(r.read())
        except Exception as e: err = str(e); time.sleep(3)
    return {"erreur": err}
e = get("https://72-11-157-70.sslip.io/api/bot/banc/etat"); print("version", e.get("version")); print("actives", e.get("actives"), e.get("mode")); print("moteur", json.dumps(e.get("moteur"), ensure_ascii=False)[:300]); print("source", json.dumps(e.get("sourceSignaux"), ensure_ascii=False)[:300])
d = get("https://72-11-157-70.sslip.io/api/bot/banc/trades?depuis=2026-11-12T00:00:00Z&plafond=100")
print("banc", len(d.get("trades") or []))
os.makedirs("etude/analyse", exist_ok=True)
with gzip.open("etude/analyse/banc_15matin.json.gz", "wt") as f: json.dump(d, f)
x = get("https://72-11-157-70.sslip.io/api/bot/banc/decisions?depuis=2026-11-14T00:00:00Z")
tp = [t for t in (x.get("tradesPaper") or []) if t.get("ouvert", "") >= "2026-11-14T15:00"]
print("onglet Trades depuis 16 h :", len(tp), "gain", round(sum((t.get("pnl") or 0) for t in tp), 2))
for t in tp: print("  ", t.get("ouvert", "")[:19], t.get("side") or t.get("cote"), t.get("prix"), t.get("mise"), t.get("pnl"), t.get("statut"))
p = get("https://72-11-157-70.sslip.io/api/bot/paires")
for k in ["v1", "v2", "v3", "v4"]:
    v = p.get(k) or {}; print(k, v.get("numero"), json.dumps({z: v.get(z) for z in ["cycles", "gain", "mise", "rendementPct", "cyclesPositifs", "creux", "sommeMedianePaire", "cyclesEquilibres", "cyclesDesequilibres", "parJour"]}, ensure_ascii=False))
K = []; t = int(time.mktime(time.strptime("2026-11-12 00:00", "%Y-%m-%d %H:%M"))) * 1000; fin = int(time.time() * 1000)
while t < fin:
    k = get(f"https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=1m&startTime={t}&limit=1000")
    if not isinstance(k, list) or not k: break
    K += [[x[0], float(x[1]), float(x[4])] for x in k]; t = k[-1][0] + 60000
with gzip.open("etude/analyse/bougies_15matin.json.gz", "wt") as f: json.dump(K, f)
subprocess.run(["git", "add", "etude/analyse"])
