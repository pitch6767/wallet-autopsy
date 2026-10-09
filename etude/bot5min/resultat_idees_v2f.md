# 5 tests sur V2-F « écart qui grandit » (BTC) — rejeu sur les vrais carnets (07.10 08:03 → 09.10 08:11)

448 trades rejoués, 107 gagnés, +6'096 $. Plus longue série de pertes du rejeu : 25 (07.10 22:32 → 08.10 00:36).

Modèle reconstruit (tests 3 et 4) contre modèle enregistré par le bot : corrélation 0.988, écart médian 0.6 pts.

## Test 1 — retournements du modèle dans le cycle avant l'achat

| Groupe / filtre | Trades | Gagnés | % gagnés | Résultat | Sans top 3 | Pertes de la série évitées | Des 10 plus gros gagnants | Q1 | Q2 | Q3 | Q4 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| TOUS | 448 | 107 | 24 % | **+6'096 $** | +2'339 $ | 0 / 25 | 10 / 10 | +2'861 $ | +999 $ | +779 $ | +1'456 $ |
| 0 retournement (≥ 10 pts) | 205 | 52 | 25 % | **+1'657 $** | −849 $ | 6 / 25 | 2 / 10 | +2'226 $ | −1'583 $ | +67 $ | +947 $ |
| 1 retournement | 97 | 18 | 19 % | **+1'713 $** | −849 $ | 20 / 25 | 4 / 10 | +738 $ | +1'881 $ | −437 $ | −469 $ |
| 2 retournements | 44 | 12 | 27 % | **+583 $** | −364 $ | 24 / 25 | 0 / 10 | −325 $ | −12 $ | +689 $ | +232 $ |
| 3 et plus | 102 | 25 | 25 % | **+2'142 $** | +129 $ | 25 / 25 | 4 / 10 | +222 $ | +713 $ | +460 $ | +746 $ |
| agitation 30 s faible (< 0.018) | 141 | 29 | 21 % | **−246 $** | −2'086 $ | 9 / 25 | 1 / 10 | +1'363 $ | −1'197 $ | −363 $ | −49 $ |
| agitation moyenne | 157 | 39 | 25 % | **+4'355 $** | +1'015 $ | 19 / 25 | 6 / 10 | +709 $ | +2'300 $ | +168 $ | +1'178 $ |
| agitation forte (≥ 0.034) | 150 | 39 | 26 % | **+1'986 $** | +511 $ | 22 / 25 | 3 / 10 | +788 $ | −104 $ | +974 $ | +328 $ |

## Test 2 — miroir temporel (modèle en retard, carnet inchangé)

| Groupe / filtre | Trades | Gagnés | % gagnés | Résultat | Sans top 3 | Pertes de la série évitées | Des 10 plus gros gagnants | Q1 | Q2 | Q3 | Q4 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| TOUS | 448 | 107 | 24 % | **+6'096 $** | +2'339 $ | 0 / 25 | 10 / 10 | +2'861 $ | +999 $ | +779 $ | +1'456 $ |
| signal encore là avec 0.25 s de retard | 163 | 37 | 23 % | **−291 $** | −1'318 $ | 10 / 25 | 0 / 10 | +242 $ | −1'402 $ | −111 $ | +980 $ |
| signal disparaît avec 0.25 s de retard | 285 | 70 | 25 % | **+6'387 $** | +2'630 $ | 15 / 25 | 10 / 10 | +2'619 $ | +2'402 $ | +890 $ | +476 $ |
| signal encore là avec 0.5 s de retard | 160 | 36 | 22 % | **+8 $** | −1'259 $ | 10 / 25 | 1 / 10 | +178 $ | −1'137 $ | −728 $ | +1'695 $ |
| signal disparaît avec 0.5 s de retard | 288 | 71 | 25 % | **+6'088 $** | +2'332 $ | 15 / 25 | 9 / 10 | +2'683 $ | +2'136 $ | +1'507 $ | −239 $ |
| signal encore là avec 1.0 s de retard | 176 | 39 | 22 % | **−813 $** | −1'812 $ | 10 / 25 | 0 / 10 | −33 $ | −994 $ | −618 $ | +833 $ |
| signal disparaît avec 1.0 s de retard | 272 | 68 | 25 % | **+6'908 $** | +3'152 $ | 15 / 25 | 10 / 10 | +2'894 $ | +1'993 $ | +1'397 $ | +623 $ |
| signal encore là avec 2.0 s de retard | 180 | 40 | 22 % | **−383 $** | −1'409 $ | 9 / 25 | 0 / 10 | +30 $ | −801 $ | −665 $ | +1'054 $ |
| signal disparaît avec 2.0 s de retard | 268 | 67 | 25 % | **+6'478 $** | +2'722 $ | 16 / 25 | 10 / 10 | +2'831 $ | +1'800 $ | +1'444 $ | +403 $ |
| solide : là aux 4 retards | 115 | 27 | 23 % | **+43 $** | −873 $ | 12 / 25 | 0 / 10 | +233 $ | −714 $ | −352 $ | +877 $ |
| fragile : disparaît à au moins un retard | 333 | 80 | 24 % | **+6'053 $** | +2'297 $ | 13 / 25 | 10 / 10 | +2'629 $ | +1'713 $ | +1'131 $ | +580 $ |

## Test 3 — d'où vient la hausse du modèle sur 3 s (nouveauté de l'information)

| Groupe / filtre | Trades | Gagnés | % gagnés | Résultat | Sans top 3 | Pertes de la série évitées | Des 10 plus gros gagnants | Q1 | Q2 | Q3 | Q4 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| TOUS | 448 | 107 | 24 % | **+6'096 $** | +2'339 $ | 0 / 25 | 10 / 10 | +2'861 $ | +999 $ | +779 $ | +1'456 $ |
| prix BTC | 156 | 37 | 24 % | **+2'359 $** | −417 $ | 20 / 25 | 5 / 10 | +1'796 $ | +1'187 $ | +306 $ | −931 $ |
| temps qui passe | 0 | | | | | | | | | | |
| volatilite | 0 | | | | | | | | | | |
| modele stable | 291 | 70 | 24 % | **+3'789 $** | +866 $ | 5 / 25 | 5 / 10 | +1'065 $ | −188 $ | +473 $ | +2'439 $ |
| non calculable | 1 | 0 | 0 % | **−52 $** | +0 $ | 25 / 25 | 0 / 10 | +0 $ | +0 $ | +0 $ | −52 $ |

Dans « modèle stable », c'est Polymarket qui a bougé (le modèle n'a pas pris 2 pts).

## Test 4 — consensus interne (5 variantes du modèle)

| Groupe / filtre | Trades | Gagnés | % gagnés | Résultat | Sans top 3 | Pertes de la série évitées | Des 10 plus gros gagnants | Q1 | Q2 | Q3 | Q4 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| TOUS | 448 | 107 | 24 % | **+6'096 $** | +2'339 $ | 0 / 25 | 10 / 10 | +2'861 $ | +999 $ | +779 $ | +1'456 $ |
| variantes proches (dispersion < 8 pts) | 147 | 40 | 27 % | **+377 $** | −475 $ | 19 / 25 | 1 / 10 | +673 $ | +339 $ | −512 $ | −124 $ |
| dispersion moyenne | 152 | 42 | 28 % | **+4'565 $** | +2'386 $ | 17 / 25 | 6 / 10 | +1'423 $ | −675 $ | +1'691 $ | +2'126 $ |
| variantes en désaccord (≥ 14 pts) | 148 | 25 | 17 % | **+1'206 $** | −2'384 $ | 14 / 25 | 3 / 10 | +765 $ | +1'335 $ | −400 $ | −493 $ |
| toutes les variantes voient ≥ 20 pts d'écart | 62 | 20 | 32 % | **+412 $** | −250 $ | 21 / 25 | 0 / 10 | +401 $ | −250 $ | +304 $ | −42 $ |
| au moins une variante ne voit pas 20 pts | 385 | 87 | 23 % | **+5'736 $** | +1'979 $ | 4 / 25 | 10 / 10 | +2'460 $ | +1'250 $ | +475 $ | +1'551 $ |
| la variante « marge corrigée » voit ≥ 20 pts | 121 | 43 | 36 % | **+890 $** | +171 $ | 20 / 25 | 0 / 10 | +777 $ | −502 $ | +492 $ | +123 $ |
| la variante « Chainlink seul » voit ≥ 20 pts | 239 | 59 | 25 % | **+3'974 $** | +1'050 $ | 7 / 25 | 4 / 10 | +1'127 $ | −13 $ | +1'596 $ | +1'263 $ |
| la variante « vol 60 s » voit ≥ 20 pts | 286 | 73 | 26 % | **+5'978 $** | +2'222 $ | 7 / 25 | 8 / 10 | +3'382 $ | +118 $ | +1'178 $ | +1'301 $ |

## Test 5 — mémoire des erreurs (pause si les trades récents déjà réglés sont trop mauvais)

On ne regarde que les trades déjà réglés au moment de l'achat. Somme sur les N derniers de (1 si gagné sinon 0) − prix payé = notre vrai avantage récent contre Polymarket ; ou − modèle = l'erreur du modèle.

| Groupe / filtre | Trades | Gagnés | % gagnés | Résultat | Sans top 3 | Pertes de la série évitées | Des 10 plus gros gagnants | Q1 | Q2 | Q3 | Q4 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| TOUS (aucune pause) | 448 | 107 | 24 % | **+6'096 $** | +2'339 $ | 0 / 25 | 10 / 10 | +2'861 $ | +999 $ | +779 $ | +1'456 $ |
| pause si somme(résultat − prix) sur 20 derniers < -1 | 373 | 94 | 25 % | **+6'814 $** | +3'058 $ | 16 / 25 | 9 / 10 | +2'861 $ | +2'409 $ | −22 $ | +1'567 $ |
| pause si somme(résultat − prix) sur 20 derniers < -2 | 403 | 101 | 25 % | **+7'233 $** | +3'477 $ | 15 / 25 | 10 / 10 | +2'861 $ | +2'372 $ | +699 $ | +1'301 $ |
| pause si somme(résultat − prix) sur 20 derniers < -3 | 439 | 104 | 24 % | **+5'949 $** | +2'193 $ | 5 / 25 | 10 / 10 | +2'861 $ | +852 $ | +779 $ | +1'456 $ |
| pause si somme(résultat − prix) sur 30 derniers < -2 | 406 | 100 | 25 % | **+6'708 $** | +2'952 $ | 8 / 25 | 10 / 10 | +2'861 $ | +2'038 $ | +353 $ | +1'456 $ |
| pause si somme(résultat − prix) sur 30 derniers < -3 | 413 | 103 | 25 % | **+7'096 $** | +3'340 $ | 6 / 25 | 10 / 10 | +2'861 $ | +2'000 $ | +779 $ | +1'456 $ |
| pause si somme(résultat − prix) sur 30 derniers < -4 | 434 | 104 | 24 % | **+6'213 $** | +2'457 $ | 5 / 25 | 10 / 10 | +2'861 $ | +1'117 $ | +779 $ | +1'456 $ |
| pause si somme(résultat − modele) sur 20 derniers < -3 | 199 | 45 | 23 % | **+1'990 $** | −225 $ | 20 / 25 | 5 / 10 | +2'404 $ | −651 $ | +9 $ | +228 $ |
| pause si somme(résultat − modele) sur 20 derniers < -4 | 272 | 73 | 27 % | **+6'325 $** | +2'735 $ | 19 / 25 | 8 / 10 | +2'757 $ | +2'634 $ | +88 $ | +846 $ |
| pause si somme(résultat − modele) sur 20 derniers < -5 | 340 | 83 | 24 % | **+5'206 $** | +1'616 $ | 18 / 25 | 8 / 10 | +2'617 $ | +2'264 $ | +55 $ | +270 $ |
| pause si somme(résultat − modele) sur 30 derniers < -5 | 225 | 54 | 24 % | **+4'168 $** | +578 $ | 18 / 25 | 6 / 10 | +2'499 $ | +2'155 $ | −205 $ | −282 $ |
| pause si somme(résultat − modele) sur 30 derniers < -6 | 297 | 71 | 24 % | **+4'534 $** | +944 $ | 15 / 25 | 8 / 10 | +2'407 $ | +1'805 $ | −61 $ | +383 $ |
| pause si somme(résultat − modele) sur 30 derniers < -7 | 344 | 84 | 24 % | **+4'662 $** | +1'073 $ | 11 / 25 | 8 / 10 | +2'820 $ | +1'657 $ | −222 $ | +408 $ |

## Combinaisons

| Groupe / filtre | Trades | Gagnés | % gagnés | Résultat | Sans top 3 | Pertes de la série évitées | Des 10 plus gros gagnants | Q1 | Q2 | Q3 | Q4 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| TOUS | 448 | 107 | 24 % | **+6'096 $** | +2'339 $ | 0 / 25 | 10 / 10 | +2'861 $ | +999 $ | +779 $ | +1'456 $ |
| écart né dans la dernière seconde (disparaît avec 1 s de retard) | 272 | 68 | 25 % | **+6'908 $** | +3'152 $ | 15 / 25 | 10 / 10 | +2'894 $ | +1'993 $ | +1'397 $ | +623 $ |
| écart né dans la dernière 0,25 s | 285 | 70 | 25 % | **+6'387 $** | +2'630 $ | 15 / 25 | 10 / 10 | +2'619 $ | +2'402 $ | +890 $ | +476 $ |
| pause (résultat − prix, 20 derniers < −2) | 403 | 101 | 25 % | **+7'233 $** | +3'477 $ | 15 / 25 | 10 / 10 | +2'861 $ | +2'372 $ | +699 $ | +1'301 $ |
| écart né dans la dernière seconde + pause | 253 | 66 | 26 % | **+7'459 $** | +3'703 $ | 21 / 25 | 10 / 10 | +2'894 $ | +2'544 $ | +1'397 $ | +623 $ |
| écart né dans la dernière seconde + pas « les deux baissent » | 257 | 66 | 26 % | **+7'159 $** | +3'402 $ | 16 / 25 | 10 / 10 | +3'211 $ | +1'850 $ | +1'316 $ | +783 $ |
| écart né dans la dernière seconde + pas « les deux baissent » + pause | 239 | 64 | 27 % | **+7'656 $** | +3'900 $ | 21 / 25 | 10 / 10 | +3'211 $ | +2'347 $ | +1'316 $ | +783 $ |
| pas « les deux baissent » (déjà en fantôme) | 360 | 93 | 26 % | **+7'578 $** | +3'821 $ | 7 / 25 | 10 / 10 | +3'399 $ | +1'754 $ | +1'257 $ | +1'168 $ |
| vol 60 s voit ≥ 20 pts + écart né dans la dernière seconde | 177 | 45 | 25 % | **+5'353 $** | +1'597 $ | 18 / 25 | 8 / 10 | +2'932 $ | +979 $ | +1'294 $ | +147 $ |

Robustesse — première moitié / seconde moitié des trades :

- TOUS : +3'860 $ / +2'235 $
- écart né dans la dernière seconde : +4'888 $ / +2'021 $
- pause −2 : +5'233 $ / +2'000 $
- écart né dernière seconde + pause : +5'438 $ / +2'021 $