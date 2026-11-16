# 16.11.2026 garde vitesse : lecture seule de /vitesse?historique=70 et /moteur
import json, urllib.request, time
print("lu à", time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()), time.time())
def g(u):
    try: return json.loads(urllib.request.urlopen(urllib.request.Request(u, headers={"user-agent": "verif"}), timeout=120).read())
    except Exception as e: return {"ERREUR": str(e)}
print("VITESSE", json.dumps(g("https://72-11-157-70.sslip.io/api/bot/vitesse?historique=70"), ensure_ascii=False))
print("MOTEUR", json.dumps(g("https://72-11-157-70.sslip.io/api/bot/moteur"), ensure_ascii=False))
