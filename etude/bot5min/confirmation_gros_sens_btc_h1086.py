"""BOT95 — H1086 « confirmation : gros achat dans le sens du BTC ». Hors ligne, aucun ordre.
ORIGINE : piste vue APRÈS la validation de H1085 (etude/bot5min/grosses_transactions_h1085.py). Un gros achat preneur (≥ 500 $) fait
  dans le sens du mouvement BTC des 10 dernières secondes gagnait, à NOTRE prix, +0,3 pt de plus que ce prix en exploration (12.09–30.09,
  IC contenant 0) et +1,3 pt en validation (01.10–08.10, IC 90 % [+0,5 ; +2,2]). Pitch a dit « go » : on la teste sur des jours NEUFS,
  jamais lus par aucune étude de gros achats : 09.10, 10.10, 11.10, 12.10 et 13.10 (marchés dont le début est dans [09.10 00:00 ; 14.10 00:00[ UTC).
  CE SCRIPT EST FIGÉ ET POUSSÉ AVANT TOUT CALCUL SUR CES JOURS. Il est lancé UNE seule fois.
DÉFINITIONS (copiées de H1085, sans changement) :
  preneur = 1re ligne de chaque transaction (même hash), gardée si c'est un achat ; rafale = achats preneur d'un même portefeuille sur la
  même issue, écart ≤ 3 s entre deux achats, rafale ≤ 5 s ; événement = seconde te ∈ [0 ; 300[ où le cumul Σ prix × parts franchit 500 $.
  b10 = (c[te−1] − c[te−11]) / (σ1s(1 h)·√10), compté dans le sens du gros (σ1s = racine de la moyenne des carrés des écarts 1 s sur
  les 3 600 s qui finissent à te). « Avec BTC » = b10 > 1 (classe ]1 ; 99] de H1085) ; « contre BTC » = b10 ≤ −1 (classe ]−99 ; −1]).
  Notre prix = médiane des achats (toutes lignes BUY) de l'issue du gros dans ]te+1 ; te+6] ; gardé si dans [0,01 ; 0,99] ;
  frais 0,07·p·(1−p) ; gardé jusqu'au règlement ; 10 $ par achat ; prix pessimiste = max(notre prix, prix de ce côté dans ]te−6 ; te−1]).
RÈGLE PRIMAIRE (une seule) : SUIVRE le PREMIER gros achat ≥ 500 $ du cycle qui est « avec BTC » (b10 > 1) et dont notre prix est dans
  [0,01 ; 0,99] ; un seul achat par cycle.
  SECONDAIRE (information, pas critère) : même règle, en ne gardant que les événements où notre prix ≤ 0,95 (premier tel événement du cycle).
  CONTRÔLE (information) : la même chose pour les gros achats « contre BTC » (b10 ≤ −1), suivis.
CRITÈRE (règle primaire, prix observé) : ROI > 0 ET intervalle de confiance à 90 % du P&L entièrement > 0 sur les 5 jours neufs.
  IC = bootstrap par cycles (tous les cycles retenus, 0 $ pour un cycle sans achat), 10 000 tirages, percentiles 5 et 95, graine 1086.
  Une seule règle primaire → pas de correction pour essais multiples. Aucun fantôme sans accord de Pitch.
DONNÉES BTC : H1085 utilisait les bougies 1 s BTCUSDT au comptant Binance (data.binance.vision). Le téléchargement direct est bloqué
  dans cet environnement. On utilise donc : (1) le fichier btc1s.npz (mêmes bougies Binance, déjà téléchargées) jusqu'au 11.10 23:59:59 ;
  (2) au-delà (12.10 et 13.10), la colonne binance_spot enregistrée par le bot (bot95/donnees/<jour>/rec_BTC.json.gz et sig_BTC.json.gz) :
  dernière valeur relevée dans chaque seconde, reportée au plus 2 s (âge < 3 s), sinon manquante. Sur 09–11.10 cette colonne égale les
  bougies Binance (écart médian 0, 90e centile 0,01 $). σ1s = moyenne des carrés des écarts 1 s disponibles (≥ 1 800 sur 3 600 exigés).
  Un événement dont b10 n'est pas calculable est écarté (nombre publié).
RÉSULTATS DES MARCHÉS : champ « resultat » du fichier polytrades ; s'il manque (fin du 12.10, fichier capturé avant le règlement), le
  gagnant officiel de bot95/officiels.json (vérifié identique sur les 225 marchés du 12.10 où les deux existent).
Usage : python3 etude/bot5min/confirmation_gros_sens_btc_h1086.py btc1s.npz polytrades_2026-10-{09..13}.json.gz"""
import sys, json, gzip, os, glob, numpy as np, pandas as pd
ICI = os.path.dirname(os.path.abspath(__file__)); RACINE = os.path.dirname(os.path.dirname(ICI))
DEBUT = 1791504000; FIN = 1791936000; FIN_NPZ = 1791763200            # 09.10 / 14.10 / 12.10 00:00 UTC
fee = lambda p: 0.07 * p * (1 - p); SEUIL = 500; GAP = 3; SPAN = 5
JOURS = {DEBUT + k * 86400: f"{9 + k:02d}.10" for k in range(5)}

def serie_btc(npz):
    t_deb = DEBUT - 3700; n = FIN + 400 - t_deb; c = np.full(n, np.nan)
    z = np.load(npz); zt = z["t"].astype(np.int64); zc = z["c"].astype(float)
    m = (zt >= t_deb) & (zt < min(FIN_NPZ, FIN + 400)); c[zt[m] - t_deb] = zc[m]
    vu = {}
    for jour in ("2026-10-12", "2026-10-13", "2026-10-14"):
        for kind in ("rec", "sig"):
            f = os.path.join(RACINE, "bot95", "donnees", jour, f"{kind}_BTC.json.gz")
            if not os.path.exists(f): continue
            for doc in json.load(gzip.open(f, "rt")).values():
                i = doc["colonnes"].index("binance_spot")
                for r in doc["lignes"]:
                    if r[i] and r[0] >= FIN_NPZ: vu[float(r[0])] = r[i]
    T = np.array(sorted(vu)); V = np.array([vu[x] for x in T])
    s = np.arange(FIN_NPZ, FIN + 400); k = np.searchsorted(T, s + 1, side="left") - 1     # dernière valeur avec t < s+1
    ok = (k >= 0) & (s + 1 - T[np.maximum(k, 0)] <= 3)
    c[s - t_deb] = np.where(ok, V[np.maximum(k, 0)], np.nan)
    return t_deb, c

def lire(f, O):
    out = {}
    for st_, m in json.load(gzip.open(f))["marches"].items():
        st = int(st_); r = m.get("resultat") or {}
        if not (DEBUT <= st < FIN): continue
        if r.get("Up") in (0.0, 1.0): upw = int(r["Up"] == 1.0)
        elif (O.get(f"BTC:{st}") or {}).get("gagnant") in ("Up", "Down"): upw = int(O[f"BTC:{st}"]["gagnant"] == "Up")
        else: continue
        vu = set(); wid = {}; rows = []
        for x in m["trades"]:
            if x[0] is None or not x[4] or not (0 < x[4] < 1) or x[5] is None: continue
            premier = x[6] not in vu; vu.add(x[6])
            rows.append((x[0] - st, wid.setdefault(x[1], len(wid)), x[2] == "BUY", x[3] == "Up", x[4], x[5], premier))
        out[st] = (upw, np.array(rows, float).reshape(-1, 7))
    return out

def construire(npz, fichiers):
    t0, c = serie_btc(npz); O = json.load(open(os.path.join(RACINE, "bot95", "officiels.json")))
    d = np.diff(c, prepend=np.nan); d2 = np.where(np.isfinite(d), d * d, 0.0); nd = np.isfinite(d).astype(float)
    S2 = np.concatenate([[0], np.cumsum(d2)]); N2 = np.concatenate([[0], np.cumsum(nd)])
    def sd(i, w):
        nn = N2[i + 1] - N2[i + 1 - w]
        return np.sqrt((S2[i + 1] - S2[i + 1 - w]) / nn) if nn >= w / 2 else np.nan
    ev = []; cyc = {}; sans_btc = 0
    for f in sorted(fichiers):
        for st, (upw, A) in lire(f, O).items():
            s0 = st - t0; cyc[st] = JOURS[DEBUT + (st - DEBUT) // 86400 * 86400]
            A = A[np.argsort(A[:, 0], kind="stable")]; B = A[A[:, 2] == 1]; tb = B[:, 0]; pu = np.where(B[:, 3] == 1, B[:, 4], 1 - B[:, 4])
            def med(lo, hi, oc=None):
                m = (tb > lo) & (tb <= hi)
                if oc is None: return np.median(pu[m]) if m.any() else np.nan
                m &= B[:, 3] == oc; return np.median(B[m, 4]) if m.any() else np.nan
            K = A[(A[:, 6] == 1) & (A[:, 2] == 1) & (A[:, 0] >= 0) & (A[:, 0] < 300)]
            uk, inv = np.unique(K[:, 1] * 2 + K[:, 3], return_inverse=True); tot = np.bincount(inv, weights=K[:, 4] * K[:, 5])
            for kk in np.where(tot >= SEUIL)[0]:
                g = K[inv == kk]; X = int(g[0, 3]); tt = g[:, 0]; nn = g[:, 4] * g[:, 5]; ss = g[:, 5]; sg = 1 if X else -1; i = 0
                cote = lambda v: (v if X else 1 - v) if np.isfinite(v) else np.nan
                while i < len(tt):
                    j = i; cum = sh = 0; fait = False
                    while j < len(tt) and (j == i or (tt[j] - tt[j - 1] <= GAP and tt[j] - tt[i] <= SPAN)):
                        cum += nn[j]; sh += ss[j]
                        if cum >= SEUIL and not fait:
                            fait = True; te = int(tt[j]); i0 = s0 + te
                            b10 = sg * (c[i0 - 1] - c[i0 - 11]) / (sd(i0, 3600) * np.sqrt(10))
                            if not np.isfinite(b10): sans_btc += 1
                            ev.append(dict(st=st, jour=cyc[st], te=te, X=X, xwin=upw if X else 1 - upw, pbig=cum / sh,
                                           pav=cote(med(te - 6, te - 1)), pfol=med(te + 1, te + 6, X), b10=b10))
                        j += 1
                    i = j
    return pd.DataFrame(ev), cyc, sans_btc

def bilan(x, cyc_ids, rng, prix="observe"):
    px = x.pfol if prix == "observe" else np.maximum(x.pfol, x.pav.fillna(0))
    pnl = (x.xwin / (px + fee(px)) - 1).values * 10
    vv = np.concatenate([pnl, np.zeros(len(cyc_ids) - len(x))])
    bs = vv[rng.integers(0, len(vv), (10000, len(vv)))].sum(1)
    return dict(cycles=len(cyc_ids), achats=int(len(x)), gagnes=int(x.xwin.sum()), taux=float(x.xwin.mean()) if len(x) else None,
                prix=float(px.mean()) if len(x) else None, roi=float(pnl.mean() / 10) if len(x) else None, pnl=float(vv.sum()),
                ic90=np.percentile(bs, [5, 95]).tolist(), ecart_pts=float((x.xwin - px).mean() * 100) if len(x) else None)

if __name__ == "__main__":
    E, cyc, sans_btc = construire(sys.argv[1], sys.argv[2:]); RNG = np.random.default_rng(1086)
    E = E.reset_index(drop=True); E["ordre"] = np.arange(len(E))
    out = {"cycles": len(cyc), "cycles_par_jour": {j: sum(v == j for v in cyc.values()) for j in JOURS.values()},
           "evenements_500": int(len(E)), "evenements_sans_btc": int(sans_btc), "regles": {}}
    def choisir(cond, plafond):
        x = E[cond & E.pfol.between(.01, .99)]
        if plafond: x = x[x.pfol <= .95]
        return x.sort_values(["st", "te", "ordre"], kind="stable").groupby("st").head(1)
    for nom, cond in (("avec BTC (b10 > 1)", E.b10 > 1), ("contre BTC (b10 ≤ −1)", E.b10 <= -1)):
        for plafond in (False, True):
            cle = nom + (" — prix ≤ 0,95" if plafond else ""); x = choisir(cond, plafond); R = {}
            R["total"] = bilan(x, list(cyc), RNG); R["total_pessimiste"] = bilan(x, list(cyc), RNG, "pessimiste")
            for jr in JOURS.values():
                R[jr] = bilan(x[x.jour == jr], [s for s, v in cyc.items() if v == jr], RNG)
            out["regles"][cle] = R
    P = out["regles"]["avec BTC (b10 > 1)"]["total"]
    out["verdict"] = "CONFIRMÉ" if (P["roi"] or 0) > 0 and P["ic90"][0] > 0 else "NON CONFIRMÉ"
    s = json.dumps(out, ensure_ascii=False, indent=1, default=str); print(s)
    open(os.path.join(ICI, "confirmation_gros_sens_btc_h1086.json"), "w").write(s)
