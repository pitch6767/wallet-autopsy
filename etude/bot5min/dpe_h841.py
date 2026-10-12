"""BOT95 — DYNAMIC POSITION ENGINE : H841 à H860 (Pitch, 12.10.2026 12:49 et 12:53). PROTOCOLE PRÉ-ENREGISTRÉ (ce fichier tel que committé
avant le calcul de validation et de test). Hors ligne ; aucun ordre ; aucun bot actif, H816, H821, R4 ni fantôme modifié ; aucun nouveau fantôme ;
période réservée (≥ 13.10.2026) jamais lue.

DONNÉES : cycles Dublin (carnet Polymarket Up complet toutes les 10 s + chaque changement à ±3 c, carnet Down = miroir), prix des places et
  Chainlink, carnets Binance (H852). Résultat officiel (bot95/reglements.json, sinon gagnant Dublin, sinon moyenne 60 s officielle reçue).
DÉCOUPAGE (chronologique, figé) : test INÉDIT = cycles commençant le 12.10.2026 à 06:00 UTC ou après (jamais utilisés par aucune étude) ;
  avant : apprentissage = 2/3 premiers, validation = 1/3 suivant.
PROBABILITÉ (la même pour toutes les politiques) : modèle de règlement M0 (Chainlink, moyenne finale exacte, volatilité 300 s) recalibré par
  logistique sur l'apprentissage (décisions toutes les 10 s). Sensibilité : même chose sans recalibrage.
REJEU : décision chaque seconde de 10 à 290 s après le début du cycle, avec le carnet observé à t ; exécution preneur à t + 164 ms sur le carnet
  enregistré, limitée au prix observé à t (achat : vendeurs ≤ prix vu ; vente : acheteurs ≥ prix vu), quantités affichées seulement ; une quantité
  déjà prise par nous à un prix reste indisponible 5 s. Frais preneur 0,07·p·(1−p) par part à l'achat et à la vente. Aucun ordre maker (les études
  H804–H815 les ont tous trouvés négatifs) : les trois bornes de file ne s'appliquent donc pas. Paires Up + Down fusionnées dès qu'elles existent
  (1 $ par paire, libère le capital). Budget : 50 $ de capital net engagé par cycle au plus (achats − ventes − fusions), jamais dépassé.
SIGNAL D'ENTRÉE COMMUN : première seconde où l'avantage net d'un côté X, p_X − prix vendeur − frais, atteint e ; e ∈ {0,05 ; 0,10 ; 0,15}
  choisi sur l'apprentissage pour la référence A, puis le même e pour toutes les politiques.
POLITIQUES (paramètres fixés ici, aucun réglage sur la validation ou le test) :
  A  achat unique 50 $, conservation.                       B  achats fractionnés à horaires fixes : 10 $ au signal puis 10 $ toutes les 30 s.
  C  couverture statique : 40 $ côté X + 10 $ côté opposé.   D  sortie partielle simple : A, vente de 50 % si acheteur ≥ prix moyen + 0,20.
  G  abstention.
  H857 échelle conditionnelle : 10 $ à chaque seconde où l'avantage ≥ e, au moins 10 s d'écart, 5 tranches au plus.
  H842 achat sur repli : 20 $ au signal, puis 10 $ si le vendeur X a baissé de ≥ 3 c depuis l'entrée ET l'avantage recalculé ≥ e (3 fois max).
  H854a vente d'une jambe : A ; si p_X tombe de ≥ 0,15 sous p_X à l'entrée → vente de 50 % de X.
  H854b achat de l'opposé : A ; même déclencheur → achat de l'opposé pour la même quantité (50 % de X), dans la limite du budget.
  H851/H858 rotation : A ; vente de tout X si acheteur − frais − p_X ≥ 0,05 ; rachat si l'avantage repasse ≥ e (3 allers-retours max).
  H849/H853/H845 verrou de paire : A ; achat de l'opposé pour toute la quantité non appariée dès que coût moyen X + vendeur opposé + frais ≤ 0,99.
  H850 cliquet : A ; vente de 25 % à chaque hausse de l'acheteur de 0,10 au-dessus du dernier palier (départ : prix moyen), 3 fois max.
  H852 couverture au retournement : A ; si le modèle court terme du carnet (H834 : logistique apprise sur l'apprentissage, hausse à 30 s)
       donne ≥ 0,65 contre X ET p_X a perdu ≥ 0,05 depuis l'entrée → achat de l'opposé pour 50 % de X (une fois).
  H856 couverture avant la moyenne finale : A ; aux points 90/60/45/30/15 s restants, si p_X < 0,35 et X non apparié → vente de 50 % de X (une fois).
  H859/H847 DPE : chaque seconde, une action au plus, par ordre : fusion ; verrou de paire (règle H849) ; vente de 10 $ de X si acheteur − frais
       − p_X ≥ 0,05 ; achat de 10 $ du côté dont l'avantage ≥ e (pas de moyenne à la baisse automatique : l'achat exige l'avantage recalculé) ;
       sinon attendre. Budget 50 $.
  H860 tournoi : toutes les politiques sur les mêmes cycles ; IC 90 % par cycles de l'écart avec A ; IC corrigé de Bonferroni (14 comparaisons).
  H848 combinaison : construite seulement si au moins un composant bat A sur la validation ET le test avec IC corrigé > 0 (sinon non construite).
  H855 carte des occasions : par seconde, avantage exécutable à 164 ms (quantité et coût), par temps restant, sans sélection a posteriori.
MESURES : P&L net, par cycle, par $ de capital maximal, transactions, frais, coût d'écart (prix payé − milieu), parts, capital maximal, pire cycle,
  drawdown, expected shortfall 5 %, cycles gagnants, jackpots (cycle ≥ +50 $), écart avec A ; paires verrouillées et jambes isolées ;
  journal d'inventaire seconde par seconde (DPE, test) dans resultat_dpe_h841_journal.csv.gz.
CRITÈRE : une politique « bat le hold » seulement si l'IC corrigé de l'écart avec A sur le TEST inédit est entièrement > 0.
Usage : python3 etude/bot5min/dpe_h841.py dossier_cycles_dublin [--controle]  (--controle = apprentissage et validation seulement)"""
import os, sys, glob, json, gzip, math, time, collections, bisect
import numpy as np

ICI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, ICI)
import latence_h766 as LH, liquidite_h833 as L
CONTROLE = "--controle" in sys.argv; RESERVE = 1791849600; TEST_DEB = 1791784800
SORTIE = os.path.join(ICI, "resultat_dpe_h841" + ("_controle" if CONTROLE else "") + ".md")
EXEC = 164; BUDGET = 50.0; TRANCHE = 10.0; RNG = np.random.default_rng(841)
fee = lambda p: 0.07 * p * (1 - p)
lg = L.lg
POL = ["A", "B", "C", "D", "G", "H857", "H842", "H854a", "H854b", "H851/H858", "H849", "H850", "H852", "H856", "H859 DPE"]


class Inv:
    def __init__(s): s.q = {"Up": 0.0, "Down": 0.0}; s.cout = {"Up": 0.0, "Down": 0.0}; s.cash = 0.0; s.maxcap = 0.0; s.n = 0; s.frais = 0.0; s.ecart = 0.0
    def cap(s): return max(-s.cash, 0.0)
    def libre(s): return BUDGET - s.cap()
    def moy(s, X): return s.cout[X] / s.q[X] if s.q[X] > 1e-9 else None
    def fusion(s):
        m = min(s.q["Up"], s.q["Down"])
        if m > 1e-9:
            for X in ("Up", "Down"): s.cout[X] *= (s.q[X] - m) / s.q[X]; s.q[X] -= m
            s.cash += m; s.paires = getattr(s, "paires", 0) + m


class Moteur:
    """exécution sur le carnet enregistré ; liquidité prise par nous indisponible 5 s"""
    def __init__(s, E): s.E = E; s.pris = []
    def dispo(s, t, X, side, px):
        return sum(q for (tt, XX, sd, p, q) in s.pris if XX == X and sd == side and p == px and t - tt < 5000)
    def acheter(s, inv, t, X, dollars, lim, mid):
        dollars = min(dollars, inv.libre())
        if dollars < 0.5 or lim is None: return 0.0
        q = c = 0.0
        for px, sz in vend(s.E[t + EXEC], X):
            if px > lim: break
            sz = sz - s.dispo(t, X, "a", px)
            if sz <= 1e-9: continue
            pp = px / 1000; u = pp + fee(pp); k = min(sz, (dollars - c) / u)
            if k <= 1e-9: break
            q += k; c += k * u; s.pris.append((t, X, "a", px, k)); inv.frais += k * fee(pp); inv.ecart += k * (pp - mid) if mid else 0
        if q > 0:
            inv.q[X] += q; inv.cout[X] += c; inv.cash -= c; inv.n += 1; inv.maxcap = max(inv.maxcap, inv.cap())
        return q
    def vendre(s, inv, t, X, parts, lim, mid):
        parts = min(parts, inv.q[X])
        if parts <= 1e-9 or lim is None: return 0.0
        q = r = 0.0
        for px, sz in ach(s.E[t + EXEC], X):
            if px < lim: break
            sz = sz - s.dispo(t, X, "b", px)
            if sz <= 1e-9: continue
            pp = px / 1000; k = min(sz, parts - q)
            if k <= 1e-9: break
            q += k; r += k * (pp - fee(pp)); s.pris.append((t, X, "b", px, k)); inv.frais += k * fee(pp); inv.ecart += k * (mid - pp) if mid else 0
        if q > 0:
            m = inv.moy(X); inv.cout[X] -= q * m; inv.q[X] -= q; inv.cash += r; inv.n += 1
        return q


def vend(Lc, X):
    """vendeurs du côté X (prix en millièmes, taille), du meilleur au pire, sur un carnet compact (A = vendeurs Up, B = acheteurs Up)"""
    if Lc is None: return []
    return Lc[0] if X == "Up" else [(1000 - c, q) for c, q in Lc[1]]


def ach(Lc, X):
    if Lc is None: return []
    return Lc[1] if X == "Up" else [(1000 - c, q) for c, q in Lc[0]]


def compact(Lv):
    if Lv is None: return None
    return (sorted(Lv.a.items())[:15], sorted(Lv.b.items(), reverse=True)[:15])


def meilleur(Lv, X, cote):
    v = (vend(Lv, X) if cote == "a" else ach(Lv, X))
    return v[0][0] if v else None


def simuler(pol, cy_info, e, journal=None):
    """une politique sur un cycle ; renvoie l'inventaire final et le P&L"""
    st, E, PT, y, CT = cy_info["st"], cy_info["E"], cy_info["p"], cy_info["y"], cy_info.get("court")
    inv = Inv(); M = Moteur(E); mem = {}
    if pol == "G": return inv, 0.0
    for k, t in enumerate(cy_info["T"]):
        Lo = E[t]
        if Lo is None: continue
        rest = 300 - (t // 1000 - st); pU = PT[k]
        if pU is None: continue
        pX = {"Up": pU, "Down": 1 - pU}
        ask = {X: meilleur(Lo, X, "a") for X in ("Up", "Down")}; bid = {X: meilleur(Lo, X, "b") for X in ("Up", "Down")}
        mid = {X: ((ask[X] + bid[X]) / 2000 if ask[X] and bid[X] else None) for X in ("Up", "Down")}
        edge = {X: (pX[X] - ask[X] / 1000 - fee(ask[X] / 1000)) if ask[X] else -9 for X in ("Up", "Down")}
        inv.fusion()
        X0 = mem.get("X")
        if X0 is None:
            if rest < 20: continue
            Xb = max(edge, key=edge.get)
            if edge[Xb] < e: continue
            mem.update(X=Xb, t0=t, p0=pX[Xb], a0=ask[Xb])
            X0 = Xb
            dol = {"A": BUDGET, "D": BUDGET, "H854a": BUDGET, "H854b": BUDGET, "H851/H858": BUDGET, "H849": BUDGET, "H850": BUDGET, "H852": BUDGET,
                   "H856": BUDGET, "B": TRANCHE, "H857": TRANCHE, "H859 DPE": TRANCHE, "H842": 20.0, "C": 40.0}[pol]
            M.acheter(inv, t, X0, dol, ask[X0], mid[X0]); mem["last"] = t; mem["n"] = 1
            if pol == "C":
                Y = "Down" if X0 == "Up" else "Up"; M.acheter(inv, t, Y, 10.0, ask[Y], mid[Y])
            mem["palier"] = inv.moy(X0)
            if journal is not None: journal.append((st, t, pol, "entrée " + X0, inv.q["Up"], inv.q["Down"], round(inv.cash, 3), round(pU, 4)))
            continue
        X = X0; Y = "Down" if X == "Up" else "Up"; act = None
        if pol == "B" and t - mem["last"] >= 30000 and rest >= 20 and mem["n"] < 5:
            M.acheter(inv, t, X, TRANCHE, ask[X], mid[X]); mem["last"] = t; mem["n"] += 1; act = "achat fixe"
        elif pol == "H857" and t - mem["last"] >= 10000 and mem["n"] < 5 and edge[X] >= e and rest >= 20:
            M.acheter(inv, t, X, TRANCHE, ask[X], mid[X]); mem["last"] = t; mem["n"] += 1; act = "palier"
        elif pol == "H842" and mem["n"] < 4 and ask[X] and ask[X] <= mem["a0"] - 30 and edge[X] >= e and rest >= 20:
            M.acheter(inv, t, X, TRANCHE, ask[X], mid[X]); mem["n"] += 1; mem["a0"] = ask[X]; act = "repli"
        elif pol == "D" and not mem.get("fait") and bid[X] and inv.moy(X) and bid[X] / 1000 >= inv.moy(X) + 0.20:
            M.vendre(inv, t, X, inv.q[X] * 0.5, bid[X], mid[X]); mem["fait"] = 1; act = "sortie partielle"
        elif pol in ("H854a", "H854b") and not mem.get("fait") and pX[X] <= mem["p0"] - 0.15:
            if pol == "H854a": M.vendre(inv, t, X, inv.q[X] * 0.5, bid[X], mid[X])
            else:
                qv = inv.q[X] * 0.5; a = ask[Y]
                if a: M.acheter(inv, t, Y, qv * (a / 1000 + fee(a / 1000)), a, mid[Y])
            mem["fait"] = 1; act = "protection"
        elif pol == "H851/H858":
            if inv.q[X] > 1e-6 and bid[X] and bid[X] / 1000 - fee(bid[X] / 1000) - pX[X] >= 0.05:
                M.vendre(inv, t, X, inv.q[X], bid[X], mid[X]); mem["ventes"] = mem.get("ventes", 0) + 1; act = "vente rotation"
            elif inv.q[X] <= 1e-6 and mem.get("ventes", 0) <= 3 and edge[X] >= e and rest >= 20:
                M.acheter(inv, t, X, BUDGET, ask[X], mid[X]); act = "rachat"
        elif pol == "H849":
            nap = inv.q[X] - inv.q[Y]
            if nap > 1e-6 and ask[Y] and inv.moy(X) is not None and inv.moy(X) + ask[Y] / 1000 + fee(ask[Y] / 1000) <= 0.99:
                M.acheter(inv, t, Y, nap * (ask[Y] / 1000 + fee(ask[Y] / 1000)), ask[Y], mid[Y]); act = "verrou"
        elif pol == "H850" and mem.get("n50", 0) < 3 and bid[X] and mem["palier"] and bid[X] / 1000 >= mem["palier"] + 0.10:
            M.vendre(inv, t, X, inv.q[X] * 0.25, bid[X], mid[X]); mem["palier"] = bid[X] / 1000; mem["n50"] = mem.get("n50", 0) + 1; act = "cliquet"
        elif pol == "H852" and not mem.get("fait") and CT is not None and CT[k] is not None:
            contre = (1 - CT[k]) if X == "Up" else CT[k]
            if contre >= 0.65 and pX[X] <= mem["p0"] - 0.05 and ask[Y]:
                qv = inv.q[X] * 0.5; M.acheter(inv, t, Y, qv * (ask[Y] / 1000 + fee(ask[Y] / 1000)), ask[Y], mid[Y]); mem["fait"] = 1; act = "couverture carnet"
        elif pol == "H856" and not mem.get("fait") and rest in (90, 60, 45, 30, 15) and pX[X] < 0.35 and inv.q[X] - inv.q[Y] > 1e-6:
            M.vendre(inv, t, X, (inv.q[X] - inv.q[Y]) * 0.5, bid[X], mid[X]); mem["fait"] = 1; act = "couverture finale"
        elif pol == "H859 DPE":
            Z = None
            for S_ in (X, Y):
                T_ = "Down" if S_ == "Up" else "Up"; nap = inv.q[S_] - inv.q[T_]
                if nap > 1e-6 and ask[T_] and inv.moy(S_) is not None and inv.moy(S_) + ask[T_] / 1000 + fee(ask[T_] / 1000) <= 0.99:
                    M.acheter(inv, t, T_, nap * (ask[T_] / 1000 + fee(ask[T_] / 1000)), ask[T_], mid[T_]); Z = "verrou"; break
            if Z is None:
                for S_ in (X, Y):
                    if inv.q[S_] > 1e-6 and bid[S_] and bid[S_] / 1000 - fee(bid[S_] / 1000) - pX[S_] >= 0.05:
                        M.vendre(inv, t, S_, min(inv.q[S_], TRANCHE / (bid[S_] / 1000)), bid[S_], mid[S_]); Z = "vente"; break
            if Z is None and rest >= 20:
                Sb = max(edge, key=edge.get)
                if edge[Sb] >= e and inv.libre() >= 1: M.acheter(inv, t, Sb, TRANCHE, ask[Sb], mid[Sb]); Z = "achat " + Sb
            act = Z
        if journal is not None and (act or k % 10 == 0): journal.append((st, t, pol, act or "attente", round(inv.q["Up"], 3), round(inv.q["Down"], 3), round(inv.cash, 3), round(pU, 4)))
    inv.fusion()
    pnl = inv.cash + inv.q["Up"] * y + inv.q["Down"] * (1 - y)
    return inv, pnl


def mesures(R, ref=None, sts=None):
    v = np.array([R[s][1] for s in sts]); cap = np.array([R[s][0].maxcap for s in sts])
    act = v != 0
    cum = np.cumsum(v); dd = float(np.max(np.maximum.accumulate(np.concatenate([[0], cum]))[1:] - cum)) if len(v) else 0
    es = float(np.mean(np.sort(v)[:max(1, int(0.05 * len(v)))])) if len(v) else 0
    return dict(tot=v.sum(), n=int(act.sum()), moy=v[act].mean() if act.any() else 0, parcap=v.sum() / max(cap.sum(), 1e-9), tx=sum(R[s][0].n for s in sts),
                frais=sum(R[s][0].frais for s in sts), ecart=sum(R[s][0].ecart for s in sts), capmax=cap.max() if len(cap) else 0, pire=v.min() if len(v) else 0,
                dd=dd, es=es, gagn=int((v > 0).sum()), jack=int((v >= 50).sum()), paires=sum(getattr(R[s][0], "paires", 0) for s in sts),
                isol=sum(abs(R[s][0].q["Up"] - R[s][0].q["Down"]) for s in sts))


def ic_cy(d, alpha=0.10, B=4000):
    d = np.asarray(d, float)
    if len(d) < 3: return (float("nan"), float("nan"))
    idx = RNG.integers(0, len(d), (B, len(d))); m = d[idx].sum(1)
    return float(np.percentile(m, 100 * alpha / 2)), float(np.percentile(m, 100 * (1 - alpha / 2)))


def main():
    global EXEC
    t_go = time.time(); o = []; w = o.append
    G, cyc = L.grille(sys.argv[1]); P = L.preparer(G); L.P_sd1 = P["sd1"]; Y = L.resultats_officiels(cyc)
    cycles = sorted(s for s in cyc if s in Y and s < RESERVE)
    avant = [s for s in cycles if s < TEST_DEB]; n_tr = len(avant) * 2 // 3
    TR, VA, TE = avant[:n_tr], avant[n_tr:], [s for s in cycles if s >= TEST_DEB]
    if CONTROLE: TE = []
    w(f"# Bot95 — Dynamic Position Engine H841–H860 ({'CONTRÔLE : apprentissage et validation' if CONTROLE else 'apprentissage / validation / test inédit'})\n")
    w(f"Généré le {time.strftime('%d.%m.%Y %H:%M', time.gmtime())} UTC. Cycles avec résultat officiel : apprentissage {len(TR)}, validation {len(VA)}, "
      f"test inédit {len(TE)} (≥ 12.10 06:00 UTC). Budget 50 $ par cycle, exécution preneur à 164 ms sur le carnet enregistré. Aucun ordre ; aucun fantôme "
      "modifié ; période réservée non lue.\n")
    # probabilité recalibrée (apprentissage)
    Xc, yc = [], []
    for st in TR:
        for r in range(290, 10, -10):
            m = L.m0(G, cyc, st, r)
            if m: Xc.append([lg(m[0])]); yc.append(Y[st])
    bA = L.ajuster(np.array(Xc), np.array(yc), 0.1)
    w(f"Probabilité : M0 recalibré, logit(p) = {bA[0]:+.3f} + {bA[1]:.3f} × logit(M0), appris sur {len(yc)} décisions d'apprentissage.\n")
    # modèle court terme du carnet (H852), appris sur l'apprentissage
    Ic = [i for st in TR for i in range(st - G["t0"] + 10, st - G["t0"] + 270, 3) if 620 <= i < G["n"] - 31 and np.isfinite(G["bid"][i]) and np.isfinite(G["bn"][i + 30]) and np.isfinite(P["sd1"][i])]
    ctrl = lambda i: [(G["bn"][i] - G["bn"][i - 1]) / P["sd1"][i], (G["bn"][i] - G["bn"][i - 5]) / P["sd1"][i], (G["bn"][i] - G["bn"][i - 30]) / P["sd1"][i], P["sd1"][i]]
    Xs = np.nan_to_num(np.array([ctrl(i) + L.feats(G, P, i)[1] for i in Ic])); mu_s, sd_s = Xs.mean(0), Xs.std(0) + 1e-9
    bS = L.ajuster((Xs - mu_s) / sd_s, np.array([G["bn"][i + 30] > G["bn"][i] for i in Ic], float), 2.0)

    def preparer_cycle(st, recal=True):
        cy = LH.Cycle(cyc[st]["f"]); T = [st * 1000 + s * 1000 for s in range(10, 291)]
        E = {k: compact(v) for k, v in cy.etats(T + [t + EXEC for t in T]).items()}; p, court = [], []
        for t in T:
            rest = 300 - (t // 1000 - st); m = L.m0(G, cyc, st, rest)
            if m is None: p.append(None); court.append(None); continue
            p.append(float(L.predire(bA, np.array([[lg(m[0])]]))[0]) if recal else m[0])
            i = m[2]
            if 620 <= i < G["n"] and np.isfinite(G["bid"][i]) and np.isfinite(P["sd1"][i]):
                x = np.nan_to_num(np.array([ctrl(i) + L.feats(G, P, i)[1]])); court.append(float(L.predire(bS, (x - mu_s) / sd_s)[0]))
            else: court.append(None)
        return dict(st=st, E=E, T=T, p=p, court=court, y=Y[st])

    C_ = {}
    for st in TR + VA + TE: C_[st] = preparer_cycle(st)
    # choix de e sur l'apprentissage (référence A)
    choix = {e: sum(simuler("A", C_[s], e)[1] for s in TR) for e in (0.05, 0.10, 0.15)}
    e = max(choix, key=choix.get)
    w(f"Seuil d'avantage e choisi sur l'apprentissage (politique A) : {e:.2f} (P&L apprentissage : " + ", ".join(f"e={k:.2f} → {v:+.0f} $" for k, v in choix.items()) + ").\n")
    # H855 carte des occasions
    w("## 1. H855 — Carte des occasions exécutables (toutes périodes, chronologique)\n")
    w("| Temps restant | Secondes observées | Avantage ≥ 0,05 | Avantage ≥ 0,10 | Parts achetables à 164 ms au prix vu (médiane, si ≥ 0,05) |\n|---|---|---|---|---|")
    occ = collections.defaultdict(lambda: [0, 0, 0, []])
    for st, c in C_.items():
        if st in TE and CONTROLE: continue
        for k, t in enumerate(c["T"]):
            Lo = c["E"][t]; pU = c["p"][k]
            if Lo is None or pU is None: continue
            rest = 300 - (t // 1000 - st); b = (rest - 1) // 60
            best = -9; Xb = None
            for X, pX in (("Up", pU), ("Down", 1 - pU)):
                a = meilleur(Lo, X, "a")
                if a is not None and pX - a / 1000 - fee(a / 1000) > best: best = pX - a / 1000 - fee(a / 1000); Xb = X; ab = a
            o_ = occ[b]; o_[0] += 1; o_[1] += best >= 0.05; o_[2] += best >= 0.10
            if best >= 0.05: o_[3].append(sum(sz for px, sz in vend(c["E"][t + EXEC], Xb) if px <= ab))
    for b in sorted(occ, reverse=True):
        o_ = occ[b]; w(f"| {b * 60 + 1}–{b * 60 + 60} s | {o_[0]} | {100 * o_[1] / max(o_[0], 1):.1f} % | {100 * o_[2] / max(o_[0], 1):.1f} % | {np.median(o_[3]) if o_[3] else 0:.0f} |")

    # tournoi
    w("\n## 2. H841–H860 — Tableau des politiques\n")
    journal = []
    res = {}
    for nom, S_ in (("apprentissage", TR), ("validation", VA), ("TEST inédit", TE)):
        if not S_: continue
        R = {pol: {s: simuler(pol, C_[s], e, journal if (pol == "H859 DPE" and nom == "TEST inédit") else None) for s in S_} for pol in POL}
        res[nom] = (R, S_)
        w(f"### {nom} ({len(S_)} cycles)\n")
        w("| Politique | Cycles actifs | P&L ($) | Par cycle actif | Par $ de capital max | Transactions | Frais ($) | Coût d'écart ($) | Capital max | Pire cycle | Drawdown | ES 5 % | Cycles gagnants | Jackpots (≥ 50 $) | Paires fusionnées | Parts isolées | Écart avec A ($) | IC 90 % | IC corrigé (14) |\n"
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
        a = np.array([R["A"][s][1] for s in S_])
        for pol in POL:
            m = mesures(R[pol], sts=S_); d = np.array([R[pol][s][1] for s in S_]) - a
            c1 = ic_cy(d); c2 = ic_cy(d, 0.10 / 14)
            w(f"| {pol} | {m['n']} | {m['tot']:+.0f} | {m['moy']:+.2f} | {100 * m['parcap']:+.1f} % | {m['tx']} | {m['frais']:.0f} | {m['ecart']:.0f} | {m['capmax']:.0f} | {m['pire']:+.0f} | "
              f"{m['dd']:.0f} | {m['es']:+.0f} | {m['gagn']} | {m['jack']} | {m['paires']:.0f} | {m['isol']:.0f} | {d.sum():+.0f} | "
              + ("—" if pol == "A" else f"[{c1[0]:+.0f} ; {c1[1]:+.0f}]") + " | " + ("—" if pol == "A" else f"[{c2[0]:+.0f} ; {c2[1]:+.0f}]") + " |")
        w("")
    # sensibilité : probabilité non recalibrée et latence 300 ms (A et DPE), test ou validation
    S_ = TE or VA; nom = "test inédit" if TE else "validation"
    w(f"## 3. Sensibilité ({nom})\n")
    w("| Variante | A ($) | H859 DPE ($) | H849 verrou ($) |\n|---|---|---|---|")
    for lab, recal, ex in (("probabilité M0 non recalibrée, 164 ms", False, 164), ("probabilité recalibrée, 300 ms", True, 300), ("probabilité recalibrée, 500 ms", True, 500)):
        EXEC = ex; Cx = {s: preparer_cycle(s, recal) for s in S_}
        w(f"| {lab} | " + " | ".join(f"{sum(simuler(pol, Cx[s], e)[1] for s in S_):+.0f}" for pol in ("A", "H859 DPE", "H849")) + " |")
    EXEC = 164
    # H848
    w("\n## 4. H848 — Combinaison\n")
    ok = []
    if TE:
        for pol in POL:
            if pol in ("A", "G"): continue
            okk = True
            for nom in ("validation", "TEST inédit"):
                R, S2 = res[nom]; d = np.array([R[pol][s][1] - R["A"][s][1] for s in S2])
                if not ic_cy(d, 0.10 / 14)[0] > 0: okk = False
            if okk: ok.append(pol)
    w(("Composants validés (IC corrigé > 0 sur validation ET test) : " + ", ".join(ok) + ". Combinaison à pré-enregistrer séparément.") if ok
      else "Aucun composant ne bat A avec un IC corrigé > 0 sur la validation et le test : **combinaison non construite** (règle pré-enregistrée).")
    if journal:
        import csv, io
        p = os.path.join(ICI, "resultat_dpe_h841_journal.csv.gz")
        with gzip.open(p, "wt") as f:
            wr = csv.writer(f); wr.writerow(["debut_cycle", "t_ms", "politique", "action", "parts_up", "parts_down", "cash", "p_up"]); wr.writerows(journal)
        w(f"\nJournal d'inventaire (DPE, test inédit) : resultat_dpe_h841_journal.csv.gz, {len(journal)} lignes.\n")
    w("\n## Limites\n- Quelques heures de cycles : faible puissance. Exécution preneur uniquement (pas de maker).\n"
      "- La liquidité prise par nous est retirée 5 s ; au-delà, le carnet enregistré ne reflète pas notre propre impact.\n"
      "- Toutes les politiques utilisent la même probabilité ; si elle n'a pas d'avantage, aucune gestion ne peut en créer.\n")
    w(f"_Calcul : {time.time() - t_go:.0f} s._\n")
    open(SORTIE, "w").write("\n".join(o)); print("\n".join(o))


if __name__ == "__main__":
    main()
