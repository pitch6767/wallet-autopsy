# Paires BTC 5 min « a valeur » — 1926 cycles, 7 jours (2026-09-28 -> 2026-10-04)

Retard = la proba est calculee avec le prix Binance de L secondes AVANT l'echange (temps de reaction du bot). 100 parts par jambe. Remplissage prudent sauf mention. Frais taker 0,072 x p x (1-p) ; maker 0.

| Strategie | Marge | Cycles trades | Paires | Gain total | Gain/jour | Gain moyen/cycle trade | Pire cycle | Pire baisse |
|---|---|---|---|---|---|---|---|---|
| V1 Pitch filtre, retard 0 s | 0.08 | 1123 (160/j) | 301 | +12403 $ | +1772 $ | +11.04 $ | -58 $ | -140 $ |
| V2 jambe gardee, retard 0 s | 0.08 | 1903 (272/j) | 107 | +31752 $ | +4536 $ | +16.69 $ | -198 $ | -794 $ |
| V2 sortie 90, retard 0 s | 0.10 | 1882 (269/j) | 159 | +17862 $ | +2552 $ | +9.49 $ | -154 $ | -874 $ |
| V1 Pitch filtre, retard 1 s | 0.08 | 1057 (151/j) | 229 | +10002 $ | +1429 $ | +9.46 $ | -58 $ | -154 $ |
| V2 jambe gardee, retard 1 s | 0.08 | 1898 (271/j) | 122 | +20638 $ | +2948 $ | +10.87 $ | -165 $ | -1283 $ |
| V2 sortie 90, retard 1 s | 0.10 | 1871 (267/j) | 157 | +10116 $ | +1445 $ | +5.41 $ | -131 $ | -1776 $ |
| V1 Pitch filtre, retard 2 s | 0.08 | 1000 (143/j) | 181 | +5407 $ | +772 $ | +5.41 $ | -58 $ | -314 $ |
| V2 jambe gardee, retard 2 s | 0.08 | 1892 (270/j) | 139 | +8689 $ | +1241 $ | +4.59 $ | -165 $ | -2322 $ |
| V2 sortie 90, retard 2 s | 0.10 | 1844 (263/j) | 164 | +3558 $ | +508 $ | +1.93 $ | -138 $ | -2069 $ |
| V1 Pitch filtre, retard 5 s | 0.08 | 967 (138/j) | 252 | -3691 $ | -527 $ | -3.82 $ | -58 $ | -3739 $ |
| V2 jambe gardee, retard 5 s | 0.08 | 1904 (272/j) | 163 | -47702 $ | -6815 $ | -25.05 $ | -252 $ | -47702 $ |
| V2 sortie 90, retard 5 s | 0.10 | 1892 (270/j) | 230 | -33477 $ | -4782 $ | -17.69 $ | -203 $ | -33477 $ |
| V2 jambe gardee, retard 2 s | 0.15 | 1564 (223/j) | 111 | +11183 $ | +1598 $ | +7.15 $ | -124 $ | -835 $ |
| V2 jambe gardee, retard 5 s | 0.15 | 1746 (249/j) | 119 | -24466 $ | -3495 $ | -14.01 $ | -168 $ | -24466 $ |

## Detail par issue

- V1 Pitch filtre, retard 0 s, marge 0.08 : sortie 90 435 (+31.96 $) ; stop 362 (-12.90 $) ; paire 187 (+14.65 $) ; stop+paire partielle 114 (+0.43 $) ; fin gagnee 20 (+33.42 $) ; fin perdue 5 (-57.42 $)
- V2 jambe gardee, retard 0 s, marge 0.08 : jambe+seule gagnee 1310 (+29.09 $) ; jambe+seule perdue 486 (-12.75 $) ; paire+seule perdue 70 (-10.43 $) ; paire+seule gagnee 34 (+19.67 $) ; paire 3 (-32.08 $)
- V2 sortie 90, retard 0 s, marge 0.1 : jambe+90 1442 (+17.84 $) ; jambe+seule perdue 281 (-26.24 $) ; paire+90 84 (+13.72 $) ; paire+seule perdue 75 (-21.94 $)
- V1 Pitch filtre, retard 1 s, marge 0.08 : sortie 90 403 (+31.98 $) ; stop 400 (-13.79 $) ; paire 151 (+15.45 $) ; stop+paire partielle 78 (-1.31 $) ; fin gagnee 20 (+34.32 $) ; fin perdue 5 (-57.42 $)
- V2 jambe gardee, retard 1 s, marge 0.08 : jambe+seule gagnee 1249 (+24.85 $) ; jambe+seule perdue 527 (-17.73 $) ; paire+seule perdue 78 (-20.03 $) ; paire+seule gagnee 39 (+12.56 $) ; paire 5 (+3.50 $)
- V2 sortie 90, retard 1 s, marge 0.1 : jambe+90 1382 (+15.70 $) ; jambe+seule perdue 332 (-30.15 $) ; paire+90 89 (+3.34 $) ; paire+seule perdue 68 (-27.53 $)
- V1 Pitch filtre, retard 2 s, marge 0.08 : stop 437 (-18.83 $) ; sortie 90 366 (+31.96 $) ; paire 128 (+16.70 $) ; stop+paire partielle 53 (-5.93 $) ; fin gagnee 11 (+36.52 $) ; fin perdue 5 (-57.42 $)
- V2 jambe gardee, retard 2 s, marge 0.08 : jambe+seule gagnee 1173 (+21.99 $) ; jambe+seule perdue 580 (-25.39 $) ; paire+seule perdue 80 (-28.37 $) ; paire+seule gagnee 48 (+1.44 $) ; paire 11 (-16.74 $)
- V2 sortie 90, retard 2 s, marge 0.1 : jambe+90 1303 (+13.88 $) ; jambe+seule perdue 377 (-32.00 $) ; paire+90 91 (+1.14 $) ; paire+seule perdue 70 (-35.66 $) ; paire 3 (-24.05 $)
- V1 Pitch filtre, retard 5 s, marge 0.08 : stop 515 (-23.08 $) ; paire 207 (+13.37 $) ; sortie 90 164 (+31.88 $) ; stop+paire partielle 45 (-8.63 $) ; fin gagnee 30 (+30.86 $) ; fin perdue 6 (-56.87 $)
- V2 jambe gardee, retard 5 s, marge 0.08 : jambe+seule gagnee 872 (+5.57 $) ; jambe+seule perdue 869 (-55.23 $) ; paire+seule perdue 94 (-34.91 $) ; paire+seule gagnee 64 (-16.42 $) ; paire 5 (-46.74 $)
- V2 sortie 90, retard 5 s, marge 0.1 : jambe+90 1034 (+0.46 $) ; jambe+seule perdue 628 (-48.79 $) ; paire+90 154 (-3.68 $) ; paire+seule perdue 71 (-36.52 $) ; paire 5 (-30.42 $)
- V2 jambe gardee, retard 2 s, marge 0.15 : jambe+seule gagnee 940 (+28.14 $) ; jambe+seule perdue 513 (-25.15 $) ; paire+seule perdue 78 (-33.52 $) ; paire+seule gagnee 26 (+12.34 $) ; paire 7 (-10.56 $)
- V2 jambe gardee, retard 5 s, marge 0.15 : jambe+seule perdue 934 (-40.32 $) ; jambe+seule gagnee 693 (+20.95 $) ; paire+seule perdue 74 (-25.90 $) ; paire+seule gagnee 38 (+19.66 $) ; paire 7 (-22.76 $)

Duree : 426 s