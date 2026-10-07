"""Detail de 2 portefeuilles (07.10.2026) : a quel moment exact ils achetent (par rapport a la FIN du marche), a quel prix, et combien ca gagne.
stingo43 : achats medians ~4 s APRES la fin du marche 5 min -> achete-t-il apres la fin, quand le resultat est presque connu ?
0xb27bc932 : paire complete en maker (paire mediane 0,923).
"""
import json, sys, time, statistics, collections, urllib.request
sys.path.insert(0, "etude/bot5min")
from portefeuilles import get, resolution, debut, duree, activite, D

CIBLES = {"0x0006af12cd4dacc450836a0e1ec6ce47365d8c63": "stingo43", "0xb27bc932bf8110d8f78e55da7d5f0497a18b5b82": "paire complete 0xb27"}
OUT = "etude/bot5min/"


def taker_ids(w, tmin):
    ids = set()
    for off in range(0, 6000, 500):
        try: lot = get(f"{D}/trades?user={w}&limit=500&offset={off}&takerOnly=true")
        except Exception: break
        for t in lot: ids.add(t.get("transactionHash"))
        if len(lot) < 500 or int(lot[-1]["timestamp"]) < tmin: break
    return ids


def main():
    rap = ["# Detail : moment et prix des achats", ""]
    for w, nom in CIBLES.items():
        ev = [e for e in activite(w, 8000) if e.get("type") == "TRADE" and e.get("side") == "BUY" and "updown" in (e.get("slug") or "")]
        if not ev: rap.append(f"{nom} : rien"); continue
        tmin = min(int(e["timestamp"]) for e in ev); tmax = max(int(e["timestamp"]) for e in ev)
        tk = taker_ids(w, tmin)
        rap += [f"## {nom} ({w})", f"Periode lue : {time.strftime('%d.%m %H:%M', time.gmtime(tmin))} -> {time.strftime('%d.%m %H:%M', time.gmtime(tmax))} UTC, {len(ev)} achats", ""]
        B = collections.defaultdict(lambda: {"n": 0, "usd": 0.0, "gain": 0.0, "gagne": 0, "prix": [], "taker": 0})
        for e in ev:
            slug = e["slug"]; st = debut(slug); d = duree(slug)
            if not st or d != 300: continue
            g = resolution(slug)
            if g is None: continue
            rel = int(e["timestamp"]) - (st + d)          # secondes par rapport a la FIN (negatif = avant)
            if rel < -240: k = "plus de 4 min avant la fin"
            elif rel < -60: k = "1-4 min avant la fin"
            elif rel < -10: k = "10-60 s avant la fin"
            elif rel < 0: k = "0-10 s avant la fin"
            elif rel < 5: k = "0-5 s APRES la fin"
            elif rel < 30: k = "5-30 s APRES la fin"
            else: k = "plus de 30 s APRES la fin"
            p = float(e["price"]); sz = float(e["size"]); usd = float(e.get("usdcSize") or p * sz)
            ok = (e.get("outcome") or "").lower() == g.lower()
            b = B[k]; b["n"] += 1; b["usd"] += usd; b["gain"] += (sz if ok else 0) - usd; b["gagne"] += ok; b["prix"].append(p)
            b["taker"] += e.get("transactionHash") in tk
        ordre = ["plus de 4 min avant la fin", "1-4 min avant la fin", "10-60 s avant la fin", "0-10 s avant la fin", "0-5 s APRES la fin", "5-30 s APRES la fin", "plus de 30 s APRES la fin"]
        rap += ["Marches 5 min seulement. Gain = parts gagnantes x 1 $ - prix paye (garde jusqu'au resultat).", "",
                "| Moment de l'achat | Achats | Mise | Cote achete gagne | Prix median | Gain | Gain / mise | En taker |", "|---|---|---|---|---|---|---|---|"]
        for k in ordre:
            b = B.get(k)
            if not b or not b["n"]: continue
            rap.append(f"| {k} | {b['n']} | {b['usd']:.0f} $ | {100 * b['gagne'] / b['n']:.0f} % | {statistics.median(b['prix']):.2f} | {b['gain']:+.0f} $ | {100 * b['gain'] / max(b['usd'], 1):+.1f} % | {100 * b['taker'] / b['n']:.0f} % |")
        # prix x issue pour les achats apres la fin
        apres = [e for e in ev if debut(e["slug"]) and duree(e["slug"]) == 300 and int(e["timestamp"]) >= debut(e["slug"]) + 300 and resolution(e["slug"]) is not None]
        if apres:
            rap += ["", "Achats APRES la fin, par prix :", "", "| Prix | Achats | Gagne | Gain / mise |", "|---|---|---|---|"]
            for lo, hi in ((0, 0.1), (0.1, 0.3), (0.3, 0.5), (0.5, 0.7), (0.7, 0.9), (0.9, 1.01)):
                X = [e for e in apres if lo <= float(e["price"]) < hi]
                if not X: continue
                usd = sum(float(e.get("usdcSize") or 0) for e in X); gain = sum((float(e["size"]) if (e.get("outcome") or "").lower() == resolution(e["slug"]).lower() else 0) - float(e.get("usdcSize") or 0) for e in X)
                rap.append(f"| {lo:.1f}-{hi:.1f} | {len(X)} | {100 * sum((e.get('outcome') or '').lower() == resolution(e['slug']).lower() for e in X) / len(X):.0f} % | {100 * gain / max(usd, 1):+.1f} % |")
        rap.append("")
        open(OUT + "resultat_portefeuilles_detail.md", "w").write("\n".join(rap))
    print("\n".join(rap))


if __name__ == "__main__":
    main()
