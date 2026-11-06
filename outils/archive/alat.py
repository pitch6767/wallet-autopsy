import pickle,collections,datetime as dt
C=pickle.load(open("cyc.pkl","rb")); res,ptb,fin=pickle.load(open("off.pkl","rb"))
def fee(a): return 0.07*a*(1-a)
def run(seuil,lo,hi,t0,t1,lat,rafale=0.0,nom=""):
    J=collections.defaultdict(float); n=w=0; H=collections.defaultdict(float); mm=0
    for s,c in C.items():
        if s not in res: continue
        t=dt.datetime.fromtimestamp(s,dt.timezone.utc)+dt.timedelta(hours=1); j=t.strftime("%m-%d")
        for sec in range(t0,t1,5):
            v=c.get(sec)
            if not v or not v[0] or not v[2] or not v[1] or not v[3]: continue
            d=(v[1]-v[3])/(v[1]+v[3])
            if abs(d)<seuil: continue
            side,ia=("DOWN",2) if d>0 else ("UP",0)
            if not(lo<=v[ia]<=hi): continue
            e=c.get(sec+lat) or c.get(sec+lat+1)
            if not e or not e[ia] or not e[ia+1]: break
            a=e[ia]
            if a>v[ia]+rafale: break          # prix parti au-delà de la limite
            mise=min(50,e[ia+1]*a)
            if mise<2: break
            win=res[s]==side; g=mise*((1/(a+fee(a))-1) if win else -1); J[j]+=g; n+=1; w+=win; mm+=mise
            H[t.hour//3]+=g; break
    ap=sum(v for k,v in J.items() if k<"11-01"); te=sum(v for k,v in J.items() if k>="11-01"); neg=sum(1 for v in J.values() if v<0)
    print(f"{nom} latence {lat}s limite +{rafale*100:.0f}c: trades {n} gagnés {100*w/max(1,n):.1f}% mise moy {mm/max(1,n):.0f}$ | appr {ap:+.0f} | test {te:+.0f} | jours nég {neg}/{len(J)}")
    return H
for lat in (0,1,2,3):
    for raf in (0.0,0.02):
        H=run(0.85,0.65,0.95,120,210,lat,raf,"A")
print("A (latence 1 s) par tranche horaire de 3 h (heure de Paris):",{f"{k*3}h-{k*3+3}h":round(v) for k,v in sorted(run(0.85,0.65,0.95,120,210,1,0.0,"A").items())})
