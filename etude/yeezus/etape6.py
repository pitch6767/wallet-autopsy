# Étape 6 : sonde pagination + tri, puis tous les traders (avec transferts / financeur) de chaque token
import json, urllib.request, time, datetime as dt
H = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36", "accept": "application/json", "referer": "https://gmgn.ai/"}
def get(u):
    for k in range(6):
        try: return json.loads(urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=40).read())
        except Exception as e:
            if "429" in str(e): time.sleep(15*(k+1)); continue
            print("ERR", u[-80:], str(e)[:60]); return None
    return None
T = json.load(open("etude/yeezus/traders.json"))
toks = [m for m, v in T.items() if v["traders"]]
M = toks[0]; B = f"https://gmgn.ai/vas/api/v1/token_traders/sol/{M}"
for q in ["?limit=100&orderby=profit&direction=desc", "?limit=100&orderby=start_holding_at&direction=asc", "?limit=100&orderby=buy_volume_cur&direction=desc", "?limit=500&orderby=profit&direction=desc", "?limit=100&orderby=profit&direction=asc"]:
    j = get(B + q); d = (j or {}).get("data") or {}
    print("SONDE", q, "cles", [k for k in d if k != "list"], {k: d[k] for k in d if k != "list"}, "n", len(d.get("list") or []))
    time.sleep(2)
KEEP = ["address","profit","realized_profit","buy_volume_cur","sell_volume_cur","start_holding_at","end_holding_at","buy_tx_count_cur","sell_tx_count_cur","tags","maker_token_tags","native_transfer","token_transfer_in","token_transfer_out","twitter_username","wallet_tag_v2","is_suspicious","avg_cost","avg_sold"]
OUT = {}
for i, m in enumerate(toks):
    seen = {}
    for q in ["?limit=100&orderby=profit&direction=desc", "?limit=100&orderby=start_holding_at&direction=asc", "?limit=100&orderby=buy_volume_cur&direction=desc", "?limit=100&orderby=profit&direction=asc"]:
        u = f"https://gmgn.ai/vas/api/v1/token_traders/sol/{m}" + q; cur = None
        for page in range(5):
            j = get(u + (f"&cursor={cur}" if cur else ""))
            d = (j or {}).get("data") or {}
            for t in d.get("list") or []: seen[t["address"]] = {k: t.get(k) for k in KEEP}
            cur = d.get("next") or d.get("cursor")
            if not cur or not d.get("list"): break
            time.sleep(1.5)
        time.sleep(1.5)
    OUT[m] = {"appel": T[m]["appel"], "traders": list(seen.values())}
    print(i, m, len(seen))
json.dump(OUT, open("etude/yeezus/traders_complet.json", "w"))
print("FIN", sum(len(v["traders"]) for v in OUT.values()))
