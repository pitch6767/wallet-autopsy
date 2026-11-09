# 09.11.2026 22 h 23 (Pitch : « analyse ces trades et compare-les à ceux des jours où on cartonne »). Lecture seule, plafond 200 $.
import json, urllib.request, collections, datetime as dt, statistics as st
from zoneinfo import ZoneInfo
PZ = ZoneInfo("Europe/Paris")
def get(u):
    with urllib.request.urlopen(urllib.request.Request(u, headers={"user-agent": "analyse"}), timeout=180) as r: return json.load(r)
dep = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=95)).strftime("%Y-%m-%dT%H:%M:%SZ")
T = get(f"https://72-11-157-70.sslip.io/api/bot/banc/trades?depuis={dep}&plafond=200")["trades"]
AUJ = [2165, 2175, 300072, 301072, 11001, 1001, 11022, 11021, 10322, 10122]
NOUS = [600005, 2171, 2172, 2162, 2111]
T = [t for t in T if t["num"] in AUJ + NOUS]
t0 = min(t["endTs"] for t in T) // 1000 - 7200; t1 = max(t["endTs"] for t in T) // 1000
K = []; deb = t0 * 1000
while deb < t1 * 1000:
    k = get(f"https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=1m&limit=1000&startTime={deb}")
    if not k: break
    K += [(x[0] // 1000, float(x[4])) for x in k]; deb = k[-1][0] + 60000
I = {x[0]: i for i, x in enumerate(K)}
for t in T:
    d = t["endTs"] // 1000 - 300; i = I.get(d - 60); t["j"] = dt.datetime.fromtimestamp(d, PZ).strftime("%d")
    if i is None or i < 61: t["F"] = None; continue
    mv = 1e4 * (K[i][1] / K[i - 60][1] - 1); vol = 1e4 * st.pstdev([K[j][1] / K[j - 1][1] - 1 for j in range(i - 59, i + 1)])
    sec = dt.datetime.fromisoformat(t["ouvert"].replace("Z", "+00:00")).timestamp() - d
    t["F"] = dict(mv=mv, vol=vol, sens="avec" if (mv > 0) == (t["side"] == "UP") else "contre", sec=sec, h=dt.datetime.fromtimestamp(d, PZ).hour)
T = [t for t in T if t["F"] and t["j"] in ("06", "07", "08", "09")]
JJ = ["06", "07", "08", "09"]
# 09.11 22 h 30 : règle « jour de tendance » — 600005 telle quelle, sauf quand le BTC a beaucoup bougé dans l'heure (|mv| ≥ X) ou est nerveux (vol ≥ V) :
# alors seulement les trades dans le sens du mouvement de l'heure (ou la 2175 à la place).
B = sorted([t for t in T if t["num"] == 600005], key=lambda t: t["endTs"]); B75 = [t for t in T if t["num"] == 2175]
def res(X):
    X = sorted(X, key=lambda t: t["endTs"]); c = p = cr = 0
    for t in X: c += t["pnl"]; p = max(p, c); cr = max(cr, p - c)
    return " | ".join(f"{sum(t['pnl'] for t in X if t['j']==d):+6.0f}" for d in JJ) + f" | {c:+7.0f} | -{cr:5.0f} | {len(X)}"
print("règle : 06 | 07 | 08 | 09 | total | creux | trades")
print(f"{'600005 telle quelle':44s}", res(B))
print(f"{'2175 seule':44s}", res(B75))
for X in (15, 20, 25, 30, 40):
    tend = lambda t, X=X: abs(t["F"]["mv"]) >= X
    print(f"{'|mv| ≥ ' + str(X) + ' : seulement dans le sens':44s}", res([t for t in B if not tend(t) or t["F"]["sens"] == "avec"]))
    print(f"{'|mv| ≥ ' + str(X) + ' : 2175 à la place':44s}", res([t for t in B if not tend(t)] + [t for t in B75 if tend(t)]))
for V in (3, 4, 5):
    nerv = lambda t, V=V: t["F"]["vol"] >= V
    print(f"{'vol ≥ ' + str(V) + ' : seulement dans le sens':44s}", res([t for t in B if not nerv(t) or t["F"]["sens"] == "avec"]))
    print(f"{'vol ≥ ' + str(V) + ' : 2175 à la place':44s}", res([t for t in B if not nerv(t)] + [t for t in B75 if nerv(t)]))
