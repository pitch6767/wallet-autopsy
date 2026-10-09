"""5 tests sur V2-F « ecart qui grandit » (BTC), 09.10.2026 — idees ChatGPT (oscillations, miroir temporel, nouveaute, consensus, memoire des erreurs).
Donnees : carnets sauves bot95/donnees/<jour>/rec_BTC.json.gz (4 mesures/s) + carnets encore dans le bot. Rien n'est change dans le bot.
1. Retournements du modele dans le cycle avant l'achat (zigzags >= 10 pts) et agitation des 30 s d'avant.
2. Miroir temporel : le signal existe-t-il encore si le modele a 0,25 / 0,5 / 1 / 2 s de retard (carnet inchange) ?
3. Nouveaute : la hausse du modele sur 3 s vient-elle du prix BTC, du temps qui passe ou de la volatilite ? (modele reconstruit)
4. Consensus interne : 5 variantes du modele (vol 60 s / 300 s / 900 s, Chainlink seul, marge corrigee) — dispersion.
5. Memoire des erreurs : pause quand la somme recente (resultat - prix paye) ou (resultat - modele) devient trop negative.
"""
import os, sys, json, gzip, glob, math, time, bisect, statistics as stt, collections
import numpy as np
sys.path.insert(0, "etude/bot5min")
from sauvetage import FEE, get, U
import sauvetage

OUT = "etude/bot5min/"
phi = lambda x: 0.5 * (1 + math.erf(x / math.sqrt(2)))


def charger():
    L = {}
    for f in sorted(glob.glob("bot95/donnees/*/rec_BTC.json.gz")):
        for k, doc in json.load(gzip.open(f, "rt")).items():
            for r in doc["lignes"]: L[r[0]] = r
    if os.environ.get("LOCAL"): pass
    else:
     try:
        apres = None
        while True:
            d = get(f"{U}/api/rec?a=BTC&n=60" + (f"&apres={apres}" if apres else ""))
            for doc in d["docs"]:
                for r in doc["lignes"]: L[r[0]] = r
            if not d["cles"] or len(d["cles"]) < 60: break
            apres = d["suivant"]
     except Exception as e: print("api rec", e)
    rows = sorted(L.values(), key=lambda r: r[0])
    C = collections.defaultdict(list)
    for r in rows:
        if None in (r[2], r[3], r[4], r[5], r[6]): continue
        C[r[1]].append(r)
    return rows, C


def main():
    rows, C = charger(); sts = sorted(C)
    print("cycles", len(sts), time.strftime("%d.%m %H:%M", time.gmtime(sts[0] + 7200)), "->", time.strftime("%d.%m %H:%M", time.gmtime(sts[-1] + 7500)))
    # resultats : cache du rejeu precedent, puis Polymarket, sinon Chainlink fin >= debut
    RES = {}
    try:
        for t in json.load(open(OUT + "v2f_tous.json")): RES[t["st"]] = t["gagne"] if t["cote"] == "Up" else (not t["gagne"])
    except Exception: pass
    # series 1 s : perp (Bybit sinon OKX) et Chainlink
    P1, CL1 = {}, {}
    for r in rows:
        s = int(r[0]); p = r[11] or r[12]
        if p: P1[s] = p
        if r[15]: CL1[s] = r[15]
    def serie(D, s0, s1): return [D[s] for s in range(s0, s1 + 1) if s in D]
    def vol(s, w):
        x = serie(P1, s - w, s)
        if len(x) < min(60, w // 2): return None
        lr = np.diff(np.log(x)); return float(np.std(lr)) or 1e-6
    def base(s):
        d = [P1[k] - CL1[k] for k in range(s - 120, s + 1) if k in P1 and k in CL1]
        return float(np.median(d)) if d else None
    def modele(t, st, K, perp, sg, b, sd=8e-4, S=None):
        if S is None:
            if perp is None or b is None: return None
            S = perp - b
        ts = int(t); end = st + 300; deb = end - 59
        if ts >= deb:
            con = [CL1[k] for k in range(deb, ts + 1) if k in CL1]; nr = max(1, end - ts)
            E = (sum(con) + nr * S) / (len(con) + nr); v = (sg * S) ** 2 * nr ** 3 / 3 / 3600
        else: E = S; v = (sg * S) ** 2 * ((deb - ts) + 20)
        return phi((E - K) / math.sqrt(v + (sd * S) ** 2))
    def res(st):
        if st in RES: return RES[st]
        g = None if os.environ.get("LOCAL") else sauvetage.resultat("BTC", st)
        if g is None:
            a, b = CL1.get(st), CL1.get(st + 300) or CL1.get(st + 299)
            g = (b >= a) if a and b else None
        RES[st] = g; return g
    # ---- rejeu V2-F + mesures
    T = []; verif = []
    for st in sts:
        R = C[st]; ts_ = [x[0] for x in R]
        def ligne(t):
            k = bisect.bisect_right(ts_, t) - 1
            return R[k] if k >= 0 else None
        for i, r in enumerate(R):
            tl = st + 300 - r[0]
            if tl < 5: break
            j = i
            while j > 0 and r[0] - R[j][0] < 3: j -= 1
            h3 = R[j] if r[0] - R[j][0] >= 2.5 else None
            if h3 is None: continue
            pris = None
            for up in (True, False):
                ask = r[4] if up else r[6]; fair = r[2] if up else 1 - r[2]
                a3 = h3[4] if up else h3[6]; f3 = h3[2] if up else 1 - h3[2]
                if ask is None or a3 is None or not (0.03 <= ask <= 0.97): continue
                if fair - ask >= 0.20 and (fair - ask) - (f3 - a3) >= 0.03: pris = (up, ask, fair, a3, f3); break
            if not pris: continue
            g = res(st)
            if g is None: break
            up, ask, fair, a3, f3 = pris; sg_ = 1 if up else -1; side = (lambda p: p if up else 1 - p)
            gm = g if up else (not g)
            pnl = (50 / ask) * ((1 if gm else 0) - ask - FEE(ask))
            dm, da = fair - f3, ask - a3
            if dm >= 0.02 and abs(da) < 0.02: orig = "M"
            elif da <= -0.02 and abs(dm) < 0.02: orig = "P"
            elif dm >= 0.02 and da <= -0.02: orig = "M+P"
            elif dm < 0 and da < dm: orig = "2B"
            else: orig = "autre"
            # 1. retournements : zigzag >= 0,10 sur le modele de notre cote depuis le debut du cycle
            ser = [side(x[2]) for x in R[:i + 1]]
            zz, d, hi, lo, e = 0, 0, ser[0], ser[0], ser[0]
            for v in ser:
                if d == 0:
                    hi, lo = max(hi, v), min(lo, v)
                    if hi - v >= 0.10: d, e = -1, v
                    elif v - lo >= 0.10: d, e = 1, v
                elif d == 1:
                    if v > e: e = v
                    elif e - v >= 0.10: zz += 1; d, e = -1, v
                else:
                    if v < e: e = v
                    elif v - e >= 0.10: zz += 1; d, e = 1, v
            agit = float(np.std([side(x[2]) for x in R[:i + 1] if r[0] - x[0] <= 30])) if i > 4 else 0.0
            # 2. miroir temporel
            mir = {}
            for L in (0.25, 0.5, 1.0, 2.0):
                x0, x3 = ligne(r[0] - L), ligne(r[0] - 3 - L)
                if x0 is None or x3 is None: mir[L] = False; continue
                fL, f3L = side(x0[2]), side(x3[2])
                mir[L] = fL - ask >= 0.20 and (fL - ask) - (f3L - a3) >= 0.03
            # 3. nouveaute : modele reconstruit, decomposition sur 3 s
            s0, s3 = int(r[0]), int(h3[0]); K = r[16]
            nouv = None; var = {}
            if K:
                sgA, sgB = vol(s0, 300), vol(s3, 300); bA, bB = base(s0), base(s3)
                pA, pB = (r[11] or r[12]), (h3[11] or h3[12])
                if None not in (sgA, sgB, bA, bB, pA, pB):
                    mA = modele(r[0], st, K, pA, sgA, bA); mB = modele(h3[0], st, K, pB, sgB, bB)
                    verif.append((r[2], mA))
                    m_prix = modele(h3[0], st, K, pA, sgB, bA) - mB
                    m_temps = modele(r[0], st, K, pA, sgB, bA) - modele(h3[0], st, K, pA, sgB, bA)
                    m_vol = mA - modele(r[0], st, K, pA, sgB, bA)
                    parts = {"prix BTC": sg_ * m_prix, "temps qui passe": sg_ * m_temps, "volatilite": sg_ * m_vol}
                    tot = sg_ * (mA - mB)
                    nouv = "modele stable" if tot < 0.02 else max(parts, key=lambda k: parts[k])
                    # 4. consensus : 5 variantes
                    for nom, (w, cl_seul, sd) in {"vol 300 s": (300, False, 8e-4), "vol 60 s": (60, False, 8e-4), "vol 900 s": (900, False, 8e-4),
                                                 "Chainlink seul": (300, True, 8e-4), "marge corrigee": (300, False, 1.5e-4)}.items():
                        sgw = vol(s0, w)
                        if sgw is None: continue
                        S = CL1.get(s0) if cl_seul else None
                        if cl_seul and S is None: continue
                        var[nom] = side(modele(r[0], st, K, pA, sgw, bA, sd=sd, S=S))
            T.append({"t": r[0], "st": st, "cote": "Up" if up else "Down", "prix": ask, "modele": round(fair, 3), "gagne": bool(gm), "pnl": round(pnl, 2),
                      "orig": orig, "reste": round(tl), "zz": zz, "agit": round(agit, 3), "mir": mir, "nouv": nouv, "var": {k: round(v, 3) for k, v in var.items()}})
            break
    T.sort(key=lambda x: x["t"])
    json.dump(T, open(OUT + "idees_v2f.json", "w"), ensure_ascii=False)
    # ---- outils de jugement
    best = c = s0 = 0
    for k, t in enumerate(T):
        c = c + 1 if not t["gagne"] else 0
        if c > best: best, s0 = c, k - c + 1
    SER = set(id(t) for t in T[s0:s0 + best])
    gros = set(id(t) for t in sorted(T, key=lambda t: -t["pnl"])[:10])
    q = [T[int(len(T) * k / 4)]["t"] for k in (1, 2, 3)]
    quart = lambda t: sum(t["t"] >= x for x in q)
    hs = lambda t: time.strftime("%d.%m %H:%M", time.gmtime(t + 7200))
    f0 = lambda x: (f"+{x:,.0f} $" if x >= 0 else f"−{-x:,.0f} $").replace(",", "'")
    H = "| Groupe / filtre | Trades | Gagnés | % gagnés | Résultat | Sans top 3 | Pertes de la série évitées | Des 10 plus gros gagnants | Q1 | Q2 | Q3 | Q4 |\n|---|---|---|---|---|---|---|---|---|---|---|---|"
    def lig(nom, X, garde=True):
        if not X: return f"| {nom} | 0 | | | | | | | | | | |"
        P = sorted((t["pnl"] for t in X), reverse=True); ids = set(id(t) for t in X)
        Q = [sum(t["pnl"] for t in X if quart(t) == k) for k in range(4)]
        return (f"| {nom} | {len(X)} | {sum(t['gagne'] for t in X)} | {100 * stt.mean(t['gagne'] for t in X):.0f} % | **{f0(sum(P))}** | {f0(sum(P[3:]))} | "
                f"{sum(1 for k in SER if k not in ids)} / {best} | {sum(1 for k in gros if k in ids)} / 10 | " + " | ".join(f0(x) for x in Q) + " |")
    tot = sum(t["pnl"] for t in T)
    rap = [f"# 5 tests sur V2-F « écart qui grandit » (BTC) — rejeu sur les vrais carnets ({hs(T[0]['t'])} → {hs(T[-1]['t'])})", "",
           f"{len(T)} trades rejoués, {sum(t['gagne'] for t in T)} gagnés, {f0(tot)}. Plus longue série de pertes du rejeu : {best} ({hs(T[s0]['t'])} → {hs(T[s0 + best - 1]['t'])}).", ""]
    if verif:
        a = np.array(verif); cor = float(np.corrcoef(a[:, 0], a[:, 1])[0, 1]); err = float(np.median(np.abs(a[:, 0] - a[:, 1])))
        rap += [f"Modèle reconstruit (tests 3 et 4) contre modèle enregistré par le bot : corrélation {cor:.3f}, écart médian {100 * err:.1f} pts.", ""]
    rap += ["## Test 1 — retournements du modèle dans le cycle avant l'achat", "", H, lig("TOUS", T)]
    for nm, f in (("0 retournement (≥ 10 pts)", lambda t: t["zz"] == 0), ("1 retournement", lambda t: t["zz"] == 1), ("2 retournements", lambda t: t["zz"] == 2), ("3 et plus", lambda t: t["zz"] >= 3)):
        rap.append(lig(nm, [t for t in T if f(t)]))
    a1, a2 = np.percentile([t["agit"] for t in T], [33, 67])
    for nm, f in ((f"agitation 30 s faible (< {a1:.3f})", lambda t: t["agit"] < a1), ("agitation moyenne", lambda t: a1 <= t["agit"] < a2), (f"agitation forte (≥ {a2:.3f})", lambda t: t["agit"] >= a2)):
        rap.append(lig(nm, [t for t in T if f(t)]))
    rap += ["", "## Test 2 — miroir temporel (modèle en retard, carnet inchangé)", "", H, lig("TOUS", T)]
    for L in (0.25, 0.5, 1.0, 2.0):
        rap.append(lig(f"signal encore là avec {L} s de retard", [t for t in T if t["mir"][L]]))
        rap.append(lig(f"signal disparaît avec {L} s de retard", [t for t in T if not t["mir"][L]]))
    rap.append(lig("solide : là aux 4 retards", [t for t in T if all(t["mir"].values())]))
    rap.append(lig("fragile : disparaît à au moins un retard", [t for t in T if not all(t["mir"].values())]))
    rap += ["", "## Test 3 — d'où vient la hausse du modèle sur 3 s (nouveauté de l'information)", "", H, lig("TOUS", T)]
    for nm in ("prix BTC", "temps qui passe", "volatilite", "modele stable", None):
        rap.append(lig(nm or "non calculable", [t for t in T if t["nouv"] == nm]))
    rap += ["", "Dans « modèle stable », c'est Polymarket qui a bougé (le modèle n'a pas pris 2 pts).", "",
            "## Test 4 — consensus interne (5 variantes du modèle)", "", H, lig("TOUS", T)]
    D = [t for t in T if len(t["var"]) >= 4]
    for t in D:
        v = list(t["var"].values()); t["disp"] = max(v) - min(v); t["nb20"] = sum(1 for x in v if x - t["prix"] >= 0.20); t["nv"] = len(v)
    if D:
        d1, d2 = np.percentile([t["disp"] for t in D], [33, 67])
        for nm, f in ((f"variantes proches (dispersion < {100 * d1:.0f} pts)", lambda t: t["disp"] < d1), ("dispersion moyenne", lambda t: d1 <= t["disp"] < d2),
                      (f"variantes en désaccord (≥ {100 * d2:.0f} pts)", lambda t: t["disp"] >= d2),
                      ("toutes les variantes voient ≥ 20 pts d'écart", lambda t: t["nb20"] == t["nv"]), ("au moins une variante ne voit pas 20 pts", lambda t: t["nb20"] < t["nv"]),
                      ("la variante « marge corrigée » voit ≥ 20 pts", lambda t: t["var"].get("marge corrigee", 0) - t["prix"] >= 0.20),
                      ("la variante « Chainlink seul » voit ≥ 20 pts", lambda t: t["var"].get("Chainlink seul", 0) - t["prix"] >= 0.20),
                      ("la variante « vol 60 s » voit ≥ 20 pts", lambda t: t["var"].get("vol 60 s", 0) - t["prix"] >= 0.20)):
            rap.append(lig(nm, [t for t in D if f(t)]))
    # 5. memoire des erreurs
    rap += ["", "## Test 5 — mémoire des erreurs (pause si les trades récents déjà réglés sont trop mauvais)", "",
            "On ne regarde que les trades déjà réglés au moment de l'achat. Somme sur les N derniers de (1 si gagné sinon 0) − prix payé = notre vrai avantage récent contre Polymarket ; ou − modèle = l'erreur du modèle.", "", H, lig("TOUS (aucune pause)", T)]
    for base_, N, ks in (("prix", 20, (-1, -2, -3)), ("prix", 30, (-2, -3, -4)), ("modele", 20, (-3, -4, -5)), ("modele", 30, (-5, -6, -7))):
        for k in ks:
            X = []
            for i, t in enumerate(T):
                regl = [u for u in T[:i] if u["st"] + 300 <= t["t"]][-N:]
                if len(regl) == N and sum((1 if u["gagne"] else 0) - u[base_] for u in regl) < k: continue
                X.append(t)
            rap.append(lig(f"pause si somme(résultat − {base_}) sur {N} derniers < {k}", X))
    def pause(X0, N=20, k=-2):
        X = []
        for i, t in enumerate(T):
            regl = [u for u in T[:i] if u["st"] + 300 <= t["t"]][-N:]
            if len(regl) == N and sum((1 if u["gagne"] else 0) - u["prix"] for u in regl) < k: continue
            if t in X0: X.append(t)
        return X
    frais = lambda L: [t for t in T if not t["mir"][L]]
    rap += ["", "## Combinaisons", "", H, lig("TOUS", T),
            lig("écart né dans la dernière seconde (disparaît avec 1 s de retard)", frais(1.0)),
            lig("écart né dans la dernière 0,25 s", frais(0.25)),
            lig("pause (résultat − prix, 20 derniers < −2)", pause(T)),
            lig("écart né dans la dernière seconde + pause", pause(frais(1.0))),
            lig("écart né dans la dernière seconde + pas « les deux baissent »", [t for t in frais(1.0) if t["orig"] != "2B"]),
            lig("écart né dans la dernière seconde + pas « les deux baissent » + pause", pause([t for t in frais(1.0) if t["orig"] != "2B"])),
            lig("pas « les deux baissent » (déjà en fantôme)", [t for t in T if t["orig"] != "2B"]),
            lig("vol 60 s voit ≥ 20 pts + écart né dans la dernière seconde", [t for t in frais(1.0) if t["var"].get("vol 60 s", 0) - t["prix"] >= 0.20])]
    # premiere et seconde moitie : robustesse
    m = len(T) // 2
    rap += ["", "Robustesse — première moitié / seconde moitié des trades :", ""]
    for nm, X in (("TOUS", T), ("écart né dans la dernière seconde", frais(1.0)), ("pause −2", pause(T)), ("écart né dernière seconde + pause", pause(frais(1.0)))):
        A = [t for t in X if T.index(t) < m]; B = [t for t in X if T.index(t) >= m]
        rap.append(f"- {nm} : {f0(sum(t['pnl'] for t in A))} / {f0(sum(t['pnl'] for t in B))}")
    open(OUT + "resultat_idees_v2f.md", "w").write("\n".join(rap))
    print("\n".join(rap))


if __name__ == "__main__":
    main()
