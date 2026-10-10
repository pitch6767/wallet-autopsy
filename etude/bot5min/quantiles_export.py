"""Exporte les tables de quantiles des erreurs normalisées du moteur TWAP fin (modèle E), apprises sur la période d'apprentissage
(avant le 08.10 21:55), vers bot95/src/quantiles_twap.js pour le fantôme « TWAP fin quantiles ». Tables figées."""
import sys, json
sys.path.insert(0, "etude/bot5min")
exec(open("etude/bot5min/oracle_fiabilite.py").read().split("# ---- G :")[0])
T = {}
for (bk, rg), a in QS.items():
    T[f"{bk}|{rg}"] = {"n": int(len(a)), "q": [round(float(x), 4) for x in np.quantile(a, np.linspace(0, 1, 401))]}
src = ("// Tables figées (10.10.2026) : quantiles 0..100 % (pas de 0,25 %) de l'erreur normalisée u = (moyenne finale officielle − moyenne prévue) / écart-type du moteur,\n"
       "// par tranche de temps et par régime (calme = volatilité du perp < 2 $/s), apprises sur les cycles BTC avant le 08.10 21:55. Généré par etude/bot5min/quantiles_export.py.\n"
       "export const QTWAP = " + json.dumps(T, ensure_ascii=False) + ";\n")
open("bot95/src/quantiles_twap.js", "w").write(src); print({k: v["n"] for k, v in T.items()})
