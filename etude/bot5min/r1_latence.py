"""BOT95 — R1 « garde latence » (accord de Pitch, 11.10.2026 16:46). MESURE PURE : aucun ordre, aucun fantôme nouveau, aucun bot modifié.
Question : les signaux Bot95 qui disparaissent avant que nous puissions les acheter gagnent-ils plus souvent que ceux qui restent achetables ?
(constat du 11.10 sur 161 signaux : 44 % de gains pour les partis avant 250 ms contre 22 % pour les restés achetables).
Source : bot95/rapide.json, champ « apres » déjà enregistré à Dublin pour chaque signal (quantité encore achetable au prix du signal à 1…2000 ms).
Par défaut la période réservée (≥ 13.10 00:00 UTC) est EXCLUE ; --hors-echantillon ne lit QUE cette période (verdict du 15.10).
Usage : python3 etude/bot5min/r1_latence.py [--hors-echantillon] → etude/bot5min/resultat_r1_latence[_hors_echantillon].md"""
import json, os, sys, time, collections
import numpy as np

ICI = os.path.dirname(os.path.abspath(__file__)); RACINE = os.path.abspath(os.path.join(ICI, "..", ".."))
HORS_ECH = 1791849600; HE = "--hors-echantillon" in sys.argv
SORTIE = os.path.join(ICI, "resultat_r1_latence" + ("_hors_echantillon" if HE else "") + ".md")
DELAIS = ("50", "100", "250", "500", "1000")
rng = np.random.default_rng(1)


def ic(groupes, fn, n=2000):
    G = [g for g in groupes if g]
    if len(G) < 3: return (float("nan"), float("nan"))
    v = []
    for _ in range(n):
        s = [x for i in rng.integers(0, len(G), len(G)) for x in G[i]]
        r = fn(s)
        if r is not None: v.append(r)
    return (np.percentile(v, 5), np.percentile(v, 95)) if v else (float("nan"), float("nan"))


def main():
    S = [s for s in json.load(open(os.path.join(RACINE, "bot95", "rapide.json")))["signaux"] if s.get("gagnant")]
    S = [s for s in S if (s["start"] >= HORS_ECH) == HE]
    par_cycle = collections.defaultdict(list)
    for s in S: par_cycle[s["start"]].append(s)
    o = []; w = o.append
    w(f"# Bot95 — R1 garde latence ({'période réservée ≥ 13.10' if HE else 'avant le 13.10'}) — mesure pure\n")
    w(f"Généré le {time.strftime('%d.%m.%Y %H:%M', time.gmtime())} UTC. {len(S)} signaux réglés sur {len(par_cycle)} cycles. "
      "« Resté » = encore une quantité achetable au prix du signal après le délai. IC 90 % par rééchantillonnage de cycles.\n")
    if not S: open(SORTIE, "w").write("\n".join(o)); print("\n".join(o)); return
    q = lambda s, d: ((s.get("apres") or {}).get(d) or {}).get("q", 0) or 0
    tg = lambda L: 100 * np.mean([1.0 if s["gagne"] else 0.0 for s in L]) if L else float("nan")
    w("| Délai après décision | Restés | gagnés | prix moyen | Partis | gagnés | prix moyen | Écart partis − restés (points) | IC 90 % |\n|---|---|---|---|---|---|---|---|---|")
    for d in DELAIS:
        R = [s for s in S if q(s, d) > 0]; P = [s for s in S if q(s, d) <= 0]
        f = lambda L: (tg([s for s in L if q(s, d) <= 0]) - tg([s for s in L if q(s, d) > 0])) if any(q(s, d) <= 0 for s in L) and any(q(s, d) > 0 for s in L) else None
        e = f(S); c = ic(list(par_cycle.values()), f)
        w(f"| {d} ms | {len(R)} | {tg(R):.0f} % | {np.mean([s['a0'] for s in R]) if R else float('nan'):.2f} | {len(P)} | {tg(P):.0f} % | "
          f"{np.mean([s['a0'] for s in P]) if P else float('nan'):.2f} | {'%+.0f' % e if e is not None else '—'} | [{c[0]:+.0f} ; {c[1]:+.0f}] |")
    w("\n**Par variante (250 ms)**\n")
    w("| Variante | Signaux | Restés : gagnés | Partis : gagnés | P&L réel à 250 ms ($) |\n|---|---|---|---|---|")
    for nom in sorted({s["nom"] for s in S}):
        L = [s for s in S if s["nom"] == nom]; R = [s for s in L if q(s, "250") > 0]; P = [s for s in L if q(s, "250") <= 0]
        pnl = sum(((s.get("resultat") or {}).get("250") or 0) for s in L)
        w(f"| {nom} | {len(L)} | {len(R)} : {tg(R):.0f} % | {len(P)} : {tg(P):.0f} % | {pnl:+.2f} |")
    w("\nLecture : un écart positif et stable signifie que les signaux gagnants sont pris par d'autres avant nous (sélection adverse par la latence). "
      "Aucune règle n'est tirée de cette mesure sans décision de Pitch.\n")
    open(SORTIE, "w").write("\n".join(o)); print("\n".join(o))


if __name__ == "__main__":
    main()
