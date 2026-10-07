# Se rapprocher de l'achat a l'entree des « vrais » desaccords — vrais carnets du bot, 4 mesures/s

Toutes les regles sont causales (decision avec ce qu'on sait a ce moment-la). 50 $ par trade, frais compris. « Sans top 3 » = resultat sans les 3 meilleurs trades.

## BTC — 325 desaccords >= 0,20

| Regle | Trades | 1re moitie | 2e moitie | **Total** | Par trade | Sans top 3 |
|---|---|---|---|---|---|---|
| REFERENCE : tout acheter a l'entree, garder | 325 | -643 $ | +2196 $ | **+1553 $** | +4.8 $ | -1509 $ |

### A. Achat immediat, sortie au meilleur acheteur si le desaccord se revele faux

| Regle | Trades | 1re moitie | 2e moitie | **Total** | Par trade | Sans top 3 |
|---|---|---|---|---|---|---|
| sortie a 1 s si modele -3 c | 325 | -270 $ | +1561 $ | **+1291 $** | +4.0 $ | -1771 $ |
| sortie a 2 s si modele -3 c | 325 | -285 $ | +1373 $ | **+1088 $** | +3.3 $ | -1974 $ |
| sortie a 3 s si modele -3 c | 325 | -311 $ | +1952 $ | **+1640 $** | +5.0 $ | -1422 $ |
| sortie a 5 s si modele -3 c | 325 | -173 $ | +1111 $ | **+938 $** | +2.9 $ | -2124 $ |
| sortie a 10 s si modele -3 c | 325 | -490 $ | +1724 $ | **+1234 $** | +3.8 $ | -1772 $ |
| sortie a 1 s si Poly n'a pas monte de 3 c | 325 | -1139 $ | -23 $ | **-1162 $** | -3.6 $ | -2374 $ |
| sortie a 2 s si Poly n'a pas monte de 3 c | 325 | -1204 $ | +346 $ | **-858 $** | -2.6 $ | -2069 $ |
| sortie a 3 s si Poly n'a pas monte de 3 c | 325 | -1500 $ | +327 $ | **-1173 $** | -3.6 $ | -2385 $ |
| sortie a 5 s si Poly n'a pas monte de 3 c | 325 | -1497 $ | +122 $ | **-1375 $** | -4.2 $ | -2586 $ |
| sortie a 10 s si Poly n'a pas monte de 3 c | 325 | -396 $ | +1472 $ | **+1076 $** | +3.3 $ | -1930 $ |
| sortie a 1 s si modele -3 c OU Poly pas monte | 325 | -1276 $ | +187 $ | **-1089 $** | -3.4 $ | -2300 $ |
| sortie a 2 s si modele -3 c OU Poly pas monte | 325 | -1287 $ | +183 $ | **-1103 $** | -3.4 $ | -2232 $ |
| sortie a 3 s si modele -3 c OU Poly pas monte | 325 | -1444 $ | +165 $ | **-1279 $** | -3.9 $ | -2407 $ |
| sortie a 5 s si modele -3 c OU Poly pas monte | 325 | -1365 $ | +135 $ | **-1231 $** | -3.8 $ | -2442 $ |
| sortie a 10 s si modele -3 c OU Poly pas monte | 325 | -264 $ | +1521 $ | **+1256 $** | +3.9 $ | -1750 $ |

### B. Achat aux premiers signes (Polymarket monte de x c vers le modele, modele stable, dans les W s)

| Regle | Trades | 1re moitie | 2e moitie | **Total** | Par trade | Sans top 3 |
|---|---|---|---|---|---|---|
| W 1 s, x 1 c | 94 | -579 $ | +679 $ | **+101 $** | +1.1 $ | -839 $ |
| W 1 s, x 2 c | 67 | -506 $ | +879 $ | **+374 $** | +5.6 $ | -494 $ |
| W 1 s, x 3 c | 53 | -212 $ | +650 $ | **+438 $** | +8.3 $ | -430 $ |
| W 1 s, x 5 c | 32 | -130 $ | +74 $ | **-56 $** | -1.7 $ | -576 $ |
| W 2 s, x 1 c | 125 | -629 $ | +569 $ | **-61 $** | -0.5 $ | -1000 $ |
| W 2 s, x 2 c | 86 | -515 $ | +751 $ | **+235 $** | +2.7 $ | -632 $ |
| W 2 s, x 3 c | 70 | -168 $ | +734 $ | **+566 $** | +8.1 $ | -302 $ |
| W 2 s, x 5 c | 45 | -132 $ | +590 $ | **+458 $** | +10.2 $ | -289 $ |
| W 3 s, x 1 c | 153 | -429 $ | +799 $ | **+370 $** | +2.4 $ | -713 $ |
| W 3 s, x 2 c | 100 | -737 $ | +537 $ | **-200 $** | -2.0 $ | -1067 $ |
| W 3 s, x 3 c | 80 | -112 $ | +626 $ | **+514 $** | +6.4 $ | -354 $ |
| W 3 s, x 5 c | 55 | -238 $ | +568 $ | **+331 $** | +6.0 $ | -416 $ |
| W 5 s, x 1 c | 165 | -258 $ | +892 $ | **+634 $** | +3.8 $ | -448 $ |
| W 5 s, x 2 c | 113 | -818 $ | +684 $ | **-135 $** | -1.2 $ | -1047 $ |
| W 5 s, x 3 c | 92 | -141 $ | +748 $ | **+608 $** | +6.6 $ | -281 $ |
| W 5 s, x 5 c | 63 | -61 $ | +358 $ | **+297 $** | +4.7 $ | -449 $ |
| W 10 s, x 1 c | 194 | -257 $ | +1148 $ | **+891 $** | +4.6 $ | -389 $ |
| W 10 s, x 2 c | 147 | -798 $ | +1348 $ | **+550 $** | +3.7 $ | -588 $ |
| W 10 s, x 3 c | 128 | -405 $ | +1208 $ | **+803 $** | +6.3 $ | -137 $ |
| W 10 s, x 5 c | 90 | +42 $ | +773 $ | **+816 $** | +9.1 $ | -77 $ |

### C. Filtre bourses a l'entree (3 s avant), achat immediat, garder

| Regle | Trades | 1re moitie | 2e moitie | **Total** | Par trade | Sans top 3 |
|---|---|---|---|---|---|---|
| aucun | 325 | -643 $ | +2196 $ | **+1553 $** | +4.8 $ | -1509 $ |
| Binance avec nous | 72 | +1953 $ | +1765 $ | **+3719 $** | +51.6 $ | +1258 $ |
| perp avec nous | 84 | +1301 $ | +1307 $ | **+2609 $** | +31.1 $ | +147 $ |
| Binance ou perp avec nous | 104 | +1360 $ | +1887 $ | **+3247 $** | +31.2 $ | +786 $ |
| Binance et perp >= 0 | 122 | +849 $ | +2199 $ | **+3048 $** | +25.0 $ | +42 $ |
| 3 bourses sur 4 avec nous | 54 | +1750 $ | +768 $ | **+2518 $** | +46.6 $ | +57 $ |
| aucune bourse contre nous | 86 | +1558 $ | +1664 $ | **+3222 $** | +37.5 $ | +216 $ |

### D. Filtre bourses + sortie si faux

| Regle | Trades | 1re moitie | 2e moitie | **Total** | Par trade | Sans top 3 |
|---|---|---|---|---|---|---|
| Binance ou perp avec nous + sortie 3 s (retombe) | 104 | +1283 $ | +1763 $ | **+3046 $** | +29.3 $ | +585 $ |
| Binance ou perp avec nous + sortie 5 s (retombe) | 104 | +1702 $ | +1273 $ | **+2975 $** | +28.6 $ | +514 $ |
| Binance ou perp avec nous + sortie 5 s (les_deux) | 104 | +411 $ | +1193 $ | **+1604 $** | +15.4 $ | +392 $ |
| Binance ou perp avec nous + sortie 10 s (pas_rejoint) | 104 | +1650 $ | +1170 $ | **+2819 $** | +27.1 $ | +358 $ |
| aucune bourse contre nous + sortie 3 s (retombe) | 86 | +1539 $ | +1880 $ | **+3419 $** | +39.8 $ | +413 $ |
| aucune bourse contre nous + sortie 5 s (retombe) | 86 | +1646 $ | +1226 $ | **+2872 $** | +33.4 $ | -135 $ |
| aucune bourse contre nous + sortie 5 s (les_deux) | 86 | +209 $ | +955 $ | **+1164 $** | +13.5 $ | +35 $ |
| aucune bourse contre nous + sortie 10 s (pas_rejoint) | 86 | +1568 $ | +1958 $ | **+3526 $** | +41.0 $ | +520 $ |
| 3 bourses sur 4 avec nous + sortie 3 s (retombe) | 54 | +1646 $ | +948 $ | **+2594 $** | +48.0 $ | +132 $ |
| 3 bourses sur 4 avec nous + sortie 5 s (retombe) | 54 | +1813 $ | +714 $ | **+2528 $** | +46.8 $ | +66 $ |
| 3 bourses sur 4 avec nous + sortie 5 s (les_deux) | 54 | +347 $ | +938 $ | **+1285 $** | +23.8 $ | +157 $ |
| 3 bourses sur 4 avec nous + sortie 10 s (pas_rejoint) | 54 | +1733 $ | +1100 $ | **+2834 $** | +52.5 $ | +372 $ |

### E. Memes regles SANS LA NUIT (aucun achat 00h-08h, heure suisse)

| Regle | Trades | 1re moitie | 2e moitie | **Total** | Par trade | Sans top 3 |
|---|---|---|---|---|---|---|
| tout acheter a l'entree, sans nuit | 227 | +339 $ | +2583 $ | **+2922 $** | +12.9 $ | -84 $ |
| Binance avec nous, sans nuit | 57 | +1943 $ | +1464 $ | **+3407 $** | +59.8 $ | +946 $ |
| Binance avec nous, LA NUIT seulement | 15 | +11 $ | +301 $ | **+312 $** | +20.8 $ | -409 $ |
| Binance ou perp avec nous, sans nuit | 81 | +1719 $ | +1639 $ | **+3358 $** | +41.5 $ | +897 $ |
| Binance ou perp avec nous, LA NUIT seulement | 23 | -359 $ | +249 $ | **-111 $** | -4.8 $ | -832 $ |
| aucune bourse contre nous, sans nuit | 67 | +1545 $ | +1746 $ | **+3291 $** | +49.1 $ | +285 $ |
| aucune bourse contre nous, LA NUIT seulement | 19 | +14 $ | -82 $ | **-69 $** | -3.6 $ | -618 $ |
| aucune bourse contre nous + sortie 10 s (pas_rejoint), sans nuit | 67 | +1569 $ | +1922 $ | **+3491 $** | +52.1 $ | +485 $ |

## ETH — 294 desaccords >= 0,20

| Regle | Trades | 1re moitie | 2e moitie | **Total** | Par trade | Sans top 3 |
|---|---|---|---|---|---|---|
| REFERENCE : tout acheter a l'entree, garder | 294 | -731 $ | +2047 $ | **+1316 $** | +4.5 $ | -1321 $ |

### A. Achat immediat, sortie au meilleur acheteur si le desaccord se revele faux

| Regle | Trades | 1re moitie | 2e moitie | **Total** | Par trade | Sans top 3 |
|---|---|---|---|---|---|---|
| sortie a 1 s si modele -3 c | 294 | -965 $ | +1719 $ | **+754 $** | +2.6 $ | -1623 $ |
| sortie a 2 s si modele -3 c | 294 | -935 $ | +2069 $ | **+1135 $** | +3.9 $ | -1503 $ |
| sortie a 3 s si modele -3 c | 294 | -615 $ | +1318 $ | **+703 $** | +2.4 $ | -1934 $ |
| sortie a 5 s si modele -3 c | 294 | -1526 $ | +1326 $ | **-200 $** | -0.7 $ | -2838 $ |
| sortie a 10 s si modele -3 c | 294 | -1408 $ | +937 $ | **-471 $** | -1.6 $ | -3109 $ |
| sortie a 1 s si Poly n'a pas monte de 3 c | 294 | -1826 $ | +93 $ | **-1733 $** | -5.9 $ | -3573 $ |
| sortie a 2 s si Poly n'a pas monte de 3 c | 294 | -2037 $ | +821 $ | **-1216 $** | -4.1 $ | -3437 $ |
| sortie a 3 s si Poly n'a pas monte de 3 c | 294 | -802 $ | +467 $ | **-335 $** | -1.1 $ | -2594 $ |
| sortie a 5 s si Poly n'a pas monte de 3 c | 294 | -991 $ | -387 $ | **-1379 $** | -4.7 $ | -3567 $ |
| sortie a 10 s si Poly n'a pas monte de 3 c | 294 | -893 $ | +148 $ | **-745 $** | -2.5 $ | -2934 $ |
| sortie a 1 s si modele -3 c OU Poly pas monte | 294 | -1863 $ | +143 $ | **-1721 $** | -5.9 $ | -3561 $ |
| sortie a 2 s si modele -3 c OU Poly pas monte | 294 | -1919 $ | +669 $ | **-1250 $** | -4.3 $ | -3471 $ |
| sortie a 3 s si modele -3 c OU Poly pas monte | 294 | -603 $ | +467 $ | **-136 $** | -0.5 $ | -2394 $ |
| sortie a 5 s si modele -3 c OU Poly pas monte | 294 | -771 $ | -387 $ | **-1158 $** | -3.9 $ | -3347 $ |
| sortie a 10 s si modele -3 c OU Poly pas monte | 294 | -758 $ | +51 $ | **-707 $** | -2.4 $ | -2896 $ |

### B. Achat aux premiers signes (Polymarket monte de x c vers le modele, modele stable, dans les W s)

| Regle | Trades | 1re moitie | 2e moitie | **Total** | Par trade | Sans top 3 |
|---|---|---|---|---|---|---|
| W 1 s, x 1 c | 92 | -598 $ | +693 $ | **+95 $** | +1.0 $ | -1087 $ |
| W 1 s, x 2 c | 60 | -786 $ | +1141 $ | **+354 $** | +5.9 $ | -761 $ |
| W 1 s, x 3 c | 45 | -499 $ | +1400 $ | **+901 $** | +20.0 $ | -215 $ |
| W 1 s, x 5 c | 26 | -190 $ | +115 $ | **-75 $** | -2.9 $ | -570 $ |
| W 2 s, x 1 c | 114 | -813 $ | +959 $ | **+145 $** | +1.3 $ | -1076 $ |
| W 2 s, x 2 c | 84 | -790 $ | +1249 $ | **+459 $** | +5.5 $ | -762 $ |
| W 2 s, x 3 c | 62 | -745 $ | +1136 $ | **+391 $** | +6.3 $ | -725 $ |
| W 2 s, x 5 c | 36 | -226 $ | +585 $ | **+359 $** | +10.0 $ | -391 $ |
| W 3 s, x 1 c | 135 | -378 $ | +1682 $ | **+1305 $** | +9.7 $ | +59 $ |
| W 3 s, x 2 c | 99 | +107 $ | +1643 $ | **+1750 $** | +17.7 $ | +505 $ |
| W 3 s, x 3 c | 76 | +100 $ | +1530 $ | **+1630 $** | +21.5 $ | +385 $ |
| W 3 s, x 5 c | 48 | -262 $ | +821 $ | **+559 $** | +11.6 $ | -297 $ |
| W 5 s, x 1 c | 154 | -709 $ | +1536 $ | **+827 $** | +5.4 $ | -418 $ |
| W 5 s, x 2 c | 115 | -191 $ | +1602 $ | **+1411 $** | +12.3 $ | +166 $ |
| W 5 s, x 3 c | 93 | -344 $ | +1301 $ | **+957 $** | +10.3 $ | -288 $ |
| W 5 s, x 5 c | 63 | -118 $ | +776 $ | **+658 $** | +10.4 $ | -221 $ |
| W 10 s, x 1 c | 176 | -628 $ | +1632 $ | **+1004 $** | +5.7 $ | -533 $ |
| W 10 s, x 2 c | 135 | -279 $ | +1700 $ | **+1421 $** | +10.5 $ | -116 $ |
| W 10 s, x 3 c | 117 | -538 $ | +1291 $ | **+753 $** | +6.4 $ | -659 $ |
| W 10 s, x 5 c | 89 | -288 $ | +522 $ | **+233 $** | +2.6 $ | -646 $ |

### C. Filtre bourses a l'entree (3 s avant), achat immediat, garder

| Regle | Trades | 1re moitie | 2e moitie | **Total** | Par trade | Sans top 3 |
|---|---|---|---|---|---|---|
| aucun | 294 | -731 $ | +2047 $ | **+1316 $** | +4.5 $ | -1321 $ |
| Binance avec nous | 62 | -478 $ | +90 $ | **-388 $** | -6.3 $ | -1342 $ |
| perp avec nous | 63 | -609 $ | +19 $ | **-590 $** | -9.4 $ | -1589 $ |
| Binance ou perp avec nous | 84 | -851 $ | +176 $ | **-675 $** | -8.0 $ | -1674 $ |
| Binance et perp >= 0 | 108 | -378 $ | +533 $ | **+156 $** | +1.4 $ | -1736 $ |
| 3 bourses sur 4 avec nous | 47 | -78 $ | -387 $ | **-465 $** | -9.9 $ | -1419 $ |
| aucune bourse contre nous | 77 | -423 $ | +957 $ | **+534 $** | +6.9 $ | -1357 $ |

### D. Filtre bourses + sortie si faux

| Regle | Trades | 1re moitie | 2e moitie | **Total** | Par trade | Sans top 3 |
|---|---|---|---|---|---|---|
| Binance ou perp avec nous + sortie 3 s (retombe) | 84 | -740 $ | -212 $ | **-952 $** | -11.3 $ | -1907 $ |
| Binance ou perp avec nous + sortie 5 s (retombe) | 84 | -734 $ | -557 $ | **-1291 $** | -15.4 $ | -2057 $ |
| Binance ou perp avec nous + sortie 5 s (les_deux) | 84 | -396 $ | -235 $ | **-631 $** | -7.5 $ | -1397 $ |
| Binance ou perp avec nous + sortie 10 s (pas_rejoint) | 84 | -657 $ | -312 $ | **-969 $** | -11.5 $ | -1734 $ |
| aucune bourse contre nous + sortie 3 s (retombe) | 77 | -262 $ | +939 $ | **+676 $** | +8.8 $ | -1215 $ |
| aucune bourse contre nous + sortie 5 s (retombe) | 77 | -268 $ | +473 $ | **+205 $** | +2.7 $ | -1582 $ |
| aucune bourse contre nous + sortie 5 s (les_deux) | 77 | -285 $ | +880 $ | **+595 $** | +7.7 $ | -1192 $ |
| aucune bourse contre nous + sortie 10 s (pas_rejoint) | 77 | -367 $ | +784 $ | **+417 $** | +5.4 $ | -1370 $ |
| 3 bourses sur 4 avec nous + sortie 3 s (retombe) | 47 | +44 $ | -151 $ | **-107 $** | -2.3 $ | -1062 $ |
| 3 bourses sur 4 avec nous + sortie 5 s (retombe) | 47 | -39 $ | -584 $ | **-623 $** | -13.3 $ | -1328 $ |
| 3 bourses sur 4 avec nous + sortie 5 s (les_deux) | 47 | +104 $ | -344 $ | **-240 $** | -5.1 $ | -945 $ |
| 3 bourses sur 4 avec nous + sortie 10 s (pas_rejoint) | 47 | -78 $ | -380 $ | **-459 $** | -9.8 $ | -1164 $ |

### E. Memes regles SANS LA NUIT (aucun achat 00h-08h, heure suisse)

| Regle | Trades | 1re moitie | 2e moitie | **Total** | Par trade | Sans top 3 |
|---|---|---|---|---|---|---|
| tout acheter a l'entree, sans nuit | 203 | -481 $ | +761 $ | **+280 $** | +1.4 $ | -1979 $ |
| Binance avec nous, sans nuit | 44 | -354 $ | +84 $ | **-270 $** | -6.1 $ | -1118 $ |
| Binance avec nous, LA NUIT seulement | 18 | -124 $ | +6 $ | **-118 $** | -6.5 $ | -683 $ |
| Binance ou perp avec nous, sans nuit | 64 | -675 $ | +223 $ | **-452 $** | -7.1 $ | -1379 $ |
| Binance ou perp avec nous, LA NUIT seulement | 20 | -177 $ | -47 $ | **-223 $** | -11.2 $ | -789 $ |
| aucune bourse contre nous, sans nuit | 55 | -278 $ | +1056 $ | **+778 $** | +14.1 $ | -1086 $ |
| aucune bourse contre nous, LA NUIT seulement | 22 | -145 $ | -99 $ | **-244 $** | -11.1 $ | -893 $ |
| aucune bourse contre nous + sortie 10 s (pas_rejoint), sans nuit | 55 | -414 $ | +766 $ | **+352 $** | +6.4 $ | -1218 $ |
