"""BOT95 — H1053 : FILTRE DE CONSENSUS pour les stratégies BTC gagnantes du 12.10 (Pitch, 12.10.2026 18:57 : « on reprend les stratégies qui
gagnent aujourd'hui et on cherche comment les améliorer, c'est-à-dire réduire le nombre de perdantes surtout »).
PROTOCOLE PRÉ-ENREGISTRÉ (ce fichier tel que committé le 12.10.2026 ~19:20 heure suisse). Hors ligne ; aucun ordre ; aucune stratégie ni fantôme
modifié ; aucun nouveau fantôme sans accord de Pitch.

DONNÉES : trades du bot Cloudflare (bot95/sauvegarde/*_BTC.json, rafraîchi par sauvegarde_go.txt) : heure de décision, côté, prix, parts, P&L,
  probabilité du modèle, temps restant. Chaque trade est ramené à une mise de 10 $ (P&L × 10 / coût).
STRATÉGIES : les 10 meilleures BTC du 12.10 (liste figée ci-dessous).
VARIABLE : « consensus » = nombre d'AUTRES stratégies BTC du bot (toutes, pas seulement les 10) qui ont déjà acheté le MÊME côté dans le même cycle
  au moment de la décision (heure ≤ heure du trade). Connu en direct par le bot.
EXPLORATION (faite le 12.10, documentée dans le rapport) : sur 08.10 → 12.10 12:00 UTC, 7 175 trades, la base fait −1 864 $ (10 $ par trade) ;
  garder seulement les trades avec consensus ≥ 8 et ≥ 120 s restantes fait +3 642 $ (IC 90 % par cycles de l'écart [+998 ; +9 800]),
  positif pour 8 stratégies sur 10 ; l'effet est régulier pour des seuils de 6 à 10. Le taux de perdants baisse peu (77 % → 75 %) : le filtre
  réduit surtout le NOMBRE de trades perdants (5 557 → ~2 500) et la perte totale. Plusieurs règles ont été regardées (environ 180 seuils sur
  10 variables, et l'après-midi du 12.10 a été vu) : ce résultat est une hypothèse, pas une preuve.
RÈGLES FIGÉES (aucun changement après ce commit) :
  K2 (principale) : garder si consensus ≥ 8 ET temps restant ≥ 120 s.
  K1 : consensus ≥ 8.   K3 : consensus ≥ 6 ET temps restant ≥ 120 s.   K4 : consensus ≥ 10 ET temps restant ≥ 120 s.
TEST : cycles ≥ 13.10.2026 00:00 UTC (jamais vus), jusqu'à l'export du jour du calcul.
CRITÈRE : K2 est confirmée si, sur le test, l'écart de P&L avec la base (somme des 10 stratégies, 10 $ par trade) a un IC 90 % par cycles
  entièrement > 0, que le nombre de trades perdants baisse, et que l'écart est positif pour au moins 6 stratégies sur 10. Les autres règles sont
  rapportées sans verdict (IC corrigé pour 4 comparaisons). Une confirmation ne vaut pas mise en production : Claude propose, Pitch décide.
Usage : python3 etude/bot5min/consensus_h1053.py [--depuis AAAA-MM-JJ]"""
import os, sys, json, glob, datetime, collections, time
import numpy as np

ICI = os.path.dirname(os.path.abspath(__file__)); SAUV = os.path.join(ICI, "..", "..", "bot95", "sauvegarde")
TEST = 1791849600; RNG = np.random.default_rng(1053)
TOP = ["V2-F + pas les deux baissent BTC", "V2-D perp 120-269 s BTC", "V2-F + plus de 120 s BTC", "V2-C perp BTC", "V2-G jury des bourses BTC",
       "V2-F ecart qui grandit BTC", "V2-B hors 60-89 s BTC", "V2-H veto complet BTC", "desaccord 20 Binance ou perp avec nous BTC", "desaccord 20 sans nuit BTC"]
REGLES = {"K2 consensus ≥ 8 et ≥ 120 s": lambda d: d["same"] >= 8 and d["rest"] >= 120, "K1 consensus ≥ 8": lambda d: d["same"] >= 8,
          "K3 consensus ≥ 6 et ≥ 120 s": lambda d: d["same"] >= 6 and d["rest"] >= 120, "K4 consensus ≥ 10 et ≥ 120 s": lambda d: d["same"] >= 10 and d["rest"] >= 120}


def charger():
    rows = []
    for f in glob.glob(os.path.join(SAUV, "*_BTC.json")):
        d = json.load(open(f)); nom = d.get("nom")
        for t in (d.get("trades") or {}).values():
            if not isinstance(t, dict) or any(t.get(k) is None for k in ("net", "heure", "start", "cote", "prix", "restant_s", "parts")): continue
            ts = datetime.datetime.fromisoformat(t["heure"].replace("Z", "+00:00")).timestamp()
            rows.append(dict(nom=nom, st=t["start"], ts=ts, cote=t["cote"], prix=t["prix"], parts=t["parts"], net=t["net"], rest=t["restant_s"]))
    byc = collections.defaultdict(list)
    for r in rows: byc[r["st"]].append(r)
    D = []
    for r in rows:
        if r["nom"] not in TOP: continue
        cost = r["parts"] * r["prix"]
        if cost <= 0: continue
        same = len({x["nom"] for x in byc[r["st"]] if x["cote"] == r["cote"] and x["ts"] <= r["ts"] and x["nom"] != r["nom"]})
        D.append(dict(nom=r["nom"], st=r["st"], pnl=10 * r["net"] / cost, los=r["net"] < 0, rest=r["rest"], same=same))
    return D


def ic(g, v, alpha=0.10, B=4000):
    g = np.asarray(g); v = np.asarray(v, float); U, inv = np.unique(g, return_inverse=True)
    if len(U) < 3: return (float("nan"), float("nan"))
    S = np.bincount(inv, v); idx = RNG.integers(0, len(U), (B, len(U))); m = S[idx].sum(1)
    return float(np.percentile(m, 100 * alpha / 2)), float(np.percentile(m, 100 * (1 - alpha / 2)))


def main():
    o = []; w = o.append; D = charger()
    w(f"# Bot95 — H1053 : filtre de consensus sur les gagnantes du 12.10\n\nGénéré le {time.strftime('%d.%m.%Y %H:%M', time.gmtime())} UTC. Mise ramenée à 10 $ par trade. Aucun ordre.\n")
    for lab, S in (("Exploration (avant le 13.10, déjà vue)", [d for d in D if d["st"] < TEST]), ("TEST (≥ 13.10, jamais vu)", [d for d in D if d["st"] >= TEST])):
        w(f"## {lab} — {len(S)} trades, base {sum(d['pnl'] for d in S):+.0f} $, {sum(d['los'] for d in S)} perdants\n")
        if not S: continue
        w("| Règle | Trades gardés | P&L gardé ($) | Perdants gardés | Taux de perdants | Écart avec la base ($) | IC 90 % | IC corrigé (4) | Stratégies améliorées |\n|---|---|---|---|---|---|---|---|---|")
        g = [d["st"] for d in S]
        for k, f in REGLES.items():
            K = [d for d in S if f(d)]; dv = [0.0 if f(d) else -d["pnl"] for d in S]; c1 = ic(g, dv); c2 = ic(g, dv, 0.10 / 4)
            amel = sum(1 for n in TOP if sum((0.0 if f(d) else -d["pnl"]) for d in S if d["nom"] == n) > 0)
            w(f"| {k} | {len(K)} / {len(S)} | {sum(d['pnl'] for d in K):+.0f} | {sum(d['los'] for d in K)} / {sum(d['los'] for d in S)} | "
              f"{100 * np.mean([d['los'] for d in K]) if K else 0:.0f} % (base {100 * np.mean([d['los'] for d in S]):.0f} %) | {sum(dv):+.0f} | [{c1[0]:+.0f} ; {c1[1]:+.0f}] | "
              f"[{c2[0]:+.0f} ; {c2[1]:+.0f}] | {amel} / 10 |")
        w("\n| Stratégie | Base ($) | K2 ($) | Écart | Perdants base → K2 |\n|---|---|---|---|---|")
        f = REGLES["K2 consensus ≥ 8 et ≥ 120 s"]
        for n in TOP:
            Sn = [d for d in S if d["nom"] == n]; Kn = [d for d in Sn if f(d)]
            w(f"| {n} | {sum(d['pnl'] for d in Sn):+.0f} | {sum(d['pnl'] for d in Kn):+.0f} | {sum(d['pnl'] for d in Kn) - sum(d['pnl'] for d in Sn):+.0f} | "
              f"{sum(d['los'] for d in Sn)} → {sum(d['los'] for d in Kn)} |")
        if lab.startswith("TEST"):
            dv = [0.0 if f(d) else -d["pnl"] for d in S]; c1 = ic(g, dv); Kc = sum(1 for n in TOP if sum((0.0 if f(d) else -d["pnl"]) for d in S if d["nom"] == n) > 0)
            ok = c1[0] > 0 and sum(d["los"] for d in S if f(d)) < sum(d["los"] for d in S) and Kc >= 6
            w(f"\n**Verdict K2 : {'CONFIRMÉE' if ok else 'non confirmée'}** (IC [{c1[0]:+.0f} ; {c1[1]:+.0f}], {Kc} stratégies sur 10 améliorées).\n")
        w("")
    p = os.path.join(ICI, "resultat_consensus_h1053.md"); open(p, "w").write("\n".join(o)); print("\n".join(o))


if __name__ == "__main__":
    main()
