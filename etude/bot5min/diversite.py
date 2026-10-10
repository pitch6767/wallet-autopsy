"""Diversité : stratégies éliminées et variations de paramètres, pour « avoir une idée » (demande de Pitch 10.10.2026 14:00-14:02).
Pas d'optimisation : une dimension à la fois, autour des règles existantes. Jugé à 0 s ET à 0,5 s de délai (leçon de l'attribution 0,01 %).
Mesure de diversité : corrélation, cycle par cycle, avec V2-F 0,01 % (moteur du bot, H1) et avec V2-F original."""
import sys
sys.path.insert(0, "etude/bot5min")
exec(open("etude/bot5min/attribution_001.py").read().split("cyc = {p:")[0])
def premier(st, regle):
    """premier instant du cycle où regle(r, up, fair, a, tl) est vraie (modèle du bot enregistré)"""
    R_ = C[st]; end = st + 300
    for i, r in enumerate(R_):
        tl = end - r[0]
        if tl < 5: break
        for up in (True, False):
            a = r[4] if up else r[6]
            if a is None or not (0.02 <= a <= 0.98): continue
            fair = r[2] if up else 1 - r[2]
            res = regle(r, up, fair, a, tl)
            if res: return dict(i=i, t=r[0], up=(up if res is True else not up), a=(a if res is True else (r[6] if up else r[4])), tl=tl)
    return None
VAR = [("seuil", "désaccord ≥ 0,10", lambda r, up, f, a, tl: f - a >= 0.10),
       ("seuil", "désaccord ≥ 0,15", lambda r, up, f, a, tl: f - a >= 0.15),
       ("seuil", "désaccord ≥ 0,20 (désaccord 20)", lambda r, up, f, a, tl: f - a >= 0.20),
       ("seuil", "désaccord ≥ 0,30", lambda r, up, f, a, tl: f - a >= 0.30),
       ("temps", "désaccord 20, plus de 180 s", lambda r, up, f, a, tl: f - a >= 0.20 and tl > 180),
       ("temps", "désaccord 20, 60-180 s", lambda r, up, f, a, tl: f - a >= 0.20 and 60 < tl <= 180),
       ("temps", "désaccord 20, moins de 60 s", lambda r, up, f, a, tl: f - a >= 0.20 and tl <= 60),
       ("prix", "désaccord 20, jeton < 0,15", lambda r, up, f, a, tl: f - a >= 0.20 and a < 0.15),
       ("prix", "désaccord 20, jeton 0,15-0,35", lambda r, up, f, a, tl: f - a >= 0.20 and 0.15 <= a < 0.35),
       ("prix", "désaccord 20, jeton 0,35-0,65", lambda r, up, f, a, tl: f - a >= 0.20 and 0.35 <= a < 0.65),
       ("inverse", "inverse désaccord 20 (on suit Polymarket)", lambda r, up, f, a, tl: "inv" if f - a >= 0.20 else False),
       ("favori", "favori de fin : jeton 0,90-0,97, modèle ≥ prix + 3 c, < 90 s", lambda r, up, f, a, tl: 0.90 <= a <= 0.97 and f >= a + 0.03 and tl < 90),
       ("favori", "favori de fin : jeton 0,80-0,90, modèle ≥ prix + 5 c, < 90 s", lambda r, up, f, a, tl: 0.80 <= a < 0.90 and f >= a + 0.05 and tl < 90)]
REF = {"V2-F 0,01 % (H1)": {st: execu(st, SIGV[("H1", st)], 0) for st in valides if ("H1", st) in SIGV},
       "V2-F original": {st: execu(st, SIGV[("O8", st)], 0) for st in valides if ("O8", st) in SIGV}}
vec = lambda D: np.array([(D.get(st) or {}).get("pn", 0.0) for st in valides])
out = ["# Diversité : stratégies éliminées et variations de paramètres — pour avoir une idée", "",
       f"{len(valides)} cycles BTC ({hs(valides[0])} → {hs(valides[-1] + 300)}). Premier signal du cycle, modèle du bot (0,08 %), meilleur vendeur seul, quantité affichée, 50 $ maximum.",
       "Une dimension à la fois autour des règles existantes ; rien n'est optimisé ni activé.", "",
       "| Famille | Variante | Achats | App. 0 s | Hors app. 0 s | Hors app. 0,5 s | Corrélation avec V2-F 0,01 % | avec V2-F original |", "|---|---|---|---|---|---|---|---|"]
for fam, nom, regle in VAR:
    S0 = {st: premier(st, regle) for st in valides}
    D0 = {st: execu(st, s, 0) for st, s in S0.items() if s}; D5 = {st: execu(st, s, 0.5) for st, s in S0.items() if s}
    app = sum(x["pn"] for st, x in D0.items() if x and PER(st) == "apprentissage")
    ho0 = sum(x["pn"] for st, x in D0.items() if x and PER(st) != "apprentissage"); ho5 = sum(x["pn"] for st, x in D5.items() if x and PER(st) != "apprentissage")
    v = vec(D0); c1 = np.corrcoef(v, vec(REF["V2-F 0,01 % (H1)"]))[0, 1]; c2 = np.corrcoef(v, vec(REF["V2-F original"]))[0, 1]
    out.append(f"| {fam} | {nom} | {sum(1 for x in D0.values() if x)} | {f0(app)} | **{f0(ho0)}** | {f0(ho5)} | {c1:+.2f} | {c2:+.2f} |")
for nom, D in REF.items():
    D5 = {st: execu(st, SIGV[("H1" if "0,01" in nom else "O8", st)], 0.5) for st in D}
    out.append(f"| référence | {nom} | {sum(1 for x in D.values() if x)} | {f0(sum(x['pn'] for st, x in D.items() if x and PER(st) == 'apprentissage'))} | **{f0(sum(x['pn'] for st, x in D.items() if x and PER(st) != 'apprentissage'))}** | {f0(sum(x['pn'] for st, x in D5.items() if x and PER(st) != 'apprentissage'))} | — | — |")
out += ["", "Hors app. = validation + inédit (473 cycles environ). Corrélation des résultats cycle par cycle (cycles sans achat = 0), exécution à 0 s."]
open("etude/bot5min/resultat_diversite.md", "w").write("\n".join(out)); print("\n".join(out))
