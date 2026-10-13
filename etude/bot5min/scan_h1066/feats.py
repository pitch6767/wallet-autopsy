import numpy as np, pandas as pd
P = pd.read_pickle("panel.pkl").sort_values(["st", "s"])
rows = []
prev = {}
for st, D in P.groupby("st", sort=True):
    D = D.reset_index(drop=True)
    g = lambda k: D[k].values.astype(float)
    perp, cl, um, bn = g("perp"), g("cl"), g("um"), g("bn")
    K = D.strike.iloc[0]; y = D.y.iloc[0]
    dperp = np.diff(perp, prepend=np.nan)
    agg = g("agb") - g("ags") + g("agb_by") - g("ags_by")
    cs = lambda x: np.concatenate([[0], np.cumsum(np.nan_to_num(x))])
    C = {k: cs(v) for k, v in dict(agg=agg, ofi=g("ofi"), pf=g("pf"), pv=g("pv"), pn=g("pn"), pbig=g("pbig"), liq=g("liq"),
                                   decb=g("dec_b"), deca=g("dec_a"), addb=g("add_b"), adda=g("add_a"), agv=g("agb") + g("ags")).items()}
    W = lambda k, t, w: C[k][t + 1] - C[k][max(t + 1 - w, 0)]
    cross = np.concatenate([[0], np.cumsum(np.abs(np.diff(np.sign(np.nan_to_num(um, nan=0.5) - 0.5))) > 0)])
    pr = prev.get(st - 300)
    for t in range(20, 295):
        if not np.isfinite(um[t]) or not np.isfinite(perp[t]): continue
        sg = 1 if um[t] >= 0.5 else -1; fp = um[t] if sg > 0 else 1 - um[t]
        v30 = np.nanstd(dperp[max(t - 29, 1):t + 1]); v120 = np.nanstd(dperp[max(t - 119, 1):t + 1])
        rest = 300 - t
        f = dict(st=st, t=t, part=D.part.iloc[0], fp=fp, sg=sg, lost=int((y == 1.0) != (sg > 0)),
                 v30=v30, v120=v120, vratio=v30 / v120 if v120 > 0 else np.nan)
        for w in (5, 15, 30, 60):
            f[f"rp{w}"] = sg * (perp[t] - perp[max(t - w, 0)]) / (v30 * np.sqrt(w) + 1e-9)
            f[f"rum{w}"] = sg * (um[t] - um[max(t - w, 0)]) if np.isfinite(um[max(t - w, 0)]) else np.nan
        f["zcl"] = sg * (cl[t] - K) / (v120 * np.sqrt(rest) + 1e-9) if np.isfinite(cl[t]) and np.isfinite(K) else np.nan
        f["zperp"] = sg * (perp[t] - K) / (v120 * np.sqrt(rest) + 1e-9) if np.isfinite(K) else np.nan
        f["cl_perp"] = sg * (cl[t] - perp[t]) if np.isfinite(cl[t]) else np.nan
        f["bn_perp"] = sg * (bn[t] - perp[t]) if np.isfinite(bn[t]) else np.nan
        f["cb_perp"] = sg * (D.cb.values[t] - perp[t])
        f["okx_perp"] = sg * (D.okx.values[t] - perp[t])
        f["by_bn"] = sg * ((D.byb.values[t] + D.bya.values[t]) / 2 - bn[t]) if np.isfinite(bn[t]) else np.nan
        tw = D.tw.values[t]; f["ztw"] = sg * (tw - K) / (v120 * np.sqrt(rest) + 1e-9) if np.isfinite(tw) and np.isfinite(K) else np.nan
        for w in (10, 30):
            av = W("agv", t, w)
            f[f"agg{w}"] = sg * W("agg", t, w) / (av + 1e-9)
            f[f"ofi{w}"] = sg * W("ofi", t, w)
            pv = W("pv", t, w); f[f"pf{w}"] = sg * W("pf", t, w) / (pv + 1e-9); f[f"pv{w}"] = pv
            f[f"pbig{w}"] = sg * W("pbig", t, w); f[f"liq{w}"] = sg * W("liq", t, w)
        f["pv_surge"] = W("pv", t, 30) / (C["pv"][t + 1] / (t + 1) * 30 + 1e-9)
        f["agv_surge"] = W("agv", t, 30) / (C["agv"][t + 1] / (t + 1) * 30 + 1e-9)
        cb10, ca10 = D.cb10.values[t], D.ca10.values[t]; f["bimb"] = sg * (cb10 - ca10) / (cb10 + ca10 + 1e-9)
        f["pull"] = sg * ((W("decb", t, 10) - W("addb", t, 10)) - (W("deca", t, 10) - W("adda", t, 10)))
        mb, ma = D.mur_b.values[t], D.mur_a.values[t]; f["mur"] = sg * (np.sign(np.nan_to_num(mb)) - np.sign(np.nan_to_num(ma)))
        udb, uda = D.udb.values[t], D.uda.values[t]; f["pimb"] = sg * (udb - uda) / (udb + uda + 1e-9) if np.isfinite(udb) else np.nan
        f["usp"] = D.usp.values[t]
        f["cross"] = cross[t]; f["fpmax"] = np.nanmax(np.where(sg > 0, um[:t + 1], 1 - um[:t + 1])); f["fade"] = f["fpmax"] - fp
        f["umvol30"] = np.nanstd(np.diff(um[max(t - 30, 0):t + 1]))
        rng = np.nanmax(perp[:t + 1]) - np.nanmin(perp[:t + 1]); f["range_z"] = rng / (v120 * np.sqrt(t) + 1e-9)
        oi = D.oi.values; f["doi30"] = (oi[t] - oi[max(t - 30, 0)]) if np.isfinite(oi[t]) and np.isfinite(oi[max(t - 30, 0)]) else np.nan
        f["hour"] = ((st % 86400) // 3600); f["prev_same"] = (np.nan if pr is None else int((pr > 0.5) == (sg > 0)))
        # accélération à venir (10 s)
        if t + 10 < 300 and np.isfinite(um[t + 10]): f["acc10"] = um[t + 10] - um[t]; f["acc10s"] = sg * (um[t + 10] - um[t])
        rows.append(f)
    prev[st] = y
F = pd.DataFrame(rows); F.to_pickle("feats.pkl"); print("FIN", F.shape)
