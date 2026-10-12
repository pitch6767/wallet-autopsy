# Bot95 — H833 à H835 : absorption, retrait de liquidité, autres actifs (apprentissage → test)

Généré le 12.10.2026 10:58 UTC. Cycles Dublin : 255 (11.10 08:45 → 12.10 06:05 UTC) ; apprentissage 127 cycles (avant 11.10 19:25 UTC), test 128. Résultat officiel connu pour 255 cycles. Aucun ordre ; bots, H816, H821, R4, fantômes inchangés ; période réservée non lue.

## 1. Couverture et qualité des données L2 (Dublin)

| Donnée | Secondes couvertes |
|---|---|
| Prix Binance spot | 97.3 % |
| Prix Bybit perp | 97.2 % |
| Prix OKX swap | 97.3 % |
| Prix Coinbase | 97.3 % |
| Chainlink | 97.3 % |
| Carnet Binance (meilleurs prix, cumuls) | 83.3 % |
| Carnet Bybit | 83.3 % |
| Photos 10 niveaux Binance (murs) | 81.7 % |

Secondes enregistrées : 76500 (21.2 h). Trous signalés par l'enregistreur : bn silence : 311, by silence : 25.

Limites : profondeur au-delà de 50 $ et au-delà de 10 niveaux non enregistrée ; liquidations Bybit agrégées seulement ; Deribit à partir du 12.10.

## 2. H833 — Absorption de liquidité

Variation BTC (Binance spot) après l'événement, signée dans le sens prévu (positif = la prévision était juste), en $. IC 90 % par cycles.

| Échantillon | Type | Sens du flux | Événements | 1 s | 3 s | 5 s | 10 s | 30 s | 60 s | 30 s en σ5 |
|---|---|---|---|---|---|---|---|---|---|---|
| apprentissage | absorption | achats | 10 | +0.0 [+0.0 ; +0.0] | +1.2 [+0.0 ; +3.5] | +1.2 [+0.0 ; +3.5] | -2.8 [-5.6 ; +0.0] | -16.3 [-46.1 ; +1.0] | -22.4 [-45.1 ; -4.2] | -4.31 |
| apprentissage | absorption | ventes | 18 | +0.0 [+0.0 ; +0.0] | +0.0 [+0.0 ; +0.0] | +0.0 [+0.0 ; +0.0] | +0.6 [-1.5 ; +2.9] | +1.5 [-7.0 ; +12.7] | -1.0 [-12.5 ; +12.6] | +0.40 |
| apprentissage | flux suivi | achats | 81 | +3.4 [+1.6 ; +5.5] | +6.1 [+2.2 ; +11.0] | +8.3 [+3.2 ; +14.9] | +8.7 [+3.2 ; +15.3] | +11.6 [+4.2 ; +20.2] | +11.5 [+4.0 ; +19.8] | +15.85 |
| apprentissage | flux suivi | ventes | 71 | +2.1 [+0.9 ; +3.3] | +2.3 [+1.1 ; +3.7] | +3.1 [+1.1 ; +5.2] | +4.4 [+2.1 ; +6.8] | +4.3 [-2.2 ; +9.4] | +8.0 [-1.5 ; +16.3] | +1.03 |
| test | absorption | achats | 25 | -2.3 [-4.4 ; -0.6] | -3.7 [-6.8 ; -0.9] | -3.9 [-7.0 ; -1.3] | -6.1 [-10.5 ; -2.1] | -3.7 [-12.4 ; +3.8] | -7.0 [-20.4 ; +4.4] | -0.16 |
| test | absorption | ventes | 21 | -2.7 [-6.0 ; -0.1] | -3.3 [-8.7 ; +0.5] | -3.9 [-9.6 ; +0.3] | -3.7 [-9.8 ; +1.5] | -4.2 [-11.4 ; +2.2] | -11.9 [-27.1 ; +0.2] | -0.94 |
| test | flux suivi | achats | 117 | +1.4 [+0.6 ; +2.3] | +3.2 [+2.1 ; +4.4] | +4.4 [+3.0 ; +5.9] | +5.3 [+3.4 ; +7.1] | +7.5 [+4.2 ; +10.7] | +3.6 [-2.7 ; +9.2] | +1.52 |
| test | flux suivi | ventes | 123 | +2.6 [+1.5 ; +3.9] | +4.7 [+3.3 ; +6.2] | +6.3 [+4.6 ; +8.1] | +7.5 [+5.3 ; +9.6] | +10.0 [+5.9 ; +14.0] | +5.6 [+0.7 ; +10.2] | +2.16 |

**Effet sur le règlement officiel** (événements avec 30 à 240 s restantes) : résultat − probabilité M0 au même instant, signé dans le sens prévu.

| Échantillon | Type | Événements | Écart moyen | IC 90 % par cycles |
|---|---|---|---|---|
| apprentissage | absorption | 12 | -0.177 | [-0.362 ; +0.008] |
| apprentissage | flux suivi | 101 | +0.140 | [+0.085 ; +0.200] |
| test | absorption | 27 | +0.056 | [-0.094 ; +0.208] |
| test | flux suivi | 147 | +0.096 | [+0.046 ; +0.148] |

## 3. H834 — Retrait de liquidité : annonce-t-il le mouvement ?

20935 instants (toutes les 3 s). Contrôles = variations passées 1/5/30 s et volatilité ; liquidité = OFI, retraits, profondeur, déséquilibres, microprix, écart, murs.

| Cible | Taux de base test | AUC contrôles seuls | AUC contrôles + liquidité | Écart (IC 90 % par cycles) |
|---|---|---|---|---|
| hausse à 10 s | 39 % | 0.617 | 0.702 | +0.085 [+0.075 ; +0.094] |
| hausse à 30 s | 45 % | 0.601 | 0.665 | +0.064 [+0.051 ; +0.077] |
| grand mouvement à 30 s, vers le haut | 12 % | 0.571 | 0.655 | +0.083 [+0.059 ; +0.106] |
| grand mouvement à 30 s, vers le bas | 13 % | 0.624 | 0.667 | +0.043 [+0.024 ; +0.060] |

## 4. H835 — Autres actifs et autres places

**(a) ETH et SOL contre BTC, Binance 1 s, 30 jours.** Corrélation simultanée ; avance = corrélation du rendement passé de l'actif sur k s avec le rendement futur de BTC sur k s ; R² hors échantillon (test 02.10 → 11.10) d'une régression BTC futur ~ BTC passé + actif passé, contre BTC passé seul.

| Actif | k | Corrélation simultanée | Avance (actif passé → BTC futur) | R² test BTC seul | R² test + actif | Gain de R² |
|---|---|---|---|---|---|---|
| ETH | 1 s | +0.678 | +0.1460 | +1.554 % | +2.253 % | +0.699 pt |
| ETH | 2 s | +0.725 | +0.1449 | +1.764 % | +2.402 % | +0.638 pt |
| ETH | 5 s | +0.777 | +0.1311 | +1.147 % | +1.587 % | +0.440 pt |
| ETH | 10 s | +0.807 | +0.0932 | +0.728 % | +1.229 % | +0.500 pt |
| ETH | 30 s | +0.840 | +0.0526 | -0.072 % | +0.083 % | +0.155 pt |
| SOL | 1 s | +0.545 | +0.1224 | +1.554 % | +2.053 % | +0.498 pt |
| SOL | 2 s | +0.614 | +0.1299 | +1.764 % | +2.299 % | +0.535 pt |
| SOL | 5 s | +0.692 | +0.1265 | +1.147 % | +1.717 % | +0.571 pt |
| SOL | 10 s | +0.735 | +0.0936 | +0.728 % | +1.122 % | +0.393 pt |
| SOL | 30 s | +0.778 | +0.0561 | -0.072 % | +0.181 % | +0.254 pt |

**(b) Places BTC à Dublin (50 ms, heures de réception)** : corrélation du rendement passé de la place sur Δ avec le rendement futur de Binance spot sur Δ, test.

| Place | Δ = 100 ms | 250 ms | 500 ms | 1 000 ms |
|---|---|---|---|---|
| perp | +0.397 | +0.378 | +0.334 | +0.292 |
| okx | +0.377 | +0.345 | +0.290 | +0.248 |
| cb | +0.068 | +0.074 | +0.092 | +0.127 |
| cl | +0.045 | +0.065 | +0.080 | +0.094 |

Nasdaq, or, devises, CME : non disponibles à la seconde (déclarés, non estimés). Deribit : enregistré depuis le 12.10, pour plus tard.

## 5. Modèles A / B / C / D sur les mêmes décisions

Décisions : apprentissage 466, test 738 (123 cycles).

**Toutes les décisions** (738 décisions, 123 cycles)

| Modèle | Brier | Log loss | Précision | Apport marginal (Brier, modèle précédent − celui-ci) | IC 90 % | IC corrigé (9) |
|---|---|---|---|---|---|---|
| A règlement seul | 0.1144 | 0.3594 | 85.1 % | — | — | — |
| B + flux BTC | 0.1140 | 0.3586 | 84.8 % | +0.00044 | [-0.00263 ; +0.00350] | [-0.00458 ; +0.00509] |
| C + liquidité L2 | 0.1111 | 0.3624 | 85.1 % | +0.00288 | [-0.00206 ; +0.00744] | [-0.00456 ; +0.00972] |
| D + autres places | 0.1108 | 0.3621 | 85.1 % | +0.00027 | [-0.00013 ; +0.00066] | [-0.00035 ; +0.00088] |

**Proches de 50 % (M0 entre 0,35 et 0,65)** (115 décisions, 69 cycles)

| Modèle | Brier | Log loss | Précision | Apport marginal (Brier, modèle précédent − celui-ci) | IC 90 % | IC corrigé (9) |
|---|---|---|---|---|---|---|
| A règlement seul | 0.2411 | 0.6753 | 58.3 % | — | — | — |
| B + flux BTC | 0.2377 | 0.6689 | 60.0 % | +0.00339 | [-0.00959 ; +0.01502] | [-0.01695 ; +0.02047] |
| C + liquidité L2 | 0.2455 | 0.6851 | 59.1 % | -0.00775 | [-0.02487 ; +0.00892] | [-0.03239 ; +0.01698] |
| D + autres places | 0.2455 | 0.6850 | 60.9 % | -0.00002 | [-0.00136 ; +0.00136] | [-0.00224 ; +0.00210] |

**Marge faible |z| < 0,5** (146 décisions, 78 cycles)

| Modèle | Brier | Log loss | Précision | Apport marginal (Brier, modèle précédent − celui-ci) | IC 90 % | IC corrigé (9) |
|---|---|---|---|---|---|---|
| A règlement seul | 0.2400 | 0.6731 | 59.6 % | — | — | — |
| B + flux BTC | 0.2392 | 0.6725 | 61.0 % | +0.00080 | [-0.00964 ; +0.01035] | [-0.01592 ; +0.01548] |
| C + liquidité L2 | 0.2386 | 0.6716 | 61.6 % | +0.00061 | [-0.01349 ; +0.01402] | [-0.02164 ; +0.02086] |
| D + autres places | 0.2389 | 0.6719 | 62.3 % | -0.00027 | [-0.00153 ; +0.00095] | [-0.00240 ; +0.00172] |

**Calibration (test, toutes décisions)**

| Probabilité annoncée | A : décisions / victoire | D : décisions / victoire |
|---|---|---|
| 0.0–0.2 | 184 / 3 % | 243 / 6 % |
| 0.2–0.4 | 124 / 16 % | 117 / 29 % |
| 0.4–0.6 | 163 / 52 % | 90 / 48 % |
| 0.6–0.8 | 94 / 85 % | 69 / 88 % |
| 0.8–1.0 | 173 / 95 % | 219 / 92 % |

## 6. P&L exécutable (test) : achat 20 $ si avantage ≥ 0,05 après frais, exécution à 164 ms, résultat officiel

| Modèle | Cycles avec achat | P&L ($) | Écart avec A ($) | IC 90 % (total, par cycles) |
|---|---|---|---|---|
| A règlement seul | 104 | -471 | +0 | — |
| B + flux BTC | 102 | -169 | +302 | [-136 ; +765] |
| C + liquidité L2 | 106 | +560 | +1031 | [+81 ; +2355] |
| D + autres places | 104 | +732 | +1203 | [+162 ; +2544] |

Cycles du test où le substitut Binance diffère du résultat officiel : 1 sur 123 (tous les résultats ci-dessus utilisent l'officiel).

_Calcul : 121 s._
