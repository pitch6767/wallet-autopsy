import json, subprocess, urllib.request, concurrent.futures as cf, time, itertools
U="https://wallet-autopsy.pitch67.workers.dev"
rows=json.load(urllib.request.urlopen(U+"/api/btc/copiables",timeout=60))[:90]
def get(a):
    for k in range(3):
        try:
            with urllib.request.urlopen(f"{U}/api/etude?addr={a}",timeout=120) as r: return json.load(r)
        except Exception as e: time.sleep(5)
    return None
with cf.ThreadPoolExecutor(4) as ex: res=list(ex.map(lambda r:(r,get(r["wallet"])),rows))
now=time.time(); ok=[]
for r,e in res:
    if not e or not e.get("meilleure"): continue
    s=e["stats"]; m=e["meilleure"]
    actif = now - s["fin"] < 3*86400
    d=dict(w=r["wallet"],titre=e["titre"],lib=m["lib"],marge=m["marge"],n=m["n"],roi=m["roi"],p=m["p"],avant=m["avant"],r1=s["r1"],r2=s["r2"],rrec=s.get("roiCibleRecent"),
      part=s["partMax"],mise=s.get("miseCibleMed"),parJour=s["parJour"],fin=s["fin"],actif=actif,pnl=e["pnl"],marches=e["marches"],cible={(c[0],c[1]) for c in e.get("cible",[])},cids={c[0] for c in e.get("cible",[])},verdict=e["verdict"])
    ok.append(d)
print("etudies",len(ok))
# overlap
for a,b in itertools.combinations(ok,2):
    inter=len(a["cids"]&b["cids"])
    if inter>=20:
        same=len(a["cible"]&b["cible"])
        if inter/min(len(a["cids"]),len(b["cids"]))>0.5: print("RECOUVRE",a["w"][:10],b["w"][:10],"communs",inter,"meme cote",same)
for d in sorted(ok,key=lambda d:-d["marge"]*d["n"]**.5):
    print(json.dumps({k:(round(v,3) if isinstance(v,float) else v) for k,v in d.items() if k not in("cible","cids","verdict")}))
