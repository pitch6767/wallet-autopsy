# Bot95 — Structure du gain (moyenne > 0, médiane < 0)

480 signaux réglés, 107 cycles ; 144 décisions uniques.

5 meilleurs signaux : +2326 $ sur +3915 $ ; ils viennent de 3 cycles seulement.

| Échantillon | Prix | Signaux | Cycles | Taux de gain | Prix moyen | Gain − prix (points) | IC 90 % | Modèle |
|---|---|---|---|---|---|---|---|---|
| tous | 0.0–0.1 | 55 | 39 | 15 % | 6 % | +8.2 | [-1.2 ; +18.7] | 33 % |
| tous | 0.1–0.2 | 145 | 79 | 25 % | 15 % | +9.6 | [+0.0 ; +19.4] | 41 % |
| tous | 0.2–0.3 | 197 | 81 | 37 % | 24 % | +12.4 | [+3.0 ; +21.6] | 47 % |
| tous | 0.3–0.5 | 62 | 29 | 56 % | 36 % | +20.2 | [+5.2 ; +36.3] | 58 % |
| tous | 0.0–0.5 | 459 | 106 | 33 % | 21 % | +12.1 | [+5.4 ; +18.7] | 45 % |
| décisions uniques | 0.0–0.1 | 4 | 4 | 0 % | 6 % | -6.0 | [-8.0 ; -3.5] | 26 % |
| décisions uniques | 0.1–0.2 | 27 | 26 | 15 % | 15 % | -0.4 | [-11.0 ; +10.7] | 38 % |
| décisions uniques | 0.2–0.3 | 80 | 74 | 34 % | 24 % | +9.5 | [+1.5 ; +17.6] | 46 % |
| décisions uniques | 0.3–0.5 | 21 | 20 | 62 % | 38 % | +23.5 | [+7.7 ; +38.5] | 60 % |
| décisions uniques | 0.0–0.5 | 132 | 106 | 33 % | 24 % | +9.2 | [+4.1 ; +14.3] | 46 % |

Offres retirées avant 250 ms (décisions uniques) : 43, gain 49 % au prix 34 % ; restées : 101, gain 31 % au prix 24 %. Écart (gain − prix) retirées − restées : +8.8 points [-4.3 ; +22.7]. Début de retrait médian 53 ms, disparition médiane 135 ms.

| Connu à la décision | Part retirée : oui / non | Gain − prix : oui / non |
|---|---|---|
| déclenché par le carnet Polymarket | 13 % / 60 % | +5.6 / +14.6 |
| profondeur au signal < 50 parts | 22 % / 41 % | +1.8 / +19.3 |
| écart modèle − prix ≥ 0,25 | 58 % / 27 % | +3.2 / +9.4 |