import json, urllib.request
U="https://bot95.pitch67.workers.dev"
g=lambda p: json.loads(urllib.request.urlopen(urllib.request.Request(U+p,headers={"User-Agent":"x"}),timeout=30).read())
e=g("/api/etat")["e"]; v=g("/api/verif")["verif"]
print("TRADES"); [print(json.dumps(t,ensure_ascii=False)) for t in e["trades"]]
perte=[t for t in e["trades"] if t["net"]<0]
print("\nVERIF des marches perdus")
for t in perte:
    for x in v:
        if x["slug"]==t["slug"]: print(json.dumps(x))
print("\nECARTS K par actif (bot - officiel), relatif")
import statistics
for a in ["BTC","ETH","SOL","XRP","DOGE","BNB","HYPE"]:
    L=[x for x in v if x["actif"]==a and x.get("fait") and x.get("ecartK") is not None]
    if L: print(a, len(L), "ecartK rel max %.2e med %.2e"%(max(abs(x["ecartK"]/x["kOff"]) for x in L), statistics.median(abs(x["ecartK"]/x["kOff"]) for x in L)),
                 "ecartFin rel max %.2e"%max(abs((x.get("ecartFin") or 0)/x["kOff"]) for x in L),
                 "faux gagnant", sum(1 for x in L if x.get("fin") and ((x["fin"]>=x["kOff"])!=(x["gagnant"]=="Up"))),
                 "k bot faux sens", sum(1 for x in L if x.get("fin") and x.get("k") and ((x["fin"]>=x["k"])!=(x["gagnant"]=="Up"))))
