# Bot95 — Audit complémentaire maker (M4a/b/c, M6, M8, file d'attente) — DIAGNOSTIC, pas un verdict

Généré le 11.10.2026 13:33 UTC. 1 cycles enregistrés avec la version du 11.10 14:55, avant la période réservée (13.10.2026 00:00 UTC). Aucun fantôme, paramètre ou bot modifié ; aucun ordre.

**Statut** — MESURE : heures, files affichées, transactions, prix. SIMULATION : remplissages (3 bornes de file) et résultats. CONTREFACTUEL : recalcul hors ligne, jamais des remplissages réels. HYPOTHÈSE : retard preneur 150 ms (documentation, non mesuré). Intervalles à 90 % par rééchantillonnage des CYCLES. Moins de 30 remplissages = INSUFFISANT.

## 2. M4 — les huit combinaisons a / b / c sur les mêmes opportunités

Base commune : chaque offre posée par M2 marge 5 c (même prix que M4, aucun retrait) est une opportunité. Pour chaque REMPLISSAGE de M2, on regarde quelles conditions l'auraient évité (déclenchée entre 2 s et le trajet de l'annulation avant le remplissage), avec les seules données reçues avant. Les 8 lignes partitionnent donc les mêmes remplissages : aucune comparaison entre fantômes différents.

| a | b | c | Opportunités (offres posées) | Cotations actives | Remplissages | Parts | Sélection adverse +1/+3/+5/+10 s (c/part) | Victoire finale | Résultat | IC 90 % | Bons remplissages perdus si on retire |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Non | Non | Non | 83 | 83 | 0 | — | — | — | — | — | — |
| Oui | Non | Non | 0 | 0 | 0 | — | — | — | — | — | — |
| Non | Oui | Non | 0 | 0 | 0 | — | — | — | — | — | — |
| Non | Non | Oui | 3 | 3 | 0 | — | — | — | — | — | — |
| Oui | Oui | Non | 0 | 0 | 0 | — | — | — | — | — | — |
| Oui | Non | Oui | 0 | 0 | 0 | — | — | — | — | — | — |
| Non | Oui | Oui | 0 | 0 | 0 | — | — | — | — | — | — |
| Oui | Oui | Oui | 0 | 0 | 0 | — | — | — | — | — | — |

Remplissages de M2 marge 5 c analysés : 0 — **INSUFFISANT** pour séparer les combinaisons.

**Effet marginal de chaque condition** (sur les mêmes remplissages : résultat des remplissages qu'elle seule ferait éviter, et ceux évités par elle quelle que soit la combinaison) :

- a : seule → 0 remplissages évités, +0 $ ; au total → 0 remplissages évités, +0 $ (dont 0 gagnants perdus).
- b : seule → 0 remplissages évités, +0 $ ; au total → 0 remplissages évités, +0 $ (dont 0 gagnants perdus).
- c : seule → 0 remplissages évités, +0 $ ; au total → 0 remplissages évités, +0 $ (dont 0 gagnants perdus).

Interaction = résultat des lignes à plusieurs conditions comparé à la somme des lignes à une condition. Une condition active sur un remplissage gagnant ou perdant ne prouve rien à elle seule : seul l'écart contre le contrefactuel aléatoire (section 3) mesure une capacité de prédiction.

**Comparaison directe des fantômes** (même prix, mêmes cycles, chacun simulé seul) :

| Fantôme | Remplissages | Parts | Résultat prudent | IC 90 % | Sélection adverse +3 s |
|---|---|---|---|---|---|
| M2 cotation marge 5 c | 0 | 0 | +0 $ | [—] | +nan c |
| M4 retrait toxique | 0 | 0 | +0 $ | [—] | +nan c |
| M4a seul bourses -10 $ | 0 | 0 | +0 $ | [—] | +nan c |
| M4b seul flux agressif | 0 | 0 | +0 $ | [—] | +nan c |
| M4c seul ventes Polymarket | 0 | 0 | +0 $ | [—] | +nan c |
| M0 temoin aleatoire | 0 | 0 | +0 $ | [—] | +nan c |

## 3. Contrôles contre les faux gains (CONTREFACTUELS hors ligne, base : remplissages de M2 marge 5 c)

| Contrefactuel | Remplissages gardés | Parts | Résultat |
|---|---|---|---|
| B. M4 sans annulations (= M2 marge 5 c) | 0 | 0 | +0 $ |
| A. M4 complet (recalculé) | 0 | 0 | +0 $ |
| C. M4 annulations retardées de 100 ms | 0 | 0 | +0 $ |
| C. M4 annulations retardées de 300 ms | 0 | 0 | +0 $ |
| C. M4 annulations retardées de 1000 ms | 0 | 0 | +0 $ |
| D. Annulations aléatoires, même fréquence de retrait (3 % des poses) — 300 tirages | — | — | médiane +0 $ [p5 +0 ; p95 +0] |
| E. Même durée de présence : mêmes nombres de pauses de 2 s placées au hasard — 300 tirages | — | — | médiane +0 $ [p5 +0 ; p95 +0] |
| F. Mêmes horaires, autres prix de cotation | — | — | NON CALCULABLE de façon fiable hors ligne : la file aux autres prix n'est enregistrée qu'à ±3 c du meilleur prix (proposé comme fantôme après le verdict) |

**Lecture** : M4 recalculé garde +0 $ ; des retraits au hasard de même durée gardent +0 $ en médiane. Part des tirages aléatoires au moins aussi bons que M4 : 100 %. Si cette part est faible (< 5 %), M4 prédit vraiment la toxicité ; sinon son avantage peut venir d'une simple exposition réduite.

Validation de la méthode : le résultat « A recalculé » doit être proche du fantôme M4 réel (section 2) ; un écart signale une différence de calcul des conditions.

## 4. M6 — durée de vie des cotations

| Variante | Ordres posés | Remplacements | Temps réellement actif (min) | Attente d'annulation (s) | Délai confirmation → nouvelle pose (médiane ms) | Remplissages pendant l'annulation (parts) | Remplissages partiels | Parts | Résultat prudent | par ordre posé | par minute d'exposition | par $ exécuté | Capital immobilisé moyen ($ posés) | Bons remplissages manqués vs M2 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| M2 cotation marge 5 c | 86 | 0 | 4.3 | 0.0 | nan | 0 | 0 | 0 | +0 $ | +0.000 $ | +0.00 $ | +nan | 42.6 $ | — |
| M6 duree de vie 100 ms | 1809 | 1748 | 2.8 | 52.4 | 3 | 64 | 0 | 0 | +0 $ | +0.000 $ | +0.00 $ | +nan | 28.2 $ | 0 |
| M6 duree de vie 250 ms | 911 | 834 | 3.6 | 25.0 | 3 | 0 | 0 | 0 | +0 $ | +0.000 $ | +0.00 $ | +nan | 36.5 $ | 0 |
| M6 duree de vie 500 ms | 516 | 434 | 4.0 | 13.0 | 3 | 9 | 0 | 0 | +0 $ | +0.000 $ | +0.00 $ | +nan | 39.8 $ | 0 |
| M6 duree de vie 1000 ms | 301 | 213 | 4.2 | 6.4 | 4 | 0 | 0 | 0 | +0 $ | +0.000 $ | +0.00 $ | +nan | 41.7 $ | 0 |

Une durée courte n'est pas meilleure parce qu'elle évite des remplissages toxiques : il faut regarder le résultat par minute d'exposition et les bons remplissages manqués. La perte de priorité par remplacement est détaillée dans resultat_verifications_h559.md (section 2).

## 5. File d'attente — huit contrôles

Offres remplies contrôlées : 0 (indéterminées faute de transactions enregistrées : 0).

- 1. prudent > central : **0**
- 2. central > optimiste : **0**
- 3. 1er remplissage prudent AVANT le central (ordre de priorité) : **0**
- 5. parts remplies > volume échangé à notre prix : **0**
- 6. remplissage avant l'arrivée de l'offre : **0**
- 7. annulée sans heure effective : **0**
- 8. remplissage après l'annulation effective : **0**
- 4. double comptage d'un retrait entre fantômes : corrigé dans le code le 11.10 à 14:55 (une seule attribution transaction / retrait par baisse du niveau, partagée par tous les fantômes) ; les remplissages d'avant ne sont pas utilisés ici. Les fantômes restent simulés SEULS face au carnet : leurs résultats ne s'additionnent pas.

Défaut connu (contrôle 1) : seule la borne prudente est plafonnée à la quantité affichée ; la centrale et l'optimiste ne le sont pas. Fantômes gelés : pas de correction avant le verdict. Annulation : effective chez Polymarket après le trajet simple (≈ 15 ms) ; un remplissage entre la demande et cet instant est compté (comme en réel). Aucune de ces bornes n'est notre position réelle dans la file.

## 6. M8 — routeur maker / preneur

Formule actuelle (code gelé) — PRENEUR : parts disponibles au prix vu (50 $) × probabilité du modèle − coût frais compris ; le retard de 150 ms et la disparition de l'offre n'entrent PAS dans la décision (seulement dans l'exécution simulée). MAKER : parts attendues en 10 s × (probabilité du modèle − prix − 2 c) ; ce n'est PAS « probabilité de remplissage × gain conditionnel au remplissage » : la sélection adverse est une constante (2 c) au lieu de la probabilité de victoire SACHANT le remplissage. Abstention : oui, si aucune voie n'a une espérance positive (preneur) ou ≥ 0,50 $ (maker). **Non conforme à la formule demandée** ; version conforme proposée après le verdict, M8 actuel inchangé.

| Décision | Nombre | Remplies | Parts | Résultat prudent | Jackpots (≤ 0,25 gagnés) | Creux |
|---|---|---|---|---|---|---|
| preneur | 0 | 0 | 0 | +0 $ | 0 | +0 $ |
| maker | 0 | 0 | 0 | +0 $ | 0 | +0 $ |
| abstention | 0 (signaux sans décision M8) | — | — | — | — | — |

## 7–8. Comparaison des moteurs sur les mêmes cycles (délai preneur : plusieurs scénarios)

Cycles communs : 0. FAST / SLOW / HYBRID : achat preneur de 50 $ au prix du signal ou mieux, frais 0,07·p·(1−p), aux délais 0 / 50 / 150 / 250 ms (150 = HYPOTHÈSE documentée).

| Moteur | Positions | $ engagés (capital) | Prix moyen | Frais | Résultat | IC 90 % | Sélection adverse +3 s (c/part) | Creux max | Pire série de pertes | Jackpots |
|---|---|---|---|---|---|---|---|---|---|---|
| FAST (délai 0 ms) | 0 | 0 $ | nan | 0 $ | +0 $ | [—] | +nan | +0 $ | 0 | 0 |
| FAST (délai 50 ms) | 0 | 0 $ | nan | 0 $ | +0 $ | [—] | +nan | +0 $ | 0 | 0 |
| FAST (délai 150 ms) | 0 | 0 $ | nan | 0 $ | +0 $ | [—] | +nan | +0 $ | 0 | 0 |
| SLOW (délai 150 ms) | 0 | 0 $ | nan | 0 $ | +0 $ | [—] | +nan | +0 $ | 0 | 0 |
| HYBRID (délai 150 ms) | 0 | 0 $ | nan | 0 $ | +0 $ | [—] | +nan | +0 $ | 0 | 0 |
| FAST (délai 250 ms) | 0 | 0 $ | nan | 0 $ | +0 $ | [—] | +nan | +0 $ | 0 | 0 |
| M0 témoin (prudent) | 0 | 0 $ | nan | 0 $ | +0 $ | [—] | +nan | +0 $ | 0 | 0 |
| M1 maker sur signal (prudent) | 0 | 0 $ | nan | 0 $ | +0 $ | [—] | +nan | +0 $ | 0 | 0 |
| M2 marge 5 c (prudent) | 0 | 0 $ | nan | 0 $ | +0 $ | [—] | +nan | +0 $ | 0 | 0 |
| M4 (prudent) | 0 | 0 $ | nan | 0 $ | +0 $ | [—] | +nan | +0 $ | 0 | 0 |
| M4a (prudent) | 0 | 0 $ | nan | 0 $ | +0 $ | [—] | +nan | +0 $ | 0 | 0 |
| M4b (prudent) | 0 | 0 $ | nan | 0 $ | +0 $ | [—] | +nan | +0 $ | 0 | 0 |
| M4c (prudent) | 0 | 0 $ | nan | 0 $ | +0 $ | [—] | +nan | +0 $ | 0 | 0 |
| M6 100 ms (prudent) | 0 | 0 $ | nan | 0 $ | +0 $ | [—] | +nan | +0 $ | 0 | 0 |
| M6 250 ms (prudent) | 0 | 0 $ | nan | 0 $ | +0 $ | [—] | +nan | +0 $ | 0 | 0 |
| M6 500 ms (prudent) | 0 | 0 $ | nan | 0 $ | +0 $ | [—] | +nan | +0 $ | 0 | 0 |
| M6 1000 ms (prudent) | 0 | 0 $ | nan | 0 $ | +0 $ | [—] | +nan | +0 $ | 0 | 0 |
| M8 routeur (prudent) | 0 | 0 $ | nan | 0 $ | +0 $ | [—] | +nan | +0 $ | 0 | 0 |

**Résultat marginal contre M4 et contre M0 (différence par cycle, IC 90 %)** :

- FAST 0 − M4 : +0 $ [—]
- FAST 0 − M0 témoin : +0 $ [—]
- FAST 50 − M4 : +0 $ [—]
- FAST 50 − M0 témoin : +0 $ [—]
- FAST 150 − M4 : +0 $ [—]
- FAST 150 − M0 témoin : +0 $ [—]
- SLOW 150 − M4 : +0 $ [—]
- SLOW 150 − M0 témoin : +0 $ [—]
- HYBRID 150 − M4 : +0 $ [—]
- HYBRID 150 − M0 témoin : +0 $ [—]
- FAST 250 − M4 : +0 $ [—]
- FAST 250 − M0 témoin : +0 $ [—]
- M1 maker sur signal − M4 : +0 $ [—]
- M1 maker sur signal − M0 témoin : +0 $ [—]
- M2 marge 5 c − M4 : +0 $ [—]
- M2 marge 5 c − M0 témoin : +0 $ [—]
- M4a − M4 : +0 $ [—]
- M4a − M0 témoin : +0 $ [—]
- M4b − M4 : +0 $ [—]
- M4b − M0 témoin : +0 $ [—]
- M4c − M4 : +0 $ [—]
- M4c − M0 témoin : +0 $ [—]
- M6 100 ms − M4 : +0 $ [—]
- M6 100 ms − M0 témoin : +0 $ [—]
- M6 250 ms − M4 : +0 $ [—]
- M6 250 ms − M0 témoin : +0 $ [—]
- M6 500 ms − M4 : +0 $ [—]
- M6 500 ms − M0 témoin : +0 $ [—]
- M6 1000 ms − M4 : +0 $ [—]
- M6 1000 ms − M0 témoin : +0 $ [—]
- M8 routeur − M4 : +0 $ [—]
- M8 routeur − M0 témoin : +0 $ [—]

**Par temps restant à la pose (makers, prudent)** :

| Moteur | 180–300 s | 60–180 s | 0–60 s |
|---|---|---|---|
| M0 | +0 $ (0 — insuffisant) | +0 $ (0 — insuffisant) | +0 $ (0 — insuffisant) |
| M1 | +0 $ (0 — insuffisant) | +0 $ (0 — insuffisant) | +0 $ (0 — insuffisant) |
| M2 5 c | +0 $ (0 — insuffisant) | +0 $ (0 — insuffisant) | +0 $ (0 — insuffisant) |
| M4 | +0 $ (0 — insuffisant) | +0 $ (0 — insuffisant) | +0 $ (0 — insuffisant) |
| M5 | +0 $ (0 — insuffisant) | +0 $ (0 — insuffisant) | +0 $ (0 — insuffisant) |
| M6 1000 ms | +0 $ (0 — insuffisant) | +0 $ (0 — insuffisant) | +0 $ (0 — insuffisant) |
| M8 | +0 $ (0 — insuffisant) | +0 $ (0 — insuffisant) | +0 $ (0 — insuffisant) |

## 9–10. Limites
- Données d'une seule journée pour la version du 11.10 14:55 : la plupart des lignes sont INSUFFISANTES.
- Remplissages simulés (trois bornes), jamais des exécutions réelles ; retard preneur de 150 ms non mesuré (test réel de 1 $ soumis à ton accord).
- Les fantômes sont simulés seuls : leurs résultats ne s'additionnent pas.
- Aucune règle n'a été réglée sur ces chiffres ; la période réservée du 13.10 n'est pas lue.
