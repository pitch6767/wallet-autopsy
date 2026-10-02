import json, urllib.request
def get(u):
    return json.loads(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent":"x"}), timeout=40).read())
res = json.load(open("diagnostic/etude_mm.json")) if False else None
C="https://clob.polymarket.com"
mk = {}
cur=""
qs = ["Spain snap election called by October 31?","Will Taylor Swift's daily YouTube view count hit 24M in October?","Rain during the Bahrain Grand Prix?","Will Hong Kong have between 70-120mm","Will DeepSeek have the highest OpenRouter"]
for _ in range(100):
    d=get(f"{C}/sampling-markets"+(f"?next_cursor={cur}" if cur else ""))
    for x in d["data"]:
        for q in qs:
            if x.get("question","").startswith(q[:40]): mk[q]=x
    cur=d.get("next_cursor") or ""
    if not cur or cur=="LTE=": break
for q,x in mk.items():
    t=x["tokens"][0]["token_id"]
    b=get(f"{C}/book?token_id={t}")
    bids=sorted(b["bids"],key=lambda n:-float(n["price"]))[:6]; asks=sorted(b["asks"],key=lambda n:float(n["price"]))[:6]
    print("\n==",q,"| rewards:",x.get("rewards"))
    print(" bids:",[(n["price"],n["size"]) for n in bids])
    print(" asks:",[(n["price"],n["size"]) for n in asks])
    print(" tick", x.get("minimum_tick_size"), "min order", x.get("minimum_order_size"))
