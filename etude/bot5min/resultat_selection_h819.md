# Bot95 — H819 / H820 / H821 : calibration, gagnants contre perdants, préservation des jackpots — PRÉLIMINAIRE (hors ligne)

Généré le 11.10.2026 19:55 UTC. Décisions uniques sur cycles Dublin : 77 (62 dans H816) sur 55 cycles ; apprentissage 41 / test 36 (coupure 12:30 UTC). Exécution 20 $, 164 ms. Aucun ordre ; H816, R4, fantômes inchangés.

## 1. H819 — Calibration au règlement

**A. Toutes les décisions uniques de bot95/rapide.json (cycles sans carnet compris) : probabilité Bot95 contre prix payé a0**

144 décisions sur 107 cycles. Brier : Bot95 0.217 ; prix a0 0.206. Log loss : Bot95 0.630 ; prix a0 0.596.

| Tranche de probabilité | Décisions | Bot95 moyen | Prix a0 moyen | Victoire observée |
|---|---|---|---|---|
| Bot95 0.2–0.3 | 4 | 0.26 | 0.06 | 0 % |
| Bot95 0.3–0.4 | 21 | 0.36 | 0.15 | 19 % |
| Bot95 0.4–0.5 | 82 | 0.45 | 0.24 | 32 % |
| Bot95 0.5–0.7 | 24 | 0.58 | 0.35 | 54 % |
| Bot95 0.7–1.0 | 13 | 0.82 | 0.61 | 69 % |

| Temps restant | Décisions | Bot95 moyen | Prix a0 moyen | Victoire observée | Brier Bot95 / prix |
|---|---|---|---|---|---|
| 60–120 s | 21 | 0.45 | 0.21 | 14 % | 0.182 / 0.093 |
| 120–180 s | 31 | 0.48 | 0.26 | 32 % | 0.182 / 0.156 |
| 180–240 s | 41 | 0.50 | 0.29 | 44 % | 0.255 / 0.275 |
| 240–301 s | 51 | 0.50 | 0.29 | 41 % | 0.223 / 0.229 |

**B. Cycles Dublin : Bot95 / milieu Polymarket / prix payé / combinaison (logistique sur logit Bot95 + logit milieu, apprise sur l'apprentissage)**

| Estimateur | Brier test | Log loss test | Brier apprentissage |
|---|---|---|---|
| Bot95 | 0.265 | 0.752 | 0.227 |
| milieu Polymarket | 0.234 | 0.662 | 0.242 |
| prix payé a0 | 0.233 | 0.660 | 0.231 |
| combinaison (apprise) | 0.249 | 0.724 | 0.217 |

Poids de la combinaison (logit) : constante -0.28, Bot95 +1.14, milieu +0.13. Test : 36 décisions — petit échantillon.

## 2. H820 — Gagnants contre perdants, à prix et temps restant égaux

Logistique « gagné ~ logit(prix) + temps restant + variable », variable standardisée, IC 90 % par cycles et IC corrigé de Bonferroni (10 variables). Toutes les décisions Dublin (77).

| Variable | Gagnants (médiane) | Perdants (médiane) | Coefficient | IC 90 % | IC corrigé | Verdict |
|---|---|---|---|---|---|---|
| écart modèle − marché | +0.21 | +0.21 | +0.22 | [-0.15 ; +0.66] | [-0.54 ; +1.13] | rien |
| distance au prix à battre (écarts-types) | -0.17 | -0.25 | +0.18 | [-0.32 ; +0.83] | [-0.54 ; +1.25] | rien |
| distance au prix à battre ($, signée) | -2.08 | -2.19 | -0.23 | [-0.86 ; +0.22] | [-1.33 ; +0.44] | rien |
| tendance BTC 10 s (pb, vers nous) | +0.00 | -0.13 | +0.33 | [-0.12 ; +0.92] | [-0.32 ; +1.39] | rien |
| tendance BTC 30 s (pb) | +0.00 | -0.53 | +0.19 | [-0.26 ; +0.84] | [-0.63 ; +1.27] | rien |
| volatilité BTC 60 s (pb) | +0.14 | +0.17 | -0.04 | [-0.46 ; +0.39] | [-0.75 ; +0.60] | rien |
| profondeur vendeuse ≤ a0 ($) | +3.68 | +3.18 | +0.14 | [-0.38 ; +0.85] | [-0.63 ; +1.52] | rien |
| déséquilibre acheteurs / vendeurs | -0.47 | -0.27 | -0.10 | [-0.55 ; +0.30] | [-0.79 ; +0.55] | rien |
| flux preneur 10 s vers nous (parts) | +5.43 | -77.01 | +0.16 | [-0.37 ; +0.61] | [-0.77 ; +0.99] | rien |
| déclenché par le carnet (1/0) | +1.00 | +1.00 | -0.19 | [-0.70 ; +0.29] | [-0.88 ; +0.47] | rien |

## 3. H821 — Règles simples d'exclusion qui épargnent les jackpots

38 règles candidates (une variable, seuil = tercile de l'apprentissage, deux sens). Admissibles : ne suppriment aucun jackpot de l'apprentissage et gardent ≥ 50 % des signaux. **Retenue sur l'apprentissage : exclure si distance au prix à battre (écarts-types) > -0.090** (gain d'apprentissage +87 $).

| Échantillon | Politique | Signaux gardés | Perdants évités | Gagnants perdus | Jackpots perdus | P&L ($) | Marginal vs H816/base ($) | IC 90 % du marginal (par signal) | Drawdown | 5 meilleurs / total |
|---|---|---|---|---|---|---|---|---|---|---|
| TEST — toutes | base | 36 / 36 | 0 | 0 | 0 | +72 | +0 | [+0.00 ; +0.00] | 147 | 476 % |
| TEST — toutes | avec la règle | 26 / 36 | 8 | 2 | 0 | +211 | +139 | [+2.01 ; +5.82] | 82 | 162 % |
| TEST — H816 | base | 29 / 29 | 0 | 0 | 0 | +47 | +0 | [+0.00 ; +0.00] | 131 | 644 % |
| TEST — H816 | avec la règle | 23 / 29 | 5 | 1 | 0 | +126 | +79 | [+0.82 ; +4.92] | 82 | 239 % |
| apprentissage — toutes | base | 41 / 41 | 0 | 0 | 0 | +264 | +0 | [+0.00 ; +0.00] | 63 | 130 % |
| apprentissage — toutes | avec la règle | 27 / 41 | 10 | 4 | 0 | +351 | +87 | [+0.09 ; +4.12] | 40 | 98 % |

**Les 5 meilleures règles sur l'apprentissage et leur résultat sur le test** (lecture : un écart apprentissage → test = sur-apprentissage)

| Règle | Gain apprentissage ($) | Gain test ($) |
|---|---|---|
| exclure si distance au prix à battre (écarts-types) > -0.090 | +87 | +139 |
| exclure si flux preneur 10 s vers nous (parts) > +62.000 | +68 | -138 |
| exclure si profondeur vendeuse ≤ a0 ($) < +0.000 | +0 | +0 |
| exclure si déclenché par le carnet (1/0) > +1.000 | +0 | +0 |
| exclure si écart modèle − marché > +0.206 | -1000000000 | -40 |

## 4. Verdict
- Une variante future n'est proposée que si la règle retenue améliore le P&L sur le TEST avec un IC par cycles > 0, sans perdre de jackpot.

## Limites
- Une journée ; ~40 décisions de test : très faible puissance.
- Modèle Bot95 = probabilité enregistrée au signal ; milieu Polymarket reconstruit (±3 c, photos 10 s).
