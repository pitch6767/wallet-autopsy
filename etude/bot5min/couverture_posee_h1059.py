"""BOT95 — H1059 : jambe + couverture POSÉE EN MÊME TEMPS, plus bas (Pitch, 13.10.2026 11:15 « D'abord on améliore l'idée. Et passer les 2 ordres
en même temps mais déjà plus bas pour le 2e. Déjà prêt chauffé ? »). PROTOCOLE PRÉ-ENREGISTRÉ avant le calcul de la validation et du test.
Hors ligne ; aucun ordre ; aucun fantôme ni stratégie modifié.

ENTRÉE (identique à H1058) : le perp bouge d'au moins J $ en 300 ms (30 à 280 s écoulées, pause 5 s) ; côté X du mouvement avec meilleur
  vendeur 0,40–0,70 ; achat preneur 10 $ exécuté sur le carnet à t + 164 ms (limite + 1 c).
COUVERTURE POSÉE : au même instant, ordre d'achat (maker, sans frais) du même nombre de parts de l'opposé au prix
  b = arrondi inférieur au centime de (1 − m − prix payé par part, frais compris). Si le meilleur vendeur de l'opposé est déjà ≤ b : exécution
  immédiate en preneur (frais). Sinon l'ordre attend W secondes ; rempli (hypothèse PRUDENTE) seulement si le meilleur vendeur de l'opposé
  descend à b − 1 c ou moins (le prix traverse notre ordre) ; l'hypothèse optimiste (toucher b) est rapportée à part. Non rempli : ordre
  annulé, X gardé jusqu'au règlement.
EXPLORATION (apprentissage seulement, 171 entrées) : couverture posée à m = 0,02 : +25 $ (elle verrouille trop tôt des trades qui auraient bien
  gagné) ; m = 0,06, W = 10 s : +97 $ (prudent), 77 % positives ; garder seul : +84 $, 59 % ; couverture preneur H1058 : +124 $.
  L'avantage est surtout dans les gros sauts (≥ 10 $ : 32 cas, +84 $, 94 % positives).
RÈGLES FIGÉES : CP5 (J = 5 $) et CP10 (J = 10 $), m = 0,06, W = 10 s, remplissage prudent. Témoins : mêmes entrées gardées (G5, G10).
CRITÈRE : ROI > 0 en validation ET sur le test, et IC 90 % par cycles (corrigé pour 2 règles) > 0 sur le test. Sinon abandon.
Usage : python3 etude/bot5min/couverture_posee_h1059.py dossier_cycles_dublin [--confirmation]"""
import os, sys, json, gzip, time, math
import numpy as np

ICI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, ICI)
import liquidite_h833 as L, latence_h766 as LH, dpe_h841 as DP
import reversal_h1003 as RV
from jambe_couverture_h1058 import achat_d
CONF = "--confirmation" in sys.argv
if CONF: L.RESERVE = 10 ** 12
SORTIE = os.path.join(ICI, "resultat_couverture_posee_h1059" + ("_confirmation" if CONF else "") + ".md")
TEST1 = 1791849600; M, W = 0.06, 10
fee = lambda p: 0.07 * p * (1 - p)
RNG = np.random.default_rng(1059)


def couvrir(q, c, win, oa0, oa, prudent):
    hold = q * win - c
    b = math.floor((1 - M - c / q) * 100) / 100 * 1000
    if b <= 0: return hold, False
    if oa0 and oa0 <= b: return q - c - q * (oa0 / 1000 + fee(oa0 / 1000)), True
    for x in oa[:W * 4]:
        if x and x <= b - (10 if prudent else 0): return q - c - q * b / 1000, True
    return hold, False


def main():
    t_go = time.time()
    G, cyc = L.grille(sys.argv[1]); Y = L.resultats_officiels(cyc)
    cycles = sorted(s for s in cyc if s in Y)
    if CONF: cycles = [s for s in cycles if s >= TEST1]; part = lambda s: "confirmation"
    else:
        dev = [s for s in cycles if s < RV.DEV_FIN]; tr = set(dev[:len(dev) * 2 // 3]); va = set(dev[len(dev) * 2 // 3:])
        cycles = [s for s in cycles if s < TEST1]
        part = lambda s: "apprentissage" if s in tr else ("validation" if s in va else "test")
    R = {k: [] for k in ("CP5", "CP5 optimiste", "G5", "CP10", "CP10 optimiste", "G10")}
    for st in cycles:
        try: Rj = json.load(gzip.open(cyc[st]["f"]))
        except Exception: continue
        rows = sorted(Rj.get("ex", []), key=lambda r: r[0]); pp = [(r[0], r[1][0]) for r in rows if r[1] and r[1][0]]
        if len(pp) < 100: continue
        tt = np.array([x[0] for x in pp], float); px = np.array([x[1] for x in pp], float); trig = []; last = -1e18; j0 = 0
        for k in range(len(tt)):
            t = tt[k]
            while tt[j0] < t - 300: j0 += 1
            if not (st * 1000 + 30000 <= t <= st * 1000 + 280000) or t - last < 5000: continue
            d = px[k] - px[j0]
            if abs(d) >= 5: trig.append((int(t), d)); last = t
        if not trig: continue
        T = []
        for t, d in trig: T += [t, t + 164] + [t + 164 + 250 * h for h in range(1, W * 4 + 1)]
        try: E = {k: DP.compact(v) for k, v in LH.Cycle(cyc[st]["f"]).etats(sorted(set(T))).items()}
        except Exception: continue
        for t, d in trig:
            X = "Up" if d > 0 else "Down"; O = "Down" if X == "Up" else "Up"
            a = DP.meilleur(E.get(t), X, "a")
            if not a or not (400 <= a <= 700): continue
            q, c = achat_d(E.get(t + 164), X, a + 10)
            if q <= 0 or c < 5: continue
            win = int((Y[st] == 1.0) == (X == "Up"))
            oa0 = DP.meilleur(E.get(t + 164), O, "a"); oa = [DP.meilleur(E.get(t + 164 + 250 * h), O, "a") for h in range(1, W * 4 + 1)]
            v_p, lk_p = couvrir(q, c, win, oa0, oa, True); v_o, lk_o = couvrir(q, c, win, oa0, oa, False)
            for J in (5, 10):
                if abs(d) < J: continue
                R[f"CP{J}"].append((part(st), st, c, v_p, lk_p)); R[f"CP{J} optimiste"].append((part(st), st, c, v_o, lk_o))
                R[f"G{J}"].append((part(st), st, c, q * win - c, False))
    parts = ["confirmation"] if CONF else ["apprentissage", "validation", "test"]
    o = [f"# Bot95 — H1059 : jambe + couverture posée en même temps{' — CONFIRMATION (≥ 13.10)' if CONF else ''}\n",
         f"Généré le {time.strftime('%d.%m.%Y %H:%M', time.gmtime())} UTC. 10 $ par entrée ; couverture posée à 1 − {M} − prix payé, {W} s. Aucun ordre.\n",
         "| Règle | Période | Cycles | Entrées | Couvertes | Positives | P&L ($) | ROI | IC 90 % (corrigé, 2 règles) |", "|---|---|---|---|---|---|---|---|---|"]
    V = {}
    for k in R:
        for pa in parts:
            x = [r for r in R[k] if r[0] == pa]; g = {}
            for r in x: g[r[1]] = g.get(r[1], 0) + r[3]
            nc = len([s for s in cycles if part(s) == pa])
            vv = np.concatenate([np.array(list(g.values()) or [0.0]), np.zeros(max(nc - max(len(g), 1), 0))])
            bs = vv[RNG.integers(0, len(vv), (4000, len(vv)))].sum(1); lo, hi = np.percentile(bs, [2.5, 97.5])
            pnl = sum(r[3] for r in x); cost = sum(r[2] for r in x) or 1
            o.append(f"| {k} | {pa} | {nc} | {len(x)} | {sum(1 for r in x if r[4])} | {sum(1 for r in x if r[3] > 0)} | {pnl:+.0f} | {100 * pnl / cost:+.1f} % | [{lo:+.0f} ; {hi:+.0f}] |")
            V[(k, pa)] = (pnl, lo)
    if not CONF:
        o.append("\n**Verdict (critère figé, remplissage prudent)**\n")
        for k in ("CP5", "CP10"):
            ok = V[(k, "validation")][0] > 0 and V[(k, "test")][0] > 0 and V[(k, "test")][1] > 0
            o.append(f"- {k} : {'candidat (proposition à Pitch, confirmation ≥ 13.10)' if ok else 'abandon'}")
    o.append(f"\n_Calcul : {time.time() - t_go:.0f} s._\n")
    open(SORTIE, "w").write("\n".join(o)); print("\n".join(o))


if __name__ == "__main__":
    main()
