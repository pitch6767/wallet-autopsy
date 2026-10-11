# BOT95 — Trois moteurs fantômes sur les mêmes signaux (A brut · B corrigé · C alpha exécutable)

Étude hors ligne du 11.10.2026 — aucun bot, aucun workflow modifié, rien publié. 1146 cycles BTC réglés (07.10 08:00 → 11.10 07:55, heure suisse) : apprentissage < 08.10 22:00 · validation → 10.10 10:25 · test après (déjà en partie regardé par d'autres études : **exploratoire**). Positions indépendantes de 50 $ (frais compris), aucun plafond de capital. Résultat principal = exécution PRUDENTE 0,3 s ; référence = moteur A (= GARDER chaque signal tel qu'aujourd'hui). Fuite de `parts_r` corrigée : la cohorte B utilise le modèle 0,015 % calculé avec la valeur À LA DATE de la seconde courante.

## Verdict (en tête)

- **B désaccord corrigé** contre A (prudente 0,3 s) : validation +0 $ [IC 90 % +0 $ ; +0 $] · test +0 $ [+0 $ ; +0 $] → **pas d'amélioration nette sur les deux périodes**.
- **C alpha exécutable** contre A (prudente 0,3 s) : validation +533 $ [IC 90 % −686 $ ; +1 804 $] · test +1 169 $ [−89 $ ; +2 349 $] → **amélioration nette sur les deux périodes** (IC encore à cheval sur 0 : à confirmer en direct).
- **Résultats absolus (prudente 0,3 s)** : A +1 544 $ / −401 $ / −1 664 $ ; B +1 544 $ / −401 $ / −1 664 $ ; C +2 384 $ / +132 $ / −495 $ (apprentissage / validation / test). C participe à 63 % des signaux en validation et 46 % en test : il **perd moins** que A, il n'est **pas rentable** en test.
- **B = A** : la marge choisie sur l'apprentissage (0,00) laisse passer tous les signaux (la calibration ne trie rien : toutes les probabilités calibrées restent au-dessus du prix + frais).
- **D'où vient l'écart de C** : la sélection seule (limite = prix du signal) fait validation +286 $, test +1 051 $ ; le plafond de prix seul (tout envoyer) fait +175 $ / +118 $.
- **Gagnant déclaré : C alpha exécutable** (règle : amélioration nette en validation ET en test).
- **Sélection adverse confirmée sur les lignes 0,3 s** (toutes périodes) : cohorte A — offre encore là à 0,3 s : 25 % gagnés (96), disparue : 49 % (63) ; cohorte B : 31 % (388) contre 39 % (311) ; V2-F original : 20 % (717) contre 28 % (256). En direct (vitesse.json, 0,25 s, tous fantômes) : 20 % (977) contre 37 % (235).
- **Pourquoi C ne peut pas faire mieux que « choisir ce qui reste »** : P(survie) est bien prévisible (AUC validation 0,82, test 0,76), mais P(gain | offre encore là) ne l'est presque pas (AUC validation 0,63, test 0,59) ; la probabilité du modèle seule : AUC 0,64 / 0,71.

## 1. Sélection adverse : l'offre encore achetable après notre délai gagne-t-elle moins souvent ?

Offre « encore là » = à la première ligne ≥ signal + 0,3 s, le meilleur vendeur est ≤ prix du signal avec ≥ 1 part. Taux de gain du côté acheté (issue officielle).

| Signaux | Période | Offre encore là : gagnés | n | Offre disparue : gagnés | n |
|---|---|---|---|---|---|
| A | apprentissage | 36 % | 25 | 40 % | 25 |
| A | validation | 22 % | 37 | 60 % | 25 |
| A | test | 21 % | 34 | 46 % | 13 |
| A | toutes | 25 % | 96 | 49 % | 63 |
| B | apprentissage | 40 % | 124 | 43 % | 136 |
| B | validation | 33 % | 151 | 32 % | 107 |
| B | test | 19 % | 113 | 43 % | 68 |
| B | toutes | 31 % | 388 | 39 % | 311 |
| V2-F O8 | apprentissage | 20 % | 223 | 30 % | 114 |
| V2-F O8 | validation | 21 % | 298 | 21 % | 80 |
| V2-F O8 | test | 19 % | 196 | 32 % | 62 |
| V2-F O8 | toutes | 20 % | 717 | 28 % | 256 |
| désaccord 30 | apprentissage | 18 % | 141 | 24 % | 78 |
| désaccord 30 | validation | 15 % | 212 | 23 % | 71 |
| désaccord 30 | test | 11 % | 201 | 22 % | 46 |
| désaccord 30 | toutes | 14 % | 554 | 23 % | 195 |
| désaccord 20 60-180 s | apprentissage | 21 % | 228 | 22 % | 82 |
| désaccord 20 60-180 s | validation | 20 % | 314 | 12 % | 51 |
| désaccord 20 60-180 s | test | 16 % | 227 | 50 % | 22 |
| désaccord 20 60-180 s | toutes | 19 % | 769 | 23 % | 155 |

Direct (vitesse.json, offre au prix encore achetable 0,25 s après le signal, cycles réglés) :

| Fantôme | Encore là : gagnés | n | Disparue : gagnés | n |
|---|---|---|---|---|
| tous | 20 % | 977 | 37 % | 235 |
| V2-F ecart qui grandit | 21 % | 203 | 33 % | 43 |
| desaccord 20 60-180 s | 16 % | 220 | 48 % | 21 |
| desaccord 30 | 15 % | 181 | 18 % | 55 |
| V2-F incertitude 0,01 % | 24 % | 148 | 48 % | 54 |
| V2-F pause memoire | 20 % | 160 | 31 % | 35 |
| V2-F miroir 1 s | 26 % | 62 | 40 % | 15 |
| desaccord 20 jeton 0,35-0,65 | 67 % | 3 | 75 % | 12 |

Lecture : quand l'offre disparaît, c'est souvent qu'un autre acheteur mieux informé (ou plus rapide) l'a prise — nous n'obtenons que les offres que personne ne voulait.

## 2. Modèles et paramètres (appris sur l'apprentissage, figés ensuite)

- Signaux d'apprentissage : 309 (A 50, B 259) ; offre encore là à 0,3 s : 149.
- Calibration (moteur B) : logistique sur logit(proba du modèle), logit(milieu Polymarket), cohorte → coefficients 0,92, 0,28, −0,02, constante −0,18.
- Moteur C : variables = logit proba calibrée, logit prix, log taille affichée, écart calibré − prix, variation du prix 1 s, variation du prix 3 s, variation de taille 1 s, variation du modèle 3 s, temps restant, volatilité Bybit 30 s, écart vendeur-acheteur, âge Bybit (ind.), âge OKX (ind.), âge Chainlink (ind.), cohorte B (âges = indicateur « dernier changement », pas l'âge vrai).

| Période | AUC P(survie) | AUC P(gain | survie) | AUC proba calibrée → gain | AUC proba du modèle → gain |
|---|---|---|---|---|
| apprentissage | 0,85 | 0,78 | 0,68 | 0,68 |
| validation | 0,82 | 0,63 | 0,64 | 0,64 |
| test | 0,76 | 0,59 | 0,69 | 0,71 |

Marge choisie sur l'apprentissage (P&L prudent d'apprentissage par marge) :

- B désaccord corrigé : **0,00** — 0,00 → +1 544 $ · 0,05 → +1 544 $ · 0,10 → +1 044 $ · 0,15 → +885 $ · 0,20 → +307 $ · 0,25 → +280 $
- C alpha exécutable : **0,01** — −0,02 → +2 322 $ · 0,00 → +2 126 $ · 0,01 → +2 384 $ · 0,02 → +2 161 $ · 0,05 → +1 836 $

## 3. Bilans par moteur et par période

Participation = ordres envoyés / signaux disponibles. Remplis = achats réellement faits (partiels inclus). Jackpots = signaux qui rapportent ≥ 4× la mise à l'exécution idéale ; « gardés » = gagnés par le moteur.

### apprentissage

| Moteur | Exécution | Signaux | Envoyés | Remplis (partiels) | Gagnés | P&L net | Δ vs A [IC 90 % blocs 1 h] | Jackpots gardés / manqués | Pire suite de pertes | Creux max |
|---|---|---|---|---|---|---|---|---|---|---|
| A désaccord brut | idéale 0 s | 309 | 309 (100 %) | 309 (190) | 41 % | +3 569 $ | — | 22 / 0 | 9 | −541 $ |
| A désaccord brut | prudente 0,3 s | 309 | 309 (100 %) | 149 (76) | 40 % | **+1 544 $** | — | 6 / 16 | 7 | −607 $ |
| A désaccord brut | pessimiste 0,6 s | 309 | 309 (100 %) | 115 (66) | 36 % | +395 $ | — | 3 / 19 | 7 | −753 $ |
| B désaccord corrigé | idéale 0 s | 309 | 309 (100 %) | 309 (190) | 41 % | +3 569 $ | +0 $ [+0 $ ; +0 $] | 22 / 0 | 9 | −541 $ |
| B désaccord corrigé | prudente 0,3 s | 309 | 309 (100 %) | 149 (76) | 40 % | **+1 544 $** | +0 $ [+0 $ ; +0 $] | 6 / 16 | 7 | −607 $ |
| B désaccord corrigé | pessimiste 0,6 s | 309 | 309 (100 %) | 115 (66) | 36 % | +395 $ | +0 $ [+0 $ ; +0 $] | 3 / 19 | 7 | −753 $ |
| C alpha exécutable | idéale 0 s | 309 | 197 (64 %) | 197 (108) | 49 % | +3 517 $ | −52 $ [−952 $ ; +740 $] | 14 / 8 | 5 | −356 $ |
| C alpha exécutable | prudente 0,3 s | 309 | 197 (64 %) | 175 (99) | 50 % | **+2 384 $** | +840 $ [−343 $ ; +1 964 $] | 10 / 12 | 10 | −463 $ |
| C alpha exécutable | pessimiste 0,6 s | 309 | 197 (64 %) | 161 (96) | 49 % | +1 140 $ | +745 $ [−381 $ ; +1 906 $] | 6 / 16 | 9 | −363 $ |

### validation

| Moteur | Exécution | Signaux | Envoyés | Remplis (partiels) | Gagnés | P&L net | Δ vs A [IC 90 % blocs 1 h] | Jackpots gardés / manqués | Pire suite de pertes | Creux max |
|---|---|---|---|---|---|---|---|---|---|---|
| A désaccord brut | idéale 0 s | 318 | 318 (100 %) | 318 (176) | 34 % | +1 662 $ | — | 26 / 0 | 12 | −964 $ |
| A désaccord brut | prudente 0,3 s | 318 | 318 (100 %) | 188 (78) | 31 % | **−401 $** | — | 11 / 15 | 11 | −1 210 $ |
| A désaccord brut | pessimiste 0,6 s | 318 | 318 (100 %) | 161 (76) | 26 % | −865 $ | — | 5 / 21 | 13 | −1 451 $ |
| B désaccord corrigé | idéale 0 s | 318 | 318 (100 %) | 318 (176) | 34 % | +1 662 $ | +0 $ [+0 $ ; +0 $] | 26 / 0 | 12 | −964 $ |
| B désaccord corrigé | prudente 0,3 s | 318 | 318 (100 %) | 188 (78) | 31 % | **−401 $** | +0 $ [+0 $ ; +0 $] | 11 / 15 | 11 | −1 210 $ |
| B désaccord corrigé | pessimiste 0,6 s | 318 | 318 (100 %) | 161 (76) | 26 % | −865 $ | +0 $ [+0 $ ; +0 $] | 5 / 21 | 13 | −1 451 $ |
| C alpha exécutable | idéale 0 s | 318 | 201 (63 %) | 201 (97) | 40 % | +1 919 $ | +257 $ [−1 184 $ ; +1 560 $] | 20 / 6 | 9 | −489 $ |
| C alpha exécutable | prudente 0,3 s | 318 | 201 (63 %) | 169 (72) | 38 % | **+132 $** | +533 $ [−686 $ ; +1 804 $] | 12 / 14 | 7 | −859 $ |
| C alpha exécutable | pessimiste 0,6 s | 318 | 201 (63 %) | 162 (79) | 37 % | −378 $ | +487 $ [−569 $ ; +1 600 $] | 10 / 16 | 7 | −974 $ |

### test

| Moteur | Exécution | Signaux | Envoyés | Remplis (partiels) | Gagnés | P&L net | Δ vs A [IC 90 % blocs 1 h] | Jackpots gardés / manqués | Pire suite de pertes | Creux max |
|---|---|---|---|---|---|---|---|---|---|---|
| A désaccord brut | idéale 0 s | 228 | 228 (100 %) | 228 (123) | 28 % | +184 $ | — | 18 / 0 | 16 | −685 $ |
| A désaccord brut | prudente 0,3 s | 228 | 228 (100 %) | 147 (62) | 20 % | **−1 664 $** | — | 10 / 8 | 19 | −1 825 $ |
| A désaccord brut | pessimiste 0,6 s | 228 | 228 (100 %) | 131 (68) | 18 % | −1 306 $ | — | 7 / 11 | 18 | −1 479 $ |
| B désaccord corrigé | idéale 0 s | 228 | 228 (100 %) | 228 (123) | 28 % | +184 $ | +0 $ [+0 $ ; +0 $] | 18 / 0 | 16 | −685 $ |
| B désaccord corrigé | prudente 0,3 s | 228 | 228 (100 %) | 147 (62) | 20 % | **−1 664 $** | +0 $ [+0 $ ; +0 $] | 10 / 8 | 19 | −1 825 $ |
| B désaccord corrigé | pessimiste 0,6 s | 228 | 228 (100 %) | 131 (68) | 18 % | −1 306 $ | +0 $ [+0 $ ; +0 $] | 7 / 11 | 18 | −1 479 $ |
| C alpha exécutable | idéale 0 s | 228 | 106 (46 %) | 106 (59) | 39 % | +891 $ | +707 $ [−531 $ ; +1 924 $] | 8 / 10 | 7 | −220 $ |
| C alpha exécutable | prudente 0,3 s | 228 | 106 (46 %) | 79 (40) | 33 % | **−495 $** | +1 169 $ [−89 $ ; +2 349 $] | 4 / 14 | 9 | −842 $ |
| C alpha exécutable | pessimiste 0,6 s | 228 | 106 (46 %) | 72 (44) | 29 % | −225 $ | +1 081 $ [+145 $ ; +1 986 $] | 4 / 14 | 8 | −442 $ |

### Par cohorte (prudente 0,3 s)

| Moteur | Cohorte | apprentissage | validation | test |
|---|---|---|---|---|
| A désaccord brut | A | +734 $ (25) | −293 $ (37) | −411 $ (34) |
| A désaccord brut | B | +810 $ (124) | −108 $ (151) | −1 253 $ (113) |
| B désaccord corrigé | A | +734 $ (25) | −293 $ (37) | −411 $ (34) |
| B désaccord corrigé | B | +810 $ (124) | −108 $ (151) | −1 253 $ (113) |
| C alpha exécutable | A | +1 172 $ (43) | −43 $ (43) | −370 $ (31) |
| C alpha exécutable | B | +1 212 $ (132) | +175 $ (126) | −126 $ (48) |

### Diagnostic : d'où vient l'écart de C ? (Δ vs A, prudente 0,3 s)

| Variante | apprentissage | validation | test |
|---|---|---|---|
| C sélection seule (limite = prix du signal) | −48 $ [−876 $ ; +642 $] | +286 $ [−825 $ ; +1 316 $] | +1 051 $ [−119 $ ; +2 133 $] |
| A + plafond de C (tout envoyer, limite = plafond) | +886 $ [+57 $ ; +1 820 $] | +175 $ [−446 $ ; +865 $] | +118 $ [−155 $ ; +429 $] |
| C alpha exécutable | +840 $ [−343 $ ; +1 964 $] | +533 $ [−686 $ ; +1 804 $] | +1 169 $ [−89 $ ; +2 349 $] |

## 4. Par jour (prudente 0,3 s, heure suisse)

| Jour | Signaux | A désaccord brut | B désaccord corrigé | C alpha exécutable |
|---|---|---|---|---|
| 07.10 | 133 | +322 $ | +322 $ | +1 247 $ |
| 08.10 | 195 | +1 104 $ | +1 104 $ | +888 $ |
| 09.10 | 202 | +237 $ | +237 $ | +295 $ |
| 10.10 | 241 | −1 895 $ | −1 895 $ | +62 $ |
| 11.10 | 84 | −290 $ | −290 $ | −472 $ |

## 5. Diagnostic : V2-F original (O8), mêmes moteurs appliqués sans réapprentissage

Les modèles B et C ont été appris sur les cohortes A et B ; on les applique tels quels aux signaux V2-F original (cohorte « B » = 0 dans les variables). Diagnostic seulement.

| Moteur | apprentissage | validation | test |
|---|---|---|---|
| A désaccord brut | +832 $ | −1 482 $ | −2 278 $ |
| B désaccord corrigé | +832 $ | −1 482 $ | −2 278 $ |
| C alpha exécutable | +185 $ | −698 $ | −114 $ |

## 6. Faire tourner le moteur C comme fantôme en direct : ce qu'il faut à l'enregistreur de Dublin (branche donnees-rapide)

Le moteur C a besoin, AU MOMENT du signal, des mêmes variables qu'ici, calculées exactement comme dans ce fichier, puis de l'issue de l'ordre :

- **À la décision (signal A ou B)** : heure locale et heure Polymarket ; côté ; meilleur vendeur et sa taille, meilleur acheteur ; vendeur et taille 1 s et 3 s avant ; probabilité du modèle (r[2] pour A, modèle 0,015 % à la date pour B) et sa valeur 3 s avant ; temps restant ; volatilité Bybit 30 s ; **âge VRAI** de Bybit, OKX, Chainlink (horodatage source, pas l'indicateur « dernier changement ») ; P(survie), P(gain|survie), valeur attendue, plafond, décision C (envoyer oui/non).
- **Après la décision** : carnet Up complet ±3 c toutes les 50 ms pendant 3 s (pour savoir si l'offre est restée, à quel prix et quelle quantité était achetable à 0,1 / 0,25 / 0,3 / 0,6 s) ; **transactions Polymarket** sur notre jeton dans ces 3 s (qui a pris l'offre : distinguer « prise par un autre acheteur » de « retirée par le vendeur ») ; carnet Down idem (miroir).
- **Fantôme C** : ordre fictif limite au plafond, envoyé au temps réel mesuré Cloudflare → Polymarket (aller-retour noté), rempli seulement si une ligne ≥ envoi + latence montre un vendeur ≤ plafond ; quantité ≤ taille affichée ; noter remplissage, prix, partiel, et l'issue officielle du cycle.
- **Volume nécessaire** : les modèles sont appris sur ~309 signaux d'apprentissage ; il faut au moins autant de signaux enregistrés à 50 ms avec âges vrais pour réapprendre P(survie) et P(gain|survie) sur les données de Dublin, puis une période de validation de taille comparable avant tout passage en réel.
