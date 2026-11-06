import pickle,numpy as np
K,S=pickle.load(open("sig.pkl","rb")); ix={k:i for i,k in enumerate(K)}
C=pickle.load(open("cyc.pkl","rb"))
src=["bybit_perp","okx_perp","deribit_perp","binance_spot","coinbase","chainlink"]
T=[]; 
for s in sorted(S):
    for sec,r in S[s].items(): T.append((s+sec,r))
T.sort(); t0=T[0][0]; n=T[-1][0]-t0+1
M={k:np.full(n,np.nan) for k in src}; PM=np.full(n,np.nan)
for t,r in T:
    for k in src:
        v=r[ix[k]]
        if v: M[k][t-t0]=v
for s,c in C.items():
    for sec,v in c.items():
        if v[0] and v[2]: PM[s+sec-t0]=(v[0]+1-v[2])/2   # proba UP du cycle (attention : change à chaque cycle)
np.save("t0.npy",np.array([t0])); pickle.dump((M,PM),open("series.pkl","wb"))
R={k:np.diff(np.log(M[k])) for k in src}
print("Qui mène ? corrélation entre le rendement de X sur [t-k-1,t-k] et celui de Chainlink sur [t,t+1] (1 s)")
for k in src:
    row=[]
    for lag in range(0,6):
        a=R[k][:len(R[k])-lag-1] if lag>=0 else None; b=R["chainlink"][lag+1:]
        m=~np.isnan(a)&~np.isnan(b)&(a!=0)
        row.append(np.corrcoef(a[m],b[m])[0,1] if m.sum()>1000 else np.nan)
    print(f"{k:14s}"+" ".join(f"lag{l}:{x:+.3f}" for l,x in enumerate(row)))
# cumul : part du mouvement de Chainlink sur 10 s déjà visible sur X avant
print("\nRégression : mouvement Chainlink des 10 prochaines s expliqué par le mouvement de X des 10 dernières s moins celui de Chainlink")
CL=M["chainlink"]
for k in src[:-1]:
    X=M[k]; idx=np.arange(20,n-11,5)
    gap=np.log(X[idx])-np.log(CL[idx])- (np.log(X[idx-10])-np.log(CL[idx-10]))
    fut=np.log(CL[idx+10])-np.log(CL[idx])
    m=~np.isnan(gap)&~np.isnan(fut)
    b=np.polyfit(gap[m],fut[m],1)[0]; c=np.corrcoef(gap[m],fut[m])[0,1]
    print(f"{k:14s} pente {b:.2f}  corrélation {c:+.3f}  (n={m.sum()})")
