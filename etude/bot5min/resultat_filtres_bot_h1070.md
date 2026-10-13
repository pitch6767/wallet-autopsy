# Bot95 — H1070 : les trouvailles du 13.10 appliquées aux stratégies du bot

13.10.2026 (Pitch 21:35). 7 442 trades BTC de 53 stratégies (sauvegarde), achetés entre 11.10 08:05 et 12.10 24:00, joints au carnet Dublin
de la seconde précédant l'achat. Exploration (les trois périodes regardées : aucune valeur de preuve). Aucun ordre.

| Filtre (à l'achat) | Apprentissage gardés / écartés | Validation | Test | Écart, IC 90 % par cycles |
|---|---|---|---|---|
| **Carnet Polymarket de notre côté** (plus d'acheteurs que de vendeurs sur 5 niveaux) | +24 % (+12 502 $) / −9 % (−7 267 $) | +240 % / +34 % | +44 % (+17 784 $) / −29 % (−10 179 $) | A [+2 ; +63] pts, T [+35 ; +116] pts |
| Élan du perp 30 s pour nous | +18 % / −3 % | +22 % / +124 % | +25 % / 0 % | contient 0 |
| Pas de saut Bybit contre nous dans les 10 s | +6 % / −92 % (106 trades) | — | +11 % / −18 % (100) | A > 0, T contient 0 |
| Marché calme | +8 % / −3 % | −96 % / +192 % | +24 % / −23 % | instable |

Le filtre « carnet de notre côté » va dans le même sens pour chaque famille (V2-B à H, désaccord 20/30, TWAP fin, consensus, corrigé) et
pour chaque tranche de prix sous 0,40 (billets ≤ 0,20 : −40 % / −37 % écartés contre +38 % / +46 % gardés).
Fantômes « <stratégie> + carnet » ajoutés (copie du trade d'origine quand le carnet penche de notre côté à l'achat) : la seule preuve
sera la suite, en direct.
