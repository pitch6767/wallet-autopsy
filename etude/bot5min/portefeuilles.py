"""Autopsie des portefeuilles qui gagnent sur les marches crypto Up/Down 5 min / 15 min de Polymarket (demande de Pitch, 07.10.2026).
Pour chaque portefeuille : sur quels marches, achete-t-il les deux cotes, cout moyen de la paire, desequilibre final, moment des achats,
part en taker, gain reel par marche (resolution officielle).
Portefeuilles : ceux cites comme gagnants sur le web + les plus actifs des derniers marches BTC/ETH 5 min.
"""
import json, sys, time, statistics, collections, urllib.request, urllib.parse

G = "https://gamma-api.polymarket.com"
D = "https://data-api.polymarket.com"
OUT = "etude/bot5min/"
NOMMES = {"0xb27bc932bf8110d8f78e55da7d5f0497a18b5b82": "web : paire complete"}
PSEUDOS = {"ohanism": "web : paire puis penchant", "bonereaper": "web : desequilibre", "stingo43": "web : fin a 0,99",
           "collabbsucksandiswashedongrok": "web : valeur juste"}


def get(url, tries=5):
    err = None
    for k in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "etude"}), timeout=60) as r:
                return json.loads(r.read())
        except Exception as e:
            err = e
            if "404" in str(e) or "400" in str(e): break
            time.sleep(8 if "429" in str(e) else 1.5 * (k + 1))
    raise err


def log(*a): print(*a, flush=True)


# ---------- resolution des marches (cache)
RES = {}
def resolution(slug):
    if slug in RES: return RES[slug]
    r = None
    try:
        ev = get(f"{G}/events?slug={slug}")
        m = ev[0]["markets"][0]
        out = json.loads(m["outcomes"]); px = [float(x) for x in json.loads(m["outcomePrices"])]
        if sorted(px) == [0.0, 1.0]: r = out[px.index(1.0)]
    except Exception: pass
    RES[slug] = r
    return r


def debut(slug):
    try: return int(slug.rsplit("-", 1)[1])
    except Exception: return None


def duree(slug):
    for k, v in (("-5m-", 300), ("-15m-", 900), ("-4h-", 14400), ("-1h-", 3600)):
        if k in slug: return v
    return None


# ---------- 1. pseudos -> adresses
def adresse(pseudo):
    try:
        r = get(f"{G}/public-search?q={urllib.parse.quote(pseudo)}&search_profiles=true&limit_per_type=5")
        for p in r.get("profiles") or []:
            if (p.get("name") or "").lower() == pseudo.lower() or (p.get("pseudonym") or "").lower() == pseudo.lower():
                return p.get("proxyWallet")
        P = r.get("profiles") or []
        return P[0].get("proxyWallet") if P else None
    except Exception as e:
        log("recherche", pseudo, e); return None


# ---------- 2. les plus actifs des derniers marches 5 min
def actifs_recents(n_cycles=60):
    maintenant = int(time.time()) // 300 * 300
    compte = collections.Counter(); vol = collections.Counter()
    for a in ("btc", "eth"):
        for k in range(2, 2 + n_cycles):
            st = maintenant - 300 * k
            try:
                ev = get(f"{G}/events?slug={a}-updown-5m-{st}")
                cid = ev[0]["markets"][0]["conditionId"]
            except Exception: continue
            vus = set()
            for off in (0, 500, 1000):
                try: lot = get(f"{D}/trades?market={cid}&limit=500&offset={off}&takerOnly=false")
                except Exception: break
                for t in lot:
                    w = t.get("proxyWallet"); vus.add(w); vol[w] += float(t["size"]) * float(t["price"])
                if len(lot) < 500: break
            for w in vus: compte[w] += 1
    top = sorted(compte, key=lambda w: (-compte[w], -vol[w]))[:12]
    return [(w, f"actif : {compte[w]} marches / {2 * n_cycles}, {vol[w]:.0f} $") for w in top if w]


# ---------- 3. autopsie d'un portefeuille
def activite(w, maxi=4000):
    ev = []
    for off in range(0, maxi, 500):
        try: lot = get(f"{D}/activity?user={w}&limit=500&offset={off}")
        except Exception: break
        if not lot: break
        ev += lot
        if len(lot) < 500: break
    return ev


def autopsie(w):
    ev = [e for e in activite(w) if "updown" in (e.get("slug") or e.get("eventSlug") or "")]
    if not ev: return None
    M = collections.defaultdict(lambda: {"U": 0.0, "D": 0.0, "cU": 0.0, "cD": 0.0, "ventes": 0.0, "fusion": 0.0, "t": [], "achats": [], "n": 0})
    for e in ev:
        slug = e.get("slug") or e.get("eventSlug"); m = M[slug]; typ = e.get("type"); usd = float(e.get("usdcSize") or 0); sz = float(e.get("size") or 0)
        if typ == "TRADE":
            up = (e.get("outcome") or "").lower() == "up"; m["n"] += 1
            if e.get("side") == "BUY":
                if up: m["U"] += sz; m["cU"] += usd
                else: m["D"] += sz; m["cD"] += usd
                st = debut(slug)
                if st: m["t"].append(int(e["timestamp"]) - st)
                m["achats"].append((float(e.get("price") or 0), up))
            else:
                m["ventes"] += usd
                if up: m["U"] -= sz
                else: m["D"] -= sz
        elif typ == "MERGE":
            m["fusion"] += usd; m["U"] -= sz; m["D"] -= sz
    lignes = []
    for slug, m in M.items():
        if m["n"] == 0: continue
        g = resolution(slug)
        if g is None: continue
        cout = m["cU"] + m["cD"]
        paye = (m["U"] if g.lower() == "up" else m["D"])
        pnl = -cout + m["ventes"] + m["fusion"] + max(paye, 0)
        deux = m["cU"] > 0 and m["cD"] > 0
        # cout moyen par part de chaque cote (sur les achats)
        aU = [p for p, u in m["achats"] if u]; aD = [p for p, u in m["achats"] if not u]
        pmU = statistics.mean(aU) if aU else None; pmD = statistics.mean(aD) if aD else None
        tot = abs(m["U"]) + abs(m["D"])
        lignes.append({"slug": slug, "duree": duree(slug), "cout": cout, "pnl": pnl, "deux": deux,
                       "paire": (pmU + pmD) if (pmU is not None and pmD is not None) else None,
                       "deseq": abs(m["U"] - m["D"]) / tot if tot > 0 else 0, "favori_gagne": (m["U"] > m["D"]) == (g.lower() == "up"),
                       "t0": min(m["t"]) if m["t"] else None, "t1": max(m["t"]) if m["t"] else None, "n": m["n"],
                       "prix_moy": statistics.mean([p for p, _ in m["achats"]]) if m["achats"] else None, "tmin": min(int(e["timestamp"]) for e in ev)})
    return lignes


def taker_part(w, tmin):
    try:
        k = 0
        for off in range(0, 4000, 500):
            lot = get(f"{D}/trades?user={w}&limit=500&offset={off}&takerOnly=true")
            k += sum(1 for t in lot if "updown" in (t.get("slug") or t.get("eventSlug") or "") and int(t["timestamp"]) >= tmin)
            if len(lot) < 500 or int(lot[-1]["timestamp"]) < tmin: break
        return k
    except Exception: return None


def resume(w, etiquette, L):
    if not L: return [f"| {w[:10]}… | {etiquette} | aucun marche Up/Down resolu | | | | | | | | |"]
    par = collections.defaultdict(list)
    for x in L: par[x["duree"]].append(x)
    out = []
    for d, X in sorted(par.items(), key=lambda kv: -len(kv[1])):
        pn = [x["pnl"] for x in X]; co = sum(x["cout"] for x in X)
        deux = [x for x in X if x["deux"]]; pa = [x["paire"] for x in deux if x["paire"]]
        t0 = [x["t0"] for x in X if x["t0"] is not None]
        out.append(f"| {w[:10]}… | {etiquette} | {('%d min' % (d // 60)) if d else '?'} | {len(X)} | {sum(pn):+.0f} $ | {sum(pn) / max(co, 1) * 100:+.1f} % | {100 * sum(1 for p in pn if p > 0) / len(X):.0f} % | "
                   f"{100 * len(deux) / len(X):.0f} % | {statistics.median(pa) if pa else float('nan'):.3f} | {statistics.median([x['deseq'] for x in X]):.2f} | "
                   f"{100 * sum(1 for x in X if x['favori_gagne']) / len(X):.0f} % | {statistics.median(t0) if t0 else float('nan'):.0f} s | {statistics.mean(x['prix_moy'] for x in X if x['prix_moy']):.2f} |")
    return out


def main():
    cibles = list(NOMMES.items())
    for p, et in PSEUDOS.items():
        a = adresse(p); log("pseudo", p, a)
        if a: cibles.append((a, f"{et} ({p})"))
    try: cibles += actifs_recents(int(sys.argv[1]) if len(sys.argv) > 1 else 60)
    except Exception as e: log("actifs", e)
    vus = set(); rap = ["# Autopsie des portefeuilles sur les marches crypto Up/Down (Polymarket)", "",
                        "Gain = resolution officielle (parts gagnantes x 1 $) + ventes + fusions - achats. Paire = prix moyen d'achat Up + prix moyen d'achat Down (marches ou il achete les deux). "
                        "Desequilibre = |Up - Down| / (Up + Down) en fin de marche (0 = paire parfaite, 1 = un seul cote). Favori gagne = le cote ou il avait le plus de parts a gagne. 1er achat = secondes apres le debut du marche.", "",
                        "| Portefeuille | Origine | Marche | Marches | Gain | Gain / mise | Marches gagnants | Achete les 2 cotes | Paire mediane | Desequilibre median | Favori gagne | 1er achat | Prix moyen achete |",
                        "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    detail = []
    for w, et in cibles:
        if not w or w in vus: continue
        vus.add(w)
        try:
            L = autopsie(w); log(w, et, len(L or []))
        except Exception as e:
            log("erreur", w, e); continue
        rap += resume(w, et, L)
        if L:
            k = taker_part(w, L[0]["tmin"])
            detail.append(f"- {w} ({et}) : {sum(x['n'] for x in L)} executions Up/Down lues, dont {k} en taker (le reste en maker)")
        open(OUT + "resultat_portefeuilles.md", "w").write("\n".join(rap + ["", "## Taker / maker", ""] + detail))
    open(OUT + "resultat_portefeuilles.md", "w").write("\n".join(rap + ["", "## Taker / maker", ""] + detail))
    print("\n".join(rap + detail))


if __name__ == "__main__":
    main()
