# HEDGE PRICE PREDICTOR — peut-on acheter le côté opposé moins cher dans les secondes qui suivent ?

Étude hors ligne du 11.10.2026 — aucun bot, aucun fichier du bot modifié. 1146 cycles BTC 5 min réglés (07.10 08:00 → 11.10 07:55, heure suisse). Apprentissage 455 cycles (< 08.10 22:00) · validation 433 (→ 10.10 10:25) · test inédit 258 cycles (après 10.10 10:25) — environ 22 h de marché, plus court que la validation.

## Verdict (honnête, en tête)

- **Prévisibilité : faible là où elle servirait.** Sur toutes les décisions, le modèle logistique (figé sur l'apprentissage) fait mieux que le taux naïf : baisse ≥ 1 c en 1 s, AUC 0,72 (Brier 0,096 contre 0,102) ; en 3 s, AUC 0,72. Mais cet avantage vient surtout des carnets « morts » (rien ne bouge) : limité aux moments vivants (vendeur opposé 0,10-0,90, > 30 s restantes) l'AUC tombe à 0,59 (1 s) et 0,54 (3 s), et sur les photos 100 ms autour des désaccords à 0,57 (1 s, 5168 décisions). La probabilité est mal calibrée aux extrêmes (voir section 2).
- **Attendre pour acheter l'opposé moins cher ne paie pas.** Après le déclencheur « modèle −10 », toutes les variantes d'attente (ordres −1/−2/−3 c sinon immédiat, attente prédictive ; 0,25 à 10 s) paient en moyenne entre −2,36 et 0,06 c de moins que l'achat immédiat (négatif = plus cher) sur la validation : le côté opposé a tendance à **monter** juste après ce déclencheur. Sur les 96 combinaisons testées contre (b), 12 ont un Δ P&L dont l'IC 90 % validation est entièrement positif (5 restent positives sur le test) ; mais le prix payé n'explique que +2 672 $ sur +18 674 $ de ces gains : le reste vient de positions **laissées non couvertes** (cycle terminé pendant l'attente, quantités différentes) qui ont ensuite gagné — du hasard de résultat, pas un achat moins cher. 4 combinaisons sont entièrement négatives.
- **Seule piste où le prix payé est meilleur en validation (> 100 $ d'effet prix) et pas pire sur le test** : entrée + 30 s, délai 0 s, 5 s, attente prédictive — validation 0,27 c par paire (effet prix +618 $), test −0,06 c (effet prix +139 $) ; entrée + 30 s, délai 0,3 s, 5 s, attente prédictive — validation 0,19 c par paire (effet prix +429 $), test −0,09 c (effet prix +264 $). Quelques dixièmes de cent par paire au mieux ; sur le test l'effet prix pondéré par les parts reste un peu positif mais la moyenne par paire est négative : signal trop faible et non confirmé, à revoir seulement avec des données plus fines.
- **Le délai d'exécution coûte** : avec 0,3 s de retard, la couverture immédiate paie en moyenne 1,34 c de plus que le prix vu au déclencheur « modèle −10 » (validation : le prix monte juste après ce déclencheur), contre −0,10 c au déclencheur « entrée + 30 s » (moment neutre).
- **Couvrir contre garder (modèle −10)** : couverture immédiate −1 792 $ sur la validation [IC 90 % −4 782 $ ; +601 $], −139 $ sur le test ; 10 jackpots (≥ 4× la mise) sacrifiés sur la validation, gains sacrifiés +4 500 $. Vendre la moitié : −960 $ [−2 598 $ ; +441 $]. Rien de démontré : la couverture change la forme du risque, pas l'espérance.
- **Couvrir contre garder (entrée + 30 s)** : couverture immédiate −4 334 $ sur la validation [IC 90 % −10 541 $ ; +1 081 $], +82 $ sur le test ; 51 jackpots (≥ 4× la mise) sacrifiés sur la validation, gains sacrifiés +17 253 $. Vendre la moitié : −2 322 $ [−5 502 $ ; +664 $]. Rien de démontré : la couverture change la forme du risque, pas l'espérance.
- **Coût Up + Down** : une paire couverte coûte en médiane 1,10 au déclencheur « modèle −10 » (seulement 3,5 % des 401 paires < 1) et 1,03 à « entrée + 30 s » (35,9 % des 912 paires < 1) : on « verrouille » surtout des pertes (section 5).
- **Conclusion** : avec les données actuelles (meilleur niveau seulement, 0,3 s), il n'existe pas de prédicteur de prix de couverture exploitable ; la règle la plus simple — couvrir tout de suite, ou ne pas couvrir — n'est battue par aucune attente de façon confirmée. Ce que le VPS de Dublin devrait enregistrer pour trancher est en section 6.

## Définitions (pré-enregistrées avant tout calcul)

**Positions** (premier signal du cycle, achat au seul meilleur vendeur de la ligne enregistrée, quantité affichée, 50 $ max, frais 0,072·p·(1−p) par part) :

- **désaccord 20** : premier instant où proba du modèle du bot (r[2]) − vendeur ≥ 0,20, vendeur 0,02-0,98, ≥ 5 s restantes.
- **V2-F original** : écart ≥ 0,20 qui a grandi d'au moins 3 c en 3 s, vendeur 0,03-0,97 (définition O8 inchangée).
- **désaccord 30** : premier écart ≥ 0,30, vendeur 0,02-0,98.
- **V1 (0,55-0,56)** : copie de la règle V1 du bot (bot95/src/index.js, `v1Eval`) : meilleur vendeur entre 0,55 et 0,56, modèle de notre côté ≥ 0,63 (PMIN + MARGE), élan du perp Bybit sur 5 s dans notre sens. Différence : le bot exige 50 $ remplis jusqu'à 0,56 sur plusieurs niveaux ; ici seul le meilleur niveau est connu → quantité affichée.

| Stratégie | Positions app. | valid. | test |
|---|---|---|---|
| désaccord 20 | 348 | 385 | 258 |
| V2-F original | 339 | 379 | 258 |
| désaccord 30 | 219 | 283 | 246 |
| V1 (0,55-0,56) | 12 | 9 | 2 |

Les quatre stratégies achètent souvent le même cycle (désaccord 20 et V2-F surtout) : elles sont traitées comme quatre portefeuilles fantômes séparés et leurs résultats sont **additionnés** dans les tableaux.

**Déclencheurs de la couverture** (un seul moment par position) :

- **modèle −10** : première ligne après l'entrée où la proba du modèle de notre côté est ≥ 10 points sous celle de l'entrée (comme la « sortie modèle −10 »), au moins 2 s avant la fin.
- **entrée + 30 s** : première ligne à l'entrée + 30 s ou après (au moins 2 s avant la fin).
- Position sans déclencheur : aucune action, résultat = garder. **Toutes les positions comptent dans tous les totaux**, déclenchées ou non.

**Politiques**, même budget pour toutes : au plus autant de parts opposées que de parts détenues (couverture « verrouillée »), au seul meilleur vendeur, quantité affichée :

- (a) garder sans couvrir.
- (b) couverture immédiate au meilleur vendeur opposé (quantité affichée ; le reste n'est pas couvert, faute de profondeur connue).
- (c) ordre passif à vendeur opposé − k c (k = 1, 2, 3), valable H secondes. **Hypothèse : nous sommes derniers dans la file d'attente** ; l'ordre n'est rempli que si le meilleur vendeur enregistré descend **au moins 1 c sous notre prix** (≤ limite − 0,01) sur une ligne, pour la quantité affichée de cette ligne. Les frais preneur sont comptés aussi sur l'ordre passif (prudent : Polymarket ne fait pas payer le teneur d'ordre). Non rempli → deux variantes : achat immédiat au vendeur à la fin de l'attente, ou rien.
- (d) attente prédictive : si le modèle « baisse ≥ 1 c dans H » donne une probabilité > seuil, on attend H puis on achète au meilleur vendeur du moment (même s'il a monté) ; sinon achat immédiat. Seuil choisi sur l'apprentissage seulement (celui qui maximise la baisse moyenne obtenue sur toutes les positions déclenchées).
- (e) vente immédiate de la moitié de la position au meilleur acheteur de notre côté (quantité affichée), frais compris.
- Délai d'exécution : 0 s (principal) et 0,3 s (variante : l'ordre part sur la première ligne ≥ décision + 0,3 s).

**Remarque de structure importante** : sur Polymarket, le carnet Down est le miroir du carnet Up (vendeur Down = 1 − acheteur Up : vérifié, les colonnes manquantes coïncident exactement). Acheter le côté opposé au prix o revient donc à revendre notre côté à 1 − o, frais identiques (0,072·p·(1−p) est symétrique). La « couverture immédiate » (b) a le même effet économique qu'une **vente** de la position au meilleur acheteur — mais elle immobilise du capital jusqu'au règlement.

## 1. Ce que montre le carnet opposé après une entrée (taux bruts)

198525 instants de décision (une par seconde après chaque entrée, jusqu'à la fin du cycle ; dédoublonnés quand deux stratégies tiennent le même côté du même cycle à la même seconde). Seul le **meilleur niveau** du carnet est enregistré (prix + taille) : la profondeur au-delà n'existe pas dans les lignes.

- apprentissage : 60950 décisions · vendeur opposé médian 0,89 · taille affichée médiane 392 parts (10 % des cas < 40 parts)
- validation : 73847 décisions · vendeur opposé médian 0,91 · taille affichée médiane 352 parts (10 % des cas < 40 parts)
- inédit : 63728 décisions · vendeur opposé médian 0,89 · taille affichée médiane 243 parts (10 % des cas < 25 parts)

Fréquence observée (apprentissage + validation + test) de « le meilleur vendeur opposé descend d'au moins X c dans les H secondes » et « il est plus cher au bout de H » :

| Horizon | n | ≥ 1 c | ≥ 2 c | ≥ 3 c | ≥ 5 c | ≥ 10 c | plus cher à H |
|---|---|---|---|---|---|---|---|
| 0,25 s | 198525 | 3,8 % | 1,8 % | 1,0 % | 0,5 % | 0,1 % | 4,7 % |
| 0,5 s | 198229 | 7,9 % | 4,1 % | 2,5 % | 1,2 % | 0,4 % | 9,8 % |
| 1 s | 197560 | 12,6 % | 7,2 % | 4,7 % | 2,5 % | 0,8 % | 15,2 % |
| 3 s | 195396 | 23,0 % | 15,5 % | 11,3 % | 6,8 % | 2,8 % | 26,0 % |
| 5 s | 193232 | 28,6 % | 20,6 % | 15,8 % | 10,2 % | 4,6 % | 30,7 % |
| 10 s | 187822 | 36,3 % | 28,2 % | 23,0 % | 16,4 % | 8,7 % | 36,3 % |

Les lignes arrivent toutes les ~0,3 s : l'horizon 0,25 s contient 0 ou 1 nouvelle ligne (fenêtre sans ligne = « pas de baisse observée »), l'horizon 0,5 s une ou deux. Ces deux horizons ne sont mesurés qu'**approximativement** ; voir le contrôle à 100 ms (section 3).

## 2. Prédire la baisse du côté opposé — régression logistique figée sur l'apprentissage

Une régression logistique par horizon et par seuil (30 modèles) + une par horizon pour « plus cher à H » (6), ajustées sur l'apprentissage SEULEMENT, variables centrées-réduites sur l'apprentissage, aucune variable choisie après coup. 19 variables, toutes connues à la décision (lignes d'horodatage ≤ instant de décision) : temps restant, vendeur opposé, log taille opposée, vendeur de notre côté, proba modèle notre côté, variation vendeur opposé 1 s, variation vendeur opposé 3 s, Bybit 1 s, OKX 1 s, Coinbase 1 s, Binance 1 s, Chainlink 1 s, Bybit 3 s, OKX 3 s, Coinbase 3 s, Binance 3 s, Chainlink 3 s, écart vendeur-acheteur, distance au prix d'exercice (Chainlink), distance au prix d'exercice (perp). Mouvements des bourses comptés positivement quand ils vont dans notre sens (donc vers un côté opposé moins cher).

« Brier naïf » = prédire toujours le taux de l'apprentissage. Le modèle n'apporte quelque chose que si son Brier est **plus bas** que le naïf et son AUC nettement > 0,5. Les instants d'une même position se suivent seconde par seconde : ils ne sont pas indépendants, les AUC sont donc plus précises en apparence qu'en réalité.

### Horizons < 1 s (mesure approximative, cadence 0,3 s)

| Horizon | Cible | Taux app. | Valid. : n · taux · AUC · Brier modèle / naïf | Test : n · taux · AUC · Brier modèle / naïf |
|---|---|---|---|---|
| 0,25 s | baisse ≥ 1 c | 4,2 % | 73847 · 3,3 % · 0,74 · 0,031 / 0,032 | 63728 · 4,0 % · 0,72 · 0,037 / 0,039 |
| 0,25 s | baisse ≥ 2 c | 2,0 % | 73847 · 1,5 % · 0,74 · 0,014 / 0,015 | 63728 · 1,9 % · 0,71 · 0,018 / 0,018 |
| 0,25 s | baisse ≥ 3 c | 1,2 % | 73847 · 0,9 % · 0,75 · 0,009 / 0,009 | 63728 · 1,0 % · 0,69 · 0,010 / 0,010 |
| 0,25 s | baisse ≥ 5 c | 0,5 % | 73847 · 0,4 % · 0,75 · 0,004 / 0,004 | 63728 · 0,4 % · 0,71 · 0,004 / 0,004 |
| 0,25 s | baisse ≥ 10 c | 0,1 % | 73847 · 0,1 % · 0,78 · 0,001 / 0,001 | 63728 · 0,1 % · 0,73 · 0,002 / 0,001 |
| 0,25 s | plus cher à H | 4,9 % | 73847 · 4,4 % · 0,83 · 0,039 / 0,042 | 63728 · 4,8 % · 0,82 · 0,042 / 0,045 |
| 0,5 s | baisse ≥ 1 c | 8,5 % | 73734 · 7,2 % · 0,73 · 0,063 / 0,067 | 63653 · 8,3 % · 0,71 · 0,072 / 0,076 |
| 0,5 s | baisse ≥ 2 c | 4,5 % | 73734 · 3,6 % · 0,73 · 0,033 / 0,035 | 63653 · 4,3 % · 0,72 · 0,039 / 0,041 |
| 0,5 s | baisse ≥ 3 c | 2,8 % | 73734 · 2,2 % · 0,74 · 0,020 / 0,021 | 63653 · 2,5 % · 0,70 · 0,024 / 0,025 |
| 0,5 s | baisse ≥ 5 c | 1,4 % | 73734 · 1,1 % · 0,74 · 0,010 / 0,011 | 63653 · 1,1 % · 0,72 · 0,011 / 0,011 |
| 0,5 s | baisse ≥ 10 c | 0,4 % | 73734 · 0,4 % · 0,71 · 0,003 / 0,004 | 63653 · 0,4 % · 0,73 · 0,004 / 0,004 |
| 0,5 s | plus cher à H | 10,0 % | 73734 · 9,3 % · 0,80 · 0,074 / 0,085 | 63653 · 10,0 % · 0,80 · 0,080 / 0,090 |

### Horizons 1-10 s

| Horizon | Cible | Taux app. | Valid. : n · taux · AUC · Brier modèle / naïf | Test : n · taux · AUC · Brier modèle / naïf |
|---|---|---|---|---|
| 1 s | baisse ≥ 1 c | 13,2 % | 73471 · 11,6 % · 0,72 · 0,096 / 0,102 | 63464 · 13,1 % · 0,70 · 0,107 / 0,114 |
| 1 s | baisse ≥ 2 c | 7,8 % | 73471 · 6,5 % · 0,71 · 0,058 / 0,061 | 63464 · 7,4 % · 0,70 · 0,066 / 0,069 |
| 1 s | baisse ≥ 3 c | 5,4 % | 73471 · 4,2 % · 0,72 · 0,038 / 0,040 | 63464 · 4,7 % · 0,70 · 0,043 / 0,045 |
| 1 s | baisse ≥ 5 c | 2,9 % | 73471 · 2,3 % · 0,72 · 0,022 / 0,022 | 63464 · 2,3 % · 0,71 · 0,021 / 0,022 |
| 1 s | baisse ≥ 10 c | 0,9 % | 73471 · 0,8 % · 0,70 · 0,008 / 0,008 | 63464 · 0,8 % · 0,68 · 0,007 / 0,008 |
| 1 s | plus cher à H | 15,2 % | 73471 · 15,0 % · 0,78 · 0,110 / 0,127 | 63464 · 15,6 % · 0,77 · 0,117 / 0,132 |
| 3 s | baisse ≥ 1 c | 23,3 % | 72637 · 21,7 % · 0,72 · 0,155 / 0,170 | 62880 · 24,3 % · 0,70 · 0,169 / 0,184 |
| 3 s | baisse ≥ 2 c | 16,4 % | 72637 · 14,5 % · 0,71 · 0,117 / 0,125 | 62880 · 15,9 % · 0,70 · 0,126 / 0,133 |
| 3 s | baisse ≥ 3 c | 12,6 % | 72637 · 10,4 % · 0,70 · 0,089 / 0,094 | 62880 · 11,1 % · 0,70 · 0,094 / 0,099 |
| 3 s | baisse ≥ 5 c | 7,9 % | 72637 · 6,4 % · 0,70 · 0,058 / 0,060 | 62880 · 6,2 % · 0,70 · 0,056 / 0,058 |
| 3 s | baisse ≥ 10 c | 3,2 % | 72637 · 2,7 % · 0,68 · 0,025 / 0,026 | 62880 · 2,4 % · 0,68 · 0,023 / 0,024 |
| 3 s | plus cher à H | 24,1 % | 72637 · 26,3 % · 0,74 · 0,169 / 0,194 | 62880 · 27,4 % · 0,73 · 0,175 / 0,200 |
| 5 s | baisse ≥ 1 c | 28,3 % | 71803 · 27,3 % · 0,72 · 0,178 / 0,198 | 62296 · 30,5 % · 0,71 · 0,190 / 0,213 |
| 5 s | baisse ≥ 2 c | 21,4 % | 71803 · 19,6 % · 0,71 · 0,146 / 0,158 | 62296 · 21,0 % · 0,70 · 0,154 / 0,166 |
| 5 s | baisse ≥ 3 c | 17,3 % | 71803 · 14,9 % · 0,70 · 0,120 / 0,127 | 62296 · 15,4 % · 0,70 · 0,124 / 0,131 |
| 5 s | baisse ≥ 5 c | 11,8 % | 71803 · 9,8 % · 0,69 · 0,085 / 0,089 | 62296 · 9,3 % · 0,69 · 0,082 / 0,085 |
| 5 s | baisse ≥ 10 c | 5,5 % | 71803 · 4,4 % · 0,67 · 0,041 / 0,042 | 62296 · 4,0 % · 0,67 · 0,038 / 0,039 |
| 5 s | plus cher à H | 27,7 % | 71803 · 31,3 % · 0,74 · 0,188 / 0,216 | 62296 · 32,9 % · 0,72 · 0,193 / 0,223 |
| 10 s | baisse ≥ 1 c | 35,2 % | 69718 · 34,9 % · 0,73 · 0,198 / 0,227 | 60836 · 38,9 % · 0,72 · 0,206 / 0,239 |
| 10 s | baisse ≥ 2 c | 28,6 % | 69718 · 27,4 % · 0,72 · 0,179 / 0,199 | 60836 · 28,9 % · 0,71 · 0,185 / 0,205 |
| 10 s | baisse ≥ 3 c | 24,3 % | 69718 · 22,2 % · 0,71 · 0,160 / 0,173 | 60836 · 22,7 % · 0,70 · 0,163 / 0,176 |
| 10 s | baisse ≥ 5 c | 18,1 % | 69718 · 16,1 % · 0,69 · 0,128 / 0,135 | 60836 · 15,1 % · 0,69 · 0,123 / 0,129 |
| 10 s | baisse ≥ 10 c | 10,0 % | 69718 · 8,4 % · 0,67 · 0,075 / 0,077 | 60836 · 7,6 % · 0,66 · 0,069 / 0,071 |
| 10 s | plus cher à H | 31,8 % | 69718 · 37,0 % · 0,73 · 0,203 / 0,236 | 60836 · 39,9 % · 0,72 · 0,209 / 0,246 |

### Le modèle sur les seuls moments « vivants »

Une grande partie des décisions tombe dans des carnets morts (côté opposé à 0,95-0,99 ou presque plus de temps) où rien ne bouge : facile à prédire, mais inutile pour couvrir. Même évaluation limitée aux instants où le vendeur opposé est entre 0,10 et 0,90 et où il reste plus de 30 s :

| Horizon | Valid. : n · taux baisse ≥ 1 c · AUC · Brier modèle / naïf | Test : n · taux · AUC · Brier modèle / naïf |
|---|---|---|
| 0,25 s | 30442 · 6,2 % · 0,66 · 0,056 / 0,058 | 28930 · 7,0 % · 0,66 · 0,064 / 0,066 |
| 0,5 s | 30442 · 13,0 % · 0,62 · 0,110 / 0,115 | 28930 · 14,3 % · 0,62 · 0,119 / 0,126 |
| 1 s | 30442 · 20,6 % · 0,59 · 0,162 / 0,169 | 28930 · 22,1 % · 0,58 · 0,171 / 0,180 |
| 3 s | 30442 · 37,0 % · 0,54 · 0,242 / 0,252 | 28930 · 39,0 % · 0,53 · 0,247 / 0,263 |
| 5 s | 30442 · 45,2 % · 0,53 · 0,263 / 0,276 | 28930 · 47,6 % · 0,52 · 0,264 / 0,287 |
| 10 s | 30442 · 54,9 % · 0,52 · 0,268 / 0,286 | 28930 · 58,0 % · 0,52 · 0,263 / 0,295 |

Attention : le Brier « naïf » de ce tableau reste le taux global de l'apprentissage (plus bas que le taux de ces moments vivants), ce qui avantage le modèle ; l'AUC est la mesure à lire ici.

### Calibration sur la validation (baisse ≥ 1 c)

Horizon 1 s :

| Prédit (tranche) | n | Prédit moyen | Observé |
|---|---|---|---|
| 0,00-0,05 | 7347 | 3,8 % | 0,9 % |
| 0,05-0,06 | 7347 | 5,1 % | 1,2 % |
| 0,06-0,07 | 7347 | 6,2 % | 3,5 % |
| 0,07-0,08 | 7347 | 7,5 % | 7,4 % |
| 0,08-0,10 | 7347 | 9,0 % | 11,1 % |
| 0,10-0,12 | 7347 | 10,7 % | 13,8 % |
| 0,12-0,14 | 7347 | 13,0 % | 16,2 % |
| 0,14-0,18 | 7347 | 15,8 % | 17,2 % |
| 0,18-0,22 | 7347 | 19,8 % | 19,0 % |
| 0,22-1,00 | 7348 | 29,1 % | 25,2 % |

Horizon 3 s :

| Prédit (tranche) | n | Prédit moyen | Observé |
|---|---|---|---|
| 0,00-0,08 | 7264 | 7,3 % | 0,7 % |
| 0,08-0,10 | 7264 | 9,3 % | 1,8 % |
| 0,10-0,13 | 7263 | 11,3 % | 7,5 % |
| 0,13-0,15 | 7264 | 14,0 % | 17,3 % |
| 0,15-0,19 | 7263 | 17,3 % | 25,2 % |
| 0,19-0,23 | 7264 | 21,2 % | 29,6 % |
| 0,23-0,28 | 7264 | 25,5 % | 29,9 % |
| 0,28-0,33 | 7263 | 30,3 % | 31,4 % |
| 0,33-0,40 | 7264 | 36,1 % | 33,7 % |
| 0,40-1,00 | 7264 | 47,8 % | 40,1 % |

Horizon 10 s :

| Prédit (tranche) | n | Prédit moyen | Observé |
|---|---|---|---|
| 0,04-0,14 | 6972 | 11,4 % | 0,8 % |
| 0,14-0,17 | 6972 | 15,1 % | 4,3 % |
| 0,17-0,21 | 6972 | 18,6 % | 18,8 % |
| 0,21-0,26 | 6971 | 23,4 % | 32,4 % |
| 0,26-0,32 | 6972 | 28,9 % | 42,6 % |
| 0,32-0,38 | 6972 | 34,7 % | 44,8 % |
| 0,38-0,44 | 6971 | 40,6 % | 47,5 % |
| 0,44-0,50 | 6972 | 46,9 % | 48,5 % |
| 0,50-0,59 | 6972 | 54,3 % | 53,3 % |
| 0,59-0,99 | 6972 | 66,7 % | 56,0 % |

Poids du modèle « baisse ≥ 1 c en 3 s » (variables centrées-réduites, les 8 plus forts) : proba modèle notre côté 0,84 ; distance au prix d'exercice (Chainlink) −0,67 ; temps restant 0,53 ; Bybit 1 s 0,20 ; vendeur de notre côté 0,16 ; vendeur opposé −0,16 ; Bybit 3 s 0,14 ; écart vendeur-acheteur 0,12.

## 3. Contrôle sous-seconde avec les photos 100 ms (lead.json.gz)

Sous-ensemble : instants de décision qui tombent dans une photo (≈ 10 s avant → 10 s après le premier désaccord ≥ 0,20 vu par le bot en direct), fenêtre entièrement couverte. Même instant de décision, même côté opposé ; la cible est mesurée deux fois : sur les lignes 0,3 s et sur les photos 100 ms. Les prédictions viennent des modèles ajustés sur les lignes 0,3 s.

| Horizon | Cible | n | Taux mesuré 0,3 s | Taux mesuré 100 ms | Accord des deux mesures | AUC du modèle (cible 0,3 s) | AUC du modèle (cible 100 ms) |
|---|---|---|---|---|---|---|---|
| 0,25 s | baisse ≥ 1 c | 5706 | 6,9 % | 7,9 % | 93,7 % | 0,66 | 0,65 |
| 0,25 s | baisse ≥ 2 c | 5706 | 3,2 % | 3,2 % | 96,9 % | 0,71 | 0,68 |
| 0,25 s | plus cher à H | 5706 | 7,4 % | 8,2 % | 92,6 % | 0,78 | 0,73 |
| 0,5 s | baisse ≥ 1 c | 5679 | 13,8 % | 14,7 % | 94,5 % | 0,63 | 0,60 |
| 0,5 s | baisse ≥ 2 c | 5679 | 7,0 % | 7,5 % | 96,3 % | 0,64 | 0,61 |
| 0,5 s | plus cher à H | 5679 | 15,6 % | 15,7 % | 93,8 % | 0,72 | 0,67 |
| 1 s | baisse ≥ 1 c | 5168 | 21,6 % | 22,7 % | 94,4 % | 0,59 | 0,57 |
| 1 s | baisse ≥ 2 c | 5168 | 12,9 % | 13,5 % | 96,2 % | 0,59 | 0,56 |
| 1 s | plus cher à H | 5168 | 25,1 % | 25,5 % | 93,8 % | 0,66 | 0,61 |
| 3 s | baisse ≥ 1 c | 3934 | 40,0 % | 41,9 % | 95,0 % | 0,54 | 0,53 |
| 3 s | baisse ≥ 2 c | 3934 | 27,8 % | 29,1 % | 95,7 % | 0,53 | 0,52 |
| 3 s | plus cher à H | 3934 | 42,0 % | 43,1 % | 95,4 % | 0,57 | 0,54 |
| 5 s | baisse ≥ 1 c | 2716 | 50,4 % | 52,7 % | 94,4 % | 0,52 | 0,51 |
| 5 s | baisse ≥ 2 c | 2716 | 38,0 % | 40,1 % | 95,0 % | 0,51 | 0,50 |
| 5 s | plus cher à H | 2716 | 47,7 % | 48,3 % | 95,3 % | 0,53 | 0,51 |

Toutes périodes confondues (les photos ne couvrent que ~20 s par cycle, autour du premier désaccord). Les horodatages restent l'heure de réception par le bot.

## 4. Politiques de couverture — TABLEAU FINAL

Lecture : **baisse captée** = vendeur opposé au moment de la décision − prix réellement payé (moyenne des couvertures exécutées, en cents ; négatif = payé plus cher). **P&L en plus** = somme sur TOUTES les positions de (résultat avec la politique − résultat en gardant), frais compris ; IC 90 % par bootstrap de blocs d'une heure. **sans top 5** = même somme sans les 5 positions où la politique a le plus rapporté. **creux max** = plus forte baisse du portefeuille (positions + couvertures) dans l'ordre chronologique. **gains sacrifiés** = ce que la couverture a coûté sur les positions qui auraient gagné ; entre parenthèses, nombre de jackpots (gain ≥ 4× la mise) perdus.

Référence « garder » (4 stratégies additionnées) : apprentissage 918 positions, +3 697 $, creux −4 258 $ · validation 1056 positions, +383 $, creux −6 685 $ · inédit 764 positions, −5 401 $, creux −5 751 $.

### Déclencheur « modèle −10 » — délai 0 s

Positions déclenchées : apprentissage 391/918 · validation 401/1056 · inédit 257/764.

| Horizon | Politique | Valid. : baisse captée (c) | remplis / déclenchés | P&L net en plus vs garder [IC 90 %] | sans top 5 | creux max (portefeuille) | gains sacrifiés (jackpots perdus) | Test : baisse captée (c) | remplis / déclenchés | P&L en plus vs garder [IC 90 %] | sans top 5 | creux max | gains sacrifiés (jackpots) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| tous | (a) garder sans couvrir | — | 0/0 | **+0 $** [+0 $ ; +0 $] | +0 $ | −6 685 $ | +0 $ (0) | — | 0/0 | **+0 $** [+0 $ ; +0 $] | +0 $ | −5 751 $ | +0 $ (0) |
| tous | (b) couverture immédiate | 0,00 | 401/401 (100,0 %) | **−1 792 $** [−4 620 $ ; +656 $] | −2 014 $ | −7 510 $ | +4 500 $ (10) | 0,00 | 257/257 (100,0 %) | **−139 $** [−1 760 $ ; +1 144 $] | −312 $ | −5 933 $ | +1 680 $ (4) |
| tous | (e) vente immédiate de la moitié | — | 399/401 (99,5 %) | **−960 $** [−2 655 $ ; +397 $] | −1 080 $ | −7 147 $ | +2 663 $ (8) | — | 257/257 (100,0 %) | **+66 $** [−730 $ ; +770 $] | −50 $ | −5 713 $ | +874 $ (3) |
| 0,25 s | (c) ordre passif −1 c, sinon immédiat | −1,34 | 394/401 (98,3 %) | **−3 241 $** [−6 527 $ ; −393 $] | −3 439 $ | −8 286 $ | +6 343 $ (12) | −1,20 | 255/257 (99,2 %) | **−263 $** [−1 790 $ ; +1 154 $] | −427 $ | −6 063 $ | +1 743 $ (3) |
| 0,25 s | (c) ordre passif −1 c, sinon rien | — | 0/401 (0,0 %) | **+0 $** [+0 $ ; +0 $] | +0 $ | −6 685 $ | +0 $ (0) | — | 0/257 (0,0 %) | **+0 $** [+0 $ ; +0 $] | +0 $ | −5 751 $ | +0 $ (0) |
| 0,25 s | (c) ordre passif −2 c, sinon immédiat | −1,34 | 394/401 (98,3 %) | **−3 241 $** [−6 474 $ ; −261 $] | −3 439 $ | −8 286 $ | +6 343 $ (12) | −1,20 | 255/257 (99,2 %) | **−263 $** [−1 835 $ ; +1 098 $] | −427 $ | −6 063 $ | +1 743 $ (3) |
| 0,25 s | (c) ordre passif −2 c, sinon rien | — | 0/401 (0,0 %) | **+0 $** [+0 $ ; +0 $] | +0 $ | −6 685 $ | +0 $ (0) | — | 0/257 (0,0 %) | **+0 $** [+0 $ ; +0 $] | +0 $ | −5 751 $ | +0 $ (0) |
| 0,25 s | (c) ordre passif −3 c, sinon immédiat | −1,34 | 394/401 (98,3 %) | **−3 241 $** [−6 673 $ ; −352 $] | −3 439 $ | −8 286 $ | +6 343 $ (12) | −1,20 | 255/257 (99,2 %) | **−263 $** [−1 879 $ ; +1 096 $] | −427 $ | −6 063 $ | +1 743 $ (3) |
| 0,25 s | (c) ordre passif −3 c, sinon rien | — | 0/401 (0,0 %) | **+0 $** [+0 $ ; +0 $] | +0 $ | −6 685 $ | +0 $ (0) | — | 0/257 (0,0 %) | **+0 $** [+0 $ ; +0 $] | +0 $ | −5 751 $ | +0 $ (0) |
| 0,25 s | (d) attente si P(baisse ≥ 1 c) > seuil (seuil 0,05) | 0,03 | 401/401 (100,0 %) · attend 7 | **−1 790 $** [−4 618 $ ; +630 $] | −2 012 $ | −7 509 $ | +4 499 $ (10) | −0,04 | 257/257 (100,0 %) · attend 8 | **−197 $** [−1 886 $ ; +1 150 $] | −370 $ | −5 991 $ | +1 737 $ (4) |
| 0,5 s | (c) ordre passif −1 c, sinon immédiat | −1,64 | 388/401 (96,8 %) | **−2 468 $** [−5 939 $ ; +358 $] | −2 664 $ | −7 873 $ | +5 900 $ (12) | −1,28 | 252/257 (98,1 %) | **−335 $** [−2 018 $ ; +1 115 $] | −492 $ | −6 118 $ | +1 867 $ (4) |
| 0,5 s | (c) ordre passif −1 c, sinon rien | 1,00 | 5/401 (1,2 %) | **−79 $** [−246 $ ; +9 $] | −83 $ | −6 683 $ | +83 $ (0) | 1,00 | 1/257 (0,4 %) | **+3 $** [+0 $ ; +8 $] | +0 $ | −5 749 $ | +0 $ (0) |
| 0,5 s | (c) ordre passif −2 c, sinon immédiat | −1,62 | 388/401 (96,8 %) | **−2 467 $** [−5 662 $ ; +338 $] | −2 663 $ | −7 873 $ | +5 899 $ (12) | −1,27 | 252/257 (98,1 %) | **−335 $** [−2 053 $ ; +1 117 $] | −491 $ | −6 118 $ | +1 867 $ (4) |
| 0,5 s | (c) ordre passif −2 c, sinon rien | 2,00 | 5/401 (1,2 %) | **−77 $** [−242 $ ; +10 $] | −82 $ | −6 682 $ | +82 $ (0) | 2,00 | 1/257 (0,4 %) | **+3 $** [+0 $ ; +10 $] | +0 $ | −5 748 $ | +0 $ (0) |
| 0,5 s | (c) ordre passif −3 c, sinon immédiat | −1,61 | 388/401 (96,8 %) | **−2 466 $** [−5 598 $ ; +572 $] | −2 662 $ | −7 873 $ | +5 898 $ (12) | −1,27 | 252/257 (98,1 %) | **−335 $** [−2 061 $ ; +1 113 $] | −491 $ | −6 118 $ | +1 867 $ (4) |
| 0,5 s | (c) ordre passif −3 c, sinon rien | 3,00 | 5/401 (1,2 %) | **−76 $** [−238 $ ; +10 $] | −81 $ | −6 682 $ | +81 $ (0) | — | 0/257 (0,0 %) | **+0 $** [+0 $ ; +0 $] | +0 $ | −5 751 $ | +0 $ (0) |
| 0,5 s | (d) attente si P(baisse ≥ 1 c) > seuil (seuil 0,20) | 0,04 | 401/401 (100,0 %) · attend 3 | **−1 790 $** [−4 590 $ ; +577 $] | −2 013 $ | −7 509 $ | +4 500 $ (10) | 0,04 | 257/257 (100,0 %) · attend 3 | **−231 $** [−1 919 $ ; +1 169 $] | −404 $ | −6 025 $ | +1 772 $ (4) |
| 1 s | (c) ordre passif −1 c, sinon immédiat | −1,84 | 381/401 (95,0 %) | **−2 882 $** [−5 949 $ ; −116 $] | −3 080 $ | −8 118 $ | +6 139 $ (11) | −1,41 | 252/257 (98,1 %) | **−326 $** [−1 973 $ ; +1 134 $] | −479 $ | −6 126 $ | +1 879 $ (4) |
| 1 s | (c) ordre passif −1 c, sinon rien | 1,00 | 15/401 (3,7 %) | **−8 $** [−200 $ ; +167 $] | −94 $ | −6 640 $ | +131 $ (0) | 1,00 | 8/257 (3,1 %) | **−16 $** [−211 $ ; +151 $] | −95 $ | −5 768 $ | +96 $ (0) |
| 1 s | (c) ordre passif −2 c, sinon immédiat | −1,80 | 381/401 (95,0 %) | **−2 860 $** [−5 875 $ ; −126 $] | −3 057 $ | −8 103 $ | +6 138 $ (11) | −1,38 | 252/257 (98,1 %) | **−338 $** [−1 948 $ ; +1 064 $] | −492 $ | −6 138 $ | +1 876 $ (4) |
| 1 s | (c) ordre passif −2 c, sinon rien | 2,00 | 11/401 (2,7 %) | **+25 $** [−165 $ ; +194 $] | −68 $ | −6 615 $ | +82 $ (0) | 2,00 | 7/257 (2,7 %) | **−69 $** [−255 $ ; +43 $] | −93 $ | −5 820 $ | +93 $ (0) |
| 1 s | (c) ordre passif −3 c, sinon immédiat | −1,78 | 381/401 (95,0 %) | **−2 895 $** [−5 951 $ ; −155 $] | −3 093 $ | −8 147 $ | +6 137 $ (11) | −1,37 | 252/257 (98,1 %) | **−350 $** [−2 056 $ ; +1 034 $] | −504 $ | −6 150 $ | +1 873 $ (4) |
| 1 s | (c) ordre passif −3 c, sinon rien | 3,00 | 9/401 (2,2 %) | **−12 $** [−163 $ ; +122 $] | −79 $ | −6 660 $ | +81 $ (0) | 3,00 | 4/257 (1,6 %) | **−87 $** [−268 $ ; +7 $] | −90 $ | −5 838 $ | +90 $ (0) |
| 1 s | (d) attente si P(baisse ≥ 1 c) > seuil (seuil 0,30) | 0,06 | 401/401 (100,0 %) · attend 3 | **−1 789 $** [−4 624 $ ; +648 $] | −2 012 $ | −7 509 $ | +4 500 $ (10) | 0,05 | 257/257 (100,0 %) · attend 2 | **−217 $** [−1 912 $ ; +1 130 $] | −390 $ | −6 011 $ | +1 758 $ (4) |
| 3 s | (c) ordre passif −1 c, sinon immédiat | −2,14 | 377/401 (94,0 %) | **−2 598 $** [−5 697 $ ; +285 $] | −2 849 $ | −8 321 $ | +6 147 $ (10) | −1,52 | 252/257 (98,1 %) | **−1 014 $** [−2 904 $ ; +679 $] | −1 160 $ | −6 794 $ | +2 426 $ (4) |
| 3 s | (c) ordre passif −1 c, sinon rien | 1,00 | 42/401 (10,5 %) | **−459 $** [−1 818 $ ; +394 $] | −615 $ | −7 085 $ | +877 $ (2) | 1,00 | 24/257 (9,3 %) | **−58 $** [−473 $ ; +249 $] | −175 $ | −5 810 $ | +272 $ (0) |
| 3 s | (c) ordre passif −2 c, sinon immédiat | −2,10 | 377/401 (94,0 %) | **−1 897 $** [−4 737 $ ; +662 $] | −2 149 $ | −7 616 $ | +5 450 $ (8) | −1,38 | 252/257 (98,1 %) | **−1 009 $** [−2 918 $ ; +627 $] | −1 199 $ | −6 789 $ | +2 422 $ (4) |
| 3 s | (c) ordre passif −2 c, sinon rien | 2,00 | 29/401 (7,2 %) | **+200 $** [−70 $ ; +462 $] | +44 $ | −6 434 $ | +138 $ (0) | 2,00 | 17/257 (6,6 %) | **−160 $** [−524 $ ; +125 $] | −236 $ | −5 911 $ | +267 $ (0) |
| 3 s | (c) ordre passif −3 c, sinon immédiat | −2,05 | 377/401 (94,0 %) | **−1 915 $** [−4 999 $ ; +635 $] | −2 167 $ | −7 639 $ | +5 448 $ (8) | −1,36 | 252/257 (98,1 %) | **−1 018 $** [−2 986 $ ; +668 $] | −1 208 $ | −6 798 $ | +2 417 $ (4) |
| 3 s | (c) ordre passif −3 c, sinon rien | 3,00 | 20/401 (5,0 %) | **+81 $** [−157 $ ; +331 $] | −52 $ | −6 537 $ | +136 $ (0) | 3,00 | 10/257 (3,9 %) | **−202 $** [−547 $ ; +73 $] | −262 $ | −5 953 $ | +262 $ (0) |
| 3 s | (d) attente si P(baisse ≥ 1 c) > seuil (seuil 0,40) | 0,03 | 401/401 (100,0 %) · attend 4 | **−1 789 $** [−4 690 $ ; +581 $] | −2 011 $ | −7 510 $ | +4 500 $ (10) | 0,06 | 257/257 (100,0 %) · attend 4 | **−205 $** [−1 775 $ ; +1 154 $] | −383 $ | −5 999 $ | +1 752 $ (4) |
| 5 s | (c) ordre passif −1 c, sinon immédiat | −2,30 | 370/401 (92,3 %) | **−3 069 $** [−6 167 $ ; −236 $] | −3 295 $ | −8 322 $ | +6 492 $ (12) | −1,27 | 248/257 (96,5 %) | **−373 $** [−2 216 $ ; +1 149 $] | −549 $ | −6 185 $ | +2 037 $ (4) |
| 5 s | (c) ordre passif −1 c, sinon rien | 1,00 | 49/401 (12,2 %) | **−341 $** [−1 566 $ ; +548 $] | −518 $ | −7 038 $ | +877 $ (2) | 1,00 | 29/257 (11,3 %) | **−55 $** [−423 $ ; +249 $] | −171 $ | −5 806 $ | +272 $ (0) |
| 5 s | (c) ordre passif −2 c, sinon immédiat | −2,25 | 370/401 (92,3 %) | **−2 633 $** [−5 604 $ ; +105 $] | −2 853 $ | −7 898 $ | +6 070 $ (10) | −1,05 | 248/257 (96,5 %) | **−263 $** [−2 054 $ ; +1 220 $] | −545 $ | −6 075 $ | +2 032 $ (4) |
| 5 s | (c) ordre passif −2 c, sinon rien | 2,00 | 35/401 (8,7 %) | **+98 $** [−289 $ ; +444 $] | −58 $ | −6 563 $ | +285 $ (1) | 2,00 | 19/257 (7,4 %) | **−158 $** [−522 $ ; +130 $] | −235 $ | −5 909 $ | +267 $ (0) |
| 5 s | (c) ordre passif −3 c, sinon immédiat | −2,19 | 370/401 (92,3 %) | **−2 525 $** [−5 413 $ ; +192 $] | −2 746 $ | −7 813 $ | +5 977 $ (9) | −1,04 | 248/257 (96,5 %) | **−256 $** [−2 129 $ ; +1 307 $] | −540 $ | −6 069 $ | +2 027 $ (4) |
| 5 s | (c) ordre passif −3 c, sinon rien | 3,00 | 21/401 (5,2 %) | **+99 $** [−151 $ ; +346 $] | −36 $ | −6 519 $ | +136 $ (0) | 3,00 | 13/257 (5,1 %) | **−192 $** [−532 $ ; +79 $] | −255 $ | −5 943 $ | +262 $ (0) |
| 5 s | (d) attente si P(baisse ≥ 1 c) > seuil (seuil 0,30) | −0,25 | 401/401 (100,0 %) · attend 88 | **−1 873 $** [−4 682 $ ; +612 $] | −2 096 $ | −7 374 $ | +5 011 $ (10) | 0,01 | 257/257 (100,0 %) · attend 64 | **−307 $** [−2 025 $ ; +1 216 $] | −496 $ | −6 132 $ | +1 992 $ (4) |
| 10 s | (c) ordre passif −1 c, sinon immédiat | −2,36 | 356/401 (88,8 %) | **−3 394 $** [−6 751 $ ; −394 $] | −3 609 $ | −8 376 $ | +6 758 $ (12) | −1,16 | 244/257 (94,9 %) | **−377 $** [−2 200 $ ; +1 043 $] | −547 $ | −6 165 $ | +1 995 $ (4) |
| 10 s | (c) ordre passif −1 c, sinon rien | 1,00 | 88/401 (21,9 %) | **−144 $** [−1 678 $ ; +885 $] | −341 $ | −6 956 $ | +1 058 $ (2) | 1,00 | 60/257 (23,3 %) | **−242 $** [−1 194 $ ; +377 $] | −395 $ | −5 996 $ | +698 $ (2) |
| 10 s | (c) ordre passif −2 c, sinon immédiat | −2,28 | 356/401 (88,8 %) | **−3 426 $** [−6 718 $ ; −500 $] | −3 638 $ | −8 423 $ | +6 804 $ (12) | −1,05 | 244/257 (94,9 %) | **−254 $** [−1 981 $ ; +1 111 $] | −408 $ | −6 043 $ | +1 825 $ (4) |
| 10 s | (c) ordre passif −2 c, sinon rien | 2,00 | 68/401 (17,0 %) | **+417 $** [−35 $ ; +830 $] | +225 $ | −6 442 $ | +406 $ (1) | 2,00 | 42/257 (16,3 %) | **−269 $** [−957 $ ; +194 $] | −380 $ | −6 023 $ | +523 $ (2) |
| 10 s | (c) ordre passif −3 c, sinon immédiat | −2,22 | 356/401 (88,8 %) | **−3 440 $** [−6 499 $ ; −442 $] | −3 658 $ | −8 449 $ | +6 784 $ (12) | −1,05 | 244/257 (94,9 %) | **−238 $** [−1 846 $ ; +1 115 $] | −393 $ | −6 027 $ | +1 818 $ (4) |
| 10 s | (c) ordre passif −3 c, sinon rien | 3,00 | 54/401 (13,5 %) | **+451 $** [+136 $ ; +774 $] | +249 $ | −6 406 $ | +255 $ (0) | 3,00 | 32/257 (12,5 %) | **−346 $** [−1 151 $ ; +152 $] | −441 $ | −6 100 $ | +516 $ (2) |
| 10 s | (d) attente si P(baisse ≥ 1 c) > seuil (seuil 0,15) | −1,16 | 395/401 (98,5 %) · attend 320 | **−3 441 $** [−6 531 $ ; −597 $] | −3 668 $ | −8 444 $ | +6 699 $ (12) | −0,44 | 249/257 (96,9 %) · attend 234 | **−58 $** [−1 669 $ ; +1 223 $] | −233 $ | −5 846 $ | +1 695 $ (3) |

### Déclencheur « entrée + 30 s » — délai 0 s

Positions déclenchées : apprentissage 751/918 · validation 912/1056 · inédit 747/764.

| Horizon | Politique | Valid. : baisse captée (c) | remplis / déclenchés | P&L net en plus vs garder [IC 90 %] | sans top 5 | creux max (portefeuille) | gains sacrifiés (jackpots perdus) | Test : baisse captée (c) | remplis / déclenchés | P&L en plus vs garder [IC 90 %] | sans top 5 | creux max | gains sacrifiés (jackpots) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| tous | (a) garder sans couvrir | — | 0/0 | **+0 $** [+0 $ ; +0 $] | +0 $ | −6 685 $ | +0 $ (0) | — | 0/0 | **+0 $** [+0 $ ; +0 $] | +0 $ | −5 751 $ | +0 $ (0) |
| tous | (b) couverture immédiate | 0,00 | 912/912 (100,0 %) | **−4 334 $** [−10 468 $ ; +1 185 $] | −5 081 $ | −5 721 $ | +17 253 $ (51) | 0,00 | 747/747 (100,0 %) | **+82 $** [−2 905 $ ; +2 947 $] | −557 $ | −5 557 $ | +9 046 $ (28) |
| tous | (e) vente immédiate de la moitié | — | 910/912 (99,8 %) | **−2 322 $** [−5 722 $ ; +595 $] | −2 695 $ | −6 029 $ | +9 920 $ (33) | — | 747/747 (100,0 %) | **+123 $** [−1 675 $ ; +1 863 $] | −296 $ | −5 559 $ | +5 383 $ (23) |
| 0,25 s | (c) ordre passif −1 c, sinon immédiat | 0,09 | 909/912 (99,7 %) | **−4 118 $** [−9 420 $ ; +1 059 $] | −4 836 $ | −6 437 $ | +16 847 $ (49) | 0,02 | 747/747 (100,0 %) | **+2 $** [−3 281 $ ; +3 097 $] | −532 $ | −5 637 $ | +9 062 $ (31) |
| 0,25 s | (c) ordre passif −1 c, sinon rien | — | 0/912 (0,0 %) | **+0 $** [+0 $ ; +0 $] | +0 $ | −6 685 $ | +0 $ (0) | — | 0/747 (0,0 %) | **+0 $** [+0 $ ; +0 $] | +0 $ | −5 751 $ | +0 $ (0) |
| 0,25 s | (c) ordre passif −2 c, sinon immédiat | 0,09 | 909/912 (99,7 %) | **−4 118 $** [−9 499 $ ; +1 151 $] | −4 836 $ | −6 437 $ | +16 847 $ (49) | 0,02 | 747/747 (100,0 %) | **+2 $** [−3 264 $ ; +3 246 $] | −532 $ | −5 637 $ | +9 062 $ (31) |
| 0,25 s | (c) ordre passif −2 c, sinon rien | — | 0/912 (0,0 %) | **+0 $** [+0 $ ; +0 $] | +0 $ | −6 685 $ | +0 $ (0) | — | 0/747 (0,0 %) | **+0 $** [+0 $ ; +0 $] | +0 $ | −5 751 $ | +0 $ (0) |
| 0,25 s | (c) ordre passif −3 c, sinon immédiat | 0,09 | 909/912 (99,7 %) | **−4 118 $** [−9 379 $ ; +849 $] | −4 836 $ | −6 437 $ | +16 847 $ (49) | 0,02 | 747/747 (100,0 %) | **+2 $** [−3 316 $ ; +3 175 $] | −532 $ | −5 637 $ | +9 062 $ (31) |
| 0,25 s | (c) ordre passif −3 c, sinon rien | — | 0/912 (0,0 %) | **+0 $** [+0 $ ; +0 $] | +0 $ | −6 685 $ | +0 $ (0) | — | 0/747 (0,0 %) | **+0 $** [+0 $ ; +0 $] | +0 $ | −5 751 $ | +0 $ (0) |
| 0,25 s | (d) attente si P(baisse ≥ 1 c) > seuil (seuil 0,05) | 0,21 | 912/912 (100,0 %) · attend 196 | **−4 389 $** [−10 084 $ ; +983 $] | −5 107 $ | −5 834 $ | +17 034 $ (51) | 0,07 | 747/747 (100,0 %) · attend 200 | **+111 $** [−3 136 $ ; +2 811 $] | −422 $ | −5 528 $ | +8 702 $ (27) |
| 0,5 s | (c) ordre passif −1 c, sinon immédiat | −0,10 | 909/912 (99,7 %) | **−3 675 $** [−8 341 $ ; +862 $] | −4 322 $ | −6 663 $ | +16 766 $ (51) | −0,16 | 747/747 (100,0 %) | **−160 $** [−3 663 $ ; +2 864 $] | −687 $ | −5 800 $ | +9 184 $ (29) |
| 0,5 s | (c) ordre passif −1 c, sinon rien | 1,00 | 37/912 (4,1 %) | **−440 $** [−1 465 $ ; +496 $] | −917 $ | −6 461 $ | +1 226 $ (3) | 1,00 | 33/747 (4,4 %) | **−346 $** [−1 009 $ ; +243 $] | −594 $ | −6 097 $ | +744 $ (3) |
| 0,5 s | (c) ordre passif −2 c, sinon immédiat | −0,03 | 909/912 (99,7 %) | **−3 696 $** [−7 993 $ ; +658 $] | −4 295 $ | −6 632 $ | +16 738 $ (51) | −0,12 | 747/747 (100,0 %) | **−280 $** [−3 738 $ ; +2 744 $] | −807 $ | −5 919 $ | +9 174 $ (29) |
| 0,5 s | (c) ordre passif −2 c, sinon rien | 2,00 | 24/912 (2,6 %) | **−609 $** [−1 502 $ ; +87 $] | −869 $ | −6 578 $ | +880 $ (2) | 2,00 | 17/747 (2,3 %) | **−297 $** [−675 $ ; +13 $] | −399 $ | −6 049 $ | +431 $ (3) |
| 0,5 s | (c) ordre passif −3 c, sinon immédiat | 0,00 | 908/912 (99,6 %) | **−3 647 $** [−8 175 $ ; +766 $] | −4 246 $ | −6 612 $ | +16 701 $ (51) | −0,11 | 747/747 (100,0 %) | **−277 $** [−3 742 $ ; +2 822 $] | −803 $ | −5 916 $ | +9 167 $ (29) |
| 0,5 s | (c) ordre passif −3 c, sinon rien | 3,00 | 14/912 (1,5 %) | **−721 $** [−1 503 $ ; −117 $] | −781 $ | −6 760 $ | +781 $ (2) | 3,00 | 11/747 (1,5 %) | **−168 $** [−407 $ ; +37 $] | −259 $ | −5 920 $ | +259 $ (3) |
| 0,5 s | (d) attente si P(baisse ≥ 1 c) > seuil (seuil 0,20) | 0,30 | 912/912 (100,0 %) · attend 45 | **−4 271 $** [−10 255 $ ; +1 147 $] | −5 018 $ | −5 591 $ | +17 077 $ (51) | 0,04 | 747/747 (100,0 %) · attend 26 | **+73 $** [−3 089 $ ; +2 878 $] | −566 $ | −5 566 $ | +8 866 $ (27) |
| 1 s | (c) ordre passif −1 c, sinon immédiat | −0,32 | 909/912 (99,7 %) | **−5 263 $** [−11 310 $ ; +470 $] | −5 883 $ | −6 686 $ | +18 587 $ (52) | −0,27 | 747/747 (100,0 %) | **+51 $** [−2 805 $ ; +2 853 $] | −457 $ | −5 591 $ | +8 766 $ (30) |
| 1 s | (c) ordre passif −1 c, sinon rien | 1,00 | 81/912 (8,9 %) | **−873 $** [−2 535 $ ; +605 $] | −1 398 $ | −6 568 $ | +2 377 $ (6) | 1,00 | 73/747 (9,8 %) | **−855 $** [−1 739 $ ; −75 $] | −1 117 $ | −6 606 $ | +1 483 $ (8) |
| 1 s | (c) ordre passif −2 c, sinon immédiat | −0,25 | 909/912 (99,7 %) | **−4 900 $** [−10 866 $ ; +436 $] | −5 526 $ | −6 603 $ | +18 247 $ (52) | −0,19 | 747/747 (100,0 %) | **−41 $** [−3 136 $ ; +2 804 $] | −549 $ | −5 683 $ | +8 721 $ (30) |
| 1 s | (c) ordre passif −2 c, sinon rien | 2,00 | 51/912 (5,6 %) | **−1 161 $** [−2 429 $ ; −107 $] | −1 433 $ | −6 977 $ | +1 678 $ (3) | 2,00 | 45/747 (6,0 %) | **−681 $** [−1 373 $ ; −94 $] | −857 $ | −6 433 $ | +1 041 $ (8) |
| 1 s | (c) ordre passif −3 c, sinon immédiat | −0,21 | 908/912 (99,6 %) | **−4 722 $** [−10 376 $ ; +769 $] | −5 348 $ | −6 470 $ | +18 081 $ (52) | −0,14 | 747/747 (100,0 %) | **+22 $** [−2 777 $ ; +2 737 $] | −486 $ | −5 620 $ | +8 650 $ (30) |
| 1 s | (c) ordre passif −3 c, sinon rien | 3,00 | 36/912 (3,9 %) | **−940 $** [−1 992 $ ; −53 $] | −1 200 $ | −6 791 $ | +1 321 $ (2) | 3,00 | 29/747 (3,9 %) | **−314 $** [−706 $ ; +24 $] | −480 $ | −6 071 $ | +554 $ (6) |
| 1 s | (d) attente si P(baisse ≥ 1 c) > seuil (seuil 0,30) | 0,27 | 912/912 (100,0 %) · attend 49 | **−4 112 $** [−10 039 $ ; +1 218 $] | −4 858 $ | −5 593 $ | +17 082 $ (51) | 0,02 | 747/747 (100,0 %) · attend 31 | **−344 $** [−3 221 $ ; +2 661 $] | −927 $ | −5 984 $ | +9 196 $ (28) |
| 3 s | (c) ordre passif −1 c, sinon immédiat | −0,79 | 903/912 (99,0 %) | **−4 699 $** [−10 747 $ ; +1 007 $] | −5 451 $ | −6 487 $ | +18 330 $ (52) | −0,72 | 742/747 (99,3 %) | **+504 $** [−2 495 $ ; +3 545 $] | −258 $ | −5 206 $ | +9 263 $ (30) |
| 3 s | (c) ordre passif −1 c, sinon rien | 1,00 | 192/912 (21,1 %) | **−1 559 $** [−4 464 $ ; +1 073 $] | −2 168 $ | −6 469 $ | +5 315 $ (13) | 1,00 | 147/747 (19,7 %) | **−643 $** [−1 762 $ ; +459 $] | −976 $ | −6 224 $ | +2 313 $ (12) |
| 3 s | (c) ordre passif −2 c, sinon immédiat | −0,69 | 903/912 (99,0 %) | **−4 081 $** [−10 157 $ ; +1 655 $] | −4 832 $ | −6 130 $ | +17 688 $ (52) | −0,61 | 742/747 (99,3 %) | **+190 $** [−2 988 $ ; +3 240 $] | −573 $ | −5 535 $ | +9 342 $ (29) |
| 3 s | (c) ordre passif −2 c, sinon rien | 2,00 | 140/912 (15,4 %) | **−1 547 $** [−4 041 $ ; +685 $] | −2 163 $ | −6 422 $ | +3 945 $ (11) | 2,00 | 103/747 (13,8 %) | **−841 $** [−1 817 $ ; +131 $] | −1 112 $ | −6 436 $ | +2 025 $ (11) |
| 3 s | (c) ordre passif −3 c, sinon immédiat | −0,59 | 902/912 (98,9 %) | **−3 654 $** [−9 776 $ ; +2 021 $] | −4 412 $ | −5 723 $ | +17 233 $ (52) | −0,52 | 742/747 (99,3 %) | **+78 $** [−3 012 $ ; +3 078 $] | −686 $ | −5 651 $ | +9 304 $ (29) |
| 3 s | (c) ordre passif −3 c, sinon rien | 3,00 | 107/912 (11,7 %) | **−540 $** [−2 018 $ ; +916 $] | −1 092 $ | −5 985 $ | +2 530 $ (10) | 3,00 | 71/747 (9,5 %) | **−722 $** [−1 514 $ ; −12 $] | −999 $ | −6 473 $ | +1 459 $ (8) |
| 3 s | (d) attente si P(baisse ≥ 1 c) > seuil (seuil 0,40) | 0,16 | 912/912 (100,0 %) · attend 135 | **−4 645 $** [−10 636 $ ; +909 $] | −5 385 $ | −5 885 $ | +17 285 $ (51) | −0,02 | 747/747 (100,0 %) · attend 180 | **+501 $** [−2 656 $ ; +3 399 $] | −245 $ | −5 136 $ | +8 891 $ (28) |
| 5 s | (c) ordre passif −1 c, sinon immédiat | −0,82 | 892/912 (97,8 %) | **−5 712 $** [−12 412 $ ; +281 $] | −6 524 $ | −6 711 $ | +19 838 $ (56) | −0,77 | 738/747 (98,8 %) | **+313 $** [−2 696 $ ; +3 387 $] | −565 $ | −5 477 $ | +9 733 $ (33) |
| 5 s | (c) ordre passif −1 c, sinon rien | 1,00 | 268/912 (29,4 %) | **−3 506 $** [−6 858 $ ; −253 $] | −4 116 $ | −7 679 $ | +8 106 $ (22) | 1,00 | 201/747 (26,9 %) | **−1 018 $** [−2 673 $ ; +587 $] | −1 603 $ | −6 599 $ | +3 628 $ (17) |
| 5 s | (c) ordre passif −2 c, sinon immédiat | −0,69 | 892/912 (97,8 %) | **−5 372 $** [−11 728 $ ; +889 $] | −6 192 $ | −6 403 $ | +19 468 $ (55) | −0,65 | 738/747 (98,8 %) | **+523 $** [−2 440 $ ; +3 580 $] | −362 $ | −5 319 $ | +9 363 $ (33) |
| 5 s | (c) ordre passif −2 c, sinon rien | 2,00 | 209/912 (22,9 %) | **−3 130 $** [−6 107 $ ; −532 $] | −3 746 $ | −7 217 $ | +6 504 $ (21) | 2,00 | 136/747 (18,2 %) | **−372 $** [−1 475 $ ; +754 $] | −915 $ | −5 948 $ | +2 237 $ (14) |
| 5 s | (c) ordre passif −3 c, sinon immédiat | −0,56 | 891/912 (97,7 %) | **−4 350 $** [−10 341 $ ; +1 093 $] | −5 176 $ | −5 749 $ | +18 428 $ (53) | −0,58 | 736/747 (98,5 %) | **+666 $** [−2 540 $ ; +3 659 $] | −224 $ | −5 188 $ | +9 070 $ (33) |
| 5 s | (c) ordre passif −3 c, sinon rien | 3,00 | 172/912 (18,9 %) | **−2 066 $** [−4 449 $ ; +183 $] | −2 731 $ | −6 781 $ | +5 162 $ (19) | 3,00 | 101/747 (13,5 %) | **−478 $** [−1 421 $ ; +512 $] | −1 037 $ | −6 065 $ | +1 875 $ (11) |
| 5 s | (d) attente si P(baisse ≥ 1 c) > seuil (seuil 0,30) | 0,27 | 908/912 (99,6 %) · attend 476 | **−2 127 $** [−7 625 $ ; +3 023 $] | −3 007 $ | −4 286 $ | +16 280 $ (46) | −0,06 | 744/747 (99,6 %) · attend 519 | **+984 $** [−2 089 $ ; +4 086 $] | +297 $ | −4 910 $ | +8 634 $ (29) |
| 10 s | (c) ordre passif −1 c, sinon immédiat | −0,87 | 872/912 (95,6 %) | **−4 020 $** [−9 915 $ ; +1 341 $] | −4 785 $ | −6 359 $ | +17 969 $ (52) | −1,25 | 724/747 (96,9 %) | **−782 $** [−4 661 $ ; +2 841 $] | −1 531 $ | −6 360 $ | +10 327 $ (31) |
| 10 s | (c) ordre passif −1 c, sinon rien | 1,00 | 367/912 (40,2 %) | **−2 845 $** [−6 874 $ ; +1 043 $] | −3 591 $ | −6 574 $ | +9 492 $ (25) | 1,00 | 286/747 (38,3 %) | **−1 827 $** [−4 189 $ ; +361 $] | −2 412 $ | −7 408 $ | +5 301 $ (21) |
| 10 s | (c) ordre passif −2 c, sinon immédiat | −0,68 | 872/912 (95,6 %) | **−3 708 $** [−9 738 $ ; +1 685 $] | −4 488 $ | −6 186 $ | +17 631 $ (52) | −1,14 | 724/747 (96,9 %) | **−445 $** [−3 913 $ ; +2 919 $] | −1 201 $ | −6 021 $ | +9 771 $ (31) |
| 10 s | (c) ordre passif −2 c, sinon rien | 2,00 | 304/912 (33,3 %) | **−3 550 $** [−7 151 $ ; −290 $] | −4 166 $ | −7 224 $ | +8 340 $ (23) | 2,00 | 221/747 (29,6 %) | **−401 $** [−1 819 $ ; +1 079 $] | −998 $ | −6 020 $ | +3 427 $ (17) |
| 10 s | (c) ordre passif −3 c, sinon immédiat | −0,58 | 871/912 (95,5 %) | **−2 784 $** [−8 125 $ ; +2 434 $] | −3 573 $ | −5 865 $ | +16 719 $ (50) | −1,06 | 724/747 (96,9 %) | **−493 $** [−3 706 $ ; +2 683 $] | −1 256 $ | −6 077 $ | +9 606 $ (30) |
| 10 s | (c) ordre passif −3 c, sinon rien | 3,00 | 260/912 (28,5 %) | **−1 772 $** [−4 829 $ ; +1 081 $] | −2 437 $ | −5 744 $ | +6 566 $ (21) | 3,00 | 168/747 (22,5 %) | **−452 $** [−1 762 $ ; +891 $] | −1 060 $ | −6 039 $ | +2 895 $ (15) |
| 10 s | (d) attente si P(baisse ≥ 1 c) > seuil (seuil 0,15) | 0,64 | 872/912 (95,6 %) · attend 899 | **−133 $** [−4 699 $ ; +4 185 $] | −953 $ | −4 753 $ | +13 324 $ (40) | −0,62 | 724/747 (96,9 %) · attend 746 | **−286 $** [−3 165 $ ; +2 556 $] | −845 $ | −5 949 $ | +8 240 $ (24) |

### Déclencheur « modèle −10 » — délai d'exécution 0,3 s

| Horizon | Politique | Valid. : baisse captée (c) | remplis / déclenchés | P&L net en plus vs garder [IC 90 %] | sans top 5 | creux max (portefeuille) | gains sacrifiés (jackpots perdus) | Test : baisse captée (c) | remplis / déclenchés | P&L en plus vs garder [IC 90 %] | sans top 5 | creux max | gains sacrifiés (jackpots) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| tous | (a) garder sans couvrir | — | 0/0 | **+0 $** [+0 $ ; +0 $] | +0 $ | −6 685 $ | +0 $ (0) | — | 0/0 | **+0 $** [+0 $ ; +0 $] | +0 $ | −5 751 $ | +0 $ (0) |
| tous | (b) couverture immédiate | −1,34 | 394/401 (98,3 %) | **−3 241 $** [−6 552 $ ; −457 $] | −3 438 $ | −8 285 $ | +6 343 $ (12) | −1,20 | 255/257 (99,2 %) | **−263 $** [−1 839 $ ; +1 053 $] | −427 $ | −6 063 $ | +1 743 $ (3) |
| tous | (e) vente immédiate de la moitié | — | 392/401 (97,8 %) | **−1 638 $** [−3 469 $ ; +19 $] | −1 743 $ | −7 530 $ | +3 483 $ (10) | — | 255/257 (99,2 %) | **−212 $** [−1 148 $ ; +612 $] | −322 $ | −5 987 $ | +1 054 $ (3) |
| 0,25 s | (c) ordre passif −1 c, sinon immédiat | −1,56 | 388/401 (96,8 %) | **−2 397 $** [−5 664 $ ; +535 $] | −2 593 $ | −7 872 $ | +5 830 $ (12) | −1,28 | 252/257 (98,1 %) | **−335 $** [−1 972 $ ; +1 136 $] | −492 $ | −6 118 $ | +1 867 $ (4) |
| 0,25 s | (c) ordre passif −1 c, sinon rien | — | 0/401 (0,0 %) | **+0 $** [+0 $ ; +0 $] | +0 $ | −6 685 $ | +0 $ (0) | 1,00 | 1/257 (0,4 %) | **+3 $** [+0 $ ; +8 $] | +0 $ | −5 749 $ | +0 $ (0) |
| 0,25 s | (c) ordre passif −2 c, sinon immédiat | −1,56 | 388/401 (96,8 %) | **−2 397 $** [−5 604 $ ; +492 $] | −2 593 $ | −7 872 $ | +5 830 $ (12) | −1,27 | 252/257 (98,1 %) | **−335 $** [−2 049 $ ; +1 155 $] | −491 $ | −6 118 $ | +1 867 $ (4) |
| 0,25 s | (c) ordre passif −2 c, sinon rien | — | 0/401 (0,0 %) | **+0 $** [+0 $ ; +0 $] | +0 $ | −6 685 $ | +0 $ (0) | 2,00 | 1/257 (0,4 %) | **+3 $** [+0 $ ; +10 $] | +0 $ | −5 748 $ | +0 $ (0) |
| 0,25 s | (c) ordre passif −3 c, sinon immédiat | −1,56 | 388/401 (96,8 %) | **−2 397 $** [−5 778 $ ; +635 $] | −2 593 $ | −7 872 $ | +5 830 $ (12) | −1,27 | 252/257 (98,1 %) | **−335 $** [−2 114 $ ; +1 176 $] | −491 $ | −6 118 $ | +1 867 $ (4) |
| 0,25 s | (c) ordre passif −3 c, sinon rien | — | 0/401 (0,0 %) | **+0 $** [+0 $ ; +0 $] | +0 $ | −6 685 $ | +0 $ (0) | — | 0/257 (0,0 %) | **+0 $** [+0 $ ; +0 $] | +0 $ | −5 751 $ | +0 $ (0) |
| 0,25 s | (d) attente si P(baisse ≥ 1 c) > seuil (seuil 0,05) | −1,32 | 394/401 (98,3 %) · attend 7 | **−3 240 $** [−6 635 $ ; −171 $] | −3 438 $ | −8 285 $ | +6 343 $ (12) | −1,10 | 255/257 (99,2 %) · attend 8 | **−289 $** [−1 921 $ ; +1 078 $] | −453 $ | −6 089 $ | +1 778 $ (3) |
| 0,5 s | (c) ordre passif −1 c, sinon immédiat | −1,74 | 382/401 (95,3 %) | **−2 162 $** [−5 056 $ ; +547 $] | −2 358 $ | −7 892 $ | +5 472 $ (9) | −1,33 | 252/257 (98,1 %) | **−210 $** [−1 863 $ ; +1 160 $] | −359 $ | −6 000 $ | +1 734 $ (4) |
| 0,5 s | (c) ordre passif −1 c, sinon rien | 1,00 | 9/401 (2,2 %) | **+51 $** [−15 $ ; +141 $] | −13 $ | −6 621 $ | +15 $ (0) | 1,00 | 8/257 (3,1 %) | **−16 $** [−228 $ ; +151 $] | −95 $ | −5 768 $ | +96 $ (0) |
| 0,5 s | (c) ordre passif −2 c, sinon immédiat | −1,72 | 382/401 (95,3 %) | **−2 151 $** [−5 098 $ ; +385 $] | −2 347 $ | −7 882 $ | +5 472 $ (9) | −1,28 | 252/257 (98,1 %) | **−240 $** [−1 726 $ ; +1 152 $] | −389 $ | −6 031 $ | +1 726 $ (4) |
| 0,5 s | (c) ordre passif −2 c, sinon rien | 2,00 | 7/401 (1,7 %) | **+10 $** [−29 $ ; +53 $] | −15 $ | −6 663 $ | +15 $ (0) | 2,00 | 3/257 (1,2 %) | **+6 $** [+0 $ ; +13 $] | +0 $ | −5 745 $ | +0 $ (0) |
| 0,5 s | (c) ordre passif −3 c, sinon immédiat | −1,71 | 382/401 (95,3 %) | **−2 148 $** [−5 263 $ ; +416 $] | −2 344 $ | −7 879 $ | +5 472 $ (9) | −1,28 | 252/257 (98,1 %) | **−240 $** [−1 846 $ ; +1 064 $] | −389 $ | −6 030 $ | +1 726 $ (4) |
| 0,5 s | (c) ordre passif −3 c, sinon rien | 3,00 | 7/401 (1,7 %) | **+13 $** [−29 $ ; +60 $] | −14 $ | −6 660 $ | +14 $ (0) | 3,00 | 2/257 (0,8 %) | **+4 $** [+0 $ ; +11 $] | +0 $ | −5 748 $ | +0 $ (0) |
| 0,5 s | (d) attente si P(baisse ≥ 1 c) > seuil (seuil 0,20) | −1,32 | 394/401 (98,3 %) · attend 3 | **−3 240 $** [−6 586 $ ; −350 $] | −3 437 $ | −8 285 $ | +6 343 $ (12) | −1,06 | 255/257 (99,2 %) · attend 3 | **−286 $** [−1 924 $ ; +1 070 $] | −451 $ | −6 087 $ | +1 772 $ (3) |
| 1 s | (c) ordre passif −1 c, sinon immédiat | −2,01 | 381/401 (95,0 %) | **−2 653 $** [−5 743 $ ; +21 $] | −2 840 $ | −8 134 $ | +6 001 $ (11) | −1,42 | 252/257 (98,1 %) | **−374 $** [−2 083 $ ; +1 094 $] | −521 $ | −6 184 $ | +1 894 $ (4) |
| 1 s | (c) ordre passif −1 c, sinon rien | 1,00 | 19/401 (4,7 %) | **+137 $** [−30 $ ; +320 $] | +22 $ | −6 584 $ | +62 $ (0) | 1,00 | 14/257 (5,4 %) | **+51 $** [−129 $ ; +210 $] | −65 $ | −5 700 $ | +96 $ (0) |
| 1 s | (c) ordre passif −2 c, sinon immédiat | −1,99 | 381/401 (95,0 %) | **−2 593 $** [−5 660 $ ; +117 $] | −2 780 $ | −8 083 $ | +5 954 $ (11) | −1,38 | 252/257 (98,1 %) | **−382 $** [−2 130 $ ; +1 092 $] | −529 $ | −6 192 $ | +1 891 $ (4) |
| 1 s | (c) ordre passif −2 c, sinon rien | 2,00 | 13/401 (3,2 %) | **+116 $** [+0 $ ; +251 $] | +21 $ | −6 615 $ | +15 $ (0) | 2,00 | 9/257 (3,5 %) | **−61 $** [−247 $ ; +54 $] | −90 $ | −5 813 $ | +93 $ (0) |
| 1 s | (c) ordre passif −3 c, sinon immédiat | −1,97 | 381/401 (95,0 %) | **−2 580 $** [−5 598 $ ; +124 $] | −2 767 $ | −8 080 $ | +5 954 $ (11) | −1,36 | 252/257 (98,1 %) | **−385 $** [−2 147 $ ; +1 061 $] | −532 $ | −6 195 $ | +1 888 $ (4) |
| 1 s | (c) ordre passif −3 c, sinon rien | 3,00 | 11/401 (2,7 %) | **+80 $** [−14 $ ; +214 $] | +2 $ | −6 660 $ | +14 $ (0) | 3,00 | 4/257 (1,6 %) | **−87 $** [−268 $ ; +7 $] | −90 $ | −5 838 $ | +90 $ (0) |
| 1 s | (d) attente si P(baisse ≥ 1 c) > seuil (seuil 0,30) | −1,29 | 394/401 (98,3 %) · attend 3 | **−3 238 $** [−6 509 $ ; −246 $] | −3 435 $ | −8 285 $ | +6 343 $ (12) | −1,09 | 255/257 (99,2 %) · attend 2 | **−284 $** [−1 800 $ ; +1 073 $] | −448 $ | −6 084 $ | +1 764 $ (3) |
| 3 s | (c) ordre passif −1 c, sinon immédiat | −2,15 | 377/401 (94,0 %) | **−2 968 $** [−6 070 $ ; +5 $] | −3 187 $ | −8 358 $ | +6 470 $ (12) | −1,39 | 252/257 (98,1 %) | **−939 $** [−2 797 $ ; +720 $] | −1 079 $ | −6 723 $ | +2 427 $ (3) |
| 3 s | (c) ordre passif −1 c, sinon rien | 1,00 | 42/401 (10,5 %) | **−390 $** [−1 712 $ ; +447 $] | −547 $ | −7 085 $ | +809 $ (2) | 1,00 | 25/257 (9,7 %) | **−57 $** [−407 $ ; +252 $] | −174 $ | −5 809 $ | +272 $ (0) |
| 3 s | (c) ordre passif −2 c, sinon immédiat | −2,13 | 377/401 (94,0 %) | **−2 476 $** [−5 538 $ ; +250 $] | −2 695 $ | −7 864 $ | +5 984 $ (10) | −1,26 | 252/257 (98,1 %) | **−937 $** [−2 946 $ ; +754 $] | −1 114 $ | −6 722 $ | +2 422 $ (3) |
| 3 s | (c) ordre passif −2 c, sinon rien | 2,00 | 29/401 (7,2 %) | **+267 $** [+60 $ ; +504 $] | +111 $ | −6 434 $ | +71 $ (0) | 2,00 | 18/257 (7,0 %) | **−159 $** [−528 $ ; +133 $] | −235 $ | −5 910 $ | +267 $ (0) |
| 3 s | (c) ordre passif −3 c, sinon immédiat | −2,09 | 377/401 (94,0 %) | **−2 482 $** [−5 477 $ ; +141 $] | −2 701 $ | −7 875 $ | +5 983 $ (10) | −1,23 | 252/257 (98,1 %) | **−967 $** [−2 862 $ ; +724 $] | −1 144 $ | −6 752 $ | +2 417 $ (3) |
| 3 s | (c) ordre passif −3 c, sinon rien | 3,00 | 20/401 (5,0 %) | **+147 $** [−42 $ ; +356 $] | +14 $ | −6 537 $ | +70 $ (0) | 3,00 | 11/257 (4,3 %) | **−200 $** [−542 $ ; +70 $] | −260 $ | −5 952 $ | +262 $ (0) |
| 3 s | (d) attente si P(baisse ≥ 1 c) > seuil (seuil 0,40) | −1,35 | 394/401 (98,3 %) · attend 4 | **−3 239 $** [−6 620 $ ; −291 $] | −3 436 $ | −8 286 $ | +6 343 $ (12) | −1,08 | 255/257 (99,2 %) · attend 4 | **−280 $** [−1 807 $ ; +1 058 $] | −443 $ | −6 080 $ | +1 758 $ (3) |
| 5 s | (c) ordre passif −1 c, sinon immédiat | −2,33 | 370/401 (92,3 %) | **−3 128 $** [−6 601 $ ; −151 $] | −3 354 $ | −8 193 $ | +6 596 $ (12) | −1,28 | 247/257 (96,1 %) | **−657 $** [−2 600 $ ; +921 $] | −832 $ | −6 456 $ | +2 252 $ (4) |
| 5 s | (c) ordre passif −1 c, sinon rien | 1,00 | 54/401 (13,5 %) | **−204 $** [−1 569 $ ; +684 $] | −381 $ | −6 980 $ | +809 $ (2) | 1,00 | 32/257 (12,5 %) | **−50 $** [−418 $ ; +248 $] | −166 $ | −5 801 $ | +272 $ (0) |
| 5 s | (c) ordre passif −2 c, sinon immédiat | −2,29 | 370/401 (92,3 %) | **−3 259 $** [−6 462 $ ; −478 $] | −3 481 $ | −8 336 $ | +6 712 $ (12) | −1,05 | 247/257 (96,1 %) | **−556 $** [−2 651 $ ; +1 099 $] | −844 $ | −6 355 $ | +2 247 $ (4) |
| 5 s | (c) ordre passif −2 c, sinon rien | 2,00 | 40/401 (10,0 %) | **+241 $** [−142 $ ; +567 $] | +84 $ | −6 500 $ | +218 $ (1) | 2,00 | 19/257 (7,4 %) | **−158 $** [−531 $ ; +134 $] | −235 $ | −5 909 $ | +267 $ (0) |
| 5 s | (c) ordre passif −3 c, sinon immédiat | −2,27 | 370/401 (92,3 %) | **−3 146 $** [−6 009 $ ; −241 $] | −3 369 $ | −8 220 $ | +6 583 $ (11) | −1,05 | 247/257 (96,1 %) | **−551 $** [−2 469 $ ; +1 196 $] | −840 $ | −6 350 $ | +2 243 $ (4) |
| 5 s | (c) ordre passif −3 c, sinon rien | 3,00 | 28/401 (7,0 %) | **+289 $** [+51 $ ; +531 $] | +140 $ | −6 450 $ | +70 $ (0) | 3,00 | 13/257 (5,1 %) | **−192 $** [−545 $ ; +98 $] | −255 $ | −5 943 $ | +262 $ (0) |
| 5 s | (d) attente si P(baisse ≥ 1 c) > seuil (seuil 0,30) | −1,41 | 394/401 (98,3 %) · attend 88 | **−3 126 $** [−6 320 $ ; −69 $] | −3 326 $ | −8 245 $ | +6 329 $ (12) | −0,71 | 255/257 (99,2 %) · attend 64 | **−351 $** [−1 987 $ ; +1 090 $] | −534 $ | −6 159 $ | +1 878 $ (4) |
| 10 s | (c) ordre passif −1 c, sinon immédiat | −2,22 | 354/401 (88,3 %) | **−3 325 $** [−6 478 $ ; −666 $] | −3 527 $ | −8 229 $ | +6 636 $ (12) | −1,05 | 244/257 (94,9 %) | **−432 $** [−2 282 $ ; +1 066 $] | −604 $ | −6 218 $ | +2 013 $ (4) |
| 10 s | (c) ordre passif −1 c, sinon rien | 1,00 | 88/401 (21,9 %) | **−76 $** [−1 497 $ ; +906 $] | −273 $ | −6 956 $ | +989 $ (2) | 1,00 | 60/257 (23,3 %) | **−242 $** [−1 180 $ ; +368 $] | −395 $ | −5 996 $ | +698 $ (2) |
| 10 s | (c) ordre passif −2 c, sinon immédiat | −2,13 | 354/401 (88,3 %) | **−3 369 $** [−6 357 $ ; −600 $] | −3 568 $ | −8 276 $ | +6 683 $ (12) | −0,90 | 244/257 (94,9 %) | **−304 $** [−1 993 $ ; +1 051 $] | −459 $ | −6 091 $ | +1 843 $ (4) |
| 10 s | (c) ordre passif −2 c, sinon rien | 2,00 | 68/401 (17,0 %) | **+484 $** [+91 $ ; +866 $] | +292 $ | −6 442 $ | +338 $ (1) | 2,00 | 42/257 (16,3 %) | **−269 $** [−957 $ ; +190 $] | −380 $ | −6 023 $ | +523 $ (2) |
| 10 s | (c) ordre passif −3 c, sinon immédiat | −2,09 | 354/401 (88,3 %) | **−3 371 $** [−6 608 $ ; −665 $] | −3 578 $ | −8 279 $ | +6 650 $ (12) | −0,91 | 244/257 (94,9 %) | **−290 $** [−1 954 $ ; +1 071 $] | −447 $ | −6 077 $ | +1 836 $ (4) |
| 10 s | (c) ordre passif −3 c, sinon rien | 3,00 | 54/401 (13,5 %) | **+518 $** [+229 $ ; +828 $] | +316 $ | −6 406 $ | +189 $ (0) | 3,00 | 32/257 (12,5 %) | **−346 $** [−1 140 $ ; +152 $] | −441 $ | −6 100 $ | +516 $ (2) |
| 10 s | (d) attente si P(baisse ≥ 1 c) > seuil (seuil 0,15) | −1,54 | 386/401 (96,3 %) · attend 320 | **−3 376 $** [−6 514 $ ; −604 $] | −3 559 $ | −8 323 $ | +6 613 $ (12) | −0,60 | 248/257 (96,5 %) · attend 234 | **−192 $** [−1 672 $ ; +1 126 $] | −369 $ | −5 978 $ | +1 748 $ (4) |

### Déclencheur « entrée + 30 s » — délai d'exécution 0,3 s

| Horizon | Politique | Valid. : baisse captée (c) | remplis / déclenchés | P&L net en plus vs garder [IC 90 %] | sans top 5 | creux max (portefeuille) | gains sacrifiés (jackpots perdus) | Test : baisse captée (c) | remplis / déclenchés | P&L en plus vs garder [IC 90 %] | sans top 5 | creux max | gains sacrifiés (jackpots) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| tous | (a) garder sans couvrir | — | 0/0 | **+0 $** [+0 $ ; +0 $] | +0 $ | −6 685 $ | +0 $ (0) | — | 0/0 | **+0 $** [+0 $ ; +0 $] | +0 $ | −5 751 $ | +0 $ (0) |
| tous | (b) couverture immédiate | 0,10 | 909/912 (99,7 %) | **−4 137 $** [−9 134 $ ; +1 182 $] | −4 855 $ | −6 463 $ | +16 847 $ (49) | 0,02 | 747/747 (100,0 %) | **+41 $** [−3 407 $ ; +3 119 $] | −493 $ | −5 598 $ | +9 067 $ (31) |
| tous | (e) vente immédiate de la moitié | — | 907/912 (99,5 %) | **−2 539 $** [−5 744 $ ; +460 $] | −2 919 $ | −6 303 $ | +10 042 $ (32) | — | 747/747 (100,0 %) | **+305 $** [−1 533 $ ; +2 083 $] | −9 $ | −5 377 $ | +5 157 $ (26) |
| 0,25 s | (c) ordre passif −1 c, sinon immédiat | 0,15 | 908/912 (99,6 %) | **−3 166 $** [−7 392 $ ; +1 103 $] | −3 766 $ | −6 609 $ | +16 212 $ (50) | −0,08 | 747/747 (100,0 %) | **−238 $** [−3 305 $ ; +2 842 $] | −765 $ | −5 878 $ | +9 055 $ (29) |
| 0,25 s | (c) ordre passif −1 c, sinon rien | 1,00 | 4/912 (0,4 %) | **−253 $** [−555 $ ; +0 $] | −297 $ | −6 723 $ | +297 $ (1) | 1,00 | 4/747 (0,5 %) | **−236 $** [−744 $ ; +33 $] | −257 $ | −5 988 $ | +257 $ (0) |
| 0,25 s | (c) ordre passif −2 c, sinon immédiat | 0,15 | 908/912 (99,6 %) | **−3 159 $** [−7 520 $ ; +904 $] | −3 759 $ | −6 604 $ | +16 208 $ (50) | −0,08 | 747/747 (100,0 %) | **−233 $** [−3 789 $ ; +2 769 $] | −759 $ | −5 872 $ | +9 052 $ (29) |
| 0,25 s | (c) ordre passif −2 c, sinon rien | 2,00 | 3/912 (0,3 %) | **−142 $** [−401 $ ; +46 $] | −188 $ | −6 720 $ | +188 $ (1) | 2,00 | 1/747 (0,1 %) | **+14 $** [+0 $ ; +42 $] | +0 $ | −5 737 $ | +0 $ (0) |
| 0,25 s | (c) ordre passif −3 c, sinon immédiat | 0,15 | 908/912 (99,6 %) | **−3 154 $** [−7 409 $ ; +876 $] | −3 754 $ | −6 599 $ | +16 204 $ (50) | −0,08 | 747/747 (100,0 %) | **−232 $** [−3 399 $ ; +2 794 $] | −758 $ | −5 871 $ | +9 052 $ (29) |
| 0,25 s | (c) ordre passif −3 c, sinon rien | 3,00 | 3/912 (0,3 %) | **−137 $** [−393 $ ; +88 $] | −185 $ | −6 717 $ | +185 $ (1) | 3,00 | 1/747 (0,1 %) | **+15 $** [+0 $ ; +45 $] | +0 $ | −5 736 $ | +0 $ (0) |
| 0,25 s | (d) attente si P(baisse ≥ 1 c) > seuil (seuil 0,05) | 0,22 | 908/912 (99,6 %) · attend 196 | **−3 772 $** [−8 788 $ ; +1 186 $] | −4 490 $ | −6 366 $ | +16 549 $ (49) | −0,02 | 747/747 (100,0 %) · attend 200 | **+379 $** [−2 783 $ ; +3 226 $] | −148 $ | −5 260 $ | +8 612 $ (30) |
| 0,5 s | (c) ordre passif −1 c, sinon immédiat | −0,29 | 908/912 (99,6 %) | **−4 839 $** [−10 430 $ ; +478 $] | −5 487 $ | −6 709 $ | +17 948 $ (52) | −0,23 | 747/747 (100,0 %) | **+351 $** [−3 210 $ ; +3 303 $] | −115 $ | −5 328 $ | +8 585 $ (30) |
| 0,5 s | (c) ordre passif −1 c, sinon rien | 1,00 | 60/912 (6,6 %) | **−626 $** [−1 810 $ ; +437 $] | −1 087 $ | −6 784 $ | +1 658 $ (3) | 1,00 | 52/747 (7,0 %) | **−708 $** [−1 485 $ ; +10 $] | −838 $ | −6 459 $ | +1 082 $ (4) |
| 0,5 s | (c) ordre passif −2 c, sinon immédiat | −0,23 | 908/912 (99,6 %) | **−4 971 $** [−10 746 $ ; −124 $] | −5 572 $ | −6 846 $ | +17 828 $ (52) | −0,14 | 747/747 (100,0 %) | **+505 $** [−2 758 $ ; +3 609 $] | +39 $ | −5 173 $ | +8 409 $ (30) |
| 0,5 s | (c) ordre passif −2 c, sinon rien | 2,00 | 38/912 (4,2 %) | **−775 $** [−1 577 $ ; −49 $] | −1 042 $ | −6 987 $ | +1 183 $ (1) | 2,00 | 21/747 (2,8 %) | **−177 $** [−603 $ ; +187 $] | −315 $ | −5 929 $ | +398 $ (3) |
| 0,5 s | (c) ordre passif −3 c, sinon immédiat | −0,19 | 908/912 (99,6 %) | **−4 964 $** [−10 361 $ ; +254 $] | −5 564 $ | −6 852 $ | +17 804 $ (52) | −0,12 | 747/747 (100,0 %) | **+595 $** [−2 697 $ ; +3 706 $] | +129 $ | −5 083 $ | +8 330 $ (30) |
| 0,5 s | (c) ordre passif −3 c, sinon rien | 3,00 | 30/912 (3,3 %) | **−565 $** [−1 129 $ ; −5 $] | −798 $ | −6 905 $ | +844 $ (1) | 3,00 | 15/747 (2,0 %) | **−75 $** [−390 $ ; +165 $] | −193 $ | −5 826 $ | +227 $ (3) |
| 0,5 s | (d) attente si P(baisse ≥ 1 c) > seuil (seuil 0,20) | 0,25 | 909/912 (99,7 %) · attend 45 | **−3 820 $** [−8 986 $ ; +1 229 $] | −4 538 $ | −6 177 $ | +16 493 $ (49) | 0,02 | 747/747 (100,0 %) · attend 26 | **+167 $** [−3 263 $ ; +3 271 $] | −367 $ | −5 472 $ | +8 949 $ (32) |
| 1 s | (c) ordre passif −1 c, sinon immédiat | −0,39 | 907/912 (99,5 %) | **−4 726 $** [−10 920 $ ; +499 $] | −5 366 $ | −6 628 $ | +17 715 $ (51) | −0,41 | 746/747 (99,9 %) | **+568 $** [−2 792 $ ; +3 749 $] | −297 $ | −5 091 $ | +8 694 $ (30) |
| 1 s | (c) ordre passif −1 c, sinon rien | 1,00 | 101/912 (11,1 %) | **−681 $** [−2 149 $ ; +677 $] | −1 194 $ | −6 771 $ | +2 434 $ (7) | 1,00 | 88/747 (11,8 %) | **−846 $** [−1 712 $ ; −83 $] | −1 029 $ | −6 597 $ | +1 558 $ (8) |
| 1 s | (c) ordre passif −2 c, sinon immédiat | −0,31 | 907/912 (99,5 %) | **−4 530 $** [−10 318 $ ; +657 $] | −5 110 $ | −6 677 $ | +17 452 $ (53) | −0,31 | 746/747 (99,9 %) | **+513 $** [−2 812 $ ; +3 672 $] | −352 $ | −5 145 $ | +8 625 $ (30) |
| 1 s | (c) ordre passif −2 c, sinon rien | 2,00 | 70/912 (7,7 %) | **−881 $** [−1 844 $ ; +46 $] | −1 161 $ | −7 088 $ | +1 769 $ (6) | 2,00 | 55/747 (7,4 %) | **−472 $** [−1 184 $ ; +215 $] | −667 $ | −6 223 $ | +1 000 $ (8) |
| 1 s | (c) ordre passif −3 c, sinon immédiat | −0,25 | 907/912 (99,5 %) | **−4 537 $** [−10 109 $ ; +953 $] | −5 116 $ | −6 672 $ | +17 369 $ (53) | −0,25 | 746/747 (99,9 %) | **+558 $** [−2 788 $ ; +3 639 $] | −307 $ | −5 100 $ | +8 561 $ (29) |
| 1 s | (c) ordre passif −3 c, sinon rien | 3,00 | 51/912 (5,6 %) | **−632 $** [−1 410 $ ; +134 $] | −893 $ | −6 811 $ | +1 217 $ (5) | 3,00 | 34/747 (4,6 %) | **−428 $** [−929 $ ; +20 $] | −574 $ | −6 179 $ | +678 $ (6) |
| 1 s | (d) attente si P(baisse ≥ 1 c) > seuil (seuil 0,30) | 0,22 | 909/912 (99,7 %) · attend 49 | **−3 962 $** [−9 257 $ ; +1 196 $] | −4 661 $ | −6 324 $ | +16 619 $ (49) | 0,03 | 747/747 (100,0 %) · attend 31 | **+98 $** [−3 036 $ ; +3 248 $] | −436 $ | −5 541 $ | +9 003 $ (32) |
| 3 s | (c) ordre passif −1 c, sinon immédiat | −0,73 | 902/912 (98,9 %) | **−4 463 $** [−10 274 $ ; +786 $] | −5 216 $ | −6 412 $ | +18 235 $ (49) | −0,73 | 742/747 (99,3 %) | **+383 $** [−2 844 $ ; +3 540 $] | −435 $ | −5 428 $ | +9 578 $ (31) |
| 3 s | (c) ordre passif −1 c, sinon rien | 1,00 | 205/912 (22,5 %) | **−1 381 $** [−3 922 $ ; +1 109 $] | −1 984 $ | −6 469 $ | +5 212 $ (12) | 1,00 | 149/747 (19,9 %) | **−648 $** [−1 790 $ ; +488 $] | −914 $ | −6 229 $ | +2 300 $ (12) |
| 3 s | (c) ordre passif −2 c, sinon immédiat | −0,63 | 902/912 (98,9 %) | **−4 020 $** [−10 168 $ ; +1 230 $] | −4 771 $ | −6 342 $ | +17 771 $ (49) | −0,65 | 742/747 (99,3 %) | **+162 $** [−3 251 $ ; +3 267 $] | −658 $ | −5 655 $ | +9 605 $ (31) |
| 3 s | (c) ordre passif −2 c, sinon rien | 2,00 | 147/912 (16,1 %) | **−1 264 $** [−3 147 $ ; +562 $] | −1 880 $ | −6 017 $ | +3 756 $ (10) | 2,00 | 103/747 (13,8 %) | **−800 $** [−1 756 $ ; +183 $] | −1 071 $ | −6 395 $ | +1 983 $ (11) |
| 3 s | (c) ordre passif −3 c, sinon immédiat | −0,53 | 902/912 (98,9 %) | **−3 279 $** [−9 362 $ ; +2 032 $] | −4 038 $ | −5 966 $ | +17 008 $ (47) | −0,56 | 742/747 (99,3 %) | **+72 $** [−3 193 $ ; +3 029 $] | −748 $ | −5 749 $ | +9 567 $ (31) |
| 3 s | (c) ordre passif −3 c, sinon rien | 3,00 | 121/912 (13,3 %) | **−236 $** [−1 659 $ ; +1 127 $] | −788 $ | −5 862 $ | +2 433 $ (9) | 3,00 | 72/747 (9,6 %) | **−739 $** [−1 542 $ ; +14 $] | −1 016 $ | −6 490 $ | +1 480 $ (8) |
| 3 s | (d) attente si P(baisse ≥ 1 c) > seuil (seuil 0,40) | 0,09 | 909/912 (99,7 %) · attend 135 | **−4 016 $** [−9 157 $ ; +1 176 $] | −4 723 $ | −6 263 $ | +16 674 $ (49) | −0,03 | 747/747 (100,0 %) · attend 180 | **−9 $** [−3 681 $ ; +3 483 $] | −801 $ | −5 666 $ | +9 539 $ (33) |
| 5 s | (c) ordre passif −1 c, sinon immédiat | −0,83 | 890/912 (97,6 %) | **−5 831 $** [−12 209 $ ; +203 $] | −6 643 $ | −7 031 $ | +19 699 $ (56) | −0,79 | 735/747 (98,4 %) | **−16 $** [−3 210 $ ; +3 030 $] | −806 $ | −5 806 $ | +10 165 $ (31) |
| 5 s | (c) ordre passif −1 c, sinon rien | 1,00 | 273/912 (29,9 %) | **−3 204 $** [−6 226 $ ; −303 $] | −3 806 $ | −7 667 $ | +7 818 $ (21) | 1,00 | 209/747 (28,0 %) | **−987 $** [−2 537 $ ; +614 $] | −1 521 $ | −6 568 $ | +3 619 $ (18) |
| 5 s | (c) ordre passif −2 c, sinon immédiat | −0,69 | 890/912 (97,6 %) | **−5 674 $** [−11 939 $ ; −29 $] | −6 493 $ | −6 847 $ | +19 406 $ (56) | −0,68 | 735/747 (98,4 %) | **+109 $** [−2 884 $ ; +3 167 $] | −688 $ | −5 742 $ | +9 920 $ (31) |
| 5 s | (c) ordre passif −2 c, sinon rien | 2,00 | 214/912 (23,5 %) | **−2 691 $** [−5 265 $ ; −306 $] | −3 308 $ | −6 959 $ | +6 139 $ (20) | 2,00 | 141/747 (18,9 %) | **−314 $** [−1 415 $ ; +789 $] | −857 $ | −5 889 $ | +2 228 $ (15) |
| 5 s | (c) ordre passif −3 c, sinon immédiat | −0,58 | 890/912 (97,6 %) | **−4 686 $** [−10 174 $ ; +705 $] | −5 513 $ | −6 318 $ | +18 377 $ (54) | −0,62 | 735/747 (98,4 %) | **+122 $** [−3 040 $ ; +3 143 $] | −681 $ | −5 741 $ | +9 760 $ (30) |
| 5 s | (c) ordre passif −3 c, sinon rien | 3,00 | 178/912 (19,5 %) | **−1 699 $** [−3 826 $ ; +362 $] | −2 363 $ | −6 787 $ | +4 839 $ (18) | 3,00 | 103/747 (13,8 %) | **−378 $** [−1 283 $ ; +563 $] | −937 $ | −5 965 $ | +1 834 $ (11) |
| 5 s | (d) attente si P(baisse ≥ 1 c) > seuil (seuil 0,30) | 0,22 | 905/912 (99,2 %) · attend 476 | **−1 673 $** [−6 400 $ ; +3 029 $] | −2 554 $ | −4 739 $ | +15 309 $ (45) | −0,07 | 742/747 (99,3 %) · attend 519 | **+574 $** [−2 434 $ ; +3 363 $] | −113 $ | −5 340 $ | +9 199 $ (28) |
| 10 s | (c) ordre passif −1 c, sinon immédiat | −0,99 | 871/912 (95,5 %) | **−3 634 $** [−9 146 $ ; +1 698 $] | −4 410 $ | −5 873 $ | +17 665 $ (48) | −1,23 | 722/747 (96,7 %) | **−782 $** [−4 498 $ ; +2 769 $] | −1 534 $ | −6 382 $ | +10 460 $ (31) |
| 10 s | (c) ordre passif −1 c, sinon rien | 1,00 | 366/912 (40,1 %) | **−2 471 $** [−6 288 $ ; +1 255 $] | −3 217 $ | −6 387 $ | +9 102 $ (24) | 1,00 | 294/747 (39,4 %) | **−1 765 $** [−4 097 $ ; +395 $] | −2 309 $ | −7 346 $ | +5 324 $ (22) |
| 10 s | (c) ordre passif −2 c, sinon immédiat | −0,83 | 871/912 (95,5 %) | **−3 431 $** [−8 916 $ ; +1 918 $] | −4 222 $ | −5 655 $ | +17 451 $ (48) | −1,14 | 722/747 (96,7 %) | **−844 $** [−4 328 $ ; +2 519 $] | −1 603 $ | −6 442 $ | +10 263 $ (31) |
| 10 s | (c) ordre passif −2 c, sinon rien | 2,00 | 305/912 (33,4 %) | **−3 123 $** [−6 275 $ ; −77 $] | −3 739 $ | −6 797 $ | +7 973 $ (22) | 2,00 | 224/747 (30,0 %) | **−371 $** [−1 754 $ ; +1 066 $] | −968 $ | −5 970 $ | +3 403 $ (18) |
| 10 s | (c) ordre passif −3 c, sinon immédiat | −0,73 | 871/912 (95,5 %) | **−2 743 $** [−8 438 $ ; +2 733 $] | −3 541 $ | −5 461 $ | +16 785 $ (46) | −1,03 | 722/747 (96,7 %) | **−820 $** [−4 511 $ ; +2 545 $] | −1 586 $ | −6 426 $ | +10 096 $ (30) |
| 10 s | (c) ordre passif −3 c, sinon rien | 3,00 | 263/912 (28,8 %) | **−1 430 $** [−4 292 $ ; +1 245 $] | −2 094 $ | −5 771 $ | +6 285 $ (20) | 3,00 | 170/747 (22,8 %) | **−402 $** [−1 642 $ ; +804 $] | −1 010 $ | −5 989 $ | +2 854 $ (15) |
| 10 s | (d) attente si P(baisse ≥ 1 c) > seuil (seuil 0,15) | 0,52 | 870/912 (95,4 %) · attend 899 | **−244 $** [−4 452 $ ; +4 258 $] | −1 068 $ | −4 138 $ | +13 269 $ (35) | −0,60 | 722/747 (96,7 %) · attend 746 | **−381 $** [−3 685 $ ; +2 552 $] | −952 $ | −6 018 $ | +8 627 $ (26) |

### Attendre plutôt que couvrir tout de suite : gain par rapport à (b) immédiat

Comparaison directe sur les MÊMES positions et le même moment de déclenchement : la seule différence est l'attente. « Prix payé en moins » = prix de (b) − prix payé par la politique (moyenne, en cents, sur les positions couvertes par les deux ; positif = moins cher). Les ordres non remplis sont achetés au vendeur de la fin de l'attente (variantes « sinon immédiat » seulement : les variantes « sinon rien » ne couvrent presque pas et ne sont pas comparables).

« dont effet prix » = la part de Δ P&L due au seul prix payé (frais compris) sur les parts couvertes par les deux ; le reste vient de positions couvertes par l'une et pas l'autre (fin du cycle atteinte pendant l'attente, quantité affichée différente) — c'est-à-dire du hasard du résultat des positions laissées ouvertes, pas d'un achat moins cher.

| Déclencheur | Délai | Horizon | Politique | Valid. : prix payé en moins (c) · % moins cher · n | Δ P&L vs (b) [IC 90 %] | dont effet prix | Test : prix payé en moins (c) · % moins cher · n | Δ P&L vs (b) [IC 90 %] | dont effet prix |
|---|---|---|---|---|---|---|---|---|---|
| modèle −10 | 0 s | 0,25 s | (c) −1 c | −1,34 · 11,7 % · 394 | **−1 450 $** [−2 740 $ ; −315 $] | −266 $ | −1,20 · 13,7 % · 255 | **−124 $** [−408 $ ; +106 $] | −91 $ |
| modèle −10 | 0 s | 0,25 s | (c) −2 c | −1,34 · 11,7 % · 394 | **−1 450 $** [−2 684 $ ; −369 $] | −266 $ | −1,20 · 13,7 % · 255 | **−124 $** [−379 $ ; +115 $] | −91 $ |
| modèle −10 | 0 s | 0,25 s | (c) −3 c | −1,34 · 11,7 % · 394 | **−1 450 $** [−2 763 $ ; −289 $] | −266 $ | −1,20 · 13,7 % · 255 | **−124 $** [−403 $ ; +110 $] | −91 $ |
| modèle −10 | 0 s | 0,25 s | (d) seuil 0,05 | 0,03 · 1,0 % · 401 | **+2 $** [+0 $ ; +4 $] | +2 $ | −0,04 · 0,4 % · 257 | **−58 $** [−171 $ ; +0 $] | +1 $ |
| modèle −10 | 0 s | 0,5 s | (c) −1 c | −1,64 · 12,1 % · 388 | **−677 $** [−2 042 $ ; +535 $] | −296 $ | −1,28 · 15,1 % · 252 | **−196 $** [−507 $ ; +80 $] | −94 $ |
| modèle −10 | 0 s | 0,5 s | (c) −2 c | −1,62 · 12,1 % · 388 | **−675 $** [−2 029 $ ; +519 $] | −294 $ | −1,27 · 15,1 % · 252 | **−196 $** [−512 $ ; +82 $] | −94 $ |
| modèle −10 | 0 s | 0,5 s | (c) −3 c | −1,61 · 12,1 % · 388 | **−674 $** [−2 033 $ ; +559 $] | −293 $ | −1,27 · 15,1 % · 252 | **−196 $** [−510 $ ; +91 $] | −94 $ |
| modèle −10 | 0 s | 0,5 s | (d) seuil 0,20 | 0,04 · 0,7 % · 401 | **+1 $** [+0 $ ; +3 $] | +1 $ | 0,04 · 1,2 % · 257 | **−92 $** [−276 $ ; +0 $] | +1 $ |
| modèle −10 | 0 s | 1 s | (c) −1 c | −1,84 · 14,2 % · 381 | **−1 091 $** [−2 779 $ ; +509 $] | −268 $ | −1,41 · 18,7 % · 252 | **−186 $** [−430 $ ; +47 $] | −144 $ |
| modèle −10 | 0 s | 1 s | (c) −2 c | −1,80 · 14,2 % · 381 | **−1 068 $** [−2 774 $ ; +561 $] | −250 $ | −1,38 · 18,7 % · 252 | **−198 $** [−433 $ ; +30 $] | −140 $ |
| modèle −10 | 0 s | 1 s | (c) −3 c | −1,78 · 14,2 % · 381 | **−1 104 $** [−2 867 $ ; +548 $] | −240 $ | −1,37 · 18,7 % · 252 | **−210 $** [−457 $ ; +11 $] | −141 $ |
| modèle −10 | 0 s | 1 s | (d) seuil 0,30 | 0,06 · 0,7 % · 401 | **+2 $** [+0 $ ; +6 $] | +2 $ | 0,05 · 0,8 % · 257 | **−78 $** [−233 $ ; +0 $] | +0 $ |
| modèle −10 | 0 s | 3 s | (c) −1 c | −2,14 · 19,4 % · 377 | **−806 $** [−2 503 $ ; +902 $] | −475 $ | −1,52 · 22,2 % · 252 | **−874 $** [−1 824 $ ; −168 $] | −176 $ |
| modèle −10 | 0 s | 3 s | (c) −2 c | −2,10 · 18,0 % · 377 | **−106 $** [−1 791 $ ; +1 571 $] | −483 $ | −1,38 · 21,4 % · 252 | **−870 $** [−1 829 $ ; −157 $] | −135 $ |
| modèle −10 | 0 s | 3 s | (c) −3 c | −2,05 · 17,8 % · 377 | **−124 $** [−1 890 $ ; +1 481 $] | −470 $ | −1,36 · 21,0 % · 252 | **−878 $** [−1 818 $ ; −172 $] | −133 $ |
| modèle −10 | 0 s | 3 s | (d) seuil 0,40 | 0,03 · 0,2 % · 401 | **+3 $** [−0 $ ; +10 $] | +3 $ | 0,06 · 0,8 % · 257 | **−66 $** [−209 $ ; +13 $] | −2 $ |
| modèle −10 | 0 s | 5 s | (c) −1 c | −2,30 · 20,0 % · 370 | **−1 277 $** [−2 898 $ ; +334 $] | −540 $ | −1,27 · 31,0 % · 248 | **−233 $** [−1 322 $ ; +835 $] | −163 $ |
| modèle −10 | 0 s | 5 s | (c) −2 c | −2,25 · 17,6 % · 370 | **−841 $** [−2 554 $ ; +774 $] | −542 $ | −1,05 · 30,2 % · 248 | **−123 $** [−1 264 $ ; +970 $] | −57 $ |
| modèle −10 | 0 s | 5 s | (c) −3 c | −2,19 · 16,5 % · 370 | **−734 $** [−2 440 $ ; +978 $] | −512 $ | −1,04 · 29,0 % · 248 | **−117 $** [−1 215 $ ; +948 $] | −55 $ |
| modèle −10 | 0 s | 5 s | (d) seuil 0,30 | −0,25 · 3,2 % · 401 | **−82 $** [−605 $ ; +340 $] | −38 $ | 0,01 · 9,3 % · 257 | **−167 $** [−440 $ ; +76 $] | −17 $ |
| modèle −10 | 0 s | 10 s | (c) −1 c | −2,36 · 31,5 % · 356 | **−1 602 $** [−3 362 $ ; +96 $] | −375 $ | −1,16 · 31,1 % · 244 | **−238 $** [−1 161 $ ; +677 $] | −151 $ |
| modèle −10 | 0 s | 10 s | (c) −2 c | −2,28 · 30,3 % · 356 | **−1 634 $** [−3 483 $ ; +99 $] | −383 $ | −1,05 · 28,7 % · 244 | **−115 $** [−1 022 $ ; +751 $] | −140 $ |
| modèle −10 | 0 s | 10 s | (c) −3 c | −2,22 · 28,4 % · 356 | **−1 649 $** [−3 360 $ ; +45 $] | −373 $ | −1,05 · 27,9 % · 244 | **−99 $** [−964 $ ; +734 $] | −128 $ |
| modèle −10 | 0 s | 10 s | (d) seuil 0,15 | −1,16 · 20,8 % · 395 | **−1 649 $** [−3 414 $ ; −14 $] | −261 $ | −0,44 · 21,7 % · 249 | **+81 $** [−816 $ ; +924 $] | −129 $ |
| modèle −10 | 0,3 s | 0,25 s | (c) −1 c | −0,20 · 17,5 % · 388 | **+844 $** [+368 $ ; +1 429 $] | +6 $ | −0,06 · 17,1 % · 252 | **−72 $** [−282 $ ; +94 $] | +31 $ |
| modèle −10 | 0,3 s | 0,25 s | (c) −2 c | −0,20 · 17,5 % · 388 | **+844 $** [+352 $ ; +1 355 $] | +6 $ | −0,06 · 17,1 % · 252 | **−72 $** [−284 $ ; +107 $] | +31 $ |
| modèle −10 | 0,3 s | 0,25 s | (c) −3 c | −0,20 · 17,5 % · 388 | **+844 $** [+370 $ ; +1 372 $] | +6 $ | −0,06 · 17,1 % · 252 | **−72 $** [−273 $ ; +94 $] | +31 $ |
| modèle −10 | 0,3 s | 0,25 s | (d) seuil 0,05 | 0,02 · 0,5 % · 394 | **+0 $** [+0 $ ; +1 $] | +0 $ | 0,10 · 2,0 % · 255 | **−26 $** [−99 $ ; +18 $] | +20 $ |
| modèle −10 | 0,3 s | 0,5 s | (c) −1 c | −0,36 · 19,1 % · 382 | **+1 079 $** [+292 $ ; +1 950 $] | +45 $ | −0,11 · 19,0 % · 252 | **+53 $** [−65 $ ; +175 $] | +22 $ |
| modèle −10 | 0,3 s | 0,5 s | (c) −2 c | −0,34 · 19,1 % · 382 | **+1 089 $** [+330 $ ; +1 985 $] | +53 $ | −0,06 · 19,4 % · 252 | **+23 $** [−104 $ ; +156 $] | +28 $ |
| modèle −10 | 0,3 s | 0,5 s | (c) −3 c | −0,33 · 19,1 % · 382 | **+1 093 $** [+324 $ ; +1 982 $] | +53 $ | −0,06 · 19,4 % · 252 | **+23 $** [−103 $ ; +150 $] | +29 $ |
| modèle −10 | 0,3 s | 0,5 s | (d) seuil 0,20 | 0,02 · 0,8 % · 394 | **+0 $** [+0 $ ; +1 $] | +0 $ | 0,14 · 1,2 % · 255 | **−23 $** [−82 $ ; +12 $] | +22 $ |
| modèle −10 | 0,3 s | 1 s | (c) −1 c | −0,63 · 21,3 % · 381 | **+587 $** [−600 $ ; +1 740 $] | −16 $ | −0,21 · 25,0 % · 252 | **−111 $** [−450 $ ; +171 $] | −1 $ |
| modèle −10 | 0,3 s | 1 s | (c) −2 c | −0,61 · 20,5 % · 381 | **+648 $** [−534 $ ; +1 872 $] | −6 $ | −0,16 · 25,8 % · 252 | **−119 $** [−425 $ ; +146 $] | +13 $ |
| modèle −10 | 0,3 s | 1 s | (c) −3 c | −0,58 · 20,5 % · 381 | **+660 $** [−565 $ ; +1 871 $] | +3 $ | −0,14 · 25,8 % · 252 | **−122 $** [−446 $ ; +156 $] | +14 $ |
| modèle −10 | 0,3 s | 1 s | (d) seuil 0,30 | 0,05 · 0,8 % · 394 | **+3 $** [+0 $ ; +7 $] | +3 $ | 0,11 · 0,8 % · 255 | **−21 $** [−62 $ ; +0 $] | +19 $ |
| modèle −10 | 0,3 s | 3 s | (c) −1 c | −0,76 · 27,9 % · 377 | **+273 $** [−937 $ ; +1 537 $] | −144 $ | −0,18 · 28,2 % · 252 | **−676 $** [−1 546 $ ; −62 $] | −1 $ |
| modèle −10 | 0,3 s | 3 s | (c) −2 c | −0,73 · 26,5 % · 377 | **+765 $** [−510 $ ; +2 193 $] | −143 $ | −0,04 · 28,6 % · 252 | **−674 $** [−1 516 $ ; −39 $] | +38 $ |
| modèle −10 | 0,3 s | 3 s | (c) −3 c | −0,69 · 26,3 % · 377 | **+759 $** [−581 $ ; +2 268 $] | −129 $ | −0,01 · 28,6 % · 252 | **−704 $** [−1 492 $ ; −60 $] | +40 $ |
| modèle −10 | 0,3 s | 3 s | (d) seuil 0,40 | −0,01 · 0,3 % · 394 | **+2 $** [−2 $ ; +7 $] | +2 $ | 0,12 · 0,8 % · 255 | **−17 $** [−45 $ ; +0 $] | +20 $ |
| modèle −10 | 0,3 s | 5 s | (c) −1 c | −0,91 · 28,9 % · 370 | **+113 $** [−1 118 $ ; +1 444 $] | −172 $ | −0,05 · 37,2 % · 247 | **−394 $** [−1 457 $ ; +500 $] | +31 $ |
| modèle −10 | 0,3 s | 5 s | (c) −2 c | −0,87 · 26,8 % · 370 | **−19 $** [−1 314 $ ; +1 231 $] | −176 $ | 0,18 · 36,8 % · 247 | **−293 $** [−1 352 $ ; +679 $] | +149 $ |
| modèle −10 | 0,3 s | 5 s | (c) −3 c | −0,86 · 25,7 % · 370 | **+94 $** [−1 182 $ ; +1 421 $] | −182 $ | 0,18 · 36,0 % · 247 | **−288 $** [−1 425 $ ; +660 $] | +152 $ |
| modèle −10 | 0,3 s | 5 s | (d) seuil 0,30 | −0,07 · 6,3 % · 394 | **+115 $** [+3 $ ; +242 $] | −12 $ | 0,49 · 11,4 % · 255 | **−88 $** [−258 $ ; +69 $] | +93 $ |
| modèle −10 | 0,3 s | 10 s | (c) −1 c | −0,76 · 38,4 % · 354 | **−84 $** [−1 224 $ ; +1 105 $] | −6 $ | 0,19 · 35,7 % · 244 | **−169 $** [−960 $ ; +659 $] | +42 $ |
| modèle −10 | 0,3 s | 10 s | (c) −2 c | −0,67 · 37,3 % · 354 | **−128 $** [−1 285 $ ; +1 099 $] | +13 $ | 0,33 · 34,8 % · 244 | **−41 $** [−858 $ ; +794 $] | +63 $ |
| modèle −10 | 0,3 s | 10 s | (c) −3 c | −0,63 · 35,3 % · 354 | **−130 $** [−1 263 $ ; +1 056 $] | +14 $ | 0,33 · 34,0 % · 244 | **−27 $** [−803 $ ; +763 $] | +82 $ |
| modèle −10 | 0,3 s | 10 s | (d) seuil 0,15 | −0,18 · 28,2 % · 386 | **−135 $** [−1 255 $ ; +1 049 $] | +100 $ | 0,62 · 28,6 % · 248 | **+71 $** [−719 $ ; +888 $] | +117 $ |
| entrée + 30 s | 0 s | 0,25 s | (c) −1 c | 0,09 · 14,2 % · 909 | **+216 $** [−1 573 $ ; +2 126 $] | +148 $ | 0,02 · 16,9 % · 747 | **−80 $** [−1 047 $ ; +944 $] | +53 $ |
| entrée + 30 s | 0 s | 0,25 s | (c) −2 c | 0,09 · 14,2 % · 909 | **+216 $** [−1 455 $ ; +2 115 $] | +148 $ | 0,02 · 16,9 % · 747 | **−80 $** [−1 047 $ ; +926 $] | +53 $ |
| entrée + 30 s | 0 s | 0,25 s | (c) −3 c | 0,09 · 14,2 % · 909 | **+216 $** [−1 554 $ ; +2 121 $] | +148 $ | 0,02 · 16,9 % · 747 | **−80 $** [−1 063 $ ; +931 $] | +53 $ |
| entrée + 30 s | 0 s | 0,25 s | (d) seuil 0,05 | 0,21 · 4,2 % · 912 | **−55 $** [−497 $ ; +428 $] | +126 $ | 0,07 · 4,7 % · 747 | **+29 $** [−466 $ ; +569 $] | +24 $ |
| entrée + 30 s | 0 s | 0,5 s | (c) −1 c | −0,10 · 19,3 % · 909 | **+660 $** [−2 235 $ ; +4 413 $] | +125 $ | −0,16 · 19,4 % · 747 | **−242 $** [−1 289 $ ; +921 $] | +24 $ |
| entrée + 30 s | 0 s | 0,5 s | (c) −2 c | −0,03 · 19,3 % · 909 | **+639 $** [−2 315 $ ; +4 350 $] | +166 $ | −0,12 · 19,4 % · 747 | **−362 $** [−1 456 $ ; +794 $] | +42 $ |
| entrée + 30 s | 0 s | 0,5 s | (c) −3 c | 0,00 · 19,2 % · 908 | **+688 $** [−2 306 $ ; +4 544 $] | +190 $ | −0,11 · 19,4 % · 747 | **−359 $** [−1 535 $ ; +781 $] | +52 $ |
| entrée + 30 s | 0 s | 0,5 s | (d) seuil 0,20 | 0,30 · 2,4 % · 912 | **+63 $** [−230 $ ; +339 $] | +211 $ | 0,04 · 1,3 % · 747 | **−9 $** [−345 $ ; +388 $] | +22 $ |
| entrée + 30 s | 0 s | 1 s | (c) −1 c | −0,32 · 23,1 % · 909 | **−929 $** [−2 564 $ ; +710 $] | −108 $ | −0,27 · 24,6 % · 747 | **−31 $** [−1 475 $ ; +1 469 $] | −60 $ |
| entrée + 30 s | 0 s | 1 s | (c) −2 c | −0,25 · 22,8 % · 909 | **−566 $** [−2 275 $ ; +1 224 $] | −44 $ | −0,19 · 24,2 % · 747 | **−123 $** [−1 546 $ ; +1 370 $] | −20 $ |
| entrée + 30 s | 0 s | 1 s | (c) −3 c | −0,21 · 22,7 % · 908 | **−388 $** [−2 052 $ ; +1 329 $] | −17 $ | −0,14 · 24,2 % · 747 | **−60 $** [−1 522 $ ; +1 378 $] | +8 $ |
| entrée + 30 s | 0 s | 1 s | (d) seuil 0,30 | 0,27 · 2,0 % · 912 | **+222 $** [−82 $ ; +580 $] | +144 $ | 0,02 · 2,1 % · 747 | **−426 $** [−873 $ ; −33 $] | +2 $ |
| entrée + 30 s | 0 s | 3 s | (c) −1 c | −0,79 · 28,8 % · 903 | **−364 $** [−2 159 $ ; +1 454 $] | −371 $ | −0,72 · 31,4 % · 742 | **+422 $** [−1 035 $ ; +1 817 $] | −206 $ |
| entrée + 30 s | 0 s | 3 s | (c) −2 c | −0,69 · 27,9 % · 903 | **+253 $** [−1 663 $ ; +2 150 $] | −286 $ | −0,61 · 30,6 % · 742 | **+108 $** [−1 353 $ ; +1 516 $] | −140 $ |
| entrée + 30 s | 0 s | 3 s | (c) −3 c | −0,59 · 27,1 % · 902 | **+680 $** [−1 128 $ ; +2 515 $] | −220 $ | −0,52 · 30,2 % · 742 | **−4 $** [−1 422 $ ; +1 533 $] | −96 $ |
| entrée + 30 s | 0 s | 3 s | (d) seuil 0,40 | 0,16 · 4,5 % · 912 | **−310 $** [−1 144 $ ; +519 $] | +11 $ | −0,02 · 7,8 % · 747 | **+419 $** [−250 $ ; +1 086 $] | +38 $ |
| entrée + 30 s | 0 s | 5 s | (c) −1 c | −0,82 · 38,3 % · 892 | **−1 378 $** [−3 640 $ ; +603 $] | −200 $ | −0,77 · 35,6 % · 738 | **+231 $** [−897 $ ; +1 353 $] | −133 $ |
| entrée + 30 s | 0 s | 5 s | (c) −2 c | −0,69 · 36,4 % · 892 | **−1 038 $** [−3 318 $ ; +1 072 $] | −72 $ | −0,65 · 33,6 % · 738 | **+441 $** [−767 $ ; +1 743 $] | −44 $ |
| entrée + 30 s | 0 s | 5 s | (c) −3 c | −0,56 · 35,1 % · 891 | **−15 $** [−1 834 $ ; +1 806 $] | +17 $ | −0,58 · 32,5 % · 736 | **+584 $** [−800 $ ; +1 938 $] | +9 $ |
| entrée + 30 s | 0 s | 5 s | (d) seuil 0,30 | 0,27 · 18,0 % · 908 | **+2 208 $** [+697 $ ; +3 870 $] | +618 $ | −0,06 · 20,6 % · 744 | **+902 $** [−498 $ ; +2 447 $] | +139 $ |
| entrée + 30 s | 0 s | 10 s | (c) −1 c | −0,87 · 43,1 % · 872 | **+314 $** [−2 461 $ ; +3 078 $] | −237 $ | −1,25 · 41,3 % · 724 | **−864 $** [−2 511 $ ; +790 $] | −577 $ |
| entrée + 30 s | 0 s | 10 s | (c) −2 c | −0,68 · 41,1 % · 872 | **+626 $** [−2 144 $ ; +3 368 $] | −82 $ | −1,14 · 38,7 % · 724 | **−527 $** [−2 203 $ ; +1 044 $] | −560 $ |
| entrée + 30 s | 0 s | 10 s | (c) −3 c | −0,58 · 38,6 % · 871 | **+1 550 $** [−1 314 $ ; +4 368 $] | +51 $ | −1,06 · 36,6 % · 724 | **−575 $** [−2 255 $ ; +916 $] | −500 $ |
| entrée + 30 s | 0 s | 10 s | (d) seuil 0,15 | 0,64 · 31,5 % · 872 | **+4 201 $** [+1 190 $ ; +7 497 $] | +887 $ | −0,62 · 30,9 % · 724 | **−368 $** [−1 989 $ ; +1 233 $] | −511 $ |
| entrée + 30 s | 0,3 s | 0,25 s | (c) −1 c | 0,06 · 14,9 % · 907 | **+971 $** [−984 $ ; +3 470 $] | +154 $ | −0,10 · 13,8 % · 747 | **−280 $** [−1 097 $ ; +501 $] | −13 $ |
| entrée + 30 s | 0,3 s | 0,25 s | (c) −2 c | 0,06 · 14,9 % · 907 | **+978 $** [−1 035 $ ; +3 388 $] | +161 $ | −0,10 · 13,8 % · 747 | **−274 $** [−1 045 $ ; +520 $] | −9 $ |
| entrée + 30 s | 0,3 s | 0,25 s | (c) −3 c | 0,06 · 14,9 % · 907 | **+983 $** [−1 081 $ ; +3 353 $] | +165 $ | −0,10 · 13,8 % · 747 | **−273 $** [−1 080 $ ; +529 $] | −8 $ |
| entrée + 30 s | 0,3 s | 0,25 s | (d) seuil 0,05 | 0,12 · 3,9 % · 908 | **+365 $** [−206 $ ; +962 $] | +139 $ | −0,03 · 1,7 % · 747 | **+338 $** [−189 $ ; +906 $] | +11 $ |
| entrée + 30 s | 0,3 s | 0,5 s | (c) −1 c | −0,38 · 15,2 % · 907 | **−702 $** [−2 691 $ ; +1 078 $] | −130 $ | −0,25 · 16,2 % · 747 | **+309 $** [−453 $ ; +1 087 $] | −58 $ |
| entrée + 30 s | 0,3 s | 0,5 s | (c) −2 c | −0,32 · 16,2 % · 907 | **−834 $** [−2 760 $ ; +1 011 $] | −63 $ | −0,16 · 17,7 % · 747 | **+464 $** [−408 $ ; +1 361 $] | −5 $ |
| entrée + 30 s | 0,3 s | 0,5 s | (c) −3 c | −0,29 · 16,8 % · 907 | **−827 $** [−2 879 $ ; +971 $] | −25 $ | −0,13 · 17,8 % · 747 | **+554 $** [−288 $ ; +1 412 $] | +9 $ |
| entrée + 30 s | 0,3 s | 0,5 s | (d) seuil 0,20 | 0,16 · 1,4 % · 909 | **+317 $** [−38 $ ; +723 $] | +203 $ | 0,00 · 0,4 % · 747 | **+126 $** [−35 $ ; +312 $] | +7 $ |
| entrée + 30 s | 0,3 s | 1 s | (c) −1 c | −0,48 · 19,5 % · 906 | **−589 $** [−2 748 $ ; +1 387 $] | −381 $ | −0,43 · 19,6 % · 746 | **+527 $** [−1 235 $ ; +2 112 $] | −91 $ |
| entrée + 30 s | 0,3 s | 1 s | (c) −2 c | −0,40 · 20,9 % · 906 | **−393 $** [−2 328 $ ; +1 578 $] | −290 $ | −0,33 · 21,0 % · 746 | **+472 $** [−1 228 $ ; +2 138 $] | −31 $ |
| entrée + 30 s | 0,3 s | 1 s | (c) −3 c | −0,34 · 22,2 % · 906 | **−400 $** [−2 337 $ ; +1 586 $] | −232 $ | −0,27 · 21,6 % · 746 | **+517 $** [−1 274 $ ; +2 112 $] | +2 $ |
| entrée + 30 s | 0,3 s | 1 s | (d) seuil 0,30 | 0,13 · 2,3 % · 909 | **+175 $** [−114 $ ; +513 $] | +58 $ | 0,02 · 1,3 % · 747 | **+57 $** [−352 $ ; +427 $] | +10 $ |
| entrée + 30 s | 0,3 s | 3 s | (c) −1 c | −0,82 · 25,5 % · 901 | **−326 $** [−2 550 $ ; +1 852 $] | −279 $ | −0,75 · 26,5 % · 742 | **+342 $** [−1 001 $ ; +1 844 $] | −184 $ |
| entrée + 30 s | 0,3 s | 3 s | (c) −2 c | −0,72 · 26,1 % · 901 | **+117 $** [−2 272 $ ; +2 609 $] | −162 $ | −0,66 · 27,8 % · 742 | **+120 $** [−1 231 $ ; +1 584 $] | −100 $ |
| entrée + 30 s | 0,3 s | 3 s | (c) −3 c | −0,62 · 26,4 % · 901 | **+858 $** [−1 417 $ ; +3 206 $] | −86 $ | −0,57 · 27,9 % · 742 | **+31 $** [−1 418 $ ; +1 524 $] | −41 $ |
| entrée + 30 s | 0,3 s | 3 s | (d) seuil 0,40 | −0,00 · 3,9 % · 909 | **+121 $** [−593 $ ; +879 $] | +85 $ | −0,04 · 7,9 % · 747 | **−51 $** [−884 $ ; +769 $] | +9 $ |
| entrée + 30 s | 0,3 s | 5 s | (c) −1 c | −0,93 · 33,9 % · 889 | **−1 694 $** [−4 320 $ ; +1 007 $] | −403 $ | −0,82 · 32,5 % · 735 | **−57 $** [−1 622 $ ; +1 567 $] | −126 $ |
| entrée + 30 s | 0,3 s | 5 s | (c) −2 c | −0,78 · 33,9 % · 889 | **−1 537 $** [−4 068 $ ; +1 226 $] | −264 $ | −0,70 · 32,4 % · 735 | **+68 $** [−1 511 $ ; +1 712 $] | −18 $ |
| entrée + 30 s | 0,3 s | 5 s | (c) −3 c | −0,67 · 34,0 % · 889 | **−549 $** [−2 954 $ ; +2 015 $] | −162 $ | −0,64 · 31,3 % · 735 | **+81 $** [−1 512 $ ; +1 795 $] | +49 $ |
| entrée + 30 s | 0,3 s | 5 s | (d) seuil 0,30 | 0,19 · 17,8 % · 905 | **+2 464 $** [+840 $ ; +4 186 $] | +429 $ | −0,09 · 20,5 % · 742 | **+533 $** [−1 004 $ ; +2 181 $] | +264 $ |
| entrée + 30 s | 0,3 s | 10 s | (c) −1 c | −1,09 · 37,4 % · 870 | **+503 $** [−2 347 $ ; +3 704 $] | −580 $ | −1,26 · 36,0 % · 722 | **−823 $** [−2 602 $ ; +881 $] | −556 $ |
| entrée + 30 s | 0,3 s | 10 s | (c) −2 c | −0,92 · 37,4 % · 870 | **+705 $** [−2 195 $ ; +4 078 $] | −421 $ | −1,16 · 34,9 % · 722 | **−885 $** [−2 631 $ ; +856 $] | −543 $ |
| entrée + 30 s | 0,3 s | 10 s | (c) −3 c | −0,82 · 35,6 % · 870 | **+1 394 $** [−1 551 $ ; +4 514 $] | −270 $ | −1,06 · 35,2 % · 722 | **−862 $** [−2 438 $ ; +822 $] | −489 $ |
| entrée + 30 s | 0,3 s | 10 s | (d) seuil 0,15 | 0,49 · 30,5 % · 869 | **+3 893 $** [+635 $ ; +7 576 $] | +578 $ | −0,62 · 29,9 % · 722 | **−422 $** [−2 031 $ ; +1 293 $] | −349 $ |

### Sensibilité : règle de remplissage moins prudente (ordre −1 c, sinon immédiat, déclencheur modèle −10, délai 0)

Rempli dès que le meilleur vendeur enregistré touche notre prix (≤ limite) au lieu de passer 1 c dessous. C'est optimiste : il suppose que nous sommes servis dès que le prix touche, malgré la file d'attente.

| Horizon | Politique | Valid. : baisse captée (c) | remplis / déclenchés | P&L net en plus vs garder [IC 90 %] | sans top 5 | creux max (portefeuille) | gains sacrifiés (jackpots perdus) | Test : baisse captée (c) | remplis / déclenchés | P&L en plus vs garder [IC 90 %] | sans top 5 | creux max | gains sacrifiés (jackpots) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0,25 s | (c) −1 c, sinon immédiat — remplissage optimiste | −1,34 | 394/401 (98,3 %) | **−3 241 $** [−6 614 $ ; −225 $] | −3 439 $ | −8 286 $ | +6 343 $ (12) | −1,20 | 255/257 (99,2 %) | **−263 $** [−1 859 $ ; +1 062 $] | −427 $ | −6 063 $ | +1 743 $ (3) |
| 0,5 s | (c) −1 c, sinon immédiat — remplissage optimiste | −1,64 | 388/401 (96,8 %) | **−2 468 $** [−5 564 $ ; +442 $] | −2 664 $ | −7 873 $ | +5 900 $ (12) | −1,28 | 252/257 (98,1 %) | **−375 $** [−2 102 $ ; +1 157 $] | −531 $ | −6 157 $ | +1 905 $ (4) |
| 1 s | (c) −1 c, sinon immédiat — remplissage optimiste | −1,83 | 381/401 (95,0 %) | **−2 882 $** [−5 973 $ ; −102 $] | −3 079 $ | −8 117 $ | +6 139 $ (11) | −1,43 | 252/257 (98,1 %) | **−239 $** [−2 027 $ ; +1 193 $] | −396 $ | −6 039 $ | +1 893 $ (4) |
| 3 s | (c) −1 c, sinon immédiat — remplissage optimiste | −2,13 | 377/401 (94,0 %) | **−2 543 $** [−5 891 $ ; +452 $] | −2 794 $ | −8 268 $ | +6 147 $ (10) | −1,47 | 252/257 (98,1 %) | **−934 $** [−2 908 $ ; +724 $] | −1 088 $ | −6 727 $ | +2 426 $ (4) |
| 5 s | (c) −1 c, sinon immédiat — remplissage optimiste | −2,26 | 370/401 (92,3 %) | **−3 062 $** [−6 388 $ ; +20 $] | −3 289 $ | −8 406 $ | +6 617 $ (12) | −1,14 | 248/257 (96,5 %) | **−466 $** [−2 219 $ ; +1 156 $] | −644 $ | −6 280 $ | +2 239 $ (4) |
| 10 s | (c) −1 c, sinon immédiat — remplissage optimiste | −2,37 | 356/401 (88,8 %) | **−3 485 $** [−6 724 $ ; −522 $] | −3 700 $ | −8 509 $ | +6 991 $ (12) | −1,10 | 244/257 (94,9 %) | **−466 $** [−2 224 $ ; +1 070 $] | −639 $ | −6 273 $ | +2 231 $ (4) |

### Par stratégie — validation, délai 0 (P&L en plus vs garder)

| Stratégie | Déclencheur | Garder | (b) immédiat | (e) vendre la moitié | (c) −1 c 3 s sinon immédiat | (d) prédictif 3 s |
|---|---|---|---|---|---|---|
| désaccord 20 | modèle −10 | −228 $ | −1 037 $ | −572 $ | −1 555 $ | −1 037 $ |
| désaccord 20 | entrée + 30 s | −228 $ | −2 063 $ | −1 004 $ | −1 804 $ | −2 382 $ |
| V2-F original | modèle −10 | −711 $ | −1 008 $ | −543 $ | −1 346 $ | −1 008 $ |
| V2-F original | entrée + 30 s | −711 $ | −1 701 $ | −973 $ | −1 705 $ | −1 669 $ |
| désaccord 30 | modèle −10 | +1 388 $ | +167 $ | +114 $ | +296 $ | +170 $ |
| désaccord 30 | entrée + 30 s | +1 388 $ | −597 $ | −358 $ | −1 202 $ | −608 $ |
| V1 (0,55-0,56) | modèle −10 | −66 $ | +86 $ | +41 $ | +7 $ | +86 $ |
| V1 (0,55-0,56) | entrée + 30 s | −66 $ | +27 $ | +14 $ | +12 $ | +15 $ |

## 5. Coût total Up + Down des paires couvertes et profits verrouillés

Coût de la paire = prix d'entrée + prix payé pour le côté opposé (par part). Si < 1, la paire rapporte à coup sûr parts × (1 − coût) − frais des deux jambes ; si > 1 elle perd à coup sûr. Toutes stratégies additionnées, délai 0.

| Déclencheur | Politique | Période | Paires | Coût 10 % | médiane | 90 % | Paires < 1 | Profit verrouillé (paires < 1) | Perte verrouillée (paires > 1) | Net verrouillé |
|---|---|---|---|---|---|---|---|---|---|---|
| modèle −10 | (b) immédiat | apprentissage | 391 | 0,99 | 1,09 | 1,17 | 43 (11,0 %) | +46 $ | −5 148 $ | **−5 113 $** |
| modèle −10 | (b) immédiat | validation | 401 | 1,04 | 1,10 | 1,19 | 14 (3,5 %) | +37 $ | −6 226 $ | **−6 191 $** |
| modèle −10 | (b) immédiat | inédit | 257 | 1,05 | 1,15 | 1,23 | 8 (3,1 %) | +49 $ | −4 894 $ | **−4 846 $** |
| modèle −10 | (c) −1 c 3 s, sinon immédiat | apprentissage | 367 | 1,03 | 1,10 | 1,18 | 23 (6,3 %) | +17 $ | −7 155 $ | **−7 138 $** |
| modèle −10 | (c) −1 c 3 s, sinon immédiat | validation | 377 | 1,05 | 1,12 | 1,21 | 8 (2,1 %) | +32 $ | −8 386 $ | **−8 366 $** |
| modèle −10 | (c) −1 c 3 s, sinon immédiat | inédit | 252 | 1,06 | 1,16 | 1,24 | 7 (2,8 %) | +147 $ | −5 680 $ | **−5 533 $** |
| modèle −10 | (c) −3 c 10 s, sinon immédiat | apprentissage | 332 | 1,01 | 1,11 | 1,19 | 28 (8,4 %) | +255 $ | −6 181 $ | **−5 927 $** |
| modèle −10 | (c) −3 c 10 s, sinon immédiat | validation | 356 | 1,04 | 1,12 | 1,22 | 14 (3,9 %) | +6 $ | −8 053 $ | **−8 047 $** |
| modèle −10 | (c) −3 c 10 s, sinon immédiat | inédit | 244 | 1,06 | 1,16 | 1,24 | 10 (4,1 %) | +159 $ | −5 490 $ | **−5 332 $** |
| modèle −10 | (d) prédictif 3 s | apprentissage | 391 | 0,99 | 1,09 | 1,17 | 43 (11,0 %) | +53 $ | −5 167 $ | **−5 126 $** |
| modèle −10 | (d) prédictif 3 s | validation | 401 | 1,04 | 1,10 | 1,19 | 14 (3,5 %) | +40 $ | −6 226 $ | **−6 188 $** |
| modèle −10 | (d) prédictif 3 s | inédit | 257 | 1,05 | 1,15 | 1,23 | 8 (3,1 %) | +148 $ | −4 902 $ | **−4 755 $** |
| entrée + 30 s | (b) immédiat | apprentissage | 751 | 0,68 | 1,01 | 1,15 | 335 (44,6 %) | +6 054 $ | −6 551 $ | **−511 $** |
| entrée + 30 s | (b) immédiat | validation | 912 | 0,75 | 1,03 | 1,14 | 327 (35,9 %) | +5 774 $ | −8 992 $ | **−3 260 $** |
| entrée + 30 s | (b) immédiat | inédit | 747 | 0,81 | 1,04 | 1,14 | 229 (30,7 %) | +3 185 $ | −6 014 $ | **−2 895 $** |
| entrée + 30 s | (c) −1 c 3 s, sinon immédiat | apprentissage | 720 | 0,67 | 1,02 | 1,16 | 306 (42,5 %) | +6 388 $ | −6 437 $ | **−85 $** |
| entrée + 30 s | (c) −1 c 3 s, sinon immédiat | validation | 903 | 0,75 | 1,04 | 1,15 | 301 (33,3 %) | +5 907 $ | −9 952 $ | **−4 119 $** |
| entrée + 30 s | (c) −1 c 3 s, sinon immédiat | inédit | 742 | 0,82 | 1,04 | 1,14 | 215 (29,0 %) | +4 023 $ | −6 675 $ | **−2 698 $** |
| entrée + 30 s | (c) −3 c 10 s, sinon immédiat | apprentissage | 660 | 0,64 | 1,01 | 1,16 | 299 (45,3 %) | +7 452 $ | −6 122 $ | **+1 311 $** |
| entrée + 30 s | (c) −3 c 10 s, sinon immédiat | validation | 871 | 0,72 | 1,04 | 1,15 | 301 (34,6 %) | +6 967 $ | −9 102 $ | **−2 181 $** |
| entrée + 30 s | (c) −3 c 10 s, sinon immédiat | inédit | 724 | 0,81 | 1,04 | 1,15 | 210 (29,0 %) | +3 453 $ | −6 773 $ | **−3 368 $** |
| entrée + 30 s | (d) prédictif 3 s | apprentissage | 749 | 0,65 | 1,01 | 1,15 | 333 (44,5 %) | +6 019 $ | −6 445 $ | **−441 $** |
| entrée + 30 s | (d) prédictif 3 s | validation | 912 | 0,75 | 1,03 | 1,14 | 328 (36,0 %) | +5 789 $ | −8 983 $ | **−3 233 $** |
| entrée + 30 s | (d) prédictif 3 s | inédit | 747 | 0,81 | 1,04 | 1,14 | 230 (30,8 %) | +3 449 $ | −5 922 $ | **−2 553 $** |

Ce tableau ne compte que la partie couverte ; la partie non couverte (quantité affichée insuffisante) reste exposée et figure dans le P&L de la section 4.

## 6. Ce qui ne peut pas être mesuré avec les données actuelles

- **Profondeur du carnet opposé** : seuls le meilleur prix et sa taille sont enregistrés (r[6]/r[10] ou r[4]/r[8]). Impossible de savoir à quel prix moyen on couvrirait 80-100 parts quand le meilleur niveau n'en affiche que 20.
- **File d'attente et transactions réelles** : aucune transaction Polymarket (prix, taille, côté) ni position dans la file ; le remplissage d'un ordre passif est donc déduit du seul meilleur vendeur — d'où la règle prudente « 1 c dessous ».
- **Sous-seconde** : cadence réelle 0,3 s ; les horizons 0,25 s et 0,5 s sont approximatifs. Les photos 100 ms ne couvrent que ~20 s autour du premier désaccord de chaque cycle.
- **Heure des événements** : toutes les lignes sont horodatées à la réception par le bot ; la latence propre à chaque source n'est pas séparable.
- **Notre propre impact** : un achat de couverture retire la liquidité affichée ; le rejeu suppose qu'elle était toute disponible pour nous.
- **Frais teneur d'ordre** : comptés comme frais preneur (prudent).

### Ce que le programme du VPS de Dublin (bot95/rapide/rapide.js) devrait enregistrer en direct

1. Après chaque position ouverte (réelle ou fantôme) : **le carnet complet du côté opposé** (tous les niveaux vendeurs et acheteurs, prix + taille) **toutes les 50 ms** jusqu'à la fin du cycle, horodaté à la réception ET avec l'horodatage du message Polymarket.
2. **Toutes les transactions** Polymarket des deux jetons du cycle (prix, taille, côté preneur, horodatage du serveur) — indispensable pour savoir si un ordre passif aurait été servi.
3. Les **événements du carnet** (ajout / retrait / modification à chaque niveau) pour reconstruire la file d'attente à notre prix.
4. Pour un vrai test : un **ordre passif fantôme** posé en direct (1 part, côté opposé, vendeur − 1 c) et son sort réel (rempli / quand / combien), plus le temps aller-retour de nos ordres.
5. Les mêmes 5 prix de bourses au même rythme 50 ms pendant ces fenêtres (pour les variables de décision).

Durée de calcul : 82 s.