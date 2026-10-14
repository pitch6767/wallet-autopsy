# Bot95 — H1090 « l'ouverture du cycle » (BTC 5 min)

*Étude hors ligne du 14.10.2026. Aucun ordre, aucun bot modifié. Script : `etude/bot5min/ouverture_cycle_h1090.py`. Règles figées et poussées avant la validation : commit 6c3c4fd0.*

## Verdict

**Non. Le carnet Polymarket intègre l'« avance » du début de cycle tout de suite, dès la première seconde. Aucune des 3 règles figées ne gagne en validation.**

- L'avance existe bien : au début du cycle, le prix Chainlink du moment est en moyenne à 11–17 $ du prix à battre (en valeur absolue). La vraie probabilité de Up n'est donc pas 0,50 : environ 1 cycle sur 4 démarre déjà hors de 0,40–0,60.
- Mais le carnet le sait déjà. Le milieu du carnet bouge exactement comme le modèle (pente 0,99 en exploration, 1,10 en validation à t = 0 s). Il n'est pas collé à 0,50. Il prédit le gagnant aussi bien que le modèle à t = 0 et mieux à 10 et 30 s (le carnet voit les bourses avant Chainlink, qui arrive avec environ 1,7 s de retard).
- Le carnet est en place dès l'ouverture : écart de 1 c dans 97 % des photos, environ 80 $ au meilleur vendeur à 0 s et 1 200 $ sur 5 niveaux. On peut acheter, mais il n'y a pas de prix en retard à attraper.
- Validation des règles (13.10 + 14.10, 428 cycles, lue une seule fois) : R1 −115 $ (ROI −11,5 %), R2 +31 $ (+4,5 %), R3 −97 $ (−9,3 %). Les 3 intervalles corrigés contiennent 0. Les « avantages » que les règles achetaient étaient des erreurs du modèle, pas des erreurs du marché : elles achètent surtout le côté bon marché (prix moyen ≈ 0,37–0,39) et gagnent 35–44 % du temps.
- **Aucun fantôme proposé.**

Piège évité : avec la volatilité Chainlink « brute » (k = 1), on croit voir un carnet en retard (pente 0,61 à 0,69). Ce n'est pas le carnet qui est en retard, c'est le modèle qui est trop sûr de lui. Une fois le risque corrigé (k = 1,8, ajusté sur l'exploration seulement), la pente passe à 1,0.

## L'idée

Le prix à battre est la **moyenne** Chainlink des 60 s avant le début du cycle. Le règlement compare la moyenne des 60 dernières secondes. À l'ouverture, le prix du moment S n'est donc pas égal au prix à battre K : si le BTC a monté pendant la minute précédente, S est déjà au-dessus de K. La question : le carnet en tient-il compte dans les 30 premières secondes, ou les premières cotations restent-elles près de 0,50 ?

## Méthode

- **Données** : enregistreur de Dublin (branche donnees-rapide), cycles BTC 5 min du 11.10 au 14.10 15 h 50 UTC. Pour chaque cycle : photos du carnet Up/Down (5 niveaux, chaque seconde), Chainlink (cl2), moyenne 60 s officielle (tw), Coinbase.
- **Prix à battre** = strikeTwap enregistré (identique au « ptb » officiel). **Gagnant** = bot95/officiels.json, sinon prix à battre du cycle suivant (= moyenne finale de celui-ci). Les deux sources concordent sur les 709 cycles communs (709/709).
- **Modèle** : P(Up) = Φ((S − K) / (σ · k · √(260 − t))). σ = volatilité Chainlink d'une seconde mesurée sur le cycle précédent (passé seulement). k = 1,8, ajusté sur l'exploration. S = dernier prix Chainlink reçu (« Chainlink ») ou Coinbase reçu moins l'écart médian Coinbase − Chainlink du cycle précédent (« Coinbase ajusté »).
- **Découpage chronologique** : exploration = cycles du 11.10 et du 12.10 (405 cycles utilisables sur 469). Validation = 13.10 + 14.10 (428 utilisables sur 464). Le 13.10, jour réservé, n'a été lu qu'une fois, après le gel. Cycles écartés : sans cycle précédent enregistré, enregistrement coupé ou carnet absent.
- **Achat simulé** : photo du carnet à l'instant t. Achat au meilleur vendeur de cette photo, 10 $ maximum, limité à la taille affichée à ce prix. Frais 0,07·p·(1−p) par part. Gardé jusqu'au règlement. Un achat par cycle et par règle. Variante pessimiste : achat au meilleur vendeur de la photo suivante (environ 1 s plus tard).
- **Statistiques** : IC 90 % par bootstrap sur les cycles (10 000 tirages, tous les cycles de la période comptés, 0 $ quand rien ne se déclenche). Correction de Bonferroni pour 3 règles : percentiles 1,67 / 98,33.
- **Règles figées** (les meilleures plausibles parmi 168 combinaisons balayées en exploration, dont la plupart étaient négatives. Elles sont donc exposées au biais de sélection) : R1 = 0–5 s, Chainlink, avantage net ≥ 0,06 ; R2 = 5–15 s, Coinbase ajusté, avantage net ≥ 0,08 ; R3 = 15–30 s, Chainlink, avantage net ≥ 0,10. Avantage net = proba modèle du côté − meilleur prix vendeur − frais.

## Résultats

### Tableau A — l'avance au début du cycle (distance prix Chainlink du moment − prix à battre)

| Période | Instant | Cycles | Distance en $ (5 % / 25 % / médiane / 75 % / 95 %) | Distance moyenne absolue | z (en écarts-types, k = 1,8) 5 % / médiane / 95 % | Part des cycles où la proba modèle est hors 0,40–0,60 | Écart moyen à 0,50 : modèle | : carnet |
|---|---|---|---|---|---|---|---|---|
| exploration | t = 0 s | 275 | −22 / −6 / 0 / 7 / 27 | 10,7 $ | −0,34 / 0,01 / 0,44 | 27 % | 0,071 | 0,085 |
| exploration | t = 10 s | 405 | −37 / −11 / −1 / 7 / 30 | 14,7 $ | −0,63 / −0,02 / 0,49 | 38 % | 0,096 | 0,117 |
| exploration | t = 30 s | 405 | −51 / −15 / −1 / 12 / 38 | 20,3 $ | −0,98 / −0,02 / 0,80 | 49 % | 0,134 | 0,154 |
| validation | t = 0 s | 292 | −31 / −10 / 1 / 13 / 39 | 16,7 $ | −0,42 / 0,02 / 0,37 | 28 % | 0,074 | 0,095 |
| validation | t = 10 s | 428 | −46 / −14 / 1 / 16 / 51 | 21,0 $ | −0,54 / 0,02 / 0,50 | 38 % | 0,098 | 0,123 |
| validation | t = 30 s | 428 | −57 / −20 / 2 / 21 / 64 | 27,5 $ | −0,72 / 0,03 / 0,70 | 54 % | 0,131 | 0,157 |

### Tableau B — le carnet suit-il l'avance ? (milieu du carnet comparé au modèle, et qui prédit le mieux le gagnant)

| Période | Instant | Pente milieu du carnet / modèle (1 = suit entièrement, 0 = collé à 0,50) | Corrélation | Brier modèle | Brier carnet | Brier « toujours 0,50 » | Âge du dernier prix Chainlink |
|---|---|---|---|---|---|---|---|
| exploration (k = 1) | 0 s | 0,61 | 0,88 | 0,2461 | 0,2408 | 0,2500 | 1,6 s |
| exploration (k = 1) | 10 s | 0,69 | 0,94 | 0,2325 | 0,2265 | 0,2500 | 1,8 s |
| exploration (k = 1) | 30 s | 0,69 | 0,94 | 0,2200 | 0,2174 | 0,2500 | 1,8 s |
| exploration (k = 1,8) | 0 s | 0,99 | 0,88 | 0,2420 | 0,2408 | 0,2500 | 1,6 s |
| exploration (k = 1,8) | 10 s | 1,02 | 0,93 | 0,2301 | 0,2265 | 0,2500 | 1,8 s |
| exploration (k = 1,8) | 30 s | 0,98 | 0,93 | 0,2154 | 0,2174 | 0,2500 | 1,8 s |
| validation (k = 1,8) | 0 s | 1,10 | 0,89 | 0,2433 | 0,2434 | 0,2500 | 1,6 s |
| validation (k = 1,8) | 10 s | 1,11 | 0,93 | 0,2331 | 0,2256 | 0,2500 | 1,8 s |
| validation (k = 1,8) | 30 s | 1,07 | 0,95 | 0,2162 | 0,2120 | 0,2500 | 1,7 s |

### Tableau C — calibration, validation (photos à 5–30 s, une toutes les 5 s par cycle)

| Proba modèle | Photos | Cycles | Modèle (moyenne) | Milieu du carnet | Fréquence réelle de Up |
|---|---|---|---|---|---|
| 0,0–0,1 | 6 | 5 | 0,06 | 0,11 | 0,17 |
| 0,1–0,2 | 39 | 16 | 0,16 | 0,18 | 0,31 |
| 0,2–0,3 | 106 | 44 | 0,25 | 0,24 | 0,25 |
| 0,3–0,4 | 276 | 108 | 0,36 | 0,33 | 0,28 |
| 0,4–0,5 | 577 | 198 | 0,45 | 0,43 | 0,42 |
| 0,5–0,6 | 633 | 217 | 0,55 | 0,56 | 0,57 |
| 0,6–0,7 | 359 | 134 | 0,64 | 0,67 | 0,67 |
| 0,7–0,8 | 109 | 49 | 0,74 | 0,75 | 0,79 |
| 0,8–0,9 | 25 | 11 | 0,85 | 0,77 | 0,72 |
| 0,9–1,0 | 10 | 5 | 0,93 | 0,84 | 1,00 |

### Tableau D — état du carnet Up dans les premières secondes (validation, médianes)

| Seconde | Photos | Écart achat-vente | Part des photos à 1 c d'écart | Taille au meilleur vendeur | Profondeur 5 niveaux vendeurs | Avantage max. moyen du modèle sur le meilleur vendeur |
|---|---|---|---|---|---|---|
| 0 s | 291 | 0,01 | 97 % | 80 $ | 1165 $ | 0,032 |
| 1 s | 424 | 0,01 | 96 % | 129 $ | 1264 $ | 0,031 |
| 2 s | 426 | 0,01 | 97 % | 124 $ | 1303 $ | 0,034 |
| 3 s | 426 | 0,01 | 96 % | 157 $ | 1384 $ | 0,037 |
| 5 s | 423 | 0,01 | 97 % | 183 $ | 1553 $ | 0,039 |
| 10 s | 389 | 0,01 | 98 % | 209 $ | 1706 $ | 0,038 |
| 20 s | 428 | 0,01 | 96 % | 201 $ | 1728 $ | 0,037 |
| 30 s | 424 | 0,01 | 96 % | 224 $ | 1703 $ | 0,043 |

### Tableau E — règles figées : validation (13.10 + 14.10, lue une seule fois)

| Règle | Achats | Gagnés | Prix moyen | Proba modèle moyenne | Mise | ROI | P&L | IC 90 % | IC 90 % corrigé (Bonferroni ×3) | Pessimiste (+1 s) P&L / IC corrigé | 13.10 | 14.10 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| R1 ouverture 0–5 s, Chainlink, avantage ≥ 0,06 | 107 | 39 | 0,383 | 0,488 | 996 $ | −11,5 % | **−115 $** | [−330 $ ; +101 $] | [−387 $ ; +164 $] | −87 $ [−373 $ ; +208 $] | 73 achats, −85 $ | 34 achats, −30 $ |
| R2 5–15 s, Coinbase ajusté, avantage ≥ 0,08 | 73 | 32 | 0,390 | 0,516 | 695 $ | +4,5 % | **+31 $** | [−141 $ ; +199 $] | [−188 $ ; +254 $] | +21 $ [−197 $ ; +254 $] | 45 achats, −40 $ | 28 achats, +71 $ |
| R3 15–30 s, Chainlink, avantage ≥ 0,10 | 113 | 42 | 0,366 | 0,507 | 1049 $ | −9,3 % | **−97 $** | [−316 $ ; +132 $] | [−375 $ ; +196 $] | −82 $ [−377 $ ; +229 $] | 64 achats, −127 $ | 49 achats, +30 $ |

Rappel exploration (11–12.10, mêmes règles) :

- R1 : 121 achats, 50 gagnés, prix 0,387, ROI 4,2 %, +47 $ (IC 90 % [−189 $ ; +293 $])
- R3 : 120 achats, 52 gagnés, prix 0,387, ROI 13,2 %, +155 $ (IC 90 % [−108 $ ; +422 $])
- R2 : 94 achats, 45 gagnés, prix 0,437, ROI 10,1 %, +92 $ (IC 90 % [−118 $ ; +307 $])

## Lecture

- **L'avance est réelle et grandit avec le temps** (Tableau A). La moitié des cycles démarrent à plus de 6 à 10 $ du prix à battre. À 30 s, la moitié de la distance est de 15 à 20 $.
- **Le carnet ne la sous-estime pas** (Tableau B). Il s'écarte même un peu plus de 0,50 que le modèle (0,095 contre 0,074 à 0 s en validation), parce qu'il voit les bourses avant que Chainlink publie.
- **Calibration** (Tableau C) : dans les tranches qui ont du volume (0,2–0,8), le milieu du carnet est au moins aussi près de la fréquence réelle que le modèle. Les écarts aux extrêmes reposent sur 5 à 16 cycles.
- **Exécution** (Tableau D) : à 0 s, le meilleur vendeur offre environ 80 $ (médiane). Le carnet s'épaissit ensuite à environ 200 $ dès 10 s. Un achat de 10 $ passe donc presque toujours en entier, mais au prix juste.
- **Règles** (Tableau E) : en exploration, R1, R2 et R3 faisaient +47 $, +92 $ et +155 $. En validation : −115 $, +31 $ et −97 $. C'est le schéma classique d'un balayage qui a retenu du bruit. R2 est positive sur l'ensemble, mais seulement grâce au 14.10 (+71 $, 28 achats). Le 13.10 donne −40 $, et l'IC corrigé [−188 ; +254] $ est très large.

## Limites

- 4 jours de données (11.10 → 14.10 15 h 50 UTC), environ 830 cycles utilisables. Avec un IC corrigé d'environ ±200 $ pour 100 achats, un avantage de 2–3 % ne serait pas détectable.
- Le modèle est une marche aléatoire normale avec un σ du cycle précédent multiplié par un facteur unique (k = 1,8). Il ne tient compte ni des queues épaisses, ni des changements de volatilité dans le cycle.
- Le prix à battre n'est reçu qu'après environ 1,3 s (médiane). À t = 0 et 1 s, un vrai bot ne le connaît pas encore exactement : le tableau descriptif à 0 s est donc un peu optimiste pour un bot.
- Les photos du carnet sont prises chaque seconde. Un retard du carnet de moins d'une seconde serait invisible ici (cette question a déjà été traitée par les études « queue race »).
- Exécution simulée sans file d'attente ni concurrence. La variante +1 s change peu le résultat.
- Les 168 combinaisons balayées en exploration rendent les 3 règles retenues optimistes par construction. La validation l'a confirmé.

## Fichiers

- Script : `etude/bot5min/ouverture_cycle_h1090.py` (modes `--extraire`, exploration, `--validation`).
- Résultats bruts : `etude/bot5min/ouverture_cycle_h1090_exploration.json` (balayage complet), `etude/bot5min/ouverture_cycle_h1090_validation.json`.
- PDF : `etude/bot5min/archives/pdf/ouverture_cycle_h1090.pdf`.
