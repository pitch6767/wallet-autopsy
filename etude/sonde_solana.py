# 14.11.2026 : vérification version H + teneur de paires v1/v2 (lecture seule)
import json, urllib.request
g = lambda u: json.loads(urllib.request.urlopen(urllib.request.Request(u, headers={"user-agent": "analyse"}), timeout=120).read())
e = g("https://72-11-157-70.sslip.io/api/bot/banc/etat"); print("version :", e.get("version")); print("actives :", e.get("actives"), "mode :", e.get("mode")); print("regles :", json.dumps((e.get("regles") or {}).get("refuses")), (e.get("regles") or {}).get("depuis"))
p = g("https://72-11-157-70.sslip.io/api/bot/paires")
for k in ["v1", "v2", "v1MemePeriodeQueV2"]:
    v = p.get(k) or {}
    print(k, json.dumps({x: v.get(x) for x in ["depuis", "cycles", "gain", "mise", "rendementPct", "cyclesPositifs", "creux", "sommeMedianePaire", "cyclesEquilibres", "cyclesDesequilibres", "parJour"]}, ensure_ascii=False))
# 1
