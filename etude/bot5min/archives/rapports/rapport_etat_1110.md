# Bot95 — résultats au dimanche 11.10.2026, 08:45 (heure suisse)

> **Résumé pour ChatGPT**
> - **Période jugée :** depuis la remise à zéro de tous les fantômes, le samedi 10.10 à 13:50, soit environ 19 h et 225 cycles BTC de 5 minutes.
> - **Mode :** argent fictif seulement (MODE_REEL = non).
> - **La nuit a été mauvaise pour toute la famille V2** (désaccord modèle / marché) : entre −1 188 $ et −3 332 $.
>   - V2-G jury des bourses, le meilleur du bilan sur 3 jours, est maintenant **le pire** : −3 332 $.
> - **Seule la famille « zone » tient :** désaccord ≥ 0,30 sur un jeton entre 0,15 et 0,35, avec des filtres. Sept variantes sur huit sont positives ; elles vont de −39 $ à +730 $.
> - **Vitesse mesurée en direct :** 5 à 16 % des offres visées ont déjà disparu 0,1 s après le signal, et 14 à 33 % après 0,5 s.
> - **Conclusion provisoire :** 19 h ne suffisent pas pour juger. Mais le schéma « fort au début, puis effondrement » se répète pour V2. Aucune stratégie n'est validée.

## 1. Rappels

**Le bot**
- Marchés Polymarket « BTC Up/Down 5 minutes ».
- Chaque fantôme simule au plus un achat par cycle, 50 $ au maximum, au prix vendeur affiché et dans la quantité affichée, frais compris. Il garde la position jusqu'au règlement.

**Exécution**
- Les fantômes créés le 10.10 achètent au **seul meilleur vendeur**.
- Les plus anciens (V2, désaccords, zone) achètent jusqu'au meilleur vendeur + 1 c.

**Règlement**
- Prix à battre = moyenne Chainlink des 60 s avant le début du cycle.
- Prix final = moyenne Chainlink des 60 dernières secondes.

**Remise à zéro du 10.10 13:50**
- Tous les compteurs sont repartis de 0 au même moment, pour comparer les fantômes sur les mêmes cycles.
- Les trades d'avant sont conservés à part.

## 2. Toutes les stratégies BTC actives, depuis le 10.10 13:50

Colonnes : trades, part de gagnés, résultat net, creux maximal (pire baisse depuis un sommet), plus longue série de pertes. Classement par résultat.

| Stratégie | Trades | Gagnés | Résultat | Creux max | Pertes de suite |
|---|---|---|---|---|---|
| desaccord 30 zone + modele monte | 61 | 31 % | **+730 $** | −259 $ | 6 |
| corrige : zone + Binance et perp + sortie -10 | 66 | 29 % | **+668 $** | −116 $ | 8 |
| desaccord 20 Binance ou perp avec nous | 26 | 42 % | **+571 $** | −112 $ | 5 |
| desaccord 30 zone + Binance et perp + sortie modele -10 + pas Poly qui baisse + taille 25/50 | 110 | 25 % | **+502 $** | −257 $ | 11 |
| desaccord 30 0,15-0,60 + perp + ecart qui grandit | 122 | 25 % | **+486 $** | −544 $ | 10 |
| desaccord 30 zone + sortie modele -10 | 134 | 22 % | **+344 $** | −551 $ | 12 |
| desaccord 30 zone 0,15-0,35 | 134 | 23 % | **+340 $** | −493 $ | 12 |
| desaccord 30 zone 0,15-0,35 + Binance et perp | 119 | 25 % | **+306 $** | −606 $ | 11 |
| desaccord confirme perp | 33 | 39 % | **+240 $** | −471 $ | 6 |
| desaccord 20 Binance ou perp avec nous sans nuit | 13 | 31 % | **+214 $** | −110 $ | 5 |
| desaccord 20 Binance avec nous | 1 | 100 % | **+135 $** | +0 $ | 0 |
| desaccord 20 jeton 0,35-0,65 | 13 | 62 % | **+113 $** | −40 $ | 2 |
| desaccord 30 zone + Binance et perp + sortie modele -10 | 119 | 24 % | **+4 $** | −629 $ | 11 |
| desaccord 30 | 212 | 15 % | **−10 $** | −622 $ | 20 |
| V2-F miroir 1 s | 75 | 28 % | **−22 $** | −520 $ | 6 |
| desaccord 30 zone + Binance et perp + sortie modele -10 + pas Poly qui baisse | 110 | 25 % | **−39 $** | −574 $ | 11 |
| TWAP fin confirme Chainlink 0,5 s | 32 | 28 % | **−211 $** | −361 $ | 6 |
| desaccord 20 Poly rejoint 10 s sans nuit | 27 | 48 % | **−242 $** | −301 $ | 3 |
| corrige marge mesuree : V2-F | 184 | 32 % | **−256 $** | −782 $ | 9 |
| V2-F incertitude 0,01 % | 185 | 31 % | **−338 $** | −493 $ | 10 |
| corrige : desaccord 20 | 190 | 30 % | **−350 $** | −981 $ | 10 |
| TWAP fin sauts | 61 | 31 % | **−395 $** | −648 $ | 8 |
| TWAP fin prevision Chainlink | 57 | 33 % | **−412 $** | −412 $ | 5 |
| TWAP fin correction spot-perp | 60 | 33 % | **−424 $** | −666 $ | 8 |
| desaccord 20 sans nuit | 130 | 22 % | **−427 $** | −703 $ | 16 |
| TWAP fin quantiles | 59 | 32 % | **−430 $** | −704 $ | 8 |
| corrige : V2-F + garde-fou | 189 | 28 % | **−548 $** | −941 $ | 10 |
| corrige : V2-F ecart qui grandit | 189 | 28 % | **−550 $** | −942 $ | 10 |
| TWAP fin anti-saut | 63 | 25 % | **−731 $** | −847 $ | 9 |
| corrige : V2-F + pas les deux baissent | 188 | 28 % | **−750 $** | −927 $ | 10 |
| TWAP fin | 65 | 25 % | **−777 $** | −939 $ | 11 |
| V2-F pause memoire | 185 | 22 % | **−866 $** | −1 140 $ | 13 |
| V2-F + plus de 120 s | 219 | 23 % | **−1 188 $** | −1 707 $ | 14 |
| V2-B hors 60-89 s | 226 | 23 % | **−1 292 $** | −1 568 $ | 14 |
| V2-D perp 120-269 s | 218 | 21 % | **−1 296 $** | −2 345 $ | 14 |
| V2-C perp | 226 | 22 % | **−1 423 $** | −2 072 $ | 14 |
| V2-F ecart qui grandit | 226 | 23 % | **−1 474 $** | −1 879 $ | 14 |
| desaccord 20 60-180 s | 218 | 18 % | **−1 997 $** | −1 997 $ | 13 |
| V2-F + pas les deux baissent | 226 | 22 % | **−2 213 $** | −2 551 $ | 14 |
| V2-E persistant | 226 | 18 % | **−2 624 $** | −2 820 $ | 20 |
| V2-H veto complet | 226 | 20 % | **−2 809 $** | −2 974 $ | 14 |
| V2-G jury des bourses | 220 | 17 % | **−3 332 $** | −3 332 $ | 19 |

## 3. Ce qui ressort

1. **La famille V2 s'effondre pour la deuxième nuit de suite**, tant que le marché ne rejoint pas le modèle. Elle va de −1 188 $ à −3 332 $, et tous ses fantômes perdent.
   - Sur 3 jours (07.10 → 10.10), ces mêmes stratégies gagnaient +1 182 $ à +2 458 $, mais presque tout venait de la première moitié.
2. **La famille « zone » est la seule positive (7 variantes sur 8).** Elle achète un désaccord ≥ 0,30 sur un jeton entre 0,15 et 0,35, avec plus de 60 s restantes. Ses variantes :
   - « zone + modèle monte » : +730 $ sur 61 trades ;
   - « corrigé : zone + Binance et perp + sortie −10 » : +668 $ sur 66 trades ;
   - zone simple : +340 $ sur 134 trades.
   - La seule variante négative est « zone + Binance et perp + sortie −10 + pas Poly qui baisse » (−39 $).
   - Les creux vont de −116 $ à −629 $.
3. **TWAP fin (fin de cycle) est négatif pour toutes ses variantes** : −211 $ à −777 $ sur environ 60 trades.
   - La version « quantiles », jugée la plus solide la veille, fait −430 $.
4. **Les trois nouvelles variantes de V2-F**, sur les mêmes cycles que V2-F original (−1 474 $ sur 226 trades) :
   - **miroir 1 s :** −22 $ sur 75 trades. Elle évite le plus de pertes, parce qu'elle achète beaucoup moins.
   - **incertitude 0,01 % :** −338 $ sur 185 trades.
   - **pause mémoire :** −866 $ sur 185 trades.
   - **Les trois font mieux que l'original, mais aucune ne gagne.**
5. **Les trois fantômes « diversité »**, lancés le 10.10 vers 14:20 :
   - désaccord 30 : −10 $ sur 212 trades ;
   - désaccord 20 entre 60 et 180 s : −1 997 $ sur 218 trades ;
   - désaccord 20 jeton 0,35–0,65 : +113 $ sur 13 trades, ce qui est trop peu pour juger.

## 4. La vitesse, mesurée en direct (1 109 signaux depuis le 10.10 14:20)

Pour chaque signal, le bot regarde si l'offre vue au moment de la décision est encore achetable, au même prix ou mieux, un peu plus tard.

| Stratégie | Signaux | Offre déjà partie à 0,1 s | 0,25 s | 0,5 s | 1 s | 2 s |
|---|---|---|---|---|---|---|
| V2-F original | 223 | 12 % | 18 % | 27 % | 31 % | 41 % |
| V2-F 0,01 % | 182 | 16 % | 26 % | 33 % | 41 % | 42 % |
| V2-F miroir 1 s | 75 | 15 % | 20 % | 25 % | 28 % | 40 % |
| désaccord 30 | 215 | 15 % | 23 % | 33 % | 38 % | 38 % |
| désaccord 20 60-180 s | 219 | 5 % | 9 % | 14 % | 21 % | 27 % |

**Âge des données au moment de la décision**

| Source | Médiane | 9 cas sur 10 sous |
|---|---|---|
| Coinbase | 0,14 s | 0,80 s |
| OKX | 0,21 s | 1,19 s |
| Binance | 0,22 s | 1,18 s |
| Bybit | 0,32 s | 3,6 s |
| Chainlink | 0,53 s | 1,14 s |

- **Bybit est parfois très en retard.** C'est un problème, car le modèle s'en sert en premier.
- **Les horloges sont décalées :** l'heure des messages Polymarket est 0,13 à 0,29 s en avance sur celle du bot. Les mesures sous 0,25 s n'y sont donc pas fiables.

## 5. Les études faites samedi

**META-ROUTER** (choisir la stratégie selon la volatilité, la tendance, l'heure) : **abandonné.**
- Sur 469 cycles hors apprentissage, la meilleure stratégie fixe fait +1 352 $.
- Le routeur fait +326 $, et +117 $ avec l'heure.
- Un portefeuille fixe des six stratégies fait +97 $.
- Les stratégies sont trop corrélées entre elles (0,7 à 0,8) pour qu'un routeur ait de quoi choisir.

**Attribution de V2-F 0,01 %**
- Ses gagnants propres viennent bien de la formule : 45 sur 47.
- Mais son gain dépend de la vitesse :

| Délai d'exécution | Résultat |
|---|---|
| 0 s | +3 794 $ |
| 0,25 s | +2 089 $ |
| 0,5 s | +109 $ |
| 1 s | −54 $ |

- Les offres qui disparaissent en moins d'une demi-seconde portent tout le gain.

**Expériences V3 (001 à 006)**
- Aucune piste ne tient en validation avec 0,5 s de délai.
- Coinbase devance Chainlink, pas Polymarket.
- Le prix Polymarket est mieux calibré que notre modèle (Brier 0,152 contre 0,201).
- Les régimes de marché s'inversent d'une période à l'autre.
- Un routeur simple perd 2 648 $ par rapport à la meilleure stratégie fixe.

**Bilan sur 3 jours (07.10 → 10.10)**
- Six stratégies V2 étaient positives, mais toutes surtout dans la première moitié.
- Polymarket bouge en premier dans 64 % des cas.
- Le gain vient uniquement des cycles où Polymarket rejoint ensuite le modèle (+9 130 $).

## 6. Le serveur rapide (VPS de Dublin)

- Un programme fantôme est prêt pour le serveur 107.174.203.201 : aucun ordre, aucune clé de portefeuille.
- Il garde les connexions ouvertes en permanence et mesure à la milliseconde, de 1 ms à 2 s, si les offres visées sont encore là.
- L'installation est en cours par Replit, sans toucher au reste du serveur. Pas encore de mesures.

## 7. Questions ouvertes (décisions de Pitch)

1. **Famille V2.** Après deux nuits fortement négatives, faut-il arrêter certaines variantes ? Les candidates les plus évidentes sont V2-G, V2-H et V2-E.
2. **Famille zone.** C'est la seule positive sur cette période. Mais 19 h ne suffisent pas. Le verdict de mardi 14.10 la jugera sur plus de cycles.
3. **Vitesse.** La plupart des gains théoriques sont dans des offres qui disparaissent en moins d'une demi-seconde. Seules les mesures du serveur de Dublin, puis un vrai ordre (le test de 1 $, reporté), diront si nous pouvons arriver à temps.
4. **Ce qu'on ne peut pas conclure :** aucune stratégie n'est validée, et aucune n'est en argent réel.
