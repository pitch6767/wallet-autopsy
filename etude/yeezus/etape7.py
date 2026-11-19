# Étape 7 : liens on-chain entre wallets candidats (transactions communes) via RPC public
import json, urllib.request, time, itertools, collections
RPC = ["https://api.mainnet-beta.solana.com", "https://solana-rpc.publicnode.com", "https://api.mainnet.solana.com"]
k = [0]
def rpc(method, params):
    for essai in range(8):
        u = RPC[k[0] % len(RPC)]; k[0] += 1
        try:
            r = urllib.request.urlopen(urllib.request.Request(u, json.dumps({"jsonrpc":"2.0","id":1,"method":method,"params":params}).encode(), {"content-type":"application/json","user-agent":"curl/8.5"}), timeout=60).read()
            j = json.loads(r)
            if "result" in j: return j["result"]
        except Exception as e: pass
        time.sleep(2 + essai)
    return None
C = json.load(open("etude/yeezus/candidats.json"))
S = {}
for a in C["tous"]:
    sigs = []; before = None
    for p in range(15):
        r = rpc("getSignaturesForAddress", [a, {"limit": 1000, **({"before": before} if before else {})}])
        if not r: break
        sigs += [x["signature"] for x in r if not x.get("err")]
        before = r[-1]["signature"]
        if len(r) < 1000: break
        time.sleep(0.3)
    S[a] = set(sigs); print(a, len(sigs), "complet" if len(sigs) < 15000 else "tronqué")
pairs = []
for a, b in itertools.combinations(S, 2):
    com = S[a] & S[b]
    if com: pairs.append((a, b, len(com), sorted(com)[:5]))
pairs.sort(key=lambda x: -x[2])
print("PAIRES AVEC TRANSACTIONS COMMUNES", len(pairs))
det = {}
for a, b, n, ex in pairs[:80]:
    print("PAIRE", a, b, n)
    for s in ex[:2]:
        tx = rpc("getTransaction", [s, {"maxSupportedTransactionVersion": 0, "encoding": "jsonParsed"}])
        if not tx: continue
        keys = [x["pubkey"] if isinstance(x, dict) else x for x in tx["transaction"]["message"]["accountKeys"]]
        pre, post = tx["meta"]["preBalances"], tx["meta"]["postBalances"]
        delta = {keys[i]: round((post[i]-pre[i])/1e9, 3) for i in range(len(keys)) if keys[i] in (a, b)}
        ins = [i.get("parsed", {}).get("type") if isinstance(i.get("parsed"), dict) else i.get("program") for i in tx["transaction"]["message"]["instructions"]]
        print("   tx", s[:20], tx.get("blockTime"), "SOL", delta, "instr", ins[:6])
json.dump({"paires": [(a, b, n) for a, b, n, _ in pairs]}, open("etude/yeezus/liens.json", "w"))
