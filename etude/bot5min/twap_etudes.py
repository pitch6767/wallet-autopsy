"""Études TWAP fin (10.10.2026, « fait tout ») — BTC, carnets enregistrés 4 fois par seconde, règlement reconstruit exactement.
A  durée de vie de l'avantage (0,25 / 0,5 / 1 / 2 / 5 s après le signal) ; B  partie nouvelle de l'écart spot-perp ; C  quel modèle déclenche en premier ;
D  changements de favori ; E  prochain prix Chainlink. Tout est calculé avec ce qui était connu à l'instant (prix reçus avant l'instant)."""
import json, gzip, glob, math, bisect, time, statistics as stt, collections, sys
import numpy as np
sys.path.insert(0, "etude/bot5min")
from sauvetage import FEE
phi = lambda x: 0.5 * (1 + math.erf(x / math.sqrt(2)))
def t4(x):
    u = x * math.sqrt(2); q = u * u / 4
    return 0.5 + 0.375 * (u / math.sqrt(1 + q)) * (1 - q / (3 * (1 + q)))
f0 = lambda x: (f"+{x:,.0f} $" if x >= 0 else f"−{-x:,.0f} $").replace(",", "'")
hs = lambda t: time.strftime("%d.%m %H:%M", time.gmtime(t + 7200))
O = json.load(open("bot95/officiels.json"))
rows = {}
for f in sorted(glob.glob("bot95/donnees/*/rec_BTC.json.gz")):
    for doc in json.load(gzip.open(f, "rt")).values():
        for r in doc["lignes"]: rows[r[0]] = r
rows = sorted(rows.values(), key=lambda r: r[0])
SER = {}
for nom, i in (("cl", 15), ("perp", 11), ("okx", 12), ("cb", 13), ("bn", 14)):
    SER[nom] = ([r[0] for r in rows if r[i]], [r[i] for r in rows if r[i]])
def der(nom, t, age=10):
    T, V = SER[nom]; k = bisect.bisect_right(T, t) - 1
    return V[k] if k >= 0 and t - T[k] < age else None
CLT, CLV = SER["cl"]
SEC = {}
def sec(nom, s):
    k = (nom, s)
    if k not in SEC: SEC[k] = der(nom, s + 0.999)
    return SEC[k]
def tw(a, b):
    v = [sec("cl", s) for s in range(a, b)]; v = [x for x in v if x is not None]
    return (sum(v) / len(v), len(v)) if v else (None, 0)
BC = {}
def base(nom, s):
    k = (nom, s // 5)
    if k not in BC:
        d = [sec(nom, x) - sec("cl", x) for x in range(s - 120, s) if sec(nom, x) and sec("cl", x)]
        BC[k] = float(np.median(d)) if len(d) > 30 else None
    return BC[k]
VC = {}
def vol(s):
    if s not in VC:
        x = [sec("perp", j) for j in range(s - 300, s)]; x = [y for y in x if y]
        VC[s] = float(np.std(np.diff(x))) if len(x) > 100 else None
    return VC[s]
C = collections.defaultdict(list)
for r in rows: C[r[1]].append(r)
CY = {}
for st in sorted(C):
    o = O.get(f"BTC:{st}") or {}; g = o.get("gagnant"); fin_off = (O.get(f"BTC:{st + 300}") or {}).get("ptb")
    K, n0 = tw(st - 60, st)
    if not g or K is None or n0 < 40 or not fin_off: continue
    end = st + 300; deb = end - 60; L = []
    for r in C[st]:
        t = r[0]; tl = end - t
        if tl > 95 or tl < 1: continue
        s = int(t); sg = vol(s); bp = base("perp", s); p = der("perp", t)
        if not sg or bp is None or not p: continue
        S0 = p - bp
        bnp, bb = der("bn", t), base("bn", s); cbp, cb_ = der("cb", t), base("cb", s)
        Sbn = bnp - bb if bnp and bb is not None else S0; Scb = cbp - cb_ if cbp and cb_ is not None else S0
        k2 = bisect.bisect_right(CLT, t) - 1; con = []
        if s >= deb:
            con = [sec("cl", j) for j in range(deb, s)]; con = [x for x in con if x is not None]
            rem = 60 - len(con); E = (sum(con) + rem * S0) / 60; v = sg ** 2 * rem ** 3 / 3 / 3600; remf = rem / 60
        else: rem = 60; E = S0; v = sg ** 2 * ((deb - s) + 20); remf = 1.0
        sd = math.sqrt(v + 0.25); z = (E - K) / sd
        dlt = (0.40 * (Sbn - S0) + 0.16 * (Scb - S0)) * remf
        ub, ua, db, da = r[3], r[4], r[5], r[6]
        L.append(dict(t=t, tl=tl, p0=phi(z), pT=t4(z), pS=phi(z + dlt / sd), z=z, sd=sd, E=E, K=K, remf=remf, sp=Sbn - S0, spc=Scb - S0,
                      cl_t=CLT[k2] if k2 >= 0 else None, cl_v=CLV[k2] if k2 >= 0 else None, S0=S0,
                      ua=ua, da=da, ub=ub, db=db, uz=r[8] or 0, dz=r[10] or 0,
                      mid=((ub + ua) / 2) if ub is not None and ua is not None else ((1 - (db + da) / 2) if db is not None and da is not None else None)))
    if L: CY[st] = dict(L=L, up=g == "Up", fin=fin_off, K=K)
cyc = sorted(CY)
rap = [f"# TWAP fin — études A à E (BTC, {len(cyc)} cycles, {hs(cyc[0])} → {hs(cyc[-1] + 300)})", "",
       "Carnet enregistré 4 fois par seconde ; règlement reconstruit exactement ; probabilités calculées avec seulement ce qui était reçu à l'instant. "
       "Achats simulés au meilleur vendeur, limités à la quantité affichée, frais compris.", ""]
ask = lambda x, up: x["ua"] if up else x["da"]
sz = lambda x, up: x["uz"] if up else x["dz"]
pr = lambda x, k, up: x[k] if up else 1 - x[k]
def pnl(x, up, gm, prix=None):
    a = prix if prix is not None else ask(x, up); z = sz(x, up)
    if a is None or z <= 0 or not (0.02 <= a <= 0.98): return None
    parts = min(50 / a, z); return parts * ((1 if gm else 0) - a - FEE(a)), parts * a
def signal(st, k, seuil=0.20):
    c = CY[st]
    for i, x in enumerate(c["L"]):
        if not (20 <= x["tl"] <= 90): continue
        for up in (True, False):
            a = ask(x, up)
            if a is None or not (0.02 <= a <= 0.98) or sz(x, up) <= 0: continue
            if pr(x, k, up) - a >= seuil: return i, up
    return None
def stats(L):
    if not L: return "0 | | | | | |"
    pn = [l[0] for l in L]; cum = pk = cr = 0.0; s = sm = 0
    for l in L: cum += l[0]; pk = max(pk, cum); cr = min(cr, cum - pk); s = 0 if l[2] else s + 1; sm = max(sm, s)
    return f"{len(L)} | {100 * sum(l[2] for l in L) / len(L):.0f} % | **{f0(sum(pn))}** | {100 * sum(pn) / max(1, sum(l[1] for l in L)):+.0f} % | {f0(cr)} | {sm}"
HH = "| Groupe | Achats | Gagnés | Résultat | Par $ | Creux | Pertes de suite max |\n|---|---|---|---|---|---|---|"
# ---------- A. duree de vie de l'avantage
SIG = {}
for st in cyc:
    s0 = signal(st, "p0")
    if s0: SIG[st] = s0
rap += ["## A. Combien de temps l'avantage reste achetable après le signal (moteur actuel, premier signal de chaque cycle)", "",
        f"{len(SIG)} signaux.", "", "| Délai d'achat | Encore achetable | Avantage moyen restant | Avantage ≥ 0,20 encore | ≥ 0,10 encore | Prix moyen | Quantité moyenne affichée | Résultat si on achète à ce moment |", "|---|---|---|---|---|---|---|---|"]
for dl in (0, 0.25, 0.5, 1, 2, 5):
    res, edges, prix, qte = [], [], [], []; n20 = n10 = ok = 0
    for st, (i, up) in SIG.items():
        L = CY[st]["L"]; t0 = L[i]["t"] + dl
        j = next((j for j in range(i, len(L)) if L[j]["t"] >= t0 - 1e-6), None)
        if j is None: continue
        x = L[j]; a = ask(x, up)
        if a is None or sz(x, up) <= 0: continue
        ok += 1; e = pr(x, "p0", up) - a; edges.append(e); prix.append(a); qte.append(sz(x, up))
        n20 += e >= 0.20; n10 += e >= 0.10
        gm = CY[st]["up"] if up else not CY[st]["up"]; pp = pnl(x, up, gm)
        if pp: res.append(pp[0])
    rap.append(f"| {dl} s | {ok} / {len(SIG)} | {stt.mean(edges):+.3f} | {n20} | {n10} | {stt.mean(prix):.3f} | {stt.median(qte):.0f} jetons | {f0(sum(res))} |")
rap += ["", "Lecture : si l'avantage disparaît en moins d'une seconde, seule une exécution très rapide en profitera.", ""]
# ---------- B. ecart spot-perp : partie nouvelle
X = []
for st in cyc:
    c = CY[st]; L = c["L"]
    for i, x in enumerate(L):
        if not (20 <= x["tl"] <= 90) or i % 4: continue
        j5 = next((j for j in range(i, -1, -1) if x["t"] - L[j]["t"] >= 5), None)
        j60 = [L[j]["sp"] for j in range(max(0, i - 240), i)]
        if j5 is None or len(j60) < 40: continue
        med, sdv = float(np.median(j60)), float(np.std(j60)) or 1.0
        dur = 0
        for j in range(i, -1, -1):
            if (L[j]["sp"] > 0) != (x["sp"] > 0): break
            dur = x["t"] - L[j]["t"]
        X.append(dict(st=st, err=(c["fin"] - x["E"]), errz=(c["fin"] - x["E"]) / x["sd"], sp=x["sp"] * x["remf"], spc=x["spc"] * x["remf"],
                      lag=L[j5]["sp"] * x["remf"], mom=(x["S0"] - L[j5]["S0"]), shock=(x["sp"] - med) / sdv * x["remf"], dur=dur, remf=x["remf"], raw=x["sp"]))
cutB = cyc[int(len(cyc) * 0.6)]
TR = [x for x in X if x["st"] < cutB]; TE = [x for x in X if x["st"] >= cutB]
A_ = lambda S, ks: np.array([[x[k] for k in ks] + [1.0] for x in S])
co, *_ = np.linalg.lstsq(A_(TR, ["lag", "mom"]), np.array([x["sp"] for x in TR]), rcond=None)
for x in X: x["innov"] = x["sp"] - float(np.dot(co, [x["lag"], x["mom"], 1.0]))
def cor(S, k): a = np.array([[x[k], x["err"]] for x in S]); return float(np.corrcoef(a[:, 0], a[:, 1])[0, 1])
rap += ["## B. L'écart Binance − perp : quelle partie annonce vraiment l'erreur de la moyenne finale ?", "",
        f"{len(X)} mesures (une par seconde, 90-20 s avant la fin). Corrélation avec l'erreur réelle de la moyenne finale (officiel − prévu), apprentissage avant le {hs(cutB)}, test après.", "",
        "| Mesure | Corrélation (apprentissage) | Corrélation (test, jamais vu) |", "|---|---|---|"]
for k, lab in (("sp", "écart Binance − perp (niveau)"), ("spc", "écart Coinbase − perp"), ("innov", "partie NOUVELLE de l'écart (non expliquée par l'écart d'il y a 5 s et le mouvement)"),
               ("shock", "saut de l'écart par rapport à sa médiane de la minute"), ("lag", "écart d'il y a 5 s")):
    rap.append(f"| {lab} | {cor(TR, k):+.3f} | {cor(TE, k):+.3f} |")
rap += ["", "| Taille de l'écart (sans le prorata) | Mesures | Pente $ d'erreur par $ d'écart (test) |", "|---|---|---|"]
for a, b in ((0, 2), (2, 10), (10, 30), (30, 1e9)):
    S = [x for x in TE if a <= abs(x["raw"]) < b]
    if len(S) > 50:
        m = np.polyfit([x["sp"] for x in S], [x["err"] for x in S], 1)[0]; rap.append(f"| {a:.0f}-{b:.0f} $ | {len(S)} | {m:+.2f} |".replace("-1000000000 $", " $ et plus"))
for lab, f in (("écart qui dure > 5 s", lambda x: x["dur"] > 5), ("écart récent (≤ 5 s)", lambda x: x["dur"] <= 5)):
    S = [x for x in TE if f(x)]
    if len(S) > 50: rap.append(f"| {lab} | {len(S)} | {np.polyfit([x['sp'] for x in S], [x['err'] for x in S], 1)[0]:+.2f} |")
sgn = np.array([np.sign(x["sp"]) == np.sign(x["err"]) for x in TE if abs(x["sp"]) > 0.5])
rap += ["", f"Idée 30 — le **sens** de l'écart annonce le sens de l'erreur dans **{100 * sgn.mean():.1f} %** des cas (test, écart > 0,5 $) ; 50 % = hasard.", ""]
# ---------- C. trois modeles
rap += ["## C. Les trois modèles TWAP fin sur les mêmes cycles (rejeu, un achat par cycle)", ""]
SM = {k: {st: signal(st, k) for st in cyc} for k in ("p0", "pT", "pS")}
NOM = {"p0": "original", "pT": "sauts", "pS": "correction spot-perp"}
groupes = collections.defaultdict(list)
for st in cyc:
    a = {k: SM[k][st] for k in SM if SM[k][st]}
    cotes = {v[1] for v in a.values()}
    if not a: cle = "aucun"
    elif len(cotes) > 1: cle = "côtés opposés"
    elif len(a) == 3: cle = "les trois"
    elif len(a) == 2: cle = "deux : " + " + ".join(NOM[k] for k in a)
    else: cle = "seul : " + NOM[list(a)[0]]
    groupes[cle].append(st)
rap += ["| Groupe de cycles | Cycles | Résultat original | Résultat sauts | Résultat correction |", "|---|---|---|---|---|"]
def res_m(k, sts):
    t = 0.0; n = 0
    for st in sts:
        s0 = SM[k][st]
        if not s0: continue
        i, up = s0; x = CY[st]["L"][i]; gm = CY[st]["up"] if up else not CY[st]["up"]; pp = pnl(x, up, gm)
        if pp: t += pp[0]; n += 1
    return f"{f0(t)} ({n})" if n else "—"
for cle in sorted(groupes, key=lambda c: -len(groupes[c])):
    if cle == "aucun": rap.append(f"| aucun achat | {len(groupes[cle])} | — | — | — |"); continue
    rap.append(f"| {cle} | {len(groupes[cle])} | {res_m('p0', groupes[cle])} | {res_m('pT', groupes[cle])} | {res_m('pS', groupes[cle])} |")
tot = {k: [] for k in SM}
for k in SM:
    for st in cyc:
        s0 = SM[k][st]
        if not s0: continue
        i, up = s0; x = CY[st]["L"][i]; gm = CY[st]["up"] if up else not CY[st]["up"]; pp = pnl(x, up, gm)
        if pp: tot[k].append((pp[0], pp[1], gm))
rap += ["", HH.replace("Groupe", "Modèle")] + [f"| {NOM[k]} | {stats(tot[k])} |" for k in SM]
# qui declenche en premier
lead = collections.Counter(); delais = collections.defaultdict(list); first_res = []; cout2 = []
for st in cyc:
    a = {k: SM[k][st] for k in SM if SM[k][st]}
    if len(a) < 2 or len({v[1] for v in a.values()}) > 1: continue
    ts_ = {k: CY[st]["L"][v[0]]["t"] for k, v in a.items()}
    k1 = min(ts_, key=ts_.get); lead[NOM[k1]] += 1
    for k, t_ in ts_.items():
        if k != k1: delais[NOM[k1] + " avant " + NOM[k]].append(t_ - ts_[k1])
    i1, up = a[k1]; ordre = sorted(ts_.values())
    if len(ordre) >= 2:
        x1 = CY[st]["L"][i1]; x2 = next(x for x in CY[st]["L"] if x["t"] >= ordre[1])
        if ask(x1, up) is not None and ask(x2, up) is not None: cout2.append(ask(x2, up) - ask(x1, up))
rap += ["", "Quand au moins deux modèles achètent le même côté, celui qui déclenche en premier : " + ", ".join(f"{k} {v} fois" for k, v in lead.most_common()) + "."]
for k, v in delais.items():
    if v: rap.append(f"- {k} : {stt.median(v):.1f} s d'avance en médiane ({len(v)} cycles)")
if cout2: rap.append(f"- Attendre la 2e confirmation coûte en médiane {100 * stt.median(cout2):+.1f} c (moyenne {100 * stt.mean(cout2):+.1f} c) sur {len(cout2)} cycles.")
# ---------- D. changements de favori
rap += ["", "## D. Changements de favori (moteur actuel) : qui bascule en premier, notre modèle ou le carnet ?", "", HH]
grp = collections.defaultdict(list)
for st, (i, up) in SIG.items():
    L = CY[st]["L"]; x = L[i]
    t1 = next((L[j]["t"] for j in range(i, 0, -1) if (L[j]["p0"] - 0.5) * (L[j - 1]["p0"] - 0.5) < 0), None)
    t2 = next((L[j]["t"] for j in range(i, 0, -1) if L[j]["mid"] is not None and L[j - 1]["mid"] is not None and (L[j]["mid"] - 0.5) * (L[j - 1]["mid"] - 0.5) < 0), None)
    gm = CY[st]["up"] if up else not CY[st]["up"]; pp = pnl(x, up, gm)
    if not pp: continue
    item = (pp[0], pp[1], gm)
    age = x["t"] - t1 if t1 else None
    grp["pas de changement de favori dans le cycle" if t1 is None else ("changement il y a < 3 s" if age < 3 else "il y a 3-10 s" if age < 10 else "il y a 10-30 s" if age < 30 else "il y a > 30 s")].append(item)
    if t1 and t2: grp["notre modèle a basculé AVANT le carnet" if t1 < t2 else "le carnet a basculé avant notre modèle"].append(item)
    elif t1 and not t2: grp["notre modèle a basculé, le carnet jamais"].append(item)
    nfl = sum(1 for j in range(max(1, i - 120), i) if (L[j]["p0"] - 0.5) * (L[j - 1]["p0"] - 0.5) < 0)
    grp["≥ 3 bascules en 30 s (oscillations)" if nfl >= 3 else "0-2 bascules en 30 s"].append(item)
for k in ("pas de changement de favori dans le cycle", "changement il y a < 3 s", "il y a 3-10 s", "il y a 10-30 s", "il y a > 30 s", "notre modèle a basculé AVANT le carnet",
          "le carnet a basculé avant notre modèle", "notre modèle a basculé, le carnet jamais", "≥ 3 bascules en 30 s (oscillations)", "0-2 bascules en 30 s"):
    if grp.get(k): rap.append(f"| {k} | {stats(grp[k])} |")
# ---------- E. prochain prix Chainlink
rap += ["", "## E. Le prochain prix Chainlink après le signal confirme-t-il notre avantage ?", "", HH]
grpE = collections.defaultdict(list); attente = []
for st, (i, up) in SIG.items():
    L = CY[st]["L"]; x = L[i]; gm = CY[st]["up"] if up else not CY[st]["up"]
    j = next((j for j in range(i + 1, len(L)) if L[j]["cl_t"] and x["cl_t"] and L[j]["cl_t"] > x["cl_t"] and L[j]["cl_v"] != x["cl_v"]), None)
    pp = pnl(x, up, gm)
    if not pp: continue
    if j is None: grpE["pas de nouveau prix Chainlink avant la fin"].append((pp[0], pp[1], gm)); continue
    y = L[j]; mv = (y["cl_v"] - x["cl_v"]) * (1 if up else -1)
    grpE["le prix Chainlink suivant va dans notre sens" if mv > 0 else "le prix Chainlink suivant va contre nous"].append((pp[0], pp[1], gm))
    if ask(y, up) is not None and pr(y, "p0", up) - ask(y, up) >= 0.20:
        p2 = pnl(y, up, gm)
        if p2: attente.append((p2[0], p2[1], gm))
    grpE["délai jusqu'au prochain prix Chainlink < 2 s" if y["t"] - x["t"] < 2 else "délai ≥ 2 s"].append((pp[0], pp[1], gm))
for k, v in grpE.items(): rap.append(f"| {k} | {stats(v)} |")
rap.append(f"| *politique : attendre le prochain prix Chainlink, acheter si l'avantage est encore ≥ 0,20* | {stats(attente)} |")
open("etude/bot5min/resultat_twap_etudes.md", "w").write("\n".join(rap)); print("\n".join(rap))
