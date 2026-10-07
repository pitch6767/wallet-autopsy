"""Se rapprocher du +6 404 $ (achat a l'entree des desaccords ou Polymarket rejoint ensuite le modele) — 07.10.2026.
Vrais carnets du bot (48 h, 4 mesures/s, sans sous-echantillonnage). Desaccord = 1er instant du cycle et du cote ou modele - meilleur vendeur >= 0,20.
Familles de regles, toutes CAUSALES (on n'utilise que ce qui est connu au moment de la decision) :
 A. ACHAT IMMEDIAT + SORTIE si le desaccord se revele faux : a h s, si le modele a baisse de >= 3 c (ou si Polymarket n'a pas monte), on revend au meilleur acheteur.
 B. ACHAT DES LES PREMIERS SIGNES : on achete au 1er instant (dans W s) ou Polymarket a monte de >= x c vers le modele, modele stable.
 C. FILTRE A L'ENTREE : bourses (Binance / perp / OKX / Coinbase) dans notre sens sur 3 s, puis achat immediat.
 D. C + A.
Resultat pour 50 $, frais compris, 1re / 2e moitie, et sans les 3 meilleurs trades.
"""
import sys, json, statistics, collections, itertools
sys.path.insert(0, "etude/bot5min")
import sauvetage as SV
from sauvetage import resultat, RES, FEE, get, U

OUT = "etude/bot5min/"
E = 0.20


def charger_brut(a):
    L, apres = [], None
    while True:
        d = get(f"{U}/api/rec?a={a}&n=60" + (f"&apres={apres}" if apres else ""))
        for doc in d["docs"]: L += doc["lignes"]
        if not d["cles"] or len(d["cles"]) < 60: break
        apres = d["suivant"]
    L.sort(key=lambda r: r[0])
    C = collections.defaultdict(list)
    for r in L:
        if None in (r[2], r[3], r[4], r[5], r[6]): continue
        C[r[1]].append(r)
    return C


def evenements(A, C):
    out = []
    for st in sorted(C):
        R = C[st]; g = RES.get((A, st))
        if g is None: continue
        for up in (True, False):
            for i, r in enumerate(R):
                tl = st + 300 - r[0]
                if tl < 15: break
                ask = r[4] if up else r[6]
                fair = r[2] if up else 1 - r[2]
                if not (0.03 <= ask <= 0.97) or fair - ask < E: continue
                sg = 1 if up else -1
                j = i
                while j > 0 and r[0] - R[j][0] < 3: j -= 1
                h3 = R[j] if r[0] - R[j][0] >= 2.5 else None
                d = lambda c: ((r[c] - h3[c]) * sg) if h3 and h3[c] and r[c] else 0.0
                # chemin apres l'entree : (dt, fair, mid, ask, bid, taille bid)
                ch = []
                for x in R[i + 1:]:
                    dt = x[0] - r[0]
                    if dt > 60: break
                    ch.append((dt, x[2] if up else 1 - x[2], (x[3] + x[4]) / 2 if up else (x[5] + x[6]) / 2,
                               x[4] if up else x[6], x[3] if up else x[5], (x[7] if up else x[9]) or 0))
                out.append({"st": st, "ask": ask, "fair": fair, "mid": (r[3] + r[4]) / 2 if up else (r[5] + r[6]) / 2,
                            "gm": g if up else (not g), "ch": ch, "bn": d(14), "perp": d(11), "okx": d(12), "cb": d(13)})
                break
    return out


def pnl_tenir(p, gm): return (50 / p) * ((1 if gm else 0) - p - FEE(p))
def pnl_vendre(p, b, z):
    parts = 50 / p
    bx = b if z >= parts / 2 else b - 0.01
    return parts * (max(bx, 0.0) - FEE(max(bx, 0.0))) - parts * (p + FEE(p))


def regle_A(e, h, mode):
    """achat immediat ; a h s : sortie si faux. mode 'retombe' = modele -3 c ; 'pas_rejoint' = Poly n'a pas monte de 3 c ; 'les_deux' = l'un ou l'autre."""
    pt = next((x for x in e["ch"] if x[0] >= h), None)
    if pt is None: return pnl_tenir(e["ask"], e["gm"])
    _, f2, m2, a2, b2, z2 = pt
    retombe = f2 - e["fair"] <= -0.03; rejoint = m2 - e["mid"] >= 0.03
    sortir = {"retombe": retombe and not rejoint, "pas_rejoint": not rejoint, "les_deux": retombe or not rejoint}[mode]
    return pnl_vendre(e["ask"], b2, z2) if sortir and b2 is not None else pnl_tenir(e["ask"], e["gm"])


def regle_B(e, W, x):
    for dt, f2, m2, a2, b2, z2 in e["ch"]:
        if dt > W: return None
        if m2 - e["mid"] >= x and f2 - e["fair"] > -0.03 and a2 is not None and 0.03 <= a2 <= 0.97 and f2 - a2 > 0:
            return pnl_tenir(a2, e["gm"])
    return None


FILTRES = {"aucun": lambda e: True, "Binance avec nous": lambda e: e["bn"] > 0, "perp avec nous": lambda e: e["perp"] > 0,
           "Binance ou perp avec nous": lambda e: e["bn"] > 0 or e["perp"] > 0, "Binance et perp >= 0": lambda e: e["bn"] >= 0 and e["perp"] >= 0,
           "3 bourses sur 4 avec nous": lambda e: sum(v > 0 for v in (e["bn"], e["perp"], e["okx"], e["cb"])) >= 3,
           "aucune bourse contre nous": lambda e: min(e["bn"], e["perp"], e["okx"], e["cb"]) >= 0}


def ligne(nom, X, mi):
    X = [(s, p) for s, p in X if p is not None]
    if not X: return f"| {nom} | 0 | | | | | |"
    a = sum(p for s, p in X if s < mi); b = sum(p for s, p in X if s >= mi); P = sorted((p for s, p in X), reverse=True)
    return f"| {nom} | {len(X)} | {a:+.0f} $ | {b:+.0f} $ | **{a + b:+.0f} $** | {(a + b) / len(X):+.1f} $ | {sum(P[3:]):+.0f} $ |"


def main():
    rap = ["# Se rapprocher de l'achat a l'entree des « vrais » desaccords — vrais carnets du bot, 4 mesures/s", "",
           "Toutes les regles sont causales (decision avec ce qu'on sait a ce moment-la). 50 $ par trade, frais compris. « Sans top 3 » = resultat sans les 3 meilleurs trades.", ""]
    H = "| Regle | Trades | 1re moitie | 2e moitie | **Total** | Par trade | Sans top 3 |\n|---|---|---|---|---|---|---|"
    for A in ("BTC", "ETH"):
        C = charger_brut(A); sts = sorted(C)
        for st in sts: resultat(A, st)
        EV = evenements(A, C); mi = sts[len(sts) // 2]
        rap += [f"## {A} — {len(EV)} desaccords >= 0,20", "", H]
        base = [(e["st"], pnl_tenir(e["ask"], e["gm"])) for e in EV]
        rap.append(ligne("REFERENCE : tout acheter a l'entree, garder", base, mi))
        rap += ["", "### A. Achat immediat, sortie au meilleur acheteur si le desaccord se revele faux", "", H]
        for mode, lab in (("retombe", "modele -3 c"), ("pas_rejoint", "Poly n'a pas monte de 3 c"), ("les_deux", "modele -3 c OU Poly pas monte")):
            for h in (1, 2, 3, 5, 10):
                rap.append(ligne(f"sortie a {h} s si {lab}", [(e["st"], regle_A(e, h, mode)) for e in EV], mi))
        rap += ["", "### B. Achat aux premiers signes (Polymarket monte de x c vers le modele, modele stable, dans les W s)", "", H]
        for W in (1, 2, 3, 5, 10):
            for x in (0.01, 0.02, 0.03, 0.05):
                rap.append(ligne(f"W {W} s, x {round(100 * x)} c", [(e["st"], regle_B(e, W, x)) for e in EV], mi))
        rap += ["", "### C. Filtre bourses a l'entree (3 s avant), achat immediat, garder", "", H]
        for nom, f in FILTRES.items():
            rap.append(ligne(nom, [(e["st"], pnl_tenir(e["ask"], e["gm"])) for e in EV if f(e)], mi))
        rap += ["", "### D. Filtre bourses + sortie si faux", "", H]
        for nom in ("Binance ou perp avec nous", "aucune bourse contre nous", "3 bourses sur 4 avec nous"):
            for mode, h in (("retombe", 3), ("retombe", 5), ("les_deux", 5), ("pas_rejoint", 10)):
                rap.append(ligne(f"{nom} + sortie {h} s ({mode})", [(e["st"], regle_A(e, h, mode)) for e in EV if FILTRES[nom](e)], mi))
        rap.append("")
        open(OUT + "resultat_proche.md", "w").write("\n".join(rap))
    print("\n".join(rap))


if __name__ == "__main__":
    main()
