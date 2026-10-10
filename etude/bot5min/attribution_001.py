"""Attribution exacte des signaux « V2-F 0,01 % » (demande de Pitch 10.10.2026 13:59). Diagnostic seulement, aucun filtre construit.
Question : les gagnants que seule la version 0,01 % prend viennent-ils de la FORMULE (incertitude 0,01 % au lieu de 0,08 %) ou d'un DÉTAIL
(modèle reconstruit pour l'étude ≠ modèle du bot, moment de déclenchement) ? Et que deviennent-ils avec une exécution réaliste ?
Quatre versions de la MÊME règle V2-F (écart ≥ 0,20 qui a grandi d'au moins 3 c en 3 s, vendeur 0,03-0,97, premier signal du cycle) :
  O8 = modèle du bot tel qu'enregistré (0,08 %) = V2-F original
  X8 = modèle reconstruit par l'étude, 0,08 %        X1 = modèle reconstruit, 0,01 % (celui du META-ROUTER)
  H1 = modèle du bot ramené à 0,01 % : on garde SA distance au prix d'exercice (z × écart type 0,08 %) et on ne change que l'écart type
       → c'est ce que calcule le fantôme réel « V2-F incertitude 0,01 % » (même formule probaV1, seul sdRel change).
X1 − X8 = effet de la formule à données identiques ; X8 − O8 = effet de la reconstruction (détail) ; H1 − O8 = effet de la formule dans le moteur du bot.
Exécution : au seul meilleur vendeur, quantité affichée, 50 $ maximum, avec un délai de 0 / 0,5 / 1 / 2 s : on achète sur le carnet du moment
d'exécution, seulement au prix vu à la décision ou mieux (sinon rien)."""
import sys
from statistics import NormalDist
sys.path.insert(0, "etude/bot5min")
exec(open("etude/bot5min/meta_router.py").read().split("# ---------- outils")[0])
ND = NormalDist()
def parts_r(r, st):
    """reconstruction : renvoie (proba 0,08, v, S) ou None"""
    K = r[16]; p = r[11] or r[12]; s = int(r[0])
    if not K or not p: return None
    sg, b = volr(s), baser(s)
    if sg is None or b is None: return None
    S = p - b; end = st + 300; deb = end - 59
    if s >= deb:
        con = [CL1[k] for k in range(deb, s + 1) if k in CL1]; nr = max(1, end - s)
        E = (sum(con) + nr * S) / (len(con) + nr); v = (sg * S) ** 2 * nr ** 3 / 3 / 3600
    else: E = S; v = (sg * S) ** 2 * ((deb - s) + 20)
    return E - K, v, S
def proba(version, st, i, cache):
    k = (version, i)
    if k in cache: return cache[k]
    r = C[st][i]; out = None
    if version == "O8": out = r[2]
    else:
        x = parts_r(r, st)
        if x:
            d, v, S = x
            if version == "X8": out = phi(d / math.sqrt(v + (8e-4 * S) ** 2))
            elif version == "X1": out = phi(d / math.sqrt(v + (1e-4 * S) ** 2))
            elif version == "H1" and r[2] is not None:
                z8 = ND.inv_cdf(min(0.9999, max(0.0001, r[2])))
                out = phi(z8 * math.sqrt(v + (8e-4 * S) ** 2) / math.sqrt(v + (1e-4 * S) ** 2))
    cache[k] = out; return out
VERS = ["O8", "X8", "X1", "H1"]
VN = {"O8": "O8 modèle du bot 0,08 % (V2-F original)", "X8": "X8 reconstruit 0,08 %", "X1": "X1 reconstruit 0,01 %", "H1": "H1 modèle du bot ramené à 0,01 % (= fantôme réel)"}
SIGV = {}       # (version, st) -> dict(i, up, edge, croiss, ...)
for st in valides:
    R_ = C[st]
    if not R_: continue
    T_ = [r[0] for r in R_]; end = st + 300; cache = {}
    for ver in VERS:
        for i, r in enumerate(R_):
            if end - r[0] < 5: break
            j3 = bisect.bisect_right(T_, r[0] - 3) - 1
            if j3 < 0: continue
            p0, p3 = proba(ver, st, i, cache), proba(ver, st, j3, cache)
            if p0 is None or p3 is None: continue
            hit = None
            for up in (True, False):
                a = r[4] if up else r[6]; a3 = R_[j3][4] if up else R_[j3][6]
                if a is None or a3 is None or not (0.03 <= a <= 0.97): continue
                f0_, f3_ = (p0, p3) if up else (1 - p0, 1 - p3)
                if f0_ - a >= 0.20 and (f0_ - a) - (f3_ - a3) >= 0.03: hit = (up, f0_, a, (f0_ - a) - (f3_ - a3)); break
            if hit:
                SIGV[(ver, st)] = dict(i=i, t=r[0], up=hit[0], fair=hit[1], a=hit[2], cr=hit[3], tl=end - r[0]); break
def execu(st, s, delta):
    R_ = C[st]; T_ = [r[0] for r in R_]
    k = bisect.bisect_left(T_, s["t"] + delta)
    if k >= len(R_) or R_[k][0] >= st + 300: return None
    r = R_[k]; a = r[4] if s["up"] else r[6]; z = (r[8] if s["up"] else r[10]) or 0
    if a is None or a > s["a"] + 1e-9: return None            # le prix a monté : rien (meilleur vendeur seul, limite = prix vu)
    q = min(50 / a, z)
    if q < 1: return None
    y = O[f"BTC:{st}"]["gagnant"] == "Up"; gm = y if s["up"] else not y
    return dict(pn=q * ((1 if gm else 0) - a - FEE(a)), mise=q * a, gm=gm)
def bilan(L):
    T = [x for x in L if x]; cum = pk = dd = 0.0
    for x in T: cum += x["pn"]; pk = max(pk, cum); dd = min(dd, cum - pk)
    return len(T), sum(x["pn"] for x in T), dd, sum(1 for x in T if x["pn"] >= 4 * x["mise"]), (100 * sum(x["gm"] for x in T) / len(T)) if T else 0
cyc = {p: [st for st in valides if PER(st) == p] for p in PERS}
out = ["# V2-F 0,01 % — attribution exacte des signaux", "",
       f"{len(valides)} cycles BTC réglés ({hs(valides[0])} → {hs(valides[-1] + 300)}). Apprentissage {len(cyc['apprentissage'])} · validation {len(cyc['validation'])} · inédit {len(cyc['inédit'])} (après le 10.10 10:25).", "",
       "Quatre versions de la même règle V2-F, mêmes cycles :", ""] + [f"- **{VN[v]}**" for v in VERS] + [""]
# 0. controle : X1 = la V2-F 0,01 % du META-ROUTER
same = sum(1 for st in valides if ((("X1", st) in SIGV) == ((st, "V2-F 0,01 %") in SIG)))
out += [f"Contrôle : la version X1 refait exactement la « V2-F 0,01 % » du META-ROUTER sur {same} cycles sur {len(valides)}.", ""]
# 1. qui déclenche où
out += ["## 1. Recouvrement des signaux (cycles où chaque version achète)", "", "| | O8 | X8 | X1 | H1 |", "|---|---|---|---|---|"]
for a in VERS:
    cel = []
    for b in VERS:
        A = {st for (v, st) in SIGV if v == a}; B = {st for (v, st) in SIGV if v == b}
        both = A & B; same_side = sum(1 for st in both if SIGV[(a, st)]["up"] == SIGV[(b, st)]["up"])
        near = sum(1 for st in both if SIGV[(a, st)]["up"] == SIGV[(b, st)]["up"] and abs(SIGV[(a, st)]["t"] - SIGV[(b, st)]["t"]) <= 1)
        cel.append(f"**{len(A)}**" if a == b else f"{len(both)} · {same_side} · {near}")
    out.append(f"| {a} | " + " | ".join(cel) + " |")
out += ["", "Chaque case : cycles achetés par les deux · même côté · même côté à 1 s près.", ""]
# 2. les gagnants exclusifs du META-ROUTER
EX = [st for st in valides if (st, "V2-F 0,01 %") in TR and TR[(st, "V2-F 0,01 %")]["pn"] > 0
      and not any((st, b) in TR and TR[(st, b)]["pn"] > 0 for b in NOMS if b != "V2-F 0,01 %")]
def classe(st):
    s1 = SIGV.get(("X1", st)); s8 = SIGV.get(("X8", st)); o8 = SIGV.get(("O8", st)); h1 = SIGV.get(("H1", st))
    if s8 and s8["up"] == s1["up"] and abs(s8["t"] - s1["t"]) <= 1: c = "reconstruction : X8 (0,08 %) prend le même signal → la formule n'y est pour rien"
    elif s8 and s8["up"] == s1["up"]: c = "moment : X8 prend le même côté, mais à un autre instant"
    elif s8: c = "côté opposé chez X8"
    else: c = "formule : X8 (0,08 %, mêmes données) ne déclenche pas dans ce cycle"
    return c, bool(h1 and h1["up"] == s1["up"]), bool(o8)
out += ["## 2. Les 47 gagnants exclusifs : d'où viennent-ils ?", "",
        f"{len(EX)} cycles où X1 gagne alors qu'aucune des cinq autres stratégies ne gagne. Pour chacun : que fait X8 (même modèle reconstruit, 0,08 %) ? et H1 (le moteur du bot à 0,01 %) le prend-il aussi ?", "",
        "| Origine | Cycles | Gain (exécution du META-ROUTER) | dont aussi pris par H1 (même côté) | V2-F original achète ce cycle |", "|---|---|---|---|---|"]
G = collections.defaultdict(list)
for st in EX: G[classe(st)[0]].append(st)
for c, L in sorted(G.items(), key=lambda x: -len(x[1])):
    out.append(f"| {c} | {len(L)} | {f0(sum(TR[(st, 'V2-F 0,01 %')]['pn'] for st in L))} | {sum(1 for st in L if classe(st)[1])} | {sum(1 for st in L if classe(st)[2])} |")
# 3. Pourquoi la formule ajoute des signaux : à l'instant du signal X1, que voit X8 ?
F_only = [st for st in valides if ("X1", st) in SIGV and ("X8", st) not in SIGV]
F_both = [st for st in valides if ("X1", st) in SIGV and ("X8", st) in SIGV]
X8_only = [st for st in valides if ("X8", st) in SIGV and ("X1", st) not in SIGV]
out += ["", "## 3. Ce que la formule change, à données identiques (X1 contre X8)", "",
        f"- Cycles achetés par les deux : {len(F_both)} ; seulement à 0,01 % : {len(F_only)} ; seulement à 0,08 % : {len(X8_only)}.", ""]
why = collections.Counter(); prix = collections.defaultdict(list); tl = collections.defaultdict(list); p8l = []
for st in F_only:
    s = SIGV[("X1", st)]; R_ = C[st]; T_ = [r[0] for r in R_]; i = s["i"]; j3 = bisect.bisect_right(T_, R_[i][0] - 3) - 1
    d, v, S = parts_r(R_[i], st); p8 = phi(d / math.sqrt(v + (8e-4 * S) ** 2)); f8 = p8 if s["up"] else 1 - p8
    x3 = parts_r(R_[j3], st); p83 = phi(x3[0] / math.sqrt(x3[1] + (8e-4 * x3[2]) ** 2)) if x3 else None
    a3 = R_[j3][4] if s["up"] else R_[j3][6]; f83 = (p83 if s["up"] else 1 - p83) if p83 is not None else None
    e8 = f8 - s["a"]; g8 = (e8 - (f83 - a3)) if f83 is not None else None
    why["à 0,08 % l'écart n'atteint pas 0,20" if e8 < 0.20 else ("à 0,08 % l'écart est là mais n'a pas grandi de 3 c en 3 s" if g8 is not None and g8 < 0.03 else "autre")] += 1
    p8l.append((s["fair"], f8, s["a"], s["tl"], math.sqrt(v), 8e-4 * S, 1e-4 * S))
out += ["À l'instant précis où X1 déclenche dans un cycle que X8 ne prend jamais :", "", "| Raison | Cycles |", "|---|---|"] + [f"| {k} | {v} |" for k, v in why.most_common()]
P = np.array(p8l)
out += ["", f"Profil médian de ces {len(F_only)} signaux : probabilité 0,01 % = {np.median(P[:, 0]):.2f}, la même à 0,08 % = {np.median(P[:, 1]):.2f}, prix payé = {np.median(P[:, 2]):.2f}, "
        f"temps restant = {np.median(P[:, 3]):.0f} s ; incertitude due au mouvement d'ici la fin = {np.median(P[:, 4]):.1f} $, incertitude fixe 0,08 % = {np.median(P[:, 5]):.1f} $, 0,01 % = {np.median(P[:, 6]):.1f} $.", ""]
tb = collections.defaultdict(lambda: [0, 0.0])
for st in F_only:
    s = SIGV[("X1", st)]; k = "> 120 s" if s["tl"] > 120 else ("60-120 s" if s["tl"] > 60 else "< 60 s")
    x = execu(st, s, 0); tb[k][0] += 1; tb[k][1] += x["pn"] if x else 0
out += ["| Temps restant au signal (seulement à 0,01 %) | Cycles | Résultat (exécution sans délai) |", "|---|---|---|"] + [f"| {k} | {v[0]} | {f0(v[1])} |" for k, v in sorted(tb.items())] + [""]
# 4. exécution réaliste
out += ["## 4. Exécution réaliste : meilleur vendeur seul, quantité affichée, délai entre décision et achat", "",
        "Achat sur le carnet du moment d'exécution, jamais plus cher que le prix vu à la décision.", ""]
for grp, f in (("toutes périodes", lambda st: True), ("apprentissage", lambda st: PER(st) == "apprentissage"),
               ("validation", lambda st: PER(st) == "validation"), ("inédit (après 10.10 10:25)", lambda st: PER(st) == "inédit")):
    out += [f"### {grp}", "", "| Version | Délai 0 s | 0,25 s | 0,5 s | 1 s | 2 s | Achats (0 s) | Gagnés | Creux (0 s) | Jackpots (0 s) |", "|---|---|---|---|---|---|---|---|---|---|"]
    for v in VERS:
        S_ = [st for st in valides if f(st) and (v, st) in SIGV]
        res = [bilan([execu(st, SIGV[(v, st)], d) for st in S_]) for d in (0, 0.25, 0.5, 1, 2)]
        out.append(f"| {VN[v]} | " + " | ".join(f"**{f0(x[1])}**" if k == 0 else f0(x[1]) for k, x in enumerate(res)) + f" | {res[0][0]} | {res[0][4]:.0f} % | {f0(res[0][2])} | {res[0][3]} |")
    # la part propre à 0,01 % dans le moteur du bot
    S_ = [st for st in valides if f(st) and ("H1", st) in SIGV and ("O8", st) not in SIGV]
    res = [bilan([execu(st, SIGV[("H1", st)], d) for st in S_]) for d in (0, 0.25, 0.5, 1, 2)]
    out.append(f"| ↳ H1 seulement (cycles que V2-F original ne prend pas) | " + " | ".join(f0(x[1]) for x in res) + f" | {res[0][0]} | {res[0][4]:.0f} % | {f0(res[0][2])} | {res[0][3]} |")
    S_ = [st for st in valides if f(st) and ("X1", st) in SIGV and ("X8", st) not in SIGV]
    res = [bilan([execu(st, SIGV[("X1", st)], d) for st in S_]) for d in (0, 0.25, 0.5, 1, 2)]
    out.append(f"| ↳ X1 seulement (cycles que X8 ne prend pas) | " + " | ".join(f0(x[1]) for x in res) + f" | {res[0][0]} | {res[0][4]:.0f} % | {f0(res[0][2])} | {res[0][3]} |")
    out.append("")
# 4b. pourquoi le délai coûte : achats perdus (prix monté) contre achats faits à un autre prix
out += ["### Pourquoi le délai coûte autant (toutes périodes)", "",
        "| Version | Délai | Achats à 0 s | Encore achetables après le délai | Résultat à 0 s des achats PERDUS (le prix a monté) | dont gagnants perdus | Résultat des achats faits : à 0 s → après délai |", "|---|---|---|---|---|---|---|"]
for v in ("O8", "H1", "X1"):
    S_ = [st for st in valides if (v, st) in SIGV]
    for d in (0.25, 0.5, 1):
        z0 = {st: execu(st, SIGV[(v, st)], 0) for st in S_}; zd = {st: execu(st, SIGV[(v, st)], d) for st in S_}
        perdus = [st for st in S_ if z0[st] and not zd[st]]; faits = [st for st in S_ if z0[st] and zd[st]]
        out.append(f"| {v} | {d} s | {sum(1 for st in S_ if z0[st])} | {len(faits)} | {f0(sum(z0[st]['pn'] for st in perdus))} ({len(perdus)}) | {sum(1 for st in perdus if z0[st]['pn'] > 0)} | "
                   f"{f0(sum(z0[st]['pn'] for st in faits))} → {f0(sum(zd[st]['pn'] for st in faits))} |")
out.append("")
# 5. cycles où les deux prennent : la formule change-t-elle le moment ou le côté ?
bothO = [st for st in valides if ("H1", st) in SIGV and ("O8", st) in SIGV]
dt = [SIGV[("H1", st)]["t"] - SIGV[("O8", st)]["t"] for st in bothO if SIGV[("H1", st)]["up"] == SIGV[("O8", st)]["up"]]
out += ["## 5. Quand le moteur du bot à 0,01 % (H1) et V2-F original (O8) prennent le même cycle", "",
        f"- {len(bothO)} cycles communs, dont {len(dt)} du même côté et {len(bothO) - len(dt)} du côté opposé.",
        f"- Même côté : H1 déclenche en médiane {np.median(dt):+.1f} s par rapport à O8 (au même instant à 1 s près : {sum(1 for x in dt if abs(x) <= 1)} cycles).", ""]
open("etude/bot5min/resultat_attribution_001.md", "w").write("\n".join(out)); print("\n".join(out))
