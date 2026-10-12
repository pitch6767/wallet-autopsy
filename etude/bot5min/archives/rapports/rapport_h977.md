# Bot95 — H976 / H977 / H978 : flux de début de cycle contre prix Polymarket, déplacement de cotations, alerte multi-actifs — rapport du 12.10.2026

**Cadre**
- Étude hors ligne uniquement. Aucun ordre réel.
- Aucun bot ni fantôme modifié ; H816, H821 et R4 sont inchangés. La période réservée n'a pas été lue.
- Protocole enregistré sur GitHub **avant tout calcul** (commit 13bf7ab).

**Échantillons (laboratoire de Dublin)**

| Échantillon | Cycles | Remarque |
|---|---|---|
| Apprentissage | 169 | seul utilisé pour apprendre les règles et les coefficients |
| Validation | 85 | |
| Test | 71 | 12.10, 06:00–12:00 UTC ; déjà consulté pour H941 |
| Nouveau | 12 | à partir de 12:00 UTC ; trop peu pour conclure |

La définition H941 est reprise **sans changement**. Les résultats économiques utilisent le règlement officiel.

## Réponse courte

1. **H977 — non, Polymarket ne sous-estime pas le côté favorisé par le flux.** Le prix du marché prévoit mieux le résultat que notre modèle, même augmenté de l'effet H941. Acheter ce côté au prix exécutable rapporte zéro hors apprentissage. **Abandonner comme stratégie d'achat.**
2. **H976 — l'explication par le déplacement de cotations est confirmée**, mais elle n'apporte **aucune information supplémentaire** aux mesures simples. **Abandonner comme signal.**
3. **H978 — ETH et SOL précèdent légèrement les vagues BTC**, avec un petit gain réel. Il n'est **pas mesurable sur Polymarket**, faute de données ETH et SOL à Dublin. **Approfondir seulement si on enregistre ETH et SOL à Dublin.**

## 1. H977 — Le flux de début de cycle crée-t-il une sous-évaluation Polymarket ?

**Méthode**
- Une décision par cycle : la première vague agressive forte entre 150 et 240 s avant la fin. On regarde le côté du flux.
- Trois probabilités comparées :
  - **A** : modèle de règlement seul ;
  - **B** : prix Polymarket (milieu du carnet) ;
  - **C** : A + effet H941, appris sur l'apprentissage (décalage de +1,08 en logit).

**Qualité des probabilités** (Brier, plus bas = mieux)

| Échantillon | Décisions | Victoire du côté du flux | A règlement | B Polymarket | C règlement + H941 |
|---|---|---|---|---|---|
| Apprentissage | 61 | 75 % | 0,206 | 0,178 | 0,155 |
| Validation | 45 | 64 % | 0,176 | **0,157** | 0,182 |
| Test | 27 | 70 % | 0,142 | **0,125** | 0,140 |

**Le prix Polymarket est le meilleur** sur la validation et le test. L'effet H941 n'aide que sur l'apprentissage, là où il a été appris.

**P&L** : achat de 20 $ du côté du flux, exécuté 164 ms plus tard au prix vu, frais compris, conservé jusqu'au règlement officiel.

| Échantillon | Règle | Achats | Victoire | Prix payé | Avantage par achat (IC 90 %) | P&L | Gagnants / perdants | Drawdown |
|---|---|---|---|---|---|---|---|---|
| Apprentissage | toujours | 44 | 77 % | 0,64 | +0,13 [+0,03 ; +0,23] | +285 $ | 34 / 10 | 79 $ |
| Validation | toujours | 29 | 72 % | 0,74 | **−0,01 [−0,14 ; +0,10]** | −25 $ | 21 / 8 | 88 $ |
| Test | toujours | 20 | 65 % | 0,66 | **−0,01 [−0,15 ; +0,13]** | −47 $ | 13 / 7 | 62 $ |
| Test | si C − prix ≥ 0,05 | 11 | 64 % | 0,55 | +0,09 [−0,12 ; +0,28] | −5 $ | 7 / 4 | 26 $ |
| Nouveau | toujours | 1 | 0 % | 0,66 | — | −20 $ | 0 / 1 | — |

**Autres mesures**
- **Latence** : 164, 300 ou 500 ms donnent presque le même résultat. Ce n'est pas la vitesse qui manque.
- **Proches de 50 %** : 11 cas sur le test, avantage +0,07 [−0,15 ; +0,27]. Non démontré.
- **Calibration hors apprentissage** : un billet payé 0,60 gagne 64 % du temps ; un billet payé 0,80 gagne 90 % du temps. Le prix est presque juste.
- **Jackpots** : 8 sur l'apprentissage, 0 sur la validation et le test.

**Verdict H977.** L'effet de +0,10 sur le règlement (H941) est **déjà dans le prix Polymarket** au moment où l'on peut acheter : le côté du flux coûte en moyenne 0,66 à 0,74. **Abandonner comme stratégie d'achat.**

## 2. H976 — Pourquoi les retraits synchronisés annoncent une baisse

Chaque retrait d'offres vendeuses synchronisé sur Binance et Bybit est classé sur les 2 secondes suivantes :
- **déplacement** : le meilleur vendeur descend et de nouvelles offres apparaissent ;
- **consommation** : ce sont des achats agressifs qui ont pris les offres ;
- **annulation** : tous les autres cas.

L'inverse s'applique côté acheteurs.

Mouvement BTC dans le sens attendu (baisse après un retrait vendeur), en $ :

| Échantillon | Classe | Événements | 1 s | 10 s | 30 s | 10 s après le classement (t + 2 s) |
|---|---|---|---|---|---|---|
| Validation | déplacement | 841 | +3,7 | +10,8 | +12,4 | **+4,9 [+3,8 ; +5,9]** |
| Validation | annulation | 1 384 | −0,3 | +0,4 | +0,6 | +1,5 [+1,0 ; +2,0] |
| Test | déplacement | 615 | +3,5 | +11,3 | +12,1 | **+5,2 [+3,8 ; +6,6]** |
| Test | annulation | 1 064 | −0,3 | −0,2 | +0,4 | +1,0 [+0,2 ; +1,7] |
| Nouveau | déplacement | 297 | +5,0 | +13,6 | +13,6 | +3,6 [+2,1 ; +6,7] |

Aucun retrait synchronisé n'a été classé « consommation ».

**Lecture**
- L'hypothèse est **confirmée** : quand les vendeurs annulent leurs offres et les reposent plus bas, le prix continue de baisser d'environ 4 à 5 $ dans les 10 s suivantes. C'est stable sur les 4 échantillons.
- Les simples annulations, sans nouvelle offre plus basse, ne font presque rien.
- Rien ne prouve que ce soit le même teneur de marché qui annule puis repose.

**Apport marginal** pour prévoir le sens du BTC (AUC, IC corrigé pour 12 comparaisons) :

| Cible | Échantillon | A : OFI + momentum + volatilité | B : + retraits synchronisés | C : + déplacement |
|---|---|---|---|---|
| Hausse à 10 s | validation | 0,668 | 0,668 | 0,670 (+0,003 [+0,001 ; +0,004]) |
| Hausse à 10 s | test | 0,658 | 0,655 | 0,657 |
| Hausse à 10 s | nouveau | 0,690 | 0,684 | 0,684 |
| Hausse à 30 s | test | 0,618 | 0,616 | 0,615 |

**Verdict H976.** Le mécanisme est réel et stable, mais il est **déjà contenu dans l'OFI et le momentum**. Le gain est de +0,003 au mieux, et seulement sur la validation. **Abandonner comme signal.**

## 3. H978 — Un autre actif précède-t-il les vagues BTC ?

**(a) ETH et SOL, Binance à la seconde, 30 jours, test du 02.10 au 11.10.** Part des vagues BTC où l'actif avait déjà bougé dans le même sens **avant** la vague, comparée à des instants pris au hasard :

| Actif | 1 s avant | 2 s | 5 s | 10 s |
|---|---|---|---|---|
| ETH | +2,1 pts | +2,7 pts | **+5,0 pts [+2,8 ; +6,7]** | **+6,0 pts [+3,9 ; +7,6]** |
| SOL | +1,6 pts | +2,3 pts | **+4,3 pts [+2,5 ; +5,8]** | **+5,8 pts [+4,2 ; +7,2]** |

Pour prévoir le **sens** d'une vague BTC avec les données arrêtées 5 s avant son début, l'AUC passe de 0,605 avec BTC seul à **0,618 avec ETH et SOL**, soit +0,013 [+0,005 ; +0,020]. Le gain est petit mais réel.

**(b) Places BTC à Dublin, dans les 2 s avant les vagues de début de cycle.** Le perp Bybit, OKX, Coinbase et Chainlink bougent dans le sens de la vague à peu près **en même temps** que Binance spot. C'est une corrélation simultanée, pas une avance exploitable.

**Limites**
- ETH et SOL ne sont pas enregistrés à Dublin. Leur effet sur le règlement Polymarket et sur l'exécution n'est donc **pas mesurable**.
- Nasdaq, or, devises et CME ne sont pas disponibles à la seconde.
- Deribit n'est enregistré que depuis aujourd'hui, 11:55 UTC.

**Verdict H978.** Il y a une petite avance d'ETH et SOL sur les vagues BTC, de l'ordre de 1 à 2 points d'AUC. Pour aller plus loin, il faudrait **enregistrer les flux ETH et SOL à Dublin**. Cela demande ton accord, puisque c'est une modification de l'enregistreur, en lecture seule.

## 4. Recommandations

| Piste | Décision proposée |
|---|---|
| H977 Flux de début de cycle → achat Polymarket | **Abandonner** : le marché intègre déjà l'effet |
| H976 Déplacement de cotations | **Abandonner comme signal** : déjà contenu dans l'OFI et le momentum |
| H978 ETH/SOL → BTC | **Approfondir seulement si ETH et SOL sont ajoutés à l'enregistreur de Dublin** (ton accord nécessaire) |

**Conclusion générale.** Tout ce que nous avons testé aujourd'hui sur le BTC (carnets, flux, liquidité, perp, retraits) est soit déjà dans les mesures simples, soit déjà dans le prix Polymarket au moment où l'on peut acheter. Le marché Polymarket 5 minutes est efficace à notre échelle de latence.

Les seules pistes encore ouvertes :
- une **information externe plus rapide** : ETH et SOL à Dublin, Deribit ;
- une **latence nettement plus faible** ;
- le **verdict du 14.10** sur H816 et H821, avec la période réservée.

Fichiers :
- https://github.com/pitch6767/wallet-autopsy/blob/main/etude/bot5min/resultat_flux_h977.md
- https://github.com/pitch6767/wallet-autopsy/blob/main/etude/bot5min/flux_h977.py
