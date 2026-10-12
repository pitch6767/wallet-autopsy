# TWAP FIN — jackpots, attente, exécution, mises, robustesse : les 41 idées testées

**Données :** BTC, 693 cycles du 07.10 au 09.10. La référence est le premier signal TWAP FIN original de chaque cycle : 140 achats, +2 323 $.

**Jackpot :** un achat qui rapporte au moins 4 fois sa mise. Il y en a 18, pour +1 892 $.

**Méthode :** on sépare les données en deux périodes. L'apprentissage couvre les cycles avant le 08.10 20:30, la validation ceux d'après. Une piste ne compte que si elle tient dans les deux.

Aucun fantôme n'a été modifié. Le document s'arrête au milieu de l'idée 42 : je l'ai traitée avec ce qui était écrit.

## Une correction importante d'abord

Dans les deux rapports précédents, j'ai écrit qu'avec 50 $, la quantité affichée ne limitait « presque jamais » l'achat. **C'est faux.**

Au meilleur vendeur, au moment du signal :
- le montant réellement achetable est de **10 $ en médiane** (20 $ en moyenne) ;
- les 50 $ complets ne sont disponibles que dans **33 signaux sur 140** ;
- la référence n'a engagé que 2 833 $ au total, au lieu de 7 000 $.

Les résultats du fantôme et de tous les tests restent justes, car ils étaient déjà limités à la quantité affichée. Ce qui était faux, c'est mon commentaire.

Un chiffre doit aussi être corrigé : le « +2 407 $ » du groupe « notre modèle a basculé, le carnet jamais » supposait 50 $ toujours disponibles. Il était surestimé.

La conséquence est importante pour le réel : **une grande partie de nos gains vient de petites quantités.** Remonter dans le carnet (idée 17) devient une vraie question.

## En bref

1. **La stratégie dépend fortement des jackpots.** Les 10 plus gros gains font 92 % du résultat. Sans les 20 plus gros, on est à −785 $.
2. **Les opportunités « mûres » sont les meilleures.**
   - Un désaccord né il y a plus de 5 s : +1 645 $ (+117 % par $), positif dans les deux périodes.
   - Un désaccord apparu d'un coup, en moins d'une seconde : +293 $, et −216 $ en validation.
   - Après au moins 2 prix Chainlink depuis la naissance du désaccord : +1 780 $ (+134 % par $), positif dans les deux périodes.
3. **Le fractionnement « 35 $ immédiats + 15 $ si confirmé » fait aussi bien que 50 $ immédiats** : +2 362 $ contre +2 323 $, avec un creux un peu plus faible. Il fait mieux en validation (+1 151 $ contre +1 026 $).
4. **Proportionner la mise à l'avantage fait moins bien** (−600 à −860 $). Une mise fixe reste préférable.
5. **Le moteur surestime un peu ses probabilités** sur les contrats très bon marché : 30 % annoncés pour 13 % gagnés entre 2 et 10 c. C'est quand même rentable, puisque le seuil de rentabilité est à 6 %.
6. **Mélanger le moteur et le carnet à parts égales prévoit mieux que chacun des deux**, surtout entre 40 et 20 s.

## Partie A — quand acheter ou attendre

**Idées 2-4. Horloge Chainlink.** On mesure, à l'instant du signal, le temps écoulé depuis le dernier prix Chainlink, rapporté à l'intervalle habituel entre deux prix.

| Phase au signal | Achats | Résultat | Appr. | Valid. | Si on attendait le Chainlink suivant |
|---|---|---|---|---|---|
| juste après un prix Chainlink | 73 | +819 $ | +409 $ | +410 $ | +595 $ |
| milieu de l'intervalle | 25 | +140 $ | +123 $ | +17 $ | **+375 $** |
| proche du prochain prix attendu | 39 | **+1 204 $** (+157 % par $) | +598 $ | +606 $ | +698 $ |

- **Idée 2 :** l'horloge compte. Un signal qui arrive juste avant le prochain prix attendu est le meilleur, dans les deux périodes. On y anticipe la mise à jour que le carnet n'a pas encore vue.
- **Idée 3 :** confirmé, en n'utilisant que ce qui est connu à l'instant (âge du dernier prix et intervalle habituel).
- **Idée 4 :** attendre ne vaut la peine qu'au milieu de l'intervalle (+375 $ contre +140 $), mais sur 25 signaux seulement.

**Idées 5-6. Âge du désaccord.**

| Désaccord | Achats | Résultat | Appr. | Valid. | Si on attendait Chainlink |
|---|---|---|---|---|---|
| né d'un coup (< 1 s) | 38 | +293 $ | +508 $ | **−216 $** | −183 $ |
| né il y a 1-5 s | 30 | +385 $ | +138 $ | +247 $ | +482 $ |
| montée progressive (> 5 s) | 72 | **+1 645 $** | +651 $ | +994 $ | +1 363 $ |

- **Idée 5 :** c'est l'inverse de l'hypothèse de départ. Les opportunités anciennes sont les meilleures, et il faut les acheter tout de suite. Les sauts brutaux sont les plus fragiles.
- **Idée 6 :** même lecture. Un désaccord qui persiste et s'élargit vaut plus qu'un désaccord qui vient de naître.

**Idée 7. Premier signal ou suivants** (mesure seulement).
- 1er franchissement du seuil : +2 323 $, 46 % gagnés.
- 2e franchissement : +635 $, 30 % gagnés, 11 pertes de suite.
- 3e et suivants : +3 257 $, mais 19 pertes de suite et un creux de −890 $.

Le premier signal est le plus régulier. Les suivants rapportent aussi, mais avec beaucoup plus de risque. Un achat par cycle reste justifié.

## Partie B — les jackpots

**Idées 8-9. Pourquoi l'attente abandonne-t-elle des signaux ?** Au prochain prix Chainlink :

| Ce qui arrive | Signaux | Résultat d'un achat immédiat |
|---|---|---|
| confirmé (on achète après l'attente) | 53 | +932 $ |
| risque A : le prix Polymarket a monté, notre probabilité est stable | **71** | **+984 $** (52 % gagnés) |
| risque B : notre probabilité a baissé | 14 | +162 $ (43 %) |
| offre disparue | 2 | +246 $ |

La grande majorité des signaux abandonnés le sont parce que **le marché nous a donné raison** (risque A). Ce sont de bons signaux.

Un prédicteur (idée 9) ne servirait pas à grand-chose : 71 fois sur 140, le prix monte.

**Idée 10. Regret asymétrique.** L'attente évite 554 $ de pertes, mais fait manquer 1 945 $ de gains. Le regret est nettement du côté de l'attente.

**Idée 11. ADN des jackpots.** On compare les 18 jackpots aux 47 perdants achetés à 0,20 $ ou moins.

| Mesure à l'achat | Jackpots | Perdants bon marché | Différence réelle ? |
|---|---|---|---|
| probabilité du moteur | 0,40 | 0,36 | oui, faible |
| distance au seuil (z) | 0,28 | 0,38 | oui : les jackpots sont plus près du seuil |
| temps restant | 68 s | 59 s | oui : les jackpots arrivent plus tôt |
| prix, avantage, quantité, âge Chainlink, variations sur 3 s | — | — | non |

Les jackpots ont une légère signature : plus tôt dans la fenêtre, et plus près du prix à battre. Mais la différence est trop faible pour les trier. Ils sont surtout la bonne partie d'une distribution asymétrique.

**Idée 12. Concentration des gains.**

| Retirer les | Gains retirés | Part du total | Résultat restant |
|---|---|---|---|
| 1 plus gros | 401 $ | 17 % | +1 922 $ |
| 5 plus gros | 1 263 $ | 54 % | +1 060 $ |
| 10 plus gros | 2 143 $ | 92 % | +180 $ |
| 20 plus gros | 3 109 $ | 134 % | −785 $ |

**C'est le chiffre le plus important du rapport.** La stratégie vit de ses gros gains. Tout filtre qui en supprime quelques-uns peut la rendre nulle.

**Idée 13. Part des jackpots conservée.** Elle est donnée pour chaque politique dans la partie D.

## Partie C — exécution

**Idées 14-15. Capacité.** Voir la correction en tête de rapport. Par montant disponible au meilleur vendeur :

| Disponible | Achats | Résultat | Appr. | Valid. |
|---|---|---|---|---|
| moins de 10 $ | 70 | +142 $ | +127 $ | +15 $ |
| 10 à 49 $ | 37 | +820 $ | +537 $ | +282 $ |
| 50 $ complets | 33 | **+1 362 $** | +634 $ | +728 $ |

Les signaux avec beaucoup de quantité font l'essentiel du gain.

L'espérance en dollars (quantité × (probabilité − prix − frais)) n'est que faiblement liée au résultat réel (corrélation +0,18). Elle annonce 3 569 $ pour 2 323 $ réalisés, ce qui confirme que le moteur est un peu trop optimiste.

**Idée 16. Budget de latence.**

| Délai | Prix | Quantité médiane | Probabilité | Avantage < 0,20 | Résultat |
|---|---|---|---|---|---|
| 0 s | 0,25 | 62 | 0,512 | 0 | +2 323 $ |
| 0,25 s | 0,34 | 88 | 0,513 | 68 | +2 845 $ |
| 0,5 s | 0,36 | 129 | 0,511 | 87 | +2 486 $ |
| 1 s | 0,38 | 174 | 0,511 | 99 | +731 $ |
| 2 s | 0,38 | 220 | 0,498 | 100 | +1 633 $ |

Avec le retard, **le prix monte mais la quantité aussi** : le carnet se recharge plus haut. La probabilité ne bouge pas. Aucune offre ne disparaît.

Le résultat varie beaucoup selon le délai, car quelques jackpots entrent ou sortent. La latence se joue entre « peu de jetons pas chers » et « beaucoup de jetons plus chers ».

**Idée 17. Remonter dans le carnet.** Ce n'est pas mesurable : nos enregistrements n'ont qu'un niveau de prix par côté. Vu la correction sur la capacité, c'est devenu une vraie question.

**Proposition (tu décides) :** enregistrer 8 niveaux du carnet à chaque achat TWAP fin, comme le fait déjà le fantôme corrigé. Cela ne change aucune décision du fantôme.

## Partie D — immédiat, fractionné ou confirmé

Toutes les politiques ont le même budget de 50 $, limité à la quantité affichée à chaque instant.

| Politique | Achats | Résultat | Par $ | Creux | Appr. | Valid. | Jackpots conservés |
|---|---|---|---|---|---|---|---|
| A — 50 $ immédiats (référence) | 140 | +2 323 $ | +82 % | −160 $ | +1 298 $ | +1 026 $ | 100 % |
| **B — 35 $ + 15 $ si confirmé** | 140 | **+2 362 $** | +81 % | **−141 $** | +1 211 $ | **+1 151 $** | 116 % |
| C — 15 $ + 35 $ si confirmé | 140 | +2 159 $ | +89 % | −169 $ | +903 $ | +1 256 $ | 119 % |
| attente complète | 53 | +1 661 $ | +112 % | −177 $ | +494 $ | +1 167 $ | 93 % |
| D — mise selon l'avantage | 140 | +1 714 $ | +81 % | −121 $ | +1 035 $ | +679 $ | 79 % |
| E — mise selon l'avantage prudent | 140 | +1 459 $ | +81 % | −109 $ | +938 $ | +521 $ | 69 % |
| idée 20 — selon la fenêtre | 127 | **+2 503 $** | **+102 %** | −161 $ | +1 469 $ | +1 034 $ | 113 % |
| fenêtre 90-40 s seulement | 127 | +2 297 $ | +87 % | −156 $ | +1 230 $ | +1 067 $ | 100 % |

Une part de jackpots au-dessus de 100 % est possible : le complément acheté après confirmation profite d'un carnet rechargé, donc d'une quantité plus grande.

- **Idée 18 (achat partiel) :** les fractionnements B et C sont proches de la référence. Ils ne la battent pas nettement.
- **Idée 19 (35 + 15) :** c'est la seule politique au moins égale à la référence dans les deux périodes, avec un creux plus faible. Le gain est petit (+39 $).
- **Idée 20 (selon la fenêtre) :** meilleure au total (+2 503 $), mais tout le gain vient de la période d'apprentissage. En validation, elle égale la référence (+1 034 $ contre +1 026 $). Non démontré.
- **Idée 21 (tournoi des mises) :** les mises proportionnelles à l'avantage (D, E) perdent 600 à 860 $ et un quart des jackpots. Les gros avantages ne sont pas plus sûrs. **La mise fixe reste la meilleure.**

## Partie E — robustesse des probabilités

**Idées 23-24. Calibration des signaux.**

| Prix payé | Achats | Probabilité du moteur | Gagnés réellement | Seuil de rentabilité |
|---|---|---|---|---|
| 0,02-0,10 | 23 | 0,30 | 13 % | 0,06 |
| 0,10-0,20 | 38 | 0,40 | 39 % | 0,15 |
| 0,20-0,35 | 46 | 0,52 | 48 % | 0,26 |
| 0,35-0,60 | 22 | 0,70 | 68 % | 0,45 |
| 0,60-0,98 | 11 | 0,93 | 82 % | 0,68 |

- **Idée 23 (seuil de rentabilité) :** chaque tranche gagne plus souvent que son seuil de rentabilité.
- **Idée 24 (calibration) :** le moteur est bien calibré de 10 à 60 c. Il est trop optimiste sur les tout petits prix (30 % annoncés, 13 % réels) et sur les gros (93 % annoncés, 82 % réels).

**Test de stress** : on retire N points à notre probabilité, et on ne garde que les signaux qui restent à un avantage d'au moins 0,20.

| Scénario | Achats restants | Résultat | Jackpots conservés |
|---|---|---|---|
| − 5 pts | 51 | +841 $ | 42 % |
| − 10 pts | 30 | +238 $ | 8 % |
| − 15 pts | 13 | +118 $ | 5 % |
| × 0,8 (pèse sur les chers) | 26 | +607 $ | 29 % |
| − 10 pts seulement entre 40 et 20 s | 128 | +2 306 $ | 100 % |

La stratégie est très sensible à une erreur de calibration : avec 5 points d'erreur, il ne reste qu'un tiers du gain.

**Idées 25-26 (avantage prudent, mise prudente) :** à ne pas utiliser comme veto. Il supprimerait la plupart des jackpots, et la mise prudente (E) fait moins bien.

**Idée 22. Même avantage, prix différent.**

| Prix | Achats | Gagnés | Résultat | Appr. | Valid. |
|---|---|---|---|---|---|
| < 0,15 $ | 40 | 20 % | +399 $ | +378 $ | +20 $ |
| **0,15-0,35 $** | 67 | 48 % | **+1 689 $** (+122 % par $) | +566 $ | +1 123 $ |
| > 0,35 $ | 33 | 73 % | +235 $ | +353 $ | −118 $ |

La zone 0,15-0,35 $ est la plus solide dans les deux périodes. On retrouve la « zone » découverte le 08.10 sur d'autres stratégies.

## Partie F — erreurs du marché

**Idées 27, 30. Carte prix × distance au seuil × temps restant.** On regarde toutes les cotations, en points (apprentissage / validation) :

| Prix | Distance au seuil | 90-60 s | 60-40 s | 40-20 s |
|---|---|---|---|---|
| < 0,15 $ | proche | +0,6 / +3,3 | **+4,8 / +3,2** | +4,8 / −0,9 |
| < 0,15 $ | loin | −0,3 / −1,8 | −0,8 / −1,0 | −1,7 / −0,6 |
| 0,15-0,50 $ | proche | −1,4 / +0,4 | +1,0 / +1,3 | −1,8 / −7,9 |
| > 0,50 $ | proche | −3,6 / −3,9 | −5,6 / −4,8 | −3,0 / +1,9 |

- **Idée 27 :** il existe une sous-évaluation récurrente. Les contrats à moins de 15 c, quand le BTC reste proche du prix à battre, sont sous-évalués de 3 à 5 points entre 90 et 40 s, dans les deux périodes.
- **Idée 30 :** à l'inverse, les favoris chers proches du seuil sont trop chers (−4 à −6 points).
- **Idée 28 (angles morts du marché) :** c'est le même résultat. L'angle mort du marché est le retournement près du seuil.

**Idées 29, 31-32. Qui a raison selon le contexte** (Brier, plus bas = meilleur) :

| Contexte | Moteur | Sauts | Carnet |
|---|---|---|---|
| côté bon marché < 10 c (queues) | 0,0371 | 0,0352 | **0,0347** |
| 10-30 c | **0,1663** | 0,1655 | 0,1711 |
| 30-50 c (incertain) | **0,2393** | 0,2423 | 0,2456 |
| près du seuil (|z| < 0,5) | 0,2284 | **0,2271** | 0,2371 |
| moyen (0,5-1,5) | 0,1154 | 0,1142 | **0,1124** |
| loin (|z| ≥ 1,5) | 0,0137 | **0,0135** | 0,0158 |

- **Idée 29 :** notre moteur est meilleur dans les zones incertaines et près du seuil. C'est là qu'il gagne.
- **Idée 31 (queues) :** le carnet est un peu meilleur sur les queues, et la version sauts fait mieux que l'original. Les jackpots ne viennent donc pas d'une erreur du marché sur les queues extrêmes. Ils viennent des retournements près du seuil (idée 27).
- **Idée 32 (distance normalisée) :** même lecture.

## Partie G — le marché sait-il quelque chose ?

**Idées 33-34. Trajectoire du prix sur les 10 s avant le signal.**

| Trajectoire | Achats | Résultat | Appr. | Valid. |
|---|---|---|---|---|
| chute rapide | 22 | +519 $ | +298 $ | +221 $ |
| prix stable | 47 | +715 $ | +552 $ | +163 $ |
| remontée | 29 | +379 $ | −42 $ | +421 $ |
| oscillations | 19 | +269 $ | +374 $ | −105 $ |

Aucune trajectoire n'est mauvaise dans les deux périodes. La chute rapide n'est pas dangereuse pour TWAP fin, contrairement à ce qu'on avait vu sur les anciennes stratégies.

**Idées 35-37, 41. Le carnet contre nous.**

| Sur les 3 dernières secondes | Achats | Résultat | Appr. | Valid. |
|---|---|---|---|---|
| le carnet bouge contre nous | 42 | +858 $ | +491 $ | +367 $ |
| le carnet réagit peu | 64 | +858 $ | +668 $ | +190 $ |
| le carnet suit | 22 | +247 $ | +92 $ | +154 $ |
| nouveau Chainlink pour nous ET carnet contre | 18 | +567 $ (+128 % par $) | +261 $ | +306 $ |

- **Idées 35-36 :** l'écart entre la réaction du carnet et celle de notre modèle n'annonce pas nos erreurs.
- **Idée 37 :** quand Chainlink va dans notre sens mais que le carnet bouge contre nous, ce sont même de bons achats. C'est le carnet qui est en retard.
- **Idée 41 :** un veto « carnet contre nous » ferait perdre 858 $. Rejeté.

**Idée 38. Deux erreurs distinctes du modèle.**
- 23 signaux voient notre probabilité baisser de plus de 15 points dans les 5 s qui suivent. 5 d'entre eux gagnent quand même.
- 76 signaux perdent au règlement, dont 18 seulement avaient connu cette révision.
- La plupart des pertes ne sont pas annoncées par une révision du modèle : ce sont des issues normales d'un pari.

**Idées 39-40. Le marché sait d'abord, et depuis quand.** Couvertes par les tableaux 35-37. Les mouvements contraires du carnet ne précèdent pas nos pertes, quel que soit leur âge sur les 3 dernières secondes.

**Idée 42. Modèle B = moteur et carnet mélangés à parts égales.** Le poids est fixé d'avance, pas optimisé. Brier (plus bas = meilleur) :

| Temps restant | Moteur | Carnet | Mélange 50/50 |
|---|---|---|---|
| 90-60 s | 0,1110 | 0,1132 | **0,1104** |
| 60-40 s | 0,1034 | 0,1052 | **0,1012** |
| 40-20 s | 0,0810 | 0,0733 | **0,0724** |

Le mélange prévoit mieux que chacun des deux, partout. Mais un meilleur prévisionniste n'est pas forcément plus rentable : le mélange réduit l'écart avec le carnet, donc le nombre de signaux. À tester seulement en fantôme, si tu le décides.

## Ce que je te propose (tu décides)

1. Ne rien changer aux fantômes.
2. Enregistrer 8 niveaux du carnet à chaque achat TWAP fin (aucun effet sur les décisions), pour mesurer ce qu'on gagnerait à remonter dans le carnet.
3. Au bilan, vérifier en direct les deux découvertes les plus solides : les désaccords mûrs (plus de 5 s ou au moins 2 prix Chainlink) contre les sauts brutaux, et la zone 0,15-0,35 $.
4. Plus tard, candidats pour de nouveaux fantômes :
   - « 35 $ immédiats + 15 $ si confirmé » ;
   - « mélange moteur/carnet ».
