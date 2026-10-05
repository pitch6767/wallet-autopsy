"""Strategie de paires BTC 5 min (idee de Pitch, 05.10.2026), sur les vrais echanges Polymarket.
- Offres d'achat (maker, 0 frais) a X des deux cotes, posees des l'ouverture des ordres => premiers dans la file :
  servies par tout vendeur de cette issue a <= X, ou tout acheteur de l'issue opposee a >= 1-X (appariement Polymarket).
- Option declencheur : achat immediat (taker) de la premiere issue qui s'echange a >= 0,55.
- Des qu'on a 1 Up + 1 Down : fusion => 1 $ (gain bloque). Jambe seule : vente a 0,90 si atteint (taker), sinon reglement.
"""
import sys, json, time, statistics
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, "etude/bot5min")
import test as T

JOURS = int(sys.argv[1]) if len(sys.argv) > 1 else 7
N = 100.0                     # parts par jambe
FEE = lambda p: T.FEE_RATE * p * (1 - p)


def marche(start):
    try:
        ev = T.get(f"{T.G}/events?slug=btc-updown-5m-{start}")
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
    return {"start": start, "end": start + 300, "cid": m["conditionId"], "up_gagne": out[px.index(1.0)].lower() == "up",
            "cree": m.get("createdAt") or e.get("createdAt"), "ordres": m.get("acceptingOrdersTimestamp"), "debut": m.get("startDate") or e.get("startDate")}


def echanges(m):
    res, off, tronque = [], 0, False
    while True:
        lot = T.get(f"{T.D}/trades?market={m['cid']}&limit=500&offset={off}&takerOnly=true")
        if not lot: break
        for t in lot:
            p = float(t["price"]); up = (t.get("outcome") or "").lower() == "up"
            res.append((int(t["timestamp"]), up, p, float(t["size"]), t.get("side")))
        if len(lot) < 500: break
        off += 500
        if off > 9500: tronque = True; break
    res.sort(key=lambda x: x[0])
    return res, tronque


def simuler(m, X, declencheur, sortie90, garder_bid_meme_cote=True):
    """renvoie (pnl, etat) pour un cycle"""
    inv = {True: [], False: []}            # liste de prix de revient par issue (parts de N)
    reste_bid = {True: N, False: N}        # parts encore a acheter par offre maker
    pnl, entre, fini = 0.0, False, False
    etat = "rien"
    for (ts, up, p, size, side) in m["tr"]:
        if ts > m["end"]: break
        if fini: break
        # --- offres maker a X
        for cote in (True, False):
            if reste_bid[cote] <= 0: continue
            touche = (up == cote and side == "SELL" and p <= X + 1e-9) or (up != cote and side == "BUY" and p >= 1 - X - 1e-9)
            if touche:
                q = min(size, reste_bid[cote]); reste_bid[cote] -= q
                inv[cote].append((X, q))
        # --- declencheur 0,55 (achat immediat)
        if declencheur and not entre and ts >= m["start"] and p >= 0.55 and side == "BUY":
            entre = True
            px = max(0.55, p)
            inv[up].append((px, N)); pnl -= N * FEE(px)
            if not garder_bid_meme_cote: reste_bid[up] = 0
        # --- fusion des paires
        qu, qd = sum(q for _, q in inv[True]), sum(q for _, q in inv[False])
        k = min(qu, qd)
        if k > 1e-9:
            for cote in (True, False):
                a_retirer, nouv = k, []
                for (c, q) in inv[cote]:
                    if a_retirer > 0:
                        pris = min(q, a_retirer); pnl -= c * pris; a_retirer -= pris
                        if q - pris > 1e-9: nouv.append((c, q - pris))
                    else: nouv.append((c, q))
                inv[cote] = nouv
            pnl += k          # 1 $ par paire fusionnee
            etat = "paire"
        # --- jambe seule : sortie a 0,90
        if sortie90:
            for cote in (True, False):
                q = sum(qq for _, qq in inv[cote])
                if q > 1e-9 and up == cote and p >= 0.90 and not inv[not cote]:
                    pnl += q * 0.90 - q * FEE(0.90) - sum(c * qq for c, qq in inv[cote]); inv[cote] = []
                    etat = "paire+90" if etat == "paire" else "sortie 90"
                    reste_bid = {True: 0, False: 0}; fini = True
    # --- reglement des jambes restantes
    for cote in (True, False):
        q = sum(qq for _, qq in inv[cote])
        if q > 1e-9:
            gagne = (cote == m["up_gagne"])
            pnl += (q if gagne else 0) - sum(c * qq for c, qq in inv[cote])
            etat = ("paire+" if etat == "paire" else "") + ("jambe gagnee" if gagne else "jambe perdue")
    return pnl, etat


def main():
    t0 = time.time()
    fin = int(time.time()) // 300 * 300 - 900
    debut = fin - JOURS * 86400
    with ThreadPoolExecutor(12) as ex:
        M = sorted([m for m in ex.map(marche, range(debut, fin, 300)) if m], key=lambda m: m["start"])
    print("marches", len(M), "(%.0fs)" % (time.time() - t0)); sys.stdout.flush()
    tron = 0
    def tr(m):
        nonlocal tron
        try:
            m["tr"], t = echanges(m)
            if t: tron += 1
        except Exception:
            m["tr"] = []
        return m
    with ThreadPoolExecutor(10) as ex:
        M = [m for m in ex.map(tr, M) if m["tr"]]
    print("echanges charges (%.0fs), tronques %d" % (time.time() - t0, tron)); sys.stdout.flush()

    rap = [f"# Paires BTC 5 min — {len(M)} cycles sur {JOURS} jours\n",
           f"Ouverture des ordres (exemples) : " + "; ".join(f"cree {m['cree']} / ordres {m['ordres']} / debut cycle {m['debut']}" for m in M[:3]),
           f"\nEchanges avant le debut du cycle : {statistics.mean(sum(1 for x in m['tr'] if x[0] < m['start']) / len(m['tr']) for m in M) * 100:.1f} % en moyenne",
           f"Marches avec historique tronque (>10 000 echanges) : {tron}\n",
           f"Taille : {N:.0f} parts par jambe. Offres maker sans frais ; achats/ventes immediats avec frais 0,072 x p x (1-p).\n",
           "| Strategie | Cycles | Paire (gain bloque) | Sortie 90 | Jambe seule gagnee | Jambe seule perdue | Rien | Gain total | Gain/jour | Pire cycle | Pire baisse |",
           "|---|---|---|---|---|---|---|---|---|---|---|"]
    variantes = [("Pitch : declencheur 55 + offres 40 des 2 cotes, sortie 90", 0.40, True, True),
                 ("Pitch sans sortie 90", 0.40, True, False),
                 ("Declencheur 55 + offres 42", 0.42, True, True),
                 ("Declencheur 55 + offres 45", 0.45, True, True),
                 ("Offres 40 seules, sortie 90", 0.40, False, True),
                 ("Offres 40 seules, sans sortie", 0.40, False, False),
                 ("Offres 42 seules, sortie 90", 0.42, False, True),
                 ("Offres 45 seules, sortie 90", 0.45, False, True),
                 ("Offres 45 seules, sans sortie", 0.45, False, False),
                 ("Offres 48 seules, sans sortie", 0.48, False, False)]
    for nom, X, dec, s90 in variantes:
        R = [simuler(m, X, dec, s90) for m in M]
        c = {}
        for _, e in R:
            k = ("paire" if e.startswith("paire") else e)
            c[k] = c.get(k, 0) + 1
        cum = pic = dd = 0
        for p, _ in R:
            cum += p; pic = max(pic, cum); dd = max(dd, pic - cum)
        n = len(R); pc = lambda k: f"{100 * c.get(k, 0) / n:.1f} %"
        tot = sum(p for p, _ in R)
        rap.append(f"| {nom} | {n} | {pc('paire')} | {pc('sortie 90')} | {pc('jambe gagnee')} | {pc('jambe perdue')} | {pc('rien')} | {tot:+.0f} $ | {tot / JOURS:+.0f} $ | {min(p for p, _ in R):+.0f} $ | -{dd:.0f} $ |")
    rap.append(f"\nDuree : {time.time() - t0:.0f} s")
    open("etude/bot5min/resultat_paires.md", "w").write("\n".join(rap))
    print("\n".join(rap))


if __name__ == "__main__":
    main()
