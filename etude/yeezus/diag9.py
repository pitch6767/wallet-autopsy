import json, urllib.request, time
H = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36", "accept": "application/json", "referer": "https://gmgn.ai/"}
def get(u):
    try: return json.loads(urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=40).read())
    except Exception as e: return {"_err": str(e)[:80]}
a = "3KcPSJ8ouE7H1feoWHmhDwXhLnXhpxP6R6713uytFmBM"; m = "Gg5aWvfucyMwihDzyfCEaLgyeeNE2dkob2LTwWfHpump"
j = get(f"https://gmgn.ai/api/v1/token_info/sol/{m}"); print("TOKENINFO", json.dumps(j)[:2500])
j = get(f"https://gmgn.ai/api/v1/token_dev_info/sol/{m}"); print("DEVINFO", json.dumps(j)[:1500])
for u in [f"https://gmgn.ai/vas/api/v1/wallet_holdings/sol/{a}?limit=50&orderby=last_active_timestamp&direction=desc&showsmall=true&sellout=true",
          f"https://gmgn.ai/api/v1/wallet_holdings/sol/{a}?limit=50&orderby=last_active_timestamp&direction=desc&showsmall=true&sellout=true",
          f"https://gmgn.ai/defi/quotation/v1/wallet/sol/holdings/{a}?limit=50&orderby=last_active_timestamp&direction=desc&showsmall=true&sellout=true",
          f"https://gmgn.ai/vas/api/v1/wallet_activity/sol?wallet={a}&limit=50",
          f"https://gmgn.ai/api/v1/wallet_activity/sol?wallet={a}&limit=50",
          f"https://gmgn.ai/defi/quotation/v1/wallet_activity/sol?wallet={a}&limit=50",
          f"https://gmgn.ai/api/v1/wallet_stat/sol/{a}/30d", f"https://gmgn.ai/vas/api/v1/wallet_stat/sol/{a}/30d"]:
    j = get(u); print("W", u.split("gmgn.ai")[1][:60], json.dumps(j)[:900]); time.sleep(1)
# v4
