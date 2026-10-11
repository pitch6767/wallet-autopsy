# Bot95 — H804 / H805 / H806 — PRÉLIMINAIRE (hors ligne)

Généré le 11.10.2026 17:07 UTC. Fantômes maker vivants de Dublin : 5311 ordres réglés (11.10 10:55 → 16:55 UTC). Marchés complets lus : 595. Aucun ordre, aucun réglage modifié.

## 1. H804 — M21 contre M1 / M4 (mêmes cycles, mêmes hypothèses d'exécution)

Cycles où M1, M21 et M4 ont tous coté : **24**. Fills « prudents » (seules les transactions font avancer la file) et « proportionnels ». Résultat au règlement, sans frais maker, ristourne non comptée. Capital immobilisé = parts remplies × prix.

| Moteur | Ordres tentés | Ordres remplis (prudent) | Parts (prudent / prop.) | P&L prudent ($) | P&L prop. ($) | par ordre tenté | par part | IC 90 % par cycle (prudent) | Drawdown (prudent) | Capital immobilisé moyen / max par cycle |
|---|---|---|---|---|---|---|---|---|---|---|
| M1 | 99 | 61 | 21018 / 21102 | -2396 | -2325 | -24.21 | -11.4 c | [-132.7 ; -63.9] $/cycle | 2396 | 125 / 250 $ |
| M21 | 161 | 103 | 2980 / 3686 | -90 | -6 | -0.56 | -3.0 c | [-16.6 ; +10.0] $/cycle | 176 | 80 / 212 $ |
| M4 | 235 | 178 | 9614 / 9269 | -489 | -556 | -2.08 | -5.1 c | [-44.0 ; +4.0] $/cycle | 606 | 117 / 342 $ |
| M6 | 656 | 622 | 38947 / 32557 | +200 | +447 | +0.30 | +0.5 c | [-131.7 ; +168.4] $/cycle | 2572 | 557 / 1065 $ |
| M8 | 68 | 51 | 17631 / 17716 | -1896 | -1825 | -27.89 | -10.8 c | [-128.7 ; -49.6] $/cycle | 1896 | 119 / 250 $ |

**Tous les cycles de chaque moteur (pas seulement les 24 communs), prudent** : M1 238 ordres / 52 cycles, 46 542 parts, −72 $ (−0,2 c/part ; sans ses 3 meilleurs cycles −3 013 $) ; M21 167 / 26, 3 256 parts, −151 $ (−4,6 c ; sans top 3 −376 $) ; M4 471 / 45, −650 $ (−3,4 c) ; M6 1 089 / 39, −826 $ (−1,2 c) ; M8 162 / 37, −1 919 $ (−6,5 c).
Le « +2,1 c (M1) / +1,6 c (M21) par part » du rapport précédent venait d'un sous-ensemble plus court (cycles Dublin exportés jusqu'à 12:55 UTC) : il ne tient pas sur l'ensemble.

**Pourquoi M1 / M21 gagnent par part et pas M4 / M6 / M8 — caractéristiques des ordres remplis (prudent, cycles communs)**

| Moteur | Prix moyen payé | Part sur le favori (> 0,5) | Temps restant médian à la pose | Taux de gain des fills | Gain − prix (c/part) | Markout +1 s / +5 s / +10 s (c/part) | Écart modèle − prix à la pose (c) | Fills sous condition toxique |
|---|---|---|---|---|---|---|---|---|
| M1 | 0.143 | 1 % | 127 s | 3 % | -11.4 | -1.0 / -1.9 / -1.6 | +21.9 | 64 % des parts |
| M21 | 0.641 | 97 % | 221 s | 61 % | -3.0 | -1.0 / -1.6 / -3.4 | -6.5 | 5 % des parts |
| M4 | 0.291 | 3 % | 249 s | 24 % | -5.1 | -0.1 / -0.0 / -0.0 | +10.1 | 24 % des parts |
| M6 | 0.343 | 4 % | 261 s | 35 % | +0.5 | -1.4 / -1.0 / -0.5 | +7.6 | 64 % des parts |
| M8 | 0.142 | 1 % | 127 s | 3 % | -10.8 | -0.8 / -1.5 / -1.7 | +22.0 | 60 % des parts |

**Résultat par part selon le prix payé (prudent, cycles communs)**

| Moteur | < 0,30 | 0,30–0,50 | 0,50–0,70 | 0,70–0,90 | ≥ 0,90 |
|---|---|---|---|---|---|
| M1 | -11.8 c (20856 p.) | — | +38.0 c (161 p.) | — | — |
| M21 | — | — | -9.6 c (2128 p.) | +13.3 c (852 p.) | — |
| M4 | -10.7 c (4888 p.) | +2.1 c (4332 p.) | -21.5 c (331 p.) | +21.0 c (63 p.) | — |
| M6 | +11.9 c (10889 p.) | -4.2 c (26392 p.) | -3.8 c (1412 p.) | +21.0 c (253 p.) | — |
| M8 | -11.2 c (17470 p.) | — | +38.0 c (161 p.) | — | — |

## 2. H805 — Achats maker à 0,95–0,99 selon le temps restant

**A. Fills observés de tous les makers (595 marchés complets).** Retournement = le côté acheté perd. Borne haute 95 % du taux de perte : Clopper-Pearson (zéro perte observée ne veut pas dire zéro risque). Markout = prix du côté à la transaction suivante ≥ 5 s plus tard (API, à la seconde) − prix payé.

| Prix | Fenêtre | Fills | Marchés | Fills perdants | Taux de perte | Borne haute 95 % | Seuil de rentabilité | Résultat | Plus grosse perte (1 fill) | Plus grosse perte (1 marché) | Markout +5 s (c) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0,95–0,97 | 30–15 s | 1547 | 86 | 32 | 2.07 % | 2.75 % | ≈ 4 % | +723 $ | -54 $ | -480 $ | +1.96 |
| 0,95–0,97 | 15–5 s | 213 | 18 | 5 | 2.35 % | 4.87 % | ≈ 4 % | +52 $ | -31 $ | -117 $ | +0.01 |
| 0,95–0,97 | 5–0 s | 59 | 4 | 0 | 0.00 % | 4.95 % | ≈ 4 % | +76 $ | +0 $ | +5 $ | +2.76 |
| 0,97–0,98 | 30–15 s | 908 | 95 | 1 | 0.11 % | 0.49 % | ≈ 2,5 % | +706 $ | -18 $ | -18 $ | +0.82 |
| 0,97–0,98 | 15–5 s | 136 | 18 | 0 | 0.00 % | 2.18 % | ≈ 2,5 % | +113 $ | +0 $ | +1 $ | +1.93 |
| 0,97–0,98 | 5–0 s | 31 | 4 | 0 | 0.00 % | 9.21 % | ≈ 2,5 % | +38 $ | +0 $ | +3 $ | +1.36 |
| 0,98–0,99 | 30–15 s | 1293 | 118 | 11 | 0.85 % | 1.39 % | ≈ 1,5 % | +404 $ | -132 $ | -457 $ | -0.25 |
| 0,98–0,99 | 15–5 s | 271 | 31 | 0 | 0.00 % | 1.10 % | ≈ 1,5 % | +170 $ | +0 $ | +0 $ | +1.00 |
| 0,98–0,99 | 5–0 s | 53 | 8 | 0 | 0.00 % | 5.50 % | ≈ 1,5 % | +27 $ | +0 $ | +0 $ | +1.00 |
| ≥ 0,99 | 30–15 s | 4830 | 476 | 34 | 0.70 % | 0.93 % | ≈ 0,7 % | -1033 $ | -584 $ | -4190 $ | -1.15 |
| ≥ 0,99 | 15–5 s | 3304 | 487 | 0 | 0.00 % | 0.08 % | ≈ 0,7 % | +2084 $ | +0 $ | +0 $ | -0.09 |
| ≥ 0,99 | 5–0 s | 1201 | 268 | 0 | 0.00 % | 0.22 % | ≈ 0,7 % | +834 $ | +0 $ | +0 $ | +0.07 |

Note : le taux de perte est compté par fill ; plusieurs fills du même marché perdent ensemble (un retournement touche tout le monde). Le nombre de marchés retournés est la vraie unité de risque.

**B. Simulation sur les cycles de Dublin : offre d'achat posée au meilleur acheteur du favori si celui-ci est entre 0,95 et 0,99, à 30 / 15 / 5 s de la fin, gardée jusqu'à la fin (100 parts).** Montre combien de ces offres auraient été remplies (le reste = fills non obtenus).

| Pose à | File | Offres posées | Remplies | Taux de fill | Parts | Perdantes | Résultat ($) |
|---|---|---|---|---|---|---|---|
| 30 s avant la fin | prudente | 64 | 6 | 9 % | 600 | 0 | +14 |
| 30 s avant la fin | centrale | 64 | 9 | 14 % | 769 | 0 | +18 |
| 30 s avant la fin | optimiste | 64 | 23 | 36 % | 2300 | 0 | +50 |
| 15 s avant la fin | prudente | 63 | 0 | 0 % | 0 | 0 | +0 |
| 15 s avant la fin | centrale | 63 | 0 | 0 % | 0 | 0 | +0 |
| 15 s avant la fin | optimiste | 63 | 2 | 3 % | 200 | 0 | +2 |
| 5 s avant la fin | prudente | 61 | 0 | 0 % | 0 | 0 | +0 |
| 5 s avant la fin | centrale | 61 | 0 | 0 % | 0 | 0 | +0 |
| 5 s avant la fin | optimiste | 61 | 3 | 5 % | 300 | 0 | +3 |

## 3. H806 — Sélection des fills : makers réels contre nos fantômes à conditions égales

Fills de makers réels datés à la ms (achats) : 83912 ; fills prudents de nos fantômes : 4588 ; mêmes cycles Dublin.

| Groupe | Fills | Markout +1 s (c) | +5 s (c) | Règlement (c/part) | Makers réels à prix × minute identiques : +1 s / +5 s / règlement |
|---|---|---|---|---|---|
| makers réels (tous) | 83912 | +0.36 | +0.67 | +0.82 | — |
| nous M0 | 102 | -0.58 | -1.48 | -3.94 | +0.04 / -0.10 / +1.36 |
| nous M1 | 316 | -1.03 | -0.58 | +3.25 | -0.13 / +0.04 / +3.41 |
| nous M10 | 195 | -0.57 | -0.29 | -3.93 | -0.10 / -0.13 / +12.66 |
| nous M2 | 674 | -2.04 | -2.94 | -1.57 | +0.09 / +0.04 / +11.96 |
| nous M21 | 87 | -1.27 | -2.48 | +3.46 | +0.50 / +1.61 / -0.79 |
| nous M3 | 166 | +5.09 | +2.68 | +4.47 | +0.13 / -0.16 / -3.02 |
| nous M4 | 450 | -1.06 | -1.28 | -2.38 | -0.02 / +0.02 / +11.20 |
| nous M4a | 307 | -1.41 | -1.21 | -2.85 | +0.11 / +0.68 / +12.78 |
| nous M4b | 294 | -1.38 | -1.03 | -4.65 | +0.12 / +0.99 / +13.23 |
| nous M4c | 293 | -1.35 | -1.85 | -7.60 | +0.05 / +0.52 / +9.27 |
| nous M5 | 337 | -2.54 | -2.04 | -2.23 | +0.05 / +0.07 / +15.57 |
| nous M6 | 1019 | -2.47 | -1.85 | -5.89 | +0.00 / -0.15 / +13.21 |
| nous M8 | 199 | -0.46 | -0.23 | -4.83 | -0.18 / +0.08 / +0.61 |
| nous M8b | 131 | -0.73 | -0.61 | -7.90 | -0.18 / +0.26 / +1.00 |

**Conditions au moment du fill** (médianes ; proportions)

| Groupe | Au meilleur prix | Taille du preneur < 10 $ | Profondeur à notre niveau (parts) | Flux vendeur 2 s avant (parts) | Volatilité 30 s (c) | Écart vendeur-acheteur (c) |
|---|---|---|---|---|---|---|
| makers réels | 95 % | 96 % | 272 | 80 | 2.75 | 1.0 |
| nous (tous fantômes) | 55 % | nan % | 50 | 125 | 5.45 | 1.0 |
| nous M1 | 38 % | nan % | 70 | 167 | 5.50 | 1.0 |
| nous M21 | 70 % | nan % | 39 | 73 | 6.11 | 1.0 |
| nous M4 | 63 % | nan % | 50 | 86 | 6.12 | 1.0 |
| nous M6 | 44 % | nan % | 42 | 140 | 4.54 | 1.0 |
| nous M8 | 49 % | nan % | 58 | 204 | 5.87 | 1.0 |

**Markout +5 s selon chaque condition (makers réels | nos fantômes)** — un mécanisme reproductible doit montrer le même effet chez les deux

| Condition | Makers réels : oui / non | Fantômes : oui / non |
|---|---|---|
| au meilleur prix | +0.79 (79741) / -0.84 (4171) | -0.37 (2503) / -1.65 (2085) |
| flux vendeur 2 s avant = 0 | +0.78 (604) / +0.67 (83308) | +nan (0) / -1.31 (4588) |
| profondeur ≥ 100 parts | +1.08 (59129) / -0.29 (24783) | -0.95 (1338) / -1.51 (3250) |
| volatilité 30 s < 1 c | +0.38 (12389) / +0.72 (71523) | -2.77 (50) / -1.30 (4538) |
| écart vendeur-acheteur = 1 c | +0.81 (77857) / -2.20 (6055) | -1.47 (3811) / -0.90 (777) |
| prix ≥ 0,50 (favori) | +0.69 (26559) / +0.67 (57353) | -1.93 (207) / -1.30 (4381) |

**Régression commune du markout +5 s (c/part), IC 90 % par cycles**

| Variable | Coefficient | IC 90 % |
|---|---|---|
| fantôme (vs maker réel) | -0.64 | [-1.48 ; +0.33] |
| au meilleur prix | +1.91 | [+1.06 ; +2.68] |
| aucun flux vendeur 2 s avant | +0.53 | [-0.20 ; +1.23] |
| log profondeur | +0.53 | [+0.32 ; +0.73] |
| volatilité 30 s | +0.07 | [+0.00 ; +0.14] |
| écart vendeur-acheteur | +0.69 | [-0.10 ; +1.06] |
| prix | -0.62 | [-2.05 ; +0.97] |
| moment du cycle | +0.31 | [-1.18 ; +2.03] |

Écart brut fantômes − makers réels au markout +5 s : -1.98 c ; écart restant après conditions : -0.64 c.

## Limites
- Une journée ; fantômes vivants depuis le 11.10 vers 11 h UTC seulement.
- Fills réels : seuls ceux rapprochés d'une transaction Dublin à la ms sont datés.
- On ne voit jamais les ordres réels posés puis annulés (fills non obtenus des makers réels inconnus) ; la partie B de H805 les simule pour nous.
