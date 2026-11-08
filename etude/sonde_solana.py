# 08.11.2026 21 h : classement du banc depuis 16 h pour 2171 / 2172 / 12112 et les 600000 — lecture seule /api/bot/banc/trades
import json, urllib.request, collections
with urllib.request.urlopen(urllib.request.Request("https://72-11-157-70.sslip.io/api/bot/banc/trades?depuis=2026-11-08T15:00:00Z&plafond=200", headers={"user-agent": "analyse"}), timeout=120) as r: T = json.load(r)["trades"]
G = collections.defaultdict(lambda: [0, 0.0])
for t in T: G[t["num"]][0] += 1; G[t["num"]][1] += t["pnl"]
print("trades réglés depuis 16 h :", len(T), "; dernier :", max(t["ouvert"] for t in T))
print("top 12 :", [(n, round(g), k) for n, (k, g) in sorted(G.items(), key=lambda x: -x[1][1])[:12]])
for n in [2171, 2172, 12112] + list(range(600001, 600009)):
    print(n, G[n][0], "trades", round(G[n][1]), "$")
big = sorted([t for t in T if t["num"] == 2171], key=lambda t: -t["pnl"])[:3]
print("plus gros gains 2171 :", [(t["ouvert"][11:19], t["side"], round(t["prix"], 2), round(t["pnl"])) for t in big])
# relance 20:08:30
# relance 20:17:21
