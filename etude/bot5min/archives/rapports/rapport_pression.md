# Bot95 — Pression de règlement, grecques, réévaluations et balayage du carnet

BTC, 850 cycles du 07.10 au 10.10 07:15. On mesure une fois par seconde, entre 90 et 20 s avant la fin. La probabilité utilisée est celle du modèle E, avec exactement les tables du bot. L'écart Bybit/Chainlink est recalculé à chaque seconde.

Trois périodes : apprentissage, validation, et la nuit du 10.10 à part. Toutes les limites de groupe (médianes) sont fixées sur l'apprentissage.

Pour les parties 8 à 10 (balayage du carnet), j'utilise les carnets à 8 niveaux enregistrés aux signaux depuis le 10.10 à 01:22. Cela fait 34 cycles, presque tous pendant la mauvaise nuit : c'est un petit échantillon.

Aucun fantôme n'a été modifié. Ton document s'arrête au milieu de l'idée 69, j'ai traité les idées 1 à 68.

**Remarque :** ici, le signal E est évalué une fois par seconde, contre 4 fois par seconde dans le contrôle de robustesse. Les nombres d'achats diffèrent donc un peu entre les deux rapports. Les comparaisons à l'intérieur de ce rapport se font toutes sur les mêmes mesures.

## En bref

1. **La découverte utile pour l'exécution : le carnet se vide avant que le prix monte.**
   - Quand la quantité au meilleur prix vendeur est divisée par deux en 0,5 s, sans que le prix change, ce prix monte d'au moins 2 c dans la seconde suivante dans **30 % des cas**.
   - Sans ce retrait, cela n'arrive que dans **4,4 % des cas**, soit 7 fois moins.
   - C'est un signal d'urgence d'exécution (idées 34, 35, 37, 39), pas un signal d'achat.
2. **La liquidité existe, mais pas au premier niveau.**
   - Au meilleur prix vendeur, on peut acheter **13 $** en médiane.
   - Sur les 8 premiers niveaux, avec au moins 20 points d'avantage, il y a **147 $** disponibles en médiane. 50 $ complets sont disponibles dans 22 cycles sur 34.
   - La faible mise actuelle vient donc du premier niveau, pas d'un manque général de liquidité (idée 62).
3. **Mais balayer le carnet multiplie l'avantage, quel qu'il soit.** Sur ces 34 cycles, presque tous pendant la mauvaise nuit, acheter plus a perdu plus :
   - meilleur prix seul : −287 $ ;
   - balayage jusqu'à 20 points d'avantage : −500 $ ;
   - balayage jusqu'à 100 $ : −1 122 $.
   Ce test devra être refait sur des jours normaux.
4. **Polymarket réagit en moyenne à 58 % d'une révision de E dans la même seconde.**
   - Quand il réagit trop peu, il continue ensuite dans le sens de E dans 62 à 66 % des cas.
   - Quand il réagit trop fort, il ne revient pas en arrière (51-52 %, le hasard). Il ne faut donc pas parier contre une sur-réaction, ce qui confirme les anciennes pertes.
5. **Les grecques (delta, gamma, thêta, barrière) n'apportent pas de règle solide.** Leurs effets changent de sens d'une période à l'autre.
6. **Un avertissement :** les signaux avec un très gros avantage (30 points ou plus) **perdent** hors apprentissage (−295 $ sur 26 achats). Un avantage énorme est souvent un signe que le modèle se trompe.

## Parties 1-4 — Pression de règlement et grecques (idées 1-25)

Pour chaque premier signal E du cycle, on regarde ces mesures au moment exact du signal. Chaque case donne : achats / gagnés / résultat / jackpots.

| Groupe au signal | Apprentissage | Validation | Nuit 10.10 |
|---|---|---|---|
| tous les signaux E | 60 / 48 % / +1 399 $ / 7 | 40 / 50 % / +638 $ / 5 | 34 / 29 % / −402 $ / 1 |
| delta fort (≥ 0,023 par $) | 30 / 33 % / +457 $ / 3 | 24 / 42 % / +455 $ / 2 | 23 / 26 % / −382 $ / 0 |
| delta faible | 30 / 63 % / +942 $ / 4 | 16 / 62 % / +183 $ / 3 | 11 / 36 % / −20 $ / 1 |
| réévaluation attendue forte | 30 / 30 % / +435 $ / 2 | 23 / 43 % / +498 $ / 2 | 25 / 24 % / −441 $ / 1 |
| réévaluation attendue faible | 30 / 67 % / +964 $ / 5 | 17 / 59 % / +140 $ / 3 | 9 / 44 % / +39 $ / 0 |
| convexité forte | 30 / 47 % / +617 $ / 4 | 22 / 45 % / +543 $ / 2 | 29 / 31 % / −249 $ / 1 |
| le temps qui passe joue pour nous | 32 / 62 % / +200 $ / 3 | 20 / 60 % / +225 $ / 1 | 22 / 36 % / −222 $ / 1 |
| le temps qui passe joue contre nous | 28 / 32 % / +1 199 $ / 4 | 20 / 40 % / +413 $ / 4 | 12 / 17 % / −180 $ / 0 |
| barrière qui s'éloigne en notre faveur | 4 / 75 % / +78 $ | 3 / 33 % / +88 $ | 2 / 50 % / +6 $ |
| barrière qui se rapproche contre nous | 28 / 32 % / +865 $ / 4 | 8 / 25 % / −97 $ | 4 / 0 % / −103 $ |

**Idées 1-5 (barrière, accélération, divergence, latence) :**
- La barrière est la moyenne future qu'il faut atteindre pour gagner.
- Le cas « elle se rapproche contre nous » gagne en apprentissage (+865 $) mais perd ensuite (−97 $ et −103 $). Ce n'est pas stable.
- **Idée 3** (E monte, barrière favorable, carnet immobile) : cela n'arrive presque jamais au moment d'un signal (1 cas en 3 jours).
- **Idée 5 (latence de réévaluation) :** mesurée hier. Le marché rejoint E en moins d'une seconde.

**Idées 6-13 (delta, gamma, réévaluation attendue) :**
- Les signaux où une petite variation de Chainlink change beaucoup la probabilité (delta fort, réévaluation attendue forte) gagnent **moins souvent** (30 à 43 %), mais portent un peu plus de jackpots.
- Ceux où la probabilité est peu sensible gagnent plus souvent (59 à 67 %), mais rapportent moins en validation.
- **Aucun des deux groupes n'est meilleur partout.** Pas de règle.

Carte de l'idée 13 (avantage × réévaluation attendue), hors apprentissage :

| Avantage au signal | Réévaluation attendue | Achats / gagnés / résultat |
|---|---|---|
| 20-30 points | forte | 35 / 37 % / +169 $ |
| 20-30 points | faible | 13 / 69 % / **+362 $** |
| ≥ 30 points | forte | 13 / 23 % / **−113 $** |
| ≥ 30 points | faible | 13 / 38 % / **−182 $** |

Les avantages modérés (20-30 points) sont rentables, les très gros avantages ne le sont pas. C'est cohérent avec l'audit de la nuit : un avantage énorme signale souvent un saut mal interprété.

**Idées 14-20 (thêta, fixation, attribution) :**
- Le passage du temps, avec chaque nouvelle seconde Chainlink fixée au prix prévu, n'explique que **22 %** des variations de probabilité d'une seconde à l'autre. Le reste vient des nouveaux prix.
- La variation prévue par le thêta n'annonce presque pas la variation réelle (corrélation +0,07).
- **Idée 19 (fixation pure, sans mouvement des exchanges) :** une seule révision de plus de 10 points au moment d'un signal en 3 jours. Ce cas n'existe presque pas.

**Idées 21-25 (surprise de fixation, asymétrie) :** elles sont couvertes par la « réévaluation attendue » ci-dessus et par la réaction du marché ci-dessous. Elles n'apportent pas de signal supplémentaire.

## Parties 5-7 — Comment Polymarket réagit (idées 26-48)

**Idée 30 (réaction normale) :** dans la même seconde, le milieu du carnet bouge en moyenne de **0,58 fois** la révision de E (1 084 révisions de plus de 5 points, apprentissage).

**Idées 27, 28, 31, 32 (sous-réaction, sur-réaction, résidu, cycle de vie) :** mesurées hors apprentissage.

| Réaction dans la même seconde | Révisions | Le carnet continue dans le sens de E dans les 2 s | dans les 5 s | Le côté de la révision gagne |
|---|---|---|---|---|
| sous-réaction (moins d'un tiers de la normale) | 170 | **62 %** | **66 %** | 64 % |
| réaction normale | 364 | 50 % | 53 % | 63 % |
| sur-réaction (plus de 2 fois la normale) | 96 | 52 % | 51 % | 60 % |

- La **sous-réaction se corrige** en partie dans les secondes suivantes. C'est le mécanisme de TWAP fin lui-même.
- La **sur-réaction ne se corrige pas.** Ne jamais acheter le côté opposé.

**Idées 10, 26, 38 (prévoir la montée du prix vendeur dans la seconde) :** la mesure (AUC) vaut 0,5 pour le hasard et 1 pour une prévision parfaite.

| Variable | Apprentissage | Validation + nuit |
|---|---|---|
| taille de la révision de E | 0,63 | 0,62 |
| avantage E − prix | 0,60 | 0,59 |
| retrait de quantité au meilleur prix | 0,55 | 0,57 |
| spread | 0,53 | 0,58 |
| delta / gamma d'information | 0,57 | 0,56 |

Ces variables donnent une prévision faible mais stable. La meilleure est simplement la taille de la révision.

**Idées 34-41 (le carnet se vide avant que le prix monte) :**

| Situation | Mesures | Le prix vendeur monte d'au moins 2 c dans la seconde |
|---|---|---|
| quantité stable ou en hausse | 62 412 | 4,4 % |
| **quantité au meilleur prix divisée par 2 en 0,5 s, prix inchangé** | 3 182 | **29,9 %** |

C'est le résultat le plus net du document. Le retrait de liquidité précède la hausse de prix (idée 39). C'est utile pour décider d'acheter **tout de suite**, pas pour décider d'acheter.

**Idées 42-48 (prix futur, moment optimal d'exécution) :** mesuré hier. L'avantage fond de moitié en 0,5 s et le prix monte, mais la quantité aussi. Acheter tout de suite reste la meilleure politique. Attendre 100 ou 250 ms n'est pas mesurable avec 4 enregistrements par seconde. On le saura avec le test réel, qui reste reporté.

## Parties 8-10 — Balayer le carnet (idées 49-68)

34 cycles avec un signal TWAP fin et un résultat officiel, depuis le 10.10 à 01:22. On utilise la probabilité du signal. Au plus 50 $ par cycle, frais compris.

| Politique | Cycles | Capital engagé | Résultat | Jackpots |
|---|---|---|---|---|
| meilleur vendeur seul (actuel) | 33 | 801 $ | **−287 $** | 2 |
| balayer tant que l'avantage ≥ 20 points | 33 | 1 200 $ | −500 $ | 2 |
| balayer tant que l'avantage ≥ 15 points | 34 | 1 608 $ | −493 $ | 2 |
| balayer tant que l'avantage ≥ 10 points | 34 | 1 650 $ | −499 $ | 2 |
| balayer tant que l'avantage net > 0 | 34 | 1 650 $ | −499 $ | 2 |
| balayer prudent (probabilité − 10 points) | 32 | 1 199 $ | −499 $ | 2 |
| balayer ≥ 20 points, jusqu'à 100 $ | 33 | 2 289 $ | **−1 122 $** | 2 |

- **Idées 49-54, 57, 60-61 (alpha marginal, frontière de balayage) :** pendant cette mauvaise nuit, chaque dollar en plus a perdu à peu près autant que les premiers (−36 % à −49 % par dollar). Balayer ne change pas le signe du résultat : cela le multiplie.
- **Idées 55, 58 (limite dynamique, balayage prudent) :** retirer 10 points à la probabilité ne protège pas : −499 $.
- **Idée 62 (plafond de capacité) :** la liquidité existe, comme le montre l'en bref. Ce qui manque, c'est un avantage fiable.
- **Idées 64-67 (reconstitution du carnet) :** 0,25 s après le signal, le même prix ou moins cher est encore disponible dans 62 % des cas. À 2 s, dans 47 % des cas. La quantité rentable (avantage d'au moins 20 points) reste d'environ 150 $ pendant 2 s.
- **Idée 68 (exécution patiente) :** acheter au meilleur prix à 0, 1 et 2 s fait −660 $. C'est pire que de tout prendre tout de suite.
- **Idées 56, 59, 63 (coût d'opportunité, portefeuille, ordres passifs) :** sans objet en fantôme à 50 $ par cycle. Les ordres passifs ont déjà été rejetés (sélection adverse).

## Ce que je te propose (tu décides)

1. **Ne rien changer aux fantômes.**
2. **Enregistrer le « retrait de liquidité »** (quantité au meilleur prix divisée par deux en 0,5 s) au moment de chaque signal TWAP fin. C'est de l'enregistrement seulement, pour mesurer en direct si ce signal d'urgence tient.
3. **Refaire la comparaison des balayages** dans 3 à 5 jours, quand les carnets à 8 niveaux couvriront des jours normaux. Ce n'est qu'avec un avantage confirmé positif que balayer peut augmenter le gain.
4. **Surveiller les signaux avec un avantage de 30 points ou plus.** Ils perdent hors apprentissage. Aucun filtre pour l'instant : seulement de l'observation.
