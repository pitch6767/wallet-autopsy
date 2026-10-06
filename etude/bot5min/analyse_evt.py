"""Analyse de l'enregistreur au message pres (idee 3) : qui mene a 50-200 ms pres, et combien de temps un vendeur « en retard » reste disponible.
Choc = une source bouge d'au moins X pb en moins de 500 ms. On mesure :
 - le retard avant que le meilleur prix Polymarket du jeton favorise par le choc bouge (milieu +1 cent dans le bon sens) ;
 - combien de temps le meilleur VENDEUR du jeton favorise reste au prix d'avant le choc (fenetre pour l'acheter) ;
 - la part des chocs ou Polymarket a bouge AVANT la source (Polymarket mene).
"""
import json, sys, time, statistics, collections, urllib.request, bisect

U = "https://bot95.pitch67.workers.dev"
OUT = "etude/bot5min/"


def get(url):
    err = None
    for k in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "analyse"}), timeout=60) as r: return json.loads(r.read())
        except Exception as e: err = e; time.sleep(2)
    raise err


def charger():
    ev, apres = [], None
    while True:
        d = get(f"{U}/api/evt?n=80" + (f"&apres={apres}" if apres else ""))
        for doc in d["docs"]: ev += doc
        if not d["cles"] or len(d["cles"]) < 80: break
        apres = d["suivant"]
    ev.sort(key=lambda x: x[0])
    return ev


def main():
    E = charger()
    rap = [f"# Enregistreur au message pres — {len(E)} evenements", ""]
    if len(E) < 1000:
        open(OUT + "resultat_evt.md", "w").write("\n".join(rap + ["Pas assez de donnees."])); return
    rap.append(f"Periode : {time.strftime('%d.%m %H:%M', time.gmtime(E[0][0] / 1000))} -> {time.strftime('%d.%m %H:%M', time.gmtime(E[-1][0] / 1000))} UTC (10 min par heure)\n")
    for A in ("B", "E"):
        nom = "BTC" if A == "B" else "ETH"
        src = {k: [(e[0], e[2]) for e in E if e[1] == A + k] for k in ("p", "o", "n", "c", "l")}
        noms = {"p": "Bybit perp", "o": "OKX perp", "n": "Binance spot", "c": "Coinbase", "l": "Chainlink"}
        up = [(e[0], e[2], e[3]) for e in E if e[1] == A + "U" and e[2] is not None and e[3] is not None]
        dn = [(e[0], e[2], e[3]) for e in E if e[1] == A + "D" and e[2] is not None and e[3] is not None]
        if len(up) < 200: rap.append(f"## {nom} : pas assez de carnets"); continue
        tu = [x[0] for x in up]; td = [x[0] for x in dn]
        def etat(serie, ts_, t):
            i = bisect.bisect_right(ts_, t) - 1
            return serie[i] if i >= 0 else None
        rap += [f"## {nom}\n", "| Source du choc | Seuil | Chocs | Polymarket bouge en moyenne apres | Mediane | 90 % des cas avant | Polymarket avait deja bouge (il mene) | Vendeur en retard encore la apres 50 ms | apres 150 ms | apres 300 ms | Duree mediane du vendeur en retard |",
                "|---|---|---|---|---|---|---|---|---|---|---|"]
        for k, serie in src.items():
            if len(serie) < 50: continue
            ts_s = [x[0] for x in serie]
            for seuil in (2, 4, 8):
                chocs, dernier = [], -1e18
                j = 0
                for i, (t, p) in enumerate(serie):
                    while ts_s[j] < t - 500: j += 1
                    p0 = serie[j][1]
                    mv = (p / p0 - 1) * 1e4
                    if abs(mv) >= seuil and t - dernier > 3000:
                        chocs.append((t, 1 if mv > 0 else -1)); dernier = t
                delais, avant, dispo50, dispo150, dispo300, durees = [], 0, 0, 0, 0, []
                for (t, s) in chocs:
                    # jeton favorise : Up si hausse, Down si baisse
                    serie_pm, ts_pm = (up, tu) if s > 0 else (dn, td)
                    e0 = etat(serie_pm, ts_pm, t)
                    if not e0: continue
                    mid0 = (e0[1] + e0[2]) / 2; ask0 = e0[2]
                    # Polymarket a-t-il deja bouge dans les 500 ms AVANT le choc ?
                    e_av = etat(serie_pm, ts_pm, t - 500)
                    if e_av and (e_av[1] + e_av[2]) / 2 <= mid0 - 0.01: avant += 1
                    # retard de reaction : premier instant ou le milieu monte d'1 cent
                    i0 = bisect.bisect_right(ts_pm, t)
                    d = None
                    for x in serie_pm[i0:i0 + 400]:
                        if x[0] - t > 10000: break
                        if (x[1] + x[2]) / 2 >= mid0 + 0.01: d = x[0] - t; break
                    if d is not None: delais.append(d)
                    # duree pendant laquelle le meilleur vendeur reste <= ask d'avant le choc
                    fin_ = None
                    for x in serie_pm[i0:i0 + 400]:
                        if x[2] > ask0 + 1e-9: fin_ = x[0] - t; break
                        if x[0] - t > 10000: fin_ = 10000; break
                    fin_ = fin_ if fin_ is not None else 10000
                    durees.append(fin_)
                    dispo50 += fin_ > 50; dispo150 += fin_ > 150; dispo300 += fin_ > 300
                n = len(durees)
                if n < 10: continue
                q90 = sorted(delais)[int(len(delais) * 0.9)] if delais else None
                rap.append(f"| {noms[k]} | {seuil} pb / 0,5 s | {n} | {statistics.mean(delais):.0f} ms | {statistics.median(delais):.0f} ms | {q90} ms | {100 * avant / n:.0f} % | {100 * dispo50 / n:.0f} % | {100 * dispo150 / n:.0f} % | {100 * dispo300 / n:.0f} % | {statistics.median(durees):.0f} ms |" if delais else f"| {noms[k]} | {seuil} pb | {n} | — | | | | | | | |")
        rap.append("")
    open(OUT + "resultat_evt.md", "w").write("\n".join(rap))
    print("\n".join(rap))


if __name__ == "__main__":
    main()
