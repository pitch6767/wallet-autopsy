# TWAP fin — nouvelles idées : fiabilité, bid/spread, contrat opposé (BTC, 693 cycles, 07.10 08:05 → 09.10 22:35)

Signaux de référence : les 140 premiers signaux TWAP fin original de chaque cycle (avantage ≥ 0,20, 90-20 s), +2 323 $. Apprentissage avant le 08.10 20:30, validation après.

## A. Qui prévoit le mieux le gagnant, seconde par seconde ? (Brier, plus bas = meilleur, une mesure par seconde)

| Temps restant | Mesures | Moteur original | Sauts | Spot-perp | Carnet (milieu) | Quand ils divergent > 15 pts : moteur / carnet (mesures) |
|---|---|---|---|---|---|---|
| 80-90 s | 4507 | 0.1109 | 0.1111 | 0.1100 | 0.1108 | 0.193 / 0.172 (258) |
| 70-80 s | 4072 | 0.1118 | 0.1122 | 0.1114 | 0.1152 | 0.207 / 0.254 (263) |
| 60-70 s | 3542 | 0.1105 | 0.1101 | 0.1114 | 0.1142 | 0.217 / 0.263 (339) |
| 50-60 s | 2537 | 0.1093 | 0.1086 | 0.1093 | 0.1117 | 0.193 / 0.228 (376) |
| 40-50 s | 1758 | 0.0947 | 0.0918 | 0.0960 | 0.0959 | 0.166 / 0.186 (307) |
| 30-40 s | 1201 | 0.0819 | 0.0775 | 0.0786 | 0.0729 | 0.151 / 0.114 (251) |
| 20-30 s | 645 | 0.0793 | 0.0722 | 0.0775 | 0.0736 | 0.124 / 0.123 (195) |
| 10-20 s | 304 | 0.0748 | 0.0682 | 0.0656 | 0.0815 | 0.093 / 0.120 (112) |

Rentabilité des signaux selon le moment du signal :

| Groupe | Achats | Gagnés | Résultat | Par $ | Creux | Pertes de suite max |
|---|---|---|---|---|---|---|
| signal 40-20 s | 13 | 23 % | **+26 $** | +13 % | −80 $ | 3 |
| signal 40-20 s — appr. | 8 | 25 % | **+68 $** | +44 % | −80 $ | 3 |
| signal 40-20 s — valid. | 5 | 20 % | **−41 $** | -95 % | −41 $ | 3 |
| signal 60-40 s | 42 | 38 % | **+414 $** | +52 % | −210 $ | 6 |
| signal 60-40 s — appr. | 26 | 42 % | **+318 $** | +74 % | −210 $ | 6 |
| signal 60-40 s — valid. | 16 | 31 % | **+96 $** | +26 % | −115 $ | 4 |
| signal 90-60 s | 85 | 53 % | **+1'882 $** | +102 % | −197 $ | 4 |
| signal 90-60 s — appr. | 48 | 46 % | **+912 $** | +100 % | −157 $ | 4 |
| signal 90-60 s — valid. | 37 | 62 % | **+970 $** | +104 % | −104 $ | 3 |

## A bis. Acheter tout de suite, attendre le prochain Chainlink, ou ne rien faire — par fenêtre (mêmes signaux)

| Fenêtre du signal | Signaux | Tout de suite | Attendre Chainlink | Achats après attente | Pertes évitées | Gains manqués (dont jackpots ≥ 5×) |
|---|---|---|---|---|---|---|
| 90-60 s | 85 | +1'882 $ | +1'164 $ | 34 | +191 $ | +1'129 $ (9) |
| 60-40 s | 42 | +414 $ | +573 $ | 13 | +319 $ | +640 $ (2) |
| 40-20 s | 13 | +26 $ | −75 $ | 6 | +44 $ | +176 $ (0) |

## B. Le bid et le spread de notre côté apportent-ils une information en plus de l'avantage ?

| Groupe | Achats | Gagnés | Résultat | Par $ | Creux | Pertes de suite max |
|---|---|---|---|---|---|---|
| spread ≤ 2 c | 117 | 41 % | **+2'091 $** | +79 % | −210 $ | 5 |
| spread ≤ 2 c — appr. | 71 | 39 % | **+1'236 $** | +87 % | −117 $ | 5 |
| spread ≤ 2 c — valid. | 46 | 43 % | **+855 $** | +69 % | −157 $ | 4 |
| spread 3-6 c | 17 | 65 % | **+220 $** | +165 % | −8 $ | 2 |
| spread 3-6 c — appr. | 6 | 50 % | **+52 $** | +149 % | −8 $ | 2 |
| spread 3-6 c — valid. | 11 | 73 % | **+169 $** | +170 % | −4 $ | 1 |
| spread > 6 c | 6 | 83 % | **+11 $** | +28 % | −18 $ | 1 |
| spread > 6 c — appr. | 5 | 80 % | **+10 $** | +26 % | −18 $ | 1 |
| spread > 6 c — valid. | 1 | 100 % | **+2 $** | +47 % | +0 $ | 0 |
| autres cas (idée 11) | 134 | 45 % | **+2'159 $** | +80 % | −165 $ | 5 |
| autres cas (idée 11) — appr. | 79 | 42 % | **+1'140 $** | +80 % | −123 $ | 5 |
| autres cas (idée 11) — valid. | 55 | 49 % | **+1'020 $** | +80 % | −156 $ | 4 |
| BAPT > 0 : bid monte plus que le vendeur (idée 13) | 4 | 75 % | **+106 $** | +183 % | −3 $ | 1 |
| BAPT > 0 : bid monte plus que le vendeur (idée 13) — appr. | 2 | 50 % | **+0 $** | +2 % | −3 $ | 1 |
| BAPT > 0 : bid monte plus que le vendeur (idée 13) — valid. | 2 | 100 % | **+106 $** | +199 % | +0 $ | 0 |
| BAPT ≈ 0 (idée 13) | 102 | 39 % | **+1'804 $** | +74 % | −252 $ | 5 |
| BAPT ≈ 0 (idée 13) — appr. | 63 | 40 % | **+1'098 $** | +82 % | −121 $ | 5 |
| BAPT ≈ 0 (idée 13) — valid. | 39 | 38 % | **+706 $** | +64 % | −252 $ | 4 |
| BAPT < 0 (idée 13) | 28 | 61 % | **+250 $** | +120 % | −34 $ | 4 |
| BAPT < 0 (idée 13) — appr. | 14 | 50 % | **+42 $** | +49 % | −34 $ | 4 |
| BAPT < 0 (idée 13) — valid. | 14 | 71 % | **+208 $** | +170 % | −4 $ | 1 |

## Idée 4-5. Les trois modèles d'accord ou dispersés au moment du signal

| Groupe | Achats | Gagnés | Résultat | Par $ | Creux | Pertes de suite max |
|---|---|---|---|---|---|---|
| dispersion > médiane | 70 | 50 % | **+1'108 $** | +76 % | −105 $ | 3 |
| dispersion > médiane — appr. | 41 | 54 % | **+750 $** | +106 % | −69 $ | 3 |
| dispersion > médiane — valid. | 29 | 45 % | **+358 $** | +47 % | −105 $ | 3 |
| dispersion ≤ médiane (0.087) | 70 | 41 % | **+1'215 $** | +89 % | −156 $ | 8 |
| dispersion ≤ médiane (0.087) — appr. | 41 | 32 % | **+548 $** | +70 % | −156 $ | 8 |
| dispersion ≤ médiane (0.087) — valid. | 29 | 55 % | **+668 $** | +115 % | −110 $ | 3 |

## C. Sortie par le contrat opposé : vente directe au bid contre « acheter l'opposé + fusionner » (positions des 140 signaux)

| Moment | Mesures | Vente directe (bid) | Voie synthétique (1 − vendeur opposé − frais) | Synthétique meilleure | Gain moyen quand meilleure | Règlement (garder) |
|---|---|---|---|---|---|---|
| +1 s | 140 | 0.353 | 0.353 | 42 | +0.0 c | 0.457 |
| +5 s | 138 | 0.383 | 0.383 | 33 | +0.0 c | 0.464 |
| +10 s | 135 | 0.388 | 0.388 | 44 | +0.0 c | 0.474 |
| +20 s | 116 | 0.471 | 0.471 | 33 | +0.0 c | 0.543 |

Verrouillage (idée 18) : acheter l'opposé à +k s et garder la paire = valeur 1 $ sûre, contre garder seul :

| Moment | Mesures | Gain verrouillé moyen par jeton | Gain moyen en gardant seul | Verrouillage meilleur (cas) |
|---|---|---|---|---|
| +1 s | 140 | +0.091 | +0.195 | 76 |
| +5 s | 138 | +0.118 | +0.198 | 74 |
| +10 s | 135 | +0.126 | +0.212 | 71 |
| +20 s | 116 | +0.189 | +0.261 | 53 |

## Idées 14 et 17. Incohérences entre les carnets Up et Down (toutes les mesures, 4 par seconde)

- Acheter Up + Down au vendeur coûte moins de 1 $ après frais : **1** mesures sur 69161 (1 cycles), gain total théorique 0.04 $ (en sommant toutes les mesures, donc très surestimé).
- Vendre Up + Down à l'acheteur rapporte plus de 1 $ après frais : **1** mesures (1 cycles).

## Idée 6. Le carnet est très sûr (côté opposé à 10 c ou moins) : le côté bon marché vaut-il plus que son prix ? (60-20 s, une mesure par cycle et par tranche)

| Notre probabilité pour le côté bon marché | Mesures | Prix moyen | Gagnés | Écart gagné − prix − frais |
|---|---|---|---|---|
| < prix | 563 | 0.023 | 1.2 % | -1.3 pts |
| prix à prix + 5 pts | 305 | 0.041 | 4.3 % | -0.1 pts |
| prix + 5 à 15 pts | 196 | 0.062 | 7.7 % | +1.0 pts |
| > prix + 15 pts | 86 | 0.073 | 14.0 % | +6.2 pts |

## Idée 8. Surface « prix × temps restant » sur TOUTES les cotations (une par cycle, par côté et par case) : gagné − prix − frais, en points

| Prix du contrat | 90-60 s appr. | 90-60 s valid. | 60-40 s appr. | 60-40 s valid. | 40-20 s appr. | 40-20 s valid. |
|---|---|---|---|---|---|---|
| 1-5 c | -1.3 (285) | -1.9 (187) | -1.2 (303) | -1.8 (218) | -1.7 (312) | -0.8 (225) |
| 5-15 c | +0.2 (205) | -0.9 (153) | +3.2 (131) | +1.8 (95) | +0.8 (70) | -3.3 (34) |
| 15-35 c | -1.4 (182) | -0.3 (136) | -0.3 (104) | +0.7 (62) | -1.9 (48) | -13.2 (24) |
| 35-65 c | -2.5 (176) | -4.6 (108) | -3.4 (92) | -4.7 (45) | -4.5 (40) | -6.4 (20) |
| 65-85 c | -2.7 (180) | -3.1 (132) | -5.3 (105) | -2.0 (59) | -2.4 (46) | +10.1 (23) |
| 85-95 c | -2.7 (187) | -3.3 (144) | -5.3 (117) | -5.0 (86) | -2.6 (62) | +2.5 (29) |
| 95-99 c | -0.2 (200) | +0.0 (157) | -1.4 (152) | -2.2 (107) | +2.0 (82) | -0.8 (57) |

Entre parenthèses : nombre de mesures. Une case n'est intéressante que si elle est positive en apprentissage ET en validation.