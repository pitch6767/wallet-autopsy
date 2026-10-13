import numpy as np, pandas as pd
T = pd.read_pickle("trades_feats2.pkl"); P = pd.read_pickle("panel.pkl").set_index(["st", "s"]); F = pd.read_pickle("feats.pkl").set_index(["st", "t"])
U = pd.read_pickle("pulls.pkl").sort_values(["st", "s"])
for c in ["decb", "deca", "addb", "adda"]: U[c + "3"] = U.groupby("st")[c].transform(lambda x: x.rolling(3, min_periods=1).sum())
U["pressUp"] = ((U.addb3 - U.decb3) - (U.adda3 - U.deca3)) / (U.addb3 + U.decb3 + U.adda3 + U.deca3 + 1); Ui = U.set_index(["st", "s"])
k = pd.MultiIndex.from_arrays([T.st, T.s]); k1 = pd.MultiIndex.from_arrays([T.st, T.s - 1]); sx = np.where(T.cote == "Up", 1, -1)
T["press"] = sx * Ui.pressUp.reindex(k1).values
T["depth"] = np.where(sx > 0, P.udb.reindex(k1).values, P.uda.reindex(k1).values)
T["rp5"] = sx * (P.perp.reindex(k1).values - P.perp.reindex(pd.MultiIndex.from_arrays([T.st, T.s - 6])).values)
T["clp"] = sx * (P.cl.reindex(k1).values - P.perp.reindex(k1).values)
T["heure"] = ((T.st // 3600) + 2) % 24
dmed = np.nanmedian(T[T.part == "A"].depth)
FILTRES = {
    "carnet Poly pour nous": T.pimb > 0, "écart Poly ≤ 1 c": T.usp <= 0.011, "cycle calme (≤ 2 passages à 0,5)": T.cross <= 2,
    "contre la foule (flux 30 s)": T.pf30 <= -0.296, "pression carnet pour nous": T.press > 0, "élan perp 30 s pour nous": T.m30 > 0,
    "élan perp 30 s contre nous": T.m30 < 0, "marché calme (vol 5 min < 1 h)": T.vr < 1, "pas de saut Bybit contre (10 s)": ~T.by10c,
    "Poly a monté pour nous (5 s)": T.poly5 > 0, "perp pour nous (5 s)": T.rp5 > 0, "pas la nuit (02 h – 10 h)": ~T.heure.between(2, 9),
    "profondeur de notre côté > médiane": T.depth > dmed, "côté le moins cher (prix < 0,5)": T.prix < 0.5, "pas fenêtre :00/:30": ~T.m00,
    "Chainlink au-dessus du perp pour nous": T.clp > 0, "carnet Binance pour nous": T.bimb > 0, "reste > 120 s": T.rest > 120,
}
FILTRES = {k: v.fillna(False).values.astype(bool) for k, v in FILTRES.items()}
T = T.reset_index(drop=True)
keep = ~T.nom.str.contains("ETH").values
T = T[keep].reset_index(drop=True); FILTRES = {k: v[keep] for k, v in FILTRES.items()}
def pnl(m, part): x = T[m & (T.part.values == part)]; return x.net.sum(), len(x), (100 * x.net.sum() / x.c.sum() if len(x) else np.nan)
def glouton(base):
    m = base.copy(); used = []; steps = [("base", m.copy())]
    for _ in range(10):
        best = None; bA = pnl(m, "A")[0]
        for nom, f in FILTRES.items():
            if nom in used: continue
            mm = m & f; a, n, _ = pnl(mm, "A")
            if n >= 10 and a > bA + 1e-9 and (best is None or a > best[1]): best = (nom, a, mm)
        if best is None: break
        used.append(best[0]); m = best[2]; steps.append(("+ " + best[0], m.copy()))
    return steps
def ligne(nom, m):
    r = [nom]
    for p in "AVT": s, n, roi = pnl(m, p); r += [n, round(s), None if np.isnan(roi) else round(roi)]
    return r
cols = ["étape", "n A", "P&L A", "ROI A", "n V", "P&L V", "ROI V", "n T", "P&L T", "ROI T"]
out = ["# Bot95 — H1076 : chaque stratégie, filtres ajoutés un par un (sélection sur l'apprentissage)\n",
       "Demande de Pitch (14.10.2026 00:06). 7 442 trades BTC (11.10 08:05 → 12.10 24:00) ; 18 filtres trouvés le 13.10. À chaque étape on ajoute le filtre qui",
       "augmente le plus le P&L de l'APPRENTISSAGE (au moins 10 trades gardés) ; validation et test sont seulement regardés. Arrêt quand plus rien n'améliore",
       "l'apprentissage, ou à 10 filtres. Aucun ordre ; exploration (les filtres eux-mêmes ont été trouvés en regardant les 3 périodes).\n"]
resume = []
groups = [("TOUTES LES STRATÉGIES ENSEMBLE", np.ones(len(T), bool))] + [(n, (T.nom == n).values) for n in T.nom.value_counts().index if (T.nom == n).sum() >= 30]
for nom, base in groups:
    st = glouton(base); rows = [ligne(e, m) for e, m in st]
    D = pd.DataFrame(rows, columns=cols)
    out.append(f"## {nom}\n"); out.append(D.to_markdown(index=False)); out.append("")
    b, f = rows[0], rows[-1]; resume.append((nom, len(st) - 1, b[2], f[2], b[5], f[5], b[8], f[8], f[0]))
R = pd.DataFrame(resume, columns=["stratégie", "filtres", "A base", "A filtré", "V base", "V filtré", "T base", "T filtré", "dernier filtre"])
out.insert(5, "## Résumé (P&L en $)\n\n" + R.to_markdown(index=False) + "\n")
open("empile.md", "w").write("\n".join(out)); R.to_pickle("empile_R.pkl")
