Bonjour, je suis un ancien trader d'options (conversions/reversals sur futures DAX à Eurex). Je construis un bot sur Polymarket et je cherche des idées neuves. Voici tout ce qui a été fait et testé.

## 1. Le marché
- Marchés Polymarket « Bitcoin Up or Down » de 5 minutes (aussi ETH, SOL, XRP, DOGE, BNB, HYPE), un nouveau toutes les 5 minutes, jetons Up et Down entre 0 et 1 $.
- Règle de résolution : moyenne Chainlink des 60 dernières secondes du cycle ≥ moyenne Chainlink des 60 secondes avant le début (le « price to beat ») → Up gagne.
- Frais taker : 0,072 × p × (1 − p) par part (environ 1,8 ¢ à 0,55). Frais maker : 0. Up + Down peuvent être fusionnés contre 1 $.
- Le prix de départ affiché en direct par Polymarket peut différer de l'officiel d'environ 0,08 %.

## 2. L'infrastructure
- Bot sur Cloudflare (Durable Object à Amsterdam). Messages Polymarket reçus en ~0,05 s, aller-retour vers le carnet d'ordres ~22 ms, réaction totale ~0,1 s.
- Prix rapide : perp Bybit (et OKX en secours), recalé sur le niveau Chainlink. Mesure du jour : Bybit perp est la source la plus rapide reçue à Amsterdam. Binance spot arrive ~200 ms après, Binance perp refuse Cloudflare, Coinbase est à égalité.
- Modèle : probabilité que la moyenne finale dépasse le prix de départ (partie déjà connue de la moyenne + prix rapide actuel, écart-type tiré de la volatilité à 1 s, plus une incertitude de mesure).
- Capital 250 $, mise 50 $ par trade. Pour l'instant en mode fantôme (pas d'argent réel).

## 3. Stratégie A — acheter le favori en toute fin de cycle
- Achat du favori entre 0,85 et 0,999 dans les 30 à 120 dernières secondes, seulement si le modèle est très sûr.
- En fantôme : 14 gagnés, 1 perdu (−43 $ sur SOL) en ~9 h. Peu de trades.

## 4. Stratégie V1 — la principale
Règles :
- Acheter la jambe qui atteint 0,55–0,56 (taker), seulement si le modèle donne ≥ 0,63 (0,55 + marge 0,08) ET si le prix rapide a monté dans notre sens sur les 5 dernières secondes.
- Poser en même temps une offre d'achat maker sur le côté opposé, au prix de sa valeur moins 0,08 (au maximum 0,43). Si elle est servie en totalité → paire fusionnée, gain bloqué.
- Stop : si la probabilité du modèle baisse de 15 points depuis l'entrée → vente.
- Sortie : vente à 0,90 si on tient une seule jambe.
- Une seule entrée par cycle.

Résultats simulés sur 12 jours (23.09 → 04.10.2026), 100 parts par trade (~55 $), retard 1 s, remplissages prudents :

| Crypto | Gain par jour |
|---|---|
| BTC | +1 486 $ (≈122 trades/jour) |
| ETH | +491 $ |
| SOL | +300 $ |
| XRP | +187 $ |
| BNB | +68 $ |
| DOGE | +58 $ |
| HYPE | +2 $ |

Détail BTC sur 12 jours (1 516 trades, +18 090 $) :
- Stops : 699 trades, −5 521 $
- Sorties à 0,90 : 640 trades, +20 471 $
- Paires fusionnées : 147 trades, +2 430 $
- Fins perdues : 4 trades, −230 $
- 39 % des trades stoppés auraient fini gagnants si on les avait gardés.
ETH : 633 trades, +6 520 $, dont 323 stops pour −2 723 $.

## 5. Ce qui a été testé et qui NE marche PAS
- Paires fixes (acheter à 0,55 puis offre à 0,40–0,48 de l'autre côté sans modèle) : perd. Sélection adverse : la jambe seule qu'on garde est presque toujours la perdante.
- Arbitrage marché 15 min contre trois marchés 5 min : les moments sans risque existent (5–9 % des cycles) mais ~5 parts disponibles à chaque fois, moins de 10 $/jour.
- Filtres d'entrée (30+ signaux : flux perp et spot, volume, nombre d'échanges, vitesse du passage à 0,55, moment du cycle, autre crypto, etc., plus un modèle combiné GradientBoosting) : aucun n'améliore le gain net sur des jours jamais vus. Ils coupent les pertes mais coupent plus de gains.
- 21 façons de sortir :
  - Aucun stop : pertes doublées, gain −18 % (BTC) et −50 % (ETH).
  - Stops plus larges (−20 à −30 pts) : gains plus faibles.
  - Stop confirmé sur 3 à 5 s, ou seulement si le perp vend, ou pas de stop pendant 10–20 s : tous moins bons.
  - Stop sur le prix (0,40 ou 0,35) : très mauvais (gain divisé par 2).
  - Entrer seulement après 30 ou 60 s de cycle : pertes −27 %, mais gain −12 %.
  - Sortie à 0,95 au lieu de 0,90 : gain +10 %, mais la pire baisse double sur BTC.
- 32 variantes « anti-pertes » (seuils choisis sur 8 jours, vérifiés sur 4 jours jamais vus) :
  - Écart perp-spot anormal comme filtre d'entrée : moins bon.
  - Très gros ordres sur le perp Binance contre nous, comme filtre : moins bon. Comme sortie : ETH un peu mieux (pertes −22 %, gain égal), BTC pertes −38 % mais gain −9 %.
  - Régime de marché (ratio de variance 30 min / 1 h, tendance contre allers-retours) : nettement moins bon.
  - Vendre une partie à 0,70/0,75 ou stop suiveur : moins bon (55 % des trades stoppés étaient pourtant montés à 0,70 avant).
  - Achats agressifs du côté opposé sur Polymarket : très mauvais sur BTC, neutre sur ETH.
- Seule chose retenue : mise 0,5× si l'avance du modèle est sous la médiane, 1,5× sinon. Gain +14 %, mais les pertes ne baissent pas.

## 6. En cours
Le bot enregistre en direct, à chaque trade, ce qui n'a pas d'historique : liquidations, retraits d'ordres des teneurs de marché sur Polymarket, profondeur des carnets des deux côtés, recul du meilleur prix d'achat. Analyse dans quelques jours.

## 7. Pistes pas encore testées
- Valeur relative entre cryptos : acheter BTC Up + ETH Down (ou d'autres couples) quand l'ensemble coûte moins que sa valeur. On ne perd que si les deux divergent.
- Polymarket contre Kalshi/Limitless sur les mêmes marchés crypto courts (sources de prix différentes).
- Teneur de marché des deux côtés au prix du modèle, avec retrait des offres en 0,1 s, puis fusion des paires.
- Acheter à 0,70–0,85 dans les 90 dernières secondes quand le modèle donne ≥ 0,95.

## 8. Ma question
Je veux réduire les pertes SANS réduire le gain. Le stop ne me plaît pas : quand il se déclenche, le côté opposé est déjà parti et la perte est faite. Quelles idées vraiment différentes as-tu, pour détecter les mauvais trades à l'avance, construire une structure à perte limitée, ou trouver un autre avantage sur ces marchés 5 minutes ? Sois concret et dis comment chaque idée pourrait se tester.
