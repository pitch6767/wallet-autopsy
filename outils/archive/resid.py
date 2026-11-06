import pickle,statistics as st
F=pickle.load(open("F.pkl","rb"))
A=[f for f in F if f["jour"]<"11-01"]; T=[f for f in F if f["jour"]>="11-01"]
feats=["modele_moins_marche","mom_pm30","btc30","btc10","ecart_btc_pm","desequilibre","spread","prec","prec2","tend1h","vol","binance_moins_chainlink","z"]
print("Résidu = (UP gagne ? 1 : 0) − prix milieu, en centimes. Par quintile de la variable (bornes fixées sur l'apprentissage).")
for k in feats:
    xs=sorted(f[k] for f in A); q=[xs[int(len(xs)*i/5)] for i in range(1,5)]
    def b(x): return sum(x>t for t in q)
    out=[]
    for D in (A,T):
        m=[[] for _ in range(5)]
        for f in D: m[b(f[k])].append((f["res"]=="UP")-f["mid"])
        out.append([100*st.mean(x) if x else 0 for x in m])
    print(f"{k:24s} appr " + " ".join(f"{x:+5.1f}" for x in out[0]) + " | test " + " ".join(f"{x:+5.1f}" for x in out[1]))
