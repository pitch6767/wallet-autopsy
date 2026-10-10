"""Photos « qui a bougé en premier » (/api/lead) : 10 s à 100 ms avant le 1er désaccord ≥ 0,20 du cycle, puis 10 s après.
Pour chaque photo « avant » : qui a bougé en premier dans notre sens ? Bourses (Bybit perp, OKX, Coinbase, Binance), Chainlink, ou Polymarket (prix vendeur de notre côté qui baisse).
Puis 10 s après : Polymarket a-t-il rejoint le modèle, ou les bourses sont-elles revenues en arrière ?"""
import json, gzip, collections, time, sys
import numpy as np
sys.path.insert(0, "etude/bot5min")
D = json.load(gzip.open("bot95/lead.json.gz", "rt")); O = json.load(open("bot95/officiels.json"))
f0 = lambda x: (f"+{x:,.0f} $" if x >= 0 else f"−{-x:,.0f} $").replace(",", " ")
AV = {d["start"]: d for d in D if d["phase"] == "avant"}; AP = {d["start"]: d for d in D if d["phase"] == "apres"}
SRC = [("Bybit perp", 1), ("OKX perp", 2), ("Coinbase", 3), ("Binance", 4), ("Chainlink", 5)]
def ask_cote(l, cols, up):
    k = cols.index("pm_up_ventes_top3" if up else "pm_down_ventes_top3"); v = l[k]
    return v[0][0] if v else None
res = []
for st, d in AV.items():
    cols = d["colonnes"]; L = d["lignes"]; up = d["cote"] == "Up"; sg = 1 if up else -1
    if len(L) < 50: continue
    t0 = L[0][0]; first = {}
    for nom, i in SRC:
        p0 = next((l[i] for l in L if l[i]), None)
        if p0 is None: continue
        for l in L:
            if l[i] and (l[i] - p0) * sg >= 5: first[nom] = l[0] - t0; break
    a0 = next((ask_cote(l, cols, up) for l in L if ask_cote(l, cols, up) is not None), None)
    if a0 is not None:
        for l in L:
            a = ask_cote(l, cols, up)
            if a is not None and a0 - a >= 0.01: first["Polymarket"] = l[0] - t0; break
    qui = min(first, key=first.get) if first else "personne (≥ 5 $ ou ≥ 1 c)"
    mv = {nom: ((L[-1][i] - next((l[i] for l in L if l[i]), L[-1][i])) * sg if L[-1][i] else None) for nom, i in SRC}
    # 10 s après
    ap = AP.get(st); apres = None
    if ap and len(ap["lignes"]) > 10:
        La = ap["lignes"]; aa = ask_cote(La[-1], cols, up); pp = La[-1][1]; p_sig = L[-1][1]
        apres = dict(ask10=aa, dperp=(pp - p_sig) * sg if pp and p_sig else None)
    g = (O.get(f"BTC:{st}") or {}).get("gagnant")
    res.append(dict(st=st, qui=qui, first=first, mv=mv, ask=d["ask"], ecart=d["ecart"], reste=d["reste_s"], apres=apres, gagne=None if g is None else ((g == "Up") == up)))
out = ["# Qui a bougé en premier ? Photos des 10 s avant le premier désaccord ≥ 0,20 du cycle", "",
       f"{len(res)} photos BTC ({time.strftime('%d.%m %H:%M', time.gmtime(min(r['st'] for r in res) + 7200))} → {time.strftime('%d.%m %H:%M', time.gmtime(max(r['st'] for r in res) + 7200))}). "
       "« A bougé » = au moins 5 $ dans notre sens pour une bourse ou Chainlink, au moins 1 c de baisse du vendeur de notre côté pour Polymarket.", "",
       "| Premier à bouger | Photos | Part | Désaccord gagné (côté du modèle) | Gain si achat 50 $ au prix du signal |", "|---|---|---|---|---|"]
from sauvetage import FEE
C_ = collections.defaultdict(list)
for r in res: C_[r["qui"]].append(r)
pn = lambda r: (50 / r["ask"]) * ((1 if r["gagne"] else 0) - r["ask"] - FEE(r["ask"])) if r["gagne"] is not None else 0
for q, L in sorted(C_.items(), key=lambda x: -len(x[1])):
    v = [r for r in L if r["gagne"] is not None]
    out.append(f"| {q} | {len(L)} | {100 * len(L) / len(res):.0f} % | {100 * sum(r['gagne'] for r in v) / max(1, len(v)):.0f} % ({len(v)}) | {f0(sum(pn(r) for r in v))} |")
# Polymarket seul vs bourses
pm_only = [r for r in res if "Polymarket" in r["first"] and not any(k in r["first"] for k, _ in SRC)]
bx_only = [r for r in res if any(k in r["first"] for k, _ in SRC) and "Polymarket" not in r["first"]]
both = [r for r in res if "Polymarket" in r["first"] and any(k in r["first"] for k, _ in SRC)]
out += ["", "## Qui a créé le désaccord ?", "", "| Cas | Photos | Désaccord gagné | Gain (50 $ au prix du signal) |", "|---|---|---|---|"]
for nom, L in (("seul Polymarket a bougé (vendeur qui baisse, bourses immobiles)", pm_only), ("seules les bourses ont bougé (Polymarket immobile)", bx_only), ("les deux ont bougé", both),
               ("personne n'a bougé de façon nette", [r for r in res if not r["first"]])):
    v = [r for r in L if r["gagne"] is not None]
    out.append(f"| {nom} | {len(L)} | {100 * sum(r['gagne'] for r in v) / max(1, len(v)):.0f} % | {f0(sum(pn(r) for r in v))} |")
# avance moyenne
out += ["", "## Avance des sources (quand plusieurs ont bougé)", "", "| Source | A bougé (photos) | Moment médian du mouvement dans les 10 s | Premier quand elle a bougé |", "|---|---|---|---|"]
for nom in [s for s, _ in SRC] + ["Polymarket"]:
    L = [r for r in res if nom in r["first"]]
    out.append(f"| {nom} | {len(L)} | {np.median([r['first'][nom] for r in L]):.1f} s | {100 * sum(1 for r in L if r['qui'] == nom) / max(1, len(L)):.0f} % |")
# 10 s apres
ok = [r for r in res if r["apres"] and r["apres"]["ask10"] is not None and r["apres"]["dperp"] is not None]
cat = collections.defaultdict(list)
for r in ok:
    j = r["apres"]["ask10"] - r["ask"]; rev = r["apres"]["dperp"] < -5
    c = ("Polymarket a rejoint (vendeur +3 c ou plus)" if j >= 0.03 else "Polymarket n'a pas bougé (±3 c)" if abs(j) < 0.03 else "Polymarket s'est éloigné encore (−3 c ou plus)") + (" · bourses revenues en arrière" if rev else "")
    cat[c].append(r)
out += ["", "## 10 s après le signal", "", "« Bourses revenues en arrière » = le perp Bybit est revenu d'au moins 5 $ contre nous pendant les 10 s suivantes (le mouvement qui créait le désaccord s'est effacé).", "",
        "| Ce qui s'est passé | Photos | Désaccord gagné | Gain (50 $ au prix du signal) |", "|---|---|---|---|"]
for c, L in sorted(cat.items(), key=lambda x: -len(x[1])):
    v = [r for r in L if r["gagne"] is not None]
    out.append(f"| {c} | {len(L)} | {100 * sum(r['gagne'] for r in v) / max(1, len(v)):.0f} % | {f0(sum(pn(r) for r in v))} |")
open("etude/bot5min/resultat_lead.md", "w").write("\n".join(out)); print("\n".join(out))
