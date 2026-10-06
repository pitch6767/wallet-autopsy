# Desaccords modele/marche : quelles combinaisons gagnent ? — 12 jours (2026-09-24 -> 2026-10-05)
Episode = premier instant ou |modele - marche| >= 0,10 ; achat du cote du modele seulement si un vrai acheteur a paye ce prix (+1 cent) dans les 2 s ; garde jusqu'a la fin ; gain par part, frais compris.
Combinaisons choisies sur les jours 1-8 (au moins 60 episodes), verifiees sur les jours 9-12.


## BTC — 8884 episodes achetables (j1-8 : 6083, j9-12 : 2801)

Tous : gain/part j1-8 +0.069 $, **j9-12 +0.074 $**

### Chaque critere seul

| Critere | Valeur | Episodes j1-8 | Gagne | Gain/part j1-8 | Episodes j9-12 | **Gain/part j9-12** |
|---|---|---|---|---|---|---|
| temps | debut >4min | 1713 | 61 % | +0.045 $ | 930 | **+0.066 $** |
| temps | dernieres 30s | 65 | 23 % | +0.063 $ | 37 | **+0.077 $** |
| temps | fin <2min | 1588 | 56 % | +0.119 $ | 640 | **+0.105 $** |
| temps | milieu | 2717 | 62 % | +0.056 $ | 1194 | **+0.062 $** |
| prix | 0.30-0.50 | 1507 | 49 % | +0.061 $ | 760 | **+0.085 $** |
| prix | <0.30 | 1031 | 29 % | +0.113 $ | 610 | **+0.064 $** |
| prix | >0.50 | 3545 | 73 % | +0.060 $ | 1431 | **+0.072 $** |
| perp | perp avec | 3641 | 63 % | +0.108 $ | 1481 | **+0.127 $** |
| perp | perp contre | 1650 | 57 % | +0.021 $ | 803 | **+0.015 $** |
| perp | perp plat | 792 | 50 % | -0.011 $ | 517 | **+0.012 $** |
| marche | marche contre | 3156 | 55 % | +0.058 $ | 1536 | **+0.057 $** |
| marche | marche stable | 1310 | 62 % | +0.083 $ | 629 | **+0.100 $** |
| marche | marche vers nous | 1617 | 67 % | +0.080 $ | 636 | **+0.087 $** |
| autre | autre ? | 970 | 57 % | +0.072 $ | 414 | **+0.092 $** |
| autre | autre contre | 384 | 48 % | -0.003 $ | 243 | **-0.006 $** |
| autre | autre d'accord | 2866 | 64 % | +0.100 $ | 1171 | **+0.108 $** |
| autre | autre neutre | 1863 | 57 % | +0.036 $ | 973 | **+0.044 $** |
| ecart | 0.10-0.15 | 4578 | 59 % | +0.046 $ | 2092 | **+0.049 $** |
| ecart | 0.15-0.20 | 901 | 60 % | +0.100 $ | 429 | **+0.118 $** |
| ecart | ecart>=0.20 | 604 | 62 % | +0.198 $ | 280 | **+0.188 $** |

### Meilleures combinaisons (choisies j1-8)

| Combinaison | Episodes j1-8 | Gagne j1-8 | Gain/part j1-8 | Episodes j9-12 | Gagne j9-12 | **Gain/part j9-12** |
|---|---|---|---|---|---|---|
| temps=fin <2min + perp=perp avec + ecart=ecart>=0.20 | 183 | 62 % | +0.335 $ | 74 | 62 % | **+0.333 $** |
| prix=<0.30 + perp=perp avec + ecart=ecart>=0.20 | 157 | 49 % | +0.331 $ | 68 | 47 % | **+0.321 $** |
| prix=<0.30 + autre=autre d'accord + ecart=ecart>=0.20 | 91 | 52 % | +0.328 $ | 42 | 55 % | **+0.382 $** |
| prix=0.30-0.50 + perp=perp avec + ecart=ecart>=0.20 | 128 | 75 % | +0.325 $ | 56 | 62 % | **+0.199 $** |
| perp=perp avec + marche=marche contre + ecart=ecart>=0.20 | 188 | 63 % | +0.310 $ | 82 | 65 % | **+0.314 $** |
| prix=<0.30 + marche=marche contre + ecart=ecart>=0.20 | 133 | 45 % | +0.291 $ | 59 | 42 % | **+0.241 $** |
| prix=0.30-0.50 + autre=autre d'accord + ecart=ecart>=0.20 | 97 | 71 % | +0.279 $ | 41 | 66 % | **+0.234 $** |
| temps=fin <2min + prix=<0.30 + ecart=ecart>=0.20 | 135 | 43 % | +0.278 $ | 57 | 42 % | **+0.278 $** |
| perp=perp avec + autre=autre neutre + ecart=ecart>=0.20 | 71 | 63 % | +0.278 $ | 40 | 65 % | **+0.233 $** |
| temps=fin <2min + autre=autre d'accord + ecart=ecart>=0.20 | 114 | 62 % | +0.272 $ | 47 | 57 % | **+0.276 $** |
| prix=<0.30 + ecart=ecart>=0.20 | 193 | 44 % | +0.271 $ | 89 | 42 % | **+0.246 $** |
| prix=0.30-0.50 + ecart=ecart>=0.20 | 169 | 69 % | +0.265 $ | 87 | 59 % | **+0.156 $** |
| temps=milieu + prix=0.30-0.50 + ecart=ecart>=0.20 | 70 | 70 % | +0.264 $ | 29 | 62 % | **+0.189 $** |
| marche=marche contre + autre=autre d'accord + ecart=ecart>=0.20 | 145 | 63 % | +0.258 $ | 60 | 68 % | **+0.322 $** |
| temps=milieu + autre=autre d'accord + ecart=ecart>=0.20 | 125 | 72 % | +0.248 $ | 52 | 77 % | **+0.297 $** |
| temps=fin <2min + ecart=ecart>=0.20 | 257 | 58 % | +0.246 $ | 103 | 57 % | **+0.255 $** |
| perp=perp avec + ecart=ecart>=0.20 | 482 | 66 % | +0.243 $ | 196 | 67 % | **+0.265 $** |
| perp=perp avec + autre=autre ? + ecart=ecart>=0.20 | 113 | 64 % | +0.240 $ | 39 | 64 % | **+0.223 $** |
| perp=perp avec + autre=autre d'accord + ecart=ecart>=0.20 | 292 | 67 % | +0.238 $ | 110 | 71 % | **+0.303 $** |
| temps=fin <2min + marche=marche contre + ecart=ecart>=0.20 | 163 | 55 % | +0.233 $ | 67 | 57 % | **+0.261 $** |
| temps=milieu + perp=perp avec + ecart=ecart>=0.20 | 177 | 71 % | +0.232 $ | 70 | 71 % | **+0.236 $** |
| prix=<0.30 + marche=marche vers nous + autre=autre d'accord | 79 | 46 % | +0.229 $ | 31 | 29 % | **+0.080 $** |
| prix=0.30-0.50 + marche=marche contre + ecart=ecart>=0.20 | 80 | 64 % | +0.223 $ | 43 | 60 % | **+0.193 $** |
| temps=fin <2min + perp=perp avec + marche=marche contre | 363 | 55 % | +0.223 $ | 151 | 51 % | **+0.179 $** |
| temps=fin <2min + prix=<0.30 + perp=perp avec | 356 | 36 % | +0.219 $ | 148 | 30 % | **+0.160 $** |

### Pires combinaisons (a eviter, choisies j1-8)

| Combinaison | Episodes j1-8 | Gain/part j1-8 | Episodes j9-12 | **Gain/part j9-12** |
|---|---|---|---|---|
| perp=perp plat + marche=marche contre + autre=autre contre | 75 | -0.131 $ | 53 | **+0.028 $** |
| temps=debut >4min + prix=0.30-0.50 + perp=perp plat | 94 | -0.112 $ | 99 | **+0.007 $** |
| perp=perp plat + autre=autre contre | 96 | -0.091 $ | 76 | **+0.018 $** |
| perp=perp plat + autre=autre contre + ecart=0.10-0.15 | 79 | -0.087 $ | 60 | **+0.044 $** |
| prix=0.30-0.50 + autre=autre contre | 127 | -0.078 $ | 83 | **+0.035 $** |
| prix=0.30-0.50 + autre=autre contre + ecart=0.10-0.15 | 101 | -0.076 $ | 62 | **+0.045 $** |
| perp=perp plat + autre=autre ? | 112 | -0.073 $ | 80 | **+0.008 $** |
| prix=0.30-0.50 + marche=marche contre + autre=autre contre | 98 | -0.073 $ | 55 | **-0.007 $** |
| temps=debut >4min + perp=perp plat + marche=marche stable | 89 | -0.068 $ | 91 | **+0.006 $** |
| perp=perp contre + marche=marche vers nous + autre=autre neutre | 72 | -0.058 $ | 20 | **-0.125 $** |
| temps=milieu + marche=marche contre + autre=autre contre | 140 | -0.053 $ | 84 | **-0.066 $** |
| perp=perp plat + autre=autre ? + ecart=0.10-0.15 | 92 | -0.051 $ | 70 | **-0.030 $** |

Les 25 meilleures (j1-8) en moyenne : j1-8 +0.266 $ -> **j9-12 +0.247 $** ; restent positives sur j9-12 : 25/25

## ETH — 3289 episodes achetables (j1-8 : 2240, j9-12 : 1049)

Tous : gain/part j1-8 +0.094 $, **j9-12 +0.074 $**

### Chaque critere seul

| Critere | Valeur | Episodes j1-8 | Gagne | Gain/part j1-8 | Episodes j9-12 | **Gain/part j9-12** |
|---|---|---|---|---|---|---|
| temps | debut >4min | 503 | 61 % | +0.054 $ | 259 | **+0.042 $** |
| temps | dernieres 30s | 41 | 29 % | +0.093 $ | 16 | **+0.079 $** |
| temps | fin <2min | 842 | 57 % | +0.128 $ | 351 | **+0.088 $** |
| temps | milieu | 854 | 62 % | +0.083 $ | 423 | **+0.083 $** |
| prix | 0.30-0.50 | 516 | 53 % | +0.109 $ | 260 | **+0.073 $** |
| prix | <0.30 | 531 | 31 % | +0.129 $ | 251 | **+0.063 $** |
| prix | >0.50 | 1193 | 75 % | +0.071 $ | 538 | **+0.080 $** |
| perp | perp avec | 1597 | 61 % | +0.121 $ | 650 | **+0.125 $** |
| perp | perp contre | 459 | 57 % | +0.043 $ | 243 | **-0.015 $** |
| perp | perp plat | 184 | 52 % | -0.016 $ | 156 | **+0.004 $** |
| marche | marche contre | 1085 | 54 % | +0.088 $ | 533 | **+0.052 $** |
| marche | marche stable | 435 | 60 % | +0.082 $ | 204 | **+0.080 $** |
| marche | marche vers nous | 720 | 67 % | +0.109 $ | 312 | **+0.109 $** |
| autre | autre ? | 32 | 44 % | +0.116 $ | 20 | **-0.013 $** |
| autre | autre contre | 239 | 49 % | +0.005 $ | 161 | **+0.040 $** |
| autre | autre d'accord | 1227 | 64 % | +0.104 $ | 491 | **+0.056 $** |
| autre | autre neutre | 742 | 57 % | +0.104 $ | 377 | **+0.118 $** |
| ecart | 0.10-0.15 | 1612 | 60 % | +0.069 $ | 791 | **+0.046 $** |
| ecart | 0.15-0.20 | 379 | 60 % | +0.125 $ | 161 | **+0.117 $** |
| ecart | ecart>=0.20 | 249 | 58 % | +0.203 $ | 97 | **+0.236 $** |

### Meilleures combinaisons (choisies j1-8)

| Combinaison | Episodes j1-8 | Gagne j1-8 | Gain/part j1-8 | Episodes j9-12 | Gagne j9-12 | **Gain/part j9-12** |
|---|---|---|---|---|---|---|
| perp=perp avec + marche=marche contre + ecart=ecart>=0.20 | 91 | 64 % | +0.323 $ | 31 | 65 % | **+0.370 $** |
| temps=fin <2min + autre=autre d'accord + ecart=ecart>=0.20 | 73 | 62 % | +0.284 $ | 20 | 40 % | **+0.030 $** |
| temps=fin <2min + marche=marche contre + ecart=ecart>=0.20 | 72 | 58 % | +0.282 $ | 26 | 35 % | **+0.037 $** |
| marche=marche contre + ecart=ecart>=0.20 | 116 | 59 % | +0.268 $ | 46 | 46 % | **+0.133 $** |
| temps=fin <2min + perp=perp avec + ecart=ecart>=0.20 | 111 | 59 % | +0.256 $ | 34 | 71 % | **+0.383 $** |
| temps=fin <2min + ecart=ecart>=0.20 | 131 | 59 % | +0.252 $ | 45 | 53 % | **+0.192 $** |
| temps=fin <2min + prix=<0.30 + ecart=ecart>=0.20 | 64 | 41 % | +0.244 $ | 22 | 45 % | **+0.285 $** |
| prix=0.30-0.50 + ecart=ecart>=0.20 | 75 | 65 % | +0.241 $ | 24 | 67 % | **+0.258 $** |
| prix=0.30-0.50 + perp=perp avec + ecart=ecart>=0.20 | 63 | 65 % | +0.239 $ | 20 | 80 % | **+0.393 $** |
| autre=autre d'accord + ecart=ecart>=0.20 | 143 | 62 % | +0.239 $ | 54 | 61 % | **+0.189 $** |
| prix=<0.30 + perp=perp avec + ecart=ecart>=0.20 | 84 | 40 % | +0.236 $ | 31 | 58 % | **+0.414 $** |
| perp=perp avec + autre=autre neutre + ecart=ecart>=0.20 | 60 | 60 % | +0.236 $ | 24 | 83 % | **+0.524 $** |
| prix=0.30-0.50 + perp=perp avec + ecart=0.15-0.20 | 63 | 67 % | +0.235 $ | 29 | 66 % | **+0.244 $** |
| perp=perp avec + autre=autre d'accord + ecart=ecart>=0.20 | 136 | 61 % | +0.224 $ | 47 | 68 % | **+0.265 $** |
| temps=fin <2min + perp=perp avec + autre=autre d'accord | 249 | 63 % | +0.217 $ | 67 | 51 % | **+0.103 $** |
| perp=perp avec + ecart=ecart>=0.20 | 216 | 60 % | +0.215 $ | 80 | 74 % | **+0.352 $** |
| prix=<0.30 + ecart=ecart>=0.20 | 99 | 38 % | +0.215 $ | 37 | 49 % | **+0.315 $** |
| temps=milieu + perp=perp avec + ecart=0.15-0.20 | 104 | 72 % | +0.214 $ | 47 | 64 % | **+0.139 $** |
| temps=fin <2min + prix=<0.30 + autre=autre d'accord | 124 | 36 % | +0.213 $ | 49 | 16 % | **-0.004 $** |
| prix=<0.30 + marche=marche contre + autre=autre d'accord | 140 | 39 % | +0.211 $ | 63 | 14 % | **-0.044 $** |
| temps=fin <2min + autre=autre d'accord + ecart=0.15-0.20 | 72 | 62 % | +0.208 $ | 20 | 50 % | **+0.107 $** |
| temps=fin <2min + perp=perp avec + marche=marche contre | 236 | 53 % | +0.202 $ | 82 | 51 % | **+0.171 $** |
| autre=autre neutre + ecart=ecart>=0.20 | 70 | 56 % | +0.197 $ | 33 | 64 % | **+0.307 $** |
| temps=fin <2min + marche=marche vers nous + autre=autre d'accord | 114 | 75 % | +0.194 $ | 37 | 59 % | **+0.077 $** |
| temps=milieu + prix=0.30-0.50 + perp=perp avec | 140 | 61 % | +0.192 $ | 64 | 56 % | **+0.148 $** |

### Pires combinaisons (a eviter, choisies j1-8)

| Combinaison | Episodes j1-8 | Gain/part j1-8 | Episodes j9-12 | **Gain/part j9-12** |
|---|---|---|---|---|
| temps=milieu + autre=autre contre + ecart=0.10-0.15 | 74 | -0.104 $ | 58 | **+0.047 $** |
| marche=marche contre + autre=autre contre + ecart=0.10-0.15 | 92 | -0.082 $ | 74 | **-0.001 $** |
| temps=milieu + marche=marche contre + autre=autre contre | 61 | -0.070 $ | 42 | **+0.135 $** |
| perp=perp contre + autre=autre contre | 68 | -0.069 $ | 53 | **-0.028 $** |
| prix=>0.50 + perp=perp plat | 106 | -0.058 $ | 78 | **+0.032 $** |
| prix=>0.50 + perp=perp plat + ecart=0.10-0.15 | 92 | -0.055 $ | 64 | **+0.055 $** |
| prix=>0.50 + perp=perp plat + marche=marche contre | 65 | -0.051 $ | 48 | **+0.082 $** |
| temps=fin <2min + perp=perp plat + marche=marche contre | 60 | -0.050 $ | 48 | **+0.012 $** |
| temps=fin <2min + perp=perp plat | 87 | -0.042 $ | 62 | **+0.001 $** |
| marche=marche contre + autre=autre contre | 130 | -0.038 $ | 92 | **+0.057 $** |
| autre=autre contre + ecart=0.10-0.15 | 167 | -0.036 $ | 126 | **+0.002 $** |
| perp=perp plat + autre=autre d'accord + ecart=0.10-0.15 | 72 | -0.030 $ | 44 | **-0.051 $** |

Les 25 meilleures (j1-8) en moyenne : j1-8 +0.234 $ -> **j9-12 +0.215 $** ; restent positives sur j9-12 : 23/25

Duree : 1268 s