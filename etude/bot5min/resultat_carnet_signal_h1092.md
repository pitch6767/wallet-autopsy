# Bot95 — H1092 « le carnet comme signal seul » (BTC 5 min)

*Étude hors ligne du 15.10.2026. Aucun ordre, aucun bot ni fantôme modifié. Script : `etude/bot5min/carnet_signal_h1092.py`. Règles figées et poussées avant la validation : commit 78f085e5.*

## Verdict

**Non. Le déséquilibre du carnet Polymarket, pris seul, ne dit rien de plus sur le gagnant que le prix lui-même. Aucune des mesures testées n'ajoute d'information au milieu du carnet, ni au modèle de règlement. Aucune règle ne gagne ; l'une perd de façon démontrée.**

- **Gagnant − milieu par décile de déséquilibre : plat.** Que le carnet Up penche fortement vers les acheteurs ou vers les vendeurs, le gagnant tombe en moyenne là où le prix l'annonçait (écarts de −4 à +2,5 points, tous les intervalles contiennent 0, et le dessin change de forme entre exploration et validation).
- **Test logistique : le carnet n'ajoute rien au prix.** Ajouter les 5 mesures du carnet au milieu ne baisse pas l'erreur de prévision (Brier) : en validation, elle *augmente* légèrement, +0,0005 [−0,0001 ; +0,0012]. Même chose quand le modèle de règlement est déjà dans l'équation (+0,0006 [−0,0001 ; +0,0012]).
- **Validation des 3 règles figées** (13.10 00:00 → 14.10 16:25 UTC, 439 cycles, lue une seule fois) :
  - R1 « plus de niveaux de notre côté » : 224 achats, −309 $, ROI −14,5 %, IC corrigé [−577 ; −31] $ → **perd de façon démontrée** (les deux jours négatifs).
  - R2 « meilleur niveau penché de notre côté » : 386 achats, −183 $, ROI −5,1 %, IC corrigé [−654 ; +301] $ → **rien de démontré**.
  - R3 « l'autre côté se vide en fin de cycle » : 57 achats, +52 $, ROI +9,9 %, IC corrigé [−183 ; +305] $ → **rien de démontré** (+102 $ le 13.10, −50 $ le 14.10).
- **Aucun fantôme proposé** (aucun IC corrigé au-dessus de 0).
- **Conséquence pour le filtre « + carnet »** : s'il aide vraiment les stratégies en direct (non démontré en H1088), ce n'est pas parce que le carnet prédit le gagnant à lui seul. Ce serait au mieux un effet d'exécution (on achète quand il y a de la taille) ou un hasard.

## L'idée

En direct, les copies fantômes avec le filtre « + carnet » (carnet des 5 meilleurs niveaux penché de notre côté) semblaient faire mieux que les autres. Si c'est vrai, le carnet devrait aussi prédire le gagnant **tout seul**, sans stratégie autour. On le vérifie, à prix égal : à milieu de carnet identique, un carnet penché vers Up annonce-t-il plus souvent Up ?

## Méthode

- **Données** : enregistreur de Dublin (branche donnees-rapide), cycles BTC 5 min du 11.10 00:00 au 14.10 16:25 UTC (dernier cycle exporté, malgré un export relancé le 15.10 à 03 h 29). Photo du carnet chaque seconde, 5 niveaux de chaque côté. 933 cycles enregistrés, 844 utilisables (carnet complet, gagnant connu, pas de coupure).
- **Gagnant** = bot95/officiels.json (rafraîchi le 15.10), sinon prix à battre du cycle suivant (concordance 806/806 sur l'exploration).
- **Le carnet Down est le miroir exact du carnet Up** (acheteur Down à x = vendeur Up à 1 − x, mêmes tailles) : un seul carnet à étudier.
- **Mesures**, sur le jeton Up :
  - **I5** = (Σ tailles acheteurs − Σ tailles vendeurs) / total, sur les 5 meilleurs niveaux (+1 = que des acheteurs Up, −1 = que des vendeurs Up) ;
  - **I1** = la même chose au seul meilleur niveau ;
  - **micro** = microprix − milieu (le prix « pondéré par les tailles » du meilleur niveau) ;
  - **Iloin** = déséquilibre des niveaux 3 à 5 seulement (la profondeur loin du milieu) ;
  - **W5** = retrait soudain : variation en 5 s de la taille totale acheteurs moins celle des vendeurs (en log). W5 ≥ 1,5 = l'un des côtés a perdu plus des trois quarts de sa taille par rapport à l'autre ;
  - **Nniv** = nombre de niveaux acheteurs moins nombre de niveaux vendeurs à 5 c ou moins du milieu. Presque toujours 0 (les 5 niveaux sont collés à 1 c), sauf quand un côté est troué.
- **Modèle de règlement** : celui de H1090/H1091, inchangé (k = 1,8, Coinbase ajusté sur Chainlink).
- **Descriptif** : aux instants t = 30, 60, …, 270 s, gagnant (1 = Up) moins milieu, par décile de chaque mesure (déciles fixés sur l'exploration). Unité : points (1 point = 1 c). Positif = Up gagne plus souvent que le prix ne l'annonce.
- **Logistique** : P(Up) prédite par le milieu seul (M0) contre milieu + les 5 mesures (M1) ; puis milieu + modèle (M2) contre M2 + les 5 mesures (M3). Coefficients ajustés sur l'exploration, appliqués tels quels à la validation. Comparaison par le score de Brier (erreur au carré ; plus petit = meilleur).
- **Découpage chronologique** : exploration = 11.10 + 12.10 (405 cycles utilisables) ; validation = 13.10 + 14.10 jusqu'à 16:25 (439). Le 13.10, jour réservé, n'a été lu qu'une fois, après le gel.
- **Achat simulé** : décision sur la photo de la seconde t, achat au meilleur vendeur de la photo suivante (≈ t + 1 s), limité à la taille affichée, 10 $ maximum, frais 0,07·p·(1−p) par part, gardé jusqu'au règlement, un achat par cycle et par règle. Seulement quand l'écart acheteur-vendeur ≤ 3 c.
- **Statistiques** : IC 90 % par bootstrap sur les cycles (2 000 tirages pour les tableaux, 4 000 pour le Brier, 10 000 pour les règles ; tous les cycles de la période comptés, 0 $ sans achat). Bonferroni pour 3 règles : percentiles 1,67 / 98,33.
- **Balayage d'exploration** : 208 règles (mesure, seuil, tous côtés ou côté le moins cher, moment du cycle, plage de prix ; on achète le côté vers lequel le carnet penche). **59 sur 208 positives seulement** — moins que le hasard (≈ la moitié moins les frais). Les règles « I5 tous côtés » : 1 sur 24 positive. Les trois retenues sont les meilleures par borne basse de l'IC, une par famille : elles portent donc un biais de sélection.

## Résultats

### Tableau A — gagnant − milieu par décile de I5 (points, IC 90 %)

Instants 30 à 270 s regroupés. Décile 1 = carnet le plus penché vers les vendeurs Up (donc vers Down), décile 10 = le plus penché vers les acheteurs Up. Si le carnet était un signal, on verrait une pente du négatif vers le positif.

| Décile | I5 moyen | Exploration (11–12.10) | Validation (13–14.10) |
|---|---|---|---|
| 1 | −0,74 | −4,3 [−9,7 ; +1,2] | +1,6 [−4,1 ; +6,7] |
| 2 | −0,54 | −4,2 [−9,4 ; +1,1] | −2,1 [−7,3 ; +3,1] |
| 3 | −0,37 | −1,6 [−6,7 ; +3,1] | −0,3 [−4,9 ; +4,2] |
| 4 | −0,22 | +1,9 [−2,8 ; +6,6] | −1,0 [−4,7 ; +3,3] |
| 5 | −0,06 | −0,8 [−5,4 ; +4,0] | −0,6 [−4,8 ; +3,5] |
| 6 | +0,09 | +2,1 [−2,4 ; +6,8] | +0,2 [−4,9 ; +5,0] |
| 7 | +0,23 | +2,5 [−2,9 ; +8,0] | −0,8 [−5,7 ; +3,9] |
| 8 | +0,38 | +2,0 [−3,4 ; +7,1] | −1,3 [−5,9 ; +3,4] |
| 9 | +0,53 | −0,4 [−5,7 ; +5,3] | −1,5 [−6,6 ; +3,7] |
| 10 | +0,74 | −1,5 [−7,2 ; +4,5] | +1,5 [−5,4 ; +8,4] |

Aucune pente, aucun intervalle hors de 0, et pas le même dessin d'une période à l'autre. Mêmes conclusions pour I1, micro, Iloin et W5 (tableaux complets dans les fichiers JSON) : un seul décile sur 50 a un intervalle qui exclut 0 en validation (micro, décile 4, −4,2 [−8,4 ; −0,1]), ce qu'on attend du hasard.

Remarque : le déséquilibre est un peu lié au prix (corrélation I5–milieu −0,19 en exploration, −0,15 en validation) — quand Up est cher, il y a un peu plus de vendeurs Up affichés. Le test logistique corrige ce lien.

### Tableau B — le carnet ajoute-t-il quelque chose au prix ? (Brier, IC 90 %)

Négatif = le carnet améliore la prévision.

| Comparaison | Exploration (validation croisée 5 blocs) | Validation (coefficients d'exploration) |
|---|---|---|
| M1 − M0 (milieu + carnet contre milieu seul) | +0,00004 [−0,0008 ; +0,0008] | +0,0005 [−0,0001 ; +0,0012] |
| M3 − M2 (milieu + modèle + carnet contre milieu + modèle) | +0,00006 [−0,0008 ; +0,0009] | +0,0006 [−0,0001 ; +0,0012] |

Brier de validation : milieu brut 0,1611, M0 0,1610, M1 0,1616. Le milieu du carnet seul est déjà aussi bon que tout ce qu'on peut construire avec. Le modèle de règlement n'ajoute rien non plus (son coefficient est ≈ 0,01 à côté du milieu), comme en H1090/H1091.

### Tableau C — validation des 3 règles figées (13.10 00:00 → 14.10 16:25, 439 cycles)

On achète le côté vers lequel le carnet penche.

| Règle | Achats | Gagnés | Prix moyen | Mise | ROI | P&L | IC 90 % | IC corrigé (3 règles) |
|---|---|---|---|---|---|---|---|---|
| R1 ≥ 2 niveaux de plus de notre côté à ≤ 5 c, 120–240 s, prix 0,05–0,95 | 224 | 137 | 0,617 | 2 125 $ | −14,5 % | −309 $ | [−514 ; −95] | [−577 ; −31] |
| R2 meilleur niveau penché ≥ 0,5 de notre côté (I1), 60–240 s, prix 0,20–0,80 | 386 | 184 | 0,486 | 3 608 $ | −5,1 % | −183 $ | [−556 ; +185] | [−654 ; +301] |
| R3 l'autre côté se vide (W5 ≥ 1,5), côté le moins cher, 240–285 s, prix 0,20–0,80 | 57 | 21 | 0,352 | 525 $ | +9,9 % | +52 $ | [−129 ; +244] | [−183 ; +305] |

Par jour :

| Règle | 13.10 | 14.10 (jusqu'à 16:25) |
|---|---|---|
| R1 | 143 achats, −156 $ (−11,4 %) | 81 achats, −152 $ (−20,1 %) |
| R2 | 235 achats, −125 $ (−5,6 %) | 151 achats, −58 $ (−4,2 %) |
| R3 | 29 achats, +102 $ (+40,4 %) | 28 achats, −50 $ (−18,2 %) |

Rappel exploration (11–12.10) : R1 +246 $ (ROI +11,0 %), R2 +257 $ (+7,8 %), R3 +117 $ (+26,1 %). Les trois chutent en validation : c'est le signe classique d'un résultat d'exploration dû au hasard, choisi parmi 208.

R1 perd vraiment : quand un côté du carnet est « troué » (moins de niveaux près du milieu), acheter l'autre côté revient à payer le prix fort au moment où le marché va contre nous.

## Limites

- **Peu de données** : 2,7 jours (844 cycles), deux jours en validation dont un incomplet. L'export de Dublin s'arrête au 14.10 16:25 UTC alors qu'il a été relancé le 15.10 03:29 : l'enregistreur n'a peut-être rien envoyé depuis (à vérifier).
- **5 niveaux seulement**, photos chaque seconde : les ordres plus loin, et ce qui bouge entre deux photos, ne sont pas vus. Les ordres affichés peuvent être retirés (faux ordres), ce qui rend le carnet bruité par nature.
- **Nniv est presque toujours 0** : la mesure « nombre de niveaux » n'a de sens que quand un côté est troué ; elle mesure plutôt un carnet anormal qu'un déséquilibre.
- **Achats limités à la taille du meilleur niveau** et à 10 $ ; pas de file d'attente ni de latence réelle au-delà de +1 s.
- **Ce test ne dit pas** que le filtre « + carnet » est inutile dans une stratégie : il dit que le carnet seul ne prédit pas le gagnant. Une interaction (carnet + signal d'une stratégie) reste possible mais n'a pas été démontrée en H1088 non plus.
- **Biais de sélection** sur les règles (3 retenues parmi 208), corrigé seulement en partie par Bonferroni.

## Fichiers

- Script : `etude/bot5min/carnet_signal_h1092.py`
- Résultats bruts : `etude/bot5min/carnet_signal_h1092_exploration.json`, `etude/bot5min/carnet_signal_h1092_validation.json`
- PDF : `etude/bot5min/archives/pdf/carnet_signal_h1092.pdf`
