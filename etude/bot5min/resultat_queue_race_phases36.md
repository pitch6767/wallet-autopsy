# BOT95 — QUEUE RACE ENGINE · phases 3 à 6 (et phases 0 à 2 relancées sur toutes les données)

Étude hors ligne du 14.10.2026, demandée par Pitch le 11.10 (« je veux tout oui »), hypothèses H491–H510 et H523–H558. **Aucun bot, aucun workflow, aucun fantôme, aucun paramètre modifié, aucun ordre réel.** Données : enregistreur du VPS de Dublin (branche `donnees-rapide`), **752 cycles BTC 5 min du 11.10 10:45 au 14.10 02:20** (heure suisse), tous utilisés, sans sous-échantillonnage. Scripts : `queue_race_phases.py` (phases 0–2, copie adaptée de `queue_race_phase12.py`, laissé intact) → `resultat_queue_race_phases.md` ; `queue_race_phases36.py` (phases 3–5) → ce fichier. Découpage **chronologique** : apprentissage (11.10 10:45 → 12.10 18:15), validation (→ 13.10 09:55), **test (13.10 09:55 → 14.10 02:20)** ; tous les seuils sont choisis sans regarder le test.

## Verdict (en tête)

- **Les deux modèles marchent pour prévoir le carnet, mais aucun fantôme ne bat le moteur C. Rien à mettre en fantôme.**
- **Phase 3** : retrait du meilleur vendeur dans les 22,7 → 522,7 ms : **AUC test 0,759** [IC 90 % 0,754 ; 0,763] ; consommation par un acheteur : **AUC test 0,765** [0,760 ; 0,769]. Bien calibrés sauf le décile le plus haut (surestimé de 3–4 points). Mais les deux modèles reposent sur les mêmes indices (petite taille de l'offre, déséquilibre du carnet) : le modèle « retrait » devine aussi bien les consommations (0,763) que le modèle « consommation ». On prévoit **qu'une offre va disparaître**, pas vraiment **pourquoi**.
- **Phase 4 (course)** : quand le modèle « retrait » sonne (5 % des instants les plus risqués), l'offre disparaît dans l'horizon 34,5 % des fois (9,9 % au hasard), mais notre ordre arriverait avant la disparition seulement **60,8 %** des fois (aller simple 14 ms) / **53,2 %** (aller-retour 28 ms), contre 81,5 % / 77,5 % au hasard. Acheter à l'alerte vaut −2,8 ‰ par part à 5 s [−4,3 ; −1,4] (frais compris), contre −18,1 ‰ au hasard : on perd beaucoup moins, mais **on perd quand même**. Alerte « consommation » : 0,0 ‰ [−1,5 ; +1,5] → nul.
- **Phase 5 (test, 71 signaux des cohortes A/B, 188 cycles)** : moteur C **+299 $**. **R +143 $** (Δ **−155 $**, IC 90 % [−307 ; −31], Bonferroni [−361 ; −1]) ; **S +107 $** (Δ **−192 $**, [−347 ; −63], Bonferroni [−403 ; −34]) ; **RS +107 $** (Δ −192 $, Bonferroni [−392 ; −35]). Jackpots sur le test : 0 pour C, 0 récupéré par R, S ou RS. Pertes ajoutées : R −167 $ pour +12 $ de gains, S/RS −203 $ pour +12 $. Perte maximale (drawdown) : C 272 $, R 331 $, S et RS 345 $. Capital engagé : C 2 094 $, R 2 269 $, S/RS 2 305 $.
- **Verdict corrigé pour 3 tests (Bonferroni)** : aucune variante n'améliore le moteur C ; **S et RS sont démontrées moins bonnes** (IC entièrement négatif), R l'est presque (borne haute −1 $). Attention : ce « démontré » repose sur 8 à 12 achats ajoutés seulement. Conclusion pratique : acheter les signaux que le moteur C refuse parce que le vendeur risque de retirer son offre (ou parce qu'un acheteur risque de la prendre) **ne rapporte pas** ; le moteur C a raison de les refuser.
- **Phases 0–2 sur 752 cycles** : le résultat du 11.10 tient : **75,8 % des disparitions du meilleur vendeur sont des retraits**, 24,2 % des consommations (stable chaque jour : 74,7 % à 77,1 %). Une information de bourse (saut ≥ 5 $) précède 30,8 % des disparitions contre 21,9 % au hasard : elle n'en explique que ≈ 9 points.

## Hypothèses (interprétation)

Les fiches des hypothèses H491, H496, H502, H536 et H545 ne sont pas dans le dépôt (seule la plage H491–H510 / H523–H558 est citée dans `queue_race_phase12.py`). Je les ai donc définies simplement, avant de calculer :

| Hypothèse | Définition retenue | Résultat (test) |
|---|---|---|
| H491 | Le **retrait** du meilleur vendeur est prévisible avant qu'il arrive, avec notre délai (22,7 ms) | **oui** : AUC 0,759 [0,754 ; 0,763] (horizon 500 ms) ; 0,823 (horizon 200 ms) |
| H496 | La **consommation** du meilleur vendeur par un acheteur est prévisible avec notre délai | **oui** : AUC 0,765 [0,760 ; 0,769] ; 0,850 (200 ms) |
| H502 | Le déséquilibre du carnet (microprix) annonce la consommation assez tôt pour nous | **oui mais faible** : seul, AUC 0,739 (≥ 22,7 ms avant) ; 0,876 juste avant (mécanique), 0,619 arrêté 500 ms avant |
| H536 | Un mouvement des bourses (perp Bybit, flux agressifs) annonce le **retrait** des vendeurs | **faible** : AUC seule 0,562 (perp) et 0,564 (flux) ; en phase 2, l'information de bourse n'explique que ≈ 9 points des disparitions |
| H545 | Retraits et consommations ont des **précurseurs différents** (deux modèles valent mieux qu'un) | **non** : le modèle retrait classe les consommations à 0,763 (modèle dédié 0,765) ; un modèle unique fait 0,759 / 0,766 |

## Synthèse des 12 livrables (phase 6)

| # | Livrable | Résultat |
|---|---|---|
| 1 | Audit des données et couverture | 752 cycles, 61,1 h de flux sur 62,7 h ; 732 cycles en millièmes, 17 au cent, 3 bruts ; 735 avec flux agressifs `fx` ; 11 cycles coupés, 10 presque vides. Reconstruction du meilleur niveau : prix 99,8 %, prix + taille 98,3–98,4 % contre les photos 1 s ; miroir Up/Down 100 %. Contrôle des signaux : 1 820/1 832 (99,3 %) même verdict « disparue / pas disparue » que le bot en direct. |
| 2 | Causes de disparition | 248 779 disparitions complètes : retiré 57,1 %, déplacé 18,7 %, consommé 23,1 %, mixte 1,0 % (4 406 indéterminées exclues). Offres visées par les 2 246 signaux du bot : retirées 1 088, consommées 128, mixtes 244, encore là à 2 s 736. Gagnants : retirée 31,6 %, consommée 40,7 %, **encore là 13,1 %** (sélection adverse confirmée). |
| 3 | Chronologie information → réaction → retrait → transaction | Après un saut de bourse ≥ 5 $ (médianes, témoin au hasard) : réaction de l'autre côté 20 ms (31), 1er retrait 45 ms (50), 1re consommation 100 ms (146), disparition 222 ms (443). Retrait d'abord 69,6 % (témoin 72,8 %). Flux agressifs ≥ 250 k$ : retrait d'abord 78,2 % (73,1 %), 1er retrait 30 ms (52). |
| 4 | Précurseurs et AUC | Déséquilibre du microprix : 0,876 juste avant une consommation, 0,799 / 0,730 / 0,619 arrêté 100 / 200 / 500 ms avant ; modèle combiné 0,904 → 0,639. Phase 3 (≥ 22,7 ms avant) : taille de l'offre (petite = disparaît) 0,74, déséquilibre 0,71–0,74, renforcement d'en face 0,58–0,60, perp et flux 0,56–0,59. |
| 5 | Modèle retrait | AUC validation 0,747, test 0,759 ; Brier test 0,0774 contre 0,0840 sans modèle ; décile haut : prédit 31,9 %, observé 27,9 %. |
| 6 | Modèle consommation | AUC validation 0,772, test 0,765 ; Brier test 0,0312 contre 0,0323 ; décile haut : prédit 14,8 %, observé 11,6 %. |
| 7 | Course avec délais réels | Alerte retrait : arrivé avant la disparition 60,8 % (14 ms) / 53,2 % (28 ms) contre 81,5 % / 77,5 % au hasard ; encore achetable à +28 ms 84,3 % ; valeur à 5 s −2,8 ‰/part. Alerte consommation : 65,5 % / 59,8 % ; valeur 0,0 ‰. Avant la 1re baisse du niveau visé : 43 à 48 %, comme au hasard. |
| 8 | Fantôme R contre moteur C (test) | +143 $ contre +299 $ : Δ −155 $ [−307 ; −31] ; 8 achats ajoutés, 0 jackpot ; drawdown 331 $ contre 272 $. |
| 9 | Fantôme S contre moteur C (test) | +107 $ : Δ −192 $ [−347 ; −63] ; 12 achats ajoutés, 0 jackpot ; drawdown 345 $. |
| 10 | Fantôme RS contre moteur C (test) | +107 $ : Δ −192 $ [−343 ; −63] (sur le test RS = S : les ajouts de R sont tous dans S) ; drawdown 345 $. |
| 11 | Verdict corrigé (Bonferroni, 3 variantes, IC 96,7 %) | R [−361 ; −1], S [−403 ; −34], RS [−392 ; −35] : **aucune amélioration ; S et RS moins bonnes que C**. Sur l'apprentissage et la validation, les trois variantes étaient légèrement positives (+40 à +127 $, IC contenant 0) : le gain apparent n'a pas tenu. |
| 12 | Ce qu'il faudrait pour aller en réel, et limites | Rien à mettre en réel ni en fantôme. Pour aller plus loin il faudrait : (a) un signal qui prédit **le gagnant** et non la disparition (sur tous les signaux du bot, la probabilité de retrait n'annonce pas le gain : AUC test 0,477) ; (b) un délai plus court que celui des concurrents (on arrive après la 1re baisse plus d'une fois sur deux quand l'alerte sonne) ; (c) plusieurs centaines de signaux refusés par C sur une période neuve avant tout verdict. Limites ci-dessous. |

## Limites (à lire)

- **Petits effectifs en phase 5** : 71 signaux de cohorte au test, dont 8 à 12 achats ajoutés par les variantes. Les IC par cycle sont fragiles avec si peu de cycles concernés ; « démontré moins bon » veut surtout dire « aucune raison de continuer ».
- **Exécution simulée** sur le carnet reconstruit reçu à Dublin 28 ms après la décision, quantité affichée, sans file d'attente ni réaction des autres à notre ordre. Le P&L simulé du moteur C (+2 732 $ sur les 175 envois de toute la période) est plus optimiste que celui enregistré en direct par le bot (+2 400 $) : frais 0,07 contre 0,072 et aller-retour 28 ms contre 30–36 ms mesurés.
- **Moteur C** : décisions prises telles qu'enregistrées en direct (`moteurC.envoie`, plafond) ; elles n'existent que pour les cohortes A et B. Les variantes R/S n'ajoutent que des signaux refusés par C (lecture retenue de « acheter tout de suite au lieu d'attendre / de laisser passer »).
- **Modèles volontairement simples** (régression logistique, 10 variables fixées à l'avance, aucun réglage). Les flux agressifs n'existent qu'à partir du 11.10 après-midi (mis à 0 avant). Instants sur une grille de 250 ms ; un niveau qui perd la première place parce qu'un meilleur prix arrive n'est pas compté comme « retiré ».
- **Horloges** Dublin / Polymarket comparées directement (le décalage est inclus dans les 8,6 ms). Échantillon 50 ms des bourses. Un seul actif, 2,6 jours, test sur 188 cycles ≈ 15,7 h (13.10 matin → 14.10 nuit).

# Détail des calculs (produit par `queue_race_phases36.py`)

## Données et découpage

- 752 cycles BTC 5 min (résumés produits par `queue_race_phases.py`). Découpage **chronologique** par cycle : apprentissage 376 cycles (11.10 10:45 → 12.10 18:15), validation 188 (12.10 18:15 → 13.10 09:55), **test 188** (13.10 09:55 → 14.10 02:20), heure suisse. Aucun paramètre n'est choisi sur le test.
- Instants éligibles : grille de 250 ms sur chaque cycle, les deux offres (Up et Down), prix entre 0,03 et 0,97 : **1 274 430 instants**. Exclus des modèles : niveau disparu avant notre délai (22,7 ms) 16 239 (1,3 %) ; disparition « indéterminée » dans l'horizon 879.
- **Délai** : Polymarket → Dublin 8,6 ms + calcul 0,1 ms + aller simple 14 ms = **22,7 ms**. Variables calculées avec ce qui est reçu à Dublin à l'instant T ; l'événement à prédire doit arriver entre T + 22,7 ms et T + 22,7 + 500 ms (sensibilité 200 ms).

## Phase 3 — deux modèles séparés : retrait vendeur et consommation acheteuse

Régression logistique, 10 variables fixées avant tout calcul (les mêmes pour les deux modèles) : (1) déséquilibre du microprix vers l'offre ; (2) log taille de l'offre ; (3) écart acheteur-vendeur (‰) ; (4) variation log taille de l'offre 200 ms ; (5) variation log taille d'en face 200 ms ; (6) log âge du meilleur prix (ms) ; (7) logit du prix de l'offre ; (8) mouvement du perp Bybit 500 ms ($, sens favorable) ; (9) flux agressif net 500 ms (k$, sens favorable) ; (10) log volume exécuté sur l'offre 500 ms. « Sens favorable » = sens qui rend l'offre trop bon marché (BTC monte pour l'offre Up, baisse pour l'offre Down). Flux agressifs absents avant le 12.10 (mis à 0).

| Modèle (horizon) | Période | Instants | Événements | Taux | AUC [IC 90 % par cycle] | Brier | Brier sans modèle (taux d'apprentissage) |
|---|---|---|---|---|---|---|---|
| retrait (500 ms) | validation | 318 892 | 29 525 | 9,3 % | 0,747 [0,742 ; 0,751] | 0,0784 | 0,0843 |
| retrait (500 ms) | test | 309 912 | 28 564 | 9,2 % | 0,759 [0,754 ; 0,763] | 0,0774 | 0,0840 |
| retrait (200 ms) | validation | 318 931 | 15 210 | 4,8 % | 0,813 | 0,0424 | 0,0455 |
| retrait (200 ms) | test | 309 946 | 14 754 | 4,8 % | 0,823 | 0,0420 | 0,0454 |
| consommation (500 ms) | validation | 318 892 | 11 450 | 3,6 % | 0,772 [0,767 ; 0,776] | 0,0332 | 0,0347 |
| consommation (500 ms) | test | 309 912 | 10 322 | 3,3 % | 0,765 [0,760 ; 0,769] | 0,0312 | 0,0323 |
| consommation (200 ms) | validation | 318 931 | 5 692 | 1,8 % | 0,855 | 0,0168 | 0,0175 |
| consommation (200 ms) | test | 309 946 | 5 247 | 1,7 % | 0,850 | 0,0161 | 0,0167 |

**Calibration — retrait (500 ms)** (déciles de probabilité prédite : prédit moyen → observé)

| Décile | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| validation | 1,9 % → 1,1 % | 2,7 % → 2,3 % | 3,5 % → 3,3 % | 4,3 % → 4,4 % | 5,4 % → 6,0 % | 6,9 % → 7,8 % | 9,3 % → 9,5 % | 12,7 % → 13,0 % | 17,8 % → 18,3 % | 31,1 % → 26,8 % |
| test | 1,9 % → 1,0 % | 2,7 % → 1,9 % | 3,5 % → 2,9 % | 4,3 % → 4,0 % | 5,4 % → 5,7 % | 7,1 % → 7,6 % | 9,7 % → 9,7 % | 13,2 % → 13,1 % | 18,4 % → 18,5 % | 31,9 % → 27,9 % |

**Calibration — consommation (500 ms)** (déciles de probabilité prédite : prédit moyen → observé)

| Décile | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| validation | 0,5 % → 0,5 % | 0,7 % → 0,7 % | 0,9 % → 1,0 % | 1,2 % → 1,3 % | 1,6 % → 1,8 % | 2,3 % → 2,3 % | 3,4 % → 3,1 % | 5,0 % → 4,6 % | 7,4 % → 7,5 % | 14,4 % → 13,1 % |
| test | 0,5 % → 0,4 % | 0,7 % → 0,6 % | 0,9 % → 1,0 % | 1,2 % → 1,3 % | 1,6 % → 1,7 % | 2,3 % → 2,3 % | 3,6 % → 3,2 % | 5,3 % → 4,4 % | 7,7 % → 6,8 % | 14,8 % → 11,6 % |

**AUC de chaque variable seule (test, horizon 500 ms)** et coefficient standardisé du modèle

| Variable | AUC retrait | coef. retrait | AUC consommation | coef. consommation |
|---|---|---|---|---|
| déséquilibre du microprix vers l'offre | 0,714 | 0,11 | 0,739 | 0,38 |
| log taille de l'offre | 0,260 | -0,64 | 0,248 | -0,59 |
| écart acheteur-vendeur (‰) | 0,510 | -0,04 | 0,511 | -0,02 |
| variation log taille de l'offre 200 ms | 0,389 | 0,01 | 0,366 | -0,02 |
| variation log taille d'en face 200 ms | 0,584 | 0,16 | 0,601 | 0,16 |
| log âge du meilleur prix (ms) | 0,389 | -0,26 | 0,418 | -0,12 |
| logit du prix de l'offre | 0,568 | 0,13 | 0,550 | 0,04 |
| mouvement du perp Bybit 500 ms ($, sens favorable) | 0,562 | 0,09 | 0,586 | 0,12 |
| flux agressif net 500 ms (k$, sens favorable) | 0,564 | 0,01 | 0,584 | 0,00 |
| log volume exécuté sur l'offre 500 ms | 0,537 | 0,11 | 0,543 | 0,11 |

**H545 — retraits et consommations ont-ils des précurseurs différents ?** (test) : le modèle retrait classe les consommations avec AUC 0,763 (modèle consommation : 0,765) ; le modèle consommation classe les retraits avec AUC 0,751 (modèle retrait : 0,759). Un modèle unique « disparition » : AUC 0,759 sur les retraits, 0,766 sur les consommations.

## Phase 4 — course avec nos délais réels

Alerte = probabilité ≥ 95e centile de la validation (seuil fixé sur la validation, mesuré sur le test). Ordre parti à T + 0,1 ms, arrivé chez Polymarket à T + 14,1 ms (aller simple) ou T + 28,1 ms (aller-retour complet), comparé à l'heure Polymarket de la disparition. « Encore achetable » = le niveau est encore au meilleur prix avec ≥ 1 part dans le carnet reçu à T + 28 ms. Valeur à 5 s = milieu du carnet 5 s plus tard − prix payé − frais (‰ par part, 1 ‰ = 0,1 c).

| Modèle | Instants | Seuil | Disparition (cette cause) ≤ 522 ms | Arrivé avant la disparition : aller simple · aller-retour | Arrivé avant la 1re baisse | Encore achetable à +28 ms | Valeur à 5 s (‰/part) moy. [IC 90 % par cycle] · méd. |
|---|---|---|---|---|---|---|---|
| retrait — alerte (test) | 18 882 | 0,284 | 6 510 (34,5 %) | 60,8 % · 53,2 % | 43,3 % | 84,3 % | -2,8 [-4,3 ; -1,4] · -1,9 |
| retrait — instants au hasard (test) | 313 390 | — | 31 041 (9,9 %) | 81,5 % · 77,5 % | 43,2 % | 98,3 % | -18,1 [-18,4 ; -17,8] · -17,0 |
| consommation — alerte (test) | 18 506 | 0,127 | 2 786 (15,1 %) | 65,5 % · 59,8 % | 47,6 % | 83,9 % | 0,0 [-1,5 ; 1,5] · -1,5 |
| consommation — instants au hasard (test) | 313 390 | — | 11 194 (3,6 %) | 83,3 % · 80,3 % | 45,2 % | 98,3 % | -18,1 [-18,4 ; -17,8] · -17,0 |

## Phase 5 — fantômes R, S, RS contre le moteur C (mêmes signaux, simulation hors ligne)

Signaux : cohortes A et B de `rapide.json` (les seules où le moteur C est calculé), réglés, dont le cycle est enregistré : 314 (apprentissage 163, validation 80, test 71). Moteur C = décision enregistrée en direct (« envoie », plafond) ; exécution simulée sur le carnet reconstruit reçu à T + 28 ms (aller-retour), 50 $ par signal, frais 0,07·p·(1−p) par part, règlement par `gagnant`. **R** = C + achat immédiat (limite = prix du signal) des signaux REFUSÉS par C quand P(retrait) ≥ seuil ; **S** = idem avec P(consommation) ; **RS** = l'un ou l'autre. Seuils choisis sur apprentissage + validation seulement (centiles 50, 60, 70, 80, 90 % des probabilités des signaux refusés, ou « jamais ») : R 0,367 (gain apprentissage+validation +88 $), S 0,123 (+139 $). Jackpot = gain ≥ 4 × la mise. IC par bootstrap des cycles (10000 tirages) ; Bonferroni sur 3 variantes = IC à 96,7 %.

| Période | Stratégie | P&L | Δ contre C [IC 90 %] | IC Bonferroni 96,7 % | Achats | Jackpots | Signaux ajoutés (exécutés) | Gains · pertes des ajouts | Jackpots ajoutés | Perte max. (drawdown) | Capital engagé (max par cycle) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| apprentissage | moteur C | +2 215 $ | — | — | 85 | 5 | — | — | — | 424 $ | 3 959 $ |
| | R | +2 256 $ | +40 $ [−218 $ ; +330 $] | [−288 $ ; +442 $] | 104 | 7 | 22 (19) | +259 $ · −219 $ | 2 | 450 $ | 4 266 $ (100 $) |
| | S | +2 308 $ | +93 $ [−140 $ ; +363 $] | [−199 $ ; +447 $] | 110 | 9 | 30 (25) | +274 $ · −182 $ | 4 | 450 $ | 4 238 $ (100 $) |
| | RS | +2 342 $ | +127 $ [−154 $ ; +425 $] | [−221 $ ; +529 $] | 113 | 10 | 33 (28) | +359 $ · −232 $ | 5 | 450 $ | 4 304 $ (100 $) |
| validation | moteur C | +218 $ | — | — | 47 | 1 | — | — | — | 363 $ | 2 206 $ |
| | R | +266 $ | +48 $ [−84 $ ; +248 $] | [−106 $ ; +317 $] | 56 | 1 | 11 (9) | +100 $ · −52 $ | 0 | 386 $ | 2 286 $ (100 $) |
| | S | +265 $ | +47 $ [−86 $ ; +240 $] | [−108 $ ; +294 $] | 59 | 2 | 14 (12) | +109 $ · −62 $ | 1 | 377 $ | 2 297 $ (100 $) |
| | RS | +265 $ | +47 $ [−85 $ ; +245 $] | [−108 $ ; +308 $] | 59 | 2 | 14 (12) | +109 $ · −62 $ | 1 | 377 $ | 2 297 $ (100 $) |
| test | moteur C | +299 $ | — | — | 43 | 0 | — | — | — | 272 $ | 2 094 $ |
| | R | +143 $ | −155 $ [−307 $ ; −31 $] | [−361 $ ; −1 $] | 51 | 0 | 9 (8) | +12 $ · −167 $ | 0 | 331 $ | 2 269 $ (100 $) |
| | S | +107 $ | −192 $ [−347 $ ; −63 $] | [−403 $ ; −34 $] | 55 | 0 | 15 (12) | +12 $ · −203 $ | 0 | 345 $ | 2 305 $ (100 $) |
| | RS | +107 $ | −192 $ [−343 $ ; −63 $] | [−392 $ ; −35 $] | 55 | 0 | 15 (12) | +12 $ · −203 $ | 0 | 345 $ | 2 305 $ (100 $) |

**Exploratoire (pas un verdict)** — sur le test, ajouts des signaux refusés par C pour chaque seuil de la grille :

| Probabilité | Seuil | Gain app.+val. | Signaux ajoutés test | exécutés | P&L test des ajouts |
|---|---|---|---|---|---|
| retrait | 0,256 | +50 $ | 14 | 12 | −228 $ |
| retrait | 0,294 | −18 $ | 13 | 11 | −213 $ |
| retrait | 0,367 | +88 $ | 9 | 8 | −155 $ |
| retrait | 0,435 | +26 $ | 6 | 5 | −48 $ |
| retrait | 0,481 | −66 $ | 2 | 2 | −43 $ |
| consommation | 0,093 | −1 $ | 16 | 13 | −242 $ |
| consommation | 0,123 | +139 $ | 15 | 12 | −192 $ |
| consommation | 0,150 | +34 $ | 11 | 10 | −126 $ |
| consommation | 0,190 | −63 $ | 6 | 6 | −98 $ |
| consommation | 0,277 | −21 $ | 2 | 2 | +12 $ |

**Diagnostic sur tous les signaux du bot (toutes règles)** — la probabilité de retrait / consommation de l'offre visée annonce-t-elle un signal gagnant ? validation (479 signaux) : AUC retrait 0,543, consommation 0,571, prix seul (bas = gagne) 0,291 ; test (452 signaux) : AUC retrait 0,477, consommation 0,521, prix seul (bas = gagne) 0,271.

Contrôles : prix du meilleur vendeur reconstruit = prix du signal pour 1645/1833 signaux ; P&L simulé du moteur C contre le P&L enregistré en direct par le bot (même signal) : écart médian 0,07 $, total simulé +2 732 $ contre +2 400 $ enregistré (175 envois ; le bot utilise des frais 0,072·p·(1−p) et son aller-retour mesuré ~30–36 ms).

Durée d'exécution : 271 s.
