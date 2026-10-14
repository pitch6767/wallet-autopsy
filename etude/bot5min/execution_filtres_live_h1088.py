# H1088 — Filtres d'exécution en direct (fantômes du bot, BTC 5 min)
# Pour chaque famille de copies (« + carnet », « + ecart serre », …) et chaque stratégie de base :
#   gardés = trades de base présents dans la copie ; écartés = trades de base absents de la copie
#   (même période : depuis le premier trade de la famille, au plus tôt 13.10 21:00 heure suisse).
# Comparaison ROI / P&L par trade, IC 90 % par bootstrap sur les cycles (start), version groupée
# et version « poids égal par stratégie », stabilité par jour suisse. Aucune modification du bot.
import json, os, collections, sys
import numpy as np

RACINE = os.path.dirname(os.path.abspath(__file__)) + "/../../bot95/sauvegarde"
DEBUT = "2026-10-13T19:00:00Z"  # 21:00 heure suisse
FAMILLES = ["+ carnet pression", "+ carnet ecart serre", "+ ecart carnet calme", "+ foule bybit x2",
            "+ foule bybit", "+ carnet", "+ ecart serre", "+ calme", "+ contre foule"]
ORDRE = ["+ carnet", "+ carnet pression", "+ carnet ecart serre", "+ ecart serre", "+ calme",
         "+ contre foule", "+ ecart carnet calme", "+ foule bybit", "+ foule bybit x2"]
B = 3000
rng = np.random.default_rng(1088)


def charger():
    S = {}
    for f in os.listdir(RACINE):
        if not f.endswith(".json"):
            continue
        d = json.load(open(os.path.join(RACINE, f)))
        nom = d.get("nom") or f[:-5]
        if not nom.endswith(" BTC"):
            continue
        t = d.get("trades") or {}
        L = list(t.values()) if isinstance(t, dict) else list(t)
        R = {}
        for x in L:
            if not x.get("heure") or x.get("net") is None:
                continue
            R[(x["heure"], x.get("cote"))] = {"heure": x["heure"], "cote": x.get("cote"), "prix": x.get("prix"),
                                               "parts": x.get("parts"), "net": float(x["net"]), "start": x.get("start")}
        for a in d.get("archive") or []:
            k = (a[0], a[1])
            if a[0] and k not in R and a[3] is not None:
                R[k] = {"heure": a[0], "cote": a[1], "prix": a[2], "parts": None, "net": float(a[3]), "start": None, "archive": True}
        S[nom[:-4]] = R
    return S


def cycle(x):
    if x.get("start"):
        return int(x["start"])
    import datetime
    e = datetime.datetime.fromisoformat(x["heure"].replace("Z", "+00:00")).timestamp()
    return int(e // 300 * 300)


def jour_suisse(h):
    import datetime
    e = datetime.datetime.fromisoformat(h.replace("Z", "+00:00")) + datetime.timedelta(hours=2)
    return e.strftime("%d.%m")


def mise(x, base=None):
    p, q = x.get("prix"), x.get("parts")
    if (q is None or p is None) and base is not None:
        p, q = base.get("prix"), base.get("parts")
    if p is None or q is None:
        return np.nan
    return abs(float(p)) * float(q)


def construire(S):
    """Retourne par famille une liste de lignes (strat, cycle, garde, net, mise, jour)."""
    out = {}
    infos = {}
    for fam in FAMILLES:
        out[fam] = []
    # attribution : nom de copie -> (base, famille) ; tester les suffixes longs d'abord
    paires = []
    for nom in S:
        for fam in FAMILLES:
            if nom.endswith(" " + fam) and nom[:-len(fam) - 1] in S:
                paires.append((nom[:-len(fam) - 1], fam, nom))
                break
    for fam in FAMILLES:
        P = [(b, c) for (b, f, c) in paires if f == fam]
        debut_fam = max(DEBUT, min([x["heure"] for b, c in P for x in S[c].values()] or [DEBUT]))
        orphelins = 0
        for b, c in P:
            base, copie = S[b], S[c]
            for k, x in base.items():
                if x["heure"] < debut_fam:
                    continue
                if k in copie:
                    y = copie[k]
                    out[fam].append((b, cycle(x), 1, y["net"], mise(y, x), jour_suisse(x["heure"]), x.get("prix") or 0))
                else:
                    out[fam].append((b, cycle(x), 0, x["net"], mise(x), jour_suisse(x["heure"]), x.get("prix") or 0))
            orphelins += sum(1 for k, y in copie.items() if y["heure"] >= debut_fam and k not in base)
        infos[fam] = {"debut": debut_fam, "orphelins": orphelins, "n_strat": len(P)}
    return out, infos


def stats(rows):
    rows = [r for r in rows if r[4] == r[4]]
    if not rows:
        return None
    strat = sorted({r[0] for r in rows})
    cyc = sorted({r[1] for r in rows})
    si = {s: i for i, s in enumerate(strat)}
    ci = {c: i for i, c in enumerate(cyc)}
    s_ = np.array([si[r[0]] for r in rows]); c_ = np.array([ci[r[1]] for r in rows])
    g = np.array([r[2] for r in rows]); net = np.array([r[3] for r in rows]); m = np.array([r[4] for r in rows])
    res = {}
    for lab, msk in (("k", g == 1), ("r", g == 0)):
        res["n_" + lab] = int(msk.sum()); res["pnl_" + lab] = float(net[msk].sum())
        res["mise_" + lab] = float(m[msk].sum())
        res["wr_" + lab] = float((net[msk] > 0).mean()) if msk.any() else np.nan
        res["roi_" + lab] = res["pnl_" + lab] / res["mise_" + lab] if res["mise_" + lab] > 0 else np.nan
        res["moy_" + lab] = float(net[msk].mean()) if msk.any() else np.nan
    res["d_roi"] = res["roi_k"] - res["roi_r"]; res["d_moy"] = res["moy_k"] - res["moy_r"]
    # par stratégie
    nS = len(strat)
    def grp(W):  # W : (B, N) poids ; renvoie sommes par (strat, gardé)
        o = {}
        for lab, gv in (("k", 1), ("r", 0)):
            msk = g == gv
            M = np.zeros((msk.sum(), nS)); M[np.arange(msk.sum()), s_[msk]] = 1
            o["n" + lab] = W[:, msk] @ M
            o["p" + lab] = (W[:, msk] * net[msk]) @ M
            o["m" + lab] = (W[:, msk] * m[msk]) @ M
        return o
    o1 = grp(np.ones((1, len(rows))))
    ok = (o1["nk"][0] >= 5) & (o1["nr"][0] >= 5)
    roik = o1["pk"][0] / np.where(o1["mk"][0] > 0, o1["mk"][0], np.nan)
    roir = o1["pr"][0] / np.where(o1["mr"][0] > 0, o1["mr"][0], np.nan)
    res["strat_ok"] = int(ok.sum()); res["strat_mieux"] = int(((roik > roir) & ok).sum())
    res["eq_d_roi"] = float(np.nanmean((roik - roir)[ok])) if ok.any() else np.nan
    res["par_strat"] = {strat[i]: (int(o1["nk"][0][i]), float(o1["pk"][0][i]), roik[i], int(o1["nr"][0][i]), float(o1["pr"][0][i]), roir[i]) for i in range(nS)}
    # bootstrap par cycles
    W = rng.multinomial(len(cyc), np.ones(len(cyc)) / len(cyc), size=B).astype(float)[:, c_]
    wk, wr = W * (g == 1), W * (g == 0)
    with np.errstate(invalid="ignore", divide="ignore"), __import__("warnings").catch_warnings():
        __import__("warnings").simplefilter("ignore")
        broi = (wk @ net) / (wk @ m) - (wr @ net) / (wr @ m)
        bmoy = (wk @ net) / wk.sum(1) - (wr @ net) / wr.sum(1)
        o = grp(W)
        dk = o["pk"] / o["mk"] - o["pr"] / o["mr"]
        beq = np.nanmean(np.where(ok[None, :], dk, np.nan), axis=1)
    def q(a):
        a = a[np.isfinite(a)]
        return (float(np.percentile(a, 5)), float(np.percentile(a, 95))) if len(a) else (float("nan"), float("nan"))
    res["ic_d_roi"] = q(broi); res["ic_d_moy"] = q(bmoy); res["ic_eq"] = q(beq)
    res["n_cycles"] = len(cyc)
    return res


def main():
    S = charger()
    data, infos = construire(S)
    R = {}
    for fam in ORDRE:
        rows = data[fam]
        R[fam] = {"tout": stats(rows), "jours": {}}
        # robustesse : sans les billets (prix d'achat < 0,10), qui font l'essentiel des gros gains
        R[fam]["jours"]["sans billets"] = stats([r for r in rows if r[6] >= 0.10])
        nk = sorted([r[3] for r in rows if r[2] == 1], reverse=True)
        R[fam]["tout"]["part_top10_k"] = sum(nk[:10]) / sum(nk) if sum(nk) else float("nan")
        for j in sorted({r[5] for r in rows}):
            R[fam]["jours"][j] = stats([r for r in rows if r[5] == j])
    # paires (stratégie, famille) n gardés >= 30
    paires = []
    for fam in ORDRE:
        st = R[fam]["tout"]
        for s, (nk, pk, rk, nr, pr, rr) in st["par_strat"].items():
            if nk >= 30:
                paires.append((pk, s, fam, nk, rk, pk + pr, nk + nr, rr))
    paires.sort(reverse=True)
    sans = sorted(n for n in S if "sans 02-10h" in n)
    sans_n = {n: (len(S[n]), round(sum(x["net"] for x in S[n].values()), 2)) for n in sans}
    json.dump({"infos": infos, "R": {f: {"tout": {k: v for k, v in R[f]["tout"].items() if k != "par_strat"},
                                             "jours": {j: ({k: v for k, v in s.items() if k != "par_strat"} if s else None) for j, s in R[f]["jours"].items()}} for f in R},
               "top": paires[:10], "sans": sans_n}, open(sys.argv[1] if len(sys.argv) > 1 else "/dev/stdout", "w"), indent=1, default=float)


if __name__ == "__main__":
    main()
