# Analyse du portefeuille hqb.prediction (lecture seule, API publique Polymarket)
import json, urllib.request, urllib.parse, time, collections, datetime
U = "0x76eca4109d0dfe8649d5e3861dfccac67ae7d630"
B = "https://data-api.polymarket.com"
OUT = "etude/hqb/"

def get(url):
    for k in range(4):
        try:
            r = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            return json.load(urllib.request.urlopen(r, timeout=30))
        except Exception as e:
            print("erreur", url, e); time.sleep(3)
    return []

def pages(path, maxn=50000):
    out, cur = [], None
    while len(out) < maxn:
        url = f"{B}{path}&user={U}&limit=1000" + (f"&cursor={urllib.parse.quote(cur)}" if cur else "")
        j = get(url)
        data = j.get("data", []) if isinstance(j, dict) else (j or [])
        for d in data:
            for k in list(d.keys()):
                c = "".join(w if i==0 else w.capitalize() for i,w in enumerate(k.split("_")))
                d.setdefault(c, d[k])
            d.setdefault("timestamp", d.get("last_event_at"))
            d.setdefault("totalBought", d.get("total_size"))
            d.setdefault("cashPnl", d.get("total_pnl"))
        out += data
        pg = j.get("pagination", {}) if isinstance(j, dict) else {}
        cur = pg.get("next_cursor")
        if not data or not pg.get("has_more") or not cur: break
        time.sleep(0.3)
    return out

closed = pages("/v2/positions?status=CLOSED")
openp = pages("/v2/positions?status=OPEN")
act = pages("/v2/activity?x=1")
json.dump(closed, open(OUT+"closed.json","w"))
json.dump(openp, open(OUT+"open.json","w"))
json.dump(act, open(OUT+"activity.json","w"))

def mois(ts):
    try: return datetime.datetime.utcfromtimestamp(int(ts)).strftime("%Y-%m")
    except: return "?"

L = []
L.append(f"Positions fermees: {len(closed)} | ouvertes: {len(openp)} | lignes d'activite: {len(act)}")
tot = sum(float(c.get("realizedPnl",0)) for c in closed)
gagn = [c for c in closed if float(c.get("realizedPnl",0)) > 0]
L.append(f"PnL realise total (fermees): {tot:,.0f} $ | gagnantes {len(gagn)} / {len(closed)}")
op = sum(float(p.get("cashPnl",0)) for p in openp)
L.append(f"PnL latent (ouvertes): {op:,.0f} $ | valeur ouverte {sum(float(p.get('currentValue',0)) for p in openp):,.0f} $")

L.append("\n== PnL realise par mois (date de cloture) ==")
pm = collections.defaultdict(lambda:[0.0,0,0,0.0])
for c in closed:
    m = mois(c.get("timestamp")); x = float(c.get("realizedPnl",0))
    pm[m][0]+=x; pm[m][1]+=1; pm[m][2]+= x>0; pm[m][3]+= float(c.get("total_cost_usdc") or 0)
for m in sorted(pm): L.append(f"{m}: PnL {pm[m][0]:>12,.0f} $ | {pm[m][2]}/{pm[m][1]} gagnantes | mise ~{pm[m][3]:,.0f} $")

def typ(t):
    t=(t or "").lower()
    for k in ["dip to","reach","up or down","above","below","between","price of"]:
        if k in t: return k
    return "autre"
L.append("\n== Par type de marche ==")
pt = collections.defaultdict(lambda:[0.0,0,0])
for c in closed:
    k=typ(c.get("title")); x=float(c.get("realizedPnl",0)); pt[k][0]+=x; pt[k][1]+=1; pt[k][2]+= x>0
for k,v in sorted(pt.items(), key=lambda kv:-kv[1][0]): L.append(f"{k}: PnL {v[0]:,.0f} $ | {v[2]}/{v[1]} gagnantes")

L.append("\n== Par prix d'entree ==")
pb = collections.defaultdict(lambda:[0.0,0,0])
for c in closed:
    a=float(c.get("avgPrice",0)); b = "<10c" if a<.1 else "10-30c" if a<.3 else "30-70c" if a<.7 else "70-90c" if a<.9 else ">90c"
    x=float(c.get("realizedPnl",0)); pb[b][0]+=x; pb[b][1]+=1; pb[b][2]+= x>0
for k,v in pb.items(): L.append(f"{k}: PnL {v[0]:,.0f} $ | {v[2]}/{v[1]} gagnantes")

L.append("\n== 15 plus gros gains / 15 plus grosses pertes ==")
s = sorted(closed, key=lambda c: float(c.get("realizedPnl",0)))
for c in s[::-1][:15]+s[:15]:
    L.append(f"{mois(c.get('timestamp'))} | {c.get('title')} [{c.get('outcome')}] entree {float(c.get('avgPrice',0))*100:.1f}c | PnL {float(c.get('realizedPnl',0)):,.0f} $")

L.append("\n== Activite par mois (achats/ventes en $) ==")
am = collections.defaultdict(lambda: collections.Counter())
for a in act:
    am[mois(a.get("timestamp"))][(a.get("type"),a.get("side"))] += float(a.get("usdcSize") or 0)
for m in sorted(am): L.append(m+": "+", ".join(f"{k[0]}/{k[1]}={v:,.0f}" for k,v in am[m].items()))

L.append("\n== Taille typique des ordres (TRADE BUY) ==")
buys=[a for a in act if a.get("type")=="TRADE" and a.get("side")=="BUY"]
if buys:
    sz=sorted(float(a.get("usdcSize") or 0) for a in buys)
    L.append(f"{len(buys)} achats | mediane {sz[len(sz)//2]:,.0f} $ | max {sz[-1]:,.0f} $")
open(OUT+"resume.txt","w").write("\n".join(L))
print("\n".join(L))
