# 17.11.2026 03:35 : garde horaire — vérification vitesse/moteur/maj (lecture seule)
import json, urllib.request, time
print("lu à", time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()), time.time())
def g(u):
    try: return json.loads(urllib.request.urlopen(urllib.request.Request(u, headers={"user-agent": "verif"}), timeout=200).read())
    except Exception as e: return {"ERREUR": str(e)}
V = g("https://72-11-157-70.sslip.io/api/bot/vitesse?historique=70")
print("vitesse", json.dumps({k: V.get(k) for k in ("feu", "raisons", "achatMs", "trajetSignalMs", "blocageServeurMs", "moteur", "signaux", "issues", "dernierSignal", "ERREUR")}, ensure_ascii=False)[:3000])
H = V.get("minutesNonVertes", []) or []
print("minutes non vertes (70 min) :", len(H), "dont rouges :", sum(1 for h in H if h.get("feu") == "rouge"))
for h in H[-70:]: print(h.get("t", "")[11:16], h.get("feu"), "; ".join(h.get("raisons", []))[:160])
M = g("https://72-11-157-70.sslip.io/api/bot/moteur")
print("MOTEUR", json.dumps(M, ensure_ascii=False)[:4000])

J = g("https://72-11-157-70.sslip.io/api/bot/maj"); print("MAJ-AUTO", json.dumps({k: v for k, v in J.items() if k != "journal"}, ensure_ascii=False)[:3000])
for l in (J.get("journal") or [])[-12:]: print("  maj|", str(l)[:300])
