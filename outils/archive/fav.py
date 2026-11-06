import pickle,collections,statistics as st
C=pickle.load(open("cyc.pkl","rb")); R=pickle.load(open("rows.pkl","rb"))
med=st.median({r["s"]:r["vol"] for r in R}.values())
def fee(a): return 0.07*a*(1-a)
def g(v,k):
    for d in (0,1,-1,2,-2): 
        x=C.get(v,{}).get(k+d)
        if x: return x
by={(r["s"],r["sec"]):r for r in R}
cy=sorted({r["s"] for r in R})
def taker(lo,hi,t0,t1,filt=lambda r:True):
    J=collections.defaultdict(float); n=w=0
    for s in cy:
        for sec in range(t0,t1,5):
            r=by.get((s,sec))
            if not r or not filt(r): continue
            hit=None
            for side,a,sz in (("UP",r["ua"],r["us"]),("DOWN",r["da"],r["ds"])):
                if a and sz and lo<=a<=hi: hit=(side,a,sz)
            if hit:
                side,a,sz=hit; mise=min(50,sz*a)
                if mise<5: break
                win=r["res"]==side; J[r["jour"]]+=mise*((1/(a+fee(a))-1) if win else -1); n+=1; w+=win; break
    return J,n,w
def maker(lo,hi,t0,t1,att=30,filt=lambda r:True):
    J=collections.defaultdict(float); n=w=0; posees=0
    for s in cy:
        for sec in range(t0,t1,5):
            r=by.get((s,sec))
            if not r or not filt(r) or not r["ua"] or not r["da"]: continue
            v=g(s,sec)
            hit=None
            for side,bid,ia in (("UP",v[7],0),("DOWN",v[8],2)):
                if bid and lo<=bid<=hi: hit=(side,bid,ia)
            if not hit: continue
            side,bid,ia=hit; posees+=1
            rempli=any((C[s].get(k) and C[s][k][ia] is not None and C[s][k][ia]<=bid-0.01) for k in range(sec+1,min(299,sec+att)))
            if rempli:
                win=r["res"]==side; J[r["jour"]]+=50*((1/bid-1) if win else -1); n+=1; w+=win
            break
    return J,n,w,posees
def show(nom,J,n,w,extra=""):
    a=sum(v for k,v in J.items() if k<"11-01"); t=sum(v for k,v in J.items() if k>="11-01")
    neg=sum(1 for v in J.values() if v<0)
    print(f"{nom:52s} trades {n:5d} gagnés {100*w/max(1,n):4.1f} % | appr {a:+7.0f} $ | test(1-6.11) {t:+6.0f} $ | jours négatifs {neg}/{len(J)} {extra}")
nuitcalme=lambda r:(r["h"]>=22 or r["h"]<7) and r["vol"]<med
for lo,hi in ((0.75,0.85),(0.80,0.90),(0.85,0.95)):
    for t0,t1 in ((30,120),(120,210),(210,280)):
        show(f"preneur favori {lo}-{hi} sec {t0}-{t1}",*taker(lo,hi,t0,t1))
for lo,hi in ((0.75,0.85),(0.80,0.90),(0.85,0.95)):
    for t0,t1 in ((30,120),(120,210),(210,280)):
        J,n,w,p=maker(lo,hi,t0,t1); show(f"teneur favori {lo}-{hi} sec {t0}-{t1}",J,n,w,f"(ordres posés {p})")
