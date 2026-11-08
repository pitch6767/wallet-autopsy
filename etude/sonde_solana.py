# 08.11.2026 (Pitch : « il est bon ? » @niulai4) : lecture seule des données publiques Polymarket de ce compte.
import json, urllib.request, collections, datetime as dt, statistics as st
def get(u):
    with urllib.request.urlopen(urllib.request.Request(u, headers={"user-agent": "Mozilla/5.0"}), timeout=60) as r: return json.load(r)
s = get("https://gamma-api.polymarket.com/public-search?q=niulai4&search_profiles=true")
P = [p for p in s.get("profiles", []) if (p.get("name") or "").lower() == "niulai4" or (p.get("pseudonym") or "").lower() == "niulai4"] or s.get("profiles", [])
print("profils :", [(p.get("name"), p.get("proxyWallet")) for p in s.get("profiles", [])][:5])
W = P[0]["proxyWallet"]; print("portefeuille :", W)
# courbe de gain par jour
for iv in ["all"]:
    try:
        c = get(f"https://user-pnl-api.polymarket.com/user-pnl?user_address={W}&interval={iv}&fidelity=1d")
        print("\n=== gain cumulé par jour ===")
        prev = None
        for x in c:
            d = dt.datetime.utcfromtimestamp(x["t"]).strftime("%m-%d"); v = x["p"]
            print(d, f"{v:+.0f}", "" if prev is None else f"(jour {v-prev:+.0f})"); prev = v
    except Exception as e: print("pnl", e)
# activité récente : trades + rachats
A = []; off = 0
while off < 3000:
    try: r = get(f"https://data-api.polymarket.com/activity?user={W}&limit=500&offset={off}")
    except Exception as e: print("activité", e); break
    if not r: break
    A += r; off += 500
print("\nactivités lues :", len(A), "de", dt.datetime.utcfromtimestamp(min(a["timestamp"] for a in A)), "à", dt.datetime.utcfromtimestamp(max(a["timestamp"] for a in A)))
print(collections.Counter(a["type"] for a in A))
T = [a for a in A if a["type"] == "TRADE"]
print("marchés :", collections.Counter(("BTC" if "Bitcoin" in a.get("title", "") else a.get("title", "")[:30]) + (" 5m" if "-5m-" in a.get("slug", "") or ":" in a.get("title", "") else "") for a in T).most_common(6))
print("côtés :", collections.Counter(a["side"] for a in T))
pr = [a["price"] for a in T if a["side"] == "BUY"]
print("prix d'achat : médiane", st.median(pr), "; tranches", collections.Counter("<0,05" if p < .05 else "0,05-0,15" if p < .15 else "0,15-0,40" if p < .4 else "0,40-0,70" if p < .7 else "0,70-0,90" if p < .9 else ">=0,90" for p in pr))
us = [a["usdcSize"] for a in T]
print("taille des trades $ : médiane", round(st.median(us), 2), "moyenne", round(st.mean(us), 2), "max", round(max(us), 2), "; total", round(sum(us)))
# moment dans le cycle (slug btc-updown-5m-<debut>)
sec = []
for a in T:
    sl = a.get("slug", "")
    if sl.startswith("btc-updown-5m-"):
        try: sec.append(a["timestamp"] - int(sl.rsplit("-", 1)[1]))
        except: pass
if sec: print("seconde du cycle à l'achat :", collections.Counter("0-60" if x < 60 else "60-180" if x < 180 else "180-240" if x < 240 else "240-270" if x < 270 else "270-300" if x < 300 else "après" for x in sec))
# résultat par marché sur la période lue (achats - ventes + rachats)
M = collections.defaultdict(float)
for a in A:
    k = a.get("conditionId")
    if a["type"] == "TRADE": M[k] += (-a["usdcSize"] if a["side"] == "BUY" else a["usdcSize"])
    elif a["type"] in ("REDEEM", "MERGE"): M[k] += a["usdcSize"]
    elif a["type"] == "REWARD": M["reward"] += a["usdcSize"]
v = [x for k, x in M.items() if k != "reward"]
print(f"\nsur la période lue : {len(v)} marchés, résultat {sum(v):+.0f} $ (marchés encore ouverts comptés à 0), gagnants {sum(x>0 for x in v)}, rewards {M['reward']:.0f}")
