import gzip,json,glob,os,pickle,collections
D="/home/claude/wallet-autopsy/bot95/donnees"
cyc=collections.defaultdict(dict)  # start -> sec -> tuple
for f in sorted(glob.glob(D+"/*/rec_ETH.json.gz")):
    d=json.load(gzip.open(f))
    for k,v in d.items():
        c=v["colonnes"]; i={n:j for j,n in enumerate(c)}
        for r in v["lignes"]:
            s=r[i["start"]]; 
            if s is None: continue
            sec=int(r[i["t"]]-s)
            if sec<0 or sec>=300: continue
            g=lambda n: r[i[n]] if n in i else None
            px=g("chainlink") or g("binance_spot") or g("coinbase")
            cyc[s][sec]=(g("up_vente"),g("up_vente_taille"),g("down_vente"),g("down_vente_taille"),g("chainlink"),g("binance_spot") or g("coinbase"),g("prix_a_battre"),g("up_achat"),g("down_achat"))
    print(f,len(cyc),flush=True)
pickle.dump(dict(cyc),open("cycE.pkl","wb"))
