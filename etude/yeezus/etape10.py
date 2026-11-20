# Étape 10 v2 : précision = part des tokens achetés par un wallet qui ont été appelés par le canal
import json, urllib.request, time, collections, sys, threading, queue
H = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36", "accept": "application/json", "referer": "https://gmgn.ai/"}
def get(u):
    for k in range(6):
        try: return json.loads(urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=40).read())
        except Exception as e:
            if "429" in str(e): time.sleep(5*(k+1)); continue
            return {}
    return {}
D = json.load(open(sys.argv[1])); TC = json.load(open("etude/yeezus/traders_complet.json")); CALLED = set(TC)
early = collections.defaultdict(set); pre = collections.defaultdict(set)
for m, v in D.items():
    tr = v["trades"]
    if not tr: continue
    t0 = tr[0][5]
    for x in tr:
        if x[1] != "buy" or x[5] > v["tc"]: continue
        pre[x[0]].add(m)
        if x[5] <= t0 + 120: early[x[0]].add(m)
cand = [a for a, s in sorted(early.items(), key=lambda x: -len(x[1])) if len(s) >= 4][:45]
cand += [a for a, s in sorted(pre.items(), key=lambda x: -len(x[1])) if len(s) >= 8][:45]
cand = list(dict.fromkeys(cand)); print("candidats", len(cand), flush=True)
q = queue.Queue(); [q.put(a) for a in cand]; RES = {}; lock = threading.Lock()
def work():
    while True:
        try: a = q.get_nowait()
        except queue.Empty: return
        toks = set(); cur = None; tmin = tmax = None; n = 0
        for p in range(30):
            j = get(f"https://gmgn.ai/vas/api/v1/wallet_activity/sol?wallet={a}&limit=50&type=buy" + (f"&cursor={cur}" if cur else ""))
            d = j.get("data") or {}; L = d.get("activities") or []
            for x in L:
                if x.get("event_type") != "buy": continue
                t = (x.get("token") or {}).get("address")
                if t: toks.add(t); n += 1
                ts = x.get("timestamp") or 0; tmin = min(tmin or ts, ts); tmax = max(tmax or ts, ts)
            cur = d.get("next")
            if not cur or not L: break
            time.sleep(0.4)
        hit = toks & CALLED
        with lock:
            RES[a] = {"early": len(early.get(a, ())), "pre": len(pre.get(a, ())), "tokens": len(toks), "appeles": len(hit), "de": tmin, "a": tmax}
            print(f"{a} | 1ers acheteurs {len(early.get(a,()))} calls, avant post {len(pre.get(a,()))} calls | tokens achetés vus {len(toks)} | appelés {len(hit)} = {100*len(hit)/max(len(toks),1):.1f} %", flush=True)
th = [threading.Thread(target=work) for _ in range(5)]; [t.start() for t in th]; [t.join() for t in th]
print("\nCLASSEMENT PAR PRÉCISION (>=3 tokens appelés)")
for a, r in sorted(RES.items(), key=lambda x: -x[1]["appeles"] / max(x[1]["tokens"], 1)):
    if r["appeles"] >= 3: print(f"  {a} {r['appeles']}/{r['tokens']} = {100*r['appeles']/r['tokens']:.1f} % | avant post sur {r['pre']} calls | période {time.strftime('%Y-%m-%d', time.gmtime(r['de'] or 0))} -> {time.strftime('%Y-%m-%d', time.gmtime(r['a'] or 0))}")
json.dump(RES, open("etude/yeezus/resultat10.json", "w"))
