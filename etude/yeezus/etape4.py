# Étape 4 : relance des CA manquants (429) avec pauses
import json, urllib.request, time, re
H = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36", "accept": "application/json"}
KEEP = re.compile(r"address|profit|buy|sell|holding|tag|cost|time|active|name|twitter|amount|balance|usd|history", re.I)
T = json.load(open("etude/yeezus/traders.json"))
manq = [m for m, v in T.items() if not v["traders"]]; print("manquants", len(manq))
for mint in manq:
    for essai in range(6):
        try:
            j = json.loads(urllib.request.urlopen(urllib.request.Request(f"https://gmgn.ai/vas/api/v1/token_traders/sol/{mint}?limit=100&orderby=profit&direction=desc", headers=H), timeout=40).read())
            lst = (j.get("data") or {}).get("list") or []
            T[mint]["traders"] = [{k: v for k, v in t.items() if KEEP.search(k) and not isinstance(v, dict)} for t in lst]
            print(mint, len(lst)); break
        except Exception as e:
            s = str(e); print("ERR", mint, s[:40], essai)
            if "429" not in s: break
            time.sleep(15 * (essai + 1))
    time.sleep(4)
json.dump(T, open("etude/yeezus/traders.json", "w"))
print("FIN", sum(1 for v in T.values() if v["traders"]), "/", len(T))
