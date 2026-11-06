import pickle,math,collections,statistics as st,datetime as dt
C=pickle.load(open("cyc.pkl","rb")); res,ptb,fin=pickle.load(open("off.pkl","rb"))
def at(s,k):
    c=C.get(s,{})
    for d in (0,1,-1,2,-2):
        v=c.get(k+d)
        if v and v[0] and v[2] and (v[4] or v[5]): return v
vol={}
for s in res:
    r=[math.log(ptb[s-300*(k-1)]/ptb[s-300*k]) for k in range(1,13) if ptb.get(s-300*k) and ptb.get(s-300*(k-1))]
    if len(r)>=8: vol[s]=st.pstdev(r)
F=[]
for s in sorted(res):
    if s not in C or s not in vol or s not in ptb: continue
    t=dt.datetime.fromtimestamp(s,dt.timezone.utc)+dt.timedelta(hours=1)
    prev=res.get(s-300); prev2=res.get(s-600)
    for sec in range(30,280,15):
        v=at(s,sec); v30=at(s,sec-30); v10=at(s,sec-10)
        if not v or not v30 or not v10: continue
        P=v[5] or v[4]; P30=v30[5] or v30[4]; P10=v10[5] or v10[4]; K=ptb[s]
        mid=(v[0]+1-v[2])/2; mid30=(v30[0]+1-v30[2])/2
        sig=vol[s]*math.sqrt((300-sec)/300); z=math.log((v[4] or v[5])/K)/sig if sig else 0
        fair=0.5*(1+math.erf(z/math.sqrt(2)))
        F.append(dict(s=s,sec=sec,jour=t.strftime("%m-%d"),h=t.hour,res=res[s],mid=mid,ua=v[0],da=v[2],us=v[1],ds=v[3],
            z=z, modele_moins_marche=fair-mid, mom_pm30=mid-mid30, btc30=(P-P30)/P*1e4, btc10=(P-P10)/P*1e4,
            ecart_btc_pm=(P-P30)/P*1e4/ (vol[s]*1e4+1e-9) - (mid-mid30)*10,
            desequilibre=( (v[1]or 0)-(v[3]or 0))/((v[1]or 0)+(v[3]or 0)+1), spread=v[0]+v[2]-1,
            prec=(1 if prev=="UP" else -1 if prev=="DOWN" else 0), prec2=(1 if prev==prev2=="UP" else -1 if prev==prev2=="DOWN" else 0),
            tend1h=math.log(K/ptb[s-3600])*1e4 if ptb.get(s-3600) else 0, vol=vol[s]*1e4, binance_moins_chainlink=((v[5] or 0)-(v[4] or 0)) if v[5] and v[4] else 0))
pickle.dump(F,open("F.pkl","wb")); print(len(F))
