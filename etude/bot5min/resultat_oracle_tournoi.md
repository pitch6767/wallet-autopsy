# Tournoi des prévisions Chainlink — BTC, 849 cycles (07.10 08:00 → 10.10 07:15)

Apprentissage : cycles avant le 08.10 21:55 ; validation : 08.10 21:55 → 09.10 23:36 ; nuit du 10.10 à part. Tout est calculé avec les données reçues avant l'instant de décision.

## Q1. Quelle part de l'écart exchange − Chainlink Chainlink rattrape-t-il, et en combien de temps ?

Écart = prix de l'exchange ramené au niveau Chainlink (médiane de l'écart sur 120 s) − dernier Chainlink. Pente = variation de Chainlink / écart (régression robuste par l'origine, écarts ≥ 2 $). 1,00 = tout est transmis.

| Source | Mesures | 0,5 s | 1 s | 2 s | 5 s | 10 s |
|---|---|---|---|---|---|---|
| Bybit perp | 78923 | 0.08 | 0.16 | 0.33 | 0.57 | 0.69 |
| OKX | 71315 | 0.09 | 0.19 | 0.38 | 0.63 | 0.75 |
| Binance | 55304 | 0.12 | 0.26 | 0.51 | 0.78 | 0.85 |
| Coinbase | 73855 | 0.09 | 0.19 | 0.36 | 0.56 | 0.66 |
| consensus des 4 | 59390 | 0.12 | 0.24 | 0.49 | 0.80 | 0.95 |
| consensus, 1 exchange(s) d'accord | 6 | — | — | — | — | — |
| consensus, 2 exchange(s) d'accord | 13808 | 0.06 | 0.12 | 0.26 | 0.59 | 0.81 |
| consensus, 3 exchange(s) d'accord | 24332 | 0.07 | 0.14 | 0.31 | 0.63 | 0.81 |
| consensus, 4 exchange(s) d'accord | 21244 | 0.15 | 0.31 | 0.60 | 0.91 | 1.03 |
| consensus, régime agité (≥ 2 $/s) | 54656 | 0.12 | 0.25 | 0.49 | 0.82 | 0.96 |
| consensus, régime calme (< 2 $/s) | 4734 | 0.07 | 0.16 | 0.31 | 0.51 | 0.68 |

## Q17. Les sauts d'une seconde du perp Bybit : que reste-t-il après 2, 5, 10 s, et combien passe dans Chainlink ?

Saut = mouvement du perp en 1 s ≥ 4 fois sa volatilité par seconde et ≥ 3 $. Confirmé = OKX ou Binance bougent dans le même sens d'au moins la moitié dans la même seconde.

| Type de saut | Sauts | Reste sur le perp à 2 s | à 5 s | à 10 s | Passé dans Chainlink à 2 s | à 5 s | à 10 s |
|---|---|---|---|---|---|---|---|
| confirmé | 2663 | 100 % | 101 % | 104 % | 35 % | 86 % | 94 % |
| confirmé, 07-09.10 | 2308 | 100 % | 101 % | 105 % | 36 % | 86 % | 94 % |
| confirmé, nuit 10.10 | 355 | 100 % | 101 % | 101 % | 34 % | 86 % | 89 % |
| isolé (Bybit seul) | 571 | 100 % | 100 % | 100 % | 10 % | 43 % | 47 % |
| isolé, 07-09.10 | 404 | 100 % | 100 % | 100 % | 11 % | 47 % | 52 % |
| isolé, nuit 10.10 | 167 | 100 % | 100 % | 100 % | 5 % | 33 % | 39 % |
| tous | 3234 | 100 % | 101 % | 102 % | 30 % | 80 % | 87 % |

## Tournoi des quatre modèles

Coefficients appris sur l'apprentissage seulement : C garde **0.88** d'un saut récent ; D prolonge le dernier Chainlink plus **0.98** fois l'écart entre le consensus des 4 exchanges et Chainlink. Même incertitude (même écart-type) pour les 4 modèles : seule la moyenne prévue change.

### apprentissage

| Modèle | Mesures | Erreur moyenne finale (RMSE, $) | Brier | Proba > 95 % fausse | Proba > 99 % fausse |
|---|---|---|---|---|---|
| A — actuel (dernier prix Bybit prolongé) | 29102 | 21.28 | 0.0406 | 35 / 20555 (0.2 %) | 0 / 17388 (0.0 %) |
| B — anti-saut (saut accepté si confirmé ou après 2 s) | 29102 | 21.28 | 0.0406 | 35 / 20554 (0.2 %) | 0 / 17389 (0.0 %) |
| C — persistance du saut (garde 0.88 du saut) | 29102 | 21.28 | 0.0406 | 35 / 20551 (0.2 %) | 0 / 17388 (0.0 %) |
| C2 — persistance selon confirmation (isolé 0.60, confirmé 0.89) | 29102 | 21.28 | 0.0406 | 35 / 20549 (0.2 %) | 0 / 17387 (0.0 %) |
| D — prévision Chainlink (dernier Chainlink + 0.98 × écart consensus) | 29102 | 21.13 | 0.0408 | 17 / 20547 (0.1 %) | 0 / 17485 (0.0 %) |

### validation

| Modèle | Mesures | Erreur moyenne finale (RMSE, $) | Brier | Proba > 95 % fausse | Proba > 99 % fausse |
|---|---|---|---|---|---|
| A — actuel (dernier prix Bybit prolongé) | 18175 | 15.88 | 0.0463 | 84 / 12684 (0.7 %) | 43 / 10444 (0.4 %) |
| B — anti-saut (saut accepté si confirmé ou après 2 s) | 18175 | 15.88 | 0.0463 | 84 / 12683 (0.7 %) | 43 / 10444 (0.4 %) |
| C — persistance du saut (garde 0.88 du saut) | 18175 | 15.87 | 0.0463 | 83 / 12684 (0.7 %) | 43 / 10441 (0.4 %) |
| C2 — persistance selon confirmation (isolé 0.60, confirmé 0.89) | 18175 | 15.87 | 0.0463 | 83 / 12684 (0.7 %) | 43 / 10441 (0.4 %) |
| D — prévision Chainlink (dernier Chainlink + 0.98 × écart consensus) | 18175 | 15.74 | 0.0462 | 74 / 12659 (0.6 %) | 30 / 10402 (0.3 %) |

### nuit 10.10

| Modèle | Mesures | Erreur moyenne finale (RMSE, $) | Brier | Proba > 95 % fausse | Proba > 99 % fausse |
|---|---|---|---|---|---|
| A — actuel (dernier prix Bybit prolongé) | 5980 | 7.70 | 0.0602 | 89 / 4213 (2.1 %) | 58 / 3638 (1.6 %) |
| B — anti-saut (saut accepté si confirmé ou après 2 s) | 5980 | 7.69 | 0.0595 | 87 / 4213 (2.1 %) | 58 / 3637 (1.6 %) |
| C — persistance du saut (garde 0.88 du saut) | 5980 | 7.70 | 0.0600 | 89 / 4215 (2.1 %) | 58 / 3632 (1.6 %) |
| C2 — persistance selon confirmation (isolé 0.60, confirmé 0.89) | 5980 | 7.69 | 0.0597 | 87 / 4213 (2.1 %) | 58 / 3632 (1.6 %) |
| D — prévision Chainlink (dernier Chainlink + 0.98 × écart consensus) | 5980 | 7.31 | 0.0582 | 75 / 4171 (1.8 %) | 44 / 3587 (1.2 %) |

### régime calme

| Modèle | Mesures | Erreur moyenne finale (RMSE, $) | Brier | Proba > 95 % fausse | Proba > 99 % fausse |
|---|---|---|---|---|---|
| A — actuel (dernier prix Bybit prolongé) | 7490 | 7.99 | 0.0660 | 136 / 5438 (2.5 %) | 87 / 4651 (1.9 %) |
| B — anti-saut (saut accepté si confirmé ou après 2 s) | 7490 | 7.98 | 0.0655 | 134 / 5438 (2.5 %) | 87 / 4650 (1.9 %) |
| C — persistance du saut (garde 0.88 du saut) | 7490 | 7.99 | 0.0659 | 135 / 5437 (2.5 %) | 87 / 4644 (1.9 %) |
| C2 — persistance selon confirmation (isolé 0.60, confirmé 0.89) | 7490 | 7.98 | 0.0656 | 133 / 5435 (2.4 %) | 87 / 4643 (1.9 %) |
| D — prévision Chainlink (dernier Chainlink + 0.98 × écart consensus) | 7490 | 7.61 | 0.0644 | 115 / 5391 (2.1 %) | 55 / 4626 (1.2 %) |

### régime agité

| Modèle | Mesures | Erreur moyenne finale (RMSE, $) | Brier | Proba > 95 % fausse | Proba > 99 % fausse |
|---|---|---|---|---|---|
| A — actuel (dernier prix Bybit prolongé) | 45767 | 19.63 | 0.0412 | 72 / 32014 (0.2 %) | 14 / 26819 (0.1 %) |
| B — anti-saut (saut accepté si confirmé ou après 2 s) | 45767 | 19.63 | 0.0413 | 72 / 32012 (0.2 %) | 14 / 26820 (0.1 %) |
| C — persistance du saut (garde 0.88 du saut) | 45767 | 19.63 | 0.0412 | 72 / 32013 (0.2 %) | 14 / 26817 (0.1 %) |
| C2 — persistance selon confirmation (isolé 0.60, confirmé 0.89) | 45767 | 19.63 | 0.0412 | 72 / 32011 (0.2 %) | 14 / 26817 (0.1 %) |
| D — prévision Chainlink (dernier Chainlink + 0.98 × écart consensus) | 45767 | 19.49 | 0.0413 | 51 / 31986 (0.2 %) | 19 / 26848 (0.1 %) |

### Rejeu TWAP fin avec chaque modèle (premier signal du cycle, avantage ≥ 0,20, 90-20 s, 50 $ max limité à la quantité affichée, frais compris)

| Modèle | Période | Achats | Gagnés | Résultat | Par $ | Creux | Pertes de suite | Jackpots (≥ 4× la mise) |
|---|---|---|---|---|---|---|---|---|
| A — actuel (dernier prix Bybit prolongé) | apprentissage | 86 | 42 % | **+1'195 $** | +75 % | −153 $ | 5 | 10 (+989 $) |
| A — actuel (dernier prix Bybit prolongé) | validation | 58 | 50 % | **+1'214 $** | +87 % | −215 $ | 5 | 8 (+1'138 $) |
| A — actuel (dernier prix Bybit prolongé) | nuit 10.10 | 28 | 36 % | **−241 $** | -29 % | −331 $ | 8 | 3 (+157 $) |
| B — anti-saut (saut accepté si confirmé ou après 2 s) | apprentissage | 85 | 42 % | **+1'403 $** | +85 % | −153 $ | 5 | 11 (+1'200 $) |
| B — anti-saut (saut accepté si confirmé ou après 2 s) | validation | 58 | 50 % | **+1'214 $** | +87 % | −215 $ | 5 | 8 (+1'138 $) |
| B — anti-saut (saut accepté si confirmé ou après 2 s) | nuit 10.10 | 28 | 39 % | **−215 $** | -26 % | −304 $ | 5 | 3 (+157 $) |
| C — persistance du saut (garde 0.88 du saut) | apprentissage | 83 | 41 % | **+1'192 $** | +75 % | −152 $ | 5 | 10 (+989 $) |
| C — persistance du saut (garde 0.88 du saut) | validation | 58 | 50 % | **+1'257 $** | +93 % | −172 $ | 5 | 8 (+1'138 $) |
| C — persistance du saut (garde 0.88 du saut) | nuit 10.10 | 28 | 32 % | **−409 $** | -47 % | −480 $ | 7 | 1 (+40 $) |
| C2 — persistance selon confirmation (isolé 0.60, confirmé 0.89) | apprentissage | 82 | 41 % | **+1'400 $** | +85 % | −152 $ | 5 | 11 (+1'200 $) |
| C2 — persistance selon confirmation (isolé 0.60, confirmé 0.89) | validation | 58 | 50 % | **+1'257 $** | +93 % | −172 $ | 5 | 8 (+1'138 $) |
| C2 — persistance selon confirmation (isolé 0.60, confirmé 0.89) | nuit 10.10 | 28 | 36 % | **−297 $** | -33 % | −388 $ | 4 | 1 (+40 $) |
| D — prévision Chainlink (dernier Chainlink + 0.98 × écart consensus) | apprentissage | 68 | 34 % | **+1'197 $** | +71 % | −565 $ | 7 | 10 (+1'696 $) |
| D — prévision Chainlink (dernier Chainlink + 0.98 × écart consensus) | validation | 37 | 38 % | **+811 $** | +71 % | −331 $ | 6 | 4 (+898 $) |
| D — prévision Chainlink (dernier Chainlink + 0.98 × écart consensus) | nuit 10.10 | 24 | 54 % | **+175 $** | +34 % | −177 $ | 4 | 3 (+176 $) |

## Q18. Basculements extrêmes de la probabilité (modèle actuel), entre 90 et 20 s

| Basculement en 1 s | Événements | Déclenché surtout par Bybit | Chainlink a bougé dans le même sens | Revenu à moins de la moitié 5 s après | Le nouveau côté a gagné | Dont régime calme : gagné |
|---|---|---|---|---|---|---|
| > 20 points | 338 | 62 % | 19 % | 14 % | 65 % | 67 % (48) |
| > 40 points | 71 | 54 % | 27 % | 10 % | 76 % | 75 % (32) |
| > 70 points | 14 | 57 % | 21 % | 0 % | 71 % | 56 % (9) |
| de < 5 % à > 95 % (ou inverse) | 2 | 100 % | 0 % | 0 % | 50 % | 50 % (2) |