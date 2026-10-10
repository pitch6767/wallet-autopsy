"""Contribution exacte au résultat de A de chaque trade refusé par B, C et D (demande du 10.10.2026 12:21). Lit combinaison_D_opportunites.json."""
import json, time
f0 = lambda x: (f"+{x:,.0f} $" if x >= 0 else f"−{-x:,.0f} $").replace(",", " ")
hs = lambda t: time.strftime("%d.%m %H:%M", time.gmtime(t + 7200))
D = {int(k): v for k, v in json.load(open("etude/bot5min/combinaison_D_opportunites.json")).items()}
B = lambda d: 0.20 <= d["edge"] < 0.30
POL = {"B": B, "C": lambda d: B(d) and d["ncl"] >= 2, "D": lambda d: B(d) and d["ncl"] >= 2 and d["indep"]}
jk = lambda d: d["pn"] >= 4 * d["mise"]
out = ["# Les trades refusés par B, C et D : contribution exacte au résultat de A", "",
       "A = tous les premiers signaux E du cycle. Pour chaque politique, les trades de A qu'elle refuse, classés par contribution. Toutes périodes (07.10 → 10.10 11:10), puis hors apprentissage.", ""]
for g, filt in (("toutes périodes", lambda d: True), ("hors apprentissage", lambda d: d["per"] != "apprentissage")):
    A = [d for d in D.values() if filt(d)]; tA = sum(d["pn"] for d in A)
    out += [f"## {g} — A : {len(A)} trades, {f0(tA)}", "", "| Politique | Trades gardés | Résultat gardé | Trades refusés | Pertes évitées (nombre) | Gains sacrifiés (nombre) | dont jackpots sacrifiés | Solde des refusés | Résultat final vs A |", "|---|---|---|---|---|---|---|---|---|"]
    for k, f in POL.items():
        G_ = [d for d in A if f(d)]; R_ = [d for d in A if not f(d)]
        pe = [d for d in R_ if d["pn"] < 0]; gs = [d for d in R_ if d["pn"] >= 0]; jj = [d for d in gs if jk(d)]
        out.append(f"| {k} | {len(G_)} | {f0(sum(d['pn'] for d in G_))} | {len(R_)} | {f0(-sum(d['pn'] for d in pe))} ({len(pe)}) | {f0(sum(d['pn'] for d in gs))} ({len(gs)}) | {f0(sum(d['pn'] for d in jj))} ({len(jj)}) | {f0(sum(d['pn'] for d in R_))} | **{f0(sum(d['pn'] for d in G_) - tA)}** |")
    out.append("")
    # pourquoi B > D : trades refusés par D mais gardés par B
    X = [d for d in A if POL["B"](d) and not POL["D"](d)]
    out += [f"### Pourquoi B fait mieux que D ({g}) : les {len(X)} trades gardés par B mais refusés par D", "",
            f"Résultat de ces trades : **{f0(sum(d['pn'] for d in X))}** ; gagnants {sum(d['gm'] for d in X)} ; jackpots {sum(1 for d in X if jk(d))} ({f0(sum(d['pn'] for d in X if jk(d)))}) ; "
            f"pertes {sum(1 for d in X if d['pn'] < 0)} ({f0(sum(d['pn'] for d in X if d['pn'] < 0))}).", ""]
    Y = sorted(X, key=lambda d: -d["pn"])[:8]
    out += ["Les plus gros gains que D aurait sacrifiés :", "", "| Cycle | Côté | Prix | Avantage | Valeurs Chainlink depuis la naissance | Indépendant du dernier mouvement | Résultat |", "|---|---|---|---|---|---|---|"]
    for d in Y: out.append(f"| {hs(d['t'])} | {'Up' if d['up'] else 'Down'} | {d['a']:.2f} | {d['edge']:.2f} | {d['ncl']} | {'oui' if d['indep'] else 'non'} | {f0(d['pn'])} |")
    # concentration
    s = sorted([d["pn"] for d in A], reverse=True)
    out += ["", f"Concentration ({g}) : les 5 plus gros gains de A font {f0(sum(s[:5]))}, les 10 plus gros {f0(sum(s[:10]))}, pour un total de {f0(tA)}.", ""]
open("etude/bot5min/resultat_refuses_BCD.md", "w").write("\n".join(out)); print("\n".join(out))
