# Bot95 — R4 « retry engine », H776–H778 — PRÉLIMINAIRE (hors ligne)

Généré le 11.10.2026 15:28 UTC. 157 signaux réglés sur 31 cycles enregistrés à Dublin (avant le 13.10). IC 90 % par rééchantillonnage de cycles ; 1re moitié = cycles < 10:55 UTC. Envoi à la décision puis toutes les 500 ms, exécution 164 ms après chaque envoi, budget 50 $, frais preneur. Condition R4 : probabilité recalculée − prix − frais ≥ 0.05. Le fantôme R4 vivant (déployé à Dublin le 11.10 vers 15:30 UTC) donnera la mesure réellement hors échantillon.

## 1. R4 contre Bot95 actuel et les relances demandées (livrables 1 à 6)

| Politique | Signaux remplis | Parts | Prix moyen | P&L ($) | / signal (IC 90 %) | P&L marginal vs Bot95 | 1re / 2e moitié | Drawdown | Jackpots | Offres récupérées | Nouveaux perdants |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Bot95 preneur immédiat (164 ms, prix du signal) | 128 | 23616 | 0.184 | +4580 | +29.17 [+7.78 ; +54.53] | +0 | +9.77 / +47.84 | 767 | 24 | 0 | 0 |
| relance 5 s au prix initial | 132 | 35193 | 0.160 | +5088 | +32.41 [+5.04 ; +61.30] | +508 | +12.01 / +52.04 | 990 | 25 | 5 | 3 |
| relance 5 s, +1 c | 137 | 36032 | 0.166 | +5029 | +32.03 [+6.90 ; +58.78] | +449 | +10.12 / +53.12 | 1013 | 25 | 10 | 8 |
| **R4 : relance 5 s, +2 c, recalcul** | 137 | 36773 | 0.169 | +5341 | +34.02 [+7.60 ; +60.72] | +761 | +11.64 / +55.56 | 939 | 25 | 10 | 8 |
| relance 5 s, +2 c, modèle figé | 138 | 37246 | 0.169 | +5754 | +36.65 [+8.75 ; +69.00] | +1174 | +11.78 / +60.58 | 929 | 26 | 10 | 8 |
| relance 5 s, +2 c, sans condition | 138 | 37246 | 0.169 | +5754 | +36.65 [+7.94 ; +66.21] | +1174 | +11.78 / +60.58 | 929 | 26 | 10 | 8 |

- **Offres récupérées** (Bot95 n'a rien eu, R4 a acheté) : 10 signaux ; gagnants 2, perdants 8 ; jackpots récupérés (gain à prix ≤ 0,25) : 2.
- **Quantité récupérée** (parts achetées en plus de Bot95, tous signaux) : 13628 parts pour 1937 $ (**coût des relances**) ; résultat de ces parts : +1181 $.
- Signaux où R4 achète MOINS que Bot95 (la condition d'avantage recalculée refuse) : 1 ; P&L laissé : +420 $ (gagnants 1, perdants 0).
- P&L marginal R4 − Bot95 par signal : +4.85 $, IC 90 % [-3.46 ; +12.93].
- Décisions uniques (1 par cycle et côté, 45) — Bot95 : +965 $, +21.45 / décision [+4.78 ; +39.04].
- Décisions uniques (1 par cycle et côté, 45) — R4 : +1008 $, +22.39 / décision [+5.87 ; +39.56].

## 2. H778 — Résultats par durée de relance et par plafond (livrables 7, 8) — avec condition et recalcul

| Durée | +0 c | +1 c | +2 c | +3 c |
|---|---|---|---|---|
| 1 s | +4158 $ (128 remplis ; 2e m. +43.1) | +4882 $ (135 remplis ; 2e m. +51.0) | +5141 $ (135 remplis ; 2e m. +53.9) | +5341 $ (137 remplis ; 2e m. +55.8) |
| 2 s | +4850 $ (130 remplis ; 2e m. +48.3) | +4936 $ (135 remplis ; 2e m. +52.6) | +5245 $ (135 remplis ; 2e m. +55.2) | +5321 $ (137 remplis ; 2e m. +55.8) |
| 3 s | +4852 $ (132 remplis ; 2e m. +48.9) | +4947 $ (137 remplis ; 2e m. +53.3) | +5280 $ (137 remplis ; 2e m. +55.7) | +5366 $ (139 remplis ; 2e m. +56.4) |
| 5 s | +5088 $ (132 remplis ; 2e m. +52.0) | +5029 $ (137 remplis ; 2e m. +53.1) | +5341 $ (137 remplis ; 2e m. +55.6) | +5386 $ (139 remplis ; 2e m. +56.1) |

| Une seule tentative (164 ms), sans condition | +4580 $ | +4731 $ | +5261 $ | +5576 $ |

Lecture : la grille est descriptive ; aucun paramètre n'est choisi sur elle (R4 = 5 s, +2 c fixé par Pitch avant la mesure).

## 3. Effet du recalcul du modèle (livrable 9)

| Durée / plafond | recalcul | modèle figé au signal | sans condition |
|---|---|---|---|
| 1 s, +2 c | +5141 $ | +5627 $ | +5627 $ |
| 2 s, +2 c | +5245 $ | +5731 $ | +5731 $ |
| 5 s, +0 c | +5088 $ | +5490 $ | +5490 $ |
| 5 s, +2 c | +5341 $ | +5754 $ | +5754 $ |

Dérive de la probabilité recalculée par rapport à celle du signal pendant les 5 s : médiane -0.000, 10e/90e centiles -0.070 / +0.081. (Modèle recalculé fidèle à ±0,005 pour ~3/4 des signaux.)

## 4. H776 — Réapparition des offres après disparition

Offre au prix du signal disparue dans les 5 s : 110 / 157 signaux.

| Retour | Signaux | Délai médian (ms) | Prix médian au retour | Quantité médiane | Profondeur médiane (≤ +3 c) | Probabilité recalculée médiane − prix | Taux de gain |
|---|---|---|---|---|---|---|---|
| ≤ prix + 0 c | 36 | 1162 | 0.21 | 72 | 1168 | +0.232 | 53 % |
| ≤ prix + 1 c | 70 | 25 | 0.23 | 54 | 333 | +0.201 | 41 % |
| ≤ prix + 2 c | 83 | 25 | 0.22 | 67 | 257 | +0.203 | 41 % |
| jamais revenue (≤ +2 c) | 27 | — | — | — | — | — | 81 % |

## 5. H777 — Relance systématique contre conditionnelle

Probabilité de réapparition (≤ +2 c en 5 s) apprise sur la 1re moitié : prix < 0,15 → 0.67 ; 0,15–0,30 → 0.85 ; ≥ 0,30 → 0.82.

| Politique (2e moitié seulement) | Remplis | P&L ($) | / signal | IC 90 % |
|---|---|---|---|---|
| Bot95 immédiat | 59 | +3827 | +47.84 | [+8.48 ; +90.04] |
| relance systématique 5 s +2 c (sans condition) | 66 | +4847 | +60.58 | [+16.81 ; +110.55] |
| relance conditionnelle à l'avantage net (R4) | 65 | +4445 | +55.56 | [+13.14 ; +96.85] |
| relance si réapparition probable (≥ 0,5) | 65 | +4445 | +55.56 | [+15.28 ; +96.56] |

## 6. Comparaison avec M4 et M8 (mêmes cycles, fantômes vivants)

16 cycles communs.

| Moteur | P&L ($) |
|---|---|
| M4 (vivant, prudent / proportionnel) | +190 / +400 |
| M8 (vivant, prudent / proportionnel) | +453 / +453 |
| Bot95 immédiat (simulé) | +3827 |
| R4 (simulé) | +4445 |

## 7. Verdict statistique (livrable 10)

- R4 +5341 $ contre Bot95 +4580 $ ; différence +761 $ ; IC 90 % de la différence par signal [-3.46 ; +12.93] → **amélioration NON démontrée (l’IC contient 0)**.
- 1re moitié : Bot95 +9.77 / R4 +11.64 par signal ; 2e moitié : Bot95 +47.84 / R4 +55.56.
- Quelle que soit l'issue ici, seule la mesure du fantôme R4 vivant sur des cycles nouveaux (et la période réservée du 13.10) compte comme validation.

## Limites
- Une journée, peu de cycles, résultats portés par quelques gros gains.
- Modèle recalculé hors ligne (fidèle à ±0,005 pour ~3/4 des signaux).
- Carnet suivi à ±3 c du meilleur prix entre deux photos complètes.
- La relance n'affecte pas le carnet (fantôme) : en réel, nos achats déplaceraient le prix.
