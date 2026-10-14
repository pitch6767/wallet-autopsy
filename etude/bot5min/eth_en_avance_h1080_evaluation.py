"""H1080 — évaluation (14.10.2026) : exécute UNE fois la règle figée eth_en_avance_h1080.py (inchangée) en mode --confirmation,
sur un dossier ne contenant que les cycles Dublin >= 14.10.2026 00:00 UTC, puis calcule P&L, ROI et IC 90 % par cycles (bootstrap).
Usage : cd <dossier>/run && python3 eth_en_avance_h1080_evaluation.py   (les cycles dans <dossier>/rev_all/cycles/2026-10-14/...)"""
import sys, os, runpy, json, numpy as np
ICI = os.path.dirname(os.path.abspath(__file__))
sys.argv = [os.path.join(ICI, "eth_en_avance_h1080.py"), "--confirmation"]
g = runpy.run_path(sys.argv[0], run_name="__main__")
D, cycles = g["D"], g["cycles"]
EVAL = 1791936000  # 14.10.2026 00:00 UTC
cyc_eval = [s for s in cycles if s >= EVAL]
out = dict(cycles_disponibles=len(cyc_eval), premier=min(cyc_eval) if cyc_eval else None, dernier=max(cyc_eval) if cyc_eval else None, cas=0)
if len(D):
    D = D[D.st >= EVAL]
    out.update(cas=len(D), cycles_avec_cas=int(D.st.nunique()), gagnes=int(D.win.sum()), mise=round(D.c.sum(), 2), pnl=round(D.hold.sum(), 2),
               roi=round(100 * D.hold.sum() / D.c.sum(), 1), btc_suit_2s=round(float((D.btc_suit_2s > 0).mean()), 3),
               btc_2s_moy=round(float(D.btc_suit_2s.mean()), 1))
    per = D.groupby("st").agg(h=("hold", "sum"), c=("c", "sum")); rng = np.random.default_rng(1080); k = len(per)
    idx = rng.integers(0, k, (10000, k)); H = per.h.values[idx].sum(1); C = per.c.values[idx].sum(1)
    out.update(ic90_pnl=[round(float(np.percentile(H, 5)), 2), round(float(np.percentile(H, 95)), 2)],
               ic90_roi=[round(float(np.percentile(100 * H / C, 5)), 1), round(float(np.percentile(100 * H / C, 95)), 1)])
    D.to_csv("cas_h1080_evaluation.csv", index=False)
print(json.dumps(out, ensure_ascii=False, indent=1))
