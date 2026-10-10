"""Tournoi des prévisions Chainlink (demande ChatGPT 10.10.2026 08:05) — BTC, 07.10 → 10.10 07:30, données enregistrées par le bot.
Q1 transmission exchanges -> Chainlink ; Q17 persistance des sauts ; Q18 basculements extrêmes de probabilité ;
tournoi A actuel / B anti-saut / C persistance du saut (Shock Decay) / D prévision Chainlink (Nowcast).
Coefficients de C et D appris sur la période d'apprentissage seulement ; validation sur les jours suivants et sur la nuit du 10.10 séparément.
Diagnostic seulement : aucune stratégie modifiée."""
import sys
sys.path.insert(0, "etude/bot5min")
exec(open("etude/bot5min/twap_etudes.py").read().split("C = collections.defaultdict(list)")[0])
EXCH = ("perp", "okx", "bn", "cb")
def lev(nom, t):
    p = der(nom, t); b = base(nom, int(t))
    return p - b if p is not None and b is not None else None
starts = sorted({r[1] for r in rows})
O_ = O
def fin_off(st):
    o = O_.get(f"BTC:{st}") or {}
    return o.get("final") or (O_.get(f"BTC:{st + 300}") or {}).get("ptb")
NUIT0 = 1791581760          # 10.10 00:16 heure suisse
valides = [st for st in starts if (O_.get(f"BTC:{st}") or {}).get("gagnant") and fin_off(st)]
avant_nuit = [st for st in valides if st < NUIT0]
CUT = avant_nuit[int(len(avant_nuit) * 0.6)]
per = lambda st: "apprentissage" if st < CUT else ("validation" if st < NUIT0 else "nuit 10.10")
out = [f"# Tournoi des prévisions Chainlink — BTC, {len(valides)} cycles ({hs(valides[0])} → {hs(valides[-1] + 300)})", "",
       f"Apprentissage : cycles avant le {hs(CUT)} ; validation : {hs(CUT)} → {hs(NUIT0)} ; nuit du 10.10 à part. Tout est calculé avec les données reçues avant l'instant de décision.", ""]
# ---------------- Q1 transmission
out += ["## Q1. Quelle part de l'écart exchange − Chainlink Chainlink rattrape-t-il, et en combien de temps ?", "",
        "Écart = prix de l'exchange ramené au niveau Chainlink (médiane de l'écart sur 120 s) − dernier Chainlink. Pente = variation de Chainlink / écart (régression robuste par l'origine, écarts ≥ 2 $). 1,00 = tout est transmis.", "",
        "| Source | Mesures | 0,5 s | 1 s | 2 s | 5 s | 10 s |", "|---|---|---|---|---|---|---|"]
HZ = (0.5, 1, 2, 5, 10)
TQ = collections.defaultdict(lambda: collections.defaultdict(list))
for st in valides:
    for s in range(st, st + 300, 2):
        t = s + 0.5; c0 = der("cl", t)
        if c0 is None: continue
        L = {x: lev(x, t) for x in EXCH}; g = {x: (L[x] - c0) for x in EXCH if L[x] is not None}
        if not g: continue
        dc = {h: (der("cl", t + h) - c0) if der("cl", t + h) is not None else None for h in HZ}
        cons = float(np.median(list(g.values()))); nconf = sum(1 for v in g.values() if abs(v) >= 2 and np.sign(v) == np.sign(cons))
        vs = vol(s) or 0; reg = "calme (< 2 $/s)" if vs < 2 else "agité (≥ 2 $/s)"
        for k, gv in list(g.items()) + [("consensus des 4", cons)]:
            if abs(gv) < 2: continue
            for h in HZ:
                if dc[h] is not None: TQ[k][h].append((gv, dc[h]))
        if abs(cons) >= 2:
            for h in HZ:
                if dc[h] is not None:
                    TQ[f"consensus, {nconf} exchange(s) d'accord"][h].append((cons, dc[h])); TQ[f"consensus, régime {reg}"][h].append((cons, dc[h]))
def pente(P):
    if len(P) < 30: return None
    a = np.array(P); g, d = a[:, 0], a[:, 1]; w = 1 / np.maximum(1, np.abs(g))          # robuste : poids décroissants pour les grands écarts
    return float(np.sum(w * g * d) / np.sum(w * g * g))
NOMX = {"perp": "Bybit perp", "okx": "OKX", "bn": "Binance", "cb": "Coinbase"}
for k in list(EXCH) + ["consensus des 4"] + sorted(k for k in TQ if k.startswith("consensus,")):
    if k not in TQ: continue
    vals = [pente(TQ[k][h]) for h in HZ]
    out.append(f"| {NOMX.get(k, k)} | {len(TQ[k][1])} | " + " | ".join(f"{v:.2f}" if v is not None else "—" for v in vals) + " |")
# ---------------- Q17 persistance des sauts
out += ["", "## Q17. Les sauts d'une seconde du perp Bybit : que reste-t-il après 2, 5, 10 s, et combien passe dans Chainlink ?", "",
        "Saut = mouvement du perp en 1 s ≥ 4 fois sa volatilité par seconde et ≥ 3 $. Confirmé = OKX ou Binance bougent dans le même sens d'au moins la moitié dans la même seconde.", "",
        "| Type de saut | Sauts | Reste sur le perp à 2 s | à 5 s | à 10 s | Passé dans Chainlink à 2 s | à 5 s | à 10 s |", "|---|---|---|---|---|---|---|---|"]
SJ = collections.defaultdict(list)
for st in valides:
    for s in range(st - 60, st + 300):
        t = s + 0.999; p1, p0 = der("perp", t), der("perp", t - 1); sg = vol(s)
        if p1 is None or p0 is None or not sg: continue
        J = p1 - p0
        if abs(J) < max(3, 4 * sg): continue
        conf = any((der(x, t) or 0) and (der(x, t - 1) or 0) and np.sign(der(x, t) - der(x, t - 1)) == np.sign(J) and abs(der(x, t) - der(x, t - 1)) >= abs(J) / 2 for x in ("okx", "bn"))
        c0 = der("cl", t - 1)
        r = [((der("perp", t + h) or p1) - p0) / J for h in (2, 5, 10)] + [((der("cl", t + h) or c0) - c0) / J if c0 else np.nan for h in (2, 5, 10)]
        SJ["confirmé" if conf else "isolé (Bybit seul)"].append(r); SJ["tous"].append(r)
        SJ[("confirmé" if conf else "isolé") + (", nuit 10.10" if st >= NUIT0 else ", 07-09.10")].append(r)
for k in sorted(SJ):
    a = np.array(SJ[k], float)
    out.append(f"| {k} | {len(a)} | " + " | ".join(f"{100 * np.nanmedian(np.clip(a[:, i], -1, 2)):.0f} %" for i in range(6)) + " |")
# ---------------- tournoi : construction des mesures
def mesures():
    M = []
    for st in valides:
        end = st + 300; deb = end - 60; K, n0 = tw(st - 60, st)
        if K is None or n0 < 40: continue
        y = (O_.get(f"BTC:{st}") or {}).get("gagnant") == "Up"; F = fin_off(st)
        for r in C2[st]:
            t = r[0]; tl = end - t
            if tl > 90 or tl < 20: continue
            s = int(t); sg = vol(s)
            Lp = lev("perp", t); c0 = der("cl", t)
            if not sg or Lp is None or c0 is None: continue
            Lp2 = lev("perp", t - 2); Lp1 = lev("perp", t - 1)
            levs = {x: lev(x, t) for x in EXCH}; cons = float(np.median([v for v in levs.values() if v is not None]))
            mv2 = (Lp - Lp2) if Lp2 is not None else 0.0
            conf2 = any(levs[x] is not None and lev(x, t - 2) is not None and np.sign(levs[x] - lev(x, t - 2)) == np.sign(mv2) and abs(levs[x] - lev(x, t - 2)) >= abs(mv2) / 2 for x in ("okx", "bn", "cb"))
            saut = abs(mv2) >= max(3, 4 * sg * math.sqrt(2))
            if s >= deb:
                con = [sec("cl", j) for j in range(deb, s)]; con = [x for x in con if x is not None]; rem = 60 - len(con); kn = sum(con)
                v = sg ** 2 * rem ** 3 / 3 / 3600
            else: rem = 60; kn = 0.0; v = sg ** 2 * ((deb - s) + 20)
            sd = math.sqrt(v + 0.25)
            M.append(dict(st=st, t=t, tl=tl, K=K, y=y, F=F, kn=kn, rem=rem, sd=sd, Lp=Lp, Lpre=(Lp2 if saut and Lp2 is not None else Lp), saut=saut, conf=conf2, cl=c0, cons=cons, sg=sg,
                          ua=r[4], da=r[6], uz=r[8] or 0, dz=r[10] or 0, mid=((r[3] + r[4]) / 2) if r[3] is not None and r[4] is not None else None))
    return M
C2 = collections.defaultdict(list)
for r in rows: C2[r[1]].append(r)
M = mesures()
E_ = lambda m, S: (m["kn"] + m["rem"] * S) / 60
# apprentissage des coefficients : C (part du saut conservée) et D (part de l'écart consensus − Chainlink conservée)
TRN = [m for m in M if m["st"] < CUT]
num = den = 0.0
for m in TRN:
    if not m["saut"]: continue
    w = m["rem"] / 60 * (m["Lp"] - m["Lpre"]); e0 = m["F"] - E_(m, m["Lpre"]); num += e0 * w; den += w * w
PHI = num / den if den else 1.0
PH2 = {}
for cf in (True, False):
    num = den = 0.0
    for m in TRN:
        if not m["saut"] or m["conf"] != cf: continue
        w = m["rem"] / 60 * (m["Lp"] - m["Lpre"]); e0 = m["F"] - E_(m, m["Lpre"]); num += e0 * w; den += w * w
    PH2[cf] = num / den if den else 1.0
num = den = 0.0
for m in TRN:
    w = m["rem"] / 60 * (m["cons"] - m["cl"]); e0 = m["F"] - E_(m, m["cl"]); num += e0 * w; den += w * w
BETA = num / den if den else 1.0
MOD = {"A — actuel (dernier prix Bybit prolongé)": lambda m: m["Lp"],
       "B — anti-saut (saut accepté si confirmé ou après 2 s)": lambda m: m["Lpre"] if (m["saut"] and not m["conf"]) else m["Lp"],
       f"C — persistance du saut (garde {PHI:.2f} du saut)": lambda m: m["Lpre"] + PHI * (m["Lp"] - m["Lpre"]),
       f"C2 — persistance selon confirmation (isolé {PH2[False]:.2f}, confirmé {PH2[True]:.2f})": lambda m: m["Lpre"] + PH2[m["conf"]] * (m["Lp"] - m["Lpre"]) if m["saut"] else m["Lp"],
       f"D — prévision Chainlink (dernier Chainlink + {BETA:.2f} × écart consensus)": lambda m: m["cl"] + BETA * (m["cons"] - m["cl"])}
out += ["", "## Tournoi des quatre modèles", "",
        f"Coefficients appris sur l'apprentissage seulement : C garde **{PHI:.2f}** d'un saut récent ; D prolonge le dernier Chainlink plus **{BETA:.2f}** fois l'écart entre le consensus des 4 exchanges et Chainlink. "
        "Même incertitude (même écart-type) pour les 4 modèles : seule la moyenne prévue change.", ""]
R = collections.defaultdict(lambda: collections.defaultdict(list)); SIGN = collections.defaultdict(lambda: collections.defaultdict(dict))
for m in M:
    for nom, f in MOD.items():
        S = f(m); E = E_(m, S); p = phi((E - m["K"]) / m["sd"])
        for g in (per(m["st"]), "régime calme" if m["sg"] < 2 else "régime agité"):
            R[g][nom].append((E, p, m["F"], m["y"], m["t"]))
        d = SIGN[nom]
        if m["st"] not in d:
            for up in (True, False):
                a = m["ua"] if up else m["da"]; z = m["uz"] if up else m["dz"]
                if a is None or not (0.02 <= a <= 0.98) or z <= 0: continue
                if (p if up else 1 - p) - a >= 0.20:
                    gm = m["y"] if up else not m["y"]; q = min(50 / a, z); d[m["st"]] = (q * ((1 if gm else 0) - a - FEE(a)), q * a, gm, a); break
for g in ("apprentissage", "validation", "nuit 10.10", "régime calme", "régime agité"):
    out += [f"### {g}", "", "| Modèle | Mesures | Erreur moyenne finale (RMSE, $) | Brier | Proba > 95 % fausse | Proba > 99 % fausse |", "|---|---|---|---|---|---|"]
    for nom in MOD:
        A = np.array(R[g][nom], float)
        if not len(A): continue
        _, idx = np.unique(np.floor(A[:, 4]), return_index=True); A = A[idx]          # une mesure par seconde
        e = A[:, 2] - A[:, 0]; pr_ = A[:, 1]; y = A[:, 3]
        conf95 = np.maximum(pr_, 1 - pr_) > 0.95; faux95 = conf95 & ((pr_ > 0.5) != (y > 0.5))
        conf99 = np.maximum(pr_, 1 - pr_) > 0.99; faux99 = conf99 & ((pr_ > 0.5) != (y > 0.5))
        out.append(f"| {nom} | {len(A)} | {np.sqrt(np.mean(e ** 2)):.2f} | {np.mean((pr_ - y) ** 2):.4f} | {faux95.sum()} / {conf95.sum()} ({100 * faux95.sum() / max(1, conf95.sum()):.1f} %) | {faux99.sum()} / {conf99.sum()} ({100 * faux99.sum() / max(1, conf99.sum()):.1f} %) |")
    out.append("")
out += ["### Rejeu TWAP fin avec chaque modèle (premier signal du cycle, avantage ≥ 0,20, 90-20 s, 50 $ max limité à la quantité affichée, frais compris)", "",
        "| Modèle | Période | Achats | Gagnés | Résultat | Par $ | Creux | Pertes de suite | Jackpots (≥ 4× la mise) |", "|---|---|---|---|---|---|---|---|---|"]
for nom in MOD:
    for g in ("apprentissage", "validation", "nuit 10.10"):
        L = [v for st, v in sorted(SIGN[nom].items()) if per(st) == g]
        if not L: continue
        pn = [l[0] for l in L]; cum = pk = cr = 0.0; s_ = smax = 0
        for l in L: cum += l[0]; pk = max(pk, cum); cr = min(cr, cum - pk); s_ = 0 if l[2] else s_ + 1; smax = max(smax, s_)
        jk = [l for l in L if l[0] >= 4 * l[1]]
        out.append(f"| {nom} | {g} | {len(L)} | {100 * sum(l[2] for l in L) / len(L):.0f} % | **{f0(sum(pn))}** | {100 * sum(pn) / max(1, sum(l[1] for l in L)):+.0f} % | {f0(cr)} | {smax} | {len(jk)} ({f0(sum(l[0] for l in jk))}) |")
# ---------------- Q18 basculements extremes (modele A)
out += ["", "## Q18. Basculements extrêmes de la probabilité (modèle actuel), entre 90 et 20 s", "",
        "| Basculement en 1 s | Événements | Déclenché surtout par Bybit | Chainlink a bougé dans le même sens | Revenu à moins de la moitié 5 s après | Le nouveau côté a gagné | Dont régime calme : gagné |", "|---|---|---|---|---|---|---|"]
EV = collections.defaultdict(list)
byst = collections.defaultdict(list)
for m in M: byst[m["st"]].append(m)
for st, L in byst.items():
    L.sort(key=lambda m: m["t"]); P = [(m["t"], phi((E_(m, m["Lp"]) - m["K"]) / m["sd"]), m) for m in L]; vu = set()
    for i, (t, p, m) in enumerate(P):
        j0 = next((j for j in range(i, -1, -1) if t - P[j][0] >= 1), None)
        if j0 is None: continue
        dp = p - P[j0][1]; k5 = next((k for k in range(i, len(P)) if P[k][0] - t >= 5), None)
        for seuil, lab in ((0.70, "> 70 points"), (0.40, "> 40 points"), (0.20, "> 20 points")):
            if abs(dp) >= seuil and (lab, int(t) // 3) not in vu:
                vu.add((lab, int(t) // 3))
                mv = {x: (lev(x, t) or 0) - (lev(x, t - 1) or 0) for x in EXCH}; trig = max(mv, key=lambda x: abs(mv[x]))
                dcl = (der("cl", t) or 0) - (der("cl", t - 1) or 0)
                rev = k5 is not None and abs(P[k5][1] - P[j0][1]) < abs(dp) / 2
                nouveau_up = dp > 0; gagne = m["y"] == nouveau_up
                EV[lab].append((trig == "perp", np.sign(dcl) == np.sign(dp) and abs(dcl) > 0.5, rev, gagne, m["sg"] < 2))
                if P[j0][1] < 0.05 and p > 0.95 or P[j0][1] > 0.95 and p < 0.05: EV["de < 5 % à > 95 % (ou inverse)"].append((trig == "perp", np.sign(dcl) == np.sign(dp) and abs(dcl) > 0.5, rev, gagne, m["sg"] < 2))
                break
for lab in ("> 20 points", "> 40 points", "> 70 points", "de < 5 % à > 95 % (ou inverse)"):
    a = EV[lab]
    if not a: continue
    A = np.array(a, float); cal = A[A[:, 4] == 1]
    out.append(f"| {lab} | {len(A)} | {100 * A[:, 0].mean():.0f} % | {100 * A[:, 1].mean():.0f} % | {100 * A[:, 2].mean():.0f} % | {100 * A[:, 3].mean():.0f} % | {100 * cal[:, 3].mean() if len(cal) else float('nan'):.0f} % ({len(cal)}) |")
open("etude/bot5min/resultat_oracle_tournoi.md", "w").write("\n".join(out)); print("\n".join(out))
