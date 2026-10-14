# Bot95 — H1086 : gros achats dans le sens du BTC, confirmation sur 5 jours neufs (09.10 → 13.10.2026)

## Verdict

**Non confirmé.** Sur les 5 jours neufs, suivre un gros achat (500 $ ou plus) fait dans le sens du mouvement BTC **perd un peu** :

- 412 achats, 381 gagnés (92,5 %) pour un prix moyen de 0,930 ;
- ROI **−1,6 %**, P&L **−66 $** à 10 $ par achat ;
- intervalle de confiance à 90 % : **[−172 ; +37] $**. Il contient 0, et le résultat est négatif.

La piste vue après H1085 (+1,3 point au-dessus de notre prix en validation) ne se retrouve pas : sur les jours neufs, l'écart est de **−0,5 point**. Ce n'était donc pas un vrai avantage, mais un hasard de la période 01–08.10. La version limitée aux prix ≤ 0,95 fait pire (−5,2 %). Le contrôle (gros achat **contre** BTC) ne donne rien non plus.

Aucun fantôme proposé, rien lancé. Aucun ordre n'a été passé. Aucun fichier du bot (bot95/src, bot95/rapide), aucun workflow et aucun fantôme n'a été modifié.

## Règle testée (figée avant tout calcul)

La règle a été écrite et poussée (commit f68f1c1) **avant** de calculer le moindre chiffre sur 09–13.10. Le calcul a ensuite été lancé une seule fois. Les définitions sont celles de H1085, sans changement :

- **Gros achat** : achats preneur (première ligne de chaque transaction) d'un même portefeuille sur la même issue, regroupés en rafale de 5 s au plus. L'événement a lieu quand le cumul franchit 500 $.
- **Sens du BTC** : mouvement de BTC sur les 10 secondes d'avant, en écarts-types. « Avec BTC » veut dire plus de 1 écart-type dans le sens du gros. « Contre BTC » veut dire 1 écart-type ou plus dans l'autre sens.
- **Notre achat** : on achète la même issue que le gros, au prix médian des achats 1 à 6 secondes après lui. Frais 0,07·p·(1−p). On garde le billet jusqu'au règlement. On fait un seul achat par cycle, sur le premier gros achat qui remplit la condition, à 10 $ par achat.
- **Critère** : ROI > 0 **et** intervalle à 90 % du P&L entièrement au-dessus de 0. L'intervalle est calculé en tirant des cycles au hasard (1 440 cycles, 10 000 tirages).

## Résultats

**Règle principale : suivre un gros achat dans le sens du BTC**

| Jour | Achats | Gagnés | Prix moyen | ROI | P&L | IC 90 % |
|---|---|---|---|---|---|---|
| 09.10 | 112 | 103 | 0,930 | −3,2 % | −36 $ | [−91 ; +15] $ |
| 10.10 | 72 | 67 | 0,902 | +3,7 % | +26 $ | [−21 ; +71] $ |
| 11.10 | 69 | 60 | 0,905 | −8,7 % | −60 $ | [−112 ; −12] $ |
| 12.10 | 43 | 42 | 0,951 | +4,5 % | +20 $ | [−9 ; +50] $ |
| 13.10 | 116 | 109 | 0,954 | −1,4 % | −16 $ | [−69 ; +33] $ |
| **Total** | **412** | **381** | **0,930** | **−1,6 %** | **−66 $** | **[−172 ; +37] $** |
| Total, prix pessimiste | 412 | 381 | 0,932 | −1,8 % | −74 $ | [−180 ; +27] $ |

Le prix pessimiste est le plus haut entre notre prix et le prix juste avant le gros achat.

**Secondaire : même règle, seulement quand notre prix est ≤ 0,95**

| Jour | Achats | Gagnés | Prix moyen | ROI | P&L | IC 90 % |
|---|---|---|---|---|---|---|
| 09.10 | 27 | 18 | 0,750 | −17,0 % | −46 $ | [−101 ; +5] $ |
| 10.10 | 35 | 30 | 0,816 | +6,0 % | +21 $ | [−27 ; +66] $ |
| 11.10 | 23 | 15 | 0,738 | −24,0 % | −55 $ | [−105 ; −10] $ |
| 12.10 | 7 | 6 | 0,768 | +21,5 % | +15 $ | [−14 ; +47] $ |
| 13.10 | 26 | 22 | 0,837 | +1,6 % | +4 $ | [−40 ; +44] $ |
| **Total** | **118** | **91** | **0,787** | **−5,2 %** | **−61 $** | **[−161 ; +36] $** |

**Contrôle : suivre un gros achat CONTRE le sens du BTC**

| Jour | Achats | Gagnés | Prix moyen | ROI | P&L | IC 90 % |
|---|---|---|---|---|---|---|
| 09.10 | 49 | 34 | 0,715 | −10,9 % | −53 $ | [−133 ; +24] $ |
| 10.10 | 19 | 9 | 0,561 | −35,9 % | −68 $ | [−127 ; −14] $ |
| 11.10 | 23 | 14 | 0,638 | −17,1 % | −39 $ | [−105 ; +32] $ |
| 12.10 | 13 | 10 | 0,701 | +12,5 % | +16 $ | [−33 ; +69] $ |
| 13.10 | 40 | 24 | 0,552 | +30,7 % | +123 $ | [−43 ; +313] $ |
| **Total** | **144** | **91** | **0,636** | **−1,5 %** | **−22 $** | **[−233 ; +210] $** |
| Total, prix pessimiste | 144 | 91 | 0,702 | −10,7 % | −154 $ | [−331 ; +33] $ |

Avec le plafond à 0,95, le contrôle donne 119 achats, 66 gagnés, un prix moyen de 0,563, un ROI de −2,2 %, un P&L de −26 $ et un IC de [−239 ; +211] $.

**Lecture.**

- **Les deux sens donnent à peu près le même résultat**, légèrement négatif. Le sens du BTC ne distingue donc pas les bons gros achats des mauvais.
- **Les journées se contredisent.** La règle principale est positive deux jours sur cinq (10.10 et 12.10) et franchement négative le 11.10. C'est le profil du bruit, pas d'un avantage.
- **Le tableau descriptif de H1085 a menti.** En validation, on y lisait +1,3 point au-dessus de notre prix. Sur les jours neufs, on lit −0,5 point, et −1,6 point pour les achats à 0,95 ou moins. C'est exactement pour cela qu'une piste vue après coup doit être retestée sur des données neuves.

## Données

- **Transactions** : marchés BTC 5 min Up/Down dont le début se situe entre le 09.10 00:00 et le 14.10 00:00 UTC, soit 1 440 cycles (288 par jour). Les fichiers viennent de la branche donnees-btc pour les 09–12.10 et de la branche pt-polytrades_2026-10-13 pour le 13.10.
  - On compte 2 867 gros achats de 500 $ ou plus.
  - Pour 63 marchés de la fin du 12.10, le résultat manquait dans le fichier : il a été pris dans bot95/officiels.json, qui concorde à 100 % sur les 225 autres marchés de ce jour.
- **Prix BTC** : comme dans H1085, BTCUSDT au comptant Binance à la seconde, mais de deux sources, car le téléchargement direct (data.binance.vision) est bloqué ici :
  - **09–11.10** : bougies Binance 1 s officielles, la même source que H1085 ;
  - **12–13.10** : colonne binance_spot enregistrée par le bot lui-même (bot95/donnees/…/rec_BTC et sig_BTC). Cette colonne est identique aux bougies Binance les jours où les deux existent (écart médian 0, 9 cas sur 10 à 0,01 $ ou moins).

## Limites

- **Trous dans les données BTC du bot.** Les enregistrements couvrent 70 % des secondes du 12.10 et 95 % du 13.10. 230 gros achats sur 2 867 (8 %) n'ont pas pu être classés et ont été écartés (190 le 12.10, 40 le 13.10), ce qui explique le petit nombre d'achats ce jour-là. Pour le 12.10 et le 13.10, la valeur prise est la dernière relevée par le bot dans la seconde, et non la clôture officielle de la bougie.
- **Exécution inconnue**, comme dans H1085. Notre prix est la médiane des transactions des 5 secondes suivantes, pas un vrai ordre.
- **Cinq jours seulement.** L'intervalle est large (environ ±100 $), et un petit avantage de l'ordre de +0,5 point ne pourrait pas être détecté. En revanche, le +1,3 point vu en validation est, lui, nettement écarté : ici, l'écart est négatif.

Fichiers : etude/bot5min/confirmation_gros_sens_btc_h1086.py (règle figée, commit f68f1c1), etude/bot5min/confirmation_gros_sens_btc_h1086.json (chiffres bruts).
