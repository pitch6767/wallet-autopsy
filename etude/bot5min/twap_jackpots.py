"""TWAP fin — jackpots, attente, exécution, mises, robustesse, angles morts (idées ChatGPT 10.10.2026 01:08). Aucun fantôme modifié.
Apprentissage = 60 % premiers cycles, validation = 40 % derniers. Les décisions n'utilisent que ce qui était reçu à l'instant."""
import sys
sys.path.insert(0, "etude/bot5min")
exec(open("etude/bot5min/twap_etudes.py").read().split("# ---------- B.")[0])
bid = lambda x, up: x["ub"] if up else x["db"]
CUT = cyc[int(len(cyc) * 0.6)]
per = lambda st: "appr." if st < CUT else "valid."
def jdl(L, i, dl, sens=1):
    t0 = L[i]["t"] + sens * dl
    if sens > 0: return next((j for j in range(i, len(L)) if L[j]["t"] >= t0 - 1e-6), None)
    return next((j for j in range(i, -1, -1) if L[j]["t"] <= t0 + 1e-6), None)
def achat(x, up, gm, mise=50.0, prix=None):
    a = prix if prix is not None else ask(x, up); z = sz(x, up)
    if a is None or z <= 0 or not (0.02 <= a <= 0.98) or mise <= 0: return None
    q = min(mise / a, z); return (q * ((1 if gm else 0) - a - FEE(a)), q * a, gm)
def nxt_cl(L, i):
    x = L[i]
    return next((j for j in range(i + 1, len(L)) if L[j]["cl_t"] and x["cl_t"] and L[j]["cl_t"] > x["cl_t"] and L[j]["cl_v"] != x["cl_v"]), None)
def cl_hist(L, i):
    """temps des changements de valeur Chainlink reçus avant l'instant i (dans le cycle)"""
    out = []; last = None
    for j in range(0, i + 1):
        v = L[j]["cl_v"]
        if v is not None and v != last: out.append(L[j]["t"]); last = v
    return out
R = []
for st, (i, up) in SIG.items():
    L = CY[st]["L"]; x = L[i]; gm = CY[st]["up"] if up else not CY[st]["up"]; b = achat(x, up, gm)
    if b: R.append(dict(st=st, i=i, up=up, gm=gm, it=b, x=x, L=L, jack=b[0] >= 4 * b[1]))
JACK_REF = sum(r["it"][0] for r in R if r["jack"])
def table(G, ordre=None, split=True):
    o = [HH]
    for k in (ordre or sorted(G, key=lambda k: (k.split(" — ")[0], k))):
        if G.get(k): o.append(f"| {k} | {stats(G[k])} |")
    return o
def deux(G, cle, it, st): G[cle].append(it); G[f"{cle} — {per(st)}"].append(it)
def pol_line(nom, L_):
    jk = sum(l[0] for l in L_ if l[0] >= 4 * l[1]); return f"| {nom} | {stats(L_)} | {100 * jk / JACK_REF:.0f} % |"
HP = "| Politique | Achats | Gagnés | Résultat | Par $ | Creux | Pertes de suite max | Jackpots conservés |\n|---|---|---|---|---|---|---|---|"
out = [f"# TWAP fin — jackpots, attente, exécution, mises, robustesse (BTC, {len(cyc)} cycles, {hs(cyc[0])} → {hs(cyc[-1] + 300)})", "",
       f"Référence : {len(R)} premiers signaux TWAP fin original (avantage ≥ 0,20, 90-20 s), {f0(sum(r['it'][0] for r in R))}. "
       f"Jackpot = gain ≥ 4 × la mise ; {sum(r['jack'] for r in R)} jackpots pour {f0(JACK_REF)}. Apprentissage avant le {hs(CUT)}, validation après.", ""]
# ======================= PARTIE A
out += ["## Partie A — horloge Chainlink, âge de l'opportunité, premier signal", "", "### Idées 2-4. Phase Chainlink au moment du signal (connue à l'instant : âge du dernier prix reçu / intervalle médian des 5 derniers)", ""]
G = collections.defaultdict(list); GW = collections.defaultdict(lambda: [0.0, 0.0, 0])
for r in R:
    L, i, x = r["L"], r["i"], r["x"]; H_ = cl_hist(L, i)
    if len(H_) < 3: continue
    age = x["t"] - H_[-1]; iv = float(np.median(np.diff(H_[-6:])))
    ph = age / iv if iv > 0 else 0
    k = "juste après un prix Chainlink (< 1/3 de l'intervalle)" if ph < 1 / 3 else "milieu de l'intervalle" if ph < 2 / 3 else "proche du prochain prix attendu (> 2/3)"
    deux(G, k, r["it"], r["st"])
    j = nxt_cl(L, i); w = 0.0
    if j is not None and ask(L[j], r["up"]) is not None and pr(L[j], "p0", r["up"]) - ask(L[j], r["up"]) >= 0.20:
        b2 = achat(L[j], r["up"], r["gm"]); w = b2[0] if b2 else 0.0
    GW[k][0] += r["it"][0]; GW[k][1] += w; GW[k][2] += 1
out += table(G)
out += ["", "| Phase | Signaux | Acheter tout de suite | Attendre le prochain Chainlink |", "|---|---|---|---|"] + [f"| {k} | {v[2]} | {f0(v[0])} | {f0(v[1])} |" for k, v in GW.items()]
# 5-6 maturite
out += ["", "### Idées 5-6. Âge du désaccord au moment du signal (naissance = dernier instant où l'avantage était < 0,05)", ""]
G = collections.defaultdict(list); GW = collections.defaultdict(lambda: [0.0, 0.0, 0])
for r in R:
    L, i, up, x = r["L"], r["i"], r["up"], r["x"]
    jb = next((j for j in range(i, -1, -1) if ask(L[j], up) is not None and pr(L[j], "p0", up) - ask(L[j], up) < 0.05), None)
    age = x["t"] - L[jb]["t"] if jb is not None else 99
    ncl = len([t for t in cl_hist(L, i) if jb is not None and t > L[jb]["t"]])
    k = "désaccord né il y a < 1 s (saut)" if age < 1 else "né il y a 1-5 s" if age < 5 else "né il y a > 5 s (montée progressive)"
    deux(G, k, r["it"], r["st"]); deux(G, f"{min(ncl, 2)}{'+' if ncl >= 2 else ''} prix Chainlink depuis la naissance", r["it"], r["st"])
    j = nxt_cl(L, i); w = 0.0
    if j is not None and ask(L[j], up) is not None and pr(L[j], "p0", up) - ask(L[j], up) >= 0.20:
        b2 = achat(L[j], up, r["gm"]); w = b2[0] if b2 else 0.0
    GW[k][0] += r["it"][0]; GW[k][1] += w; GW[k][2] += 1
out += table(G)
out += ["", "| Âge | Signaux | Acheter tout de suite | Attendre le prochain Chainlink |", "|---|---|---|---|"] + [f"| {k} | {v[2]} | {f0(v[0])} | {f0(v[1])} |" for k, v in GW.items()]
# 7 premiers / suivants franchissements
out += ["", "### Idée 7. Premier franchissement du seuil contre les suivants (mesure seulement, un achat par cycle reste la règle)", ""]
G = collections.defaultdict(list)
for st in cyc:
    L = CY[st]["L"]; n = 0; prev = {True: False, False: False}
    for j, x in enumerate(L):
        if not (20 <= x["tl"] <= 90): continue
        for up in (True, False):
            a = ask(x, up); on = a is not None and 0.02 <= a <= 0.98 and sz(x, up) > 0 and pr(x, "p0", up) - a >= 0.20
            if on and not prev[up]:
                n += 1; b = achat(x, up, CY[st]["up"] == up)
                if b: deux(G, "1er franchissement" if n == 1 else "2e franchissement" if n == 2 else "3e et suivants", b, st)
            prev[up] = on
out += table(G)
# ======================= PARTIE B
out += ["", "## Partie B — jackpots", "", "### Idées 8-10. Pourquoi l'attente du prochain Chainlink abandonne-t-elle des signaux ?", ""]
G = collections.defaultdict(list); ev = mq = 0.0
for r in R:
    L, i, up = r["L"], r["i"], r["up"]; j = nxt_cl(L, i)
    if j is None: k = "pas de nouveau Chainlink"
    else:
        y = L[j]; a2 = ask(y, up)
        if a2 is None: k = "offre disparue"
        elif pr(y, "p0", up) - a2 >= 0.20: k = "confirmé (on achète après attente)"
        elif pr(y, "p0", up) < pr(r["x"], "p0", up) - 0.05: k = "risque B : notre probabilité a baissé"
        else: k = "risque A : le prix Polymarket a monté (proba stable)"
    G[k].append(r["it"])
    if not k.startswith("confirmé"):
        if r["it"][0] < 0: ev += -r["it"][0]
        else: mq += r["it"][0]
out += [HH.replace("Groupe", "Ce qui arrive au prochain Chainlink (résultat = achat immédiat)")] + [f"| {k} | {stats(v)} |" for k, v in sorted(G.items())]
out += ["", f"Regret asymétrique (idée 10) : l'attente évite {f0(ev)} de pertes mais fait manquer {f0(mq)} de gains (achats immédiats des signaux abandonnés).", ""]
# 11 ADN des jackpots
out += ["### Idée 11. ADN des jackpots : jackpots contre perdants au même prix (≤ 0,20 $), mesures connues à l'achat", "",
        "| Mesure | Jackpots | Perdants bon marché | Écart significatif ? |", "|---|---|---|---|"]
J_ = [r for r in R if r["jack"]]; P_ = [r for r in R if not r["gm"] and ask(r["x"], r["up"]) <= 0.20]
def feat(r):
    L, i, up, x = r["L"], r["i"], r["up"], r["x"]; j3 = jdl(L, i, 3, -1); H_ = cl_hist(L, i)
    return dict(prix=ask(x, up), proba=pr(x, "p0", up), avantage=pr(x, "p0", up) - ask(x, up), distance_z=abs(x["z"]), restant=x["tl"],
                age_cl=(x["t"] - H_[-1]) if H_ else np.nan, var_prix_3s=(ask(x, up) - ask(L[j3], up)) if j3 is not None and ask(L[j3], up) is not None else np.nan,
                var_proba_3s=(pr(x, "p0", up) - pr(L[j3], "p0", up)) if j3 is not None else np.nan, quantite=sz(x, up))
FJ = [feat(r) for r in J_]; FP = [feat(r) for r in P_]
for k in FJ[0]:
    a = np.array([f[k] for f in FJ], float); b = np.array([f[k] for f in FP], float); a, b = a[~np.isnan(a)], b[~np.isnan(b)]
    se = math.sqrt(a.var() / len(a) + b.var() / len(b)) if len(a) > 1 and len(b) > 1 else 1
    out.append(f"| {k} | {a.mean():.3f} | {b.mean():.3f} | {'oui' if abs(a.mean() - b.mean()) > 2 * se else 'non'} (t = {(a.mean() - b.mean()) / se:+.1f}) |")
out += ["", f"{len(J_)} jackpots, {len(P_)} perdants à 0,20 $ ou moins.", ""]
# 12 concentration
pn = sorted([r["it"][0] for r in R], reverse=True); T = sum(pn)
out += ["### Idée 12. Concentration des gains", "", "| Retirer les | Gains retirés | Part du total | Résultat restant |", "|---|---|---|---|"]
for n in (1, 5, 10, 20):
    out.append(f"| {n} plus gros | {f0(sum(pn[:n]))} | {100 * sum(pn[:n]) / T:.0f} % | {f0(T - sum(pn[:n]))} |")
# ======================= PARTIE C
out += ["", "## Partie C — exécution", "", "### Idées 14-15. Capacité : la quantité affichée au meilleur vendeur suffit-elle pour 50 $ ?", ""]
cap = [min(sz(r["x"], r["up"]) * ask(r["x"], r["up"]), 50) for r in R]
out += [f"- Montant réellement achetable au meilleur vendeur : médiane **{np.median(cap):.1f} $**, moyenne {np.mean(cap):.1f} $ ; 50 $ complets dans {sum(c >= 49.99 for c in cap)} signaux sur {len(R)}.",
        f"- Capital réellement engagé par la référence : {sum(r['it'][1] for r in R):.0f} $ pour {len(R)} achats (au lieu de {50 * len(R)} $ prévus).", ""]
G = collections.defaultdict(list)
for r, c in zip(R, cap):
    deux(G, "moins de 10 $ disponibles" if c < 10 else "10 à 49 $" if c < 49.99 else "50 $ complets", r["it"], r["st"])
    ev_ = sz(r["x"], r["up"]) * 0 + min(50 / ask(r["x"], r["up"]), sz(r["x"], r["up"])) * (pr(r["x"], "p0", r["up"]) - ask(r["x"], r["up"]) - FEE(ask(r["x"], r["up"])))
    r["ev"] = ev_
out += table(G)
evs = np.array([r["ev"] for r in R]); rl = np.array([r["it"][0] for r in R])
out += ["", f"Idée 15 : espérance en $ (quantité × (proba − prix − frais)) moyenne {evs.mean():.2f} $ ; corrélation avec le résultat réel {np.corrcoef(evs, rl)[0, 1]:+.2f} ; "
        f"somme des espérances {f0(evs.sum())} contre résultat réel {f0(rl.sum())}.", ""]
# 16 budget de latence
out += ["### Idée 16. Budget de latence : ce qui change si l'ordre arrive plus tard", "",
        "| Délai | Prix vendeur moyen | Quantité médiane | Proba moyenne (notre côté) | Offre disparue | Avantage < 0,20 | Résultat (50 $ max, quantité affichée) |", "|---|---|---|---|---|---|---|"]
for dl in (0, 0.25, 0.5, 1, 2):
    A_, Q, P, gone, lost, res = [], [], [], 0, 0, []
    for r in R:
        j = jdl(r["L"], r["i"], dl)
        if j is None: gone += 1; continue
        y = r["L"][j]; a = ask(y, r["up"])
        if a is None or sz(y, r["up"]) <= 0: gone += 1; continue
        A_.append(a); Q.append(sz(y, r["up"])); P.append(pr(y, "p0", r["up"])); lost += pr(y, "p0", r["up"]) - a < 0.20
        b = achat(y, r["up"], r["gm"]); res.append(b[0] if b else 0)
    out.append(f"| {dl} s | {np.mean(A_):.3f} | {np.median(Q):.0f} | {np.mean(P):.3f} | {gone} | {lost} | {f0(sum(res))} |")
out += ["", "### Idée 17. Remonter dans le carnet : les niveaux au-delà du meilleur vendeur ne sont pas dans les données enregistrées (1 niveau par côté). "
        "Le fantôme corrigé enregistre 8 niveaux à ses achats ; à ajouter au TWAP fin si tu le décides.", ""]
# ======================= PARTIE D
out += ["## Partie D — achat immédiat, fractionné ou confirmé (même budget 50 $, quantité affichée à chaque instant)", "", HP]
def politique(f):
    L_ = []
    for r in R:
        res = f(r)
        if res: L_.append(res)
    return L_
def combo(r, now, later, fen=None):
    L, i, up, x, gm = r["L"], r["i"], r["up"], r["x"], r["gm"]; tl = x["tl"]
    if fen and not fen(tl): return None
    pn_ = mi = 0.0; ok = False
    if now > 0:
        b = achat(x, up, gm, now)
        if b: pn_ += b[0]; mi += b[1]; ok = True
    if later > 0:
        j = nxt_cl(L, i)
        if j is not None and ask(L[j], up) is not None and pr(L[j], "p0", up) - ask(L[j], up) >= 0.20:
            b = achat(L[j], up, gm, later)
            if b: pn_ += b[0]; mi += b[1]; ok = True
    return (pn_, mi, gm) if ok else None
edge0 = lambda r: pr(r["x"], "p0", r["up"]) - ask(r["x"], r["up"])
POL = [("A — 50 $ immédiats (référence)", lambda r: combo(r, 50, 0)),
       ("B — 35 $ immédiats + 15 $ si confirmé", lambda r: combo(r, 35, 15)),
       ("C — 15 $ immédiats + 35 $ si confirmé", lambda r: combo(r, 15, 35)),
       ("attente complète (50 $ si confirmé)", lambda r: combo(r, 0, 50)),
       ("D — mise selon l'avantage : 50 $ × avantage / 0,40 (max 50)", lambda r: combo(r, min(50, 50 * edge0(r) / 0.40), 0)),
       ("E — mise selon l'avantage prudent (proba − 10 pts) : 50 $ × (avantage − 0,10) / 0,30", lambda r: combo(r, min(50, max(0, 50 * (edge0(r) - 0.10) / 0.30)), 0)),
       ("idée 20 — 90-60 s immédiat ; 60-40 s 15 + 35 confirmé ; 40-20 s rien", lambda r: combo(r, 50, 0) if r["x"]["tl"] > 60 else combo(r, 15, 35) if r["x"]["tl"] > 40 else None),
       ("fenêtre 90-40 s seulement, 50 $ immédiats", lambda r: combo(r, 50, 0) if r["x"]["tl"] > 40 else None)]
for nom, f in POL:
    L_ = politique(f); out.append(pol_line(nom, L_))
    out.append(pol_line(nom + " — appr.", [l for l, r in zip([f(r) for r in R], R) if l and r["st"] < CUT]))
    out.append(pol_line(nom + " — valid.", [l for l, r in zip([f(r) for r in R], R) if l and r["st"] >= CUT]))
# ======================= PARTIE E
out += ["", "## Partie E — robustesse des probabilités", "", "### Idées 23-24. Calibration réelle des signaux et seuil de rentabilité", "",
        "| Prix payé | Achats | Proba moyenne du moteur | Gagnés réellement | Seuil de rentabilité (prix + frais) |", "|---|---|---|---|---|"]
for a_, b_ in ((0.02, 0.10), (0.10, 0.20), (0.20, 0.35), (0.35, 0.60), (0.60, 0.98)):
    S = [r for r in R if a_ <= ask(r["x"], r["up"]) < b_]
    if S: out.append(f"| {a_:.2f}-{b_:.2f} | {len(S)} | {np.mean([pr(r['x'], 'p0', r['up']) for r in S]):.3f} | {100 * np.mean([r['gm'] for r in S]):.0f} % | {np.mean([ask(r['x'], r['up']) + FEE(ask(r['x'], r['up'])) for r in S]):.3f} |")
out += ["", "Test de stress (idée 24) : si le moteur surestimait notre côté de N points, quels signaux garderaient un avantage ≥ 0,20 — et que rapportent-ils vraiment ?", "", HP]
for d in (0.05, 0.10, 0.15):
    out.append(pol_line(f"proba − {int(d * 100)} pts : avantage encore ≥ 0,20", [r["it"] for r in R if edge0(r) - d >= 0.20]))
out.append(pol_line("proba × 0,8 (correction proportionnelle, pèse sur les chers)", [r["it"] for r in R if 0.8 * pr(r["x"], "p0", r["up"]) - ask(r["x"], r["up"]) >= 0.20]))
out.append(pol_line("proba − 10 pts seulement entre 40 et 20 s", [r["it"] for r in R if edge0(r) - (0.10 if r["x"]["tl"] <= 40 else 0) >= 0.20]))
out += ["", "### Idées 22, 25-26. Même avantage, prix différent", ""]
G = collections.defaultdict(list)
for r in R:
    a = ask(r["x"], r["up"]); deux(G, "prix < 0,15 $" if a < 0.15 else "prix 0,15-0,35 $" if a < 0.35 else "prix > 0,35 $", r["it"], r["st"])
out += table(G)
# ======================= PARTIE F
out += ["", "## Partie F — erreurs du marché (toutes les cotations, une par cycle, par côté et par case)", "",
        "### Idées 27, 30. Carte : temps restant × prix × distance au seuil (|z| du moteur) — gagné − prix − frais, en points (appr. / valid.)", "",
        "| Prix | Distance | 90-60 s | 60-40 s | 40-20 s |", "|---|---|---|---|---|"]
M = collections.defaultdict(dict)
for st in cyc:
    for x in CY[st]["L"]:
        if not (20 <= x["tl"] <= 90): continue
        tb = 0 if x["tl"] > 60 else 1 if x["tl"] > 40 else 2
        for up in (True, False):
            a = ask(x, up)
            if a is None or not (0.01 <= a <= 0.99): continue
            pb = 0 if a < 0.15 else 1 if a < 0.50 else 2; db_ = 0 if abs(x["z"]) < 1 else 1
            M[(pb, db_, tb, per(st))].setdefault((st, up), (a, CY[st]["up"] == up))
for pb, pl in ((0, "< 0,15 $"), (1, "0,15-0,50 $"), (2, "> 0,50 $")):
    for db_, dl_ in ((0, "proche (|z| < 1)"), (1, "loin (|z| ≥ 1)")):
        cells = []
        for tb in range(3):
            v = [list(M[(pb, db_, tb, pe)].values()) for pe in ("appr.", "valid.")]
            cells.append(" / ".join(f"{100 * np.mean([g - a - FEE(a) for a, g in w]):+.1f}" if len(w) >= 20 else "—" for w in v))
        out.append(f"| {pl} | {dl_} | " + " | ".join(cells) + " |")
out += ["", "### Idées 29, 31-32. Qui a raison selon le prix et la distance (Brier, une mesure par seconde, 90-20 s)", "",
        "| Groupe | Mesures | Moteur original | Sauts | Carnet |", "|---|---|---|---|---|"]
B = collections.defaultdict(list)
for st in cyc:
    vu = set()
    for x in CY[st]["L"]:
        s = int(x["t"])
        if not (20 <= x["tl"] <= 90) or x["mid"] is None or s in vu: continue
        vu.add(s); y = CY[st]["up"]; m = min(x["mid"], 1 - x["mid"])
        k1 = "côté bon marché < 10 c (queues)" if m < 0.10 else "10-30 c" if m < 0.30 else "30-50 c (incertain)"
        k2 = "|z| < 0,5" if abs(x["z"]) < 0.5 else "|z| 0,5-1,5" if abs(x["z"]) < 1.5 else "|z| ≥ 1,5"
        for k in (k1, k2): B[k].append((x["p0"], x["pT"], x["mid"], y))
for k in ("côté bon marché < 10 c (queues)", "10-30 c", "30-50 c (incertain)", "|z| < 0,5", "|z| 0,5-1,5", "|z| ≥ 1,5"):
    A = np.array(B[k], float); y = A[:, 3]
    out.append(f"| {k} | {len(A)} | {np.mean((A[:, 0] - y) ** 2):.4f} | {np.mean((A[:, 1] - y) ** 2):.4f} | {np.mean((A[:, 2] - y) ** 2):.4f} |")
# ======================= PARTIE G
out += ["", "## Partie G — le marché sait-il quelque chose ? (mesures avant l'achat)", "", "### Idées 33-34. Trajectoire du prix de notre côté sur les 10 s avant le signal", ""]
G = collections.defaultdict(list)
for r in R:
    L, i, up, x = r["L"], r["i"], r["up"], r["x"]; j = jdl(L, i, 10, -1)
    if j is None or ask(L[j], up) is None: continue
    w = [ask(L[k], up) for k in range(j, i + 1) if ask(L[k], up) is not None]; d = ask(x, up) - ask(L[j], up)
    osc = sum(1 for k in range(1, len(w) - 1) if (w[k] - w[k - 1]) * (w[k + 1] - w[k]) < 0 and abs(w[k] - w[k - 1]) >= 0.02)
    k = "oscillations (≥ 3 allers-retours de 2 c)" if osc >= 3 else "chute rapide (≥ 10 c en 10 s)" if d <= -0.10 else "remontée (≥ 5 c)" if d >= 0.05 else "prix stable"
    deux(G, k, r["it"], r["st"])
out += table(G)
out += ["", "### Idées 35-37, 41. Réaction du carnet aux 3 dernières secondes, comparée à la variation de notre probabilité", ""]
G = collections.defaultdict(list)
for r in R:
    L, i, up, x = r["L"], r["i"], r["up"], r["x"]; j = jdl(L, i, 3, -1)
    if j is None or j == i or x["mid"] is None or L[j]["mid"] is None: continue
    dp = pr(x, "p0", up) - pr(L[j], "p0", up); dm = (x["mid"] - L[j]["mid"]) * (1 if up else -1)
    if dm <= -0.03: k = "carnet CONTRE nous (milieu de notre côté −3 c ou plus)"
    elif dp > 0.02 and dm < dp / 3: k = "carnet réagit moins d'1/3 de notre hausse"
    elif dp > 0.02: k = "carnet suit (≥ 1/3)"
    else: k = "notre proba n'a pas monté (le désaccord vient du prix)"
    deux(G, k, r["it"], r["st"])
    newcl = any(t > L[j]["t"] for t in cl_hist(L, i)[-3:])
    if newcl and dp > 0.02 and dm <= -0.03: deux(G, "idée 37 : nouveau Chainlink en notre faveur ET carnet contre", r["it"], r["st"])
out += table(G)
out += ["", "### Idée 38. Deux erreurs distinctes du modèle", ""]
A_rev = [r for r in R if (lambda j: j is not None and pr(r["L"][j], "p0", r["up"]) < pr(r["x"], "p0", r["up"]) - 0.15)(jdl(r["L"], r["i"], 5))]
out += [f"- A : notre probabilité baisse de plus de 15 points dans les 5 s : {len(A_rev)} signaux sur {len(R)}, dont {sum(r['gm'] for r in A_rev)} gagnés quand même.",
        f"- B : le contrat perd au règlement : {sum(not r['gm'] for r in R)} signaux ; parmi eux, {sum(1 for r in A_rev if not r['gm'])} avaient d'abord connu la révision A.", ""]
# 42 modele B : melange moteur + carnet
out += ["### Idée 42. Modèle B = moteur et carnet mélangés à parts égales (poids fixé d'avance, pas optimisé) — Brier par temps restant", "",
        "| Temps restant | Moteur | Carnet | Mélange 50/50 |", "|---|---|---|---|"]
for a_, b_ in ((60, 90), (40, 60), (20, 40)):
    A = []
    for st in cyc:
        vu = set()
        for x in CY[st]["L"]:
            s = int(x["t"])
            if a_ <= x["tl"] < b_ and x["mid"] is not None and s not in vu: vu.add(s); A.append((x["p0"], x["mid"], CY[st]["up"]))
    A = np.array(A, float); y = A[:, 2]
    out.append(f"| {a_}-{b_} s | {np.mean((A[:, 0] - y) ** 2):.4f} | {np.mean((A[:, 1] - y) ** 2):.4f} | {np.mean(((A[:, 0] + A[:, 1]) / 2 - y) ** 2):.4f} |")
open("etude/bot5min/resultat_twap_jackpots.md", "w").write("\n".join(out)); print("\n".join(out))
