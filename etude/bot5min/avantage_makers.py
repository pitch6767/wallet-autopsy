"""BOT95 — H687 / H718 : D'OÙ VIENT L'AVANTAGE DES MAKERS GAGNANTS ? Demande de Pitch, 11.10.2026 16:18 (« trouver leurs avantages, leurs façons de faire »).
Lecture seule, hors ligne, aucun ordre, aucun fantôme modifié ; période réservée (≥ 13.10.2026 00:00 UTC) exclue.
Pour chaque remplissage maker (position LONGUE prise sur un côté X au prix p) :
  - prix payé contre le prix du marché juste avant (dernière transaction preneuse sur X) et juste après (+10 / +30 / +60 s) ;
  - côté favori ou outsider ; moment du cycle ; taille ;
  - gestion du stock : le remplissage RÉÉQUILIBRE-t-il le portefeuille (achat du côté où il est court) ou CHARGE-t-il le côté déjà surpondéré ?
  - sur les cycles enregistrés à Dublin : VALEUR FONDAMENTALE approchée du côté X à l'instant du remplissage (bourses + Chainlink + prix à battre),
    et mouvement du BTC contre X dans les 3 s avant (remplissage « en retard » sur l'information).
Puis : gagnants contre perdants (classés sur la 1re moitié chronologique, mesurés sur la 2e), et attribution de l'écart de résultat par poste.
FAITS : exécutions, prix, transactions. APPROCHÉ : valeur fondamentale (modèle simple, documenté). INFÉRENCE : l'interprétation.
Usage : python3 etude/bot5min/avantage_makers.py makers_suivi.json dossier_cycles → etude/bot5min/resultat_avantage_makers.md"""
import json, os, sys, glob, gzip, bisect, collections, time, math
import numpy as np

ICI = os.path.dirname(os.path.abspath(__file__)); SORTIE = os.path.join(ICI, "resultat_avantage_makers.md"); HORS_ECH = 1791849600
PHI = lambda x: 0.5 * (1 + math.erf(x / math.sqrt(2)))


def fondamental_dublin(dossier, starts):
    """par cycle Dublin : fonction t (s) → (proba Up approchée, mouvement BTC sur 3 s) à partir des prix reçus AVANT t"""
    F = {}
    for fn in glob.glob(os.path.join(dossier, "**", "*.json.gz"), recursive=True):
        st = int(os.path.basename(fn).split(".")[0])
        if st not in starts: continue
        R = json.load(gzip.open(fn)); strike = (R.get("marche") or {}).get("strike")
        if not strike: continue
        T, X, CL = [], [], []
        for r in R.get("ex", []):
            px = [r[k][0] for k in (1, 2, 3, 4) if r[k]]
            if not px: continue
            T.append(r[0] / 1000); X.append(float(np.median(px))); CL.append(r[5][0] if r[5] else np.nan)
        if len(T) < 100: continue
        F[st] = (np.array(T), np.array(X), np.array(CL), strike)
    return F


def proba_up(F, st, t):
    T, X, CL, strike = F[st]
    i = np.searchsorted(T, t, "right") - 1
    if i < 50: return None, None
    j0 = np.searchsorted(T, t - 60); base = np.nanmedian(X[j0:i + 1] - CL[j0:i + 1])     # écart bourses − Chainlink des 60 dernières secondes
    if np.isnan(base): return None, None
    S = X[i] - base
    k0 = np.searchsorted(T, t - 300); seg = X[k0:i + 1]; tt = T[k0:i + 1]
    if len(seg) < 30: return None, None
    # volatilité par seconde (rendements sur pas de 1 s rééchantillonnés)
    grid = np.arange(tt[0], tt[-1], 1.0); xs = np.interp(grid, tt, seg); r = np.diff(np.log(xs))
    sig = float(np.std(r)) if len(r) > 10 else None
    if not sig: return None, None
    fin = st + 300; deb = fin - 60
    if t >= deb:                                                           # dernière minute : moyenne en partie connue (Chainlink reçu)
        jd = np.searchsorted(T, deb); connu = CL[jd:i + 1]; connu = connu[~np.isnan(connu)]
        nr = max(1.0, fin - t); n_c = max(1, int(t - deb))
        E = (np.mean(connu) * n_c + nr * S) / (n_c + nr) if len(connu) else S
        v = (sig * S) ** 2 * nr ** 3 / 3 / 3600
    else:
        E = S; v = (sig * S) ** 2 * ((deb - t) + 20)
    pu = PHI((E - strike) / math.sqrt(v + (1.5e-4 * S) ** 2))
    j3 = np.searchsorted(T, t - 3); mv = X[i] - X[j3] if j3 < i else 0.0
    return pu, mv


def main():
    base = json.load(open(sys.argv[1])); dossier = sys.argv[2] if len(sys.argv) > 2 else None
    M = {int(k): v for k, v in base["marches"].items() if int(k) < HORS_ECH and not v.get("tronque")}
    starts = sorted(M); coupe = starts[len(starts) // 2]
    # classement (1re moitié)
    vol = collections.Counter(); volM = collections.Counter(); pnl = collections.Counter(); nm = collections.defaultdict(set)
    for st in starts:
        if st >= coupe: continue
        g = M[st]["gagnant"]
        for w, role, out, side, sz, p, ts in M[st]["ex"]:
            win = 1.0 if out == g else 0.0; vol[w] += sz * p; nm[w].add(st)
            if role == "M": volM[w] += sz * p
            pnl[w] += sz * (win - p) if side == "BUY" else sz * (p - win)
    makers = [w for w in volM if len(nm[w]) >= 10 and volM[w] >= 0.7 * vol[w] and vol[w] >= 2500]
    G = {w for w in makers if pnl[w] / vol[w] >= 0.01}; P = {w for w in makers if pnl[w] / vol[w] <= -0.005}
    F = fondamental_dublin(dossier, set(starts)) if dossier else {}
    R = []
    for st in starts:
        if st < coupe: continue
        mk = M[st]; g = mk["gagnant"]
        tp = sorted((x[6], x[2], x[5]) for x in mk["ex"] if x[1] == "P")           # transactions preneuses (prix par issue)
        T = [x[0] for x in tp]
        def prix_x(out, t, avant=True):
            i = bisect.bisect_left(T, t) - 1 if avant else bisect.bisect_right(T, t)
            rng = range(i, -1, -1) if avant else range(i, len(tp))
            for k in rng:
                if 0 <= k < len(tp):
                    ts, o, p = tp[k]
                    if (avant and ts >= t) or (not avant and ts < t): continue
                    return p if o == out else 1 - p
            return None
        inv = collections.defaultdict(lambda: {"Up": 0.0, "Down": 0.0})
        for w, role, out, side, sz, p, ts in sorted(mk["ex"], key=lambda x: x[6]):
            # côté LONG pris et prix équivalent (vendre X à p = acheter l'autre à 1 − p)
            if side == "BUY": X_, px = out, p
            else: X_, px = ("Down" if out == "Up" else "Up"), 1 - p
            I = inv[w]; avant_tilt = I["Up"] - I["Down"]
            if side == "BUY": I[out] += sz
            else: I[out] -= sz
            if role != "M" or w not in makers: continue
            grp = "gagnants" if w in G else ("perdants" if w in P else "autres")
            win = 1.0 if g == X_ else 0.0
            pa = prix_x(X_, ts, True); p10 = prix_x(X_, ts + 10, True); p60 = prix_x(X_, ts + 60, True)
            reeq = (avant_tilt > 0 and X_ == "Down") or (avant_tilt < 0 and X_ == "Up")
            charge = (avant_tilt > 0 and X_ == "Up") or (avant_tilt < 0 and X_ == "Down")
            fav = pa is not None and pa > 0.5
            d = dict(grp=grp, q=sz, px=px, gain=sz * (win - px), t=ts - st, fav=fav, reeq=reeq, charge=charge,
                     avant=(px - pa) if pa is not None else None, d10=(p10 - px) if p10 is not None else None, d60=(p60 - px) if p60 is not None else None)
            if st in F:
                pu, mv = proba_up(F, st, ts + 0.5)
                if pu is not None:
                    fx = pu if X_ == "Up" else 1 - pu
                    d["fond"] = fx - px; d["contre"] = (mv < -5) if X_ == "Up" else (mv > 5)
            R.append(d)
    o = []; w_ = o.append
    w_("# Bot95 — D'où vient l'avantage des makers gagnants ? (H687, H718) — PRÉLIMINAIRE\n")
    w_(f"Généré le {time.strftime('%d.%m.%Y %H:%M', time.gmtime())} UTC. {len(starts)} marchés complets ; gagnants / perdants classés sur la 1re moitié (avant le "
       f"{time.strftime('%d.%m %H:%M', time.gmtime(coupe))} UTC), comportements mesurés sur la 2e moitié : {sum(1 for x in R if x['grp'] == 'gagnants')} remplissages de {len(G)} gagnants, "
       f"{sum(1 for x in R if x['grp'] == 'perdants')} de {len(P)} perdants. Valeur fondamentale approchée sur {len(F)} cycles enregistrés à Dublin.\n")

    def ligne(nom, X):
        if not X: return f"| {nom} | 0 | — | — | — | — | — |"
        q = sum(x["q"] for x in X); g = sum(x["gain"] for x in X); cap = sum(x["q"] * x["px"] for x in X)
        a = [x for x in X if x["d10"] is not None]; b = [x for x in X if x["d60"] is not None]
        return (f"| {nom} | {len(X)} | {q:.0f} | {g:+.0f} $ | {100 * g / cap if cap else 0:+.1f} % | "
                f"{100 * sum(x['q'] * x['d10'] for x in a) / max(sum(x['q'] for x in a), 1e-9):+.2f} | {100 * sum(x['q'] * x['d60'] for x in b) / max(sum(x['q'] for x in b), 1e-9):+.2f} |")
    for titre, f in (("Ensemble", None), ("Côté acheté : favori (> 0,5) ou outsider", "fav"), ("Gestion du stock : rééquilibre (achète le côté court) / charge (achète le côté déjà long)", "stock"),
                     ("Moment du cycle", "t"), ("Prix payé", "px")):
        w_(f"## {titre}\n")
        w_("| Groupe | Remplissages | Parts | Résultat au règlement | par $ | Prix du côté +10 s − prix payé (c) | +60 s (c) |\n|---|---|---|---|---|---|---|")
        for grp in ("gagnants", "perdants"):
            X = [x for x in R if x["grp"] == grp]
            if f is None: w_(ligne(grp, X))
            elif f == "fav":
                w_(ligne(grp + " — favori", [x for x in X if x["fav"]])); w_(ligne(grp + " — outsider", [x for x in X if not x["fav"]]))
            elif f == "stock":
                w_(ligne(grp + " — rééquilibre", [x for x in X if x["reeq"]])); w_(ligne(grp + " — charge", [x for x in X if x["charge"]])); w_(ligne(grp + " — 1er achat (stock nul)", [x for x in X if not x["reeq"] and not x["charge"]]))
            elif f == "t":
                for lo, hi in ((0, 60), (60, 120), (120, 180), (180, 240), (240, 300)): w_(ligne(f"{grp} — {lo}–{hi} s", [x for x in X if lo <= x["t"] < hi]))
            elif f == "px":
                for lo, hi in ((0, .1), (.1, .3), (.3, .5), (.5, .7), (.7, .9), (.9, 1.01)): w_(ligne(f"{grp} — {lo:.1f}–{min(hi, 1):.1f}", [x for x in X if lo <= x["px"] < hi]))
        w_("")
    # mix des comportements
    w_("## Répartition des comportements (part des parts remplies)\n")
    w_("| Groupe | Favori | Rééquilibre | Charge | 0–60 s | 240–300 s | Prix médian | Taille médiane |\n|---|---|---|---|---|---|---|---|")
    for grp in ("gagnants", "perdants"):
        X = [x for x in R if x["grp"] == grp]; q = sum(x["q"] for x in X) or 1
        sh = lambda c: 100 * sum(x["q"] for x in X if c(x)) / q
        w_(f"| {grp} | {sh(lambda x: x['fav']):.0f} % | {sh(lambda x: x['reeq']):.0f} % | {sh(lambda x: x['charge']):.0f} % | {sh(lambda x: x['t'] < 60):.0f} % | {sh(lambda x: x['t'] >= 240):.0f} % | "
           f"{np.median([x['px'] for x in X]) if X else float('nan'):.2f} | {np.median([x['q'] for x in X]) if X else float('nan'):.1f} |")
    # valeur fondamentale (Dublin)
    w_("\n## Prix payé contre la valeur fondamentale approchée (cycles Dublin)\n")
    w_("Valeur fondamentale = probabilité de règlement calculée avec les bourses et Chainlink reçus AVANT le remplissage (modèle simple : écart au prix à battre, "
       "volatilité des 300 dernières secondes, moyenne de la dernière minute). Positif = le maker a acheté SOUS la valeur.\n")
    w_("| Groupe | Remplissages | Valeur − prix payé (c, moyenne pondérée) | Part achetée sous la valeur | Remplissages juste après un mouvement BTC contre lui (> 5 $ en 3 s) | Résultat de ces remplissages |\n|---|---|---|---|---|---|")
    for grp in ("gagnants", "perdants", "autres"):
        X = [x for x in R if x["grp"] == grp and "fond" in x]
        if not X: w_(f"| {grp} | 0 | — | — | — | — |"); continue
        q = sum(x["q"] for x in X); c = [x for x in X if x["contre"]]
        w_(f"| {grp} | {len(X)} | {100 * sum(x['q'] * x['fond'] for x in X) / q:+.2f} | {100 * sum(x['q'] for x in X if x['fond'] > 0) / q:.0f} % | "
           f"{len(c)} ({100 * len(c) / len(X):.0f} %) | {sum(x['gain'] for x in c):+.0f} $ |")
    # attribution : effet de répartition contre effet de performance par catégorie (temps × favori)
    w_("\n## Attribution de l'écart gagnants − perdants (par $ engagé)\n")
    def cle(x): return (min(int(x["t"] // 60), 4), x["fav"])
    def tab(grp):
        X = [x for x in R if x["grp"] == grp]; cap = sum(x["q"] * x["px"] for x in X) or 1; D = collections.defaultdict(lambda: [0.0, 0.0])
        for x in X: D[cle(x)][0] += x["q"] * x["px"]; D[cle(x)][1] += x["gain"]
        return {k: (v[0] / cap, v[1] / v[0] if v[0] else 0.0) for k, v in D.items()}, sum(x["gain"] for x in X) / cap
    A, ra = tab("gagnants"); B, rb = tab("perdants")
    rep = sum((A.get(k, (0, 0))[0] - B.get(k, (0, 0))[0]) * B.get(k, (0, 0))[1] for k in set(A) | set(B))
    perf = sum(A.get(k, (0, 0))[0] * (A.get(k, (0, 0))[1] - B.get(k, (0, 0))[1]) for k in set(A) | set(B))
    w_(f"Résultat par $ : gagnants {100 * ra:+.2f} %, perdants {100 * rb:+.2f} %, écart {100 * (ra - rb):+.2f} points. "
       f"Effet de RÉPARTITION (où ils achètent : minute × favori/outsider) {100 * rep:+.2f} points ; effet de PERFORMANCE (mieux dans les mêmes cases) {100 * perf:+.2f} points ; "
       f"résidu {100 * (ra - rb - rep - perf):+.2f} points.\n")
    w_("## Limites\n- Une journée de marchés (2e moitié), makers classés sur la 1re ; la valeur fondamentale est approchée (pas le modèle Bot95 exact).\n"
       "- Les ordres annulés sont invisibles : on ne voit que les remplissages. Résultat sans ristourne maker.\n")
    open(SORTIE, "w").write("\n".join(o)); print("\n".join(o))


if __name__ == "__main__":
    main()
