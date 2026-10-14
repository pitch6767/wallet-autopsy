"""BOT95 — H1089 « ailleurs » : les marchés crypto Up/Down Polymarket PLUS LONGS (BTC 15 min, BTC horaire) sont-ils moins efficaces
que le BTC 5 min (biais favori-billet, calibration en fin de fenêtre, prix mal placé par rapport à la distance au prix à battre) ?
Hors ligne, aucun ordre. Données : transactions publiques Polymarket (data-api, téléchargées par .github/workflows/histo_autres_marches.yml,
branches pa-btc-15m-AAAA-MM-JJ / pa-btc-1h-AAAA-MM-JJ ; 5 min : polytrades_AAAA-MM-JJ.json.gz), Binance BTCUSDT 1 s (btc1s.npz, 12.09–11.10).
PÉRIODE : 29.09 → 11.10.2026 (13 jours). EXPLORATION 29.09–06.10 (8 jours), VALIDATION 07.10–11.10 (5 jours), lue UNE seule fois.
RÈGLEMENT (descriptions Polymarket lues le 14.10) :
  15 min et 5 min : moyenne (TWAP) Chainlink BTC/USD 60 s à la fin ≥ celle du début (priceToBeat). Approximation Binance :
    K = moyenne c[début−60, début) ; F = moyenne c[fin−60, fin).
  horaire (bitcoin-up-or-down-<mois>-<jour>-<année>-<h>am|pm-et) : bougie 1 h Binance BTC/USDT, Up si clôture ≥ ouverture.
    Approximation : O = c[début−1], F = c[fin−1].
CONVENTIONS (reprises de H1084 / H1067) : prix du marché à t = médiane des achats (en prix Up) dans (t−6, t], au moins 2 ; favori = côté ≥ 0,5.
  Prix PAYÉ = médiane des achats du côté acheté dans (t+1, t+6] ; frais preneur 0,07·p·(1−p) (feeSchedule rate 0,07 takerOnly lu sur
  les marchés 15 min ; même taux appliqué à l'horaire par prudence). Prix gardé seulement dans ]0,01 ; 0,99[ ; un achat par marché et par règle
  (premier instant qui déclenche) ; 10 $ par achat ; tous les marchés de la période comptent (0 $ s'il n'y a pas d'achat). Prix PESSIMISTE =
  max(prix du signal, prix payé).
DISTANCE z : (F attendu − K) / écart-type de F, σ1s sur 1 h Binance ; zf = z dans le sens du favori ; Φ(zf) = probabilité « modèle ».
Instants : pas = durée/60 (5 s, 15 s, 60 s) + toutes les 5 s dans les 60 dernières secondes.
Usage : python3 etude/bot5min/autres_marches_h1089.py btc1s.npz TYPE fichiers... [--validation]   (TYPE = 5m | 15m | 1h)
"""
import sys, json, gzip, os, numpy as np, pandas as pd
from math import erf, sqrt
ICI = os.path.dirname(os.path.abspath(__file__))
DEB = 1790640000; FIN_EXPLO = 1791331200; FIN = 1791763200     # 29.09 / 07.10 / 12.10 00:00 UTC
fee = lambda p: 0.07 * p * (1 - p); PHI = np.vectorize(lambda x: 0.5 * (1 + erf(x / sqrt(2))))
DUREE = {"5m": 300, "15m": 900, "1h": 3600}


def instants(L):
    pas = L // 60
    return sorted(set(range(pas, L, pas)) | set(range(L - 60, L, 5)))


def construire(npz, typ, fichiers):
    L = DUREE[typ]; TT = instants(L)
    z = np.load(npz); t0 = int(z["t"][0]); c = z["c"].astype(float)
    Cc = np.concatenate([[0], np.cumsum(c)]); Cd2 = np.concatenate([[0], np.cumsum(np.diff(c, prepend=c[0]) ** 2)])
    sd = lambda i, w: np.sqrt((Cd2[i + 1] - Cd2[i + 1 - w]) / w)
    # écart-type (en unités de σ1s) du règlement vu de t, pour la moyenne des 60 dernières secondes
    def fac(tt):
        if typ == "1h": return sqrt(max(L - 1 - tt, 0.25))
        a = max(L - 60, tt + 1); n = L - a
        if n <= 0: return 0.5
        d = np.arange(a - tt, a - tt + n, dtype=float)
        return sqrt(float((d * (2 * (n - 1 - np.arange(n)) + 1)).sum())) / 60
    FAC = {tt: fac(tt) for tt in TT}
    rows, marches = [], []
    for f in sorted(fichiers):
        for st_, m in json.load(gzip.open(f))["marches"].items():
            st = int(st_); r = m.get("resultat") or {}
            if r.get("Up") not in (0.0, 1.0) or not (DEB <= st and st + L <= FIN): continue
            s0 = st - t0
            if s0 < 3700 or s0 + L >= len(c): continue
            upw = int(r["Up"] == 1.0)
            if typ == "1h": K = c[s0 - 1]; Fb = c[s0 + L - 1]
            else: K = (Cc[s0] - Cc[s0 - 60]) / 60; Fb = (Cc[s0 + L] - Cc[s0 + L - 60]) / 60
            TR = [x for x in m["trades"] if x[0] is not None and x[4] and 0 < x[4] < 1]
            ins = [x for x in TR if 0 <= x[0] - st < L]
            marches.append(dict(st=st, upw=upw, binance_ok=int((Fb >= K) == bool(upw)), n_tr=len(TR), n_fen=len(ins),
                                usd_fen=float(sum(x[4] * x[5] for x in ins if x[5])), usd_tot=float(sum(x[4] * x[5] for x in TR if x[5])),
                                n_fin=sum(1 for x in ins if x[0] - st >= 0.9 * L), tronque=bool(m.get("tronque")) or len(m["trades"]) >= 9900,
                                wallets=len(set(x[1] for x in ins))))
            T = np.array([(x[0] - st, x[4] if x[3] == "Up" else 1 - x[4], 1 if x[3] == "Up" else 0, x[4]) for x in TR
                          if x[2] == "BUY" and -10 <= x[0] - st < L], float).reshape(-1, 4)
            for tt in TT:
                i = s0 + tt; s1 = sd(i, 3600)
                if typ == "1h": EA = c[i]
                else:
                    kn = max(0, min(tt + 1, L) - (L - 60)); nu = 60 - kn
                    EA = ((Cc[i + 1] - Cc[s0 + L - 60]) if kn else 0) / 60 + nu * c[i] / 60
                zz = (EA - K) / (s1 * FAC[tt]); m30 = (c[i] - c[i - 30]) / (s1 * sqrt(30))
                w = T[(T[:, 0] > tt - 6) & (T[:, 0] <= tt)]; nx = T[(T[:, 0] > tt) & (T[:, 0] <= tt + 6)]
                w30 = T[(T[:, 0] > tt - 36) & (T[:, 0] <= tt - 30)]
                pU = nx[nx[:, 2] == 1][:, 3]; pD = nx[nx[:, 2] == 0][:, 3]
                rows.append(dict(st=st, t=tt, upw=upw, pu=np.median(w[:, 1]) if len(w) >= 2 else np.nan,
                                 pu30=np.median(w30[:, 1]) if len(w30) >= 2 else np.nan,
                                 pUp=np.median(pU) if len(pU) else np.nan, pDown=np.median(pD) if len(pD) else np.nan, z=zz, m30=m30))
    D = pd.DataFrame(rows); M = pd.DataFrame(marches)
    for X in (D, M): X["part"] = np.where(X.st < FIN_EXPLO, "exploration", "validation")
    D["fav_up"] = D.pu >= .5; D["fp"] = np.where(D.fav_up, D.pu, 1 - D.pu); D["fw"] = np.where(D.fav_up, D.upw, 1 - D.upw)
    D["pf"] = np.where(D.fav_up, D.pUp, D.pDown); D["pt"] = np.where(D.fav_up, D.pDown, D.pUp)
    D["zf"] = np.where(D.fav_up, D.z, -D.z); D["m30f"] = np.where(D.fav_up, D.m30, -D.m30)
    D["dp30f"] = np.where(D.fav_up, D.pu - D.pu30, D.pu30 - D.pu)       # mouvement du prix du favori sur 30 s
    D["reste"] = (L - D.t) / L; D["phi"] = PHI(D.zf.clip(-8, 8))
    return D[D.pu.notna()].copy(), D, M


def calibration(P, rng, nb=1000):
    """Écart fréquence − prix par tranche de temps restant et de prix, IC 90 % par marchés."""
    out = []
    P = P.assign(rb=pd.cut(P.reste, [0, .05, .15, .35, .65, 1.0]), pb=pd.cut(P.fp, [.5, .6, .7, .8, .9, .95, .98, .995]))
    for (rb, pb), g in P.groupby(["rb", "pb"], observed=True):
        if g.st.nunique() < 15: continue
        a = g.groupby("st").apply(lambda x: pd.Series({"d": (x.fw - x.fp).sum(), "n": len(x), "dm": (x.fw - x.phi).sum()}), include_groups=False)
        idx = rng.integers(0, len(a), (nb, len(a))); dv, nv = a.d.values, a.n.values
        bs = dv[idx].sum(1) / nv[idx].sum(1)
        out.append(dict(reste=str(rb), tranche=str(pb), lignes=int(len(g)), marches=int(len(a)), prix=round(float(g.fp.mean()), 4),
                        freq=round(float(g.fw.mean()), 4), ecart=round(float(dv.sum() / nv.sum()), 4), ic90=[round(float(x), 4) for x in np.percentile(bs, [5, 95])],
                        phi=round(float(g.phi.mean()), 4)))
    return out


def resume_efficacite(P, rng, nb=500):
    """Brier du marché vs Brier du modèle Binance, et pente logistique (prix → fréquence), par tranche de temps restant."""
    out = []
    P = P.assign(rb=pd.cut(P.reste, [0, .05, .15, .35, .65, 1.0]))
    for rb, g in P.groupby("rb", observed=True):
        y = g.upw.values; p = g.pu.clip(.005, .995).values; ph = PHI(g.z.clip(-8, 8)).clip(.005, .995)
        bm = float(((p - y) ** 2).mean()); bz = float(((ph - y) ** 2).mean())
        lp = np.log(p / (1 - p)); lz = np.log(ph / (1 - ph))
        # régression logistique y ~ a + b·logit(prix) + c·logit(modèle) (Newton, 15 pas)
        X = np.column_stack([np.ones_like(lp), lp, lz]); beta = np.zeros(3)
        for _ in range(25):
            q = 1 / (1 + np.exp(-X @ beta)); W = q * (1 - q) + 1e-9
            beta = beta + np.linalg.solve(X.T @ (X * W[:, None]) + 1e-6 * np.eye(3), X.T @ (y - q))
        X1 = X[:, :2]; b1 = np.zeros(2)
        for _ in range(25):
            q = 1 / (1 + np.exp(-X1 @ b1)); W = q * (1 - q) + 1e-9
            b1 = b1 + np.linalg.solve(X1.T @ (X1 * W[:, None]) + 1e-6 * np.eye(2), X1.T @ (y - q))
        out.append(dict(reste=str(rb), lignes=int(len(g)), marches=int(g.st.nunique()), brier_marche=round(bm, 4), brier_modele_binance=round(bz, 4),
                        pente_prix_seul=round(float(b1[1]), 3), pente_prix=round(float(beta[1]), 3), poids_modele=round(float(beta[2]), 3)))
    return out


# RÈGLES FIGÉES le 14.10.2026 après lecture de l'EXPLORATION SEULE (29.09–06.10 : 768 marchés 15 min, 192 marchés horaires),
# avant toute lecture de la validation. Une vingtaine de variantes ont été essayées en exploration (fichier de travail hors dépôt) :
# les 4 retenues sont les meilleures ou les plus proches de la question ; le risque de sélection est donc réel.
#   Exploration (10 $ par achat, IC 90 % par marchés, non corrigé) :
#   R1 15 min, favori 0,55–0,90 avec ≥ 65 % du temps restant (5 premières minutes) → favori : 744 achats, ROI +6,0 %, +444 $ [+94 ; +783]
#      (pessimiste +4,5 %) — MAIS la même règle sur l'horaire fait −10,5 % : suspect.
#   R2 horaire, favori 0,90–0,98 dans les 10 derniers % (6 dernières minutes) → favori : 82 achats, ROI +2,7 %, +22 $ [−7 ; +43]
#   R3 horaire, |Φ(zf) − prix| ≥ 0,15 à n'importe quel instant → acheter le côté que préfère le modèle Binance (le règlement EST la bougie
#      Binance) : 53 achats, ROI +14,0 %, +74 $ [−23 ; +168]
#   R4 15 min, favori 0,60–0,92 et Φ(zf) − prix ≥ 0,08 (le modèle Binance juge le favori sous-payé) → favori : 629 achats, ROI +3,1 %,
#      +193 $ [−48 ; +435]
#   Écartés : billets 0,02–0,20 en fin de fenêtre (−32 % en 15 min, −42 % en horaire), favoris tardifs avec zf ≥ 2 en 15 min (0,0 %),
#   élan BTC 30 s non suivi par le prix (+1 %, peu de cas).
# CRITÈRE : ROI > 0 en exploration ET en validation, et borne basse de l'IC 90 % corrigé Bonferroni (4 règles → percentiles 1,25 / 98,75,
#   bootstrap par marchés, 10 000 tirages) du P&L de validation > 0. Prix pessimiste publié à côté. Aucun fantôme sans accord de Pitch.
REGLES = {"15m": {"R1 15 min favori 0,55–0,90, ≥ 65 % du temps restant → favori": (lambda x: x.fp.between(.55, .90) & (x.reste >= .65), "fav"),
                  "R4 15 min favori 0,60–0,92, modèle − prix ≥ 0,08 → favori": (lambda x: ((x.phi - x.fp) >= .08) & x.fp.between(.60, .92), "fav")},
          "1h": {"R2 horaire favori 0,90–0,98, ≤ 10 % restant → favori": (lambda x: x.fp.between(.90, .98) & (x.reste <= .10), "fav"),
                 "R3 horaire |modèle − prix| ≥ 0,15 → côté du modèle": (lambda x: (x.phi - x.fp).abs() >= .15, "mod")}}


def evaluer(D, M, regles, pa, rng, nb=10000):
    out = {}
    P = D[D.part == pa]; nc = int((M.part == pa).sum())
    for nom, (f, cote) in regles.items():
        for prix in ("observe", "pessimiste"):
            x = P[f(P)].copy()
            sf = (x.phi >= x.fp) if cote == "mod" else pd.Series(cote == "fav", index=x.index)   # côté acheté = favori ?
            x["px"] = np.where(sf, x.pf, x.pt); x["w"] = np.where(sf, x.fw, 1 - x.fw); x["sig"] = np.where(sf, x.fp, 1 - x.fp)
            x = x[np.isfinite(x.px) & (x.px > 0.01) & (x.px < 0.99)].sort_values(["st", "t"]).groupby("st").head(1)
            if prix == "pessimiste": x["px"] = np.maximum(x.px, x.sig)
            x["pnl"] = x.w / (x.px + fee(x.px)) - 1
            vv = np.concatenate([x.pnl.values, np.zeros(max(nc - len(x), 0))]) * 10
            bs = vv[rng.integers(0, len(vv), (nb, len(vv)))].sum(1) if len(vv) else np.zeros(1)
            out[f"{nom}|{pa}|{prix}"] = dict(marches=nc, achats=int(len(x)), gagnants=int(x.w.sum()), taux=float(x.w.mean()) if len(x) else None,
                prix=float(x.px.mean()) if len(x) else None, roi=float(x.pnl.mean()) if len(x) else None, pnl10=float(vv.sum()),
                ic90=np.percentile(bs, [5, 95]).tolist(), ic_bonf=np.percentile(bs, [1.25, 98.75]).tolist())
    return out


if __name__ == "__main__":
    VALID = "--validation" in sys.argv; args = [a for a in sys.argv[1:] if a != "--validation"]
    typ = args[1]; D, TOUT, M = construire(args[0], typ, args[2:]); rng = np.random.default_rng(1089)
    parts = ["exploration"] + (["validation"] if VALID else [])
    out = {"type": typ, "marches": {}, "liquidite": {}, "calib": {}, "efficacite": {}, "regles": {}}
    for pa in parts:
        Mp = M[M.part == pa]; Tp = TOUT[TOUT.part == pa]
        out["marches"][pa] = int(len(Mp))
        out["liquidite"][pa] = dict(transactions_med=float(Mp.n_tr.median()), transactions_fenetre_med=float(Mp.n_fen.median()),
            usd_fenetre_med=float(Mp.usd_fen.median()), usd_total_med=float(Mp.usd_tot.median()), transactions_10pct_fin_med=float(Mp.n_fin.median()),
            portefeuilles_fenetre_med=float(Mp.wallets.median()), tronques=int(Mp.tronque.sum()), binance_bon_gagnant=float(Mp.binance_ok.mean()),
            up_gagne=float(Mp.upw.mean()), couverture_prix=float(Tp.pu.notna().mean()),
            couverture_prix_derniers_10pct=float(Tp[(Tp.t >= 0.9 * DUREE[typ])].pu.notna().mean()))
        P = D[D.part == pa]
        out["calib"][pa] = calibration(P, rng); out["efficacite"][pa] = resume_efficacite(P, rng)
        if REGLES.get(typ): out["regles"].update(evaluer(D, M, REGLES[typ], pa, rng))
    s = json.dumps(out, ensure_ascii=False, indent=1, default=str); print(s)
    open(os.path.join(ICI, f"autres_marches_h1089_{typ}_" + ("validation" if VALID else "exploration") + ".json"), "w").write(s)
