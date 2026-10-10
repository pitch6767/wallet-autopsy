"""BOT95 META-ROUTER — étude demandée par Pitch le 10.10.2026 13:43. Diagnostic seulement : aucun fantôme modifié, aucun routeur actif.
Six stratégies rejouées sur les carnets enregistrés 4×/s, mêmes cycles, une décision par cycle, 50 $ maximum au SEUL meilleur vendeur
dans la quantité affichée, frais compris, cycles sans achat = 0 $.
  1 V2-D perp 120-269 s · 2 Zone 30 + modèle monte · 3 V2-G jury des bourses · 4 V2-F original · 5 V2-F 0,01 % (modèle reconstruit) · 6 V2-F miroir 1 s
Étape 1 complémentarité · Étape 2 régimes (connus au DÉBUT du cycle) · Étape 3 routeurs R0-R3 figés sur l'apprentissage.
Périodes : apprentissage < 08.10 ~22:00 ; validation → 10.10 10:25 (déjà explorée par d'autres études) ; inédit après 10.10 10:25."""
import sys
sys.path.insert(0, "etude/bot5min")
exec(open("etude/bot5min/robustesse_E.py").read().split("def rejouer(delta):")[0])
MATIN0 = 1791620700
PER = lambda st: "apprentissage" if st < CUT else ("validation" if st < MATIN0 else "inédit")
PERS = ("apprentissage", "validation", "inédit")
# ---------- modèle reconstruit (edge_truth.py) pour la version 0,01 %
P1, CL1 = {}, {}
for r in rows:
    s = int(r[0]); p = r[11] or r[12]
    if p: P1[s] = p
    if r[15]: CL1[s] = r[15]
VL, BL_ = {}, {}
def volr(s):
    if s not in VL:
        x = [P1[k] for k in range(s - 300, s + 1) if k in P1]
        VL[s] = (float(np.std(np.diff(np.log(x)))) or 1e-6) if len(x) >= 150 else None
    return VL[s]
def baser(s):
    if s not in BL_:
        d = [P1[k] - CL1[k] for k in range(s - 120, s + 1) if k in P1 and k in CL1]
        BL_[s] = float(np.median(d)) if d else None
    return BL_[s]
def mod_r(r, st, sd):
    K = r[16]; p = r[11] or r[12]; s = int(r[0])
    if not K or not p: return None
    sg, b = volr(s), baser(s)
    if sg is None or b is None: return None
    S = p - b; end = st + 300; deb = end - 59
    if s >= deb:
        con = [CL1[k] for k in range(deb, s + 1) if k in CL1]; nr = max(1, end - s)
        E = (sum(con) + nr * S) / (len(con) + nr); v = (sg * S) ** 2 * nr ** 3 / 3 / 3600
    else: E = S; v = (sg * S) ** 2 * ((deb - s) + 20)
    return phi((E - K) / math.sqrt(v + (sd * S) ** 2))
NOMS = ["V2-D perp 120-269 s", "Zone 30 + modèle monte", "V2-G jury des bourses", "V2-F original", "V2-F 0,01 %", "V2-F miroir 1 s"]
CT = {"V2-D perp 120-269 s": "V2-D", "Zone 30 + modèle monte": "Zone+monte", "V2-G jury des bourses": "V2-G", "V2-F original": "V2-F",
      "V2-F 0,01 %": "V2-F 0,01", "V2-F miroir 1 s": "Miroir"}
# ---------- rejeu : signaux (st, nom) -> (indice de ligne, côté)
SIG = {}
for st in valides:
    R_ = [r for r in C[st] if None not in (r[2], r[3], r[4], r[5], r[6])]; C[st] = R_
    if not R_: continue
    end = st + 300; T_ = [r[0] for r in R_]; MC = {}
    m01 = lambda k: MC.setdefault(k, mod_r(R_[k], st, 1e-4))
    def ago(i, sec_):
        k = bisect.bisect_right(T_, R_[i][0] - sec_) - 1
        return k if k >= 0 else None
    for i, r in enumerate(R_):
        t = r[0]; tl = end - t
        if tl < 5: break
        j3, j5, j1, j4 = ago(i, 3), ago(i, 5), ago(i, 1), ago(i, 4)
        for up in (True, False):
            a = r[4] if up else r[6]; sg = 1 if up else -1
            if a is None or not (0.03 <= a <= 0.97): continue
            sd_ = (lambda p: p if up else 1 - p)
            fair = sd_(r[2]); edge = fair - a
            h3 = R_[j3] if j3 is not None else None
            a3 = (h3[4] if up else h3[6]) if h3 else None
            e3 = sd_(h3[2]) - a3 if h3 else None
            grandit = edge >= 0.20 and e3 is not None and edge - e3 >= 0.03
            # 4 V2-F original et 6 miroir (décidé au même instant)
            if grandit and (st, "V2-F original") not in SIG:
                SIG[(st, "V2-F original")] = (i, up)
                x1, x4 = (R_[j1] if j1 is not None else None), (R_[j4] if j4 is not None else None)
                mir = bool(x1 and x4) and sd_(x1[2]) - a >= 0.20 and (sd_(x1[2]) - a) - (sd_(x4[2]) - a3) >= 0.03
                if not mir: SIG[(st, "V2-F miroir 1 s")] = (i, up)
                SIG.setdefault((st, "_miroir_decide"), (i, up))
            # 1 V2-D
            if edge >= 0.20 and 120 <= tl <= 269 and (st, "V2-D perp 120-269 s") not in SIG:
                h5 = R_[j5] if j5 is not None else None
                if h5 and h5[11] and r[11] and (r[11] - h5[11]) * sg >= 0: SIG[(st, "V2-D perp 120-269 s")] = (i, up)
            # 3 V2-G jury
            if edge >= 0.20 and h3 and (st, "V2-G jury des bourses") not in SIG:
                d3 = [((r[c] - h3[c]) * sg if r[c] and h3[c] else None) for c in (11, 12, 14, 13)]
                mid = lambda x: ((x[3] + x[4]) / 2 if up else (x[5] + x[6]) / 2)
                if all(v is not None and v >= 0 for v in d3) and any(v > 0 for v in d3) and (fair - sd_(h3[2])) - (mid(r) - mid(h3)) >= 0.03:
                    SIG[(st, "V2-G jury des bourses")] = (i, up)
            # 2 zone 30 + modèle monte
            if tl > 60 and 0.15 <= a < 0.35 and edge >= 0.30 and h3 and fair - sd_(h3[2]) >= 0.03 and (st, "Zone 30 + modèle monte") not in SIG:
                SIG[(st, "Zone 30 + modèle monte")] = (i, up)
            # 5 V2-F 0,01 %
            if (st, "V2-F 0,01 %") not in SIG and j3 is not None:
                p0, p3 = m01(i), m01(j3)
                if p0 is not None and p3 is not None:
                    f0_, f3_ = sd_(p0), sd_(p3)
                    if f0_ - a >= 0.20 and (f0_ - a) - (f3_ - a3) >= 0.03: SIG[(st, "V2-F 0,01 %")] = (i, up)
def executer(st, i, up, budget, pris=None):
    """achat au seul meilleur vendeur, quantité affichée moins ce que d'autres fantômes du même portefeuille ont déjà pris à ce prix"""
    r = C[st][i]; a = r[4] if up else r[6]; z = (r[8] if up else r[10]) or 0
    if pris is not None: z = max(0.0, z - pris.get((up, a), 0.0))
    q = min(budget / a, z)
    if q < 1: return None
    if pris is not None: pris[(up, a)] = pris.get((up, a), 0.0) + q
    y = O[f"BTC:{st}"]["gagnant"] == "Up"; gm = y if up else not y
    return dict(pn=q * ((1 if gm else 0) - a - FEE(a)), mise=q * a, gm=gm, up=up, a=a)
TR = {(st, n): executer(st, *SIG[(st, n)], 50) for st in valides for n in NOMS if (st, n) in SIG}
TR = {k: v for k, v in TR.items() if v}
PN = {n: np.array([TR[(st, n)]["pn"] if (st, n) in TR else 0.0 for st in valides]) for n in NOMS}
# ---------- régimes, connus au début du cycle
def tendance(st):
    """efficacité du mouvement sur 15 min : dernière valeur connue de chaque minute (au moins 12 minutes renseignées)"""
    P = []
    for k in range(15):
        v = [P1[s1] for s1 in range(st - 900 + 60 * k, st - 840 + 60 * k) if s1 in P1]
        if v: P.append(v[-1])
    if len(P) < 12: return None
    tot = sum(abs(P[k + 1] - P[k]) for k in range(len(P) - 1)); return abs(P[-1] - P[0]) / tot if tot > 0 else None
def clq(st):
    v = [CL1[k] for k in range(st - 600, st) if k in CL1]
    return sum(1 for k in range(1, len(v)) if v[k] != v[k - 1]) / 10 if len(v) > 300 else None
RG = {}
for st in valides:
    v = vol(st); RG[st] = dict(vol=None if v is None else ("calme" if v < 2 else "agité"), er=tendance(st), cl=clq(st),
                               bloc=["00-06 UTC", "06-12 UTC", "12-18 UTC", "18-24 UTC"][time.gmtime(st).tm_hour // 6])
APP = [st for st in valides if PER(st) == "apprentissage"]
ER_MED = float(np.median([RG[st]["er"] for st in APP if RG[st]["er"] is not None]))
CL_MED = float(np.median([RG[st]["cl"] for st in APP if RG[st]["cl"] is not None]))
for st in valides:
    g = RG[st]
    g["tend"] = None if g["er"] is None else ("directionnel" if g["er"] >= ER_MED else "oscillant")
    g["clq"] = None if g["cl"] is None else ("Chainlink rapide" if g["cl"] >= CL_MED else "Chainlink lent")
# ---------- outils
def st_(L):  # L = liste de trades (dict) dans l'ordre des cycles, None pour cycles sans achat
    T = [x for x in L if x]; cum = pk = dd = 0.0; c = cm = 0
    for x in T:
        cum += x["pn"]; pk = max(pk, cum); dd = min(dd, cum - pk); c = c + 1 if x["pn"] < 0 else 0; cm = max(cm, c)
    return dict(n=len(T), pnl=sum(x["pn"] for x in T), win=(100 * sum(x["gm"] for x in T) / len(T)) if T else 0, dd=dd, cm=cm,
                mise=sum(x["mise"] for x in T), jp=sum(1 for x in T if x["pn"] >= 4 * x["mise"]), jpv=sum(x["pn"] for x in T if x["pn"] >= 4 * x["mise"]))
def lig(nom, L, ncyc):
    s = st_(L); return f"| {nom} | {ncyc} | {s['n']} | {s['win']:.0f} % | **{f0(s['pnl'])}** | {f0(s['dd'])} | {s['cm']} | {f0(s['mise'])} | {s['jp']} ({f0(s['jpv'])}) |"
HD = "| Politique | Cycles | Achats | Gagnés | Résultat net | Creux max | Pertes de suite max | Capital engagé | Jackpots (gain) |\n|---|---|---|---|---|---|---|---|---|"
cyc = {p: [st for st in valides if PER(st) == p] for p in PERS}
out = [f"# BOT95 META-ROUTER — étude (aucun routeur actif)", "",
       f"{len(valides)} cycles BTC réglés : {hs(valides[0])} → {hs(valides[-1] + 300)}. "
       f"Apprentissage {len(cyc['apprentissage'])} cycles (< {hs(CUT)}) · validation {len(cyc['validation'])} (→ {hs(MATIN0)}) · inédit {len(cyc['inédit'])} (après).", "",
       "Achat au seul meilleur vendeur, quantité affichée, frais compris, 50 $ maximum, une décision par cycle ; cycles sans achat = 0 $. Jackpot = gain ≥ 4 × la mise.", ""]
# ---------- ÉTAPE 1
out += ["## Étape 1 — Complémentarité", "", "### Chaque stratégie seule", ""]
for p in PERS:
    out += [f"**{p}**", "", HD] + [lig(n, [TR.get((st, n)) for st in cyc[p]], len(cyc[p])) for n in NOMS] + [""]
out += ["### Chevauchements (toute la période) : cycles achetés par les deux · même côté · pertes communes", "",
        "| | " + " | ".join(CT[n] for n in NOMS) + " |", "|---|" + "---|" * len(NOMS)]
for a in NOMS:
    cel = []
    for b in NOMS:
        both = [st for st in valides if (st, a) in TR and (st, b) in TR]
        same = sum(1 for st in both if TR[(st, a)]["up"] == TR[(st, b)]["up"])
        pc = sum(1 for st in both if TR[(st, a)]["pn"] < 0 and TR[(st, b)]["pn"] < 0)
        cel.append(f"{len(both)} · {same} · {pc}" if a != b else f"**{sum(1 for st in valides if (st, a) in TR)}**")
    out.append(f"| {CT[a]} | " + " | ".join(cel) + " |")
out += ["", "### Gagnants exclusifs et jackpots (toute la période)", "", "| Stratégie | Gagnants | dont exclusifs (aucune autre ne gagne ce cycle) | Gain des exclusifs | Jackpots | dont exclusifs |", "|---|---|---|---|---|---|"]
for a in NOMS:
    W = [st for st in valides if (st, a) in TR and TR[(st, a)]["pn"] > 0]
    ex = [st for st in W if not any((st, b) in TR and TR[(st, b)]["pn"] > 0 for b in NOMS if b != a)]
    J = [st for st in W if TR[(st, a)]["pn"] >= 4 * TR[(st, a)]["mise"]]
    jx = [st for st in J if not any((st, b) in TR and TR[(st, b)]["pn"] >= 4 * TR[(st, b)]["mise"] for b in NOMS if b != a)]
    out.append(f"| {a} | {len(W)} | {len(ex)} | {f0(sum(TR[(st, a)]['pn'] for st in ex))} | {len(J)} | {len(jx)} |")
M = np.corrcoef(np.array([PN[n] for n in NOMS]))
out += ["", "### Corrélation des résultats par cycle (cycles sans achat = 0)", "", "| | " + " | ".join(CT[n] for n in NOMS) + " |", "|---|" + "---|" * len(NOMS)]
out += [f"| {CT[a]} | " + " | ".join(f"{M[i, j]:+.2f}" for j in range(len(NOMS))) + " |" for i, a in enumerate(NOMS)]
# ---------- ÉTAPE 2
out += ["", "## Étape 2 — Régimes (mesurés AVANT le début du cycle)", "",
        f"- Volatilité : écart type des variations du perp sur les 5 minutes d'avant ; calme < 2 $/s, agité ≥ 2 $/s (seuil du modèle E, pas réoptimisé).",
        f"- Directionnel / oscillant : efficacité du mouvement sur les 15 minutes d'avant (|déplacement net| / somme des mouvements minute par minute) ; seuil = médiane de l'apprentissage ({ER_MED:.2f}).",
        f"- Transmission Chainlink : nombre de nouvelles valeurs Chainlink reçues par minute sur les 10 minutes d'avant ; seuil = médiane de l'apprentissage ({CL_MED:.1f} par minute).",
        "- Blocs horaires UTC fixes : 00-06, 06-12, 12-18, 18-24 (heure suisse = UTC + 2).", "",
        "Chaque case : résultat net (achats). Colonnes « app. » = apprentissage, « hors app. » = validation + inédit.", ""]
DIMS = [("vol", "Volatilité"), ("tend", "Tendance"), ("clq", "Transmission Chainlink"), ("bloc", "Bloc horaire")]
for d, titre in DIMS:
    niv = sorted({RG[st][d] for st in valides if RG[st][d] is not None})
    out += [f"### {titre}", "", "| Stratégie | " + " | ".join(f"{v} app. | {v} hors app." for v in niv) + " |", "|---|" + "---|" * (2 * len(niv))]
    eff = []
    for v in niv:
        for grp in ("app", "hors"):
            S = [st for st in valides if RG[st][d] == v and ((PER(st) == "apprentissage") == (grp == "app"))]
            eff.append(str(len(S)))
    out.append("| *cycles* | " + " | ".join(eff) + " |")
    for n in NOMS:
        cel = []
        for v in niv:
            for grp in ("app", "hors"):
                S = [st for st in valides if RG[st][d] == v and ((PER(st) == "apprentissage") == (grp == "app"))]
                cel.append(f"{f0(sum(TR[(st, n)]['pn'] for st in S if (st, n) in TR))} ({sum(1 for st in S if (st, n) in TR)})")
        out.append(f"| {n} | " + " | ".join(cel) + " |")
    out.append("")
# ---------- ÉTAPE 3 : routeurs figés sur l'apprentissage
MIN_N = 10
def choix_case(S, defaut):
    """meilleure stratégie de la case sur l'apprentissage ; 'aucun achat' si aucune n'est positive ; défaut si trop peu d'achats"""
    cand = [(sum(TR[(st, n)]["pn"] for st in S if (st, n) in TR), n) for n in NOMS if sum(1 for st in S if (st, n) in TR) >= MIN_N]
    if not cand: return defaut
    best = max(cand)
    return best[1] if best[0] > 0 else "aucun achat"
R0 = max(NOMS, key=lambda n: sum(TR[(st, n)]["pn"] for st in APP if (st, n) in TR))
k1 = lambda st: (RG[st]["vol"], RG[st]["tend"])
k2 = lambda st: (RG[st]["vol"], RG[st]["tend"], RG[st]["bloc"])
T1 = {c: choix_case([st for st in APP if k1(st) == c], R0) for c in {k1(st) for st in valides}}
T2 = {c: choix_case([st for st in APP if k2(st) == c], T1.get(c[:2], R0)) for c in {k2(st) for st in valides}}
def route(table, key, st):
    n = table.get(key(st), R0) if None not in key(st) else R0
    return TR.get((st, n)) if n != "aucun achat" else None
def portefeuille(st):
    pris = {}; L = []
    for n in sorted(NOMS, key=lambda n: SIG[(st, n)][0] if (st, n) in SIG else 1e9):
        if (st, n) in SIG:
            x = executer(st, *SIG[(st, n)], 50 / len(NOMS), pris)
            if x: L.append(x)
    if not L: return None
    return dict(pn=sum(x["pn"] for x in L), mise=sum(x["mise"] for x in L), gm=sum(x["pn"] for x in L) > 0)
ROUT = {f"R0 — meilleure stratégie fixe de l'apprentissage ({R0})": lambda st: TR.get((st, R0)),
        "R1 — choix selon volatilité et tendance": lambda st: route(T1, k1, st),
        "R2 — R1 + bloc horaire": lambda st: route(T2, k2, st),
        "R3 — portefeuille fixe des 6 (8,33 $ chacune, 50 $ au total)": portefeuille}
out += ["## Étape 3 — Routeurs (règles figées sur l'apprentissage, jugées sur validation et inédit)", "",
        f"R1 et R2 : dans chaque case, la stratégie au meilleur résultat d'apprentissage (au moins {MIN_N} achats), « aucun achat » si aucune n'y gagne ; "
        "case trop maigre → choix de R1 (pour R2) ou de R0. Les fantômes qui achètent au même moment ne cumulent rien : une seule enveloppe de 50 $ par cycle ; "
        "dans le portefeuille, chaque achat ne prend que la quantité affichée laissée par les achats précédents au même prix.", ""]
for p in PERS:
    out += [f"**{p}**", "", HD] + [lig(nom, [f(st) for st in cyc[p]], len(cyc[p])) for nom, f in ROUT.items()] + [""]
HO = cyc["validation"] + cyc["inédit"]
out += ["**hors apprentissage (validation + inédit)**", "", HD] + [lig(nom, [f(st) for st in HO], len(HO)) for nom, f in ROUT.items()] + [""]
out += ["### Ce que les routeurs ont choisi (sur l'apprentissage)", "", "| Case R1 (volatilité, tendance) | Choix | Cycles app. | Cycles hors app. |", "|---|---|---|---|"]
for c, n in sorted(T1.items(), key=lambda x: str(x[0])):
    out.append(f"| {c[0]} / {c[1]} | {n} | {sum(1 for st in APP if k1(st) == c)} | {sum(1 for st in HO if k1(st) == c)} |")
out += ["", "| Case R2 | Choix | Cycles app. | Cycles hors app. |", "|---|---|---|---|"]
for c, n in sorted(T2.items(), key=lambda x: str(x[0])):
    if None in c: continue
    out.append(f"| {' / '.join(c)} | {n} | {sum(1 for st in APP if k2(st) == c)} | {sum(1 for st in HO if k2(st) == c)} |")
# incertitude : bootstrap par blocs de 12 cycles (1 h) sur la différence hors apprentissage
rng = np.random.default_rng(7)
def diff_boot(fa, fb, S, B=4000):
    d = np.array([((fa(st) or {}).get("pn", 0.0)) - ((fb(st) or {}).get("pn", 0.0)) for st in S]); nb = max(1, len(d) // 12)
    blocs = [d[k * 12:(k + 1) * 12] for k in range(nb)]
    sims = [sum(blocs[j].sum() for j in rng.integers(0, nb, nb)) for _ in range(B)]
    return d.sum(), np.percentile(sims, 5), np.percentile(sims, 95), float(np.mean(np.array(sims) <= 0))
out += ["", "### Le dynamique bat-il le fixe ? Différence hors apprentissage, incertitude par blocs d'une heure", "",
        "| Comparaison | Différence | Intervalle à 90 % | Probabilité que ce soit ≤ 0 |", "|---|---|---|---|"]
rn = list(ROUT.items())
for a, b in ((1, 0), (2, 0), (1, 3), (2, 3), (3, 0)):
    d, lo, hi, pz = diff_boot(rn[a][1], rn[b][1], HO)
    out.append(f"| {rn[a][0].split(' —')[0]} − {rn[b][0].split(' —')[0]} | {f0(d)} | [{f0(lo)} ; {f0(hi)}] | {100 * pz:.0f} % |")
# routeur « après coup » : la meilleure par case en regardant les cycles jugés (illusion)
T1x = {c: choix_case([st for st in HO if k1(st) == c], R0) for c in {k1(st) for st in valides}}
out += ["", f"Pour mesurer l'illusion : R1 construit en regardant les cycles hors apprentissage eux-mêmes ferait {f0(sum((route(T1x, k1, st) or {}).get('pn', 0) for st in HO))} sur ces cycles — c'est ce qu'on obtient quand on optimise sur les données qu'on juge.", ""]
open("etude/bot5min/resultat_meta_router.md", "w").write("\n".join(out)); print("\n".join(out))
