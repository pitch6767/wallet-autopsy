# Bot95 — Adaptive Reversal & Hedge Engine H1003–H1035 (CONTRÔLE : apprentissage et validation)

Généré le 12.10.2026 16:11 UTC. Cycles avec résultat officiel : apprentissage 197, validation 99, test 0. Capital ≤ 50 $, limite 5 CHF = 6.00 $. Exécution preneur sur le carnet enregistré. Aucun ordre ; aucun fantôme modifié.

## 1. Cerveau A — trajectoire courte du BTC (H1004, H1009, H1019, H1026–H1028)

| Cible | Échantillon | Taux de base | AUC momentum seul | AUC toutes familles | Gain d'AUC (IC 90 %) |
|---|---|---|---|---|---|
| hausse à 1 s | validation | 23.0 % | 0.580 | 0.617 | +0.037 [+0.029 ; +0.045] |
| hausse à 3 s | validation | 30.8 % | 0.606 | 0.672 | +0.066 [+0.058 ; +0.071] |
| hausse à 5 s | validation | 33.8 % | 0.621 | 0.697 | +0.076 [+0.067 ; +0.086] |
| hausse à 10 s | validation | 37.7 % | 0.624 | 0.698 | +0.074 [+0.064 ; +0.084] |
| hausse à 15 s | validation | 41.3 % | 0.602 | 0.688 | +0.086 [+0.074 ; +0.097] |
| hausse à 30 s | validation | 45.1 % | 0.588 | 0.647 | +0.060 [+0.044 ; +0.075] |
| hausse à 60 s | validation | 46.4 % | 0.568 | 0.606 | +0.037 [+0.018 ; +0.056] |
| retournement à 30 s | validation | 26.1 % | 0.560 | 0.563 | +0.004 [-0.002 ; +0.010] |

**Ablation (hausse à 30 s) : perte d'AUC quand on retire une famille** (positif = la famille apporte)

| Famille retirée | validation |
|---|---|
| mom | +0.0055 [+0.0022 ; +0.0087] |
| flux | +0.0015 [+0.0005 ; +0.0027] |
| carnet | +0.0497 [+0.0335 ; +0.0646] |
| inter | +0.0001 [+0.0000 ; +0.0002] |
| liq | -0.0003 [-0.0008 ; +0.0003] |
| cl | +0.0001 [+0.0000 ; +0.0001] |

**Ampleur du mouvement à 30 s (H1009)** — Brier : modèle gaussien (volatilité seule) contre logistique toutes familles

| Seuil | Échantillon | Fréquence | Brier gaussien | Brier modèle | Différence (IC 90 %) |
|---|---|---|---|---|---|
| ≥ 5 $ | validation | 68.5 % | 0.2062 | 0.2120 | +0.0058 [+0.0016 ; +0.0098] |
| ≥ 10 $ | validation | 52.5 % | 0.2573 | 0.2523 | -0.0050 [-0.0090 ; -0.0012] |
| ≥ 20 $ | validation | 27.1 % | 0.2081 | 0.1964 | -0.0117 [-0.0148 ; -0.0088] |
| ≥ 40 $ | validation | 6.6 % | 0.0625 | 0.0607 | -0.0018 [-0.0026 ; -0.0010] |

## 2. Cerveau B — probabilité de règlement (H1016)

logit p = -0.050 + -0.003 × logit(M0) + 0.943 × logit(milieu Polymarket) (sans milieu : -0.036 + 0.462 × logit(M0)) ; 4150 décisions d'apprentissage.


# FAMILLE D'ENTRÉE : avantage du cerveau B ≥ e


**Calibration de règlement (H1016, décisions toutes les 10 s)** — Brier et log loss ; écart = cerveau B − milieu du marché

| Échantillon | Décisions | Brier marché | Brier M0 brut | Brier cerveau B | Cerveau B − marché (IC 90 %) | LL marché | LL cerveau B | Ajout de a30 (H1026) : ΔBrier (IC 90 %) |
|---|---|---|---|---|---|---|---|---|
| apprentissage | 4150 | 0.1695 | 0.1876 | 0.1690 | -0.0004 [-0.0016 ; +0.0007] | 0.5010 | 0.5004 | -0.00074 [-0.00180 ; +0.00027] |
| validation | 2203 | 0.1328 | 0.1243 | 0.1337 | +0.0009 [-0.0005 ; +0.0023] | 0.4152 | 0.4188 | +0.00052 [-0.00085 ; +0.00197] |

Seuil d'entrée e choisi sur l'apprentissage (T0-50) : **0.05** (e=0.05 → +0 $, e=0.10 → +0 $, e=0.15 → +0 $).

Attribution RS (apprentissage) : aucun signal → T0-50.


## 3. Tournoi T0–T7 (H1034), latence 164 ms

### apprentissage (sert au choix de e et de RS) (197 cycles)

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

### validation (99 cycles)

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

### Simulation A — entrées progressives — validation (99 cycles)

| Politique | Cycles actifs | P&L net ($) | Par cycle actif | Par $ de capital max | Cycles gagnants | Perte max | Pertes > 6 $ | Drawdown | ES 5 % | Capital max | Achats / ventes | Frais ($) | Coût d'écart ($) | Parts achetées | P&L couvertures ($) | Plancher le plus bas (moy.) | Jackpots conservés | Sans les 5 meilleurs | Écart avec T0-50 ($) | IC 90 % | IC corrigé (13) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T0-50 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | — | — |
| T0-10 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| T1 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| T1v | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| T2 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| T2p | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |

### Simulation B — changement de camp — validation (99 cycles)

| Politique | Cycles actifs | P&L net ($) | Par cycle actif | Par $ de capital max | Cycles gagnants | Perte max | Pertes > 6 $ | Drawdown | ES 5 % | Capital max | Achats / ventes | Frais ($) | Coût d'écart ($) | Parts achetées | P&L couvertures ($) | Plancher le plus bas (moy.) | Jackpots conservés | Sans les 5 meilleurs | Écart avec T0-50 ($) | IC 90 % | IC corrigé (13) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T0-50 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | — | — |
| T1 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| T2 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| T4 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| LAD | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| T5 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| T7 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |

### Simulation C — protection du capital (même plafond de 50 $) — validation (99 cycles)

| Politique | Cycles actifs | P&L net ($) | Par cycle actif | Par $ de capital max | Cycles gagnants | Perte max | Pertes > 6 $ | Drawdown | ES 5 % | Capital max | Achats / ventes | Frais ($) | Coût d'écart ($) | Parts achetées | P&L couvertures ($) | Plancher le plus bas (moy.) | Jackpots conservés | Sans les 5 meilleurs | Écart avec T0-50 ($) | IC 90 % | IC corrigé (13) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T0-50 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | — | — |
| T7 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| T7s | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| T5 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |
| T6 | 0 | +0 | +0.00 | +0.0 % | 0 | +0 | 0 | 0 | +0.0 | 0 | 0 / 0 | 0 | 0 | 0 | +0 | +0.0 | nan % (0) | +0 | +0 | [+0 ; +0] | [+0 ; +0] |

**H1033 — coût économique de la protection stricte (validation)** : T7 − T7s = +0 $ [+0 ; +0] ; pertes > 6 $ : T7 0, T7s 0 ; T5 − T6 = +0 $ (pertes > 6 $ : T5 0, T6 0).


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

## 8. H1017 — Régimes au signal d'entrée

| validation : régime | Cycles | T0-50 | T1 | T3 | T5 | T7 | RS |
|---|---|---|---|---|---|---|---|
| aucun signal | 99 | +0 | +0 | +0 | +0 | +0 | +0 |

## 9. H1036–H1040 — Sauvetage de la première position (entrée 10 $, mêmes cycles)

R0 conserver ; R1 vendre toute la position à −0,15 ; R2 couverture préventive (−0,05 et cerveau A contre ≥ 0,60) ; R3 couverture complète à −0,15 ; R4 couverture tardive (p ≤ 0,25) ; R5 vente de 50 % puis couverture du reste à −0,15 ; R6 inversion complète à −0,15 (vente de tout + 10 $ de l'opposé) ; R7 adaptatif (H1039 : probabilité de redevenir gagnante, apprise sur l'apprentissage ; vend si acheteur net > probabilité + 0,01, couvre si (1 − probabilité) − coût opposé > 0,01, sinon conserve). Couverture = achat de l'opposé pour toutes les parts non appariées. Les noms R0–R7 sont propres à cette étude (aucun lien avec le fantôme R4).

Modèle de récupération H1039 : 2750 états détériorés d'apprentissage (taux de récupération 33.4 %).

### Tournoi de sauvetage R0–R7 — validation (99 cycles)

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


# FAMILLE D'ENTRÉE : favori du marché (vendeur 0,60–0,85, 60 à 180 s écoulées)

| Échantillon | Décisions | Brier marché | Brier M0 brut | Brier cerveau B | Cerveau B − marché (IC 90 %) | LL marché | LL cerveau B | Ajout de a30 (H1026) : ΔBrier (IC 90 %) |
|---|---|---|---|---|---|---|---|---|
| apprentissage | 4150 | 0.1695 | 0.1876 | 0.1690 | -0.0004 [-0.0016 ; +0.0007] | 0.5010 | 0.5004 | -0.00074 [-0.00179 ; +0.00032] |
| validation | 2203 | 0.1328 | 0.1243 | 0.1337 | +0.0009 [-0.0005 ; +0.0022] | 0.4152 | 0.4188 | +0.00052 [-0.00083 ; +0.00198] |

Seuil d'entrée e choisi sur l'apprentissage (T0-50) : **0.05** (e=0.05 → +0 $, e=0.10 → +0 $, e=0.15 → +0 $).

Attribution RS (apprentissage) : aucun signal → T0-50, choc de liquidations → T0-50, range → T7, retournement probable → T7, tendance → T7.


## 3. Tournoi T0–T7 (H1034), latence 164 ms

### apprentissage (sert au choix de e et de RS) (197 cycles)

| Politique | Cycles actifs | P&L net ($) | Par cycle actif | Par $ de capital max | Cycles gagnants | Perte max | Pertes > 6 $ | Drawdown | ES 5 % | Capital max | Achats / ventes | Frais ($) | Coût d'écart ($) | Parts achetées | P&L couvertures ($) | Plancher le plus bas (moy.) | Jackpots conservés | Sans les 5 meilleurs | Écart avec T0-50 ($) | IC 90 % | IC corrigé (13) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T0-50 | 150 | -1265 | -8.44 | -18.6 % | 88 | -50 | 61 | 1433 | -50.0 | 50 | 150 / 0 | 142 | 42 | 9689 | +0 | -34.5 | nan % (0) | -1421 | +0 | — | — |
| T0-10 | 150 | -253 | -1.69 | -17.0 % | 88 | -10 | 61 | 281 | -10.0 | 10 | 150 / 0 | 31 | 9 | 2116 | +0 | -7.5 | nan % (0) | -284 | +1012 | [+491 ; +1518] | [+149 ; +1910] |
| T1 | 150 | -253 | -1.69 | -17.0 % | 88 | -10 | 61 | 281 | -10.0 | 10 | 150 / 0 | 31 | 9 | 2116 | +0 | -7.5 | nan % (0) | -284 | +1012 | [+501 ; +1554] | [+170 ; +1877] |
| T1v | 150 | -253 | -1.69 | -17.0 % | 88 | -10 | 61 | 281 | -10.0 | 10 | 150 / 0 | 31 | 9 | 2116 | +0 | -7.5 | nan % (0) | -284 | +1012 | [+492 ; +1557] | [+137 ; +1919] |
| T2 | 150 | -253 | -1.69 | -17.0 % | 88 | -10 | 61 | 281 | -10.0 | 10 | 150 / 0 | 31 | 9 | 2116 | +0 | -7.5 | nan % (0) | -284 | +1012 | [+475 ; +1567] | [+168 ; +1897] |
| T2p | 150 | -253 | -1.69 | -17.0 % | 88 | -10 | 61 | 281 | -10.0 | 10 | 150 / 0 | 31 | 9 | 2116 | +0 | -7.5 | nan % (0) | -284 | +1012 | [+496 ; +1563] | [+196 ; +1888] |
| T3 | 150 | -196 | -1.31 | -10.7 % | 86 | -10 | 54 | 221 | -9.9 | 18 | 225 / 0 | 37 | 10 | 2648 | +57 | -7.5 | nan % (0) | -227 | +1069 | [+519 ; +1636] | [+198 ; +1955] |
| T4 | 150 | -210 | -1.40 | -14.2 % | 85 | -10 | 57 | 236 | -10.0 | 10 | 150 / 50 | 37 | 9 | 2116 | +42 | -7.5 | nan % (0) | -242 | +1055 | [+506 ; +1628] | [+180 ; +1938] |
| LAD | 150 | -210 | -1.40 | -13.3 % | 73 | -10 | 37 | 226 | -10.0 | 20 | 185 / 56 | 42 | 9 | 2414 | +43 | -7.5 | nan % (0) | -241 | +1056 | [+482 ; +1652] | [+163 ; +2014] |
| T5 | 150 | -174 | -1.16 | -9.0 % | 125 | -10 | 25 | 178 | -10.0 | 16 | 287 / 0 | 54 | 12 | 3920 | +78 | -7.5 | nan % (0) | -187 | +1091 | [+463 ; +1731] | [+86 ; +2121] |
| T6 | 150 | -106 | -0.71 | -9.1 % | 125 | -6 | 0 | 109 | -6.0 | 10 | 282 / 0 | 32 | 8 | 2360 | +47 | -4.6 | nan % (0) | -114 | +1159 | [+515 ; +1800] | [+128 ; +2184] |
| T7 | 150 | -109 | -0.72 | -6.0 % | 70 | -6 | 0 | 109 | -5.9 | 17 | 252 / 103 | 60 | 14 | 3318 | +144 | -7.5 | nan % (0) | -118 | +1157 | [+488 ; +1820] | [+80 ; +2245] |
| T7s | 150 | -81 | -0.54 | -7.5 % | 81 | -6 | 0 | 81 | -5.9 | 10 | 234 / 78 | 35 | 8 | 1982 | +73 | -4.6 | nan % (0) | -88 | +1184 | [+530 ; +1840] | [+143 ; +2306] |
| RS | 150 | -93 | -0.62 | -5.0 % | 70 | -6 | 0 | 93 | -5.9 | 50 | 250 / 103 | 61 | 14 | 3388 | +147 | -7.9 | nan % (0) | -116 | +1173 | [+520 ; +1816] | [+107 ; +2194] |

### validation (99 cycles)

| Politique | Cycles actifs | P&L net ($) | Par cycle actif | Par $ de capital max | Cycles gagnants | Perte max | Pertes > 6 $ | Drawdown | ES 5 % | Capital max | Achats / ventes | Frais ($) | Coût d'écart ($) | Parts achetées | P&L couvertures ($) | Plancher le plus bas (moy.) | Jackpots conservés | Sans les 5 meilleurs | Écart avec T0-50 ($) | IC 90 % | IC corrigé (13) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T0-50 | 78 | +533 | +6.84 | +16.0 % | 63 | -50 | 14 | 124 | -50.0 | 50 | 78 / 0 | 68 | 19 | 4714 | +0 | -33.8 | nan % (0) | +379 | +0 | — | — |
| T0-10 | 78 | +103 | +1.33 | +13.8 % | 63 | -10 | 14 | 36 | -10.0 | 10 | 78 / 0 | 15 | 4 | 1062 | +0 | -7.6 | nan % (0) | +73 | -430 | [-707 ; -127] | [-884 ; +72] |
| T1 | 78 | +103 | +1.33 | +13.8 % | 63 | -10 | 14 | 36 | -10.0 | 10 | 78 / 0 | 15 | 4 | 1062 | +0 | -7.6 | nan % (0) | +73 | -430 | [-712 ; -131] | [-841 ; +57] |
| T1v | 78 | +103 | +1.33 | +13.8 % | 63 | -10 | 14 | 36 | -10.0 | 10 | 78 / 0 | 15 | 4 | 1062 | +0 | -7.6 | nan % (0) | +73 | -430 | [-718 ; -138] | [-868 ; +62] |
| T2 | 78 | +103 | +1.33 | +13.8 % | 63 | -10 | 14 | 36 | -10.0 | 10 | 78 / 0 | 15 | 4 | 1062 | +0 | -7.6 | nan % (0) | +73 | -430 | [-710 ; -138] | [-882 ; +77] |
| T2p | 78 | +103 | +1.33 | +13.8 % | 63 | -10 | 14 | 36 | -10.0 | 10 | 78 / 0 | 15 | 4 | 1062 | +0 | -7.6 | nan % (0) | +73 | -430 | [-706 ; -144] | [-853 ; +43] |
| T3 | 78 | +80 | +1.03 | +9.1 % | 60 | -10 | 13 | 33 | -9.8 | 18 | 107 / 0 | 18 | 5 | 1261 | -23 | -7.6 | nan % (0) | +50 | -453 | [-748 ; -139] | [-944 ; +82] |
| T4 | 78 | +76 | +0.98 | +10.2 % | 58 | -10 | 13 | 36 | -10.0 | 10 | 78 / 24 | 18 | 5 | 1062 | -27 | -7.6 | nan % (0) | +46 | -457 | [-751 ; -145] | [-911 ; +46] |
| LAD | 78 | +54 | +0.69 | +7.0 % | 53 | -10 | 10 | 53 | -10.0 | 19 | 91 / 23 | 20 | 4 | 1158 | -50 | -7.6 | nan % (0) | +23 | -480 | [-767 ; -153] | [-961 ; +58] |
| T5 | 78 | -32 | -0.41 | -3.2 % | 71 | -10 | 7 | 40 | -10.0 | 16 | 155 / 0 | 28 | 7 | 2030 | -135 | -7.6 | nan % (0) | -41 | -565 | [-884 ; -226] | [-1072 ; -6] |
| T6 | 78 | -19 | -0.24 | -3.1 % | 71 | -6 | 0 | 24 | -6.0 | 10 | 152 / 0 | 17 | 4 | 1240 | -82 | -4.6 | nan % (0) | -25 | -552 | [-884 ; -205] | [-1068 ; +27] |
| T7 | 78 | -31 | -0.40 | -3.3 % | 47 | -6 | 0 | 34 | -5.2 | 16 | 135 / 45 | 30 | 7 | 1767 | -135 | -7.6 | nan % (0) | -39 | -564 | [-907 ; -202] | [-1082 ; +34] |
| T7s | 78 | -23 | -0.30 | -4.1 % | 52 | -6 | 0 | 26 | -5.0 | 10 | 132 / 34 | 18 | 5 | 1089 | -87 | -4.6 | nan % (0) | -28 | -556 | [-907 ; -192] | [-1100 ; +67] |
| RS | 78 | -31 | -0.40 | -3.3 % | 47 | -6 | 0 | 34 | -5.2 | 16 | 135 / 45 | 30 | 7 | 1767 | -135 | -7.6 | nan % (0) | -39 | -564 | [-911 ; -190] | [-1105 ; +44] |

## 4. Les trois simulations prioritaires

### Simulation A — entrées progressives — validation (99 cycles)

| Politique | Cycles actifs | P&L net ($) | Par cycle actif | Par $ de capital max | Cycles gagnants | Perte max | Pertes > 6 $ | Drawdown | ES 5 % | Capital max | Achats / ventes | Frais ($) | Coût d'écart ($) | Parts achetées | P&L couvertures ($) | Plancher le plus bas (moy.) | Jackpots conservés | Sans les 5 meilleurs | Écart avec T0-50 ($) | IC 90 % | IC corrigé (13) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T0-50 | 78 | +533 | +6.84 | +16.0 % | 63 | -50 | 14 | 124 | -50.0 | 50 | 78 / 0 | 68 | 19 | 4714 | +0 | -33.8 | nan % (0) | +379 | +0 | — | — |
| T0-10 | 78 | +103 | +1.33 | +13.8 % | 63 | -10 | 14 | 36 | -10.0 | 10 | 78 / 0 | 15 | 4 | 1062 | +0 | -7.6 | nan % (0) | +73 | -430 | [-710 ; -137] | [-833 ; +61] |
| T1 | 78 | +103 | +1.33 | +13.8 % | 63 | -10 | 14 | 36 | -10.0 | 10 | 78 / 0 | 15 | 4 | 1062 | +0 | -7.6 | nan % (0) | +73 | -430 | [-709 ; -136] | [-877 ; +45] |
| T1v | 78 | +103 | +1.33 | +13.8 % | 63 | -10 | 14 | 36 | -10.0 | 10 | 78 / 0 | 15 | 4 | 1062 | +0 | -7.6 | nan % (0) | +73 | -430 | [-706 ; -137] | [-861 ; +61] |
| T2 | 78 | +103 | +1.33 | +13.8 % | 63 | -10 | 14 | 36 | -10.0 | 10 | 78 / 0 | 15 | 4 | 1062 | +0 | -7.6 | nan % (0) | +73 | -430 | [-720 ; -128] | [-863 ; +73] |
| T2p | 78 | +103 | +1.33 | +13.8 % | 63 | -10 | 14 | 36 | -10.0 | 10 | 78 / 0 | 15 | 4 | 1062 | +0 | -7.6 | nan % (0) | +73 | -430 | [-725 ; -147] | [-861 ; +33] |

### Simulation B — changement de camp — validation (99 cycles)

| Politique | Cycles actifs | P&L net ($) | Par cycle actif | Par $ de capital max | Cycles gagnants | Perte max | Pertes > 6 $ | Drawdown | ES 5 % | Capital max | Achats / ventes | Frais ($) | Coût d'écart ($) | Parts achetées | P&L couvertures ($) | Plancher le plus bas (moy.) | Jackpots conservés | Sans les 5 meilleurs | Écart avec T0-50 ($) | IC 90 % | IC corrigé (13) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T0-50 | 78 | +533 | +6.84 | +16.0 % | 63 | -50 | 14 | 124 | -50.0 | 50 | 78 / 0 | 68 | 19 | 4714 | +0 | -33.8 | nan % (0) | +379 | +0 | — | — |
| T1 | 78 | +103 | +1.33 | +13.8 % | 63 | -10 | 14 | 36 | -10.0 | 10 | 78 / 0 | 15 | 4 | 1062 | +0 | -7.6 | nan % (0) | +73 | -430 | [-703 ; -128] | [-862 ; +63] |
| T2 | 78 | +103 | +1.33 | +13.8 % | 63 | -10 | 14 | 36 | -10.0 | 10 | 78 / 0 | 15 | 4 | 1062 | +0 | -7.6 | nan % (0) | +73 | -430 | [-712 ; -136] | [-858 ; +44] |
| T4 | 78 | +76 | +0.98 | +10.2 % | 58 | -10 | 13 | 36 | -10.0 | 10 | 78 / 24 | 18 | 5 | 1062 | -27 | -7.6 | nan % (0) | +46 | -457 | [-744 ; -154] | [-925 ; +87] |
| LAD | 78 | +54 | +0.69 | +7.0 % | 53 | -10 | 10 | 53 | -10.0 | 19 | 91 / 23 | 20 | 4 | 1158 | -50 | -7.6 | nan % (0) | +23 | -480 | [-786 ; -168] | [-958 ; +60] |
| T5 | 78 | -32 | -0.41 | -3.2 % | 71 | -10 | 7 | 40 | -10.0 | 16 | 155 / 0 | 28 | 7 | 2030 | -135 | -7.6 | nan % (0) | -41 | -565 | [-903 ; -232] | [-1093 ; -22] |
| T7 | 78 | -31 | -0.40 | -3.3 % | 47 | -6 | 0 | 34 | -5.2 | 16 | 135 / 45 | 30 | 7 | 1767 | -135 | -7.6 | nan % (0) | -39 | -564 | [-911 ; -194] | [-1092 ; +25] |

### Simulation C — protection du capital (même plafond de 50 $) — validation (99 cycles)

| Politique | Cycles actifs | P&L net ($) | Par cycle actif | Par $ de capital max | Cycles gagnants | Perte max | Pertes > 6 $ | Drawdown | ES 5 % | Capital max | Achats / ventes | Frais ($) | Coût d'écart ($) | Parts achetées | P&L couvertures ($) | Plancher le plus bas (moy.) | Jackpots conservés | Sans les 5 meilleurs | Écart avec T0-50 ($) | IC 90 % | IC corrigé (13) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T0-50 | 78 | +533 | +6.84 | +16.0 % | 63 | -50 | 14 | 124 | -50.0 | 50 | 78 / 0 | 68 | 19 | 4714 | +0 | -33.8 | nan % (0) | +379 | +0 | — | — |
| T7 | 78 | -31 | -0.40 | -3.3 % | 47 | -6 | 0 | 34 | -5.2 | 16 | 135 / 45 | 30 | 7 | 1767 | -135 | -7.6 | nan % (0) | -39 | -564 | [-908 ; -202] | [-1092 ; +26] |
| T7s | 78 | -23 | -0.30 | -4.1 % | 52 | -6 | 0 | 26 | -5.0 | 10 | 132 / 34 | 18 | 5 | 1089 | -87 | -4.6 | nan % (0) | -28 | -556 | [-920 ; -193] | [-1099 ; +38] |
| T5 | 78 | -32 | -0.41 | -3.2 % | 71 | -10 | 7 | 40 | -10.0 | 16 | 155 / 0 | 28 | 7 | 2030 | -135 | -7.6 | nan % (0) | -41 | -565 | [-899 ; -231] | [-1093 ; -12] |
| T6 | 78 | -19 | -0.24 | -3.1 % | 71 | -6 | 0 | 24 | -6.0 | 10 | 152 / 0 | 17 | 4 | 1240 | -82 | -4.6 | nan % (0) | -25 | -552 | [-878 ; -200] | [-1078 ; +38] |

**H1033 — coût économique de la protection stricte (validation)** : T7 − T7s = -8 $ [-15 ; -1] ; pertes > 6 $ : T7 0, T7s 0 ; T5 − T6 = -13 $ (pertes > 6 $ : T5 7, T6 0).


## 7. Renforts, couvertures, inversions

**H1013 — P&L de chaque tranche jusqu'au règlement (validation)**

| Politique | Tranche | Nombre | Coût ($) | P&L ($) | P&L / $ |
|---|---|---|---|---|---|
| T1 | 1 | 78 | 750 | +103 | +13.8 % |
| T1v | 1 | 78 | 750 | +103 | +13.8 % |
| T2 | 1 | 78 | 750 | +103 | +13.8 % |
| T2p | 1 | 78 | 750 | +103 | +13.8 % |

**P&L des transactions de protection par type (validation)** (valeur au règlement − coût)

| Politique | Couverture | Protection (vente) | Inversion | Verrou | Sortie |
|---|---|---|---|---|---|
| T3 | -23 | +0 | +0 | +0 | +0 |
| T4 | +0 | -27 | +0 | +0 | +0 |
| LAD | -25 | -25 | +0 | +0 | +0 |
| T5 | +0 | +0 | +0 | -135 | +0 |
| T6 | +0 | +0 | +0 | -82 | +0 |
| T7 | +0 | +3 | +0 | -95 | -43 |
| T7s | +0 | +0 | +0 | -57 | -30 |

**H1025 — coût par dollar de perte maximale évitée (validation, contre T1)**

| Politique | P&L − T1 ($) | Plancher moyen le plus bas − T1 ($) | Coût par $ évité |
|---|---|---|---|
| T3 | -23 | +0.00 | +nan |
| T4 | -27 | +0.00 | +nan |
| LAD | -50 | +0.00 | +nan |
| T7 | -135 | +0.00 | +nan |

**H1020 — changements de camp (validation)** : aucun.

## 8. H1017 — Régimes au signal d'entrée

| validation : régime | Cycles | T0-50 | T1 | T3 | T5 | T7 | RS |
|---|---|---|---|---|---|---|---|
| aucun signal | 11 | +0 | +0 | +0 | +0 | +0 | +0 |
| choc de liquidations | 1 | +0 | +0 | +0 | +0 | +0 | +0 |
| range | 61 | +261 | +40 | +26 | -41 | -27 | -27 |
| retournement probable | 9 | +83 | +19 | +16 | +3 | +1 | +1 |
| tendance | 17 | +189 | +44 | +38 | +7 | -5 | -5 |

## 9. H1036–H1040 — Sauvetage de la première position (entrée 10 $, mêmes cycles)

R0 conserver ; R1 vendre toute la position à −0,15 ; R2 couverture préventive (−0,05 et cerveau A contre ≥ 0,60) ; R3 couverture complète à −0,15 ; R4 couverture tardive (p ≤ 0,25) ; R5 vente de 50 % puis couverture du reste à −0,15 ; R6 inversion complète à −0,15 (vente de tout + 10 $ de l'opposé) ; R7 adaptatif (H1039 : probabilité de redevenir gagnante, apprise sur l'apprentissage ; vend si acheteur net > probabilité + 0,01, couvre si (1 − probabilité) − coût opposé > 0,01, sinon conserve). Couverture = achat de l'opposé pour toutes les parts non appariées. Les noms R0–R7 sont propres à cette étude (aucun lien avec le fantôme R4).

Modèle de récupération H1039 : 2750 états détériorés d'apprentissage (taux de récupération 33.4 %).

### Tournoi de sauvetage R0–R7 — validation (99 cycles)

| Politique | Cycles actifs | P&L net ($) | Par cycle actif | Par $ de capital max | Cycles gagnants | Perte max | Pertes > 6 $ | Drawdown | ES 5 % | Capital max | Achats / ventes | Frais ($) | Coût d'écart ($) | Parts achetées | P&L couvertures ($) | Plancher le plus bas (moy.) | Jackpots conservés | Sans les 5 meilleurs | Écart avec R0 ($) | IC 90 % | IC corrigé (7) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| R0 | 78 | +103 | +1.33 | +13.8 % | 63 | -10 | 14 | 36 | -10.0 | 10 | 78 / 0 | 15 | 4 | 1062 | +0 | -7.6 | nan % (0) | +73 | +0 | — | — |
| R1 | 78 | +5 | +0.06 | +0.6 % | 35 | -6 | 1 | 45 | -4.9 | 10 | 78 / 43 | 25 | 3 | 1062 | -99 | -7.6 | nan % (0) | -26 | -99 | [-169 ; -27] | [-207 ; +9] |
| R2 | 78 | -49 | -0.63 | -4.4 % | 20 | -6 | 1 | 56 | -4.7 | 22 | 136 / 0 | 28 | 6 | 1856 | -152 | -7.6 | nan % (0) | -79 | -152 | [-234 ; -73] | [-271 ; -32] |
| R3 | 78 | +2 | +0.03 | +0.2 % | 35 | -6 | 1 | 45 | -4.9 | 22 | 121 / 0 | 25 | 2 | 1659 | -101 | -7.6 | nan % (0) | -28 | -101 | [-174 ; -30] | [-208 ; +6] |
| R4 | 78 | +91 | +1.16 | +9.3 % | 58 | -9 | 19 | 22 | -8.1 | 23 | 98 / 0 | 19 | 5 | 1337 | -13 | -7.6 | nan % (0) | +60 | -13 | [-58 ; +27] | [-84 ; +44] |
| R5 | 78 | +4 | +0.05 | +0.5 % | 35 | -6 | 1 | 45 | -4.9 | 14 | 121 / 43 | 25 | 2 | 1361 | -100 | -7.6 | nan % (0) | -27 | -100 | [-172 ; -31] | [-205 ; +6] |
| R6 | 78 | -145 | -1.86 | -16.1 % | 49 | -15 | 28 | 204 | -14.1 | 16 | 121 / 43 | 40 | 0 | 1931 | -248 | -9.1 | nan % (0) | -193 | -248 | [-419 ; -77] | [-511 ; +13] |
| R7 | 78 | +4 | +0.06 | +0.5 % | 35 | -6 | 1 | 45 | -4.9 | 20 | 93 / 28 | 25 | 3 | 1286 | -99 | -7.6 | nan % (0) | -26 | -99 | [-171 ; -27] | [-209 ; +5] |

**Niveaux de détérioration (H1036, descriptif, aucun choix) — validation** : R1-10 -99 $ ; R1 -99 $ ; R1-20 -90 $ ; R1-30 -24 $ ; R3-10 -100 $ ; R3 -101 $ ; R3-20 -93 $ ; R3-30 -24 $ (écart avec R0).

**Test décisif (section 9) — validation** : 49 positions devenues défavorables (p ≤ entrée − 0,15) ; ramené à 100.

| Politique | Perdantes sans intervention | Gagnantes sans intervention | Sauvetages (perte réduite) | Coût moyen d'un sauvetage réussi ($ gagnés) | Couvertures inutiles (gagnantes abîmées) | Coût des couvertures inutiles ($) | Perte moyenne R0 → politique | Perte max R0 → politique | P&L net − R0 (défavorables) | P&L net − R0 (tous) |
|---|---|---|---|---|---|---|---|---|---|---|
| R1 | 31 | 57 | 31 | +6.10 | 57 | 190 | -9.52 → -3.11 | -10.0 → -6.4 | -99 | -99 |
| R2 | 31 | 57 | 31 | +7.25 | 57 | 178 | -9.52 → -2.43 | -10.0 → -6.4 | -69 | -152 |
| R3 | 31 | 57 | 31 | +6.18 | 57 | 194 | -9.52 → -3.17 | -10.0 → -6.4 | -101 | -101 |
| R4 | 31 | 57 | 31 | +2.71 | 10 | 53 | -9.52 → -6.98 | -10.0 → -8.8 | -13 | -13 |
| R5 | 31 | 57 | 31 | +6.14 | 57 | 192 | -9.52 → -3.14 | -10.0 → -6.4 | -100 | -100 |
| R6 | 31 | 57 | 31 | +14.79 | 57 | 470 | -9.52 → -12.62 | -10.0 → -14.8 | -248 | -248 |
| R7 | 31 | 57 | 31 | +6.13 | 57 | 191 | -9.52 → -3.12 | -10.0 → -6.4 | -99 | -99 |
| Rv | 31 | 57 | 29 | +4.00 | 55 | 112 | -9.52 → -3.14 | -10.0 → -6.4 | -56 | -56 |
| Ra | 31 | 57 | 29 | +4.07 | 55 | 114 | -9.52 → -3.06 | -10.0 → -6.0 | -57 | -57 |
| Rm | 31 | 57 | 29 | +4.02 | 55 | 111 | -9.52 → -3.13 | -10.0 → -6.0 | -55 | -55 |

**H1038 — vendre ou acheter l'opposé, à risque comparable (cible : pire résultat ≥ −6 $, dès p ≤ entrée − 0,15) — validation**

| Réaction | Cycles où elle a agi | Pire résultat final moyen | Pertes > 6 $ | Capital max moyen ($) | Frais ($) | P&L net ($) | Écart avec R0 (IC 90 %) |
|---|---|---|---|---|---|---|---|
| ne rien faire | 0 | -7.58 | 14 | 7.6 | 15.4 | +103 | +0 [+0 ; +0] |
| vendre une partie | 41 | -5.93 | 1 | 7.6 | 21.3 | +48 | -56 [-100 ; -11] |
| acheter l'opposé | 41 | -5.91 | 1 | 9.5 | 21.4 | +47 | -57 [-101 ; -11] |
| vendre une partie puis acheter l'opposé | 41 | -5.95 | 3 | 7.8 | 21.3 | +48 | -55 [-100 ; -11] |


## Limites
- Exécution preneur seulement ; notre propre impact au-delà de 5 s n'est pas modélisé.
- Toutes les politiques partagent la même probabilité ; si elle n'a pas d'avantage sur le marché, la gestion ne peut pas en créer.
- Nombreuses politiques : seuls les IC corrigés comptent. Peu de cycles par échantillon.

_Calcul : 321 s._
