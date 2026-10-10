"""Audit de la nuit du 09 au 10.10.2026 (demande ChatGPT 07:34) : chaque achat TWAP fin reconstruit à partir des données enregistrées
(carnet 4×/s, perp Bybit, OKX, Chainlink), comparé au règlement officiel. Aucune décision ni stratégie modifiée."""
import json, gzip, glob, bisect, math, time, calendar, collections, sys
import numpy as np
sys.path.insert(0, "etude/bot5min")
from sauvetage import FEE
O = json.load(open("bot95/officiels.json"))
rows = {}
for f in sorted(glob.glob("bot95/donnees/2026-10-*/rec_BTC.json.gz"))[-2:]:
    for doc in json.load(gzip.open(f, "rt")).values():
        for r in doc["lignes"]: rows[r[0]] = r
R = sorted(rows.values(), key=lambda r: r[0]); T = [r[0] for r in R]
def sec(i, s):
    k = bisect.bisect_right(T, s + 0.999) - 1
    while k >= 0 and not R[k][i]: k -= 1
    return R[k][i] if k >= 0 and s + 1 - R[k][0] < 30 else None
def at(i, t):
    k = bisect.bisect_right(T, t) - 1
    while k >= 0 and not R[k][i]: k -= 1
    return (R[k][i], R[k][0]) if k >= 0 else (None, None)
phi = lambda x: 0.5 * (1 + math.erf(x / math.sqrt(2)))
hs = lambda t: time.strftime("%H:%M:%S", time.gmtime(t + 7200))
f0 = lambda x: (f"+{x:,.0f} $" if x >= 0 else f"−{-x:,.0f} $").replace(",", " ")
def moteur(t, st):
    """reconstruction du moteur TWAP fin à l'instant t, avec ce qui était reçu avant t"""
    end = st + 300; deb = end - 60; ts = int(t)
    K = np.mean([v for v in (sec(15, s) for s in range(st - 60, st)) if v])
    ser = [sec(11, s) for s in range(ts - 300, ts + 1)]; ser = [x for x in ser if x]
    r = np.diff(np.log(ser)); sg = float(np.std(r))
    base = float(np.median([sec(11, s) - sec(15, s) for s in range(ts - 120, ts) if sec(11, s) and sec(15, s)]))
    p, tp = at(11, t); S = p - base
    if ts >= deb:
        con = [v for v in (sec(15, s) for s in range(deb, min(ts, end - 1) + 1)) if v]; nr = max(1, end - 1 - ts)
        E = (sum(con) + nr * S) / (len(con) + nr); v = (sg * S) ** 2 * nr ** 3 / 3 / 3600; known = len(con)
    else: E = S; v = (sg * S) ** 2 * ((deb - ts) + 20); known = 0
    sd = math.sqrt(v + 0.25)
    p1 = sec(11, ts - 1); saut = (p - p1) if p1 else 0
    vol_s = sg * S
    return dict(K=K, E=E, sd=sd, z=(E - K) / sd, p=phi((E - K) / sd), vol=vol_s, saut=saut, sautz=saut / vol_s if vol_s > 0 else 0, known=known,
                cl=sec(15, ts - 1), S=S, base=base, fige=sum(1 for a, b in zip(ser[-120:], ser[-119:]) if a == b))
NOMS = ["TWAP fin", "TWAP fin sauts", "TWAP fin correction spot-perp", "TWAP fin confirme Chainlink"]
DEBUT, FIN = calendar.timegm((2026, 10, 9, 23, 36, 0)), calendar.timegm((2026, 10, 10, 5, 30, 0))
out = ["# Audit de la nuit du 9 au 10 octobre — TWAP fin (01:36 → 07:30, heure suisse)", ""]
TR = []
for n in NOMS:
    d = json.load(open(f"bot95/sauvegarde/{n.replace(' ', '_')}_BTC.json"))
    for x in d["trades"].values():
        t = x.get("tAchat") or calendar.timegm(time.strptime(x["heure"][:19], "%Y-%m-%dT%H:%M:%S"))
        if DEBUT <= t <= FIN and x.get("gagnant"): TR.append((n, t, x))
TR.sort(key=lambda z: z[1])
out += ["## 1. Chaque achat reconstruit", "",
        "Prix à battre : moyenne Chainlink des 60 s avant le début. « Saut » : mouvement du perp Bybit dans la dernière seconde, en $ et en nombre d'écarts-types (volatilité par seconde que le moteur utilisait). « Figé » : secondes sur 120 où le perp n'a pas bougé.", "",
        "| Heure | Fantôme | Côté | Prix payé | Proba enregistrée | Proba reconstruite | Restant | Prix à battre (officiel) | Moyenne prévue | Dernier Chainlink | Vol./s | Saut 1 s | Figé | Gagnant | Net |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
A = []
for n, t, x in TR:
    st = x["start"]; m = moteur(t, st); o = O.get(f"BTC:{st}") or {}
    up = x["cote"] == "Up"; pr_ = m["p"] if up else 1 - m["p"]
    A.append(dict(n=n, t=t, x=x, m=m, up=up))
    out.append(f"| {hs(t)} | {n.replace('TWAP fin', 'TF').strip() or 'TF'} | {x['cote']} | {x['prix']:.3f} | {x.get('proba0')} | {pr_:.3f} | {x.get('restant_s')} s | {m['K']:.2f} ({o.get('ptb', 0):.2f}) | {m['E']:.2f} | {m['cl']:.2f} | {m['vol']:.2f} $ | {m['saut']:+.1f} $ ({m['sautz']:+.0f}×) | {m['fige']} | {x['gagnant']} | {f0(x['net'])} |")
# 2. sauts
out += ["", "## 2. Les achats déclenchés par un saut d'une seconde", "", "| Groupe | Achats | Gagnés | Résultat |", "|---|---|---|---|"]
G = collections.defaultdict(list)
for a in A:
    k = "saut ≥ 10 écarts-types dans la dernière seconde" if abs(a["m"]["sautz"]) >= 10 else "saut 4-10 écarts-types" if abs(a["m"]["sautz"]) >= 4 else "pas de saut"
    G[k].append(a); G["proba ≥ 0,90"].append(a) if (a["x"].get("proba0") or 0) >= 0.9 else None
for k, v in G.items():
    out.append(f"| {k} | {len(v)} | {sum(a['x']['gagnant'] == a['x']['cote'] for a in v)} | {f0(sum(a['x']['net'] for a in v))} |")
open("etude/bot5min/resultat_audit_nuit.md", "w").write("\n".join(out)); print("\n".join(out))
# 3. bilan par fantome et attente selon le prix du marche
out += ["", "## 3. La nuit par fantôme : résultat contre ce que le prix du marché annonçait", "",
        "| Fantôme | Achats | Gagnés | Gagnés attendus selon le prix payé | Gagnés attendus selon notre proba | Probabilité d'avoir aussi peu ou moins (selon le prix) | Résultat |", "|---|---|---|---|---|---|---|"]
def pbin(ps, k):
    D = np.zeros(len(ps) + 1); D[0] = 1
    for p in ps: D[1:] = D[1:] * (1 - p) + D[:-1] * p; D[0] *= (1 - p)
    return D[:k + 1].sum()
for n in NOMS:
    S = [a for a in A if a["n"] == n]
    if not S: continue
    g = sum(a["x"]["gagnant"] == a["x"]["cote"] for a in S); ps = [min(0.99, a["x"]["prix"]) for a in S]
    out.append(f"| {n} | {len(S)} | {g} | {sum(ps):.1f} | {sum(a['x'].get('proba0') or 0 for a in S):.1f} | {100 * pbin(ps, g):.0f} % | {f0(sum(a['x']['net'] for a in S))} |")
# 4. confirme chainlink : journal
try:
    J = [j for j in json.load(open("bot95/twap_confirme.json")) if DEBUT - 300 <= j["start"] <= FIN]
    out += ["", f"## 4. TWAP fin confirmé Chainlink : les {len(J)} signaux de la nuit (achetés et abandonnés)", "",
            "| Signal | Côté | Restant | Proba / vendeur au signal | Chainlink suivant reçu après | Proba / vendeur après | Décision | Gagnant |", "|---|---|---|---|---|---|---|---|"]
    for j in sorted(J, key=lambda j: j["tSignal"]):
        g = (O.get(f"BTC:{j['start']}") or {}).get("gagnant", "?")
        out.append(f"| {hs(j['tSignal'])} | {j['cote']} | {j['restant_s']} s | {j['proba']} / {j['vendeur']} | {j.get('attente_s', '—')} s | {j.get('proba2', '—')} / {j.get('vendeur2', '—')} | {j['etat']} | {g} |")
    ab = [j for j in J if j["etat"] != "achat"]
    out.append(f"\nSignaux abandonnés : {len(ab)} ; parmi eux, le côté du signal a gagné {sum((O.get(f'BTC:{j[chr(115)+chr(116)+chr(97)+chr(114)+chr(116)]}') or {}).get('gagnant') == j['cote'] for j in ab)} fois.")
except Exception as e: out += ["", f"(journal du confirmé indisponible : {e})"]
open("etude/bot5min/resultat_audit_nuit.md", "w").write("\n".join(out)); print("\n".join(out[-60:]))
