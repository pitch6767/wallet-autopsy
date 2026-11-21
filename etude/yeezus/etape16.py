# Étape 16 : quelle règle de revente aurait le plus rapporté sur les calls du réseau ? (bougies 5 min, 10 jours après l'achat)
import json, urllib.request, time, statistics as st
H = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36", "accept": "application/json", "referer": "https://gmgn.ai/"}
def get(u):
    for k in range(6):
        try: return json.loads(urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=40).read())
        except Exception as e:
            if "429" in str(e): time.sleep(5*(k+1)); continue
            return {}
    return {}
R = json.load(open("etude/yeezus/resultat15.json"))
calls = {}
for res, tr in R.items():
    for t in tr:
        for l in t["calls"]:
            if l["mint"] not in calls or l["achat_date"] < calls[l["mint"]]["achat_date"]: calls[l["mint"]] = l
now = int(time.time()); D = []
for m, l in calls.items():
    t0 = int(time.mktime(time.strptime(l["achat_date"], "%Y-%m-%d %H:%M")))
    j = get(f"https://gmgn.ai/api/v1/token_kline/sol/{m}?resolution=5m&from={t0-300}&to={min(now, t0+10*86400)}")
    L = (j.get("data") or {}).get("list") or []
    c = sorted([(int(x["time"]) // 1000, float(x["high"]), float(x["low"]), float(x["close"])) for x in L if int(x["time"]) // 1000 >= t0 - 300])
    if c: D.append((l, c))
    time.sleep(0.6)
print("calls avec bougies:", len(D), "/", len(calls))
def sim(regle, l, c):
    p0 = l["prix_achat"]; reste = 1.0; gain = 0.0; mx = p0
    for ts, h, lo, cl in c:
        # ordre prudent dans la bougie : d'abord le stop (bas), puis les objectifs (haut)
        for kind, a, part in regle:
            if reste <= 1e-9: break
            if kind == "stop" and lo <= p0 * a: gain += reste * a; reste = 0
            if kind == "suiveur" and mx >= p0 * part and lo <= mx * (1 - a): gain += reste * mx * (1 - a) / p0; reste = 0
        if reste <= 1e-9: break
        for kind, a, part in regle:
            if kind == "tp" and h >= p0 * a and not getattr(sim, "_x", None):
                pass
        mx = max(mx, h)
        for i, (kind, a, part) in enumerate(regle):
            if kind == "tp" and reste > 1e-9 and h >= p0 * a and ("tp", a) not in fait: q = min(part, reste); gain += q * a; reste -= q; fait.add(("tp", a))
    gain += reste * (c[-1][3] / p0)   # le reste est vendu au dernier prix (10 jours ou maintenant)
    return gain
REGLES = {
 "leur vente réelle": None,
 "tout à x2": [("tp", 2, 1)], "tout à x3": [("tp", 3, 1)], "tout à x5": [("tp", 5, 1)],
 "x2 + stop -50 %": [("stop", 0.5, 0), ("tp", 2, 1)],
 "moitié à x2, reste suiveur -40 %": [("tp", 2, 0.5), ("suiveur", 0.4, 2)],
 "moitié à x2, reste suiveur -50 %": [("tp", 2, 0.5), ("suiveur", 0.5, 2)],
 "1/3 x2, 1/3 x4, 1/3 suiveur -50 %": [("tp", 2, 1/3), ("tp", 4, 1/3), ("suiveur", 0.5, 4)],
 "mise récupérée à x2 (moitié), reste à x10": [("tp", 2, 0.5), ("tp", 10, 0.5)],
 "suiveur -30 % dès x1,5": [("suiveur", 0.3, 1.5)], "suiveur -50 % dès x2": [("suiveur", 0.5, 2)],
 "moitié x2 + stop -50 %, reste suiveur -50 %": [("stop", 0.5, 0), ("tp", 2, 0.5), ("suiveur", 0.5, 2)],
}
print("\nmise égale de 100 $ par call, entrée au prix d'achat du réseau")
res = []
for nom, r in REGLES.items():
    out = []
    for l, c in D:
        if r is None: out.append(l["prix_vente"] / l["prix_achat"] if l["prix_vente"] else c[-1][3] / l["prix_achat"])
        else: fait = set(); globals()["fait"] = fait; out.append(sim(r, l, c))
    tot = sum(out) * 100; mise = 100 * len(out)
    res.append((tot / mise, nom, tot - mise, sum(o > 1 for o in out), st.median(out)))
for m_, nom, g, w, med in sorted(res, reverse=True):
    print(f"{nom:45} | rendu x{m_:.2f} | gain {g:+,.0f} $ pour {100*len(D):,} $ misés | gagnants {w}/{len(D)} | médiane x{med:.2f}")
# même chose seulement sur les calls achetés AVANT le post
print("\nseulement les calls achetés AVANT le post :")
D2 = [(l, c) for l, c in D if l["minutes_avant_call"] > 0]
for nom, r in REGLES.items():
    out = []
    for l, c in D2:
        if r is None: out.append(l["prix_vente"] / l["prix_achat"] if l["prix_vente"] else c[-1][3] / l["prix_achat"])
        else: fait = set(); globals()["fait"] = fait; out.append(sim(r, l, c))
    print(f"{nom:45} | rendu x{sum(out)/len(out):.2f} | gagnants {sum(o>1 for o in out)}/{len(out)}")
