# Bot95 — Une hypothèse, un test : la combinaison D

**Question :** un avantage de 20 à 30 points, confirmé par 2 nouvelles valeurs Chainlink (reçues **avant** l'achat), et qui reste positif sans le dernier mouvement des exchanges, garde-t-il son avantage ?

**Critère (le tien) :** seul le **bénéfice net absolu** compte, avec un creux supportable et une exécution réaliste. Un meilleur taux de réussite ne suffit pas.

**Méthode :**
- Toutes les politiques partent des **mêmes premières opportunités E** : le premier signal E de chaque cycle, avec 0,20 d'avantage ou plus.
- Achat au meilleur vendeur, limité à la quantité affichée, frais compris.
- Aucune donnée future n'entre dans les décisions.

**Les quatre politiques** (ton message ne les listait pas, je les ai définies ainsi) :
- **A** = E sans filtre, la référence ;
- **B** = avantage de 20 à 30 points ;
- **C** = B + au moins 2 nouvelles valeurs Chainlink depuis la naissance du désaccord ;
- **D** = C + avantage encore positif sans le mouvement des 2 dernières secondes.

J'ajoute chaque propriété prise seule, et une variante « D attendu » : on achète au premier instant du cycle où les trois conditions sont réunies, même plus tard que le premier signal.

**Honnêteté sur les données :** tout ce qui précède le 10.10 à 10:25 a déjà servi à explorer des hypothèses. Après 10:25, il n'y a qu'**une seule** opportunité. **Le verdict sur journées inédites est donc programmé pour le mardi 14.10 à 08:00.** Ce rapport n'est qu'un premier regard.

## Résultats par période

Chaque case donne : achats / taux de gain / bénéfice net / creux.

| Politique | Apprentissage (< 08.10 22:00) | Validation (→ 09.10 23:36) | Nuit + matinée 10.10 (→ 10:25) |
|---|---|---|---|
| **A — E sans filtre** | 77 / 51 % / **+1 264 $** / −136 $ | 51 / 51 % / **+935 $** / −141 $ | 35 / 34 % / **−296 $** / −392 $ |
| B — 20-30 pts | 57 / 49 % / +986 $ / −128 $ | 40 / 52 % / **+1 144 $** / −97 $ | 21 / 48 % / **+83 $** / −251 $ |
| C — B + 2 Chainlink | 21 / 52 % / +903 $ / −118 $ | 12 / 67 % / +713 $ / −46 $ | 3 / 33 % / +16 $ / −52 $ |
| **D — C + indépendant** | 19 / 53 % / **+735 $** / −118 $ | 10 / **80 %** / **+762 $** / −43 $ | 3 / 33 % / +16 $ / −52 $ |
| seule : 2 Chainlink | 25 / 52 % / +830 $ / −185 $ | 17 / 65 % / +659 $ / −52 $ | 6 / 33 % / −5 $ / −104 $ |
| seule : indépendant | 45 / 51 % / +990 $ / −173 $ | 38 / 53 % / +980 $ / −136 $ | 32 / 34 % / −228 $ / −324 $ |
| D attendu | 38 / 42 % / +711 $ / −199 $ | 27 / 44 % / +474 $ / −298 $ | 19 / 37 % / +133 $ / −104 $ |

**D comparé à A, sur les mêmes opportunités :**

| | Apprentissage | Validation | Nuit + matinée |
|---|---|---|---|
| Pertes évitées | 523 $ | 585 $ | 847 $ |
| Gains sacrifiés | 1 052 $ (4 jackpots) | 758 $ (2 jackpots) | 535 $ (2 jackpots) |

## Verdict sur les données déjà explorées

1. **D ne bat pas E en bénéfice net** sur les deux périodes « normales » :
   - apprentissage : +735 $ contre +1 264 $ ;
   - validation : +762 $ contre +935 $.
   - D gagne bien plus souvent (80 % en validation) et ses creux sont 3 fois plus faibles. Mais il sacrifie plus de gains qu'il n'évite de pertes, dont des jackpots.
   - **Selon ton critère, D est abandonné**, sauf si les journées inédites disent le contraire.
2. **Les trois propriétés ne sont presque pas liées entre elles** (corrélations de 0,02 à 0,24). Les additionner trie vraiment, mais elle **réduit trop** le nombre d'achats : 10 à 19 au lieu de 51 à 77.
3. **« D attendu » est moins bon que D partout,** sauf la nuit. Attendre fait payer plus cher et manquer des gains.
4. **B (20-30 points seulement) est le seul filtre qui bat A sur 2 périodes sur 3** : +209 $ en validation et +379 $ la nuit. Il fait cependant −278 $ en apprentissage. Ce n'est pas démontré, mais c'est le meilleur candidat pour le test sur journées inédites.

## La baisse modérée de 10 à 30 c en 3 s

| Groupe | Apprentissage | Hors apprentissage |
|---|---|---|
| baisse modérée, tous | 10 / 70 % / +458 $ | 10 / 70 % / +373 $ |
| baisse modérée **avec** les 3 propriétés | 3 / 100 % / +391 $ | 3 / 33 % / +48 $ |
| baisse modérée **sans** les 3 propriétés | 7 / 57 % / +67 $ | 7 / 86 % / +325 $ |
| les 3 propriétés **sans** baisse modérée | 16 / 44 % / +344 $ | 11 / 73 % / +679 $ |

- La baisse modérée gagne aussi **sans** les trois propriétés. Elle ne fait donc pas double emploi avec elles.
- Mais l'effet change de côté d'une période à l'autre, et il ne repose que sur 10 achats par période.
- **Elle n'apporte pas d'information démontrée en plus de D.** Selon ta règle : **pas de fantôme**, on la revoit sur les journées inédites.

## Ce qui est en place

- **Fantômes :** aucun n'a été modifié.
- **Certificat de naissance :** depuis 11:23, chaque signal enregistre la probabilité et le prix vendeur 1 s et 3 s avant, la dernière valeur Chainlink et ses heures, le saut des exchanges sur 2 s, sa confirmation, la volatilité et le régime.
- **Compteur « faux cadeau » :** il apparaît dans l'encadré santé de la page des fantômes. Il compte les signaux où le prix s'est effondré d'au moins 30 c en 3 s alors que la probabilité n'a presque pas bougé, et leur résultat.
- **« Sans faux cadeau » :** préparé, **pas activé**. On attend de vérifier les 11 pertes sur 11 sur des cycles nouveaux.
- **Mardi 14.10 à 08:00 :** un seul PDF de verdicts chiffrés sur les cycles postérieurs au 10.10 10:25 (jamais utilisés) :
  - A, B, C, D, E et les propriétés seules ;
  - les faux cadeaux ;
  - les balayages du carnet ;
  - A contre E.

**Ce qu'on décidera mardi :** si aucune combinaison ne bat E en bénéfice net, on garde E et on passe à la validation d'exécution.
