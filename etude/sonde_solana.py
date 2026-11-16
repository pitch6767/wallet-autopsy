# 16.11.2026 : garde vitesse du bot — vitesse + moteur (lecture seule)
import json, urllib.request, time
print("lu à", time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()), time.time())
def g(u):
    try: return json.loads(urllib.request.urlopen(urllib.request.Request(u, headers={"user-agent": "verif"}), timeout=120).read())
    except Exception as e: return {"ERREUR": str(e)}
V = g("https://72-11-157-70.sslip.io/api/bot/vitesse?historique=70")
print("VITESSE", json.dumps(V, ensure_ascii=False)[:12000])
M = g("https://72-11-157-70.sslip.io/api/bot/moteur")
print("MOTEUR", json.dumps(M, ensure_ascii=False)[:8000])
