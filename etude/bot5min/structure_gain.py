"""BOT95 — Pourquoi la moyenne est positive alors que la médiane est négative (Pitch, 11.10.2026 21:19). Hors ligne, aucun ordre.
Source : bot95/rapide.json (signaux réglés avant le 13.10, résultat mesuré à Dublin à 250 ms). IC 90 % par rééchantillonnage de CYCLES.
Décision unique = premier signal par cycle et par côté (les variantes du même cycle achètent le même billet)."""
import json, os, numpy as np
R = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
S = sorted([s for s in json.load(open(os.path.join(R, "bot95", "rapide.json")))["signaux"] if s.get("gagnant") and s["start"] < 1791849600], key=lambda s: s["tDecision"])
U = {}; [U.setdefault((s["start"], s["cote"]), s) for s in S]; U = list(U.values())
rng = np.random.default_rng(2); r = lambda s: ((s.get("resultat") or {}).get("250") or 0)
q = lambda s, d: (((s.get("apres") or {}).get(d) or {}).get("q") or 0); ret = lambda s: q(s, "250") < 0.5 * (s.get("achetable0") or {}).get("q", 0)
def boot(L, f, n=3000):
    G = list({s["start"]: [x for x in L if x["start"] == s["start"]] for s in L}.values()); v = []
    for _ in range(n):
        z = [x for i in rng.integers(0, len(G), len(G)) for x in G[i]]
        try: v.append(f(z))
        except Exception: pass
    return np.percentile(v, 5), np.percentile(v, 95)
o = [f"# Bot95 — Structure du gain (moyenne > 0, médiane < 0)\n", f"{len(S)} signaux réglés, {len({s['start'] for s in S})} cycles ; {len(U)} décisions uniques.\n"]
top = sorted(S, key=lambda s: -r(s))[:5]
o.append(f"5 meilleurs signaux : {sum(r(s) for s in top):+.0f} $ sur {sum(r(s) for s in S):+.0f} $ ; ils viennent de {len({s['start'] for s in top})} cycles seulement.\n")
o.append("| Échantillon | Prix | Signaux | Cycles | Taux de gain | Prix moyen | Gain − prix (points) | IC 90 % | Modèle |\n|---|---|---|---|---|---|---|---|---|")
for nom, L in (("tous", S), ("décisions uniques", U)):
    for lo, hi in ((0, .1), (.1, .2), (.2, .3), (.3, .5), (0, .5)):
        B = [s for s in L if lo <= s["a0"] < hi]
        if not B: continue
        f = lambda z: np.mean([x["gagne"] for x in z]) - np.mean([x["a0"] for x in z]); c = boot(B, f)
        o.append(f"| {nom} | {lo:.1f}–{hi:.1f} | {len(B)} | {len({s['start'] for s in B})} | {100 * np.mean([s['gagne'] for s in B]):.0f} % | {100 * np.mean([s['a0'] for s in B]):.0f} % | {100 * f(B):+.1f} | [{100 * c[0]:+.1f} ; {100 * c[1]:+.1f}] | {100 * np.mean([s['modele'] for s in B]):.0f} % |")
W = [s for s in U if ret(s)]; K = [s for s in U if not ret(s)]
f = lambda z: np.mean([x["gagne"] - x["a0"] for x in z if ret(x)]) - np.mean([x["gagne"] - x["a0"] for x in z if not ret(x)]); c = boot(U, f)
o.append(f"\nOffres retirées avant 250 ms (décisions uniques) : {len(W)}, gain {100 * np.mean([s['gagne'] for s in W]):.0f} % au prix {100 * np.mean([s['a0'] for s in W]):.0f} % ; restées : {len(K)}, gain {100 * np.mean([s['gagne'] for s in K]):.0f} % au prix {100 * np.mean([s['a0'] for s in K]):.0f} %. "
         f"Écart (gain − prix) retirées − restées : {100 * f(U):+.1f} points [{100 * c[0]:+.1f} ; {100 * c[1]:+.1f}]. Début de retrait médian {np.median([s['premiereBaisse_ms'] for s in W if s.get('premiereBaisse_ms') is not None]):.0f} ms, disparition médiane {np.median([s['disparu_ms'] for s in W if s.get('disparu_ms')]):.0f} ms.\n")
o.append("| Connu à la décision | Part retirée : oui / non | Gain − prix : oui / non |\n|---|---|---|")
for k, fn in (("déclenché par le carnet Polymarket", lambda s: s["declencheur"] == "poly"), ("profondeur au signal < 50 parts", lambda s: s["q0"] < 50), ("écart modèle − prix ≥ 0,25", lambda s: s["ecart"] >= 0.25)):
    A = [s for s in U if fn(s)]; B = [s for s in U if not fn(s)]
    o.append(f"| {k} | {100 * np.mean([ret(x) for x in A]):.0f} % / {100 * np.mean([ret(x) for x in B]):.0f} % | {100 * np.mean([x['gagne'] - x['a0'] for x in A]):+.1f} / {100 * np.mean([x['gagne'] - x['a0'] for x in B]):+.1f} |")
open(os.path.join(R, "etude", "bot5min", "resultat_structure_gain.md"), "w").write("\n".join(o)); print("\n".join(o))
