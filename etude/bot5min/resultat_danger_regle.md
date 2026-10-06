# Moteur de danger + assurances pour V1 — 12 jours (2026-09-24 -> 2026-10-05)
Tout est choisi sur les jours 1-8 ; les jours 9-12 servent de juge. Prix Polymarket = dernier echange +/- 1 cent, frais taker, retard 1 s.

## BTC — 3381 cycles, 1526 trades V1

### Peut-on voir venir le stop ? (modele appris jours 1-8, juge jours 9-12 ; AUC 0,5 = hasard, 1 = parfait)

| Cible | Stops / lignes jours 1-8 | Stops / lignes jours 9-12 | AUC jours 9-12 |
|---|---|---|---|
| stop dans les 1 s | 506 / 67701 | 179 / 29054 | **0.916** |
| stop dans les 3 s | 1494 / 67701 | 526 / 29054 | **0.872** |
| stop dans les 5 s | 2449 / 67701 | 862 / 29054 | **0.846** |

### Chaque capteur seul (stop dans les 3 s, AUC jours 9-12)

| Capteur | Danger quand il est | AUC |
|---|---|---|
| baisse_proba | haut | 0.840 |
| proba | bas | 0.819 |
| notre_prix | bas | 0.763 |
| pente_proba_3s | bas | 0.749 |
| ret_spot_3s | bas | 0.737 |
| convexite | haut | 0.653 |
| ofi10 | bas | 0.643 |
| var_notre_prix_3s | bas | 0.611 |
| ofi3 | bas | 0.608 |
| ofi1 | bas | 0.592 |
| ret_perp_1s | bas | 0.580 |
| volume_rel | haut | 0.561 |
| pression_opposee_10s | haut | 0.561 |
| pression_opposee_3s | haut | 0.559 |
| gros_contre | haut | 0.548 |
| depuis_entree | bas | 0.545 |
| d_ofi3 | bas | 0.539 |
| ecart_perp_spot | bas | 0.524 |
| frag5 | bas | 0.523 |
| pression_nette_10s | bas | 0.523 |
| ofi10_moins_ofi3 | haut | 0.515 |
| gros_pour | bas | 0.508 |
| temps_restant | bas | 0.503 |
| d2_ofi3 | bas | 0.503 |
| frag1 | haut | 0.501 |
| frag3 | haut | 0.488 |

### Strategies (gains pour 100 parts ≈ 55 $ ; entre parentheses : ecart avec la reference)

| Strategie | Trades | Gain net | Gain/jour | Pertes totales | Trades perdants | Pire baisse | Gain/jour jours 1-8 | **Gain/jour jours 9-12 (jamais vus)** | Issues |
|---|---|---|---|---|---|---|---|---|---|
| Reference V1 | 1526 | +18627 $ (+0) | +1552 $ | -6935 $ (+0) | 557 (+0) | -120 $ | +1619 $ (+0) | **+1518 $ (+0)** | stop 688, sortie 649, paire 155, fin 34 |
| Regle simple sans stop : baisse 5/8/11 pts -> 25/50/100 %, retrait < 3 pts | 1526 | +18584 $ (-43) | +1549 $ | -5480 $ (+1455) | 554 (-3) | -104 $ | +1626 $ (+7) | **+1490 $ (-27)** | paire anticipee 756, sortie 610, paire 135, fin 20, couvert 5 |
| Regle simple sans stop : baisse 6/9/12 pts -> 25/50/100 %, retrait < 3 pts | 1526 | +18747 $ (+120) | +1562 $ | -5728 $ (+1207) | 554 (-3) | -100 $ | +1638 $ (+19) | **+1510 $ (-8)** | paire anticipee 731, sortie 621, paire 145, fin 21, couvert 8 |
| Regle simple sans stop : baisse 7/10/13 pts -> 25/50/100 %, retrait < 3 pts | 1526 | +18929 $ (+302) | +1577 $ | -5893 $ (+1042) | 553 (-4) | -115 $ | +1644 $ (+25) | **+1544 $ (+27)** | paire anticipee 711, sortie 633, paire 151, fin 22, couvert 9 |
| Regle simple sans stop : baisse 8/11/14 pts -> 25/50/100 %, retrait < 3 pts | 1526 | +18919 $ (+292) | +1577 $ | -6106 $ (+829) | 557 (+0) | -114 $ | +1654 $ (+35) | **+1521 $ (+4)** | paire anticipee 695, sortie 642, paire 158, fin 23, couvert 8 |
| Regle simple sans stop : baisse 4/7/10 pts -> 25/50/100 %, retrait < 3 pts | 1526 | +18688 $ (+62) | +1557 $ | -5158 $ (+1777) | 549 (-8) | -107 $ | +1629 $ (+11) | **+1512 $ (-6)** | paire anticipee 768, sortie 600, paire 133, fin 17, couvert 8 |
| Regle 6/9/12 sans retrait, sans stop | 1526 | +18282 $ (-345) | +1524 $ | -5537 $ (+1398) | 551 (-6) | -85 $ | +1601 $ (-18) | **+1463 $ (-54)** | paire anticipee 730, sortie 621, paire 146, fin 21, couvert 8 |
| Regle 6/9/12 AVEC le stop -15 en plus | 1526 | +18747 $ (+120) | +1562 $ | -5728 $ (+1207) | 554 (-3) | -100 $ | +1638 $ (+19) | **+1510 $ (-8)** | paire anticipee 731, sortie 621, paire 145, fin 21, couvert 8 |
| Mise 1,5x + regle 6/9/12 sans stop | 1526 | +21205 $ (+2578) | +1767 $ | -5308 $ (+1627) | 548 (-9) | -112 $ | +1795 $ (+176) | **+1830 $ (+312)** | paire anticipee 731, sortie 621, paire 145, fin 20, couvert 9 |
| Modele de danger (pour comparer) : graduee sans stop | 1526 | +19956 $ (+1329) | +1663 $ | -4602 $ (+2333) | 495 (-62) | -97 $ | +1800 $ (+181) | **+1487 $ (-31)** | paire anticipee 706, sortie 636, paire 156, couvert 19, fin 9 |

## ETH — 3381 cycles, 629 trades V1

### Peut-on voir venir le stop ? (modele appris jours 1-8, juge jours 9-12 ; AUC 0,5 = hasard, 1 = parfait)

| Cible | Stops / lignes jours 1-8 | Stops / lignes jours 9-12 | AUC jours 9-12 |
|---|---|---|---|
| stop dans les 1 s | 237 / 25686 | 78 / 9695 | **0.954** |
| stop dans les 3 s | 702 / 25686 | 225 / 9695 | **0.897** |
| stop dans les 5 s | 1147 / 25686 | 369 / 9695 | **0.872** |

### Chaque capteur seul (stop dans les 3 s, AUC jours 9-12)

| Capteur | Danger quand il est | AUC |
|---|---|---|
| baisse_proba | haut | 0.883 |
| proba | bas | 0.860 |
| pente_proba_3s | bas | 0.782 |
| notre_prix | bas | 0.764 |
| ret_spot_3s | bas | 0.751 |
| ofi10 | bas | 0.739 |
| ofi3 | bas | 0.699 |
| gros_contre | haut | 0.698 |
| ret_perp_1s | bas | 0.678 |
| convexite | haut | 0.675 |
| volume_rel | haut | 0.655 |
| var_notre_prix_3s | bas | 0.643 |
| ofi1 | bas | 0.641 |
| ecart_perp_spot | bas | 0.619 |
| frag1 | haut | 0.579 |
| pression_opposee_10s | haut | 0.568 |
| frag5 | bas | 0.557 |
| d_ofi3 | bas | 0.547 |
| depuis_entree | bas | 0.546 |
| pression_opposee_3s | haut | 0.543 |
| temps_restant | bas | 0.537 |
| ofi10_moins_ofi3 | haut | 0.527 |
| gros_pour | bas | 0.524 |
| d2_ofi3 | haut | 0.505 |
| frag3 | haut | 0.498 |
| pression_nette_10s | bas | 0.498 |

### Strategies (gains pour 100 parts ≈ 55 $ ; entre parentheses : ecart avec la reference)

| Strategie | Trades | Gain net | Gain/jour | Pertes totales | Trades perdants | Pire baisse | Gain/jour jours 1-8 | **Gain/jour jours 9-12 (jamais vus)** | Issues |
|---|---|---|---|---|---|---|---|---|---|
| Reference V1 | 629 | +6444 $ (+0) | +537 $ | -3681 $ (+0) | 259 (+0) | -129 $ | +520 $ (+0) | **+610 $ (+0)** | stop 318, sortie 250, fin 37, paire 24 |
| Regle simple sans stop : baisse 5/8/11 pts -> 25/50/100 %, retrait < 3 pts | 629 | +6480 $ (+35) | +540 $ | -2891 $ (+789) | 244 (-15) | -76 $ | +541 $ (+20) | **+576 $ (-34)** | paire anticipee 343, sortie 234, paire 23, fin 22, couvert 7 |
| Regle simple sans stop : baisse 6/9/12 pts -> 25/50/100 %, retrait < 3 pts | 629 | +6436 $ (-8) | +536 $ | -3014 $ (+666) | 251 (-8) | -86 $ | +530 $ (+10) | **+587 $ (-23)** | paire anticipee 340, sortie 235, fin 25, paire 23, couvert 6 |
| Regle simple sans stop : baisse 7/10/13 pts -> 25/50/100 %, retrait < 3 pts | 629 | +6504 $ (+60) | +542 $ | -3121 $ (+560) | 255 (-4) | -89 $ | +539 $ (+18) | **+587 $ (-23)** | paire anticipee 334, sortie 238, fin 25, paire 23, couvert 9 |
| Regle simple sans stop : baisse 8/11/14 pts -> 25/50/100 %, retrait < 3 pts | 629 | +6437 $ (-7) | +536 $ | -3292 $ (+388) | 255 (-4) | -92 $ | +524 $ (+4) | **+599 $ (-11)** | paire anticipee 325, sortie 244, fin 26, paire 24, couvert 10 |
| Regle simple sans stop : baisse 4/7/10 pts -> 25/50/100 %, retrait < 3 pts | 629 | +6575 $ (+131) | +548 $ | -2729 $ (+952) | 244 (-15) | -75 $ | +549 $ (+29) | **+584 $ (-26)** | paire anticipee 346, sortie 232, paire 23, fin 20, couvert 8 |
| Regle 6/9/12 sans retrait, sans stop | 629 | +6396 $ (-49) | +533 $ | -2850 $ (+831) | 249 (-10) | -78 $ | +527 $ (+7) | **+582 $ (-28)** | paire anticipee 340, sortie 235, paire 25, fin 25, couvert 4 |
| Regle 6/9/12 AVEC le stop -15 en plus | 629 | +6436 $ (-8) | +536 $ | -3014 $ (+666) | 251 (-8) | -86 $ | +530 $ (+10) | **+587 $ (-23)** | paire anticipee 340, sortie 235, fin 25, paire 23, couvert 6 |
| Mise 1,5x + regle 6/9/12 sans stop | 629 | +7521 $ (+1077) | +627 $ | -2884 $ (+796) | 252 (-7) | -144 $ | +593 $ (+73) | **+743 $ (+133)** | paire anticipee 340, sortie 235, paire 25, fin 23, couvert 6 |
| Modele de danger (pour comparer) : graduee sans stop | 629 | +6878 $ (+434) | +573 $ | -2807 $ (+874) | 242 (-17) | -106 $ | +582 $ (+62) | **+594 $ (-16)** | paire anticipee 318, sortie 250, paire 24, couvert 19, fin 18 |

Duree : 1467 s