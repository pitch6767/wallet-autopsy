import json,gzip,collections,numpy as np,pandas as pd
rows=[]
for day in ['09','10','11','12']:
    m=json.load(gzip.open(f'amel/poly/polytrades_2026-10-{day}.json.gz'))['marches']
    for st,v in m.items():
        st=int(st)
        if st>=1791849600: continue
        res=v.get('resultat')
        if not res: continue
        for ts,w,sd,o,px,q,tx in v['trades']:
            el=ts-st
            if not (0<=el<=300): continue
            r=res[o]; sg=1 if sd=='BUY' else -1
            rows.append((st,el,w,sg,o,px,q,sg*(r-px)*q, px*q, tx))
d=pd.DataFrame(rows,columns='st el w sg o px q pnl usd tx'.split()); d.to_pickle('wal.pkl')
print(len(d), d.w.nunique(), d.st.nunique())
