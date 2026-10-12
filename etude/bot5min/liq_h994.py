"""BOT95 — LIQUIDATION INTELLIGENCE ENGINE : H994 à H1002 (Pitch, 12.10.2026 16:21). PROTOCOLE PRÉ-ENREGISTRÉ (ce fichier tel que committé le
12.10.2026, avant toute donnée de validation ou de test). Hors ligne ; aucun ordre ; aucun abonnement ; aucun bot, H816, H821, R4 ni fantôme modifié.
Les résultats de ce protocole sont séparés de ceux de H986–H993.

DONNÉES (Dublin, heures de réception) : ticker Bybit BTCUSDT (dernier, mark, index, open interest, funding) depuis le 12.10 14:26 UTC ;
  Binance perp BTCUSDT (mark/index 1 s, liquidations forceOrder — au plus une par seconde, échantillonnées —, transactions agressives) depuis le
  12.10 ~14:50 UTC ; open interest Binance (REST, 5 s) ; liquidations Bybit agrégées (allLiquidation) ; transactions et carnets Binance/Bybit ;
  Chainlink ; carnet Polymarket ; résultat officiel.
ÉCHANTILLONS (chronologiques, figés) : apprentissage = cycles du 12.10 15:00 UTC au 13.10 00:00 UTC ; validation = 13.10 00:00 → 14.10 00:00 UTC ;
  test inédit = 14.10 00:00 UTC → fin des données disponibles au lancement. Tous les paramètres appris sur l'apprentissage seul. La période du
  13.10 n'est utilisée qu'en validation de CE protocole ; elle ne sert à choisir aucune règle de H816/H821 (verdict déjà programmé, inchangé).
SALVE : liquidations d'un même côté (Bybit allLiquidation + Binance forceOrder, en $) ≥ 50 000 $ sur 5 s, au plus une par 10 s et par côté.
  Côté « ventes forcées » = positions longues liquidées (pression baissière) ; « achats forcés » = courtes liquidées (pression haussière).
VARIABLES À t (seconde, messages reçus avant t) : écart mark − index Bybit et Binance (en $ et z sur 600 s) et leur variation sur 5 s ;
  variation d'OI Bybit et Binance sur 10 s et 60 s (en %) ; base perp − spot ; OFI Binance 5 s ; pression nette agressive 5 s ; rapport de
  profondeur 20 $ ; accélération du prix (variation 5 s − variation des 5 s précédentes) ; volatilité 300 s ; funding.
H994 CARTE DE PRESSION : à partir des seules augmentations d'OI Bybit (prix et quantité au moment de l'ajout, 24 h glissantes), zones de liquidation
  supposées pour des leviers de 10, 25, 50, 100 (moitié longs, moitié courts) ; densité de la carte à ± 0,1 % du prix. Probabilité d'une salve
  dans les 30 s selon le tiers de densité, contre une carte placebo décalée de ± 0,5 %. Les vrais niveaux de liquidation sont inconnus : c'est un scénario.
H995 DIVERGENCE MARK/INDEX : AUC pour prévoir une salve dans 1 / 5 / 10 / 30 s ; modèle A = |variation du prix 5 s|, volatilité, OFI, pression ;
  modèle B = A + divergence mark/index (niveau, z, variation). ΔAUC, IC 90 % par cycles, corrigé (4 horizons).
H996 CHOC D'OI : 4 régimes (prix ↑/↓ × OI ↑/↓ sur 60 s, seuils = médianes absolues de l'apprentissage) ; mouvement du prix sur 60 s et
  probabilité de salve dans 60 s par régime ; ΔAUC de l'OI pour prévoir le signe du prix à 30 s (en plus du flux et du momentum).
H997 CASCADE : probabilité d'une 2e salve du même côté dans 1/3/5/10/30 s et d'un mouvement durable (> 1,5 σ60 sur 60 s dans le sens forcé),
  contre des chocs de prix appariés (même |variation 5 s| ± 30 %) sans salve.
H998 ABSORPTION DU FLUX FORCÉ : après chaque salve, continuation à 5/15/30/60/120 s et impact par dollar agressif sur 5 s ; corrélation entre
  impact et continuation ; variation de la probabilité de règlement M0 et résultat officiel − M0 (signé).
H999 CASCADE INTER-PLATEFORMES : décalage entre salves Bybit et Binance (± 5 s), contre placebo par décalage circulaire de 60 à 600 s.
H1000 PRÉ-LIQUIDATION : logistique (apprentissage) prévoyant une salve dans les 5 à 30 s, avec toutes les variables à t (aucune salve en cours :
  aucune liquidation ≥ 10 000 $ dans les 10 s précédentes). Seuil = 99e centile du score sur l'apprentissage. Mesures : AUC, précision, rappel,
  calibration, délai d'avance (début de la salve − signal), et H1002.
H1001 RÈGLEMENT : décisions à 240/180/120/90/60/30 s ; A = M0 recalibré ; B = A + flux BTC (pression 5/30 s, momentum) ; C = B + variables de
  liquidation (divergences, OI, liquidations des 60 s) ; Brier, log loss ; tous, proches de 50 % ; IC corrigé (2 comparaisons × 2 sous-ensembles).
H1002 ALPHA EXÉCUTABLE : à chaque signal H1000 (et à chaque salve H997/H998 pour comparaison « après coup »), achat de 20 $ du jeton dans le sens
  de la pression attendue (sens = signe de la variation du prix sur 5 s pour H1000 ; sens forcé pour les salves) au prix vendeur vu, exécuté à
  164 / 200 / 250 / 500 ms sur le carnet enregistré, conservé, résultat officiel ; non-exécutions comptées ; P&L sans les 1 / 3 / 5 meilleurs ;
  comparaison au prix Polymarket (avantage = résultat − prix − frais), Up / Down / abstention.
CRITÈRE DE POURSUITE (section 16 de Pitch) : amélioration de la calibration hors échantillon face au marché ET/OU P&L net exécutable avec IC > 0
  sur la validation ET le test, sans dépendre des 5 meilleurs trades. Verdicts : confirmé / non démontré / rejeté / données insuffisantes.
ADDENDUM (Pitch, 12.10.2026 17:03, avant toute donnée de validation ou de test ; périodes, seuil de 50 000 $ et règles inchangés, aucun seuil
  optimisé sur la validation ni le test) — section 8 du rapport :
  8.1 Pression pré-liquidation à 1 / 3 / 5 / 10 / 30 s avant le début de chaque salve (première seconde avec liquidation du côté de la salve
      dans les 5 s du déclenchement), variables connues à cet instant (OFI 5 s, pression nette 5 s, prix 5 s, mark − index Bybit et Binance
      signés dans le sens forcé ; OI Bybit 10 s non signé), contre 5 témoins par salve tirés parmi les instants du même échantillon sans aucune
      liquidation dans les 60 s avant et après (sens tiré au hasard). Différence salves − témoins, IC 90 % par cycles.
  8.2 Délais réels (s, depuis la seconde de la première liquidation) : premier avertissement H1000 (score ≥ seuil dans les 30 s avant),
      déclenchement de la salve, réaction BTC (premier écart Binance ≥ max(5 $, 2 σ1s √k) dans le sens forcé, ≤ 60 s), réaction Polymarket
      (premier mouvement ≥ 1 c du meilleur vendeur du jeton du sens forcé, carnet relu toutes les 100 ms sur 20 s), première exécution possible
      (avertissement ou déclenchement + 164 ms). Part des cas où Polymarket a réagi avant notre première exécution possible.
  8.3 Par latence 164 / 200 / 250 / 500 ms : exécutions, quantité, prix réellement payé (frais compris, seuls les niveaux ≤ meilleur vendeur vu),
      taux de victoire, avantage, P&L net total et par signal (IC 90 % par cycles).
  8.4 Rapports séparés : cascades anticipées (≥ 1 avertissement H1000 dans les 5–30 s avant le début), fausses alertes (signal H1000 sans salve
      dans 5–30 s), cascades manquées, précision, rappel, gain de temps, impact sur le TWAP Chainlink (mouvement Chainlink 5/30/60 s signé et,
      pour les salves avant la fin du cycle, TWAP final − Chainlink au déclenchement, signé, contre témoins), P&L par signal, drawdown,
      pire perte et moyenne des 5 % pires, IC par cycles.
Usage : python3 etude/bot5min/liq_h994.py dossier_cycles_dublin [--controle]  (--controle = apprentissage seul, pour vérifier le code)"""
import os, sys, math, time, json, gzip, collections
import numpy as np, pandas as pd

ICI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, ICI)
import latence_h766 as LH, liquidite_h833 as L, dpe_h841 as DP, pression_h971 as PR
CONTROLE = "--controle" in sys.argv
DEB = 1791817200; VAL = 1791849600; TEST = 1791936000
SORTIE = os.path.join(ICI, "resultat_liq_h994" + ("_controle" if CONTROLE else "") + ".md")
MISE = 20.0; RNG = np.random.default_rng(994); fee = lambda p: 0.07 * p * (1 - p); SEUIL = 50000


def cell(v, g):
    v = np.asarray(v, float); g = np.asarray(g); m = np.isfinite(v)
    if m.sum() < 5: return f"— (n={int(m.sum())})"
    c = L.ic_g(g[m], v[m]); return f"{v[m].mean():+.3f} [{c[0]:+.3f} ; {c[1]:+.3f}] (n={int(m.sum())})"


def part_of(st):
    if st < DEB: return None
    if st < VAL: return "apprentissage"
    if CONTROLE: return None
    return "validation" if st < TEST else "test"


COUPES = set()


def charger_deriv(G, cyc):
    n = G["n"]; t0 = G["t0"]
    F = {k: np.full(n, np.nan) for k in ("by_mark", "by_index", "by_oi", "by_fund", "bn_mark", "bn_index", "bn_oi")}
    LQ = {"a": np.zeros(n), "v": np.zeros(n)}; LQs = {"by": {"a": np.zeros(n), "v": np.zeros(n)}, "bn": {"a": np.zeros(n), "v": np.zeros(n)}}
    audit = collections.defaultdict(list)
    for st, c in cyc.items():
        try: R = json.load(gzip.open(c["f"]))
        except Exception: continue
        if R.get("coupe"): COUPES.add(st)
        D = R.get("deriv") or {}
        for r in D.get("by_ticker", []):
            i = int(math.ceil(r[0] / 1000)) - t0
            if 0 <= i < n: F["by_mark"][i], F["by_index"][i], F["by_oi"][i], F["by_fund"][i] = r[3], r[4], r[5], r[6]
            audit["by_ticker"].append(r[0])
        for r in D.get("bn_mark", []):
            i = int(math.ceil(r[0] / 1000)) - t0
            if 0 <= i < n: F["bn_mark"][i], F["bn_index"][i] = r[2], r[3]
            audit["bn_mark"].append(r[0])
        for r in D.get("bn_oi", []):
            i = int(math.ceil(r[0] / 1000)) - t0
            if 0 <= i < n: F["bn_oi"][i] = r[2]
            audit["bn_oi"].append(r[0])
        for r in D.get("bn_liq", []):
            i = int(math.ceil(r[0] / 1000)) - t0
            if 0 <= i < n and r[3] and (r[5] or r[4]):
                usd = r[3] * (r[5] or r[4]); side = "v" if r[2] == "SELL" else "a"; LQ[side][i] += usd; LQs["bn"][side][i] += usd
            audit["bn_liq"].append(r[0])
        for r in D.get("bn_perp_tx", []): audit["bn_perp_tx"].append(r[0])
        for r in R.get("fx", []):
            x = r[1].get("liq_bybit")
            if not x: continue
            i = int(math.ceil(r[0] / 1000)) - t0
            if 0 <= i < n: LQ["a"][i] += x[0]; LQ["v"][i] += x[1]; LQs["by"]["a"][i] += x[0]; LQs["by"]["v"][i] += x[1]
    for k in F: F[k] = pd.Series(F[k]).ffill(limit=10).values
    return F, LQ, LQs, audit


def main():
    t_go = time.time(); o = []; w = o.append
    G, cyc = L.grille(sys.argv[1]); P = L.preparer(G); L.P_sd1 = P["sd1"]; Y = L.resultats_officiels(cyc); V = PR.grandeurs(G, P)
    cycles = sorted(s for s in cyc if part_of(s)); part = {s: part_of(s) for s in cycles}
    PARTS = [p for p in ("apprentissage", "validation", "test") if p in part.values()]; nb = collections.Counter(part.values())
    F, LQ, LQs, audit = charger_deriv(G, cyc)
    stof = lambda i: (G["t0"] + i) - (G["t0"] + i) % 300; bn = G["bn"]; n = G["n"]
    cs = lambda x: np.concatenate([[0], np.cumsum(np.nan_to_num(x))]); win = lambda C, i, k: C[i + 1] - C[max(i + 1 - k, 0)]
    CA, CV = cs(LQ["a"]), cs(LQ["v"])
    w(f"# Bot95 — Liquidation Intelligence Engine H994–H1002 ({'CONTRÔLE : apprentissage seul' if CONTROLE else 'apprentissage / validation / test inédit'})\n")
    w(f"Généré le {time.strftime('%d.%m.%Y %H:%M', time.gmtime())} UTC. Cycles : " + ", ".join(f"{k} {nb[k]}" for k in PARTS) + ". Aucun ordre ; aucun abonnement.\n")
    w("## 0. Audit des nouveaux flux\n\n| Flux | Messages | Intervalle médian (ms) | Trous > max(5 s ; 3 × médiane) | Plus long trou (s) | Doublons d'horodatage |\n|---|---|---|---|---|---|")
    for k, T in audit.items():
        T = np.sort(np.array(T)); d = np.diff(T) if len(T) > 1 else np.array([0]); md = np.median(d)
        w(f"| {k} | {len(T)} | {md:.0f} | {int((d > max(5000, 3 * md)).sum())} | {d.max() / 1000:.0f} | {int((d == 0).sum())} |")
    cc_ = [s_ for s_ in cyc if part_of(s_)]; nc = len(COUPES & set(cc_))
    w(f"\nCycles de l'étude : {len(cc_)}" + f" ; tronqués par la limite de stockage du serveur : {nc} (gardés, signalés)" + ".\n")
    # variables
    z600 = lambda x: ((pd.Series(x) - pd.Series(x).rolling(600, min_periods=200).mean().shift(1)) / pd.Series(x).rolling(600, min_periods=200).std().shift(1)).values
    dby = F["by_mark"] - F["by_index"]; dbn = F["bn_mark"] - F["bn_index"]; zby, zbn = z600(dby), z600(dbn)
    lag = lambda x, k: np.concatenate([np.full(k, np.nan), x[:-k]])
    oi10 = (F["by_oi"] / lag(F["by_oi"], 10) - 1) * 100; oi60 = (F["by_oi"] / lag(F["by_oi"], 60) - 1) * 100
    oib60 = (F["bn_oi"] / lag(F["bn_oi"], 60) - 1) * 100
    base = G["perp"] - bn; d5 = P["d5"]; acc = d5 - lag(d5, 5); vol = P["sd1"]
    def X_(i):
        return [abs(d5[i]) if np.isfinite(d5[i]) else 0, vol[i], V["ofi5"][i], V["Pn5"][i], acc[i], dby[i], zby[i], dby[i] - dby[i - 5], dbn[i], zbn[i], dbn[i] - dbn[i - 5],
                oi10[i], oi60[i], oib60[i], base[i], (G["cb20"][i] - G["ca20"][i]) / max(G["cb20"][i] + G["ca20"][i], 1e-9), F["by_fund"][i]]
    # salves
    sal = []; lastS = {"a": -99, "v": -99}
    for i in range(700, n - 121):
        st = stof(i)
        if st not in part or not G["ok"][i]: continue
        for sd, C in (("a", CA), ("v", CV)):
            if win(C, i, 5) >= SEUIL and i - lastS[sd] >= 10:
                lastS[sd] = i; sal.append(dict(i=i, st=st, sd=sd, s=1 if sd == "a" else -1, part=part[st], amp=win(C, i, 5)))
    w(f"\n{len(sal)} salves (≥ 50 000 $ du même côté en 5 s, Bybit + Binance).\n")
    nouvelle = lambda i, sd, k: float(((CA if sd == "a" else CV)[min(i + 1 + k, n)] - (CA if sd == "a" else CV)[i + 1]) >= SEUIL)
    salve_dans = lambda i, a, b: float(max(CA[min(i + 1 + b, n)] - CA[min(i + 1 + a, n)], CV[min(i + 1 + b, n)] - CV[min(i + 1 + a, n)]) >= SEUIL)

    # H994
    w("## 1. H994 — Carte de pression des liquidations (scénarios de levier)\n")
    grille_px = np.arange(70000, 100000, 10.0); dens = np.zeros(n)
    hist = collections.deque(); carte = np.zeros(len(grille_px))
    def ajoute(px, q, sign):
        for lv in (10, 25, 50, 100):
            for pz in (px * (1 - 1 / lv), px * (1 + 1 / lv)):
                j = int((pz - 70000) / 10)
                if 0 <= j < len(carte): carte[j] += sign * q / 8
    prev_oi = np.nan
    for i in range(0, n, 10):
        oi = F["by_oi"][i]; px = G["perp"][i]
        if np.isfinite(oi) and np.isfinite(prev_oi) and np.isfinite(px) and oi > prev_oi: ajoute(px, oi - prev_oi, 1); hist.append((i, px, oi - prev_oi))
        while hist and hist[0][0] < i - 86400: _, p_, q_ = hist.popleft(); ajoute(p_, q_, -1)
        prev_oi = oi if np.isfinite(oi) else prev_oi
        if np.isfinite(bn[i]):
            j = int((bn[i] - 70000) / 10); dens[i:i + 10] = carte[max(j - 8, 0):j + 9].sum() if 0 <= j < len(carte) else 0
    w("| Échantillon | Tiers de densité | Instants | Salve dans 30 s | Placebo (carte décalée ± 0,5 %) |\n|---|---|---|---|---|")
    for pt in PARTS:
        I = np.array([i for i in range(700, n - 31, 5) if part.get(stof(i)) == pt and G["ok"][i]])
        if not len(I): continue
        ds = dens[I]; q = np.percentile(ds[part_of(stof(I[0])) == pt] if False else ds, [33.3, 66.7])
        y = np.array([salve_dans(i, 0, 30) for i in I])
        off = int(0.005 * 82000 / 10)
        for k, lab in enumerate(("bas", "moyen", "haut")):
            m = (np.searchsorted(q, ds) == k)
            w(f"| {pt} | {lab} | {int(m.sum())} | {100 * y[m].mean() if m.any() else float('nan'):.1f} % | — |")
    # H995 / H1000 : modèles de prévision de salve
    I = np.array([i for i in range(700, n - 31, 2) if stof(i) in part and G["ok"][i] and np.isfinite(F["by_mark"][i]) and win(CA, i, 10) + win(CV, i, 10) < 10000])
    pI = np.array([part[stof(i)] for i in I]); gI = np.array([stof(i) for i in I]); trm = pI == "apprentissage"
    XA = np.nan_to_num(np.array([X_(i)[:5] for i in I])); XF = np.nan_to_num(np.array([X_(i) for i in I]))
    w("\n## 2. H995 / H1000 — Prévoir une salve avant qu'elle n'arrive\n")
    w("| Horizon | Échantillon | Taux de base | AUC sans dérivés (prix, volatilité, OFI, pression, accélération) | AUC avec mark/index, OI, base, profondeur, funding | ΔAUC (IC 90 % ; corrigé 4) |\n|---|---|---|---|---|---|")
    pr5_30 = None
    for (a, b, lab) in ((0, 1, "1 s"), (0, 5, "5 s"), (0, 10, "10 s"), (5, 30, "5–30 s")):
        y = np.array([salve_dans(i, a, b) for i in I])
        if y[trm].sum() < 3: w(f"| {lab} | apprentissage | {100 * y[trm].mean():.2f} % | — | — | données insuffisantes |"); continue
        prd = {}
        for k_, X in (("A", XA), ("F", XF)):
            mu, sd = X[trm].mean(0), X[trm].std(0) + 1e-9; bb = L.ajuster((X[trm] - mu) / sd, y[trm], 2.0); prd[k_] = L.predire(bb, (X - mu) / sd)
        if lab == "5–30 s": pr5_30 = (prd["F"], y)
        for pt in [p for p in PARTS if p != "apprentissage"] or ["apprentissage"]:
            m = pI == pt; yt = y[m]
            if yt.sum() < 2: w(f"| {lab} | {pt} | {100 * yt.mean():.2f} % | — | — | données insuffisantes |"); continue
            g = gI[m]; U = np.unique(g); D = []
            for _ in range(300):
                mm = np.isin(g, RNG.choice(U, len(U)))
                if 0 < yt[mm].sum() < mm.sum(): D.append(L.auc(prd["F"][m][mm], yt[mm]) - L.auc(prd["A"][m][mm], yt[mm]))
            w(f"| {lab} | {pt} | {100 * yt.mean():.2f} % | {L.auc(prd['A'][m], yt):.3f} | {L.auc(prd['F'][m], yt):.3f} | "
              f"{np.percentile(D, 50):+.3f} [{np.percentile(D, 5):+.3f} ; {np.percentile(D, 95):+.3f}] ; [{np.percentile(D, 1.25):+.3f} ; {np.percentile(D, 98.75):+.3f}] |")
    sig = []; score = {}; thr = np.inf
    if pr5_30 is not None:
        sc, y = pr5_30; thr = np.percentile(sc[trm], 99); score = dict(zip(I.tolist(), sc.tolist()))
        w(f"\n**H1000** — seuil = 99e centile du score d'apprentissage ({thr:.4f}).\n")
        w("| Échantillon | Signaux | Précision (salve dans 5–30 s) | Rappel | Délai d'avance médian (s) |\n|---|---|---|---|---|")
        for pt in PARTS:
            m = pI == pt; fire = m & (sc >= thr)
            if not m.any(): continue
            prec = y[fire].mean() if fire.any() else float("nan"); rec = (y[fire].sum() / max(y[m].sum(), 1))
            leads = []
            for i in I[fire]:
                for k in range(5, 31):
                    if max(LQ["a"][i + k], LQ["v"][i + k]) > 0 and salve_dans(i, k - 5, k): leads.append(k); break
            w(f"| {pt} | {int(fire.sum())} | {100 * prec:.1f} % | {100 * rec:.1f} % | {np.median(leads) if leads else float('nan'):.0f} |")
            last = -99
            for i in I[fire]:
                if i - last >= 30: sig.append(dict(i=i, st=stof(i), s=1 if (d5[i] or 0) > 0 else -1, part=pt, src="H1000")); last = i
    # H996
    w("\n## 3. H996 — Régimes prix × open interest (60 s)\n")
    J = np.array([i for i in range(700, n - 61, 10) if stof(i) in part and G["ok"][i] and np.isfinite(oi60[i]) and np.isfinite(bn[i - 60])])
    if len(J):
        dp = bn[J] - bn[J - 60]; do = oi60[J]; pJ = np.array([part[stof(i)] for i in J])
        mp, mo = np.median(np.abs(dp[pJ == "apprentissage"])) if (pJ == "apprentissage").any() else 0, np.median(np.abs(do[pJ == "apprentissage"])) if (pJ == "apprentissage").any() else 0
        w("| Échantillon | Régime | Instants | Prix sur 60 s suivantes ($) | Salve dans 60 s |\n|---|---|---|---|---|")
        for pt in PARTS:
            for lab, f in (("prix ↑ / OI ↑", lambda a, b: (a > mp) & (b > mo)), ("prix ↑ / OI ↓", lambda a, b: (a > mp) & (b < -mo)),
                           ("prix ↓ / OI ↑", lambda a, b: (a < -mp) & (b > mo)), ("prix ↓ / OI ↓", lambda a, b: (a < -mp) & (b < -mo))):
                m = (pJ == pt) & f(dp, do)
                if m.sum() < 5: continue
                fut = bn[J[m] + 60] - bn[J[m]]; ss = np.array([salve_dans(i, 0, 60) for i in J[m]])
                w(f"| {pt} | {lab} | {int(m.sum())} | {cell(fut, [stof(i) for i in J[m]])} | {100 * ss.mean():.1f} % |")
    # H997 / H998
    w("\n## 4. H997 / H998 — Après une salve : nouvelle salve, continuation, absorption, règlement\n")
    w("| Échantillon | Salves | 2e salve dans 1 / 5 / 30 s | Témoins appariés | Mouvement durable (> 1,5 σ60 sur 60 s) | Continuation 30 s / 120 s (sens forcé, $) | Résultat − M0 (signé) |\n|---|---|---|---|---|---|---|")
    cand = np.array([i for i in range(700, n - 121, 7) if stof(i) in part and win(CA, i, 5) + win(CV, i, 5) < 1000 and np.isfinite(d5[i])])
    for pt in PARTS:
        Z = [z for z in sal if z["part"] == pt]
        if not Z: continue
        g = [z["st"] for z in Z]
        p2 = " / ".join(f"{100 * np.mean([nouvelle(z['i'], z['sd'], k) for z in Z]):.0f} %" for k in (1, 5, 30))
        tem = []
        for z in Z:
            a = abs(d5[z["i"]]) if np.isfinite(d5[z["i"]]) else 0; cc = cand[np.array([part[stof(i)] == pt for i in cand])] if len(cand) else cand
            mm = cc[np.abs(np.abs(d5[cc]) - a) <= 0.3 * max(a, 1)] if len(cc) else cc
            if len(mm): tem += list(RNG.choice(mm, min(5, len(mm)), replace=False))
        pt2 = " / ".join(f"{100 * np.mean([max(nouvelle(i, 'a', k), nouvelle(i, 'v', k)) for i in tem]):.0f} %" if tem else "—" for k in (1, 5, 30))
        dur = np.mean([((bn[z["i"] + 60] - bn[z["i"]]) * z["s"]) > 1.5 * vol[z["i"]] * math.sqrt(60) for z in Z])
        def regl(z):
            rest = z["st"] + 300 - (G["t0"] + z["i"])
            if not (30 <= rest <= 280) or z["st"] not in Y: return np.nan
            m_ = L.m0(G, cyc, z["st"], rest); return ((Y[z["st"]] - m_[0]) * z["s"]) if m_ else np.nan
        w(f"| {pt} | {len(Z)} | {p2} | {pt2} | {100 * dur:.0f} % | {cell([(bn[z['i'] + 30] - bn[z['i']]) * z['s'] for z in Z], g)} / {cell([(bn[z['i'] + 120] - bn[z['i']]) * z['s'] for z in Z], g)} | {cell([regl(z) for z in Z], g)} |")
        for z in Z: sig.append(dict(i=z["i"], st=z["st"], s=z["s"], part=pt, src="salve (après coup)"))
    # H999
    w("\n## 5. H999 — Bybit avant Binance, ou l'inverse ?\n")
    def tps(d):
        T = []; last = -99
        for i in range(n):
            if (d["a"][max(i - 4, 0):i + 1].sum() >= 20000 or d["v"][max(i - 4, 0):i + 1].sum() >= 20000) and i - last >= 10: T.append(i); last = i
        return np.array(T)
    Tb, Tn = tps(LQs["by"]), tps(LQs["bn"])
    if len(Tb) and len(Tn):
        def lags(A, Bv):
            out = []
            for a in A:
                j = np.searchsorted(Bv, a - 5);
                if j < len(Bv) and abs(Bv[j] - a) <= 5: out.append(Bv[j] - a)
            return np.array(out)
        lg_ = lags(Tb, Tn); pl = lags(Tb, np.sort((Tn + RNG.integers(60, 600)) % n))
        w(f"Salves Bybit (≥ 20 000 $) : {len(Tb)} ; Binance : {len(Tn)}. Paires à ± 5 s : {len(lg_)} (placebo décalé : {len(pl)}). "
          f"Décalage médian Binance − Bybit : {np.median(lg_) if len(lg_) else float('nan'):+.1f} s ; Bybit d'abord : {100 * np.mean(lg_ > 0) if len(lg_) else float('nan'):.0f} %, "
          f"simultané : {100 * np.mean(lg_ == 0) if len(lg_) else float('nan'):.0f} %.\n")
    else: w("Données insuffisantes.\n")
    # H1001
    w("## 6. H1001 — Règlement officiel : M0, + flux BTC, + variables de liquidation\n")
    Dd = []
    for st in cycles:
        if st not in Y: continue
        for rest in (240, 180, 120, 90, 60, 30):
            m_ = L.m0(G, cyc, st, rest)
            if not m_: continue
            i = m_[2]
            if i < 700: continue
            fl = [V["Pn5"][i], V["Pn30"][i], (bn[i] - bn[i - 30]) / max(vol[i], 1e-9)]
            lq = [dby[i], zby[i], dbn[i], zbn[i], oi60[i], oib60[i], win(CA, i, 60) - win(CV, i, 60), base[i]]
            Dd.append(dict(st=st, p=m_[0], y=Y[st], fl=fl, lq=lq, part=part[st]))
    tr = [d for d in Dd if d["part"] == "apprentissage"]
    if len(tr) > 30:
        mk = lambda Z, k: np.nan_to_num(np.array([[L.lg(d["p"])] + (d["fl"] if k >= 1 else []) + (d["lq"] if k >= 2 else []) for d in Z]))
        B_ = {}
        for k in (0, 1, 2):
            X = mk(tr, k); mu, sd = X.mean(0), X.std(0) + 1e-9; mu[0], sd[0] = 0, 1; B_[k] = (L.ajuster((X - mu) / sd, np.array([d["y"] for d in tr]), 2.0 if k else 0.1), mu, sd)
        w("| Échantillon | Sous-ensemble | Décisions | Brier A | Brier B (+ flux) | Brier C (+ liquidations) | C − B (IC 90 % ; corrigé 4) |\n|---|---|---|---|---|---|---|")
        for pt in PARTS:
            Z = [d for d in Dd if d["part"] == pt]
            if not Z: continue
            yv = np.array([d["y"] for d in Z]); g = np.array([d["st"] for d in Z])
            pr = {k: L.predire(B_[k][0], (mk(Z, k) - B_[k][1]) / B_[k][2]) for k in (0, 1, 2)}
            for lab, m in (("toutes", np.ones(len(Z), bool)), ("proches de 50 %", np.array([0.35 <= d["p"] <= 0.65 for d in Z]))):
                if m.sum() < 10: continue
                dl = L.brier(pr[1][m], yv[m]) - L.brier(pr[2][m], yv[m]); c1 = L.ic_g(g[m], dl); c2 = L.ic_g(g[m], dl, 0.10 / 4)
                w(f"| {pt} | {lab} | {int(m.sum())} | {L.brier(pr[0][m], yv[m]).mean():.4f} | {L.brier(pr[1][m], yv[m]).mean():.4f} | {L.brier(pr[2][m], yv[m]).mean():.4f} | "
                  f"{dl.mean():+.5f} [{c1[0]:+.5f} ; {c1[1]:+.5f}] ; [{c2[0]:+.5f} ; {c2[1]:+.5f}] |")
    # H1002
    w("\n## 7. H1002 — Alpha exécutable sur Polymarket\n")
    w("| Échantillon | Source | Signaux | Exécutés à 164 ms | Victoire | Prix payé | Avantage (résultat − prix − frais) | P&L 164 / 200 / 250 / 500 ms ($) | P&L sans les 1 / 3 / 5 meilleurs | IC 90 % (164 ms) |\n|---|---|---|---|---|---|---|---|---|---|")
    RES = {}
    for pt in PARTS:
        for src in ("H1000", "salve (après coup)"):
            Z = [s_ for s_ in sig if s_["part"] == pt and s_["src"] == src and s_["st"] in Y and s_["st"] + 300 - (G["t0"] + s_["i"]) >= 35]
            if not Z: continue
            R_ = []
            for s_ in Z:
                cy = LH.Cycle(cyc[s_["st"]]["f"]); t = (G["t0"] + s_["i"]) * 1000
                E = {k: DP.compact(x) for k, x in cy.etats([t] + [t + ms for ms in (164, 200, 250, 500)]).items()}
                X = "Up" if s_["s"] > 0 else "Down"; vv = DP.vend(E[t], X); yX = Y[s_["st"]] if X == "Up" else 1 - Y[s_["st"]]; row = {}
                for ms in (164, 200, 250, 500):
                    q = cc = 0.0
                    if vv:
                        for px, sz in DP.vend(E[t + ms], X):
                            if px > vv[0][0]: break
                            if px <= 0 or px >= 1000: continue
                            pp = px / 1000; u = pp + fee(pp); k = min(sz, (MISE - cc) / u)
                            if k <= 1e-9: break
                            q += k; cc += k * u
                    row[ms] = (q * yX - cc, cc / q if q > 0 else np.nan, q > 0, q)
                R_.append((s_["st"], yX, row, s_["i"]))
            RES[(pt, src)] = R_; ex = [r for r in R_ if r[2][164][2]]
            if not ex: w(f"| {pt} | {src} | {len(Z)} | 0 | — | — | — | — | — | — |"); continue
            pn = np.array([r[2][164][0] for r in ex]); g = np.array([r[0] for r in ex]); srt = np.sort(pn)[::-1]
            ci = L.ic_tot(g, pn) if len(ex) >= 3 else (np.nan, np.nan)
            w(f"| {pt} | {src} | {len(Z)} | {len(ex)} | {100 * np.mean([r[1] for r in ex]):.0f} % | {np.nanmean([r[2][164][1] for r in ex]):.2f} | "
              f"{cell([r[1] - r[2][164][1] for r in ex], g)} | " + " / ".join(f"{sum(r[2][ms][0] for r in R_):+.0f}" for ms in (164, 200, 250, 500)) +
              f" | {srt[1:].sum():+.0f} / {srt[3:].sum():+.0f} / {srt[5:].sum():+.0f} | [{ci[0]:+.0f} ; {ci[1]:+.0f}] |")
    # ===== 8. ADDENDUM Pitch 12.10 17:03 — contrôles supplémentaires (règles, périodes et seuils inchangés) =====
    w("\n## 8. Contrôles demandés par Pitch le 12.10 à 17:03 (règles, périodes et seuils inchangés)\n")
    def debut(z):
        L_ = LQ[z["sd"]]
        for j in range(z["i"] - 4, z["i"] + 1):
            if L_[j] > 0: return j
        return z["i"]
    for z in sal: z["i0"] = debut(z)
    def diff_ic(gs, vs, gc, vc, B=2000):
        gs, vs, gc, vc = np.asarray(gs), np.asarray(vs, float), np.asarray(gc), np.asarray(vc, float)
        ms, mc = np.isfinite(vs), np.isfinite(vc); gs, vs, gc, vc = gs[ms], vs[ms], gc[mc], vc[mc]
        U = np.unique(np.concatenate([gs, gc]))
        if len(U) < 3 or not len(vs) or not len(vc): return np.nan, np.nan, np.nan
        D = []
        for _ in range(B):
            u = RNG.choice(U, len(U)); a = np.isin(gs, u); b = np.isin(gc, u)
            if a.any() and b.any():
                ws = np.array([np.sum(u == x) for x in gs[a]]); wc = np.array([np.sum(u == x) for x in gc[b]])
                D.append(np.average(vs[a], weights=ws) - np.average(vc[b], weights=wc))
        return vs.mean() - vc.mean(), np.percentile(D, 5), np.percentile(D, 95)
    calme = lambda i: (CA[min(i + 61, n)] - CA[max(i - 60, 0)]) + (CV[min(i + 61, n)] - CV[max(i - 60, 0)]) == 0
    temoins = {pt: np.array([i for i in range(700, n - 121, 13) if part.get(stof(i)) == pt and G["ok"][i] and calme(i)]) for pt in PARTS}
    # 8.1
    w("### 8.1 Pression avant le début de chaque salve, contre des périodes sans liquidation\n")
    w("Variables connues à l'instant indiqué (avant le déclenchement). Signe aligné sur le sens forcé (témoins : sens au hasard) ; OI non signé.\n")
    VARS = (("OFI 5 s", lambda i: V["ofi5"][i], 1), ("Pression nette 5 s", lambda i: V["Pn5"][i], 1), ("Prix Binance 5 s ($)", lambda i: d5[i], 1),
            ("Mark − index Bybit ($)", lambda i: dby[i], 1), ("Mark − index Binance ($)", lambda i: dbn[i], 1), ("OI Bybit 10 s (%)", lambda i: oi10[i], 0))
    w("| Échantillon | Variable | Avant | Salves | Témoins | Salves − témoins (IC 90 %) |\n|---|---|---|---|---|---|")
    for pt in PARTS:
        Z = [z for z in sal if z["part"] == pt]; T = temoins[pt]
        if not Z or not len(T): continue
        TT = RNG.choice(T, min(len(T), 5 * len(Z)), replace=len(T) < 5 * len(Z)); sT = RNG.choice([-1, 1], len(TT))
        for nom, fv, sg in VARS:
            for k in (1, 3, 5, 10, 30):
                vs = [fv(z["i0"] - k) * (z["s"] if sg else 1) for z in Z]; gs = [z["st"] for z in Z]
                vc = [fv(i - k) * (s0 if sg else 1) for i, s0 in zip(TT, sT)]; gc = [stof(i) for i in TT]
                d, a, b = diff_ic(gs, vs, gc, vc)
                w(f"| {pt} | {nom} | {k} s | {cell(vs, gs)} | {cell(vc, gc)} | {d:+.3f} [{a:+.3f} ; {b:+.3f}] |")
    # 8.2
    w("\n### 8.2 Délais réels depuis la première liquidation (secondes)\n")
    w("Résolution : seconde pour les liquidations, 100 ms pour le carnet Polymarket. Médiane [10e ; 90e centile] (n).\n")
    q3 = lambda v: (f"{np.median(v):+.1f} [{np.percentile(v, 10):+.1f} ; {np.percentile(v, 90):+.1f}] (n={len(v)})" if len(v) else "—")
    w("| Échantillon | Salves | 1er avertissement | Déclenchement | Réaction BTC | Réaction Polymarket | 1re exécution possible | Polymarket avant nous |\n|---|---|---|---|---|---|---|---|")
    for pt in PARTS:
        Z = [z for z in sal if z["part"] == pt]
        if not Z: continue
        A_, Dc, Bt, Pm, Ex, avant = [], [], [], [], [], []
        for z in Z:
            i0, s0 = z["i0"], z["s"]; ref = G["t0"] + i0 - 1
            war = [j for j in range(i0 - 30, i0) if score.get(j, -1) >= thr]
            if war: A_.append(war[0] - i0 + 1)
            Dc.append(z["i"] - i0 + 1)
            for k in range(0, 61):
                if i0 + k < n and np.isfinite(bn[i0 + k]) and np.isfinite(bn[i0 - 1]) and (bn[i0 + k] - bn[i0 - 1]) * s0 >= max(5, 2 * vol[i0] * math.sqrt(k + 1)): Bt.append(k + 1); break
            ex = ((war[0] if war else z["i"]) + G["t0"] - ref) + 0.164; Ex.append(ex)
            if z["st"] in cyc and z["st"] + 300 - ref >= 1:
                X = "Up" if s0 > 0 else "Down"; tt = [ref * 1000 + 100 * j for j in range(201)]
                try: E = {k_: DP.compact(x) for k_, x in LH.Cycle(cyc[z["st"]]["f"]).etats(tt).items()}
                except Exception: E = {}
                v0 = DP.vend(E[tt[0]], X) if tt[0] in E else None
                if v0:
                    for t_ in tt[1:]:
                        vv = DP.vend(E[t_], X) if t_ in E else None
                        if vv and vv[0][0] - v0[0][0] >= 10: Pm.append((t_ - tt[0]) / 1000); avant.append((t_ - tt[0]) / 1000 < ex); break
        w(f"| {pt} | {len(Z)} | {q3(A_)} | {q3(Dc)} | {q3(Bt)} | {q3(Pm)} | {q3(Ex)} | {100 * np.mean(avant) if avant else float('nan'):.0f} % (n={len(avant)}) |")
    # 8.3
    w("\n### 8.3 Qualité et P&L net par latence (frais, quantité disponible, prix réellement accessible)\n")
    w("| Échantillon | Source | Latence | Exécutés / signaux | Parts moyennes | Prix payé moyen (frais compris) | Victoire | Avantage (IC 90 %) | P&L net total (IC 90 %) | P&L par signal exécuté (IC 90 %) |\n|---|---|---|---|---|---|---|---|---|---|")
    for (pt, src), R_ in RES.items():
        for ms in (164, 200, 250, 500):
            ex = [r for r in R_ if r[2][ms][2]]
            if not ex: w(f"| {pt} | {src} | {ms} ms | 0 / {len(R_)} | — | — | — | — | — | — |"); continue
            pn = np.array([r[2][ms][0] for r in ex]); g = np.array([r[0] for r in ex]); u = np.array([r[2][ms][1] for r in ex]); qq = np.array([r[2][ms][3] for r in ex])
            ct = L.ic_tot(g, pn) if len(ex) >= 3 else (np.nan, np.nan)
            w(f"| {pt} | {src} | {ms} ms | {len(ex)} / {len(R_)} | {qq.mean():.1f} | {u.mean():.3f} | {100 * np.mean([r[1] for r in ex]):.0f} % | "
              f"{cell([r[1] - uu for r, uu in zip(ex, u)], g)} | {pn.sum():+.1f} [{ct[0]:+.1f} ; {ct[1]:+.1f}] | {cell(pn, g)} |")
    # 8.4
    w("\n### 8.4 Bilan séparé\n")
    w("**Cascades anticipées, fausses alertes, manquées (H1000, seuil d'apprentissage inchangé)**\n")
    w("| Échantillon | Salves | Anticipées (≥ 1 avertissement 5–30 s avant) | Manquées | Signaux H1000 (dédoublonnés) | Fausses alertes | Précision | Rappel | Gain de temps médian (s) |\n|---|---|---|---|---|---|---|---|---|")
    for pt in PARTS:
        Z = [z for z in sal if z["part"] == pt]; S_ = [s_ for s_ in sig if s_["part"] == pt and s_["src"] == "H1000"]
        ant = [z for z in Z if any(score.get(j, -1) >= thr for j in range(z["i0"] - 30, z["i0"] - 4))]
        gain = [z["i"] - min(j for j in range(z["i0"] - 30, z["i0"] - 4) if score.get(j, -1) >= thr) for z in ant]
        fa = [s_ for s_ in S_ if not salve_dans(s_["i"], 5, 30)]
        w(f"| {pt} | {len(Z)} | {len(ant)} | {len(Z) - len(ant)} | {len(S_)} | {len(fa)} | {100 * (1 - len(fa) / len(S_)) if S_ else float('nan'):.0f} % | "
          f"{100 * len(ant) / len(Z) if Z else float('nan'):.0f} % | {np.median(gain) if gain else float('nan'):.0f} |")
    w("\n**Impact sur Chainlink et sur le TWAP final** (sens forcé, $ ; témoins = instants sans liquidation, sens au hasard)\n")
    w("| Échantillon | Mesure | Salves | Témoins | Différence (IC 90 %) |\n|---|---|---|---|---|")
    cl = G["cl"]
    def twap(st, i, s0):
        a = st + 240 - G["t0"]; b = st + 300 - G["t0"]
        if i >= a or b > n or not np.isfinite(cl[i]): return np.nan
        x = cl[a:b]; x = x[np.isfinite(x)]; return (x.mean() - cl[i]) * s0 if len(x) > 30 else np.nan
    for pt in PARTS:
        Z = [z for z in sal if z["part"] == pt]; T = temoins[pt]
        if not Z or not len(T): continue
        TT = RNG.choice(T, min(len(T), 5 * len(Z)), replace=len(T) < 5 * len(Z)); sT = RNG.choice([-1, 1], len(TT))
        gs = [z["st"] for z in Z]; gc = [stof(i) for i in TT]
        for lab, f_ in ((f"Chainlink {k} s", (lambda k: lambda i, s0, st: (cl[min(i + k, n - 1)] - cl[i]) * s0)(k)) for k in (5, 30, 60)):
            vs = [f_(z["i"], z["s"], z["st"]) for z in Z]; vc = [f_(i, s0, stof(i)) for i, s0 in zip(TT, sT)]; d, a, b = diff_ic(gs, vs, gc, vc)
            w(f"| {pt} | {lab} | {cell(vs, gs)} | {cell(vc, gc)} | {d:+.2f} [{a:+.2f} ; {b:+.2f}] |")
        vs = [twap(z["st"], z["i"], z["s"]) for z in Z]; vc = [twap(stof(i), i, s0) for i, s0 in zip(TT, sT)]; d, a, b = diff_ic(gs, vs, gc, vc)
        w(f"| {pt} | TWAP final − Chainlink au déclenchement | {cell(vs, gs)} | {cell(vc, gc)} | {d:+.2f} [{a:+.2f} ; {b:+.2f}] |")
    w("\n**P&L par signal, drawdown et pertes extrêmes** (ordre chronologique, mise 20 $)\n")
    w("| Échantillon | Source | Latence | Exécutés | P&L par signal (IC 90 %) | P&L total | Drawdown max | Pire perte | Moyenne des 5 % pires | Pertes consécutives max |\n|---|---|---|---|---|---|---|---|---|---|")
    for (pt, src), R_ in RES.items():
        for ms in (164, 200, 250, 500):
            ex = sorted([r for r in R_ if r[2][ms][2]], key=lambda r: r[3])
            if not ex: continue
            pn = np.array([r[2][ms][0] for r in ex]); cum = np.cumsum(pn); dd = float(np.max(np.maximum.accumulate(np.concatenate([[0], cum]))[1:] - cum))
            k5 = max(1, int(math.ceil(0.05 * len(pn)))); run = mx = 0
            for x in pn: run = run + 1 if x < 0 else 0; mx = max(mx, run)
            w(f"| {pt} | {src} | {ms} ms | {len(ex)} | {cell(pn, [r[0] for r in ex])} | {pn.sum():+.1f} | {dd:.1f} | {pn.min():+.1f} | {np.sort(pn)[:k5].mean():+.1f} | {mx} |")
    w("\n## Limites\n- Niveaux réels de liquidation inconnus (carte = scénarios). Binance forceOrder : au plus une liquidation par seconde (échantillonné).\n"
      "- Open interest Bybit publié à la cadence du ticker ; pas d'interpolation de valeurs futures.\n")
    w(f"_Calcul : {time.time() - t_go:.0f} s._\n")
    open(SORTIE, "w").write("\n".join(o)); print("\n".join(o))


if __name__ == "__main__":
    main()
