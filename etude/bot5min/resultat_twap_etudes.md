# TWAP fin — études A à E (BTC, 693 cycles, 07.10 08:05 → 09.10 22:35)

Carnet enregistré 4 fois par seconde ; règlement reconstruit exactement ; probabilités calculées avec seulement ce qui était reçu à l'instant. Achats simulés au meilleur vendeur, limités à la quantité affichée, frais compris.

## A. Combien de temps l'avantage reste achetable après le signal (moteur actuel, premier signal de chaque cycle)

140 signaux.

| Délai d'achat | Encore achetable | Avantage moyen restant | Avantage ≥ 0,20 encore | ≥ 0,10 encore | Prix moyen | Quantité moyenne affichée | Résultat si on achète à ce moment |
|---|---|---|---|---|---|---|---|
| 0 s | 140 / 140 | +0.261 | 140 | 140 | 0.251 | 62 jetons | +2'323 $ |
| 0.25 s | 140 / 140 | +0.178 | 72 | 112 | 0.336 | 88 jetons | +2'845 $ |
| 0.5 s | 140 / 140 | +0.153 | 53 | 98 | 0.358 | 129 jetons | +2'486 $ |
| 1 s | 140 / 140 | +0.132 | 41 | 88 | 0.379 | 174 jetons | +731 $ |
| 2 s | 138 / 140 | +0.122 | 38 | 84 | 0.376 | 220 jetons | +1'633 $ |
| 5 s | 137 / 140 | +0.095 | 20 | 72 | 0.388 | 202 jetons | +853 $ |

Lecture : si l'avantage disparaît en moins d'une seconde, seule une exécution très rapide en profitera.

## B. L'écart Binance − perp : quelle partie annonce vraiment l'erreur de la moyenne finale ?

35167 mesures (une par seconde, 90-20 s avant la fin). Corrélation avec l'erreur réelle de la moyenne finale (officiel − prévu), apprentissage avant le 08.10 20:30, test après.

| Mesure | Corrélation (apprentissage) | Corrélation (test, jamais vu) |
|---|---|---|
| écart Binance − perp (niveau) | +0.134 | +0.128 |
| écart Coinbase − perp | +0.107 | +0.079 |
| partie NOUVELLE de l'écart (non expliquée par l'écart d'il y a 5 s et le mouvement) | +0.063 | +0.082 |
| saut de l'écart par rapport à sa médiane de la minute | -0.015 | +0.049 |
| écart d'il y a 5 s | +0.121 | +0.107 |

| Taille de l'écart (sans le prorata) | Mesures | Pente $ d'erreur par $ d'écart (test) |
|---|---|---|
| 0-2 $ | 3883 | +1.38 |
| 2-10 $ | 9026 | +0.35 |
| 10-30 $ | 1275 | +0.39 |
| écart qui dure > 5 s | 9818 | +0.45 |
| écart récent (≤ 5 s) | 4367 | +0.14 |

Idée 30 — le **sens** de l'écart annonce le sens de l'erreur dans **61.9 %** des cas (test, écart > 0,5 $) ; 50 % = hasard.

## C. Les trois modèles TWAP fin sur les mêmes cycles (rejeu, un achat par cycle)

| Groupe de cycles | Cycles | Résultat original | Résultat sauts | Résultat correction |
|---|---|---|---|---|
| aucun achat | 543 | — | — | — |
| les trois | 75 | +1'658 $ (75) | +1'393 $ (75) | +1'132 $ (75) |
| deux : original + sauts | 28 | +38 $ (28) | +59 $ (28) | — |
| seul : original | 18 | −233 $ (18) | — | — |
| côtés opposés | 17 | +874 $ (17) | +346 $ (17) | +36 $ (16) |
| seul : sauts | 6 | — | +173 $ (6) | — |
| seul : correction spot-perp | 4 | — | — | −103 $ (4) |
| deux : original + correction spot-perp | 2 | −13 $ (2) | — | −57 $ (2) |

| Modèle | Achats | Gagnés | Résultat | Par $ | Creux | Pertes de suite max |
|---|---|---|---|---|---|---|
| original | 140 | 46 % | **+2'323 $** | +82 % | −160 $ | 5 |
| sauts | 126 | 51 % | **+1'971 $** | +69 % | −256 $ | 4 |
| correction spot-perp | 97 | 42 % | **+1'009 $** | +42 % | −447 $ | 5 |

Quand au moins deux modèles achètent le même côté, celui qui déclenche en premier : original 90 fois, sauts 8 fois, correction spot-perp 7 fois.
- original avant sauts : 0.0 s d'avance en médiane (89 cycles)
- original avant correction spot-perp : 0.0 s d'avance en médiane (66 cycles)
- sauts avant original : 0.6 s d'avance en médiane (8 cycles)
- sauts avant correction spot-perp : 4.6 s d'avance en médiane (4 cycles)
- correction spot-perp avant original : 14.7 s d'avance en médiane (7 cycles)
- correction spot-perp avant sauts : 18.3 s d'avance en médiane (6 cycles)
- Attendre la 2e confirmation coûte en médiane +0.0 c (moyenne +0.3 c) sur 105 cycles.

## D. Changements de favori (moteur actuel) : qui bascule en premier, notre modèle ou le carnet ?

| Groupe | Achats | Gagnés | Résultat | Par $ | Creux | Pertes de suite max |
|---|---|---|---|---|---|---|
| pas de changement de favori dans le cycle | 81 | 33 % | **+721 $** | +44 % | −217 $ | 9 |
| changement il y a < 3 s | 37 | 73 % | **+816 $** | +115 % | −71 $ | 2 |
| il y a 3-10 s | 7 | 57 % | **+62 $** | +25 % | −106 $ | 2 |
| il y a 10-30 s | 8 | 38 % | **+145 $** | +147 % | −56 $ | 3 |
| il y a > 30 s | 7 | 43 % | **+579 $** | +426 % | −32 $ | 3 |
| notre modèle a basculé AVANT le carnet | 8 | 75 % | **+64 $** | +32 % | −53 $ | 1 |
| le carnet a basculé avant notre modèle | 27 | 44 % | **+524 $** | +89 % | −121 $ | 5 |
| notre modèle a basculé, le carnet jamais | 24 | 79 % | **+1'015 $** | +255 % | −71 $ | 2 |
| ≥ 3 bascules en 30 s (oscillations) | 12 | 67 % | **+394 $** | +128 % | −53 $ | 2 |
| 0-2 bascules en 30 s | 128 | 44 % | **+1'929 $** | +76 % | −236 $ | 5 |

## E. Le prochain prix Chainlink après le signal confirme-t-il notre avantage ?

| Groupe | Achats | Gagnés | Résultat | Par $ | Creux | Pertes de suite max |
|---|---|---|---|---|---|---|
| le prix Chainlink suivant va dans notre sens | 82 | 41 % | **+1'707 $** | +105 % | −181 $ | 5 |
| délai jusqu'au prochain prix Chainlink < 2 s | 134 | 46 % | **+2'139 $** | +80 % | −156 $ | 5 |
| le prix Chainlink suivant va contre nous | 58 | 52 % | **+616 $** | +51 % | −176 $ | 6 |
| délai ≥ 2 s | 6 | 50 % | **+184 $** | +119 % | −53 $ | 1 |
| *politique : attendre le prochain prix Chainlink, acheter si l'avantage est encore ≥ 0,20* | 53 | 36 % | **+1'661 $** | +112 % | −177 $ | 5 |