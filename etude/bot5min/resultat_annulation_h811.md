# Bot95 — H811–H815 : vitesse d'annulation des makers — PRÉLIMINAIRE (hors ligne)

Généré le 11.10.2026 19:11 UTC. 82 cycles Dublin ; 13955 cotations (mêmes que H807 : 20 $ au meilleur acheteur, vie 5 s, latence 14 ms). Apprentissage / test : 7032 / 6923 cotations (coupure 12:10 UTC) — aucun paramètre n'est ajusté, la coupure sert seulement à vérifier la stabilité. Aucun ordre, aucun fantôme touché.

## 1. H811 — Délai entre le premier avertissement et le fill (fills toxiques, file centrale)

Cotations remplies : 8770 ; fills toxiques (milieu à +5 s ≤ prix − 1 c) : 4212 ; bons fills (≥ prix) : 3397.

| Avertissement | Fills toxiques avec avertissement avant le fill | Délai médian avertissement → fill (ms) | p10 / p25 / p75 / p90 | Bons fills avec avertissement avant |
|---|---|---|---|---|
| W | 3909 / 4212 (93 %) | 823 | 65 / 280 / 1865 / 3041 | 3022 / 3397 (89 %) |
| W1 | 3345 / 4212 (79 %) | 1033 | 150 / 405 / 2053 / 3185 | 2661 / 3397 (78 %) |
| W2 | 2546 / 4212 (60 %) | 155 | 13 / 29 / 417 / 1101 | 1454 / 3397 (43 %) |
| W3 | 45 / 4212 (1 %) | 181 | 80 / 134 / 323 / 709 | 7 / 3397 (0 %) |

## 2. H814 — Part des fills toxiques réellement évitables selon le délai d'annulation (avertissement W)

Évitable = l'annulation (avertissement + d) prend effet AVANT le premier fill. « Trop tard » = avertissement arrivé, mais fill avant l'effet de l'annulation. « Sans avertissement » = aucun signe observable avant le fill.

| Délai d | Toxiques évitables | Trop tard | Sans avertissement avant le fill | Bons fills perdus (annulés avant leur fill) |
|---|---|---|---|---|
| 10 ms (hors d’atteinte physique) | 3845 (91 %) | 64 (2 %) | 303 (7 %) | 2984 / 3397 (88 %) |
| 25 ms | 3705 (88 %) | 204 (5 %) | 303 (7 %) | 2911 / 3397 (86 %) |
| 50 ms | 3567 (85 %) | 342 (8 %) | 303 (7 %) | 2827 / 3397 (83 %) |
| 100 ms | 3411 (81 %) | 498 (12 %) | 303 (7 %) | 2718 / 3397 (80 %) |
| 200 ms | 3167 (75 %) | 742 (18 %) | 303 (7 %) | 2532 / 3397 (75 %) |

## 3. H812 / H815 — Garder contre annuler, P&L net à chaque délai

P&L au règlement des parts réellement remplies (même offre, même file) ; P&L « markout » = parts × (milieu à +5 s − prix) pour la file indiquée, moins bruité. Annuler ne coûte rien (pas de frais), mais fait perdre les bons fills.

### TOUS LES CYCLES

| Politique | File | Cotations remplies | Parts | P&L règlement / cotation (c) | IC 90 % | Marginal vs garder (c / cotation) | IC 90 % du marginal |
|---|---|---|---|---|---|---|---|
| garder | prudente | 7430 | 397601 | -75.2 | [-146.3 ; -5.1] | +0.0 | [+0.0 ; +0.0] |
| annuler W à 10 ms | prudente | 286 | 6948 | +0.9 | [-2.3 ; +4.6] | +76.1 | [+0.8 ; +147.7] |
| annuler W à 25 ms | prudente | 519 | 15082 | -2.8 | [-7.3 ; +2.0] | +72.4 | [-2.3 ; +142.3] |
| annuler W à 50 ms | prudente | 774 | 25893 | -4.5 | [-10.6 ; +2.1] | +70.7 | [+1.0 ; +139.8] |
| annuler W à 100 ms | prudente | 1071 | 36341 | -4.0 | [-13.3 ; +6.0] | +71.2 | [+3.8 ; +133.5] |
| annuler W à 200 ms | prudente | 1500 | 48933 | -6.5 | [-16.9 ; +4.5] | +68.7 | [+4.4 ; +128.4] |
| annuler W1 seul à 50 ms | prudente | 1465 | 66125 | -10.7 | [-26.3 ; +6.2] | +64.5 | [+0.3 ; +120.6] |
| annuler W2 seul à 50 ms | prudente | 2682 | 96823 | -13.3 | [-29.9 ; +5.8] | +61.9 | [+2.4 ; +117.8] |
| annuler W3 seul à 50 ms | prudente | 7371 | 388720 | -68.0 | [-138.2 ; +6.5] | +7.2 | [+4.7 ; +9.8] |
| garder | centrale | 8770 | 445470 | -69.4 | [-151.2 ; +15.8] | +0.0 | [+0.0 ; +0.0] |
| annuler W à 10 ms | centrale | 889 | 14563 | -0.3 | [-4.5 ; +4.0] | +69.1 | [-15.6 ; +147.8] |
| annuler W à 25 ms | centrale | 1128 | 22803 | -3.8 | [-8.9 ; +1.5] | +65.6 | [-21.1 ; +143.9] |
| annuler W à 50 ms | centrale | 1374 | 33788 | -5.2 | [-12.1 ; +1.9] | +64.2 | [-16.7 ; +140.6] |
| annuler W à 100 ms | centrale | 1675 | 44711 | -4.7 | [-14.8 ; +6.2] | +64.7 | [-14.4 ; +139.0] |
| annuler W à 200 ms | centrale | 2157 | 58240 | -7.1 | [-18.2 ; +4.6] | +62.3 | [-17.6 ; +132.6] |
| annuler W1 seul à 50 ms | centrale | 2071 | 74403 | -11.0 | [-27.0 ; +6.4] | +58.5 | [-9.8 ; +126.4] |
| annuler W2 seul à 50 ms | centrale | 5552 | 157271 | -9.1 | [-34.7 ; +23.8] | +60.3 | [-0.0 ; +120.4] |
| annuler W3 seul à 50 ms | centrale | 8716 | 436824 | -62.3 | [-141.3 ; +25.0] | +7.1 | [+4.9 ; +9.6] |
| garder | optimiste | 13053 | 856241 | +62.7 | [-114.4 ; +258.9] | +0.0 | [+0.0 ; +0.0] |
| annuler W à 10 ms | optimiste | 3988 | 158772 | +55.3 | [+18.9 ; +95.0] | -7.4 | [-181.2 ; +144.6] |
| annuler W à 25 ms | optimiste | 4254 | 169978 | +53.3 | [+15.7 ; +95.5] | -9.5 | [-183.2 ; +137.9] |
| annuler W à 50 ms | optimiste | 4599 | 187070 | +49.5 | [+11.5 ; +91.3] | -13.2 | [-188.2 ; +129.4] |
| annuler W à 100 ms | optimiste | 5162 | 212067 | +53.4 | [+7.5 ; +99.7] | -9.4 | [-167.0 ; +129.7] |
| annuler W à 200 ms | optimiste | 6045 | 252808 | +59.8 | [+5.2 ; +119.3] | -3.0 | [-153.7 ; +129.3] |
| annuler W1 seul à 50 ms | optimiste | 5172 | 235453 | +51.0 | [+0.5 ; +105.4] | -11.7 | [-170.5 ; +128.4] |
| annuler W2 seul à 50 ms | optimiste | 11351 | 622750 | +106.5 | [-32.8 ; +268.6] | +43.8 | [-5.6 ; +90.4] |
| annuler W3 seul à 50 ms | optimiste | 13038 | 851968 | +65.6 | [-121.8 ; +258.3] | +2.9 | [+1.1 ; +4.8] |

### 1re moitié

| Politique | File | Cotations remplies | Parts | P&L règlement / cotation (c) | IC 90 % | Marginal vs garder (c / cotation) | IC 90 % du marginal |
|---|---|---|---|---|---|---|---|
| garder | prudente | 3642 | 195999 | -34.7 | [-137.3 ; +78.3] | +0.0 | [+0.0 ; +0.0] |
| annuler W à 10 ms | prudente | 107 | 2454 | +2.3 | [-1.1 ; +5.7] | +37.0 | [-69.9 ; +134.2] |
| annuler W à 25 ms | prudente | 214 | 6369 | -1.4 | [-6.4 ; +3.5] | +33.3 | [-73.6 ; +131.7] |
| annuler W à 50 ms | prudente | 326 | 11440 | -1.5 | [-8.7 ; +6.1] | +33.2 | [-72.6 ; +128.3] |
| annuler W à 100 ms | prudente | 471 | 15906 | +2.6 | [-10.7 ; +17.0] | +37.3 | [-61.4 ; +131.4] |
| annuler W à 200 ms | prudente | 679 | 21796 | +0.9 | [-12.8 ; +16.1] | +35.6 | [-60.4 ; +128.5] |
| annuler W1 seul à 50 ms | prudente | 651 | 30521 | -6.0 | [-27.7 ; +19.0] | +28.7 | [-55.2 ; +114.4] |
| annuler W2 seul à 50 ms | prudente | 1247 | 45343 | -12.0 | [-31.2 ; +7.6] | +22.7 | [-68.9 ; +108.7] |
| annuler W3 seul à 50 ms | prudente | 3628 | 193362 | -28.9 | [-125.8 ; +78.2] | +5.8 | [+3.3 ; +8.5] |
| garder | centrale | 4317 | 220809 | -37.7 | [-143.4 ; +80.0] | +0.0 | [+0.0 ; +0.0] |
| annuler W à 10 ms | centrale | 364 | 5770 | +0.2 | [-3.6 ; +4.1] | +37.9 | [-78.6 ; +142.8] |
| annuler W à 25 ms | centrale | 477 | 9818 | -3.2 | [-8.8 ; +2.5] | +34.4 | [-71.1 ; +142.9] |
| annuler W à 50 ms | centrale | 583 | 14930 | -3.2 | [-11.2 ; +5.0] | +34.5 | [-78.6 ; +140.6] |
| annuler W à 100 ms | centrale | 734 | 19649 | +0.8 | [-12.0 ; +15.6] | +38.5 | [-68.2 ; +136.8] |
| annuler W à 200 ms | centrale | 963 | 25715 | -0.2 | [-14.8 ; +16.7] | +37.5 | [-67.3 ; +135.2] |
| annuler W1 seul à 50 ms | centrale | 913 | 34091 | -7.4 | [-28.4 ; +16.2] | +30.3 | [-68.9 ; +124.7] |
| annuler W2 seul à 50 ms | centrale | 2686 | 75602 | -17.0 | [-48.1 ; +12.2] | +20.7 | [-72.2 ; +106.8] |
| annuler W3 seul à 50 ms | centrale | 4303 | 218217 | -32.1 | [-139.0 ; +82.9] | +5.6 | [+3.2 ; +8.2] |
| garder | optimiste | 6423 | 430166 | +142.4 | [-111.2 ; +428.0] | +0.0 | [+0.0 ; +0.0] |
| annuler W à 10 ms | optimiste | 1673 | 67088 | +54.8 | [+13.4 ; +99.9] | -87.6 | [-345.7 ; +131.2] |
| annuler W à 25 ms | optimiste | 1803 | 72227 | +53.1 | [+8.9 ; +99.9] | -89.3 | [-323.2 ; +133.6] |
| annuler W à 50 ms | optimiste | 1951 | 80078 | +49.6 | [+5.7 ; +100.8] | -92.8 | [-336.1 ; +123.5] |
| annuler W à 100 ms | optimiste | 2224 | 92286 | +62.4 | [+6.2 ; +127.4] | -80.0 | [-303.5 ; +126.6] |
| annuler W à 200 ms | optimiste | 2654 | 112101 | +73.4 | [+5.0 ; +146.9] | -69.1 | [-295.0 ; +123.9] |
| annuler W1 seul à 50 ms | optimiste | 2216 | 102036 | +62.2 | [+0.8 ; +131.5] | -80.2 | [-306.3 ; +122.0] |
| annuler W2 seul à 50 ms | optimiste | 5585 | 312227 | +145.8 | [-52.6 ; +383.5] | +3.4 | [-72.7 ; +71.7] |
| annuler W3 seul à 50 ms | optimiste | 6419 | 429055 | +144.6 | [-111.4 ; +419.4] | +2.2 | [+0.8 ; +3.9] |

### 2e moitié

| Politique | File | Cotations remplies | Parts | P&L règlement / cotation (c) | IC 90 % | Marginal vs garder (c / cotation) | IC 90 % du marginal |
|---|---|---|---|---|---|---|---|
| garder | prudente | 3788 | 201602 | -116.4 | [-207.7 ; -11.5] | +0.0 | [+0.0 ; +0.0] |
| annuler W à 10 ms | prudente | 179 | 4494 | -0.4 | [-5.8 ; +5.6] | +116.0 | [+14.2 ; +206.0] |
| annuler W à 25 ms | prudente | 305 | 8713 | -4.3 | [-11.3 ; +3.1] | +112.0 | [+6.4 ; +203.4] |
| annuler W à 50 ms | prudente | 448 | 14453 | -7.6 | [-17.0 ; +3.6] | +108.7 | [+7.1 ; +195.0] |
| annuler W à 100 ms | prudente | 600 | 20435 | -10.7 | [-23.2 ; +2.6] | +105.7 | [+14.4 ; +190.9] |
| annuler W à 200 ms | prudente | 821 | 27137 | -14.0 | [-29.1 ; +1.7] | +102.3 | [+2.6 ; +187.1] |
| annuler W1 seul à 50 ms | prudente | 814 | 35605 | -15.4 | [-36.5 ; +10.6] | +101.0 | [+21.4 ; +182.1] |
| annuler W2 seul à 50 ms | prudente | 1435 | 51480 | -14.5 | [-42.6 ; +18.7] | +101.8 | [+24.3 ; +174.4] |
| annuler W3 seul à 50 ms | prudente | 3743 | 195358 | -107.6 | [-199.7 ; +3.3] | +8.7 | [+4.4 ; +13.3] |
| garder | centrale | 4453 | 224662 | -101.7 | [-209.6 ; +23.5] | +0.0 | [+0.0 ; +0.0] |
| annuler W à 10 ms | centrale | 525 | 8793 | -0.9 | [-8.3 ; +6.9] | +100.8 | [-21.4 ; +207.7] |
| annuler W à 25 ms | centrale | 651 | 12984 | -4.5 | [-13.3 ; +4.7] | +97.2 | [-28.2 ; +208.8] |
| annuler W à 50 ms | centrale | 791 | 18857 | -7.3 | [-18.5 ; +5.1] | +94.4 | [-25.1 ; +201.7] |
| annuler W à 100 ms | centrale | 941 | 25062 | -10.3 | [-24.3 ; +5.2] | +91.4 | [-23.3 ; +191.0] |
| annuler W à 200 ms | centrale | 1194 | 32525 | -14.2 | [-31.2 ; +4.0] | +87.5 | [-23.8 ; +185.0] |
| annuler W1 seul à 50 ms | centrale | 1158 | 40312 | -14.7 | [-36.0 ; +11.2] | +87.0 | [-27.8 ; +173.1] |
| annuler W2 seul à 50 ms | centrale | 2866 | 81669 | -1.1 | [-45.3 ; +55.3] | +100.6 | [+17.6 ; +172.5] |
| annuler W3 seul à 50 ms | centrale | 4413 | 218607 | -93.0 | [-198.8 ; +43.3] | +8.7 | [+4.9 ; +12.8] |
| garder | optimiste | 6630 | 426075 | -18.2 | [-267.0 ; +276.8] | +0.0 | [+0.0 ; +0.0] |
| annuler W à 10 ms | optimiste | 2315 | 91684 | +55.7 | [-1.1 ; +121.2] | +74.0 | [-158.0 ; +268.2] |
| annuler W à 25 ms | optimiste | 2451 | 97751 | +53.4 | [-4.8 ; +118.1] | +71.6 | [-150.4 ; +256.6] |
| annuler W à 50 ms | optimiste | 2648 | 106993 | +49.5 | [-15.2 ; +118.4] | +67.7 | [-161.1 ; +254.0] |
| annuler W à 100 ms | optimiste | 2938 | 119781 | +44.1 | [-23.2 ; +123.9] | +62.4 | [-164.4 ; +242.5] |
| annuler W à 200 ms | optimiste | 3391 | 140708 | +46.0 | [-35.1 ; +136.1] | +64.2 | [-132.5 ; +235.5] |
| annuler W1 seul à 50 ms | optimiste | 2956 | 133417 | +39.6 | [-36.4 ; +129.4] | +57.8 | [-162.6 ; +222.5] |
| annuler W2 seul à 50 ms | optimiste | 5766 | 310523 | +66.7 | [-125.6 ; +302.0] | +84.9 | [+23.8 ; +141.7] |
| annuler W3 seul à 50 ms | optimiste | 6619 | 422914 | -14.6 | [-263.3 ; +274.7] | +3.6 | [+0.4 ; +7.2] |

**P&L markout +5 s (moins dépendant des jackpots), file centrale, tous les cycles**

| Politique | Markout total (c / cotation) | Parts |
|---|---|---|
| garder | -58.00 | 445470 |
| annuler W à 10 ms | -1.28 | 14563 |
| annuler W à 25 ms | -2.60 | 22803 |
| annuler W à 50 ms | -4.33 | 33788 |
| annuler W à 100 ms | -6.05 | 44711 |
| annuler W à 200 ms | -8.42 | 58240 |

## 4. H813 — Coût de la perte de priorité (annuler à 50 ms, reposer 500 ms plus tard en fin de file)

Comparaison sur la même fenêtre (de la repose à la fin de vie) : parts et P&L que l'offre d'origine aurait obtenus si on l'avait gardée (avec sa place) contre ce que l'offre reposée en fin de file obtient.

| File | Cotations reposées | Parts : gardée / reposée | P&L règlement : gardée / reposée ($) | Coût de la priorité ($) |
|---|---|---|---|---|
| prudente | 13553 | 301002 / 319216 | -8437 / -7439 | -998 |
| centrale | 13553 | 333418 / 356784 | -7445 / -7277 | -168 |
| optimiste | 13553 | 469916 / 631882 | -1813 / +3251 | -5064 |

## 5. Lecture
- Délai maximal acceptable = plus grand d pour lequel « annuler » reste au-dessus de « garder » ET au-dessus de 0 sous la file prudente, avec un IC par cycles > 0.
- Le délai réaliste depuis Dublin est ≥ 14 ms (trajet simple) + temps de calcul ; Polymarket n'impose pas de retard aux annulations.

## Limites
- Une journée, ~80 cycles ; offres fictives qui ne modifient pas le carnet.
- Le markout et le statut toxique sont mesurés au premier fill.
- W2 et W1 sont mesurés sur le carnet reçu à Dublin (≈ 10 ms après Polymarket) : ce sont bien des informations disponibles à Dublin.
