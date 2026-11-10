# 10.11.2026 : comparaison banc 600005 / décisions du moteur depuis la mise en ligne de 836a383 — lecture seule
import json, urllib.request
def get(u):
    with urllib.request.urlopen(urllib.request.Request(u, headers={"user-agent": "analyse"}), timeout=180) as r: return json.load(r)
dep = "2026-11-10T12:05:00Z"
D = get(f"https://72-11-157-70.sslip.io/api/bot/banc/decisions?depuis={dep}")["decisions"]
T = [t for t in get(f"https://72-11-157-70.sslip.io/api/bot/banc/trades?depuis={dep}&plafond=200")["trades"] if t["num"] == 600005]
print("décisions du moteur :", len(D), "; trades 600005 du banc réglés :", len(T))
for d in D: print("MOTEUR", d.get("at", "")[11:19], d.get("base"), d.get("cote"), d.get("prix"), "k", d.get("k"), "eff", d.get("eff"), "tend", d.get("tend"), "h", d.get("heure"), "|", d.get("statut"), "| pris" if d.get("pris") else "")
for t in sorted(T, key=lambda t: t["ouvert"]): print("BANC  ", t["ouvert"][11:19], t["side"], round(t["prix"], 3), "mise", round(t["mise"]), "gain", round(t["pnl"]))
