import pickle,numpy as np,collections,datetime as dt
M,PM=pickle.load(open("series.pkl","rb")); t0=int(np.load("t0.npy")[0])
C=pickle.load(open("cyc.pkl","rb")); res,ptb,fin=pickle.load(open("off.pkl","rb"))
def fee(a): return 0.07*a*(1-a)
P=np.log(M["okx_perp"]); n=len(P)
def run(X,lo,hi):
    vu=0; mk=[]; J=collections.defaultdict(float); w=k=0
    last=-99
    for i in range(2,n-5):
        if np.isnan(P[i]) or np.isnan(P[i-1]): continue
        d=(P[i]-P[i-1])*1e4
        if abs(d)<X or i-last<5: continue
        t=i+t0; s=t-t%300; sec=t%300
        if s not in res or sec<5 or sec>285: continue
        c=C.get(s,{}); pre=c.get(sec-1); post=c.get(sec+3)
        if not pre or not post: continue
        side,ia=("UP",0) if d>0 else ("DOWN",2)
        a=pre[ia]
        bidp=post[7] if ia==0 else post[8]
        if a is None or not(lo<=a<=hi) or post[ia] is None or bidp is None: continue
        midp=(post[ia]+bidp)/2
        mk.append(midp-a-fee(a)); last=i
        mise=min(50,(pre[ia+1] or 0)*a)
        if mise<2: continue
        win=res[s]==side; J[(dt.datetime.fromtimestamp(s,dt.timezone.utc)+dt.timedelta(hours=1)).strftime("%m-%d")]+=mise*((1/(a+fee(a))-1) if win else -1); k+=1; w+=win
    ap=sum(v for kk,v in J.items() if kk<"11-01"); te=sum(v for kk,v in J.items() if kk>="11-01")
    print(f"perp ≥{X} pb en 1 s, prix d'avant {lo}-{hi}: {len(mk)} cas, valeur 3 s après {100*np.mean(mk):+.2f} c/part | gardé jusqu'au règlement: {k} trades gagnés {100*w/max(1,k):.0f}% appr {ap:+.0f} $ test {te:+.0f} $ jours positifs {sum(v>0 for v in J.values())}/{len(J)}")
for X in (3,5,8):
    for lo,hi in ((0.05,0.95),(0.2,0.8)):
        run(X,lo,hi)
