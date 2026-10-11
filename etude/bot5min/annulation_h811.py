"""BOT95 — H811–H815 (Pitch, 11.10.2026 20:00) : la vitesse d'annulation peut-elle rendre le maker viable ? Hors ligne ; aucun ordre ;
aucun bot ni fantôme modifié ; aucun nouveau fantôme. Période réservée (≥ 13.10) jamais lue.

Mêmes cotations que H807 (mêmes cycles, même budget 20 $, même prix = meilleur acheteur, même vie 5 s, mêmes 3 bornes de file, latence 14 ms).
Avertissements FIXÉS A PRIORI (aucun réglage), observés à Dublin après la pose, uniquement avec des données déjà reçues :
  W1  première transaction vendeuse qui consomme notre côté du carnet au prix de notre offre ou mieux (la file au-dessus / à notre niveau fond)
  W2  le meilleur vendeur de notre côté baisse par rapport à la pose (le prix vient vers nous)
  W3  Binance bouge contre notre côté d'au moins 1 point de base en 300 ms
  W   = le premier des trois
Politique « annuler à d ms » : l'annulation prend effet à (avertissement + d) ; d = délai total réception → effet chez Polymarket
(10, 25, 50, 100, 200 ms ; le trajet simple Dublin → Polymarket est ≈ 14 ms, donc 10 ms est physiquement hors d'atteinte).
Fill toxique = milieu de notre côté 5 s après le premier fill < prix − 1 c ; bon fill = ≥ prix.
H813 : annuler puis reposer 500 ms après au meilleur acheteur du moment, en fin de file, jusqu'à la fin de vie initiale.
Usage : python3 etude/bot5min/annulation_h811.py dossier_cycles makers_complet.json → etude/bot5min/resultat_annulation_h811.md"""
import json, os, sys, glob, math, time, collections, bisect
import numpy as np

ICI = os.path.dirname(os.path.abspath(__file__)); RACINE = os.path.abspath(os.path.join(ICI, "..", ".."))
sys.path.insert(0, ICI)
import latence_h766 as LH, queue_race_phase12 as Q, modele_dublin as MD, mecanismes_h807 as MH
HORS_ECH = 1791849600; SORTIE = os.path.join(ICI, "resultat_annulation_h811.md")
BORNES = MH.BORNES; TAILLE = 20.0; VIE = 5000; LAT = 14; DELAIS = (10, 25, 50, 100, 200)
rng = np.random.default_rng(811)


def ic(G, fn, n=1500):
    G = [g for g in G if g]
    if len(G) < 3: return (float("nan"), float("nan"))
    v = []
    for _ in range(n):
        try: v.append(fn([x for i in rng.integers(0, len(G), len(G)) for x in G[i]]))
        except Exception: pass
    return (float(np.percentile(v, 5)), float(np.percentile(v, 95))) if v else (float("nan"), float("nan"))


def ic_moy(X_, f, n=2000):
    """IC 90 % de Σf / nombre de cotations, rééchantillonnage de cycles (sommes pré-calculées par cycle)"""
    S_ = collections.defaultdict(lambda: [0.0, 0])
    for o in X_: a = S_[o["st"]]; a[0] += f(o); a[1] += 1
    v = np.array(list(S_.values()))
    if len(v) < 3: return (float("nan"), float("nan"))
    idx = rng.integers(0, len(v), (n, len(v))); r = v[idx, 0].sum(1) / v[idx, 1].sum(1)
    return (float(np.percentile(r, 5)), float(np.percentile(r, 95)))


def main():
    dossier = sys.argv[1]; base = json.load(open(sys.argv[2]))
    MARCHES = {int(k): v for k, v in base["marches"].items() if int(k) < HORS_ECH}
    F = {int(os.path.basename(f).split(".")[0]): f for f in glob.glob(os.path.join(dossier, "**", "*.json.gz"), recursive=True)}
    F = {k: v for k, v in sorted(F.items()) if k < HORS_ECH and k in MARCHES}
    cycles = sorted(F); coupe = cycles[len(cycles) // 2]
    OR = []
    for st in cycles:
        try:
            cy = LH.Cycle(F[st]); S = Q.rejouer(cy.C)["serie"]; ex = MD.charger_ex([F[st]])
        except Exception: continue
        if len(S) < 50: continue
        bnT, bnP = ex["bn"]; bnT = bnT * 1000
        g = MARCHES[st]["gagnant"]
        def bb_x(i, X):
            if X == "Up": return S[i, 1], S[i, 2]
            return (1000 - S[i, 3], S[i, 4]) if not np.isnan(S[i, 3]) else (np.nan, 0)
        def ask_x(i, X):
            return S[i, 3] if X == "Up" else (1000 - S[i, 1] if not np.isnan(S[i, 1]) else np.nan)
        def mid_x(t, X):
            i = np.searchsorted(S[:, 0], t, "right") - 1
            if i < 0 or np.isnan(S[i, 1]) or np.isnan(S[i, 3]): return None
            m = (S[i, 1] + S[i, 3]) / 2000; return m if X == "Up" else 1 - m
        grille = [st * 1000 + 30000 + 2000 * k for k in range(121)]
        E = cy.etats([t + LAT for t in grille])
        for t in grille:
            i = np.searchsorted(S[:, 0], t, "right") - 1
            if i < 0 or np.isnan(S[i, 1]) or np.isnan(S[i, 3]): continue
            L = E[t + LAT]; ta = t + LAT; tf = ta + VIE
            for X in ("Up", "Down"):
                b, prof = bb_x(i, X)
                if np.isnan(b) or not (50 <= b <= 950): continue
                prix = int(b); q = TAILLE / (prix / 1000); side = 0 if X == "Up" else 1; c = prix if X == "Up" else 1000 - prix
                lvl = (L.b if X == "Up" else L.a).get(c, 0.0) if L else prof
                # ---- avertissements (premier instant après l'arrivée)
                w = {}
                j0 = bisect.bisect_right(cy.trT, ta); j1 = bisect.bisect_right(cy.trT, tf)
                for j in range(j0, j1):
                    _, cs, cm, sz = cy.tr[j]
                    if cs == side and ((side == 0 and cm >= c) or (side == 1 and cm <= c)): w["W1"] = cy.tr[j][0]; break
                a0 = ask_x(i, X); k0 = np.searchsorted(S[:, 0], ta, "right"); k1 = np.searchsorted(S[:, 0], tf, "right")
                for k in range(k0, k1):
                    ak = ask_x(k, X)
                    if not np.isnan(ak) and not np.isnan(a0) and ak < a0: w["W2"] = S[k, 0]; break
                m0 = bisect.bisect_right(bnT, ta); m1 = bisect.bisect_right(bnT, tf); sens = 1 if X == "Up" else -1
                for m in range(m0, m1):
                    r = bisect.bisect_right(bnT, bnT[m] - 300) - 1
                    if r >= 0 and sens * (bnP[m] - bnP[r]) / bnP[r] * 1e4 <= -1.0: w["W3"] = bnT[m]; break
                if w: w["W"] = min(w.values())
                garder = MH.simuler(cy, X, prix, ta, tf, q, lvl)
                win = 1.0 if g == X else 0.0; p = prix / 1000
                mo = {}
                for bn in BORNES:
                    qq, t1 = garder[bn]
                    m5 = mid_x(t1 + 5000, X) if qq > 0 and t1 else None
                    mo[bn] = (m5 - p) if m5 is not None else None
                ann = {}
                for cle in ("W", "W1", "W2", "W3"):
                    if cle not in w: continue
                    for d in (DELAIS if cle == "W" else (50,)):
                        tc = w[cle] + d
                        if tc >= tf: continue
                        ann[(cle, d)] = MH.simuler(cy, X, prix, ta, tc, q, lvl)
                repose = None; garde_fen = None
                tr_ = (w["W"] + 50 + 500) if ("W", 50) in ann else None
                OR.append(dict(st=st, X=X, p=p, q=q, win=win, w=w, ta=ta, tf=tf, prix=prix, lvl=lvl, garder=garder, mo=mo, ann=ann, repose=repose, garde_fen=garde_fen,
                               tr_=(tr_ if tr_ is not None and tr_ < tf else None)))
        # H813 en lot (un seul passage sur le carnet pour toutes les reposes du cycle)
        A_ = [o for o in OR if o["st"] == st and o["tr_"]]
        Er = cy.etats([o["tr_"] for o in A_])
        for o in A_:
            Lr = Er[o["tr_"]]; bbr = LH.acheteurs(Lr, o["X"]) if Lr else []
            if not bbr: continue
            pr2 = bbr[0][0]; c2 = pr2 if o["X"] == "Up" else 1000 - pr2
            lv2 = (Lr.b if o["X"] == "Up" else Lr.a).get(c2, 0.0)
            reste = {bn: o["q"] - o["ann"][("W", 50)][bn][0] for bn in BORNES}
            r2 = MH.simuler(cy, o["X"], pr2, o["tr_"], o["tf"], max(reste.values()), lv2)
            o["repose"] = {bn: (min(r2[bn][0], reste[bn]), pr2 / 1000) for bn in BORNES}
            avant = MH.simuler(cy, o["X"], o["prix"], o["ta"], o["tr_"], o["q"], o["lvl"])
            o["garde_fen"] = {bn: o["garder"][bn][0] - avant[bn][0] for bn in BORNES}
    tr = [o for o in OR if o["st"] < coupe]; te = [o for o in OR if o["st"] >= coupe]
    par_cy = lambda X_: list({o["st"]: [m for m in X_ if m["st"] == o["st"]] for o in X_}.values())
    out = []; W_ = out.append
    W_("# Bot95 — H811–H815 : vitesse d'annulation des makers — PRÉLIMINAIRE (hors ligne)\n")
    W_(f"Généré le {time.strftime('%d.%m.%Y %H:%M', time.gmtime())} UTC. {len(cycles)} cycles Dublin ; {len(OR)} cotations (mêmes que H807 : 20 $ au meilleur acheteur, "
       f"vie 5 s, latence 14 ms). Apprentissage / test : {len(tr)} / {len(te)} cotations (coupure {time.strftime('%H:%M', time.gmtime(coupe))} UTC) — aucun paramètre "
       "n'est ajusté, la coupure sert seulement à vérifier la stabilité. Aucun ordre, aucun fantôme touché.\n")

    # ---------------- H811 / H814
    W_("## 1. H811 — Délai entre le premier avertissement et le fill (fills toxiques, file centrale)\n")
    bn = "centrale"
    tox = [o for o in OR if o["garder"][bn][0] > 0 and o["mo"][bn] is not None and o["mo"][bn] <= -0.01]
    bons = [o for o in OR if o["garder"][bn][0] > 0 and o["mo"][bn] is not None and o["mo"][bn] >= 0]
    W_(f"Cotations remplies : {sum(1 for o in OR if o['garder'][bn][0] > 0)} ; fills toxiques (milieu à +5 s ≤ prix − 1 c) : {len(tox)} ; bons fills (≥ prix) : {len(bons)}.\n")
    W_("| Avertissement | Fills toxiques avec avertissement avant le fill | Délai médian avertissement → fill (ms) | p10 / p25 / p75 / p90 | Bons fills avec avertissement avant |\n|---|---|---|---|---|")
    for cle in ("W", "W1", "W2", "W3"):
        dl = [o["garder"][bn][1] - o["w"][cle] for o in tox if cle in o["w"] and o["w"][cle] <= o["garder"][bn][1]]
        db = [1 for o in bons if cle in o["w"] and o["w"][cle] <= o["garder"][bn][1]]
        if dl: W_(f"| {cle} | {len(dl)} / {len(tox)} ({100 * len(dl) / len(tox):.0f} %) | {np.median(dl):.0f} | {np.percentile(dl, 10):.0f} / {np.percentile(dl, 25):.0f} / {np.percentile(dl, 75):.0f} / {np.percentile(dl, 90):.0f} | {len(db)} / {len(bons)} ({100 * len(db) / max(len(bons), 1):.0f} %) |")
    W_("\n## 2. H814 — Part des fills toxiques réellement évitables selon le délai d'annulation (avertissement W)\n")
    W_("Évitable = l'annulation (avertissement + d) prend effet AVANT le premier fill. « Trop tard » = avertissement arrivé, mais fill avant l'effet de l'annulation. "
       "« Sans avertissement » = aucun signe observable avant le fill.\n")
    W_("| Délai d | Toxiques évitables | Trop tard | Sans avertissement avant le fill | Bons fills perdus (annulés avant leur fill) |\n|---|---|---|---|---|")
    for d in DELAIS:
        ev = sum(1 for o in tox if "W" in o["w"] and o["w"]["W"] + d < o["garder"][bn][1])
        tard = sum(1 for o in tox if "W" in o["w"] and o["w"]["W"] <= o["garder"][bn][1] <= o["w"]["W"] + d)
        sans = len(tox) - ev - tard
        bp = sum(1 for o in bons if "W" in o["w"] and o["w"]["W"] + d < o["garder"][bn][1])
        W_(f"| {d} ms{' (hors d’atteinte physique)' if d < 14 else ''} | {ev} ({100 * ev / len(tox):.0f} %) | {tard} ({100 * tard / len(tox):.0f} %) | {sans} ({100 * sans / len(tox):.0f} %) | {bp} / {len(bons)} ({100 * bp / max(len(bons), 1):.0f} %) |")

    # ---------------- H812 / H815
    W_("\n## 3. H812 / H815 — Garder contre annuler, P&L net à chaque délai\n")
    W_("P&L au règlement des parts réellement remplies (même offre, même file) ; P&L « markout » = parts × (milieu à +5 s − prix) pour la file indiquée, "
       "moins bruité. Annuler ne coûte rien (pas de frais), mais fait perdre les bons fills.\n")
    def pnl_regl(o, res, b): return res[b][0] * (o["win"] - o["p"])
    for titre, X_ in (("TOUS LES CYCLES", OR), ("1re moitié", tr), ("2e moitié", te)):
        W_(f"### {titre}\n")
        W_("| Politique | File | Cotations remplies | Parts | P&L règlement / cotation (c) | IC 90 % | Marginal vs garder (c / cotation) | IC 90 % du marginal |\n|---|---|---|---|---|---|---|---|")
        for b in BORNES:
            base_ = lambda o: pnl_regl(o, o["garder"], b)
            pol = [("garder", base_)] + [(f"annuler W à {d} ms", (lambda d: lambda o: pnl_regl(o, o["ann"].get(("W", d), o["garder"]), b))(d)) for d in DELAIS] \
                  + [(f"annuler {k} seul à 50 ms", (lambda k: lambda o: pnl_regl(o, o["ann"].get((k, 50), o["garder"]), b))(k)) for k in ("W1", "W2", "W3")]
            for nom, f in pol:
                if nom.startswith("annuler W à") or nom.startswith("annuler W1") or nom.startswith("annuler W2") or nom.startswith("annuler W3"):
                    k = ("W", int(nom.split("à ")[1].split(" ")[0])) if nom.startswith("annuler W à") else (nom.split()[1], 50)
                    nr = sum(1 for o in X_ if o["ann"].get(k, o["garder"])[b][0] > 0); parts = sum(o["ann"].get(k, o["garder"])[b][0] for o in X_)
                else:
                    nr = sum(1 for o in X_ if o["garder"][b][0] > 0); parts = sum(o["garder"][b][0] for o in X_)
                v = sum(f(o) for o in X_) / len(X_)
                c_ = ic_moy(X_, f)
                m_ = sum(f(o) - base_(o) for o in X_) / len(X_); cm = ic_moy(X_, lambda o: f(o) - base_(o))
                W_(f"| {nom} | {b} | {nr} | {parts:.0f} | {100 * v:+.1f} | [{100 * c_[0]:+.1f} ; {100 * c_[1]:+.1f}] | {100 * m_:+.1f} | [{100 * cm[0]:+.1f} ; {100 * cm[1]:+.1f}] |")
        W_("")
    # markout-based (moins bruité), file centrale
    W_("**P&L markout +5 s (moins dépendant des jackpots), file centrale, tous les cycles**\n")
    W_("| Politique | Markout total (c / cotation) | Parts |\n|---|---|---|")
    def mk(o, res):
        qq, t1 = res["centrale"]
        if qq <= 0 or not t1: return 0.0
        mo = o["mo"]["centrale"]                                    # milieu à +5 s après le 1er fill (même 1er fill si non annulé avant)
        return qq * mo if mo is not None else 0.0
    for nom, k in [("garder", None)] + [(f"annuler W à {d} ms", ("W", d)) for d in DELAIS]:
        tot = sum(mk(o, o["garder"] if k is None else o["ann"].get(k, o["garder"])) for o in OR) / len(OR)
        W_(f"| {nom} | {100 * tot:+.2f} | {sum((o['garder'] if k is None else o['ann'].get(k, o['garder']))['centrale'][0] for o in OR):.0f} |")

    # ---------------- H813
    W_("\n## 4. H813 — Coût de la perte de priorité (annuler à 50 ms, reposer 500 ms plus tard en fin de file)\n")
    W_("Comparaison sur la même fenêtre (de la repose à la fin de vie) : parts et P&L que l'offre d'origine aurait obtenus si on l'avait gardée (avec sa place) "
       "contre ce que l'offre reposée en fin de file obtient.\n")
    W_("| File | Cotations reposées | Parts : gardée / reposée | P&L règlement : gardée / reposée ($) | Coût de la priorité ($) |\n|---|---|---|---|---|")
    R_ = [o for o in OR if o["repose"]]
    for b in BORNES:
        qg = sum(o["garde_fen"][b] for o in R_); qr = sum(o["repose"][b][0] for o in R_)
        pg = sum(o["garde_fen"][b] * (o["win"] - o["p"]) for o in R_); pr = sum(o["repose"][b][0] * (o["win"] - o["repose"][b][1]) for o in R_)
        W_(f"| {b} | {len(R_)} | {qg:.0f} / {qr:.0f} | {pg:+.0f} / {pr:+.0f} | {pg - pr:+.0f} |")
    W_("\n## 5. Lecture\n- Délai maximal acceptable = plus grand d pour lequel « annuler » reste au-dessus de « garder » ET au-dessus de 0 sous la file prudente, avec un IC par cycles > 0.\n"
       "- Le délai réaliste depuis Dublin est ≥ 14 ms (trajet simple) + temps de calcul ; Polymarket n'impose pas de retard aux annulations.\n")
    W_("## Limites\n- Une journée, ~80 cycles ; offres fictives qui ne modifient pas le carnet.\n- Le markout et le statut toxique sont mesurés au premier fill.\n"
       "- W2 et W1 sont mesurés sur le carnet reçu à Dublin (≈ 10 ms après Polymarket) : ce sont bien des informations disponibles à Dublin.\n")
    open(SORTIE, "w").write("\n".join(out)); print("\n".join(out))


if __name__ == "__main__":
    main()
