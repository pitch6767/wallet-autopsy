# Bot95 — les fantômes lancés le 09.10.2026 : résultats détaillés

Rapport du 09.10.2026 à 20:57 (heure suisse) · BTC 5 min Polymarket · 50 $ par trade, frais Polymarket compris · aucun argent réel (fantômes : achats simulés au vrai carnet, en descendant jusqu'à +1 c).

## Contexte (pour relecture)

- Le modèle du bot calcule la probabilité Up/Down à partir du prix BTC (perp Bybit/OKX ramené au niveau Chainlink), du prix à battre, du temps restant et de la volatilité 5 min. Il ajoutait une incertitude fixe de 0,08 % (≈ 66 $) qui tire toutes les probabilités vers 50 % : il annonçait 42 % de chances en moyenne sur V2-F, on gagnait 24 %.
- Le rejeu sur les carnets enregistrés (07-09.10) donnait avec 0,015 % : 38 % de gagnants, creux divisé par 3,5, positif dans les 4 quarts. La cohorte « corrigé » teste cela en direct depuis le 09.10 à 08:54, en parallèle des originaux inchangés.

## En bref

- **Les 4 fantômes « corrigé » gagnent tous de l'argent** et gagnent 35 à 40 % du temps, contre 21-22 % pour les originaux sur la même période : le taux de gagnants du rejeu (38 %) se confirme en direct. Sur la même période, V2-F original et désaccord 20 original perdent de l'argent.
- **Le mécanisme est le même que dans le rejeu :** sur les cycles achetés par les deux, le corrigé gagne un peu moins que l'original (il achète plus tard et plus cher : ~0,33 $ contre ~0,23 $). Tout son avantage vient des cycles qu'il refuse : 20 à 23 cycles évités par cohorte V2-F/désaccord, qui coûtaient −744 à −811 $ à l'original.
- **Fragilité :** le résultat du corrigé V2-F dépend encore de ses meilleurs trades (sans les 3 meilleurs, il est négatif) ; une seule journée de données.
- **Les filtres sur V2-F (modèle actuel) ne marchent pas en direct** : « pas les deux baissent » perd (−381 $) et ne change presque pas les cycles achetés (il décale juste l'achat dans le même cycle) ; avec « volatilité ≥ 2 » c'est pire (supprimé à 18:00). « Plus de 120 s » est positif (+247 $) alors que V2-F perd sur la même période : il évite 28 cycles qui coûtaient −568 $.

## Résumé (chiffres du bot à l'heure du rapport)

| Fantôme | Depuis | Trades | Gagnés | % gagnés | Résultat | Creux max | Pertes de suite max | Original sur la même période |
|---|---|---|---|---|---|---|---|---|
| corrige : V2-F ecart qui grandit | 09.10 08:54 | 84 | 32 | 38 % | **+617 $** | −769 $ | 8 | V2-F ecart qui grandit : 108 trades, 21 %, −265 $ |
| corrige : V2-F + pas les deux baissent | 09.10 08:54 | 81 | 31 | 38 % | **+544 $** | −846 $ | 8 | V2-F ecart qui grandit : 108 trades, 21 %, −265 $ |
| corrige : desaccord 20 | 09.10 08:54 | 86 | 32 | 37 % | **+242 $** | −965 $ | 10 | desaccord 20 : 104 trades, 22 %, −286 $ |
| corrige : zone + Binance et perp + sortie -10 | 09.10 08:54 | 32 | 11 | 34 % | **+632 $** | −125 $ | 5 | desaccord 30 zone + Binance et perp + sortie modele -10 : 36 trades, 36 %, +372 $ |
| V2-F + pas les deux baissent | 09.10 08:27 | 117 | 24 | 21 % | **−291 $** | −1'212 $ | 15 | V2-F ecart qui grandit : 113 trades, 20 %, −529 $ |
| V2-F + plus de 120 s | 09.10 08:32 | 85 | 20 | 24 % | **+403 $** | −685 $ | 12 | V2-F ecart qui grandit : 112 trades, 21 %, −476 $ |
| V2-F + pas les deux baissent + volatilite >= 2 | 09.10 09:01 | 48 | 11 | 23 % | **−540 $** | −852 $ | 13 | V2-F ecart qui grandit : 56 trades, 29 %, +386 $ |

« Original sur la même période » : trades de la stratégie d'origine (modèle 0,08 %, sans filtre) depuis la même heure, d'après ses trades sauvegardés.
---PAGE---
## 1. corrige : V2-F ecart qui grandit

**Règle :** Exactement la règle V2-F (écart modèle − meilleur vendeur ≥ 0,20 ET écart plus grand d'au moins 3 pts qu'il y a 3 s, ≥ 5 s restantes, prix 0,03-0,97, 50 $, un achat par cycle, gardé jusqu'au résultat), mais la probabilité du modèle est calculée avec une incertitude fixe de 0,015 % du prix BTC (≈ 12 $) au lieu de 0,08 % (≈ 66 $).

- Trades : **84** (82 dont j'ai le détail), 32 gagnés (38 %), résultat **+617 $**, creux max −769 $, pertes de suite max 8.
- Gain moyen d'un gagnant +84 $, perte moyenne d'un perdant −39 $, mise moyenne réellement remplie 40 $. Sans les 3 meilleurs trades : −194 $.
- **Original (V2-F ecart qui grandit) sur la même période :** 108 trades, 23 gagnés (21 %), −265 $, creux −989 $, pertes de suite max 15.

### Mêmes cycles que l'original

| | Cycles | Résultat de ce fantôme | Résultat de l'original |
|---|---|---|---|
| achetés par les deux | 78 | +719 $ | +734 $ |
| seulement ce fantôme | 3 | +59 $ | — |
| seulement l'original (évités) | 29 | — | −1'146 $ |
| ↳ sur les cycles communs : même côté | 70 / 78 | prix moyen 0.32 | prix moyen 0.23 |

### Par prix d'achat

| Groupe | Trades | Gagnés | % | Résultat |
|---|---|---|---|---|
| < 0,10 $ | 3 | 0 | 0 % | −75 $ |
| 0,10-0,20 $ | 13 | 3 | 23 % | +426 $ |
| 0,20-0,35 $ | 33 | 10 | 30 % | +33 $ |
| ≥ 0,35 $ | 33 | 19 | 58 % | +342 $ |

### Par temps restant à l'achat

| Groupe | Trades | Gagnés | % | Résultat |
|---|---|---|---|---|
| < 60 s | 4 | 1 | 25 % | −49 $ |
| 60-120 s | 23 | 9 | 39 % | −197 $ |
| 120-200 s | 23 | 11 | 48 % | +752 $ |
| ≥ 200 s | 32 | 11 | 34 % | +219 $ |

### Par heure (suisse)

| Groupe | Trades | Gagnés | % | Résultat |
|---|---|---|---|---|
| 09h | 9 | 6 | 67 % | +417 $ |
| 10h | 11 | 6 | 55 % | +156 $ |
| 11h | 8 | 5 | 62 % | +344 $ |
| 12h | 8 | 3 | 38 % | +371 $ |
| 13h | 7 | 2 | 29 % | −70 $ |
| 14h | 6 | 0 | 0 % | −179 $ |
| 15h | 4 | 3 | 75 % | +186 $ |
| 16h | 5 | 2 | 40 % | −50 $ |
| 17h | 7 | 1 | 14 % | −104 $ |
| 18h | 5 | 2 | 40 % | −81 $ |
| 19h | 9 | 2 | 22 % | −155 $ |
| 20h | 3 | 0 | 0 % | −108 $ |

### Tous les trades

| # | Heure (CH) | Côté | Prix | Jetons | Modèle | Reste | Issue | Résultat | Cumul |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 09.10 09:07:32 | Down | 0.284 | 46 | 0.47 | 148 s | une seule jambe | +32.68 $ | +32.68 $ |
| 2 | 09.10 09:10:38 | Down | 0.195 | 278 | 0.417 | 262 s | une seule jambe | +223.63 $ | +256.31 $ |
| 3 | 09.10 09:15:48 | Down | 0.320 | 167 | 0.563 | 251 s | une seule jambe | −53.36 $ | +202.95 $ |
| 4 | 09.10 09:21:44 | Up | 0.518 | 94 | 0.711 | 195 s | une seule jambe | +45.37 $ | +248.32 $ |
| 5 | 09.10 09:25:51 | Down | 0.389 | 123 | 0.604 | 249 s | une seule jambe | +75.34 $ | +323.66 $ |
| 6 | 09.10 09:33:50 | Up | 0.568 | 91 | 1 | 69 s | une seule jambe | +39.29 $ | +362.95 $ |
| 7 | 09.10 09:48:27 | Up | 0.189 | 93 | 0.37 | 92 s | une seule jambe | −17.50 $ | +345.45 $ |
| 8 | 09.10 09:51:09 | Up | 0.294 | 179 | 0.486 | 231 s | une seule jambe | +125.98 $ | +471.43 $ |
| 9 | 09.10 09:55:25 | Down | 0.240 | 227 | 0.506 | 275 s | une seule jambe | −54.55 $ | +416.88 $ |
| 10 | 09.10 10:02:28 | Down | 0.387 | 90 | 0.578 | 152 s | une seule jambe | +55.19 $ | +472.07 $ |
| 11 | 09.10 10:08:30 | Up | 0.666 | 77 | 0.882 | 90 s | une seule jambe | +25.66 $ | +497.73 $ |
| 12 | 09.10 10:12:50 | Up | 0.394 | 135 | 0.571 | 129 s | une seule jambe | +81.90 $ | +579.63 $ |
| 13 | 09.10 10:19:06 | Up | 0.315 | 10 | 0.532 | 53 s | une seule jambe | −3.15 $ | +576.48 $ |
| 14 | 09.10 10:22:40 | Up | 0.405 | 26 | 0.58 | 140 s | une seule jambe | −10.53 $ | +565.95 $ |
| 15 | 09.10 10:29:00 | Up | 0.617 | 83 | 0.968 | 59 s | une seule jambe | +31.89 $ | +597.84 $ |
| 16 | 09.10 10:31:11 | Down | 0.632 | 20 | 0.812 | 228 s | une seule jambe | +7.36 $ | +605.20 $ |
| 17 | 09.10 10:36:17 | Down | 0.397 | 132 | 0.614 | 222 s | une seule jambe | −52.23 $ | +552.97 $ |
| 18 | 09.10 10:42:21 | Down | 0.503 | 104 | 0.758 | 158 s | une seule jambe | −52.36 $ | +500.61 $ |
| 19 | 09.10 10:46:05 | Up | 0.302 | 179 | 0.48 | 235 s | une seule jambe | +124.65 $ | +625.26 $ |
| 20 | 09.10 10:50:49 | Down | 0.356 | 147 | 0.572 | 251 s | une seule jambe | −52.38 $ | +572.88 $ |
| 21 | 09.10 11:05:58 | Up | 0.294 | 179 | 0.486 | 241 s | une seule jambe | −52.59 $ | +520.29 $ |
| 22 | 09.10 11:17:46 | Up | 0.264 | 30 | 0.495 | 133 s | une seule jambe | +22.09 $ | +542.38 $ |
| 23 | 09.10 11:20:10 | Up | 0.315 | 167 | 0.507 | 289 s | une seule jambe | +114.15 $ | +656.53 $ |
| 24 | 09.10 11:25:54 | Up | 0.243 | 217 | 0.449 | 246 s | une seule jambe | −52.77 $ | +603.76 $ |
| 25 | 09.10 11:36:06 | Down | 0.346 | 152 | 0.601 | 234 s | une seule jambe | +99.10 $ | +702.86 $ |
| 26 | 09.10 11:41:35 | Down | 0.211 | 250 | 0.452 | 205 s | une seule jambe | +197.12 $ | +899.98 $ |
| 27 | 09.10 11:50:39 | Down | 0.356 | 147 | 0.557 | 261 s | une seule jambe | −52.38 $ | +847.60 $ |
| 28 | 09.10 11:57:19 | Down | 0.434 | 122 | 0.614 | 161 s | une seule jambe | +69.00 $ | +916.60 $ |
| 29 | 09.10 12:01:50 | Up | 0.102 | 556 | 0.334 | 189 s | une seule jambe | +498.76 $ | +1'415.36 $ |
| 30 | 09.10 12:08:14 | Down | 0.438 | 119 | 0.631 | 106 s | une seule jambe | +66.96 $ | +1'482.32 $ |
| 31 | 09.10 12:10:18 | Down | 0.332 | 26 | 0.618 | 282 s | une seule jambe | −8.62 $ | +1'473.70 $ |
| 32 | 09.10 12:16:19 | Down | 0.705 | 72 | 0.919 | 221 s | une seule jambe | +21.35 $ | +1'495.05 $ |
| 33 | 09.10 12:22:41 | Up | 0.260 | 171 | 0.449 | 139 s | une seule jambe | −44.44 $ | +1'450.61 $ |
| 34 | 09.10 12:28:10 | Down | 0.304 | 179 | 0.485 | 109 s | une seule jambe | −54.35 $ | +1'396.26 $ |
| 35 | 09.10 12:35:18 | Up | 0.261 | 208 | 0.544 | 281 s | une seule jambe | −54.41 $ | +1'341.85 $ |
| 36 | 09.10 12:52:53 | Up | 0.291 | 185 | 0.578 | 127 s | une seule jambe | −53.92 $ | +1'287.93 $ |
| 37 | 09.10 13:08:18 | Down | 0.156 | 357 | 0.342 | 102 s | une seule jambe | −55.83 $ | +1'232.10 $ |
| 38 | 09.10 13:10:03 | Up | 0.325 | 161 | 0.546 | 297 s | une seule jambe | −52.48 $ | +1'179.62 $ |
| 39 | 09.10 13:16:12 | Down | 0.302 | 105 | 0.483 | 228 s | une seule jambe | −31.70 $ | +1'147.92 $ |
| 40 | 09.10 13:27:56 | Down | 0.568 | 91 | 0.769 | 124 s | une seule jambe | −51.62 $ | +1'096.30 $ |
| 41 | 09.10 13:35:52 | Up | 0.325 | 161 | 0.644 | 248 s | une seule jambe | +108.81 $ | +1'205.11 $ |
| 42 | 09.10 13:43:28 | Down | 0.586 | 89 | 0.761 | 92 s | une seule jambe | +36.98 $ | +1'242.09 $ |
| 43 | 09.10 13:59:46 | Up | 0.038 | 638 | 0.306 | 13 s | une seule jambe | −24.56 $ | +1'217.53 $ |
| 44 | 09.10 14:01:30 | Down | 0.292 | 185 | 0.479 | 209 s | une seule jambe | −54.04 $ | +1'163.49 $ |
| 45 | 09.10 14:10:19 | Up | 0.558 | 35 | 0.77 | 281 s | une seule jambe | −19.53 $ | +1'143.96 $ |
| 46 | 09.10 14:17:30 | Up | 0.211 | 5 | 0.416 | 149 s | une seule jambe | −1.06 $ | +1'142.90 $ |
| 47 | 09.10 14:27:31 | Up | 0.149 | 5 | 0.349 | 149 s | une seule jambe | −0.74 $ | +1'142.16 $ |
| 48 | 09.10 14:36:21 | Up | 0.294 | 170 | 0.474 | 219 s | une seule jambe | −50.02 $ | +1'092.14 $ |
| 49 | 09.10 14:48:44 | Down | 0.256 | 208 | 0.638 | 75 s | une seule jambe | −53.34 $ | +1'038.80 $ |
| 50 | 09.10 15:17:55 | Up | 0.381 | 75 | 0.593 | 125 s | une seule jambe | +46.45 $ | +1'085.25 $ |
| 51 | 09.10 15:20:24 | Down | 0.447 | 119 | 0.629 | 275 s | une seule jambe | +65.81 $ | +1'151.06 $ |
| 52 | 09.10 15:48:24 | Up | 0.356 | 147 | 0.558 | 96 s | une seule jambe | +94.68 $ | +1'245.74 $ |
| 53 | 09.10 15:58:46 | Up | 0.069 | 308 | 0.374 | 73 s | une seule jambe | −21.26 $ | +1'224.48 $ |
| 54 | 09.10 16:03:48 | Up | 0.441 | 97 | 0.625 | 72 s | une seule jambe | +54.45 $ | +1'278.93 $ |
| 55 | 09.10 16:13:10 | Up | 0.412 | 10 | 0.592 | 110 s | une seule jambe | +6.03 $ | +1'284.96 $ |
| 56 | 09.10 16:28:21 | Up | 0.294 | 179 | 0.485 | 98 s | une seule jambe | −52.59 $ | +1'232.37 $ |
| 57 | 09.10 16:33:44 | Down | 0.117 | 40 | 0.318 | 76 s | une seule jambe | −4.66 $ | +1'227.71 $ |
| 58 | 09.10 16:41:41 | Up | 0.497 | 106 | 0.67 | 198 s | une seule jambe | −52.93 $ | +1'174.78 $ |
| 59 | 09.10 17:13:13 | Down | 0.158 | 357 | 0.345 | 107 s | une seule jambe | −56.43 $ | +1'118.35 $ |
| 60 | 09.10 17:21:39 | Up | 0.426 | 125 | 0.674 | 201 s | une seule jambe | −53.22 $ | +1'065.13 $ |
| 61 | 09.10 17:26:21 | Down | 0.472 | 111 | 0.654 | 219 s | une seule jambe | −52.49 $ | +1'012.64 $ |
| 62 | 09.10 17:29:02 | Down | 0.180 | 294 | 0.738 | 58 s | une seule jambe | −52.99 $ | +959.65 $ |
| 63 | 09.10 17:38:45 | Down | 0.042 | 698 | 0.266 | 74 s | une seule jambe | −29.15 $ | +930.50 $ |
| 64 | 09.10 17:51:41 | Down | 0.232 | 227 | 0.42 | 198 s | une seule jambe | +174.46 $ | +1'104.96 $ |
| 65 | 09.10 17:55:35 | Down | 0.155 | 223 | 0.345 | 264 s | une seule jambe | −34.61 $ | +1'070.35 $ |
| 66 | 09.10 18:05:04 | Down | 0.232 | 227 | 0.456 | 296 s | une seule jambe | −52.81 $ | +1'017.54 $ |
| 67 | 09.10 18:18:40 | Down | 0.128 | 5 | 0.338 | 80 s | une seule jambe | +4.36 $ | +1'021.90 $ |
| 68 | 09.10 18:43:39 | Up | 0.427 | 75 | 0.611 | 81 s | une seule jambe | −32.06 $ | +989.84 $ |
| 69 | 09.10 18:53:04 | Down | 0.284 | 50 | 0.482 | 115 s | une seule jambe | +35.79 $ | +1'025.63 $ |
| 70 | 09.10 18:57:27 | Up | 0.366 | 100 | 0.566 | 153 s | une seule jambe | −36.64 $ | +988.99 $ |
| 71 | 09.10 19:02:07 | Down | 0.458 | 60 | 0.642 | 172 s | une seule jambe | +32.54 $ | +1'021.53 $ |
| 72 | 09.10 19:08:32 | Up | 0.253 | 208 | 0.505 | 87 s | une seule jambe | −52.74 $ | +968.79 $ |
| 73 | 09.10 19:10:45 | Up | 0.340 | 156 | 0.546 | 255 s | une seule jambe | −53.15 $ | +915.64 $ |
| 74 | 09.10 19:16:54 | Up | 0.462 | 114 | 0.645 | 186 s | une seule jambe | +61.10 $ | +976.74 $ |
| 75 | 09.10 19:20:49 | Up | 0.488 | 10 | 0.677 | 250 s | une seule jambe | −4.88 $ | +971.86 $ |
| 76 | 09.10 19:33:28 | Up | 0.152 | 141 | 0.359 | 91 s | une seule jambe | −21.52 $ | +950.34 $ |
| 77 | 09.10 19:38:53 | Down | 0.178 | 312 | 0.369 | 66 s | une seule jambe | −55.73 $ | +894.61 $ |
| 78 | 09.10 19:41:00 | Down | 0.478 | 109 | 0.661 | 240 s | une seule jambe | −51.94 $ | +842.67 $ |
| 79 | 09.10 19:46:51 | Up | 0.247 | 35 | 0.535 | 189 s | une seule jambe | −8.65 $ | +834.02 $ |
| 80 | 09.10 20:13:41 | Up | 0.292 | 185 | 0.512 | 78 s | une seule jambe | −54.13 $ | +779.89 $ |
| 81 | 09.10 20:17:05 | Up | 0.287 | 185 | 0.484 | 174 s | une seule jambe | −53.17 $ | +726.72 $ |
| 82 | 09.10 20:32:38 | Up | 0.191 | 6 | 0.382 | 141 s | une seule jambe | −1.14 $ | +725.58 $ |
---PAGE---
## 2. corrige : V2-F + pas les deux baissent

**Règle :** V2-F avec le modèle corrigé (0,015 %), en refusant les entrées où, sur les 3 dernières secondes, le modèle ET le prix Polymarket ont baissé, Polymarket plus fort que le modèle.

- Trades : **81** (79 dont j'ai le détail), 31 gagnés (38 %), résultat **+544 $**, creux max −846 $, pertes de suite max 8.
- Gain moyen d'un gagnant +85 $, perte moyenne d'un perdant −42 $, mise moyenne réellement remplie 42 $. Sans les 3 meilleurs trades : −267 $.
- **Original (V2-F ecart qui grandit) sur la même période :** 108 trades, 23 gagnés (21 %), −265 $, creux −989 $, pertes de suite max 15.

### Mêmes cycles que l'original

| | Cycles | Résultat de ce fantôme | Résultat de l'original |
|---|---|---|---|
| achetés par les deux | 75 | +646 $ | +705 $ |
| seulement ce fantôme | 3 | +59 $ | — |
| seulement l'original (évités) | 32 | — | −1'117 $ |
| ↳ sur les cycles communs : même côté | 67 / 75 | prix moyen 0.32 | prix moyen 0.23 |

### Par prix d'achat

| Groupe | Trades | Gagnés | % | Résultat |
|---|---|---|---|---|
| < 0,10 $ | 3 | 0 | 0 % | −75 $ |
| 0,10-0,20 $ | 13 | 3 | 23 % | +351 $ |
| 0,20-0,35 $ | 32 | 11 | 34 % | +71 $ |
| ≥ 0,35 $ | 31 | 17 | 55 % | +306 $ |

### Par temps restant à l'achat

| Groupe | Trades | Gagnés | % | Résultat |
|---|---|---|---|---|
| < 60 s | 3 | 1 | 33 % | −46 $ |
| 60-120 s | 25 | 9 | 36 % | −308 $ |
| 120-200 s | 21 | 10 | 48 % | +721 $ |
| ≥ 200 s | 30 | 11 | 37 % | +285 $ |

### Par heure (suisse)

| Groupe | Trades | Gagnés | % | Résultat |
|---|---|---|---|---|
| 09h | 9 | 6 | 67 % | +417 $ |
| 10h | 10 | 6 | 60 % | +159 $ |
| 11h | 8 | 5 | 62 % | +344 $ |
| 12h | 8 | 3 | 38 % | +371 $ |
| 13h | 7 | 2 | 29 % | −90 $ |
| 14h | 6 | 0 | 0 % | −235 $ |
| 15h | 4 | 3 | 75 % | +186 $ |
| 16h | 5 | 2 | 40 % | −52 $ |
| 17h | 6 | 1 | 17 % | −70 $ |
| 18h | 5 | 2 | 40 % | −81 $ |
| 19h | 8 | 1 | 12 % | −188 $ |
| 20h | 3 | 0 | 0 % | −108 $ |

### Tous les trades

| # | Heure (CH) | Côté | Prix | Jetons | Modèle | Reste | Issue | Résultat | Cumul |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 09.10 09:07:32 | Down | 0.284 | 46 | 0.47 | 148 s | une seule jambe | +32.68 $ | +32.68 $ |
| 2 | 09.10 09:10:38 | Down | 0.195 | 278 | 0.417 | 262 s | une seule jambe | +223.63 $ | +256.31 $ |
| 3 | 09.10 09:15:48 | Down | 0.320 | 167 | 0.563 | 251 s | une seule jambe | −53.36 $ | +202.95 $ |
| 4 | 09.10 09:21:44 | Up | 0.518 | 94 | 0.711 | 195 s | une seule jambe | +45.37 $ | +248.32 $ |
| 5 | 09.10 09:25:51 | Down | 0.389 | 123 | 0.604 | 249 s | une seule jambe | +75.34 $ | +323.66 $ |
| 6 | 09.10 09:33:50 | Up | 0.568 | 91 | 1 | 69 s | une seule jambe | +39.29 $ | +362.95 $ |
| 7 | 09.10 09:48:27 | Up | 0.189 | 93 | 0.37 | 92 s | une seule jambe | −17.50 $ | +345.45 $ |
| 8 | 09.10 09:51:09 | Up | 0.294 | 179 | 0.486 | 231 s | une seule jambe | +125.98 $ | +471.43 $ |
| 9 | 09.10 09:55:25 | Down | 0.240 | 227 | 0.506 | 275 s | une seule jambe | −54.55 $ | +416.88 $ |
| 10 | 09.10 10:02:28 | Down | 0.387 | 90 | 0.578 | 152 s | une seule jambe | +55.19 $ | +472.07 $ |
| 11 | 09.10 10:08:30 | Up | 0.666 | 77 | 0.882 | 90 s | une seule jambe | +25.66 $ | +497.73 $ |
| 12 | 09.10 10:12:50 | Up | 0.394 | 135 | 0.571 | 129 s | une seule jambe | +81.90 $ | +579.63 $ |
| 13 | 09.10 10:22:40 | Up | 0.405 | 26 | 0.58 | 140 s | une seule jambe | −10.53 $ | +569.10 $ |
| 14 | 09.10 10:29:00 | Up | 0.617 | 83 | 0.968 | 59 s | une seule jambe | +31.89 $ | +600.99 $ |
| 15 | 09.10 10:31:11 | Down | 0.632 | 20 | 0.812 | 228 s | une seule jambe | +7.36 $ | +608.35 $ |
| 16 | 09.10 10:36:17 | Down | 0.397 | 132 | 0.614 | 222 s | une seule jambe | −52.23 $ | +556.12 $ |
| 17 | 09.10 10:42:21 | Down | 0.503 | 104 | 0.758 | 158 s | une seule jambe | −52.36 $ | +503.76 $ |
| 18 | 09.10 10:46:05 | Up | 0.302 | 179 | 0.48 | 235 s | une seule jambe | +124.65 $ | +628.41 $ |
| 19 | 09.10 10:50:49 | Down | 0.356 | 147 | 0.572 | 251 s | une seule jambe | −52.38 $ | +576.03 $ |
| 20 | 09.10 11:05:58 | Up | 0.294 | 179 | 0.486 | 241 s | une seule jambe | −52.59 $ | +523.44 $ |
| 21 | 09.10 11:17:46 | Up | 0.264 | 30 | 0.495 | 133 s | une seule jambe | +22.09 $ | +545.53 $ |
| 22 | 09.10 11:20:10 | Up | 0.315 | 167 | 0.507 | 289 s | une seule jambe | +114.15 $ | +659.68 $ |
| 23 | 09.10 11:25:54 | Up | 0.243 | 217 | 0.449 | 246 s | une seule jambe | −52.77 $ | +606.91 $ |
| 24 | 09.10 11:36:06 | Down | 0.346 | 152 | 0.601 | 234 s | une seule jambe | +99.10 $ | +706.01 $ |
| 25 | 09.10 11:41:35 | Down | 0.211 | 250 | 0.452 | 205 s | une seule jambe | +197.12 $ | +903.13 $ |
| 26 | 09.10 11:50:39 | Down | 0.356 | 147 | 0.557 | 261 s | une seule jambe | −52.38 $ | +850.75 $ |
| 27 | 09.10 11:57:19 | Down | 0.434 | 122 | 0.614 | 161 s | une seule jambe | +69.00 $ | +919.75 $ |
| 28 | 09.10 12:01:50 | Up | 0.102 | 556 | 0.334 | 189 s | une seule jambe | +498.76 $ | +1'418.51 $ |
| 29 | 09.10 12:08:14 | Down | 0.438 | 119 | 0.631 | 106 s | une seule jambe | +66.96 $ | +1'485.47 $ |
| 30 | 09.10 12:10:18 | Down | 0.332 | 26 | 0.618 | 282 s | une seule jambe | −8.62 $ | +1'476.85 $ |
| 31 | 09.10 12:16:19 | Down | 0.705 | 72 | 0.919 | 221 s | une seule jambe | +21.35 $ | +1'498.20 $ |
| 32 | 09.10 12:22:41 | Up | 0.260 | 171 | 0.449 | 139 s | une seule jambe | −44.44 $ | +1'453.76 $ |
| 33 | 09.10 12:28:10 | Down | 0.304 | 179 | 0.485 | 109 s | une seule jambe | −54.35 $ | +1'399.41 $ |
| 34 | 09.10 12:35:18 | Up | 0.261 | 208 | 0.544 | 281 s | une seule jambe | −54.41 $ | +1'345.00 $ |
| 35 | 09.10 12:52:53 | Up | 0.291 | 185 | 0.578 | 127 s | une seule jambe | −53.92 $ | +1'291.08 $ |
| 36 | 09.10 13:08:18 | Down | 0.156 | 357 | 0.342 | 102 s | une seule jambe | −55.83 $ | +1'235.25 $ |
| 37 | 09.10 13:10:03 | Up | 0.315 | 167 | 0.545 | 296 s | une seule jambe | −52.52 $ | +1'182.73 $ |
| 38 | 09.10 13:18:37 | Down | 0.117 | 455 | 0.322 | 83 s | une seule jambe | −53.20 $ | +1'129.53 $ |
| 39 | 09.10 13:27:56 | Down | 0.568 | 91 | 0.769 | 124 s | une seule jambe | −51.62 $ | +1'077.91 $ |
| 40 | 09.10 13:35:52 | Up | 0.325 | 161 | 0.644 | 248 s | une seule jambe | +108.81 $ | +1'186.72 $ |
| 41 | 09.10 13:43:32 | Down | 0.478 | 75 | 0.671 | 88 s | une seule jambe | +39.16 $ | +1'225.88 $ |
| 42 | 09.10 13:59:46 | Up | 0.038 | 638 | 0.306 | 13 s | une seule jambe | −24.56 $ | +1'201.32 $ |
| 43 | 09.10 14:01:30 | Down | 0.292 | 185 | 0.479 | 209 s | une seule jambe | −54.04 $ | +1'147.28 $ |
| 44 | 09.10 14:10:19 | Up | 0.558 | 35 | 0.77 | 281 s | une seule jambe | −19.53 $ | +1'127.75 $ |
| 45 | 09.10 14:17:30 | Up | 0.211 | 5 | 0.416 | 149 s | une seule jambe | −1.06 $ | +1'126.69 $ |
| 46 | 09.10 14:28:29 | Up | 0.137 | 417 | 0.323 | 91 s | une seule jambe | −57.10 $ | +1'069.59 $ |
| 47 | 09.10 14:36:21 | Up | 0.294 | 170 | 0.474 | 219 s | une seule jambe | −50.02 $ | +1'019.57 $ |
| 48 | 09.10 14:48:44 | Down | 0.256 | 208 | 0.638 | 75 s | une seule jambe | −53.34 $ | +966.23 $ |
| 49 | 09.10 15:17:55 | Up | 0.381 | 75 | 0.593 | 125 s | une seule jambe | +46.45 $ | +1'012.68 $ |
| 50 | 09.10 15:20:24 | Down | 0.447 | 119 | 0.629 | 275 s | une seule jambe | +65.81 $ | +1'078.49 $ |
| 51 | 09.10 15:48:24 | Up | 0.356 | 147 | 0.558 | 96 s | une seule jambe | +94.68 $ | +1'173.17 $ |
| 52 | 09.10 15:58:46 | Up | 0.069 | 308 | 0.374 | 73 s | une seule jambe | −21.26 $ | +1'151.91 $ |
| 53 | 09.10 16:03:48 | Up | 0.441 | 97 | 0.625 | 72 s | une seule jambe | +54.45 $ | +1'206.36 $ |
| 54 | 09.10 16:13:36 | Up | 0.294 | 5 | 0.496 | 83 s | une seule jambe | +3.53 $ | +1'209.89 $ |
| 55 | 09.10 16:28:21 | Up | 0.294 | 179 | 0.485 | 98 s | une seule jambe | −52.59 $ | +1'157.30 $ |
| 56 | 09.10 16:33:44 | Down | 0.117 | 40 | 0.318 | 76 s | une seule jambe | −4.66 $ | +1'152.64 $ |
| 57 | 09.10 16:41:41 | Up | 0.497 | 106 | 0.67 | 198 s | une seule jambe | −52.93 $ | +1'099.71 $ |
| 58 | 09.10 17:13:13 | Down | 0.158 | 357 | 0.345 | 107 s | une seule jambe | −56.43 $ | +1'043.28 $ |
| 59 | 09.10 17:21:39 | Up | 0.426 | 125 | 0.674 | 201 s | une seule jambe | −53.22 $ | +990.06 $ |
| 60 | 09.10 17:26:21 | Down | 0.472 | 111 | 0.654 | 219 s | une seule jambe | −52.49 $ | +937.57 $ |
| 61 | 09.10 17:29:02 | Down | 0.180 | 294 | 0.738 | 58 s | une seule jambe | −52.99 $ | +884.58 $ |
| 62 | 09.10 17:38:45 | Down | 0.042 | 698 | 0.266 | 74 s | une seule jambe | −29.15 $ | +855.43 $ |
| 63 | 09.10 17:51:41 | Down | 0.232 | 227 | 0.42 | 198 s | une seule jambe | +174.46 $ | +1'029.89 $ |
| 64 | 09.10 18:05:04 | Down | 0.232 | 227 | 0.456 | 296 s | une seule jambe | −52.81 $ | +977.08 $ |
| 65 | 09.10 18:18:40 | Down | 0.128 | 5 | 0.338 | 80 s | une seule jambe | +4.36 $ | +981.44 $ |
| 66 | 09.10 18:43:39 | Up | 0.427 | 75 | 0.611 | 81 s | une seule jambe | −32.06 $ | +949.38 $ |
| 67 | 09.10 18:53:04 | Down | 0.284 | 50 | 0.482 | 115 s | une seule jambe | +35.79 $ | +985.17 $ |
| 68 | 09.10 18:57:27 | Up | 0.366 | 100 | 0.566 | 153 s | une seule jambe | −36.64 $ | +948.53 $ |
| 69 | 09.10 19:08:32 | Up | 0.253 | 208 | 0.505 | 87 s | une seule jambe | −52.74 $ | +895.79 $ |
| 70 | 09.10 19:10:45 | Up | 0.340 | 156 | 0.546 | 255 s | une seule jambe | −53.15 $ | +842.64 $ |
| 71 | 09.10 19:16:54 | Up | 0.462 | 114 | 0.645 | 186 s | une seule jambe | +61.10 $ | +903.74 $ |
| 72 | 09.10 19:20:49 | Up | 0.488 | 10 | 0.677 | 250 s | une seule jambe | −4.88 $ | +898.86 $ |
| 73 | 09.10 19:33:28 | Up | 0.152 | 141 | 0.359 | 91 s | une seule jambe | −21.52 $ | +877.34 $ |
| 74 | 09.10 19:38:53 | Down | 0.178 | 312 | 0.369 | 66 s | une seule jambe | −55.73 $ | +821.61 $ |
| 75 | 09.10 19:41:00 | Down | 0.478 | 109 | 0.661 | 240 s | une seule jambe | −51.94 $ | +769.67 $ |
| 76 | 09.10 19:46:51 | Up | 0.247 | 35 | 0.535 | 189 s | une seule jambe | −8.65 $ | +761.02 $ |
| 77 | 09.10 20:13:41 | Up | 0.292 | 185 | 0.512 | 78 s | une seule jambe | −54.13 $ | +706.89 $ |
| 78 | 09.10 20:17:05 | Up | 0.287 | 185 | 0.484 | 174 s | une seule jambe | −53.17 $ | +653.72 $ |
| 79 | 09.10 20:32:38 | Up | 0.191 | 6 | 0.382 | 141 s | une seule jambe | −1.14 $ | +652.58 $ |
---PAGE---
## 3. corrige : desaccord 20

**Règle :** Désaccord 20 : achat 50 $ dès que modèle − meilleur vendeur ≥ 0,20 (≥ 5 s restantes, un achat par cycle, gardé jusqu'au résultat), avec le modèle corrigé (0,015 %).

- Trades : **86** (84 dont j'ai le détail), 32 gagnés (37 %), résultat **+242 $**, creux max −965 $, pertes de suite max 10.
- Gain moyen d'un gagnant +79 $, perte moyenne d'un perdant −42 $, mise moyenne réellement remplie 40 $. Sans les 3 meilleurs trades : −612 $.
- **Original (desaccord 20) sur la même période :** 104 trades, 23 gagnés (22 %), −286 $, creux −1'067 $, pertes de suite max 15.

### Mêmes cycles que l'original

| | Cycles | Résultat de ce fantôme | Résultat de l'original |
|---|---|---|---|
| achetés par les deux | 76 | +504 $ | +750 $ |
| seulement ce fantôme | 6 | −47 $ | — |
| seulement l'original (évités) | 28 | — | −1'036 $ |
| ↳ sur les cycles communs : même côté | 69 / 76 | prix moyen 0.33 | prix moyen 0.24 |

### Par prix d'achat

| Groupe | Trades | Gagnés | % | Résultat |
|---|---|---|---|---|
| < 0,10 $ | 2 | 0 | 0 % | −89 $ |
| 0,10-0,20 $ | 14 | 4 | 29 % | +667 $ |
| 0,20-0,35 $ | 33 | 10 | 30 % | −293 $ |
| ≥ 0,35 $ | 35 | 18 | 51 % | +67 $ |

### Par temps restant à l'achat

| Groupe | Trades | Gagnés | % | Résultat |
|---|---|---|---|---|
| < 60 s | 4 | 1 | 25 % | −60 $ |
| 60-120 s | 24 | 9 | 38 % | −170 $ |
| 120-200 s | 23 | 11 | 48 % | +753 $ |
| ≥ 200 s | 33 | 11 | 33 % | −172 $ |

### Par heure (suisse)

| Groupe | Trades | Gagnés | % | Résultat |
|---|---|---|---|---|
| 09h | 9 | 6 | 67 % | +284 $ |
| 10h | 11 | 6 | 55 % | +151 $ |
| 11h | 8 | 5 | 62 % | +142 $ |
| 12h | 8 | 3 | 38 % | +508 $ |
| 13h | 7 | 2 | 29 % | −71 $ |
| 14h | 6 | 0 | 0 % | −212 $ |
| 15h | 4 | 3 | 75 % | +154 $ |
| 16h | 5 | 2 | 40 % | −50 $ |
| 17h | 9 | 1 | 11 % | −224 $ |
| 18h | 5 | 2 | 40 % | −69 $ |
| 19h | 9 | 2 | 22 % | −155 $ |
| 20h | 3 | 0 | 0 % | −107 $ |

### Tous les trades

| # | Heure (CH) | Côté | Prix | Jetons | Modèle | Reste | Issue | Résultat | Cumul |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 09.10 09:07:32 | Down | 0.284 | 46 | 0.47 | 148 s | une seule jambe | +32.68 $ | +32.68 $ |
| 2 | 09.10 09:10:38 | Down | 0.195 | 278 | 0.417 | 262 s | une seule jambe | +223.63 $ | +256.31 $ |
| 3 | 09.10 09:15:48 | Down | 0.320 | 167 | 0.563 | 251 s | une seule jambe | −53.36 $ | +202.95 $ |
| 4 | 09.10 09:21:44 | Up | 0.518 | 94 | 0.711 | 195 s | une seule jambe | +45.37 $ | +248.32 $ |
| 5 | 09.10 09:25:51 | Down | 0.389 | 123 | 0.604 | 249 s | une seule jambe | +75.34 $ | +323.66 $ |
| 6 | 09.10 09:33:38 | Up | 0.802 | 17 | 0.998 | 82 s | une seule jambe | +3.28 $ | +326.94 $ |
| 7 | 09.10 09:48:27 | Up | 0.189 | 93 | 0.37 | 92 s | une seule jambe | −17.50 $ | +309.44 $ |
| 8 | 09.10 09:50:52 | Up | 0.294 | 39 | 0.487 | 247 s | une seule jambe | +27.51 $ | +336.95 $ |
| 9 | 09.10 09:55:15 | Down | 0.253 | 208 | 0.506 | 285 s | une seule jambe | −52.74 $ | +284.21 $ |
| 10 | 09.10 10:02:28 | Down | 0.387 | 90 | 0.578 | 152 s | une seule jambe | +55.19 $ | +339.40 $ |
| 11 | 09.10 10:08:28 | Up | 0.714 | 72 | 0.896 | 92 s | une seule jambe | +20.69 $ | +360.09 $ |
| 12 | 09.10 10:12:50 | Up | 0.394 | 135 | 0.571 | 129 s | une seule jambe | +81.90 $ | +441.99 $ |
| 13 | 09.10 10:19:06 | Up | 0.315 | 10 | 0.532 | 53 s | une seule jambe | −3.15 $ | +438.84 $ |
| 14 | 09.10 10:22:40 | Up | 0.405 | 26 | 0.58 | 140 s | une seule jambe | −10.53 $ | +428.31 $ |
| 15 | 09.10 10:29:00 | Up | 0.617 | 83 | 0.968 | 59 s | une seule jambe | +31.89 $ | +460.20 $ |
| 16 | 09.10 10:31:11 | Down | 0.632 | 20 | 0.812 | 228 s | une seule jambe | +7.36 $ | +467.56 $ |
| 17 | 09.10 10:36:17 | Down | 0.397 | 132 | 0.614 | 222 s | une seule jambe | −52.23 $ | +415.33 $ |
| 18 | 09.10 10:42:15 | Down | 0.452 | 116 | 0.721 | 164 s | une seule jambe | −52.55 $ | +362.78 $ |
| 19 | 09.10 10:46:05 | Up | 0.302 | 179 | 0.48 | 235 s | une seule jambe | +124.65 $ | +487.43 $ |
| 20 | 09.10 10:50:46 | Down | 0.366 | 143 | 0.572 | 254 s | une seule jambe | −52.34 $ | +435.09 $ |
| 21 | 09.10 11:05:58 | Up | 0.294 | 179 | 0.486 | 241 s | une seule jambe | −52.59 $ | +382.50 $ |
| 22 | 09.10 11:17:46 | Up | 0.264 | 30 | 0.495 | 133 s | une seule jambe | +22.09 $ | +404.59 $ |
| 23 | 09.10 11:20:10 | Up | 0.315 | 167 | 0.507 | 289 s | une seule jambe | +114.15 $ | +518.74 $ |
| 24 | 09.10 11:25:47 | Up | 0.273 | 200 | 0.453 | 253 s | une seule jambe | −54.56 $ | +464.18 $ |
| 25 | 09.10 11:36:01 | Down | 0.284 | 91 | 0.53 | 239 s | une seule jambe | +64.85 $ | +529.03 $ |
| 26 | 09.10 11:41:30 | Down | 0.223 | 40 | 0.451 | 210 s | une seule jambe | +31.07 $ | +560.10 $ |
| 27 | 09.10 11:50:39 | Down | 0.356 | 147 | 0.557 | 261 s | une seule jambe | −52.38 $ | +507.72 $ |
| 28 | 09.10 11:57:19 | Down | 0.434 | 122 | 0.614 | 161 s | une seule jambe | +69.00 $ | +576.72 $ |
| 29 | 09.10 12:01:50 | Up | 0.102 | 556 | 0.334 | 189 s | une seule jambe | +498.76 $ | +1'075.48 $ |
| 30 | 09.10 12:08:00 | Down | 0.180 | 294 | 0.384 | 119 s | une seule jambe | +241.13 $ | +1'316.61 $ |
| 31 | 09.10 12:10:15 | Down | 0.325 | 161 | 0.52 | 285 s | une seule jambe | −52.48 $ | +1'264.13 $ |
| 32 | 09.10 12:16:15 | Down | 0.676 | 76 | 0.917 | 225 s | une seule jambe | +24.53 $ | +1'288.66 $ |
| 33 | 09.10 12:22:41 | Up | 0.260 | 171 | 0.449 | 139 s | une seule jambe | −44.44 $ | +1'244.22 $ |
| 34 | 09.10 12:28:10 | Down | 0.304 | 179 | 0.485 | 109 s | une seule jambe | −54.35 $ | +1'189.87 $ |
| 35 | 09.10 12:35:15 | Up | 0.284 | 185 | 0.543 | 284 s | une seule jambe | −52.63 $ | +1'137.24 $ |
| 36 | 09.10 12:52:46 | Up | 0.264 | 200 | 0.548 | 134 s | une seule jambe | −52.70 $ | +1'084.54 $ |
| 37 | 09.10 13:08:18 | Down | 0.156 | 357 | 0.342 | 102 s | une seule jambe | −55.83 $ | +1'028.71 $ |
| 38 | 09.10 13:10:00 | Up | 0.395 | 135 | 0.575 | 300 s | une seule jambe | −53.34 $ | +975.37 $ |
| 39 | 09.10 13:16:12 | Down | 0.302 | 105 | 0.483 | 228 s | une seule jambe | −31.70 $ | +943.67 $ |
| 40 | 09.10 13:27:56 | Down | 0.568 | 91 | 0.769 | 124 s | une seule jambe | −51.62 $ | +892.05 $ |
| 41 | 09.10 13:35:52 | Up | 0.325 | 161 | 0.644 | 248 s | une seule jambe | +108.81 $ | +1'000.86 $ |
| 42 | 09.10 13:43:28 | Down | 0.586 | 89 | 0.761 | 92 s | une seule jambe | +36.98 $ | +1'037.84 $ |
| 43 | 09.10 13:59:46 | Up | 0.038 | 638 | 0.306 | 13 s | une seule jambe | −24.56 $ | +1'013.28 $ |
| 44 | 09.10 14:01:30 | Down | 0.292 | 185 | 0.479 | 209 s | une seule jambe | −54.04 $ | +959.24 $ |
| 45 | 09.10 14:10:19 | Up | 0.597 | 88 | 0.77 | 281 s | une seule jambe | −52.37 $ | +906.87 $ |
| 46 | 09.10 14:17:30 | Up | 0.211 | 5 | 0.416 | 149 s | une seule jambe | −1.06 $ | +905.81 $ |
| 47 | 09.10 14:27:31 | Up | 0.149 | 5 | 0.349 | 149 s | une seule jambe | −0.74 $ | +905.07 $ |
| 48 | 09.10 14:36:21 | Up | 0.294 | 170 | 0.474 | 219 s | une seule jambe | −50.02 $ | +855.05 $ |
| 49 | 09.10 14:48:44 | Down | 0.256 | 208 | 0.638 | 75 s | une seule jambe | −53.34 $ | +801.71 $ |
| 50 | 09.10 15:17:55 | Up | 0.381 | 75 | 0.593 | 125 s | une seule jambe | +46.45 $ | +848.16 $ |
| 51 | 09.10 15:20:24 | Down | 0.447 | 119 | 0.629 | 275 s | une seule jambe | +65.81 $ | +913.97 $ |
| 52 | 09.10 15:48:24 | Up | 0.356 | 147 | 0.558 | 96 s | une seule jambe | +94.68 $ | +1'008.65 $ |
| 53 | 09.10 15:58:36 | Up | 0.138 | 385 | 0.48 | 84 s | une seule jambe | −53.13 $ | +955.52 $ |
| 54 | 09.10 16:03:48 | Up | 0.441 | 97 | 0.625 | 72 s | une seule jambe | +54.45 $ | +1'009.97 $ |
| 55 | 09.10 16:13:10 | Up | 0.412 | 10 | 0.592 | 110 s | une seule jambe | +6.03 $ | +1'016.00 $ |
| 56 | 09.10 16:28:21 | Up | 0.294 | 179 | 0.485 | 98 s | une seule jambe | −52.59 $ | +963.41 $ |
| 57 | 09.10 16:33:44 | Down | 0.117 | 40 | 0.318 | 76 s | une seule jambe | −4.66 $ | +958.75 $ |
| 58 | 09.10 16:41:41 | Up | 0.497 | 106 | 0.67 | 198 s | une seule jambe | −52.93 $ | +905.82 $ |
| 59 | 09.10 17:01:31 | Up | 0.489 | 65 | 0.672 | 209 s | une seule jambe | −31.90 $ | +873.92 $ |
| 60 | 09.10 17:13:13 | Down | 0.158 | 357 | 0.345 | 107 s | une seule jambe | −56.43 $ | +817.49 $ |
| 61 | 09.10 17:21:39 | Up | 0.426 | 125 | 0.674 | 201 s | une seule jambe | −53.22 $ | +764.27 $ |
| 62 | 09.10 17:24:21 | Up | 0.052 | 1250 | 0.617 | 38 s | une seule jambe | −64.61 $ | +699.66 $ |
| 63 | 09.10 17:26:21 | Down | 0.472 | 111 | 0.654 | 219 s | une seule jambe | −52.49 $ | +647.17 $ |
| 64 | 09.10 17:28:57 | Down | 0.407 | 128 | 0.71 | 63 s | une seule jambe | −52.20 $ | +594.97 $ |
| 65 | 09.10 17:38:25 | Down | 0.222 | 238 | 0.541 | 95 s | une seule jambe | −52.84 $ | +542.13 $ |
| 66 | 09.10 17:51:41 | Down | 0.232 | 227 | 0.42 | 198 s | une seule jambe | +174.46 $ | +716.59 $ |
| 67 | 09.10 17:55:35 | Down | 0.155 | 223 | 0.345 | 264 s | une seule jambe | −34.61 $ | +681.98 $ |
| 68 | 09.10 18:05:00 | Down | 0.273 | 148 | 0.457 | 299 s | une seule jambe | −40.45 $ | +641.53 $ |
| 69 | 09.10 18:18:40 | Down | 0.128 | 5 | 0.338 | 80 s | une seule jambe | +4.36 $ | +645.89 $ |
| 70 | 09.10 18:43:39 | Up | 0.427 | 75 | 0.611 | 81 s | une seule jambe | −32.06 $ | +613.83 $ |
| 71 | 09.10 18:53:04 | Down | 0.284 | 50 | 0.482 | 115 s | une seule jambe | +35.79 $ | +649.62 $ |
| 72 | 09.10 18:57:27 | Up | 0.366 | 100 | 0.566 | 153 s | une seule jambe | −36.64 $ | +612.98 $ |
| 73 | 09.10 19:02:07 | Down | 0.458 | 60 | 0.642 | 172 s | une seule jambe | +32.54 $ | +645.52 $ |
| 74 | 09.10 19:08:32 | Up | 0.253 | 208 | 0.505 | 87 s | une seule jambe | −52.74 $ | +592.78 $ |
| 75 | 09.10 19:10:30 | Up | 0.341 | 156 | 0.537 | 269 s | une seule jambe | −53.23 $ | +539.55 $ |
| 76 | 09.10 19:16:54 | Up | 0.462 | 114 | 0.645 | 186 s | une seule jambe | +61.10 $ | +600.65 $ |
| 77 | 09.10 19:20:49 | Up | 0.488 | 10 | 0.677 | 250 s | une seule jambe | −4.88 $ | +595.77 $ |
| 78 | 09.10 19:33:28 | Up | 0.152 | 141 | 0.359 | 91 s | une seule jambe | −21.52 $ | +574.25 $ |
| 79 | 09.10 19:38:53 | Down | 0.178 | 312 | 0.369 | 66 s | une seule jambe | −55.73 $ | +518.52 $ |
| 80 | 09.10 19:41:00 | Down | 0.478 | 109 | 0.661 | 240 s | une seule jambe | −51.94 $ | +466.58 $ |
| 81 | 09.10 19:46:51 | Up | 0.247 | 35 | 0.535 | 189 s | une seule jambe | −8.65 $ | +457.93 $ |
| 82 | 09.10 20:13:38 | Up | 0.325 | 161 | 0.512 | 81 s | une seule jambe | −52.48 $ | +405.45 $ |
| 83 | 09.10 20:17:05 | Up | 0.287 | 185 | 0.484 | 174 s | une seule jambe | −53.17 $ | +352.28 $ |
| 84 | 09.10 20:32:38 | Up | 0.191 | 6 | 0.382 | 141 s | une seule jambe | −1.14 $ | +351.14 $ |
---PAGE---
## 4. corrige : zone + Binance et perp + sortie -10

**Règle :** Zone : écart ≥ 0,30, prix 0,15-0,35 $, plus de 60 s restantes, Binance et le perp Bybit ont bougé dans notre sens sur les 3 s d'avant ; revente si le modèle perd 10 pts depuis l'entrée (jamais sous max(0,05, meilleur acheteur − 0,02)) ; avec le modèle corrigé (0,015 %).

- Trades : **32** (31 dont j'ai le détail), 11 gagnés (34 %), résultat **+632 $**, creux max −125 $, pertes de suite max 5.
- Gain moyen d'un gagnant +107 $, perte moyenne d'un perdant −24 $, mise moyenne réellement remplie 42 $. Sans les 3 meilleurs trades : −15 $.
- **Original (desaccord 30 zone + Binance et perp + sortie modele -10) sur la même période :** 36 trades, 13 gagnés (36 %), +372 $, creux −335 $, pertes de suite max 7.

### Mêmes cycles que l'original

| | Cycles | Résultat de ce fantôme | Résultat de l'original |
|---|---|---|---|
| achetés par les deux | 28 | +768 $ | +518 $ |
| seulement ce fantôme | 3 | −82 $ | — |
| seulement l'original (évités) | 8 | — | −147 $ |
| ↳ sur les cycles communs : même côté | 28 / 28 | prix moyen 0.26 | prix moyen 0.22 |

### Par prix d'achat

| Groupe | Trades | Gagnés | % | Résultat |
|---|---|---|---|---|
| 0,10-0,20 $ | 7 | 4 | 57 % | +580 $ |
| 0,20-0,35 $ | 23 | 7 | 30 % | +149 $ |
| ≥ 0,35 $ | 1 | 0 | 0 % | −43 $ |

### Par temps restant à l'achat

| Groupe | Trades | Gagnés | % | Résultat |
|---|---|---|---|---|
| 60-120 s | 17 | 7 | 41 % | +512 $ |
| 120-200 s | 7 | 3 | 43 % | +142 $ |
| ≥ 200 s | 7 | 1 | 14 % | +32 $ |

### Par heure (suisse)

| Groupe | Trades | Gagnés | % | Résultat |
|---|---|---|---|---|
| 09h | 3 | 2 | 67 % | +405 $ |
| 10h | 6 | 1 | 17 % | −12 $ |
| 11h | 5 | 3 | 60 % | +308 $ |
| 12h | 5 | 1 | 20 % | −79 $ |
| 13h | 2 | 1 | 50 % | +108 $ |
| 14h | 3 | 1 | 33 % | −22 $ |
| 15h | 1 | 0 | 0 % | −18 $ |
| 17h | 3 | 1 | 33 % | +41 $ |
| 19h | 2 | 1 | 50 % | +0 $ |
| 20h | 1 | 0 | 0 % | −44 $ |

### Tous les trades

| # | Heure (CH) | Côté | Prix | Jetons | Modèle | Reste | Issue | Résultat | Cumul |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 09.10 09:13:49 | Down | 0.164 | 333 | 0.461 | 71 s | une seule jambe | +278.76 $ | +278.76 $ |
| 2 | 09.10 09:52:02 | Up | 0.273 | 200 | 0.55 | 177 s | une seule jambe | +145.47 $ | +424.23 $ |
| 3 | 09.10 09:55:28 | Down | 0.211 | 263 | 0.497 | 272 s | une seule jambe | −18.90 $ | +405.33 $ |
| 4 | 09.10 10:08:53 | Up | 0.346 | 152 | 0.962 | 66 s | une seule jambe | +99.10 $ | +504.43 $ |
| 5 | 09.10 10:13:46 | Up | 0.232 | 227 | 0.622 | 74 s | une seule jambe | −33.72 $ | +470.71 $ |
| 6 | 09.10 10:37:30 | Down | 0.282 | 192 | 0.566 | 149 s | une seule jambe | −10.41 $ | +460.30 $ |
| 7 | 09.10 10:43:30 | Down | 0.191 | 278 | 0.488 | 90 s | une seule jambe | −38.53 $ | +421.77 $ |
| 8 | 09.10 10:48:52 | Up | 0.330 | 62 | 0.65 | 68 s | une seule jambe | −2.76 $ | +419.01 $ |
| 9 | 09.10 10:52:12 | Down | 0.232 | 238 | 0.513 | 168 s | une seule jambe | −25.67 $ | +393.34 $ |
| 10 | 09.10 11:23:02 | Up | 0.161 | 96 | 0.665 | 117 s | une seule jambe | +80.82 $ | +474.16 $ |
| 11 | 09.10 11:27:58 | Up | 0.222 | 238 | 0.527 | 121 s | une seule jambe | −41.75 $ | +432.41 $ |
| 12 | 09.10 11:36:01 | Down | 0.284 | 185 | 0.601 | 239 s | une seule jambe | −10.24 $ | +422.17 $ |
| 13 | 09.10 11:43:25 | Down | 0.159 | 21 | 0.752 | 95 s | une seule jambe | +1.61 $ | +423.78 $ |
| 14 | 09.10 11:58:55 | Down | 0.168 | 333 | 0.455 | 64 s | une seule jambe | +277.24 $ | +701.02 $ |
| 15 | 09.10 12:08:01 | Down | 0.318 | 21 | 0.651 | 118 s | une seule jambe | +3.08 $ | +704.10 $ |
| 16 | 09.10 12:10:18 | Down | 0.334 | 120 | 0.618 | 282 s | une seule jambe | −5.85 $ | +698.25 $ |
| 17 | 09.10 12:28:25 | Down | 0.188 | 294 | 0.473 | 95 s | une seule jambe | −1.37 $ | +696.88 $ |
| 18 | 09.10 12:35:15 | Up | 0.284 | 185 | 0.57 | 284 s | une seule jambe | −20.52 $ | +676.36 $ |
| 19 | 09.10 12:52:46 | Up | 0.261 | 208 | 0.548 | 134 s | une seule jambe | −54.44 $ | +621.92 $ |
| 20 | 09.10 13:28:11 | Down | 0.336 | 22 | 0.714 | 109 s | une seule jambe | −1.12 $ | +620.80 $ |
| 21 | 09.10 13:35:52 | Up | 0.325 | 161 | 0.644 | 248 s | une seule jambe | +108.81 $ | +729.61 $ |
| 22 | 09.10 14:11:37 | Up | 0.293 | 185 | 0.571 | 202 s | une seule jambe | −18.68 $ | +710.93 $ |
| 23 | 09.10 14:38:12 | Up | 0.346 | 152 | 0.666 | 107 s | une seule jambe | −52.41 $ | +658.52 $ |
| 24 | 09.10 14:48:44 | Down | 0.256 | 208 | 0.638 | 75 s | une seule jambe | +48.64 $ | +707.16 $ |
| 25 | 09.10 15:58:36 | Up | 0.166 | 198 | 0.48 | 83 s | une seule jambe | −18.04 $ | +689.12 $ |
| 26 | 09.10 17:28:57 | Down | 0.361 | 120 | 0.71 | 63 s | une seule jambe | −43.35 $ | +645.77 $ |
| 27 | 09.10 17:38:25 | Down | 0.222 | 238 | 0.541 | 95 s | une seule jambe | −41.33 $ | +604.44 $ |
| 28 | 09.10 17:52:59 | Down | 0.294 | 179 | 0.603 | 121 s | une seule jambe | +125.98 $ | +730.42 $ |
| 29 | 09.10 19:11:31 | Up | 0.275 | 33 | 0.597 | 208 s | une seule jambe | −2.24 $ | +728.18 $ |
| 30 | 09.10 19:46:51 | Up | 0.247 | 35 | 0.535 | 189 s | une seule jambe | +2.68 $ | +730.86 $ |
| 31 | 09.10 20:13:55 | Up | 0.242 | 227 | 0.522 | 64 s | une seule jambe | −44.50 $ | +686.36 $ |
---PAGE---
## 5. V2-F + pas les deux baissent

**Règle :** V2-F (modèle actuel 0,08 %) en refusant les entrées « les deux baissent, Polymarket plus fort » sur 3 s.

- Trades : **117** (113 dont j'ai le détail), 24 gagnés (21 %), résultat **−291 $**, creux max −1'212 $, pertes de suite max 15.
- Gain moyen d'un gagnant +135 $, perte moyenne d'un perdant −40 $, mise moyenne réellement remplie 41 $. Sans les 3 meilleurs trades : −1'332 $.
- **Original (V2-F ecart qui grandit) sur la même période :** 113 trades, 23 gagnés (20 %), −529 $, creux −989 $, pertes de suite max 15.

### Mêmes cycles que l'original

| | Cycles | Résultat de ce fantôme | Résultat de l'original |
|---|---|---|---|
| achetés par les deux | 112 | −639 $ | −676 $ |
| seulement ce fantôme | 0 | +0 $ | — |
| seulement l'original (évités) | 0 | — | +0 $ |
| ↳ sur les cycles communs : même côté | 112 / 112 | prix moyen 0.20 | prix moyen 0.20 |

### Par prix d'achat

| Groupe | Trades | Gagnés | % | Résultat |
|---|---|---|---|---|
| < 0,10 $ | 23 | 2 | 9 % | −362 $ |
| 0,10-0,20 $ | 34 | 3 | 9 % | −497 $ |
| 0,20-0,35 $ | 50 | 13 | 26 % | +99 $ |
| ≥ 0,35 $ | 6 | 5 | 83 % | +269 $ |

### Par temps restant à l'achat

| Groupe | Trades | Gagnés | % | Résultat |
|---|---|---|---|---|
| < 60 s | 1 | 0 | 0 % | −33 $ |
| 60-120 s | 33 | 4 | 12 % | −804 $ |
| 120-200 s | 38 | 6 | 16 % | −454 $ |
| ≥ 200 s | 41 | 13 | 32 % | +800 $ |

### Par heure (suisse)

| Groupe | Trades | Gagnés | % | Résultat |
|---|---|---|---|---|
| 08h | 6 | 0 | 0 % | −318 $ |
| 09h | 12 | 4 | 33 % | +364 $ |
| 10h | 11 | 4 | 36 % | −7 $ |
| 11h | 12 | 4 | 33 % | +292 $ |
| 12h | 11 | 2 | 18 % | +24 $ |
| 13h | 10 | 2 | 20 % | −161 $ |
| 14h | 9 | 0 | 0 % | −333 $ |
| 15h | 4 | 1 | 25 % | −31 $ |
| 16h | 5 | 1 | 20 % | +31 $ |
| 17h | 7 | 1 | 14 % | +11 $ |
| 18h | 9 | 2 | 22 % | +144 $ |
| 19h | 11 | 2 | 18 % | −236 $ |
| 20h | 6 | 0 | 0 % | −271 $ |

### Tous les trades

| # | Heure (CH) | Côté | Prix | Jetons | Modèle | Reste | Issue | Résultat | Cumul |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 09.10 08:32:40 | Down | 0.106 | 500 | 0.328 | 140 s | une seule jambe | −53.24 $ | −53.24 $ |
| 2 | 09.10 08:37:53 | Down | 0.248 | 208 | 0.436 | 126 s | une seule jambe | −51.64 $ | −104.88 $ |
| 3 | 09.10 08:42:05 | Down | 0.191 | 278 | 0.381 | 174 s | une seule jambe | −52.95 $ | −157.83 $ |
| 4 | 09.10 08:45:29 | Down | 0.284 | 185 | 0.473 | 270 s | une seule jambe | −52.63 $ | −210.46 $ |
| 5 | 09.10 08:51:38 | Up | 0.172 | 312 | 0.376 | 202 s | une seule jambe | −53.89 $ | −264.35 $ |
| 6 | 09.10 08:58:04 | Down | 0.128 | 417 | 0.413 | 116 s | une seule jambe | −53.17 $ | −317.52 $ |
| 7 | 09.10 09:01:52 | Up | 0.084 | 433 | 0.282 | 188 s | une seule jambe | −36.51 $ | −354.03 $ |
| 8 | 09.10 09:07:24 | Down | 0.221 | 250 | 0.429 | 155 s | une seule jambe | +194.84 $ | −159.19 $ |
| 9 | 09.10 09:10:38 | Down | 0.191 | 278 | 0.407 | 262 s | une seule jambe | +224.83 $ | +65.64 $ |
| 10 | 09.10 09:15:34 | Down | 0.207 | 57 | 0.409 | 266 s | une seule jambe | −11.80 $ | +53.84 $ |
| 11 | 09.10 09:22:59 | Down | 0.067 | 353 | 0.267 | 121 s | une seule jambe | −23.76 $ | +30.08 $ |
| 12 | 09.10 09:25:51 | Down | 0.388 | 36 | 0.572 | 249 s | une seule jambe | +22.16 $ | +52.24 $ |
| 13 | 09.10 09:32:27 | Down | 0.201 | 278 | 0.38 | 152 s | une seule jambe | −55.75 $ | −3.51 $ |
| 14 | 09.10 09:37:33 | Up | 0.191 | 12 | 0.388 | 146 s | une seule jambe | −2.37 $ | −5.88 $ |
| 15 | 09.10 09:43:25 | Up | 0.201 | 13 | 0.42 | 95 s | une seule jambe | −2.61 $ | −8.49 $ |
| 16 | 09.10 09:48:08 | Up | 0.304 | 55 | 0.481 | 112 s | une seule jambe | −16.70 $ | −25.19 $ |
| 17 | 09.10 09:51:09 | Up | 0.294 | 179 | 0.494 | 231 s | une seule jambe | +125.98 $ | +100.79 $ |
| 18 | 09.10 09:55:25 | Down | 0.240 | 227 | 0.503 | 275 s | une seule jambe | −54.55 $ | +46.24 $ |
| 19 | 09.10 10:02:31 | Down | 0.305 | 172 | 0.495 | 148 s | une seule jambe | +119.86 $ | +166.10 $ |
| 20 | 09.10 10:08:38 | Up | 0.577 | 91 | 0.76 | 82 s | une seule jambe | +38.44 $ | +204.54 $ |
| 21 | 09.10 10:11:47 | Up | 0.243 | 40 | 0.438 | 192 s | une seule jambe | +30.29 $ | +234.83 $ |
| 22 | 09.10 10:16:42 | Up | 0.184 | 294 | 0.372 | 198 s | une seule jambe | −54.08 $ | +180.75 $ |
| 23 | 09.10 10:21:54 | Up | 0.264 | 200 | 0.456 | 185 s | une seule jambe | −52.70 $ | +128.05 $ |
| 24 | 09.10 10:28:43 | Down | 0.117 | 455 | 0.316 | 76 s | une seule jambe | −53.20 $ | +74.85 $ |
| 25 | 09.10 10:33:28 | Up | 0.062 | 184 | 0.275 | 91 s | une seule jambe | −11.40 $ | +63.45 $ |
| 26 | 09.10 10:36:17 | Down | 0.297 | 145 | 0.499 | 222 s | une seule jambe | −43.09 $ | +20.36 $ |
| 27 | 09.10 10:42:33 | Down | 0.106 | 500 | 0.405 | 146 s | une seule jambe | −53.24 $ | −32.88 $ |
| 28 | 09.10 10:46:05 | Up | 0.302 | 179 | 0.488 | 235 s | une seule jambe | +124.65 $ | +91.77 $ |
| 29 | 09.10 10:50:50 | Down | 0.336 | 156 | 0.534 | 249 s | une seule jambe | −52.45 $ | +39.32 $ |
| 30 | 09.10 11:00:04 | Up | 0.232 | 238 | 0.412 | 295 s | une seule jambe | −55.27 $ | −15.95 $ |
| 31 | 09.10 11:05:57 | Up | 0.309 | 172 | 0.494 | 242 s | une seule jambe | −53.30 $ | −69.25 $ |
| 32 | 09.10 11:12:47 | Down | 0.170 | 312 | 0.386 | 132 s | une seule jambe | −53.02 $ | −122.27 $ |
| 33 | 09.10 11:16:20 | Up | 0.251 | 217 | 0.431 | 220 s | une seule jambe | +162.88 $ | +40.61 $ |
| 34 | 09.10 11:20:10 | Up | 0.315 | 167 | 0.502 | 289 s | une seule jambe | +114.15 $ | +154.76 $ |
| 35 | 09.10 11:25:08 | Up | 0.243 | 217 | 0.433 | 292 s | une seule jambe | −52.77 $ | +101.99 $ |
| 36 | 09.10 11:32:27 | Up | 0.128 | 417 | 0.356 | 152 s | une seule jambe | −53.17 $ | +48.82 $ |
| 37 | 09.10 11:36:20 | Down | 0.304 | 179 | 0.545 | 219 s | une seule jambe | +124.34 $ | +173.16 $ |
| 38 | 09.10 11:41:36 | Down | 0.159 | 333 | 0.453 | 203 s | une seule jambe | +280.27 $ | +453.43 $ |
| 39 | 09.10 11:45:04 | Down | 0.294 | 179 | 0.482 | 295 s | une seule jambe | −52.59 $ | +400.84 $ |
| 40 | 09.10 11:51:22 | Down | 0.306 | 172 | 0.506 | 218 s | une seule jambe | −52.70 $ | +348.14 $ |
| 41 | 09.10 11:57:42 | Up | 0.301 | 55 | 0.495 | 137 s | une seule jambe | −16.56 $ | +331.58 $ |
| 42 | 09.10 12:01:02 | Up | 0.222 | 238 | 0.432 | 238 s | une seule jambe | +185.25 $ | +516.83 $ |
| 43 | 09.10 12:06:17 | Down | 0.264 | 200 | 0.472 | 222 s | une seule jambe | +147.30 $ | +664.13 $ |
| 44 | 09.10 12:08:35 | Up | 0.085 | 625 | 0.366 | 85 s | une seule jambe | −53.31 $ | +610.82 $ |
| 45 | 09.10 12:10:18 | Down | 0.332 | 26 | 0.567 | 282 s | une seule jambe | −8.62 $ | +602.20 $ |
| 46 | 09.10 12:17:50 | Up | 0.137 | 417 | 0.322 | 130 s | une seule jambe | −57.10 $ | +545.10 $ |
| 47 | 09.10 12:21:22 | Up | 0.253 | 60 | 0.448 | 217 s | une seule jambe | −15.19 $ | +529.91 $ |
| 48 | 09.10 12:26:18 | Down | 0.180 | 294 | 0.385 | 221 s | une seule jambe | −52.99 $ | +476.92 $ |
| 49 | 09.10 12:32:18 | Up | 0.229 | 238 | 0.42 | 162 s | une seule jambe | −54.44 $ | +422.48 $ |
| 50 | 09.10 12:35:18 | Up | 0.261 | 208 | 0.529 | 281 s | une seule jambe | −54.41 $ | +368.07 $ |
| 51 | 09.10 12:42:47 | Up | 0.106 | 42 | 0.302 | 132 s | une seule jambe | −4.42 $ | +363.65 $ |
| 52 | 09.10 12:52:53 | Up | 0.253 | 30 | 0.534 | 127 s | une seule jambe | −7.59 $ | +356.06 $ |
| 53 | 09.10 13:02:40 | Up | 0.191 | 278 | 0.394 | 139 s | une seule jambe | −52.95 $ | +303.11 $ |
| 54 | 09.10 13:06:49 | Down | 0.207 | 263 | 0.393 | 190 s | une seule jambe | −54.47 $ | +248.64 $ |
| 55 | 09.10 13:10:03 | Up | 0.330 | 161 | 0.53 | 297 s | une seule jambe | −53.30 $ | +195.34 $ |
| 56 | 09.10 13:17:03 | Down | 0.074 | 300 | 0.263 | 177 s | une seule jambe | −22.35 $ | +172.99 $ |
| 57 | 09.10 13:23:17 | Up | 0.112 | 333 | 0.302 | 102 s | une seule jambe | −37.34 $ | +135.65 $ |
| 58 | 09.10 13:28:20 | Down | 0.346 | 156 | 0.548 | 99 s | une seule jambe | −54.00 $ | +81.65 $ |
| 59 | 09.10 13:35:52 | Up | 0.325 | 161 | 0.632 | 248 s | une seule jambe | +108.81 $ | +190.46 $ |
| 60 | 09.10 13:43:36 | Down | 0.397 | 60 | 0.608 | 83 s | une seule jambe | +36.18 $ | +226.64 $ |
| 61 | 09.10 13:53:33 | Up | 0.041 | 188 | 0.286 | 87 s | une seule jambe | −7.64 $ | +219.00 $ |
| 62 | 09.10 13:58:38 | Up | 0.124 | 195 | 0.316 | 81 s | une seule jambe | −24.25 $ | +194.75 $ |
| 63 | 09.10 14:01:30 | Down | 0.301 | 148 | 0.482 | 209 s | une seule jambe | −44.50 $ | +150.25 $ |
| 64 | 09.10 14:10:50 | Up | 0.478 | 25 | 0.666 | 250 s | une seule jambe | −11.95 $ | +138.30 $ |
| 65 | 09.10 14:17:30 | Up | 0.207 | 263 | 0.403 | 150 s | une seule jambe | −54.47 $ | +83.83 $ |
| 66 | 09.10 14:28:05 | Up | 0.046 | 156 | 0.254 | 114 s | une seule jambe | −7.18 $ | +76.65 $ |
| 67 | 09.10 14:36:21 | Up | 0.284 | 185 | 0.473 | 218 s | une seule jambe | −52.63 $ | +24.02 $ |
| 68 | 09.10 14:40:43 | Up | 0.201 | 263 | 0.392 | 257 s | une seule jambe | −52.92 $ | −28.90 $ |
| 69 | 09.10 14:48:17 | Down | 0.039 | 318 | 0.23 | 102 s | une seule jambe | −12.29 $ | −41.19 $ |
| 70 | 09.10 14:51:48 | Up | 0.117 | 455 | 0.319 | 192 s | une seule jambe | −53.20 $ | −94.39 $ |
| 71 | 09.10 14:58:22 | Down | 0.108 | 409 | 0.305 | 98 s | une seule jambe | −44.35 $ | −138.74 $ |
| 72 | 09.10 15:02:43 | Down | 0.102 | 33 | 0.301 | 136 s | une seule jambe | −3.35 $ | −142.09 $ |
| 73 | 09.10 15:13:15 | Up | 0.041 | 1667 | 0.264 | 104 s | une seule jambe | −69.06 $ | −211.15 $ |
| 74 | 09.10 15:48:24 | Up | 0.356 | 147 | 0.54 | 95 s | une seule jambe | +94.68 $ | −116.47 $ |
| 75 | 09.10 15:58:42 | Up | 0.085 | 625 | 0.412 | 78 s | une seule jambe | −53.31 $ | −169.78 $ |
| 76 | 09.10 16:03:58 | Down | 0.106 | 500 | 0.316 | 61 s | une seule jambe | −53.24 $ | −223.02 $ |
| 77 | 09.10 16:13:32 | Up | 0.294 | 179 | 0.501 | 88 s | une seule jambe | +125.98 $ | −97.04 $ |
| 78 | 09.10 16:27:04 | Up | 0.195 | 118 | 0.39 | 176 s | une seule jambe | −23.02 $ | −120.06 $ |
| 79 | 09.10 16:33:20 | Down | 0.138 | 5 | 0.333 | 99 s | une seule jambe | −0.69 $ | −120.75 $ |
| 80 | 09.10 16:53:19 | Down | 0.047 | 395 | 0.246 | 100 s | une seule jambe | −18.44 $ | −139.19 $ |
| 81 | 09.10 17:12:13 | Down | 0.117 | 455 | 0.311 | 166 s | une seule jambe | −53.20 $ | −192.39 $ |
| 82 | 09.10 17:21:10 | Up | 0.222 | 85 | 0.404 | 229 s | une seule jambe | −18.92 $ | −211.31 $ |
| 83 | 09.10 17:29:02 | Down | 0.081 | 414 | 0.573 | 58 s | une seule jambe | −33.38 $ | −244.69 $ |
| 84 | 09.10 17:38:46 | Down | 0.032 | 1667 | 0.366 | 74 s | une seule jambe | −53.49 $ | −298.18 $ |
| 85 | 09.10 17:43:22 | Up | 0.070 | 806 | 0.27 | 98 s | une seule jambe | −56.88 $ | −355.06 $ |
| 86 | 09.10 17:51:21 | Down | 0.159 | 333 | 0.363 | 218 s | une seule jambe | +280.27 $ | −74.79 $ |
| 87 | 09.10 17:55:45 | Down | 0.106 | 500 | 0.332 | 255 s | une seule jambe | −53.24 $ | −128.03 $ |
| 88 | 09.10 18:05:04 | Down | 0.232 | 227 | 0.46 | 296 s | une seule jambe | −52.81 $ | −180.84 $ |
| 89 | 09.10 18:13:29 | Down | 0.038 | 580 | 0.237 | 91 s | une seule jambe | −22.30 $ | −203.14 $ |
| 90 | 09.10 18:17:25 | Down | 0.046 | 294 | 0.241 | 154 s | une seule jambe | +280.42 $ | +77.28 $ |
| 91 | 09.10 18:21:07 | Up | 0.199 | 78 | 0.385 | 232 s | une seule jambe | −15.60 $ | +61.68 $ |
| 92 | 09.10 18:33:27 | Down | 0.121 | 411 | 0.312 | 93 s | une seule jambe | −49.97 $ | +11.71 $ |
| 93 | 09.10 18:43:10 | Up | 0.220 | 206 | 0.41 | 110 s | une seule jambe | −45.32 $ | −33.61 $ |
| 94 | 09.10 18:47:41 | Down | 0.085 | 714 | 0.271 | 138 s | une seule jambe | −60.76 $ | −94.37 $ |
| 95 | 09.10 18:52:29 | Down | 0.091 | 126 | 0.297 | 151 s | une seule jambe | +114.12 $ | +19.75 $ |
| 96 | 09.10 18:57:48 | Up | 0.294 | 12 | 0.488 | 132 s | une seule jambe | −3.66 $ | +16.09 $ |
| 97 | 09.10 19:01:02 | Down | 0.206 | 107 | 0.397 | 238 s | une seule jambe | +84.58 $ | +100.67 $ |
| 98 | 09.10 19:07:03 | Up | 0.177 | 312 | 0.365 | 177 s | une seule jambe | −55.38 $ | +45.29 $ |
| 99 | 09.10 19:10:42 | Up | 0.322 | 136 | 0.509 | 257 s | une seule jambe | −43.79 $ | +1.50 $ |
| 100 | 09.10 19:16:43 | Up | 0.373 | 143 | 0.555 | 196 s | une seule jambe | +89.51 $ | +91.01 $ |
| 101 | 09.10 19:23:04 | Up | 0.037 | 1667 | 0.245 | 115 s | une seule jambe | −61.98 $ | +29.03 $ |
| 102 | 09.10 19:31:39 | Up | 0.092 | 260 | 0.28 | 200 s | une seule jambe | −24.03 $ | +5.00 $ |
| 103 | 09.10 19:38:09 | Down | 0.157 | 357 | 0.348 | 110 s | une seule jambe | −56.22 $ | −51.22 $ |
| 104 | 09.10 19:42:46 | Down | 0.106 | 500 | 0.312 | 133 s | une seule jambe | −53.24 $ | −104.46 $ |
| 105 | 09.10 19:46:42 | Up | 0.170 | 12 | 0.367 | 197 s | une seule jambe | −2.04 $ | −106.50 $ |
| 106 | 09.10 19:53:27 | Down | 0.049 | 1250 | 0.279 | 93 s | une seule jambe | −61.04 $ | −167.54 $ |
| 107 | 09.10 19:58:10 | Down | 0.243 | 217 | 0.438 | 109 s | une seule jambe | −52.77 $ | −220.31 $ |
| 108 | 09.10 20:01:39 | Up | 0.119 | 455 | 0.331 | 201 s | une seule jambe | −54.32 $ | −274.63 $ |
| 109 | 09.10 20:07:35 | Down | 0.066 | 833 | 0.266 | 145 s | une seule jambe | −54.87 $ | −329.50 $ |
| 110 | 09.10 20:13:41 | Up | 0.292 | 185 | 0.505 | 78 s | une seule jambe | −54.13 $ | −383.63 $ |
| 111 | 09.10 20:15:56 | Up | 0.240 | 172 | 0.428 | 243 s | une seule jambe | −41.40 $ | −425.03 $ |
| 112 | 09.10 20:26:50 | Up | 0.269 | 200 | 0.451 | 190 s | une seule jambe | −53.74 $ | −478.77 $ |
| 113 | 09.10 20:33:31 | Up | 0.060 | 208 | 0.352 | 89 s | une seule jambe | −12.59 $ | −491.36 $ |
---PAGE---
## 6. V2-F + plus de 120 s

**Règle :** V2-F (modèle actuel 0,08 %) seulement s'il reste au moins 120 s dans le cycle.

- Trades : **85** (81 dont j'ai le détail), 20 gagnés (24 %), résultat **+403 $**, creux max −685 $, pertes de suite max 12.
- Gain moyen d'un gagnant +131 $, perte moyenne d'un perdant −37 $, mise moyenne réellement remplie 37 $. Sans les 3 meilleurs trades : −584 $.
- **Original (V2-F ecart qui grandit) sur la même période :** 112 trades, 23 gagnés (21 %), −476 $, creux −989 $, pertes de suite max 15.

### Mêmes cycles que l'original

| | Cycles | Résultat de ce fantôme | Résultat de l'original |
|---|---|---|---|
| achetés par les deux | 81 | +202 $ | +52 $ |
| seulement ce fantôme | 0 | +0 $ | — |
| seulement l'original (évités) | 30 | — | −675 $ |
| ↳ sur les cycles communs : même côté | 80 / 81 | prix moyen 0.22 | prix moyen 0.22 |

### Par prix d'achat

| Groupe | Trades | Gagnés | % | Résultat |
|---|---|---|---|---|
| < 0,10 $ | 6 | 2 | 33 % | +218 $ |
| 0,10-0,20 $ | 25 | 3 | 12 % | −144 $ |
| 0,20-0,35 $ | 47 | 12 | 26 % | +25 $ |
| ≥ 0,35 $ | 3 | 2 | 67 % | +103 $ |

### Par temps restant à l'achat

| Groupe | Trades | Gagnés | % | Résultat |
|---|---|---|---|---|
| 120-200 s | 39 | 6 | 15 % | −455 $ |
| ≥ 200 s | 42 | 13 | 31 % | +657 $ |

### Par heure (suisse)

| Groupe | Trades | Gagnés | % | Résultat |
|---|---|---|---|---|
| 08h | 4 | 0 | 0 % | −211 $ |
| 09h | 10 | 4 | 40 % | +349 $ |
| 10h | 8 | 3 | 38 % | −29 $ |
| 11h | 12 | 4 | 33 % | +170 $ |
| 12h | 10 | 2 | 20 % | +78 $ |
| 13h | 5 | 1 | 20 % | −82 $ |
| 14h | 7 | 0 | 0 % | −268 $ |
| 15h | 1 | 0 | 0 % | −3 $ |
| 16h | 1 | 0 | 0 % | −23 $ |
| 17h | 4 | 1 | 25 % | +224 $ |
| 18h | 6 | 2 | 33 % | +262 $ |
| 19h | 8 | 2 | 25 % | −59 $ |
| 20h | 5 | 0 | 0 % | −205 $ |

### Tous les trades

| # | Heure (CH) | Côté | Prix | Jetons | Modèle | Reste | Issue | Résultat | Cumul |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 09.10 08:37:53 | Down | 0.248 | 208 | 0.436 | 126 s | une seule jambe | −51.64 $ | −51.64 $ |
| 2 | 09.10 08:42:05 | Down | 0.191 | 278 | 0.381 | 174 s | une seule jambe | −52.95 $ | −104.59 $ |
| 3 | 09.10 08:45:29 | Down | 0.284 | 185 | 0.473 | 270 s | une seule jambe | −52.63 $ | −157.22 $ |
| 4 | 09.10 08:51:38 | Up | 0.172 | 312 | 0.376 | 202 s | une seule jambe | −53.89 $ | −211.11 $ |
| 5 | 09.10 09:01:52 | Up | 0.084 | 433 | 0.282 | 188 s | une seule jambe | −36.51 $ | −247.62 $ |
| 6 | 09.10 09:07:24 | Down | 0.221 | 250 | 0.429 | 155 s | une seule jambe | +194.84 $ | −52.78 $ |
| 7 | 09.10 09:10:38 | Down | 0.191 | 278 | 0.407 | 262 s | une seule jambe | +224.83 $ | +172.05 $ |
| 8 | 09.10 09:15:34 | Down | 0.207 | 57 | 0.409 | 266 s | une seule jambe | −11.80 $ | +160.25 $ |
| 9 | 09.10 09:22:48 | Down | 0.127 | 455 | 0.311 | 131 s | une seule jambe | −57.63 $ | +102.62 $ |
| 10 | 09.10 09:25:51 | Down | 0.388 | 36 | 0.572 | 249 s | une seule jambe | +22.16 $ | +124.78 $ |
| 11 | 09.10 09:32:27 | Down | 0.201 | 278 | 0.38 | 152 s | une seule jambe | −55.75 $ | +69.03 $ |
| 12 | 09.10 09:37:33 | Up | 0.191 | 12 | 0.388 | 146 s | une seule jambe | −2.37 $ | +66.66 $ |
| 13 | 09.10 09:51:09 | Up | 0.294 | 179 | 0.494 | 231 s | une seule jambe | +125.98 $ | +192.64 $ |
| 14 | 09.10 09:55:25 | Down | 0.240 | 227 | 0.503 | 275 s | une seule jambe | −54.55 $ | +138.09 $ |
| 15 | 09.10 10:02:31 | Down | 0.312 | 30 | 0.495 | 149 s | une seule jambe | +20.65 $ | +158.74 $ |
| 16 | 09.10 10:11:47 | Up | 0.243 | 40 | 0.438 | 192 s | une seule jambe | +30.29 $ | +189.03 $ |
| 17 | 09.10 10:16:42 | Up | 0.184 | 294 | 0.372 | 198 s | une seule jambe | −54.08 $ | +134.95 $ |
| 18 | 09.10 10:21:47 | Up | 0.264 | 200 | 0.456 | 192 s | une seule jambe | −52.70 $ | +82.25 $ |
| 19 | 09.10 10:36:17 | Down | 0.297 | 145 | 0.499 | 222 s | une seule jambe | −43.09 $ | +39.16 $ |
| 20 | 09.10 10:42:30 | Down | 0.201 | 11 | 0.414 | 149 s | une seule jambe | −2.21 $ | +36.95 $ |
| 21 | 09.10 10:46:05 | Up | 0.302 | 179 | 0.488 | 235 s | une seule jambe | +124.65 $ | +161.60 $ |
| 22 | 09.10 10:50:50 | Down | 0.336 | 156 | 0.534 | 249 s | une seule jambe | −52.45 $ | +109.15 $ |
| 23 | 09.10 11:00:04 | Up | 0.232 | 238 | 0.412 | 295 s | une seule jambe | −55.27 $ | +53.88 $ |
| 24 | 09.10 11:05:57 | Up | 0.309 | 172 | 0.494 | 242 s | une seule jambe | −53.30 $ | +0.58 $ |
| 25 | 09.10 11:12:47 | Down | 0.191 | 24 | 0.388 | 133 s | une seule jambe | −4.53 $ | −3.95 $ |
| 26 | 09.10 11:16:20 | Up | 0.251 | 217 | 0.431 | 220 s | une seule jambe | +162.88 $ | +158.93 $ |
| 27 | 09.10 11:20:10 | Up | 0.315 | 167 | 0.502 | 289 s | une seule jambe | +114.15 $ | +273.08 $ |
| 28 | 09.10 11:25:07 | Up | 0.252 | 63 | 0.433 | 292 s | une seule jambe | −15.91 $ | +257.17 $ |
| 29 | 09.10 11:32:25 | Up | 0.128 | 417 | 0.353 | 154 s | une seule jambe | −53.17 $ | +204.00 $ |
| 30 | 09.10 11:36:20 | Down | 0.304 | 179 | 0.545 | 219 s | une seule jambe | +124.34 $ | +328.34 $ |
| 31 | 09.10 11:41:36 | Down | 0.170 | 74 | 0.453 | 203 s | une seule jambe | +61.44 $ | +389.78 $ |
| 32 | 09.10 11:45:04 | Down | 0.294 | 179 | 0.482 | 295 s | une seule jambe | −52.59 $ | +337.19 $ |
| 33 | 09.10 11:51:20 | Down | 0.323 | 167 | 0.506 | 220 s | une seule jambe | −53.82 $ | +283.37 $ |
| 34 | 09.10 11:57:40 | Up | 0.232 | 18 | 0.424 | 139 s | une seule jambe | −4.20 $ | +279.17 $ |
| 35 | 09.10 12:01:02 | Up | 0.222 | 238 | 0.432 | 238 s | une seule jambe | +185.25 $ | +464.42 $ |
| 36 | 09.10 12:06:17 | Down | 0.264 | 200 | 0.472 | 222 s | une seule jambe | +147.30 $ | +611.72 $ |
| 37 | 09.10 12:10:18 | Down | 0.332 | 26 | 0.567 | 282 s | une seule jambe | −8.62 $ | +603.10 $ |
| 38 | 09.10 12:17:50 | Up | 0.137 | 417 | 0.322 | 130 s | une seule jambe | −57.10 $ | +546.00 $ |
| 39 | 09.10 12:21:22 | Up | 0.253 | 60 | 0.448 | 217 s | une seule jambe | −15.19 $ | +530.81 $ |
| 40 | 09.10 12:26:18 | Down | 0.180 | 294 | 0.385 | 221 s | une seule jambe | −52.99 $ | +477.82 $ |
| 41 | 09.10 12:32:18 | Up | 0.229 | 238 | 0.42 | 162 s | une seule jambe | −54.44 $ | +423.38 $ |
| 42 | 09.10 12:35:18 | Up | 0.261 | 208 | 0.529 | 281 s | une seule jambe | −54.41 $ | +368.97 $ |
| 43 | 09.10 12:42:47 | Up | 0.106 | 42 | 0.302 | 132 s | une seule jambe | −4.42 $ | +364.55 $ |
| 44 | 09.10 12:52:53 | Up | 0.253 | 30 | 0.534 | 127 s | une seule jambe | −7.59 $ | +356.96 $ |
| 45 | 09.10 13:02:40 | Up | 0.201 | 263 | 0.394 | 140 s | une seule jambe | −52.92 $ | +304.04 $ |
| 46 | 09.10 13:06:48 | Down | 0.201 | 263 | 0.394 | 191 s | une seule jambe | −52.92 $ | +251.12 $ |
| 47 | 09.10 13:10:03 | Up | 0.330 | 161 | 0.53 | 297 s | une seule jambe | −53.30 $ | +197.82 $ |
| 48 | 09.10 13:16:12 | Down | 0.302 | 105 | 0.483 | 228 s | une seule jambe | −31.70 $ | +166.12 $ |
| 49 | 09.10 13:35:52 | Up | 0.325 | 161 | 0.632 | 248 s | une seule jambe | +108.81 $ | +274.93 $ |
| 50 | 09.10 14:01:30 | Down | 0.301 | 148 | 0.482 | 209 s | une seule jambe | −44.50 $ | +230.43 $ |
| 51 | 09.10 14:10:41 | Up | 0.468 | 19 | 0.671 | 258 s | une seule jambe | −9.11 $ | +221.32 $ |
| 52 | 09.10 14:17:30 | Up | 0.207 | 263 | 0.403 | 150 s | une seule jambe | −54.47 $ | +166.85 $ |
| 53 | 09.10 14:27:31 | Up | 0.149 | 5 | 0.352 | 149 s | une seule jambe | −0.74 $ | +166.11 $ |
| 54 | 09.10 14:36:21 | Up | 0.284 | 185 | 0.473 | 218 s | une seule jambe | −52.63 $ | +113.48 $ |
| 55 | 09.10 14:40:43 | Up | 0.201 | 263 | 0.392 | 257 s | une seule jambe | −52.92 $ | +60.56 $ |
| 56 | 09.10 14:51:48 | Up | 0.117 | 455 | 0.319 | 192 s | une seule jambe | −53.20 $ | +7.36 $ |
| 57 | 09.10 15:02:43 | Down | 0.102 | 33 | 0.301 | 136 s | une seule jambe | −3.35 $ | +4.01 $ |
| 58 | 09.10 16:27:04 | Up | 0.195 | 118 | 0.39 | 176 s | une seule jambe | −23.02 $ | −19.01 $ |
| 59 | 09.10 17:12:13 | Down | 0.117 | 455 | 0.311 | 166 s | une seule jambe | −53.20 $ | −72.21 $ |
| 60 | 09.10 17:20:55 | Up | 0.274 | 5 | 0.465 | 244 s | une seule jambe | −1.37 $ | −73.58 $ |
| 61 | 09.10 17:51:21 | Down | 0.159 | 333 | 0.363 | 218 s | une seule jambe | +280.27 $ | +206.69 $ |
| 62 | 09.10 17:55:35 | Down | 0.196 | 10 | 0.387 | 264 s | une seule jambe | −1.96 $ | +204.73 $ |
| 63 | 09.10 18:05:04 | Down | 0.232 | 227 | 0.46 | 296 s | une seule jambe | −52.81 $ | +151.92 $ |
| 64 | 09.10 18:17:25 | Down | 0.046 | 294 | 0.241 | 154 s | une seule jambe | +280.42 $ | +432.34 $ |
| 65 | 09.10 18:21:07 | Up | 0.199 | 78 | 0.385 | 232 s | une seule jambe | −15.60 $ | +416.74 $ |
| 66 | 09.10 18:47:41 | Down | 0.085 | 714 | 0.271 | 138 s | une seule jambe | −60.76 $ | +355.98 $ |
| 67 | 09.10 18:52:29 | Down | 0.091 | 126 | 0.297 | 151 s | une seule jambe | +114.12 $ | +470.10 $ |
| 68 | 09.10 18:57:48 | Up | 0.294 | 12 | 0.488 | 132 s | une seule jambe | −3.66 $ | +466.44 $ |
| 69 | 09.10 19:01:02 | Down | 0.206 | 107 | 0.397 | 238 s | une seule jambe | +84.58 $ | +551.02 $ |
| 70 | 09.10 19:07:03 | Up | 0.177 | 312 | 0.365 | 177 s | une seule jambe | −55.38 $ | +495.64 $ |
| 71 | 09.10 19:10:42 | Up | 0.322 | 136 | 0.509 | 257 s | une seule jambe | −43.79 $ | +451.85 $ |
| 72 | 09.10 19:16:43 | Up | 0.373 | 143 | 0.555 | 196 s | une seule jambe | +89.51 $ | +541.36 $ |
| 73 | 09.10 19:31:39 | Up | 0.092 | 260 | 0.28 | 200 s | une seule jambe | −24.03 $ | +517.33 $ |
| 74 | 09.10 19:42:46 | Down | 0.106 | 500 | 0.312 | 133 s | une seule jambe | −53.24 $ | +464.09 $ |
| 75 | 09.10 19:46:42 | Up | 0.170 | 12 | 0.367 | 197 s | une seule jambe | −2.04 $ | +462.05 $ |
| 76 | 09.10 19:57:50 | Down | 0.230 | 238 | 0.41 | 129 s | une seule jambe | −54.70 $ | +407.35 $ |
| 77 | 09.10 20:01:39 | Up | 0.119 | 455 | 0.331 | 201 s | une seule jambe | −54.32 $ | +353.03 $ |
| 78 | 09.10 20:07:35 | Down | 0.066 | 833 | 0.266 | 145 s | une seule jambe | −54.87 $ | +298.16 $ |
| 79 | 09.10 20:15:56 | Up | 0.240 | 172 | 0.428 | 243 s | une seule jambe | −41.40 $ | +256.76 $ |
| 80 | 09.10 20:26:50 | Up | 0.269 | 200 | 0.451 | 190 s | une seule jambe | −53.74 $ | +203.02 $ |
| 81 | 09.10 20:32:38 | Up | 0.191 | 6 | 0.392 | 141 s | une seule jambe | −1.14 $ | +201.88 $ |
---PAGE---
## 7. V2-F + pas les deux baissent + volatilite >= 2

**Règle :** V2-F + pas les deux baissent + volatilité BTC ≥ 2 $/s sur 60 s (écart-type des variations du perp toutes les 0,25 s × 2). **Supprimée à 18:00 (plus de 500 $ de pertes)** ; résultats jusqu'à sa suppression.

- Trades : **48** (48 dont j'ai le détail), 11 gagnés (23 %), résultat **−540 $**, creux max −852 $, pertes de suite max 13.
- Gain moyen d'un gagnant +88 $, perte moyenne d'un perdant −41 $, mise moyenne réellement remplie 39 $. Sans les 3 meilleurs trades : −1'105 $.
- **Original (V2-F ecart qui grandit) sur la même période :** 56 trades, 16 gagnés (29 %), +386 $, creux −496 $, pertes de suite max 15.

### Mêmes cycles que l'original

| | Cycles | Résultat de ce fantôme | Résultat de l'original |
|---|---|---|---|
| achetés par les deux | 47 | −481 $ | +260 $ |
| seulement ce fantôme | 1 | −60 $ | — |
| seulement l'original (évités) | 8 | — | −22 $ |
| ↳ sur les cycles communs : même côté | 45 / 47 | prix moyen 0.22 | prix moyen 0.24 |

### Par prix d'achat

| Groupe | Trades | Gagnés | % | Résultat |
|---|---|---|---|---|
| < 0,10 $ | 8 | 0 | 0 % | −302 $ |
| 0,10-0,20 $ | 14 | 1 | 7 % | −305 $ |
| 0,20-0,35 $ | 20 | 7 | 35 % | +108 $ |
| ≥ 0,35 $ | 6 | 3 | 50 % | −41 $ |

### Par temps restant à l'achat

| Groupe | Trades | Gagnés | % | Résultat |
|---|---|---|---|---|
| 60-120 s | 13 | 3 | 23 % | −323 $ |
| 120-200 s | 19 | 3 | 16 % | −468 $ |
| ≥ 200 s | 16 | 5 | 31 % | +251 $ |

### Par heure (suisse)

| Groupe | Trades | Gagnés | % | Résultat |
|---|---|---|---|---|
| 09h | 11 | 4 | 36 % | −31 $ |
| 10h | 8 | 2 | 25 % | −108 $ |
| 11h | 11 | 2 | 18 % | −127 $ |
| 12h | 8 | 1 | 12 % | −114 $ |
| 13h | 10 | 2 | 20 % | −161 $ |

### Tous les trades

| # | Heure (CH) | Côté | Prix | Jetons | Modèle | Reste | Issue | Résultat | Cumul |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 09.10 09:01:55 | Up | 0.096 | 625 | 0.285 | 185 s | une seule jambe | −59.67 $ | −59.67 $ |
| 2 | 09.10 09:07:44 | Down | 0.481 | 68 | 0.666 | 135 s | une seule jambe | +35.07 $ | −24.60 $ |
| 3 | 09.10 09:10:38 | Down | 0.195 | 278 | 0.447 | 262 s | une seule jambe | +223.63 $ | +199.03 $ |
| 4 | 09.10 09:15:34 | Down | 0.207 | 57 | 0.409 | 266 s | une seule jambe | −11.80 $ | +187.23 $ |
| 5 | 09.10 09:22:59 | Down | 0.067 | 353 | 0.267 | 121 s | une seule jambe | −23.76 $ | +163.47 $ |
| 6 | 09.10 09:25:51 | Down | 0.388 | 36 | 0.572 | 249 s | une seule jambe | +22.16 $ | +185.63 $ |
| 7 | 09.10 09:32:27 | Down | 0.201 | 278 | 0.38 | 152 s | une seule jambe | −55.75 $ | +129.88 $ |
| 8 | 09.10 09:37:39 | Up | 0.164 | 333 | 0.365 | 141 s | une seule jambe | −54.50 $ | +75.38 $ |
| 9 | 09.10 09:48:39 | Up | 0.057 | 1000 | 0.353 | 80 s | une seule jambe | −56.84 $ | +18.54 $ |
| 10 | 09.10 09:53:46 | Up | 0.264 | 5 | 0.588 | 73 s | une seule jambe | +3.68 $ | +22.22 $ |
| 11 | 09.10 09:55:31 | Down | 0.117 | 455 | 0.367 | 268 s | une seule jambe | −53.20 $ | −30.98 $ |
| 12 | 09.10 10:02:31 | Down | 0.305 | 172 | 0.495 | 148 s | une seule jambe | +119.86 $ | +88.88 $ |
| 13 | 09.10 10:11:47 | Up | 0.243 | 40 | 0.438 | 192 s | une seule jambe | +30.29 $ | +119.17 $ |
| 14 | 09.10 10:16:57 | Up | 0.228 | 77 | 0.415 | 182 s | une seule jambe | −17.58 $ | +101.59 $ |
| 15 | 09.10 10:21:54 | Up | 0.264 | 200 | 0.456 | 185 s | une seule jambe | −52.70 $ | +48.89 $ |
| 16 | 09.10 10:28:43 | Down | 0.117 | 455 | 0.316 | 76 s | une seule jambe | −53.20 $ | −4.31 $ |
| 17 | 09.10 10:36:37 | Down | 0.264 | 200 | 0.455 | 203 s | une seule jambe | −52.70 $ | −57.01 $ |
| 18 | 09.10 10:42:33 | Down | 0.106 | 500 | 0.405 | 146 s | une seule jambe | −53.24 $ | −110.25 $ |
| 19 | 09.10 10:51:02 | Down | 0.435 | 65 | 0.618 | 238 s | une seule jambe | −28.29 $ | −138.54 $ |
| 20 | 09.10 11:00:20 | Up | 0.197 | 91 | 0.393 | 280 s | une seule jambe | −17.93 $ | −156.47 $ |
| 21 | 09.10 11:06:18 | Up | 0.203 | 60 | 0.417 | 221 s | une seule jambe | −12.11 $ | −168.58 $ |
| 22 | 09.10 11:12:47 | Down | 0.170 | 312 | 0.386 | 132 s | une seule jambe | −53.02 $ | −221.60 $ |
| 23 | 09.10 11:18:01 | Down | 0.122 | 120 | 0.378 | 119 s | une seule jambe | −14.68 $ | −236.28 $ |
| 24 | 09.10 11:20:26 | Up | 0.253 | 208 | 0.444 | 274 s | une seule jambe | +155.60 $ | −80.68 $ |
| 25 | 09.10 11:25:08 | Up | 0.243 | 217 | 0.433 | 292 s | une seule jambe | −52.77 $ | −133.45 $ |
| 26 | 09.10 11:32:27 | Up | 0.128 | 417 | 0.356 | 152 s | une seule jambe | −53.17 $ | −186.62 $ |
| 27 | 09.10 11:38:45 | Up | 0.065 | 833 | 0.283 | 74 s | une seule jambe | −54.07 $ | −240.69 $ |
| 28 | 09.10 11:43:28 | Down | 0.320 | 65 | 0.602 | 91 s | une seule jambe | +44.21 $ | −196.48 $ |
| 29 | 09.10 11:45:04 | Down | 0.294 | 179 | 0.482 | 295 s | une seule jambe | −52.59 $ | −249.07 $ |
| 30 | 09.10 11:57:42 | Up | 0.301 | 55 | 0.487 | 137 s | une seule jambe | −16.56 $ | −265.63 $ |
| 31 | 09.10 12:01:02 | Up | 0.222 | 238 | 0.432 | 238 s | une seule jambe | +185.25 $ | −80.38 $ |
| 32 | 09.10 12:08:35 | Up | 0.085 | 625 | 0.366 | 85 s | une seule jambe | −53.31 $ | −133.69 $ |
| 33 | 09.10 12:10:30 | Down | 0.396 | 135 | 0.574 | 270 s | une seule jambe | −53.54 $ | −187.23 $ |
| 34 | 09.10 12:26:56 | Down | 0.063 | 391 | 0.265 | 183 s | une seule jambe | −24.73 $ | −211.96 $ |
| 35 | 09.10 12:32:18 | Up | 0.229 | 238 | 0.42 | 162 s | une seule jambe | −54.44 $ | −266.40 $ |
| 36 | 09.10 12:35:52 | Up | 0.159 | 357 | 0.497 | 247 s | une seule jambe | −56.80 $ | −323.20 $ |
| 37 | 09.10 12:42:47 | Up | 0.106 | 42 | 0.302 | 132 s | une seule jambe | −4.42 $ | −327.62 $ |
| 38 | 09.10 12:53:03 | Up | 0.438 | 119 | 0.621 | 117 s | une seule jambe | −52.09 $ | −379.71 $ |
| 39 | 09.10 13:02:40 | Up | 0.191 | 278 | 0.394 | 139 s | une seule jambe | −52.95 $ | −432.66 $ |
| 40 | 09.10 13:06:49 | Down | 0.207 | 263 | 0.393 | 190 s | une seule jambe | −54.47 $ | −487.13 $ |
| 41 | 09.10 13:10:05 | Up | 0.315 | 167 | 0.516 | 294 s | une seule jambe | −52.52 $ | −539.65 $ |
| 42 | 09.10 13:17:03 | Down | 0.074 | 300 | 0.263 | 177 s | une seule jambe | −22.35 $ | −562.00 $ |
| 43 | 09.10 13:23:17 | Up | 0.112 | 333 | 0.302 | 102 s | une seule jambe | −37.34 $ | −599.34 $ |
| 44 | 09.10 13:28:20 | Down | 0.346 | 156 | 0.548 | 99 s | une seule jambe | −54.00 $ | −653.34 $ |
| 45 | 09.10 13:35:52 | Up | 0.325 | 161 | 0.632 | 248 s | une seule jambe | +108.81 $ | −544.53 $ |
| 46 | 09.10 13:43:36 | Down | 0.397 | 60 | 0.608 | 83 s | une seule jambe | +36.18 $ | −508.35 $ |
| 47 | 09.10 13:53:33 | Up | 0.041 | 188 | 0.286 | 87 s | une seule jambe | −7.64 $ | −515.99 $ |
| 48 | 09.10 13:58:38 | Up | 0.124 | 195 | 0.316 | 81 s | une seule jambe | −24.25 $ | −540.24 $ |
---PAGE---