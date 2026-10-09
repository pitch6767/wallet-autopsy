"""Inertie de la moyenne de clôture (idées ChatGPT 09.10.2026 au soir) — BTC, carnets enregistrés 07.10 → 09.10.
Règlement reconstruit : prix à battre = moyenne Chainlink des 60 s avant le début ; fin = moyenne des 60 s avant la fin (680/681 gagnants justes).
Pour chaque mesure du carnet dans les 90 dernières secondes, on calcule la probabilité de règlement « moyenne » (moteur TWAP) avec ce qui est
connu À CET INSTANT (Chainlink déjà reçu, prix BTC actuel, volatilité des 5 dernières minutes), sans rien du futur.
Tests : calibration contre Polymarket ; réaction excessive du carnet ; « règlement verrouillé » ; achats simulés au vrai carnet (quantité affichée)."""
import json, gzip, glob, math, bisect, time, statistics as stt, collections
import numpy as np
from sauvetage import FEE
phi = lambda x: 0.5 * (1 + math.erf(x / math.sqrt(2)))
f0 = lambda x: (f"+{x:,.0f} $" if x >= 0 else f"−{-x:,.0f} $").replace(",", "'")
O = json.load(open("bot95/officiels.json"))
rows = {}
for f in sorted(glob.glob("bot95/donnees/*/rec_BTC.json.gz")):
    for doc in json.load(gzip.open(f, "rt")).values():
        for r in doc["lignes"]: rows[r[0]] = r
rows = sorted(rows.values(), key=lambda r: r[0])
CLt = [r[0] for r in rows if r[15]]; CLv = [r[15] for r in rows if r[15]]
PPt = [r[0] for r in rows if (r[11] or r[12])]; PPv = [(r[11] or r[12]) for r in rows if (r[11] or r[12])]
def der(T, V, t):
    k = bisect.bisect_right(T, t) - 1
    return V[k] if k >= 0 and t - T[k] < 10 else None
def tw(a, b):                      # moyenne Chainlink des secondes a … b-1 (dernier prix reçu à chaque seconde)
    v = [der(CLt, CLv, s + 0.999) for s in range(a, b)]; v = [x for x in v if x is not None]
    return (sum(v) / len(v), len(v)) if v else (None, 0)
VC = {}
def vol(s):                        # écart-type par seconde, en $, sur 300 s (perp)
    if s not in VC:
        x = [der(PPt, PPv, k + 0.999) for k in range(s - 300, s)]; x = [y for y in x if y]
        VC[s] = float(np.std(np.diff(x))) if len(x) > 100 else None
    return VC[s]
BC = {}
def base(s):
    if s not in BC:
        d = [der(PPt, PPv, k + .999) - der(CLt, CLv, k + .999) for k in range(s - 120, s) if der(PPt, PPv, k + .999) and der(CLt, CLv, k + .999)]
        BC[s] = float(np.median(d)) if d else None
    return BC[s]
C = collections.defaultdict(list)
for r in rows: C[r[1]].append(r)
P = []        # une ligne par mesure du carnet dans les 90 dernières secondes
for st in sorted(C):
    g = (O.get(f"BTC:{st}") or {}).get("gagnant")
    K, n0 = tw(st - 60, st)
    if not g or K is None or n0 < 40: continue
    up_gagne = g == "Up"; end = st + 300
    for r in C[st]:
        t = r[0]; tl = end - t
        if tl > 90 or tl < 1: continue
        s = int(t); sg, b = vol(s), base(s); p = der(PPt, PPv, t)
        if not sg or b is None or not p: continue
        S = p - b                                    # prix BTC actuel ramené au niveau Chainlink
        deb = end - 60
        if s >= deb:
            con = [der(CLt, CLv, k + .999) for k in range(deb, s)]; con = [x for x in con if x is not None]
            rem = 60 - len(con); E = (sum(con) + rem * S) / 60; v = sg ** 2 * rem ** 3 / 3 / 3600
        else:
            rem = 60; E = S; v = sg ** 2 * ((deb - s) + 20)
        pt = phi((E - K) / math.sqrt(v + 0.25)) if v >= 0 else None      # + 0,5 $ d'erreur de reconstruction
        ub, ua, db, da = r[3], r[4], r[5], r[6]
        mid = (ub + ua) / 2 if ub is not None and ua is not None else (1 - (db + da) / 2 if db is not None and da is not None else None)
        P.append(dict(st=st, t=t, tl=tl, pt=pt, mid=mid, ua=ua, da=da, uz=r[8] or 0, dz=r[10] or 0, up=up_gagne, dist=E - K, S=S))
P.sort(key=lambda x: x["t"])
idx = collections.defaultdict(list)
for x in P: idx[x["st"]].append(x)
rap = [f"# Inertie de la moyenne de clôture — BTC, {len(idx)} cycles ({time.strftime('%d.%m %H:%M', time.gmtime(min(idx) + 7200))} → {time.strftime('%d.%m %H:%M', time.gmtime(max(idx) + 7500))})", "",
       f"{len(P)} mesures du carnet dans les 90 dernières secondes. Probabilité « moteur TWAP » calculée avec seulement ce qui était connu à l'instant.", ""]
# 1. calibration
rap += ["## 1. Qui prévoit le mieux le gagnant officiel : notre moteur TWAP ou le carnet Polymarket ?", "",
        "| Temps restant | Mesures | Brier moteur TWAP | Brier Polymarket (milieu) | Le meilleur |", "|---|---|---|---|---|"]
for a, b in ((60, 90), (40, 60), (20, 40), (10, 20), (1, 10)):
    X = [x for x in P if a <= x["tl"] < b and x["mid"] is not None and x["pt"] is not None]
    if len(X) < 50: continue
    y = np.array([x["up"] for x in X], float); bt = np.mean((np.array([x["pt"] for x in X]) - y) ** 2); bm = np.mean((np.array([x["mid"] for x in X]) - y) ** 2)
    rap.append(f"| {a}-{b} s | {len(X)} | {bt:.4f} | {bm:.4f} | {'moteur TWAP' if bt < bm else 'Polymarket'} |")
rap += ["", "Brier : plus bas = meilleur. Le milieu Polymarket n'existe pas quand un côté du carnet est vide (souvent dans les dernières secondes).", ""]
# 2. achats simules
def acheter(x, up):
    ask = x["ua"] if up else x["da"]; z = x["uz"] if up else x["dz"]
    if ask is None or not (0.02 <= ask <= 0.98) or z <= 0: return None
    parts = min(50 / ask, z); gm = x["up"] if up else not x["up"]
    return parts * ((1 if gm else 0) - ask - FEE(ask)), parts * ask, gm, ask
def strat(nom, cond, tmin=1, tmax=90):
    L = []
    for st, X in idx.items():
        for i, x in enumerate(X):
            if not (tmin <= x["tl"] <= tmax) or x["pt"] is None: continue
            j = i
            while j > 0 and x["t"] - X[j]["t"] < 3: j -= 1
            prev = X[j] if x["t"] - X[j]["t"] >= 2.5 else None
            for up in (True, False):
                res = cond(x, prev, up)
                if res:
                    a = acheter(x, up)
                    if a: L.append((x, up) + a); break
            else: continue
            break
    if not L: return f"| {nom} | 0 | | | | | |"
    pn = [l[2] for l in L]; mise = sum(l[3] for l in L); cum = pk = cr = 0.0
    for v in pn: cum += v; pk = max(pk, cum); cr = min(cr, cum - pk)
    m = len(L) // 2
    return (f"| {nom} | {len(L)} | {sum(l[4] for l in L)} ({100 * sum(l[4] for l in L) / len(L):.0f} %) | {stt.mean(l[5] for l in L):.2f} | **{f0(sum(pn))}** | {100 * sum(pn) / mise:+.0f} % | {f0(cr)} | {f0(sum(pn[:m]))} / {f0(sum(pn[m:]))} |")
prob = lambda x, up: x["pt"] if up else 1 - x["pt"]
askf = lambda x, up: x["ua"] if up else x["da"]
rap += ["## 2. Achats simulés (un par cycle, 50 $ au meilleur vendeur limité à la quantité affichée, frais compris)", "",
        "| Règle | Achats | Gagnés | Prix moyen | Résultat | Par $ | Creux | 1re moitié / 2e moitié |", "|---|---|---|---|---|---|---|---|"]
for e in (0.10, 0.15, 0.20, 0.30):
    rap.append(strat(f"moteur TWAP − prix ≥ {e:.2f}, 60 dernières secondes", lambda x, p, up, e=e: x["tl"] <= 60 and askf(x, up) is not None and prob(x, up) - askf(x, up) >= e))
for e in (0.10, 0.20):
    rap.append(strat(f"moteur TWAP − prix ≥ {e:.2f}, 60-90 s avant la fin", lambda x, p, up, e=e: x["tl"] > 60 and askf(x, up) is not None and prob(x, up) - askf(x, up) >= e))
for lk, mx in ((0.97, 0.90), (0.99, 0.95), (0.95, 0.85)):
    rap.append(strat(f"règlement « verrouillé » : moteur ≥ {lk}, prix ≤ {mx}", lambda x, p, up, lk=lk, mx=mx: askf(x, up) is not None and prob(x, up) >= lk and askf(x, up) <= mx, tmax=60))
def surreac(x, p, up, seuil):
    if p is None or askf(x, up) is None or askf(p, up) is None or p["pt"] is None: return False
    dm = (p["ua"] if up else p["da"]) - askf(x, up)       # baisse du prix de notre côté sur 3 s
    dp = prob(x, up) - prob(p, up)                         # variation de la proba TWAP de notre côté
    return x["tl"] <= 60 and dm >= seuil and dp > -dm / 3 and prob(x, up) - askf(x, up) >= 0.05
for sl in (0.10, 0.20):
    rap.append(strat(f"réaction excessive : notre côté chute de ≥ {sl:.2f} en 3 s alors que la proba TWAP baisse 3× moins, et moteur > prix", lambda x, p, up, sl=sl: surreac(x, p, up, sl)))
# 3. seuil implicite / vol implicite
iv = []
for x in P:
    if x["mid"] is None or x["pt"] is None or not (0.05 < x["mid"] < 0.95) or x["tl"] > 60: continue
    iv.append((x["pt"], x["mid"]))
if iv:
    a = np.array(iv); rap += ["", "## 3. Où le carnet et le moteur divergent le plus (60 dernières secondes, carnet entre 5 et 95 c)", "",
                              f"Écart moyen |moteur − carnet| : {np.mean(abs(a[:, 0] - a[:, 1])):.3f} ; corrélation {np.corrcoef(a[:, 0], a[:, 1])[0, 1]:.3f} ({len(a)} mesures)."]
open("etude/bot5min/resultat_twap_fin.md", "w").write("\n".join(rap)); print("\n".join(rap))
