# Bot95 — Vérifications H559–H564 (préliminaire)

Généré le 12.10.2026 19:18 UTC. 335 cycles enregistrés avec la version du 11.10 14:55 (bornes à trois niveaux), avant la période réservée. Aucun fantôme ni règle modifié.

**Statut des chiffres** — MESURE : heures, files vues à l'arrivée, transactions, prix. SIMULATION : remplissages (trois bornes), résultats en $. INSUFFISANT : tout ce qui porte sur moins de ~30 remplissages.

## 1. Interactions des conditions a / b / c (offres de M2 marge 5 c, classées à la pose)

a : bourses −10 $ en 300 ms ; b : flux agressif net ≥ 250 000 $ contre nous en 250 ms ; c : ≥ 100 parts vendues sur nos acheteurs en 500 ms ; chacune « active » si déclenchée dans les 2 s avant la pose (même pause que M4). Classement fait uniquement avec les données reçues AVANT la pose.

| Combinaison | Opportunités (offres posées) | Remplies (prudent) | Parts | Résultat prudent | par part | Sélection adverse +1 / +3 / +5 / +10 s (c/part) |
|---|---|---|---|---|---|---|
| aucune | 61264 | 701 | 46990 | +599 $ | +1.3 c | -0.8 / -0.6 / -0.4 / +0.2 |
| a | 963 | 23 | 2354 | +388 $ | +16.5 c | -0.9 / +1.3 / +0.8 / +3.5 |
| b | 4347 | 89 | 7122 | -742 $ | -10.4 c | -1.3 / -1.8 / -1.6 / -1.5 |
| c | 28142 | 329 | 21760 | +929 $ | +4.3 c | -0.5 / -0.7 / -0.8 / -1.8 |
| ab | 1031 | 30 | 3024 | -588 $ | -19.4 c | -3.5 / -5.1 / -3.8 / -1.5 |
| ac | 1443 | 23 | 1548 | +122 $ | +7.9 c | +0.5 / +1.2 / +1.9 / +2.8 |
| bc | 3965 | 69 | 6111 | -800 $ | -13.1 c | -2.1 / -1.1 / -1.4 / -1.0 |
| abc | 2894 | 77 | 7916 | -385 $ | -4.9 c | -0.5 / -0.2 / +0.8 / -1.0 |

Effet propre d'une condition = ligne « a » (ou « b », « c ») seule contre « aucune » ; interaction = lignes combinées contre la somme des effets propres. Avec si peu de remplissages, aucune interaction ne peut être distinguée du hasard à ce stade.

## 2. M6 : durée de vie et perte de priorité

| Variante | Offres | Temps réellement actif médian (ms) | Remplacements par cycle et côté (médiane) | Temps sans offre (annulations en attente, total s) | Parts remplies pendant l'annulation | Offres remplies | Perte de priorité estimée par remplacement (parts, médiane / p90) |
|---|---|---|---|---|---|---|---|
| M2 cotation marge 5 c | 104671 | 154 | 0 | 0.0 | 42049 | 1676 | 0 / 193 |
| M6 duree de vie 100 ms | 455214 | 85 | 590 | 13206.9 | 75170 | 2179 | 0 / 19 |
| M6 duree de vie 250 ms | 256989 | 234 | 244 | 5722.9 | 74388 | 2198 | 0 / 35 |
| M6 duree de vie 500 ms | 178135 | 327 | 110 | 2749.7 | 69699 | 2244 | 0 / 56 |
| M6 duree de vie 1000 ms | 135828 | 236 | 40 | 1182.8 | 62144 | 2131 | 0 / 85 |

Perte de priorité = file devant la nouvelle offre à son arrivée − file qui restait devant l'ancienne à son annulation (borne prudente : seules les transactions l'ont fait avancer). MESURE de la file affichée ; l'avancée dans la file est SIMULÉE.

## 3. Cohérence de la file d'attente

Offres posées contrôlées : 1744016. Remplissages partiels (prudent) : 22341.

- prudent > central : **10977** offres ; central > optimiste : **0** offres.
  - M0 temoin aleatoire : prudent > central 2
  - M1 V2-F ecart qui grandit : prudent > central 3
  - M1 V2-F incertitude 0,01 % : prudent > central 3
  - M1 cohorte B : V2-F corrige 0,015 % : prudent > central 2
  - M1 desaccord 20 60-180 s : prudent > central 3
  - M10 double maker meilleur prix : prudent > central 961
  - M11 zone maker : prudent > central 13
  - M2 cotation marge 10 c : prudent > central 469
  - M2 cotation marge 5 c : prudent > central 538
  - M21 maker du favori : prudent > central 524
  - M3 anticipation Chainlink : prudent > central 484
  - M4 retrait toxique : prudent > central 764
  - M4a seul bourses -10 $ : prudent > central 635
  - M4b seul flux agressif : prudent > central 641
  - M4c seul ventes Polymarket : prudent > central 674
  - M5 remplissage attendu : prudent > central 1349
  - M6 duree de vie 100 ms : prudent > central 961
  - M6 duree de vie 1000 ms : prudent > central 871
  - M6 duree de vie 250 ms : prudent > central 1011
  - M6 duree de vie 500 ms : prudent > central 1036
  - M8 hybride V2-F ecart qui grandit : prudent > central 3
  - M8 hybride V2-F incertitude 0,01 % : prudent > central 3
  - M8 hybride cohorte B : V2-F corrige 0,015 % : prudent > central 2
  - M8 hybride desaccord 20 60-180 s : prudent > central 3
  - M8b routeur corrige V2-F ecart qui grandit : prudent > central 2
  - M8b routeur corrige V2-F incertitude 0,01 % : prudent > central 3
  - M8b routeur corrige cohorte B : V2-F corrige 0,015 % : prudent > central 2
  - M8b routeur corrige desaccord 20 60-180 s : prudent > central 2
  - M9 fin de cycle cote acquis : prudent > central 13

**Cause identifiée dans le code (non corrigée, fantômes gelés jusqu'au verdict)** : la borne « prudente » plafonne la file devant nous à la quantité affichée (min avec l'affiché), alors que la borne centrale et la borne optimiste ne sont pas plafonnées. Après de gros retraits, la prudente peut donc avancer plus vite que la centrale. L'ordre prudent ≤ central ≤ optimiste n'est garanti que si les trois bornes appliquent le même plafond.

Borne STRICTE recalculée hors ligne (ventes à notre prix après la file vue à l'arrivée, sans plafond ni retrait ; traversée = tout) :

| Variante | Parts stricte (hors ligne) | Parts prudent (enregistré) | Parts central | Parts optimiste | central ≤ optimiste ? | stricte ≤ central ? |
|---|---|---|---|---|---|---|
| M0 temoin aleatoire | 87140 | 87464 | 88250 | 88480 | oui | oui |
| M1 V2-F ecart qui grandit | 64561 | 64400 | 64507 | 64586 | oui | NON |
| M1 V2-F incertitude 0,01 % | 18888 | 19268 | 20010 | 20012 | oui | oui |
| M1 cohorte A : zone + modele monte | 6693 | 6693 | 6694 | 6694 | oui | oui |
| M1 cohorte B : V2-F corrige 0,015 % | 25215 | 25680 | 26415 | 26419 | oui | oui |
| M1 desaccord 20 60-180 s | 75408 | 74586 | 74577 | 74647 | oui | NON |
| M1 desaccord 20 jeton 0,35-0,65 | 432 | 432 | 432 | 432 | oui | oui |
| M1 desaccord 30 | 71650 | 71650 | 72283 | 72507 | oui | oui |
| M10 double maker meilleur prix | 89042 | 103051 | 112999 | 126834 | oui | oui |
| M11 zone maker | 1755 | 1599 | 1509 | 1554 | oui | NON |
| M2 cotation marge 10 c | 130600 | 129820 | 125665 | 129106 | oui | NON |
| M2 cotation marge 5 c | 122580 | 116725 | 114246 | 117917 | oui | NON |
| M21 maker du favori | 35407 | 46104 | 47617 | 53629 | oui | oui |
| M3 anticipation Chainlink | 111057 | 114716 | 107769 | 110453 | oui | NON |
| M4 retrait toxique | 127669 | 129618 | 127283 | 134343 | oui | NON |
| M4a seul bourses -10 $ | 122231 | 123378 | 120700 | 124729 | oui | NON |
| M4b seul flux agressif | 121402 | 122938 | 122641 | 127940 | oui | oui |
| M4c seul ventes Polymarket | 135940 | 131855 | 131070 | 137239 | oui | NON |
| M5 remplissage attendu | 148105 | 164293 | 145649 | 148298 | oui | NON |
| M6 duree de vie 100 ms | 154061 | 169315 | 146493 | 146493 | oui | NON |
| M6 duree de vie 1000 ms | 146169 | 149203 | 133938 | 137232 | oui | NON |
| M6 duree de vie 250 ms | 153764 | 169874 | 144776 | 144793 | oui | NON |
| M6 duree de vie 500 ms | 154998 | 166529 | 141096 | 141831 | oui | NON |
| M8 hybride V2-F ecart qui grandit | 39872 | 39892 | 39980 | 40057 | oui | oui |
| M8 hybride V2-F incertitude 0,01 % | 15500 | 15564 | 15585 | 15587 | oui | oui |
| M8 hybride cohorte A : zone + modele monte | 6336 | 6336 | 6336 | 6336 | oui | oui |
| M8 hybride cohorte B : V2-F corrige 0,015 % | 19870 | 19933 | 19946 | 19950 | oui | oui |
| M8 hybride desaccord 20 60-180 s | 41414 | 41469 | 41416 | 41486 | oui | oui |
| M8 hybride desaccord 20 jeton 0,35-0,65 | 432 | 432 | 432 | 432 | oui | oui |
| M8 hybride desaccord 30 | 57435 | 57435 | 57561 | 57577 | oui | oui |
| M8b routeur corrige V2-F ecart qui grandit | 40225 | 40244 | 40333 | 40403 | oui | oui |
| M8b routeur corrige V2-F incertitude 0,01 % | 14874 | 14938 | 14959 | 14961 | oui | oui |
| M8b routeur corrige cohorte A : zone + modele monte | 6336 | 6336 | 6336 | 6336 | oui | oui |
| M8b routeur corrige cohorte B : V2-F corrige 0,015 % | 18994 | 19056 | 19069 | 19073 | oui | oui |
| M8b routeur corrige desaccord 20 60-180 s | 45495 | 45548 | 45497 | 45567 | oui | oui |
| M8b routeur corrige desaccord 20 jeton 0,35-0,65 | 432 | 432 | 432 | 432 | oui | oui |
| M8b routeur corrige desaccord 30 | 58109 | 58109 | 58235 | 58251 | oui | oui |
| M9 fin de cycle cote acquis | 2271 | 2589 | 2346 | 2540 | oui | oui |

La borne stricte hors ligne n'est pas toujours ≤ la borne enregistrée : le fichier du cycle donne l'heure THÉORIQUE d'arrivée et d'annulation (pose + trajet), alors que le fantôme en direct ne devient actif qu'au déclenchement réel de son minuteur (quelques ms plus tard). Une transaction tombée dans cet intervalle est comptée hors ligne mais pas en direct (et inversement à l'annulation). Ces écarts sont des différences de minutage, pas des doubles comptages ; les heures réelles d'arrivée et d'annulation ne sont pas encore enregistrées dans le fichier compact.


Double comptage entre fantômes : chaque fantôme se simule SEUL face au carnet réel ; deux fantômes au même prix sont remplis par la même transaction. Leurs résultats ne s'additionnent donc pas (offres simultanées au même prix et à la même seconde : 1627843). Un défaut de partage entre fantômes de l'attribution transaction/retrait (borne centrale) a été corrigé à 14:55 ; les offres antérieures ne sont pas utilisées ici.

## 4. Calcul de M8 (hybride maker / preneur)

Ce que fait le code actuel (gelé jusqu'au verdict) :

- **Preneur** : espérance = parts disponibles au prix vu (50 $) × probabilité du modèle − coût frais compris (0,07·p·(1−p)). Le retard de 150 ms N'entre PAS dans la décision ; il n'entre que dans l'exécution simulée (quantité réellement présente 150 ms + trajet plus tard).

- **Maker** : espérance = parts attendues en 10 s × (probabilité du modèle − prix − 2 c). Les parts attendues viennent du rythme des ventes des 30 dernières s moins la file devant nous. Ce n'est **PAS** un gain conditionnel au remplissage : la non-exécution est seulement implicite (parts attendues), la sélection adverse est une constante de 2 c (alors que la mesure sur M2 est de −8 à −11 c), aucune ristourne ni frais maker, et la probabilité du modèle n'est pas recalculée sachant qu'on est rempli.

- **Conséquence** : M8 surestime le gain maker. Une version conforme (P(remplissage) × E[gain | remplissage] avec sélection adverse mesurée, et preneur × probabilité de survie à 164 ms) est proposée comme NOUVEAU fantôme après le verdict, sur les données d'apprentissage seulement ; M8 actuel reste inchangé.

- M8 preneur : 448 positions, résultat prudent -1792 $, espérance annoncée moyenne +23.24 $
- M8 maker : 1108 positions, résultat prudent -229 $, espérance annoncée moyenne +68.71 $