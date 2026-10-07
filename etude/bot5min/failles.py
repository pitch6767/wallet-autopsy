"""Chasse aux failles (07.10.2026, demande de Pitch : « il y en a toujours une »).
A. Echelles de prix crypto sur Polymarket (« Bitcoin above X on ... ») = strip d'options digitales.
   Sans arbitrage : P(au-dessus de K) decroit avec K. Faille = acheter OUI(K bas) + NON(K haut) pour moins de 1 $
   (paye au moins 1 $ quoi qu'il arrive, 2 $ si le prix finit entre les deux) -> spread vertical gratuit.
B. Fourchettes exclusives (« between X and Y ») : somme des OUI achetables < 1 $ -> acheter tout ; somme des NON < n-1 -> idem.
C. Remboursements maker sur les 5 min BTC/ETH : 20 % des frais taker reverses aux makers -> combien par part servie,
   et ce que ca change pour la paire complete (portefeuille 0x41e2) ; champs de recompenses de liquidite des marches.
Tout en lecture seule, carnets reels (CLOB), plusieurs passages pour voir si les failles durent.
"""
import json, re, sys, time, statistics, collections, urllib.request
sys.path.insert(0, "etude/bot5min")
from portefeuilles import get, D, G

C = "https://clob.polymarket.com"
OUT = "etude/bot5min/"
FEE = lambda p: 0.072 * p * (1 - p)


def log(*a): print(*a, flush=True)


def livre(tok):
    try:
        b = get(f"{C}/book?token_id={tok}", tries=3)
        asks = sorted(((float(x["price"]), float(x["size"])) for x in b.get("asks", [])))
        bids = sorted(((float(x["price"]), float(x["size"])) for x in b.get("bids", [])), reverse=True)
        return asks, bids
    except Exception:
        return [], []


def nombre(q):
    """premier prix dans la question : $120,000 / 120k / 4,500"""
    m = re.search(r"\$\s?([\d,]+(?:\.\d+)?)\s*([kK])?", q) or re.search(r"([\d,]{4,}(?:\.\d+)?)", q)
    if not m: return None
    v = float(m.group(1).replace(",", ""))
    if len(m.groups()) > 1 and m.group(2): v *= 1000
    return v


def evenements():
    E = []
    for off in range(0, 3000, 100):
        try: lot = get(f"{G}/events?closed=false&active=true&limit=100&offset={off}&tag_slug=crypto")
        except Exception: break
        if not lot: break
        E += lot
        if len(lot) < 100: break
    return E


def scan(E):
    res = []
    for e in E:
        M = [m for m in (e.get("markets") or []) if m.get("active") and not m.get("closed") and m.get("clobTokenIds")]
        if len(M) < 3: continue
        titre = e.get("title") or ""
        lignes = []
        for m in M:
            try: toks = json.loads(m["clobTokenIds"]); outs = json.loads(m["outcomes"])
            except Exception: continue
            if len(toks) != 2: continue
            q = m.get("question") or m.get("groupItemTitle") or ""
            k = nombre(m.get("groupItemTitle") or q)
            yes = toks[outs.index("Yes")] if "Yes" in outs else toks[0]; no = toks[1] if yes == toks[0] else toks[0]
            lignes.append({"q": q, "k": k, "yes": yes, "no": no, "neg": m.get("negRisk") or e.get("negRisk")})
        if len(lignes) < 3: continue
        dessus = all(re.search(r"above|over|reach|hit|>|higher", l["q"], re.I) for l in lignes) and all(l["k"] for l in lignes)
        fourchette = bool(e.get("negRisk")) or all(re.search(r"between|range|-|to ", l["q"], re.I) for l in lignes)
        for l in lignes:
            l["ya"], l["yb"] = livre(l["yes"]); l["na"], l["nb"] = livre(l["no"])
        if dessus and not re.search(r"reach|hit", titre + lignes[0]["q"], re.I):
            L = sorted(lignes, key=lambda l: l["k"])
            for i in range(len(L)):
                for j in range(i + 1, len(L)):
                    lo, hi = L[i], L[j]
                    if not lo["ya"] or not hi["na"]: continue
                    a, b = lo["ya"][0], hi["na"][0]
                    cout = a[0] + b[0]
                    res.append({"type": "echelle", "titre": titre, "jambes": f"OUI >{lo['k']:g} a {a[0]} + NON >{hi['k']:g} a {b[0]}", "cout": cout,
                                "net": 1 - cout - FEE(a[0]) - FEE(b[0]), "taille": min(a[1], b[1])})
        if fourchette:
            ya = [l["ya"][0] if l["ya"] else None for l in lignes]
            if all(ya):
                s = sum(p for p, _ in ya)
                res.append({"type": "fourchettes OUI", "titre": titre, "jambes": f"{len(ya)} OUI", "cout": s, "net": 1 - s - sum(FEE(p) for p, _ in ya), "taille": min(z for _, z in ya)})
            na = [l["na"][0] if l["na"] else None for l in lignes]
            if all(na):
                s = sum(p for p, _ in na); n = len(na)
                res.append({"type": "fourchettes NON", "titre": titre, "jambes": f"{n} NON (paye {n - 1} $)", "cout": s / (n - 1), "net": (n - 1 - s - sum(FEE(p) for p, _ in na)) / (n - 1), "taille": min(z for _, z in na)})
    return res


def remboursements(n=80):
    rap = ["## C. Remboursements maker sur les 5 min", ""]
    maintenant = int(time.time()) // 300 * 300
    champs = None
    for a in ("btc", "eth"):
        frais = 0.0; parts = 0.0; k_ok = 0
        for k in range(3, 3 + n):
            st = maintenant - 300 * k
            try:
                ev = get(f"{G}/events?slug={a}-updown-5m-{st}"); m = ev[0]["markets"][0]; cid = m["conditionId"]
                if champs is None: champs = {kk: m[kk] for kk in m if re.search(r"reward|fee|maker|rebate|spread|minSize", kk, re.I)}
            except Exception: continue
            k_ok += 1
            for off in (0, 500, 1000, 1500, 2000):
                try: lot = get(f"{D}/trades?market={cid}&limit=500&offset={off}&takerOnly=true")
                except Exception: break
                for t in lot:
                    p = float(t["price"]); sz = float(t["size"]); frais += FEE(p) * sz; parts += sz
                if len(lot) < 500: break
        if parts:
            r = 0.2 * frais / parts
            rap.append(f"- {a.upper()} : {k_ok} marches, {parts:.0f} parts echangees, frais taker {frais:.0f} $ -> remboursement maker ≈ **{100 * r:.2f} cents par part servie** "
                       f"(≈ {200 * r:.2f} cents par paire Up+Down servie, soit {200 * r / 0.975:.2f} % d'une paire a 0,975)")
    rap += ["", "Champs recompenses/frais d'un marche 5 min (gamma) : `" + json.dumps(champs or {}, ensure_ascii=False)[:800] + "`", ""]
    return rap


def main():
    passages = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    rap = ["# Chasse aux failles — Polymarket crypto", ""]
    try: rap += remboursements()
    except Exception as e: rap.append(f"remboursements : erreur {e}")
    open(OUT + "resultat_failles.md", "w").write("\n".join(rap))
    E = evenements(); log("evenements crypto ouverts", len(E))
    vus = collections.defaultdict(list)
    for p in range(passages):
        t0 = time.time()
        R = scan(E)
        for r in R: vus[(r["type"], r["titre"], r["jambes"].split(" a ")[0])].append(r)
        log("passage", p, len(R), "combinaisons", f"{time.time() - t0:.0f} s")
        if p < passages - 1: time.sleep(max(0, 300 - (time.time() - t0)))
    lignes = []
    for cle, L in vus.items():
        best = max(L, key=lambda r: r["net"])
        lignes.append((best["net"], cle, best, sum(1 for r in L if r["net"] > 0), len(L)))
    lignes.sort(key=lambda x: -x[0])
    rap += [f"## A/B. Echelles et fourchettes crypto ouvertes — {len(E)} evenements, {passages} passages a 5 min d'intervalle", "",
            "Net = gain garanti par dollar de paiement, frais taker 0,072·p·(1−p) compris (hypothese prudente). Positif = faille.", "",
            "| Type | Evenement | Jambes (meilleur moment) | Cout | Net garanti | Taille dispo (parts) | Passages positifs |", "|---|---|---|---|---|---|---|"]
    for net, cle, b, npos, n in lignes[:40]:
        rap.append(f"| {b['type']} | {b['titre'][:60]} | {b['jambes']} | {b['cout']:.3f} | **{net:+.3f}** | {b['taille']:.0f} | {npos}/{n} |")
    pos = [x for x in lignes if x[0] > 0]
    rap += ["", f"Combinaisons avec un gain garanti > 0 au moins une fois : **{len(pos)}** sur {len(lignes)}."]
    open(OUT + "resultat_failles.md", "w").write("\n".join(rap))
    print("\n".join(rap))


if __name__ == "__main__":
    main()
