# 12.11.2026 : rejouer le trou 03:53-maintenant — quelles données bot95 (Cloudflare) a-t-il gardées ? (lecture seule)
import json, urllib.request, urllib.parse
def get(u):
    try:
        with urllib.request.urlopen(urllib.request.Request(u, headers={"user-agent": "analyse"}), timeout=90) as r: return json.loads(r.read())
    except Exception as e: return {"erreur": str(e)}
noms = ["PORTEFEUILLE 400 + idées", "PORTEFEUILLE 400", "corrige : desaccord 20 + foule bybit x2 + idées", "corrige : desaccord 20 + foule bybit x2",
        "corrige : V2-F + pas les deux baissent + carnet + sur mesure", "corrige : V2-F + pas les deux baissent + carnet",
        "TWAP fin quantiles + idées", "TWAP fin quantiles"]
for n in noms:
    d = get("https://bot95.pitch67.workers.dev/api/hist?s=" + urllib.parse.quote(n + " BTC"))
    a = d.get("archive") or []; der = d.get("derniers") or []
    auj = [x for x in a if str(x[0]) >= "2026-11-12T03:50"]
    print(n, "| résumé", d.get("resume"), "| archive", len(a), "dont depuis 03:50 UTC", len(auj), "| derniers", len(der), d.get("erreur", ""))
    for x in auj[:3]: print("   ", x)
s = get("https://bot95.pitch67.workers.dev/api/sig?a=BTC&n=3"); print("sig clés", (s.get("cles") or [])[:3], s.get("erreur", ""))
k = (s.get("cles") or [None])[0]
if s.get("docs"): print("doc exemple (début):", json.dumps(s["docs"][0], ensure_ascii=False)[:600])
s2 = get("https://bot95.pitch67.workers.dev/api/sig?a=BTC&n=120&apres=sig:BTC:1794469000"); print("sig après 03:50 UTC :", len(s2.get("cles") or []), (s2.get("cles") or [])[:2], (s2.get("cles") or [])[-2:])
