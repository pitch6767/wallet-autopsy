# Pourquoi l'avantage fond si vite — attribution de la convergence et double alpha (BTC, 140 signaux, 07.10 08:05 → 09.10 22:35)

Mêmes signaux que l'étude A : moteur TWAP fin original, avantage ≥ 0,20, entre 90 et 20 s avant la fin, premier signal du cycle, 50 $ au meilleur vendeur limité à la quantité affichée, frais compris. « Notre côté » = le côté que le signal achète. Variation de l'avantage = variation de notre probabilité − variation du prix demandé (identité exacte).

## 1. La question décisive : qui bouge ?

| Délai | Variation de l'avantage | dont notre probabilité | dont le prix demandé (signe −) | Part due au marché | Prix vendeur moyen | Prix acheteur moyen |
|---|---|---|---|---|---|---|
| 0.25 s | -0.083 | +0.002 | -0.085 | 98 % | 0.336 | 0.312 |
| 0.5 s | -0.108 | -0.001 | -0.107 | 99 % | 0.358 | 0.337 |
| 1 s | -0.129 | -0.001 | -0.128 | 99 % | 0.379 | 0.365 |
| 2 s | -0.140 | -0.008 | -0.132 | 94 % | 0.376 | 0.364 |
| 5 s | -0.166 | -0.019 | -0.147 | 89 % | 0.388 | 0.381 |
| 10 s | -0.170 | -0.033 | -0.137 | 81 % | 0.377 | 0.379 |
| 20 s | -0.207 | -0.092 | -0.116 | 56 % | 0.345 | 0.408 |

Au signal : prix vendeur moyen 0.251, notre probabilité moyenne 0.512, prix acheteur moyen 0.232.

## 2. Classement des signaux selon ce qui se passe dans les 1 s suivantes (seuil 5 points, fixé avant de regarder)

| Groupe | Achats | Gagnés | Résultat | Par $ | Creux | Pertes de suite max |
|---|---|---|---|---|---|---|
| 1. Polymarket rejoint notre modèle | 72 | 60 % | **+1'098 $** | +99 % | −122 $ | 3 |
| 2. notre modèle rejoint Polymarket | 13 | 31 % | **+95 $** | +34 % | −99 $ | 3 |
| 3. les deux convergent | 5 | 60 % | **+487 $** | +460 % | −10 $ | 1 |
| 4. les deux s'écartent davantage | 7 | 29 % | **−112 $** | -56 % | −112 $ | 3 |
| 5. presque rien ne bouge (< 5 points) | 43 | 28 % | **+756 $** | +66 % | −155 $ | 7 |

## 2. Classement des signaux selon ce qui se passe dans les 5 s suivantes (seuil 5 points, fixé avant de regarder)

| Groupe | Achats | Gagnés | Résultat | Par $ | Creux | Pertes de suite max |
|---|---|---|---|---|---|---|
| 1. Polymarket rejoint notre modèle | 68 | 68 % | **+1'832 $** | +136 % | −105 $ | 3 |
| 2. notre modèle rejoint Polymarket | 42 | 17 % | **+469 $** | +55 % | −275 $ | 13 |
| 3. les deux convergent | 7 | 43 % | **+1 $** | +1 % | −45 $ | 2 |
| 4. les deux s'écartent davantage | 4 | 50 % | **+88 $** | +56 % | −53 $ | 1 |
| 5. presque rien ne bouge (< 5 points) | 16 | 19 % | **−86 $** | -24 % | −158 $ | 7 |
| carnet vide de notre côté | 3 | 100 % | **+19 $** | +31 % | +0 $ | 0 |

Résultat = achat au moment du signal, conservé jusqu'au règlement. Le classement utilise l'avenir : c'est un diagnostic, pas une règle.

## 3. Double alpha : gain au règlement contre revente possible (prix acheteur réellement affiché)

| Moment | Revente possible avec bénéfice après frais | Gain moyen par jeton si on revendait | Gain moyen par jeton au règlement |
|---|---|---|---|
| +1 s | 83 / 140 | +0.091 | +0.195 |
| +2 s | 86 / 140 | +0.099 | +0.195 |
| +5 s | 82 / 138 | +0.118 | +0.198 |
| +10 s | 73 / 135 | +0.126 | +0.212 |
| +20 s | 64 / 116 | +0.189 | +0.261 |

Rappel : les sorties anticipées naïves ont déjà détruit de la performance. Ce tableau mesure, il ne propose pas de vendre.

## 4. Qui a créé l'avantage ? (3 s AVANT le signal, information disponible au moment de l'achat)

| Groupe | Achats | Gagnés | Résultat | Par $ | Creux | Pertes de suite max |
|---|---|---|---|---|---|---|
| désaccord déjà là (avantage ≥ 0,15 trois secondes avant) | 28 | 43 % | **+684 $** | +99 % | −89 $ | 3 |
| le prix Polymarket a chuté, notre probabilité stable | 20 | 35 % | **+199 $** | +35 % | −192 $ | 7 |
| les deux (proba ↑, prix ↓) | 11 | 55 % | **+196 $** | +72 % | −43 $ | 2 |
| notre probabilité a monté, le prix n'a pas baissé | 73 | 44 % | **+681 $** | +61 % | −185 $ | 5 |
| pas de mesure 3 s avant | 5 | 80 % | **+174 $** | +149 % | −8 $ | 1 |
| petits mouvements des deux côtés | 3 | 100 % | **+389 $** | +489 % | +0 $ | 0 |

## 5. Surprise : la révision inattendue prédit-elle mieux le gain que l'avantage instantané ?

Sur 135 signaux, corrélation avec (gagné 1/0 − prix payé) :

- avantage instantané (proba − prix) : +0.174
- variation de notre proba sur 3 s : +0.151
- dont partie mécanique (le temps passe, rien de nouveau) : -0.045 — taille moyenne -0.009
- dont partie inattendue (information nouvelle) : +0.151 — taille moyenne +0.173
- « prix de la surprise » = partie inattendue − hausse du prix demandé : +0.124

Avec 135 signaux, une corrélation doit dépasser environ ±0.17 pour ne pas être du hasard.

| Groupe | Achats | Gagnés | Résultat | Par $ | Creux | Pertes de suite max |
|---|---|---|---|---|---|---|
| en dessous | 68 | 38 % | **+1'394 $** | +91 % | −241 $ | 7 |
| surprise non intégrée au-dessus de la médiane | 67 | 51 % | **+755 $** | +64 % | −197 $ | 4 |

## 6. Les bascules récentes (< 3 s) : 37 signaux

| Groupe | Achats | Gagnés | Résultat | Par $ | Creux | Pertes de suite max |
|---|---|---|---|---|---|---|
| carnet : favori changé après nous | 3 | 100 % | **+262 $** | +282 % | +0 $ | 0 |
| carnet : favori changé avant nous | 14 | 64 % | **+292 $** | +80 % | −52 $ | 2 |
| carnet : favori jamais changé | 20 | 75 % | **+262 $** | +106 % | −71 $ | 2 |
| origine : nouveau prix Chainlink reçu | 37 | 73 % | **+816 $** | +115 % | −71 $ | 2 |
| réaction du carnet faible (< 1/3 du mouvement de notre proba) | 25 | 68 % | **+537 $** | +103 % | −96 $ | 4 |
| réaction forte (> 2/3) | 1 | 0 % | **−44 $** | -105 % | −44 $ | 1 |
| réaction partielle (1/3 à 2/3) | 9 | 89 % | **+98 $** | +103 % | −18 $ | 1 |

## 7. Le groupe « notre modèle a basculé, le carnet jamais » (24 signaux) avec latence

| Achat après | Encore ≥ 0,20 | Résultat | Prix moyen |
|---|---|---|---|
| 0 s | 24 / 24 | +2'407 $ | 0.30 |
| 0.25 s | 11 / 24 | +1'461 $ | 0.46 |
| 0.5 s | 8 / 24 | +1'300 $ | 0.52 |
| 1 s | 7 / 24 | +1'094 $ | 0.55 |

(Ici la quantité est supposée disponible pour 50 $ ; l'étude A montre que c'est presque toujours le cas.)

## 8. Même probabilité, prix différents : les contrats bon marché gagnent-ils assez ? (60-20 s, une mesure par cycle et par tranche)

| Notre probabilité | Prix demandé | Mesures | Prix moyen | Gagnés | Écart gagné − prix |
|---|---|---|---|---|---|
| 0-20 % | bien moins cher (≥ 15 points sous la proba) | 22 | 0.03 | 0 % | -3 points |
| 0-20 % | proche | 315 | 0.07 | 7 % | -0 points |
| 0-20 % | plus cher | 60 | 0.34 | 8 % | -25 points |
| 20-40 % | bien moins cher (≥ 15 points sous la proba) | 108 | 0.13 | 19 % | +5 points |
| 20-40 % | proche | 159 | 0.22 | 23 % | +1 points |
| 20-40 % | plus cher | 62 | 0.50 | 27 % | -22 points |
| 40-60 % | bien moins cher (≥ 15 points sous la proba) | 70 | 0.25 | 41 % | +16 points |
| 40-60 % | proche | 105 | 0.45 | 48 % | +2 points |
| 40-60 % | plus cher | 105 | 0.67 | 56 % | -11 points |
| 60-80 % | bien moins cher (≥ 15 points sous la proba) | 29 | 0.41 | 76 % | +35 points |
| 60-80 % | proche | 103 | 0.68 | 71 % | +3 points |
| 60-80 % | plus cher | 167 | 0.83 | 77 % | -6 points |
| 80-100 % | bien moins cher (≥ 15 points sous la proba) | 27 | 0.48 | 93 % | +45 points |
| 80-100 % | proche | 245 | 0.92 | 91 % | -0 points |
| 80-100 % | plus cher | 191 | 0.94 | 92 % | -2 points |

## 9. Quand notre modèle et le carnet divergent de plus de 15 points, qui avait raison ? (Brier, plus bas = meilleur)

| Temps restant | Mesures | Cycles | Brier moteur | Brier carnet (milieu) |
|---|---|---|---|---|
| 60-90 s | 2902 | 166 | 0.208 | 0.233 |
| 40-60 s | 2301 | 119 | 0.183 | 0.209 |
| 20-40 s | 1521 | 71 | 0.138 | 0.119 |

Total des 140 signaux achetés au signal : +2'323 $.