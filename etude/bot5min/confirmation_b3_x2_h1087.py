"""BOT95 — H1087 « confirmation de B3 et X2 sur des jours neufs ». Hors ligne, aucun ordre.
ORIGINE : deux règles déjà figées, validées sur 01–08.10 et qui tournent déjà comme fantômes :
  B3 (etude/bot5min/biais_fin_cycle_h1084.py) : 20 à 60 s restantes, favori 0,90–0,98 au signal, distance zf ≥ 3 σ → acheter le favori 10 $.
     Validation 01–08.10 : 169 achats, 168 gagnés, +42 $.
  X2 (etude/bot5min/d_un_cycle_a_l_autre_h1083.py) : à t = 10 s, r30 ≤ −1,018 ET r5 < 0 → acheter Up 10 $.
     Validation 01–08.10 : 305 achats, +352 $, +11,6 %, IC Bonferroni contenant 0.
  On les rejoue SANS AUCUN CHANGEMENT sur des jours NEUFS, jamais lus par leurs études : 09.10, 10.10, 11.10, 12.10, 13.10
  (marchés BTC 5 min dont le début est dans [09.10 00:00 ; 14.10 00:00[ UTC).
  CE SCRIPT EST FIGÉ ET POUSSÉ AVANT TOUT CALCUL SUR CES JOURS. Il est lancé UNE seule fois.
DÉFINITIONS (copiées de H1084 / H1083, seuils inchangés) :
  B3 : instants t = 240, 245, …, 290 s ; prix du marché à t = médiane des achats (en prix Up) dans (t−6, t], au moins 2 achats ;
     favori = côté ≥ 0,5 ; fp = prix du favori ; reste = 300 − t ∈ [20 ; 60] ; fp ∈ [0,90 ; 0,98] ; zf ≥ 3. K = moyenne c[début−60, début) ;
     moyenne finale attendue = (Σ c[début+240 .. i] + n·c[i]) / 60 avec n = 300 − t − 1 ; écart-type = σ1s(1 h)·√(n(n+1)(2n+1)/6)/60 ;
     zf = z compté dans le sens du favori. Prix payé = médiane des achats du favori dans (t, t+6] (comme le code H1084) ; gardé si dans
     ]0,01 ; 0,99[ ; premier instant du cycle qui déclenche ; prix PESSIMISTE = max(prix payé, fp).
  X2 : t = 10 s ; au moins 5 achats dans [−10 ; 70] s du cycle ; prix du marché à 10 s = médiane des achats dans (4, 10], au moins 2 ;
     r30 = (c[début] − c[début−1800]) / (σ1s(1 h)·√1800) ≤ −1,018 ; r5 = (c[début] − c[début−300]) / (σ1s(1 h)·√300) < 0 ;
     prix payé = médiane des achats Up dans (10, 16] ; gardé si dans ]0,01 ; 0,99[. Cycles comptés = cycles ayant au moins une ligne
     (t = 10, 20 ou 30 s avec ≥ 2 achats dans la fenêtre), comme dans H1083. H1083 exigeait aussi 24 h d'historique BTC (pour une
     variable v1h24 que X2 n'utilise pas) : seuls σ1s(1 h), r5 et r30 sont nécessaires ici.
  Frais 0,07·p·(1−p) ; billet gardé jusqu'au règlement ; 10 $ par achat ; un achat au plus par cycle et par règle.
CRITÈRE (pour CHAQUE règle, prix observé, total des 5 jours) : ROI > 0 ET intervalle de confiance à 90 % du P&L entièrement > 0.
  IC = bootstrap par cycles (tous les cycles retenus, 0 $ pour un cycle sans achat), 10 000 tirages, percentiles 5 et 95, graine 1087.
  Deux règles, chacune jugée seule (pas de correction pour essais multiples ; le rapport le signale). Aucun changement de fantôme.
DONNÉES BTC (reprises de H1086, fonction serie_btc importée telle quelle) : bougies Binance 1 s (btc1s.npz) jusqu'au 11.10 23:59:59 ;
  12.10 et 13.10 : colonne binance_spot des enregistrements du bot (rec_BTC / sig_BTC), dernière valeur de chaque seconde, reportée
  au plus 2 s, sinon manquante. Les études d'origine avaient une série complète ; ici :
  TROUS : σ1s(1 h) = racine de la moyenne des carrés des écarts 1 s DISPONIBLES sur les 3 600 s, au moins 1 800 exigés (comme H1086) ;
  les prix ponctuels (c[début], c[début−300], c[début−1800], c[i]) et les moyennes (K sur 60 s, partie connue de la moyenne finale)
  doivent être complets. Sinon : pour X2 le cycle est écarté ; pour B3 l'instant t n'est pas évaluable, et le cycle est écarté si
  K ou un des 11 instants manque (on ne veut pas d'un cycle à moitié lu). Nombres de cycles écartés publiés.
RÉSULTATS DES MARCHÉS : champ « resultat » du fichier polytrades ; s'il manque, gagnant officiel de bot95/officiels.json ; sinon le cycle
  est écarté (nombre publié).
Usage : python3 etude/bot5min/confirmation_b3_x2_h1087.py btc1s.npz polytrades_2026-10-{09..13}.json.gz"""
import sys, json, gzip, os, numpy as np, pandas as pd
ICI = os.path.dirname(os.path.abspath(__file__)); RACINE = os.path.dirname(os.path.dirname(ICI)); sys.path.insert(0, ICI)
from confirmation_gros_sens_btc_h1086 import serie_btc          # même série BTC que H1086 (npz puis enregistrements du bot)
DEBUT = 1791504000; FIN = 1791936000                            # 09.10 / 14.10 00:00 UTC
JOURS = {DEBUT + k * 86400: f"{9 + k:02d}.10" for k in range(5)}
fee = lambda p: 0.07 * p * (1 - p); TT = list(range(240, 295, 5)); Q20_R30 = -1.018

def construire(npz, fichiers):
    t0, c = serie_btc(npz); O = json.load(open(os.path.join(RACINE, "bot95", "officiels.json")))
    ok = np.isfinite(c); cz = np.where(ok, c, 0.0)
    Cc = np.concatenate([[0], np.cumsum(cz)]); Cn = np.concatenate([[0], np.cumsum(ok)])
    d = np.diff(c, prepend=np.nan); fd = np.isfinite(d)
    Cd2 = np.concatenate([[0], np.cumsum(np.where(fd, d * d, 0.0))]); Nd = np.concatenate([[0], np.cumsum(fd)])
    def sd(i, w):
        nn = Nd[i + 1] - Nd[i + 1 - w]
        return np.sqrt((Cd2[i + 1] - Cd2[i + 1 - w]) / nn) if nn >= w / 2 else np.nan
    plein = lambda a, b: Cn[b] - Cn[a] == b - a                 # c[a..b[ complet
    B, X = [], []; cyc_b, cyc_x = {}, {}; ecart = dict(sans_resultat=0, b3_btc=0, x2_btc=0, x2_moins_5_achats=0, x2_sans_ligne=0)
    for f in sorted(fichiers):
        for st_, m in json.load(gzip.open(f))["marches"].items():
            st = int(st_); r = m.get("resultat") or {}
            if not (DEBUT <= st < FIN): continue
            if r.get("Up") in (0.0, 1.0): upw = int(r["Up"] == 1.0)
            elif (O.get(f"BTC:{st}") or {}).get("gagnant") in ("Up", "Down"): upw = int(O[f"BTC:{st}"]["gagnant"] == "Up")
            else: ecart["sans_resultat"] += 1; continue
            jour = JOURS[DEBUT + (st - DEBUT) // 86400 * 86400]; s0 = st - t0
            A = np.array([(x[0] - st, x[4] if x[3] == "Up" else 1 - x[4], 1 if x[3] == "Up" else 0, x[4]) for x in m["trades"]
                          if x[0] is not None and x[4] and 0 < x[4] < 1 and x[2] == "BUY"], float).reshape(-1, 4)
            # ---- B3 (H1084) ----
            T = A[(A[:, 0] >= 228) & (A[:, 0] < 300)]; rows = []; bon = plein(s0 - 60, s0)
            if bon:
                K = (Cc[s0] - Cc[s0 - 60]) / 60
                for tt in TT:
                    i = s0 + tt; s1 = sd(i, 3600); n = 300 - tt - 1
                    if not (np.isfinite(s1) and plein(s0 + 240, i + 1)): bon = False; break
                    EA = (Cc[i + 1] - Cc[s0 + 240] + n * c[i]) / 60; zz = (EA - K) / (s1 * np.sqrt(n * (n + 1) * (2 * n + 1) / 6) / 60)
                    w = T[(T[:, 0] > tt - 6) & (T[:, 0] <= tt)]; nx = T[(T[:, 0] > tt) & (T[:, 0] <= tt + 6)]
                    pU = nx[nx[:, 2] == 1][:, 3]; pD = nx[nx[:, 2] == 0][:, 3]
                    rows.append(dict(st=st, jour=jour, t=tt, upw=upw, pu=np.median(w[:, 1]) if len(w) >= 2 else np.nan,
                                     pUp=np.median(pU) if len(pU) else np.nan, pDown=np.median(pD) if len(pD) else np.nan, z=zz))
            if bon: cyc_b[st] = jour; B += rows
            else: ecart["b3_btc"] += 1
            # ---- X2 (H1083) ----
            T = A[(A[:, 0] >= -10) & (A[:, 0] <= 70)]
            if len(T) < 5: ecart["x2_moins_5_achats"] += 1; continue
            s1h = sd(s0, 3600)
            if not (np.isfinite(s1h) and all(np.isfinite(c[k]) for k in (s0, s0 - 300, s0 - 1800))): ecart["x2_btc"] += 1; continue
            if not any((((T[:, 0] > tt - 6) & (T[:, 0] <= tt)).sum() >= 2) for tt in (10, 20, 30)): ecart["x2_sans_ligne"] += 1; continue
            cyc_x[st] = jour
            w = T[(T[:, 0] > 4) & (T[:, 0] <= 10)]
            if len(w) < 2: continue
            nx = T[(T[:, 0] > 10) & (T[:, 0] <= 16)]; pU = nx[nx[:, 2] == 1][:, 3]
            X.append(dict(st=st, jour=jour, upw=upw, pu=np.median(w[:, 1]), pUp=np.median(pU) if len(pU) else np.nan,
                          r5=(c[s0] - c[s0 - 300]) / (s1h * np.sqrt(300)), r30=(c[s0] - c[s0 - 1800]) / (s1h * np.sqrt(1800))))
    D = pd.DataFrame(B); D = D[D.pu.notna()].copy()
    D["fav_up"] = D.pu >= .5; D["fp"] = np.where(D.fav_up, D.pu, 1 - D.pu); D["fw"] = np.where(D.fav_up, D.upw, 1 - D.upw)
    D["pf"] = np.where(D.fav_up, D.pUp, D.pDown); D["zf"] = np.where(D.fav_up, D.z, -D.z); D["left"] = 300 - D.t
    return D, pd.DataFrame(X), cyc_b, cyc_x, ecart

def achats_b3(D):
    x = D[D.fp.between(.90, .98) & D.left.between(20, 60) & (D.zf >= 3)].copy(); x["px"] = x.pf; x["w"] = x.fw
    return x[np.isfinite(x.px) & (x.px > 0.01) & (x.px < 0.99)].sort_values(["st", "t"]).groupby("st").head(1)

def achats_x2(X):
    x = X[(X.r30 <= Q20_R30) & (X.r5 < 0)].copy(); x["px"] = x.pUp; x["w"] = x.upw
    return x[np.isfinite(x.px) & (x.px > 0.01) & (x.px < 0.99)]

def bilan(x, nc, rng):
    pnl = (x.w / (x.px + fee(x.px)) - 1).values * 10
    vv = np.concatenate([pnl, np.zeros(max(nc - len(x), 0))]); bs = vv[rng.integers(0, len(vv), (10000, len(vv)))].sum(1)
    return dict(cycles=int(nc), achats=int(len(x)), gagnes=int(x.w.sum()), prix=float(x.px.mean()) if len(x) else None,
                roi=float(pnl.mean() / 10) if len(x) else None, pnl=float(vv.sum()), ic90=np.percentile(bs, [5, 95]).tolist())

if __name__ == "__main__":
    D, X, cyc_b, cyc_x, ecart = construire(sys.argv[1], sys.argv[2:]); RNG = np.random.default_rng(1087)
    out = {"cycles_b3": len(cyc_b), "cycles_x2": len(cyc_x), "ecartes": ecart,
           "cycles_par_jour_b3": {j: sum(v == j for v in cyc_b.values()) for j in JOURS.values()},
           "cycles_par_jour_x2": {j: sum(v == j for v in cyc_x.values()) for j in JOURS.values()}, "regles": {}}
    xb = achats_b3(D); xp = xb.copy(); xp["px"] = np.maximum(xp.px, xp.fp); xx = achats_x2(X)
    for nom, x, cy in (("B3", xb, cyc_b), ("B3 prix pessimiste", xp, cyc_b), ("X2", xx, cyc_x)):
        R = {"total": bilan(x, len(cy), RNG)}
        for jr in JOURS.values(): R[jr] = bilan(x[x.jour == jr], sum(v == jr for v in cy.values()), RNG)
        out["regles"][nom] = R
    for nom in ("B3", "X2"):
        P = out["regles"][nom]["total"]; out["regles"][nom]["verdict"] = "CONFIRMÉ" if (P["roi"] or 0) > 0 and P["ic90"][0] > 0 else "NON CONFIRMÉ"
    s = json.dumps(out, ensure_ascii=False, indent=1, default=str); print(s)
    open(os.path.join(ICI, "confirmation_b3_x2_h1087.json"), "w").write(s)
