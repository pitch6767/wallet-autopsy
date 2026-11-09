# 09.11.2026 21 h 51 (Pitch : « analyse les trades d'aujourd'hui et reviens-moi avec une solution »). Lecture seule.
# Banc 95 h, plafond 200 $. Stratégies clés. Pourquoi aujourd'hui (09.11) est mauvais ? Caractéristiques connues AVANT/AU signal.
import json, urllib.request, collections, datetime as dt, statistics as st, math
from zoneinfo import ZoneInfo
PZ = ZoneInfo("Europe/Paris")
def get(u):
    with urllib.request.urlopen(urllib.request.Request(u, headers={"user-agent": "analyse"}), timeout=180) as r: return json.load(r)
dep = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=95)).strftime("%Y-%m-%dT%H:%M:%SZ")
T = get(f"https://72-11-157-70.sslip.io/api/bot/banc/trades?depuis={dep}&plafond=200")["trades"]
CLES = [600005, 2171, 2172, 2162, 2111, 2112, 12112, 600006, 313, 13, 1114]
T = [t for t in T if t["num"] in CLES]
t0 = min(t["endTs"] for t in T) // 1000 - 7200; t1 = max(t["endTs"] for t in T) // 1000
K = []; deb = t0 * 1000
while deb < t1 * 1000:
    k = get(f"https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=1m&limit=1000&startTime={deb}")
    if not k: break
    K += [(x[0] // 1000, float(x[1]), float(x[4]), float(x[5])) for x in k]; deb = k[-1][0] + 60000
I = {x[0]: i for i, x in enumerate(K)}
def F(t):
    d = t["endTs"] // 1000 - 300; i = I.get(d - 60)
    if i is None or i < 120: return None
    c = [K[j][2] for j in range(i - 30, i + 1)]; s = sum(abs(c[j] - c[j - 1]) for j in range(1, 31))
    er = abs(c[-1] - c[0]) / s if s else 0
    mv = 1e4 * (K[i][2] / K[i - 60][2] - 1); vol = 1e4 * st.pstdev([K[j][2] / K[j - 1][2] - 1 for j in range(i - 59, i + 1)])
    up = t["side"] == "UP"; sec = (dt.datetime.fromisoformat(t["ouvert"].replace("Z", "+00:00")).timestamp() - d)
    return dict(er=er, mv=mv, vol=vol, sens="avec 1 h" if (mv > 0) == up else "contre 1 h", prix=t["prix"], sec=sec, h=dt.datetime.fromtimestamp(d, PZ).hour, side=t["side"])
J = lambda t: dt.datetime.fromtimestamp(t["endTs"] / 1000, PZ).strftime("%d")
for t in T: t["F"] = F(t); t["j"] = J(t)
T = [t for t in T if t["F"]]
print("trades :", len(T), collections.Counter(t["j"] for t in T))
# 09.11 22 h : filtres candidats appliqués aux stratégies clés, jour par jour (gain $, plafond 200 déjà appliqué)
FI = {
  "aucun": lambda f: True,
  "A pas 04-12 h": lambda f: not (4 <= f["h"] < 12),
  "B pas contre 1 h si |mv|>=13,8": lambda f: not (f["sens"] == "contre 1 h" and abs(f["mv"]) >= 13.8),
  "C pas si vol 1 min >= 5": lambda f: f["vol"] < 5,
  "A + B": lambda f: not (4 <= f["h"] < 12) and not (f["sens"] == "contre 1 h" and abs(f["mv"]) >= 13.8),
  "A + C": lambda f: not (4 <= f["h"] < 12) and f["vol"] < 5,
}
JJ = sorted({t["j"] for t in T if t["j"] != "05"})
for n in [600005, 2171, 2172, 2162, 2111, 313]:
    print(f"\n--- {n} : " + " | ".join(JJ) + " | total | creux | trades")
    for nom, f in FI.items():
        X = sorted([t for t in T if t["num"] == n and t["j"] in JJ and f(t["F"])], key=lambda t: t["endTs"])
        c = p_ = cr = 0
        for t in X: c += t["pnl"]; p_ = max(p_, c); cr = max(cr, p_ - c)
        print(f"{nom:34s}", " | ".join(f"{sum(t['pnl'] for t in X if t['j']==d):+6.0f}" for d in JJ), f"| {c:+7.0f} | -{cr:5.0f} | {len(X)}")
print("\n=== par jour et stratégie : gain (trades, gagnés %) ===")
for n in CLES:
    X = [t for t in T if t["num"] == n]
    print(n, " | ".join(f"{d}: {sum(t['pnl'] for t in X if t['j']==d):+.0f} ({sum(t['j']==d for t in X)}, {100*sum(t['gagne'] for t in X if t['j']==d)/max(1,sum(t['j']==d for t in X)):.0f}%)" for d in sorted({t['j'] for t in T})))
print("\n=== BTC par jour : vol 1 min moyenne (pb), |mouvement 1 h| moyen, efficacité 30 min moyenne ===")
for d in sorted({t["j"] for t in T}):
    X = [t["F"] for t in T if t["j"] == d]
    print(d, f"vol {st.mean(x['vol'] for x in X):.2f}", f"|mv| {st.mean(abs(x['mv']) for x in X):.1f}", f"eff {st.mean(x['er'] for x in X):.2f}")
U = {}
for t in T:
    if t["num"] in (2171, 2172, 2162, 2111, 2112): U.setdefault((t["endTs"], t["side"], round(t["prix"], 2)), t)
U = list(U.values())
def tab(nom, f, cles=None):
    print(f"\n=== signaux uniques (portefeuilles 101+105) par {nom} : jour → trades / gagnés % / gain pour 1 $ ===")
    for g in cles or sorted({f(t) for t in U}):
        lig = []
        for d in sorted({t["j"] for t in U}):
            X = [t for t in U if t["j"] == d and f(t) == g]
            lig.append(f"{len(X)}/{100*sum(t['gagne'] for t in X)/len(X):.0f}%/{sum(t['pnl'] for t in X)/sum(t['mise'] for t in X):+.2f}" if X else "—")
        Xa = [t for t in U if f(t) == g and t["j"] != "09"]; Xb = [t for t in U if f(t) == g and t["j"] == "09"]
        print(f"{str(g):16s} |", " | ".join(lig), f"|| avant 09 : {sum(t['pnl'] for t in Xa)/max(1,sum(t['mise'] for t in Xa)):+.2f} ; 09 : {sum(t['pnl'] for t in Xb)/max(1,sum(t['mise'] for t in Xb)):+.2f}")
tab("prix", lambda t: "<0,10" if t["prix"] < .1 else "0,10-0,20" if t["prix"] < .2 else "0,20-0,35" if t["prix"] < .35 else "0,35-0,50" if t["prix"] < .5 else ">=0,50")
tab("seconde du cycle", lambda t: "0-60" if t["F"]["sec"] < 60 else "60-150" if t["F"]["sec"] < 150 else "150-240" if t["F"]["sec"] < 240 else "240+")
tab("sens / BTC 1 h", lambda t: t["F"]["sens"])
tab("côté", lambda t: t["side"])
tab("efficacité 30 min", lambda t: "<0,10" if t["F"]["er"] < .1 else "0,10-0,17" if t["F"]["er"] < .17 else "0,17-0,30" if t["F"]["er"] < .3 else ">=0,30")
tab("vol 1 min (pb)", lambda t: "<2" if t["F"]["vol"] < 2 else "2-3" if t["F"]["vol"] < 3 else "3-5" if t["F"]["vol"] < 5 else ">=5")
tab("heure (Paris)", lambda t: f"{t['F']['h']//4*4:02d}-{t['F']['h']//4*4+3:02d} h")
