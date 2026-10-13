# Bot95 — H1075 : cycle calme et « contre la foule » (stratégies du bot)

13.10.2026 soir, mêmes 7 442 trades BTC qu'en H1070, mesures Dublin à l'instant d'achat. Balayage de 19 mesures ; exploration (3 périodes regardées).

| Filtre (gardés / écartés) | Apprentissage | Validation | Test |
|---|---|---|---|
| Cycle calme : ≤ 2 passages du prix Up par 0,5 depuis le début | +15 % / −8 % | +335 % / −70 % | +40 % / −20 % |
| Contre la foule : flux des preneurs Polymarket 30 s pas pour nous | +21 % / −14 % | +248 % / −61 % | +21 % / −2 % |
| Écart ≤ 1 c + carnet pour nous + cycle calme | +44 % / −6 % | +654 % / +8 % | +91 % / −18 % (IC > 0) |

Aussi cohérents sur les 3 périodes (sans fantôme) : prix Polymarket qui vient de monter pour nous (5 s), perp qui vient d'aller pour nous (5 s),
profondeur acheteuse de notre côté ; acheter le favori fait moins bien qu'acheter l'autre côté.
Fantômes « + calme », « + contre foule », « + ecart carnet calme » en ligne. Aucun ordre réel. Multiplication des filtres : prudence.
