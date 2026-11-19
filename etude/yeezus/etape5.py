# Étape 5 : historique global des wallets candidats (gmgn)
import json, urllib.request, time
H = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36", "accept": "application/json", "referer": "https://gmgn.ai/"}
C = """F7RV6aBWfniixoFkQNWmRwznDj2vae2XbusFfvMMjtbE JEETvEhPCKw7L8bLSfWeK5NyjcmHWQR3iqC1eC5Bg9MZ 5FeAupGkPDpnPqPi8WzyF5CMyrfyatttB6pwNb7GEYzJ FTaSBuVj6w2S7XUa8fw19xrLy57DDr6kZDL6sxDXtvTP 2fg5QD1eD7rzNNCsvnhmXFm5hqNgwTTG8p7kQ6f3rx6f HK9YzXtrwnAFrGfyPp4r8Tz7ffPLPZTCSowcvqzr3jZE 4jP9FZ7BNj4MBoJS3mNzD4vdhTZHZbZ5Cy82BSmLpDd3 GXDZ1GDLsb9X5wApUo2pH6GPMCMAecLo92vBhDSS1ed 2JKCGnz5yabxcpARBnSKJBNPiFrfRDhk5Y6HY9zC94oq GuBsW6Gfj4GsJt1fXngR81B4fnDD8WQ3gw37o8qJrjUj niggerd597QYedtvjQDVHZTCCGyJrwHNm2i49dkm5zS 3nG9zBc6fTne3j9kkS1CB5quyt25CS29GEjvMGNKmDSz 7Aid9ZPdnSjHMgZ4NMU2awv7omW89WZd689bin9714yb FT9VDscMGy2qDkcbFBD4xLkaGPBqkEgDA6E59GaHN7u6 B5SPrkAnfjhvF6BUsLFNmjQ6jTWamHYYPK8VM6k6Y3Ln""".split()
URLS = ["https://gmgn.ai/vas/api/v1/wallet_stat/sol/{a}/{p}", "https://gmgn.ai/api/v1/wallet_stat/sol/{a}/{p}", "https://gmgn.ai/defi/quotation/v1/smartmoney/sol/walletNew/{a}?period={p}", "https://gmgn.ai/vas/api/v1/wallet_holdings/sol/{a}?limit=50&orderby=last_active_timestamp&direction=desc&showsmall=true&sellout=true"]
ok = None
for u in URLS:
    try:
        b = urllib.request.urlopen(urllib.request.Request(u.format(a=C[0], p="30d"), headers=H), timeout=40).read(); print("SONDE OK", u, b[:1500]); ok = ok or u
    except Exception as e: print("SONDE ERR", u, str(e)[:80])
    time.sleep(3)
R = {}
for a in C:
    R[a] = {}
    for p in ("7d", "30d", "all"):
        for u in URLS[:3]:
            try:
                j = json.loads(urllib.request.urlopen(urllib.request.Request(u.format(a=a, p=p), headers=H), timeout=40).read())
                d = j.get("data") or {}
                if d: R[a][p] = {k: v for k, v in d.items() if not isinstance(v, (list, dict))}; break
            except Exception as e:
                if "429" in str(e): time.sleep(20)
            time.sleep(2)
    print(a, json.dumps(R[a])[:900])
    try:
        j = json.loads(urllib.request.urlopen(urllib.request.Request(URLS[3].format(a=a), headers=H), timeout=40).read())
        R[a]["recents"] = [{k: h.get(k) for k in ("token", "symbol", "realized_profit", "total_profit", "unrealized_profit", "last_active_timestamp", "start_holding_at", "history_bought_cost")} for h in ((j.get("data") or {}).get("holdings") or (j.get("data") or {}).get("list") or [])][:50]
        print("  recents", len(R[a]["recents"]), json.dumps(R[a]["recents"][:2])[:500])
    except Exception as e: print("  recents ERR", str(e)[:80])
    time.sleep(3)
json.dump(R, open("etude/yeezus/wallets.json", "w"))
