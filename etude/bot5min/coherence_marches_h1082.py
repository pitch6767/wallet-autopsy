"""BOT95 — H1082 « cohérence entre marchés » : les marchés ETH / SOL Up/Down 5 min de Polymarket sont-ils en retard sur le BTC du même créneau ?
PROTOCOLE PRÉ-ENREGISTRÉ le 14.10.2026, AVANT tout calcul sur la période de validation. Hors ligne ; aucun ordre ; aucun fantôme, bot ni workflow modifié.

DONNÉES (seules journées où les transactions BTC, ETH et SOL existent toutes, avant le 13.10.2026 00:00 UTC) : 11.10 et 12.10.2026.
  - transactions publiques Polymarket (data-api, branche donnees-btc/polytrades) : BTC, ETH, SOL 5 min. Prix « Up » d'une transaction = prix si
    jeton Up, 1 − prix si jeton Down. Les transactions BTC du 12.10 après ~19:25 UTC manquent dans le fichier : R1–R3 n'y sont pas testables.
  - prix spot Binance à la seconde : BTC (btc1s.npz, jusqu'au 11.10 inclus) puis transactions Binance enregistrées à Dublin (12.10).
DÉCOUPAGE CHRONOLOGIQUE (créneaux de 5 min) : exploration = 346 premiers créneaux (11.10 00:00 → 12.10 04:50 UTC, ~60 %),
  validation = 230 suivants (12.10 04:50 → 13.10 00:00). Aucun jour ≥ 13.10 n'a servi à choisir quoi que ce soit (pas de données ETH/SOL ≥ 13.10).
MESURES à chaque instant t = 30, 40, …, 270 s du créneau :
  pX(t) = médiane des prix « Up » de toutes les transactions du marché X dans (t − 10, t] (au moins 2, sinon inconnu) ;
  dX = pX(t) − pX(t − 30) (mouvement du marché sur 30 s) ; zB = rendement du BTC spot sur 30 s / (écart-type 1 s des 600 s précédentes · √30).
  Prix PAYÉ = médiane des ACHATS du côté acheté dans (t + 1, t + 6] (donc après la décision), + frais preneur 0,07·p·(1 − p) par part ;
  achat seulement si ce prix est entre 0,05 et 0,95 ; gardé jusqu'au règlement. Un seul achat par règle, par actif et par créneau (1er instant).
RÈGLES FIGÉES (seuils choisis sur l'exploration seule) :
  R1 (ETH) : |dBTC| ≥ 0,10 et le marché ETH n'a pas bougé dans le même sens (signe(dBTC)·dETH ≤ 0) → acheter le côté ETH du mouvement BTC.
  R2 (SOL) : même règle sur le marché SOL.
  R3 (ETH + SOL) : correspondance logit(pALT) = a + b·logit(pBTC) ajustée sur l'exploration (par actif) ; si |pALT_attendu − pALT| ≥ 0,15,
       acheter le côté bon marché de l'ALT (Up si pALT < attendu, sinon Down).
  R4 (ETH + SOL) : |zB| ≥ 2 (BTC spot a bougé fort en 30 s) et le marché ALT n'a pas suivi (signe(zB)·dALT ≤ 0) → acheter le côté ALT du BTC.
TÉMOINS (descriptifs, pas des règles) : acheter Up / Down à t = 150 s sans condition (mesure la tendance de la période et le biais de la
  méthode de prix) ; R4 quand l'ALT a déjà suivi (signe(zB)·dALT > 0,05).
STATISTIQUES : ROI par dollar engagé, P&L à 10 $ par achat, IC par bootstrap des créneaux (4 000 tirages) : 90 % brut et 97,5 % (Bonferroni,
  4 règles). CRITÈRE : ROI > 0 en exploration ET en validation, ET borne basse de l'IC 97,5 % de la validation > 0. Sinon abandon.
  Aucun fantôme sans accord de Pitch.
Usage : python3 etude/bot5min/coherence_marches_h1082.py dossier_polytrades btc1s.npz dossier_cycles_dublin"""
import os, sys, json, gzip, glob, numpy as np, pandas as pd
ICI = os.path.dirname(os.path.abspath(__file__)); RNG = np.random.default_rng(1082)
DEBUT, FIN, CUT, BN_FIN = 1791676800, 1791849600, 1791780600, 1791763200
INST = list(range(30, 271, 10)); W, N = 10, 30
fee = lambda p: 0.07 * p * (1 - p)
lg = lambda p: np.log(np.clip(p, 0.02, 0.98) / (1 - np.clip(p, 0.02, 0.98)))


def charge_poly(fichiers):
    out = {}
    for f in sorted(fichiers):
        for k, m in json.load(gzip.open(f))["marches"].items():
            st = int(k)
            if not (DEBUT <= st < FIN): continue
            r = m.get("resultat") or {}; up = r.get("Up")
            up = None if up is None or 0.01 < float(up) < 0.99 else int(float(up) >= 0.99)
            T = np.array([(x[0] - st, x[4] if x[3] == "Up" else 1 - x[4], 1 if x[2] == "BUY" else 0, 1 if x[3] == "Up" else 0, x[4])
                          for x in m["trades"] if x[0] and x[4] and 0 < x[4] < 1 and x[3] in ("Up", "Down")], float).reshape(-1, 5)
            out[st] = (T[np.argsort(T[:, 0], kind="stable")], up)
    return out


def spot_btc(npz, dublin):
    a = np.full(FIN - DEBUT + 4000, np.nan); z = np.load(npz)
    k = z["t"].astype(int) - DEBUT + 3600; ok = (k >= 0) & (k < len(a)); a[k[ok]] = z["c"][ok]
    for f in sorted(glob.glob(os.path.join(dublin, "*", "*.json.gz"))):
        st = int(os.path.basename(f).split(".")[0])
        if not (BN_FIN - 300 <= st < FIN): continue
        try: L = json.load(gzip.open(f)).get("trx", {}).get("bn", [])
        except Exception: continue
        for x in L:
            s = int(x[1] // 1000)
            if s >= BN_FIN and s - DEBUT + 3600 < len(a): a[s - DEBUT + 3600] = float(x[3])
    return pd.Series(a).ffill(limit=5).values


def med(T, a, b):
    i0, i1 = np.searchsorted(T[:, 0], [a, b], side="right")
    return np.median(T[i0:i1, 1]) if i1 - i0 >= 2 else np.nan


def prix_entree(T, t, cote_up):
    i0, i1 = np.searchsorted(T[:, 0], [t + 1, t + 6], side="right"); x = T[i0:i1]
    x = x[(x[:, 2] == 1) & (x[:, 3] == cote_up)]
    return np.median(x[:, 4]) if len(x) else np.nan


def panneau(P, S):
    rows = []
    for alt in ("eth", "sol"):
        for st, (TA, upA) in sorted(P[alt].items()):
            if upA is None or len(TA) < 20: continue
            TB = P["btc"].get(st, (np.zeros((0, 5)), None))[0]
            if len(TB) < 50: TB = np.zeros((0, 5))
            for t in INST:
                i = st + t - DEBUT + 3600; c = S[i - 600:i + 1]
                zb = np.nan if np.isnan(c).any() else np.log(c[-1] / c[-1 - N]) / ((np.diff(np.log(c)).std() + 1e-12) * np.sqrt(N))
                rows.append(dict(st=st, alt=alt, t=t, pb=med(TB, t - W, t), pb0=med(TB, t - N - W, t - N), pa=med(TA, t - W, t),
                                 pa0=med(TA, t - N - W, t - N), up=upA, eu=prix_entree(TA, t, 1), ed=prix_entree(TA, t, 0), zb=zb))
    D = pd.DataFrame(rows); D["part"] = np.where(D.st < CUT, "exploration", "validation")
    D["dB"] = D.pb - D.pb0; D["dA"] = D.pa - D.pa0
    return D


def achats(D, m, cote):
    X = D[m.fillna(False)].copy(); c = cote[m.fillna(False)]
    X["px"] = np.where(c > 0, X.eu, X.ed); X["w"] = np.where(c > 0, X.up, 1 - X.up)
    X = X[np.isfinite(X.px) & (X.px >= 0.05) & (X.px <= 0.95)].sort_values(["st", "t"]).groupby(["alt", "st"]).head(1)
    X["pnl"] = X.w / (X.px + fee(X.px)) - 1                                    # par dollar engagé
    return X


def stats(x, B=4000):
    if len(x) == 0: return dict(n=0)
    g = x.groupby("st").pnl.agg(["sum", "count"]); s, n = g["sum"].values, g["count"].values
    idx = RNG.integers(0, len(g), (B, len(g))); roi = s[idx].sum(1) / n[idx].sum(1); tot = 10 * s[idx].sum(1)
    q = lambda v, a: np.percentile(v, [a, 100 - a])
    return dict(n=len(x), cyc=len(g), win=x.w.mean(), px=x.px.mean(), roi=x.pnl.mean(), pl=10 * x.pnl.sum(),
                roi90=q(roi, 5), roi975=q(roi, 1.25), pl90=q(tot, 5), pl975=q(tot, 1.25))


def main():
    poly, npz, dublin = sys.argv[1:4]
    P = {"btc": charge_poly(glob.glob(os.path.join(poly, "polytrades_2026-*.json.gz"))),
         "eth": charge_poly(glob.glob(os.path.join(poly, "polytrades_eth_*.json.gz"))),
         "sol": charge_poly(glob.glob(os.path.join(poly, "polytrades_sol_*.json.gz")))}
    D = panneau(P, spot_btc(npz, dublin))
    if os.environ.get("H1082_EXPLO_SEULE"): D = D[D.part == "exploration"]          # essai technique sans regarder la validation
    E = D[(D.part == "exploration")].dropna(subset=["pa", "pb"])
    fit = {a: np.polyfit(lg(x.pb), lg(x.pa), 1) for a, x in E.groupby("alt")}
    D["fa"] = [1 / (1 + np.exp(-(fit[a][0] * v + fit[a][1]))) for a, v in zip(D.alt, lg(D.pb))]
    sB, sZ, gap = np.sign(D.dB), np.sign(D.zb), D.fa - D.pa
    R = {"R1 ETH en retard sur le marché BTC": ((D.alt == "eth") & (D.dB.abs() >= 0.10) & (sB * D.dA <= 0), sB),
         "R2 SOL en retard sur le marché BTC": ((D.alt == "sol") & (D.dB.abs() >= 0.10) & (sB * D.dA <= 0), sB),
         "R3 écart à la correspondance BTC → ETH/SOL ≥ 0,15": ((gap.abs() >= 0.15) & D.pa.notna() & D.pb.notna(), np.sign(gap)),
         "R4 BTC spot a bougé (z ≥ 2), ETH/SOL pas suivi": ((D.zb.abs() >= 2) & (sZ * D.dA <= 0), sZ)}
    T = {"Témoin : Up à 150 s": (D.t == 150, pd.Series(1.0, index=D.index)), "Témoin : Down à 150 s": (D.t == 150, pd.Series(-1.0, index=D.index)),
         "Témoin : R4 mais ALT a déjà suivi": ((D.zb.abs() >= 2) & (sZ * D.dA > 0.05), sZ)}
    ncy = D.groupby("part").st.nunique().to_dict()
    o = ["# Bot95 — H1082 : cohérence entre marchés BTC / ETH / SOL 5 min (résultats bruts)\n",
         f"Créneaux : exploration {ncy.get('exploration')}, validation {ncy.get('validation')}. Correspondance (exploration) : "
         + ", ".join(f"{a.upper()} logit = {b:.3f}·logit(pBTC) {c:+.3f}" for a, (b, c) in fit.items()) + ". Aucun ordre.\n",
         "| Règle | Période | Achats | Créneaux | Gagnants | Prix moyen | ROI | IC 90 % du ROI | IC 97,5 % (Bonferroni) du ROI | P&L à 10 $ | IC 97,5 % du P&L |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    V = {}
    for nom, (m, c) in list(R.items()) + list(T.items()):
        X = achats(D, m, c)
        for pa in ("exploration", "validation"):
            s = stats(X[X.part == pa]); V[(nom, pa)] = s
            if s["n"] == 0: o.append(f"| {nom} | {pa} | 0 | | | | | | | | |"); continue
            o.append(f"| {nom} | {pa} | {s['n']} | {s['cyc']} | {100 * s['win']:.0f} % | {s['px']:.3f} | {100 * s['roi']:+.1f} % | "
                     f"[{100 * s['roi90'][0]:+.1f} ; {100 * s['roi90'][1]:+.1f}] % | [{100 * s['roi975'][0]:+.1f} ; {100 * s['roi975'][1]:+.1f}] % | "
                     f"{s['pl']:+.0f} $ | [{s['pl975'][0]:+.0f} ; {s['pl975'][1]:+.0f}] $ |")
    o.append("\n**Verdict (critère figé)**\n")
    for nom in R:
        e, v = V[(nom, "exploration")], V[(nom, "validation")]
        ok = e.get("n", 0) and v.get("n", 0) and e["roi"] > 0 and v["roi"] > 0 and v["roi975"][0] > 0
        o.append(f"- {nom} : {'candidat (proposition de fantôme à Pitch)' if ok else 'abandon'}")
    print("\n".join(o))


if __name__ == "__main__":
    main()
