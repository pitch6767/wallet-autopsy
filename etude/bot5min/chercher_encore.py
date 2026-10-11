"""BOT95 — « Cherche encore » (Pitch, 11.10.2026 16:22). Lecture seule, hors ligne, aucun ordre. Période réservée (≥ 13.10) exclue ; marchés tronqués exclus.
 E1  QUI NOUS VEND NOS BILLETS : pour chaque signal Bot95 réglé (bot95/rapide.json), les makers qui ont vendu ce côté (ou acheté l'autre côté au prix
     complémentaire) au prix du signal ou mieux dans les 10 s : qui sont-ils, sont-ils rentables, et le signal gagne-t-il ?
 E2  PRENEURS EN MIROIR : résultat des preneurs par prix payé, par minute et par taille (le miroir des makers).
 E3  FAVORI : élan ou biais ? Résultat des achats maker sur le favori / l'outsider selon que le prix a MONTÉ ou BAISSÉ dans les 30 s précédentes
     (connu à l'instant de l'achat), et selon l'écart au prix 0,5.
Usage : python3 etude/bot5min/chercher_encore.py makers_suivi.json → etude/bot5min/resultat_chercher_encore.md"""
import json, os, sys, collections, bisect, time
import numpy as np

ICI = os.path.dirname(os.path.abspath(__file__)); RACINE = os.path.abspath(os.path.join(ICI, "..", "..")); HORS_ECH = 1791849600
SORTIE = os.path.join(ICI, "resultat_chercher_encore.md")


def main():
    base = json.load(open(sys.argv[1]))
    M = {int(k): v for k, v in base["marches"].items() if int(k) < HORS_ECH and not v.get("tronque")}
    # rentabilité des portefeuilles (makers) sur tous les marchés complets
    pnl = collections.Counter(); vol = collections.Counter()
    for st, mk in M.items():
        g = mk["gagnant"]
        for w, role, out, side, sz, p, ts in mk["ex"]:
            win = 1.0 if out == g else 0.0; vol[w] += sz * p; pnl[w] += sz * (win - p) if side == "BUY" else sz * (p - win)
    o = []; w_ = o.append
    w_("# Bot95 — Chercher encore : qui nous vend nos billets, preneurs en miroir, favori (PRÉLIMINAIRE)\n")
    w_(f"{len(M)} marchés complets (tronqués exclus — biais possible : ce sont les plus actifs).\n")
    # ---------------- E1
    SIG = [s for s in json.load(open(os.path.join(RACINE, "bot95", "rapide.json")))["signaux"] if s.get("gagnant") and s["start"] in M]
    w_("## E1. Qui vend les billets que Bot95 veut acheter ?\n")
    vend = collections.Counter(); vend_q = collections.Counter(); ns = 0; R = []
    for s in SIG:
        mk = M[s["start"]]; t0 = s["tDecision"] / 1000; X = s["cote"]; a0 = s["a0"]
        parts = collections.Counter()
        for w, role, out, side, sz, p, ts in mk["ex"]:
            if role != "M" or not (t0 - 1 <= ts <= t0 + 10): continue
            # le maker vend X à ≤ a0 : SELL X à p ≤ a0, ou BUY l'autre côté à ≥ 1 − a0
            if (out == X and side == "SELL" and p <= a0 + 1e-9) or (out != X and side == "BUY" and p >= 1 - a0 - 1e-9):
                parts[w] += sz
        if parts: ns += 1
        for w, q in parts.items(): vend[w] += 1; vend_q[w] += q
        R.append((s, sum(parts.values())))
    w_(f"Signaux Bot95 réglés sur des marchés lus : {len(SIG)} ; signaux où au moins un maker a vendu ce côté au prix du signal ou mieux dans les 10 s : {ns}.\n")
    w_("| Vendeur (maker) | Signaux servis | Parts vendues | Résultat global du portefeuille | par $ |\n|---|---|---|---|---|")
    for w, n in vend.most_common(15):
        w_(f"| `{w}` | {n} | {vend_q[w]:.0f} | {pnl[w]:+.0f} $ | {100 * pnl[w] / vol[w] if vol[w] else 0:+.1f} % |")
    sv = [s for s, q in R if q > 0]; nsv = [s for s, q in R if q == 0]
    gw = lambda L: (100 * np.mean([1.0 if x["gagne"] else 0.0 for x in L]), np.mean([x["a0"] for x in L])) if L else (float("nan"), float("nan"))
    w_(f"\nSignaux servis par des makers : gagnés {gw(sv)[0]:.0f} % (prix moyen {gw(sv)[1]:.2f}) ; signaux NON servis : gagnés {gw(nsv)[0]:.0f} % (prix moyen {gw(nsv)[1]:.2f}).\n")
    # ---------------- E2
    w_("## E2. Les preneurs en miroir\n")
    D = collections.defaultdict(lambda: [0.0, 0.0, 0])
    for st, mk in M.items():
        g = mk["gagnant"]
        for w, role, out, side, sz, p, ts in mk["ex"]:
            if role != "P" or not (st <= ts < st + 300): continue        # horodatages hors du marché (rares) ignorés
            X, px = (out, p) if side == "BUY" else (("Down" if out == "Up" else "Up"), 1 - p)
            win = 1.0 if g == X else 0.0; fee = sz * 0.07 * p * (1 - p)
            for k in (("prix", min(int(px * 10), 9)), ("minute", min(int((ts - st) // 60), 4)), ("taille", 0 if sz * p < 10 else 1 if sz * p < 50 else 2 if sz * p < 200 else 3)):
                D[k][0] += sz * px; D[k][1] += sz * (win - px) - fee; D[k][2] += 1
    w_("| Découpage | Tranche | Exécutions | Résultat net de frais par $ |\n|---|---|---|---|")
    noms = {"taille": ["< 10 $", "10–50 $", "50–200 $", "≥ 200 $"]}
    for (k, v), (c, r, n) in sorted(D.items()):
        lab = f"{v / 10:.1f}–{(v + 1) / 10:.1f}" if k == "prix" else (f"{v * 60}–{v * 60 + 60} s" if k == "minute" else noms["taille"][v])
        w_(f"| {k} | {lab} | {n} | {100 * r / c if c else 0:+.1f} % |")
    # ---------------- E3
    w_("\n## E3. L'effet favori : élan ou biais permanent ?\n")
    E = collections.defaultdict(lambda: [0.0, 0.0, 0])
    for st, mk in M.items():
        g = mk["gagnant"]; tp = sorted((x[6], x[2], x[5]) for x in mk["ex"] if x[1] == "P"); T = [x[0] for x in tp]
        def px_up(t):
            i = bisect.bisect_left(T, t) - 1
            if i < 0: return None
            ts, o, p = tp[i]; return p if o == "Up" else 1 - p
        for w, role, out, side, sz, p, ts in mk["ex"]:
            if role != "M": continue
            X, px = (out, p) if side == "BUY" else (("Down" if out == "Up" else "Up"), 1 - p)
            u0 = px_up(ts); u30 = px_up(ts - 30)
            if u0 is None or u30 is None: continue
            mvt = (u0 - u30) if X == "Up" else (u30 - u0)               # variation du prix de X sur les 30 s précédentes
            fav = "favori" if px >= 0.5 else "outsider"; el = "a monté" if mvt > 0.02 else ("a baissé" if mvt < -0.02 else "stable")
            win = 1.0 if g == X else 0.0; k = (fav, el); E[k][0] += sz * px; E[k][1] += sz * (win - px); E[k][2] += 1
    w_("| Côté acheté (maker) | Prix du côté sur les 30 s précédentes | Remplissages | Résultat par $ |\n|---|---|---|---|")
    for k in sorted(E): c, r, n = E[k]; w_(f"| {k[0]} | {k[1]} | {n} | {100 * r / c if c else 0:+.1f} % |")
    w_("\nLecture : si le favori gagne surtout quand son prix vient de monter, c'est de l'ÉLAN (le marché sous-réagit) ; s'il gagne même stable, c'est un biais "
       "favori / outsider (les outsiders sont trop chers).\n")
    w_("## Limites\n- Une journée ; marchés les plus actifs exclus (tronqués) — à refaire sur les données complètes.\n")
    open(SORTIE, "w").write("\n".join(o)); print("\n".join(o))


if __name__ == "__main__":
    main()
