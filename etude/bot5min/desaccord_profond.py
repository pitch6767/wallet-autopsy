"""Desaccords : recherche a fond sur les VRAIS carnets Polymarket enregistres par le bot (4 mesures/s, 48 h) — 07.10.2026.
Question de Pitch : peut-on voir que ca tourne mal (sortir, inverser, couvrir) ou n'entrer que sur un retournement / une confirmation ?
Chaque desaccord (modele - meilleur vendeur >= E) est rejoue avec des centaines de regles d'entree x gestion :
  entree  : tout de suite / apres d s si le marche confirme (+c) / apres un rebond (creux puis +r) / seulement si le perp va dans notre sens
  gestion : garder / sortir si le prix tombe de s / inverser si le prix tombe de s / couvrir (acheter l'autre cote) si le prix tombe de s
Achat au meilleur vendeur, vente au meilleur acheteur, frais taker, resultat officiel. Choix des regles sur la 1re moitie, verification sur la 2e.
"""
import json, sys, time, math, statistics, collections, urllib.request, itertools

U = "https://bot95.pitch67.workers.dev"
OUT = "etude/bot5min/"
FEE = lambda p: 0.072 * p * (1 - p)


def get(url):
    err = None
    for k in range(6):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "analyse"}), timeout=90) as r: return json.loads(r.read())
        except Exception as e: err = e; time.sleep(3)
    raise err


def log(*a): print(*a, flush=True)


def charger(a):
    L, apres = [], None
    while True:
        d = get(f"{U}/api/rec?a={a}&n=60" + (f"&apres={apres}" if apres else ""))
        for doc in d["docs"]: L += doc["lignes"]
        if not d["cles"] or len(d["cles"]) < 60: break
        apres = d["suivant"]
    L.sort(key=lambda r: r[0])
    return L


RES = {}
def resultat(a, st):
    k = (a, st)
    if k in RES: return RES[k]
    r = None
    try:
        ev = get(f"https://gamma-api.polymarket.com/events?slug={a.lower()}-updown-5m-{st}")
        m = ev[0]["markets"][0]; px = [float(x) for x in json.loads(m["outcomePrices"])]; outs = json.loads(m["outcomes"])
        if sorted(px) == [0.0, 1.0]: r = outs[px.index(1.0)].lower() == "up"
    except Exception: pass
    RES[k] = r
    return r


# colonnes rec : t start pu ub ua db da ubs uas dbs das perp okx cb bn cl strike
def cycles(L):
    C = collections.defaultdict(list)
    for r in L:
        if r[2] is None or r[3] is None or r[4] is None or r[5] is None or r[6] is None: continue
        if C[r[1]] and r[0] - C[r[1]][-1][0] < 1: continue          # 1 mesure par seconde suffit
        C[r[1]].append(r)
    return C


def cote(r, up):
    """(bid, ask, valeur modele) du cote choisi"""
    return (r[3], r[4], r[2]) if up else (r[5], r[6], 1 - r[2])


def evenements(C, E):
    ev = []
    for st, R in C.items():
        for up in (True, False):
            for i, r in enumerate(R):
                tl = st + 300 - r[0]
                if tl < 8: break
                b, a, f = cote(r, up)
                if 0.03 <= a <= 0.97 and f - a >= E:
                    ev.append((st, up, i)); break
    return ev


def jouer(R, up, i0, gagne, regle):
    """rejoue un desaccord detecte a l'indice i0 ; renvoie le gain par part (ou None si pas d'entree)"""
    entree, d, c, r_, perp, gest, s = regle
    st = R[0][1]
    # ---- entree
    ie = None
    if entree == "direct":
        ie = i0
    elif entree == "attente":           # apres d s : le marche doit avoir bouge de +c vers nous, et le modele garder un avantage
        b0, a0, f0 = cote(R[i0], up)
        for j in range(i0, len(R)):
            if R[j][0] - R[i0][0] >= d:
                b, a, f = cote(R[j], up)
                if (b + a) / 2 - (b0 + a0) / 2 >= c and f - a >= 0.03 and st + 300 - R[j][0] >= 5: ie = j
                break
    elif entree == "rebond":            # le prix de notre cote fait un creux puis remonte de r_ (dans les 60 s), avantage toujours la
        creux = 9;
        for j in range(i0, len(R)):
            if R[j][0] - R[i0][0] > 60 or st + 300 - R[j][0] < 5: break
            b, a, f = cote(R[j], up); m = (b + a) / 2
            creux = min(creux, m)
            if m - creux >= r_ and f - a >= 0.03: ie = j; break
    if ie is None: return None
    if perp:
        j5 = next((j for j in range(ie, -1, -1) if R[ie][0] - R[j][0] >= 5), None)
        if j5 is None or R[ie][11] is None or R[j5][11] is None: return None
        if (R[ie][11] - R[j5][11]) * (1 if up else -1) < 0: return None
    b, a, f = cote(R[ie], up)
    px = a; cash = -(a + FEE(a)); pos_main = 1.0; pos_autre = 0.0
    # ---- gestion
    if gest != "garder":
        for j in range(ie + 1, len(R)):
            if st + 300 - R[j][0] < 2: break
            b2, a2, _ = cote(R[j], up)
            if px - b2 >= s:
                if gest in ("sortir", "inverser"):
                    cash += b2 - FEE(b2); pos_main = 0.0
                if gest == "inverser" or gest == "couvrir":
                    ob, oa, _ = cote(R[j], not up)
                    cash -= oa + FEE(oa); pos_autre = 1.0
                break
    if gagne is None: return None
    win_main = gagne if up else (not gagne)
    return cash + pos_main * (1 if win_main else 0) + pos_autre * (0 if win_main else 1)


def main():
    data = {a: cycles(charger(a)) for a in ("BTC", "ETH")}
    for a in data: log(a, len(data[a]), "cycles")
    regles = []
    for entree in ("direct", "attente", "rebond"):
        for d, c, r_ in ([(0, 0, 0)] if entree == "direct" else ([(d, c, 0) for d in (2, 5, 10, 20) for c in (0.0, 0.01, 0.03)] if entree == "attente" else [(0, 0, r) for r in (0.02, 0.04, 0.06)])):
            for perp in (False, True):
                for gest, s in [("garder", 0)] + [(g, s) for g in ("sortir", "inverser", "couvrir") for s in (0.05, 0.10, 0.15)]:
                    regles.append((entree, d, c, r_, perp, gest, s))
    log(len(regles), "regles")
    rap = ["# Desaccords — recherche a fond sur les vrais carnets (enregistreur du bot)", "",
           "Entree : direct = tout de suite ; attente d/c = apres d s si le marche a bouge de +c vers nous ; rebond r = creux puis remontee de r. perp = seulement si le perp va dans notre sens (5 s).",
           "Gestion : garder ; sortir / inverser / couvrir si le meilleur acheteur tombe de s sous le prix d'entree. Gain par part (1 part), frais compris, resultat officiel.", ""]
    for a, C in data.items():
        sts = sorted(C); mi = sts[len(sts) // 2] if sts else 0
        for st in sts: resultat(a, st)
        for E in (0.10, 0.15, 0.20):
            EV = evenements(C, E)
            if len(EV) < 20: continue
            res = []
            for rg in regles:
                A, B = [], []
                for (st, up, i0) in EV:
                    g = jouer(C[st], up, i0, RES.get((a, st)), rg)
                    if g is None: continue
                    (A if st < mi else B).append(g)
                if len(A) >= 15 and len(B) >= 10:
                    res.append((statistics.mean(A), len(A), statistics.mean(B), len(B), sum(B), rg))
            if not res: continue
            res.sort(key=lambda x: -x[0])
            base = next((x for x in res if x[5][0] == "direct" and not x[5][4] and x[5][5] == "garder"), None)
            nom = lambda rg: f"{rg[0]}{' ' + str(rg[1]) + ' s +' + str(rg[2]) if rg[0] == 'attente' else (' ' + str(rg[3]) if rg[0] == 'rebond' else '')}{' + perp' if rg[4] else ''} · {rg[5]}{' ' + str(rg[6]) if rg[5] != 'garder' else ''}"
            rap += [f"## {a} — ecart >= {E:.2f} — {len(EV)} desaccords ({time.strftime('%d.%m %H:%M', time.gmtime(sts[0]))} -> {time.strftime('%d.%m %H:%M', time.gmtime(sts[-1] + 300))} UTC)", ""]
            if base: rap.append(f"Reference (tout de suite, garder) : 1re moitie {base[0]:+.3f} $/part ({base[1]}), **2e moitie {base[2]:+.3f} $/part ({base[3]})**")
            rap += ["", "| Regle (classee sur la 1re moitie) | 1re moitie : gain/part (trades) | **2e moitie : gain/part (trades)** | 2e moitie total (1 part) |", "|---|---|---|---|"]
            for x in res[:12]:
                rap.append(f"| {nom(x[5])} | {x[0]:+.3f} ({x[1]}) | **{x[2]:+.3f}** ({x[3]}) | {x[4]:+.2f} |")
            ok = [x for x in res[:20] if x[2] > 0]
            rap += ["", f"Parmi les 20 meilleures de la 1re moitie : **{len(ok)}** restent positives sur la 2e moitie.", ""]
            # meilleure gestion par type (moyenne sur les entrees)
            par = collections.defaultdict(list)
            for x in res: par[x[5][5] + (" " + str(x[5][6]) if x[5][5] != "garder" else "")].append(x[2])
            rap += ["Gestion seule (moyenne de toutes les entrees, 2e moitie) : " + " · ".join(f"{k} {statistics.mean(v):+.3f}" for k, v in sorted(par.items(), key=lambda kv: -statistics.mean(kv[1]))), ""]
            open(OUT + "resultat_desaccord_profond.md", "w").write("\n".join(rap))
    open(OUT + "resultat_desaccord_profond.md", "w").write("\n".join(rap))
    print("\n".join(rap))


if __name__ == "__main__":
    main()
