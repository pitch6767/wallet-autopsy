# Bot95 — Adaptive Reversal & Hedge Engine H1003–H1035 (CONFIRMATION (≥ 13.10))

Généré le 15.10.2026 13:06 UTC. Cycles avec résultat officiel : apprentissage 216, validation 109, confirmation (≥ 13.10) 674. Capital ≤ 50 $, limite 5 CHF = 6.00 $. Exécution preneur sur le carnet enregistré. Aucun ordre ; aucun fantôme modifié.

## 1. Cerveau A — trajectoire courte du BTC (H1004, H1009, H1019, H1026–H1028)

| Cible | Échantillon | Taux de base | AUC momentum seul | AUC toutes familles | Gain d'AUC (IC 90 %) |
|---|---|---|---|---|---|
| hausse à 1 s | validation | 22.0 % | 0.578 | 0.618 | +0.040 [+0.031 ; +0.049] |
| hausse à 1 s | CONFIRMATION (≥ 13.10) | 26.3 % | 0.603 | 0.666 | +0.064 [+0.060 ; +0.068] |
| hausse à 3 s | validation | 29.7 % | 0.604 | 0.666 | +0.062 [+0.056 ; +0.069] |
| hausse à 3 s | CONFIRMATION (≥ 13.10) | 34.3 % | 0.615 | 0.705 | +0.090 [+0.087 ; +0.094] |
| hausse à 5 s | validation | 32.1 % | 0.619 | 0.692 | +0.072 [+0.065 ; +0.080] |
| hausse à 5 s | CONFIRMATION (≥ 13.10) | 37.9 % | 0.616 | 0.709 | +0.093 [+0.089 ; +0.097] |
| hausse à 10 s | validation | 35.9 % | 0.623 | 0.700 | +0.077 [+0.067 ; +0.087] |
| hausse à 10 s | CONFIRMATION (≥ 13.10) | 42.3 % | 0.601 | 0.691 | +0.090 [+0.086 ; +0.094] |
| hausse à 15 s | validation | 39.3 % | 0.603 | 0.692 | +0.089 [+0.078 ; +0.100] |
| hausse à 15 s | CONFIRMATION (≥ 13.10) | 44.9 % | 0.567 | 0.668 | +0.102 [+0.097 ; +0.107] |
| hausse à 30 s | validation | 43.1 % | 0.591 | 0.663 | +0.072 [+0.058 ; +0.086] |
| hausse à 30 s | CONFIRMATION (≥ 13.10) | 47.8 % | 0.538 | 0.615 | +0.077 [+0.072 ; +0.083] |
| hausse à 60 s | validation | 44.7 % | 0.576 | 0.623 | +0.047 [+0.030 ; +0.064] |
| hausse à 60 s | CONFIRMATION (≥ 13.10) | 49.2 % | 0.522 | 0.576 | +0.054 [+0.048 ; +0.062] |
| retournement à 30 s | validation | 24.8 % | 0.556 | 0.556 | +0.000 [-0.006 ; +0.007] |
| retournement à 30 s | CONFIRMATION (≥ 13.10) | 30.4 % | 0.534 | 0.531 | -0.002 [-0.005 ; +0.000] |

**Ablation (hausse à 30 s) : perte d'AUC quand on retire une famille** (positif = la famille apporte)

| Famille retirée | validation | CONFIRMATION (≥ 13.10) |
|---|---|---|
| mom | +0.0043 [+0.0007 ; +0.0080] | -0.0002 [-0.0017 ; +0.0013] |
| flux | +0.0014 [+0.0006 ; +0.0019] | -0.0001 [-0.0005 ; +0.0003] |
| carnet | +0.0606 [+0.0481 ; +0.0742] | +0.0626 [+0.0579 ; +0.0680] |
| inter | +0.0001 [+0.0000 ; +0.0002] | -0.0006 [-0.0010 ; +0.0001] |
| liq | -0.0000 [-0.0006 ; +0.0005] | -0.0005 [-0.0007 ; -0.0002] |
| cl | +0.0001 [+0.0000 ; +0.0001] | -0.0002 [-0.0004 ; +0.0000] |

**Ampleur du mouvement à 30 s (H1009)** — Brier : modèle gaussien (volatilité seule) contre logistique toutes familles

| Seuil | Échantillon | Fréquence | Brier gaussien | Brier modèle | Différence (IC 90 %) |
|---|---|---|---|---|---|
| ≥ 5 $ | validation | 65.0 % | 0.2208 | 0.2225 | +0.0017 [-0.0021 ; +0.0056] |
| ≥ 5 $ | CONFIRMATION (≥ 13.10) | 76.9 % | 0.1688 | 0.1728 | +0.0041 [+0.0030 ; +0.0052] |
| ≥ 10 $ | validation | 48.6 % | 0.2576 | 0.2482 | -0.0094 [-0.0134 ; -0.0058] |
| ≥ 10 $ | CONFIRMATION (≥ 13.10) | 61.8 % | 0.2303 | 0.2292 | -0.0012 [-0.0026 ; +0.0004] |
| ≥ 20 $ | validation | 24.3 % | 0.1912 | 0.1792 | -0.0120 [-0.0154 ; -0.0090] |
| ≥ 20 $ | CONFIRMATION (≥ 13.10) | 38.2 % | 0.2335 | 0.2282 | -0.0053 [-0.0072 ; -0.0034] |
| ≥ 40 $ | validation | 5.6 % | 0.0531 | 0.0515 | -0.0017 [-0.0025 ; -0.0008] |
| ≥ 40 $ | CONFIRMATION (≥ 13.10) | 13.3 % | 0.1089 | 0.1085 | -0.0004 [-0.0018 ; +0.0010] |

## 2. Cerveau B — probabilité de règlement (H1016)

logit p = -0.073 + 0.010 × logit(M0) + 0.937 × logit(milieu Polymarket) (sans milieu : -0.068 + 0.481 × logit(M0)) ; 4559 décisions d'apprentissage.


# FAMILLE D'ENTRÉE : avantage du cerveau B ≥ e


**Calibration de règlement (H1016, décisions toutes les 10 s)** — Brier et log loss ; écart = cerveau B − milieu du marché

| Échantillon | Décisions | Brier marché | Brier M0 brut | Brier cerveau B | Cerveau B − marché (IC 90 %) | LL marché | LL cerveau B | Ajout de a30 (H1026) : ΔBrier (IC 90 %) |
|---|---|---|---|---|---|---|---|---|
| apprentissage | 4559 | 0.1683 | 0.1844 | 0.1678 | -0.0005 [-0.0019 ; +0.0009] | 0.4981 | 0.4974 | -0.00044 [-0.00118 ; +0.00031] |
| validation | 2301 | 0.1363 | 0.1308 | 0.1364 | +0.0001 [-0.0017 ; +0.0018] | 0.4226 | 0.4237 | -0.00062 [-0.00165 ; +0.00041] |
| CONFIRMATION (≥ 13.10) | 14070 | 0.1658 | 0.1731 | 0.1660 | +0.0003 [-0.0006 ; +0.0011] | 0.4949 | 0.4957 | -0.00013 [-0.00080 ; +0.00051] |

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

### CONFIRMATION (≥ 13.10) (674 cycles)

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

### Simulation A — entrées progressives — CONFIRMATION (≥ 13.10) (674 cycles)

| Politique | Cycles actifs | P&L net ($) | Par cycle actif | Par $ de capital max | Cycles gagnants | Perte max | Pertes > 6 $ | Drawdown | ES 5 % | Capital max | Achats / ventes | Frais ($) | Coût d'écart ($) | Parts achetées | P&L couvertures ($) | Plancher le plus bas (moy.) | Jackpots conservés | Sans les 5 meilleurs | Écart avec T0-50 ($) | IC 90 % | IC corrigé (13) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T0-50 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | — | — |
| T0-10 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| T1 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| T1v | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| T2 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| T2p | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |

### Simulation B — changement de camp — CONFIRMATION (≥ 13.10) (674 cycles)

| Politique | Cycles actifs | P&L net ($) | Par cycle actif | Par $ de capital max | Cycles gagnants | Perte max | Pertes > 6 $ | Drawdown | ES 5 % | Capital max | Achats / ventes | Frais ($) | Coût d'écart ($) | Parts achetées | P&L couvertures ($) | Plancher le plus bas (moy.) | Jackpots conservés | Sans les 5 meilleurs | Écart avec T0-50 ($) | IC 90 % | IC corrigé (13) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T0-50 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | — | — |
| T1 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| T2 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| T4 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| LAD | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| T5 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| T7 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |

### Simulation C — protection du capital (même plafond de 50 $) — CONFIRMATION (≥ 13.10) (674 cycles)

| Politique | Cycles actifs | P&L net ($) | Par cycle actif | Par $ de capital max | Cycles gagnants | Perte max | Pertes > 6 $ | Drawdown | ES 5 % | Capital max | Achats / ventes | Frais ($) | Coût d'écart ($) | Parts achetées | P&L couvertures ($) | Plancher le plus bas (moy.) | Jackpots conservés | Sans les 5 meilleurs | Écart avec T0-50 ($) | IC 90 % | IC corrigé (13) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T0-50 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | — | — |
| T7 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| T7s | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| T5 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| T6 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |

**H1033 — coût économique de la protection stricte (CONFIRMATION (≥ 13.10))** : T7 − T7s = +0 $ [+0 ; +0] ; pertes > 6 $ : T7 0, T7s 0 ; T5 − T6 = +0 $ (pertes > 6 $ : T5 0, T6 0).

## 5. Sensibilité à la latence et aux frais (CONFIRMATION (≥ 13.10))

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

**H1013 — P&L de chaque tranche jusqu'au règlement (CONFIRMATION (≥ 13.10))**

| Politique | Tranche | Nombre | Coût ($) | P&L ($) | P&L / $ |
|---|---|---|---|---|---|

**P&L des transactions de protection par type (CONFIRMATION (≥ 13.10))** (valeur au règlement − coût)

| Politique | Couverture | Protection (vente) | Inversion | Verrou | Sortie |
|---|---|---|---|---|---|
| T3 | +0 | +0 | +0 | +0 | +0 |
| T4 | +0 | +0 | +0 | +0 | +0 |
| LAD | +0 | +0 | +0 | +0 | +0 |
| T5 | +0 | +0 | +0 | +0 | +0 |
| T6 | +0 | +0 | +0 | +0 | +0 |
| T7 | +0 | +0 | +0 | +0 | +0 |
| T7s | +0 | +0 | +0 | +0 | +0 |

**H1025 — coût par dollar de perte maximale évitée (CONFIRMATION (≥ 13.10), contre T1)**

| Politique | P&L − T1 ($) | Plancher moyen le plus bas − T1 ($) | Coût par $ évité |
|---|---|---|---|
| T3 | +0 | +0.00 | +nan |
| T4 | +0 | +0.00 | +nan |
| LAD | +0 | +0.00 | +nan |
| T7 | +0 | +0.00 | +nan |

**H1020 — changements de camp (CONFIRMATION (≥ 13.10))** : aucun.

## 8. H1017 — Régimes au signal d'entrée

| validation : régime | Cycles | T0-50 | T1 | T3 | T5 | T7 | RS |
|---|---|---|---|---|---|---|---|
| aucun signal | 109 | +0 | +0 | +0 | +0 | +0 | +0 |

| CONFIRMATION (≥ 13.10) : régime | Cycles | T0-50 | T1 | T3 | T5 | T7 | RS |
|---|---|---|---|---|---|---|---|
| aucun signal | 674 | +0 | +0 | +0 | +0 | +0 | +0 |

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

### Tournoi de sauvetage R0–R7 — CONFIRMATION (≥ 13.10) (674 cycles)

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

**Niveaux de détérioration (H1036, descriptif, aucun choix) — CONFIRMATION (≥ 13.10)** : R1-10 +0 $ ; R1 +0 $ ; R1-20 +0 $ ; R1-30 +0 $ ; R3-10 +0 $ ; R3 +0 $ ; R3-20 +0 $ ; R3-30 +0 $ (écart avec R0).

**Test décisif (section 9) — CONFIRMATION (≥ 13.10)** : 0 positions devenues défavorables (p ≤ entrée − 0,15) ; ramené à 100.

| Politique | Perdantes sans intervention | Gagnantes sans intervention | Sauvetages (perte réduite) | Coût moyen d'un sauvetage réussi ($ gagnés) | Couvertures inutiles (gagnantes abîmées) | Coût des couvertures inutiles ($) | Perte moyenne R0 → politique | Perte max R0 → politique | P&L net − R0 (défavorables) | P&L net − R0 (tous) |
|---|---|---|---|---|---|---|---|---|---|---|

**H1038 — vendre ou acheter l'opposé, à risque comparable (cible : pire résultat ≥ −6 $, dès p ≤ entrée − 0,15) — CONFIRMATION (≥ 13.10)**

| Réaction | Cycles où elle a agi | Pire résultat final moyen | Pertes > 6 $ | Capital max moyen ($) | Frais ($) | P&L net ($) | Écart avec R0 (IC 90 %) |
|---|---|---|---|---|---|---|---|
| ne rien faire | 0 | +0.00 | 0 | 0.0 | 0.0 | +0 | +0 [+0 ; +0] |
| vendre une partie | 0 | +0.00 | 0 | 0.0 | 0.0 | +0 | +0 [+0 ; +0] |
| acheter l'opposé | 0 | +0.00 | 0 | 0.0 | 0.0 | +0 | +0 [+0 ; +0] |
| vendre une partie puis acheter l'opposé | 0 | +0.00 | 0 | 0.0 | 0.0 | +0 | +0 [+0 ; +0] |

**Sauvetage — latence et frais (CONFIRMATION (≥ 13.10))**

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

### Protection des gains — CONFIRMATION (≥ 13.10) (674 cycles)

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

**Protection des gains — latence et frais (CONFIRMATION (≥ 13.10))**

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
## 10. Critère de réussite (section 43) sur CONFIRMATION (≥ 13.10)

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
| apprentissage | 4559 | 0.1683 | 0.1844 | 0.1678 | -0.0005 [-0.0019 ; +0.0009] | 0.4981 | 0.4974 | -0.00044 [-0.00118 ; +0.00028] |
| validation | 2301 | 0.1363 | 0.1308 | 0.1364 | +0.0001 [-0.0018 ; +0.0018] | 0.4226 | 0.4237 | -0.00062 [-0.00163 ; +0.00040] |
| CONFIRMATION (≥ 13.10) | 14070 | 0.1658 | 0.1731 | 0.1660 | +0.0003 [-0.0006 ; +0.0010] | 0.4949 | 0.4957 | -0.00013 [-0.00082 ; +0.00057] |

Seuil d'entrée e choisi sur l'apprentissage (T0-50) : **0.05** (e=0.05 → +0 $, e=0.10 → +0 $, e=0.15 → +0 $).

Attribution RS (apprentissage) : aucun signal → T0-50, choc de liquidations → T0-50, range → T7, retournement probable → T7, tendance → T5.


## 3. Tournoi T0–T7 (H1034), latence 164 ms

### apprentissage (sert au choix de e et de RS) (216 cycles)

| Politique | Cycles actifs | P&L net ($) | Par cycle actif | Par $ de capital max | Cycles gagnants | Perte max | Pertes > 6 $ | Drawdown | ES 5 % | Capital max | Achats / ventes | Frais ($) | Coût d'écart ($) | Parts achetées | P&L couvertures ($) | Plancher le plus bas (moy.) | Jackpots conservés | Sans les 5 meilleurs | Écart avec T0-50 ($) | IC 90 % | IC corrigé (13) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T0-50 | 165 | -1144 | -6.93 | -15.3 % | 101 | -50 | 63 | 1433 | -50.0 | 50 | 165 / 0 | 155 | 46 | 10637 | +0 | -34.6 | nan % (0) | -1300 | +0 | — | — |
| T0-10 | 165 | -227 | -1.37 | -13.9 % | 101 | -10 | 63 | 281 | -10.0 | 10 | 165 / 0 | 34 | 10 | 2312 | +0 | -7.5 | nan % (0) | -258 | +918 | [+383 ; +1470] | [+48 ; +1798] |
| T1 | 165 | -227 | -1.37 | -13.9 % | 101 | -10 | 63 | 281 | -10.0 | 10 | 165 / 0 | 34 | 10 | 2312 | +0 | -7.5 | nan % (0) | -258 | +918 | [+384 ; +1468] | [+63 ; +1800] |
| T1v | 165 | -227 | -1.37 | -13.9 % | 101 | -10 | 63 | 281 | -10.0 | 10 | 165 / 0 | 34 | 10 | 2312 | +0 | -7.5 | nan % (0) | -258 | +918 | [+353 ; +1472] | [+30 ; +1814] |
| T2 | 165 | -227 | -1.37 | -13.9 % | 101 | -10 | 63 | 281 | -10.0 | 10 | 165 / 0 | 34 | 10 | 2312 | +0 | -7.5 | nan % (0) | -258 | +918 | [+367 ; +1466] | [+54 ; +1807] |
| T2p | 165 | -227 | -1.37 | -13.9 % | 101 | -10 | 63 | 281 | -10.0 | 10 | 165 / 0 | 34 | 10 | 2312 | +0 | -7.5 | nan % (0) | -258 | +918 | [+372 ; +1468] | [-7 ; +1822] |
| T3 | 165 | -174 | -1.05 | -8.7 % | 99 | -10 | 58 | 225 | -9.9 | 18 | 244 / 0 | 40 | 11 | 2874 | +53 | -7.5 | nan % (0) | -205 | +971 | [+415 ; +1541] | [+87 ; +1892] |
| T4 | 165 | -185 | -1.12 | -11.4 % | 98 | -10 | 59 | 237 | -10.0 | 10 | 165 / 52 | 40 | 10 | 2312 | +41 | -7.5 | nan % (0) | -216 | +959 | [+381 ; +1541] | [+75 ; +1870] |
| LAD | 165 | -190 | -1.15 | -11.2 % | 86 | -10 | 38 | 236 | -10.0 | 20 | 202 / 53 | 45 | 10 | 2607 | +37 | -7.5 | nan % (0) | -221 | +954 | [+359 ; +1567] | [+34 ; +1934] |
| T5 | 165 | -176 | -1.07 | -8.3 % | 139 | -10 | 26 | 188 | -10.0 | 16 | 315 / 0 | 58 | 14 | 4290 | +50 | -7.5 | nan % (0) | -190 | +968 | [+314 ; +1630] | [-98 ; +2061] |
| T6 | 165 | -108 | -0.65 | -8.4 % | 139 | -6 | 0 | 115 | -6.0 | 10 | 310 / 0 | 35 | 9 | 2586 | +30 | -4.6 | nan % (0) | -116 | +1037 | [+349 ; +1722] | [-43 ; +2095] |
| T7 | 165 | -134 | -0.81 | -6.7 % | 86 | -8 | 10 | 139 | -7.2 | 24 | 274 / 103 | 65 | 16 | 3698 | +93 | -7.5 | nan % (0) | -145 | +1010 | [+328 ; +1700] | [-87 ; +2155] |
| T7s | 165 | -89 | -0.54 | -7.5 % | 93 | -6 | 0 | 92 | -5.9 | 10 | 260 / 82 | 38 | 9 | 2198 | +48 | -4.6 | nan % (0) | -97 | +1055 | [+360 ; +1765] | [-26 ; +2177] |
| RS | 165 | -111 | -0.67 | -5.3 % | 98 | -10 | 12 | 120 | -7.7 | 50 | 282 / 84 | 65 | 16 | 3892 | +103 | -7.9 | nan % (0) | -135 | +1033 | [+366 ; +1734] | [-100 ; +2151] |

### validation (109 cycles)

| Politique | Cycles actifs | P&L net ($) | Par cycle actif | Par $ de capital max | Cycles gagnants | Perte max | Pertes > 6 $ | Drawdown | ES 5 % | Capital max | Achats / ventes | Frais ($) | Coût d'écart ($) | Parts achetées | P&L couvertures ($) | Plancher le plus bas (moy.) | Jackpots conservés | Sans les 5 meilleurs | Écart avec T0-50 ($) | IC 90 % | IC corrigé (13) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T0-50 | 82 | +182 | +2.22 | +5.2 % | 60 | -50 | 20 | 258 | -50.0 | 50 | 82 / 0 | 71 | 19 | 4926 | +0 | -32.1 | nan % (0) | +26 | +0 | — | — |
| T0-10 | 82 | +25 | +0.31 | +3.2 % | 60 | -10 | 20 | 55 | -10.0 | 10 | 82 / 0 | 16 | 4 | 1115 | +0 | -7.2 | nan % (0) | -6 | -156 | [-473 ; +198] | [-651 ; +396] |
| T1 | 82 | +25 | +0.31 | +3.2 % | 60 | -10 | 20 | 55 | -10.0 | 10 | 82 / 0 | 16 | 4 | 1115 | +0 | -7.2 | nan % (0) | -6 | -156 | [-476 ; +157] | [-679 ; +398] |
| T1v | 82 | +25 | +0.31 | +3.2 % | 60 | -10 | 20 | 55 | -10.0 | 10 | 82 / 0 | 16 | 4 | 1115 | +0 | -7.2 | nan % (0) | -6 | -156 | [-469 ; +176] | [-639 ; +370] |
| T2 | 82 | +25 | +0.31 | +3.2 % | 60 | -10 | 20 | 55 | -10.0 | 10 | 82 / 0 | 16 | 4 | 1115 | +0 | -7.2 | nan % (0) | -6 | -156 | [-482 ; +181] | [-661 ; +366] |
| T2p | 82 | +25 | +0.31 | +3.2 % | 60 | -10 | 20 | 55 | -10.0 | 10 | 82 / 0 | 16 | 4 | 1115 | +0 | -7.2 | nan % (0) | -6 | -156 | [-478 ; +166] | [-642 ; +382] |
| T3 | 82 | +17 | +0.20 | +1.8 % | 57 | -10 | 17 | 40 | -9.9 | 18 | 113 / 0 | 18 | 5 | 1331 | -9 | -7.2 | nan % (0) | -14 | -165 | [-506 ; +188] | [-675 ; +396] |
| T4 | 82 | +12 | +0.14 | +1.5 % | 58 | -10 | 17 | 45 | -10.0 | 10 | 82 / 22 | 19 | 5 | 1115 | -14 | -7.2 | nan % (0) | -19 | -170 | [-508 ; +171] | [-694 ; +380] |
| LAD | 82 | -7 | -0.08 | -0.9 % | 53 | -10 | 15 | 57 | -10.0 | 19 | 94 / 23 | 20 | 5 | 1207 | -32 | -7.2 | nan % (0) | -37 | -189 | [-521 ; +161] | [-714 ; +415] |
| T5 | 82 | -42 | -0.51 | -4.0 % | 74 | -10 | 8 | 42 | -10.0 | 16 | 165 / 0 | 29 | 7 | 2132 | -67 | -7.2 | nan % (0) | -50 | -223 | [-597 ; +172] | [-847 ; +403] |
| T6 | 82 | -25 | -0.30 | -3.9 % | 74 | -6 | 0 | 25 | -6.0 | 10 | 162 / 0 | 18 | 4 | 1301 | -39 | -4.4 | nan % (0) | -30 | -207 | [-604 ; +192] | [-847 ; +495] |
| T7 | 82 | -28 | -0.34 | -2.9 % | 51 | -7 | 1 | 32 | -5.0 | 16 | 141 / 43 | 31 | 8 | 1846 | -54 | -7.2 | nan % (0) | -36 | -210 | [-593 ; +206] | [-851 ; +465] |
| T7s | 82 | -22 | -0.27 | -3.7 % | 55 | -6 | 0 | 25 | -4.4 | 10 | 139 / 35 | 19 | 5 | 1138 | -37 | -4.4 | nan % (0) | -27 | -204 | [-613 ; +211] | [-823 ; +470] |
| RS | 82 | -11 | -0.13 | -1.0 % | 56 | -7 | 1 | 30 | -5.0 | 50 | 144 / 36 | 31 | 8 | 1936 | -44 | -7.6 | nan % (0) | -28 | -192 | [-583 ; +218] | [-832 ; +485] |

### CONFIRMATION (≥ 13.10) (674 cycles)

| Politique | Cycles actifs | P&L net ($) | Par cycle actif | Par $ de capital max | Cycles gagnants | Perte max | Pertes > 6 $ | Drawdown | ES 5 % | Capital max | Achats / ventes | Frais ($) | Coût d'écart ($) | Parts achetées | P&L couvertures ($) | Plancher le plus bas (moy.) | Jackpots conservés | Sans les 5 meilleurs | Écart avec T0-50 ($) | IC 90 % | IC corrigé (13) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T0-50 | 530 | -2004 | -3.78 | -8.3 % | 352 | -50 | 177 | 2126 | -50.0 | 50 | 530 / 0 | 495 | 138 | 34178 | +0 | -35.8 | nan % (0) | -2165 | +0 | — | — |
| T0-10 | 530 | -397 | -0.75 | -7.6 % | 352 | -10 | 177 | 421 | -10.0 | 10 | 530 / 0 | 107 | 30 | 7376 | +0 | -7.7 | nan % (0) | -429 | +1607 | [+638 ; +2575] | [+51 ; +3184] |
| T1 | 530 | -397 | -0.75 | -7.6 % | 352 | -10 | 177 | 421 | -10.0 | 10 | 530 / 0 | 107 | 30 | 7376 | +0 | -7.7 | nan % (0) | -429 | +1607 | [+659 ; +2583] | [+94 ; +3185] |
| T1v | 530 | -397 | -0.75 | -7.6 % | 352 | -10 | 177 | 421 | -10.0 | 10 | 530 / 0 | 107 | 30 | 7376 | +0 | -7.7 | nan % (0) | -429 | +1607 | [+656 ; +2543] | [+64 ; +3163] |
| T2 | 530 | -397 | -0.75 | -7.6 % | 352 | -10 | 177 | 421 | -10.0 | 10 | 530 / 0 | 107 | 30 | 7376 | +0 | -7.7 | nan % (0) | -429 | +1607 | [+651 ; +2556] | [+114 ; +3154] |
| T2p | 530 | -397 | -0.75 | -7.6 % | 352 | -10 | 177 | 421 | -10.0 | 10 | 530 / 0 | 107 | 30 | 7376 | +0 | -7.7 | nan % (0) | -429 | +1607 | [+652 ; +2543] | [+74 ; +3161] |
| T3 | 530 | -358 | -0.68 | -5.7 % | 342 | -10 | 161 | 385 | -10.0 | 18 | 754 / 0 | 125 | 35 | 8977 | +39 | -7.7 | nan % (0) | -391 | +1646 | [+674 ; +2661] | [+106 ; +3289] |
| T4 | 530 | -364 | -0.69 | -7.0 % | 337 | -10 | 159 | 399 | -10.0 | 10 | 530 / 146 | 124 | 34 | 7376 | +33 | -7.7 | nan % (0) | -397 | +1640 | [+641 ; +2632] | [+46 ; +3298] |
| LAD | 530 | -344 | -0.65 | -6.3 % | 300 | -10 | 104 | 370 | -10.0 | 21 | 643 / 155 | 141 | 38 | 8337 | +53 | -7.7 | nan % (0) | -377 | +1660 | [+616 ; +2687] | [+15 ; +3326] |
| T5 | 530 | -397 | -0.75 | -5.8 % | 466 | -10 | 63 | 414 | -10.0 | 16 | 1031 / 0 | 189 | 49 | 13947 | -0 | -7.7 | nan % (0) | -408 | +1607 | [+441 ; +2762] | [-173 ; +3474] |
| T6 | 530 | -232 | -0.44 | -5.6 % | 467 | -6 | 0 | 242 | -6.0 | 10 | 1016 / 0 | 115 | 29 | 8456 | -1 | -4.7 | nan % (0) | -239 | +1771 | [+595 ; +2958] | [-67 ; +3729] |
| T7 | 530 | -310 | -0.59 | -4.8 % | 274 | -8 | 16 | 313 | -6.5 | 24 | 889 / 317 | 208 | 56 | 11863 | +87 | -7.7 | nan % (0) | -319 | +1693 | [+503 ; +2892] | [-243 ; +3753] |
| T7s | 530 | -196 | -0.37 | -5.1 % | 310 | -6 | 0 | 199 | -5.3 | 10 | 843 / 268 | 123 | 34 | 7126 | +35 | -4.7 | nan % (0) | -202 | +1808 | [+603 ; +2983] | [-137 ; +3753] |
| RS | 530 | -529 | -1.00 | -7.7 % | 299 | -50 | 25 | 532 | -14.9 | 50 | 905 / 274 | 212 | 55 | 12596 | +53 | -8.3 | nan % (0) | -601 | +1474 | [+306 ; +2657] | [-406 ; +3422] |

## 4. Les trois simulations prioritaires

### Simulation A — entrées progressives — validation (109 cycles)

| Politique | Cycles actifs | P&L net ($) | Par cycle actif | Par $ de capital max | Cycles gagnants | Perte max | Pertes > 6 $ | Drawdown | ES 5 % | Capital max | Achats / ventes | Frais ($) | Coût d'écart ($) | Parts achetées | P&L couvertures ($) | Plancher le plus bas (moy.) | Jackpots conservés | Sans les 5 meilleurs | Écart avec T0-50 ($) | IC 90 % | IC corrigé (13) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T0-50 | 82 | +182 | +2.22 | +5.2 % | 60 | -50 | 20 | 258 | -50.0 | 50 | 82 / 0 | 71 | 19 | 4926 | +0 | -32.1 | nan % (0) | +26 | +0 | — | — |
| T0-10 | 82 | +25 | +0.31 | +3.2 % | 60 | -10 | 20 | 55 | -10.0 | 10 | 82 / 0 | 16 | 4 | 1115 | +0 | -7.2 | nan % (0) | -6 | -156 | [-482 ; +175] | [-660 ; +396] |
| T1 | 82 | +25 | +0.31 | +3.2 % | 60 | -10 | 20 | 55 | -10.0 | 10 | 82 / 0 | 16 | 4 | 1115 | +0 | -7.2 | nan % (0) | -6 | -156 | [-478 ; +175] | [-636 ; +397] |
| T1v | 82 | +25 | +0.31 | +3.2 % | 60 | -10 | 20 | 55 | -10.0 | 10 | 82 / 0 | 16 | 4 | 1115 | +0 | -7.2 | nan % (0) | -6 | -156 | [-468 ; +182] | [-657 ; +383] |
| T2 | 82 | +25 | +0.31 | +3.2 % | 60 | -10 | 20 | 55 | -10.0 | 10 | 82 / 0 | 16 | 4 | 1115 | +0 | -7.2 | nan % (0) | -6 | -156 | [-486 ; +182] | [-646 ; +371] |
| T2p | 82 | +25 | +0.31 | +3.2 % | 60 | -10 | 20 | 55 | -10.0 | 10 | 82 / 0 | 16 | 4 | 1115 | +0 | -7.2 | nan % (0) | -6 | -156 | [-476 ; +182] | [-651 ; +392] |

### Simulation B — changement de camp — validation (109 cycles)

| Politique | Cycles actifs | P&L net ($) | Par cycle actif | Par $ de capital max | Cycles gagnants | Perte max | Pertes > 6 $ | Drawdown | ES 5 % | Capital max | Achats / ventes | Frais ($) | Coût d'écart ($) | Parts achetées | P&L couvertures ($) | Plancher le plus bas (moy.) | Jackpots conservés | Sans les 5 meilleurs | Écart avec T0-50 ($) | IC 90 % | IC corrigé (13) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T0-50 | 82 | +182 | +2.22 | +5.2 % | 60 | -50 | 20 | 258 | -50.0 | 50 | 82 / 0 | 71 | 19 | 4926 | +0 | -32.1 | nan % (0) | +26 | +0 | — | — |
| T1 | 82 | +25 | +0.31 | +3.2 % | 60 | -10 | 20 | 55 | -10.0 | 10 | 82 / 0 | 16 | 4 | 1115 | +0 | -7.2 | nan % (0) | -6 | -156 | [-470 ; +175] | [-653 ; +366] |
| T2 | 82 | +25 | +0.31 | +3.2 % | 60 | -10 | 20 | 55 | -10.0 | 10 | 82 / 0 | 16 | 4 | 1115 | +0 | -7.2 | nan % (0) | -6 | -156 | [-477 ; +175] | [-681 ; +363] |
| T4 | 82 | +12 | +0.14 | +1.5 % | 58 | -10 | 17 | 45 | -10.0 | 10 | 82 / 22 | 19 | 5 | 1115 | -14 | -7.2 | nan % (0) | -19 | -170 | [-505 ; +165] | [-690 ; +407] |
| LAD | 82 | -7 | -0.08 | -0.9 % | 53 | -10 | 15 | 57 | -10.0 | 19 | 94 / 23 | 20 | 5 | 1207 | -32 | -7.2 | nan % (0) | -37 | -189 | [-539 ; +160] | [-710 ; +394] |
| T5 | 82 | -42 | -0.51 | -4.0 % | 74 | -10 | 8 | 42 | -10.0 | 16 | 165 / 0 | 29 | 7 | 2132 | -67 | -7.2 | nan % (0) | -50 | -223 | [-597 ; +159] | [-811 ; +412] |
| T7 | 82 | -28 | -0.34 | -2.9 % | 51 | -7 | 1 | 32 | -5.0 | 16 | 141 / 43 | 31 | 8 | 1846 | -54 | -7.2 | nan % (0) | -36 | -210 | [-599 ; +201] | [-848 ; +495] |

### Simulation C — protection du capital (même plafond de 50 $) — validation (109 cycles)

| Politique | Cycles actifs | P&L net ($) | Par cycle actif | Par $ de capital max | Cycles gagnants | Perte max | Pertes > 6 $ | Drawdown | ES 5 % | Capital max | Achats / ventes | Frais ($) | Coût d'écart ($) | Parts achetées | P&L couvertures ($) | Plancher le plus bas (moy.) | Jackpots conservés | Sans les 5 meilleurs | Écart avec T0-50 ($) | IC 90 % | IC corrigé (13) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T0-50 | 82 | +182 | +2.22 | +5.2 % | 60 | -50 | 20 | 258 | -50.0 | 50 | 82 / 0 | 71 | 19 | 4926 | +0 | -32.1 | nan % (0) | +26 | +0 | — | — |
| T7 | 82 | -28 | -0.34 | -2.9 % | 51 | -7 | 1 | 32 | -5.0 | 16 | 141 / 43 | 31 | 8 | 1846 | -54 | -7.2 | nan % (0) | -36 | -210 | [-606 ; +205] | [-857 ; +454] |
| T7s | 82 | -22 | -0.27 | -3.7 % | 55 | -6 | 0 | 25 | -4.4 | 10 | 139 / 35 | 19 | 5 | 1138 | -37 | -4.4 | nan % (0) | -27 | -204 | [-601 ; +198] | [-838 ; +489] |
| T5 | 82 | -42 | -0.51 | -4.0 % | 74 | -10 | 8 | 42 | -10.0 | 16 | 165 / 0 | 29 | 7 | 2132 | -67 | -7.2 | nan % (0) | -50 | -223 | [-607 ; +168] | [-820 ; +457] |
| T6 | 82 | -25 | -0.30 | -3.9 % | 74 | -6 | 0 | 25 | -6.0 | 10 | 162 / 0 | 18 | 4 | 1301 | -39 | -4.4 | nan % (0) | -30 | -207 | [-604 ; +177] | [-804 ; +439] |

**H1033 — coût économique de la protection stricte (validation)** : T7 − T7s = -6 $ [-13 ; +1] ; pertes > 6 $ : T7 1, T7s 0 ; T5 − T6 = -17 $ (pertes > 6 $ : T5 8, T6 0).

### Simulation A — entrées progressives — CONFIRMATION (≥ 13.10) (674 cycles)

| Politique | Cycles actifs | P&L net ($) | Par cycle actif | Par $ de capital max | Cycles gagnants | Perte max | Pertes > 6 $ | Drawdown | ES 5 % | Capital max | Achats / ventes | Frais ($) | Coût d'écart ($) | Parts achetées | P&L couvertures ($) | Plancher le plus bas (moy.) | Jackpots conservés | Sans les 5 meilleurs | Écart avec T0-50 ($) | IC 90 % | IC corrigé (13) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T0-50 | 530 | -2004 | -3.78 | -8.3 % | 352 | -50 | 177 | 2126 | -50.0 | 50 | 530 / 0 | 495 | 138 | 34178 | +0 | -35.8 | nan % (0) | -2165 | +0 | — | — |
| T0-10 | 530 | -397 | -0.75 | -7.6 % | 352 | -10 | 177 | 421 | -10.0 | 10 | 530 / 0 | 107 | 30 | 7376 | +0 | -7.7 | nan % (0) | -429 | +1607 | [+652 ; +2582] | [+55 ; +3115] |
| T1 | 530 | -397 | -0.75 | -7.6 % | 352 | -10 | 177 | 421 | -10.0 | 10 | 530 / 0 | 107 | 30 | 7376 | +0 | -7.7 | nan % (0) | -429 | +1607 | [+635 ; +2550] | [+10 ; +3176] |
| T1v | 530 | -397 | -0.75 | -7.6 % | 352 | -10 | 177 | 421 | -10.0 | 10 | 530 / 0 | 107 | 30 | 7376 | +0 | -7.7 | nan % (0) | -429 | +1607 | [+635 ; +2546] | [+128 ; +3161] |
| T2 | 530 | -397 | -0.75 | -7.6 % | 352 | -10 | 177 | 421 | -10.0 | 10 | 530 / 0 | 107 | 30 | 7376 | +0 | -7.7 | nan % (0) | -429 | +1607 | [+620 ; +2569] | [+66 ; +3048] |
| T2p | 530 | -397 | -0.75 | -7.6 % | 352 | -10 | 177 | 421 | -10.0 | 10 | 530 / 0 | 107 | 30 | 7376 | +0 | -7.7 | nan % (0) | -429 | +1607 | [+651 ; +2545] | [+104 ; +3179] |

### Simulation B — changement de camp — CONFIRMATION (≥ 13.10) (674 cycles)

| Politique | Cycles actifs | P&L net ($) | Par cycle actif | Par $ de capital max | Cycles gagnants | Perte max | Pertes > 6 $ | Drawdown | ES 5 % | Capital max | Achats / ventes | Frais ($) | Coût d'écart ($) | Parts achetées | P&L couvertures ($) | Plancher le plus bas (moy.) | Jackpots conservés | Sans les 5 meilleurs | Écart avec T0-50 ($) | IC 90 % | IC corrigé (13) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T0-50 | 530 | -2004 | -3.78 | -8.3 % | 352 | -50 | 177 | 2126 | -50.0 | 50 | 530 / 0 | 495 | 138 | 34178 | +0 | -35.8 | nan % (0) | -2165 | +0 | — | — |
| T1 | 530 | -397 | -0.75 | -7.6 % | 352 | -10 | 177 | 421 | -10.0 | 10 | 530 / 0 | 107 | 30 | 7376 | +0 | -7.7 | nan % (0) | -429 | +1607 | [+668 ; +2581] | [+181 ; +3115] |
| T2 | 530 | -397 | -0.75 | -7.6 % | 352 | -10 | 177 | 421 | -10.0 | 10 | 530 / 0 | 107 | 30 | 7376 | +0 | -7.7 | nan % (0) | -429 | +1607 | [+643 ; +2552] | [+91 ; +3090] |
| T4 | 530 | -364 | -0.69 | -7.0 % | 337 | -10 | 159 | 399 | -10.0 | 10 | 530 / 146 | 124 | 34 | 7376 | +33 | -7.7 | nan % (0) | -397 | +1640 | [+651 ; +2637] | [+18 ; +3292] |
| LAD | 530 | -344 | -0.65 | -6.3 % | 300 | -10 | 104 | 370 | -10.0 | 21 | 643 / 155 | 141 | 38 | 8337 | +53 | -7.7 | nan % (0) | -377 | +1660 | [+619 ; +2714] | [-11 ; +3427] |
| T5 | 530 | -397 | -0.75 | -5.8 % | 466 | -10 | 63 | 414 | -10.0 | 16 | 1031 / 0 | 189 | 49 | 13947 | -0 | -7.7 | nan % (0) | -408 | +1607 | [+454 ; +2772] | [-226 ; +3532] |
| T7 | 530 | -310 | -0.59 | -4.8 % | 274 | -8 | 16 | 313 | -6.5 | 24 | 889 / 317 | 208 | 56 | 11863 | +87 | -7.7 | nan % (0) | -319 | +1693 | [+531 ; +2890] | [-170 ; +3621] |

### Simulation C — protection du capital (même plafond de 50 $) — CONFIRMATION (≥ 13.10) (674 cycles)

| Politique | Cycles actifs | P&L net ($) | Par cycle actif | Par $ de capital max | Cycles gagnants | Perte max | Pertes > 6 $ | Drawdown | ES 5 % | Capital max | Achats / ventes | Frais ($) | Coût d'écart ($) | Parts achetées | P&L couvertures ($) | Plancher le plus bas (moy.) | Jackpots conservés | Sans les 5 meilleurs | Écart avec T0-50 ($) | IC 90 % | IC corrigé (13) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T0-50 | 530 | -2004 | -3.78 | -8.3 % | 352 | -50 | 177 | 2126 | -50.0 | 50 | 530 / 0 | 495 | 138 | 34178 | +0 | -35.8 | nan % (0) | -2165 | +0 | — | — |
| T7 | 530 | -310 | -0.59 | -4.8 % | 274 | -8 | 16 | 313 | -6.5 | 24 | 889 / 317 | 208 | 56 | 11863 | +87 | -7.7 | nan % (0) | -319 | +1693 | [+567 ; +2870] | [-226 ; +3583] |
| T7s | 530 | -196 | -0.37 | -5.1 % | 310 | -6 | 0 | 199 | -5.3 | 10 | 843 / 268 | 123 | 34 | 7126 | +35 | -4.7 | nan % (0) | -202 | +1808 | [+563 ; +3006] | [-211 ; +3731] |
| T5 | 530 | -397 | -0.75 | -5.8 % | 466 | -10 | 63 | 414 | -10.0 | 16 | 1031 / 0 | 189 | 49 | 13947 | -0 | -7.7 | nan % (0) | -408 | +1607 | [+466 ; +2751] | [-184 ; +3479] |
| T6 | 530 | -232 | -0.44 | -5.6 % | 467 | -6 | 0 | 242 | -6.0 | 10 | 1016 / 0 | 115 | 29 | 8456 | -1 | -4.7 | nan % (0) | -239 | +1771 | [+622 ; +2986] | [-82 ; +3775] |

**H1033 — coût économique de la protection stricte (CONFIRMATION (≥ 13.10))** : T7 − T7s = -114 $ [-143 ; -87] ; pertes > 6 $ : T7 16, T7s 0 ; T5 − T6 = -165 $ (pertes > 6 $ : T5 63, T6 0).

## 5. Sensibilité à la latence et aux frais (CONFIRMATION (≥ 13.10))

| Politique | 164 ms | 200 ms | 250 ms | 500 ms | frais×0,5 | frais×1,5 |
|---|---|---|---|---|---|---|
| T0-50 | -2004 | -1762 | -1650 | -1286 | -1774 | -2229 |
| T0-10 | -397 | -359 | -336 | -241 | -347 | -445 |
| T1 | -397 | -359 | -336 | -241 | -347 | -445 |
| T1v | -397 | -359 | -336 | -241 | -347 | -445 |
| T2 | -397 | -359 | -336 | -241 | -347 | -445 |
| T2p | -397 | -359 | -336 | -241 | -347 | -445 |
| T3 | -358 | -324 | -301 | -198 | -281 | -413 |
| T4 | -364 | -336 | -317 | -192 | -322 | -437 |
| LAD | -344 | -305 | -277 | -146 | -292 | -412 |
| T5 | -397 | -397 | -412 | -392 | -282 | -522 |
| T6 | -232 | -231 | -245 | -238 | -166 | -310 |
| T7 | -310 | -314 | -324 | -306 | -201 | -438 |
| T7s | -196 | -194 | -207 | -196 | -125 | -270 |

## 6. H1018 — Scénarios défavorables (164 ms)

| Politique | Normal | acheteurs disparus | couverture + 2 c | fills ÷ 2 | vente de protection impossible | Pertes > 6 $ (normal → pire scénario) | Perte max (normal → pire) |
|---|---|---|---|---|---|---|---|
| T0-50 | -2004 | -2004 | -2004 | -1807 | -2004 | 177 → 177 | -50 → -50 |
| T1 | -397 | -397 | -397 | -415 | -397 | 177 → 177 | -10 → -10 |
| T3 | -358 | -358 | -390 | -371 | -358 | 161 → 175 | -10 → -10 |
| T4 | -364 | -397 | -364 | -383 | -397 | 159 → 177 | -10 → -10 |
| LAD | -344 | -371 | -363 | -349 | -371 | 104 → 115 | -10 → -10 |
| T5 | -397 | -397 | -516 | -400 | -397 | 63 → 63 | -10 → -10 |
| T7 | -310 | -354 | -391 | -316 | -354 | 16 → 26 | -8 → -9 |
| T7s | -196 | -232 | -245 | -200 | -232 | 0 → 0 | -6 → -6 |

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

**H1013 — P&L de chaque tranche jusqu'au règlement (CONFIRMATION (≥ 13.10))**

| Politique | Tranche | Nombre | Coût ($) | P&L ($) | P&L / $ |
|---|---|---|---|---|---|
| T1 | 1 | 530 | 5195 | -397 | -7.6 % |
| T1v | 1 | 530 | 5195 | -397 | -7.6 % |
| T2 | 1 | 530 | 5195 | -397 | -7.6 % |
| T2p | 1 | 530 | 5195 | -397 | -7.6 % |

**P&L des transactions de protection par type (CONFIRMATION (≥ 13.10))** (valeur au règlement − coût)

| Politique | Couverture | Protection (vente) | Inversion | Verrou | Sortie |
|---|---|---|---|---|---|
| T3 | +39 | +0 | +0 | +0 | +0 |
| T4 | +0 | +33 | +0 | +0 | +0 |
| LAD | +23 | +30 | +0 | +0 | +0 |
| T5 | +0 | +0 | +0 | -0 | +0 |
| T6 | +0 | +0 | +0 | -1 | +0 |
| T7 | +0 | +23 | +0 | -24 | +87 |
| T7s | +0 | +0 | +0 | -14 | +49 |

**H1025 — coût par dollar de perte maximale évitée (CONFIRMATION (≥ 13.10), contre T1)**

| Politique | P&L − T1 ($) | Plancher moyen le plus bas − T1 ($) | Coût par $ évité |
|---|---|---|---|
| T3 | +39 | +0.00 | +nan |
| T4 | +33 | +0.00 | +nan |
| LAD | +53 | +0.00 | +nan |
| T7 | +87 | +0.00 | +nan |

**H1020 — changements de camp (CONFIRMATION (≥ 13.10))** : aucun.

## 8. H1017 — Régimes au signal d'entrée

| validation : régime | Cycles | T0-50 | T1 | T3 | T5 | T7 | RS |
|---|---|---|---|---|---|---|---|
| aucun signal | 17 | +0 | +0 | +0 | +0 | +0 | +0 |
| choc de liquidations | 2 | +10 | +2 | +2 | +0 | -1 | +10 |
| range | 66 | -13 | -22 | -29 | -39 | -27 | -27 |
| retournement probable | 8 | +14 | +4 | +4 | -8 | +1 | +1 |
| tendance | 16 | +171 | +42 | +40 | +5 | -1 | +5 |

| CONFIRMATION (≥ 13.10) : régime | Cycles | T0-50 | T1 | T3 | T5 | T7 | RS |
|---|---|---|---|---|---|---|---|
| aucun signal | 91 | +0 | +0 | +0 | +0 | +0 | +0 |
| choc de liquidations | 11 | -230 | -45 | -31 | -7 | -3 | -230 |
| range | 438 | -1134 | -223 | -221 | -314 | -253 | -253 |
| retournement probable | 58 | -583 | -121 | -93 | -62 | -32 | -32 |
| tendance | 76 | -56 | -8 | -13 | -14 | -22 | -14 |

## 9. H1036–H1040 — Sauvetage de la première position (entrée 10 $, mêmes cycles)

R0 conserver ; R1 vendre toute la position à −0,15 ; R2 couverture préventive (−0,05 et cerveau A contre ≥ 0,60) ; R3 couverture complète à −0,15 ; R4 couverture tardive (p ≤ 0,25) ; R5 vente de 50 % puis couverture du reste à −0,15 ; R6 inversion complète à −0,15 (vente de tout + 10 $ de l'opposé) ; R7 adaptatif (H1039 : probabilité de redevenir gagnante, apprise sur l'apprentissage ; vend si acheteur net > probabilité + 0,01, couvre si (1 − probabilité) − coût opposé > 0,01, sinon conserve). Couverture = achat de l'opposé pour toutes les parts non appariées. Les noms R0–R7 sont propres à cette étude (aucun lien avec le fantôme R4).

Modèle de récupération H1039 : 2959 états détériorés d'apprentissage (taux de récupération 36.3 %).

### Tournoi de sauvetage R0–R7 — validation (109 cycles)

| Politique | Cycles actifs | P&L net ($) | Par cycle actif | Par $ de capital max | Cycles gagnants | Perte max | Pertes > 6 $ | Drawdown | ES 5 % | Capital max | Achats / ventes | Frais ($) | Coût d'écart ($) | Parts achetées | P&L couvertures ($) | Plancher le plus bas (moy.) | Jackpots conservés | Sans les 5 meilleurs | Écart avec R0 ($) | IC 90 % | IC corrigé (7) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| R0 | 82 | +25 | +0.31 | +3.2 % | 60 | -10 | 20 | 55 | -10.0 | 10 | 82 / 0 | 16 | 4 | 1115 | +0 | -7.2 | nan % (0) | -6 | +0 | — | — |
| R1 | 82 | -27 | -0.33 | -3.4 % | 34 | -7 | 2 | 42 | -5.3 | 10 | 82 / 48 | 27 | 3 | 1115 | -52 | -7.2 | nan % (0) | -57 | -52 | [-129 ; +25] | [-171 ; +61] |
| R2 | 82 | -51 | -0.62 | -4.4 % | 23 | -8 | 2 | 54 | -5.2 | 22 | 141 / 0 | 29 | 7 | 1912 | -76 | -7.2 | nan % (0) | -80 | -76 | [-161 ; +10] | [-206 ; +51] |
| R3 | 82 | -28 | -0.35 | -2.5 % | 34 | -7 | 2 | 43 | -5.3 | 22 | 130 / 0 | 27 | 2 | 1786 | -54 | -7.2 | nan % (0) | -59 | -54 | [-134 ; +25] | [-169 ; +66] |
| R4 | 82 | +48 | +0.59 | +4.5 % | 57 | -9 | 23 | 38 | -8.2 | 25 | 107 / 0 | 20 | 6 | 1454 | +23 | -7.2 | nan % (0) | +17 | +23 | [-15 ; +56] | [-33 ; +70] |
| R5 | 82 | -27 | -0.33 | -3.3 % | 34 | -7 | 2 | 42 | -5.2 | 15 | 130 / 48 | 27 | 3 | 1451 | -53 | -7.2 | nan % (0) | -58 | -53 | [-132 ; +26] | [-167 ; +61] |
| R6 | 82 | -87 | -1.06 | -9.0 % | 54 | -15 | 26 | 179 | -14.1 | 17 | 130 / 48 | 43 | 1 | 2071 | -112 | -8.8 | nan % (0) | -156 | -112 | [-306 ; +78] | [-400 ; +172] |
| R7 | 82 | -27 | -0.33 | -2.8 % | 34 | -7 | 2 | 42 | -5.2 | 20 | 103 / 27 | 27 | 3 | 1416 | -52 | -7.2 | nan % (0) | -57 | -52 | [-129 ; +26] | [-172 ; +59] |

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
| vendre une partie | 46 | -5.57 | 2 | 7.2 | 22.7 | -7 | -32 [-79 ; +16] |
| acheter l'opposé | 46 | -5.55 | 3 | 9.3 | 22.9 | -7 | -33 [-83 ; +16] |
| vendre une partie puis acheter l'opposé | 46 | -5.63 | 3 | 7.5 | 22.8 | -5 | -30 [-80 ; +17] |

### Tournoi de sauvetage R0–R7 — CONFIRMATION (≥ 13.10) (674 cycles)

| Politique | Cycles actifs | P&L net ($) | Par cycle actif | Par $ de capital max | Cycles gagnants | Perte max | Pertes > 6 $ | Drawdown | ES 5 % | Capital max | Achats / ventes | Frais ($) | Coût d'écart ($) | Parts achetées | P&L couvertures ($) | Plancher le plus bas (moy.) | Jackpots conservés | Sans les 5 meilleurs | Écart avec R0 ($) | IC 90 % | IC corrigé (7) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| R0 | 530 | -397 | -0.75 | -7.6 % | 352 | -10 | 177 | 421 | -10.0 | 10 | 530 / 0 | 107 | 30 | 7376 | +0 | -7.7 | nan % (0) | -429 | +0 | — | — |
| R1 | 530 | -338 | -0.64 | -6.5 % | 210 | -9 | 14 | 367 | -6.1 | 10 | 530 / 323 | 182 | 47 | 7376 | +58 | -7.7 | nan % (0) | -371 | +58 | [-147 ; +258] | [-247 ; +369] |
| R2 | 530 | -251 | -0.47 | -3.3 % | 161 | -10 | 14 | 273 | -6.1 | 24 | 908 / 0 | 191 | 47 | 12546 | +145 | -7.7 | nan % (0) | -284 | +145 | [-67 ; +362] | [-179 ; +481] |
| R3 | 530 | -337 | -0.64 | -4.4 % | 210 | -9 | 14 | 365 | -6.1 | 23 | 853 / 0 | 182 | 46 | 11871 | +60 | -7.7 | nan % (0) | -369 | +60 | [-144 ; +266] | [-235 ; +376] |
| R4 | 530 | -476 | -0.90 | -6.1 % | 304 | -10 | 219 | 503 | -8.6 | 24 | 755 / 0 | 142 | 39 | 10523 | -79 | -7.7 | nan % (0) | -508 | -79 | [-224 ; +57] | [-296 ; +118] |
| R5 | 530 | -342 | -0.64 | -6.2 % | 207 | -9 | 10 | 366 | -5.7 | 15 | 853 / 323 | 183 | 47 | 9657 | +55 | -7.7 | nan % (0) | -374 | +55 | [-150 ; +263] | [-251 ; +355] |
| R6 | 530 | -225 | -0.43 | -3.6 % | 367 | -18 | 143 | 431 | -14.7 | 19 | 853 / 323 | 283 | 68 | 13400 | +171 | -9.4 | nan % (0) | -312 | +171 | [-310 ; +647] | [-573 ; +885] |
| R7 | 530 | -328 | -0.62 | -5.4 % | 214 | -10 | 17 | 360 | -6.8 | 22 | 648 / 194 | 180 | 45 | 9038 | +69 | -7.7 | nan % (0) | -360 | +69 | [-131 ; +263] | [-229 ; +375] |

**Niveaux de détérioration (H1036, descriptif, aucun choix) — CONFIRMATION (≥ 13.10)** : R1-10 +114 $ ; R1 +58 $ ; R1-20 +19 $ ; R1-30 -21 $ ; R3-10 +117 $ ; R3 +60 $ ; R3-20 +18 $ ; R3-30 -21 $ (écart avec R0).

**Test décisif (section 9) — CONFIRMATION (≥ 13.10)** : 359 positions devenues défavorables (p ≤ entrée − 0,15) ; ramené à 100.

| Politique | Perdantes sans intervention | Gagnantes sans intervention | Sauvetages (perte réduite) | Coût moyen d'un sauvetage réussi ($ gagnés) | Couvertures inutiles (gagnantes abîmées) | Coût des couvertures inutiles ($) | Perte moyenne R0 → politique | Perte max R0 → politique | P&L net − R0 (défavorables) | P&L net − R0 (tous) |
|---|---|---|---|---|---|---|---|---|---|---|
| R1 | 50 | 40 | 50 | +6.23 | 40 | 1051 | -9.94 → -3.55 | -10.0 → -8.6 | +58 | +58 |
| R2 | 50 | 40 | 49 | +7.27 | 38 | 819 | -9.94 → -2.45 | -10.0 → -10.0 | +468 | +145 |
| R3 | 50 | 40 | 50 | +6.27 | 40 | 1056 | -9.94 → -3.54 | -10.0 → -8.6 | +60 | +60 |
| R4 | 50 | 40 | 49 | +2.58 | 13 | 536 | -9.94 → -7.27 | -10.0 → -10.0 | -79 | -79 |
| R5 | 50 | 40 | 50 | +6.33 | 40 | 1071 | -9.94 → -3.51 | -10.0 → -8.5 | +55 | +55 |
| R6 | 50 | 40 | 50 | +14.78 | 40 | 2459 | -9.94 → -11.92 | -10.0 → -17.6 | +171 | +171 |
| R7 | 50 | 40 | 48 | +6.28 | 39 | 1012 | -9.94 → -3.64 | -10.0 → -10.0 | +69 | +69 |
| Rv | 50 | 40 | 49 | +3.91 | 40 | 673 | -9.94 → -4.27 | -10.0 → -8.6 | +19 | +19 |
| Ra | 50 | 40 | 49 | +3.97 | 40 | 688 | -9.94 → -4.27 | -10.0 → -17.8 | +14 | +14 |
| Rm | 50 | 40 | 49 | +3.99 | 40 | 691 | -9.94 → -4.22 | -10.0 → -15.1 | +16 | +16 |

**H1038 — vendre ou acheter l'opposé, à risque comparable (cible : pire résultat ≥ −6 $, dès p ≤ entrée − 0,15) — CONFIRMATION (≥ 13.10)**

| Réaction | Cycles où elle a agi | Pire résultat final moyen | Pertes > 6 $ | Capital max moyen ($) | Frais ($) | P&L net ($) | Écart avec R0 (IC 90 %) |
|---|---|---|---|---|---|---|---|
| ne rien faire | 0 | -7.71 | 177 | 7.7 | 107.0 | -397 | +0 [+0 ; +0] |
| vendre une partie | 319 | -5.87 | 14 | 7.7 | 154.2 | -378 | +19 [-111 ; +151] |
| acheter l'opposé | 319 | -5.93 | 29 | 10.2 | 155.0 | -383 | +14 [-125 ; +149] |
| vendre une partie puis acheter l'opposé | 319 | -5.92 | 41 | 8.1 | 155.3 | -381 | +16 [-125 ; +155] |

**Sauvetage — latence et frais (CONFIRMATION (≥ 13.10))**

| Politique | 164 ms | 200 ms | 250 ms | 500 ms | frais×0,5 | frais×1,5 |
|---|---|---|---|---|---|---|
| R0 | -397 | -359 | -336 | -241 | -347 | -445 |
| R1 | -338 | -305 | -305 | -278 | -250 | -425 |
| R2 | -251 | -257 | -260 | -238 | -158 | -343 |
| R3 | -337 | -302 | -302 | -280 | -248 | -423 |
| R4 | -476 | -466 | -432 | -343 | -410 | -540 |
| R5 | -342 | -308 | -307 | -280 | -253 | -429 |
| R6 | -225 | -194 | -210 | -291 | -83 | -364 |
| R7 | -328 | -306 | -307 | -281 | -244 | -417 |
| Rv | -378 | -348 | -342 | -285 | -305 | -450 |
| Ra | -383 | -356 | -351 | -289 | -309 | -457 |
| Rm | -381 | -354 | -350 | -290 | -307 | -455 |

**Critère (sauvetage, contre R0)** : une politique n'est retenue que si l'IC corrigé (7) de l'écart avec R0 est > 0 sur le test, la validation va dans le même sens, l'écart reste > 0 à 500 ms et sans les 5 meilleurs cycles.

| Politique | IC corrigé > 0 | Validation même sens | > 0 à 500 ms | > 0 sans les 5 meilleurs | Verdict |
|---|---|---|---|---|---|
| R1 | non | non | non | oui | non démontrée |
| R2 | non | non | oui | oui | non démontrée |
| R3 | non | non | non | oui | non démontrée |
| R4 | non | oui | non | non | non démontrée |
| R5 | non | non | non | oui | non démontrée |
| R6 | non | non | non | oui | non démontrée |
| R7 | non | non | non | oui | non démontrée |
## 11. H1041–H1046 — Protection des positions gagnantes (entrée 10 $, mêmes cycles)

P0 conserver ; P-TP100 / P-TP200 tout vendre si acheteur net ≥ 2× / 3× le prix payé ; P-VP vendre 50 % si acheteur net ≥ prix payé + 0,20 ; P-TR10…40 trailing : tout vendre quand le profit liquidable (acheteurs affichés, frais, profondeur) retombe de 10/20/30/40 % sous son maximum (maximum ≥ 2 $) ; P-TF trailing fondamental : p de règlement recalibrée ≤ son maximum − 0,15 ET cerveau A contre ≥ 0,55 (momentum, OFI, liquidations, Chainlink ; ETH/SOL non disponibles avant le 12.10) ; P-L0 (free-roll : mise récupérée), P-L5, P-L10, P-L20, P-Lm6 (5 CHF) : vente de la quantité minimale qui verrouille ce résultat dans le cas perdant, dès que la profondeur le permet ; à retracement de 30 % : P-HA vente partielle, P-HB achat de l'opposé, P-HC moitié-moitié (verrou 0 $) ; P-PF cliquet du portefeuille : à 30 % de retracement, plancher contractuel porté à 50 % du gain liquidable maximal par le moyen le moins cher. Un gain n'est « verrouillé » que s'il est garanti par l'inventaire exécuté.

### Protection des gains — validation (109 cycles)

| Politique | Cycles actifs | P&L net ($) | Par cycle actif | Par $ de capital max | Cycles gagnants | Perte max | Pertes > 6 $ | Drawdown | ES 5 % | Capital max | Achats / ventes | Frais ($) | Coût d'écart ($) | Parts achetées | P&L couvertures ($) | Plancher le plus bas (moy.) | Jackpots conservés | Sans les 5 meilleurs | Écart avec P0 ($) | IC 90 % | IC corrigé (17) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P0 | 82 | +25 | +0.31 | +3.2 % | 60 | -10 | 20 | 55 | -10.0 | 10 | 82 / 0 | 16 | 4 | 1115 | +0 | -7.2 | nan % (0) | -6 | +0 | — | — |
| P-TP100 | 82 | +25 | +0.31 | +3.2 % | 60 | -10 | 20 | 55 | -10.0 | 10 | 82 / 0 | 16 | 4 | 1115 | +0 | -7.2 | nan % (0) | -6 | +0 | [+0 ; +0] | [+0 ; +0] |
| P-TP200 | 82 | +25 | +0.31 | +3.2 % | 60 | -10 | 20 | 55 | -10.0 | 10 | 82 / 0 | 16 | 4 | 1115 | +0 | -7.2 | nan % (0) | -6 | +0 | [+0 ; +0] | [+0 ; +0] |
| P-VP | 82 | +1 | +0.01 | +0.2 % | 60 | -10 | 19 | 64 | -10.0 | 10 | 82 / 45 | 18 | 5 | 1115 | +0 | -7.2 | nan % (0) | -23 | -24 | [-37 ; -8] | [-44 ; +4] |
| P-TR10 | 82 | -10 | -0.12 | -1.2 % | 64 | -10 | 15 | 70 | -10.0 | 10 | 82 / 41 | 22 | 7 | 1115 | +0 | -7.2 | nan % (0) | -33 | -35 | [-82 ; +15] | [-107 ; +51] |
| P-TR20 | 82 | -6 | -0.08 | -0.8 % | 63 | -10 | 15 | 71 | -10.0 | 10 | 82 / 33 | 21 | 5 | 1115 | +0 | -7.2 | nan % (0) | -33 | -32 | [-82 ; +23] | [-109 ; +69] |
| P-TR30 | 82 | +2 | +0.03 | +0.3 % | 63 | -10 | 15 | 69 | -10.0 | 10 | 82 / 28 | 21 | 4 | 1115 | +0 | -7.2 | nan % (0) | -27 | -23 | [-72 ; +30] | [-103 ; +65] |
| P-TR40 | 82 | -1 | -0.01 | -0.1 % | 61 | -10 | 15 | 67 | -10.0 | 10 | 82 / 24 | 21 | 3 | 1115 | +0 | -7.2 | nan % (0) | -32 | -26 | [-77 ; +26] | [-104 ; +68] |
| P-TF | 82 | +2 | +0.02 | +0.2 % | 53 | -10 | 16 | 61 | -10.0 | 10 | 82 / 18 | 20 | 4 | 1115 | +0 | -7.2 | nan % (0) | -29 | -23 | [-67 ; +23] | [-101 ; +62] |
| P-L0 | 82 | -20 | -0.25 | -2.6 % | 68 | -10 | 5 | 22 | -8.3 | 10 | 82 / 82 | 29 | 7 | 1115 | +0 | -7.2 | nan % (0) | -29 | -46 | [-122 ; +36] | [-176 ; +88] |
| P-L5 | 82 | +30 | +0.37 | +3.8 % | 61 | -10 | 19 | 57 | -10.0 | 10 | 82 / 14 | 17 | 5 | 1115 | +0 | -7.2 | nan % (0) | +3 | +5 | [-14 ; +35] | [-18 ; +61] |
| P-L10 | 82 | +25 | +0.31 | +3.2 % | 60 | -10 | 20 | 55 | -10.0 | 10 | 82 / 0 | 16 | 4 | 1115 | +0 | -7.2 | nan % (0) | -6 | +0 | [+0 ; +0] | [+0 ; +0] |
| P-L20 | 82 | +25 | +0.31 | +3.2 % | 60 | -10 | 20 | 55 | -10.0 | 10 | 82 / 0 | 16 | 4 | 1115 | +0 | -7.2 | nan % (0) | -6 | +0 | [+0 ; +0] | [+0 ; +0] |
| P-Lm6 | 82 | -11 | -0.14 | -1.4 % | 60 | -6 | 0 | 43 | -6.0 | 10 | 82 / 78 | 23 | 6 | 1115 | +0 | -7.2 | nan % (0) | -27 | -37 | [-74 ; +3] | [-101 ; +33] |
| P-HA | 82 | +12 | +0.14 | +1.5 % | 60 | -10 | 16 | 73 | -10.0 | 10 | 82 / 21 | 19 | 5 | 1115 | +0 | -7.2 | nan % (0) | -18 | -14 | [-54 ; +27] | [-74 ; +61] |
| P-HB | 82 | +6 | +0.07 | +0.7 % | 59 | -10 | 15 | 64 | -10.0 | 19 | 106 / 0 | 20 | 4 | 1452 | +0 | -7.2 | nan % (0) | -23 | -19 | [-65 ; +29] | [-88 ; +62] |
| P-HC | 82 | +8 | +0.09 | +1.0 % | 60 | -10 | 15 | 63 | -10.0 | 10 | 106 / 24 | 20 | 4 | 1282 | +0 | -7.2 | nan % (0) | -22 | -18 | [-62 ; +29] | [-89 ; +67] |
| P-PF | 82 | +44 | +0.53 | +5.3 % | 65 | -10 | 15 | 48 | -10.0 | 18 | 90 / 9 | 19 | 4 | 1244 | +0 | -7.2 | nan % (0) | +13 | +18 | [-26 ; +67] | [-52 ; +100] |

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

### Protection des gains — CONFIRMATION (≥ 13.10) (674 cycles)

| Politique | Cycles actifs | P&L net ($) | Par cycle actif | Par $ de capital max | Cycles gagnants | Perte max | Pertes > 6 $ | Drawdown | ES 5 % | Capital max | Achats / ventes | Frais ($) | Coût d'écart ($) | Parts achetées | P&L couvertures ($) | Plancher le plus bas (moy.) | Jackpots conservés | Sans les 5 meilleurs | Écart avec P0 ($) | IC 90 % | IC corrigé (17) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P0 | 530 | -397 | -0.75 | -7.6 % | 352 | -10 | 177 | 421 | -10.0 | 10 | 530 / 0 | 107 | 30 | 7376 | +0 | -7.7 | nan % (0) | -429 | +0 | — | — |
| P-TP100 | 530 | -397 | -0.75 | -7.6 % | 352 | -10 | 177 | 421 | -10.0 | 10 | 530 / 0 | 107 | 30 | 7376 | +0 | -7.7 | nan % (0) | -429 | +0 | [+0 ; +0] | [+0 ; +0] |
| P-TP200 | 530 | -397 | -0.75 | -7.6 % | 352 | -10 | 177 | 421 | -10.0 | 10 | 530 / 0 | 107 | 30 | 7376 | +0 | -7.7 | nan % (0) | -429 | +0 | [+0 ; +0] | [+0 ; +0] |
| P-VP | 530 | -441 | -0.83 | -8.5 % | 352 | -10 | 155 | 466 | -10.0 | 10 | 530 / 265 | 120 | 36 | 7376 | +0 | -7.7 | nan % (0) | -468 | -44 | [-99 ; +16] | [-129 ; +54] |
| P-TR10 | 530 | -485 | -0.92 | -9.3 % | 385 | -10 | 135 | 504 | -10.0 | 10 | 530 / 260 | 144 | 45 | 7376 | +0 | -7.7 | nan % (0) | -513 | -88 | [-232 ; +60] | [-312 ; +181] |
| P-TR20 | 530 | -523 | -0.99 | -10.1 % | 382 | -10 | 136 | 543 | -10.0 | 10 | 530 / 242 | 145 | 41 | 7376 | +0 | -7.7 | nan % (0) | -552 | -126 | [-270 ; +22] | [-351 ; +127] |
| P-TR30 | 530 | -495 | -0.93 | -9.5 % | 380 | -10 | 136 | 519 | -10.0 | 10 | 530 / 209 | 143 | 37 | 7376 | +0 | -7.7 | nan % (0) | -526 | -98 | [-238 ; +42] | [-333 ; +142] |
| P-TR40 | 530 | -477 | -0.90 | -9.2 % | 373 | -10 | 136 | 511 | -10.0 | 10 | 530 / 188 | 141 | 37 | 7376 | +0 | -7.7 | nan % (0) | -509 | -80 | [-219 ; +62] | [-307 ; +151] |
| P-TF | 530 | -456 | -0.86 | -8.8 % | 327 | -10 | 137 | 477 | -10.0 | 10 | 530 / 134 | 136 | 33 | 7376 | +0 | -7.7 | nan % (0) | -488 | -59 | [-187 ; +73] | [-267 ; +157] |
| P-L0 | 530 | -380 | -0.72 | -7.3 % | 369 | -10 | 56 | 394 | -10.0 | 10 | 530 / 483 | 189 | 49 | 7376 | +0 | -7.7 | nan % (0) | -393 | +16 | [-204 ; +237] | [-333 ; +366] |
| P-L5 | 530 | -415 | -0.78 | -8.0 % | 356 | -10 | 173 | 436 | -10.0 | 10 | 530 / 97 | 112 | 37 | 7376 | +0 | -7.7 | nan % (0) | -444 | -19 | [-65 ; +39] | [-88 ; +82] |
| P-L10 | 530 | -397 | -0.75 | -7.6 % | 352 | -10 | 177 | 421 | -10.0 | 10 | 530 / 0 | 107 | 30 | 7376 | +0 | -7.7 | nan % (0) | -429 | +0 | [+0 ; +0] | [+0 ; +0] |
| P-L20 | 530 | -397 | -0.75 | -7.6 % | 352 | -10 | 177 | 421 | -10.0 | 10 | 530 / 0 | 107 | 30 | 7376 | +0 | -7.7 | nan % (0) | -429 | +0 | [+0 ; +0] | [+0 ; +0] |
| P-Lm6 | 530 | -350 | -0.66 | -6.7 % | 351 | -6 | 0 | 355 | -6.0 | 10 | 530 / 533 | 153 | 41 | 7376 | +0 | -7.7 | nan % (0) | -369 | +47 | [-60 ; +153] | [-138 ; +239] |
| P-HA | 530 | -475 | -0.90 | -9.1 % | 355 | -10 | 149 | 504 | -10.0 | 10 | 530 / 162 | 130 | 35 | 7376 | +0 | -7.7 | nan % (0) | -507 | -78 | [-179 ; +22] | [-239 ; +87] |
| P-HB | 530 | -460 | -0.87 | -8.1 % | 355 | -10 | 147 | 489 | -10.0 | 17 | 695 / 0 | 131 | 35 | 9474 | +0 | -7.7 | nan % (0) | -492 | -64 | [-169 ; +46] | [-235 ; +121] |
| P-HC | 530 | -452 | -0.85 | -8.7 % | 355 | -10 | 146 | 480 | -10.0 | 10 | 688 / 165 | 131 | 36 | 8398 | +0 | -7.7 | nan % (0) | -484 | -55 | [-157 ; +56] | [-213 ; +129] |
| P-PF | 530 | -460 | -0.87 | -8.5 % | 380 | -10 | 146 | 484 | -10.0 | 18 | 596 / 103 | 134 | 37 | 8360 | +0 | -7.7 | nan % (0) | -494 | -63 | [-183 ; +59] | [-250 ; +155] |

**H1041 — profit abandonné (P0, CONFIRMATION (≥ 13.10))** : 530 positions ; prix d'achat moyen 0.713 ; 13.9 parts ; meilleur acheteur moyen pendant le cycle 0.911 ; profit latent maximal exécutable moyen +2.80 $ ; profit final moyen -0.75 $ ; profit abandonné moyen 0.41 $ ; gagnants (≥ +5 $ liquidables) devenus perdants : **4** sur 96.

| Politique | Gagnants devenus perdants | Évités vs P0 | Jackpots supprimés | Profit latent abandonné ($) | Profit réellement verrouillé ($) | Fills partiels | P&L − P0 ($) |
|---|---|---|---|---|---|---|---|
| P0 | 4 | 0 | 0 / 0 | 220 | 0 | 0 | +0 |
| P-TP100 | 4 | 0 | 0 / 0 | 220 | 0 | 0 | +0 |
| P-TP200 | 4 | 0 | 0 / 0 | 220 | 0 | 0 | +0 |
| P-VP | 4 | 0 | 0 / 0 | 341 | 0 | 12 | -44 |
| P-TR10 | 3 | 1 | 0 / 0 | 639 | 522 | 64 | -88 |
| P-TR20 | 3 | 1 | 0 / 0 | 673 | 431 | 64 | -126 |
| P-TR30 | 3 | 1 | 0 / 0 | 654 | 323 | 61 | -98 |
| P-TR40 | 6 | -2 | 0 / 0 | 641 | 236 | 60 | -80 |
| P-TF | 21 | -17 | 0 / 0 | 572 | 76 | 50 | -59 |
| P-L0 | 0 | 4 | 0 / 0 | 1305 | 18 | 52 | +16 |
| P-L5 | 0 | 4 | 0 / 0 | 247 | 481 | 2 | -19 |
| P-L10 | 4 | 0 | 0 / 0 | 220 | 0 | 0 | +0 |
| P-L20 | 4 | 0 | 0 / 0 | 220 | 0 | 0 | +0 |
| P-Lm6 | 4 | 0 | 0 / 0 | 772 | 0 | 71 | +47 |
| P-HA | 0 | 4 | 0 / 0 | 527 | 6 | 48 | -78 |
| P-HB | 2 | 2 | 0 / 0 | 532 | 35 | 0 | -64 |
| P-HC | 2 | 2 | 0 / 0 | 535 | 15 | 49 | -55 |
| P-PF | 1 | 3 | 0 / 0 | 542 | 244 | 22 | -63 |

**Protection des gains — latence et frais (CONFIRMATION (≥ 13.10))**

| Politique | 164 ms | 200 ms | 250 ms | 500 ms | frais×0,5 | frais×1,5 |
|---|---|---|---|---|---|---|
| P0 | -397 | -359 | -336 | -241 | -347 | -445 |
| P-TP100 | -397 | -359 | -336 | -241 | -347 | -445 |
| P-TP200 | -397 | -359 | -336 | -241 | -347 | -445 |
| P-VP | -441 | -412 | -386 | -296 | -379 | -488 |
| P-TR10 | -485 | -472 | -420 | -376 | -435 | -507 |
| P-TR20 | -523 | -502 | -451 | -381 | -476 | -546 |
| P-TR30 | -495 | -482 | -438 | -372 | -430 | -544 |
| P-TR40 | -477 | -454 | -420 | -336 | -424 | -519 |
| P-TF | -456 | -423 | -396 | -330 | -385 | -495 |
| P-L0 | -380 | -373 | -374 | -349 | -244 | -482 |
| P-L5 | -415 | -379 | -354 | -273 | -355 | -456 |
| P-L10 | -397 | -359 | -336 | -241 | -347 | -445 |
| P-L20 | -397 | -359 | -336 | -241 | -347 | -445 |
| P-Lm6 | -350 | -330 | -320 | -261 | -277 | -421 |
| P-HA | -475 | -474 | -429 | -311 | -398 | -536 |
| P-HB | -460 | -454 | -402 | -300 | -386 | -510 |
| P-HC | -452 | -441 | -403 | -294 | -378 | -502 |
| P-PF | -460 | -455 | -418 | -324 | -370 | -538 |

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
| P-L5 | non | oui | non | non | non démontrée |
| P-L10 | non | non | non | non | non démontrée |
| P-L20 | non | non | non | non | non démontrée |
| P-Lm6 | non | non | non | oui | non démontrée |
| P-HA | non | non | non | non | non démontrée |
| P-HB | non | non | non | non | non démontrée |
| P-HC | non | non | non | non | non démontrée |
| P-PF | non | oui | non | non | non démontrée |
## 10. Critère de réussite (section 43) sur CONFIRMATION (≥ 13.10)

| Politique | IC corrigé > 0 | Pertes > 6 $ pas plus fréquentes | Jackpots ≥ 50 % | Écart > 0 à 500 ms | Écart > 0 sans les 5 meilleurs | Validation même sens | Verdict |
|---|---|---|---|---|---|---|---|
| T0-10 | oui | oui | oui | oui | oui | non | non démontrée |
| T1 | oui | oui | oui | oui | oui | non | non démontrée |
| T1v | oui | oui | oui | oui | oui | non | non démontrée |
| T2 | oui | oui | oui | oui | oui | non | non démontrée |
| T2p | oui | oui | oui | oui | oui | non | non démontrée |
| T3 | oui | oui | oui | oui | oui | non | non démontrée |
| T4 | non | oui | oui | oui | oui | non | non démontrée |
| LAD | oui | oui | oui | oui | oui | non | non démontrée |
| T5 | non | oui | oui | oui | oui | non | non démontrée |
| T6 | non | oui | oui | oui | oui | non | non démontrée |
| T7 | non | oui | oui | oui | oui | non | non démontrée |
| T7s | non | oui | oui | oui | oui | non | non démontrée |
| RS | non | oui | oui | — | oui | non | non démontrée |

Journal T7 (CONFIRMATION (≥ 13.10)) : chaque transaction avec les deux paiements possibles après exécution — resultat_reversal_h1003_journal_favori_confirmation.csv.gz, 1206 lignes.


## Limites
- Exécution preneur seulement ; notre propre impact au-delà de 5 s n'est pas modélisé.
- Toutes les politiques partagent la même probabilité ; si elle n'a pas d'avantage sur le marché, la gestion ne peut pas en créer.
- Nombreuses politiques : seuls les IC corrigés comptent. Peu de cycles par échantillon.

_Calcul : 2327 s._
