# 08.11.2026 20 h 38 (Pitch : « go » — concours des détecteurs de marché rapide / lent). Lecture seule, données publiques.
# Pour chaque détecteur (mesuré AVANT le début du cycle) : ligne « tous les trades de la RAPIDE quand rapide, tous ceux de la LENTE quand lent ».
# Paires testées : (rapide 2171, lente 2172) et (rapide 12112, lente 2172). Jugé aussi sur les 2 premiers jours vs les 2 derniers (stabilité).
import json, urllib.request, collections, datetime as dt, statistics as st, math
from zoneinfo import ZoneInfo
PZ = ZoneInfo("Europe/Paris")
def get(u, h={"user-agent": "analyse"}):
    with urllib.request.urlopen(urllib.request.Request(u, headers=h), timeout=120) as r: return json.load(r)
dep = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=95)).strftime("%Y-%m-%dT%H:%M:%SZ")
T = get("https://72-11-157-70.sslip.io/api/bot/banc/trades?depuis=" + dep)["trades"]
P = collections.defaultdict(list)
for t in T:
    if t["num"] in (2171, 2172, 12112): P[t["num"]].append(t)
print("trades lus :", len(T), "; 2171/2172/12112 :", {k: len(v) for k, v in P.items()})
t0 = min(t["endTs"] for t in T) // 1000 - 6 * 3600; t1 = max(t["endTs"] for t in T) // 1000
K = []; deb = t0 * 1000
while deb < t1 * 1000:
    k = get(f"https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=1m&limit=1000&startTime={deb}")
    if not k: break
    K += [(x[0] // 1000, float(x[1]), float(x[2]), float(x[3]), float(x[4]), float(x[5]), int(x[8])) for x in k]; deb = k[-1][0] + 60000
I = {x[0]: i for i, x in enumerate(K)}
DV = {}
try:
    d = get(f"https://www.deribit.com/api/v2/public/get_volatility_index_data?currency=BTC&start_timestamp={t0*1000}&end_timestamp={t1*1000}&resolution=60")
    for x in d["result"]["data"]: DV[x[0] // 1000] = x[4]
    print("DVOL minutes :", len(DV))
except Exception as e: print("deribit", repr(e))
def r1(i, n): return [math.log(K[j][4] / K[j - 1][4]) for j in range(i - n + 1, i + 1)]
def feat(debut):
    i = I.get(debut - 60)
    if i is None or i < 360: return None
    f = {}
    f["agit 1 h (actuel)"] = 1e4 * st.pstdev([math.log(K[j][4] / K[j - 5][4]) for j in range(i - 55, i + 1, 5)])
    f["tendance 1 h"] = abs(1e4 * math.log(K[i][4] / K[i - 60][4]))
    for w in (2, 3, 5, 10, 15, 20, 30, 45):   # 08.11 20 h 47 (Pitch : « efficacité sur d'autres périodes, de 1 à 45 min ? »)
        m = r1(i, w); f[f"efficacité {w:02d} min"] = abs(sum(m)) / max(1e-12, sum(abs(x) for x in m))
    f["vol 15 min / vol 2 h"] = st.pstdev(r1(i, 15)) / max(1e-12, st.pstdev(r1(i, 120)))
    f["vol 15 min"] = 1e4 * st.pstdev(r1(i, 15))
    f["volume 15 min / 6 h"] = sum(K[j][5] for j in range(i - 14, i + 1)) / 15 / max(1e-9, sum(K[j][5] for j in range(i - 359, i + 1)) / 360)
    f["nb échanges 15 min"] = sum(K[j][6] for j in range(i - 14, i + 1))
    dv = [DV[k] for k in range(debut - 600, debut, 60) if k in DV]
    if dv: f["DVOL Deribit"] = dv[-1]
    h = dt.datetime.fromtimestamp(debut, PZ); f["agenda (semaine 14-22 h)"] = 1.0 if h.weekday() < 5 and 14 <= h.hour < 22 else 0.0
    return f
debuts = sorted({t["endTs"] // 1000 - 300 for t in T})
F = {d: feat(d) for d in debuts}
noms = sorted({k for f in F.values() if f for k in f})
def courbe(L):
    L = sorted(L, key=lambda t: t["endTs"]); cum = pic = cr = 0
    for t in L: cum += t["pnl"]; pic = max(pic, cum); cr = max(cr, pic - cum)
    return cum, cr, len(L)
milieu = debuts[len(debuts) // 2]
def evalue(rap, lent, choix):
    L = [t for t in P[rap] if choix(t["endTs"] // 1000 - 300) is True] + [t for t in P[lent] if choix(t["endTs"] // 1000 - 300) is False]
    g, cr, n = courbe(L); a = sum(t["pnl"] for t in L if t["endTs"] // 1000 - 300 < milieu); b = g - a
    return g, cr, n, a, b
# « suivre la gagnante » : celle qui a le plus gagné sur les 2 h réglées avant le cycle
def suiveur(rap, lent):
    def c(d):
        s = lambda n: sum(t["pnl"] for t in P[n] if d - 7200 <= t["endTs"] // 1000 <= d)
        return s(rap) >= s(lent)
    return c
for rap, lent in [(2171, 2172), (12112, 2172)]:
    print(f"\n######## rapide = {rap}, lente = {lent}  — gain total | creux | trades | 1re moitié | 2e moitié")
    for nom, ch in [(f"toujours {rap}", lambda d: True), (f"toujours {lent}", lambda d: False), ("suivre la gagnante 2 h", suiveur(rap, lent))]:
        g, cr, n, a, b = evalue(rap, lent, ch); print(f"{nom:34s} | {g:+7.0f} | -{cr:5.0f} | {n:4d} | {a:+7.0f} | {b:+7.0f}")
    for k in [x for x in noms if x.startswith("efficacité") or x.startswith("agit")]:
        vals = sorted(f[k] for f in F.values() if f and k in f)
        if not vals: continue
        seuils = sorted({vals[int(len(vals) * q)] for q in (0.2, 0.35, 0.5, 0.65, 0.8)}) if k != "agenda (semaine 14-22 h)" else [0.5]
        if k == "agit 1 h (actuel)": seuils = sorted(set(seuils + [5.0]))
        if k == "tendance 1 h": seuils = sorted(set(seuils + [13.8]))
        for s_ in seuils:
            ch = lambda d, k=k, s_=s_: (None if not F.get(d) or k not in F[d] else F[d][k] >= s_)
            g, cr, n, a, b = evalue(rap, lent, ch)
            print(f"{k + ' ≥ ' + format(s_, '.3g'):34s} | {g:+7.0f} | -{cr:5.0f} | {n:4d} | {a:+7.0f} | {b:+7.0f}")
