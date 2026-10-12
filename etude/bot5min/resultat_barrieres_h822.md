# Bot95 — Fusion Engine F1 : H822 à H832 — barrières, figures de liquidité et règlement (apprentissage → test)

Généré le 12.10.2026 10:41 UTC. BTCUSDT 1 s Binance du 12.09.2026 au 11.10.2026 23:59 UTC. Apprentissage < 02.10.2026 ; test 02.10 → 11.10. Open interest : disponible (5 min). Profondeur loin du prix et liquidations : non mesurables. Aucun ordre ; H816, H821, R4, fantômes inchangés ; période réservée non lue.

## 0. Substitut du règlement
Résultat Binance (moyennes 60 s) contre résultat officiel Polymarket : **95.8 %** d'accord sur 636 cycles ; désaccords seulement quand |F − K| < 5 $ (77 % d'accord sous 5 $, 100.0 % au-dessus).

## 1. H823 — Que se passe-t-il au contact d'un niveau ?

Contact = le prix arrive à ± tol (≈ 16 $) d'un niveau après en avoir été à ≥ 3 tol. Résultat à 60 s : cassure (> 1 tol au-delà), rejet (> 2 tol en deçà), fausse cassure (passé au-delà puis revenu). Placebo = mêmes règles sur des niveaux fictifs décalés.

| Échantillon | Type de niveau | Contacts | Rejet | Cassure | Fausse cassure | Rejet en excès vs placebo (IC 90 % par jours) | Mouvement médian 5 / 10 / 20 / 30 / 60 s (tol, sens de l'approche) |
|---|---|---|---|---|---|---|---|
| apprentissage | rond 1000 | 952 | 32 % | 27 % | 16 % | +0.6 pts [-2.9 ; +3.5] | -0.6 / -0.5 / -0.5 / -0.4 / -0.7 |
| apprentissage | rond 500 | 941 | 32 % | 28 % | 14 % | +0.7 pts [-1.6 ; +3.3] | -0.6 / -0.6 / -0.6 / -0.5 / -0.6 |
| apprentissage | rond 100 | 7126 | 32 % | 31 % | 16 % | +0.5 pts [-0.6 ; +1.7] | -0.6 / -0.5 / -0.5 / -0.5 / -0.5 |
| apprentissage | pivot — 2e contact (double) | 7138 | 21 % | 21 % | 8 % | -6.0 pts [-8.0 ; -3.9] | -0.6 / -0.6 / -0.5 / -0.5 / -0.5 |
| apprentissage | pivot — 3e contact et plus (triple) | 22252 | 26 % | 26 % | 10 % | -1.6 pts [-2.6 ; -0.7] | -0.6 / -0.5 / -0.5 / -0.5 / -0.5 |
| apprentissage | pivot | 29390 | 25 % | 25 % | 10 % | -2.6 pts [-3.8 ; -1.7] | -0.6 / -0.6 / -0.5 / -0.5 / -0.5 |
| apprentissage | placebo rond | 9066 | 31 % | 31 % | 15 % | — | -0.6 / -0.5 / -0.5 / -0.5 / -0.5 |
| apprentissage | placebo pivot — 2e contact (double) | 5538 | 25 % | 25 % | 10 % | — | -0.6 / -0.6 / -0.5 / -0.5 / -0.5 |
| apprentissage | placebo pivot — 3e contact et plus (triple) | 18112 | 28 % | 27 % | 12 % | — | -0.6 / -0.5 / -0.5 / -0.5 / -0.5 |
| apprentissage | placebo pivot | 23650 | 27 % | 26 % | 11 % | — | -0.6 / -0.5 / -0.5 / -0.5 / -0.5 |
| test | rond 1000 | 342 | 28 % | 33 % | 13 % | -2.5 pts [-8.3 ; +3.0] | -0.7 / -0.6 / -0.6 / -0.6 / -0.4 |
| test | rond 500 | 328 | 36 % | 19 % | 16 % | +5.4 pts [-1.5 ; +11.3] | -0.8 / -0.7 / -0.8 / -0.8 / -1.1 |
| test | rond 100 | 2523 | 30 % | 29 % | 16 % | -0.6 pts [-1.6 ; +0.3] | -0.6 / -0.6 / -0.5 / -0.5 / -0.6 |
| test | pivot — 2e contact (double) | 3781 | 15 % | 16 % | 5 % | -8.7 pts [-12.7 ; -4.8] | -0.7 / -0.7 / -0.6 / -0.6 / -0.6 |
| test | pivot — 3e contact et plus (triple) | 8494 | 21 % | 20 % | 8 % | -3.1 pts [-4.9 ; -1.6] | -0.7 / -0.6 / -0.6 / -0.6 / -0.5 |
| test | pivot | 12275 | 19 % | 19 % | 7 % | -4.8 pts [-7.3 ; -2.6] | -0.7 / -0.6 / -0.6 / -0.6 / -0.5 |
| test | placebo rond | 3206 | 30 % | 27 % | 16 % | — | -0.6 / -0.6 / -0.5 / -0.6 / -0.6 |
| test | placebo pivot — 2e contact (double) | 2651 | 24 % | 19 % | 11 % | — | -0.7 / -0.6 / -0.6 / -0.6 / -0.6 |
| test | placebo pivot — 3e contact et plus (triple) | 6474 | 24 % | 23 % | 11 % | — | -0.6 / -0.6 / -0.6 / -0.5 / -0.6 |
| test | placebo pivot | 9125 | 24 % | 22 % | 11 % | — | -0.6 / -0.6 / -0.6 / -0.6 / -0.6 |

Probabilités de rejet en excès retenues pour H822 (apprentissage, seulement si l'IC exclut 0) : aucune.

## 2. H825 — Prévoir cassure, rejet et fausse cassure avant le contact

| Cible | Niveaux | AUC test (IC 90 % par jours) | Taux de base test |
|---|---|---|---|
| rejet | réels | 0.661 [0.632 ; 0.683] | 21 % |
| rejet | placebo | 0.648 [0.627 ; 0.668] | 26 % |
| cassure | réels | 0.646 [0.613 ; 0.673] | 21 % |
| cassure | placebo | 0.605 [0.582 ; 0.627] | 23 % |
| fausse cassure | réels | 0.767 [0.739 ; 0.794] | 9 % |
| fausse cassure | placebo | 0.725 [0.711 ; 0.739] | 12 % |

Lecture : un niveau n'apporte une information propre que si l'AUC sur les niveaux réels dépasse nettement celle des placebos.

## 3. Figures potentielles (H827–H832) : fréquence et effet sur le résultat officiel (substitut), apprentissage

| Figure | Décisions où elle est présente | Victoire Up quand haussière / baissière | Probabilité M0 moyenne quand haussière / baissière |
|---|---|---|---|
| double sommet | 3830 | — / 63 % | — / 64 % |
| triple sommet | 3410 | — / 67 % | — / 67 % |
| double creux | 3632 | 37 % / — | 36 % / — |
| triple creux | 3474 | 34 % / — | 33 % / — |
| sommets egaux | 9777 | — / 55 % | — / 55 % |
| creux egaux | 9799 | 46 % / — | 45 % / — |
| balayage | 5375 | 68 % / 34 % | 68 % / 32 % |
| fausse cassure | 7801 | 79 % / 21 % | 80 % / 20 % |
| cassure retest | 6541 | 27 % / 74 % | 26 % / 74 % |
| compression | 14870 | 52 % / 51 % | 51 % / 50 % |

Coefficients du modèle avec figures (logit, appris) : const -0.004, logit M0 +0.643, double_sommet +0.031, triple_sommet -0.052, double_creux -0.048, triple_creux +0.001, sommets_egaux -0.055, creux_egaux +0.004, balayage +0.004, fausse_cassure +0.122, cassure_retest -0.182, compression +0.047, obstacle majeur +0.013, obstacle +0.097

## 4. H822 / H827–H832 — Le modèle avec barrières ou figures prévoit-il mieux le résultat officiel ? (test, décisions synthétiques)

**Toutes les décisions** (17274 décisions, 2879 cycles)

| Modèle | Brier | Log loss | Précision directionnelle | Brier − référence M0* | IC 90 % | IC corrigé (4 comparaisons) |
|---|---|---|---|---|---|---|
| M0 règlement seul | 0.1084 | 0.3546 | 84.5 % | +0.00027 | [-0.00048 ; +0.00105] | [-0.00071 ; +0.00131] |
| M0* recalibré (référence) | 0.1081 | 0.3382 | 84.6 % | — | — | — |
| MC0 trajectoires sans barrières | 0.1085 | 0.3480 | 84.3 % | +0.00044 | [-0.00030 ; +0.00124] | [-0.00051 ; +0.00143] |
| MCB trajectoires avec barrières (H822) | 0.1085 | 0.3480 | 84.3 % | +0.00044 | [-0.00029 ; +0.00119] | [-0.00060 ; +0.00143] |
| MF avec figures et obstacles (H827–H832) | 0.1084 | 0.3388 | 84.4 % | +0.00029 | [-0.00015 ; +0.00074] | [-0.00033 ; +0.00091] |

**Marge faible |z| < 0,5** (3460 décisions, 1745 cycles)

| Modèle | Brier | Log loss | Précision directionnelle | Brier − référence M0* | IC 90 % | IC corrigé (4 comparaisons) |
|---|---|---|---|---|---|---|
| M0 règlement seul | 0.2383 | 0.6695 | 59.6 % | -0.00154 | [-0.00258 ; -0.00051] | [-0.00293 ; -0.00013] |
| M0* recalibré (référence) | 0.2399 | 0.6727 | 60.0 % | — | — | — |
| MC0 trajectoires sans barrières | 0.2394 | 0.6717 | 58.6 % | -0.00050 | [-0.00179 ; +0.00079] | [-0.00220 ; +0.00125] |
| MCB trajectoires avec barrières (H822) | 0.2394 | 0.6717 | 58.6 % | -0.00050 | [-0.00177 ; +0.00082] | [-0.00224 ; +0.00128] |
| MF avec figures et obstacles (H827–H832) | 0.2410 | 0.6750 | 59.0 % | +0.00109 | [-0.00080 ; +0.00304] | [-0.00154 ; +0.00380] |

**Calibration (test)**

| Probabilité annoncée | Décisions | M0* : victoire observée | MF : victoire observée |
|---|---|---|---|
| 0.0–0.1 | 4052 / 4057 | 2 % | 2 % |
| 0.1–0.3 | 2062 / 2102 | 17 % | 17 % |
| 0.3–0.5 | 2192 / 2374 | 36 % | 38 % |
| 0.5–0.7 | 2667 / 2394 | 62 % | 62 % |
| 0.7–0.9 | 1974 / 2014 | 84 % | 83 % |
| 0.9–1.0 | 4327 / 4333 | 98 % | 98 % |

## 5. H824 — Marge de sécurité dynamique

P(le côté en tête gagne) apprise en fonction de |z|, avec et sans obstacle majeur devant le prix (dans le sens d'un retour vers le prix à battre). Marge |z| nécessaire pour 90 % et 95 %, par temps restant (apprentissage), puis taux observé sur le test au-delà de cette marge.

| Temps restant | Obstacle | Marge pour 90 % | Taux test au-delà | Marge pour 95 % | Taux test au-delà |
|---|---|---|---|---|---|
| 240 s | non | 1.93 σ | 93.9 % (82) | 2.59 σ | 86.7 % (15) |
| 240 s | oui | 1.89 σ | 94.6 % (56) | 2.57 σ | 100.0 % (8) |
| 180 s | non | 1.93 σ | 94.5 % (271) | 2.63 σ | 94.8 % (96) |
| 180 s | oui | 1.94 σ | 93.2 % (278) | 2.63 σ | 96.0 % (101) |
| 120 s | non | 1.83 σ | 96.7 % (607) | 2.47 σ | 97.8 % (402) |
| 120 s | oui | 1.85 σ | 94.7 % (628) | 2.58 σ | 96.9 % (386) |
| 90 s | non | 1.79 σ | 97.7 % (857) | 2.49 σ | 98.8 % (653) |
| 90 s | oui | 1.87 σ | 96.1 % (785) | 2.65 σ | 97.2 % (572) |
| 60 s | non | 1.63 σ | 98.4 % (1154) | 2.33 σ | 98.8 % (1014) |
| 60 s | oui | 1.77 σ | 98.1 % (976) | 2.66 σ | 98.6 % (845) |
| 30 s | non | 1.38 σ | 99.8 % (1524) | 2.02 σ | 99.8 % (1489) |
| 30 s | oui | 1.15 σ | 99.9 % (1147) | 2.35 σ | 100.0 % (1077) |

## 6. H826 (et figures H827–H832 en veto) — sur les vraies décisions Bot95

U1 = fantômes Cloudflare (première décision par cycle × côté, 20 $ au prix enregistré) : apprentissage 413, test 1099. U2 = H816 Dublin du 11.10 à 164 ms : 64 décisions (test).

| Règle (obstacle × marge m) | Gain apprentissage U1 ($) | Gain test U1 ($) |
|---|---|---|
| obstacle majeur, z < 0.5 | +119 | inadmissible |
| obstacle majeur, z < 1.0 | +110 | inadmissible |
| obstacle quelconque, z < 0.5 | inadmissible | inadmissible |
| obstacle quelconque, z < 1.0 | inadmissible | inadmissible |
| double/triple contraire, z < 0.5 | -102 | -197 |
| double/triple contraire, z < 1.0 | -144 | -351 |
| balayage contraire, z < 0.5 | +126 | +382 |
| balayage contraire, z < 1.0 | +126 | +382 |
| fausse cassure contraire, z < 0.5 | -130 | +663 |
| fausse cassure contraire, z < 1.0 | -130 | +663 |
| compression devant, z < 0.5 | +362 | +398 |
| compression devant, z < 1.0 | +367 | +350 |

**Règle retenue sur l'apprentissage : compression devant, z < 1.0.**

| Échantillon | Décisions | Gardées | Perdants évités | Gagnants supprimés | Jackpots supprimés | P&L base ($) | P&L avec veto ($) | Marginal ($) | IC 90 % par décision | IC corrigé (12) | Drawdown base / veto |
|---|---|---|---|---|---|---|---|---|---|---|---|
| apprentissage U1 | 413 | 339 | 52 | 22 | 6 | -365 | +1 | +367 | [-0.05 ; +1.79] | [-0.70 ; +2.31] | 878 / 663 |
| TEST U1 | 1099 | 850 | 180 | 69 | 43 | -2955 | -2604 | +350 | [-0.65 ; +1.20] | [-1.25 ; +1.60] | 3068 / 2909 |
| TEST U2 (H816, 164 ms) | 64 | 43 | 16 | 4 | 2 | +283 | +407 | +124 | [-1.45 ; +4.91] | [-3.84 ; +6.69] | 119 / 79 |

**Marge faible seulement (z du côté parié < 0,5), test U1** : décisions, taux de gain, P&L selon la présence d'un obstacle majeur devant.

| Obstacle majeur devant | Décisions | Taux de gain | Prix moyen | P&L ($) |
|---|---|---|---|---|
| non | 363 | 25 % | 0.25 | -700 |
| oui | 618 | 25 % | 0.29 | -2391 |

## Limites
- Règlement reconstruit avec Binance (accord 95.8 % avec l'officiel, désaccords sous 5 $ d'écart).
- Profondeur loin du prix, rechargement / retrait de profondeur et liquidations : non disponibles en historique, non mesurés.
- Open interest : 5 min seulement, trop grossier pour 5–60 s.
- U1 : prix enregistrés par les fantômes Cloudflare (exécution moins réaliste que U2). U2 : une seule journée.
- Nombreuses comparaisons : seuls les IC corrigés permettent de conclure.

_Calcul : 67 s._
