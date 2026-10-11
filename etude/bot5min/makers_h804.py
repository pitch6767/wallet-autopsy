"""BOT95 — H804 / H805 / H806 (Pitch, 11.10.2026 19:03). Hors ligne uniquement ; aucun bot ni fantôme modifié ; aucun ordre ; période réservée non lue.
H804  M21 contre M1 / M4 (et M6, M8 pour contexte) sur les MÊMES cycles, mêmes hypothèses d'exécution (enregistrements vivants de Dublin) :
      ordres tentés, fills, parts, P&L par ordre / par part, drawdown, capital immobilisé, IC par cycles ; pourquoi M1 / M21 > 0 par part.
H805  Achats maker à 0,95–0,99 selon le temps restant (30–15 / 15–5 / 5–0 s) : 595 marchés complets (fills observés de tous les makers) +
      simulation sur les cycles de Dublin d'une offre au meilleur acheteur ≥ 0,95 (fills obtenus / NON obtenus, 3 bornes de file).
H806  Sélection des fills : makers réels (fills datés à la ms via Dublin) contre nos fantômes, à conditions égales (prix, temps restant,
      meilleur prix, taille du preneur, profondeur, volatilité, flux agressif) ; markouts et résultat ; aucune identité de wallet utilisée.
Usage : python3 etude/bot5min/makers_h804.py makers_complet.json dossier_cycles → etude/bot5min/resultat_makers_h804.md"""
import json, os, sys, glob, math, time, collections, bisect, ast
import numpy as np

ICI = os.path.dirname(os.path.abspath(__file__)); RACINE = os.path.abspath(os.path.join(ICI, "..", ".."))
sys.path.insert(0, ICI)
import latence_h766 as LH, fast_fenetre as FF, queue_race_phase12 as Q
HORS_ECH = 1791849600; SORTIE = os.path.join(ICI, "resultat_makers_h804.md")
rng = np.random.default_rng(804)
mil = lambda p: int(round(p * 1000))


def ic(G, fn, n=2000):
    G = [g for g in G if g]
    if len(G) < 3: return (float("nan"), float("nan"))
    v = []
    for _ in range(n):
        try: v.append(fn([x for i in rng.integers(0, len(G), len(G)) for x in G[i]]))
        except Exception: pass
    return (float(np.percentile(v, 5)), float(np.percentile(v, 95))) if v else (float("nan"), float("nan"))


def lit(v):
    if isinstance(v, str):
        try: return ast.literal_eval(v)
        except Exception:
            try: return float(v)
            except Exception: return v
    return v


def cp_haut(k, n, a=0.05):
    """borne haute unilatérale 95 % de Clopper-Pearson (k pertes sur n)"""
    if n == 0: return float("nan")
    lo, hi = k / n, 1.0
    from math import comb
    def cdf(p): return sum(comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(0, k + 1)) if n <= 400 else None
    if n > 400:                                    # approximation (règle de trois / Wilson) pour les grands n
        z = 1.645; ph = k / n; return min(1.0, (ph + z * z / (2 * n) + z * math.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n))) / (1 + z * z / n))
    for _ in range(60):
        m = (lo + hi) / 2
        if cdf(m) > a: lo = m
        else: hi = m
    return hi


def main():
    base = json.load(open(sys.argv[1])); dossier = sys.argv[2]
    MARCHES = {int(k): v for k, v in base["marches"].items() if int(k) < HORS_ECH}
    MK = []
    for x in json.load(open(os.path.join(RACINE, "bot95", "rapide_maker.json"))):
        if x.get("type") == "resume": continue
        x = {k: lit(v) for k, v in x.items()}
        if not x.get("resultat") or int(x["start"]) >= HORS_ECH or x.get("mode") == "preneur": continue
        x["start"] = int(x["start"]); MK.append(x)
    fam = lambda x: x["variante"].split()[0]
    o = []; w = o.append
    w("# Bot95 — H804 / H805 / H806 — PRÉLIMINAIRE (hors ligne)\n")
    w(f"Généré le {time.strftime('%d.%m.%Y %H:%M', time.gmtime())} UTC. Fantômes maker vivants de Dublin : {len(MK)} ordres réglés "
      f"({time.strftime('%d.%m %H:%M', time.gmtime(min(x['start'] for x in MK)))} → {time.strftime('%H:%M', time.gmtime(max(x['start'] for x in MK)))} UTC). "
      f"Marchés complets lus : {sum(1 for v in MARCHES.values() if not v.get('tronque'))}. Aucun ordre, aucun réglage modifié.\n")

    # ================= H804
    w("## 1. H804 — M21 contre M1 / M4 (mêmes cycles, mêmes hypothèses d'exécution)\n")
    FAM = ["M1", "M21", "M4", "M6", "M8"]
    par = {f: [x for x in MK if fam(x) == f] for f in FAM}
    communs = set.intersection(*[{x["start"] for x in par[f]} for f in ("M1", "M21", "M4")]) if all(par[f] for f in ("M1", "M21", "M4")) else set()
    w(f"Cycles où M1, M21 et M4 ont tous coté : **{len(communs)}**. Fills « prudents » (seules les transactions font avancer la file) et « proportionnels ». "
      "Résultat au règlement, sans frais maker, ristourne non comptée. Capital immobilisé = parts remplies × prix.\n")
    w("| Moteur | Ordres tentés | Ordres remplis (prudent) | Parts (prudent / prop.) | P&L prudent ($) | P&L prop. ($) | par ordre tenté | par part | IC 90 % par cycle (prudent) | Drawdown (prudent) | Capital immobilisé moyen / max par cycle |\n|---|---|---|---|---|---|---|---|---|---|---|")
    RES = {}
    for f in FAM:
        X = [x for x in par[f] if x["start"] in communs]
        if not X: continue
        pp = sum(x["resultat"]["prudent"] for x in X); pr = sum(x["resultat"]["proportionnel"] for x in X)
        qp = sum(x.get("remplP") or 0 for x in X); qr = sum(x.get("remplR") or 0 for x in X)
        cyc = collections.defaultdict(float); capc = collections.defaultdict(float)
        for x in X: cyc[x["start"]] += x["resultat"]["prudent"]; capc[x["start"]] += (x.get("remplP") or 0) * x["prix"]
        ser = [cyc[s] for s in sorted(cyc)]; cum = np.cumsum(ser); dd = float(np.max(np.maximum.accumulate(np.concatenate([[0], cum]))[1:] - cum))
        c_ = ic([[v] for v in cyc.values()], lambda z: float(np.mean(z)))
        RES[f] = X
        w(f"| {f} | {len(X)} | {sum(1 for x in X if (x.get('remplP') or 0) > 0)} | {qp:.0f} / {qr:.0f} | {pp:+.0f} | {pr:+.0f} | {pp / len(X):+.2f} | {100 * pp / qp if qp else 0:+.1f} c | "
          f"[{c_[0]:+.1f} ; {c_[1]:+.1f}] $/cycle | {dd:.0f} | {np.mean(list(capc.values())):.0f} / {max(capc.values()):.0f} $ |")
    # pourquoi : caractéristiques des fills
    w("\n**Pourquoi M1 / M21 gagnent par part et pas M4 / M6 / M8 — caractéristiques des ordres remplis (prudent, cycles communs)**\n")
    w("| Moteur | Prix moyen payé | Part sur le favori (> 0,5) | Temps restant médian à la pose | Taux de gain des fills | Gain − prix (c/part) | Markout +1 s / +5 s / +10 s (c/part) | Écart modèle − prix à la pose (c) | Fills sous condition toxique |\n|---|---|---|---|---|---|---|---|---|")
    for f, X in RES.items():
        F_ = [x for x in X if (x.get("remplP") or 0) > 0]
        if not F_: continue
        q = np.array([x["remplP"] for x in F_]); p = np.array([x["prix"] for x in F_]); g = np.array([1.0 if x.get("gagne") else 0.0 for x in F_])
        mo = {}
        for h in ("1", "5", "10"):
            v = [(x.get("mo") or {}).get("p", {}).get(h) for x in F_]; v = [a for a in v if a and a[1]]
            mo[h] = 100 * sum(a[0] for a in v) / sum(a[1] for a in v) if v else float("nan")
        mod = [100 * (x["modele"] - x["prix"]) for x in F_ if isinstance(x.get("modele"), (int, float))]
        tox = [t for x in F_ for t in (x.get("toxRempl") or []) if isinstance(t, (list, tuple))]
        w(f"| {f} | {np.average(p, weights=q):.3f} | {100 * np.average(p > 0.5, weights=q):.0f} % | {np.median([x.get('restantPose_s') or 0 for x in F_]):.0f} s | "
          f"{100 * np.average(g, weights=q):.0f} % | {100 * np.average(g - p, weights=q):+.1f} | {mo['1']:+.1f} / {mo['5']:+.1f} / {mo['10']:+.1f} | "
          f"{np.median(mod) if mod else float('nan'):+.1f} | {100 * sum(t[0] for t in tox if t[1]) / max(sum(t[0] for t in tox), 1e-9):.0f} % des parts |")
    w("\n**Résultat par part selon le prix payé (prudent, cycles communs)**\n\n| Moteur | < 0,30 | 0,30–0,50 | 0,50–0,70 | 0,70–0,90 | ≥ 0,90 |\n|---|---|---|---|---|---|")
    for f, X in RES.items():
        cells = []
        for lo, hi in ((0, .3), (.3, .5), (.5, .7), (.7, .9), (.9, 1.01)):
            F_ = [x for x in X if (x.get("remplP") or 0) > 0 and lo <= x["prix"] < hi]
            q = sum(x["remplP"] for x in F_)
            cells.append(f"{100 * sum(x['resultat']['prudent'] for x in F_) / q:+.1f} c ({q:.0f} p.)" if q else "—")
        w(f"| {f} | " + " | ".join(cells) + " |")
    w("")

    # ================= H805
    w("## 2. H805 — Achats maker à 0,95–0,99 selon le temps restant\n")
    w("**A. Fills observés de tous les makers (595 marchés complets).** Retournement = le côté acheté perd. Borne haute 95 % du taux de perte : Clopper-Pearson "
      "(zéro perte observée ne veut pas dire zéro risque). Markout = prix du côté à la transaction suivante ≥ 5 s plus tard (API, à la seconde) − prix payé.\n")
    w("| Prix | Fenêtre | Fills | Marchés | Fills perdants | Taux de perte | Borne haute 95 % | Seuil de rentabilité | Résultat | Plus grosse perte (1 fill) | Plus grosse perte (1 marché) | Markout +5 s (c) |\n|---|---|---|---|---|---|---|---|---|---|---|---|")
    TR = {}
    for st, mk in MARCHES.items():
        if mk.get("tronque"): continue
        T = sorted((x[6], x[2], x[5]) for x in mk["ex"] if x[1] == "P"); TR[st] = (T, [t[0] for t in T])
    A = collections.defaultdict(lambda: dict(n=0, l=0, r=0.0, pm=0.0, mk=collections.defaultdict(float), m=set(), mo=[], q=0.0))
    for st, mk in MARCHES.items():
        if mk.get("tronque"): continue
        g = mk["gagnant"]; T, TT = TR[st]
        for wl, role, out, side, sz, p, ts in mk["ex"]:
            if role != "M" or side != "BUY" or not (0.95 <= p < 1.0) or not (270 <= ts - st < 300): continue
            b = "0,95–0,97" if p < 0.97 else ("0,97–0,98" if p < 0.98 else ("0,98–0,99" if p < 0.99 else "≥ 0,99"))
            fen = "30–15 s" if ts - st < 285 else ("15–5 s" if ts - st < 295 else "5–0 s")
            win = out == g; x = A[(b, fen)]; x["n"] += 1; x["l"] += (not win); r = sz * ((1.0 if win else 0.0) - p); x["r"] += r; x["m"].add(st); x["q"] += sz
            x["pm"] = min(x["pm"], r); x["mk"][st] += r
            i = bisect.bisect_left(TT, ts + 5)
            if i < len(T):
                _, o2, p2 = T[i]; px = p2 if o2 == out else 1 - p2; x["mo"].append((sz, px - p))
    for b in ("0,95–0,97", "0,97–0,98", "0,98–0,99", "≥ 0,99"):
        for fen in ("30–15 s", "15–5 s", "5–0 s"):
            x = A.get((b, fen))
            if not x or not x["n"]: continue
            mo = 100 * sum(s * d for s, d in x["mo"]) / sum(s for s, _ in x["mo"]) if x["mo"] else float("nan")
            seuil = {"0,95–0,97": "≈ 4 %", "0,97–0,98": "≈ 2,5 %", "0,98–0,99": "≈ 1,5 %", "≥ 0,99": "≈ 0,7 %"}[b]
            w(f"| {b} | {fen} | {x['n']} | {len(x['m'])} | {x['l']} | {100 * x['l'] / x['n']:.2f} % | {100 * cp_haut(x['l'], x['n']):.2f} % | {seuil} | {x['r']:+.0f} $ | "
              f"{x['pm']:+.0f} $ | {min(x['mk'].values()):+.0f} $ | {mo:+.2f} |")
    w("\nNote : le taux de perte est compté par fill ; plusieurs fills du même marché perdent ensemble (un retournement touche tout le monde). "
      "Le nombre de marchés retournés est la vraie unité de risque.\n")
    # B. simulation Dublin : fills obtenus / non obtenus
    w("**B. Simulation sur les cycles de Dublin : offre d'achat posée au meilleur acheteur du favori si celui-ci est entre 0,95 et 0,99, à 30 / 15 / 5 s "
      "de la fin, gardée jusqu'à la fin (100 parts).** Montre combien de ces offres auraient été remplies (le reste = fills non obtenus).\n")
    F = {int(os.path.basename(f).split(".")[0]): f for f in glob.glob(os.path.join(dossier, "**", "*.json.gz"), recursive=True)}
    F = {k: v for k, v in F.items() if k < HORS_ECH and k in MARCHES}
    SIM = collections.defaultdict(lambda: {b: [0, 0, 0.0, 0, 0.0] for b in LH.BORNES})   # n offres, remplies, parts, perdantes, résultat
    for st in sorted(F):
        try: cy = LH.Cycle(F[st])
        except Exception: continue
        g = MARCHES[st]["gagnant"]
        for rest in (30, 15, 5):
            t = (st + 300 - rest) * 1000; L = cy.etats([t + 14])[t + 14]
            if L is None: continue
            for X in ("Up", "Down"):
                bb = LH.acheteurs(L, X)
                if not bb or not (950 <= bb[0][0] <= 990): continue
                prix = bb[0][0]; res = LH.simuler_maker(cy, X, prix, t + 14, (st + 300) * 1000, 100.0, L)
                key = f"{rest} s"; win = 1.0 if g == X else 0.0
                for b, (q, t1) in res.items():
                    s_ = SIM[key][b]; s_[0] += 1; s_[1] += (q > 0); s_[2] += q; s_[3] += (q > 0 and win == 0); s_[4] += q * (win - prix / 1000)
    w("| Pose à | File | Offres posées | Remplies | Taux de fill | Parts | Perdantes | Résultat ($) |\n|---|---|---|---|---|---|---|---|")
    for key in ("30 s", "15 s", "5 s"):
        for b in LH.BORNES:
            s_ = SIM[key][b]
            if s_[0]: w(f"| {key} avant la fin | {b} | {s_[0]} | {s_[1]} | {100 * s_[1] / s_[0]:.0f} % | {s_[2]:.0f} | {s_[3]} | {s_[4]:+.0f} |")
    w("")

    # ================= H806
    w("## 3. H806 — Sélection des fills : makers réels contre nos fantômes à conditions égales\n")
    REM = []; NOS = []
    for st in sorted(F):
        try:
            cy = LH.Cycle(F[st]); Rj = Q.rejouer(cy.C); S = Rj["serie"]
        except Exception: continue
        if len(S) < 10: continue
        mk = MARCHES[st]; g = mk["gagnant"]
        def mid_up(t):
            i = np.searchsorted(S[:, 0], t, "right") - 1
            if i < 0 or np.isnan(S[i, 1]) or np.isnan(S[i, 3]): return None
            return (S[i, 1] + S[i, 3]) / 2000
        def contexte(t, up_long, prix_up):
            i = np.searchsorted(S[:, 0], t, "left") - 1
            if i < 0: return None
            bb, bq, ba, aq = S[i, 1] / 1000, S[i, 2], S[i, 3] / 1000, S[i, 4]
            prof = bq if up_long else aq                                     # taille affichée au meilleur prix de notre côté
            au_meilleur = abs(prix_up - (bb if up_long else ba)) < 0.0051
            j0 = bisect.bisect_left(cy.trT, t - 2000); j1 = bisect.bisect_left(cy.trT, t)
            # flux agressif CONTRE nous dans les 2 s : preneurs qui vendent notre côté (consomment le côté acheteur où nous sommes)
            flux = sum(x[3] for x in cy.tr[j0:j1] if x[1] == (0 if up_long else 1))
            m30 = [mid_up(t - k * 1000) for k in range(0, 31, 5)]; m30 = [m for m in m30 if m is not None]
            vol = float(np.std(m30)) * 100 if len(m30) >= 3 else float("nan")
            return dict(au_meilleur=au_meilleur, prof=prof, flux=flux, vol=vol, ecart=(ba - bb) * 100 if ba and bb else float("nan"))
        def mark(t, up_long, prix_up):
            out = {}
            for h in (1, 5):
                m1 = mid_up(t + h * 1000)
                if m1 is not None: out[h] = (m1 - prix_up) if up_long else (prix_up - m1)
            out["regl"] = ((1.0 if g == "Up" else 0.0) - prix_up) if up_long else (prix_up - (1.0 if g == "Up" else 0.0))
            return out
        IDX = collections.defaultdict(list)
        for tt in Rj["trades"]:
            if tt[1] is not None: IDX[(int(tt[1] // 1000), tt[2], tt[3], tt[4])].append(tt)
        par_ts = collections.defaultdict(list)
        for x in mk["ex"]: par_ts[x[6]].append(x)
        for ts, Lx in par_ts.items():
            pren = [x for x in Lx if x[1] == "P"]; mak = [x for x in Lx if x[1] == "M"]
            for wl, role, out, side, sz, p, _ in pren:
                tok = 0 if out == "Up" else 1; sd = 1 if side == "BUY" else 0
                cand = [tt for d in (0, -1, 1) for tt in IDX.get((ts + d, tok, sd, mil(p)), []) if abs(tt[5] - sz) <= 0.02 * max(1.0, sz)]
                if not cand: continue
                tR = cand[0][0]
                for mw, _, mout, mside, msz, mp, _ in mak:
                    if not ((mout == out and mside != side and abs(mp - p) < 1e-9) or (mout != out and mside == side and abs(mp - (1 - p)) < 1e-9)): continue
                    if mside != "BUY": continue                              # comme nos fantômes : achats seulement
                    up_long = mout == "Up"; prix_up = mp if up_long else 1 - mp
                    c = contexte(tR, up_long, prix_up)
                    if c is None: continue
                    REM.append(dict(q=msz, prix=mp, t=tR / 1000 - st, taille=sz * p, mo=mark(tR, up_long, prix_up), st=st, **c))
        for x in MK:
            if x["start"] != st: continue
            rl = x.get("rempl") or []
            for ms, k, q in rl:
                if k != "p" or q <= 0: continue
                t = (x.get("tArrivee") or x["tPose"]) + ms; up_long = x["cote"] == "Up"; prix_up = x["prix"] if up_long else 1 - x["prix"]
                c = contexte(t, up_long, prix_up)
                if c is None: continue
                NOS.append(dict(q=q, prix=x["prix"], t=t / 1000 - st, taille=float("nan"), mo=mark(t, up_long, prix_up), st=st, fam=fam(x), **c))
    w(f"Fills de makers réels datés à la ms (achats) : {len(REM)} ; fills prudents de nos fantômes : {len(NOS)} ; mêmes cycles Dublin.\n")
    def moy(X_, h):
        v = [(x["mo"][h], x["q"]) for x in X_ if h in x["mo"]]
        return 100 * sum(a * b for a, b in v) / sum(b for a, b in v) if v else float("nan")
    # comparaison brute puis à conditions égales (repondération des makers réels sur la distribution prix × minute de nos fills)
    strate = lambda x: (min(int(x["prix"] * 10), 9), min(max(int(x["t"] // 60), 0), 4))
    def apparie(R_, N_, h):
        cR = collections.defaultdict(list)
        for x in R_: cR[strate(x)].append(x)
        num = den = 0.0
        for x in N_:
            Z = cR.get(strate(x))
            if not Z or h not in x["mo"]: continue
            m = moy(Z, h)
            if not math.isnan(m): num += x["q"] * m; den += x["q"]
        return num / den if den else float("nan")
    w("| Groupe | Fills | Markout +1 s (c) | +5 s (c) | Règlement (c/part) | Makers réels à prix × minute identiques : +1 s / +5 s / règlement |\n|---|---|---|---|---|---|")
    w(f"| makers réels (tous) | {len(REM)} | {moy(REM, 1):+.2f} | {moy(REM, 5):+.2f} | {moy(REM, 'regl'):+.2f} | — |")
    for f in sorted({x["fam"] for x in NOS}):
        N_ = [x for x in NOS if x["fam"] == f]
        if len(N_) < 20: continue
        w(f"| nous {f} | {len(N_)} | {moy(N_, 1):+.2f} | {moy(N_, 5):+.2f} | {moy(N_, 'regl'):+.2f} | {apparie(REM, N_, 1):+.2f} / {apparie(REM, N_, 5):+.2f} / {apparie(REM, N_, 'regl'):+.2f} |")
    # mécanismes reproductibles : conditions au fill
    w("\n**Conditions au moment du fill** (médianes ; proportions)\n")
    w("| Groupe | Au meilleur prix | Taille du preneur < 10 $ | Profondeur à notre niveau (parts) | Flux vendeur 2 s avant (parts) | Volatilité 30 s (c) | Écart vendeur-acheteur (c) |\n|---|---|---|---|---|---|---|")
    def ligne(nom, X_):
        if not X_: return
        tl = [x["taille"] for x in X_ if not math.isnan(x["taille"])]
        w(f"| {nom} | {100 * np.mean([x['au_meilleur'] for x in X_]):.0f} % | {100 * np.mean([t < 10 for t in tl]) if tl else float('nan'):.0f} % | "
          f"{np.median([x['prof'] for x in X_]):.0f} | {np.median([x['flux'] for x in X_]):.0f} | {np.nanmedian([x['vol'] for x in X_]):.2f} | {np.nanmedian([x['ecart'] for x in X_]):.1f} |")
    ligne("makers réels", REM); ligne("nous (tous fantômes)", NOS)
    for f in ("M1", "M21", "M4", "M6", "M8"): ligne(f"nous {f}", [x for x in NOS if x["fam"] == f])
    w("\n**Markout +5 s selon chaque condition (makers réels | nos fantômes)** — un mécanisme reproductible doit montrer le même effet chez les deux\n")
    w("| Condition | Makers réels : oui / non | Fantômes : oui / non |\n|---|---|---|")
    CONDS = [("au meilleur prix", lambda x: x["au_meilleur"]), ("flux vendeur 2 s avant = 0", lambda x: x["flux"] <= 0),
             ("profondeur ≥ 100 parts", lambda x: x["prof"] >= 100), ("volatilité 30 s < 1 c", lambda x: not math.isnan(x["vol"]) and x["vol"] < 1),
             ("écart vendeur-acheteur = 1 c", lambda x: not math.isnan(x["ecart"]) and x["ecart"] <= 1.05), ("prix ≥ 0,50 (favori)", lambda x: x["prix"] >= 0.5)]
    for nom, f in CONDS:
        a = [x for x in REM if f(x)]; b = [x for x in REM if not f(x)]; c = [x for x in NOS if f(x)]; d = [x for x in NOS if not f(x)]
        w(f"| {nom} | {moy(a, 5):+.2f} ({len(a)}) / {moy(b, 5):+.2f} ({len(b)}) | {moy(c, 5):+.2f} ({len(c)}) / {moy(d, 5):+.2f} ({len(d)}) |")
    # régression commune : markout +5 s ~ fantôme + conditions (l'écart « fantôme » restant = ce que les conditions n'expliquent pas)
    ALL = [(x, 0.0) for x in REM if 5 in x["mo"]] + [(x, 1.0) for x in NOS if 5 in x["mo"]]
    def X_(x, fa):
        return [fa, float(x["au_meilleur"]), float(x["flux"] <= 0), math.log1p(x["prof"]), 0.0 if math.isnan(x["vol"]) else x["vol"],
                0.0 if math.isnan(x["ecart"]) else x["ecart"], x["prix"], x["t"] / 300]
    if len(ALL) > 50:
        Xm = np.array([X_(x, fa) for x, fa in ALL]); ym = np.array([100 * x["mo"][5] for x, _ in ALL]); wm = np.array([min(x["q"], 200) for x, _ in ALL])
        def fit(idx):
            Xa = np.column_stack([np.ones(len(idx)), Xm[idx]]); W = np.sqrt(wm[idx])
            return np.linalg.lstsq(Xa * W[:, None], ym[idx] * W, rcond=None)[0]
        b0 = fit(np.arange(len(ALL)))
        cyc = collections.defaultdict(list)
        for i, (x, _) in enumerate(ALL): cyc[x["st"]].append(i)
        G = list(cyc.values()); bs = []
        for _ in range(300):
            idx = np.array([i for k in rng.integers(0, len(G), len(G)) for i in G[k]]); bs.append(fit(idx))
        bs = np.array(bs); noms = ["fantôme (vs maker réel)", "au meilleur prix", "aucun flux vendeur 2 s avant", "log profondeur", "volatilité 30 s", "écart vendeur-acheteur", "prix", "moment du cycle"]
        w("\n**Régression commune du markout +5 s (c/part), IC 90 % par cycles**\n\n| Variable | Coefficient | IC 90 % |\n|---|---|---|")
        for i, n_ in enumerate(noms): w(f"| {n_} | {b0[i + 1]:+.2f} | [{np.percentile(bs[:, i + 1], 5):+.2f} ; {np.percentile(bs[:, i + 1], 95):+.2f}] |")
        bnc = fit(np.arange(len(ALL)))
        brut = moy(NOS, 5) - moy(REM, 5)
        w(f"\nÉcart brut fantômes − makers réels au markout +5 s : {brut:+.2f} c ; écart restant après conditions : {b0[1]:+.2f} c.\n")
    w("## Limites\n- Une journée ; fantômes vivants depuis le 11.10 vers 11 h UTC seulement.\n- Fills réels : seuls ceux rapprochés d'une transaction Dublin à la ms sont datés.\n"
      "- On ne voit jamais les ordres réels posés puis annulés (fills non obtenus des makers réels inconnus) ; la partie B de H805 les simule pour nous.\n")
    open(SORTIE, "w").write("\n".join(o)); print("\n".join(o))


if __name__ == "__main__":
    main()
