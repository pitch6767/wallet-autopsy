"""BOT95 — FUSION ENGINE F1, priorité 1 : H971 PRESSURE VS CAPACITY et H972 LIQUIDITY CAPACITY COLLAPSE (Pitch, 12.10.2026 14:13).
PROTOCOLE PRÉ-ENREGISTRÉ (ce fichier tel que committé avant le calcul de validation et de test). Hors ligne ; aucun ordre ; aucun bot actif,
H816, H821, R4 ni fantôme modifié ; période réservée (≥ 13.10.2026) jamais lue.

DONNÉES : cycles Dublin (< 13.10) : carnet Binance spot toutes les 100 ms (cumuls à 5/10/20 $, baisses et ajouts de quantité), transactions
  Binance spot et Bybit perp avec côté agresseur, prix des places, Chainlink, carnet Polymarket Up (Down = miroir). Résultat officiel.
DÉCOUPAGE (identique au DPE) : test INÉDIT = cycles ≥ 12.10.2026 06:00 UTC ; avant : apprentissage 2/3, validation 1/3.
GRANDEURS (seconde t, messages reçus avant t, unités en BTC) :
  pression nette Pn(w) = achats agressifs − ventes agressives (Binance spot + Bybit perp) sur w s ;
  capacité côté vendeur Ca(w) = profondeur vendeuse à 20 $ + ajouts vendeurs sur w s ; côté acheteur Cb(w) symétrique ;
  retraits vendeurs Wa(w) = baisses vendeuses − achats agressifs Binance sur w s (annulations estimées) ; Wb symétrique ;
  indice pression/capacité PCI(w) = Pn / (Ca si Pn > 0, sinon Cb), puis z-score sur les 600 s précédentes (unités et volatilité neutralisées) ;
  rechargement ρa = ajouts vendeurs 5 s / médiane des ajouts vendeurs 5 s sur les 300 s précédentes (ρb symétrique).
H972 EFFONDREMENT DE CAPACITÉ (haussier ; baissier symétrique), au plus un événement par 10 s :
  z(Pn 5 s) ≥ 1,5 ; profondeur vendeuse à 20 $ ≤ 70 % de celle d'il y a 5 s ; ρa ≤ 0,5 ; microprix > milieu ;
  hausse du prix Binance sur 5 s ≤ 0,5 σ5 (le spot n'a pas encore fait le mouvement).
  Témoin : même z(Pn 5 s) ≥ 1,5 sans les autres conditions.
  Mesures : mouvement BTC signé à 1/3/5/10/30/60 s ; réévaluation Polymarket (milieu du jeton prévu à +1/3/5/10/30 s, en c) ;
  effet sur le règlement officiel (résultat − M0 au même instant, signé) ; occasion exécutable : achat 20 $ du jeton prévu à t + 164 ms au prix
  vendeur vu à t, (a) revendu 30 s plus tard au meilleur acheteur (frais compris), (b) conservé jusqu'au règlement. IC 90 % par cycles.
H971 PRÉVISION : régression logistique, cibles = hausse BTC à 10 s, hausse à 30 s, grand mouvement à 30 s (|Δ| > 1,5 σ30) vers le haut / vers le bas,
  hausse du milieu Polymarket Up de ≥ 1 c à 10 s. Modèle simple S = OFI 1/5 s + momentum 1/5/30 s + volatilité ; modèle S + PC = S + PCI 5/30 s,
  ρa, ρb, retraits Wa/Wb 5 s, variation des profondeurs à 20 $ sur 5 s, microprix − milieu. Appris sur l'apprentissage ; AUC et ΔAUC sur la
  validation et le test, IC 90 % par cycles, correction de Bonferroni (5 cibles × 2 échantillons = 10).
  Règlement : modèle A (M0 recalibré) contre A + PC, décisions à 240/180/120/90/60/30 s ; Brier, log loss, précision ; tous, proches de 50 %,
  marge faible ; IC corrigé.
CRITÈRE : PC « apporte une information » si ΔAUC > 0 avec IC corrigé > 0 sur la validation ET le test ; « effondrement » utile si le mouvement
  signé à 10 s a un IC > 0 sur la validation ET le test ; « exécutable » seulement si le P&L (a) ou (b) a un IC par cycles > 0 sur le test.
Usage : python3 etude/bot5min/pression_h971.py dossier_cycles_dublin [--controle]  (--controle = apprentissage et validation seulement)"""
import os, sys, math, time, collections
import numpy as np, pandas as pd

ICI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, ICI)
import latence_h766 as LH, liquidite_h833 as L, dpe_h841 as DP
CONTROLE = "--controle" in sys.argv; RESERVE = 1791849600; TEST_DEB = 1791784800
SORTIE = os.path.join(ICI, "resultat_pression_h971" + ("_controle" if CONTROLE else "") + ".md")
EXEC = 164; MISE = 20.0; HZ = (1, 3, 5, 10, 30, 60); HP = (1, 3, 5, 10, 30); RNG = np.random.default_rng(971)
fee = lambda p: 0.07 * p * (1 - p)


def zroll(x, w=600):
    s = pd.Series(x); m = s.rolling(w, min_periods=w // 3).mean().shift(1); sd = s.rolling(w, min_periods=w // 3).std().shift(1)
    return ((s - m) / sd).values


def medroll(x, w=300):
    return pd.Series(x).rolling(w, min_periods=w // 3).median().shift(1).values


def grandeurs(G, P):
    n = G["n"]; c = lambda k: np.concatenate([[0], np.cumsum(np.nan_to_num(G[k]))])
    C = {k: c(k) for k in ("agb", "ags", "agb_by", "ags_by", "add_a", "add_b", "dec_a", "dec_b", "ofi")}
    win = lambda k, w: np.array([C[k][i + 1] - C[k][max(i + 1 - w, 0)] for i in range(n)])
    V = {}
    for w in (5, 30):
        Pn = (win("agb", w) - win("ags", w)) + (win("agb_by", w) - win("ags_by", w))
        Ca = np.nan_to_num(G["ca20"]) + win("add_a", w); Cb = np.nan_to_num(G["cb20"]) + win("add_b", w)
        V[f"Pn{w}"] = Pn; V[f"PCI{w}"] = zroll(np.where(Pn > 0, Pn / np.maximum(Ca, 1e-6), Pn / np.maximum(Cb, 1e-6)))
    V["zPn5"] = zroll(V["Pn5"])
    a5, b5 = win("add_a", 5), win("add_b", 5)
    V["rho_a"] = a5 / np.maximum(medroll(a5), 1e-6); V["rho_b"] = b5 / np.maximum(medroll(b5), 1e-6)
    V["Wa"] = win("dec_a", 5) - win("agb", 5); V["Wb"] = win("dec_b", 5) - win("ags", 5)
    ca, cb = G["ca20"], G["cb20"]
    V["dCa"] = ca - np.concatenate([np.full(5, np.nan), ca[:-5]]); V["dCb"] = cb - np.concatenate([np.full(5, np.nan), cb[:-5]])
    V["ca_rel"] = ca / np.concatenate([np.full(5, np.nan), ca[:-5]]); V["cb_rel"] = cb / np.concatenate([np.full(5, np.nan), cb[:-5]])
    V["ofi1"] = win("ofi", 1); V["ofi5"] = win("ofi", 5)
    V["micro"] = P["micro"] - P["mid"]
    return V


def main():
    t_go = time.time(); o = []; w = o.append
    G, cyc = L.grille(sys.argv[1]); P = L.preparer(G); L.P_sd1 = P["sd1"]; Y = L.resultats_officiels(cyc); V = grandeurs(G, P)
    cycles = sorted(s for s in cyc if s < RESERVE)
    avant = [s for s in cycles if s < TEST_DEB]; n_tr = len(avant) * 2 // 3
    part = {s: ("apprentissage" if k < n_tr else "validation") for k, s in enumerate(avant)}
    if not CONTROLE: part.update({s: "test" for s in cycles if s >= TEST_DEB})
    PARTS = ["apprentissage", "validation"] + ([] if CONTROLE else ["test"])
    nb = collections.Counter(part.values())
    w(f"# Bot95 — H971 / H972 : pression contre capacité, effondrement de liquidité ({'CONTRÔLE : apprentissage et validation' if CONTROLE else 'apprentissage / validation / test inédit'})\n")
    w(f"Généré le {time.strftime('%d.%m.%Y %H:%M', time.gmtime())} UTC. Cycles Dublin : " + ", ".join(f"{k} {nb[k]}" for k in PARTS) +
      " (test inédit = à partir du 12.10 06:00 UTC). Aucun ordre ; bots, H816, H821, R4, fantômes inchangés ; période réservée non lue.\n")
    # milieu Polymarket Up par seconde et carnets compacts (pour l'exécution)
    MID = np.full(G["n"], np.nan); BOOK = {}
    for st in cycles:
        if st not in part: continue
        cy = LH.Cycle(cyc[st]["f"]); T = [st * 1000 + s * 1000 for s in range(0, 300)]
        E = cy.etats(T + [t + EXEC for t in T])
        for t in T:
            Lc = DP.compact(E[t]); i = t // 1000 - G["t0"]
            if Lc and Lc[0] and Lc[1]: MID[i] = (Lc[0][0][0] + Lc[1][0][0]) / 2000
        BOOK[st] = {t: DP.compact(v) for t, v in E.items()}
    stof = lambda i: (G["t0"] + i) - (G["t0"] + i) % 300
    bn = G["bn"]; sd5 = P["sd5"]

    # ---------- H972 événements
    E = []; last = -99
    for i in range(700, G["n"] - 61):
        st = stof(i)
        if st not in part or not (G["ok"][i] and G["ok"][i + 60]) or not np.isfinite(V["zPn5"][i]) or not np.isfinite(sd5[i]): continue
        z = V["zPn5"][i]
        if abs(z) < 1.5 or i - last < 10: continue
        s = 1 if z > 0 else -1
        rel = V["ca_rel"][i] if s > 0 else V["cb_rel"][i]; rho = V["rho_a"][i] if s > 0 else V["rho_b"][i]
        mv = P["d5"][i] * s; mic = V["micro"][i] * s
        coll = np.isfinite(rel) and rel <= 0.70 and np.isfinite(rho) and rho <= 0.5 and np.isfinite(mic) and mic > 0 and mv <= 0.5 * sd5[i]
        E.append(dict(i=i, st=st, sens=s, type="effondrement" if coll else "témoin", part=part[st])); last = i
    def suivre(e):
        i, s, st = e["i"], e["sens"], e["st"]
        e["y"] = {h: (bn[i + h] - bn[i]) * s for h in HZ}
        e["pm"] = {h: ((MID[i + h] - MID[i]) * 100 * s) if (i + h < G["n"] and np.isfinite(MID[i + h]) and np.isfinite(MID[i])) else np.nan for h in HP}
        rest = st + 300 - (G["t0"] + i); m = L.m0(G, cyc, st, rest) if 30 <= rest <= 280 else None
        e["regl"] = ((Y[st] - m[0]) * s) if (m and st in Y) else np.nan
        # exécution : jeton prévu (Up si s > 0)
        X = "Up" if s > 0 else "Down"; t = (G["t0"] + i) * 1000; B = BOOK.get(st, {})
        e["pa"] = e["pb"] = np.nan
        Lo = B.get(t); Lx = B.get(t + EXEC)
        if Lo and Lx and rest >= 35:
            v = DP.vend(Lo, X)
            if v:
                lim = v[0][0]; q = c = 0.0
                for px, sz in DP.vend(Lx, X):
                    if px > lim: break
                    if px <= 0 or px >= 1000: continue
                    pp = px / 1000; u = pp + fee(pp); k = min(sz, (MISE - c) / u)
                    if k <= 1e-9: break
                    q += k; c += k * u
                if q > 0:
                    if st in Y: e["pb"] = q * (1.0 if ((Y[st] == 1.0) == (X == "Up")) else 0.0) - c
                    t2 = t + 30000; L2 = B.get(t2 - t2 % 1000 + EXEC) or B.get(t2 - t2 % 1000)
                    if L2:
                        r = 0.0; rest_q = q
                        for px, sz in DP.ach(L2, X):
                            k = min(sz, rest_q); pp = px / 1000; r += k * (pp - fee(pp)); rest_q -= k
                            if rest_q <= 1e-9: break
                        e["pa"] = r - c if rest_q <= 1e-9 else np.nan
        return e
    E = [suivre(e) for e in E]
    w("## 1. H972 — Effondrement de capacité\n")
    w("Mouvement BTC Binance après l'événement, en $, signé dans le sens prévu (positif = juste). IC 90 % par cycles.\n")
    w("| Échantillon | Type | Événements | " + " | ".join(f"{h} s" for h in HZ) + " |\n|---|---|---|" + "---|" * len(HZ))
    for pt in PARTS:
        for ty in ("effondrement", "témoin"):
            Z = [e for e in E if e["part"] == pt and e["type"] == ty]
            if len(Z) < 5: w(f"| {pt} | {ty} | {len(Z)} |" + " — |" * len(HZ)); continue
            cells = []
            for h in HZ:
                v = np.array([e["y"][h] for e in Z]); m = np.isfinite(v); c_ = L.ic_g(np.array([e["st"] for e in Z])[m], v[m])
                cells.append(f"{np.nanmean(v):+.1f} [{c_[0]:+.1f} ; {c_[1]:+.1f}]")
            w(f"| {pt} | {ty} | {len(Z)} | " + " | ".join(cells) + " |")
    w("\n**Réévaluation Polymarket** (milieu du jeton prévu, en centimes, signé) et **règlement officiel** (résultat − M0, signé)\n")
    w("| Échantillon | Type | " + " | ".join(f"Polymarket {h} s" for h in HP) + " | Règlement |\n|---|---|" + "---|" * (len(HP) + 1))
    for pt in PARTS:
        for ty in ("effondrement", "témoin"):
            Z = [e for e in E if e["part"] == pt and e["type"] == ty]
            if len(Z) < 5: continue
            cells = []
            for h in HP + ("r",):
                v = np.array([(e["pm"][h] if h != "r" else e["regl"]) for e in Z], float); m = np.isfinite(v)
                if m.sum() < 5: cells.append("—"); continue
                c_ = L.ic_g(np.array([e["st"] for e in Z])[m], v[m]); cells.append(f"{v[m].mean():+.2f} [{c_[0]:+.2f} ; {c_[1]:+.2f}] (n={m.sum()})" if h == "r" else f"{v[m].mean():+.2f} [{c_[0]:+.2f} ; {c_[1]:+.2f}]")
            w(f"| {pt} | {ty} | " + " | ".join(cells) + " |")
    w("\n**Occasion exécutable** : achat 20 $ du jeton prévu à 164 ms au prix vu (frais compris), (a) revente 30 s après au meilleur acheteur, (b) conservation.\n")
    w("| Échantillon | Type | Achats | (a) P&L total, revente à 30 s | IC 90 % (total) | (b) P&L total, règlement | IC 90 % (total) |\n|---|---|---|---|---|---|---|")
    for pt in PARTS:
        for ty in ("effondrement", "témoin"):
            Z = [e for e in E if e["part"] == pt and e["type"] == ty]
            row = f"| {pt} | {ty} |"
            pa = np.array([e["pa"] for e in Z], float); pb = np.array([e["pb"] for e in Z], float); g = np.array([e["st"] for e in Z])
            row += f" {int(np.isfinite(pb).sum())} |"
            for v in (pa, pb):
                m = np.isfinite(v)
                if m.sum() < 3: row += " — | — |"; continue
                c_ = L.ic_tot(g[m], v[m]); row += f" {v[m].sum():+.0f} | [{c_[0]:+.0f} ; {c_[1]:+.0f}] |"
            w(row)

    # ---------- H971 prévision
    w("\n## 2. H971 — La pression rapportée à la capacité prévoit-elle mieux qu'OFI + momentum + volatilité ?\n")
    I = [i for i in range(700, G["n"] - 31, 3) if stof(i) in part and G["ok"][i] and G["ok"][i + 30] and np.isfinite(bn[i + 30]) and np.isfinite(G["bid"][i]) and np.isfinite(P["sd1"][i])]
    s1 = lambda i: P["sd1"][i]
    XS = np.nan_to_num(np.array([[V["ofi1"][i], V["ofi5"][i], (bn[i] - bn[i - 1]) / s1(i), (bn[i] - bn[i - 5]) / s1(i), (bn[i] - bn[i - 30]) / s1(i), s1(i)] for i in I]))
    XP = np.nan_to_num(np.array([[V["PCI5"][i], V["PCI30"][i], min(V["rho_a"][i], 10), min(V["rho_b"][i], 10), V["Wa"][i], V["Wb"][i], V["dCa"][i], V["dCb"][i], V["micro"][i] / s1(i)] for i in I]))
    pt_I = np.array([part[stof(i)] for i in I]); g_I = np.array([stof(i) for i in I])
    sd30 = np.array([s1(i) * math.sqrt(30) for i in I])
    cib = {"hausse BTC à 10 s": np.array([bn[i + 10] > bn[i] for i in I], float), "hausse BTC à 30 s": np.array([bn[i + 30] > bn[i] for i in I], float),
           "grand mouvement à 30 s vers le haut": np.array([(bn[i + 30] - bn[i]) > 1.5 * s for i, s in zip(I, sd30)], float),
           "grand mouvement à 30 s vers le bas": np.array([(bn[i + 30] - bn[i]) < -1.5 * s for i, s in zip(I, sd30)], float),
           "milieu Polymarket Up +1 c à 10 s": np.array([(MID[i + 10] - MID[i]) >= 0.01 if (np.isfinite(MID[i + 10]) and np.isfinite(MID[i])) else np.nan for i in I], float)}
    w(f"{len(I)} instants (toutes les 3 s). IC corrigé : 10 comparaisons.\n")
    w("| Cible | Échantillon | Taux de base | AUC simple (OFI, momentum, volatilité) | AUC simple + pression/capacité | ΔAUC | IC 90 % | IC corrigé |\n|---|---|---|---|---|---|---|---|")
    trm = pt_I == "apprentissage"
    for nom, y in cib.items():
        ok = np.isfinite(y)
        res = {}
        for lab, X in (("S", XS), ("SP", np.column_stack([XS, XP]))):
            mu, sd = X[trm & ok].mean(0), X[trm & ok].std(0) + 1e-9; b = L.ajuster((X[trm & ok] - mu) / sd, y[trm & ok], 2.0); res[lab] = L.predire(b, (X - mu) / sd)
        for pt in [p for p in PARTS if p != "apprentissage"]:
            m = (pt_I == pt) & ok
            if m.sum() < 100: continue
            yt = y[m]; a0 = L.auc(res["S"][m], yt); a1 = L.auc(res["SP"][m], yt); g = g_I[m]; Ug = np.unique(g); D = []
            for _ in range(400):
                mm = np.isin(g, RNG.choice(Ug, len(Ug)))
                if yt[mm].min() != yt[mm].max(): D.append(L.auc(res["SP"][m][mm], yt[mm]) - L.auc(res["S"][m][mm], yt[mm]))
            w(f"| {nom} | {pt} | {100 * yt.mean():.0f} % | {a0:.3f} | {a1:.3f} | {a1 - a0:+.3f} | [{np.percentile(D, 5):+.3f} ; {np.percentile(D, 95):+.3f}] | "
              f"[{np.percentile(D, 0.5):+.3f} ; {np.percentile(D, 99.5):+.3f}] |")

    # ---------- règlement A contre A + PC
    w("\n## 3. Règlement officiel : modèle A (règlement seul, recalibré) contre A + pression/capacité\n")
    D_ = []
    for st in cycles:
        if st not in Y or st not in part: continue
        for rest in (240, 180, 120, 90, 60, 30):
            m = L.m0(G, cyc, st, rest)
            if m is None: continue
            i = m[2]
            if i < 700 or not np.isfinite(G["bid"][i]): continue
            x = [V["PCI5"][i], V["PCI30"][i], min(V["rho_a"][i], 10), min(V["rho_b"][i], 10), V["Wa"][i], V["Wb"][i], V["dCa"][i], V["dCb"][i], V["micro"][i] / s1(i)]
            D_.append(dict(st=st, p=m[0], z=m[1], y=Y[st], x=np.nan_to_num(np.array(x, float)), part=part[st]))
    tr = [d for d in D_ if d["part"] == "apprentissage"]
    XA = lambda Z: np.array([[L.lg(d["p"])] for d in Z]); XB = lambda Z: np.array([[L.lg(d["p"])] + list(d["x"]) for d in Z])
    bA = L.ajuster(XA(tr), np.array([d["y"] for d in tr]), 0.1)
    Xb = XB(tr); mu, sd = Xb.mean(0), Xb.std(0) + 1e-9; mu[0], sd[0] = 0, 1; bB = L.ajuster((Xb - mu) / sd, np.array([d["y"] for d in tr]), 2.0)
    w("| Échantillon | Sous-ensemble | Décisions | Brier A | Brier A + PC | Log loss A / A + PC | Précision A / A + PC | ΔBrier (A − A+PC) | IC 90 % | IC corrigé (6) |\n|---|---|---|---|---|---|---|---|---|---|")
    for pt in [p for p in PARTS if p != "apprentissage"]:
        Z = [d for d in D_ if d["part"] == pt]
        if not Z: continue
        pa = L.predire(bA, XA(Z)); pb = L.predire(bB, (XB(Z) - mu) / sd); y = np.array([d["y"] for d in Z]); g = np.array([d["st"] for d in Z])
        for lab, m in (("toutes", np.ones(len(Z), bool)), ("proches de 50 %", np.array([0.35 <= d["p"] <= 0.65 for d in Z])), ("marge faible", np.array([abs(d["z"]) < 0.5 for d in Z]))):
            if m.sum() < 10: continue
            ea, eb = L.brier(pa[m], y[m]), L.brier(pb[m], y[m]); d_ = ea - eb; c1 = L.ic_g(g[m], d_); c2 = L.ic_g(g[m], d_, 0.10 / 6)
            w(f"| {pt} | {lab} | {int(m.sum())} | {ea.mean():.4f} | {eb.mean():.4f} | {L.ll(pa[m], y[m]).mean():.3f} / {L.ll(pb[m], y[m]).mean():.3f} | "
              f"{100 * np.mean((pa[m] > .5) == (y[m] > .5)):.0f} % / {100 * np.mean((pb[m] > .5) == (y[m] > .5)):.0f} % | {d_.mean():+.5f} | [{c1[0]:+.5f} ; {c1[1]:+.5f}] | [{c2[0]:+.5f} ; {c2[1]:+.5f}] |")
    w("\n## Limites\n- Carnet Binance limité à 50 $ du meilleur prix ; Bybit et OKX sans carnet profond enregistré ; liquidations agrégées seulement.\n"
      "- Quelques dizaines d'heures de données ; test inédit d'environ 6 h.\n- Le milieu Polymarket est reconstruit (photos 10 s + changements à ±3 c).\n")
    w(f"_Calcul : {time.time() - t_go:.0f} s._\n")
    open(SORTIE, "w").write("\n".join(o)); print("\n".join(o))


if __name__ == "__main__":
    main()
