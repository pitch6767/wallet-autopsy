import pickle,json,collections,statistics as st
R=pickle.load(open("rows.pkl","rb"))
O=json.load(open("/home/claude/wallet-autopsy/bot95/officiels.json"))
res={r["s"]:r["res"] for r in R}; ok=n=0
for k,v in O.items():
    s=int(k.split(":")[1])
    if s in res: n+=1; ok+= (res[s]==v["gagnant"].upper())
print("accord résultat officiel",ok,"/",n)
med=st.median({r["s"]:r["vol"] for r in R}.values())
def pnl(a,win): f=0.07*a*(1-a); return (1/(a+f)-1) if win else -1
def run(edge,lo,hi,filt,secs):
    out=collections.defaultdict(lambda:[0.0,0,0]); vu=set()
    for r in R:
        if r["s"] in vu or not(secs[0]<=r["sec"]<secs[1]) or not filt(r): continue
        for side,a,sz,f in (("UP",r["ua"],r["us"],r["fair"]),("DOWN",r["da"],r["ds"],1-r["fair"])):
            if a and sz and lo<=a<=hi and f-a>=edge:
                mise=min(50,sz*a); 
                if mise<5: continue
                g=mise*pnl(a,r["res"]==side); p="test" if r["jour"]>="11-01" else "appr"
                o=out[p]; o[0]+=g;o[1]+=1;o[2]+=(r["res"]==side); vu.add(r["s"]); break
    return {k:(round(v[0]),v[1],round(100*v[2]/max(1,v[1]))) for k,v in out.items()}
nuit=lambda r: r["h"]>=22 or r["h"]<7
calme=lambda r: r["vol"]<med
tous=lambda r:True
for nom,fl in (("tous",tous),("nuit",nuit),("calme",calme),("jour agité",lambda r: not nuit(r) and not calme(r))):
  for secs in ((10,60),(60,180),(180,290)):
    for edge in (0.05,0.10,0.15):
      for lo,hi in ((0.05,0.35),(0.35,0.65),(0.65,0.95)):
        print(nom,secs,edge,(lo,hi),run(edge,lo,hi,fl,secs))
