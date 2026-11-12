# 12.11.2026 : vérification garde-fous 2 — état public du bot + clients du moteur de signaux (lecture seule)
import json, urllib.request
def get(u):
    try:
        with urllib.request.urlopen(urllib.request.Request(u, headers={"user-agent": "analyse"}), timeout=60) as r: return json.loads(r.read())
    except Exception as e: return {"erreur": str(e)}
e = get("https://72-11-157-70.sslip.io/api/bot/banc/etat"); e.pop("mises", None); print(json.dumps(e, ensure_ascii=False, indent=1))
print("bot95-signaux clients :", get("https://bot95-signaux.pitch67.workers.dev/api/flux_signaux"))
s = get("https://bot95-signaux.pitch67.workers.dev/api/statut"); print("journal :"); [print(" ", x.get("at"), x.get("num"), x.get("statut"), "clients", x.get("clients")) for x in (s.get("journal") or [])[:8]]
