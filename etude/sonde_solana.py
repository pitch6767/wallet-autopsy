# 16.11.2026 18:32 : état de la mise à jour automatique + vitesse (lecture seule)
import json, urllib.request, time
print("lu à", time.strftime("%H:%M:%S"), time.time())
def g(u):
    try: return json.loads(urllib.request.urlopen(urllib.request.Request(u, headers={"user-agent": "verif"}), timeout=200).read())
    except Exception as e: return {"ERREUR": str(e)}
V = g("https://72-11-157-70.sslip.io/api/bot/vitesse?historique=20"); print("vitesse", json.dumps({k: V.get(k) for k in ("feu", "raisons", "achatMs", "trajetSignalMs", "blocageServeurMs", "moteur", "signaux", "issues", "dernierSignal")}, ensure_ascii=False)[:1500])
H = V.get("minutesNonVertes", []); print("minutes non vertes (3 h) :", len(H)); 
for h in H[-40:]: print(h["t"][11:16], h["feu"], "; ".join(h["raisons"])[:160])
D = g("https://72-11-157-70.sslip.io/api/bot/diag?heures=1")
for h in D.get("heures", []): print(json.dumps(h, ensure_ascii=False)[:700])
M = g("https://72-11-157-70.sslip.io/api/bot/moteur"); s = M.get("statut") or {}; print("moteur", M.get("lu"), s.get("flux"), s.get("reconnexions"), "erreurs", (s.get("erreurs") or [])[:10], "perf", json.dumps(s.get("perf"))[:600])

J = g("https://72-11-157-70.sslip.io/api/bot/maj"); print("MAJ-AUTO", json.dumps(J, ensure_ascii=False)[:3000])
