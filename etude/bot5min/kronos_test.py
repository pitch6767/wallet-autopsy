"""Test de Kronos (modele IA open source de prevision de bougies) sur les marches 5 min Polymarket — BTC et ETH, 12 jours.
1. A l'ouverture du cycle (et a 2 min), Kronos-small recoit les 240 dernieres bougies 1 min Binance et dessine K chemins pour la suite.
   P_kronos(Up) = part des chemins ou la moyenne de la derniere minute depasse la moyenne de la minute avant l'ouverture.
2. Comparaison au vrai resultat Polymarket, a des reperes simples et a NOTRE modele au meme instant.
3. Apport reel : regression logistique (resultat ~ notre proba + Kronos) apprise jours 1-8, jugee jours 9-12.
4. Filtre sur V1 : on garde/refuse les trades V1 selon l'avis de Kronos.
Usage : python kronos_test.py JOURS [essai]
"""
import sys, io, os, math, time, zipfile, statistics
import numpy as np
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
sys.path.insert(0, "etude/bot5min")
import test as T
import paires as P
import solutions as S
from sorties import spot_jour, charger, dernier

JOURS = int(sys.argv[1]) if len(sys.argv) > 1 else 12
ESSAI = len(sys.argv) > 2 and sys.argv[2] == "essai"
K = 8            # chemins par prevision
LOOK = 240       # bougies d'historique
L = 1
N = 100.0
FEE = lambda p: T.FEE_RATE * p * (1 - p)
OUT = "etude/bot5min/"
LIMITE_S = 4.6 * 3600

sys.path.insert(0, "/tmp/Kronos")
import torch
from model import Kronos, KronosTokenizer, KronosPredictor
torch.set_num_threads(os.cpu_count() or 2)
TOK = KronosTokenizer.from_pretrained("NeoQuasar/Kronos-Tokenizer-base")
MOD = Kronos.from_pretrained("NeoQuasar/Kronos-small")
PRED = KronosPredictor(MOD, TOK, device="cpu", max_context=512)


def bougies_jour(sym, jour):
    url = f"https://data.binance.vision/data/spot/daily/klines/{sym}/1m/{sym}-1m-{jour}.zip"
    z = zipfile.ZipFile(io.BytesIO(T.get(url, raw=True)))
    out = {}
    for ligne in z.read(z.namelist()[0]).decode().splitlines():
        c = ligne.split(",")
        if not c[0].isdigit(): continue
        t = int(c[0]); t = t // 1000 if t > 1e14 else t
        out[t // 1000] = (float(c[1]), float(c[2]), float(c[3]), float(c[4]), float(c[5]), float(c[7]))
    return out


def kronos_proba(BG, ancres, n_pred):
    """ancres : liste de (t_ancre, prix_reference). Renvoie la liste des P(Up) (part des chemins au-dessus)."""
    dfs, xs, ys, refs = [], [], [], []
    for (ta, ref) in ancres:
        ts = list(range(ta - LOOK * 60, ta, 60))
        rows = [BG.get(t) for t in ts]
        if any(r is None for r in rows):
            dfs.append(None); continue
        df = pd.DataFrame(rows, columns=["open", "high", "low", "close", "volume", "amount"])
        x = pd.Series(pd.to_datetime(ts, unit="s")); y = pd.Series(pd.to_datetime(list(range(ta, ta + n_pred * 60, 60)), unit="s"))
        for _ in range(K):
            dfs.append(df); xs.append(x); ys.append(y)
        refs.append(ref)
    ok = [d is not None for d in dfs]
    reels = [d for d in dfs if d is not None]
    res = []
    if reels:
        out = []
        for i in range(0, len(reels), 64):
            out += PRED.predict_batch(df_list=reels[i:i + 64], x_timestamp_list=xs[i:i + 64], y_timestamp_list=ys[i:i + 64],
                                      pred_len=n_pred, T=1.0, top_p=0.9, sample_count=1, verbose=False)
        j = 0
        for ri, ref in enumerate(refs):
            chemins = out[j:j + K]; j += K
            fin = [float((c.iloc[-1]["open"] + c.iloc[-1]["high"] + c.iloc[-1]["low"] + c.iloc[-1]["close"]) / 4) for c in chemins]
            res.append((sum(1 for f in fin if f > ref) / K, statistics.mean(fin) / ref - 1))
    # remettre dans l'ordre des ancres (None si historique incomplet)
    final, it = [], iter(res)
    k = 0
    for (ta, ref) in ancres:
        if dfs[k] is None: final.append(None); k += 1
        else: final.append(next(it)); k += K
    return final


def etudier(prefixe, sym, jours, debut, fin, coupe, t_dep):
    t0 = time.time()
    BG = charger(bougies_jour, sym, jours)
    SP = charger(spot_jour, sym, jours)
    SPx = {s: (v[0], v[0]) for s, v in SP.items()}
    with ThreadPoolExecutor(12) as ex:
        M = sorted([m for m in ex.map(lambda st: S.marche(prefixe, st), range(debut, fin, 300)) if m], key=lambda m: m["start"])
    def tr(m):
        try: m["tr"], _ = P.echanges(m)
        except Exception: m["tr"] = []
        return m
    with ThreadPoolExecutor(10) as ex:
        M = [m for m in ex.map(tr, M) if m.get("strike") is not None]
    if ESSAI: M = M[-30:]
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

    # ---------- predictions Kronos (ouverture et +2 min), par paquets, avec limite de temps
    for m in M:
        c0 = BG.get(m["start"] - 60)
        m["ref"] = (c0[0] + c0[1] + c0[2] + c0[3]) / 4 if c0 else None   # moyenne de la minute avant l'ouverture (= prix a battre, en prix Binance)
    paquet = 40
    for i in range(0, len(M), paquet):
        if time.time() - t_dep > LIMITE_S * (1.0 if prefixe == "eth" else 0.5): print("limite de temps atteinte", prefixe, i); break
        G = [m for m in M[i:i + paquet] if m["ref"]]
        r0 = kronos_proba(BG, [(m["start"], m["ref"]) for m in G], 5)
        r2 = kronos_proba(BG, [(m["start"] + 120, m["ref"]) for m in G], 3)
        for m, a, b in zip(G, r0, r2):
            m["k0"], m["k2"] = a, b
        if i % 400 == 0: print(prefixe, "kronos", i, "/", len(M), "(%.0fs)" % (time.time() - t0)); sys.stdout.flush()
    E = [m for m in M if m.get("k0") and m.get("k2")]
    for m in E:
        m["p0"] = proba_up(m, m["start"] - L); m["p2"] = proba_up(m, m["start"] + 120 - L)
        a, b = prix(m["start"] - 300), prix(m["start"] - 1)
        m["mom"] = (b > a) if a and b else None
        a, b = prix(m["start"] + 60), prix(m["start"] + 119)
        m["mom2"] = (b > a) if a and b else None

    rap = [f"\n## {prefixe.upper()} — {len(E)} cycles avec prevision Kronos (sur {len(M)})\n"]
    if not E: return rap
    # ---------- 1. justesse de la direction
    def juste(L_, f):
        v = [(f(m), m["up_gagne"]) for m in L_ if f(m) is not None]
        v = [(p, g) for p, g in v if p != 0.5]
        return (sum(1 for p, g in v if (p > 0.5) == g) / len(v), len(v)) if v else (float("nan"), 0)
    rap += ["### 1. Direction annoncee contre vrai resultat Polymarket\n", "| Qui predit | Moment | Bonne direction | Cycles |", "|---|---|---|---|"]
    for nom, mom, f in [("Kronos", "ouverture", lambda m: m["k0"][0]), ("Kronos", "+2 min", lambda m: m["k2"][0]),
                        ("Elan des 5 dernieres minutes", "ouverture", lambda m: None if m["mom"] is None else float(m["mom"])),
                        ("Elan de la minute 1-2", "+2 min", lambda m: None if m["mom2"] is None else float(m["mom2"])),
                        ("Notre modele", "ouverture", lambda m: m["p0"]), ("Notre modele", "+2 min", lambda m: m["p2"])]:
        j, n = juste(E, f)
        rap.append(f"| {nom} | {mom} | {100 * j:.1f} % | {n} |")
    rap += ["\n### Kronos quand il est sur de lui (ouverture)\n", "| Kronos dit | Cycles | Bonne direction |", "|---|---|---|"]
    for lo, hi in ((0.0, 0.125), (0.125, 0.375), (0.375, 0.625), (0.625, 0.875), (0.875, 1.01)):
        G = [m for m in E if lo <= m["k0"][0] < hi]
        if G:
            ok = sum(1 for m in G if (m["k0"][0] > 0.5) == m["up_gagne"]) if not (lo >= 0.375 and hi <= 0.625) else sum(1 for m in G if m["up_gagne"])
            rap.append(f"| P(Up) {lo:.2f}-{min(hi, 1):.2f} | {len(G)} | {100 * ok / len(G):.1f} %{' (part de Up)' if lo >= 0.375 and hi <= 0.625 else ''} |")
    # ---------- 2. apport au-dela de notre modele (logistique, jours 1-8 -> 9-12)
    from sklearn.linear_model import LogisticRegression
    def X(m, k):
        p = min(max(m["p" + k] or 0.5, 1e-4), 1 - 1e-4); kk = "k" + k
        return [math.log(p / (1 - p)), m[kk][0] - 0.5, m[kk][1] * 1e4]
    A_ = [m for m in E if m["start"] < coupe and m["p0"] and m["p2"]]; B_ = [m for m in E if m["start"] >= coupe and m["p0"] and m["p2"]]
    rap += ["\n### 2. Kronos apporte-t-il quelque chose en plus de notre modele ? (appris jours 1-8, juge jours 9-12)\n",
            "| Moment | Erreur notre modele seul | Erreur notre modele + Kronos | Bonne direction seul | Bonne direction + Kronos |", "|---|---|---|---|---|"]
    if len(A_) > 50 and len(B_) > 20:
        for k in ("0", "2"):
            ya = [m["up_gagne"] for m in A_]; yb = np.array([m["up_gagne"] for m in B_])
            l1 = LogisticRegression().fit([X(m, k)[:1] for m in A_], ya); l2 = LogisticRegression().fit([X(m, k) for m in A_], ya)
            p1 = l1.predict_proba([X(m, k)[:1] for m in B_])[:, 1]; p2 = l2.predict_proba([X(m, k) for m in B_])[:, 1]
            ll = lambda p: -np.mean(yb * np.log(p) + (1 - yb) * np.log(1 - p))
            rap.append(f"| {'ouverture' if k == '0' else '+2 min'} | {ll(p1):.4f} | {ll(p2):.4f} | {100 * np.mean((p1 > 0.5) == yb):.1f} % | {100 * np.mean((p2 > 0.5) == yb):.1f} % |")
    # ---------- 3. filtre sur V1
    def v1(m):
        A = None; invB = [0.0, 0.0]; pnl = 0.0; dern = {True: 0.5, False: 0.5}
        for (ts, up, p, size, side) in m.get("tr", []):
            if ts > m["end"] - 1: break
            if ts < m["start"]: continue
            dern[up] = p; dern[not up] = 1 - p
            pu = proba_up(m, ts - L)
            if pu is None: continue
            if A is None:
                if side == "BUY" and 0.55 <= p <= 0.56:
                    fair = pu if up else 1 - pu
                    if fair >= 0.63:
                        a0, b0 = prix(ts - L - 5), prix(ts - L)
                        if not (a0 and b0 and ((b0 - a0) * (1 if up else -1)) > 0): continue
                        A = {"c": up, "prix": p, "fair0": fair, "ts": ts}; pnl -= N * FEE(p)
                continue
            c = A["c"]; fairA = pu if c else 1 - pu
            if side == "SELL": O, qq = up, p
            elif side == "BUY": O, qq = (not up), 1 - p
            else: O = None
            if O is not None and O != c and invB[0] < N:
                offre = min(math.floor(((1 - fairA) - 0.08) * 100) / 100, 0.43)
                if offre >= 0.02 and qq <= offre - 0.01 + 1e-9:
                    k = min(size, N - invB[0]); invB[0] += k; invB[1] += k * offre
            if invB[0] >= N - 1e-9:
                return (A, pnl + N * (1 - A["prix"]) - invB[1])
            if fairA < A["fair0"] - 0.15:
                pv = max(0.01, dern[c] - 0.01); qa = N - invB[0]
                return (A, pnl + qa * (pv - FEE(pv)) - qa * A["prix"] + invB[0] * (1 - A["prix"]) - invB[1])
            if up == c and p >= 0.90 and invB[0] < 1e-9:
                return (A, pnl + N * (0.90 - FEE(0.90) - A["prix"]))
        if A is None: return None
        g = A["c"] == m["up_gagne"]; qa = N - invB[0]
        return (A, pnl + qa * ((1 if g else 0) - A["prix"]) + invB[0] * (1 - A["prix"]) - invB[1])
    TR = []
    for m in E:
        r = v1(m)
        if r:
            A, pnl = r
            k = m["k2"] if A["ts"] >= m["start"] + 120 else m["k0"]
            TR.append((m["start"], pnl, k[0] if A["c"] else 1 - k[0]))
    jours_a = (coupe - debut) / 86400; jours_b = (fin - coupe) / 86400
    rap += ["\n### 3. Kronos comme filtre de V1 (avis de Kronos sur le cote achete)\n",
            "| Regle | Trades | Gain net | Pertes | Gain/jour jours 1-8 | **Gain/jour jours 9-12** |", "|---|---|---|---|---|---|"]
    for nom, f in [("V1 sans filtre", lambda x: True), ("Refuser si Kronos donne < 50 % a notre cote", lambda x: x[2] >= 0.5),
                   ("Refuser si Kronos donne < 25 % a notre cote", lambda x: x[2] >= 0.25), ("Refuser si Kronos donne < 13 % (presque tous les chemins contre)", lambda x: x[2] >= 0.13),
                   ("Garder seulement si Kronos donne >= 75 %", lambda x: x[2] >= 0.75)]:
        G = [x for x in TR if f(x)]
        if G:
            rap.append(f"| {nom} | {len(G)} | {sum(x[1] for x in G):+.0f} $ | {sum(x[1] for x in G if x[1] < 0):+.0f} $ | {sum(x[1] for x in G if x[0] < coupe) / jours_a:+.0f} $ | **{sum(x[1] for x in G if x[0] >= coupe) / jours_b:+.0f} $** |")
    print("\n".join(rap)); sys.stdout.flush()
    return rap


def main():
    t0 = time.time()
    fin = int(time.time()) // 300 * 300 - 900
    debut = fin - JOURS * 86400
    jours = sorted({datetime.fromtimestamp(t, timezone.utc).strftime("%Y-%m-%d") for t in range(debut - LOOK * 60 - 3700, fin + 600, 3600)})
    jours = [j for j in jours if j < datetime.now(timezone.utc).strftime("%Y-%m-%d")]
    fin = min(fin, int(datetime.strptime(jours[-1], "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp()) + 86400 - 300)
    coupe = debut + int(JOURS * 2 / 3) * 86400
    rap = [f"# Kronos (IA de prevision de bougies) sur les marches 5 min — {JOURS} jours ({jours[0]} -> {jours[-1]})" + (" — ESSAI" if ESSAI else ""),
           f"Kronos-small, {LOOK} bougies 1 min d'historique, {K} chemins par prevision. Comparaison au resultat officiel Polymarket."]
    for prefixe, sym in (("btc", "BTCUSDT"), ("eth", "ETHUSDT")):
        rap += etudier(prefixe, sym, jours, debut, fin, coupe, t0)
        if not ESSAI: open(OUT + "resultat_kronos.md", "w").write("\n".join(rap))
    rap.append(f"\nDuree : {time.time() - t0:.0f} s")
    open(OUT + ("resultat_kronos_essai.md" if ESSAI else "resultat_kronos.md"), "w").write("\n".join(rap))
    print("\n".join(rap))


if __name__ == "__main__":
    main()
