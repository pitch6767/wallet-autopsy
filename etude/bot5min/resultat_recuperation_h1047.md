# Bot95 — Récupération, faux sauvetages, trailing fondamental, protection sélective : H1047–H1050 (TEST)

Généré le 13.10.2026 00:47 UTC. Étude séparée (le protocole figé H1003–H1046 n'est pas modifié). Cycles : apprentissage 216, validation 109, test 144. Position : 10 $ sur le favori du marché. Aucun ordre.

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
| TEST | 0.10 | 88 | 64 % | 52 % | 48 % | 0.534 | 0.533 | 0.710 | 0.2398 | 0.2401 | 0.2953 | +0.0003 [-0.0028 ; +0.0034] |
| TEST | 0.15 | 74 | 54 % | 43 % | 57 % | 0.460 | 0.462 | 0.647 | 0.2490 | 0.2476 | 0.3046 | -0.0014 [-0.0047 ; +0.0020] |
| TEST | 0.20 | 69 | 43 % | 39 % | 61 % | 0.399 | 0.405 | 0.587 | 0.2348 | 0.2332 | 0.2983 | -0.0016 [-0.0051 ; +0.0019] |
| TEST | 0.30 | 64 | 38 % | 34 % | 66 % | 0.304 | 0.313 | 0.485 | 0.2209 | 0.2186 | 0.2756 | -0.0023 [-0.0061 ; +0.0012] |

**Par temps restant et perte latente liquidable (d = 0,15, toutes périodes hors apprentissage)** — récupération du prix / victoire finale / milieu moyen (n)

| Temps restant | perte -2 à +0 $ | perte -4 à -2 $ | perte -6 à -4 $ | perte < −6 $ |
|---|---|---|---|---|
| 181–240 s | — | 65 % / 53 % / 0.50 (75) | 64 % / 64 % / 0.40 (11) | — |
| 121–180 s | — | 68 % / 59 % / 0.51 (22) | 0 % / 0 % / 0.37 (3) | 0 % / 0 % / 0.26 (1) |
| 61–120 s | — | 43 % / 14 % / 0.48 (7) | 0 % / 0 % / 0.39 (3) | 0 % / 0 % / 0.23 (2) |
| 1–60 s | — | — | 100 % / 0 % / 0.45 (1) | 0 % / 50 % / 0.23 (2) |

**Modèles (apprentissage) : AUC contre le milieu du marché seul**

| Cible | Échantillon | AUC milieu seul | AUC modèle (cerveau B, milieu, z Chainlink, temps restant, perte latente) |
|---|---|---|---|
| récupération du prix | validation | 0.730 | 0.681 |
| récupération du prix | TEST | 0.701 | 0.680 |
| victoire finale | validation | 0.683 | 0.656 |
| victoire finale | TEST | 0.608 | 0.568 |

## 2. H1048 — Coût des faux sauvetages (interventions H1036 contre R0, 164 ms)

### validation (109 cycles)

| Intervention | Pertes évitées ($, cycles perdants de R0) | Gagnants sacrifiés ($, cycles gagnants de R0) | Cycles gagnants abîmés | Jackpots supprimés | Frais en plus ($) | Coût d'écart en plus ($) | Capital supplémentaire moyen ($) | P&L − R0 ($) | IC 90 % |
|---|---|---|---|---|---|---|---|---|---|
| R1 vente totale | +132 | -184 | 26 / 60 | 0 | +11.0 | -1.4 | +0.00 | -52 | [-130 ; +23] |
| R3 couverture complète | +134 | -188 | 26 / 60 | 0 | +11.2 | -2.2 | +3.27 | -54 | [-134 ; +26] |
| R4 couverture tardive | +54 | -31 | 3 / 60 | 0 | +3.7 | +1.3 | +2.54 | +23 | [-13 ; +57] |
| R5 moitié-moitié | +133 | -186 | 26 / 60 | 0 | +11.1 | -1.8 | +0.40 | -53 | [-131 ; +25] |

### TEST (144 cycles)

| Intervention | Pertes évitées ($, cycles perdants de R0) | Gagnants sacrifiés ($, cycles gagnants de R0) | Cycles gagnants abîmés | Jackpots supprimés | Frais en plus ($) | Coût d'écart en plus ($) | Capital supplémentaire moyen ($) | P&L − R0 ($) | IC 90 % |
|---|---|---|---|---|---|---|---|---|---|
| R1 vente totale | +233 | -234 | 29 / 72 | 0 | +16.4 | +3.7 | +0.00 | -1 | [-97 ; +94] |
| R3 couverture complète | +234 | -235 | 29 / 72 | 0 | +16.5 | +3.7 | +3.90 | -1 | [-100 ; +94] |
| R4 couverture tardive | +102 | -147 | 12 / 72 | 0 | +7.8 | +2.7 | +4.18 | -45 | [-121 ; +28] |
| R5 moitié-moitié | +234 | -237 | 29 / 72 | 0 | +16.5 | +3.8 | +0.59 | -3 | [-102 ; +93] |

## 3. H1049 — Trailing fondamental contre trailing classique et conservation (164 ms)

### validation (109 cycles)

| Règle | Cycles où elle a agi | P&L net ($) | Cycles gagnants | Perte max | Gagnants sacrifiés ($) | Pertes évitées ($) | Frais ($) | Fills partiels | Capital max | P&L − H0 ($) | IC 90 % | IC corrigé (4) | 500 ms : P&L − H0 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| H0 | 0 | +25 | 60 | -10.0 | -0 | +0 | 16.1 | 0 | 10 | +0 | [+nan ; +nan] | [+nan ; +nan] | +0 |
| C1 | 63 | -59 | 24 | -4.3 | -250 | +165 | 30.2 | 18 | 10 | -84 | [-173 ; +7] | [-204 ; +43] | -81 |
| C2 | 28 | +2 | 63 | -10.0 | -78 | +55 | 20.9 | 6 | 10 | -23 | [-71 ; +28] | [-89 ; +49] | -41 |
| F1 | 28 | +58 | 54 | -9.4 | -47 | +80 | 21.2 | 9 | 10 | +33 | [-12 ; +76] | [-28 ; +92] | +19 |
| F2 | 22 | +45 | 59 | -10.0 | -12 | +31 | 18.0 | 2 | 10 | +19 | [-6 ; +40] | [-18 ; +47] | +14 |

### TEST (144 cycles)

| Règle | Cycles où elle a agi | P&L net ($) | Cycles gagnants | Perte max | Gagnants sacrifiés ($) | Pertes évitées ($) | Frais ($) | Fills partiels | Capital max | P&L − H0 ($) | IC 90 % | IC corrigé (4) | 500 ms : P&L − H0 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| H0 | 0 | -98 | 72 | -10.0 | -0 | +0 | 22.5 | 0 | 10 | +0 | [+nan ; +nan] | [+nan ; +nan] | +0 |
| C1 | 86 | -88 | 34 | -8.5 | -286 | +296 | 42.0 | 20 | 10 | +10 | [-98 ; +126] | [-142 ; +158] | -44 |
| C2 | 43 | -99 | 77 | -10.0 | -115 | +114 | 30.0 | 14 | 10 | -1 | [-68 ; +69] | [-93 ; +104] | -5 |
| F1 | 59 | -162 | 53 | -9.9 | -189 | +125 | 33.3 | 16 | 10 | -63 | [-146 ; +14] | [-176 ; +41] | -81 |
| F2 | 42 | -142 | 65 | -10.0 | -84 | +40 | 26.2 | 6 | 10 | -44 | [-100 ; +6] | [-123 ; +21] | -51 |

## 4. H1050 — Protection sélective après un gain réellement liquidable (164 ms)

### validation (109 cycles)

| Règle | Cycles où elle a agi | P&L net ($) | Cycles gagnants | Perte max | Gagnants sacrifiés ($) | Pertes évitées ($) | Frais ($) | Fills partiels | Capital max | P&L − H0 ($) | IC 90 % | IC corrigé (9) | 500 ms : P&L − H0 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| H0 | 0 | +25 | 60 | -10.0 | -0 | +0 | 16.1 | 0 | 10 | +0 | [+nan ; +nan] | [+nan ; +nan] | +0 |
| S-V-2 | 52 | -5 | 60 | -10.0 | -80 | +50 | 21.1 | 5 | 10 | -30 | [-70 ; +15] | [-88 ; +44] | -50 |
| S-A-2 | 46 | -3 | 60 | -10.0 | -79 | +50 | 21.1 | 0 | 13 | -29 | [-69 ; +16] | [-87 ; +45] | -49 |
| S-M-2 | 52 | -4 | 60 | -10.0 | -80 | +50 | 21.1 | 13 | 10 | -30 | [-72 ; +17] | [-87 ; +38] | -50 |
| S-V-5 | 14 | +29 | 60 | -10.0 | -7 | +10 | 16.5 | 1 | 10 | +3 | [-9 ; +23] | [-11 ; +35] | +1 |
| S-A-5 | 9 | +30 | 60 | -10.0 | -5 | +10 | 16.4 | 0 | 11 | +5 | [-8 ; +25] | [-10 ; +36] | -7 |
| S-M-5 | 14 | +29 | 60 | -10.0 | -7 | +10 | 16.5 | 6 | 10 | +3 | [-9 ; +22] | [-11 ; +34] | -4 |
| S-V-8 | 0 | +25 | 60 | -10.0 | -0 | +0 | 16.1 | 0 | 10 | +0 | [+0 ; +0] | [+0 ; +0] | +0 |
| S-A-8 | 0 | +25 | 60 | -10.0 | -0 | +0 | 16.1 | 0 | 10 | +0 | [+0 ; +0] | [+0 ; +0] | +0 |
| S-M-8 | 0 | +25 | 60 | -10.0 | -0 | +0 | 16.1 | 0 | 10 | +0 | [+0 ; +0] | [+0 ; +0] | +0 |

### TEST (144 cycles)

| Règle | Cycles où elle a agi | P&L net ($) | Cycles gagnants | Perte max | Gagnants sacrifiés ($) | Pertes évitées ($) | Frais ($) | Fills partiels | Capital max | P&L − H0 ($) | IC 90 % | IC corrigé (9) | 500 ms : P&L − H0 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| H0 | 0 | -98 | 72 | -10.0 | -0 | +0 | 22.5 | 0 | 10 | +0 | [+nan ; +nan] | [+nan ; +nan] | +0 |
| S-V-2 | 64 | -86 | 75 | -10.0 | -98 | +110 | 29.2 | 5 | 10 | +13 | [-45 ; +75] | [-74 ; +111] | +11 |
| S-A-2 | 57 | -93 | 75 | -10.0 | -96 | +101 | 29.1 | 0 | 13 | +5 | [-53 ; +65] | [-80 ; +111] | -2 |
| S-M-2 | 64 | -85 | 75 | -10.0 | -98 | +111 | 29.2 | 11 | 10 | +13 | [-44 ; +76] | [-74 ; +113] | +7 |
| S-V-5 | 22 | -98 | 72 | -10.0 | -10 | +10 | 23.2 | 1 | 10 | -0 | [-13 ; +20] | [-15 ; +32] | -0 |
| S-A-5 | 12 | -96 | 72 | -10.0 | -8 | +10 | 23.0 | 0 | 11 | +2 | [-10 ; +23] | [-13 ; +36] | +4 |
| S-M-5 | 22 | -100 | 72 | -10.0 | -9 | +8 | 23.1 | 11 | 10 | -2 | [-12 ; +13] | [-14 ; +23] | -2 |
| S-V-8 | 0 | -98 | 72 | -10.0 | -0 | +0 | 22.5 | 0 | 10 | +0 | [+0 ; +0] | [+0 ; +0] | +0 |
| S-A-8 | 0 | -98 | 72 | -10.0 | -0 | +0 | 22.5 | 0 | 10 | +0 | [+0 ; +0] | [+0 ; +0] | +0 |
| S-M-8 | 0 | -98 | 72 | -10.0 | -0 | +0 | 22.5 | 0 | 10 | +0 | [+0 ; +0] | [+0 ; +0] | +0 |

## 5. Latence (TEST) : P&L − H0 ($)

| Règle | 164 ms | 200 ms | 250 ms | 500 ms |
|---|---|---|---|---|
| C1 | +10 | -10 | -23 | -44 |
| C2 | -1 | -10 | -22 | -5 |
| F1 | -63 | -66 | -72 | -81 |
| F2 | -44 | -47 | -45 | -51 |
| S-V-2 | +13 | +3 | -5 | +11 |
| S-A-2 | +5 | -2 | -11 | -2 |
| S-M-2 | +13 | +4 | -4 | +7 |
| S-V-5 | -0 | +0 | +0 | -0 |
| S-A-5 | +2 | +4 | +4 | +4 |
| S-M-5 | -2 | -2 | -2 | -2 |
| S-V-8 | +0 | +0 | +0 | +0 |
| S-A-8 | +0 | +0 | +0 | +0 |
| S-M-8 | +0 | +0 | +0 | +0 |

## 6. Verdict (TEST)

| Règle | IC corrigé > 0 | Validation même sens | > 0 à 500 ms | Verdict |
|---|---|---|---|---|
| C1 | non | non | non | abandonner |
| C2 | non | non | non | abandonner |
| F1 | non | oui | non | abandonner |
| F2 | non | oui | non | abandonner |
| S-V-2 | non | non | oui | abandonner |
| S-A-2 | non | non | non | abandonner |
| S-M-2 | non | non | oui | abandonner |
| S-V-5 | non | oui | non | abandonner |
| S-A-5 | non | oui | oui | abandonner |
| S-M-5 | non | oui | non | abandonner |
| S-V-8 | non | non | non | abandonner |
| S-A-8 | non | non | non | abandonner |
| S-M-8 | non | non | non | abandonner |

## Limites
- Exécution preneur ; peu de cycles ; une seule famille d'entrée (favori) ; règles H1049/H1050 fixées a priori, sans réglage.

_Calcul : 565 s._
