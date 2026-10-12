# Bot95 — Rapport pour ChatGPT : makers, fantômes, combinaisons (11.10.2026, 16:20)

> **En bref (tout est PRÉLIMINAIRE, rien n'est validé statistiquement ; aucun ordre réel ; période réservée ≥ 13.10.2026 00:00 UTC jamais lue)**
> 1. **Pourquoi nos makers sont mal remplis.** Les makers réels sont au meilleur prix dans 97 % de leurs remplissages, presque toujours servis par de petits preneurs (< 10 $), avec une sélection adverse d'environ +0,4 c à 1–10 s. Notre M2 (modèle − 5 c) n'est au meilleur prix que dans 63 % des cas et subit −3 à −7 c : il est surtout rempli quand un gros preneur traverse plusieurs niveaux.
> 2. **Gagnants et perdants ont des remplissages identiques** (97 % contre 96 % au meilleur prix). La différence est ailleurs : hors échantillon, les makers perdants ont un stock qui penche vers le côté perdant dès la 1re minute (−15 % au-delà du prix du marché à 60 s, IC 90 % [−22 ; −7]) ; les gagnants ne battent que faiblement le marché (+1 à +2,5 %, IC contenant 0).
> 3. **Les paires ne font pas le profit.** Les makers les plus rentables (+5 à +6 % par $) perdent sur leurs paires et gagnent sur leurs jambes seules ; un portefeuille qui achète ses paires à 0,867 perd quand même −6 253 $ à cause de ses jambes seules. Un portefeuille sépare 1 $ en Up + Down et revend les deux côtés : +5 % (déduction).
> 4. **Preneurs** : les gains se concentrent dans la 1re minute du cycle (+14 % par $ pour 0xc4e21390…) ; le même portefeuille 0x41e2e1cc… gagne +6 %/$ en preneur et perd −8 %/$ en maker dans cette minute.
> 5. **« Tout combiné »** : sur 892 combinaisons de filtres (17 653 trades fantômes), le hasard produit plus de « gagnants » en validation (157/300) que les vraies meilleures combinaisons (100/300). Seule la zone 0,15–0,35 avec écart ≥ 30 c tient sur les deux périodes (+0,9 $/$ puis +1,0 $/$, cohorte A) — mais ces offres disparaissent avant un preneur.
> 6. **Nouveaux fantômes à Dublin** (accords de Pitch) : M4a/b/c, M6 (100/250/500/1000 ms), M8 ; puis M8b (routeur corrigé), M9 (fin de cycle ≤ 0,98), M10 (double maker au meilleur prix + retrait toxique), M11 (zone 0,15–0,35 en maker). Les 15 premiers sont GELÉS jusqu'au verdict du 15.10.
> 7. **Défauts trouvés et documentés** : borne « prudente » de file plafonnée seule (19 offres sur 4 147 avec prudent > central) ; M8 ne calcule pas un gain conditionnel au remplissage (corrigé dans le NOUVEAU fantôme M8b, M8 inchangé) ; 88 marchés sur 300 tronqués à 4 000 exécutions (recollecte jusqu'à 10 000 en cours) ; risque à 0,95–0,99 non mesurable tant que ces marchés manquent.

## Ce qui a été déployé ou lancé depuis 14:45

| Élément | Statut | Rôle |
|---|---|---|
| M4a / M4b / M4c | Dublin, gelé | M4 avec une seule condition (bourses −10 $ / flux agressif / 100 parts vendues) |
| M6 100 / 250 / 500 / 1000 ms | Dublin, gelé | durée de vie des cotations, nouvelle pose après confirmation d'annulation |
| M8 | Dublin, gelé | routeur maker / preneur sur signal (calcul non conforme, documenté) |
| Bornes de file prudente / centrale / optimiste | Dublin | trois estimations de remplissage, aucune certaine |
| M8b, M9, M10, M11 | Dublin (accords 15:47 et 15:53) | routeur corrigé ; fin de cycle ≤ 0,98 ; double maker meilleur prix ; zone maker |
| Suivi des makers | GitHub, quotidien | exécutions maker / preneur de 600 marchés BTC 5 min, activité de 48 portefeuilles |
| Audit maker (12 sections) | script prêt | rapport du 12.10 à 20 h |

## Prochaines étapes
- 11.10 vers 17 h 50 : analyses H681–H719 sur les 600 marchés complets (audit des données, penchant H712/H714, gagnants contre perdants H718, meilleur prix contre ticks plus bas H717, M22 preneur 1re minute, M23 Split & Sell, risque 0,95–0,99 sur 30/15/5 s). Aucun nouveau fantôme sans accord de Pitch.
- 12.10 à 20 h : audit M4/M6/M8 (10 livrables).
- 15.10 à 19 h : verdict sur la période réservée.



## Annexe — Bot95 — Pourquoi les makers rentables évitent les mauvais remplissages (H695, Test B) — PRÉLIMINAIRE

Généré le 11.10.2026 14:06 UTC. 51 cycles communs (marchés lus × cycles enregistrés à Dublin). Transactions preneuses rapprochées de Dublin : 11731 / 62531 (19 %). Remplissages makers datés à la ms : 62122. Makers classés sur toute la base (≥ 20 marchés, ≥ 5 000 $) : 40 rentables (≥ +1 % par $), 48 perdants (≤ −0,5 %).

Sélection adverse = prix du côté du maker h secondes après, moins son prix (cents par part ; négatif = le marché est parti contre lui). Pondérée par les parts.

### 1. Sélection adverse : makers réels contre nos fantômes

| Groupe | Remplissages | +0,1 s | +0,3 s | +1 s | +3 s | +5 s | +10 s | règlement |
|---|---|---|---|---|---|---|---|---|
| makers rentables | 10849 | +0.4 | +0.3 | +0.4 | +0.4 | +0.5 | +0.8 | -0.6 |
| makers perdants | 10289 | +0.4 | +0.2 | -0.0 | -0.1 | -0.1 | +0.8 | +0.7 |
| makers autres | 40984 | +0.5 | +0.5 | +0.5 | +0.3 | +0.1 | -0.4 | -1.4 |
| nous M0 | 21 | — | — | -0.3 | -1.3 | -1.8 | +2.9 | +13.8 |
| nous M1 | 80 | — | — | -0.4 | +0.0 | -0.4 | -0.9 | +16.7 |
| nous M2 | 259 | — | — | -3.0 | -5.5 | -6.0 | -6.8 | -0.0 |
| nous M3 | 50 | — | — | +3.7 | +3.7 | -1.0 | +8.8 | +27.4 |
| nous M4 | 103 | — | — | -1.1 | -1.7 | -2.2 | -2.5 | +3.4 |
| nous M5 | 82 | — | — | -2.5 | -4.1 | -3.9 | -4.8 | +8.9 |

(nos fantômes : pas de mesure à 0,1 et 0,3 s ; la sélection adverse « règlement » est le résultat par part)

### 2. Explications candidates (tous les makers réels, puis rentables seulement)

**Au meilleur prix ou plus loin**

| Groupe | Remplissages | +0,1 s | +0,3 s | +1 s | +3 s | +5 s | +10 s | règlement |
|---|---|---|---|---|---|---|---|---|
| au meilleur prix — tous | 59916 | +0.5 | +0.4 | +0.4 | +0.2 | +0.2 | +0.1 | -1.2 |
| au meilleur prix — rentables | 10488 | +0.4 | +0.4 | +0.4 | +0.4 | +0.4 | +0.8 | -0.8 |
| plus loin (servi par un balayage) — tous | 2206 | +0.3 | -0.2 | +0.0 | +0.5 | -0.7 | -1.8 | +2.4 |
| plus loin (servi par un balayage) — rentables | 361 | +0.1 | -0.3 | +0.4 | +1.1 | +1.9 | +0.5 | +3.9 |

**Balayage de plusieurs niveaux par le preneur**

| Groupe | Remplissages | +0,1 s | +0,3 s | +1 s | +3 s | +5 s | +10 s | règlement |
|---|---|---|---|---|---|---|---|---|
| preneur sur un seul prix — tous | 34727 | +0.4 | +0.3 | +0.4 | +0.1 | +0.1 | -0.1 | -1.0 |
| preneur sur un seul prix — rentables | 5248 | +0.4 | +0.2 | +0.3 | +0.3 | +0.6 | +1.0 | -0.6 |
| balayage — tous | 27395 | +0.5 | +0.5 | +0.4 | +0.5 | +0.2 | +0.2 | -1.2 |
| balayage — rentables | 5601 | +0.5 | +0.5 | +0.6 | +0.5 | +0.4 | +0.6 | -0.6 |

**Conditions toxiques de M4 actives au remplissage**

| Groupe | Remplissages | +0,1 s | +0,3 s | +1 s | +3 s | +5 s | +10 s | règlement |
|---|---|---|---|---|---|---|---|---|
| aucune — tous | 36943 | +0.5 | +0.4 | +0.3 | +0.1 | +0.2 | +0.1 | -1.0 |
| aucune — rentables | 7252 | +0.5 | +0.4 | +0.4 | +0.2 | +0.3 | +0.4 | -2.2 |
| a — tous | 40 | -1.5 | -2.5 | -5.5 | -9.5 | -8.5 | -2.5 | +47.7 |
| a — rentables | 9 | +0.5 | +0.5 | +0.5 | +5.5 | +6.5 | +5.5 | +52.0 |
| b — tous | 256 | +0.8 | +0.7 | +0.1 | -0.5 | -0.7 | -0.8 | -3.2 |
| b — rentables | 4 | +0.5 | +0.5 | +0.5 | -0.5 | -1.5 | -1.5 | -5.0 |
| c — tous | 23573 | +0.5 | +0.4 | +0.6 | +0.5 | +0.2 | +0.1 | -0.4 |
| c — rentables | 3494 | +0.4 | +0.3 | +0.4 | +0.6 | +0.7 | +1.3 | +1.1 |
| ac — tous | 76 | +0.6 | -1.3 | -1.3 | -1.6 | -0.9 | -2.4 | -7.5 |
| ac — rentables | 3 | +10.0 | +11.5 | +16.5 | +17.5 | +19.9 | +23.5 | +28.0 |
| bc — tous | 1110 | +0.0 | -0.1 | -0.2 | -0.8 | -0.7 | -2.0 | -10.9 |
| bc — rentables | 56 | +0.4 | +0.7 | +1.0 | +0.4 | +1.5 | +1.0 | +1.3 |
| ab — tous | 16 | -3.5 | -17.5 | -13.5 | -19.5 | -20.5 | -19.5 | -24.3 |
| ab — rentables | 0 | — | — | — | — | — | — | — |
| abc — tous | 108 | +0.2 | -0.1 | +0.1 | +1.0 | +1.0 | -1.4 | -9.3 |
| abc — rentables | 31 | +0.0 | +0.1 | +0.2 | +0.9 | +1.3 | -1.3 | -9.1 |

**Taille de la transaction du preneur**

| Groupe | Remplissages | +0,1 s | +0,3 s | +1 s | +3 s | +5 s | +10 s | règlement |
|---|---|---|---|---|---|---|---|---|
| preneur 0–10 $ — tous | 59919 | +0.5 | +0.4 | +0.5 | +0.3 | +0.2 | +0.1 | -1.3 |
| preneur 0–10 $ — rentables | 10592 | +0.5 | +0.4 | +0.5 | +0.5 | +0.5 | +0.7 | -1.2 |
| preneur 10–50 $ — tous | 1809 | +0.1 | -0.1 | -0.2 | -1.0 | -0.2 | -0.8 | +1.3 |
| preneur 10–50 $ — rentables | 221 | -0.1 | -0.6 | -1.0 | -1.3 | -0.3 | +1.2 | +7.0 |
| preneur 50–200 $ — tous | 351 | +0.3 | -0.0 | -0.1 | -0.7 | -0.6 | -2.0 | +1.2 |
| preneur 50–200 $ — rentables | 32 | +1.2 | +1.1 | +2.3 | +3.8 | +10.4 | +10.8 | +9.1 |
| preneur 200–∞ $ — tous | 43 | +0.1 | -0.2 | -1.5 | -1.5 | +1.5 | +1.5 | +8.3 |
| preneur 200–∞ $ — rentables | 4 | -1.5 | -1.5 | -1.5 | -1.5 | +1.5 | +1.5 | +42.0 |

**Part de chaque situation : makers rentables contre perdants contre nos fantômes**

- makers rentables : au meilleur prix 97 % ; balayages 52 % ; condition toxique active 33 % ; prix médian 0.33 ; moment médian 165 s
- makers perdants : au meilleur prix 96 % ; balayages 55 % ; condition toxique active 32 % ; prix médian 0.33 ; moment médian 147 s
- nos fantômes : au meilleur prix 63 % ; prix médian 0.28

### Limites
- Une journée de cycles communs ; rapprochement par seconde, prix, côté et taille (les transactions non rapprochées sont exclues).
- Les ordres posés puis annulés par ces makers sont invisibles : on ne voit que leurs remplissages.
- Rentable / perdant est mesuré sur toute la base, y compris ces cycles.


## Annexe — Bot95 — Penchant de l'inventaire des makers (H712, H714, H718) — PRÉLIMINAIRE

Généré le 11.10.2026 14:15 UTC. FAITS : exécutions de l'API Data. INFÉRENCES : interprétation. Aucune valeur future n'entre dans le penchant ni dans le prix de référence.

### 1. Audit des données collectées

- Marchés collectés (avant la période réservée) : **300**, du 10.10 12:25 au 11.10 13:20 UTC.
- Marchés complets (< 10 000 exécutions) : **212** ; encore tronqués (≥ 10 000, plafond de l'API) : **88** — isolés, exclus des résultats.
- Dont marchés entre 4 000 et 10 000 exécutions (récupérés grâce au nouveau plafond) : 0.
- Exécutions : 987482 ; doublons exacts : 63712 ; valeurs incohérentes (prix, taille, issue, côté) : 0 ; horodatages hors du marché (±10 min) : 728.
- Rôles : 328093 lignes preneur, 659389 lignes maker (un même preneur peut être servi par plusieurs makers).
- Horodatages : à la seconde (API Data). Jetons : issue « Up » / « Down » lue dans chaque exécution ; gagnant lu dans Gamma (prix final 1).
- Activité (fusions, séparations, règlements, récompenses) : pas encore lue dans ce fichier.
- Au-delà de 10 000 exécutions : aucune pagination supplémentaire de l'API Data ; seule une reconstruction par la blockchain (sous-graphe OrderFilled, refusé pour l'instant : 429) le permettrait.
- Une réponse de 10 000 lignes n'est jamais supposée complète (marché marqué tronqué).

### 2. Penchant de l'inventaire au fil du cycle (H712)

Makers retenus (≥ 10 marchés complets, ≥ 70 % de volume maker, ≥ 2 500 $ sur la 1re moitié) : 103 ; gagnants (≥ +1 %/$) : 55 ; perdants (≤ −0,5 %/$) : 21. **Classement fait sur la 1re moitié chronologique des marchés (avant le 11.10 01:45 UTC), penchant mesuré sur la 2e moitié uniquement** (sinon « gagnant » et « bon penchant » seraient la même chose).

Précision = part des cycles où le côté surpondéré à t est le gagnant final. Valeur au-delà du marché = Σ résiduel × (résultat − prix implicite à t) / Σ capital résiduel au prix de t (0 attendu sans information ; >0 = le penchant anticipe mieux que le prix du marché à ce moment).

| Groupe | 30 s | 60 s | 90 s | 120 s | 150 s | 180 s | 210 s | 240 s | 270 s | 299 s |
|---|---|---|---|---|---|---|---|---|---|---|
| gagnants | 54 % / -1.1 % | 54 % / +1.1 % | 57 % / +2.4 % | 59 % / +2.5 % | 62 % / +0.8 % | 64 % / +2.5 % | 66 % / +0.2 % | 68 % / +0.1 % | 69 % / +0.5 % | 70 % / +0.4 % |
| perdants | 41 % / -18.4 % | 42 % / -14.8 % | 42 % / -13.7 % | 42 % / -11.2 % | 43 % / -7.7 % | 43 % / -5.8 % | 43 % / -4.2 % | 44 % / +1.5 % | 44 % / -1.3 % | 44 % / -0.6 % |
| autres makers | 52 % / -6.4 % | 50 % / -4.4 % | 54 % / -5.1 % | 52 % / -5.1 % | 52 % / +0.3 % | 52 % / -1.5 % | 53 % / -1.9 % | 49 % / +3.2 % | 49 % / -1.0 % | 49 % / -0.4 % |
| témoin (sens au hasard) | 51 % / -1.3 % | 49 % / -1.9 % | 49 % / -3.0 % | 50 % / -1.4 % | 49 % / -1.0 % | 50 % / +0.4 % | 51 % / -0.4 % | 51 % / -0.0 % | 50 % / +0.0 % | 51 % / +0.0 % |

(chaque case : précision / valeur au-delà du marché par $ de résiduel)

**Valeur au-delà du marché pondérée par le capital, intervalles à 90 % (rééchantillonnage) à 60, 120 et 240 s** :

- gagnants : 60 s : +1.1 % [-2.8 ; +5.1] ; 120 s : +2.5 % [-0.2 ; +5.1] ; 240 s : +0.1 % [-1.1 ; +1.4]
- perdants : 60 s : -14.8 % [-22.0 ; -7.2] ; 120 s : -11.2 % [-17.3 ; -5.1] ; 240 s : +1.5 % [-2.0 ; +5.2]
- témoin (sens au hasard) : 60 s : -1.9 % [-4.9 ; +1.3] ; 120 s : -1.4 % [-3.7 ; +1.0] ; 240 s : -0.0 % [-1.3 ; +1.2]

### 3. Avance du penchant sur le marché (H714)

Délai = premier instant où le penchant (|tilt| ≥ 0,2) est du côté gagnant − premier instant où le favori du marché (prix implicite > 0,5) est le gagnant. Négatif = le portefeuille était du bon côté AVANT que le marché le donne favori. Distribution (p10 / p25 / médiane / p75 / p90) en secondes.

- gagnants (3073 portefeuille-marchés) : -30 / 0 / 0 / 0 / 60 ; part négative (avance) 15 %, nulle 66 %
- perdants (718 portefeuille-marchés) : -60 / 0 / 0 / 0 / 30 ; part négative (avance) 24 %, nulle 63 %
- autres makers (1472 portefeuille-marchés) : -60 / 0 / 0 / 0 / 60 ; part négative (avance) 16 %, nulle 64 %

Limite : seuls le prix Polymarket et le résultat sont disponibles pour tous les marchés ; la probabilité Bot95, la distance Chainlink et le BTC ne le sont que pour les cycles enregistrés à Dublin (étude séparée).


## Annexe — Bot95 — Autopsie des makers et preneurs rentables (H681–H710) — PRÉLIMINAIRE

Généré le 11.10.2026 14:08 UTC. 300 marchés BTC 5 min lus du 10.10 12:25 au 11.10 13:20 UTC (avant la période réservée). Marchés INCOMPLETS (≥ 10 000 exécutions, plafond de l'API) : 88 — exclus de tous les calculs de résultat ci-dessous.

FAITS : exécutions (API Data : portefeuille, maker/preneur, issue, côté, parts, prix, seconde) et activité (fusions, règlements, récompenses). INFÉRENCES : l'interprétation. Frais preneur 0,07·p·(1−p) comptés ; ristourne maker comptée seulement si visible dans l'activité (REWARD). Une vente sans achat visible (jetons venus d'une séparation ou d'un transfert) est signalée.

### 1. Les portefeuilles étudiés (25 plus gros makers, 20 plus rentables, 3 preneurs)

| Portefeuille (adresse complète) | Marchés | Volume maker | Volume preneur | Résultat (paires + jambes seules + ventes − frais) | par $ | 1re moitié / 2e moitié | Creux | Part des 5 meilleurs marchés | Capital médian / max par marché | Fusions | Récompenses |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `0x86b14772a4da70f3e6d5eee06933ebef143efc87` | 207 | 156476 $ | 0 $ | +8989 $ | +5.7 % | +5539 / +3450 $ | -589 $ | 20 % | 683 / 2783 $ | non lu | non lu |
| `0xe29042f5d913dcc4015aab3455c13c58514ca33f` | 210 | 90373 $ | 8369 $ | -749 $ | -0.8 % | -44 / -705 $ | -1537 $ | — | 453 / 1218 $ | non lu | non lu |
| `0x41e2e1ccf1e4940029af02259a31c6b89b9fa354` | 212 | 80879 $ | 91346 $ | +600 $ | +0.3 % | +16 / +584 $ | -348 $ | 102 % | 770 / 1656 $ | non lu | non lu |
| `0x21f4c1a1be34a39a7bc20985df4b7e5a39fb691d` | 207 | 76141 $ | 15852 $ | +1015 $ | +1.1 % | +814 / +200 $ | -583 $ | 92 % | 385 / 1656 $ | non lu | non lu |
| `0xaa1a4f31c010d4a63fc49770d4ca2d69ea370602` | 207 | 64300 $ | 0 $ | -1377 $ | -2.1 % | -639 / -738 $ | -1508 $ | — | 312 / 665 $ | non lu | non lu |
| `0x18c18e0c8c3154360b4f730ec8b9d8013ceb2183` | 177 | 55402 $ | 1474 $ | +384 $ | +0.7 % | +169 / +215 $ | -98 $ | 59 % | 308 / 616 $ | non lu | non lu |
| `0x32ed2e546b187ca15e2841edc82b22c713cf8ec3` | 180 | 49087 $ | 21700 $ | +3379 $ | +4.8 % | +3630 / -251 $ | -1318 $ | 58 % | 309 / 1940 $ | non lu | non lu |
| `0x239e726f1f4131ca78a7e5abf1fec86bfc151c10` | 211 | 47708 $ | 3463 $ | -6253 $ | -12.2 % | -1911 / -4342 $ | -6471 $ | — | 204 / 918 $ | non lu | non lu |
| `0x1a80c37798935774f92fa2f376f0a4e4a7e83b26` | 148 | 47107 $ | 2769 $ | +23 $ | +0.0 % | +112 / -90 $ | -161 $ | 129 % | 298 / 636 $ | non lu | non lu |
| `0xaef68b9bbd746ffe4e582a687cf8a21f1c44134f` | 190 | 44917 $ | 0 $ | +661 $ | +1.5 % | +566 / +95 $ | -314 $ | 6 % | 294 / 419 $ | non lu | non lu |
| `0xc2ad03f79ca3f3c17d8c7de2612ce0c89b7d40ed` | 177 | 44657 $ | 12165 $ | +1933 $ | +3.4 % | +2309 / -376 $ | -1092 $ | 69 % | 213 / 1773 $ | non lu | non lu |
| `0x3725d52f3c252e8374999cc8617292ea2608ad88` | 177 | 44063 $ | 9472 $ | +3763 $ | +7.0 % | +3297 / +466 $ | -989 $ | 48 % | 223 / 1385 $ | non lu | non lu |
| `0x55aeeb3eb4e8cc0da6d9e4939caf533bf6c3f5df` | 161 | 40837 $ | 190 $ | +360 $ | +0.9 % | +66 / +294 $ | -332 $ | 188 % | 137 / 600 $ | non lu | non lu |
| `0xdcedfd60071d904471fb22464be85f54139992c6` | 207 | 39995 $ | 0 $ | +262 $ | +0.7 % | +481 / -219 $ | -377 $ | 146 % | 159 / 594 $ | non lu | non lu |
| `0xee65685de42f8de9a03b4c53ee77d56a20d2cfc9` | 84 | 39799 $ | 15377 $ | -922 $ | -1.7 % | -721 / -201 $ | -1180 $ | — | 38 / 6881 $ | non lu | non lu |
| `0xcd30457c790d8b35a08bcf3f894ad6bb52bc2dd0` | 210 | 38415 $ | 184 $ | +1196 $ | +3.1 % | +784 / +412 $ | -178 $ | 31 % | 171 / 545 $ | non lu | non lu |
| `0xf8af03f1e68ee7162db8983f0d6dd0dc869854c6` | 212 | 37752 $ | 1459 $ | -220 $ | -0.6 % | +222 / -442 $ | -648 $ | — | 154 / 580 $ | non lu | non lu |
| `0x322b2e7c44237c9fed01d534cd1c96687d52aa0c` | 210 | 34044 $ | 0 $ | -614 $ | -1.8 % | -271 / -343 $ | -775 $ | — | 160 / 304 $ | non lu | non lu |
| `0x720babbde4ee159d8735ee09a1e35c4bdb46d2cd` | 172 | 33365 $ | 3124 $ | -124 $ | -0.3 % | +40 / -164 $ | -215 $ | — | 198 / 339 $ | non lu | non lu |
| `0xf9b7876ba2c35370e0bedb7f8ee772da722aa37c` | 209 | 32923 $ | 0 $ | +1944 $ | +5.9 % | +1501 / +443 $ | -174 $ | 21 % | 141 / 411 $ | non lu | non lu |
| `0x4c9497941333332d29f1c235dd23200f3623ffad` | 212 | 31447 $ | 0 $ | +1818 $ | +5.8 % | +1381 / +437 $ | -162 $ | 22 % | 137 / 417 $ | non lu | non lu |
| `0x85a186d1a0be8593bf7eb5d323f96d932bc991b9` | 210 | 30783 $ | 0 $ | -639 $ | -2.1 % | -278 / -361 $ | -687 $ | — | 147 / 249 $ | non lu | non lu |
| `0xeba7be146396301075344bb2d477f2ffdba92d1f` | 86 | 30716 $ | 0 $ | +310 $ | +1.0 % | +160 / +151 $ | +0 $ | 6 % | 396 / 396 $ | non lu | non lu |
| `0x568b079891fcc8bef2e557fa2a8a7ecca1700b3b` | 212 | 29760 $ | 0 $ | +1360 $ | +4.6 % | +954 / +407 $ | -220 $ | 25 % | 135 / 407 $ | non lu | non lu |
| `0x56f609c609975454bf851f0d91079fbc4a5fe251` | 177 | 29595 $ | 4699 $ | +2982 $ | +8.7 % | +2145 / +837 $ | -349 $ | 18 % | 342 / 1000 $ | non lu | non lu |
| `0x368a83f2686acc0db0681e010f410ce323e53057` | 53 | 0 $ | 59936 $ | +7166 $ | +12.0 % | +6191 / +975 $ | -1236 $ | 65 % | 900 / 4716 $ | non lu | non lu |
| `0xc4e21390f8357e33f6692c3cfc4979592de8fef6` | 96 | 0 $ | 56837 $ | +5890 $ | +10.4 % | +3143 / +2747 $ | -1589 $ | 31 % | 410 / 802 $ | non lu | non lu |
| `0x32e0f4b7ab1559ba2ba0089cdc05d40e746958be` | 127 | 0 $ | 19569 $ | +4269 $ | +21.8 % | +2525 / +1743 $ | -532 $ | 15 % | 150 / 150 $ | non lu | non lu |
| `0xc6e3fec2e1a29e7a03e1f2d57f4e4eee39dc8b84` | 79 | 0 $ | 26153 $ | +3880 $ | +14.8 % | +1188 / +2692 $ | -1669 $ | 49 % | 270 / 613 $ | non lu | non lu |
| `0xa9a7b6ac35afed85fed9cde1768c1b09a13bfa09` | 35 | 9016 $ | 12987 $ | +1673 $ | +7.6 % | +1273 / +400 $ | -599 $ | 71 % | 50 / 600 $ | non lu | non lu |
| `0x7f36360df1dcda25dcc2ea99f67bc2ad4d3afc98` | 103 | 1604 $ | 9225 $ | +1555 $ | +14.4 % | +809 / +746 $ | -258 $ | 79 % | 75 / 275 $ | non lu | non lu |
| `0x8718dce13f775c14054c4840cded8b2d2fb7ff8c` | 23 | 0 $ | 6564 $ | +1206 $ | +18.4 % | -7 / +1213 $ | -516 $ | 132 % | 100 / 700 $ | non lu | non lu |
| `0x361528e242bc6cc789ac8da6fd5cb98046178fdf` | 124 | 0 $ | 17516 $ | +1200 $ | +6.9 % | +736 / +464 $ | -246 $ | 54 % | 92 / 927 $ | non lu | non lu |
| `0x2ed94d1a460379292d2e3b46f2cf7d94b033f271` | 209 | 4857 $ | 28448 $ | +1156 $ | +3.5 % | +318 / +838 $ | -683 $ | 102 % | 114 / 1008 $ | non lu | non lu |
| `0x81ff4f443803cb0885cd3683d412b1cd1aa79c4d` | 212 | 11841 $ | 0 $ | +1098 $ | +9.3 % | +660 / +438 $ | -37 $ | 18 % | 48 / 246 $ | non lu | non lu |
| `0xeebde7a0e019a63e6b476eb425505b7b3e6eba30` | 204 | 4112 $ | 30537 $ | +1027 $ | +3.0 % | +293 / +734 $ | -526 $ | 77 % | 124 / 1051 $ | non lu | non lu |
| `0x11aade7bb6828721f988af53e2a70b67dec9c3d7` | 22 | 0 $ | 21799 $ | -713 $ | -3.3 % | -2803 / +2090 $ | -4696 $ | — | 547 / 2900 $ | non lu | non lu |

### 2. Paires Up + Down : d'où vient vraiment le résultat ?

Par portefeuille et par marché : parts appariées = min(Up acheté, Down acheté) après ventes ; coût de la paire = prix moyen Up + prix moyen Down ; résultat des paires = parts appariées × (1 − coût) (acquis quel que soit le gagnant) ; jambe seule = le reste, réglée au résultat officiel.

| Portefeuille | Marchés avec paire | Paire < 1 $ | < 0,98 $ | < 0,95 $ | Coût médian | Délai médian 1re → 2e jambe | Résultat des paires | Résultat des jambes seules | Ventes réalisées | Vente de jetons séparés (déduit) | Frais preneur | Part du résultat venant des paires |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `0x86b14772a4…` | 195 | 48 % | 42 % | 32 % | 1.005 | 27 s | -2693 $ | +11682 $ | +0 $ | +0 $ (0 $ séparés) | 0 $ | -30 % |
| `0xe29042f5d9…` | 204 | 72 % | 58 % | 33 % | 0.970 | 22 s | +3239 $ | -3797 $ | +0 $ | +0 $ (0 $ séparés) | 191 $ | nan % |
| `0x41e2e1ccf1…` | 212 | 53 % | 33 % | 12 % | 0.996 | 5 s | +1279 $ | +1509 $ | +0 $ | +0 $ (0 $ séparés) | 2187 $ | 213 % |
| `0x21f4c1a1be…` | 203 | 72 % | 65 % | 53 % | 0.944 | 38 s | +5151 $ | -3876 $ | +0 $ | +0 $ (0 $ séparés) | 260 $ | 508 % |
| `0xaa1a4f31c0…` | 204 | 62 % | 41 % | 19 % | 0.991 | 16 s | +746 $ | -2123 $ | +0 $ | +0 $ (0 $ séparés) | 0 $ | nan % |
| `0x18c18e0c8c…` | 177 | 65 % | 47 % | 20 % | 0.985 | 4 s | +1243 $ | -1144 $ | +288 $ | +0 $ (0 $ séparés) | 3 $ | 324 % |
| `0x32ed2e546b…` | 125 | 46 % | 42 % | 39 % | 1.016 | 40 s | -1397 $ | +5392 $ | +0 $ | +0 $ (0 $ séparés) | 617 $ | -41 % |
| `0x239e726f1f…` | 156 | 75 % | 72 % | 67 % | 0.867 | 31 s | +5487 $ | -11608 $ | +0 $ | +0 $ (0 $ séparés) | 133 $ | nan % |
| `0x1a80c37798…` | 67 | 46 % | 0 % | 0 % | 1.000 | 3 s | -104 $ | +105 $ | +33 $ | +0 $ (0 $ séparés) | 12 $ | -457 % |
| `0xaef68b9bbd…` | 0 | — | — | — | — | — | +0 $ | +661 $ | +0 $ | +0 $ (0 $ séparés) | 0 $ | 0 % |
| `0xc2ad03f79c…` | 111 | 45 % | 41 % | 41 % | 1.020 | 44 s | -1706 $ | +3935 $ | +0 $ | +0 $ (0 $ séparés) | 296 $ | -88 % |
| `0x3725d52f3c…` | 105 | 46 % | 44 % | 36 % | 1.011 | 41 s | -939 $ | +4942 $ | +0 $ | +0 $ (0 $ séparés) | 241 $ | -25 % |
| `0x55aeeb3eb4…` | 57 | 25 % | 7 % | 7 % | 1.000 | 22 s | +708 $ | -343 $ | +0 $ | +0 $ (0 $ séparés) | 6 $ | 197 % |
| `0xdcedfd6007…` | 174 | 22 % | 17 % | 14 % | 1.114 | 55 s | -1621 $ | +1883 $ | +0 $ | +0 $ (0 $ séparés) | 0 $ | -619 % |
| `0xee65685de4…` | 5 | 0 % | 0 % | 0 % | 1.051 | 160 s | -145 $ | -776 $ | +0 $ | +0 $ (0 $ séparés) | 1 $ | nan % |
| `0xcd30457c79…` | 202 | 47 % | 34 % | 24 % | 1.006 | 18 s | -457 $ | +1671 $ | -12 $ | +0 $ (0 $ séparés) | 5 $ | -38 % |
| `0xf8af03f1e6…` | 178 | 22 % | 20 % | 13 % | 1.115 | 60 s | -1769 $ | +1595 $ | +0 $ | +0 $ (0 $ séparés) | 46 $ | nan % |
| `0x322b2e7c44…` | 210 | 61 % | 38 % | 11 % | 0.991 | 18 s | +296 $ | -910 $ | +0 $ | +0 $ (0 $ séparés) | 0 $ | nan % |
| `0x720babbde4…` | 62 | 39 % | 0 % | 0 % | 1.000 | 8 s | -80 $ | -83 $ | +49 $ | +0 $ (0 $ séparés) | 10 $ | nan % |
| `0xf9b7876ba2…` | 204 | 41 % | 28 % | 19 % | 1.020 | 14 s | -964 $ | +2908 $ | +0 $ | +0 $ (0 $ séparés) | 0 $ | -50 % |
| `0x4c94979413…` | 207 | 36 % | 23 % | 14 % | 1.030 | 14 s | -918 $ | +2736 $ | +0 $ | +0 $ (0 $ séparés) | 0 $ | -51 % |
| `0x85a186d1a0…` | 210 | 56 % | 32 % | 6 % | 0.996 | 18 s | +98 $ | -737 $ | +0 $ | +0 $ (0 $ séparés) | 0 $ | nan % |
| `0xeba7be1463…` | 0 | — | — | — | — | — | +0 $ | +310 $ | +0 $ | +0 $ (0 $ séparés) | 0 $ | 0 % |
| `0x568b079891…` | 207 | 34 % | 25 % | 14 % | 1.021 | 15 s | -916 $ | +2276 $ | +0 $ | +0 $ (0 $ séparés) | 0 $ | -67 % |
| `0x56f609c609…` | 0 | — | — | — | — | — | +0 $ | +0 $ | +0 $ | +3108 $ (61827 $ séparés) | 125 $ | 0 % |
| `0x368a83f268…` | 2 | 0 % | 0 % | 0 % | 1.383 | 128 s | -0 $ | +10492 $ | -2524 $ | +0 $ (0 $ séparés) | 802 $ | -0 % |
| `0xc4e21390f8…` | 3 | 67 % | 67 % | 0 % | 0.980 | 27 s | +1 $ | +6658 $ | +200 $ | +0 $ (0 $ séparés) | 967 $ | 0 % |
| `0x32e0f4b7ab…` | 0 | — | — | — | — | — | +0 $ | +4487 $ | +239 $ | +0 $ (0 $ séparés) | 457 $ | 0 % |
| `0xc6e3fec2e1…` | 1 | 0 % | 0 % | 0 % | 1.064 | 249 s | -3 $ | +4603 $ | +0 $ | +0 $ (0 $ séparés) | 719 $ | -0 % |
| `0xa9a7b6ac35…` | 0 | — | — | — | — | — | +0 $ | +960 $ | +908 $ | +0 $ (0 $ séparés) | 195 $ | 0 % |
| `0x7f36360df1…` | 7 | 0 % | 0 % | 0 % | 1.325 | 74 s | -26 $ | +1358 $ | +367 $ | +0 $ (0 $ séparés) | 144 $ | -2 % |
| `0x8718dce13f…` | 0 | — | — | — | — | — | +0 $ | +1033 $ | +348 $ | +0 $ (0 $ séparés) | 175 $ | 0 % |
| `0x361528e242…` | 9 | 22 % | 22 % | 11 % | 1.136 | 63 s | -82 $ | +1440 $ | +0 $ | +0 $ (0 $ séparés) | 158 $ | -7 % |
| `0x2ed94d1a46…` | 147 | 55 % | 50 % | 40 % | 0.981 | 53 s | +288 $ | +1427 $ | +0 $ | +0 $ (0 $ séparés) | 559 $ | 25 % |
| `0x81ff4f4438…` | 179 | 39 % | 34 % | 25 % | 1.029 | 24 s | -439 $ | +1536 $ | +0 $ | +0 $ (0 $ séparés) | 0 $ | -40 % |
| `0xeebde7a0e0…` | 144 | 49 % | 44 % | 36 % | 1.005 | 53 s | -53 $ | +1626 $ | +0 $ | +0 $ (0 $ séparés) | 546 $ | -5 % |
| `0x11aade7bb6…` | 0 | — | — | — | — | — | +0 $ | +1075 $ | -1327 $ | +0 $ (0 $ séparés) | 462 $ | 0 % |

Vente de jetons séparés : un portefeuille qui VEND des jetons sans les avoir achetés les a obtenus en séparant 1 $ en Up + Down ; on compte ce coût (1 $ la paire) et la jambe non vendue gardée jusqu'au règlement. C'est une déduction (la séparation elle-même n'est visible que dans l'activité).


Lecture : un portefeuille gagne « grâce aux paires » si le résultat des paires est positif et porte l'essentiel du total ; s'il vient des jambes seules, c'est un pari directionnel.

### 3. Autopsie des trois preneurs

### `0x41e2e1ccf1e4940029af02259a31c6b89b9fa354`

212 marchés, volume preneur 91346 $, maker 80879 $ ; marchés avec les deux côtés : 212.

| Rôle | Minute du cycle | Côté | Exécutions | Volume | Résultat au règlement (frais preneur déduits) | par $ |
|---|---|---|---|---|---|---|
| maker | 0–60 s | BUY | 3474 | 22034 $ | -1825 $ | -0.083 |
| maker | 60–120 s | BUY | 2821 | 17787 $ | +305 $ | +0.017 |
| maker | 120–180 s | BUY | 2738 | 18468 $ | -98 $ | -0.005 |
| maker | 180–240 s | BUY | 2438 | 17186 $ | -83 $ | -0.005 |
| maker | 240–300 s | BUY | 646 | 5403 $ | -49 $ | -0.009 |
| preneur | 0–60 s | BUY | 1039 | 19524 $ | +1220 $ | +0.062 |
| preneur | 60–120 s | BUY | 1246 | 26045 $ | +764 $ | +0.029 |
| preneur | 120–180 s | BUY | 1092 | 23971 $ | +291 $ | +0.012 |
| preneur | 180–240 s | BUY | 835 | 19019 $ | +57 $ | +0.003 |
| preneur | 240–300 s | BUY | 94 | 2787 $ | +17 $ | +0.006 |

### `0x11aade7bb6828721f988af53e2a70b67dec9c3d7`

22 marchés, volume preneur 21799 $, maker 0 $ ; marchés avec les deux côtés : 0.

| Rôle | Minute du cycle | Côté | Exécutions | Volume | Résultat au règlement (frais preneur déduits) | par $ |
|---|---|---|---|---|---|---|
| preneur | -180–-120 s | BUY | 2 | 75 $ | +60 $ | +0.800 |
| preneur | -60–0 s | BUY | 8 | 1202 $ | -202 $ | -0.168 |
| preneur | 0–60 s | BUY | 24 | 4749 $ | -872 $ | -0.184 |
| preneur | 60–120 s | BUY | 17 | 5505 $ | -1561 $ | -0.284 |
| preneur | 120–180 s | BUY | 32 | 6719 $ | +1769 $ | +0.263 |
| preneur | 180–240 s | BUY | 7 | 1840 $ | +51 $ | +0.028 |
| preneur | 180–240 s | SELL | 2 | 64 $ | +60 $ | +0.932 |
| preneur | 240–300 s | SELL | 2 | 1646 $ | -18 $ | -0.011 |

### `0xc4e21390f8357e33f6692c3cfc4979592de8fef6`

96 marchés, volume preneur 56837 $, maker 0 $ ; marchés avec les deux côtés : 3.

| Rôle | Minute du cycle | Côté | Exécutions | Volume | Résultat au règlement (frais preneur déduits) | par $ |
|---|---|---|---|---|---|---|
| preneur | 0–60 s | BUY | 816 | 39211 $ | +5535 $ | +0.141 |
| preneur | 60–120 s | BUY | 173 | 9719 $ | +906 $ | +0.093 |
| preneur | 60–120 s | SELL | 2 | 810 $ | -159 $ | -0.196 |
| preneur | 120–180 s | BUY | 69 | 4155 $ | -51 $ | -0.012 |
| preneur | 120–180 s | SELL | 2 | 1664 $ | -311 $ | -0.187 |
| preneur | 180–240 s | BUY | 5 | 262 $ | +84 $ | +0.319 |
| preneur | 180–240 s | SELL | 3 | 1016 $ | -112 $ | -0.111 |

### 4. Risque d'achat à 0,95–0,99 en fin de cycle (M9) — toutes les exécutions de tous les portefeuilles

Achats MAKER à ces prix dans les 30 dernières secondes (aucun frais maker ; ristourne non comptée, de l'ordre de 0,02 c par part à ces prix).

| Prix | Remplissages | Parts | Marchés | Remplissages perdants | Taux de victoire nécessaire (seuil) | Taux observé | Résultat | par part | Plus grosse perte d'un remplissage |
|---|---|---|---|---|---|---|---|---|---|
| 0,95–0,97 | 159 | 4709 | 13 | 0 | ≈ 96 % | 100.00 % | +200 $ | +4.24 c | 0 $ |
| 0,97–0,98 | 134 | 4208 | 17 | 0 | ≈ 97,5 % | 100.00 % | +126 $ | +3.00 c | 0 $ |
| 0,98–0,99 | 239 | 7432 | 21 | 0 | ≈ 98,5 % | 100.00 % | +149 $ | +2.00 c | 0 $ |
| ≥ 0,99 | 3722 | 246126 | 209 | 0 | ≈ 99,3 % | 100.00 % | +1632 $ | +0.66 c | 0 $ |

Lecture : à 0,98, une seule part perdue coûte 0,98 $ et efface 49 parts gagnées. Une politique plafonnée à 0,95 se lit sur la 1re ligne.

### 5. Intégrité des données

- Marchés lus : 300 ; incomplets (≥ 10 000 exécutions) : 88 (exclus des résultats). Plafond de l'API Data : décalage ≤ 10 000.
- Événements blockchain (OrderFilled) : le sous-graphe public Goldsky a répondu « trop de requêtes » (429) depuis GitHub ; reconstruction par la blockchain NON faite à ce stade.
- Maker / preneur : déduit de l'API Data (liste « preneur seulement »), non vérifié contre les événements blockchain.
- Fusions, séparations, règlements, récompenses : lus dans l'activité des portefeuilles étudiés seulement (« non lu » sinon). Une vente sans achat visible signale des jetons venus d'une séparation.
- Ristournes maker : comptées seulement si l'activité les montre. Frais preneur : calculés (0,07·p·(1−p)).


## Annexe — Bot95 — Tout combiné avec tout (PRÉLIMINAIRE, non validé statistiquement)

Généré le 11.10.2026 13:52 UTC. 17653 trades fantômes BTC de 100 stratégies (+ portefeuille TOUS : 1336 trades), du 06.10 10:05 au 11.10 12:50 UTC. Apprentissage avant le 10.10 02:40 UTC, validation après. Période réservée (≥ 13.10) non lue.

Combinaisons testées : 892 (1 à 3 filtres, au moins 40 trades en apprentissage et 20 en validation pour le classement).

### Le contrôle qui compte : combien de « gagnants » le hasard fabrique-t-il ?

- Données réelles : parmi les 300 meilleures combinaisons en apprentissage, **100** restent positives en validation.
- Résultats mélangés au hasard (aucun vrai signal) : **157** sur 300 restent positives en validation.
- Si les deux nombres sont proches, les « meilleures combinaisons » sont surtout du hasard sélectionné après coup.

### Les 30 meilleures combinaisons en apprentissage, et ce qu'elles font ensuite

| Stratégie | Filtres | Trades appr. | Résultat appr. | par $ | Trades valid. | Résultat valid. | par $ valid. |
|---|---|---|---|---|---|---|---|
| corrige_desaccord_20 | écart 0.2–0.3 | 54 | +1941 $ | +1.04 | 107 | -696 $ | -0.21 |
| desaccord_30_zone_+_modele_monte | prix 0.15–0.35 + écart 0.3–+ | 44 | +1305 $ | +0.91 | 53 | +1377 $ | +0.98 |
| V2-G_jury_des_bourses | restant 120–180 s + écart 0.2–0.3 | 46 | +1754 $ | +0.91 | 69 | -962 $ | -0.33 |
| desaccord_30_zone_+_modele_monte | prix 0.15–0.35 + côté Down | 57 | +1736 $ | +0.90 | 54 | +729 $ | +0.44 |
| desaccord_30_zone_+_modele_monte | côté Down | 59 | +1728 $ | +0.87 | 54 | +729 $ | +0.44 |
| desaccord_30_zone_+_modele_monte | écart 0.3–+ | 46 | +1297 $ | +0.87 | 53 | +1377 $ | +0.98 |
| V2-B_hors_60-89_s | écart 0.2–0.3 + côté Down | 45 | +1410 $ | +0.78 | 40 | -357 $ | -0.38 |
| desaccord_30_zone_+_modele_monte | prix 0.15–0.35 + restant 60–120 s | 51 | +1452 $ | +0.75 | 36 | +489 $ | +0.46 |
| desaccord_20_sans_nuit | écart 0.2–0.3 + côté Down | 40 | +1115 $ | +0.75 | 22 | -156 $ | -0.30 |
| V2-D_perp_120-269_s | restant 120–180 s + nuit 0–8 h | 41 | +1317 $ | +0.74 | 28 | -555 $ | -0.45 |
| V2-B_hors_60-89_s | écart 0.2–0.3 | 80 | +2244 $ | +0.74 | 85 | -43 $ | -0.02 |
| desaccord_20_sans_nuit | écart 0.2–0.3 | 68 | +1886 $ | +0.74 | 54 | +308 $ | +0.21 |
| desaccord_30_zone_+_Binance_et_perp_+_sortie_modele_-10_+_pas_Poly_qui_baisse_+_taille_25_50 | prix 0.15–0.35 + côté Down | 57 | +1255 $ | +0.72 | 102 | +55 $ | +0.02 |
| TOUS (premier trade du cycle et du côté) | restant 180–240 s + écart 0.2–0.3 | 47 | +1302 $ | +0.72 | 51 | -121 $ | -0.07 |
| desaccord_30_zone_+_Binance_et_perp_+_sortie_modele_-10_+_pas_Poly_qui_baisse_+_taille_25_50 | côté Down | 59 | +1289 $ | +0.71 | 102 | +55 $ | +0.02 |
| desaccord_30_zone_+_modele_monte | prix 0.15–0.35 | 105 | +2575 $ | +0.70 | 105 | +1305 $ | +0.40 |
| desaccord_30_zone_+_modele_monte | restant 60–120 s | 53 | +1374 $ | +0.68 | 36 | +489 $ | +0.46 |
| corrige_V2-F_ecart_qui_grandit | écart 0.2–0.3 | 65 | +1542 $ | +0.67 | 119 | -359 $ | -0.10 |
| V2-D_perp_120-269_s | prix 0.00–0.15 | 63 | +1603 $ | +0.65 | 45 | +62 $ | +0.03 |
| V2-F_+_plus_de_120_s | écart 0.2–0.3 | 56 | +1394 $ | +0.64 | 113 | +29 $ | +0.01 |
| desaccord_30_zone_+_Binance_et_perp_+_sortie_modele_-10_+_pas_Poly_qui_baisse_+_taille_25_50 | nuit 0–8 h | 48 | +979 $ | +0.64 | 58 | +459 $ | +0.30 |
| V2-C_perp | écart 0.2–0.3 + côté Down | 50 | +1489 $ | +0.64 | 63 | -1254 $ | -0.42 |
| desaccord_30_zone_+_Binance_et_perp_+_sortie_modele_-10_+_pas_Poly_qui_baisse_+_taille_25_50 | prix 0.15–0.35 + nuit 0–8 h | 47 | +932 $ | +0.62 | 58 | +459 $ | +0.30 |
| desaccord_30_zone_+_Binance_et_perp_+_sortie_modele_-10_+_pas_Poly_qui_baisse_+_taille_25_50 | prix 0.15–0.35 | 99 | +1911 $ | +0.62 | 198 | +447 $ | +0.09 |
| V2-E_persistant | restant 120–180 s + écart 0.2–0.3 | 44 | +1382 $ | +0.61 | 44 | -804 $ | -0.42 |
| corrige_V2-F_+_pas_les_deux_baissent | écart 0.2–0.3 | 64 | +1387 $ | +0.59 | 123 | -453 $ | -0.12 |
| V2-B_hors_60-89_s | prix 0.15–0.35 + écart 0.2–0.3 | 47 | +1063 $ | +0.59 | 79 | -14 $ | -0.01 |
| V2-H_veto_complet | prix 0.00–0.15 | 77 | +2028 $ | +0.59 | 27 | -849 $ | -0.70 |
| desaccord_30_zone_+_Binance_et_perp_+_sortie_modele_-10_+_pas_Poly_qui_baisse_+_taille_25_50 | restant 60–120 s | 62 | +1124 $ | +0.58 | 83 | +414 $ | +0.22 |
| V2-G_jury_des_bourses | restant 120–180 s + nuit 0–8 h | 43 | +1042 $ | +0.58 | 35 | -1317 $ | -0.88 |

### Les combinaisons positives sur les DEUX périodes, triées par la validation (au moins 30 trades dans chaque)

| Stratégie | Filtres | Trades appr. | par $ appr. | Trades valid. | par $ valid. | Résultat total |
|---|---|---|---|---|---|---|
| desaccord_30_zone_+_modele_monte | prix 0.15–0.35 + écart 0.3–+ | 44 | +0.91 | 53 | +0.98 | +2682 $ |
| desaccord_30_zone_+_modele_monte | écart 0.3–+ | 46 | +0.87 | 53 | +0.98 | +2674 $ |
| desaccord_30_zone_0,15-0,35_+_Binance_et_perp | écart 0.3–+ | 42 | +0.52 | 57 | +0.50 | +1618 $ |
| desaccord_30_zone_0,15-0,35_+_Binance_et_perp | prix 0.15–0.35 + écart 0.3–+ | 40 | +0.55 | 57 | +0.50 | +1627 $ |
| TOUS (premier trade du cycle et du côté) | restant 120–180 s + écart 0.2–0.3 | 52 | +0.49 | 38 | +0.46 | +1625 $ |
| desaccord_30_zone_+_modele_monte | restant 60–120 s | 53 | +0.68 | 36 | +0.46 | +1863 $ |
| desaccord_30_zone_+_modele_monte | prix 0.15–0.35 + restant 60–120 s | 51 | +0.75 | 36 | +0.46 | +1942 $ |
| desaccord_30_zone_+_modele_monte | côté Down | 59 | +0.87 | 54 | +0.44 | +2456 $ |
| desaccord_30_zone_+_modele_monte | prix 0.15–0.35 + côté Down | 57 | +0.90 | 54 | +0.44 | +2465 $ |
| desaccord_30_zone_+_Binance_et_perp_+_sortie_modele_-10 | écart 0.3–+ | 42 | +0.51 | 57 | +0.40 | +1421 $ |
| desaccord_30_zone_+_Binance_et_perp_+_sortie_modele_-10 | prix 0.15–0.35 + écart 0.3–+ | 40 | +0.52 | 57 | +0.40 | +1399 $ |
| desaccord_30_zone_+_modele_monte | prix 0.15–0.35 | 105 | +0.70 | 105 | +0.40 | +3880 $ |
| desaccord_30_zone_+_modele_monte | côté Up | 50 | +0.40 | 51 | +0.35 | +1326 $ |
| desaccord_30_zone_+_modele_monte | prix 0.15–0.35 + côté Up | 48 | +0.47 | 51 | +0.35 | +1415 $ |
| desaccord_30_zone_+_Binance_et_perp_+_sortie_modele_-10_+_pas_Poly_qui_baisse_+_taille_25_50 | nuit 0–8 h | 48 | +0.64 | 58 | +0.30 | +1438 $ |
| desaccord_30_zone_+_Binance_et_perp_+_sortie_modele_-10_+_pas_Poly_qui_baisse_+_taille_25_50 | prix 0.15–0.35 + nuit 0–8 h | 47 | +0.62 | 58 | +0.30 | +1391 $ |
| desaccord_30_zone_+_Binance_et_perp_+_sortie_modele_-10 | restant 60–120 s + côté Down | 40 | +0.27 | 40 | +0.28 | +779 $ |
| TOUS (premier trade du cycle et du côté) | restant 120–180 s | 188 | +0.25 | 102 | +0.26 | +2932 $ |
| desaccord_30_zone_+_Binance_et_perp_+_sortie_modele_-10_+_pas_Poly_qui_baisse_+_taille_25_50 | restant 60–120 s | 62 | +0.58 | 83 | +0.22 | +1538 $ |
| desaccord_30_zone_+_Binance_et_perp_+_sortie_modele_-10_+_pas_Poly_qui_baisse_+_taille_25_50 | prix 0.15–0.35 + restant 60–120 s | 59 | +0.56 | 83 | +0.22 | +1456 $ |
| corrige_zone_+_Binance_et_perp_+_sortie_-10 | prix 0.15–0.35 | 50 | +0.21 | 114 | +0.21 | +1242 $ |
| desaccord_20_sans_nuit | écart 0.2–0.3 | 68 | +0.74 | 54 | +0.21 | +2194 $ |
| TOUS (premier trade du cycle et du côté) | prix 0.15–0.35 + restant 120–180 s | 97 | +0.21 | 61 | +0.42 | +1827 $ |
| TOUS (premier trade du cycle et du côté) | côté Down + après-midi 14–20 h | 61 | +0.30 | 60 | +0.20 | +1188 $ |
| desaccord_30_zone_+_sortie_modele_-10 | nuit 0–8 h | 63 | +0.19 | 74 | +0.27 | +1118 $ |
| TOUS (premier trade du cycle et du côté) | restant 120–180 s + côté Down | 97 | +0.35 | 42 | +0.18 | +1662 $ |
| TOUS (premier trade du cycle et du côté) | prix 0.15–0.35 + restant 180–240 s + côté Up | 56 | +0.17 | 52 | +0.39 | +1110 $ |
| desaccord_30_zone_+_sortie_modele_-10 | prix 0.15–0.35 + nuit 0–8 h | 62 | +0.17 | 74 | +0.27 | +1054 $ |
| desaccord_30_zone_+_sortie_modele_-10 | restant 60–120 s + côté Down | 47 | +0.16 | 45 | +0.16 | +498 $ |
| desaccord_30_zone_0,15-0,35_+_Binance_et_perp | restant 60–120 s + côté Down | 40 | +0.16 | 40 | +0.26 | +581 $ |

**Filtres qui reviennent le plus souvent dans les combinaisons positives sur les deux périodes** : prix 0.15–0.35 (13), restant 60–120 s (7), côté Down (7), écart 0.3–+ (6), restant 120–180 s (4), nuit 0–8 h (4), côté Up (3), écart 0.2–0.3 (2), après-midi 14–20 h (1), restant 180–240 s (1)

### Limites
- Beaucoup de combinaisons testées : certaines « marchent » par chance (voir le témoin mélangé).
- Les trades fantômes supposent l'achat au prix vu (pas de retard de 150 ms, pas de file).
- Seul le test sur la période réservée (cycles ≥ 13.10) peut confirmer un filtre ; aucun filtre n'est ajouté sans ton accord.


## Annexe — Bot95 — Vérifications H559–H564 (préliminaire)

Généré le 11.10.2026 13:03 UTC. 1 cycles enregistrés avec la version du 11.10 14:55 (bornes à trois niveaux), avant la période réservée. Aucun fantôme ni règle modifié.

**Statut des chiffres** — MESURE : heures, files vues à l'arrivée, transactions, prix. SIMULATION : remplissages (trois bornes), résultats en $. INSUFFISANT : tout ce qui porte sur moins de ~30 remplissages.

### 1. Interactions des conditions a / b / c (offres de M2 marge 5 c, classées à la pose)

a : bourses −10 $ en 300 ms ; b : flux agressif net ≥ 250 000 $ contre nous en 250 ms ; c : ≥ 100 parts vendues sur nos acheteurs en 500 ms ; chacune « active » si déclenchée dans les 2 s avant la pose (même pause que M4). Classement fait uniquement avec les données reçues AVANT la pose.

| Combinaison | Opportunités (offres posées) | Remplies (prudent) | Parts | Résultat prudent | par part | Sélection adverse +1 / +3 / +5 / +10 s (c/part) |
|---|---|---|---|---|---|---|
| aucune | 83 | 0 | 0 | +0 $ | +nan c | — / — / — / — |
| a | 0 | — | — | — | — | — |
| b | 0 | — | — | — | — | — |
| c | 3 | 0 | 0 | +0 $ | +nan c | — / — / — / — |
| ab | 0 | — | — | — | — | — |
| ac | 0 | — | — | — | — | — |
| bc | 0 | — | — | — | — | — |
| abc | 0 | — | — | — | — | — |

Effet propre d'une condition = ligne « a » (ou « b », « c ») seule contre « aucune » ; interaction = lignes combinées contre la somme des effets propres. Avec si peu de remplissages, aucune interaction ne peut être distinguée du hasard à ce stade.

### 2. M6 : durée de vie et perte de priorité

| Variante | Offres | Temps réellement actif médian (ms) | Remplacements par cycle et côté (médiane) | Temps sans offre (annulations en attente, total s) | Parts remplies pendant l'annulation | Offres remplies | Perte de priorité estimée par remplacement (parts, médiane / p90) |
|---|---|---|---|---|---|---|---|
| M2 cotation marge 5 c | 86 | 1086 | 0 | 0.0 | 0 | 5 | — |
| M6 duree de vie 100 ms | 1809 | 88 | 874 | 52.4 | 64 | 5 | 0 / 15 |
| M6 duree de vie 250 ms | 911 | 238 | 417 | 25.0 | 0 | 6 | 0 / 20 |
| M6 duree de vie 500 ms | 516 | 488 | 217 | 13.0 | 9 | 6 | 0 / 30 |
| M6 duree de vie 1000 ms | 301 | 987 | 106 | 6.4 | 0 | 6 | 0 / 45 |

Perte de priorité = file devant la nouvelle offre à son arrivée − file qui restait devant l'ancienne à son annulation (borne prudente : seules les transactions l'ont fait avancer). MESURE de la file affichée ; l'avancée dans la file est SIMULÉE.

### 3. Cohérence de la file d'attente

Offres posées contrôlées : 4147. Remplissages partiels (prudent) : 48.

- prudent > central : **19** offres ; central > optimiste : **0** offres.
  - M2 cotation marge 5 c : prudent > central 1
  - M4 retrait toxique : prudent > central 2
  - M4a seul bourses -10 $ : prudent > central 2
  - M4b seul flux agressif : prudent > central 1
  - M4c seul ventes Polymarket : prudent > central 1
  - M5 remplissage attendu : prudent > central 4
  - M6 duree de vie 100 ms : prudent > central 1
  - M6 duree de vie 1000 ms : prudent > central 2
  - M6 duree de vie 250 ms : prudent > central 2
  - M6 duree de vie 500 ms : prudent > central 3

**Cause identifiée dans le code (non corrigée, fantômes gelés jusqu'au verdict)** : la borne « prudente » plafonne la file devant nous à la quantité affichée (min avec l'affiché), alors que la borne centrale et la borne optimiste ne sont pas plafonnées. Après de gros retraits, la prudente peut donc avancer plus vite que la centrale. L'ordre prudent ≤ central ≤ optimiste n'est garanti que si les trois bornes appliquent le même plafond.

Borne STRICTE recalculée hors ligne (ventes à notre prix après la file vue à l'arrivée, sans plafond ni retrait ; traversée = tout) :

| Variante | Parts stricte (hors ligne) | Parts prudent (enregistré) | Parts central | Parts optimiste | central ≤ optimiste ? | stricte ≤ central ? |
|---|---|---|---|---|---|---|
| M0 temoin aleatoire | 174 | 174 | 174 | 174 | oui | oui |
| M1 V2-F ecart qui grandit | 179 | 179 | 179 | 179 | oui | oui |
| M1 V2-F incertitude 0,01 % | 0 | 0 | 0 | 0 | oui | oui |
| M1 cohorte B : V2-F corrige 0,015 % | 147 | 147 | 147 | 147 | oui | oui |
| M1 desaccord 30 | 278 | 278 | 278 | 278 | oui | oui |
| M2 cotation marge 10 c | 260 | 260 | 260 | 260 | oui | oui |
| M2 cotation marge 5 c | 130 | 173 | 224 | 255 | oui | oui |
| M3 anticipation Chainlink | 172 | 172 | 172 | 172 | oui | oui |
| M4 retrait toxique | 130 | 185 | 224 | 262 | oui | oui |
| M4a seul bourses -10 $ | 130 | 179 | 224 | 255 | oui | oui |
| M4b seul flux agressif | 130 | 173 | 224 | 255 | oui | oui |
| M4c seul ventes Polymarket | 130 | 173 | 224 | 262 | oui | oui |
| M5 remplissage attendu | 339 | 291 | 331 | 365 | oui | NON |
| M6 duree de vie 100 ms | 239 | 294 | 239 | 239 | oui | oui |
| M6 duree de vie 1000 ms | 249 | 194 | 226 | 260 | oui | NON |
| M6 duree de vie 250 ms | 232 | 246 | 230 | 230 | oui | NON |
| M6 duree de vie 500 ms | 230 | 247 | 230 | 230 | oui | oui |
| M8 hybride V2-F ecart qui grandit | 179 | 179 | 179 | 179 | oui | oui |
| M8 hybride V2-F incertitude 0,01 % | 0 | 0 | 0 | 0 | oui | oui |
| M8 hybride cohorte B : V2-F corrige 0,015 % | 147 | 147 | 147 | 147 | oui | oui |
| M8 hybride desaccord 30 | 278 | 278 | 278 | 278 | oui | oui |

La borne stricte hors ligne n'est pas toujours ≤ la borne enregistrée : le fichier du cycle donne l'heure THÉORIQUE d'arrivée et d'annulation (pose + trajet), alors que le fantôme en direct ne devient actif qu'au déclenchement réel de son minuteur (quelques ms plus tard). Une transaction tombée dans cet intervalle est comptée hors ligne mais pas en direct (et inversement à l'annulation). Ces écarts sont des différences de minutage, pas des doubles comptages ; les heures réelles d'arrivée et d'annulation ne sont pas encore enregistrées dans le fichier compact.


Double comptage entre fantômes : chaque fantôme se simule SEUL face au carnet réel ; deux fantômes au même prix sont remplis par la même transaction. Leurs résultats ne s'additionnent donc pas (offres simultanées au même prix et à la même seconde : 4041). Un défaut de partage entre fantômes de l'attribution transaction/retrait (borne centrale) a été corrigé à 14:55 ; les offres antérieures ne sont pas utilisées ici.

### 4. Calcul de M8 (hybride maker / preneur)

Ce que fait le code actuel (gelé jusqu'au verdict) :

- **Preneur** : espérance = parts disponibles au prix vu (50 $) × probabilité du modèle − coût frais compris (0,07·p·(1−p)). Le retard de 150 ms N'entre PAS dans la décision ; il n'entre que dans l'exécution simulée (quantité réellement présente 150 ms + trajet plus tard).

- **Maker** : espérance = parts attendues en 10 s × (probabilité du modèle − prix − 2 c). Les parts attendues viennent du rythme des ventes des 30 dernières s moins la file devant nous. Ce n'est **PAS** un gain conditionnel au remplissage : la non-exécution est seulement implicite (parts attendues), la sélection adverse est une constante de 2 c (alors que la mesure sur M2 est de −8 à −11 c), aucune ristourne ni frais maker, et la probabilité du modèle n'est pas recalculée sachant qu'on est rempli.

- **Conséquence** : M8 surestime le gain maker. Une version conforme (P(remplissage) × E[gain | remplissage] avec sélection adverse mesurée, et preneur × probabilité de survie à 164 ms) est proposée comme NOUVEAU fantôme après le verdict, sur les données d'apprentissage seulement ; M8 actuel reste inchangé.

- M8 : pas encore de positions réglées.


## Annexe — Bot95 — Trois idées de Claude, premier test sur les cycles enregistrés (PRÉLIMINAIRE)

51 cycles de Dublin (avant la période réservée) ; gagnant lu dans le carnet de fin de cycle (inconnu pour 21). Aucune règle, aucun bot modifié.

### I1. Suivre les gros preneurs Polymarket

| Taille de la transaction preneuse | Transactions | Mouvement du milieu dans son sens +1 s / +5 s / +30 s (c) | Suivre au même prix : résultat par part au règlement |
|---|---|---|---|
| < 100 $ | 56344 | +0.47 / +0.62 / +0.30 | -0.40 c (35312) |
| 100–500 $ | 862 | +0.16 / -0.05 / -1.15 | -2.19 c (563) |
| ≥ 500 $ | 57 | +1.54 / -0.08 / -0.94 | -11.29 c (36) |

Si les grosses transactions continuent dans leur sens, on peut les suivre sans course de vitesse (horizon de secondes, pas de millisecondes).

### I2. Maker de fin de cycle sur le côté presque acquis (≥ 0,90 à 30 s de la fin)

- Cycles avec un côté ≥ 0,90 à 30 s de la fin : 9 ; ce côté a gagné 9 fois (100 %).
- Cycles où des vendeurs ont frappé les acheteurs de ce côté (≥ 0,90) dans les 30 dernières s : 8 ; volume médian 1227 parts ; prix moyen 0.984 ; le côté a gagné 8 fois sur 8.
- Un acheteur posé à ces prix (sans frais maker, avec ristourne) gagne 1 − prix par part si le côté gagne, perd le prix sinon.

### I3. Double maker (meilleur acheteur ET meilleur vendeur du jeton Up)

- Fenêtres de 10 s : 1428 ; meilleur acheteur consommé : 1181 ; meilleur vendeur consommé : 1183 ; LES DEUX : 1119 (78 %). Écart médian au début de la fenêtre : 1.0 c.
- Un double maker en tête de file gagnerait l'écart sur ces fenêtres ; ailleurs il garde un côté seul (risque directionnel, sélection adverse mesurée sur M2).

### Limites
- Une journée de données ; aucune file d'attente simulée pour I2 et I3 (on suppose être en tête) : ce sont des PLAFONDS.
