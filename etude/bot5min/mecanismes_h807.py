"""BOT95 — H807–H810 (Pitch, 11.10.2026 19:49) : profondeur, présence au meilleur prix, petits flux, calme. Hors ligne ; fantômes existants
inchangés ; aucun ordre. Période réservée (≥ 13.10) jamais lue. Seuils choisis UNIQUEMENT sur la 1re moitié chronologique des cycles.

Moteur de référence (le même partout) : toutes les 2 s entre 30 s et 270 s du cycle, sur chaque côté, une offre d'achat fictive de 20 $ au meilleur
acheteur (post-only), arrivée après 14 ms, retirée 5 s plus tard (+14 ms). Remplissage simulé contre le carnet enregistré à Dublin, 3 bornes de file
(prudente / centrale / optimiste, comme latence_h766.simuler_maker). Pas de frais maker, ristourne non comptée. Résultat au règlement.
Variables (toutes connues à l'instant de la pose, aucune donnée future) : profondeur au meilleur acheteur, volatilité du milieu sur 30 s,
taille moyenne des transactions des 10 s précédentes, écart vendeur-acheteur, prix.
H807  profondeur devant nous (et priorité hypothétique : 0 / 50 / 100 % de la file affichée devant nous).
H808  part du temps de vie où l'offre est restée au meilleur prix (mesurée après coup : variable de DESCRIPTION, pas de décision).
H809  régime de petites transactions récentes.  H810  filtre « calme + profond » contre le même moteur sans filtre.
Usage : python3 etude/bot5min/mecanismes_h807.py dossier_cycles makers_complet.json → etude/bot5min/resultat_mecanismes_h807.md"""
import json, os, sys, glob, math, time, collections, bisect, itertools
import numpy as np

ICI = os.path.dirname(os.path.abspath(__file__)); RACINE = os.path.abspath(os.path.join(ICI, "..", ".."))
sys.path.insert(0, ICI)
import latence_h766 as LH, queue_race_phase12 as Q
HORS_ECH = 1791849600; SORTIE = os.path.join(ICI, "resultat_mecanismes_h807.md")
BORNES = ("prudente", "centrale", "optimiste"); TAILLE = 20.0; VIE = 5000; LAT = 14
rng = np.random.default_rng(807)


def ic(G, fn, n=1500):
    G = [g for g in G if g]
    if len(G) < 3: return (float("nan"), float("nan"))
    v = []
    for _ in range(n):
        try:
            r = fn([x for i in rng.integers(0, len(G), len(G)) for x in G[i]])
            if r is not None and not math.isnan(r): v.append(r)
        except Exception: pass
    return (float(np.percentile(v, 5)), float(np.percentile(v, 95))) if v else (float("nan"), float("nan"))


def simuler(cy, X, prix, t_arr, t_fin, qty, ahead0):
    """comme LH.simuler_maker mais avec la file devant nous imposée (priorité hypothétique) ; rend {borne: (parts, t1)}"""
    side = 0 if X == "Up" else 1; c = prix if X == "Up" else 1000 - prix
    ahead = {b: ahead0 for b in BORNES}; rem = {b: qty for b in BORNES}; t1 = {b: None for b in BORNES}
    taille = None
    i0 = bisect.bisect_right(cy.T, t_arr); i1 = bisect.bisect_right(cy.T, t_fin); j1 = bisect.bisect_right(cy.trT, t_fin + 60); pris = set()
    def remplir(b, k, t):
        if rem[b] <= 1e-9 or k <= 0: return
        f = min(rem[b], k); rem[b] -= f
        if t1[b] is None: t1[b] = t
    for e in cy.fl[i0:i1]:
        if e[2] == "B":
            nv = dict(e[3] if side == 0 else e[4]).get(c, 0.0); taille = nv
            for b in BORNES: ahead[b] = min(ahead[b], nv)
            continue
        if e[2] == "T":
            cs, cm = Q.cible_trade(e[3], e[4], e[5])
            if cs == side and ((side == 0 and cm < c) or (side == 1 and cm > c)):
                for b in BORNES: remplir(b, e[6], e[0])
            continue
        if e[2] != "P" or e[3] != side or e[4] != c: continue
        z = e[5]; old = taille if taille is not None else z; taille = z
        if z >= old - 1e-9: continue
        d = old - z; tv = 0.0
        for j in range(bisect.bisect_left(cy.trT, e[0] - 5), min(j1, bisect.bisect_right(cy.trT, e[0] + 60))):
            if j in pris: continue
            tt = cy.tr[j]
            if tt[1] == side and tt[2] == c: tv += tt[3]; pris.add(j)
            if tv >= d - 1e-9: break
        tp = min(d, tv); an = d - tp
        for b in BORNES:
            a = ahead[b]
            if b == "centrale" and old > 0: a -= an * (a / old)
            elif b == "optimiste": a -= an
            a -= tp
            if a < 0: remplir(b, -a, e[0]); a = 0.0
            ahead[b] = max(0.0, a)
    return {b: (qty - rem[b], t1[b]) for b in BORNES}


def main():
    dossier = sys.argv[1]; base = json.load(open(sys.argv[2]))
    MARCHES = {int(k): v for k, v in base["marches"].items() if int(k) < HORS_ECH}
    F = {int(os.path.basename(f).split(".")[0]): f for f in glob.glob(os.path.join(dossier, "**", "*.json.gz"), recursive=True)}
    F = {k: v for k, v in sorted(F.items()) if k < HORS_ECH and k in MARCHES}
    cycles = sorted(F); coupe = cycles[len(cycles) // 2]
    OR = []
    for st in cycles:
        try:
            cy = LH.Cycle(F[st]); S = Q.rejouer(cy.C)["serie"]
        except Exception: continue
        if len(S) < 50: continue
        g = MARCHES[st]["gagnant"]
        def bb_x(i, X):
            if X == "Up": return S[i, 1], S[i, 2]
            return (1000 - S[i, 3], S[i, 4]) if not np.isnan(S[i, 3]) else (np.nan, 0)
        def mid_x(t, X):
            i = np.searchsorted(S[:, 0], t, "right") - 1
            if i < 0 or np.isnan(S[i, 1]) or np.isnan(S[i, 3]): return None
            m = (S[i, 1] + S[i, 3]) / 2000; return m if X == "Up" else 1 - m
        grille = [st * 1000 + 30000 + 2000 * k for k in range(121)]
        E = cy.etats([t + LAT for t in grille])
        for t in grille:
            i = np.searchsorted(S[:, 0], t, "right") - 1
            if i < 0 or np.isnan(S[i, 1]) or np.isnan(S[i, 3]): continue
            ecart = S[i, 3] - S[i, 1]
            ms = [mid_x(t - 1000 * k, "Up") for k in range(0, 31, 3)]; ms = [m for m in ms if m is not None]
            vol = float(np.std(ms)) * 100 if len(ms) >= 4 else float("nan")
            j0 = bisect.bisect_left(cy.trT, t - 10000); j1 = bisect.bisect_left(cy.trT, t)
            tr10 = [x[3] * (x[2] / 1000 if x[1] == 1 else 1 - x[2] / 1000) for x in cy.tr[j0:j1]]   # $ approximatifs
            taille10 = float(np.mean(tr10)) if tr10 else 0.0
            L = E[t + LAT]
            for X in ("Up", "Down"):
                b, prof = bb_x(i, X)
                if np.isnan(b) or not (50 <= b <= 950): continue
                prix = int(b); q = TAILLE / (prix / 1000)
                lvl = (L.b if X == "Up" else L.a).get(prix if X == "Up" else 1000 - prix, 0.0) if L else prof
                res = {}
                for frac in (1.0, 0.5, 0.0):
                    res[frac] = simuler(cy, X, prix, t + LAT, t + LAT + VIE, q, lvl * frac)
                # H808 : part du temps où notre prix est le meilleur acheteur pendant la vie de l'offre
                k0 = np.searchsorted(S[:, 0], t + LAT, "right") - 1; k1 = np.searchsorted(S[:, 0], t + LAT + VIE, "right")
                tps = 0.0; au = 0.0
                for k in range(max(k0, 0), k1):
                    a_ = max(S[k, 0], t + LAT); b_ = min(S[k + 1, 0] if k + 1 < len(S) else t + LAT + VIE, t + LAT + VIE)
                    if b_ <= a_: continue
                    bk = bb_x(k, X)[0]; tps += b_ - a_
                    if not np.isnan(bk) and int(bk) <= prix: au += b_ - a_
                win = 1.0 if g == X else 0.0; p = prix / 1000
                mo = {}
                for b in BORNES:
                    qq, t1 = res[1.0][b]
                    mo[b] = {}
                    if qq > 0 and t1:
                        for h in (1, 3, 5, 10):
                            m1 = mid_x(t1 + h * 1000, X)
                            if m1 is not None: mo[b][h] = m1 - p
                OR.append(dict(st=st, X=X, p=p, q=q, prof=prof, vol=vol, taille10=taille10, n10=len(tr10), ecart=ecart / 10, au=au / tps if tps else float("nan"),
                               win=win, res=res, mo=mo, t=(t - st * 1000) / 1000))
    tr = [o for o in OR if o["st"] < coupe]; te = [o for o in OR if o["st"] >= coupe]
    par_cy = lambda X_: list({o["st"]: [m for m in X_ if m["st"] == o["st"]] for o in X_}.values())
    pnl = lambda o, b, frac=1.0: o["res"][frac][b][0] * (o["win"] - o["p"])
    def bilan(X_, b="centrale", frac=1.0):
        if not X_: return None
        n = len(X_); f = [o for o in X_ if o["res"][frac][b][0] > 0]
        q = sum(o["res"][frac][b][0] for o in X_); cap = sum(o["res"][frac][b][0] * o["p"] for o in X_); P = sum(pnl(o, b, frac) for o in X_)
        mo = {}
        for h in (1, 3, 5, 10):
            v = [(o["mo"][b][h], o["res"][1.0][b][0]) for o in f if h in o["mo"].get(b, {})]
            mo[h] = 100 * sum(a * w for a, w in v) / sum(w for a, w in v) if v else float("nan")
        cyc = collections.defaultdict(float)
        for o in X_: cyc[o["st"]] += pnl(o, b, frac)
        cum = np.cumsum([cyc[s] for s in sorted(cyc)]); dd = float(np.max(np.maximum.accumulate(np.concatenate([[0], cum]))[1:] - cum)) if len(cum) else 0.0
        part = np.mean([o["res"][frac][b][0] / o["q"] for o in f]) if f else float("nan")
        c_ = ic(par_cy(X_), lambda z: sum(pnl(o, b, frac) for o in z) / len(z))
        return dict(n=n, nf=len(f), pf=len(f) / n, q=q, P=P, po=P / n, pd=P / cap if cap else float("nan"), mo=mo, dd=dd, part=part, ic=c_)
    o_ = []; w = o_.append
    w("# Bot95 — H807–H810 : profondeur, meilleur prix, petits flux, calme — PRÉLIMINAIRE (hors ligne)\n")
    w(f"Généré le {time.strftime('%d.%m.%Y %H:%M', time.gmtime())} UTC. {len(cycles)} cycles enregistrés à Dublin ; {len(OR)} offres fictives "
      f"(apprentissage {len(tr)} / test {len(te)} ; coupure {time.strftime('%d.%m %H:%M', time.gmtime(coupe))} UTC). Moteur : 20 $ au meilleur acheteur, "
      "toutes les 2 s, vie 5 s, latence 14 ms, 3 bornes de file. Aucun ordre, aucun fantôme modifié.\n")
    ENT = "| Groupe | Offres | Remplies | P&L / offre (c) | P&L / $ immobilisé | Markout 1 / 3 / 5 / 10 s (c) | Fill moyen (part de l'offre) |\n|---|---|---|---|---|---|---|"
    def ligne(nom, X_, b="centrale", frac=1.0):
        r = bilan(X_, b, frac)
        if not r: return
        w(f"| {nom} | {r['n']} | {100 * r['pf']:.0f} % | {100 * r['po']:+.1f} [{100 * r['ic'][0]:+.1f} ; {100 * r['ic'][1]:+.1f}] | {100 * r['pd']:+.1f} % | "
          f"{r['mo'][1]:+.2f} / {r['mo'][3]:+.2f} / {r['mo'][5]:+.2f} / {r['mo'][10]:+.2f} | {100 * r['part']:.0f} % |")
    w("## 1. H807 — Effet de la profondeur et de la place dans la file (tous les cycles, file centrale)\n")
    w(ENT)
    for lo, hi in ((0, 50), (50, 200), (200, 1000), (1000, 1e12)):
        ligne(f"profondeur au meilleur {lo}–{'∞' if hi > 1e9 else hi} parts", [o for o in OR if lo <= o["prof"] < hi])
    w("\n**Priorité hypothétique** (même offre, file devant nous = 100 % / 50 % / 0 % de l'affiché ; 0 % = premier dans la file)\n")
    w(ENT)
    for frac in (1.0, 0.5, 0.0): ligne(f"{int(frac * 100)} % de la file devant nous", OR, "centrale", frac)
    w("\n## 2. H808 — Part du temps passée au meilleur prix (description, mesurée après coup)\n"); w(ENT)
    for lo, hi in ((0, 0.25), (0.25, 0.75), (0.75, 0.999), (0.999, 1.01)):
        ligne(f"au meilleur {int(lo * 100)}–{min(int(hi * 100), 100)} % du temps", [o for o in OR if lo <= o["au"] < hi])
    w("\n## 3. H809 — Régime de petites transactions récentes (10 s avant la pose)\n"); w(ENT)
    for nom, f in (("aucune transaction", lambda o: o["n10"] == 0), ("taille moyenne < 10 $", lambda o: o["n10"] > 0 and o["taille10"] < 10),
                   ("10–50 $", lambda o: 10 <= o["taille10"] < 50), ("≥ 50 $", lambda o: o["taille10"] >= 50)):
        ligne(nom, [o for o in OR if f(o)])
    w("\n## 4. Effet de la volatilité (30 s avant la pose)\n"); w(ENT)
    for lo, hi in ((0, 1), (1, 2), (2, 4), (4, 1e9)):
        ligne(f"volatilité {lo}–{'∞' if hi > 1e8 else hi} c", [o for o in OR if not math.isnan(o["vol"]) and lo <= o["vol"] < hi])
    # H810 : filtres choisis sur l'apprentissage
    w("\n## 5. H810 — Politiques comparées (seuils choisis sur l'apprentissage, mesurés une fois sur le test)\n")
    GR = list(itertools.product((1, 2, 4, 1e9), (0, 100, 300, 1000), (1e9, 50, 10)))
    def filtre(o, v, d, s): return (not math.isnan(o["vol"])) and o["vol"] < v and o["prof"] >= d and (o["taille10"] < s)
    score = lambda X_: sum(pnl(o, "centrale") for o in X_) / max(len(X_), 1) if len(X_) >= 50 else -1e9
    best = max(GR, key=lambda g: score([o for o in tr if filtre(o, *g)]))
    w(f"Grille : volatilité < 1 / 2 / 4 c / sans ; profondeur ≥ 0 / 100 / 300 / 1 000 parts ; taille moyenne récente < 10 / 50 $ / sans ({len(GR)} réglages). "
      f"**Retenu sur l'apprentissage : volatilité < {best[0] if best[0] < 1e8 else '∞'} c, profondeur ≥ {best[1]} parts, taille récente < {best[2] if best[2] < 1e8 else '∞'} $.**\n")
    for titre, X_ in (("TEST (cycles non vus)", te), ("apprentissage", tr)):
        w(f"### {titre}\n")
        w("| Politique | File | Offres | Remplies | P&L / offre (c, IC 90 %) | P&L / $ immobilisé | Markout 1 / 3 / 5 / 10 s | Drawdown ($) | P&L total ($) |\n|---|---|---|---|---|---|---|---|---|")
        for nom, Y in (("moteur sans filtre", X_), ("calme + profond (H810)", [o for o in X_ if filtre(o, *best)]),
                       ("profondeur ≥ 300 seule", [o for o in X_ if o["prof"] >= 300]), ("volatilité < 2 c seule", [o for o in X_ if not math.isnan(o["vol"]) and o["vol"] < 2])):
            for b in BORNES:
                r = bilan(Y, b)
                if not r: continue
                w(f"| {nom} | {b} | {r['n']} | {r['nf']} | {100 * r['po']:+.1f} [{100 * r['ic'][0]:+.1f} ; {100 * r['ic'][1]:+.1f}] | {100 * r['pd']:+.1f} % | "
                  f"{r['mo'][1]:+.2f} / {r['mo'][3]:+.2f} / {r['mo'][5]:+.2f} / {r['mo'][10]:+.2f} | {r['dd']:.0f} | {r['P']:+.0f} |")
        w("")
    # robustesse : effet du filtre sur le test, IC par cycles (différence par offre du moteur sans filtre restreint à ce qu'il garde)
    w("## 6. Robustesse\n")
    for b in BORNES:
        keep = [o for o in te if filtre(o, *best)]; drop = [o for o in te if not filtre(o, *best)]
        ck = ic(par_cy(keep), lambda z: sum(pnl(o, b) for o in z) / len(z)); cd = ic(par_cy(drop), lambda z: sum(pnl(o, b) for o in z) / len(z))
        w(f"- File {b} (test) : offres gardées par le filtre {100 * sum(pnl(o, b) for o in keep) / max(len(keep), 1):+.2f} c/offre [{100 * ck[0]:+.2f} ; {100 * ck[1]:+.2f}] "
          f"contre offres écartées {100 * sum(pnl(o, b) for o in drop) / max(len(drop), 1):+.2f} c/offre [{100 * cd[0]:+.2f} ; {100 * cd[1]:+.2f}].")
    w("\nLecture : un mécanisme exploitable doit (1) rester positif sur le test, (2) avec un IC par cycles au-dessus de 0, (3) sous la file prudente aussi. "
      "Sinon, simple corrélation historique.\n")
    w("## Limites\n- Une journée, ~80 cycles.\n- Carnet suivi à ±3 c du meilleur prix ; fills datés au premier fill pour les markouts.\n"
      "- Les offres fictives n'agissent pas sur le carnet ; la priorité « 0 % devant » est hypothétique (il faudrait être là avant les autres).\n")
    open(SORTIE, "w").write("\n".join(o_)); print("\n".join(o_))


if __name__ == "__main__":
    main()
