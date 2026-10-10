"""BOT95 V3 — expérience 001 FIRST MOVER (hors ligne). Demande de Pitch, plan « BOT95 V3 ».
Données : photos /api/lead (bot95/lead.json.gz) = 10 s à 100 ms AVANT le premier désaccord ≥ 0,20 du cycle vu par le bot en direct, et 10 s APRÈS.
Règles (reprises telles quelles de lead_analyse.py, NON réglées ici) : une source « a bougé » quand elle a fait ≥ 5 $ dans notre sens depuis le début
de la photo (bourses, Chainlink) ; Polymarket « a bougé » quand le meilleur vendeur de notre côté a baissé d'au moins 1 c.
Exécution réaliste : (A) lignes enregistrées rec_BTC, meilleur vendeur seul, quantité affichée, prix ≤ prix de décision, 50 $ max, première ligne à t+délai ;
(B) carnet des photos « après » (100 ms, 3 niveaux) : on balaie les 3 niveaux ≤ prix de décision jusqu'à 50 $.
Périodes : apprentissage < CUT, validation CUT → MATIN0, test inédit après MATIN0 (petit). Aucune donnée future dans les décisions :
le premier à bouger est mesuré sur les 10 s AVANT le signal ; le résultat officiel ne sert qu'au P&L."""
exec(open("etude/bot5min/v3_commun.py").read())
DL = json.load(gzip.open("bot95/lead.json.gz", "rt"))
AV, AP = {}, collections.defaultdict(list)
for d in sorted(DL, key=lambda x: x["t"]):
    if d["phase"] == "avant": AV.setdefault(d["start"], d)
    else: AP[d["start"]].append(d)
SRC = [("Bybit", 1), ("OKX", 2), ("Coinbase", 3), ("Binance", 4), ("Chainlink", 5)]
EXCH = ["Bybit", "OKX", "Coinbase", "Binance"]
def kcol(cols, up, sens="ventes"): return cols.index(f"pm_{'up' if up else 'down'}_{sens}_top3")
def best(l, k): v = l[k]; return v[0][0] if v else None
def balaie(levels, limite, budget=50.0):
    q = cout = 0.0
    for p, z in levels or []:
        if p > limite + 1e-9: break
        x = min(z, (budget - cout) / p)
        if x <= 0: break
        q += x; cout += x * p
        if cout >= budget - 1e-6: break
    return q, cout
P = []
for st, d in sorted(AV.items()):
    cols = d["colonnes"]; L = d["lignes"]; up = d["cote"] == "Up"; sg = 1 if up else -1; ts = d["t"]
    if len(L) < 50: continue
    first, net = {}, {}
    for nom, i in SRC:
        p0 = next((l[i] for l in L if l[i]), None); pl = next((l[i] for l in reversed(L) if l[i]), None)
        if p0 is None: continue
        net[nom] = (pl - p0) * sg
        for l in L:
            if l[i] and (l[i] - p0) * sg >= 5: first[nom] = l[0]; break
    ka = kcol(cols, up); a0 = next((best(l, ka) for l in L if best(l, ka) is not None), None); al = next((best(l, ka) for l in reversed(L) if best(l, ka) is not None), None)
    if a0 is not None:
        net["Polymarket"] = (a0 - al) * 100 if al is not None else None
        for l in L:
            a = best(l, ka)
            if a is not None and a0 - a >= 0.01: first["Polymarket"] = l[0]; break
    ordre = sorted(first.items(), key=lambda x: x[1])
    qui = ordre[0][0] if ordre else "personne"
    ex_avec = sum(1 for e in EXCH if net.get(e) is not None and net[e] >= 5); ex_contre = sum(1 for e in EXCH if net.get(e) is not None and net[e] <= -5)
    conf = ("aucune bourse ne bouge" if ex_avec == 0 and ex_contre == 0 else "divergence (≥ 1 bourse contre nous)" if ex_contre > 0
            else "confirmation forte (≥ 3 bourses avec, 0 contre)" if ex_avec >= 3 else "confirmation partielle (1-2 bourses avec, 0 contre)")
    g = (O.get(f"BTC:{st}") or {}).get("gagnant")
    # exécution A (rec_BTC)
    sA = None
    if st in C and C[st] and g:
        k = bisect.bisect_left(TT[st], ts)
        if k < len(C[st]): sA = dict(i=k, t=ts, up=up, a=d["ask"])
    eA = {dl: (exe(st, sA, dl) if sA else None) for dl in (0, 0.5)}
    # exécution B (photo après, 100 ms, 3 niveaux)
    apr = min(AP.get(st, []), key=lambda x: abs(x["t"] - 10 - ts), default=None)
    eB = {}
    if apr and abs(apr["t"] - 10 - ts) < 1 and g:
        La = apr["lignes"]; kb = kcol(apr["colonnes"], up); gm = (g == "Up") == up
        for dl in (0, 0.1, 0.2, 0.5, 1.0):
            l = next((x for x in La if x[0] >= ts + dl - 0.03), None)
            if l is None: eB[dl] = None; continue
            q, cout = balaie(l[kb], d["ask"])
            eB[dl] = None
            if q >= 1:
                fee = 0.0; rest = q
                for p, z in l[kb]:
                    x = min(z, rest); fee += x * FEE(p); rest -= x
                    if rest <= 1e-9: break
                eB[dl] = dict(st=st, pn=q * (1 if gm else 0) - cout - fee, mise=cout, gm=gm, q=q)
    P.append(dict(st=st, ts=ts, up=up, ask=d["ask"], ecart=d["ecart"], reste=d["reste_s"], first=first, ordre=ordre, qui=qui, net=net, conf=conf,
                  g=g, eA=eA, eB=eB, per=PER(st)))
PG = [x for x in P if x["g"]]
cycP = {p: [x["st"] for x in PG if x["per"] == p] for p in PERS}
out = ["# BOT95 V3 — Expérience 001 : qui bouge en premier ? (FIRST MOVER)", "", ENTETE, "",
       f"Photos utilisées : {len(P)} cycles (première photo « avant » de chaque cycle, ≥ 50 lignes), dont {len(PG)} avec résultat officiel "
       f"(app. {len(cycP['apprentissage'])} · valid. {len(cycP['validation'])} · inédit {len(cycP['inédit'])}). Les photos commencent le 07.10 à 15:43 : "
       "l'apprentissage des photos est plus court que celui des lignes.", "",
       "**Résolution** : lignes à 100 ms, mais les prix des bourses ne changent en médiane que toutes les 0,4-0,5 s (Chainlink 0,9 s) — voir l'audit. "
       "Les temps ci-dessous sont des multiples de 100 ms, à l'heure de RÉCEPTION par le bot : une avance de 100-400 ms peut n'être qu'une différence de latence réseau. "
       "Les fenêtres de 50 ms ne sont pas mesurables avec ces données (le programme du VPS de Dublin `bot95/rapide/rapide.js` les mesurera).", "",
       "Règles (fixées avant, reprises de `lead_analyse.py`) : bourse/Chainlink « bouge » = ≥ 5 $ dans le sens du signal depuis le début de la photo ; "
       "Polymarket « bouge » = le meilleur vendeur de notre côté baisse d'au moins 1 c. **Ces deux seuils ne sont pas comparables** (1 c de Polymarket arrive bien plus souvent que 5 $ de BTC) : "
       "« Polymarket premier » est en partie un effet de seuil.", ""]
# ---------- 1. ordre des mouvements
out += ["## 1. Premier à bouger, temps d'avance et ordre", "", "| Premier à bouger | Photos | Part | Avance sur le signal (médiane, ms) | p25-p75 (ms) | Gagné (côté du signal) |", "|---|---|---|---|---|---|"]
G = collections.defaultdict(list)
for x in PG: G[x["qui"]].append(x)
for q, L in sorted(G.items(), key=lambda z: -len(z[1])):
    av_ = [1000 * (x["ts"] - x["ordre"][0][1]) for x in L if x["ordre"]]
    out.append(f"| {q} | {len(L)} | {100 * len(L) / len(PG):.0f} % | {np.median(av_):.0f} | {np.percentile(av_, 25):.0f}-{np.percentile(av_, 75):.0f} | {100 * sum((x['g'] == 'Up') == x['up'] for x in L) / len(L):.0f} % |" if av_ else
               f"| {q} | {len(L)} | {100 * len(L) / len(PG):.0f} % | — | — | {100 * sum((x['g'] == 'Up') == x['up'] for x in L) / len(L):.0f} % |")
out += ["", "Ordre complet des mouvements (les 12 séquences les plus fréquentes ; « = » : même ligne de 100 ms) :", "", "| Séquence | Photos | Gagné |", "|---|---|---|"]
def seq(x):
    o = x["ordre"]; s = ""
    for k, (n, t) in enumerate(o): s += ("" if k == 0 else (" = " if abs(t - o[k - 1][1]) < 0.05 else " → ")) + n
    return s or "personne"
SQ = collections.defaultdict(list)
for x in PG: SQ[seq(x)].append(x)
for s_, L in sorted(SQ.items(), key=lambda z: -len(z[1]))[:12]:
    out.append(f"| {s_} | {len(L)} | {100 * sum((x['g'] == 'Up') == x['up'] for x in L) / len(L):.0f} % |")
out += ["", "Décalage entre sources quand les deux ont bougé (médiane, ms ; positif = la source de la ligne bouge AVANT celle de la colonne) :", "",
        "| | " + " | ".join(n for n, _ in SRC) + " | Polymarket |", "|---|" + "---|" * 6]
ALLS = [n for n, _ in SRC] + ["Polymarket"]
for a in ALLS:
    cel = []
    for b in ALLS:
        if a == b: cel.append("—"); continue
        dd = [1000 * (x["first"][b] - x["first"][a]) for x in PG if a in x["first"] and b in x["first"]]
        cel.append(f"{np.median(dd):+.0f} ({len(dd)})" if dd else "—")
    out.append(f"| {a} | " + " | ".join(cel) + " |")
# ---------- 2. direction / amplitude, confirmation / divergence
out += ["", "## 2. Direction et amplitude sur les 10 s avant le signal ; confirmation ou divergence", "",
        "| Source | Mouvement médian dans le sens du signal | p10 | p90 | Photos où la source va CONTRE le signal (≤ −5 $ / ≤ −1 c) |", "|---|---|---|---|---|"]
for n in ALLS:
    v = [x["net"][n] for x in PG if x["net"].get(n) is not None]; u = "c" if n == "Polymarket" else "$"
    thr = -1 if n == "Polymarket" else -5
    out.append(f"| {n} | {np.median(v):+.1f} {u} | {np.percentile(v, 10):+.1f} | {np.percentile(v, 90):+.1f} | {sum(1 for z in v if z <= thr)} ({100 * sum(1 for z in v if z <= thr) / len(v):.0f} %) |")
# ---------- 3. P&L par premier à bouger, exécution réaliste
def tab_groupes(titre, cle, ordre_g=None):
    o = [f"### {titre}", ""]
    for p in PERS + ("toutes périodes",):
        S = PG if p == "toutes périodes" else [x for x in PG if x["per"] == p]
        cyc = [x["st"] for x in S]
        GG = collections.defaultdict(list)
        for x in S: GG[cle(x)].append(x)
        o += [f"**{p}** ({len(S)} photos) — exécution (A) lignes enregistrées, délai 0", "",
              hdr("Groupe").split("\n")[0] + " (A) délai 0,5 s demandé | (B) carnet photo 3 niveaux : 0 · 0,1 · 0,2 · 0,5 · 1 s |\n" + "|---" * 14 + "|"]
        for q in (ordre_g or sorted(GG, key=lambda z: -len(GG[z]))):
            L = GG.get(q, [])
            if not L: continue
            b = bilan([x["eA"][0] for x in L], cyc); b5 = sum((x["eA"][0.5] or {}).get("pn", 0) for x in L)
            bb = " · ".join(f0(sum((x["eB"].get(dl) or {}).get("pn", 0) for x in L)) for dl in (0, 0.1, 0.2, 0.5, 1.0))
            o.append(lig(f"{q} ({len(L)} photos)", b) + f" {f0(b5)} | {bb} |")
        o.append("")
    return o
out += ["", "## 3. Résultat par premier à bouger — exécution réaliste", "",
        "Signal = l'achat du côté du modèle au prix vendeur vu par le bot en direct (`ask` de la photo). (A) première ligne enregistrée (≈ 0,3 s) au signal ou après : meilleur vendeur seul, "
        "quantité affichée, jamais plus cher que le prix du signal, 50 $ max. (B) photo « après » (100 ms) : balayage des 3 premiers niveaux ≤ prix du signal. "
        "Achats = achats réellement exécutés en (A). « Gagné » = part des achats gagnants.", ""]
out += tab_groupes("Par premier à bouger", lambda x: x["qui"], ["Polymarket", "Coinbase", "Bybit", "OKX", "Chainlink", "Binance", "personne"])
out += tab_groupes("Confirmation / divergence des 4 bourses", lambda x: x["conf"])
# ---------- 4. Coinbase est-il un vrai indicateur avancé ?
out += ["## 4. Coinbase est-il un vrai indicateur avancé ?", "", "### 4a. Le groupe « Coinbase premier » période par période", "",
        "| Période | Photos | Coinbase premier | Gagné | Résultat (A) délai 0 | sans top 1 | sans top 3 | IC 90 % | (A) 0,5 s | Autres photos : résultat (A) 0 |", "|---|---|---|---|---|---|---|---|---|---|"]
for p in PERS:
    S = [x for x in PG if x["per"] == p]; L = [x for x in S if x["qui"] == "Coinbase"]; R = [x for x in S if x["qui"] != "Coinbase"]
    b = bilan([x["eA"][0] for x in L], [x["st"] for x in S])
    out.append(f"| {p} | {len(S)} | {len(L)} ({100 * len(L) / max(1, len(S)):.0f} %) | {b['win']:.0f} % | **{f0(b['pnl'])}** | {f0(b['sans'][1])} | {f0(b['sans'][3])} | [{f0(b['lo'])} ; {f0(b['hi'])}] | "
               f"{f0(sum((x['eA'][0.5] or {}).get('pn', 0) for x in L))} | {f0(sum((x['eA'][0] or {}).get('pn', 0) for x in R))} |")
# 4b. pouvoir prédictif : le mouvement passé de Coinbase prédit-il le mouvement futur de Polymarket / Chainlink / Bybit, à Bybit connu ?
def series(d):
    cols = d["colonnes"]; L = d["lignes"]; ku, kb = cols.index("pm_up_ventes_top3"), cols.index("pm_up_achats_top3")
    out_ = []
    for l in L:
        a, b_ = best(l, ku), best(l, kb)
        out_.append((l[0], l[1], l[2], l[3], l[4], l[5], (a + b_) / 2 if a is not None and b_ is not None else None))
    return out_
REG = {p: collections.defaultdict(list) for p in PERS}
for x in PG:
    d = AV[x["st"]]; apr = min(AP.get(x["st"], []), key=lambda y: abs(y["t"] - 10 - x["ts"]), default=None)
    S = series(d) + (series(apr) if apr and abs(apr["t"] - 10 - x["ts"]) < 1 else [])
    S = sorted(S); T_ = [s[0] for s in S]
    def val(t, j):
        k = bisect.bisect_right(T_, t) - 1
        return S[k][j] if k >= 0 and S[k][j] is not None else None
    t = S[0][0] + 1.0
    while t + 1.0 <= S[-1][0]:
        v = {j: (val(t, j), val(t - 1, j), val(t + 1, j)) for j in (1, 2, 3, 4, 5, 6)}
        if all(None not in v[j] for j in v):
            REG[x["per"]]["cb"].append(v[3][0] - v[3][1]); REG[x["per"]]["by"].append(v[1][0] - v[1][1])
            for nom, j in (("pm", 6), ("cl", 5), ("byf", 1), ("cbf", 3)): REG[x["per"]][nom].append(v[j][2] - v[j][0])
        t += 1.0
def ols(y, X):
    X = np.column_stack([np.ones(len(y))] + X); y = np.array(y); b = np.linalg.lstsq(X, y, rcond=None)[0]; e = y - X @ b
    cov = np.linalg.inv(X.T @ X) * (e @ e) / (len(y) - X.shape[1]); return b, b / np.sqrt(np.diag(cov))
out += ["", "### 4b. Pouvoir prédictif, à mouvement de Bybit connu", "",
        "Pas de 1 s, sans chevauchement, dans les 20 s autour de chaque signal (photos avant + après). Régression : mouvement FUTUR de la cible sur [t, t+1 s] "
        "= a + b × mouvement PASSÉ de Coinbase sur [t−1 s, t] + c × mouvement PASSÉ de Bybit sur [t−1 s, t]. Si Coinbase est un vrai indicateur avancé, b doit être positif et stable "
        "d'une période à l'autre. Échantillon biaisé : uniquement des fenêtres autour de désaccords. t de Student naïfs (observations d'une même photo non indépendantes).", "",
        "| Période | Pas de 1 s | Cible | b Coinbase (t) | c Bybit (t) |", "|---|---|---|---|---|"]
for p in PERS:
    R = REG[p]
    if len(R["cb"]) < 30: out.append(f"| {p} | {len(R['cb'])} | — | trop peu | — |"); continue
    b0, t0_ = ols(R["pm"], [R["cb"]]); out.append(f"| {p} | {len(R['cb'])} | Polymarket Up, Coinbase SEUL (sans Bybit) | {b0[1] * 1e4:+.3f} ({t0_[1]:+.1f}) | — |")
    for nom, lab, u in (("pm", "Polymarket Up (milieu, en c pour 100 $)", 100 * 100), ("cl", "Chainlink ($ par $)", 1), ("byf", "Bybit futur ($ par $)", 1), ("cbf", "Coinbase futur ($ par $)", 1)):
        b, tt = ols(R[nom], [R["cb"], R["by"]])
        out.append(f"| {p} | {len(R['cb'])} | {lab} | {b[1] * u:+.3f} ({tt[1]:+.1f}) | {b[2] * u:+.3f} ({tt[2]:+.1f}) |")
out += ["", "Lecture : pour Polymarket, b = de combien de centimes le milieu Up bouge dans la seconde suivante pour 100 $ de mouvement passé de Coinbase (Bybit tenu constant).", ""]
open("etude/bot5min/resultat_v3_exp001.md", "w").write("\n".join(out)); print("\n".join(out))
