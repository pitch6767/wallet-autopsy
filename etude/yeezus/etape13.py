# Étape 13 : où part l'argent des groupes FT9VD et 7v56q43K quand ils arrêtent, et le receveur continue-t-il sur les calls ?
import json, urllib.request, time, collections
H = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36", "accept": "application/json", "referer": "https://gmgn.ai/"}
def gm(u):
    for k in range(5):
        try: return json.loads(urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=40).read())
        except Exception as e:
            if "429" in str(e): time.sleep(5*(k+1)); continue
            return {}
    return {}
RPC = ["https://api.mainnet-beta.solana.com", "https://api.mainnet.solana.com"]; kk = [0]
def rpc(m, p):
    for e in range(8):
        u = RPC[kk[0] % 2]; kk[0] += 1
        try:
            j = json.loads(urllib.request.urlopen(urllib.request.Request(u, json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p}).encode(), {"content-type":"application/json","user-agent":"curl/8.5"}), timeout=60).read())
            if "result" in j: return j["result"]
        except Exception: pass
        time.sleep(1 + e)
    return None
CALLED = set(json.load(open("etude/yeezus/traders_complet.json")))
D = lambda t: time.strftime("%Y-%m-%d %H:%M", time.gmtime(t or 0))
def activite(w, pages=6):
    toks = set(); last = 0; first = None; cur = None; calls = []
    for p in range(pages):
        j = gm(f"https://gmgn.ai/vas/api/v1/wallet_activity/sol?wallet={w}&limit=50&type=buy" + (f"&cursor={cur}" if cur else ""))
        d = j.get("data") or {}; L = d.get("activities") or []
        for x in L:
            t = (x.get("token") or {}).get("address"); ts = x.get("timestamp") or 0
            if not t: continue
            toks.add(t); last = max(last, ts); first = min(first or ts, ts)
            if t in CALLED: calls.append(D(ts)[:10])
        cur = d.get("next")
        if not cur or not L: break
        time.sleep(0.3)
    return {"tokens": len(toks), "calls": len(set(toks) & CALLED), "dernier": D(last)[:10], "premier": D(first)[:10], "dates_calls": sorted(set(calls))[-6:]}
def sorties(w, t_fin, jours=45, maxtx=400):
    # signatures entre t_fin - 3 j et t_fin + jours
    sigs = []; before = None
    for p in range(40):
        r = rpc("getSignaturesForAddress", [w, {"limit": 1000, **({"before": before} if before else {})}])
        if not r: break
        for x in r:
            bt = x.get("blockTime") or 0
            if t_fin - 3*86400 <= bt <= t_fin + jours*86400 and not x.get("err"): sigs.append((bt, x["signature"]))
        before = r[-1]["signature"]
        if (r[-1].get("blockTime") or 0) < t_fin - 3*86400 or len(r) < 1000: break
    sigs = sorted(sigs)[:maxtx]
    out = []
    for bt, s in sigs:
        tx = rpc("getTransaction", [s, {"maxSupportedTransactionVersion": 0, "encoding": "jsonParsed"}])
        if not tx: continue
        ins = tx["transaction"]["message"]["instructions"] + [i for g in (tx["meta"].get("innerInstructions") or []) for i in g["instructions"]]
        for i in ins:
            p = i.get("parsed") if isinstance(i, dict) else None
            if isinstance(p, dict) and i.get("program") == "system" and p.get("type") == "transfer":
                inf = p["info"]
                if inf.get("source") == w and inf.get("lamports", 0) >= 0.1e9: out.append((bt, inf["destination"], round(inf["lamports"]/1e9, 3)))
    return out, len(sigs)
GROUPES = {"FT9VD": ["FT9VDscMGy2qDkcbFBD4xLkaGPBqkEgDA6E59GaHN7u6", "5aud5SUDR3eS2Es6a7gZDXedXMEJUnJG1XdzXXHu89YS", "51o5VwwsB2KG1Ejuq2FdmaCQcnuTyKRF6c5HjtYVmEgr"],
           "7v56q43K": ["6pNn9kad5aC3ei9ztg62Y7RjFkTTavNsCfqcybVhCCx6", "GTgo1tRPS6q5vMjyXhK1vkfBuPPpefgiTdr3oKpytP54", "EEbS5amC8uQbxhbMN5vy8h8eAEuGvsyeBN565Y6SCqME", "7v56q43K6MbxKGaFVTEej45sjJddLtUU3eMapDDSMJ8f"]}
RES = {}; vus = set()
for g, ws in GROUPES.items():
    print(f"\n######## GROUPE {g}", flush=True)
    for w in ws:
        a = activite(w, 8); t_fin = int(time.mktime(time.strptime(a["dernier"], "%Y-%m-%d"))) if a["dernier"] > "1971" else int(time.time())
        out, n = sorties(w, t_fin)
        print(f"\n== {w} | {a['tokens']} tokens achetés, {a['calls']} calls | actif {a['premier']} -> {a['dernier']} | {n} tx lues autour de l'arrêt, {len(out)} sorties >= 0.1 SOL", flush=True)
        agg = collections.defaultdict(lambda: [0, 0, None])
        for bt, dst, sol in out:
            x = agg[dst]; x[0] += sol; x[1] += 1; x[2] = x[2] or bt
        for dst, (sol, n2, bt) in sorted(agg.items(), key=lambda x: -x[1][0])[:6]:
            if dst in vus: print(f"   -> {dst} {sol:.2f} SOL ({n2}x, 1re fois {D(bt)}) [déjà vu]"); continue
            vus.add(dst); b = activite(dst, 6)
            print(f"   -> {dst} {sol:.2f} SOL ({n2}x, 1re fois {D(bt)}) | ce wallet : {b['tokens']} tokens, {b['calls']} calls, actif {b['premier']} -> {b['dernier']} | calls: {b['dates_calls']}", flush=True)
            RES.setdefault(g, []).append({"de": w, "vers": dst, "sol": round(sol, 2), "n": n2, "date": D(bt), **b})
            if sol >= 1 and b["tokens"] == 0:   # wallet relais : on suit un saut de plus
                o2, _ = sorties(dst, bt, 30, 150)
                a2 = collections.defaultdict(float)
                for _, d2, s2 in o2: a2[d2] += s2
                for d2, s2 in sorted(a2.items(), key=lambda x: -x[1])[:4]:
                    c = activite(d2, 6)
                    print(f"        puis -> {d2} {s2:.2f} SOL | {c['tokens']} tokens, {c['calls']} calls, actif {c['premier']} -> {c['dernier']} | calls: {c['dates_calls']}", flush=True)
json.dump(RES, open("etude/yeezus/resultat13.json", "w"))
print("FIN")
