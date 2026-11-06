import pickle,collections,datetime as dt,math,numpy as np
G=pickle.load(open("G.pkl","rb"))
def fee(a): return 0.07*a*(1-a)
for f in G:
    f["ratio"]=abs(f["btc30"])/(f["vol"]*math.sqrt(30/300)+1e-9)
    f["ratio_vol"]=f["perp_vol_30"]
xs=sorted(f["ratio"] for f in G if f["jour"]<"11-01"); q=[xs[int(len(xs)*p)] for p in (0.5,0.8,0.9,0.95)]
print("seuils ratio",[round(x,2) for x in q])
A=collections.defaultdict(lambda:[0,0.0,0.0])
for f in G:
    b=sum(f["ratio"]>t for t in q)
    for side,mid in (("UP",f["mid"]),("DOWN",1-f["mid"])):
        if 0.05<=mid<=0.35:
            a=A[(b,f["jour"]>="11-01")]; a[0]+=1; a[1]+=(f["res"]==side); a[2]+=mid
print("Jeton outsider (5-35 c) : gagne réel vs prix, selon l'explosion du BTC sur 30 s par rapport à sa volatilité de l'heure")
for b in range(5):
    x=[A[(b,False)],A[(b,True)]]
    print(f" palier {b}: "+" | ".join(f"{'test' if i else 'appr'} {a[0]:5d} pts écart {100*(a[1]-a[2])/max(1,a[0]):+.1f}" for i,a in enumerate(x)))
# stratégie : ouverture Wall Street, acheter l'outsider
def strat(nom,cond,lo=0.05,hi=0.35,t0=60,t1=240):
    J=collections.defaultdict(float); vu=set(); n=w=0
    for f in G:
        if f["s"] in vu or not(t0<=f["sec"]<t1) or not cond(f): continue
        for side,a,sz in (("UP",f["ua"],f["us"]),("DOWN",f["da"],f["ds"])):
            if a and sz and lo<=a<=hi:
                mise=min(50,sz*a)
                if mise<2: continue
                J[f["jour"]]+=mise*((1/(a+fee(a))-1) if f["res"]==side else -1); n+=1; w+=f["res"]==side; vu.add(f["s"]); break
    ap=sum(v for k,v in J.items() if k<"11-01"); te=sum(v for k,v in J.items() if k>="11-01")
    print(f"{nom}: {n} trades, gagnés {100*w/max(1,n):.0f} %, appr {ap:+.0f} $, test {te:+.0f} $, jours positifs {sum(v>0 for v in J.values())}/{len(J)}")
def tparis(f): return dt.datetime.fromtimestamp(f["s"],dt.timezone.utc)+dt.timedelta(hours=1)
def ouv(a,b):
    def c(f):
        t=tparis(f); m=t.hour*60+t.minute; return t.weekday()<5 and a<=m<=b
    return c
strat("Ouverture Wall Street 15:25-15:40, outsider 5-35 c",ouv(15*60+25,15*60+40))
strat("Ouverture Wall Street 15:30-15:35 seul, outsider 5-35 c",ouv(15*60+30,15*60+30))
strat("Chiffres US 14:25-14:40, outsider 5-35 c",ouv(14*60+25,14*60+40))
strat("Ouverture 15:25-15:40, outsider 35-50 c",ouv(15*60+25,15*60+40),0.35,0.5)
for p in (3,4):
    strat(f"Explosion BTC (palier {p}), outsider 5-35 c",lambda f,p=p: sum(f['ratio']>t for t in q)>=p)
