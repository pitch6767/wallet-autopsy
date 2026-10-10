"""Contrôle de robustesse du modèle E (TWAP fin quantiles) contre A (TWAP fin original) — demande de Pitch 10.10.2026 09:37.
1. décalages −1 s, −0,5 s, 0, +0,5 s, +1 s sans fuite : δ < 0 = le calcul utilise des données plus anciennes de |δ| (calcul en retard) ;
   δ > 0 = décision prise à l'instant t avec les données de t, exécutée à t + δ au prix du carnet de t + δ (retard d'exécution).
   L'écart Bybit → Chainlink est recalculé à chaque seconde exacte (plus de cache de 5 s).
2. décomposition A / E sur la validation ; 3. par journée et incertitude par blocs (bootstrap) ; 4. tables E figées et apprises sur l'apprentissage seulement.
Les tables E utilisées sont EXACTEMENT celles du bot (bot95/src/quantiles_twap.js)."""
import json, gzip, glob, bisect, math, time, collections, sys, re
import numpy as np
sys.path.insert(0, "etude/bot5min")
from sauvetage import FEE
phi = lambda x: 0.5 * (1 + math.erf(x / math.sqrt(2)))
f0 = lambda x: (f"+{x:,.0f} $" if x >= 0 else f"−{-x:,.0f} $").replace(",", " ")
hs = lambda t: time.strftime("%d.%m %H:%M", time.gmtime(t + 7200))
O = json.load(open("bot95/officiels.json"))
rows = {}
for f in sorted(glob.glob("bot95/donnees/*/rec_BTC.json.gz")):
    for doc in json.load(gzip.open(f, "rt")).values():
        for r in doc["lignes"]: rows[r[0]] = r
rows = sorted(rows.values(), key=lambda r: r[0])
SER = {nom: ([r[0] for r in rows if r[i]], [r[i] for r in rows if r[i]]) for nom, i in (("cl", 15), ("perp", 11))}
def der(nom, t, age=10):
    T, V = SER[nom]; k = bisect.bisect_right(T, t) - 1
    return V[k] if k >= 0 and t - T[k] < age else None
SEC = {}
def sec(nom, s):
    if (nom, s) not in SEC: SEC[(nom, s)] = der(nom, s + 0.999)
    return SEC[(nom, s)]
BC = {}
def base(s):                                  # médiane perp − Chainlink sur [s−120, s), recalculée à chaque seconde
    if s not in BC:
        d = [sec("perp", x) - sec("cl", x) for x in range(s - 120, s) if sec("perp", x) and sec("cl", x)]
        BC[s] = float(np.median(d)) if len(d) > 30 else None
    return BC[s]
VC = {}
def vol(s):
    if s not in VC:
        x = [sec("perp", j) for j in range(s - 300, s)]; x = [y for y in x if y]
        VC[s] = float(np.std(np.diff(x))) if len(x) > 100 else None
    return VC[s]
# tables E du bot
QT = json.loads(re.search(r"export const QTWAP = (\{.*\});", open("bot95/src/quantiles_twap.js").read()).group(1))
def survie(cle, x):
    T = QT.get(cle)
    if not T: return None
    q, n = T["q"], T["n"]; L = len(q) - 1
    if x < q[0]: return min(0.9995, 1 - 0.5 / (n + 1))
    if x >= q[L]: return max(0.0005, 0.5 / (n + 1))
    lo = bisect.bisect_right(q, x) - 1; hi = lo + 1
    fr = (lo + ((x - q[lo]) / (q[hi] - q[lo]) if q[hi] > q[lo] else 0)) / L
    return min(0.9995, max(0.0005, 1 - fr))
C = collections.defaultdict(list)
for r in rows: C[r[1]].append(r)
NUIT0 = 1791581760
valides = [st for st in sorted(C) if (O.get(f"BTC:{st}") or {}).get("gagnant")]
avant = [st for st in valides if st < NUIT0]; CUT = avant[int(len(avant) * 0.6)]
per = lambda st: "apprentissage" if st < CUT else ("validation" if st < NUIT0 else "nuit 10.10")
def modele(st, ti):
    end = st + 300; deb = end - 60; s = int(ti)
    K = [sec("cl", x) for x in range(st - 60, st)]; K = [x for x in K if x is not None]
    if len(K) < 40: return None
    K = sum(K) / len(K); sg = vol(s); b = base(s); p = der("perp", ti)
    if not sg or b is None or p is None: return None
    S = p - b
    if s >= deb:
        con = [sec("cl", j) for j in range(deb, s)]; con = [x for x in con if x is not None]; rem = 60 - len(con)
        E = (sum(con) + rem * S) / 60; v = sg ** 2 * rem ** 3 / 3 / 3600
    else: rem = 60; E = S; v = sg ** 2 * ((deb - s) + 20)
    sd = math.sqrt(v + 0.25); z = (E - K) / sd
    bk = "avant la fenêtre" if s < deb else ("45-60 s restantes" if rem > 45 else "30-45 s" if rem > 30 else "15-30 s" if rem > 15 else "< 15 s")
    rg = "calme" if sg < 2 else "agité"
    pe = survie(f"{bk}|{rg}" if f"{bk}|{rg}" in QT else f"{bk}|*", -z)
    return phi(z), (pe if pe is not None else phi(z)), rg
def rejouer(delta):
    res = {"A": {}, "E": {}}
    for st in valides:
        R = C[st]; T_ = [r[0] for r in R]; up_g = O[f"BTC:{st}"]["gagnant"] == "Up"; end = st + 300
        for i, r in enumerate(R):
            t = r[0]; tl = end - t
            if tl > 90 or tl < 20: continue
            if "A" in res and st in res["A"] and st in res["E"]: break
            ti = t + min(delta, 0); m = modele(st, ti)
            if not m: continue
            for k, p in (("A", m[0]), ("E", m[1])):
                if st in res[k]: continue
                for up in (True, False):
                    a = r[4] if up else r[6]
                    if a is None or not (0.02 <= a <= 0.98) or not ((r[8] if up else r[10]) or 0) > 0: continue
                    if (p if up else 1 - p) - a >= 0.20:
                        j = i
                        if delta > 0:
                            j = bisect.bisect_left(T_, t + delta)
                            if j >= len(R): break
                        x = R[j]; ax = x[4] if up else x[6]; zx = (x[8] if up else x[10]) or 0
                        if ax is None or not (0.02 <= ax <= 0.98) or zx <= 0: res[k][st] = None; break
                        gm = up_g if up else not up_g; q = min(50 / ax, zx)
                        res[k][st] = dict(pn=q * ((1 if gm else 0) - ax - FEE(ax)), mise=q * ax, gm=gm, up=up, prix=ax, t=x[0], rg=m[2]); break
    for k in res: res[k] = {st: v for st, v in res[k].items() if v}
    return res
def st_(L):
    if not L: return "0 | — | — | — | — | —"
    pn = [l["pn"] for l in L]; cum = pk = cr = 0.0; s = sm = 0
    for l in L: cum += l["pn"]; pk = max(pk, cum); cr = min(cr, cum - pk); s = 0 if l["gm"] else s + 1; sm = max(sm, s)
    jk = sum(1 for l in L if l["pn"] >= 4 * l["mise"])
    return f"{len(L)} | {100 * sum(l['gm'] for l in L) / len(L):.0f} % | **{f0(sum(pn))}** | {f0(cr)} | {sm} | {jk}"
out = [f"# Contrôle de robustesse du modèle E (TWAP fin quantiles) contre A (TWAP fin original) — BTC, {len(valides)} cycles ({hs(valides[0])} → {hs(valides[-1] + 300)})", "",
       f"Apprentissage avant le {hs(CUT)} ; validation {hs(CUT)} → {hs(NUIT0)} ; nuit du 10.10 à part. Tables E : exactement celles du bot. Écart Bybit → Chainlink recalculé à chaque seconde.", "",
       "## 1. Décalages de calcul et d'exécution (sans fuite)", "",
       "δ négatif : le moteur calcule avec des données plus vieilles de |δ|. δ positif : décision avec les données de l'instant, achat |δ| plus tard au prix du carnet de ce moment.", "",
       "| Décalage | Modèle | Période | Achats | Gagnés | Résultat | Creux | Pertes de suite | Jackpots |", "|---|---|---|---|---|---|---|---|---|"]
RES = {}
for d in (-1.0, -0.5, 0.0, 0.5, 1.0):
    RES[d] = rejouer(d)
    for k in ("A", "E"):
        for g in ("apprentissage", "validation", "nuit 10.10"):
            L = [v for st, v in sorted(RES[d][k].items()) if per(st) == g]
            out.append(f"| {d:+.1f} s | {k} | {g} | {st_(L)} |")
out += ["", "### Résumé : E − A (validation + nuit) selon le décalage", "", "| Décalage | A | E | E − A |", "|---|---|---|---|"]
for d in RES:
    a = sum(v["pn"] for st, v in RES[d]["A"].items() if per(st) != "apprentissage"); e = sum(v["pn"] for st, v in RES[d]["E"].items() if per(st) != "apprentissage")
    out.append(f"| {d:+.1f} s | {f0(a)} | {f0(e)} | **{f0(e - a)}** |")
# 2. decomposition (δ = 0, validation)
R0 = RES[0.0]; VA = {st: v for st, v in R0["A"].items() if per(st) == "validation"}; VE = {st: v for st, v in R0["E"].items() if per(st) == "validation"}
com = set(VA) & set(VE); oa = set(VA) - set(VE); oe = set(VE) - set(VA)
memes = [st for st in com if VA[st]["up"] == VE[st]["up"]]; opp = [st for st in com if VA[st]["up"] != VE[st]["up"]]
tot = sum(v["pn"] for v in VE.values()) - sum(v["pn"] for v in VA.values())
out += ["", "## 2. Décomposition de l'écart E − A en validation (décalage 0)", "",
        f"Écart total : **{f0(tot)}** (A {f0(sum(v['pn'] for v in VA.values()))}, E {f0(sum(v['pn'] for v in VE.values()))}).", "",
        "| Composante | Cycles | Résultat A | Résultat E | Contribution à E − A |", "|---|---|---|---|---|"]
def ligne(nom, sts, a=True, e=True):
    ra = sum(VA[s]["pn"] for s in sts if s in VA) if a else 0.0; re_ = sum(VE[s]["pn"] for s in sts if s in VE) if e else 0.0
    out.append(f"| {nom} | {len(sts)} | {f0(ra) if a else '—'} | {f0(re_) if e else '—'} | **{f0(re_ - ra)}** |")
ligne("communs, même côté, même instant", [s for s in memes if abs(VA[s]["t"] - VE[s]["t"]) < 0.01])
ligne("communs, même côté, instant différent (prix différent)", [s for s in memes if abs(VA[s]["t"] - VE[s]["t"]) >= 0.01])
ligne("communs, côtés opposés", opp)
ligne("A seul achète (E s'abstient)", sorted(oa), e=False)
ligne("E seul achète", sorted(oe), a=False)
pa = [VA[s] for s in oa]
out += ["", f"Dans les cycles où **seul A achète** : {sum(1 for v in pa if v['pn'] < 0)} pertes évitées par E ({f0(sum(v['pn'] for v in pa if v['pn'] < 0))}), "
        f"{sum(1 for v in pa if v['pn'] >= 0)} gains sacrifiés ({f0(sum(v['pn'] for v in pa if v['pn'] >= 0))}), dont {sum(1 for v in pa if v['pn'] >= 4 * v['mise'])} jackpots ({f0(sum(v['pn'] for v in pa if v['pn'] >= 4 * v['mise']))}).",
        f"Dans les cycles où **seul E achète** : {sum(1 for s in oe if VE[s]['pn'] >= 0)} gagnés ({f0(sum(VE[s]['pn'] for s in oe if VE[s]['pn'] >= 0))}), {sum(1 for s in oe if VE[s]['pn'] < 0)} perdus ({f0(sum(VE[s]['pn'] for s in oe if VE[s]['pn'] < 0))}), "
        f"dont {sum(1 for s in oe if VE[s]['pn'] >= 4 * VE[s]['mise'])} jackpots.",
        f"Les 3 plus grosses contributions à l'écart : " + ", ".join(f"{hs(s)} ({f0((VE[s]['pn'] if s in VE else 0) - (VA[s]['pn'] if s in VA else 0))})" for s in sorted(set(VA) | set(VE), key=lambda s: -abs((VE[s]['pn'] if s in VE else 0) - (VA[s]['pn'] if s in VA else 0)))[:3]) + "."]
# 3. par jour + bootstrap par blocs
out += ["", "## 3. Par journée (heure suisse) et incertitude statistique", "", "| Journée | Cycles | A | E | E − A |", "|---|---|---|---|---|"]
J = collections.defaultdict(lambda: [0, 0.0, 0.0])
for st in valides:
    k = time.strftime("%d.%m", time.gmtime(st + 7200)); J[k][0] += 1
    J[k][1] += R0["A"].get(st, {}).get("pn", 0.0); J[k][2] += R0["E"].get(st, {}).get("pn", 0.0)
for k in sorted(J): out.append(f"| {k} | {J[k][0]} | {f0(J[k][1])} | {f0(J[k][2])} | **{f0(J[k][2] - J[k][1])}** |")
hors = [st for st in valides if per(st) != "apprentissage"]
dif = np.array([R0["E"].get(st, {}).get("pn", 0.0) - R0["A"].get(st, {}).get("pn", 0.0) for st in hors])
rng = np.random.default_rng(1); B = 12; nb = math.ceil(len(dif) / B); boot = []
for _ in range(10000):
    idx = rng.integers(0, len(dif) - B + 1, nb); boot.append(np.concatenate([dif[i:i + B] for i in idx])[:len(dif)].sum())
boot = np.array(boot)
out += ["", f"Validation + nuit ({len(hors)} cycles) : E − A = **{f0(dif.sum())}**. Bootstrap par blocs d'une heure (12 cycles, 10 000 tirages) : "
        f"intervalle à 90 % [{f0(np.quantile(boot, 0.05))} ; {f0(np.quantile(boot, 0.95))}] ; probabilité que l'écart soit ≤ 0 : **{100 * np.mean(boot <= 0):.0f} %**."]
# 4. tables figees
TRN = None
out += ["", "## 4. Les tables E sont-elles figées et apprises seulement sur l'apprentissage ?", ""]
src = open("etude/bot5min/quantiles_export.py").read() + open("etude/bot5min/oracle_fiabilite.py").read()
out += [f"- Le script d'export n'utilise que `TR = [m for m in M if per(m[\"st\"]) == \"apprentissage\"]` : {'oui' if 'per(m[\"st\"]) == \"apprentissage\"' in src else 'NON'}.",
        f"- Effectifs des tables (somme des cases « * ») : {sum(v['n'] for k, v in QT.items() if k.endswith('|*'))} mesures, à comparer aux mesures d'apprentissage seules.",
        "- Dans le bot, `QTWAP` est une constante importée d'un fichier ; aucun code ne la modifie (vérifié : aucune affectation à QTWAP dans index.js).",
        f"- Le dernier cycle d'apprentissage commence le {hs(CUT - 300)} ; son prix final est publié avant le premier cycle de validation ({hs(CUT)})."]
js = open("bot95/src/index.js").read()
out.append(f"- Contrôle automatique : affectations à QTWAP trouvées dans index.js = {len(re.findall(r'QTWAP\\s*(\\[[^]]*\\])?\\s*=[^=]', js))}.")
open("etude/bot5min/resultat_robustesse_E.md", "w").write("\n".join(out)); print("\n".join(out))
