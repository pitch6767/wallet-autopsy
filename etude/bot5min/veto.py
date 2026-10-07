"""Moteur fantome V2 teste sur 12 jours d'historique (07.10.2026) — memes variantes que dans le bot, parametres FIGES :
A tel quel · B hors 60-89 s · C perp (5 s) · D perp + 120-269 s · E persistant (l'ecart tient 2 s, entree 2 s plus tard) ·
F ecart qui grandit (+3 pts sur 3 s) · G jury (spot dans notre sens sur 3 s + Polymarket en retard sur le modele) · H veto complet.
+ decoupage loterie (< 0,10) / confirmation (0,15-0,40). KPI : gain moyen par trade de 50 $ (pas le % de gagnants).
Choix sur j1-8, verification j9-12, et nombre de jours positifs.
"""
import sys, time, statistics, collections
import numpy as np
from datetime import datetime, timezone
sys.argv = [sys.argv[0], sys.argv[1] if len(sys.argv) > 1 else "12"]
sys.path.insert(0, "etude/bot5min")
import combinaisons as CB

OUT = "etude/bot5min/"
FEE = lambda p: 0.072 * p * (1 - p)


def achat(c, k, cote_up, prix_max):
    X = c["bu"] if cote_up else c["bd"]
    if k + 2 >= len(X): return None
    f_ = min(X[k + 1], X[k + 2])
    return f_ if f_ <= prix_max + 1e-9 else None


def evenements(D, A, E):
    out = []
    for st, c in D[A].items():
        up, pm, vu, sp = c["up"], c["pm"], c["vu"], c["sp"]
        for k in range(5, 290):
            if vu[k] < k - 3 or np.isnan(pm[k]) or np.isnan(up[k]): continue
            ec = pm[k] - up[k]
            if abs(ec) < E: continue
            s = 1 if ec > 0 else -1; cote_up = ec > 0
            prixm = (up[k] if cote_up else 1 - up[k]) + 0.01
            f_ = achat(c, k, cote_up, prixm)
            if f_ is None or not (0.03 <= f_ <= 0.97): continue   # pas de vendeur reel a ce prix : on continue de chercher
            edge = lambda j: (pm[j] - up[j]) * s
            d = lambda arr, n: (arr[k] - arr[k - n]) * s if k >= n and not np.isnan(arr[k - n]) and not np.isnan(arr[k]) else 0.0
            tl = 300 - k
            perp5, sp3 = d(sp, 5), d(sp, 3)
            grandit = k >= 3 and edge(k) - edge(k - 3) >= 0.03
            fond = k >= 3 and edge(k) - edge(k - 3) < -0.02
            retard = k >= 3 and d(pm, 3) - d(up, 3) >= 0.03
            corrige = k >= 5 and d(up, 5) >= max(0.05, edge(k) / 2)
            # persistance : l'ecart tient encore 2 s plus tard -> entree a k+2
            f_pers = None
            if k + 4 < 300 and all(not np.isnan(pm[j]) and edge(j) >= E for j in (k + 1, k + 2)):
                f_pers = achat(c, k + 2, cote_up, (up[k + 2] if cote_up else 1 - up[k + 2]) + 0.01)
            gagne = (c["g"] == 1) == cote_up
            pnl = lambda p: ((1 if gagne else 0) - p - FEE(p)) * 50 / p
            out.append({"st": st, "tl": tl, "prix": f_, "g": gagne, "pnl": pnl(f_), "pnl_pers": None if f_pers is None else pnl(f_pers),
                        "perp": perp5 >= 0, "sp3": sp3, "grandit": grandit, "fond": fond, "retard": retard, "corrige": corrige})
            break
    return out


def main():
    J_ = CB.JOURS
    fin = int(time.time()) // 86400 * 86400 - 300
    debut = fin + 300 - J_ * 86400
    jours = sorted({datetime.fromtimestamp(t, timezone.utc).strftime("%Y-%m-%d") for t in range(debut - 3700, fin + 600, 3600)})
    jours = [j for j in jours if j < datetime.now(timezone.utc).strftime("%Y-%m-%d")]
    coupe = debut + int(J_ * 2 / 3) * 86400
    D = {"btc": CB.preparer("btc", "BTCUSDT", jours, debut, fin, coupe), "eth": CB.preparer("eth", "ETHUSDT", jours, debut, fin, coupe)}
    V = {
        "A tel quel": lambda e: e["pnl"],
        "B hors 60-89 s": lambda e: None if 60 <= e["tl"] < 90 else e["pnl"],
        "C perp": lambda e: e["pnl"] if e["perp"] else None,
        "D perp + 120-269 s": lambda e: e["pnl"] if e["perp"] and 120 <= e["tl"] <= 269 else None,
        "E persistant 2 s": lambda e: e["pnl_pers"],
        "F ecart qui grandit": lambda e: e["pnl"] if e["grandit"] else None,
        "G jury (spot + retard Polymarket)": lambda e: e["pnl"] if e["sp3"] >= 0 and e["retard"] else None,
        "H veto complet": lambda e: None if (e["fond"] or e["sp3"] < 0 or 60 <= e["tl"] < 90 or e["corrige"]) else e["pnl"],
        "C+F perp + grandit": lambda e: e["pnl"] if e["perp"] and e["grandit"] else None,
        "C+G perp + jury": lambda e: e["pnl"] if e["perp"] and e["sp3"] >= 0 and e["retard"] else None,
        "H + perp": lambda e: None if (not e["perp"] or e["fond"] or e["sp3"] < 0 or 60 <= e["tl"] < 90 or e["corrige"]) else e["pnl"],
    }
    rap = [f"# Moteur fantome V2 sur {J_} jours ({jours[1]} -> {jours[-1]}) — gain moyen par trade de 50 $", "",
           "Achat au prix d'un vrai acheteur dans les 2 s (sinon pas de trade), frais compris, garde jusqu'au resultat officiel. j1-8 = jours de choix, j9-12 = verification.", ""]
    for A in ("btc", "eth"):
        for E in (0.10, 0.15, 0.20):
            EV = evenements(D, A, E)
            if not EV: continue
            rap += [f"## {A.upper()} — ecart >= {E:.2f} — {len(EV)} desaccords", "",
                    "| Variante | Zone de prix | Trades j1-8 | Gain/trade j1-8 | Trades j9-12 | **Gain/trade j9-12** | % gagnants | Jours positifs |", "|---|---|---|---|---|---|---|---|"]
            for nom, f in V.items():
                for zone, zf in (("tous", lambda p: True), ("loterie < 0,10", lambda p: p < 0.10), ("0,15-0,40", lambda p: 0.15 <= p <= 0.40)):
                    X = [(e, f(e)) for e in EV if zf(e["prix"]) and f(e) is not None]
                    a_ = [g for e, g in X if e["st"] < coupe]; b_ = [g for e, g in X if e["st"] >= coupe]
                    if len(a_) < 15 or len(b_) < 8: continue
                    pj = collections.defaultdict(float)
                    for e, g in X: pj[datetime.fromtimestamp(e["st"], timezone.utc).strftime("%d.%m")] += g
                    rap.append(f"| {nom} | {zone} | {len(a_)} | {statistics.mean(a_):+.2f} $ | {len(b_)} | **{statistics.mean(b_):+.2f} $** | {100 * statistics.mean(1 if e['g'] else 0 for e, g in X):.0f} % | {sum(1 for v in pj.values() if v > 0)}/{len(pj)} |")
            rap.append("")
            open(OUT + "resultat_veto.md", "w").write("\n".join(rap))
    print("\n".join(rap))


if __name__ == "__main__":
    main()
