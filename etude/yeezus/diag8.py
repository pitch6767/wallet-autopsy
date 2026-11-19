import json, urllib.request, time
M = ["34DXEU2ttEtBSb1TqGJm7izgvYTTkqKcCoiNWdPDpump", "Gg5aWvfucyMwihDzyfCEaLgyeeNE2dkob2LTwWfHpump", "38W8MYeqwpnZTBNbgRBnReqM2CbiYfCXgCbYsmjhpump"]
RPC = ["https://api.mainnet-beta.solana.com", "https://solana-rpc.publicnode.com", "https://api.mainnet.solana.com", "https://solana.drpc.org", "https://rpc.ankr.com/solana"]
def call(u, m, p):
    t=time.time()
    try:
        r = urllib.request.urlopen(urllib.request.Request(u, json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p}).encode(), {"content-type":"application/json","user-agent":"curl/8.5"}), timeout=60).read()
        j = json.loads(r); return ("OK" if "result" in j else "ERRJSON"), (len(j["result"]) if isinstance(j.get("result"), list) else str(j)[:200]), round(time.time()-t,1), j.get("result")
    except Exception as e:
        b = ""
        try: b = e.read()[:200]
        except: pass
        return "EXC", str(e)[:100] + " " + str(b), round(time.time()-t,1), None
for mint in M:
    for u in RPC:
        st, info, dt_, res = call(u, "getSignaturesForAddress", [mint, {"limit": 1000}])
        print(mint[:6], u, "p1", st, info, dt_)
        if res:
            print("   newest", res[0].get("blockTime"), "oldest", res[-1].get("blockTime"))
            st, info, dt_, res2 = call(u, "getSignaturesForAddress", [mint, {"limit": 1000, "before": res[-1]["signature"]}])
            print("   p2", st, info, dt_, (res2[-1].get("blockTime") if res2 else None))
            st, info, dt_, tx = call(u, "getTransaction", [res[-1]["signature"], {"maxSupportedTransactionVersion": 0, "encoding": "json"}])
            print("   tx", st, str(info)[:80], dt_)
        time.sleep(1)
