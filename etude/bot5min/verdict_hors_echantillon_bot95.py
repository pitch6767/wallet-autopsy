"""BOT95 — VERDICT HORS ÉCHANTILLON : tableau récapitulatif par variante maker (lecture seule, aucun ordre, aucune règle modifiée).
Demande de Pitch, 15.10.2026. Complète resultat_maker_h559_hors_echantillon.md et resultat_fast_fenetre_hors_echantillon.md :
mêmes données (bot95/rapide_maker.json, cycles ≥ 13.10.2026 00:00 UTC), mêmes fonctions ic_blocs / creux que maker_h559.py,
mais groupes de variantes EXACTS (dans maker_h559.py, « M1 » attrape aussi M10 et M11, « M8 » attrape aussi M8b).
Ajoute : couverture réelle des données, comparaison appariée au témoin M0 par cycle, rappel des chiffres avant la période réservée.
Usage : python3 etude/bot5min/verdict_hors_echantillon_bot95.py [dossier_des_cycles] [--complet] → etude/bot5min/resultat_verdict_hors_echantillon_bot95.md (ou ..._complet.md)"""
import json, os, sys, collections, time
import numpy as np

ICI = os.path.dirname(os.path.abspath(__file__)); RACINE = os.path.abspath(os.path.join(ICI, "..", ".."))
sys.path.insert(0, ICI)
from maker_h559 import ic_blocs, creux, HORS_ECH
COMPLET = "--complet" in sys.argv   # 16.10.2026 : même verdict sur toute la période réservée (sauvegarde maker réparée), sortie séparée
SORTIE = os.path.join(ICI, "resultat_verdict_hors_echantillon_bot95_complet.md" if COMPLET else "resultat_verdict_hors_echantillon_bot95.md")

GROUPES = [  # (nom affiché, test sur le nom de variante)
    ("M0 témoin aléatoire", lambda v: v == "M0 temoin aleatoire"),
    ("M1 offre au signal (toutes cohortes)", lambda v: v.startswith("M1 ")),
    ("M2 marge 5 c", lambda v: v == "M2 cotation marge 5 c"),
    ("M2 marge 10 c", lambda v: v == "M2 cotation marge 10 c"),
    ("M4 retrait toxique", lambda v: v == "M4 retrait toxique"),
    ("M5 remplissage attendu", lambda v: v == "M5 remplissage attendu"),
    ("M8 hybride (toutes cohortes)", lambda v: v.startswith("M8 hybride")),
    ("M8b routeur corrigé (toutes cohortes)", lambda v: v.startswith("M8b")),
    ("M3 anticipation Chainlink", lambda v: v == "M3 anticipation Chainlink"),
    ("M10 double maker", lambda v: v.startswith("M10")),
]


def stats(X):
    remplies = [x for x in X if (x.get("remplP") or 0) > 0]
    parts = sum(x["remplP"] for x in remplies)
    usd = sum((x.get("cout") or x["remplP"] * x["prix"]) for x in remplies)
    pc = collections.defaultdict(float)
    for x in X: pc[x["start"]] += x["resultat"]["prudent"] or 0
    r = sum(pc.values()); ic = ic_blocs(pc)
    mo = []
    for h in ("1", "3", "5", "10"):
        a = sum((x.get("mo") or {}).get("p", {}).get(h, [0, 0])[0] for x in X); b = sum((x.get("mo") or {}).get("p", {}).get(h, [0, 0])[1] for x in X)
        mo.append(f"{100 * a / b:+.1f}" if b else "—")
    cen = sum((x["resultat"].get("proportionnel") or 0) for x in X)
    modes = collections.Counter(x.get("mode") or "maker" for x in remplies)
    return dict(n=len(remplies), parts=parts, usd=usd, r=r, ic=ic, creux=creux(pc), mo=mo, cen=cen, pc=pc, modes=modes)


def diff_m0(pcv, pc0, n=2000):
    cyc = sorted(set(pcv) | set(pc0))
    if len(cyc) < 3: return None
    d = np.array([pcv.get(c, 0.0) - pc0.get(c, 0.0) for c in cyc]); rng = np.random.default_rng(3)
    b = [d[rng.integers(0, len(d), len(d))].sum() for _ in range(n)]
    return d.sum(), np.percentile(b, [5, 95])


def fic(ic): return f"[{ic[0]:+.0f} ; {ic[1]:+.0f}]" if ic is not None else "[—]"


def main():
    MK = json.load(open(os.path.join(RACINE, "bot95", "rapide_maker.json")))
    MK = [x for x in MK if x.get("type") != "resume" and x.get("resultat")]
    HO = [x for x in MK if x["start"] >= HORS_ECH]; IN = [x for x in MK if x["start"] < HORS_ECH]
    cyc_h = sorted({x["start"] for x in HO})
    o = []; w = o.append
    w("# Bot95 — verdict hors échantillon : récapitulatif par variante maker\n")
    w(f"Généré le {time.strftime('%d.%m.%Y %H:%M', time.gmtime())} UTC. Fichier bot95/rapide_maker.json (sauvegarde du dépôt). "
      f"Offres réglées hors échantillon : cycles du {time.strftime('%d.%m %H:%M', time.gmtime(cyc_h[0]))} au {time.strftime('%d.%m %H:%M', time.gmtime(cyc_h[-1]))} UTC "
      f"({len(cyc_h)} cycles avec au moins une offre réglée). Remplissages SIMULÉS (borne prudente), aucun ordre réel.\n")
    w("Résultat prudent en $ ; IC 90 % par rééchantillonnage des cycles (2 000 tirages) ; creux = pire baisse cumulée ; "
      "sélection adverse = milieu du carnet h s après le remplissage moins notre prix (c par part, négatif = contre nous).\n")
    w("| Variante | Remplissages | Parts | $ engagés | Résultat prudent | IC 90 % | Central | Creux | Sélection adverse +1/+3/+5/+10 s | Écart à M0 (même cycles) [IC 90 %] | Avant le 13.10 (prudent) [IC 90 %] |")
    w("|---|---|---|---|---|---|---|---|---|---|---|")
    S0 = None; lignes = []
    for nom, f in GROUPES:
        X = [x for x in HO if f(x["variante"])]; s = stats(X)
        if S0 is None: S0 = s
        si = stats([x for x in IN if f(x["variante"])])
        d = diff_m0(s["pc"], S0["pc"]) if nom != GROUPES[0][0] else None
        dd = f"{d[0]:+.0f} {fic(d[1])}" if d else "—"
        w(f"| {nom} | {s['n']}" + (f" ({', '.join(f'{k} {v}' for k, v in s['modes'].items())})" if len(s['modes']) > 1 else "") +
          f" | {s['parts']:.0f} | {s['usd']:.0f} $ | {s['r']:+.0f} $ | {fic(s['ic'])} | {s['cen']:+.0f} $ | {s['creux']:+.0f} $ | {' / '.join(s['mo'])} | {dd} | {si['r']:+.0f} $ {fic(si['ic'])} |")
        lignes.append((nom, s))
    # moteur C (preneur, exécution mesurée à 300 ms), même champ que fast_fenetre.py section 6, mais tous les signaux réglés ≥ 13.10 avec IC
    SIG = json.load(open(os.path.join(RACINE, "bot95", "rapide.json")))["signaux"]
    w("\n## Moteur C (preneur, exécution à 300 ms) : tous les signaux réglés de la période réservée\n")
    w("| Période | Signaux avec résultat | Trades exécutés | $ engagés | Résultat | IC 90 % | Creux |\n|---|---|---|---|---|---|---|")
    for nom, g in (("≥ 13.10.2026 (hors échantillon)", lambda st: st >= HORS_ECH), ("avant le 13.10", lambda st: st < HORS_ECH)):
        X = [S for S in SIG if g(S["start"]) and S.get("moteurC") and (S["moteurC"].get("resultat") or {}).get("300ms") is not None]
        pc = collections.defaultdict(float); n = 0; c = 0.0
        for S in X:
            v = S["moteurC"]["resultat"]["300ms"]; pc[S["start"]] += v
            if v != 0: n += 1; c += ((S["moteurC"].get("remplissage") or {}).get("300ms") or {}).get("c") or 0
        w(f"| {nom} | {len(X)} | {n} | {c:.0f} $ | {sum(pc.values()):+.0f} $ | {fic(ic_blocs(pc))} | {creux(pc):+.0f} $ |")
    dossier = [a for a in sys.argv[1:] if not a.startswith("--")]
    if dossier:   # FAST / SLOW / HYBRID : mêmes fonctions figées que fast_fenetre.py (tournoi_signaux), pour ajouter parts et creux
        import glob, fast_fenetre as FF
        MKall = json.load(open(os.path.join(RACINE, "bot95", "rapide_maker.json")))
        debut = min(x["start"] for x in MKall if x.get("type") != "resume")
        SIGc = collections.defaultdict(list)
        for S in SIG:
            if S.get("gagnant") and S.get("tDecision"): SIGc[S["start"]].append(S)
        T = []
        for fn in sorted(glob.glob(os.path.join(dossier[0], "**", "*.json.gz"), recursive=True)):
            st = int(os.path.basename(fn).split(".")[0])
            if st < HORS_ECH or st < debut or not SIGc.get(st): continue
            C = FF.normaliser(fn)
            if not C["flux"] or not any(e[2] == "B" for e in C["flux"]): continue
            T += FF.tournoi_signaux(C, SIGc[st])
        w("\n## FAST / SLOW / HYBRID (preneur) : recalcul descriptif avec les fonctions figées de fast_fenetre.py\n")
        w(f"{len({x['start'] for x in T})} cycles avec signaux réglés. Totaux identiques attendus à resultat_fast_fenetre_hors_echantillon.md section 6 ; ajoute parts et creux.\n")
        w("| Stratégie | Trades | Parts | $ engagés | Résultat | IC 90 % | par $ | Creux |\n|---|---|---|---|---|---|---|---|")
        for k in ("FAST", "SLOW", "HYBRID"):
            X = [x for x in T if x[k][0] > 0]; pc = collections.defaultdict(float)
            for x in X: pc[x["start"]] += x[k][2]
            c = sum(x[k][1] for x in X); r = sum(pc.values())
            w(f"| {k} | {len(X)} | {sum(x[k][0] for x in X):.0f} | {c:.0f} $ | {r:+.0f} $ | {fic(FF.ic_blocs(pc))} | {(r / c if c else float('nan')):+.2f} | {creux(pc):+.0f} $ |")
    w("\n## Lecture\n")
    for nom, s in lignes:
        ic = s["ic"]
        if ic is None: v = "trop peu de données"
        elif ic[0] > 0: v = "gain démontré (IC entièrement au-dessus de 0)"
        elif ic[1] < 0: v = "perte démontrée (IC entièrement sous 0)"
        else: v = "non démontré (l'IC contient 0)"
        w(f"- {nom} : {v}.")
    w("\n## Limites\n" + (f"- Sauvegarde maker réparée : offres réglées couvrant toute la période réservée jusqu'au cycle du {time.strftime('%d.%m.%Y %H:%M', time.gmtime(cyc_h[-1]))} UTC.\n" if COMPLET else
      "- Les offres réglées s'arrêtent au cycle du 14.10.2026 07:50 UTC : depuis, la sauvegarde de bot95/rapide_maker.json échoue "
      "(l'adresse /api/rapidemaker du bot répond « erreur 500 »). Le volet maker couvre donc ~32 h de la période réservée, pas 2,7 jours.\n") +
      "- Remplissages simulés (file d'attente reconstituée), pas des exécutions réelles ; retard preneur de 150 ms supposé, non mesuré.\n"
      "- Variantes testées en parallèle sur les mêmes cycles : avec une dizaine de variantes, un IC qui exclurait 0 de peu pourrait être dû au hasard.\n")
    open(SORTIE, "w").write("\n".join(o)); print("\n".join(o))


if __name__ == "__main__":
    main()
