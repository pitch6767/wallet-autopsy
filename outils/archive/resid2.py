import pickle,statistics as st
F=pickle.load(open("G.pkl","rb"))
A=[f for f in F if f["jour"]<"11-01"]; T=[f for f in F if f["jour"]>="11-01"]
feats=[k for k in F[0] if k.startswith(("pm_","perp_","liq_","dublin","financement","base","coinbase"))]
for k in feats:
    xs=sorted(f[k] for f in A); q=[xs[int(len(xs)*i/5)] for i in range(1,5)]
    b=lambda x: sum(x>t for t in q)
    out=[]
    for D in (A,T):
        m=[[] for _ in range(5)]
        for f in D: m[b(f[k])].append((f["res"]=="UP")-f["mid"])
        out.append([100*st.mean(x) if x else 0 for x in m])
    rob= "  <== même sens" if (out[0][0]-out[0][4])*(out[1][0]-out[1][4])>0 and abs(out[0][0]-out[0][4])>1.5 and abs(out[1][0]-out[1][4])>1.5 else ""
    print(f"{k:26s} appr " + " ".join(f"{x:+5.1f}" for x in out[0]) + " | test " + " ".join(f"{x:+5.1f}" for x in out[1])+rob)
