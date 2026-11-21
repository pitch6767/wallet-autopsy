# Étape 15 : par tranche (wallets reliés par les transferts), chaque call : nom, prix d'achat, de vente, plus haut après l'achat
import json, urllib.request, time, collections, datetime as dt
H = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36", "accept": "application/json", "referer": "https://gmgn.ai/"}
def get(u):
    for k in range(6):
        try: return json.loads(urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=40).read())
        except Exception as e:
            if "429" in str(e): time.sleep(5*(k+1)); continue
            return {"_err": str(e)[:100]}
    return {}
TC = json.load(open("etude/yeezus/traders_complet.json"))
CALL = {m: dt.datetime.fromisoformat(v["appel"]["date"]).timestamp() for m, v in TC.items()}
RESEAUX = {
 "Réseau 1 (FT9VD → 4xmBBT6U → FX5rF3 → 9jA4MU)": [
  ("Tranche 1 — 5aud5S", ["5aud5SUDR3eS2Es6a7gZDXedXMEJUnJG1XdzXXHu89YS"]),
  ("Tranche 2 — FT9VD + 51o5Vw", ["FT9VDscMGy2qDkcbFBD4xLkaGPBqkEgDA6E59GaHN7u6", "51o5VwwsB2KG1Ejuq2FdmaCQcnuTyKRF6c5HjtYVmEgr"]),
  ("Tranche 3 — relais 4xmBBT6U et ses receveurs", ["4xmBBT6ULCFgUUUPtc1L19Yjfxt912GYLx4da9pxKNr5", "BdpVwDK5qKNhPBuaXxMYPLuA4ufnNjYRvucytWPopNGB", "32WtUYouq7EtqtxfV8jC5GmVcRcQW9xfy1GEiyNcWGjm", "6Di9hEvtEmoTPHCy6L7PGr5jqTLXRPG1hY9dgjMTarY5", "Byw469gjf6Urs4NvCc2x2hJtkf43X7bhxaR3xABiMBug", "FX5rF3QAvqzhw5xTAJCF1Bo1gGVd8nSzquEnwhDRYeHX"]),
  ("Tranche 4 — groupe 9jA4MU", ["9jA4MUtsPAXy3ZhsiQUhkSXMop2ogrCWYv7rE9xovsWp", "43hawvey7znGUfxnGo54Wrm4uGRN7S4tawVBWgrxf4uV", "4r6qNe1XPwGaghFY6hmuDngdzzWaRJuhf8rdYA5vY4KZ", "592X5D58VB9QyHVv2EyKw7PnkJPY4x2giwVqtN32ays1", "5LE1mUudCxAZigJbaJDC4itTbbiy8P274fF256aQSQv", "97WJWwFk23Nu5QkxCSYgqRo89UvdsEApPJtSwhMJfzd9", "BDo54QPVCaFWEEfu4ftvyKL2tLXWEEa6dYvcBgVWpNYP", "C3zCUv1QyMLKmavQ4Q3a54zyfTBBfKjXcodp3AxkKiwi", "D2rcDMoWyayhMAPUdoHKoJz3syY6MHKm4hz4564jhetE", "E6syzgXYWzmqFnFRZM9bymhbTm8CKaBQ6wqYVXTvGhYW", "vAvfo5rEFSFh3zwYP9crZWZSnGT8FEn9FLoCpUJenzu"]),
 ],
 "Réseau 2 (6pNn9kad → EEbS5am → 2fZCfDPk)": [
  ("Tranche 1 — 6pNn9kad + GTgo1t + 7v56q43K", ["6pNn9kad5aC3ei9ztg62Y7RjFkTTavNsCfqcybVhCCx6", "GTgo1tRPS6q5vMjyXhK1vkfBuPPpefgiTdr3oKpytP54", "7v56q43K6MbxKGaFVTEej45sjJddLtUU3eMapDDSMJ8f"]),
  ("Tranche 2 — EEbS5am", ["EEbS5amC8uQbxhbMN5vy8h8eAEuGvsyeBN565Y6SCqME"]),
  ("Tranche 3 — 2fZCfDPk + F4iL5X", ["2fZCfDPk8hstiUgYbeadZSAmDGMMQmSJkfVqtfsGetaQ", "F4iL5Xphw6vQC4Wudv2RVgyMoxYJM56KTMRJYvPYBWLu"]),
 ]}
# sonde d'un endpoint de bougies
m0 = next(iter(TC)); now = int(time.time())
KL = None
for u in [f"https://gmgn.ai/api/v1/token_kline/sol/{m0}?resolution=1h&from={now-86400*400}&to={now}",
          f"https://gmgn.ai/vas/api/v1/token_kline/sol/{m0}?resolution=1h&from={now-86400*400}&to={now}",
          f"https://gmgn.ai/defi/quotation/v1/tokens/kline/sol/{m0}?resolution=1h&from={now-86400*400}&to={now}",
          f"https://gmgn.ai/api/v1/token_candles/sol/{m0}?resolution=1h&from={now-86400*400}&to={now}&limit=1000"]:
    j = get(u); d = j.get("data")
    L = d.get("list") if isinstance(d, dict) else d
    print("SONDE bougies", u.split("gmgn.ai")[1][:45], "n", len(L) if isinstance(L, list) else None, json.dumps(j)[:250])
    if isinstance(L, list) and L and KL is None: KL = u.split(m0)[0] + "{m}" + u.split(m0)[1].split("?")[0] + "?resolution={r}&from={f}&to={t}"
    time.sleep(1)
print("BOUGIES:", KL)
def plus_haut(m, depuis):
    if not KL: return None
    best = 0
    for r, span in (("1h", None),):
        j = get(KL.format(m=m, r="5m", f=int(depuis) - 300, t=min(now, int(depuis) + 10 * 86400))); d = j.get("data")
        L = d.get("list") if isinstance(d, dict) else d
        for c in L or []:
            h = float(c.get("high") or c.get("h") or 0)
            ts = int(c.get("time") or c.get("timestamp") or c.get("t") or 0)
            if ts > 1e12: ts //= 1000
            if ts >= depuis - 300: best = max(best, h)
    return best or None
def activite(w):
    out = []; cur = None
    for p in range(40):
        j = get(f"https://gmgn.ai/vas/api/v1/wallet_activity/sol?wallet={w}&limit=50" + (f"&cursor={cur}" if cur else ""))
        d = j.get("data") or {}; L = d.get("activities") or []
        out += L; cur = d.get("next")
        if not cur or not L: break
        time.sleep(0.3)
    return out
if False:
    a = activite("FT9VDscMGy2qDkcbFBD4xLkaGPBqkEgDA6E59GaHN7u6")
    print("EX ACTIVITE", json.dumps([x for x in a if x.get("event_type") in ("buy","sell")][:2])[:1500])
RES = {}
for reseau, tranches in RESEAUX.items():
    print(f"\n################ {reseau}", flush=True)
    tot = set()
    for nom, ws in tranches:
        par = collections.defaultdict(lambda: {"buy_usd": 0, "buy_qte": 0, "sell_usd": 0, "sell_qte": 0, "t0": None, "nom": "", "wallets": set()})
        for w in ws:
            for x in activite(w):
                t = x.get("token") or {}; m = t.get("address")
                if m not in CALL or x.get("event_type") not in ("buy", "sell"): continue
                r = par[m]; r["nom"] = t.get("symbol") or t.get("name") or ""; r["wallets"].add(w[:6])
                usd = float(x.get("cost_usd") or 0); q = float(x.get("token_amount") or 0); ts = x.get("timestamp") or 0
                if x["event_type"] == "buy":
                    r["buy_usd"] += usd; r["buy_qte"] += q; r["t0"] = min(r["t0"] or ts, ts)
                else: r["sell_usd"] += usd; r["sell_qte"] += q
        lignes = []
        for m, r in sorted(par.items(), key=lambda x: x[1]["t0"] or 0):
            if not r["buy_qte"]: continue
            pa = r["buy_usd"] / r["buy_qte"]; pv = (r["sell_usd"] / r["sell_qte"]) if r["sell_qte"] else None
            ph = plus_haut(m, r["t0"]); avance = round((CALL[m] - r["t0"]) / 60)
            lignes.append({"mint": m, "nom": r["nom"], "achat_date": time.strftime("%Y-%m-%d %H:%M", time.gmtime(r["t0"])), "minutes_avant_call": avance,
                           "prix_achat": pa, "prix_vente": pv, "plus_haut": ph, "mise": round(r["buy_usd"]), "vendu": round(r["sell_usd"]), "wallets": sorted(r["wallets"])})
            time.sleep(0.5)
        tot |= {l["mint"] for l in lignes}
        RES.setdefault(reseau, []).append({"tranche": nom, "calls": lignes})
        nav = sum(1 for l in lignes if l["minutes_avant_call"] > 0)
        print(f"\n=== {nom} : {len(lignes)} calls ({nav} achetés AVANT le call)", flush=True)
        for l in lignes:
            f = lambda v: f"{v:.8g}" if v else "-"
            mult = f"x{l['plus_haut']/l['prix_achat']:.1f}" if l["plus_haut"] and l["prix_achat"] else "-"
            print(f"  {l['achat_date']} {l['nom'][:14]:14} | {(str(l['minutes_avant_call'])+' min AVANT le call') if l['minutes_avant_call']>0 else ('même minute que le call' if l['minutes_avant_call']==0 else str(-l['minutes_avant_call'])+' min après le call')} | achat {f(l['prix_achat'])} $ | vente {f(l['prix_vente'])} $ | plus haut après achat {f(l['plus_haut'])} $ ({mult}) | mise {l['mise']} $ vendu {l['vendu']} $ | {','.join(l['wallets'])} | {l['mint']}", flush=True)
    av = {l["mint"] for t in RES[reseau] for l in t["calls"] if l["minutes_avant_call"] > 0}
    print(f"\nTOTAL {reseau} : {len(tot)} calls différents, dont {len(av)} achetés AVANT le call", flush=True)
json.dump(RES, open("etude/yeezus/resultat15.json", "w"))
print("FIN")

# v2 : plus haut sur 10 jours en bougies 5 min
