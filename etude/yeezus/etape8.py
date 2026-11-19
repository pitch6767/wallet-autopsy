# Étape 8 (option A) : tous les acheteurs on-chain dans l'heure avant chaque post (RPC publics)
import json, urllib.request, time, datetime as dt, threading, queue, os
RPC = ["https://api.mainnet-beta.solana.com", "https://api.mainnet.solana.com"]
def call(url, method, params):
    for essai in range(10):
        try:
            r = urllib.request.urlopen(urllib.request.Request(url, json.dumps({"jsonrpc":"2.0","id":1,"method":method,"params":params}).encode(), {"content-type":"application/json","user-agent":"curl/8.5"}), timeout=60).read()
            j = json.loads(r)
            if "result" in j: return j["result"]
            time.sleep(2 + essai)
        except Exception as e:
            time.sleep(3 + 3 * essai)
    return "ECHEC"
T = json.load(open("etude/yeezus/traders_complet.json"))
OUTF = "etude/yeezus/acheteurs.json"
OUT = json.load(open(OUTF)) if os.path.exists(OUTF) else {}
FEN = 3 * 3600; CAP_PAGES = 300; CAP_TX = 2500
for n, (mint, v) in enumerate(T.items()):
    if mint in OUT and OUT[mint].get("fini"): continue
    tc = int(dt.datetime.fromisoformat(v["appel"]["date"]).timestamp())
    sigs = []; before = None; pages = 0; atteint = False; k = 0; derniers = []; debut_atteint = False
    while pages < CAP_PAGES:
        r = call(RPC[k % 2], "getSignaturesForAddress", [mint, {"limit": 1000, **({"before": before} if before else {})}]); k += 1
        if r == "ECHEC" or not r: break
        pages += 1
        for x in r:
            bt = x.get("blockTime") or 0
            if tc - FEN <= bt <= tc + 5 and not x.get("err"): sigs.append((x["signature"], bt))
        before = r[-1]["signature"]
        if (r[-1].get("blockTime") or 0) < tc - FEN: atteint = True
        derniers = (derniers + [(x["signature"], x.get("blockTime") or 0) for x in r if not x.get("err")])[-600:]
        if len(r) < 1000: debut_atteint = True; break
        time.sleep(0.25)
    sigs = sorted(sigs, key=lambda x: -x[1])[:CAP_TX]   # les plus proches du post
    deb = derniers if debut_atteint else []          # 600 premières tx du token (création + bundle)
    vus = {x[0] for x in sigs}; sigs += [x for x in deb if x[0] not in vus]
    q = queue.Queue(); [q.put(s) for s in sigs]; res = []; lock = threading.Lock()
    def worker(url):
        while True:
            try: s, bt = q.get_nowait()
            except queue.Empty: return
            tx = call(url, "getTransaction", [s, {"maxSupportedTransactionVersion": 0, "encoding": "json"}])
            if isinstance(tx, dict):
                meta = tx.get("meta") or {}; keys = tx["transaction"]["message"]["accountKeys"] + (meta.get("loadedAddresses") or {}).get("writable", []) + (meta.get("loadedAddresses") or {}).get("readonly", [])
                pre = {(b.get("owner")): float(b["uiTokenAmount"]["uiAmount"] or 0) for b in meta.get("preTokenBalances", []) if b.get("mint") == mint}
                post = {(b.get("owner")): float(b["uiTokenAmount"]["uiAmount"] or 0) for b in meta.get("postTokenBalances", []) if b.get("mint") == mint}
                payer = keys[0]; dsol = (meta["postBalances"][0] - meta["preBalances"][0]) / 1e9
                rec = [(o, round(post.get(o, 0) - pre.get(o, 0))) for o in set(pre) | set(post) if post.get(o, 0) - pre.get(o, 0) > 0]
                vend = [o for o in set(pre) | set(post) if post.get(o, 0) - pre.get(o, 0) < 0]
                if rec:
                    with lock: res.append({"sig": s, "slot": tx.get("slot"), "t": bt, "payeur": payer, "sol_payeur": round(-dsol, 4), "recoit": rec, "envoie": vend})
            time.sleep(0.12)
    th = [threading.Thread(target=worker, args=(u,)) for u in RPC for _ in range(2)]
    [t.start() for t in th]; [t.join() for t in th]
    OUT[mint] = {"appel": v["appel"]["date"], "pages": pages, "fenetre_atteinte": atteint, "tx_fenetre": len(sigs), "debut_atteint": debut_atteint, "creation": min([x[1] for x in deb]) if deb else None, "achats": res, "fini": True}
    json.dump(OUT, open(OUTF, "w"))
    print(n, mint, "pages", pages, "atteint", atteint, "tx", len(sigs), "achats", len(res), time.strftime("%H:%M:%S"), flush=True)
print("FIN")
