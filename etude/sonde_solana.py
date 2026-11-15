# 15.11.2026 10 h (Pitch : « tout est détraqué ») — bilan depuis 8 h, lecture seule
import json, urllib.request, gzip, subprocess, os, time
print("lu à", time.strftime("%H:%M:%S"))
def get(u, t=280):
    for k in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers={"user-agent": "analyse"}), timeout=t) as r: return json.loads(r.read())
        except Exception as e: err = str(e); time.sleep(3)
    return {"erreur": err}
e = get("https://72-11-157-70.sslip.io/api/bot/banc/etat"); print("version", e.get("version")); print("actives", e.get("actives"), e.get("mode"), e.get("activesDepuis")); print("moteur", json.dumps(e.get("moteur"))[:200]); print("source", json.dumps(e.get("sourceSignaux"))[:250])
d = get("https://72-11-157-70.sslip.io/api/bot/banc/trades?depuis=2026-11-12T00:00:00Z&plafond=100")
print("banc", len(d.get("trades") or []))
os.makedirs("etude/analyse", exist_ok=True)
with gzip.open("etude/analyse/banc_15_10h.json.gz", "wt") as f: json.dump(d, f)
x = get("https://72-11-157-70.sslip.io/api/bot/banc/decisions?depuis=2026-11-15T00:00:00Z")
tp = [t for t in (x.get("tradesPaper") or []) if t.get("ouvert", "") >= "2026-11-15T07:00"]
print("onglet Trades depuis 8 h :", len(tp)); print(json.dumps(tp[:3], ensure_ascii=False)[:900])
subprocess.run(["git", "add", "etude/analyse"])
