# Bot95 — Suite R4 : H796–H798 — PRÉLIMINAIRE (hors ligne)

Généré le 11.10.2026 15:36 UTC. 157 signaux réglés, 31 cycles (avant le 13.10). Apprentissage = cycles < 10:55 UTC, test = après (cycles indépendants). IC 90 % par rééchantillonnage de cycles. R4 = relances toutes les 500 ms pendant 5 s, +2 c, probabilité recalculée − prix − frais ≥ 0,05, exécution 164 ms après chaque envoi, budget 50 $.

## 1. H796 — Prédicteur de non-retour (livrable 1)

Offres retirées dans les 5 s : 122 (apprentissage 61, test 61). Non-retour (≤ prix + 2 c, 5 s après le retrait) : 22 %. Instant médian du retrait : 125 ms après la décision. Taux de gain du signal : non-retour 81 %, retour 40 %.

**Variables (toutes connues au retrait) — AUC seule sur le test** (orientée sur l'apprentissage)

| Variable | Sens | AUC test | IC 90 % |
|---|---|---|---|
| btc_bn1 | + | 0.85 | [0.73 ; 0.97] |
| btc_bn3 | + | 0.87 | [0.74 ; 0.96] |
| btc_perp3 | + | 0.88 | [0.77 ; 0.96] |
| cl5 | − | 0.40 | [0.23 ; 0.55] |
| ask_mv | + | 0.91 | [0.80 ; 0.98] |
| bid_mv | + | 0.64 | [0.45 ; 0.84] |
| prof_ratio | − | 0.96 | [0.92 ; 0.99] |
| trade | + | 0.55 | [0.35 ; 0.74] |
| edge | + | 0.70 | [0.55 ; 0.84] |
| a0 | − | 0.43 | [0.21 ; 0.62] |
| tleft | − | 0.46 | [0.26 ; 0.66] |

| Modèle | AUC test | IC 90 % | Brier test | Brier « taux de base » |
|---|---|---|---|---|
| témoin BTC (Binance 1 s + 3 s, Bybit 3 s) | 0.87 | [0.76 ; 0.97] | 0.134 | 0.214 |
| témoin Chainlink (5 s) | 0.60 | [0.46 ; 0.75] | 0.214 | 0.214 |
| témoin carnet (vendeur, acheteur, profondeur) | 0.95 | [0.90 ; 0.99] | 0.140 | 0.214 |
| prédicteur complet | 0.95 | [0.87 ; 0.99] | 0.100 | 0.214 |

**Calibration du prédicteur complet (test)**

| Probabilité prédite | Offres | Non-retour observé |
|---|---|---|
| 0.0–0.2 | 42 | 2 % |
| 0.2–0.4 | 5 | 80 % |
| 0.4–0.6 | 6 | 83 % |
| 0.6–1.0 | 8 | 88 % |

**Avance temporelle** : la prédiction est faite au retrait (médiane 125 ms après la décision), soit 5 s avant que le non-retour soit constaté. Mais à cet instant l'offre au prix du signal est déjà partie : l'avance ne permet pas d'acheter au prix du signal.

**Valeur économique (test)** — on ne garde que ce qui est exécutable : achat 164 ms après le retrait, budget restant, frais.

- Relances R4 après le retrait (toutes) : +433 $ ; relances seulement si retour probable (p < 0,5) : +404 $.
- Poursuite immédiate jusqu'à +5 c quand le non-retour est probable (p ≥ 0,5) : +415 $ sur 11 offres (3 exécutées).

## 2. H797 — Relance après zéro fill / après fill partiel (livrables 2, 3, 4, 6)

| Politique | Remplis | Parts | P&L ($) | / signal (IC 90 %) | marginal vs D | IC 90 % du marginal | 1re / 2e moitié | Drawdown | Jackpots | Signaux en plus : gagnants / perdants |
|---|---|---|---|---|---|---|---|---|---|---|
| Bot95 actuel (164 ms, prix du signal) | 128 | 23616 | +4580 | +29.17 [+6.12 ; +52.98] | -195 | [-8.01 ; +4.73] / signal | +9.77 / +47.84 | 767 | 24 | 2 / 0 |
| D — aucune relance (1re tentative R4) | 134 | 31275 | +4775 | +30.42 [+6.09 ; +56.90] | +0 | [+0.00 ; +0.00] / signal | +11.32 / +48.79 | 958 | 25 | 0 / 0 |
| A — relance après zéro fill | 137 | 34253 | +4753 | +30.27 [+5.59 ; +56.50] | -23 | [-1.06 ; +0.94] / signal | +11.32 / +48.51 | 958 | 25 | 1 / 2 |
| B — relance après fill partiel | 134 | 33795 | +5363 | +34.16 [+7.77 ; +61.07] | +588 | [+0.34 ; +7.85] / signal | +11.64 / +55.84 | 939 | 25 | 0 / 0 |
| C — les deux (= R4) | 137 | 36773 | +5341 | +34.02 [+9.76 ; +61.48] | +566 | [-0.02 ; +7.81] / signal | +11.64 / +55.56 | 939 | 25 | 1 / 2 |

- Parts supplémentaires après zéro fill : 3 signaux, 2978 parts, 146 $ ; résultat -23 $ (-16 % par $) ; gagnants 1, perdants 2.

- Parts supplémentaires après fill partiel : 24 signaux, 2520 parts, 461 $ ; résultat +588 $ (+128 % par $) ; gagnants 12, perdants 12.

## 3. H798 — Le premier fill renseigne-t-il sur la qualité des parts supplémentaires ? (livrable 5)

Signaux avec premier fill partiel puis parts supplémentaires : 24. Variable expliquée : résultat par $ des parts supplémentaires.

| Groupe | Signaux | Résultat des parts supplémentaires par $ | Taux de gain |
|---|---|---|---|
| premier fill < 25 % du budget | 4 | +199 % | 50 % |
| premier fill ≥ 25 % du budget | 20 | +101 % | 50 % |

Régression logistique (gain du signal, 134 signaux avec un premier fill ; coefficients standardisés, IC 90 % par cycles) :

| Variable | Coefficient | IC 90 % |
|---|---|---|
| frac | -0.11 | [-0.54 ; +0.40] |
| a0 | +0.68 | [+0.08 ; +1.49] |
| logq0 | +0.63 | [+0.26 ; +1.19] |
| tleft | -0.20 | [-0.63 ; +0.37] |
| vol | -0.14 | [-0.63 ; +0.73] |
| modele | +0.14 | [-0.28 ; +1.12] |

frac = part du budget remplie au premier fill ; le délai du premier fill est presque toujours la 1re tentative (164 ms), donc peu informatif ici.

## 4. Verdict statistique sur cycles indépendants (livrable 7)

- Test (2e moitié) — A contre D : -0.28 $ / signal, IC 90 % [-2.39 ; +1.76].
- Test (2e moitié) — B contre D : +7.05 $ / signal, IC 90 % [+0.69 ; +13.89].
- Test (2e moitié) — C = R4 contre D : +6.76 $ / signal, IC 90 % [-0.53 ; +14.77].
- Prédicteur de non-retour : voir l'AUC test et son IC ci-dessus (≥ 0,5 + IC strictement au-dessus de 0,5 = information réelle).

## Limites
- Une journée, ~15 cycles de test : faible puissance.
- Modèle recalculé hors ligne (fidèle à ±0,005 pour ~3/4 des signaux).
- Les variantes du même cycle ne sont pas indépendantes (IC par cycles).
