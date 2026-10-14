"""BOT95 — H1084 « biais favori / billet en fin de cycle » : dans les 60 dernières secondes des marchés Polymarket BTC 5 min Up/Down,
les favoris (0,80–0,99) ou les billets (0,01–0,20) sont-ils mal payés par rapport à leur fréquence réelle ?
Hors ligne, aucun ordre. Données : transactions publiques Polymarket (achats seulement ; prix Up = prix Up ou 1 − prix Down),
Binance BTCUSDT 1 s (approximation de Chainlink). Rien après le 08.10.2026 n'est lu (marchés ≥ 09.10 00:00 UTC écartés).
DÉCOUPAGE : exploration 12.09–30.09, validation 01.10–08.10, lue UNE seule fois.
CONVENTIONS (reprises de H1067 / H1083) : instants t = 240, 245, …, 290 s (60 à 10 s restantes). Prix du marché à t = médiane des achats
  (en prix Up) dans (t−6, t], au moins 2 achats ; favori = côté ≥ 0,5. Prix PAYÉ = médiane des achats du côté acheté dans (t+1, t+6] ;
  frais 0,07·p·(1−p) ; prix payé gardé seulement dans ]0,01 ; 0,99[ ; billet gardé jusqu'au règlement ; un seul achat par cycle et par règle
  (premier instant qui déclenche).
DISTANCE AU PRIX À BATTRE (z) : le règlement compare la moyenne Chainlink des 60 dernières secondes à la moyenne des 60 s avant le début.
  Avec Binance : K = moyenne c[début−60, début) ; à t, moyenne finale attendue = (partie déjà connue + prix actuel × secondes restantes) / 60 ;
  écart-type = σ1s(1 h) · √(n(n+1)(2n+1)/6) / 60 ; z = écart / écart-type, compté dans le sens du favori (zf). Binance ≠ Chainlink :
  le signe de la moyenne Binance ne donne le bon gagnant que dans ~97,7 % des cycles.
EXPLORATION (12.09–30.09, 5 459 cycles) : le marché est bien calibré en fin de cycle ; les favoris gagnent 1 à 3 points de plus que leur
  prix du signal, mais le prix réellement payé juste après est plus bas (le prix glisse) ; acheter le favori 0,90–0,98 avec 20–60 s restantes :
  +0,1 % (premier achat du cycle). PIÈGE DE SÉLECTION : un achat n'existe que si quelqu'un vend dans (t+1, t+6]. Les cycles sans
  transaction ont un favori gagnant à 99,6 %, ceux avec transaction à 95,6 % : les transactions arrivent quand le favori vacille.
  On compte donc chaque cycle de la période (0 $ quand rien ne déclenche ou rien n'est servi) et on rejoue aussi un prix PESSIMISTE
  = max(prix médian du signal, prix médian après), pour ne pas profiter d'une glissade qu'un vrai ordre n'aurait pas eue.
  Le filtre zf sépare bien : zf < 1 → −2,8 % (−10 % au prix pessimiste) ; zf ≥ 2 → +0,6 % ; zf ≥ 3 → +1,5 %. Billets 0,02–0,20 : −24 %.
RÈGLES FIGÉES (avant toute lecture de la validation) :
  B1 : favori 0,90–0,98 au signal, 20–60 s restantes → acheter le favori (concept Bot95 d'origine).
  B2 : B1 et zf ≥ 2 → acheter le favori.
  B3 : B1 et zf ≥ 3 → acheter le favori (seuil choisi après plusieurs essais : le plus exposé au hasard).
  B4 : billet 0,02–0,20 au signal (1 − prix du favori), 10–60 s restantes → acheter le billet (contrôle du biais favori-billet).
CRITÈRE : ROI > 0 en exploration ET en validation, et borne basse de l'IC 90 % corrigé Bonferroni (4 règles → percentiles 1,25 / 98,75,
  bootstrap par cycles, 10 000 tirages) du P&L de validation > 0. Le prix pessimiste est publié à côté. Biais billet confirmé si la borne
  HAUTE corrigée de B4 en validation est < 0. Aucun fantôme sans accord de Pitch.
Usage : python3 etude/bot5min/biais_fin_cycle_h1084.py btc1s.npz polytrades_*.json.gz  [--validation]"""
import sys, json, gzip, os, numpy as np, pandas as pd
from math import erf, sqrt
ICI = os.path.dirname(os.path.abspath(__file__)); FIN_EXPLO = 1790812800; FIN_VALID = 1791504000   # 01.10 / 09.10 00:00 UTC
fee = lambda p: 0.07 * p * (1 - p); TT = list(range(240, 295, 5)); PHI = np.vectorize(lambda x: 0.5 * (1 + erf(x / sqrt(2))))

def construire(npz, fichiers):
    z = np.load(npz); t0 = int(z["t"][0]); c = z["c"].astype(float)
    Cc = np.concatenate([[0], np.cumsum(c)]); Cd2 = np.concatenate([[0], np.cumsum(np.diff(c, prepend=c[0]) ** 2)])
    sd = lambda i, w: np.sqrt((Cd2[i + 1] - Cd2[i + 1 - w]) / w)
    rows = []
    for f in sorted(fichiers):
        for st_, m in json.load(gzip.open(f))["marches"].items():
            st = int(st_); r = m.get("resultat") or {}
            if r.get("Up") not in (0.0, 1.0) or st >= FIN_VALID: continue
            s0 = st - t0
            if s0 < 3700 or s0 + 300 >= len(c): continue
            upw = int(r["Up"] == 1.0); K = (Cc[s0] - Cc[s0 - 60]) / 60
            T = np.array([(x[0] - st, x[4] if x[3] == "Up" else 1 - x[4], 1 if x[3] == "Up" else 0, x[4]) for x in m["trades"]
                          if x[0] is not None and x[4] and 0 < x[4] < 1 and x[2] == "BUY" and 228 <= x[0] - st < 300], float).reshape(-1, 4)
            for tt in TT:
                i = s0 + tt; s1 = sd(i, 3600); n = 300 - tt - 1
                EA = (Cc[i + 1] - Cc[s0 + 240] + n * c[i]) / 60; zz = (EA - K) / (s1 * np.sqrt(n * (n + 1) * (2 * n + 1) / 6) / 60)
                w = T[(T[:, 0] > tt - 6) & (T[:, 0] <= tt)]; nx = T[(T[:, 0] > tt) & (T[:, 0] <= tt + 6)]
                pU = nx[nx[:, 2] == 1][:, 3]; pD = nx[nx[:, 2] == 0][:, 3]
                rows.append(dict(st=st, t=tt, upw=upw, pu=np.median(w[:, 1]) if len(w) >= 2 else np.nan,
                                 pUp=np.median(pU) if len(pU) else np.nan, pDown=np.median(pD) if len(pD) else np.nan, z=zz))
    D = pd.DataFrame(rows); D["part"] = np.where(D.st < FIN_EXPLO, "exploration", "validation")
    D["fav_up"] = D.pu >= .5; D["fp"] = np.where(D.fav_up, D.pu, 1 - D.pu); D["fw"] = np.where(D.fav_up, D.upw, 1 - D.upw)
    D["pf"] = np.where(D.fav_up, D.pUp, D.pDown); D["pt"] = np.where(D.fav_up, D.pDown, D.pUp)
    D["zf"] = np.where(D.fav_up, D.z, -D.z); D["left"] = 300 - D.t
    return D[D.pu.notna()].copy(), D

REGLES = {"B1 favori 0,90–0,98, 20–60 s → favori": (lambda x: x.fp.between(.90, .98) & x.left.between(20, 60), "fav"),
          "B2 B1 + distance zf ≥ 2 → favori": (lambda x: x.fp.between(.90, .98) & x.left.between(20, 60) & (x.zf >= 2), "fav"),
          "B3 B1 + distance zf ≥ 3 → favori": (lambda x: x.fp.between(.90, .98) & x.left.between(20, 60) & (x.zf >= 3), "fav"),
          "B4 billet 0,02–0,20, 10–60 s → billet": (lambda x: (1 - x.fp).between(.02, .20) & x.left.between(10, 60), "tic")}

if __name__ == "__main__":
    VALID = "--validation" in sys.argv; args = [a for a in sys.argv[1:] if a != "--validation"]
    D, TOUT = construire(args[0], args[1:]); RNG = np.random.default_rng(1084)
    parts = ["exploration"] + (["validation"] if VALID else [])
    out = {"cycles": {p: int(TOUT[TOUT.part == p].st.nunique()) for p in parts}, "regles": {}, "calib": {}, "selection": {}}
    for nom, (f, cote) in REGLES.items():
        for pa in parts:
            for prix in ("observe", "pessimiste"):
                P = D[D.part == pa]; nc = out["cycles"][pa]; x = P[f(P)].copy()
                x["px"] = x.pf if cote == "fav" else x.pt; x["w"] = x.fw if cote == "fav" else 1 - x.fw
                x = x[np.isfinite(x.px) & (x.px > 0.01) & (x.px < 0.99)].sort_values(["st", "t"]).groupby("st").head(1)   # mêmes achats
                if prix == "pessimiste": x["px"] = np.maximum(x.px, x.fp if cote == "fav" else 1 - x.fp)
                x["pnl"] = x.w / (x.px + fee(x.px)) - 1
                vv = np.concatenate([x.pnl.values, np.zeros(max(nc - len(x), 0))]) * 10            # 10 $ par achat, tous les cycles
                bs = vv[RNG.integers(0, len(vv), (10000, len(vv)))].sum(1)
                br = x.pnl.values[RNG.integers(0, len(x), (10000, len(x)))].mean(1)
                out["regles"][f"{nom}|{pa}|{prix}"] = dict(cycles=nc, achats=int(len(x)), gagnants=int(x.w.sum()), taux=float(x.w.mean()),
                    prix=float(x.px.mean()), roi=float(x.pnl.mean()), pnl10=float(vv.sum()), ic90=np.percentile(bs, [5, 95]).tolist(),
                    ic_bonf=np.percentile(bs, [1.25, 98.75]).tolist(), roi_ic90=np.percentile(br, [5, 95]).tolist(),
                    roi_ic_bonf=np.percentile(br, [1.25, 98.75]).tolist())
    for pa in parts:
        P = D[D.part == pa]; b = pd.cut(P.fp, [.5, .6, .7, .8, .85, .9, .95, .98, .995]); lb = pd.cut(P.left, [5, 20, 40, 60])
        P = P.assign(phi=PHI(P.zf.clip(-8, 8)))
        g = P.groupby([lb, b], observed=True).agg(n=("fw", "size"), cycles=("st", "nunique"), prix=("fp", "mean"), freq=("fw", "mean"), phi=("phi", "mean")).reset_index()
        out["calib"][pa] = [dict(reste=str(r.left), tranche=str(r.fp), n=int(r.n), cycles=int(r.cycles), prix=float(r.prix), freq=float(r.freq), phi_binance=float(r.phi))
                            for r in g.itertuples()]
        S = P[P.fp.between(.90, .98) & P.left.between(20, 60)]; fill = np.isfinite(S.pf) & (S.pf > .01) & (S.pf < .99)
        out["selection"][pa] = dict(lignes=int(len(S)), taux_servi=float(fill.mean()), fav_gagne_servi=float(S[fill].fw.mean()),
                                    fav_gagne_non_servi=float(S[~fill].fw.mean()), prix_signal_servi=float(S[fill].fp.mean()),
                                    prix_paye_servi=float(S[fill].pf.mean()), prix_signal_non_servi=float(S[~fill].fp.mean()))
        A = TOUT[TOUT.part == pa]; out["selection"][pa]["couverture_prix_par_t"] = A.groupby("t").pu.apply(lambda s: round(float(s.notna().mean()), 3)).to_dict()
    s = json.dumps(out, ensure_ascii=False, indent=1, default=str); print(s)
    open(os.path.join(ICI, "biais_fin_cycle_h1084_" + ("validation" if VALID else "exploration") + ".json"), "w").write(s)
