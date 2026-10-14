import json, gzip, glob, os, numpy as np
files = sorted(glob.glob("../rev_all/*.json.gz")); res = {}; n = 0
SER = ["btc_by", "btc_bnspot", "btc_bnperp", "btc_okx", "btc_cb", "eth_by", "eth_bn", "sol_by", "sol_bn"]
acc = {s: np.zeros(41) for s in SER}; cnt = 0
for f in files:
    st = int(os.path.basename(f).split(".")[0])
    try: R = json.load(gzip.open(f))
    except Exception: continue
    d = R.get("deriv") or {}; t2 = R.get("trx2") or {}; tx = R.get("trx") or {}
    if not d.get("bn_perp_tx") or not t2.get("eth_by"): continue
    src = {"btc_by": [(r[0], r[3]) for r in tx.get("by", [])], "btc_bnspot": [(r[0], r[3]) for r in tx.get("bn", [])],
           "btc_bnperp": [(r[0], r[3]) for r in d.get("bn_perp_tx", [])], "eth_by": [(r[0], r[3]) for r in t2.get("eth_by", [])],
           "eth_bn": [(r[0], r[3]) for r in t2.get("eth_bn", [])], "sol_by": [(r[0], r[3]) for r in t2.get("sol_by", [])], "sol_bn": [(r[0], r[3]) for r in t2.get("sol_bn", [])]}
    ex = sorted(R.get("ex", []), key=lambda r: r[0])
    src["btc_okx"] = [(r[0], r[2][0]) for r in ex if r[2] and r[2][0]]; src["btc_cb"] = [(r[0], r[4][0]) for r in ex if r[4] and r[4][0]]
    grid = np.arange(st * 1000, st * 1000 + 300000, 100.0); G = {}
    ok = True
    for k, v in src.items():
        if len(v) < 50: ok = False; break
        a = np.array(sorted(v)); i = np.searchsorted(a[:, 0], grid, "right") - 1; i = np.clip(i, 0, None); p = a[i, 1]; p[grid < a[0, 0]] = np.nan
        G[k] = np.diff(np.log(p))
    if not ok: continue
    ref = G["btc_by"]; m0 = np.isfinite(ref)
    for k in SER:
        x = G[k]
        for j, lag in enumerate(range(-20, 21)):   # corr(x(t), ref(t+lag)) : lag > 0 → x en avance sur Bybit
            a = x[max(0, -lag):len(x) - max(0, lag)]; b = ref[max(0, lag):len(ref) - max(0, -lag)]
            mm = np.isfinite(a) & np.isfinite(b)
            if mm.sum() > 100 and a[mm].std() > 0 and b[mm].std() > 0: acc[k][j] += np.corrcoef(a[mm], b[mm])[0, 1]
    cnt += 1
print("cycles", cnt)
lags = np.arange(-20, 21) * 100
for k in SER:
    c = acc[k] / cnt; j = int(np.argmax(c))
    print(f"{k:11s} corrélation max {c[j]:.3f} au décalage {lags[j]:+5d} ms | en avance (100–500 ms) {c[21:26].round(3)} | en retard {c[15:20].round(3)}")
