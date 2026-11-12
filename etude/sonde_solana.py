# 12.11.2026 : affichage rapide en ligne ? version du bot, nouvelle route, page publiée (lecture seule)
import urllib.request, json, re
def g(u):
    try:
        with urllib.request.urlopen(urllib.request.Request(u, headers={"user-agent": "analyse"}), timeout=60) as r: return r.status, r.read()
    except urllib.error.HTTPError as e: return e.code, e.read()
B = "https://72-11-157-70.sslip.io"
s, b = g(B + "/api/bot/banc/etat"); e = json.loads(b); print("version :", e.get("version"), "| actives", e.get("actives"), "| moteur ok", (e.get("moteur") or {}).get("ok"))
print("route /api/bot/trades/version (sans connexion, 401 attendu = elle existe) :", g(B + "/api/bot/trades/version")[0])
s, h = g(B + "/"); js = re.findall(rb'/assets/(index-[^"]+\.js)', h); print("page publiée :", js)
if js:
    s, j = g(B + "/assets/" + js[0].decode()); print("contient la nouvelle version du tableau de bord :", b"trades/version" in j, b"trades500" in j)
