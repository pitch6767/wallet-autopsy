import pickle,numpy as np,collections,datetime as dt
M,PM=pickle.load(open("series.pkl","rb")); t0=int(np.load("t0.npy")[0]); C=pickle.load(open("cyc.pkl","rb")); res,ptb,fin=pickle.load(open("off.pkl","rb"))
def fee(a): return 0.07*a*(1-a)
P=M["okx_perp"]; CL=M["chainlink"]
A=collections.defaultdict(lambda:[0,0.0,0.0,0])
for s in res:
    if s not in C or s not in ptb: continue
    for sec in range(1,16):
        i=s+sec-t0
        if i<0 or i>=len(P) or np.isnan(P[i]): continue
        v=C[s].get(sec)
        if not v or not v[0] or not v[2]: continue
        d=(P[i]-ptb[s])/ptb[s]*1e4 - 0  # écart perp vs prix à battre (pb) ; le perp a une base vs Chainlink
        b=CL[i]
        if np.isnan(b): continue
        base=(P[i]-b)/b*1e4
        dd=d-base   # écart corrigé de la base perp/chainlink instantanée → où devrait être Chainlink
        if abs(dd)<2: continue
        side,ia=("UP",0) if dd>0 else ("DOWN",2); a=v[ia]
        k=("2-4 pb" if abs(dd)<4 else "4-8 pb" if abs(dd)<8 else "8+ pb", "s1-5" if sec<=5 else "s6-15", s>=1793404800)  # coupe 01.11
        z=A[k]; z[0]+=1; z[1]+=(res[s]==side); z[2]+=a; z[3]+=(res[s]==side)/(a+fee(a))-1 if True else 0
        break
for k in sorted(A):
    z=A[k]; print(f"écart {k[0]:7s} {k[1]} {'test' if k[2] else 'appr'}: {z[0]} cycles, gagne {100*z[1]/z[0]:.1f} % vs prix payé {100*z[2]/z[0]:.1f} % → rendement {100*z[3]/z[0]:+.1f} %")
