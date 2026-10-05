"""Arbitrage 15 min contre 5 min (idee de Pitch, 05.10.2026), vrais echanges Polymarket.
Les 5 dernieres minutes d'un marche 15 min et le marche 5 min qui commence 10 min apres se reglent sur la MEME moyenne Chainlink finale F.
15 min : Up si F >= K15 ; 5 min : Up si F >= K5 (K = moyenne d'ouverture de chaque marche, publiee par Polymarket).
Si K15 < K5 : acheter 15m Up + 5m Down => paie 1 si F >= K5 ou F < K15, et 2 si K15 <= F < K5 (jamais 0).
Si K15 > K5 : acheter 15m Down + 5m Up (symetrique).
Prix d'achat = prix des derniers ACHATS reels (vus dans les 3 dernieres secondes) ; frais taker 0,072 x p x (1-p) par jambe.
"""
import sys, json, time, statistics
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, "etude/bot5min")
import test as T
import paires as P

JOURS = int(sys.argv[1]) if len(sys.argv) > 1 else 7
PREFIXE = sys.argv[2] if len(sys.argv) > 2 else "btc"
FEE = lambda p: T.FEE_RATE * p * (1 - p)


def marche(duree, start):
    try:
        ev = T.get(f"{T.G}/events?slug={PREFIXE}-updown-{duree}-{start}")
    except Exception:
        return None
    if not ev: return None
    e = ev[0]; m = (e.get("markets") or [None])[0]
    if not m: return None
    try:
        out = json.loads(m.get("outcomes") or "[]"); px = [float(x) for x in json.loads(m.get("outcomePrices") or "[]")]
    except Exception:
        return None
    if sorted(px) != [0.0, 1.0]: return None
    meta = e.get("eventMetadata") or m.get("eventMetadata") or {}
    if isinstance(meta, str):
        try: meta = json.loads(meta)
        except Exception: meta = {}
    if meta.get("priceToBeat") is None: return None
    return {"start": start, "cid": m["conditionId"], "up_gagne": out[px.index(1.0)].lower() == "up", "K": float(meta["priceToBeat"]),
            "F": float(meta["finalPrice"]) if meta.get("finalPrice") is not None else None}


def paire(s15):
    a = marche("15m", s15); b = marche("5m", s15 + 600)
    if not a or not b: return None
    try:
        a["tr"], _ = P.echanges({"cid": a["cid"]}); b["tr"], _ = P.echanges({"cid": b["cid"]})
    except Exception:
        return None
    return a, b


def main():
    t0 = time.time()
    fin = int(time.time()) // 900 * 900 - 1800
    debut = fin - JOURS * 86400
    with ThreadPoolExecutor(8) as ex:
        Z = [z for z in ex.map(paire, range(debut, fin, 900)) if z]
    print(PREFIXE, "paires", len(Z), "(%.0fs)" % (time.time() - t0)); sys.stdout.flush()
    rows, ecarts = [], []
    for a, b in Z:
        fin_c = b["start"] + 300
        if a["K"] == b["K"]: continue
        bas15 = a["K"] < b["K"]                  # vrai : acheter 15m Up + 5m Down
        ecarts.append(abs(a["K"] - b["K"]) / a["K"])
        # dernier ACHAT vu par seconde pour chaque jambe voulue (prix, taille)
        def serie(m, want_up):
            d = {}
            for (ts, up, p, size, side) in m["tr"]:
                if ts < b["start"] or ts > fin_c - 1 or side != "BUY": continue
                if up == want_up: d[ts] = (p, size)
                else: d[ts] = (None, 0)          # achat de l'autre issue : on ne connait pas l'ask de la notre
            return d
        A = serie(a, bas15); B = serie(b, not bas15)
        lastA = lastB = None; meilleur = None; premier = None
        for s in range(b["start"], fin_c):
            if s in A and A[s][0] is not None: lastA = (s, *A[s])
            if s in B and B[s][0] is not None: lastB = (s, *B[s])
            if not lastA or not lastB or s - lastA[0] > 3 or s - lastB[0] > 3: continue
            pa, pb = lastA[1], lastB[1]
            cout = pa + pb + FEE(pa) + FEE(pb)
            if meilleur is None or cout < meilleur[0]: meilleur = (cout, s, pa, pb, min(lastA[2], lastB[2]))
            if premier is None and cout < 1: premier = (cout, s, pa, pb, min(lastA[2], lastB[2]))
        if meilleur is None: continue
        # paiement reel
        F = b["F"] if b["F"] is not None else a["F"]
        jA = a["up_gagne"] if bas15 else not a["up_gagne"]      # notre jambe 15 min gagne ?
        jB = (not b["up_gagne"]) if bas15 else b["up_gagne"]    # notre jambe 5 min gagne ?
        paie = int(jA) + int(jB)
        rows.append({"meilleur": meilleur, "premier": premier, "paie": paie, "ecart": abs(a["K"] - b["K"]) / a["K"], "fin": fin_c})
    n = len(rows)
    sans = [r for r in rows if r["premier"]]
    gain_sur = sum((1 - r["premier"][0]) * min(100, r["premier"][4]) for r in sans)
    gain_reel = sum((r["paie"] - r["premier"][0]) * min(100, r["premier"][4]) for r in sans)
    # strategie « esperance » : acheter au meilleur prix du cycle si cout < seuil, paiement reel (1 ou 2)
    rap = [f"## {PREFIXE.upper()} — {len(Z)} paires 15 min / 5 min sur {JOURS} jours (fenetre : 5 dernieres minutes)\n",
           f"Ecart median entre les deux prix d'exercice : {statistics.median(ecarts) * 100:.3f} % du prix",
           f"Cycles avec prix des deux jambes observables : {n}",
           f"**Cycles avec un moment SANS RISQUE (cout + frais < 1,00) : {len(sans)} ({100 * len(sans) / max(1, n):.1f} %)**",
           f"Gain sans risque (premier moment, taille limitee aux echanges vus, max 100 parts) : {gain_sur:+.1f} $ sur {JOURS} jours, soit {gain_sur / JOURS:+.1f} $/jour",
           f"Gain reel de ces memes achats (bonus quand les deux jambes gagnent) : {gain_reel:+.1f} $ sur {JOURS} jours",
           f"Taille mediane disponible au moment sans risque : {statistics.median([r['premier'][4] for r in sans]) if sans else 0:.0f} parts",
           f"Cout + frais le plus bas observe, mediane par cycle : {statistics.median([r['meilleur'][0] for r in rows]) if rows else 0:.3f}",
           f"Les deux jambes gagnent (paie 2) : {sum(1 for r in rows if r['paie'] == 2)} cycles sur {n} ({100 * sum(1 for r in rows if r['paie'] == 2) / max(1, n):.1f} %)\n",
           "| Seuil d'achat (cout + frais) | Cycles achetes | Gain reel 100 parts | Gain/jour | Pire cycle |", "|---|---|---|---|---|"]
    for seuil in (0.98, 1.00, 1.02, 1.05, 1.10):
        L = [r for r in rows if r["meilleur"][0] < seuil]
        g = [(r["paie"] - r["meilleur"][0]) * 100 for r in L]
        rap.append(f"| < {seuil:.2f} | {len(L)} | {sum(g):+.0f} $ | {sum(g) / JOURS:+.0f} $ | {min(g, default=0):+.0f} $ |")
    rap.append("\n(Le tableau achete au MEILLEUR prix du cycle : c'est un plafond optimiste, connu seulement apres coup.)")
    rap.append(f"\nDuree : {time.time() - t0:.0f} s")
    open(f"etude/bot5min/resultat_arb15_{PREFIXE}.md", "w").write("\n".join(rap))
    print("\n".join(rap))


if __name__ == "__main__":
    main()
