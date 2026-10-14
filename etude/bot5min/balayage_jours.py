"""Balayage du carnet (parties 8-10 de pression_reglement.py) refait en séparant les jours normaux de la nuit du 10.10 (demande de Pitch).
Même code que pression_reglement.py, appliqué à deux groupes de cycles. Diagnostic seulement : rien n'est modifié ni activé."""
import json, numpy as np, time
from sauvetage import FEE
O = json.load(open("bot95/officiels.json"))
f0 = lambda x: (f"+{x:,.0f} $" if x >= 0 else f"−{-x:,.0f} $").replace(",", " ")
MATIN0 = 1791620700   # 10.10 10:25 heure suisse
TOUT = json.load(open("bot95/twap_carnets.json"))
res = []
for titre, filtre in (("nuit et matinée du 10.10 (avant 10:25)", lambda s_: s_["start"] < MATIN0), ("jours normaux (après le 10.10 10:25)", lambda s_: s_["start"] >= MATIN0)):
    out = []
    # ---------- PARTIE B : carnet 8 niveaux
    out += ["", f"## Balayer le carnet — {titre}", ""]
    try:
        J = [s_ for s_ in TOUT if filtre(s_)]
        vu = {};
        for s_ in sorted(J, key=lambda s_: s_["t0"]):
            if s_["start"] not in vu and (O.get(f"BTC:{s_['start']}") or {}).get("gagnant"): vu[s_["start"]] = s_
        SS = list(vu.values())
        out.append(f"{len(SS)} cycles avec signal et résultat officiel (premier signal TWAP fin du cycle, toutes variantes confondues). Petit échantillon : à lire comme une première mesure.")
        def bal(s_, lim, cap=50.0, snap="0", prud=0.0):
            p = s_["proba"] - prud; gm = O[f"BTC:{s_['start']}"]["gagnant"] == s_["cote"]; q = mi = pn = 0.0
            for pr_, z in s_["asks"].get(snap, []):
                if p - pr_ < lim or mi >= cap: break
                qq = min(z, (cap - mi) / pr_); q += qq; mi += qq * pr_; pn += qq * ((1 if gm else 0) - pr_ - FEE(pr_))
            return pn, mi, gm
        out += ["", "| Politique (50 $ max par cycle) | Cycles achetés | Capital engagé | Résultat | Jackpots |", "|---|---|---|---|---|"]
        def best_only(s_):
            lv = s_["asks"].get("0", [])
            if not lv: return (0, 0, False)
            pr_, z = lv[0]; gm = O[f"BTC:{s_['start']}"]["gagnant"] == s_["cote"]
            if s_["proba"] - pr_ < 0.20: return (0, 0, gm)
            q = min(z, 50 / pr_); return (q * ((1 if gm else 0) - pr_ - FEE(pr_)), q * pr_, gm)
        for nom, f in (("meilleur vendeur seul (actuel)", best_only),
                       ("balayer tant que l'avantage ≥ 20 pts", lambda s_: bal(s_, 0.20)),
                       ("balayer tant que l'avantage ≥ 15 pts", lambda s_: bal(s_, 0.15)),
                       ("balayer tant que l'avantage ≥ 10 pts", lambda s_: bal(s_, 0.10)),
                       ("balayer tant que l'avantage net > 0", lambda s_: bal(s_, 0.0)),
                       ("balayer prudent (proba − 10 pts, avantage ≥ 10 pts)", lambda s_: bal(s_, 0.10, prud=0.10)),
                       ("balayer ≥ 20 pts, jusqu'à 100 $", lambda s_: bal(s_, 0.20, cap=100.0))):
            R_ = [f(s_) for s_ in SS]; R_ = [r for r in R_ if r[1] > 0]
            out.append(f"| {nom} | {len(R_)} | {sum(r[1] for r in R_):.0f} $ | **{f0(sum(r[0] for r in R_))}** | {sum(1 for r in R_ if r[0] >= 4 * r[1])} |")
        cap = {lim: [] for lim in (0.20, 0.10, 0.0)}
        for s_ in SS:
            for lim in cap:
                m_ = sum(min(z, 1e9) * pr_ for pr_, z in s_["asks"].get("0", []) if s_["proba"] - pr_ >= lim); cap[lim].append(m_)
        out += ["", "Idée 62 — capacité totale dans les 8 premiers niveaux au moment du signal (médiane / moyenne, en $) :", ""]
        for lim, v in cap.items(): out.append(f"- avantage ≥ {int(lim * 100)} pts : médiane {np.median(v):.0f} $, moyenne {np.mean(v):.0f} $ ; ≥ 50 $ disponibles dans {sum(1 for x in v if x >= 50)} cycles sur {len(v)}.")
        first = [s_["asks"]["0"][0][1] * s_["asks"]["0"][0][0] for s_ in SS if s_["asks"].get("0")]
        out.append(f"- au seul meilleur vendeur : médiane {np.median(first):.0f} $.")
        # reconstitution (64-67)
        out += ["", "Idées 64-67 — reconstitution : après le signal, le meilleur prix du signal est-il encore disponible (sans tenir compte de notre propre achat, qui n'a pas eu lieu en vrai) ?", "",
                "| Délai | Meilleur vendeur au même prix ou moins cher | Quantité médiane à ce prix ou moins cher | Capacité ≥ 20 pts d'avantage (médiane) |", "|---|---|---|---|"]
        for d_ in ("0.25", "0.5", "1", "2", "5"):
            ok = []; qq = []; cc = []
            for s_ in SS:
                a0 = s_["asks"].get("0"); a1 = s_["asks"].get(d_)
                if not a0 or not a1: continue
                p0 = a0[0][0]; ok.append(a1[0][0] <= p0 + 1e-9); qq.append(sum(z for pr_, z in a1 if pr_ <= p0 + 1e-9))
                cc.append(sum(z * pr_ for pr_, z in a1 if s_["proba"] - pr_ >= 0.20))
            if ok: out.append(f"| {d_} s | {100 * np.mean(ok):.0f} % ({len(ok)}) | {np.median(qq):.0f} jetons | {np.median(cc):.0f} $ |")
        # execution patiente (68)
        pat = []
        for s_ in SS:
            gm = O[f"BTC:{s_['start']}"]["gagnant"] == s_["cote"]; p = s_["proba"]; mi = pn = 0.0
            for snap in ("0", "1", "2"):
                lv = s_["asks"].get(snap) or []
                if not lv: continue
                pr_, z = lv[0]
                if p - pr_ < 0.20 or mi >= 50: continue
                qq = min(z, (50 - mi) / pr_); mi += qq * pr_; pn += qq * ((1 if gm else 0) - pr_ - FEE(pr_))
            if mi > 0: pat.append((pn, mi, gm))
        out.append(f"\nIdée 68 — exécution patiente (meilleur vendeur à 0 s, puis encore au meilleur vendeur à 1 s et 2 s si l'avantage reste ≥ 20 pts, 50 $ max) : {len(pat)} cycles, capital {sum(r[1] for r in pat):.0f} $, résultat **{f0(sum(r[0] for r in pat))}**.")
    except Exception as e:
        out.append(f"(journal des carnets indisponible : {e})")
    res += out
open("etude/bot5min/resultat_balayage_jours.md", "w").write("# Balayage du carnet : jours normaux et nuit du 10.10 séparés\n\nGénéré le " + time.strftime("%d.%m.%Y %H:%M", time.gmtime()) + " UTC.\n" + "\n".join(res)); print("\n".join(res))
