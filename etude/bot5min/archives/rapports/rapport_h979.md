# Bot95 — H979 à H985 : options Deribit, CME, Coinbase, gamma, avance exécutable — rapport du 12.10.2026

**Cadre**
- Étude hors ligne uniquement. Aucun ordre réel, aucun abonnement acheté.
- Aucun bot ni fantôme modifié ; H816, H821 et R4 sont inchangés. La période réservée n'a pas été lue.
- Protocole enregistré sur GitHub **avant tout calcul** (commit 3020365).

**Données**
- Toutes les transactions d'options BTC de Deribit du 12.09 au 12.10 : 192 759 transactions, récupérées gratuitement par l'API publique d'historique.
- BTC Binance à la seconde sur 30 jours (apprentissage avant le 02.10, test du 02.10 au 11.10).
- Laboratoire de Dublin du 11.10 au 12.10, avec le carnet Polymarket et les résultats officiels.

## 0. Audit des données

| Source | Disponible ? | Limite / coût |
|---|---|---|
| Transactions d'options Deribit (instrument, côté preneur, quantité, volatilité implicite) | **oui**, gratuit, 30 jours | heure de l'échange seulement : on suppose l'information disponible 100 ms après. Environ 6 300 transactions par jour, une toutes les 14 s. |
| Open interest Deribit par prix d'exercice, carnets d'options | **non** en historique | gratuit en direct : à enregistrer à partir de maintenant pour tester H981 |
| Deribit indice, perpétuel, DVOL | oui à Dublin depuis aujourd'hui 11:55 UTC | trop récent pour cette étude |
| Coinbase BTC/USD | prix et flux agressifs à Dublin depuis le 11.10 | carnet L2 public et gratuit, mais pas encore enregistré |
| CME BTC et Micro BTC | **non** | payant, chez Databento par exemple : historique à partir de 0,50 $ par Go, 125 $ de crédit offert, temps réel dans les offres payantes. Rien n'a été acheté. |
| Nasdaq, taux, dollar, or | **non** à la seconde | sources gratuites en bougies de 1 minute seulement |

## 1. H979 — Les grosses transactions d'options précèdent-elles le BTC ?

**Définition**
- Grosse transaction : plus de 1,25 M$ de notionnel (95e centile de l'apprentissage).
- Le mouvement du BTC est signé dans le sens du delta du preneur.
- On mesure aussi les 10 secondes **avant** la transaction, pour distinguer avance et réaction.

| Échantillon | Catégorie | Événements | 10 s AVANT | 1 s après | 10 s après | 30 s après | Placebo 10 s |
|---|---|---|---|---|---|---|---|
| Apprentissage | toutes | 6 782 | **+4,1 $** | +0,2 | +0,7 | +0,7 | 0,0 |
| Test | toutes | 3 044 | **+6,4 $** | −0,1 | +0,7 | +1,4 | +0,2 |
| Test | courtes (< 2 jours), proches de la monnaie | 193 | **+15,1 $** | −2,0 | +1,3 | +5,3 | −0,2 |
| Test | blocs | 1 066 | −0,4 | 0,0 | −0,3 | +0,3 | +0,6 |

**Les grosses transactions d'options suivent le BTC, elles ne le précèdent pas.** Le BTC a déjà bougé de 4 à 15 $ dans le bon sens dans les 10 s avant la transaction. Après, il reste moins d'un dollar à 1 à 10 s. Ce sont des réactions, ou des couvertures, à un mouvement déjà fait.

**Le même événement à Dublin** (190 cas, heures de réception, résultat officiel)

| Mesure | Résultat |
|---|---|
| BTC spot, 10 s avant (signé) | **+6,0 $** [+1,6 ; +11,6] |
| Perp Bybit après 250 / 500 / 1 000 ms | +0,8 / +1,6 / +1,8 $ |
| Binance spot après 250 / 500 / 1 000 ms | +0,3 / +0,5 / +0,7 $ |
| Polymarket +1 c dans le bon sens | 47 % des cas, délai médian 750 ms |
| Règlement officiel − modèle (signé) | +0,05 [+0,01 ; +0,10] |
| Achat de 20 $ du jeton dans le sens, à 164 ms, conservé | **−177 $** sur 125 achats, IC [−689 ; +496] |

Le petit effet sur le règlement **ne se traduit pas en profit** au prix Polymarket réellement exécutable.

## 2. H980 — Le flux delta des options ajoute-t-il de l'information ?

Le flux delta est la somme du delta acheté ou vendu par les preneurs, pondéré par la quantité, sur des fenêtres de 1 à 60 s, avec en plus la volatilité implicite. Mesure sur 517 588 instants, sur 30 jours.

| Cible | AUC BTC seul | AUC + flux delta | ΔAUC (IC corrigé) |
|---|---|---|---|
| Hausse BTC à 5 s | 0,6101 | 0,6098 | −0,0002 [−0,0006 ; +0,0001] |
| Hausse BTC à 10 s | 0,6146 | 0,6144 | −0,0002 |
| Hausse BTC à 30 s | 0,5878 | 0,5873 | −0,0005 |
| Hausse BTC à 60 s | 0,5590 | 0,5576 | −0,0015 |

**Règlement** (11 512 décisions de test) : Brier 0,1353 sans le flux delta, 0,1352 avec. Le gain est nul.

**Le flux delta des options n'apporte aucune information** en plus du flux et du momentum du BTC.

## 3. H981 — Gamma des teneurs de marché

**Non testable.** L'open interest par prix d'exercice n'existe pas en historique gratuit. Pour le tester, il faudrait l'enregistrer chaque minute à partir de maintenant. C'est gratuit, mais il faut modifier l'enregistreur, donc ton accord. Rappel : même enregistré, l'open interest ne dit pas la position nette des teneurs de marché.

## 4. H982 — CME

**Non testable sans abonnement.** Le coût est indiqué dans l'audit, et rien n'a été acheté. Vu que le perp Bybit, déjà gratuit, mène le spot sans que Polymarket soit battable (H937/H969), **je ne recommande pas d'acheter le CME** à ce stade.

## 5. H983 — Coinbase BTC/USD

Le flux agressif Coinbase et l'écart Coinbase − Binance sont ajoutés au modèle Binance (flux et momentum).

| Cible | Échantillon | AUC Binance seul | AUC + Coinbase | ΔAUC (IC 90 %) |
|---|---|---|---|---|
| Hausse Binance à 5 s | validation | 0,614 | 0,625 | **+0,011 [+0,008 ; +0,014]** |
| Hausse Binance à 5 s | test | 0,613 | 0,622 | **+0,009 [+0,005 ; +0,013]** |
| Hausse Binance à 30 s | validation | 0,585 | 0,593 | +0,008 [+0,005 ; +0,010] |
| Hausse Binance à 30 s | test | 0,601 | 0,601 | +0,000 [−0,003 ; +0,004] |

**Coinbase apporte une petite information réelle sur 5 secondes**, stable sur la validation et le test, mais **rien à 30 s**. C'est trop court pour un règlement à 5 minutes, et H937/H969 ont montré que Polymarket intègre ce genre de mouvement en environ 250 ms.

## 6. H984 / H985 — Combinaison et avance exécutable

- **H984** : pas construite. Aucun instrument n'a de valeur individuelle démontrée sur le règlement ou le P&L.
- **H985, avance temporelle** :
  - options Deribit : avance **négative**, elles arrivent après le mouvement ;
  - perp Bybit : environ 250 ms, mais Polymarket réagit en environ 250 ms (H937) ;
  - Coinbase : utile sur 5 s seulement.
  - Aucun instrument disponible ne laisse d'avance économique après nos 164 ms.

## 7. Classement des instruments (selon l'information supplémentaire et la rentabilité, pas la corrélation)

| Instrument | Avance | Information en plus | Règlement | P&L exécutable | Verdict |
|---|---|---|---|---|---|
| Grosses transactions d'options | **négative** (réaction) | non | +0,05 | −177 $ | **Abandonner** |
| Flux delta des options | — | ΔAUC ≈ 0 | gain nul | — | **Abandonner** |
| Gamma des teneurs de marché | non testable | — | — | — | Approfondir **seulement** si tu acceptes d'enregistrer l'open interest |
| CME | non testable | — | — | — | **Ne pas acheter** pour l'instant |
| Coinbase BTC/USD | environ 5 s | +0,01 d'AUC à 5 s | non testé | non testé | Petite information réelle, horizon trop court : **en réserve** |
| Perp Bybit (rappel H937) | environ 250 ms | oui | — | non démontré | Utile seulement avec une latence bien plus faible |

## Conclusion

Les options Deribit ne contiennent pas d'information **avant** le BTC : les grosses transactions réagissent à des mouvements déjà faits. Coinbase apporte quelques millièmes d'AUC sur 5 secondes. Aucune source gratuite testée ne donne une avance que Polymarket n'ait pas déjà intégrée au moment où l'on peut acheter.

Deux décisions te reviennent, sans urgence :
1. Enregistrer l'open interest Deribit par prix d'exercice (H981) et le carnet Coinbase. C'est gratuit et en lecture seule, mais il faut modifier l'enregistreur de Dublin.
2. Acheter des données CME. Je ne le recommande pas à ce stade.

Sources des coûts : [Databento — Futures data](https://databento.com/futures), [Coinbase — canaux WebSocket publics](https://docs.cdp.coinbase.com/coinbase-app/advanced-trade-apis/websocket/websocket-channels.md).

Fichiers :
- https://github.com/pitch6767/wallet-autopsy/blob/main/etude/bot5min/resultat_options_h979.md
- https://github.com/pitch6767/wallet-autopsy/blob/main/etude/bot5min/options_h979.py
