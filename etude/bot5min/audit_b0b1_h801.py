"""BOT95 — H801–H803 + validation future de B0 / B1 (Pitch, 11.10.2026 18:21). Hors ligne ; R4 et fantômes gelés inchangés ; aucun ordre.
B0 et B1 sont FIGÉS (définis dans completion_h799.py) : D = 1re tentative R4 seule ; B0 = compléter (relances R4) après tout fill partiel ;
B1 = B0 seulement si la profondeur affichée au prix du signal ≥ 25 $. Aucun seuil ré-optimisé. Période réservée (≥ 13.10) jamais lue.
H801  dépendance aux gros gains (1 / 3 / 5 meilleurs compléments, exclusion analytique, prix des billets, Expected Shortfall, drawdown)
H802  migration des fills selon la latence 164 / 250 / 500 ms (fills communs / propres, décomposition prix / quantité / sélection / disponibilité)
H803  stabilité de la profondeur (signal, 1er fill, chaque relance) ; valeur ajoutée de B1 après contrôles (prix, temps restant, volatilité)
VALIDATION  B0 / B1 / D recalculés exactement sur les cycles NOUVEAUX enregistrés par le fantôme R4 vivant (tentatives enregistrées une à une).
Usage : python3 etude/bot5min/audit_b0b1_h801.py dossier_cycles → etude/bot5min/resultat_audit_b0b1_h801.md"""
import json, os, sys, glob, math, time, collections
import numpy as np

ICI = os.path.dirname(os.path.abspath(__file__)); RACINE = os.path.abspath(os.path.join(ICI, "..", ".."))
sys.path.insert(0, ICI)
import latence_h766 as LH, modele_dublin as MD, completion_h799 as CP, contreparties_h724 as CH
HORS_ECH = 1791849600; SORTIE = os.path.join(ICI, "resultat_audit_b0b1_h801.md")
BUDGET = 50.0; CAP = 20; SEUIL_B1 = 25.0; DEB_R4 = 1791731400            # R4 vivant déployé le 11.10 vers 15:30 UTC
fee = CP.fee_f(1.0)
rng = np.random.default_rng(801)


def ic(G, fn, n=2000, alpha=0.10):
    G = [g for g in G if g]
    if len(G) < 3: return (float("nan"), float("nan"))
    v = []
    for _ in range(n):
        try: v.append(fn([x for i in rng.integers(0, len(G), len(G)) for x in G[i]]))
        except Exception: pass
    return (float(np.percentile(v, 100 * alpha / 2)), float(np.percentile(v, 100 * (1 - alpha / 2)))) if v else (float("nan"), float("nan"))


def prof_dollars(L, X, lim):
    return sum(sz * p / 1000 for p, sz in LH.vendeurs(L, X) if p <= lim)


def tentatives(E, t0, X, a0m, probs, ex):
    """R4 : 10 envois (0, 0,5 … 4,5 s), exécution ex ms après chaque envoi, budget partagé. Rend la liste des tentatives."""
    out = []; budget = BUDGET
    for k in range(10):
        lim = CP.limite(probs[k], a0m, fee)
        Ls, Lx = E[t0 + 500 * k], E[t0 + 500 * k + ex]
        d_env = prof_dollars(Ls, X, lim) if lim > 0 else 0.0; d_ex = prof_dollars(Lx, X, lim) if lim > 0 else 0.0
        q = c = 0.0
        if lim > 0 and budget > 0.01:
            q, c = CP.acheter(Lx, X, lim, budget, fee)
            # vérification : jamais plus que la quantité affichée ≤ plafond à l'exécution
            assert q <= sum(sz for p, sz in LH.vendeurs(Lx, X) if p <= lim) + 1e-6
            budget -= c
        out.append(dict(k=k, lim=lim, d_env=d_env, d_ex=d_ex, q=q, c=c))
    return out


def politique(att, y, prof0, nom):
    """att : tentatives [(q, c)] ; renvoie (q1, c1, qc, cc)"""
    q1, c1 = att[0][0], att[0][1]
    comp = nom in ("B0", "B1") and q1 > 0 and (nom == "B0" or prof0 >= SEUIL_B1)
    qc = sum(a[0] for a in att[1:]) if comp else 0.0; cc = sum(a[1] for a in att[1:]) if comp else 0.0
    return q1, c1, qc, cc


def main():
    dossier = sys.argv[1]
    F = {int(os.path.basename(f).split(".")[0]): f for f in glob.glob(os.path.join(dossier, "**", "*.json.gz"), recursive=True)}
    F = {k: v for k, v in F.items() if k < HORS_ECH}
    TOUS = [s for s in json.load(open(os.path.join(RACINE, "bot95", "rapide.json")))["signaux"] if s.get("gagnant") and s["start"] < HORS_ECH]
    SIG = sorted([s for s in TOUS if s["start"] in F], key=lambda s: s["tDecision"])
    cycles = sorted({s["start"] for s in SIG}); coupe = cycles[len(cycles) // 2]
    LIG = []
    for st in cycles:
        cy = LH.Cycle(F[st]); prev = F.get(st - 300)
        Mo = MD.Modele(MD.charger_ex([f for f in (prev, F[st]) if f]), cy.strike, st + 300)
        S = [s for s in SIG if s["start"] == st]
        inst = []
        for s in S:
            t0 = s["tDecision"]; inst += [t0] + [t0 + 500 * k + e for k in range(10) for e in (0, 164, 250, 500)]
        E = cy.etats(inst)
        for s in S:
            t0 = s["tDecision"]; X = s["cote"]; a0m = int(round(s["a0"] * 1000)); y = 1.0 if s["gagne"] else 0.0
            probs = []
            for k in range(10):
                p = Mo.proba((t0 + 500 * k) / 1000); f = None if p is None else LH.fair_regle(s["nom"], p)
                probs.append(None if f is None else (f if X == "Up" else 1 - f))
            sg = Mo._lent(int(t0 / 1000) - 1)
            r = dict(s=s, st=st, y=y, X=X, a0=s["a0"], prof0=(s.get("q0") or 0) * s["a0"], d_sig=prof_dollars(E[t0], X, a0m + CAP),
                     vol=(sg[0] * 1e4 if sg else float("nan")), att={})
            for ex in (164, 250, 500): r["att"][ex] = tentatives(E, t0, X, a0m, probs, ex)
            LIG.append(r)
    par_cy = lambda X_: list({l["st"]: [m for m in X_ if m["st"] == l["st"]] for l in X_}.values())
    te = [l for l in LIG if l["st"] >= coupe]
    def P(l, nom, ex=164):
        q1, c1, qc, cc = politique([(a["q"], a["c"]) for a in l["att"][ex]], l["y"], l["prof0"], nom)
        return dict(q1=q1, c1=c1, qc=qc, cc=cc, p1=q1 * l["y"] - c1, pc=qc * l["y"] - cc, tot=(q1 + qc) * l["y"] - c1 - cc)
    o = []; w = o.append
    w("# Bot95 — H801–H803 et validation future de B0 / B1 — PRÉLIMINAIRE\n")
    w(f"Généré le {time.strftime('%d.%m.%Y %H:%M', time.gmtime())} UTC. Hors ligne : {len(LIG)} signaux, {len(cycles)} cycles enregistrés à Dublin (test = cycles ≥ "
      f"{time.strftime('%H:%M', time.gmtime(coupe))} UTC). B0 et B1 figés (B1 : profondeur au signal ≥ {SEUIL_B1:.0f} $), aucun seuil ré-optimisé. "
      "Toutes les parts sont vérifiées ≤ quantité affichée au plafond à l'instant d'exécution (aucune violation).\n")

    # ================= H801
    w("## 1. H801 — Dépendance aux gros gains (compléments)\n")
    for titre, X_ in (("test (cycles non vus)", te), ("tout", LIG)):
        w(f"### {titre}\n")
        w("| Politique | P&L total | dont compléments | 1 meilleur | 3 meilleurs | 5 meilleurs | compl. sans le meilleur | sans les 3 | sans les 5 | Complétés G / P | ES 10 % compl. / signal complété | Drawdown total |\n|---|---|---|---|---|---|---|---|---|---|---|---|")
        for nom in ("B0", "B1"):
            pcs = sorted([P(l, nom)["pc"] for l in X_ if P(l, nom)["qc"] > 0], reverse=True); comp = sum(pcs)
            tot = sum(P(l, nom)["tot"] for l in X_)
            ns = [l for l in X_ if P(l, nom)["qc"] > 0]
            es = float(np.mean(sorted(pcs)[:max(1, int(math.ceil(0.10 * len(pcs))))])) if pcs else float("nan")
            cum = np.cumsum([P(l, nom)["tot"] for l in sorted(X_, key=lambda l: l["s"]["tDecision"])])
            dd = float(np.max(np.maximum.accumulate(np.concatenate([[0], cum]))[1:] - cum))
            w(f"| {nom} | {tot:+.0f} | {comp:+.0f} | {sum(pcs[:1]):+.0f} | {sum(pcs[:3]):+.0f} | {sum(pcs[:5]):+.0f} | {comp - sum(pcs[:1]):+.0f} | {comp - sum(pcs[:3]):+.0f} | "
              f"{comp - sum(pcs[:5]):+.0f} | {sum(1 for l in ns if l['y'] == 1)} / {sum(1 for l in ns if l['y'] == 0)} | {es:+.1f} | {dd:.0f} |")
        w("")
    w("**Compléments par prix du billet (tout)**\n\n| Prix moyen du complément | B0 : signaux | B0 : P&L | B1 : signaux | B1 : P&L |\n|---|---|---|---|---|")
    for lo, hi in ((0, 0.10), (0.10, 0.20), (0.20, 0.35), (0.35, 1.01)):
        cells = []
        for nom in ("B0", "B1"):
            Z = [l for l in LIG if P(l, nom)["qc"] > 0 and lo <= P(l, nom)["cc"] / P(l, nom)["qc"] < hi]
            cells += [str(len(Z)), f"{sum(P(l, nom)['pc'] for l in Z):+.0f}"]
        w(f"| {lo:.2f}–{min(hi, 1):.2f} | " + " | ".join(cells) + " |")
    w("")

    # ================= H802
    w("## 2. H802 — Migration des fills selon la latence (B0)\n")
    w("| Latence | D (1re tentative) | Compléments B0 | B0 total | Signaux complétés | Envois où l'offre visible à l'envoi a disparu à l'exécution |\n|---|---|---|---|---|---|")
    for ex in (164, 250, 500):
        nd = sum(1 for l in LIG for a in l["att"][ex] if a["lim"] > 0 and a["d_env"] >= 1 and a["d_ex"] < 1)
        ne = sum(1 for l in LIG for a in l["att"][ex] if a["lim"] > 0 and a["d_env"] >= 1)
        w(f"| {ex} ms | {sum(P(l, 'D', ex)['tot'] for l in LIG):+.0f} | {sum(P(l, 'B0', ex)['pc'] for l in LIG):+.0f} | {sum(P(l, 'B0', ex)['tot'] for l in LIG):+.0f} | "
          f"{sum(1 for l in LIG if P(l, 'B0', ex)['qc'] > 0)} | {nd} / {ne} ({100 * nd / max(ne, 1):.0f} %) |")
    for ex in (250, 500):
        A = {id(l) for l in LIG if P(l, "B0", 164)["qc"] > 0}; B = {id(l) for l in LIG if P(l, "B0", ex)["qc"] > 0}
        com = [l for l in LIG if id(l) in A & B]; seulA = [l for l in LIG if id(l) in A - B]; seulB = [l for l in LIG if id(l) in B - A]
        dD = sum(P(l, "D", 164)["tot"] - P(l, "D", ex)["tot"] for l in LIG)
        selA = sum(P(l, "B0", 164)["pc"] for l in seulA); selB = sum(P(l, "B0", ex)["pc"] for l in seulB)
        dq = dp = 0.0
        for l in com:
            a, b = P(l, "B0", 164), P(l, "B0", ex)
            pa = a["cc"] / a["qc"]; pb = b["cc"] / b["qc"]
            dq += (a["qc"] - b["qc"]) * (l["y"] - pb); dp += a["qc"] * (pb - pa)
        tot = sum(P(l, "B0", 164)["tot"] - P(l, "B0", ex)["tot"] for l in LIG)
        w(f"\n**164 ms contre {ex} ms** — écart B0 total {tot:+.0f} $ =")
        w(f"- 1re tentative (offres déjà parties au moment d'exécuter = disponibilité) : {dD:+.0f} $")
        w(f"- sélection des signaux complétés : complétés seulement à 164 ms ({len(seulA)} signaux, {selA:+.0f} $) moins complétés seulement à {ex} ms ({len(seulB)} signaux, {selB:+.0f} $) = {selA - selB:+.0f} $")
        w(f"- sur les {len(com)} signaux complétés aux deux délais : effet quantité {dq:+.0f} $, effet prix {dp:+.0f} $")
        w(f"- reste (arrondis, interaction) : {tot - dD - (selA - selB) - dq - dp:+.0f} $")
    w("")

    # ================= H803
    w("## 3. H803 — Stabilité de la profondeur et valeur de B1\n")
    w("Profondeur = $ affichés au plafond (prix + 2 c) du côté acheté.\n")
    w("| Instant | Médiane ($) | 25e / 75e centiles | Corrélation (rang) avec la profondeur au signal |\n|---|---|---|---|")
    def rang(a, b):
        a = np.argsort(np.argsort(a)); b = np.argsort(np.argsort(b)); return float(np.corrcoef(a, b)[0, 1])
    base = np.array([l["d_sig"] for l in LIG])
    rows = [("au signal", base), ("au 1er fill (exécution de la 1re tentative)", np.array([l["att"][164][0]["d_ex"] for l in LIG]))]
    for k in (1, 2, 4, 9): rows.append((f"à la relance {k} (envoi à {0.5 * k:.1f} s)", np.array([l["att"][164][k]["d_env"] for l in LIG])))
    for nom, v in rows: w(f"| {nom} | {np.median(v):.0f} | {np.percentile(v, 25):.0f} / {np.percentile(v, 75):.0f} | {rang(base, v):+.2f} |")
    PF = [l for l in LIG if l["att"][164][0]["q"] > 0 and BUDGET - l["att"][164][0]["c"] > 0.01 and not math.isnan(l["vol"])]
    w(f"\n**B1 apporte-t-il quelque chose après contrôles ?** Signaux avec un 1er fill partiel (là où B0 et B1 diffèrent) : {len(PF)}.\n")
    if len(PF) >= 10:
        keys = ["prof0 ≥ 25 $", "prix du signal", "temps restant", "volatilité"]
        row = lambda l: [1.0 if l["prof0"] >= SEUIL_B1 else 0.0, l["a0"], l["s"]["restant_s"], l["vol"]]
        Xa = np.array([row(l) for l in PF]); m_ = Xa.mean(0); sd_ = Xa.std(0); sd_[sd_ == 0] = 1
        yv = np.array([P(l, "B0")["pc"] / max(P(l, "B0")["cc"], 1e-9) if P(l, "B0")["cc"] > 0 else 0.0 for l in PF])
        # MCO : rendement par $ des compléments ~ indicateur B1 + contrôles ; IC par cycles
        def mco(L):
            X = np.column_stack([np.ones(len(L)), (np.array([row(l) for l in L]) - m_) / sd_])
            yy = np.array([P(l, "B0")["pc"] / P(l, "B0")["cc"] if P(l, "B0")["cc"] > 0 else 0.0 for l in L])
            return np.linalg.lstsq(X, yy, rcond=None)[0]
        b = mco(PF); G = par_cy(PF); bs = []
        for _ in range(500):
            s_ = [x for i in rng.integers(0, len(G), len(G)) for x in G[i]]
            try: bs.append(mco(s_))
            except Exception: pass
        bs = np.array(bs)
        w("Régression (MCO) du rendement par $ des compléments B0, variables standardisées, IC 90 % par cycles :\n")
        w("| Variable | Coefficient | IC 90 % |\n|---|---|---|")
        for i, k in enumerate(keys): w(f"| {k} | {b[i + 1]:+.2f} | [{np.percentile(bs[:, i + 1], 5):+.2f} ; {np.percentile(bs[:, i + 1], 95):+.2f}] |")
        g1 = [l for l in PF if l["prof0"] >= SEUIL_B1]; g0 = [l for l in PF if l["prof0"] < SEUIL_B1]
        f = lambda Z: 100 * sum(P(l, "B0")["pc"] for l in Z) / max(sum(P(l, "B0")["cc"] for l in Z), 1e-9)
        w(f"\nBrut : compléments quand profondeur au signal ≥ 25 $ : {len(g1)} signaux, {f(g1):+.0f} % par $ ; < 25 $ : {len(g0)} signaux, {f(g0):+.0f} % par $.\n")

    # ================= VALIDATION FUTURE (R4 vivant)
    w("## 4. Validation future : B0 / B1 / D recalculés sur les cycles NOUVEAUX du fantôme R4 vivant\n")
    V = sorted([s for s in TOUS if s.get("r4") and (s["r4"].get("R4") or {}).get("tentatives") is not None and s["start"] >= DEB_R4], key=lambda s: s["tDecision"])
    vu = {}; U = []
    for s in V:
        k = (s["start"], s["cote"])
        if k not in vu: vu[k] = 1; U.append(s)
    w(f"Signaux réglés avec R4 : {len(V)} ; décisions uniques (1 par cycle et côté, sans double position) : {len(U)} sur {len({s['start'] for s in U})} cycles.\n")
    if U:
        def vivant(s, nom):
            T = sorted(s["r4"]["R4"]["tentatives"], key=lambda x: x[0]); y = 1.0 if s["gagne"] else 0.0
            att = [(t[6] or 0.0, t[7] or 0.0) for t in T]
            if not att: return 0.0
            q1, c1, qc, cc = politique(att, y, (s.get("q0") or 0) * s["a0"], nom)
            return (q1 + qc) * y - c1 - cc
        G = list({s["start"]: [x for x in U if x["start"] == s["start"]] for s in U}.values())
        w("| Politique | P&L ($) | / décision | IC 90 % | vs D ($) | IC 90 % de l'écart / décision |\n|---|---|---|---|---|---|")
        for nom in ("D", "B0", "B1"):
            pn = [vivant(s, nom) for s in U]
            c_ = ic(G, lambda z: float(np.mean([vivant(s, nom) for s in z])))
            cd = ic(G, lambda z: float(np.mean([vivant(s, nom) - vivant(s, "D") for s in z])))
            w(f"| {nom} | {sum(pn):+.0f} | {np.mean(pn):+.2f} | [{c_[0]:+.2f} ; {c_[1]:+.2f}] | {sum(pn) - sum(vivant(s, 'D') for s in U):+.0f} | [{cd[0]:+.2f} ; {cd[1]:+.2f}] |")
        w("\nTrop peu de cycles pour conclure tant que l'IC contient 0 ; ce tableau se met à jour à chaque relance du script.\n")
    else:
        w("Pas encore de signal réglé avec R4 dans la sauvegarde (R4 vivant depuis le 11.10 vers 15:30 UTC).\n")

    # ================= verdict
    w("## 5. Verdict\n")
    cB0 = ic(par_cy(te), lambda z: float(np.mean([P(l, "B0")["tot"] - P(l, "D")["tot"] for l in z])))
    cB1 = ic(par_cy(te), lambda z: float(np.mean([P(l, "B1")["tot"] - P(l, "D")["tot"] for l in z])))
    w(f"- Hors ligne, cycles de test : B0 − D [{cB0[0]:+.2f} ; {cB0[1]:+.2f}] $/signal ; B1 − D [{cB1[0]:+.2f} ; {cB1[1]:+.2f}] $/signal.")
    w("- Le verdict final (B0, B1 ou aucune amélioration démontrée) ne sera donné que sur les cycles nouveaux de R4 puis la période réservée.\n")
    open(SORTIE, "w").write("\n".join(o)); print("\n".join(o))


if __name__ == "__main__":
    main()
