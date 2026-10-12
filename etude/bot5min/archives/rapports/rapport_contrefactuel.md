# Bot95 — Fiabilité de l'avantage, urgence, faux cadeaux, origine des désaccords, TWAP contrefactuel

**Données :** BTC, 889 cycles du 07.10 08:00 au 10.10 10:25. On prend le premier signal E de chaque cycle (modèle E, tables du bot, avantage d'au moins 0,20, entre 90 et 20 s avant la fin), soit 163 signaux.

**Règles du test :**
- Achat au meilleur vendeur, limité à la quantité affichée, frais compris.
- Apprentissage avant le 08.10 22:00. Validation et nuit ensuite, matinée du 10.10 incluse.
- Seuils et corrections appris sur l'apprentissage seulement.
- Aucun fantôme modifié.

Ton document s'arrête au milieu de l'idée 27. J'ai traité les idées 2 à 27.

## En bref : une découverte importante

**Les « faux cadeaux » ont une signature claire : Polymarket bouge AVANT nos données.**

Hors apprentissage, on regarde les signaux où le prix vendeur de notre côté s'est **effondré d'au moins 30 c dans les 3 secondes** avant le signal, alors que **notre probabilité E n'a presque pas bougé** (moins de 5 points) :

| | Apprentissage | Validation + nuit |
|---|---|---|
| Achats | 1 | **11** |
| Gagnés | 1 (100 %) | **0 (0 %)** |
| Résultat | +41 $ | **−573 $** |

**11 pertes sur 11.**

Exemple à 10:18 ce matin :
- Polymarket fait passer le prix de Down de 0,98 à 0,40 entre 10:18:55 et 10:18:57.
- Nos exchanges enregistrés (Bybit, OKX, Binance, Coinbase) ne montrent la hausse de +20 $ du BTC qu'**après le signal, entre 10:18:57 et 10:19:00**. Chainlink suit juste après.
- Pendant ces 2 à 3 secondes, notre moteur croit encore à Down à 100 % et voit un « cadeau » à 0,40. En réalité, le marché a déjà vu le mouvement.

C'est le mécanisme C de ton document (idée 21) : **le marché a une information plus rapide que nos flux.**

**Attention :**
- Il n'y a qu'un seul cas dans l'apprentissage. La règle n'est donc pas validée de façon indépendante.
- Elle colle exactement à l'explication, mais c'est une observation, pas une preuve.

**Deuxième résultat, stable dans les deux périodes :**

| | Apprentissage | Validation + nuit |
|---|---|---|
| avantage 20-30 points | 57 achats, **+986 $** | 61 achats, **+1 227 $** |
| avantage ≥ 30 points | 20 achats, +278 $ | 25 achats, **−588 $** |

Les très gros avantages perdent hors apprentissage. La raison principale est celle ci-dessus : un gros avantage apparaît souvent parce que le marché a bougé avant nous.

## Partie A — Fiabilité de l'avantage et urgence d'exécution (idées 2-7)

**Idée 2 (séparer « faut-il acheter » de « faut-il se dépêcher ») :** c'est la bonne façon de penser. Les résultats ci-dessous le confirment : le retrait de liquidité dit **quand** acheter, pas **s'il faut** acheter.

**Idée 4 (retrait de liquidité selon le contexte).** Au moment du signal, le prix vendeur monte-t-il d'au moins 2 c dans la seconde ?

| Groupe | Signaux | Monte de 2 c ou plus | Variation moyenne |
|---|---|---|---|
| pas de retrait fort | 150 | 53 % | +9 c |
| **retrait fort (≥ 50 % de la quantité en 0,5 s)** | 13 | **92 %** | **+26 c** |
| avantage 20-30 points + retrait fort | 9 | 89 % | +20 c |
| avantage ≥ 30 points + retrait fort | 4 | 100 % | +40 c |
| régime agité | 112 | 62 % | +12 c |
| régime calme | 38 | **29 %** | +2 c |
| après un saut des exchanges | 15 | 87 % | +24 c |

- Au moment d'un signal, le prix monte dans la seconde une fois sur deux.
- Avec un retrait fort, il monte 9 fois sur 10.
- En régime calme, le marché bouge beaucoup moins après nos signaux.

**Idée 5 (acheter tout de suite seulement si le carnet se vide, sinon attendre).** Délais fixés d'avance. Chaque case donne : achats / résultat.

| Politique | Apprentissage | Validation + nuit |
|---|---|---|
| A — toujours tout de suite (référence) | 77 / **+1 264 $** | 86 / +639 $ |
| B — sinon attendre 0,25 s | 41 / +752 $ | 62 / +794 $ |
| B — sinon attendre 0,5 s | 30 / +330 $ | 57 / +825 $ |
| B — sinon attendre 1 s | 23 / +150 $ | 46 / +223 $ |

B fait mieux en validation, mais nettement moins bien en apprentissage. **Pas démontré.** Acheter tout de suite reste la référence.

**Idée 3 (avantage « fiable »).** La surestimation apprise sur l'apprentissage est faible : +0,04 en moyenne, et +0,13 après un saut des exchanges. Un avantage fiable d'au moins 0,20 donne 29 achats et +947 $ en apprentissage, mais 43 achats et −519 $ ensuite. Ce sont les gros avantages, donc souvent les faux cadeaux. **Cette correction ne protège pas.**

**Idée 6 (carte avantage × fiabilité × retrait, validation + nuit) :**

| Avantage | Retrait fort | Achats / gagnés / résultat |
|---|---|---|
| 20-30 points | oui | 6 / 67 % / +120 $ |
| 20-30 points | non | 55 / 49 % / **+1 107 $** |
| ≥ 30 points | non | 25 / 28 % / **−588 $** |

**Idée 7 (deux scores, valeur et urgence) :** c'est la bonne architecture pour plus tard. Pas de routeur automatique avant validation, comme tu le demandes.

## Partie B — Les faux cadeaux (idées 8-9)

Hors apprentissage, il y a 25 signaux à 30 points d'avantage ou plus :
- 7 gagnés, dont 2 jackpots, pour −588 $ au total ;
- après un saut des exchanges : 6 ;
- en régime calme : 14 ;
- désaccord né il y a moins de 3 s : 12 ;
- prix vendeur en baisse d'au moins 5 c dans les 3 s précédentes : 13.

Le détail cycle par cycle est en annexe.

| Prix vendeur dans les 3 s avant le signal | Apprentissage | Validation + nuit |
|---|---|---|
| effondré d'au moins 30 c | 1 / +41 $ | **14 / 14 % gagnés / −523 $** |
| en baisse de 10 à 30 c | 10 / 70 % / +458 $ | 10 / 70 % / **+373 $** |
| stable ou en hausse | 66 / 47 % / +765 $ | 62 / 47 % / +789 $ |
| **effondré d'au moins 30 c ET E quasi inchangé** | 1 / +41 $ | **11 / 0 % / −573 $** |

**Lecture :**
- Une baisse modérée du prix (10 à 30 c) est une **bonne** affaire dans les deux périodes : 70 % de gagnés.
- Un effondrement brutal (30 c ou plus), alors que notre modèle ne voit rien de nouveau, est presque toujours un piège.
- **Idée 9 (détecteur simple) :** la règle la plus simple fonctionne déjà. Mais elle n'a été vue qu'**une seule fois** en apprentissage. Il faut la valider en direct avant d'en faire un veto.

## Partie C — D'où vient l'avantage ? (idées 10-15)

Classement selon ce qui s'est passé dans la seconde avant le signal. Chaque case donne : achats / gagnés / résultat.

| Origine | Apprentissage | Validation + nuit |
|---|---|---|
| 1. E monte, prix stable | 20 / 30 % / +384 $ | 9 / 33 % / +32 $ |
| 2. E stable, prix baisse | 15 / 60 % / +300 $ | 34 / 41 % / +311 $ |
| 3. E monte et prix baisse | 9 / 56 % / +119 $ | 3 / 67 % / +4 $ |
| 4. E monte, prix monte moins vite | 30 / 57 % / +284 $ | 22 / 50 % / +147 $ |
| 5. E baisse, prix baisse plus vite | 1 / +225 $ | 3 / 33 % / +6 $ |
| 6. petits mouvements | 1 / −51 $ | 11 / 36 % / +173 $ |

- **Idées 10-11 :** sur une seule seconde, aucune origine n'est mauvaise dans les deux périodes. La différence apparaît sur 3 secondes et pour les effondrements brutaux (partie B).
- **Idée 12 (avantage de 30 à 50 points) :** l'origine « E stable, prix baisse » fait 8 achats, 25 % de gagnés, −240 $ hors apprentissage. Ce sont les faux cadeaux.
- **Idée 13 (accélération de l'avantage) :** elle est incluse dans les mesures sur 1 s et 3 s. Rien de plus.
- **Idée 14 (origine de l'information) :** presque tous les signaux (149 sur 163) naissent avec une nouvelle valeur Chainlink. Sans saut des exchanges ni baisse du marché, les autres origines sont trop rares pour conclure.
- **Idée 15 (certificat de naissance) :** le bot enregistre déjà, à chaque signal, le côté, la probabilité, le prix, la quantité, les 8 niveaux du carnet, le retrait et l'avantage. **Je propose d'y ajouter** la probabilité et le prix 1 s et 3 s avant, la dernière valeur Chainlink et son heure, le saut des exchanges et le régime. C'est de l'enregistrement seulement.

## Partie D — Maturité et origine (idées 16-23)

| Origine × maturité | Apprentissage | Validation + nuit |
|---|---|---|
| nouvelle valeur Chainlink, désaccord **mûr** (né il y a ≥ 3 s) | 28 / 50 % / +737 $ | 45 / 44 % / **+527 $** |
| nouvelle valeur Chainlink, désaccord **récent** (< 3 s) | 40 / 55 % / +571 $ | 36 / 39 % / **−295 $** |

**Idée 18 (maturité de l'information).** Nombre de nouvelles valeurs Chainlink depuis la naissance du désaccord :

| Nouvelles valeurs Chainlink | Apprentissage | Validation + nuit |
|---|---|---|
| 0 | 47 / 51 % / +438 $ | 58 / 38 % / **−1 $** |
| 1 | 5 / −3 $ | 5 / −14 $ |
| **2 ou plus** | 25 / 52 % / **+830 $** | 23 / 57 % / **+654 $** |

C'est le **résultat le plus stable de ce rapport.** Un désaccord qui a déjà survécu à 2 nouvelles valeurs Chainlink est rentable dans les deux périodes. Il confirme ce que montrait le rapport « jackpots » d'hier.

- **Idées 16-17 :** ce sont les tableaux ci-dessus. Les désaccords mûrs tiennent mieux.
- **Idée 19 (survie après les valeurs Chainlink suivantes) :** c'est l'idée 18, mesurée sans regarder l'avenir.
- **Idées 20 et 23 (pureté de l'information, confiance) :** ce sont des mesures descriptives. Le nombre de valeurs Chainlink depuis la naissance en est la version la plus simple, et elle fonctionne.
- **Idée 21 (mécanisme des faux cadeaux) :** c'est le mécanisme C, le marché mieux informé (partie B). Ce n'est pas une erreur de calibration : la correction de l'idée 3 n'aide pas.
- **Idée 22 :** voir le tableau origine × maturité ci-dessus.

## Partie E — TWAP contrefactuel (idées 24-27)

**Idées 24-26 (dépendance au dernier choc).** On calcule le SDR : de combien la probabilité E changerait sans le mouvement des 2 dernières secondes, rapporté à l'avantage.

| Groupe | Apprentissage | Validation + nuit |
|---|---|---|
| SDR faible (≤ 0,82) : le signal ne dépend pas du dernier choc | 39 / 49 % / +819 $ | 65 / 45 % / **+744 $** |
| SDR fort : le signal dépend du dernier choc | 38 / 53 % / +445 $ | 21 / 43 % / **−105 $** |
| SDR > 1 : sans le dernier choc, plus d'avantage | 29 / 52 % / +271 $ | 15 / 40 % / **−133 $** |

Les signaux qui ne dépendent pas du dernier choc font mieux dans les deux périodes. Ceux qui en dépendent deviennent perdants hors apprentissage.

**Idée 27 (consensus de trois mondes).** On compte combien de ces trois points de vue voient un avantage d'au moins 0,20 : E actuel, dernier Chainlink prolongé, consensus des 4 exchanges.

| Mondes d'accord | Apprentissage | Validation + nuit |
|---|---|---|
| 1 sur 3 | 51 / 47 % / +1 121 $ | 44 / 43 % / **+839 $** |
| 2 sur 3 | 20 / 55 % / +84 $ | 16 / 62 % / +223 $ |
| **3 sur 3** | 6 / 67 % / +59 $ | 26 / 35 % / **−423 $** |

C'est contre-intuitif : quand **tous** nos modèles voient un gros avantage et que le marché n'est pas d'accord, c'est souvent le marché qui a raison. C'est de nouveau le faux cadeau : le prix s'est effondré parce que le marché sait déjà.

## Ce que je te propose (tu décides)

1. **Ne rien changer aux fantômes.**
2. **Enregistrer le « certificat de naissance » complet** à chaque signal (idée 15). C'est de l'enregistrement seulement.
3. **Ajouter le compteur « faux cadeau »** dans le moniteur de santé : effondrement d'au moins 30 c en 3 s alors que E ne bouge pas. On vérifiera en direct si les 11 pertes sur 11 se confirment.
4. Si ça se confirme sur quelques jours, deux nouveaux fantômes de comparaison sont possibles, sans toucher à l'original :
   - « TWAP fin sans faux cadeau » ;
   - « TWAP fin mûr » (au moins 2 nouvelles valeurs Chainlink depuis la naissance du désaccord).

## Annexe — Les 25 signaux à 30 points d'avantage ou plus, hors apprentissage

| Heure | Côté | Prix | Proba E | Avantage | Restant | Régime | Saut | Âge du désaccord | Prix 3 s avant | Proba sans dernier choc | Gagné | Net |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 08.10 23:33 | Down | 0,64 | 0,96 | 0,32 | 76 s | agité | oui | 4,2 s | 0,64 | 0,72 | oui | +3 $ |
| 09.10 00:43 | Down | 0,40 | 0,88 | 0,48 | 65 s | agité | non | 0,3 s | 0,83 | 0,89 | non | −52 $ |
| 09.10 00:59 | Down | 0,51 | 0,90 | 0,39 | 55 s | agité | non | 3,0 s | 0,87 | 0,91 | non | −52 $ |
| 09.10 03:03 | Down | 0,17 | 0,51 | 0,34 | 63 s | agité | non | 10,8 s | 0,10 | 0,21 | oui | +16 $ |
| 09.10 03:53 | Up | 0,40 | 0,79 | 0,39 | 64 s | agité | non | 0,3 s | 0,85 | 0,78 | non | −52 $ |
| 09.10 06:19 | Down | 0,18 | 0,50 | 0,32 | 57 s | agité | non | 3,9 s | 0,23 | 0,30 | non | −26 $ |
| 09.10 08:48 | Down | 0,22 | 0,54 | 0,32 | 81 s | agité | non | 0,6 s | 0,23 | 0,20 | non | −27 $ |
| 09.10 10:08 | Up | 0,65 | 0,97 | 0,32 | 90 s | agité | non | — | 0,71 | 0,97 | oui | +26 $ |
| 09.10 10:19 | Down | 0,62 | 0,99 | 0,37 | 53 s | agité | oui | 0,3 s | 0,45 | 0,52 | oui | +2 $ |
| 09.10 21:43 | Up | 0,28 | 0,76 | 0,48 | 86 s | agité | oui | 4,2 s | 0,28 | 0,37 | oui | +4 $ |
| 09.10 23:23 | Up | 0,50 | 1,00 | 0,50 | 63 s | calme | non | 1,2 s | 0,97 | 1,00 | non | −52 $ |
| 09.10 23:59 | Up | 0,60 | 0,90 | 0,30 | 58 s | agité | non | 3,9 s | 0,78 | 0,90 | oui | +32 $ |
| 10.10 00:23 | Down | 0,19 | 0,59 | 0,40 | 90 s | calme | non | — | 0,24 | 0,59 | oui | +40 $ |
| 10.10 01:33 | Down | 0,20 | 0,66 | 0,46 | 77 s | calme | non | 12,0 s | 0,23 | 0,32 | non | −1 $ |
| 10.10 02:44 | Up | 0,40 | 0,98 | 0,58 | 58 s | calme | non | 0,3 s | 0,93 | 0,98 | non | −52 $ |
| 10.10 02:48 | Down | 0,40 | 0,89 | 0,49 | 62 s | calme | non | 0,3 s | 0,89 | 0,89 | non | −52 $ |
| 10.10 05:19 | Up | 0,53 | 0,97 | 0,44 | 48 s | calme | oui | 0,3 s | 0,05 | 0,00 | non | −21 $ |
| 10.10 06:29 | Down | 0,35 | 0,72 | 0,37 | 37 s | calme | oui | 0,3 s | 0,01 | 0,00 | non | −52 $ |
| 10.10 07:23 | Up | 0,18 | 0,67 | 0,49 | 90 s | calme | non | — | 0,27 | 0,69 | non | −5 $ |
| 10.10 09:43 | Down | 0,02 | 0,57 | 0,55 | 67 s | calme | oui | 0,6 s | 0,01 | 0,04 | non | −7 $ |
| 10.10 09:53 | Down | 0,50 | 0,94 | 0,44 | 67 s | calme | non | — | 0,88 | 0,94 | non | −52 $ |
| 10.10 09:58 | Down | 0,18 | 0,57 | 0,39 | 90 s | calme | non | — | 0,19 | 0,57 | non | −53 $ |
| 10.10 10:13 | Down | 0,40 | 0,94 | 0,54 | 69 s | calme | non | 0,3 s | 0,92 | 0,94 | non | −52 $ |
| 10.10 10:18 | Down | 0,40 | 1,00 | 0,60 | 63 s | calme | non | 0,3 s | 0,98 | 1,00 | non | −52 $ |
| 10.10 10:23 | Down | 0,60 | 1,00 | 0,40 | 68 s | calme | non | 16,2 s | — | 1,00 | non | −51 $ |

« — » dans l'âge du désaccord : le désaccord existait déjà quand la fenêtre de 90 s s'est ouverte.
