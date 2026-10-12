# Bot95 — V2-F « écart qui grandit » (BTC)

Rapport du 09.10.2026 · fantôme figé depuis le 07.10 à 13:46 (heure suisse) · 50 $ par trade, frais Polymarket compris.

## 1. En bref

- **Depuis le 07.10 à 13:46 : 427 trades, 103 positifs, 324 négatifs, +3'254 $** — en moyenne +8 $ par trade.
- Les 60 derniers trades (08.10 au soir → 09.10 matin), listés en annexe : 16 gagnés, +614 $.
- Comme toutes les stratégies de désaccord, elle gagne environ 1 fois sur 4, mais ses gagnants rapportent 3 à 6 fois la mise.
> **Limite importante :** jusqu'à ce matin, le bot ne gardait le détail que des 60 derniers trades de chaque fantôme (plus le total). Les 367 trades plus anciens ne sont donc connus qu'en total. **Corrigé ce matin :** depuis 07:45, chaque trade est archivé (jusqu'à 1 500 par fantôme), le prochain PDF les contiendra tous.
## 2. La règle en détail

**Le marché.** Toutes les 5 minutes, Polymarket propose « le BTC finira-t-il plus haut (Up) ou plus bas (Down) qu'au début du cycle ? ». Le jeton gagnant vaut 1 $, l'autre 0 $.
**Le modèle** du bot calcule sa probabilité pour chaque côté à partir du prix BTC (Chainlink et bourses), du prix à battre, du temps restant et de la volatilité.
**Les conditions d'achat (toutes en même temps) :**
- 1. **Écart d'au moins 20 points** : probabilité du modèle − prix du meilleur vendeur ≥ 0,20.
- 2. **L'écart grandit** : il est plus grand d'au moins 3 points qu'il y a 3 secondes. Le désaccord ne se referme pas, il s'ouvre : le modèle voit quelque chose que Polymarket n'a pas encore intégré.
- 3. **Au moins 5 secondes restantes** dans le cycle.
- Aucun filtre de prix : le jeton peut coûter de 0,03 à 0,97 $ (beaucoup sont entre 0,10 et 0,30 $).
**L'achat.** 50 $ au meilleur vendeur, jusqu'à son prix + 1 cent (moins si le vendeur n'a pas assez de jetons). **Un seul achat par cycle.**
**La sortie.** Aucune : on garde jusqu'au résultat (1 $ par jeton si gagné, 0 $ sinon).
**Exemple réel (09.10, 07:27) :** 180 s avant la fin, écart 0,21 et qui grandit, achat de 347 jetons Down à 0,15 $ (52 $) avec un modèle à 0,35. Le BTC finit plus haut : **−52,06 $**.

## 3. Les 3 meilleurs des 60 derniers trades

| Heure (CH) | Côté | Prix | Jetons | Résultat |
|---|---|---|---|---|
| 09.10 00:52 | Down | 0.083 | 611 | +560.37 $ |
| 09.10 01:03 | Up | 0.190 | 294 | +238.36 $ |
| 09.10 02:22 | Up | 0.201 | 263 | +210.24 $ |

Sans ces 3 trades, les 60 derniers font −395 $.

> **À noter :** j'ai aussi essayé de reconstruire tous les trades depuis le 07.10 à partir des carnets enregistrés (4 mesures/s). La reconstruction ne retrouve pas le résultat réel (+254 $ au lieu de +3 254 $) : le bot décide à chaque mise à jour du carnet, plus souvent que l'enregistrement, et achète donc à des instants et prix légèrement différents. Elle n'est pas fiable comme liste de trades, je ne l'utilise pas ici.
---PAGE---
## Annexe — les 60 derniers trades réels

| # | Heure (CH) | Côté | Prix | Jetons | Mise | Modèle | Écart | Reste | Gagnant | Résultat | Cumul |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 09.10 00:40 | Down | 0.322 | 167 | 54 $ | 0.5 | 0.20 | 268 s | oui | +113.07 $ | +113.07 $ |
| 2 | 09.10 00:52 | Down | 0.083 | 611 | 51 $ | 0.287 | 0.22 | 146 s | oui | +560.37 $ | +673.44 $ |
| 3 | 09.10 00:58 | Down | 0.264 | 55 | 14 $ | 0.5 | 0.25 | 95 s | non | −14.49 $ | +658.95 $ |
| 4 | 09.10 01:03 | Up | 0.190 | 294 | 56 $ | 0.372 | 0.20 | 68 s | oui | +238.36 $ | +897.31 $ |
| 5 | 09.10 01:05 | Down | 0.261 | 208 | 54 $ | 0.486 | 0.25 | 276 s | non | −54.37 $ | +842.94 $ |
| 6 | 09.10 01:13 | Down | 0.038 | 563 | 22 $ | 0.284 | 0.25 | 71 s | non | −21.51 $ | +821.43 $ |
| 7 | 09.10 01:17 | Up | 0.086 | 625 | 54 $ | 0.282 | 0.20 | 134 s | non | −53.99 $ | +767.44 $ |
| 8 | 09.10 01:21 | Up | 0.350 | 152 | 53 $ | 0.591 | 0.26 | 235 s | non | −52.99 $ | +714.45 $ |
| 9 | 09.10 01:28 | Down | 0.355 | 109 | 39 $ | 0.54 | 0.21 | 85 s | non | −38.72 $ | +675.73 $ |
| 10 | 09.10 01:36 | Up | 0.346 | 152 | 52 $ | 0.547 | 0.22 | 233 s | non | −52.41 $ | +623.32 $ |
| 11 | 09.10 01:47 | Down | 0.106 | 276 | 29 $ | 0.306 | 0.22 | 128 s | non | −29.23 $ | +594.09 $ |
| 12 | 09.10 01:52 | Up | 0.191 | 13 | 3 $ | 0.388 | 0.21 | 134 s | oui | +10.82 $ | +604.91 $ |
| 13 | 09.10 01:56 | Down | 0.284 | 185 | 53 $ | 0.488 | 0.22 | 205 s | oui | +132.56 $ | +737.47 $ |
| 14 | 09.10 02:02 | Down | 0.113 | 153 | 17 $ | 0.301 | 0.20 | 146 s | oui | +135.51 $ | +872.98 $ |
| 15 | 09.10 02:10 | Down | 0.336 | 156 | 52 $ | 0.539 | 0.22 | 266 s | oui | +103.80 $ | +976.78 $ |
| 16 | 09.10 02:22 | Up | 0.201 | 263 | 53 $ | 0.407 | 0.22 | 179 s | oui | +210.24 $ | +1187.02 $ |
| 17 | 09.10 02:30 | Up | 0.243 | 217 | 53 $ | 0.441 | 0.21 | 251 s | non | −52.77 $ | +1134.25 $ |
| 18 | 09.10 02:38 | Down | 0.494 | 106 | 53 $ | 0.677 | 0.21 | 77 s | oui | +53.81 $ | +1188.06 $ |
| 19 | 09.10 02:48 | Up | 0.064 | 833 | 53 $ | 0.338 | 0.28 | 72 s | non | −53.38 $ | +1134.68 $ |
| 20 | 09.10 02:52 | Down | 0.230 | 238 | 55 $ | 0.442 | 0.23 | 155 s | oui | +183.29 $ | +1317.97 $ |
| 21 | 09.10 02:56 | Down | 0.377 | 139 | 52 $ | 0.561 | 0.20 | 226 s | non | −52.30 $ | +1265.67 $ |
| 22 | 09.10 03:01 | Down | 0.211 | 250 | 53 $ | 0.401 | 0.20 | 212 s | non | −52.88 $ | +1212.79 $ |
| 23 | 09.10 03:13 | Up | 0.050 | 938 | 47 $ | 0.241 | 0.20 | 117 s | non | −47.03 $ | +1165.76 $ |
| 24 | 09.10 03:17 | Up | 0.059 | 583 | 35 $ | 0.25 | 0.20 | 131 s | non | −34.52 $ | +1131.24 $ |
| 25 | 09.10 03:20 | Down | 0.435 | 122 | 53 $ | 0.61 | 0.20 | 259 s | oui | +68.87 $ | +1200.11 $ |
| 26 | 09.10 03:28 | Up | 0.085 | 400 | 34 $ | 0.271 | 0.20 | 80 s | non | −33.99 $ | +1166.12 $ |
| 27 | 09.10 03:32 | Up | 0.538 | 96 | 52 $ | 0.731 | 0.21 | 145 s | oui | +44.43 $ | +1210.55 $ |
| 28 | 09.10 03:37 | Down | 0.125 | 208 | 26 $ | 0.316 | 0.21 | 150 s | non | −25.99 $ | +1184.56 $ |
| 29 | 09.10 03:42 | Down | 0.047 | 126 | 6 $ | 0.24 | 0.20 | 153 s | non | −5.96 $ | +1178.60 $ |
| 30 | 09.10 03:52 | Down | 0.106 | 5 | 1 $ | 0.307 | 0.21 | 150 s | non | −0.50 $ | +1178.10 $ |
| 31 | 09.10 03:56 | Up | 0.149 | 357 | 53 $ | 0.378 | 0.24 | 239 s | non | −53.10 $ | +1125.00 $ |
| 32 | 09.10 04:02 | Up | 0.264 | 200 | 53 $ | 0.456 | 0.21 | 122 s | non | −52.70 $ | +1072.30 $ |
| 33 | 09.10 04:06 | Down | 0.259 | 208 | 54 $ | 0.441 | 0.20 | 214 s | non | −53.89 $ | +1018.41 $ |
| 34 | 09.10 04:12 | Up | 0.243 | 217 | 53 $ | 0.431 | 0.20 | 155 s | non | −52.77 $ | +965.64 $ |
| 35 | 09.10 04:21 | Down | 0.201 | 263 | 53 $ | 0.398 | 0.21 | 217 s | non | −52.92 $ | +912.72 $ |
| 36 | 09.10 04:28 | Up | 0.325 | 167 | 54 $ | 0.504 | 0.20 | 66 s | non | −54.13 $ | +858.59 $ |
| 37 | 09.10 04:32 | Up | 0.136 | 377 | 51 $ | 0.33 | 0.21 | 139 s | non | −51.42 $ | +807.17 $ |
| 38 | 09.10 04:35 | Down | 0.302 | 179 | 54 $ | 0.489 | 0.21 | 261 s | non | −53.87 $ | +753.30 $ |
| 39 | 09.10 04:46 | Down | 0.315 | 167 | 53 $ | 0.503 | 0.20 | 193 s | oui | +114.15 $ | +867.45 $ |
| 40 | 09.10 04:52 | Up | 0.229 | 238 | 54 $ | 0.415 | 0.20 | 173 s | oui | +183.69 $ | +1051.14 $ |
| 41 | 09.10 04:55 | Down | 0.232 | 227 | 53 $ | 0.484 | 0.26 | 295 s | non | −52.81 $ | +998.33 $ |
| 42 | 09.10 04:57 | Down | 0.253 | 208 | 53 $ | 0.6 | 0.36 | 144 s | non | −52.74 $ | +945.59 $ |
| 43 | 09.10 05:02 | Down | 0.156 | 192 | 30 $ | 0.353 | 0.21 | 171 s | non | −29.97 $ | +915.62 $ |
| 44 | 09.10 05:07 | Down | 0.168 | 69 | 12 $ | 0.352 | 0.20 | 147 s | non | −11.62 $ | +904.00 $ |
| 45 | 09.10 05:12 | Down | 0.231 | 238 | 55 $ | 0.41 | 0.20 | 145 s | non | −54.91 $ | +849.09 $ |
| 46 | 09.10 05:17 | Down | 0.284 | 16 | 5 $ | 0.474 | 0.20 | 168 s | non | −4.55 $ | +844.54 $ |
| 47 | 09.10 05:22 | Up | 0.170 | 75 | 13 $ | 0.364 | 0.20 | 144 s | non | −12.73 $ | +831.81 $ |
| 48 | 09.10 05:26 | Up | 0.217 | 149 | 32 $ | 0.406 | 0.21 | 239 s | non | −32.35 $ | +799.46 $ |
| 49 | 09.10 05:32 | Down | 0.221 | 250 | 55 $ | 0.408 | 0.21 | 170 s | non | −55.28 $ | +744.18 $ |
| 50 | 09.10 05:35 | Down | 0.254 | 208 | 53 $ | 0.461 | 0.22 | 253 s | oui | +155.36 $ | +899.54 $ |
| 51 | 09.10 05:41 | Up | 0.138 | 385 | 53 $ | 0.396 | 0.27 | 188 s | non | −53.13 $ | +846.41 $ |
| 52 | 09.10 05:46 | Up | 0.138 | 15 | 2 $ | 0.342 | 0.21 | 185 s | non | −2.02 $ | +844.39 $ |
| 53 | 09.10 05:50 | Up | 0.138 | 385 | 53 $ | 0.334 | 0.20 | 242 s | non | −53.13 $ | +791.26 $ |
| 54 | 09.10 05:55 | Down | 0.175 | 312 | 55 $ | 0.37 | 0.21 | 264 s | non | −54.67 $ | +736.59 $ |
| 55 | 09.10 06:01 | Up | 0.284 | 185 | 53 $ | 0.494 | 0.22 | 236 s | oui | +132.56 $ | +869.15 $ |
| 56 | 09.10 06:06 | Down | 0.294 | 179 | 53 $ | 0.485 | 0.21 | 213 s | non | −52.59 $ | +816.56 $ |
| 57 | 09.10 06:10 | Down | 0.211 | 250 | 53 $ | 0.502 | 0.30 | 251 s | non | −52.88 $ | +763.68 $ |
| 58 | 09.10 06:16 | Down | 0.198 | 278 | 55 $ | 0.388 | 0.21 | 185 s | non | −55.12 $ | +708.56 $ |
| 59 | 09.10 06:22 | Up | 0.040 | 1049 | 42 $ | 0.23 | 0.20 | 144 s | non | −42.34 $ | +666.22 $ |
| 60 | 09.10 06:27 | Down | 0.150 | 347 | 52 $ | 0.35 | 0.21 | 180 s | non | −52.06 $ | +614.16 $ |