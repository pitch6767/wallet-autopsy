"""BOT95 — H1057 : acheter le côté qui a déjà la direction, à 0,55 ou plus (Pitch, 13.10.2026 10:25 « Juste l'opposé. Je veux trouver des
stratégies où on a déjà la direction. Pas de petit prix mais plus à 55 c »). PROTOCOLE PRÉ-ENREGISTRÉ avant le calcul de la validation et du
test. Hors ligne ; aucun ordre ; aucun fantôme ni stratégie modifié.

DONNÉES : cycles Dublin (carnet rejoué), preneur à 164 ms, 10 $ par achat, limite = meilleur vendeur + 1 c, frais 0,07·p·(1−p).
PÉRIODES : apprentissage = 2/3 des cycles avant le 12.10 12:00 UTC (seule période explorée) ; validation = dernier tiers ; test = 12.10
  12:00–24:00 UTC ; confirmation (--confirmation) = cycles à partir du 13.10, lancée une seule fois plus tard.
EXPLORATION (apprentissage, déjà vue) : premier favori 0,55–0,90 : gagne 72 % pour 0,73 payé (ROI −1,5 %). Binance, Chainlink, perp, flux,
  vitesse : rien de monotone. Seule tendance : un favori à son plus haut du cycle (recul ≤ 0,02) fait mieux qu'un favori qui recule (≥ 0,09) :
  ROI +2 % contre −5 % ; à 0,55–0,75 et au plus haut : +8,5 % (96 cas) ; dernière minute 0,55–0,75 : +10 % (23 cas).
RÈGLES FIGÉES (au plus une entrée par cycle) :
  T  témoin : premier instant où un côté a un meilleur vendeur entre 0,55 et 0,90, 20 à 200 s restantes ;
  DA favori à son plus haut : idem, et le milieu du côté est à moins de 0,02 de son plus haut du cycle ;
  DB favori à son plus haut, 0,55–0,75 seulement ;
  DC dernière minute : meilleur vendeur 0,55–0,75 avec 20 à 60 s restantes.
CRITÈRE : ROI > 0 en validation ET sur le test, et IC 90 % par cycles (corrigé pour 3 règles) > 0 sur le test. Sinon abandon.
  Périodes rapportées séparément. Aucun fantôme sans accord de Pitch.
Usage : python3 etude/bot5min/direction_h1057.py dossier_cycles_dublin [--confirmation]"""
import os, sys, time
import numpy as np

ICI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, ICI)
import liquidite_h833 as L, latence_h766 as LH, dpe_h841 as DP
import reversal_h1003 as RV
CONF = "--confirmation" in sys.argv
if CONF: L.RESERVE = 10 ** 12
SORTIE = os.path.join(ICI, "resultat_direction_h1057" + ("_confirmation" if CONF else "") + ".md")
TEST1 = 1791849600
fee = lambda p: 0.07 * p * (1 - p)
RNG = np.random.default_rng(1057)
REGLES = ("T", "DA", "DB", "DC")


def achat(Lc, X, lim, dollars=10.0):
    q = c = 0.0
    for px, sz in DP.vend(Lc, X):
        if px > lim: break
        if px <= 0: continue
        pp = px / 1000; u = pp + fee(pp); k = min(sz, (dollars - c) / u)
        if k <= 1e-9: break
        q += k; c += k * u
    return q, c


def main():
    t_go = time.time()
    G, cyc = L.grille(sys.argv[1]); Y = L.resultats_officiels(cyc)
    cycles = sorted(s for s in cyc if s in Y)
    if CONF: cycles = [s for s in cycles if s >= TEST1]; part = lambda s: "confirmation"
    else:
        dev = [s for s in cycles if s < RV.DEV_FIN]; tr = set(dev[:len(dev) * 2 // 3]); va = set(dev[len(dev) * 2 // 3:])
        cycles = [s for s in cycles if s < TEST1]
        part = lambda s: "apprentissage" if s in tr else ("validation" if s in va else "test")
    R = {k: [] for k in REGLES}
    for st in cycles:
        T = [st * 1000 + s * 1000 for s in range(300)]
        try: E = {k: DP.compact(v) for k, v in LH.Cycle(cyc[st]["f"]).etats(T + [t + 164 for t in T]).items()}
        except Exception: continue
        mid = {"Up": [None] * 300, "Down": [None] * 300}
        for s in range(300):
            Lc = E.get(T[s])
            for X in mid:
                a, b = DP.meilleur(Lc, X, "a"), DP.meilleur(Lc, X, "b")
                mid[X][s] = (a + b) / 2000 if a and b else (mid[X][s - 1] if s else None)
        fait = set()
        for s in range(100, 281):
            rest = 300 - s
            for X in ("Up", "Down"):
                a = DP.meilleur(E.get(T[s]), X, "a")
                if not a or not (550 <= a <= 900): continue
                h = [x for x in mid[X][:s + 1] if x is not None]
                hi = max(h) if h else None; now = mid[X][s]
                haut = hi is not None and now is not None and hi - now <= 0.02
                cand = []
                if "T" not in fait: cand.append("T")
                if "DA" not in fait and haut: cand.append("DA")
                if "DB" not in fait and haut and a <= 750: cand.append("DB")
                if "DC" not in fait and a <= 750 and 20 <= rest <= 60: cand.append("DC")
                if not cand: continue
                q, c = achat(E.get(T[s] + 164), X, a + 10)
                if q <= 0 or c < 5: continue
                win = (Y[st] == 1.0) == (X == "Up")
                for k in cand: fait.add(k); R[k].append((part(st), st, c, q * win - c, int(win), c / q))
    parts = ["confirmation"] if CONF else ["apprentissage", "validation", "test"]
    o = [f"# Bot95 — H1057 : acheter la direction déjà prise (0,55 et plus){' — CONFIRMATION (≥ 13.10)' if CONF else ''}\n",
         f"Généré le {time.strftime('%d.%m.%Y %H:%M', time.gmtime())} UTC. 10 $ par achat, preneur 164 ms. Aucun ordre.\n",
         "| Règle | Période | Cycles | Achats | Gagnants | Prix moyen payé | Taux de gain | P&L ($) | ROI | IC 90 % (corrigé, 3 règles) |", "|---|---|---|---|---|---|---|---|---|---|"]
    V = {}
    for k in REGLES:
        for pa in parts:
            x = [r for r in R[k] if r[0] == pa]; g = {}
            for r in x: g[r[1]] = g.get(r[1], 0) + r[3]
            nc = len([s for s in cycles if part(s) == pa])
            vv = np.concatenate([np.array(list(g.values()) or [0.0]), np.zeros(max(nc - max(len(g), 1), 0))])
            bs = vv[RNG.integers(0, len(vv), (4000, len(vv)))].sum(1); lo, hi = np.percentile(bs, [100 * 0.10 / 3 / 2, 100 - 100 * 0.10 / 3 / 2])
            pnl = sum(r[3] for r in x); cost = sum(r[2] for r in x) or 1
            o.append(f"| {k} | {pa} | {nc} | {len(x)} | {sum(r[4] for r in x)} | {np.mean([r[5] for r in x]) if x else 0:.3f} | "
                     f"{100 * np.mean([r[4] for r in x]) if x else 0:.0f} % | {pnl:+.0f} | {100 * pnl / cost:+.1f} % | [{lo:+.0f} ; {hi:+.0f}] |")
            V[(k, pa)] = (pnl, lo)
    if not CONF:
        o.append("\n**Verdict (critère figé)**\n")
        for k in REGLES[1:]:
            ok = V[(k, "validation")][0] > 0 and V[(k, "test")][0] > 0 and V[(k, "test")][1] > 0
            o.append(f"- {k} : {'candidat (proposition à Pitch, confirmation ≥ 13.10)' if ok else 'abandon'}")
    o.append(f"\n_Calcul : {time.time() - t_go:.0f} s._\n")
    open(SORTIE, "w").write("\n".join(o)); print("\n".join(o))


if __name__ == "__main__":
    main()
