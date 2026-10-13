"""BOT95 — H1058 : une jambe vers 0,55 puis couverture plus bas (Pitch, 13.10.2026 10:44 « Cherche une idée où on peut savoir que dans les
prochaines secondes si on achète une leg maintenant on peut se hedger plus bas assez vite »). PROTOCOLE PRÉ-ENREGISTRÉ avant le calcul de la
validation et du test. Hors ligne ; aucun ordre ; aucun fantôme ni stratégie modifié.

IDÉE : acheter X ≈ 0,55 au moment où le perp vient de sauter dans le sens de X ; Polymarket suit dans les secondes suivantes ; dès que
  prix payé + meilleur vendeur de l'opposé + frais ≤ 1 − 0,02, acheter autant de parts de l'opposé : la paire paie 1 $ quoi qu'il arrive
  (gain verrouillé). Sans couverture dans les 5 s : garder jusqu'au règlement.
EXPLORATION (apprentissage seulement) :
  - sans déclencheur (achat chaque seconde à 0,45–0,65) : couverture dans 10 s 28–38 % des cas, mais les non-couverts perdent :
    −0,35 $ par 10 $, comme garder (−0,35 $) ; carnet Binance, flux, vitesse : rien de stable ;
  - après un saut du perp ≥ 10 $ en 300 ms (côté X 0,45–0,65) : le milieu de X monte de +7 c en 1 s et +11 c en 5 s ; couverture dans les
    2 s dans ~80 % des cas ; +1,2 à +2,0 $ par 10 $ (40 cas) ;
  - seuil 5 $, X 0,40–0,70 : 153 cas, couverture 2 c dans 5 s ≈ 46–54 %, total +157 $ (ROI +10 %), garder seul +152 $.
RÈGLE (sur chaque cycle, 30 à 280 s écoulées, pause 5 s entre deux déclenchements) :
  déclencheur : le perp (Binance futures) a bougé d'au moins J $ entre t−300 ms et t (premier message qui franchit) ; X = côté du mouvement ;
  entrée : meilleur vendeur de X entre 0,40 et 0,70 à t ; achat 10 $ exécuté sur le carnet à t + 164 ms, limite meilleur vendeur + 1 c ;
  couverture : toutes les 250 ms jusqu'à 5 s, si prix payé + vendeur de l'opposé + frais ≤ 0,98, achat des mêmes parts de l'opposé
    exécuté 250 ms plus tard (limite + 1 c, ≥ 95 % des parts) ; sinon on garde X jusqu'au règlement.
  JC5 = seuil 5 $ ; JC10 = seuil 10 $ ; témoins G5 / G10 = même entrée, jamais couverte. Sensibilité : entrée à 500 ms.
CRITÈRE : ROI > 0 en validation ET sur le test, et IC 90 % par cycles (corrigé pour 2 règles) > 0 sur le test. Sinon abandon.
  Périodes rapportées séparément. Aucun fantôme sans accord de Pitch. Confirmation (--confirmation) sur les cycles ≥ 13.10, une fois, plus tard.
Usage : python3 etude/bot5min/jambe_couverture_h1058.py dossier_cycles_dublin [--confirmation]"""
import os, sys, json, gzip, time
import numpy as np

ICI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, ICI)
import liquidite_h833 as L, latence_h766 as LH, dpe_h841 as DP
import reversal_h1003 as RV
CONF = "--confirmation" in sys.argv
if CONF: L.RESERVE = 10 ** 12
SORTIE = os.path.join(ICI, "resultat_jambe_couverture_h1058" + ("_confirmation" if CONF else "") + ".md")
TEST1 = 1791849600
fee = lambda p: 0.07 * p * (1 - p)
RNG = np.random.default_rng(1058)


def achat_d(Lc, X, lim, dollars=10.0):
    q = c = 0.0
    for px, sz in DP.vend(Lc, X):
        if px > lim: break
        if px <= 0: continue
        pp = px / 1000; u = pp + fee(pp); k = min(sz, (dollars - c) / u)
        if k <= 1e-9: break
        q += k; c += k * u
    return q, c


def achat_q(Lc, X, lim, qq):
    q = c = 0.0
    for px, sz in DP.vend(Lc, X):
        if px > lim: break
        if px <= 0: continue
        pp = px / 1000; k = min(sz, qq - q)
        if k <= 1e-9: break
        q += k; c += k * (pp + fee(pp))
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
    R = {(k, lat): [] for k in ("JC5", "JC10", "G5", "G10") for lat in (164, 500)}
    nver = {k: [0, 0, []] for k in ("JC5", "JC10")}
    for st in cycles:
        try: Rj = json.load(gzip.open(cyc[st]["f"]))
        except Exception: continue
        rows = sorted(Rj.get("ex", []), key=lambda r: r[0])
        pp = [(r[0], r[1][0]) for r in rows if r[1] and r[1][0]]
        if len(pp) < 100: continue
        tt = np.array([x[0] for x in pp], float); px = np.array([x[1] for x in pp], float)
        trig = []; last = -1e18; j0 = 0
        for k in range(len(tt)):
            t = tt[k]
            while tt[j0] < t - 300: j0 += 1
            if not (st * 1000 + 30000 <= t <= st * 1000 + 280000) or t - last < 5000: continue
            d = px[k] - px[j0]
            if abs(d) >= 5: trig.append((int(t), d)); last = t
        if not trig: continue
        T = []
        for t, d in trig: T += [t, t + 164, t + 500] + [t + 164 + 250 * h for h in range(1, 23)] + [t + 500 + 250 * h for h in range(1, 23)]
        try: E = {k: DP.compact(v) for k, v in LH.Cycle(cyc[st]["f"]).etats(sorted(set(T))).items()}
        except Exception: continue
        for t, d in trig:
            X = "Up" if d > 0 else "Down"; O = "Down" if X == "Up" else "Up"
            a = DP.meilleur(E.get(t), X, "a")
            if not a or not (400 <= a <= 700): continue
            win = (Y[st] == 1.0) == (X == "Up")
            for lat in (164, 500):
                q, c = achat_d(E.get(t + lat), X, a + 10)
                if q <= 0 or c < 5: continue
                hold = q * win - c; res = None; tl = None
                for h in range(1, 21):
                    u = t + lat + 250 * h; oa = DP.meilleur(E.get(u), O, "a")
                    if oa and c / q + oa / 1000 + fee(oa / 1000) <= 0.98:
                        q2, c2 = achat_q(E.get(u + 250), O, oa + 10, q)
                        if q2 >= 0.95 * q: res = q2 - c - c2 + (q - q2) * win; tl = 250 * (h + 1); break
                for J in (5, 10):
                    if abs(d) < J: continue
                    R[(f"JC{J}", lat)].append((part(st), st, c, res if res is not None else hold, int((res if res is not None else hold) > 0)))
                    R[(f"G{J}", lat)].append((part(st), st, c, hold, int(win)))
                    if lat == 164: nver[f"JC{J}"][0] += 1; nver[f"JC{J}"][1] += res is not None; (nver[f"JC{J}"][2].append(tl) if tl else None)
    parts = ["confirmation"] if CONF else ["apprentissage", "validation", "test"]
    o = [f"# Bot95 — H1058 : une jambe puis couverture plus bas{' — CONFIRMATION (≥ 13.10)' if CONF else ''}\n",
         f"Généré le {time.strftime('%d.%m.%Y %H:%M', time.gmtime())} UTC. 10 $ par entrée, preneur. Aucun ordre.\n",
         "| Règle | Entrée | Période | Cycles | Entrées | Positives | P&L ($) | ROI | IC 90 % (corrigé, 2 règles) |", "|---|---|---|---|---|---|---|---|---|"]
    V = {}
    for k in ("JC5", "G5", "JC10", "G10"):
        for lat in (164, 500):
            for pa in parts:
                x = [r for r in R[(k, lat)] if r[0] == pa]; g = {}
                for r in x: g[r[1]] = g.get(r[1], 0) + r[3]
                nc = len([s for s in cycles if part(s) == pa])
                vv = np.concatenate([np.array(list(g.values()) or [0.0]), np.zeros(max(nc - max(len(g), 1), 0))])
                bs = vv[RNG.integers(0, len(vv), (4000, len(vv)))].sum(1); lo, hi = np.percentile(bs, [2.5, 97.5])
                pnl = sum(r[3] for r in x); cost = sum(r[2] for r in x) or 1
                o.append(f"| {k} | {lat} ms | {pa} | {nc} | {len(x)} | {sum(r[4] for r in x)} | {pnl:+.0f} | {100 * pnl / cost:+.1f} % | [{lo:+.0f} ; {hi:+.0f}] |")
                V[(k, lat, pa)] = (pnl, lo)
    for k in ("JC5", "JC10"):
        n, v, tl = nver[k]
        o.append(f"\n{k} (164 ms, toutes périodes) : couverture obtenue {v}/{n} ({100 * v / max(n, 1):.0f} %), délai médian {np.median(tl) if tl else 0:.0f} ms.")
    if not CONF:
        o.append("\n**Verdict (critère figé)**\n")
        for k in ("JC5", "JC10"):
            ok = V[(k, 164, "validation")][0] > 0 and V[(k, 164, "test")][0] > 0 and V[(k, 164, "test")][1] > 0
            o.append(f"- {k} : {'candidat (proposition à Pitch, confirmation ≥ 13.10)' if ok else 'abandon'}")
    o.append(f"\n_Calcul : {time.time() - t_go:.0f} s._\n")
    open(SORTIE, "w").write("\n".join(o)); print("\n".join(o))


if __name__ == "__main__":
    main()
