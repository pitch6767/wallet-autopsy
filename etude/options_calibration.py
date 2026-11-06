# 06.11.2026 (Pitch : « approfondis bien options Deribit ») — Les OUI Polymarket « Bitcoin above X on <date> » sortent ~8–9 c sous la
# probabilité Deribit, toujours dans le même sens. Avant d'y croire : Polymarket se trompe-t-il VRAIMENT ? On le juge sur le RÉSULTAT réel
# des marchés déjà réglés (35 derniers jours), sans hypothèse de modèle, puis on compare au modèle options (prix Binance + DVOL Deribit).
# Données : Gamma (marchés réglés), CLOB prices-history (prix Polymarket dans le temps), Binance klines 5 min, Deribit DVOL (vol implicite 30 j).
# Aucun ordre. Sortie sans signes inférieur / supérieur.
import json, sys, time, math, urllib.request, collections, datetime as dt
def get(u, essais=3):
    for i in range(essais):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers={"user-agent": "etude-options"}), timeout=60) as r: return json.load(r)
        except Exception as e:
            if i == essais - 1: print("ERREUR", u[:90], str(e)[:80]); return None
            time.sleep(1.5)
N = lambda x: 0.5 * (1 + math.erf(x / math.sqrt(2)))
MAINT = time.time(); DEBUT = MAINT - 36 * 86400
# 1. marchés « above » réglés
marches = []; vus = set()
for off in range(0, 3000, 100):
    ev = get(f"https://gamma-api.polymarket.com/events?tag_slug=bitcoin&closed=true&limit=100&offset={off}&order=endDate&ascending=false")
    if not ev: break
    stop = False
    for e in ev:
        fin_e = e.get("endDate") or ""
        try: tf = dt.datetime.fromisoformat(fin_e.replace("Z", "+00:00")).timestamp()
        except Exception: continue
        if tf < DEBUT: stop = True; continue
        if "bitcoin-above" not in str(e.get("slug", "")): continue
        for m in e.get("markets") or []:
            if m["id"] in vus: continue
            q = str(m.get("question", ""))
            if "above" not in q.lower(): continue
            try:
                px = [float(x) for x in json.loads(m.get("outcomePrices") or "[]")]; toks = json.loads(m.get("clobTokenIds") or "[]")
                K = float(str(m.get("groupItemTitle") or "").replace(",", "").replace("$", "")) if any(c.isdigit() for c in str(m.get("groupItemTitle") or "")) else None
                if K is None:
                    import re; mm = re.search(r"\$([\d,]+)", q); K = float(mm.group(1).replace(",", "")) if mm else None
                fin = dt.datetime.fromisoformat(str(m.get("endDate")).replace("Z", "+00:00")).timestamp()
            except Exception: continue
            if not K or len(px) != 2 or not toks or max(px) != 1: continue
            vus.add(m["id"]); marches.append(dict(id=m["id"], K=K, fin=fin, tok=toks[0], oui=px[0] == 1, q=q))
    if stop and off > 300: break
print("marchés « above » réglés trouvés :", len(marches))
# 2. Binance 5 min et DVOL
bin5 = {}
t = int(DEBUT * 1000)
while t < MAINT * 1000:
    k = get(f"https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=5m&startTime={t}&limit=1000")
    if not k: break
    for b in k: bin5[int(b[0]) // 1000] = float(b[4])
    t = int(k[-1][0]) + 300000
    if len(k) < 1000: break
dv = get(f"https://www.deribit.com/api/v2/public/get_volatility_index_data?currency=BTC&start_timestamp={int(DEBUT*1000)}&end_timestamp={int(MAINT*1000)}&resolution=3600")
dvol = {int(x[0]) // 1000: float(x[4]) for x in ((dv or {}).get("result", {}).get("data") or [])}
print("bougies Binance 5 min :", len(bin5), "; heures DVOL :", len(dvol))
def prix_btc(ts):
    b = int(ts) // 300 * 300 - 300
    return bin5.get(b)
def vol(ts):
    h = int(ts) // 3600 * 3600 - 3600
    for d in range(0, 6):
        if h - d * 3600 in dvol: return dvol[h - d * 3600] / 100
    return None
# 3. prix Polymarket dans le temps et comparaison
HEURES = [1, 2, 3, 6, 12, 24]
L = []
for i, m in enumerate(marches):
    h = get(f"https://clob.polymarket.com/prices-history?market={m['tok']}&startTs={int(m['fin'] - 26*3600)}&endTs={int(m['fin'])}&fidelity=5")
    hist = sorted((int(x["t"]), float(x["p"])) for x in ((h or {}).get("history") or []))
    if not hist: continue
    for hh in HEURES:
        ts = m["fin"] - hh * 3600
        avant = [p for (t2, p) in hist if t2 <= ts and t2 >= ts - 1800]
        if not avant: continue
        p = avant[-1]; S = prix_btc(ts); s = vol(ts)
        if not S or not s or not (0.02 <= p <= 0.98): continue
        sT = s * math.sqrt(hh / 8766); d2 = (math.log(S / m["K"]) - sT * sT / 2) / sT
        L.append(dict(h=hh, p=p, juste=N(d2), oui=m["oui"], jour=dt.datetime.utcfromtimestamp(m["fin"]).strftime("%m-%d"), K=m["K"], S=S, iv=s))
    if i % 100 == 0: print("…", i, len(L), flush=True)
print("observations :", len(L))
def resume(titre, G):
    print("\n=== " + titre + " ===")
    for k in sorted(G):
        v = G[k]
        if len(v) >= 15: print(f"{k}: {len(v)} obs. | prix Polymarket moyen {100*sum(x['p'] for x in v)/len(v):5.1f} % | modèle options {100*sum(x['juste'] for x in v)/len(v):5.1f} % | RÉALISÉ {100*sum(x['oui'] for x in v)/len(v):5.1f} %")
G = collections.defaultdict(list); H = collections.defaultdict(list)
for x in L:
    G[f"prix PM {int(x['p']*10)/10:.1f}-{int(x['p']*10)/10+0.1:.1f}"].append(x)
    H[f"modèle {int(x['juste']*10)/10:.1f}-{int(x['juste']*10)/10+0.1:.1f}"].append(x)
resume("Par prix Polymarket : qui a raison, Polymarket ou les options ?", G)
resume("Par probabilité du modèle options (prix Binance + DVOL)", H)
# 4. stratégie : acheter le côté sous-évalué selon le modèle (coût = prix + 1 c d'écart + frais 0,07·p·(1−p))
fee = lambda q: 0.07 * q * (1 - q)
print("\n=== Stratégie : acheter le côté moins cher que le modèle options (mise 100 $, prix + 1 c, frais compris) ===")
for marge in (0.03, 0.05, 0.08, 0.12):
    for hs in ((1, 2, 3), (6, 12, 24)):
        R = collections.defaultdict(lambda: [0.0, 0, 0]); vu = set()
        for x in L:
            if x["h"] not in hs: continue
            for cote, q, gagne in (("OUI", x["p"] + 0.01, x["oui"]), ("NON", 1 - x["p"] + 0.01, not x["oui"])):
                juste = x["juste"] if cote == "OUI" else 1 - x["juste"]
                if q >= 0.99 or juste - q - fee(q) < marge: continue
                g = 100 * ((1 / (q + fee(q)) - 1) if gagne else -1)
                per = "26.10-05.11" if x["jour"] >= "10-26" else "01-25.10"
                r = R[per]; r[0] += g; r[1] += 1; r[2] += gagne
        print(f"marge ≥ {marge:.2f}, à {hs} h de la fin : " + " | ".join(f"{k} : {v[1]} trades, {100*v[2]/max(1,v[1]):.0f} % gagnés, {v[0]:+.0f} $" for k, v in sorted(R.items())))
print("\nvol implicite moyenne DVOL utilisée :", round(100 * sum(x["iv"] for x in L) / max(1, len(L)), 1), "%")
print("FIN")
