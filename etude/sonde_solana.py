# 13.11.2026 : vérification du gagnant officiel de 7 cycles où Binance a bougé de ≥ 10 pb dans l'autre sens que le gagnant du banc (lecture seule)
import json, urllib.request, datetime
def get(u):
    try:
        with urllib.request.urlopen(urllib.request.Request(u, headers={"user-agent": "Mozilla/5.0"}), timeout=60) as r: return json.loads(r.read())
    except Exception as e: return {"erreur": str(e)}
for iso, banc in [("2026-11-09T14:50:00Z","UP"),("2026-11-10T09:10:00Z","DOWN"),("2026-11-10T13:25:00Z","DOWN"),("2026-11-10T13:35:00Z","UP"),("2026-11-12T14:10:00Z","DOWN"),("2026-11-13T01:10:00Z","DOWN"),("2026-11-13T05:35:00Z","DOWN")]:
    s = int(datetime.datetime.fromisoformat(iso.replace("Z","+00:00")).timestamp())
    ev = get(f"https://gamma-api.polymarket.com/events?slug=btc-updown-5m-{s}")
    m = (ev[0]["markets"][0] if isinstance(ev, list) and ev else {})
    o = get(f"https://polymarket.com/api/crypto/crypto-price?symbol=BTC&eventStartTime={iso}&variant=fiveminute")
    print(iso, "| banc :", banc, "| Polymarket :", m.get("outcomes"), m.get("outcomePrices"), "| ouverture/clôture Chainlink :", o.get("openPrice"), o.get("closePrice"), o.get("erreur", ""))
