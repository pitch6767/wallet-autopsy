# Paires BTC 5 min « a valeur » — 1929 cycles, 7 jours (2026-09-28 -> 2026-10-04)

100 parts par jambe. Remplissage prudent sauf mention. Frais taker 0,072 x p x (1-p) ; maker 0.

| Strategie | Marge | Cycles trades | Paires | Gain total | Gain/jour | Gain moyen/cycle trade | Pire cycle | Pire baisse |
|---|---|---|---|---|---|---|---|---|
| V1 Pitch filtre (55 si proba >= 55+marge, offre opposee a valeur <= 43) | 0.05 | 1305 (186/j) | 511 | +12519 $ | +1788 $ | +9.59 $ | -58 $ | -131 $ |
| V1 Pitch filtre (55 si proba >= 55+marge, offre opposee a valeur <= 43) | 0.08 | 1124 (161/j) | 301 | +12435 $ | +1776 $ | +11.06 $ | -58 $ | -140 $ |
| V1 Pitch filtre (55 si proba >= 55+marge, offre opposee a valeur <= 43) | 0.10 | 1011 (144/j) | 203 | +11632 $ | +1662 $ | +11.51 $ | -58 $ | -118 $ |
| V1 Pitch filtre (55 si proba >= 55+marge, offre opposee a valeur <= 43) | 0.15 | 692 (99/j) | 74 | +9810 $ | +1401 $ | +14.18 $ | -58 $ | -141 $ |
| V2 offres a valeur des 2 cotes, jambe gardee | 0.05 | 1916 (274/j) | 94 | +29068 $ | +4153 $ | +15.17 $ | -249 $ | -2043 $ |
| V2 offres a valeur, sortie 90 | 0.05 | 1916 (274/j) | 151 | +16175 $ | +2311 $ | +8.44 $ | -194 $ | -3500 $ |
| V2 offres a valeur des 2 cotes, jambe gardee | 0.08 | 1906 (272/j) | 108 | +31875 $ | +4554 $ | +16.72 $ | -198 $ | -794 $ |
| V2 offres a valeur, sortie 90 | 0.08 | 1906 (272/j) | 134 | +18057 $ | +2580 $ | +9.47 $ | -149 $ | -1601 $ |
| V2 offres a valeur des 2 cotes, jambe gardee | 0.10 | 1885 (269/j) | 143 | +31123 $ | +4446 $ | +16.51 $ | -199 $ | -622 $ |
| V2 offres a valeur, sortie 90 | 0.10 | 1885 (269/j) | 159 | +17946 $ | +2564 $ | +9.52 $ | -154 $ | -874 $ |
| V2 offres a valeur des 2 cotes, jambe gardee | 0.15 | 1694 (242/j) | 113 | +26421 $ | +3774 $ | +15.60 $ | -161 $ | -421 $ |
| V2 offres a valeur, sortie 90 | 0.15 | 1694 (242/j) | 113 | +16059 $ | +2294 $ | +9.48 $ | -126 $ | -463 $ |
| V2 offres a valeur, OPTIMISTE (premier dans la file) | 0.08 | 1909 (273/j) | 103 | +40820 $ | +5831 $ | +21.38 $ | -185 $ | -812 $ |
| V1 Pitch filtre, OPTIMISTE | 0.08 | 1124 (161/j) | 345 | +12797 $ | +1828 $ | +11.38 $ | -58 $ | -112 $ |

## Detail par issue

- V1 Pitch filtre (55 si proba >= 55+marge, offre opposee a valeur <= 43), marge 0.05 : sortie 90 375 (+31.95 $) ; stop 373 (-12.43 $) ; paire 362 (+11.94 $) ; stop+paire partielle 149 (-1.22 $) ; fin gagnee 41 (+32.25 $) ; fin perdue 5 (-57.42 $)
- V1 Pitch filtre (55 si proba >= 55+marge, offre opposee a valeur <= 43), marge 0.08 : sortie 90 436 (+31.96 $) ; stop 362 (-12.90 $) ; paire 187 (+14.65 $) ; stop+paire partielle 114 (+0.43 $) ; fin gagnee 20 (+33.42 $) ; fin perdue 5 (-57.42 $)
- V1 Pitch filtre (55 si proba >= 55+marge, offre opposee a valeur <= 43), marge 0.1 : sortie 90 424 (+31.95 $) ; stop 357 (-12.47 $) ; paire 120 (+16.14 $) ; stop+paire partielle 83 (+1.57 $) ; fin gagnee 22 (+34.45 $) ; fin perdue 5 (-57.42 $)
- V1 Pitch filtre (55 si proba >= 55+marge, offre opposee a valeur <= 43), marge 0.15 : sortie 90 376 (+31.95 $) ; stop 227 (-13.07 $) ; paire 38 (+16.60 $) ; stop+paire partielle 36 (+6.59 $) ; fin gagnee 8 (+36.92 $) ; fin perdue 7 (-57.46 $)
- V2 offres a valeur des 2 cotes, jambe gardee, marge 0.05 : jambe+seule gagnee 1311 (+26.84 $) ; jambe+seule perdue 511 (-11.57 $) ; paire+seule perdue 60 (-11.66 $) ; paire+seule gagnee 30 (+15.05 $) ; paire 4 (+9.84 $)
- V2 offres a valeur, sortie 90, marge 0.05 : jambe+90 1507 (+15.02 $) ; jambe+seule perdue 258 (-25.97 $) ; paire+90 109 (+10.82 $) ; paire+seule perdue 40 (-25.45 $) ; paire 2 (+35.75 $)
- V2 offres a valeur des 2 cotes, jambe gardee, marge 0.08 : jambe+seule gagnee 1312 (+29.13 $) ; jambe+seule perdue 486 (-12.75 $) ; paire+seule perdue 71 (-10.13 $) ; paire+seule gagnee 34 (+19.67 $) ; paire 3 (-32.08 $)
- V2 offres a valeur, sortie 90, marge 0.08 : jambe+90 1489 (+17.19 $) ; jambe+seule perdue 283 (-25.70 $) ; paire+90 81 (+9.72 $) ; paire+seule perdue 51 (-19.35 $) ; paire 2 (-35.00 $)
- V2 offres a valeur des 2 cotes, jambe gardee, marge 0.1 : jambe+seule gagnee 1289 (+29.86 $) ; jambe+seule perdue 453 (-14.99 $) ; paire+seule perdue 96 (-16.27 $) ; paire+seule gagnee 44 (+22.56 $) ; paire 3 (-0.68 $)
- V2 offres a valeur, sortie 90, marge 0.1 : jambe+90 1445 (+17.86 $) ; jambe+seule perdue 281 (-26.21 $) ; paire+90 84 (+13.74 $) ; paire+seule perdue 75 (-21.94 $)
- V2 offres a valeur des 2 cotes, jambe gardee, marge 0.15 : jambe+seule gagnee 1152 (+31.42 $) ; jambe+seule perdue 429 (-18.60 $) ; paire+seule perdue 76 (-30.88 $) ; paire+seule gagnee 33 (+19.73 $) ; paire 4 (-23.44 $)
- V2 offres a valeur, sortie 90, marge 0.15 : jambe+90 1285 (+20.13 $) ; jambe+seule perdue 296 (-29.90 $) ; paire+seule perdue 57 (-31.33 $) ; paire+90 53 (+17.89 $) ; paire 3 (-38.79 $)
- V2 offres a valeur, OPTIMISTE (premier dans la file), marge 0.08 : jambe+seule gagnee 1318 (+32.54 $) ; jambe+seule perdue 488 (-4.96 $) ; paire+seule perdue 66 (-5.88 $) ; paire+seule gagnee 32 (+23.73 $) ; paire 5 (-4.20 $)
- V1 Pitch filtre, OPTIMISTE, marge 0.08 : sortie 90 415 (+31.96 $) ; stop 341 (-13.04 $) ; paire 231 (+15.50 $) ; stop+paire partielle 114 (+0.73 $) ; fin gagnee 18 (+33.57 $) ; fin perdue 5 (-57.42 $)

Duree : 749 s