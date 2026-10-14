"""Verdict prospectif des trois variantes V2-F (en ligne depuis le 10.10 12:33 heure suisse) contre V2-F original, SUR LES MÊMES CYCLES.
Demande de Pitch (10.10) : quelle modification apporte le plus de bénéfice supplémentaire sans sacrifier excessivement les jackpots ?
Sources : bot95/sauvegarde/V2-F_*_BTC.json (trades réglés) et bot95/v2f_variantes.json (chaque opportunité, achetée ou refusée,
avec partsMeilleur/coutMeilleur = original ramené au seul meilleur vendeur). Résultats officiels : bot95/officiels.json.
Périodes : « verdict » = 10.10 12:33 → 12.10 24:00 (heure suisse) ; « 13.10 » à part (jour réservé, pas utilisé pour choisir).
Diagnostic seulement : aucun fantôme modifié, rien activé."""
import json, time, collections
h = lambda t: time.strftime("%d.%m %H:%M", time.gmtime(t + 7200))
D0 = 1791628380                      # 10.10 12:33 heure suisse
J13 = 1791842400                     # 13.10 00:00 heure suisse
O = json.load(open("bot95/officiels.json"))
def charge(f):
    J = json.load(open(f"bot95/sauvegarde/{f}.json")); T = J["trades"]; T = list(T.values()) if isinstance(T, dict) else T
    out = {}
    for t in T:
        if t.get("start") is None or t.get("net") is None: continue
        c = t["parts"] * t["prix"]
        out.setdefault(t["start"], []).append((t["net"], c, t["start"]))
    return out, J["maj"]
NOMS = {"V2-F original (vendeur + 1 c)": "V2-F_ecart_qui_grandit_BTC", "V2-F miroir 1 s": "V2-F_miroir_1_s_BTC",
        "V2-F incertitude 0,01 %": "V2-F_incertitude_0,01_BTC", "V2-F pause memoire": "V2-F_pause_memoire_BTC"}
DAT = {k: charge(v) for k, v in NOMS.items()}
fin_orig = max(DAT["V2-F original (vendeur + 1 c)"][0]); fin_pause = max(DAT["V2-F pause memoire"][0])
FIN = min(fin_orig, fin_pause) + 300
# original au seul meilleur vendeur, depuis le journal (signal original, premier par cycle)
V = json.load(open("bot95/v2f_variantes.json")); om = {}
for x in sorted(V, key=lambda x: x["t"]):
    if x["nom"] != "V2-F ecart qui grandit" or x["decision"] != "signal" or x["start"] in om: continue
    g = O.get(f"BTC:{x['start']}", {}).get("gagnant")
    if g is None or not x.get("partsMeilleur"): continue
    om[x["start"]] = [((x["partsMeilleur"] if g == x["cote"] else 0) - x["coutMeilleur"], x["coutMeilleur"], x["start"])]
DAT["V2-F original au seul meilleur vendeur (journal)"] = (om, "journal")
def stats(d, a, b, ref=None):
    L = sorted([x for st, v in d.items() if a <= st < b for x in v], key=lambda x: x[2])
    n = len(L); pnl = sum(x[0] for x in L); cap = sum(x[1] for x in L); w = sum(x[0] > 0 for x in L)
    cum = pk = dd = 0; run = mx = 0
    for x in L:
        cum += x[0]; pk = max(pk, cum); dd = max(dd, pk - cum)
        run = run + 1 if x[0] <= 0 else 0; mx = max(mx, run)
    jp = {x[2] for x in L if x[0] >= 4 * x[1]}
    return dict(n=n, pnl=pnl, w=w, cap=cap, dd=dd, mx=mx, jp=jp, jpv=sum(x[0] for x in L if x[0] >= 4 * x[1]), cyc={x[2] for x in L},
                perdu=sum(x[0] for x in L if x[0] < 0))
f0 = lambda x: (f"+{x:,.0f} $" if x >= 0 else f"−{-x:,.0f} $").replace(",", " ")
out = ["# V2-F : les trois variantes contre l'original, sur les mêmes cycles (prospectif)", "",
       f"Généré le {time.strftime('%d.%m.%Y %H:%M', time.gmtime())} UTC. Original et « pause mémoire » enregistrés jusqu'au {h(FIN - 300)} (arrêtés ensuite) : la comparaison s'arrête là.", ""]
RES = {}
for lab, a, b in (("verdict : 10.10 12:33 → 12.10 24:00", D0, J13), ("13.10 seul (jour réservé, pas utilisé pour choisir)", J13, FIN)):
    out += [f"## {lab}", "", "| Stratégie | Achats | Gagnés | Bénéfice net | Capital engagé | ROI | Creux max | Pertes de suite max | Jackpots (≥ 4× mise) | Jackpots de l'original manqués | Pertes de l'original évitées |",
            "|---|---|---|---|---|---|---|---|---|---|---|"]
    so = stats(DAT["V2-F original (vendeur + 1 c)"][0], a, b)
    for k, (d, _) in DAT.items():
        s = stats(d, a, b); RES[(lab, k)] = s
        manq = len(so["jp"] - s["cyc"]) if "original" not in k else 0
        Lo = {st: v for st, v in DAT["V2-F original (vendeur + 1 c)"][0].items() if a <= st < b}
        evit = -sum(x[0] for st, v in Lo.items() if st not in s["cyc"] for x in v if x[0] < 0) if "original" not in k else 0
        out.append(f"| {k} | {s['n']} | {s['w']} ({100 * s['w'] / max(s['n'], 1):.0f} %) | {f0(s['pnl'])} | {f0(s['cap'])} | {100 * s['pnl'] / max(s['cap'], 1):+.1f} % | {f0(s['dd'])} | {s['mx']} | {len(s['jp'])} ({f0(s['jpv'])}) | {manq if 'original' not in k else '—'} | {f0(evit) if 'original' not in k else '—'} |")
    out.append("")
open("etude/bot5min/resultat_v2f_variantes_verdict.md", "w").write("\n".join(out)); print("\n".join(out))
