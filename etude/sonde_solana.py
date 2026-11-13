# 13.11.2026 : que renvoie crypto-price avec une heure non alignée (= « prix en direct » du bot) ? (lecture seule)
import json, urllib.request, datetime, time
def get(u):
    try:
        with urllib.request.urlopen(urllib.request.Request(u, headers={"user-agent": "Mozilla/5.0"}), timeout=60) as r: return json.loads(r.read())
    except Exception as e: return {"erreur": str(e)}
for k in range(4):
    now = time.time(); iso = datetime.datetime.fromtimestamp(now - 1, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    debut = int(now // 300 * 300); isod = datetime.datetime.fromtimestamp(debut, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    a = get(f"https://polymarket.com/api/crypto/crypto-price?symbol=BTC&eventStartTime={iso}&variant=fiveminute")
    b = get(f"https://polymarket.com/api/crypto/crypto-price?symbol=BTC&eventStartTime={isod}&variant=fiveminute")
    bn = get("https://data-api.binance.vision/api/v3/ticker/price?symbol=BTCUSDT")
    print(iso, "| « direct » :", a.get("openPrice"), "| ouverture du cycle", isod, ":", b.get("openPrice"), "| Binance :", bn.get("price"))
    time.sleep(20)
