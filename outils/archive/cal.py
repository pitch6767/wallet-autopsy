import pickle,collections,statistics as st
R=pickle.load(open("rows.pkl","rb"))
med=st.median({r["s"]:r["vol"] for r in R}.values())
# un point par cycle et par minute (sec 30,90,150,210,270), côté UP ; prix "mid" = (ask_up + 1-ask_down)/2
A=collections.defaultdict(lambda:[0,0,0.0])
for r in R:
    if r["sec"]%60!=30 or not r["ua"] or not r["da"]: continue
    mid=(r["ua"]+1-r["da"])/2
    for side,m in (("UP",mid),("DOWN",1-mid)):
        b=min(9,int(m*10)); per="test" if r["jour"]>="11-01" else "appr"
        reg=("nuit" if (r["h"]>=22 or r["h"]<7) else "jour")+("/calme" if r["vol"]<med else "/agité")
        for key in ((per,"tous",b),(per,reg,b)):
            a=A[key]; a[0]+=1; a[1]+=(r["res"]==side); a[2]+=m
print("prix milieu | régime | appr: n, % gagnés réel vs prix | test: n, % réel vs prix")
for reg in ("tous","nuit/calme","nuit/agité","jour/calme","jour/agité"):
    for b in range(10):
        a=A[("appr",reg,b)]; t=A[("test",reg,b)]
        if a[0]<30: continue
        f=lambda x:(x[0], 100*x[1]/max(1,x[0]), 100*x[2]/max(1,x[0]))
        fa,ft=f(a),f(t)
        print(f"{b/10:.1f}-{(b+1)/10:.1f} {reg:11s} | {fa[0]:5d} réel {fa[1]:5.1f} % prix {fa[2]:5.1f} % écart {fa[1]-fa[2]:+5.1f} | {ft[0]:5d} réel {ft[1]:5.1f} % prix {ft[2]:5.1f} % écart {ft[1]-ft[2]:+5.1f}")
