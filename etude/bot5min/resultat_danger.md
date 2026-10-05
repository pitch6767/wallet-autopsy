# Moteur de danger + assurances pour V1 — 12 jours (2026-09-23 -> 2026-10-04)
Tout est choisi sur les jours 1-8 ; les jours 9-12 servent de juge. Prix Polymarket = dernier echange +/- 1 cent, frais taker, retard 1 s.

## BTC — 3283 cycles, 1496 trades V1

### Peut-on voir venir le stop ? (modele appris jours 1-8, juge jours 9-12 ; AUC 0,5 = hasard, 1 = parfait)

| Cible | Stops / lignes jours 1-8 | Stops / lignes jours 9-12 | AUC jours 9-12 |
|---|---|---|---|
| stop dans les 1 s | 524 / 67918 | 158 / 25899 | **0.909** |
| stop dans les 3 s | 1547 / 67918 | 466 / 25899 | **0.870** |
| stop dans les 5 s | 2538 / 67918 | 764 / 25899 | **0.842** |

### Chaque capteur seul (stop dans les 3 s, AUC jours 9-12)

| Capteur | Danger quand il est | AUC |
|---|---|---|
| baisse_proba | haut | 0.830 |
| proba | bas | 0.814 |
| notre_prix | bas | 0.749 |
| pente_proba_3s | bas | 0.726 |
| ret_spot_3s | bas | 0.724 |
| ecart_perp_spot | bas | 0.692 |
| ofi10 | bas | 0.677 |
| convexite | haut | 0.665 |
| gros_contre | haut | 0.659 |
| ofi3 | bas | 0.647 |
| ret_perp_1s | bas | 0.636 |
| ofi1 | bas | 0.622 |
| var_notre_prix_3s | bas | 0.621 |
| pression_opposee_10s | haut | 0.590 |
| pression_opposee_3s | haut | 0.572 |
| volume_rel | haut | 0.568 |
| d_ofi3 | bas | 0.554 |
| depuis_entree | bas | 0.549 |
| pression_nette_10s | bas | 0.546 |
| frag5 | bas | 0.539 |
| temps_restant | bas | 0.527 |
| ofi10_moins_ofi3 | haut | 0.521 |
| d2_ofi3 | bas | 0.510 |
| gros_pour | bas | 0.482 |
| frag1 | haut | 0.478 |
| frag3 | haut | 0.466 |

### Strategies (gains pour 100 parts ≈ 55 $ ; entre parentheses : ecart avec la reference)

| Strategie | Trades | Gain net | Gain/jour | Pertes totales | Trades perdants | Pire baisse | Gain/jour jours 1-8 | **Gain/jour jours 9-12 (jamais vus)** | Issues |
|---|---|---|---|---|---|---|---|---|---|
| Reference V1 | 1496 | +17946 $ (+0) | +1496 $ | -6882 $ (+0) | 551 (+0) | -120 $ | +1593 $ (+0) | **+1530 $ (+0)** | stop 685, sortie 635, paire 146, fin 30 |
| Entree : refuser si fragilite 3 pb > 20 % haut | 1128 | +12010 $ (-5936) | +1001 $ | -5255 $ (+1627) | 461 (-90) | -160 $ | +1155 $ (-438) | **+815 $ (-715)** | stop 557, sortie 450, paire 101, fin 20 |
| Entree : refuser si fragilite > 10 % haut | 1288 | +14124 $ (-3822) | +1177 $ | -6064 $ (+818) | 510 (-41) | -148 $ | +1345 $ (-248) | **+990 $ (-540)** | stop 623, sortie 523, paire 117, fin 25 |
| Entree : mise inverse a la fragilite | 1496 | +19849 $ (+1903) | +1654 $ | -8013 $ (-1131) | 557 (+6) | -171 $ | +1852 $ (+259) | **+1480 $ (-49)** | stop 697, sortie 635, paire 137, fin 27 |
| Mise 0,5x / 1,5x selon l'avance (retenue) | 1496 | +20451 $ (+2505) | +1704 $ | -6208 $ (+673) | 542 (-9) | -113 $ | +1770 $ (+177) | **+1851 $ (+322)** | stop 676, sortie 635, paire 157, fin 28 |
| Assurance temporaire 30 % si danger top 5 %, retiree quand ca se calme | 1496 | +18767 $ (+821) | +1564 $ | -5892 $ (+990) | 540 (-11) | -126 $ | +1682 $ (+88) | **+1563 $ (+33)** | stop 675, sortie 635, paire 157, fin 17, couvert 12 |
| Assurance temporaire 50 % si danger top 5 % | 1496 | +19286 $ (+1340) | +1607 $ | -5322 $ (+1560) | 528 (-23) | -130 $ | +1739 $ (+145) | **+1582 $ (+52)** | stop 667, sortie 635, paire 165, fin 17, couvert 12 |
| Assurance temporaire 30 % si danger top 2 % | 1496 | +18539 $ (+593) | +1545 $ | -6285 $ (+597) | 541 (-10) | -117 $ | +1657 $ (+64) | **+1553 $ (+23)** | stop 681, sortie 635, paire 150, fin 28, couvert 2 |
| Assurance 30 % top 10 %, retiree apres 3 s calmes | 1496 | +18429 $ (+483) | +1536 $ | -5772 $ (+1110) | 539 (-12) | -122 $ | +1650 $ (+57) | **+1538 $ (+8)** | stop 675, sortie 635, paire 157, couvert 18, fin 11 |
| Assurance graduee 25 / 50 / 100 % (danger top 10 / 5 / 2 %) | 1496 | +19559 $ (+1613) | +1630 $ | -4574 $ (+2308) | 493 (-58) | -120 $ | +1786 $ (+193) | **+1551 $ (+21)** | paire anticipee 699, sortie 622, paire 145, couvert 16, fin 11, stop 3 |
| Assurance graduee, jamais retiree | 1496 | +18028 $ (+82) | +1502 $ | -3953 $ (+2929) | 476 (-75) | -66 $ | +1646 $ (+53) | **+1429 $ (-101)** | paire anticipee 698, sortie 622, paire 146, couvert 16, fin 11, stop 3 |
| Paire anticipee 100 % si danger top 5 % et oppose <= 0,45 | 1496 | +19076 $ (+1130) | +1590 $ | -3986 $ (+2896) | 457 (-94) | -107 $ | +1753 $ (+160) | **+1485 $ (-44)** | paire anticipee 654, sortie 559, stop 171, paire 93, fin 19 |
| Paire anticipee 100 % si danger top 2 % et oppose <= 0,48 | 1496 | +19693 $ (+1747) | +1641 $ | -5175 $ (+1707) | 503 (-48) | -120 $ | +1799 $ (+205) | **+1561 $ (+31)** | sortie 626, paire anticipee 514, stop 192, paire 135, fin 29 |
| Assurance 30 % top 5 % + revendue si elle gagne 8 cents (monetiser) | 1496 | +18496 $ (+550) | +1541 $ | -6170 $ (+712) | 548 (-3) | -117 $ | +1651 $ (+58) | **+1555 $ (+25)** | stop 676, sortie 635, paire 155, fin 17, couvert 13 |
| Assurance 50 % top 5 % + monetiser 5 cents | 1496 | +18421 $ (+475) | +1535 $ | -6085 $ (+796) | 552 (+1) | -118 $ | +1652 $ (+59) | **+1531 $ (+1)** | stop 670, sortie 635, paire 162, fin 17, couvert 12 |
| SANS STOP + assurance graduee | 1496 | +19578 $ (+1632) | +1632 $ | -4575 $ (+2307) | 493 (-58) | -120 $ | +1786 $ (+193) | **+1556 $ (+26)** | paire anticipee 701, sortie 623, paire 145, couvert 16, fin 11 |
| SANS STOP + paire anticipee top 5 % (oppose <= 0,48) | 1496 | +18951 $ (+1005) | +1579 $ | -4067 $ (+2815) | 462 (-89) | -112 $ | +1738 $ (+145) | **+1484 $ (-45)** | paire anticipee 787, sortie 557, paire 95, fin 57 |
| SANS STOP + graduee + paire complete top 1 % | 1496 | +19494 $ (+1548) | +1625 $ | -4863 $ (+2019) | 507 (-44) | -122 $ | +1789 $ (+196) | **+1525 $ (-5)** | paire anticipee 675, sortie 634, paire 156, couvert 20, fin 11 |
| Simple : assurance 30 % si fragilite top 5 % | 1496 | +17102 $ (-844) | +1425 $ | -6798 $ (+84) | 550 (-1) | -120 $ | +1538 $ (-55) | **+1411 $ (-119)** | stop 685, sortie 635, paire 146, fin 26, couvert 4 |
| Simple : assurance 30 % si acceleration du flux contre nous (5 % bas) | 1496 | +14642 $ (-3305) | +1220 $ | -7802 $ (-920) | 573 (+22) | -158 $ | +1312 $ (-281) | **+1220 $ (-310)** | stop 683, sortie 635, paire 148, couvert 24, fin 6 |
| Simple : assurance 30 % si la proba a deja perdu 7 pts | 1496 | +18516 $ (+570) | +1543 $ | -6181 $ (+701) | 543 (-8) | -120 $ | +1649 $ (+56) | **+1566 $ (+36)** | stop 678, sortie 635, paire 153, fin 23, couvert 7 |
| Simple : avalanche (2 signaux sur 4) -> assurance 50 % | 1496 | +17946 $ (+0) | +1496 $ | -6882 $ (+0) | 551 (+0) | -120 $ | +1593 $ (+0) | **+1530 $ (+0)** | stop 685, sortie 635, paire 146, fin 30 |
| Combo : fragilite 10 % refusee + assurance graduee | 1288 | +15709 $ (-2237) | +1309 $ | -3917 $ (+2965) | 452 (-99) | -136 $ | +1529 $ (-64) | **+1023 $ (-507)** | paire anticipee 636, sortie 510, paire 116, couvert 14, fin 10, stop 2 |
| Combo : mise 1,5x + assurance graduee | 1496 | +21850 $ (+3904) | +1821 $ | -4174 $ (+2708) | 490 (-61) | -84 $ | +1957 $ (+364) | **+1821 $ (+291)** | paire anticipee 698, sortie 622, paire 148, couvert 16, fin 9, stop 3 |
| Combo : mise 1,5x + assurance 30 % top 5 % + monetiser | 1496 | +20923 $ (+2977) | +1744 $ | -5573 $ (+1309) | 543 (-8) | -102 $ | +1823 $ (+230) | **+1864 $ (+334)** | stop 671, sortie 635, paire 162, fin 16, couvert 12 |
| Combo : mise 1,5x + fragilite refusee + graduee + monetiser | 1288 | +16542 $ (-1404) | +1378 $ | -3560 $ (+3322) | 459 (-92) | -89 $ | +1600 $ (+7) | **+1101 $ (-429)** | paire anticipee 635, sortie 510, paire 117, couvert 15, fin 9, stop 2 |
| Combo : mise 1,5x + SANS STOP + graduee | 1496 | +21879 $ (+3933) | +1823 $ | -4175 $ (+2707) | 490 (-61) | -84 $ | +1957 $ (+364) | **+1830 $ (+300)** | paire anticipee 700, sortie 623, paire 148, couvert 16, fin 9 |

## ETH — 3283 cycles, 626 trades V1

### Peut-on voir venir le stop ? (modele appris jours 1-8, juge jours 9-12 ; AUC 0,5 = hasard, 1 = parfait)

| Cible | Stops / lignes jours 1-8 | Stops / lignes jours 9-12 | AUC jours 9-12 |
|---|---|---|---|
| stop dans les 1 s | 245 / 26832 | 72 / 8824 | **0.936** |
| stop dans les 3 s | 726 / 26832 | 209 / 8824 | **0.894** |
| stop dans les 5 s | 1182 / 26832 | 343 / 8824 | **0.871** |

### Chaque capteur seul (stop dans les 3 s, AUC jours 9-12)

| Capteur | Danger quand il est | AUC |
|---|---|---|
| baisse_proba | haut | 0.889 |
| proba | bas | 0.856 |
| pente_proba_3s | bas | 0.777 |
| notre_prix | bas | 0.776 |
| ret_spot_3s | bas | 0.752 |
| ofi10 | bas | 0.740 |
| gros_contre | haut | 0.715 |
| ofi3 | bas | 0.709 |
| convexite | haut | 0.680 |
| ret_perp_1s | bas | 0.662 |
| var_notre_prix_3s | bas | 0.654 |
| ofi1 | bas | 0.646 |
| volume_rel | haut | 0.639 |
| ecart_perp_spot | bas | 0.598 |
| frag5 | bas | 0.579 |
| pression_opposee_10s | haut | 0.565 |
| temps_restant | bas | 0.557 |
| ofi10_moins_ofi3 | haut | 0.542 |
| d_ofi3 | bas | 0.541 |
| pression_opposee_3s | haut | 0.541 |
| frag1 | haut | 0.535 |
| pression_nette_10s | bas | 0.519 |
| d2_ofi3 | haut | 0.509 |
| depuis_entree | bas | 0.509 |
| gros_pour | bas | 0.489 |
| frag3 | haut | 0.461 |

### Strategies (gains pour 100 parts ≈ 55 $ ; entre parentheses : ecart avec la reference)

| Strategie | Trades | Gain net | Gain/jour | Pertes totales | Trades perdants | Pire baisse | Gain/jour jours 1-8 | **Gain/jour jours 9-12 (jamais vus)** | Issues |
|---|---|---|---|---|---|---|---|---|---|
| Reference V1 | 626 | +6394 $ (+0) | +533 $ | -3534 $ (+0) | 260 (+0) | -129 $ | +551 $ (+0) | **+584 $ (+0)** | stop 320, sortie 243, fin 35, paire 28 |
| Entree : refuser si fragilite 3 pb > 20 % haut | 465 | +4490 $ (-1904) | +374 $ | -2449 $ (+1085) | 204 (-56) | -91 $ | +432 $ (-118) | **+303 $ (-281)** | stop 253, sortie 175, fin 21, paire 16 |
| Entree : refuser si fragilite > 10 % haut | 546 | +5297 $ (-1097) | +441 $ | -3040 $ (+493) | 235 (-25) | -121 $ | +481 $ (-70) | **+425 $ (-159)** | stop 290, sortie 206, fin 31, paire 19 |
| Entree : mise inverse a la fragilite | 626 | +6669 $ (+276) | +556 $ | -4229 $ (-695) | 260 (+0) | -184 $ | +630 $ (+79) | **+480 $ (-104)** | stop 319, sortie 243, fin 35, paire 29 |
| Mise 0,5x / 1,5x selon l'avance (retenue) | 626 | +7212 $ (+818) | +601 $ | -3396 $ (+137) | 256 (-4) | -157 $ | +608 $ (+57) | **+690 $ (+106)** | stop 318, sortie 243, fin 33, paire 32 |
| Assurance temporaire 30 % si danger top 5 %, retiree quand ca se calme | 626 | +6588 $ (+194) | +549 $ | -3169 $ (+365) | 250 (-10) | -117 $ | +582 $ (+32) | **+567 $ (-17)** | stop 320, sortie 243, paire 28, fin 23, couvert 12 |
| Assurance temporaire 50 % si danger top 5 % | 626 | +6749 $ (+355) | +562 $ | -2938 $ (+596) | 238 (-22) | -109 $ | +606 $ (+55) | **+560 $ (-25)** | stop 319, sortie 243, paire 29, fin 22, couvert 13 |
| Assurance temporaire 30 % si danger top 2 % | 626 | +6555 $ (+161) | +546 $ | -3386 $ (+148) | 257 (-3) | -131 $ | +571 $ (+20) | **+584 $ (-0)** | stop 320, sortie 243, fin 35, paire 28 |
| Assurance 30 % top 10 %, retiree apres 3 s calmes | 626 | +6420 $ (+26) | +535 $ | -2985 $ (+549) | 254 (-6) | -96 $ | +572 $ (+21) | **+542 $ (-42)** | stop 319, sortie 243, paire 30, fin 17, couvert 17 |
| Assurance graduee 25 / 50 / 100 % (danger top 10 / 5 / 2 %) | 626 | +6932 $ (+538) | +578 $ | -2656 $ (+878) | 232 (-28) | -98 $ | +637 $ (+86) | **+541 $ (-44)** | paire anticipee 304, sortie 243, paire 30, fin 17, couvert 17, stop 15 |
| Assurance graduee, jamais retiree | 626 | +6597 $ (+203) | +550 $ | -2332 $ (+1202) | 221 (-39) | -83 $ | +609 $ (+58) | **+507 $ (-77)** | paire anticipee 304, sortie 243, paire 32, fin 17, stop 15, couvert 15 |
| Paire anticipee 100 % si danger top 5 % et oppose <= 0,45 | 626 | +6968 $ (+574) | +581 $ | -2468 $ (+1066) | 216 (-44) | -84 $ | +647 $ (+96) | **+527 $ (-58)** | paire anticipee 237, sortie 220, stop 127, fin 24, paire 18 |
| Paire anticipee 100 % si danger top 2 % et oppose <= 0,48 | 626 | +7023 $ (+629) | +585 $ | -3091 $ (+442) | 234 (-26) | -129 $ | +628 $ (+77) | **+587 $ (+3)** | sortie 243, paire anticipee 163, stop 157, fin 35, paire 28 |
| Assurance 30 % top 5 % + revendue si elle gagne 8 cents (monetiser) | 626 | +6538 $ (+144) | +545 $ | -3245 $ (+288) | 254 (-6) | -123 $ | +576 $ (+25) | **+569 $ (-16)** | stop 320, sortie 243, paire 28, fin 23, couvert 12 |
| Assurance 50 % top 5 % + monetiser 5 cents | 626 | +6547 $ (+153) | +546 $ | -3125 $ (+409) | 247 (-13) | -118 $ | +584 $ (+33) | **+551 $ (-33)** | stop 319, sortie 243, paire 29, fin 22, couvert 13 |
| SANS STOP + assurance graduee | 626 | +6974 $ (+580) | +581 $ | -2653 $ (+881) | 229 (-31) | -98 $ | +641 $ (+90) | **+543 $ (-41)** | paire anticipee 315, sortie 245, paire 31, couvert 18, fin 17 |
| SANS STOP + paire anticipee top 5 % (oppose <= 0,48) | 626 | +6706 $ (+312) | +559 $ | -2891 $ (+642) | 205 (-55) | -122 $ | +640 $ (+89) | **+466 $ (-118)** | paire anticipee 324, sortie 221, fin 62, paire 19 |
| SANS STOP + graduee + paire complete top 1 % | 626 | +6698 $ (+304) | +558 $ | -2882 $ (+652) | 238 (-22) | -94 $ | +605 $ (+54) | **+546 $ (-38)** | paire anticipee 305, sortie 249, paire 37, couvert 18, fin 17 |
| Simple : assurance 30 % si fragilite top 5 % | 626 | +6110 $ (-284) | +509 $ | -3454 $ (+80) | 260 (+0) | -127 $ | +540 $ (-11) | **+527 $ (-57)** | stop 320, sortie 243, fin 31, paire 28, couvert 4 |
| Simple : assurance 30 % si acceleration du flux contre nous (5 % bas) | 626 | +5851 $ (-543) | +488 $ | -3648 $ (-114) | 263 (+3) | -135 $ | +508 $ (-43) | **+525 $ (-59)** | stop 320, sortie 243, paire 28, couvert 19, fin 16 |
| Simple : assurance 30 % si la proba a deja perdu 7 pts | 626 | +6485 $ (+91) | +540 $ | -3303 $ (+231) | 254 (-6) | -137 $ | +562 $ (+11) | **+585 $ (+1)** | stop 320, sortie 243, paire 28, fin 22, couvert 13 |
| Simple : avalanche (2 signaux sur 4) -> assurance 50 % | 626 | +6394 $ (+0) | +533 $ | -3534 $ (+0) | 260 (+0) | -129 $ | +551 $ (+0) | **+584 $ (+0)** | stop 320, sortie 243, fin 35, paire 28 |
| Combo : fragilite 10 % refusee + assurance graduee | 546 | +5940 $ (-454) | +495 $ | -2241 $ (+1293) | 209 (-51) | -76 $ | +565 $ (+14) | **+418 $ (-167)** | paire anticipee 275, sortie 206, paire 21, fin 15, couvert 15, stop 14 |
| Combo : mise 1,5x + assurance graduee | 626 | +7692 $ (+1299) | +641 $ | -2574 $ (+960) | 233 (-27) | -116 $ | +690 $ (+139) | **+639 $ (+55)** | paire anticipee 303, sortie 243, paire 33, fin 17, stop 15, couvert 15 |
| Combo : mise 1,5x + assurance 30 % top 5 % + monetiser | 626 | +7315 $ (+921) | +610 $ | -3131 $ (+403) | 252 (-8) | -146 $ | +631 $ (+80) | **+667 $ (+83)** | stop 317, sortie 243, paire 33, fin 22, couvert 11 |
| Combo : mise 1,5x + fragilite refusee + graduee + monetiser | 546 | +6244 $ (-150) | +520 $ | -2077 $ (+1457) | 211 (-49) | -156 $ | +592 $ (+41) | **+443 $ (-142)** | paire anticipee 274, sortie 206, paire 24, fin 15, stop 14, couvert 13 |
| Combo : mise 1,5x + SANS STOP + graduee | 626 | +7744 $ (+1350) | +645 $ | -2573 $ (+961) | 230 (-30) | -116 $ | +692 $ (+141) | **+650 $ (+65)** | paire anticipee 315, sortie 245, paire 33, fin 17, couvert 16 |

Duree : 1764 s