# Bot95 — F1 priorités 2 à 5 : fatigue de l'absorption, perp → spot, retraits synchronisés, règlement, avance exploitable — rapport du 12.10.2026

**Cadre**
- Étude hors ligne uniquement. Aucun ordre réel.
- Aucun bot ni fantôme modifié ; H816, H821 et R4 sont inchangés. La période réservée n'a pas été lue.
- Protocole figé avant le calcul du test (commit 288a30c).

**Données**
- Laboratoire de Dublin, avec les heures de **réception** des messages.
- Découpage : apprentissage, validation, puis **test inédit** (12.10 à partir de 06:00 UTC).
- IC 90 % calculés par cycle.

## Réponse courte

- **La fatigue de l'absorption et la transition vers la cassure** (H933/H954) : **non démontrées**.
- **Le perp Bybit mène bien le spot et Polymarket**. Mais Polymarket se réévalue en 250 ms environ : **après nos 164 ms, il ne reste qu'environ 86 ms** d'avance. Le profit exécutable n'est **pas démontré** (H937/H965/H969).
- **Un flux fort au début du cycle déplace le règlement officiel** plus que ne le prévoit le modèle (H941). C'est cohérent avec H833.
- **Retraits synchronisés** (H956) : signal **fort et stable**, mais **dans le sens inverse** de l'hypothèse.

## 1. H933 — Fatigue de l'absorption

Une vague = une forte pression agressive. Le rang compte les vagues de même sens dans les 60 s précédentes. L'efficacité mesure le mouvement du prix en $ par BTC de pression nette.

| Échantillon | Rang | Vagues | Absorbées | Efficacité ($/BTC) | Mouvement à 10 s |
|---|---|---|---|---|---|
| Apprentissage | 1re / 2e / 3e et plus | 268 / 143 / 131 | 47 / 48 / 48 % | 0,76 / 0,66 / 1,00 | +4,4 / +4,0 / +4,0 $ |
| Validation | 1re / 2e / 3e et plus | 178 / 105 / 86 | 44 / 38 / 35 % | 0,72 / 0,93 / 0,86 | +6,0 / +3,7 / +7,7 $ |
| Test | 1re / 2e / 3e et plus | 180 / 114 / 93 | 48 / 42 / 35 % | 0,53 / 0,70 / 0,99 | +4,6 / +5,4 / +3,4 $ |

**Lecture.** Sur la validation et le test, l'absorption s'affaiblit un peu au fil des vagues (moins de vagues absorbées, plus d'efficacité). Ce n'est pas le cas sur l'apprentissage, et le mouvement à 10 s n'augmente pas avec le rang. **Non démontré.**

## 2. H954 — Après une absorption, la vague suivante casse-t-elle plus souvent ?

Une cassure = mouvement de plus de 1,5 σ en 30 s dans le sens de la vague.

| Échantillon | 1re vague | Vague après absorption | Écart |
|---|---|---|---|
| Validation | 26 % | 27 % | +0,5 pt [−6,9 ; +8,3] |
| Test | 23 % | 20 % | −3,2 pts [−9,6 ; +4,1] |

**Rejeté** : l'absorption n'annonce pas de cassure.

## 3. H941 — Un mouvement BTC déplace-t-il assez la probabilité de règlement ?

| Échantillon | Temps restant | Vagues | Déplacement de la probabilité en 10 s | Déplacement > 0,03 | Résultat officiel − probabilité au départ |
|---|---|---|---|---|---|
| Test | 30–89 s | 66 | +0,00 | 8 % | +0,01 |
| Test | 90–149 s | 67 | +0,04 | 21 % | +0,03 |
| Test | 150–240 s | 117 | +0,05 | 42 % | **+0,10 [+0,04 ; +0,17]** |
| Validation | 150–240 s | 104 | +0,07 | 47 % | +0,09 [−0,01 ; +0,19] |
| Apprentissage | 150–240 s | 120 | +0,08 | 51 % | +0,18 [+0,12 ; +0,25] |

**Lecture**
- Plus le flux arrive tôt dans le cycle, plus son effet sur le règlement est fort.
- Un flux fort entre 150 et 240 s avant la fin déplace la probabilité de 0,05 à 0,08 en 10 s. Le résultat officiel va ensuite **encore plus loin** dans ce sens que ne le prévoit le modèle : +0,10 sur le test.
- C'est l'effet de continuation déjà vu dans H833. **Il reste à savoir si Polymarket l'intègre déjà dans son prix.**

## 4. H937 / H965 / H969 — Chocs du perp Bybit (≥ 3 écarts-types en 500 ms, spot encore immobile)

| Échantillon | Chocs | Part du choc reproduite par le spot à 100 / 250 / 500 / 1 000 / 2 000 ms | Polymarket +1 c | Délai médian de Polymarket | Avance restante après 164 ms |
|---|---|---|---|---|---|
| Validation | 819 | 0,19 / 0,28 / 0,38 / 0,46 / 0,64 | 79 % | 250 ms | 86 ms |
| Test | 672 | 0,15 / 0,25 / 0,31 / 0,39 / 0,48 | 73 % | 250 ms | 86 ms |

**Lecture**
- Le perp mène : le spot reproduit 40 à 65 % du choc en 1 à 2 s.
- **Polymarket réagit presque aussi vite** : 3 fois sur 4, le jeton bouge d'au moins 1 c dans les 250 ms.

**H969 — achat de 20 $ du jeton dans le sens du choc, à 164 ms, au prix vu, frais compris :**

| Échantillon | Revente à 10 s | Revente à 30 s | Conservation jusqu'au règlement |
|---|---|---|---|
| Apprentissage | +678 $ [+4 ; +1 400] | +763 $ [+50 ; +1 548] | −31 $ |
| Validation | −111 $ [−257 ; +36] | +90 $ [−149 ; +352] | **−1 395 $** |
| Test | +96 $ [−91 ; +326] | +57 $ [−107 ; +225] | −163 $ |

**Non démontré.** C'est positif sur l'apprentissage, mais pas sur la validation, et l'IC du test contient zéro. Garder la position jusqu'au règlement perd de l'argent. L'avance est réelle mais minuscule (environ 86 ms) : il faudrait une latence bien inférieure à 164 ms.

## 5. H956 — Retraits synchronisés Binance spot / Bybit perp

Un retrait = une baisse de profondeur non expliquée par les transactions, au-dessus du 95e centile. L'hypothèse : un retrait d'offres vendeuses annonce une hausse.

| Échantillon | Type | Secondes | 5 s | 10 s | 30 s |
|---|---|---|---|---|---|
| Test | synchronisé | 1 698 | **−3,0 $** | **−4,0 $** | **−4,6 $** |
| Test | Binance seul | 2 337 | −1,4 $ | −2,0 $ | −2,2 $ |
| Test | Bybit seul | 2 210 | −0,1 $ | +0,0 $ | −0,0 $ |

Tous les IC du synchronisé excluent zéro, sur l'apprentissage, la validation et le test.

**Lecture : c'est l'inverse de l'hypothèse.** Quand les offres vendeuses disparaissent en même temps sur les deux places, le prix **baisse**. L'explication la plus probable : ce ne sont pas des retraits, mais des vendeurs qui **déplacent leurs offres plus bas**. Ils annulent puis reposent moins cher, et cela précède la baisse.

Le signal est fort et stable. Mais son **apport en plus de l'OFI et du momentum n'a pas été testé** : H971 suggère qu'il pourrait déjà y être.

## 6. Verdict

| Famille | Décision |
|---|---|
| H933 Fatigue de l'absorption | **Non démontré** (pas stable sur l'apprentissage) |
| H954 Absorption → cassure | **Abandonner** |
| H937 Perp → spot | **Démontré** (le perp mène le spot de 0,1 à 2 s) |
| H965 Avance après latence | Environ **86 ms** restantes face à Polymarket : **insuffisant à 164 ms** |
| H969 Alpha exécutable sur les chocs du perp | **Non démontré** (validation négative) |
| H941 Flux → règlement | **Effet réel en début de cycle** (+0,10 sur le test) : à confronter au prix Polymarket |
| H956 Retraits synchronisés | **Signal fort, sens inverse** : à approfondir en apport marginal, sans conclusion économique |

**Où on en est.** Le marché BTC transmet bien l'information, mais Polymarket la reprend en environ 250 ms. Il y a deux pistes :
- **réduire la latence**, car une exécution sous 100 ms changerait H969 ;
- **chercher l'information là où Polymarket ne la reprend pas** : l'effet du flux sur le règlement en début de cycle (H941) est la piste la plus prometteuse.

Fichiers :
- https://github.com/pitch6767/wallet-autopsy/blob/main/etude/bot5min/resultat_transmission_h933.md
- https://github.com/pitch6767/wallet-autopsy/blob/main/etude/bot5min/transmission_h933.py
