import pickle,numpy as np,datetime as dt,collections
M,PM=pickle.load(open("series.pkl","rb")); t0=int(np.load("t0.npy")[0]); K,S=pickle.load(open("sig.pkl","rb")); ix={k:i for i,k in enumerate(K)}
P=M["okx_perp"]; n=len(P)
# volatilité (|rendement 60 s|) par heure de Paris et minute de l'heure
idx=np.arange(60,n,60); r=np.abs(np.log(P[idx])-np.log(P[idx-60]))*1e4
tt=t0+idx; h=((tt//3600)+1)%24; mi=(tt//60)%60; wd=((tt//86400)+4)%7  # 0=lundi? 1970-01-01 jeudi
m=~np.isnan(r)
H=collections.defaultdict(list); MI=collections.defaultdict(list); W=collections.defaultdict(list)
for a,b,c,d in zip(r[m],h[m],mi[m],wd[m]): H[b].append(a); MI[c].append(a); W[(d+3)%7].append(a)
print("Mouvement moyen sur 1 min (points de base) par heure de Paris:")
print(" ".join(f"{k}h:{np.mean(v):.1f}" for k,v in sorted(H.items())))
print("par minute de l'heure (les plus agitées):",sorted(((round(np.mean(v),1),k) for k,v in MI.items()),reverse=True)[:8],"moyenne",round(np.mean(r[m]),1))
print("par jour (0=lundi):"," ".join(f"{k}:{np.mean(v):.1f}" for k,v in sorted(W.items())))
# top moves : 30 s > 99e centile
i30=np.arange(30,n-30,5); mv=(np.log(P[i30])-np.log(P[i30-30]))*1e4; ok=~np.isnan(mv)
th=np.percentile(np.abs(mv[ok]),99); print(f"\nGros mouvements : > {th:.0f} pb en 30 s ({np.sum(np.abs(mv[ok])>th)} cas)")
big=i30[ok][np.abs(mv[ok])>th]
# dédoublonner (un événement = 60 s)
ev=[]; last=-999
for b in big:
    if b-last>60: ev.append(b)
    last=b
print("événements distincts:",len(ev))
# heures de Paris des événements (minute précise)
cnt=collections.Counter(); cntm=collections.Counter()
for e in ev:
    t=t0+e-30; d=dt.datetime.fromtimestamp(t,dt.timezone.utc)+dt.timedelta(hours=1); cnt[d.hour]+=1; cntm[(d.hour,d.minute)]+=1
print("par heure:",dict(sorted(cnt.items())))
print("minutes précises les plus fréquentes:",cntm.most_common(10))
# précurseurs : dans les 30 s AVANT le début du mouvement vs normal
def tot(t,w,k):
    s=sum(( (S.get(x - x%300,{}).get(x%300) or [None]*len(K))[ix[k]] or 0) for x in range(t-w,t)); return s
pre=collections.defaultdict(list); base=collections.defaultdict(list)
rng=np.random.default_rng(0); norm=rng.choice(i30[ok],2000,replace=False)
for grp,L in (("avant gros mouvement",ev),("moment normal",norm)):
    for e in L:
        t=t0+int(e)-30
        for k in ("perp_achats_usd","perp_ventes_usd","liq_longs_usd","liq_courts_usd","pm_up_echange_achat","pm_down_echange_achat"):
            (pre if grp.startswith("avant") else base)[k].append(tot(t,30,k))
print("\nDans les 30 s avant le début : moyenne (avant gros mouvement / moment normal)")
for k in pre: print(f"  {k:22s} {np.mean(pre[k]):12.0f} / {np.mean(base[k]):12.0f}  x{np.mean(pre[k])/max(1,np.mean(base[k])):.1f}")
pickle.dump(ev,open("ev.pkl","wb"))
