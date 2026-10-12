# Bot95 — F1 priorités 2 à 5 : fatigue de l'absorption, perp → spot, retraits synchronisés, règlement, avance exploitable (apprentissage / validation / test inédit)

Généré le 12.10.2026 12:50 UTC. Cycles : apprentissage 169, validation 85, test 72. Aucun ordre ; période réservée non lue.

## 1. H933 — Fatigue de l'absorption

Efficacité = mouvement du prix sur 5 s ($) par BTC de pression nette ; part de vagues absorbées ; mouvement à 10 s (signé).

| Échantillon | Rang de la vague | Vagues | Absorbées | Efficacité ($/BTC) | Mouvement à 10 s ($) |
|---|---|---|---|---|---|
| apprentissage | 1re | 268 | 47 % | +0.76 [+0.63 ; +0.90] | +4.43 [+2.60 ; +6.45] |
| apprentissage | 2e | 143 | 48 % | +0.66 [+0.49 ; +0.82] | +4.01 [+2.34 ; +5.92] |
| apprentissage | 3e et plus | 131 | 48 % | +1.00 [+0.70 ; +1.32] | +3.97 [+2.35 ; +5.59] |
| validation | 1re | 178 | 44 % | +0.72 [+0.55 ; +0.89] | +5.99 [+4.27 ; +7.85] |
| validation | 2e | 105 | 38 % | +0.93 [+0.71 ; +1.17] | +3.72 [+1.54 ; +5.96] |
| validation | 3e et plus | 86 | 35 % | +0.86 [+0.69 ; +0.99] | +7.74 [+3.74 ; +11.17] |
| test | 1re | 180 | 48 % | +0.53 [+0.24 ; +0.78] | +4.63 [+3.07 ; +6.24] |
| test | 2e | 114 | 42 % | +0.70 [+0.51 ; +0.91] | +5.40 [+3.35 ; +7.47] |
| test | 3e et plus | 93 | 35 % | +0.99 [+0.71 ; +1.24] | +3.42 [+0.63 ; +5.74] |

## 2. H954 — Après une absorption, la vague suivante casse-t-elle plus souvent ?

Cassure = mouvement > 1,5 σ30 dans le sens de la vague sur 30 s.

| Échantillon | Vague | Vagues | Taux de cassure (IC 90 %) | Écart avec une 1re vague (IC 90 %) |
|---|---|---|---|---|
| apprentissage | 1re vague | 268 | +25.75 [+21.25 ; +30.45] % | — |
| apprentissage | après absorption | 172 | +22.09 [+15.24 ; +30.06] % | -3.65 [-10.87 ; +4.71] pts |
| validation | 1re vague | 178 | +26.40 [+21.30 ; +31.82] % | — |
| validation | après absorption | 108 | +26.85 [+19.05 ; +34.33] % | +0.45 [-6.89 ; +8.29] pts |
| test | 1re vague | 180 | +23.33 [+18.65 ; +27.81] % | — |
| test | après absorption | 119 | +20.17 [+13.51 ; +27.10] % | -3.17 [-9.57 ; +4.10] pts |

## 3. H941 — Un mouvement BTC déplace-t-il assez la probabilité de règlement ?

Pour chaque vague forte avec 30 à 240 s restantes : déplacement de M0 entre t et t + 10 s (signé), part des cas où il dépasse 0,03, et résultat officiel − M0(t).

| Échantillon | Temps restant | Vagues | Δ M0 à 10 s | Part > 0,03 | Résultat − M0(t) |
|---|---|---|---|---|---|
| apprentissage | 30–89 s | 104 | +0.06 [+0.03 ; +0.10] | 18 % | +0.05 [+0.01 ; +0.10] |
| apprentissage | 90–149 s | 86 | +0.08 [+0.05 ; +0.12] | 37 % | +0.06 [-0.01 ; +0.13] |
| apprentissage | 150–240 s | 120 | +0.08 [+0.07 ; +0.10] | 51 % | +0.18 [+0.12 ; +0.25] |
| validation | 30–89 s | 70 | +0.04 [+0.01 ; +0.07] | 21 % | +0.02 [-0.02 ; +0.07] |
| validation | 90–149 s | 74 | +0.06 [+0.03 ; +0.10] | 34 % | +0.00 [-0.08 ; +0.09] |
| validation | 150–240 s | 104 | +0.07 [+0.05 ; +0.09] | 47 % | +0.09 [-0.01 ; +0.19] |
| test | 30–89 s | 66 | +0.00 [-0.01 ; +0.01] | 8 % | +0.01 [+0.00 ; +0.04] |
| test | 90–149 s | 67 | +0.04 [+0.02 ; +0.06] | 21 % | +0.03 [+0.00 ; +0.08] |
| test | 150–240 s | 117 | +0.05 [+0.03 ; +0.06] | 42 % | +0.10 [+0.04 ; +0.17] |

## 4. H937 / H965 / H969 — Chocs du perp Bybit : transmission au spot, à Polymarket, et avance exploitable

2893 chocs du perp (≥ 3 écarts-types en 500 ms, spot encore immobile).

| Échantillon | Chocs | Part reproduite par le spot à 100 / 250 / 500 / 1 000 / 2 000 ms | Délai spot à 50 % (médiane, ms) | Polymarket +1 c : part et délai médian (ms) | Avance restante après 164 ms (médiane, ms) |
|---|---|---|---|---|---|
| apprentissage | 1402 | +0.12 / +0.29 / +0.54 / +0.57 / +0.67 | 250 (23 % atteignent 50 %) | 74 %, 250 | 86 |
| validation | 819 | +0.19 / +0.28 / +0.38 / +0.46 / +0.64 | 300 (40 % atteignent 50 %) | 79 %, 250 | 86 |
| test | 672 | +0.15 / +0.25 / +0.31 / +0.39 / +0.48 | 250 (36 % atteignent 50 %) | 73 %, 250 | 86 |

**H969 — Achat de 20 $ du jeton dans le sens du choc à 164 ms, au prix vu (frais compris)**

| Échantillon | Achats | (a) revente à 10 s ($, IC 90 % total) | (b) revente à 30 s | (c) règlement |
|---|---|---|---|---|
| apprentissage | 874 | +678 [+34 ; +1411] (n=801) | +763 [+12 ; +1534] (n=768) | -31 [-1440 ; +1481] (n=874) |
| validation | 343 | -111 [-257 ; +36] (n=297) | +90 [-149 ; +352] (n=282) | -1395 [-1849 ; -975] (n=343) |
| test | 327 | +96 [-91 ; +326] (n=294) | +57 [-107 ; +225] (n=280) | -163 [-487 ; +172] (n=189) |

## 5. H956 — Retraits synchronisés Binance spot / Bybit perp

Mouvement BTC signé (retrait d'offres vendeuses → hausse attendue), en $.

| Échantillon | Type | Secondes | 5 s | 10 s | 30 s |
|---|---|---|---|---|---|
| apprentissage | synchronisé | 2229 | -2.93 [-3.52 ; -2.35] | -3.76 [-4.74 ; -2.78] | -4.01 [-5.71 ; -2.40] |
| apprentissage | Binance seul | 2841 | -1.97 [-2.41 ; -1.55] | -3.08 [-3.71 ; -2.42] | -4.50 [-6.22 ; -2.92] |
| apprentissage | Bybit seul | 2841 | -0.01 [-0.34 ; +0.31] | -0.40 [-0.99 ; +0.15] | -0.41 [-1.65 ; +0.78] |
| validation | synchronisé | 2225 | -3.38 [-3.79 ; -2.95] | -4.35 [-4.91 ; -3.81] | -5.09 [-6.55 ; -3.74] |
| validation | Binance seul | 2601 | -1.71 [-2.13 ; -1.26] | -2.57 [-3.23 ; -1.91] | -4.45 [-5.82 ; -3.10] |
| validation | Bybit seul | 2807 | -0.49 [-0.85 ; -0.15] | -0.75 [-1.29 ; -0.23] | -0.65 [-1.78 ; +0.52] |
| test | synchronisé | 1698 | -2.95 [-3.25 ; -2.62] | -3.99 [-4.46 ; -3.49] | -4.64 [-5.85 ; -3.42] |
| test | Binance seul | 2337 | -1.35 [-1.67 ; -1.04] | -1.95 [-2.44 ; -1.49] | -2.23 [-3.10 ; -1.33] |
| test | Bybit seul | 2210 | -0.13 [-0.55 ; +0.28] | +0.04 [-0.63 ; +0.71] | -0.04 [-1.24 ; +1.16] |

## Limites
- Carnets limités à 50 $ du meilleur prix ; perp Binance non enregistré ; quelques dizaines d'heures.
- Les délais sont des heures de réception à Dublin ; notre latence de 164 ms est appliquée en plus.

_Calcul : 209 s._
