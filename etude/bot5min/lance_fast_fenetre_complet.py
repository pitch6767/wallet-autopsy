"""Lance fast_fenetre.py --hors-echantillon sur toute la période réservée (16.10.2026), SANS changer aucun calcul.
Seule différence : pour tenir en mémoire (916 cycles, ~7 millions d'offres maker), chaque offre lue dans les cycles est raccourcie à
ses 10 premiers champs — la section 5 de fast_fenetre.py n'utilise que les champs 0 à 9. Sortie séparée pour garder l'historique :
etude/bot5min/resultat_fast_fenetre_hors_echantillon_complet.md (resultat_fast_fenetre.md, avant la période réservée, n'est pas écrasé).
Usage : python3 etude/bot5min/lance_fast_fenetre_complet.py dossier_des_cycles"""
import os, sys

ICI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, ICI)
import fast_fenetre as FF

_orig = FF.normaliser


def normaliser_leger(path):
    C = _orig(path); C["mk"] = [r[:10] for r in C["mk"]]; return C


FF.normaliser = normaliser_leger
FF.SORTIE = os.path.join(ICI, "resultat_fast_fenetre_hors_echantillon_complet.md")
if "--hors-echantillon" not in sys.argv: sys.argv.append("--hors-echantillon")
FF.main()
