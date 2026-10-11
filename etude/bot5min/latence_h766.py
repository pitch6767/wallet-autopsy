"""BOT95 — H766 à H775 (Pitch, 11.10.2026 17:07) : l'avantage des signaux Bot95 peut-il être capturé malgré la latence ?
Hors ligne uniquement. Aucun ordre réel, aucun fantôme modifié, aucun déploiement. Période réservée (≥ 13.10 00:00 UTC) jamais lue.

Source : fichiers de cycle enregistrés à Dublin (carnet Up complet toutes les 10 s + chaque changement à ±3 c du meilleur prix, transactions des
deux jetons, prix des bourses), signaux de bot95/rapide.json, fantômes maker vivants de bot95/rapide_maker.json (M1, M4, M8).
Carnet miroir : offre Down au prix p ≡ demande Up au prix 1 − p.

H766  P&L net et quantité exécutable à 0/25/50/100/150/164/250/300/500 ms (frais preneur 0,07·p·(1−p), budget 50 $ comme Dublin).
H767  Disparitions : consommées par des transactions / retirées / indéterminées (jamais d'attribution inventée).
H768  Latence critique : premier délai où l'espérance par signal devient ≤ 0 (et où l'IC 90 % est entièrement < 0).
H769  Plafonds +0 / +1 / +2 / +3 c.
H770  Maker contre preneur sur les mêmes signaux (simulation, 3 bornes de file) + fantôme vivant M1.
H771–H773  Offres d'achat prépositionnées AVANT les signaux (condition sans regard vers le futur : écart du modèle ≥ 0,10), 3 bornes de file,
      inventaire plafonné à 50 $ par côté et par cycle, remplissages non désirés gardés jusqu'au règlement.
H774  Abandon immédiat / deuxième chance au plafond / attente (relances toutes les 500 ms pendant 5 s), achat seulement si modèle − prix − frais ≥ 0,05.
H775  500 ms avant chaque signal : avec un flux plus rapide (Binance) ajouté au prix Bybit/OKX, la même règle se serait-elle déclenchée plus tôt ?
      Grille de 100 ms sur tout le cycle (gagnants et perdants supplémentaires inclus), mêmes règles, mêmes seuils.
Usage : python3 etude/bot5min/latence_h766.py dossier_cycles → etude/bot5min/resultat_latence_h766.md"""
import gzip, json, os, sys, glob, bisect, collections, math, time
import numpy as np

ICI = os.path.dirname(os.path.abspath(__file__)); RACINE = os.path.abspath(os.path.join(ICI, "..", ".."))
sys.path.insert(0, ICI)
import fast_fenetre as FF, queue_race_phase12 as Q, modele_dublin as MD
HORS_ECH = 1791849600; SORTIE = os.path.join(ICI, "resultat_latence_h766.md")
DELAIS = (0, 25, 50, 100, 150, 164, 250, 300, 500)
PLAFONDS = (0, 10, 20, 30)                 # millièmes
LAT = 14; RETARD = 150; EXEC = LAT + RETARD
BUDGET = 50.0
BORNES = ("prudente", "centrale", "optimiste")
fee = lambda p: 0.07 * p * (1 - p)
rng = np.random.default_rng(766)


def ic(groupes, fn, n=1500):
    G = [g for g in groupes if g]
    if len(G) < 3: return (float("nan"), float("nan"))
    v = []
    for _ in range(n):
        s = [x for i in rng.integers(0, len(G), len(G)) for x in G[i]]
        r = fn(s)
        if r is not None and not (isinstance(r, float) and math.isnan(r)): v.append(r)
    return (float(np.percentile(v, 5)), float(np.percentile(v, 95))) if v else (float("nan"), float("nan"))


# ======================================================================= carnet
class Cycle:
    def __init__(self, fn):
        self.C = FF.normaliser(fn); self.R = json.load(gzip.open(fn)); self.st = self.C["start"]
        self.fl = self.C["flux"]; self.T = [e[0] for e in self.fl]
        self.strike = (self.R.get("marche") or {}).get("strike")
        # transactions → (t, côté du carnet Up consommé, prix Up, taille)
        self.tr = []
        for e in self.fl:
            if e[2] == "T":
                cs, cm = Q.cible_trade(e[3], e[4], e[5]); self.tr.append((e[0], cs, cm, e[6]))
        self.trT = [x[0] for x in self.tr]
        self.B = [e[0] for e in self.fl if e[2] == "B"]

    def etats(self, instants):
        """carnet (copie) juste après le dernier événement ≤ t, pour chaque t (trié)"""
        out = {}; L = Q.Livre(); vu = False; i = 0; ins = sorted(set(instants)); j = 0
        for t in ins:
            while i < len(self.fl) and self.fl[i][0] <= t:
                e = self.fl[i]; i += 1
                if e[2] == "B": L.charger(e[3], e[4]); vu = True
                elif e[2] == "P" and vu: L.maj(e[3], e[4], e[5])
            out[t] = L.copie() if vu else None
        return out


def vendeurs(L, X):
    """offres du côté X en (prix X en millièmes, taille), du meilleur au pire"""
    if L is None: return []
    if X == "Up": return sorted(L.a.items())
    return sorted(((1000 - c, s) for c, s in L.b.items()), key=lambda x: x[0])


def acheteurs(L, X):
    if L is None: return []
    if X == "Up": return sorted(L.b.items(), reverse=True)
    return sorted(((1000 - c, s) for c, s in L.a.items()), reverse=True)


def acheter(L, X, limite, qmax):
    """prise au plafond `limite` (millièmes) : parts, coût frais compris"""
    q = c = 0.0
    for p, sz in vendeurs(L, X):
        if p > limite: break
        k = min(sz, qmax - q)
        if k <= 1e-9: break
        pp = p / 1000; q += k; c += k * (pp + fee(pp))
    return q, c


# ======================================================================= simulateur maker (ordre fictif post-only)
def simuler_maker(cy, X, prix, t_arr, t_fin, qty, L_arr):
    """ordre d'achat fictif du côté X au prix `prix` (millièmes X), arrivé à t_arr, retiré à t_fin. Rend {borne: (parts, t premier rempl.)}.
    En coordonnées du carnet Up : X = Up → côté 0 au prix c ; X = Down → côté 1 au prix 1000 − prix."""
    side = 0 if X == "Up" else 1; c = prix if X == "Up" else 1000 - prix
    lvl = (L_arr.b if side == 0 else L_arr.a).get(c, 0.0) if L_arr else 0.0
    ahead = {b: lvl for b in BORNES}; rem = {b: qty for b in BORNES}; t1 = {b: None for b in BORNES}
    taille = lvl
    i0 = bisect.bisect_right(cy.T, t_arr); i1 = bisect.bisect_right(cy.T, t_fin)
    # transactions à notre niveau ou au-delà
    j0 = bisect.bisect_right(cy.trT, t_arr); j1 = bisect.bisect_right(cy.trT, t_fin + 60)
    pris = set()
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
            if cs == side and ((side == 0 and cm < c) or (side == 1 and cm > c)):      # transaction au-delà de notre prix : niveau épuisé
                for b in BORNES: remplir(b, e[6], e[0])
            continue
        if e[2] != "P" or e[3] != side or e[4] != c: continue
        z = e[5]; old = taille; taille = z
        if z >= old - 1e-9: continue
        d = old - z
        # part due aux transactions : transactions non encore attribuées à ce niveau dans [−5 ; +60] ms
        tv = 0.0
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


# ======================================================================= règles de Dublin (copie de evaluer())
def regles(fair_t, a_up, a_dn, h3, tleft):
    """fair_t = (pu, pu01, pu015) ; h3 = (fair3, a_up3, a_dn3) il y a ≥ 3 s ; rend [(nom, cote)]"""
    out = []
    pu, pu01, pu015 = fair_t
    for up in (True, False):
        a = (a_up if up else a_dn)
        if a is None: continue
        X = "Up" if up else "Down"; fair = pu if up else 1 - pu; edge = fair - a
        if h3:
            f3, au3, ad3 = h3; a3 = au3 if up else ad3
            if a3 is not None:
                g = lambda p, p3: (p if up else 1 - p, p3 if up else 1 - p3)
                if 0.03 <= a <= 0.97 and edge >= 0.20 and edge - (g(pu, f3[0])[1] - a3) >= 0.03: out.append(("V2-F ecart qui grandit", X))
                f1, f13 = g(pu01, f3[1])
                if 0.03 <= a <= 0.97 and f1 - a >= 0.20 and (f1 - a) - (f13 - a3) >= 0.03: out.append(("V2-F incertitude 0,01 %", X))
                if tleft > 60 and 0.15 <= a < 0.35 and edge >= 0.30 and fair - g(pu, f3[0])[1] >= 0.03: out.append(("cohorte A : zone + modele monte", X))
                f2, f23 = g(pu015, f3[2])
                if 0.03 <= a <= 0.97 and f2 - a >= 0.20 and (f2 - a) - (f23 - a3) >= 0.03: out.append(("cohorte B : V2-F corrige 0,015 %", X))
        if 0.02 <= a <= 0.98:
            if edge >= 0.30: out.append(("desaccord 30", X))
            if edge >= 0.20 and 60 < tleft <= 180: out.append(("desaccord 20 60-180 s", X))
            if edge >= 0.20 and 0.35 <= a < 0.65: out.append(("desaccord 20 jeton 0,35-0,65", X))
    return out


def fair_regle(nom, p):
    return p[1] if "0,01 %" in nom else (p[2] if nom.startswith("cohorte B") else p[0])


def main():
    dossier = sys.argv[1]
    fichiers = {int(os.path.basename(f).split(".")[0]): f for f in glob.glob(os.path.join(dossier, "**", "*.json.gz"), recursive=True)}
    fichiers = {k: v for k, v in fichiers.items() if k < HORS_ECH}
    SIG = [s for s in json.load(open(os.path.join(RACINE, "bot95", "rapide.json")))["signaux"] if s.get("gagnant") and s["start"] in fichiers and s["start"] < HORS_ECH]
    MK = [x for x in json.load(open(os.path.join(RACINE, "bot95", "rapide_maker.json"))) if x.get("type") != "resume" and x.get("resultat") and x["start"] in fichiers]
    cycles = sorted({s["start"] for s in SIG}); coupe = cycles[len(cycles) // 2]
    o = []; w = o.append
    w("# Bot95 — H766 à H775 : capturer l'avantage malgré la latence ? — PRÉLIMINAIRE\n")
    w(f"Généré le {time.strftime('%d.%m.%Y %H:%M', time.gmtime())} UTC. Cycles enregistrés à Dublin avant le 13.10 : {len(fichiers)} ; signaux Bot95 réglés sur ces cycles : "
      f"**{len(SIG)}** sur **{len(cycles)} cycles**. IC 90 % par rééchantillonnage de cycles. Validation chronologique : 1re moitié = cycles < "
      f"{time.strftime('%H:%M', time.gmtime(coupe))} UTC, 2e moitié après. Exécution preneur : décision + {LAT} ms de trajet + {RETARD} ms de retard Polymarket = {EXEC} ms. "
      f"Budget 50 $ par signal (comme Dublin). Aucun ordre, aucun fantôme touché.\n")

    LIG = []; CY = {}
    for st in cycles:
        cy = Cycle(fichiers[st]); CY[st] = cy
        S = [s for s in SIG if s["start"] == st]
        inst = []
        for s in S:
            t0 = s["tDecision"]
            inst += [t0 + max(d, 1) for d in DELAIS] + [t0 + LAT] + [t0 + EXEC + 500 * k for k in range(11)]
        E = cy.etats(inst)
        for s in S:
            t0 = s["tDecision"]; X = s["cote"]; a0 = int(round(s["a0"] * 1000)); y = 1.0 if s["gagne"] else 0.0; qmax = BUDGET / s["a0"]
            r = dict(s=s, st=st, X=X, a0=a0, y=y, qmax=qmax, mod=s["modele"], t0=t0, cap={})
            for d in DELAIS:
                for cp in PLAFONDS:
                    q, c = acheter(E[t0 + max(d, 1)], X, a0 + cp, qmax); r["cap"][(d, cp)] = (q, c, q * y - c)
            a0m = s.get("achetable0") or {}
            if a0m.get("q") is not None: r["cap"][(0, 0)] = (a0m["q"], a0m["c"], a0m["q"] * y - a0m["c"])     # 0 ms : mesure exacte de Dublin
            # contrôle : notre carnet contre ce que Dublin a vu
            r["ctrl"] = {d: ((s.get("apres") or {}).get(str(d)) or {}).get("q") for d in (50, 100, 250, 500)}; r["ctrl"][0] = (s.get("achetable0") or {}).get("q")
            # H774 : relances toutes les 500 ms pendant 5 s, au plafond +0 ou +2 c, si modèle − prix − frais ≥ 0,05 (modèle figé au signal)
            for nom, cp in (("relance", 0), ("relance +2 c", 20)):
                q = c = 0.0
                for k in range(11):
                    L = E[t0 + EXEC + 500 * k]; lim = a0 + cp
                    lim = min(lim, int(math.floor((s["modele"] - 0.05) * 1000)))        # jamais au-dessus de modèle − marge
                    lim2 = lim
                    while lim2 >= 0 and (lim2 / 1000) + fee(lim2 / 1000) > s["modele"] - 0.05: lim2 -= 1
                    dq, dc = acheter(L, X, lim2, qmax - q); q += dq; c += dc
                    if q >= qmax - 1e-6: break
                r[nom] = (q, c, q * y - c)
            # H770 maker au signal : meilleur acheteur + 1 c si l'écart vendeur-acheteur > 1 c (règle M1), sinon au meilleur acheteur
            L = E[t0 + LAT]; bb = acheteurs(L, X); aa = vendeurs(L, X)
            if bb and aa:
                b0 = bb[0][0]; prix = b0 + 10 if aa[0][0] - b0 > 10 else b0
                for hz in (10, 60):
                    res = simuler_maker(cy, X, prix, t0 + LAT, min(t0 + LAT + hz * 1000, (st + 300) * 1000), BUDGET / (prix / 1000), L)
                    r[f"maker{hz}"] = {b: (q, q * (y - prix / 1000), tt) for b, (q, tt) in res.items()}; r["prixMaker"] = prix
            LIG.append(r)
    n = len(LIG); par_cy = lambda X_: list({l["st"]: [m for m in X_ if m["st"] == l["st"]] for l in X_}.values())

    # ---------------------------------------------------------------- contrôle
    w("## 0. Contrôle de la reconstruction du carnet\n")
    for d in (0, 50, 100, 250, 500):
        v = [(l["cap"][(d, 0)][0], l["ctrl"][d]) for l in LIG if l["ctrl"].get(d) is not None]
        ok = np.mean([abs(a - b) <= max(1.0, 0.05 * b) for a, b in v]) if v else float("nan")
        w(f"- {d} ms : quantité achetable reconstruite = quantité vue par Dublin (± 5 %) dans {100 * ok:.0f} % des {len(v)} signaux.")
    w("")

    # ---------------------------------------------------------------- H766 / H768
    w("## 1. H766 — P&L et quantité exécutable selon la latence (preneur, prix du signal, plafond +0) — livrables « courbe P&L/latence », « quantités capturables », « P&L par signal initial »\n")
    w("P&L par **signal initial** = résultat en $ de ce que l'on aurait réellement pu acheter (0 si rien), frais compris, puis moyenne sur tous les signaux.\n")
    w("| Délai | Signaux exécutables | Parts / parts à 0 ms | P&L total ($) | P&L moyen par signal ($) | IC 90 % | par $ investi | 1re moitié / signal | 2e moitié / signal |\n|---|---|---|---|---|---|---|---|---|")
    q0tot = sum(l["cap"][(0, 0)][0] for l in LIG); COURBE = {}
    for d in DELAIS:
        k = (d, 0); pn = [l["cap"][k][2] for l in LIG]; cost = sum(l["cap"][k][1] for l in LIG)
        moy = float(np.mean(pn)); c_ = ic(par_cy(LIG), lambda s: float(np.mean([l["cap"][k][2] for l in s])))
        h1 = np.mean([l["cap"][k][2] for l in LIG if l["st"] < coupe]); h2 = np.mean([l["cap"][k][2] for l in LIG if l["st"] >= coupe])
        COURBE[d] = (moy, c_)
        w(f"| {d} ms{' (preneur réel)' if d == EXEC else (' (mesure Dublin)' if d == 0 else '')} | {sum(1 for l in LIG if l['cap'][k][0] > 0)} / {n} | {100 * sum(l['cap'][k][0] for l in LIG) / q0tot:.0f} % | {sum(pn):+.0f} | "
          f"{moy:+.2f} | [{c_[0]:+.2f} ; {c_[1]:+.2f}] | {100 * sum(pn) / cost if cost else 0:+.1f} % | {h1:+.2f} | {h2:+.2f} |")
    w("\n**Robustesse (preneur 164 ms, plafond +0)** — le résultat dépend-il de quelques gros gains ?\n")
    k = (EXEC, 0); pn = sorted([l["cap"][k][2] for l in LIG], reverse=True)
    w(f"- Médiane par signal : {np.median(pn):+.2f} $ ; part du P&L total venant des 5 meilleurs signaux : {100 * sum(pn[:5]) / sum(pn) if sum(pn) else 0:.0f} % ; "
      f"P&L sans les 5 meilleurs : {sum(pn[5:]):+.0f} $ ; sans les 10 meilleurs : {sum(pn[10:]):+.0f} $.")
    vu = {}
    for l in sorted(LIG, key=lambda l: l["t0"]): vu.setdefault((l["st"], l["X"]), l)
    U = list(vu.values()); pu_ = [l["cap"][k][2] for l in U]
    w(f"- **Décisions uniques** (un seul achat par cycle et par côté — le premier signal ; les variantes du même cycle achètent souvent le même billet) : {len(U)} décisions, "
      f"P&L {sum(pu_):+.0f} $, moyen {np.mean(pu_):+.2f} $ IC 90 % [{'%+.2f ; %+.2f' % ic(par_cy(U), lambda s_: float(np.mean([l['cap'][k][2] for l in s_])))}], "
      f"médiane {np.median(pu_):+.2f} $.")
    w("\n| Prix du signal | Signaux | Taux de gain | P&L 0 ms ($) | P&L 164 ms ($) | P&L 500 ms ($) | perte due à la latence 0→164 ms |\n|---|---|---|---|---|---|---|")
    for lo, hi in ((0, 0.10), (0.10, 0.20), (0.20, 0.35), (0.35, 1.0)):
        B_ = [l for l in LIG if lo <= l["s"]["a0"] < hi]
        if not B_: continue
        p0 = sum(l["cap"][(0, 0)][2] for l in B_); p1 = sum(l["cap"][(EXEC, 0)][2] for l in B_)
        w(f"| {lo:.2f}–{hi:.2f} | {len(B_)} | {100 * np.mean([l['y'] for l in B_]):.0f} % | {p0:+.0f} | {p1:+.0f} | {sum(l['cap'][(500, 0)][2] for l in B_):+.0f} | {p1 - p0:+.0f} |")
    pos = [d for d in DELAIS if COURBE[d][0] <= 0]; neg = [d for d in DELAIS if COURBE[d][1][1] < 0]
    w(f"\n## 2. H768 — Latence critique\n")
    w(f"- Premier délai où l'espérance moyenne par signal devient ≤ 0 : **{str(pos[0]) + ' ms' if pos else 'aucun jusqu’à 500 ms'}**.")
    w(f"- Premier délai où l'IC 90 % est entièrement négatif : **{str(neg[0]) + ' ms' if neg else 'aucun jusqu’à 500 ms'}**.")
    w(f"- Premier délai où l'IC 90 % ne contient plus que du positif : {', '.join(str(d) + ' ms' for d in DELAIS if COURBE[d][1][0] > 0) or 'aucun'}.\n")

    # ---------------------------------------------------------------- H767
    w("## 3. H767 — Pourquoi les offres disparaissent (livrable « analyse des offres disparues »)\n")
    w("Pour chaque signal : baisse des quantités vendues au prix du signal ou mieux entre la décision et +250 ms (puis +500 ms), et transactions qui consomment ce côté "
      "à ces prix (reçues jusqu'à 60 ms après). Consommé = min(baisse, transactions) ; retiré = le reste ; **indéterminé** si un carnet complet est rechargé dans la fenêtre "
      "ou si le flux est coupé (aucune attribution inventée).\n")
    CAUSE = collections.Counter(); VOLC = collections.Counter(); GAGNE = collections.defaultdict(list)
    for l in LIG:
        cy = CY[l["st"]]; t0 = l["t0"]; X = l["X"]; side = 1 if X == "Up" else 0
        q0 = (l["s"].get("achetable0") or {}).get("q") or 0; q250 = ((l["s"].get("apres") or {}).get("250") or {}).get("q", 0) or 0
        if q0 <= 0: continue
        disparu = q250 < 0.5 * q0
        lims = (lambda c: c <= l["a0"]) if X == "Up" else (lambda c: c >= 1000 - l["a0"])
        rech = any(t0 < tb <= t0 + 250 for tb in cy.B) or cy.C["coupe"]
        bais = 0.0; taille = {}
        L0 = cy.etats([t0])[t0]; taille = dict(L0.a if side == 1 else L0.b) if L0 else {}
        for e in cy.fl[bisect.bisect_right(cy.T, t0):bisect.bisect_right(cy.T, t0 + 250)]:
            if e[2] == "P" and e[3] == side and lims(e[4]):
                old = taille.get(e[4], 0.0); taille[e[4]] = e[5]
                if e[5] < old: bais += old - e[5]
        trv = sum(x[3] for x in cy.tr[bisect.bisect_right(cy.trT, t0):bisect.bisect_right(cy.trT, t0 + 310)] if x[1] == side and lims(x[2]))
        cons = min(bais, trv); ret = bais - cons
        if rech: cause = "indéterminé (carnet rechargé / flux coupé)"
        elif not disparu: cause = "pas disparue (≥ 50 % encore là à 250 ms)"
        elif bais <= 0: cause = "indéterminé (pas de baisse vue au niveau)"
        elif cons >= 0.5 * bais: cause = "consommée par des transactions"
        elif ret >= 0.5 * bais: cause = "retirée (annulation)"
        else: cause = "mixte"
        CAUSE[cause] += 1; VOLC[cause + "|c"] += cons; VOLC[cause + "|r"] += ret; GAGNE[cause].append(l["y"])
    w("| Cause | Signaux | Parts consommées | Parts retirées | Taux de gain du signal |\n|---|---|---|---|---|")
    for k, v in CAUSE.most_common():
        w(f"| {k} | {v} | {VOLC[k + '|c']:.0f} | {VOLC[k + '|r']:.0f} | {100 * np.mean(GAGNE[k]):.0f} % |")
    w("\nLecture : « consommée » = un autre preneur a acheté avant nous (course de vitesse) ; « retirée » = le vendeur a annulé (il a vu le même mouvement).\n")

    # ---------------------------------------------------------------- H769
    w("## 4. H769 — Prix plafond (livrable « gain marginal des prix plafonds »)\n")
    w("| Délai | Plafond | Signaux exécutables | Parts | P&L total ($) | P&L moyen / signal | IC 90 % | Gain marginal vs +0 ($) | 2e moitié / signal |\n|---|---|---|---|---|---|---|---|---|")
    for d in (EXEC, 250, 500):
        b0 = sum(l["cap"][(d, 0)][2] for l in LIG)
        for cp in PLAFONDS:
            k = (d, cp); pn = [l["cap"][k][2] for l in LIG]
            c_ = ic(par_cy(LIG), lambda s: float(np.mean([l["cap"][k][2] for l in s])))
            w(f"| {d} ms | +{cp // 10} c | {sum(1 for l in LIG if l['cap'][k][0] > 0)} | {sum(l['cap'][k][0] for l in LIG):.0f} | {sum(pn):+.0f} | {np.mean(pn):+.2f} | "
              f"[{c_[0]:+.2f} ; {c_[1]:+.2f}] | {sum(pn) - b0:+.0f} | {np.mean([l['cap'][k][2] for l in LIG if l['st'] >= coupe]):+.2f} |")
    w("")

    # ---------------------------------------------------------------- H774
    w("## 5. H774 — Alpha sans poursuite (abandon / deuxième chance / attente)\n")
    w("Achat seulement tant que modèle (figé au signal) − prix − frais ≥ 0,05.\n")
    w("| Politique | Signaux exécutés | Parts | P&L total ($) | moyen / signal | IC 90 % | 2e moitié / signal |\n|---|---|---|---|---|---|---|")
    POL = {"abandon immédiat (164 ms, +0)": lambda l: l["cap"][(EXEC, 0)], "deuxième chance (+164 ms puis 500 ms, plafond +2 c)": None,
           "attente : relances 5 s au prix du signal": lambda l: l["relance"], "attente : relances 5 s, plafond +2 c": lambda l: l["relance +2 c"]}
    def deux(l):
        q, c, p = l["cap"][(EXEC, 0)]
        if q > 0: return (q, c, p)
        return l["cap"][(500, 20)]
    POL["deuxième chance (+164 ms puis 500 ms, plafond +2 c)"] = deux
    for nom, f in POL.items():
        pn = [f(l)[2] for l in LIG]; c_ = ic(par_cy(LIG), lambda s: float(np.mean([f(l)[2] for l in s])))
        w(f"| {nom} | {sum(1 for l in LIG if f(l)[0] > 0)} | {sum(f(l)[0] for l in LIG):.0f} | {sum(pn):+.0f} | {np.mean(pn):+.2f} | [{c_[0]:+.2f} ; {c_[1]:+.2f}] | "
          f"{np.mean([f(l)[2] for l in LIG if l['st'] >= coupe]):+.2f} |")
    w("")

    # ---------------------------------------------------------------- H770
    w("## 6. H770 — Maker contre preneur sur les mêmes signaux\n")
    w("Maker simulé : offre d'achat posée à décision + 14 ms au meilleur acheteur (+1 c si l'écart > 1 c, règle de M1), retirée après 10 s ou 60 s ; "
      "file d'attente : prudente (seules les transactions nous font avancer), centrale (annulations réparties), optimiste (toutes les annulations devant nous). "
      "Gardé jusqu'au règlement, sans frais (maker).\n")
    w("| Voie | Signaux remplis | Parts | P&L total ($) | moyen / signal | IC 90 % | Taux de gain des remplis | 2e moitié / signal |\n|---|---|---|---|---|---|---|---|")
    LM = [l for l in LIG if "maker10" in l]
    pn = [l["cap"][(EXEC, 0)][2] for l in LM]
    w(f"| preneur 164 ms (Bot95 actuel) | {sum(1 for l in LM if l['cap'][(EXEC, 0)][0] > 0)} | {sum(l['cap'][(EXEC, 0)][0] for l in LM):.0f} | {sum(pn):+.0f} | {np.mean(pn):+.2f} | "
      f"{'[%+.2f ; %+.2f]' % ic(par_cy(LM), lambda s: float(np.mean([l['cap'][(EXEC, 0)][2] for l in s])))} | "
      f"{100 * np.mean([l['y'] for l in LM if l['cap'][(EXEC, 0)][0] > 0]):.0f} % | {np.mean([l['cap'][(EXEC, 0)][2] for l in LM if l['st'] >= coupe]):+.2f} |")
    for hz in (10, 60):
        for b in BORNES:
            g = lambda l: l[f"maker{hz}"][b]
            pn = [g(l)[1] for l in LM]; rem = [l for l in LM if g(l)[0] > 0]
            w(f"| maker {hz} s, file {b} | {len(rem)} | {sum(g(l)[0] for l in LM):.0f} | {sum(pn):+.0f} | {np.mean(pn):+.2f} | "
              f"{'[%+.2f ; %+.2f]' % ic(par_cy(LM), lambda s: float(np.mean([g(l)[1] for l in s])))} | {100 * np.mean([l['y'] for l in rem]) if rem else float('nan'):.0f} % | "
              f"{np.mean([g(l)[1] for l in LM if l['st'] >= coupe]):+.2f} |")
    # fantôme vivant M1 sur les mêmes signaux
    m1 = collections.defaultdict(list)
    for x in MK:
        if x["variante"].startswith("M1 "): m1[(x["start"], x["cote"], x["variante"][3:])].append(x)
    pairs = [(l, m1[(l["st"], l["X"], l["s"]["nom"])][0]) for l in LIG if m1.get((l["st"], l["X"], l["s"]["nom"]))]
    if pairs:
        w(f"\n**Fantôme vivant M1 (maker au signal, mesuré en direct) sur les mêmes signaux** : {len(pairs)} signaux appariés. "
          f"M1 prudent {sum(x['resultat']['prudent'] for _, x in pairs):+.0f} $, proportionnel {sum(x['resultat']['proportionnel'] for _, x in pairs):+.0f} $ ; "
          f"preneur 164 ms sur ces signaux {sum(l['cap'][(EXEC, 0)][2] for l, _ in pairs):+.0f} $ ; simulation maker 60 s centrale {sum(l['maker60']['centrale'][1] for l, _ in pairs if 'maker60' in l):+.0f} $. "
          f"(M1 est mis à l'échelle de 50 $ au prix maker.)\n")

    # ---------------------------------------------------------------- comparaison M4 / M8
    w("## 7. Comparaison contre Bot95 actuel, M4 et M8 (mêmes cycles)\n")
    cyc_mk = sorted({x["start"] for x in MK})
    if cyc_mk:
        w(f"Cycles communs avec les fantômes maker vivants : {len(cyc_mk)}.\n")
        w("| Moteur | Ordres / signaux | P&L prudent ($) | P&L proportionnel ($) | par cycle (prudent) |\n|---|---|---|---|---|")
        for fam in ("M4", "M8"):
            X_ = [x for x in MK if x["variante"].split()[0] == fam]
            w(f"| {fam} (vivant) | {len(X_)} | {sum(x['resultat']['prudent'] for x in X_):+.0f} | {sum(x['resultat']['proportionnel'] for x in X_):+.0f} | {sum(x['resultat']['prudent'] for x in X_) / len(cyc_mk):+.2f} |")
        lc = [l for l in LIG if l["st"] in set(cyc_mk)]
        w(f"| Bot95 preneur 164 ms (simulé) | {len(lc)} | {sum(l['cap'][(EXEC, 0)][2] for l in lc):+.0f} | — | {sum(l['cap'][(EXEC, 0)][2] for l in lc) / len(cyc_mk):+.2f} |")
        w(f"| Bot95 à 0 ms (borne idéale) | {len(lc)} | {sum(l['cap'][(0, 0)][2] for l in lc):+.0f} | — | {sum(l['cap'][(0, 0)][2] for l in lc) / len(cyc_mk):+.2f} |")
        w("\nM4 et M8 ne sont pas déclenchés par les signaux : comparaison par cycle, pas par signal.\n")

    # ---------------------------------------------------------------- H775 + H771–H773 : modèle reconstruit sur grille
    w("## 8. H775 — Décision anticipée (500 ms avant chaque signal) — livrables « signaux anticipables », « gagnants / perdants supplémentaires »\n")
    w("Le modèle de Dublin est recalculé hors ligne (copie de proba()). Validation au moment des signaux : voir la note. Grille de 100 ms sur tout le cycle ; "
      "première fois qu'une règle se déclenche dans le cycle (comme le bot). **Base** = mêmes flux que le bot ; **rapide** = on ajoute au prix Bybit/OKX le "
      "mouvement de Binance depuis cette observation (information disponible plus tôt). Exécution : décision + 164 ms, plafond = prix vu à la décision.\n")
    GR = {}; val = []
    for st in cycles:
        cy = CY[st]; prev = fichiers.get(st - 300)
        Mo = MD.Modele(MD.charger_ex([f for f in (prev, fichiers[st]) if f]), cy.strike, st + 300)
        grille = [st * 1000 + 100 * k for k in range(0, 2950)]
        E = cy.etats(grille)
        def meilleur(L, X):
            v = vendeurs(L, X); return v[0][0] / 1000 if v else None
        res = {}
        for mode in ("base", "rapide"):
            P = {}; fait = {}; sig = []
            for t in grille:
                p = Mo.proba(t / 1000, rapide=("bn" if mode == "rapide" else None))
                L = E[t]; au, ad = meilleur(L, "Up"), meilleur(L, "Down"); P[t] = (p, au, ad)
                if p is None or au is None or ad is None: continue
                tleft = st + 300 - t / 1000
                if tleft < 5: continue
                h = P.get(t - 3000); h3 = (h[0], h[1], h[2]) if h and h[0] is not None else None
                for nom, X in regles(p, au, ad, h3, tleft):
                    if nom in fait: continue
                    fait[nom] = t; a = au if X == "Up" else ad; sig.append(dict(nom=nom, X=X, t=t, a=a, fair=fair_regle(nom, p) if X == "Up" else 1 - fair_regle(nom, p)))
            res[mode] = (P, sig)
        GR[st] = res
        # validation du modèle au moment des signaux réels
        for s in SIG:
            if s["start"] != st: continue
            p = Mo.proba(s["tDecision"] / 1000)
            if p is not None: f = fair_regle(s["nom"], p); val.append(abs((f if s["cote"] == "Up" else 1 - f) - s["modele"]))
        # exécution des signaux de grille
        inst = [x["t"] + EXEC for m in res for x in res[m][1]]
        E2 = cy.etats(inst); gag = (CY[st].R.get("marche") or {})
        for m in res:
            for x in res[m][1]:
                win = None
                for s in SIG:
                    if s["start"] == st: win = s["gagnant"]; break
                x["y"] = None if win is None else (1.0 if win == x["X"] else 0.0)
                q, c = acheter(E2[x["t"] + EXEC], x["X"], int(round(x["a"] * 1000)), BUDGET / x["a"])
                x["q"], x["c"] = q, c; x["pnl"] = (q * x["y"] - c) if x["y"] is not None else None
    v = np.array(val)
    w(f"*Note de validation* : écart entre le modèle recalculé et le modèle enregistré au signal ≤ 0,005 pour {100 * np.mean(v <= 0.005):.0f} % des {len(v)} signaux "
      f"(médiane {np.median(v):.4f}) ; les écarts viennent surtout des signaux déclenchés par Bybit/OKX (l'enregistreur ne garde qu'une valeur par 50 ms).\n")
    # appariement base ↔ réel, base ↔ rapide
    nb = nr = nmatch = 0; avance = []; extra = []; perdus = []; communs = []
    for st in cycles:
        B = {x["nom"]: x for x in GR[st]["base"][1]}; Rr = {x["nom"]: x for x in GR[st]["rapide"][1]}
        reel = {s["nom"]: s for s in SIG if s["start"] == st}
        nb += len(B); nr += len(Rr); nmatch += sum(1 for k in reel if k in B and B[k]["X"] == reel[k]["cote"])
        for k in set(B) | set(Rr):
            b, r = B.get(k), Rr.get(k)
            if b and r and b["X"] == r["X"]:
                communs.append((st, b, r)); avance.append(b["t"] - r["t"])
            else:
                if r and r.get("y") is not None: extra.append((st, r))
                if b and b.get("y") is not None: perdus.append((st, b))
    w(f"- Signaux de grille « base » : {nb} ; signaux réels retrouvés par la grille (même règle, même côté, même cycle) : {nmatch} / {len(SIG)}.")
    w(f"- Signaux de grille « rapide » : {nr}. Appariés à un signal « base » (même règle et côté) : {len(communs)}.")
    if avance:
        A = np.array(avance)
        w(f"- Avance de la décision rapide sur la base : médiane {np.median(A):.0f} ms ; décidés plus tôt dans {100 * np.mean(A > 0):.0f} % des cas ; "
          f"**au moins 164 ms plus tôt : {int(np.sum(A >= 164))}** ; au moins 500 ms plus tôt : {int(np.sum(A >= 500))}.")
        pb = [b["pnl"] for st, b, r in communs if b["pnl"] is not None]; pr = [r["pnl"] for st, b, r in communs if r["pnl"] is not None]
        grp = lambda: list({st: [] for st, _, _ in communs}.keys())
        G_ = collections.defaultdict(list)
        for st, b, r in communs:
            if b["pnl"] is not None and r["pnl"] is not None: G_[st].append(r["pnl"] - b["pnl"])
        c_ = ic(list(G_.values()), lambda s: float(np.mean(s)))
        w(f"- Sur les mêmes opportunités : base {sum(pb):+.0f} $ ({np.mean(pb):+.2f} / signal), rapide {sum(pr):+.0f} $ ({np.mean(pr):+.2f} / signal) ; "
          f"différence moyenne {np.mean([x for g in G_.values() for x in g]):+.2f} $ / signal, IC 90 % [{c_[0]:+.2f} ; {c_[1]:+.2f}].")
    w(f"- **Signaux supplémentaires** (rapide seulement) : {len(extra)} — gagnants {sum(1 for _, r in extra if r['y'] == 1)}, perdants {sum(1 for _, r in extra if r['y'] == 0)}, "
      f"P&L exécuté {sum(r['pnl'] for _, r in extra if r['pnl'] is not None):+.0f} $.")
    w(f"- **Signaux perdus** (base seulement) : {len(perdus)} — gagnants {sum(1 for _, b in perdus if b['y'] == 1)}, perdants {sum(1 for _, b in perdus if b['y'] == 0)}, "
      f"P&L qu'ils auraient donné {sum(b['pnl'] for _, b in perdus if b['pnl'] is not None):+.0f} $.\n")

    # ---------------------------------------------------------------- H771–H773
    w("## 9. H771–H773 — Offres d'achat prépositionnées avant les signaux (livrable « valeur de la priorité maker »)\n")
    w("Règle sans regard vers le futur (modèle « base » recalculé toutes les 100 ms) : tant que modèle − meilleur vendeur ≥ 0,10 sur un côté (prix 0,03–0,97, "
      "plus de 10 s restantes), une offre d'achat est posée au meilleur acheteur de ce côté (arrivée + 14 ms) et gardée à son prix ; retirée (+ 14 ms) quand la "
      "condition tombe. Inventaire plafonné à 50 $ par côté et par cycle. Tout remplissage est gardé jusqu'au règlement, y compris quand aucun signal ne suit "
      "(« non désiré »).\n")
    PRE = {b: collections.Counter() for b in BORNES}; PRE_cy = {b: collections.defaultdict(float) for b in BORNES}
    couvre = {b: [] for b in BORNES}
    for st in cycles:
        cy = CY[st]; P, _ = GR[st]["base"]; ts_ = sorted(P)
        win = next(s["gagnant"] for s in SIG if s["start"] == st)
        reels = [s for s in SIG if s["start"] == st]
        for X in ("Up", "Down"):
            y = 1.0 if win == X else 0.0
            ep = []; deb = None
            for t in ts_:
                p, au, ad = P[t]; a = au if X == "Up" else ad
                ok = p is not None and a is not None and 0.03 <= a <= 0.97 and (st + 300 - t / 1000) > 10 and ((p[0] if X == "Up" else 1 - p[0]) - a >= 0.10)
                if ok and deb is None: deb = t
                if not ok and deb is not None: ep.append((deb, t)); deb = None
            if deb is not None: ep.append((deb, ts_[-1]))
            Ed = cy.etats([d + LAT for d, _ in ep])
            budget = {b: BUDGET for b in BORNES}
            for d, f in ep:
                L = Ed[d + LAT]; bb = acheteurs(L, X)
                if not bb: continue
                prix = bb[0][0]
                if prix <= 0: continue
                res = simuler_maker(cy, X, prix, d + LAT, f + LAT, BUDGET / (prix / 1000), L)
                sig_ep = [s for s in reels if s["cote"] == X and d <= s["tDecision"] <= f + LAT]
                for b in BORNES:
                    qmax = budget[b] / (prix / 1000); q = min(res[b][0], qmax)
                    if q <= 0: continue
                    budget[b] -= q * prix / 1000; pn = q * (y - prix / 1000)
                    tag = "désiré (un signal Bot95 de ce côté pendant l'offre)" if sig_ep else "non désiré (aucun signal)"
                    PRE[b][tag + "|q"] += q; PRE[b][tag + "|p"] += pn; PRE[b][tag + "|n"] += 1; PRE_cy[b][st] += pn
                    if sig_ep: couvre[b].append((st, X, sig_ep[0]["nom"], q, pn))
    w("| File | Remplissages désirés : parts | P&L ($) | Remplissages non désirés : parts | P&L ($) | Total ($) | IC 90 % total par cycle |\n|---|---|---|---|---|---|---|")
    for b in BORNES:
        D_ = "désiré (un signal Bot95 de ce côté pendant l'offre)"; N_ = "non désiré (aucun signal)"
        tot = PRE[b][D_ + "|p"] + PRE[b][N_ + "|p"]
        vals = [[PRE_cy[b].get(st, 0.0)] for st in cycles]
        c_ = ic(vals, lambda s: float(np.mean(s)))
        w(f"| {b} | {PRE[b][D_ + '|q']:.0f} | {PRE[b][D_ + '|p']:+.0f} | {PRE[b][N_ + '|q']:.0f} | {PRE[b][N_ + '|p']:+.0f} | {tot:+.0f} | [{c_[0]:+.1f} ; {c_[1]:+.1f}] / cycle |")
    # valeur de la priorité : sur les signaux couverts par une offre prépositionnée, comparer au maker posé AU signal
    w("\n**Valeur de la priorité** — signaux réels couverts par une offre prépositionnée : parts et P&L de l'offre prépositionnée contre l'offre posée au signal (60 s).\n")
    w("| File | Signaux couverts | Prépositionnée : parts | P&L | Au signal : parts | P&L |\n|---|---|---|---|---|---|")
    idx = {(l["st"], l["X"], l["s"]["nom"]): l for l in LIG}
    for b in BORNES:
        C_ = [(c, idx.get((c[0], c[1], c[2]))) for c in couvre[b]]; C_ = [(c, l) for c, l in C_ if l and "maker60" in l]
        w(f"| {b} | {len(C_)} | {sum(c[3] for c, _ in C_):.0f} | {sum(c[4] for c, _ in C_):+.0f} | {sum(l['maker60'][b][0] for _, l in C_):.0f} | {sum(l['maker60'][b][1] for _, l in C_):+.0f} |")
    w("")
    w("## Limites\n- Une seule journée, peu de cycles : tout est préliminaire ; aucune règle n'a été ajustée sur ces résultats.\n"
      "- Carnet suivi seulement à ±3 c du meilleur prix entre deux photos complètes (10 s).\n- File d'attente maker : trois bornes, la vraie valeur est entre prudente et optimiste.\n"
      "- Modèle recalculé : fidèle pour les signaux déclenchés par le carnet, moins pour ceux déclenchés par Bybit/OKX (une valeur par 50 ms enregistrée).\n"
      "- Les fantômes vivants M1/M4/M8 ne couvrent qu'une partie des cycles.\n")
    open(SORTIE, "w").write("\n".join(o)); print("\n".join(o))


if __name__ == "__main__":
    main()
