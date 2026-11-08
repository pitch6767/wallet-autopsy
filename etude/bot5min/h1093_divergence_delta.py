# H1093 (08.11.2026) — divergence du delta cumulé (CVD) du perp Bybit sur 60 s.
# Hypothèse écrite AVANT calcul : quand, sur les 60 s avant la décision, le delta cumulé du perp Bybit (achats agressifs − ventes
# agressives) part dans le sens opposé à la variation du prix Bybit, et qu'il est fort (|CVD| ≥ médiane de l'apprentissage),
# acheter sur Polymarket le côté indiqué par le FLUX (pas par le prix) rapporte de l'argent après frais.
# Source de l'idée : zadescoxp/order-flow-screener (« CVD and price change with a divergence flag »).
# Moment de décision principal : T−60 s (fixé avant calcul). Secondaire (2e essai du registre) : T−30 s.
# Données réelles uniquement : signaux seconde par seconde enregistrés par bot95 (bot95/donnees/*/sig_BTC.json.gz),
# prix d'achat = meilleur vendeur Polymarket à la seconde de décision (taille disponible respectée), frais taker 0,072·p·(1−p) par part.
# Apprentissage (seuil seulement) : 07.10–12.10. Jugement : 13.10 → 08.11, en 4 périodes. Aucun ordre.
import gzip, json, os, glob, random, math, sys
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
PARIS = ZoneInfo("Europe/Paris")
BASE = os.path.join(os.path.dirname(__file__), "..", "..", "bot95")
MISE, FEE = 50.0, 0.072

C = {}
for f in sorted(glob.glob(os.path.join(BASE, "donnees", "*", "sig_BTC.json.gz"))):
    d = json.load(gzip.open(f))
    for doc in d.values():
        col = doc["colonnes"]; ix = {c: i for i, c in enumerate(col)}
        for L in doc["lignes"]:
            C[L[ix["t"]]] = (L[ix["start"]], L[ix["prix_a_battre"]], L[ix["bybit_perp"]], L[ix["perp_achats_usd"]] or 0, L[ix["perp_ventes_usd"]] or 0,
                             L[ix["pm_up_achat"]], L[ix["pm_up_vente"]], L[ix["pm_up_achat_taille"]], L[ix["pm_up_vente_taille"]])
print("secondes:", len(C), file=sys.stderr)

# H1093 (08.11.2026) — divergence du delta cumulé (CVD) du perp Bybit sur 60 s.
# Hypothèse écrite AVANT calcul : quand, sur les 60 s avant la décision, le delta cumulé du perp Bybit (achats agressifs − ventes
# agressives) part dans le sens opposé à la variation du prix Bybit, et qu'il est fort (|CVD| ≥ médiane de l'apprentissage),
# acheter sur Polymarket le côté indiqué par le FLUX (pas par le prix) rapporte de l'argent après frais.
# Source de l'idée : zadescoxp/order-flow-screener (« CVD and price change with a divergence flag »).
# Moment de décision principal : T−60 s (fixé avant calcul). Secondaire (2e essai du registre) : T−30 s.
# Données réelles uniquement : signaux seconde par seconde enregistrés par bot95 (bot95/donnees/*/sig_BTC.json.gz),
# prix d'achat = meilleur vendeur Polymarket à la seconde de décision, frais taker 0,072·p·(1−p) par part,
# règlement officiel Polymarket de chaque marché BTC 5 min (table markets de Wallet Autopsy, 0 = Up, 1 = Down ;
# vérifié identique à officiels.json sur les 2 271 marchés communs). Le « prix à battre » des signaux n'est PAS utilisé.
WA = json.load(open(os.path.join(os.path.dirname(__file__), "h1093_gagnants_wa.json")))
gagnant = {int(k): ("Up" if v == 0 else "Down") for k, v in WA.items()}
print("marchés réglés:", len(gagnant), file=sys.stderr)

def mesures(s, avant):
    t = s + 300 - avant
    if t not in C or C[t][0] != s: return None
    pts = [C[x] for x in range(t - 60, t) if x in C]
    if len(pts) < 50 or (t - 60) not in C or C[t][2] is None or C[t - 60][2] is None: return None
    cvd = sum(p[3] - p[4] for p in pts); dp = C[t][2] - C[t - 60][2]
    r = C[t]; bid, ask, tb, ta = r[5], r[6], r[7], r[8]
    if not bid or not ask or ask <= bid: return None
    return dict(t=t, cvd=cvd, dp=dp, bid=bid, ask=ask, tb=tb or 0, ta=ta or 0)

def jour(t): return datetime.fromtimestamp(t, PARIS).date()
def periode(t):
    j = jour(t)
    if j <= datetime(2026, 10, 12).date(): return "apprentissage"
    if j <= datetime(2026, 10, 19).date(): return "P1 13-19.10"
    if j <= datetime(2026, 10, 26).date(): return "P2 20-26.10"
    if j <= datetime(2026, 11, 2).date(): return "P3 27.10-02.11"
    return "P4 03-08.11"

def trade(m, cote, s):
    if m["ask"] - m["bid"] > 0.0101: return None          # écart > 1 c au moment d'acheter : on n'achète pas (règle H1074)
    p, taille = (m["ask"], m["ta"]) if cote == "Up" else (round(1 - m["bid"], 4), m["tb"])
    if not (0.02 <= p <= 0.98): return None
    parts = min(MISE / p, taille) if taille else 0
    if parts < 1: return None
    g = gagnant[s] == cote
    return parts * ((1 if g else 0) - p) - parts * FEE * p * (1 - p), parts * p

def stats(T):
    if not T: return dict(n=0)
    T = sorted(T); pnl = [x[1] for x in T]; cum = pk = dd = 0
    for x in pnl: cum += x; pk = max(pk, cum); dd = min(dd, cum - pk)
    jours = {}
    for t, v, _ in T: jours[jour(t)] = jours.get(jour(t), 0) + v
    J = list(jours.values()); rng = random.Random(1093); B = []
    for _ in range(2000): B.append(sum(rng.choice(J) for _ in J))
    B.sort(); nj = max(1, (max(t for t, _, _ in T) - min(t for t, _, _ in T)) / 86400)
    gm = sum(1 for x in pnl if x > 0) / len(pnl)
    return dict(n=len(T), net=round(sum(pnl), 1), par_jour=round(sum(pnl) / nj, 1), creux=round(dd, 1), mise_max=round(max(x[2] for x in T), 1),
                ic95=[round(B[50], 1), round(B[1949], 1)], gagnes=round(gm * 100), par_dollar=round(sum(pnl) / sum(x[2] for x in T) * 100, 1))

def etude(avant):
    marches = sorted(s for s in gagnant)
    M = {s: mesures(s, avant) for s in marches}; M = {s: m for s, m in M.items() if m}
    q = sorted(abs(m["cvd"]) for s, m in M.items() if periode(m["t"]) == "apprentissage")
    seuil = q[len(q) // 2] if q else 0
    R = {k: {} for k in ["H : divergence, côté du flux", "nul A : divergence, côté du prix", "nul C : flux fort ET prix d'accord, côté du flux", "tous les marchés, côté du flux fort"]}
    hasard = {}
    for s, m in M.items():
        P = periode(m["t"])
        if abs(m["cvd"]) < seuil or m["dp"] == 0: continue
        flux = "Up" if m["cvd"] > 0 else "Down"; prix = "Up" if m["dp"] > 0 else "Down"
        div = flux != prix
        def ajoute(nom, cote):
            r = trade(m, cote, s)
            if r: R[nom].setdefault(P, []).append((m["t"], r[0], r[1]))
        ajoute("tous les marchés, côté du flux fort", flux)
        if div:
            ajoute("H : divergence, côté du flux", flux); ajoute("nul A : divergence, côté du prix", prix)
            hasard.setdefault(P, []).append((s, m))
        else: ajoute("nul C : flux fort ET prix d'accord, côté du flux", flux)
    # nul B : mêmes moments que H, côté tiré au hasard (500 tirages) — part des tirages qui font au moins aussi bien que H
    nulB = {}
    for P, L in hasard.items():
        h = sum(x[1] for x in R["H : divergence, côté du flux"].get(P, []))
        rng = random.Random(hash(P) & 0xffff); mieux = 0
        for _ in range(500):
            tot = 0
            for s, m in L:
                r = trade(m, rng.choice(["Up", "Down"]), s)
                if r: tot += r[0]
            mieux += tot >= h
        nulB[P] = round(mieux / 500, 3)
    out = {"avant_fin_s": avant, "seuil_cvd_usd": round(seuil), "marches_mesures": len(M), "nulB_part_hasard_aussi_bon": nulB, "resultats": {}}
    for nom, parP in R.items():
        out["resultats"][nom] = {P: stats(parP.get(P, [])) for P in ["apprentissage", "P1 13-19.10", "P2 20-26.10", "P3 27.10-02.11", "P4 03-08.11"]}
        out["resultats"][nom]["jugement 13.10-08.11"] = stats([x for P, L in parP.items() if P != "apprentissage" for x in L])
    return out

res = {"T-60 (principal)": etude(60), "T-30 (secondaire)": etude(30)}
json.dump(res, open(os.path.join(os.path.dirname(__file__), "h1093_resultat.json"), "w"), ensure_ascii=False, indent=1)
for k, o in res.items():
    print("=====", k, "seuil", o["seuil_cvd_usd"], "marchés", o["marches_mesures"], "hasard", o["nulB_part_hasard_aussi_bon"])
    for nom, r in o["resultats"].items():
        print(" --", nom)
        for P, s in r.items(): print("    ", P.ljust(22), s)
