# BOT95 V3 — Expérience 002 : micro-âge du désaccord

928 cycles BTC 5 min réglés (07.10 08:00 → 10.10 13:45, heure suisse). Apprentissage 455 cycles (< 08.10 22:00) · validation 433 (→ 10.10 10:25) · test inédit 40 cycles seulement (après 10.10 10:25) — le test est minuscule, aucun verdict ne peut s'y appuyer seul.

**Résolution** : les lignes enregistrées arrivent toutes les ~0,3 s (voir l'audit). Un âge mesuré de 0 veut dire « franchi depuis la ligne précédente », c'est-à-dire entre 0 et ~300 ms ; 0,3 s mesuré = 300-600 ms réels, etc. Les tranches 0-250 / 250-500 ms sont donc approximatives, et **les fenêtres 0-50 ms et 50-100 ms ne sont pas mesurables avec les données actuelles** : le nouveau programme du VPS de Dublin (`bot95/rapide/rapide.js`) les mesurera à la milliseconde.

Exécution : meilleur vendeur seul, quantité affichée, prix ≤ prix de décision, 50 $ max, frais inclus ; délai 0 (ligne de décision) et délai 0,5 s demandé (~0,6 s réel).

## A. Âge du désaccord au moment des signaux V2-F

« Nouveau » = l'épisode en cours est le premier du cycle de ce côté ; « reprise » = un écart ≥ 0,20 de ce côté avait déjà existé puis disparu dans le cycle.

### V2-F original (O8) — toutes périodes

| Âge de l'épisode | Achats | Gagnés | Résultat net | Espérance / achat | sans top 1 | sans top 3 | sans top 5 | sans top 10 | Creux max | Facteur de profit | IC 90 % (blocs 1 h) | Signaux | Prix payé moyen | Taille affichée médiane (parts) | Écart médian | Résultat délai 0,5 s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0-250 ms (vu à la ligne même du franchissement) | 604 | 21 % | **−2 458 $** | −4,07 $ | −3 030 $ | −3 861 $ | −4 588 $ | −6 167 $ | −3 950 $ | 0,85 | [−5 875 $ ; +1 135 $] | 605 | 0.20 | 273 | 0.21 | −2 875 $ |
| 250-500 ms (1 ligne plus tard) | 46 | 30 % | **+1 322 $** | +28,75 $ | +921 $ | +279 $ | −103 $ | −914 $ | −290 $ | 2,06 | [+27 $ ; +2 714 $] | 46 | 0.20 | 562 | 0.21 | +876 $ |
| 500-1000 ms (2-3 lignes) | 30 | 17 % | **−357 $** | −11,90 $ | −522 $ | −697 $ | −776 $ | −762 $ | −532 $ | 0,54 | [−773 $ ; +107 $] | 30 | 0.18 | 267 | 0.21 | −298 $ |
| > 1000 ms | 78 | 23 % | **+524 $** | +6,71 $ | −24 $ | −690 $ | −1 072 $ | −1 828 $ | −639 $ | 1,22 | [−993 $ ; +2 130 $] | 78 | 0.20 | 438 | 0.24 | −163 $ |
| nouveau (1er épisode du cycle) | 618 | 22 % | **−574 $** | −0,93 $ | −1 146 $ | −2 124 $ | −2 911 $ | −4 601 $ | −2 723 $ | 0,97 | [−4 405 $ ; +3 454 $] | 618 | 0.20 | 304 | 0.21 | −2 193 $ |
| reprise (épisode déjà vu puis disparu) | 140 | 20 % | **−395 $** | −2,82 $ | −796 $ | −1 508 $ | −1 991 $ | −2 920 $ | −1 126 $ | 0,90 | [−2 064 $ ; +1 207 $] | 141 | 0.19 | 293 | 0.22 | −267 $ |

### V2-F original (O8) — apprentissage

| Âge de l'épisode | Achats | Gagnés | Résultat net | Espérance / achat | sans top 1 | sans top 3 | sans top 5 | sans top 10 | Creux max | Facteur de profit | IC 90 % (blocs 1 h) | Signaux | Prix payé moyen | Taille affichée médiane (parts) | Écart médian | Résultat délai 0,5 s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0-250 ms (vu à la ligne même du franchissement) | 277 | 22 % | **−579 $** | −2,09 $ | −1 009 $ | −1 774 $ | −2 469 $ | −3 828 $ | −2 081 $ | 0,92 | [−2 969 $ ; +2 085 $] | 277 | 0.19 | 239 | 0.21 | −848 $ |
| 250-500 ms (1 ligne plus tard) | 18 | 33 % | **+504 $** | +28,00 $ | +193 $ | −177 $ | −415 $ | −382 $ | −135 $ | 2,21 | [−172 $ ; +1 293 $] | 18 | 0.22 | 406 | 0.21 | +538 $ |
| 500-1000 ms (2-3 lignes) | 14 | 21 % | **+10 $** | +0,70 $ | −96 $ | −212 $ | −208 $ | −175 $ | −165 $ | 1,05 | [−295 $ ; +377 $] | 14 | 0.19 | 106 | 0.21 | +70 $ |
| > 1000 ms | 30 | 33 % | **+658 $** | +21,94 $ | +234 $ | −127 $ | −439 $ | −787 $ | −261 $ | 1,84 | [−242 $ ; +1 629 $] | 30 | 0.21 | 318 | 0.24 | +664 $ |
| nouveau (1er épisode du cycle) | 274 | 24 % | **+495 $** | +1,81 $ | +66 $ | −722 $ | −1 417 $ | −2 732 $ | −1 534 $ | 1,08 | [−1 977 $ ; +3 280 $] | 274 | 0.19 | 226 | 0.21 | +269 $ |
| reprise (épisode déjà vu puis disparu) | 65 | 20 % | **+98 $** | +1,50 $ | −304 $ | −855 $ | −1 238 $ | −1 752 $ | −596 $ | 1,05 | [−1 029 $ ; +1 277 $] | 65 | 0.20 | 276 | 0.21 | +156 $ |

### V2-F original (O8) — validation

| Âge de l'épisode | Achats | Gagnés | Résultat net | Espérance / achat | sans top 1 | sans top 3 | sans top 5 | sans top 10 | Creux max | Facteur de profit | IC 90 % (blocs 1 h) | Signaux | Prix payé moyen | Taille affichée médiane (parts) | Écart médian | Résultat délai 0,5 s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0-250 ms (vu à la ligne même du franchissement) | 293 | 22 % | **−989 $** | −3,38 $ | −1 561 $ | −2 173 $ | −2 655 $ | −3 741 $ | −1 879 $ | 0,88 | [−3 306 $ ; +1 339 $] | 294 | 0.21 | 328 | 0.21 | −1 129 $ |
| 250-500 ms (1 ligne plus tard) | 26 | 27 % | **+702 $** | +26,99 $ | +300 $ | −228 $ | −551 $ | −795 $ | −290 $ | 1,85 | [−252 $ ; +1 808 $] | 26 | 0.19 | 657 | 0.21 | +326 $ |
| 500-1000 ms (2-3 lignes) | 16 | 12 % | **−367 $** | −22,92 $ | −531 $ | −560 $ | −534 $ | −318 $ | −399 $ | 0,35 | [−611 $ ; −114 $] | 16 | 0.17 | 700 | 0.21 | −369 $ |
| > 1000 ms | 44 | 16 % | **−57 $** | −1,30 $ | −605 $ | −1 032 $ | −1 297 $ | −1 453 $ | −599 $ | 0,96 | [−1 164 $ ; +1 288 $] | 44 | 0.18 | 525 | 0.25 | −774 $ |
| nouveau (1er épisode du cycle) | 309 | 22 % | **−107 $** | −0,35 $ | −678 $ | −1 558 $ | −2 170 $ | −3 331 $ | −1 808 $ | 0,99 | [−2 811 $ ; +2 767 $] | 309 | 0.21 | 384 | 0.21 | −1 564 $ |
| reprise (épisode déjà vu puis disparu) | 70 | 17 % | **−605 $** | −8,64 $ | −1 006 $ | −1 444 $ | −1 765 $ | −2 180 $ | −1 126 $ | 0,72 | [−1 749 $ ; +555 $] | 71 | 0.18 | 371 | 0.22 | −382 $ |

### V2-F original (O8) — inédit

| Âge de l'épisode | Achats | Gagnés | Résultat net | Espérance / achat | sans top 1 | sans top 3 | sans top 5 | sans top 10 | Creux max | Facteur de profit | IC 90 % (blocs 1 h) | Signaux | Prix payé moyen | Taille affichée médiane (parts) | Écart médian | Résultat délai 0,5 s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0-250 ms (vu à la ligne même du franchissement) | 34 | 18 % | **−890 $** | −26,17 $ | −1 010 $ | −1 123 $ | −1 153 $ | −1 143 $ | −1 065 $ | 0,23 | [−1 234 $ ; −546 $] | 34 | 0.25 | 310 | 0.21 | −898 $ |
| 250-500 ms (1 ligne plus tard) | 2 | 50 % | **+117 $** | +58,28 $ | −3 $ | +0 $ | +0 $ | +0 $ | −3 $ | 36,42 | [−7 $ ; +240 $] | 2 | 0.27 | 425 | 0.21 | +11 $ |
| 500-1000 ms (2-3 lignes) | 0 | — | 0 $ | — | — | — | — | — | — | — | — | 0 | nan | 0 | nan | +0 $ |
| > 1000 ms | 4 | 25 % | **−78 $** | −19,39 $ | −113 $ | −53 $ | +0 $ | +0 $ | −78 $ | 0,31 | [−219 $ ; +54 $] | 4 | 0.20 | 210 | 0.25 | −53 $ |
| nouveau (1er épisode du cycle) | 35 | 14 % | **−963 $** | −27,51 $ | −1 083 $ | −1 196 $ | −1 214 $ | −1 196 $ | −1 085 $ | 0,21 | [−1 237 $ ; −655 $] | 35 | 0.25 | 318 | 0.21 | −898 $ |
| reprise (épisode déjà vu puis disparu) | 5 | 60 % | **+112 $** | +22,40 $ | −8 $ | −60 $ | +0 $ | +0 $ | −60 $ | 2,87 | [−120 $ ; +344 $] | 5 | 0.26 | 49 | 0.21 | −42 $ |

Répartition des âges (V2-F original (O8), 759 signaux) : médiane 0.0 s, 75 % 0.0 s, 90 % 1.2 s ; âge depuis le 1er franchissement du cycle : médiane 0.0 s.

### V2-F 0,01 % (H1) — toutes périodes

| Âge de l'épisode | Achats | Gagnés | Résultat net | Espérance / achat | sans top 1 | sans top 3 | sans top 5 | sans top 10 | Creux max | Facteur de profit | IC 90 % (blocs 1 h) | Signaux | Prix payé moyen | Taille affichée médiane (parts) | Écart médian | Résultat délai 0,5 s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0-250 ms (vu à la ligne même du franchissement) | 453 | 39 % | **+3 868 $** | +8,54 $ | +3 453 $ | +2 720 $ | +2 121 $ | +860 $ | −914 $ | 1,45 | [+1 772 $ ; +6 108 $] | 455 | 0.29 | 168 | 0.22 | +672 $ |
| 250-500 ms (1 ligne plus tard) | 12 | 25 % | **−169 $** | −14,06 $ | −366 $ | −401 $ | −369 $ | −106 $ | −268 $ | 0,58 | [−517 $ ; +292 $] | 12 | 0.26 | 566 | 0.22 | −407 $ |
| 500-1000 ms (2-3 lignes) | 9 | 44 % | **+36 $** | +3,97 $ | −51 $ | −168 $ | −176 $ | +0 $ | −145 $ | 1,20 | [−194 $ ; +276 $] | 9 | 0.32 | 263 | 0.23 | +40 $ |
| > 1000 ms | 33 | 33 % | **+59 $** | +1,78 $ | −138 $ | −450 $ | −701 $ | −946 $ | −362 $ | 1,06 | [−562 $ ; +806 $] | 33 | 0.28 | 881 | 0.25 | −196 $ |
| nouveau (1er épisode du cycle) | 449 | 38 % | **+3 002 $** | +6,69 $ | +2 587 $ | +1 854 $ | +1 275 $ | +64 $ | −981 $ | 1,35 | [+801 $ ; +5 269 $] | 451 | 0.29 | 175 | 0.22 | −440 $ |
| reprise (épisode déjà vu puis disparu) | 58 | 36 % | **+792 $** | +13,65 $ | +512 $ | +117 $ | −204 $ | −835 $ | −343 $ | 1,58 | [−114 $ ; +1 836 $] | 58 | 0.28 | 268 | 0.22 | +549 $ |

### V2-F 0,01 % (H1) — apprentissage

| Âge de l'épisode | Achats | Gagnés | Résultat net | Espérance / achat | sans top 1 | sans top 3 | sans top 5 | sans top 10 | Creux max | Facteur de profit | IC 90 % (blocs 1 h) | Signaux | Prix payé moyen | Taille affichée médiane (parts) | Écart médian | Résultat délai 0,5 s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0-250 ms (vu à la ligne même du franchissement) | 206 | 39 % | **+2 276 $** | +11,05 $ | +1 875 $ | +1 356 $ | +855 $ | −108 $ | −243 $ | 1,70 | [+1 088 $ ; +3 568 $] | 207 | 0.28 | 98 | 0.22 | +606 $ |
| 250-500 ms (1 ligne plus tard) | 5 | 40 % | **+47 $** | +9,32 $ | −151 $ | −105 $ | +0 $ | +0 $ | −105 $ | 1,30 | [−256 $ ; +441 $] | 5 | 0.27 | 647 | 0.23 | −158 $ |
| 500-1000 ms (2-3 lignes) | 6 | 50 % | **−11 $** | −1,88 $ | −94 $ | −140 $ | −53 $ | −0 $ | −140 $ | 0,92 | [−193 $ ; +188 $] | 6 | 0.35 | 281 | 0.23 | +12 $ |
| > 1000 ms | 16 | 38 % | **+39 $** | +2,41 $ | −126 $ | −343 $ | −425 $ | −315 $ | −309 $ | 1,09 | [−421 $ ; +517 $] | 16 | 0.30 | 364 | 0.26 | −199 $ |
| nouveau (1er épisode du cycle) | 204 | 40 % | **+2 073 $** | +10,16 $ | +1 671 $ | +1 152 $ | +652 $ | −299 $ | −260 $ | 1,62 | [+701 $ ; +3 514 $] | 205 | 0.28 | 100 | 0.22 | +117 $ |
| reprise (épisode déjà vu puis disparu) | 29 | 34 % | **+277 $** | +9,56 $ | +80 $ | −264 $ | −475 $ | −638 $ | −212 $ | 1,43 | [−303 $ ; +919 $] | 29 | 0.26 | 206 | 0.23 | +146 $ |

### V2-F 0,01 % (H1) — validation

| Âge de l'épisode | Achats | Gagnés | Résultat net | Espérance / achat | sans top 1 | sans top 3 | sans top 5 | sans top 10 | Creux max | Facteur de profit | IC 90 % (blocs 1 h) | Signaux | Prix payé moyen | Taille affichée médiane (parts) | Écart médian | Résultat délai 0,5 s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0-250 ms (vu à la ligne même du franchissement) | 217 | 40 % | **+1 984 $** | +9,14 $ | +1 569 $ | +918 $ | +397 $ | −463 $ | −608 $ | 1,44 | [+347 $ ; +3 670 $] | 218 | 0.30 | 220 | 0.22 | +578 $ |
| 250-500 ms (1 ligne plus tard) | 6 | 17 % | **−162 $** | −27,08 $ | −190 $ | −158 $ | −53 $ | +0 $ | −190 $ | 0,15 | [−303 $ ; −53 $] | 6 | 0.26 | 474 | 0.22 | −197 $ |
| 500-1000 ms (2-3 lignes) | 3 | 33 % | **+47 $** | +15,67 $ | −40 $ | +0 $ | +0 $ | +0 $ | −40 $ | 2,19 | [−79 $ ; +220 $] | 3 | 0.27 | 263 | 0.23 | +28 $ |
| > 1000 ms | 17 | 29 % | **+20 $** | +1,19 $ | −177 $ | −428 $ | −521 $ | −369 $ | −238 $ | 1,04 | [−464 $ ; +547 $] | 17 | 0.26 | 1147 | 0.25 | +3 $ |
| nouveau (1er épisode du cycle) | 215 | 38 % | **+1 335 $** | +6,21 $ | +919 $ | +269 $ | −174 $ | −989 $ | −523 $ | 1,29 | [−321 $ ; +3 161 $] | 216 | 0.29 | 223 | 0.22 | +5 $ |
| reprise (épisode déjà vu puis disparu) | 28 | 39 % | **+554 $** | +19,80 $ | +274 $ | −48 $ | −320 $ | −671 $ | −285 $ | 1,80 | [−212 $ ; +1 338 $] | 28 | 0.29 | 610 | 0.22 | +406 $ |

### V2-F 0,01 % (H1) — inédit

| Âge de l'épisode | Achats | Gagnés | Résultat net | Espérance / achat | sans top 1 | sans top 3 | sans top 5 | sans top 10 | Creux max | Facteur de profit | IC 90 % (blocs 1 h) | Signaux | Prix payé moyen | Taille affichée médiane (parts) | Écart médian | Résultat délai 0,5 s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0-250 ms (vu à la ligne même du franchissement) | 30 | 27 % | **−392 $** | −13,07 $ | −512 $ | −640 $ | −696 $ | −727 $ | −585 $ | 0,46 | [−603 $ ; −54 $] | 30 | 0.30 | 168 | 0.23 | −512 $ |
| 250-500 ms (1 ligne plus tard) | 1 | 0 % | **−53 $** | −52,84 $ | +0 $ | +0 $ | +0 $ | +0 $ | −53 $ | 0,00 | [−159 $ ; +0 $] | 1 | 0.21 | 1701 | 0.20 | −53 $ |
| 500-1000 ms (2-3 lignes) | 0 | — | 0 $ | — | — | — | — | — | — | — | — | 0 | nan | 0 | nan | +0 $ |
| > 1000 ms | 0 | — | 0 $ | — | — | — | — | — | — | — | — | 0 | nan | 0 | nan | +0 $ |
| nouveau (1er épisode du cycle) | 30 | 27 % | **−405 $** | −13,50 $ | −525 $ | −653 $ | −709 $ | −740 $ | −598 $ | 0,46 | [−640 $ ; −170 $] | 30 | 0.30 | 172 | 0.22 | −562 $ |
| reprise (épisode déjà vu puis disparu) | 1 | 0 % | **−40 $** | −39,95 $ | +0 $ | +0 $ | +0 $ | +0 $ | −40 $ | 0,00 | [−80 $ ; +0 $] | 1 | 0.21 | 180 | 0.23 | −2 $ |

Répartition des âges (V2-F 0,01 % (H1), 509 signaux) : médiane 0.0 s, 75 % 0.0 s, 90 % 0.3 s ; âge depuis le 1er franchissement du cycle : médiane 0.0 s.

## B. Premier désaccord ≥ 0,20 du cycle (modèle du bot O8) : décider à 0, 0,25, 0,5, 1 ou 2 s d'âge

Pour le signal « désaccord 20 » l'âge au signal est 0 par construction (premier franchissement du cycle). On mesure donc ce que vaut la MÊME opportunité si on décide plus tard : à l'âge X, on regarde la première ligne à t0 + X ou après ; si l'écart est resté ≥ 0,20 sans interruption, on achète au meilleur vendeur de CETTE ligne (nouvelle décision, prix du moment). « Mêmes cycles à l'âge 0 » = résultat de ces mêmes cycles achetés au franchissement : la différence isole l'effet du temps (prix et sélection des épisodes qui survivent).

### toutes périodes (773 premiers désaccords)

| Âge de décision | Achats | Gagnés | Résultat net | Espérance / achat | sans top 1 | sans top 3 | sans top 5 | sans top 10 | Creux max | Facteur de profit | IC 90 % (blocs 1 h) | Épisodes encore vivants | Âge réel médian | Prix payé moyen | Taille affichée médiane | Mêmes cycles à l'âge 0 | Délai d'exécution 0,5 s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 s | 765 | 22 % | **−436 $** | −0,57 $ | −1 008 $ | −2 067 $ | −3 016 $ | −4 951 $ | −3 458 $ | 0,98 | [−4 740 $ ; +4 283 $] | 765 (99 %) | 0.00 s | 0.20 | 312 | −436 $ | −693 $ |
| 0.25 s | 512 | 21 % | **−1 033 $** | −2,02 $ | −1 980 $ | −3 123 $ | −4 072 $ | −5 850 $ | −3 912 $ | 0,94 | [−5 134 $ ; +2 998 $] | 512 (66 %) | 0.30 s | 0.20 | 488 | −828 $ | −1 931 $ |
| 0.5 s | 421 | 21 % | **+274 $** | +0,65 $ | −673 $ | −1 816 $ | −2 765 $ | −4 543 $ | −3 265 $ | 1,02 | [−3 415 $ ; +4 280 $] | 421 (54 %) | 0.60 s | 0.20 | 485 | +371 $ | −781 $ |
| 1 s | 297 | 21 % | **+326 $** | +1,10 $ | −245 $ | −1 184 $ | −2 078 $ | −3 465 $ | −2 393 $ | 1,03 | [−2 542 $ ; +3 590 $] | 297 (38 %) | 1.20 s | 0.20 | 651 | +85 $ | −297 $ |
| 2 s | 225 | 20 % | **−854 $** | −3,80 $ | −1 426 $ | −2 319 $ | −2 962 $ | −4 009 $ | −2 352 $ | 0,89 | [−3 491 $ ; +1 838 $] | 225 (29 %) | 2.10 s | 0.20 | 699 | −602 $ | +81 $ |

### apprentissage (348 premiers désaccords)

| Âge de décision | Achats | Gagnés | Résultat net | Espérance / achat | sans top 1 | sans top 3 | sans top 5 | sans top 10 | Creux max | Facteur de profit | IC 90 % (blocs 1 h) | Épisodes encore vivants | Âge réel médian | Prix payé moyen | Taille affichée médiane | Mêmes cycles à l'âge 0 | Délai d'exécution 0,5 s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 s | 346 | 23 % | **+364 $** | +1,05 $ | −193 $ | −1 142 $ | −1 935 $ | −3 507 $ | −2 517 $ | 1,04 | [−2 737 $ ; +3 878 $] | 346 (99 %) | 0.00 s | 0.19 | 238 | +364 $ | +865 $ |
| 0.25 s | 205 | 20 % | **+193 $** | +0,94 $ | −754 $ | −1 772 $ | −2 418 $ | −3 462 $ | −2 220 $ | 1,03 | [−2 482 $ ; +3 124 $] | 205 (59 %) | 0.30 s | 0.19 | 295 | −109 $ | −246 $ |
| 0.5 s | 163 | 21 % | **+1 144 $** | +7,02 $ | +197 $ | −821 $ | −1 426 $ | −2 427 $ | −1 584 $ | 1,26 | [−1 367 $ ; +4 039 $] | 163 (47 %) | 0.60 s | 0.19 | 365 | +314 $ | +354 $ |
| 1 s | 108 | 21 % | **+762 $** | +7,05 $ | +190 $ | −620 $ | −1 016 $ | −1 892 $ | −1 115 $ | 1,23 | [−1 074 $ ; +2 619 $] | 108 (31 %) | 1.20 s | 0.18 | 463 | +493 $ | +701 $ |
| 2 s | 71 | 20 % | **−106 $** | −1,50 $ | −553 $ | −1 196 $ | −1 570 $ | −2 094 $ | −1 326 $ | 0,95 | [−1 479 $ ; +1 456 $] | 71 (20 %) | 2.10 s | 0.18 | 469 | +101 $ | +438 $ |

### validation (385 premiers désaccords)

| Âge de décision | Achats | Gagnés | Résultat net | Espérance / achat | sans top 1 | sans top 3 | sans top 5 | sans top 10 | Creux max | Facteur de profit | IC 90 % (blocs 1 h) | Épisodes encore vivants | Âge réel médian | Prix payé moyen | Taille affichée médiane | Mêmes cycles à l'âge 0 | Délai d'exécution 0,5 s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 s | 379 | 21 % | **−105 $** | −0,28 $ | −677 $ | −1 626 $ | −2 289 $ | −3 489 $ | −2 812 $ | 0,99 | [−3 073 $ ; +3 062 $] | 379 (98 %) | 0.00 s | 0.21 | 382 | −105 $ | −684 $ |
| 0.25 s | 272 | 22 % | **−484 $** | −1,78 $ | −1 055 $ | −2 004 $ | −2 667 $ | −3 944 $ | −3 308 $ | 0,95 | [−3 385 $ ; +2 624 $] | 272 (71 %) | 0.30 s | 0.21 | 672 | +129 $ | −1 026 $ |
| 0.5 s | 228 | 23 % | **+88 $** | +0,39 $ | −484 $ | −1 433 $ | −2 096 $ | −3 318 $ | −2 387 $ | 1,01 | [−2 617 $ ; +3 038 $] | 228 (59 %) | 0.60 s | 0.21 | 671 | +971 $ | −519 $ |
| 1 s | 168 | 22 % | **+129 $** | +0,77 $ | −363 $ | −1 257 $ | −1 830 $ | −2 804 $ | −2 114 $ | 1,02 | [−2 125 $ ; +2 683 $] | 168 (44 %) | 1.20 s | 0.21 | 814 | +147 $ | −431 $ |
| 2 s | 134 | 22 % | **−187 $** | −1,40 $ | −759 $ | −1 447 $ | −1 867 $ | −2 739 $ | −2 246 $ | 0,96 | [−2 385 $ ; +2 328 $] | 134 (35 %) | 2.10 s | 0.21 | 938 | −201 $ | −39 $ |

### inédit (40 premiers désaccords)

| Âge de décision | Achats | Gagnés | Résultat net | Espérance / achat | sans top 1 | sans top 3 | sans top 5 | sans top 10 | Creux max | Facteur de profit | IC 90 % (blocs 1 h) | Épisodes encore vivants | Âge réel médian | Prix payé moyen | Taille affichée médiane | Mêmes cycles à l'âge 0 | Délai d'exécution 0,5 s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 s | 40 | 20 % | **−695 $** | −17,36 $ | −880 $ | −1 139 $ | −1 252 $ | −1 283 $ | −817 $ | 0,46 | [−1 212 $ ; −177 $] | 40 (100 %) | 0.00 s | 0.25 | 374 | −695 $ | −874 $ |
| 0.25 s | 35 | 14 % | **−743 $** | −21,22 $ | −928 $ | −1 177 $ | −1 218 $ | −1 178 $ | −771 $ | 0,39 | [−1 268 $ ; −263 $] | 35 (88 %) | 0.30 s | 0.24 | 356 | −848 $ | −659 $ |
| 0.5 s | 30 | 7 % | **−958 $** | −31,92 $ | −1 143 $ | −1 174 $ | −1 162 $ | −1 052 $ | −958 $ | 0,19 | [−1 349 $ ; −593 $] | 30 (75 %) | 0.60 s | 0.24 | 511 | −914 $ | −617 $ |
| 1 s | 21 | 10 % | **−564 $** | −26,86 $ | −749 $ | −845 $ | −829 $ | −581 $ | −564 $ | 0,33 | [−873 $ ; −287 $] | 21 (52 %) | 1.20 s | 0.23 | 941 | −554 $ | −567 $ |
| 2 s | 20 | 10 % | **−561 $** | −28,03 $ | −746 $ | −841 $ | −773 $ | −528 $ | −561 $ | 0,34 | [−783 $ ; −345 $] | 20 (50 %) | 2.10 s | 0.22 | 474 | −502 $ | −319 $ |

## Ce qu'on ne peut pas mesurer ici

- L'âge exact sous 300 ms (les tranches 0-50 et 50-100 ms du plan) : il faut l'horodatage à la milliseconde du programme `rapide.js` (VPS de Dublin).
- La file d'attente au meilleur vendeur et qui nous devance sur l'offre : aucune donnée de transactions Polymarket dans les lignes.
