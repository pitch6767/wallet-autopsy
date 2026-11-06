import pickle,numpy as np,collections,datetime as dt
M,PM=pickle.load(open("series.pkl","rb")); t0=int(np.load("t0.npy")[0])
CE=pickle.load(open("cycE.pkl","rb")); resE=pickle.load(open("resE.pkl","rb")); CB=pickle.load(open("cyc.pkl","rb")); res,ptb,fin=pickle.load(open("off.pkl","rb"))
def fee(a): return 0.07*a*(1-a)
P=np.log(M["okx_perp"]); n=len(P)
def run(nom,C,R,X,off,garde=False):
    mk=[];last=-99;J=collections.defaultdict(float);k=w=0
    for i in range(2,n-6):
        if np.isnan(P[i]) or np.isnan(P[i-1]): continue
        d=(P[i]-P[i-1])*1e4
        if abs(d)<X or i-last<5: continue
        t=i+t0; s=t-t%300; sec=t%300
        if s not in R or sec<5 or sec>285: continue
        c=C.get(s,{}); pre=c.get(sec+off); post=c.get(sec+5)
        if not pre or not post: continue
        ia=0 if d>0 else 2; bid=post[7] if ia==0 else post[8]; a=pre[ia]
        if a is None or bid is None or post[ia] is None or not(0.05<=a<=0.95): continue
        mk.append((post[ia]+bid)/2-a-fee(a)); last=i
        mise=min(50,(pre[ia+1] or 0)*a)
        if mise>=2:
            side="UP" if ia==0 else "DOWN"; win=R[s]==side; k+=1; w+=win
            J[(dt.datetime.fromtimestamp(s,dt.timezone.utc)+dt.timedelta(hours=1)).strftime("%m-%d")]+=mise*((1/(a+fee(a))-1) if win else -1)
    print(f"{nom} perp BTC ≥{X} pb, achat au prix vu à {off:+d} s: {len(mk)} cas, valeur 5 s après {100*np.mean(mk):+.2f} c | règlement: {k} trades, {100*w/max(1,k):.0f}% gagnés, {sum(J.values()):+.0f} $, jours positifs {sum(v>0 for v in J.values())}/{len(J)}")
for off in (-1,0,1,2,3):
    run("ETH",CE,resE,3,off)
for off in (0,1):
    run("BTC (même période)",{s:v for s,v in CB.items() if s in resE or True},res,3,off)
