# 16.11.2026 : signaux reçus et « non remplis » par jour pour les lignes principales (différence entre deux « depuis ») — lecture seule
import json, urllib.request, time, gzip, subprocess
print("lu à", time.strftime("%H:%M:%S"))
g = lambda u: json.loads(urllib.request.urlopen(urllib.request.Request(u, headers={"user-agent": "verif"}), timeout=280).read())
L = [101, 105, 6, 600013, 2162]
J = ["2026-11-08T23:00:00Z", "2026-11-09T23:00:00Z", "2026-11-10T23:00:00Z", "2026-11-11T23:00:00Z", "2026-11-12T23:00:00Z", "2026-11-13T23:00:00Z", "2026-11-14T23:00:00Z", "2026-11-15T23:00:00Z"]
out = {}
for d in J:
    R = g(f"https://72-11-157-70.sslip.io/api/bot/banc?depuis={d}&plafond=100")
    out[d] = {s["num"]: {k: s.get(k) for k in ("signaux", "nonRemplis", "enCours", "trades", "gain")} for s in R["strategies"] if s["num"] in L}
    print(d, json.dumps(out[d]))
try: print("etat", json.dumps(g("https://72-11-157-70.sslip.io/api/bot/banc/etat"))[:1500])
except Exception as e: print("etat", e)
json.dump(out, open("etude/analyse/signaux_jours.json", "w")); subprocess.run(["git", "add", "etude/analyse/signaux_jours.json"])
