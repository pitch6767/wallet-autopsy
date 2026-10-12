"""BOT95 — H1054 : « jouer contre l'argent bête » (12.10.2026 ~22:00, Pitch : « cherche encore »). PROTOCOLE PRÉ-ENREGISTRÉ avant toute donnée
du 13.10. Hors ligne ; aucun ordre ; aucune stratégie modifiée.

IDÉE : les portefeuilles Polymarket qui ont presque toujours le MAUVAIS côté (z ≤ −3 sur leur position finale, 09–10.10, ≥ 30 marchés) ne
  savent rien. Quand ils viennent de pousser le prix CONTRE le côté qu'une de nos stratégies achète (vente de notre jeton ou achat de l'autre
  dans les 10 s qui précèdent, jusqu'à 1 s avant la décision), notre billet est moins cher pour une mauvaise raison.
EXPLORATION (11.10 → 12.10, portefeuilles classés sur 09–10.10 uniquement) : sur les 10 stratégies gagnantes du 12.10 (10 $ par trade) :
  11.10 +2 618 $ (base −2 687 $), 12.10 matin +1 893 $ (base +2 351 $), 12.10 après-midi +1 343 $ (base +598 $), perdants 66 % / 67 % / 58 %
  (base 77 % / 69 % / 78 %). Avec K5 : +954 / +2 298 / +1 490 $, perdants 56 % / 24 % / 0 %.
  FRAGILE : avec 5 s de retard sur l'information, l'effet disparaît sur l'ensemble des trades (11.10 −1 138 $) ; il tient mieux avec K5. Le
  retard réel d'un flux en direct des portefeuilles n'est pas encore mesuré. Environ 27 réglages regardés (seuil z, fenêtre, retard).
RÈGLES FIGÉES : A1 = trade gardé si le flux des « mauvais » (z ≤ −3) dans [décision − 11 s ; décision − 1 s] est contre notre côté.
  A2 = K5 ET A1. A3 = K5 ET même flux avec 5 s de retard ([décision − 15 s ; décision − 5 s]) (version réaliste).
TEST : trades des 10 stratégies sur les cycles ≥ 13.10 00:00 UTC ; transactions Polymarket du 13.10 téléchargées APRÈS la journée (workflow
  histo_polytrades.yml, qui n'accepte que des dates ≤ 13.10 : il faut l'étendre ce jour-là, sans rien changer d'autre) ; classement des
  portefeuilles inchangé (09–10.10). Critère : écart avec la base > 0 avec IC 90 % par cycles > 0 et perdants en baisse (A1 et A2) ; A3 décide
  si un flux en direct vaut la peine d'être enregistré.
Usage : python3 etude/bot5min/argent_bete_h1054.py dossier_polytrades (fichiers polytrades_AAAA-MM-JJ.json.gz, 09.10 → jour testé)"""
import os, sys, json, gzip, glob, datetime, collections, bisect, math
import numpy as np

ICI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, ICI)
import consensus_h1053 as K
TEST = 1791849600; RNG = np.random.default_rng(1054)


def main():
    M = {}
    for f in sorted(glob.glob(os.path.join(sys.argv[1], "polytrades_*.json.gz"))):
        d = json.load(gzip.open(f)); M.update({int(k): v for k, v in d["marches"].items()})
    R = collections.defaultdict(lambda: [0, 0])                                         # direction des portefeuilles sur 09–10.10
    for st, v in M.items():
        if not (1791504000 <= st < 1791676800): continue
        res = v["resultat"]
        if not res or max(res.values()) < 0.99: continue
        up = res.get("Up", 0) > 0.5; E = collections.defaultdict(float)
        for ts, w, side, out, px, sz, _ in v["trades"]:
            if sz is None or out not in ("Up", "Down"): continue
            E[w] += (1 if out == "Up" else -1) * (1 if side == "BUY" else -1) * sz
        for w, e in E.items():
            if abs(e) >= 10: R[w][0] += 1; R[w][1] += (e > 0) == up
    BETE = {w for w, (n, k) in R.items() if n >= 30 and (k - 0.5 * n) / math.sqrt(0.25 * n) <= -3}
    IDX = {}
    for st, v in M.items():
        if st < TEST: continue
        L = sorted(((ts, (1 if out == "Up" else -1) * (1 if side == "BUY" else -1) * sz) for ts, w, side, out, px, sz, _ in v["trades"]
                    if w in BETE and sz and ts and out in ("Up", "Down")), key=lambda x: x[0])
        IDX[st] = (L, [x[0] for x in L])
    # trades du bot (avec l'heure) : on relit la sauvegarde
    import glob as g2
    rows = {}
    for f in g2.glob(os.path.join(K.SAUV, "*_BTC.json")):
        d = json.load(open(f))
        for t in (d.get("trades") or {}).values():
            if isinstance(t, dict) and t.get("heure") and t.get("start", 0) >= TEST:
                rows[(d.get("nom"), t["start"])] = (datetime.datetime.fromisoformat(t["heure"].replace("Z", "+00:00")).timestamp(), t["cote"])
    D = [d for d in K.charger() if d["st"] >= TEST and d["st"] in IDX]
    def flux(d, a_, b_):
        x = rows.get((d["nom"], d["st"]))
        if not x: return None
        ts, cote = x; L, T = IDX[d["st"]]; i = bisect.bisect_left(T, ts - a_); j = bisect.bisect_right(T, ts - b_)
        return sum(v for _, v in L[i:j]) * (1 if cote == "Up" else -1)
    K5 = lambda d: d["same"] >= 8 and d["rest"] >= 120 and d["age"] <= 3
    RG = {"A1 mauvais contre nous (10 s, 1 s)": lambda d: (flux(d, 11, 1) or 0) < 0, "A2 K5 + A1": lambda d: K5(d) and (flux(d, 11, 1) or 0) < 0,
          "A3 K5 + mauvais contre nous avec 5 s de retard": lambda d: K5(d) and (flux(d, 15, 5) or 0) < 0, "K5 seul (rappel)": K5}
    o = [f"# Bot95 — H1054 : jouer contre l'argent bête — TEST (≥ 13.10)\n\n{len(BETE)} portefeuilles « mauvais » (09–10.10). {len(D)} trades testés ; base "
         f"{sum(d['pnl'] for d in D):+.0f} $, {sum(d['los'] for d in D)} perdants.\n",
         "| Règle | Trades gardés | P&L gardé | Perdants | Écart avec la base | IC 90 % |\n|---|---|---|---|---|---|"]
    gg = [d["st"] for d in D]
    for k, f in RG.items():
        keep = [f(d) for d in D]; dv = [0.0 if kk else -d["pnl"] for kk, d in zip(keep, D)]; c = K.ic(gg, dv)
        o.append(f"| {k} | {sum(keep)} | {sum(d['pnl'] for kk, d in zip(keep, D) if kk):+.0f} | {sum(d['los'] for kk, d in zip(keep, D) if kk)} | {sum(dv):+.0f} | [{c[0]:+.0f} ; {c[1]:+.0f}] |")
    open(os.path.join(ICI, "resultat_argent_bete_h1054.md"), "w").write("\n".join(o)); print("\n".join(o))


if __name__ == "__main__":
    main()
