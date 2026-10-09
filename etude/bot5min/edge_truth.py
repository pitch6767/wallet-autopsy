"""EDGE TRUTH (demande ChatGPT/Pitch, 09.10.2026) — V2-F « ecart qui grandit » BTC, rien n'est change dans le bot.
A. Modele avec moins d'incertitude fixe (0,08 % actuel -> 0,02 % / 0,01 %) : rejeu COMPLET de la regle V2-F avec chaque version
   (les opportunites qui disparaissent ET celles qui apparaissent), calibration, P&L.
B. Probabilite corrigee « historique » apprise en avancant dans le temps (jamais de resultat futur) :
   B1 groupes origine x prix, regularises vers le prix paye ; B2 regression logistique (prix, modele, temps restant, distance Chainlink,
   volatilite, origine, cote). Decision = esperance nette > 0 (P x 1 $ - prix - frais), pas le taux de reussite -> les jetons a 0,05 $ restent possibles.
   B3 = B2 + mise 25 $ quand l'avantage estime est faible (< 25 % par dollar).
C. Les 88 « les deux baissent » : classement par avantage corrige, gagnants vs perdants.
Donnees : v2f_tous.json (448 trades rejoues) + carnets sauves bot95/donnees (4 mesures/s).
"""
import os, sys, json, gzip, glob, math, time, bisect, statistics as stt, collections
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
sys.path.insert(0, "etude/bot5min")
from sauvetage import FEE

OUT = "etude/bot5min/"
phi = lambda x: 0.5 * (1 + math.erf(x / math.sqrt(2)))
f0 = lambda x: (f"+{x:,.0f} $" if x >= 0 else f"−{-x:,.0f} $").replace(",", "'")
hs = lambda t: time.strftime("%d.%m %H:%M", time.gmtime(t + 7200))
MIN_APP = 120          # trades deja regles necessaires avant de commencer a decider


def stats(X, mises=None):
    """X : liste de trades (dict avec pnl pour 50 $, prix, gagne). mises : dict id->mise."""
    pn = [t["pnl"] * ((mises or {}).get(id(t), 50) / 50) for t in X]
    cum = pk = cr = 0.0; ser = smax = 0
    for t, x in zip(X, pn):
        cum += x; pk = max(pk, cum); cr = min(cr, cum - pk)
        ser = 0 if t["gagne"] else ser + 1; smax = max(smax, ser)
    eng = sum((mises or {}).get(id(t), 50) for t in X)
    return {"n": len(X), "g": sum(t["gagne"] for t in X), "pnl": sum(pn), "creux": cr, "smax": smax, "par$": sum(pn) / eng if eng else 0, "pn": pn}


def main():
    T = json.load(open(OUT + "v2f_tous.json")); T.sort(key=lambda t: t["t"])
    for t in T: t["jack"] = t["pnl"] >= 200
    nJ = sum(t["jack"] for t in T)
    rap = [f"# EDGE TRUTH — V2-F « écart qui grandit » (BTC), rejeu sur les vrais carnets ({hs(T[0]['t'])} → {hs(T[-1]['t'] + 60)})", "",
           f"{len(T)} trades, {sum(t['gagne'] for t in T)} gagnés, {f0(sum(t['pnl'] for t in T))} · « jackpot » = trade qui rapporte au moins +200 $ ({nJ} trades). 50 $ par trade, frais compris.", ""]
    # ================= B. probabilite corrigee, apprise en avancant dans le temps =================
    ORIG = ["le modele monte, Poly stable", "Poly baisse, modele stable", "modele monte ET Poly baisse", "les deux baissent, Poly plus", "autre"]
    lg = lambda p: math.log(max(1e-3, min(1 - 1e-3, p)) / (1 - max(1e-3, min(1 - 1e-3, p))))
    def feat(t):
        return [lg(t["prix"]), lg(t["modele"]), t["reste"] / 300, max(-3, min(3, t["z"])), math.log(max(0.3, t["vol"])), 1.0 if t["cote"] == "Up" else 0.0] + [1.0 if t["origine"] == o else 0.0 for o in ORIG[:-1]]
    bucket = lambda p: 0 if p < 0.10 else 1 if p < 0.20 else 2 if p < 0.35 else 3
    K = 20
    for i, t in enumerate(T):
        app = [u for u in T[:i] if u["st"] + 300 <= t["t"]]
        t["napp"] = len(app)
        if len(app) < MIN_APP: t["p_grp"] = t["p_log"] = None; continue
        G = [u for u in app if u["origine"] == t["origine"] and bucket(u["prix"]) == bucket(t["prix"])]
        t["p_grp"] = (sum(u["gagne"] for u in G) + K * t["prix"]) / (len(G) + K)
        X = np.array([feat(u) for u in app]); y = np.array([u["gagne"] for u in app])
        m = LogisticRegression(C=0.3, max_iter=2000).fit(X, y)
        t["p_log"] = float(m.predict_proba(np.array([feat(t)]))[0, 1])
    TE = [t for t in T if t["p_log"] is not None]
    ev = lambda p, prix: p - prix - FEE(prix)
    rap += ["## 1. Les probabilités corrigées (apprises seulement sur le passé)", "",
            f"Chaque trade est jugé avec ce qu'on savait au moment de l'achat (trades déjà réglés). On attend {MIN_APP} trades réglés avant de décider : "
            f"les **{len(TE)} trades « nouveaux »** vont du {hs(TE[0]['t'])} au {hs(TE[-1]['t'])}.", "",
            "| Probabilité | Annonce en moyenne | Gagne en vrai | Brier (plus bas = mieux) | AUC (gagnants vs perdants, 0,5 = hasard) |", "|---|---|---|---|---|"]
    y = np.array([t["gagne"] for t in TE])
    for nom, k in (("modèle du bot (V2-F)", "modele"), ("prix Polymarket payé", "prix"), ("B1 groupes origine × prix", "p_grp"), ("B2 régression (prix, modèle, temps, distance, volatilité, origine, côté)", "p_log")):
        p = np.array([t[k] for t in TE])
        rap.append(f"| {nom} | {100 * p.mean():.1f} % | {100 * y.mean():.1f} % | {np.mean((p - y) ** 2):.4f} | {roc_auc_score(y, p):.3f} |")
    rap += ["", "### Calibration de B2 par tranche", "", "| B2 annonce | Trades | Annonce moyenne | Gagne en vrai | Prix moyen payé | Résultat |", "|---|---|---|---|---|---|"]
    for a, b in ((0, 0.15), (0.15, 0.25), (0.25, 0.35), (0.35, 1.01)):
        X = [t for t in TE if a <= t["p_log"] < b]
        if X: rap.append(f"| {a:.2f}–{min(b, 1):.2f} | {len(X)} | {100 * stt.mean(t['p_log'] for t in X):.0f} % | {100 * stt.mean(t['gagne'] for t in X):.0f} % | {stt.mean(t['prix'] for t in X):.2f} | {f0(sum(t['pnl'] for t in X))} |")
    # decisions
    H = "| Décision | Trades | Gagnés | Résultat | Par $ engagé | Creux max | Pertes de suite max | Jackpots gardés | 1re moitié | 2e moitié |\n|---|---|---|---|---|---|---|---|---|---|"
    mid = TE[len(TE) // 2]["t"]; JT = sum(t["jack"] for t in TE)
    def lig(nom, X, mises=None):
        s = stats(X, mises); A = [t for t in X if t["t"] < mid]; B = [t for t in X if t["t"] >= mid]
        return (f"| {nom} | {s['n']} | {s['g']} | **{f0(s['pnl'])}** | {100 * s['par$']:+.0f} % | {f0(s['creux'])} | {s['smax']} | {sum(t['jack'] for t in X)} / {JT} | "
                f"{f0(stats(A, mises)['pnl'])} | {f0(stats(B, mises)['pnl'])} |")
    D1 = [t for t in TE if ev(t["p_grp"], t["prix"]) > 0]
    D2 = [t for t in TE if ev(t["p_log"], t["prix"]) > 0]
    M3 = {id(t): (50 if ev(t["p_log"], t["prix"]) / t["prix"] >= 0.25 else 25) for t in D2}
    D4 = [t for t in TE if ev(t["p_log"], t["prix"]) > 0.02]
    rap += ["", "## 2. Les décisions comparées sur les trades nouveaux", "", H,
            lig("1. V2-F original (tout acheter)", TE),
            lig("2a. probabilité corrigée B1 (groupes) : acheter si espérance > 0", D1),
            lig("2b. probabilité corrigée B2 (régression) : acheter si espérance > 0", D2),
            lig("2c. B2, espérance > 2 cents par jeton", D4),
            lig("3. B2 + mise 25 $ quand l'avantage estimé < 25 % par dollar", D2, M3), ""]
    # pourquoi : ce que B2 retire
    R2 = [t for t in TE if t not in D2]
    if R2:
        c = collections.Counter(t["origine"] for t in R2)
        rap += [f"Ce que B2 retire : {len(R2)} trades, {sum(t['gagne'] for t in R2)} gagnés, {f0(sum(t['pnl'] for t in R2))} ; "
                f"jackpots retirés {sum(t['jack'] for t in R2)}. Par origine : " + ", ".join(f"{k} {v}" for k, v in c.most_common()) + ".", ""]
    # ================= C. les 88 « les deux baissent » =================
    DB = [t for t in T if t["origine"] == "les deux baissent, Poly plus"]
    DBn = [t for t in DB if t["p_log"] is not None]
    rap += [f"## 3. Les {len(DB)} trades « les deux baissent, Polymarket plus fort »", "",
            f"Tous : {sum(t['gagne'] for t in DB)} gagnés, {f0(sum(t['pnl'] for t in DB))}. Parmi eux, **{len(DBn)} sont des trades nouveaux** (jugés sans voir leur résultat) : "
            f"{sum(t['gagne'] for t in DBn)} gagnés, {f0(sum(t['pnl'] for t in DBn))}.", ""]
    def tiers(X, key, nom):
        X = sorted(X, key=key, reverse=True); n = len(X); o = []
        for k, (a, b) in enumerate(((0, n // 3), (n // 3, 2 * n // 3), (2 * n // 3, n))):
            Y = X[a:b]
            if Y: o.append(f"| {nom} — tiers {'haut' if k == 0 else 'milieu' if k == 1 else 'bas'} | {len(Y)} | {sum(t['gagne'] for t in Y)} | {stt.mean(key(t) for t in Y):+.3f} | {f0(sum(t['pnl'] for t in Y))} |")
        return o
    if len(DBn) >= 9:
        rap += ["### 3.1 Sur les trades nouveaux (strictement sans regarder l'avenir)", "", "| Classement par | Trades | Gagnés | Avantage moyen | Résultat |", "|---|---|---|---|---|"]
        rap += tiers(DBn, lambda t: ev(t["p_log"], t["prix"]), "avantage corrigé B2")
        rap += tiers(DBn, lambda t: t["modele"] - t["prix"], "avantage annoncé par le modèle")
        yy = [t["gagne"] for t in DBn]
        if 0 < sum(yy) < len(yy):
            rap += ["", f"AUC sur ces trades (0,5 = hasard) : B2 {roc_auc_score(yy, [t['p_log'] for t in DBn]):.2f} · modèle du bot {roc_auc_score(yy, [t['modele'] for t in DBn]):.2f} · prix {roc_auc_score(yy, [t['prix'] for t in DBn]):.2f}"]
        k = [t for t in DBn if ev(t["p_log"], t["prix"]) > 0]
        rap += [f"", f"B2 en garde {len(k)} (espérance > 0) : {sum(t['gagne'] for t in k)} gagnés, {f0(sum(t['pnl'] for t in k))} ; il en écarte {len(DBn) - len(k)} : "
                f"{sum(t['gagne'] for t in DBn if t not in k)} gagnés, {f0(sum(t['pnl'] for t in DBn if t not in k))}.", ""]
    # validation croisee par blocs de temps pour les 88 (pas strictement chronologique : indique)
    blocs = np.array_split(np.arange(len(T)), 5)
    for b in blocs:
        test = set(b.tolist()); app = [u for j, u in enumerate(T) if j not in test]
        m = LogisticRegression(C=0.3, max_iter=2000).fit(np.array([feat(u) for u in app]), np.array([u["gagne"] for u in app]))
        for j in test: T[j]["p_cv"] = float(m.predict_proba(np.array([feat(T[j])]))[0, 1])
    rap += [f"### 3.2 Sur les {len(DB)} (validation par 5 blocs de temps : chaque bloc jugé par un modèle appris sur les 4 autres — utilise aussi des données postérieures, donc moins strict)", "",
            "| Classement par | Trades | Gagnés | Avantage moyen | Résultat |", "|---|---|---|---|---|"]
    rap += tiers(DB, lambda t: ev(t["p_cv"], t["prix"]), "avantage corrigé")
    yy = [t["gagne"] for t in DB]
    rap += ["", f"AUC : modèle corrigé {roc_auc_score(yy, [t['p_cv'] for t in DB]):.2f} · modèle du bot {roc_auc_score(yy, [t['modele'] for t in DB]):.2f} · prix {roc_auc_score(yy, [t['prix'] for t in DB]):.2f}", ""]
    yy = [t["gagne"] for t in T]
    rap += [f"Sur les {len(T)} trades (même validation par blocs) : AUC modèle corrigé {roc_auc_score(yy, [t['p_cv'] for t in T]):.2f} · modèle du bot {roc_auc_score(yy, [t['modele'] for t in T]):.2f} · prix {roc_auc_score(yy, [t['prix'] for t in T]):.2f}", ""]
    json.dump([{k: v for k, v in t.items() if k != "pn"} for t in T], open(OUT + "edge_truth.json", "w"), ensure_ascii=False)
    # ================= A. moins d'incertitude fixe : rejeu complet =================
    rap += partie_A(T)
    open(OUT + "resultat_edge_truth.md", "w").write("\n".join(rap))
    print("\n".join(rap))


def partie_A(T0):
    L = {}
    for f in sorted(glob.glob("bot95/donnees/*/rec_BTC.json.gz")):
        for k, doc in json.load(gzip.open(f, "rt")).items():
            for r in doc["lignes"]: L[r[0]] = r
    rows = sorted(L.values(), key=lambda r: r[0])
    C = collections.defaultdict(list)
    for r in rows:
        if None in (r[2], r[3], r[4], r[5], r[6]): continue
        C[r[1]].append(r)
    RES = {t["st"]: (t["gagne"] if t["cote"] == "Up" else not t["gagne"]) for t in T0}
    P1, CL1 = {}, {}
    for r in rows:
        s = int(r[0]); p = r[11] or r[12]
        if p: P1[s] = p
        if r[15]: CL1[s] = r[15]
    VC, BC = {}, {}
    def vol(s):
        if s not in VC:
            x = [P1[k] for k in range(s - 300, s + 1) if k in P1]
            VC[s] = (float(np.std(np.diff(np.log(x)))) or 1e-6) if len(x) >= 150 else None
        return VC[s]
    def base(s):
        if s not in BC:
            d = [P1[k] - CL1[k] for k in range(s - 120, s + 1) if k in P1 and k in CL1]
            BC[s] = float(np.median(d)) if d else None
        return BC[s]
    def modele(r, st, sd):
        K = r[16]; p = r[11] or r[12]; s = int(r[0])
        if not K or not p: return None
        sg, b = vol(s), base(s)
        if sg is None or b is None: return None
        S = p - b; end = st + 300; deb = end - 59
        if s >= deb:
            con = [CL1[k] for k in range(deb, s + 1) if k in CL1]; nr = max(1, end - s)
            E = (sum(con) + nr * S) / (len(con) + nr); v = (sg * S) ** 2 * nr ** 3 / 3 / 3600
        else: E = S; v = (sg * S) ** 2 * ((deb - s) + 20)
        return phi((E - K) / math.sqrt(v + (sd * S) ** 2))
    def rejouer(sd):
        out = []
        for st in sorted(C):
            g = RES.get(st)
            if g is None:
                a, b = CL1.get(st), CL1.get(st + 300) or CL1.get(st + 299)
                g = (b >= a) if a and b else None
            if g is None: continue
            R = C[st]; MC = {}
            mo = lambda k: MC.setdefault(k, R[k][2] if sd is None else modele(R[k], st, sd))
            for i, r in enumerate(R):
                tl = st + 300 - r[0]
                if tl < 5: break
                j = i
                while j > 0 and r[0] - R[j][0] < 3: j -= 1
                if r[0] - R[j][0] < 2.5: continue
                pu, p3 = mo(i), mo(j)
                if pu is None or p3 is None: continue
                h3 = R[j]; fait = False
                for up in (True, False):
                    ask = r[4] if up else r[6]; a3 = h3[4] if up else h3[6]
                    fair = pu if up else 1 - pu; f3 = p3 if up else 1 - p3
                    if ask is None or a3 is None or not (0.03 <= ask <= 0.97): continue
                    if fair - ask >= 0.20 and (fair - ask) - (f3 - a3) >= 0.03:
                        gm = g if up else (not g)
                        out.append({"t": r[0], "st": st, "prix": ask, "p": fair, "gagne": bool(gm), "pnl": (50 / ask) * ((1 if gm else 0) - ask - FEE(ask))}); fait = True; break
                if fait: break
        return out
    o = ["## 4. Moins d'incertitude fixe dans le modèle : rejeu complet de la règle V2-F avec chaque version", "",
         "Chaque version du modèle refait tout le rejeu : certaines opportunités disparaissent, d'autres apparaissent (cycles différents ou autre moment).", "",
         "| Version du modèle | Trades | Gagnés | Annonce moyenne | Gagne en vrai | Prix moyen | Résultat | Creux max | Pertes de suite max | Jackpots (≥ +200 $) | Cycles en commun avec l'actuel |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    ref = None; QL = ["", "Par quart de la période (mêmes dates pour toutes les versions) et par jour :", "", "| Version | Q1 | Q2 | Q3 | Q4 | Par jour |", "|---|---|---|---|---|---|"]
    for nom, sd in (("modèle enregistré du bot (0,08 %, celui de V2-F)", None), ("reconstruit 0,08 % (contrôle)", 8e-4), ("0,02 %", 2e-4), ("0,01 %", 1e-4)):
        X = rejouer(sd); s = stats(X)
        if ref is None: ref = {t["st"] for t in X}; QQ = sorted(t["t"] for t in X); QQ = [QQ[int(len(QQ) * k / 4)] for k in (1, 2, 3)]
        Q = [sum(t["pnl"] for t in X if sum(t["t"] >= x for x in QQ) == k) for k in range(4)]
        jours = collections.defaultdict(float)
        for t in X: jours[time.strftime("%d.%m", time.gmtime(t["t"] + 7200))] += t["pnl"]
        QL.append(f"| {nom} | " + " | ".join(f0(x) for x in Q) + " | " + " · ".join(f"{k} {f0(v)}" for k, v in sorted(jours.items())) + " |")
        comm = {t["st"] for t in X} & ref
        o.append(f"| {nom} | {s['n']} | {s['g']} | {100 * stt.mean(t['p'] for t in X):.0f} % | {100 * stt.mean(t['gagne'] for t in X):.0f} % | {stt.mean(t['prix'] for t in X):.2f} | **{f0(s['pnl'])}** | "
                 f"{f0(s['creux'])} | {s['smax']} | {sum(1 for t in X if t['pnl'] >= 200)} | {len(comm)} |")
        if sd in (2e-4, 1e-4):
            A = [t for t in X if t["st"] in ref]; N = [t for t in X if t["st"] not in ref]
            o.append(f"| ↳ dont cycles aussi pris par l'actuel / cycles nouveaux | {len(A)} / {len(N)} | {sum(t['gagne'] for t in A)} / {sum(t['gagne'] for t in N)} | | | | {f0(sum(t['pnl'] for t in A))} / {f0(sum(t['pnl'] for t in N))} | | | | |")
    return o + QL + [""]


if __name__ == "__main__":
    main()
