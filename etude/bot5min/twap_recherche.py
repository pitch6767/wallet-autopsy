"""Recherche TWAP fin (10.10.2026, demande « on fait tout ») — BTC, carnets enregistrés.
Base : moteur TWAP (prix à battre = moyenne Chainlink 60 s avant le début ; fin = moyenne des 60 s avant la fin).
Une mesure par seconde entre 90 et 20 s de la fin. Apprentissage sur les cycles ANCIENS, test sur les cycles SUIVANTS (jamais vus).
Probabilités comparées : moteur actuel (perp) ; C nowcast 4 bourses ; sauts (loi de Student) ; distribution empirique des erreurs ;
jumeaux (plus proches voisins) ; B correction apprise (régression logistique sur variables connues à l'instant).
Pour chacune : qualité de prévision (Brier) et règle TWAP fin (probabilité − prix ≥ 0,20, un achat par cycle, quantité affichée)."""
import json, gzip, glob, math, bisect, time, statistics as stt, collections, sys
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import NearestNeighbors
from scipy.stats import t as student
sys.path.insert(0, "etude/bot5min")
from sauvetage import FEE
phi = lambda x: 0.5 * (1 + math.erf(x / math.sqrt(2)))
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
    T = [r[0] for r in rows if r[i]]; V = [r[i] for r in rows if r[i]]; SER[nom] = (T, V)
def der(nom, t, age=10):
    T, V = SER[nom]; k = bisect.bisect_right(T, t) - 1
    return V[k] if k >= 0 and t - T[k] < age else None
def age_cl(t):
    T, _ = SER["cl"]; k = bisect.bisect_right(T, t) - 1
    return t - T[k] if k >= 0 else 99
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
def vol(s, w=300):
    k = (s, w)
    if k not in VC:
        x = [sec("perp", j) for j in range(s - w, s)]; x = [y for y in x if y]
        VC[k] = float(np.std(np.diff(x))) if len(x) > w / 3 else None
    return VC[k]
C = collections.defaultdict(list)
for r in rows: C[r[1]].append(r)
D = []
for st in sorted(C):
    o = O.get(f"BTC:{st}") or {}; g = o.get("gagnant"); fin_off = (O.get(f"BTC:{st + 300}") or {}).get("ptb")
    K, n0 = tw(st - 60, st)
    if not g or K is None or n0 < 40: continue
    end = st + 300; deb = end - 60
    R = C[st]; ts = [r[0] for r in R]; hist = []
    for s in range(end - 90, end - 19):
        k = bisect.bisect_right(ts, s + 0.999) - 1
        if k < 0 or s + 0.999 - R[k][0] > 2: continue
        r = R[k]; t = s + 0.999; tl = end - t
        sg, sg30 = vol(s), vol(s, 30)
        if not sg: continue
        lev = {}
        for nom in ("perp", "okx", "cb", "bn"):
            p, b = sec(nom, s), base(nom, s)
            if p and b is not None: lev[nom] = p - b
        if "perp" not in lev: continue
        con = [sec("cl", j) for j in range(deb, min(s, end))] if s >= deb else []
        con = [x for x in con if x is not None]; rem = 60 - len(con) if s >= deb else 60
        def E_of(S): return (sum(con) + rem * S) / 60 if s >= deb else S
        v = sg ** 2 * (rem ** 3 / 3 / 3600 if s >= deb else ((deb - s) + 20)) + 0.25
        sd = math.sqrt(v)
        S0 = lev["perp"]; Sc = float(np.median(list(lev.values())))
        E0, Ec = E_of(S0), E_of(Sc)
        mom = {w: (S0 - (sec("perp", s - w) - (base("perp", s) or 0))) if sec("perp", s - w) else 0.0 for w in (5, 15, 30)}
        p0 = phi((E0 - K) / sd); hist.append(p0)
        h10 = hist[-10:]
        flips = sum(1 for a2, b2 in zip(h10, h10[1:]) if (a2 - 0.5) * (b2 - 0.5) < 0)
        x30 = [sec("perp", j) for j in range(s - 30, s + 1)]; x30 = [y for y in x30 if y]
        if len(x30) > 10:
            cf = np.polyfit(np.arange(len(x30)), x30, 2); curv, slope = cf[0], cf[1] + 2 * cf[0] * len(x30)
        else: curv = slope = 0.0
        ub, ua, db, da = r[3], r[4], r[5], r[6]
        D.append(dict(st=st, t=t, tl=tl, up=g == "Up", K=K, E0=E0, Ec=Ec, sd=sd, rem=rem, p0=p0, pC=phi((Ec - K) / sd),
                      pT=float(student.cdf((E0 - K) / sd * math.sqrt(4 / 2), 4)), z=(E0 - K) / sd,
                      m5=mom[5] / (sg * 3), m15=mom[15] / (sg * 4), m30=mom[30] / (sg * 6), volr=(sg30 or sg) / sg, agecl=min(age_cl(t), 30),
                      spread=(lev.get("cb", S0) - S0) / sg, spread_bn=(lev.get("bn", S0) - S0) / sg, dp3=p0 - (hist[-4] if len(hist) > 3 else p0),
                      stab=float(np.std(h10)) if len(h10) > 2 else 0.0, flips=flips, slope=slope / sg, curv=curv * 100 / sg,
                      fin_err=(fin_off - E0) / sd if fin_off else None, ua=ua, da=da, uz=r[8] or 0, dz=r[10] or 0))
D.sort(key=lambda x: x["t"])
cyc = sorted({d["st"] for d in D}); cut = cyc[int(len(cyc) * 0.6)]
TR = [d for d in D if d["st"] < cut]; TE = [d for d in D if d["st"] >= cut]
lg = lambda p: math.log(max(1e-4, min(1 - 1e-4, p)) / (1 - max(1e-4, min(1 - 1e-4, p))))
FEAT = lambda d: [lg(d["p0"]), lg(d["pC"]), d["m5"], d["m15"], d["m30"], d["volr"], d["agecl"] / 10, d["spread"], d["spread_bn"], d["dp3"] * 5, d["stab"] * 5,
                  d["flips"] / 3, d["slope"], d["curv"], d["rem"] / 60, d["tl"] / 90]
y_tr = np.array([d["up"] for d in TR]); X_tr = np.array([FEAT(d) for d in TR])
mB = LogisticRegression(C=0.5, max_iter=3000).fit(X_tr, y_tr)
for d in TE: d["pB"] = float(mB.predict_proba(np.array([FEAT(d)]))[0, 1])
# distribution empirique des erreurs standardisees de la moyenne finale (apprise sur le passe)
errs = collections.defaultdict(list)
for d in TR:
    if d["fin_err"] is not None: errs[int(d["tl"] // 15)].append(d["fin_err"])
for d in TE:
    e = np.array(errs.get(int(d["tl"] // 15)) or [0.0]); d["pE"] = float(np.mean(e > -d["z"]))
# jumeaux
JX = lambda d: [d["z"], d["tl"] / 30, d["m15"], d["m30"], d["volr"]]
nn = NearestNeighbors(n_neighbors=60).fit(np.array([JX(d) for d in TR]))
_, ind = nn.kneighbors(np.array([JX(d) for d in TE]))
for d, ii in zip(TE, ind): d["pJ"] = float(np.mean(y_tr[ii]))
PR = {"moteur actuel (perp)": "p0", "C : nowcast 4 bourses": "pC", "sauts (loi de Student)": "pT", "distribution empirique des erreurs": "pE",
      "jumeaux (60 plus proches cas passés)": "pJ", "B : correction apprise": "pB"}
rap = [f"# Recherche TWAP fin — BTC, {len(cyc)} cycles ({hs(cyc[0])} → {hs(cyc[-1] + 300)})", "",
       f"Apprentissage sur les {sum(1 for c in cyc if c < cut)} premiers cycles (jusqu'au {hs(cut)}), **test sur les {sum(1 for c in cyc if c >= cut)} cycles suivants, jamais vus**. "
       f"Une mesure par seconde entre 90 et 20 s de la fin ({len(TE)} mesures de test).", "",
       "## 1. Qualité de prévision du gagnant officiel (test)", "", "| Probabilité | Brier (plus bas = mieux) | Log-loss |", "|---|---|---|"]
y = np.array([d["up"] for d in TE], float)
for nom, k in PR.items():
    p = np.clip(np.array([d[k] for d in TE]), 1e-4, 1 - 1e-4)
    rap.append(f"| {nom} | {np.mean((p - y) ** 2):.4f} | {-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)):.4f} |")
mids = [(d, (d["ua"] + (1 - d["da"])) / 2) for d in TE if d["ua"] is not None and d["da"] is not None]
if mids:
    yy = np.array([d["up"] for d, _ in mids], float); pm = np.array([m for _, m in mids])
    p0m = np.array([d["p0"] for d, _ in mids])
    rap.append(f"| *(carnet Polymarket, sur les {len(mids)} mesures où il existe ; moteur sur les mêmes : {np.mean((p0m - yy) ** 2):.4f})* | {np.mean((pm - yy) ** 2):.4f} | |")
def regle(k, X, extra=None):
    L = []
    by = collections.defaultdict(list)
    for d in X: by[d["st"]].append(d)
    for st, Y in sorted(by.items()):
        for d in Y:
            done = False
            for up in (True, False):
                p = d[k] if up else 1 - d[k]; ask = d["ua"] if up else d["da"]; z = d["uz"] if up else d["dz"]
                if ask is None or not (0.02 <= ask <= 0.98) or z <= 0 or p - ask < 0.20: continue
                if extra and not extra(d, up): continue
                parts = min(50 / ask, z); gm = d["up"] if up else not d["up"]
                L.append(dict(d=d, up=up, pnl=parts * ((1 if gm else 0) - ask - FEE(ask)), mise=parts * ask, g=gm, ask=ask)); done = True; break
            if done: break
    return L
def ligne(nom, L):
    if not L: return f"| {nom} | 0 | | | | | | |"
    pn = [l["pnl"] for l in L]; cum = pk = cr = 0.0; s = sm = 0
    for l in L: cum += l["pnl"]; pk = max(pk, cum); cr = min(cr, cum - pk); s = 0 if l["g"] else s + 1; sm = max(sm, s)
    m = len(L) // 2
    return (f"| {nom} | {len(L)} | {100 * sum(l['g'] for l in L) / len(L):.0f} % | {stt.mean(l['mise'] for l in L):.0f} $ | **{f0(sum(pn))}** | {100 * sum(pn) / sum(l['mise'] for l in L):+.0f} % | {f0(cr)} | {sm} | "
            f"{sum(1 for l in L if l['pnl'] >= 100)} | {f0(sum(pn[:m]))} / {f0(sum(pn[m:]))} |")
H = "| Probabilité utilisée | Achats | Gagnés | Mise remplie | Résultat | Par $ | Creux | Pertes de suite max | Gains ≥ +100 $ | 1re / 2e moitié du test |\n|---|---|---|---|---|---|---|---|---|---|"
rap += ["", "## 2. Règle TWAP fin (probabilité − prix ≥ 0,20, 90-20 s, un achat par cycle, quantité affichée) — cycles de test", "", H]
for nom, k in PR.items(): rap.append(ligne(nom, regle(k, TE)))
# 3. analyses de la regle actuelle (moteur) sur TOUS les cycles
ALL = regle("p0", D)
def coupe(titre, groupes):
    o = ["", f"### {titre}", "", H.replace("Probabilité utilisée", "Groupe")]
    for nom, f in groupes: o.append(ligne(nom, [l for l in ALL if f(l)]))
    return o
ed = lambda l: (l["d"]["p0"] if l["up"] else 1 - l["d"]["p0"]) - l["ask"]
dirp = lambda l: l["d"]["dp3"] * (1 if l["up"] else -1)
rap += ["", "## 3. Les trades du moteur actuel (tous les cycles), découpés selon les idées de ChatGPT", ""]
rap += coupe("Idée 2/9 — vitesse : variation de la probabilité sur 3 s, dans notre sens", [("monte vite (≥ +5 pts)", lambda l: dirp(l) >= 0.05), ("stable (−5 à +5)", lambda l: -0.05 < dirp(l) < 0.05), ("baisse (≤ −5 pts)", lambda l: dirp(l) <= -0.05)])
rap += coupe("Idée 10 — stabilité de la probabilité sur 10 s", [("stable (écart-type < 0,03)", lambda l: l["d"]["stab"] < 0.03), ("agitée (≥ 0,03)", lambda l: l["d"]["stab"] >= 0.03),
                                                                ("a changé de favori sur 10 s", lambda l: l["d"]["flips"] > 0)])
rap += coupe("Idée 11 — mouvement nécessaire pour inverser (distance en écarts-types)", [("|z| < 0,5", lambda l: abs(l["d"]["z"]) < 0.5), ("0,5-1", lambda l: 0.5 <= abs(l["d"]["z"]) < 1), ("1-2", lambda l: 1 <= abs(l["d"]["z"]) < 2), ("≥ 2", lambda l: abs(l["d"]["z"]) >= 2)])
sgn = lambda l: 1 if l["up"] else -1
rap += coupe("Idée 4/20 — forme de la trajectoire sur 30 s (pente dans notre sens)", [("pente dans notre sens", lambda l: l["d"]["slope"] * sgn(l) > 0), ("pente contre nous", lambda l: l["d"]["slope"] * sgn(l) <= 0),
                                                                                     ("accélère dans notre sens", lambda l: l["d"]["curv"] * sgn(l) > 0), ("ralentit / s'inverse", lambda l: l["d"]["curv"] * sgn(l) <= 0)])
rap += coupe("Idée 17 — volatilité 30 s / volatilité 5 min", [("plus calme qu'avant (< 0,8)", lambda l: l["d"]["volr"] < 0.8), ("pareil (0,8-1,25)", lambda l: 0.8 <= l["d"]["volr"] < 1.25), ("plus agitée (≥ 1,25)", lambda l: l["d"]["volr"] >= 1.25)])
rap += coupe("Idée 21 — côté acheté", [("Up", lambda l: l["up"]), ("Down", lambda l: not l["up"])])
rap += coupe("Idée 27 — avance des bourses : Coinbase par rapport au perp, dans notre sens", [("Coinbase dans notre sens", lambda l: l["d"]["spread"] * sgn(l) > 0.2), ("neutre", lambda l: abs(l["d"]["spread"]) <= 0.2), ("Coinbase contre nous", lambda l: l["d"]["spread"] * sgn(l) < -0.2)])
rap += coupe("Idée 3 — fraîcheur du dernier prix Chainlink reçu", [("< 2 s", lambda l: l["d"]["agecl"] < 2), ("2-5 s", lambda l: 2 <= l["d"]["agecl"] < 5), ("≥ 5 s", lambda l: l["d"]["agecl"] >= 5)])
rap += coupe("Écart annoncé", [("20-30 pts", lambda l: ed(l) < 0.30), ("30-50 pts", lambda l: 0.30 <= ed(l) < 0.50), ("≥ 50 pts", lambda l: ed(l) >= 0.50)])
# idee 5 : biais de l'erreur de moyenne finale
E = [(d["fin_err"], d["m15"], d["m30"], d["z"]) for d in D if d["fin_err"] is not None]
a = np.array(E)
rap += ["", "## 4. Idée 5 — l'erreur de la moyenne finale prévue a-t-elle un sens ?", "",
        f"Erreur standardisée (officiel − prévu, en écarts-types du moteur) : moyenne {a[:, 0].mean():+.3f}, écart-type {a[:, 0].std():.2f} (1,00 = moteur bien calibré).",
        f"Corrélation avec le mouvement 15 s : {np.corrcoef(a[:, 0], a[:, 1])[0, 1]:+.3f} ; 30 s : {np.corrcoef(a[:, 0], a[:, 2])[0, 1]:+.3f} (positif = le mouvement continue, négatif = il revient)."]
open("etude/bot5min/resultat_twap_recherche.md", "w").write("\n".join(rap)); print("\n".join(rap))
