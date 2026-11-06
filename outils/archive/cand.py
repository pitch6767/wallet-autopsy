import pickle,collections
F=pickle.load(open("F.pkl","rb"))
def fee(a): return 0.07*a*(1-a)
def per(j): return "07-14.10" if j<"10-15" else "15-23.10" if j<"10-24" else "24-31.10" if j<"11-01" else "01-06.11 (inédit)"
def run(nom,cond,choix,t0,t1):
    J=collections.defaultdict(float); P=collections.defaultdict(lambda:[0.0,0]); vu=set(); n=w=0; H=collections.defaultdict(float)
    for f in F:
        if not(t0<=f["sec"]<t1) or f["s"] in vu or not cond(f): continue
        c=choix(f)
        if not c: continue
        side,a,sz=c; mise=min(50,sz*a)
        if mise<2: continue
        g=mise*((1/(a+fee(a))-1) if f["res"]==side else -1)
        J[f["jour"]]+=g; P[per(f["jour"])][0]+=g; P[per(f["jour"])][1]+=1; vu.add(f["s"]); n+=1; w+=f["res"]==side
        H["nuit" if (f["h"]>=22 or f["h"]<7) else "jour"]+=g
    neg=sum(1 for v in J.values() if v<0)
    print(f"\n{nom}: {n} trades, {100*w/max(1,n):.1f} % gagnés, total {sum(J.values()):+.0f} $, jours négatifs {neg}/{len(J)}, nuit {H['nuit']:+.0f} / jour {H['jour']:+.0f}")
    for k in ("07-14.10","15-23.10","24-31.10","01-06.11 (inédit)"): print(f"   {k:18s} {P[k][0]:+7.0f} $ ({P[k][1]} trades)")
    return J
def mince(seuil,lo,hi):
    def c(f):
        d=f["desequilibre"]
        if abs(d)<seuil: return None
        side,a,sz=("DOWN",f["da"],f["ds"]) if d>0 else ("UP",f["ua"],f["us"])
        return (side,a,sz) if lo<=a<=hi and sz else None
    return c
J1=run("A. Favori 65-95 c dont l'offre est mince (déséq. ≥ 0,85), 2e-3e min",lambda f:True,mince(0.85,0.65,0.95),120,210)
J2=run("A'. idem déséq. ≥ 0,7",lambda f:True,mince(0.7,0.65,0.95),120,210)
def fav(lo,hi):
    def c(f):
        for side,a,sz in (("UP",f["ua"],f["us"]),("DOWN",f["da"],f["ds"])):
            if a and sz and lo<=a<=hi: return (side,a,sz)
    return c
for zmin in (2,2.5,3):
    run(f"B. Fin de cycle quasi sûre : |z| ≥ {zmin}, favori 90-98 c, 4e-5e min",lambda f,zm=zmin:abs(f["z"])>=zm,fav(0.90,0.98),240,280)
