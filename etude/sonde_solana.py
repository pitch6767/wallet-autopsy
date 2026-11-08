# 08.11.2026 (Pitch : « analyse la journée… on a eu 2 jours comme cela, je veux la recette ») : lecture seule des trades réglés du banc
# (route publique /api/bot/banc/trades, 96 h) + bougies BTC Binance 5 min ; résultats par jour (heure de Paris). Aucun ordre, aucun réglage.
import json, urllib.request, datetime as dt, collections, statistics as st
from zoneinfo import ZoneInfo
PZ = ZoneInfo("Europe/Paris")
def get(u):
    with urllib.request.urlopen(urllib.request.Request(u, headers={"user-agent": "analyse"}), timeout=120) as r: return json.load(r)
dep = (dt.datetime.utcnow() - dt.timedelta(hours=95)).strftime("%Y-%m-%dT%H:%M:%SZ")
T = get("https://72-11-157-70.sslip.io/api/bot/banc/trades?depuis=" + dep)["trades"]
T = [t for t in T if not (9000 <= t["num"] <= 9014)]
jour = lambda ms: dt.datetime.fromtimestamp(ms / 1000, PZ).strftime("%a %d")
for t in T: t["j"] = jour(t["endTs"]); t["h"] = dt.datetime.fromtimestamp(t["endTs"] / 1000, PZ).hour; t["sec"] = round(300 - (t["endTs"] - dt.datetime.fromisoformat(t["ouvert"].replace("Z", "+00:00")).timestamp() * 1000) / 1000)
J = sorted({t["j"] for t in T}, key=lambda j: min(x["endTs"] for x in T if x["j"] == j))
print("trades réglés lus :", len(T), "depuis", dep, "; jours :", J)

# BTC : bougies 5 min (= les cycles), Binance
K = []; deb = int((dt.datetime.utcnow() - dt.timedelta(hours=100)).timestamp() * 1000)
while True:
    k = get(f"https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=5m&limit=1000&startTime={deb}")
    if not k: break
    K += k; deb = k[-1][0] + 1
    if len(k) < 1000: break
cyc = {}
for k in K: cyc[k[0] + 300000] = (float(k[1]), float(k[4]), float(k[2]), float(k[3]))
print("\n=== BTC par jour (heure de Paris), cycles 5 min ===")
print("jour | variation jour | amplitude | cycles UP % | mouvement moyen par cycle (pb) | cycles > 10 pb | plus forte tendance 1 h (pb)")
for j in J:
    C = sorted((e, v) for e, v in cyc.items() if jour(e) == j)
    if not C: continue
    o, c = C[0][1][0], C[-1][1][1]; hi = max(v[2] for _, v in C); lo = min(v[3] for _, v in C)
    mv = [1e4 * (v[1] - v[0]) / v[0] for _, v in C]
    h1 = [1e4 * (C[i + 11][1][1] - C[i][1][0]) / C[i][1][0] for i in range(len(C) - 11)]
    print(f"{j} | {100*(c-o)/o:+.2f} % | {100*(hi-lo)/o:.2f} % | {100*sum(m>0 for m in mv)/len(mv):.0f} % | {st.mean(abs(m) for m in mv):.1f} | {sum(abs(m)>10 for m in mv)} / {len(mv)} | {max(h1, key=abs):+.0f}")

# résultat par stratégie et par jour
P = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0.0, 0]))
for t in T: x = P[t["num"]][t["j"]]; x[0] += 1; x[1] += t["pnl"]; x[2] += t["gagne"]
tot = {n: sum(v[1] for v in d.values()) for n, d in P.items()}
print("\n=== gain par stratégie et par jour ($, fantôme, réglé Polymarket) — stratégies avec au moins 30 trades, triées par le dernier jour ===")
print("n° | " + " | ".join(J) + " | total | trades")
L = [n for n in P if sum(v[0] for v in P[n].values()) >= 30]
for n in sorted(L, key=lambda n: -P[n][J[-1]][1])[:45]:
    print(n, "|", " | ".join(f"{P[n][j][1]:+.0f} ({P[n][j][0]})" for j in J), f"| {tot[n]:+.0f} | {sum(v[0] for v in P[n].values())}")
print("... les 10 pires du dernier jour :")
for n in sorted(L, key=lambda n: P[n][J[-1]][1])[:10]:
    print(n, "|", " | ".join(f"{P[n][j][1]:+.0f} ({P[n][j][0]})" for j in J), f"| {tot[n]:+.0f}")

# somme de toutes les stratégies par jour (pour repérer les « grands jours »)
print("\n=== tous signaux confondus, par jour : trades, gagnés %, gain total, gain moyen par trade ===")
for j in J:
    X = [t for t in T if t["j"] == j]
    print(j, len(X), f"{100*sum(t['gagne'] for t in X)/len(X):.0f} %", f"{sum(t['pnl'] for t in X):+.0f}", f"{st.mean(t['pnl'] for t in X):+.2f}")

# caractéristiques des trades (signaux uniques) : prix, seconde du cycle, sens par rapport au BTC du cycle et de l'heure d'avant
U = {}
for t in T: U.setdefault((t["endTs"], t["side"], round(t["prixSignal"], 2)), t)
def tranche(p): return "<0,15" if p < .15 else "0,15-0,30" if p < .3 else "0,30-0,50" if p < .5 else "0,50-0,70" if p < .7 else ">=0,70"
def sens1h(t):
    e = t["endTs"] - 300000; a = cyc.get(e - 3600000 + 300000); b = cyc.get(e)
    if not a or not b: return "?"
    m = 1e4 * (b[1] - a[0]) / a[0]; up = t["side"] == "UP"
    return "plat (<15 pb)" if abs(m) < 15 else ("dans le sens de l'heure" if (m > 0) == up else "contre l'heure")
for nom, f in [("prix d'entrée", lambda t: tranche(t["prix"])), ("seconde du cycle", lambda t: "0-60" if t["sec"] < 60 else "60-120" if t["sec"] < 120 else "120-180" if t["sec"] < 180 else "180-240" if t["sec"] < 240 else "240-300"),
               ("sens / BTC heure d'avant", sens1h), ("côté", lambda t: t["side"])]:
    print(f"\n=== signaux uniques par {nom} : jour → trades / gagnés % / gain moyen par 1 $ misé ===")
    for g in sorted({f(t) for t in U.values()}):
        lig = []
        for j in J:
            X = [t for t in U.values() if t["j"] == j and f(t) == g]
            lig.append(f"{len(X)} / {100*sum(t['gagne'] for t in X)/len(X):.0f} % / {sum(t['pnl'] for t in X)/max(1e-9, sum(t['mise'] for t in X)):+.2f}" if X else "—")
        print(g, "|", " | ".join(lig))
# dernier jour : heures
print(f"\n=== {J[-1]} par heure (signaux uniques) : trades, gagnés %, gain par 1 $, mouvement BTC de l'heure (pb) ===")
for h in range(24):
    X = [t for t in U.values() if t["j"] == J[-1] and t["h"] == h]
    C = sorted((e, v) for e, v in cyc.items() if jour(e) == J[-1] and dt.datetime.fromtimestamp(e / 1000, PZ).hour == h)
    if X: print(h, len(X), f"{100*sum(t['gagne'] for t in X)/len(X):.0f} %", f"{sum(t['pnl'] for t in X)/sum(t['mise'] for t in X):+.2f}", f"{1e4*(C[-1][1][1]-C[0][1][0])/C[0][1][0]:+.0f}" if C else "")
