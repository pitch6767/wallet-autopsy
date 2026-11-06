import pickle,math
F=pickle.load(open("F.pkl","rb")); K,S=pickle.load(open("sig.pkl","rb")); ix={k:i for i,k in enumerate(K)}
def somme(s,sec,w,k):
    c=S.get(s,{}); t=0.0; n=0
    for x in range(sec-w+1,sec+1):
        r=c.get(x)
        if r and r[ix[k]] is not None: t+=r[ix[k]]; n+=1
    return t,n
def val(s,sec,k):
    c=S.get(s,{})
    for d in (0,-1,1,-2,2):
        r=c.get(sec+d)
        if r and r[ix[k]] is not None: return r[ix[k]]
G=[]
for f in F:
    s,sec=f["s"],f["sec"]
    if s not in S: continue
    g=dict(f)
    for w in (10,30):
        ub,_=somme(s,sec,w,"pm_up_echange_achat"); us,_=somme(s,sec,w,"pm_up_echange_vente")
        db,_=somme(s,sec,w,"pm_down_echange_achat"); ds,_=somme(s,sec,w,"pm_down_echange_vente")
        g[f"pm_flux_up_{w}"]=(ub-us)-(db-ds); g[f"pm_volume_{w}"]=ub+us+db+ds
        ua,_=somme(s,sec,w,"pm_up_ajout_vente"); ur,_=somme(s,sec,w,"pm_up_retrait_vente")
        da,_=somme(s,sec,w,"pm_down_ajout_vente"); dr,_=somme(s,sec,w,"pm_down_retrait_vente")
        g[f"pm_offre_nette_up_{w}"]=(ua-ur)-(da-dr)
        ba,_=somme(s,sec,w,"pm_up_ajout_achat"); br,_=somme(s,sec,w,"pm_up_retrait_achat")
        g[f"pm_demande_nette_up_{w}"]=(ba-br)
        pa,_=somme(s,sec,w,"perp_achats_usd"); pv,_=somme(s,sec,w,"perp_ventes_usd")
        g[f"perp_flux_{w}"]=(pa-pv)/1e5; g[f"perp_vol_{w}"]=(pa+pv)/1e5
        ll,_=somme(s,sec,w,"liq_longs_usd"); lc,_=somme(s,sec,w,"liq_courts_usd"); g[f"liq_net_{w}"]=(lc-ll)/1e4
    pm=val(s,sec,"proba_up_modele"); g["dublin_moins_marche"]=(pm-f["mid"]) if pm is not None else 0
    g["financement"]=(val(s,sec,"bybit_financement") or 0)*1e4; g["base"]=val(s,sec,"bybit_base_pb") or 0
    bp,cl=val(s,sec,"bybit_perp"),val(s,sec,"chainlink"); g["perp_moins_chainlink"]=((bp-cl)/cl*1e4) if bp and cl else 0
    cb=val(s,sec,"coinbase"); g["coinbase_moins_chainlink"]=((cb-cl)/cl*1e4) if cb and cl else 0
    G.append(g)
pickle.dump(G,open("G.pkl","wb")); print(len(G))
