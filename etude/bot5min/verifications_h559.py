"""BOT95 — Quatre vérifications demandées par Pitch (11.10.2026 15:00) sur les fantômes H559–H564, à partir des données DÉJÀ enregistrées.
Aucun fantôme ni règle modifié ; période réservée (≥ 13.10.2026 00:00 UTC) non lue.
 1. Interactions des conditions toxiques a/b/c (8 combinaisons), classées avec l'information disponible AU MOMENT de la pose seulement.
 2. M6 : temps réellement actif, remplacements, annulations en attente, remplissages pendant l'annulation, perte de priorité estimée.
 3. Cohérence de la file : prudent ≤ central ≤ optimiste, remplissages partiels, double comptage entre fantômes.
 4. Calcul de M8 : ce que fait réellement le code, et comparaison au preneur.
Usage : python3 etude/bot5min/verifications_h559.py dossier_des_cycles → etude/bot5min/resultat_verifications_h559.md"""
import gzip, json, os, sys, glob, bisect, collections, time
import numpy as np

ICI = os.path.dirname(os.path.abspath(__file__)); RACINE = os.path.abspath(os.path.join(ICI, "..", ".."))
sys.path.insert(0, ICI)
import queue_race_phase12 as Q
HORS_ECH = 1791849600
SORTIE = os.path.join(ICI, "resultat_verifications_h559.md")
mil = lambda p: int(round(p * 1000))
# indices des enregistrements compacts « mk » (rapide.js, makerMenage)
I_V, I_COTE, I_PRIX, I_TPOSE, I_LAT, I_ETAT, I_QDEV, I_RP, I_RR, I_PREM, I_REST, I_MOD, I_BB, I_ASK, I_NIV, I_TANN, I_RAIS, I_EV, I_RO, I_AP, I_AR, I_MODE = range(22)


def series_cycle(R):
    """séries pour les conditions toxiques, avec l'heure de RÉCEPTION à Dublin (aucune donnée future)"""
    ex = []
    for r in R.get("ex", []):
        px = [r[k][0] for k in (1, 2, 3, 4) if r[k]]
        if px: ex.append((r[0], float(np.median(px))))
    fx = []
    for t, d in R.get("fx") or []:
        fx.append((t, sum(v[0] - v[1] for k, v in d.items() if k != "liq_bybit")))
    tr = []                                                    # ventes sur les acheteurs : (heure, jeton 0 Up / 1 Down, parts)
    for e in R.get("ev", []):
        if e[0] != "T": continue
        tok, side, p, sz = e[3], e[4], e[5], e[6]
        cs, c = Q.cible_trade(tok, side, mil(p))
        if cs == 0: tr.append((e[1], 0, sz))                  # demande Up consommée
        else: tr.append((e[1], 1, sz))                        # offre Up consommée = demande Down consommée
    return ex, fx, tr


def conditions(ser, t, up):
    """a / b / c déclenchées dans les 2 s avant t (même pause que M4), calculées comme M4 avec les données reçues avant t"""
    ex, fx, tr = ser; sens = 1 if up else -1; out = set()
    Et = [x[0] for x in ex]
    i1 = bisect.bisect_right(Et, t)
    for j in range(bisect.bisect_left(Et, t - 2000), i1):
        tj, pj = ex[j]; k = bisect.bisect_right(Et, tj - 300) - 1
        if k >= 0 and sens * (pj - ex[k][1]) <= -10: out.add("a"); break
    Ft = [x[0] for x in fx]; i1 = bisect.bisect_right(Ft, t); i0 = bisect.bisect_left(Ft, t - 2000 - 250)
    for j in range(max(i0, 0), i1):
        tj = fx[j][0]
        if tj < t - 2000: continue
        k0 = bisect.bisect_left(Ft, tj - 250); s = sum(x[1] for x in fx[k0:j + 1])
        if sens * s <= -250000: out.add("b"); break
    Tt = [x[0] for x in tr]; i1 = bisect.bisect_right(Tt, t)
    for j in range(bisect.bisect_left(Tt, t - 2000), i1):
        tj = tr[j][0]; k0 = bisect.bisect_left(Tt, tj - 500)
        if sum(x[2] for x in tr[k0:j + 1] if x[1] == (0 if up else 1)) >= 100: out.add("c"); break
    return "".join(sorted(out)) or "aucune"


def volume_niveau(tr_raw, up, prix, t0, t1):
    """parts vendues sur les acheteurs de notre jeton À notre prix entre t0 et t1 ; traversée = vente à un prix plus bas"""
    v = 0.0; trav = False; pm = mil(prix)
    for t, tok, side, p, sz in tr_raw:
        if t < t0 or t > t1: continue
        cs, c = Q.cible_trade(tok, side, mil(p))
        if up and cs == 0:
            if c == pm: v += sz
            elif c < pm: trav = True
        if not up and cs == 1:
            q = 1000 - c
            if q == pm: v += sz
            elif q < pm: trav = True
    return v, trav


def main():
    dossier = sys.argv[1]
    MKR = json.load(open(os.path.join(RACINE, "bot95", "rapide_maker.json")))
    regle = {}
    for x in MKR:
        if x.get("type") == "resume" or not x.get("resultat") or x["start"] >= HORS_ECH: continue
        regle[(x["variante"], round(x["tPose"]))] = x
    COMBO = collections.defaultdict(lambda: dict(n=0, fills=0, parts=0.0, pnl=0.0, mo=collections.defaultdict(lambda: [0.0, 0.0])))
    M6 = collections.defaultdict(lambda: dict(n=0, actif=[], remplacements=collections.Counter(), annul_attente_ms=0.0, parts_pendant=0.0, perte=[], fills=0))
    COH = collections.Counter(); COHv = collections.defaultdict(collections.Counter); stricte = collections.defaultdict(lambda: [0.0, 0.0, 0.0, 0.0])
    PARTAGE = collections.Counter(); ncy = 0
    for fn in sorted(glob.glob(os.path.join(dossier, "**", "*.json.gz"), recursive=True)):
        st = int(os.path.basename(fn).split(".")[0])
        if st >= HORS_ECH: continue
        R = json.load(gzip.open(fn)); mk = R.get("mk") or []
        if not mk or len(mk[0]) < 22: continue                 # versions antérieures au 11.10 14:55 (pas de borne optimiste)
        ncy += 1; ser = series_cycle(R)
        tr_raw = [(e[1], e[3], e[4], e[5], e[6]) for e in R.get("ev", []) if e[0] == "T"]
        # ---- 1. combinaisons (M2 marge 5 c : même prix que M4, aucun retrait)
        for r in mk:
            if r[I_V] != "M2 cotation marge 5 c" or r[I_ETAT] == "rejetee": continue
            up = r[I_COTE] == "Up"; cmb = conditions(ser, r[I_TPOSE], up); C = COMBO[cmb]; C["n"] += 1
            x = regle.get((r[I_V], round(r[I_TPOSE])))
            if x and x["remplP"] > 0:
                C["fills"] += 1; C["parts"] += x["remplP"]; C["pnl"] += x["resultat"]["prudent"]
                for h in ("1", "3", "5", "10"):
                    a = (x.get("mo") or {}).get("p", {}).get(h)
                    if a: C["mo"][h][0] += a[0]; C["mo"][h][1] += a[1]
        # ---- 2. M6
        par = collections.defaultdict(list)
        for r in mk:
            if r[I_V].startswith("M6") or r[I_V] == "M2 cotation marge 5 c": par[(r[I_V], r[I_COTE])].append(r)
        for (v, cote), L in par.items():
            L.sort(key=lambda r: r[I_TPOSE]); S = M6[v]
            for i, r in enumerate(L):
                S["n"] += 1; lat = r[I_LAT] or 15
                if r[I_TANN]:
                    S["actif"].append(max(0.0, r[I_TANN] - (r[I_TPOSE] + lat)))
                    if r[I_RAIS] == "duree de vie": S["remplacements"][st] += 1; S["annul_attente_ms"] += 2 * lat
                S["parts_pendant"] += r[I_AP] or 0; S["fills"] += (r[I_RP] or 0) > 0
                if r[I_TANN] and r[I_QDEV] is not None and i + 1 < len(L) and abs(L[i + 1][I_PRIX] - r[I_PRIX]) < 1e-9 and L[i + 1][I_QDEV] is not None:
                    vol, trav = volume_niveau(tr_raw, cote == "Up", r[I_PRIX], r[I_TPOSE] + lat, r[I_TANN] + lat)
                    reste = max(0.0, r[I_QDEV] - vol)          # file devant l'ancienne offre à son annulation (borne prudente)
                    S["perte"].append(L[i + 1][I_QDEV] - reste)
        # ---- 3. cohérence
        poses = collections.Counter()
        for r in mk:
            if r[I_ETAT] == "rejetee" or r[I_MODE] == "preneur": continue
            p_, c_, o_ = r[I_RP] or 0, r[I_RR] or 0, r[I_RO] or 0
            COH["offres"] += 1
            if p_ > c_ + 1e-6: COH["prudent > central"] += 1; COHv[r[I_V]]["prudent > central"] += 1
            if c_ > o_ + 1e-6: COH["central > optimiste"] += 1; COHv[r[I_V]]["central > optimiste"] += 1
            if 0 < p_ < 50 / r[I_PRIX] - 0.05: COH["remplissages partiels (prudent)"] += 1
            # borne STRICTE recalculée hors ligne : seules les ventes à notre prix après la file vue à l'arrivée (aucun plafond), ou traversée
            if r[I_QDEV] is not None:
                lat = r[I_LAT] or 15; t1 = (r[I_TANN] + lat) if r[I_TANN] else (st + 300) * 1000
                vol, trav = volume_niveau(tr_raw, r[I_COTE] == "Up", r[I_PRIX], r[I_TPOSE] + lat, t1)
                taille = 50 / r[I_PRIX]; s = taille if trav else min(taille, max(0.0, vol - r[I_QDEV]))
                B = stricte[r[I_V]]; B[0] += s; B[1] += p_; B[2] += c_; B[3] += o_
            poses[(r[I_COTE], r[I_PRIX], round(r[I_TPOSE] / 1000))] += 1
        for k, n in poses.items():
            if n > 1: PARTAGE["offres simultanées au même prix (plusieurs fantômes)"] += n
    # ---------------------------------------------------------------- rapport
    o = []; w = o.append
    w("# Bot95 — Vérifications H559–H564 (préliminaire)\n")
    w(f"Généré le {time.strftime('%d.%m.%Y %H:%M', time.gmtime())} UTC. {ncy} cycles enregistrés avec la version du 11.10 14:55 (bornes à trois niveaux), avant la période réservée. "
      "Aucun fantôme ni règle modifié.\n")
    w("**Statut des chiffres** — MESURE : heures, files vues à l'arrivée, transactions, prix. SIMULATION : remplissages (trois bornes), résultats en $. "
      "INSUFFISANT : tout ce qui porte sur moins de ~30 remplissages.\n")
    w("## 1. Interactions des conditions a / b / c (offres de M2 marge 5 c, classées à la pose)\n")
    w("a : bourses −10 $ en 300 ms ; b : flux agressif net ≥ 250 000 $ contre nous en 250 ms ; c : ≥ 100 parts vendues sur nos acheteurs en 500 ms ; "
      "chacune « active » si déclenchée dans les 2 s avant la pose (même pause que M4). Classement fait uniquement avec les données reçues AVANT la pose.\n")
    w("| Combinaison | Opportunités (offres posées) | Remplies (prudent) | Parts | Résultat prudent | par part | Sélection adverse +1 / +3 / +5 / +10 s (c/part) |\n|---|---|---|---|---|---|---|")
    for k in ("aucune", "a", "b", "c", "ab", "ac", "bc", "abc"):
        C = COMBO.get(k)
        if not C: w(f"| {k} | 0 | — | — | — | — | — |"); continue
        mo = " / ".join(f"{100 * C['mo'][h][0] / C['mo'][h][1]:+.1f}" if C["mo"][h][1] else "—" for h in ("1", "3", "5", "10"))
        w(f"| {k} | {C['n']} | {C['fills']} | {C['parts']:.0f} | {C['pnl']:+.0f} $ | {(100 * C['pnl'] / C['parts'] if C['parts'] else float('nan')):+.1f} c | {mo} |")
    w("\nEffet propre d'une condition = ligne « a » (ou « b », « c ») seule contre « aucune » ; interaction = lignes combinées contre la somme des effets propres. "
      "Avec si peu de remplissages, aucune interaction ne peut être distinguée du hasard à ce stade.\n")
    w("## 2. M6 : durée de vie et perte de priorité\n")
    w("| Variante | Offres | Temps réellement actif médian (ms) | Remplacements par cycle et côté (médiane) | Temps sans offre (annulations en attente, total s) | Parts remplies pendant l'annulation | Offres remplies | Perte de priorité estimée par remplacement (parts, médiane / p90) |\n|---|---|---|---|---|---|---|---|")
    for v in ["M2 cotation marge 5 c"] + [f"M6 duree de vie {L} ms" for L in (100, 250, 500, 1000)]:
        S = M6.get(v)
        if not S: continue
        rp = list(S["remplacements"].values())
        w(f"| {v} | {S['n']} | {np.median(S['actif']) if S['actif'] else float('nan'):.0f} | {np.median(rp) / 2 if rp else 0:.0f} | {S['annul_attente_ms'] / 1000:.1f} | {S['parts_pendant']:.0f} | {S['fills']} | "
          + (f"{np.median(S['perte']):.0f} / {np.percentile(S['perte'], 90):.0f} |" if S["perte"] else "— |"))
    w("\nPerte de priorité = file devant la nouvelle offre à son arrivée − file qui restait devant l'ancienne à son annulation (borne prudente : seules les transactions l'ont fait avancer). "
      "MESURE de la file affichée ; l'avancée dans la file est SIMULÉE.\n")
    w("## 3. Cohérence de la file d'attente\n")
    w(f"Offres posées contrôlées : {COH['offres']}. Remplissages partiels (prudent) : {COH['remplissages partiels (prudent)']}.\n")
    w(f"- prudent > central : **{COH['prudent > central']}** offres ; central > optimiste : **{COH['central > optimiste']}** offres.")
    for v, c in sorted(COHv.items()):
        w(f"  - {v} : " + ", ".join(f"{k} {n}" for k, n in c.items()))
    w("\n**Cause identifiée dans le code (non corrigée, fantômes gelés jusqu'au verdict)** : la borne « prudente » plafonne la file devant nous à la quantité affichée "
      "(min avec l'affiché), alors que la borne centrale et la borne optimiste ne sont pas plafonnées. Après de gros retraits, la prudente peut donc avancer plus vite que la centrale. "
      "L'ordre prudent ≤ central ≤ optimiste n'est garanti que si les trois bornes appliquent le même plafond.\n")
    w("Borne STRICTE recalculée hors ligne (ventes à notre prix après la file vue à l'arrivée, sans plafond ni retrait ; traversée = tout) :\n")
    w("| Variante | Parts stricte (hors ligne) | Parts prudent (enregistré) | Parts central | Parts optimiste | central ≤ optimiste ? | stricte ≤ central ? |\n|---|---|---|---|---|---|---|")
    for v, (s, p_, c_, o_) in sorted(stricte.items()):
        w(f"| {v} | {s:.0f} | {p_:.0f} | {c_:.0f} | {o_:.0f} | {'oui' if c_ <= o_ + 0.5 else 'NON'} | {'oui' if s <= c_ + 0.5 else 'NON'} |")
    w("\nLa borne stricte hors ligne n'est pas toujours ≤ la borne enregistrée : le fichier du cycle donne l'heure THÉORIQUE d'arrivée et d'annulation (pose + trajet), "
      "alors que le fantôme en direct ne devient actif qu'au déclenchement réel de son minuteur (quelques ms plus tard). Une transaction tombée dans cet intervalle est comptée "
      "hors ligne mais pas en direct (et inversement à l'annulation). Ces écarts sont des différences de minutage, pas des doubles comptages ; les heures réelles d'arrivée et "
      "d'annulation ne sont pas encore enregistrées dans le fichier compact.\n")
    w("\nDouble comptage entre fantômes : chaque fantôme se simule SEUL face au carnet réel ; deux fantômes au même prix sont remplis par la même transaction. "
      f"Leurs résultats ne s'additionnent donc pas (offres simultanées au même prix et à la même seconde : {PARTAGE['offres simultanées au même prix (plusieurs fantômes)']}). "
      "Un défaut de partage entre fantômes de l'attribution transaction/retrait (borne centrale) a été corrigé à 14:55 ; les offres antérieures ne sont pas utilisées ici.\n")
    w("## 4. Calcul de M8 (hybride maker / preneur)\n")
    w("Ce que fait le code actuel (gelé jusqu'au verdict) :\n")
    w("- **Preneur** : espérance = parts disponibles au prix vu (50 $) × probabilité du modèle − coût frais compris (0,07·p·(1−p)). "
      "Le retard de 150 ms N'entre PAS dans la décision ; il n'entre que dans l'exécution simulée (quantité réellement présente 150 ms + trajet plus tard).\n")
    w("- **Maker** : espérance = parts attendues en 10 s × (probabilité du modèle − prix − 2 c). Les parts attendues viennent du rythme des ventes des 30 dernières s moins la file devant nous. "
      "Ce n'est **PAS** un gain conditionnel au remplissage : la non-exécution est seulement implicite (parts attendues), la sélection adverse est une constante de 2 c "
      "(alors que la mesure sur M2 est de −8 à −11 c), aucune ristourne ni frais maker, et la probabilité du modèle n'est pas recalculée sachant qu'on est rempli.\n")
    w("- **Conséquence** : M8 surestime le gain maker. Une version conforme (P(remplissage) × E[gain | remplissage] avec sélection adverse mesurée, et preneur × probabilité de survie à 164 ms) "
      "est proposée comme NOUVEAU fantôme après le verdict, sur les données d'apprentissage seulement ; M8 actuel reste inchangé.\n")
    M8 = [x for x in MKR if str(x.get("variante", "")).startswith("M8") and x.get("resultat") and x["start"] < HORS_ECH]
    if M8:
        for mode in ("preneur", "maker"):
            X = [x for x in M8 if x.get("mode") == mode]
            if X: w(f"- M8 {mode} : {len(X)} positions, résultat prudent {sum(x['resultat']['prudent'] for x in X):+.0f} $, espérance annoncée moyenne {np.mean([x.get('evPreneur' if mode == 'preneur' else 'evMaker') or 0 for x in X]):+.2f} $")
    else:
        w("- M8 : pas encore de positions réglées.\n")
    open(SORTIE, "w").write("\n".join(o)); print("\n".join(o))


if __name__ == "__main__":
    main()
