"""Validation FUTURE de B0 / B1 (figés) contre D sur les cycles NOUVEAUX du fantôme R4 vivant (Dublin), à partir de bot95/rapide.json.
D = 1re tentative R4 ; B0 = + relances R4 si la 1re tentative a eu un fill partiel ; B1 = B0 seulement si profondeur au signal ≥ 25 $.
Une décision par cycle et par côté (le premier signal) ; IC 90 % par cycles. Période réservée (≥ 13.10) exclue, sauf --hors-echantillon (verdict).
Aucun ordre, aucun réglage modifié. Usage : python3 etude/bot5min/validation_b0b1_vivant.py [--hors-echantillon]"""
import json, os, sys, time
import numpy as np
ICI = os.path.dirname(os.path.abspath(__file__)); RACINE = os.path.abspath(os.path.join(ICI, "..", ".."))
HORS_ECH = 1791849600; DEB_R4 = 1791731400; SEUIL = 25.0; HE = "--hors-echantillon" in sys.argv
SORTIE = os.path.join(ICI, "resultat_validation_b0b1_vivant" + ("_hors_echantillon" if HE else "") + ".md")
rng = np.random.default_rng(1)


def pnl(s, nom):
    T = sorted(s["r4"]["R4"]["tentatives"], key=lambda x: x[0]); y = 1.0 if s["gagne"] else 0.0
    att = [(t[6] or 0.0, t[7] or 0.0) for t in T]
    if not att: return 0.0
    q1, c1 = att[0]
    comp = nom != "D" and q1 > 0 and (nom == "B0" or (s.get("q0") or 0) * s["a0"] >= SEUIL)
    qc = sum(a[0] for a in att[1:]) if comp else 0.0; cc = sum(a[1] for a in att[1:]) if comp else 0.0
    return (q1 + qc) * y - c1 - cc


def ic(G, fn, n=3000):
    if len(G) < 3: return (float("nan"), float("nan"))
    v = [fn([x for i in rng.integers(0, len(G), len(G)) for x in G[i]]) for _ in range(n)]
    return (float(np.percentile(v, 5)), float(np.percentile(v, 95)))


S = [s for s in json.load(open(os.path.join(RACINE, "bot95", "rapide.json")))["signaux"]
     if s.get("gagnant") and (s.get("r4") or {}).get("R4") and s["start"] >= DEB_R4 and ((s["start"] >= HORS_ECH) == HE)]
S.sort(key=lambda s: s["tDecision"]); vu = set(); U = []
for s in S:
    if (s["start"], s["cote"]) not in vu: vu.add((s["start"], s["cote"])); U.append(s)
G = list({s["start"]: [x for x in U if x["start"] == s["start"]] for s in U}.values())
o = [f"# Bot95 — Validation future B0 / B1 contre D (fantôme R4 vivant{', PÉRIODE RÉSERVÉE' if HE else ''})\n",
     f"Mis à jour le {time.strftime('%d.%m.%Y %H:%M', time.gmtime())} UTC. Signaux réglés avec R4 : {len(S)} ; décisions uniques : {len(U)} sur {len(G)} cycles.\n",
     "| Politique | P&L ($) | / décision | IC 90 % | vs D ($) | IC 90 % de l'écart / décision | compléments : gagnants / perdants |", "|---|---|---|---|---|---|---|"]
for nom in ("D", "B0", "B1"):
    p = [pnl(s, nom) for s in U]; c = ic(G, lambda z: float(np.mean([pnl(s, nom) for s in z]))); d = ic(G, lambda z: float(np.mean([pnl(s, nom) - pnl(s, "D") for s in z])))
    comp = [s for s in U if abs(pnl(s, nom) - pnl(s, "D")) > 1e-9]
    o.append(f"| {nom} | {sum(p):+.0f} | {np.mean(p) if p else 0:+.2f} | [{c[0]:+.2f} ; {c[1]:+.2f}] | {sum(p) - sum(pnl(s, 'D') for s in U):+.0f} | [{d[0]:+.2f} ; {d[1]:+.2f}] | "
             f"{sum(1 for s in comp if s['gagne'])} / {sum(1 for s in comp if not s['gagne'])} |")
o.append("\nVerdict : une amélioration n'est retenue que si l'IC 90 % de l'écart à D est entièrement > 0. Aucun seuil n'est ré-optimisé.\n")
open(SORTIE, "w").write("\n".join(o)); print("\n".join(o))
