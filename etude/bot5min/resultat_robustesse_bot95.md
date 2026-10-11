# Bot95 — Test de robustesse H816 (avant le 13.10) — protocole figé

Généré le 11.10.2026 19:26 UTC. Cycles avec carnet Dublin : 55 ; signaux réglés : 278 ; décisions du protocole (prix 0,20–0,50, une par cycle et côté, la première) : **64** sur 53 cycles. Mise 20 $ par décision. IC 90 % par cycles. Aucun ordre ; R4 et fantômes inchangés.

## 1. Résultat principal et sensibilité à la latence

| Stratégie | Délai | Décisions | Exécutées | Taux de gain | Prix moyen payé | P&L ($) | P&L par $ engagé (IC 90 %) | P&L par jeton (c, IC 90 %) | Médiane ($) | 5 meilleures / total | Drawdown ($) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| protocole H816 (20 $, 0,20–0,50, 1 décision) | 164 ms (protocole) | 64 | 60 | 42 % | 0.284 | +283 | +28.0 % [-8.8 ; +67.2] | +7.5 [-2.4 ; +18.0] | -13.40 | 121 % | 119 |
| protocole H816 (20 $, 0,20–0,50, 1 décision) | 200 ms (diagnostic) | 64 | 58 | 41 % | 0.282 | +255 | +26.3 % [-12.7 ; +68.0] | +6.9 [-3.3 ; +18.0] | -10.70 | 136 % | 124 |
| protocole H816 (20 $, 0,20–0,50, 1 décision) | 250 ms (diagnostic) | 64 | 53 | 38 % | 0.273 | +238 | +24.4 % [-16.0 ; +66.7] | +6.3 [-4.4 ; +17.8] | -17.79 | 148 % | 163 |
| protocole H816 (20 $, 0,20–0,50, 1 décision) | 500 ms (diagnostic) | 64 | 47 | 34 % | 0.263 | +281 | +31.5 % [-12.4 ; +78.3] | +8.0 [-3.1 ; +19.6] | +0.00 | 126 % | 112 |
| stratégie actuelle (tous signaux, 50 $) | 164 ms (protocole) | 278 | 229 | 34 % | 0.242 | +4141 | +56.4 % [-1.8 ; +114.4] | +11.4 [-0.3 ; +23.2] | -3.55 | 59 % | 908 |
| stratégie actuelle (tous signaux, 50 $) | 200 ms (diagnostic) | 278 | 218 | 33 % | 0.242 | +4049 | +56.9 % [-3.5 ; +121.9] | +11.3 [-0.3 ; +23.9] | -2.94 | 60 % | 937 |
| stratégie actuelle (tous signaux, 50 $) | 250 ms (diagnostic) | 278 | 194 | 29 % | 0.234 | +3672 | +53.6 % [-2.7 ; +116.9] | +10.6 [-0.5 ; +22.6] | +0.00 | 65 % | 947 |
| stratégie actuelle (tous signaux, 50 $) | 500 ms (diagnostic) | 278 | 166 | 28 % | 0.222 | +2640 | +42.8 % [-12.6 ; +97.9] | +8.3 [-2.0 ; +19.2] | +0.00 | 74 % | 942 |

## 2. Stabilité chronologique (protocole, 164 ms)

| Stratégie | Délai | Décisions | Exécutées | Taux de gain | Prix moyen payé | P&L ($) | P&L par $ engagé (IC 90 %) | P&L par jeton (c, IC 90 %) | Médiane ($) | 5 meilleures / total | Drawdown ($) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1re moitié des cycles | 164 ms (protocole) | 33 | 30 | 47 % | 0.280 | +243 | +46.0 % [-3.5 ; +99.7] | +12.1 [-1.7 ; +26.7] | +0.00 | 124 % | 57 |
| 2e moitié des cycles | 164 ms (protocole) | 31 | 30 | 37 % | 0.289 | +40 | +8.2 % [-42.2 ; +65.5] | +2.2 [-11.5 ; +18.0] | -15.47 | 761 % | 119 |

## 3. Contrôle sur tous les cycles (mesure directe de Dublin, sans reconstruction du carnet)

Achetable mesuré par Dublin au prix du signal à 100 / 250 / 500 ms (champ « apres », budget 50 $) ramené à une mise de 20 $ (si le coût Dublin dépasse 20 $, quantité réduite proportionnellement). Tous les cycles, y compris ceux sans fichier de carnet.

| Stratégie | Délai | Décisions | Exécutées | Taux de gain | Prix moyen payé | P&L ($) | P&L par $ engagé (IC 90 %) | P&L par jeton (c, IC 90 %) | Médiane ($) | 5 meilleures / total | Drawdown ($) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| protocole, tous cycles | 100 ms | 104 | 94 | 39 % | 0.278 | +467 | +29.7 % [+0.2 ; +57.8] | +7.9 [+0.6 ; +15.8] | -4.23 | 71 % | 188 |
| protocole, tous cycles | 250 ms | 104 | 78 | 37 % | 0.267 | +353 | +24.9 % [-6.1 ; +57.7] | +6.3 [-1.6 ; +14.8] | +0.00 | 98 % | 245 |
| protocole, tous cycles | 500 ms | 104 | 69 | 35 % | 0.259 | +414 | +31.6 % [-4.8 ; +67.7] | +7.9 [-0.7 ; +16.7] | +0.00 | 85 % | 174 |

(104 décisions sur 88 cycles.)

## Lecture
- Par $ engagé = rendement de la mise ; par jeton = gain moyen par part achetée (une mise fixe achète plus de jetons quand le prix est bas).
- Fragilité : si le résultat devient nul ou négatif dès 200 ms, la stratégie est jugée extrêmement fragile, même si 164 ms est positif.
- Le verdict se fera sur la période réservée (--hors-echantillon), mêmes paramètres, sans aucun ajustement.
