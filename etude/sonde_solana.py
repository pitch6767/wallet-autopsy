# 16.11.2026 14 h 46 : pourquoi aucun trade dans le banc depuis 14 h ? (lecture seule)
import json, urllib.request, time, collections
print("lu à", time.strftime("%H:%M:%S"), time.time())
def g(u):
    try: return json.loads(urllib.request.urlopen(urllib.request.Request(u, headers={"user-agent": "verif"}), timeout=200).read())
    except Exception as e: return {"ERREUR": str(e)}
T = g("https://72-11-157-70.sslip.io/api/bot/banc/trades?depuis=2026-11-16T13:00:00Z&plafond=100")
L = T.get("trades", []); print("banc trades réglés depuis 13:00Z :", len(L), "lignes", len({t["num"] for t in L}), "depuis", T.get("depuis"))
c = collections.Counter(t["ouvert"][:15] for t in L); print(sorted(c.items())[-12:])
T2 = g("https://72-11-157-70.sslip.io/api/bot/banc/trades?depuis=2026-11-16T11:00:00Z&plafond=100"); L2 = T2.get("trades", [])
c2 = collections.Counter(t["ouvert"][:15] for t in L2); print("depuis 11:00Z, par 10 min :", sorted(c2.items()))
V = g("https://72-11-157-70.sslip.io/api/bot/vitesse"); print("vitesse", json.dumps({k: V.get(k) for k in ("feu", "raisons", "signaux", "issues", "dernierSignal")}, ensure_ascii=False))
D = g("https://72-11-157-70.sslip.io/api/bot/diag?heures=2")
for h in D.get("heures", []): print(json.dumps({k: h.get(k) for k in ("heure", "signaux", "issues")}, ensure_ascii=False))
print("derniers", json.dumps(D.get("derniersSignaux", [])[:10], ensure_ascii=False))
