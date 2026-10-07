"""Meta-modele « desaccord vrai ou faux » + gain attendu + fonction de reaction de Polymarket — 12 jours (07.10.2026).
1. Candidats : chaque seconde ou le modele depasse le prix de marche d'au moins 5 c (un candidat par cycle et par cote, le premier achetable),
   achat au prix d'un vrai acheteur dans les 2 s, garde jusqu'au resultat, gain pour 50 $.
2. Regles simples figees : seuil fixe (+20 pts) contre gain attendu par dollar (+25 / +50 / +100 %), modes loterie / normal / cher.
3. Fonction de reaction : de combien le prix Polymarket bouge normalement en 3 s quand le modele bouge (appris j1-8) ; residu = retard de Polymarket.
4. LightGBM sur j1-8 (variables connues AVANT l'achat), jugement j9-12, explication SHAP des variables.
"""
import sys, time, statistics, collections, math
import numpy as np
from datetime import datetime, timezone
sys.argv = [sys.argv[0], sys.argv[1] if len(sys.argv) > 1 else "12"]
sys.path.insert(0, "etude/bot5min")
import combinaisons as CB

OUT = "etude/bot5min/"
FEE = lambda p: 0.072 * p * (1 - p)


def candidats(D, A, seuil=0.05):
    out = []
    for st, c in D[A].items():
        up, pm, vu, sp = c["up"], c["pm"], c["vu"], c["sp"]
        faits = set()
        for k in range(16, 295):
            if vu[k] < k - 3 or np.isnan(pm[k]) or np.isnan(up[k]): continue
            for s in (1, -1):
                if s in faits: continue
                fair = pm[k] if s > 0 else 1 - pm[k]; mkt = up[k] if s > 0 else 1 - up[k]
                if fair - mkt < seuil: continue
                X = c["bu"] if s > 0 else c["bd"]
                f_ = min(X[k + 1], X[k + 2])
                if not (f_ <= mkt + 0.01 + 1e-9) or not (0.02 <= f_ <= 0.97): continue
                faits.add(s)
                d = lambda arr, n: float((arr[k] - arr[k - n]) * s) if not np.isnan(arr[k - n]) and not np.isnan(arr[k]) else 0.0
                rets = [d(sp, n) / sp[k] * 1e4 if not np.isnan(sp[k]) else 0.0 for n in (1, 3, 5, 15)]
                vol = float(np.nanstd(np.diff(sp[max(0, k - 30):k + 1])) / sp[k] * 1e4) if k > 5 else 0.0
                edge = lambda j: (pm[j] - up[j]) * s
                gagne = (c["g"] == 1) == (s > 0)
                out.append({"st": st, "s": s, "A": A, "tl": 300 - k, "prix": float(f_), "fair": float(fair), "edge": float(fair - f_), "ratio": float(fair / f_),
                            "v1": float(edge(k) - edge(k - 1)), "v3": float(edge(k) - edge(k - 3)), "acc": float((edge(k) - edge(k - 1)) - (edge(k - 1) - edge(k - 2))),
                            "dpm3": d(pm, 3), "dup3": d(up, 3), "dup10": d(up, 10), "r1": rets[0], "r3": rets[1], "r5": rets[2], "r15": rets[3], "vol": vol,
                            "heure": (datetime.fromtimestamp(st, timezone.utc).hour + 2) % 24, "g": gagne,
                            "pnl": float(((1 if gagne else 0) - f_ - FEE(f_)) * 50 / f_)})
    return out


def resume(X):
    if not X: return "—"
    return f"{len(X)} trades · {statistics.mean(x['pnl'] for x in X):+.2f} $/trade · total {sum(x['pnl'] for x in X):+.0f} $ · {100 * statistics.mean(1 if x['g'] else 0 for x in X):.0f} % gagnants"


def main():
    J_ = CB.JOURS
    fin = int(time.time()) // 86400 * 86400 - 300
    debut = fin + 300 - J_ * 86400
    jours = sorted({datetime.fromtimestamp(t, timezone.utc).strftime("%Y-%m-%d") for t in range(debut - 3700, fin + 600, 3600)})
    jours = [j for j in jours if j < datetime.now(timezone.utc).strftime("%Y-%m-%d")]
    coupe = debut + int(J_ * 2 / 3) * 86400
    D = {"btc": CB.preparer("btc", "BTCUSDT", jours, debut, fin, coupe), "eth": CB.preparer("eth", "ETHUSDT", jours, debut, fin, coupe)}
    C = candidats(D, "btc") + candidats(D, "eth")
    a_ = [x for x in C if x["st"] < coupe]; b_ = [x for x in C if x["st"] >= coupe]
    rap = [f"# Meta-modele, gain attendu, reaction de Polymarket — {J_} jours ({jours[1]} -> {jours[-1]})", "",
           f"{len(C)} candidats (modele >= marche + 5 c, achetables) — j1-8 : {len(a_)}, j9-12 : {len(b_)}. Gain pour 50 $ par trade, frais compris.", ""]
    # ---- 3. fonction de reaction (j1-8) : dup3 ~ beta * dpm3
    xs = np.array([x["dpm3"] for x in a_]); ys = np.array([x["dup3"] for x in a_])
    beta = float((xs * ys).sum() / max((xs * xs).sum(), 1e-9))
    for x in C: x["residu"] = x["dup3"] - beta * x["dpm3"]          # negatif = Polymarket a moins suivi que d'habitude (en retard)
    rap += [f"Fonction de reaction (j1-8) : en 3 s, Polymarket bouge en moyenne de **{beta:.2f} fois** le mouvement du modele. Residu < 0 = Polymarket en retard.", ""]
    # ---- 2. regles simples figees
    R = {
        "seuil fixe +20 pts (actuel)": lambda x: x["edge"] >= 0.20,
        "seuil fixe +10 pts": lambda x: x["edge"] >= 0.10,
        "gain attendu >= +25 % / $": lambda x: x["ratio"] >= 1.25 and x["edge"] >= 0.05,
        "gain attendu >= +50 % / $": lambda x: x["ratio"] >= 1.5 and x["edge"] >= 0.05,
        "gain attendu >= +100 % / $": lambda x: x["ratio"] >= 2.0 and x["edge"] >= 0.05,
        "loterie (prix <= 0,10, modele >= 2x)": lambda x: x["prix"] <= 0.10 and x["ratio"] >= 2,
        "normal (0,10-0,35, +20 pts)": lambda x: 0.10 < x["prix"] <= 0.35 and x["edge"] >= 0.20,
        "cher (> 0,35, +10 pts)": lambda x: x["prix"] > 0.35 and x["edge"] >= 0.10,
        "Polymarket en retard (residu <= -0,03) + gain >= 50 %": lambda x: x["residu"] <= -0.03 and x["ratio"] >= 1.5 and x["edge"] >= 0.05,
        "Polymarket en retard + spot avec nous (3 s)": lambda x: x["residu"] <= -0.03 and x["r3"] > 0 and x["edge"] >= 0.05,
        "gain >= 50 % + spot avec nous (5 s)": lambda x: x["ratio"] >= 1.5 and x["edge"] >= 0.05 and x["r5"] >= 0,
        "gain >= 50 % + ecart qui grandit (3 s)": lambda x: x["ratio"] >= 1.5 and x["edge"] >= 0.05 and x["v3"] > 0,
    }
    rap += ["## Regles simples (figees, aucune optimisation)", "", "| Regle | j1-8 | **j9-12 (verification)** |", "|---|---|---|"]
    for nom, f in R.items():
        rap.append(f"| {nom} | {resume([x for x in a_ if f(x)])} | **{resume([x for x in b_ if f(x)])}** |")
    # ---- 4. LightGBM
    try:
        import lightgbm as lgb
        F = ["tl", "prix", "fair", "edge", "ratio", "v1", "v3", "acc", "dpm3", "dup3", "dup10", "r1", "r3", "r5", "r15", "vol", "heure", "residu"]
        Xa = np.array([[x[f] for f in F] + [1 if x["A"] == "btc" else 0] for x in a_]); ya = np.array([x["pnl"] for x in a_])
        Xb = np.array([[x[f] for f in F] + [1 if x["A"] == "btc" else 0] for x in b_])
        m = lgb.LGBMRegressor(n_estimators=300, learning_rate=0.03, num_leaves=15, min_child_samples=80, subsample=0.8, subsample_freq=1, colsample_bytree=0.8, verbose=-1)
        m.fit(Xa, ya)
        pa = m.predict(Xa); pb = m.predict(Xb)
        rap += ["", "## Meta-modele LightGBM (appris j1-8, gain attendu predit pour chaque candidat)", "",
                "| On achete si le gain predit depasse | j1-8 (appris, optimiste) | **j9-12 (jamais vu)** |", "|---|---|---|"]
        for q in (0, 2, 5, 10, 20):
            rap.append(f"| {q} $ | {resume([x for x, p in zip(a_, pa) if p > q])} | **{resume([x for x, p in zip(b_, pb) if p > q])}** |")
        try:
            import shap
            ex = shap.TreeExplainer(m); sv = ex.shap_values(Xb[:3000])
            imp = sorted(zip(F + ["btc"], np.abs(sv).mean(0)), key=lambda z: -z[1])
            rap += ["", "Variables les plus utiles (SHAP, j9-12) : " + " · ".join(f"{n} {v:.2f}" for n, v in imp[:10])]
        except Exception as e: rap.append(f"SHAP : {e}")
    except Exception as e:
        rap.append(f"LightGBM : erreur {e}")
    open(OUT + "resultat_meta.md", "w").write("\n".join(rap))
    print("\n".join(rap))


if __name__ == "__main__":
    main()
