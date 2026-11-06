import gzip,json,glob,pickle,collections
D="/home/claude/wallet-autopsy/bot95/donnees"
K=['proba_up_modele','perp_achats_usd','perp_ventes_usd','perp_plus_gros_achat','perp_plus_grosse_vente','liq_longs_usd','liq_courts_usd',
 'pm_up_retrait_achat','pm_up_retrait_vente','pm_up_ajout_achat','pm_up_ajout_vente','pm_up_echange_achat','pm_up_echange_vente',
 'pm_down_retrait_achat','pm_down_retrait_vente','pm_down_ajout_achat','pm_down_ajout_vente','pm_down_echange_achat','pm_down_echange_vente',
 'bybit_financement','bybit_base_pb','bybit_interet_ouvert','bybit_perp','okx_perp','deribit_perp','coinbase','binance_spot','chainlink','pm_up_achat_taille','pm_up_vente_taille']
S=collections.defaultdict(dict)
for f in sorted(glob.glob(D+"/*/sig_BTC.json.gz")):
    d=json.load(gzip.open(f))
    for v in d.values():
        i={n:j for j,n in enumerate(v["colonnes"])}
        for r in v["lignes"]:
            s=r[i["start"]]
            if s is None: continue
            sec=int(r[i["t"]]-s)
            if 0<=sec<300: S[s][sec]=tuple(r[i[k]] if k in i else None for k in K)
    print(f[-22:],len(S),flush=True)
pickle.dump((K,dict(S)),open("sig.pkl","wb"))
