# Bot95 — H971 / H972 : pression contre capacité, effondrement de liquidité (apprentissage / validation / test inédit)

Généré le 12.10.2026 12:41 UTC. Cycles Dublin : apprentissage 169, validation 85, test 72 (test inédit = à partir du 12.10 06:00 UTC). Aucun ordre ; bots, H816, H821, R4, fantômes inchangés ; période réservée non lue.

## 1. H972 — Effondrement de capacité

Mouvement BTC Binance après l'événement, en $, signé dans le sens prévu (positif = juste). IC 90 % par cycles.

| Échantillon | Type | Événements | 1 s | 3 s | 5 s | 10 s | 30 s | 60 s |
|---|---|---|---|---|---|---|---|---|
| apprentissage | effondrement | 17 | +1.4 [+0.4 ; +2.8] | +4.2 [+1.4 ; +7.7] | +5.1 [+1.9 ; +9.3] | +4.8 [+1.2 ; +9.6] | +9.9 [+2.1 ; +20.0] | +14.3 [+6.0 ; +23.3] |
| apprentissage | témoin | 428 | +1.6 [+1.1 ; +2.1] | +3.0 [+2.0 ; +4.2] | +3.8 [+2.5 ; +5.4] | +4.3 [+2.9 ; +6.0] | +5.1 [+3.2 ; +7.0] | +4.1 [+1.6 ; +6.8] |
| validation | effondrement | 13 | +1.6 [+0.4 ; +3.1] | +1.9 [+0.4 ; +4.0] | +1.8 [+0.3 ; +3.9] | -0.4 [-5.8 ; +4.4] | -6.9 [-17.2 ; +2.1] | -15.3 [-35.2 ; +0.8] |
| validation | témoin | 304 | +2.3 [+1.6 ; +3.1] | +3.5 [+2.8 ; +4.3] | +4.5 [+3.6 ; +5.4] | +5.6 [+4.4 ; +6.9] | +7.6 [+5.2 ; +9.9] | +6.1 [+2.9 ; +9.1] |
| test | effondrement | 21 | +2.1 [+0.4 ; +3.8] | +2.4 [+0.5 ; +4.5] | +3.1 [+0.8 ; +6.0] | +4.7 [+1.3 ; +8.6] | +3.0 [-3.2 ; +8.6] | +1.4 [-6.5 ; +10.5] |
| test | témoin | 305 | +2.3 [+1.7 ; +2.9] | +3.1 [+2.5 ; +3.7] | +3.6 [+3.0 ; +4.3] | +4.4 [+3.2 ; +5.6] | +4.3 [+2.3 ; +6.3] | +3.4 [+0.2 ; +6.7] |

**Réévaluation Polymarket** (milieu du jeton prévu, en centimes, signé) et **règlement officiel** (résultat − M0, signé)

| Échantillon | Type | Polymarket 1 s | Polymarket 3 s | Polymarket 5 s | Polymarket 10 s | Polymarket 30 s | Règlement |
|---|---|---|---|---|---|---|---|
| apprentissage | effondrement | +1.67 [+0.68 ; +2.64] | +2.08 [-0.25 ; +4.68] | +2.79 [-0.08 ; +6.14] | +2.05 [-1.50 ; +6.40] | +10.73 [+0.66 ; +22.85] | +0.01 [-0.20 ; +0.24] (n=15) |
| apprentissage | témoin | +2.12 [+1.55 ; +2.74] | +3.00 [+2.21 ; +3.85] | +3.15 [+2.25 ; +4.10] | +2.37 [+1.38 ; +3.42] | +2.41 [+0.75 ; +4.02] | +0.10 [+0.07 ; +0.13] (n=315) |
| validation | effondrement | +1.73 [+0.32 ; +3.68] | +0.41 [-1.82 ; +2.86] | -0.32 [-2.82 ; +2.36] | -1.55 [-8.01 ; +4.18] | -5.49 [-12.91 ; +1.83] | -0.12 [-0.31 ; +0.04] (n=11) |
| validation | témoin | +2.34 [+1.45 ; +3.32] | +2.65 [+1.75 ; +3.62] | +2.59 [+1.55 ; +3.69] | +2.38 [+1.00 ; +3.76] | +0.88 [-1.24 ; +2.93] | +0.03 [-0.01 ; +0.07] (n=244) |
| test | effondrement | +0.54 [-0.46 ; +1.67] | -0.77 [-1.92 ; +0.46] | -0.85 [-2.79 ; +1.08] | -0.00 [-2.83 ; +2.64] | +0.12 [-5.96 ; +5.32] | +0.00 [-0.13 ; +0.10] (n=11) |
| test | témoin | +1.89 [+1.14 ; +2.69] | +1.28 [+0.48 ; +2.15] | +1.37 [+0.51 ; +2.29] | +1.14 [-0.10 ; +2.37] | +1.53 [-0.30 ; +3.46] | +0.06 [+0.02 ; +0.10] (n=153) |

**Occasion exécutable** : achat 20 $ du jeton prévu à 164 ms au prix vu (frais compris), (a) revente 30 s après au meilleur acheteur, (b) conservation.

| Échantillon | Type | Achats | (a) P&L total, revente à 30 s | IC 90 % (total) | (b) P&L total, règlement | IC 90 % (total) |
|---|---|---|---|---|---|---|
| apprentissage | effondrement | 10 | +26 | [-5 ; +68] | -4 | [-87 ; +88] |
| apprentissage | témoin | 255 | -117 | [-256 ; +46] | +56 | [-400 ; +576] |
| validation | effondrement | 4 | -8 | [-14 ; -2] | -31 | [-80 ; +10] |
| validation | témoin | 194 | -56 | [-294 ; +223] | +314 | [-675 ; +1906] |
| test | effondrement | 7 | -44 | [-90 ; -0] | -85 | [-140 ; -30] |
| test | témoin | 117 | -167 | [-311 ; -11] | -591 | [-902 ; -289] |

## 2. H971 — La pression rapportée à la capacité prévoit-elle mieux qu'OFI + momentum + volatilité ?

27626 instants (toutes les 3 s). IC corrigé : 10 comparaisons.

| Cible | Échantillon | Taux de base | AUC simple (OFI, momentum, volatilité) | AUC simple + pression/capacité | ΔAUC | IC 90 % | IC corrigé |
|---|---|---|---|---|---|---|---|
| hausse BTC à 10 s | validation | 38 % | 0.668 | 0.673 | +0.005 | [+0.001 ; +0.009] | [-0.001 ; +0.011] |
| hausse BTC à 10 s | test | 36 % | 0.657 | 0.662 | +0.004 | [-0.000 ; +0.009] | [-0.004 ; +0.011] |
| hausse BTC à 30 s | validation | 46 % | 0.618 | 0.615 | -0.003 | [-0.008 ; +0.004] | [-0.010 ; +0.007] |
| hausse BTC à 30 s | test | 42 % | 0.617 | 0.613 | -0.005 | [-0.013 ; +0.003] | [-0.016 ; +0.007] |
| grand mouvement à 30 s vers le haut | validation | 13 % | 0.618 | 0.629 | +0.011 | [+0.001 ; +0.025] | [-0.005 ; +0.032] |
| grand mouvement à 30 s vers le haut | test | 11 % | 0.639 | 0.627 | -0.012 | [-0.025 ; -0.000] | [-0.033 ; +0.006] |
| grand mouvement à 30 s vers le bas | validation | 13 % | 0.649 | 0.641 | -0.008 | [-0.016 ; +0.001] | [-0.018 ; +0.004] |
| grand mouvement à 30 s vers le bas | test | 14 % | 0.611 | 0.617 | +0.007 | [-0.002 ; +0.015] | [-0.007 ; +0.018] |
| milieu Polymarket Up +1 c à 10 s | validation | 45 % | 0.537 | 0.535 | -0.002 | [-0.007 ; +0.002] | [-0.008 ; +0.005] |
| milieu Polymarket Up +1 c à 10 s | test | 39 % | 0.566 | 0.558 | -0.008 | [-0.013 ; -0.001] | [-0.017 ; +0.001] |

## 3. Règlement officiel : modèle A (règlement seul, recalibré) contre A + pression/capacité

| Échantillon | Sous-ensemble | Décisions | Brier A | Brier A + PC | Log loss A / A + PC | Précision A / A + PC | ΔBrier (A − A+PC) | IC 90 % | IC corrigé (6) |
|---|---|---|---|---|---|---|---|---|---|
| validation | toutes | 492 | 0.1150 | 0.1262 | 0.364 / 0.394 | 85 % / 83 % | -0.01117 | [-0.01960 ; -0.00297] | [-0.02396 ; +0.00015] |
| validation | proches de 50 % | 83 | 0.2456 | 0.2643 | 0.684 / 0.749 | 52 % / 54 % | -0.01876 | [-0.04746 ; +0.00560] | [-0.06153 ; +0.01574] |
| validation | marge faible | 102 | 0.2390 | 0.2517 | 0.671 / 0.717 | 57 % / 59 % | -0.01276 | [-0.03650 ; +0.00852] | [-0.05016 ; +0.01821] |
| test | toutes | 252 | 0.0805 | 0.0914 | 0.265 / 0.297 | 92 % / 88 % | -0.01085 | [-0.02010 ; -0.00205] | [-0.02400 ; +0.00102] |
| test | proches de 50 % | 35 | 0.2397 | 0.2385 | 0.673 / 0.752 | 71 % / 63 % | +0.00127 | [-0.03656 ; +0.03887] | [-0.05371 ; +0.06057] |
| test | marge faible | 45 | 0.2425 | 0.2606 | 0.678 / 0.779 | 67 % / 56 % | -0.01810 | [-0.05359 ; +0.01876] | [-0.06673 ; +0.03778] |

## Limites
- Carnet Binance limité à 50 $ du meilleur prix ; Bybit et OKX sans carnet profond enregistré ; liquidations agrégées seulement.
- Quelques dizaines d'heures de données ; test inédit d'environ 6 h.
- Le milieu Polymarket est reconstruit (photos 10 s + changements à ±3 c).

_Calcul : 174 s._
