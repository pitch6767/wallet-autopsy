# Garde vitesse horaire (lecture seule) — 15:36 UTC 19.11
import json, urllib.request, time
print("lu à", time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()), time.time())
def g(u):
    try: return json.loads(urllib.request.urlopen(urllib.request.Request(u, headers={"user-agent": "verif"}), timeout=200).read())
    except Exception as e: return {"ERREUR": str(e)}
V = g("https://72-11-157-70.sslip.io/api/bot/vitesse?historique=70")
print("vitesse", json.dumps({k: V.get(k) for k in ("ERREUR", "feu", "raisons", "achatMs", "trajetSignalMs", "blocageServeurMs", "moteur", "signaux", "issues", "dernierSignal")}, ensure_ascii=False)[:2500])
H = V.get("minutesNonVertes", []) or []; print("minutes non vertes :", len(H))
for h in H[-70:]: print(h.get("t", "")[11:16], h.get("feu"), "; ".join(h.get("raisons") or [])[:200])
M = g("https://72-11-157-70.sslip.io/api/bot/moteur"); s = M.get("statut") or {}
print("moteur", M.get("ERREUR"), "lu", M.get("lu"), "flux", json.dumps(s.get("flux"), ensure_ascii=False)[:800], "reconnexions", s.get("reconnexions"), "erreurs", json.dumps((s.get("erreurs") or [])[:10], ensure_ascii=False)[:800])
J = g("https://72-11-157-70.sslip.io/api/bot/maj"); print("MAJ-AUTO", json.dumps({k: v for k, v in J.items() if k != "journal"}, ensure_ascii=False)[:2000]); print("MAJ-JOURNAL", json.dumps((J.get("journal") or [])[-15:], ensure_ascii=False)[:3000])

print("BLOCAGES", json.dumps(V.get("blocages"), ensure_ascii=False)[:4000])

MC = g("https://72-11-157-70.sslip.io/api/bot/moteur"); st = (MC or {}).get("statut") or {}
print("MOTEUR-COMPLET", json.dumps({k: st.get(k) for k in ("heure", "clients", "cycle", "pause429", "rondesBloquees", "rondeEnCoursS", "secoursPrixABattre", "relaisSecours", "doublonsPoly", "ouvertes", "strategies", "nums", "ages_s")}, ensure_ascii=False)[:2500])
print("MOTEUR-PERF", json.dumps(st.get("perf"), ensure_ascii=False)[:1500])
BE = g("https://72-11-157-70.sslip.io/api/bot/banc/etat"); print("SOURCE", json.dumps((BE or {}).get("sourceSignaux"), ensure_ascii=False)[:800], json.dumps((BE or {}).get("moteur"), ensure_ascii=False)[:800])

DG = g("https://72-11-157-70.sslip.io/api/bot/diag?heures=14"); print("DIAG-HEURES", json.dumps(DG, ensure_ascii=False)[:6000])

print("EXECUTEUR", json.dumps((V or {}).get("executeur"), ensure_ascii=False)[:1200]); print("MEMOIRE", json.dumps((V or {}).get("memoire"), ensure_ascii=False)[:1200])
