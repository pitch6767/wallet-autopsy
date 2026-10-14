# Queue Race : phases 3 à 6 — en clair

Étude hors ligne du 14.10.2026. Aucun bot, aucun fantôme, aucun réglage touché, aucun ordre. Données : 752 cycles BTC 5 min enregistrés à Dublin, du 11.10 10:45 au 14.10 02:20 (heure suisse), tous utilisés. Les règles sont fixées sur la première moitié (apprentissage), réglées sur le quart suivant (validation) et jugées une seule fois sur le dernier quart (**test : 13.10 09:55 → 14.10 02:20, 188 cycles**).

## Le verdict en une phrase

> On sait prévoir assez bien qu'une offre va disparaître du carnet, mais s'en servir pour acheter les signaux que le moteur C refuse **fait perdre de l'argent** : sur le test, R, S et RS gagnent moins que le moteur C. Rien à mettre en fantôme ni en réel.

## Ce qu'on a appris

- **Qui fait disparaître la meilleure offre ?** Sur 248 779 disparitions : 3 sur 4 sont des **vendeurs qui retirent** leur offre (75,8 %), 1 sur 4 est un **acheteur qui la prend** (24,2 %). Pareil chaque jour (de 74,7 % à 77,1 % de retraits). Le chiffre du 11.10 (77 %) tient.
- **Les nouvelles des bourses expliquent peu** : un saut de prix ≥ 5 $ précède 30,8 % des disparitions, contre 21,9 % si on place les sauts au hasard. Soit environ 9 points seulement.
- **Les offres que nos signaux visent** : quand elles restent là, nos signaux gagnent 13 % des fois ; quand un vendeur les retire, 32 % ; quand un acheteur les prend avant nous, 41 %. On obtient surtout les offres dont personne ne veut.

## Les deux modèles (phase 3)

Note sur 1 : 0,5 = pile ou face, 1 = parfait. Mesuré sur le test, en n'utilisant que ce qu'on sait au moins 22,7 ms avant (notre délai).

| Modèle | Ce qu'il prévoit | Note (AUC) test | Fourchette 90 % |
|---|---|---|---|
| Retrait | le vendeur retire son offre dans la demi-seconde | 0,759 | 0,754 – 0,763 |
| Consommation | un acheteur prend l'offre dans la demi-seconde | 0,765 | 0,760 – 0,769 |

Les deux modèles sont bien réglés (probabilité annoncée ≈ fréquence observée), sauf les cas les plus extrêmes, un peu surestimés. Mais ils regardent les mêmes indices (offre petite, carnet déséquilibré) : ils voient **qu'une offre va partir**, pas **pourquoi**.

## La course (phase 4)

Quand le modèle « retrait » sonne (les 5 % de moments les plus risqués) :

| | Alerte retrait | Moment au hasard |
|---|---|---|
| L'offre disparaît dans la demi-seconde | 34,5 % | 9,9 % |
| Notre ordre arrive avant (aller simple 14 ms) | 60,8 % | 81,5 % |
| Notre ordre arrive avant (aller-retour 28 ms) | 53,2 % | 77,5 % |
| Valeur de l'achat 5 s plus tard, frais compris | −0,28 c par part | −1,8 c par part |

On perd beaucoup moins qu'en achetant au hasard, mais **on perd quand même**. Pour l'alerte « consommation », la valeur est nulle (0,0).

## Les fantômes contre le moteur C (phase 5, test)

Mêmes 71 signaux des cohortes A et B. R = moteur C + achat des signaux refusés quand le retrait est probable ; S = idem quand la consommation est probable ; RS = l'un ou l'autre. Seuils choisis avant le test. 50 $ par signal, frais compris.

| Stratégie | Résultat test | Écart avec C | Fourchette 90 % | Fourchette corrigée (3 essais) | Jackpots | Pire baisse | Capital engagé |
|---|---|---|---|---|---|---|---|
| Moteur C | +299 $ | — | — | — | 0 | 272 $ | 2 094 $ |
| R | +143 $ | −155 $ | −307 à −31 $ | −361 à −1 $ | 0 | 331 $ | 2 269 $ |
| S | +107 $ | −192 $ | −347 à −63 $ | −403 à −34 $ | 0 | 345 $ | 2 305 $ |
| RS | +107 $ | −192 $ | −343 à −63 $ | −392 à −35 $ | 0 | 345 $ | 2 305 $ |

Les achats ajoutés ont rapporté +12 $ et coûté −167 $ (R) ou −203 $ (S et RS). Aucun jackpot récupéré. Sur l'apprentissage et la validation, les trois variantes semblaient un peu meilleures (+40 à +127 $, mais fourchette contenant 0) : **ça n'a pas tenu sur le test**.

## Conclusion

- Le moteur C a raison de refuser ces signaux : une offre qui va disparaître n'est pas pour autant une bonne affaire.
- **Aucune proposition de fantôme.** La piste « deviner le retrait des vendeurs » est fermée pour le moment.
- Ce qu'il faudrait pour y revenir : un indicateur qui prévoit **le gagnant** (sur tous les signaux, la probabilité de retrait ne prévoit pas le gain : 0,48, soit le hasard), un délai plus court que les concurrents, et plusieurs centaines de signaux refusés sur une période neuve.

## Limites

- Peu d'achats ajoutés sur le test (8 à 12) : la fourchette est fragile ; « moins bon » veut surtout dire « aucune raison de continuer ».
- Exécution simulée sur le carnet reçu à Dublin 28 ms après la décision, sans file d'attente. Le moteur C simulé est un peu plus optimiste que celui mesuré en direct (+2 732 $ contre +2 400 $ sur ses 175 envois).
- Un seul marché (BTC 5 min), 2,6 jours de données, test de 15,7 h.

Détails et tableaux complets : `resultat_queue_race_phases36.md` et `resultat_queue_race_phases.md`.
