"""Sélecteur de stratégie par condition de marché et heure (demande de Pitch 10.10.2026 13:40).
Question : choisir, pour chaque cycle, la stratégie qui a le mieux marché PAR LE PASSÉ dans la même condition (régime calme / agité, tranche horaire)
bat-il le simple choix d'UNE stratégie (la meilleure par le passé) jouée tout le temps ?
Méthode « jour après jour » (walk-forward) : blocs de 12 h ; pour chaque bloc, la sélection n'utilise que les cycles déjà réglés avant le début du bloc.
Conditions fixées À L'AVANCE, connues au début du cycle : régime = volatilité du perp sur 300 s au début du cycle (< 2 $/s = calme),
tranche = heure suisse du début du cycle (nuit 00-08, Europe 08-15:30, US 15:30-24).
Stratégies rejouées sur les carnets enregistrés 4×/s : une décision par cycle, 50 $ maximum au SEUL meilleur vendeur dans la quantité affichée, frais compris.
Aucune donnée future dans les décisions. Diagnostic seulement : rien n'est modifié dans le bot."""
import sys, json
sys.path.insert(0, "etude/bot5min")
exec(open("etude/bot5min/robustesse_E.py").read().split("def rejouer(delta):")[0])
from datetime import datetime, timezone
HS = lambda st: datetime.fromtimestamp(st + 7200, timezone.utc)
def tranche(st):
    d = HS(st); m = d.hour * 60 + d.minute
    return "nuit 00-08" if m < 480 else ("Europe 08-15:30" if m < 930 else "US 15:30-24")
def regime(st):
    v = vol(st); return None if v is None else ("calme" if v < 2 else "agité")
NOMS = ["desaccord 20", "V2-B hors 60-89 s", "V2-C perp", "V2-D perp 120-269 s", "V2-E persistant", "V2-F ecart qui grandit",
        "V2-F + plus de 120 s", "V2-F + pas les deux baissent", "zone 30 (0,15-0,35)", "TWAP fin A (original)", "TWAP fin E (quantiles)"]
def achat(R_, i, up, y):
    r = R_[i]; a = r[4] if up else r[6]; z = (r[8] if up else r[10]) or 0
    q = min(50 / a, z)
    if q < 1: return None
    gm = y if up else not y
    return dict(pn=q * ((1 if gm else 0) - a - FEE(a)), mise=q * a, gm=gm, a=a)
TR = {}            # (st, nom) -> trade
for st in valides:
    R_ = C[st]; y = O[f"BTC:{st}"]["gagnant"] == "Up"; end = st + 300; fait = set(); T_ = [r[0] for r in R_]
    def ilya(i, sec_):
        t = R_[i][0]
        for j in range(i, -1, -1):
            if t - R_[j][0] >= sec_: return R_[j]
        return None
    for i, r in enumerate(R_):
        t = r[0]; tl = end - t
        if tl < 5: break
        if r[2] is None: continue
        h3, h5 = ilya(i, 3), ilya(i, 5)
        for up in (True, False):
            a = r[4] if up else r[6]
            if a is None or not (0.03 <= a <= 0.97): continue
            fair = r[2] if up else 1 - r[2]; edge = fair - a; sg = 1 if up else -1
            ed = lambda x: None if x is None or x[2] is None or (x[4] if up else x[6]) is None else ((x[2] if up else 1 - x[2]) - (x[4] if up else x[6]))
            e3 = ed(h3)
            grandit = e3 is not None and edge - e3 >= 0.03
            perp5 = (r[11] - h5[11]) * sg if h5 and h5[11] and r[11] else None
            rec = [x for x in R_[:i + 1] if t - x[0] <= 1.5]
            persist = len(rec) >= 4 and all((ed(x) or -1) >= 0.20 for x in rec) and t - R_[0][0] >= 1.5
            dmo = (fair - (h3[2] if up else 1 - h3[2])) if h3 and h3[2] is not None else 0
            dpo = (a - (h3[4] if up else h3[6])) if h3 and (h3[4] if up else h3[6]) is not None else 0
            deuxB = bool(h3) and dmo < 0 and dpo < dmo and not (abs(dmo) < 0.02 and dpo <= -0.02)
            V = {}
            if edge >= 0.20:
                V = {"desaccord 20": True, "V2-B hors 60-89 s": not (60 <= tl < 90), "V2-C perp": perp5 is not None and perp5 >= 0,
                     "V2-D perp 120-269 s": perp5 is not None and perp5 >= 0 and 120 <= tl <= 269, "V2-E persistant": persist,
                     "V2-F ecart qui grandit": grandit, "V2-F + plus de 120 s": grandit and tl >= 120, "V2-F + pas les deux baissent": grandit and not deuxB}
            if tl > 60 and edge >= 0.30 and 0.15 <= a < 0.35: V["zone 30 (0,15-0,35)"] = True
            for nom, ok in V.items():
                if ok and nom not in fait:
                    x = achat(R_, i, up, y); fait.add(nom)
                    if x: TR[(st, nom)] = x
        # TWAP fin A et E : premier signal du cycle, avantage >= 0,20, entre 90 et 20 s
        if 20 <= tl <= 90 and not {"TWAP fin A (original)", "TWAP fin E (quantiles)"} <= fait:
            m = modele(st, t)
            if m:
                for nom, p in (("TWAP fin A (original)", m[0]), ("TWAP fin E (quantiles)", m[1])):
                    if nom in fait: continue
                    for up in (True, False):
                        a = r[4] if up else r[6]
                        if a is None or not (0.02 <= a <= 0.98): continue
                        if (p if up else 1 - p) - a >= 0.20:
                            x = achat(R_, i, up, y); fait.add(nom)
                            if x: TR[(st, nom)] = x
                            break
COND = {st: (regime(st), tranche(st)) for st in valides}
# blocs de 12 h (heure suisse)
bloc = lambda st: (st + 7200) // 43200
BL = sorted({bloc(st) for st in valides})
hb = lambda b: time.strftime("%d.%m %Hh", time.gmtime(b * 43200))
def pn(st, nom): x = TR.get((st, nom)); return x["pn"] if x else 0.0
CLES = {"régime": lambda st: COND[st][0], "tranche": lambda st: COND[st][1], "régime × tranche": lambda st: f"{COND[st][0]} / {COND[st][1]}"}
MIN_T = 8                       # minimum de trades passés dans la case pour s'y fier, sinon la meilleure stratégie globale
def meilleure(passe, nom_list=NOMS):
    return max(nom_list, key=lambda n: sum(pn(st, n) for st in passe))
res = collections.defaultdict(list)     # politique -> liste de (st, trade or None)
choix_log = []
tests = BL[2:]                          # les 2 premiers blocs servent seulement d'historique
for b in tests:
    deb = b * 43200 - 7200
    passe = [st for st in valides if st + 300 <= deb]
    cyc = [st for st in valides if bloc(st) == b]
    g = meilleure(passe)
    for st in cyc: res["une seule stratégie (la meilleure du passé)"].append((st, g))
    lg = [f"{hb(b)} : globale = {g}"]
    for cn, f in CLES.items():
        cases = {}
        for st in cyc:
            c = f(st)
            if c not in cases:
                P = [s for s in passe if f(s) == c]
                bons = [n for n in NOMS if sum(1 for s in P if (s, n) in TR) >= MIN_T]
                cases[c] = meilleure(P, bons) if bons and sum(pn(s, meilleure(P, bons)) for s in P) > 0 else g
            res[f"sélecteur par {cn}"].append((st, cases[c]))
        lg.append(f"{cn} : " + " ; ".join(f"{c} → {n}" for c, n in sorted(cases.items(), key=lambda x: str(x[0]))))
    choix_log.append(lg)
    for n in NOMS: res[n].extend((st, n) for st in cyc)
def stats(L_):
    T = [TR[(st, n)] for st, n in L_ if (st, n) in TR]
    if not T: return dict(n=0, pnl=0, win=0, dd=0, consec=0, mise=0, jp=0)
    cum = pk = dd = 0.0; c = cm = 0
    for x in T:
        cum += x["pn"]; pk = max(pk, cum); dd = min(dd, cum - pk)
        c = c + 1 if x["pn"] < 0 else 0; cm = max(cm, c)
    return dict(n=len(T), pnl=sum(x["pn"] for x in T), win=100 * sum(x["gm"] for x in T) / len(T), dd=dd, consec=cm, mise=sum(x["mise"] for x in T),
                jp=sum(1 for x in T if x["pn"] >= 4 * x["mise"]))
def ligne(nom, L_):
    s = stats(L_); return f"| {nom} | {s['n']} | {s['win']:.0f} % | **{f0(s['pnl'])}** | {f0(s['dd'])} | {s['consec']} | {f0(s['mise'])} | {s['jp']} |"
H = "| Politique | Trades | Gagnés | Résultat net | Creux max | Pertes consécutives max | Capital engagé | Jackpots |\n|---|---|---|---|---|---|---|---|"
out = [f"# Sélecteur par condition de marché et par heure — test jour après jour", "",
       f"Données : {len(valides)} cycles BTC réglés ({hs(valides[0])} → {hs(valides[-1] + 300)}), carnets enregistrés 4×/s.",
       f"Blocs de 12 h ; {len(tests)} blocs de test ({hb(tests[0])} → {hb(tests[-1])}), chacun jugé avec un choix fait uniquement sur les cycles réglés avant lui.", "",
       "## Résultat sur les blocs de test (choix faits sans connaître le bloc)", "", H]
for nom in ["une seule stratégie (la meilleure du passé)", "sélecteur par régime", "sélecteur par tranche", "sélecteur par régime × tranche"]:
    out.append(ligne(nom, res[nom]))
out += ["", "Pour comparaison, chaque stratégie jouée tout le temps sur les mêmes blocs :", "", H]
for nom in sorted(NOMS, key=lambda n: -stats(res[n])["pnl"]): out.append(ligne(nom, res[nom]))
# par bloc
out += ["", "## Bloc par bloc", "", "| Bloc | Une seule | Par régime | Par tranche | Par régime × tranche | Meilleure stratégie après coup |", "|---|---|---|---|---|---|"]
for b in tests:
    f_ = lambda nom: f0(sum(pn(st, n) for st, n in res[nom] if bloc(st) == b))
    cyc = [st for st in valides if bloc(st) == b]; mb = meilleure(cyc)
    out.append(f"| {hb(b)} | {f_('une seule stratégie (la meilleure du passé)')} | {f_('sélecteur par régime')} | {f_('sélecteur par tranche')} | {f_('sélecteur par régime × tranche')} | {mb} ({f0(sum(pn(s, mb) for s in cyc))}) |")
# illusion : meilleur choix par case après coup sur toute la période
out += ["", "## L'illusion du « après coup »", "", "Si l'on choisit la meilleure stratégie de chaque case en regardant toute la période (y compris les cycles jugés), le résultat est forcément magnifique :", "", "| Choix après coup | Résultat net |", "|---|---|"]
TT = [st for st in valides if bloc(st) in tests]
for cn, f in CLES.items():
    tot = 0
    for c in {f(st) for st in TT}:
        P = [st for st in TT if f(st) == c]; m = meilleure(P); tot += sum(pn(st, m) for st in P)
    out.append(f"| par {cn} | {f0(tot)} |")
m = meilleure(TT); out.append(f"| une seule stratégie | {f0(sum(pn(st, m) for st in TT))} ({m}) |")
# stabilite du classement : la meilleure d'un bloc reste-t-elle bonne au bloc suivant ?
out += ["", "## Le classement est-il stable d'un bloc à l'autre ?", "",
        "Corrélation de rang (Spearman) entre le résultat des 11 stratégies dans une case pendant un bloc et pendant le bloc suivant. Proche de 0 = le classement d'hier ne dit rien sur demain.", "",
        "| Case | Corrélation moyenne | Blocs comparés |", "|---|---|---|"]
def rang(v): o = np.argsort(np.argsort(v)); return o
for cn, f in (("toutes conditions", lambda st: "tout"),) + tuple(CLES.items()):
    cs = collections.defaultdict(list)
    for c in sorted({f(st) for st in valides}, key=str):
        for b0, b1 in zip(BL, BL[1:]):
            A = [sum(pn(st, n) for st in valides if bloc(st) == b0 and f(st) == c) for n in NOMS]
            B = [sum(pn(st, n) for st in valides if bloc(st) == b1 and f(st) == c) for n in NOMS]
            if np.std(A) > 0 and np.std(B) > 0: cs[c].append(float(np.corrcoef(rang(A), rang(B))[0, 1]))
    for c, v in cs.items(): out.append(f"| {cn} : {c} | {np.mean(v):+.2f} | {len(v)} |")
# resultats par case sur toute la periode
out += ["", "## Résultat de chaque stratégie par régime et par tranche (toute la période, pour information)", ""]
for cn, f in (("régime", CLES["régime"]), ("tranche", CLES["tranche"])):
    cs = sorted({f(st) for st in valides}, key=str)
    out += [f"| Stratégie | " + " | ".join(str(c) for c in cs) + " |", "|---|" + "---|" * len(cs)]
    for n in NOMS:
        out.append(f"| {n} | " + " | ".join(f"{f0(sum(pn(st, n) for st in valides if f(st) == c))} ({sum(1 for st in valides if f(st) == c and (st, n) in TR)})" for c in cs) + " |")
    out.append("")
out += ["## Choix faits à chaque bloc", ""] + [f"- " + "<br>".join(l) for l in choix_log]
open("etude/bot5min/resultat_selecteur.md", "w").write("\n".join(out)); print("\n".join(out))
