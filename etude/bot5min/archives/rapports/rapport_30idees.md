# TWAP FIN — les 30 idées testées et commentées

BTC, 693 cycles du 07.10 08:05 au 09.10 22:35. Le carnet est enregistré 4 fois par seconde. Le règlement est reconstruit exactement (moyenne Chainlink des 60 dernières secondes).

Les probabilités utilisent seulement ce qui était reçu à l'instant. Les achats simulés se font au meilleur vendeur, limités à la quantité affichée, frais compris, avec un achat par cycle.

**Prudence :** 2,5 jours de données, 140 signaux. Tout ce qui suit est une piste, pas une preuve. Les fantômes en direct décideront.

## En bref : ce que j'ai appris

1. **L'avantage disparaît très vite.** Au moment du signal, l'avantage moyen est de +0,26. Il tombe à +0,18 après 0,25 s et à +0,13 après 1 s. Un signal ≥ 0,20 n'est encore là que dans 51 % des cas après 0,25 s, et 29 % après 1 s. Mais le prix bouge *dans notre sens* (le marché finit par nous donner raison) : acheter un peu plus tard reste gagnant, juste moins. **La vitesse d'exécution sera décisive en réel.**
2. **Le modèle original reste le meilleur** : +2 323 $ sur 140 achats, contre +1 971 $ pour sauts et +1 009 $ pour correction spot-perp. La correction spot-perp est la plus faible, alors que ses coefficients ont été ajustés sur ces mêmes jours : c'est mauvais signe pour elle.
3. **L'écart Binance − perp annonce un peu l'erreur finale** (corrélation +0,13, stable sur les jours jamais vus). Son sens est juste 62 % du temps. Mais la partie « nouvelle » de l'écart n'apporte rien de plus que son niveau : le niveau suffit.
4. **Le meilleur groupe : notre modèle a changé de favori, le carnet jamais.** 24 achats, 79 % gagnés, +1 015 $. Ce sont exactement les cycles où le carnet n'a pas compris la moyenne de fin.
5. **Attendre le prochain prix Chainlink** (et n'acheter que si l'avantage tient encore) donne 53 achats au lieu de 140. Le résultat est +1 661 $ au lieu de +2 323 $, mais rapporte plus par dollar (+112 % contre +82 %), avec le même creux. C'est intéressant, mais pas démontré.
6. **Rien de tout cela ne justifie de changer les fantômes avant samedi.**

## A. Vitesse : combien de temps l'avantage reste achetable

| Délai d'achat | Avantage moyen | Encore ≥ 0,20 | Encore ≥ 0,10 | Prix moyen | Résultat |
|---|---|---|---|---|---|
| 0 s | +0,261 | 140 | 140 | 0,25 | +2 323 $ |
| 0,25 s | +0,178 | 72 | 112 | 0,34 | +2 845 $ |
| 0,5 s | +0,153 | 53 | 98 | 0,36 | +2 486 $ |
| 1 s | +0,132 | 41 | 88 | 0,38 | +731 $ |
| 2 s | +0,122 | 38 | 84 | 0,38 | +1 633 $ |
| 5 s | +0,095 | 20 | 72 | 0,39 | +853 $ |

Les résultats sautent de +731 à +2 845 $ selon le délai. C'est la marque d'un petit échantillon dominé par quelques gros gains à bas prix : il ne faut pas lire une tendance fine dedans.

Le message solide : la moitié de l'avantage part dans la première seconde, mais il en reste.

## B. Écart spot − perp

| Mesure | Corrélation (apprentissage) | Corrélation (test) |
|---|---|---|
| Binance − perp (niveau) | +0,134 | +0,128 |
| Coinbase − perp | +0,107 | +0,079 |
| partie nouvelle de l'écart | +0,063 | +0,082 |
| saut par rapport à la médiane de la minute | −0,015 | +0,049 |
| écart d'il y a 5 s | +0,121 | +0,107 |

La pente est d'environ 0,35 à 0,45 $ d'erreur par $ d'écart, sauf pour les écarts minuscules (bruit). Un écart qui dure plus de 5 s vaut davantage (pente 0,45) qu'un écart tout récent (0,14).

## C. Les trois modèles sur les mêmes cycles

| Modèle | Achats | Gagnés | Résultat | Par $ | Creux | Pertes de suite |
|---|---|---|---|---|---|---|
| original | 140 | 46 % | **+2 323 $** | +82 % | −160 $ | 5 |
| sauts | 126 | 51 % | **+1 971 $** | +69 % | −256 $ | 4 |
| correction spot-perp | 97 | 42 % | **+1 009 $** | +42 % | −447 $ | 5 |

**Répartition des cycles :**
- Les trois achètent le même côté : 75 cycles (original +1 658 $).
- Original seul : 18 cycles, −233 $.
- Correction seule : 4 cycles, −103 $.
- Côtés opposés : 17 cycles. L'original gagne +874 $, sauts +346 $, correction +36 $.
- L'original déclenche le premier 90 fois sur 105. Quand deux modèles sont d'accord, ils déclenchent presque toujours en même temps : « attendre la confirmation » ne coûte rien en prix, mais fait perdre les cycles où l'original est seul.

## D. Changements de favori

| Groupe | Achats | Gagnés | Résultat | Par $ |
|---|---|---|---|---|
| pas de changement dans le cycle | 81 | 33 % | +721 $ | +44 % |
| changement il y a < 3 s | 37 | 73 % | +816 $ | +115 % |
| changement il y a 3-10 s | 7 | 57 % | +62 $ | +25 % |
| changement il y a > 10 s | 15 | 40 % | +724 $ | — |
| notre modèle a basculé avant le carnet | 8 | 75 % | +64 $ | +32 % |
| le carnet a basculé avant notre modèle | 27 | 44 % | +524 $ | +89 % |
| **notre modèle a basculé, le carnet jamais** | **24** | **79 %** | **+1 015 $** | **+255 %** |
| oscillations (≥ 3 bascules en 30 s) | 12 | 67 % | +394 $ | +128 % |

## E. Le prochain prix Chainlink

| Groupe | Achats | Gagnés | Résultat | Par $ |
|---|---|---|---|---|
| le prix suivant va dans notre sens | 82 | 41 % | +1 707 $ | +105 % |
| le prix suivant va contre nous | 58 | 52 % | +616 $ | +51 % |
| attendre le prix suivant, acheter si avantage ≥ 0,20 | 53 | 36 % | +1 661 $ | +112 % |

Le prochain prix Chainlink arrive en moins de 2 s dans 134 cas sur 140 : attendre coûte peu de temps.

## Les 30 idées, une par une

**1. Résultats sur 692 cycles (rappel).** C'est la base de ce rapport. Mêmes chiffres retrouvés : l'original reste devant.

**1bis. TWAP FIN sauts (Student-t).** Il est déjà en fantôme. Il fait un peu moins bien que l'original (+1 971 $ contre +2 323 $), avec plus de gagnants (51 %) mais moins de gros gains. Il apporte 6 cycles « seul » à +173 $. À garder en observation.

**2bis. TWAP FIN correction spot-perp.** Il est déjà en fantôme. C'est le plus faible (+1 009 $, creux −447 $), alors même qu'il est ajusté sur ces jours. S'il ne se reprend pas en direct, il faudra l'arrêter. Je te le proposerai samedi.

**2. FAVORITE FLIP.** Testé (D). Un achat juste après un changement de favori de notre modèle gagne 73 % du temps (37 achats). C'est le cœur du signal : le moteur voit la moyenne de fin passer de l'autre côté.

**3. FLIP AGE.** Testé (D). Frais (< 3 s), c'est le meilleur. De 3 à 10 s, c'est faible. Au-delà de 10 s, les résultats sont bons mais tiennent à quelques achats : non concluant.

**4. FLIP QUALITY.** Testé partiellement par les oscillations : 12 achats à 67 %, donc les oscillations ne sont pas un danger ici. Je n'ai pas de mesure plus fine de la « qualité » qui tienne sur si peu de cas.

**5. MODEL DISAGREEMENT.** Testé (C). Quand les modèles achètent des côtés opposés (17 cycles), l'original gagne +874 $. Le désaccord n'est donc pas une raison de s'abstenir.

**6. ALPHA SEQUENCE.** Testé (C). L'original déclenche presque toujours en premier ou en même temps. La correction spot-perp est parfois en avance de 15 s (7 cycles), sans que ce soit rentable.

**7. MODEL LEADERSHIP.** Testé (C). Le meneur est l'original. Aucun modèle ne « prévient » les autres de façon utile.

**8. CONFIRMATION COST.** Testé (C). Le coût en prix est d'environ 0 c, puisqu'ils déclenchent ensemble. Le vrai coût est de rater les cycles « original seul » et « côtés opposés » : le résultat net serait légèrement en baisse, sans gain de sécurité clair.

**9. STABLE ALPHA.** Non testé directement. C'est très proche de E (« attendre que l'avantage tienne ») : la version « attendre le prochain Chainlink » rapporte plus par dollar, mais moins au total.

**10. EDGE HALF-LIFE.** Testé (A). La demi-vie de l'avantage est d'environ 0,5 s : il passe de +0,26 à +0,15 en 0,5 s.

**11. PERSISTENT MISPRICING.** Testé (A). Une partie persiste : 72 signaux sur 140 gardent ≥ 0,10 après 5 s. Le marché ne corrige pas tout.

**12. ECONOMIC PERSISTENCE.** Testé (A). La quantité affichée *augmente* quand on attend (62 → 200 jetons), car le carnet se recharge à un prix plus élevé. Avec 50 $, on n'est presque jamais limité par la liquidité.

**13. NEXT ORACLE UPDATE.** Testé (E). Quand le prochain prix Chainlink va dans notre sens, ça rapporte deux fois plus par dollar. Mais on ne le sait qu'après coup, sauf si on attend.

**14. ORACLE EVENT STUDY.** Couvert par A et E. La chronologie est : nouveau prix Chainlink, puis notre moteur bascule, puis le carnet suit en 0,25 à 1 s.

**15. ORACLE CONFIRMATION TRADE.** Testé (E, politique « attendre »). 53 achats, +1 661 $, +112 % par dollar, même creux. C'est la meilleure idée « d'exécution » de la série. **Proposition : un fantôme « TWAP fin confirmé Chainlink » à partir de samedi**, si tu es d'accord.

**16. ORACLE SURPRISE.** Non testé séparément. Prévoir le prochain prix Chainlink, c'est ce que fait déjà le moteur en prenant le prix BTC actuel. L'étude B montre qu'il reste très peu d'information en plus (corrélation 0,13).

**17. ORACLE ALPHA DECAY.** Testé (A), aux mêmes délais que demandé (0,25 / 0,5 / 1 / 2 / 5 s). Le palier de 0,1 s n'est pas mesurable : le carnet est enregistré tous les 0,25 s.

**18. LATENCY-ADJUSTED ALPHA.** Déductible de A. Avec la vitesse réelle du worker (environ 0,5 à 1 s entre l'information et l'ordre), il faut compter environ la moitié de l'avantage affiché. Le fantôme TWAP fin en direct mesure déjà cela, car il achète au carnet qu'il voit vraiment.

**19. ORACLE INNOVATION.** Testé (B). La partie « nouvelle » de l'écart spot-perp (corrélation +0,08) fait moins bien que son simple niveau (+0,13). Rejeté.

**20. SPOT-PERP SHOCK.** Testé (B). Le saut brutal par rapport à la médiane de la minute vaut ≈ 0 (−0,02 puis +0,05). Rejeté.

**21. SPOT-PERP LEADERSHIP.** Non testé : il faudrait savoir qui, du spot ou du perp, revient vers l'autre. Faible priorité, puisque le niveau de l'écart n'explique déjà que 2 % de l'erreur.

**22. ORACLE TRANSMISSION.** Partiellement couvert par B. Un écart qui dure plus de 5 s « passe » mieux dans la moyenne (pente 0,45) qu'un écart tout récent (0,14).

**23. DOUBLE RETARD.** C'est exactement le groupe D « notre modèle a basculé, le carnet jamais » : 79 % gagnés, +1 015 $. C'est le signal le plus fort de l'étude, mais sur 24 achats.

**24. SPOT-PERP NON LINÉAIRE.** Testé (B). La pente est à peu près constante (0,35 à 0,39) de 2 à 30 $. Les très petits écarts sont du bruit. Pas de non-linéarité utile.

**25. SPOT-PERP PERSISTENCE.** Testé (B). L'écart d'il y a 5 s annonce presque aussi bien que l'écart actuel (+0,11 contre +0,13) : l'information est lente, pas un éclair.

**26. TRIPLE RESIDUAL.** Non testé : il manque une 3e source fiable à la seconde. Faible priorité.

**27. PRICE IMPACT FAILURE.** Non testé : il faut le flux d'ordres agressifs du perp, que nous n'enregistrons pas finement. Les essais précédents sur le flux d'ordres n'ont rien donné.

**28. SPOT-PERP ABSORPTION.** Même raison que l'idée 27. Mis de côté.

**29. RESIDUAL TRANSMISSION SCORE.** Ce serait un score combinant 19 à 28. Comme chaque morceau est faible ou nul, je ne le construis pas : on ajusterait du bruit.

**30. Signe de l'erreur.** Testé (B). Le sens de l'écart Binance − perp annonce le sens de l'erreur finale 62 % du temps sur des jours jamais vus. C'est réel mais modeste. Cela confirme que la correction spot-perp vise juste en direction, mais elle pèse trop dans la probabilité.

## Ce que je te propose (tu décides)

1. Ne rien changer avant le bilan de samedi 15:00.
2. Samedi : comparer en direct l'original, sauts et correction. Si la correction reste dernière, l'arrêter.
3. Samedi : ajouter un fantôme « TWAP fin confirmé par le prochain Chainlink » (idée 15).
4. Plus tard, après plus de données : un fantôme « notre modèle a basculé, le carnet non » (idées 2 / 23).
