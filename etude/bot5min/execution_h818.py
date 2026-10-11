"""BOT95 — H818 : sélection adverse et qualité des exécutions (Pitch, 11.10.2026 21:42). Hors ligne ; aucun ordre ; R4, H816, fantômes inchangés ;
période réservée (≥ 13.10) jamais lue. PROTOCOLE VERSIONNÉ AVANT CALCUL (ce fichier tel que committé).

Référence = décisions H816 (prix 0,20–0,50, prix filtré d'abord, premier signal par cycle et côté, 20 $, 164 ms, pas de relance, conservation).
Univers de contrôle = mêmes règles sans filtre de prix (« tous les signaux accessibles »).
Données : carnets enregistrés à Dublin (niveaux de prix, pas d'identifiants d'ordres → on mesure la PRÉSENCE D'UN NIVEAU DE PRIX, pas l'âge d'un
ordre ; un niveau présent depuis la dernière photo complète a un âge seulement minoré, signalé « ≥ »).
H818-B groupes A (exécuté entièrement ≥ 95 % de la mise) / B (partiel) / C (rien : l'offre au prix a disparu avant 164 ms) / D (rien : autre raison).
       Rendement réalisé pour A/B ; rendement CONTREFACTUEL (non réalisable, au prix a0 pour 20 $) pour C/D, toujours séparé.
H818-C présence du niveau au prix a0 (0–50 / 50–150 / 150–500 / > 500 ms).
H818-F offres disparues contre restées (contrôle prix, temps restant, côté).
H818-H markouts après remplissage à 0,1 / 0,25 / 0,5 / 1 / 3 / 10 s contre P&L final.
H818-I filtre de survie : P(exécution | infos à la décision) × E(P&L | exécution), appris sur la 1re moitié, mesuré sur la 2e.
H818-J latence 164 / 200 / 250 / 500 ms sur les mêmes signaux.   H818-K taille 5 / 10 / 20 / 50 / 100 $.
Usage : python3 etude/bot5min/execution_h818.py dossier_cycles → etude/bot5min/resultat_execution_h818.md"""
import json, os, sys, glob, math, time, collections, bisect
import numpy as np

ICI = os.path.dirname(os.path.abspath(__file__)); RACINE = os.path.abspath(os.path.join(ICI, "..", ".."))
sys.path.insert(0, ICI)
import latence_h766 as LH, modele_dublin as MD, queue_race_phase12 as Q, contreparties_h724 as CH
HORS_ECH = 1791849600; SORTIE = os.path.join(ICI, "resultat_execution_h818.md")
MISE = 20.0; EXEC = 164; DELAIS = (164, 200, 250, 500); TAILLES = (5, 10, 20, 50, 100); MO = (100, 250, 500, 1000, 3000, 10000)
fee = lambda p: 0.07 * p * (1 - p)
rng = np.random.default_rng(818)


def acheter(L, X, lim, mise):
    q = c = 0.0
    for p, sz in LH.vendeurs(L, X):
        if p > lim: break
        pp = p / 1000; u = pp + fee(pp); k = min(sz, (mise - c) / u)
        if k <= 1e-9: break
        q += k; c += k * u
    return q, c


def ic(G, fn, n=2000):
    G = [g for g in G if g]
    if len(G) < 3: return (float("nan"), float("nan"))
    v = []
    for _ in range(n):
        try:
            r = fn([x for i in rng.integers(0, len(G), len(G)) for x in G[i]])
            if r is not None and not math.isnan(r): v.append(r)
        except Exception: pass
    return (float(np.percentile(v, 5)), float(np.percentile(v, 95))) if v else (float("nan"), float("nan"))


def presence_niveau(cy, side, c, t):
    """durée depuis la dernière apparition du niveau (side, c) avant t ; (ms, minoré ?)"""
    i1 = bisect.bisect_right(cy.T, t); vu = None; mino = False; present = False
    for e in cy.fl[:i1]:
        if e[2] == "B":
            lv = dict(e[3] if side == 0 else e[4]); z = lv.get(c, 0.0)
            if z > 0 and not present: vu = e[0]; mino = True
            present = z > 0
            if not present: vu = None
        elif e[2] == "P" and e[3] == side and e[4] == c:
            if e[5] > 0 and not present: vu = e[0]; mino = False; present = True
            elif e[5] <= 0: present = False; vu = None
    return ((t - vu) if (present and vu is not None) else None), mino


def main():
    dossier = sys.argv[1]
    F = {int(os.path.basename(f).split(".")[0]): f for f in glob.glob(os.path.join(dossier, "**", "*.json.gz"), recursive=True)}
    F = {k: v for k, v in F.items() if k < HORS_ECH}
    SIG = sorted([s for s in json.load(open(os.path.join(RACINE, "bot95", "rapide.json")))["signaux"] if s.get("gagnant") and s["start"] in F and s["start"] < HORS_ECH],
                 key=lambda s: (s["start"], s["cote"], s["tDecision"], s["nom"]))
    def uniques(L):
        D = {}
        for s in L: D.setdefault((s["start"], s["cote"]), s)
        return list(D.values())
    H816 = {id(s) for s in uniques([s for s in SIG if 0.20 - 1e-9 <= s["a0"] <= 0.50 + 1e-9])}
    TOUS = uniques(SIG)
    ENS = {id(s): s for s in TOUS}; ENS.update({id(s): s for s in SIG if id(s) in H816})
    cycles = sorted({s["start"] for s in ENS.values()}); coupe = cycles[len(cycles) // 2]
    R = []
    for st in cycles:
        cy = LH.Cycle(F[st]); S_ = Q.rejouer(cy.C)["serie"]; ex = MD.charger_ex([F[st]])
        def mid_x(t, X):
            i = np.searchsorted(S_[:, 0], t, "right") - 1
            if i < 0 or np.isnan(S_[i, 1]) or np.isnan(S_[i, 3]): return None
            m = (S_[i, 1] + S_[i, 3]) / 2000; return m if X == "Up" else 1 - m
        def mv(src, a, b, X):
            T, P = ex[src]
            i = bisect.bisect_right(T * 1000, a) - 1; j = bisect.bisect_right(T * 1000, b) - 1
            if i < 0 or j < 0: return None
            return (1 if X == "Up" else -1) * (P[j] - P[i]) / P[i] * 1e4
        for s in [x for x in ENS.values() if x["start"] == st]:
            t0 = s["tDecision"]; X = s["cote"]; a0m = int(round(s["a0"] * 1000)); y = 1.0 if s["gagne"] else 0.0
            inst = [t0, t0 + EXEC] + [t0 + d for d in DELAIS] + [t0 + EXEC + m for m in MO]
            E = cy.etats(inst)
            q0 = sum(sz for p, sz in LH.vendeurs(E[t0], X) if p <= a0m)
            ex_ = {d: acheter(E[t0 + d], X, a0m, MISE) for d in DELAIS}
            taille = {m: acheter(E[t0 + EXEC], X, a0m, m) for m in TAILLES}
            q, c = ex_[EXEC]
            grp = "A" if c >= 0.95 * MISE else ("B" if q > 0 else ("C" if q0 > 0 else "D"))
            # annulations / transactions entre t0 et t0+164 au niveau ≤ a0 de notre côté
            side = 1 if X == "Up" else 0; lims = (lambda cc: cc <= a0m) if X == "Up" else (lambda cc: cc >= 1000 - a0m)
            L0 = E[t0]; taille_niv = dict(L0.a if side == 1 else L0.b) if L0 else {}; bais = 0.0
            for e in cy.fl[bisect.bisect_right(cy.T, t0):bisect.bisect_right(cy.T, t0 + EXEC)]:
                if e[2] == "P" and e[3] == side and lims(e[4]):
                    old = taille_niv.get(e[4], 0.0); taille_niv[e[4]] = e[5]
                    if e[5] < old: bais += old - e[5]
            trv = sum(x[3] for x in cy.tr[bisect.bisect_right(cy.trT, t0):bisect.bisect_right(cy.trT, t0 + EXEC + 60)] if x[1] == side and lims(x[2]))
            cons = min(bais, trv); annul = bais - cons
            age, mino = presence_niveau(cy, side, a0m if X == "Up" else 1000 - a0m, t0)
            bb = LH.acheteurs(L0, X) if L0 else []; aa = LH.vendeurs(L0, X) if L0 else []
            prof_b = sum(sz for p, sz in bb[:3]); prof_a = sum(sz for p, sz in aa[:3])
            mos = {}
            if q > 0:
                pm = c / q
                for m in MO:
                    v = mid_x(t0 + EXEC + m, X)
                    if v is not None: mos[m] = v - (c - q * fee(pm)) / q
            apres = {k: (mid_x(t0 + EXEC + k, X) - s["a0"]) if mid_x(t0 + EXEC + k, X) is not None else None for k in (1000, 5000)}
            R.append(dict(s=s, st=st, X=X, y=y, a0=s["a0"], h816=id(s) in H816, tous=id(s) in {id(x) for x in TOUS}, q=q, c=c, grp=grp, q0=q0,
                          q0d=q0 * s["a0"], ex=ex_, taille=taille, bais=bais, cons=cons, annul=annul, age=age, mino=mino, prof_b=prof_b, prof_a=prof_a,
                          mos=mos, apres=apres, rest=s["restant_s"], decl=s["declencheur"], ecart=s["ecart"],
                          mv={k: mv(k, t0 - 1000, t0, X) for k in ("bn", "perp", "okx", "cl")}, mvl={k: mv(k, t0, t0 + EXEC, X) for k in ("bn", "perp", "okx", "cl")}))
    o = []; w = o.append
    par_cy = lambda X_: list({x["st"]: [m for m in X_ if m["st"] == x["st"]] for x in X_}.values())
    rr = lambda x, d=EXEC: x["ex"][d][0] * x["y"] - x["ex"][d][1]
    cf = lambda x: (MISE / (x["a0"] + fee(x["a0"]))) * x["y"] - MISE                          # contrefactuel 20 $ au prix a0 (NON réalisable si non exécuté)
    w("# Bot95 — H818 : sélection adverse et qualité des exécutions — PRÉLIMINAIRE (hors ligne)\n")
    w(f"Généré le {time.strftime('%d.%m.%Y %H:%M', time.gmtime())} UTC. Cycles Dublin : {len(cycles)} ; décisions H816 : {sum(x['h816'] for x in R)} ; "
      f"décisions « tous signaux » (mêmes règles, sans filtre de prix) : {sum(x['tous'] for x in R)}. Apprentissage < {time.strftime('%H:%M', time.gmtime(coupe))} UTC, test après. "
      "Aucun ordre ; R4, H816, fantômes inchangés.\n")
    w("## 0. Données manquantes (avant toute conclusion)\n- Identifiants d'ordres : absents → âge d'un ORDRE non mesurable ; on mesure la durée de présence du NIVEAU de prix.\n"
      "- Carnet suivi à ±3 c du meilleur prix entre deux photos complètes (10 s) ; niveaux présents depuis une photo : durée minorée.\n"
      "- Prix des bourses : une valeur par 50 ms. Mouvements signés dans le sens du billet acheté (+ = favorable), en points de base.\n"
      "- Une seule journée ; échantillons petits : les IC par cycles sont larges.\n")
    for nom_u, filt in (("H816", lambda x: x["h816"]), ("tous signaux", lambda x: x["tous"])):
        U = [x for x in R if filt(x)]
        w(f"## 1. H818-B — Groupes d'exécution ({nom_u}, 164 ms, 20 $)\n")
        w("| Groupe | Signaux | Taux de gain | Prix | Réalisé : P&L ($) | Réalisé par $ | Contrefactuel NON réalisable par $ (20 $ au prix a0) | Mouv. Binance 1 s avant (pb) | Mouv. Binance pendant 164 ms (pb) | Annulations / baisse au prix |\n|---|---|---|---|---|---|---|---|---|---|")
        for g, lab in (("A", "A — exécuté entièrement"), ("B", "B — partiel"), ("C", "C — offre disparue"), ("D", "D — autre raison")):
            G_ = [x for x in U if x["grp"] == g]
            if not G_: w(f"| {lab} | 0 | | | | | | | | |"); continue
            real = sum(rr(x) for x in G_); eng = sum(x["c"] for x in G_)
            mb = [x["mv"]["bn"] for x in G_ if x["mv"]["bn"] is not None]; ml = [x["mvl"]["bn"] for x in G_ if x["mvl"]["bn"] is not None]
            an = sum(x["annul"] for x in G_); ba = sum(x["bais"] for x in G_)
            w(f"| {lab} | {len(G_)} | {100 * np.mean([x['y'] for x in G_]):.0f} % | {np.mean([x['a0'] for x in G_]):.2f} | "
              f"{real:+.0f} | {100 * real / eng if eng else float('nan'):+.0f} % | {100 * np.mean([cf(x) for x in G_]) / MISE:+.0f} % (non réalisable) | "
              f"{np.median(mb) if mb else float('nan'):+.2f} | {np.median(ml) if ml else float('nan'):+.2f} | {100 * an / ba if ba else 0:.0f} % |")
        w("")
    U = [x for x in R if x["h816"]]; T_ = [x for x in R if x["tous"]]
    # ===== C
    w("## 2. H818-C — Présence du niveau de prix a0 au moment de la décision (tous signaux)\n")
    w("| Présence du niveau | Signaux | dont minorée | Survie à 164 ms | Taux de remplissage complet | Rendement si rempli | Rendement par signal envoyé | Annulations / baisse | Volume accessible ($) |\n|---|---|---|---|---|---|---|---|---|")
    for lo, hi in ((0, 50), (50, 150), (150, 500), (500, 1e12)):
        G_ = [x for x in T_ if x["age"] is not None and lo <= x["age"] < hi]
        if not G_: continue
        rem = [x for x in G_ if x["q"] > 0]; eng = sum(x["c"] for x in rem)
        w(f"| {lo}–{'∞' if hi > 1e9 else hi} ms | {len(G_)} | {sum(x['mino'] for x in G_)} | {100 * np.mean([x['q'] > 0 for x in G_]):.0f} % | {100 * np.mean([x['grp'] == 'A' for x in G_]):.0f} % | "
          f"{100 * sum(rr(x) for x in rem) / eng if eng else float('nan'):+.0f} % | {np.mean([rr(x) for x in G_]):+.2f} $ | "
          f"{100 * sum(x['annul'] for x in G_) / max(sum(x['bais'] for x in G_), 1e-9):.0f} % | {np.median([x['q0d'] for x in G_]):.0f} |")
    w(f"\nSans niveau au prix a0 au moment de la décision (offre déjà partie / signal sur une offre absente) : {sum(1 for x in T_ if x['age'] is None)} signaux.\n")
    # ===== F
    w("## 3. H818-F — Offres disparues contre offres restées (tous signaux)\n")
    dis = [x for x in T_ if x["q0"] > 0 and x["ex"][EXEC][0] < 0.5 * min(x["q0"], MISE / x["a0"])]; res = [x for x in T_ if x["q0"] > 0 and x not in dis]
    w("| Groupe | Signaux | Taux de gain | Prix | Rendement théorique au prix a0 | Rendement exécutable | Milieu +1 s − a0 | +5 s | Cause : annulation | Profondeur acheteurs / vendeurs (3 niveaux) |\n|---|---|---|---|---|---|---|---|---|---|")
    for nom, G_ in (("disparues", dis), ("restées", res)):
        eng = sum(x["c"] for x in G_)
        a1 = [x["apres"][1000] for x in G_ if x["apres"][1000] is not None]; a5 = [x["apres"][5000] for x in G_ if x["apres"][5000] is not None]
        w(f"| {nom} | {len(G_)} | {100 * np.mean([x['y'] for x in G_]):.0f} % | {np.mean([x['a0'] for x in G_]):.2f} | {100 * np.mean([cf(x) for x in G_]) / MISE:+.0f} % | "
          f"{100 * sum(rr(x) for x in G_) / eng if eng else float('nan'):+.0f} % | {100 * np.median(a1) if a1 else float('nan'):+.1f} c | {100 * np.median(a5) if a5 else float('nan'):+.1f} c | "
          f"{100 * sum(x['annul'] for x in G_) / max(sum(x['bais'] for x in G_), 1e-9):.0f} % | {np.median([x['prof_b'] for x in G_]):.0f} / {np.median([x['prof_a'] for x in G_]):.0f} |")
    # régression contrôlée : gagne − prix ~ disparue + prix + temps restant + côté
    Z = dis + res
    if len(Z) > 20:
        Xm = np.array([[1.0, 1.0 if x in dis else 0.0, x["a0"], x["rest"] / 300, 1.0 if x["X"] == "Up" else 0.0] for x in Z]); ym = np.array([x["y"] - x["a0"] for x in Z])
        b = np.linalg.lstsq(Xm, ym, rcond=None)[0]
        G = par_cy(Z); bs = []
        idx = {id(x): i for i, x in enumerate(Z)}
        for _ in range(1000):
            ii = [idx[id(x)] for k in rng.integers(0, len(G), len(G)) for x in G[k]]
            bs.append(np.linalg.lstsq(Xm[ii], ym[ii], rcond=None)[0][1])
        w(f"\nÀ prix, temps restant et côté égaux : écart (gain − prix) disparues − restées = {100 * b[1]:+.1f} points [IC 90 % {100 * np.percentile(bs, 5):+.1f} ; {100 * np.percentile(bs, 95):+.1f}].\n")
    # ===== H
    w("## 4. H818-H — Markouts après remplissage (tous signaux exécutés, c par part, milieu du côté acheté − prix payé hors frais)\n")
    rem = [x for x in T_ if x["q"] > 0]
    w("| Groupe | Remplis | " + " | ".join(f"+{m} ms" for m in MO) + " | P&L final par part |\n|---|---|" + "---|" * len(MO) + "---|")
    for nom, G_ in (("tous", rem), ("gagnants au règlement", [x for x in rem if x["y"] == 1]), ("perdants au règlement", [x for x in rem if x["y"] == 0])):
        cells = []
        for m in MO:
            v = [(x["mos"][m], x["q"]) for x in G_ if m in x["mos"]]
            cells.append(f"{100 * sum(a * b for a, b in v) / sum(b for a, b in v):+.1f}" if v else "—")
        w(f"| {nom} | {len(G_)} | " + " | ".join(cells) + f" | {100 * sum(rr(x) for x in G_) / max(sum(x['q'] for x in G_), 1e-9):+.1f} |")
    m3 = [(x["mos"].get(3000), x) for x in rem if 3000 in x["mos"]]
    if m3:
        neg = [x for v, x in m3 if v < 0]; pos_ = [x for v, x in m3 if v >= 0]
        w(f"\nMarkout à 3 s négatif : {len(neg)} remplissages, gain au règlement {100 * np.mean([x['y'] for x in neg]) if neg else float('nan'):.0f} % ; "
          f"positif ou nul : {len(pos_)}, gain {100 * np.mean([x['y'] for x in pos_]) if pos_ else float('nan'):.0f} %.\n")
    # ===== I : filtre de survie
    w("## 5. H818-I — Filtre de survie : P(exécution) × E(P&L | exécution)\n")
    feats = lambda x: [math.log1p(x["q0d"]), 0.0 if x["age"] is None else math.log1p(x["age"]), 1.0 if x["decl"] == "poly" else 0.0, x["ecart"], x["a0"], x["rest"] / 300,
                       0.0 if x["mv"]["bn"] is None else max(-20, min(20, x["mv"]["bn"]))]
    tr = [x for x in T_ if x["st"] < coupe]; te = [x for x in T_ if x["st"] >= coupe]
    if len(tr) > 15 and len(te) > 10:
        Xt = np.array([feats(x) for x in tr]); m_ = Xt.mean(0); sd_ = Xt.std(0); sd_[sd_ == 0] = 1
        b_ex = CH.ajuster((Xt - m_) / sd_, np.array([1.0 if x["q"] > 0 else 0.0 for x in tr]), 1.0)
        rem_tr = [x for x in tr if x["q"] > 0]
        Xr = np.array([feats(x) for x in rem_tr]); yr = np.array([rr(x) / max(x["c"], 1e-9) for x in rem_tr])
        b_pl = np.linalg.lstsq(np.column_stack([np.ones(len(Xr)), (Xr - m_) / sd_]), yr, rcond=None)[0] if len(rem_tr) > 8 else None
        def ev(x):
            z = (np.array(feats(x)) - m_) / sd_; pe = CH.predire(b_ex, z[None, :])[0]
            pl = float(np.concatenate([[1.0], z]) @ b_pl) if b_pl is not None else 0.0
            return pe * pl * MISE, pe
        for x in T_: x["ev"], x["pe"] = ev(x)
        w(f"Modèles appris sur {len(tr)} signaux (apprentissage) ; appliqués aux {len(te)} signaux du test. Règle : envoyer seulement si valeur attendue > 0.\n")
        w("| Politique (test) | Signaux envoyés | Exécutés | P&L ($) | par signal (IC 90 %) | par $ engagé | sans les 5 meilleurs |\n|---|---|---|---|---|---|---|")
        for nom, sel in (("H816 inchangé", lambda x: x["h816"]), ("tous signaux sans filtre", lambda x: True), ("H818 filtré (EV > 0)", lambda x: x["ev"] > 0)):
            G_ = [x for x in te if sel(x)]
            if not G_: continue
            pn = sorted([rr(x) for x in G_], reverse=True); eng = sum(x["c"] for x in G_)
            c_ = ic(par_cy(G_), lambda z: float(np.mean([rr(x) for x in z])))
            w(f"| {nom} | {len(G_)} | {sum(1 for x in G_ if x['q'] > 0)} | {sum(pn):+.0f} | {np.mean(pn):+.2f} [{c_[0]:+.2f} ; {c_[1]:+.2f}] | "
              f"{100 * sum(pn) / eng if eng else float('nan'):+.0f} % | {sum(pn[5:]):+.0f} |")
        pe_te = np.array([x["pe"] for x in te]); ex_te = np.array([1.0 if x["q"] > 0 else 0.0 for x in te])
        w(f"\nQualité du modèle de survie sur le test : AUC {CH_auc(pe_te, ex_te):.2f} (exécuté ou non).\n")
    # ===== J
    w("## 6. H818-J — Prix de la latence (mêmes signaux initiaux, tous signaux)\n")
    w("| Délai | Remplis | Taux de gain des remplis | Taux de gain des NON remplis | P&L ($) | par signal (IC 90 %) | par $ engagé | Opportunités perdues (non remplis gagnants) |\n|---|---|---|---|---|---|---|---|")
    for d in DELAIS:
        rem_ = [x for x in T_ if x["ex"][d][0] > 0]; non = [x for x in T_ if x["ex"][d][0] <= 0]
        eng = sum(x["ex"][d][1] for x in T_); P = sum(rr(x, d) for x in T_)
        c_ = ic(par_cy(T_), lambda z, d=d: float(np.mean([rr(x, d) for x in z])))
        w(f"| {d} ms | {len(rem_)} / {len(T_)} | {100 * np.mean([x['y'] for x in rem_]) if rem_ else float('nan'):.0f} % | {100 * np.mean([x['y'] for x in non]) if non else float('nan'):.0f} % | "
          f"{P:+.0f} | {P / len(T_):+.2f} [{c_[0]:+.2f} ; {c_[1]:+.2f}] | {100 * P / eng if eng else float('nan'):+.0f} % | {sum(1 for x in non if x['y'] == 1)} |")
    # ===== K
    w("\n## 7. H818-K — Taille (164 ms, tous signaux)\n")
    w("| Mise visée | Parts | Prix moyen payé (frais compris) | Frais ($) | Capital réellement engagé ($) | P&L ($) | Rendement par $ |\n|---|---|---|---|---|---|---|")
    for m in TAILLES:
        qq = sum(x["taille"][m][0] for x in T_); cc = sum(x["taille"][m][1] for x in T_)
        P = sum(x["taille"][m][0] * x["y"] - x["taille"][m][1] for x in T_)
        fr = sum(x["taille"][m][0] * fee(x["taille"][m][1] / x["taille"][m][0]) for x in T_ if x["taille"][m][0] > 0)
        w(f"| {m} $ | {qq:.0f} | {cc / qq if qq else float('nan'):.3f} | {fr:.1f} | {cc:.0f} | {P:+.0f} | {100 * P / cc if cc else float('nan'):+.1f} % |")
    w("\n## 8. Critère de décision\n- Une modification de Bot95 n'est proposée que si un filtre améliore le P&L net sur le TEST avec un IC par cycles > 0, après coûts et exécution réaliste.\n")
    open(SORTIE, "w").write("\n".join(o)); print("\n".join(o))


def CH_auc(s, y):
    P = s[y == 1]; N = s[y == 0]
    if not len(P) or not len(N): return float("nan")
    return float(np.mean([(p > n) + 0.5 * (p == n) for p in P for n in N]))


if __name__ == "__main__":
    main()
