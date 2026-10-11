"""BOT95 — Suite R4 : H796–H798 (Pitch, 11.10.2026 17:35). Hors ligne uniquement ; aucun ordre ; R4 vivant et fantômes gelés inchangés.
Période réservée (≥ 13.10 00:00 UTC) jamais lue. Validation chronologique : apprentissage = 1re moitié des cycles, test = 2e moitié.

H796  Prédicteur de NON-RETOUR : au moment exact du retrait (première fois que plus rien n'est achetable au prix du signal), avec les seules données
      reçues à cet instant, prédire si une offre ≤ prix + 2 c ne reviendra pas dans les 5 s. Témoins : mouvement BTC (Binance, Bybit), variation
      Chainlink, déplacement du carnet. AUC, calibration, avance temporelle, valeur économique.
H797  Relances : A après zéro fill seulement / B après fill partiel seulement / C les deux (= R4) / D aucune. Mêmes règles que R4 (+2 c, recalcul,
      probabilité − prix − frais ≥ 0,05), même budget, latence, frais, signaux.
H798  Le premier fill (quantité, délai) prédit-il la qualité des parts supplémentaires ? Contrôles : prix, profondeur, temps restant, volatilité, modèle.
Usage : python3 etude/bot5min/suite_r4_h796.py dossier_cycles → etude/bot5min/resultat_suite_r4_h796.md"""
import json, os, sys, glob, collections, math, time
import numpy as np

ICI = os.path.dirname(os.path.abspath(__file__)); RACINE = os.path.abspath(os.path.join(ICI, "..", ".."))
sys.path.insert(0, ICI)
import latence_h766 as LH, modele_dublin as MD, retry_h776 as RH
HORS_ECH = 1791849600; SORTIE = os.path.join(ICI, "resultat_suite_r4_h796.md")
EXEC = 164; BUDGET = 50.0; CAP = 20
rng = np.random.default_rng(796)


def auc(s, y):
    s = np.asarray(s, float); y = np.asarray(y, float); P = s[y == 1]; N = s[y == 0]
    if not len(P) or not len(N): return float("nan")
    return float(np.mean([(p > n) + 0.5 * (p == n) for p in P for n in N]))


def ic(G, fn, n=1000):
    G = [g for g in G if g]
    if len(G) < 3: return (float("nan"), float("nan"))
    v = []
    for _ in range(n):
        s = [x for i in rng.integers(0, len(G), len(G)) for x in G[i]]
        try: r = fn(s)
        except Exception: r = None
        if r is not None and not (isinstance(r, float) and math.isnan(r)): v.append(r)
    return (float(np.percentile(v, 5)), float(np.percentile(v, 95))) if v else (float("nan"), float("nan"))


def zs(Xtr, Xte):
    m = Xtr.mean(0); s = Xtr.std(0); s[s == 0] = 1; return (Xtr - m) / s, (Xte - m) / s


def main():
    dossier = sys.argv[1]
    F = {int(os.path.basename(f).split(".")[0]): f for f in glob.glob(os.path.join(dossier, "**", "*.json.gz"), recursive=True)}
    F = {k: v for k, v in F.items() if k < HORS_ECH}
    SIG = sorted([s for s in json.load(open(os.path.join(RACINE, "bot95", "rapide.json")))["signaux"] if s.get("gagnant") and s["start"] in F and s["start"] < HORS_ECH], key=lambda s: s["tDecision"])
    cycles = sorted({s["start"] for s in SIG}); coupe = cycles[len(cycles) // 2]
    LIG = []
    for st in cycles:
        cy = LH.Cycle(F[st]); prev = F.get(st - 300)
        Mo = MD.Modele(MD.charger_ex([f for f in (prev, F[st]) if f]), cy.strike, st + 300)
        S = [s for s in SIG if s["start"] == st]
        inst = []
        for s in S:
            t0 = s["tDecision"]; inst += [t0 + 500 * k + EXEC for k in range(10)] + [t0 + 25 * j for j in range(0, 401)]
        E = cy.etats(inst)
        for s in S:
            t0 = s["tDecision"]; X = s["cote"]; a0m = int(round(s["a0"] * 1000)); y = 1.0 if s["gagne"] else 0.0; sens = 1 if X == "Up" else -1
            def prob(t):
                p = Mo.proba(t / 1000)
                if p is None: return None
                f = LH.fair_regle(s["nom"], p); return f if X == "Up" else 1 - f
            # ---- tentatives R4 (enregistrées une à une) : (k, parts, coût)
            probs = [prob(t0 + 500 * k) for k in range(10)]; budget = BUDGET; att = []
            for k in range(10):
                lim = RH.limite(probs[k], a0m, CAP, True)
                if lim <= 0 or budget <= 0.01: att.append((k, 0.0, 0.0)); continue
                dq, dc = RH.acheter_lim(E[t0 + 500 * k + EXEC], X, lim, budget); budget -= dc; att.append((k, dq, dc))
            # Bot95 (une tentative au prix du signal, sans condition)
            qb, cb = RH.acheter_lim(E[t0 + EXEC], X, a0m, BUDGET)
            # ---- H796 : instant de retrait et retour
            td = None
            for j in range(0, 201):
                if LH.acheter(E[t0 + 25 * j], X, a0m, 1e9)[0] < 1: td = j; break
            feat = None; nonret = None
            if td is not None:
                tdm = t0 + 25 * td
                nonret = 1.0
                for j in range(td + 1, min(400, td + 200) + 1):
                    if LH.acheter(E[t0 + 25 * j], X, a0m + CAP, 1e9)[0] >= 1: nonret = 0.0; break
                def mv(src, dt):
                    a = Mo.dernier(src, tdm / 1000); b = Mo.dernier(src, tdm / 1000 - dt)
                    return sens * (a[1] - b[1]) / b[1] * 1e4 if a and b else 0.0
                L0, Ld = E[t0], E[tdm]
                v0 = LH.vendeurs(L0, X); vd = LH.vendeurs(Ld, X); b0 = LH.acheteurs(L0, X); bd = LH.acheteurs(Ld, X)
                prof = lambda v, lim: sum(sz for p, sz in v if p <= lim)
                # cause passée (transactions vs retraits) entre t0 et le retrait
                side = 1 if X == "Up" else 0; lims = (lambda c: c <= a0m) if X == "Up" else (lambda c: c >= 1000 - a0m)
                import bisect
                trv = sum(x[3] for x in cy.tr[bisect.bisect_right(cy.trT, t0):bisect.bisect_right(cy.trT, tdm)] if x[1] == side and lims(x[2]))
                pd = prob(tdm)
                feat = dict(btc_bn1=mv("bn", 1), btc_bn3=mv("bn", 3), btc_perp3=mv("perp", 3), cl5=mv("cl", 5),
                            ask_mv=((vd[0][0] - a0m) / 10 if vd else 3.0), bid_mv=((bd[0][0] - b0[0][0]) / 10 if bd and b0 else 0.0),
                            prof_ratio=math.log1p(prof(vd, a0m + 30)) - math.log1p(prof(v0, a0m + 30)), trade=1.0 if trv > 0 else 0.0,
                            edge=(pd - s["a0"]) if pd is not None else (s["modele"] - s["a0"]), a0=s["a0"], tleft=s["restant_s"], td=25 * td)
            sg = Mo._lent(int(s["tDecision"] / 1000) - 1)
            LIG.append(dict(s=s, st=st, y=y, X=X, att=att, qb=qb, cb=cb, td=td, nonret=nonret, feat=feat, vol=(sg[0] if sg else None),
                            q0=(s.get("achetable0") or {}).get("q", 0)))
    par_cy = lambda X_: list({l["st"]: [m for m in X_ if m["st"] == l["st"]] for l in X_}.values())
    o = []; w = o.append
    w("# Bot95 — Suite R4 : H796–H798 — PRÉLIMINAIRE (hors ligne)\n")
    w(f"Généré le {time.strftime('%d.%m.%Y %H:%M', time.gmtime())} UTC. {len(SIG)} signaux réglés, {len(cycles)} cycles (avant le 13.10). Apprentissage = cycles < "
      f"{time.strftime('%H:%M', time.gmtime(coupe))} UTC, test = après (cycles indépendants). IC 90 % par rééchantillonnage de cycles. R4 = relances toutes les 500 ms "
      "pendant 5 s, +2 c, probabilité recalculée − prix − frais ≥ 0,05, exécution 164 ms après chaque envoi, budget 50 $.\n")

    # ================= H796
    w("## 1. H796 — Prédicteur de non-retour (livrable 1)\n")
    D = [l for l in LIG if l["feat"] is not None]
    tr = [l for l in D if l["st"] < coupe]; te = [l for l in D if l["st"] >= coupe]
    w(f"Offres retirées dans les 5 s : {len(D)} (apprentissage {len(tr)}, test {len(te)}). Non-retour (≤ prix + 2 c, 5 s après le retrait) : "
      f"{100 * np.mean([l['nonret'] for l in D]):.0f} %. Instant médian du retrait : {np.median([l['feat']['td'] for l in D]):.0f} ms après la décision. "
      f"Taux de gain du signal : non-retour {100 * np.mean([l['y'] for l in D if l['nonret'] == 1]):.0f} %, retour {100 * np.mean([l['y'] for l in D if l['nonret'] == 0]):.0f} %.\n")
    K = ["btc_bn1", "btc_bn3", "btc_perp3", "cl5", "ask_mv", "bid_mv", "prof_ratio", "trade", "edge", "a0", "tleft"]
    w("**Variables (toutes connues au retrait) — AUC seule sur le test** (orientée sur l'apprentissage)\n")
    w("| Variable | Sens | AUC test | IC 90 % |\n|---|---|---|---|")
    ytr = np.array([l["nonret"] for l in tr]); yte = np.array([l["nonret"] for l in te])
    for k in K:
        str_ = [l["feat"][k] for l in tr]; sgn = 1 if auc(str_, ytr) >= 0.5 else -1
        a = auc([sgn * l["feat"][k] for l in te], yte); c_ = ic(par_cy(te), lambda s: auc([sgn * l["feat"][k] for l in s], [l["nonret"] for l in s]))
        w(f"| {k} | {'+' if sgn > 0 else '−'} | {a:.2f} | [{c_[0]:.2f} ; {c_[1]:.2f}] |")
    # modèle complet (logistique L2) contre témoins simples
    def fit(keys):
        Xtr = np.array([[l["feat"][k] for k in keys] for l in tr]); Xte = np.array([[l["feat"][k] for k in keys] for l in te])
        Xtr, Xte = zs(Xtr, Xte); b = LH_ajuster(Xtr, ytr, 3.0); return LH_predire(b, Xte)
    import contreparties_h724 as CH
    global LH_ajuster, LH_predire
    LH_ajuster, LH_predire = CH.ajuster, CH.predire
    MODS = {"témoin BTC (Binance 1 s + 3 s, Bybit 3 s)": ["btc_bn1", "btc_bn3", "btc_perp3"], "témoin Chainlink (5 s)": ["cl5"],
            "témoin carnet (vendeur, acheteur, profondeur)": ["ask_mv", "bid_mv", "prof_ratio"], "prédicteur complet": K}
    w("\n| Modèle | AUC test | IC 90 % | Brier test | Brier « taux de base » |\n|---|---|---|---|---|")
    PRED = {}
    base = np.mean(ytr)
    for nom, keys in MODS.items():
        p = fit(keys); PRED[nom] = p
        for l, pp in zip(te, p): l.setdefault("p", {})[nom] = float(pp)
        c_ = ic(par_cy(te), lambda s: auc([l["p"][nom] for l in s], [l["nonret"] for l in s]))
        w(f"| {nom} | {auc(p, yte):.2f} | [{c_[0]:.2f} ; {c_[1]:.2f}] | {np.mean((p - yte) ** 2):.3f} | {np.mean((base - yte) ** 2):.3f} |")
    p = PRED["prédicteur complet"]
    w("\n**Calibration du prédicteur complet (test)**\n\n| Probabilité prédite | Offres | Non-retour observé |\n|---|---|---|")
    for lo, hi in ((0, 0.2), (0.2, 0.4), (0.4, 0.6), (0.6, 1.01)):
        m = (p >= lo) & (p < hi)
        if m.sum(): w(f"| {lo:.1f}–{min(hi, 1):.1f} | {int(m.sum())} | {100 * yte[m].mean():.0f} % |")
    w(f"\n**Avance temporelle** : la prédiction est faite au retrait (médiane {np.median([l['feat']['td'] for l in te]):.0f} ms après la décision), soit 5 s avant que le "
      "non-retour soit constaté. Mais à cet instant l'offre au prix du signal est déjà partie : l'avance ne permet pas d'acheter au prix du signal.\n")
    # valeur économique : (i) ne relancer que si retour probable ; (ii) poursuivre jusqu'à +5 c si non-retour probable
    w("**Valeur économique (test)** — on ne garde que ce qui est exécutable : achat 164 ms après le retrait, budget restant, frais.\n")
    cyF = {}
    for l in te:
        cyF.setdefault(l["st"], LH.Cycle(F[l["st"]]))
    rows = []
    for l in te:
        s = l["s"]; t0 = s["tDecision"]; tdm = t0 + l["feat"]["td"]; a0m = int(round(s["a0"] * 1000)); X = l["X"]
        L = cyF[l["st"]].etats([tdm + EXEC])[tdm + EXEC]
        spent = sum(c for k, q, c in l["att"] if 500 * k <= l["feat"]["td"])
        q5, c5 = RH.acheter_lim(L, X, min(a0m + 50, int((s["modele"] - 0.05) * 1000)), max(0.0, BUDGET - spent))
        l["chase"] = q5 * l["y"] - c5
        r4_apres = sum(q * l["y"] - c for k, q, c in l["att"] if 500 * k > l["feat"]["td"])
        l["r4_apres"] = r4_apres; rows.append(l)
    pc = PRED["prédicteur complet"]
    for l, pp in zip(te, pc): l["pn"] = pp
    g1 = sum(l["r4_apres"] for l in rows); g2 = sum(l["r4_apres"] for l in rows if l["pn"] < 0.5); g3 = sum(l["chase"] for l in rows if l["pn"] >= 0.5)
    w(f"- Relances R4 après le retrait (toutes) : {g1:+.0f} $ ; relances seulement si retour probable (p < 0,5) : {g2:+.0f} $.")
    w(f"- Poursuite immédiate jusqu'à +5 c quand le non-retour est probable (p ≥ 0,5) : {g3:+.0f} $ sur {sum(1 for l in rows if l['pn'] >= 0.5)} offres "
      f"({sum(1 for l in rows if l['pn'] >= 0.5 and l['chase'] != 0)} exécutées).\n")

    # ================= H797
    w("## 2. H797 — Relance après zéro fill / après fill partiel (livrables 2, 3, 4, 6)\n")
    def pol(l, mode):
        a = l["att"]; q0_, c0_ = a[0][1], a[0][2]
        if mode == "D": ks = [0]
        elif mode == "C": ks = range(10)
        elif mode == "A": ks = range(10) if q0_ <= 0 else [0]
        else: ks = range(10) if q0_ > 0 else [0]                       # B
        q = sum(a[k][1] for k in ks); c = sum(a[k][2] for k in ks)
        return q, c, q * l["y"] - c
    def dd(vals):
        cum = np.cumsum(vals); return float(np.max(np.maximum.accumulate(np.concatenate([[0], cum]))[1:] - cum)) if len(cum) else 0.0
    w("| Politique | Remplis | Parts | P&L ($) | / signal (IC 90 %) | marginal vs D | IC 90 % du marginal | 1re / 2e moitié | Drawdown | Jackpots | Signaux en plus : gagnants / perdants |\n|---|---|---|---|---|---|---|---|---|---|---|")
    NOMS = {"Bot95 actuel (164 ms, prix du signal)": None, "D — aucune relance (1re tentative R4)": "D", "A — relance après zéro fill": "A",
            "B — relance après fill partiel": "B", "C — les deux (= R4)": "C"}
    Ls = sorted(LIG, key=lambda l: l["s"]["tDecision"])
    for nom, m in NOMS.items():
        f = (lambda l: (l["qb"], l["cb"], l["qb"] * l["y"] - l["cb"])) if m is None else (lambda l, m=m: pol(l, m))
        pn = [f(l)[2] for l in Ls]; D_ = [pol(l, "D")[2] for l in Ls]
        c_ = ic(par_cy(Ls), lambda s: float(np.mean([f(l)[2] for l in s])))
        cm = ic(par_cy(Ls), lambda s: float(np.mean([f(l)[2] - pol(l, "D")[2] for l in s])))
        nouveaux = [l for l in Ls if f(l)[0] > 0 and pol(l, "D")[0] <= 0]
        jack = sum(1 for l in Ls if f(l)[0] > 0 and l["y"] == 1 and f(l)[1] / f(l)[0] <= 0.25)
        w(f"| {nom} | {sum(1 for l in Ls if f(l)[0] > 0)} | {sum(f(l)[0] for l in Ls):.0f} | {sum(pn):+.0f} | {np.mean(pn):+.2f} [{c_[0]:+.2f} ; {c_[1]:+.2f}] | "
          f"{sum(pn) - sum(D_):+.0f} | [{cm[0]:+.2f} ; {cm[1]:+.2f}] / signal | {np.mean([f(l)[2] for l in Ls if l['st'] < coupe]):+.2f} / {np.mean([f(l)[2] for l in Ls if l['st'] >= coupe]):+.2f} | "
          f"{dd(pn):.0f} | {jack} | {sum(1 for l in nouveaux if l['y'] == 1)} / {sum(1 for l in nouveaux if l['y'] == 0)} |")
    # quantités supplémentaires
    sup = [(l, sum(q for k, q, c in l["att"][1:]), sum(c for k, q, c in l["att"][1:])) for l in Ls]
    zf = [(l, q, c) for l, q, c in sup if l["att"][0][1] <= 0 and q > 0]; pf = [(l, q, c) for l, q, c in sup if l["att"][0][1] > 0 and q > 0]
    for nom, Z in (("après zéro fill", zf), ("après fill partiel", pf)):
        if Z: w(f"\n- Parts supplémentaires {nom} : {len(Z)} signaux, {sum(q for _, q, _ in Z):.0f} parts, {sum(c for _, _, c in Z):.0f} $ ; résultat "
                f"{sum(q * l['y'] - c for l, q, c in Z):+.0f} $ ({100 * sum(q * l['y'] - c for l, q, c in Z) / sum(c for _, _, c in Z):+.0f} % par $) ; "
                f"gagnants {sum(1 for l, _, _ in Z if l['y'] == 1)}, perdants {sum(1 for l, _, _ in Z if l['y'] == 0)}.")
    w("")

    # ================= H798
    w("## 3. H798 — Le premier fill renseigne-t-il sur la qualité des parts supplémentaires ? (livrable 5)\n")
    P_ = [(l, q, c) for l, q, c in pf]
    w(f"Signaux avec premier fill partiel puis parts supplémentaires : {len(P_)}. Variable expliquée : résultat par $ des parts supplémentaires.\n")
    if len(P_) >= 8:
        frac = lambda l: l["att"][0][2] / BUDGET
        k1 = lambda l: next((k for k, q, c in l["att"] if q > 0), 0)
        w("| Groupe | Signaux | Résultat des parts supplémentaires par $ | Taux de gain |\n|---|---|---|---|")
        for nom, f in (("premier fill < 25 % du budget", lambda l: frac(l) < 0.25), ("premier fill ≥ 25 % du budget", lambda l: frac(l) >= 0.25)):
            G = [(l, q, c) for l, q, c in P_ if f(l)]
            if G: w(f"| {nom} | {len(G)} | {100 * sum(q * l['y'] - c for l, q, c in G) / sum(c for _, _, c in G):+.0f} % | {100 * np.mean([l['y'] for l, _, _ in G]):.0f} % |")
        # régression : gain du signal ~ fraction remplie + contrôles (sur tous les signaux avec un premier fill)
        A_ = [l for l in Ls if l["att"][0][1] > 0 and l["vol"]]
        keys = ["frac", "a0", "logq0", "tleft", "vol", "modele"]
        def row(l): return [l["att"][0][2] / BUDGET, l["s"]["a0"], math.log1p(l["q0"] or 0), l["s"]["restant_s"], l["vol"] * 1e4, l["s"]["modele"]]
        Xa = np.array([row(l) for l in A_]); ya = np.array([l["y"] for l in A_]); Xz, _ = zs(Xa, Xa)
        b = CH.ajuster(Xz, ya, 1.0)
        bs = []
        G = par_cy(A_)
        for _ in range(300):
            s_ = [x for i in rng.integers(0, len(G), len(G)) for x in G[i]]
            Xs = np.array([row(l) for l in s_]); ys = np.array([l["y"] for l in s_])
            m_ = Xa.mean(0); sd_ = Xa.std(0); sd_[sd_ == 0] = 1
            try: bs.append(CH.ajuster((Xs - m_) / sd_, ys, 1.0))
            except Exception: pass
        bs = np.array(bs)
        w(f"\nRégression logistique (gain du signal, {len(A_)} signaux avec un premier fill ; coefficients standardisés, IC 90 % par cycles) :\n")
        w("| Variable | Coefficient | IC 90 % |\n|---|---|---|")
        for i, k in enumerate(keys):
            w(f"| {k} | {b[i + 1]:+.2f} | [{np.percentile(bs[:, i + 1], 5):+.2f} ; {np.percentile(bs[:, i + 1], 95):+.2f}] |")
        w("\nfrac = part du budget remplie au premier fill ; le délai du premier fill est presque toujours la 1re tentative (164 ms), donc peu informatif ici.\n")

    # ================= verdict
    w("## 4. Verdict statistique sur cycles indépendants (livrable 7)\n")
    te_l = [l for l in Ls if l["st"] >= coupe]
    for nom, m in (("A", "A"), ("B", "B"), ("C = R4", "C")):
        cm = ic(par_cy(te_l), lambda s: float(np.mean([pol(l, m)[2] - pol(l, "D")[2] for l in s])))
        w(f"- Test (2e moitié) — {nom} contre D : {np.mean([pol(l, m)[2] - pol(l, 'D')[2] for l in te_l]):+.2f} $ / signal, IC 90 % [{cm[0]:+.2f} ; {cm[1]:+.2f}].")
    w("- Prédicteur de non-retour : voir l'AUC test et son IC ci-dessus (≥ 0,5 + IC strictement au-dessus de 0,5 = information réelle).\n")
    w("## Limites\n- Une journée, ~15 cycles de test : faible puissance.\n- Modèle recalculé hors ligne (fidèle à ±0,005 pour ~3/4 des signaux).\n"
      "- Les variantes du même cycle ne sont pas indépendantes (IC par cycles).\n")
    open(SORTIE, "w").write("\n".join(o)); print("\n".join(o))


if __name__ == "__main__":
    main()
