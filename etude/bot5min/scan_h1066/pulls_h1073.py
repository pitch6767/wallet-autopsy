import json, gzip, glob, os, numpy as np, pandas as pd
rows = []
for f in sorted(glob.glob("../rev_all/*.json.gz")):
    st = int(os.path.basename(f).split(".")[0])
    try: R = json.load(gzip.open(f))
    except Exception: continue
    p = R.get("p")
    if not isinstance(p, list) or not p: continue
    A = np.zeros((300, 4))  # dec_b, dec_a, add_b, add_a
    t = 0; last = {}
    for k, x in enumerate(p):
        t = x[0] if k == 0 else t + x[0]
        s = int(t // 1000) - st; key = (x[2], x[3]); q = x[4] / 100; q0 = last.get(key, 0); last[key] = q
        if 0 <= s < 300:
            d = q - q0
            if d < 0: A[s, x[2]] += -d
            else: A[s, 2 + x[2]] += d
    D = pd.DataFrame(A, columns=["decb", "deca", "addb", "adda"]); D["st"] = st; D["s"] = np.arange(300); rows.append(D)
P = pd.concat(rows); P.to_pickle("pulls.pkl"); print(P.shape, P[["decb", "deca", "addb", "adda"]].mean().round(1).to_dict())
