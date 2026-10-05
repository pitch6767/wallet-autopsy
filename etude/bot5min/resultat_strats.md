# Strategies separees (idees 29 et 30) — 12 jours (2026-09-23 -> 2026-10-04)
100 parts. Retard 1 s. Aucun stop.

## BTC — 3283 cycles

### Idee 30 — acheter en fin de cycle entre 0,70 et 0,90, garder jusqu'a la fin

| Variante | Trades | Perdus | Gain net | Gain/jour | Pertes | Pire baisse | Gain/jour jours 1-8 | **Gain/jour jours 9-12** |
|---|---|---|---|---|---|---|---|---|
| 90 dernieres s, 0,70-0,85, SANS modele (controle) | 1423 | 319 | -1736 $ | -145 $ | -24672 $ | -2215 $ | -155 $ | **-145 $** |
| 90 dernieres s, 0.70-0.80, modele >= 0.93 | 387 | 48 | +3728 $ | +311 $ | -3722 $ | -203 $ | +368 $ | **+231 $** |
| 90 dernieres s, 0.70-0.80, modele >= 0.95 | 298 | 36 | +2988 $ | +249 $ | -2781 $ | -228 $ | +303 $ | **+166 $** |
| 90 dernieres s, 0.70-0.80, modele >= 0.97 | 189 | 15 | +2662 $ | +222 $ | -1165 $ | -185 $ | +242 $ | **+213 $** |
| 90 dernieres s, 0.80-0.85, modele >= 0.93 | 548 | 61 | +2747 $ | +229 $ | -5097 $ | -349 $ | +304 $ | **+93 $** |
| 90 dernieres s, 0.80-0.85, modele >= 0.95 | 421 | 43 | +2464 $ | +205 $ | -3604 $ | -383 $ | +274 $ | **+81 $** |
| 90 dernieres s, 0.80-0.85, modele >= 0.97 | 270 | 23 | +2027 $ | +169 $ | -1920 $ | -252 $ | +210 $ | **+102 $** |
| 90 dernieres s, 0.85-0.90, modele >= 0.93 | 928 | 83 | +1912 $ | +159 $ | -7364 $ | -687 $ | +227 $ | **+27 $** |
| 90 dernieres s, 0.85-0.90, modele >= 0.95 | 735 | 59 | +2143 $ | +179 $ | -5224 $ | -382 $ | +252 $ | **+37 $** |
| 90 dernieres s, 0.85-0.90, modele >= 0.97 | 532 | 41 | +1624 $ | +135 $ | -3654 $ | -415 $ | +185 $ | **+42 $** |
| 90 dernieres s, 0.70-0.85, modele >= 0.93 | 573 | 69 | +3652 $ | +304 $ | -5573 $ | -277 $ | +378 $ | **+184 $** |
| 90 dernieres s, 0.70-0.85, modele >= 0.95 | 446 | 50 | +3193 $ | +266 $ | -4034 $ | -315 $ | +336 $ | **+149 $** |
| 90 dernieres s, 0.70-0.85, modele >= 0.97 | 287 | 25 | +2721 $ | +227 $ | -2033 $ | -227 $ | +259 $ | **+192 $** |
| 90 dernieres s, 0.70-0.90, modele >= 0.93 | 953 | 98 | +3282 $ | +274 $ | -8329 $ | -624 $ | +361 $ | **+115 $** |
| 90 dernieres s, 0.70-0.90, modele >= 0.95 | 759 | 69 | +3410 $ | +284 $ | -5860 $ | -363 $ | +382 $ | **+105 $** |
| 90 dernieres s, 0.70-0.90, modele >= 0.97 | 548 | 44 | +2735 $ | +228 $ | -3807 $ | -348 $ | +271 $ | **+168 $** |
| 60 dernieres s, 0,70-0,85, modele >= 0,95 | 258 | 21 | +2746 $ | +229 $ | -1697 $ | -209 $ | +267 $ | **+180 $** |
| 120 dernieres s, 0,70-0,85, modele >= 0,95 | 652 | 84 | +3228 $ | +269 $ | -6831 $ | -404 $ | +319 $ | **+200 $** |
| 180 dernieres s, 0,70-0,85, modele >= 0,95 | 1016 | 124 | +5660 $ | +472 $ | -10087 $ | -397 $ | +507 $ | **+472 $** |

### Idee 29 — teneur de marche des deux cotes au prix du modele (aucun frais, paires fusionnees)

| Variante | Cycles servis | Cycles perdants | Gain net | Gain/jour | Pertes | Pire baisse | Paires moy. | Parts seules moy. | **Gain/jour jours 9-12** |
|---|---|---|---|---|---|---|---|---|---|
| marge 0.03, desequilibre max 50 parts, arret 10 s avant la fin | 3272 | 1445 | +2585 $ | +215 $ | -17838 $ | -2024 $ | 73 | 17 | **-317 $** |
| marge 0.03, desequilibre max 100 parts, arret 10 s avant la fin | 3272 | 1663 | -3458 $ | -288 $ | -33803 $ | -4960 $ | 79 | 21 | **-973 $** |
| marge 0.03, desequilibre max 50 parts, arret 60 s avant la fin | 3272 | 1440 | +2338 $ | +195 $ | -18311 $ | -2043 $ | 71 | 18 | **-324 $** |
| marge 0.03, desequilibre max 25 parts, arret 10 s avant la fin | 3272 | 1223 | +5704 $ | +475 $ | -8798 $ | -912 $ | 63 | 13 | **+81 $** |
| marge 0.05, desequilibre max 50 parts, arret 10 s avant la fin | 3269 | 1288 | +8749 $ | +729 $ | -17662 $ | -1109 $ | 63 | 23 | **+127 $** |
| marge 0.05, desequilibre max 100 parts, arret 10 s avant la fin | 3269 | 1594 | +2641 $ | +220 $ | -35409 $ | -2797 $ | 70 | 29 | **-538 $** |
| marge 0.05, desequilibre max 50 parts, arret 60 s avant la fin | 3269 | 1289 | +8185 $ | +682 $ | -18427 $ | -1156 $ | 60 | 25 | **+105 $** |
| marge 0.05, desequilibre max 25 parts, arret 10 s avant la fin | 3269 | 1077 | +10242 $ | +853 $ | -8231 $ | -321 $ | 51 | 17 | **+444 $** |
| marge 0.08, desequilibre max 50 parts, arret 10 s avant la fin | 3242 | 1185 | +14046 $ | +1171 $ | -17606 $ | -352 $ | 48 | 31 | **+730 $** |
| marge 0.08, desequilibre max 100 parts, arret 10 s avant la fin | 3242 | 1465 | +9375 $ | +781 $ | -36855 $ | -1561 $ | 57 | 42 | **+278 $** |
| marge 0.08, desequilibre max 50 parts, arret 60 s avant la fin | 3240 | 1196 | +12715 $ | +1060 $ | -19093 $ | -504 $ | 44 | 33 | **+611 $** |
| marge 0.08, desequilibre max 25 parts, arret 10 s avant la fin | 3242 | 954 | +13470 $ | +1123 $ | -7658 $ | -189 $ | 36 | 20 | **+811 $** |
| marge 0.12, desequilibre max 50 parts, arret 10 s avant la fin | 3080 | 1015 | +16493 $ | +1374 $ | -16852 $ | -220 $ | 31 | 38 | **+1195 $** |
| marge 0.12, desequilibre max 100 parts, arret 10 s avant la fin | 3080 | 1204 | +16997 $ | +1416 $ | -35144 $ | -1045 $ | 40 | 55 | **+1089 $** |
| marge 0.12, desequilibre max 50 parts, arret 60 s avant la fin | 3075 | 1037 | +14214 $ | +1185 $ | -19029 $ | -248 $ | 26 | 40 | **+965 $** |
| marge 0.12, desequilibre max 25 parts, arret 10 s avant la fin | 3080 | 888 | +13060 $ | +1088 $ | -7598 $ | -113 $ | 21 | 22 | **+997 $** |

## ETH — 3283 cycles

### Idee 30 — acheter en fin de cycle entre 0,70 et 0,90, garder jusqu'a la fin

| Variante | Trades | Perdus | Gain net | Gain/jour | Pertes | Pire baisse | Gain/jour jours 1-8 | **Gain/jour jours 9-12** |
|---|---|---|---|---|---|---|---|---|
| 90 dernieres s, 0,70-0,85, SANS modele (controle) | 1472 | 296 | +1562 $ | +130 $ | -22978 $ | -1863 $ | -79 $ | **+646 $** |
| 90 dernieres s, 0.70-0.80, modele >= 0.93 | 204 | 22 | +2346 $ | +196 $ | -1688 $ | -329 $ | +167 $ | **+298 $** |
| 90 dernieres s, 0.70-0.80, modele >= 0.95 | 125 | 12 | +1588 $ | +132 $ | -913 $ | -163 $ | +121 $ | **+181 $** |
| 90 dernieres s, 0.70-0.80, modele >= 0.97 | 79 | 6 | +1162 $ | +97 $ | -452 $ | -122 $ | +80 $ | **+153 $** |
| 90 dernieres s, 0.80-0.85, modele >= 0.93 | 345 | 25 | +2966 $ | +247 $ | -2098 $ | -434 $ | +227 $ | **+338 $** |
| 90 dernieres s, 0.80-0.85, modele >= 0.95 | 237 | 14 | +2334 $ | +195 $ | -1179 $ | -284 $ | +193 $ | **+232 $** |
| 90 dernieres s, 0.80-0.85, modele >= 0.97 | 134 | 7 | +1437 $ | +120 $ | -595 $ | -240 $ | +125 $ | **+128 $** |
| 90 dernieres s, 0.85-0.90, modele >= 0.93 | 762 | 51 | +3410 $ | +284 $ | -4538 $ | -415 $ | +262 $ | **+386 $** |
| 90 dernieres s, 0.85-0.90, modele >= 0.95 | 574 | 34 | +2943 $ | +245 $ | -3024 $ | -453 $ | +251 $ | **+275 $** |
| 90 dernieres s, 0.85-0.90, modele >= 0.97 | 345 | 19 | +1899 $ | +158 $ | -1686 $ | -367 $ | +186 $ | **+121 $** |
| 90 dernieres s, 0.70-0.85, modele >= 0.93 | 404 | 34 | +3882 $ | +324 $ | -2747 $ | -485 $ | +312 $ | **+408 $** |
| 90 dernieres s, 0.70-0.85, modele >= 0.95 | 287 | 23 | +2752 $ | +229 $ | -1861 $ | -334 $ | +231 $ | **+265 $** |
| 90 dernieres s, 0.70-0.85, modele >= 0.97 | 167 | 12 | +1802 $ | +150 $ | -972 $ | -254 $ | +153 $ | **+171 $** |
| 90 dernieres s, 0.70-0.90, modele >= 0.93 | 820 | 59 | +4952 $ | +413 $ | -5067 $ | -349 $ | +381 $ | **+560 $** |
| 90 dernieres s, 0.70-0.90, modele >= 0.95 | 622 | 41 | +3918 $ | +327 $ | -3535 $ | -369 $ | +326 $ | **+386 $** |
| 90 dernieres s, 0.70-0.90, modele >= 0.97 | 381 | 23 | +2634 $ | +220 $ | -1982 $ | -337 $ | +238 $ | **+216 $** |
| 60 dernieres s, 0,70-0,85, modele >= 0,95 | 165 | 13 | +1627 $ | +136 $ | -1036 $ | -139 $ | +147 $ | **+132 $** |
| 120 dernieres s, 0,70-0,85, modele >= 0,95 | 404 | 37 | +3285 $ | +274 $ | -3050 $ | -403 $ | +301 $ | **+258 $** |
| 180 dernieres s, 0,70-0,85, modele >= 0,95 | 610 | 65 | +4039 $ | +337 $ | -5342 $ | -324 $ | +348 $ | **+370 $** |

### Idee 29 — teneur de marche des deux cotes au prix du modele (aucun frais, paires fusionnees)

| Variante | Cycles servis | Cycles perdants | Gain net | Gain/jour | Pertes | Pire baisse | Paires moy. | Parts seules moy. | **Gain/jour jours 9-12** |
|---|---|---|---|---|---|---|---|---|---|
| marge 0.03, desequilibre max 50 parts, arret 10 s avant la fin | 3270 | 1568 | -3864 $ | -322 $ | -26312 $ | -4808 $ | 50 | 30 | **-637 $** |
| marge 0.03, desequilibre max 100 parts, arret 10 s avant la fin | 3270 | 1614 | -8156 $ | -680 $ | -43387 $ | -8735 $ | 56 | 42 | **-952 $** |
| marge 0.03, desequilibre max 50 parts, arret 60 s avant la fin | 3270 | 1539 | -3668 $ | -306 $ | -26936 $ | -4725 $ | 46 | 32 | **-711 $** |
| marge 0.03, desequilibre max 25 parts, arret 10 s avant la fin | 3270 | 1484 | -194 $ | -16 $ | -13735 $ | -1422 $ | 41 | 19 | **-263 $** |
| marge 0.05, desequilibre max 50 parts, arret 10 s avant la fin | 3235 | 1421 | -30 $ | -2 $ | -24603 $ | -2067 $ | 37 | 34 | **-281 $** |
| marge 0.05, desequilibre max 100 parts, arret 10 s avant la fin | 3235 | 1481 | -3554 $ | -296 $ | -41556 $ | -5226 $ | 42 | 50 | **-603 $** |
| marge 0.05, desequilibre max 50 parts, arret 60 s avant la fin | 3235 | 1408 | -182 $ | -15 $ | -25625 $ | -2198 $ | 32 | 36 | **-369 $** |
| marge 0.05, desequilibre max 25 parts, arret 10 s avant la fin | 3235 | 1358 | +2414 $ | +201 $ | -12520 $ | -1067 $ | 29 | 20 | **-11 $** |
| marge 0.08, desequilibre max 50 parts, arret 10 s avant la fin | 3052 | 1211 | +4655 $ | +388 $ | -20116 $ | -1114 $ | 23 | 36 | **+74 $** |
| marge 0.08, desequilibre max 100 parts, arret 10 s avant la fin | 3052 | 1242 | +3299 $ | +275 $ | -34481 $ | -2021 $ | 27 | 53 | **-141 $** |
| marge 0.08, desequilibre max 50 parts, arret 60 s avant la fin | 3036 | 1180 | +4241 $ | +353 $ | -20985 $ | -1145 $ | 18 | 37 | **+54 $** |
| marge 0.08, desequilibre max 25 parts, arret 10 s avant la fin | 3052 | 1187 | +4635 $ | +386 $ | -10142 $ | -491 $ | 18 | 21 | **+187 $** |
| marge 0.12, desequilibre max 50 parts, arret 10 s avant la fin | 2490 | 940 | +6077 $ | +506 $ | -14249 $ | -605 $ | 14 | 34 | **+195 $** |
| marge 0.12, desequilibre max 100 parts, arret 10 s avant la fin | 2490 | 965 | +5851 $ | +488 $ | -24258 $ | -1148 $ | 17 | 51 | **+22 $** |
| marge 0.12, desequilibre max 50 parts, arret 60 s avant la fin | 2410 | 892 | +4652 $ | +388 $ | -14352 $ | -595 $ | 8 | 33 | **+94 $** |
| marge 0.12, desequilibre max 25 parts, arret 10 s avant la fin | 2490 | 916 | +4935 $ | +411 $ | -7382 $ | -287 $ | 10 | 20 | **+230 $** |

## SOL — 3282 cycles

### Idee 30 — acheter en fin de cycle entre 0,70 et 0,90, garder jusqu'a la fin

| Variante | Trades | Perdus | Gain net | Gain/jour | Pertes | Pire baisse | Gain/jour jours 1-8 | **Gain/jour jours 9-12** |
|---|---|---|---|---|---|---|---|---|
| 90 dernieres s, 0,70-0,85, SANS modele (controle) | 1398 | 310 | -1564 $ | -130 $ | -24152 $ | -1786 $ | -169 $ | **-63 $** |
| 90 dernieres s, 0.70-0.80, modele >= 0.93 | 73 | 3 | +1381 $ | +115 $ | -235 $ | -154 $ | +128 $ | **+106 $** |
| 90 dernieres s, 0.70-0.80, modele >= 0.95 | 49 | 3 | +833 $ | +69 $ | -235 $ | -154 $ | +76 $ | **+67 $** |
| 90 dernieres s, 0.70-0.80, modele >= 0.97 | 24 | 0 | +576 $ | +48 $ | +0 $ | -0 $ | +58 $ | **+34 $** |
| 90 dernieres s, 0.80-0.85, modele >= 0.93 | 113 | 3 | +1478 $ | +123 $ | -252 $ | -86 $ | +136 $ | **+116 $** |
| 90 dernieres s, 0.80-0.85, modele >= 0.95 | 61 | 2 | +769 $ | +64 $ | -166 $ | -84 $ | +73 $ | **+54 $** |
| 90 dernieres s, 0.80-0.85, modele >= 0.97 | 31 | 0 | +490 $ | +41 $ | +0 $ | -0 $ | +46 $ | **+35 $** |
| 90 dernieres s, 0.85-0.90, modele >= 0.93 | 255 | 11 | +1690 $ | +141 $ | -984 $ | -167 $ | +130 $ | **+192 $** |
| 90 dernieres s, 0.85-0.90, modele >= 0.95 | 130 | 5 | +921 $ | +77 $ | -442 $ | -158 $ | +83 $ | **+77 $** |
| 90 dernieres s, 0.85-0.90, modele >= 0.97 | 59 | 1 | +546 $ | +45 $ | -89 $ | -89 $ | +43 $ | **+59 $** |
| 90 dernieres s, 0.70-0.85, modele >= 0.93 | 154 | 5 | +2365 $ | +197 $ | -406 $ | -86 $ | +218 $ | **+184 $** |
| 90 dernieres s, 0.70-0.85, modele >= 0.95 | 92 | 4 | +1377 $ | +115 $ | -320 $ | -124 $ | +124 $ | **+114 $** |
| 90 dernieres s, 0.70-0.85, modele >= 0.97 | 47 | 0 | +921 $ | +77 $ | +0 $ | -0 $ | +86 $ | **+69 $** |
| 90 dernieres s, 0.70-0.90, modele >= 0.93 | 318 | 13 | +3032 $ | +253 $ | -1137 $ | -165 $ | +265 $ | **+268 $** |
| 90 dernieres s, 0.70-0.90, modele >= 0.95 | 180 | 7 | +1902 $ | +158 $ | -595 $ | -133 $ | +177 $ | **+142 $** |
| 90 dernieres s, 0.70-0.90, modele >= 0.97 | 85 | 1 | +1180 $ | +98 $ | -89 $ | -89 $ | +108 $ | **+94 $** |
| 60 dernieres s, 0,70-0,85, modele >= 0,95 | 73 | 4 | +1019 $ | +85 $ | -320 $ | -124 $ | +91 $ | **+86 $** |
| 120 dernieres s, 0,70-0,85, modele >= 0,95 | 98 | 4 | +1464 $ | +122 $ | -320 $ | -109 $ | +134 $ | **+114 $** |
| 180 dernieres s, 0,70-0,85, modele >= 0,95 | 109 | 6 | +1443 $ | +120 $ | -488 $ | -95 $ | +148 $ | **+75 $** |

### Idee 29 — teneur de marche des deux cotes au prix du modele (aucun frais, paires fusionnees)

| Variante | Cycles servis | Cycles perdants | Gain net | Gain/jour | Pertes | Pire baisse | Paires moy. | Parts seules moy. | **Gain/jour jours 9-12** |
|---|---|---|---|---|---|---|---|---|---|
| marge 0.03, desequilibre max 50 parts, arret 10 s avant la fin | 3232 | 1611 | +697 $ | +58 $ | -20735 $ | -1800 $ | 37 | 31 | **-414 $** |
| marge 0.03, desequilibre max 100 parts, arret 10 s avant la fin | 3232 | 1595 | +538 $ | +45 $ | -30777 $ | -2318 $ | 41 | 43 | **-575 $** |
| marge 0.03, desequilibre max 50 parts, arret 60 s avant la fin | 3232 | 1622 | +611 $ | +51 $ | -21576 $ | -1835 $ | 31 | 33 | **-430 $** |
| marge 0.03, desequilibre max 25 parts, arret 10 s avant la fin | 3232 | 1646 | +1242 $ | +104 $ | -11678 $ | -1341 $ | 31 | 19 | **-275 $** |
| marge 0.05, desequilibre max 50 parts, arret 10 s avant la fin | 3095 | 1562 | +3194 $ | +266 $ | -18041 $ | -1164 $ | 26 | 31 | **-98 $** |
| marge 0.05, desequilibre max 100 parts, arret 10 s avant la fin | 3095 | 1560 | +3572 $ | +298 $ | -26844 $ | -1283 $ | 28 | 43 | **-81 $** |
| marge 0.05, desequilibre max 50 parts, arret 60 s avant la fin | 3087 | 1576 | +3040 $ | +253 $ | -18523 $ | -1136 $ | 19 | 33 | **-96 $** |
| marge 0.05, desequilibre max 25 parts, arret 10 s avant la fin | 3095 | 1542 | +3181 $ | +265 $ | -9990 $ | -715 $ | 21 | 20 | **+3 $** |
| marge 0.08, desequilibre max 50 parts, arret 10 s avant la fin | 2574 | 1294 | +5599 $ | +467 $ | -12553 $ | -317 $ | 16 | 30 | **+178 $** |
| marge 0.08, desequilibre max 100 parts, arret 10 s avant la fin | 2574 | 1287 | +6372 $ | +531 $ | -18437 $ | -456 $ | 18 | 41 | **+226 $** |
| marge 0.08, desequilibre max 50 parts, arret 60 s avant la fin | 2532 | 1274 | +5333 $ | +444 $ | -12138 $ | -295 $ | 9 | 29 | **+162 $** |
| marge 0.08, desequilibre max 25 parts, arret 10 s avant la fin | 2574 | 1263 | +4579 $ | +382 $ | -7151 $ | -218 $ | 13 | 19 | **+169 $** |
| marge 0.12, desequilibre max 50 parts, arret 10 s avant la fin | 1796 | 907 | +4874 $ | +406 $ | -7576 $ | -175 $ | 10 | 29 | **+278 $** |
| marge 0.12, desequilibre max 100 parts, arret 10 s avant la fin | 1796 | 921 | +5539 $ | +462 $ | -11386 $ | -296 $ | 11 | 41 | **+274 $** |
| marge 0.12, desequilibre max 50 parts, arret 60 s avant la fin | 1614 | 814 | +3950 $ | +329 $ | -6080 $ | -223 $ | 4 | 25 | **+267 $** |
| marge 0.12, desequilibre max 25 parts, arret 10 s avant la fin | 1796 | 876 | +3889 $ | +324 $ | -4384 $ | -95 $ | 8 | 18 | **+228 $** |

## XRP — 3283 cycles

### Idee 30 — acheter en fin de cycle entre 0,70 et 0,90, garder jusqu'a la fin

| Variante | Trades | Perdus | Gain net | Gain/jour | Pertes | Pire baisse | Gain/jour jours 1-8 | **Gain/jour jours 9-12** |
|---|---|---|---|---|---|---|---|---|
| 90 dernieres s, 0,70-0,85, SANS modele (controle) | 1257 | 273 | -901 $ | -75 $ | -21303 $ | -2574 $ | -68 $ | **-105 $** |
| 90 dernieres s, 0.70-0.80, modele >= 0.93 | 73 | 7 | +962 $ | +80 $ | -533 $ | -274 $ | +101 $ | **+46 $** |
| 90 dernieres s, 0.70-0.80, modele >= 0.95 | 48 | 4 | +695 $ | +58 $ | -306 $ | -199 $ | +79 $ | **+18 $** |
| 90 dernieres s, 0.70-0.80, modele >= 0.97 | 29 | 3 | +375 $ | +31 $ | -228 $ | -199 $ | +55 $ | **-20 $** |
| 90 dernieres s, 0.80-0.85, modele >= 0.93 | 114 | 8 | +1006 $ | +84 $ | -681 $ | -257 $ | +92 $ | **+79 $** |
| 90 dernieres s, 0.80-0.85, modele >= 0.95 | 65 | 3 | +737 $ | +61 $ | -257 $ | -91 $ | +71 $ | **+49 $** |
| 90 dernieres s, 0.80-0.85, modele >= 0.97 | 34 | 2 | +351 $ | +29 $ | -171 $ | -171 $ | +45 $ | **-3 $** |
| 90 dernieres s, 0.85-0.90, modele >= 0.93 | 287 | 16 | +1532 $ | +128 $ | -1413 $ | -285 $ | +119 $ | **+170 $** |
| 90 dernieres s, 0.85-0.90, modele >= 0.95 | 170 | 4 | +1452 $ | +121 $ | -356 $ | -91 $ | +112 $ | **+164 $** |
| 90 dernieres s, 0.85-0.90, modele >= 0.97 | 92 | 2 | +796 $ | +66 $ | -176 $ | -90 $ | +66 $ | **+79 $** |
| 90 dernieres s, 0.70-0.85, modele >= 0.93 | 156 | 12 | +1708 $ | +142 $ | -968 $ | -228 $ | +167 $ | **+109 $** |
| 90 dernieres s, 0.70-0.85, modele >= 0.95 | 94 | 5 | +1305 $ | +109 $ | -392 $ | -153 $ | +127 $ | **+84 $** |
| 90 dernieres s, 0.70-0.85, modele >= 0.97 | 53 | 3 | +755 $ | +63 $ | -228 $ | -199 $ | +87 $ | **+16 $** |
| 90 dernieres s, 0.70-0.90, modele >= 0.93 | 355 | 22 | +2604 $ | +217 $ | -1861 $ | -274 $ | +246 $ | **+187 $** |
| 90 dernieres s, 0.70-0.90, modele >= 0.95 | 215 | 7 | +2266 $ | +189 $ | -572 $ | -108 $ | +199 $ | **+199 $** |
| 90 dernieres s, 0.70-0.90, modele >= 0.97 | 121 | 4 | +1321 $ | +110 $ | -317 $ | -121 $ | +125 $ | **+94 $** |
| 60 dernieres s, 0,70-0,85, modele >= 0,95 | 64 | 3 | +949 $ | +79 $ | -234 $ | -86 $ | +101 $ | **+41 $** |
| 120 dernieres s, 0,70-0,85, modele >= 0,95 | 114 | 6 | +1525 $ | +127 $ | -477 $ | -238 $ | +147 $ | **+102 $** |
| 180 dernieres s, 0,70-0,85, modele >= 0,95 | 133 | 8 | +1628 $ | +136 $ | -644 $ | -238 $ | +160 $ | **+103 $** |

### Idee 29 — teneur de marche des deux cotes au prix du modele (aucun frais, paires fusionnees)

| Variante | Cycles servis | Cycles perdants | Gain net | Gain/jour | Pertes | Pire baisse | Paires moy. | Parts seules moy. | **Gain/jour jours 9-12** |
|---|---|---|---|---|---|---|---|---|---|
| marge 0.03, desequilibre max 50 parts, arret 10 s avant la fin | 3144 | 1540 | -590 $ | -49 $ | -17605 $ | -1565 $ | 21 | 30 | **-286 $** |
| marge 0.03, desequilibre max 100 parts, arret 10 s avant la fin | 3144 | 1539 | -1405 $ | -117 $ | -24048 $ | -1689 $ | 22 | 40 | **-205 $** |
| marge 0.03, desequilibre max 50 parts, arret 60 s avant la fin | 3140 | 1498 | +721 $ | +60 $ | -16792 $ | -1039 $ | 15 | 28 | **-76 $** |
| marge 0.03, desequilibre max 25 parts, arret 10 s avant la fin | 3144 | 1525 | +306 $ | +25 $ | -10606 $ | -1204 $ | 18 | 19 | **-217 $** |
| marge 0.05, desequilibre max 50 parts, arret 10 s avant la fin | 2873 | 1389 | +1535 $ | +128 $ | -13895 $ | -1000 $ | 14 | 28 | **-121 $** |
| marge 0.05, desequilibre max 100 parts, arret 10 s avant la fin | 2873 | 1401 | +651 $ | +54 $ | -19132 $ | -1431 $ | 15 | 37 | **-118 $** |
| marge 0.05, desequilibre max 50 parts, arret 60 s avant la fin | 2847 | 1328 | +2317 $ | +193 $ | -12692 $ | -621 $ | 9 | 25 | **+42 $** |
| marge 0.05, desequilibre max 25 parts, arret 10 s avant la fin | 2873 | 1375 | +1711 $ | +143 $ | -8513 $ | -698 $ | 12 | 18 | **-80 $** |
| marge 0.08, desequilibre max 50 parts, arret 10 s avant la fin | 2228 | 1106 | +2119 $ | +177 $ | -9352 $ | -901 $ | 8 | 25 | **-94 $** |
| marge 0.08, desequilibre max 100 parts, arret 10 s avant la fin | 2228 | 1118 | +1566 $ | +130 $ | -12867 $ | -1430 $ | 9 | 34 | **-167 $** |
| marge 0.08, desequilibre max 50 parts, arret 60 s avant la fin | 2111 | 1013 | +2398 $ | +200 $ | -7614 $ | -467 $ | 4 | 21 | **+12 $** |
| marge 0.08, desequilibre max 25 parts, arret 10 s avant la fin | 2228 | 1084 | +2057 $ | +171 $ | -5835 $ | -472 $ | 7 | 17 | **-25 $** |
| marge 0.12, desequilibre max 50 parts, arret 10 s avant la fin | 1499 | 752 | +2027 $ | +169 $ | -5618 $ | -672 $ | 5 | 24 | **-2 $** |
| marge 0.12, desequilibre max 100 parts, arret 10 s avant la fin | 1499 | 757 | +1321 $ | +110 $ | -8093 $ | -1164 $ | 5 | 33 | **-120 $** |
| marge 0.12, desequilibre max 50 parts, arret 60 s avant la fin | 1228 | 585 | +1768 $ | +147 $ | -3432 $ | -293 $ | 2 | 17 | **+38 $** |
| marge 0.12, desequilibre max 25 parts, arret 10 s avant la fin | 1499 | 729 | +2052 $ | +171 $ | -3406 $ | -327 $ | 4 | 16 | **+39 $** |

Duree : 1960 s