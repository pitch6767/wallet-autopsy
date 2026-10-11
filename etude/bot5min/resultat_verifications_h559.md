# Bot95 — Vérifications H559–H564 (préliminaire)

Généré le 11.10.2026 13:03 UTC. 1 cycles enregistrés avec la version du 11.10 14:55 (bornes à trois niveaux), avant la période réservée. Aucun fantôme ni règle modifié.

**Statut des chiffres** — MESURE : heures, files vues à l'arrivée, transactions, prix. SIMULATION : remplissages (trois bornes), résultats en $. INSUFFISANT : tout ce qui porte sur moins de ~30 remplissages.

## 1. Interactions des conditions a / b / c (offres de M2 marge 5 c, classées à la pose)

a : bourses −10 $ en 300 ms ; b : flux agressif net ≥ 250 000 $ contre nous en 250 ms ; c : ≥ 100 parts vendues sur nos acheteurs en 500 ms ; chacune « active » si déclenchée dans les 2 s avant la pose (même pause que M4). Classement fait uniquement avec les données reçues AVANT la pose.

| Combinaison | Opportunités (offres posées) | Remplies (prudent) | Parts | Résultat prudent | par part | Sélection adverse +1 / +3 / +5 / +10 s (c/part) |
|---|---|---|---|---|---|---|
| aucune | 83 | 0 | 0 | +0 $ | +nan c | — / — / — / — |
| a | 0 | — | — | — | — | — |
| b | 0 | — | — | — | — | — |
| c | 3 | 0 | 0 | +0 $ | +nan c | — / — / — / — |
| ab | 0 | — | — | — | — | — |
| ac | 0 | — | — | — | — | — |
| bc | 0 | — | — | — | — | — |
| abc | 0 | — | — | — | — | — |

Effet propre d'une condition = ligne « a » (ou « b », « c ») seule contre « aucune » ; interaction = lignes combinées contre la somme des effets propres. Avec si peu de remplissages, aucune interaction ne peut être distinguée du hasard à ce stade.

## 2. M6 : durée de vie et perte de priorité

| Variante | Offres | Temps réellement actif médian (ms) | Remplacements par cycle et côté (médiane) | Temps sans offre (annulations en attente, total s) | Parts remplies pendant l'annulation | Offres remplies | Perte de priorité estimée par remplacement (parts, médiane / p90) |
|---|---|---|---|---|---|---|---|
| M2 cotation marge 5 c | 86 | 1086 | 0 | 0.0 | 0 | 5 | — |
| M6 duree de vie 100 ms | 1809 | 88 | 874 | 52.4 | 64 | 5 | 0 / 15 |
| M6 duree de vie 250 ms | 911 | 238 | 417 | 25.0 | 0 | 6 | 0 / 20 |
| M6 duree de vie 500 ms | 516 | 488 | 217 | 13.0 | 9 | 6 | 0 / 30 |
| M6 duree de vie 1000 ms | 301 | 987 | 106 | 6.4 | 0 | 6 | 0 / 45 |

Perte de priorité = file devant la nouvelle offre à son arrivée − file qui restait devant l'ancienne à son annulation (borne prudente : seules les transactions l'ont fait avancer). MESURE de la file affichée ; l'avancée dans la file est SIMULÉE.

## 3. Cohérence de la file d'attente

Offres posées contrôlées : 4147. Remplissages partiels (prudent) : 48.

- prudent > central : **19** offres ; central > optimiste : **0** offres.
  - M2 cotation marge 5 c : prudent > central 1
  - M4 retrait toxique : prudent > central 2
  - M4a seul bourses -10 $ : prudent > central 2
  - M4b seul flux agressif : prudent > central 1
  - M4c seul ventes Polymarket : prudent > central 1
  - M5 remplissage attendu : prudent > central 4
  - M6 duree de vie 100 ms : prudent > central 1
  - M6 duree de vie 1000 ms : prudent > central 2
  - M6 duree de vie 250 ms : prudent > central 2
  - M6 duree de vie 500 ms : prudent > central 3

**Cause identifiée dans le code (non corrigée, fantômes gelés jusqu'au verdict)** : la borne « prudente » plafonne la file devant nous à la quantité affichée (min avec l'affiché), alors que la borne centrale et la borne optimiste ne sont pas plafonnées. Après de gros retraits, la prudente peut donc avancer plus vite que la centrale. L'ordre prudent ≤ central ≤ optimiste n'est garanti que si les trois bornes appliquent le même plafond.

Borne STRICTE recalculée hors ligne (ventes à notre prix après la file vue à l'arrivée, sans plafond ni retrait ; traversée = tout) :

| Variante | Parts stricte (hors ligne) | Parts prudent (enregistré) | Parts central | Parts optimiste | central ≤ optimiste ? | stricte ≤ central ? |
|---|---|---|---|---|---|---|
| M0 temoin aleatoire | 174 | 174 | 174 | 174 | oui | oui |
| M1 V2-F ecart qui grandit | 179 | 179 | 179 | 179 | oui | oui |
| M1 V2-F incertitude 0,01 % | 0 | 0 | 0 | 0 | oui | oui |
| M1 cohorte B : V2-F corrige 0,015 % | 147 | 147 | 147 | 147 | oui | oui |
| M1 desaccord 30 | 278 | 278 | 278 | 278 | oui | oui |
| M2 cotation marge 10 c | 260 | 260 | 260 | 260 | oui | oui |
| M2 cotation marge 5 c | 130 | 173 | 224 | 255 | oui | oui |
| M3 anticipation Chainlink | 172 | 172 | 172 | 172 | oui | oui |
| M4 retrait toxique | 130 | 185 | 224 | 262 | oui | oui |
| M4a seul bourses -10 $ | 130 | 179 | 224 | 255 | oui | oui |
| M4b seul flux agressif | 130 | 173 | 224 | 255 | oui | oui |
| M4c seul ventes Polymarket | 130 | 173 | 224 | 262 | oui | oui |
| M5 remplissage attendu | 339 | 291 | 331 | 365 | oui | NON |
| M6 duree de vie 100 ms | 239 | 294 | 239 | 239 | oui | oui |
| M6 duree de vie 1000 ms | 249 | 194 | 226 | 260 | oui | NON |
| M6 duree de vie 250 ms | 232 | 246 | 230 | 230 | oui | NON |
| M6 duree de vie 500 ms | 230 | 247 | 230 | 230 | oui | oui |
| M8 hybride V2-F ecart qui grandit | 179 | 179 | 179 | 179 | oui | oui |
| M8 hybride V2-F incertitude 0,01 % | 0 | 0 | 0 | 0 | oui | oui |
| M8 hybride cohorte B : V2-F corrige 0,015 % | 147 | 147 | 147 | 147 | oui | oui |
| M8 hybride desaccord 30 | 278 | 278 | 278 | 278 | oui | oui |

La borne stricte hors ligne n'est pas toujours ≤ la borne enregistrée : le fichier du cycle donne l'heure THÉORIQUE d'arrivée et d'annulation (pose + trajet), alors que le fantôme en direct ne devient actif qu'au déclenchement réel de son minuteur (quelques ms plus tard). Une transaction tombée dans cet intervalle est comptée hors ligne mais pas en direct (et inversement à l'annulation). Ces écarts sont des différences de minutage, pas des doubles comptages ; les heures réelles d'arrivée et d'annulation ne sont pas encore enregistrées dans le fichier compact.


Double comptage entre fantômes : chaque fantôme se simule SEUL face au carnet réel ; deux fantômes au même prix sont remplis par la même transaction. Leurs résultats ne s'additionnent donc pas (offres simultanées au même prix et à la même seconde : 4041). Un défaut de partage entre fantômes de l'attribution transaction/retrait (borne centrale) a été corrigé à 14:55 ; les offres antérieures ne sont pas utilisées ici.

## 4. Calcul de M8 (hybride maker / preneur)

Ce que fait le code actuel (gelé jusqu'au verdict) :

- **Preneur** : espérance = parts disponibles au prix vu (50 $) × probabilité du modèle − coût frais compris (0,07·p·(1−p)). Le retard de 150 ms N'entre PAS dans la décision ; il n'entre que dans l'exécution simulée (quantité réellement présente 150 ms + trajet plus tard).

- **Maker** : espérance = parts attendues en 10 s × (probabilité du modèle − prix − 2 c). Les parts attendues viennent du rythme des ventes des 30 dernières s moins la file devant nous. Ce n'est **PAS** un gain conditionnel au remplissage : la non-exécution est seulement implicite (parts attendues), la sélection adverse est une constante de 2 c (alors que la mesure sur M2 est de −8 à −11 c), aucune ristourne ni frais maker, et la probabilité du modèle n'est pas recalculée sachant qu'on est rempli.

- **Conséquence** : M8 surestime le gain maker. Une version conforme (P(remplissage) × E[gain | remplissage] avec sélection adverse mesurée, et preneur × probabilité de survie à 164 ms) est proposée comme NOUVEAU fantôme après le verdict, sur les données d'apprentissage seulement ; M8 actuel reste inchangé.

- M8 : pas encore de positions réglées.
