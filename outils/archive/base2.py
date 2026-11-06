import pickle,math,datetime as dt,statistics as st
C=pickle.load(open("cyc.pkl","rb")); res,ptb,fin=pickle.load(open("off.pkl","rb"))
err=[]
for s in res:
    if s in C and s in fin:
        ks=[k for k in sorted(C[s]) if C[s][k][4] and k>=250]
        if ks: err.append(abs(C[s][ks[-1]][4]-fin[s]))
print("écart chainlink enregistré vs final officiel (médiane $)",st.median(err))
vol={}
for s in res:
    r=[math.log(ptb[s-300*(k-1)]/ptb[s-300*k]) for k in range(1,13) if ptb.get(s-300*k) and ptb.get(s-300*(k-1))]
    if len(r)>=8: vol[s]=st.pstdev(r)
rows=[]
for s in sorted(res):
    if s not in C or s not in vol or s not in ptb: continue
    K=ptb[s]; t=dt.datetime.fromtimestamp(s,dt.timezone.utc)+dt.timedelta(hours=1)
    mv=math.log(K/ptb[s-3600]) if ptb.get(s-3600) else 0
    for sec in range(5,295,5):
        v=C[s].get(sec) or C[s].get(sec+1) or C[s].get(sec-1)
        if not v: continue
        P=v[4] or v[5]
        if not P: continue
        sig=vol[s]*math.sqrt((300-sec)/300); z=math.log(P/K)/sig if sig>0 else 0
        rows.append(dict(s=s,sec=sec,h=t.hour,jour=t.strftime("%m-%d"),vol=vol[s],mv=mv,z=z,fair=0.5*(1+math.erf(z/math.sqrt(2))),ua=v[0],us=v[1],da=v[2],ds=v[3],res=res[s]))
pickle.dump(rows,open("rows.pkl","wb")); print(len(rows))
