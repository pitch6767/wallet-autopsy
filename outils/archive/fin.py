import pickle,numpy as np,collections,datetime as dt
M,PM=pickle.load(open("series.pkl","rb")); t0=int(np.load("t0.npy")[0])
C=pickle.load(open("cyc.pkl","rb")); res,ptb,fin=pickle.load(open("off.pkl","rb"))
def fee(a): return 0.07*a*(1-a)
CL=M["chainlink"]; PP=M["okx_perp"]; BY=M["bybit_perp"]
def run(tdec,lat,marge,lo,hi):
    J=collections.defaultdict(float); n=w=0; dejà=0
    for s in res:
        if s not in C or s not in ptb: continue
        i=s+tdec-t0
        if i<10 or i>=len(CL): continue
        cl,p,p2=CL[i],PP[i],PP[i-2]
        if np.isnan(cl) or np.isnan(p) or np.isnan(p2): continue
        # Chainlink final estimé = Chainlink maintenant + ce que le perp a fait sur les 2 dernières s (pas encore dans Chainlink)
        est=cl*(1+ (np.log(p)-np.log(p2)))
        d=(est-ptb[s])/ptb[s]*1e4
        if abs(d)<marge: continue
        side,ia=("UP",0) if d>0 else ("DOWN",2)
        # ce que dit Chainlink seul (sans le perp) : on ne garde que les cas où le perp CHANGE l'avis ou le renforce
        e=C[s].get(tdec+lat)
        if not e or not e[ia] or not e[ia+1]: continue
        a=e[ia]
        if not(lo<=a<=hi): continue
        mise=min(50,e[ia+1]*a)
        if mise<2: continue
        win=res[s]==side; J[(dt.datetime.fromtimestamp(s,dt.timezone.utc)+dt.timedelta(hours=1)).strftime("%m-%d")]+=mise*((1/(a+fee(a))-1) if win else -1); n+=1; w+=win
    ap=sum(v for k,v in J.items() if k<"11-01"); te=sum(v for k,v in J.items() if k>="11-01")
    print(f"décision à {tdec}s, achat {lat}s après, marge ≥{marge}pb, prix {lo}-{hi}: {n} trades gagnés {100*w/max(1,n):.1f}% | appr {ap:+.0f} $ | test {te:+.0f} $ | jours positifs {sum(v>0 for v in J.values())}/{len(J)}")
for tdec in (295,297,298):
    for lat in (1,):
        for marge in (0.5,1,2):
            for lo,hi in ((0.05,0.6),(0.6,0.95),(0.95,0.99)):
                run(tdec,lat,marge,lo,hi)
