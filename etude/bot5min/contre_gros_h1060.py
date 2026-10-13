"""BOT95 — H1060 : jouer CONTRE les gros preneurs de Polymarket (Pitch, 13.10.2026 14:37 « Trouve-moi encore des idées »). PROTOCOLE
PRÉ-ENREGISTRÉ avant le calcul de la validation et du test. Hors ligne ; aucun ordre ; aucun fantôme ni stratégie modifié.

ÉVÉNEMENT : une transaction Polymarket (flux « last_trade_price » enregistré à Dublin) d'au moins N $ (prix × parts), 30 à 280 s écoulées,
  pause 3 s entre deux événements d'un même cycle (comptée sur le seuil 150 $). Côté poussé X = côté acheté par le preneur (achat de X, ou
  vente de l'autre jeton). Condition : meilleur vendeur de X entre 0,40 et 0,70 à l'instant de la transaction.
ACTION : acheter l'AUTRE côté O, 10 $, preneur, sur le carnet vu à +164 ms, limite meilleur vendeur de O + 1 c ; garder jusqu'au règlement.
EXPLORATION (apprentissage seulement) : après ces transactions le côté X ne monte pas (+0,2 c à 1 s, −3 c à 30 s) et ne gagne que 47 % pour
  0,58 payé ; suivre : −546 $ ; jouer contre : +392 $ (283 cas, ROI +14 %) ; 150–300 $ : +11,5 % ; ≥ 300 $ : +20 %.
RÈGLES FIGÉES : FG150 (N = 150 $) et FG300 (N = 300 $). Témoin : suivre (acheter X, même instant).
CRITÈRE : ROI > 0 en validation ET sur le test, et IC 90 % par cycles (corrigé pour 2 règles) > 0 sur le test. Sinon abandon.
  Périodes rapportées séparément. Aucun fantôme sans accord de Pitch. Confirmation (--confirmation) sur les cycles ≥ 13.10, une fois, plus tard.
Usage : python3 etude/bot5min/contre_gros_h1060.py dossier_cycles_dublin [--confirmation]"""
import os, sys, json, gzip, time
import numpy as np

ICI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, ICI)
import liquidite_h833 as L, latence_h766 as LH, dpe_h841 as DP
import reversal_h1003 as RV
from jambe_couverture_h1058 import achat_d
CONF = "--confirmation" in sys.argv
if CONF: L.RESERVE = 10 ** 12
SORTIE = os.path.join(ICI, "resultat_contre_gros_h1060" + ("_confirmation" if CONF else "") + ".md")
TEST1 = 1791849600
RNG = np.random.default_rng(1060)


def main():
    t_go = time.time()
    G, cyc = L.grille(sys.argv[1]); Y = L.resultats_officiels(cyc)
    cycles = sorted(s for s in cyc if s in Y)
    if CONF: cycles = [s for s in cycles if s >= TEST1]; part = lambda s: "confirmation"
    else:
        dev = [s for s in cycles if s < RV.DEV_FIN]; tr = set(dev[:len(dev) * 2 // 3]); va = set(dev[len(dev) * 2 // 3:])
        cycles = [s for s in cycles if s < TEST1]
        part = lambda s: "apprentissage" if s in tr else ("validation" if s in va else "test")
    R = {k: [] for k in ("FG150", "FG300", "suivre 150", "suivre 300")}
    for st in cycles:
        try: Rj = json.load(gzip.open(cyc[st]["f"]))
        except Exception: continue
        tr_ = sorted((r for r in Rj.get("ev", []) if r and r[0] == "T" and len(r) >= 7), key=lambda r: r[1])
        trig = []; last = -1e18
        for r in tr_:
            t, k, side, px, sz = r[1], r[3], r[4], r[5], r[6]
            if not (st * 1000 + 30000 <= t <= st * 1000 + 280000) or t - last < 3000 or px * sz < 150: continue
            X = ("Up" if k == 0 else "Down") if side == 1 else ("Down" if k == 0 else "Up")
            trig.append((int(t), X, px * sz)); last = t
        if not trig: continue
        T = []
        for t, X, v in trig: T += [t, t + 164]
        try: E = {k: DP.compact(v) for k, v in LH.Cycle(cyc[st]["f"]).etats(sorted(set(T))).items()}
        except Exception: continue
        for t, X, v in trig:
            O = "Down" if X == "Up" else "Up"
            a = DP.meilleur(E.get(t), X, "a"); ao = DP.meilleur(E.get(t), O, "a")
            if not a or not (400 <= a <= 700) or not ao: continue
            winX = int((Y[st] == 1.0) == (X == "Up"))
            qo, co = achat_d(E.get(t + 164), O, ao + 10); qx, cx = achat_d(E.get(t + 164), X, a + 10)
            for N in (150, 300):
                if v < N: continue
                if qo > 0 and co >= 5: R[f"FG{N}"].append((part(st), st, co, qo * (1 - winX) - co, int(1 - winX)))
                if qx > 0 and cx >= 5: R[f"suivre {N}"].append((part(st), st, cx, qx * winX - cx, winX))
    parts = ["confirmation"] if CONF else ["apprentissage", "validation", "test"]
    o = [f"# Bot95 — H1060 : jouer contre les gros preneurs de Polymarket{' — CONFIRMATION (≥ 13.10)' if CONF else ''}\n",
         f"Généré le {time.strftime('%d.%m.%Y %H:%M', time.gmtime())} UTC. 10 $ par entrée, preneur 164 ms, gardé jusqu'au règlement. Aucun ordre.\n",
         "| Règle | Période | Cycles | Entrées | Gagnantes | P&L ($) | ROI | IC 90 % (corrigé, 2 règles) |", "|---|---|---|---|---|---|---|---|"]
    V = {}
    for k in R:
        for pa in parts:
            x = [r for r in R[k] if r[0] == pa]; g = {}
            for r in x: g[r[1]] = g.get(r[1], 0) + r[3]
            nc = len([s for s in cycles if part(s) == pa])
            vv = np.concatenate([np.array(list(g.values()) or [0.0]), np.zeros(max(nc - max(len(g), 1), 0))])
            bs = vv[RNG.integers(0, len(vv), (4000, len(vv)))].sum(1); lo, hi = np.percentile(bs, [2.5, 97.5])
            pnl = sum(r[3] for r in x); cost = sum(r[2] for r in x) or 1
            o.append(f"| {k} | {pa} | {nc} | {len(x)} | {sum(r[4] for r in x)} | {pnl:+.0f} | {100 * pnl / cost:+.1f} % | [{lo:+.0f} ; {hi:+.0f}] |")
            V[(k, pa)] = (pnl, lo)
    if not CONF:
        o.append("\n**Verdict (critère figé)**\n")
        for k in ("FG150", "FG300"):
            ok = V[(k, "validation")][0] > 0 and V[(k, "test")][0] > 0 and V[(k, "test")][1] > 0
            o.append(f"- {k} : {'candidat (proposition à Pitch, confirmation ≥ 13.10)' if ok else 'abandon'}")
    o.append(f"\n_Calcul : {time.time() - t_go:.0f} s._\n")
    open(SORTIE, "w").write("\n".join(o)); print("\n".join(o))


if __name__ == "__main__":
    main()
