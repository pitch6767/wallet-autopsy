# 12.11.2026 : pourquoi plus de signaux 101/105/1114/116 depuis 03:49 UTC — lecture seule (états publics du moteur de signaux)
import json, urllib.request
def get(u):
    try:
        with urllib.request.urlopen(urllib.request.Request(u, headers={"user-agent": "analyse"}), timeout=60) as r: return json.loads(r.read())
    except Exception as e: return {"erreur": str(e)}
for u in ["https://bot95-signaux.pitch67.workers.dev/api/statut", "https://bot95-signaux.pitch67.workers.dev/api/sante",
          "https://bot95-signaux.pitch67.workers.dev/api/flux_signaux", "https://bot95.pitch67.workers.dev/api/flux_signaux"]:
    d = get(u)
    if isinstance(d, dict) and "journal" in d:
        j = d.pop("journal"); print(u, json.dumps(d, ensure_ascii=False)[:3000])
        print("journal (50 derniers):"); [print(" ", json.dumps(x, ensure_ascii=False)[:300]) for x in j[:50]]
    else: print(u, json.dumps(d, ensure_ascii=False)[:3000])
    print()
