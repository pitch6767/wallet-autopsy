# Bot95 — Adaptive Reversal & Hedge Engine H1003–H1035 (TEST)

Généré le 13.10.2026 00:47 UTC. Cycles avec résultat officiel : apprentissage 216, validation 109, test 144. Capital ≤ 50 $, limite 5 CHF = 6.00 $. Exécution preneur sur le carnet enregistré. Aucun ordre ; aucun fantôme modifié.

## 1. Cerveau A — trajectoire courte du BTC (H1004, H1009, H1019, H1026–H1028)

| Cible | Échantillon | Taux de base | AUC momentum seul | AUC toutes familles | Gain d'AUC (IC 90 %) |
|---|---|---|---|---|---|
| hausse à 1 s | validation | 22.0 % | 0.578 | 0.618 | +0.040 [+0.031 ; +0.049] |
| hausse à 1 s | TEST | 26.0 % | 0.587 | 0.634 | +0.047 [+0.041 ; +0.054] |
| hausse à 3 s | validation | 29.7 % | 0.604 | 0.666 | +0.062 [+0.055 ; +0.070] |
| hausse à 3 s | TEST | 34.4 % | 0.609 | 0.676 | +0.067 [+0.060 ; +0.074] |
| hausse à 5 s | validation | 32.1 % | 0.619 | 0.692 | +0.072 [+0.064 ; +0.081] |
| hausse à 5 s | TEST | 36.8 % | 0.628 | 0.692 | +0.064 [+0.057 ; +0.072] |
| hausse à 10 s | validation | 35.9 % | 0.623 | 0.700 | +0.077 [+0.067 ; +0.088] |
| hausse à 10 s | TEST | 41.9 % | 0.618 | 0.686 | +0.068 [+0.061 ; +0.076] |
| hausse à 15 s | validation | 39.3 % | 0.603 | 0.692 | +0.089 [+0.079 ; +0.101] |
| hausse à 15 s | TEST | 43.9 % | 0.599 | 0.668 | +0.069 [+0.060 ; +0.078] |
| hausse à 30 s | validation | 43.1 % | 0.591 | 0.663 | +0.072 [+0.059 ; +0.088] |
| hausse à 30 s | TEST | 47.0 % | 0.569 | 0.626 | +0.057 [+0.044 ; +0.070] |
| hausse à 60 s | validation | 44.7 % | 0.576 | 0.623 | +0.047 [+0.029 ; +0.067] |
| hausse à 60 s | TEST | 48.6 % | 0.547 | 0.587 | +0.040 [+0.024 ; +0.055] |
| retournement à 30 s | validation | 24.8 % | 0.556 | 0.556 | +0.000 [-0.005 ; +0.006] |
| retournement à 30 s | TEST | 27.7 % | 0.557 | 0.552 | -0.004 [-0.011 ; +0.003] |

**Ablation (hausse à 30 s) : perte d'AUC quand on retire une famille** (positif = la famille apporte)

| Famille retirée | validation | TEST |
|---|---|---|
| mom | +0.0043 [+0.0002 ; +0.0081] | +0.0059 [+0.0018 ; +0.0104] |
| flux | +0.0014 [+0.0008 ; +0.0020] | -0.0007 [-0.0014 ; +0.0002] |
| carnet | +0.0606 [+0.0486 ; +0.0742] | +0.0466 [+0.0366 ; +0.0580] |
| inter | +0.0001 [+0.0000 ; +0.0003] | +0.0002 [+0.0001 ; +0.0003] |
| liq | -0.0000 [-0.0006 ; +0.0005] | -0.0002 [-0.0007 ; +0.0003] |
| cl | +0.0001 [+0.0000 ; +0.0001] | +0.0000 [+0.0000 ; +0.0001] |

**Ampleur du mouvement à 30 s (H1009)** — Brier : modèle gaussien (volatilité seule) contre logistique toutes familles

| Seuil | Échantillon | Fréquence | Brier gaussien | Brier modèle | Différence (IC 90 %) |
|---|---|---|---|---|---|
| ≥ 5 $ | validation | 65.0 % | 0.2208 | 0.2225 | +0.0017 [-0.0021 ; +0.0056] |
| ≥ 5 $ | TEST | 70.6 % | 0.1875 | 0.1877 | +0.0002 [-0.0031 ; +0.0034] |
| ≥ 10 $ | validation | 48.6 % | 0.2576 | 0.2482 | -0.0094 [-0.0132 ; -0.0057] |
| ≥ 10 $ | TEST | 56.2 % | 0.2297 | 0.2273 | -0.0024 [-0.0055 ; +0.0007] |
| ≥ 20 $ | validation | 24.3 % | 0.1912 | 0.1792 | -0.0120 [-0.0152 ; -0.0089] |
| ≥ 20 $ | TEST | 33.2 % | 0.2091 | 0.2048 | -0.0043 [-0.0072 ; -0.0015] |
| ≥ 40 $ | validation | 5.6 % | 0.0531 | 0.0515 | -0.0017 [-0.0025 ; -0.0008] |
| ≥ 40 $ | TEST | 12.0 % | 0.0997 | 0.0988 | -0.0009 [-0.0027 ; +0.0009] |

## 2. Cerveau B — probabilité de règlement (H1016)

logit p = -0.073 + 0.010 × logit(M0) + 0.937 × logit(milieu Polymarket) (sans milieu : -0.068 + 0.481 × logit(M0)) ; 4559 décisions d'apprentissage.


# FAMILLE D'ENTRÉE : avantage du cerveau B ≥ e


**Calibration de règlement (H1016, décisions toutes les 10 s)** — Brier et log loss ; écart = cerveau B − milieu du marché

| Échantillon | Décisions | Brier marché | Brier M0 brut | Brier cerveau B | Cerveau B − marché (IC 90 %) | LL marché | LL cerveau B | Ajout de a30 (H1026) : ΔBrier (IC 90 %) |
|---|---|---|---|---|---|---|---|---|
| apprentissage | 4559 | 0.1683 | 0.1844 | 0.1678 | -0.0005 [-0.0019 ; +0.0010] | 0.4981 | 0.4974 | -0.00044 [-0.00120 ; +0.00029] |
| validation | 2301 | 0.1363 | 0.1308 | 0.1364 | +0.0001 [-0.0017 ; +0.0018] | 0.4226 | 0.4237 | -0.00062 [-0.00163 ; +0.00045] |
| TEST | 2968 | 0.1772 | 0.1880 | 0.1770 | -0.0002 [-0.0021 ; +0.0015] | 0.5231 | 0.5227 | -0.00071 [-0.00234 ; +0.00078] |

Seuil d'entrée e choisi sur l'apprentissage (T0-50) : **0.05** (e=0.05 → +0 $, e=0.10 → +0 $, e=0.15 → +0 $).

Attribution RS (apprentissage) : aucun signal → T0-50.


## 3. Tournoi T0–T7 (H1034), latence 164 ms

### apprentissage (sert au choix de e et de RS) (216 cycles)

| Politique | Cycles actifs | P&L net ($) | Par cycle actif | Par $ de capital max | Cycles gagnants | Perte max | Pertes > 6 $ | Drawdown | ES 5 % | Capital max | Achats / ventes | Frais ($) | Coût d'écart ($) | Parts achetées | P&L couvertures ($) | Plancher le plus bas (moy.) | Jackpots conservés | Sans les 5 meilleurs | Écart avec T0-50 ($) | IC 90 % | IC corrigé (13) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T0-50 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | — | — |
| T0-10 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| T1 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| T1v | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| T2 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| T2p | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| T3 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| T4 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| LAD | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| T5 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| T6 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| T7 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| T7s | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| RS | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |

### validation (109 cycles)

| Politique | Cycles actifs | P&L net ($) | Par cycle actif | Par $ de capital max | Cycles gagnants | Perte max | Pertes > 6 $ | Drawdown | ES 5 % | Capital max | Achats / ventes | Frais ($) | Coût d'écart ($) | Parts achetées | P&L couvertures ($) | Plancher le plus bas (moy.) | Jackpots conservés | Sans les 5 meilleurs | Écart avec T0-50 ($) | IC 90 % | IC corrigé (13) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T0-50 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | — | — |
| T0-10 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| T1 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| T1v | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| T2 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| T2p | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| T3 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| T4 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| LAD | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| T5 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| T6 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| T7 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| T7s | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| RS | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |

### TEST (144 cycles)

| Politique | Cycles actifs | P&L net ($) | Par cycle actif | Par $ de capital max | Cycles gagnants | Perte max | Pertes > 6 $ | Drawdown | ES 5 % | Capital max | Achats / ventes | Frais ($) | Coût d'écart ($) | Parts achetées | P&L couvertures ($) | Plancher le plus bas (moy.) | Jackpots conservés | Sans les 5 meilleurs | Écart avec T0-50 ($) | IC 90 % | IC corrigé (13) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T0-50 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | — | — |
| T0-10 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| T1 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| T1v | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| T2 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| T2p | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| T3 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| T4 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| LAD | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| T5 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| T6 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| T7 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| T7s | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| RS | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |

## 4. Les trois simulations prioritaires

### Simulation A — entrées progressives — validation (109 cycles)

| Politique | Cycles actifs | P&L net ($) | Par cycle actif | Par $ de capital max | Cycles gagnants | Perte max | Pertes > 6 $ | Drawdown | ES 5 % | Capital max | Achats / ventes | Frais ($) | Coût d'écart ($) | Parts achetées | P&L couvertures ($) | Plancher le plus bas (moy.) | Jackpots conservés | Sans les 5 meilleurs | Écart avec T0-50 ($) | IC 90 % | IC corrigé (13) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T0-50 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | — | — |
| T0-10 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| T1 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| T1v | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| T2 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| T2p | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |

### Simulation B — changement de camp — validation (109 cycles)

| Politique | Cycles actifs | P&L net ($) | Par cycle actif | Par $ de capital max | Cycles gagnants | Perte max | Pertes > 6 $ | Drawdown | ES 5 % | Capital max | Achats / ventes | Frais ($) | Coût d'écart ($) | Parts achetées | P&L couvertures ($) | Plancher le plus bas (moy.) | Jackpots conservés | Sans les 5 meilleurs | Écart avec T0-50 ($) | IC 90 % | IC corrigé (13) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T0-50 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | — | — |
| T1 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| T2 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| T4 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| LAD | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| T5 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| T7 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |

### Simulation C — protection du capital (même plafond de 50 $) — validation (109 cycles)

| Politique | Cycles actifs | P&L net ($) | Par cycle actif | Par $ de capital max | Cycles gagnants | Perte max | Pertes > 6 $ | Drawdown | ES 5 % | Capital max | Achats / ventes | Frais ($) | Coût d'écart ($) | Parts achetées | P&L couvertures ($) | Plancher le plus bas (moy.) | Jackpots conservés | Sans les 5 meilleurs | Écart avec T0-50 ($) | IC 90 % | IC corrigé (13) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T0-50 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | — | — |
| T7 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| T7s | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| T5 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| T6 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |

**H1033 — coût économique de la protection stricte (validation)** : T7 − T7s = +0 $ [+0 ; +0] ; pertes > 6 $ : T7 0, T7s 0 ; T5 − T6 = +0 $ (pertes > 6 $ : T5 0, T6 0).

### Simulation A — entrées progressives — TEST (144 cycles)

| Politique | Cycles actifs | P&L net ($) | Par cycle actif | Par $ de capital max | Cycles gagnants | Perte max | Pertes > 6 $ | Drawdown | ES 5 % | Capital max | Achats / ventes | Frais ($) | Coût d'écart ($) | Parts achetées | P&L couvertures ($) | Plancher le plus bas (moy.) | Jackpots conservés | Sans les 5 meilleurs | Écart avec T0-50 ($) | IC 90 % | IC corrigé (13) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T0-50 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | — | — |
| T0-10 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| T1 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| T1v | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| T2 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| T2p | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |

### Simulation B — changement de camp — TEST (144 cycles)

| Politique | Cycles actifs | P&L net ($) | Par cycle actif | Par $ de capital max | Cycles gagnants | Perte max | Pertes > 6 $ | Drawdown | ES 5 % | Capital max | Achats / ventes | Frais ($) | Coût d'écart ($) | Parts achetées | P&L couvertures ($) | Plancher le plus bas (moy.) | Jackpots conservés | Sans les 5 meilleurs | Écart avec T0-50 ($) | IC 90 % | IC corrigé (13) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T0-50 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | — | — |
| T1 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| T2 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| T4 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| LAD | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| T5 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| T7 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |

### Simulation C — protection du capital (même plafond de 50 $) — TEST (144 cycles)

| Politique | Cycles actifs | P&L net ($) | Par cycle actif | Par $ de capital max | Cycles gagnants | Perte max | Pertes > 6 $ | Drawdown | ES 5 % | Capital max | Achats / ventes | Frais ($) | Coût d'écart ($) | Parts achetées | P&L couvertures ($) | Plancher le plus bas (moy.) | Jackpots conservés | Sans les 5 meilleurs | Écart avec T0-50 ($) | IC 90 % | IC corrigé (13) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T0-50 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | — | — |
| T7 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| T7s | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| T5 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| T6 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |

**H1033 — coût économique de la protection stricte (TEST)** : T7 − T7s = +0 $ [+0 ; +0] ; pertes > 6 $ : T7 0, T7s 0 ; T5 − T6 = +0 $ (pertes > 6 $ : T5 0, T6 0).

## 5. Sensibilité à la latence et aux frais (TEST)

| Politique | 164 ms | 200 ms | 250 ms | 500 ms | frais×0,5 | frais×1,5 |
|---|---|---|---|---|---|---|
| T0-50 | +0 | +0 | +0 | +0 | +0 | +0 |
| T0-10 | +0 | +0 | +0 | +0 | +0 | +0 |
| T1 | +0 | +0 | +0 | +0 | +0 | +0 |
| T1v | +0 | +0 | +0 | +0 | +0 | +0 |
| T2 | +0 | +0 | +0 | +0 | +0 | +0 |
| T2p | +0 | +0 | +0 | +0 | +0 | +0 |
| T3 | +0 | +0 | +0 | +0 | +0 | +0 |
| T4 | +0 | +0 | +0 | +0 | +0 | +0 |
| LAD | +0 | +0 | +0 | +0 | +0 | +0 |
| T5 | +0 | +0 | +0 | +0 | +0 | +0 |
| T6 | +0 | +0 | +0 | +0 | +0 | +0 |
| T7 | +0 | +0 | +0 | +0 | +0 | +0 |
| T7s | +0 | +0 | +0 | +0 | +0 | +0 |

## 6. H1018 — Scénarios défavorables (164 ms)

| Politique | Normal | acheteurs disparus | couverture + 2 c | fills ÷ 2 | vente de protection impossible | Pertes > 6 $ (normal → pire scénario) | Perte max (normal → pire) |
|---|---|---|---|---|---|---|---|
| T0-50 | +0 | +0 | +0 | +0 | +0 | 0 → 0 | +0 → +0 |
| T1 | +0 | +0 | +0 | +0 | +0 | 0 → 0 | +0 → +0 |
| T3 | +0 | +0 | +0 | +0 | +0 | 0 → 0 | +0 → +0 |
| T4 | +0 | +0 | +0 | +0 | +0 | 0 → 0 | +0 → +0 |
| LAD | +0 | +0 | +0 | +0 | +0 | 0 → 0 | +0 → +0 |
| T5 | +0 | +0 | +0 | +0 | +0 | 0 → 0 | +0 → +0 |
| T7 | +0 | +0 | +0 | +0 | +0 | 0 → 0 | +0 → +0 |
| T7s | +0 | +0 | +0 | +0 | +0 | 0 → 0 | +0 → +0 |

## 7. Renforts, couvertures, inversions

**H1013 — P&L de chaque tranche jusqu'au règlement (validation)**

| Politique | Tranche | Nombre | Coût ($) | P&L ($) | P&L / $ |
|---|---|---|---|---|---|

**P&L des transactions de protection par type (validation)** (valeur au règlement − coût)

| Politique | Couverture | Protection (vente) | Inversion | Verrou | Sortie |
|---|---|---|---|---|---|
| T3 | +0 | +0 | +0 | +0 | +0 |
| T4 | +0 | +0 | +0 | +0 | +0 |
| LAD | +0 | +0 | +0 | +0 | +0 |
| T5 | +0 | +0 | +0 | +0 | +0 |
| T6 | +0 | +0 | +0 | +0 | +0 |
| T7 | +0 | +0 | +0 | +0 | +0 |
| T7s | +0 | +0 | +0 | +0 | +0 |

**H1025 — coût par dollar de perte maximale évitée (validation, contre T1)**

| Politique | P&L − T1 ($) | Plancher moyen le plus bas − T1 ($) | Coût par $ évité |
|---|---|---|---|
| T3 | +0 | +0.00 | +nan |
| T4 | +0 | +0.00 | +nan |
| LAD | +0 | +0.00 | +nan |
| T7 | +0 | +0.00 | +nan |

**H1020 — changements de camp (validation)** : aucun.

**H1013 — P&L de chaque tranche jusqu'au règlement (TEST)**

| Politique | Tranche | Nombre | Coût ($) | P&L ($) | P&L / $ |
|---|---|---|---|---|---|

**P&L des transactions de protection par type (TEST)** (valeur au règlement − coût)

| Politique | Couverture | Protection (vente) | Inversion | Verrou | Sortie |
|---|---|---|---|---|---|
| T3 | +0 | +0 | +0 | +0 | +0 |
| T4 | +0 | +0 | +0 | +0 | +0 |
| LAD | +0 | +0 | +0 | +0 | +0 |
| T5 | +0 | +0 | +0 | +0 | +0 |
| T6 | +0 | +0 | +0 | +0 | +0 |
| T7 | +0 | +0 | +0 | +0 | +0 |
| T7s | +0 | +0 | +0 | +0 | +0 |

**H1025 — coût par dollar de perte maximale évitée (TEST, contre T1)**

| Politique | P&L − T1 ($) | Plancher moyen le plus bas − T1 ($) | Coût par $ évité |
|---|---|---|---|
| T3 | +0 | +0.00 | +nan |
| T4 | +0 | +0.00 | +nan |
| LAD | +0 | +0.00 | +nan |
| T7 | +0 | +0.00 | +nan |

**H1020 — changements de camp (TEST)** : aucun.

## 8. H1017 — Régimes au signal d'entrée

| validation : régime | Cycles | T0-50 | T1 | T3 | T5 | T7 | RS |
|---|---|---|---|---|---|---|---|
| aucun signal | 109 | +0 | +0 | +0 | +0 | +0 | +0 |

| TEST : régime | Cycles | T0-50 | T1 | T3 | T5 | T7 | RS |
|---|---|---|---|---|---|---|---|
| aucun signal | 144 | +0 | +0 | +0 | +0 | +0 | +0 |

## 9. H1036–H1040 — Sauvetage de la première position (entrée 10 $, mêmes cycles)

R0 conserver ; R1 vendre toute la position à −0,15 ; R2 couverture préventive (−0,05 et cerveau A contre ≥ 0,60) ; R3 couverture complète à −0,15 ; R4 couverture tardive (p ≤ 0,25) ; R5 vente de 50 % puis couverture du reste à −0,15 ; R6 inversion complète à −0,15 (vente de tout + 10 $ de l'opposé) ; R7 adaptatif (H1039 : probabilité de redevenir gagnante, apprise sur l'apprentissage ; vend si acheteur net > probabilité + 0,01, couvre si (1 − probabilité) − coût opposé > 0,01, sinon conserve). Couverture = achat de l'opposé pour toutes les parts non appariées. Les noms R0–R7 sont propres à cette étude (aucun lien avec le fantôme R4).

Modèle de récupération H1039 : 2959 états détériorés d'apprentissage (taux de récupération 36.3 %).

### Tournoi de sauvetage R0–R7 — validation (109 cycles)

| Politique | Cycles actifs | P&L net ($) | Par cycle actif | Par $ de capital max | Cycles gagnants | Perte max | Pertes > 6 $ | Drawdown | ES 5 % | Capital max | Achats / ventes | Frais ($) | Coût d'écart ($) | Parts achetées | P&L couvertures ($) | Plancher le plus bas (moy.) | Jackpots conservés | Sans les 5 meilleurs | Écart avec R0 ($) | IC 90 % | IC corrigé (7) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| R0 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | — | — |
| R1 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| R2 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| R3 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| R4 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| R5 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| R6 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| R7 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |

**Niveaux de détérioration (H1036, descriptif, aucun choix) — validation** : R1-10 +0 $ ; R1 +0 $ ; R1-20 +0 $ ; R1-30 +0 $ ; R3-10 +0 $ ; R3 +0 $ ; R3-20 +0 $ ; R3-30 +0 $ (écart avec R0).

**Test décisif (section 9) — validation** : 0 positions devenues défavorables (p ≤ entrée − 0,15) ; ramené à 100.

| Politique | Perdantes sans intervention | Gagnantes sans intervention | Sauvetages (perte réduite) | Coût moyen d'un sauvetage réussi ($ gagnés) | Couvertures inutiles (gagnantes abîmées) | Coût des couvertures inutiles ($) | Perte moyenne R0 → politique | Perte max R0 → politique | P&L net − R0 (défavorables) | P&L net − R0 (tous) |
|---|---|---|---|---|---|---|---|---|---|---|

**H1038 — vendre ou acheter l'opposé, à risque comparable (cible : pire résultat ≥ −6 $, dès p ≤ entrée − 0,15) — validation**

| Réaction | Cycles où elle a agi | Pire résultat final moyen | Pertes > 6 $ | Capital max moyen ($) | Frais ($) | P&L net ($) | Écart avec R0 (IC 90 %) |
|---|---|---|---|---|---|---|---|
| ne rien faire | 0 | +0.00 | 0 | 0.0 | 0.0 | +0 | +0 [+0 ; +0] |
| vendre une partie | 0 | +0.00 | 0 | 0.0 | 0.0 | +0 | +0 [+0 ; +0] |
| acheter l'opposé | 0 | +0.00 | 0 | 0.0 | 0.0 | +0 | +0 [+0 ; +0] |
| vendre une partie puis acheter l'opposé | 0 | +0.00 | 0 | 0.0 | 0.0 | +0 | +0 [+0 ; +0] |

### Tournoi de sauvetage R0–R7 — TEST (144 cycles)

| Politique | Cycles actifs | P&L net ($) | Par cycle actif | Par $ de capital max | Cycles gagnants | Perte max | Pertes > 6 $ | Drawdown | ES 5 % | Capital max | Achats / ventes | Frais ($) | Coût d'écart ($) | Parts achetées | P&L couvertures ($) | Plancher le plus bas (moy.) | Jackpots conservés | Sans les 5 meilleurs | Écart avec R0 ($) | IC 90 % | IC corrigé (7) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| R0 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | — | — |
| R1 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| R2 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| R3 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| R4 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| R5 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| R6 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| R7 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |

**Niveaux de détérioration (H1036, descriptif, aucun choix) — TEST** : R1-10 +0 $ ; R1 +0 $ ; R1-20 +0 $ ; R1-30 +0 $ ; R3-10 +0 $ ; R3 +0 $ ; R3-20 +0 $ ; R3-30 +0 $ (écart avec R0).

**Test décisif (section 9) — TEST** : 0 positions devenues défavorables (p ≤ entrée − 0,15) ; ramené à 100.

| Politique | Perdantes sans intervention | Gagnantes sans intervention | Sauvetages (perte réduite) | Coût moyen d'un sauvetage réussi ($ gagnés) | Couvertures inutiles (gagnantes abîmées) | Coût des couvertures inutiles ($) | Perte moyenne R0 → politique | Perte max R0 → politique | P&L net − R0 (défavorables) | P&L net − R0 (tous) |
|---|---|---|---|---|---|---|---|---|---|---|

**H1038 — vendre ou acheter l'opposé, à risque comparable (cible : pire résultat ≥ −6 $, dès p ≤ entrée − 0,15) — TEST**

| Réaction | Cycles où elle a agi | Pire résultat final moyen | Pertes > 6 $ | Capital max moyen ($) | Frais ($) | P&L net ($) | Écart avec R0 (IC 90 %) |
|---|---|---|---|---|---|---|---|
| ne rien faire | 0 | +0.00 | 0 | 0.0 | 0.0 | +0 | +0 [+0 ; +0] |
| vendre une partie | 0 | +0.00 | 0 | 0.0 | 0.0 | +0 | +0 [+0 ; +0] |
| acheter l'opposé | 0 | +0.00 | 0 | 0.0 | 0.0 | +0 | +0 [+0 ; +0] |
| vendre une partie puis acheter l'opposé | 0 | +0.00 | 0 | 0.0 | 0.0 | +0 | +0 [+0 ; +0] |

**Sauvetage — latence et frais (TEST)**

| Politique | 164 ms | 200 ms | 250 ms | 500 ms | frais×0,5 | frais×1,5 |
|---|---|---|---|---|---|---|
| R0 | +0 | +0 | +0 | +0 | +0 | +0 |
| R1 | +0 | +0 | +0 | +0 | +0 | +0 |
| R2 | +0 | +0 | +0 | +0 | +0 | +0 |
| R3 | +0 | +0 | +0 | +0 | +0 | +0 |
| R4 | +0 | +0 | +0 | +0 | +0 | +0 |
| R5 | +0 | +0 | +0 | +0 | +0 | +0 |
| R6 | +0 | +0 | +0 | +0 | +0 | +0 |
| R7 | +0 | +0 | +0 | +0 | +0 | +0 |
| Rv | +0 | +0 | +0 | +0 | +0 | +0 |
| Ra | +0 | +0 | +0 | +0 | +0 | +0 |
| Rm | +0 | +0 | +0 | +0 | +0 | +0 |

**Critère (sauvetage, contre R0)** : une politique n'est retenue que si l'IC corrigé (7) de l'écart avec R0 est > 0 sur le test, la validation va dans le même sens, l'écart reste > 0 à 500 ms et sans les 5 meilleurs cycles.

| Politique | IC corrigé > 0 | Validation même sens | > 0 à 500 ms | > 0 sans les 5 meilleurs | Verdict |
|---|---|---|---|---|---|
| R1 | non | non | non | non | non démontrée |
| R2 | non | non | non | non | non démontrée |
| R3 | non | non | non | non | non démontrée |
| R4 | non | non | non | non | non démontrée |
| R5 | non | non | non | non | non démontrée |
| R6 | non | non | non | non | non démontrée |
| R7 | non | non | non | non | non démontrée |
## 11. H1041–H1046 — Protection des positions gagnantes (entrée 10 $, mêmes cycles)

P0 conserver ; P-TP100 / P-TP200 tout vendre si acheteur net ≥ 2× / 3× le prix payé ; P-VP vendre 50 % si acheteur net ≥ prix payé + 0,20 ; P-TR10…40 trailing : tout vendre quand le profit liquidable (acheteurs affichés, frais, profondeur) retombe de 10/20/30/40 % sous son maximum (maximum ≥ 2 $) ; P-TF trailing fondamental : p de règlement recalibrée ≤ son maximum − 0,15 ET cerveau A contre ≥ 0,55 (momentum, OFI, liquidations, Chainlink ; ETH/SOL non disponibles avant le 12.10) ; P-L0 (free-roll : mise récupérée), P-L5, P-L10, P-L20, P-Lm6 (5 CHF) : vente de la quantité minimale qui verrouille ce résultat dans le cas perdant, dès que la profondeur le permet ; à retracement de 30 % : P-HA vente partielle, P-HB achat de l'opposé, P-HC moitié-moitié (verrou 0 $) ; P-PF cliquet du portefeuille : à 30 % de retracement, plancher contractuel porté à 50 % du gain liquidable maximal par le moyen le moins cher. Un gain n'est « verrouillé » que s'il est garanti par l'inventaire exécuté.

### Protection des gains — validation (109 cycles)

| Politique | Cycles actifs | P&L net ($) | Par cycle actif | Par $ de capital max | Cycles gagnants | Perte max | Pertes > 6 $ | Drawdown | ES 5 % | Capital max | Achats / ventes | Frais ($) | Coût d'écart ($) | Parts achetées | P&L couvertures ($) | Plancher le plus bas (moy.) | Jackpots conservés | Sans les 5 meilleurs | Écart avec P0 ($) | IC 90 % | IC corrigé (17) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P0 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | — | — |
| P-TP100 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| P-TP200 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| P-VP | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| P-TR10 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| P-TR20 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| P-TR30 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| P-TR40 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| P-TF | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| P-L0 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| P-L5 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| P-L10 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| P-L20 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| P-Lm6 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| P-HA | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| P-HB | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| P-HC | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| P-PF | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |

### Protection des gains — TEST (144 cycles)

| Politique | Cycles actifs | P&L net ($) | Par cycle actif | Par $ de capital max | Cycles gagnants | Perte max | Pertes > 6 $ | Drawdown | ES 5 % | Capital max | Achats / ventes | Frais ($) | Coût d'écart ($) | Parts achetées | P&L couvertures ($) | Plancher le plus bas (moy.) | Jackpots conservés | Sans les 5 meilleurs | Écart avec P0 ($) | IC 90 % | IC corrigé (17) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P0 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | — | — |
| P-TP100 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| P-TP200 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| P-VP | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| P-TR10 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| P-TR20 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| P-TR30 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| P-TR40 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| P-TF | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| P-L0 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| P-L5 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| P-L10 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| P-L20 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| P-Lm6 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| P-HA | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| P-HB | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| P-HC | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| P-PF | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |

**Protection des gains — latence et frais (TEST)**

| Politique | 164 ms | 200 ms | 250 ms | 500 ms | frais×0,5 | frais×1,5 |
|---|---|---|---|---|---|---|
| P0 | +0 | +0 | +0 | +0 | +0 | +0 |
| P-TP100 | +0 | +0 | +0 | +0 | +0 | +0 |
| P-TP200 | +0 | +0 | +0 | +0 | +0 | +0 |
| P-VP | +0 | +0 | +0 | +0 | +0 | +0 |
| P-TR10 | +0 | +0 | +0 | +0 | +0 | +0 |
| P-TR20 | +0 | +0 | +0 | +0 | +0 | +0 |
| P-TR30 | +0 | +0 | +0 | +0 | +0 | +0 |
| P-TR40 | +0 | +0 | +0 | +0 | +0 | +0 |
| P-TF | +0 | +0 | +0 | +0 | +0 | +0 |
| P-L0 | +0 | +0 | +0 | +0 | +0 | +0 |
| P-L5 | +0 | +0 | +0 | +0 | +0 | +0 |
| P-L10 | +0 | +0 | +0 | +0 | +0 | +0 |
| P-L20 | +0 | +0 | +0 | +0 | +0 | +0 |
| P-Lm6 | +0 | +0 | +0 | +0 | +0 | +0 |
| P-HA | +0 | +0 | +0 | +0 | +0 | +0 |
| P-HB | +0 | +0 | +0 | +0 | +0 | +0 |
| P-HC | +0 | +0 | +0 | +0 | +0 | +0 |
| P-PF | +0 | +0 | +0 | +0 | +0 | +0 |

| Politique | IC corrigé (17) > 0 contre P0 | Validation même sens | > 0 à 500 ms | > 0 sans les 5 meilleurs | Verdict |
|---|---|---|---|---|---|
| P-TP100 | non | non | non | non | non démontrée |
| P-TP200 | non | non | non | non | non démontrée |
| P-VP | non | non | non | non | non démontrée |
| P-TR10 | non | non | non | non | non démontrée |
| P-TR20 | non | non | non | non | non démontrée |
| P-TR30 | non | non | non | non | non démontrée |
| P-TR40 | non | non | non | non | non démontrée |
| P-TF | non | non | non | non | non démontrée |
| P-L0 | non | non | non | non | non démontrée |
| P-L5 | non | non | non | non | non démontrée |
| P-L10 | non | non | non | non | non démontrée |
| P-L20 | non | non | non | non | non démontrée |
| P-Lm6 | non | non | non | non | non démontrée |
| P-HA | non | non | non | non | non démontrée |
| P-HB | non | non | non | non | non démontrée |
| P-HC | non | non | non | non | non démontrée |
| P-PF | non | non | non | non | non démontrée |
## 10. Critère de réussite (section 43) sur TEST

| Politique | IC corrigé > 0 | Pertes > 6 $ pas plus fréquentes | Jackpots ≥ 50 % | Écart > 0 à 500 ms | Écart > 0 sans les 5 meilleurs | Validation même sens | Verdict |
|---|---|---|---|---|---|---|---|
| T0-10 | non | oui | oui | non | non | non | non démontrée |
| T1 | non | oui | oui | non | non | non | non démontrée |
| T1v | non | oui | oui | non | non | non | non démontrée |
| T2 | non | oui | oui | non | non | non | non démontrée |
| T2p | non | oui | oui | non | non | non | non démontrée |
| T3 | non | oui | oui | non | non | non | non démontrée |
| T4 | non | oui | oui | non | non | non | non démontrée |
| LAD | non | oui | oui | non | non | non | non démontrée |
| T5 | non | oui | oui | non | non | non | non démontrée |
| T6 | non | oui | oui | non | non | non | non démontrée |
| T7 | non | oui | oui | non | non | non | non démontrée |
| T7s | non | oui | oui | non | non | non | non démontrée |
| RS | non | oui | oui | — | non | non | non démontrée |

# FAMILLE D'ENTRÉE : favori du marché (vendeur 0,60–0,85, 60 à 180 s écoulées)

| Échantillon | Décisions | Brier marché | Brier M0 brut | Brier cerveau B | Cerveau B − marché (IC 90 %) | LL marché | LL cerveau B | Ajout de a30 (H1026) : ΔBrier (IC 90 %) |
|---|---|---|---|---|---|---|---|---|
| apprentissage | 4559 | 0.1683 | 0.1844 | 0.1678 | -0.0005 [-0.0018 ; +0.0009] | 0.4981 | 0.4974 | -0.00044 [-0.00120 ; +0.00032] |
| validation | 2301 | 0.1363 | 0.1308 | 0.1364 | +0.0001 [-0.0017 ; +0.0018] | 0.4226 | 0.4237 | -0.00062 [-0.00166 ; +0.00045] |
| TEST | 2968 | 0.1772 | 0.1880 | 0.1770 | -0.0002 [-0.0020 ; +0.0016] | 0.5231 | 0.5227 | -0.00071 [-0.00232 ; +0.00081] |

Seuil d'entrée e choisi sur l'apprentissage (T0-50) : **0.05** (e=0.05 → +0 $, e=0.10 → +0 $, e=0.15 → +0 $).

Attribution RS (apprentissage) : aucun signal → T0-50, choc de liquidations → T0-50, range → T7, retournement probable → T7, tendance → T5.


## 3. Tournoi T0–T7 (H1034), latence 164 ms

### apprentissage (sert au choix de e et de RS) (216 cycles)

| Politique | Cycles actifs | P&L net ($) | Par cycle actif | Par $ de capital max | Cycles gagnants | Perte max | Pertes > 6 $ | Drawdown | ES 5 % | Capital max | Achats / ventes | Frais ($) | Coût d'écart ($) | Parts achetées | P&L couvertures ($) | Plancher le plus bas (moy.) | Jackpots conservés | Sans les 5 meilleurs | Écart avec T0-50 ($) | IC 90 % | IC corrigé (13) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T0-50 | 165 | -1144 | -6.93 | -15.3 % | 101 | -50 | 63 | 1433 | -50.0 | 50 | 165 / 0 | 155 | 46 | 10637 | +0 | -34.6 | nan % (0) | -1300 | +0 | — | — |
| T0-10 | 165 | -227 | -1.37 | -13.9 % | 101 | -10 | 63 | 281 | -10.0 | 10 | 165 / 0 | 34 | 10 | 2312 | +0 | -7.5 | nan % (0) | -258 | +918 | [+368 ; +1466] | [+4 ; +1793] |
| T1 | 165 | -227 | -1.37 | -13.9 % | 101 | -10 | 63 | 281 | -10.0 | 10 | 165 / 0 | 34 | 10 | 2312 | +0 | -7.5 | nan % (0) | -258 | +918 | [+364 ; +1469] | [+39 ; +1833] |
| T1v | 165 | -227 | -1.37 | -13.9 % | 101 | -10 | 63 | 281 | -10.0 | 10 | 165 / 0 | 34 | 10 | 2312 | +0 | -7.5 | nan % (0) | -258 | +918 | [+395 ; +1475] | [+16 ; +1897] |
| T2 | 165 | -227 | -1.37 | -13.9 % | 101 | -10 | 63 | 281 | -10.0 | 10 | 165 / 0 | 34 | 10 | 2312 | +0 | -7.5 | nan % (0) | -258 | +918 | [+391 ; +1470] | [+37 ; +1808] |
| T2p | 165 | -227 | -1.37 | -13.9 % | 101 | -10 | 63 | 281 | -10.0 | 10 | 165 / 0 | 34 | 10 | 2312 | +0 | -7.5 | nan % (0) | -258 | +918 | [+361 ; +1483] | [+48 ; +1826] |
| T3 | 165 | -174 | -1.05 | -8.7 % | 99 | -10 | 58 | 225 | -9.9 | 18 | 244 / 0 | 40 | 11 | 2874 | +53 | -7.5 | nan % (0) | -205 | +971 | [+405 ; +1537] | [+58 ; +1919] |
| T4 | 165 | -185 | -1.12 | -11.4 % | 98 | -10 | 59 | 237 | -10.0 | 10 | 165 / 52 | 40 | 10 | 2312 | +41 | -7.5 | nan % (0) | -216 | +959 | [+374 ; +1551] | [+72 ; +1830] |
| LAD | 165 | -190 | -1.15 | -11.2 % | 86 | -10 | 38 | 236 | -10.0 | 20 | 202 / 53 | 45 | 10 | 2607 | +37 | -7.5 | nan % (0) | -221 | +954 | [+358 ; +1574] | [+5 ; +1931] |
| T5 | 165 | -176 | -1.07 | -8.3 % | 139 | -10 | 26 | 188 | -10.0 | 16 | 315 / 0 | 58 | 14 | 4290 | +50 | -7.5 | nan % (0) | -190 | +968 | [+296 ; +1603] | [-31 ; +2056] |
| T6 | 165 | -108 | -0.65 | -8.4 % | 139 | -6 | 0 | 115 | -6.0 | 10 | 310 / 0 | 35 | 9 | 2586 | +30 | -4.6 | nan % (0) | -116 | +1037 | [+355 ; +1738] | [-41 ; +2096] |
| T7 | 165 | -134 | -0.81 | -6.7 % | 86 | -8 | 10 | 139 | -7.2 | 24 | 274 / 103 | 65 | 16 | 3698 | +93 | -7.5 | nan % (0) | -145 | +1010 | [+337 ; +1680] | [-52 ; +2094] |
| T7s | 165 | -89 | -0.54 | -7.5 % | 93 | -6 | 0 | 92 | -5.9 | 10 | 260 / 82 | 38 | 9 | 2198 | +48 | -4.6 | nan % (0) | -97 | +1055 | [+410 ; +1732] | [+4 ; +2171] |
| RS | 165 | -111 | -0.67 | -5.3 % | 98 | -10 | 12 | 120 | -7.7 | 50 | 282 / 84 | 65 | 16 | 3892 | +103 | -7.9 | nan % (0) | -135 | +1033 | [+354 ; +1707] | [+25 ; +2218] |

### validation (109 cycles)

| Politique | Cycles actifs | P&L net ($) | Par cycle actif | Par $ de capital max | Cycles gagnants | Perte max | Pertes > 6 $ | Drawdown | ES 5 % | Capital max | Achats / ventes | Frais ($) | Coût d'écart ($) | Parts achetées | P&L couvertures ($) | Plancher le plus bas (moy.) | Jackpots conservés | Sans les 5 meilleurs | Écart avec T0-50 ($) | IC 90 % | IC corrigé (13) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T0-50 | 82 | +182 | +2.22 | +5.2 % | 60 | -50 | 20 | 258 | -50.0 | 50 | 82 / 0 | 71 | 19 | 4926 | +0 | -32.1 | nan % (0) | +26 | +0 | — | — |
| T0-10 | 82 | +25 | +0.31 | +3.2 % | 60 | -10 | 20 | 55 | -10.0 | 10 | 82 / 0 | 16 | 4 | 1115 | +0 | -7.2 | nan % (0) | -6 | -156 | [-471 ; +172] | [-668 ; +416] |
| T1 | 82 | +25 | +0.31 | +3.2 % | 60 | -10 | 20 | 55 | -10.0 | 10 | 82 / 0 | 16 | 4 | 1115 | +0 | -7.2 | nan % (0) | -6 | -156 | [-475 ; +169] | [-659 ; +418] |
| T1v | 82 | +25 | +0.31 | +3.2 % | 60 | -10 | 20 | 55 | -10.0 | 10 | 82 / 0 | 16 | 4 | 1115 | +0 | -7.2 | nan % (0) | -6 | -156 | [-480 ; +171] | [-657 ; +377] |
| T2 | 82 | +25 | +0.31 | +3.2 % | 60 | -10 | 20 | 55 | -10.0 | 10 | 82 / 0 | 16 | 4 | 1115 | +0 | -7.2 | nan % (0) | -6 | -156 | [-478 ; +176] | [-694 ; +376] |
| T2p | 82 | +25 | +0.31 | +3.2 % | 60 | -10 | 20 | 55 | -10.0 | 10 | 82 / 0 | 16 | 4 | 1115 | +0 | -7.2 | nan % (0) | -6 | -156 | [-476 ; +165] | [-671 ; +398] |
| T3 | 82 | +17 | +0.20 | +1.8 % | 57 | -10 | 17 | 40 | -9.9 | 18 | 113 / 0 | 18 | 5 | 1331 | -9 | -7.2 | nan % (0) | -14 | -165 | [-504 ; +190] | [-672 ; +392] |
| T4 | 82 | +12 | +0.14 | +1.5 % | 58 | -10 | 17 | 45 | -10.0 | 10 | 82 / 22 | 19 | 5 | 1115 | -14 | -7.2 | nan % (0) | -19 | -170 | [-503 ; +174] | [-687 ; +383] |
| LAD | 82 | -7 | -0.08 | -0.9 % | 53 | -10 | 15 | 57 | -10.0 | 19 | 94 / 23 | 20 | 5 | 1207 | -32 | -7.2 | nan % (0) | -37 | -189 | [-532 ; +162] | [-730 ; +372] |
| T5 | 82 | -42 | -0.51 | -4.0 % | 74 | -10 | 8 | 42 | -10.0 | 16 | 165 / 0 | 29 | 7 | 2132 | -67 | -7.2 | nan % (0) | -50 | -223 | [-607 ; +163] | [-822 ; +421] |
| T6 | 82 | -25 | -0.30 | -3.9 % | 74 | -6 | 0 | 25 | -6.0 | 10 | 162 / 0 | 18 | 4 | 1301 | -39 | -4.4 | nan % (0) | -30 | -207 | [-586 ; +196] | [-835 ; +464] |
| T7 | 82 | -28 | -0.34 | -2.9 % | 51 | -7 | 1 | 32 | -5.0 | 16 | 141 / 43 | 31 | 8 | 1846 | -54 | -7.2 | nan % (0) | -36 | -210 | [-612 ; +203] | [-833 ; +434] |
| T7s | 82 | -22 | -0.27 | -3.7 % | 55 | -6 | 0 | 25 | -4.4 | 10 | 139 / 35 | 19 | 5 | 1138 | -37 | -4.4 | nan % (0) | -27 | -204 | [-595 ; +212] | [-857 ; +478] |
| RS | 82 | -11 | -0.13 | -1.0 % | 56 | -7 | 1 | 30 | -5.0 | 50 | 144 / 36 | 31 | 8 | 1936 | -44 | -7.6 | nan % (0) | -28 | -192 | [-579 ; +204] | [-796 ; +524] |

### TEST (144 cycles)

| Politique | Cycles actifs | P&L net ($) | Par cycle actif | Par $ de capital max | Cycles gagnants | Perte max | Pertes > 6 $ | Drawdown | ES 5 % | Capital max | Achats / ventes | Frais ($) | Coût d'écart ($) | Parts achetées | P&L couvertures ($) | Plancher le plus bas (moy.) | Jackpots conservés | Sans les 5 meilleurs | Écart avec T0-50 ($) | IC 90 % | IC corrigé (13) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T0-50 | 111 | -368 | -3.32 | -7.2 % | 72 | -50 | 37 | 560 | -50.0 | 50 | 111 / 0 | 106 | 32 | 7329 | +0 | -35.7 | nan % (0) | -524 | +0 | — | — |
| T0-10 | 111 | -98 | -0.88 | -9.0 % | 72 | -10 | 37 | 136 | -10.0 | 10 | 111 / 0 | 23 | 7 | 1551 | +0 | -7.6 | nan % (0) | -129 | +270 | [-165 ; +698] | [-402 ; +1052] |
| T1 | 111 | -98 | -0.88 | -9.0 % | 72 | -10 | 37 | 136 | -10.0 | 10 | 111 / 0 | 23 | 7 | 1551 | +0 | -7.6 | nan % (0) | -129 | +270 | [-156 ; +716] | [-432 ; +981] |
| T1v | 111 | -98 | -0.88 | -9.0 % | 72 | -10 | 37 | 136 | -10.0 | 10 | 111 / 0 | 23 | 7 | 1551 | +0 | -7.6 | nan % (0) | -129 | +270 | [-159 ; +702] | [-387 ; +1007] |
| T2 | 111 | -98 | -0.88 | -9.0 % | 72 | -10 | 37 | 136 | -10.0 | 10 | 111 / 0 | 23 | 7 | 1551 | +0 | -7.6 | nan % (0) | -129 | +270 | [-162 ; +697] | [-420 ; +1022] |
| T2p | 111 | -98 | -0.88 | -9.0 % | 72 | -10 | 37 | 136 | -10.0 | 10 | 111 / 0 | 23 | 7 | 1551 | +0 | -7.6 | nan % (0) | -129 | +270 | [-162 ; +692] | [-377 ; +995] |
| T3 | 111 | -93 | -0.84 | -6.9 % | 69 | -10 | 34 | 130 | -9.9 | 18 | 167 / 0 | 28 | 9 | 1956 | +5 | -7.6 | nan % (0) | -124 | +275 | [-167 ; +731] | [-478 ; +1065] |
| T4 | 111 | -98 | -0.89 | -9.0 % | 67 | -10 | 33 | 137 | -10.0 | 10 | 111 / 41 | 27 | 8 | 1551 | -0 | -7.6 | nan % (0) | -129 | +270 | [-197 ; +721] | [-478 ; +1004] |
| LAD | 111 | -85 | -0.76 | -7.4 % | 59 | -10 | 17 | 118 | -10.0 | 21 | 141 / 45 | 32 | 9 | 1787 | +13 | -7.6 | nan % (0) | -116 | +283 | [-191 ; +767] | [-460 ; +1081] |
| T5 | 111 | -77 | -0.70 | -5.4 % | 97 | -10 | 13 | 88 | -10.0 | 16 | 221 / 0 | 39 | 6 | 2947 | +21 | -7.6 | nan % (0) | -86 | +291 | [-224 ; +815] | [-498 ; +1162] |
| T6 | 111 | -47 | -0.42 | -5.5 % | 97 | -6 | 0 | 53 | -6.0 | 10 | 218 / 0 | 24 | 3 | 1775 | +15 | -4.6 | nan % (0) | -52 | +321 | [-215 ; +856] | [-518 ; +1207] |
| T7 | 111 | -70 | -0.63 | -5.2 % | 61 | -8 | 5 | 76 | -6.8 | 24 | 194 / 68 | 44 | 9 | 2550 | +28 | -7.6 | nan % (0) | -78 | +298 | [-244 ; +849] | [-590 ; +1157] |
| T7s | 111 | -35 | -0.31 | -4.3 % | 71 | -6 | 0 | 42 | -4.8 | 10 | 185 / 59 | 26 | 4 | 1540 | +27 | -4.6 | nan % (0) | -39 | +334 | [-192 ; +887] | [-527 ; +1272] |
| RS | 111 | -134 | -1.21 | -8.8 % | 66 | -50 | 8 | 171 | -18.4 | 50 | 198 / 57 | 45 | 10 | 2802 | +12 | -8.7 | nan % (0) | -178 | +234 | [-285 ; +771] | [-591 ; +1123] |

## 4. Les trois simulations prioritaires

### Simulation A — entrées progressives — validation (109 cycles)

| Politique | Cycles actifs | P&L net ($) | Par cycle actif | Par $ de capital max | Cycles gagnants | Perte max | Pertes > 6 $ | Drawdown | ES 5 % | Capital max | Achats / ventes | Frais ($) | Coût d'écart ($) | Parts achetées | P&L couvertures ($) | Plancher le plus bas (moy.) | Jackpots conservés | Sans les 5 meilleurs | Écart avec T0-50 ($) | IC 90 % | IC corrigé (13) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T0-50 | 82 | +182 | +2.22 | +5.2 % | 60 | -50 | 20 | 258 | -50.0 | 50 | 82 / 0 | 71 | 19 | 4926 | +0 | -32.1 | nan % (0) | +26 | +0 | — | — |
| T0-10 | 82 | +25 | +0.31 | +3.2 % | 60 | -10 | 20 | 55 | -10.0 | 10 | 82 / 0 | 16 | 4 | 1115 | +0 | -7.2 | nan % (0) | -6 | -156 | [-473 ; +195] | [-651 ; +394] |
| T1 | 82 | +25 | +0.31 | +3.2 % | 60 | -10 | 20 | 55 | -10.0 | 10 | 82 / 0 | 16 | 4 | 1115 | +0 | -7.2 | nan % (0) | -6 | -156 | [-475 ; +185] | [-656 ; +375] |
| T1v | 82 | +25 | +0.31 | +3.2 % | 60 | -10 | 20 | 55 | -10.0 | 10 | 82 / 0 | 16 | 4 | 1115 | +0 | -7.2 | nan % (0) | -6 | -156 | [-474 ; +168] | [-685 ; +369] |
| T2 | 82 | +25 | +0.31 | +3.2 % | 60 | -10 | 20 | 55 | -10.0 | 10 | 82 / 0 | 16 | 4 | 1115 | +0 | -7.2 | nan % (0) | -6 | -156 | [-470 ; +167] | [-662 ; +394] |
| T2p | 82 | +25 | +0.31 | +3.2 % | 60 | -10 | 20 | 55 | -10.0 | 10 | 82 / 0 | 16 | 4 | 1115 | +0 | -7.2 | nan % (0) | -6 | -156 | [-472 ; +166] | [-642 ; +398] |

### Simulation B — changement de camp — validation (109 cycles)

| Politique | Cycles actifs | P&L net ($) | Par cycle actif | Par $ de capital max | Cycles gagnants | Perte max | Pertes > 6 $ | Drawdown | ES 5 % | Capital max | Achats / ventes | Frais ($) | Coût d'écart ($) | Parts achetées | P&L couvertures ($) | Plancher le plus bas (moy.) | Jackpots conservés | Sans les 5 meilleurs | Écart avec T0-50 ($) | IC 90 % | IC corrigé (13) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T0-50 | 82 | +182 | +2.22 | +5.2 % | 60 | -50 | 20 | 258 | -50.0 | 50 | 82 / 0 | 71 | 19 | 4926 | +0 | -32.1 | nan % (0) | +26 | +0 | — | — |
| T1 | 82 | +25 | +0.31 | +3.2 % | 60 | -10 | 20 | 55 | -10.0 | 10 | 82 / 0 | 16 | 4 | 1115 | +0 | -7.2 | nan % (0) | -6 | -156 | [-475 ; +171] | [-697 ; +398] |
| T2 | 82 | +25 | +0.31 | +3.2 % | 60 | -10 | 20 | 55 | -10.0 | 10 | 82 / 0 | 16 | 4 | 1115 | +0 | -7.2 | nan % (0) | -6 | -156 | [-484 ; +162] | [-672 ; +370] |
| T4 | 82 | +12 | +0.14 | +1.5 % | 58 | -10 | 17 | 45 | -10.0 | 10 | 82 / 22 | 19 | 5 | 1115 | -14 | -7.2 | nan % (0) | -19 | -170 | [-503 ; +179] | [-668 ; +394] |
| LAD | 82 | -7 | -0.08 | -0.9 % | 53 | -10 | 15 | 57 | -10.0 | 19 | 94 / 23 | 20 | 5 | 1207 | -32 | -7.2 | nan % (0) | -37 | -189 | [-537 ; +175] | [-724 ; +381] |
| T5 | 82 | -42 | -0.51 | -4.0 % | 74 | -10 | 8 | 42 | -10.0 | 16 | 165 / 0 | 29 | 7 | 2132 | -67 | -7.2 | nan % (0) | -50 | -223 | [-597 ; +180] | [-840 ; +445] |
| T7 | 82 | -28 | -0.34 | -2.9 % | 51 | -7 | 1 | 32 | -5.0 | 16 | 141 / 43 | 31 | 8 | 1846 | -54 | -7.2 | nan % (0) | -36 | -210 | [-600 ; +203] | [-833 ; +458] |

### Simulation C — protection du capital (même plafond de 50 $) — validation (109 cycles)

| Politique | Cycles actifs | P&L net ($) | Par cycle actif | Par $ de capital max | Cycles gagnants | Perte max | Pertes > 6 $ | Drawdown | ES 5 % | Capital max | Achats / ventes | Frais ($) | Coût d'écart ($) | Parts achetées | P&L couvertures ($) | Plancher le plus bas (moy.) | Jackpots conservés | Sans les 5 meilleurs | Écart avec T0-50 ($) | IC 90 % | IC corrigé (13) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T0-50 | 82 | +182 | +2.22 | +5.2 % | 60 | -50 | 20 | 258 | -50.0 | 50 | 82 / 0 | 71 | 19 | 4926 | +0 | -32.1 | nan % (0) | +26 | +0 | — | — |
| T7 | 82 | -28 | -0.34 | -2.9 % | 51 | -7 | 1 | 32 | -5.0 | 16 | 141 / 43 | 31 | 8 | 1846 | -54 | -7.2 | nan % (0) | -36 | -210 | [-613 ; +197] | [-826 ; +503] |
| T7s | 82 | -22 | -0.27 | -3.7 % | 55 | -6 | 0 | 25 | -4.4 | 10 | 139 / 35 | 19 | 5 | 1138 | -37 | -4.4 | nan % (0) | -27 | -204 | [-606 ; +204] | [-853 ; +457] |
| T5 | 82 | -42 | -0.51 | -4.0 % | 74 | -10 | 8 | 42 | -10.0 | 16 | 165 / 0 | 29 | 7 | 2132 | -67 | -7.2 | nan % (0) | -50 | -223 | [-603 ; +169] | [-806 ; +444] |
| T6 | 82 | -25 | -0.30 | -3.9 % | 74 | -6 | 0 | 25 | -6.0 | 10 | 162 / 0 | 18 | 4 | 1301 | -39 | -4.4 | nan % (0) | -30 | -207 | [-604 ; +187] | [-814 ; +483] |

**H1033 — coût économique de la protection stricte (validation)** : T7 − T7s = -6 $ [-13 ; +1] ; pertes > 6 $ : T7 1, T7s 0 ; T5 − T6 = -17 $ (pertes > 6 $ : T5 8, T6 0).

### Simulation A — entrées progressives — TEST (144 cycles)

| Politique | Cycles actifs | P&L net ($) | Par cycle actif | Par $ de capital max | Cycles gagnants | Perte max | Pertes > 6 $ | Drawdown | ES 5 % | Capital max | Achats / ventes | Frais ($) | Coût d'écart ($) | Parts achetées | P&L couvertures ($) | Plancher le plus bas (moy.) | Jackpots conservés | Sans les 5 meilleurs | Écart avec T0-50 ($) | IC 90 % | IC corrigé (13) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T0-50 | 111 | -368 | -3.32 | -7.2 % | 72 | -50 | 37 | 560 | -50.0 | 50 | 111 / 0 | 106 | 32 | 7329 | +0 | -35.7 | nan % (0) | -524 | +0 | — | — |
| T0-10 | 111 | -98 | -0.88 | -9.0 % | 72 | -10 | 37 | 136 | -10.0 | 10 | 111 / 0 | 23 | 7 | 1551 | +0 | -7.6 | nan % (0) | -129 | +270 | [-164 ; +704] | [-439 ; +978] |
| T1 | 111 | -98 | -0.88 | -9.0 % | 72 | -10 | 37 | 136 | -10.0 | 10 | 111 / 0 | 23 | 7 | 1551 | +0 | -7.6 | nan % (0) | -129 | +270 | [-155 ; +714] | [-411 ; +1008] |
| T1v | 111 | -98 | -0.88 | -9.0 % | 72 | -10 | 37 | 136 | -10.0 | 10 | 111 / 0 | 23 | 7 | 1551 | +0 | -7.6 | nan % (0) | -129 | +270 | [-161 ; +712] | [-419 ; +926] |
| T2 | 111 | -98 | -0.88 | -9.0 % | 72 | -10 | 37 | 136 | -10.0 | 10 | 111 / 0 | 23 | 7 | 1551 | +0 | -7.6 | nan % (0) | -129 | +270 | [-161 ; +723] | [-411 ; +979] |
| T2p | 111 | -98 | -0.88 | -9.0 % | 72 | -10 | 37 | 136 | -10.0 | 10 | 111 / 0 | 23 | 7 | 1551 | +0 | -7.6 | nan % (0) | -129 | +270 | [-156 ; +710] | [-410 ; +1005] |

### Simulation B — changement de camp — TEST (144 cycles)

| Politique | Cycles actifs | P&L net ($) | Par cycle actif | Par $ de capital max | Cycles gagnants | Perte max | Pertes > 6 $ | Drawdown | ES 5 % | Capital max | Achats / ventes | Frais ($) | Coût d'écart ($) | Parts achetées | P&L couvertures ($) | Plancher le plus bas (moy.) | Jackpots conservés | Sans les 5 meilleurs | Écart avec T0-50 ($) | IC 90 % | IC corrigé (13) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T0-50 | 111 | -368 | -3.32 | -7.2 % | 72 | -50 | 37 | 560 | -50.0 | 50 | 111 / 0 | 106 | 32 | 7329 | +0 | -35.7 | nan % (0) | -524 | +0 | — | — |
| T1 | 111 | -98 | -0.88 | -9.0 % | 72 | -10 | 37 | 136 | -10.0 | 10 | 111 / 0 | 23 | 7 | 1551 | +0 | -7.6 | nan % (0) | -129 | +270 | [-162 ; +713] | [-426 ; +1003] |
| T2 | 111 | -98 | -0.88 | -9.0 % | 72 | -10 | 37 | 136 | -10.0 | 10 | 111 / 0 | 23 | 7 | 1551 | +0 | -7.6 | nan % (0) | -129 | +270 | [-155 ; +701] | [-383 ; +1002] |
| T4 | 111 | -98 | -0.89 | -9.0 % | 67 | -10 | 33 | 137 | -10.0 | 10 | 111 / 41 | 27 | 8 | 1551 | -0 | -7.6 | nan % (0) | -129 | +270 | [-187 ; +745] | [-465 ; +1014] |
| LAD | 111 | -85 | -0.76 | -7.4 % | 59 | -10 | 17 | 118 | -10.0 | 21 | 141 / 45 | 32 | 9 | 1787 | +13 | -7.6 | nan % (0) | -116 | +283 | [-192 ; +760] | [-462 ; +1077] |
| T5 | 111 | -77 | -0.70 | -5.4 % | 97 | -10 | 13 | 88 | -10.0 | 16 | 221 / 0 | 39 | 6 | 2947 | +21 | -7.6 | nan % (0) | -86 | +291 | [-213 ; +822] | [-534 ; +1138] |
| T7 | 111 | -70 | -0.63 | -5.2 % | 61 | -8 | 5 | 76 | -6.8 | 24 | 194 / 68 | 44 | 9 | 2550 | +28 | -7.6 | nan % (0) | -78 | +298 | [-237 ; +846] | [-512 ; +1167] |

### Simulation C — protection du capital (même plafond de 50 $) — TEST (144 cycles)

| Politique | Cycles actifs | P&L net ($) | Par cycle actif | Par $ de capital max | Cycles gagnants | Perte max | Pertes > 6 $ | Drawdown | ES 5 % | Capital max | Achats / ventes | Frais ($) | Coût d'écart ($) | Parts achetées | P&L couvertures ($) | Plancher le plus bas (moy.) | Jackpots conservés | Sans les 5 meilleurs | Écart avec T0-50 ($) | IC 90 % | IC corrigé (13) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T0-50 | 111 | -368 | -3.32 | -7.2 % | 72 | -50 | 37 | 560 | -50.0 | 50 | 111 / 0 | 106 | 32 | 7329 | +0 | -35.7 | nan % (0) | -524 | +0 | — | — |
| T7 | 111 | -70 | -0.63 | -5.2 % | 61 | -8 | 5 | 76 | -6.8 | 24 | 194 / 68 | 44 | 9 | 2550 | +28 | -7.6 | nan % (0) | -78 | +298 | [-243 ; +843] | [-540 ; +1184] |
| T7s | 111 | -35 | -0.31 | -4.3 % | 71 | -6 | 0 | 42 | -4.8 | 10 | 185 / 59 | 26 | 4 | 1540 | +27 | -4.6 | nan % (0) | -39 | +334 | [-194 ; +885] | [-494 ; +1226] |
| T5 | 111 | -77 | -0.70 | -5.4 % | 97 | -10 | 13 | 88 | -10.0 | 16 | 221 / 0 | 39 | 6 | 2947 | +21 | -7.6 | nan % (0) | -86 | +291 | [-236 ; +819] | [-513 ; +1129] |
| T6 | 111 | -47 | -0.42 | -5.5 % | 97 | -6 | 0 | 53 | -6.0 | 10 | 218 / 0 | 24 | 3 | 1775 | +15 | -4.6 | nan % (0) | -52 | +321 | [-201 ; +846] | [-498 ; +1206] |

**H1033 — coût économique de la protection stricte (TEST)** : T7 − T7s = -36 $ [-58 ; -16] ; pertes > 6 $ : T7 5, T7s 0 ; T5 − T6 = -30 $ (pertes > 6 $ : T5 13, T6 0).

## 5. Sensibilité à la latence et aux frais (TEST)

| Politique | 164 ms | 200 ms | 250 ms | 500 ms | frais×0,5 | frais×1,5 |
|---|---|---|---|---|---|---|
| T0-50 | -368 | -306 | -315 | -162 | -318 | -417 |
| T0-10 | -98 | -83 | -77 | -49 | -88 | -108 |
| T1 | -98 | -83 | -77 | -49 | -88 | -108 |
| T1v | -98 | -83 | -77 | -49 | -88 | -108 |
| T2 | -98 | -83 | -77 | -49 | -88 | -108 |
| T2p | -98 | -83 | -77 | -49 | -88 | -108 |
| T3 | -93 | -87 | -82 | -66 | -85 | -109 |
| T4 | -98 | -90 | -84 | -69 | -86 | -108 |
| LAD | -85 | -77 | -73 | -55 | -70 | -107 |
| T5 | -77 | -74 | -76 | -56 | -45 | -89 |
| T6 | -47 | -44 | -45 | -33 | -27 | -53 |
| T7 | -70 | -70 | -72 | -75 | -43 | -78 |
| T7s | -35 | -34 | -34 | -33 | -26 | -37 |

## 6. H1018 — Scénarios défavorables (164 ms)

| Politique | Normal | acheteurs disparus | couverture + 2 c | fills ÷ 2 | vente de protection impossible | Pertes > 6 $ (normal → pire scénario) | Perte max (normal → pire) |
|---|---|---|---|---|---|---|---|
| T0-50 | -368 | -368 | -368 | -305 | -368 | 37 → 37 | -50 → -50 |
| T1 | -98 | -98 | -98 | -91 | -98 | 37 → 37 | -10 → -10 |
| T3 | -93 | -93 | -101 | -88 | -93 | 34 → 37 | -10 → -10 |
| T4 | -98 | -98 | -98 | -94 | -98 | 33 → 37 | -10 → -10 |
| LAD | -85 | -73 | -90 | -79 | -73 | 17 → 19 | -10 → -10 |
| T5 | -77 | -77 | -100 | -75 | -77 | 13 → 13 | -10 → -10 |
| T7 | -70 | -80 | -89 | -72 | -80 | 5 → 6 | -8 → -8 |
| T7s | -35 | -47 | -44 | -34 | -47 | 0 → 0 | -6 → -6 |

## 7. Renforts, couvertures, inversions

**H1013 — P&L de chaque tranche jusqu'au règlement (validation)**

| Politique | Tranche | Nombre | Coût ($) | P&L ($) | P&L / $ |
|---|---|---|---|---|---|
| T1 | 1 | 82 | 790 | +25 | +3.2 % |
| T1v | 1 | 82 | 790 | +25 | +3.2 % |
| T2 | 1 | 82 | 790 | +25 | +3.2 % |
| T2p | 1 | 82 | 790 | +25 | +3.2 % |

**P&L des transactions de protection par type (validation)** (valeur au règlement − coût)

| Politique | Couverture | Protection (vente) | Inversion | Verrou | Sortie |
|---|---|---|---|---|---|
| T3 | -9 | +0 | +0 | +0 | +0 |
| T4 | +0 | -14 | +0 | +0 | +0 |
| LAD | -17 | -16 | +0 | +0 | +0 |
| T5 | +0 | +0 | +0 | -67 | +0 |
| T6 | +0 | +0 | +0 | -39 | +0 |
| T7 | +0 | -2 | +0 | -50 | -1 |
| T7s | +0 | +0 | +0 | -27 | -10 |

**H1025 — coût par dollar de perte maximale évitée (validation, contre T1)**

| Politique | P&L − T1 ($) | Plancher moyen le plus bas − T1 ($) | Coût par $ évité |
|---|---|---|---|
| T3 | -9 | +0.00 | +nan |
| T4 | -14 | +0.00 | +nan |
| LAD | -32 | +0.00 | +nan |
| T7 | -54 | +0.00 | +nan |

**H1020 — changements de camp (validation)** : aucun.

**H1013 — P&L de chaque tranche jusqu'au règlement (TEST)**

| Politique | Tranche | Nombre | Coût ($) | P&L ($) | P&L / $ |
|---|---|---|---|---|---|
| T1 | 1 | 111 | 1088 | -98 | -9.0 % |
| T1v | 1 | 111 | 1088 | -98 | -9.0 % |
| T2 | 1 | 111 | 1088 | -98 | -9.0 % |
| T2p | 1 | 111 | 1088 | -98 | -9.0 % |

**P&L des transactions de protection par type (TEST)** (valeur au règlement − coût)

| Politique | Couverture | Protection (vente) | Inversion | Verrou | Sortie |
|---|---|---|---|---|---|
| T3 | +5 | +0 | +0 | +0 | +0 |
| T4 | +0 | -0 | +0 | +0 | +0 |
| LAD | +11 | +2 | +0 | +0 | +0 |
| T5 | +0 | +0 | +0 | +21 | +0 |
| T6 | +0 | +0 | +0 | +15 | +0 |
| T7 | +0 | -23 | +0 | +55 | -4 |
| T7s | +0 | +0 | +0 | +26 | +1 |

**H1025 — coût par dollar de perte maximale évitée (TEST, contre T1)**

| Politique | P&L − T1 ($) | Plancher moyen le plus bas − T1 ($) | Coût par $ évité |
|---|---|---|---|
| T3 | +5 | +0.00 | +nan |
| T4 | -0 | +0.00 | +nan |
| LAD | +13 | +0.00 | +nan |
| T7 | +28 | +0.00 | +nan |

**H1020 — changements de camp (TEST)** : aucun.

## 8. H1017 — Régimes au signal d'entrée

| validation : régime | Cycles | T0-50 | T1 | T3 | T5 | T7 | RS |
|---|---|---|---|---|---|---|---|
| aucun signal | 17 | +0 | +0 | +0 | +0 | +0 | +0 |
| choc de liquidations | 2 | +10 | +2 | +2 | +0 | -1 | +10 |
| range | 66 | -13 | -22 | -29 | -39 | -27 | -27 |
| retournement probable | 8 | +14 | +4 | +4 | -8 | +1 | +1 |
| tendance | 16 | +171 | +42 | +40 | +5 | -1 | +5 |

| TEST : régime | Cycles | T0-50 | T1 | T3 | T5 | T7 | RS |
|---|---|---|---|---|---|---|---|
| aucun signal | 20 | +0 | +0 | +0 | +0 | +0 | +0 |
| choc de liquidations | 4 | -61 | -12 | -12 | +1 | -0 | -61 |
| range | 96 | -379 | -88 | -85 | -78 | -72 | -72 |
| retournement probable | 4 | -41 | -8 | -10 | +1 | +0 | +0 |
| tendance | 20 | +113 | +10 | +14 | -2 | +2 | -2 |

## 9. H1036–H1040 — Sauvetage de la première position (entrée 10 $, mêmes cycles)

R0 conserver ; R1 vendre toute la position à −0,15 ; R2 couverture préventive (−0,05 et cerveau A contre ≥ 0,60) ; R3 couverture complète à −0,15 ; R4 couverture tardive (p ≤ 0,25) ; R5 vente de 50 % puis couverture du reste à −0,15 ; R6 inversion complète à −0,15 (vente de tout + 10 $ de l'opposé) ; R7 adaptatif (H1039 : probabilité de redevenir gagnante, apprise sur l'apprentissage ; vend si acheteur net > probabilité + 0,01, couvre si (1 − probabilité) − coût opposé > 0,01, sinon conserve). Couverture = achat de l'opposé pour toutes les parts non appariées. Les noms R0–R7 sont propres à cette étude (aucun lien avec le fantôme R4).

Modèle de récupération H1039 : 2959 états détériorés d'apprentissage (taux de récupération 36.3 %).

### Tournoi de sauvetage R0–R7 — validation (109 cycles)

| Politique | Cycles actifs | P&L net ($) | Par cycle actif | Par $ de capital max | Cycles gagnants | Perte max | Pertes > 6 $ | Drawdown | ES 5 % | Capital max | Achats / ventes | Frais ($) | Coût d'écart ($) | Parts achetées | P&L couvertures ($) | Plancher le plus bas (moy.) | Jackpots conservés | Sans les 5 meilleurs | Écart avec R0 ($) | IC 90 % | IC corrigé (7) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| R0 | 82 | +25 | +0.31 | +3.2 % | 60 | -10 | 20 | 55 | -10.0 | 10 | 82 / 0 | 16 | 4 | 1115 | +0 | -7.2 | nan % (0) | -6 | +0 | — | — |
| R1 | 82 | -27 | -0.33 | -3.4 % | 34 | -7 | 2 | 42 | -5.3 | 10 | 82 / 48 | 27 | 3 | 1115 | -52 | -7.2 | nan % (0) | -57 | -52 | [-133 ; +24] | [-174 ; +61] |
| R2 | 82 | -51 | -0.62 | -4.4 % | 23 | -8 | 2 | 54 | -5.2 | 22 | 141 / 0 | 29 | 7 | 1912 | -76 | -7.2 | nan % (0) | -80 | -76 | [-162 ; +11] | [-205 ; +48] |
| R3 | 82 | -28 | -0.35 | -2.5 % | 34 | -7 | 2 | 43 | -5.3 | 22 | 130 / 0 | 27 | 2 | 1786 | -54 | -7.2 | nan % (0) | -59 | -54 | [-133 ; +23] | [-177 ; +56] |
| R4 | 82 | +48 | +0.59 | +4.5 % | 57 | -9 | 23 | 38 | -8.2 | 25 | 107 / 0 | 20 | 6 | 1454 | +23 | -7.2 | nan % (0) | +17 | +23 | [-14 ; +56] | [-36 ; +70] |
| R5 | 82 | -27 | -0.33 | -3.3 % | 34 | -7 | 2 | 42 | -5.2 | 15 | 130 / 48 | 27 | 3 | 1451 | -53 | -7.2 | nan % (0) | -58 | -53 | [-130 ; +27] | [-167 ; +63] |
| R6 | 82 | -87 | -1.06 | -9.0 % | 54 | -15 | 26 | 179 | -14.1 | 17 | 130 / 48 | 43 | 1 | 2071 | -112 | -8.8 | nan % (0) | -156 | -112 | [-309 ; +74] | [-399 ; +175] |
| R7 | 82 | -27 | -0.33 | -2.8 % | 34 | -7 | 2 | 42 | -5.2 | 20 | 103 / 27 | 27 | 3 | 1416 | -52 | -7.2 | nan % (0) | -57 | -52 | [-130 ; +26] | [-163 ; +68] |

**Niveaux de détérioration (H1036, descriptif, aucun choix) — validation** : R1-10 -53 $ ; R1 -52 $ ; R1-20 -44 $ ; R1-30 +6 $ ; R3-10 -52 $ ; R3 -54 $ ; R3-20 -48 $ ; R3-30 +6 $ (écart avec R0).

**Test décisif (section 9) — validation** : 53 positions devenues défavorables (p ≤ entrée − 0,15) ; ramené à 100.

| Politique | Perdantes sans intervention | Gagnantes sans intervention | Sauvetages (perte réduite) | Coût moyen d'un sauvetage réussi ($ gagnés) | Couvertures inutiles (gagnantes abîmées) | Coût des couvertures inutiles ($) | Perte moyenne R0 → politique | Perte max R0 → politique | P&L net − R0 (défavorables) | P&L net − R0 (tous) |
|---|---|---|---|---|---|---|---|---|---|---|
| R1 | 42 | 49 | 42 | +6.00 | 49 | 184 | -9.37 → -3.23 | -10.0 → -7.2 | -52 | -52 |
| R2 | 42 | 49 | 42 | +6.98 | 47 | 164 | -9.37 → -2.46 | -10.0 → -7.9 | -10 | -76 |
| R3 | 42 | 49 | 42 | +6.07 | 49 | 188 | -9.37 → -3.27 | -10.0 → -7.2 | -54 | -54 |
| R4 | 42 | 49 | 42 | +2.46 | 6 | 31 | -9.37 → -6.97 | -10.0 → -8.8 | +23 | +23 |
| R5 | 42 | 49 | 42 | +6.04 | 49 | 186 | -9.37 → -3.25 | -10.0 → -7.1 | -53 | -53 |
| R6 | 42 | 49 | 42 | +15.04 | 49 | 443 | -9.37 → -12.44 | -10.0 → -14.8 | -112 | -112 |
| R7 | 42 | 49 | 42 | +6.05 | 49 | 185 | -9.37 → -3.23 | -10.0 → -7.1 | -52 | -52 |
| Rv | 42 | 49 | 38 | +3.96 | 49 | 111 | -9.37 → -3.55 | -10.0 → -7.2 | -32 | -32 |
| Ra | 42 | 49 | 38 | +4.03 | 49 | 113 | -9.37 → -3.47 | -10.0 → -7.2 | -33 | -33 |
| Rm | 42 | 49 | 38 | +4.03 | 49 | 111 | -9.37 → -3.52 | -10.0 → -6.0 | -30 | -30 |

**H1038 — vendre ou acheter l'opposé, à risque comparable (cible : pire résultat ≥ −6 $, dès p ≤ entrée − 0,15) — validation**

| Réaction | Cycles où elle a agi | Pire résultat final moyen | Pertes > 6 $ | Capital max moyen ($) | Frais ($) | P&L net ($) | Écart avec R0 (IC 90 %) |
|---|---|---|---|---|---|---|---|
| ne rien faire | 0 | -7.25 | 20 | 7.2 | 16.1 | +25 | +0 [+0 ; +0] |
| vendre une partie | 46 | -5.57 | 2 | 7.2 | 22.7 | -7 | -32 [-80 ; +15] |
| acheter l'opposé | 46 | -5.55 | 3 | 9.3 | 22.9 | -7 | -33 [-81 ; +16] |
| vendre une partie puis acheter l'opposé | 46 | -5.63 | 3 | 7.5 | 22.8 | -5 | -30 [-77 ; +17] |

### Tournoi de sauvetage R0–R7 — TEST (144 cycles)

| Politique | Cycles actifs | P&L net ($) | Par cycle actif | Par $ de capital max | Cycles gagnants | Perte max | Pertes > 6 $ | Drawdown | ES 5 % | Capital max | Achats / ventes | Frais ($) | Coût d'écart ($) | Parts achetées | P&L couvertures ($) | Plancher le plus bas (moy.) | Jackpots conservés | Sans les 5 meilleurs | Écart avec R0 ($) | IC 90 % | IC corrigé (7) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| R0 | 111 | -98 | -0.88 | -9.0 % | 72 | -10 | 37 | 136 | -10.0 | 10 | 111 / 0 | 23 | 7 | 1551 | +0 | -7.6 | nan % (0) | -129 | +0 | — | — |
| R1 | 111 | -99 | -0.89 | -9.1 % | 43 | -7 | 2 | 102 | -5.6 | 10 | 111 / 68 | 39 | 11 | 1551 | -1 | -7.6 | nan % (0) | -130 | -1 | [-97 ; +95] | [-150 ; +142] |
| R2 | 111 | -139 | -1.25 | -8.4 % | 23 | -10 | 4 | 142 | -6.7 | 22 | 198 / 0 | 42 | 12 | 2754 | -41 | -7.6 | nan % (0) | -168 | -41 | [-147 ; +60] | [-196 ; +114] |
| R3 | 111 | -99 | -0.90 | -6.0 % | 43 | -7 | 2 | 103 | -5.6 | 23 | 179 / 0 | 39 | 11 | 2533 | -1 | -7.6 | nan % (0) | -130 | -1 | [-98 ; +96] | [-146 ; +139] |
| R4 | 111 | -144 | -1.29 | -8.5 % | 60 | -10 | 49 | 158 | -8.7 | 25 | 162 / 0 | 30 | 10 | 2287 | -45 | -7.6 | nan % (0) | -175 | -45 | [-123 ; +26] | [-171 ; +61] |
| R5 | 111 | -101 | -0.91 | -8.6 % | 43 | -7 | 2 | 105 | -5.5 | 15 | 179 / 68 | 39 | 11 | 2046 | -3 | -7.6 | nan % (0) | -132 | -3 | [-102 ; +89] | [-147 ; +140] |
| R6 | 111 | -84 | -0.76 | -6.3 % | 78 | -17 | 28 | 111 | -14.5 | 17 | 179 / 68 | 59 | 15 | 2771 | +14 | -9.3 | nan % (0) | -145 | +14 | [-192 ; +230] | [-301 ; +338] |
| R7 | 111 | -93 | -0.84 | -7.1 % | 44 | -10 | 2 | 96 | -6.1 | 21 | 136 / 41 | 38 | 10 | 1929 | +5 | -7.6 | nan % (0) | -124 | +5 | [-87 ; +98] | [-143 ; +143] |

**Niveaux de détérioration (H1036, descriptif, aucun choix) — TEST** : R1-10 -27 $ ; R1 -1 $ ; R1-20 -24 $ ; R1-30 -75 $ ; R3-10 -27 $ ; R3 -1 $ ; R3-20 -25 $ ; R3-30 -76 $ (écart avec R0).

**Test décisif (section 9) — TEST** : 74 positions devenues défavorables (p ≤ entrée − 0,15) ; ramené à 100.

| Politique | Perdantes sans intervention | Gagnantes sans intervention | Sauvetages (perte réduite) | Coût moyen d'un sauvetage réussi ($ gagnés) | Couvertures inutiles (gagnantes abîmées) | Coût des couvertures inutiles ($) | Perte moyenne R0 → politique | Perte max R0 → politique | P&L net − R0 (défavorables) | P&L net − R0 (tous) |
|---|---|---|---|---|---|---|---|---|---|---|
| R1 | 53 | 39 | 53 | +5.98 | 39 | 234 | -9.66 → -3.58 | -10.0 → -7.3 | -1 | -1 |
| R2 | 53 | 39 | 51 | +6.76 | 38 | 197 | -9.66 → -2.80 | -10.0 → -10.0 | +60 | -41 |
| R3 | 53 | 39 | 53 | +6.00 | 39 | 235 | -9.66 → -3.59 | -10.0 → -7.3 | -1 | -1 |
| R4 | 53 | 39 | 53 | +2.61 | 16 | 147 | -9.66 → -7.13 | -10.0 → -9.5 | -45 | -45 |
| R5 | 53 | 39 | 53 | +6.01 | 39 | 237 | -9.66 → -3.61 | -10.0 → -7.3 | -3 | -3 |
| R6 | 53 | 39 | 53 | +13.67 | 39 | 519 | -9.66 → -11.88 | -10.0 → -17.3 | +14 | +14 |
| R7 | 53 | 39 | 51 | +5.96 | 38 | 221 | -9.66 → -3.64 | -10.0 → -10.0 | +5 | +5 |
| Rv | 53 | 39 | 50 | +4.01 | 39 | 152 | -9.66 → -4.29 | -10.0 → -7.3 | -4 | -4 |
| Ra | 53 | 39 | 50 | +4.04 | 39 | 160 | -9.66 → -4.39 | -10.0 → -13.6 | -10 | -10 |
| Rm | 53 | 39 | 50 | +4.02 | 39 | 159 | -9.66 → -4.40 | -10.0 → -13.6 | -10 | -10 |

**H1038 — vendre ou acheter l'opposé, à risque comparable (cible : pire résultat ≥ −6 $, dès p ≤ entrée − 0,15) — TEST**

| Réaction | Cycles où elle a agi | Pire résultat final moyen | Pertes > 6 $ | Capital max moyen ($) | Frais ($) | P&L net ($) | Écart avec R0 (IC 90 %) |
|---|---|---|---|---|---|---|---|
| ne rien faire | 0 | -7.56 | 37 | 7.6 | 22.5 | -98 | +0 [+0 ; +0] |
| vendre une partie | 66 | -5.72 | 2 | 7.6 | 33.1 | -102 | -4 [-70 ; +60] |
| acheter l'opposé | 66 | -5.77 | 8 | 10.2 | 33.2 | -108 | -10 [-80 ; +57] |
| vendre une partie puis acheter l'opposé | 66 | -5.78 | 14 | 8.0 | 33.1 | -108 | -10 [-81 ; +56] |

**Sauvetage — latence et frais (TEST)**

| Politique | 164 ms | 200 ms | 250 ms | 500 ms | frais×0,5 | frais×1,5 |
|---|---|---|---|---|---|---|
| R0 | -98 | -83 | -77 | -49 | -88 | -108 |
| R1 | -99 | -102 | -109 | -96 | -81 | -117 |
| R2 | -139 | -123 | -113 | -112 | -120 | -158 |
| R3 | -99 | -103 | -110 | -95 | -81 | -117 |
| R4 | -144 | -134 | -121 | -112 | -130 | -157 |
| R5 | -101 | -100 | -104 | -93 | -83 | -119 |
| R6 | -84 | -108 | -134 | -147 | -55 | -112 |
| R7 | -93 | -96 | -100 | -90 | -75 | -113 |
| Rv | -102 | -99 | -103 | -81 | -87 | -117 |
| Ra | -108 | -104 | -108 | -85 | -93 | -124 |
| Rm | -108 | -102 | -105 | -83 | -92 | -124 |

**Critère (sauvetage, contre R0)** : une politique n'est retenue que si l'IC corrigé (7) de l'écart avec R0 est > 0 sur le test, la validation va dans le même sens, l'écart reste > 0 à 500 ms et sans les 5 meilleurs cycles.

| Politique | IC corrigé > 0 | Validation même sens | > 0 à 500 ms | > 0 sans les 5 meilleurs | Verdict |
|---|---|---|---|---|---|
| R1 | non | non | non | non | non démontrée |
| R2 | non | non | non | non | non démontrée |
| R3 | non | non | non | non | non démontrée |
| R4 | non | oui | non | non | non démontrée |
| R5 | non | non | non | non | non démontrée |
| R6 | non | non | non | non | non démontrée |
| R7 | non | non | non | non | non démontrée |
## 11. H1041–H1046 — Protection des positions gagnantes (entrée 10 $, mêmes cycles)

P0 conserver ; P-TP100 / P-TP200 tout vendre si acheteur net ≥ 2× / 3× le prix payé ; P-VP vendre 50 % si acheteur net ≥ prix payé + 0,20 ; P-TR10…40 trailing : tout vendre quand le profit liquidable (acheteurs affichés, frais, profondeur) retombe de 10/20/30/40 % sous son maximum (maximum ≥ 2 $) ; P-TF trailing fondamental : p de règlement recalibrée ≤ son maximum − 0,15 ET cerveau A contre ≥ 0,55 (momentum, OFI, liquidations, Chainlink ; ETH/SOL non disponibles avant le 12.10) ; P-L0 (free-roll : mise récupérée), P-L5, P-L10, P-L20, P-Lm6 (5 CHF) : vente de la quantité minimale qui verrouille ce résultat dans le cas perdant, dès que la profondeur le permet ; à retracement de 30 % : P-HA vente partielle, P-HB achat de l'opposé, P-HC moitié-moitié (verrou 0 $) ; P-PF cliquet du portefeuille : à 30 % de retracement, plancher contractuel porté à 50 % du gain liquidable maximal par le moyen le moins cher. Un gain n'est « verrouillé » que s'il est garanti par l'inventaire exécuté.

### Protection des gains — validation (109 cycles)

| Politique | Cycles actifs | P&L net ($) | Par cycle actif | Par $ de capital max | Cycles gagnants | Perte max | Pertes > 6 $ | Drawdown | ES 5 % | Capital max | Achats / ventes | Frais ($) | Coût d'écart ($) | Parts achetées | P&L couvertures ($) | Plancher le plus bas (moy.) | Jackpots conservés | Sans les 5 meilleurs | Écart avec P0 ($) | IC 90 % | IC corrigé (17) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P0 | 82 | +25 | +0.31 | +3.2 % | 60 | -10 | 20 | 55 | -10.0 | 10 | 82 / 0 | 16 | 4 | 1115 | +0 | -7.2 | nan % (0) | -6 | +0 | — | — |
| P-TP100 | 82 | +25 | +0.31 | +3.2 % | 60 | -10 | 20 | 55 | -10.0 | 10 | 82 / 0 | 16 | 4 | 1115 | +0 | -7.2 | nan % (0) | -6 | +0 | [+0 ; +0] | [+0 ; +0] |
| P-TP200 | 82 | +25 | +0.31 | +3.2 % | 60 | -10 | 20 | 55 | -10.0 | 10 | 82 / 0 | 16 | 4 | 1115 | +0 | -7.2 | nan % (0) | -6 | +0 | [+0 ; +0] | [+0 ; +0] |
| P-VP | 82 | +1 | +0.01 | +0.2 % | 60 | -10 | 19 | 64 | -10.0 | 10 | 82 / 45 | 18 | 5 | 1115 | +0 | -7.2 | nan % (0) | -23 | -24 | [-37 ; -9] | [-44 ; +4] |
| P-TR10 | 82 | -10 | -0.12 | -1.2 % | 64 | -10 | 15 | 70 | -10.0 | 10 | 82 / 41 | 22 | 7 | 1115 | +0 | -7.2 | nan % (0) | -33 | -35 | [-81 ; +16] | [-108 ; +54] |
| P-TR20 | 82 | -6 | -0.08 | -0.8 % | 63 | -10 | 15 | 71 | -10.0 | 10 | 82 / 33 | 21 | 5 | 1115 | +0 | -7.2 | nan % (0) | -33 | -32 | [-80 ; +20] | [-112 ; +62] |
| P-TR30 | 82 | +2 | +0.03 | +0.3 % | 63 | -10 | 15 | 69 | -10.0 | 10 | 82 / 28 | 21 | 4 | 1115 | +0 | -7.2 | nan % (0) | -27 | -23 | [-71 ; +29] | [-96 ; +67] |
| P-TR40 | 82 | -1 | -0.01 | -0.1 % | 61 | -10 | 15 | 67 | -10.0 | 10 | 82 / 24 | 21 | 3 | 1115 | +0 | -7.2 | nan % (0) | -32 | -26 | [-76 ; +27] | [-108 ; +74] |
| P-TF | 82 | +2 | +0.02 | +0.2 % | 53 | -10 | 16 | 61 | -10.0 | 10 | 82 / 18 | 20 | 4 | 1115 | +0 | -7.2 | nan % (0) | -29 | -23 | [-69 ; +24] | [-94 ; +59] |
| P-L0 | 82 | -20 | -0.25 | -2.6 % | 68 | -10 | 5 | 22 | -8.3 | 10 | 82 / 82 | 29 | 7 | 1115 | +0 | -7.2 | nan % (0) | -29 | -46 | [-121 ; +34] | [-172 ; +87] |
| P-L5 | 82 | +30 | +0.37 | +3.8 % | 61 | -10 | 19 | 57 | -10.0 | 10 | 82 / 14 | 17 | 5 | 1115 | +0 | -7.2 | nan % (0) | +3 | +5 | [-14 ; +35] | [-18 ; +56] |
| P-L10 | 82 | +25 | +0.31 | +3.2 % | 60 | -10 | 20 | 55 | -10.0 | 10 | 82 / 0 | 16 | 4 | 1115 | +0 | -7.2 | nan % (0) | -6 | +0 | [+0 ; +0] | [+0 ; +0] |
| P-L20 | 82 | +25 | +0.31 | +3.2 % | 60 | -10 | 20 | 55 | -10.0 | 10 | 82 / 0 | 16 | 4 | 1115 | +0 | -7.2 | nan % (0) | -6 | +0 | [+0 ; +0] | [+0 ; +0] |
| P-Lm6 | 82 | -11 | -0.14 | -1.4 % | 60 | -6 | 0 | 43 | -6.0 | 10 | 82 / 78 | 23 | 6 | 1115 | +0 | -7.2 | nan % (0) | -27 | -37 | [-77 ; +4] | [-99 ; +35] |
| P-HA | 82 | +12 | +0.14 | +1.5 % | 60 | -10 | 16 | 73 | -10.0 | 10 | 82 / 21 | 19 | 5 | 1115 | +0 | -7.2 | nan % (0) | -18 | -14 | [-53 ; +28] | [-72 ; +58] |
| P-HB | 82 | +6 | +0.07 | +0.7 % | 59 | -10 | 15 | 64 | -10.0 | 19 | 106 / 0 | 20 | 4 | 1452 | +0 | -7.2 | nan % (0) | -23 | -19 | [-65 ; +30] | [-93 ; +64] |
| P-HC | 82 | +8 | +0.09 | +1.0 % | 60 | -10 | 15 | 63 | -10.0 | 10 | 106 / 24 | 20 | 4 | 1282 | +0 | -7.2 | nan % (0) | -22 | -18 | [-61 ; +30] | [-89 ; +62] |
| P-PF | 82 | +44 | +0.53 | +5.3 % | 65 | -10 | 15 | 48 | -10.0 | 18 | 90 / 9 | 19 | 4 | 1244 | +0 | -7.2 | nan % (0) | +13 | +18 | [-26 ; +65] | [-49 ; +104] |

**H1041 — profit abandonné (P0, validation)** : 82 positions ; prix d'achat moyen 0.715 ; 13.6 parts ; meilleur acheteur moyen pendant le cycle 0.925 ; profit latent maximal exécutable moyen +2.89 $ ; profit final moyen +0.31 $ ; profit abandonné moyen 0.27 $ ; gagnants (≥ +5 $ liquidables) devenus perdants : **1** sur 14.

| Politique | Gagnants devenus perdants | Évités vs P0 | Jackpots supprimés | Profit latent abandonné ($) | Profit réellement verrouillé ($) | Fills partiels | P&L − P0 ($) |
|---|---|---|---|---|---|---|---|
| P0 | 1 | 0 | 0 / 0 | 22 | 0 | 0 | +0 |
| P-TP100 | 1 | 0 | 0 / 0 | 22 | 0 | 0 | +0 |
| P-TP200 | 1 | 0 | 0 / 0 | 22 | 0 | 0 | +0 |
| P-VP | 1 | 0 | 0 / 0 | 43 | 0 | 3 | -24 |
| P-TR10 | 0 | 1 | 0 / 0 | 96 | 78 | 10 | -35 |
| P-TR20 | 1 | 0 | 0 / 0 | 93 | 56 | 7 | -32 |
| P-TR30 | 1 | 0 | 0 / 0 | 86 | 40 | 6 | -23 |
| P-TR40 | 2 | -1 | 0 / 0 | 88 | 19 | 9 | -26 |
| P-TF | 3 | -2 | 0 / 0 | 76 | 6 | 7 | -23 |
| P-L0 | 0 | 1 | 0 / 0 | 208 | 3 | 12 | -46 |
| P-L5 | 0 | 1 | 0 / 0 | 23 | 70 | 1 | +5 |
| P-L10 | 1 | 0 | 0 / 0 | 22 | 0 | 0 | +0 |
| P-L20 | 1 | 0 | 0 / 0 | 22 | 0 | 0 | +0 |
| P-Lm6 | 1 | 0 | 0 / 0 | 122 | 0 | 8 | -37 |
| P-HA | 0 | 1 | 0 / 0 | 71 | 1 | 4 | -14 |
| P-HB | 2 | -1 | 0 / 0 | 82 | 3 | 0 | -19 |
| P-HC | 1 | 0 | 0 / 0 | 82 | 3 | 4 | -18 |
| P-PF | 0 | 1 | 0 / 0 | 50 | 23 | 2 | +18 |

### Protection des gains — TEST (144 cycles)

| Politique | Cycles actifs | P&L net ($) | Par cycle actif | Par $ de capital max | Cycles gagnants | Perte max | Pertes > 6 $ | Drawdown | ES 5 % | Capital max | Achats / ventes | Frais ($) | Coût d'écart ($) | Parts achetées | P&L couvertures ($) | Plancher le plus bas (moy.) | Jackpots conservés | Sans les 5 meilleurs | Écart avec P0 ($) | IC 90 % | IC corrigé (17) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P0 | 111 | -98 | -0.88 | -9.0 % | 72 | -10 | 37 | 136 | -10.0 | 10 | 111 / 0 | 23 | 7 | 1551 | +0 | -7.6 | nan % (0) | -129 | +0 | — | — |
| P-TP100 | 111 | -98 | -0.88 | -9.0 % | 72 | -10 | 37 | 136 | -10.0 | 10 | 111 / 0 | 23 | 7 | 1551 | +0 | -7.6 | nan % (0) | -129 | +0 | [+0 ; +0] | [+0 ; +0] |
| P-TP200 | 111 | -98 | -0.88 | -9.0 % | 72 | -10 | 37 | 136 | -10.0 | 10 | 111 / 0 | 23 | 7 | 1551 | +0 | -7.6 | nan % (0) | -129 | +0 | [+0 ; +0] | [+0 ; +0] |
| P-VP | 111 | -104 | -0.94 | -9.6 % | 72 | -10 | 32 | 135 | -10.0 | 10 | 111 / 52 | 25 | 8 | 1551 | +0 | -7.6 | nan % (0) | -129 | -6 | [-30 ; +23] | [-44 ; +46] |
| P-TR10 | 111 | -85 | -0.77 | -7.9 % | 83 | -10 | 26 | 102 | -10.0 | 10 | 111 / 52 | 30 | 8 | 1551 | +0 | -7.6 | nan % (0) | -109 | +13 | [-56 ; +89] | [-99 ; +146] |
| P-TR20 | 111 | -100 | -0.90 | -9.2 % | 80 | -10 | 27 | 118 | -10.0 | 10 | 111 / 47 | 30 | 8 | 1551 | +0 | -7.6 | nan % (0) | -127 | -2 | [-70 ; +71] | [-113 ; +121] |
| P-TR30 | 111 | -99 | -0.89 | -9.1 % | 77 | -10 | 27 | 124 | -10.0 | 10 | 111 / 43 | 30 | 8 | 1551 | +0 | -7.6 | nan % (0) | -127 | -1 | [-67 ; +70] | [-110 ; +122] |
| P-TR40 | 111 | -96 | -0.86 | -8.8 % | 76 | -10 | 27 | 120 | -10.0 | 10 | 111 / 38 | 30 | 7 | 1551 | +0 | -7.6 | nan % (0) | -124 | +3 | [-63 ; +73] | [-103 ; +121] |
| P-TF | 111 | -90 | -0.82 | -8.3 % | 64 | -10 | 27 | 116 | -10.0 | 10 | 111 / 27 | 28 | 7 | 1551 | +0 | -7.6 | nan % (0) | -121 | +8 | [-55 ; +74] | [-91 ; +114] |
| P-L0 | 111 | -58 | -0.53 | -5.4 % | 80 | -10 | 10 | 75 | -10.0 | 10 | 111 / 103 | 39 | 8 | 1551 | +0 | -7.6 | nan % (0) | -70 | +40 | [-60 ; +138] | [-129 ; +209] |
| P-L5 | 111 | -98 | -0.89 | -9.0 % | 73 | -10 | 36 | 134 | -10.0 | 10 | 111 / 22 | 24 | 8 | 1551 | +0 | -7.6 | nan % (0) | -125 | -0 | [-19 ; +31] | [-25 ; +56] |
| P-L10 | 111 | -98 | -0.88 | -9.0 % | 72 | -10 | 37 | 136 | -10.0 | 10 | 111 / 0 | 23 | 7 | 1551 | +0 | -7.6 | nan % (0) | -129 | +0 | [+0 ; +0] | [+0 ; +0] |
| P-L20 | 111 | -98 | -0.88 | -9.0 % | 72 | -10 | 37 | 136 | -10.0 | 10 | 111 / 0 | 23 | 7 | 1551 | +0 | -7.6 | nan % (0) | -129 | +0 | [+0 ; +0] | [+0 ; +0] |
| P-Lm6 | 111 | -85 | -0.77 | -7.8 % | 72 | -6 | 0 | 102 | -6.0 | 10 | 111 / 108 | 32 | 9 | 1551 | +0 | -7.6 | nan % (0) | -102 | +13 | [-36 ; +64] | [-69 ; +100] |
| P-HA | 111 | -54 | -0.48 | -4.9 % | 73 | -10 | 27 | 90 | -10.0 | 10 | 111 / 32 | 27 | 8 | 1551 | +0 | -7.6 | nan % (0) | -85 | +45 | [-10 ; +101] | [-43 ; +146] |
| P-HB | 111 | -67 | -0.60 | -5.6 % | 72 | -10 | 27 | 96 | -10.0 | 16 | 145 / 0 | 28 | 8 | 1997 | +0 | -7.6 | nan % (0) | -97 | +32 | [-24 ; +92] | [-59 ; +145] |
| P-HC | 111 | -66 | -0.60 | -6.1 % | 72 | -10 | 27 | 96 | -10.0 | 10 | 144 / 34 | 28 | 8 | 1769 | +0 | -7.6 | nan % (0) | -97 | +32 | [-27 ; +92] | [-60 ; +138] |
| P-PF | 111 | -103 | -0.92 | -9.0 % | 76 | -10 | 30 | 128 | -10.0 | 21 | 120 / 23 | 28 | 7 | 1706 | +0 | -7.6 | nan % (0) | -133 | -4 | [-63 ; +57] | [-101 ; +101] |

**H1041 — profit abandonné (P0, TEST)** : 111 positions ; prix d'achat moyen 0.712 ; 14.0 parts ; meilleur acheteur moyen pendant le cycle 0.905 ; profit latent maximal exécutable moyen +2.75 $ ; profit final moyen -0.88 $ ; profit abandonné moyen 0.44 $ ; gagnants (≥ +5 $ liquidables) devenus perdants : **1** sur 22.

| Politique | Gagnants devenus perdants | Évités vs P0 | Jackpots supprimés | Profit latent abandonné ($) | Profit réellement verrouillé ($) | Fills partiels | P&L − P0 ($) |
|---|---|---|---|---|---|---|---|
| P0 | 1 | 0 | 0 / 0 | 49 | 0 | 0 | +0 |
| P-TP100 | 1 | 0 | 0 / 0 | 49 | 0 | 0 | +0 |
| P-TP200 | 1 | 0 | 0 / 0 | 49 | 0 | 0 | +0 |
| P-VP | 1 | 0 | 0 / 0 | 73 | 0 | 4 | -6 |
| P-TR10 | 0 | 1 | 0 / 0 | 132 | 106 | 8 | +13 |
| P-TR20 | 1 | 0 | 0 / 0 | 137 | 81 | 15 | -2 |
| P-TR30 | 3 | -2 | 0 / 0 | 136 | 58 | 14 | -1 |
| P-TR40 | 3 | -2 | 0 / 0 | 134 | 41 | 13 | +3 |
| P-TF | 6 | -5 | 0 / 0 | 115 | 8 | 19 | +8 |
| P-L0 | 0 | 1 | 0 / 0 | 261 | 7 | 7 | +40 |
| P-L5 | 0 | 1 | 0 / 0 | 51 | 110 | 1 | -0 |
| P-L10 | 1 | 0 | 0 / 0 | 49 | 0 | 0 | +0 |
| P-L20 | 1 | 0 | 0 / 0 | 49 | 0 | 0 | +0 |
| P-Lm6 | 1 | 0 | 0 / 0 | 162 | 0 | 15 | +13 |
| P-HA | 0 | 1 | 0 / 0 | 97 | 1 | 8 | +45 |
| P-HB | 1 | 0 | 0 / 0 | 108 | 5 | 0 | +32 |
| P-HC | 1 | 0 | 0 / 0 | 108 | 3 | 9 | +32 |
| P-PF | 3 | -2 | 0 / 0 | 107 | 43 | 2 | -4 |

**Protection des gains — latence et frais (TEST)**

| Politique | 164 ms | 200 ms | 250 ms | 500 ms | frais×0,5 | frais×1,5 |
|---|---|---|---|---|---|---|
| P0 | -98 | -83 | -77 | -49 | -88 | -108 |
| P-TP100 | -98 | -83 | -77 | -49 | -88 | -108 |
| P-TP200 | -98 | -83 | -77 | -49 | -88 | -108 |
| P-VP | -104 | -89 | -88 | -54 | -89 | -110 |
| P-TR10 | -85 | -84 | -89 | -44 | -66 | -98 |
| P-TR20 | -100 | -99 | -101 | -60 | -78 | -117 |
| P-TR30 | -99 | -93 | -98 | -54 | -77 | -116 |
| P-TR40 | -96 | -89 | -96 | -52 | -79 | -116 |
| P-TF | -90 | -84 | -94 | -42 | -74 | -112 |
| P-L0 | -58 | -54 | -56 | -54 | -46 | -91 |
| P-L5 | -98 | -83 | -77 | -49 | -93 | -118 |
| P-L10 | -98 | -83 | -77 | -49 | -88 | -108 |
| P-L20 | -98 | -83 | -77 | -49 | -88 | -108 |
| P-Lm6 | -85 | -75 | -73 | -58 | -70 | -100 |
| P-HA | -54 | -53 | -59 | -20 | -47 | -77 |
| P-HB | -67 | -66 | -72 | -23 | -53 | -93 |
| P-HC | -66 | -67 | -71 | -23 | -53 | -92 |
| P-PF | -103 | -81 | -97 | -45 | -61 | -80 |

| Politique | IC corrigé (17) > 0 contre P0 | Validation même sens | > 0 à 500 ms | > 0 sans les 5 meilleurs | Verdict |
|---|---|---|---|---|---|
| P-TP100 | non | non | non | non | non démontrée |
| P-TP200 | non | non | non | non | non démontrée |
| P-VP | non | non | non | non | non démontrée |
| P-TR10 | non | non | oui | non | non démontrée |
| P-TR20 | non | non | non | non | non démontrée |
| P-TR30 | non | non | non | non | non démontrée |
| P-TR40 | non | non | non | non | non démontrée |
| P-TF | non | non | oui | non | non démontrée |
| P-L0 | non | non | non | non | non démontrée |
| P-L5 | non | oui | non | non | non démontrée |
| P-L10 | non | non | non | non | non démontrée |
| P-L20 | non | non | non | non | non démontrée |
| P-Lm6 | non | non | non | non | non démontrée |
| P-HA | non | non | oui | non | non démontrée |
| P-HB | non | non | oui | non | non démontrée |
| P-HC | non | non | oui | non | non démontrée |
| P-PF | non | oui | oui | non | non démontrée |
## 10. Critère de réussite (section 43) sur TEST

| Politique | IC corrigé > 0 | Pertes > 6 $ pas plus fréquentes | Jackpots ≥ 50 % | Écart > 0 à 500 ms | Écart > 0 sans les 5 meilleurs | Validation même sens | Verdict |
|---|---|---|---|---|---|---|---|
| T0-10 | non | oui | oui | oui | oui | non | non démontrée |
| T1 | non | oui | oui | oui | oui | non | non démontrée |
| T1v | non | oui | oui | oui | oui | non | non démontrée |
| T2 | non | oui | oui | oui | oui | non | non démontrée |
| T2p | non | oui | oui | oui | oui | non | non démontrée |
| T3 | non | oui | oui | oui | oui | non | non démontrée |
| T4 | non | oui | oui | oui | oui | non | non démontrée |
| LAD | non | oui | oui | oui | oui | non | non démontrée |
| T5 | non | oui | oui | oui | oui | non | non démontrée |
| T6 | non | oui | oui | oui | oui | non | non démontrée |
| T7 | non | oui | oui | oui | oui | non | non démontrée |
| T7s | non | oui | oui | oui | oui | non | non démontrée |
| RS | non | oui | oui | — | non | non | non démontrée |

Journal T7 (TEST) : chaque transaction avec les deux paiements possibles après exécution — resultat_reversal_h1003_journal_favori.csv.gz, 262 lignes.


## Limites
- Exécution preneur seulement ; notre propre impact au-delà de 5 s n'est pas modélisé.
- Toutes les politiques partagent la même probabilité ; si elle n'a pas d'avantage sur le marché, la gestion ne peut pas en créer.
- Nombreuses politiques : seuls les IC corrigés comptent. Peu de cycles par échantillon.

_Calcul : 947 s._
