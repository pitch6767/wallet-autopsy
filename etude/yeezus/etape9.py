# Étape 9 : tous les trades gmgn (du plus ancien au post) pour chaque token appelé (gmgn garde 1 an)
import json, urllib.request, time, datetime as dt, threading, queue
H = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36", "accept": "application/json", "referer": "https://gmgn.ai/"}
def get(u):
    for k in range(8):
        try: return json.loads(urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=40).read())
        except Exception as e:
            time.sleep(5 * (k + 1) if "429" in str(e) else 2)
    return None
T = json.load(open("etude/yeezus/traders_complet.json"))
jobs = [(m, int(dt.datetime.fromisoformat(v["appel"]["date"]).timestamp())) for m, v in T.items() if v["appel"]["date"] > "2025-11-21"]
OUT = {}; lock = threading.Lock(); q = queue.Queue(); [q.put(j) for j in jobs]
def work():
    while True:
        try: m, tc = q.get_nowait()
        except queue.Empty: return
        tr = []; cur = None; pages = 0; fin = False
        while pages < 600:
            j = get(f"https://gmgn.ai/vas/api/v1/token_trades/sol/{m}?limit=50&revert=true" + (f"&cursor={cur}" if cur else ""))
            d = (j or {}).get("data") or {}; h = d.get("history") or []; pages += 1
            for x in h:
                if x["timestamp"] > tc + 600: fin = True; break
                tr.append({k: x.get(k) for k in ("maker", "event", "amount_usd", "quote_amount", "price_usd", "timestamp", "tx_hash", "maker_tags", "maker_token_tags")})
            cur = d.get("next")
            if fin or not h or not cur: break
            time.sleep(0.4)
        with lock:
            OUT[m] = {"tc": tc, "pages": pages, "complet": fin, "premier": tr[0]["timestamp"] if tr else None, "trades": tr}
            print(len(OUT), m, "pages", pages, "trades", len(tr), "jusqu'au post" if fin else "INCOMPLET", time.strftime("%H:%M:%S"), flush=True)
            if len(OUT) % 10 == 0: json.dump(OUT, open("etude/yeezus/trades_gmgn.json", "w"))
th = [threading.Thread(target=work) for _ in range(4)]; [t.start() for t in th]; [t.join() for t in th]
json.dump(OUT, open("etude/yeezus/trades_gmgn.json", "w")); print("FIN")
