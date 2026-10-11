# Bot95 — H766 à H775 : capturer l'avantage malgré la latence ? — PRÉLIMINAIRE

Généré le 11.10.2026 19:12 UTC. Cycles enregistrés à Dublin avant le 13.10 : 83 ; signaux Bot95 réglés sur ces cycles : **278** sur **55 cycles**. IC 90 % par rééchantillonnage de cycles. Validation chronologique : 1re moitié = cycles < 12:30 UTC, 2e moitié après. Exécution preneur : décision + 14 ms de trajet + 150 ms de retard Polymarket = 164 ms. Budget 50 $ par signal (comme Dublin). Aucun ordre, aucun fantôme touché.

## 0. Contrôle de la reconstruction du carnet

- 0 ms : quantité achetable reconstruite = quantité vue par Dublin (± 5 %) dans 100 % des 278 signaux.
- 50 ms : quantité achetable reconstruite = quantité vue par Dublin (± 5 %) dans 89 % des 278 signaux.
- 100 ms : quantité achetable reconstruite = quantité vue par Dublin (± 5 %) dans 90 % des 278 signaux.
- 250 ms : quantité achetable reconstruite = quantité vue par Dublin (± 5 %) dans 95 % des 278 signaux.
- 500 ms : quantité achetable reconstruite = quantité vue par Dublin (± 5 %) dans 97 % des 278 signaux.

## 1. H766 — P&L et quantité exécutable selon la latence (preneur, prix du signal, plafond +0) — livrables « courbe P&L/latence », « quantités capturables », « P&L par signal initial »

P&L par **signal initial** = résultat en $ de ce que l'on aurait réellement pu acheter (0 si rien), frais compris, puis moyenne sur tous les signaux.

| Délai | Signaux exécutables | Parts / parts à 0 ms | P&L total ($) | P&L moyen par signal ($) | IC 90 % | par $ investi | 1re moitié / signal | 2e moitié / signal |
|---|---|---|---|---|---|---|---|---|
| 0 ms (mesure Dublin) | 278 / 278 | 100 % | +5641 | +20.29 | [+7.42 ; +35.57] | +116.0 % | +18.44 | +22.12 |
| 25 ms | 262 / 278 | 135 % | +5335 | +19.19 | [+4.68 ; +34.87] | +77.8 % | +17.91 | +20.45 |
| 50 ms | 259 / 278 | 146 % | +5323 | +19.15 | [+3.28 ; +37.77] | +72.3 % | +16.92 | +21.35 |
| 100 ms | 246 / 278 | 153 % | +4357 | +15.67 | [+0.66 ; +32.68] | +56.9 % | +12.47 | +18.83 |
| 150 ms | 234 / 278 | 150 % | +4236 | +15.24 | [+0.21 ; +31.36] | +56.9 % | +12.54 | +17.90 |
| 164 ms (preneur réel) | 229 / 278 | 149 % | +4141 | +14.90 | [+0.39 ; +31.19] | +56.4 % | +12.05 | +17.71 |
| 250 ms | 194 / 278 | 142 % | +3672 | +13.21 | [-0.94 ; +28.73] | +53.6 % | +10.44 | +15.93 |
| 300 ms | 179 / 278 | 137 % | +3537 | +12.72 | [-0.72 ; +27.74] | +54.0 % | +9.52 | +15.88 |
| 500 ms | 166 / 278 | 130 % | +2640 | +9.50 | [-2.33 ; +22.43] | +42.8 % | +9.73 | +9.27 |

**Robustesse (preneur 164 ms, plafond +0)** — le résultat dépend-il de quelques gros gains ?

- Médiane par signal : -3.55 $ ; part du P&L total venant des 5 meilleurs signaux : 59 % ; P&L sans les 5 meilleurs : +1696 $ ; sans les 10 meilleurs : +314 $.
- **Décisions uniques** (un seul achat par cycle et par côté — le premier signal ; les variantes du même cycle achètent souvent le même billet) : 77 décisions, P&L +810 $, moyen +10.52 $ IC 90 % [-2.29 ; +23.81], médiane -12.65 $.

| Prix du signal | Signaux | Taux de gain | P&L 0 ms ($) | P&L 164 ms ($) | P&L 500 ms ($) | perte due à la latence 0→164 ms |
|---|---|---|---|---|---|---|
| 0.00–0.10 | 21 | 19 % | +1400 | +1474 | +1397 | +74 |
| 0.10–0.20 | 74 | 24 % | +1485 | +1237 | +42 | -248 |
| 0.20–0.35 | 153 | 36 % | +2199 | +1501 | +1358 | -698 |
| 0.35–1.00 | 30 | 63 % | +556 | -72 | -157 | -628 |

## 2. H768 — Latence critique

- Premier délai où l'espérance moyenne par signal devient ≤ 0 : **aucun jusqu’à 500 ms**.
- Premier délai où l'IC 90 % est entièrement négatif : **aucun jusqu’à 500 ms**.
- Premier délai où l'IC 90 % ne contient plus que du positif : 0 ms, 25 ms, 50 ms, 100 ms, 150 ms, 164 ms.

## 3. H767 — Pourquoi les offres disparaissent (livrable « analyse des offres disparues »)

Pour chaque signal : baisse des quantités vendues au prix du signal ou mieux entre la décision et +250 ms (puis +500 ms), et transactions qui consomment ce côté à ces prix (reçues jusqu'à 60 ms après). Consommé = min(baisse, transactions) ; retiré = le reste ; **indéterminé** si un carnet complet est rechargé dans la fenêtre ou si le flux est coupé (aucune attribution inventée).

| Cause | Signaux | Parts consommées | Parts retirées | Taux de gain du signal |
|---|---|---|---|---|
| pas disparue (≥ 50 % encore là à 250 ms) | 169 | 2313 | 39688 | 28 % |
| retirée (annulation) | 83 | 1310 | 11855 | 42 % |
| indéterminé (carnet rechargé / flux coupé) | 14 | 212 | 798 | 50 % |
| consommée par des transactions | 12 | 1184 | 200 | 50 % |

Lecture : « consommée » = un autre preneur a acheté avant nous (course de vitesse) ; « retirée » = le vendeur a annulé (il a vu le même mouvement).

## 4. H769 — Prix plafond (livrable « gain marginal des prix plafonds »)

| Délai | Plafond | Signaux exécutables | Parts | P&L total ($) | P&L moyen / signal | IC 90 % | Gain marginal vs +0 ($) | 2e moitié / signal |
|---|---|---|---|---|---|---|---|---|
| 164 ms | +0 c | 229 | 36412 | +4141 | +14.90 | [-0.16 ; +31.73] | +0 | +17.71 |
| 164 ms | +1 c | 243 | 45148 | +3967 | +14.27 | [-2.94 ; +32.01] | -175 | +17.44 |
| 164 ms | +2 c | 246 | 52041 | +4122 | +14.83 | [-2.95 ; +35.38] | -19 | +15.19 |
| 164 ms | +3 c | 251 | 57435 | +4352 | +15.65 | [-2.95 ; +36.99] | +211 | +14.75 |
| 250 ms | +0 c | 194 | 34666 | +3672 | +13.21 | [-1.31 ; +29.52] | +0 | +15.93 |
| 250 ms | +1 c | 216 | 43650 | +3568 | +12.83 | [-3.95 ; +30.86] | -104 | +16.34 |
| 250 ms | +2 c | 224 | 49879 | +3297 | +11.86 | [-6.25 ; +31.67] | -375 | +13.60 |
| 250 ms | +3 c | 227 | 54717 | +3373 | +12.13 | [-5.63 ; +31.48] | -299 | +12.84 |
| 500 ms | +0 c | 166 | 31903 | +2640 | +9.50 | [-2.34 ; +22.13] | +0 | +9.27 |
| 500 ms | +1 c | 190 | 42186 | +2533 | +9.11 | [-4.31 ; +24.47] | -108 | +9.88 |
| 500 ms | +2 c | 201 | 49127 | +2314 | +8.32 | [-7.60 ; +24.29] | -326 | +7.82 |
| 500 ms | +3 c | 207 | 53888 | +2238 | +8.05 | [-9.12 ; +26.57] | -402 | +5.86 |

## 5. H774 — Alpha sans poursuite (abandon / deuxième chance / attente)

Achat seulement tant que modèle (figé au signal) − prix − frais ≥ 0,05.

| Politique | Signaux exécutés | Parts | P&L total ($) | moyen / signal | IC 90 % | 2e moitié / signal |
|---|---|---|---|---|---|---|
| abandon immédiat (164 ms, +0) | 229 | 36412 | +4141 | +14.90 | [-0.61 ; +31.40] | +17.71 |
| deuxième chance (+164 ms puis 500 ms, plafond +2 c) | 244 | 39821 | +3939 | +14.17 | [-1.89 ; +31.09] | +15.87 |
| attente : relances 5 s au prix du signal | 243 | 58658 | +4052 | +14.58 | [-3.40 ; +35.70] | +14.16 |
| attente : relances 5 s, plafond +2 c | 250 | 64620 | +4067 | +14.63 | [-5.36 ; +35.32] | +12.20 |

## 6. H770 — Maker contre preneur sur les mêmes signaux

Maker simulé : offre d'achat posée à décision + 14 ms au meilleur acheteur (+1 c si l'écart > 1 c, règle de M1), retirée après 10 s ou 60 s ; file d'attente : prudente (seules les transactions nous font avancer), centrale (annulations réparties), optimiste (toutes les annulations devant nous). Gardé jusqu'au règlement, sans frais (maker).

| Voie | Signaux remplis | Parts | P&L total ($) | moyen / signal | IC 90 % | Taux de gain des remplis | 2e moitié / signal |
|---|---|---|---|---|---|---|---|
| preneur 164 ms (Bot95 actuel) | 229 | 36412 | +4141 | +14.90 | [-0.32 ; +31.78] | 34 % | +17.71 |
| maker 10 s, file prudente | 178 | 37176 | +405 | +1.46 | [-9.27 ; +12.36] | 26 % | -4.26 |
| maker 10 s, file centrale | 190 | 38992 | +417 | +1.50 | [-9.15 ; +12.48] | 26 % | -4.27 |
| maker 10 s, file optimiste | 236 | 67832 | +3379 | +12.15 | [-5.94 ; +31.27] | 28 % | +8.21 |
| maker 60 s, file prudente | 223 | 63447 | +333 | +1.20 | [-14.28 ; +18.25] | 23 % | -4.50 |
| maker 60 s, file centrale | 225 | 64084 | +479 | +1.72 | [-14.86 ; +18.59] | 24 % | -4.12 |
| maker 60 s, file optimiste | 248 | 78900 | +3869 | +13.92 | [-6.41 ; +36.61] | 28 % | +11.32 |

**Fantôme vivant M1 (maker au signal, mesuré en direct) sur les mêmes signaux** : 198 signaux appariés. M1 prudent +1167 $, proportionnel +1203 $ ; preneur 164 ms sur ces signaux +3443 $ ; simulation maker 60 s centrale +411 $. (M1 est mis à l'échelle de 50 $ au prix maker.)

## 7. Comparaison contre Bot95 actuel, M4 et M8 (mêmes cycles)

Cycles communs avec les fantômes maker vivants : 40.

| Moteur | Ordres / signaux | P&L prudent ($) | P&L proportionnel ($) | par cycle (prudent) |
|---|---|---|---|---|
| M4 (vivant) | 351 | -433 | -35 | -10.83 |
| M8 (vivant) | 122 | -816 | -745 | -20.41 |
| Bot95 preneur 164 ms (simulé) | 201 | +3422 | — | +85.54 |
| Bot95 à 0 ms (borne idéale) | 201 | +4558 | — | +113.94 |

M4 et M8 ne sont pas déclenchés par les signaux : comparaison par cycle, pas par signal.

## 8. H775 — Décision anticipée (500 ms avant chaque signal) — livrables « signaux anticipables », « gagnants / perdants supplémentaires »

Le modèle de Dublin est recalculé hors ligne (copie de proba()). Validation au moment des signaux : voir la note. Grille de 100 ms sur tout le cycle ; première fois qu'une règle se déclenche dans le cycle (comme le bot). **Base** = mêmes flux que le bot ; **rapide** = on ajoute au prix Bybit/OKX le mouvement de Binance depuis cette observation (information disponible plus tôt). Exécution : décision + 164 ms, plafond = prix vu à la décision.

*Note de validation* : écart entre le modèle recalculé et le modèle enregistré au signal ≤ 0,005 pour 72 % des 278 signaux (médiane 0.0001) ; les écarts viennent surtout des signaux déclenchés par Bybit/OKX (l'enregistreur ne garde qu'une valeur par 50 ms).

- Signaux de grille « base » : 274 ; signaux réels retrouvés par la grille (même règle, même côté, même cycle) : 269 / 278.
- Signaux de grille « rapide » : 281. Appariés à un signal « base » (même règle et côté) : 271.
- Avance de la décision rapide sur la base : médiane 0 ms ; décidés plus tôt dans 4 % des cas ; **au moins 164 ms plus tôt : 8** ; au moins 500 ms plus tôt : 8.
- Sur les mêmes opportunités : base +3201 $ (+11.81 / signal), rapide +3145 $ (+11.61 / signal) ; différence moyenne -0.21 $ / signal, IC 90 % [-1.18 ; +0.70].
- **Signaux supplémentaires** (rapide seulement) : 10 — gagnants 3, perdants 7, P&L exécuté -64 $.
- **Signaux perdus** (base seulement) : 3 — gagnants 2, perdants 1, P&L qu'ils auraient donné +4 $.

## 9. H771–H773 — Offres d'achat prépositionnées avant les signaux (livrable « valeur de la priorité maker »)

Règle sans regard vers le futur (modèle « base » recalculé toutes les 100 ms) : tant que modèle − meilleur vendeur ≥ 0,10 sur un côté (prix 0,03–0,97, plus de 10 s restantes), une offre d'achat est posée au meilleur acheteur de ce côté (arrivée + 14 ms) et gardée à son prix ; retirée (+ 14 ms) quand la condition tombe. Inventaire plafonné à 50 $ par côté et par cycle. Tout remplissage est gardé jusqu'au règlement, y compris quand aucun signal ne suit (« non désiré »).

| File | Remplissages désirés : parts | P&L ($) | Remplissages non désirés : parts | P&L ($) | Total ($) | IC 90 % total par cycle |
|---|---|---|---|---|---|---|
| prudente | 5338 | +217 | 7617 | -216 | +1 | [-12.0 ; +12.3] / cycle |
| centrale | 4937 | +325 | 8055 | -322 | +4 | [-11.9 ; +11.3] / cycle |
| optimiste | 3648 | +222 | 9192 | -167 | +56 | [-10.9 ; +12.7] / cycle |

**Valeur de la priorité** — signaux réels couverts par une offre prépositionnée : parts et P&L de l'offre prépositionnée contre l'offre posée au signal (60 s).

| File | Signaux couverts | Prépositionnée : parts | P&L | Au signal : parts | P&L |
|---|---|---|---|---|---|
| prudente | 41 | 5338 | +217 | 9100 | +791 |
| centrale | 38 | 4937 | +325 | 8759 | +956 |
| optimiste | 27 | 3648 | +222 | 7376 | +1307 |

## Limites
- Une seule journée, peu de cycles : tout est préliminaire ; aucune règle n'a été ajustée sur ces résultats.
- Carnet suivi seulement à ±3 c du meilleur prix entre deux photos complètes (10 s).
- File d'attente maker : trois bornes, la vraie valeur est entre prudente et optimiste.
- Modèle recalculé : fidèle pour les signaux déclenchés par le carnet, moins pour ceux déclenchés par Bybit/OKX (une valeur par 50 ms enregistrée).
- Les fantômes vivants M1/M4/M8 ne couvrent qu'une partie des cycles.
