# Bot95 — H1063 : le perp premier à bouger

Généré le 13.10.2026 18:00 UTC. 10 $ par saut, preneur 164 ms, gardé jusqu'au règlement. Aucun ordre.

| Règle | Période | Sauts | Gagnants | P&L ($) | ROI | IC 90 % corrigé (2 règles) |
|---|---|---|---|---|---|---|
| PB1 | apprentissage | 93 | 62 | +170 | +18.2 % | [+2 ; +334] |
| PB1 | validation | 61 | 40 | +113 | +18.7 % | [-28 ; +263] |
| PB1 | test | 208 | 123 | +145 | +7.0 % | [-162 ; +446] |
| PB2 | apprentissage | 68 | 45 | +135 | +19.9 % | [-16 ; +291] |
| PB2 | validation | 44 | 31 | +112 | +25.6 % | [+0 ; +224] |
| PB2 | test | 132 | 81 | +126 | +9.5 % | [-115 ; +365] |
| témoin (tous) | apprentissage | 153 | 96 | +152 | +9.9 % | [-49 ; +354] |
| témoin (tous) | validation | 100 | 64 | +147 | +14.8 % | [-19 ; +301] |
| témoin (tous) | test | 299 | 173 | +173 | +5.8 % | [-144 ; +489] |

**Verdict (critère figé)**

- PB1 : abandon
- PB2 : abandon

## Correction (13.10.2026 20:20)

Erreur de signe : `poly1s` était signé deux fois. Pour les sauts vers le bas, PB1/PB2 ne testaient donc PAS « Polymarket pas contre nous ».
Le verdict ci-dessus (abandon) reste valable pour les règles telles que calculées. Règles corrigées, regardées après coup (NON pré-enregistrées) :

| Règle (signe juste) | Apprentissage | Validation | Test |
|---|---|---|---|
| perp seul (nconf = 0) | 105 sauts, +15,3 % | 73, +21,9 % | 182, +10,9 % |
| Polymarket immobile 1 s | 46, +29,7 % | 19, +26,8 % | 99, +19,7 % |
| perp seul + Polymarket immobile | 31, +38,3 % | 17, +30,6 % | 64, +25,3 % |
| tous (témoin) | 153, +9,9 % | 100, +14,8 % | 299, +5,8 % |

Seule preuve propre possible : la période réservée ≥ 13.10, une fois, par `confirmation_h1063.py` (figé avant calcul). Fantômes « PB seul » et
« PB seul + Poly immobile » en ligne à Dublin depuis 13.10 20:15 (accord de Pitch « Go »).
