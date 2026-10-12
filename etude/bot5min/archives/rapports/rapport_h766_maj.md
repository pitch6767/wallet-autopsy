# Bot95 — H766–H775 refait avec plus de données — 11.10.2026, 19:15 UTC

Analyse refaite hors ligne avec les nouveaux cycles enregistrés à Dublin. Aucun ordre, aucun fantôme touché.

**Échantillon :**
- Avant (15:20 UTC) : 157 signaux sur 31 cycles.
- Maintenant : **278 signaux sur 55 cycles**.

## Ce qui change

| Mesure | Avant (31 cycles) | Maintenant (55 cycles) |
|---|---|---|
| Preneur à 164 ms, par signal | +29,7 $ [+6,0 ; +56,9] | **+14,9 $ [+0,4 ; +31,2]** : tout juste positif |
| Preneur à 250 ms | IC entièrement > 0 | **+13,2 $ [−0,9 ; +28,7]** : non démontré |
| Preneur à 500 ms | IC entièrement > 0 | **+9,5 $ [−2,3 ; +22,4]** : non démontré |
| Décisions uniques (une par cycle et par côté) | +21,8 $ [+3,9 ; +39,6] | **+10,5 $ [−2,3 ; +23,8]** : non démontré |
| Médiane par signal | 0 $ | **−3,6 $** |
| Part du gain due aux 5 meilleurs signaux | 52 % | **59 %** |
| H769 : plafond +1 à +3 c | gain marginal jusqu’à +1 131 $ | **−175 à +211 $** : pas d’effet |
| H774 : relances 5 s au plafond +2 c | meilleure politique (+6 013 $ contre +4 670 $) | **pas mieux** (+4 067 $ contre +4 141 $ pour l'abandon immédiat) |

## Ce qui ne change pas

- **Taker contre maker :** le taker reste meilleur. Maker 60 s : +333 à +479 $, contre +4 141 $ pour le taker.
- **Offres disparues :** elles sont surtout retirées par les vendeurs. Ces signaux-là gagnent davantage (42 %) que ceux dont l'offre reste (28 %).
- **Décision anticipée par Binance :** pas d'avantage. Écart de −0,21 $ par signal, IC [−1,18 ; +0,70].

## Lecture

- L'avantage de Bot95 en taker **s'affaiblit avec plus de données**. Il ne tient plus qu'à 164 ms, de justesse, et repose sur quelques gros gains.
- Les relances (base de R4) **n'ajoutent plus rien** hors ligne.
- Le verdict reste à faire sur R4 en direct et sur la période réservée du 13.10.
