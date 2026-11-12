# 12.11.2026 14 h : pourquoi la 600005 n'a plus de trade depuis 04 h 20 ? — lecture seule
import json, urllib.request, collections
def get(u):
    with urllib.request.urlopen(urllib.request.Request(u, headers={"user-agent": "analyse"}), timeout=180) as r: return json.load(r)
T = get("https://72-11-157-70.sslip.io/api/bot/banc/trades?depuis=2026-11-12T03:00:00Z&plafond=100")["trades"]
c = collections.Counter(t["num"] for t in T)
print("trades réglés du banc depuis 04 h Paris :", len(T), "| dernier :", max((t["ouvert"] for t in T), default=None))
for n in [101, 105, 2171, 2172, 600005, 600006, 600013, 1114, 116]: print(n, c.get(n, 0), "| dernier :", max((t["ouvert"] for t in T if t["num"] == n), default=None))
D = get("https://72-11-157-70.sslip.io/api/bot/banc/decisions?depuis=2026-11-12T03:00:00Z")
print("décisions du moteur :", len(D.get("decisions", [])))
for d in D.get("decisions", [])[-8:]: print(" ", d.get("at", "")[11:19], d.get("base"), d.get("cote"), "k", d.get("k"), "eff", d.get("eff"), "tend", d.get("tend"), "|", str(d.get("statut"))[:120])
