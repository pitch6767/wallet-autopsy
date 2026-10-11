# BOT95 HEDGE LAB — oscillations des tickets bon marché : H27 vendre-racheter, H28 couvrir-décourir, H29 inventaire dynamique, H30 conversion

Étude hors ligne du 11.10.2026 — aucun bot, aucun workflow modifié, rien publié. Mêmes entrées A et B que resultat_hedge_lab.md, mêmes scénarios, mêmes périodes (apprentissage < 08.10 22:00 · validation → 10.10 10:25 · test inédit après). Δ = P&L avec la règle − P&L en gardant, sur les mêmes positions, frais preneur compris (frais teneur d'ordre supposés 0, non vérifiés) ; IC 90 % par blocs d'une heure.

## Réponse courte (en tête)

- **A · désaccord 30 zone + modèle monte** (prudent, 50 $ indépendants) — paramètres H27 appris : +3 c, vendre 25 %, racheter à vente − 2 c. H27 preneur valid. −20 $ [−61 $ ; +15 $] → test +25 $ [+1 $ ; +52 $] ; VENTE seule au même instant +2 $ → −1 $ ; valeur de la jambe de rachat valid. −22 $, test +26 $. Validation : 20 ventes, 15 rachats ; allers-retours +20 $, perte d'opportunité −40 $, gain quand notre côté perd +0 $ ; jackpots perdus 0/5. H27 passif valid. −74 $ [−151 $ ; −13 $] → test −7 $ [−16 $ ; −0 $] ; H29 valid. +0 $ [+0 $ ; +0 $] → test +0 $ [+0 $ ; +0 $] (règle : R0 garder) ; H30 = H25 valid. −24 $ [−632 $ ; +540 $] → test +7 $ [−572 $ ; +499 $].
- **B · V2-F corrigé 0,015 %** (prudent, 50 $ indépendants) — paramètres H27 appris : +3 c, vendre 25 %, racheter à vente − 5 c. H27 preneur valid. −105 $ [−272 $ ; +33 $] → test +78 $ [+14 $ ; +139 $] ; VENTE seule au même instant −235 $ → +193 $ ; valeur de la jambe de rachat valid. +130 $, test −115 $. Validation : 90 ventes, 71 rachats ; allers-retours +121 $, perte d'opportunité −244 $, gain quand notre côté perd +18 $ ; jackpots perdus 0/5. H27 passif valid. −162 $ [−248 $ ; −85 $] → test −57 $ [−101 $ ; −19 $] ; H29 valid. +0 $ [+0 $ ; +0 $] → test +0 $ [+0 $ ; +0 $] (règle : R0 garder) ; H30 = H25 valid. −988 $ [−2 155 $ ; +109 $] → test +698 $ [−490 $ ; +1 938 $].
- **H28 = H27** au cent près dans les trois scénarios (miroir : mêmes prix, mêmes tailles, mêmes frais) ; seule différence : le capital bloqué (section 4).
- **Différence avec les anciens essais** : la vente seule au même instant EST l'ancienne sortie anticipée / free-roll ; H27 n'ajoute que la jambe de rachat, dont la valeur est isolée ci-dessus et en section 3.
- **Données** : suffisantes pour les variantes preneur (premier verdict, limites 0,3 s et meilleur niveau) ; insuffisantes pour toute variante passive (file, transactions, annulations) → enregistrements 50 ms de Dublin nécessaires (section 7).
- **Verdict** : aucune de ces règles ne bat GARDER de façon démontrée (IC 90 % validation entièrement > 0 ET test > 0).

## 1. Définitions et paramètres (choisis sur l'apprentissage, prudent, 50 $ indépendants, puis figés)

Grille pré-enregistrée (36 combinaisons) : hausse de notre côté mesurée sur le **meilleur acheteur** (prix auquel on peut vendre) : +3 / +5 / +10 c ou +30 / +50 / +100 % du prix d'entrée ; fraction vendue f = 25 / 50 % ; rachat quand le meilleur vendeur de notre côté ≤ prix de vente moyen − y, y = 2 / 5 / 10 c.

- **H27 preneur** : au premier moment où la hausse est atteinte, vente de f au meilleur acheteur (ordre au prix vu, renouvelé tant que la hausse tient) ; puis rachat de la même quantité au meilleur vendeur dès qu'il est ≤ vente − y, jusqu'au règlement (un seul aller-retour).
- **H27 passif** : même vente ; le rachat est un ordre passif à vente − y posé jusqu'au règlement, rempli seulement si le vendeur passe 1 c sous notre prix (prudent), 2 lignes de suite et moitié de la taille (pessimiste), dès qu'il touche (idéal, borne haute).
- **VENTE seule** = la même vente au même instant SANS jambe de rachat : c'est l'ancienne « sortie anticipée / free-roll partiel ». H27 − VENTE seule = valeur de la seule jambe de rachat.
- **H28** : mêmes instants, mêmes quantités, mais on ACHÈTE l'opposé au lieu de vendre, puis on le REVEND au lieu de racheter notre côté (seuils traduits par le miroir : vendeur opposé = 1 − acheteur de notre côté).
- **H29** : à chaque instant, une règle simple parmi six candidates fixées à l'avance (garder / vendre partiel / racheter / acheter l'opposé — ce dernier identique à vendre par le miroir) ; la règle est choisie sur l'apprentissage.
- **H30** = H25 (apparier seulement les paires strictement rentables tous frais compris, au meilleur niveau, balayage continu).

| Cohorte | H27 preneur | H27 passif | H29 règle choisie |
|---|---|---|---|
| A | +3 c, vendre 25 %, racheter à vente − 2 c (app. +919 $) | +50 % du prix d'entrée, vendre 25 %, racheter à vente − 2 c (app. +884 $) | R0 garder |
| B | +3 c, vendre 25 %, racheter à vente − 5 c (app. +394 $) | +100 % du prix d'entrée, vendre 25 %, racheter à vente − 2 c (app. +382 $) | R0 garder |

H29 — Σ P&L apprentissage (prudent) de chaque règle candidate : A : R0 +946 $, R1 +919 $, R2 +773 $, R3 +623 $, R4 +595 $, R5 +184 $ · B : R0 +460 $, R1 +394 $, R2 +147 $, R3 −537 $, R4 −577 $, R5 −823 $.
GARDER sur l'apprentissage (prudent) : A +946 $ · B +460 $.

## 2. Résultat marginal contre GARDER (toutes les positions, exécutées ou non)

### A · désaccord 30 zone + modèle monte — idéal

| Règle | Δ app. [IC 90 %] | Δ valid. [IC 90 %] | Δ test [IC 90 %] | Δ 250 $ valid. / test | Creux max valid. / test | Capital engagé max | Jackpots perdus valid. / test | Profit sacrifié jackpots valid. / test |
|---|---|---|---|---|---|---|---|---|
| H27 preneur | −281 $ [−491 $ ; −94 $] | −152 $ [−267 $ ; −52 $] | −20 $ [−64 $ ; +20 $] | −152 $ / −20 $ | −236 $ / −320 $ | +51 $ | 3/14 / 2/8 | +92 $ / +2 $ |
| H27 passif | −122 $ [−254 $ ; −8 $] | −133 $ [−216 $ ; −60 $] | −82 $ [−140 $ ; −30 $] | −133 $ / −82 $ | −236 $ / −328 $ | +50 $ | 2/14 / 2/8 | +40 $ / +48 $ |
| VENTE seule (même instant, H27 preneur) | −302 $ [−547 $ ; −58 $] | −240 $ [−452 $ ; −27 $] | −76 $ [−230 $ ; +66 $] | −240 $ / −76 $ | −205 $ / −256 $ | +50 $ | 6/14 / 5/8 | +293 $ / +160 $ |
| VENTE seule (même instant, H27 passif) | −263 $ [−476 $ ; −53 $] | −244 $ [−435 $ ; −63 $] | −75 $ [−171 $ ; +18 $] | −244 $ / −75 $ | −203 $ / −287 $ | +50 $ | 6/14 / 3/8 | +272 $ / +121 $ |
| H28 preneur | −281 $ [−492 $ ; −101 $] | −152 $ [−283 $ ; −51 $] | −20 $ [−65 $ ; +21 $] | −152 $ / −20 $ | −236 $ / −320 $ | +51 $ | 3/14 / 2/8 | +92 $ / +2 $ |
| H28 passif | −122 $ [−257 $ ; −9 $] | −133 $ [−219 $ ; −56 $] | −82 $ [−144 $ ; −31 $] | −133 $ / −82 $ | −236 $ / −328 $ | +50 $ | 2/14 / 2/8 | +40 $ / +48 $ |
| H29 | −0 $ [+0 $ ; +0 $] | −0 $ [+0 $ ; +0 $] | +0 $ [+0 $ ; +0 $] | −0 $ / +0 $ | −219 $ / −318 $ | +50 $ | 0/14 / 0/8 | +0 $ / +0 $ |
| H30 = H25 | −1 248 $ [−2 215 $ ; −307 $] | −1 013 $ [−1 845 $ ; −216 $] | −306 $ [−977 $ ; +248 $] | −972 $ / −309 $ | −377 $ / −120 $ | +50 $ | 14/14 / 8/8 | +1 173 $ / +641 $ |

GARDER : apprentissage 51 positions +1 632 $ (creux −140 $) · validation 62 positions +753 $ (creux −219 $) · inédit 47 positions +273 $ (creux −318 $).

### A · désaccord 30 zone + modèle monte — prudent

| Règle | Δ app. [IC 90 %] | Δ valid. [IC 90 %] | Δ test [IC 90 %] | Δ 250 $ valid. / test | Creux max valid. / test | Capital engagé max | Jackpots perdus valid. / test | Profit sacrifié jackpots valid. / test |
|---|---|---|---|---|---|---|---|---|
| H27 preneur | −27 $ [−127 $ ; +53 $] | −20 $ [−61 $ ; +15 $] | +25 $ [+1 $ ; +52 $] | +0 $ / +0 $ | −364 $ / −510 $ | +51 $ | 0/5 / 0/5 | +14 $ / −11 $ |
| H27 passif | −61 $ [−163 $ ; +22 $] | −74 $ [−151 $ ; −13 $] | −7 $ [−16 $ ; −0 $] | +0 $ / −0 $ | −403 $ / −531 $ | +50 $ | 0/5 / 0/5 | +14 $ / +7 $ |
| VENTE seule (même instant, H27 preneur) | −173 $ [−357 $ ; +3 $] | +2 $ [−153 $ ; +140 $] | −1 $ [−149 $ ; +130 $] | −0 $ / −0 $ | −336 $ / −463 $ | +50 $ | 1/5 / 2/5 | +78 $ / +101 $ |
| VENTE seule (même instant, H27 passif) | −163 $ [−338 $ ; −8 $] | −51 $ [−206 $ ; +92 $] | −27 $ [−166 $ ; +93 $] | +0 $ / +0 $ | −379 $ / −484 $ | +50 $ | 1/5 / 0/5 | +78 $ / +75 $ |
| H28 preneur | −27 $ [−130 $ ; +49 $] | −20 $ [−64 $ ; +14 $] | +25 $ [+1 $ ; +52 $] | +1 $ / +0 $ | −364 $ / −510 $ | +115 $ | 0/5 / 0/5 | +14 $ / −11 $ |
| H28 passif | −61 $ [−164 $ ; +23 $] | −74 $ [−153 $ ; −15 $] | −7 $ [−16 $ ; +0 $] | +0 $ / −0 $ | −403 $ / −531 $ | +111 $ | 0/5 / 0/5 | +14 $ / +7 $ |
| H29 | +0 $ [+0 $ ; +0 $] | +0 $ [+0 $ ; +0 $] | +0 $ [+0 $ ; +0 $] | −0 $ / +0 $ | −355 $ / −523 $ | +50 $ | 0/5 / 0/5 | +0 $ / +0 $ |
| H30 = H25 | −762 $ [−1 501 $ ; −72 $] | −24 $ [−632 $ ; +540 $] | +7 $ [−572 $ ; +499 $] | +108 $ / +0 $ | −317 $ / −449 $ | +314 $ | 5/5 / 5/5 | +313 $ / +392 $ |

GARDER : apprentissage 26 positions +946 $ (creux −150 $) · validation 37 positions −293 $ (creux −355 $) · inédit 34 positions −411 $ (creux −523 $).

### A · désaccord 30 zone + modèle monte — pessimiste

| Règle | Δ app. [IC 90 %] | Δ valid. [IC 90 %] | Δ test [IC 90 %] | Δ 250 $ valid. / test | Creux max valid. / test | Capital engagé max | Jackpots perdus valid. / test | Profit sacrifié jackpots valid. / test |
|---|---|---|---|---|---|---|---|---|
| H27 preneur | −31 $ [−87 $ ; +12 $] | −11 $ [−56 $ ; +26 $] | −44 $ [−146 $ ; +12 $] | −11 $ / +1 $ | −265 $ / −313 $ | +51 $ | 0/3 / 0/4 | +19 $ / +51 $ |
| H27 passif | −110 $ [−244 $ ; −17 $] | −33 $ [−75 $ ; −2 $] | −2 $ [−12 $ ; +4 $] | −68 $ / +0 $ | −272 $ / −288 $ | +50 $ | 0/3 / 0/4 | +19 $ / +4 $ |
| VENTE seule (même instant, H27 preneur) | −111 $ [−268 $ ; +30 $] | −26 $ [−183 $ ; +103 $] | −11 $ [−142 $ ; +105 $] | −26 $ / −0 $ | −245 $ / −280 $ | +50 $ | 0/3 / 1/4 | +81 $ / +85 $ |
| VENTE seule (même instant, H27 passif) | −103 $ [−257 $ ; +32 $] | −67 $ [−209 $ ; +62 $] | +22 $ [−51 $ ; +92 $] | −68 $ / −0 $ | −283 $ / −251 $ | +50 $ | 0/3 / 0/4 | +81 $ / +20 $ |
| H28 preneur | −31 $ [−91 $ ; +12 $] | −11 $ [−53 $ ; +25 $] | −44 $ [−147 $ ; +12 $] | −11 $ / +0 $ | −265 $ / −313 $ | +112 $ | 0/3 / 0/4 | +19 $ / +51 $ |
| H28 passif | −110 $ [−242 $ ; −17 $] | −33 $ [−73 $ ; −2 $] | −2 $ [−12 $ ; +4 $] | −68 $ / +0 $ | −272 $ / −288 $ | +111 $ | 0/3 / 0/4 | +19 $ / +4 $ |
| H29 | +0 $ [+0 $ ; +0 $] | +0 $ [+0 $ ; +0 $] | +0 $ [+0 $ ; +0 $] | +0 $ / +0 $ | −253 $ / −284 $ | +50 $ | 0/3 / 0/4 | +0 $ / +0 $ |
| H30 = H25 | −493 $ [−1 136 $ ; +70 $] | −105 $ [−720 $ ; +421 $] | +50 $ [−367 $ ; +440 $] | +75 $ / +0 $ | −337 $ / −285 $ | +314 $ | 3/3 / 4/4 | +316 $ / +252 $ |

GARDER : apprentissage 19 positions +594 $ (creux −104 $) · validation 31 positions −182 $ (creux −253 $) · inédit 30 positions −269 $ (creux −284 $).

### B · V2-F corrigé 0,015 % — idéal

| Règle | Δ app. [IC 90 %] | Δ valid. [IC 90 %] | Δ test [IC 90 %] | Δ 250 $ valid. / test | Creux max valid. / test | Capital engagé max | Jackpots perdus valid. / test | Profit sacrifié jackpots valid. / test |
|---|---|---|---|---|---|---|---|---|
| H27 preneur | −375 $ [−628 $ ; −148 $] | −385 $ [−697 $ ; −126 $] | −90 $ [−236 $ ; +47 $] | −385 $ / +1 $ | −872 $ / −705 $ | +50 $ | 2/11 / 1/11 | +297 $ / −5 $ |
| H27 passif | −238 $ [−425 $ ; −86 $] | −292 $ [−406 $ ; −189 $] | −137 $ [−233 $ ; −52 $] | −292 $ / +0 $ | −865 $ / −740 $ | +50 $ | 1/11 / 0/11 | +48 $ / +1 $ |
| VENTE seule (même instant, H27 preneur) | −599 $ [−1 000 $ ; −225 $] | −383 $ [−801 $ ; +19 $] | +32 $ [−279 $ ; +353 $] | −383 $ / +0 $ | −744 $ / −573 $ | +50 $ | 3/11 / 4/11 | +475 $ / +147 $ |
| VENTE seule (même instant, H27 passif) | −398 $ [−742 $ ; −79 $] | −387 $ [−754 $ ; −21 $] | −80 $ [−342 $ ; +193 $] | −387 $ / +0 $ | −822 $ / −644 $ | +50 $ | 3/11 / 3/11 | +449 $ / +133 $ |
| H28 preneur | −375 $ [−637 $ ; −154 $] | −385 $ [−672 $ ; −122 $] | −90 $ [−238 $ ; +47 $] | −384 $ / −0 $ | −872 $ / −705 $ | +50 $ | 2/11 / 1/11 | +297 $ / −5 $ |
| H28 passif | −238 $ [−419 $ ; −90 $] | −292 $ [−412 $ ; −181 $] | −137 $ [−239 $ ; −53 $] | −292 $ / +0 $ | −865 $ / −740 $ | +50 $ | 1/11 / 0/11 | +48 $ / +1 $ |
| H29 | +0 $ [+0 $ ; +0 $] | −0 $ [+0 $ ; +0 $] | +0 $ [+0 $ ; +0 $] | −0 $ / +0 $ | −848 $ / −656 $ | +50 $ | 0/11 / 0/11 | +0 $ / +0 $ |
| H30 = H25 | −2 391 $ [−3 941 $ ; −823 $] | −1 437 $ [−3 115 $ ; +128 $] | +164 $ [−1 087 $ ; +1 476 $] | −1 176 $ / +197 $ | −602 $ / −324 $ | +50 $ | 11/11 / 10/11 | +1 920 $ / +587 $ |

GARDER : apprentissage 238 positions +2 191 $ (creux −431 $) · validation 237 positions +926 $ (creux −848 $) · inédit 178 positions −304 $ (creux −656 $).

### B · V2-F corrigé 0,015 % — prudent

| Règle | Δ app. [IC 90 %] | Δ valid. [IC 90 %] | Δ test [IC 90 %] | Δ 250 $ valid. / test | Creux max valid. / test | Capital engagé max | Jackpots perdus valid. / test | Profit sacrifié jackpots valid. / test |
|---|---|---|---|---|---|---|---|---|
| H27 preneur | −66 $ [−188 $ ; +40 $] | −105 $ [−272 $ ; +33 $] | +78 $ [+14 $ ; +139 $] | +0 $ / +1 $ | −892 $ / −1 692 $ | +50 $ | 0/5 / 0/5 | +59 $ / −6 $ |
| H27 passif | −77 $ [−149 $ ; −21 $] | −162 $ [−248 $ ; −85 $] | −57 $ [−101 $ ; −19 $] | +0 $ / +0 $ | −929 $ / −1 827 $ | +50 $ | 0/5 / 0/5 | −2 $ / +1 $ |
| VENTE seule (même instant, H27 preneur) | −312 $ [−540 $ ; −105 $] | −235 $ [−529 $ ; +58 $] | +193 $ [−120 $ ; +515 $] | −0 $ / −0 $ | −883 $ / −1 520 $ | +50 $ | 0/5 / 2/5 | +261 $ / +96 $ |
| VENTE seule (même instant, H27 passif) | −227 $ [−422 $ ; −50 $] | −268 $ [−537 $ ; +0 $] | +76 $ [−135 $ ; +316 $] | +0 $ / +0 $ | −941 $ / −1 691 $ | +50 $ | 0/5 / 2/5 | +253 $ / +86 $ |
| H28 preneur | −66 $ [−186 $ ; +39 $] | −105 $ [−278 $ ; +38 $] | +78 $ [+11 $ ; +139 $] | +0 $ / −0 $ | −892 $ / −1 692 $ | +153 $ | 0/5 / 0/5 | +59 $ / −6 $ |
| H28 passif | −77 $ [−151 $ ; −18 $] | −162 $ [−245 $ ; −87 $] | −57 $ [−98 $ ; −20 $] | −0 $ / −0 $ | −929 $ / −1 827 $ | +135 $ | 0/5 / 0/5 | −2 $ / +1 $ |
| H29 | +0 $ [+0 $ ; +0 $] | +0 $ [+0 $ ; +0 $] | +0 $ [+0 $ ; +0 $] | +0 $ / −0 $ | −910 $ / −1 776 $ | +50 $ | 0/5 / 0/5 | +0 $ / +0 $ |
| H30 = H25 | −1 283 $ [−2 179 $ ; −439 $] | −988 $ [−2 155 $ ; +109 $] | +698 $ [−490 $ ; +1 938 $] | −0 $ / +0 $ | −1 194 $ / −915 $ | +475 $ | 5/5 / 3/5 | +1 048 $ / +373 $ |

GARDER : apprentissage 113 positions +460 $ (creux −458 $) · validation 144 positions −70 $ (creux −910 $) · inédit 112 positions −1 583 $ (creux −1 776 $).

### B · V2-F corrigé 0,015 % — pessimiste

| Règle | Δ app. [IC 90 %] | Δ valid. [IC 90 %] | Δ test [IC 90 %] | Δ 250 $ valid. / test | Creux max valid. / test | Capital engagé max | Jackpots perdus valid. / test | Profit sacrifié jackpots valid. / test |
|---|---|---|---|---|---|---|---|---|
| H27 preneur | −27 $ [−108 $ ; +37 $] | −30 $ [−123 $ ; +58 $] | +30 $ [−33 $ ; +87 $] | +1 $ / −0 $ | −1 062 $ / −1 454 $ | +50 $ | 0/4 / 0/3 | −3 $ / −3 $ |
| H27 passif | −42 $ [−95 $ ; −7 $] | −134 $ [−214 $ ; −61 $] | −52 $ [−94 $ ; −16 $] | +0 $ / +0 $ | −1 121 $ / −1 532 $ | +50 $ | 0/4 / 0/3 | −2 $ / −0 $ |
| VENTE seule (même instant, H27 preneur) | −151 $ [−332 $ ; +12 $] | −51 $ [−277 $ ; +169 $] | +104 $ [−119 $ ; +313 $] | +0 $ / +1 $ | −998 $ / −1 331 $ | +50 $ | 0/4 / 2/3 | +143 $ / +45 $ |
| VENTE seule (même instant, H27 passif) | −137 $ [−290 $ ; +11 $] | −137 $ [−349 $ ; +48 $] | +147 $ [−44 $ ; +364 $] | +0 $ / +0 $ | −1 134 $ / −1 318 $ | +50 $ | 0/4 / 1/3 | +140 $ / +28 $ |
| H28 preneur | −27 $ [−109 $ ; +37 $] | −30 $ [−123 $ ; +56 $] | +30 $ [−37 $ ; +87 $] | +0 $ / −0 $ | −1 062 $ / −1 454 $ | +195 $ | 0/4 / 0/3 | −3 $ / −3 $ |
| H28 passif | −42 $ [−94 $ ; −7 $] | −134 $ [−218 $ ; −63 $] | −52 $ [−93 $ ; −18 $] | +0 $ / −0 $ | −1 121 $ / −1 532 $ | +187 $ | 0/4 / 0/3 | −2 $ / −0 $ |
| H29 | +0 $ [+0 $ ; +0 $] | −0 $ [+0 $ ; +0 $] | +0 $ [+0 $ ; +0 $] | +0 $ / +0 $ | −1 063 $ / −1 479 $ | +50 $ | 0/4 / 0/3 | +0 $ / +0 $ |
| H30 = H25 | −596 $ [−1 269 $ ; +101 $] | −215 $ [−1 164 $ ; +660 $] | +521 $ [−340 $ ; +1 411 $] | +0 $ / +0 $ | −952 $ / −851 $ | +640 $ | 4/4 / 3/3 | +573 $ / +162 $ |

GARDER : apprentissage 98 positions −40 $ (creux −533 $) · validation 120 positions −593 $ (creux −1 063 $) · inédit 99 positions −1 304 $ (creux −1 479 $).

## 3. H27 décomposé : allers-retours, rachats manqués, jambe de rachat isolée

(a) gain des allers-retours réalisés = parts rachetées × (prix de vente net − coût de rachat) ; (b) perte d'opportunité = parts vendues jamais rachetées × (1 − prix de vente net) quand notre côté gagne ; en face, gain quand il perd = parts non rachetées × prix de vente net. (d) Δ total = (a) + (b) + gain d'en face, sur TOUTES les positions. « Valeur de la jambe de rachat » = Δ(H27) − Δ(VENTE seule au même instant).

| Cohorte | Variante | Scénario | Période | Positions avec vente | avec rachat | (a) allers-retours | (b) perte d'opportunité | gain quand notre côté perd | (d) Δ vs GARDER | Valeur de la jambe de rachat |
|---|---|---|---|---|---|---|---|---|---|---|
| A | H27 preneur | idéal | apprentissage | 44 | 32 | +16 $ | −325 $ | +28 $ | −281 $ | +21 $ |
| A | H27 preneur | idéal | validation | 44 | 33 | +11 $ | −162 $ | +0 $ | −152 $ | +88 $ |
| A | H27 preneur | idéal | inédit | 33 | 28 | +26 $ | −46 $ | +0 $ | −20 $ | +56 $ |
| A | H27 preneur | prudent | apprentissage | 19 | 15 | +18 $ | −64 $ | +19 $ | −27 $ | +146 $ |
| A | H27 preneur | prudent | validation | 20 | 15 | +20 $ | −40 $ | +0 $ | −20 $ | −22 $ |
| A | H27 preneur | prudent | inédit | 19 | 17 | +27 $ | −2 $ | +0 $ | +25 $ | +26 $ |
| A | H27 preneur | pessimiste | apprentissage | 12 | 10 | +9 $ | −40 $ | +0 $ | −31 $ | +80 $ |
| A | H27 preneur | pessimiste | validation | 15 | 12 | +24 $ | −35 $ | +0 $ | −11 $ | +15 $ |
| A | H27 preneur | pessimiste | inédit | 14 | 13 | +8 $ | −51 $ | +0 $ | −44 $ | −33 $ |
| A | H27 passif | idéal | apprentissage | 38 | 27 | +4 $ | −159 $ | +33 $ | −122 $ | +141 $ |
| A | H27 passif | idéal | validation | 37 | 26 | +4 $ | −137 $ | +0 $ | −133 $ | +111 $ |
| A | H27 passif | idéal | inédit | 24 | 17 | +3 $ | −84 $ | +0 $ | −82 $ | −7 $ |
| A | H27 passif | prudent | apprentissage | 16 | 10 | +2 $ | −83 $ | +19 $ | −61 $ | +101 $ |
| A | H27 passif | prudent | validation | 14 | 8 | +1 $ | −75 $ | +0 $ | −74 $ | −23 $ |
| A | H27 passif | prudent | inédit | 13 | 9 | +2 $ | −9 $ | +0 $ | −7 $ | +19 $ |
| A | H27 passif | pessimiste | apprentissage | 11 | 8 | +2 $ | −112 $ | +0 $ | −110 $ | −7 $ |
| A | H27 passif | pessimiste | validation | 9 | 6 | +1 $ | −35 $ | +0 $ | −33 $ | +33 $ |
| A | H27 passif | pessimiste | inédit | 9 | 8 | +2 $ | −5 $ | +0 $ | −2 $ | −25 $ |
| B | H27 preneur | idéal | apprentissage | 198 | 151 | +172 $ | −571 $ | +24 $ | −375 $ | +224 $ |
| B | H27 preneur | idéal | validation | 178 | 137 | +193 $ | −584 $ | +5 $ | −385 $ | −2 $ |
| B | H27 preneur | idéal | inédit | 140 | 116 | +165 $ | −255 $ | +0 $ | −90 $ | −123 $ |
| B | H27 preneur | prudent | apprentissage | 76 | 57 | +113 $ | −181 $ | +2 $ | −66 $ | +246 $ |
| B | H27 preneur | prudent | validation | 90 | 71 | +121 $ | −244 $ | +18 $ | −105 $ | +130 $ |
| B | H27 preneur | prudent | inédit | 69 | 63 | +134 $ | −56 $ | +0 $ | +78 $ | −115 $ |
| B | H27 preneur | pessimiste | apprentissage | 56 | 45 | +71 $ | −98 $ | +0 $ | −27 $ | +124 $ |
| B | H27 preneur | pessimiste | validation | 70 | 59 | +111 $ | −142 $ | +0 $ | −30 $ | +21 $ |
| B | H27 preneur | pessimiste | inédit | 57 | 52 | +104 $ | −74 $ | +0 $ | +30 $ | −74 $ |
| B | H27 passif | idéal | apprentissage | 128 | 95 | +17 $ | −262 $ | +7 $ | −238 $ | +160 $ |
| B | H27 passif | idéal | validation | 105 | 76 | +14 $ | −307 $ | +1 $ | −292 $ | +95 $ |
| B | H27 passif | idéal | inédit | 77 | 56 | +7 $ | −144 $ | +0 $ | −137 $ | −57 $ |
| B | H27 passif | prudent | apprentissage | 49 | 36 | +6 $ | −87 $ | +4 $ | −77 $ | +149 $ |
| B | H27 passif | prudent | validation | 52 | 34 | +7 $ | −169 $ | +0 $ | −162 $ | +106 $ |
| B | H27 passif | prudent | inédit | 37 | 27 | +4 $ | −61 $ | +0 $ | −57 $ | −133 $ |
| B | H27 passif | pessimiste | apprentissage | 32 | 24 | +4 $ | −46 $ | +0 $ | −42 $ | +95 $ |
| B | H27 passif | pessimiste | validation | 38 | 23 | +5 $ | −139 $ | +0 $ | −134 $ | +3 $ |
| B | H27 passif | pessimiste | inédit | 32 | 24 | +3 $ | −55 $ | +0 $ | −52 $ | −199 $ |

## 4. H27 contre H28 : même exposition, mêmes quantités, mêmes instants

| Cohorte | Variante | Scénario | Δ P&L H27 − H28 (app. / valid. / test) | Capital engagé max H27 / H28 | Positions où la quantité exécutée diffère |
|---|---|---|---|---|---|
| A | preneur | idéal | +0 $ / +0 $ / +0 $ | +51 $ / +51 $ | 0 |
| A | preneur | prudent | −0 $ / +0 $ / +0 $ | +51 $ / +115 $ | 0 |
| A | preneur | pessimiste | +0 $ / −0 $ / +0 $ | +51 $ / +112 $ | 0 |
| A | passif | idéal | −0 $ / +0 $ / −0 $ | +50 $ / +50 $ | 0 |
| A | passif | prudent | +0 $ / +0 $ / −0 $ | +50 $ / +111 $ | 0 |
| A | passif | pessimiste | +0 $ / +0 $ / −0 $ | +50 $ / +111 $ | 0 |
| B | preneur | idéal | +0 $ / +0 $ / −0 $ | +50 $ / +50 $ | 0 |
| B | preneur | prudent | −0 $ / −0 $ / −0 $ | +50 $ / +153 $ | 0 |
| B | preneur | pessimiste | +0 $ / +0 $ / −0 $ | +50 $ / +195 $ | 0 |
| B | passif | idéal | +0 $ / +0 $ / −0 $ | +50 $ / +50 $ | 0 |
| B | passif | prudent | −0 $ / +0 $ / +0 $ | +50 $ / +135 $ | 0 |
| B | passif | pessimiste | −0 $ / +0 $ / +0 $ | +50 $ / +187 $ | 0 |

Explication : vendeur opposé = 1 − acheteur de notre côté et acheteur opposé = 1 − vendeur de notre côté, avec les mêmes tailles ; frais 0,072·p·(1−p) identiques pour p et 1 − p. Vendre x parts de notre côté au prix b ou acheter x parts opposées à 1 − b donne exactement le même P&L dans les deux issues ; seul change le capital : H28 paie 1 − b par part au lieu d'encaisser b, et ce capital reste bloqué jusqu'à la revente ou au règlement. Différences de frais : 0 ; différences d'exécution : 0 (mêmes tailles des deux côtés par construction du miroir).

## 5. H30 = H25 (conversion seule)

- A (prudent, toutes périodes) : 62 positions avec paire rentable ; couverture médiane 100,0 % de la position au meilleur niveau ; capital engagé max +314 $ ; profit verrouillé valid. +348 $, test +207 $ ; Δ valid. −24 $ [−632 $ ; +540 $], test +7 $ [−572 $ ; +499 $]. Confirmé identique à H25 du rapport précédent (même règle, même moteur).
- B (prudent, toutes périodes) : 255 positions avec paire rentable ; couverture médiane 100,0 % de la position au meilleur niveau ; capital engagé max +475 $ ; profit verrouillé valid. +1 034 $, test +809 $ ; Δ valid. −988 $ [−2 155 $ ; +109 $], test +698 $ [−490 $ ; +1 938 $]. Confirmé identique à H25 du rapport précédent (même règle, même moteur).
- Fusion Up + Down : transaction on-chain, non observable ; comptée 1 $ au règlement (capital libéré tôt seulement en idéal).

## 6. Par jour (calendrier suisse), prudent, Δ vs GARDER, 50 $ indépendants (toutes périodes)

### A · désaccord 30 zone + modèle monte

| Règle | 07.10 | 08.10 | 09.10 | 10.10 | 11.10 | jours positifs |
|---|---|---|---|---|---|---|
| H27 preneur | +29 $ | −55 $ | −6 $ | +10 $ | +2 $ | 3/5 |
| H27 passif | +13 $ | −74 $ | −61 $ | −22 $ | +1 $ | 2/5 |
| VENTE seule (même instant, H27 preneur) | −1 $ | −172 $ | +36 $ | −96 $ | +61 $ | 2/5 |
| VENTE seule (même instant, H27 passif) | +7 $ | −170 $ | −16 $ | −91 $ | +30 $ | 2/5 |
| H28 preneur | +29 $ | −55 $ | −6 $ | +10 $ | +2 $ | 3/5 |
| H28 passif | +13 $ | −74 $ | −61 $ | −22 $ | +1 $ | 2/5 |
| H29 | +0 $ | +0 $ | −0 $ | +0 $ | +0 $ | 0/5 |
| H30 = H25 | −73 $ | −689 $ | +114 $ | −375 $ | +244 $ | 2/5 |

### B · V2-F corrigé 0,015 %

| Règle | 07.10 | 08.10 | 09.10 | 10.10 | 11.10 | jours positifs |
|---|---|---|---|---|---|---|
| H27 preneur | −55 $ | −12 $ | −77 $ | +15 $ | +36 $ | 2/5 |
| H27 passif | −24 $ | −57 $ | −94 $ | −94 $ | −28 $ | 0/5 |
| VENTE seule (même instant, H27 preneur) | −171 $ | −155 $ | −173 $ | +251 $ | −107 $ | 1/5 |
| VENTE seule (même instant, H27 passif) | −122 $ | −123 $ | −156 $ | +107 $ | −124 $ | 1/5 |
| H28 preneur | −55 $ | −12 $ | −77 $ | +15 $ | +36 $ | 2/5 |
| H28 passif | −24 $ | −57 $ | −94 $ | −94 $ | −28 $ | 0/5 |
| H29 | −0 $ | +0 $ | −0 $ | +0 $ | −0 $ | 0/5 |
| H30 = H25 | −677 $ | −659 $ | −697 $ | +906 $ | −447 $ | 1/5 |

## 7. Les données actuelles suffisent-elles ?

| Fantôme | Variante preneur (achat / vente au meilleur prix) | Variante passive (ordre limite) |
|---|---|---|
| H27 | **Suffisantes pour un premier verdict** : meilleur acheteur / vendeur + taille toutes les 0,3 s, des deux côtés. Limites : fenêtres < 0,3 s invisibles, pas de profondeur au-delà du meilleur niveau (vente ou rachat > taille affichée non mesurable), heure de réception seulement. | **Insuffisantes** : remplissage du rachat passif non mesurable (file d'attente inconnue, transactions seulement agrégées) ; résultats = bornes idéal / prudent / pessimiste. Il faut les enregistrements 50 ms de Dublin : carnet complet, transactions individuelles (prix, taille, côté), annulations, horodatage Polymarket. |
| H28 | Même chose que H27 (miroir exact) ; aucune donnée en plus n'est utile tant que les carnets restent miroirs. Seule vérification utile en direct : que le miroir tient aussi en profondeur et dans les ordres réellement exécutables. | Même chose que H27 passif. |
| H29 | Suffisantes pour les règles preneur (choix entre vendre, racheter, garder) ; mêmes limites de résolution 0,3 s et de profondeur. | Insuffisantes dès que la règle utilise un ordre passif. |
| H30 (= H25) | Suffisantes pour la décision et le P&L au meilleur niveau ; la quantité au-delà du meilleur niveau et les fenêtres < 0,3 s demandent la profondeur et la résolution 50 ms. Fusion : non observable (sans effet sur le P&L). | — |

Les photos 100 ms (3 niveaux, ~20 s autour du premier désaccord) ne couvrent presque jamais le moment des oscillations, qui arrivent plus tard dans le cycle : elles ne suffisent pas à valider la résolution. Le flux agrégé (1 s / 100 ms) dit qu'il y a eu des échanges, pas à quel prix ni si notre niveau a été touché.

Durée de calcul : 117 s.