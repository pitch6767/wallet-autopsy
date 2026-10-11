"""BOT95 — Audit des données (section 3) + H712 INVENTORY TILT ATTRIBUTION + H714 TILT LEAD-TIME + H718 (décomposition gagnants / perdants).
Mission de Pitch du 11.10.2026 16:14. Lecture seule, hors ligne, aucun ordre, aucun fantôme modifié. Période réservée (≥ 13.10.2026 00:00 UTC) exclue.
Inventaire de chaque portefeuille reconstruit chronologiquement (achats, ventes ; ventes sans achat visible = jetons séparés, 1 $ la paire).
Penchant (tilt) = (Up − Down) / (Up + Down) à 30, 60, …, 270 s et avant le règlement. Référence de marché = prix de la dernière transaction Up
avant l'instant (prix implicite Polymarket, connu à cet instant). Valeur ÉCONOMIQUE du penchant à t = position résiduelle × (résultat − prix implicite
à t) : c'est ce que le penchant rapporte AU-DELÀ du marché à cet instant (0 en espérance pour un penchant sans information). Témoin : même
portefeuilles, penchant tiré au hasard (même taille de position résiduelle, sens aléatoire).
Méthode d'appariement (documentée) : appariement global par marché, coût moyen par côté (pas de FIFO) ; paires = min(Up, Down) ; résiduel = le reste.
Usage : python3 etude/bot5min/tilt_makers.py makers_suivi.json → etude/bot5min/resultat_tilt_makers.md"""
import json, os, sys, collections, time, random, bisect
import numpy as np

ICI = os.path.dirname(os.path.abspath(__file__)); SORTIE = os.path.join(ICI, "resultat_tilt_makers.md"); HORS_ECH = 1791849600
INST = [30, 60, 90, 120, 150, 180, 210, 240, 270, 299]
random.seed(12)


def ic_blocs(v, n=2000):
    v = np.array(v, dtype=float)
    if len(v) < 5: return None
    rng = np.random.default_rng(5); b = [v[rng.integers(0, len(v), len(v))].mean() for _ in range(n)]
    return np.percentile(b, [5, 95])


def audit(base, M):
    o = []; w = o.append
    n = len(M); tr = [st for st, mk in M.items() if mk.get("tronque")]; lim = [st for st, mk in M.items() if not mk.get("tronque") and mk["n"] >= 4000]
    tot = sum(mk["n"] for mk in M.values())
    dup = 0; incoh = 0; hors = 0; seconds = []
    for st, mk in M.items():
        vu = collections.Counter(tuple(x) for x in mk["ex"]); dup += sum(c - 1 for c in vu.values() if c > 1)
        for wal, role, out, side, sz, p, ts in mk["ex"]:
            if not (0 < p < 1) or sz <= 0 or out not in ("Up", "Down") or side not in ("BUY", "SELL"): incoh += 1
            if not (st - 600 <= ts <= st + 900): hors += 1
        P = sum(1 for x in mk["ex"] if x[1] == "P"); Mk = sum(1 for x in mk["ex"] if x[1] == "M")
        seconds.append((P, Mk))
    w("## 1. Audit des données collectées\n")
    w(f"- Marchés collectés (avant la période réservée) : **{n}**, du {time.strftime('%d.%m %H:%M', time.gmtime(min(M)))} au {time.strftime('%d.%m %H:%M', time.gmtime(max(M)))} UTC.")
    w(f"- Marchés complets (< 10 000 exécutions) : **{n - len(tr)}** ; encore tronqués (≥ 10 000, plafond de l'API) : **{len(tr)}** — isolés, exclus des résultats.")
    w(f"- Dont marchés entre 4 000 et 10 000 exécutions (récupérés grâce au nouveau plafond) : {len(lim)}.")
    w(f"- Exécutions : {tot} ; doublons exacts : {dup} ; valeurs incohérentes (prix, taille, issue, côté) : {incoh} ; horodatages hors du marché (±10 min) : {hors}.")
    pm = [P for P, Mk in seconds]; mm = [Mk for P, Mk in seconds]
    w(f"- Rôles : {sum(pm)} lignes preneur, {sum(mm)} lignes maker (un même preneur peut être servi par plusieurs makers).")
    w("- Horodatages : à la seconde (API Data). Jetons : issue « Up » / « Down » lue dans chaque exécution ; gagnant lu dans Gamma (prix final 1).")
    A = base.get("activites", {})
    if A:
        ty = collections.Counter(e["type"] for L in A.values() for e in L)
        w(f"- Activité lue pour {len(A)} portefeuilles : " + ", ".join(f"{k} {v}" for k, v in ty.most_common()) + ".")
    else:
        w("- Activité (fusions, séparations, règlements, récompenses) : pas encore lue dans ce fichier.")
    w("- Au-delà de 10 000 exécutions : aucune pagination supplémentaire de l'API Data ; seule une reconstruction par la blockchain (sous-graphe OrderFilled, refusé pour l'instant : 429) le permettrait.")
    w("- Une réponse de 10 000 lignes n'est jamais supposée complète (marché marqué tronqué).\n")
    return o


def prix_implicite(mk):
    """série (ts, prix Up) des transactions preneuses, pour connaître le prix du marché à chaque instant (sans information future)"""
    L = []
    for wal, role, out, side, sz, p, ts in mk["ex"]:
        if role != "P": continue
        L.append((ts, p if out == "Up" else 1 - p))
    L.sort(); return [x[0] for x in L], [x[1] for x in L]


def inventaire(ex, jusqua):
    """Up, Down, coûts, à l'instant jusqua (exécutions au plus tard à cet instant)"""
    q = {"Up": 0.0, "Down": 0.0}; c = {"Up": 0.0, "Down": 0.0}; court = {"Up": 0.0, "Down": 0.0}
    for ts, role, out, side, sz, p in ex:
        if ts > jusqua: break
        if side == "BUY": q[out] += sz; c[out] += sz * p
        else:
            x = min(sz, q[out]); pm = c[out] / q[out] if q[out] > 1e-9 else 0
            q[out] -= x; c[out] -= x * pm
            if sz > x: court[out] += sz - x
    # jetons séparés : l'autre jambe de la séparation est détenue
    sep = max(court["Up"], court["Down"])
    if sep > 0: q["Up"] += sep - court["Up"]; q["Down"] += sep - court["Down"]
    return q, c


def main():
    base = json.load(open(sys.argv[1]))
    M = {int(k): v for k, v in base["marches"].items() if int(k) < HORS_ECH}
    o = ["# Bot95 — Penchant de l'inventaire des makers (H712, H714, H718) — PRÉLIMINAIRE\n",
         f"Généré le {time.strftime('%d.%m.%Y %H:%M', time.gmtime())} UTC. FAITS : exécutions de l'API Data. INFÉRENCES : interprétation. Aucune valeur future n'entre dans le penchant ni dans le prix de référence.\n"]
    o += audit(base, M)
    w = o.append
    OK = {st: mk for st, mk in M.items() if not mk.get("tronque")}
    # portefeuilles makers et leur rentabilité (comptée sur les marchés complets)
    W = collections.defaultdict(list)
    for st, mk in OK.items():
        for wal, role, out, side, sz, p, ts in mk["ex"]: W[(wal, st)].append((ts, role, out, side, sz, p))
    vol = collections.Counter(); volM = collections.Counter(); pnl = collections.Counter(); nm = collections.defaultdict(set)
    coupe = sorted(OK)[len(OK) // 2]                                          # classement gagnant / perdant sur la 1re moitié, mesure sur la 2e
    for (wal, st), ex in W.items():
        ex.sort()
        if st >= coupe: continue
        g = OK[st]["gagnant"]
        for ts, role, out, side, sz, p in ex:
            win = 1.0 if out == g else 0.0; vol[wal] += sz * p
            if role == "M": volM[wal] += sz * p
            pnl[wal] += sz * (win - p) if side == "BUY" else sz * (p - win)
            if role == "P": pnl[wal] -= sz * 0.07 * p * (1 - p)
            nm[wal].add(st)
    makers = [x for x in volM if len(nm[x]) >= 10 and volM[x] >= 0.7 * vol[x] and vol[x] >= 2500]
    gagn = {x for x in makers if pnl[x] / vol[x] >= 0.01}; perd = {x for x in makers if pnl[x] / vol[x] <= -0.005}
    w(f"## 2. Penchant de l'inventaire au fil du cycle (H712)\n")
    w(f"Makers retenus (≥ 10 marchés complets, ≥ 70 % de volume maker, ≥ 2 500 $ sur la 1re moitié) : {len(makers)} ; gagnants (≥ +1 %/$) : {len(gagn)} ; perdants (≤ −0,5 %/$) : {len(perd)}. "
      f"**Classement fait sur la 1re moitié chronologique des marchés (avant le {time.strftime('%d.%m %H:%M', time.gmtime(coupe))} UTC), penchant mesuré sur la 2e moitié uniquement** "
      "(sinon « gagnant » et « bon penchant » seraient la même chose).\n")
    PI = {st: prix_implicite(mk) for st, mk in OK.items()}
    R = collections.defaultdict(lambda: collections.defaultdict(list))     # groupe → instant → [(précision, valeur éco par $ de capital résiduel, taille résiduelle)]
    LEAD = collections.defaultdict(list)
    for (wal, st), ex in W.items():
        if st < coupe: continue
        grp = "gagnants" if wal in gagn else ("perdants" if wal in perd else ("autres makers" if wal in makers else None))
        if grp is None: continue
        g = OK[st]["gagnant"]; Tts, Tp = PI[st]
        if not Tts: continue
        premier_bon = None; favori_bon = None
        for t in INST:
            q, c = inventaire(ex, st + t)
            tot = q["Up"] + q["Down"]
            if tot < 1e-9: continue
            tilt = (q["Up"] - q["Down"]) / tot; resid = abs(q["Up"] - q["Down"])
            i = bisect.bisect_right(Tts, st + t) - 1
            if i < 0 or resid < 1e-9: continue
            pu = Tp[i]; cote = "Up" if tilt > 0 else "Down"; p_cote = pu if cote == "Up" else 1 - pu
            win = 1.0 if g == cote else 0.0
            val = resid * (win - p_cote)                                    # gain du résiduel AU-DELÀ du prix du marché à t
            R[grp][t].append((win, val, resid * p_cote))
            # témoin : même résiduel, sens tiré au hasard
            cr = random.choice(("Up", "Down")); pr = pu if cr == "Up" else 1 - pu
            R["témoin (sens au hasard)"][t].append((1.0 if g == cr else 0.0, resid * ((1.0 if g == cr else 0.0) - pr), resid * pr))
            if premier_bon is None and win == 1.0 and abs(tilt) >= 0.2: premier_bon = t
            if favori_bon is None and ((pu > 0.5) == (g == "Up")): favori_bon = t
        if premier_bon is not None and favori_bon is not None: LEAD[grp].append(premier_bon - favori_bon)
    w("Précision = part des cycles où le côté surpondéré à t est le gagnant final. Valeur au-delà du marché = Σ résiduel × (résultat − prix implicite à t) / Σ capital résiduel au prix de t "
      "(0 attendu sans information ; >0 = le penchant anticipe mieux que le prix du marché à ce moment).\n")
    w("| Groupe | " + " | ".join(f"{t} s" for t in INST) + " |\n|---|" + "---|" * len(INST))
    for grp in ("gagnants", "perdants", "autres makers", "témoin (sens au hasard)"):
        cells = []
        for t in INST:
            L = R[grp][t]
            if not L: cells.append("—"); continue
            prec = np.mean([x[0] for x in L]); v = sum(x[1] for x in L) / max(sum(x[2] for x in L), 1e-9)
            cells.append(f"{100 * prec:.0f} % / {100 * v:+.1f} %")
        w(f"| {grp} | " + " | ".join(cells) + " |")
    w("\n(chaque case : précision / valeur au-delà du marché par $ de résiduel)\n")
    w("**Valeur au-delà du marché pondérée par le capital, intervalles à 90 % (rééchantillonnage) à 60, 120 et 240 s** :\n")
    for grp in ("gagnants", "perdants", "témoin (sens au hasard)"):
        parts = []
        for t in (60, 120, 240):
            L = R[grp][t]
            if len(L) < 5: parts.append(f"{t} s : —"); continue
            a = np.array([x[1] for x in L]); b = np.array([x[2] for x in L]); rng = np.random.default_rng(5)
            bs = [a[idx].sum() / max(b[idx].sum(), 1e-9) for idx in (rng.integers(0, len(a), len(a)) for _ in range(1000))]
            parts.append(f"{t} s : {100 * a.sum() / b.sum():+.1f} % [{100 * np.percentile(bs, 5):+.1f} ; {100 * np.percentile(bs, 95):+.1f}]")
        w(f"- {grp} : " + " ; ".join(parts))
    w("\n## 3. Avance du penchant sur le marché (H714)\n")
    w("Délai = premier instant où le penchant (|tilt| ≥ 0,2) est du côté gagnant − premier instant où le favori du marché (prix implicite > 0,5) est le gagnant. "
      "Négatif = le portefeuille était du bon côté AVANT que le marché le donne favori. Distribution (p10 / p25 / médiane / p75 / p90) en secondes.\n")
    for grp in ("gagnants", "perdants", "autres makers"):
        L = LEAD.get(grp, [])
        if L: w(f"- {grp} ({len(L)} portefeuille-marchés) : {' / '.join(f'{x:.0f}' for x in np.percentile(L, [10, 25, 50, 75, 90]))} ; part négative (avance) {100 * np.mean([x < 0 for x in L]):.0f} %, nulle {100 * np.mean([x == 0 for x in L]):.0f} %")
    w("\nLimite : seuls le prix Polymarket et le résultat sont disponibles pour tous les marchés ; la probabilité Bot95, la distance Chainlink et le BTC ne le sont que pour les cycles enregistrés à Dublin (étude séparée).\n")
    open(SORTIE, "w").write("\n".join(o)); print("\n".join(o))


if __name__ == "__main__":
    main()
