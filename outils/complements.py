# 06.11.2026 — Étude H-COMPLÉMENT : stratégies qui gagnent quand la famille 101 + 105 perd (la nuit 00-08 Paris, BTC calme dans l'heure).
# VRAIS trades du banc (signaux reçus, vrai carnet, frais, règlement Polymarket), limite +5 c, 200 $ par cycle. Conditions connues AVANT le cycle.
import json, sys, urllib.request, statistics, collections, datetime as dt, math
VPS, DEP = sys.argv[1], sys.argv[2]
def get(u):
    with urllib.request.urlopen(urllib.request.Request(u, headers={"cache-control": "no-store", "user-agent": "etude"}), timeout=120) as r: return json.load(r)
d = get(f"{VPS}/api/bot/banc/trades?depuis={DEP}&plafond=200"); T = d["trades"]; print("trades", len(T), "depuis", d["depuis"])
t0 = int(dt.datetime.fromisoformat(d["depuis"].replace("Z", "+00:00")).timestamp() * 1000) - 2 * 3600_000; t1 = int(dt.datetime.now(dt.timezone.utc).timestamp() * 1000)
K = {}
while t0 < t1:
    ks = get(f"https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=5m&startTime={t0}&limit=1000")
    if not ks: break
    for k in ks: K[k[0] // 1000] = (float(k[1]), float(k[4]))
    t0 = ks[-1][0] + 300_000
def cond(s):
    prev = [K.get(s - 300 * i) for i in range(1, 13)]
    if any(x is None for x in prev): return None
    tend = abs(prev[0][1] / prev[-1][0] - 1) * 1e4
    h = dt.datetime.fromtimestamp(s, dt.timezone.utc) + dt.timedelta(hours=1)
    return tend, h.hour < 8, h.strftime("%d.%m %Hh")
noms = {}
try:
    for c in get("https://raw.githubusercontent.com/pitch6767/wallet-autopsy/main/bot95/src/catalogue.json"): noms[c["n"]] = c["nom"]
except Exception: pass
S = collections.defaultdict(lambda: {"nuit": [0.0, 0], "calme": [0.0, 0], "nuit_ou_calme": [0.0, 0], "reste": [0.0, 0], "tout": [0.0, 0], "h": collections.defaultdict(float)})
for t in T:
    c = cond(t["endTs"] // 1000 - 300)
    if not c: continue
    z = S[t["num"]]; nc = c[1] or c[0] < 13.8
    for k, ok in (("nuit", c[1]), ("calme", c[0] < 13.8), ("nuit_ou_calme", nc), ("reste", not nc), ("tout", True)):
        if ok: z[k][0] += t["pnl"]; z[k][1] += 1
    z["h"][c[2]] += t["pnl"]
ref = S.get(2112, {}).get("h", {})
H = sorted(set(h for z in S.values() for h in z["h"]))
def corr(a, b):
    x = [a.get(h, 0.0) for h in H]; y = [b.get(h, 0.0) for h in H]
    mx, my = sum(x) / len(x), sum(y) / len(y); sx = math.sqrt(sum((v - mx) ** 2 for v in x)); sy = math.sqrt(sum((v - my) ** 2 for v in y))
    return sum((a2 - mx) * (b2 - my) for a2, b2 in zip(x, y)) / (sx * sy) if sx and sy else 0
print(f"\nheures comparées : {len(H)} ; référence = n° 2112 (portefeuille 101 + 105 + x2 carnet d'accord)")
print("\n=== MEILLEURES LA NUIT OU QUAND LE BTC EST CALME (au moins 12 trades dans ces conditions) ===")
print("n° | stratégie | nuit ou calme | dont nuit | dont calme | autres moments | corrélation horaire avec 2112")
L = [(n, z) for n, z in S.items() if z["nuit_ou_calme"][1] >= 12]
for n, z in sorted(L, key=lambda x: -x[1]["nuit_ou_calme"][0])[:30]:
    print(f"{n} | {noms.get(n, '')[:60]} | {z['nuit_ou_calme'][0]:.0f} ({z['nuit_ou_calme'][1]}) | {z['nuit'][0]:.0f} ({z['nuit'][1]}) | {z['calme'][0]:.0f} ({z['calme'][1]}) | {z['reste'][0]:.0f} ({z['reste'][1]}) | {corr(z['h'], ref):+.2f}")
print("\n=== COMBINAISONS (2112 seulement hors nuit et si le BTC bouge) + (stratégie X seulement la nuit ou quand le BTC est calme) ===")
r2112 = S[2112]["reste"][0]
for n, z in sorted(L, key=lambda x: -x[1]["nuit_ou_calme"][0])[:10]:
    print(f"2112 en tendance ({r2112:.0f}) + {n} nuit/calme ({z['nuit_ou_calme'][0]:.0f}) = {r2112 + z['nuit_ou_calme'][0]:.0f} $  | 2112 tout le temps seule = {S[2112]['tout'][0]:.0f} $")
print("\nFIN")
