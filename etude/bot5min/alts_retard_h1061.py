"""BOT95 — H1061 : les marchés ETH et SOL 5 min suivent en retard les sauts du perp BTC (Pitch, 13.10.2026 « Trouve-moi encore des idées »).
PROTOCOLE PRÉ-ENREGISTRÉ avant le calcul de la validation et du test. Hors ligne ; aucun ordre ; aucun fantôme ni stratégie modifié.

DONNÉES : sauts du perp BTC enregistrés à Dublin (fichiers de cycle) ; transactions publiques des marchés ETH/SOL Up/Down 5 min de Polymarket
  (data-api, horodatage à la seconde, branche donnees-btc/polytrades, 11–12.10). Le carnet ETH/SOL n'est PAS enregistré : le prix d'achat est
  approché par le prix de la première transaction ETH/SOL au moins 1 s après le saut, + 1 c, + frais 0,07·p·(1−p).
EXPLORATION (apprentissage seulement) : après un saut du perp ≥ 5 $ en 300 ms, le prix du côté du saut monte de +6 c (1re transaction après
  1 s) puis +9 c à 30 s sur ETH et SOL ; acheter à la 1re transaction après 1 s : ETH 1 113 cas, 57 % gagnés à 0,52, ROI +12 % ;
  SOL 1 064 cas, 55 % à 0,52, ROI +21 %.
RÈGLE (par cycle, 30 à 280 s écoulées, pause 5 s entre deux sauts) : saut du perp ≥ 5 $ entre t − 300 ms et t ; côté X du saut sur le marché
  ETH (règle AE) ou SOL (règle AS) du même créneau ; achat 10 $ au prix de la 1re transaction après t + 1 s + 1 c + frais, si ce prix est entre
  0,05 et 0,95 ; gardé jusqu'au règlement. Témoin : même chose sur le marché BTC (transactions publiques), règle AB.
CRITÈRE : ROI > 0 en validation ET sur le test, et IC 90 % par cycles (corrigé pour 2 règles AE/AS) > 0 sur le test. Sinon abandon.
  LIMITE MAJEURE : prix approché par des transactions d'autres participants, pas par un carnet ; un résultat positif devra être confirmé par
  l'enregistrement des carnets ETH/SOL à Dublin avant toute conclusion. Aucun fantôme sans accord de Pitch.
Usage : python3 etude/bot5min/alts_retard_h1061.py dossier_cycles_dublin dossier_polytrades"""
import os, sys, json, gzip, glob, bisect, time
import numpy as np
ICI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, ICI)
import reversal_h1003 as RV
fee = lambda p: 0.07 * p * (1 - p)
RNG = np.random.default_rng(1061); TEST1 = 1791849600; MIDI = 1791806400


def charge(poly, pre):
    M = {}
    for f in sorted(glob.glob(os.path.join(poly, pre + "*.json.gz"))): M.update({int(k): v for k, v in json.load(gzip.open(f))["marches"].items()})
    out = {}
    for st, v in M.items():
        if not v["resultat"] or max(v["resultat"].values()) < 0.99: continue
        T = sorted([(t[0], (t[4] if t[3] == "Up" else 1 - t[4])) for t in v["trades"] if t[0] and t[4] is not None and t[3] in ("Up", "Down")])
        out[st] = ([x[0] for x in T], [x[1] for x in T], v["resultat"].get("Up", 0) > 0.5)
    return out


def main():
    t_go = time.time(); cyc_dir, poly = sys.argv[1], sys.argv[2]
    MK = {"AE": charge(poly, "polytrades_eth_"), "AS": charge(poly, "polytrades_sol_"), "AB": charge(poly, "polytrades_2026-")}
    files = sorted(glob.glob(os.path.join(cyc_dir, "*.json.gz"))); sts = sorted(int(os.path.basename(f).split(".")[0]) for f in files)
    allc = sorted(s for s in sts if s < TEST1); dev = [s for s in allc if s < RV.DEV_FIN]; tr = set(dev[:len(dev) * 2 // 3]); va = set(dev[len(dev) * 2 // 3:])
    part = lambda s: "apprentissage" if s in tr else ("validation" if s in va else "test")
    R = {k: [] for k in MK}; ncy = {k: {p: set() for p in ("apprentissage", "validation", "test")} for k in MK}
    for f in files:
        st = int(os.path.basename(f).split(".")[0])
        if st >= TEST1: continue
        try: Rj = json.load(gzip.open(f))
        except Exception: continue
        rows = sorted(Rj.get("ex", []), key=lambda r: r[0]); pp = [(r[0], r[1][0]) for r in rows if r[1] and r[1][0]]
        if len(pp) < 100: continue
        for k in MK:
            if st in MK[k]: ncy[k][part(st)].add(st)
        tt = np.array([x[0] for x in pp], float); px = np.array([x[1] for x in pp], float); last = -1e18; j0 = 0
        for i in range(len(tt)):
            t = tt[i]
            while tt[j0] < t - 300: j0 += 1
            if not (st * 1000 + 30000 <= t <= st * 1000 + 280000) or t - last < 5000: continue
            d = px[i] - px[j0]
            if abs(d) < 5: continue
            last = t; sg = 1 if d > 0 else -1
            for k, MM in MK.items():
                if st not in MM: continue
                ts, ps, up = MM[st]; j = bisect.bisect_left(ts, t / 1000 + 1)
                if j >= len(ts): continue
                q = ps[j] if sg > 0 else 1 - ps[j]
                if not (0.05 < q < 0.95): continue
                pe = q + 0.01; pe += fee(pe); win = up if sg > 0 else not up
                R[k].append((part(st), st, 10 * (int(win) / pe - 1), int(win)))
    o = ["# Bot95 — H1061 : retard des marchés ETH et SOL après un saut du perp BTC\n",
         f"Généré le {time.strftime('%d.%m.%Y %H:%M', time.gmtime())} UTC. 10 $ par achat, prix = 1re transaction après +1 s + 1 c + frais (approximation). Aucun ordre.\n",
         "| Règle | Période | Cycles | Achats | Gagnants | P&L ($) | ROI | IC 90 % (corrigé, 2 règles) |", "|---|---|---|---|---|---|---|---|"]
    V = {}
    for k in ("AE", "AS", "AB"):
        for pa in ("apprentissage", "validation", "test"):
            x = [r for r in R[k] if r[0] == pa]; g = {}
            for r in x: g[r[1]] = g.get(r[1], 0) + r[2]
            nc = len(ncy[k][pa]) or 1
            vv = np.concatenate([np.array(list(g.values()) or [0.0]), np.zeros(max(nc - max(len(g), 1), 0))])
            bs = vv[RNG.integers(0, len(vv), (4000, len(vv)))].sum(1); lo, hi = np.percentile(bs, [2.5, 97.5])
            pnl = sum(r[2] for r in x)
            o.append(f"| {k} | {pa} | {nc} | {len(x)} | {sum(r[3] for r in x)} | {pnl:+.0f} | {100 * pnl / max(10 * len(x), 1):+.1f} % | [{lo:+.0f} ; {hi:+.0f}] |")
            V[(k, pa)] = (pnl, lo)
    o.append("\n**Verdict (critère figé)**\n")
    for k in ("AE", "AS"):
        ok = V[(k, "validation")][0] > 0 and V[(k, "test")][0] > 0 and V[(k, "test")][1] > 0
        o.append(f"- {k} : {'candidat — à confirmer avec les carnets ETH/SOL enregistrés à Dublin (proposition à Pitch)' if ok else 'abandon'}")
    o.append(f"\n_Calcul : {time.time() - t_go:.0f} s._\n")
    open(os.path.join(ICI, "resultat_alts_retard_h1061.md"), "w").write("\n".join(o)); print("\n".join(o))


if __name__ == "__main__":
    main()
