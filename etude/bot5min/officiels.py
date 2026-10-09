"""Valeurs officielles (priceToBeat, finalPrice, gagnant) de tous les cycles BTC/ETH enregistres (07.10 -> maintenant), via l'API gamma Polymarket."""
import json, gzip, glob, os, time, urllib.request
def get(u):
    for k in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=30) as r: return json.loads(r.read())
        except Exception as e: err = e; time.sleep(2)
    return None
out = {}
f = "bot95/officiels.json"
if os.path.exists(f): out = json.load(open(f))
sts = set()
for fic in glob.glob("bot95/donnees/*/rec_BTC.json.gz"):
    for k in json.load(gzip.open(fic, "rt")): sts.add(int(k.split(":")[2]) * 60 // 300 * 300)
fin = int(time.time() // 300 * 300) - 900
sts = sorted(s for s in sts | set(range(min(sts), fin, 300)) if s <= fin)
n = 0
for a in ("BTC", "ETH"):
    for st in sts:
        k = f"{a}:{st}"
        if k in out and out[k].get("ptb") is not None and out[k].get("gagnant"): continue
        ev = get(f"https://gamma-api.polymarket.com/events?slug={a.lower()}-updown-5m-{st}")
        if not ev: continue
        e = ev[0]; m = (e.get("markets") or [{}])[0]
        meta = e.get("eventMetadata") or m.get("eventMetadata") or {}
        if isinstance(meta, str): meta = json.loads(meta)
        try: px = [float(x) for x in json.loads(m.get("outcomePrices") or "[]")]; outs = json.loads(m.get("outcomes") or "[]")
        except Exception: px, outs = [], []
        g = outs[px.index(1.0)] if 1.0 in px and 0.0 in px else None
        out[k] = {"ptb": meta.get("priceToBeat"), "final": meta.get("finalPrice"), "gagnant": g}
        n += 1; time.sleep(0.05)
json.dump(out, open(f, "w"))
print(len(out), "cycles,", n, "nouveaux")
