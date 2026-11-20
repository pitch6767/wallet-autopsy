# Étape 11 : suivi de l'argent des wallets qui ont arrêté (où partent les SOL, et le receveur continue-t-il sur les calls ?)
import json, urllib.request, time, sys, collections, threading
RPC = ["https://api.mainnet-beta.solana.com", "https://api.mainnet.solana.com"]; k = [0]
def rpc(m, p):
    for e in range(8):
        u = RPC[k[0] % 2]; k[0] += 1
        try:
            j = json.loads(urllib.request.urlopen(urllib.request.Request(u, json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p}).encode(), {"content-type":"application/json","user-agent":"curl/8.5"}), timeout=60).read())
            if "result" in j: return j["result"]
        except Exception: pass
        time.sleep(1.5 + e)
    return None
D = json.load(open(sys.argv[1]))
pre = collections.defaultdict(set)
for m, v in D.items():
    for x in v["trades"]:
        if x[1] == "buy" and x[5] <= v["tc"]: pre[x[0]].add(m)
def sorties(w, n=60):
    sigs = rpc("getSignaturesForAddress", [w, {"limit": n}]) or []
    out = []; first = last = None
    for s in sigs:
        if s.get("err"): continue
        tx = rpc("getTransaction", [s["signature"], {"maxSupportedTransactionVersion": 0, "encoding": "jsonParsed"}])
        if not tx: continue
        bt = tx.get("blockTime")
        ins = tx["transaction"]["message"]["instructions"] + [i for g in (tx["meta"].get("innerInstructions") or []) for i in g["instructions"]]
        for i in ins:
            p = i.get("parsed") if isinstance(i, dict) else None
            if not isinstance(p, dict): continue
            inf = p.get("info") or {}
            if p.get("type") in ("transfer", "transferChecked") and i.get("program") == "system" and inf.get("source") == w and inf.get("lamports", 0) >= 0.3e9:
                out.append((bt, inf["destination"], round(inf["lamports"]/1e9, 3)))
    return out, len(sigs)
SUIVIS = ["F7RV6aBWfniixoFkQNWmRwznDj2vae2XbusFfvMMjtbE", "FTaSBuVj6w2S7XUa8fw19xrLy57DDr6kZDL6sxDXtvTP", "E5FKUYe6ewCGKTaJ9yKx25S23cSowc4jNktDituLURoz",
          "JEETvEhPCKw7L8bLSfWeK5NyjcmHWQR3iqC1eC5Bg9MZ", "2o9UsXTRWZTfPt2mgTpUM5NcTCMKHsgox4nFdwTVdfks", "4rpW8e5Q2N6Ag7Q2Nem9e7Znsr74Ark5N6e2zGLk17bU",
          "EpX2frAkxvnxzRxEqfungBdrdap4NhaaBytJrTLHTPeV", "CuF7yvF5rKMV1uFrhjWJFzn3HL8qogDixFhzAtdCHD5e", "9ZvHo6MVfoAGkNMQpBkSYd7U7FPo8CtwLkvmFHK6Ab6Q"]
RES = {}; lock = threading.Lock()
def suivre(w):
    out, n = sorties(w)
    lignes = []
    for bt, dst, sol in sorted(out):
        o2, _ = sorties(dst, 25)
        lignes.append({"date": time.strftime("%Y-%m-%d %H:%M", time.gmtime(bt or 0)), "vers": dst, "sol": sol, "receveur_avant_post_calls": len(pre.get(dst, ())),
                       "receveur_renvoie": [(time.strftime("%Y-%m-%d", time.gmtime(b or 0)), d, s, len(pre.get(d, ()))) for b, d, s in o2[:6]]})
    with lock:
        RES[w] = lignes
        print(f"\n=== {w} (avant post sur {len(pre.get(w,()))} calls) — {n} dernières tx lues, {len(out)} sorties >= 0.3 SOL", flush=True)
        for l in lignes:
            print(f"  {l['date']}  -> {l['vers']}  {l['sol']} SOL | ce receveur achète avant post sur {l['receveur_avant_post_calls']} calls", flush=True)
            for r in l["receveur_renvoie"]: print(f"        puis {r[0]} -> {r[1]} {r[2]} SOL (avant post sur {r[3]} calls)", flush=True)
th = [threading.Thread(target=suivre, args=(w,)) for w in SUIVIS if len(w) > 30]
for t in th: t.start(); time.sleep(2)
for t in th: t.join()
json.dump(RES, open("etude/yeezus/resultat11.json", "w"))
