import pickle,numpy as np,collections,datetime as dt
M,PM=pickle.load(open("series.pkl","rb")); t0=int(np.load("t0.npy")[0]); C=pickle.load(open("cyc.pkl","rb")); res,ptb,fin=pickle.load(open("off.pkl","rb"))
def fee(a): return 0.07*a*(1-a)
P=M["okx_perp"]; CL=M["chainlink"]
def run(seuil,smax,lat):
    J=collections.defaultdict(float); n=w=0; pay=0
    for s in res:
        if s not in C or s not in ptb: continue
        for sec in range(1,smax+1):
            i=s+sec-t0
            if i<0 or i>=len(P) or np.isnan(P[i]) or np.isnan(CL[i]): continue
            dd=(P[i]-ptb[s])/ptb[s]*1e4-(P[i]-CL[i])/CL[i]*1e4
            if abs(dd)<seuil: continue
            side,ia=("UP",0) if dd>0 else ("DOWN",2)
            e=C[s].get(sec+lat)
            if not e or not e[ia] or not e[ia+1]: break
            a=e[ia]
            if not(0.05<=a<=0.95): break
            mise=min(50,e[ia+1]*a)
            if mise<2: break
            win=res[s]==side; J[(dt.datetime.fromtimestamp(s,dt.timezone.utc)+dt.timedelta(hours=1)).strftime("%m-%d")]+=mise*((1/(a+fee(a))-1) if win else -1); n+=1; w+=win; pay+=a; break
    ap=sum(v for k,v in J.items() if k<"10-31"); te=sum(v for k,v in J.items() if k>="10-31")
    print(f"écart ≥{seuil} pb dans les {smax} premières s, achat {lat}s après: {n} trades, {100*w/max(1,n):.0f}% gagnés (prix moyen {100*pay/max(1,n):.0f} c) | 07-30.10 {ap:+.0f} $ | 31.10-06.11 {te:+.0f} $ | jours positifs {sum(v>0 for v in J.values())}/{len(J)}")
for seuil in (6,8,12):
    for smax in (5,15):
        for lat in (0,1,2):
            run(seuil,smax,lat)
