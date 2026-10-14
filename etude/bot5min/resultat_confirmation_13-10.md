# Bot95 — Confirmation du 13.10.2026 (période réservée, jamais regardée avant), une seule fois

Lancé le 14.10.2026 00:50–01:15 UTC, 279 cycles BTC du 13.10 (enregistrés à Dublin), règles figées avant. Aucun ordre réel.

| Étude (règle) | Entrées | P&L 10 $ | ROI | IC 90 % | Verdict |
|---|---|---|---|---|---|
| H1058 JC5 (saut perp 5 $ + couverture preneur) | 515 | +270 $ | +5,4 % | [−12 ; +544] | pas démontré (positif) |
| H1058 JC10 (saut 10 $) | 84 | +92 $ | +11,4 % | [+2 ; +185] | positif, IC > 0 |
| H1058 garder seul (G5) | 515 | +224 $ | +4,5 % | [−167 ; +608] | témoin |
| H1059 CP5 (couverture posée) | 515 | +202 $ | +4,0 % | [−77 ; +484] | pas démontré |
| H1059 CP10 | 84 | +73 $ | +9,1 % | [−28 ; +174] | pas démontré |
| H1060 FG150 (contre les gros) | 306 | −197 $ | −6,5 % | [−597 ; +211] | non |
| H1060 FG300 | 94 | −241 $ | −25,7 % | [−473 ; −32] | **négatif** |
| H1062 SA10 / SA10-5 / SAsig (petit à petit) | 472 / 513 / 507 | +92 / +150 / +97 $ | +1,9 / +4,3 / +3,3 % | contiennent 0 | pas démontré |
| H1063 bis PS / PI / PSI (perp seul, Poly immobile) | 332 / 163 / 116 | +22 / +32 / +1 $ | ≈ 0 % | contiennent 0 | non (règles vues après coup, erreur de signe) |
| H1068 BY1 Bybit premier 10 $ | 451 | −14 $ | −0,3 % | [−331 ; +297] | **non** |
| H1068 BY1 100 $ | 268 | −2 840 $ | −11,3 % | [−5 055 ; −586] | **négatif** |
| H1069 BY1 + contre l'élan + calme 10 $ / 100 $ | 126 / 72 | −25 / −1 079 $ | −2,0 / −15,7 % | contiennent 0 | non (choisie en regardant les 3 périodes) |
| H1065 bis T1 billets, Poly du favori en baisse 5 s | 49 gardés | — | −9 % contre +59 % écartés | [−191 ; +57] pts | non |
| **H1065 bis T2 billets, perp contre le favori 30 s** | **77 gardés** | — | **+178 % contre −48 %** | **[+58 ; +425] pts** | **confirmé** |
| H1065 bis T3 billets, carnet Binance contre le favori | 84 gardés | — | +86 % contre +8 % | [−71 ; +261] pts | non |
| Piste H1066 fenêtres :00 / :30 (favori 0,65–0,95) | 128 instants | — | +0,6 pt contre −0,5 pt | — | rien |

## Fantômes en direct (sauvegarde du 14.10 00:48 UTC)

CP10 +85 $ (138) ; JC5 −12 $ (232) ; CP5 −75 $ (232) ; billet + favori −504 $ (201) ; FG150 +79 $ (48) ; FG300 −1 $ (12) ;
petit à petit −1 / +13 / −9 $ (93–110) ; PB seul +10 $ (53) ; PB + Poly immobile +46 $ (23) ; BY1 10 $ +119 $ (52) ; BY1 100 $ +537 $ (25) ;
BY1 contre-élan calme +12 $ (2) ; BY1 pression contre +36 $ (10) ; billet élan retourné −28 $ (26) ; E1 +28 $ (27) ; E2 −107 $ (30) ; E3 +27 $ (14) ;
E4 −70 $ (7) ; consensus K2 +828 $ (145) ; K5 −380 $ (87) ; K5 anti-bête −321 $ (34) ; K9 +62 $ (14).
Règlement des PB réparé : tous réglés. Les 16 stratégies arrêtées n'ont rien ouvert après leur arrêt ; K2 / K5 / K9 tournent.

Filtres sur les stratégies du bot, comparés aux originaux sur la même période (quelques heures seulement) :
écart serré +349 $ contre −706 $ ; carnet + écart serré +594 $ contre +367 $ ; écart + carnet + calme +175 $ contre +378 $ ;
carnet −585 $ contre +1 598 $ ; carnet pression −1 823 $ contre −1 523 $ ; contre la foule −2 433 $ contre −125 $ ; foule + Bybit −170 $ contre +2 911 $.

## Lecture

- La famille « saut du perp » reste légèrement positive (+4 à +11 %) sans être démontrée ; les raffinements de la soirée (Bybit premier,
  combinaison, Poly immobile) ne tiennent PAS sur la journée propre : c'était du sur-ajustement.
- « Contre les gros ≥ 300 $ » est négatif : à arrêter (proposition).
- Une seule règle confirmée : billet seulement quand le perp va contre le favori sur 30 s (T2).
