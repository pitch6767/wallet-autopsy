# 10.11.2026 12 h 49 (Pitch : « différence entre l'onglet Trades et le banc ? résultats 2x sur le banc ») : la 600005 du banc depuis l'activation PAPER (10.11 00 h 48 Paris) — lecture seule
import json, urllib.request
for dep, lab in [("2026-11-09T23:48:00Z", "depuis l'activation (00 h 48)"), ("2026-11-08T15:00:00Z", "depuis la remise à 0 (dim. 16 h)")]:
    with urllib.request.urlopen(urllib.request.Request(f"https://72-11-157-70.sslip.io/api/bot/banc/trades?depuis={dep}&plafond=200", headers={"user-agent": "analyse"}), timeout=180) as r: T = json.load(r)["trades"]
    X = sorted([t for t in T if t["num"] == 600005], key=lambda t: t["ouvert"])
    print(f"\n600005 {lab} : {len(X)} trades, gain {sum(t['pnl'] for t in X):+.0f} $, misé {sum(t['mise'] for t in X):.0f} $, mise moyenne {sum(t['mise'] for t in X)/max(1,len(X)):.0f} $")
    if lab.startswith("depuis l'act"):
        cyc = {}
        for t in X: cyc.setdefault((t["endTs"], t["side"]), []).append(t)
        print("cycles+côté :", len(cyc), "; cycles avec plusieurs entrées :", sum(len(v) > 1 for v in cyc.values()))
        for t in X: print(" ", t["ouvert"][11:19], "UTC", t["side"], "prix", round(t["prix"], 3), "mise", round(t["mise"]), "gain", round(t["pnl"]), "gagné" if t["gagne"] else "perdu")
