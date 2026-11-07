# 07.11.2026 : test des transactions « version 1 » de Solana (refusées avec maxSupportedTransactionVersion 0)
import json, time, urllib.request
def post(m, p):
    r = urllib.request.urlopen(urllib.request.Request("https://api.mainnet-beta.solana.com", data=json.dumps({"jsonrpc": "2.0", "id": 1, "method": m, "params": p}).encode(), headers={"content-type": "application/json"}), timeout=30)
    return json.load(r)
d = json.load(urllib.request.urlopen(urllib.request.Request("https://api.geckoterminal.com/api/v2/networks/solana/new_pools?page=1", headers={"user-agent": "sonde"}), timeout=30))
mint = next(p["relationships"]["base_token"]["data"]["id"].replace("solana_", "") for p in d["data"] if p["relationships"]["base_token"]["data"]["id"].endswith("pump"))
sigs = post("getSignaturesForAddress", [mint, {"limit": 30}])["result"]; print("mint", mint, len(sigs))
n = {}
for s in sigs[:15]:
    for v in (0, 1):
        r = post("getTransaction", [s["signature"], {"encoding": "jsonParsed", "maxSupportedTransactionVersion": v, "commitment": "confirmed"}])
        k = f"v{v} " + ("ok" if r.get("result") else str(r.get("error", {}).get("message", "vide"))[:60]); n[k] = n.get(k, 0) + 1
        if v == 1 and r.get("result") and "montre" not in n:
            n["montre"] = 1; t = r["result"]; print("version", t.get("version"), "| clés meta", sorted(t["meta"].keys())[:12], "| accountKeys[0]", str(t["transaction"]["message"]["accountKeys"][0])[:120])
        time.sleep(0.15)
print(n)
