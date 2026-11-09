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
print("=== gain par jour ($) ===")
for n in AUJ + NOUS:
    X = [t for t in T if t["num"] == n]
    print(f"{n:>7}", " | ".join(f"{d}: {sum(t['pnl'] for t in X if t['j']==d):+6.0f} ({sum(t['j']==d for t in X):3d})" for d in JJ), f"| total {sum(t['pnl'] for t in X):+6.0f}")
def profil(nom, X):
    if not X: print(nom, "—"); return
    g = [t for t in X if t["gagne"]]
    print(f"\n### {nom} : {len(X)} trades, gagnés {100*len(g)/len(X):.0f} %, gain {sum(t['pnl'] for t in X):+.0f} $, gain pour 1 $ {sum(t['pnl'] for t in X)/sum(t['mise'] for t in X):+.2f}")
    print("  prix médian", round(st.median(t["prix"] for t in X), 3), "| prix médian des gagnants", round(st.median(t["prix"] for t in g), 3) if g else "—")
    print("  seconde médiane", round(st.median(t["F"]["sec"] for t in X)), "| côté", dict(collections.Counter(t["side"] for t in X)), "| sens / BTC 1 h", dict(collections.Counter(t["F"]["sens"] for t in X)))
    print("  BTC : |mv 1 h| médian", round(st.median(abs(t["F"]["mv"]) for t in X), 1), "pb | vol 1 min médiane", round(st.median(t["F"]["vol"] for t in X), 2))
    for lab, f in [("prix", lambda t: "<0,10" if t["prix"] < .1 else "0,10-0,25" if t["prix"] < .25 else "0,25-0,50" if t["prix"] < .5 else ">=0,50"),
                   ("sens", lambda t: t["F"]["sens"]), ("seconde", lambda t: "0-60" if t["F"]["sec"] < 60 else "60-180" if t["F"]["sec"] < 180 else "180+")]:
        out = []
        for k in sorted({f(t) for t in X}):
            Y = [t for t in X if f(t) == k]; out.append(f"{k}: {len(Y)} / {100*sum(t['gagne'] for t in Y)/len(Y):.0f} % / {sum(t['pnl'] for t in Y)/sum(t['mise'] for t in Y):+.2f}")
        print(f"  par {lab} :", " ; ".join(out))
# signaux uniques
def uniq(X):
    U = {}
    for t in X: U.setdefault((t["endTs"], t["side"], round(t["prix"], 2)), t)
    return list(U.values())
profil("GAGNANTES D'AUJOURD'HUI, le 09.11", uniq([t for t in T if t["num"] in AUJ and t["j"] == "09"]))
profil("les mêmes, du 06 au 08.11", uniq([t for t in T if t["num"] in AUJ and t["j"] != "09"]))
profil("NOS STRATÉGIES (600005, 2171, 2172, 2162, 2111) les jours où on cartonne, 06–08.11", uniq([t for t in T if t["num"] in NOUS and t["j"] != "09"]))
profil("nos stratégies le 09.11", uniq([t for t in T if t["num"] in NOUS and t["j"] == "09"]))
print("\nchevauchement 09.11 : trades communs (cycle + côté) entre gagnantes d'aujourd'hui et nos stratégies :",
      len({(t["endTs"], t["side"]) for t in T if t["num"] in AUJ and t["j"] == "09"} & {(t["endTs"], t["side"]) for t in T if t["num"] in NOUS and t["j"] == "09"}))
