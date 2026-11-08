# 08.11.2026 (Pitch : « il est bon ? » @niulai4) : lecture seule des données publiques Polymarket de ce compte.
import json, urllib.request, collections, datetime as dt, statistics as st
def get(u):
    with urllib.request.urlopen(urllib.request.Request(u, headers={"user-agent": "Mozilla/5.0"}), timeout=60) as r: return json.load(r)
import re, sys, traceback
W = None
try:
    s = get("https://gamma-api.polymarket.com/public-search?q=niulai4&search_profiles=true")
    P = [p for p in s.get("profiles", []) if (p.get("name") or "").lower() == "niulai4"] or s.get("profiles", [])
    print("profils :", [(p.get("name"), p.get("proxyWallet")) for p in s.get("profiles", [])][:5]); W = P[0]["proxyWallet"]
except Exception as e: print("recherche", repr(e))
if not W:
    try:
        h = urllib.request.urlopen(urllib.request.Request("https://polymarket.com/@niulai4", headers={"user-agent": "Mozilla/5.0"}), timeout=60).read().decode("utf8", "ignore")
        m = re.findall(r'"proxyWallet":"(0x[0-9a-fA-F]{40})"', h) or re.findall(r'(0x[0-9a-fA-F]{40})', h); print("page :", m[:3]); W = m[0]
    except Exception as e: print("page", repr(e))
print("portefeuille :", W)
if not W: sys.exit(0)
# API v1 retirée le 02.11.2026 → v2 (réponse {data, pagination}, curseur), champs snake_case
def v2(chemin, extra=""):
    out = []; cur = None
    for _ in range(12):
        u = f"https://data-api.polymarket.com/v2/{chemin}?user={W}&limit=1000{extra}" + (f"&cursor={urllib.parse.quote(cur)}" if cur else "")
        try: r = get(u)
        except Exception as e: print(chemin, repr(e)); break
        d = r.get("data", r) if isinstance(r, dict) else r
        out += d; pg = r.get("pagination", {}) if isinstance(r, dict) else {}
        cur = pg.get("cursor") or pg.get("next_cursor")
        if not d or not cur or not pg.get("has_more", True): break
    return out
import urllib.parse
def c(o):
    for k, v in list(o.items()):
        cc = re.sub(r"_([a-z])", lambda m: m.group(1).upper(), k); o.setdefault(cc, v)
    o.setdefault("usdcSize", o.get("usdc_size")); o.setdefault("conditionId", o.get("condition_id")); return o
A = [c(a) for a in v2("activity")]
F = [c(a) for a in v2("positions", "&status=CLOSED")]
if F:
    pn = [float(x.get("realizedPnl") or x.get("realized_pnl") or x.get("totalPnl") or x.get("total_pnl") or 0) for x in F]
    print(f"positions fermées lues : {len(F)}, gain réalisé total {sum(pn):+.0f} $, gagnantes {sum(p>0 for p in pn)}")
    jours = collections.defaultdict(float)
    for x, p in zip(F, pn):
        e = x.get("endDate") or x.get("end_date") or ""
        jours[str(e)[:10]] += p
    print("gain réalisé par jour de fin du marché :"); [print(" ", j, f"{v:+.0f}") for j, v in sorted(jours.items())[-25:]]
if not A: sys.exit(0)
# 08.11.2026 (Pitch : « je veux un truc comme lui ») : rétro-ingénierie de ses achats — à chaque achat : secondes restantes, écart du BTC
# depuis le début du cycle (Binance 1 s), côté acheté (celui qui mène ?), prix payé ; résultat par réglement approximé Binance (fin vs début).
T = [a for a in A if a["type"] == "TRADE" and a.get("slug", "").startswith("btc-updown-5m-")]
for a in T[:3]: print("EXEMPLE", json.dumps({k: v for k, v in a.items() if not isinstance(v, (dict, list))}, default=str)[:900])
print("outcomes :", collections.Counter((a.get("outcome"), a.get("outcome_index"), a.get("outcomeIndex")) for a in T).most_common(6))
ts = lambda a: int(a["timestamp"] if isinstance(a["timestamp"], (int, float)) else dt.datetime.fromisoformat(str(a["timestamp"]).replace("Z", "+00:00")).timestamp())
t0, t1 = min(ts(a) for a in T) - 400, max(ts(a) for a in T) + 400
PX = {}; deb = t0 * 1000
while deb < t1 * 1000:
    try: k = get(f"https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=1s&limit=1000&startTime={deb}")
    except Exception as e: print("binance", repr(e)); break
    if not k: break
    for x in k: PX[x[0] // 1000] = (float(x[1]), float(x[4]))
    deb = k[-1][0] + 1000
print("secondes BTC lues :", len(PX))
def px(t, ouv=False):
    for d in range(0, 5):
        if t - d in PX: return PX[t - d][0 if ouv else 1]
    return None
# résultat officiel : gamma-api (outcomePrices) par lots de slugs
RES = {}
sl = sorted({a["slug"] for a in T})
for i in range(0, len(sl), 40):
    try:
        q = "&".join("slug=" + x for x in sl[i:i + 40])
        for m in get("https://gamma-api.polymarket.com/markets?closed=true&limit=100&" + q):
            op = json.loads(m.get("outcomePrices") or "[]")
            if len(op) == 2 and max(map(float, op)) > 0.99: RES[m["slug"]] = float(op[0]) > 0.99   # True = Up gagne
    except Exception as e: print("gamma", repr(e)); break
print("marchés réglés lus :", len(RES), "/", len(sl))
R = []
for a in T:
    debut = int(a["slug"].rsplit("-", 1)[1]); t = ts(a)
    p0, pt, pf = px(debut, True), px(t), px(debut + 299)
    if not (p0 and pt and pf): continue
    up = (a.get("outcome") or "").lower().startswith("up") or str(a.get("outcomeIndex", a.get("outcome_index"))) == "0"
    if a["slug"] not in RES: continue
    d = 1e4 * (pt - p0) / p0; gagne = RES[a["slug"]] == up; acc = (pf >= p0) == RES[a["slug"]]
    R.append(dict(sec=300 - (t - debut), d=d if up else -d, prix=a["price"], usd=a["usdcSize"], gagne=gagne, pnl=(a["usdcSize"] / a["price"] if gagne else 0) - a["usdcSize"], acc=acc))
print("achats analysés :", len(R), "; côté qui mène au moment de l'achat :", f"{100*sum(r['d']>0 for r in R)/len(R):.0f} %")
print("Binance donne le bon gagnant :", f"{100*sum(r['acc'] for r in R)/len(R):.0f} %")
print("résultat (règlement officiel Polymarket) :", f"{sum(r['pnl'] for r in R):+.0f} $ sur {sum(r['usd'] for r in R):.0f} $ misés, gagnés {100*sum(r['gagne'] for r in R)/len(R):.0f} %")
def tab(nom, f, cles):
    print(f"\n=== par {nom} : achats / gagnés % / prix médian / gain par 1 $ ===")
    for c_ in cles:
        X = [r for r in R if f(r) == c_]
        if X: print(c_, "|", len(X), f"| {100*sum(r['gagne'] for r in X)/len(X):.0f} %", f"| {st.median(r['prix'] for r in X):.2f}", f"| {sum(r['pnl'] for r in X)/sum(r['usd'] for r in X):+.3f}")
tab("secondes restantes", lambda r: "≤10" if r["sec"] <= 10 else "11-30" if r["sec"] <= 30 else "31-45" if r["sec"] <= 45 else "46-60" if r["sec"] <= 60 else ">60", ["≤10", "11-30", "31-45", "46-60", ">60"])
tab("avance du côté acheté (pb)", lambda r: "contre" if r["d"] < 0 else "0-2" if r["d"] < 2 else "2-5" if r["d"] < 5 else "5-10" if r["d"] < 10 else "10-20" if r["d"] < 20 else ">20", ["contre", "0-2", "2-5", "5-10", "10-20", ">20"])
tab("prix payé", lambda r: "<0,15" if r["prix"] < .15 else "0,15-0,50" if r["prix"] < .5 else "0,50-0,80" if r["prix"] < .8 else "0,80-0,90" if r["prix"] < .9 else "0,90-0,95" if r["prix"] < .95 else ">=0,95", ["<0,15", "0,15-0,50", "0,50-0,80", "0,80-0,90", "0,90-0,95", ">=0,95"])
print("\n=== prix médian payé selon avance (pb) × secondes restantes (achats) ===")
for dd in ["contre", "0-2", "2-5", "5-10", "10-20", ">20"]:
    lig = []
    for ss in ["≤10", "11-30", "31-45", "46-60"]:
        X = [r for r in R if ("contre" if r["d"] < 0 else "0-2" if r["d"] < 2 else "2-5" if r["d"] < 5 else "5-10" if r["d"] < 10 else "10-20" if r["d"] < 20 else ">20") == dd and ("≤10" if r["sec"] <= 10 else "11-30" if r["sec"] <= 30 else "31-45" if r["sec"] <= 45 else "46-60" if r["sec"] <= 60 else ">60") == ss]
        lig.append(f"{len(X)}x {st.median(r['prix'] for r in X):.2f} {100*sum(r['gagne'] for r in X)/len(X):.0f}% {sum(r['pnl'] for r in X)/sum(r['usd'] for r in X):+.2f}" if X else "—")
    print(dd, "|", " | ".join(lig))
sys.exit(0)
