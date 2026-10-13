# Bot95 — H1076 : chaque stratégie, filtres ajoutés un par un (sélection sur l'apprentissage)

Demande de Pitch (14.10.2026 00:06). 7 442 trades BTC (11.10 08:05 → 12.10 24:00) ; 18 filtres trouvés le 13.10. À chaque étape on ajoute le filtre qui
augmente le plus le P&L de l'APPRENTISSAGE (au moins 10 trades gardés) ; validation et test sont seulement regardés. Arrêt quand plus rien n'améliore
l'apprentissage, ou à 10 filtres. Aucun ordre ; exploration (les filtres eux-mêmes ont été trouvés en regardant les 3 périodes).


## Conclusion (14.10.2026)

- 40 stratégies BTC ont pu être filtrées ; la sélection s'arrête d'elle-même entre 1 et 5 filtres (jamais 10 : au-delà, plus rien n'améliore l'apprentissage).
- Apprentissage : +6 433 $ → +34 486 $ (normal : les filtres sont choisis là-dessus).
- **Validation : +12 101 $ → +8 115 $ ; test : +6 433 $ → +5 590 $.** Empiler des filtres choisis stratégie par stratégie ne tient pas hors apprentissage :
  25 stratégies sur 40 font mieux sur le test, 19 sur la validation, mais la somme baisse. C'est du sur-ajustement (trop de choix pour trop peu de trades par stratégie).
- Toutes les stratégies ensemble (filtres choisis une seule fois pour tout le monde) : « contre la foule » puis « pas de saut Bybit contre ».
  ROI apprentissage +5 % → +25 %, validation +114 % → +259 %, test +11 % → +18 %, avec moitié moins de trades ; P&L du test 7 422 $ → 6 772 $.
- Filtres choisis le plus souvent : pas de saut Bybit contre nous (28 fois), pas de fenêtre :00/:30 (16), contre la foule (14), reste > 120 s (10), marché calme (10), écart ≤ 1 c (9).
- Leçon : peu de filtres simples, les mêmes pour toutes les stratégies, plutôt qu'une recette par stratégie.

## TOUTES LES STRATÉGIES ENSEMBLE

## Résumé (P&L en $)

| stratégie                                                                                        |   filtres |   A base |   A filtré |   V base |   V filtré |   T base |   T filtré | dernier filtre                       |
|:-------------------------------------------------------------------------------------------------|----------:|---------:|-----------:|---------:|-----------:|---------:|-----------:|:-------------------------------------|
| TOUTES LES STRATÉGIES ENSEMBLE                                                                   |         2 |     7026 |      16172 |    12073 |      14815 |     7422 |       6772 | + pas de saut Bybit contre (10 s)    |
| desaccord 20 60-180 s BTC                                                                        |         2 |      675 |       1451 |      -47 |       -190 |      -63 |        369 | + pas de saut Bybit contre (10 s)    |
| V2-C perp BTC                                                                                    |         3 |     -156 |       1187 |      908 |        780 |      862 |       1752 | + pas de saut Bybit contre (10 s)    |
| V2-F + pas les deux baissent BTC                                                                 |         4 |      266 |       1258 |      871 |        587 |      749 |       -316 | + reste > 120 s                      |
| V2-B hors 60-89 s BTC                                                                            |         3 |     -426 |       1237 |      820 |        641 |     -560 |       -503 | + pas fenêtre :00/:30                |
| V2-F ecart qui grandit BTC                                                                       |         3 |       68 |       1461 |      829 |        534 |     -393 |       -598 | + pas fenêtre :00/:30                |
| V2-H veto complet BTC                                                                            |         5 |     -704 |       1336 |      822 |        -53 |     -397 |       -276 | + reste > 120 s                      |
| V2-E persistant BTC                                                                              |         5 |     -447 |       1260 |      247 |         68 |     -884 |        340 | + reste > 120 s                      |
| V2-G jury des bourses BTC                                                                        |         3 |     1294 |       1989 |      880 |       1122 |      898 |       1563 | + pas de saut Bybit contre (10 s)    |
| V2-F pause memoire BTC                                                                           |         4 |      -64 |        701 |      425 |        440 |      243 |        154 | + côté le moins cher (prix < 0,5)    |
| V2-D perp 120-269 s BTC                                                                          |         3 |      142 |       1447 |      961 |        780 |     1440 |       1664 | + pas de saut Bybit contre (10 s)    |
| desaccord 30 BTC                                                                                 |         1 |     1381 |       1675 |      245 |        264 |     -166 |       -232 | + profondeur de notre côté > médiane |
| desaccord 20 sans nuit BTC                                                                       |         3 |    -1131 |        182 |      928 |          0 |     -121 |        -49 | + reste > 120 s                      |
| V2-F + plus de 120 s BTC                                                                         |         3 |      -24 |       1398 |      883 |        534 |      113 |       -334 | + pas fenêtre :00/:30                |
| corrige marge mesuree : V2-F BTC                                                                 |         4 |      915 |       1675 |       61 |        -14 |     -311 |        273 | + écart Poly ≤ 1 c                   |
| corrige : V2-F ecart qui grandit BTC                                                             |         3 |      603 |       1326 |       61 |        -68 |      320 |        682 | + élan perp 30 s pour nous           |
| corrige : desaccord 20 BTC                                                                       |         3 |      343 |       1338 |       61 |        -68 |      299 |        636 | + pas de saut Bybit contre (10 s)    |
| corrige : V2-F + garde-fou BTC                                                                   |         3 |      603 |       1326 |       61 |        -68 |      339 |        701 | + élan perp 30 s pour nous           |
| corrige : V2-F + pas les deux baissent BTC                                                       |         2 |      672 |       1429 |      111 |        -18 |      319 |        530 | + pas de saut Bybit contre (10 s)    |
| V2-F incertitude 0,01 % BTC                                                                      |         2 |     1228 |       1578 |      155 |        -32 |       45 |         93 | + pas de saut Bybit contre (10 s)    |
| V2-F miroir 1 s BTC                                                                              |         3 |     -270 |        277 |      149 |          0 |      377 |        249 | + pas fenêtre :00/:30                |
| desaccord 30 zone 0,15-0,35 BTC                                                                  |         2 |     -380 |        458 |      161 |        280 |     -167 |       -200 | + contre la foule (flux 30 s)        |
| desaccord 30 zone + sortie modele -10 BTC                                                        |         1 |      -53 |        468 |      192 |        272 |     -115 |       -264 | + Poly a monté pour nous (5 s)       |
| TWAP fin anti-saut BTC                                                                           |         4 |      621 |        772 |      -19 |          0 |     1500 |         19 | + pas la nuit (02 h – 10 h)          |
| TWAP fin BTC                                                                                     |         4 |      641 |        772 |      -19 |          0 |     1500 |         19 | + pas la nuit (02 h – 10 h)          |
| TWAP fin quantiles BTC                                                                           |         1 |      487 |        603 |      -95 |        -24 |     1194 |          9 | + élan perp 30 s contre nous         |
| TWAP fin sauts BTC                                                                               |         1 |      470 |        581 |      -69 |          0 |     1179 |        -40 | + élan perp 30 s contre nous         |
| desaccord 30 0,15-0,60 + perp + ecart qui grandit BTC                                            |         1 |     -400 |        255 |      163 |        272 |     -244 |        -77 | + perp pour nous (5 s)               |
| TWAP fin correction spot-perp BTC                                                                |         3 |       96 |        316 |       26 |          0 |      400 |        325 | + marché calme (vol 5 min < 1 h)     |
| desaccord 30 zone 0,15-0,35 + Binance et perp BTC                                                |         1 |     -598 |        115 |      163 |        272 |     -258 |       -125 | + perp pour nous (5 s)               |
| desaccord 30 zone + Binance et perp + sortie modele -10 BTC                                      |         4 |     -404 |        472 |      194 |        280 |     -207 |        -55 | + reste > 120 s                      |
| TWAP fin prevision Chainlink BTC                                                                 |         3 |      209 |        290 |      -37 |         15 |      -45 |       -108 | + pas de saut Bybit contre (10 s)    |
| desaccord 20 Binance ou perp avec nous BTC                                                       |         3 |      780 |       1026 |      488 |        568 |     -529 |       -149 | + écart Poly ≤ 1 c                   |
| desaccord 20 Poly rejoint 10 s sans nuit BTC                                                     |         2 |       19 |        217 |      245 |        -24 |     -227 |       -142 | + côté le moins cher (prix < 0,5)    |
| desaccord 30 zone + Binance et perp + sortie modele -10 + pas Poly qui baisse + taille 25/50 BTC |         3 |     -151 |        332 |      253 |        280 |      -91 |        -56 | + pression carnet pour nous          |
| desaccord 30 zone + Binance et perp + sortie modele -10 + pas Poly qui baisse BTC                |         3 |     -353 |        496 |      253 |        280 |      -91 |        -79 | + pas de saut Bybit contre (10 s)    |
| desaccord 20 Binance ou perp avec nous sans nuit BTC                                             |         1 |      306 |        462 |      488 |        -14 |     -343 |       -102 | + pression carnet pour nous          |
| desaccord confirme perp BTC                                                                      |         2 |     -138 |        304 |      146 |        146 |     -131 |        -90 | + Poly a monté pour nous (5 s)       |
| desaccord 30 zone + modele monte BTC                                                             |         2 |       97 |        417 |      239 |        280 |      -40 |        -30 | + pas de saut Bybit contre (10 s)    |
| corrige : zone + Binance et perp + sortie -10 BTC                                                |         2 |      -61 |        200 |      -43 |          0 |      -32 |         -6 | + cycle calme (≤ 2 passages à 0,5)   |
| consensus K2 BTC                                                                                 |         0 |        0 |          0 |        0 |          0 |      945 |        945 | base                                 |
| TWAP fin confirme Chainlink 0,5 s BTC                                                            |         1 |      277 |        399 |      -59 |         -7 |       71 |         43 | + contre la foule (flux 30 s)        |

| étape                             |   n A |   P&L A |   ROI A |   n V |   P&L V |   ROI V |   n T |   P&L T |   ROI T |
|:----------------------------------|------:|--------:|--------:|------:|--------:|--------:|------:|--------:|--------:|
| base                              |  4211 |    7026 |       5 |   285 |   12073 |     114 |  2097 |    7422 |      11 |
| + contre la foule (flux 30 s)     |  2098 |   14097 |      21 |   145 |   14815 |     259 |  1106 |    7177 |      19 |
| + pas de saut Bybit contre (10 s) |  2040 |   16172 |      25 |   145 |   14815 |     259 |  1099 |    6772 |      18 |

## desaccord 20 60-180 s BTC

| étape                             |   n A |   P&L A |   ROI A |   n V |   P&L V |   ROI V |   n T |   P&L T |   ROI T |
|:----------------------------------|------:|--------:|--------:|------:|--------:|--------:|------:|--------:|--------:|
| base                              |   194 |     675 |      17 |    13 |     -47 |     -11 |   102 |     -63 |      -3 |
| + marché calme (vol 5 min < 1 h)  |   119 |    1432 |      59 |     4 |    -190 |    -100 |    72 |     356 |      25 |
| + pas de saut Bybit contre (10 s) |   117 |    1451 |      60 |     4 |    -190 |    -100 |    70 |     369 |      26 |

## V2-C perp BTC

| étape                                |   n A |   P&L A |   ROI A |   n V |   P&L V |   ROI V |   n T |   P&L T |   ROI T |
|:-------------------------------------|------:|--------:|--------:|------:|--------:|--------:|------:|--------:|--------:|
| base                                 |   184 |    -156 |      -2 |    13 |     908 |     147 |   105 |     862 |      21 |
| + carnet Poly pour nous              |    78 |    1042 |      35 |     5 |     780 |     340 |    70 |    1694 |      68 |
| + profondeur de notre côté > médiane |    72 |    1134 |      42 |     5 |     780 |     340 |    70 |    1694 |      68 |
| + pas de saut Bybit contre (10 s)    |    71 |    1187 |      45 |     5 |     780 |     340 |    67 |    1752 |      72 |

## V2-F + pas les deux baissent BTC

| étape                                   |   n A |   P&L A |   ROI A |   n V |   P&L V |   ROI V |   n T |   P&L T |   ROI T |
|:----------------------------------------|------:|--------:|--------:|------:|--------:|--------:|------:|--------:|--------:|
| base                                    |   186 |     266 |       4 |    13 |     871 |     156 |   100 |     749 |      20 |
| + Chainlink au-dessus du perp pour nous |    92 |     856 |      24 |     5 |     576 |     253 |    53 |     141 |       8 |
| + contre la foule (flux 30 s)           |    48 |    1206 |      63 |     4 |     587 |     272 |    27 |      -4 |       0 |
| + pas fenêtre :00/:30                   |    43 |    1240 |      73 |     4 |     587 |     272 |    20 |    -741 |     -93 |
| + reste > 120 s                         |    37 |    1258 |      83 |     4 |     587 |     272 |     8 |    -316 |    -100 |

## V2-B hors 60-89 s BTC

| étape                                   |   n A |   P&L A |   ROI A |   n V |   P&L V |   ROI V |   n T |   P&L T |   ROI T |
|:----------------------------------------|------:|--------:|--------:|------:|--------:|--------:|------:|--------:|--------:|
| base                                    |   182 |    -426 |      -7 |    13 |     820 |     124 |   104 |    -560 |     -14 |
| + Chainlink au-dessus du perp pour nous |    88 |     674 |      22 |     5 |     588 |     220 |    55 |    -271 |     -13 |
| + contre la foule (flux 30 s)           |    43 |    1182 |      75 |     4 |     641 |     300 |    29 |     -90 |      -8 |
| + pas fenêtre :00/:30                   |    38 |    1237 |      94 |     4 |     641 |     300 |    21 |    -503 |     -62 |

## V2-F ecart qui grandit BTC

| étape                                   |   n A |   P&L A |   ROI A |   n V |   P&L V |   ROI V |   n T |   P&L T |   ROI T |
|:----------------------------------------|------:|--------:|--------:|------:|--------:|--------:|------:|--------:|--------:|
| base                                    |   185 |      68 |       1 |    13 |     829 |     138 |   100 |    -393 |     -11 |
| + Chainlink au-dessus du perp pour nous |    91 |    1172 |      38 |     5 |     534 |     198 |    53 |     -45 |      -3 |
| + contre la foule (flux 30 s)           |    44 |    1428 |      87 |     5 |     534 |     198 |    26 |    -123 |     -13 |
| + pas fenêtre :00/:30                   |    39 |    1461 |     104 |     5 |     534 |     198 |    19 |    -598 |     -88 |

## V2-H veto complet BTC

| étape                                   |   n A |   P&L A |   ROI A |   n V |   P&L V |   ROI V |   n T |   P&L T |   ROI T |
|:----------------------------------------|------:|--------:|--------:|------:|--------:|--------:|------:|--------:|--------:|
| base                                    |   182 |    -704 |      -9 |    13 |     822 |     125 |   100 |    -397 |      -8 |
| + carnet Poly pour nous                 |    80 |     488 |      14 |     4 |     408 |     187 |    59 |     -56 |      -2 |
| + Chainlink au-dessus du perp pour nous |    43 |     874 |      49 |     1 |     -53 |    -100 |    31 |      91 |       8 |
| + pas fenêtre :00/:30                   |    34 |    1083 |      78 |     1 |     -53 |    -100 |    24 |     -76 |      -9 |
| + profondeur de notre côté > médiane    |    31 |    1235 |     100 |     1 |     -53 |    -100 |    23 |     -52 |      -6 |
| + reste > 120 s                         |    23 |    1336 |     138 |     1 |     -53 |    -100 |    10 |    -276 |     -71 |

## V2-E persistant BTC

| étape                                |   n A |   P&L A |   ROI A |   n V |   P&L V |   ROI V |   n T |   P&L T |   ROI T |
|:-------------------------------------|------:|--------:|--------:|------:|--------:|--------:|------:|--------:|--------:|
| base                                 |   185 |    -447 |      -6 |    12 |     247 |      39 |    90 |    -884 |     -20 |
| + profondeur de notre côté > médiane |   103 |     509 |      12 |     8 |     443 |     103 |    73 |    -577 |     -16 |
| + élan perp 30 s contre nous         |    69 |    1028 |      34 |     4 |      15 |       7 |    42 |    -268 |     -13 |
| + pas de saut Bybit contre (10 s)    |    64 |    1161 |      41 |     4 |      15 |       7 |    42 |    -268 |     -13 |
| + contre la foule (flux 30 s)        |    39 |    1196 |      70 |     3 |      68 |      43 |    28 |      62 |       4 |
| + reste > 120 s                      |    29 |    1260 |      97 |     3 |      68 |      43 |    14 |     340 |      46 |

## V2-G jury des bourses BTC

| étape                              |   n A |   P&L A |   ROI A |   n V |   P&L V |   ROI V |   n T |   P&L T |   ROI T |
|:-----------------------------------|------:|--------:|--------:|------:|--------:|--------:|------:|--------:|--------:|
| base                               |   178 |    1294 |      19 |    13 |     880 |     160 |    86 |     898 |      30 |
| + cycle calme (≤ 2 passages à 0,5) |    98 |    1833 |      50 |     6 |    1122 |     366 |    41 |    1557 |     113 |
| + écart Poly ≤ 1 c                 |    94 |    1936 |      54 |     6 |    1122 |     366 |    40 |    1563 |     114 |
| + pas de saut Bybit contre (10 s)  |    93 |    1989 |      56 |     6 |    1122 |     366 |    40 |    1563 |     114 |

## V2-F pause memoire BTC

| étape                                   |   n A |   P&L A |   ROI A |   n V |   P&L V |   ROI V |   n T |   P&L T |   ROI T |
|:----------------------------------------|------:|--------:|--------:|------:|--------:|--------:|------:|--------:|--------:|
| base                                    |   155 |     -64 |      -3 |    13 |     425 |      98 |    97 |     243 |      15 |
| + Chainlink au-dessus du perp pour nous |    75 |     625 |      53 |     5 |     440 |     263 |    52 |     290 |      36 |
| + pas fenêtre :00/:30                   |    63 |     678 |      74 |     5 |     440 |     263 |    41 |     154 |      23 |
| + pas de saut Bybit contre (10 s)       |    61 |     698 |      78 |     5 |     440 |     263 |    41 |     154 |      23 |
| + côté le moins cher (prix < 0,5)       |    60 |     701 |      78 |     5 |     440 |     263 |    41 |     154 |      23 |

## V2-D perp 120-269 s BTC

| étape                                |   n A |   P&L A |   ROI A |   n V |   P&L V |   ROI V |   n T |   P&L T |   ROI T |
|:-------------------------------------|------:|--------:|--------:|------:|--------:|--------:|------:|--------:|--------:|
| base                                 |   167 |     142 |       2 |    12 |     961 |     170 |    64 |    1440 |      52 |
| + carnet Poly pour nous              |    66 |    1234 |      46 |     5 |     780 |     340 |    40 |    1660 |     104 |
| + profondeur de notre côté > médiane |    63 |    1394 |      55 |     5 |     780 |     340 |    40 |    1660 |     104 |
| + pas de saut Bybit contre (10 s)    |    62 |    1447 |      58 |     5 |     780 |     340 |    39 |    1664 |     104 |

## desaccord 30 BTC

| étape                                |   n A |   P&L A |   ROI A |   n V |   P&L V |   ROI V |   n T |   P&L T |   ROI T |
|:-------------------------------------|------:|--------:|--------:|------:|--------:|--------:|------:|--------:|--------:|
| base                                 |   162 |    1381 |      78 |     8 |     245 |     456 |    64 |    -166 |     -15 |
| + profondeur de notre côté > médiane |    78 |    1675 |     199 |     4 |     264 |     753 |    56 |    -232 |     -22 |

## desaccord 20 sans nuit BTC

| étape                          |   n A |   P&L A |   ROI A |   n V |   P&L V |   ROI V |   n T |   P&L T |   ROI T |
|:-------------------------------|------:|--------:|--------:|------:|--------:|--------:|------:|--------:|--------:|
| base                           |   128 |   -1131 |     -27 |    11 |     928 |     168 |    88 |    -121 |      -4 |
| + Poly a monté pour nous (5 s) |    19 |     117 |      22 |     0 |       0 |     nan |    15 |    -227 |     -42 |
| + pas fenêtre :00/:30          |    15 |     170 |      37 |     0 |       0 |     nan |    14 |    -174 |     -36 |
| + reste > 120 s                |    14 |     182 |      40 |     0 |       0 |     nan |    10 |     -49 |     -14 |

## V2-F + plus de 120 s BTC

| étape                                   |   n A |   P&L A |   ROI A |   n V |   P&L V |   ROI V |   n T |   P&L T |   ROI T |
|:----------------------------------------|------:|--------:|--------:|------:|--------:|--------:|------:|--------:|--------:|
| base                                    |   156 |     -24 |       0 |    12 |     883 |     162 |    58 |     113 |       5 |
| + Chainlink au-dessus du perp pour nous |    78 |    1095 |      38 |     5 |     534 |     198 |    27 |     273 |      27 |
| + contre la foule (flux 30 s)           |    40 |    1366 |      89 |     5 |     534 |     198 |    13 |     152 |      30 |
| + pas fenêtre :00/:30                   |    35 |    1398 |     107 |     5 |     534 |     198 |     9 |    -334 |    -100 |

## corrige marge mesuree : V2-F BTC

| étape                             |   n A |   P&L A |   ROI A |   n V |   P&L V |   ROI V |   n T |   P&L T |   ROI T |
|:----------------------------------|------:|--------:|--------:|------:|--------:|--------:|------:|--------:|--------:|
| base                              |   132 |     915 |      23 |     8 |      61 |      30 |    69 |    -311 |     -13 |
| + élan perp 30 s pour nous        |    65 |    1512 |      68 |     3 |     -65 |     -92 |    39 |     -82 |      -6 |
| + marché calme (vol 5 min < 1 h)  |    45 |    1609 |     110 |     2 |     -68 |    -100 |    32 |     167 |      14 |
| + pas de saut Bybit contre (10 s) |    44 |    1662 |     118 |     2 |     -68 |    -100 |    32 |     167 |      14 |
| + écart Poly ≤ 1 c                |    43 |    1675 |     120 |     1 |     -14 |    -100 |    30 |     273 |      24 |

## corrige : V2-F ecart qui grandit BTC

| étape                             |   n A |   P&L A |   ROI A |   n V |   P&L V |   ROI V |   n T |   P&L T |   ROI T |
|:----------------------------------|------:|--------:|--------:|------:|--------:|--------:|------:|--------:|--------:|
| base                              |   139 |     603 |      13 |     8 |      61 |      30 |    62 |     320 |      15 |
| + marché calme (vol 5 min < 1 h)  |    91 |    1256 |      43 |     3 |    -122 |    -100 |    46 |     598 |      37 |
| + pas de saut Bybit contre (10 s) |    90 |    1309 |      45 |     3 |    -122 |    -100 |    43 |     568 |      36 |
| + élan perp 30 s pour nous        |    43 |    1326 |      99 |     2 |     -68 |    -100 |    27 |     682 |      70 |

## corrige : desaccord 20 BTC

| étape                             |   n A |   P&L A |   ROI A |   n V |   P&L V |   ROI V |   n T |   P&L T |   ROI T |
|:----------------------------------|------:|--------:|--------:|------:|--------:|--------:|------:|--------:|--------:|
| base                              |   138 |     343 |       8 |     8 |      61 |      30 |    62 |     299 |      14 |
| + marché calme (vol 5 min < 1 h)  |    90 |    1111 |      40 |     3 |    -122 |    -100 |    46 |     552 |      34 |
| + élan perp 30 s pour nous        |    43 |    1285 |      98 |     2 |     -68 |    -100 |    27 |     636 |      63 |
| + pas de saut Bybit contre (10 s) |    42 |    1338 |     106 |     2 |     -68 |    -100 |    27 |     636 |      63 |

## corrige : V2-F + garde-fou BTC

| étape                             |   n A |   P&L A |   ROI A |   n V |   P&L V |   ROI V |   n T |   P&L T |   ROI T |
|:----------------------------------|------:|--------:|--------:|------:|--------:|--------:|------:|--------:|--------:|
| base                              |   139 |     603 |      13 |     8 |      61 |      30 |    61 |     339 |      16 |
| + marché calme (vol 5 min < 1 h)  |    91 |    1256 |      43 |     3 |    -122 |    -100 |    45 |     617 |      39 |
| + pas de saut Bybit contre (10 s) |    90 |    1309 |      45 |     3 |    -122 |    -100 |    42 |     587 |      38 |
| + élan perp 30 s pour nous        |    43 |    1326 |      99 |     2 |     -68 |    -100 |    26 |     701 |      74 |

## corrige : V2-F + pas les deux baissent BTC

| étape                             |   n A |   P&L A |   ROI A |   n V |   P&L V |   ROI V |   n T |   P&L T |   ROI T |
|:----------------------------------|------:|--------:|--------:|------:|--------:|--------:|------:|--------:|--------:|
| base                              |   138 |     672 |      15 |     8 |     111 |      70 |    60 |     319 |      15 |
| + marché calme (vol 5 min < 1 h)  |    90 |    1323 |      46 |     2 |     -18 |    -100 |    46 |     631 |      40 |
| + pas de saut Bybit contre (10 s) |    88 |    1429 |      51 |     2 |     -18 |    -100 |    43 |     530 |      35 |

## V2-F incertitude 0,01 % BTC

| étape                             |   n A |   P&L A |   ROI A |   n V |   P&L V |   ROI V |   n T |   P&L T |   ROI T |
|:----------------------------------|------:|--------:|--------:|------:|--------:|--------:|------:|--------:|--------:|
| base                              |   130 |    1228 |      54 |     8 |     155 |     157 |    59 |      45 |       4 |
| + marché calme (vol 5 min < 1 h)  |    85 |    1576 |     107 |     3 |     -32 |    -100 |    43 |     125 |      13 |
| + pas de saut Bybit contre (10 s) |    84 |    1578 |     107 |     3 |     -32 |    -100 |    40 |      93 |      10 |

## V2-F miroir 1 s BTC

| étape                                   |   n A |   P&L A |   ROI A |   n V |   P&L V |   ROI V |   n T |   P&L T |   ROI T |
|:----------------------------------------|------:|--------:|--------:|------:|--------:|--------:|------:|--------:|--------:|
| base                                    |    68 |    -270 |     -20 |     9 |     149 |      45 |    54 |     377 |      38 |
| + Chainlink au-dessus du perp pour nous |    32 |     129 |      19 |     2 |     133 |     137 |    28 |     410 |      89 |
| + carnet Poly pour nous                 |    14 |     238 |      93 |     0 |       0 |     nan |    21 |     362 |     125 |
| + pas fenêtre :00/:30                   |    10 |     277 |     134 |     0 |       0 |     nan |    15 |     249 |     121 |

## desaccord 30 zone 0,15-0,35 BTC

| étape                          |   n A |   P&L A |   ROI A |   n V |   P&L V |   ROI V |   n T |   P&L T |   ROI T |
|:-------------------------------|------:|--------:|--------:|------:|--------:|--------:|------:|--------:|--------:|
| base                           |    83 |    -380 |     -15 |     4 |     161 |      93 |    19 |    -167 |     -41 |
| + Poly a monté pour nous (5 s) |    15 |     450 |     134 |     2 |     272 |     440 |     9 |    -280 |     -93 |
| + contre la foule (flux 30 s)  |    10 |     458 |     182 |     1 |     280 |     528 |     5 |    -200 |     -91 |

## desaccord 30 zone + sortie modele -10 BTC

| étape                          |   n A |   P&L A |   ROI A |   n V |   P&L V |   ROI V |   n T |   P&L T |   ROI T |
|:-------------------------------|------:|--------:|--------:|------:|--------:|--------:|------:|--------:|--------:|
| base                           |    83 |     -53 |      -2 |     4 |     192 |     112 |    19 |    -115 |     -28 |
| + Poly a monté pour nous (5 s) |    15 |     468 |     140 |     2 |     272 |     440 |     9 |    -264 |     -88 |

## TWAP fin anti-saut BTC

| étape                             |   n A |   P&L A |   ROI A |   n V |   P&L V |   ROI V |   n T |   P&L T |   ROI T |
|:----------------------------------|------:|--------:|--------:|------:|--------:|--------:|------:|--------:|--------:|
| base                              |    64 |     621 |      60 |     4 |     -19 |     -24 |    32 |    1500 |     228 |
| + élan perp 30 s contre nous      |    18 |     766 |     301 |     1 |      -1 |    -100 |    13 |      52 |      17 |
| + côté le moins cher (prix < 0,5) |    17 |     769 |     307 |     1 |      -1 |    -100 |    13 |      52 |      17 |
| + écart Poly ≤ 1 c                |    16 |     771 |     309 |     1 |      -1 |    -100 |    11 |      19 |       7 |
| + pas la nuit (02 h – 10 h)       |    15 |     772 |     311 |     0 |       0 |     nan |    11 |      19 |       7 |

## TWAP fin BTC

| étape                             |   n A |   P&L A |   ROI A |   n V |   P&L V |   ROI V |   n T |   P&L T |   ROI T |
|:----------------------------------|------:|--------:|--------:|------:|--------:|--------:|------:|--------:|--------:|
| base                              |    63 |     641 |      62 |     4 |     -19 |     -24 |    32 |    1500 |     228 |
| + élan perp 30 s contre nous      |    18 |     766 |     301 |     1 |      -1 |    -100 |    13 |      52 |      17 |
| + côté le moins cher (prix < 0,5) |    17 |     769 |     307 |     1 |      -1 |    -100 |    13 |      52 |      17 |
| + écart Poly ≤ 1 c                |    16 |     771 |     309 |     1 |      -1 |    -100 |    11 |      19 |       7 |
| + pas la nuit (02 h – 10 h)       |    15 |     772 |     311 |     0 |       0 |     nan |    11 |      19 |       7 |

## TWAP fin quantiles BTC

| étape                        |   n A |   P&L A |   ROI A |   n V |   P&L V |   ROI V |   n T |   P&L T |   ROI T |
|:-----------------------------|------:|--------:|--------:|------:|--------:|--------:|------:|--------:|--------:|
| base                         |    62 |     487 |      41 |     4 |     -95 |    -100 |    30 |    1194 |     163 |
| + élan perp 30 s contre nous |    14 |     603 |     175 |     1 |     -24 |    -100 |    12 |       9 |       3 |

## TWAP fin sauts BTC

| étape                        |   n A |   P&L A |   ROI A |   n V |   P&L V |   ROI V |   n T |   P&L T |   ROI T |
|:-----------------------------|------:|--------:|--------:|------:|--------:|--------:|------:|--------:|--------:|
| base                         |    59 |     470 |      46 |     4 |     -69 |     -93 |    28 |    1179 |     155 |
| + élan perp 30 s contre nous |    16 |     581 |     249 |     0 |       0 |     nan |    10 |     -40 |     -10 |

## desaccord 30 0,15-0,60 + perp + ecart qui grandit BTC

| étape                  |   n A |   P&L A |   ROI A |   n V |   P&L V |   ROI V |   n T |   P&L T |   ROI T |
|:-----------------------|------:|--------:|--------:|------:|--------:|--------:|------:|--------:|--------:|
| base                   |    73 |    -400 |     -17 |     4 |     163 |      95 |    13 |    -244 |     -77 |
| + perp pour nous (5 s) |    14 |     255 |      85 |     2 |     272 |     440 |     8 |     -77 |     -52 |

## TWAP fin correction spot-perp BTC

| étape                            |   n A |   P&L A |   ROI A |   n V |   P&L V |   ROI V |   n T |   P&L T |   ROI T |
|:---------------------------------|------:|--------:|--------:|------:|--------:|--------:|------:|--------:|--------:|
| base                             |    58 |      96 |      10 |     3 |      26 |      76 |    27 |     400 |      72 |
| + carnet Binance pour nous       |    24 |     201 |      45 |     2 |      34 |     127 |    14 |     335 |     137 |
| + écart Poly ≤ 1 c               |    17 |     285 |      86 |     1 |      38 |     173 |    13 |     300 |     129 |
| + marché calme (vol 5 min < 1 h) |    12 |     316 |     129 |     0 |       0 |     nan |    11 |     325 |     158 |

## desaccord 30 zone 0,15-0,35 + Binance et perp BTC

| étape                  |   n A |   P&L A |   ROI A |   n V |   P&L V |   ROI V |   n T |   P&L T |   ROI T |
|:-----------------------|------:|--------:|--------:|------:|--------:|--------:|------:|--------:|--------:|
| base                   |    66 |    -598 |     -26 |     4 |     163 |      95 |    13 |    -258 |     -77 |
| + perp pour nous (5 s) |    11 |     115 |      47 |     2 |     272 |     440 |     8 |    -125 |     -62 |

## desaccord 30 zone + Binance et perp + sortie modele -10 BTC

| étape                             |   n A |   P&L A |   ROI A |   n V |   P&L V |   ROI V |   n T |   P&L T |   ROI T |
|:----------------------------------|------:|--------:|--------:|------:|--------:|--------:|------:|--------:|--------:|
| base                              |    66 |    -404 |     -18 |     4 |     194 |     114 |    13 |    -207 |     -62 |
| + contre la foule (flux 30 s)     |    38 |     149 |      11 |     2 |     259 |     245 |     9 |    -188 |     -74 |
| + pas fenêtre :00/:30             |    30 |     387 |      36 |     2 |     259 |     245 |     9 |    -188 |     -74 |
| + pas de saut Bybit contre (10 s) |    28 |     451 |      45 |     2 |     259 |     245 |     9 |    -188 |     -74 |
| + reste > 120 s                   |    17 |     472 |      69 |     1 |     280 |     528 |     1 |     -55 |    -100 |

## TWAP fin prevision Chainlink BTC

| étape                             |   n A |   P&L A |   ROI A |   n V |   P&L V |   ROI V |   n T |   P&L T |   ROI T |
|:----------------------------------|------:|--------:|--------:|------:|--------:|--------:|------:|--------:|--------:|
| base                              |    53 |     209 |      29 |     3 |     -37 |     -58 |    27 |     -45 |      -9 |
| + carnet Poly pour nous           |    28 |     252 |      73 |     2 |      15 |     129 |    13 |     -31 |     -14 |
| + écart Poly ≤ 1 c                |    21 |     275 |     124 |     2 |      15 |     129 |    11 |     -31 |     -17 |
| + pas de saut Bybit contre (10 s) |    20 |     290 |     141 |     2 |      15 |     129 |     9 |    -108 |     -67 |

## desaccord 20 Binance ou perp avec nous BTC

| étape                        |   n A |   P&L A |   ROI A |   n V |   P&L V |   ROI V |   n T |   P&L T |   ROI T |
|:-----------------------------|------:|--------:|--------:|------:|--------:|--------:|------:|--------:|--------:|
| base                         |    34 |     780 |      79 |     4 |     488 |     357 |    37 |    -529 |     -39 |
| + élan perp 30 s contre nous |    19 |     908 |     134 |     1 |     568 |     992 |    21 |    -147 |     -20 |
| + pas fenêtre :00/:30        |    13 |    1008 |     182 |     1 |     568 |     992 |    12 |    -149 |     -41 |
| + écart Poly ≤ 1 c           |    12 |    1026 |     192 |     1 |     568 |     992 |    12 |    -149 |     -41 |

## desaccord 20 Poly rejoint 10 s sans nuit BTC

| étape                             |   n A |   P&L A |   ROI A |   n V |   P&L V |   ROI V |   n T |   P&L T |   ROI T |
|:----------------------------------|------:|--------:|--------:|------:|--------:|--------:|------:|--------:|--------:|
| base                              |    35 |      19 |       1 |     5 |     245 |     103 |    32 |    -227 |     -15 |
| + marché calme (vol 5 min < 1 h)  |    20 |     112 |      12 |     1 |     -24 |    -100 |    22 |     -98 |      -9 |
| + côté le moins cher (prix < 0,5) |    12 |     217 |      38 |     1 |     -24 |    -100 |    18 |    -142 |     -17 |

## desaccord 30 zone + Binance et perp + sortie modele -10 + pas Poly qui baisse + taille 25/50 BTC

| étape                       |   n A |   P&L A |   ROI A |   n V |   P&L V |   ROI V |   n T |   P&L T |   ROI T |
|:----------------------------|------:|--------:|--------:|------:|--------:|--------:|------:|--------:|--------:|
| base                        |    53 |    -151 |     -12 |     2 |     253 |     268 |     9 |     -91 |     -45 |
| + perp pour nous (5 s)      |    15 |     269 |      95 |     1 |     280 |     528 |     6 |     -65 |     -46 |
| + pas fenêtre :00/:30       |    12 |     307 |     132 |     1 |     280 |     528 |     6 |     -65 |     -46 |
| + pression carnet pour nous |    10 |     332 |     162 |     1 |     280 |     528 |     3 |     -56 |     -74 |

## desaccord 30 zone + Binance et perp + sortie modele -10 + pas Poly qui baisse BTC

| étape                             |   n A |   P&L A |   ROI A |   n V |   P&L V |   ROI V |   n T |   P&L T |   ROI T |
|:----------------------------------|------:|--------:|--------:|------:|--------:|--------:|------:|--------:|--------:|
| base                              |    53 |    -353 |     -19 |     2 |     253 |     268 |     9 |     -91 |     -45 |
| + contre la foule (flux 30 s)     |    33 |     246 |      22 |     1 |     280 |     528 |     6 |     -79 |     -62 |
| + pas fenêtre :00/:30             |    26 |     426 |      48 |     1 |     280 |     528 |     6 |     -79 |     -62 |
| + pas de saut Bybit contre (10 s) |    24 |     496 |      61 |     1 |     280 |     528 |     6 |     -79 |     -62 |

## desaccord 20 Binance ou perp avec nous sans nuit BTC

| étape                       |   n A |   P&L A |   ROI A |   n V |   P&L V |   ROI V |   n T |   P&L T |   ROI T |
|:----------------------------|------:|--------:|--------:|------:|--------:|--------:|------:|--------:|--------:|
| base                        |    24 |     306 |      37 |     4 |     488 |     357 |    29 |    -343 |     -31 |
| + pression carnet pour nous |    10 |     462 |     163 |     1 |     -14 |    -100 |    16 |    -102 |     -19 |

## desaccord confirme perp BTC

| étape                          |   n A |   P&L A |   ROI A |   n V |   P&L V |   ROI V |   n T |   P&L T |   ROI T |
|:-------------------------------|------:|--------:|--------:|------:|--------:|--------:|------:|--------:|--------:|
| base                           |    31 |    -138 |     -10 |     1 |     146 |     268 |    23 |    -131 |     -12 |
| + perp pour nous (5 s)         |    13 |     199 |      32 |     1 |     146 |     268 |    17 |      87 |      10 |
| + Poly a monté pour nous (5 s) |    11 |     304 |      58 |     1 |     146 |     268 |    14 |     -90 |     -13 |

## desaccord 30 zone + modele monte BTC

| étape                             |   n A |   P&L A |   ROI A |   n V |   P&L V |   ROI V |   n T |   P&L T |   ROI T |
|:----------------------------------|------:|--------:|--------:|------:|--------:|--------:|------:|--------:|--------:|
| base                              |    35 |      97 |      10 |     2 |     239 |     253 |    12 |     -40 |     -18 |
| + contre la foule (flux 30 s)     |    21 |     364 |      62 |     1 |     280 |     528 |     8 |     -30 |     -23 |
| + pas de saut Bybit contre (10 s) |    20 |     417 |      78 |     1 |     280 |     528 |     8 |     -30 |     -23 |

## corrige : zone + Binance et perp + sortie -10 BTC

| étape                              |   n A |   P&L A |   ROI A |   n V |   P&L V |   ROI V |   n T |   P&L T |   ROI T |
|:-----------------------------------|------:|--------:|--------:|------:|--------:|--------:|------:|--------:|--------:|
| base                               |    30 |     -61 |      -6 |     3 |     -43 |     -40 |     7 |     -32 |     -16 |
| + contre la foule (flux 30 s)      |    16 |     178 |      30 |     0 |       0 |     nan |     1 |      -6 |     -10 |
| + cycle calme (≤ 2 passages à 0,5) |    10 |     200 |      50 |     0 |       0 |     nan |     1 |      -6 |     -10 |

## consensus K2 BTC

| étape   |   n A |   P&L A | ROI A   |   n V |   P&L V | ROI V   |   n T |   P&L T |   ROI T |
|:--------|------:|--------:|:--------|------:|--------:|:--------|------:|--------:|--------:|
| base    |     0 |       0 |         |     0 |       0 |         |    38 |     945 |      59 |

## TWAP fin confirme Chainlink 0,5 s BTC

| étape                         |   n A |   P&L A |   ROI A |   n V |   P&L V |   ROI V |   n T |   P&L T |   ROI T |
|:------------------------------|------:|--------:|--------:|------:|--------:|--------:|------:|--------:|--------:|
| base                          |    25 |     277 |      40 |     2 |     -59 |    -100 |     8 |      71 |      29 |
| + contre la foule (flux 30 s) |    11 |     399 |     113 |     1 |      -7 |    -100 |     3 |      43 |      39 |
