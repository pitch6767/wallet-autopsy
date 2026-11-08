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

# 08.11 (Pitch : « tu rajoutes les stratégies qui cartonnent quand ça bouge beaucoup ») : régime connu AVANT le cycle =
# mouvement moyen |clôture − ouverture| des 12 cycles 5 min précédents (1 h). calme < 4 pb, moyen 4–8, agité >= 8.
ordre = sorted(cyc)
def regime(endTs):
    i = next((k for k, e in enumerate(ordre) if e >= endTs - 300000), None)
    if i is None or i < 12: return None
    m = st.mean(abs(1e4 * (cyc[e][1] - cyc[e][0]) / cyc[e][0]) for e in ordre[i - 12:i])
    return "calme" if m < 4 else "moyen" if m < 8 else "agité"
cache = {}
for t in T:
    if t["endTs"] not in cache: cache[t["endTs"]] = regime(t["endTs"])
    t["r"] = cache[t["endTs"]]
print("\ncycles par régime :", collections.Counter(cache.values()))
R = ["calme", "moyen", "agité"]
P = collections.defaultdict(lambda: collections.defaultdict(list))
for t in sorted(T, key=lambda t: t["endTs"]):
    if t["r"]: P[t["num"]][t["r"]].append(t)
def stats(L):
    if not L: return "—"
    g = sum(t["pnl"] for t in L); cum = pic = creux = 0
    for t in L: cum += t["pnl"]; pic = max(pic, cum); creux = max(creux, pic - cum)
    jours = collections.defaultdict(float)
    for t in L: jours[t["j"]] += t["pnl"]
    return f"{g:+.0f} $ ({len(L)} tr, {100*sum(t['gagne'] for t in L)/len(L):.0f} %, creux -{creux:.0f}, jours neg {sum(v<0 for v in jours.values())}/{len(jours)}, mise moy {st.mean(t['mise'] for t in L):.0f})"
for r in R:
    L = [n for n in P if len(P[n][r]) >= 25]
    print(f"\n=== régime {r} : 25 meilleures stratégies (au moins 25 trades dans ce régime) — et ce qu'elles font dans les autres régimes ===")
    for n in sorted(L, key=lambda n: -sum(t["pnl"] for t in P[n][r]))[:25]:
        print(n, "|", r, stats(P[n][r]), "|| " + " | ".join(f"{x}: {stats(P[n][x])}" for x in R if x != r))
