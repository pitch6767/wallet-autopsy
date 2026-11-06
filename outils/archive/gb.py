import pickle,numpy as np,collections
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import log_loss
F=pickle.load(open("G.pkl","rb"))
X_keys=[k for k in F[0] if k not in ("s","jour","res","ua","da","us","ds")]
def M(D): return np.array([[f[k] for k in X_keys] for f in D],float), np.array([f["res"]=="UP" for f in D],int)
tr=[f for f in F if f["jour"]<"10-24"]; va=[f for f in F if "10-24"<=f["jour"]<"11-01"]; te=[f for f in F if f["jour"]>="11-01"]
Xt,yt=M(tr); m=HistGradientBoostingClassifier(max_iter=300,learning_rate=0.03,max_leaf_nodes=15,min_samples_leaf=400,l2_regularization=1.0)
m.fit(Xt,yt)
def fee(a): return 0.07*a*(1-a)
def evalue(D,nom,marges=(0.0,0.01,0.02,0.03)):
    X,y=M(D); p=m.predict_proba(X)[:,1]; mid=np.clip([f["mid"] for f in D],0.01,0.99)
    print(f"{nom}: perte log modèle {log_loss(y,p):.4f} vs marché {log_loss(y,mid):.4f}")
    for mg in marges:
        for lo,hi in ((0.05,0.95),(0.6,0.95)):
            J=collections.defaultdict(float); vu=set(); n=w=0
            for f,pu in zip(D,p):
                if f["s"] in vu: continue
                for side,a,sz,pp in (("UP",f["ua"],f["us"],pu),("DOWN",f["da"],f["ds"],1-pu)):
                    if a and sz and lo<=a<=hi and pp-(a+fee(a))>mg:
                        mise=min(50,sz*a)
                        if mise<2: continue
                        J[f["jour"]]+=mise*((1/(a+fee(a))-1) if f["res"]==side else -1); n+=1; w+=f["res"]==side; vu.add(f["s"]); break
            neg=sum(1 for v in J.values() if v<0)
            print(f"   marge {mg:.2f} prix {lo}-{hi}: trades {n:5d} gagnés {100*w/max(1,n):4.1f}% total {sum(J.values()):+7.0f} $ jours nég {neg}/{len(J)}")
evalue(va,"VALIDATION 24-31.10")
evalue(te,"TEST inédit 01-06.11")
imp=sorted(zip(X_keys,np.zeros(len(X_keys))),key=lambda x:x[0])
from sklearn.inspection import permutation_importance
Xv,yv=M(va); r=permutation_importance(m,Xv[:20000],yv[:20000],n_repeats=3,random_state=0,scoring="neg_log_loss")
print("variables les plus utiles :",[ (X_keys[i],round(r.importances_mean[i]*1e4,1)) for i in np.argsort(-r.importances_mean)[:10]])
