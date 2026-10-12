# Bot95 — Contrôle de robustesse du modèle E (TWAP FIN QUANTILES)

BTC, 850 cycles du 07.10 08:00 au 10.10 07:15. On compare deux versions de TWAP FIN :
- **A** : la version originale ;
- **E** : la version « quantiles », dont les probabilités sont lues dans des tables d'erreurs passées.

**Périodes :**
- apprentissage : jusqu'au 08.10 22:00 (les tables E ont été apprises sur les cycles d'avant 21:55, donc sur une partie de cette période) ;
- validation : du 08.10 22:00 au 09.10 23:36 ;
- nuit du 10.10 : à part.

**Règles du test :**
- Les tables E utilisées sont **exactement** celles du bot.
- L'écart entre Bybit et Chainlink est maintenant recalculé **à chaque seconde exacte**, au lieu d'une fois toutes les 5 s.
- Aucun paramètre n'a été modifié, aucun argent réel n'est engagé.

**À savoir :** le fantôme E tourne déjà depuis 09:30, après ton « 1 et 2 ». Il ne touche à aucun autre fantôme. Si tu juges ce rapport insuffisant, je l'arrête.

## Verdict

**Aucun défaut majeur, mais le gain annoncé de +664 $ ne tient pas.**

1. **Anomalie importante :**
   - Le gain de +664 $ venait en grande partie de la façon dont l'écart Bybit/Chainlink était recalculé (une fois toutes les 5 s).
   - En le recalculant à chaque seconde, l'avance de E en validation tombe à **+48 $**, et à **+135 $** validation et nuit réunies.
   - Ce n'est **pas statistiquement significatif** : il y a 38 % de chances que l'écart soit nul ou négatif.
2. **Points favorables, stables :**
   - E fait **au moins aussi bien que A à tous les décalages testés et chaque jour**.
   - Il a **des creux plus faibles** et **des séries de pertes plus courtes**.
   - Il est **beaucoup moins sensible** à un calcul fait avec des données un peu vieilles.
3. **Les tables sont bien figées** et apprises uniquement sur l'apprentissage.
4. **Conclusion :** E peut rester en fantôme à côté de A. **Il n'est pas validé comme amélioration du gain.** C'est un modèle plus prudent et plus stable, dont l'avantage en dollars reste à prouver sur des jours nouveaux.

## 1. Décalages de calcul et d'exécution, sans fuite

- **Décalage négatif :** le moteur calcule avec des données plus vieilles (calcul en retard).
- **Décalage positif :** la décision est prise avec les données du moment, mais l'achat se fait plus tard, au prix du carnet à ce moment-là (exécution en retard).

Dans aucun cas une donnée future n'est utilisée.

| Décalage | Période | A : achats / résultat / creux / pertes de suite | E : achats / résultat / creux / pertes de suite |
|---|---|---|---|
| −1 s | apprentissage | 125 / +157 $ / −458 $ / 12 | 109 / **+523 $** / −360 $ / 7 |
| −1 s | validation | 77 / +362 $ / −628 $ / 8 | 67 / **+866 $** / −301 $ / 7 |
| −1 s | nuit | 29 / −195 $ / −446 $ / 6 | 29 / **+205 $** / −336 $ / 4 |
| −0,5 s | apprentissage | 113 / **+503 $** / −396 $ / 12 | 97 / +83 $ / −416 $ / 7 |
| −0,5 s | validation | 68 / +255 $ / −647 $ / 7 | 59 / **+1 159 $** / −239 $ / 7 |
| −0,5 s | nuit | 30 / −140 $ / −382 $ / 6 | 29 / **+204 $** / −322 $ / 4 |
| **0** | apprentissage | 84 / +1 073 $ / −160 $ / 5 | 77 / **+1 264 $** / −136 $ / 4 |
| **0** | validation | 57 / +887 $ / −215 $ / 5 | 51 / **+935 $** / −141 $ / 4 |
| **0** | nuit | 28 / −182 $ / −322 $ / 8 | 25 / **−95 $** / −280 $ / 3 |
| +0,5 s | apprentissage | 84 / +1 175 $ / −249 $ / 5 | 77 / **+1 270 $** / −150 $ / 4 |
| +0,5 s | validation | 57 / **+1 279 $** / −192 $ / 5 | 51 / +1 115 $ / −180 $ / 4 |
| +0,5 s | nuit | 28 / −350 $ / −364 $ / 8 | 25 / **−19 $** / −232 $ / 3 |
| +1 s | apprentissage | 84 / −25 $ / −344 $ / 5 | 76 / **+518 $** / −339 $ / 4 |
| +1 s | validation | 57 / +620 $ / −313 $ / 5 | 51 / +577 $ / −215 $ / 4 |
| +1 s | nuit | 28 / −354 $ / −495 $ / 8 | 25 / **+70 $** / −311 $ / 3 |

**Écart E − A, validation et nuit réunies :**

| Décalage | A | E | E − A |
|---|---|---|---|
| −1 s | +167 $ | +1 071 $ | +904 $ |
| −0,5 s | +115 $ | +1 362 $ | +1 247 $ |
| 0 | +705 $ | +840 $ | +135 $ |
| +0,5 s | +929 $ | +1 096 $ | +167 $ |
| +1 s | +266 $ | +647 $ | +381 $ |

**Ce que le tableau montre :**
- L'écart est positif à tous les décalages, mais sa taille varie énormément : de +135 $ à +1 247 $.
- Quand le calcul se fait avec des données vieilles d'une demi-seconde à une seconde, A s'effondre (+115 à +167 $) alors que E tient (+1 071 à +1 362 $). E est plus robuste à un calcul en retard.
- Le résultat de A lui-même varie de +887 $ à +1 279 $ en validation pour une demi-seconde d'écart. **Les résultats en dollars dépendent de quelques trades.** Il faut juger sur de nombreux jours.

## 2. D'où vient l'écart en validation (décalage 0) : +48 $

A gagne +887 $ et E +935 $.

| Composante | Cycles | A | E | Contribution E − A |
|---|---|---|---|---|
| achats identiques (même côté, même instant) | 32 | +459 $ | +459 $ | 0 $ |
| même côté, instant différent (prix différent) | 15 | +488 $ | +361 $ | **−128 $** |
| côtés opposés | 4 | +13 $ | +116 $ | **+103 $** |
| A achète, E s'abstient | 6 | −73 $ | — | **+73 $** |
| E achète, A s'abstient | 0 | — | — | 0 $ |

**Lecture :**
- **Pertes évitées par E :** 5 cycles, 77 $ de pertes évitées.
- **Gains sacrifiés :** 1 seul, un petit jackpot de 4 $ (une toute petite quantité disponible).
- **Différences d'exécution :** E entre parfois plus tard que A, à un autre prix, ce qui coûte 128 $ sur 15 cycles.
- **Côtés opposés :** E prend 4 fois le côté contraire de A et gagne 103 $ de plus.
- **Les 3 plus grosses contributions :** 09.10 00:15 (−206 $), 09.10 09:10 (−164 $), 09.10 23:15 (+151 $). Trois cycles pèsent plus que l'écart total.

## 3. Par journée et incertitude statistique

| Journée | Cycles | A | E | E − A |
|---|---|---|---|---|
| 07.10 | 191 | +372 $ | +491 $ | +119 $ |
| 08.10 | 288 | +879 $ | +971 $ | +92 $ |
| 09.10 | 284 | +740 $ | +751 $ | +11 $ |
| 10.10 (nuit) | 87 | −213 $ | −108 $ | +105 $ |

E fait mieux que A **chaque jour**, mais de peu.

**Incertitude :** sur la validation et la nuit (395 cycles), on refait le calcul 10 000 fois en tirant au hasard des blocs d'une heure (12 cycles) :
- **intervalle à 90 % de l'écart E − A : de −678 $ à +927 $** ;
- **probabilité que l'écart soit nul ou négatif : 38 %**.

L'avantage de E en dollars **n'est pas démontré**.

## 4. Les tables E sont-elles figées et apprises seulement sur l'apprentissage ?

- **Apprises sur l'apprentissage seulement :** oui. Le script d'export ne garde que les mesures de la période d'apprentissage. Les tables contiennent 29 102 mesures, exactement le nombre de mesures d'apprentissage. Aucune mesure de validation ni de la nuit n'y entre.
- **Figées :** oui. Dans le bot, les tables sont une constante lue dans un fichier. Le contrôle automatique a trouvé 0 endroit du code qui la modifie.
- **Pas de fuite entre périodes :** le dernier cycle d'apprentissage se termine avant le premier cycle de validation.

## 5. Ce qui est en place (sans argent réel, aucun paramètre ne change tout seul)

- **Fantôme E « TWAP fin quantiles » :** il tourne à côté de TWAP fin original depuis 09:30. Aucun autre fantôme n'a été modifié.
- **Moniteur de santé** sur la page des fantômes (https://bot95.pitch67.workers.dev/nouveaux), mis à jour depuis 09:55 :
  - **Brier par tranche de 3 h**, moteur contre carnet, avec l'alerte CUSUM ;
  - **Brier par régime** (calme / agité) pour A, E et le carnet ;
  - **Intervalles de prévision** : part des résultats officiels tombés dans les intervalles à 50, 80 et 95 %, pour A et pour E ;
  - **Calibration** : par tranche de 10 %, la part de cycles où Up a vraiment gagné, pour A et pour E.
  - Il se remplit au fil des cycles réglés. Il n'enregistre et n'affiche que des mesures : aucune décision n'est modifiée.

## Anomalies relevées

1. **Le chiffre de +664 $ était trop optimiste**, dû à un détail de calcul (rafraîchissement toutes les 5 s). Je l'avais présenté comme le résultat principal : c'était une erreur de ma part, corrigée ici.
2. **Le bot en direct rafraîchit aussi l'écart Bybit/Chainlink toutes les 5 s.** Ses résultats en direct ressembleront donc plutôt à l'ancien calcul. C'est une source de variation, pas une fuite de données. Je ne le change pas sans ton accord.
3. **Les résultats en dollars de TWAP fin dépendent de quelques trades** : une demi-seconde de décalage fait varier A de près de 400 $. Toute comparaison doit porter sur plusieurs jours nouveaux.

**Je te propose (tu décides) :** garder E en observation, sans le considérer comme validé, et refaire ce même contrôle dans 3 à 5 jours, sur des cycles que ni A ni E n'ont jamais vus.
