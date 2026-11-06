import pickle,collections
F=pickle.load(open("F.pkl","rb"))
def fee(a): return 0.07*a*(1-a)
def run(seuil,lo,hi,t0,t1,cap=50,un=True):
    J=collections.defaultdict(float); n=w=0; vu=set(); mises=0
    for f in F:
        if not(t0<=f["sec"]<t1) or (un and f["s"] in vu): continue
        d=f["desequilibre"]
        if abs(d)<seuil: continue
        side,a,sz=("DOWN",f["da"],f["ds"]) if d>0 else ("UP",f["ua"],f["us"])   # côté dont l'offre est mince
        if not(lo<=a<=hi) or not sz: continue
        mise=min(cap,sz*a)
        if mise<2: continue
        win=f["res"]==side; J[f["jour"]]+=mise*((1/(a+fee(a))-1) if win else -1); n+=1; w+=win; vu.add(f["s"]); mises+=mise
    ap=sum(v for k,v in J.items() if k<"11-01"); te=sum(v for k,v in J.items() if k>="11-01"); neg=sum(1 for v in J.values() if v<0)
    return n,w,ap,te,neg,len(J),mises/max(1,n)
print("Acheter le côté dont l'OFFRE est mince (peu de vendeurs au meilleur prix)")
for seuil in (0.5,0.7,0.85):
  for lo,hi in ((0.05,0.35),(0.35,0.65),(0.65,0.95),(0.05,0.95)):
    for t0,t1 in ((30,120),(120,210),(210,280),(30,280)):
      n,w,ap,te,neg,nj,m=run(seuil,lo,hi,t0,t1)
      fl=" <==" if ap>0 and te>0 and n>100 else ""
      print(f"désequilibre ≥{seuil} prix {lo}-{hi} sec {t0}-{t1}: trades {n:5d} gagnés {100*w/max(1,n):4.1f}% mise moy {m:4.0f}$ | appr {ap:+7.0f} | test {te:+6.0f} | jours nég {neg}/{nj}{fl}")
