# Idees anti-pertes pour V1 — 12 jours (2026-09-23 -> 2026-10-04)
Entre parentheses : difference avec la reference. Gains pour 100 parts par trade (environ 55 $ de mise).

## BTC — 3295 cycles, 12 jours, 100 parts, retard 1 s

Seuils choisis sur les jours 1-8 ; les jours 9-12 n'ont jamais servi a les choisir.

| Idee | Trades | Gain net | Gain/jour | Pertes totales | Pire baisse | Gain/jour jours 1-8 | **Gain/jour jours 9-12 (jamais vus)** | Mise moy. |
|---|---|---|---|---|---|---|---|---|
| Reference V1 (stop -15 pts, sortie 0,90) | 1504 | +18009 $ (+0) | +1501 $ | -6900 $ (+0) | -120 $ | +1590 $ (+0) | **+1538 $ (+0)** | 55 $ |
| 3. Refuser si perp en avance dans notre sens > 0.44 pb (tiers haut) | 1156 | +12618 $ (-5390) | +1052 $ | -5717 $ (+1183) | -157 $ | +1090 $ (-499) | **+1133 $ (-405)** | 55 $ |
| 3. Refuser si perp en avance > 0.64 pb (20 % haut) | 1285 | +14701 $ (-3308) | +1225 $ | -6090 $ (+810) | -133 $ | +1299 $ (-291) | **+1252 $ (-286)** | 55 $ |
| 3. Refuser si perp en avance > 0.88 pb (10 % haut) | 1403 | +16595 $ (-1413) | +1383 $ | -6416 $ (+484) | -120 $ | +1484 $ (-106) | **+1373 $ (-165)** | 55 $ |
| 3. Refuser si perp en retard < -0.32 pb (20 % bas) | 1294 | +16801 $ (-1207) | +1400 $ | -5641 $ (+1260) | -119 $ | +1510 $ (-80) | **+1372 $ (-166)** | 55 $ |
| 3. Sortir si l'ecart perp-spot passe contre nous de 0.99 pb | 1504 | +16821 $ (-1188) | +1402 $ | -5163 $ (+1737) | -98 $ | +1486 $ (-103) | **+1432 $ (-105)** | 55 $ |
| 4. Refuser si gros ordre perp contre nous (5 s) > 79 k$ | 1183 | +14931 $ (-3077) | +1244 $ | -5619 $ (+1281) | -133 $ | +1323 $ (-267) | **+1265 $ (-273)** | 55 $ |
| 4. Refuser si gros ordre contre > 142 k$ | 1317 | +16353 $ (-1656) | +1363 $ | -6285 $ (+615) | -120 $ | +1448 $ (-141) | **+1385 $ (-153)** | 55 $ |
| 4. Refuser si gros ordre contre > 285 k$ | 1411 | +17009 $ (-999) | +1417 $ | -6686 $ (+214) | -120 $ | +1516 $ (-74) | **+1419 $ (-119)** | 55 $ |
| 4. Exiger un gros ordre pour nous (10 s) > 201 k$ | 901 | +11186 $ (-6823) | +932 $ | -3718 $ (+3182) | -85 $ | +969 $ (-621) | **+999 $ (-539)** | 55 $ |
| 4. Sortir si gros ordre contre nous > 142 k$ pendant le trade | 1504 | +14598 $ (-3410) | +1217 $ | -3215 $ (+3685) | -94 $ | +1266 $ (-323) | **+1298 $ (-239)** | 55 $ |
| 4. Sortir si gros ordre contre nous > 285 k$ pendant le trade | 1504 | +16340 $ (-1669) | +1362 $ | -4307 $ (+2593) | -61 $ | +1432 $ (-158) | **+1419 $ (-119)** | 55 $ |
| 5. Refuser si allers-retours (ratio 30 min < 1.36, 20 % bas) | 1164 | +13678 $ (-4331) | +1140 $ | -5174 $ (+1726) | -101 $ | +1327 $ (-263) | **+891 $ (-647)** | 55 $ |
| 5. Refuser si ratio 30 min < 1.47 (tiers bas) | 973 | +11102 $ (-6906) | +925 $ | -4419 $ (+2482) | -116 $ | +1115 $ (-474) | **+633 $ (-905)** | 55 $ |
| 5. Refuser si ratio 30 min < 1.60 (moitie basse) | 742 | +8263 $ (-9745) | +689 $ | -3577 $ (+3324) | -104 $ | +858 $ (-732) | **+408 $ (-1130)** | 55 $ |
| 5. Refuser si forte tendance (ratio > 1.84, controle) | 1248 | +15459 $ (-2550) | +1288 $ | -5604 $ (+1296) | -120 $ | +1336 $ (-253) | **+1386 $ (-152)** | 55 $ |
| 5. Refuser si ratio 1 h (pas 60 s) < 1.44 | 1177 | +13919 $ (-4089) | +1160 $ | -5350 $ (+1550) | -120 $ | +1316 $ (-274) | **+986 $ (-552)** | 55 $ |
| 5. Refuser si ratio 1 h < 1.59 | 991 | +12034 $ (-5974) | +1003 $ | -4490 $ (+2410) | -120 $ | +1142 $ (-447) | **+842 $ (-696)** | 55 $ |
| 6. Mise proportionnelle a l'avance du modele (meme mise moyenne) | 1504 | +21666 $ (+3657) | +1806 $ | -6214 $ (+686) | -154 $ | +1817 $ (+227) | **+2072 $ (+534)** | 57 $ |
| 6. Mise selon l'avance au carre (meme mise moyenne) | 1504 | +26192 $ (+8183) | +2183 $ | -5622 $ (+1278) | -328 $ | +2080 $ (+491) | **+2776 $ (+1238)** | 59 $ |
| 6. Demi-mise si avance < mediane, 1,5x sinon | 1504 | +20605 $ (+2597) | +1717 $ | -6319 $ (+582) | -113 $ | +1774 $ (+184) | **+1865 $ (+327)** | 56 $ |
| 7. Vendre la moitie a 0,70, le reste a 0,90 | 1504 | +13792 $ (-4216) | +1149 $ | -4282 $ (+2618) | -72 $ | +1240 $ (-349) | **+1124 $ (-414)** | 55 $ |
| 7. Vendre la moitie a 0,75, le reste a 0,90 | 1504 | +15147 $ (-2862) | +1262 $ | -5151 $ (+1749) | -69 $ | +1352 $ (-237) | **+1258 $ (-280)** | 55 $ |
| 7. Vendre 1/3 a 0,70, le reste a 0,90 | 1504 | +15197 $ (-2812) | +1266 $ | -4993 $ (+1907) | -80 $ | +1357 $ (-233) | **+1262 $ (-276)** | 55 $ |
| 7. Moitie a 0,70 + reste sorti a 0,56 s'il redescend | 1504 | +9898 $ (-8111) | +825 $ | -3998 $ (+2902) | -80 $ | +918 $ (-672) | **+742 $ (-795)** | 55 $ |
| 7. Stop suiveur seul : apres 0,75, sortir a 0,56 s'il redescend | 1504 | +13896 $ (-4113) | +1158 $ | -6899 $ (+1) | -80 $ | +1252 $ (-337) | **+1127 $ (-411)** | 55 $ |
| 7. Stop suiveur seul : apres 0,70, sortir a 0,56 s'il redescend | 1504 | +10474 $ (-7534) | +873 $ | -7223 $ (-322) | -126 $ | +961 $ (-629) | **+810 $ (-728)** | 55 $ |
| 1. Sortir si achats agressifs du cote oppose > 100 parts en 3 s | 1504 | +6651 $ (-11358) | +554 $ | -2574 $ (+4326) | -64 $ | +609 $ (-981) | **+518 $ (-1020)** | 55 $ |
| 1. Sortir si achats agressifs du cote oppose > 250 parts en 3 s | 1504 | +7621 $ (-10388) | +635 $ | -3219 $ (+3681) | -75 $ | +694 $ (-896) | **+602 $ (-936)** | 55 $ |
| 1. Sortir si achats agressifs du cote oppose > 500 parts en 3 s | 1504 | +10251 $ (-7758) | +854 $ | -4209 $ (+2692) | -90 $ | +909 $ (-681) | **+866 $ (-672)** | 55 $ |
| 1. Refuser si achats du cote oppose > 250 parts dans les 10 s avant | 573 | +6649 $ (-11360) | +554 $ | -2781 $ (+4119) | -104 $ | +583 $ (-1007) | **+578 $ (-960)** | 55 $ |

### Idee 7 — jusqu'ou le jeton est monte avant la sortie (reference)

| Issue | Trades | a touche 0,65 | 0,70 | 0,75 | 0,80 |
|---|---|---|---|---|---|
| fin gagnee | 26 | 26 (100 %) | 26 (100 %) | 26 (100 %) | 26 (100 %) |
| fin perdue | 4 | 4 (100 %) | 3 (75 %) | 2 (50 %) | 1 (25 %) |
| paire | 148 | 148 (100 %) | 139 (94 %) | 125 (84 %) | 95 (64 %) |
| sortie | 636 | 636 (100 %) | 636 (100 %) | 636 (100 %) | 636 (100 %) |
| stop | 690 | 516 (75 %) | 378 (55 %) | 236 (34 %) | 127 (18 %) |

Reperes (jours 1-8) : ecart perp-spot a l'entree mediane 0.19 pb ; plus gros ordre contre nous (5 s) median 30 k$ ; ratio de variance 30 min median 1.60, 1 h median 1.78 ; avance moyenne du modele 0.151.

## ETH — 3295 cycles, 12 jours, 100 parts, retard 1 s

Seuils choisis sur les jours 1-8 ; les jours 9-12 n'ont jamais servi a les choisir.

| Idee | Trades | Gain net | Gain/jour | Pertes totales | Pire baisse | Gain/jour jours 1-8 | **Gain/jour jours 9-12 (jamais vus)** | Mise moy. |
|---|---|---|---|---|---|---|---|---|
| Reference V1 (stop -15 pts, sortie 0,90) | 629 | +6484 $ (+0) | +540 $ | -3534 $ (+0) | -129 $ | +559 $ (+0) | **+586 $ (+0)** | 55 $ |
| 3. Refuser si perp en avance dans notre sens > 0.30 pb (tiers haut) | 459 | +4646 $ (-1838) | +387 $ | -2504 $ (+1029) | -116 $ | +405 $ (-153) | **+408 $ (-178)** | 55 $ |
| 3. Refuser si perp en avance > 0.52 pb (20 % haut) | 533 | +5038 $ (-1446) | +420 $ | -3197 $ (+337) | -129 $ | +438 $ (-121) | **+447 $ (-139)** | 55 $ |
| 3. Refuser si perp en avance > 0.77 pb (10 % haut) | 575 | +5774 $ (-710) | +481 $ | -3307 $ (+227) | -136 $ | +515 $ (-44) | **+481 $ (-105)** | 55 $ |
| 3. Refuser si perp en retard < -0.39 pb (20 % bas) | 518 | +5797 $ (-687) | +483 $ | -2839 $ (+695) | -137 $ | +507 $ (-52) | **+507 $ (-79)** | 55 $ |
| 3. Sortir si l'ecart perp-spot passe contre nous de 0.89 pb | 629 | +6505 $ (+21) | +542 $ | -2774 $ (+760) | -96 $ | +558 $ (-0) | **+592 $ (+6)** | 55 $ |
| 4. Refuser si gros ordre perp contre nous (5 s) > 59 k$ | 452 | +5280 $ (-1204) | +440 $ | -2463 $ (+1070) | -96 $ | +444 $ (-115) | **+503 $ (-83)** | 55 $ |
| 4. Refuser si gros ordre contre > 120 k$ | 528 | +5768 $ (-716) | +481 $ | -2992 $ (+542) | -106 $ | +488 $ (-71) | **+542 $ (-43)** | 55 $ |
| 4. Refuser si gros ordre contre > 257 k$ | 583 | +6288 $ (-196) | +524 $ | -3265 $ (+268) | -113 $ | +547 $ (-12) | **+556 $ (-30)** | 55 $ |
| 4. Exiger un gros ordre pour nous (10 s) > 139 k$ | 328 | +3193 $ (-3291) | +266 $ | -1805 $ (+1729) | -115 $ | +274 $ (-284) | **+290 $ (-295)** | 55 $ |
| 4. Sortir si gros ordre contre nous > 120 k$ pendant le trade | 629 | +6219 $ (-265) | +518 $ | -2156 $ (+1378) | -106 $ | +529 $ (-29) | **+576 $ (-9)** | 55 $ |
| 4. Sortir si gros ordre contre nous > 257 k$ pendant le trade | 629 | +6716 $ (+232) | +560 $ | -2746 $ (+788) | -129 $ | +570 $ (+11) | **+627 $ (+41)** | 55 $ |
| 5. Refuser si allers-retours (ratio 30 min < 1.19, 20 % bas) | 498 | +4748 $ (-1736) | +396 $ | -2935 $ (+599) | -168 $ | +431 $ (-128) | **+378 $ (-207)** | 55 $ |
| 5. Refuser si ratio 30 min < 1.29 (tiers bas) | 411 | +4125 $ (-2359) | +344 $ | -2416 $ (+1118) | -105 $ | +416 $ (-143) | **+233 $ (-353)** | 55 $ |
| 5. Refuser si ratio 30 min < 1.39 (moitie basse) | 300 | +2992 $ (-3491) | +249 $ | -1698 $ (+1836) | -84 $ | +300 $ (-259) | **+173 $ (-413)** | 55 $ |
| 5. Refuser si forte tendance (ratio > 1.61, controle) | 528 | +5743 $ (-741) | +479 $ | -2915 $ (+619) | -123 $ | +471 $ (-88) | **+574 $ (-12)** | 55 $ |
| 5. Refuser si ratio 1 h (pas 60 s) < 1.11 | 502 | +5065 $ (-1419) | +422 $ | -2929 $ (+605) | -134 $ | +455 $ (-104) | **+415 $ (-171)** | 55 $ |
| 5. Refuser si ratio 1 h < 1.23 | 417 | +4252 $ (-2232) | +354 $ | -2458 $ (+1075) | -150 $ | +398 $ (-160) | **+310 $ (-276)** | 55 $ |
| 6. Mise proportionnelle a l'avance du modele (meme mise moyenne) | 629 | +7797 $ (+1313) | +650 $ | -3456 $ (+78) | -242 $ | +617 $ (+58) | **+832 $ (+246)** | 57 $ |
| 6. Mise selon l'avance au carre (meme mise moyenne) | 629 | +9473 $ (+2989) | +789 $ | -3523 $ (+10) | -466 $ | +662 $ (+104) | **+1214 $ (+628)** | 59 $ |
| 6. Demi-mise si avance < mediane, 1,5x sinon | 629 | +7347 $ (+863) | +612 $ | -3396 $ (+137) | -157 $ | +619 $ (+61) | **+696 $ (+110)** | 56 $ |
| 7. Vendre la moitie a 0,70, le reste a 0,90 | 629 | +4962 $ (-1522) | +413 $ | -2339 $ (+1195) | -84 $ | +439 $ (-119) | **+421 $ (-165)** | 55 $ |
| 7. Vendre la moitie a 0,75, le reste a 0,90 | 629 | +5491 $ (-993) | +458 $ | -2711 $ (+823) | -98 $ | +479 $ (-79) | **+481 $ (-105)** | 55 $ |
| 7. Vendre 1/3 a 0,70, le reste a 0,90 | 629 | +5466 $ (-1018) | +456 $ | -2674 $ (+860) | -99 $ | +479 $ (-80) | **+476 $ (-110)** | 55 $ |
| 7. Moitie a 0,70 + reste sorti a 0,56 s'il redescend | 629 | +3906 $ (-2578) | +326 $ | -2264 $ (+1270) | -123 $ | +353 $ (-205) | **+313 $ (-272)** | 55 $ |
| 7. Stop suiveur seul : apres 0,75, sortir a 0,56 s'il redescend | 629 | +5211 $ (-1273) | +434 $ | -3484 $ (+50) | -139 $ | +471 $ (-87) | **+418 $ (-167)** | 55 $ |
| 7. Stop suiveur seul : apres 0,70, sortir a 0,56 s'il redescend | 629 | +4631 $ (-1853) | +386 $ | -3477 $ (+56) | -179 $ | +413 $ (-145) | **+385 $ (-200)** | 55 $ |
| 1. Sortir si achats agressifs du cote oppose > 100 parts en 3 s | 629 | +6059 $ (-425) | +505 $ | -2573 $ (+961) | -99 $ | +539 $ (-20) | **+508 $ (-78)** | 55 $ |
| 1. Sortir si achats agressifs du cote oppose > 250 parts en 3 s | 629 | +6401 $ (-83) | +533 $ | -3314 $ (+220) | -129 $ | +556 $ (-3) | **+568 $ (-18)** | 55 $ |
| 1. Sortir si achats agressifs du cote oppose > 500 parts en 3 s | 629 | +6502 $ (+19) | +542 $ | -3475 $ (+58) | -129 $ | +562 $ (+4) | **+583 $ (-3)** | 55 $ |
| 1. Refuser si achats du cote oppose > 250 parts dans les 10 s avant | 588 | +5969 $ (-514) | +497 $ | -3185 $ (+349) | -104 $ | +515 $ (-43) | **+537 $ (-49)** | 55 $ |

### Idee 7 — jusqu'ou le jeton est monte avant la sortie (reference)

| Issue | Trades | a touche 0,65 | 0,70 | 0,75 | 0,80 |
|---|---|---|---|---|---|
| fin gagnee | 30 | 30 (100 %) | 30 (100 %) | 30 (100 %) | 30 (100 %) |
| fin perdue | 5 | 4 (80 %) | 3 (60 %) | 2 (40 %) | 2 (40 %) |
| paire | 28 | 28 (100 %) | 28 (100 %) | 28 (100 %) | 24 (86 %) |
| sortie | 245 | 245 (100 %) | 245 (100 %) | 245 (100 %) | 245 (100 %) |
| stop | 321 | 239 (74 %) | 169 (53 %) | 118 (37 %) | 71 (22 %) |

Reperes (jours 1-8) : ecart perp-spot a l'entree mediane 0.04 pb ; plus gros ordre contre nous (5 s) median 29 k$ ; ratio de variance 30 min median 1.39, 1 h median 1.40 ; avance moyenne du modele 0.144.

Duree : 1434 s