import json, urllib.request, time
H = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36", "accept": "application/json", "referer": "https://gmgn.ai/"}
M = "C9rL8FzN"  # remplacé ci-dessous
T = json.load(open("etude/yeezus/traders_complet.json"))
mint = [m for m in T if m.startswith("C9rL8F")][0]
import datetime as dt
tc = int(dt.datetime.fromisoformat(T[mint]["appel"]["date"]).timestamp())
U = [f"https://gmgn.ai/vas/api/v1/token_trades/sol/{mint}?limit=100",
     f"https://gmgn.ai/vas/api/v1/token_trades/sol/{mint}?limit=100&to={tc}",
     f"https://gmgn.ai/vas/api/v1/token_trades/sol/{mint}?limit=100&from={tc-3600}&to={tc}",
     f"https://gmgn.ai/defi/quotation/v1/trades/sol/{mint}?limit=100",
     f"https://gmgn.ai/defi/quotation/v1/trades/sol/{mint}?limit=100&to={tc}",
     f"https://gmgn.ai/api/v1/token_trades/sol/{mint}?limit=100&to={tc}",
     f"https://gmgn.ai/vas/api/v1/token_holders/sol/{mint}?limit=100&orderby=amount_percentage&direction=desc",
     f"https://gmgn.ai/vas/api/v1/token_traders/sol/{mint}?limit=100&orderby=start_holding_at&direction=asc&tag=bundler",
     f"https://gmgn.ai/api/v1/token_stat/sol/{mint}",
     f"https://gmgn.ai/defi/quotation/v1/tokens/sol/{mint}"]
for u in U:
    try:
        b = urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=40).read()
        j = json.loads(b); d = j.get("data")
        lst = d.get("history") or d.get("list") or d.get("trades") if isinstance(d, dict) else d
        print("OK", u.split("gmgn.ai")[1][:90], "cles", list(d.keys())[:12] if isinstance(d, dict) else type(d), "n", len(lst) if isinstance(lst, list) else None)
        if isinstance(lst, list) and lst: print("   EX", json.dumps(lst[0])[:700]); print("   DERNIER ts", lst[-1].get("timestamp"), "PREMIER ts", lst[0].get("timestamp"), "tc", tc, "next", (d or {}).get("next"))
    except Exception as e: print("ERR", u.split("gmgn.ai")[1][:90], str(e)[:80])
    time.sleep(2)
