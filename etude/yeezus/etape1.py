# Étape 1 : lire tout le canal t.me/s/cryptoyeezuscalls + sonder les sources Solana
import json, re, time, urllib.request, html
UA = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36", "accept": "*/*"}
def get(u, data=None, h=None):
    hh = dict(UA); hh.update(h or {})
    r = urllib.request.Request(u, data=data, headers=hh)
    return urllib.request.urlopen(r, timeout=40).read()
CA = re.compile(r"\b[1-9A-HJ-NP-Za-km-z]{32,44}\b")
msgs = {}; before = None
for page in range(200):
    u = "https://t.me/s/cryptoyeezuscalls" + (f"?before={before}" if before else "")
    try: t = get(u).decode("utf-8", "ignore")
    except Exception as e: print("ERR page", page, e); break
    blocks = t.split('class="tgme_widget_message_wrap')[1:]
    ids = []
    for b in blocks:
        m = re.search(r'data-post="cryptoyeezuscalls/(\d+)"', b)
        if not m: continue
        i = int(m.group(1)); ids.append(i)
        tx = re.search(r'tgme_widget_message_text[^>]*>(.*?)</div>', b, re.S)
        txt = html.unescape(re.sub(r"<br\s*/?>", "\n", tx.group(1))) if tx else ""
        txt = re.sub(r"<[^>]+>", " ", txt)
        links = re.findall(r'href="([^"]+)"', b)
        d = re.search(r'datetime="([^"]+)"', b)
        allt = txt + " " + " ".join(links)
        cas = sorted(set(c for c in CA.findall(allt) if not c.isdigit()))
        msgs[i] = {"id": i, "date": d.group(1) if d else None, "texte": txt.strip()[:1500], "cas": cas, "liens": [l for l in links if "t.me/cryptoyeezus" not in l][:10]}
    print("page", page, "messages", len(ids), "min", min(ids) if ids else None)
    if not ids or (before and min(ids) >= before): break
    before = min(ids)
    if before <= 1: break
    time.sleep(1.5)
L = [msgs[k] for k in sorted(msgs)]
json.dump(L, open("etude/yeezus/messages.json", "w"), ensure_ascii=False, indent=1)
avec = [m for m in L if m["cas"]]
print("TOTAL messages", len(L), "avec CA", len(avec), "CA distincts", len(set(c for m in avec for c in m["cas"])))
for m in L[:3] + L[-3:]: print(json.dumps(m, ensure_ascii=False)[:600])
# sondes sources
mint = None
for m in avec:
    for c in m["cas"]:
        mint = c; break
    if mint: break
print("MINT TEST", mint)
tests = {
 "gmgn_top_traders": f"https://gmgn.ai/defi/quotation/v1/tokens/top_traders/sol/{mint}?orderby=profit&direction=desc",
 "gmgn_token": f"https://gmgn.ai/api/v1/token_info/sol/{mint}",
 "dexscreener": f"https://api.dexscreener.com/latest/dex/tokens/{mint}",
 "gecko_pools": f"https://api.geckoterminal.com/api/v2/networks/solana/tokens/{mint}/pools",
 "birdeye_public": f"https://public-api.birdeye.so/defi/v2/tokens/top_traders?address={mint}",
 "solscan_pub": f"https://public-api.solscan.io/token/holders?tokenAddress={mint}",
 "pumpfun_trades": f"https://frontend-api-v3.pump.fun/trades/all/{mint}?limit=50&offset=0&minimumSize=0",
 "pumpfun_coin": f"https://frontend-api-v3.pump.fun/coins/{mint}",
}
for k, u in tests.items():
    try: b = get(u); print("SONDE", k, "OK", len(b), b[:300])
    except Exception as e: print("SONDE", k, "ERR", str(e)[:200])
try:
    b = get("https://api.mainnet-beta.solana.com", json.dumps({"jsonrpc":"2.0","id":1,"method":"getSignaturesForAddress","params":[mint,{"limit":5}]}).encode(), {"content-type":"application/json"})
    print("SONDE rpc OK", b[:400])
except Exception as e: print("SONDE rpc ERR", e)
