import pickle,collections,datetime as dt
C=pickle.load(open("cyc.pkl","rb")); res,ptb,fin=pickle.load(open("off.pkl","rb"))
def fee(a): return 0.07*a*(1-a)
def run(seuil,fen,lat,lo,hi,t0=20,t1=285):
    J=collections.defaultdict(float); n=w=0
    for s,c in C.items():
        if s not in res: continue
        jour=(dt.datetime.fromtimestamp(s,dt.timezone.utc)+dt.timedelta(hours=1)).strftime("%m-%d")
        for sec in range(t0,t1):
            a,b=c.get(sec-fen),c.get(sec)
            if not a or not b or not a[5] or not b[5]: continue
            d=b[5]-a[5]
            if abs(d)<seuil: continue
            side,ia=("UP",0) if d>0 else ("DOWN",2)
            if b[ia] is None or a[ia] is None or b[ia]>a[ia]: continue   # le carnet n'a pas encore monté
            e=c.get(sec+lat)
            if not e or e[ia] is None or not e[ia+1]: continue
            px=e[ia]
            if not(lo<=px<=hi): continue
            mise=min(50,e[ia+1]*px)
            if mise<5: continue
            win=res[s]==side; J[jour]+=mise*((1/(px+fee(px))-1) if win else -1); n+=1; w+=win; break
    a=sum(v for k,v in J.items() if k<"11-01"); t=sum(v for k,v in J.items() if k>="11-01"); neg=sum(1 for v in J.values() if v<0)
    print(f"BTC bouge ≥{seuil}$ en {fen}s, carnet pas encore bougé, achat {lat}s après, prix {lo}-{hi}: trades {n:5d} gagnés {100*w/max(1,n):4.1f}% | appr {a:+7.0f} $ | test {t:+6.0f} $ | jours nég {neg}/{len(J)}",flush=True)
for seuil in (20,40,60):
  for fen in (2,5):
    for lat in (1,2):
      for lo,hi in ((0.05,0.5),(0.5,0.95)):
        run(seuil,fen,lat,lo,hi)
