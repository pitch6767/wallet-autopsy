# Bot95 — Analyses makers refaites sur données COMPLÈTES — 11.10.2026

**Données.** 600 marchés BTC 5 min, du 09.10 13:40 au 11.10 15:35 UTC.
- 595 marchés sont complets. Seuls 5 restent tronqués à 10 000 exécutions ; ils sont exclus.
- La collecte compte 2,32 millions d'exécutions, plus l'activité de 38 wallets (fusions, règlements, ristournes).
- La première collecte avait été perdue (fichier > 100 Mo). Elle a été refaite.
- Hors ligne, aucun ordre. Aucun fantôme modifié. La période réservée (≥ 13.10) n'a pas été lue.

**Mode de lecture.** FAITS = mesuré dans les données. INFÉRENCES = interprétation. HYPOTHÈSES = à tester.

## 1. Ce qui change par rapport aux résultats sur données tronquées

| Point | Avant (tronqué) | Maintenant (complet) |
|---|---|---|
| Rentabilité des 3 wallets 0xf9b7… / 0x4c94… / 0x568b… | +4,6 à +5,9 % par $ | **+0,8 à +1,4 % par $** |
| Les makers « gagnants » restent-ils gagnants ? | non mesuré | **non** : −0,8 % par $ sur la 2e moitié (perdants : 0,0 %) |
| Les 3 wallets vendent-ils de moins bons billets que les autres makers (à prix et minute égaux) ? | +0,4 pt, non significatif | **−3,3 pts [−5,3 ; −1,3]**, significatif |
| Indice « flux 1–3 s avant le signal » | placebo 11–12 % | **placebo 63–67 %**, l'indice disparaît |
| Identité des wallets dans la calibration | dégrade | +0,0015 de log loss ; placebo 28 % : **pas d'apport** |
| Veto « 3 wallets 30 s » | non significatif | **nuisible** : −14,6 parts [−30,5 ; −0,8] |
| Reverse Bot95 (acheter le côté opposé) | −0,09 $ par part | **−0,22 $ par part [−0,34 ; −0,11]** |

**Conclusion maintenue et renforcée :** abandonner l'identité des wallets comme signal de trading.

## 2. Faits principaux

**La rentabilité des makers ne persiste pas d'une moitié à l'autre (H718).**
- Les makers classés gagnants sur la 1re moitié perdent −0,8 % par $ sur la 2e moitié.
- Les makers classés perdants font 0,0 %.
- Les deux groupes perdent sur les outsiders (−4 % par $). Les bons résultats viennent des achats du favori qui « rééquilibrent » un stock.

**Penchant de l'inventaire (H712/H714).**
- Le côté surpondéré par les makers gagnants ne bat pas le prix du marché. Mesure à 60 s : −4,8 % [−8,0 ; −1,9].
- Leur penchant n'arrive pas en avance sur le marché : retard médian de 0 s pour tous les groupes.

**Les 3 wallets.**
- Ce sont des acheteurs purs des deux côtés : 0 vente. Leurs paires Up+Down coûtent 1,06–1,07 $ et ils les fusionnent (137 à 165 fusions chacun). Les paires perdent environ 5 300 à 5 900 $ chacune.
- Les jambes non appariées gagnent +6 600 à +7 100 $. Résultat net : +1 200 à +1 800 $.

**Risque d'achat à 0,95–0,99 en fin de cycle (M9), selon le temps restant :**

| Prix d'achat (maker) | 30 à 15 s restantes | 15 à 5 s | 5 à 0 s |
|---|---|---|---|
| ≥ 0,99 | **34 perdants, −1 033 $** | 0 perdant, +2 084 $ | 0 perdant, +834 $ |
| 0,95–0,99 | 44 perdants, +1 833 $ | 5 perdants, +335 $ | 0 perdant, +141 $ |

Le risque se concentre entre 30 et 15 s avant la fin. Aucune perte n'est observée dans les 5 dernières secondes.

**Sélection adverse (toxicité).**
- Les makers réels gagnent +0,4 à +0,7 c au bout de 1 à 5 s.
- Nos fantômes maker perdent −1 à −3 c, sauf M3.
- Résultat par part au règlement : M1 +2,1 c et M21 +1,6 c sont positifs ; M4/M6/M8 vont de −4,5 à −7,3 c.

**Bot95 sur 353 signaux complets (74 cycles).**
- Taux de gain de 34 % à un prix moyen de 0,23.
- Signaux encore achetables à 250 ms : 29 % de gain. Signaux partis avant : 48 %. La sélection adverse par la latence est confirmée.
- Achat du côté Bot95 à 250 ms : +0,06 $ par part [−0,02 ; +0,14] sur tous les signaux. Sur le test : +0,31 $ par part [+0,10 ; +0,52].

## 3. Inférences

- Le savoir-faire des makers rentables n'est pas une information directionnelle exploitable. Leurs résultats sont faibles et ne persistent pas.
- Les 3 wallets ont pourtant une meilleure sélection de leurs fills que les autres makers (−3,3 pts pour l'acheteur). Sur nos signaux, cela ne se traduit pas en information utilisable avant le signal.

## 4. Hypothèses, encore à tester

- M9 (achats à 0,95–0,99) ne serait sûr que dans les 15 dernières secondes. Ce n'est pas encore testé hors échantillon.
- **H717, M22 et M23 ne sont pas faits ici.** Pour M23, l'activité de 0x56f609c6… ne figure pas dans la collecte : il faudrait l'ajouter à la liste des wallets suivis.

Détails :
- resultat_autopsie_wallets.md
- resultat_tilt_makers.md
- resultat_avantage_makers.md
- resultat_toxicite_makers.md
- resultat_chercher_encore.md
- resultat_contreparties_h724.md
