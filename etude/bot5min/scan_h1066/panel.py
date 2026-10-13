"""Panneau 1 s par cycle : Polymarket + bourses + Chainlink, pour le scan des renversements / accélérations."""
import sys, json, gzip, numpy as np, pandas as pd
sys.path.insert(0, "/home/claude/wallet-autopsy/etude/bot5min")
import liquidite_h833 as L, reversal_h1003 as RV
G, cyc = L.grille(sys.argv[1]); Y = L.resultats_officiels(cyc)
cycles = sorted(s for s in cyc if s in Y)
dev = [s for s in cycles if s < RV.DEV_FIN]; tr = set(dev[:len(dev) * 2 // 3]); va = set(dev[len(dev) * 2 // 3:])
part = lambda s: "A" if s in tr else ("V" if s in va else "T")
GK = ["perp", "okx", "bn", "cb", "cl", "bid", "ask", "s1b", "s1a", "cb10", "ca10", "byb", "bya", "dec_b", "dec_a", "add_b", "add_a", "ofi", "agb", "ags", "agb_by", "ags_by", "mur_b", "mur_a"]
out = []
for st in cycles:
    try: R = json.load(gzip.open(cyc[st]["f"]))
    except Exception: continue
    i0 = st - G["t0"]
    D = pd.DataFrame({k: G[k][i0:i0 + 300] for k in GK}); D["s"] = np.arange(300); D["st"] = st; D["y"] = Y[st]; D["part"] = part(st)
    D["strike"] = (R.get("marche") or {}).get("strike") or np.nan
    um = np.full(300, np.nan); usp = np.full(300, np.nan); db = np.full(300, np.nan); da = np.full(300, np.nan)
    for r in R.get("snap", []):
        s = int(r[0] // 1000) - st
        if not (0 <= s < 300) or not r[1] or not r[2]: continue
        b, a = r[1][0][0], r[2][0][0]; um[s] = (a + b) / 2; usp[s] = a - b
        db[s] = sum(x[1] for x in r[1]); da[s] = sum(x[1] for x in r[2])
    D["um"] = pd.Series(um).ffill(limit=3).values; D["usp"] = usp; D["udb"] = db; D["uda"] = da
    pv = np.zeros(300); pf = np.zeros(300); pn = np.zeros(300); pbig = np.zeros(300)
    for r in R.get("ev", []):
        if not r or r[0] != "T" or len(r) < 7: continue
        s = int(r[1] // 1000) - st
        if not (0 <= s < 300): continue
        k, side, px, sz = r[3], r[4], r[5], r[6]; usd = px * sz
        up = (k == 0) == (side == 1)
        pv[s] += usd; pf[s] += usd if up else -usd; pn[s] += 1
        if usd >= 150: pbig[s] += 1 if up else -1
    D["pv"], D["pf"], D["pn"], D["pbig"] = pv, pf, pn, pbig
    tw = np.full(300, np.nan)
    for r in R.get("tw", []) or []:
        s = int(r[1] // 1000) - st
        if 0 <= s < 300: tw[s] = r[2]
    D["tw"] = pd.Series(tw).ffill().values
    liq = np.zeros(300); oi = np.full(300, np.nan)
    dv = R.get("deriv") or {}
    for r in dv.get("bn_liq", []) or []:
        s = int(r[1] // 1000) - st
        if 0 <= s < 300: liq[s] += (1 if r[2] == "BUY" else -1) * r[3] * r[4]
    for r in dv.get("bn_oi", []) or []:
        s = int(r[1] // 1000) - st
        if 0 <= s < 300: oi[s] = r[2]
    D["liq"] = liq; D["oi"] = pd.Series(oi).ffill().values
    out.append(D)
P = pd.concat(out, ignore_index=True); P.to_pickle(sys.argv[2]); print("FIN", P.st.nunique(), len(P), P.groupby("part").st.nunique().to_dict())
