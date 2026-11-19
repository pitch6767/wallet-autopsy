# Étape 3 : top traders gmgn pour chaque CA du canal
import json, urllib.request, time, re
H = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36", "accept": "application/json"}
def get(u): return json.loads(urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=40).read())
L = json.load(open("etude/yeezus/messages.json"))
first = {}  # mint -> premier message (heure d'appel)
for m in L:
    for c in m["cas"]:
        if c not in first: first[c] = {"id": m["id"], "date": m["date"], "texte": m["texte"][:160]}
KEEP = re.compile(r"address|profit|buy|sell|holding|tag|cost|time|active|name|twitter|amount|balance|usd|history", re.I)
out = {}; n = 0
for mint, info in first.items():
    try:
        j = get(f"https://gmgn.ai/vas/api/v1/token_traders/sol/{mint}?limit=100&orderby=profit&direction=desc")
        lst = (j.get("data") or {}).get("list") or []
    except Exception as e:
        print("ERR", mint, str(e)[:80]); lst = None
    if lst is None or not lst: out[mint] = {"appel": info, "traders": []}; time.sleep(1); continue
    if n == 0: print("CLES", list(lst[0].keys())); print("EX", json.dumps(lst[0])[:3000])
    n += 1
    out[mint] = {"appel": info, "traders": [{k: v for k, v in t.items() if KEEP.search(k) and not isinstance(v, (dict,)) } for t in lst]}
    print(mint, len(lst), info["date"])
    time.sleep(1.2)
json.dump(out, open("etude/yeezus/traders.json", "w"))
print("FIN tokens avec traders", n, "sur", len(first))
