# 09.11.2026 22 h 19 (Pitch : « remets dans le bot les stratégies qui ont fait les meilleurs gains aujourd'hui ») — lecture seule, plafond 200 $
import json, urllib.request, collections
with urllib.request.urlopen(urllib.request.Request("https://72-11-157-70.sslip.io/api/bot/banc/trades?depuis=2026-11-08T23:00:00Z&plafond=200", headers={"user-agent": "analyse"}), timeout=180) as r: T = json.load(r)["trades"]
G = collections.defaultdict(lambda: [0, 0.0, 0])
for t in T: G[t["num"]][0] += 1; G[t["num"]][1] += t["pnl"]; G[t["num"]][2] += t["gagne"]
sig = collections.defaultdict(list)
for n in G: sig[tuple(sorted((t["endTs"], t["side"], round(t["pnl"], 1)) for t in T if t["num"] == n))].append(n)
grp = {min(v): sorted(v) for v in sig.values()}
print("lignes :", len(G), "différentes :", len(grp), "dernier trade :", max(t["ouvert"] for t in T))
for n, (k, g, w) in sorted(((n, G[n]) for n in grp), key=lambda x: -x[1][1])[:25]:
    print(n, f"{g:+.0f} $", k, "trades", f"{100*w/k:.0f} %", "doublons :", grp[n][1:6])
