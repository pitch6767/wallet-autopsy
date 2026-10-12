# Bot95 — H818 : sélection adverse et qualité des exécutions — rapport du 11.10.2026

**Cadre**
- Étude hors ligne uniquement. Aucun ordre réel.
- R4, H816 et les fantômes sont inchangés. La période réservée n'a pas été lue.
- Protocole et code versionnés avant le calcul (commit b771777).

**Données**
- 55 cycles enregistrés à Dublin.
- 64 décisions H816 (prix de 0,20 à 0,50).
- 77 décisions « tous signaux » : mêmes règles, sans filtre de prix.
- Apprentissage sur les cycles avant 12:30 UTC, test sur les cycles après.

**Simulation** : mise de 20 $, exécution 164 ms après la décision.

## Réponse à la question centrale

**Les pertes viennent principalement de la sélection des billets, pas du mécanisme de remplissage.**

- **Exécution** : 60 des 64 décisions H816 sont exécutées à 164 ms (43 en entier, 17 en partie). Seules 2 sont perdues parce que l'offre a disparu, et 2 pour une autre raison.
- **Où se trouvent les pertes** : dans les trades **exécutés entièrement**. Ils gagnent 33 % du temps, à un prix moyen de 0,27, pour +18 % par dollar engagé.
- **Aucune trace de remplissage toxique** : juste après l'achat, le prix ne bouge presque pas. L'écart va de −0,5 à +0,6 centime entre 100 ms et 10 s, aussi bien pour les gagnants que pour les perdants. Le résultat se décide au règlement, pas à l'exécution.

## 1. H818-B — Groupes d'exécution

**Décisions H816**

| Groupe | Signaux | Taux de gain | Rendement réalisé par $ | Rendement si achat au prix affiché (non réalisable) |
|---|---|---|---|---|
| A — exécuté entièrement | 43 | 33 % | +18 % | +14 % |
| B — exécuté en partie | 17 | 65 % | +83 % | +110 % |
| C — non exécuté : offre disparue | 2 | 0 % | — | −100 % |
| D — non exécuté : autre raison | 2 | 0 % | — | −100 % |

**Tous signaux**

| Groupe | Signaux | Taux de gain | Rendement réalisé par $ | Rendement si achat au prix affiché (non réalisable) |
|---|---|---|---|---|
| A | 52 | 33 % | +22 % | +18 % |
| B | 18 | 56 % | +70 % | +75 % |
| C | 5 | 40 % | — | −31 % |
| D | 2 | 0 % | — | −100 % |

**Lecture**
- Les exécutions **partielles** sont les meilleures (65 % de gain). L'offre se vide parce que d'autres acheteurs ou vendeurs voient la même information.
- Quand la quantité de l'offre baisse entre la décision et l'exécution, c'est à 86–100 % par annulation des vendeurs, et non par d'autres acheteurs.

## 2. H818-C — Depuis combien de temps l'offre existe

Les données ne contiennent pas l'identifiant de chaque ordre : on ne peut pas mesurer l'âge d'un ordre. On mesure à la place depuis combien de temps le **niveau de prix** existe dans le carnet.

| Présence du niveau | Signaux | Encore là à 164 ms | Rendement si rempli | Rendement par signal envoyé |
|---|---|---|---|---|
| 0–50 ms | 29 | 97 % | +45 % | +8,2 $ |
| 150–500 ms | 6 | 100 % | −68 % | −12,1 $ |
| Plus de 500 ms | 17 | 76 % | +42 % | +4,1 $ |

Pour 24 signaux, aucun niveau au prix du signal n'apparaît dans la reconstruction du carnet à cet instant. C'est une limite de la reconstruction (photo complète toutes les 10 s seulement). **Les groupes sont trop petits pour conclure.**

## 3. H818-F — Offres disparues contre offres restées

| | Signaux | Taux de gain | Prix | Prix du marché 1 s après − prix du signal | Profondeur acheteurs / vendeurs |
|---|---|---|---|---|---|
| Disparues | 9 | 67 % | 0,35 | +15,5 c | 1 504 / 185 |
| Restées | 44 | 36 % | 0,30 | −0,5 c | 328 / 685 |

À prix, temps restant et côté égaux, l'écart est de +27 points, mais avec un IC de [−3 ; +55] : **non démontré** (seulement 9 offres disparues).

Les offres qui disparaissent sont des moments où le carnet est très chargé côté acheteurs, et où le prix monte aussitôt. Ce sont bien les meilleures, mais elles sont rares. Ce qui reste nous laisse une sélection moins bonne, sans être perdante.

## 4. H818-H — Mouvement du prix après le remplissage

Variation du prix en centimes par part après l'achat :

| | +100 ms | +250 ms | +1 s | +3 s | +10 s | Résultat final par part |
|---|---|---|---|---|---|---|
| Tous | −0,5 | −0,2 | +0,6 | +0,5 | +0,2 | +7,4 c |
| Gagnants | −0,4 | +0,5 | +1,7 | +0,8 | +2,7 | +72,6 c |
| Perdants | −0,6 | −0,5 | −0,0 | +0,4 | −1,1 | −25,9 c |

Le mouvement à 3 s ne prédit pas le résultat : 37 % de gain quand il est négatif, 40 % quand il est positif.

## 5. H818-I — Filtre « probabilité d'exécution × gain attendu »

Résultats sur le test, cycles non utilisés pour construire le filtre :

| Politique | Signaux | P&L | Par signal (IC 90 %) | Sans les 5 meilleurs |
|---|---|---|---|---|
| H816 inchangé | 29 | +47 $ | +1,61 [−7,3 ; +11,0] | **−255 $** |
| Tous signaux sans filtre | 36 | +72 $ | +2,00 [−5,9 ; +10,2] | −270 $ |
| H818 filtré | 33 | +45 $ | +1,36 [−6,5 ; +10,2] | −297 $ |

Le modèle prédit très bien **si** un ordre sera exécuté (score de classement 0,94), mais filtrer sur cette prédiction n'améliore rien. Sur le test, sans ses 5 meilleurs trades, H816 est **négatif**.

## 6. H818-J — Effet de la latence (mêmes 77 signaux de départ)

| Délai | Remplis | Gain des remplis / des non-remplis | P&L | Par signal (IC 90 %) |
|---|---|---|---|---|
| 164 ms | 70 | 39 % / 29 % | +336 $ | +4,4 [−0,8 ; +9,4] |
| 200 ms | 67 | 39 % / 30 % | +316 $ | +4,1 [−1,5 ; +9,3] |
| 250 ms | 61 | 36 % / 44 % | +316 $ | +4,1 [−1,0 ; +9,9] |
| 500 ms | 55 | 35 % / 45 % | +393 $ | +5,1 [−0,2 ; +10,9] |

La latence change surtout **quels** trades sont exécutés, et peu le P&L total. Le meilleur chiffre à 500 ms ne signifie pas que 500 ms est meilleur : les intervalles se recouvrent entièrement.

## 7. H818-K — Taille de la mise

| Mise | Parts | Prix moyen payé | Frais | Capital engagé | P&L | Rendement par $ |
|---|---|---|---|---|---|---|
| 5 $ | 1 284 | 0,259 | 16 $ | 333 $ | +115 $ | +35 % |
| 20 $ | 4 516 | 0,264 | 59 $ | 1 191 $ | +336 $ | +28 % |
| 50 $ | 9 664 | 0,263 | 126 $ | 2 546 $ | +795 $ | +31 % |
| 100 $ | 16 244 | 0,263 | 213 $ | 4 265 $ | +1 651 $ | +39 % |

La liquidité n'est pas le problème : le prix payé ne se dégrade pas jusqu'à 100 $. Le rendement par dollar reste à peu près le même, aux erreurs d'échantillon près.

## 8. Décision

**Aucun filtre ne démontre d'avantage hors échantillon. Je ne propose donc aucune modification de Bot95.**

Le levier n'est pas l'exécution : 94 % des décisions H816 sont exécutées, les remplissages ne sont pas toxiques et la profondeur suffit. Le levier est la **qualité du choix des billets**, qui reste fragile : sur le test, le gain dépend entièrement de quelques trades.

Prochaine étape naturelle : le verdict H816 du 14.10 sur la période réservée.
