"""Places lentes : Limitless BTC 5 min et Kalshi BTC 15 min (07.10.2026, demande de Pitch).
Idee : quand le BTC bouge et que Polymarket a deja reprice (1 s) mais pas la place lente, on ACHETE sur la place lente tout ce qui est
encore vendu sous le nouveau prix (en descendant dans la profondeur), puis on REVEND sur la meme place quand elle a rattrape.
On ne garde pas jusqu'au resultat (la resolution ne compte pas). Gain mesure : revente au meilleur acheteur (profondeur comprise)
5 / 10 / 30 / 60 s apres, frais compris.
Modes : « sonde » ; « mesure N » (N minutes, chaque seconde).
"""
import json, sys, time, re, statistics, urllib.request, collections

OUT = "etude/bot5min/"
L = "https://api.limitless.exchange"
K = "https://api.elections.kalshi.com/trade-api/v2"
FEE_K = lambda p: 0.07 * p * (1 - p)          # Kalshi taker (par contrat)
FEE_L = lambda p: 0.0                          # Limitless : a confirmer (0 par defaut, gain brut)


def get(url, t=6):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "etude", "Accept": "application/json"}), timeout=t) as r: return json.loads(r.read())
    except Exception as e:
        return {"_erreur": str(e)[:200]}


def log(*a): print(*a, flush=True)


# ---------- Limitless
LIM = {"t": 0, "slug": None}
def lim_slug(now):
    if now - LIM["t"] > 15 or not LIM["slug"]:
        LIM["t"] = now; cands = []
        for url in (f"{L}/markets/active", f"{L}/markets/active?page=2"):
            r = get(url); d = (r.get("data") if isinstance(r, dict) else r) or []
            cands += [m for m in d if isinstance(m, dict) and re.match(r"btc-up-or-down-5-min-", m.get("slug") or "")]
        cands = [m for m in cands if (m.get("expirationTimestamp") or 0) / 1000 > now + 5]
        cands.sort(key=lambda m: m.get("expirationTimestamp") or 0)
        LIM["slug"] = cands[0]["slug"] if cands else None
        LIM["fin"] = cands[0]["expirationTimestamp"] / 1000 if cands else 0
    return LIM["slug"]


def lim_livre(slug):
    ob = get(f"{L}/markets/{slug}/orderbook")
    try:
        bids = sorted(((float(x["price"]), float(x["size"]) / 1e6) for x in ob.get("bids") or []), reverse=True)[:10]
        asks = sorted(((float(x["price"]), float(x["size"]) / 1e6) for x in ob.get("asks") or []))[:10]
        return bids, asks
    except Exception: return None, None


# ---------- Kalshi (Oui = BTC monte sur 15 min)
KAL = {"t": 0, "tk": None}
def kal_tk(now):
    if now - KAL["t"] > 15 or not KAL["tk"] or now > KAL.get("fin", 0) - 5:
        KAL["t"] = now
        r = get(f"{K}/markets?series_ticker=KXBTC15M&status=open&limit=20")
        try:
            M = sorted(r["markets"], key=lambda m: m["close_time"]); m = M[0]
            KAL["tk"] = m["ticker"]; KAL["fin"] = time.mktime(time.strptime(m["close_time"][:19], "%Y-%m-%dT%H:%M:%S")) - time.timezone
        except Exception: KAL["tk"] = None
    return KAL["tk"]


def kal_livre(tk):
    r = get(f"{K}/markets/{tk}/orderbook")
    try:
        ob = r.get("orderbook_fp") or r.get("orderbook")
        def lv(key, keyd):
            if ob.get(keyd): return [(float(p), float(q)) for p, q in ob[keyd]]
            return [(float(p) / 100, float(q)) for p, q in (ob.get(key) or [])]
        yes = lv("yes", "yes_dollars"); no = lv("no", "no_dollars")      # offres d'achat Oui / Non
        bids = sorted(yes, reverse=True)[:10]
        asks = sorted(((round(1 - p, 4), q) for p, q in no))[:10]        # vendre Non a p = vendre... acheter Oui a 1 - p
        return bids, asks
    except Exception: return None, None


# ---------- Polymarket (reference rapide)
POLY = {}
def poly_mid(now, d):
    st = int(now) // d * d; key = f"{d}"
    if POLY.get(key + "st") != st:
        ev = get(f"https://gamma-api.polymarket.com/events?slug=btc-updown-{d // 60}m-{st}")
        try: m = ev[0]["markets"][0]; toks = json.loads(m["clobTokenIds"]); outs = json.loads(m["outcomes"]); POLY[key] = toks[outs.index("Up")]
        except Exception: POLY[key] = None
        POLY[key + "st"] = st
    if not POLY.get(key): return None
    b = get(f"https://clob.polymarket.com/book?token_id={POLY[key]}")
    try: return (max(float(x["price"]) for x in b["bids"]) + min(float(x["price"]) for x in b["asks"])) / 2
    except Exception: return None


def sonde():
    now = time.time()
    s = lim_slug(now); log("Limitless", s, lim_livre(s) if s else None)
    tk = kal_tk(now); log("Kalshi", tk, kal_livre(tk) if tk else None)
    if tk: log("Kalshi brut", json.dumps(get(f"{K}/markets/{tk}/orderbook"))[:1500]); log("Kalshi marche", json.dumps(get(f"{K}/markets/{tk}"))[:1500])
    log("Poly 5m", poly_mid(now, 300), "Poly 15m", poly_mid(now, 900))


def mesure(minutes):
    S = []; t_fin = time.time() + 60 * minutes
    while time.time() < t_fin:
        t0 = time.time()
        btc = get("https://data-api.binance.vision/api/v3/ticker/price?symbol=BTCUSDT")
        s = lim_slug(t0); tk = kal_tk(t0)
        lb, la = lim_livre(s) if s else (None, None)
        kb, ka = kal_livre(tk) if tk else (None, None)
        S.append({"t": round(t0, 1), "btc": float(btc["price"]) if "price" in btc else None, "p5": poly_mid(t0, 300), "p15": poly_mid(t0, 900),
                  "ls": s, "lb": lb, "la": la, "ks": tk, "kb": kb, "ka": ka})
        time.sleep(max(0, 1 - (time.time() - t0)))
    json.dump(S, open(OUT + "places_lentes_brut.json", "w"))
    analyser(S)


def mid(b, a):
    return (b[0][0] + a[0][0]) / 2 if b and a else None


def analyser(S):
    rap = [f"# Places lentes — {len(S)} secondes ({time.strftime('%d.%m %H:%M', time.gmtime(S[0]['t']))} -> {time.strftime('%H:%M', time.gmtime(S[-1]['t']))} UTC)", "",
           "Evenement : le BTC bouge d'au moins X pb en 3 s, Polymarket a deja bouge dans le meme sens, la place lente pas encore (moins de 1 cent).",
           "Achat : tout ce qui est vendu sur la place lente jusqu'a (ancien milieu + mouvement de Polymarket - 1 cent), profondeur comprise.",
           "Revente : au meilleur acheteur de la meme place (profondeur comprise) N secondes plus tard. Pas de garde jusqu'au resultat.", ""]
    for nom, cs, cb, ca, cp, fee in (("Limitless BTC 5 min", "ls", "lb", "la", "p5", FEE_L), ("Kalshi BTC 15 min", "ks", "kb", "ka", "p15", FEE_K)):
        rap += [f"## {nom}", "", "| Seuil BTC | Evenements | Parts achetables (mediane) | Mise moyenne | Gain revente +5 s | +10 s | +30 s | +60 s | Gain total (+30 s) |", "|---|---|---|---|---|---|---|---|---|"]
        for seuil in (3, 5, 8):
            R = []; dernier = -99
            for i in range(3, len(S) - 61):
                x0, x1 = S[i - 3], S[i]
                if not x0["btc"] or not x1["btc"] or x0[cs] != x1[cs] or not x1[cs]: continue
                mv = (x1["btc"] / x0["btc"] - 1) * 1e4
                if abs(mv) < seuil or i - dernier < 10: continue
                up = mv > 0; sg = 1 if up else -1
                if x0[cp] is None or x1[cp] is None or (x1[cp] - x0[cp]) * sg < 0.02: continue
                m0, m1 = mid(x0[cb], x0[ca]), mid(x1[cb], x1[ca])
                if m0 is None or m1 is None or (m1 - m0) * sg >= 0.01: continue
                dernier = i
                cible = m0 + (x1[cp] - x0[cp])
                # achat : Oui (asks) si hausse, Non (= vendre Oui aux bids) si baisse
                parts = cout = 0.0
                if up:
                    for p, q in x1[ca] or []:
                        if p > cible - 0.01: break
                        parts += q; cout += q * (p + fee(p))
                else:
                    for p, q in x1[cb] or []:
                        if p < cible + 0.01: break
                        parts += q; cout += q * ((1 - p) + fee(p))     # acheter Non a 1 - bid Oui
                if parts <= 0: continue
                gains = {}
                for h in (5, 10, 30, 60):
                    y = S[i + h]
                    if y[cs] != x1[cs]: gains[h] = None; continue
                    reste = parts; recu = 0.0
                    niveaux = (y[cb] or []) if up else [(round(1 - p, 4), q) for p, q in (y[ca] or [])]   # revendre Oui aux bids / Non a 1 - ask Oui
                    for p, q in niveaux:
                        k = min(q, reste); recu += k * (p - fee(p)); reste -= k
                        if reste <= 1e-9: break
                    gains[h] = recu - cout if reste <= 1e-9 else None
                R.append({"parts": parts, "cout": cout, **{f"g{h}": gains[h] for h in (5, 10, 30, 60)}})
            if not R: rap.append(f"| {seuil} pb / 3 s | 0 | | | | | | | |"); continue
            def m(h):
                v = [r[f"g{h}"] for r in R if r[f"g{h}"] is not None]
                return f"{statistics.mean(v):+.2f} $ ({len(v)})" if v else "—"
            tot = sum(r["g30"] for r in R if r["g30"] is not None)
            rap.append(f"| {seuil} pb / 3 s | {len(R)} | {statistics.median(r['parts'] for r in R):.0f} | {statistics.mean(r['cout'] for r in R):.0f} $ | {m(5)} | {m(10)} | {m(30)} | {m(60)} | **{tot:+.2f} $** |")
        rap.append("")
    rap += ["Gain = par evenement, sur toute la taille achetee ; (n) = evenements ou la revente etait possible sur la meme echeance. Frais Kalshi 0,07·p·(1−p) compris ; Limitless sans frais (a confirmer)."]
    open(OUT + "resultat_places_lentes.md", "w").write("\n".join(rap))
    print("\n".join(rap))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "sonde": sonde()
    elif len(sys.argv) > 1 and sys.argv[1] == "analyser": analyser(json.load(open(OUT + "places_lentes_brut.json")))
    else: mesure(int(sys.argv[2]) if len(sys.argv) > 2 else 150)
