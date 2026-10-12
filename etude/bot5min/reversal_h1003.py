"""BOT95 — ADAPTIVE REVERSAL & HEDGE ENGINE : H1003 à H1035 (cahier des charges de Pitch, 12.10.2026 17:45). PROTOCOLE PRÉ-ENREGISTRÉ (ce fichier
tel que committé le 12.10.2026, avant le calcul de la validation et du test). Hors ligne ; aucun ordre ; aucun bot actif, H816, H821, R4 ni fantôme
modifié ; aucun nouveau fantôme.

DONNÉES : cycles Dublin (carnet Polymarket Up complet toutes les 10 s + chaque changement à ±3 c, Down = miroir ; transactions), prix Binance spot
  et perp, Bybit, OKX, Coinbase, Chainlink, carnets Binance, flux agressifs, liquidations Bybit. Résultat officiel (bot95/reglements.json, sinon
  gagnant Dublin, sinon moyenne 60 s officielle). ETH / SOL, open interest et mark/index n'existent que depuis le 12.10 après-midi : exclus ici
  (H994–H1002 les traite) ; H1028 limité à Coinbase, OKX, Binance perp et Bybit.
DÉCOUPAGE (chronologique, figé) :
  développement = cycles avant le 12.10.2026 12:00 UTC (déjà explorés par les études précédentes) : apprentissage = 2/3 premiers, validation = 1/3 suivant ;
  TEST = cycles du 12.10 12:00 UTC au 13.10 00:00 UTC (jamais utilisés pour une politique de gestion de position) ;
  CONFIRMATION (option --confirmation, lancée plus tard) = cycles ≥ 13.10.2026 00:00 UTC, mêmes paramètres réappris sur le même apprentissage,
  aucun choix fait sur cette période (la période réservée ne sert à sélectionner aucune règle).
  Seuls paramètres appris (apprentissage seul) : les deux cerveaux, le seuil d'entrée e ∈ {0,05 ; 0,10 ; 0,15} (meilleur P&L de T0-50 $) et
  l'attribution politique ↔ régime de RS. Tout le reste est fixé ci-dessous.
CERVEAU A (trajectoire courte, H1004/H1009/H1019/H1026/H1027/H1028) : logistiques apprises sur l'apprentissage (un instant sur 3 s) ;
  familles : momentum (rendements 1/5/30/60 s normalisés, volatilité), flux agressifs Binance/Bybit 5/30 s, carnet Binance (OFI, profondeur, retraits,
  microprice, murs), inter-plateformes (base perp, avance OKX/Coinbase/perp sur 2 s), liquidations Bybit 10/60 s, écart Chainlink − Binance.
  Cibles : hausse à 1/3/5/10/15/30/60 s ; retournement à 30 s (mouvement futur opposé au mouvement des 30 s passées et ≥ la moitié de celui-ci) ;
  ampleur |Δ30 s| ≥ 5/10/20/40 $ (contre le modèle gaussien de volatilité seule). Ablation à 30 s : AUC sans chaque famille.
  Utilisé par les politiques : a30 = P(hausse BTC à 30 s) ; dirA(X) = a30 pour Up, 1 − a30 pour Down.
CERVEAU B (règlement, H1016) : logit p = a + b·logit(M0) + c·logit(milieu Polymarket Up), appris sur l'apprentissage (décisions toutes les 10 s) ;
  sans milieu : M0 recalibré. M0 = Chainlink, moyenne finale exacte, volatilité 300 s. Mesures : Brier et log loss contre le milieu du marché ;
  H1026 : apport de a30 au règlement (ΔBrier, IC par cycles).
REJEU (H1035) : décision chaque seconde de 10 à 290 s ; carnet observé à t ; exécution preneur à t + latence (164 ms ; sensibilité 200/250/500 ms)
  sur le carnet enregistré, limitée au prix observé (achat : vendeurs ≤ prix vu ; vente : acheteurs ≥ prix vu), quantités affichées seulement,
  fills partiels comptés, liquidité prise par nous indisponible 5 s. Frais preneur 0,07·p·(1−p) par part (sensibilité ×0,5 et ×1,5). Pas d'ordre
  maker (H804–H815 : tous négatifs). Paires Up + Down fusionnées (1 $ par paire). Capital net engagé ≤ 50 $. Une couverture n'existe qu'une fois
  exécutée. Après chaque transaction : profit si Up = cash + parts Up, profit si Down = cash + parts Down, plancher = min des deux (H1022).
LIMITE 5 CHF = 6,00 $ (1 CHF = 1,2001 $, OFX, 07.10.2026).
  Mode A (strict, T6 et T7s) : aucun achat ni aucune vente ne peut amener un des deux paiements sous −6,00 $ (vérifié au prix limite, donc
  garanti après exécution) ; la première entrée est donc plafonnée à 6 $. Mode B (dynamique, toutes les autres) : cible seulement, dépassements mesurés.
SIGNAL D'ENTRÉE COMMUN : première seconde (≥ 20 s restantes) où l'avantage net d'un côté X, p_X − vendeur − frais, atteint e.
POLITIQUES (H1034, mêmes cycles, mêmes données, mêmes hypothèses d'exécution) :
  T0-50  achat unique 50 $ puis règlement (référence « hold »).          T0-10  achat unique 10 $ puis règlement.
  T1     achats progressifs (H1003) : 10 $ au signal, + 10 $ dès que l'avantage ≥ e, au moins 10 s d'écart, 5 tranches au plus.
  T1v    tailles variables : idem, tranche = 10 $ × min(2 ; max(0,5 ; avantage / e)), jusqu'à 50 $.
  T2     renforts après confirmation (H1029) : T1 + cerveau A dans le sens de X ≥ 0,55 + p_X ≥ p_X de la tranche précédente + 0,02.
  T2p    renforts après amélioration du prix : 10 $ si vendeur X ≤ dernier vendeur payé − 2 c et avantage ≥ e (4 renforts au plus).
  T3     couverture après détérioration : T1 ; si p_X ≤ p_X d'entrée − 0,10 → plus de renfort ; une fois, achat de l'opposé pour 50 % des parts
         X non appariées si vendeur opposé + frais ≤ p_opposé + 0,02.
  T4     vente partielle puis inversion (H1006/H1030) : T1 ; si p_X ≤ p_X d'entrée − 0,10 ET cerveau A contre X ≥ 0,60 → une fois : vente de 50 % de X
         (si acheteur − frais ≥ p_X − 0,03), puis 10 $ de l'opposé si son avantage ≥ e / 2 ; plus de renfort de X.
  LAD    échelle de réaction (H1014) : T1 ; p_X ≤ entrée − 0,05 : plus de renfort ; − 0,10 : vente de 50 % des X non appariés (acheteur − frais ≥ p_X − 0,03) ;
         − 0,20 : achat de l'opposé pour les X restants non appariés (vendeur + frais ≤ p_opposé + 0,02) ; − 0,30 et cerveau A contre X ≥ 0,60 et
         avantage opposé ≥ e / 2 : 10 $ de l'opposé. Chaque étape une fois.
  T5     gestion simultanée Up/Down (H1007/H1023/H1015/H1021) : chaque seconde, une action au plus, par priorité : verrou de paire (coût moyen S +
         vendeur opposé + frais ≤ 0,99 → achat de l'opposé pour les S non appariés) ; vente de 10 $ de S si acheteur − frais − p_S ≥ 0,05 ; achat de
         10 $ du meilleur côté si avantage ≥ e (côté opposé à la position nette : avantage ≥ e + 0,03 ET ≥ 15 s depuis la dernière transaction
         de l'autre côté — hystérésis) ; sinon attendre.
  T6     T5 en mode A strict (H1033 B).
  T7     moteur adaptatif complet (H1035, mode B) : T5 + achats seulement si cerveau A dans le sens acheté ≥ 0,50 ; sortie d'une jambe non appariée si
         cerveau A contre elle ≥ 0,60 et acheteur − frais ≥ p − 0,02 ; protection (H1011/H1025) si plancher < −6 $ et p_S ≤ p_S d'entrée − 0,10 :
         le moins cher par part entre vendre S (p_S − acheteur net) et acheter l'opposé (vendeur + frais − p_opposé), s'il coûte ≤ 0,04 par part,
         pour la quantité qui ramène le plancher à −6 $. Priorité : protection > verrou > sortie > vente > achat.
  T7s    T7 en mode A strict.
  RS     changement de régime (H1017) : régime à la seconde du signal (choc de liquidations ≥ 50 000 $ Bybit sur 60 s ; sinon retournement probable :
         mouvement 10 s opposé au mouvement 60 s et ≥ 1 σ√10 ; sinon tendance : |mouvement 60 s| ≥ 2 σ√60 ; sinon range) ; pour chaque régime, la
         politique parmi T0-50, T1, T3, T5, T7 au meilleur P&L d'apprentissage.
SAUVETAGE H1036–H1040 (Pitch, 12.10 17:53) : entrée 10 $ au même signal ; « défavorable » = p_X ≤ p_X d'entrée − 0,15 (niveau fixé ici ;
  0,10 / 0,20 / 0,30 rapportés à titre descriptif pour R1 et R3). R0 conserver ; R1 vendre tout ; R2 couverture préventive (− 0,05 et cerveau A contre
  ≥ 0,60) ; R3 couverture complète ; R4 couverture tardive (p_X ≤ 0,25) ; R5 vente de 50 % puis couverture du reste ; R6 inversion complète (vente
  de tout + 10 $ de l'opposé) ; R7 adaptatif : probabilité de redevenir gagnante (H1039, logistique apprise sur les états détériorés de
  l'apprentissage — états des deux familles d'entrée — : cerveau B, milieu du marché, M0, cerveau A, temps restant, OFI, liquidations) ; vente si acheteur net > probabilité + 0,01,
  couverture si (1 − probabilité) − coût de l'opposé > 0,01, sinon conserver. Couverture = achat de l'opposé pour toutes les parts non appariées.
  H1038 à risque comparable : Rv (vente), Ra (achat de l'opposé), Rm (moitié-moitié), chacun pour ramener le pire résultat à −6 $.
  Mesures : test décisif (section 9, ramené à 100 positions défavorables), IC 90 % par cycles contre R0, IC corrigé (7 comparaisons).
SIMULATIONS PRIORITAIRES : A = T0-50, T0-10, T1, T1v, T2, T2p ; B = T1, T2 contre T4, LAD, T5, T7 ; C = T7s (strict) contre T7 (dynamique), 50 $ max.
MESURES (section 41) : P&L net, par cycle, par $ de capital maximal, cycles gagnants, perte max, fréquence des pertes > 6 $, drawdown, ES 5 %,
  capital max, achats, ventes, frais, coût d'écart, parts, P&L des transactions de couverture/protection/inversion, jackpots (cycles où T0-50 gagne
  avec un prix d'entrée ≤ 0,25) conservés, écart avec T0-50 (IC 90 % par cycles et IC corrigé de Bonferroni, 13 comparaisons).
  H1013 : P&L de chaque tranche de T1 (rang 1 à 5) jusqu'au règlement. H1020 : nombre de changements de camp
  par politique ; leur coût réel est inclus dans les frais et le coût d'écart de chaque politique. H1025 : coût par dollar de perte maximale évitée (contre T1).
  H1018 : scénarios défavorables (acheteurs disparus, couverture + 2 c, fills divisés par 2, latence 500 ms, vente de protection impossible).
CRITÈRE (section 43) : une politique est « intéressante » seulement si, sur le TEST, l'IC corrigé de l'écart avec T0-50 est > 0, la fréquence des
  pertes > 6 $ ne monte pas, ≥ 50 % du P&L des jackpots est conservé, l'écart reste > 0 à 500 ms et sans les 5 meilleurs cycles, et si la
  validation va dans le même sens. Sinon : simplifier ou abandonner. Une mise réduite ou un meilleur taux de victoire ne sont pas une preuve.
AMENDEMENT (12.10.2026, après le passage de contrôle sur apprentissage + validation, AVANT tout calcul du test ; commit séparé) :
  Le contrôle a montré que (1) le cerveau B appris est presque identique au milieu du marché (coefficient de M0 ≈ 0) et (2) les seuls « avantages »
  venaient de secondes où le carnet Polymarket n'avait qu'un côté : le repli « M0 recalibré seul » donnait alors 0,10–0,20 à des jetons vendus
  0,01 (billets de loterie : 20 cycles actifs sur 197 en apprentissage, dont un seul gain de +3 300 $). Corrections, sans aucun réglage de seuil :
  A1 — pas de probabilité ni de décision sans carnet à deux côtés (le repli M0 seul est supprimé).
  A2 — seconde famille d'entrée, indépendante du cerveau, pour étudier la GESTION de position sur un nombre suffisant de cycles : « favori » =
       première seconde entre 60 et 180 s écoulées où le côté favori (milieu ≥ 0,5) a un vendeur entre 0,60 et 0,85 ; même mise (50 $ pour T0-50,
       10 $ sinon). Les renforts, couvertures, ventes et sauvetages restent décidés par les règles ci-dessus. Les deux familles sont rapportées
       séparément, avec les mêmes corrections de tests multiples dans chaque famille. Le seuil e reste choisi sur T0-50 de la famille « avantage ».
Usage : python3 etude/bot5min/reversal_h1003.py dossier_cycles_dublin [--controle | --confirmation]
  --controle = apprentissage et validation seulement (vérification du code) ; --confirmation = cycles ≥ 13.10 00:00 UTC en guise de test."""
import os, sys, json, gzip, math, time, collections, csv
import numpy as np

ICI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, ICI)
import latence_h766 as LH, liquidite_h833 as L, dpe_h841 as DP, pression_h971 as PR
CONTROLE = "--controle" in sys.argv; CONFIRM = "--confirmation" in sys.argv
DEV_FIN = 1791806400; RESERVE = 1791849600
if CONFIRM: L.RESERVE = 10 ** 12
SORTIE = os.path.join(ICI, "resultat_reversal_h1003" + ("_controle" if CONTROLE else "_confirmation" if CONFIRM else "") + ".md")
LIM = 6.00; BUDGET = 50.0; TR_ = 10.0; LATS = (164, 200, 250, 500); RNG = np.random.default_rng(1003)
EXEC = 164; FEE_K = 1.0; STRESS = {}
fee = lambda p: FEE_K * 0.07 * p * (1 - p)
autre = lambda X: "Down" if X == "Up" else "Up"
POL = ["T0-50", "T0-10", "T1", "T1v", "T2", "T2p", "T3", "T4", "LAD", "T5", "T6", "T7", "T7s"]
STRICT = {"T6", "T7s"}; NCOMP = 13
RPOL = ["R0", "R1", "R2", "R3", "R4", "R5", "R6", "R7", "R1-10", "R1-20", "R1-30", "R3-10", "R3-20", "R3-30", "Rv", "Ra", "Rm"]; NCOMP_R = 7
REC_MODEL = None; ENTREE = "avantage"; FAMS = ("avantage", "favori")
vend, ach, meilleur = DP.vend, DP.ach, DP.meilleur


class Inv:
    def __init__(s):
        s.q = {"Up": 0.0, "Down": 0.0}; s.cout = {"Up": 0.0, "Down": 0.0}; s.cash = 0.0; s.maxcap = 0.0; s.na = s.nv = 0; s.frais = 0.0; s.ecart = 0.0
        s.qa = 0.0; s.paires = 0.0; s.lots = []; s.minfloor = 0.0; s.switch = []; s.defav = False; s.tres = None
    def cap(s): return max(-s.cash, 0.0)
    def libre(s): return BUDGET - s.cap()
    def moy(s, X): return s.cout[X] / s.q[X] if s.q[X] > 1e-9 else None
    def legs(s): return s.cash + s.q["Up"], s.cash + s.q["Down"]
    def floor(s): return min(s.legs())
    def net(s): return s.q["Up"] - s.q["Down"]
    def fusion(s):
        m = min(s.q["Up"], s.q["Down"])
        if m > 1e-9:
            for X in ("Up", "Down"): s.cout[X] *= (s.q[X] - m) / s.q[X]; s.q[X] -= m
            s.cash += m; s.paires += m


class Moteur:
    def __init__(s, E, strict): s.E = E; s.pris = []; s.strict = strict
    def dispo(s, t, X, side, px): return sum(q for (tt, XX, sd, p, q) in s.pris if XX == X and sd == side and p == px and t - tt < 5000)
    def acheter(s, inv, t, X, dollars, lim, mid, tag, journal=None):
        dollars = min(dollars, inv.libre())
        if s.strict: dollars = min(dollars, inv.cash + inv.q[autre(X)] + LIM - 1e-6)
        if dollars < 0.5 or lim is None: return 0.0
        hz = 20 if (STRESS.get("couv") and tag in ("couverture", "protection", "verrou", "inversion")) else 0
        q = c = 0.0
        for px, sz in vend(s.E[t + EXEC], X):
            if px > lim: break
            sz = sz * STRESS.get("fill", 1.0) - s.dispo(t, X, "a", px)
            if sz <= 1e-9: continue
            pe = min(px + hz, 999); pp = pe / 1000; u = pp + fee(pp); k = min(sz, (dollars - c) / u)
            if k <= 1e-9: break
            q += k; c += k * u; s.pris.append((t, X, "a", px, k)); inv.frais += k * fee(pp); inv.ecart += k * (pp - mid) if mid else 0
        if q > 0:
            inv.q[X] += q; inv.cout[X] += c; inv.cash -= c; inv.na += 1; inv.qa += q; inv.maxcap = max(inv.maxcap, inv.cap())
            inv.lots.append((tag, X, q, c)); inv.minfloor = min(inv.minfloor, inv.floor())
            if journal is not None: journal.append((t, "achat " + X, tag, round(q, 3), round(c, 3)) + tuple(round(v, 3) for v in inv.legs()))
        return q
    def vendre(s, inv, t, X, parts, lim, mid, tag, journal=None):
        parts = min(parts, inv.q[X])
        if parts <= 1e-9 or lim is None or STRESS.get("bids") or (STRESS.get("vprot") and tag in ("protection", "sortie")): return 0.0
        if s.strict:
            pn = lim / 1000 - fee(lim / 1000); legX = inv.cash + inv.q[X]
            if pn < 1: parts = min(parts, max(legX + LIM, 0) / (1 - pn))
            if parts <= 1e-9: return 0.0
        q = r = 0.0
        for px, sz in ach(s.E[t + EXEC], X):
            if px < lim: break
            sz = sz * STRESS.get("fill", 1.0) - s.dispo(t, X, "b", px)
            if sz <= 1e-9: continue
            pp = px / 1000; k = min(sz, parts - q)
            if k <= 1e-9: break
            q += k; r += k * (pp - fee(pp)); s.pris.append((t, X, "b", px, k)); inv.frais += k * fee(pp); inv.ecart += k * (mid - pp) if mid else 0
        if q > 0:
            m = inv.moy(X); inv.cout[X] -= q * m; inv.q[X] -= q; inv.cash += r; inv.nv += 1
            inv.lots.append((tag, X, -q, -r)); inv.minfloor = min(inv.minfloor, inv.floor())
            if journal is not None: journal.append((t, "vente " + X, tag, round(q, 3), round(r, 3)) + tuple(round(v, 3) for v in inv.legs()))
        return q


def simuler(pol, C, e, journal=None):
    st, E, PT, A30, y = C["st"], C["E"], C["p"], C["a30"], C["y"]
    strict = pol in STRICT; inv = Inv(); M = Moteur(E, strict); mem = {}; B = lambda X, d, Lo, tag: None
    J = journal
    for k, t in enumerate(C["T"]):
        Lo = E.get(t)
        if Lo is None or PT[k] is None: continue
        rest = 300 - (t // 1000 - st); pU = PT[k]; pX = {"Up": pU, "Down": 1 - pU}
        a30 = A30[k] if A30[k] is not None else 0.5; dirA = {"Up": a30, "Down": 1 - a30}
        ask = {X: meilleur(Lo, X, "a") for X in pX}; bid = {X: meilleur(Lo, X, "b") for X in pX}
        mid = {X: ((ask[X] + bid[X]) / 2000 if ask[X] and bid[X] else None) for X in pX}
        u = {X: (ask[X] / 1000 + fee(ask[X] / 1000)) if ask[X] else None for X in pX}
        bn_ = {X: (bid[X] / 1000 - fee(bid[X] / 1000)) if bid[X] else None for X in pX}
        edge = {X: (pX[X] - u[X]) if u[X] else -9 for X in pX}
        inv.fusion()
        buy = lambda X, d, tag: M.acheter(inv, t, X, d, ask[X], mid[X], tag, J)
        sell = lambda X, q, tag: M.vendre(inv, t, X, q, bid[X], mid[X], tag, J)
        X0 = mem.get("X")
        if X0 is None:
            if ENTREE == "favori":
                if not (120 <= rest <= 240) or mid["Up"] is None: continue
                Xb = "Up" if mid["Up"] >= 0.5 else "Down"
                if not (ask[Xb] and 600 <= ask[Xb] <= 850): continue
            else:
                if rest < 20: continue
                Xb = max(edge, key=edge.get)
                if edge[Xb] < e: continue
            X0 = Xb; mem.update(X=X0, p0=pX[X0], last=t, n=1, plast=pX[X0], alast=ask[X0], pent={X0: pX[X0]}, lastside={X0: t})
            buy(X0, BUDGET if pol == "T0-50" else TR_, "entrée"); mem["x"] = X0
            continue
        X = X0; Y = autre(X); unp = lambda S: max(inv.q[S] - inv.q[autre(S)], 0.0)
        if pol in ("T1", "T1v", "T2", "T3", "T4", "LAD"):
            det = pX[X] <= mem["p0"] - (0.05 if pol == "LAD" else 0.10)
            if pol in ("T3", "T4", "LAD") and det: mem["stop"] = 1
            ok = (not mem.get("stop")) and t - mem["last"] >= 10000 and edge[X] >= e and rest >= 20 and inv.libre() >= 1
            if pol in ("T1", "T2", "T3", "T4", "LAD") and mem["n"] >= 5: ok = False
            if pol == "T2" and not (dirA[X] >= 0.55 and pX[X] >= mem["plast"] + 0.02): ok = False
            if ok:
                d = TR_ * min(2.0, max(0.5, edge[X] / e)) if pol == "T1v" else TR_
                if buy(X, d, "renfort %d" % (mem["n"] + 1)) > 0: mem["last"] = t; mem["n"] += 1; mem["plast"] = pX[X]
            if pol == "T3" and det and not mem.get("h") and unp(X) > 1e-6 and u[Y] and u[Y] <= pX[Y] + 0.02:
                buy(Y, unp(X) * 0.5 * u[Y], "couverture"); mem["h"] = 1
            if pol == "T4" and not mem.get("h") and pX[X] <= mem["p0"] - 0.10 and dirA[Y] >= 0.60:
                mem["h"] = 1
                if bn_[X] is not None and bn_[X] >= pX[X] - 0.03: sell(X, inv.q[X] * 0.5, "protection")
                if edge[Y] >= e / 2: buy(Y, TR_, "inversion")
            if pol == "LAD":
                g = mem["p0"] - pX[X]
                if g >= 0.10 and not mem.get("s2"):
                    mem["s2"] = 1
                    if bn_[X] is not None and bn_[X] >= pX[X] - 0.03: sell(X, unp(X) * 0.5, "protection")
                if g >= 0.20 and not mem.get("s3"):
                    mem["s3"] = 1
                    if unp(X) > 1e-6 and u[Y] and u[Y] <= pX[Y] + 0.02: buy(Y, unp(X) * u[Y], "couverture")
                if g >= 0.30 and not mem.get("s4") and dirA[Y] >= 0.60 and edge[Y] >= e / 2:
                    mem["s4"] = 1; buy(Y, TR_, "inversion")
        elif pol == "T2p":
            if mem["n"] < 5 and ask[X] and mem["alast"] and ask[X] <= mem["alast"] - 20 and edge[X] >= e and rest >= 20:
                if buy(X, TR_, "renfort %d" % (mem["n"] + 1)) > 0: mem["n"] += 1; mem["alast"] = ask[X]
        elif pol in ("T5", "T6", "T7", "T7s"):
            adapt = pol in ("T7", "T7s"); fait = False
            if adapt and not fait:                                             # protection (mode B ; inoffensive en mode A)
                n_ = inv.net(); S = "Up" if n_ > 1e-6 else "Down" if n_ < -1e-6 else None
                if S and inv.floor() < -LIM and S in mem["pent"] and pX[S] <= mem["pent"][S] - 0.10:
                    T_ = autre(S); need = -LIM - inv.floor()
                    cs = (pX[S] - bn_[S]) if bn_[S] else 9; cb = (u[T_] - pX[T_]) if u[T_] else 9
                    if min(cs, cb) <= 0.04:
                        if cs <= cb: fait = sell(S, min(unp(S), need / max(bn_[S], 0.01)), "protection") > 0
                        else: fait = buy(T_, min(unp(S), need / max(1 - u[T_], 0.01)) * u[T_], "protection") > 0
            if not fait:                                                       # verrou de paire
                for S in (X, Y):
                    T_ = autre(S)
                    if unp(S) > 1e-6 and u[T_] and inv.moy(S) is not None and inv.moy(S) + u[T_] <= 0.99:
                        fait = buy(T_, unp(S) * u[T_], "verrou") > 0
                        if fait: break
            if adapt and not fait:                                             # sortie d'une jambe exposée
                for S in (X, Y):
                    if unp(S) > 1e-6 and dirA[autre(S)] >= 0.60 and bn_[S] is not None and bn_[S] >= pX[S] - 0.02:
                        fait = sell(S, min(unp(S), TR_ / max(bid[S] / 1000, 0.01)), "sortie") > 0
                        if fait: break
            if not fait:                                                       # vente au-dessus de la valeur
                for S in (X, Y):
                    if inv.q[S] > 1e-6 and bn_[S] is not None and bn_[S] - pX[S] >= 0.05:
                        fait = sell(S, min(inv.q[S], TR_ / max(bid[S] / 1000, 0.01)), "vente") > 0
                        if fait: break
            if not fait and rest >= 20 and inv.libre() >= 1:                    # achat (hystérésis)
                Sb = max(edge, key=edge.get); n_ = inv.net(); oppose = (n_ > 1e-6 and Sb == "Down") or (n_ < -1e-6 and Sb == "Up")
                seuil = e + (0.03 if oppose else 0)
                okb = edge[Sb] >= seuil and (not oppose or t - mem["lastside"].get(autre(Sb), 0) >= 15000)
                if adapt and dirA[Sb] < 0.50: okb = False
                if okb and buy(Sb, TR_, "achat " + ("inverse" if oppose else "même sens")) > 0:
                    mem["lastside"][Sb] = t; mem["pent"].setdefault(Sb, pX[Sb])
                    if oppose: inv.switch.append((t, Sb))
        elif pol.startswith("R"):                                                 # H1036–H1040 : sauvetage de la première position
            g = mem["p0"] - pX[X]
            if g >= 0.15: inv.defav = True
            base, lvl = (pol.split("-")[0], int(pol.split("-")[1]) / 100) if "-" in pol and pol.split("-")[1].isdigit() else (pol, 0.15)
            if not mem.get("fait") and inv.q[X] > 1e-6:
                ex = 0.0; need = -LIM - (inv.cash + inv.q[Y])
                if base == "R1" and g >= lvl: ex = sell(X, inv.q[X], "protection")
                elif base == "R2" and g >= 0.05 and dirA[Y] >= 0.60 and u[Y]: ex = buy(Y, unp(X) * u[Y], "couverture")
                elif base == "R3" and g >= lvl and u[Y]: ex = buy(Y, unp(X) * u[Y], "couverture")
                elif base == "R4" and pX[X] <= 0.25 and u[Y]: ex = buy(Y, unp(X) * u[Y], "couverture")
                elif base == "R5" and g >= lvl:
                    ex = sell(X, inv.q[X] * 0.5, "protection")
                    if u[Y]: ex += buy(Y, unp(X) * u[Y], "couverture")
                elif base == "R6" and g >= lvl:
                    ex = sell(X, inv.q[X], "protection")
                    if edge[Y] > -9: ex += buy(Y, TR_, "inversion")
                elif base == "R7" and g >= lvl and REC_MODEL is not None:
                    pr = REC_MODEL(C, k, X)
                    vs = (bn_[X] - pr) if bn_[X] is not None else -9; vh = ((1 - pr) - u[Y]) if u[Y] else -9
                    if max(vs, vh) > 0.01:
                        ex = sell(X, inv.q[X], "protection") if vs >= vh else buy(Y, unp(X) * u[Y], "couverture")
                elif base in ("Rv", "Ra", "Rm") and g >= 0.15 and need > 1e-6:            # H1038 : même cible de risque (pire ≥ −6 $)
                    if base == "Rv" and bn_[X]: ex = sell(X, need / bn_[X], "protection")
                    elif base == "Ra" and u[Y] and u[Y] < 1: ex = buy(Y, need / (1 - u[Y]) * u[Y], "couverture")
                    elif base == "Rm" and bn_[X] and u[Y] and u[Y] < 1:
                        ex = sell(X, 0.5 * need / bn_[X], "protection"); need2 = -LIM - (inv.cash + inv.q[Y])
                        if need2 > 1e-6: ex += buy(Y, need2 / (1 - u[Y]) * u[Y], "couverture")
                if ex > 0: mem["fait"] = 1; inv.tres = t
    inv.fusion()
    pnl = inv.cash + inv.q["Up"] * y + inv.q["Down"] * (1 - y)
    return inv, pnl


def resume(inv, pnl, y, C):
    yX = lambda X: y if X == "Up" else 1 - y
    hed = collections.defaultdict(float); tr = []
    for tag, X, q, c in inv.lots:
        v = q * yX(X) - c
        if tag in ("couverture", "protection", "inversion", "verrou", "sortie"): hed[tag] += v
        if tag == "entrée" or tag.startswith("renfort"): tr.append((1 if tag == "entrée" else int(tag.split()[1]), v, c))
    return dict(pnl=pnl, maxcap=inv.maxcap, na=inv.na, nv=inv.nv, frais=inv.frais, ecart=inv.ecart, qa=inv.qa, hed=dict(hed), tr=tr,
                minfloor=inv.minfloor, nsw=len(inv.switch), actif=inv.na > 0, defav=inv.defav, res=inv.tres is not None, fl=inv.floor())


# ------------------------------------------------------------------------------------------------ statistiques
def ic_cy(d, alpha=0.10, B=4000):
    d = np.asarray(d, float)
    if len(d) < 3: return (float("nan"), float("nan"))
    idx = RNG.integers(0, len(d), (B, len(d))); m = d[idx].sum(1)
    return float(np.percentile(m, 100 * alpha / 2)), float(np.percentile(m, 100 * (1 - alpha / 2)))


def mesures(Rp, sts):
    v = np.array([Rp[s]["pnl"] for s in sts]); cap = np.array([Rp[s]["maxcap"] for s in sts]); act = np.array([Rp[s]["actif"] for s in sts])
    cum = np.cumsum(v); dd = float(np.max(np.maximum.accumulate(np.concatenate([[0], cum]))[1:] - cum)) if len(v) else 0
    k5 = max(1, int(math.ceil(0.05 * len(v)))); vs = np.sort(v)
    return dict(tot=v.sum(), n=int(act.sum()), moy=v[act].mean() if act.any() else 0, parcap=v.sum() / max(cap.sum(), 1e-9), gagn=int((v > 0).sum()),
                pire=v.min() if len(v) else 0, p6=int((v < -LIM).sum()), dd=dd, es=vs[:k5].mean() if len(v) else 0, capmax=cap.max() if len(v) else 0,
                na=sum(Rp[s]["na"] for s in sts), nv=sum(Rp[s]["nv"] for s in sts), frais=sum(Rp[s]["frais"] for s in sts),
                ecart=sum(Rp[s]["ecart"] for s in sts), qa=sum(Rp[s]["qa"] for s in sts), sans5=vs[:-5].sum() if len(v) > 5 else float("nan"),
                hed=sum(sum(Rp[s]["hed"].values()) for s in sts), minf=np.mean([Rp[s]["minfloor"] for s in sts]))


def regime(G, P, LQ60, i):
    if not (0 < i < G["n"]) or not np.isfinite(G["bn"][i]) or not np.isfinite(G["bn"][i - 60]): return "inconnu"
    s = P["sd1"][i] if np.isfinite(P["sd1"][i]) and P["sd1"][i] > 0 else 1.0; bn = G["bn"]
    m60 = bn[i] - bn[i - 60]; m10 = bn[i] - bn[i - 10]
    if LQ60[i] >= 50000: return "choc de liquidations"
    if m10 * m60 < 0 and abs(m10) >= s * math.sqrt(10): return "retournement probable"
    if abs(m60) >= 2 * s * math.sqrt(60): return "tendance"
    return "range"


def signal(C, e):
    for k, t in enumerate(C["T"]):
        Lo = C["E"].get(t); pU = C["p"][k]
        if Lo is None or pU is None or 300 - (t // 1000 - C["st"]) < 20: continue
        ed = []
        for X, pX in (("Up", pU), ("Down", 1 - pU)):
            a = meilleur(Lo, X, "a")
            if a: ed.append((pX - a / 1000 - 0.07 * (a / 1000) * (1 - a / 1000), X, a))
        if ed and max(ed)[0] >= e: return k, max(ed)[1], (pU if max(ed)[1] == "Up" else 1 - pU), max(ed)[2] / 1000
    return None


def signal_fav(C):
    for k, t in enumerate(C["T"]):
        Lo = C["E"].get(t); rest = 300 - (t // 1000 - C["st"])
        if Lo is None or C["p"][k] is None or not (120 <= rest <= 240): continue
        a, b = meilleur(Lo, "Up", "a"), meilleur(Lo, "Up", "b")
        if not (a and b): continue
        X = "Up" if (a + b) / 2000 >= 0.5 else "Down"; aX = meilleur(Lo, X, "a")
        if aX and 600 <= aX <= 850: return k, X, (C["p"][k] if X == "Up" else 1 - C["p"][k]), aX / 1000
    return None


def rec_x(C, k, X):
    pU = C["p"][k]; s_ = 1 if X == "Up" else -1
    if pU is None: return None
    pX = pU if X == "Up" else 1 - pU; md = C["mid"][k]; mX = (md if X == "Up" else 1 - md) if md else pX
    m0 = C["m0"][k]; m0X = (m0 if X == "Up" else 1 - m0) if m0 is not None else pX; a = C["a30"][k] if C["a30"][k] is not None else 0.5
    rest = (300 - (C["T"][k] // 1000 - C["st"])) / 300; c = lambda p: L.lg(min(max(p, 0.005), 0.995))
    return [c(pX), c(mX), c(m0X), (a - 0.5) * s_, rest, c(pX) * rest, (C["ofi"][k] or 0) * s_, (C["liq"][k] or 0) * s_ / 1e5]


def main():
    global EXEC, FEE_K, STRESS, REC_MODEL, ENTREE
    t_go = time.time(); o = []; w = o.append
    G, cyc = L.grille(sys.argv[1]); P = L.preparer(G); L.P_sd1 = P["sd1"]; Y = L.resultats_officiels(cyc); V = PR.grandeurs(G, P)
    n = G["n"]; t0 = G["t0"]; bn = G["bn"]; sd1 = P["sd1"]
    cycles = sorted(s for s in cyc if s in Y)
    dev = [s for s in cycles if s < DEV_FIN]; ntr = len(dev) * 2 // 3; TR, VA = dev[:ntr], dev[ntr:]
    TE = [] if CONTROLE else ([s for s in cycles if s >= RESERVE] if CONFIRM else [s for s in cycles if DEV_FIN <= s < RESERVE])
    nomT = "CONFIRMATION (≥ 13.10)" if CONFIRM else "TEST"
    w(f"# Bot95 — Adaptive Reversal & Hedge Engine H1003–H1035 ({'CONTRÔLE : apprentissage et validation' if CONTROLE else nomT})\n")
    w(f"Généré le {time.strftime('%d.%m.%Y %H:%M', time.gmtime())} UTC. Cycles avec résultat officiel : apprentissage {len(TR)}, validation {len(VA)}, "
      f"{nomT.lower()} {len(TE)}. Capital ≤ 50 $, limite 5 CHF = {LIM:.2f} $. Exécution preneur sur le carnet enregistré. Aucun ordre ; aucun fantôme modifié.\n")
    # liquidations Bybit (flux fx)
    LQ = np.zeros(n); LQs = np.zeros(n)
    for st, c in cyc.items():
        try: R = json.load(gzip.open(c["f"]))
        except Exception: continue
        for r in R.get("fx", []):
            x = r[1].get("liq_bybit")
            if not x: continue
            i = int(math.ceil(r[0] / 1000)) - t0
            if 0 <= i < n: LQ[i] += x[0] + x[1]; LQs[i] += x[0] - x[1]
    cs = lambda x: np.concatenate([[0], np.cumsum(x)]); CL, CLs = cs(LQ), cs(LQs)
    win = lambda C, i, k: C[i + 1] - C[max(i + 1 - k, 0)]
    LQ60 = np.array([win(CL, i, 60) for i in range(n)])
    # ------------------------------------------------ cerveau A
    def familles(i):
        s = sd1[i] if np.isfinite(sd1[i]) and sd1[i] > 0 else 1.0
        Bf, Cf, Df = L.feats(G, P, i)
        mom = [(bn[i] - bn[i - 1]) / s, (bn[i] - bn[i - 5]) / (s * 2.24), (bn[i] - bn[i - 30]) / (s * 5.48), (bn[i] - bn[i - 60]) / (s * 7.75), s]
        return dict(mom=mom, flux=Bf[:4], carnet=Cf, inter=Df, liq=[win(CLs, i, 10) / 1e5, win(CLs, i, 60) / 1e5, LQ60[i] / 1e5],
                    cl=[(G["cl"][i] - bn[i]) / s if np.isfinite(G["cl"][i]) else 0.0])
    FAM = ("mom", "flux", "carnet", "inter", "liq", "cl")
    part = {}
    for s_ in TR: part[s_] = "apprentissage"
    for s_ in VA: part[s_] = "validation"
    for s_ in TE: part[s_] = nomT
    I = [i for st in TR + VA + TE for i in range(st - t0 + 10, st - t0 + 291, 3) if 620 <= i < n - 61 and G["ok"][i] and np.isfinite(bn[i]) and np.isfinite(bn[i + 60]) and np.isfinite(sd1[i])]
    I = np.array(I); gI = np.array([(t0 + i) - (t0 + i) % 300 for i in I]); pI = np.array([part[g] for g in gI]); trm = pI == "apprentissage"
    FX = {f: np.nan_to_num(np.array([familles(i)[f] for i in I], float)) for f in FAM}
    XF = lambda fs: np.column_stack([FX[f] for f in fs])
    def fit(X, y):
        mu, sd = X[trm].mean(0), X[trm].std(0) + 1e-9; b = L.ajuster((X[trm] - mu) / sd, y[trm], 2.0); return lambda Z: L.predire(b, (Z - mu) / sd)
    PARTS_ = [p for p in ("validation", nomT) if (pI == p).any()]
    def auc_ic(pr, y, m, base=None):
        g = gI[m]; U = np.unique(g); D = []
        for _ in range(300):
            mm = np.isin(g, RNG.choice(U, len(U)))
            if 0 < y[m][mm].sum() < mm.sum(): D.append(L.auc(pr[m][mm], y[m][mm]) - (L.auc(base[m][mm], y[m][mm]) if base is not None else 0))
        return (np.percentile(D, 5), np.percentile(D, 95)) if D else (np.nan, np.nan)
    w("## 1. Cerveau A — trajectoire courte du BTC (H1004, H1009, H1019, H1026–H1028)\n")
    w("| Cible | Échantillon | Taux de base | AUC momentum seul | AUC toutes familles | Gain d'AUC (IC 90 %) |\n|---|---|---|---|---|---|")
    full = XF(FAM); mom = XF(("mom",)); a30fun = None
    for h in (1, 3, 5, 10, 15, 30, 60):
        y = (bn[I + h] > bn[I]).astype(float); fF = fit(full, y); fM = fit(mom, y); pF, pM = fF(full), fM(mom)
        if h == 30: a30fun = fF; y30 = y; p30F = pF
        for pt in PARTS_:
            m = pI == pt; c = auc_ic(pF, y, m, pM)
            w(f"| hausse à {h} s | {pt} | {100 * y[m].mean():.1f} % | {L.auc(pM[m], y[m]):.3f} | {L.auc(pF[m], y[m]):.3f} | {L.auc(pF[m], y[m]) - L.auc(pM[m], y[m]):+.3f} [{c[0]:+.3f} ; {c[1]:+.3f}] |")
    m30 = bn[I] - bn[I - 30]; f30 = bn[I + 30] - bn[I]
    yr = ((m30 * f30 < 0) & (np.abs(f30) >= 0.5 * np.abs(m30))).astype(float); fR = fit(full, yr); fRm = fit(mom, yr); pR, pRm = fR(full), fRm(mom)
    for pt in PARTS_:
        m = pI == pt; c = auc_ic(pR, yr, m, pRm)
        w(f"| retournement à 30 s | {pt} | {100 * yr[m].mean():.1f} % | {L.auc(pRm[m], yr[m]):.3f} | {L.auc(pR[m], yr[m]):.3f} | {L.auc(pR[m], yr[m]) - L.auc(pRm[m], yr[m]):+.3f} [{c[0]:+.3f} ; {c[1]:+.3f}] |")
    w("\n**Ablation (hausse à 30 s) : perte d'AUC quand on retire une famille** (positif = la famille apporte)\n")
    w("| Famille retirée | " + " | ".join(PARTS_) + " |\n|---|" + "---|" * len(PARTS_))
    for f in FAM:
        Xs = XF([g for g in FAM if g != f]); pS = fit(Xs, y30)(Xs)
        cells = []
        for pt in PARTS_:
            m = pI == pt; c = auc_ic(p30F, y30, m, pS); cells.append(f"{L.auc(p30F[m], y30[m]) - L.auc(pS[m], y30[m]):+.4f} [{c[0]:+.4f} ; {c[1]:+.4f}]")
        w(f"| {f} | " + " | ".join(cells) + " |")
    w("\n**Ampleur du mouvement à 30 s (H1009)** — Brier : modèle gaussien (volatilité seule) contre logistique toutes familles\n")
    w("| Seuil | Échantillon | Fréquence | Brier gaussien | Brier modèle | Différence (IC 90 %) |\n|---|---|---|---|---|---|")
    from math import erf
    for k in (5, 10, 20, 40):
        ys = (np.abs(f30) >= k).astype(float); fS = fit(full, ys); pS = fS(full)
        pg = np.array([1 - erf(k / (max(sd1[i], 1e-6) * math.sqrt(30) * math.sqrt(2))) for i in I])
        for pt in PARTS_:
            m = pI == pt; d = L.brier(pS[m], ys[m]) - L.brier(pg[m], ys[m]); c = L.ic_g(gI[m], d)
            w(f"| ≥ {k} $ | {pt} | {100 * ys[m].mean():.1f} % | {L.brier(pg[m], ys[m]).mean():.4f} | {L.brier(pS[m], ys[m]).mean():.4f} | {d.mean():+.4f} [{c[0]:+.4f} ; {c[1]:+.4f}] |")
    # a30 à chaque seconde des cycles
    def a30_at(i):
        if not (620 <= i < n) or not np.isfinite(bn[i]) or not np.isfinite(sd1[i]): return None
        return float(a30fun(np.nan_to_num(np.array([sum((familles(i)[f] for f in FAM), [])], float)))[0])
    # ------------------------------------------------ cerveau B
    def tstates(st, T):
        try: return {k: DP.compact(v) for k, v in LH.Cycle(cyc[st]["f"]).etats(T).items()}
        except Exception: return {}
    def midU(Lo):
        a, b = meilleur(Lo, "Up", "a"), meilleur(Lo, "Up", "b")
        return (a + b) / 2000 if a and b and 0 < (a + b) / 2000 < 1 else None
    Xb, Xm, yb, gb = [], [], [], []
    for st in TR:
        T = [st * 1000 + s * 1000 for s in range(10, 291, 10)]; E = tstates(st, T)
        for t in T:
            m = L.m0(G, cyc, st, 300 - (t // 1000 - st))
            if not m: continue
            mu = midU(E.get(t)); Xm.append([L.lg(m[0])]); yb.append(Y[st])
            Xb.append([L.lg(m[0]), L.lg(min(max(mu, 0.005), 0.995))] if mu else None)
    yb = np.array(yb); okb = np.array([x is not None for x in Xb])
    bM = L.ajuster(np.array(Xm), yb, 0.1); bB = L.ajuster(np.array([x for x in Xb if x is not None]), yb[okb], 0.1)
    w(f"\n## 2. Cerveau B — probabilité de règlement (H1016)\n\nlogit p = {bB[0]:+.3f} + {bB[1]:.3f} × logit(M0) + {bB[2]:.3f} × logit(milieu Polymarket) "
      f"(sans milieu : {bM[0]:+.3f} + {bM[1]:.3f} × logit(M0)) ; {int(okb.sum())} décisions d'apprentissage.\n")
    def pB(st, t, Lo):
        m = L.m0(G, cyc, st, 300 - (t // 1000 - st))
        if not m: return None, None, None
        mu = midU(Lo)
        if mu: return float(L.predire(bB, np.array([[L.lg(m[0]), L.lg(min(max(mu, 0.005), 0.995))]]))[0]), m, mu
        return None, m, None                                                   # amendement A1 : pas de carnet à deux côtés → pas de décision
    # ------------------------------------------------ rejeu : préparation d'un cycle
    def preparer_cycle(st):
        T = [st * 1000 + s * 1000 for s in range(10, 291)]
        E = tstates(st, T + [t + l for t in T for l in LATS]); p, a30, m0r, mids = [], [], [], []
        for t in T:
            pp, m, mu = pB(st, t, E.get(t)); p.append(pp); m0r.append(m[0] if m else None); mids.append(mu)
            a30.append(a30_at(st + (t // 1000 - st) - t0))
        ii = [t // 1000 - t0 for t in T]
        ofi = [float(V["ofi5"][i]) if 0 <= i < n and np.isfinite(V["ofi5"][i]) else 0.0 for i in ii]; lq = [float(win(CLs, i, 60)) if 0 <= i < n else 0.0 for i in ii]
        return dict(st=st, E=E, T=T, p=p, a30=a30, m0=m0r, mid=mids, y=Y[st], ofi=ofi, liq=lq)
    # ------------------------------------------------ simulations
    RECD = []; CAL = collections.defaultdict(list)
    RESF = {f_: collections.defaultdict(dict) for f_ in FAMS}; REGF = {f_: {} for f_ in FAMS}; ENTF = {f_: {} for f_ in FAMS}; JF = {f_: [] for f_ in FAMS}; SWF = {f_: [] for f_ in FAMS}
    variantes = [("164", 164, 1.0, {})] + [(f"{l}", l, 1.0, {}) for l in LATS[1:]] + [("frais×0,5", 164, 0.5, {}), ("frais×1,5", 164, 1.5, {})]
    STR = [("acheteurs disparus", {"bids": 1}), ("couverture + 2 c", {"couv": 1}), ("fills ÷ 2", {"fill": 0.5}), ("vente de protection impossible", {"vprot": 1})]
    POLS_STR = ["T0-50", "T1", "T3", "T4", "LAD", "T5", "T7", "T7s"]
    e_choisi = None
    for st in TR + VA + TE:
        C = preparer_cycle(st); pt = part[st]
        # calibration (toutes les 10 s)
        for k in range(0, len(C["T"]), 10):
            if C["p"][k] is not None and C["mid"][k] is not None and C["m0"][k] is not None:
                CAL[pt].append((st, C["p"][k], C["mid"][k], C["m0"][k], C["a30"][k], C["y"]))
        for fam in FAMS:
            ENTREE = fam; RES_ = RESF[fam]; REG_ = REGF[fam]; ENT_ = ENTF[fam]; JOUR_ = JF[fam]; SW_ = SWF[fam]
            if pt == "apprentissage":
                vus = set()
                for e in (0.05, 0.10, 0.15):
                    for pol in POL + RPOL:
                        EXEC, FEE_K, STRESS = 164, 1.0, {}
                        inv, pnl = simuler(pol, C, e); RES_[("app", e, pol)][st] = resume(inv, pnl, C["y"], C)
                    sg = signal(C, e) if ENTREE == "avantage" else (signal_fav(C) if e == 0.10 else None)
                    if sg:
                        k0, X, p0, _a = sg; dans = False
                        for k in range(k0 + 1, len(C["T"])):
                            if C["p"][k] is None: continue
                            pX = C["p"][k] if X == "Up" else 1 - C["p"][k]
                            if pX <= p0 - 0.15: dans = True
                            if dans and (k - k0) % 5 == 0 and 300 - (C["T"][k] // 1000 - st) >= 10 and (k, X) not in vus:
                                vus.add((k, X)); RECD.append((st, rec_x(C, k, X), C["y"] if X == "Up" else 1 - C["y"]))
            else:
                if e_choisi is None:
                    sc = {e: sum(RESF["avantage"][("app", e, "T0-50")][s]["pnl"] for s in TR) for e in (0.05, 0.10, 0.15)}; e_choisi = max(sc, key=sc.get); SC_E = sc
                    Xr = np.array([r[1] for r in RECD], float); yr_ = np.array([r[2] for r in RECD], float); mu_r, sd_r = Xr.mean(0), Xr.std(0) + 1e-9
                    bR = L.ajuster((Xr - mu_r) / sd_r, yr_, 2.0) if len(RECD) >= 30 else None
                    if bR is not None: REC_MODEL = lambda C_, k_, X_: float(L.predire(bR, (np.array([rec_x(C_, k_, X_)]) - mu_r) / sd_r)[0])
                e = e_choisi
                for nom, lat, fk, _ in variantes:
                    if nom != "164" and pt == "validation" and nom not in ("500",): continue
                    EXEC, FEE_K, STRESS = lat, fk, {}
                    for pol in POL + RPOL:
                        jj = [] if (nom == "164" and pol == "T7" and pt == nomT) else None
                        inv, pnl = simuler(pol, C, e, jj); RES_[(pt, nom, pol)][st] = resume(inv, pnl, C["y"], C)
                        if jj: JOUR_ += [(st,) + r for r in jj]
                        if nom == "164" and inv.switch:
                            for (ts, Sb) in inv.switch: SW_.append((pt, pol, st, ts, Sb))
                if pt == nomT:
                    for snom, sdict in STR:
                        EXEC, FEE_K, STRESS = 164, 1.0, sdict
                        for pol in POLS_STR:
                            inv, pnl = simuler(pol, C, e); RES_[(pt, snom, pol)][st] = resume(inv, pnl, C["y"], C)
                    EXEC, FEE_K, STRESS = 164, 1.0, {}
                # coût de changement de camp au moment de chaque inversion (H1020), sur le carnet observé
            # régime au signal commun (même e pour T0-50)
            ee = e_choisi if e_choisi is not None else 0.10
            for k, t in enumerate(C["T"]):
                Lo = C["E"].get(t); pU = C["p"][k]
                if Lo is None or pU is None or 300 - (t // 1000 - st) < 20: continue
                ed = []
                for X, pX in (("Up", pU), ("Down", 1 - pU)):
                    a = meilleur(Lo, X, "a")
                    if a: ed.append((pX - a / 1000 - 0.07 * (a / 1000) * (1 - a / 1000), X, a))
                if ENTREE == "favori":
                    if not (120 <= 300 - (t // 1000 - st) <= 240): continue
                    a_u, b_u = meilleur(Lo, "Up", "a"), meilleur(Lo, "Up", "b")
                    if not (a_u and b_u): continue
                    Xf = "Up" if (a_u + b_u) / 2000 >= 0.5 else "Down"; af = meilleur(Lo, Xf, "a")
                    if af and 600 <= af <= 850:
                        REG_[st] = regime(G, P, LQ60, t // 1000 - t0); ENT_[st] = (Xf, af / 1000, t); break
                    continue
                if ed and max(ed)[0] >= ee:
                    REG_[st] = regime(G, P, LQ60, t // 1000 - t0); ENT_[st] = (max(ed)[1], max(ed)[2] / 1000, t); break
            if st not in REG_: REG_[st] = "aucun signal"
        C = None
    if e_choisi is None and TR:
        sc = {e: sum(RESF["avantage"][("app", e, "T0-50")][s]["pnl"] for s in TR) for e in (0.05, 0.10, 0.15)}; e_choisi = max(sc, key=sc.get); SC_E = sc
    e = e_choisi
    ENTREE = "avantage"

    def rapport(fam, RES, REG, ENT, JOURNAL, SW):
      e = e_choisi
      w(f"\n# FAMILLE D'ENTRÉE : {'avantage du cerveau B ≥ e' if fam == 'avantage' else 'favori du marché (vendeur 0,60–0,85, 60 à 180 s écoulées)'}\n")
      # RS : attribution sur l'apprentissage (au e choisi)
      CANDS = ["T0-50", "T1", "T3", "T5", "T7"]; ATT = {}
      for rg in set(REG[s] for s in TR):
          S_ = [s for s in TR if REG[s] == rg]; ATT[rg] = max(CANDS, key=lambda p_: sum(RES[("app", e, p_)][s]["pnl"] for s in S_))
      for key in list(RES.keys()):
          pass
      def rs_res(src):
          out = {}
          for s in src[next(iter(src))].keys() if src else []:
              pol = ATT.get(REG.get(s), "T0-50"); out[s] = src[pol][s]
          return out
      if fam == FAMS[0]: w(f"\n**Calibration de règlement (H1016, décisions toutes les 10 s)** — Brier et log loss ; écart = cerveau B − milieu du marché\n")
      w("| Échantillon | Décisions | Brier marché | Brier M0 brut | Brier cerveau B | Cerveau B − marché (IC 90 %) | LL marché | LL cerveau B | Ajout de a30 (H1026) : ΔBrier (IC 90 %) |\n|---|---|---|---|---|---|---|---|---|")
      ca = CAL["apprentissage"]
      if ca:
          Xa = np.array([[L.lg(r[1]), (r[4] if r[4] is not None else 0.5) - 0.5] for r in ca]); ya = np.array([r[5] for r in ca]); b26 = L.ajuster(Xa, ya, 0.1)
      for pt in ["apprentissage", "validation", nomT]:
          cc = CAL.get(pt)
          if not cc: continue
          g = np.array([r[0] for r in cc]); pb = np.array([r[1] for r in cc]); pm = np.array([r[2] for r in cc]); p0 = np.array([r[3] for r in cc]); yy = np.array([r[5] for r in cc])
          d = L.brier(pb, yy) - L.brier(pm, yy); c = L.ic_g(g, d)
          p26 = L.predire(b26, np.array([[L.lg(r[1]), (r[4] if r[4] is not None else 0.5) - 0.5] for r in cc])); d2 = L.brier(p26, yy) - L.brier(pb, yy); c2 = L.ic_g(g, d2)
          w(f"| {pt} | {len(cc)} | {L.brier(pm, yy).mean():.4f} | {L.brier(p0, yy).mean():.4f} | {L.brier(pb, yy).mean():.4f} | {d.mean():+.4f} [{c[0]:+.4f} ; {c[1]:+.4f}] | "
            f"{L.ll(pm, yy).mean():.4f} | {L.ll(pb, yy).mean():.4f} | {d2.mean():+.5f} [{c2[0]:+.5f} ; {c2[1]:+.5f}] |")
      w(f"\nSeuil d'entrée e choisi sur l'apprentissage (T0-50) : **{e:.2f}** (" + ", ".join(f"e={k:.2f} → {v:+.0f} $" for k, v in SC_E.items()) + ").\n")
      w("Attribution RS (apprentissage) : " + ", ".join(f"{k} → {v}" for k, v in sorted(ATT.items())) + ".\n")
      # ------------------------------------------------ tableaux
      def tableau(titre, Rd, sts, ref="T0-50", pols=None, ncomp=NCOMP):
          pols = pols or list(Rd.keys())
          w(f"### {titre} ({len(sts)} cycles)\n")
          w(f"| Politique | Cycles actifs | P&L net ($) | Par cycle actif | Par $ de capital max | Cycles gagnants | Perte max | Pertes > 6 $ | Drawdown | ES 5 % | Capital max | Achats / ventes | Frais ($) | Coût d'écart ($) | Parts achetées | P&L couvertures ($) | Plancher le plus bas (moy.) | Jackpots conservés | Sans les 5 meilleurs | Écart avec {ref} ($) | IC 90 % | IC corrigé ({ncomp}) |\n"
            "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
          a = np.array([Rd[ref][s]["pnl"] for s in sts])
          jk = [s for s in sts if s in ENT and ENT[s][1] <= 0.25 and Rd[ref][s]["pnl"] > 0]; jref = sum(Rd[ref][s]["pnl"] for s in jk)
          for pol in pols:
              if pol == "R7" and Rd is Rapp: continue
              if pol not in Rd: continue
              m = mesures(Rd[pol], sts); d = np.array([Rd[pol][s]["pnl"] for s in sts]) - a; c1 = ic_cy(d); c2 = ic_cy(d, 0.10 / ncomp)
              jc = (100 * sum(Rd[pol][s]["pnl"] for s in jk) / jref) if jref > 0 else float("nan")
              w(f"| {pol} | {m['n']} | {m['tot']:+.0f} | {m['moy']:+.2f} | {100 * m['parcap']:+.1f} % | {m['gagn']} | {m['pire']:+.0f} | {m['p6']} | {m['dd']:.0f} | {m['es']:+.1f} | "
                f"{m['capmax']:.0f} | {m['na']} / {m['nv']} | {m['frais']:.0f} | {m['ecart']:.0f} | {m['qa']:.0f} | {m['hed']:+.0f} | {m['minf']:+.1f} | {jc:.0f} % ({len(jk)}) | {m['sans5']:+.0f} | "
                f"{d.sum():+.0f} | " + ("—" if pol == ref else f"[{c1[0]:+.0f} ; {c1[1]:+.0f}]") + " | " + ("—" if pol == ref else f"[{c2[0]:+.0f} ; {c2[1]:+.0f}]") + " |")
          w("")
      w("\n## 3. Tournoi T0–T7 (H1034), latence 164 ms\n")
      Rapp = {pol: RES[("app", e, pol)] for pol in POL}; Rapp["RS"] = rs_res(Rapp)
      tableau("apprentissage (sert au choix de e et de RS)", Rapp, TR)
      SPL = [(pt, [s for s in (VA if pt == "validation" else TE)]) for pt in ("validation", nomT) if (VA if pt == "validation" else TE)]
      RV = {}
      for pt, sts in SPL:
          Rv = {pol: RES[(pt, "164", pol)] for pol in POL}; Rv["RS"] = rs_res(Rv); RV[pt] = Rv
          tableau(pt, Rv, sts)
      # simulations prioritaires
      w("## 4. Les trois simulations prioritaires\n")
      for pt, sts in SPL:
          Rv = RV[pt]
          for lab, pols in (("Simulation A — entrées progressives", ["T0-50", "T0-10", "T1", "T1v", "T2", "T2p"]),
                            ("Simulation B — changement de camp", ["T0-50", "T1", "T2", "T4", "LAD", "T5", "T7"]),
                            ("Simulation C — protection du capital (même plafond de 50 $)", ["T0-50", "T7", "T7s", "T5", "T6"])):
              tableau(f"{lab} — {pt}", Rv, sts, pols=pols)
          m7, m7s = mesures(Rv["T7"], sts), mesures(Rv["T7s"], sts); m5, m6 = mesures(Rv["T5"], sts), mesures(Rv["T6"], sts)
          d = np.array([Rv["T7"][s]["pnl"] - Rv["T7s"][s]["pnl"] for s in sts]); c = ic_cy(d)
          w(f"**H1033 — coût économique de la protection stricte ({pt})** : T7 − T7s = {d.sum():+.0f} $ [{c[0]:+.0f} ; {c[1]:+.0f}] ; pertes > 6 $ : "
            f"T7 {m7['p6']}, T7s {m7s['p6']} ; T5 − T6 = {m5['tot'] - m6['tot']:+.0f} $ (pertes > 6 $ : T5 {m5['p6']}, T6 {m6['p6']}).\n")
      # latence et frais
      if TE:
          w(f"## 5. Sensibilité à la latence et aux frais ({nomT})\n")
          noms = [v[0] for v in variantes]
          w("| Politique | " + " | ".join(f"{x} ms" if x.isdigit() else x for x in noms) + " |\n|---|" + "---|" * len(noms))
          for pol in POL:
              w(f"| {pol} | " + " | ".join(f"{sum(RES[(nomT, x, pol)][s]['pnl'] for s in TE):+.0f}" for x in noms) + " |")
          w("\n## 6. H1018 — Scénarios défavorables (164 ms)\n")
          w("| Politique | Normal | " + " | ".join(x for x, _ in STR) + " | Pertes > 6 $ (normal → pire scénario) | Perte max (normal → pire) |\n|---|---|" + "---|" * len(STR) + "---|---|")
          for pol in POLS_STR:
              base = mesures(RES[(nomT, "164", pol)], TE); ms_ = [mesures(RES[(nomT, x, pol)], TE) for x, _ in STR]
              w(f"| {pol} | {base['tot']:+.0f} | " + " | ".join(f"{m_['tot']:+.0f}" for m_ in ms_) + f" | {base['p6']} → {max(m_['p6'] for m_ in ms_)} | {base['pire']:+.0f} → {min(m_['pire'] for m_ in ms_):+.0f} |")
      # renforts, couvertures, inversions
      w("\n## 7. Renforts, couvertures, inversions\n")
      for pt, sts in SPL:
          Rv = RV[pt]
          w(f"**H1013 — P&L de chaque tranche jusqu'au règlement ({pt})**\n\n| Politique | Tranche | Nombre | Coût ($) | P&L ($) | P&L / $ |\n|---|---|---|---|---|---|")
          for pol in ("T1", "T1v", "T2", "T2p"):
              agg = collections.defaultdict(lambda: [0, 0.0, 0.0])
              for s in sts:
                  for (r, v, c_) in Rv[pol][s]["tr"]: a_ = agg[r]; a_[0] += 1; a_[1] += c_; a_[2] += v
              for r in sorted(agg): a_ = agg[r]; w(f"| {pol} | {r} | {a_[0]} | {a_[1]:.0f} | {a_[2]:+.0f} | {100 * a_[2] / max(a_[1], 1e-9):+.1f} % |")
          w(f"\n**P&L des transactions de protection par type ({pt})** (valeur au règlement − coût)\n\n| Politique | Couverture | Protection (vente) | Inversion | Verrou | Sortie |\n|---|---|---|---|---|---|")
          for pol in ("T3", "T4", "LAD", "T5", "T6", "T7", "T7s"):
              h = collections.defaultdict(float)
              for s in sts:
                  for k_, v in Rv[pol][s]["hed"].items(): h[k_] += v
              w(f"| {pol} | " + " | ".join(f"{h.get(k_, 0):+.0f}" for k_ in ("couverture", "protection", "inversion", "verrou", "sortie")) + " |")
          b1 = mesures(Rv["T1"], sts)
          w(f"\n**H1025 — coût par dollar de perte maximale évitée ({pt}, contre T1)**\n\n| Politique | P&L − T1 ($) | Plancher moyen le plus bas − T1 ($) | Coût par $ évité |\n|---|---|---|---|")
          for pol in ("T3", "T4", "LAD", "T7"):
              m_ = mesures(Rv[pol], sts); dp = m_["tot"] - b1["tot"]; df = m_["minf"] - b1["minf"]
              w(f"| {pol} | {dp:+.0f} | {df:+.2f} | {(-dp / (df * len(sts))) if df > 0 else float('nan'):+.2f} |")
          nsw = collections.Counter(p_ for (pp_, p_, *_r) in SW if pp_ == pt)
          w(f"\n**H1020 — changements de camp ({pt})** : " + (", ".join(f"{k_} {v}" for k_, v in nsw.items()) if nsw else "aucun") + ".\n")
      # régimes
      w("## 8. H1017 — Régimes au signal d'entrée\n")
      for pt, sts in SPL:
          Rv = RV[pt]
          w(f"| {pt} : régime | Cycles | " + " | ".join(["T0-50", "T1", "T3", "T5", "T7", "RS"]) + " |\n|---|---|" + "---|" * 6)
          for rg in sorted(set(REG[s] for s in sts)):
              S_ = [s for s in sts if REG[s] == rg]
              w(f"| {rg} | {len(S_)} | " + " | ".join(f"{sum(Rv[p_][s]['pnl'] for s in S_):+.0f}" for p_ in ["T0-50", "T1", "T3", "T5", "T7", "RS"]) + " |")
          w("")
      # ------------------------------------------------ H1036–H1040 : sauvetage par la jambe opposée
      w("## 9. H1036–H1040 — Sauvetage de la première position (entrée 10 $, mêmes cycles)\n")
      w("R0 conserver ; R1 vendre toute la position à −0,15 ; R2 couverture préventive (−0,05 et cerveau A contre ≥ 0,60) ; R3 couverture complète à −0,15 ; "
        "R4 couverture tardive (p ≤ 0,25) ; R5 vente de 50 % puis couverture du reste à −0,15 ; R6 inversion complète à −0,15 (vente de tout + 10 $ de l'opposé) ; "
        "R7 adaptatif (H1039 : probabilité de redevenir gagnante, apprise sur l'apprentissage ; vend si acheteur net > probabilité + 0,01, couvre si "
        "(1 − probabilité) − coût opposé > 0,01, sinon conserve). Couverture = achat de l'opposé pour toutes les parts non appariées. "
        "Les noms R0–R7 sont propres à cette étude (aucun lien avec le fantôme R4).\n")
      if RECD:
          w(f"Modèle de récupération H1039 : {len(RECD)} états détériorés d'apprentissage (taux de récupération {100 * np.mean([r[2] for r in RECD]):.1f} %).\n")
      RRV = {}
      for pt, sts in SPL:
          Rr = {pol: RES[(pt, "164", pol)] for pol in RPOL}; RRV[pt] = Rr
          tableau(f"Tournoi de sauvetage R0–R7 — {pt}", Rr, sts, ref="R0", pols=["R0", "R1", "R2", "R3", "R4", "R5", "R6", "R7"], ncomp=NCOMP_R)
          w(f"**Niveaux de détérioration (H1036, descriptif, aucun choix) — {pt}** : " + " ; ".join(
              f"{p_} {sum(Rr[p_][s_]['pnl'] for s_ in sts) - sum(Rr['R0'][s_]['pnl'] for s_ in sts):+.0f} $" for p_ in ("R1-10", "R1", "R1-20", "R1-30", "R3-10", "R3", "R3-20", "R3-30")) + " (écart avec R0).\n")
          D_ = [s_ for s_ in sts if Rr["R0"][s_]["defav"]]
          w(f"**Test décisif (section 9) — {pt}** : {len(D_)} positions devenues défavorables (p ≤ entrée − 0,15) ; ramené à 100.\n")
          w("| Politique | Perdantes sans intervention | Gagnantes sans intervention | Sauvetages (perte réduite) | Coût moyen d'un sauvetage réussi ($ gagnés) | Couvertures inutiles (gagnantes abîmées) | Coût des couvertures inutiles ($) | Perte moyenne R0 → politique | Perte max R0 → politique | P&L net − R0 (défavorables) | P&L net − R0 (tous) |\n|---|---|---|---|---|---|---|---|---|---|---|")
          for p_ in ("R1", "R2", "R3", "R4", "R5", "R6", "R7", "Rv", "Ra", "Rm"):
              if not D_: break
              k_ = 100 / len(D_); r0 = np.array([Rr["R0"][x]["pnl"] for x in D_]); rp = np.array([Rr[p_][x]["pnl"] for x in D_])
              perd, gagn = r0 < 0, r0 > 0; sauv = perd & (rp > r0); inut = gagn & (rp < r0)
              gs = (rp - r0)[sauv]; ci = (r0 - rp)[inut]
              lm0 = r0[r0 < 0].mean() if (r0 < 0).any() else 0; lmp = rp[rp < 0].mean() if (rp < 0).any() else 0
              w(f"| {p_} | {k_ * perd.sum():.0f} | {k_ * gagn.sum():.0f} | {k_ * sauv.sum():.0f} | {gs.mean() if len(gs) else float('nan'):+.2f} | {k_ * inut.sum():.0f} | "
                f"{ci.sum():.0f} | {lm0:+.2f} → {lmp:+.2f} | {r0.min():+.1f} → {rp.min():+.1f} | {(rp - r0).sum():+.0f} | "
                f"{sum(Rr[p_][x]['pnl'] - Rr['R0'][x]['pnl'] for x in sts):+.0f} |")
          w(f"\n**H1038 — vendre ou acheter l'opposé, à risque comparable (cible : pire résultat ≥ −6 $, dès p ≤ entrée − 0,15) — {pt}**\n")
          w("| Réaction | Cycles où elle a agi | Pire résultat final moyen | Pertes > 6 $ | Capital max moyen ($) | Frais ($) | P&L net ($) | Écart avec R0 (IC 90 %) |\n|---|---|---|---|---|---|---|---|")
          for p_, lab in (("R0", "ne rien faire"), ("Rv", "vendre une partie"), ("Ra", "acheter l'opposé"), ("Rm", "vendre une partie puis acheter l'opposé")):
              m_ = mesures(Rr[p_], sts); d = np.array([Rr[p_][x]["pnl"] - Rr["R0"][x]["pnl"] for x in sts]); c = ic_cy(d)
              w(f"| {lab} | {sum(Rr[p_][x]['res'] for x in sts)} | {np.mean([Rr[p_][x]['fl'] for x in sts]):+.2f} | {m_['p6']} | {np.mean([Rr[p_][x]['maxcap'] for x in sts]):.1f} | "
                f"{m_['frais']:.1f} | {m_['tot']:+.0f} | {d.sum():+.0f} [{c[0]:+.0f} ; {c[1]:+.0f}] |")
          w("")
      if TE:
          w(f"**Sauvetage — latence et frais ({nomT})**\n")
          noms = [v[0] for v in variantes]
          w("| Politique | " + " | ".join(f"{x} ms" if x.isdigit() else x for x in noms) + " |\n|---|" + "---|" * len(noms))
          for pol in ("R0", "R1", "R2", "R3", "R4", "R5", "R6", "R7", "Rv", "Ra", "Rm"):
              w(f"| {pol} | " + " | ".join(f"{sum(RES[(nomT, x, pol)][s_]['pnl'] for s_ in TE):+.0f}" for x in noms) + " |")
          w("\n**Critère (sauvetage, contre R0)** : une politique n'est retenue que si l'IC corrigé (7) de l'écart avec R0 est > 0 sur le test, la validation va "
            "dans le même sens, l'écart reste > 0 à 500 ms et sans les 5 meilleurs cycles.\n")
          w("| Politique | IC corrigé > 0 | Validation même sens | > 0 à 500 ms | > 0 sans les 5 meilleurs | Verdict |\n|---|---|---|---|---|---|")
          for pol in ("R1", "R2", "R3", "R4", "R5", "R6", "R7"):
              d = np.array([RRV[nomT][pol][x]["pnl"] - RRV[nomT]["R0"][x]["pnl"] for x in TE]); c2 = ic_cy(d, 0.10 / NCOMP_R)
              cv = sum(RRV["validation"][pol][x]["pnl"] - RRV["validation"]["R0"][x]["pnl"] for x in VA) > 0 if "validation" in RRV else None
              c5 = sum(RES[(nomT, "500", pol)][x]["pnl"] - RES[(nomT, "500", "R0")][x]["pnl"] for x in TE) > 0; ds = np.sort(d); ce = ds[:-5].sum() > 0 if len(ds) > 5 else False
              ok = c2[0] > 0 and cv is not False and c5 and ce; yn = lambda b: "—" if b is None else ("oui" if b else "non")
              w(f"| {pol} | {yn(c2[0] > 0)} | {yn(cv)} | {yn(c5)} | {yn(ce)} | {'**retenue**' if ok else 'non démontrée'} |")
      # verdict automatique (section 43)
      if TE:
          w(f"## 10. Critère de réussite (section 43) sur {nomT}\n")
          w("| Politique | IC corrigé > 0 | Pertes > 6 $ pas plus fréquentes | Jackpots ≥ 50 % | Écart > 0 à 500 ms | Écart > 0 sans les 5 meilleurs | Validation même sens | Verdict |\n|---|---|---|---|---|---|---|---|")
          Rt = RV[nomT]; a = np.array([Rt["T0-50"][s]["pnl"] for s in TE]); m0_ = mesures(Rt["T0-50"], TE)
          jk = [s for s in TE if s in ENT and ENT[s][1] <= 0.25 and Rt["T0-50"][s]["pnl"] > 0]; jref = sum(Rt["T0-50"][s]["pnl"] for s in jk)
          for pol in POL[1:] + ["RS"]:
              d = np.array([Rt[pol][s]["pnl"] for s in TE]) - a; c2 = ic_cy(d, 0.10 / NCOMP); m_ = mesures(Rt[pol], TE)
              c_a = c2[0] > 0; c_b = m_["p6"] <= m0_["p6"]; c_c = (sum(Rt[pol][s]["pnl"] for s in jk) >= 0.5 * jref) if jref > 0 else True
              c_d = (sum(RES[(nomT, "500", pol)][s]["pnl"] for s in TE) - sum(RES[(nomT, "500", "T0-50")][s]["pnl"] for s in TE) > 0) if pol != "RS" else None
              ds = np.sort(d); c_e = ds[:-5].sum() > 0 if len(ds) > 5 else False
              c_f = (sum(RV["validation"][pol][s]["pnl"] - RV["validation"]["T0-50"][s]["pnl"] for s in VA) > 0) if "validation" in RV else None
              ok = c_a and c_b and c_c and (c_d is not False) and c_e and (c_f is not False)
              yn = lambda b: "—" if b is None else ("oui" if b else "non")
              w(f"| {pol} | {yn(c_a)} | {yn(c_b)} | {yn(c_c)} | {yn(c_d)} | {yn(c_e)} | {yn(c_f)} | {'**intéressante**' if ok else 'non démontrée'} |")
      if JOURNAL:
          p_ = os.path.join(ICI, "resultat_reversal_h1003_journal_" + fam + ("_confirmation" if CONFIRM else "") + ".csv.gz")
          with gzip.open(p_, "wt") as f:
              wr = csv.writer(f); wr.writerow(["debut_cycle", "t_ms", "operation", "motif", "parts", "montant", "profit_si_up", "profit_si_down"]); wr.writerows(JOURNAL)
          w(f"\nJournal T7 ({nomT}) : chaque transaction avec les deux paiements possibles après exécution — {os.path.basename(p_)}, {len(JOURNAL)} lignes.\n")
    for fam in FAMS: rapport(fam, RESF[fam], REGF[fam], ENTF[fam], JF[fam], SWF[fam])
    w("\n## Limites\n- Exécution preneur seulement ; notre propre impact au-delà de 5 s n'est pas modélisé.\n"
      "- Toutes les politiques partagent la même probabilité ; si elle n'a pas d'avantage sur le marché, la gestion ne peut pas en créer.\n"
      "- Nombreuses politiques : seuls les IC corrigés comptent. Peu de cycles par échantillon.\n")
    w(f"_Calcul : {time.time() - t_go:.0f} s._\n")
    open(SORTIE, "w").write("\n".join(o)); print("\n".join(o))


if __name__ == "__main__":
    main()
