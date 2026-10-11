# BOT95 — QUEUE RACE ENGINE · phases 0, 1 et 2 — **PRÉLIMINAIRE**

Étude hors ligne du 11.10.2026 (aucun bot, aucun workflow modifié, rien publié). Données : enregistreur du VPS de Dublin, branche `donnees-rapide` : **15 cycles BTC 5 min ≈ 1,25 h** d'enregistrement, un seul après-midi de dimanche (marché calme). **Tout ce qui suit est préliminaire : quelques heures, un seul régime de marché ; aucune conclusion de P&L.** Les cycles ne se recouvrent pas : chaque cycle est un marché distinct ; le flux commence ~40 s avant le début du cycle (abonnement anticipé).

## Verdict (en tête)

- **Qui fait disparaître la meilleure offre ?** Sur 4464 disparitions complètes du meilleur niveau (offre Up et offre Down, hors indéterminé), **77,4 % sont des retraits** (dont 22,6 % « déplacés » : même quantité reposée à un autre prix) et **22,6 % des consommations** par une transaction (0,8 % mixtes). 676 disparitions indéterminées (reconstruction douteuse) sont exclues. Toutes baisses confondues (y compris partielles) : 111 384 baisses, 12,3 % consommées.
- **Chronologie (H533/H544/H547)** : seules **327 des 4187 disparitions (7,8 %)** sont précédées dans la seconde d'un saut de bourse ≥ 5 $ dans le bon sens, contre 4,9 % avec des informations placées au hasard (marché très calme : 465 sauts ≥ 5 $ en 1,25 h). → l'information de bourse n'explique qu'environ **2,9 points** des disparitions ; l'immense majorité n'a aucune information de bourse détectable avant elle. Quand il y a une information, tout va plus vite qu'au hasard : réaction de l'autre côté en 23 ms (témoin 44), 1er retrait 65 ms (79), 1re consommation 71 ms (150), disparition 267 ms (485) — médianes. **FIRST REQUOTE vs FIRST SWEEP** : retrait d'abord 58,4 %, consommation d'abord 39,4 % (témoin 64,3 % / 33,5 %) : les vendeurs se retirent plus souvent qu'ils ne sont balayés, et l'information déplace un peu la balance vers le balayage.
- **Course** : ordre parti de Dublin à la réception de l'information (+0,1 ms de calcul, +14 ms aller simple). Il arriverait avant la disparition complète dans 84,7 % des 327 cas, mais **avant la 1re baisse du niveau visé dans seulement 72,8 %**, contre 86,0 % à des instants pris au hasard : après une vraie information, d'autres agissent avant nous plus souvent que d'habitude. « Arriver avant la disparition » est surtout mécanique (les niveaux vivent en général plus de 14 ms) et ne prouve aucun avantage. Rappel : l'information des bourses asiatiques nous parvient déjà avec ~100–130 ms de retard. Échantillon petit.
- **Course déclenchée par le carnet lui-même** : un niveau devenu meilleur prix vit en médiane 65 ms à ce rang avant de disparaître ; 67,6 % vivent plus que notre délai « message Polymarket → Dublin → ordre arrivé » ≈ 22,7 ms.
- **Signaux du bot (55 dans ces cycles)** : offre visée disparue dans les 2 s pour 33 signaux — **retirée 30**, consommée 2, mixte 1 ; encore là à 2 s 22 ; indéterminé 0. Les offres que visent nos signaux disparaissent surtout parce que le vendeur les retire, pas parce qu'un concurrent les achète avant nous. Effectifs trop petits pour un taux de gain par catégorie (donnés pour mémoire en 1b).
- **Ce qu'il faut de plus** : plusieurs jours (≥ 3–5) incluant des heures actives (ouverture US, annonces) pour avoir des centaines de disparitions précédées d'une information ; un enregistrement des prix au millième (pas de 0,001 près de 0/1) ; idéalement les messages bruts de bourse (et non un échantillon 50 ms) pour dater l'information à la ms.

## Phase 0 — audit des données

| Cycle (début) | Version | Format | Flux couvert (s par rapport au début) | Coupé (plafond) | Changements P (Up) | Carnets B (Up) | Transactions (2 jetons) | Photos 1 s comparées | Meilleur acheteur Up : prix · prix+taille | Meilleur vendeur Up : prix · prix+taille | 5 niveaux : prix acheteur · vendeur | Miroir Up/Down exact | Purges (croisement) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1791708300 | c70ef6bba0e6 | brut | 21 → 244 | oui | 74002 | 666 | 663 | 222 | 100,0 % · 99,5 % | 100,0 % · 99,5 % | 100,0 % · 100,0 % | 100,0 % | 21 |
| 1791708600 | c70ef6bba0e6 | brut | -40 → 202 | oui | 73966 | 690 | 687 | 202 | 100,0 % · 99,5 % | 100,0 % · 100,0 % | 100,0 % · 100,0 % | 100,0 % | 11 |
| 1791708900 | c70ef6bba0e6 | brut | -39 → 173 | oui | 73963 | 692 | 689 | 172 | 100,0 % · 99,4 % | 100,0 % · 100,0 % | 100,0 % · 100,0 % | 100,0 % | 25 |
| 1791709200 | 1c4d3c034a12 | compact | 265 → 301 | non | 236 | 4 | 10 | 35 | 100,0 % · 100,0 % | 100,0 % · 100,0 % | 100,0 % · 100,0 % | 100,0 % | 0 |
| 1791709500 | 1c4d3c034a12 | compact | -35 → 300 | non | 68980 | 33 | 3963 | 300 | 99,3 % · 97,3 % | 99,7 % · 98,3 % | 82,7 % · 87,7 % | 100,0 % | 88 |
| 1791709800 | 1c4d3c034a12 | compact | -39 → 300 | non | 42442 | 30 | 1096 | 299 | 80,6 % · 60,5 % | 81,9 % · 63,9 % | 45,2 % · 75,3 % | 100,0 % | 612 |
| 1791710100 | 1c4d3c034a12 | compact | -40 → 300 | non | 50727 | 32 | 1082 | 300 | 100,0 % · 98,3 % | 100,0 % · 99,0 % | 99,0 % · 98,7 % | 100,0 % | 56 |
| 1791710400 | 1c4d3c034a12 | compact | -40 → 300 | non | 45362 | 32 | 1120 | 300 | 99,7 % · 98,3 % | 100,0 % · 99,0 % | 97,3 % · 95,7 % | 100,0 % | 50 |
| 1791710700 | 1c4d3c034a12 | compact | -40 → 300 | non | 57996 | 33 | 1451 | 300 | 99,3 % · 98,0 % | 99,7 % · 98,0 % | 92,7 % · 96,3 % | 100,0 % | 75 |
| 1791711000 | 1c4d3c034a12 | compact | -39 → 300 | non | 43042 | 33 | 1723 | 300 | 100,0 % · 100,0 % | 100,0 % · 99,3 % | 99,3 % · 99,3 % | 100,0 % | 16 |
| 1791711300 | 1c4d3c034a12 | compact | -39 → 301 | non | 29203 | 31 | 809 | 300 | 97,3 % · 91,3 % | 100,0 % · 100,0 % | 81,7 % · 100,0 % | 100,0 % | 20 |
| 1791711600 | 1c4d3c034a12 | compact | -39 → 300 | non | 34603 | 31 | 776 | 300 | 100,0 % · 98,7 % | 100,0 % · 99,0 % | 98,7 % · 100,0 % | 100,0 % | 29 |
| 1791711900 | 1c4d3c034a12 | compact | -39 → 301 | non | 48513 | 32 | 1955 | 300 | 100,0 % · 98,7 % | 99,7 % · 99,3 % | 97,7 % · 98,7 % | 100,0 % | 80 |
| 1791712200 | 1c4d3c034a12 | compact | -39 → 301 | non | 49868 | 32 | 2101 | 300 | 100,0 % · 99,3 % | 100,0 % · 98,7 % | 99,7 % · 99,3 % | 100,0 % | 58 |
| 1791712500 | 08936a31b11a | compact | 88 → 300 | non | 19105 | 20 | 993 | 211 | 98,1 % · 96,7 % | 100,0 % · 100,0 % | 91,0 % · 100,0 % | 100,0 % | 6 |
| **total** | | | | | | | | 3841 | 98,0 % · 95,1 % | 98,5 % · 96,4 % | 91,2 % · 96,2 % | 100,0 % | |

- **Couverture** : 15 cycles de 1791708300 à 1791712500 (≈ 1,25 h d'horloge). **Temps de cycle réellement couvert par le flux : 64,1 min sur 75 min** (coupures des 3 cycles bruts, cycle 1791709200 quasi vide après redémarrage — 236 changements —, dernier cycle commencé à +88 s après une nouvelle version). Aucun cycle de la version b2b4d959b243 (flux agressifs `fx`) n'est encore disponible → les flux agressifs par bourse ne sont pas utilisés ici.
- **Format brut (3 premiers cycles)** : tout est enregistré mais le plafond de 150 000 lignes coupe le cycle après ~206 s (les photos après la coupure sont exclues : 281).
- **Reconstruction** : carnet Up = dernier carnet complet B + changements P. En format brut, elle colle aux photos 1 s à ~99,5 % (meilleur prix et taille). Contrôle supplémentaire : les P seuls (sans recharger les B) reproduisent les carnets complets suivants à 99,7 % → **les exécutions sont bien publiées en `price_change`** (pas seulement en carnet complet).
- **Perte due au filtre ±3 c et au carnet complet toutes les 10 s** (simulée sur les 3 cycles bruts en appliquant le filtre exact de rapide.js) : meilleur prix 100,0 % (acheteur) / 100,0 % (vendeur) ; prix + taille 98,0 % / 98,8 % ; **5 niveaux prix+taille : 13,4 % / 11,7 %** (contre 98,7 % sans filtre). Le meilleur niveau reste fiable ; la profondeur au-delà de 3 c est périmée entre deux carnets complets. Lors d'un balayage de plus de 3 c, des retraits sont perdus : le rejeu efface alors les niveaux opposés qui croisent le carnet (« purges »).
- **Pas de 0,001** : près de 0 et 1 Polymarket cote au millième ; l'enregistreur compact arrondit au cent (`Math.round(prix*100)`) → deux niveaux (0,99 et 0,991) fusionnent et la reconstruction se trompe. Photos concernées : 210 (acheteur) / 115 (vendeur), surtout le cycle 1791709800. Toute baisse à ≤ 0,04 ou ≥ 0,96, ou pendant une seconde où la photo montre un prix au millième, est classée **indéterminée**. **À corriger dans l'enregistreur (proposition, à décider par Pitch) : enregistrer le prix en millièmes.**
- **Miroir** : carnet Down = miroir exact du carnet Up dans 100,0 % des photos.
- **Sens du champ `side` des transactions** (« BUY » sur Up ou « SELL » sur Down = acheteur Up) : transactions dites acheteuses tombant sur l'offre Up : **91,2 %** (sur la demande : 2,2 %, ailleurs : 6,6 %) ; dites vendeuses tombant sur la demande Up : **85,0 %** (sur l'offre : 8,7 %). → **`side` = côté du PRENEUR (agresseur)**. Confirmé par l'appariement : avec ce sens, les transactions s'alignent sur les baisses du carnet ; avec le sens opposé, il n'y a presque aucune coïncidence.
- **Décalage carnet → transaction** : le message `last_trade_price` est horodaté par Polymarket **~21 ms APRÈS** la baisse de quantité correspondante dans le carnet (pic net entre +18 et +30 ms, même quantité au centième). Fenêtre d'appariement fixée à [+14 ; +40] ms (heure Polymarket). Bruit de fond mesuré dans une fenêtre témoin de même largeur décalée à −200 ms : 4,0 % des baisses (et 1,3 % des disparitions complètes) y trouveraient une « consommation » par hasard — ordre de grandeur du faux appariement, à comparer aux 12,3 % de baisses classées consommées. Conséquence pratique : **la disparition par exécution se voit dans le carnet avant le message de transaction** ; un robot qui attend le message de transaction a ~20 ms de retard.

## Phase 1 — pourquoi la meilleure offre disparaît

Définitions : *baisse* = diminution de quantité au meilleur prix (côté offre Up, et côté demande Up = offre Down par miroir). *Disparition complète* = la quantité au meilleur prix tombe à 0. *Consommé* = transaction(s) au même prix (Up achetée, ou Down vendue au prix miroir) dans [+14 ; +40] ms dont la somme couvre la baisse ; *mixte* = transaction couvrant une partie ; *retiré* = aucune transaction ; *déplacé* = retiré et la même quantité (±1 %) réapparaît à un autre prix du même côté dans [−5 ; +50] ms ; *indéterminé* = reconstruction non confirmée par la dernière photo, pas de 0,001, ou après coupure.

| Côté | Toutes baisses (n) | dont consommé | mixte | retiré | déplacé | indéterminé | Volume consommé / volume total des baisses (hors indét.) |
|---|---|---|---|---|---|---|---|
| offre Up (vendeur Up) | 60225 | 6728 | 742 | 32713 | 14245 | 5797 | 9,7 % |
| demande Up = offre Down | 63735 | 6993 | 763 | 34630 | 14570 | 6779 | 7,9 % |

**Livrable : nombre d'offres disparues (disparitions complètes du meilleur niveau) par cause**

| Côté | Disparitions | consommé | mixte | retiré | déplacé | indéterminé | Durée au meilleur rang avant disparition (ms) 10 % · méd. · 90 % — consommé | — retiré/déplacé | Âge du niveau (ms) méd. consommé · retiré |
|---|---|---|---|---|---|---|---|---|---|
| offre Up (vendeur Up) | 2514 | 475 | 15 | 1215 | 489 | 320 | 0 · 130 · 1 735 | 0 · 59 · 1 308 | 1 706 · 616 |
| demande Up = offre Down | 2626 | 497 | 20 | 1231 | 522 | 356 | 0 · 124 · 1 561 | 0 · 59 · 1 340 | 1 704 · 777 |
| **total** | 5140 | 972 | 35 | 2446 | 1011 | 676 | | | |

Par cycle (disparitions complètes hors indéterminé : consommé+mixte / retiré+déplacé) : 1791708300 : 53/194 ; 1791708600 : 49/123 ; 1791708900 : 62/165 ; 1791709200 : 0/0 ; 1791709500 : 252/896 ; 1791709800 : 39/108 ; 1791710100 : 72/275 ; 1791710400 : 69/306 ; 1791710700 : 112/482 ; 1791711000 : 50/138 ; 1791711300 : 34/73 ; 1791711600 : 48/127 ; 1791711900 : 88/291 ; 1791712200 : 66/229 ; 1791712500 : 13/50.

Taille du niveau disparu (parts) — médiane : consommé 18,0 · retiré 10,0.

### H499 — remplissage après disparition complète

| Côté | Cause | n | Nouvelle quantité au MÊME prix dans 100 · 500 · 1000 ms | Meilleur prix revenu à ce prix ou mieux dans 100 · 500 · 1000 ms |
|---|---|---|---|---|
| offre Up (vendeur Up) | consommé | 490 | 20,6 % · 33,3 % · 41,8 % | 23,1 % · 34,5 % · 42,7 % |
| offre Up (vendeur Up) | retiré/déplacé | 1704 | 22,5 % · 38,1 % · 46,8 % | 24,6 % · 39,5 % · 47,9 % |
| demande Up = offre Down | consommé | 517 | 20,9 % · 36,6 % · 44,9 % | 23,2 % · 37,1 % · 45,3 % |
| demande Up = offre Down | retiré/déplacé | 1753 | 23,3 % · 39,2 % · 47,5 % | 26,1 % · 41,1 % · 49,2 % |

### Phase 1b — offres visées par les signaux réels du bot de Dublin

Pour chaque signal enregistré (`sig`), on suit la quantité disponible au prix du signal ou mieux pendant 2 s ; *disparue* = moins d'une part (même définition que `disparu_ms` du bot). Cause = part du volume disparu expliquée par des transactions appariées (≥ 80 % consommée, ≤ 20 % retirée, sinon mixte). Gagnant : `rapide.json` (Gamma) ; `officiels.json` ne couvre pas encore ces cycles.

| Catégorie | Signaux | Offres distinctes | dont gagnants (réglés, par signal) | Disparition (ms) méd. | Contrôle : `disparu_ms` du bot méd. |
|---|---|---|---|---|---|
| consommée | 2 | 1 | 2/2 | 208 | 209 |
| mixte | 1 | 1 | 0/1 | 169 | 169 |
| retirée | 30 | 23 | 11/28 | 478 | 428 |
| encore là à 2 s | 22 | 21 | 2/19 | — | — |

Contrôle de la reconstruction contre la mesure en direct du bot (`rapide.json`, 50 signaux réglés) : même verdict disparue / pas disparue dans 2 s pour 50/50, et même instant à 5 ms près pour 48/50. Signaux dans la partie coupée d'un cycle brut (exclus) : 1. **Effectifs minuscules : aucun taux de gain par catégorie n'est interprétable.**

<details><summary>Détail des signaux</summary>

| Cycle | Règle | Côté | Prix | Quantité au prix (reconstruite) | Disparue (ms) | 1re baisse (ms) | Part consommée | Catégorie | `disparu_ms` bot | Gagné |
|---|---|---|---|---|---|---|---|---|---|---|
| 1791708600 | V2-F ecart qui grandit | Up | 0.24 | 85,0 | 181 | 8 | 7,9 % | retirée | 181 | non |
| 1791708600 | cohorte B : V2-F corrige 0,015 % | Up | 0.21 | 10,0 | 506 | 506 | 3,9 % | retirée | 506 | non |
| 1791708600 | V2-F incertitude 0,01 % | Up | 0.2 | 12,0 | — | — | 0,5 % | encore là à 2 s | — | non |
| 1791708600 | desaccord 20 60-180 s | Up | 0.2 | 463,0 | — | 197 | 8,1 % | encore là à 2 s | — | non |
| 1791708600 | desaccord 30 | Up | 0.16 | 20,0 | 1 115 | 848 | 0,0 % | retirée | 1 115 | non |
| 1791708900 | V2-F ecart qui grandit | Down | 0.29 | 100,0 | 52 | 52 | 0,0 % | retirée | 52 | oui |
| 1791708900 | desaccord 20 60-180 s | Down | 0.29 | 100,0 | 51 | 51 | 0,0 % | retirée | 52 | oui |
| 1791708900 | V2-F incertitude 0,01 % | Down | 0.27 | 5,0 | 1 484 | 1 445 | 7,1 % | retirée | 1 484 | oui |
| 1791708900 | cohorte B : V2-F corrige 0,015 % | Down | 0.27 | 5,0 | 1 484 | 1 445 | 7,1 % | retirée | 1 484 | oui |
| 1791709800 | V2-F ecart qui grandit | Down | 0.25 | 7,0 | — | — | 2,1 % | encore là à 2 s | — | non |
| 1791709800 | V2-F incertitude 0,01 % | Down | 0.23 | 14,6 | — | — | 3,2 % | encore là à 2 s | — | non |
| 1791709800 | cohorte B : V2-F corrige 0,015 % | Down | 0.23 | 14,6 | — | — | 3,2 % | encore là à 2 s | — | non |
| 1791709800 | desaccord 30 | Down | 0.14 | 37,5 | — | 48 | 32,4 % | encore là à 2 s | — | non |
| 1791709800 | desaccord 20 60-180 s | Down | 0.02 | 1 397,5 | — | 30 | 0,0 % | encore là à 2 s | — | non |
| 1791710100 | V2-F ecart qui grandit | Up | 0.27 | 122,0 | 1 231 | 862 | 2,0 % | retirée | 1 232 | non |
| 1791710100 | desaccord 20 60-180 s | Up | 0.27 | 122,0 | 1 231 | 862 | 2,0 % | retirée | 1 231 | non |
| 1791710100 | V2-F incertitude 0,01 % | Up | 0.22 | 136,0 | 305 | 40 | 9,6 % | retirée | 305 | non |
| 1791710100 | cohorte B : V2-F corrige 0,015 % | Up | 0.22 | 136,0 | 305 | 40 | 9,6 % | retirée | 305 | non |
| 1791710100 | desaccord 30 | Up | 0.17 | 60,0 | — | — | 1,9 % | encore là à 2 s | — | non |
| 1791710400 | V2-F ecart qui grandit | Up | 0.23 | 16,0 | 548 | 487 | 8,0 % | retirée | 548 | oui |
| 1791710400 | V2-F incertitude 0,01 % | Up | 0.2 | 115,0 | 208 | 144 | 100,0 % | consommée | 209 | oui |
| 1791710400 | cohorte B : V2-F corrige 0,015 % | Up | 0.2 | 115,0 | 208 | 144 | 100,0 % | consommée | 209 | oui |
| 1791710400 | desaccord 20 60-180 s | Down | 0.27 | 12,0 | 591 | 537 | 8,4 % | retirée | 591 | non |
| 1791710400 | desaccord 30 | Down | 0.16 | 12,0 | 259 | 91 | 0,0 % | retirée | 259 | non |
| 1791710700 | V2-F incertitude 0,01 % | Up | 0.52 | 40,0 | 1 066 | 1 030 | 0,0 % | retirée | 1 066 | non |
| 1791710700 | cohorte B : V2-F corrige 0,015 % | Up | 0.52 | 40,0 | 1 064 | 1 028 | 0,0 % | retirée | 1 064 | non |
| 1791710700 | V2-F ecart qui grandit | Down | 0.18 | 12,0 | 1 501 | 1 501 | 9,3 % | retirée | 1 500 | oui |
| 1791710700 | desaccord 20 60-180 s | Down | 0.09 | 505,2 | — | 120 | 0,0 % | encore là à 2 s | — | oui |
| 1791710700 | desaccord 30 | Down | 0.07 | 5,0 | — | — | 0,0 % | encore là à 2 s | — | oui |
| 1791710700 | cohorte A : zone + modele monte | Down | 0.15 | 796,2 | 84 | 7 | 0,0 % | retirée | 8 | oui |
| 1791711000 | V2-F ecart qui grandit | Up | 0.27 | 15,8 | 406 | 406 | 12,1 % | retirée | 406 | non |
| 1791711000 | desaccord 20 60-180 s | Up | 0.27 | 27,0 | — | — | 0,8 % | encore là à 2 s | — | non |
| 1791711000 | cohorte B : V2-F corrige 0,015 % | Up | 0.2 | 94,0 | — | 395 | 7,9 % | encore là à 2 s | — | non |
| 1791711000 | V2-F incertitude 0,01 % | Up | 0.19 | 39,0 | 560 | 370 | 12,9 % | retirée | 560 | non |
| 1791711000 | desaccord 30 | Up | 0.17 | 8,0 | — | — | 13,0 % | encore là à 2 s | — | non |
| 1791711300 | V2-F incertitude 0,01 % | Up | 0.42 | 249,3 | 251 | 27 | 0,0 % | retirée | 251 | oui |
| 1791711300 | cohorte B : V2-F corrige 0,015 % | Up | 0.42 | 249,3 | 249 | 25 | 0,0 % | retirée | 249 | oui |
| 1791711300 | V2-F ecart qui grandit | Down | 0.16 | 21,2 | — | — | 2,3 % | encore là à 2 s | — | non |
| 1791711300 | desaccord 20 60-180 s | Down | 0.1 | 145,0 | — | 528 | 2,0 % | encore là à 2 s | — | non |
| 1791711300 | desaccord 30 | Down | 0.08 | 5,0 | 387 | 387 | 0,0 % | retirée | 387 | non |
| 1791711600 | V2-F incertitude 0,01 % | Down | 0.57 | 10,0 | 8 | 8 | 0,0 % | retirée | 8 | oui |
| 1791711600 | V2-F ecart qui grandit | Up | 0.2 | 15,0 | — | — | 14,3 % | encore là à 2 s | — | non |
| 1791711600 | desaccord 30 | Up | 0.11 | 362,1 | 169 | 15 | 31,6 % | mixte | 169 | non |
| 1791711600 | desaccord 20 60-180 s | Up | 0.12 | 389,8 | — | 23 | 2,0 % | encore là à 2 s | — | non |
| 1791711900 | V2-F ecart qui grandit | Down | 0.21 | 200,0 | 451 | 3 | 10,6 % | retirée | 451 | oui |
| 1791711900 | desaccord 20 60-180 s | Up | 0.16 | 872,2 | 837 | 4 | 5,8 % | retirée | 837 | non |
| 1791711900 | desaccord 30 | Up | 0.13 | 1 463,0 | — | 131 | 1,3 % | encore là à 2 s | — | non |
| 1791711900 | cohorte B : V2-F corrige 0,015 % | Up | 0.1 | 10,0 | — | — | 26,3 % | encore là à 2 s | — | non |
| 1791711900 | V2-F incertitude 0,01 % | Up | 0.11 | 333,0 | 119 | 1 | 0,0 % | retirée | 0 | non |
| 1791711900 | cohorte A : zone + modele monte | Up | 0.15 | 120,0 | 19 | 18 | 0,0 % | retirée | 19 | non |
| 1791712200 | V2-F ecart qui grandit | Up | 0.2 | 63,0 | — | 38 | 6,4 % | encore là à 2 s | — | — |
| 1791712200 | V2-F incertitude 0,01 % | Up | 0.13 | 12,0 | 1 660 | 1 593 | 5,1 % | retirée | — | — |
| 1791712200 | cohorte B : V2-F corrige 0,015 % | Up | 0.13 | 12,0 | 1 660 | 1 593 | 5,1 % | retirée | — | — |
| 1791712200 | desaccord 20 60-180 s | Up | 0.31 | 513,1 | — | 127 | 1,5 % | encore là à 2 s | — | — |
| 1791712200 | desaccord 30 | Down | 0.15 | 24,0 | — | — | 8,8 % | encore là à 2 s | — | — |

</details>

## Phase 2 — chronologie : information → réaction → retrait → transaction (H533, H544, H547)

*Nouvelle information* (fixée à l'avance) : saut ≥ 5 $ du prix d'une bourse (Bybit perp, OKX perp, Binance, Coinbase) entre deux échantillons 50 ms consécutifs, dans le sens qui rend l'offre qui disparaît trop bon marché (hausse pour l'offre Up, baisse pour l'offre Down) ; heure = **réception à Dublin** du dernier prix de la source. On prend l'information la plus récente dans les 1000 ms avant la disparition. Délais mesurés en heure de réception à Dublin. *Réaction* = l'autre côté du carnet s'améliore (prix ou taille au meilleur) ; *retrait* = 1re baisse « retiré/déplacé » au meilleur niveau ; *consommation* = 1re baisse « consommé/mixte ».

Informations détectées sur 1,25 h : perp 55, okx 41, bn 37, cb 332, cl 3776 (Chainlink : chaque nouvelle valeur).

**Bourses, saut ≥ 5 $ (critère principal)** — disparitions complètes (hors indét., dans le cycle) : 4187 ; précédées d'une information : **327** (7,8 %) — **témoin** (même nombre d'informations placées au hasard, 20 tirages) : 4,9 %.

| Mesure (ms après l'information) | n | 10 % · médiane · 90 % | témoin au hasard : médiane |
|---|---|---|---|
| 1re réaction de l'autre côté (renforcement) | 319 | 2 · 23 · 198 | 44 |
| 1er retrait au meilleur niveau | 309 | 10 · 65 · 306 | 79 |
| 1re consommation au meilleur niveau | 271 | 8 · 71 · 337 | 150 |
| disparition complète | 327 | 63 · 267 · 778 | 485 |

Qui vient en premier après l'information : retrait d'abord (FIRST REQUOTE) 191 (58,4 %, témoin 64,3 %) ; consommation d'abord (FIRST SWEEP) 129 (39,4 %, témoin 33,5 %) ; même milliseconde 7 (2,1 %, témoin 2,3 %).

Course (ordre envoyé à la réception de l'information, arrivée comparée à l'heure Polymarket de la disparition) : avant la disparition complète **277/327** (84,7 %) avec 14 ms aller simple, 272/327 avec l'aller-retour complet 28 ms ; **avant la 1re baisse de ce niveau après l'information : 238/327** (72,8 %). Témoin au hasard : 95,8 % et 86,0 %. Par cause de disparition (avant la disparition complète, aller simple) : consommé/mixte 89/102 ; retiré/déplacé 188/225.

**Sensibilité (déclarée à l'avance) : bourses, saut ≥ 2 $** — disparitions complètes (hors indét., dans le cycle) : 4187 ; précédées d'une information : **603** (14,4 %).

| Mesure (ms après l'information) | n | 10 % · médiane · 90 % | témoin au hasard : médiane |
|---|---|---|---|
| 1re réaction de l'autre côté (renforcement) | 582 | 2 · 20 · 188 | — |
| 1er retrait au meilleur niveau | 559 | 8 · 55 · 260 | — |
| 1re consommation au meilleur niveau | 486 | 4 · 72 · 298 | — |
| disparition complète | 603 | 43 · 210 · 757 | — |

Qui vient en premier après l'information : retrait d'abord (FIRST REQUOTE) 324 (53,7 %) ; consommation d'abord (FIRST SWEEP) 262 (43,4 %) ; même milliseconde 16 (2,7 %) ; aucun des deux avant la disparition 1 (0,2 %).

Course (ordre envoyé à la réception de l'information, arrivée comparée à l'heure Polymarket de la disparition) : avant la disparition complète **496/603** (82,3 %) avec 14 ms aller simple, 470/603 avec l'aller-retour complet 28 ms ; **avant la 1re baisse de ce niveau après l'information : 423/603** (70,1 %). Par cause de disparition (avant la disparition complète, aller simple) : consommé/mixte 149/181 ; retiré/déplacé 347/422.

**Chainlink (nouvelle valeur dans le bon sens)** — disparitions complètes (hors indét., dans le cycle) : 4187 ; précédées d'une information : **1680** (40,1 %) — **témoin** (même nombre d'informations placées au hasard, 20 tirages) : 36,4 %.

| Mesure (ms après l'information) | n | 10 % · médiane · 90 % | témoin au hasard : médiane |
|---|---|---|---|
| 1re réaction de l'autre côté (renforcement) | 1568 | 3 · 54 · 339 | 43 |
| 1er retrait au meilleur niveau | 1629 | 6 · 71 · 376 | 67 |
| 1re consommation au meilleur niveau | 1368 | 19 · 128 · 491 | 128 |
| disparition complète | 1680 | 94 · 480 · 893 | 446 |

Qui vient en premier après l'information : retrait d'abord (FIRST REQUOTE) 1051 (62,6 %, témoin 62,8 %) ; consommation d'abord (FIRST SWEEP) 597 (35,5 %, témoin 34,3 %) ; même milliseconde 31 (1,8 %, témoin 2,8 %) ; aucun des deux avant la disparition 1 (0,1 %, témoin 0,0 %).

Course (ordre envoyé à la réception de l'information, arrivée comparée à l'heure Polymarket de la disparition) : avant la disparition complète **1593/1680** (94,8 %) avec 14 ms aller simple, 1561/1680 avec l'aller-retour complet 28 ms ; **avant la 1re baisse de ce niveau après l'information : 1408/1680** (83,8 %). Témoin au hasard : 95,2 % et 84,7 %. Par cause de disparition (avant la disparition complète, aller simple) : consommé/mixte 376/397 ; retiré/déplacé 1217/1283.

Lecture : si les délais et l'ordre « retrait / consommation » sont les mêmes avec des informations placées au hasard, l'information de bourse n'explique pas la disparition : la course « avant la disparition » est alors surtout mécanique (les niveaux vivent de toute façon plus de 14 ms) et ne prouve aucun avantage.

**Course déclenchée par le carnet Polymarket lui-même** (sans information externe) : délai « Polymarket → Dublin (8,6 ms) + calcul (0,1 ms) + aller simple (14 ms) » ≈ 22,7 ms. Durée passée au meilleur rang par les niveaux qui disparaissent : 0 · 65 · 1 446 ms (10 % · méd. · 90 %) ; plus longue que notre délai pour **67,6 %** (3017/4464). Consommés seulement : 64,0 %. Attention : « vivre plus longtemps que notre délai » ne veut pas dire que l'avantage existait — c'est une borne de faisabilité mécanique, pas un gain.

### Précurseurs H497 / H541 / H543 (avant une consommation complète, contre 3 instants témoins au hasard par événement)

AUC = probabilité qu'une valeur avant consommation dépasse une valeur témoin (0,5 = aucun signal). Instants témoins : même cycle, même côté, à plus de 1 s de toute consommation. Modèle combiné : régression logistique, validation croisée par cycle (les cycles de test ne servent pas à l'apprentissage).

| Fenêtre (variations sur h ms) | Consommations · témoins | déséquilibre du microprix vers l'offre consommée (en fin de fenêtre) | variation de l'écart (compression < 0) | variation log taille du meilleur acheteur d'en face (renforcement > 0) | variation du prix d'en face (millièmes, vers l'offre > 0) | variation log taille de l'offre consommée | écart en fin de fenêtre (millièmes) | Modèle combiné (AUC validation croisée) |
|---|---|---|---|---|---|---|---|---|
| 100 ms, jusqu'à t−1 ms | 926 · 2778 | 0,840 (méd. 0,91 / -0,14) | 0,522 (méd. 0,00 / 0,00) | 0,533 (méd. 0,00 / 0,00) | 0,586 (méd. 0,00 / 0,00) | 0,341 (méd. -0,06 / 0,00) | 0,572 (méd. 10,00 / 10,00) | 0,883 |
| 200 ms, jusqu'à t−1 ms | 926 · 2778 | 0,832 (méd. 0,91 / -0,03) | 0,523 (méd. 0,00 / 0,00) | 0,585 (méd. 0,03 / 0,00) | 0,592 (méd. 0,00 / 0,00) | 0,281 (méd. -0,55 / 0,00) | 0,571 (méd. 10,00 / 10,00) | 0,880 |
| 500 ms, jusqu'à t−1 ms | 922 · 2766 | 0,841 (méd. 0,91 / -0,11) | 0,542 (méd. 0,00 / 0,00) | 0,610 (méd. 0,16 / 0,00) | 0,596 (méd. 0,00 / 0,00) | 0,216 (méd. -1,29 / 0,00) | 0,572 (méd. 10,00 / 10,00) | 0,888 |
| 100 ms, arrêté à t−100 ms | 926 · 2778 | 0,798 (méd. 0,86 / -0,17) | 0,501 (méd. 0,00 / 0,00) | 0,618 (méd. 0,01 / 0,00) | 0,534 (méd. 0,00 / 0,00) | 0,365 (méd. -0,00 / 0,00) | 0,551 (méd. 10,00 / 10,00) | 0,833 |
| 200 ms, arrêté à t−200 ms | 924 · 2772 | 0,731 (méd. 0,78 / -0,07) | 0,519 (méd. 0,00 / 0,00) | 0,601 (méd. 0,03 / 0,00) | 0,530 (méd. 0,00 / 0,00) | 0,348 (méd. -0,24 / 0,00) | 0,551 (méd. 10,00 / 10,00) | 0,773 |
| 500 ms, arrêté à t−500 ms | 918 · 2754 | 0,636 (méd. 0,57 / -0,08) | 0,516 (méd. 0,00 / 0,00) | 0,581 (méd. 0,06 / 0,00) | 0,516 (méd. 0,00 / 0,00) | 0,405 (méd. -0,14 / 0,00) | 0,531 (méd. 10,00 / 10,00) | 0,655 |

Lecture : (méd. avant consommation / méd. témoin). Lignes « jusqu'à t−1 ms » : tout ce qui est visible juste avant — en grande partie **mécanique** (la file de l'offre consommée fond déjà : consommations partielles du même niveau juste avant). Lignes « arrêté à t−h » : seulement ce qui était connu h ms avant, donc utilisable pour arriver à temps. Témoins non appariés sur le prix, l'écart ni la taille : un petit niveau est plus facilement consommé en entier, donc le déséquilibre du microprix reflète en partie la petite taille de l'offre (effet de sélection). **Préliminaire, effectifs groupés par cycle (15 cycles), aucune conclusion de P&L.**

## Ce qu'il faut de plus (et limites)

- **Durée** : 1,25 h, un seul dimanche après-midi, BTC très calme (≈ 465 sauts ≥ 5 $ en tout). Il faut **au moins 3 à 5 jours** dont des séances actives pour la phase 2 (des centaines de disparitions précédées d'une information) et pour la phase 1b (≥ 100 signaux par catégorie avant tout taux de gain).
- **Échantillon 50 ms des bourses** : seul le dernier prix de chaque tranche est gardé ; le moment exact où le seuil est franchi peut être plus tôt (jusqu'à ~50 ms). Les bourses asiatiques arrivent à Dublin avec ~100–130 ms de retard (Bybit, OKX, Binance), Coinbase ~45 ms : un concurrent mieux placé voit l'information avant nous.
- **Prix arrondis au cent** dans l'enregistreur compact (pas de 0,001 perdu près de 0/1) et profondeur au-delà de ±3 c périmée entre deux carnets complets (10 s).
- **Flux agressifs `fx`** (version b2b4d959b243) : pas encore de cycle disponible ; à intégrer à la phase 2 (balayage des bourses vs. retrait Polymarket).
- **Horloges** : la course compare l'heure Dublin (NTP) à l'heure Polymarket ; le décalage médian Polymarket → Dublin mesuré (8,6 ms) inclut un éventuel écart d'horloge.
- Durée d'exécution : 9 s.
