"""BOT95 — H1067 : Polymarket intègre-t-il ce que BTC vient de faire ? Test sur 27 jours de transactions publiques (12.09 → 09.10.2026).
PROTOCOLE PRÉ-ENREGISTRÉ le 13.10.2026 ~21:00, AVANT le téléchargement de ces 27 jours (jamais vus). Hors ligne ; aucun ordre.
SOURCES : transactions Polymarket BTC 5 min (data-api, achats seulement, prix de l'Up = prix Up ou 1 − prix Down), Binance BTCUSDT 1 s.
EXPLORATION déjà faite (09–11.10, 863 cycles ; 30 jours Binance seul) : élan des 10 dernières s vers le favori → favori perd 3 à 9 pts de
  moins que son prix ; volatilité 5 min / 1 h haute → moins de renversements ; fenêtres :00/:30 → plus ; open interest qui monte → Up.
INSTANTS : 60, 90, 120, 150, 180, 210, 240, 260 s. Favori = côté dont le prix médian des achats dans (t−6, t] est ≥ 0,5. Prix PAYÉ = médiane
  des achats du côté acheté dans (t+1, t+6] (donc APRÈS le signal ; prudence sur la latence) + frais 0,07·p·(1−p). Gardé jusqu'au règlement.
RÈGLES FIGÉES (seuils = quintiles de la période d'exploration 12.09–30.09, puis appliqués tels quels à la validation 01.10–08.10) :
  E1 : favori 0,60–0,95 et m10 (BTC sur 10 s dans le sens du favori / σ 1 h) dans le quintile haut → acheter le favori.
  E2 : favori 0,60–0,95 et m10 dans le quintile bas → acheter le billet (l'autre côté).
  E3 : favori 0,60–0,95 et volatilité 300 s / 3 600 s dans le quintile haut → acheter le favori.
  E4 : fenêtre commençant à :00 ou :30, favori 0,65–0,95 → acheter le billet.
CRITÈRE : ROI > 0 en exploration ET en validation, et IC 90 % par cycles (corrigé 4 règles → 97,5 %) de la validation > 0. Sinon abandon.
  Un seul achat par cycle et par règle (premier instant qui déclenche). Aucun fantôme sans accord de Pitch.
Usage : python3 etude/bot5min/retard_poly_h1067.py btc1s.npz polytrades_*.json.gz"""
import sys, json, gzip, os, numpy as np, pandas as pd
ICI = os.path.dirname(os.path.abspath(__file__)); RNG = np.random.default_rng(1067); FIN_EXPLO = 1790812800  # 01.10.2026 00:00 UTC
fee = lambda p: 0.07 * p * (1 - p)
z = np.load(sys.argv[1]); t = z["t"]; c = z["c"].astype(float); t0 = t[0]
cs = lambda x: np.concatenate([[0], np.cumsum(x)]); Cc = cs(c); Cd2 = cs(np.diff(c, prepend=c[0]) ** 2)
sd = lambda i, w: np.sqrt((Cd2[i + 1] - Cd2[i + 1 - w]) / w)
rows = []
for f in sorted(sys.argv[2:]):
    for st_, m in json.load(gzip.open(f))["marches"].items():
        st = int(st_); r = m.get("resultat") or {}
        if r.get("Up") not in (0.0, 1.0) or st >= 1791590400: continue
        s0 = st - t0
        if s0 < 3700 or s0 + 300 >= len(c): continue
        T = np.array([(x[0] - st, x[4] if x[3] == "Up" else 1 - x[4], 1 if x[3] == "Up" else 0, x[4]) for x in m["trades"]
                      if x[0] is not None and x[4] and 0 < x[4] < 1 and x[2] == "BUY"], float)
        if len(T) < 20: continue
        upw = int(r["Up"] == 1.0)
        for tt in (60, 90, 120, 150, 180, 210, 240, 260):
            w = T[(T[:, 0] > tt - 6) & (T[:, 0] <= tt)]; nx = T[(T[:, 0] > tt) & (T[:, 0] <= tt + 6)]
            if len(w) < 2: continue
            pu = np.median(w[:, 1]); lead = 1 if pu >= 0.5 else -1; i = s0 + tt; rest = 300 - tt
            fav = "Up" if lead > 0 else "Down"
            pf = nx[nx[:, 2] == (1 if fav == "Up" else 0)][:, 3]; pt = nx[nx[:, 2] == (0 if fav == "Up" else 1)][:, 3]
            favwin = upw if fav == "Up" else 1 - upw
            rows.append(dict(st=st, t=tt, fp=max(pu, 1 - pu), favwin=favwin, pfav=np.median(pf) if len(pf) else np.nan, ptic=np.median(pt) if len(pt) else np.nan,
                             m10=lead * (c[i] - c[i - 10]) / (sd(i, 3600) * np.sqrt(10)), vr=sd(i, 300) / sd(i, 3600), m00=(st // 60) % 60 in (0, 30)))
D = pd.DataFrame(rows); D["part"] = np.where(D.st < FIN_EXPLO, "exploration", "validation")
E = D[(D.part == "exploration") & D.fp.between(0.60, 0.95)]; q_m10 = np.quantile(E.m10, [0.2, 0.8]); q_vr = np.quantile(E.vr, 0.8)
R = {"E1 élan frais → favori": (D.fp.between(0.60, 0.95) & (D.m10 >= q_m10[1]), "fav"),
     "E2 élan contraire → billet": (D.fp.between(0.60, 0.95) & (D.m10 <= q_m10[0]), "tic"),
     "E3 volatilité haute → favori": (D.fp.between(0.60, 0.95) & (D.vr >= q_vr), "fav"),
     "E4 fenêtre :00/:30 → billet": (D.fp.between(0.65, 0.95) & D.m00, "tic")}
o = ["# Bot95 — H1067 : Polymarket et ce que BTC vient de faire (27 jours)\n",
     f"{D.st.nunique()} cycles ; seuils figés sur l'exploration : m10 quintiles {q_m10.round(3).tolist()}, volatilité q80 {q_vr:.3f}. Aucun ordre.\n",
     "| Règle | Période | Cycles | Achats | Gagnants | Prix moyen | ROI | IC 97,5 % par cycles | ", "|---|---|---|---|---|---|---|---|"]
V = {}
for nom, (m, cote) in R.items():
    X = D[m].copy(); X["px"] = X.pfav if cote == "fav" else X.ptic; X["w"] = X.favwin if cote == "fav" else 1 - X.favwin
    X = X[np.isfinite(X.px) & (X.px > 0.01) & (X.px < 0.99)].sort_values(["st", "t"]).groupby("st").head(1)
    X["pnl"] = X.w / (X.px + fee(X.px)) - 1                                   # par dollar engagé
    for pa in ("exploration", "validation"):
        x = X[X.part == pa]; nc = D[D.part == pa].st.nunique()
        vv = np.concatenate([x.pnl.values, np.zeros(max(nc - len(x), 0))])
        bs = vv[RNG.integers(0, len(vv), (4000, len(vv)))].sum(1); lo, hi = np.percentile(bs, [1.25, 98.75])
        o.append(f"| {nom} | {pa} | {nc} | {len(x)} | {int(x.w.sum())} | {x.px.mean():.3f} | {100 * x.pnl.mean():+.1f} % | [{lo:+.1f} ; {hi:+.1f}] $ pour 1 $ |")
        V[(nom, pa)] = (x.pnl.mean(), lo)
o.append("\n**Verdict (critère figé)**\n")
for nom in R:
    ok = V[(nom, "exploration")][0] > 0 and V[(nom, "validation")][0] > 0 and V[(nom, "validation")][1] > 0
    o.append(f"- {nom} : {'candidat (proposition à Pitch)' if ok else 'abandon'}")
open(os.path.join(ICI, "resultat_retard_poly_h1067.md"), "w").write("\n".join(o) + "\n"); print("\n".join(o))
