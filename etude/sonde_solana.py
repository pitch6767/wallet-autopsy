# 10.11.2026 : contrôle du miroir PAPER — trades de la 600005 (onglet Trades) vs ligne 600005 du banc, depuis l'activation 00 h 49 Paris (lecture seule)
import json, urllib.request, datetime as dt
def get(u):
    with urllib.request.urlopen(urllib.request.Request(u, headers={"user-agent": "analyse"}), timeout=180) as r: return json.load(r)
dep = "2026-11-09T23:49:26Z"
R = get(f"https://72-11-157-70.sslip.io/api/bot/banc/decisions?depuis={dep}")
P = [t for t in R.get("tradesPaper", []) if t["n"] == 600005]
B = [t for t in get(f"https://72-11-157-70.sslip.io/api/bot/banc/trades?depuis={dep}&plafond=100")["trades"] if t["num"] == 600005]
Pr = [t for t in P if t["statut"] == "settled"]
print("ONGLET TRADES (600005) :", len(P), "trades dont", len(Pr), "réglés, gain", round(sum(t["gain"] or 0 for t in Pr), 2), "| miroir :", sum(1 for t in P if str(t["signal"]).endswith("|p600005")), "| anciens non miroir :", sum(1 for t in P if not (t.get("signal") or "").endswith("|p600005")))
print("BANC 600005           :", len(B), "trades réglés, gain", round(sum(t["pnl"] for t in B), 2))
pb = {t["id"]: t for t in B}
ecarts = 0
for t in sorted(Pr, key=lambda t: t["ouvert"]):
    sid = str(t["signal"]).replace("|p600005", ""); b = pb.get(sid)
    ok = b is not None and abs((t["gain"] or 0) - b["pnl"]) < 0.01 and abs(t["mise"] - b["mise"]) < 0.01
    if not ok: ecarts += 1
    print(("OK   " if ok else "ÉCART"), t["ouvert"][11:19], t["cote"], round(t["prix"], 3), round(t["mise"], 2), round(t["gain"] or 0, 2), "| banc :", (b["side"], round(b["prix"], 3), round(b["mise"], 2), round(b["pnl"], 2)) if b else "—")
manquants = [b for b in B if b["id"] not in {str(t["signal"]).replace("|p600005", "") for t in Pr}]
print("trades du banc absents de l'onglet Trades :", [(b["ouvert"][11:19], b["side"], round(b["pnl"], 2)) for b in manquants])
print("écarts :", ecarts)
# relance 10:42:57 après plafond 100
