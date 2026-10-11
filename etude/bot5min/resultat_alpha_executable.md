# BOT95 — ALPHA EXÉCUTABLE : quelle part de l'avantage au signal survit à notre délai réel ?

Étude hors ligne du 11.10.2026 — aucun bot, aucun workflow modifié, rien publié. Cohortes A et B (mêmes entrées que le Hedge Lab). Apprentissage < 08.10 22:00 · validation → 10.10 10:25 · test inédit après. **Tout est mesuré à 0,3 s** (lignes enregistrées toutes les ~0,3 s ; photos 100 ms seulement là où elles couvrent le signal). Les enregistrements 50 ms du VPS de Dublin ne sont **pas encore disponibles** : une section 50 ms sera ajoutée plus tard.

## Réponse courte (en tête) — mesuré à 0,3 s

- **Cascade A** : apprentissage : théorique +2 168 $ → réalisé au signal +1 632 $ → 0,3 s marché +1 294 $ (offre disparue −301 $, payé trop cher −54 $) → règle actuelle +946 $ ; validation : théorique +2 972 $ → réalisé au signal +753 $ → 0,3 s marché +166 $ (offre disparue −736 $, payé trop cher −109 $) → règle actuelle −293 $ ; inédit : théorique +2 282 $ → réalisé au signal +273 $ → 0,3 s marché −465 $ (offre disparue −595 $, payé trop cher −86 $) → règle actuelle −411 $.
- **Cascade B** : apprentissage : théorique +5 982 $ → réalisé au signal +2 191 $ → 0,3 s marché +736 $ (offre disparue −1 313 $, payé trop cher −258 $) → règle actuelle +460 $ ; validation : théorique +7 229 $ → réalisé au signal +926 $ → 0,3 s marché −295 $ (offre disparue −879 $, payé trop cher −295 $) → règle actuelle −70 $ ; inédit : théorique +5 435 $ → réalisé au signal −304 $ → 0,3 s marché −1 526 $ (offre disparue −740 $, payé trop cher −170 $) → règle actuelle −1 583 $.
- **Durée de vie A** (valid. + test) : offre initiale médiane 0,90 s ; quantité voulue encore au prix du signal à 0,3 s : 55,4 % en moyenne, à 0,6 s : 49,6 % ; condition d'écart médiane 0,60 s ; seconde fenêtre au prix du signal dans 62,4 % des signaux.
- **Durée de vie B** (valid. + test) : offre initiale médiane 0,90 s ; quantité voulue encore au prix du signal à 0,3 s : 55,3 % en moyenne, à 0,6 s : 46,6 % ; condition d'écart médiane 0,90 s ; seconde fenêtre au prix du signal dans 73,0 % des signaux.
- **Politiques A** (Δ vs actuel, valid. → test) : (2) limite agressive au plafond +477 $ [+31 $ ; +969 $] → −34 $ [−136 $ ; +42 $] ; (4) seconde chance N s au plafond +477 $ [+48 $ ; +980 $] → +86 $ [−95 $ ; +311 $] ; (1) marché après 0,3 s (sans limite) +459 $ [−28 $ ; +989 $] → −54 $ [−160 $ ; +37 $]. Passif (bornes) valid. : +1 407 $ / −66 $.
- **Politiques B** (Δ vs actuel, valid. → test) : (2) limite agressive au plafond +414 $ [−502 $ ; +1 470 $] → +175 $ [−121 $ ; +479 $] ; (4) seconde chance N s au plafond +323 $ [−612 $ ; +1 436 $] → +89 $ [−216 $ ; +410 $] ; H163 sélection : P(offre encore là à 0,3 s) ≥ seuil +153 $ [−119 $ ; +440 $] → +118 $ [−119 $ ; +324 $]. Passif (bornes) valid. : +151 $ / −475 $.
- **Réponse à Pitch** : sélectionner les opportunités dont l'avantage survit au délai n'améliore PAS la performance de façon démontrée : aucune politique n'a un IC 90 % entièrement positif à la fois en validation et en test.

## 1. Cascade de l'avantage (mesuré à 0,3 s)

Avantage théorique = Σ parts × (proba du modèle − prix − frais) ; réalisé = Σ parts × (issue − prix − frais). Au signal : prix et taille de la ligne du signal. À 0,3 / 0,6 s : ordre au meilleur vendeur de la ligne exécutée (marché, sans limite ; 0,6 s : moitié de la taille). (a) **modèle faux** = avantage théorique au signal − P&L réalisé au signal ; (b) **offre disparue** = P&L au signal des parts qu'on n'a plus pu acheter ; (c) **payé trop cher** = surcoût (prix + frais) sur les parts achetées ; autre = parts en plus (prix plus bas).

| Cohorte | Période | Signaux | Avantage théorique au signal | à 0,3 s | à 0,6 s | P&L réalisé au signal | (a) modèle faux | à 0,3 s (marché) | (b) offre disparue | (c) payé trop cher | autre | à 0,3 s, règle actuelle (limite = prix du signal) | à 0,6 s (marché) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A | apprentissage | 51 | +2 168 $ | +2 263 $ | +1 774 $ | **+1 632 $** | −535 $ | **+1 294 $** | −301 $ | −54 $ | +17 $ | +946 $ | +965 $ |
| A | validation | 62 | +2 972 $ | +2 402 $ | +2 417 $ | **+753 $** | −2 219 $ | **+166 $** | −736 $ | −109 $ | +258 $ | −293 $ | +28 $ |
| A | inédit | 47 | +2 282 $ | +2 115 $ | +1 746 $ | **+273 $** | −2 008 $ | **−465 $** | −595 $ | −86 $ | −58 $ | −411 $ | −199 $ |
| B | apprentissage | 238 | +5 982 $ | +5 634 $ | +4 812 $ | **+2 191 $** | −3 792 $ | **+736 $** | −1 313 $ | −258 $ | +117 $ | +460 $ | +744 $ |
| B | validation | 237 | +7 229 $ | +6 341 $ | +5 351 $ | **+926 $** | −6 304 $ | **−295 $** | −879 $ | −295 $ | −47 $ | −70 $ | −592 $ |
| B | inédit | 178 | +5 435 $ | +4 598 $ | +3 709 $ | **−304 $** | −5 739 $ | **−1 526 $** | −740 $ | −170 $ | −312 $ | −1 583 $ | −1 336 $ |

Contrôle : P&L au signal + (b) + (c) + autre = P&L à 0,3 s (marché).

## 2. E1 — Durée de vie des signaux (mesuré à 0,3 s)

Durées depuis la ligne du signal jusqu'à la première ligne où : la condition d'écart n'est plus vraie (écart modèle − prix ≥ seuil dans la bande de prix) ; l'offre initiale n'est plus là (prix ≤ prix du signal avec ≥ 1 part) ; l'avantage économique (modèle − prix − frais ≥ 0,10) n'est plus là. Une durée de 0,3 s = disparue dès la ligne suivante (résolution). **Une offre qui disparaît n'est pas un avantage qui disparaît** : comparer les colonnes.

| Cohorte | Période | Signaux | Condition (s) : 10 % · méd. · 90 % | Offre initiale (s) : 10 % · méd. · 90 % | Avantage ≥ 0,10 (s) : méd. | Prix > plafond pour la 1re fois (s) : méd. · jamais | Part de la quantité voulue encore au prix du signal à 0,3 · 0,6 · 0,9 · 1,5 · 3 s (moyenne) | Signaux avec une 2e fenêtre ≤ prix du signal · ≤ plafond | Photos 100 ms : n · part à 0,1 · 0,2 · 0,3 s |
|---|---|---|---|---|---|---|---|---|---|
| A | apprentissage | 51 | 0,30 · 0,60 · 2,40 | 0,30 · 0,31 · 38,70 | 61,74 | 6,75 · 33,3 % | 36,0 % · 31,5 % · 28,4 % · 30,0 % · 25,6 % | 60,8 % · 86,3 % | 2 · 34,4 % · 0,0 % · 2,8 % |
| A | validation | 62 | 0,30 · 0,30 · 3,42 | 0,30 · 0,75 · 95,85 | 40,65 | 4,65 · 41,9 % | 49,7 % · 47,7 % · 38,2 % · 41,9 % · 46,0 % | 59,7 % · 67,7 % | 7 · 85,7 % · 57,1 % · 50,0 % |
| A | inédit | 47 | 0,30 · 0,60 · 3,00 | 0,30 · 1,50 · 133,60 | 82,40 | 9,60 · 51,1 % | 62,8 % · 52,0 % · 47,9 % · 40,7 % · 42,4 % | 66,0 % · 74,5 % | 0 · — · — · — |
| B | apprentissage | 238 | 0,30 · 0,60 · 16,50 | 0,30 · 0,30 · 16,65 | 10,05 | 1,50 · 27,7 % | 40,6 % · 34,2 % · 27,6 % · 26,2 % · 27,4 % | 69,3 % · 84,0 % | 62 · 62,6 % · 49,8 % · 46,6 % |
| B | validation | 237 | 0,30 · 0,90 · 25,38 | 0,30 · 0,60 · 66,24 | 16,50 | 2,10 · 37,1 % | 54,5 % · 45,4 % · 39,8 % · 38,1 % · 34,3 % | 71,3 % · 81,0 % | 69 · 72,4 % · 66,2 % · 62,7 % |
| B | inédit | 178 | 0,30 · 1,20 · 21,84 | 0,30 · 0,90 · 96,87 | 15,75 | 6,15 · 33,7 % | 56,5 % · 48,3 % · 43,4 % · 37,8 % · 39,3 % | 75,3 % · 82,0 % | 10 · 80,3 % · 67,3 % · 69,0 % |

Les quantités à 0,1 / 0,2 s viennent des photos 100 ms (3 meilleurs niveaux, quantité à un prix ≤ prix du signal) ; elles ne couvrent qu'une partie des signaux.

### H160 — grand mais bref contre modéré mais persistant (classé avec l'information du signal seulement)

Classes fixées sur l'apprentissage : écart modèle − prix au-dessus / au-dessous de sa médiane d'apprentissage ; taille affichée au-dessus / au-dessous de sa médiane d'apprentissage.

| Cohorte | Écart au signal | Taille affichée | Période | Signaux | Offre encore là à 0,3 s | Durée médiane de l'offre (s) | P&L au signal | P&L à 0,3 s (règle actuelle) |
|---|---|---|---|---|---|---|---|---|
| A | grand | grande | validation | 11 | 72,7 % | 11,40 | −146 $ | −9 $ |
| A | grand | grande | inédit | 7 | 57,1 % | 0,60 | +539 $ | +264 $ |
| A | grand | petite | validation | 13 | 23,1 % | 0,30 | +198 $ | +17 $ |
| A | grand | petite | inédit | 2 | 50,0 % | 0,60 | +10 $ | +14 $ |
| A | modéré | grande | validation | 27 | 74,1 % | 3,30 | +564 $ | −349 $ |
| A | modéré | grande | inédit | 27 | 81,5 % | 8,10 | −354 $ | −602 $ |
| A | modéré | petite | validation | 11 | 54,5 % | 0,90 | +138 $ | +48 $ |
| A | modéré | petite | inédit | 11 | 63,6 % | 0,61 | +78 $ | −87 $ |
| B | grand | grande | validation | 76 | 65,8 % | 0,90 | +791 $ | −13 $ |
| B | grand | grande | inédit | 47 | 57,4 % | 0,89 | +493 $ | −555 $ |
| B | grand | petite | validation | 47 | 29,8 % | 0,30 | +101 $ | −183 $ |
| B | grand | petite | inédit | 42 | 33,3 % | 0,30 | −77 $ | −143 $ |
| B | modéré | grande | validation | 75 | 84,0 % | 4,50 | −28 $ | −22 $ |
| B | modéré | grande | inédit | 70 | 90,0 % | 4,20 | −697 $ | −824 $ |
| B | modéré | petite | validation | 39 | 43,6 % | 0,30 | +61 $ | +148 $ |
| B | modéré | petite | inédit | 19 | 42,1 % | 0,31 | −22 $ | −61 $ |

## 3. E2 — Prix maximal exécutable et politiques d'exécution (mesuré à 0,3 s)

Probabilité prudente = régression logistique sur l'apprentissage (A + B réunis) de l'issue sur logit(proba du modèle), logit(milieu Polymarket) et la cohorte ; coefficients 0,93, 0,33, −0,08, constante −0,07. Plafond = plus haut prix c tel que c + frais(c) ≤ proba prudente − marge (arrondi au cent inférieur). Marge et N choisis sur l'apprentissage : A marge 0,00 (0,00 → +1 229 $, 0,02 → +1 229 $, 0,05 → +1 226 $, 0,10 → +1 156 $, 0,15 → +742 $), N = 1 s (1 s → +1 243 $, 3 s → +1 243 $, 5 s → +1 243 $, 10 s → +1 243 $, 30 s → +1 243 $) · B marge 0,00 (0,00 → +701 $, 0,02 → +442 $, 0,05 → +676 $, 0,10 → +270 $, 0,15 → +180 $), N = 1 s (1 s → +715 $, 3 s → +617 $, 5 s → +567 $, 10 s → +373 $, 30 s → +630 $).

**Profondeur inconnue** : seul le meilleur niveau existe dans les lignes ; la « limite agressive » (2) ne prend donc que le meilleur niveau, et (2) = (3) à ceci près que (3) garde la limite au prix du signal. (5) est une borne : ordre passif à min(plafond, prix du signal − 1 c) pendant 30 s, optimiste = rempli dès que le vendeur touche (50 $ entiers), pessimiste = traversée d'1 c tenue 2 lignes, moitié de la taille.

| Cohorte | Politique | Période | Signaux | Entrées (participation) | Partielles | Frais | P&L net | Δ vs actuel [IC 90 %] | Jackpots du signal manqués | Creux |
|---|---|---|---|---|---|---|---|---|---|---|
| A | actuel (limite = prix du signal, 0,3 s) | apprentissage | 51 | 26 (51,0 %) | 14 | +47 $ | +946 $ | — | 4/9 | −150 $ |
| A | actuel (limite = prix du signal, 0,3 s) | validation | 62 | 37 (59,7 %) | 19 | +67 $ | −293 $ | — | 9/14 | −355 $ |
| A | actuel (limite = prix du signal, 0,3 s) | inédit | 47 | 34 (72,3 %) | 15 | +65 $ | −411 $ | — | 3/8 | −523 $ |
| A | (1) marché après 0,3 s (sans limite) | apprentissage | 51 | 51 (100,0 %) | 33 | +78 $ | +1 294 $ | **+348 $** [−127 $ ; +862 $] | 0/9 | −161 $ |
| A | (1) marché après 0,3 s (sans limite) | validation | 62 | 62 (100,0 %) | 35 | +94 $ | +166 $ | **+459 $** [−28 $ ; +989 $] | 0/14 | −325 $ |
| A | (1) marché après 0,3 s (sans limite) | inédit | 47 | 47 (100,0 %) | 25 | +74 $ | −465 $ | **−54 $** [−160 $ ; +37 $] | 0/8 | −571 $ |
| A | (2) limite agressive au plafond | apprentissage | 51 | 49 (96,1 %) | 32 | +76 $ | +1 229 $ | **+283 $** [−172 $ ; +881 $] | 1/9 | −161 $ |
| A | (2) limite agressive au plafond | validation | 62 | 51 (82,3 %) | 28 | +86 $ | +184 $ | **+477 $** [+31 $ ; +969 $] | 3/14 | −273 $ |
| A | (2) limite agressive au plafond | inédit | 47 | 42 (89,4 %) | 22 | +71 $ | −445 $ | **−34 $** [−136 $ ; +42 $] | 2/8 | −557 $ |
| A | (3) abandon si prix du signal > plafond | apprentissage | 51 | 26 (51,0 %) | 14 | +47 $ | +946 $ | **+0 $** [+0 $ ; +0 $] | 4/9 | −150 $ |
| A | (3) abandon si prix du signal > plafond | validation | 62 | 37 (59,7 %) | 19 | +67 $ | −293 $ | **+0 $** [+0 $ ; +0 $] | 9/14 | −355 $ |
| A | (3) abandon si prix du signal > plafond | inédit | 47 | 34 (72,3 %) | 15 | +65 $ | −411 $ | **+0 $** [+0 $ ; +0 $] | 3/8 | −523 $ |
| A | (4) seconde chance N s au plafond | apprentissage | 51 | 50 (98,0 %) | 33 | +76 $ | +1 243 $ | **+297 $** [−182 $ ; +885 $] | 1/9 | −161 $ |
| A | (4) seconde chance N s au plafond | validation | 62 | 51 (82,3 %) | 28 | +86 $ | +184 $ | **+477 $** [+48 $ ; +980 $] | 3/14 | −273 $ |
| A | (4) seconde chance N s au plafond | inédit | 47 | 43 (91,5 %) | 22 | +73 $ | −326 $ | **+86 $** [−95 $ ; +311 $] | 1/8 | −437 $ |
| A | (5) passif borne optimiste | apprentissage | 51 | 31 (60,8 %) | 0 | +0 $ | +525 $ | **−421 $** [−1 640 $ ; +975 $] | 5/9 | −550 $ |
| A | (5) passif borne optimiste | validation | 62 | 48 (77,4 %) | 0 | +0 $ | +1 114 $ | **+1 407 $** [+153 $ ; +2 861 $] | 6/14 | −400 $ |
| A | (5) passif borne optimiste | inédit | 47 | 36 (76,6 %) | 0 | +0 $ | +8 $ | **+420 $** [−374 $ ; +1 358 $] | 4/8 | −800 $ |
| A | (5) passif borne pessimiste | apprentissage | 51 | 27 (52,9 %) | 16 | +0 $ | +3 $ | **−943 $** [−1 887 $ ; −50 $] | 5/9 | −459 $ |
| A | (5) passif borne pessimiste | validation | 62 | 44 (71,0 %) | 29 | +0 $ | −359 $ | **−66 $** [−771 $ ; +700 $] | 8/14 | −580 $ |
| A | (5) passif borne pessimiste | inédit | 47 | 34 (72,3 %) | 27 | +0 $ | +185 $ | **+597 $** [+158 $ ; +1 096 $] | 5/8 | −379 $ |
| A | H163 sélection : P(offre encore là à 0,3 s) ≥ seuil | apprentissage | 51 | 18 (35,3 %) | 9 | +33 $ | +1 153 $ | **+207 $** [+43 $ ; +388 $] | 5/9 | −111 $ |
| A | H163 sélection : P(offre encore là à 0,3 s) ≥ seuil | validation | 62 | 27 (43,5 %) | 9 | +58 $ | −228 $ | **+65 $** [−73 $ ; +201 $] | 12/14 | −296 $ |
| A | H163 sélection : P(offre encore là à 0,3 s) ≥ seuil | inédit | 47 | 21 (44,7 %) | 4 | +51 $ | −279 $ | **+133 $** [−37 $ ; +306 $] | 6/8 | −449 $ |
| A | H163 sélection : P&L prédit > 0 (ridge, app.) | apprentissage | 51 | 26 (51,0 %) | 14 | +47 $ | +946 $ | **+0 $** [+0 $ ; +0 $] | 4/9 | −150 $ |
| A | H163 sélection : P&L prédit > 0 (ridge, app.) | validation | 62 | 37 (59,7 %) | 19 | +67 $ | −293 $ | **+0 $** [+0 $ ; +0 $] | 9/14 | −355 $ |
| A | H163 sélection : P&L prédit > 0 (ridge, app.) | inédit | 47 | 34 (72,3 %) | 15 | +65 $ | −411 $ | **+0 $** [+0 $ ; +0 $] | 3/8 | −523 $ |
| A | actuel à 0,6 s (moitié de la taille) | apprentissage | 51 | 19 (37,3 %) | 12 | +32 $ | +594 $ | **−352 $** [−689 $ ; −57 $] | 6/9 | −104 $ |
| A | actuel à 0,6 s (moitié de la taille) | validation | 62 | 31 (50,0 %) | 18 | +59 $ | −182 $ | **+111 $** [−71 $ ; +301 $] | 11/14 | −253 $ |
| A | actuel à 0,6 s (moitié de la taille) | inédit | 47 | 30 (63,8 %) | 16 | +51 $ | −269 $ | **+142 $** [−76 $ ; +380 $] | 4/8 | −284 $ |
| A | (2) plafond à 0,6 s | apprentissage | 51 | 48 (94,1 %) | 32 | +66 $ | +956 $ | **+10 $** [−624 $ ; +773 $] | 2/9 | −161 $ |
| A | (2) plafond à 0,6 s | validation | 62 | 50 (80,6 %) | 28 | +87 $ | +138 $ | **+431 $** [−20 $ ; +957 $] | 3/14 | −278 $ |
| A | (2) plafond à 0,6 s | inédit | 47 | 38 (80,9 %) | 22 | +57 $ | −152 $ | **+260 $** [−97 $ ; +735 $] | 2/8 | −251 $ |
| B | actuel (limite = prix du signal, 0,3 s) | apprentissage | 238 | 113 (47,5 %) | 53 | +182 $ | +460 $ | — | 12/15 | −458 $ |
| B | actuel (limite = prix du signal, 0,3 s) | validation | 237 | 144 (60,8 %) | 59 | +258 $ | −70 $ | — | 6/11 | −910 $ |
| B | actuel (limite = prix du signal, 0,3 s) | inédit | 178 | 112 (62,9 %) | 43 | +214 $ | −1 583 $ | — | 6/11 | −1 776 $ |
| B | (1) marché après 0,3 s (sans limite) | apprentissage | 238 | 237 (99,6 %) | 142 | +322 $ | +736 $ | **+276 $** [−738 $ ; +1 332 $] | 0/15 | −739 $ |
| B | (1) marché après 0,3 s (sans limite) | validation | 237 | 237 (100,0 %) | 113 | +374 $ | −295 $ | **−225 $** [−1 214 $ ; +907 $] | 0/11 | −1 301 $ |
| B | (1) marché après 0,3 s (sans limite) | inédit | 178 | 177 (99,4 %) | 87 | +273 $ | −1 526 $ | **+56 $** [−316 $ ; +427 $] | 0/11 | −1 772 $ |
| B | (2) limite agressive au plafond | apprentissage | 238 | 205 (86,1 %) | 120 | +293 $ | +701 $ | **+241 $** [−691 $ ; +1 213 $] | 3/15 | −709 $ |
| B | (2) limite agressive au plafond | validation | 237 | 195 (82,3 %) | 83 | +335 $ | +344 $ | **+414 $** [−502 $ ; +1 470 $] | 2/11 | −1 058 $ |
| B | (2) limite agressive au plafond | inédit | 178 | 150 (84,3 %) | 70 | +250 $ | −1 407 $ | **+175 $** [−121 $ ; +479 $] | 5/11 | −1 669 $ |
| B | (3) abandon si prix du signal > plafond | apprentissage | 238 | 113 (47,5 %) | 53 | +182 $ | +460 $ | **+0 $** [+0 $ ; +0 $] | 12/15 | −458 $ |
| B | (3) abandon si prix du signal > plafond | validation | 237 | 144 (60,8 %) | 59 | +258 $ | −70 $ | **+0 $** [+0 $ ; +0 $] | 6/11 | −910 $ |
| B | (3) abandon si prix du signal > plafond | inédit | 178 | 112 (62,9 %) | 43 | +214 $ | −1 583 $ | **+0 $** [+0 $ ; +0 $] | 6/11 | −1 776 $ |
| B | (4) seconde chance N s au plafond | apprentissage | 238 | 209 (87,8 %) | 120 | +302 $ | +715 $ | **+255 $** [−725 $ ; +1 364 $] | 3/15 | −709 $ |
| B | (4) seconde chance N s au plafond | validation | 237 | 201 (84,8 %) | 85 | +347 $ | +254 $ | **+323 $** [−612 $ ; +1 436 $] | 2/11 | −1 092 $ |
| B | (4) seconde chance N s au plafond | inédit | 178 | 152 (85,4 %) | 71 | +254 $ | −1 494 $ | **+89 $** [−216 $ ; +410 $] | 5/11 | −1 705 $ |
| B | (5) passif borne optimiste | apprentissage | 238 | 149 (62,6 %) | 0 | +0 $ | −634 $ | **−1 094 $** [−2 835 $ ; +655 $] | 9/15 | −1 718 $ |
| B | (5) passif borne optimiste | validation | 237 | 167 (70,5 %) | 0 | +0 $ | +81 $ | **+151 $** [−2 064 $ ; +2 568 $] | 5/11 | −1 870 $ |
| B | (5) passif borne optimiste | inédit | 178 | 132 (74,2 %) | 0 | +0 $ | −1 109 $ | **+474 $** [−1 136 $ ; +2 195 $] | 6/11 | −1 467 $ |
| B | (5) passif borne pessimiste | apprentissage | 238 | 143 (60,1 %) | 81 | +0 $ | +617 $ | **+157 $** [−1 346 $ ; +1 757 $] | 9/15 | −1 034 $ |
| B | (5) passif borne pessimiste | validation | 237 | 152 (64,1 %) | 76 | +0 $ | −545 $ | **−475 $** [−2 108 $ ; +1 274 $] | 7/11 | −1 741 $ |
| B | (5) passif borne pessimiste | inédit | 178 | 124 (69,7 %) | 77 | +0 $ | −79 $ | **+1 504 $** [+613 $ ; +2 476 $] | 7/11 | −657 $ |
| B | H163 sélection : P(offre encore là à 0,3 s) ≥ seuil | apprentissage | 238 | 89 (37,4 %) | 30 | +171 $ | +541 $ | **+82 $** [−20 $ ; +198 $] | 12/15 | −458 $ |
| B | H163 sélection : P(offre encore là à 0,3 s) ≥ seuil | validation | 237 | 116 (48,9 %) | 37 | +232 $ | +83 $ | **+153 $** [−119 $ ; +440 $] | 6/11 | −825 $ |
| B | H163 sélection : P(offre encore là à 0,3 s) ≥ seuil | inédit | 178 | 92 (51,7 %) | 27 | +196 $ | −1 465 $ | **+118 $** [−119 $ ; +324 $] | 9/11 | −1 693 $ |
| B | H163 sélection : P&L prédit > 0 (ridge, app.) | apprentissage | 238 | 80 (33,6 %) | 28 | +145 $ | +519 $ | **+59 $** [−451 $ ; +492 $] | 13/15 | −307 $ |
| B | H163 sélection : P&L prédit > 0 (ridge, app.) | validation | 237 | 103 (43,5 %) | 25 | +214 $ | −109 $ | **−39 $** [−499 $ ; +376 $] | 7/11 | −805 $ |
| B | H163 sélection : P&L prédit > 0 (ridge, app.) | inédit | 178 | 65 (36,5 %) | 14 | +139 $ | −1 066 $ | **+517 $** [−300 $ ; +1 295 $] | 10/11 | −1 272 $ |
| B | actuel à 0,6 s (moitié de la taille) | apprentissage | 238 | 97 (40,8 %) | 56 | +140 $ | −40 $ | **−500 $** [−1 207 $ ; +143 $] | 13/15 | −532 $ |
| B | actuel à 0,6 s (moitié de la taille) | validation | 237 | 120 (50,6 %) | 58 | +202 $ | −593 $ | **−524 $** [−1 359 $ ; +225 $] | 7/11 | −1 063 $ |
| B | actuel à 0,6 s (moitié de la taille) | inédit | 178 | 99 (55,6 %) | 48 | +168 $ | −1 304 $ | **+279 $** [−319 $ ; +877 $] | 8/11 | −1 479 $ |
| B | (2) plafond à 0,6 s | apprentissage | 238 | 183 (76,9 %) | 112 | +248 $ | +188 $ | **−271 $** [−1 212 $ ; +720 $] | 7/15 | −454 $ |
| B | (2) plafond à 0,6 s | validation | 237 | 188 (79,3 %) | 96 | +292 $ | −290 $ | **−220 $** [−1 461 $ ; +1 105 $] | 3/11 | −1 162 $ |
| B | (2) plafond à 0,6 s | inédit | 178 | 139 (78,1 %) | 78 | +206 $ | −1 456 $ | **+127 $** [−432 $ ; +698 $] | 7/11 | −1 612 $ |

Sélection H163 : modèle « offre encore là à 0,3 s » (logistique, apprentissage, variables : écart modèle − prix, log taille affichée, log taille / parts voulues, volatilité perp 30 s, temps restant, prix, écart vendeur-acheteur, proba prudente − prix, cohorte B) — AUC apprentissage 0,84 · validation 0,79 · inédit 0,80 ; seuil choisi sur l'apprentissage : A 0,60 · B 0,40. Le modèle « P&L prédit » est une régression ridge sur l'apprentissage (mêmes variables).

Durée de calcul : 60 s.