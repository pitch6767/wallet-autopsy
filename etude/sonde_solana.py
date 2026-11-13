# 13.11.2026 : l'heure dans le nom du marché (slug) = début ou fin du cycle ? (lecture seule)
import json, urllib.request, datetime
def get(u):
    try:
        with urllib.request.urlopen(urllib.request.Request(u, headers={"user-agent": "Mozilla/5.0"}), timeout=60) as r: return json.loads(r.read())
    except Exception as e: return {"erreur": str(e)}
iso_ = lambda t: datetime.datetime.fromtimestamp(t, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
for iso in ["2026-11-10T09:10:00Z", "2026-11-13T01:10:00Z", "2026-11-12T14:10:00Z"]:
    s = int(datetime.datetime.fromisoformat(iso.replace("Z","+00:00")).timestamp())
    ev = get(f"https://gamma-api.polymarket.com/events?slug=btc-updown-5m-{s}")
    e0 = ev[0] if isinstance(ev, list) and ev else {}; m = (e0.get("markets") or [{}])[0]
    print(iso, "| événement :", e0.get("title"), "| startDate", e0.get("startDate"), "| endDate", e0.get("endDate"), "| eventStartTime", m.get("eventStartTime"), "| résultat", m.get("outcomePrices"))
    for dt in (-300, 0, 300):
        o = get(f"https://polymarket.com/api/crypto/crypto-price?symbol=BTC&eventStartTime={iso_(s+dt)}&variant=fiveminute")
        op, cl = o.get("openPrice"), o.get("closePrice")
        print("    crypto-price début", iso_(s+dt), ":", op, cl, "→", ("UP" if cl and op and cl > op else "DOWN" if cl and op else "?"), "| autres champs :", {k: v for k, v in o.items() if k not in ("openPrice", "closePrice")})
