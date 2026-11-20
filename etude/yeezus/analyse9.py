import json, sys, collections, statistics as st, datetime as dt
D=json.load(open(sys.argv[1])); TC=json.load(open('etude/yeezus/traders_complet.json'))
fund={}; prof={}
for m,v in TC.items():
    for t in v["traders"]:
        nt=t.get("native_transfer") or {}
        if nt.get("from_address"): fund[t["address"]]=(nt["from_address"], nt.get("name") or "", round(float(nt.get("amount") or 0),2))
        prof[(m,t["address"])]=(float(t.get("buy_volume_cur") or 0), float(t.get("profit") or 0))
N=len(D); cov=collections.defaultdict(set); first_buy=collections.defaultdict(dict)
BUN=[]; ENTRY=[]
for m,v in D.items():
    tc=v["tc"]; tr=[x for x in v["trades"] if x[5]<=tc]
    buys=[x for x in tr if x[1]=="buy"]
    for x in buys:
        cov[x[0]].add(m); first_buy[x[0]].setdefault(m,x)
    # bundles : >=3 acheteurs distincts dans la même seconde
    g=collections.defaultdict(set)
    for x in buys: g[x[5]].add(x[0])
    bs=[(s,w) for s,w in sorted(g.items()) if len(w)>=3]
    for s,w in bs: BUN.append((m,s,tc,frozenset(w)))
    if bs and v["complet"]:
        s0=bs[0][0]; after=[x for x in buys if x[5]>s0+1 and x[0] not in bs[0][1]]
        p_entry=after[0][4] if after else None
        p_post=[x[4] for x in tr if x[5]<=tc][-1] if tr else None
        p_max10=max([x[4] for x in v["trades"] if tc<x[5]<=tc+600] or [0])
        if p_entry and p_post: ENTRY.append((m,s0,tc,(tc-s0)/60,p_post/p_entry,(p_max10/p_entry) if p_max10 else None, len(bs[0][1])))
print(f"tokens {N} (complets jusqu'au post: {sum(v['complet'] for v in D.values())})")
print("\n=== A. WALLETS qui achètent AVANT le post (perdants compris), par nb de calls ===")
R=sorted(cov.items(), key=lambda x:-len(x[1]))
for a,ms in R[:20]:
    pr=[prof.get((m,a)) for m in ms if prof.get((m,a))]; mise=sum(p[0] for p in pr); g=sum(p[1] for p in pr)
    f=fund.get(a,("","",0))
    print(f"{a} {len(ms)}/{N} calls | P&L connu sur {len(pr)}: mise ${mise:,.0f} gain ${g:,.0f} | financeur {f[1] or f[0][:8]} {f[2]}")
print("\n=== C. BUNDLES (>=3 wallets même seconde avant le post) ===")
toks=collections.defaultdict(list)
for b in BUN: toks[b[0]].append(b)
print("tokens avec bundle:",len(toks),"/",N)
# lier les bundles entre tokens par wallets communs
W2B=collections.defaultdict(set)
for i,b in enumerate(BUN):
    for w in b[3]: W2B[w].add(i)
P=list(range(len(BUN)))
def f(x):
    while P[x]!=x: P[x]=P[P[x]]; x=P[x]
    return x
for w,ids in W2B.items():
    ids=list(ids)
    if len({BUN[i][0] for i in ids})>40: continue   # wallet bot partout -> pas un lien
    for i in ids[1:]: P[f(i)]=f(ids[0])
G=collections.defaultdict(list)
for i in range(len(BUN)): G[f(i)].append(i)
res=[]
for r,ids in G.items():
    tk=sorted({BUN[i][0] for i in ids}, key=lambda m:D[m]["tc"])
    if len(tk)<2: continue
    ws=set().union(*[BUN[i][3] for i in ids])
    res.append((len(tk),tk,ids,ws))
res.sort(key=lambda x:-x[0])
for n,tk,ids,ws in res[:10]:
    fr=collections.Counter((fund.get(w,("?","",0))[1] or fund.get(w,("?","",0))[0][:8]) for w in ws).most_common(3)
    am=collections.Counter(fund.get(w,("","",0))[2] for w in ws if w in fund).most_common(5)
    dl=[round((D[BUN[i][0]]["tc"]-BUN[i][1])/60) for i in ids]
    print(f"\nGROUPE de bundles sur {n} calls, {len(ws)} wallets | financeurs {fr} | montants SOL {am}")
    for m in tk: print("   ", dt.datetime.utcfromtimestamp(D[m]['tc']).strftime('%Y-%m-%d'), m[:8], "bundle", min(round((D[m]['tc']-BUN[i][1])/60) for i in ids if BUN[i][0]==m), "min avant le post")
    print("    wallets:", " ".join(sorted(ws, key=lambda w:-len(cov[w]))[:6]))
print("\n=== D. ENTRER JUSTE APRÈS LE 1er BUNDLE ===")
if ENTRY:
    x=[e[4] for e in ENTRY]; y=[e[5] for e in ENTRY if e[5]]
    print("tokens:",len(ENTRY)," délai bundle->post médiane", round(st.median([e[3] for e in ENTRY])), "min")
    print("prix au post / prix juste après bundle : médiane x%.2f, quartiles %s, gagnant (>1) %d/%d" % (st.median(x), [round(q,2) for q in st.quantiles(x,n=4)], sum(v>1 for v in x), len(x)))
    if y: print("max des 10 min après post / prix après bundle : médiane x%.2f, >2x: %d/%d" % (st.median(y), sum(v>2 for v in y), len(y)))
    for lo,hi in [(0,30),(30,180),(180,1440),(1440,99999)]:
        s=[e[4] for e in ENTRY if lo<=e[3]<hi]
        if s: print(f"  bundle {lo}-{hi} min avant post: {len(s)} tokens, médiane x{st.median(s):.2f}, gagnants {sum(v>1 for v in s)}/{len(s)}")
