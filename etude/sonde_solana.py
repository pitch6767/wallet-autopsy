# 16.11.2026 15 h : signaux remplis / non remplis par tranche de 10 min et trades réglés au banc depuis 14 h (lecture seule)
import json, urllib.request, time, collections
print("lu à", time.strftime("%H:%M:%S"), time.time())
def g(u):
    try: return json.loads(urllib.request.urlopen(urllib.request.Request(u, headers={"user-agent": "verif"}), timeout=200).read())
    except Exception as e: return {"ERREUR": str(e)}
D = g("https://72-11-157-70.sslip.io/api/bot/diag?heures=3")
for h in D.get("heures", []): print(json.dumps({k: h.get(k) for k in ("heure", "signaux", "issues", "delaiAchatMs", "trajetMs")}, ensure_ascii=False))
V = g("https://72-11-157-70.sslip.io/api/bot/vitesse"); print("vitesse 15 min", json.dumps({k: V.get(k) for k in ("feu", "raisons", "signaux", "issues", "dernierSignal")}, ensure_ascii=False))
M = g("https://72-11-157-70.sslip.io/api/bot/moteur"); s = M.get("statut") or {}; print("moteur", M.get("lu"), s.get("flux"), s.get("reconnexions"), "doublons", s.get("doublonsPoly"))
T = g("https://72-11-157-70.sslip.io/api/bot/banc/trades?depuis=2026-11-16T13:00:00Z&plafond=100"); L = T.get("trades", [])
c = collections.Counter(t["ouvert"][:15] for t in L); print("banc réglés depuis 14 h (par 10 min UTC) :", sorted(c.items()))
