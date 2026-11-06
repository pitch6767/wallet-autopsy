import pickle,collections
C=pickle.load(open("cyc.pkl","rb")); F=pickle.load(open("F.pkl","rb"))
A=collections.defaultdict(lambda:[0,0.0])
for f in F:
    if not(60<=f["sec"]<=240): continue
    v=C[f["s"]].get(f["sec"]) or C[f["s"]].get(f["sec"]+1)
    if not v or not v[4]: continue
    P=v[4]
    for pas in (500,1000):
        r=round(P/pas)*pas; d=P-r
        if abs(d)>60: continue
        # le niveau rond est juste AU-DESSUS (d<0) ou AU-DESSOUS (d>0) : le prix est-il repoussé ?
        cle=(pas,"juste sous un chiffre rond" if d<0 else "juste au-dessus d'un chiffre rond",f["jour"]>="11-01")
        a=A[cle]; a[0]+=1; a[1]+=(f["res"]=="UP")-f["mid"]
for k in sorted(A): print(k[0],"$",k[1],"test" if k[2] else "appr",A[k][0],"pts, UP gagne",f"{100*A[k][1]/A[k][0]:+.1f} pts de plus que son prix")
