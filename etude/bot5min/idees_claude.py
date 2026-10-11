"""BOT95 — trois idées de Claude testées sur les cycles déjà enregistrés à Dublin (11.10.2026). Hors ligne, aucun bot modifié.
 I1  SUIVRE LES GROS PRENEURS : après une grosse transaction preneuse sur Polymarket, le prix continue-t-il dans son sens ?
 I2  MAKER DE FIN DE CYCLE SUR LE CÔTÉ PRESQUE ACQUIS : dans les 30 dernières s, des vendeurs frappent-ils les acheteurs du côté ≥ 0,90, et ce côté gagne-t-il ?
 I3  DOUBLE MAKER : les deux meilleurs prix (acheteur et vendeur du jeton Up) sont-ils consommés dans la même fenêtre de 10 s (capture de l'écart) ?
Période réservée (≥ 13.10.2026 00:00 UTC) non lue. Usage : python3 etude/bot5min/idees_claude.py dossier → etude/bot5min/resultat_idees_claude.md"""
import gzip, json, os, sys, glob, bisect, collections, time
import numpy as np

ICI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, ICI)
import queue_race_phase12 as Q
import fast_fenetre as FF
HORS_ECH = 1791849600; SORTIE = os.path.join(ICI, "resultat_idees_claude.md")


def mid_a(S, t):
    i = np.searchsorted(S[:, 0], t, "right") - 1
    if i < 0: return None
    b, a = S[i, 1], S[i, 3]
    return None if np.isnan(b) or np.isnan(a) else (b + a) / 2000.0


RACINE = os.path.abspath(os.path.join(ICI, "..", ".."))
GAGNANTS = {}
for fich, cle in (("rapide.json", "signaux"), ("rapide_maker.json", None)):
    try:
        d = json.load(open(os.path.join(RACINE, "bot95", fich))); L = d[cle] if cle else d
        for x in L:
            if x.get("gagnant") in ("Up", "Down"): GAGNANTS[x["start"]] = 1 if x["gagnant"] == "Up" else 0
    except Exception: pass


def gagnant(C):
    if C["start"] in GAGNANTS: return GAGNANTS[C["start"]]
    """côté gagnant lu dans le carnet de la dernière seconde (≥ 0,95 ou ≤ 0,05), sinon inconnu"""
    for sn in reversed(C["snap"]):
        if sn[0] > (C["start"] + 300) * 1000 + 15000: continue
        if sn[1] and sn[2]:
            m = (sn[1][0][0] + sn[2][0][0]) / 2
            if sn[0] >= (C["start"] + 297) * 1000:
                return 1 if m >= 0.95 else (0 if m <= 0.05 else None)
        break
    return None


def main():
    fichiers = [f for f in sorted(glob.glob(os.path.join(sys.argv[1], "**", "*.json.gz"), recursive=True)) if int(os.path.basename(f).split(".")[0]) < HORS_ECH]
    I1 = collections.defaultdict(lambda: collections.defaultdict(list)); I2 = []; I3 = []; ncy = 0; inconnus = 0
    for fn in fichiers:
        C = FF.normaliser(fn)
        if not C["flux"] or not any(e[2] == "B" for e in C["flux"]): continue
        Rj = Q.rejouer(C); S = Rj["serie"]
        if len(S) < 10: continue
        ncy += 1; g = gagnant(C)
        if g is None: inconnus += 1
        st = C["start"] * 1000
        # I1 : transactions preneuses (sens Up : +1 si achat Up ou vente Down)
        for tt in Rj["trades"]:
            t, ts, tok, side, m, sz = tt[0], tt[1], tt[2], tt[3], tt[4], tt[5]
            if not (st + 5000 <= t <= st + 280000): continue
            sens = (1 if side == 1 else -1) * (1 if tok == 0 else -1)
            prixUp = m / 1000 if tok == 0 else 1 - m / 1000
            usd = sz * (m / 1000)
            cl = "≥ 500 $" if usd >= 500 else ("100–500 $" if usd >= 100 else "< 100 $")
            m0 = mid_a(S, t)
            if m0 is None: continue
            for h in (1, 5, 30):
                m1 = mid_a(S, t + h * 1000)
                if m1 is not None: I1[cl][h].append(sens * (m1 - m0))
            if g is not None:
                # suivre au prix payé par le preneur (borne optimiste : même prix) : résultat par part au règlement
                I1[cl]["regl"].append((g - prixUp) if sens == 1 else ((1 - g) - (1 - prixUp)))
        # I2 : 30 dernières secondes, côté ≥ 0,90
        if g is not None:
            t30 = st + 270000; m30 = mid_a(S, t30)
            if m30 is not None and (m30 >= 0.90 or m30 <= 0.10):
                cote_up = m30 >= 0.90; vol = 0.0; prix = []
                for tt in Rj["trades"]:
                    if not (t30 <= tt[0] <= st + 299000): continue
                    cs, c = tt[6], tt[7]
                    # vente sur les acheteurs du côté favori : demande Up (cs 0) si Up favori ; offre Up (cs 1) = demande Down si Down favori
                    if cote_up and cs == 0 and c >= 900: vol += tt[5]; prix.append(c / 1000)
                    if not cote_up and cs == 1 and c <= 100: vol += tt[5]; prix.append(1 - c / 1000)
                I2.append(dict(gagne=(g == 1) == cote_up, vol=vol, prix=float(np.mean(prix)) if prix else None))
        # I3 : fenêtres de 10 s : meilleur acheteur ET meilleur vendeur Up consommés ?
        tr = Rj["trades"]
        for w0 in range(st + 10000, st + 290000, 10000):
            b = a = False; spr = []
            i0 = np.searchsorted(S[:, 0], w0, "right") - 1
            if i0 >= 0 and not np.isnan(S[i0, 1]) and not np.isnan(S[i0, 3]): spr.append((S[i0, 3] - S[i0, 1]) / 1000)
            for tt in tr:
                if w0 <= tt[0] < w0 + 10000:
                    if tt[6] == 0 and tt[9] is not None and tt[7] >= tt[9]: b = True     # vente qui frappe le meilleur acheteur Up
                    if tt[6] == 1 and tt[8] is not None and tt[7] <= tt[8]: a = True     # achat qui frappe le meilleur vendeur Up
            I3.append((b, a, spr[0] if spr else None))
    o = []; w = o.append
    w("# Bot95 — Trois idées de Claude, premier test sur les cycles enregistrés (PRÉLIMINAIRE)\n")
    w(f"{ncy} cycles de Dublin (avant la période réservée) ; gagnant lu dans le carnet de fin de cycle (inconnu pour {inconnus}). Aucune règle, aucun bot modifié.\n")
    w("## I1. Suivre les gros preneurs Polymarket\n")
    w("| Taille de la transaction preneuse | Transactions | Mouvement du milieu dans son sens +1 s / +5 s / +30 s (c) | Suivre au même prix : résultat par part au règlement |\n|---|---|---|---|")
    for cl in ("< 100 $", "100–500 $", "≥ 500 $"):
        D = I1.get(cl)
        if not D: continue
        mv = " / ".join(f"{100 * np.mean(D[h]):+.2f}" if D[h] else "—" for h in (1, 5, 30))
        r = D["regl"]; w(f"| {cl} | {len(D[1])} | {mv} | {100 * np.mean(r):+.2f} c ({len(r)}) |" if r else f"| {cl} | {len(D[1])} | {mv} | — |")
    w("\nSi les grosses transactions continuent dans leur sens, on peut les suivre sans course de vitesse (horizon de secondes, pas de millisecondes).\n")
    w("## I2. Maker de fin de cycle sur le côté presque acquis (≥ 0,90 à 30 s de la fin)\n")
    if I2:
        n = len(I2); gw = sum(x["gagne"] for x in I2); avec = [x for x in I2 if x["vol"] > 0]
        w(f"- Cycles avec un côté ≥ 0,90 à 30 s de la fin : {n} ; ce côté a gagné {gw} fois ({100 * gw / n:.0f} %).")
        w(f"- Cycles où des vendeurs ont frappé les acheteurs de ce côté (≥ 0,90) dans les 30 dernières s : {len(avec)} ; volume médian {np.median([x['vol'] for x in avec]) if avec else 0:.0f} parts ; "
          f"prix moyen {np.mean([x['prix'] for x in avec]) if avec else float('nan'):.3f} ; le côté a gagné {sum(x['gagne'] for x in avec)} fois sur {len(avec)}.")
        w("- Un acheteur posé à ces prix (sans frais maker, avec ristourne) gagne 1 − prix par part si le côté gagne, perd le prix sinon.\n")
    w("## I3. Double maker (meilleur acheteur ET meilleur vendeur du jeton Up)\n")
    if I3:
        both = sum(1 for b, a, s in I3 if b and a); sp = [s for b, a, s in I3 if s is not None]
        w(f"- Fenêtres de 10 s : {len(I3)} ; meilleur acheteur consommé : {sum(1 for b, a, s in I3 if b)} ; meilleur vendeur consommé : {sum(1 for b, a, s in I3 if a)} ; "
          f"LES DEUX : {both} ({100 * both / len(I3):.0f} %). Écart médian au début de la fenêtre : {np.median(sp) * 100:.1f} c.")
        w("- Un double maker en tête de file gagnerait l'écart sur ces fenêtres ; ailleurs il garde un côté seul (risque directionnel, sélection adverse mesurée sur M2).\n")
    w("## Limites\n- Une journée de données ; aucune file d'attente simulée pour I2 et I3 (on suppose être en tête) : ce sont des PLAFONDS.\n")
    open(SORTIE, "w").write("\n".join(o)); print("\n".join(o))


if __name__ == "__main__":
    main()
