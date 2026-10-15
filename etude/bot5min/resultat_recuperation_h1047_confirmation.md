# Bot95 — Récupération, faux sauvetages, trailing fondamental, protection sélective : H1047–H1050 (CONFIRMATION (≥ 13.10))

Généré le 15.10.2026 13:45 UTC. Étude séparée (le protocole figé H1003–H1046 n'est pas modifié). Cycles : apprentissage 216, validation 109, confirmation (≥ 13.10) 674. Position : 10 $ sur le favori du marché. Aucun ordre.

Cerveau B (apprentissage, 4559 décisions) : logit p = -0.073 + 0.010 × logit(M0) + 0.937 × logit(milieu).

## 1. H1047 — Récupération contre perte définitive (au premier instant défavorable)

| Échantillon | Détérioration d | Positions | Prix récupéré plus tard | Victoire finale | Perte définitive | Milieu Polymarket moyen | Cerveau B moyen | M0 moyen | Brier milieu | Brier cerveau B | Brier M0 | Cerveau B − milieu (IC 90 %) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| apprentissage | 0.10 | 122 | 63 % | 43 % | 57 % | 0.521 | 0.520 | 0.702 | 0.2447 | 0.2452 | 0.3473 | +0.0006 [-0.0022 ; +0.0033] |
| apprentissage | 0.15 | 113 | 56 % | 38 % | 62 % | 0.458 | 0.461 | 0.680 | 0.2347 | 0.2353 | 0.3473 | +0.0006 [-0.0023 ; +0.0035] |
| apprentissage | 0.20 | 102 | 45 % | 31 % | 69 % | 0.393 | 0.399 | 0.656 | 0.2076 | 0.2103 | 0.3626 | +0.0028 [-0.0001 ; +0.0056] |
| apprentissage | 0.30 | 95 | 34 % | 26 % | 74 % | 0.308 | 0.318 | 0.582 | 0.1842 | 0.1877 | 0.3649 | +0.0035 [+0.0008 ; +0.0062] |
| validation | 0.10 | 59 | 75 % | 61 % | 39 % | 0.549 | 0.552 | 0.730 | 0.2343 | 0.2341 | 0.2358 | -0.0002 [-0.0039 ; +0.0035] |
| validation | 0.15 | 53 | 66 % | 57 % | 43 % | 0.495 | 0.499 | 0.698 | 0.2323 | 0.2336 | 0.2416 | +0.0013 [-0.0028 ; +0.0053] |
| validation | 0.20 | 46 | 61 % | 50 % | 50 % | 0.439 | 0.446 | 0.644 | 0.2387 | 0.2385 | 0.2178 | -0.0003 [-0.0044 ; +0.0041] |
| validation | 0.30 | 36 | 44 % | 36 % | 64 % | 0.357 | 0.366 | 0.538 | 0.2042 | 0.2061 | 0.2072 | +0.0019 [-0.0028 ; +0.0065] |
| CONFIRMATION (≥ 13.10) | 0.10 | 396 | 66 % | 51 % | 49 % | 0.540 | 0.539 | 0.718 | 0.2462 | 0.2464 | 0.2936 | +0.0001 [-0.0014 ; +0.0016] |
| CONFIRMATION (≥ 13.10) | 0.15 | 359 | 58 % | 46 % | 54 % | 0.486 | 0.489 | 0.672 | 0.2470 | 0.2472 | 0.2926 | +0.0002 [-0.0014 ; +0.0019] |
| CONFIRMATION (≥ 13.10) | 0.20 | 335 | 53 % | 42 % | 58 % | 0.432 | 0.437 | 0.620 | 0.2381 | 0.2380 | 0.2771 | -0.0001 [-0.0018 ; +0.0016] |
| CONFIRMATION (≥ 13.10) | 0.30 | 285 | 39 % | 32 % | 68 % | 0.331 | 0.340 | 0.494 | 0.2093 | 0.2094 | 0.2439 | +0.0001 [-0.0017 ; +0.0018] |

**Par temps restant et perte latente liquidable (d = 0,15, toutes périodes hors apprentissage)** — récupération du prix / victoire finale / milieu moyen (n)

| Temps restant | perte -2 à +0 $ | perte -4 à -2 $ | perte -6 à -4 $ | perte < −6 $ |
|---|---|---|---|---|
| 181–240 s | — | 64 % / 50 % / 0.51 (227) | 65 % / 58 % / 0.39 (31) | — |
| 121–180 s | — | 60 % / 46 % / 0.52 (78) | 40 % / 25 % / 0.37 (20) | 0 % / 0 % / 0.22 (2) |
| 61–120 s | — | 41 % / 41 % / 0.51 (29) | 64 % / 55 % / 0.38 (11) | 0 % / 0 % / 0.23 (2) |
| 1–60 s | — | 25 % / 0 % / 0.43 (4) | 67 % / 50 % / 0.36 (6) | 50 % / 50 % / 0.25 (2) |

**Modèles (apprentissage) : AUC contre le milieu du marché seul**

| Cible | Échantillon | AUC milieu seul | AUC modèle (cerveau B, milieu, z Chainlink, temps restant, perte latente) |
|---|---|---|---|
| récupération du prix | validation | 0.730 | 0.681 |
| récupération du prix | CONFIRMATION (≥ 13.10) | 0.640 | 0.632 |
| victoire finale | validation | 0.683 | 0.656 |
| victoire finale | CONFIRMATION (≥ 13.10) | 0.612 | 0.587 |

## 2. H1048 — Coût des faux sauvetages (interventions H1036 contre R0, 164 ms)

### validation (109 cycles)

| Intervention | Pertes évitées ($, cycles perdants de R0) | Gagnants sacrifiés ($, cycles gagnants de R0) | Cycles gagnants abîmés | Jackpots supprimés | Frais en plus ($) | Coût d'écart en plus ($) | Capital supplémentaire moyen ($) | P&L − R0 ($) | IC 90 % |
|---|---|---|---|---|---|---|---|---|---|
| R1 vente totale | +132 | -184 | 26 / 60 | 0 | +11.0 | -1.4 | +0.00 | -52 | [-130 ; +23] |
| R3 couverture complète | +134 | -188 | 26 / 60 | 0 | +11.2 | -2.2 | +3.27 | -54 | [-134 ; +26] |
| R4 couverture tardive | +54 | -31 | 3 / 60 | 0 | +3.7 | +1.3 | +2.54 | +23 | [-13 ; +57] |
| R5 moitié-moitié | +133 | -186 | 26 / 60 | 0 | +11.1 | -1.8 | +0.40 | -53 | [-131 ; +25] |

### CONFIRMATION (≥ 13.10) (674 cycles)

| Intervention | Pertes évitées ($, cycles perdants de R0) | Gagnants sacrifiés ($, cycles gagnants de R0) | Cycles gagnants abîmés | Jackpots supprimés | Frais en plus ($) | Coût d'écart en plus ($) | Capital supplémentaire moyen ($) | P&L − R0 ($) | IC 90 % |
|---|---|---|---|---|---|---|---|---|---|
| R1 vente totale | +1109 | -1051 | 145 / 352 | 0 | +74.8 | +16.8 | +0.00 | +58 | [-153 ; +266] |
| R3 couverture complète | +1116 | -1056 | 145 / 352 | 0 | +75.2 | +16.6 | +3.67 | +60 | [-150 ; +265] |
| R4 couverture tardive | +456 | -536 | 48 / 352 | 0 | +34.5 | +9.5 | +3.80 | -79 | [-221 ; +52] |
| R5 moitié-moitié | +1126 | -1071 | 145 / 352 | 0 | +76.1 | +16.8 | +0.49 | +55 | [-150 ; +261] |

## 3. H1049 — Trailing fondamental contre trailing classique et conservation (164 ms)

### validation (109 cycles)

| Règle | Cycles où elle a agi | P&L net ($) | Cycles gagnants | Perte max | Gagnants sacrifiés ($) | Pertes évitées ($) | Frais ($) | Fills partiels | Capital max | P&L − H0 ($) | IC 90 % | IC corrigé (4) | 500 ms : P&L − H0 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| H0 | 0 | +25 | 60 | -10.0 | -0 | +0 | 16.1 | 0 | 10 | +0 | [+nan ; +nan] | [+nan ; +nan] | +0 |
| C1 | 63 | -59 | 24 | -4.3 | -250 | +165 | 30.2 | 18 | 10 | -84 | [-175 ; +8] | [-204 ; +36] | -81 |
| C2 | 28 | +2 | 63 | -10.0 | -78 | +55 | 20.9 | 6 | 10 | -23 | [-69 ; +30] | [-90 ; +52] | -41 |
| F1 | 28 | +58 | 54 | -9.4 | -47 | +80 | 21.2 | 9 | 10 | +33 | [-13 ; +77] | [-32 ; +93] | +19 |
| F2 | 22 | +45 | 59 | -10.0 | -12 | +31 | 18.0 | 2 | 10 | +19 | [-6 ; +40] | [-18 ; +46] | +14 |

### CONFIRMATION (≥ 13.10) (674 cycles)

| Règle | Cycles où elle a agi | P&L net ($) | Cycles gagnants | Perte max | Gagnants sacrifiés ($) | Pertes évitées ($) | Frais ($) | Fills partiels | Capital max | P&L − H0 ($) | IC 90 % | IC corrigé (4) | 500 ms : P&L − H0 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| H0 | 0 | -397 | 352 | -10.0 | -0 | +0 | 107.0 | 0 | 10 | +0 | [+nan ; +nan] | [+nan ; +nan] | +0 |
| C1 | 409 | -357 | 175 | -9.6 | -1287 | +1326 | 197.4 | 138 | 10 | +39 | [-187 ; +269] | [-274 ; +350] | -74 |
| C2 | 209 | -495 | 380 | -10.0 | -563 | +465 | 143.1 | 61 | 10 | -98 | [-239 ; +42] | [-280 ; +91] | -130 |
| F1 | 264 | -437 | 267 | -10.0 | -773 | +733 | 160.3 | 62 | 10 | -40 | [-207 ; +128] | [-274 ; +183] | -118 |
| F2 | 192 | -373 | 331 | -10.0 | -228 | +253 | 125.8 | 41 | 10 | +24 | [-68 ; +114] | [-112 ; +144] | -13 |

## 4. H1050 — Protection sélective après un gain réellement liquidable (164 ms)

### validation (109 cycles)

| Règle | Cycles où elle a agi | P&L net ($) | Cycles gagnants | Perte max | Gagnants sacrifiés ($) | Pertes évitées ($) | Frais ($) | Fills partiels | Capital max | P&L − H0 ($) | IC 90 % | IC corrigé (9) | 500 ms : P&L − H0 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| H0 | 0 | +25 | 60 | -10.0 | -0 | +0 | 16.1 | 0 | 10 | +0 | [+nan ; +nan] | [+nan ; +nan] | +0 |
| S-V-2 | 52 | -5 | 60 | -10.0 | -80 | +50 | 21.1 | 5 | 10 | -30 | [-71 ; +15] | [-85 ; +38] | -50 |
| S-A-2 | 46 | -3 | 60 | -10.0 | -79 | +50 | 21.1 | 0 | 13 | -29 | [-69 ; +17] | [-85 ; +44] | -49 |
| S-M-2 | 52 | -4 | 60 | -10.0 | -80 | +50 | 21.1 | 13 | 10 | -30 | [-71 ; +14] | [-90 ; +40] | -50 |
| S-V-5 | 14 | +29 | 60 | -10.0 | -7 | +10 | 16.5 | 1 | 10 | +3 | [-9 ; +23] | [-11 ; +36] | +1 |
| S-A-5 | 9 | +30 | 60 | -10.0 | -5 | +10 | 16.4 | 0 | 11 | +5 | [-7 ; +24] | [-10 ; +37] | -7 |
| S-M-5 | 14 | +29 | 60 | -10.0 | -7 | +10 | 16.5 | 6 | 10 | +3 | [-9 ; +23] | [-11 ; +34] | -4 |
| S-V-8 | 0 | +25 | 60 | -10.0 | -0 | +0 | 16.1 | 0 | 10 | +0 | [+0 ; +0] | [+0 ; +0] | +0 |
| S-A-8 | 0 | +25 | 60 | -10.0 | -0 | +0 | 16.1 | 0 | 10 | +0 | [+0 ; +0] | [+0 ; +0] | +0 |
| S-M-8 | 0 | +25 | 60 | -10.0 | -0 | +0 | 16.1 | 0 | 10 | +0 | [+0 ; +0] | [+0 ; +0] | +0 |

### CONFIRMATION (≥ 13.10) (674 cycles)

| Règle | Cycles où elle a agi | P&L net ($) | Cycles gagnants | Perte max | Gagnants sacrifiés ($) | Pertes évitées ($) | Frais ($) | Fills partiels | Capital max | P&L − H0 ($) | IC 90 % | IC corrigé (9) | 500 ms : P&L − H0 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| H0 | 0 | -397 | 352 | -10.0 | -0 | +0 | 107.0 | 0 | 10 | +0 | [+nan ; +nan] | [+nan ; +nan] | +0 |
| S-V-2 | 317 | -453 | 354 | -10.0 | -497 | +440 | 139.8 | 13 | 10 | -56 | [-173 ; +72] | [-239 ; +135] | -111 |
| S-A-2 | 281 | -458 | 359 | -10.0 | -492 | +431 | 139.4 | 0 | 14 | -61 | [-182 ; +59] | [-253 ; +138] | -117 |
| S-M-2 | 317 | -458 | 359 | -10.0 | -497 | +435 | 139.7 | 48 | 10 | -61 | [-181 ; +62] | [-233 ; +147] | -111 |
| S-V-5 | 96 | -409 | 353 | -10.0 | -52 | +40 | 110.4 | 1 | 10 | -12 | [-44 ; +24] | [-56 ; +50] | -21 |
| S-A-5 | 60 | -417 | 352 | -10.0 | -41 | +20 | 109.6 | 0 | 11 | -21 | [-42 ; +6] | [-50 ; +26] | -20 |
| S-M-5 | 96 | -406 | 352 | -10.0 | -49 | +40 | 110.2 | 35 | 10 | -9 | [-40 ; +28] | [-52 ; +49] | -18 |
| S-V-8 | 0 | -397 | 352 | -10.0 | -0 | +0 | 107.0 | 0 | 10 | +0 | [+0 ; +0] | [+0 ; +0] | +0 |
| S-A-8 | 0 | -397 | 352 | -10.0 | -0 | +0 | 107.0 | 0 | 10 | +0 | [+0 ; +0] | [+0 ; +0] | +0 |
| S-M-8 | 0 | -397 | 352 | -10.0 | -0 | +0 | 107.0 | 0 | 10 | +0 | [+0 ; +0] | [+0 ; +0] | +0 |

## 5. Latence (CONFIRMATION (≥ 13.10)) : P&L − H0 ($)

| Règle | 164 ms | 200 ms | 250 ms | 500 ms |
|---|---|---|---|---|
| C1 | +39 | +10 | -12 | -74 |
| C2 | -98 | -123 | -101 | -130 |
| F1 | -40 | -75 | -77 | -118 |
| F2 | +24 | +3 | +16 | -13 |
| S-V-2 | -56 | -85 | -84 | -111 |
| S-A-2 | -61 | -89 | -89 | -117 |
| S-M-2 | -61 | -88 | -87 | -111 |
| S-V-5 | -12 | -13 | -12 | -21 |
| S-A-5 | -21 | -21 | -19 | -20 |
| S-M-5 | -9 | -9 | -8 | -18 |
| S-V-8 | +0 | +0 | +0 | +0 |
| S-A-8 | +0 | +0 | +0 | +0 |
| S-M-8 | +0 | +0 | +0 | +0 |

## 6. Verdict (CONFIRMATION (≥ 13.10))

| Règle | IC corrigé > 0 | Validation même sens | > 0 à 500 ms | Verdict |
|---|---|---|---|---|
| C1 | non | non | non | abandonner |
| C2 | non | non | non | abandonner |
| F1 | non | oui | non | abandonner |
| F2 | non | oui | non | abandonner |
| S-V-2 | non | non | non | abandonner |
| S-A-2 | non | non | non | abandonner |
| S-M-2 | non | non | non | abandonner |
| S-V-5 | non | oui | non | abandonner |
| S-A-5 | non | oui | non | abandonner |
| S-M-5 | non | oui | non | abandonner |
| S-V-8 | non | non | non | abandonner |
| S-A-8 | non | non | non | abandonner |
| S-M-8 | non | non | non | abandonner |

## Limites
- Exécution preneur ; peu de cycles ; une seule famille d'entrée (favori) ; règles H1049/H1050 fixées a priori, sans réglage.

_Calcul : 1072 s._
