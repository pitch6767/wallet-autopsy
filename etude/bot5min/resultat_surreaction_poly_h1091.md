# Bot95 — H1091 « surréaction de Polymarket » (BTC 5 min)

*Étude hors ligne du 14.10.2026. Aucun ordre, aucun bot ni fantôme modifié. Script : `etude/bot5min/surreaction_poly_h1091.py`. Règles figées et poussées avant la validation : commit da81ed03.*

## Verdict

**Ni retour net, ni suite exploitable. Quand le carnet Up bouge fort en quelques secondes sans que le BTC bouge, il ne revient presque pas : c'est surtout le BTC qui le rattrape ensuite. Le carnet est au bon prix au moment du mouvement. Aucune règle ne gagne de façon démontrée.**

- **Le milieu du carnet revient à peine.** Après un mouvement de 8 c en 5 s, BTC calme : en exploration, il rend environ 1 c à +10/+30 s. En validation, rien de mesurable (+0,8 c à +30 s, −1,7 c à +60 s ; les intervalles contiennent 0). La pente « mouvement futur / mouvement en trop » est de −0,01 à −0,12 : au mieux, un dixième du mouvement revient en 30 à 60 s.
- **C'est le modèle qui rattrape le carnet.** Dans les 30 s qui suivent, la moitié environ du « mouvement en trop » disparaît, parce que la probabilité calculée à partir du BTC bouge à son tour dans le même sens (pente du résidu ≈ −0,45, sur les deux périodes). Le carnet avait donc une information que Coinbase/Chainlink ne montraient pas encore.
- **Au règlement, le carnet avait raison, le modèle non.** Gagnant − milieu au moment du signal ≈ 0 (de −1,5 à +1 point, intervalles contenant 0 quand le BTC est calme). Gagnant − modèle ≈ +6 à +11 points, très nettement positif. Acheter contre le mouvement ou avec lui revient donc à payer l'écart et les frais sur un prix juste.
- **Validation des 3 règles figées** (13.10 + 14.10, 428 cycles, lue une seule fois) :
  - R1 « revenir » 10–150 s : 197 achats, +139 $, ROI +7,4 %, IC corrigé [−240 ; +531] $ → **non démontré** (les deux jours positifs, mais +20 $ seulement le 14.10).
  - R2 « revenir » 240–285 s : 38 achats, +22 $, ROI +6,9 %, IC corrigé [−125 ; +190] $ → **non démontré**.
  - R3 « suivre » 150–240 s : 176 achats, −365 $, ROI −22,1 %, IC corrigé [−606 ; −123] $ → **perd de façon démontrée**. Courir après un mouvement du carnet coûte cher.
- **Aucun fantôme proposé** (aucun IC corrigé au-dessus de 0).

## L'idée

Le carnet Polymarket Up bouge parfois de 5 à 15 c en quelques secondes. Si le BTC n'a pas bougé autant, deux lectures sont possibles :
1. **surréaction** : du flux d'ordres pur (un gros acheteur, un bot qui balaie) ; le prix revient ensuite → acheter le côté poussé vers le bas ;
2. **information** : quelqu'un voit quelque chose que les bourses ne montrent pas encore ; le BTC suit ensuite → suivre.

## Méthode

- **Données** : enregistreur de Dublin (branche donnees-rapide), cycles BTC 5 min du 11.10 au 14.10 16 h 30 UTC. Photo du carnet Up/Down chaque seconde (meilleurs prix et tailles), Coinbase et Binance (toutes les 50 ms), Chainlink. 933 cycles enregistrés, 833 utilisables.
- **Gagnant** = bot95/officiels.json, sinon prix à battre du cycle suivant (les deux concordent sur 709/709 cycles communs).
- **Modèle de règlement** (celui de H1090, k = 1,8 figé sur 11–12.10, étendu à tout le cycle) : le règlement compare la moyenne Chainlink des secondes 240–299 au prix à battre K. Avant 240 s : P(Up) = Φ((S − K) / (σ·1,8·√(240 − t + 20,5))). Après 240 s, la partie déjà connue de la moyenne est prise en compte. S = Coinbase reçu moins l'écart médian Coinbase − Chainlink du cycle précédent (le prix BTC le plus frais ; Chainlink arrive avec ~1,7 s de retard). σ = volatilité Chainlink 1 s du cycle précédent.
- **Résidu** (« mouvement en trop ») sur w = 3, 5 ou 10 s : r = Δ milieu du carnet Up − Δ probabilité du modèle. Mesuré chaque seconde de 10 à 270 s, quand l'écart acheteur-vendeur est ≤ 3 c et que le milieu est entre 0,05 et 0,95. « BTC calme » = le modèle a bougé de 2 points au plus sur la même fenêtre.
- **Suite** : Δ milieu à +10, +30, +60 s, Δ résidu aux mêmes horizons, et gagnant final comparé au milieu (et au modèle) au moment du signal. Signe ramené au sens du mouvement : **négatif = revient, positif = continue**. Unité : points de probabilité (1 point = 1 c).
- **Découpage chronologique** : exploration = 11.10 + 12.10 (405 cycles utilisables) ; validation = 13.10 + 14.10 (428). Le 13.10, jour réservé, n'a été lu qu'une fois, après le gel.
- **Achat simulé** : décision sur la photo t, achat au meilleur vendeur de la photo suivante (≈ t + 1 s), limité à la taille affichée, 10 $ maximum, frais 0,07·p·(1−p) par part, gardé jusqu'au règlement, un achat par cycle et par règle.
- **Statistiques** : IC 90 % par bootstrap sur les cycles (2 000 tirages pour les tableaux, 10 000 pour les règles ; tous les cycles de la période comptés, 0 $ sans achat). Bonferroni pour 3 règles : percentiles 1,67 / 98,33.
- **Balayage d'exploration** : 720 combinaisons (fenêtre, seuil, filtre BTC calme, sens, moment du cycle, plage de prix). 170 sur 638 (avec ≥ 40 achats) positives. « Revenir » fait mieux que « suivre » ; « suivre » perd presque partout, sauf un îlot à 150–240 s.

## Résultats

### Tableau A — pente du mouvement futur du milieu sur le résidu (toutes les secondes, IC 90 %)

Négatif = le milieu revient ; 0 = il ne revient pas. La dernière colonne montre que le résidu, lui, se résorbe à moitié : c'est le modèle (le BTC) qui rejoint le carnet.

| Période | Fenêtre | Pente +10 s | Pente +30 s | Pente +60 s | Pente du résidu +30 s |
|---|---|---|---|---|---|
| exploration | 3 s | −0,009 [−0,021 ; +0,001] | −0,017 [−0,035 ; −0,002] | −0,028 [−0,047 ; −0,011] | −0,481 [−0,493 ; −0,469] |
| exploration | 5 s | −0,007 [−0,021 ; +0,008] | −0,021 [−0,042 ; −0,002] | −0,028 [−0,050 ; −0,005] | −0,459 [−0,475 ; −0,442] |
| exploration | 10 s | −0,008 [−0,028 ; +0,010] | −0,017 [−0,044 ; +0,009] | −0,020 [−0,052 ; +0,012] | −0,434 [−0,450 ; −0,417] |
| validation | 3 s | −0,006 [−0,027 ; +0,012] | −0,025 [−0,047 ; −0,001] | −0,043 [−0,072 ; −0,019] | −0,468 [−0,480 ; −0,457] |
| validation | 5 s | −0,002 [−0,022 ; +0,018] | −0,034 [−0,064 ; −0,003] | −0,058 [−0,094 ; −0,026] | −0,462 [−0,476 ; −0,448] |
| validation | 10 s | +0,001 [−0,027 ; +0,029] | −0,079 [−0,115 ; −0,036] | −0,117 [−0,169 ; −0,065] | −0,443 [−0,458 ; −0,427] |

### Tableau B — suite des mouvements du carnet sans mouvement du BTC (signe ramené au sens du mouvement, en points, IC 90 %)

Exemple de lecture : « validation, 5 s, ≥ 0,08, BTC calme » = le milieu a monté (ou baissé) d'au moins 8 c de plus que le modèle en 5 s, le modèle ayant bougé de 2 points au plus : 1 439 secondes dans 317 cycles. 30 s plus tard le milieu a encore avancé de 0,8 point (non significatif). Le résidu s'est résorbé de 6,4 points (le BTC a suivi). Au règlement, le carnet au moment du signal était juste (−0,0) et le modèle se trompait de 9 points.

| Période | Fenêtre | Seuil résidu | BTC calme | Cas (s) | Cycles | Suite du milieu +10 s | +30 s | +60 s | Suite du résidu +30 s | Gagnant − milieu | Gagnant − modèle |
|---|---|---|---|---|---|---|---|---|---|---|---|
| exploration | 3 s | ≥ 0,08 | non | 7773 | 383 | −0,3 [−0,6 ; −0,1] | −0,6 [−1,0 ; −0,3] | −0,7 [−1,1 ; −0,3] | −7,2 [−7,7 ; −6,7] | −0,5 [−1,1 ; +0,0] | +7,6 [+6,8 ; +8,4] |
| exploration | 3 s | ≥ 0,08 | oui | 1607 | 316 | −0,5 [−1,2 ; +0,1] | −1,8 [−2,9 ; −0,7] | −1,2 [−2,6 ; +0,3] | −7,7 [−8,3 ; −7,1] | −1,3 [−3,3 ; +0,6] | +8,3 [+6,3 ; +10,2] |
| exploration | 5 s | ≥ 0,05 | non | 19027 | 400 | −0,1 [−0,4 ; +0,1] | −0,1 [−0,3 ; +0,2] | −0,2 [−0,5 ; +0,2] | −4,6 [−5,0 ; −4,3] | +0,1 [−0,3 ; +0,6] | +6,2 [+5,6 ; +6,7] |
| exploration | 5 s | ≥ 0,05 | oui | 5434 | 385 | −0,5 [−0,8 ; −0,1] | −0,3 [−1,0 ; +0,3] | −0,2 [−1,0 ; +0,6] | −4,6 [−5,0 ; −4,3] | −0,4 [−1,9 ; +1,1] | +6,2 [+4,5 ; +7,8] |
| exploration | 5 s | ≥ 0,08 | non | 9556 | 385 | −0,3 [−0,6 ; −0,0] | −0,5 [−0,9 ; −0,1] | −0,5 [−0,9 ; +0,0] | −6,9 [−7,4 ; −6,4] | −0,2 [−0,8 ; +0,5] | +8,2 [+7,4 ; +9,0] |
| exploration | 5 s | ≥ 0,08 | oui | 1901 | 325 | −0,9 [−1,5 ; −0,2] | −1,4 [−2,7 ; −0,2] | −1,1 [−2,6 ; +0,4] | −7,3 [−7,9 ; −6,6] | −0,7 [−2,7 ; +1,5] | +8,8 [+6,6 ; +11,0] |
| exploration | 5 s | ≥ 0,12 | non | 4602 | 336 | −0,2 [−0,6 ; +0,2] | −0,6 [−1,2 ; +0,0] | −0,5 [−1,2 ; +0,2] | −9,4 [−10,4 ; −8,6] | +0,1 [−0,8 ; +0,9] | +11,4 [+10,4 ; +12,5] |
| exploration | 5 s | ≥ 0,12 | oui | 574 | 195 | −1,1 [−2,3 ; +0,2] | −1,9 [−4,7 ; +0,8] | −0,5 [−3,7 ; +2,5] | −10,3 [−11,8 ; −8,8] | +0,5 [−3,1 ; +4,0] | +13,5 [+9,9 ; +17,1] |
| exploration | 10 s | ≥ 0,08 | non | 12278 | 394 | −0,2 [−0,6 ; +0,2] | −0,1 [−0,6 ; +0,4] | +0,1 [−0,5 ; +0,7] | −6,1 [−6,6 ; −5,7] | +0,1 [−0,6 ; +0,8] | +8,7 [+7,9 ; +9,5] |
| exploration | 10 s | ≥ 0,08 | oui | 2147 | 329 | −1,1 [−2,0 ; −0,3] | −0,9 [−2,2 ; +0,4] | −0,2 [−1,7 ; +1,2] | −6,3 [−7,0 ; −5,6] | −0,0 [−2,7 ; +2,5] | +9,8 [+7,0 ; +12,6] |
| validation | 3 s | ≥ 0,08 | non | 5515 | 389 | −0,4 [−0,7 ; −0,1] | −0,5 [−0,9 ; −0,0] | −0,5 [−1,0 ; +0,1] | −5,9 [−6,2 ; −5,7] | −1,3 [−2,0 ; −0,6] | +5,6 [+4,8 ; +6,3] |
| validation | 3 s | ≥ 0,08 | oui | 1330 | 307 | −0,0 [−0,8 ; +0,8] | +0,0 [−1,3 ; +1,3] | −0,8 [−2,7 ; +1,1] | −7,4 [−8,0 ; −6,7] | −0,4 [−2,6 ; +2,0] | +8,7 [+6,5 ; +11,0] |
| validation | 5 s | ≥ 0,05 | non | 15243 | 425 | −0,1 [−0,3 ; +0,1] | −0,1 [−0,4 ; +0,3] | −0,4 [−0,8 ; −0,0] | −4,0 [−4,1 ; −3,8] | −0,4 [−0,9 ; +0,1] | +4,6 [+4,1 ; +5,1] |
| validation | 5 s | ≥ 0,05 | oui | 4153 | 406 | +0,1 [−0,4 ; +0,5] | +0,1 [−0,6 ; +0,8] | −0,8 [−1,7 ; +0,1] | −4,5 [−4,8 ; −4,2] | +1,0 [−0,4 ; +2,4] | +7,1 [+5,7 ; +8,4] |
| validation | 5 s | ≥ 0,08 | non | 6649 | 392 | −0,2 [−0,6 ; +0,2] | −0,2 [−0,7 ; +0,3] | −0,6 [−1,3 ; +0,1] | −5,7 [−5,9 ; −5,4] | −0,9 [−1,8 ; −0,1] | +6,1 [+5,3 ; +6,9] |
| validation | 5 s | ≥ 0,08 | oui | 1439 | 317 | −0,1 [−1,0 ; +0,7] | +0,8 [−0,5 ; +2,1] | −1,7 [−3,4 ; +0,2] | −6,4 [−7,0 ; −5,6] | −0,0 [−2,2 ; +2,2] | +9,0 [+6,6 ; +11,3] |
| validation | 5 s | ≥ 0,12 | non | 2620 | 298 | −0,1 [−0,8 ; +0,6] | −1,4 [−2,3 ; −0,4] | −0,8 [−2,1 ; +0,6] | −8,1 [−8,6 ; −7,6] | −1,5 [−2,9 ; −0,2] | +8,2 [+6,8 ; +9,6] |
| validation | 5 s | ≥ 0,12 | oui | 470 | 183 | −0,2 [−1,8 ; +1,5] | −0,6 [−3,3 ; +2,0] | −2,1 [−5,6 ; +1,5] | −8,8 [−10,3 ; −7,3] | −1,4 [−5,1 ; +2,6] | +11,0 [+7,0 ; +15,0] |
| validation | 10 s | ≥ 0,08 | non | 8399 | 404 | −0,1 [−0,4 ; +0,4] | −0,6 [−1,1 ; −0,0] | −0,5 [−1,2 ; +0,3] | −5,5 [−5,7 ; −5,2] | −0,8 [−1,8 ; +0,3] | +6,7 [+5,8 ; +7,7] |
| validation | 10 s | ≥ 0,08 | oui | 1395 | 311 | +0,4 [−0,5 ; +1,2] | +0,6 [−0,9 ; +1,9] | −1,9 [−3,5 ; −0,3] | −5,8 [−6,5 ; −5,2] | −0,2 [−2,7 ; +2,3] | +8,5 [+6,0 ; +11,0] |

### Tableau C — règles figées : validation (13.10 + 14.10, lue une seule fois)

| Règle | Achats | Gagnés | Prix moyen | Proba modèle | Mise | ROI | P&L | IC 90 % | IC corrigé (Bonferroni 3) | 13.10 | 14.10 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| R1 revenir 10–150 s, 5 s, résidu ≥ 0,08, BTC calme (≤ 0,01), prix 0,20–0,80 | 197 | 90 | 0,427 | 0,511 | 1 893 $ | +7,4 % | **+139 $** | [−160 $ ; +438 $] | [−240 $ ; +531 $] | 109 achats, +119 $ | 88 achats, +20 $ |
| R2 revenir 240–285 s, 5 s, résidu ≥ 0,10, BTC calme (≤ 0,03), prix 0,20–0,80 | 38 | 18 | 0,476 | 0,558 | 325 $ | +6,9 % | **+22 $** | [−93 $ ; +146 $] | [−125 $ ; +190 $] | 20 achats, −17 $ | 18 achats, +40 $ |
| R3 suivre 150–240 s, 10 s, résidu ≥ 0,06, BTC calme (≤ 0,01), prix 0,05–0,95 | 176 | 90 | 0,557 | 0,489 | 1 653 $ | −22,1 % | **−365 $** | [−552 $ ; −178 $] | [−606 $ ; −123 $] | 115 achats, −262 $ | 61 achats, −103 $ |

Rappel exploration (11–12.10, mêmes règles) :

- R1 : 228 achats, 113 gagnés, prix 0,447, ROI +8,3 %, +182 $ (IC 90 % [−105 $ ; +472 $])
- R2 : 36 achats, 19 gagnés, prix 0,388, ROI +56,5 %, +174 $ (IC 90 % [+12 $ ; +350 $])
- R3 : 201 achats, 128 gagnés, prix 0,566, ROI +15,4 %, +299 $ (IC 90 % [−5 $ ; +622 $])

## Lecture

- **Taille des mouvements** : en 5 s, le milieu du carnet bouge de plus de 10 c environ une seconde sur dix. Le modèle bouge autant, et les deux ne sont corrélés qu'à 0,54. Les mouvements « sans BTC » au-delà de 8 c concernent environ 1 400 à 1 900 secondes sur 2 jours, dans 3 cycles sur 4.
- **Ce n'est pas de la surréaction au sens trader** : le prix ne revient pas, ou très peu (au plus 1 à 2 c sur un mouvement de 8 à 12 c, et seulement par moments). Ce qui se passe, c'est que le BTC (vu par Coinbase/Chainlink) bouge ensuite dans le sens du carnet. Les participants de Polymarket voient donc le BTC plus tôt que notre modèle : Binance ou le perpétuel en avance, ou des gros ordres sur les bourses.
- **Pas d'avantage au règlement** : le milieu au moment du signal prédit le gagnant sans biais. Acheter le côté poussé vers le bas (R1, R2) achète un prix juste, plus l'écart et les frais. Les gains de R1 (+139 $) restent dans le bruit.
- **Suivre est le pire choix** : au moment où l'on détecte le mouvement et où l'on achète une seconde plus tard, le prix a déjà intégré l'information. R3 paie en plus le haut de l'écart et perd 22 %. L'îlot positif de l'exploration était du hasard (sélection parmi 720 combinaisons).
- **Mouvements les plus forts sans filtre** (≥ 12 c en 5 s, validation) : gagnant − milieu −1,5 point [−2,9 ; −0,2], donc un très léger excès. Mais il n'apparaît pas en exploration (+0,1) et il est plus petit que l'écart + frais (~2,5 c). Pas exploitable.

## Limites

- 4 jours de données (11.10 → 14.10 16 h 30 UTC), environ 830 cycles utilisables. Un avantage de quelques % par achat ne serait pas détectable (IC corrigé d'environ ±380 $ pour 200 achats).
- « Sans mouvement du BTC » est défini par notre modèle (Coinbase ajusté + Chainlink). Si Binance ou le perpétuel bougent avant Coinbase, une partie des mouvements « sans BTC » sont en réalité des mouvements du BTC vus ailleurs. C'est cohérent avec ce qu'on observe (le modèle rattrape le carnet). Mais l'étude ne dit pas quelle bourse mène.
- Une partie du « résidu qui se résorbe » est mécanique : le bruit du modèle (prix Coinbase qui oscille) revient de lui-même. Le filtre « BTC calme » limite cet effet sans le supprimer. La conclusion principale (le milieu ne revient pas, le carnet est juste au règlement) ne dépend pas du modèle.
- Photos du carnet chaque seconde : un retour en moins d'une seconde (flash) serait invisible ici, et de toute façon hors de portée d'un bot à ~1 s.
- Exécution simulée sans file d'attente ni concurrence. L'achat se fait déjà à la photo suivante (≈ +1 s).
- Le modèle (marche aléatoire normale, σ du cycle précédent × 1,8) ignore les queues épaisses et les changements de volatilité dans le cycle.

## Fichiers

- Script : `etude/bot5min/surreaction_poly_h1091.py` (modes `--extraire`, exploration, `--validation`).
- Résultats bruts : `etude/bot5min/surreaction_poly_h1091_exploration.json` (balayage complet), `etude/bot5min/surreaction_poly_h1091_validation.json`.
- PDF : `etude/bot5min/archives/pdf/surreaction_poly_h1091.pdf`.
