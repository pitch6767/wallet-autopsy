# Bot95 — H976 / H977 / H978 : flux de début de cycle face au prix Polymarket, déplacement de cotations, alerte multi-actifs

Généré le 12.10.2026 13:04 UTC. Cycles Dublin : apprentissage 169, validation 85, test 71, nouveau 12 (test = 12.10 06:00–12:00 UTC, déjà consulté pour H941 ; nouveau = à partir du 12.10 12:00 UTC). Résultats officiels. Aucun ordre ; période réservée non lue.

## 1. H977 — Le flux de début de cycle crée-t-il une sous-évaluation réelle des billets Polymarket ?

Une décision par cycle : la première vague forte entre 150 et 240 s restantes, côté X = sens du flux. δ appris sur l'apprentissage = +1.08 (logit).

**Qualité des probabilités pour le côté X** (Brier, log loss ; plus bas = mieux)

| Échantillon | Décisions | Victoire X | A règlement seul | B prix Polymarket (milieu) | C règlement + effet H941 | B − A (Brier, IC 90 %) | B − C (Brier, IC 90 %) |
|---|---|---|---|---|---|---|---|
| apprentissage | 61 | 75 % | 0.206 / 0.609 | 0.178 / 0.523 | 0.155 / 0.505 | -0.03 [-0.05 ; -0.01] | +0.02 [-0.01 ; +0.06] |
| validation | 45 | 64 % | 0.176 / 0.538 | 0.157 / 0.490 | 0.182 / 0.554 | -0.02 [-0.05 ; +0.01] | -0.03 [-0.06 ; +0.01] |
| test | 27 | 70 % | 0.142 / 0.444 | 0.125 / 0.403 | 0.140 / 0.424 | -0.02 [-0.04 ; +0.01] | -0.01 [-0.06 ; +0.03] |
| nouveau | 1 | — | — | — | — | — | — |

**Avantage face au marché et P&L** (achat 20 $ du jeton X à 164 ms au prix vendeur vu, frais compris, conservation, résultat officiel)

| Échantillon | Règle | Achats | Victoire | Prix payé moyen | Avantage par achat (résultat − prix − frais, IC 90 %) | P&L ($) | IC 90 % total | Gagnants / perdants | Jackpots (≥ +20 $) | Drawdown |
|---|---|---|---|---|---|---|---|---|---|---|
| apprentissage | R0 toujours | 44 | 77 % | 0.643 | +0.13 [+0.03 ; +0.23] | +285 | [+59 ; +522] | 34 / 10 | 8 | 79 |
| apprentissage | R1 C − prix ≥ 0 | 37 | 73 % | 0.589 | +0.14 [+0.02 ; +0.25] | +273 | [+47 ; +509] | 27 / 10 | 8 | 81 |
| apprentissage | R2 C − prix ≥ 0,05 | 29 | 69 % | 0.535 | +0.15 [+0.01 ; +0.30] | +268 | [+42 ; +505] | 20 / 9 | 8 | 85 |
| validation | R0 toujours | 29 | 72 % | 0.737 | -0.01 [-0.14 ; +0.10] | -25 | [-135 ; +79] | 21 / 8 | 1 | 88 |
| validation | R1 C − prix ≥ 0 | 25 | 72 % | 0.725 | -0.00 [-0.13 ; +0.11] | -33 | [-127 ; +60] | 18 / 7 | 0 | 68 |
| validation | R2 C − prix ≥ 0,05 | 17 | 59 % | 0.638 | -0.05 [-0.24 ; +0.13] | -49 | [-144 ; +42] | 10 / 7 | 0 | 81 |
| test | R0 toujours | 20 | 65 % | 0.655 | -0.01 [-0.15 ; +0.13] | -47 | [-146 ; +50] | 13 / 7 | 0 | 62 |
| test | R1 C − prix ≥ 0 | 18 | 61 % | 0.627 | -0.02 [-0.17 ; +0.14] | -51 | [-146 ; +39] | 11 / 7 | 0 | 65 |
| test | R2 C − prix ≥ 0,05 | 11 | 64 % | 0.551 | +0.09 [-0.12 ; +0.28] | -5 | [-87 ; +77] | 7 / 4 | 0 | 26 |
| nouveau | R0 toujours | 1 | 0 % | 0.656 | — (n=1) | -20 | [+nan ; +nan] | 0 / 1 | 0 | 20 |
| nouveau | R1 C − prix ≥ 0 | 1 | 0 % | 0.656 | — (n=1) | -20 | [+nan ; +nan] | 0 / 1 | 0 | 20 |
| nouveau | R2 C − prix ≥ 0,05 | 1 | 0 % | 0.656 | — (n=1) | -20 | [+nan ; +nan] | 0 / 1 | 0 | 20 |

**Sensibilité à la latence (R0)** et **proches de 50 %** (A entre 0,35 et 0,65)

| Échantillon | P&L R0 à 164 / 300 / 500 ms ($) | Proches de 50 % : achats, victoire, avantage par achat |
|---|---|---|
| apprentissage | +285 / +256 / +267 | 21, 76 %, +0.13 [-0.03 ; +0.28] |
| validation | -25 / -32 / -9 | 11, 55 %, -0.07 [-0.29 ; +0.17] |
| test | -47 / -53 / -59 | 11, 64 %, +0.07 [-0.15 ; +0.27] |
| nouveau | -20 / -20 / -20 | 1, 0 %, — (n=1) |

**Calibration (toutes périodes hors apprentissage)** : victoire observée selon le prix Polymarket payé

| Prix vendeur du jeton X | Achats | Victoire observée | Prix moyen |
|---|---|---|---|
| 0.0–0.3 | 6 | 0 % | 0.14 |
| 0.3–0.5 | 10 | 30 % | 0.42 |
| 0.5–0.7 | 22 | 64 % | 0.60 |
| 0.7–0.9 | 21 | 90 % | 0.80 |
| 0.9–1.0 | 14 | 86 % | 0.94 |

## 2. H976 — Déplacement de cotations derrière les retraits synchronisés

Mouvement BTC signé dans le sens observé en H956 (retrait vendeur → baisse), en $, à partir de la seconde du retrait ; puis à partir de t + 2 s (après le classement).

| Échantillon | Classe | Événements | 1 s | 3 s | 5 s | 10 s | 30 s | 5 s après t+2 | 10 s après t+2 |
|---|---|---|---|---|---|---|---|---|---|
| apprentissage | déplacement | 834 | +4.71 [+3.68 ; +5.66] | +9.89 [+7.68 ; +11.94] | +11.17 [+8.81 ; +13.27] | +12.26 [+10.49 ; +13.82] | +12.87 [+10.77 ; +14.87] | +3.67 [+2.41 ; +4.84] | +3.60 [+1.99 ; +5.18] |
| apprentissage | annulation | 1395 | -1.09 [-1.65 ; -0.49] | -2.34 [-3.70 ; -1.01] | -2.00 [-3.28 ; -0.56] | -1.34 [-3.25 ; +0.54] | -1.29 [-3.71 ; +1.07] | +0.40 [-0.39 ; +1.14] | +1.18 [+0.29 ; +2.08] |
| validation | déplacement | 841 | +3.66 [+3.30 ; +3.99] | +7.24 [+6.39 ; +8.00] | +8.93 [+7.88 ; +9.90] | +10.80 [+9.54 ; +12.00] | +12.44 [+10.03 ; +14.91] | +3.89 [+3.10 ; +4.63] | +4.86 [+3.83 ; +5.85] |
| validation | annulation | 1384 | -0.33 [-0.49 ; -0.18] | -0.61 [-0.89 ; -0.32] | +0.01 [-0.30 ; +0.34] | +0.43 [-0.22 ; +1.08] | +0.62 [-0.47 ; +1.74] | +1.04 [+0.72 ; +1.39] | +1.49 [+0.97 ; +2.03] |
| test | déplacement | 615 | +3.51 [+3.12 ; +3.87] | +7.44 [+6.72 ; +8.11] | +8.95 [+8.02 ; +9.75] | +11.31 [+9.96 ; +12.52] | +12.09 [+10.01 ; +14.19] | +3.89 [+3.10 ; +4.66] | +5.23 [+3.82 ; +6.60] |
| test | annulation | 1064 | -0.33 [-0.54 ; -0.11] | -0.89 [-1.48 ; -0.34] | -0.51 [-1.11 ; +0.08] | -0.21 [-1.02 ; +0.56] | +0.39 [-1.19 ; +1.96] | +0.82 [+0.40 ; +1.24] | +0.96 [+0.21 ; +1.66] |
| nouveau | déplacement | 297 | +4.99 [+3.48 ; +5.51] | +10.89 [+8.23 ; +11.93] | +11.91 [+9.75 ; +14.19] | +13.55 [+10.06 ; +16.06] | +13.55 [+8.25 ; +19.05] | +3.08 [+1.37 ; +6.35] | +3.62 [+2.07 ; +6.69] |
| nouveau | annulation | 400 | -2.59 [-3.82 ; -0.61] | -4.56 [-6.52 ; -1.24] | -4.41 [-6.34 ; -1.02] | -4.01 [-6.03 ; -0.23] | -2.70 [-5.08 ; +2.52] | +0.65 [+0.03 ; +1.22] | +1.37 [+0.30 ; +2.30] |

**Apport marginal pour prévoir le signe du mouvement BTC** (AUC ; IC corrigé pour 12 comparaisons)

| Cible | Échantillon | AUC A (OFI, momentum, volatilité) | AUC B (+ retraits synchronisés) | AUC C (+ déplacement) | B − A (IC corrigé) | C − B (IC corrigé) |
|---|---|---|---|---|---|---|
| hausse à 10 s | validation | 0.668 | 0.668 | 0.670 | -0.000 [-0.004 ; +0.003] | +0.003 [+0.001 ; +0.004] |
| hausse à 10 s | test | 0.658 | 0.655 | 0.657 | -0.002 [-0.007 ; +0.002] | +0.002 [-0.001 ; +0.005] |
| hausse à 10 s | nouveau | 0.690 | 0.684 | 0.684 | -0.005 [-0.014 ; +0.004] | +0.000 [-0.006 ; +0.007] |
| hausse à 30 s | validation | 0.618 | 0.619 | 0.618 | +0.000 [-0.004 ; +0.005] | -0.000 [-0.002 ; +0.002] |
| hausse à 30 s | test | 0.618 | 0.616 | 0.615 | -0.002 [-0.007 ; +0.003] | -0.001 [-0.004 ; +0.002] |
| hausse à 30 s | nouveau | 0.640 | 0.636 | 0.632 | -0.004 [-0.014 ; +0.007] | -0.004 [-0.011 ; +0.004] |

## 3. H978 — Un autre actif précède-t-il les vagues BTC ?

**(a) Binance 1 s, 30 jours** : 40742 vagues BTC. Part des vagues où l'actif a déjà bougé dans le même sens dans les k s avant le début de la vague (fenêtre de 5 s de la vague exclue), comparée à des instants tirés au hasard.

| Actif | k | Vagues (test) : même sens avant | Hasard | Écart (IC 90 % par jours) |
|---|---|---|---|---|
| ETH | 1 s | 25.4 % | 23.3 % | +2.1 pts [-0.0 ; +3.9] |
| ETH | 2 s | 33.3 % | 30.6 % | +2.7 pts [+0.6 ; +4.5] |
| ETH | 5 s | 42.4 % | 37.4 % | +5.0 pts [+2.8 ; +6.7] |
| ETH | 10 s | 48.2 % | 42.3 % | +6.0 pts [+3.9 ; +7.6] |
| SOL | 1 s | 20.4 % | 18.8 % | +1.6 pts [-0.2 ; +3.0] |
| SOL | 2 s | 28.4 % | 26.1 % | +2.3 pts [+0.6 ; +3.8] |
| SOL | 5 s | 38.0 % | 33.7 % | +4.3 pts [+2.5 ; +5.8] |
| SOL | 10 s | 44.2 % | 38.4 % | +5.8 pts [+4.2 ; +7.2] |

Prévoir le **sens** d'une vague BTC avec les données arrêtées 5 s avant son début (test 02.10 → 11.10) : AUC BTC seul 0.605, avec ETH/SOL 0.618, écart +0.013 [+0.005 ; +0.020].

**(b) Dublin (heures de réception)** : mouvement des autres places dans les 2 s avant les vagues de début de cycle (signé dans le sens de la vague, en $), comparé à Binance spot sur la même fenêtre.

| Échantillon | Vagues | Binance spot | Perp Bybit | OKX | Coinbase | Chainlink |
|---|---|---|---|---|---|---|
| apprentissage | 130 | +1.91 [+0.55 ; +3.81] | +1.79 [+0.79 ; +2.91] | +3.32 [+1.27 ; +5.90] | +2.55 [+0.88 ; +4.50] | +2.50 [+0.74 ; +4.51] |
| validation | 106 | +1.86 [+0.77 ; +3.25] | +2.22 [+1.00 ; +3.74] | +1.98 [+0.81 ; +3.55] | +2.77 [+1.14 ; +4.68] | +1.10 [+0.60 ; +1.62] |
| test | 120 | +0.77 [-0.13 ; +1.61] | +1.37 [+0.33 ; +2.31] | +1.00 [-0.09 ; +2.02] | +0.78 [-0.70 ; +2.11] | +0.87 [+0.03 ; +1.76] |
| nouveau | 17 | +6.02 [+1.26 ; +10.11] | +1.98 [+0.21 ; +4.34] | +6.35 [+0.91 ; +10.71] | +3.93 [+1.51 ; +5.82] | +9.43 [+1.01 ; +17.95] |

Nasdaq, or, devises, CME : non disponibles à la seconde. ETH et SOL ne sont pas enregistrés à Dublin : effet sur le règlement Polymarket et exécution non mesurables pour eux. Deribit enregistré depuis le 12.10 11:55 UTC seulement.

## Limites
- Échantillon « nouveau » de quelques dizaines de cycles seulement. Test déjà consulté pour H941.
- Une décision par cycle pour H977 : faible nombre de décisions par échantillon.

_Calcul : 128 s._
