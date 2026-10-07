"""Est-ce qu'on peut encore acheter APRES la fin d'un marche 5 min (07.10.2026) ?
stingo43 gagnait +38 a +80 % en achetant 0-30 s apres la fin (avril 2026). On verifie sur les marches recents BTC/ETH 5 min :
echanges apres la fin, a quel prix, le cote achete gagne-t-il, et qui achete. + activite recente de stingo43 (tri du plus recent).
"""
import json, sys, time, statistics, collections
sys.path.insert(0, "etude/bot5min")
from portefeuilles import get, resolution, D, G

OUT = "etude/bot5min/"


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 150
    maintenant = int(time.time()) // 300 * 300
    rap = ["# Achats apres la fin d'un marche 5 min — marches recents", ""]
    for a in ("btc", "eth"):
        B = collections.defaultdict(lambda: {"n": 0, "usd": 0.0, "gain": 0.0, "ok": 0})
        acheteurs = collections.Counter(); marches_avec = 0; total = 0
        for k in range(3, 3 + n):
            st = maintenant - 300 * k; slug = f"{a}-updown-5m-{st}"
            try:
                ev = get(f"{G}/events?slug={slug}"); m = ev[0]["markets"][0]; cid = m["conditionId"]
                out = json.loads(m["outcomes"]); px = [float(x) for x in json.loads(m["outcomePrices"])]
                if sorted(px) != [0.0, 1.0]: continue
                g = out[px.index(1.0)].lower()
            except Exception: continue
            total += 1; vu = False
            for off in (0, 500, 1000, 1500):
                try: lot = get(f"{D}/trades?market={cid}&limit=500&offset={off}&takerOnly=true")
                except Exception: break
                for t in lot:
                    rel = int(t["timestamp"]) - (st + 300)
                    if rel < -10: continue
                    k2 = "0-10 s avant la fin" if rel < 0 else ("0-5 s apres" if rel < 5 else ("5-30 s apres" if rel < 30 else "plus de 30 s apres"))
                    if rel >= 0: vu = True
                    p = float(t["price"]); sz = float(t["size"]); side = t.get("side"); oc = (t.get("outcome") or "").lower()
                    # l'acheteur detient 'oc' s'il achete, l'autre cote s'il vend
                    tient = oc if side == "BUY" else ("down" if oc == "up" else "up")
                    cout = p * sz if side == "BUY" else (1 - p) * sz
                    b = B[k2]; b["n"] += 1; b["usd"] += cout; b["gain"] += (sz if tient == g else 0) - cout; b["ok"] += tient == g
                    if rel >= 0: acheteurs[t.get("proxyWallet")] += 1
                if len(lot) < 500 or int(lot[-1]["timestamp"]) < st + 290: break
            marches_avec += vu
        rap += [f"## {a.upper()} : {total} marches recents, {marches_avec} avec des echanges APRES la fin", "",
                "| Moment (taker) | Echanges | Mise | Cote pris gagne | Gain | Gain / mise |", "|---|---|---|---|---|---|"]
        for k2 in ("0-10 s avant la fin", "0-5 s apres", "5-30 s apres", "plus de 30 s apres"):
            b = B.get(k2)
            if b and b["n"]: rap.append(f"| {k2} | {b['n']} | {b['usd']:.0f} $ | {100 * b['ok'] / b['n']:.0f} % | {b['gain']:+.0f} $ | {100 * b['gain'] / max(b['usd'], 1):+.1f} % |")
        rap += ["", "Qui prend apres la fin : " + ", ".join(f"{w[:10]}… {c}" for w, c in acheteurs.most_common(6)), ""]
        open(OUT + "resultat_apres_fin.md", "w").write("\n".join(rap))
    # stingo43 recemment
    try:
        lot = get(f"{D}/activity?user=0x0006af12cd4dacc450836a0e1ec6ce47365d8c63&limit=500&sortBy=TIMESTAMP&sortDirection=DESC")
        ts = [int(e["timestamp"]) for e in lot]
        rap.append(f"stingo43 : derniere activite {time.strftime('%d.%m.%Y %H:%M', time.gmtime(max(ts)))} UTC ({len(lot)} lignes lues, la plus ancienne {time.strftime('%d.%m.%Y', time.gmtime(min(ts)))})" if ts else "stingo43 : aucune activite recente")
    except Exception as e:
        rap.append(f"stingo43 : erreur {e}")
    open(OUT + "resultat_apres_fin.md", "w").write("\n".join(rap))
    print("\n".join(rap))


if __name__ == "__main__":
    main()
