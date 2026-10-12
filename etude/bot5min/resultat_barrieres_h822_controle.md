# Bot95 — Fusion Engine F1 : H822 à H832 — barrières, figures de liquidité et règlement (CONTRÔLE, apprentissage seul)

Généré le 12.10.2026 10:40 UTC. BTCUSDT 1 s Binance du 12.09.2026 au 11.10.2026 23:59 UTC. Apprentissage < 02.10.2026 ; test 02.10 → 11.10. Open interest : disponible (5 min). Profondeur loin du prix et liquidations : non mesurables. Aucun ordre ; H816, H821, R4, fantômes inchangés ; période réservée non lue.

## 0. Substitut du règlement
Résultat Binance (moyennes 60 s) contre résultat officiel Polymarket : **95.8 %** d'accord sur 636 cycles ; désaccords seulement quand |F − K| < 5 $ (77 % d'accord sous 5 $, 100.0 % au-dessus).

## 1. H823 — Que se passe-t-il au contact d'un niveau ?

Contact = le prix arrive à ± tol (≈ 16 $) d'un niveau après en avoir été à ≥ 3 tol. Résultat à 60 s : cassure (> 1 tol au-delà), rejet (> 2 tol en deçà), fausse cassure (passé au-delà puis revenu). Placebo = mêmes règles sur des niveaux fictifs décalés.

| Échantillon | Type de niveau | Contacts | Rejet | Cassure | Fausse cassure | Rejet en excès vs placebo (IC 90 % par jours) | Mouvement médian 5 / 10 / 20 / 30 / 60 s (tol, sens de l'approche) |
|---|---|---|---|---|---|---|---|
| apprentissage | rond 1000 | 952 | 32 % | 27 % | 16 % | +0.9 pts [-2.8 ; +4.2] | -0.6 / -0.5 / -0.5 / -0.4 / -0.7 |
| apprentissage | rond 500 | 941 | 32 % | 28 % | 14 % | +1.1 pts [-1.0 ; +3.4] | -0.6 / -0.6 / -0.6 / -0.5 / -0.6 |
| apprentissage | rond 100 | 7126 | 32 % | 31 % | 16 % | +0.9 pts [-0.1 ; +2.0] | -0.6 / -0.5 / -0.5 / -0.5 / -0.5 |
| apprentissage | pivot — 2e contact (double) | 7138 | 21 % | 21 % | 8 % | -6.0 pts [-7.9 ; -4.0] | -0.6 / -0.6 / -0.5 / -0.5 / -0.5 |
| apprentissage | pivot — 3e contact et plus (triple) | 22252 | 26 % | 26 % | 10 % | -1.6 pts [-2.6 ; -0.7] | -0.6 / -0.5 / -0.5 / -0.5 / -0.5 |
| apprentissage | pivot | 29390 | 25 % | 25 % | 10 % | -2.6 pts [-3.8 ; -1.7] | -0.6 / -0.6 / -0.5 / -0.5 / -0.5 |
| apprentissage | placebo rond | 9076 | 31 % | 31 % | 15 % | — | -0.6 / -0.5 / -0.5 / -0.4 / -0.4 |
| apprentissage | placebo pivot — 2e contact (double) | 5538 | 25 % | 25 % | 10 % | — | -0.6 / -0.6 / -0.5 / -0.5 / -0.5 |
| apprentissage | placebo pivot — 3e contact et plus (triple) | 18112 | 28 % | 27 % | 12 % | — | -0.6 / -0.5 / -0.5 / -0.5 / -0.5 |
| apprentissage | placebo pivot | 23650 | 27 % | 26 % | 11 % | — | -0.6 / -0.5 / -0.5 / -0.5 / -0.5 |

Probabilités de rejet en excès retenues pour H822 (apprentissage, seulement si l'IC exclut 0) : aucune.

## 2. H825 — Prévoir cassure, rejet et fausse cassure avant le contact

| Cible | Niveaux | AUC test (IC 90 % par jours) | Taux de base test |
|---|---|---|---|

Lecture : un niveau n'apporte une information propre que si l'AUC sur les niveaux réels dépasse nettement celle des placebos.

## 3. Figures potentielles (H827–H832) : fréquence et effet sur le résultat officiel (substitut), apprentissage

| Figure | Décisions où elle est présente | Victoire Up quand haussière / baissière | Probabilité M0 moyenne quand haussière / baissière |
|---|---|---|---|
| double sommet | 3830 | — / 63 % | — / 64 % |
| triple sommet | 3409 | — / 67 % | — / 67 % |
| double creux | 3632 | 37 % / — | 36 % / — |
| triple creux | 3474 | 34 % / — | 33 % / — |
| sommets egaux | 9774 | — / 55 % | — / 55 % |
| creux egaux | 9799 | 46 % / — | 45 % / — |
| balayage | 5375 | 68 % / 34 % | 68 % / 32 % |
| fausse cassure | 7801 | 79 % / 21 % | 80 % / 20 % |
| cassure retest | 6541 | 27 % / 74 % | 26 % / 74 % |
| compression | 14869 | 52 % / 51 % | 51 % / 50 % |

Coefficients du modèle avec figures (logit, appris) : const -0.004, logit M0 +0.643, double_sommet +0.031, triple_sommet -0.053, double_creux -0.048, triple_creux +0.001, sommets_egaux -0.054, creux_egaux +0.004, balayage +0.004, fausse_cassure +0.122, cassure_retest -0.182, compression +0.047, obstacle majeur +0.013, obstacle +0.097

_Contrôle : arrêt avant le test._
