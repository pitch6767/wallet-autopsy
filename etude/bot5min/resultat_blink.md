# Qui converge vers qui ? — desaccords >= 0,20, vrais carnets du bot (48 h)

Familles a +1 / +3 / +10 s : POLY REJOINT = Polymarket monte de >= 3 c vers le modele (modele stable) ; MODELE RETOMBE = le modele baisse de >= 3 c (Poly stable) ; LES DEUX ; RIEN.
Resultat : achat 50 $ au meilleur vendeur a l'entree, garde jusqu'a la fin, frais compris.

## BTC — 293 desaccords >= 0,20

### Apres 1 s

| Famille | Desaccords | Part | Gagnes a la fin | Resultat (achat a l'entree) | Gain / trade | « Attendre et acheter seulement si POLY REJOINT » |
|---|---|---|---|---|---|---|
| POLY REJOINT | 44 | 15 % | 43 % | +1723 $ | +39.2 $ | 43 trades · +377 $ (1re moitie +4 / 2e +373) |
| MODELE RETOMBE | 45 | 16 % | 16 % | -792 $ | -17.6 $ |  |
| LES DEUX | 4 | 1 % | 25 % | +38 $ | +9.6 $ |  |
| RIEN | 196 | 68 % | 15 % | +49 $ | +0.2 $ |  |
| **tous** | 289 | 100 % | 19 % | **+1019 $** | +3.5 $ | |

### Apres 3 s

| Famille | Desaccords | Part | Gagnes a la fin | Resultat (achat a l'entree) | Gain / trade | « Attendre et acheter seulement si POLY REJOINT » |
|---|---|---|---|---|---|---|
| POLY REJOINT | 48 | 17 % | 42 % | +1635 $ | +34.1 $ | 47 trades · +246 $ (1re moitie +119 / 2e +127) |
| MODELE RETOMBE | 60 | 21 % | 12 % | -1382 $ | -23.0 $ |  |
| LES DEUX | 6 | 2 % | 17 % | -208 $ | -34.7 $ |  |
| RIEN | 175 | 61 % | 16 % | +974 $ | +5.6 $ |  |
| **tous** | 289 | 100 % | 19 % | **+1019 $** | +3.5 $ | |

### Apres 10 s

| Famille | Desaccords | Part | Gagnes a la fin | Resultat (achat a l'entree) | Gain / trade | « Attendre et acheter seulement si POLY REJOINT » |
|---|---|---|---|---|---|---|
| POLY REJOINT | 69 | 24 % | 43 % | +6404 $ | +92.8 $ | 68 trades · +1148 $ (1re moitie +757 / 2e +391) |
| MODELE RETOMBE | 92 | 33 % | 8 % | -3439 $ | -37.4 $ |  |
| LES DEUX | 6 | 2 % | 33 % | +29 $ | +4.8 $ |  |
| RIEN | 115 | 41 % | 15 % | -1603 $ | -13.9 $ |  |
| **tous** | 282 | 100 % | 20 % | **+1391 $** | +4.9 $ | |

### Ce qui annonce la famille a 3 s (bourses dans les 3 s AVANT l'entree)

| Signal | Sens | Desaccords | POLY REJOINT | MODELE RETOMBE | Resultat |
|---|---|---|---|---|---|
| Binance | contre nous | 146 | 13 % | 21 % | -2340 $ |
| Binance | neutre | 78 | 13 % | 19 % | +903 $ |
| Binance | avec nous | 65 | 29 % | 22 % | +2455 $ |
| Bybit perp | contre nous | 147 | 11 % | 23 % | -1716 $ |
| Bybit perp | neutre | 71 | 10 % | 18 % | +670 $ |
| Bybit perp | avec nous | 71 | 35 % | 18 % | +2065 $ |
| OKX | contre nous | 128 | 12 % | 22 % | -2258 $ |
| OKX | neutre | 92 | 10 % | 20 % | +1769 $ |
| OKX | avec nous | 69 | 33 % | 20 % | +1508 $ |
| Coinbase | contre nous | 154 | 13 % | 21 % | -2080 $ |
| Coinbase | neutre | 70 | 13 % | 21 % | +81 $ |
| Coinbase | avec nous | 65 | 29 % | 20 % | +3018 $ |
| Chainlink | contre nous | 167 | 14 % | 23 % | -713 $ |
| Chainlink | neutre | 27 | 15 % | 15 % | +127 $ |
| Chainlink | avec nous | 95 | 21 % | 19 % | +1605 $ |
| Polymarket | contre nous | 234 | 12 % | 22 % | -1482 $ |
| Polymarket | neutre | 38 | 32 % | 18 % | +2563 $ |
| Polymarket | avec nous | 17 | 41 % | 12 % | -63 $ |

### Peut-on prevoir a l'entree ? (appris 1re moitie, juge 2e moitie — AUC : 0,50 = hasard, 1 = parfait)

| Variables | AUC « POLY REJOINT » a 3 s | AUC « MODELE RETOMBE » a 3 s | AUC gagnant a la fin |
|---|---|---|---|
| toutes les sources | 0.71 | 0.48 | 0.61 |
| sans Binance | 0.72 | 0.47 | 0.62 |
| sans Bybit perp | 0.72 | 0.50 | 0.61 |
| sans OKX | 0.71 | 0.47 | 0.62 |
| sans Coinbase | 0.72 | 0.49 | 0.61 |
| sans Chainlink | 0.70 | 0.52 | 0.61 |
| sans carnet Poly | 0.62 | 0.50 | 0.56 |
| seulement temps/prix/ecart | 0.63 | 0.51 | 0.61 |

## ETH — 261 desaccords >= 0,20

### Apres 1 s

| Famille | Desaccords | Part | Gagnes a la fin | Resultat (achat a l'entree) | Gain / trade | « Attendre et acheter seulement si POLY REJOINT » |
|---|---|---|---|---|---|---|
| POLY REJOINT | 39 | 15 % | 21 % | +543 $ | +13.9 $ | 39 trades · -650 $ (1re moitie -694 / 2e +45) |
| MODELE RETOMBE | 35 | 13 % | 14 % | -933 $ | -26.7 $ |  |
| LES DEUX | 2 | 1 % | 50 % | +62 $ | +30.9 $ |  |
| RIEN | 184 | 71 % | 20 % | +718 $ | +3.9 $ |  |
| **tous** | 260 | 100 % | 20 % | **+389 $** | +1.5 $ | |

### Apres 3 s

| Famille | Desaccords | Part | Gagnes a la fin | Resultat (achat a l'entree) | Gain / trade | « Attendre et acheter seulement si POLY REJOINT » |
|---|---|---|---|---|---|---|
| POLY REJOINT | 55 | 22 % | 38 % | +3462 $ | +62.9 $ | 55 trades · +1341 $ (1re moitie -101 / 2e +1443) |
| MODELE RETOMBE | 55 | 22 % | 11 % | -1591 $ | -28.9 $ |  |
| LES DEUX | 2 | 1 % | 50 % | +31 $ | +15.3 $ |  |
| RIEN | 141 | 56 % | 16 % | -1138 $ | -8.1 $ |  |
| **tous** | 253 | 100 % | 20 % | **+763 $** | +3.0 $ | |

### Apres 10 s

| Famille | Desaccords | Part | Gagnes a la fin | Resultat (achat a l'entree) | Gain / trade | « Attendre et acheter seulement si POLY REJOINT » |
|---|---|---|---|---|---|---|
| POLY REJOINT | 70 | 28 % | 41 % | +4640 $ | +66.3 $ | 70 trades · +407 $ (1re moitie +70 / 2e +337) |
| MODELE RETOMBE | 70 | 28 % | 13 % | -1543 $ | -22.0 $ |  |
| LES DEUX | 4 | 2 % | 50 % | +97 $ | +24.3 $ |  |
| RIEN | 102 | 41 % | 11 % | -2059 $ | -20.2 $ |  |
| **tous** | 246 | 100 % | 21 % | **+1135 $** | +4.6 $ | |

### Ce qui annonce la famille a 3 s (bourses dans les 3 s AVANT l'entree)

| Signal | Sens | Desaccords | POLY REJOINT | MODELE RETOMBE | Resultat |
|---|---|---|---|---|---|
| Binance | contre nous | 125 | 24 % | 26 % | +540 $ |
| Binance | neutre | 82 | 17 % | 18 % | +79 $ |
| Binance | avec nous | 46 | 24 % | 17 % | +144 $ |
| Bybit perp | contre nous | 137 | 23 % | 26 % | -72 $ |
| Bybit perp | neutre | 70 | 20 % | 14 % | +921 $ |
| Bybit perp | avec nous | 46 | 22 % | 22 % | -86 $ |
| OKX | contre nous | 116 | 24 % | 29 % | +316 $ |
| OKX | neutre | 83 | 18 % | 13 % | +127 $ |
| OKX | avec nous | 54 | 22 % | 19 % | +321 $ |
| Coinbase | contre nous | 141 | 25 % | 27 % | -793 $ |
| Coinbase | neutre | 52 | 15 % | 17 % | +959 $ |
| Coinbase | avec nous | 60 | 20 % | 13 % | +597 $ |
| Chainlink | contre nous | 148 | 24 % | 24 % | +649 $ |
| Chainlink | neutre | 27 | 15 % | 7 % | +728 $ |
| Chainlink | avec nous | 78 | 19 % | 23 % | -615 $ |
| Polymarket | contre nous | 201 | 24 % | 24 % | -644 $ |
| Polymarket | neutre | 36 | 14 % | 11 % | +990 $ |
| Polymarket | avec nous | 16 | 12 % | 19 % | +417 $ |

### Peut-on prevoir a l'entree ? (appris 1re moitie, juge 2e moitie — AUC : 0,50 = hasard, 1 = parfait)

| Variables | AUC « POLY REJOINT » a 3 s | AUC « MODELE RETOMBE » a 3 s | AUC gagnant a la fin |
|---|---|---|---|
| toutes les sources | 0.50 | 0.60 | 0.66 |
| sans Binance | 0.52 | 0.56 | 0.66 |
| sans Bybit perp | 0.52 | 0.59 | 0.66 |
| sans OKX | 0.54 | 0.55 | 0.64 |
| sans Coinbase | 0.54 | 0.62 | 0.67 |
| sans Chainlink | 0.52 | 0.66 | 0.62 |
| sans carnet Poly | 0.49 | 0.49 | 0.63 |
| seulement temps/prix/ecart | 0.53 | 0.63 | 0.62 |
