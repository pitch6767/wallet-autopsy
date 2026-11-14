# 14.11.2026 midi (Pitch : « we are doing extremely poorly now ») — collecte lecture seule : banc 96 h, état des règles, décisions
import json, urllib.request, gzip, subprocess, os, time
def get(u, t=280):
    for k in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers={"user-agent": "analyse"}), timeout=t) as r: return json.loads(r.read())
        except Exception as e: err = str(e); time.sleep(3)
    return {"erreur": err}
os.makedirs("etude/analyse", exist_ok=True)
d = get("https://72-11-157-70.sslip.io/api/bot/banc/trades?depuis=2026-11-01T00:00:00Z&plafond=100")
print("banc : depuis", d.get("depuis"), "| trades", len(d.get("trades") or []), d.get("erreur", ""))
with gzip.open("etude/analyse/banc_14midi.json.gz", "wt") as f: json.dump(d, f)
e = get("https://72-11-157-70.sslip.io/api/bot/banc/etat")
print("version", e.get("version")); print("actives", e.get("actives"), e.get("activesDepuis"))
print("regles", json.dumps(e.get("regles"), ensure_ascii=False)[:1500])
with open("etude/analyse/etat_14midi.json", "w") as f: json.dump(e, f)
x = get("https://72-11-157-70.sslip.io/api/bot/banc/decisions?depuis=2026-11-13T00:00:00Z")
tp = [t for t in (x.get("tradesPaper") or []) if t.get("ouvert", "") >= "2026-11-13T10:00"]
print("Trades (onglet) depuis 13.11 11 h :", len(tp))
for t in tp: print("  ", json.dumps(t, ensure_ascii=False)[:220])
subprocess.run(["git", "add", "etude/analyse"])
