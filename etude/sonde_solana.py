# 14.11.2026 : vérification remise à zéro + numéros 800001/800002 (lecture seule)
import json, urllib.request
g = lambda u: json.loads(urllib.request.urlopen(urllib.request.Request(u, headers={"user-agent": "analyse"}), timeout=120).read())
e = g("https://72-11-157-70.sslip.io/api/bot/banc/etat"); print("version :", e.get("version")); print("actives :", e.get("actives"), "mode :", e.get("mode"), "depuis :", e.get("activesDepuis"))
x = g("https://72-11-157-70.sslip.io/api/bot/banc/decisions?depuis=2026-11-13T00:00:00Z")
tp = [t for t in (x.get("tradesPaper") or []) if t.get("ouvert", "") >= "2026-11-13T10:00"]
print("onglet Trades — trades 2162 visibles depuis 13.11 11 h :", len(tp), "| dont avant 16 h :", sum(1 for t in tp if t["ouvert"] < "2026-11-14T15:00"), "| en attente :", sum(1 for t in tp if t.get("statut") != "settled"))
p = g("https://72-11-157-70.sslip.io/api/bot/paires"); print("paires :", p.get("numeros"), p.get("depuis"))
for k in ["v1", "v2"]: v = p.get(k) or {}; print(k, v.get("numero"), {z: v.get(z) for z in ["cycles", "gain", "cyclesPositifs"]})
print("avant remise :", json.dumps(p.get("avantRemise"), ensure_ascii=False)[:800])
# 1
