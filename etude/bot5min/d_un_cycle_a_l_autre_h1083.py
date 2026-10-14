"""BOT95 — H1083 « d'un cycle à l'autre » : ce qui s'est passé AVANT le cycle prédit-il l'issue mieux que le prix du marché en début de cycle ?
Hors ligne, aucun ordre. Données : transactions publiques Polymarket BTC 5 min (achats seulement ; prix Up = prix Up ou 1 − prix Down),
Binance BTCUSDT 1 s. Rien après le 08.10.2026 n'est lu (marchés ≥ 09.10 00:00 UTC écartés).
DÉCOUPAGE : exploration 12.09–30.09 (12.09 perdu : 24 h d'historique BTC exigées), validation 01.10–08.10, lue UNE seule fois.
CONVENTIONS (reprises de H1067) : prix du marché à t = médiane des achats (en prix Up) dans (t−6, t] ; prix PAYÉ = médiane des achats
  du côté acheté dans (t+1, t+6] ; frais 0,07·p·(1−p) ; billet gardé jusqu'au règlement ; un achat par cycle et par règle.
VARIABLES : r5 / r15 / r30 = rendement BTC des 5 / 15 / 30 dernières minutes avant l'ouverture, en écarts-types (σ 1 s sur 1 h) ;
  v30 = σ 30 min / σ 1 h ; d = mouvement BTC depuis l'ouverture jusqu'à t, en σ du temps restant ; résultat et série des cycles précédents ;
  distance au prix d'ouverture du cycle précédent ; distance au multiple de 100 $ ; heure.
EXPLORATION (12.09–30.09, 5 118 cycles) : aucune variable inter-cycles n'écarte nettement l'issue du prix du marché (|t| < 2 partout) ;
  achat au hasard vers 0,50 = −3 à −5 % (frais + écart) ; seules pistes : retour à la moyenne après une baisse de 30 min, et le côté Down
  après une baisse dans les 20 premières secondes (mouvement INTRA-cycle). Modèle logistique (jours exclus à tour de rôle) : Brier −0,001.
RÈGLES FIGÉES (seuils = quantiles de l'exploration, codés en dur ci-dessous) :
  X1 : t = 10 s, r30 ≤ −1,018 (quintile bas) → acheter Up.
  X2 : t = 10 s, r30 ≤ −1,018 ET r5 < 0 → acheter Up.
  X3 : t = 10 s, v30 ≥ 1,124 (quintile haut) → acheter Down.
  X4 : t = 20 s, d ≤ −0,2302 (quintile bas, BTC a baissé depuis l'ouverture) → acheter Down.
CRITÈRE : ROI > 0 en exploration ET en validation, et borne basse de l'IC 90 % corrigé Bonferroni (4 règles → percentiles 1,25 / 98,75,
  bootstrap par cycles) du P&L de validation > 0. Sinon abandon. Aucun fantôme sans accord de Pitch.
BRIER : logistique [logit(prix marché) + variables inter-cycles] (+ variante avec d) ajustée sur l'exploration à t = 10 / 20 / 30 s,
  comparée au prix du marché sur la validation ; IC 90 % de la différence par bootstrap des cycles.
Usage : python3 etude/bot5min/d_un_cycle_a_l_autre_h1083.py btc1s.npz polytrades_*.json.gz  [--validation]"""
import sys, json, gzip, os, numpy as np, pandas as pd
from math import erf
from sklearn.linear_model import LogisticRegression
ICI = os.path.dirname(os.path.abspath(__file__)); FIN_EXPLO = 1790812800; FIN_VALID = 1791504000   # 01.10 / 09.10 00:00 UTC
fee = lambda p: 0.07 * p * (1 - p); TT = (10, 20, 30)
Q20_R30, Q20_D20, Q80_V30 = -1.018, -0.2302, 1.124   # seuils figés (quantiles de l'exploration)
X0 = ["prev", "streak", "r5", "r5b", "r15", "r30", "v15", "v30", "v1h24", "rnd", "dps"]

def construire(npz, fichiers):
    z = np.load(npz); t = z["t"]; c = z["c"].astype(float); t0 = int(t[0])
    cs = lambda x: np.concatenate([[0], np.cumsum(x)]); Cd2 = cs(np.diff(c, prepend=c[0]) ** 2)
    sd = lambda i, w: np.sqrt((Cd2[i + 1] - Cd2[i + 1 - w]) / w)
    res, cyc = {}, {}
    for f in sorted(fichiers):
        for st_, m in json.load(gzip.open(f))["marches"].items():
            st = int(st_); r = m.get("resultat") or {}
            if r.get("Up") not in (0.0, 1.0) or st >= FIN_VALID: continue
            res[st] = int(r["Up"] == 1.0)
            cyc[st] = np.array([(x[0] - st, x[4] if x[3] == "Up" else 1 - x[4], 1 if x[3] == "Up" else 0, x[4]) for x in m["trades"]
                                if x[0] is not None and x[4] and 0 < x[4] < 1 and x[2] == "BUY" and -10 <= x[0] - st <= 70], float)
    rows = []
    for st, T in cyc.items():
        s0 = st - t0
        if s0 < 86400 + 10 or s0 + 300 >= len(c) or len(T) < 5: continue
        k = 0; prev = res.get(st - 300)
        if prev is not None:
            k = 1
            while res.get(st - 300 * (k + 1)) == prev: k += 1
        s1h = sd(s0, 3600); n = lambda a, b, w: (c[a] - c[b]) / (s1h * np.sqrt(w))
        base = dict(st=st, upw=res[st], prev=np.nan if prev is None else prev, streak=(k if prev == 1 else -k) if prev is not None else np.nan,
                    r5=n(s0, s0 - 300, 300), r5b=n(s0 - 300, s0 - 600, 300), r15=n(s0, s0 - 900, 900), r30=n(s0, s0 - 1800, 1800),
                    v15=sd(s0, 900) / s1h, v30=sd(s0, 1800) / s1h, v1h24=s1h / sd(s0, 86400), rnd=(c[s0] % 100) - 50, hour=(st // 3600) % 24)
        for tt in TT:
            w = T[(T[:, 0] > tt - 6) & (T[:, 0] <= tt)]; nx = T[(T[:, 0] > tt) & (T[:, 0] <= tt + 6)]
            if len(w) < 2: continue
            i = s0 + tt; rest = 300 - tt; pU = nx[nx[:, 2] == 1][:, 3]; pD = nx[nx[:, 2] == 0][:, 3]
            rows.append(dict(base, t=tt, pu=np.median(w[:, 1]), pUp=np.median(pU) if len(pU) else np.nan, pDown=np.median(pD) if len(pD) else np.nan,
                             d=(c[i] - c[s0]) / (s1h * np.sqrt(rest)), dps=(c[i] - c[s0 - 300]) / (s1h * np.sqrt(rest))))
    D = pd.DataFrame(rows); D["part"] = np.where(D.st < FIN_EXPLO, "exploration", "validation"); return D

if __name__ == "__main__":
    VALID = "--validation" in sys.argv; args = [a for a in sys.argv[1:] if a != "--validation"]
    D = construire(args[0], args[1:]); RNG = np.random.default_rng(1083)
    parts = ["exploration"] + (["validation"] if VALID else [])
    R = {"X1 baisse 30 min → Up (t=10 s)": (lambda x: (x.t == 10) & (x.r30 <= Q20_R30), "Up"),
         "X2 baisse 30 min et 5 min → Up (t=10 s)": (lambda x: (x.t == 10) & (x.r30 <= Q20_R30) & (x.r5 < 0), "Up"),
         "X3 volatilité 30 min haute → Down (t=10 s)": (lambda x: (x.t == 10) & (x.v30 >= Q80_V30), "Down"),
         "X4 BTC a baissé depuis l'ouverture → Down (t=20 s)": (lambda x: (x.t == 20) & (x.d <= Q20_D20), "Down")}
    out = {"cycles": {p: int(D[D.part == p].st.nunique()) for p in ("exploration", "validation")}, "regles": {}, "calib": {}, "brier": {}}
    E = D[D.part == "exploration"]
    out["controle_seuils"] = {"q20_r30": float(np.quantile(E[E.t == 10].r30, .2)), "q80_v30": float(np.quantile(E[E.t == 10].v30, .8)),
                              "q20_d20": float(np.quantile(E[E.t == 20].d, .2))}
    for nom, (f, cote) in R.items():
        for pa in parts:
            P = D[D.part == pa]; nc = P.st.nunique(); x = P[f(P)].copy(); x["px"] = x["p" + cote]
            x["w"] = x.upw if cote == "Up" else 1 - x.upw; x = x[np.isfinite(x.px) & (x.px > 0.01) & (x.px < 0.99)]
            x["pnl"] = x.w / (x.px + fee(x.px)) - 1
            vv = np.concatenate([x.pnl.values, np.zeros(max(nc - len(x), 0))]) * 10            # 10 $ par achat
            bs = vv[RNG.integers(0, len(vv), (10000, len(vv)))].sum(1)
            bi = RNG.integers(0, len(x), (10000, len(x))); br = x.pnl.values[bi].mean(1)
            out["regles"][f"{nom}|{pa}"] = dict(cycles=int(nc), achats=int(len(x)), gagnants=int(x.w.sum()), taux=float(x.w.mean()), prix=float(x.px.mean()),
                roi=float(x.pnl.mean()), pnl10=float(vv.sum()), ic90=np.percentile(bs, [5, 95]).tolist(), ic_bonf=np.percentile(bs, [1.25, 98.75]).tolist(),
                roi_ic90=np.percentile(br, [5, 95]).tolist(), roi_ic_bonf=np.percentile(br, [1.25, 98.75]).tolist())
    for pa in parts:                                                                          # calibration
        P = D[(D.part == pa)]; b = pd.cut(P.pu, [0, .3, .4, .45, .5, .55, .6, .7, 1])
        g = P.groupby([P.t, b], observed=True).agg(n=("upw", "size"), prix=("pu", "mean"), freq=("upw", "mean")).reset_index()
        out["calib"][pa] = [dict(t=int(r.t), tranche=str(r.pu), n=int(r.n), prix=float(r.prix), freq=float(r.freq)) for r in g.itertuples()]
    if VALID:                                                                                 # Brier
        for nomf, feats in (("inter-cycles", X0), ("inter-cycles + d", X0 + ["d"])):
            for tt in TT:
                M = lambda x: np.column_stack([np.log(np.clip(x.pu, .02, .98) / (1 - np.clip(x.pu, .02, .98)))] + [np.clip(x[f], -5, 5) for f in feats])
                A = D[(D.part == "exploration") & (D.t == tt)].dropna(subset=feats); V = D[(D.part == "validation") & (D.t == tt)].dropna(subset=feats)
                mdl = LogisticRegression(max_iter=1000).fit(M(A), A.upw); p = mdl.predict_proba(M(V))[:, 1]
                d = (V.upw.values - p) ** 2 - (V.upw.values - V.pu.values) ** 2
                bs = d[RNG.integers(0, len(d), (10000, len(d)))].mean(1)
                out["brier"][f"{nomf}|{tt}"] = dict(n=int(len(V)), marche=float(((V.upw - V.pu) ** 2).mean()), modele=float(((V.upw - p) ** 2).mean()),
                                                     diff=float(d.mean()), ic90=np.percentile(bs, [5, 95]).tolist())
    s = json.dumps(out, ensure_ascii=False, indent=1); print(s)
    open(os.path.join(ICI, "d_un_cycle_a_l_autre_h1083_" + ("validation" if VALID else "exploration") + ".json"), "w").write(s)
