# Bot95 — H818 : sélection adverse et qualité des exécutions — PRÉLIMINAIRE (hors ligne)

Généré le 11.10.2026 19:44 UTC. Cycles Dublin : 55 ; décisions H816 : 64 ; décisions « tous signaux » (mêmes règles, sans filtre de prix) : 77. Apprentissage < 12:30 UTC, test après. Aucun ordre ; R4, H816, fantômes inchangés.

## 0. Données manquantes (avant toute conclusion)
- Identifiants d'ordres : absents → âge d'un ORDRE non mesurable ; on mesure la durée de présence du NIVEAU de prix.
- Carnet suivi à ±3 c du meilleur prix entre deux photos complètes (10 s) ; niveaux présents depuis une photo : durée minorée.
- Prix des bourses : une valeur par 50 ms. Mouvements signés dans le sens du billet acheté (+ = favorable), en points de base.
- Une seule journée ; échantillons petits : les IC par cycles sont larges.

## 1. H818-B — Groupes d'exécution (H816, 164 ms, 20 $)

| Groupe | Signaux | Taux de gain | Prix | Réalisé : P&L ($) | Réalisé par $ | Contrefactuel NON réalisable par $ (20 $ au prix a0) | Mouv. Binance 1 s avant (pb) | Mouv. Binance pendant 164 ms (pb) | Annulations / baisse au prix |
|---|---|---|---|---|---|---|---|---|---|
| A — exécuté entièrement | 43 | 33 % | 0.27 | +159 | +18 % | +14 % (non réalisable) | -0.00 | +0.00 | 95 % |
| B — partiel | 17 | 65 % | 0.29 | +124 | +83 % | +110 % (non réalisable) | +0.00 | +0.00 | 94 % |
| C — offre disparue | 2 | 0 % | 0.31 | +0 | +nan % | -100 % (non réalisable) | +0.00 | +0.00 | 95 % |
| D — autre raison | 2 | 0 % | 0.21 | +0 | +nan % | -100 % (non réalisable) | -0.08 | +0.00 | 100 % |

## 1. H818-B — Groupes d'exécution (tous signaux, 164 ms, 20 $)

| Groupe | Signaux | Taux de gain | Prix | Réalisé : P&L ($) | Réalisé par $ | Contrefactuel NON réalisable par $ (20 $ au prix a0) | Mouv. Binance 1 s avant (pb) | Mouv. Binance pendant 164 ms (pb) | Annulations / baisse au prix |
|---|---|---|---|---|---|---|---|---|---|
| A — exécuté entièrement | 52 | 33 % | 0.29 | +230 | +22 % | +18 % (non réalisable) | -0.00 | +0.00 | 95 % |
| B — partiel | 18 | 56 % | 0.27 | +105 | +70 % | +75 % (non réalisable) | +0.00 | +0.00 | 90 % |
| C — offre disparue | 5 | 40 % | 0.38 | +0 | +nan % | -31 % (non réalisable) | +0.00 | +0.00 | 86 % |
| D — autre raison | 2 | 0 % | 0.21 | +0 | +nan % | -100 % (non réalisable) | -0.08 | +0.00 | 100 % |

## 2. H818-C — Présence du niveau de prix a0 au moment de la décision (tous signaux)

| Présence du niveau | Signaux | dont minorée | Survie à 164 ms | Taux de remplissage complet | Rendement si rempli | Rendement par signal envoyé | Annulations / baisse | Volume accessible ($) |
|---|---|---|---|---|---|---|---|---|
| 0–50 ms | 29 | 0 | 97 % | 86 % | +45 % | +8.22 $ | 95 % | 3 |
| 50–150 ms | 1 | 0 | 100 % | 100 % | +365 % | +73.05 $ | 100 % | 132 |
| 150–500 ms | 6 | 0 | 100 % | 83 % | -68 % | -12.13 $ | 97 % | 42 |
| 500–∞ ms | 17 | 1 | 76 % | 35 % | +42 % | +4.10 $ | 90 % | 47 |

Sans niveau au prix a0 au moment de la décision (offre déjà partie / signal sur une offre absente) : 24 signaux.

## 3. H818-F — Offres disparues contre offres restées (tous signaux)

| Groupe | Signaux | Taux de gain | Prix | Rendement théorique au prix a0 | Rendement exécutable | Milieu +1 s − a0 | +5 s | Cause : annulation | Profondeur acheteurs / vendeurs (3 niveaux) |
|---|---|---|---|---|---|---|---|---|---|
| disparues | 9 | 67 % | 0.35 | +81 % | +261 % | +15.5 c | +13.5 c | 90 % | 1504 / 185 |
| restées | 44 | 36 % | 0.30 | +25 % | +31 % | -0.5 c | -1.5 c | 95 % | 328 / 685 |

À prix, temps restant et côté égaux : écart (gain − prix) disparues − restées = +27.2 points [IC 90 % -2.8 ; +54.8].

## 4. H818-H — Markouts après remplissage (tous signaux exécutés, c par part, milieu du côté acheté − prix payé hors frais)

| Groupe | Remplis | +100 ms | +250 ms | +500 ms | +1000 ms | +3000 ms | +10000 ms | P&L final par part |
|---|---|---|---|---|---|---|---|---|
| tous | 70 | -0.5 | -0.2 | +0.4 | +0.6 | +0.5 | +0.2 | +7.4 |
| gagnants au règlement | 27 | -0.4 | +0.5 | +1.3 | +1.7 | +0.8 | +2.7 | +72.6 |
| perdants au règlement | 43 | -0.6 | -0.5 | -0.1 | -0.0 | +0.4 | -1.1 | -25.9 |

Markout à 3 s négatif : 35 remplissages, gain au règlement 37 % ; positif ou nul : 35, gain 40 %.

## 5. H818-I — Filtre de survie : P(exécution) × E(P&L | exécution)

Modèles appris sur 41 signaux (apprentissage) ; appliqués aux 36 signaux du test. Règle : envoyer seulement si valeur attendue > 0.

| Politique (test) | Signaux envoyés | Exécutés | P&L ($) | par signal (IC 90 %) | par $ engagé | sans les 5 meilleurs |
|---|---|---|---|---|---|---|
| H816 inchangé | 29 | 28 | +47 | +1.61 [-7.27 ; +11.00] | +10 % | -255 |
| tous signaux sans filtre | 36 | 34 | +72 | +2.00 [-5.90 ; +10.18] | +13 % | -270 |
| H818 filtré (EV > 0) | 33 | 31 | +45 | +1.36 [-6.51 ; +10.23] | +9 % | -297 |

Qualité du modèle de survie sur le test : AUC 0.94 (exécuté ou non).

## 6. H818-J — Prix de la latence (mêmes signaux initiaux, tous signaux)

| Délai | Remplis | Taux de gain des remplis | Taux de gain des NON remplis | P&L ($) | par signal (IC 90 %) | par $ engagé | Opportunités perdues (non remplis gagnants) |
|---|---|---|---|---|---|---|---|
| 164 ms | 70 / 77 | 39 % | 29 % | +336 | +4.36 [-0.79 ; +9.42] | +28 % | 2 |
| 200 ms | 67 / 77 | 39 % | 30 % | +316 | +4.10 [-1.45 ; +9.31] | +28 % | 3 |
| 250 ms | 61 / 77 | 36 % | 44 % | +316 | +4.11 [-0.95 ; +9.85] | +28 % | 7 |
| 500 ms | 55 / 77 | 35 % | 45 % | +393 | +5.11 [-0.19 ; +10.87] | +38 % | 10 |

## 7. H818-K — Taille (164 ms, tous signaux)

| Mise visée | Parts | Prix moyen payé (frais compris) | Frais ($) | Capital réellement engagé ($) | P&L ($) | Rendement par $ |
|---|---|---|---|---|---|---|
| 5 $ | 1284 | 0.259 | 16.5 | 333 | +115 | +34.6 % |
| 10 $ | 2434 | 0.262 | 31.4 | 638 | +205 | +32.1 % |
| 20 $ | 4516 | 0.264 | 58.6 | 1191 | +336 | +28.2 % |
| 50 $ | 9664 | 0.263 | 126.2 | 2546 | +795 | +31.2 % |
| 100 $ | 16244 | 0.263 | 212.8 | 4265 | +1651 | +38.7 % |

## 8. Critère de décision
- Une modification de Bot95 n'est proposée que si un filtre améliore le P&L net sur le TEST avec un IC par cycles > 0, après coûts et exécution réaliste.
