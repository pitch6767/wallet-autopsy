"""Test unique demandé par Pitch (10.10.2026 11:19) : un avantage de 20-30 pts, confirmé par 2 nouvelles valeurs Chainlink reçues avant l'achat
et encore positif sans le dernier mouvement des exchanges, garde-t-il son avantage ? Politiques comparées sur les MÊMES premières opportunités E :
A = tous les premiers signaux E (référence) ; B = avantage 20-30 pts ; C = B + ≥ 2 nouvelles valeurs Chainlink depuis la naissance du désaccord ;
D = C + avantage encore > 0 sans le mouvement des 2 dernières secondes. Chaque propriété seule aussi. Variante « attendre » : acheter au premier instant
du cycle où les trois conditions sont réunies (peut être plus tard que le premier signal). Baisse modérée (10-30 c en 3 s) : apporte-t-elle quelque chose ?
Aucune donnée future dans les décisions. Diagnostic seulement."""
import sys
sys.path.insert(0, "etude/bot5min")
exec(open("etude/bot5min/contrefactuel.py").read().split("SIGS = {}")[0])
MATIN0 = 1791620700          # 10.10 10:25 heure suisse : fin des données utilisées par les études précédentes (contrefactuel.py)
per2 = lambda st: "apprentissage" if st < CUT else ("validation" if st < NUIT0 else ("nuit et matinée 10.10 (déjà explorées)" if st < MATIN0 else "après 10.10 10:25 (jamais utilisé)"))
PER = ("apprentissage", "validation", "nuit et matinée 10.10 (déjà explorées)", "après 10.10 10:25 (jamais utilisé)")
FIRST, WAIT = {}, {}
for st in valides:
    R = C[st]; T_ = [r[0] for r in R]; y = O[f"BTC:{st}"]["gagnant"] == "Up"; end = st + 300; hist = []
    for r in R:
        t = r[0]; tl = end - t
        if tl > 95 or tl < 20: continue
        c0 = coeur(st, t); p0 = prob(c0) if c0 else None
        hist.append((t, p0, r[4], r[6], der("cl", t)))
        if tl > 90 or p0 is None or (st in FIRST and st in WAIT): continue
        for up in (True, False):
            a = r[4] if up else r[6]; z = (r[8] if up else r[10]) or 0
            if a is None or not (0.02 <= a <= 0.98) or z <= 0: continue
            pr = p0 if up else 1 - p0
            if pr - a < 0.20: continue
            sd_ = lambda x: x if up else 1 - x
            naiss = None
            for h in reversed(hist[:-1]):
                ah = h[2] if up else h[3]
                if h[1] is None or ah is None: continue
                if sd_(h[1]) - ah < 0.05: naiss = h[0]; break
            vals = [h[4] for h in hist if naiss is not None and h[0] > naiss and h[4] is not None]
            ncl = len(set(vals)) - 1 if vals else 0                    # nouvelles valeurs reçues depuis la naissance (avant l'instant t)
            c2 = coeur(st, t - 2); pnc = sd_(prob(c0, c2["S"])) if c2 else pr
            h3 = [h for h in hist if h[0] <= t - 3]; a3 = ((h3[-1][2] if up else h3[-1][3]) if h3 else None)
            gm = y if up else not y; q = min(50 / a, z)
            d = dict(st=st, up=up, gm=gm, a=a, edge=pr - a, ncl=ncl, indep=(pnc - a) > 0, baisse=(a3 - a) if a3 is not None else None,
                     it=(q * ((1 if gm else 0) - a - FEE(a)), q * a, gm), t=t)
            if st not in FIRST: FIRST[st] = d
            if st not in WAIT and 0.20 <= d["edge"] < 0.30 and ncl >= 2 and d["indep"]: WAIT[st] = d
            break
def stats(L_, ref=None):
    if not L_: return "0 | — | — | — | — | —"
    pn = [l["it"][0] for l in L_]; cum = pk = cr = 0.0
    for v in pn: cum += v; pk = max(pk, cum); cr = min(cr, cum - pk)
    return f"{len(L_)} | {100 * sum(l['gm'] for l in L_) / len(L_):.0f} % | **{f0(sum(pn))}** | {f0(cr)} | {sum(1 for l in L_ if l['it'][0] >= 4 * l['it'][1])}"
B_ = lambda d: 0.20 <= d["edge"] < 0.30
POL = [("A — tous les premiers signaux E (référence)", lambda d: True), ("B — avantage 20-30 pts", B_),
       ("C — B + ≥ 2 nouvelles valeurs Chainlink", lambda d: B_(d) and d["ncl"] >= 2), ("D — C + avantage > 0 sans le dernier mouvement", lambda d: B_(d) and d["ncl"] >= 2 and d["indep"]),
       ("propriété seule : ≥ 2 valeurs Chainlink", lambda d: d["ncl"] >= 2), ("propriété seule : indépendant du dernier mouvement", lambda d: d["indep"])]
out = [f"# Une hypothèse, un test : la combinaison D — BTC, {len(valides)} cycles ({hs(valides[0])} → {hs(valides[-1] + 300)})", "",
       f"Mêmes premières opportunités E pour toutes les politiques. Apprentissage < {hs(CUT)} ; validation < {hs(NUIT0)} ; nuit et matinée < {hs(MATIN0)} ; **après {hs(MATIN0)} : jamais utilisé dans aucune étude**.", "",
       "Colonnes : achats | gagnés | résultat net | creux | jackpots (≥ 4 × la mise).", ""]
for g in PER:
    F_ = [d for st, d in FIRST.items() if per2(st) == g]
    out += [f"## {g} — {len(F_)} premières opportunités", "", "| Politique | Achats | Gagnés | Résultat | Creux | Jackpots | Pertes évitées vs A | Gains sacrifiés vs A (dont jackpots) |", "|---|---|---|---|---|---|---|---|"]
    for nom, f in POL:
        S_ = [d for d in F_ if f(d)]; X_ = [d for d in F_ if not f(d)]
        ev = sum(-d["it"][0] for d in X_ if d["it"][0] < 0); sa = sum(d["it"][0] for d in X_ if d["it"][0] > 0); js = sum(1 for d in X_ if d["it"][0] >= 4 * d["it"][1])
        out.append(f"| {nom} | {stats(S_)} | {f0(ev)} | {f0(sa)} ({js}) |")
    W_ = [d for st, d in WAIT.items() if per2(st) == g]
    out.append(f"| D attendu : acheter au premier instant où les 3 conditions sont réunies | {stats(W_)} | — | — |")
    out.append("")
# baisse moderee
out += ["## La baisse modérée de 10 à 30 c en 3 s apporte-t-elle une information en plus ?", "",
        "| Groupe (toutes périodes hors apprentissage) | Achats | Gagnés | Résultat | Creux | Jackpots |", "|---|---|---|---|---|---|"]
HA = [d for st, d in FIRST.items() if per2(st) != "apprentissage"]; TA = [d for st, d in FIRST.items() if per2(st) == "apprentissage"]
mod = lambda d: d["baisse"] is not None and 0.10 <= d["baisse"] < 0.30
D_ = lambda d: B_(d) and d["ncl"] >= 2 and d["indep"]
for nom, f in (("baisse modérée — tous", mod), ("baisse modérée ET les 3 propriétés (D)", lambda d: mod(d) and D_(d)),
               ("baisse modérée SANS les 3 propriétés", lambda d: mod(d) and not D_(d)), ("D sans baisse modérée", lambda d: D_(d) and not mod(d))):
    out.append(f"| {nom} | {stats([d for d in HA if f(d)])} |")
out += ["", "Même tableau sur l'apprentissage :", "", "| Groupe | Achats | Gagnés | Résultat | Creux | Jackpots |", "|---|---|---|---|---|---|"]
for nom, f in (("baisse modérée — tous", mod), ("baisse modérée ET D", lambda d: mod(d) and D_(d)), ("baisse modérée SANS D", lambda d: mod(d) and not D_(d)), ("D sans baisse modérée", lambda d: D_(d) and not mod(d))):
    out.append(f"| {nom} | {stats([d for d in TA if f(d)])} |")
corr_ = np.corrcoef([[1.0 if B_(d) else 0.0, 1.0 if d["ncl"] >= 2 else 0.0, 1.0 if d["indep"] else 0.0, 1.0 if mod(d) else 0.0] for d in FIRST.values()], rowvar=False)
out += ["", "Corrélation entre les propriétés (toutes opportunités) : 20-30 pts / ≥ 2 Chainlink / indépendant / baisse modérée :", ""]
labs = ["20-30 pts", "≥ 2 Chainlink", "indépendant", "baisse modérée"]
out += ["| | " + " | ".join(labs) + " |", "|---|---|---|---|---|"] + [f"| {labs[i]} | " + " | ".join(f"{corr_[i, j]:+.2f}" for j in range(4)) + " |" for i in range(4)]
open("etude/bot5min/resultat_combinaison_D.md", "w").write("\n".join(out)); print("\n".join(out))
json.dump({str(st): dict(per=per2(st), up=d["up"], gm=d["gm"], a=d["a"], edge=d["edge"], ncl=d["ncl"], indep=d["indep"], baisse=d["baisse"], pn=d["it"][0], mise=d["it"][1], t=d["t"])
           for st, d in FIRST.items()}, open("etude/bot5min/combinaison_D_opportunites.json", "w"), indent=0)
