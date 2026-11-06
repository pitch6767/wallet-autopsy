import pickle,collections
C=pickle.load(open("cyc.pkl","rb")); res,ptb,fin=pickle.load(open("off.pkl","rb"))
import datetime as dt
def fee(a): return 0.07*a*(1-a)
def run(seuil,lo,hi,t0,t1,delta,garder=False):
    J=collections.defaultdict(float); n=0; dm=[]
    for s,c in C.items():
        if s not in res: continue
        j=(dt.datetime.fromtimestamp(s,dt.timezone.utc)+dt.timedelta(hours=1)).strftime("%m-%d")
        for sec in range(t0,t1,5):
            v=c.get(sec)
            if not v or not v[0] or not v[2] or not v[1] or not v[3]: continue
            d=(v[1]-v[3])/(v[1]+v[3])
            if abs(d)<seuil: continue
            side,ia,ib=("DOWN",2,8) if d>0 else ("UP",0,7)
            a=v[ia]
            if not(lo<=a<=hi): continue
            mise=min(50,v[ia+1]*a)
            if mise<2: break
            parts=mise/(a+fee(a))
            e=None
            for k in range(sec+delta,min(299,sec+delta+3)):
                if c.get(k) and c[k][ib]: e=c[k]; break
            if not e: break
            b=e[ib]; g=parts*(b-fee(b))-mise
            dm.append(b-a); J[j]+=g; n+=1; break
    ap=sum(v for k,v in J.items() if k<"11-01"); te=sum(v for k,v in J.items() if k>="11-01")
    print(f"offre mince ≥{seuil}, prix {lo}-{hi}, sec {t0}-{t1}, revente au meilleur acheteur {delta}s après: trades {n} | écart moyen revente-achat {100*sum(dm)/max(1,len(dm)):+.2f} c | appr {ap:+.0f} $ | test {te:+.0f} $")
for delta in (5,15,30,60):
    run(0.85,0.65,0.95,120,210,delta)
    run(0.85,0.05,0.95,30,250,delta)
