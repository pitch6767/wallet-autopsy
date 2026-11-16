# 16.11.2026 (2) : contrôle après déploiement — moteur de signaux (deux flux), flottes F3/F20, diagnostic (lecture seule)
import json, urllib.request, time
print("lu à", time.strftime("%H:%M:%S"), time.time())
def g(u):
    try: return json.loads(urllib.request.urlopen(urllib.request.Request(u, headers={"user-agent": "verif"}), timeout=120).read())
    except Exception as e: return {"ERREUR": str(e)}
E = g("https://72-11-157-70.sslip.io/api/bot/banc/etat"); print("version", str(E.get("version", E))[-160:]); print("moteur", E.get("moteur"))
M = g("https://72-11-157-70.sslip.io/api/bot/moteur"); s = (M.get("statut") or {}); print("lu", M.get("lu"), "flux", s.get("flux"), "reconnexions", s.get("reconnexions"), "doublonsPoly", s.get("doublonsPoly"), "secours", s.get("secoursPrixABattre"), "pause429", s.get("pause429"), "cycle", s.get("cycle")); print("erreurs", (s.get("erreurs") or [])[:8])
D = g("https://72-11-157-70.sslip.io/api/bot/diag?heures=2")
for h in D.get("heures", []): print(json.dumps(h, ensure_ascii=False)[:500])
T = g("https://72-11-157-70.sslip.io/api/bot/banc/trades?depuis=2026-11-15T00:00:00Z&plafond=100")
L = [t for t in T.get("trades", []) if t["num"] in (900003, 900020)]; print("flottes", len(L), [ (t["num"], t["ouvert"][:16], t["prix"], round(t["mise"]), round(t["pnl"])) for t in L[-6:]])
