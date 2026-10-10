"""Morts à l'arrivée : premier désaccord ≥ 0,20 du cycle (modèle du bot) — l'offre vue au signal existe-t-elle encore 0,25 / 0,5 / 1 / 2 s plus tard,
au même prix ou mieux ? Et que valaient les offres disparues ?"""
import sys
sys.path.insert(0, "etude/bot5min")
exec(open("etude/bot5min/diversite.py").read().split("VAR = [")[0])
S = {st: premier(st, lambda r, up, f, a, tl: f - a >= 0.20) for st in valides}
S = {st: s for st, s in S.items() if s}
out = ["# Morts à l'arrivée — premier désaccord ≥ 0,20 du cycle", "", f"{len(S)} signaux. Meilleur vendeur seul, quantité affichée, 50 $ maximum, jamais plus cher que le prix vu au signal.", "",
       "| Délai | Encore achetables | Morts à l'arrivée | Ce que valaient les morts (exécution au signal) | dont gagnants | Résultat de ceux encore achetables |", "|---|---|---|---|---|---|"]
z0 = {st: execu(st, s, 0) for st, s in S.items()}
for d in (0.25, 0.5, 1, 2):
    zd = {st: execu(st, s, d) for st, s in S.items()}
    base = [st for st in S if z0[st]]; mort = [st for st in base if not zd[st]]; vit = [st for st in base if zd[st]]
    out.append(f"| {d} s | {len(vit)} / {len(base)} | {len(mort)} ({100 * len(mort) / len(base):.0f} %) | {f0(sum(z0[st]['pn'] for st in mort))} | {sum(1 for st in mort if z0[st]['pn'] > 0)} | {f0(sum(zd[st]['pn'] for st in vit))} |")
open("etude/bot5min/resultat_morts_arrivee.md", "w").write("\n".join(out)); print("\n".join(out))
