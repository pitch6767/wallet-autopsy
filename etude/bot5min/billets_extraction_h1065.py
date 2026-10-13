import json, glob, os, numpy as np, pandas as pd
rows = []
for f in glob.glob("/home/claude/wallet-autopsy/bot95/sauvegarde/*.json"):
    try: d = json.load(open(f))
    except Exception: continue
    nom = d.get("nom") or os.path.basename(f); T = d.get("trades") or {}
    for k, x in (T.items() if isinstance(T, dict) else enumerate(T)):
        if not isinstance(x, dict) or x.get("prix") is None or x.get("gagnant") is None: continue
        st = x.get("start"); ta = x.get("tAchat")
        rows.append(dict(nom=nom, fichier=os.path.basename(f), st=st, ta=ta, cote=x.get("cote"), prix=x["prix"], parts=x.get("parts"), net=x.get("net"),
                         win=int(x.get("gagnant") == x.get("cote")), rest=x.get("restant_s"), proba=x.get("proba0"), heure=x.get("heure")))
D = pd.DataFrame(rows); D.to_pickle("trades_bot.pkl")
print(len(D), D.nom.nunique()); print(D.prix.describe())
P = D[D.prix <= 0.20].copy(); P["b"] = pd.cut(P.prix, [0, .02, .05, .10, .15, .20])
print(P.groupby("b", observed=True).agg(n=("win", "size"), gagnants=("win", "sum"), taux=("win", "mean"), prix=("prix", "mean"), net=("net", "sum")).round(3))
print(P.groupby("nom").agg(n=("win", "size"), taux=("win", "mean"), prix=("prix", "mean"), net=("net", "sum")).sort_values("n", ascending=False).head(25).round(3).to_string())
