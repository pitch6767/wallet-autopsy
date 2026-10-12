"""BOT95 — H976 / H977 / H978 (Pitch, 12.10.2026 15:02). PROTOCOLE PRÉ-ENREGISTRÉ (ce fichier tel que committé avant le calcul).
Hors ligne ; aucun ordre ; aucun bot, H816, H821, R4 ni fantôme modifié ; période réservée (≥ 13.10.2026) jamais lue.

ÉCHANTILLONS (Dublin) : apprentissage / validation / test comme H971 et H941 (test = 12.10 06:00–12:00 UTC, déjà consulté pour H941) ;
  NOUVEAU = cycles commençant le 12.10 à 12:00 UTC ou après (jamais utilisés). Les règles et coefficients sont appris sur l'apprentissage seul.
H977 EARLY FLOW SETTLEMENT EDGE : définition H941 inchangée (vague = z(pression nette 5 s) ≥ 1,5, au plus une par 5 s et par sens) ;
  fenêtre 150–240 s restantes ; une décision par cycle = la première vague de la fenêtre ; côté X = sens de la vague.
  A = probabilité de règlement M0 recalibrée (apprentissage, décisions toutes les 10 s) ; B = probabilité implicite Polymarket = milieu du jeton X ;
  C = A + effet H941 : logit(C_X) = logit(A_X) + δ, δ appris sur les vagues de l'apprentissage (logistique à décalage seul).
  Mesures : Brier et log loss de A, B, C (pour le côté X) ; calibration ; avantage face au marché = résultat − (prix vendeur + frais) ;
  achat 20 $ du jeton X à 164 ms au prix vendeur vu (frais compris) selon trois règles : R0 toujours ; R1 si C_X − prix − frais ≥ 0 ;
  R2 si C_X − prix − frais ≥ 0,05 ; conservation jusqu'au résultat officiel. Sensibilité latence 300 / 500 ms. Sous-ensemble proche de 50 % :
  A entre 0,35 et 0,65 (défini avant le résultat). IC 90 % par cycles.
  QUESTION DÉCISIVE : moyenne de (résultat − prix payé − frais) pour R0 > 0 avec IC > 0 sur la validation, le test ET le nouvel échantillon ?
H976 QUOTE RELOCATION : retrait fort = baisse de profondeur non expliquée par les transactions (Binance spot et Bybit perp) au-dessus du 95e centile
  de l'apprentissage ; synchronisé = les deux places du même côté dans la même seconde. Classement de chaque retrait vendeur synchronisé sur les
  2 s suivantes : « déplacement » (meilleur vendeur Binance plus bas ET ajouts vendeurs > 0), « consommation » (achats agressifs ≥ baisse),
  « annulation » (autre). Mouvement BTC à 1/3/5/10/30 s par classe (symétrique pour les acheteurs, signé).
  Apport marginal (prévision du signe à 10 s et 30 s) : A = OFI + momentum + volatilité ; B = A + indicateurs de retraits synchronisés ;
  C = B + déplacement (variation du meilleur vendeur / acheteur sur 2 s des deux places, ajouts sur 2 s) ; D = témoins non synchronisés.
  AUC et ΔAUC sur validation, test et nouveau, IC corrigé (Bonferroni 2 cibles × 2 comparaisons × 3 échantillons = 12).
H978 CROSS-ASSET EARLY WARNING : (a) 30 jours Binance 1 s (BTC, ETH, SOL) : vagues BTC (même définition, volume agressif des bougies 1 s) ;
  avance = l'actif a-t-il bougé dans le même sens dans les k s AVANT la vague (k = 1, 2, 5, 10) plus souvent qu'au hasard ; apport marginal pour
  prévoir une vague BTC dans les 5 s (AUC BTC seul contre BTC + ETH/SOL, apprentissage < 02.10, test 02.10 → 11.10) ;
  (b) Dublin : OKX, Coinbase, perp Bybit avant les vagues BTC (heures de réception). Nasdaq, or, devises, CME : non disponibles à la seconde.
Usage : python3 etude/bot5min/flux_h977.py dossier_cycles_dublin dossier_btc"""
import os, sys, math, time, json, gzip, glob, collections
import numpy as np, pandas as pd

ICI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, ICI)
import latence_h766 as LH, liquidite_h833 as L, dpe_h841 as DP, pression_h971 as PR
RESERVE = 1791849600; TEST_DEB = 1791784800; NOUV_DEB = 1791806400; COUPE_BIN = 1790899200
SORTIE = os.path.join(ICI, "resultat_flux_h977.md"); MISE = 20.0; RNG = np.random.default_rng(977)
fee = lambda p: 0.07 * p * (1 - p); lg = L.lg


def cell(v, g, pct=False):
    v = np.asarray(v, float); g = np.asarray(g); m = np.isfinite(v)
    if m.sum() < 5: return f"— (n={int(m.sum())})"
    c = L.ic_g(g[m], v[m]); k = 100 if pct else 1
    return f"{k * v[m].mean():+.2f} [{k * c[0]:+.2f} ; {k * c[1]:+.2f}]"


def main():
    t_go = time.time(); o = []; w = o.append
    G, cyc = L.grille(sys.argv[1]); P = L.preparer(G); L.P_sd1 = P["sd1"]; Y = L.resultats_officiels(cyc); V = PR.grandeurs(G, P)
    cycles = sorted(s for s in cyc if s < RESERVE); avant = [s for s in cycles if s < TEST_DEB]; n_tr = len(avant) * 2 // 3
    part = {s: ("apprentissage" if k < n_tr else "validation") for k, s in enumerate(avant)}
    part.update({s: ("test" if s < NOUV_DEB else "nouveau") for s in cycles if s >= TEST_DEB})
    PARTS = ["apprentissage", "validation", "test", "nouveau"]; nb = collections.Counter(part.values())
    stof = lambda i: (G["t0"] + i) - (G["t0"] + i) % 300; bn = G["bn"]; sd5 = P["sd5"]
    w("# Bot95 — H976 / H977 / H978 : flux de début de cycle face au prix Polymarket, déplacement de cotations, alerte multi-actifs\n")
    w(f"Généré le {time.strftime('%d.%m.%Y %H:%M', time.gmtime())} UTC. Cycles Dublin : " + ", ".join(f"{k} {nb[k]}" for k in PARTS) +
      " (test = 12.10 06:00–12:00 UTC, déjà consulté pour H941 ; nouveau = à partir du 12.10 12:00 UTC). Résultats officiels. Aucun ordre ; période réservée non lue.\n")

    # ================= H977
    # probabilité A recalibrée (apprentissage)
    Xc, yc = [], []
    for st in [s for s in cycles if part[s] == "apprentissage" and s in Y]:
        for r in range(290, 10, -10):
            m = L.m0(G, cyc, st, r)
            if m: Xc.append([lg(m[0])]); yc.append(Y[st])
    bA = L.ajuster(np.array(Xc), np.array(yc), 0.1)
    pA = lambda p0: float(L.predire(bA, np.array([[lg(p0)]]))[0])
    vag = []; last = {1: -99, -1: -99}
    for i in range(700, G["n"] - 31):
        st = stof(i)
        if st not in part or not G["ok"][i] or not np.isfinite(V["zPn5"][i]): continue
        z = V["zPn5"][i]
        if abs(z) < 1.5: continue
        s = 1 if z > 0 else -1
        if i - last[s] < 5: continue
        last[s] = i
        rest = st + 300 - (G["t0"] + i)
        if 150 <= rest <= 240: vag.append(dict(i=i, st=st, s=s, rest=rest, z=z))
    prem = {}
    for v in vag:
        if v["st"] not in prem: prem[v["st"]] = v
    D = []
    for st, v in sorted(prem.items()):
        if st not in Y: continue
        m = L.m0(G, cyc, st, v["rest"])
        if not m: continue
        X = "Up" if v["s"] > 0 else "Down"; aU = pA(m[0]); aX = aU if X == "Up" else 1 - aU
        yX = Y[st] if X == "Up" else 1 - Y[st]
        D.append(dict(st=st, i=v["i"], X=X, aX=aX, p0=m[0], yX=yX, part=part[st], rest=v["rest"], t=(G["t0"] + v["i"]) * 1000))
    # carnet Polymarket aux instants des décisions
    for d in D:
        cy = LH.Cycle(cyc[d["st"]]["f"]); T = [d["t"]] + [d["t"] + ms for ms in (164, 300, 500)]
        E = {k: DP.compact(x) for k, x in cy.etats(T).items()}; Lo = E[d["t"]]
        v = DP.vend(Lo, d["X"]); b = DP.ach(Lo, d["X"])
        d["ask"] = v[0][0] / 1000 if v else np.nan; d["mid"] = ((v[0][0] + b[0][0]) / 2000) if (v and b) else np.nan
        d["prof"] = sum(sz for px, sz in v if px <= v[0][0] + 20) if v else 0
        for ms in (164, 300, 500):
            q = c = 0.0
            if v:
                for px, sz in DP.vend(E[d["t"] + ms], d["X"]):
                    if px > v[0][0]: break
                    if px <= 0 or px >= 1000: continue
                    pp = px / 1000; u = pp + fee(pp); k = min(sz, (MISE - c) / u)
                    if k <= 1e-9: break
                    q += k; c += k * u
            d[f"pnl{ms}"] = (q * d["yX"] - c) if q > 0 else np.nan; d[f"cout{ms}"] = (c / q) if q > 0 else np.nan
    tr = [d for d in D if d["part"] == "apprentissage"]
    # δ appris sur l'apprentissage (décalage seul)
    best, dl = 1e9, 0.0
    for de in np.arange(-1.5, 1.51, 0.01):
        ll_ = np.mean([-(d["yX"] * math.log(1 / (1 + math.exp(-(lg(d["aX"]) + de)))) + (1 - d["yX"]) * math.log(1 - 1 / (1 + math.exp(-(lg(d["aX"]) + de))))) for d in tr]) if tr else 0
        if ll_ < best: best, dl = ll_, de
    for d in D: d["cX"] = 1 / (1 + math.exp(-(lg(d["aX"]) + dl)))
    w("## 1. H977 — Le flux de début de cycle crée-t-il une sous-évaluation réelle des billets Polymarket ?\n")
    w(f"Une décision par cycle : la première vague forte entre 150 et 240 s restantes, côté X = sens du flux. δ appris sur l'apprentissage = {dl:+.2f} (logit).\n")
    w("**Qualité des probabilités pour le côté X** (Brier, log loss ; plus bas = mieux)\n")
    w("| Échantillon | Décisions | Victoire X | A règlement seul | B prix Polymarket (milieu) | C règlement + effet H941 | B − A (Brier, IC 90 %) | B − C (Brier, IC 90 %) |\n|---|---|---|---|---|---|---|---|")
    for pt in PARTS:
        Z = [d for d in D if d["part"] == pt and np.isfinite(d["mid"])]
        if len(Z) < 5: w(f"| {pt} | {len(Z)} | — | — | — | — | — | — |"); continue
        y = np.array([d["yX"] for d in Z]); g = [d["st"] for d in Z]
        a = np.array([d["aX"] for d in Z]); b = np.array([d["mid"] for d in Z]); c = np.array([d["cX"] for d in Z])
        bA_, bB_, bC_ = L.brier(a, y), L.brier(b, y), L.brier(c, y)
        w(f"| {pt} | {len(Z)} | {100 * y.mean():.0f} % | {bA_.mean():.3f} / {L.ll(a, y).mean():.3f} | {bB_.mean():.3f} / {L.ll(b, y).mean():.3f} | {bC_.mean():.3f} / {L.ll(c, y).mean():.3f} | "
          f"{cell(bB_ - bA_, g)} | {cell(bB_ - bC_, g)} |")
    w("\n**Avantage face au marché et P&L** (achat 20 $ du jeton X à 164 ms au prix vendeur vu, frais compris, conservation, résultat officiel)\n")
    w("| Échantillon | Règle | Achats | Victoire | Prix payé moyen | Avantage par achat (résultat − prix − frais, IC 90 %) | P&L ($) | IC 90 % total | Gagnants / perdants | Jackpots (≥ +20 $) | Drawdown |\n|---|---|---|---|---|---|---|---|---|---|---|")
    for pt in PARTS:
        for reg, f in (("R0 toujours", lambda d: True), ("R1 C − prix ≥ 0", lambda d: d["cX"] - d["ask"] - fee(d["ask"]) >= 0), ("R2 C − prix ≥ 0,05", lambda d: d["cX"] - d["ask"] - fee(d["ask"]) >= 0.05)):
            Z = [d for d in D if d["part"] == pt and np.isfinite(d["pnl164"]) and np.isfinite(d["ask"]) and f(d)]
            if not Z: w(f"| {pt} | {reg} | 0 | — | — | — | — | — | — | — | — |"); continue
            g = np.array([d["st"] for d in Z]); pn = np.array([d["pnl164"] for d in Z]); av = np.array([d["yX"] - d["cout164"] for d in Z])
            ci = L.ic_tot(g, pn) if len(Z) >= 3 else (np.nan, np.nan)
            cum = np.cumsum(pn); dd = float(np.max(np.maximum.accumulate(np.concatenate([[0], cum]))[1:] - cum))
            w(f"| {pt} | {reg} | {len(Z)} | {100 * np.mean([d['yX'] for d in Z]):.0f} % | {np.mean([d['cout164'] for d in Z]):.3f} | {cell(av, g)} | {pn.sum():+.0f} | [{ci[0]:+.0f} ; {ci[1]:+.0f}] | "
              f"{int((pn > 0).sum())} / {int((pn < 0).sum())} | {int((pn >= 20).sum())} | {dd:.0f} |")
    w("\n**Sensibilité à la latence (R0)** et **proches de 50 %** (A entre 0,35 et 0,65)\n")
    w("| Échantillon | P&L R0 à 164 / 300 / 500 ms ($) | Proches de 50 % : achats, victoire, avantage par achat |\n|---|---|---|")
    for pt in PARTS:
        Z = [d for d in D if d["part"] == pt]
        lat = " / ".join(f"{np.nansum([d[f'pnl{ms}'] for d in Z]):+.0f}" for ms in (164, 300, 500))
        M = [d for d in Z if 0.35 <= d["aX"] <= 0.65 and np.isfinite(d["pnl164"])]
        w(f"| {pt} | {lat} | {len(M)}, {100 * np.mean([d['yX'] for d in M]) if M else float('nan'):.0f} %, {cell([d['yX'] - d['cout164'] for d in M], [d['st'] for d in M])} |")
    w("\n**Calibration (toutes périodes hors apprentissage)** : victoire observée selon le prix Polymarket payé\n")
    w("| Prix vendeur du jeton X | Achats | Victoire observée | Prix moyen |\n|---|---|---|---|")
    Z = [d for d in D if d["part"] != "apprentissage" and np.isfinite(d["ask"])]
    for lo, hi in ((0, .3), (.3, .5), (.5, .7), (.7, .9), (.9, 1.01)):
        M = [d for d in Z if lo <= d["ask"] < hi]
        if M: w(f"| {lo:.1f}–{min(hi, 1):.1f} | {len(M)} | {100 * np.mean([d['yX'] for d in M]):.0f} % | {np.mean([d['ask'] for d in M]):.2f} |")

    # ================= H976
    w("\n## 2. H976 — Déplacement de cotations derrière les retraits synchronisés\n")
    by = {k: np.zeros(G["n"]) for k in ("dec_a", "dec_b", "add_a", "add_b")}; bya = np.full(G["n"], np.nan); byb = np.full(G["n"], np.nan)
    for st in cycles:
        try: R = json.load(gzip.open(cyc[st]["f"]))
        except Exception: continue
        for r in (R.get("ob") or {}).get("by", []):
            i = int(math.ceil(r[0] / 1000)) - G["t0"]
            if 0 <= i < G["n"] and len(r) > 17:
                by["dec_b"][i] += r[14]; by["dec_a"][i] += r[15]; by["add_b"][i] += r[16]; by["add_a"][i] += r[17]; byb[i] = r[2]; bya[i] = r[3]
    bya = pd.Series(bya).ffill(limit=5).values; byb = pd.Series(byb).ffill(limit=5).values
    Wbn = {"a": np.nan_to_num(G["dec_a"]) - np.nan_to_num(G["agb"]), "b": np.nan_to_num(G["dec_b"]) - np.nan_to_num(G["ags"])}
    Wby = {"a": by["dec_a"] - np.nan_to_num(G["agb_by"]), "b": by["dec_b"] - np.nan_to_num(G["ags_by"])}
    trI = np.array([part.get(stof(i)) == "apprentissage" and G["ok"][i] for i in range(G["n"])])
    seuil = {(pl, sd): np.percentile(W[sd][trI], 95) for pl, W in (("bn", Wbn), ("by", Wby)) for sd in ("a", "b")}
    ev = []
    for i in range(700, G["n"] - 31):
        st = stof(i)
        if st not in part or not (G["ok"][i] and G["ok"][i + 30]): continue
        for sd, s in (("a", -1), ("b", 1)):           # retrait vendeur → baisse attendue (signe observé en H956)
            f1 = Wbn[sd][i] > seuil[("bn", sd)]; f2 = Wby[sd][i] > seuil[("by", sd)]
            if not (f1 and f2): continue
            if sd == "a":
                dep = np.isfinite(G["ask"][i + 2]) and G["ask"][i + 2] < G["ask"][i] and G["add_a"][i + 1:i + 3].sum() > 0
                cons = np.nan_to_num(G["agb"][i]) >= np.nan_to_num(G["dec_a"][i])
            else:
                dep = np.isfinite(G["bid"][i + 2]) and G["bid"][i + 2] > G["bid"][i] and G["add_b"][i + 1:i + 3].sum() > 0
                cons = np.nan_to_num(G["ags"][i]) >= np.nan_to_num(G["dec_b"][i])
            cl = "consommation" if cons else ("déplacement" if dep else "annulation")
            ev.append(dict(i=i, st=st, part=part[st], cl=cl, y={h: (bn[i + h] - bn[i]) * s for h in (1, 3, 5, 10, 30)},
                           y2={h: (bn[i + 2 + h] - bn[i + 2]) * s for h in (5, 10)}))
    w("Mouvement BTC signé dans le sens observé en H956 (retrait vendeur → baisse), en $, à partir de la seconde du retrait ; puis à partir de t + 2 s (après le classement).\n")
    w("| Échantillon | Classe | Événements | 1 s | 3 s | 5 s | 10 s | 30 s | 5 s après t+2 | 10 s après t+2 |\n|---|---|---|---|---|---|---|---|---|---|")
    for pt in PARTS:
        for cl in ("déplacement", "annulation", "consommation"):
            Z = [e for e in ev if e["part"] == pt and e["cl"] == cl]
            if not Z: continue
            g = [e["st"] for e in Z]
            w(f"| {pt} | {cl} | {len(Z)} | " + " | ".join(cell([e["y"][h] for e in Z], g) for h in (1, 3, 5, 10, 30)) + " | " +
              " | ".join(cell([e["y2"][h] for e in Z], g) for h in (5, 10)) + " |")
    # apport marginal
    I = [i for i in range(700, G["n"] - 32, 3) if stof(i) in part and G["ok"][i] and G["ok"][i + 30] and np.isfinite(G["bid"][i]) and np.isfinite(P["sd1"][i]) and np.isfinite(bya[i])]
    s1 = lambda i: P["sd1"][i]
    XA = np.nan_to_num(np.array([[V["ofi1"][i], V["ofi5"][i], (bn[i] - bn[i - 1]) / s1(i), (bn[i] - bn[i - 5]) / s1(i), (bn[i] - bn[i - 30]) / s1(i), s1(i)] for i in I]))
    XB = np.array([[float(Wbn["a"][i] > seuil[("bn", "a")] and Wby["a"][i] > seuil[("by", "a")]), float(Wbn["b"][i] > seuil[("bn", "b")] and Wby["b"][i] > seuil[("by", "b")]),
                    Wbn["a"][i], Wby["a"][i], Wbn["b"][i], Wby["b"][i]] for i in I])
    XC = np.nan_to_num(np.array([[(G["ask"][i] - G["ask"][i - 2]) / s1(i), (G["bid"][i] - G["bid"][i - 2]) / s1(i), (bya[i] - bya[i - 2]) / s1(i), (byb[i] - byb[i - 2]) / s1(i),
                                  G["add_a"][i - 1:i + 1].sum(), G["add_b"][i - 1:i + 1].sum(), by["add_a"][i - 1:i + 1].sum(), by["add_b"][i - 1:i + 1].sum()] for i in I]))
    ptI = np.array([part[stof(i)] for i in I]); gI = np.array([stof(i) for i in I]); trm = ptI == "apprentissage"
    w("\n**Apport marginal pour prévoir le signe du mouvement BTC** (AUC ; IC corrigé pour 12 comparaisons)\n")
    w("| Cible | Échantillon | AUC A (OFI, momentum, volatilité) | AUC B (+ retraits synchronisés) | AUC C (+ déplacement) | B − A (IC corrigé) | C − B (IC corrigé) |\n|---|---|---|---|---|---|---|")
    for nom, h in (("hausse à 10 s", 10), ("hausse à 30 s", 30)):
        y = np.array([bn[i + h] > bn[i] for i in I], float); pr = {}
        for lab, X in (("A", XA), ("B", np.column_stack([XA, XB])), ("C", np.column_stack([XA, XB, XC]))):
            mu, sd = X[trm].mean(0), X[trm].std(0) + 1e-9; b = L.ajuster((X[trm] - mu) / sd, y[trm], 2.0); pr[lab] = L.predire(b, (X - mu) / sd)
        for pt in ("validation", "test", "nouveau"):
            m = ptI == pt
            if m.sum() < 100: continue
            yt = y[m]; g = gI[m]; Ug = np.unique(g); D1, D2 = [], []
            for _ in range(400):
                mm = np.isin(g, RNG.choice(Ug, len(Ug)))
                if yt[mm].min() != yt[mm].max():
                    a_, b_, c_ = (L.auc(pr[k][m][mm], yt[mm]) for k in ("A", "B", "C")); D1.append(b_ - a_); D2.append(c_ - b_)
            A_, B_, C_ = (L.auc(pr[k][m], yt) for k in ("A", "B", "C"))
            q = lambda D: f"{np.percentile(D, 50):+.3f} [{np.percentile(D, 0.42):+.3f} ; {np.percentile(D, 99.58):+.3f}]"
            w(f"| {nom} | {pt} | {A_:.3f} | {B_:.3f} | {C_:.3f} | {q(D1)} | {q(D2)} |")

    # ================= H978
    w("\n## 3. H978 — Un autre actif précède-t-il les vagues BTC ?\n")
    def charger1s(d, cols=("t", "c", "v", "vb")):
        fs = sorted(glob.glob(os.path.join(d, "*.csv.gz"))); Dd = pd.concat([pd.read_csv(f, usecols=list(cols)) for f in fs]).drop_duplicates("t").sort_values("t")
        return Dd[Dd.t < RESERVE].set_index("t")
    B_ = charger1s(os.path.join(sys.argv[2], "btc1s")); Ee = charger1s(os.path.join(sys.argv[2], "autres", "ETHUSDT")); Ss = charger1s(os.path.join(sys.argv[2], "autres", "SOLUSDT"))
    df = pd.DataFrame({"b": B_["c"], "bf": 2 * B_["vb"] - B_["v"], "e": Ee["c"], "ef": 2 * Ee["vb"] - Ee["v"], "s": Ss["c"], "sf": 2 * Ss["vb"] - Ss["v"]}).dropna()
    tt = df.index.values; bf5 = df["bf"].rolling(5).sum(); zb = ((bf5 - bf5.rolling(600, min_periods=200).mean().shift(1)) / bf5.rolling(600, min_periods=200).std().shift(1)).values
    lr = {k: np.log(df[k]).values for k in ("b", "e", "s")}
    wv = []; lastw = -99
    for i in np.flatnonzero(np.abs(np.nan_to_num(zb)) >= 1.5):
        if i - lastw < 5 or i < 700: continue
        lastw = i; wv.append((i, 1 if zb[i] > 0 else -1))
    wv = np.array(wv); idx = wv[:, 0]; sg = wv[:, 1]
    rnd = RNG.integers(700, len(tt) - 11, len(idx)); sgr = RNG.choice([-1, 1], len(idx))
    trW = tt[idx] < COUPE_BIN
    w(f"**(a) Binance 1 s, 30 jours** : {len(idx)} vagues BTC. Part des vagues où l'actif a déjà bougé dans le même sens dans les k s avant le début de la vague "
      "(fenêtre de 5 s de la vague exclue), comparée à des instants tirés au hasard.\n")
    w("| Actif | k | Vagues (test) : même sens avant | Hasard | Écart (IC 90 % par jours) |\n|---|---|---|---|---|")
    for a in ("e", "s"):
        for k in (1, 2, 5, 10):
            def prec(ix, sgn): j0 = ix - 5; return (lr[a][j0] - lr[a][j0 - k]) * sgn > 0
            te = ~trW; v1 = prec(idx[te], sg[te]).astype(float); v0 = prec(rnd[te], sgr[te]).astype(float)
            days = (tt[idx[te]] // 86400); U = np.unique(days); dif = []
            for _ in range(1000):
                bs = RNG.choice(U, len(U)); mm = np.isin(days, bs); dif.append(v1[mm].mean() - v0.mean())
            w(f"| {'ETH' if a == 'e' else 'SOL'} | {k} s | {100 * v1.mean():.1f} % | {100 * v0.mean():.1f} % | {100 * (v1.mean() - v0.mean()):+.1f} pts [{100 * np.percentile(dif, 5):+.1f} ; {100 * np.percentile(dif, 95):+.1f}] |")
    # apport marginal : prévoir le sens de la vague BTC à partir des 10 s précédant la vague (BTC seul contre + ETH/SOL)
    X1 = np.column_stack([lr["b"][idx - 5] - lr["b"][idx - 6], lr["b"][idx - 5] - lr["b"][idx - 15], df["bf"].rolling(10).sum().values[idx - 5]])
    X2 = np.column_stack([X1, lr["e"][idx - 5] - lr["e"][idx - 6], lr["e"][idx - 5] - lr["e"][idx - 15], df["ef"].rolling(10).sum().values[idx - 5],
                          lr["s"][idx - 5] - lr["s"][idx - 6], lr["s"][idx - 5] - lr["s"][idx - 15], df["sf"].rolling(10).sum().values[idx - 5]])
    yv = (sg > 0).astype(float); X1 = np.nan_to_num(X1); X2 = np.nan_to_num(X2); res = {}
    for lab, X in (("BTC", X1), ("+ETH/SOL", X2)):
        mu, sd = X[trW].mean(0), X[trW].std(0) + 1e-9; b = L.ajuster((X[trW] - mu) / sd, yv[trW], 2.0); res[lab] = L.predire(b, (X - mu) / sd)
    te = ~trW; days = tt[idx[te]] // 86400; U = np.unique(days); dd_ = []
    for _ in range(400):
        mm = np.isin(days, RNG.choice(U, len(U))); dd_.append(L.auc(res["+ETH/SOL"][te][mm], yv[te][mm]) - L.auc(res["BTC"][te][mm], yv[te][mm]))
    w(f"\nPrévoir le **sens** d'une vague BTC avec les données arrêtées 5 s avant son début (test 02.10 → 11.10) : AUC BTC seul {L.auc(res['BTC'][te], yv[te]):.3f}, "
      f"avec ETH/SOL {L.auc(res['+ETH/SOL'][te], yv[te]):.3f}, écart {np.percentile(dd_, 50):+.3f} [{np.percentile(dd_, 5):+.3f} ; {np.percentile(dd_, 95):+.3f}].\n")
    # (b) Dublin : autres places avant les vagues BTC
    w("**(b) Dublin (heures de réception)** : mouvement des autres places dans les 2 s avant les vagues de début de cycle (signé dans le sens de la vague, en $), "
      "comparé à Binance spot sur la même fenêtre.\n")
    w("| Échantillon | Vagues | Binance spot | Perp Bybit | OKX | Coinbase | Chainlink |\n|---|---|---|---|---|---|---|")
    for pt in PARTS:
        Z = [v for v in vag if part.get(v["st"]) == pt]
        if not Z: continue
        g = [v["st"] for v in Z]
        cells = [cell([(G[k][v["i"] - 1] - G[k][v["i"] - 3]) * v["s"] for v in Z], g) for k in ("bn", "perp", "okx", "cb", "cl")]
        w(f"| {pt} | {len(Z)} | " + " | ".join(cells) + " |")
    w("\nNasdaq, or, devises, CME : non disponibles à la seconde. ETH et SOL ne sont pas enregistrés à Dublin : effet sur le règlement Polymarket et "
      "exécution non mesurables pour eux. Deribit enregistré depuis le 12.10 11:55 UTC seulement.\n")
    w("## Limites\n- Échantillon « nouveau » de quelques dizaines de cycles seulement. Test déjà consulté pour H941.\n"
      "- Une décision par cycle pour H977 : faible nombre de décisions par échantillon.\n")
    w(f"_Calcul : {time.time() - t_go:.0f} s._\n")
    open(SORTIE, "w").write("\n".join(o)); print("\n".join(o))


if __name__ == "__main__":
    main()
