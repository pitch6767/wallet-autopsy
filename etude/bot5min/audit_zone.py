"""Famille « désaccord 30 zone » : comparaison sur les mêmes cycles (nuit 01:36-07:30 du 10.10 et depuis le début commun). Aucune stratégie modifiée."""
import json, time, calendar, collections, glob
f0 = lambda x: (f"+{x:,.0f} $" if x >= 0 else f"−{-x:,.0f} $").replace(",", " ")
N = {"zone simple": "desaccord 30 zone 0,15-0,35", "zone + modèle monte": "desaccord 30 zone + modele monte", "zone + Binance/perp": "desaccord 30 zone 0,15-0,35 + Binance et perp",
     "zone + sortie −10": "desaccord 30 zone + sortie modele -10", "zone + Binance/perp + sortie −10": "desaccord 30 zone + Binance et perp + sortie modele -10",
     "combiné taille 25/50": "desaccord 30 zone + Binance et perp + sortie modele -10 + pas Poly qui baisse + taille 25/50"}
def charge(n):
    f = "bot95/sauvegarde/" + n.replace(" ", "_").replace(",", ",") + "_BTC.json"
    c = [p for p in glob.glob("bot95/sauvegarde/*_BTC.json") if p.endswith(n.replace(" ", "_").replace("/", "_") + "_BTC.json")]
    d = json.load(open(c[0])); T = {}
    for x in d["trades"].values():
        if not x.get("gagnant"): continue
        t = x.get("tAchat") or calendar.timegm(time.strptime(x["heure"][:19], "%Y-%m-%dT%H:%M:%S")); T[x["start"]] = dict(t=t, **x)
    return T
D = {k: charge(v) for k, v in N.items()}
deb_commun = max(min(x["t"] for x in T.values()) for T in D.values())
out = ["# Famille « désaccord 30 zone » — mêmes cycles", ""]
for titre, a, b in (("Nuit du 10.10 (01:36 → 07:30)", calendar.timegm((2026, 10, 9, 23, 36, 0)), calendar.timegm((2026, 10, 10, 5, 30, 0))),
                    (f"Depuis le début commun ({time.strftime('%d.%m %H:%M', time.gmtime(deb_commun + 7200))}) → 07:30", deb_commun, calendar.timegm((2026, 10, 10, 5, 30, 0)))):
    out += [f"## {titre}", "", "| Stratégie | Trades | Gagnés | Résultat | Jackpots (≥ 4× la mise) | Prix moyen | Parts moyennes | Sorties anticipées |", "|---|---|---|---|---|---|---|---|"]
    S = {k: {st: x for st, x in T.items() if a <= x["t"] <= b} for k, T in D.items()}
    for k, T in S.items():
        L = list(T.values())
        if not L: continue
        jk = [x for x in L if x["net"] >= 4 * x["prix"] * x["parts"]]
        out.append(f"| {k} | {len(L)} | {sum(x['gagnant'] == x['cote'] for x in L)} | **{f0(sum(x['net'] for x in L))}** | {len(jk)} ({f0(sum(x['net'] for x in jk))}) | {sum(x['prix'] for x in L) / len(L):.3f} | {sum(x['parts'] for x in L) / len(L):.0f} | {sum(1 for x in L if any('revente' in j for j in x.get('journal', [])))} |")
    ref = S["zone simple"]
    out += ["", "Par rapport à « zone simple » (mêmes cycles) :", "", "| Stratégie | Cycles communs | Résultat sur les communs (elle / zone simple) | Cycles évités par elle : gagnants / perdants de zone simple | Résultat évité | Cycles en plus | Résultat des cycles en plus |", "|---|---|---|---|---|---|---|"]
    for k, T in S.items():
        if k == "zone simple": continue
        com = set(T) & set(ref); evit = set(ref) - set(T); plus = set(T) - set(ref)
        out.append(f"| {k} | {len(com)} | {f0(sum(T[s]['net'] for s in com))} / {f0(sum(ref[s]['net'] for s in com))} | {sum(ref[s]['net'] > 0 for s in evit)} / {sum(ref[s]['net'] <= 0 for s in evit)} | {f0(sum(ref[s]['net'] for s in evit))} | {len(plus)} | {f0(sum(T[s]['net'] for s in plus))} |")
    out.append("")
open("etude/bot5min/resultat_audit_zone.md", "w").write("\n".join(out)); print("\n".join(out))
