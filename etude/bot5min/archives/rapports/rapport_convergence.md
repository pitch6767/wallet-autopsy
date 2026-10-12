# Pourquoi l'avantage fond si vite — réponses chiffrées

On reprend les mêmes 140 signaux TWAP FIN original, BTC, du 07.10 au 09.10. L'achat se fait au moment du signal et le contrat est gardé jusqu'au règlement officiel (+2 323 $ au total).

Aucun fantôme n'a été modifié. Ce qui se passe après l'achat sert uniquement au diagnostic.

## La réponse à la question décisive

**C'est Polymarket qui rejoint notre modèle, presque à 100 %.**

| Délai | Baisse de l'avantage | Due à notre probabilité | Due au prix Polymarket | Part du marché |
|---|---|---|---|---|
| 0,25 s | −0,083 | +0,002 | −0,085 | 98 % |
| 0,5 s | −0,108 | −0,001 | −0,107 | 99 % |
| 1 s | −0,129 | −0,001 | −0,128 | 99 % |
| 2 s | −0,140 | −0,008 | −0,132 | 94 % |
| 10 s | −0,170 | −0,033 | −0,137 | 81 % |
| 20 s | −0,207 | −0,092 | −0,116 | 56 % |

Dans la première seconde, notre probabilité ne bouge pas du tout. C'est le prix qui monte vers nous : de 0,25 à 0,38 pour le vendeur, et de 0,23 à 0,37 pour l'acheteur.

Notre modèle ne corrige une partie de son estimation que plus tard (−9 points à 20 s), ce qui est normal : le prix BTC continue de bouger.

**Conclusion : la priorité est la vitesse d'exécution, pas la fiabilité du signal.** Un ordre qui arrive 0,25 s après le signal paie en moyenne 8 c de plus par jeton.

## Résultats des autres expériences

**Classement des signaux selon la seconde qui suit** (diagnostic, car on utilise l'avenir) :

| Ce qui se passe dans la seconde suivante | Achats | Gagnés | Résultat | Par $ |
|---|---|---|---|---|
| Polymarket rejoint notre modèle | 72 | 60 % | +1 098 $ | +99 % |
| notre modèle rejoint Polymarket | 13 | 31 % | +95 $ | +34 % |
| les deux convergent | 5 | 60 % | +487 $ | +460 % |
| les deux s'écartent | 7 | 29 % | −112 $ | −56 % |
| presque rien ne bouge | 43 | 28 % | +756 $ | +66 % |

À 5 s, le contraste est encore plus net :
- Quand le marché nous rejoint : 68 achats, 68 % gagnés, +1 832 $.
- Quand notre modèle recule : 42 achats, 17 % gagnés, +469 $, avec 13 pertes de suite.

Ce dernier groupe gagne quand même de l'argent, grâce à quelques gros gains à très bas prix.

**Double alpha (revente contre règlement), par jeton, frais compris :**

| Moment | Revente possible avec bénéfice | Gain si on revendait | Gain en gardant jusqu'au règlement |
|---|---|---|---|
| +1 s | 83 / 140 | +0,09 | +0,20 |
| +5 s | 82 / 138 | +0,12 | +0,20 |
| +20 s | 64 / 116 | +0,19 | +0,26 |

Garder jusqu'au règlement rapporte en moyenne deux fois plus que revendre. On ne touche pas à la sortie.

**Le groupe « notre modèle a basculé, le carnet jamais » avec latence** (24 signaux, 50 $ supposés disponibles) :

| Achat après | Encore ≥ 0,20 | Résultat | Prix moyen |
|---|---|---|---|
| 0 s | 24 | +2 407 $ | 0,30 |
| 0,25 s | 11 | +1 461 $ | 0,46 |
| 0,5 s | 8 | +1 300 $ | 0,52 |
| 1 s | 7 | +1 094 $ | 0,55 |

Avec une seconde de retard, la moitié du gain disparaît, mais il reste positif. (Le +1 015 $ du rapport précédent était limité à la quantité affichée. Ici, les 50 $ sont supposés disponibles.)

## Les 22 idées commentées une par une

**1. Point de départ.** Les chiffres sont confirmés et identiques au rapport précédent.

**2. FAVORITE FLIP LATENCY.** Mesuré (section 7 ci-dessus). L'avantage est encore bien présent après 1 s de retard (+1 094 $). Les horodatages complets envoi → exécution n'existeront qu'avec de vrais ordres. Le fantôme TWAP fin enregistre déjà le moment exact de son achat simulé et le carnet qu'il voyait vraiment.

**3. FLIP-TO-FILL GAP.** Même tableau. À 0,25 s, seuls 11 signaux sur 24 gardent ≥ 0,20 d'avantage, mais tous restent gagnants en moyenne. La latence réelle du worker est inconnue tant qu'on n'envoie pas d'ordre : c'est le test à 1 $ prévu après le bilan, s'il reçoit ton accord.

**4. CHAINLINK FLIP contre EXCHANGE FLIP.** Résultat net : les 37 bascules récentes qui ont donné un signal arrivent **toutes** avec un nouveau prix Chainlink. Aucune ne vient d'un mouvement des exchanges seul. C'est logique : dans la dernière minute, c'est chaque nouveau prix Chainlink qui fait bouger la moyenne de fin.

**5. FLIP SURPRISE SCORE.** Couvert par l'idée 12. La partie « inattendue » ne prédit pas mieux que l'avantage instantané.

**6. Le carnet peut réagir sans changer de favori.** C'est une remarque juste, et je l'ai mesurée en continu (idée 7).

**7. FLIP INFORMATION ADVANTAGE.** Seuils fixés avant de regarder : 1/3 et 2/3 du mouvement de notre probabilité, sur les 37 bascules récentes.
- Réaction faible : 25 achats, 68 % gagnés, +537 $.
- Réaction partielle : 9 achats, 89 % gagnés, +98 $.
- Réaction forte : 1 seul cas.

Dans la grande majorité des cas, le carnet n'avait presque pas réagi au moment du signal. C'est cohérent avec la réponse décisive : il réagit juste après.

**8. ALPHA DNA.**
- Type A (information) : c'est la source principale. Le marché nous rejoint dans la seconde (98-99 % de la convergence).
- Type B (valorisation) : il existe aussi (voir idée 9).
- Type C (liquidité) : avec 50 $, la quantité ne limite presque jamais.

**9. SAME INFORMATION, DIFFERENT PRICE.** Oui, c'est mesurable. Pour une même probabilité de notre modèle, les contrats nettement moins chers gagnent bien plus souvent que leur prix :

| Notre probabilité | Prix moyen | Gagnés |
|---|---|---|
| 40-60 % | 0,25 | 41 % (+16 points) |
| 60-80 % | 0,41 | 76 % (+35 points) |
| 80-100 % | 0,48 | 93 % (+45 points) |

Les contrats plus chers que notre probabilité perdent de 2 à 25 points. Notre modèle classe correctement les contrats sur ces jours-là.

**10. UNEXPECTED SETTLEMENT REVISION.** Mesuré : sur les 3 s avant le signal, la partie « mécanique » (le temps passe, rien de nouveau) ne pèse presque rien (−0,009 en moyenne). La partie inattendue fait presque tout (+0,173). Nos signaux naissent donc d'une information nouvelle, pas de l'écoulement du temps.

**11. EDGE OWNERSHIP.** Mesuré sur les 3 s avant le signal, avec seulement ce qui était connu à l'achat :
- Notre probabilité a monté : 73 achats, +681 $, +61 % par $.
- Désaccord déjà présent : 28 achats, +684 $, +99 % par $.
- Le prix Polymarket a chuté seul : 20 achats, +199 $, **+35 % par $**, 7 pertes de suite.

Ton hypothèse va dans le bon sens (un effondrement du prix seul est le moins bon), mais 20 cas ne prouvent rien. À suivre en direct.

**12. PRICE OF SURPRISE.** Rejeté sur ces données. Corrélations avec le gain :
- avantage instantané : +0,17 ;
- partie inattendue : +0,15 ;
- surprise non intégrée : +0,12.

Le seuil du hasard est d'environ 0,17. Les signaux à forte surprise non intégrée rapportent même moins (+755 $ contre +1 394 $).

**13. CONVERGENCE ATTRIBUTION.** C'est la réponse décisive en tête de rapport : le marché rejoint notre modèle (98-99 % dans la première seconde).

**14. CONVERGENCE ATTRIBUTION ENGINE.** Les 5 classes sont faites, à 1 s et 5 s. Le groupe « Polymarket rejoint » est de loin le meilleur. Mais c'est un diagnostic : on ne le sait qu'après l'achat.

**15. MARKET TRUTH RACE.** Quand notre modèle et le carnet divergent de plus de 15 points (Brier, plus bas = meilleur) :

| Temps restant | Notre modèle | Carnet |
|---|---|---|
| 90-60 s | 0,208 | 0,233 |
| 60-40 s | 0,183 | 0,209 |
| 40-20 s | **0,138** | **0,119** |

Dans la fenêtre 40-20 s, c'est le carnet qui a raison plus souvent. **Proposition à tester (pas à appliquer)** : regarder au bilan, sur les achats du fantôme, si ceux de 40-20 s font moins bien que ceux de 90-40 s.

**16. MARKET CATCH-UP PREDICTOR.** Non construit. Avec 140 signaux et 6 variables, on ajusterait du bruit. Surtout, la réponse décisive montre que le marché nous rejoint presque toujours : le prédicteur n'aurait pas grand-chose à prédire. À reprendre avec plusieurs semaines de données.

**17. DOUBLE CONFIRMATION ALPHA.** Même raison. Attendre la confirmation coûte 8 à 13 c par jeton (le marché rejoint en moins d'une seconde). Le rapport précédent montrait aussi qu'attendre le prochain prix Chainlink donnait moins au total.

**18. EDGE DECAY contre ALPHA DECAY.** C'est exactement ce qu'on observe. L'avantage affiché fond, mais le contrat acheté au signal vaut plus juste après : le prix acheteur passe de 0,23 à 0,37 en 1 s. La convergence est une validation, pas une dégradation.

**19. DUAL ALPHA LEDGER.** Mesuré. Une revente avec bénéfice serait possible dans 59 % des cas après 1 s, mais garder jusqu'au règlement rapporte deux fois plus par jeton (+0,20 contre +0,09). Pas de sortie anticipée.

**20. MARKET VALIDATION RATIO.** C'est la colonne « Part du marché » du premier tableau : 98-99 % à moins de 1 s, 81 % à 10 s, 56 % à 20 s.

**21. CAPTURED EDGE.** L'avantage au signal est de 0,26. Il reste 0,18 pour un ordre qui arrive 0,25 s plus tard, et 0,13 à 1 s. Notre capture réelle dépendra entièrement de la vitesse de l'ordre. On ne la connaîtra qu'avec de vrais ordres.

**22. Expérience prioritaire.** Les étapes 1 à 4 sont faites ci-dessus. Pour l'étape 5 (validation sur les prochains cycles), aucune règle n'est retenue : les fantômes continuent sans changement.

## Ce que je te propose (tu décides)

1. Ne rien changer aux fantômes. Le bilan reste aujourd’hui samedi à 15:00.
2. Après le bilan, si TWAP FIN tient en direct : le test réel à 1 $ devient la priorité, pour mesurer **notre vraie latence**. C'est elle qui décide du gain réel.
3. Au bilan, comparer les achats 90-40 s et 40-20 s du fantôme TWAP FIN (idée 15).
