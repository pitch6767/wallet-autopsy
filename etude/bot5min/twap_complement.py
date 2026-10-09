"""TWAP fin — fiabilité selon le temps restant, bid/spread, contrat opposé, surface de prime (idées ChatGPT 10.10.2026, 00:53). Aucun fantôme modifié.
Apprentissage / validation séparés dans le temps : 60 % premiers cycles / 40 % derniers. Tout ce qui sert à décider est connu à l'instant de la décision."""
import sys
sys.path.insert(0, "etude/bot5min")
exec(open("etude/bot5min/twap_etudes.py").read().split("# ---------- B.")[0])
bid = lambda x, up: x["ub"] if up else x["db"]
opp_ask = lambda x, up: x["da"] if up else x["ua"]
opp_sz = lambda x, up: x["dz"] if up else x["uz"]
def apres(L, i, dl):
    t0 = L[i]["t"] + dl
    return next((j for j in range(i, len(L)) if L[j]["t"] >= t0 - 1e-6), None)
def avant(L, i, dl):
    t0 = L[i]["t"] - dl
    return next((j for j in range(i, -1, -1) if L[j]["t"] <= t0 + 1e-6), None)
CUT = cyc[int(len(cyc) * 0.6)]
per = lambda st: "appr." if st < CUT else "valid."
R = []
for st, (i, up) in SIG.items():
    L = CY[st]["L"]; x = L[i]; gm = CY[st]["up"] if up else not CY[st]["up"]; pp = pnl(x, up, gm)
    if pp: R.append(dict(st=st, i=i, up=up, gm=gm, it=(pp[0], pp[1], gm), x=x, L=L))
def table(G, ordre=None):
    o = [HH]
    for k in (ordre or sorted(G)):
        if G.get(k): o.append(f"| {k} | {stats(G[k])} |")
    return o
def deux(G, cle, it, st): G[cle].append(it); G[f"{cle} — {per(st)}"].append(it)
out = [f"# TWAP fin — nouvelles idées : fiabilité, bid/spread, contrat opposé (BTC, {len(cyc)} cycles, {hs(cyc[0])} → {hs(cyc[-1] + 300)})", "",
       f"Signaux de référence : les {len(R)} premiers signaux TWAP fin original de chaque cycle (avantage ≥ 0,20, 90-20 s), +2 323 $. Apprentissage avant le {hs(CUT)}, validation après.", ""]
# ---------- A. fiabilite selon le temps restant
out += ["## A. Qui prévoit le mieux le gagnant, seconde par seconde ? (Brier, plus bas = meilleur, une mesure par seconde)", "",
        "| Temps restant | Mesures | Moteur original | Sauts | Spot-perp | Carnet (milieu) | Quand ils divergent > 15 pts : moteur / carnet (mesures) |", "|---|---|---|---|---|---|---|"]
for a_, b_ in ((80, 90), (70, 80), (60, 70), (50, 60), (40, 50), (30, 40), (20, 30), (10, 20), (1, 10)):
    M = []
    for st in cyc:
        vu = set()
        for x in CY[st]["L"]:
            s = int(x["t"])
            if a_ <= x["tl"] < b_ and x["mid"] is not None and s not in vu: vu.add(s); M.append((x["p0"], x["pT"], x["pS"], x["mid"], CY[st]["up"]))
    if len(M) < 100: continue
    A = np.array(M, float); y = A[:, 4]; br = lambda c: np.mean((A[:, c] - y) ** 2)
    D = A[np.abs(A[:, 0] - A[:, 3]) > 0.15]
    dd = f"{np.mean((D[:, 0] - D[:, 4]) ** 2):.3f} / {np.mean((D[:, 3] - D[:, 4]) ** 2):.3f} ({len(D)})" if len(D) > 30 else "—"
    out.append(f"| {a_}-{b_} s | {len(M)} | {br(0):.4f} | {br(1):.4f} | {br(2):.4f} | {br(3):.4f} | {dd} |")
out += ["", "Rentabilité des signaux selon le moment du signal :", ""]
G = collections.defaultdict(list)
for r in R:
    tl = r["x"]["tl"]; k = "signal 90-60 s" if tl > 60 else "signal 60-40 s" if tl > 40 else "signal 40-20 s"
    deux(G, k, r["it"], r["st"])
out += table(G)
# ---------- decision frontier / regret
out += ["", "## A bis. Acheter tout de suite, attendre le prochain Chainlink, ou ne rien faire — par fenêtre (mêmes signaux)", "",
        "| Fenêtre du signal | Signaux | Tout de suite | Attendre Chainlink | Achats après attente | Pertes évitées | Gains manqués (dont jackpots ≥ 5×) |", "|---|---|---|---|---|---|---|"]
FEN = collections.defaultdict(lambda: dict(n=0, im=0.0, at=0.0, na=0, ev=0.0, ma=0.0, jk=0))
for r in R:
    L, i, up, x = r["L"], r["i"], r["up"], r["x"]; tl = x["tl"]
    k = "90-60 s" if tl > 60 else "60-40 s" if tl > 40 else "40-20 s"
    F = FEN[k]; F["n"] += 1; F["im"] += r["it"][0]
    j = next((j for j in range(i + 1, len(L)) if L[j]["cl_t"] and x["cl_t"] and L[j]["cl_t"] > x["cl_t"] and L[j]["cl_v"] != x["cl_v"]), None)
    achete = False
    if j is not None:
        y = L[j]
        if ask(y, up) is not None and pr(y, "p0", up) - ask(y, up) >= 0.20:
            p2 = pnl(y, up, r["gm"])
            if p2: F["at"] += p2[0]; F["na"] += 1; achete = True
    if not achete:
        if r["it"][0] < 0: F["ev"] += -r["it"][0]
        else:
            F["ma"] += r["it"][0]; F["jk"] += r["it"][0] >= 4 * r["it"][1]
for k in ("90-60 s", "60-40 s", "40-20 s"):
    F = FEN[k]
    out.append(f"| {k} | {F['n']} | {f0(F['im'])} | {f0(F['at'])} | {F['na']} | {f0(F['ev'])} | {f0(F['ma'])} ({F['jk']}) |")
# ---------- B. bid / spread
out += ["", "## B. Le bid et le spread de notre côté apportent-ils une information en plus de l'avantage ?", ""]
G = collections.defaultdict(list)
for r in R:
    L, i, up, x = r["L"], r["i"], r["up"], r["x"]; a0, b0 = ask(x, up), bid(x, up)
    if b0 is None: deux(G, "pas de bid de notre côté", r["it"], r["st"]); continue
    spd = a0 - b0
    deux(G, "spread ≤ 2 c" if spd <= 0.02 + 1e-9 else "spread 3-6 c" if spd <= 0.06 + 1e-9 else "spread > 6 c", r["it"], r["st"])
    j = avant(L, i, 3)
    if j is None or j == i or bid(L[j], up) is None or ask(L[j], up) is None: continue
    db_, da_ = b0 - bid(L[j], up), a0 - ask(L[j], up)
    deux(G, "bid monté ≥ 3 c en 3 s, vendeur pas monté (idée 11)" if db_ >= 0.03 and da_ <= 0.005 else "autres cas (idée 11)", r["it"], r["st"])
    sp0 = ask(L[j], up) - bid(L[j], up)
    if spd < sp0 - 0.015:
        deux(G, "spread resserré par le BID qui monte (idée 12)" if db_ > -da_ else "spread resserré par le VENDEUR qui baisse (idée 12)", r["it"], r["st"])
    bapt = db_ - da_
    deux(G, "BAPT > 0 : bid monte plus que le vendeur (idée 13)" if bapt > 0.01 else "BAPT < 0 (idée 13)" if bapt < -0.01 else "BAPT ≈ 0 (idée 13)", r["it"], r["st"])
ordreB = []
for k in ("spread ≤ 2 c", "spread 3-6 c", "spread > 6 c", "pas de bid de notre côté", "bid monté ≥ 3 c en 3 s, vendeur pas monté (idée 11)", "autres cas (idée 11)",
          "spread resserré par le BID qui monte (idée 12)", "spread resserré par le VENDEUR qui baisse (idée 12)", "BAPT > 0 : bid monte plus que le vendeur (idée 13)", "BAPT ≈ 0 (idée 13)", "BAPT < 0 (idée 13)"):
    ordreB += [k, f"{k} — appr.", f"{k} — valid."]
out += table(G, ordreB)
# ---------- 5. enveloppe de stabilite
out += ["", "## Idée 4-5. Les trois modèles d'accord ou dispersés au moment du signal", ""]
disp = [abs(max(r["x"]["p0"], r["x"]["pT"], r["x"]["pS"]) - min(r["x"]["p0"], r["x"]["pT"], r["x"]["pS"])) for r in R]
md = float(np.median(disp)); G = collections.defaultdict(list)
for r, d in zip(R, disp): deux(G, f"dispersion ≤ médiane ({md:.3f})" if d <= md else "dispersion > médiane", r["it"], r["st"])
out += table(G)
# ---------- C. contrat oppose
out += ["", "## C. Sortie par le contrat opposé : vente directe au bid contre « acheter l'opposé + fusionner » (positions des 140 signaux)", "",
        "| Moment | Mesures | Vente directe (bid) | Voie synthétique (1 − vendeur opposé − frais) | Synthétique meilleure | Gain moyen quand meilleure | Règlement (garder) |", "|---|---|---|---|---|---|---|"]
for dl in (1, 5, 10, 20):
    V = []
    for r in R:
        j = apres(r["L"], r["i"], dl)
        if j is None: continue
        y = r["L"][j]; b, oa = bid(y, r["up"]), opp_ask(y, r["up"])
        if b is None or oa is None: continue
        syn = 1 - oa - FEE(oa); dirc = b - FEE(b); V.append((dirc, syn, 1.0 if r["gm"] else 0.0))
    if V:
        A = np.array(V); m = A[:, 1] > A[:, 0]
        out.append(f"| +{dl} s | {len(V)} | {A[:, 0].mean():.3f} | {A[:, 1].mean():.3f} | {m.sum()} | {(A[m, 1] - A[m, 0]).mean() * 100 if m.any() else 0:+.1f} c | {A[:, 2].mean():.3f} |")
out += ["", "Verrouillage (idée 18) : acheter l'opposé à +k s et garder la paire = valeur 1 $ sûre, contre garder seul :", "",
        "| Moment | Mesures | Gain verrouillé moyen par jeton | Gain moyen en gardant seul | Verrouillage meilleur (cas) |", "|---|---|---|---|---|"]
for dl in (1, 5, 10, 20):
    V = []
    for r in R:
        j = apres(r["L"], r["i"], dl)
        if j is None: continue
        y = r["L"][j]; oa = opp_ask(y, r["up"]); a0 = ask(r["x"], r["up"])
        if oa is None: continue
        lock = 1 - a0 - FEE(a0) - oa - FEE(oa); hold = (1 if r["gm"] else 0) - a0 - FEE(a0); V.append((lock, hold))
    if V:
        A = np.array(V); out.append(f"| +{dl} s | {len(V)} | {A[:, 0].mean():+.3f} | {A[:, 1].mean():+.3f} | {(A[:, 0] > A[:, 1]).sum()} |")
# ---------- 14/17. incoherences des deux carnets
nm = nb = 0; tot = 0; Gm = []; Gb = []
for st in cyc:
    for x in CY[st]["L"]:
        if x["ua"] is None or x["da"] is None: continue
        tot += 1
        c = x["ua"] + x["da"] + FEE(x["ua"]) + FEE(x["da"])
        if c < 1: nm += 1; Gm.append(((1 - c) * min(x["uz"], x["dz"]), st))
        if x["ub"] is not None and x["db"] is not None:
            v = x["ub"] + x["db"] - FEE(x["ub"]) - FEE(x["db"])
            if v > 1: nb += 1; Gb.append((v - 1, st))
out += ["", "## Idées 14 et 17. Incohérences entre les carnets Up et Down (toutes les mesures, 4 par seconde)", "",
        f"- Acheter Up + Down au vendeur coûte moins de 1 $ après frais : **{nm}** mesures sur {tot} ({len({s for _, s in Gm})} cycles), gain total théorique {sum(g for g, _ in Gm):.2f} $ (en sommant toutes les mesures, donc très surestimé).",
        f"- Vendre Up + Down à l'acheteur rapporte plus de 1 $ après frais : **{nb}** mesures ({len({s for _, s in Gb})} cycles).", ""]
# ---------- 6. marche trop sur de lui
out += ["## Idée 6. Le carnet est très sûr (côté opposé à 10 c ou moins) : le côté bon marché vaut-il plus que son prix ? (60-20 s, une mesure par cycle et par tranche)", "",
        "| Notre probabilité pour le côté bon marché | Mesures | Prix moyen | Gagnés | Écart gagné − prix − frais |", "|---|---|---|---|---|"]
T = collections.defaultdict(dict)
for st in cyc:
    for x in CY[st]["L"]:
        if not (20 <= x["tl"] <= 60): continue
        for up in (True, False):
            a = ask(x, up)
            if a is None or not (0.01 <= a <= 0.10): continue
            p = pr(x, "p0", up); k = "< prix" if p < a else "prix à prix + 5 pts" if p < a + 0.05 else "prix + 5 à 15 pts" if p < a + 0.15 else "> prix + 15 pts"
            T[k].setdefault((st, up), (a, CY[st]["up"] == up))
for k in ("< prix", "prix à prix + 5 pts", "prix + 5 à 15 pts", "> prix + 15 pts"):
    v = list(T[k].values())
    if len(v) >= 15: out.append(f"| {k} | {len(v)} | {np.mean([a for a, _ in v]):.3f} | {100 * np.mean([g for _, g in v]):.1f} % | {100 * np.mean([g - a - FEE(a) for a, g in v]):+.1f} pts |")
# ---------- 8. surface de prime
out += ["", "## Idée 8. Surface « prix × temps restant » sur TOUTES les cotations (une par cycle, par côté et par case) : gagné − prix − frais, en points", "",
        "| Prix du contrat | 90-60 s appr. | 90-60 s valid. | 60-40 s appr. | 60-40 s valid. | 40-20 s appr. | 40-20 s valid. |", "|---|---|---|---|---|---|---|"]
S8 = collections.defaultdict(dict)
for st in cyc:
    for x in CY[st]["L"]:
        if not (20 <= x["tl"] <= 90): continue
        tb = "90-60" if x["tl"] > 60 else "60-40" if x["tl"] > 40 else "40-20"
        for up in (True, False):
            a = ask(x, up)
            if a is None or not (0.01 <= a <= 0.99): continue
            pb = 0 if a < 0.05 else 1 if a < 0.15 else 2 if a < 0.35 else 3 if a < 0.65 else 4 if a < 0.85 else 5 if a < 0.95 else 6
            S8[(pb, tb, per(st))].setdefault((st, up), (a, CY[st]["up"] == up))
LAB = ["1-5 c", "5-15 c", "15-35 c", "35-65 c", "65-85 c", "85-95 c", "95-99 c"]
for pb in range(7):
    cells = []
    for tb in ("90-60", "60-40", "40-20"):
        for pe in ("appr.", "valid."):
            v = list(S8[(pb, tb, pe)].values())
            cells.append(f"{100 * np.mean([g - a - FEE(a) for a, g in v]):+.1f} ({len(v)})" if len(v) >= 20 else "—")
    out.append(f"| {LAB[pb]} | " + " | ".join(cells) + " |")
out += ["", "Entre parenthèses : nombre de mesures. Une case n'est intéressante que si elle est positive en apprentissage ET en validation."]
open("etude/bot5min/resultat_twap_complement.md", "w").write("\n".join(out)); print("\n".join(out))
