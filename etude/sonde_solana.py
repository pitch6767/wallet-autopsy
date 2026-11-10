# 10.11.2026 : contrôle 600005 — décisions + trades PAPER du bot + trades du banc, depuis minuit Paris (lecture seule)
import json, urllib.request
def get(u):
    with urllib.request.urlopen(urllib.request.Request(u, headers={"user-agent": "analyse"}), timeout=180) as r: return json.load(r)
dep = "2026-11-09T23:00:00Z"
R = get(f"https://72-11-157-70.sslip.io/api/bot/banc/decisions?depuis={dep}")
B = [t for t in get(f"https://72-11-157-70.sslip.io/api/bot/banc/trades?depuis={dep}&plafond=200")["trades"] if t["num"] == 600005]
P = [t for t in R.get("tradesPaper", []) if t["n"] == 600005]
print("BOT", len(P), "trades, gain", round(sum(t["gain"] or 0 for t in P)), "| BANC", len(B), "trades, gain", round(sum(t["pnl"] for t in B)))
cyc = sorted({t["fin"][:19] for t in P} | {__import__("datetime").datetime.utcfromtimestamp(t["endTs"] / 1000).isoformat()[:19] for t in B})
for c in cyc:
    bp = [t for t in P if t["fin"][:19] == c]; bb = [t for t in B if __import__("datetime").datetime.utcfromtimestamp(t["endTs"] / 1000).isoformat()[:19] == c]
    gp = sum(t["gain"] or 0 for t in bp); gb = sum(t["pnl"] for t in bb)
    flag = "  <== ÉCART" if abs(gp - gb) > 30 else ""
    print(f"cycle {c[11:16]} | bot {gp:+6.0f} : " + ", ".join(f"{t['cote']} {t['prix']:.3f} {t['mise']:.0f}$ {t['ouvert'][11:19]}" for t in bp) + f" | banc {gb:+6.0f} : " + ", ".join(f"{t['side']} {t['prix']:.3f} {t['mise']:.0f}$ {t['ouvert'][11:19]}" for t in bb) + flag)
print("\nDÉCISIONS refusées :")
for d in R["decisions"]:
    if not d.get("pris"): print(" ", d.get("at", "")[11:19], d.get("base"), d.get("cote"), d.get("prix"), "k", d.get("k"), "|", str(d.get("statut"))[:220])
