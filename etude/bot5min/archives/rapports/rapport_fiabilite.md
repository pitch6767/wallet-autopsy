# Bot95 — Fiabilité du moteur TWAP FIN : les idées testées

**Données :** BTC, 849 cycles du 07.10 08:00 au 10.10 07:15, tels qu'enregistrés par le bot.

**Trois périodes séparées dans le temps :**
- **apprentissage** : avant le 08.10 21:55 ;
- **validation** : du 08.10 21:55 au 09.10 23:36 ;
- **nuit du 10.10** : à part.

Tout ce qui est appris l'est sur l'apprentissage seulement. Aucune stratégie n'a été modifiée. Ton document s'arrête au début de l'idée 54 : j'ai traité les idées 1 à 53.

## En bref

1. **La vraie cause de la mauvaise nuit est trouvée : le moteur se trompe sur sa propre incertitude, dans les deux sens.**
   - Quand le marché bouge, son incertitude est **trop grande** : l'erreur réelle ne fait que 0,78 à 0,93 fois ce qu'il annonce.
   - Quand le marché est **calme**, elle est **trop petite** : l'erreur réelle fait 1,14 à 1,60 fois ce qu'il annonce. 11 à 17 % des erreurs dépassent la limite où il n'en attendait que 5 %.
   - C'est exactement le « paradoxe de la volatilité » (idée 18).
2. **Le modèle E** remplace la courbe en cloche par la vraie distribution des erreurs passées, par tranche de temps et par régime, apprise sur l'apprentissage. C'est le **meilleur modèle testé jusqu'ici** :
   - il est meilleur dans les trois périodes ;
   - validation : +1 642 $ contre +978 $ ;
   - nuit : −95 $ contre −241 $ ;
   - il garde un peu moins de jackpots : 8 contre 11.
3. **Les certitudes fragiles se reconnaissent à l'avance**, avec des informations disponibles au moment de l'achat. Une certitude de plus de 95 % se révèle fausse 4 fois plus souvent quand :
   - elle vient d'un saut des exchanges ;
   - elle est née il y a moins de 3 s ;
   - ou aucune seconde de la fenêtre finale n'est encore connue.
4. **Les erreurs n'ont pas de mémoire.** Corriger le biais à partir des erreurs récentes ne servirait à rien.
5. **Le moniteur de santé aurait donné l'alerte** dès le 09.10 vers 21:00 : le moteur fait moins bien que le carnet depuis, de façon continue, à chaque fois en régime calme.

## Partie 1 — Prévoir la trajectoire Chainlink (idées 1-5)

Ces idées ont été testées ce matin (rapport « transmission vers Chainlink »).

- **Idées 1-3 (intégrale, réponse de Chainlink, transmission) :** Chainlink rattrape un mouvement commun des exchanges à environ 49 % en 2 s, 80 % en 5 s et 95 % en 10 s. Il ne suit qu'à 69 % un mouvement de Bybit seul.
- **Idée 4 (persistance des sauts) :** un saut isolé de Bybit reste sur Bybit, mais Chainlink n'en reprend que 40 à 50 %.
- **Idée 5 (Shock Decay) :** testé (modèles C et C2), pas démontré.

## Partie 2 — Robustesse du règlement (idées 6-13)

**Idées 6, 11-13 (part déjà connue, marge d'erreur).** Taux de certitudes de plus de 95 % qui se sont révélées fausses, selon le nombre de secondes de la fenêtre finale déjà connues :

| Secondes déjà connues | Certitudes > 95 % | Fausses | Dont nuit du 10.10 |
|---|---|---|---|
| 0 (avant la fenêtre) | 44 064 | **1,04 %** | 4,3 % |
| 1-20 | 38 089 | 0,35 % | 1,0 % |
| 21-40 | 42 559 | **0,19 %** | 0,3 % |

Une certitude bâtie sur des prix Chainlink déjà acquis est **5 fois plus fiable** qu'une certitude bâtie uniquement sur la prévision.

**Idées 7-10 (barrière, chemin requis, temps de franchissement, scénarios défavorables) :** ce sont d'autres façons d'écrire la même chose que l'écart-type du moteur. Le modèle E les remplace par les vraies erreurs observées. Je ne les ai pas codées séparément : elles n'apporteraient pas d'information nouvelle.

## Partie 3 — Les erreurs du moteur (idées 14-17)

**Idée 17 (quantiles des erreurs).** Erreur normalisée = erreur réelle de la moyenne finale divisée par l'incertitude annoncée par le moteur. Si le moteur était juste, elle aurait un écart-type de 1, et 5 % des valeurs sortiraient de ±1,96.

| Tranche | Régime | Écart-type réel | Hors ±1,96 (attendu 5 %) |
|---|---|---|---|
| avant la fenêtre | agité | 0,93 | 4,6 % |
| avant la fenêtre | **calme** | 1,14 | **11,0 %** |
| 45-60 s restantes | agité | 0,92 | 3,3 % |
| 45-60 s restantes | **calme** | 1,28 | **17,3 %** |
| 30-45 s | agité | 0,86 | 2,5 % |
| 30-45 s | **calme** | 1,35 | **13,8 %** |
| 15-30 s | agité | 0,78 | 2,5 % |
| 15-30 s | **calme** | 1,60 | **13,7 %** |

**Idée 21 (intervalles calibrés).** On apprend les intervalles sur l'apprentissage, puis on vérifie s'ils contiennent bien la part prévue des résultats :

| Période | Intervalle à 50 % | à 80 % | à 95 % |
|---|---|---|---|
| validation | 50 % | 80 % | 95 % |
| nuit du 10.10 | 52 % | 81 % | 94 % |

Les intervalles appris tiennent **exactement**, même pendant la nuit difficile.

- **Idées 14-15 (mémoire des erreurs, simulation corrélée) :** l'autocorrélation des erreurs de Chainlink à 1, 2, 5 et 10 s vaut −0,04, −0,03, +0,04 et +0,03, autrement dit rien. Les erreurs sont indépendantes. Un simulateur par blocs n'apporterait rien.
- **Idée 16 (suivi du biais) :** l'erreur moyenne est de +0,06 $, sans biais notable. D'un cycle au suivant, la corrélation des erreurs vaut 0,00. Corriger un biais récent n'aiderait pas.

## Partie 4 — Incertitude et excès de confiance (idées 18-23)

**Tournoi des probabilités.** Brier et perte log : plus bas = meilleur.

| Modèle | Validation (Brier / perte log) | Nuit (Brier / perte log) | Nuit : certitudes > 99 % fausses |
|---|---|---|---|
| A — moteur actuel | 0,0463 / 0,1588 | 0,0602 / 0,2252 | 1,6 % |
| D — prévision Chainlink | 0,0462 / 0,1544 | 0,0583 / 0,2065 | 1,2 % |
| **E — quantiles des erreurs** | **0,0453 / 0,1525** | **0,0583 / 0,2034** | **1,0 %** |
| F — plancher d'incertitude par tranche | 0,0460 / 0,1559 | 0,0611 / 0,2159 | 1,0 % |
| G — incertitude × 1,39 après un saut | 0,0463 / 0,1588 | 0,0602 / 0,2245 | 1,6 % |

**Rejeu TWAP FIN** (premier signal du cycle, avantage d'au moins 0,20, quantité affichée, frais compris) :

| Modèle | Apprentissage | Validation | Nuit | Jackpots (validation + nuit) |
|---|---|---|---|---|
| A — moteur actuel | +1 188 $ (85) | +978 $ (58) | −241 $ (28) | 11 |
| D — prévision Chainlink | +1 167 $ (69) | +759 $ (38) | **+175 $** (24) | 7 |
| **E — quantiles des erreurs** | **+1 408 $** (77) | **+1 642 $** (53) | −95 $ (25) | 8 |
| F — plancher d'incertitude | +1 569 $ (85) | +1 152 $ (60) | −391 $ (30) | 11 |
| G — incertitude après saut | +1 168 $ (85) | +995 $ (61) | −193 $ (27) | 11 |

- **Idée 18 (paradoxe de la volatilité) :** confirmé, voir la partie 3.
- **Idée 19 (plancher d'incertitude, modèle F) :** il gagne en validation mais perd davantage la nuit. Un simple plancher ne suffit pas, car il faut aussi **réduire** l'incertitude quand le marché bouge.
- **Idée 20 (incertitude élargie après un saut, modèle G) :** le facteur appris est de 1,39. Effet presque nul : les sauts sont trop rares pour peser sur le total.
- **Idée 21 :** voir les intervalles ci-dessus.
- **Idées 22-23 (audit des certitudes, part due à un saut) :** voir le tableau ci-dessous.

| Origine de la certitude (> 95 %) | Mesures | Fausses |
|---|---|---|
| pas de saut récent | 123 435 | 0,52 % |
| **saut des exchanges dans les 2 dernières secondes** | 1 277 | **2,35 %** |
| certitude présente depuis plus de 3 s | 115 060 | 0,44 % |
| **certitude née il y a moins de 3 s** | 9 652 | **≈ 1,8 %** |
| le dernier Chainlink donne déjà ce côté | 124 672 | 0,54 % |
| **seule l'extrapolation des exchanges donne ce côté** | 40 | **10 %** |

Une remarque utile : notre signal TWAP FIN naît **justement** au moment où la certitude apparaît, donc souvent dans la zone « née il y a moins de 3 s ». Cela explique une part de la fragilité.

## Partie 5 — Plusieurs futurs possibles (idées 24-26)

- **Idée 24 (moteur à scénarios) :** le modèle E en est la version mesurée. Au lieu d'inventer des scénarios, il utilise directement les écarts réellement observés dans le passé. Construire des scénarios à la main ajouterait des paramètres sans preuve.
- **Idées 25-26 (tournoi complet) :** voir les tableaux de la partie 4. Les modèles A, B, C, C2 et D ont été comparés ce matin, E, F et G aujourd'hui.

## Partie 6 — Utiliser le marché (idées 27-30)

- **Idées 27-29 :** le mélange moteur/carnet 50/50, mesuré hier, prévoyait mieux que chacun des deux. Le modèle E corrige le défaut d'incertitude sans regarder le carnet. Un arbitre plus complexe n'est pas justifié tant que E n'est pas vérifié en direct.
- **Idée 30 (qui a raison, et quand) :** mesuré hier. Notre moteur est meilleur entre 80 et 40 s et près du prix à battre. Le carnet est meilleur entre 40 et 30 s, et maintenant aussi **en régime calme** (partie 7).

## Partie 7 — Santé du modèle (idées 31-35)

On compare le moteur et le carnet par tranches de 3 heures. Un compteur d'alerte cumulatif (méthode CUSUM) déclenche quand le moteur fait durablement pire que le carnet.

| Tranche (heure suisse) | Volatilité médiane | Brier moteur | Brier carnet | Alerte |
|---|---|---|---|---|
| 09.10 09:00 | 2,4 $/s | 0,110 | 0,149 | — |
| 09.10 12:00 | 4,1 $/s | 0,053 | 0,028 | — |
| 09.10 18:00 | 3,9 $/s | 0,081 | 0,070 | — |
| **09.10 21:00** | 2,4 $/s | 0,122 | 0,110 | **⚠** |
| 10.10 00:00 | 1,3 $/s | 0,173 | 0,149 | ⚠ |
| 10.10 03:00 | 1,3 $/s | 0,079 | 0,057 | ⚠ |
| 10.10 06:00 | 1,0 $/s | 0,061 | 0,043 | ⚠ |

**Ce que ça montre :**
- **Idées 31-33 :** le moniteur aurait signalé le problème dès le 09.10 vers 21:00, quand le marché est devenu calme.
- **Idée 34 (poids dynamique entre moteur et carnet) :** à tester plus tard, avec ce compteur comme signal.
- **Idée 35 (réduire la mise quand le modèle est peu fiable) :** à tester seulement en fantôme, jamais comme arrêt automatique.

## Partie 8 — Apprendre des erreurs en direct (idées 36-40)

- **Idées 36-38 :** les erreurs sont indépendantes d'une seconde à l'autre, et d'un cycle à l'autre. Il n'y a pas de « série d'erreurs » à exploiter.
- **Idées 39-40 :** corriger avec les erreurs récentes n'apporterait rien. **Rejeté.**

## Partie 9 — Les révisions de probabilité (idées 41-47)

Voir aussi l'étude des basculements faite ce matin : quand la probabilité bascule de plus de 40 points en une seconde, le nouveau côté gagne 76 % du temps.

- **Idées 41-43 (d'où viennent les certitudes extrêmes) :** voir le tableau de la partie 4. Les certitudes provoquées par les exchanges, ou nées d'un saut, sont 4 à 5 fois moins fiables.
- **Idées 44-46 (stabilité, durée de vie d'une certitude) :** une certitude présente depuis plus de 3 s est 4 fois plus fiable qu'une certitude toute neuve. C'est mesurable au moment de l'achat, sans regarder l'avenir.
- **Idée 47 (amortisseur appris) :** c'est le modèle G. Effet négligeable.

## Partie 10 — Prix Chainlink « fantôme » (idées 48-53)

On compare plusieurs façons d'estimer les prochains prix Chainlink, sur la validation et la nuit. Erreur moyenne (RMSE) :

| Estimateur | Chainlink dans 1 s | dans 5 s | Moyenne finale |
|---|---|---|---|
| dernier Chainlink | 2,31 $ | 6,42 $ | 14,72 $ |
| dernier Bybit (moteur actuel) | **5,93 $** | 5,45 $ | 14,30 $ |
| consensus spot (Binance, Coinbase) | 3,70 $ | 4,79 $ | 14,27 $ |
| consensus des 4 exchanges | 4,29 $ | **4,58 $** | **14,13 $** |
| Chainlink + 0,98 × écart (modèle D) | 4,20 $ | **4,56 $** | **14,13 $** |
| **Chainlink + 0,24 × écart** | **1,83 $** | 5,58 $ | 14,45 $ |

- **Idées 48-50 :** le meilleur prix Chainlink fantôme dépend de l'horizon. Pour la seconde suivante : le dernier Chainlink plus un quart de l'écart. Pour 5 s et pour la moyenne finale : le consensus des 4 exchanges. **Bybit seul est le plus mauvais** pour la seconde suivante.
- **Idées 51-52 (avance et risque de publication) :** mesurés hier. Le marché rejoint notre moteur en moins d'une seconde, et le prochain prix Chainlink arrive en moins de 2 s dans 96 % des cas.
- **Idée 53 :** voir le tableau.

**Une remarque d'honnêteté :** le résultat du moteur actuel en validation n'est pas le même que dans le rapport de ce matin (+978 $ ici, +1 214 $ ce matin). La seule différence est le moment exact où l'écart Bybit/Chainlink est recalculé : toutes les 5 s, à une seconde près. Deux ou trois achats changent, et le résultat bouge de 236 $. Dans chaque tableau, tous les modèles sont comparés sur exactement les mêmes données. Mais cela montre à quel point le résultat dépend de quelques gros gains.

## Ce que je te propose (tu décides)

1. **Ajouter un fantôme « TWAP fin quantiles »** (modèle E). Même moyenne prévue que l'original, mais la probabilité vient de la distribution réelle des erreurs passées, par tranche de temps et par régime calme ou agité. Les tables sont figées, apprises sur l'apprentissage.
   - C'est le meilleur modèle testé, dans les trois périodes.
2. **Ajouter un moniteur de santé** sur la page du bot : comparaison moteur/carnet par tranche de 3 heures, avec alerte. Il ne change aucune décision.
3. Ne pas lancer F, G, la correction de biais ni le moteur à scénarios : ils ne sont pas démontrés.
4. Le test réel à 1 $ reste reporté.
