# 16.11.2026 : santé du moteur de signaux bot95-signaux et de bot95 (lecture seule)
import json, urllib.request, time
print("lu à", time.strftime("%H:%M:%S"), time.time())
def g(u):
    try: return urllib.request.urlopen(urllib.request.Request(u, headers={"user-agent": "verif"}), timeout=60).read().decode()[:3000]
    except Exception as e: return f"ERREUR {e}"
print("== statut signaux"); print(g("https://bot95-signaux.pitch67.workers.dev/api/statut"))
print("== bot95 etat"); print(g("https://bot95.pitch67.workers.dev/api/etat")[:2000])
D = json.loads(g("https://72-11-157-70.sslip.io/api/bot/diag?heures=2") or "{}")
for h in D.get("heures", []): print(json.dumps(h, ensure_ascii=False)[:600])
