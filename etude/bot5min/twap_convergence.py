"""Convergence attribution + double alpha (idées ChatGPT 10.10.2026 nuit) — BTC, mêmes 140 signaux que twap_etudes.py (moteur TWAP fin original, avantage ≥ 0,20, 90-20 s).
Aucun fantôme modifié. Les événements après le signal servent uniquement au diagnostic, jamais à décider un achat passé (sauf les lignes « politique » explicitement marquées)."""
import sys
sys.path.insert(0, "etude/bot5min")
_src = open("etude/bot5min/twap_etudes.py").read().split("# ---------- B.")[0]
exec(_src)
bid = lambda x, up: x["ub"] if up else x["db"]
def apres(L, i, dl):
    t0 = L[i]["t"] + dl
    return next((L[j] for j in range(i, len(L)) if L[j]["t"] >= t0 - 1e-6), None)
def avant(L, i, dl):
    t0 = L[i]["t"] - dl
    return next((L[j] for j in range(i, -1, -1) if L[j]["t"] <= t0 + 1e-6), None)
def mecanique(xp, x):
    """proba qu'on aurait si rien de nouveau n'était arrivé : même moyenne attendue, seule l'incertitude a diminué avec le temps"""
    return phi(xp["z"] * xp["sd"] / x["sd"])
R = []
for st, (i, up) in SIG.items():
    L = CY[st]["L"]; x = L[i]; gm = CY[st]["up"] if up else not CY[st]["up"]; pp = pnl(x, up, gm)
    if not pp: continue
    d = dict(st=st, up=up, gm=gm, pn=pp[0], mise=pp[1], a0=ask(x, up), p0=pr(x, "p0", up), b0=bid(x, up))
    for dl in (0.25, 0.5, 1, 2, 5, 10, 20):
        y = apres(L, i, dl)
        d[dl] = None if y is None else dict(p=pr(y, "p0", up), a=ask(y, up), b=bid(y, up))
    xp = avant(L, i, 3)
    if xp is not None and xp["t"] < x["t"]:
        d["pre_dp"] = pr(x, "p0", up) - pr(xp, "p0", up)
        mec = mecanique(xp, x); mec = mec if up else 1 - mec
        d["pre_mec"] = mec - pr(xp, "p0", up); d["pre_inat"] = pr(x, "p0", up) - mec
        d["pre_da"] = (ask(x, up) - ask(xp, up)) if ask(xp, up) is not None else None
        d["pre_edge"] = (pr(xp, "p0", up) - ask(xp, up)) if ask(xp, up) is not None else None
    # bascule du favori (moteur) la plus récente et son origine
    j1 = next((j for j in range(i, 0, -1) if (L[j]["p0"] - 0.5) * (L[j - 1]["p0"] - 0.5) < 0), None)
    t2 = next((L[j]["t"] for j in range(i, 0, -1) if L[j]["mid"] is not None and L[j - 1]["mid"] is not None and (L[j]["mid"] - 0.5) * (L[j - 1]["mid"] - 0.5) < 0), None)
    d["flip"] = None
    if j1 is not None:
        f = L[j1]; fp = L[j1 - 1]
        nouveau_cl = f["cl_t"] is not None and fp["cl_t"] is not None and f["cl_t"] > fp["cl_t"]
        y0 = avant(L, j1, 3)
        dp = (pr(x, "p0", up) - pr(y0, "p0", up)) if y0 else None
        dm = (x["mid"] - y0["mid"]) * (1 if up else -1) if y0 and x["mid"] is not None and y0["mid"] is not None else None
        d["flip"] = dict(age=x["t"] - f["t"], cl=nouveau_cl, livre=("jamais" if t2 is None else "avant" if t2 < f["t"] else "après"), dp=dp, dm=dm)
    R.append(d)
pn_tot = sum(r["pn"] for r in R)
out = [f"# Pourquoi l'avantage fond si vite — attribution de la convergence et double alpha (BTC, {len(R)} signaux, {hs(cyc[0])} → {hs(cyc[-1] + 300)})", "",
       "Mêmes signaux que l'étude A : moteur TWAP fin original, avantage ≥ 0,20, entre 90 et 20 s avant la fin, premier signal du cycle, 50 $ au meilleur vendeur limité à la quantité affichée, frais compris. "
       "« Notre côté » = le côté que le signal achète. Variation de l'avantage = variation de notre probabilité − variation du prix demandé (identité exacte).", ""]
# 1. decomposition moyenne
out += ["## 1. La question décisive : qui bouge ?", "", "| Délai | Variation de l'avantage | dont notre probabilité | dont le prix demandé (signe −) | Part due au marché | Prix vendeur moyen | Prix acheteur moyen |", "|---|---|---|---|---|---|---|"]
for dl in (0.25, 0.5, 1, 2, 5, 10, 20):
    S = [r for r in R if r[dl] and r[dl]["a"] is not None]
    dp = np.mean([r[dl]["p"] - r["p0"] for r in S]); da = np.mean([r[dl]["a"] - r["a0"] for r in S])
    bb = [r[dl]["b"] for r in S if r[dl]["b"] is not None]
    part = da / (abs(da) + abs(dp)) if abs(da) + abs(dp) > 0 else 0
    out.append(f"| {dl} s | {dp - da:+.3f} | {dp:+.3f} | {-da:+.3f} | {100 * part:.0f} % | {np.mean([r[dl]['a'] for r in S]):.3f} | {np.mean(bb):.3f} |")
out += ["", f"Au signal : prix vendeur moyen {np.mean([r['a0'] for r in R]):.3f}, notre probabilité moyenne {np.mean([r['p0'] for r in R]):.3f}, prix acheteur moyen {np.mean([r['b0'] for r in R if r['b0'] is not None]):.3f}.", ""]
# 2. classement a 1 s
def classe(r, dl=1, s=0.05):
    y = r[dl]
    if not y or y["a"] is None: return "carnet vide de notre côté"
    dp, da = y["p"] - r["p0"], y["a"] - r["a0"]
    if da >= s and dp > -s: return "1. Polymarket rejoint notre modèle"
    if dp <= -s and da < s: return "2. notre modèle rejoint Polymarket"
    if da >= s and dp <= -s: return "3. les deux convergent"
    if da <= -s and dp >= -s or dp >= s and da < s: return "4. les deux s'écartent davantage"
    return "5. presque rien ne bouge (< 5 points)"
for dl in (1, 5):
    out += [f"## 2. Classement des signaux selon ce qui se passe dans les {dl} s suivantes (seuil 5 points, fixé avant de regarder)", "", HH]
    G = collections.defaultdict(list)
    for r in R: G[classe(r, dl)].append((r["pn"], r["mise"], r["gm"]))
    for k in sorted(G): out.append(f"| {k} | {stats(G[k])} |")
    out.append("")
out += ["Résultat = achat au moment du signal, conservé jusqu'au règlement. Le classement utilise l'avenir : c'est un diagnostic, pas une règle.", ""]
# 3. double alpha
out += ["## 3. Double alpha : gain au règlement contre revente possible (prix acheteur réellement affiché)", "",
        "| Moment | Revente possible avec bénéfice après frais | Gain moyen par jeton si on revendait | Gain moyen par jeton au règlement |", "|---|---|---|---|"]
for dl in (1, 2, 5, 10, 20):
    S = [r for r in R if r[dl] and r[dl]["b"] is not None]
    rv = [r[dl]["b"] - r["a0"] - FEE(r["a0"]) - FEE(r[dl]["b"]) for r in S]
    rg = [(1 if r["gm"] else 0) - r["a0"] - FEE(r["a0"]) for r in S]
    out.append(f"| +{dl} s | {sum(v > 0 for v in rv)} / {len(S)} | {np.mean(rv):+.3f} | {np.mean(rg):+.3f} |")
out += ["", "Rappel : les sorties anticipées naïves ont déjà détruit de la performance. Ce tableau mesure, il ne propose pas de vendre.", ""]
# 4. propriete de l'avantage
out += ["## 4. Qui a créé l'avantage ? (3 s AVANT le signal, information disponible au moment de l'achat)", "", HH]
G = collections.defaultdict(list)
for r in R:
    if r.get("pre_da") is None: G["pas de mesure 3 s avant"].append((r["pn"], r["mise"], r["gm"])); continue
    dp, da = r["pre_dp"], r["pre_da"]
    if r["pre_edge"] is not None and r["pre_edge"] >= 0.15: k = "désaccord déjà là (avantage ≥ 0,15 trois secondes avant)"
    elif dp >= 0.05 and da > -0.05: k = "notre probabilité a monté, le prix n'a pas baissé"
    elif da <= -0.05 and dp < 0.05: k = "le prix Polymarket a chuté, notre probabilité stable"
    elif dp >= 0.05 and da <= -0.05: k = "les deux (proba ↑, prix ↓)"
    else: k = "petits mouvements des deux côtés"
    G[k].append((r["pn"], r["mise"], r["gm"]))
for k in sorted(G): out.append(f"| {k} | {stats(G[k])} |")
# 5. surprise
S = [r for r in R if r.get("pre_da") is not None]
exc = np.array([(1 if r["gm"] else 0) - r["a0"] for r in S])
def cc(v): return float(np.corrcoef(np.array(v), exc)[0, 1])
out += ["", "## 5. Surprise : la révision inattendue prédit-elle mieux le gain que l'avantage instantané ?", "",
        f"Sur {len(S)} signaux, corrélation avec (gagné 1/0 − prix payé) :", "",
        f"- avantage instantané (proba − prix) : {cc([r['p0'] - r['a0'] for r in S]):+.3f}",
        f"- variation de notre proba sur 3 s : {cc([r['pre_dp'] for r in S]):+.3f}",
        f"- dont partie mécanique (le temps passe, rien de nouveau) : {cc([r['pre_mec'] for r in S]):+.3f} — taille moyenne {np.mean([r['pre_mec'] for r in S]):+.3f}",
        f"- dont partie inattendue (information nouvelle) : {cc([r['pre_inat'] for r in S]):+.3f} — taille moyenne {np.mean([r['pre_inat'] for r in S]):+.3f}",
        f"- « prix de la surprise » = partie inattendue − hausse du prix demandé : {cc([r['pre_inat'] - r['pre_da'] for r in S]):+.3f}", "",
        f"Avec {len(S)} signaux, une corrélation doit dépasser environ ±{2 / math.sqrt(len(S)):.2f} pour ne pas être du hasard.", ""]
G = collections.defaultdict(list)
med = np.median([r["pre_inat"] - r["pre_da"] for r in S])
for r in S: G["surprise non intégrée au-dessus de la médiane" if r["pre_inat"] - r["pre_da"] > med else "en dessous"].append((r["pn"], r["mise"], r["gm"]))
out += [HH] + [f"| {k} | {stats(v)} |" for k, v in G.items()]
# 6. bascules
F = [r for r in R if r["flip"] and r["flip"]["age"] < 3]
out += ["", f"## 6. Les bascules récentes (< 3 s) : {len(F)} signaux", "", HH]
G = collections.defaultdict(list)
for r in F:
    f = r["flip"]; it = (r["pn"], r["mise"], r["gm"])
    G["origine : nouveau prix Chainlink reçu" if f["cl"] else "origine : prix des exchanges (pas de nouveau Chainlink)"].append(it)
    if f["dp"] and f["dm"] is not None and f["dp"] > 0:
        q = f["dm"] / f["dp"]
        G["réaction du carnet faible (< 1/3 du mouvement de notre proba)" if q < 1 / 3 else "réaction partielle (1/3 à 2/3)" if q < 2 / 3 else "réaction forte (> 2/3)"].append(it)
    G["carnet : favori jamais changé" if f["livre"] == "jamais" else "carnet : favori changé avant nous" if f["livre"] == "avant" else "carnet : favori changé après nous"].append(it)
for k in sorted(G): out.append(f"| {k} | {stats(G[k])} |")
NJ = [r for r in R if r["flip"] and r["flip"]["livre"] == "jamais"]
out += ["", f"## 7. Le groupe « notre modèle a basculé, le carnet jamais » ({len(NJ)} signaux) avec latence", "", "| Achat après | Encore ≥ 0,20 | Résultat | Prix moyen |", "|---|---|---|---|"]
for dl in (0, 0.25, 0.5, 1):
    tt = 0; n20 = 0; px = []
    for r in NJ:
        if dl == 0: a, p = r["a0"], r["p0"]
        else:
            y = r[dl]
            if not y or y["a"] is None: continue
            a, p = y["a"], y["p"]
        if not (0.02 <= a <= 0.98): continue
        n20 += p - a >= 0.20; px.append(a); tt += (50 / a) * ((1 if r["gm"] else 0) - a - FEE(a))
    out.append(f"| {dl} s | {n20} / {len(NJ)} | {f0(tt)} | {np.mean(px):.2f} |")
out += ["", "(Ici la quantité est supposée disponible pour 50 $ ; l'étude A montre que c'est presque toujours le cas.)", ""]
# 8. meme information, prix different
out += ["## 8. Même probabilité, prix différents : les contrats bon marché gagnent-ils assez ? (60-20 s, une mesure par cycle et par tranche)", "",
        "| Notre probabilité | Prix demandé | Mesures | Prix moyen | Gagnés | Écart gagné − prix |", "|---|---|---|---|---|---|"]
T = collections.defaultdict(dict)
for st in cyc:
    for x in CY[st]["L"]:
        if not (20 <= x["tl"] <= 60): continue
        for up in (True, False):
            a = ask(x, up)
            if a is None or not (0.02 <= a <= 0.98): continue
            p = pr(x, "p0", up); pb = min(int(p * 5), 4); ab = 0 if a < p - 0.15 else 1 if a < p + 0.05 else 2
            T[(pb, ab)].setdefault((st, up), (a, CY[st]["up"] == up))
for pb in range(5):
    for ab, lab in ((0, "bien moins cher (≥ 15 points sous la proba)"), (1, "proche"), (2, "plus cher")):
        v = list(T[(pb, ab)].values())
        if len(v) >= 20:
            out.append(f"| {20 * pb}-{20 * pb + 20} % | {lab} | {len(v)} | {np.mean([a for a, _ in v]):.2f} | {100 * np.mean([g for _, g in v]):.0f} % | {100 * (np.mean([g for _, g in v]) - np.mean([a for a, _ in v])):+.0f} points |")
# 9. qui a raison quand ils divergent
out += ["", "## 9. Quand notre modèle et le carnet divergent de plus de 15 points, qui avait raison ? (Brier, plus bas = meilleur)", "", "| Temps restant | Mesures | Cycles | Brier moteur | Brier carnet (milieu) |", "|---|---|---|---|---|"]
for a_, b_ in ((60, 90), (40, 60), (20, 40)):
    M = [(x["p0"], x["mid"], CY[st]["up"], st) for st in cyc for x in CY[st]["L"] if a_ <= x["tl"] < b_ and x["mid"] is not None and abs(x["p0"] - x["mid"]) > 0.15]
    if len(M) > 50:
        y = np.array([m[2] for m in M], float)
        out.append(f"| {a_}-{b_} s | {len(M)} | {len({m[3] for m in M})} | {np.mean((np.array([m[0] for m in M]) - y) ** 2):.3f} | {np.mean((np.array([m[1] for m in M]) - y) ** 2):.3f} |")
out += ["", f"Total des {len(R)} signaux achetés au signal : {f0(pn_tot)}."]
open("etude/bot5min/resultat_twap_convergence.md", "w").write("\n".join(out)); print("\n".join(out))
