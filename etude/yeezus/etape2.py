# Étape 2 : sondes des sources de trades Solana (aucune clé)
import json, urllib.request
M = "34DXEU2ttEtBSb1TqGJm7izgvYTTkqKcCoiNWdPDpump"
def get(u, data=None, h=None):
    hh = {"user-agent": "curl/8.5", "accept": "application/json"}; hh.update(h or {})
    return urllib.request.urlopen(urllib.request.Request(u, data=data, headers=hh), timeout=40).read()
def rpc(url, method, params, ua=None):
    return get(url, json.dumps({"jsonrpc":"2.0","id":1,"method":method,"params":params}).encode(), {"content-type":"application/json", **({"user-agent": ua} if ua else {})})
RPCS = ["https://api.mainnet-beta.solana.com", "https://solana-rpc.publicnode.com", "https://solana.drpc.org", "https://rpc.ankr.com/solana",
        "https://solana-mainnet.g.alchemy.com/v2/demo", "https://api.mainnet.solana.com", "https://solana.api.onfinality.io/public",
        "https://go.getblock.io/solana", "https://solana.leorpc.com/?api_key=FREE", "https://mainnet.helius-rpc.com/", "https://rpc.shyft.to", "https://solana-mainnet.rpc.extrnode.com"]
sig = None
for u in RPCS:
    for ua in ("curl/8.5", "solana-web3.js/1.95"):
        try:
            b = rpc(u, "getSignaturesForAddress", [M, {"limit": 3}], ua); print("RPC", u, ua, "OK", b[:250]); 
            j = json.loads(b); 
            if j.get("result"): sig = sig or j["result"][0]["signature"]; ok=u
            break
        except Exception as e: print("RPC", u, ua, "ERR", str(e)[:120])
if sig:
    for u in RPCS:
        try: b = rpc(u, "getTransaction", [sig, {"maxSupportedTransactionVersion":0, "encoding":"jsonParsed"}]); print("TX", u, "OK", len(b))
        except Exception as e: print("TX", u, "ERR", str(e)[:100])
T = {
 "gecko_token_pools": f"https://api.geckoterminal.com/api/v2/networks/solana/tokens/{M}/pools",
 "dexs_tokens": f"https://api.dexscreener.com/latest/dex/tokens/{M}",
 "gmgn_tt": f"https://gmgn.ai/defi/quotation/v1/tokens/top_traders/sol/{M}?orderby=profit&direction=desc",
 "gmgn_vas": f"https://gmgn.ai/vas/api/v1/token_traders/sol/{M}?limit=100&orderby=profit&direction=desc",
 "pump_v1": f"https://frontend-api.pump.fun/trades/all/{M}?limit=5&offset=0",
 "pump_v3": f"https://frontend-api-v3.pump.fun/trades/all/{M}?limit=5&offset=0",
 "pump_swap": f"https://swap-api.pump.fun/v1/coins/{M}/trades?limit=5",
 "solscan_v2": f"https://api-v2.solscan.io/v2/token/holders?address={M}&page_size=10&page=1",
 "solanatracker": f"https://data.solanatracker.io/top-traders/{M}",
 "jup_tokens": f"https://lite-api.jup.ag/tokens/v2/search?query={M}",
 "rugcheck": f"https://api.rugcheck.xyz/v1/tokens/{M}/report/summary",
 "photon": f"https://photon-sol.tinyastro.io/api/tokens/{M}",
 "axiom": f"https://api.axiom.trade/token-info?pairAddress={M}",
 "dexs_io": f"https://io.dexscreener.com/dex/log/amm/v4/pumpfundex/top/solana/{M}?q=So11111111111111111111111111111111111111112",
 "mobula": f"https://api.mobula.io/api/1/market/trades/pair?asset={M}&blockchain=solana&limit=5",
 "moralis": f"https://solana-gateway.moralis.io/token/mainnet/{M}/swaps",
}
for k, u in T.items():
    for h in ({}, {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36", "origin": "https://pump.fun", "referer": "https://pump.fun/"}):
        try: b = get(u, h=h); print("API", k, "OK", len(b), b[:300]); break
        except Exception as e: print("API", k, "ERR", str(e)[:120])
# gecko trades of top pool
try:
    j = json.loads(get(T["gecko_token_pools"])); p = j["data"][0]["attributes"]["address"]
    b = get(f"https://api.geckoterminal.com/api/v2/networks/solana/pools/{p}/trades"); print("GECKO trades", b[:600])
except Exception as e: print("gecko trades ERR", e)
