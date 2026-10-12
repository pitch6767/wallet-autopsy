"""BOT95 — H1055 : alerte de retournement d'un favori à 80 % (Pitch, 12.10.2026 23:52 « Essaie »). PROTOCOLE PRÉ-ENREGISTRÉ avant toute donnée
du 13.10. Hors ligne ; aucun ordre ; aucune stratégie modifiée.

ÉVÉNEMENT : premier passage d'un côté à ≥ 0,80 (prix d'achat sur Polymarket) avec 30 à 200 s restantes. ALERTE : dans les 10 s qui suivent, les
  portefeuilles « bêtes » (z ≤ −3, 09–10.10) achètent net ce favori ET les « malins » (z ≥ 3, 09–10.10) le vendent net.
EXPLORATION : favori retourné 33 % (09–10.10) et 27 % (11–12.10) avec alerte, contre 15 % sans. Acheter le favori 11 s après le passage :
  avec alerte −18 / −29 / −23 / −9 $ (09, 10, 11, 12.10 ; 10 $ par achat), donc un veto gagne chaque jour ; sans veto +10 $ sur 4 jours.
  Variante « bêtes achètent » seule : −40 / −47 / −64 / +1 $. L'alerte ne sert pas avant le passage (fenêtre avant l'achat : rien).
RÈGLES FIGÉES : V1 = acheter le favori 11 s après le passage sauf alerte (les deux) ; V2 = sauf « bêtes achètent » ; témoin = toujours acheter.
TEST : marchés ≥ 13.10 00:00 UTC (transactions téléchargées après la journée). Critère : V1 − témoin > 0 et taux de retournement avec alerte
  > sans alerte ; IC 90 % par marchés rapporté.
Usage : python3 etude/bot5min/alerte_retournement_h1055.py dossier_polytrades"""
import os, sys, json, gzip, glob, collections, math
import numpy as np
TEST = 1791849600; RNG = np.random.default_rng(1055); fee = lambda p: 0.07 * p * (1 - p)


def main():
    M = {}
    for f in sorted(glob.glob(os.path.join(sys.argv[1], "polytrades_*.json.gz"))):
        d = json.load(gzip.open(f)); M.update({int(k): v for k, v in d["marches"].items()})
    R = collections.defaultdict(lambda: [0, 0])
    for st, v in M.items():
        if not (1791504000 <= st < 1791676800): continue
        res = v["resultat"]
        if not res or max(res.values()) < 0.99: continue
        up = res.get("Up", 0) > 0.5; E = collections.defaultdict(float)
        for ts, w, side, out, px, sz, _ in v["trades"]:
            if sz and out in ("Up", "Down"): E[w] += (1 if out == "Up" else -1) * (1 if side == "BUY" else -1) * sz
        for w, e in E.items():
            if abs(e) >= 10: R[w][0] += 1; R[w][1] += (e > 0) == up
    z = {w: (k - 0.5 * n) / math.sqrt(0.25 * n) for w, (n, k) in R.items() if n >= 30}
    out = {"témoin": [], "V1": [], "V2": []}; al = [0, 0, 0, 0]
    for st, v in M.items():
        res = v["resultat"]
        if st < TEST or not res or max(res.values()) < 0.99: continue
        T = sorted([t for t in v["trades"] if t[0] and t[4] is not None and t[3] in ("Up", "Down") and t[5]], key=lambda x: x[0])
        for X in ("Up", "Down"):
            hit = next((t[0] for t in T if t[2] == "BUY" and 30 <= st + 300 - t[0] <= 200 and (t[4] if t[3] == X else 1 - t[4]) >= 0.80), None)
            if hit is None: continue
            sg = lambda t: (1 if t[3] == X else -1) * (1 if t[2] == "BUY" else -1) * t[5]
            ma = sum(sg(t) for t in T if hit <= t[0] <= hit + 10 and z.get(t[1], 0) >= 3); be = sum(sg(t) for t in T if hit <= t[0] <= hit + 10 and z.get(t[1], 0) <= -3)
            a1 = ma < 0 and be > 0; perdu = res[X] < 0.5
            al[0 if a1 else 2] += 1; al[1 if a1 else 3] += perdu
            bx = [t for t in T if t[3] == X and t[2] == "BUY" and t[0] >= hit + 11]
            if not bx or not (0.02 < bx[0][4] < 0.98): continue
            q = bx[0][4]; pnl = 10 * (res[X] / (q + fee(q)) - 1)
            out["témoin"].append((st, pnl)); out["V1"].append((st, 0.0 if a1 else pnl)); out["V2"].append((st, 0.0 if be > 0 else pnl))
    o = [f"# Bot95 — H1055 : alerte de retournement d'un favori à 80 % — TEST (≥ 13.10)\n",
         f"Favoris retournés : avec alerte {al[1]}/{al[0]} = {100 * al[1] / max(al[0], 1):.0f} % ; sans alerte {al[3]}/{al[2]} = {100 * al[3] / max(al[2], 1):.0f} %.\n",
         "| Règle | Achats | P&L (10 $ par achat) | Écart avec le témoin | IC 90 % |\n|---|---|---|---|---|"]
    base = np.array([p for _, p in out["témoin"]])
    for k in ("témoin", "V1", "V2"):
        v = np.array([p for _, p in out[k]]); d = v - base
        idx = RNG.integers(0, len(d), (4000, len(d))) if len(d) else None; s = d[idx].sum(1) if len(d) else np.array([0.0])
        o.append(f"| {k} | {int(np.sum(v != 0))} | {v.sum():+.0f} | {d.sum():+.0f} | [{np.percentile(s, 5):+.0f} ; {np.percentile(s, 95):+.0f}] |")
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resultat_alerte_retournement_h1055.md"); open(p, "w").write("\n".join(o)); print("\n".join(o))


if __name__ == "__main__":
    main()
