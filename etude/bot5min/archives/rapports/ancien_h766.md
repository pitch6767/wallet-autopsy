# Bot95 — H766 à H775 : capturer l'avantage malgré la latence ? — PRÉLIMINAIRE

Généré le 11.10.2026 15:17 UTC. Cycles enregistrés à Dublin avant le 13.10 : 51 ; signaux Bot95 réglés sur ces cycles : **157** sur **31 cycles**. IC 90 % par rééchantillonnage de cycles. Validation chronologique : 1re moitié = cycles < 10:55 UTC, 2e moitié après. Exécution preneur : décision + 14 ms de trajet + 150 ms de retard Polymarket = 164 ms. Budget 50 $ par signal (comme Dublin). Aucun ordre, aucun fantôme touché.

## 0. Contrôle de la reconstruction du carnet

- 0 ms : quantité achetable reconstruite = quantité vue par Dublin (± 5 %) dans 100 % des 157 signaux.
- 50 ms : quantité achetable reconstruite = quantité vue par Dublin (± 5 %) dans 89 % des 157 signaux.
- 100 ms : quantité achetable reconstruite = quantité vue par Dublin (± 5 %) dans 89 % des 157 signaux.
- 250 ms : quantité achetable reconstruite = quantité vue par Dublin (± 5 %) dans 95 % des 157 signaux.
- 500 ms : quantité achetable reconstruite = quantité vue par Dublin (± 5 %) dans 96 % des 157 signaux.

## 1. H766 — P&L et quantité exécutable selon la latence (preneur, prix du signal, plafond +0) — livrables « courbe P&L/latence », « quantités capturables », « P&L par signal initial »

P&L par **signal initial** = résultat en $ de ce que l'on aurait réellement pu acheter (0 si rien), frais compris, puis moyenne sur tous les signaux.

| Délai | Signaux exécutables | Parts / parts à 0 ms | P&L total ($) | P&L moyen par signal ($) | IC 90 % | par $ investi | 1re moitié / signal | 2e moitié / signal |
|---|---|---|---|---|---|---|---|---|
| 0 ms (mesure Dublin) | 157 / 157 | 100 % | +5635 | +35.89 | [+15.30 ; +59.57] | +182.0 % | +14.07 | +56.89 |
| 25 ms | 144 / 157 | 124 % | +5688 | +36.23 | [+11.91 ; +61.62] | +144.6 % | +13.09 | +58.50 |
| 50 ms | 143 / 157 | 134 % | +5655 | +36.02 | [+11.64 ; +61.80] | +132.3 % | +13.67 | +57.54 |
| 100 ms | 135 / 157 | 139 % | +4928 | +31.39 | [+9.43 ; +57.47] | +111.5 % | +7.64 | +54.25 |
| 150 ms | 131 / 157 | 142 % | +4723 | +30.08 | [+7.66 ; +54.09] | +104.6 % | +10.30 | +49.13 |
| 164 ms (preneur réel) | 128 / 157 | 140 % | +4670 | +29.74 | [+5.95 ; +56.94] | +105.7 % | +9.34 | +49.38 |
| 250 ms | 107 / 157 | 131 % | +4127 | +26.29 | [+4.81 ; +49.10] | +103.2 % | +9.38 | +42.56 |
| 300 ms | 102 / 157 | 127 % | +3824 | +24.35 | [+4.30 ; +44.83] | +98.7 % | +8.77 | +39.35 |
| 500 ms | 96 / 157 | 118 % | +3039 | +19.36 | [+2.82 ; +37.46] | +85.5 % | +7.80 | +30.48 |

**Robustesse (preneur 164 ms, plafond +0)** — le résultat dépend-il de quelques gros gains ?

- Médiane par signal : +0.00 $ ; part du P&L total venant des 5 meilleurs signaux : 52 % ; P&L sans les 5 meilleurs : +2225 $ ; sans les 10 meilleurs : +963 $.
- **Décisions uniques** (un seul achat par cycle et par côté — le premier signal ; les variantes du même cycle achètent souvent le même billet) : 45 décisions, P&L +983 $, moyen +21.84 $ IC 90 % [+3.91 ; +39.60], médiane +0.00 $.

| Prix du signal | Signaux | Taux de gain | P&L 0 ms ($) | P&L 164 ms ($) | P&L 500 ms ($) | perte due à la latence 0→164 ms |
|---|---|---|---|---|---|---|
| 0.00–0.10 | 13 | 31 % | +1426 | +1545 | +1476 | +119 |
| 0.10–0.20 | 48 | 31 % | +1657 | +877 | -111 | -780 |
| 0.20–0.35 | 80 | 48 % | +1968 | +2052 | +1635 | +83 |
| 0.35–1.00 | 16 | 75 % | +583 | +196 | +39 | -387 |

## 2. H768 — Latence critique

- Premier délai où l'espérance moyenne par signal devient ≤ 0 : **aucun jusqu’à 500 ms**.
- Premier délai où l'IC 90 % est entièrement négatif : **aucun jusqu’à 500 ms**.
- Premier délai où l'IC 90 % ne contient plus que du positif : 0 ms, 25 ms, 50 ms, 100 ms, 150 ms, 164 ms, 250 ms, 300 ms, 500 ms.

## 3. H767 — Pourquoi les offres disparaissent (livrable « analyse des offres disparues »)

Pour chaque signal : baisse des quantités vendues au prix du signal ou mieux entre la décision et +250 ms (puis +500 ms), et transactions qui consomment ce côté à ces prix (reçues jusqu'à 60 ms après). Consommé = min(baisse, transactions) ; retiré = le reste ; **indéterminé** si un carnet complet est rechargé dans la fenêtre ou si le flux est coupé (aucune attribution inventée).

| Cause | Signaux | Parts consommées | Parts retirées | Taux de gain du signal |
|---|---|---|---|---|
| pas disparue (≥ 50 % encore là à 250 ms) | 93 | 1524 | 25791 | 33 % |
| retirée (annulation) | 46 | 710 | 6401 | 63 % |
| indéterminé (carnet rechargé / flux coupé) | 14 | 212 | 798 | 50 % |
| consommée par des transactions | 4 | 328 | 0 | 50 % |

Lecture : « consommée » = un autre preneur a acheté avant nous (course de vitesse) ; « retirée » = le vendeur a annulé (il a vu le même mouvement).

## 4. H769 — Prix plafond (livrable « gain marginal des prix plafonds »)

| Délai | Plafond | Signaux exécutables | Parts | P&L total ($) | P&L moyen / signal | IC 90 % | Gain marginal vs +0 ($) | 2e moitié / signal |
|---|---|---|---|---|---|---|---|---|
| 164 ms | +0 c | 128 | 24003 | +4670 | +29.74 | [+5.70 ; +55.21] | +0 | +49.38 |
| 164 ms | +1 c | 135 | 29720 | +4779 | +30.44 | [+2.28 ; +58.01] | +109 | +52.04 |
| 164 ms | +2 c | 136 | 33267 | +5313 | +33.84 | [+5.09 ; +64.10] | +643 | +56.25 |
| 164 ms | +3 c | 138 | 35642 | +5801 | +36.95 | [+7.51 ; +70.57] | +1131 | +60.54 |
| 250 ms | +0 c | 107 | 22365 | +4127 | +26.29 | [+5.24 ; +49.50] | +0 | +42.56 |
| 250 ms | +1 c | 117 | 28384 | +4460 | +28.41 | [+1.35 ; +56.51] | +333 | +49.76 |
| 250 ms | +2 c | 122 | 31474 | +4645 | +29.58 | [+2.56 ; +58.48] | +518 | +51.30 |
| 250 ms | +3 c | 124 | 33691 | +4940 | +31.47 | [+4.22 ; +59.95] | +813 | +54.44 |
| 500 ms | +0 c | 96 | 20132 | +3039 | +19.36 | [+2.23 ; +38.81] | +0 | +30.48 |
| 500 ms | +1 c | 110 | 27031 | +3380 | +21.53 | [-0.82 ; +44.09] | +341 | +39.12 |
| 500 ms | +2 c | 112 | 30396 | +3518 | +22.40 | [-0.46 ; +45.29] | +479 | +40.61 |
| 500 ms | +3 c | 116 | 32667 | +3828 | +24.38 | [-0.24 ; +49.87] | +789 | +41.77 |

## 5. H774 — Alpha sans poursuite (abandon / deuxième chance / attente)

Achat seulement tant que modèle (figé au signal) − prix − frais ≥ 0,05.

| Politique | Signaux exécutés | Parts | P&L total ($) | moyen / signal | IC 90 % | 2e moitié / signal |
|---|---|---|---|---|---|---|
| abandon immédiat (164 ms, +0) | 128 | 24003 | +4670 | +29.74 | [+6.51 ; +57.72] | +49.38 |
| deuxième chance (+164 ms puis 500 ms, plafond +2 c) | 134 | 25655 | +4890 | +31.15 | [+6.72 ; +57.14] | +54.19 |
| attente : relances 5 s au prix du signal | 133 | 35700 | +5634 | +35.88 | [+6.26 ; +66.98] | +58.61 |
| attente : relances 5 s, plafond +2 c | 138 | 39072 | +6013 | +38.30 | [+8.64 ; +70.47] | +63.23 |

## 6. H770 — Maker contre preneur sur les mêmes signaux

Maker simulé : offre d'achat posée à décision + 14 ms au meilleur acheteur (+1 c si l'écart > 1 c, règle de M1), retirée après 10 s ou 60 s ; file d'attente : prudente (seules les transactions nous font avancer), centrale (annulations réparties), optimiste (toutes les annulations devant nous). Gardé jusqu'au règlement, sans frais (maker).

| Voie | Signaux remplis | Parts | P&L total ($) | moyen / signal | IC 90 % | Taux de gain des remplis | 2e moitié / signal |
|---|---|---|---|---|---|---|---|
| preneur 164 ms (Bot95 actuel) | 128 | 24003 | +4670 | +29.74 | [+6.21 ; +55.09] | 42 % | +49.38 |
| maker 10 s, file prudente | 99 | 19702 | +2531 | +16.12 | [+0.46 ; +33.54] | 37 % | +37.04 |
| maker 10 s, file centrale | 106 | 20580 | +2544 | +16.21 | [-0.45 ; +32.72] | 37 % | +36.89 |
| maker 10 s, file optimiste | 129 | 38102 | +4902 | +31.22 | [+5.14 ; +59.09] | 40 % | +51.19 |
| maker 60 s, file prudente | 121 | 36086 | +3201 | +20.39 | [-4.60 ; +46.88] | 32 % | +38.83 |
| maker 60 s, file centrale | 122 | 36646 | +3293 | +20.98 | [-2.67 ; +46.88] | 32 % | +38.75 |
| maker 60 s, file optimiste | 137 | 47887 | +5268 | +33.56 | [+5.10 ; +67.18] | 38 % | +52.50 |

**Fantôme vivant M1 (maker au signal, mesuré en direct) sur les mêmes signaux** : 78 signaux appariés. M1 prudent +2716 $, proportionnel +2681 $ ; preneur 164 ms sur ces signaux +3970 $ ; simulation maker 60 s centrale +3176 $. (M1 est mis à l'échelle de 50 $ au prix maker.)

## 7. Comparaison contre Bot95 actuel, M4 et M8 (mêmes cycles)

Cycles communs avec les fantômes maker vivants : 16.

| Moteur | Ordres / signaux | P&L prudent ($) | P&L proportionnel ($) | par cycle (prudent) |
|---|---|---|---|---|
| M4 (vivant) | 102 | +190 | +400 | +11.86 |
| M8 (vivant) | 4 | +453 | +453 | +28.34 |
| Bot95 preneur 164 ms (simulé) | 80 | +3950 | — | +246.90 |
| Bot95 à 0 ms (borne idéale) | 80 | +4551 | — | +284.45 |

M4 et M8 ne sont pas déclenchés par les signaux : comparaison par cycle, pas par signal.

## 8. H775 — Décision anticipée (500 ms avant chaque signal) — livrables « signaux anticipables », « gagnants / perdants supplémentaires »

Le modèle de Dublin est recalculé hors ligne (copie de proba()). Validation au moment des signaux : voir la note. Grille de 100 ms sur tout le cycle ; première fois qu'une règle se déclenche dans le cycle (comme le bot). **Base** = mêmes flux que le bot ; **rapide** = on ajoute au prix Bybit/OKX le mouvement de Binance depuis cette observation (information disponible plus tôt). Exécution : décision + 164 ms, plafond = prix vu à la décision.

*Note de validation* : écart entre le modèle recalculé et le modèle enregistré au signal ≤ 0,005 pour 74 % des 157 signaux (médiane 0.0001) ; les écarts viennent surtout des signaux déclenchés par Bybit/OKX (l'enregistreur ne garde qu'une valeur par 50 ms).

- Signaux de grille « base » : 155 ; signaux réels retrouvés par la grille (même règle, même côté, même cycle) : 152 / 157.
- Signaux de grille « rapide » : 160. Appariés à un signal « base » (même règle et côté) : 154.
- Avance de la décision rapide sur la base : médiane 0 ms ; décidés plus tôt dans 2 % des cas ; **au moins 164 ms plus tôt : 3** ; au moins 500 ms plus tôt : 3.
- Sur les mêmes opportunités : base +3463 $ (+22.49 / signal), rapide +3408 $ (+22.13 / signal) ; différence moyenne -0.36 $ / signal, IC 90 % [-1.25 ; +0.20].
- **Signaux supplémentaires** (rapide seulement) : 6 — gagnants 3, perdants 3, P&L exécuté +0 $.
- **Signaux perdus** (base seulement) : 1 — gagnants 0, perdants 1, P&L qu'ils auraient donné -33 $.

## 9. H771–H773 — Offres d'achat prépositionnées avant les signaux (livrable « valeur de la priorité maker »)

Règle sans regard vers le futur (modèle « base » recalculé toutes les 100 ms) : tant que modèle − meilleur vendeur ≥ 0,10 sur un côté (prix 0,03–0,97, plus de 10 s restantes), une offre d'achat est posée au meilleur acheteur de ce côté (arrivée + 14 ms) et gardée à son prix ; retirée (+ 14 ms) quand la condition tombe. Inventaire plafonné à 50 $ par côté et par cycle. Tout remplissage est gardé jusqu'au règlement, y compris quand aucun signal ne suit (« non désiré »).

| File | Remplissages désirés : parts | P&L ($) | Remplissages non désirés : parts | P&L ($) | Total ($) | IC 90 % total par cycle |
|---|---|---|---|---|---|---|
| prudente | 3127 | +328 | 4551 | -106 | +222 | [-7.4 ; +22.0] / cycle |
| centrale | 3018 | +351 | 4669 | -131 | +220 | [-7.6 ; +21.9] / cycle |
| optimiste | 2267 | +308 | 5387 | -43 | +265 | [-7.0 ; +23.3] / cycle |

**Valeur de la priorité** — signaux réels couverts par une offre prépositionnée : parts et P&L de l'offre prépositionnée contre l'offre posée au signal (60 s).

| File | Signaux couverts | Prépositionnée : parts | P&L | Au signal : parts | P&L |
|---|---|---|---|---|---|
| prudente | 23 | 3127 | +328 | 5838 | +981 |
| centrale | 23 | 3018 | +351 | 5861 | +992 |
| optimiste | 17 | 2267 | +308 | 4600 | +814 |

## Limites
- Une seule journée, peu de cycles : tout est préliminaire ; aucune règle n'a été ajustée sur ces résultats.
- Carnet suivi seulement à ±3 c du meilleur prix entre deux photos complètes (10 s).
- File d'attente maker : trois bornes, la vraie valeur est entre prudente et optimiste.
- Modèle recalculé : fidèle pour les signaux déclenchés par le carnet, moins pour ceux déclenchés par Bybit/OKX (une valeur par 50 ms enregistrée).
- Les fantômes vivants M1/M4/M8 ne couvrent qu'une partie des cycles.
