# Bot95 — 2e diagnostic FAST, maker et Chainlink (12.10.2026, 20 h)

**C'est un diagnostic, pas un verdict.** Les données s'arrêtent au 12.10, et la période réservée (cycles à partir du 13.10 00:00 UTC) n'a pas été lue. Aucun fantôme gelé ni aucune règle n'a été modifié, et aucun ordre réel n'a été passé.

**Données :** 408 cycles de Dublin (11.10 → 12.10 19:00 UTC). 335 d'entre eux ont été enregistrés avec la version du 11.10 14:55, nécessaire pour les files d'attente.

## MESURES

**Trous des carnets Binance et Bybit.** Moyennes sur les 115 derniers cycles :

| Source | Silences par cycle | Durée médiane | Temps perdu par cycle |
|---|---|---|---|
| Binance | 8 | 0,65 s | ~8 s sur 300 s |
| Bybit | 2 | 1,3 s | ~4 s |
| Coinbase | 2 | 1,3 s | ~3 s |

- Transactions Binance manquantes : 2 cas en 115 cycles.
- La fausse alerte de séquence Coinbase a disparu depuis la version du 12.10 après-midi.
- **Aucun cycle n'est tronqué depuis la correction du plafond** (version 8afb99a3762d). Au total, 11 cycles l'avaient été.

**Pourquoi les meilleures offres disparaissent** (≈ 150 000 disparitions) :
- 51 % sont retirées par leur auteur ;
- 21 % sont consommées par une transaction ;
- 18 % sont déplacées à un autre prix ;
- 10 % restent indéterminées.

**Retard preneur.** Avec 150 ms de retard plus le trajet, il faut au moins **164 ms d'avance** pour atteindre une offre. Avec 200 ms d'avance, l'offre est encore là dans 93 % des cas, mais on n'en obtient que 50 % de la quantité.

**Avance réelle de l'information.** Un saut d'au moins 5 $ sur une bourse précède seulement 26 % des disparitions. Il donne au moins 164 ms d'avance dans 20 % des cas. Après un tel saut, une offre disparaît dans 32 % des cas, contre 20 % à des instants tirés au hasard.

**Concurrents plus rapides.** 49 % des transactions sur le côté devenu trop bon marché ont lieu moins de 150 ms après NOTRE information. D'autres acheteurs l'ont donc avant nous, ou achètent sans elle.

**Chainlink.**
- La moyenne officielle 60 s correspond à la reconstruction sur [T−60 ; T−1], avec un écart médian de 0,36 $.
- Le prix à battre calculé à Dublin s'écarte du prix officiel de 0,29 $ en médiane (7,15 $ au maximum).
- La moyenne officielle arrive à Dublin 1,27 s après son instant de calcul.

## SIMULATIONS (remplissages maker simulés, file d'attente à trois niveaux de prudence)

**Tournoi H650 préliminaire** : 217 cycles communs, 50 $ au plus par trade. Tous les intervalles de confiance contiennent zéro.

| Stratégie | Résultat | IC 90 % |
|---|---|---|
| FAST (preneur à 164 ms) | +3 470 $ | −2 388 à +10 008 $ |
| HYBRID (FAST, sinon SLOW) | +3 684 $ | −2 525 à +10 383 $ |
| SLOW (preneur à 1,164 s) | +620 $ | — |
| M4 retrait toxique (prudent) | +7 662 $ | — |
| M5 remplissage attendu | +4 219 $ | — |
| M2 marge 5 c | +2 271 $ | — |
| M0 témoin aléatoire | −2 935 $ | — |

**Comparaison des makers sur les mêmes cycles** (résultat prudent) :

| Fantôme | Résultat | IC 90 % |
|---|---|---|
| M2 marge 5 c | +925 $ | −1 717 à +3 723 $ |
| M4 retrait toxique | +827 $ | — |
| M4a, seulement le signal « bourses −10 $ » | +1 692 $ | −1 273 à +4 713 $ |
| M4b, seulement le signal « flux agressif » | +1 336 $ | — |
| M4c, seulement le signal « ventes Polymarket » | −1 816 $ | — |
| M0 témoin aléatoire | −3 373 $ | −4 838 à −1 889 $ |

**Durée de vie des offres (M6).** Plus l'offre vit peu longtemps, plus elle est souvent remplacée :
- 100 ms : 590 remplacements par cycle et par côté, 13 207 s sans offre au total ;
- 1 000 ms : 40 remplacements par cycle et par côté.

**Cohérence de la file.** Le niveau central ne dépasse jamais le niveau optimiste (0 cas). Mais le niveau prudent dépasse le central dans 10 977 offres, presque toutes du maker double (M10). C'est **à vérifier dans le code** avant de lire M10.

## CONTREFACTUELS (recalculs hors ligne, à ne pas lire comme des remplissages réels)

**Les huit combinaisons des conditions de retrait M4** (a = bourses −10 $, b = flux agressif contre nous, c = ventes sur nos acheteurs) :
- les remplissages qui auraient été évités par a et b ensemble perdaient −564 $ (IC −991 à −96 $) ;
- seule la condition « flux agressif » (b) évite des remplissages réellement mauvais : −1 933 $ évités au total, au prix de 127 bons remplissages perdus ;
- la condition c seule évite +877 $ de **bons** remplissages.

**Annulations retardées** : M4 fait +1 771 $ avec des annulations immédiates, +2 087 $ retardées de 100 ms, +1 339 $ à 300 ms, et +15 $ à 1 s.

**Témoins au hasard :**
- des annulations aléatoires à la même fréquence donnent en médiane +637 $ ;
- des pauses aléatoires de même durée donnent +1 184 $.

M4 ne bat donc pas clairement le hasard.

## HYPOTHÈSES

- Le retard preneur de 150 ms vient de la documentation. Il n'a jamais été mesuré : seul un vrai ordre de 1 $ le mesurerait, et il attend ton accord.
- On suppose que nos ordres ne changent pas le comportement des autres.

## NON CONCLUANT

- Aucune variante maker n'a d'intervalle de confiance entièrement positif.
- FAST, SLOW et HYBRID : intervalles de confiance qui contiennent zéro.
- Les interactions a/b/c reposent sur moins de 50 remplissages par combinaison : impossible de les distinguer du hasard.
- **Idées de Claude :**
  - suivre les gros preneurs : perd de −1,2 à −2,7 c par part ;
  - maker de fin de cycle sur le côté presque acquis : 29 gains sur 30, mais c'est un plafond, sans file d'attente simulée ;
  - double maker : les deux meilleurs prix sont consommés ensemble dans 80 % des fenêtres de 10 s, mais c'est aussi un plafond.
- **Suivi des makers :** le fichier resultat_makers_suivi.md n'a pas été régénéré ce soir ; sa dernière mise à jour date du 12.10 à 14:05 UTC.

Le verdict FAST et maker est prévu le 15.10 à 17:00 UTC sur la période réservée, en une seule fois.
