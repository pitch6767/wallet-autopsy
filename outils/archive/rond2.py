import pickle,collections
C=pickle.load(open("cyc.pkl","rb")); F=pickle.load(open("F.pkl","rb"))
def fee(a): return 0.07*a*(1-a)
def per(j): return "07-14.10" if j<"10-15" else "15-23.10" if j<"10-24" else "24-31.10" if j<"11-01" else "01-06.11"
base=collections.defaultdict(lambda:[0,0.0])
for f in F:
    b=base[per(f["jour"])]; b[0]+=1; b[1]+=(f["res"]=="UP")-f["mid"]
print("référence : UP gagne de plus que son prix, tous moments:",{k:round(100*v[1]/v[0],1) for k,v in base.items()})
for dist in (30,60,100):
  for lo,hi in ((0.2,0.8),(0.05,0.95)):
    P=collections.defaultdict(lambda:[0.0,0]); vu=set(); J=collections.defaultdict(float)
    for f in F:
        if f["s"] in vu or not(60<=f["sec"]<=240): continue
        v=C[f["s"]].get(f["sec"]) or C[f["s"]].get(f["sec"]+1)
        if not v or not v[4]: continue
        if abs(v[4]-round(v[4]/1000)*1000)>dist: continue
        a,sz=f["da"],f["ds"]
        if not a or not sz or not(lo<=a<=hi): continue
        mise=min(50,sz*a)
        if mise<2: continue
        g=mise*((1/(a+fee(a))-1) if f["res"]=="DOWN" else -1); p=P[per(f["jour"])]; p[0]+=g; p[1]+=1; vu.add(f["s"]); J[f["jour"]]+=g
    print(f"acheter DOWN à ±{dist}$ d'un millier rond, prix {lo}-{hi}:",{k:(round(v[0]),v[1]) for k,v in sorted(P.items())},"jours positifs",sum(x>0 for x in J.values()),"/",len(J))
