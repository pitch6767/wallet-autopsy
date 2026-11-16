# 16.11.2026 : page de diagnostic /bot/diag (lecture seule)
import json, urllib.request, time
print("lu à", time.strftime("%H:%M:%S"), time.time())
g = lambda u: json.loads(urllib.request.urlopen(urllib.request.Request(u, headers={"user-agent": "verif"}), timeout=200).read())
try:
    E = g("https://72-11-157-70.sslip.io/api/bot/banc/etat"); print("version", E.get("version", "")[-60:]); print("dernierSignal", E.get("dernierSignal")); print({k: v for k, v in E.items() if k not in ("version", "mises", "choisies")})
except Exception as e: print("etat", e)
try:
    D = g("https://72-11-157-70.sslip.io/api/bot/diag?heures=3")
    for h in D["heures"]: print(json.dumps(h, ensure_ascii=False))
    print("derniers", json.dumps(D["derniersSignaux"][:8], ensure_ascii=False))
except Exception as e: print("diag", e)
P = g("https://72-11-157-70.sslip.io/api/bot/paires"); print({k: (v.get("enCours") or {}).get("start") if isinstance(v, dict) else None for k, v in P.items() if k.startswith("v")})
