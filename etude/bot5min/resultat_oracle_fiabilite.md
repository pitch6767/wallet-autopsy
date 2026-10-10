# Fiabilité du moteur TWAP fin — BTC, 849 cycles (07.10 08:00 → 10.10 07:15)

Apprentissage avant le 08.10 21:55 ; validation 08.10 21:55 → 09.10 23:36 ; nuit du 10.10 à part. Tout ce qui est appris l'est sur l'apprentissage seulement.

## 1. Les erreurs du moteur sont-elles à la taille annoncée ? (idées 11-13, 17-19, 21)

Erreur normalisée = (moyenne finale officielle − moyenne prévue) / écart-type annoncé par le moteur. Si le moteur est juste, son écart-type vaut 1 et 95 % des erreurs sont entre −1,96 et +1,96.

| Tranche | Régime | Mesures (appr.) | Écart-type réel des erreurs | Part hors ±1,96 (attendu 5 %) | Quantiles 5 % / 95 % |
|---|---|---|---|---|---|
| avant la fenêtre | agité | 12297 | 0.93 | 4.6 % | -1.58 / +1.36 |
| avant la fenêtre | calme | 592 | 1.14 | 11.0 % | -2.45 / +1.79 |
| 45-60 s restantes | agité | 5530 | 0.92 | 3.3 % | -1.55 / +1.25 |
| 45-60 s restantes | calme | 289 | 1.28 | 17.3 % | -2.55 / +1.89 |
| 30-45 s | agité | 5941 | 0.86 | 2.5 % | -1.31 / +1.30 |
| 30-45 s | calme | 319 | 1.35 | 13.8 % | -2.21 / +2.78 |
| 15-30 s | agité | 3929 | 0.78 | 2.5 % | -1.24 / +1.17 |
| 15-30 s | calme | 205 | 1.60 | 13.7 % | -2.35 / +1.45 |

### Couverture des intervalles (idée 21) : intervalles appris sur l'apprentissage, vérifiés ensuite

| Période | Intervalle 50 % | 80 % | 95 % |
|---|---|---|---|
| apprentissage | 50 % | 80 % | 95 % |
| validation | 50 % | 80 % | 95 % |
| nuit 10.10 | 52 % | 81 % | 94 % |

## 2. Tournoi des probabilités (même moyenne prévue sauf D ; mêmes mesures, une par seconde, 90-20 s)

### apprentissage

| Modèle | Brier | Perte log | Proba > 95 % fausse | Proba > 99 % fausse |
|---|---|---|---|---|
| A — moteur actuel | 0.0406 | 0.1326 | 35 / 20560 (0.2 %) | 0 / 17389 (0.0 %) |
| D — prévision Chainlink (déjà en fantôme) | 0.0408 | 0.1321 | 17 / 20545 (0.1 %) | 0 / 17487 (0.0 %) |
| E — quantiles empiriques des erreurs (appris) | 0.0400 | 0.1310 | 61 / 21624 (0.3 %) | 1 / 16906 (0.0 %) |
| F — incertitude élargie par tranche (appris, × jusqu'à 1.6) | 0.0406 | 0.1330 | 35 / 20495 (0.2 %) | 0 / 17335 (0.0 %) |
| G — incertitude × 1.39 juste après un saut (appris) | 0.0406 | 0.1327 | 33 / 20532 (0.2 %) | 0 / 17373 (0.0 %) |

### validation

| Modèle | Brier | Perte log | Proba > 95 % fausse | Proba > 99 % fausse |
|---|---|---|---|---|
| A — moteur actuel | 0.0463 | 0.1588 | 84 / 12679 (0.7 %) | 43 / 10442 (0.4 %) |
| D — prévision Chainlink (déjà en fantôme) | 0.0462 | 0.1544 | 75 / 12656 (0.6 %) | 30 / 10397 (0.3 %) |
| E — quantiles empiriques des erreurs (appris) | 0.0453 | 0.1525 | 95 / 13226 (0.7 %) | 29 / 10109 (0.3 %) |
| F — incertitude élargie par tranche (appris, × jusqu'à 1.6) | 0.0460 | 0.1559 | 67 / 12593 (0.5 %) | 42 / 10338 (0.4 %) |
| G — incertitude × 1.39 juste après un saut (appris) | 0.0463 | 0.1588 | 81 / 12660 (0.6 %) | 42 / 10418 (0.4 %) |

### nuit 10.10

| Modèle | Brier | Perte log | Proba > 95 % fausse | Proba > 99 % fausse |
|---|---|---|---|---|
| A — moteur actuel | 0.0602 | 0.2252 | 89 / 4211 (2.1 %) | 58 / 3642 (1.6 %) |
| D — prévision Chainlink (déjà en fantôme) | 0.0583 | 0.2065 | 75 / 4171 (1.8 %) | 44 / 3587 (1.2 %) |
| E — quantiles empiriques des erreurs (appris) | 0.0583 | 0.2034 | 57 / 3825 (1.5 %) | 31 / 3089 (1.0 %) |
| F — incertitude élargie par tranche (appris, × jusqu'à 1.6) | 0.0611 | 0.2159 | 87 / 4003 (2.2 %) | 34 / 3303 (1.0 %) |
| G — incertitude × 1.39 juste après un saut (appris) | 0.0602 | 0.2245 | 86 / 4202 (2.0 %) | 57 / 3617 (1.6 %) |

### Rejeu TWAP fin (premier signal, avantage ≥ 0,20, quantité affichée, frais compris)

| Modèle | Apprentissage | Validation | Nuit 10.10 | Jackpots valid. + nuit |
|---|---|---|---|---|
| A — moteur actuel | +1'188 $ (85, 41 %) | +978 $ (58, 50 %) | −241 $ (28, 36 %) | 11 |
| D — prévision Chainlink (déjà en fantôme) | +1'167 $ (69, 33 %) | +759 $ (38, 37 %) | +175 $ (24, 54 %) | 7 |
| E — quantiles empiriques des erreurs (appris) | +1'408 $ (77, 51 %) | +1'642 $ (53, 55 %) | −95 $ (25, 44 %) | 8 |
| F — incertitude élargie par tranche (appris, × jusqu'à 1.6) | +1'569 $ (85, 41 %) | +1'152 $ (60, 50 %) | −391 $ (30, 30 %) | 11 |
| G — incertitude × 1.39 juste après un saut (appris) | +1'168 $ (85, 39 %) | +995 $ (61, 46 %) | −193 $ (27, 33 %) | 11 |

## 3. D'où viennent les certitudes ? (idées 6, 22, 23, 43, 46) — moteur actuel, probabilités > 95 %, toutes périodes

| Groupe | Mesures | Fausses | Taux faux | Dont nuit 10.10 : taux faux |
|---|---|---|---|---|
| certitude née il y a 0,25-1 s | 3025 | 53 | 1.75 % | 4.2 % (284) |
| certitude née il y a 1-3 s | 5553 | 96 | 1.73 % | 4.3 % (555) |
| certitude née il y a < 0,25 s | 1074 | 22 | 2.05 % | 5.1 % (98) |
| certitude née il y a > 3 s | 115060 | 501 | 0.44 % | 1.9 % (13069) |
| le dernier Chainlink seul donne déjà ce côté | 124672 | 668 | 0.54 % | 2.1 % (13999) |
| pas de saut récent | 123435 | 642 | 0.52 % | 2.0 % (13720) |
| saut des exchanges dans les 2 dernières secondes | 1277 | 30 | 2.35 % | 4.9 % (286) |
| secondes de la fenêtre déjà connues : 0 | 44064 | 458 | 1.04 % | 4.3 % (5318) |
| secondes de la fenêtre déjà connues : 1-20 | 38089 | 135 | 0.35 % | 1.0 % (4255) |
| secondes de la fenêtre déjà connues : 21-40 | 42559 | 79 | 0.19 % | 0.3 % (4433) |
| seule l'extrapolation des exchanges donne ce côté | 40 | 4 | 10.00 % | 14.3 % (7) |

## 4. Mémoire des erreurs (idées 14-16, 36-40)

Erreur à 1 s de la prévision Chainlink (variation réelle − 0,24 × écart consensus, la part transmise en 1 s mesurée ce matin) ; autocorrélation :

| Décalage | 1 s | 2 s | 5 s | 10 s |
|---|---|---|---|---|
| Autocorrélation | -0.04 | -0.03 | +0.04 | +0.03 |

Biais d'un cycle à l'autre (idées 16, 39) : corrélation entre l'erreur signée de la moyenne finale d'un cycle et celle du cycle suivant = **+0.00** (766 cycles). Erreur signée moyenne : +0.06 $ (apprentissage +0.20 $, validation -0.23 $, nuit +0.24 $).

## 5. Prix Chainlink « fantôme » : quel estimateur prévoit le mieux le Chainlink suivant ? (idées 48-53)

| Estimateur | Erreur sur Chainlink dans 1 s (RMSE) | dans 5 s | Erreur sur la moyenne finale si prolongé |
|---|---|---|---|
| dernier Chainlink | 2.31 $ | 6.42 $ | 14.72 $ |
| dernier Bybit (moteur actuel) | 5.93 $ | 5.45 $ | 14.30 $ |
| consensus spot (Binance, Coinbase) | 3.70 $ | 4.79 $ | 14.27 $ |
| consensus des 4 exchanges | 4.29 $ | 4.58 $ | 14.13 $ |
| prévision Chainlink D (Chainlink + 0,98 × écart) | 4.20 $ | 4.56 $ | 14.13 $ |
| Chainlink + 0,24 × écart (part transmise en 1 s) | 1.83 $ | 5.58 $ | 14.45 $ |

## 6. Santé du modèle par tranche de 3 heures (idées 31-35) : moteur contre carnet (Brier, mesures où le carnet a un milieu)

| Tranche | Mesures | Volatilité médiane ($/s) | Brier moteur | Brier carnet | Écart (moteur − carnet) | CUSUM |
|---|---|---|---|---|---|---|
| 07.10 06:00 | 381 | 2.2 | 0.1333 | 0.1640 | -0.0307 | 0.000 |
| 07.10 09:00 | 772 | 3.5 | 0.0596 | 0.0481 | +0.0115 | 0.007 |
| 07.10 12:00 | 900 | 4.7 | 0.1091 | 0.1220 | -0.0129 | 0.000 |
| 07.10 15:00 | 917 | 6.0 | 0.1056 | 0.1069 | -0.0013 | 0.000 |
| 07.10 18:00 | 919 | 3.9 | 0.1095 | 0.0936 | +0.0159 | 0.011 |
| 07.10 21:00 | 1061 | 2.6 | 0.1163 | 0.1149 | +0.0013 | 0.007 |
| 08.10 00:00 | 1010 | 2.7 | 0.1461 | 0.1541 | -0.0080 | 0.000 |
| 08.10 03:00 | 860 | 4.4 | 0.0878 | 0.0986 | -0.0108 | 0.000 |
| 08.10 06:00 | 654 | 5.6 | 0.1101 | 0.1100 | +0.0000 | 0.000 |
| 08.10 09:00 | 942 | 3.4 | 0.0878 | 0.0820 | +0.0058 | 0.001 |
| 08.10 12:00 | 603 | 4.6 | 0.1211 | 0.1335 | -0.0124 | 0.000 |
| 08.10 15:00 | 638 | 9.0 | 0.1347 | 0.1385 | -0.0039 | 0.000 |
| 08.10 18:00 | 1111 | 7.8 | 0.0927 | 0.0822 | +0.0106 | 0.006 |
| 08.10 21:00 | 901 | 3.0 | 0.0671 | 0.0665 | +0.0006 | 0.001 |
| 09.10 00:00 | 869 | 2.8 | 0.1810 | 0.1541 | +0.0269 | 0.023 |
| 09.10 03:00 | 846 | 3.2 | 0.0920 | 0.1071 | -0.0151 | 0.003 |
| 09.10 06:00 | 890 | 2.8 | 0.1609 | 0.1738 | -0.0129 | 0.000 |
| 09.10 09:00 | 1078 | 2.4 | 0.1098 | 0.1485 | -0.0387 | 0.000 |
| 09.10 12:00 | 626 | 4.1 | 0.0529 | 0.0284 | +0.0245 | 0.020 |
| 09.10 15:00 | 636 | 5.9 | 0.0975 | 0.0891 | +0.0084 | 0.023 |
| 09.10 18:00 | 836 | 3.9 | 0.0811 | 0.0699 | +0.0112 | 0.029 |
| 09.10 21:00 | 1173 | 2.4 | 0.1219 | 0.1103 | +0.0116 | 0.036 ⚠ |
| 10.10 00:00 | 1100 | 1.3 | 0.1730 | 0.1490 | +0.0240 | 0.055 ⚠ |
| 10.10 03:00 | 1357 | 1.3 | 0.0794 | 0.0572 | +0.0222 | 0.072 ⚠ |
| 10.10 06:00 | 425 | 1.0 | 0.0607 | 0.0430 | +0.0176 | 0.085 ⚠ |