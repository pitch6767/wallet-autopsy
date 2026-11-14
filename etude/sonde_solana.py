# 14.11.2026 soir : lignes 800001–800004 au banc + résultats du teneur de paires (lecture seule)
import json, urllib.request, collections
g = lambda u: json.loads(urllib.request.urlopen(urllib.request.Request(u, headers={"user-agent": "analyse"}), timeout=200).read())
e = g("https://72-11-157-70.sslip.io/api/bot/banc/etat"); print("version :", e.get("version")); print("actives :", e.get("actives"), "mode :", e.get("mode"))
T = g("https://72-11-157-70.sslip.io/api/bot/banc/trades?depuis=2026-11-14T15:00:00Z&plafond=100")["trades"]
c = collections.defaultdict(lambda: [0, 0, 0.0, 0.0])
for t in T:
    if t["num"] >= 800000 and t["num"] < 900000: x = c[t["num"]]; x[0] += 1; x[1] += 1 if t["gagne"] else 0; x[2] += t["pnl"]; x[3] += t["mise"]
for n in sorted(c): x = c[n]; print("banc", n, f"trades {x[0]}, gagnés {x[1]}, gain {x[2]:.2f} $, misé {x[3]:.0f} $")
p = g("https://72-11-157-70.sslip.io/api/bot/paires")
for k in ["v1", "v2", "v3", "v4"]:
    v = p.get(k) or {}; print(k, v.get("numero"), json.dumps({z: v.get(z) for z in ["cycles", "gain", "mise", "rendementPct", "cyclesPositifs", "creux", "sommeMedianePaire", "cyclesEquilibres", "cyclesDesequilibres"]}, ensure_ascii=False))
b = [t for t in T if t["num"] == 2162]; print("2162 depuis 16 h :", len(b), "trades, gain", round(sum(t["pnl"] for t in b), 2))
# 1
