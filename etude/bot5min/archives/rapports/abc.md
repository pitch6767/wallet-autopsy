# BOT95 — Expériences A (double ordre passif), B (survie du capital), C (qualité des entrées)

Étude hors ligne du 11.10.2026 — aucun bot, aucun workflow modifié, rien publié. Cohortes A et B du Hedge Lab, mêmes entrées. Apprentissage < 08.10 22:00 · validation → 10.10 10:25 · test inédit après (jusqu'au 11.10 07:55).

## Réponse courte (en tête)

- **A double passif (signaux A, k = 0, jusqu'à la fin)** : les deux jambes servies dans 61,6 % (borne optimiste) à 57,9 % (pessimiste) des 159 essais ; P&L total −1 390 $ (optimiste) / −933 $ (pessimiste), dont jambes seules −1 447 $ / −1 022 $. Bornes seulement : aucun résultat maker fiable.
- **A double passif (signaux B, k = 0, jusqu'à la fin)** : les deux jambes servies dans 71,6 % (borne optimiste) à 62,2 % (pessimiste) des 655 essais ; P&L total −4 173 $ (optimiste) / −3 935 $ (pessimiste), dont jambes seules −4 441 $ / −4 269 $. Bornes seulement : aucun résultat maker fiable.
- **A double passif (chaque cycle, ouverture + 10 s, k = 0, jusqu'à la fin)** : les deux jambes servies dans 83,2 % (borne optimiste) à 75,5 % (pessimiste) des 1133 essais ; P&L total −3 392 $ (optimiste) / −5 187 $ (pessimiste), dont jambes seules −3 883 $ / −5 637 $. Bornes seulement : aucun résultat maker fiable.
- **B survie (A, 250 $, 07.10 → 11.10, prudent)** : 5 $ : +126 $, creux −65 $, jamais sous la mise · 10 $ : +186 $, creux −130 $, jamais sous la mise · 15 $ : +183 $, creux −189 $, jamais sous la mise · 25 $ : +170 $, creux −342 $, jamais sous la mise · 50 $ : +241 $, creux −766 $, jamais sous la mise.
- **B survie (B, 250 $, 07.10 → 11.10, prudent)** : 5 $ : +25 $, creux −265 $, jamais sous la mise · 10 $ : −24 $, creux −582 $, jamais sous la mise · 15 $ : −80 $, creux −875 $, jamais sous la mise · 25 $ : −250 $, creux −1 179 $, ruine le 10.10 23:40 · 50 $ : −250 $, creux −1 337 $, ruine le 10.10 15:05.
- **C qualité (A)** : apprentissage : côté +1 733 $, écart −33 $, frais −67 $, délai −686 $ → délai 0,3 s (prudent − signal) ; validation : côté +910 $, écart −53 $, frais −103 $, délai −1 046 $ → délai 0,3 s (prudent − signal) ; inédit : côté +390 $, écart −38 $, frais −79 $, délai −684 $ → délai 0,3 s (prudent − signal).
- **C qualité (B)** : apprentissage : côté +2 631 $, écart −139 $, frais −301 $, délai −1 731 $ → délai 0,3 s (prudent − signal) ; validation : côté +1 442 $, écart −167 $, frais −350 $, délai −995 $ → délai 0,3 s (prudent − signal) ; inédit : côté +108 $, écart −126 $, frais −285 $, délai −1 279 $ → délai 0,3 s (prudent − signal).
- Les estimations de ruine sont des **illustrations** (bootstrap de quelques jours), pas des probabilités fiables.

## 0. Diagnostic de faisabilité (avant tout résultat)

| Expérience | Ce que les données actuelles permettent | Ce qui n'est qu'une borne | Ce qui exige l'enregistreur de Dublin |
|---|---|---|---|
| A — double ordre passif | savoir si le meilleur vendeur de chaque jeton a TOUCHÉ ou TRAVERSÉ nos prix (lignes 0,3 s), délai entre les deux, résultat officiel | tout remplissage : borne optimiste (rempli dès que le vendeur touche notre prix, quantité entière) et borne pessimiste (traversée d'1 c tenue ≥ 2 lignes, quantité affichée) | position dans la file d'attente, transactions individuelles à notre prix (prix, taille, côté, heure Polymarket), annulations / ajouts à notre niveau, carnet complet à 50 ms ; idéalement un vrai ordre de 1 part de chaque côté |
| B — survie du capital | rejeu chronologique exact des signaux, quantité affichée au meilleur niveau, délai 0,3 s, frais, capital partagé | taille au-delà du meilleur niveau (une mise de 50 $ peut dépasser la taille affichée : comptée au meilleur niveau seulement) ; probabilité de ruine (quelques jours seulement : illustration) | profondeur réelle pour les grosses mises ; plus de jours pour une vraie probabilité de ruine |
| C — qualité des entrées | décomposition exacte du P&L (côté, écart au milieu du carnet, frais), comparaison au côté opposé au même instant, régimes fixés sur l'apprentissage, effet du délai (0 / 0,3 / 0,6 s), calibration | « signal trop tard » et « moins cher dans les 30 s d'avant » sont RÉTROSPECTIFS (diagnostic, pas une stratégie) | heure Polymarket des carnets pour séparer retard réseau et retard du signal |

**Aucun résultat fiable de teneur d'ordre (maker) ne peut être annoncé avec les données actuelles** : l'expérience A ne donne que des bornes.

## A. Double ordre passif Up + Down (bornes seulement)

Au moment donné : ordre passif d'achat Up au meilleur acheteur Up − k c et ordre passif d'achat Down au meilleur acheteur Down − k c, même nombre de parts, 50 $ au total. Coût de la paire = (acheteur Up − k) + (acheteur Down − k) = 1 − écart vendeur-acheteur − 2k (carnets miroirs) : toujours < 1 ; frais teneur d'ordre supposés 0 (non vérifiés). Valable 60 s ou jusqu'à la fin − 5 s ; un ordre servi reste ; l'autre est annulé à l'échéance ; la jambe seule est gardée jusqu'au règlement. **Borne optimiste** : délai 0, rempli dès que le vendeur du jeton touche notre prix, quantité entière. **Borne pessimiste** : pose après 0,3 s, rempli seulement si le vendeur passe ≥ 1 c sous notre prix 2 lignes de suite, quantité affichée.

| Moments | k | Durée | Borne | Période | Essais | Coût paire médian | Les 2 jambes | 1 seule | Aucune | Délai entre jambes (médiane, s) | P&L paires complètes | P&L jambes seules | P&L total (tous essais) | Capital immobilisé moyen |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| signaux A | 0 c | 60 s | optimiste | apprentissage | 50 | 0,99 | 58,0 % | 42,0 % | 0,0 % | 6,90 | +16 $ | −494 $ | **−479 $** | +50 $ |
| signaux A | 0 c | 60 s | optimiste | validation | 62 | 0,99 | 59,7 % | 40,3 % | 0,0 % | 8,40 | +25 $ | −561 $ | **−536 $** | +50 $ |
| signaux A | 0 c | 60 s | optimiste | inédit | 47 | 0,99 | 59,6 % | 40,4 % | 0,0 % | 10,20 | +14 $ | −390 $ | **−376 $** | +50 $ |
| signaux A | 0 c | 60 s | pessimiste | apprentissage | 50 | 0,99 | 56,0 % | 44,0 % | 0,0 % | 9,15 | +24 $ | −245 $ | **−221 $** | +50 $ |
| signaux A | 0 c | 60 s | pessimiste | validation | 62 | 0,99 | 50,0 % | 48,4 % | 1,6 % | 7,80 | +30 $ | −353 $ | **−324 $** | +50 $ |
| signaux A | 0 c | 60 s | pessimiste | inédit | 47 | 0,99 | 53,2 % | 46,8 % | 0,0 % | 16,50 | +30 $ | −317 $ | **−287 $** | +50 $ |
| signaux A | 0 c | fin − 5 s | optimiste | apprentissage | 50 | 0,99 | 60,0 % | 40,0 % | 0,0 % | 7,80 | +16 $ | −503 $ | **−487 $** | +50 $ |
| signaux A | 0 c | fin − 5 s | optimiste | validation | 62 | 0,99 | 62,9 % | 37,1 % | 0,0 % | 10,20 | +26 $ | −544 $ | **−518 $** | +50 $ |
| signaux A | 0 c | fin − 5 s | optimiste | inédit | 47 | 0,99 | 61,7 % | 38,3 % | 0,0 % | 10,20 | +15 $ | −399 $ | **−385 $** | +50 $ |
| signaux A | 0 c | fin − 5 s | pessimiste | apprentissage | 50 | 0,99 | 64,0 % | 36,0 % | 0,0 % | 10,50 | +27 $ | −314 $ | **−286 $** | +50 $ |
| signaux A | 0 c | fin − 5 s | pessimiste | validation | 62 | 0,99 | 54,8 % | 45,2 % | 0,0 % | 8,55 | +31 $ | −383 $ | **−351 $** | +50 $ |
| signaux A | 0 c | fin − 5 s | pessimiste | inédit | 47 | 0,99 | 55,3 % | 44,7 % | 0,0 % | 16,65 | +30 $ | −326 $ | **−296 $** | +50 $ |
| signaux A | 1 c | 60 s | optimiste | apprentissage | 51 | 0,97 | 49,0 % | 51,0 % | 0,0 % | 6,30 | +40 $ | −486 $ | **−446 $** | +50 $ |
| signaux A | 1 c | 60 s | optimiste | validation | 62 | 0,97 | 54,8 % | 45,2 % | 0,0 % | 10,65 | +59 $ | −623 $ | **−563 $** | +50 $ |
| signaux A | 1 c | 60 s | optimiste | inédit | 47 | 0,97 | 53,2 % | 46,8 % | 0,0 % | 10,80 | +39 $ | −392 $ | **−353 $** | +50 $ |
| signaux A | 1 c | 60 s | pessimiste | apprentissage | 51 | 0,97 | 47,1 % | 52,9 % | 0,0 % | 13,20 | +45 $ | −211 $ | **−167 $** | +50 $ |
| signaux A | 1 c | 60 s | pessimiste | validation | 62 | 0,97 | 48,4 % | 50,0 % | 1,6 % | 8,55 | +61 $ | −352 $ | **−291 $** | +50 $ |
| signaux A | 1 c | 60 s | pessimiste | inédit | 47 | 0,97 | 44,7 % | 55,3 % | 0,0 % | 19,20 | +50 $ | −380 $ | **−330 $** | +50 $ |
| signaux A | 1 c | fin − 5 s | optimiste | apprentissage | 51 | 0,97 | 56,9 % | 43,1 % | 0,0 % | 9,90 | +46 $ | −554 $ | **−508 $** | +50 $ |
| signaux A | 1 c | fin − 5 s | optimiste | validation | 62 | 0,97 | 58,1 % | 41,9 % | 0,0 % | 11,40 | +62 $ | −607 $ | **−544 $** | +50 $ |
| signaux A | 1 c | fin − 5 s | optimiste | inédit | 47 | 0,97 | 55,3 % | 44,7 % | 0,0 % | 11,10 | +40 $ | −401 $ | **−361 $** | +50 $ |
| signaux A | 1 c | fin − 5 s | pessimiste | apprentissage | 51 | 0,97 | 58,8 % | 41,2 % | 0,0 % | 16,35 | +58 $ | −349 $ | **−292 $** | +50 $ |
| signaux A | 1 c | fin − 5 s | pessimiste | validation | 62 | 0,97 | 53,2 % | 46,8 % | 0,0 % | 9,60 | +66 $ | −383 $ | **−318 $** | +50 $ |
| signaux A | 1 c | fin − 5 s | pessimiste | inédit | 47 | 0,97 | 46,8 % | 53,2 % | 0,0 % | 19,35 | +52 $ | −390 $ | **−338 $** | +50 $ |
| signaux A | 2 c | 60 s | optimiste | apprentissage | 51 | 0,95 | 45,1 % | 54,9 % | 0,0 % | 9,90 | +62 $ | −459 $ | **−397 $** | +50 $ |
| signaux A | 2 c | 60 s | optimiste | validation | 62 | 0,95 | 46,8 % | 53,2 % | 0,0 % | 12,00 | +83 $ | −688 $ | **−605 $** | +50 $ |
| signaux A | 2 c | 60 s | optimiste | inédit | 47 | 0,95 | 51,1 % | 48,9 % | 0,0 % | 15,90 | +63 $ | −396 $ | **−332 $** | +50 $ |
| signaux A | 2 c | 60 s | pessimiste | apprentissage | 51 | 0,95 | 45,1 % | 54,9 % | 0,0 % | 12,30 | +66 $ | −217 $ | **−150 $** | +50 $ |
| signaux A | 2 c | 60 s | pessimiste | validation | 62 | 0,95 | 45,2 % | 53,2 % | 1,6 % | 11,25 | +87 $ | −400 $ | **−312 $** | +50 $ |
| signaux A | 2 c | 60 s | pessimiste | inédit | 47 | 0,95 | 40,4 % | 57,4 % | 2,1 % | 19,50 | +65 $ | −358 $ | **−293 $** | +50 $ |
| signaux A | 2 c | fin − 5 s | optimiste | apprentissage | 51 | 0,95 | 54,9 % | 45,1 % | 0,0 % | 13,50 | +75 $ | −545 $ | **−471 $** | +50 $ |
| signaux A | 2 c | fin − 5 s | optimiste | validation | 62 | 0,95 | 50,0 % | 50,0 % | 0,0 % | 13,50 | +88 $ | −672 $ | **−584 $** | +50 $ |
| signaux A | 2 c | fin − 5 s | optimiste | inédit | 47 | 0,95 | 53,2 % | 46,8 % | 0,0 % | 16,80 | +66 $ | −406 $ | **−340 $** | +50 $ |
| signaux A | 2 c | fin − 5 s | pessimiste | apprentissage | 51 | 0,95 | 54,9 % | 45,1 % | 0,0 % | 14,25 | +83 $ | −351 $ | **−268 $** | +50 $ |
| signaux A | 2 c | fin − 5 s | pessimiste | validation | 62 | 0,95 | 50,0 % | 50,0 % | 0,0 % | 12,00 | +95 $ | −432 $ | **−337 $** | +50 $ |
| signaux A | 2 c | fin − 5 s | pessimiste | inédit | 47 | 0,95 | 44,7 % | 53,2 % | 2,1 % | 19,50 | +73 $ | −386 $ | **−314 $** | +50 $ |
| signaux B | 0 c | 60 s | optimiste | apprentissage | 238 | 0,99 | 61,3 % | 37,8 % | 0,8 % | 6,61 | +86 $ | −1 761 $ | **−1 676 $** | +50 $ |
| signaux B | 0 c | 60 s | optimiste | validation | 239 | 0,99 | 62,8 % | 37,2 % | 0,0 % | 9,30 | +85 $ | −1 392 $ | **−1 307 $** | +50 $ |
| signaux B | 0 c | 60 s | optimiste | inédit | 178 | 0,99 | 68,5 % | 31,5 % | 0,0 % | 9,30 | +71 $ | −911 $ | **−840 $** | +50 $ |
| signaux B | 0 c | 60 s | pessimiste | apprentissage | 237 | 0,99 | 56,1 % | 41,8 % | 2,1 % | 7,80 | +129 $ | −1 249 $ | **−1 120 $** | +50 $ |
| signaux B | 0 c | 60 s | pessimiste | validation | 239 | 0,99 | 47,3 % | 51,5 % | 1,3 % | 12,30 | +77 $ | −1 455 $ | **−1 378 $** | +50 $ |
| signaux B | 0 c | 60 s | pessimiste | inédit | 178 | 0,99 | 59,0 % | 41,0 % | 0,0 % | 12,30 | +81 $ | −819 $ | **−738 $** | +50 $ |
| signaux B | 0 c | fin − 5 s | optimiste | apprentissage | 238 | 0,99 | 68,5 % | 31,1 % | 0,4 % | 8,40 | +95 $ | −1 897 $ | **−1 802 $** | +50 $ |
| signaux B | 0 c | fin − 5 s | optimiste | validation | 239 | 0,99 | 72,4 % | 27,6 % | 0,0 % | 12,60 | +96 $ | −1 506 $ | **−1 410 $** | +50 $ |
| signaux B | 0 c | fin − 5 s | optimiste | inédit | 178 | 0,99 | 74,7 % | 25,3 % | 0,0 % | 10,80 | +78 $ | −1 038 $ | **−960 $** | +50 $ |
| signaux B | 0 c | fin − 5 s | pessimiste | apprentissage | 237 | 0,99 | 63,7 % | 34,6 % | 1,7 % | 11,09 | +139 $ | −1 555 $ | **−1 415 $** | +50 $ |
| signaux B | 0 c | fin − 5 s | pessimiste | validation | 239 | 0,99 | 57,7 % | 41,4 % | 0,8 % | 16,20 | +92 $ | −1 768 $ | **−1 676 $** | +50 $ |
| signaux B | 0 c | fin − 5 s | pessimiste | inédit | 178 | 0,99 | 66,3 % | 33,7 % | 0,0 % | 14,55 | +102 $ | −946 $ | **−844 $** | +50 $ |
| signaux B | 1 c | 60 s | optimiste | apprentissage | 239 | 0,97 | 56,5 % | 42,3 % | 1,3 % | 8,40 | +220 $ | −1 796 $ | **−1 576 $** | +50 $ |
| signaux B | 1 c | 60 s | optimiste | validation | 239 | 0,97 | 56,1 % | 43,1 % | 0,8 % | 14,70 | +215 $ | −1 438 $ | **−1 223 $** | +50 $ |
| signaux B | 1 c | 60 s | optimiste | inédit | 178 | 0,97 | 59,6 % | 40,4 % | 0,0 % | 11,70 | +173 $ | −1 016 $ | **−843 $** | +50 $ |
| signaux B | 1 c | 60 s | pessimiste | apprentissage | 239 | 0,97 | 49,4 % | 48,1 % | 2,5 % | 11,10 | +245 $ | −1 335 $ | **−1 090 $** | +50 $ |
| signaux B | 1 c | 60 s | pessimiste | validation | 239 | 0,97 | 41,0 % | 57,3 % | 1,7 % | 15,00 | +168 $ | −1 662 $ | **−1 494 $** | +50 $ |
| signaux B | 1 c | 60 s | pessimiste | inédit | 178 | 0,97 | 52,2 % | 47,2 % | 0,6 % | 19,80 | +165 $ | −897 $ | **−732 $** | +50 $ |
| signaux B | 1 c | fin − 5 s | optimiste | apprentissage | 239 | 0,97 | 65,3 % | 33,9 % | 0,8 % | 10,80 | +253 $ | −1 947 $ | **−1 694 $** | +50 $ |
| signaux B | 1 c | fin − 5 s | optimiste | validation | 239 | 0,97 | 66,5 % | 32,6 % | 0,8 % | 16,50 | +254 $ | −1 698 $ | **−1 444 $** | +50 $ |
| signaux B | 1 c | fin − 5 s | optimiste | inédit | 178 | 0,97 | 68,0 % | 32,0 % | 0,0 % | 12,60 | +197 $ | −1 197 $ | **−1 000 $** | +50 $ |
| signaux B | 1 c | fin − 5 s | pessimiste | apprentissage | 239 | 0,97 | 58,2 % | 39,7 % | 2,1 % | 15,60 | +280 $ | −1 721 $ | **−1 440 $** | +50 $ |
| signaux B | 1 c | fin − 5 s | pessimiste | validation | 239 | 0,97 | 52,7 % | 46,0 % | 1,3 % | 21,75 | +213 $ | −2 002 $ | **−1 789 $** | +50 $ |
| signaux B | 1 c | fin − 5 s | pessimiste | inédit | 178 | 0,97 | 61,2 % | 38,2 % | 0,6 % | 22,50 | +206 $ | −1 043 $ | **−838 $** | +50 $ |
| signaux B | 2 c | 60 s | optimiste | apprentissage | 235 | 0,95 | 52,3 % | 47,2 % | 0,4 % | 11,40 | +336 $ | −1 719 $ | **−1 384 $** | +50 $ |
| signaux B | 2 c | 60 s | optimiste | validation | 235 | 0,95 | 51,1 % | 48,9 % | 0,0 % | 16,50 | +322 $ | −1 652 $ | **−1 330 $** | +50 $ |
| signaux B | 2 c | 60 s | optimiste | inédit | 178 | 0,95 | 53,9 % | 45,5 % | 0,6 % | 13,80 | +262 $ | −1 022 $ | **−761 $** | +50 $ |
| signaux B | 2 c | 60 s | pessimiste | apprentissage | 236 | 0,95 | 46,2 % | 52,1 % | 1,7 % | 14,40 | +344 $ | −1 415 $ | **−1 071 $** | +50 $ |
| signaux B | 2 c | 60 s | pessimiste | validation | 238 | 0,95 | 34,9 % | 63,0 % | 2,1 % | 19,20 | +233 $ | −1 697 $ | **−1 465 $** | +50 $ |
| signaux B | 2 c | 60 s | pessimiste | inédit | 178 | 0,95 | 43,3 % | 55,1 % | 1,7 % | 19,80 | +224 $ | −987 $ | **−763 $** | +50 $ |
| signaux B | 2 c | fin − 5 s | optimiste | apprentissage | 235 | 0,95 | 63,0 % | 37,0 % | 0,0 % | 17,85 | +402 $ | −2 000 $ | **−1 598 $** | +50 $ |
| signaux B | 2 c | fin − 5 s | optimiste | validation | 235 | 0,95 | 63,4 % | 36,6 % | 0,0 % | 20,40 | +399 $ | −1 861 $ | **−1 462 $** | +50 $ |
| signaux B | 2 c | fin − 5 s | optimiste | inédit | 178 | 0,95 | 65,2 % | 34,3 % | 0,6 % | 19,50 | +316 $ | −1 240 $ | **−924 $** | +50 $ |
| signaux B | 2 c | fin − 5 s | pessimiste | apprentissage | 236 | 0,95 | 55,5 % | 43,2 % | 1,3 % | 19,20 | +406 $ | −1 799 $ | **−1 394 $** | +50 $ |
| signaux B | 2 c | fin − 5 s | pessimiste | validation | 238 | 0,95 | 47,9 % | 50,4 % | 1,7 % | 26,25 | +317 $ | −2 101 $ | **−1 784 $** | +50 $ |
| signaux B | 2 c | fin − 5 s | pessimiste | inédit | 178 | 0,95 | 55,6 % | 43,3 % | 1,1 % | 25,80 | +296 $ | −1 217 $ | **−921 $** | +50 $ |
| chaque cycle, ouverture + 10 s | 0 c | 60 s | optimiste | apprentissage | 448 | 0,99 | 76,6 % | 23,2 % | 0,2 % | 6,60 | +180 $ | −1 520 $ | **−1 340 $** | +50 $ |
| chaque cycle, ouverture + 10 s | 0 c | 60 s | optimiste | validation | 427 | 0,99 | 68,4 % | 31,6 % | 0,0 % | 8,85 | +153 $ | −1 435 $ | **−1 282 $** | +50 $ |
| chaque cycle, ouverture + 10 s | 0 c | 60 s | optimiste | inédit | 258 | 0,99 | 68,6 % | 31,4 % | 0,0 % | 9,30 | +90 $ | −610 $ | **−520 $** | +50 $ |
| chaque cycle, ouverture + 10 s | 0 c | 60 s | pessimiste | apprentissage | 448 | 0,99 | 65,2 % | 34,6 % | 0,2 % | 9,60 | +153 $ | −2 205 $ | **−2 052 $** | +50 $ |
| chaque cycle, ouverture + 10 s | 0 c | 60 s | pessimiste | validation | 427 | 0,99 | 56,0 % | 44,0 % | 0,0 % | 14,10 | +125 $ | −2 011 $ | **−1 885 $** | +50 $ |
| chaque cycle, ouverture + 10 s | 0 c | 60 s | pessimiste | inédit | 258 | 0,99 | 52,7 % | 47,3 % | 0,0 % | 13,95 | +73 $ | −1 078 $ | **−1 005 $** | +50 $ |
| chaque cycle, ouverture + 10 s | 0 c | fin − 5 s | optimiste | apprentissage | 448 | 0,99 | 85,5 % | 14,5 % | 0,0 % | 8,10 | +202 $ | −1 350 $ | **−1 148 $** | +50 $ |
| chaque cycle, ouverture + 10 s | 0 c | fin − 5 s | optimiste | validation | 427 | 0,99 | 82,0 % | 18,0 % | 0,0 % | 11,85 | +182 $ | −1 561 $ | **−1 379 $** | +50 $ |
| chaque cycle, ouverture + 10 s | 0 c | fin − 5 s | optimiste | inédit | 258 | 0,99 | 81,4 % | 18,6 % | 0,0 % | 12,15 | +107 $ | −972 $ | **−866 $** | +50 $ |
| chaque cycle, ouverture + 10 s | 0 c | fin − 5 s | pessimiste | apprentissage | 448 | 0,99 | 77,5 % | 22,5 % | 0,0 % | 13,20 | +184 $ | −2 075 $ | **−1 891 $** | +50 $ |
| chaque cycle, ouverture + 10 s | 0 c | fin − 5 s | pessimiste | validation | 427 | 0,99 | 74,5 % | 25,5 % | 0,0 % | 22,20 | +165 $ | −2 209 $ | **−2 043 $** | +50 $ |
| chaque cycle, ouverture + 10 s | 0 c | fin − 5 s | pessimiste | inédit | 258 | 0,99 | 73,6 % | 26,4 % | 0,0 % | 23,10 | +101 $ | −1 353 $ | **−1 252 $** | +50 $ |
| chaque cycle, ouverture + 10 s | 1 c | 60 s | optimiste | apprentissage | 449 | 0,97 | 67,3 % | 32,5 % | 0,2 % | 9,30 | +473 $ | −1 981 $ | **−1 508 $** | +50 $ |
| chaque cycle, ouverture + 10 s | 1 c | 60 s | optimiste | validation | 426 | 0,97 | 58,0 % | 42,0 % | 0,0 % | 13,50 | +387 $ | −1 891 $ | **−1 504 $** | +50 $ |
| chaque cycle, ouverture + 10 s | 1 c | 60 s | optimiste | inédit | 258 | 0,97 | 56,6 % | 43,4 % | 0,0 % | 13,50 | +226 $ | −876 $ | **−651 $** | +50 $ |
| chaque cycle, ouverture + 10 s | 1 c | 60 s | pessimiste | apprentissage | 449 | 0,97 | 54,1 % | 45,7 % | 0,2 % | 14,40 | +380 $ | −2 711 $ | **−2 331 $** | +50 $ |
| chaque cycle, ouverture + 10 s | 1 c | 60 s | pessimiste | validation | 426 | 0,97 | 46,7 % | 52,8 % | 0,5 % | 18,00 | +312 $ | −1 990 $ | **−1 679 $** | +50 $ |
| chaque cycle, ouverture + 10 s | 1 c | 60 s | pessimiste | inédit | 258 | 0,97 | 44,6 % | 55,4 % | 0,0 % | 18,29 | +181 $ | −1 203 $ | **−1 022 $** | +50 $ |
| chaque cycle, ouverture + 10 s | 1 c | fin − 5 s | optimiste | apprentissage | 449 | 0,97 | 79,3 % | 20,7 % | 0,0 % | 12,75 | +560 $ | −1 859 $ | **−1 299 $** | +50 $ |
| chaque cycle, ouverture + 10 s | 1 c | fin − 5 s | optimiste | validation | 426 | 0,97 | 76,5 % | 23,5 % | 0,0 % | 22,05 | +509 $ | −2 071 $ | **−1 561 $** | +50 $ |
| chaque cycle, ouverture + 10 s | 1 c | fin − 5 s | optimiste | inédit | 258 | 0,97 | 76,0 % | 24,0 % | 0,0 % | 20,85 | +303 $ | −1 212 $ | **−909 $** | +50 $ |
| chaque cycle, ouverture + 10 s | 1 c | fin − 5 s | pessimiste | apprentissage | 449 | 0,97 | 71,5 % | 28,5 % | 0,0 % | 21,00 | +504 $ | −2 606 $ | **−2 102 $** | +50 $ |
| chaque cycle, ouverture + 10 s | 1 c | fin − 5 s | pessimiste | validation | 426 | 0,97 | 69,0 % | 31,0 % | 0,0 % | 30,15 | +460 $ | −2 593 $ | **−2 133 $** | +50 $ |
| chaque cycle, ouverture + 10 s | 1 c | fin − 5 s | pessimiste | inédit | 258 | 0,97 | 69,4 % | 30,6 % | 0,0 % | 33,30 | +282 $ | −1 596 $ | **−1 314 $** | +50 $ |
| chaque cycle, ouverture + 10 s | 2 c | 60 s | optimiste | apprentissage | 448 | 0,95 | 56,5 % | 43,3 % | 0,2 % | 12,90 | +671 $ | −2 567 $ | **−1 896 $** | +50 $ |
| chaque cycle, ouverture + 10 s | 2 c | 60 s | optimiste | validation | 426 | 0,95 | 48,6 % | 50,9 % | 0,5 % | 16,80 | +549 $ | −1 757 $ | **−1 208 $** | +50 $ |
| chaque cycle, ouverture + 10 s | 2 c | 60 s | optimiste | inédit | 258 | 0,95 | 46,9 % | 53,1 % | 0,0 % | 17,40 | +318 $ | −1 131 $ | **−812 $** | +50 $ |
| chaque cycle, ouverture + 10 s | 2 c | 60 s | pessimiste | apprentissage | 448 | 0,95 | 47,8 % | 51,8 % | 0,4 % | 16,50 | +561 $ | −2 806 $ | **−2 245 $** | +50 $ |
| chaque cycle, ouverture + 10 s | 2 c | 60 s | pessimiste | validation | 426 | 0,95 | 38,3 % | 60,8 % | 0,9 % | 21,60 | +433 $ | −2 315 $ | **−1 882 $** | +50 $ |
| chaque cycle, ouverture + 10 s | 2 c | 60 s | pessimiste | inédit | 258 | 0,95 | 36,8 % | 63,2 % | 0,0 % | 18,90 | +254 $ | −1 200 $ | **−946 $** | +50 $ |
| chaque cycle, ouverture + 10 s | 2 c | fin − 5 s | optimiste | apprentissage | 448 | 0,95 | 73,4 % | 26,6 % | 0,0 % | 20,70 | +874 $ | −2 441 $ | **−1 567 $** | +50 $ |
| chaque cycle, ouverture + 10 s | 2 c | fin − 5 s | optimiste | validation | 426 | 0,95 | 70,9 % | 29,1 % | 0,0 % | 29,40 | +800 $ | −2 448 $ | **−1 648 $** | +50 $ |
| chaque cycle, ouverture + 10 s | 2 c | fin − 5 s | optimiste | inédit | 258 | 0,95 | 70,5 % | 29,5 % | 0,0 % | 33,15 | +479 $ | −1 519 $ | **−1 040 $** | +50 $ |
| chaque cycle, ouverture + 10 s | 2 c | fin − 5 s | pessimiste | apprentissage | 448 | 0,95 | 68,3 % | 31,5 % | 0,2 % | 26,25 | +807 $ | −2 910 $ | **−2 102 $** | +50 $ |
| chaque cycle, ouverture + 10 s | 2 c | fin − 5 s | pessimiste | validation | 426 | 0,95 | 64,8 % | 35,2 % | 0,0 % | 37,20 | +731 $ | −3 007 $ | **−2 275 $** | +50 $ |
| chaque cycle, ouverture + 10 s | 2 c | fin − 5 s | pessimiste | inédit | 258 | 0,95 | 65,5 % | 34,5 % | 0,0 % | 44,10 | +451 $ | −1 824 $ | **−1 374 $** | +50 $ |

Lecture : l'écart entre la borne optimiste et la borne pessimiste EST l'incertitude ; la vraie valeur est quelque part entre les deux (ou en dessous si nous sommes servis surtout quand le prix part contre nous — sélection adverse, non mesurable ici).
Attention : ce sont des bornes sur le REMPLISSAGE, pas sur le P&L — la borne « pessimiste » peut perdre moins que l'« optimiste », car une jambe seule est presque toujours celle dont le prix est parti contre nous (le vendeur ne descend jusqu'à notre prix que quand ce jeton perd de la valeur) : les jambes seules portent toute la perte, les paires complètes ne rapportent que l'écart (~1 c par paire).

**Données live nécessaires pour un vrai résultat** : (1) chaque transaction des deux jetons (prix, taille, côté preneur, heure Polymarket) ; (2) les événements du carnet à notre niveau (ajout / retrait / taille avant-après) pour suivre la file devant nous ; (3) carnet complet des deux jetons à 50 ms ; (4) idéalement un ordre réel de 1 part de chaque côté et son sort (rempli, quand, combien) ; (5) frais teneur d'ordre réellement facturés.

## B. Survie du capital — 250 $ partagés, rejeu chronologique, prudent (0,3 s, meilleur niveau, frais)

Entrée = min(mise, capital) ; capital < 1 $ → entrée refusée. « Sous la mise » = premier moment où le capital tombe sous la mise initiale (entrées réduites). Jackpots manqués = positions qui auraient rapporté ≥ 4 × la mise avec la mise pleine mais ont été réduites ou refusées faute de capital (en $ : gain manqué). Chaque période repart de 250 $ ; « tout » = un seul portefeuille du 07.10 au 11.10.

### cohorte A (désaccord 30 zone + modèle monte)

| Mise | Période | Positions jouées | P&L | Capital final | Capital le plus bas | Creux max | Sous la mise le | Ruine (capital < 1 $) le | Entrées réduites / refusées | Jackpots manqués (n · $) | Plus longue série perdante |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 5 $ | apprentissage | 26 | +111 $ | +361 $ | +231 $ | −19 $ | — | — | 0 / 0 | 0 · +0 $ | 3 |
| 5 $ | validation | 37 | +1 $ | +251 $ | +212 $ | −44 $ | — | — | 0 / 0 | 0 · +0 $ | 9 |
| 5 $ | inédit | 34 | +14 $ | +264 $ | +226 $ | −65 $ | — | — | 0 / 0 | 0 · +0 $ | 13 |
| 5 $ | tout | 97 | +126 $ | +376 $ | +231 $ | −65 $ | — | — | 0 / 0 | 0 · +0 $ | 13 |
| 10 $ | apprentissage | 26 | +227 $ | +477 $ | +211 $ | −39 $ | — | — | 0 / 0 | 0 · +0 $ | 3 |
| 10 $ | validation | 37 | −13 $ | +237 $ | +175 $ | −81 $ | — | — | 0 / 0 | 0 · +0 $ | 9 |
| 10 $ | inédit | 34 | −28 $ | +222 $ | +202 $ | −130 $ | — | — | 0 / 0 | 0 · +0 $ | 13 |
| 10 $ | tout | 97 | +186 $ | +436 $ | +211 $ | −130 $ | — | — | 0 / 0 | 0 · +0 $ | 13 |
| 15 $ | apprentissage | 26 | +311 $ | +561 $ | +191 $ | −59 $ | — | — | 0 / 0 | 0 · +0 $ | 3 |
| 15 $ | validation | 37 | −51 $ | +199 $ | +138 $ | −120 $ | — | — | 0 / 0 | 0 · +0 $ | 9 |
| 15 $ | inédit | 34 | −76 $ | +174 $ | +174 $ | −189 $ | — | — | 0 / 0 | 0 · +0 $ | 13 |
| 15 $ | tout | 97 | +183 $ | +433 $ | +191 $ | −189 $ | — | — | 0 / 0 | 0 · +0 $ | 13 |
| 25 $ | apprentissage | 26 | +493 $ | +743 $ | +161 $ | −89 $ | — | — | 0 / 0 | 0 · +0 $ | 3 |
| 25 $ | validation | 37 | −146 $ | +104 $ | +74 $ | −195 $ | — | — | 0 / 0 | 0 · +0 $ | 9 |
| 25 $ | inédit | 34 | −177 $ | +73 $ | +73 $ | −274 $ | — | — | 0 / 0 | 0 · +0 $ | 13 |
| 25 $ | tout | 97 | +170 $ | +420 $ | +161 $ | −342 $ | — | — | 0 / 0 | 0 · +0 $ | 13 |
| 50 $ | apprentissage | 26 | +946 $ | +1 196 $ | +100 $ | −150 $ | — | — | 0 / 0 | 0 · +0 $ | 3 |
| 50 $ | validation | 21 | −250 $ | +0 $ | +0 $ | −312 $ | 09.10 12:35 | 10.10 00:20 | 4 / 16 | 4 · +401 $ | 9 |
| 50 $ | inédit | 30 | −250 $ | +0 $ | +0 $ | −362 $ | 11.10 03:45 | 11.10 04:50 | 2 / 4 | 0 · +0 $ | 9 |
| 50 $ | tout | 97 | +241 $ | +491 $ | +100 $ | −766 $ | — | — | 0 / 0 | 0 · +0 $ | 13 |

Distribution des séries perdantes (portefeuille « tout », longueur : nombre de séries) :

- mise 5 $ : 1 → 3, 2 → 8, 3 → 4, 5 → 2, 9 → 2, 13 → 1
- mise 10 $ : 1 → 3, 2 → 8, 3 → 4, 5 → 2, 9 → 2, 13 → 1
- mise 15 $ : 1 → 3, 2 → 8, 3 → 4, 5 → 2, 9 → 2, 13 → 1
- mise 25 $ : 1 → 3, 2 → 8, 3 → 4, 5 → 2, 9 → 2, 13 → 1
- mise 50 $ : 1 → 3, 2 → 8, 3 → 4, 5 → 2, 9 → 2, 13 → 1

P&L par jour (calendrier suisse, portefeuille « tout ») :

| Mise | 07.10 | 08.10 | 09.10 | 10.10 | 11.10 |
|---|---|---|---|---|---|
| 5 $ | +31 $ | +76 $ | −33 $ | +113 $ | −60 $ |
| 10 $ | +62 $ | +155 $ | −65 $ | +154 $ | −120 $ |
| 15 $ | +68 $ | +227 $ | −97 $ | +158 $ | −174 $ |
| 25 $ | +91 $ | +383 $ | −157 $ | +102 $ | −249 $ |
| 50 $ | +160 $ | +767 $ | −239 $ | −32 $ | −415 $ |

### cohorte B (V2-F corrigé 0,015 %)

| Mise | Période | Positions jouées | P&L | Capital final | Capital le plus bas | Creux max | Sous la mise le | Ruine (capital < 1 $) le | Entrées réduites / refusées | Jackpots manqués (n · $) | Plus longue série perdante |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 5 $ | apprentissage | 113 | +54 $ | +304 $ | +226 $ | −57 $ | — | — | 0 / 0 | 0 · +0 $ | 7 |
| 5 $ | validation | 144 | +143 $ | +393 $ | +245 $ | −92 $ | — | — | 0 / 0 | 0 · +0 $ | 10 |
| 5 $ | inédit | 112 | −173 $ | +77 $ | +58 $ | −192 $ | — | — | 0 / 0 | 0 · +0 $ | 17 |
| 5 $ | tout | 369 | +25 $ | +275 $ | +226 $ | −265 $ | — | — | 0 / 0 | 0 · +0 $ | 17 |
| 10 $ | apprentissage | 113 | +92 $ | +342 $ | +201 $ | −106 $ | — | — | 0 / 0 | 0 · +0 $ | 7 |
| 10 $ | validation | 144 | +273 $ | +523 $ | +238 $ | −195 $ | — | — | 0 / 0 | 0 · +0 $ | 10 |
| 10 $ | inédit | 49 | −250 $ | +0 $ | +0 $ | −250 $ | 10.10 20:15 | 10.10 20:25 | 1 / 63 | 3 · +133 $ | 10 |
| 10 $ | tout | 369 | −24 $ | +226 $ | +191 $ | −582 $ | — | — | 0 / 0 | 0 · +0 $ | 17 |
| 15 $ | apprentissage | 113 | +119 $ | +369 $ | +175 $ | −154 $ | — | — | 0 / 0 | 0 · +0 $ | 7 |
| 15 $ | validation | 144 | +380 $ | +630 $ | +230 $ | −299 $ | — | — | 0 / 0 | 0 · +0 $ | 10 |
| 15 $ | inédit | 33 | −250 $ | +0 $ | +0 $ | −250 $ | 10.10 15:15 | 10.10 16:40 | 4 / 79 | 5 · +185 $ | 10 |
| 15 $ | tout | 369 | −80 $ | +170 $ | +117 $ | −875 $ | — | — | 0 / 0 | 0 · +0 $ | 17 |
| 25 $ | apprentissage | 113 | +203 $ | +453 $ | +140 $ | −259 $ | — | — | 0 / 0 | 0 · +0 $ | 7 |
| 25 $ | validation | 144 | +337 $ | +587 $ | +200 $ | −485 $ | — | — | 0 / 0 | 0 · +0 $ | 10 |
| 25 $ | inédit | 20 | −250 $ | +0 $ | +0 $ | −250 $ | 10.10 14:35 | 10.10 14:40 | 1 / 92 | 5 · +293 $ | 6 |
| 25 $ | tout | 326 | −250 $ | +0 $ | +0 $ | −1 179 $ | 10.10 23:35 | 10.10 23:40 | 1 / 43 | 3 · +274 $ | 15 |
| 50 $ | apprentissage | 113 | +460 $ | +710 $ | +70 $ | −458 $ | — | — | 0 / 0 | 0 · +0 $ | 7 |
| 50 $ | validation | 141 | −250 $ | +0 $ | +0 $ | −873 $ | 09.10 15:20 | 10.10 10:10 | 3 / 3 | 0 · +0 $ | 10 |
| 50 $ | inédit | 16 | −250 $ | +0 $ | +0 $ | −267 $ | 10.10 13:55 | 10.10 14:10 | 2 / 96 | 5 · +458 $ | 6 |
| 50 $ | tout | 281 | −250 $ | +0 $ | +0 $ | −1 337 $ | 10.10 14:55 | 10.10 15:05 | 1 / 88 | 5 · +458 $ | 10 |

Distribution des séries perdantes (portefeuille « tout », longueur : nombre de séries) :

- mise 5 $ : 1 → 29, 2 → 18, 3 → 7, 4 → 7, 5 → 7, 6 → 4, 7 → 3, 8 → 1, 9 → 1, 10 → 2, 15 → 1, 17 → 1
- mise 10 $ : 1 → 29, 2 → 18, 3 → 7, 4 → 7, 5 → 7, 6 → 4, 7 → 3, 8 → 1, 9 → 1, 10 → 2, 15 → 1, 17 → 1
- mise 15 $ : 1 → 29, 2 → 18, 3 → 7, 4 → 7, 5 → 7, 6 → 4, 7 → 3, 8 → 1, 9 → 1, 10 → 2, 15 → 1, 17 → 1
- mise 25 $ : 1 → 25, 2 → 17, 3 → 8, 4 → 6, 5 → 5, 6 → 4, 7 → 3, 8 → 1, 9 → 1, 10 → 2, 15 → 1
- mise 50 $ : 1 → 24, 2 → 15, 3 → 6, 4 → 5, 5 → 5, 6 → 3, 7 → 3, 8 → 1, 9 → 2, 10 → 1

P&L par jour (calendrier suisse, portefeuille « tout ») :

| Mise | 07.10 | 08.10 | 09.10 | 10.10 | 11.10 |
|---|---|---|---|---|---|
| 5 $ | +52 $ | +24 $ | +169 $ | −228 $ | +7 $ |
| 10 $ | +86 $ | +46 $ | +339 $ | −481 $ | −15 $ |
| 15 $ | +97 $ | +75 $ | +493 $ | −709 $ | −36 $ |
| 25 $ | +124 $ | +127 $ | +549 $ | −1 050 $ | +0 $ |
| 50 $ | +191 $ | +243 $ | +442 $ | −1 126 $ | +0 $ |

**Probabilité de ruine — ILLUSTRATION SEULEMENT, pas une estimation fiable** (quelques jours de données, régimes changeants) : tirage de 24 blocs d'une heure ; part des tirages où le capital passe sous la mise en 24 h.

| Cohorte | Mise | Blocs de l'apprentissage seulement | Blocs de toutes les périodes |
|---|---|---|---|
| A | 5 $ | 0,0 % | 0,0 % |
| A | 10 $ | 0,0 % | 0,1 % |
| A | 15 $ | 0,0 % | 1,5 % |
| A | 25 $ | 0,1 % | 13,2 % |
| A | 50 $ | 4,1 % | 45,8 % |
| B | 5 $ | 0,0 % | 0,5 % |
| B | 10 $ | 0,6 % | 18,1 % |
| B | 15 $ | 4,2 % | 38,6 % |
| B | 25 $ | 16,4 % | 61,4 % |
| B | 50 $ | 41,5 % | 83,3 % |

## C. Qualité des entrées — d'où viennent les pertes ?

Décomposition exacte, entrée au signal (délai 0, meilleur vendeur, quantité affichée, 50 $) : **P&L = choix du côté + écart payé + frais**, avec choix du côté = parts × (issue − milieu du carnet) [le milieu = probabilité implicite de Polymarket] ; écart payé = − parts × (prix payé − milieu) ; frais = − parts × frais. Puis : côté opposé acheté au même instant (même règle de taille) ; prix vs meilleur vendeur des 5 s précédentes (connu à la décision, mais la règle n'était pas vraie) ; « presque vrai plus tôt » et « moins cher dans les 30 s d'avant » = **RÉTROSPECTIF** ; exécution réelle (idéal 0 s / prudent 0,3 s / pessimiste 0,6 s).

| Cohorte | Période | Positions | Gagnées | P&L au signal | (1) choix du côté vs milieu | (2) écart payé | frais | Côté opposé même instant | Prix vs min. 5 s avant | Rétro : presque vrai plus tôt (n · P&L) | Rétro : min. 30 s avant | (5) idéal · prudent · pessimiste (entrées) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A | apprentissage | 51 | 39,2 % | **+1 632 $** | +1 733 $ | −33 $ | −67 $ | −578 $ | −311 $ | 49 · +1 220 $ | +3 246 $ | +1 632 $ (51) · +946 $ (26) · +594 $ (19) |
| A | validation | 62 | 37,1 % | **+753 $** | +910 $ | −53 $ | −103 $ | −705 $ | −259 $ | 58 · +1 432 $ | +4 825 $ | +753 $ (62) · −293 $ (37) · −182 $ (31) |
| A | inédit | 47 | 27,7 % | **+273 $** | +390 $ | −38 $ | −79 $ | −382 $ | −176 $ | 45 · −45 $ | +1 744 $ | +273 $ (47) · −411 $ (34) · −269 $ (30) |
| B | apprentissage | 238 | 38,7 % | **+2 191 $** | +2 631 $ | −139 $ | −301 $ | −2 415 $ | −363 $ | 187 · +711 $ | +8 722 $ | +2 191 $ (238) · +460 $ (113) · −40 $ (97) |
| B | validation | 237 | 32,9 % | **+926 $** | +1 442 $ | −167 $ | −350 $ | −1 137 $ | −452 $ | 186 · +1 174 $ | +6 885 $ | +926 $ (237) · −70 $ (144) · −593 $ (120) |
| B | inédit | 178 | 28,1 % | **−304 $** | +108 $ | −126 $ | −285 $ | −637 $ | −130 $ | 135 · −774 $ | +2 675 $ | −304 $ (178) · −1 583 $ (112) · −1 304 $ (99) |

### (4) Régimes (fixés à l'avance / sur l'apprentissage : volatilité perp < 2 $/s = calme ; tendance 15 min ≥ médiane de l'apprentissage = directionnel ; bloc de 6 h UTC)

| Cohorte | Régime | app. : n · P&L | valid. : n · P&L | test : n · P&L |
|---|---|---|---|---|
| A | calme | 2 · −2 $ | 23 · −267 $ | 44 · +380 $ |
| A | agité | 48 · +1 672 $ | 37 · +1 100 $ | 3 · −107 $ |
| A | directionnel | 27 · +437 $ | 28 · +732 $ | 21 · −180 $ |
| A | oscillant | 23 · +1 233 $ | 32 · +23 $ | 26 · +453 $ |
| A | 00-06 UTC | 8 · +148 $ | 20 · +29 $ | 13 · −53 $ |
| A | 06-12 UTC | 26 · +690 $ | 20 · +130 $ | 5 · +25 $ |
| A | 12-18 UTC | 7 · +361 $ | 4 · +4 $ | 13 · +92 $ |
| A | 18-24 UTC | 10 · +433 $ | 18 · +590 $ | 16 · +209 $ |
| B | calme | 14 · −212 $ | 82 · +153 $ | 158 · −491 $ |
| B | agité | 223 · +2 409 $ | 149 · +818 $ | 20 · +188 $ |
| B | directionnel | 118 · +1 605 $ | 127 · +164 $ | 90 · −90 $ |
| B | oscillant | 114 · +641 $ | 103 · +973 $ | 88 · −214 $ |
| B | 00-06 UTC | 39 · +659 $ | 82 · −251 $ | 46 · +260 $ |
| B | 06-12 UTC | 84 · +889 $ | 63 · +107 $ | 31 · −60 $ |
| B | 12-18 UTC | 64 · +503 $ | 26 · +341 $ | 51 · −280 $ |
| B | 18-24 UTC | 51 · +139 $ | 66 · +729 $ | 50 · −223 $ |

### Calibration à l'entrée : le modèle a-t-il un avantage réel ?

| Cohorte | Période | Tranche de proba du modèle (notre côté) | n | Proba modèle moyenne | Prix payé moyen | Milieu moyen (Polymarket) | Taux de gain réel | Gain réel − prix payé − frais (par part) |
|---|---|---|---|---|---|---|---|---|
| A | apprentissage | 0,45-0,55 | 39 | 0,50 | 0,18 | 0,17 | 35,9 % | 0,172 |
| A | apprentissage | 0,55-0,65 | 9 | 0,59 | 0,23 | 0,22 | 44,4 % | 0,202 |
| A | apprentissage | 0,65-1,00 | 3 | 0,70 | 0,24 | 0,24 | 66,7 % | 0,414 |
| A | apprentissage | **toutes** | 51 | 0,53 | 0,19 | 0,18 | **39,2 %** | **0,192** |
| A | validation | 0,45-0,55 | 42 | 0,49 | 0,17 | 0,16 | 31,0 % | 0,128 |
| A | validation | 0,55-0,65 | 18 | 0,59 | 0,23 | 0,23 | 50,0 % | 0,252 |
| A | validation | 0,65-1,00 | 2 | 0,68 | 0,31 | 0,29 | 50,0 % | 0,175 |
| A | validation | **toutes** | 62 | 0,52 | 0,19 | 0,19 | **37,1 %** | **0,166** |
| A | inédit | 0,45-0,55 | 42 | 0,49 | 0,17 | 0,17 | 21,4 % | 0,033 |
| A | inédit | 0,55-0,65 | 4 | 0,60 | 0,25 | 0,25 | 75,0 % | 0,484 |
| A | inédit | 0,65-1,00 | 1 | 0,70 | 0,30 | 0,29 | 100,0 % | 0,685 |
| A | inédit | **toutes** | 47 | 0,50 | 0,18 | 0,18 | **27,7 %** | **0,085** |
| B | apprentissage | 0,00-0,45 | 96 | 0,38 | 0,15 | 0,14 | 21,9 % | 0,063 |
| B | apprentissage | 0,45-0,55 | 61 | 0,49 | 0,26 | 0,25 | 39,3 % | 0,124 |
| B | apprentissage | 0,55-0,65 | 44 | 0,59 | 0,35 | 0,35 | 38,6 % | 0,018 |
| B | apprentissage | 0,65-1,00 | 37 | 0,74 | 0,48 | 0,47 | 81,1 % | 0,315 |
| B | apprentissage | **toutes** | 238 | 0,50 | 0,26 | 0,26 | **38,7 %** | **0,109** |
| B | validation | 0,00-0,45 | 83 | 0,37 | 0,14 | 0,13 | 19,3 % | 0,047 |
| B | validation | 0,45-0,55 | 74 | 0,50 | 0,26 | 0,25 | 33,8 % | 0,063 |
| B | validation | 0,55-0,65 | 55 | 0,60 | 0,35 | 0,34 | 40,0 % | 0,034 |
| B | validation | 0,65-1,00 | 25 | 0,81 | 0,55 | 0,55 | 60,0 % | 0,032 |
| B | validation | **toutes** | 237 | 0,51 | 0,27 | 0,26 | **32,9 %** | **0,047** |
| B | inédit | 0,00-0,45 | 69 | 0,39 | 0,16 | 0,15 | 18,8 % | 0,020 |
| B | inédit | 0,45-0,55 | 58 | 0,49 | 0,25 | 0,25 | 15,5 % | −0,111 |
| B | inédit | 0,55-0,65 | 25 | 0,59 | 0,34 | 0,33 | 48,0 % | 0,125 |
| B | inédit | 0,65-1,00 | 26 | 0,74 | 0,44 | 0,44 | 61,5 % | 0,156 |
| B | inédit | **toutes** | 178 | 0,50 | 0,26 | 0,25 | **28,1 %** | **0,012** |

### Quel facteur domine ?

| Cohorte | Période | Choix du côté | Écart payé | Frais | Délai 0,3 s | Plus grand poste négatif |
|---|---|---|---|---|---|---|
| A | apprentissage | +1 733 $ | −33 $ | −67 $ | −686 $ | **délai 0,3 s (prudent − signal)** |
| A | validation | +910 $ | −53 $ | −103 $ | −1 046 $ | **délai 0,3 s (prudent − signal)** |
| A | inédit | +390 $ | −38 $ | −79 $ | −684 $ | **délai 0,3 s (prudent − signal)** |
| B | apprentissage | +2 631 $ | −139 $ | −301 $ | −1 731 $ | **délai 0,3 s (prudent − signal)** |
| B | validation | +1 442 $ | −167 $ | −350 $ | −995 $ | **délai 0,3 s (prudent − signal)** |
| B | inédit | +108 $ | −126 $ | −285 $ | −1 279 $ | **délai 0,3 s (prudent − signal)** |

Le « choix du côté » mesure l'avantage réel du signal par rapport au prix du marché (milieu) : positif = le modèle bat Polymarket ; il est très bruité (issue binaire, peu de positions). Le délai 0,3 s mélange entrées perdues (le prix est parti — souvent les meilleures) et entrées faites au même prix.

Durée de calcul : 59 s.

---

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