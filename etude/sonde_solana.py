# 08.11.2026 (Pitch : comptes Polymarket @dangerously-skip-permissions, @norm1e69 et le système « Vortex + CHOP ») — lecture seule, données publiques.
import json, urllib.request, urllib.parse, collections, datetime as dt, statistics as st, re, sys, math
def get(u):
    with urllib.request.urlopen(urllib.request.Request(u, headers={"user-agent": "Mozilla/5.0"}), timeout=60) as r: return json.load(r)
def v2(W, chemin, extra="", pages=6):
    out = []; cur = None
    for _ in range(pages):
        u = f"https://data-api.polymarket.com/v2/{chemin}?user={W}&limit=1000{extra}" + (f"&cursor={urllib.parse.quote(cur)}" if cur else "")
        try: r = get(u)
        except Exception as e: print(chemin, repr(e)); break
        d = r.get("data", r) if isinstance(r, dict) else r
        out += d; pg = r.get("pagination", {}) if isinstance(r, dict) else {}
        cur = pg.get("next_cursor") or pg.get("cursor")
        if not d or not cur: break
    return out
def wallet(nom):
    try:
        s = get("https://gamma-api.polymarket.com/public-search?q=" + urllib.parse.quote(nom) + "&search_profiles=true")
        P = [p for p in s.get("profiles", []) if (p.get("name") or "").lower() == nom.lower()] or s.get("profiles", [])
        print("profils trouvés :", [(p.get("name"), p.get("proxyWallet")) for p in s.get("profiles", [])][:4]); return P[0]["proxyWallet"] if P else None
    except Exception as e: print("recherche", repr(e)); return None
for nom in ["dangerously-skip-permissions", "norm1e69"]:
    print(f"\n################ @{nom}")
    W = wallet(nom); print("portefeuille :", W)
    if not W: continue
    A = v2(W, "activity")
    if not A: print("aucune activité"); continue
    ts = lambda a: int(a["timestamp"])
    print("activités lues :", len(A), "du", dt.datetime.utcfromtimestamp(min(map(ts, A))), "au", dt.datetime.utcfromtimestamp(max(map(ts, A))))
    print("types :", collections.Counter(a["type"] for a in A))
    T = [a for a in A if a["type"] == "TRADE"]
    print("marchés :", collections.Counter(re.sub(r"\d+", "#", a.get("slug", ""))[:30] for a in T).most_common(6))
    print("côtés :", collections.Counter(a["side"] for a in T), "; issues :", collections.Counter(a.get("outcome") for a in T).most_common(4))
    if T:
        print("prix : médiane", st.median(a["price"] for a in T), "; tailles $ : médiane", round(st.median(a["usdc_size"] for a in T), 2), "moyenne", round(st.mean(a["usdc_size"] for a in T), 2), "max", round(max(a["usdc_size"] for a in T)), "; total", round(sum(a["usdc_size"] for a in T)))
        sec = [ts(a) - int(a["slug"].rsplit("-", 1)[1]) for a in T if re.match(r"btc-updown-(5|15)m-\d+$", a.get("slug", ""))]
        if sec: print("seconde du cycle :", collections.Counter("0-30" if x < 30 else "30-120" if x < 120 else "120-240" if x < 240 else "240-300" if x < 300 else ">300" for x in sec))
    M = collections.defaultdict(float); rew = collections.Counter()
    for a in A:
        k = a.get("condition_id")
        if a["type"] == "TRADE": M[k] += (-a["usdc_size"] if a["side"] == "BUY" else a["usdc_size"])
        elif a["type"] in ("REDEEM", "MERGE", "CONVERSION"): M[k] += a["usdc_size"]
        else: rew[a["type"]] += a["usdc_size"]
    v = list(M.values())
    print(f"résultat sur la période lue : {sum(v):+.0f} $ sur {len(v)} marchés (marchés non rachetés comptés perdus), autres flux {dict(rew)}")
    jours = collections.defaultdict(float)
    for a in A:
        j = dt.datetime.utcfromtimestamp(ts(a)).strftime("%m-%d")
        if a["type"] == "TRADE": jours[j] += (-a["usdc_size"] if a["side"] == "BUY" else a["usdc_size"])
        elif a["type"] in ("REDEEM", "MERGE", "CONVERSION"): jours[j] += a["usdc_size"]
    print("flux par jour (achats − ventes − rachats, approximatif) :", {j: round(x) for j, x in sorted(jours.items())})

# Vortex + CHOP sur BTC : la direction du cycle 5 min suivant est-elle prévisible ? (bougies 1 min Binance, 30 jours)
print("\n################ Vortex + CHOP sur BTC 1 min, 30 jours, prédit le cycle 5 min suivant")
K = []; deb = int((dt.datetime.utcnow() - dt.timedelta(days=30)).timestamp() * 1000)
while True:
    k = get(f"https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=1m&limit=1000&startTime={deb}")
    if not k: break
    K += [(x[0] // 1000, float(x[1]), float(x[2]), float(x[3]), float(x[4])) for x in k]; deb = k[-1][0] + 60000
    if len(k) < 1000: break
idx = {x[0]: i for i, x in enumerate(K)}
print("bougies 1 min :", len(K))
for n in (7, 14, 21):
    res = collections.defaultdict(lambda: [0, 0])
    for x in K:
        t = x[0]
        if t % 300: continue   # début de cycle
        i = idx.get(t)
        if i is None or i < n + 1 or i + 4 >= len(K) or K[i + 4][0] != t + 240: continue
        vp = vm = tr = 0.0
        for j in range(i - n, i):
            h, l, pc = K[j][2], K[j][3], K[j - 1][4]
            vp += abs(h - K[j - 1][3]); vm += abs(l - K[j - 1][2]); tr += max(h - l, abs(h - pc), abs(l - pc))
        rng = max(K[j][2] for j in range(i - n, i)) - min(K[j][3] for j in range(i - n, i))
        if tr <= 0 or rng <= 0: continue
        chop = 100 * math.log10(tr / rng) / math.log10(n)
        up = vp > vm; gagne = (K[i + 4][4] >= K[i][1]) == up
        for s in (100, 61.8, 50, 45, 38.2):
            if chop < s: res[s][0] += 1; res[s][1] += gagne
    print(f"n = {n} :", " ; ".join(f"CHOP < {s} : {r[0]} cycles, juste {100*r[1]/r[0]:.1f} %" for s, r in sorted(res.items(), reverse=True) if r[0]))
print("(acheter à ~0,50 avec ~1,75 % de frais : il faut être juste plus de ~51 % du temps pour gagner)")
