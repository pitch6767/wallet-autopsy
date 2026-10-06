"""Teneur de marche (idee 29) avec protections contre les jambes seules — BTC et ETH, 12 jours.
Offres d'achat Up et Down a (valeur du modele - marge), recalculees avec la proba d'il y a 1 s. Remplissage prudent :
un vendeur reel doit passer 1 cent SOUS notre offre. Protections testees seules puis combinees :
  retrait  : pas d'offre si le prix spot a bouge de plus de X pb dans la derniere seconde connue
  completer: des qu'une jambe est seule, acheter l'autre cote au prix du marche (dernier prix + 1 cent, frais) si la paire coute <= 1 - c
  pencher  : l'offre du cote deja achete est retiree, celle de l'autre cote remontee de s
  petit    : 10 parts max par remplissage, ecart max 10 parts
  equilibre: offres seulement si le modele donne Up entre 35 et 65 %
  sortie   : jambe seule depuis plus de T s -> revendue (dernier prix - 1 cent, frais)
"""
import sys, math, time, statistics
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
sys.path.insert(0, "etude/bot5min")
import test as T
import paires as P
import solutions as S
from sorties import spot_jour, charger, dernier

JOURS = int(sys.argv[1]) if len(sys.argv) > 1 else 12
L = 1
FEE = lambda p: T.FEE_RATE * p * (1 - p)
OUT = "etude/bot5min/"


def etudier(prefixe, sym, jours, debut, fin, coupe):
    t0 = time.time()
    SP = charger(spot_jour, sym, jours)
    SPx = {s: (v[0], v[0]) for s, v in SP.items()}
    with ThreadPoolExecutor(12) as ex:
        M = sorted([m for m in ex.map(lambda st: S.marche(prefixe, st), range(debut, fin, 300)) if m], key=lambda m: m["start"])
    def tr(m):
        try: m["tr"], _ = P.echanges(m)
        except Exception: m["tr"] = []
        return m
    with ThreadPoolExecutor(10) as ex:
        M = [m for m in ex.map(tr, M) if m["tr"] and m.get("strike") is not None]
    print(prefixe, "marches", len(M), "(%.0fs)" % (time.time() - t0)); sys.stdout.flush()
    prix = lambda t: dernier(SP, t, 0)
    hist, derives = [], []
    for m in M:
        kp = float(m["strike"]); fo = float(m["final"]) if m.get("final") is not None else None
        tb = S.twap(SPx, m["start"] - 59, m["start"]); tf = S.twap(SPx, m["end"] - 59, m["end"])
        m["base"] = statistics.median(hist[-12:]) if len(hist) >= 3 else 0
        if tb: hist.append(tb - kp)
        m["K"] = kp + m["base"]
        m["sd_b"] = statistics.pstdev(derives[-50:]) if len(derives) >= 10 else None
        if tf and tb and fo: derives.append((tf - tb) - (fo - kp))

    def proba_up(m, ts):
        cache = m.setdefault("cache", {})
        if ts in cache: return cache[ts]
        r = None; P0 = prix(ts); sgk = ("sg", ts // 15)
        if sgk not in cache: cache[sgk] = T.sigma_s(SPx, ts)
        sg = cache[sgk]
        if P0 and sg and m["sd_b"]:
            a = m["end"] - 59
            if ts >= a:
                connus = [x for x in (prix(s) for s in range(a, ts + 1)) if x]
                nr = m["end"] - ts
                E = (sum(connus) + nr * P0) / (len(connus) + nr); var = (sg * P0) ** 2 * nr ** 3 / 3 / 3600
            else:
                E = P0; var = (sg * P0) ** 2 * ((a - ts) + 20)
            r = T.phi((E - m["K"]) / math.sqrt(var + m["sd_b"] ** 2))
        cache[ts] = r
        return r

    def mm(m, v):
        marge = v.get("marge", 0.12); deseq = v.get("deseq", 50); maxi = v.get("maxi", 100); paquet = v.get("paquet", 1e9)
        inv = {True: 0.0, False: 0.0}; cash = 0.0
        last = {True: None, False: None}; vu = {True: -99, False: -99}     # dernier prix connu de chaque jeton (Up=True)
        seul_depuis = None; dernier_cote = None; comp_attente = None; sortie_attente = None
        n_comp = n_sort = 0
        for (ts, up, p, size, side) in m["tr"]:
            if ts > m["end"] - 1: break
            # prix courant des deux jetons a partir des echanges
            last[up] = p; vu[up] = ts; last[not up] = 1 - p; vu[not up] = ts
            if ts < m["start"]: continue
            ecart = inv[True] - inv[False]
            seul = abs(ecart) > 1e-6
            # --- executions differees (decidees a ts - L, executees au premier echange >= decision + L)
            if comp_attente is not None and ts >= comp_attente and seul:
                X = ecart < 0                                    # cote qui manque (True = Up)
                ask = last[X] + 0.01
                k = abs(ecart)
                cout_seul = cout_moy[not X] if inv[not X] > 0 else 0.5
                if ask < 0.99 and cout_seul + ask + FEE(ask) <= 1 - v["completer"]:
                    inv[X] += k; cash -= k * (ask + FEE(ask)); n_comp += 1
                comp_attente = None
            if sortie_attente is not None and ts >= sortie_attente and seul:
                X = ecart > 0                                    # cote en trop
                bid = max(0.01, last[X] - 0.01); k = abs(ecart)
                inv[X] -= k; cash += k * (bid - FEE(bid)); n_sort += 1
                sortie_attente = None; seul_depuis = None
            ecart = inv[True] - inv[False]; seul = abs(ecart) > 1e-6
            if not seul: seul_depuis = None
            elif seul_depuis is None: seul_depuis = ts
            if "sortie_s" in v and seul and seul_depuis is not None and ts - seul_depuis >= v["sortie_s"] and sortie_attente is None:
                sortie_attente = ts + L
            # --- nos offres (proba d'il y a 1 s)
            if ts > m["end"] - 10: continue
            pu = proba_up(m, ts - L)
            if pu is None: continue
            if "equilibre" in v and not (v["equilibre"][0] <= pu <= v["equilibre"][1]): continue
            if "retrait_pb" in v:
                a_, b_ = prix(ts - L - 1), prix(ts - L)
                if a_ and b_ and abs(b_ / a_ - 1) * 1e4 > v["retrait_pb"]: continue
            bids = {True: math.floor((pu - marge) * 100) / 100, False: math.floor((1 - pu - marge) * 100) / 100}
            if "pencher" in v and seul:
                trop = ecart > 0
                bids[trop] = -1                                     # plus d'offre du cote deja achete
                bids[not trop] = round(bids[not trop] + v["pencher"], 2)
            # le vendeur de ce trade vend le jeton X au prix px
            if side == "SELL": X, px = up, p
            else: X, px = (not up), 1 - p
            b = bids[X]
            if b < 0.02 or px > b - 0.01 + 1e-9: continue
            k = min(size, paquet, maxi - inv[X], deseq - (inv[X] - inv[not X]))
            if k <= 0: continue
            inv[X] += k; cash -= k * b
            m.setdefault("_c", {True: [0.0, 0.0], False: [0.0, 0.0]})
            m["_c"][X][0] += k; m["_c"][X][1] += k * b
            cout_moy = {c: (m["_c"][c][1] / m["_c"][c][0] if m["_c"][c][0] > 0 else 0.5) for c in (True, False)}
            if "completer" in v and abs(inv[True] - inv[False]) > 1e-6 and comp_attente is None:
                comp_attente = ts + L
        m.pop("_c", None)
        if inv[True] + inv[False] < 1e-9 and cash == 0: return None
        g = m["up_gagne"]
        pnl = cash + inv[True] * (1 if g else 0) + inv[False] * (0 if g else 1)
        return (m["start"], pnl, min(inv[True], inv[False]), abs(inv[True] - inv[False]), n_comp, n_sort)

    jours_a = (coupe - debut) / 86400; jours_b = (fin - coupe) / 86400
    C = {"completer": 0.01}
    variantes = [
        ("Actuel (marge 0,12, ecart 50)", {}),
        ("Retrait si le prix bouge > 2 pb en 1 s", {"retrait_pb": 2}),
        ("Retrait si > 4 pb en 1 s", {"retrait_pb": 4}),
        ("Completer la paire au marche si elle coute <= 0,99", {"completer": 0.01}),
        ("Completer si <= 0,97", {"completer": 0.03}),
        ("Pencher : retirer le cote achete, remonter l'autre de 4 cents", {"pencher": 0.04}),
        ("Pencher de 8 cents", {"pencher": 0.08}),
        ("Petit : 10 parts par remplissage, ecart max 10", {"paquet": 10, "deseq": 10}),
        ("Equilibre : offres seulement si Up entre 35 et 65 %", {"equilibre": (0.35, 0.65)}),
        ("Revendre la jambe seule apres 20 s", {"sortie_s": 20}),
        ("Revendre apres 40 s", {"sortie_s": 40}),
        ("Combo : retrait 2 pb + completer 0,99", {"retrait_pb": 2, "completer": 0.01}),
        ("Combo : retrait + pencher 4 + petit", {"retrait_pb": 2, "pencher": 0.04, "paquet": 10, "deseq": 10}),
        ("Combo : retrait + completer + pencher + petit", {"retrait_pb": 2, "completer": 0.01, "pencher": 0.04, "paquet": 10, "deseq": 10}),
        ("Combo : tout + equilibre", {"retrait_pb": 2, "completer": 0.01, "pencher": 0.04, "paquet": 10, "deseq": 10, "equilibre": (0.35, 0.65)}),
        ("Combo : tout + equilibre + sortie 20 s", {"retrait_pb": 2, "completer": 0.01, "pencher": 0.04, "paquet": 10, "deseq": 10, "equilibre": (0.35, 0.65), "sortie_s": 20}),
        ("Combo tout, marge 0,08", {"marge": 0.08, "retrait_pb": 2, "completer": 0.01, "pencher": 0.04, "paquet": 10, "deseq": 10, "equilibre": (0.35, 0.65)}),
        ("Combo tout, marge 0,05", {"marge": 0.05, "retrait_pb": 2, "completer": 0.01, "pencher": 0.04, "paquet": 10, "deseq": 10, "equilibre": (0.35, 0.65)}),
        ("Combo tout, petit 25 parts", {"retrait_pb": 2, "completer": 0.01, "pencher": 0.04, "paquet": 25, "deseq": 25, "equilibre": (0.35, 0.65)}),
    ]
    rap = [f"\n## {prefixe.upper()} — {len(M)} cycles\n",
           "| Protection | Cycles servis | Cycles perdants | Gain net | Gain/jour | Pertes | Pire cycle | Pire baisse | Paires moy. | Parts seules moy. | Gain/jour jours 1-8 | **Gain/jour jours 9-12** |",
           "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for nom, v in variantes:
        R = [x for x in (mm(m, v) for m in M) if x]
        if not R:
            rap.append(f"| {nom} | 0 | | | | | | | | | | |"); continue
        R.sort()
        cum = pic = dd = 0
        for x in R:
            cum += x[1]; pic = max(pic, cum); dd = max(dd, pic - cum)
        net = sum(x[1] for x in R)
        rap.append(f"| {nom} | {len(R)} | {sum(1 for x in R if x[1] < 0)} ({100 * sum(1 for x in R if x[1] < 0) / len(R):.0f} %) | {net:+.0f} $ | {net / JOURS:+.0f} $ | {sum(x[1] for x in R if x[1] < 0):+.0f} $ | {min(x[1] for x in R):+.0f} $ | -{dd:.0f} $ | {statistics.mean(x[2] for x in R):.0f} | {statistics.mean(x[3] for x in R):.1f} | {sum(x[1] for x in R if x[0] < coupe) / jours_a:+.0f} $ | **{sum(x[1] for x in R if x[0] >= coupe) / jours_b:+.0f} $** |")
        print(rap[-1]); sys.stdout.flush()
    return rap


def main():
    t0 = time.time()
    fin = int(time.time()) // 86400 * 86400 - 300
    debut = fin + 300 - JOURS * 86400
    jours = sorted({datetime.fromtimestamp(t, timezone.utc).strftime("%Y-%m-%d") for t in range(debut - 3700, fin + 600, 3600)})
    jours = [j for j in jours if j < datetime.now(timezone.utc).strftime("%Y-%m-%d")]
    coupe = debut + int(JOURS * 2 / 3) * 86400
    rap = [f"# Teneur de marche : protections contre les jambes seules — {JOURS} jours ({jours[1]} -> {jours[-1]})",
           "Offres jusqu'a 100 parts par cote et par cycle, gardees jusqu'a la fin. Retard 1 s. Remplissage prudent (vendeur 1 cent sous notre offre)."]
    for prefixe, sym in (("btc", "BTCUSDT"), ("eth", "ETHUSDT")):
        rap += etudier(prefixe, sym, jours, debut, fin, coupe)
        open(OUT + "resultat_mm2.md", "w").write("\n".join(rap))
    rap.append(f"\nDuree : {time.time() - t0:.0f} s")
    open(OUT + "resultat_mm2.md", "w").write("\n".join(rap))
    print("\n".join(rap))


if __name__ == "__main__":
    main()
