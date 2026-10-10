"""Bilan des 3 jours des stratégies fantômes figées BTC (tâche programmée du 07.10, exécutée le 10.10). Données : bot95/sauvegarde (trades + archive compacte,
fusion par heure + côté), V1 : bot95/v1_trades.json. Jusqu'à la remise à zéro du 10.10 13:50 (heure suisse)."""
import json, glob, os, collections, time, math, calendar
import numpy as np
RAZ = "2026-10-10T11:50:49"
f0 = lambda x: (f"+{x:,.0f} $" if x >= 0 else f"−{-x:,.0f} $").replace(",", " ")
def charge(f):
    d = json.load(open(f)); T = {}
    for l in d.get("archive") or []: T[f"{l[0]}|{l[1]}"] = (l[0], l[3])
    for k, t in d["trades"].items():
        if t.get("net") is not None: T[k] = (t["heure"], t["net"])
    return sorted(v for v in T.values() if v[0] < RAZ)
STR = [("désaccord 20", "desaccord_20_BTC"), ("désaccord 20 sans nuit", "desaccord_20_sans_nuit_BTC"), ("désaccord confirmé", "desaccord_confirme_BTC"), ("désaccord confirmé + perp", "desaccord_confirme_perp_BTC"),
       ("V2-B hors 60-89 s", "V2-B_hors_60-89_s_BTC"), ("V2-C perp", "V2-C_perp_BTC"), ("V2-D perp 120-269 s", "V2-D_perp_120-269_s_BTC"), ("V2-E persistant", "V2-E_persistant_BTC"),
       ("V2-F écart qui grandit", "V2-F_ecart_qui_grandit_BTC"), ("V2-G jury des bourses", "V2-G_jury_des_bourses_BTC"), ("V2-H veto complet", "V2-H_veto_complet_BTC"),
       ("V5 gain attendu", "V5_gain_attendu_BTC"), ("V6 loterie", "V6_loterie_BTC"), ("assurance 6/9/12", "assurance_6_9_12_BTC"), ("assurance 4/7/10", "assurance_4_7_10_BTC")]
D = {n: charge(f"bot95/sauvegarde/{f}.json") for n, f in STR if os.path.exists(f"bot95/sauvegarde/{f}.json")}
if os.path.exists("bot95/v1_trades.json"):
    V = json.load(open("bot95/v1_trades.json"))["btc"]
    D["V1 (avec stop)"] = sorted((t["heure"], t["net"]) for t in V if t.get("net") is not None and t.get("heure", "") < RAZ)
jour = lambda h: time.strftime("%d.%m", time.gmtime(calendar.timegm(time.strptime(h[:19], "%Y-%m-%dT%H:%M:%S")) + 7200))
out = ["# Bilan des 3 jours — stratégies fantômes figées BTC", "", "Trades réglés jusqu'à la remise à zéro du 10.10 13:50 (heure suisse). Intervalle à 90 % sur le résultat total (dispersion des trades).", "",
       "| Stratégie | Période | Trades | Résultat | Moyen / trade | Intervalle 90 % | Creux max | Part des 5 meilleurs | Sans le meilleur | Sans les 3 | Sans les 5 |", "|---|---|---|---|---|---|---|---|---|---|---|"]
PJ = {}
for n, T in D.items():
    if not T: continue
    x = np.array([v for _, v in T]); tot = x.sum(); sd = x.std(ddof=1) if len(x) > 1 else 0
    cum = np.cumsum(x); dd = float((cum - np.maximum.accumulate(np.concatenate([[0], cum]))[1:]).min()) if len(x) else 0
    s = np.sort(x)[::-1]; g = x[x > 0].sum()
    out.append(f"| {n} | {jour(T[0][0])} → {jour(T[-1][0])} | {len(x)} | **{f0(tot)}** | {x.mean():+.1f} $ | [{f0(tot - 1.645 * sd * math.sqrt(len(x)))} ; {f0(tot + 1.645 * sd * math.sqrt(len(x)))}] | {f0(min(dd, 0))} | "
               f"{100 * s[:5].clip(min=0).sum() / g:.0f} % des gains | {f0(tot - s[:1].sum())} | {f0(tot - s[:3].sum())} | {f0(tot - s[:5].sum())} |")
    pj = collections.defaultdict(float)
    for h, v in T: pj[jour(h)] += v
    PJ[n] = pj
js = sorted({j for p in PJ.values() for j in p}, key=lambda j: (j[3:], j[:2]))
out += ["", "## Résultat par jour (heure suisse)", "", "| Stratégie | " + " | ".join(js) + " |", "|---|" + "---|" * len(js)]
for n, p in PJ.items(): out.append(f"| {n} | " + " | ".join(f0(p[j]) if j in p else "—" for j in js) + " |")
open("etude/bot5min/resultat_bilan3j.md", "w").write("\n".join(out)); print("\n".join(out))
