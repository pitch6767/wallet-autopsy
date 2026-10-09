"""Ou le site Polymarket prend-il le « prix a battre » des les premieres secondes ? (09.10.2026)
Au debut d'un cycle BTC : page du marche (HTML), API gamma (eventMetadata), API crypto-price — a +3, +8, +15, +30, +60 s."""
import json, re, time, urllib.request
def get(url, js=False):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json" if js else "text/html"}), timeout=30) as r:
            b = r.read().decode("utf-8", "replace"); return json.loads(b) if js else b
    except Exception as e: return f"ERREUR {e}"
t = time.time(); st = int(t // 300 * 300) + 300
while time.time() < st + 3: time.sleep(0.5)
iso = lambda x: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(x))
for d in (3, 8, 15, 30, 60):
    while time.time() < st + d: time.sleep(0.3)
    slug = f"btc-updown-5m-{st}"
    h = get(f"https://polymarket.com/event/{slug}")
    champs = sorted(set(re.findall(r'"(priceToBeat|openPrice|closePrice|finalPrice|price_to_beat|startPrice)"\s*:\s*"?([0-9.]+)', h if isinstance(h, str) else "")))
    autour = [h[max(0, m.start() - 150): m.end() + 150] for m in re.finditer(r'(?i)price to beat|priceToBeat', h)][:3] if isinstance(h, str) else []
    g = get(f"https://gamma-api.polymarket.com/events?slug={slug}", js=True)
    meta = None
    if isinstance(g, list) and g:
        e = g[0]; meta = e.get("eventMetadata") or (e.get("markets") or [{}])[0].get("eventMetadata")
    c = get(f"https://polymarket.com/api/crypto/crypto-price?symbol=BTC&eventStartTime={iso(st)}&variant=fiveminute&endDate={iso(st + 300)}", js=True)
    print(f"=== +{d} s ({slug})")
    print("HTML champs:", champs[:20])
    for a in autour: print("HTML autour:", a.replace("\n", " ")[:300])
    print("gamma eventMetadata:", meta)
    print("crypto-price:", c if not isinstance(c, str) else c[:200])
