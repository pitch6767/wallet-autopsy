# 07.11.2026 : l'étude des groupes n'avance pas — mesure de la vitesse réelle des nœuds Solana publics depuis GitHub, et des coins jeunes visibles
import json, time, urllib.request
def post(u, m, p):
    t = time.time()
    try:
        r = urllib.request.urlopen(urllib.request.Request(u, data=json.dumps({"jsonrpc": "2.0", "id": 1, "method": m, "params": p}).encode(), headers={"content-type": "application/json", "user-agent": "sonde"}), timeout=30)
        d = json.load(r); return round(time.time() - t, 2), ("ok" if "result" in d else str(d)[:120]), d.get("result")
    except Exception as e: return round(time.time() - t, 2), str(e)[:120], None
MINT = "So11111111111111111111111111111111111111112"
for u in ["https://api.mainnet-beta.solana.com", "https://solana-rpc.publicnode.com", "https://solana.drpc.org"]:
    for i in range(5):
        d, s, r = post(u, "getSignaturesForAddress", [MINT, {"limit": 20}]); print(u, "signatures", d, "s", s)
        if r:
            d2, s2, _ = post(u, "getTransaction", [r[0]["signature"], {"encoding": "jsonParsed", "maxSupportedTransactionVersion": 0}]); print(u, "transaction", d2, "s", s2)
t = time.time()
try:
    d = json.load(urllib.request.urlopen(urllib.request.Request("https://api.geckoterminal.com/api/v2/networks/solana/new_pools?page=1", headers={"user-agent": "sonde"}), timeout=30))
    L = d.get("data", []); print("GeckoTerminal new_pools", round(time.time() - t, 2), "s,", len(L), "pools ; dex :", sorted({(p["relationships"]["dex"]["data"] or {}).get("id") for p in L}))
    print("mints pump :", sum(1 for p in L if p["relationships"]["base_token"]["data"]["id"].endswith("pump")))
    for p in L[:5]: a = p["attributes"]; print("  ", a["name"], a["pool_created_at"], a.get("transactions", {}).get("h1"))
except Exception as e: print("GeckoTerminal erreur", e)
