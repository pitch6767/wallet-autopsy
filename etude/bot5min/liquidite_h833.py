"""BOT95 — FUSION ENGINE F1 : H833 à H835 (Pitch, 12.10.2026 12:48). PROTOCOLE PRÉ-ENREGISTRÉ (ce fichier tel que committé avant le calcul
de validation). Hors ligne ; aucun ordre ; aucun bot actif, H816, H821, R4 ni fantôme modifié ; période réservée (≥ 13.10.2026) jamais lue.

DONNÉES
  Dublin (branche donnees-rapide, cycles < 13.10) : prix Binance spot / Bybit perp / OKX swap / Coinbase / Chainlink (« ex », heure de réception),
    carnets Binance spot et Bybit perp toutes les 100 ms (meilleurs prix, tailles, cumuls à 5/10/20/50 $, baisses et ajouts de quantité),
    photos 10 niveaux chaque seconde, transactions Binance spot et Bybit perp avec côté agresseur, carnet Polymarket, prix à battre officiel.
  Binance spot 1 s BTC, ETH, SOL (12.09 → 11.10) pour H835.
  Non disponibles à la seconde (déclarés, non estimés) : Nasdaq, or, devises, CME. Deribit enregistré seulement à partir du 12.10 (futur).
GRILLE : une ligne par seconde t ; chaque variable n'utilise que des messages REÇUS à Dublin avant t.
RÉSULTAT : officiel Polymarket (bot95/reglements.json, sinon gagnant enregistré par Dublin, sinon moyenne 60 s officielle reçue vs prix à battre).
  Les cycles où le substitut Binance diffère de l'officiel sont comptés à part.

H833 ABSORPTION (événements, au plus un par 10 s) : A5 = volume agressif net (achats − ventes, BTC, Binance spot + Bybit perp) sur 5 s ;
  z = A5 / écart-type de A5 sur les 600 s précédentes ; σ5 = écart-type des variations de prix sur 5 s (600 s précédentes).
  Absorption baissière (achats absorbés) : z ≥ 2 ; hausse du prix sur 5 s ≤ 0,25 σ5 ; profondeur vendeuse à 10 $ ≥ 90 % de celle d'il y a 5 s ;
    microprix ≤ dernier prix ; au moins 3 prix différents traités à l'achat sur 5 s. Direction prévue : baisse. Absorption haussière : symétrique.
  Référence : même z ≥ 2 sans absorption (le prix a suivi le flux).
  Mesures : variation BTC signée dans le sens prévu à 1, 3, 5, 10, 30, 60 s ($ et σ), IC 90 % par cycles ; effet sur le règlement officiel :
    résultat − probabilité M0 au même instant, signé dans le sens prévu (événements avec 30 à 240 s restantes).
H834 RETRAIT DE LIQUIDITÉ : variables à t : OFI (Cont) sur 1 et 5 s, retraits (baisses non expliquées par les transactions) acheteurs et vendeurs
  sur 5 s, variation de profondeur à 20 $ sur 5 s, déséquilibre à 5 et 20 $, écart microprix − milieu, écart achat-vente, taille et âge du plus gros
  mur à 10 niveaux de chaque côté (photos 1 s, mur = taille ≥ 5 × médiane des 10 niveaux). Cible : signe de la variation à 10 s et 30 s, et
  « grand mouvement » (|variation 30 s| > 1,5 σ30) avec son sens. Logistique : contrôles seuls (variations passées 1/5/30 s, volatilité) contre
  contrôles + liquidité ; apprentissage = 1re moitié des cycles, test = 2e moitié ; AUC et écart d'AUC, IC 90 % par cycles.
H835 AUTRES ACTIFS : (a) 30 jours Binance 1 s : corrélation simultanée et avance (rendement ETH/SOL passé → BTC futur) aux décalages 1, 2, 5, 10, 30 s,
  R² hors échantillon (apprentissage < 02.10, test 02.10 → 11.10) contre BTC seul ; (b) Dublin 50 ms : perp Bybit, OKX, Coinbase contre Binance spot,
  avance de 100 à 1 000 ms, même logique.
MODÈLES A/B/C/D (décisions à 240/180/120/90/60/30 s de la fin de chaque cycle Dublin, mêmes décisions pour les quatre) :
  A = règlement seul (M0 : Chainlink, moyenne finale exacte, volatilité 300 s) recalibré par logistique ;
  B = A + flux BTC (volume agressif net 5/30 s Binance et Bybit, variations 5/30 s) ;
  C = B + liquidité L2 (OFI 1/5 s, retraits 5 s, déséquilibres, microprix, murs) ;
  D = C + autres places (base perp − spot et sa variation 5/30 s, avance OKX/Coinbase/perp sur 2 s).
  Logistique régularisée (L2 = 2, variables standardisées), apprise sur la 1re moitié des cycles, mesurée sur la 2e moitié.
  Mesures : Brier, log loss, précision, calibration ; tous / proches de 50 % (M0 entre 0,35 et 0,65) / marge faible (|z| < 0,5) ;
  écarts B−A, C−B, D−C avec IC 90 % par cycles et IC corrigé (3 comparaisons × 3 sous-ensembles = 9).
  P&L exécutable : pour chaque modèle, achat 20 $ du côté X si P(X) − prix vendeur − frais ≥ 0,05 (au plus une fois par cycle, première
  décision qui passe), exécution 164 ms après sur le carnet Polymarket enregistré, conservation, résultat officiel ; écart avec A, IC par cycles.
DÉCISION PAR MODULE : conservé seulement si l'IC corrigé de l'apport marginal (Brier) exclut 0 du bon côté ET le P&L ne se dégrade pas.
Usage : python3 etude/bot5min/liquidite_h833.py dossier_cycles_dublin dossier_btc [--controle]  (--controle = apprentissage seul)"""
import os, sys, glob, json, gzip, math, time, bisect, collections
import numpy as np, pandas as pd

ICI = os.path.dirname(os.path.abspath(__file__)); RACINE = os.path.abspath(os.path.join(ICI, "..", ".."))
sys.path.insert(0, ICI)
import latence_h766 as LH
RESERVE = 1791849600; COUPE_BIN = 1790899200; CONTROLE = "--controle" in sys.argv
SORTIE = os.path.join(ICI, "resultat_liquidite_h833" + ("_controle" if CONTROLE else "") + ".md")
RNG = np.random.default_rng(833); MISE = 20.0; EXEC = 164; RESTES = (240, 180, 120, 90, 60, 30); HZ = (1, 3, 5, 10, 30, 60)
SRC = ("perp", "okx", "bn", "cb", "cl")
fee = lambda p: 0.07 * p * (1 - p)
Phi = lambda x: 0.5 * (1 + math.erf(x / math.sqrt(2)))
lg = lambda p: math.log(min(max(p, 1e-4), 1 - 1e-4) / (1 - min(max(p, 1e-4), 1 - 1e-4)))


# ------------------------------------------------------------------ grille 1 s à partir des fichiers Dublin
def grille(dossier):
    F = sorted((int(os.path.basename(f).split(".")[0]), f) for f in glob.glob(os.path.join(dossier, "**", "*.json.gz"), recursive=True))
    F = [(s, f) for s, f in F if s < RESERVE]
    t0 = F[0][0]; t1 = F[-1][0] + 300; n = t1 - t0
    G = {k: np.full(n, np.nan) for k in ["perp", "okx", "bn", "cb", "cl", "bid", "ask", "s1b", "s1a", "cb5", "cb10", "cb20", "ca5", "ca10", "ca20",
                                          "byb", "bya", "dec_b", "dec_a", "add_b", "add_a", "ofi", "agb", "ags", "agb_by", "ags_by", "npx_b", "npx_a",
                                          "mur_b", "mur_a", "murage_b", "murage_a"]}
    for k in ("dec_b", "dec_a", "add_b", "add_a", "ofi", "agb", "ags", "agb_by", "ags_by", "npx_b", "npx_a"): G[k][:] = 0.0
    cyc = {}; ok = np.zeros(n, bool)
    for st, f in F:
        try: R = json.load(gzip.open(f))
        except Exception: continue
        cyc[st] = dict(f=f, strike=(R.get("marche") or {}).get("strike"), tw=R.get("tw") or [])
        # prix des places (réception)
        last = {}
        rows = sorted(R.get("ex", []), key=lambda r: r[0])
        j = 0
        for s_ in range(st, st + 300):
            i = s_ - t0
            while j < len(rows) and rows[j][0] / 1000 <= s_:
                for k, v in zip(SRC, rows[j][1:]):
                    if v and v[0]: last[k] = v[0]
                j += 1
            for k in SRC:
                if k in last: G[k][i] = last[k]
        # carnet Binance (100 ms) et Bybit
        ob = (R.get("ob") or {}); prev = None
        for r in ob.get("bn", []):
            s_ = int(math.ceil(r[0] / 1000)); i = s_ - t0
            if not (0 <= i < n): continue
            bid, ask, s1b, s1a = r[2], r[3], r[4], r[5]
            G["bid"][i], G["ask"][i], G["s1b"][i], G["s1a"][i] = bid, ask, s1b, s1a
            G["cb5"][i], G["cb10"][i], G["cb20"][i] = r[6], r[7], r[8]; G["ca5"][i], G["ca10"][i], G["ca20"][i] = r[10], r[11], r[12]
            G["dec_b"][i] += r[14]; G["dec_a"][i] += r[15]; G["add_b"][i] += r[16]; G["add_a"][i] += r[17]
            if prev is not None:
                pb, pa, pqb, pqa = prev
                e = (s1b if bid > pb else (s1b - pqb if bid == pb else -pqb)) - (s1a if ask < pa else (s1a - pqa if ask == pa else -pqa))
                G["ofi"][i] += e
            prev = (bid, ask, s1b, s1a)
        for r in ob.get("by", []):
            i = int(math.ceil(r[0] / 1000)) - t0
            if 0 <= i < n: G["byb"][i], G["bya"][i] = r[2], r[3]
        # transactions agressives
        tx = R.get("trx") or {}
        pxs = collections.defaultdict(lambda: [set(), set()])
        for k, (kb, ks) in (("bn", ("agb", "ags")), ("by", ("agb_by", "ags_by"))):
            for r in tx.get(k, []):
                i = int(math.ceil(r[0] / 1000)) - t0
                if not (0 <= i < n): continue
                G[kb if r[2] == 1 else ks][i] += r[4]
                if k == "bn": pxs[i][0 if r[2] == 1 else 1].add(r[3])
        for i, (a, b) in pxs.items(): G["npx_b"][i] = len(a); G["npx_a"][i] = len(b)
        # murs (photos 10 niveaux chaque seconde)
        age = {0: None, 1: None}
        for r in (R.get("obSnap") or {}).get("bn", []):
            i = int(math.ceil(r[0] / 1000)) - t0
            if not (0 <= i < n): continue
            for side, lv, kk, ka in ((0, r[2], "mur_b", "murage_b"), (1, r[3], "mur_a", "murage_a")):
                if not lv: continue
                sz = np.array([x[1] for x in lv]); med = np.median(sz); j_ = int(np.argmax(sz))
                if sz[j_] >= 5 * max(med, 1e-6):
                    px = lv[j_][0]; a = age[side]
                    age[side] = (px, a[1]) if (a and a[0] == px) else (px, i)
                    G[kk][i] = sz[j_]; G[ka][i] = i - age[side][1]
                else: age[side] = None; G[kk][i] = 0; G[ka][i] = 0
        ok[st - t0:st - t0 + 300] = True
    # remplissage vers l'avant des prix et du carnet sur les secondes sans message (pas au-delà de 5 s)
    for k in ("perp", "okx", "bn", "cb", "cl", "bid", "ask", "s1b", "s1a", "cb5", "cb10", "cb20", "ca5", "ca10", "ca20", "byb", "bya", "mur_b", "mur_a", "murage_b", "murage_a"):
        s = pd.Series(G[k]).ffill(limit=5).values; G[k] = s
    G["ok"] = ok; G["t0"] = t0; G["n"] = n
    return G, cyc


def resultats_officiels(cyc):
    R = {x["start"]: x for x in json.load(open(os.path.join(RACINE, "bot95", "reglements.json"))) if x["a"] == "BTC" and x.get("gagnant")}
    S = {}
    for s in json.load(open(os.path.join(RACINE, "bot95", "rapide.json")))["signaux"]:
        if s.get("gagnant"): S[s["start"]] = s["gagnant"]
    out = {}
    for st, c in cyc.items():
        if st in R: out[st] = 1.0 if R[st]["gagnant"] == "Up" else 0.0
        elif st in S: out[st] = 1.0 if S[st] == "Up" else 0.0
        elif c["tw"] and c["strike"]:
            last = max(c["tw"], key=lambda r: r[1])
            if last[1] >= (st + 299) * 1000: out[st] = 1.0 if last[2] > c["strike"] else 0.0
    return out


# ------------------------------------------------------------------ variables à l'instant i
def roll_sd(x, w):
    s = pd.Series(x); return s.rolling(w, min_periods=w // 2).std().shift(1).values


def preparer(G):
    n = G["n"]; bn = G["bn"]
    agg = (G["agb"] - G["ags"]) + (G["agb_by"] - G["ags_by"])
    cs = lambda x: np.concatenate([[0], np.cumsum(np.nan_to_num(x))])
    C = {k: cs(G[k]) for k in ("agb", "ags", "agb_by", "ags_by", "ofi", "dec_b", "dec_a", "npx_b", "npx_a")}; C["agg"] = cs(agg)
    win = lambda k, i, w: C[k][i + 1] - C[k][max(i + 1 - w, 0)]
    A5 = np.array([win("agg", i, 5) for i in range(n)]); sdA5 = roll_sd(A5, 600)
    d5 = np.full(n, np.nan); d5[5:] = bn[5:] - bn[:-5]; sd5 = roll_sd(d5, 600)
    d1 = np.full(n, np.nan); d1[1:] = np.diff(bn); sd1 = roll_sd(d1, 300)
    micro = (G["bid"] * G["s1a"] + G["ask"] * G["s1b"]) / np.maximum(G["s1a"] + G["s1b"], 1e-9)
    mid = (G["bid"] + G["ask"]) / 2
    return dict(agg=agg, A5=A5, sdA5=sdA5, d5=d5, sd5=sd5, sd1=sd1, micro=micro, mid=mid, win=win)


def ret(G, i, h): return G["bn"][i + h] - G["bn"][i] if i + h < G["n"] else np.nan


# ------------------------------------------------------------------ H833 absorption
def h833(G, P, part):
    n = G["n"]; bn = G["bn"]; E = []; last = -99
    for i in range(620, n - 61):
        if not (G["ok"][i] and G["ok"][i + 60]) or not np.isfinite(P["sdA5"][i]) or P["sdA5"][i] <= 0 or not np.isfinite(P["sd5"][i]): continue
        z = P["A5"][i] / P["sdA5"][i]
        if abs(z) < 2 or i - last < 10: continue
        sens_flux = 1 if z > 0 else -1; mv = P["d5"][i] * sens_flux
        if sens_flux > 0: rep = G["ca10"][i] >= 0.9 * G["ca10"][i - 5]; mic = P["micro"][i] <= bn[i]; lv = P["win"]("npx_b", i, 5) >= 3
        else: rep = G["cb10"][i] >= 0.9 * G["cb10"][i - 5]; mic = P["micro"][i] >= bn[i]; lv = P["win"]("npx_a", i, 5) >= 3
        absorbe = mv <= 0.25 * P["sd5"][i] and rep and mic and lv
        suivi = mv > 0.25 * P["sd5"][i]
        if not (absorbe or suivi): continue
        prevu = -sens_flux if absorbe else sens_flux
        st = G["t0"] + i - (G["t0"] + i) % 300
        E.append(dict(i=i, st=st, type="absorption" if absorbe else "flux suivi", sens=prevu, flux=sens_flux,
                      y={h: ret(G, i, h) * prevu for h in HZ}, s5=P["sd5"][i], part=part(st)))
        last = i
    return E


# ------------------------------------------------------------------ M0 Chainlink et décisions
def m0(G, cyc, st, rest):
    i = st + 300 - rest - G["t0"]; cl = G["cl"]; K = cyc[st]["strike"]
    if K is None or not np.isfinite(cl[i]): return None
    sig = P_sd1[i] if np.isfinite(P_sd1[i]) and P_sd1[i] > 0 else None
    if sig is None: return None
    a = st + 240 - G["t0"]
    if i <= a: mu = cl[i]; sd = sig * math.sqrt(a - i + 20)
    else:
        obs = cl[a:i]; obs = obs[np.isfinite(obs)]; n_obs = len(obs); Lf = 60 - n_obs
        mu = (obs.sum() + Lf * cl[i]) / 60.0; sd = sig * (Lf / 60.0) * math.sqrt(max(Lf, 1) / 3.0)
    sd = max(sd, 1e-6); z = (mu - K) / sd
    return Phi(z), z, i


def feats(G, P, i):
    w = P["win"]; bn = G["bn"]; s1 = P["sd1"][i] if np.isfinite(P["sd1"][i]) and P["sd1"][i] > 0 else 1.0
    B = [w("agb", i, 5) - w("ags", i, 5), w("agb", i, 30) - w("ags", i, 30), w("agb_by", i, 5) - w("ags_by", i, 5), w("agb_by", i, 30) - w("ags_by", i, 30),
         (bn[i] - bn[i - 5]) / s1, (bn[i] - bn[i - 30]) / s1]
    tr_b = w("ags", i, 5); tr_a = w("agb", i, 5)
    C = [w("ofi", i, 1), w("ofi", i, 5), (w("dec_b", i, 5) - tr_b), (w("dec_a", i, 5) - tr_a),
         (G["cb5"][i] - G["ca5"][i]) / max(G["cb5"][i] + G["ca5"][i], 1e-9), (G["cb20"][i] - G["ca20"][i]) / max(G["cb20"][i] + G["ca20"][i], 1e-9),
         (G["cb20"][i] - G["cb20"][i - 5]) - (G["ca20"][i] - G["ca20"][i - 5]), (P["micro"][i] - P["mid"][i]) / s1, (G["ask"][i] - G["bid"][i]) / s1,
         (G["mur_b"][i] or 0) - (G["mur_a"][i] or 0), min(G["murage_b"][i] or 0, 60) - min(G["murage_a"][i] or 0, 60)]
    base = lambda k, j: G[k][j] - G["bn"][j]
    D = [base("perp", i) / s1, (base("perp", i) - base("perp", i - 5)) / s1, (base("perp", i) - base("perp", i - 30)) / s1,
         ((G["okx"][i] - G["okx"][i - 2]) - (bn[i] - bn[i - 2])) / s1, ((G["cb"][i] - G["cb"][i - 2]) - (bn[i] - bn[i - 2])) / s1,
         ((G["perp"][i] - G["perp"][i - 2]) - (bn[i] - bn[i - 2])) / s1]
    return B, C, D


def ajuster(X, y, l2=1.0):
    X = np.column_stack([np.ones(len(X)), X]); b = np.zeros(X.shape[1]); Pn = np.eye(X.shape[1]) * l2; Pn[0, 0] = 0
    for _ in range(60):
        p = 1 / (1 + np.exp(-np.clip(X @ b, -30, 30))); g = X.T @ (p - y) + Pn @ b; H = X.T @ (X * (p * (1 - p))[:, None]) + Pn
        b -= np.linalg.solve(H, g)
    return b
def predire(b, X): X = np.column_stack([np.ones(len(X)), X]); return 1 / (1 + np.exp(-np.clip(X @ b, -30, 30)))
def brier(p, y): return (np.asarray(p) - np.asarray(y)) ** 2
def ll(p, y): p = np.clip(np.asarray(p), 1e-4, 1 - 1e-4); return -(y * np.log(p) + (1 - y) * np.log(1 - p))


def ic_g(g, v, alpha=0.10, B=3000):
    g = np.asarray(g); v = np.asarray(v, float); U, inv = np.unique(g, return_inverse=True)
    if len(U) < 3: return (float("nan"), float("nan"))
    S_ = np.bincount(inv, v); N_ = np.bincount(inv); idx = RNG.integers(0, len(U), (B, len(U))); m = S_[idx].sum(1) / N_[idx].sum(1)
    return float(np.percentile(m, 100 * alpha / 2)), float(np.percentile(m, 100 * (1 - alpha / 2)))


def ic_tot(g, v, alpha=0.10, B=3000):
    g = np.asarray(g); v = np.asarray(v, float); U, inv = np.unique(g, return_inverse=True)
    if len(U) < 3: return (float("nan"), float("nan"))
    S_ = np.bincount(inv, v); idx = RNG.integers(0, len(U), (B, len(U))); m = S_[idx].sum(1)
    return float(np.percentile(m, 100 * alpha / 2)), float(np.percentile(m, 100 * (1 - alpha / 2)))


def auc(s, y):
    s = np.asarray(s); y = np.asarray(y); o = np.argsort(s); r = np.empty(len(s)); r[o] = np.arange(1, len(s) + 1)
    n1 = y.sum(); n0 = len(y) - n1
    return float((r[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)) if n1 and n0 else float("nan")


# ------------------------------------------------------------------ principal
def main():
    global P_sd1
    t_go = time.time(); o = []; w = o.append
    G, cyc = grille(sys.argv[1]); P = preparer(G); P_sd1 = P["sd1"]
    Y = resultats_officiels(cyc)
    cycles = sorted(cyc); coupe = cycles[len(cycles) // 2]
    part = lambda st: "apprentissage" if st < coupe else "test"
    tr_cy = [c for c in cycles if c < coupe]
    w(f"# Bot95 — H833 à H835 : absorption, retrait de liquidité, autres actifs ({'CONTRÔLE, apprentissage seul' if CONTROLE else 'apprentissage → test'})\n")
    w(f"Généré le {time.strftime('%d.%m.%Y %H:%M', time.gmtime())} UTC. Cycles Dublin : {len(cycles)} ({time.strftime('%d.%m %H:%M', time.gmtime(cycles[0]))} → "
      f"{time.strftime('%d.%m %H:%M', time.gmtime(cycles[-1] + 300))} UTC) ; apprentissage {len(tr_cy)} cycles (avant {time.strftime('%d.%m %H:%M', time.gmtime(coupe))} UTC), "
      f"test {len(cycles) - len(tr_cy)}. Résultat officiel connu pour {len(Y)} cycles. Aucun ordre ; bots, H816, H821, R4, fantômes inchangés ; période réservée non lue.\n")

    # 1. couverture et qualité
    w("## 1. Couverture et qualité des données L2 (Dublin)\n")
    tous = G["ok"].sum()
    def cov(k): return 100 * np.mean(np.isfinite(G[k][G["ok"]]))
    trous = collections.Counter();
    for st, c in cyc.items():
        try:
            for r in json.load(gzip.open(c["f"])).get("obTrous", []): trous[(r[1], r[2])] += 1
        except Exception: pass
    w(f"| Donnée | Secondes couvertes |\n|---|---|\n| Prix Binance spot | {cov('bn'):.1f} % |\n| Prix Bybit perp | {cov('perp'):.1f} % |\n| Prix OKX swap | {cov('okx'):.1f} % |\n"
      f"| Prix Coinbase | {cov('cb'):.1f} % |\n| Chainlink | {cov('cl'):.1f} % |\n| Carnet Binance (meilleurs prix, cumuls) | {cov('bid'):.1f} % |\n| Carnet Bybit | {cov('byb'):.1f} % |\n"
      f"| Photos 10 niveaux Binance (murs) | {cov('mur_b'):.1f} % |\n")
    w(f"Secondes enregistrées : {int(tous)} ({tous / 3600:.1f} h). Trous signalés par l'enregistreur : " + (", ".join(f"{k[0]} {k[1]} : {v}" for k, v in trous.most_common()) or "aucun") + ".\n")
    w("Limites : profondeur au-delà de 50 $ et au-delà de 10 niveaux non enregistrée ; liquidations Bybit agrégées seulement ; Deribit à partir du 12.10.\n")

    # 2. H833
    E = h833(G, P, part)
    w("## 2. H833 — Absorption de liquidité\n")
    w("Variation BTC (Binance spot) après l'événement, signée dans le sens prévu (positif = la prévision était juste), en $. IC 90 % par cycles.\n")
    w("| Échantillon | Type | Sens du flux | Événements | " + " | ".join(f"{h} s" for h in HZ) + " | 30 s en σ5 |\n|---|---|---|---|" + "---|" * len(HZ) + "---|")
    for pt in (("apprentissage",) if CONTROLE else ("apprentissage", "test")):
        for ty in ("absorption", "flux suivi"):
            for fl in (1, -1):
                Z = [e for e in E if e["part"] == pt and e["type"] == ty and e["flux"] == fl and np.isfinite(e["y"][60])]
                if len(Z) < 5: w(f"| {pt} | {ty} | {'achats' if fl > 0 else 'ventes'} | {len(Z)} |" + " — |" * len(HZ) + " — |"); continue
                cells = []
                for h in HZ:
                    v = np.array([e["y"][h] for e in Z]); c = ic_g([e["st"] for e in Z], v); cells.append(f"{v.mean():+.1f} [{c[0]:+.1f} ; {c[1]:+.1f}]")
                w(f"| {pt} | {ty} | {'achats' if fl > 0 else 'ventes'} | {len(Z)} | " + " | ".join(cells) + f" | {np.mean([e['y'][30] / max(e['s5'], 1e-9) for e in Z]):+.2f} |")
    # effet sur le règlement
    w("\n**Effet sur le règlement officiel** (événements avec 30 à 240 s restantes) : résultat − probabilité M0 au même instant, signé dans le sens prévu.\n")
    w("| Échantillon | Type | Événements | Écart moyen | IC 90 % par cycles |\n|---|---|---|---|---|")
    for pt in (("apprentissage",) if CONTROLE else ("apprentissage", "test")):
        for ty in ("absorption", "flux suivi"):
            V = []; g = []
            for e in E:
                if e["part"] != pt or e["type"] != ty or e["st"] not in Y: continue
                rest = e["st"] + 300 - (G["t0"] + e["i"])
                if not (30 <= rest <= 240): continue
                m = m0(G, cyc, e["st"], rest)
                if m is None: continue
                V.append((Y[e["st"]] - m[0]) * e["sens"]); g.append(e["st"])
            if len(V) >= 5: c = ic_g(g, V); w(f"| {pt} | {ty} | {len(V)} | {np.mean(V):+.3f} | [{c[0]:+.3f} ; {c[1]:+.3f}] |")

    # 3. H834
    w("\n## 3. H834 — Retrait de liquidité : annonce-t-il le mouvement ?\n")
    I = [i for i in range(620, G["n"] - 31, 3) if G["ok"][i] and G["ok"][i + 30] and np.isfinite(G["bn"][i + 30]) and np.isfinite(G["bid"][i]) and np.isfinite(P["sd1"][i])]
    ctrl = lambda i: [(G["bn"][i] - G["bn"][i - 1]) / P["sd1"][i], (G["bn"][i] - G["bn"][i - 5]) / P["sd1"][i], (G["bn"][i] - G["bn"][i - 30]) / P["sd1"][i], P["sd1"][i]]
    Xc = np.nan_to_num(np.array([ctrl(i) for i in I])); Xl = np.nan_to_num(np.array([feats(G, P, i)[1] for i in I]))
    stI = np.array([G["t0"] + i - (G["t0"] + i) % 300 for i in I]); trm = stI < coupe; tem = ~trm
    sd30 = np.array([P["sd1"][i] * math.sqrt(30) for i in I])
    cibles = {"hausse à 10 s": np.array([G["bn"][i + 10] > G["bn"][i] for i in I], float), "hausse à 30 s": np.array([G["bn"][i + 30] > G["bn"][i] for i in I], float),
              "grand mouvement à 30 s, vers le haut": np.array([(G["bn"][i + 30] - G["bn"][i]) > 1.5 * s for i, s in zip(I, sd30)], float),
              "grand mouvement à 30 s, vers le bas": np.array([(G["bn"][i + 30] - G["bn"][i]) < -1.5 * s for i, s in zip(I, sd30)], float)}
    w(f"{len(I)} instants (toutes les 3 s). Contrôles = variations passées 1/5/30 s et volatilité ; liquidité = OFI, retraits, profondeur, déséquilibres, microprix, écart, murs.\n")
    w("| Cible | Taux de base test | AUC contrôles seuls | AUC contrôles + liquidité | Écart (IC 90 % par cycles) |\n|---|---|---|---|---|")
    for nom, y in cibles.items():
        if CONTROLE:
            continue
        X1 = Xc; X2 = np.column_stack([Xc, Xl]); res = []
        for X in (X1, X2):
            mu, sd = X[trm].mean(0), X[trm].std(0) + 1e-9; b = ajuster((X[trm] - mu) / sd, y[trm], 2.0); res.append(predire(b, (X[tem] - mu) / sd))
        yt = y[tem]; g = stI[tem]; Ug = np.unique(g); diffs = []
        for _ in range(400):
            m = np.isin(g, RNG.choice(Ug, len(Ug)))
            if yt[m].min() != yt[m].max(): diffs.append(auc(res[1][m], yt[m]) - auc(res[0][m], yt[m]))
        w(f"| {nom} | {100 * yt.mean():.0f} % | {auc(res[0], yt):.3f} | {auc(res[1], yt):.3f} | {auc(res[1], yt) - auc(res[0], yt):+.3f} [{np.percentile(diffs, 5):+.3f} ; {np.percentile(diffs, 95):+.3f}] |")
    if CONTROLE: w("_Contrôle : AUC non calculées (test non lu)._\n")

    # 4. H835 autres actifs
    w("\n## 4. H835 — Autres actifs et autres places\n")
    def charger1s(d):
        fs = sorted(glob.glob(os.path.join(d, "*.csv.gz"))); D = pd.concat([pd.read_csv(f, usecols=["t", "c"]) for f in fs]).drop_duplicates("t").sort_values("t")
        return D[D.t < RESERVE].set_index("t")["c"]
    btc = charger1s(os.path.join(sys.argv[2], "btc1s")); X_ = {k: charger1s(os.path.join(sys.argv[2], "autres", k)) for k in ("ETHUSDT", "SOLUSDT")}
    df = pd.DataFrame({"btc": btc, **{k: v for k, v in X_.items()}}).dropna(); lr = np.log(df).diff()
    tt = df.index.values; trb = tt < COUPE_BIN
    w("**(a) ETH et SOL contre BTC, Binance 1 s, 30 jours.** Corrélation simultanée ; avance = corrélation du rendement passé de l'actif sur k s avec le "
      "rendement futur de BTC sur k s ; R² hors échantillon (test 02.10 → 11.10) d'une régression BTC futur ~ BTC passé + actif passé, contre BTC passé seul.\n")
    w("| Actif | k | Corrélation simultanée | Avance (actif passé → BTC futur) | R² test BTC seul | R² test + actif | Gain de R² |\n|---|---|---|---|---|---|---|")
    for k_ in ("ETHUSDT", "SOLUSDT"):
        for k in (1, 2, 5, 10, 30):
            rb = np.log(df["btc"]).diff(k).values; rx = np.log(df[k_]).diff(k).values
            fut = np.roll(rb, -k); ok_ = np.isfinite(rb) & np.isfinite(rx) & np.isfinite(fut); ok_[-k:] = False
            simult = np.corrcoef(rb[ok_], rx[ok_])[0, 1]; avance = np.corrcoef(rx[ok_], fut[ok_])[0, 1]
            if CONTROLE: w(f"| {k_[:3]} | {k} s | {simult:+.3f} | — | — | — | — |"); continue
            def r2(cols):
                A = np.column_stack([np.ones(ok_.sum())] + [c[ok_] for c in cols]); m_tr = trb[ok_]; m_te = ~m_tr
                b = np.linalg.lstsq(A[m_tr], fut[ok_][m_tr], rcond=None)[0]; e = fut[ok_][m_te] - A[m_te] @ b
                return 1 - np.sum(e ** 2) / np.sum((fut[ok_][m_te] - fut[ok_][m_tr].mean()) ** 2)
            a1, a2 = r2([rb]), r2([rb, rx])
            w(f"| {k_[:3]} | {k} s | {simult:+.3f} | {avance:+.4f} | {100 * a1:+.3f} % | {100 * a2:+.3f} % | {100 * (a2 - a1):+.3f} pt |")
    w("\n**(b) Places BTC à Dublin (50 ms, heures de réception)** : corrélation du rendement passé de la place sur Δ avec le rendement futur de Binance spot sur Δ, test.\n")
    rows = []
    for st in cycles:
        if st < coupe and not CONTROLE: continue
        if st >= coupe and CONTROLE: continue
        try: R = json.load(gzip.open(cyc[st]["f"]))
        except Exception: continue
        for r in R.get("ex", []):
            v = [x[0] if (x and x[0]) else np.nan for x in r[1:]]; rows.append([r[0]] + v)
    EX = pd.DataFrame(rows, columns=["t"] + list(SRC)).sort_values("t").drop_duplicates("t")
    EX["t"] = (EX["t"] // 50) * 50; EX = EX.groupby("t").last().reindex(np.arange(EX.t.min(), EX.t.max() + 50, 50)).ffill(limit=20)
    w("| Place | Δ = 100 ms | 250 ms | 500 ms | 1 000 ms |\n|---|---|---|---|---|")
    for k in ("perp", "okx", "cb", "cl"):
        cells = []
        for dlt in (2, 5, 10, 20):
            a = np.log(EX[k]).diff(dlt).values; b_ = np.log(EX["bn"]).diff(dlt).shift(-dlt).values; m = np.isfinite(a) & np.isfinite(b_) & (a != 0)
            cells.append(f"{np.corrcoef(a[m], b_[m])[0, 1]:+.3f}" if m.sum() > 100 else "—")
        w(f"| {k} | " + " | ".join(cells) + " |")
    w("\nNasdaq, or, devises, CME : non disponibles à la seconde (déclarés, non estimés). Deribit : enregistré depuis le 12.10, pour plus tard.\n")

    # 5. modèles A/B/C/D
    w("## 5. Modèles A / B / C / D sur les mêmes décisions\n")
    D_ = []
    for st in cycles:
        if st not in Y: continue
        for rest in RESTES:
            m = m0(G, cyc, st, rest)
            if m is None: continue
            p, z, i = m
            if i < 620 or not (np.isfinite(G["bid"][i]) and np.isfinite(G["perp"][i]) and np.isfinite(G["okx"][i]) and np.isfinite(G["cb"][i])): continue
            B, C, Dd = feats(G, P, i)
            bnK = None
            D_.append(dict(st=st, rest=rest, i=i, p=p, z=z, y=Y[st], B=B, C=C, D=Dd))
    tr = [d for d in D_ if d["st"] < coupe]; te = [d for d in D_ if d["st"] >= coupe]
    w(f"Décisions : apprentissage {len(tr)}, test {len(te)} ({len({d['st'] for d in te})} cycles).\n")
    def X(Z, fam):
        r = []
        for d in Z:
            v = [lg(d["p"])]
            if fam >= 1: v += d["B"]
            if fam >= 2: v += d["C"]
            if fam >= 3: v += d["D"]
            r.append(v)
        return np.nan_to_num(np.array(r, float))
    MOD = {}
    for fam, nom in enumerate(("A règlement seul", "B + flux BTC", "C + liquidité L2", "D + autres places")):
        Xa = X(tr, fam); mu, sd = Xa.mean(0), Xa.std(0) + 1e-9; mu[0], sd[0] = 0, 1
        b = ajuster((Xa - mu) / sd, np.array([d["y"] for d in tr]), 2.0); MOD[nom] = (fam, b, mu, sd)
    if CONTROLE:
        w("_Contrôle : arrêt avant le test._\n"); open(SORTIE, "w").write("\n".join(o)); print("\n".join(o)); return
    PR = {nom: predire(b, (X(te, fam) - mu) / sd) for nom, (fam, b, mu, sd) in MOD.items()}
    yt = np.array([d["y"] for d in te]); gt = np.array([d["st"] for d in te]); noms = list(PR)
    for titre, m in (("Toutes les décisions", np.ones(len(te), bool)), ("Proches de 50 % (M0 entre 0,35 et 0,65)", np.array([0.35 <= d["p"] <= 0.65 for d in te])),
                     ("Marge faible |z| < 0,5", np.array([abs(d["z"]) < 0.5 for d in te]))):
        w(f"**{titre}** ({int(m.sum())} décisions, {len(set(gt[m]))} cycles)\n")
        w("| Modèle | Brier | Log loss | Précision | Apport marginal (Brier, modèle précédent − celui-ci) | IC 90 % | IC corrigé (9) |\n|---|---|---|---|---|---|---|")
        for k_, nom in enumerate(noms):
            e = brier(PR[nom][m], yt[m]); a_ = np.mean((PR[nom][m] > 0.5) == (yt[m] > 0.5))
            if k_ == 0: w(f"| {nom} | {e.mean():.4f} | {ll(PR[nom][m], yt[m]).mean():.4f} | {100 * a_:.1f} % | — | — | — |"); continue
            dlt = brier(PR[noms[k_ - 1]][m], yt[m]) - e; c1 = ic_g(gt[m], dlt); c2 = ic_g(gt[m], dlt, 0.10 / 9)
            w(f"| {nom} | {e.mean():.4f} | {ll(PR[nom][m], yt[m]).mean():.4f} | {100 * a_:.1f} % | {dlt.mean():+.5f} | [{c1[0]:+.5f} ; {c1[1]:+.5f}] | [{c2[0]:+.5f} ; {c2[1]:+.5f}] |")
        w("")
    w("**Calibration (test, toutes décisions)**\n\n| Probabilité annoncée | A : décisions / victoire | D : décisions / victoire |\n|---|---|---|")
    for lo, hi in ((0, .2), (.2, .4), (.4, .6), (.6, .8), (.8, 1.01)):
        a = (PR[noms[0]] >= lo) & (PR[noms[0]] < hi); d_ = (PR[noms[3]] >= lo) & (PR[noms[3]] < hi)
        w(f"| {lo:.1f}–{min(hi, 1):.1f} | {int(a.sum())} / {100 * yt[a].mean() if a.any() else float('nan'):.0f} % | {int(d_.sum())} / {100 * yt[d_].mean() if d_.any() else float('nan'):.0f} % |")

    # 6. P&L exécutable
    w("\n## 6. P&L exécutable (test) : achat 20 $ si avantage ≥ 0,05 après frais, exécution à 164 ms, résultat officiel\n")
    pnl = {nom: {} for nom in noms}; ncy = 0
    for st in sorted({d["st"] for d in te}):
        cy = LH.Cycle(cyc[st]["f"]); Z = sorted([(k, d) for k, d in enumerate(te) if d["st"] == st], key=lambda x: -x[1]["rest"])
        Tt = [st * 1000 + (300 - d["rest"]) * 1000 for _, d in Z]
        Et = cy.etats(Tt + [t + EXEC for t in Tt]); ncy += 1
        for nom in noms:
            pnl[nom][st] = 0.0
            for (k, d), t in zip(Z, Tt):
                L = Et[t]; done = False
                for X_side, pX in (("Up", PR[nom][k]), ("Down", 1 - PR[nom][k])):
                    v = LH.vendeurs(L, X_side)
                    if not v: continue
                    a0 = v[0][0] / 1000
                    if pX - a0 - fee(a0) < 0.05: continue
                    q = c = 0.0
                    for px, sz in LH.vendeurs(Et[t + EXEC], X_side):
                        if px > v[0][0]: break
                        pp = px / 1000; u = pp + fee(pp); kq = min(sz, (MISE - c) / u)
                        if kq <= 1e-9: break
                        q += kq; c += kq * u
                    gagne = (Y[st] == 1.0) == (X_side == "Up")
                    pnl[nom][st] = q * (1.0 if gagne else 0.0) - c; done = True; break
                if done: break
    w("| Modèle | Cycles avec achat | P&L ($) | Écart avec A ($) | IC 90 % (total, par cycles) |\n|---|---|---|---|---|")
    sts = sorted(pnl[noms[0]])
    for nom in noms:
        v = np.array([pnl[nom][s] for s in sts]); d = v - np.array([pnl[noms[0]][s] for s in sts]); c = ic_tot(sts, d)
        w(f"| {nom} | {sum(1 for s in sts if pnl[nom][s] != 0)} | {v.sum():+.0f} | {d.sum():+.0f} | " + ("—" if nom == noms[0] else f"[{c[0]:+.0f} ; {c[1]:+.0f}]") + " |")
    # cycles où le substitut Binance diffère
    dif = 0; tot = 0
    for st in sts:
        a, b_ = st + 240 - G["t0"], st + 300 - G["t0"]; K0 = np.nanmean(G["bn"][st - 60 - G["t0"]:st - G["t0"]]) if st - 60 >= G["t0"] else np.nan
        if np.isfinite(K0): tot += 1; dif += ((np.nanmean(G["bn"][a:b_]) > K0) != (Y[st] == 1.0))
    w(f"\nCycles du test où le substitut Binance diffère du résultat officiel : {dif} sur {tot} (tous les résultats ci-dessus utilisent l'officiel).\n")
    w(f"_Calcul : {time.time() - t_go:.0f} s._\n")
    open(SORTIE, "w").write("\n".join(o)); print("\n".join(o))


P_sd1 = None
if __name__ == "__main__":
    main()
