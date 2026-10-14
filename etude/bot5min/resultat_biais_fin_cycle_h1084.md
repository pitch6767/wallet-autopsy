# Bot95 — H1084 : biais favori / billet en fin de cycle (27 jours, 12.09 → 08.10.2026)

## Verdict

**Le concept Bot95 d'origine ne gagne pas.** Acheter le favori entre 0,90 et 0,98 quand il reste 20 à 60 s ne rapporte rien après frais :

- exploration : +0,1 % ;
- validation : −1,5 % ;
- au prix pessimiste : −1,3 % et −2,3 %.

**Un filtre sur la distance au prix à battre change le résultat.** La règle **B3** n'achète le favori que si BTC est à au moins 3 écarts-types du prix à battre, dans le sens du favori. Elle passe le critère figé :

- validation : 169 achats, 168 gagnés, ROI **+2,5 %** (IC 90 % [+1,2 ; +3,3] %) ;
- P&L : **+42 $** à 10 $ par achat, IC corrigé ×4 **[+11 ; +62] $** ;
- au prix pessimiste : +2,0 %, IC corrigé [+4 ; +50] $.

C'est un résultat **statistiquement positif mais petit** : environ +5 $ par jour à 10 $ par achat. Il repose sur la rareté des pertes : 9 pertes sur 675 achats au total, alors que le prix payé en tolérait environ 20. Trois limites restent sérieuses (voir « Limites ») : le seuil 3 a été choisi après plusieurs essais, Binance remplace Chainlink, et l'exécution réelle est inconnue.

**Proposition à Pitch, sans rien lancer :** un fantôme B3, en lecture seule. C'est à lui de décider.

**Les billets sont bien trop chers, comme le veut le biais favori-billet classique.** Acheter un billet à 0,02–0,20 avec 10 à 60 s restantes perd :

- −24 % en exploration et −23 % en validation au prix observé ;
- −47 % et −43 % au prix pessimiste.

Au prix observé, l'intervalle corrigé de la validation touche tout juste 0 ([−4 606 ; +114] $). Le biais n'est donc pas confirmé au sens strict du critère, mais il va nettement dans ce sens.

Aucun ordre n'a été passé. Aucun fichier du bot (bot95/src, bot95/rapide), aucun workflow et aucun fantôme n'a été modifié.

## Méthode

- **Données** : transactions publiques Polymarket BTC 5 min (achats seulement) et Binance BTCUSDT à la seconde. Aucun marché ouvert à partir du 09.10 00:00 UTC n'est utilisé.
- **Exploration** : 12.09–30.09, 5 459 cycles. **Validation** : 01.10–08.10, 2 304 cycles, lue une seule fois après le commit des règles (5ab61bb).
- **Instants** : 240, 245, …, 290 s, soit de 60 à 10 s avant la fin.
- **Prix du signal** : médiane des achats des 6 s précédentes, avec au moins 2 achats. Le favori est le côté au-dessus de 0,5.
- **Prix payé** : médiane des achats du côté acheté entre t+1 et t+6 s. **Frais** : 0,07·p·(1−p). Un seul achat par cycle et par règle (le premier instant qui déclenche), gardé jusqu'au règlement.
- **Distance au prix à battre (zf)** : le règlement compare la moyenne Chainlink des 60 dernières secondes à la moyenne des 60 s avant le début. On reproduit ce calcul avec Binance :
  - la partie déjà écoulée de la moyenne finale est connue ;
  - le reste est estimé au prix actuel ;
  - l'écart est divisé par l'incertitude de la partie restante (volatilité à 1 s sur 1 h).
- **Pourquoi Binance** : c'est une approximation. Avec Binance, la règle des moyennes donne le bon gagnant dans 97,7 % des cycles. En comparant simplement le prix à la fin et au début, on n'en trouve que 86 % : c'est pourquoi on utilise les moyennes.
- **Intervalles** : bootstrap par cycles, 10 000 tirages. Les cycles sans achat comptent pour 0 $. L'IC 90 % est simple. L'IC corrigé (Bonferroni, 4 règles) va des percentiles 1,25 à 98,75.

## Le piège de sélection, et comment il est traité

Un achat n'apparaît dans les données que si quelqu'un a traité ce côté dans les 6 s suivantes. Or ces moments ne sont pas neutres.

| Favori 0,90–0,98, 20–60 s | Exploration | Validation |
|---|---|---|
| Part des instants avec une transaction (« servis ») | 68 % | 66 % |
| Le favori gagne, instants servis | 95,6 % | 94,3 % |
| Le favori gagne, instants non servis | 99,6 % | 99,5 % |
| Prix du signal, servis / non servis | 0,948 / 0,973 | 0,947 / 0,973 |

Les transactions arrivent surtout quand le favori vacille. Un vrai ordre placé au bon moment pourrait donc être servi plus souvent, mais aussi à un prix moins favorable. Trois mesures en tiennent compte :

1. **Tous les cycles de la période comptent dans le P&L**, à 0 $ quand rien n'est servi. On n'extrapole pas à partir des seuls cycles servis.
2. **Un prix pessimiste est publié** : le plus haut entre le prix du signal et le prix d'après. Cela supprime la « bonne affaire » d'une glissade qu'un ordre envoyé au signal n'aurait pas eue.
3. **La calibration utilise le prix du signal**, mesuré avant l'instant t. La fréquence réelle est mesurée sur le résultat du cycle.

Le prix du marché, lui, n'est disponible que si des achats ont eu lieu : 82 % des cycles à 60 s de la fin, 47 % à 10 s.

## Résultats par règle (10 $ par achat)

| Règle | Période | Achats | Gagnés | Prix moyen | ROI (IC 90 %) | P&L | IC 90 % P&L | IC corrigé ×4 | ROI au prix pessimiste (IC corrigé P&L) |
|---|---|---|---|---|---|---|---|---|---|
| B1 favori 0,90–0,98, 20–60 s | exploration | 2 300 | 94,9 % | 0,942 | +0,1 % [−0,8 ; +1,0] | +22 $ | [−176 ; +221] | [−248 ; +288] | −1,3 % ([−561 ; −71]) |
| B1 | **validation** | 920 | 93,9 % | 0,942 | **−1,5 %** [−2,9 ; −0,1] | **−138 $** | [−268 ; −16] | **[−319 ; +28]** | −2,3 % ([−390 ; −53]) |
| B2 B1 + zf ≥ 2 | exploration | 1 365 | 97,4 % | 0,964 | +0,6 % [−0,1 ; +1,4] | +85 $ | [−17 ; +183] | [−57 ; +215] | +0,2 % ([−115 ; +158]) |
| B2 | **validation** | 494 | 97,0 % | 0,962 | **+0,4 %** [−1,0 ; +1,6] | **+18 $** | [−51 ; +82] | **[−78 ; +102]** | −0,2 % ([−106 ; +70]) |
| B3 B1 + zf ≥ 3 | exploration | 506 | 98,4 % | 0,968 | +1,5 % [+0,5 ; +2,4] | +75 $ | [+23 ; +121] | [+2 ; +135] | +1,0 % ([−20 ; +109]) |
| B3 | **validation** | 169 | 99,4 % | 0,969 | **+2,5 %** [+1,2 ; +3,3] | **+42 $** | [+20 ; +57] | **[+11 ; +62]** | +2,0 % ([+4 ; +50]) |
| B4 billet 0,02–0,20, 10–60 s | exploration | 2 446 | 8,4 % | 0,092 | −24,5 % [−36 ; −12] | −5 990 $ | [−8 894 ; −2 982] | [−9 853 ; −1 855] | −47,1 % ([−13 973 ; −8 865]) |
| B4 | **validation** | 1 019 | 9,2 % | 0,093 | **−23,5 %** [−40 ; −6] | **−2 389 $** | [−4 082 ; −601] | **[−4 606 ; +114]** | −42,5 % ([−5 816 ; −2 691]) |

Lecture :

- **B1 (Bot95 d'origine)** est nul en exploration et négatif en validation. Au prix pessimiste, il est négatif sur les deux périodes. Acheter un favori « à 95 % » sans autre filtre ne paie pas les frais et l'écart de prix.
- **B2 et B3** montrent que la distance au prix à battre sépare les bons favoris des mauvais. En exploration :
  - zf < 1 → −2,8 % (−10 % au prix pessimiste) ;
  - zf ≥ 2 → +0,6 % ;
  - zf ≥ 3 → +1,5 %.

  Seul B3 reste nettement positif en validation.
- **B3 jour par jour** : 22 jours positifs sur 27. Les 5 jours négatifs ont chacun 1 perte, sauf le 12.09 (4 pertes, −22 $).
  - Validation : 7 jours positifs sur 8, une seule perte (05.10).
  - 27 jours : 9 pertes sur 675 achats. Au prix payé (0,970 frais compris), il en fallait environ 20 pour être à zéro. Une égalité serait improbable (p ≈ 0,004).

## Calibration : prix du favori au signal → fréquence réelle de gain

Le prix est celui du signal (médiane des 6 s précédentes). Chaque ligne indique le nombre d'instants et le nombre de cycles. La colonne Binance donne la probabilité tirée de zf, pour comparaison.

| Temps restant | Prix favori | Exploration : n (cycles) prix → fréquence (Binance) | Validation : n (cycles) prix → fréquence (Binance) |
|---|---|---|---|
| 10–20 s | 0,80–0,85 | 81 · 0,831 → 0,864 (0,61) | 41 (36) · 0,831 → 0,805 (0,62) |
| 10–20 s | 0,85–0,90 | 148 · 0,881 → 0,865 (0,65) | 44 (40) · 0,881 → 0,909 (0,69) |
| 10–20 s | 0,90–0,95 | 244 · 0,933 → 0,975 (0,77) | 94 (78) · 0,936 → 0,968 (0,82) |
| 10–20 s | 0,95–0,98 | 607 · 0,974 → 0,982 (0,82) | 229 (173) · 0,974 → 0,987 (0,82) |
| 10–20 s | 0,98–0,995 | 5 918 · 0,990 → 0,999 (0,99) | 2 212 (1 209) · 0,990 → 1,000 (0,98) |
| 20–40 s | 0,80–0,85 | 369 · 0,832 → 0,862 (0,76) | 133 (108) · 0,832 → 0,827 (0,76) |
| 20–40 s | 0,85–0,90 | 513 · 0,881 → 0,910 (0,80) | 223 (175) · 0,881 → 0,928 (0,81) |
| 20–40 s | 0,90–0,95 | 974 · 0,934 → 0,952 (0,86) | 383 (276) · 0,934 → 0,930 (0,84) |
| 20–40 s | 0,95–0,98 | 1 830 · 0,973 → 0,982 (0,94) | 731 (459) · 0,973 → 0,992 (0,92) |
| 20–40 s | 0,98–0,995 | 8 084 · 0,990 → 0,999 (1,00) | 3 097 (1 361) · 0,990 → 0,998 (0,99) |
| 40–60 s | 0,80–0,85 | 837 · 0,831 → 0,855 (0,79) | 340 (274) · 0,831 → 0,821 (0,77) |
| 40–60 s | 0,85–0,90 | 1 069 · 0,882 → 0,910 (0,86) | 497 (372) · 0,884 → 0,867 (0,82) |
| 40–60 s | 0,90–0,95 | 1 821 · 0,933 → 0,952 (0,92) | 801 (548) · 0,933 → 0,920 (0,88) |
| 40–60 s | 0,95–0,98 | 2 970 · 0,973 → 0,981 (0,97) | 1 272 (759) · 0,973 → 0,984 (0,96) |
| 40–60 s | 0,98–0,995 | 6 783 · 0,990 → 0,997 (1,00) | 2 730 (1 241) · 0,990 → 0,997 (1,00) |

Les instants d'un même cycle sont liés : le nombre de cycles indépendants est plus faible que n. Les tranches 0,50–0,80 sont dans le fichier JSON.

Ce qu'il faut retenir :

- **Au prix du signal, le favori gagne un peu plus souvent que son prix**, le plus souvent de +1 à +4 points en exploration (une tranche à −1,6). C'est le sens du biais favori-billet : le billet (1 − prix) est trop cher.
- **En validation, l'écart est plus irrégulier.** Il est négatif dans plusieurs tranches entre 0,80 et 0,95, mais encore positif au-dessus de 0,95.
- **Cet avantage disparaît une fois l'achat fait.** Le prix réellement payé juste après le signal, plus les frais (~0,2 à 0,6 point), l'efface. Les cycles servis sont aussi ceux où le favori perd le plus souvent (voir plus haut).
- **Dans le marché, la probabilité Binance est plus basse que le prix** : 0,77 contre 0,93 à 10–20 s, par exemple. Cela ne veut pas dire que le marché a tort. Quand Binance n'est pas d'accord avec le marché, c'est le marché qui a raison, car il voit Chainlink et des flux plus rapides. C'est pour cela que B3 exige que les deux soient d'accord, et nettement.

## Limites

- **Binance remplace Chainlink.** Le vrai prix à battre et la vraie moyenne finale sont ceux de Chainlink. Avec Binance, 2,3 % des cycles sont mal classés. Un fantôme devrait calculer zf avec Chainlink ou avec le prix rapide recalé, comme le bot.
- **Seuil 3 choisi après plusieurs essais.** Une dizaine de variantes ont été regardées en exploration (seuils 2 / 2,5 / 3, tranches de prix, durées). La correction pour 4 règles ne couvre pas tous ces essais. B3 passe pourtant aussi au prix pessimiste, avec une seule perte sur 169 en validation.
- **Peu de pertes, donc un résultat fragile.** La règle gagne ~0,3 $ par achat gagné et perd ~10 $ par achat perdu. Deux pertes de plus sur la validation l'auraient ramenée à environ +22 $. Le bootstrap ne voit que les pertes observées : un krach rare (BTC qui se retourne de 3 écarts-types en 30 s, ou un écart Chainlink/Binance) peut coûter plus.
- **L'exécution est inconnue.** Le prix payé est celui des transactions des 6 s suivantes, pas le carnet d'ordres au moment du signal. La taille disponible à 0,96–0,98 n'est pas mesurée. Seuls ~20 achats par jour déclenchent.
- **Petit gain.** +42 $ en 8 jours à 10 $ par achat, soit environ +2,5 % par achat engagé. Ce n'est rentable que si l'exécution réelle tient ces prix.

## Fichiers

- Script figé : `etude/bot5min/biais_fin_cycle_h1084.py`
- Chiffres : `biais_fin_cycle_h1084_exploration.json`, `biais_fin_cycle_h1084_validation.json`
- PDF : `archives/pdf/biais_fin_cycle_h1084.pdf`
