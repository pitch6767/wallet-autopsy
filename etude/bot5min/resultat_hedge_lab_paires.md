# BOT95 HEDGE LAB — paires rentables, H25 / H26, contribution marginale et audit live

Étude hors ligne du 11.10.2026 — aucun bot, aucun workflow modifié, rien publié. Complète resultat_hedge_lab.md (mêmes entrées A et B, mêmes scénarios, mêmes périodes : apprentissage < 08.10 22:00 · validation → 10.10 10:25 · test inédit après). Δ = P&L avec la couverture − P&L en gardant, sur les MÊMES positions, frais compris ; IC 90 % par blocs d'une heure. Sauf mention : version « 50 $ indépendants » (le portefeuille de 250 $ est ruiné par GARDER en prudent, voir question 6).

## Réponse courte (en tête)

- **A · désaccord 30 zone + modèle monte** (prudent) : 69/97 positions ont au moins un moment Up + Down < 1 $ (7923 lignes) ; **62/97** restent rentables tous frais compris (7372 lignes) ; marge au premier moment : médiane 1,79 c par paire. Appariable au 1er moment au meilleur niveau : médiane 51,1 % de la position (0 dans 27,4 % des cas). H25 100 % continu : Δ vs GARDER app. −762 $ [−1 571 $ ; −108 $], valid. −24 $ [−658 $ ; +533 $], test +7 $ [−607 $ ; +497 $] ; jackpots perdus valid. 5/5, test 5/5. H26 (25 %) : valid. −4 $ [−141 $ ; +128 $], test −3 $ [−152 $ ; +125 $].
- **B · V2-F corrigé 0,015 %** (prudent) : 282/369 positions ont au moins un moment Up + Down < 1 $ (49901 lignes) ; **255/369** restent rentables tous frais compris (45091 lignes) ; marge au premier moment : médiane 2,45 c par paire. Appariable au 1er moment au meilleur niveau : médiane 106,3 % de la position (0 dans 24,3 % des cas). H25 100 % continu : Δ vs GARDER app. −1 283 $ [−2 142 $ ; −436 $], valid. −988 $ [−2 185 $ ; +179 $], test +698 $ [−579 $ ; +1 935 $] ; jackpots perdus valid. 5/5, test 3/5. H26 (25 %) : valid. −245 $ [−546 $ ; +33 $], test +182 $ [−130 $ ; +496 $].
- **Mécanique** : carnets miroirs ⇒ « paire < 1 » ⇔ acheteur de notre côté > prix payé (vérifié ligne par ligne, 0 écart). Apparier = vendre la même fraction au même instant : Δ couverture − vente = 0 $ dans tous les scénarios (section 3-5), la paire bloque seulement le capital jusqu'au règlement. Verrouiller tôt coupe surtout les positions gagnantes (qui montent d'abord) : petit profit sûr contre jackpots perdus.
- **Latence** : fenêtres rentables (lignes 0,3 s) médiane 3,90 s ; encore achetables au prix vu après 0,3 s dans 73,6 % des fenêtres, après 0,6 s dans 65,2 % (section 7).
- **Capital 250 $** : une position à la fois, donc le capital bloqué ne coûte aucune entrée ; c'est la ruine par GARDER (prudent) qui limite tout (section 6).
- **Ménage des 24 fantômes** : garder H25 (remplace H01-H03, H06), H26 (remplace H04-H05), H19 en test live seulement (avec H20, H22), H23 en variante d'observation ; H07, H08, H10, H11 = ventes (miroir) ; H09, H12-H18, H21, H24 abandonnés (section 8).
- **Live** : ni le bot Cloudflare ni rapide.js n'enregistrent le carnet opposé complet après l'entrée, les transactions individuelles ni les événements d'annulation, et rapide.js n'a ni A ni B : liste exacte section 9.

## 1. Moments où Up + Down coûte < 1 $ — combien restent rentables après TOUS les frais ?

Pour chaque position (entrée du scénario), chaque ligne 0,3 s après l'entrée et ≥ 1 s avant la fin. Trois critères : **brut** a + vendeur opposé < 1 ; **marginal** a + vendeur opposé + frais preneur de l'achat opposé < 1 (frais d'entrée déjà payés, ignorés pour la décision) ; **tous frais** a + frais(a) + vendeur opposé + frais < 1 (ce qui compte dans le P&L total). a = prix d'entrée payé.

| Cohorte | Scénario | Période | Positions | avec ≥ 1 moment brut | marginal | tous frais | Lignes | lignes brut | marginal | tous frais | Écarts à « acheteur de notre côté > a » | Écarts à « acheteur − frais > a + frais(a) » |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A | idéal | apprentissage | 51 | 45 | 45 | **45** (88,2 %) | 11796 | 7122 | 6927 | **6696** | 0 | 0 |
| A | idéal | validation | 62 | 48 | 45 | **44** (71,0 %) | 14341 | 5694 | 5557 | **5384** | 0 | 0 |
| A | idéal | inédit | 47 | 35 | 34 | **33** (70,2 %) | 15309 | 5670 | 5467 | **5258** | 0 | 0 |
| A | prudent | apprentissage | 26 | 21 | 20 | **20** (76,9 %) | 5945 | 3227 | 3151 | **3090** | 0 | 0 |
| A | prudent | validation | 37 | 24 | 22 | **20** (54,1 %) | 7635 | 1518 | 1429 | **1375** | 0 | 0 |
| A | prudent | inédit | 34 | 24 | 23 | **22** (64,7 %) | 10889 | 3178 | 3027 | **2907** | 0 | 0 |
| A | pessimiste | apprentissage | 19 | 14 | 13 | **13** (68,4 %) | 4444 | 2249 | 2218 | **2189** | 0 | 0 |
| A | pessimiste | validation | 31 | 19 | 18 | **17** (54,8 %) | 6384 | 944 | 879 | **829** | 0 | 0 |
| A | pessimiste | inédit | 30 | 21 | 21 | **20** (66,7 %) | 9255 | 2332 | 2198 | **2054** | 0 | 0 |
| B | idéal | apprentissage | 238 | 213 | 208 | **203** (85,3 %) | 77982 | 37773 | 36379 | **34921** | 0 | 0 |
| B | idéal | validation | 237 | 197 | 192 | **181** (76,4 %) | 78848 | 34672 | 33673 | **32115** | 0 | 0 |
| B | idéal | inédit | 178 | 146 | 145 | **141** (79,2 %) | 74188 | 29858 | 28738 | **27389** | 0 | 0 |
| B | prudent | apprentissage | 113 | 91 | 86 | **82** (72,6 %) | 36477 | 15364 | 14500 | **13887** | 0 | 0 |
| B | prudent | validation | 144 | 108 | 105 | **95** (66,0 %) | 50000 | 21105 | 20465 | **19463** | 0 | 0 |
| B | prudent | inédit | 112 | 83 | 81 | **78** (69,6 %) | 45823 | 13432 | 12648 | **11741** | 0 | 0 |
| B | pessimiste | apprentissage | 98 | 76 | 71 | **68** (69,4 %) | 31330 | 11657 | 10847 | **10286** | 0 | 0 |
| B | pessimiste | validation | 120 | 85 | 81 | **74** (61,7 %) | 42431 | 16196 | 15614 | **14811** | 0 | 0 |
| B | pessimiste | inédit | 99 | 72 | 71 | **67** (67,7 %) | 40898 | 11680 | 10877 | **10103** | 0 | 0 |

**Équivalence miroir** : vendeur opposé = 1 − acheteur de notre côté (même taille) ⇒ a + vendeur opposé < 1 ⇔ **acheteur de notre côté > a**, et « tous frais » ⇔ acheteur − frais(acheteur) > a + frais(a) (les frais sont symétriques). Les deux dernières colonnes comptent les lignes où l'équivalence ne tient pas : 0 partout = vérifiée ligne par ligne. Une paire rentable n'existe donc QUE quand notre côté a monté au-dessus du prix payé : c'est une prise de bénéfice.

Marge nette par paire (cents, tous frais, prudent, toutes périodes) :

| Cohorte | Moments | 10 % | médiane | 90 % | moyenne | Premier moment de chaque position : n · 10 % · médiane · 90 % | Marge marginale au premier moment (sans frais d'entrée) : médiane |
|---|---|---|---|---|---|---|---|
| A | 7372 | 3,46 | 42,23 | 78,74 | 42,23 | 62 · 0,09 · 1,79 · 25,75 | 2,81 |
| B | 45091 | 3,17 | 27,14 | 65,05 | 30,93 | 255 · 0,41 · 2,45 · 18,64 | 3,61 |

## 2. Quantité réellement appariable au seul meilleur niveau

Premier moment éligible (tous frais) de chaque position ; ordre au prix vu, exécuté sur la ligne + 0,3 s (prudent, taille affichée) ou + 0,6 s (pessimiste, moitié de la taille) ; si le vendeur opposé a monté entre-temps : 0. Rapport à la taille de la position (parts d'entrée). Puis couverture obtenue en balayant tous les moments éligibles (H25 100 % continu).

| Cohorte | Scénario | Positions avec moment éligible | Appariable au 1er moment : 10 % · médiane · 90 % | 0 (prix parti) | ≥ 25 % | ≥ 50 % | ≥ 75 % | ≥ 100 % | H25 continu : couverture médiane · part à 100 % |
|---|---|---|---|---|---|---|---|---|---|
| A | prudent | 62 | 0,0 % · 51,1 % · 981,6 % | 27,4 % | 61,3 % | 50,0 % | 46,8 % | 40,3 % | 100,0 % · 88,7 % |
| A | pessimiste | 50 | 0,0 % · 9,4 % · 362,6 % | 38,0 % | 42,0 % | 40,0 % | 30,0 % | 24,0 % | 100,0 % · 82,0 % |
| B | prudent | 255 | 0,0 % · 106,3 % · 1727,0 % | 24,3 % | 64,7 % | 57,3 % | 52,2 % | 51,4 % | 100,0 % · 89,8 % |
| B | pessimiste | 209 | 0,0 % · 38,3 % · 894,8 % | 29,2 % | 56,5 % | 46,4 % | 41,1 % | 37,8 % | 100,0 % · 87,6 % |

Idéal : quantité illimitée au meilleur niveau par hypothèse (borne haute, non atteignable).

## 3-5. Couvrir SEULEMENT les paires strictement rentables (H25) : 25 / 50 / 75 / 100 %, premier moment ou balayage continu

Décision avec la seule information du moment (critère tous frais sur la ligne de décision, ordre au prix vu). « premier » = un seul essai au premier moment éligible ; « continu » = on réessaie à chaque moment éligible jusqu'à la fraction visée. Jackpots = gain ≥ 4 × la mise en gardant ; perdus = jackpots de GARDER qui ne sont plus ≥ 4 × la mise avec la variante.

### A · désaccord 30 zone + modèle monte — idéal

| Variante | Δ app. [IC 90 %] | Δ valid. [IC 90 %] | Δ test [IC 90 %] | Positions couvertes app. / valid. / test | Jackpots perdus app. / valid. / test | Profit sacrifié jackpots (valid. / test) | Profit verrouillé (valid. / test) |
|---|---|---|---|---|---|---|---|
| H25 25 % premier | −312 $ [−561 $ ; −79 $] | −253 $ [−459 $ ; −44 $] | −76 $ [−237 $ ; +64 $] | 45 / 44 / 33 | 5/9 / 6/14 / 6/8 | +293 $ / +160 $ | +112 $ / +93 $ |
| H25 25 % continu | −312 $ [−557 $ ; −68 $] | −253 $ [−471 $ ; −52 $] | −76 $ [−232 $ ; +69 $] | 45 / 44 / 33 | 5/9 / 6/14 / 6/8 | +293 $ / +160 $ | +112 $ / +93 $ |
| H25 50 % premier | −624 $ [−1 132 $ ; −142 $] | −507 $ [−949 $ ; −106 $] | −153 $ [−447 $ ; +143 $] | 45 / 44 / 33 | 8/9 / 14/14 / 7/8 | +586 $ / +320 $ | +224 $ / +187 $ |
| H25 50 % continu | −624 $ [−1 124 $ ; −134 $] | −507 $ [−933 $ ; −97 $] | −153 $ [−457 $ ; +143 $] | 45 / 44 / 33 | 8/9 / 14/14 / 7/8 | +586 $ / +320 $ | +224 $ / +187 $ |
| H25 75 % premier | −936 $ [−1 674 $ ; −247 $] | −760 $ [−1 406 $ ; −155 $] | −229 $ [−711 $ ; +204 $] | 45 / 44 / 33 | 8/9 / 14/14 / 8/8 | +880 $ / +481 $ | +336 $ / +280 $ |
| H25 75 % continu | −936 $ [−1 670 $ ; −233 $] | −760 $ [−1 418 $ ; −171 $] | −229 $ [−687 $ ; +199 $] | 45 / 44 / 33 | 8/9 / 14/14 / 8/8 | +880 $ / +481 $ | +336 $ / +280 $ |
| H25 100 % premier | −1 248 $ [−2 263 $ ; −277 $] | −1 013 $ [−1 909 $ ; −219 $] | −306 $ [−921 $ ; +270 $] | 45 / 44 / 33 | 8/9 / 14/14 / 8/8 | +1 173 $ / +641 $ | +448 $ / +373 $ |
| H25 100 % continu | −1 248 $ [−2 215 $ ; −337 $] | −1 013 $ [−1 871 $ ; −207 $] | −306 $ [−931 $ ; +276 $] | 45 / 44 / 33 | 8/9 / 14/14 / 8/8 | +1 173 $ / +641 $ | +448 $ / +373 $ |
| H26 (25 % continu, figé app.) | −312 $ [−567 $ ; −79 $] | −253 $ [−473 $ ; −49 $] | −76 $ [−230 $ ; +71 $] | 45 / 44 / 33 | 5/9 / 6/14 / 6/8 | +293 $ / +160 $ | +112 $ / +93 $ |

GARDER : apprentissage 51 positions +1 632 $ · validation 62 positions +753 $ · inédit 47 positions +273 $.

### A · désaccord 30 zone + modèle monte — prudent

| Variante | Δ app. [IC 90 %] | Δ valid. [IC 90 %] | Δ test [IC 90 %] | Positions couvertes app. / valid. / test | Jackpots perdus app. / valid. / test | Profit sacrifié jackpots (valid. / test) | Profit verrouillé (valid. / test) |
|---|---|---|---|---|---|---|---|
| H25 25 % premier | −115 $ [−264 $ ; +15 $] | −12 $ [−127 $ ; +90 $] | +71 $ [−1 $ ; +143 $] | 16 / 16 / 13 | 1/5 / 1/5 / 2/5 | +70 $ / +31 $ | +48 $ / +29 $ |
| H25 25 % continu | −191 $ [−388 $ ; −24 $] | −4 $ [−156 $ ; +123 $] | −3 $ [−154 $ ; +121 $] | 19 / 20 / 19 | 1/5 / 1/5 / 2/5 | +78 $ / +102 $ | +81 $ / +45 $ |
| H25 50 % premier | −213 $ [−504 $ ; +38 $] | +1 $ [−150 $ ; +155 $] | +123 $ [−14 $ ; +265 $] | 16 / 16 / 13 | 3/5 / 4/5 / 2/5 | +87 $ / +62 $ | +88 $ / +54 $ |
| H25 50 % continu | −382 $ [−730 $ ; −55 $] | −14 $ [−303 $ ; +253 $] | −6 $ [−305 $ ; +253 $] | 19 / 20 / 19 | 4/5 / 5/5 / 4/5 | +156 $ / +204 $ | +166 $ / +93 $ |
| H25 75 % premier | −284 $ [−697 $ ; +50 $] | +25 $ [−148 $ ; +206 $] | +181 $ [−24 $ ; +394 $] | 16 / 16 / 13 | 3/5 / 4/5 / 2/5 | +104 $ / +86 $ | +120 $ / +80 $ |
| H25 75 % continu | −573 $ [−1 147 $ ; −74 $] | −19 $ [−461 $ ; +391 $] | −5 $ [−466 $ ; +364 $] | 19 / 20 / 19 | 4/5 / 5/5 / 4/5 | +235 $ / +303 $ | +257 $ / +144 $ |
| H25 100 % premier | −320 $ [−813 $ ; +95 $] | +54 $ [−155 $ ; +263 $] | +233 $ [−40 $ ; +506 $] | 16 / 16 / 13 | 3/5 / 4/5 / 2/5 | +121 $ / +108 $ | +150 $ / +103 $ |
| H25 100 % continu | −762 $ [−1 571 $ ; −108 $] | −24 $ [−658 $ ; +533 $] | +7 $ [−607 $ ; +497 $] | 19 / 20 / 19 | 4/5 / 5/5 / 5/5 | +313 $ / +392 $ | +348 $ / +207 $ |
| H26 (25 % continu, figé app.) | −191 $ [−384 $ ; −24 $] | −4 $ [−141 $ ; +128 $] | −3 $ [−152 $ ; +125 $] | 19 / 20 / 19 | 1/5 / 1/5 / 2/5 | +78 $ / +102 $ | +81 $ / +45 $ |

GARDER : apprentissage 26 positions +946 $ · validation 37 positions −293 $ · inédit 34 positions −411 $.

### A · désaccord 30 zone + modèle monte — pessimiste

| Variante | Δ app. [IC 90 %] | Δ valid. [IC 90 %] | Δ test [IC 90 %] | Positions couvertes app. / valid. / test | Jackpots perdus app. / valid. / test | Profit sacrifié jackpots (valid. / test) | Profit verrouillé (valid. / test) |
|---|---|---|---|---|---|---|---|
| H25 25 % premier | −104 $ [−254 $ ; +17 $] | +18 $ [−16 $ ; +56 $] | +31 $ [−39 $ ; +99 $] | 10 / 12 / 8 | 1/4 / 0/3 / 1/4 | +12 $ / +32 $ | +29 $ / +22 $ |
| H25 25 % continu | −126 $ [−288 $ ; +13 $] | −23 $ [−181 $ ; +106 $] | −20 $ [−160 $ ; +109 $] | 12 / 16 / 14 | 1/4 / 0/3 / 1/4 | +81 $ / +95 $ | +82 $ / +33 $ |
| H25 50 % premier | −212 $ [−500 $ ; +35 $] | +46 $ [−12 $ ; +113 $] | +40 $ [−90 $ ; +155 $] | 10 / 12 / 9 | 3/4 / 1/3 / 1/4 | +16 $ / +63 $ | +40 $ / +40 $ |
| H25 50 % continu | −250 $ [−561 $ ; +14 $] | −44 $ [−337 $ ; +226 $] | −5 $ [−244 $ ; +211 $] | 12 / 16 / 15 | 3/4 / 2/3 / 3/4 | +159 $ / +155 $ | +168 $ / +101 $ |
| H25 75 % premier | −310 $ [−737 $ ; +48 $] | +77 $ [−4 $ ; +172 $] | +41 $ [−144 $ ; +207 $] | 10 / 12 / 9 | 3/4 / 1/3 / 1/4 | +17 $ / +91 $ | +47 $ / +53 $ |
| H25 75 % continu | −371 $ [−839 $ ; +33 $] | −69 $ [−511 $ ; +343 $] | +22 $ [−307 $ ; +336 $] | 12 / 16 / 15 | 3/4 / 3/3 / 3/4 | +236 $ / +204 $ | +249 $ / +182 $ |
| H25 100 % premier | −351 $ [−854 $ ; +70 $] | +104 $ [+6 $ ; +227 $] | +67 $ [−122 $ ; +268 $] | 10 / 12 / 9 | 3/4 / 1/3 / 2/4 | +17 $ / +92 $ | +52 $ / +65 $ |
| H25 100 % continu | −493 $ [−1 098 $ ; +78 $] | −105 $ [−737 $ ; +430 $] | +50 $ [−380 $ ; +462 $] | 12 / 16 / 15 | 3/4 / 3/3 / 4/4 | +316 $ / +252 $ | +327 $ / +263 $ |
| H26 (25 % continu, figé app.) | −126 $ [−281 $ ; +15 $] | −23 $ [−170 $ ; +106 $] | −20 $ [−160 $ ; +102 $] | 12 / 16 / 14 | 1/4 / 0/3 / 1/4 | +81 $ / +95 $ | +82 $ / +33 $ |

GARDER : apprentissage 19 positions +594 $ · validation 31 positions −182 $ · inédit 30 positions −269 $.

### B · V2-F corrigé 0,015 % — idéal

| Variante | Δ app. [IC 90 %] | Δ valid. [IC 90 %] | Δ test [IC 90 %] | Positions couvertes app. / valid. / test | Jackpots perdus app. / valid. / test | Profit sacrifié jackpots (valid. / test) | Profit verrouillé (valid. / test) |
|---|---|---|---|---|---|---|---|
| H25 25 % premier | −598 $ [−995 $ ; −217 $] | −359 $ [−779 $ ; +47 $] | +41 $ [−269 $ ; +365 $] | 201 / 180 / 141 | 1/15 / 3/11 / 4/11 | +480 $ / +147 $ | +390 $ / +278 $ |
| H25 25 % continu | −598 $ [−1 009 $ ; −211 $] | −359 $ [−772 $ ; +32 $] | +41 $ [−288 $ ; +375 $] | 201 / 180 / 141 | 1/15 / 3/11 / 4/11 | +480 $ / +147 $ | +390 $ / +278 $ |
| H25 50 % premier | −1 195 $ [−2 035 $ ; −394 $] | −718 $ [−1 583 $ ; +37 $] | +82 $ [−564 $ ; +730 $] | 201 / 181 / 141 | 7/15 / 7/11 / 5/11 | +960 $ / +294 $ | +780 $ / +557 $ |
| H25 50 % continu | −1 195 $ [−2 004 $ ; −449 $] | −718 $ [−1 542 $ ; +69 $] | +82 $ [−564 $ ; +716 $] | 201 / 181 / 141 | 7/15 / 7/11 / 5/11 | +960 $ / +294 $ | +780 $ / +557 $ |
| H25 75 % premier | −1 793 $ [−3 097 $ ; −607 $] | −1 078 $ [−2 270 $ ; +45 $] | +123 $ [−820 $ ; +1 059 $] | 201 / 181 / 141 | 12/15 / 11/11 / 9/11 | +1 440 $ / +440 $ | +1 169 $ / +835 $ |
| H25 75 % continu | −1 793 $ [−3 053 $ ; −633 $] | −1 078 $ [−2 387 $ ; +84 $] | +123 $ [−831 $ ; +1 080 $] | 201 / 181 / 141 | 12/15 / 11/11 / 9/11 | +1 440 $ / +440 $ | +1 169 $ / +835 $ |
| H25 100 % premier | −2 391 $ [−3 999 $ ; −885 $] | −1 437 $ [−3 090 $ ; +78 $] | +164 $ [−1 125 $ ; +1 525 $] | 203 / 181 / 141 | 14/15 / 11/11 / 10/11 | +1 920 $ / +587 $ | +1 559 $ / +1 114 $ |
| H25 100 % continu | −2 391 $ [−4 036 $ ; −886 $] | −1 437 $ [−3 083 $ ; +167 $] | +164 $ [−1 145 $ ; +1 469 $] | 203 / 181 / 141 | 14/15 / 11/11 / 10/11 | +1 920 $ / +587 $ | +1 559 $ / +1 114 $ |
| H26 (25 % continu, figé app.) | −598 $ [−1 016 $ ; −220 $] | −359 $ [−785 $ ; +45 $] | +41 $ [−272 $ ; +374 $] | 201 / 180 / 141 | 1/15 / 3/11 / 4/11 | +480 $ / +147 $ | +390 $ / +278 $ |

GARDER : apprentissage 238 positions +2 191 $ · validation 237 positions +926 $ · inédit 178 positions −304 $.

### B · V2-F corrigé 0,015 % — prudent

| Variante | Δ app. [IC 90 %] | Δ valid. [IC 90 %] | Δ test [IC 90 %] | Positions couvertes app. / valid. / test | Jackpots perdus app. / valid. / test | Profit sacrifié jackpots (valid. / test) | Profit verrouillé (valid. / test) |
|---|---|---|---|---|---|---|---|
| H25 25 % premier | −286 $ [−504 $ ; −90 $] | −152 $ [−400 $ ; +88 $] | +132 $ [−127 $ ; +363 $] | 57 / 79 / 56 | 1/3 / 0/5 / 2/5 | +132 $ / +93 $ | +183 $ / +110 $ |
| H25 25 % continu | −317 $ [−532 $ ; −104 $] | −245 $ [−539 $ ; +42 $] | +182 $ [−128 $ ; +502 $] | 75 / 90 / 69 | 1/3 / 0/5 / 2/5 | +264 $ / +96 $ | +260 $ / +179 $ |
| H25 50 % premier | −536 $ [−951 $ ; −145 $] | −268 $ [−726 $ ; +172 $] | +193 $ [−274 $ ; +631 $] | 57 / 80 / 56 | 2/3 / 1/5 / 2/5 | +200 $ / +173 $ | +324 $ / +179 $ |
| H25 50 % continu | −637 $ [−1 109 $ ; −204 $] | −495 $ [−1 081 $ ; +84 $] | +352 $ [−250 $ ; +964 $] | 75 / 91 / 69 | 2/3 / 3/5 / 2/5 | +525 $ / +190 $ | +517 $ / +383 $ |
| H25 75 % premier | −706 $ [−1 332 $ ; −140 $] | −329 $ [−921 $ ; +304 $] | +307 $ [−261 $ ; +849 $] | 57 / 80 / 56 | 3/3 / 2/5 / 2/5 | +268 $ / +199 $ | +440 $ / +231 $ |
| H25 75 % continu | −960 $ [−1 646 $ ; −367 $] | −741 $ [−1 601 $ ; +138 $] | +524 $ [−368 $ ; +1 446 $] | 75 / 91 / 69 | 3/3 / 4/5 / 2/5 | +786 $ / +284 $ | +776 $ / +594 $ |
| H25 100 % premier | −814 $ [−1 531 $ ; −110 $] | −354 $ [−1 171 $ ; +426 $] | +443 $ [−208 $ ; +1 082 $] | 57 / 80 / 56 | 3/3 / 2/5 / 2/5 | +335 $ / +199 $ | +549 $ / +282 $ |
| H25 100 % continu | −1 283 $ [−2 142 $ ; −436 $] | −988 $ [−2 185 $ ; +179 $] | +698 $ [−579 $ ; +1 935 $] | 75 / 91 / 69 | 3/3 / 5/5 / 3/5 | +1 048 $ / +373 $ | +1 034 $ / +809 $ |
| H26 (25 % continu, figé app.) | −317 $ [−545 $ ; −108 $] | −245 $ [−546 $ ; +33 $] | +182 $ [−130 $ ; +496 $] | 75 / 90 / 69 | 1/3 / 0/5 / 2/5 | +264 $ / +96 $ | +260 $ / +179 $ |

GARDER : apprentissage 113 positions +460 $ · validation 144 positions −70 $ · inédit 112 positions −1 583 $.

### B · V2-F corrigé 0,015 % — pessimiste

| Variante | Δ app. [IC 90 %] | Δ valid. [IC 90 %] | Δ test [IC 90 %] | Positions couvertes app. / valid. / test | Jackpots perdus app. / valid. / test | Profit sacrifié jackpots (valid. / test) | Profit verrouillé (valid. / test) |
|---|---|---|---|---|---|---|---|
| H25 25 % premier | −192 $ [−357 $ ; −43 $] | −48 $ [−241 $ ; +132 $] | +166 $ [+26 $ ; +308 $] | 39 / 61 / 41 | 1/2 / 0/4 / 2/3 | +81 $ / +45 $ | +132 $ / +88 $ |
| H25 25 % continu | −148 $ [−345 $ ; +31 $] | −50 $ [−285 $ ; +161 $] | +124 $ [−106 $ ; +367 $] | 56 / 70 / 57 | 1/2 / 0/4 / 2/3 | +143 $ / +45 $ | +180 $ / +150 $ |
| H25 50 % premier | −343 $ [−649 $ ; −53 $] | −57 $ [−427 $ ; +298 $] | +296 $ [+63 $ ; +537 $] | 43 / 62 / 43 | 1/2 / 2/4 / 2/3 | +156 $ / +58 $ | +225 $ / +137 $ |
| H25 50 % continu | −300 $ [−682 $ ; +46 $] | −102 $ [−561 $ ; +336 $] | +254 $ [−197 $ ; +742 $] | 60 / 71 / 59 | 1/2 / 3/4 / 2/3 | +286 $ / +86 $ | +358 $ / +312 $ |
| H25 75 % premier | −420 $ [−823 $ ; −50 $] | −23 $ [−513 $ ; +471 $] | +386 $ [+113 $ ; +690 $] | 43 / 62 / 43 | 1/2 / 2/4 / 2/3 | +223 $ / +59 $ | +307 $ / +163 $ |
| H25 75 % continu | −452 $ [−1 007 $ ; +83 $] | −155 $ [−816 $ ; +463 $] | +390 $ [−304 $ ; +1 107 $] | 60 / 71 / 59 | 2/2 / 3/4 / 2/3 | +429 $ / +124 $ | +536 $ / +483 $ |
| H25 100 % premier | −511 $ [−1 032 $ ; −52 $] | +16 $ [−625 $ ; +631 $] | +469 $ [+130 $ ; +824 $] | 43 / 62 / 43 | 1/2 / 2/4 / 3/3 | +258 $ / +59 $ | +382 $ / +179 $ |
| H25 100 % continu | −596 $ [−1 339 $ ; +128 $] | −215 $ [−1 151 $ ; +654 $] | +521 $ [−397 $ ; +1 452 $] | 60 / 71 / 59 | 2/2 / 4/4 / 3/3 | +573 $ / +162 $ | +716 $ / +662 $ |
| H26 (25 % continu, figé app.) | −148 $ [−343 $ ; +29 $] | −50 $ [−269 $ ; +169 $] | +124 $ [−111 $ ; +343 $] | 56 / 70 / 57 | 1/2 / 0/4 / 2/3 | +143 $ / +45 $ | +180 $ / +150 $ |

GARDER : apprentissage 98 positions −40 $ · validation 120 positions −593 $ · inédit 99 positions −1 304 $.

H26 : fraction choisie sur l'apprentissage (prudent, Σ P&L, 25 / 50 / 75 %) puis figée : A → 25 % (25 % : +755 $, 50 % : +564 $, 75 % : +373 $) · B → 25 % (25 % : +143 $, 50 % : −177 $, 75 % : −500 $).

### H25 / H26 contre VENTE de la même fraction au même moment (mêmes lignes, même règle)

Différence de P&L attendue : 0 (miroir) ; seule différence : le capital reste immobilisé jusqu'au règlement avec la paire, il revient tout de suite avec la vente.

| Cohorte | Variante | Scénario | Δ P&L couverture − vente (app. / valid. / test) | Capital immobilisé max : couverture / vente | Capital immobilisé moyen à la fin du cycle (valid.) : couverture / vente |
|---|---|---|---|---|---|
| A | H25 100 % continu | idéal | +0 $ / −0 $ / +0 $ | +50 $ / +50 $ | +95 $ / +11 $ |
| A | H25 100 % continu | prudent | +0 $ / +0 $ / +0 $ | +314 $ / +50 $ | +79 $ / +18 $ |
| A | H25 100 % continu | pessimiste | −0 $ / +0 $ / +0 $ | +314 $ / +50 $ | +84 $ / +20 $ |
| A | H25 50 % continu | idéal | +0 $ / −0 $ / +0 $ | +50 $ / +50 $ | +63 $ / +21 $ |
| A | H25 50 % continu | prudent | +0 $ / −0 $ / +0 $ | +182 $ / +50 $ | +57 $ / +25 $ |
| A | H25 50 % continu | pessimiste | +0 $ / +0 $ / +0 $ | +182 $ / +50 $ | +60 $ / +27 $ |
| A | H26 | idéal | +0 $ / +0 $ / +0 $ | +50 $ / +50 $ | +47 $ / +26 $ |
| A | H26 | prudent | +0 $ / −0 $ / +0 $ | +116 $ / +50 $ | +45 $ / +29 $ |
| A | H26 | pessimiste | +0 $ / +0 $ / +0 $ | +116 $ / +50 $ | +47 $ / +31 $ |
| B | H25 100 % continu | idéal | +0 $ / +0 $ / −0 $ | +50 $ / +50 $ | +90 $ / +9 $ |
| B | H25 100 % continu | prudent | +0 $ / +0 $ / −0 $ | +475 $ / +50 $ | +89 $ / +16 $ |
| B | H25 100 % continu | pessimiste | +0 $ / +0 $ / +0 $ | +640 $ / +50 $ | +84 $ / +14 $ |
| B | H25 50 % continu | idéal | +0 $ / −0 $ / −0 $ | +50 $ / +50 $ | +60 $ / +20 $ |
| B | H25 50 % continu | prudent | +0 $ / +0 $ / −0 $ | +261 $ / +50 $ | +63 $ / +26 $ |
| B | H25 50 % continu | pessimiste | +0 $ / −0 $ / −0 $ | +343 $ / +50 $ | +59 $ / +24 $ |
| B | H26 | idéal | +0 $ / −0 $ / +0 $ | +50 $ / +50 $ | +45 $ / +25 $ |
| B | H26 | prudent | +0 $ / −0 $ / +0 $ | +153 $ / +50 $ | +50 $ / +32 $ |
| B | H26 | pessimiste | +0 $ / −0 $ / +0 $ | +195 $ / +50 $ | +47 $ / +29 $ |

Idéal : la fusion Up + Down rend le capital tout de suite (hypothèse), d'où un capital immobilisé égal à celui de la vente.

## 6. Avec 250 $ partagés (chronologique, entrées ≤ 50 $) : quelle part du profit verrouillé est atteignable ?

Profit verrouillé = Σ des paires formées × (1 − coût unitaire des deux jambes, frais compris). « Part atteignable » = profit verrouillé dans le portefeuille 250 $ / profit verrouillé en 50 $ indépendants.

| Cohorte | Variante | Scénario | Période | Verrouillé 50 $ indép. | Verrouillé 250 $ | Part atteignable | P&L 250 $ (GARDER) | P&L 250 $ (variante) | Positions jouées / refusées faute de capital (variante) | Capital immobilisé max (250 $) |
|---|---|---|---|---|---|---|---|---|---|---|
| A | H25 100 % continu | idéal | validation | +448 $ | +489 $ | 109,1 % | +753 $ | −219 $ | 62 / 0 | +50 $ |
| A | H25 100 % continu | idéal | inédit | +373 $ | +370 $ | 99,0 % | +273 $ | −36 $ | 47 / 0 | +50 $ |
| A | H25 100 % continu | prudent | validation | +348 $ | +317 $ | 91,1 % | −250 $ | −142 $ | 37 / 0 | +203 $ |
| A | H25 100 % continu | prudent | inédit | +207 $ | +84 $ | 40,9 % | −250 $ | −250 $ | 25 / 15 | +248 $ |
| A | H25 100 % continu | pessimiste | validation | +327 $ | +297 $ | 90,7 % | −182 $ | −107 $ | 31 / 0 | +218 $ |
| A | H25 100 % continu | pessimiste | inédit | +263 $ | +35 $ | 13,3 % | −250 $ | −250 $ | 9 / 37 | +248 $ |
| A | H26 | idéal | validation | +112 $ | +112 $ | 100,0 % | +753 $ | +500 $ | 62 / 0 | +50 $ |
| A | H26 | idéal | inédit | +93 $ | +93 $ | 100,0 % | +273 $ | +197 $ | 47 / 0 | +50 $ |
| A | H26 | prudent | validation | +81 $ | +71 $ | 87,6 % | −250 $ | −250 $ | 34 / 4 | +95 $ |
| A | H26 | prudent | inédit | +45 $ | +31 $ | 69,4 % | −250 $ | −250 $ | 29 / 7 | +109 $ |
| A | H26 | pessimiste | validation | +82 $ | +79 $ | 96,8 % | −182 $ | −169 $ | 31 / 0 | +99 $ |
| A | H26 | pessimiste | inédit | +33 $ | +9 $ | 26,8 % | −250 $ | −250 $ | 9 / 37 | +100 $ |
| B | H25 100 % continu | idéal | validation | +1 559 $ | +1 319 $ | 84,6 % | +926 $ | −250 $ | 195 / 43 | +50 $ |
| B | H25 100 % continu | idéal | inédit | +1 114 $ | +1 201 $ | 107,8 % | −250 $ | −53 $ | 178 / 0 | +50 $ |
| B | H25 100 % continu | prudent | validation | +1 034 $ | +448 $ | 43,3 % | −250 $ | −250 $ | 62 / 132 | +290 $ |
| B | H25 100 % continu | prudent | inédit | +809 $ | +182 $ | 22,6 % | −250 $ | −250 $ | 21 / 140 | +150 $ |
| B | H25 100 % continu | pessimiste | validation | +716 $ | +378 $ | 52,8 % | −250 $ | −250 $ | 56 / 127 | +269 $ |
| B | H25 100 % continu | pessimiste | inédit | +662 $ | +260 $ | 39,2 % | −250 $ | −250 $ | 45 / 89 | +203 $ |
| B | H26 | idéal | validation | +390 $ | +390 $ | 100,0 % | +926 $ | +567 $ | 237 / 0 | +50 $ |
| B | H26 | idéal | inédit | +278 $ | +78 $ | 27,9 % | −250 $ | −250 $ | 38 / 140 | +50 $ |
| B | H26 | prudent | validation | +260 $ | +240 $ | 92,2 % | −250 $ | −250 $ | 137 / 7 | +151 $ |
| B | H26 | prudent | inédit | +179 $ | +44 $ | 24,6 % | −250 $ | −250 $ | 17 / 144 | +113 $ |
| B | H26 | pessimiste | validation | +180 $ | +105 $ | 58,1 % | −250 $ | −250 $ | 65 / 96 | +141 $ |
| B | H26 | pessimiste | inédit | +150 $ | +43 $ | 28,6 % | −250 $ | −250 $ | 19 / 141 | +87 $ |

Une seule position est ouverte à la fois (un signal par cycle, cycles successifs) : l'immobilisation du capital par la paire ne bloque jamais une AUTRE entrée ; ce qui limite le profit atteignable est la **ruine** du portefeuille par les pertes des positions non couvertes, pas le capital bloqué.

## 7. Les fenêtres de paire rentable durent-elles assez pour la latence réelle ?

Fenêtre = suite ininterrompue de lignes où la paire est rentable tous frais compris (entrées du scénario prudent). Durée = jusqu'à la première ligne où elle ne l'est plus. « Encore là » = critère toujours vrai sur la première ligne ≥ début + délai ; « encore achetable » = en plus, vendeur opposé ≤ prix vu au début (l'ordre au prix vu passe).

| Cohorte | Source | Fenêtres | Durée (s) : 10 % · médiane · 90 % | Durée (lignes) : médiane · 90 % | Fenêtres d'une seule ligne | Encore là après 0,3 s | encore achetable 0,3 s | Encore là après 0,6 s | encore achetable 0,6 s |
|---|---|---|---|---|---|---|---|---|---|
| A | lignes 0,3 s | 139 | 0,30 · 2,40 · 47,82 | 8,00 · 153,40 | 14,4 % | 85,6 % | 71,2 % | 77,0 % | 62,6 % |
| A | photos 100 ms (fenêtres entières dans la photo) | 1 | 7,30 · 7,30 · 7,30 | — | — | 100,0 % | 100,0 % | 100,0 % | 100,0 % |
| B | lignes 0,3 s | 652 | 0,30 · 4,50 · 70,44 | 15,00 · 229,60 | 13,0 % | 86,7 % | 74,1 % | 80,1 % | 65,8 % |
| B | photos 100 ms (fenêtres entières dans la photo) | 16 | 0,15 · 0,95 · 4,45 | — | — | 75,0 % | 68,8 % | 62,5 % | 56,2 % |

Les photos 100 ms ne couvrent que ~20 s autour du premier désaccord de chaque cycle (souvent juste après l'entrée) : petit échantillon, mais à la bonne résolution. Une fenêtre plus courte qu'une ligne (0,3 s) est invisible dans les lignes.

## Tableau principal — contribution marginale de chaque couverture (Δ P&L vs GARDER, mêmes positions, frais + latence)

Prudent = scénario principal ; idéal (borne haute) et pessimiste donnés. 50 $ indépendants (le capital bloqué par la paire ne gêne aucune autre entrée : une position à la fois) ; dernière colonne : même Δ dans le portefeuille 250 $ (dominé par la ruine). Jackpots perdus = validation + test, prudent.

### A · désaccord 30 zone + modèle monte

| Couverture | Prudent app. | Prudent valid. [IC 90 %] | Prudent test [IC 90 %] | Idéal valid. / test | Pessimiste valid. / test | Jackpots perdus (valid. + test) | Profit sacrifié jackpots | Capital immobilisé max | Δ 250 $ valid. / test |
|---|---|---|---|---|---|---|---|---|---|
| H01 verrouillage paire complète (coût < 1) | −762 $ | −24 $ [−633 $ ; +522 $] | +7 $ [−593 $ ; +510 $] | −1 013 $ / −306 $ | −105 $ / +50 $ | 10/10 | +705 $ | +295 $ | +108 $ / +0 $ |
| H02 verrouillage partiel 25 % | −191 $ | −4 $ [−146 $ ; +129 $] | −3 $ [−144 $ ; +125 $] | −253 $ / −76 $ | −23 $ / −20 $ | 3/10 | +180 $ | +113 $ | −0 $ / +0 $ |
| H03 verrouillage partiel 50 % | −382 $ | −14 $ [−311 $ ; +264 $] | −6 $ [−313 $ ; +251 $] | −507 $ / −153 $ | −44 $ / −5 $ | 9/10 | +360 $ | +175 $ | +0 $ / −0 $ |
| H04 plancher de profit (les 2 issues ≥ 0) | −618 $ | −60 $ [−517 $ ; +330 $] | −35 $ [−533 $ ; +399 $] | −747 $ / −265 $ | −105 $ / +5 $ | 6/10 | +535 $ | +272 $ | +0 $ / −0 $ |
| H05 réserve jackpot (≥ 70 % gardé) | −236 $ | −27 $ [−218 $ ; +150 $] | +0 $ [−196 $ ; +164 $] | −360 $ / −130 $ | −48 $ / −21 $ | 9/10 | +241 $ | +128 $ | −0 $ / +0 $ |
| H06 échelle de paires (4 tranches) | −704 $ | −42 $ [−596 $ ; +494 $] | +39 $ [−477 $ ; +482 $] | −984 $ / −240 $ | −144 $ / +39 $ | 10/10 | +563 $ | +278 $ | +108 $ / −0 $ |
| H07 pire perte limitée à −25 $ | −504 $ | −391 $ [−1 082 $ ; +152 $] | −182 $ [−797 $ ; +311 $] | −410 $ / −49 $ | −308 $ / −187 $ | 2/10 | +592 $ | +368 $ | +0 $ / +0 $ |
| H08 pire perte limitée à −10 $ | −562 $ | −143 $ [−825 $ ; +421 $] | +152 $ [−454 $ ; +731 $] | −502 $ / −235 $ | −133 $ / +25 $ | 3/10 | +645 $ | +355 $ | +0 $ / +158 $ |
| H09 pire issue à 0 dans le budget (après modèle −10) | −284 $ | +5 $ [−100 $ ; +110 $] | −5 $ [−15 $ ; +0 $] | +73 $ / +8 $ | +12 $ / +0 $ | 0/10 | +5 $ | +216 $ | −0 $ / −0 $ |
| H10 couvrir ou vendre (avantage net) | −323 $ | −35 $ [−308 $ ; +142 $] | −28 $ [−111 $ ; +22 $] | +222 $ / −101 $ | −36 $ / +6 $ | 1/10 | +41 $ | +50 $ | +0 $ / +0 $ |
| H11 alerte précoce (2 signaux sur 3) 25 % | −128 $ | −78 $ [−232 $ ; +48 $] | +31 $ [−6 $ ; +70 $] | −170 $ / +42 $ | −78 $ / +29 $ | 3/10 | +107 $ | +127 $ | +0 $ / +0 $ |
| H12 horloge de risque (immédiat / attendre 3 s) | −323 $ | −55 $ [−360 $ ; +137 $] | −28 $ [−110 $ ; +22 $] | +185 $ / −101 $ | −38 $ / +6 $ | 1/10 | +41 $ | +361 $ | +1 $ / +1 $ |
| H13 prédictive 1 s | −323 $ | −35 $ [−311 $ ; +138 $] | −28 $ [−107 $ ; +22 $] | +222 $ / −101 $ | −36 $ / +6 $ | 1/10 | +41 $ | +361 $ | +1 $ / +1 $ |
| H14 prédictive 3 s | −323 $ | −48 $ [−354 $ ; +141 $] | −32 $ [−115 $ ; +15 $] | +163 $ / −106 $ | −36 $ / +6 $ | 1/10 | +41 $ | +361 $ | +1 $ / +0 $ |
| H15 prédictive 5 s | −323 $ | −37 $ [−314 $ ; +140 $] | −28 $ [−113 $ ; +22 $] | +217 $ / −132 $ | −36 $ / +6 $ | 1/10 | +41 $ | +361 $ | +0 $ / +1 $ |
| H16 prédictive 10 s | −323 $ | −35 $ [−315 $ ; +144 $] | −28 $ [−113 $ ; +22 $] | +220 $ / −101 $ | −36 $ / +6 $ | 1/10 | +41 $ | +361 $ | +1 $ / +1 $ |
| H17 premier passage (limite si EV > immédiat) | −323 $ | −35 $ [−322 $ ; +138 $] | −28 $ [−110 $ ; +22 $] | +222 $ / −101 $ | −36 $ / +6 $ | 1/10 | +41 $ | +361 $ | +1 $ / +1 $ |
| H18 fenêtre de conversion prédite (paire ≤ 0,95) — inactive si seuil appris = jamais | +0 $ | +0 $ [+0 $ ; +0 $] | +0 $ [+0 $ ; +0 $] | −0 $ / +0 $ | +0 $ / +0 $ | 0/10 | +0 $ | +50 $ | −0 $ / +0 $ |
| H19 sauvetage passif (vendeur − 1 c, 10 s) | +0 $ | −142 $ [−434 $ ; +9 $] | −31 $ [−103 $ ; +18 $] | −77 $ / −158 $ | −120 $ / +2 $ | 1/10 | +40 $ | +263 $ | +0 $ / +0 $ |
| H20 prédicteur de file (traversée) passif sinon immédiat | −323 $ | −37 $ [−325 $ ; +137 $] | −28 $ [−113 $ ; +22 $] | +224 $ / −101 $ | −38 $ / +6 $ | 1/10 | +41 $ | +361 $ | +0 $ / +1 $ |
| H21 recharge du carnet | −324 $ | −47 $ [−311 $ ; +131 $] | −30 $ [−116 $ ; +20 $] | +119 $ / −79 $ | −41 $ / +4 $ | 1/10 | +41 $ | +361 $ | +1 $ / +0 $ |
| H22 hybride 50 % immédiat + 50 % passif | −325 $ | −56 $ [−340 $ ; +122 $] | −29 $ [−110 $ ; +21 $] | +137 $ / −124 $ | −49 $ / +5 $ | 1/10 | +41 $ | +361 $ | +1 $ / +0 $ |
| H23 boomerang (revente de l'opposé +5 c) | −809 $ | −24 $ [−207 $ ; +134 $] | −166 $ [−650 $ ; +163 $] | −699 $ / +24 $ | +11 $ / −140 $ | 7/10 | +340 $ | +295 $ | +0 $ / −0 $ |
| H24 moteur d'inventaire deux jambes | +43 $ | +112 $ [−54 $ ; +291 $] | −30 $ [−127 $ ; +64 $] | −63 $ / −89 $ | +62 $ / −78 $ | 5/10 | −33 $ | +100 $ | +69 $ / +0 $ |
| H25 25 % premier | −115 $ | −12 $ [−127 $ ; +90 $] | +71 $ [−1 $ ; +143 $] | −253 $ / −76 $ | +18 $ / +31 $ | 3/10 | +102 $ | +107 $ | +0 $ / −0 $ |
| H25 25 % continu | −191 $ | −4 $ [−156 $ ; +123 $] | −3 $ [−154 $ ; +121 $] | −253 $ / −76 $ | −23 $ / −20 $ | 3/10 | +180 $ | +113 $ | −0 $ / +0 $ |
| H25 50 % premier | −213 $ | +1 $ [−150 $ ; +155 $] | +123 $ [−14 $ ; +265 $] | −507 $ / −153 $ | +46 $ / +40 $ | 6/10 | +149 $ | +164 $ | +0 $ / +0 $ |
| H25 50 % continu | −382 $ | −14 $ [−303 $ ; +253 $] | −6 $ [−305 $ ; +253 $] | −507 $ / −153 $ | −44 $ / −5 $ | 9/10 | +360 $ | +175 $ | +0 $ / −0 $ |
| H25 75 % premier | −284 $ | +25 $ [−148 $ ; +206 $] | +181 $ [−24 $ ; +394 $] | −760 $ / −229 $ | +77 $ / +41 $ | 6/10 | +190 $ | +221 $ | −0 $ / −0 $ |
| H25 75 % continu | −573 $ | −19 $ [−461 $ ; +391 $] | −5 $ [−466 $ ; +364 $] | −760 $ / −229 $ | −69 $ / +22 $ | 9/10 | +538 $ | +235 $ | +56 $ / −0 $ |
| H25 100 % premier | −320 $ | +54 $ [−155 $ ; +263 $] | +233 $ [−40 $ ; +506 $] | −1 013 $ / −306 $ | +104 $ / +67 $ | 6/10 | +229 $ | +278 $ | +0 $ / −0 $ |
| H25 100 % continu | −762 $ | −24 $ [−658 $ ; +533 $] | +7 $ [−607 $ ; +497 $] | −1 013 $ / −306 $ | −105 $ / +50 $ | 10/10 | +705 $ | +295 $ | +108 $ / +0 $ |
| H26 préservation du jackpot (fraction figée app.) (25 %) | −191 $ | −4 $ [−141 $ ; +128 $] | −3 $ [−152 $ ; +125 $] | −253 $ / −76 $ | −23 $ / −20 $ | 3/10 | +180 $ | +113 $ | −0 $ / +0 $ |

GARDER prudent : app. +946 $ · valid. −293 $ (37 positions) · test −411 $ (34).

### B · V2-F corrigé 0,015 %

| Couverture | Prudent app. | Prudent valid. [IC 90 %] | Prudent test [IC 90 %] | Idéal valid. / test | Pessimiste valid. / test | Jackpots perdus (valid. + test) | Profit sacrifié jackpots | Capital immobilisé max | Δ 250 $ valid. / test |
|---|---|---|---|---|---|---|---|---|---|
| H01 verrouillage paire complète (coût < 1) | −1 283 $ | −988 $ [−2 195 $ ; +111 $] | +698 $ [−497 $ ; +1 905 $] | −1 437 $ / +164 $ | −215 $ / +521 $ | 8/10 | +1 421 $ | +465 $ | −0 $ / +0 $ |
| H02 verrouillage partiel 25 % | −317 $ | −245 $ [−547 $ ; +41 $] | +182 $ [−108 $ ; +499 $] | −359 $ / +41 $ | −50 $ / +124 $ | 2/10 | +360 $ | +153 $ | −0 $ / +0 $ |
| H03 verrouillage partiel 50 % | −637 $ | −495 $ [−1 062 $ ; +60 $] | +352 $ [−257 $ ; +1 018 $] | −718 $ / +82 $ | −102 $ / +254 $ | 5/10 | +715 $ | +257 $ | −0 $ / −0 $ |
| H04 plancher de profit (les 2 issues ≥ 0) | −1 068 $ | −598 $ [−1 428 $ ; +249 $] | +519 $ [−540 $ ; +1 554 $] | −1 145 $ / +205 $ | −68 $ / +300 $ | 5/10 | +879 $ | +430 $ | −0 $ / −0 $ |
| H05 réserve jackpot (≥ 70 % gardé) | −443 $ | −304 $ [−727 $ ; +81 $] | +244 $ [−145 $ ; +638 $] | −515 $ / −18 $ | −71 $ / +176 $ | 2/10 | +475 $ | +177 $ | −0 $ / +0 $ |
| H06 échelle de paires (4 tranches) | −1 188 $ | −965 $ [−2 171 $ ; +57 $] | +822 $ [−269 $ ; +1 976 $] | −1 312 $ / +168 $ | −377 $ / +566 $ | 8/10 | +1 406 $ | +368 $ | −0 $ / +0 $ |
| H07 pire perte limitée à −25 $ | −568 $ | −764 $ [−1 867 $ ; +289 $] | +264 $ [−567 $ ; +995 $] | −907 $ / +15 $ | −575 $ / +299 $ | 2/10 | +684 $ | +960 $ | +0 $ / −0 $ |
| H08 pire perte limitée à −10 $ | −768 $ | −506 $ [−1 759 $ ; +730 $] | +475 $ [−563 $ ; +1 534 $] | −921 $ / +113 $ | −62 $ / +524 $ | 4/10 | +1 104 $ | +943 $ | +0 $ / +0 $ |
| H09 pire issue à 0 dans le budget (après modèle −10) | −965 $ | −510 $ [−1 087 $ ; +53 $] | +611 $ [+172 $ ; +1 062 $] | −946 $ / +810 $ | −326 $ / +391 $ | 2/10 | +451 $ | +355 $ | +0 $ / −0 $ |
| H10 couvrir ou vendre (avantage net) | −997 $ | −954 $ [−2 110 $ ; +133 $] | +902 $ [+364 $ ; +1 445 $] | −666 $ / +1 248 $ | −602 $ / +870 $ | 3/10 | +843 $ | +50 $ | −0 $ / −0 $ |
| H11 alerte précoce (2 signaux sur 3) 25 % | −287 $ | −242 $ [−548 $ ; +57 $] | −8 $ [−230 $ ; +223 $] | −168 $ / +26 $ | −123 $ / +37 $ | 1/10 | +329 $ | +166 $ | +0 $ / −0 $ |
| H12 horloge de risque (immédiat / attendre 3 s) | −896 $ | −914 $ [−2 084 $ ; +248 $] | +890 $ [+389 $ ; +1 409 $] | −941 $ / +1 220 $ | −614 $ / +815 $ | 3/10 | +860 $ | +489 $ | −0 $ / +0 $ |
| H13 prédictive 1 s | −997 $ | −954 $ [−2 193 $ ; +156 $] | +905 $ [+325 $ ; +1 426 $] | −649 $ / +1 264 $ | −602 $ / +869 $ | 3/10 | +843 $ | +489 $ | −0 $ / +0 $ |
| H14 prédictive 3 s | −979 $ | −887 $ [−2 108 $ ; +311 $] | +930 $ [+416 $ ; +1 411 $] | −1 042 $ / +989 $ | −615 $ / +830 $ | 3/10 | +853 $ | +493 $ | −0 $ / +0 $ |
| H15 prédictive 5 s | −1 034 $ | −949 $ [−2 135 $ ; +135 $] | +906 $ [+362 $ ; +1 427 $] | −731 $ / +1 093 $ | −618 $ / +876 $ | 3/10 | +843 $ | +489 $ | −0 $ / +0 $ |
| H16 prédictive 10 s | −974 $ | −921 $ [−2 090 $ ; +200 $] | +901 $ [+344 $ ; +1 426 $] | −655 $ / +1 281 $ | −598 $ / +867 $ | 3/10 | +843 $ | +489 $ | −0 $ / +0 $ |
| H17 premier passage (limite si EV > immédiat) | −987 $ | −948 $ [−2 175 $ ; +232 $] | +908 $ [+374 $ ; +1 447 $] | −648 $ / +1 252 $ | −602 $ / +873 $ | 3/10 | +843 $ | +489 $ | −0 $ / +0 $ |
| H18 fenêtre de conversion prédite (paire ≤ 0,95) — inactive si seuil appris = jamais | +0 $ | +0 $ [+0 $ ; +0 $] | +0 $ [+0 $ ; +0 $] | −0 $ / +0 $ | −0 $ / +0 $ | 0/10 | +0 $ | +50 $ | +0 $ / −0 $ |
| H19 sauvetage passif (vendeur − 1 c, 10 s) | −656 $ | −373 $ [−1 127 $ ; +321 $] | +34 $ [−439 $ ; +459 $] | −858 $ / −56 $ | −9 $ / −16 $ | 2/10 | +507 $ | +379 $ | +0 $ / −0 $ |
| H20 prédicteur de file (traversée) passif sinon immédiat | −989 $ | −961 $ [−2 043 $ ; +114 $] | +916 $ [+352 $ ; +1 445 $] | −696 $ / +1 141 $ | −636 $ / +877 $ | 3/10 | +843 $ | +489 $ | +0 $ / +0 $ |
| H21 recharge du carnet | −986 $ | −833 $ [−2 062 $ ; +314 $] | +843 $ [+327 $ ; +1 366 $] | −875 $ / +1 100 $ | −638 $ / +844 $ | 2/10 | +774 $ | +498 $ | −0 $ / +0 $ |
| H22 hybride 50 % immédiat + 50 % passif | −1 087 $ | −1 009 $ [−2 216 $ ; +93 $] | +854 $ [+321 $ ; +1 389 $] | −1 053 $ / +942 $ | −632 $ / +796 $ | 3/10 | +840 $ | +491 $ | −0 $ / −0 $ |
| H23 boomerang (revente de l'opposé +5 c) | −444 $ | −364 $ [−1 016 $ ; +207 $] | +280 $ [+30 $ ; +544 $] | −1 494 $ / −205 $ | −96 $ / +176 $ | 2/10 | +207 $ | +465 $ | +0 $ / −0 $ |
| H24 moteur d'inventaire deux jambes | −293 $ | −288 $ [−780 $ ; +198 $] | −56 $ [−367 $ ; +253 $] | −461 $ / −311 $ | −245 $ / −97 $ | 1/10 | +151 $ | +100 $ | −0 $ / −0 $ |
| H25 25 % premier | −286 $ | −152 $ [−400 $ ; +88 $] | +132 $ [−127 $ ; +363 $] | −359 $ / +41 $ | −48 $ / +166 $ | 2/10 | +225 $ | +129 $ | −0 $ / −0 $ |
| H25 25 % continu | −317 $ | −245 $ [−539 $ ; +42 $] | +182 $ [−128 $ ; +502 $] | −359 $ / +41 $ | −50 $ / +124 $ | 2/10 | +360 $ | +153 $ | −0 $ / +0 $ |
| H25 50 % premier | −536 $ | −268 $ [−726 $ ; +172 $] | +193 $ [−274 $ ; +631 $] | −718 $ / +82 $ | −57 $ / +296 $ | 3/10 | +373 $ | +209 $ | −0 $ / −0 $ |
| H25 50 % continu | −637 $ | −495 $ [−1 081 $ ; +84 $] | +352 $ [−250 $ ; +964 $] | −718 $ / +82 $ | −102 $ / +254 $ | 5/10 | +715 $ | +257 $ | −0 $ / −0 $ |
| H25 75 % premier | −706 $ | −329 $ [−921 $ ; +304 $] | +307 $ [−261 $ ; +849 $] | −1 078 $ / +123 $ | −23 $ / +386 $ | 4/10 | +467 $ | +288 $ | −0 $ / −0 $ |
| H25 75 % continu | −960 $ | −741 $ [−1 601 $ ; +138 $] | +524 $ [−368 $ ; +1 446 $] | −1 078 $ / +123 $ | −155 $ / +390 $ | 6/10 | +1 071 $ | +361 $ | +0 $ / −0 $ |
| H25 100 % premier | −814 $ | −354 $ [−1 171 $ ; +426 $] | +443 $ [−208 $ ; +1 082 $] | −1 437 $ / +164 $ | +16 $ / +469 $ | 4/10 | +535 $ | +368 $ | +0 $ / −0 $ |
| H25 100 % continu | −1 283 $ | −988 $ [−2 185 $ ; +179 $] | +698 $ [−579 $ ; +1 935 $] | −1 437 $ / +164 $ | −215 $ / +521 $ | 8/10 | +1 421 $ | +465 $ | −0 $ / +0 $ |
| H26 préservation du jackpot (fraction figée app.) (25 %) | −317 $ | −245 $ [−546 $ ; +33 $] | +182 $ [−130 $ ; +496 $] | −359 $ / +41 $ | −50 $ / +124 $ | 2/10 | +360 $ | +153 $ | −0 $ / +0 $ |

GARDER prudent : app. +460 $ · valid. −70 $ (144 positions) · test −1 583 $ (112).

## 8. Les 24 fantômes prévus : garder / fusionner / abandonner

« = VENTE 100 % » : part des positions déclenchées (A + B, prudent, validation + test) où le P&L est identique à celui de la vente de toute la position au même instant (à 1 cent près).

| Fantôme | Décision | Raison | = VENTE 100 % | Δ prudent valid. → test (50 $ indép.) |
|---|---|---|---|---|
| H01 verrouillage paire complète (coût < 1) | **fusionner → H25** | règle identique à H25 100 % continu (même critère tous frais, même balayage) | 171/215 (79,5 %) | A −24 $ → +7 $ · B −988 $ → +698 $ |
| H02 verrouillage partiel 25 % | **fusionner → H25** | = H25 25 % continu | 0/215 (0,0 %) | A −4 $ → −3 $ · B −245 $ → +182 $ |
| H03 verrouillage partiel 50 % | **fusionner → H25** | = H25 50 % continu | 0/215 (0,0 %) | A −14 $ → −6 $ · B −495 $ → +352 $ |
| H04 plancher de profit (les 2 issues ≥ 0) | **fusionner → H26** | plancher ≥ 0 sur les deux issues = paire partielle rentable ; même famille que H26, sans règle de fraction apprise | 0/214 (0,0 %) | A −60 $ → −35 $ · B −598 $ → +519 $ |
| H05 réserve jackpot (≥ 70 % gardé) | **fusionner → H26** | fraction fixée par le jackpot ; H26 la choisit sur l'apprentissage | 0/215 (0,0 %) | A −27 $ → +0 $ · B −304 $ → +244 $ |
| H06 échelle de paires (4 tranches) | **fusionner → H25** | échelle = H25 avec seuils plus stricts ; rien de plus | 66/215 (30,7 %) | A −42 $ → +39 $ · B −965 $ → +822 $ |
| H07 pire perte limitée à −25 $ | **abandonner (= vente stop-loss)** | miroir : acheter l'opposé à la perte latente −25 $ = vendre la position à ce moment | 188/198 (94,9 %) | A −391 $ → −182 $ · B −764 $ → +264 $ |
| H08 pire perte limitée à −10 $ | **abandonner (= vente stop-loss)** | idem à −10 $ | 240/250 (96,0 %) | A −143 $ → +152 $ · B −506 $ → +475 $ |
| H09 pire issue à 0 dans le budget (après modèle −10) | **abandonner** | après modèle −10 la pire issue ≥ 0 est presque toujours infaisable (miroir : il faudrait que notre côté soit au-dessus du prix payé) | 3/205 (1,5 %) | A +5 $ → −5 $ · B −510 $ → +611 $ |
| H10 couvrir ou vendre (avantage net) | **fusionner → VENTE** | avantage net = 0 dans 100 % des cas (miroir) : = vendre 100 % au déclencheur | 205/205 (100,0 %) | A −35 $ → −28 $ · B −954 $ → +902 $ |
| H11 alerte précoce (2 signaux sur 3) 25 % | **fusionner → VENTE 25 %** | achat opposé 25 % = vente 25 % au même instant | 3/233 (1,3 %) | A −78 $ → +31 $ · B −242 $ → −8 $ |
| H12 horloge de risque (immédiat / attendre 3 s) | **abandonner** | attente 3 s : prédicteurs faibles (hedge predictor, AUC 0,52-0,59 sur les moments vivants), retombe sur la vente | 129/205 (62,9 %) | A −55 $ → −28 $ · B −914 $ → +890 $ |
| H13 prédictive 1 s | **abandonner** | idem 1 s | 204/205 (99,5 %) | A −35 $ → −28 $ · B −954 $ → +905 $ |
| H14 prédictive 3 s | **abandonner** | idem 3 s | 80/205 (39,0 %) | A −48 $ → −32 $ · B −887 $ → +930 $ |
| H15 prédictive 5 s | **abandonner** | idem 5 s | 148/205 (72,2 %) | A −37 $ → −28 $ · B −949 $ → +906 $ |
| H16 prédictive 10 s | **abandonner** | idem 10 s | 184/205 (89,8 %) | A −35 $ → −28 $ · B −921 $ → +901 $ |
| H17 premier passage (limite si EV > immédiat) | **abandonner (en attente de données)** | choisit l'immédiat presque toujours (le vendeur opposé monte après modèle −10) ; un vrai test exige les remplissages réels | 200/205 (97,6 %) | A −35 $ → −28 $ · B −948 $ → +908 $ |
| H18 fenêtre de conversion prédite (paire ≤ 0,95) — inactive si seuil appris = jamais | **abandonner (en attente de données)** | seuil appris = jamais ; ordre passif à 0,95 non mesurable sans file d'attente | 0/0 (—) | A +0 $ → +0 $ · B +0 $ → +0 $ |
| H19 sauvetage passif (vendeur − 1 c, 10 s) | **garder en test LIVE seulement** | remplissage passif non mesurable hors ligne (29-41 % selon l'hypothèse) ; à mesurer avec un ordre fantôme réel | 3/205 (1,5 %) | A −142 $ → −31 $ · B −373 $ → +34 $ |
| H20 prédicteur de file (traversée) passif sinon immédiat | **fusionner → H19 (live)** | prédicteur de « traversée », pas de file ; même besoin de données que H19 | 151/205 (73,7 %) | A −37 $ → −28 $ · B −961 $ → +916 $ |
| H21 recharge du carnet | **abandonner** | = immédiat (= vente) sauf sur les sauts, qui ne reviennent presque jamais après modèle −10 | 110/205 (53,7 %) | A −47 $ → −30 $ · B −833 $ → +843 $ |
| H22 hybride 50 % immédiat + 50 % passif | **fusionner → H19 (live)** | moitié vente + moitié H19 | 21/205 (10,2 %) | A −56 $ → −29 $ · B −1 009 $ → +854 $ |
| H23 boomerang (revente de l'opposé +5 c) | **garder comme variante de H25 (observation)** | = H25 + revente de l'opposé à +5 c : pari sur le retour, signe instable entre validation et test | 29/215 (13,5 %) | A −24 $ → −166 $ · B −364 $ → +280 $ |
| H24 moteur d'inventaire deux jambes | **abandonner** | ajoute de l'exposition (rachat de notre côté) : ce n'est pas une couverture ; signe instable | 0/320 (0,0 %) | A +112 $ → −30 $ · B −288 $ → −56 $ |
| H25 conversion précoce | **garder** (remplace H01-H03, H06) | seule règle « paire strictement rentable » ; = vente de la même fraction au même instant (Δ 0 $), capital bloqué en plus | — | A −24 $ → +7 $ · B −988 $ → +698 $ |
| H26 préservation du jackpot | **garder** (remplace H04-H05) | fraction figée sur l'apprentissage (A 25 %, B 25 %) | — | A −4 $ → −3 $ · B −245 $ → +182 $ |

## 9. Audit des données pour faire tourner ces fantômes EN DIRECT

| Donnée | Bot Cloudflare (bot95/src/index.js) aujourd'hui | Programme Dublin (bot95/rapide/rapide.js) aujourd'hui | Nécessaire pour H25 / H26 / H19 |
|---|---|---|---|
| Carnet du côté OPPOSÉ après l'entrée | meilleur niveau + taille toutes les 0,3 s (rec) ; 3 niveaux à 100 ms seulement ~10 s avant / après le 1er désaccord (photos) | tient le carnet complet des deux jetons EN MÉMOIRE, mais n'enregistre rien du côté opposé (seulement notre côté au signal, jusqu'à 2 s) | carnet opposé complet (≥ 5 niveaux, prix + taille) à chaque message, de l'entrée au règlement, pour chaque position fantôme |
| Transactions (prix, taille, côté) | flux agrégé en $ par seconde (sig) et par 100 ms (photos) ; enregistreur au message près (best bid/ask + chaque transaction) actif 10 min par heure, gardé 24 h, pas exporté | reçoit last_trade_price mais l'ignore | chaque transaction des deux jetons : prix, taille, côté, horodatage Polymarket |
| Annulations / ajouts | agrégés en $ (retraits / ajouts) | appliqués au carnet en mémoire, non enregistrés | événements price_change bruts (prix, taille avant / après, côté) pour reconstruire la file à notre prix |
| Horodatages | réception Cloudflare seulement dans les lignes | réception locale (µs) + horodatage Polymarket du message, utilisés seulement en statistiques | les deux horodatages sur chaque événement enregistré |
| Règles A et B | A (« desaccord 30 zone + modele monte ») et « corrige : V2-F » (moteur 0,015 %) existent comme fantômes | règles V2-F 0,08 % / 0,01 %, désaccord 30, etc. ; **ni A ni B** (pas de sdRel 1,5e-4, pas de zone + modèle monte) | ajouter A et B à rapide.js pour mesurer la latence réelle des mêmes entrées |
| Suivi après l'entrée | aucun suivi d'une paire possible | « achetable » à 1 ms … 2 s, survie de l'offre de NOTRE côté seulement | à chaque message : coût de paire tous frais, quantité appariable au meilleur niveau et en profondeur, début / fin de chaque fenêtre rentable |
| Ordres passifs | — | aucun (fantôme, pas d'ordre) | pour H19 : un ordre réel minuscule (1 part) ou un suivi de file fantôme (taille devant nous + transactions à notre prix) |
| Fusion Up + Down | — | — | non nécessaire au P&L ; à tracer seulement si on veut libérer le capital avant le règlement |
| Latence | — | rapide.json vide : pas encore de résultats reçus | temps aller-retour d'un ordre (déjà sondé : /time), délai message → décision (déjà calculé) — à joindre à chaque fenêtre |

**À ajouter exactement dans l'enregistreur live** (rapide.js de préférence, car il tient déjà le carnet complet en mémoire) :

1. Les règles d'entrée A et B (modèle corrigé sdRel = 1,5e-4 ; zone 0,15-0,35 + modèle monte) en fantômes, mêmes définitions que le hors ligne.
2. Pour chaque position fantôme ouverte : à chaque message Polymarket des deux jetons jusqu'au règlement, une ligne [heure locale µs, heure Polymarket, meilleur vendeur et acheteur opposés + 5 niveaux (prix, taille), coût de paire tous frais, parts appariables au prix rentable].
3. Toutes les transactions last_trade_price des deux jetons (prix, taille, côté, heure Polymarket, heure locale) et les événements price_change bruts (prix, taille, côté).
4. Pour chaque fenêtre de paire rentable : heure de début et de fin, quantité disponible au début, après 1 / 10 / 100 / 300 / 600 ms.
5. Un ordre passif fantôme suivi en file (taille devant nous à la pose, transactions à notre prix ensuite), ou un ordre réel de 1 part si Pitch l'autorise — c'est la seule façon de mesurer H19.
6. Envoi au bot Cloudflare et sauvegarde dans bot95/ (rapide.json ou un fichier par jour), comme les autres données.

Durée de calcul : 119 s.