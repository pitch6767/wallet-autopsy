# Bot95 — Test de robustesse H816 (PÉRIODE RÉSERVÉE) — protocole figé

Généré le 14.10.2026 07:38 UTC. Cycles avec carnet Dublin : 193 ; signaux réglés : 689 ; décisions du protocole (prix 0,20–0,50, une par cycle et côté, la première) : **108** sur 98 cycles. Mise 20 $ par décision. IC 90 % par cycles. Aucun ordre ; R4 et fantômes inchangés.

## 1. Résultat principal et sensibilité à la latence

| Stratégie | Délai | Décisions | Exécutées | Taux de gain | Prix moyen payé | P&L ($) | P&L par $ engagé (IC 90 %) | P&L par jeton (c, IC 90 %) | Médiane ($) | 5 meilleures / total | Drawdown ($) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| protocole H816 (20 $, 0,20–0,50, 1 décision) | 164 ms (protocole) | 108 | 88 | 24 % | 0.283 | -362 | -23.2 % [-47.9 ; +1.5] | -6.1 [-12.6 ; +0.4] | -19.53 | nan % | 431 |
| protocole H816 (20 $, 0,20–0,50, 1 décision) | 200 ms (diagnostic) | 108 | 84 | 23 % | 0.279 | -393 | -26.5 % [-51.5 ; +0.4] | -6.9 [-13.4 ; +0.0] | -15.93 | nan % | 449 |
| protocole H816 (20 $, 0,20–0,50, 1 décision) | 250 ms (diagnostic) | 108 | 79 | 24 % | 0.278 | -381 | -26.0 % [-52.4 ; +0.7] | -6.7 [-12.9 ; +0.2] | -19.53 | nan % | 435 |
| protocole H816 (20 $, 0,20–0,50, 1 décision) | 500 ms (diagnostic) | 108 | 66 | 20 % | 0.264 | -354 | -28.4 % [-58.8 ; +2.8] | -6.9 [-14.2 ; +0.8] | +0.00 | nan % | 417 |
| stratégie actuelle (tous signaux, 50 $) | 164 ms (protocole) | 689 | 526 | 23 % | 0.203 | -487 | -2.6 % [-29.8 ; +28.0] | -0.4 [-4.4 ; +3.9] | -7.04 | nan % | 2799 |
| stratégie actuelle (tous signaux, 50 $) | 200 ms (diagnostic) | 689 | 498 | 22 % | 0.201 | -716 | -3.9 % [-32.5 ; +25.4] | -0.6 [-4.5 ; +3.7] | -5.07 | nan % | 2672 |
| stratégie actuelle (tous signaux, 50 $) | 250 ms (diagnostic) | 689 | 463 | 22 % | 0.201 | -792 | -4.5 % [-34.4 ; +26.8] | -0.6 [-4.9 ; +3.9] | -3.45 | nan % | 2614 |
| stratégie actuelle (tous signaux, 50 $) | 500 ms (diagnostic) | 689 | 389 | 18 % | 0.189 | -927 | -6.1 % [-38.6 ; +30.3] | -0.8 [-5.2 ; +3.9] | +0.00 | nan % | 2665 |

## 2. Stabilité chronologique (protocole, 164 ms)

| Stratégie | Délai | Décisions | Exécutées | Taux de gain | Prix moyen payé | P&L ($) | P&L par $ engagé (IC 90 %) | P&L par jeton (c, IC 90 %) | Médiane ($) | 5 meilleures / total | Drawdown ($) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1re moitié des cycles | 164 ms (protocole) | 51 | 39 | 26 % | 0.276 | -100 | -14.7 % [-51.6 ; +24.9] | -3.8 [-13.7 ; +6.8] | -10.11 | nan % | 173 |
| 2e moitié des cycles | 164 ms (protocole) | 57 | 49 | 22 % | 0.289 | -263 | -29.7 % [-60.2 ; +3.2] | -8.0 [-16.2 ; +1.1] | -20.00 | nan % | 304 |

## 3. Contrôle sur tous les cycles (mesure directe de Dublin, sans reconstruction du carnet)

Achetable mesuré par Dublin au prix du signal à 100 / 250 / 500 ms (champ « apres », budget 50 $) ramené à une mise de 20 $ (si le coût Dublin dépasse 20 $, quantité réduite proportionnellement). Tous les cycles, y compris ceux sans fichier de carnet.

| Stratégie | Délai | Décisions | Exécutées | Taux de gain | Prix moyen payé | P&L ($) | P&L par $ engagé (IC 90 %) | P&L par jeton (c, IC 90 %) | Médiane ($) | 5 meilleures / total | Drawdown ($) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| protocole, tous cycles | 100 ms | 149 | 123 | 29 % | 0.289 | -198 | -9.3 % [-30.6 ; +12.6] | -2.5 [-8.4 ; +3.5] | -10.92 | nan % | 413 |
| protocole, tous cycles | 250 ms | 149 | 103 | 27 % | 0.279 | -310 | -16.3 % [-39.6 ; +7.5] | -4.2 [-10.2 ; +1.9] | -1.58 | nan % | 450 |
| protocole, tous cycles | 500 ms | 149 | 83 | 23 % | 0.262 | -271 | -17.3 % [-47.0 ; +14.6] | -4.1 [-11.1 ; +3.1] | +0.00 | nan % | 303 |

(149 décisions sur 134 cycles.)

## Lecture
- Par $ engagé = rendement de la mise ; par jeton = gain moyen par part achetée (une mise fixe achète plus de jetons quand le prix est bas).
- Fragilité : si le résultat devient nul ou négatif dès 200 ms, la stratégie est jugée extrêmement fragile, même si 164 ms est positif.
- Le verdict se fera sur la période réservée (--hors-echantillon), mêmes paramètres, sans aucun ajustement.
