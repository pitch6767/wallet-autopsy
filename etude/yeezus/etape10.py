# Étape 10 : créateurs + premiers acheteurs des tokens appelés, et taux de "tokens appelés" dans leur activité
import json, urllib.request, time, collections, sys, datetime as dt
H = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36", "accept": "application/json", "referer": "https://gmgn.ai/"}
def get(u):
    for k in range(6):
        try: return json.loads(urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=40).read())
        except Exception as e:
            if "429" in str(e): time.sleep(5*(k+1)); continue
            return {"_err": str(e)[:80]}
    return {"_err": "429"}
D = json.load(open(sys.argv[1])); TC = json.load(open("etude/yeezus/traders_complet.json"))
CALLED = set(TC)
# 1) créateur via gmgn (sonde de plusieurs endpoints sur 1 token, puis tous)
m0 = next(iter(TC))
for u in [f"https://gmgn.ai/api/v1/token_info/sol/{m0}", f"https://gmgn.ai/vas/api/v1/token_info/sol/{m0}", f"https://gmgn.ai/api/v1/token_dev_info/sol/{m0}", f"https://gmgn.ai/vas/api/v1/token_dev_info/sol/{m0}", f"https://gmgn.ai/api/v1/token_launchpad_info/sol/{m0}"]:
    j = get(u); print("SONDE", u.split("gmgn.ai")[1][:40], json.dumps(j)[:400])
def creator(m):
    for u in [f"https://gmgn.ai/api/v1/token_info/sol/{m}", f"https://gmgn.ai/vas/api/v1/token_dev_info/sol/{m}", f"https://gmgn.ai/api/v1/token_dev_info/sol/{m}"]:
        j = get(u); s = json.dumps(j.get("data") or {})
        d = j.get("data") or {}
        if isinstance(d, dict):
            for k in ("creator", "creator_address", "dev", "dev_address", "creator_wallet"):
                v = d.get(k) or (d.get("dev") or {}).get(k) if isinstance(d.get("dev"), dict) else d.get(k)
                if isinstance(v, str) and len(v) > 30: return v
    return None
CR = {}
for m in TC:
    CR[m] = creator(m); time.sleep(0.6)
c = collections.Counter(v for v in CR.values() if v)
print("\nCREATEURS trouvés", sum(1 for v in CR.values() if v), "/", len(TC), "| répétés:", [(k, n) for k, n in c.most_common(10) if n > 1])
# 2) premiers acheteurs (120 premières secondes) des tokens appelés
early = collections.defaultdict(set); dev_guess = {}
for m, v in D.items():
    tr = v["trades"]
    if not tr: continue
    t0 = tr[0][5]; dev_guess[m] = tr[0][0]
    for x in tr:
        if x[5] > t0 + 120: break
        if x[1] == "buy": early[x[0]].add(m)
cg = collections.Counter(dev_guess.values())
print("1er acheteur (dev probable) répété:", [(k, n) for k, n in cg.most_common(10) if n > 1])
E = sorted(early.items(), key=lambda x: -len(x[1]))
print("\nPREMIERS ACHETEURS (<=120 s après création) répétés sur les calls :")
for a, ms in E[:15]: print("  ", a, len(ms), "/", len(D))
# 3) précision : part des tokens tradés par le wallet qui ont été appelés
cand = [a for a, ms in E if len(ms) >= 3][:40] + [k for k, n in c.most_common(10) if n > 1]
print("\nPRÉCISION des candidats (tokens récents du wallet appelés par le canal) :")
RES = []
for a in dict.fromkeys(cand):
    toks = set(); cur = None
    for p in range(6):
        j = get(f"https://gmgn.ai/vas/api/v1/wallet_holdings/sol/{a}?limit=50&orderby=last_active_timestamp&direction=desc&showsmall=true&sellout=true&hide_abnormal=false" + (f"&cursor={cur}" if cur else ""))
        d = (j or {}).get("data") or {}; L = d.get("holdings") or d.get("list") or []
        for h in L:
            t = h.get("token") or {}
            ad = t.get("address") if isinstance(t, dict) else h.get("token_address") or h.get("address")
            if ad: toks.add(ad)
        cur = d.get("next")
        if not cur or not L: break
        time.sleep(0.5)
    hit = toks & CALLED
    RES.append((a, len(early.get(a, ())), len(toks), len(hit)))
    print(f"  {a} premiers-acheteurs sur {len(early.get(a, ()))} calls | tokens récents vus {len(toks)} | dont appelés {len(hit)} ({100*len(hit)/max(len(toks),1):.0f} %)", flush=True)
json.dump({"createurs": CR, "precision": RES, "early": {a: sorted(ms) for a, ms in E[:200]}}, open("etude/yeezus/resultat10.json", "w"))
