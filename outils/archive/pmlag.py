import pickle,numpy as np
M,PM=pickle.load(open("series.pkl","rb")); t0=int(np.load("t0.npy")[0])
P=np.log(M["okx_perp"]); n=len(P); t=np.arange(n)+t0; sec=(t%300)
dPM=np.diff(PM); dP=np.diff(P)
ok_cycle=(sec[1:]!=0)  # pas de changement de cycle
print("Le prix Polymarket suit-il le perp ? corr(rendement perp il y a k s, variation PM maintenant)")
for lag in range(0,6):
    a=dP[:len(dP)-lag]; b=dPM[lag:]; m=~np.isnan(a)&~np.isnan(b)&ok_cycle[lag:]&(sec[1+lag:]>5)
    print(f"  lag {lag}s: {np.corrcoef(a[m],b[m])[0,1]:+.3f}")
print("\nAprès un départ brutal du perp (≥ X pb en 3 s), que fait le BTC ensuite ? (même sens = continuation)")
for X in (5,8,12):
    i=np.arange(3,n-120); mv=(P[i]-P[i-3])*1e4; m=np.abs(mv)>=X; m&=~np.isnan(mv)
    sel=i[m]; ev=[]; last=-99
    for s in sel:
        if s-last>30: ev.append(s)
        last=s
    ev=np.array(ev); sg=np.sign((P[ev]-P[ev-3]))
    for h in (2,5,10,30,60,120):
        f=(P[ev+h]-P[ev])*1e4*sg; f=f[~np.isnan(f)]
        print(f"  X={X:2d}pb ({len(ev)} cas) après {h:3d}s : moyenne {np.mean(f):+.2f} pb, même sens {100*np.mean(f>0):.0f} %")
