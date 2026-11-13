# 13.11.2026 : aucun signal refusé depuis 11 h 32 — contrôle des trades notés et du BTC (lecture seule)
import json, urllib.request, collections
def get(u):
    with urllib.request.urlopen(urllib.request.Request(u, headers={"user-agent": "analyse"}), timeout=120) as r: return json.loads(r.read())
t = get("https://72-11-157-70.sslip.io/api/bot/banc/trades?depuis=2026-11-13T10:00:00Z&plafond=0").get("trades") or []
B = [x for x in t if x["num"] < 1000]
C = collections.defaultdict(list)
for x in B: C[x["endTs"]].append(x)
k = get("https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=1m&limit=90")
O = {int(c[0]) // 1000: (float(c[1]), float(c[4])) for c in k}
for e in sorted(C):
    s = e // 1000 - 300; o = O.get(s); f = O.get(s + 240)
    mv = (f[1] / o[0] - 1) * 1e4 if o and f else None
    L = C[e]; sides = collections.Counter(x["side"] for x in L)
    print(f"cycle {s} ({len(L)} trades de base) côtés {dict(sides)} prix moy {sum(x['prixSignal'] for x in L)/len(L):.2f} mise moy {sum(x['mise'] for x in L)/len(L):.0f} gagnés {sum(x['gagne'] for x in L)} | BTC sur le cycle {mv and round(mv,1)} pb | ouvert {min(x['ouvert'] for x in L)[11:19]}–{max(x['ouvert'] for x in L)[11:19]}")
