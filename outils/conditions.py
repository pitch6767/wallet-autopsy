# 06.11.2026 — Étude H-CONDITIONS (méthode etude-fantome) sur les VRAIS trades du banc d'essai (signaux reçus, vrai carnet, frais, règlement Polymarket),
# 200 $ par cycle et par stratégie. Conditions de marché connues AVANT chaque trade (heure précédente, bougies 5 min BTCUSDT Binance) : pas de fuite du futur.
# 1) pour chaque stratégie : gain avec chaque limite de prix (+5 c, +2 c, +20 %, +1 c) -> meilleure limite ; 2) gain par condition de marché.
import json, sys, urllib.request, statistics, collections, datetime as dt
VPS, DEP = sys.argv[1], sys.argv[2]
def get(u):
    with urllib.request.urlopen(urllib.request.Request(u, headers={"cache-control": "no-store", "user-agent": "etude"}), timeout=120) as r: return json.load(r)
LIM = ["5c", "2c", "20pc", "1c"]
T = {}
for p in LIM:
    d = get(f"{VPS}/api/bot/banc/trades?depuis={DEP}&plafond=200" + ("" if p == "5c" else f"&prix={p}"))
    T[p] = d["trades"]; print("limite", p, "trades", len(T[p]), "depuis", d["depuis"])
# bougies 5 min
t0 = int(dt.datetime.fromisoformat(DEP.replace("Z", "+00:00")).timestamp() * 1000) - 2 * 3600_000; t1 = int(dt.datetime.now(dt.timezone.utc).timestamp() * 1000)
K = {}
while t0 < t1:
    ks = get(f"https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=5m&startTime={t0}&limit=1000")
    if not ks: break
    for k in ks: K[k[0] // 1000] = (float(k[1]), float(k[2]), float(k[3]), float(k[4]))
    t0 = ks[-1][0] + 300_000
print("bougies", len(K))
def cond(endTs):
    s = endTs // 1000 - 300; prev = [K.get(s - 300 * i) for i in range(1, 13)]
    if any(x is None for x in prev): return None
    closes = [x[3] for x in reversed(prev)]
    rets = [closes[i] / closes[i - 1] - 1 for i in range(1, len(closes))]
    vol = statistics.pstdev(rets) * 1e4; tend = abs(closes[-1] / prev[-1][0] - 1) * 1e4
    h = (dt.datetime.fromtimestamp(s, dt.timezone.utc) + dt.timedelta(hours=1)); hh = h.hour + h.minute / 60
    plage = "nuit 00-08" if hh < 8 else "Europe 08-15h30" if hh < 15.5 else "US 15h30-22" if hh < 22 else "soir 22-24"
    return vol, tend, plage, h.strftime("%d.%m")
# terciles calculés sur tous les cycles de la période
C = {}
for s in K:
    c = cond((s + 300) * 1000)
    if c: C[s] = c
vs = sorted(c[0] for c in C.values()); ts = sorted(c[1] for c in C.values())
qv = (vs[len(vs) // 3], vs[2 * len(vs) // 3]); qt = (ts[len(ts) // 3], ts[2 * len(ts) // 3])
cls = lambda x, q: "bas" if x < q[0] else "moyen" if x < q[1] else "haut"
print(f"seuils agitation (pb/5 min) {qv[0]:.1f} / {qv[1]:.1f} ; seuils tendance 1 h (pb) {qt[0]:.1f} / {qt[1]:.1f}")
# 1) meilleure limite par stratégie
G = collections.defaultdict(lambda: {p: [0.0, 0] for p in LIM})
for p in LIM:
    for t in T[p]: g = G[t["num"]][p]; g[0] += t["pnl"]; g[1] += 1
noms = {}
try:
    for c in get("https://raw.githubusercontent.com/pitch6767/wallet-autopsy/main/bot95/src/catalogue.json"): noms[c["n"]] = c["nom"]
except Exception: pass
R = [(n, g) for n, g in G.items() if g["5c"][1] >= 15]
best = collections.Counter(max(LIM, key=lambda p: g[p][0]) for n, g in R)
print("\n=== 1) MEILLEURE LIMITE DE PRIX (stratégies avec au moins 15 trades à +5 c) ===")
print("nombre de stratégies dont la meilleure limite est :", dict(best))
print("n° | stratégie | +5 c | +2 c | +20 % | +1 c | meilleure")
for n, g in sorted(R, key=lambda x: -max(x[1][p][0] for p in LIM))[:40]:
    b = max(LIM, key=lambda p: g[p][0])
    print(f"{n} | {noms.get(n, '')[:60]} | " + " | ".join(f"{g[p][0]:.0f} ({g[p][1]})" for p in LIM) + f" | {b}")
# 2) conditions de marché, limite +5 c, 20 meilleures stratégies
print("\n=== 2) GAIN PAR CONDITION DE MARCHÉ (limite +5 c, 20 meilleures) ===")
top = [n for n, g in sorted(R, key=lambda x: -x[1]["5c"][0])[:20]]
for n in top:
    A = collections.defaultdict(lambda: [0.0, 0])
    for t in T["5c"]:
        if t["num"] != n: continue
        c = C.get(t["endTs"] // 1000 - 300)
        if not c: continue
        for k in (f"agit {cls(c[0], qv)}", f"tend {cls(c[1], qt)}", c[2], c[3]): A[k][0] += t["pnl"]; A[k][1] += 1
    print(f"n° {n} {noms.get(n, '')[:50]} :: " + " ; ".join(f"{k} {v[0]:.0f} ({v[1]})" for k, v in sorted(A.items())))
print("\nFIN")
