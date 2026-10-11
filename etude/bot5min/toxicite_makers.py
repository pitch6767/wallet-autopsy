"""BOT95 — H695 / Test B « Toxicity Champions » : POURQUOI les makers rentables subissent-ils moins de mauvais remplissages que nos fantômes ?
Demande de Pitch, 11.10.2026 16:02. Lecture seule, hors ligne, aucun ordre, aucun fantôme modifié. Période réservée (≥ 13.10) non lue.
Méthode : chaque transaction preneuse de l'API Data (seconde) est rapprochée de la même transaction enregistrée à Dublin (milliseconde, heure Polymarket),
ce qui date à la milliseconde les remplissages des makers qui l'ont servie, et donne l'état du carnet et des bourses à cet instant.
Pour chaque remplissage maker (portefeuilles réels) et pour chaque remplissage de nos fantômes : sélection adverse à +0,1 / 0,3 / 1 / 3 / 5 / 10 s et au
règlement, puis découpage par explication candidate : au meilleur prix ou plus loin, taille du preneur, balayage de plusieurs niveaux, conditions toxiques
(a/b/c de M4) actives, moment du cycle, prix, écart vendeur-acheteur.
Faits : prix, tailles, heures des remplissages. Inférence : l'explication. L'heure de POSE des ordres des makers reste inconnue (jamais inventée).
Usage : python3 etude/bot5min/toxicite_makers.py makers_suivi.json dossier_cycles → etude/bot5min/resultat_toxicite_makers.md"""
import gzip, json, os, sys, glob, bisect, collections, time
import numpy as np

ICI = os.path.dirname(os.path.abspath(__file__)); RACINE = os.path.abspath(os.path.join(ICI, "..", ".."))
sys.path.insert(0, ICI)
import fast_fenetre as FF, queue_race_phase12 as Q, verifications_h559 as VH, audit_maker as AM
HORS_ECH = 1791849600; SORTIE = os.path.join(ICI, "resultat_toxicite_makers.md")
H = (0.1, 0.3, 1, 3, 5, 10)
mil = lambda p: int(round(p * 1000))


def mid_up(S, t):
    i = np.searchsorted(S[:, 0], t, "right") - 1
    if i < 0 or np.isnan(S[i, 1]) or np.isnan(S[i, 3]): return None
    return (S[i, 1] + S[i, 3]) / 2000.0


def etat(S, t):
    i = np.searchsorted(S[:, 0], t, "left") - 1                        # juste AVANT la transaction
    if i < 0: return None
    return S[i]


def main():
    base = json.load(open(sys.argv[1])); dossier = sys.argv[2]
    MKR = json.load(open(os.path.join(RACINE, "bot95", "rapide_maker.json")))
    # résultats des portefeuilles makers sur toute la base (pour classer rentables / perdants)
    pnl = collections.defaultdict(float); vol = collections.defaultdict(float); nm = collections.defaultdict(set)
    for st, mk in base["marches"].items():
        g = mk["gagnant"]
        for w, role, out, side, sz, p, ts in mk["ex"]:
            if role != "M": continue
            win = 1.0 if out == g else 0.0
            pnl[w] += sz * (win - p) if side == "BUY" else sz * (p - win); vol[w] += sz * p; nm[w].add(st)
    actifs = [w for w in pnl if len(nm[w]) >= 20 and vol[w] >= 5000]
    rentables = {w for w in actifs if pnl[w] / vol[w] >= 0.01}; perdants = {w for w in actifs if pnl[w] / vol[w] <= -0.005}
    REM = []                                                            # remplissages datés à la ms : dict
    ncy = nmatch = ntot = 0
    for fn in sorted(glob.glob(os.path.join(dossier, "**", "*.json.gz"), recursive=True)):
        st = int(os.path.basename(fn).split(".")[0])
        if st >= HORS_ECH or str(st) not in base["marches"]: continue
        C = FF.normaliser(fn); Rj = Q.rejouer(C); S = Rj["serie"]
        if len(S) < 10: continue
        ncy += 1; mk = base["marches"][str(st)]; g = mk["gagnant"]
        R = json.load(gzip.open(fn)); ser = VH.series_cycle(R); DEC = {True: AM.declencheurs(ser, True), False: AM.declencheurs(ser, False)}
        # transactions Dublin indexées par (seconde Polymarket, jeton, côté preneur, prix en millièmes)
        IDX = collections.defaultdict(list)
        for tt in Rj["trades"]:
            if tt[1] is None: continue
            IDX[(int(tt[1] // 1000), tt[2], tt[3], tt[4])].append(tt)
        par_ts = collections.defaultdict(list)
        for x in mk["ex"]: par_ts[x[6]].append(x)
        for ts, L in par_ts.items():
            pren = [x for x in L if x[1] == "P"]; mak = [x for x in L if x[1] == "M"]
            for w, role, out, side, sz, p, _ in pren:
                tok = 0 if out == "Up" else 1; sd = 1 if side == "BUY" else 0; ntot += 1
                cand = [tt for d in (0, -1, 1) for tt in IDX.get((ts + d, tok, sd, mil(p)), []) if abs(tt[5] - sz) <= 0.02 * max(1.0, sz)]
                if not cand: continue
                tt = cand[0]; nmatch += 1; tR = tt[0]
                nb_niveaux = len({x[5] for x in pren if x[0] == w})      # même preneur, plusieurs prix dans la seconde = balayage
                for mw, _, mout, mside, msz, mp, _ in mak:
                    # remplissage maker servi par ce preneur : même issue et côté opposé au même prix, ou autre issue même côté au prix complémentaire
                    lie = (mout == out and mside != side and abs(mp - p) < 1e-9) or (mout != out and mside == side and abs(mp - (1 - p)) < 1e-9)
                    if not lie: continue
                    up_long = (mout == "Up") == (mside == "BUY")           # sens de la position du maker sur Up
                    Sx = etat(S, tR)
                    if Sx is None: continue
                    bb, ba = Sx[1] / 1000, Sx[3] / 1000                    # meilleur acheteur / vendeur Up juste avant
                    prix_up = mp if mout == "Up" else 1 - mp
                    au_meilleur = (abs(prix_up - bb) < 0.0051) if up_long else (abs(prix_up - ba) < 0.0051)
                    m0 = mid_up(S, tR)
                    if m0 is None: continue
                    mo = {}
                    for h in H:
                        m1 = mid_up(S, tR + h * 1000)
                        if m1 is not None: mo[h] = (m1 - prix_up) if up_long else (prix_up - m1)
                    win_up = 1.0 if g == "Up" else 0.0
                    mo["regl"] = (win_up - prix_up) if up_long else (prix_up - win_up)
                    cond = "".join(c for c in "abc" if AM.actif(DEC[up_long][c], tR, 0.0)) or "aucune"
                    REM.append(dict(qui="rentable" if mw in rentables else ("perdant" if mw in perdants else "autre"), w=mw, q=msz, prix=prix_up if up_long else 1 - prix_up,
                                    mo=mo, au_meilleur=au_meilleur, taille_preneur=sz * p, balayage=nb_niveaux > 1, cond=cond, t=(tR / 1000 - st), ecart=(ba - bb) if ba and bb else None))
    # nos fantômes
    NOS = []
    for x in MKR:
        if x.get("type") == "resume" or not x.get("resultat") or x["start"] >= HORS_ECH or x.get("mode") == "preneur": continue
        v = x["variante"]; fam = v.split()[0]
        for ms, k, q in x.get("rempl") or []:
            if k != "p": continue
            a = {h: (x.get("mo") or {}).get("p", {}).get(str(h)) for h in (1, 3, 5, 10)}
            mo = {h: a[h][0] / a[h][1] for h in a if a[h] and a[h][1]}
            mo["regl"] = (1.0 if x.get("gagne") else 0.0) - x["prix"]
            NOS.append(dict(qui="nous " + fam, q=q, mo=mo, prix=x["prix"], au_meilleur=(x.get("acheteurPose") is not None and abs(x["prix"] - (x.get("acheteurPose") or 0)) <= 0.0101)))
    o = []; w = o.append
    w("# Bot95 — Pourquoi les makers rentables évitent les mauvais remplissages (H695, Test B) — PRÉLIMINAIRE\n")
    w(f"Généré le {time.strftime('%d.%m.%Y %H:%M', time.gmtime())} UTC. {ncy} cycles communs (marchés lus × cycles enregistrés à Dublin). "
      f"Transactions preneuses rapprochées de Dublin : {nmatch} / {ntot} ({100 * nmatch / max(ntot, 1):.0f} %). Remplissages makers datés à la ms : {len(REM)}. "
      f"Makers classés sur toute la base (≥ 20 marchés, ≥ 5 000 $) : {len(rentables)} rentables (≥ +1 % par $), {len(perdants)} perdants (≤ −0,5 %).\n")
    w("Sélection adverse = prix du côté du maker h secondes après, moins son prix (cents par part ; négatif = le marché est parti contre lui). Pondérée par les parts.\n")

    def ligne(nom, X):
        if not X: return f"| {nom} | 0 | " + " | ".join("—" for _ in range(len(H) + 1)) + " |"
        cells = []
        for h in list(H) + ["regl"]:
            v = [(x["mo"][h], x["q"]) for x in X if h in x["mo"]]
            cells.append(f"{100 * sum(a * b for a, b in v) / sum(b for a, b in v):+.1f}" if v else "—")
        return f"| {nom} | {len(X)} | " + " | ".join(cells) + " |"
    w("## 1. Sélection adverse : makers réels contre nos fantômes\n")
    w("| Groupe | Remplissages | +0,1 s | +0,3 s | +1 s | +3 s | +5 s | +10 s | règlement |\n|---|---|---|---|---|---|---|---|---|")
    for g in ("rentable", "perdant", "autre"): w(ligne("makers " + g + "s", [x for x in REM if x["qui"] == g]))
    for fam in sorted({x["qui"] for x in NOS}): w(ligne(fam, [x for x in NOS if x["qui"] == fam]))
    w("\n(nos fantômes : pas de mesure à 0,1 et 0,3 s ; la sélection adverse « règlement » est le résultat par part)\n")
    w("## 2. Explications candidates (tous les makers réels, puis rentables seulement)\n")
    for titre, cle, groupes in (("Au meilleur prix ou plus loin", "au_meilleur", [(True, "au meilleur prix"), (False, "plus loin (servi par un balayage)")]),
                                ("Balayage de plusieurs niveaux par le preneur", "balayage", [(False, "preneur sur un seul prix"), (True, "balayage")]),
                                ("Conditions toxiques de M4 actives au remplissage", "cond", [("aucune", "aucune"), ("a", "a"), ("b", "b"), ("c", "c"), ("ac", "ac"), ("bc", "bc"), ("ab", "ab"), ("abc", "abc")])):
        w(f"**{titre}**\n")
        w("| Groupe | Remplissages | +0,1 s | +0,3 s | +1 s | +3 s | +5 s | +10 s | règlement |\n|---|---|---|---|---|---|---|---|---|")
        for val, nom in groupes:
            w(ligne(nom + " — tous", [x for x in REM if x[cle] == val])); w(ligne(nom + " — rentables", [x for x in REM if x[cle] == val and x["qui"] == "rentable"]))
        w("")
    w("**Taille de la transaction du preneur**\n")
    w("| Groupe | Remplissages | +0,1 s | +0,3 s | +1 s | +3 s | +5 s | +10 s | règlement |\n|---|---|---|---|---|---|---|---|---|")
    for lo, hi in ((0, 10), (10, 50), (50, 200), (200, 1e9)):
        w(ligne(f"preneur {lo}–{'∞' if hi > 1e8 else hi} $ — tous", [x for x in REM if lo <= x["taille_preneur"] < hi]))
        w(ligne(f"preneur {lo}–{'∞' if hi > 1e8 else hi} $ — rentables", [x for x in REM if lo <= x["taille_preneur"] < hi and x["qui"] == "rentable"]))
    w("\n**Part de chaque situation : makers rentables contre perdants contre nos fantômes**\n")
    for g in ("rentable", "perdant"):
        X = [x for x in REM if x["qui"] == g]
        if X: w(f"- makers {g}s : au meilleur prix {100 * np.mean([x['au_meilleur'] for x in X]):.0f} % ; balayages {100 * np.mean([x['balayage'] for x in X]):.0f} % ; "
                f"condition toxique active {100 * np.mean([x['cond'] != 'aucune' for x in X]):.0f} % ; prix médian {np.median([x['prix'] for x in X]):.2f} ; moment médian {np.median([x['t'] for x in X]):.0f} s")
    X = NOS
    if X: w(f"- nos fantômes : au meilleur prix {100 * np.mean([x['au_meilleur'] for x in X]):.0f} % ; prix médian {np.median([x['prix'] for x in X]):.2f}")
    w("\n## Limites\n- Une journée de cycles communs ; rapprochement par seconde, prix, côté et taille (les transactions non rapprochées sont exclues).\n"
      "- Les ordres posés puis annulés par ces makers sont invisibles : on ne voit que leurs remplissages.\n- Rentable / perdant est mesuré sur toute la base, y compris ces cycles.\n")
    open(SORTIE, "w").write("\n".join(o)); print("\n".join(o))


if __name__ == "__main__":
    main()
