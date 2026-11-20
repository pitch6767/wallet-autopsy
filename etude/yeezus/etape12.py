# Étape 12 : pour chaque groupe de wallets (même financeur / relais), précision = part des tokens achetés qui sont des calls
import json, urllib.request, time, threading, queue, collections, statistics as st
H = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36", "accept": "application/json", "referer": "https://gmgn.ai/"}
def get(u):
    for k in range(6):
        try: return json.loads(urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=40).read())
        except Exception as e:
            if "429" in str(e): time.sleep(5*(k+1)); continue
            return {}
    return {}
TC = json.load(open("etude/yeezus/traders_complet.json")); CALLED = set(TC)
G = json.load(open("etude/yeezus/groupes.json"))
av = collections.defaultdict(set)
for c in G:
    for w in c["wallets"]: av[w]
ALL = sorted({w for c in G for w in c["wallets"]})
q = queue.Queue(); [q.put(w) for w in ALL]; ACT = {}; lock = threading.Lock()
def work():
    while True:
        try: w = q.get_nowait()
        except queue.Empty: return
        toks = set(); last = 0; first = None; cur = None
        for p in range(8):
            j = get(f"https://gmgn.ai/vas/api/v1/wallet_activity/sol?wallet={w}&limit=50&type=buy" + (f"&cursor={cur}" if cur else ""))
            d = j.get("data") or {}; L = d.get("activities") or []
            for x in L:
                if x.get("event_type") != "buy": continue
                t = (x.get("token") or {}).get("address"); ts = x.get("timestamp") or 0
                if t: toks.add(t)
                last = max(last, ts); first = min(first or ts, ts)
            cur = d.get("next")
            if not cur or not L: break
            time.sleep(0.3)
        with lock: ACT[w] = {"toks": toks, "last": last, "first": first, "complet": not cur}
th = [threading.Thread(target=work) for _ in range(6)]; [t.start() for t in th]; [t.join() for t in th]
R = []
for c in G:
    toks = set().union(*[ACT[w]["toks"] for w in c["wallets"] if w in ACT])
    hit = toks & CALLED; last = max([ACT[w]["last"] for w in c["wallets"] if w in ACT] or [0])
    actifs = sum(1 for w in c["wallets"] if ACT.get(w, {}).get("toks"))
    na, nb = len(c["calls_avant"]), len(c["calls_apres_seulement"])
    R.append({"racine": c["racine"], "wallets": len(c["wallets"]), "wallets_actifs": actifs, "calls_avant": na, "calls_apres": nb,
              "pct_avant": round(100*na/max(na+nb,1)), "tokens_achetes": len(toks), "dont_calls": len(hit), "precision": round(100*len(hit)/max(len(toks),1), 1),
              "delai_median_min": st.median(c["min_avant"]) if c["min_avant"] else None, "dernier_achat": time.strftime("%Y-%m-%d", time.gmtime(last)),
              "top_wallets": sorted(c["wallets"], key=lambda w: -len(ACT.get(w, {}).get("toks", set()) & CALLED))[:5]})
R.sort(key=lambda r: (-(r["precision"] * min(r["calls_avant"], 15)), -r["calls_avant"]))
print("racine | wallets | calls AVANT | calls après seulement | % avant | tokens achetés | dont calls | précision | délai médian | dernier achat")
for r in R:
    print(f"{r['racine']} | {r['wallets_actifs']}/{r['wallets']} | {r['calls_avant']} | {r['calls_apres']} | {r['pct_avant']}% | {r['tokens_achetes']} | {r['dont_calls']} | {r['precision']}% | {r['delai_median_min']} min | {r['dernier_achat']}")
    print("    wallets:", " ".join(r["top_wallets"]))
json.dump(R, open("etude/yeezus/resultat12.json", "w"))
