# Bot95 — Tout combiné avec tout (PRÉLIMINAIRE, non validé statistiquement)

Généré le 11.10.2026 13:52 UTC. 17653 trades fantômes BTC de 100 stratégies (+ portefeuille TOUS : 1336 trades), du 06.10 10:05 au 11.10 12:50 UTC. Apprentissage avant le 10.10 02:40 UTC, validation après. Période réservée (≥ 13.10) non lue.

Combinaisons testées : 892 (1 à 3 filtres, au moins 40 trades en apprentissage et 20 en validation pour le classement).

## Le contrôle qui compte : combien de « gagnants » le hasard fabrique-t-il ?

- Données réelles : parmi les 300 meilleures combinaisons en apprentissage, **100** restent positives en validation.
- Résultats mélangés au hasard (aucun vrai signal) : **157** sur 300 restent positives en validation.
- Si les deux nombres sont proches, les « meilleures combinaisons » sont surtout du hasard sélectionné après coup.

## Les 30 meilleures combinaisons en apprentissage, et ce qu'elles font ensuite

| Stratégie | Filtres | Trades appr. | Résultat appr. | par $ | Trades valid. | Résultat valid. | par $ valid. |
|---|---|---|---|---|---|---|---|
| corrige_desaccord_20 | écart 0.2–0.3 | 54 | +1941 $ | +1.04 | 107 | -696 $ | -0.21 |
| desaccord_30_zone_+_modele_monte | prix 0.15–0.35 + écart 0.3–+ | 44 | +1305 $ | +0.91 | 53 | +1377 $ | +0.98 |
| V2-G_jury_des_bourses | restant 120–180 s + écart 0.2–0.3 | 46 | +1754 $ | +0.91 | 69 | -962 $ | -0.33 |
| desaccord_30_zone_+_modele_monte | prix 0.15–0.35 + côté Down | 57 | +1736 $ | +0.90 | 54 | +729 $ | +0.44 |
| desaccord_30_zone_+_modele_monte | côté Down | 59 | +1728 $ | +0.87 | 54 | +729 $ | +0.44 |
| desaccord_30_zone_+_modele_monte | écart 0.3–+ | 46 | +1297 $ | +0.87 | 53 | +1377 $ | +0.98 |
| V2-B_hors_60-89_s | écart 0.2–0.3 + côté Down | 45 | +1410 $ | +0.78 | 40 | -357 $ | -0.38 |
| desaccord_30_zone_+_modele_monte | prix 0.15–0.35 + restant 60–120 s | 51 | +1452 $ | +0.75 | 36 | +489 $ | +0.46 |
| desaccord_20_sans_nuit | écart 0.2–0.3 + côté Down | 40 | +1115 $ | +0.75 | 22 | -156 $ | -0.30 |
| V2-D_perp_120-269_s | restant 120–180 s + nuit 0–8 h | 41 | +1317 $ | +0.74 | 28 | -555 $ | -0.45 |
| V2-B_hors_60-89_s | écart 0.2–0.3 | 80 | +2244 $ | +0.74 | 85 | -43 $ | -0.02 |
| desaccord_20_sans_nuit | écart 0.2–0.3 | 68 | +1886 $ | +0.74 | 54 | +308 $ | +0.21 |
| desaccord_30_zone_+_Binance_et_perp_+_sortie_modele_-10_+_pas_Poly_qui_baisse_+_taille_25_50 | prix 0.15–0.35 + côté Down | 57 | +1255 $ | +0.72 | 102 | +55 $ | +0.02 |
| TOUS (premier trade du cycle et du côté) | restant 180–240 s + écart 0.2–0.3 | 47 | +1302 $ | +0.72 | 51 | -121 $ | -0.07 |
| desaccord_30_zone_+_Binance_et_perp_+_sortie_modele_-10_+_pas_Poly_qui_baisse_+_taille_25_50 | côté Down | 59 | +1289 $ | +0.71 | 102 | +55 $ | +0.02 |
| desaccord_30_zone_+_modele_monte | prix 0.15–0.35 | 105 | +2575 $ | +0.70 | 105 | +1305 $ | +0.40 |
| desaccord_30_zone_+_modele_monte | restant 60–120 s | 53 | +1374 $ | +0.68 | 36 | +489 $ | +0.46 |
| corrige_V2-F_ecart_qui_grandit | écart 0.2–0.3 | 65 | +1542 $ | +0.67 | 119 | -359 $ | -0.10 |
| V2-D_perp_120-269_s | prix 0.00–0.15 | 63 | +1603 $ | +0.65 | 45 | +62 $ | +0.03 |
| V2-F_+_plus_de_120_s | écart 0.2–0.3 | 56 | +1394 $ | +0.64 | 113 | +29 $ | +0.01 |
| desaccord_30_zone_+_Binance_et_perp_+_sortie_modele_-10_+_pas_Poly_qui_baisse_+_taille_25_50 | nuit 0–8 h | 48 | +979 $ | +0.64 | 58 | +459 $ | +0.30 |
| V2-C_perp | écart 0.2–0.3 + côté Down | 50 | +1489 $ | +0.64 | 63 | -1254 $ | -0.42 |
| desaccord_30_zone_+_Binance_et_perp_+_sortie_modele_-10_+_pas_Poly_qui_baisse_+_taille_25_50 | prix 0.15–0.35 + nuit 0–8 h | 47 | +932 $ | +0.62 | 58 | +459 $ | +0.30 |
| desaccord_30_zone_+_Binance_et_perp_+_sortie_modele_-10_+_pas_Poly_qui_baisse_+_taille_25_50 | prix 0.15–0.35 | 99 | +1911 $ | +0.62 | 198 | +447 $ | +0.09 |
| V2-E_persistant | restant 120–180 s + écart 0.2–0.3 | 44 | +1382 $ | +0.61 | 44 | -804 $ | -0.42 |
| corrige_V2-F_+_pas_les_deux_baissent | écart 0.2–0.3 | 64 | +1387 $ | +0.59 | 123 | -453 $ | -0.12 |
| V2-B_hors_60-89_s | prix 0.15–0.35 + écart 0.2–0.3 | 47 | +1063 $ | +0.59 | 79 | -14 $ | -0.01 |
| V2-H_veto_complet | prix 0.00–0.15 | 77 | +2028 $ | +0.59 | 27 | -849 $ | -0.70 |
| desaccord_30_zone_+_Binance_et_perp_+_sortie_modele_-10_+_pas_Poly_qui_baisse_+_taille_25_50 | restant 60–120 s | 62 | +1124 $ | +0.58 | 83 | +414 $ | +0.22 |
| V2-G_jury_des_bourses | restant 120–180 s + nuit 0–8 h | 43 | +1042 $ | +0.58 | 35 | -1317 $ | -0.88 |

## Les combinaisons positives sur les DEUX périodes, triées par la validation (au moins 30 trades dans chaque)

| Stratégie | Filtres | Trades appr. | par $ appr. | Trades valid. | par $ valid. | Résultat total |
|---|---|---|---|---|---|---|
| desaccord_30_zone_+_modele_monte | prix 0.15–0.35 + écart 0.3–+ | 44 | +0.91 | 53 | +0.98 | +2682 $ |
| desaccord_30_zone_+_modele_monte | écart 0.3–+ | 46 | +0.87 | 53 | +0.98 | +2674 $ |
| desaccord_30_zone_0,15-0,35_+_Binance_et_perp | écart 0.3–+ | 42 | +0.52 | 57 | +0.50 | +1618 $ |
| desaccord_30_zone_0,15-0,35_+_Binance_et_perp | prix 0.15–0.35 + écart 0.3–+ | 40 | +0.55 | 57 | +0.50 | +1627 $ |
| TOUS (premier trade du cycle et du côté) | restant 120–180 s + écart 0.2–0.3 | 52 | +0.49 | 38 | +0.46 | +1625 $ |
| desaccord_30_zone_+_modele_monte | restant 60–120 s | 53 | +0.68 | 36 | +0.46 | +1863 $ |
| desaccord_30_zone_+_modele_monte | prix 0.15–0.35 + restant 60–120 s | 51 | +0.75 | 36 | +0.46 | +1942 $ |
| desaccord_30_zone_+_modele_monte | côté Down | 59 | +0.87 | 54 | +0.44 | +2456 $ |
| desaccord_30_zone_+_modele_monte | prix 0.15–0.35 + côté Down | 57 | +0.90 | 54 | +0.44 | +2465 $ |
| desaccord_30_zone_+_Binance_et_perp_+_sortie_modele_-10 | écart 0.3–+ | 42 | +0.51 | 57 | +0.40 | +1421 $ |
| desaccord_30_zone_+_Binance_et_perp_+_sortie_modele_-10 | prix 0.15–0.35 + écart 0.3–+ | 40 | +0.52 | 57 | +0.40 | +1399 $ |
| desaccord_30_zone_+_modele_monte | prix 0.15–0.35 | 105 | +0.70 | 105 | +0.40 | +3880 $ |
| desaccord_30_zone_+_modele_monte | côté Up | 50 | +0.40 | 51 | +0.35 | +1326 $ |
| desaccord_30_zone_+_modele_monte | prix 0.15–0.35 + côté Up | 48 | +0.47 | 51 | +0.35 | +1415 $ |
| desaccord_30_zone_+_Binance_et_perp_+_sortie_modele_-10_+_pas_Poly_qui_baisse_+_taille_25_50 | nuit 0–8 h | 48 | +0.64 | 58 | +0.30 | +1438 $ |
| desaccord_30_zone_+_Binance_et_perp_+_sortie_modele_-10_+_pas_Poly_qui_baisse_+_taille_25_50 | prix 0.15–0.35 + nuit 0–8 h | 47 | +0.62 | 58 | +0.30 | +1391 $ |
| desaccord_30_zone_+_Binance_et_perp_+_sortie_modele_-10 | restant 60–120 s + côté Down | 40 | +0.27 | 40 | +0.28 | +779 $ |
| TOUS (premier trade du cycle et du côté) | restant 120–180 s | 188 | +0.25 | 102 | +0.26 | +2932 $ |
| desaccord_30_zone_+_Binance_et_perp_+_sortie_modele_-10_+_pas_Poly_qui_baisse_+_taille_25_50 | restant 60–120 s | 62 | +0.58 | 83 | +0.22 | +1538 $ |
| desaccord_30_zone_+_Binance_et_perp_+_sortie_modele_-10_+_pas_Poly_qui_baisse_+_taille_25_50 | prix 0.15–0.35 + restant 60–120 s | 59 | +0.56 | 83 | +0.22 | +1456 $ |
| corrige_zone_+_Binance_et_perp_+_sortie_-10 | prix 0.15–0.35 | 50 | +0.21 | 114 | +0.21 | +1242 $ |
| desaccord_20_sans_nuit | écart 0.2–0.3 | 68 | +0.74 | 54 | +0.21 | +2194 $ |
| TOUS (premier trade du cycle et du côté) | prix 0.15–0.35 + restant 120–180 s | 97 | +0.21 | 61 | +0.42 | +1827 $ |
| TOUS (premier trade du cycle et du côté) | côté Down + après-midi 14–20 h | 61 | +0.30 | 60 | +0.20 | +1188 $ |
| desaccord_30_zone_+_sortie_modele_-10 | nuit 0–8 h | 63 | +0.19 | 74 | +0.27 | +1118 $ |
| TOUS (premier trade du cycle et du côté) | restant 120–180 s + côté Down | 97 | +0.35 | 42 | +0.18 | +1662 $ |
| TOUS (premier trade du cycle et du côté) | prix 0.15–0.35 + restant 180–240 s + côté Up | 56 | +0.17 | 52 | +0.39 | +1110 $ |
| desaccord_30_zone_+_sortie_modele_-10 | prix 0.15–0.35 + nuit 0–8 h | 62 | +0.17 | 74 | +0.27 | +1054 $ |
| desaccord_30_zone_+_sortie_modele_-10 | restant 60–120 s + côté Down | 47 | +0.16 | 45 | +0.16 | +498 $ |
| desaccord_30_zone_0,15-0,35_+_Binance_et_perp | restant 60–120 s + côté Down | 40 | +0.16 | 40 | +0.26 | +581 $ |

**Filtres qui reviennent le plus souvent dans les combinaisons positives sur les deux périodes** : prix 0.15–0.35 (13), restant 60–120 s (7), côté Down (7), écart 0.3–+ (6), restant 120–180 s (4), nuit 0–8 h (4), côté Up (3), écart 0.2–0.3 (2), après-midi 14–20 h (1), restant 180–240 s (1)

## Limites
- Beaucoup de combinaisons testées : certaines « marchent » par chance (voir le témoin mélangé).
- Les trades fantômes supposent l'achat au prix vu (pas de retard de 150 ms, pas de file).
- Seul le test sur la période réservée (cycles ≥ 13.10) peut confirmer un filtre ; aucun filtre n'est ajouté sans ton accord.
