# Bot95 — H971 / H972 : pression contre capacité, effondrement de la liquidité — rapport du 12.10.2026

**Cadre**
- Étude hors ligne uniquement. Aucun ordre réel.
- Aucun bot ni fantôme modifié ; H816, H821 et R4 sont inchangés. La période réservée n'a pas été lue.
- Protocole et code enregistrés sur GitHub avant le calcul du test (commit 2242e2a).

**Données et découpage**
- Laboratoire de Dublin : carnet Binance toutes les 100 ms, transactions agressives Binance et Bybit, Chainlink, carnet Polymarket.
- Apprentissage, puis validation, puis **test inédit** (12.10 à partir de 06:00 UTC).

**Mesures**
- **Pression nette** : achats agressifs moins ventes agressives.
- **Capacité** : profondeur d'en face à 20 $, plus les ajouts d'offres.
- **Indice pression / capacité** : rapport des deux, en BTC, puis normalisé (z-score sur les 10 dernières minutes). Ce n'est pas un ratio brut.
- **Rechargement** : ajouts d'offres comparés à leur niveau habituel.
- **Retraits** : baisses de profondeur non expliquées par les transactions.

## Réponse courte

**Rapporter la pression à la capacité n'apporte rien** de plus que les mesures simples : OFI, momentum et volatilité. **L'effondrement de capacité** (H972) annonce bien un petit mouvement du BTC, mais **pas mieux qu'un simple flux agressif fort**. Il ne se traduit ni en réévaluation Polymarket, ni en règlement, ni en profit exécutable.

## 1. H972 — Effondrement de capacité

**Définition** (version haussière, la baissière est symétrique). Les cinq conditions doivent être réunies :
- forte pression nette ;
- profondeur d'en face en baisse de plus de 30 % en 5 s ;
- rechargement divisé par deux ou plus ;
- microprix du bon côté ;
- spot qui n'a pas encore bougé.

Le **témoin** est la forte pression seule, sans les autres conditions.

Mouvement BTC dans le sens prévu, en $, IC 90 % par cycles :

| Échantillon | Type | Événements | 1 s | 5 s | 10 s | 30 s | 60 s |
|---|---|---|---|---|---|---|---|
| Validation | effondrement | 13 | +1,6 | +1,8 | −0,4 | −6,9 | −15,3 |
| Validation | témoin | 304 | +2,3 | +4,5 | **+5,6 [+4,4 ; +6,9]** | +7,6 | +6,1 |
| Test | effondrement | 21 | +2,1 | +3,1 | **+4,7 [+1,3 ; +8,6]** | +3,0 | +1,4 |
| Test | témoin | 305 | +2,3 | +3,6 | **+4,4 [+3,2 ; +5,6]** | +4,3 | +3,4 |

- L'effondrement est **rare** : 13 et 21 événements. Il ne fait **pas mieux que le témoin**, et sur la validation il se retourne même après 10 s.
- Le flux agressif fort seul suffit à prévoir 4 à 6 $ de continuation. Cela confirme H833.

**Polymarket et règlement**
- Le jeton prévu monte de 1 à 2 c dans les secondes qui suivent le flux fort. Après un effondrement, rien de mesurable.
- Effet sur le règlement officiel : effondrement 0,00 ; témoin +0,06 [+0,02 ; +0,10] sur le test.

**Occasion exécutable** (test) : achat de 20 $ du jeton prévu à 164 ms, au prix vu.

| Type | Achats | Revente à 30 s | Conservation jusqu'au règlement |
|---|---|---|---|
| Effondrement | 7 | −44 $ | −85 $ [−140 ; −30] |
| Témoin | 117 | −167 $ [−311 ; −11] | −591 $ [−902 ; −289] |

**Ce n'est pas exploitable.** Le mouvement de 1 à 2 c est plus petit que l'écart achat-vente plus les frais, et le marché l'a déjà intégré quand l'ordre arrive.

## 2. H971 — Prévision : pression/capacité contre OFI + momentum + volatilité

| Cible | Échantillon | AUC simple | AUC + pression/capacité | ΔAUC (IC corrigé) |
|---|---|---|---|---|
| Hausse BTC à 10 s | validation | 0,668 | 0,673 | +0,005 [−0,001 ; +0,011] |
| Hausse BTC à 10 s | test | 0,657 | 0,662 | +0,004 [−0,004 ; +0,011] |
| Hausse BTC à 30 s | test | 0,617 | 0,613 | −0,005 |
| Grand mouvement vers le haut à 30 s | test | 0,639 | 0,627 | −0,012 |
| Grand mouvement vers le bas à 30 s | test | 0,611 | 0,617 | +0,007 |
| Polymarket +1 c à 10 s | test | 0,566 | 0,558 | −0,008 |

**Aucun gain.** Le modèle simple capte déjà l'information de court terme. Le gain du carnet mesuré dans H834 (+0,085) venait de l'OFI et du microprix, qui sont déjà dans le modèle simple ici.

## 3. Règlement officiel : modèle de règlement seul contre + pression/capacité

| Échantillon | Décisions | Brier, règlement seul | Brier, + pression/capacité | ΔBrier (IC corrigé) |
|---|---|---|---|---|
| Validation, toutes | 492 | 0,1150 | 0,1262 | −0,011 [−0,024 ; +0,000] |
| Test, toutes | 252 | **0,0805** | 0,0914 | −0,011 [−0,024 ; +0,001] |
| Test, proches de 50 % | 35 | 0,2397 | 0,2385 | +0,001 [−0,054 ; +0,061] |
| Test, marge faible | 45 | 0,2425 | 0,2606 | −0,018 |

Ajouter la pression/capacité **dégrade** légèrement la probabilité de règlement. C'est du sur-apprentissage.

## 4. Verdict

| Famille | Décision |
|---|---|
| H971 Pression contre capacité (indice normalisé) | **Abandonner** : aucun gain sur les mesures simples, ni à court terme, ni sur le règlement |
| H972 Effondrement de capacité | **Abandonner** : rare, pas mieux que le flux seul, non exécutable |
| Flux agressif fort (témoin) | Continuation de 4 à 6 $ sur 10 s confirmée, mais **non exécutable** sur Polymarket après écart, frais et latence |

**La leçon.** L'information de carnet et de flux existe, mais elle vit 10 à 30 secondes, porte sur quelques dollars de BTC, et Polymarket l'intègre plus vite que nous ne pouvons acheter.

**Prochaines priorités** de ton programme F1 :
- fatigue de l'absorption et transition vers la cassure (H933/H954) ;
- passage du perp au spot et retraits synchronisés (H937/H956) ;
- traduction d'un mouvement BTC en règlement Chainlink (H941) ;
- avance réellement exploitable après latence (H965/H969).

Elles reposent largement sur les mêmes mesures, que H833 et H835 ont en partie déjà couvertes.

Fichiers :
- https://github.com/pitch6767/wallet-autopsy/blob/main/etude/bot5min/resultat_pression_h971.md
- https://github.com/pitch6767/wallet-autopsy/blob/main/etude/bot5min/pression_h971.py
