# Bot95 — H1088 : filtres d'exécution en direct (fantômes BTC, 13.10 soir → 14.10 17 h)

## Verdict

**Rien n'est démontré.** Sur ~20 heures de trades fantômes, aucune famille de filtres n'a un écart « gardés moins écartés » dont l'intervalle de confiance à 90 % exclut 0. Les intervalles font ±60 à ±100 points de ROI : avec un seul jour de données et des gains très concentrés sur quelques billets (achats à moins de 0,10 qui gagnent), on ne peut pas encore séparer un vrai effet du hasard.

Ce qu'on peut dire honnêtement :

- **Les familles basées sur l'exécution (carnet, écart serré) vont dans le sens de ta thèse** : ROI des trades gardés supérieur à celui des écartés (+21 à +39 points), mais IC tous à cheval sur 0, et ça ne tient que sur la journée du 14.10 (le soir du 13.10 va dans l'autre sens pour « + carnet »). Une fois les billets retirés, l'avantage fond (+1 à +18 points).
- **« + ecart serre » ne reproduit pas l'étude H1074** : les trades écartés (écart > 1 c, 17 % des trades) ont gagné **+21 %** ce jour-là (+1 513 $), alors qu'H1074 les voyait perdre −47 à −48 %. Le filtre reste devant (+27 pts) mais il n'y a pas de pertes évitées.
- **« + calme » et « + ecart carnet calme » font moins bien que la base** (−21 et −4 pts) le 14.10.
- **« + contre foule » / « + foule bybit »** : peu de différence en groupé (+8 à +10 pts), mais 19 stratégies sur 30 améliorées et +49 à +55 pts en poids égal — signe intéressant, IC toujours à cheval sur 0.
- Aucune recommandation de passage en réel. Continuer à laisser tourner les fantômes : il faut plusieurs jours pour conclure.

## Données et méthode

- Sauvegarde du 14.10 15:14 UTC (dernier trade fermé 15:01 UTC = 17:01 heure suisse). 36 stratégies de base BTC ont des copies ; 9 familles.
- Pour chaque stratégie S et famille F : **gardés** = trades de S présents dans la copie « S + F » (jointure par heure d'entrée et côté) ; **écartés** = trades de S absents de la copie. Période : depuis le premier trade de la famille (13.10 21:46 heure suisse pour « + carnet », 14.10 00:31 pour « foule bybit »). 0 trade de copie sans trade de base correspondant.
- Pour les trades gardés on prend le P&L de la copie (identique à la base, sauf « x2 » où la mise est doublée moins le surcoût mesuré). Mise = prix × parts ; ROI = P&L total / mise totale.
- IC 90 % : bootstrap sur les **cycles de 5 min** (3 000 tirages), toutes stratégies ensemble — les stratégies tradent souvent les mêmes cycles, donc tirer les trades un par un serait trop optimiste.
- « Poids égal » : moyenne sur les stratégies (≥ 5 gardés et ≥ 5 écartés) de leur écart de ROI, pour qu'une stratégie à grosses mises ne domine pas.
- « Stratégies améliorées » : nombre de stratégies où le ROI des gardés dépasse celui des écartés (sur celles qui ont ≥ 5 + 5 trades).

## Résultats par famille (toute la période)

| Famille | n gardés / écartés | Gagnés gardés / écartés | ROI gardés / écartés | P&L gardés / écartés | Écart ROI, IC 90 % | Écart P&L par trade, IC 90 % | Écart ROI poids égal, IC 90 % | Stratégies améliorées | Part des 10 plus gros gains |
|---|---|---|---|---|---|---|---|---|---|
| + carnet | 1147 / 936 | 37 % / 31 % | +57 % / +36 % | +17 695 $ / +12 482 $ | +21 pts [−40 ; +87] | +2,1 $ [−18 ; +23] | +17 pts [−56 ; +98] | 15/34 | 51 % |
| + carnet pression | 726 / 1241 | 39 % / 32 % | +70 % / +32 % | +13 149 $ / +13 801 $ | +39 pts [−41 ; +138] | +7,0 $ [−15 ; +34] | +44 pts [−51 ; +144] | 18/30 | 68 % |
| + carnet ecart serre | 894 / 1003 | 36 % / 34 % | +64 % / +34 % | +17 294 $ / +11 360 $ | +29 pts [−36 ; +104] | +8,0 $ [−13 ; +32] | +25 pts [−54 ; +116] | 14/31 | 52 % |
| + ecart serre | 1598 / 338 | 33 % / 42 % | +49 % / +21 % | +26 348 $ / +1 513 $ | +27 pts [−48 ; +102] | +12,0 $ [−7 ; +31] | +30 pts [−56 ; +112] | 16/24 | 34 % |
| + calme | 860 / 1066 | 35 % / 35 % | +35 % / +56 % | +9 857 $ / +18 455 $ | −21 pts [−97 ; +49] | −5,9 $ [−30 ; +16] | −6 pts [−91 ; +89] | 14/31 | 35 % |
| + contre foule | 1038 / 882 | 28 % / 44 % | +52 % / +41 % | +17 161 $ / +11 316 $ | +10 pts [−58 ; +74] | +3,7 $ [−18 ; +24] | +55 pts [−29 ; +129] | 19/30 | 52 % |
| + ecart carnet calme | 494 / 1393 | 37 % / 35 % | +45 % / +49 % | +7 179 $ / +21 454 $ | −4 pts [−78 ; +70] | −0,9 $ [−24 ; +22] | +18 pts [−75 ; +116] | 14/29 | 49 % |
| + foule bybit | 733 / 968 | 29 % / 43 % | +63 % / +56 % | +15 134 $ / +16 325 $ | +8 pts [−58 ; +79] | +3,8 $ [−18 ; +27] | +49 pts [−38 ; +126] | 19/30 | 56 % |
| + foule bybit x2 | 733 / 968 | 29 % / 43 % | +63 % / +56 % | +29 425 $ / +16 325 $ | +7 pts [−65 ; +81] | +23,3 $ [−20 ; +72] | +51 pts [−39 ; +128] | 19/30 | 58 % |

Lecture : « + carnet » a gardé 1 147 trades (ROI +57 %) et écarté 936 (ROI +36 %). L'écart de +21 points a un IC de −40 à +87 : il peut très bien être nul ou négatif.

Remarques :
- La base entière a été très gagnante ce jour-là (≈ +30 000 $ sur ≈ 2 000 trades, toutes stratégies cumulées), surtout grâce à quelques billets à 0,04–0,30 qui ont gagné (un seul trade fait +1 595 $). La moitié environ du P&L des gardés vient de 10 trades.
- « x2 » : même sélection que « foule bybit », P&L presque doublé (le surcoût de doubler a été faible), ROI identique. Doubler la mise ne crée pas d'avantage, il double aussi le risque.
- Les filtres « contre foule » baissent fortement le taux de gain (28 % contre 44 %) : ils gardent surtout des achats bon marché qui gagnent rarement mais gros.

## Stabilité par jour (heure suisse) et sans billets

Chaque case : ROI gardés / écartés, écart avec IC 90 %, stratégies améliorées.

| Famille | 13.10 soir (21–24 h) | 14.10 (00–17 h) | Toute la période, sans billets (prix < 0,10) |
|---|---|---|---|
| + carnet | −36 % / +35 %, −71 pts [−178 ; +20], 5/12 | +73 % / +36 %, +37 pts [−33 ; +118], 16/29 | +50 % / +34 %, +16 pts [−32 ; +72], 14/32 |
| + carnet pression | −36 % / −44 %, +8 pts [−65 ; +94], 2/2 | +87 % / +40 %, +47 pts [−42 ; +157], 19/29 | +45 % / +45 %, +1 pt [−60 ; +65], 15/29 |
| + carnet ecart serre | −30 % / −6 %, −24 pts [−126 ; +51], — | +73 % / +38 %, +35 pts [−34 ; +114], 17/31 | +57 % / +45 %, +12 pts [−45 ; +69], 11/29 |
| + ecart serre | −33 % / −28 %, −5 pts [−82 ; +79], — | +57 % / +30 %, +26 pts [−57 ; +111], 15/23 | +49 % / +32 %, +18 pts [−60 ; +90], 15/23 |
| + calme | +41 % / −85 %, +126 pts [+14 ; +230], 2/3 | +35 % / +70 %, −36 pts [−115 ; +41], 12/30 | +41 % / +56 %, −15 pts [−76 ; +52], 11/30 |
| + contre foule | −48 % / +2 %, −50 pts [−190 ; +44], — | +61 % / +45 %, +16 pts [−53 ; +90], 20/30 | +53 % / +45 %, +8 pts [−50 ; +68], 21/30 |
| + ecart carnet calme | +67 % / −41 %, +108 pts [−44 ; +295], — | +44 % / +57 %, −13 pts [−92 ; +70], 11/26 | +50 % / +51 %, −1 pt [−70 ; +77], 14/28 |
| + foule bybit | pas encore en ligne | +63 % / +56 %, +8 pts [−60 ; +75], 19/30 | +57 % / +66 %, −10 pts [−83 ; +60], 17/30 |
| + foule bybit x2 | pas encore en ligne | +63 % / +56 %, +7 pts [−63 ; +74], 19/30 | +56 % / +66 %, −10 pts [−82 ; +57], 18/30 |

« — » : aucune stratégie n'avait 5 trades gardés et 5 écartés sur ces 3 heures. Le soir du 13.10 ne compte que 130 à 320 trades par famille ; le seul IC qui exclut 0 (« + calme », +126 pts) s'inverse le lendemain (−36 pts) : c'est du bruit. Aucune famille n'est du même côté les deux jours avec un IC hors de 0.

## Les 10 meilleures paires (stratégie, famille) — exploratoire

Classées par P&L des trades gardés, avec au moins 30 trades gardés. **À ne pas prendre comme des résultats** : 9 familles × 36 stratégies = plus de 300 paires regardées ; les meilleures sont mécaniquement chanceuses.

| # | Stratégie | Famille | n gardés / base | P&L gardés (ROI) | P&L base entière | ROI écartés |
|---|---|---|---|---|---|---|
| 1 | corrige marge mesuree : V2-F | + foule bybit x2 | 30 / 85 | +3 202 $ (+182 %) | +3 802 $ | +36 % |
| 2 | corrige : V2-F ecart qui grandit | + carnet | 41 / 98 | +2 884 $ (+245 %) | +3 998 $ | +52 % |
| 3 | corrige : desaccord 20 | + carnet | 42 / 99 | +2 880 $ (+243 %) | +4 131 $ | +59 % |
| 4 | corrige : V2-F ecart qui grandit | + carnet ecart serre | 30 / 91 | +2 710 $ (+285 %) | +2 850 $ | +7 % |
| 5 | corrige : desaccord 20 | + ecart serre | 66 / 93 | +2 679 $ (+112 %) | +2 931 $ | +39 % |
| 6 | corrige : V2-F ecart qui grandit | + ecart serre | 67 / 92 | +2 639 $ (+109 %) | +2 798 $ | +26 % |
| 7 | corrige : V2-F + pas les deux baissent | + carnet | 47 / 98 | +2 637 $ (+185 %) | +3 936 $ | +65 % |
| 8 | corrige : V2-F + pas les deux baissent | + ecart serre | 66 / 91 | +2 637 $ (+107 %) | +2 792 $ | +25 % |
| 9 | corrige : V2-F + pas les deux baissent | + carnet ecart serre | 34 / 90 | +2 533 $ (+225 %) | +2 844 $ | +16 % |
| 10 | corrige marge mesuree : V2-F | + carnet | 47 / 103 | +2 091 $ (+151 %) | +2 220 $ | +7 % |

Ce sont toutes des stratégies « corrige » qui achètent souvent bon marché ; leur base entière est déjà très gagnante ce jour-là. Dans aucun cas la copie ne gagne plus que la base entière (le filtre enlève des trades globalement gagnants), même si son ROI est plus élevé.

## Copies « sans 02-10h » (depuis le 14.10 15:00, trop récentes)

5 copies ont déjà des trades fermés (1 à 5 trades chacune) : V2-C perp (4 trades, +102 $), V2-F miroir 1 s (2, +78 $), corrige marge mesuree : V2-F (5, +1 797 $), desaccord 20 Binance ou perp avec nous sans nuit (3, +466 $), desaccord 30 0,15-0,60 + perp + ecart qui grandit (1, −8 $). Les 4 autres n'ont pas encore de trade. Rien à en tirer.

## Limites

- **Environ 20 heures de données** (≈ 160 cycles de 5 min). C'est très peu : les IC sont énormes.
- **Comparaisons multiples** : 9 familles, 3 découpages, 36 stratégies. Même si un IC excluait 0, il faudrait le confirmer sur des jours neufs.
- **Stratégies très corrélées** : elles tradent les mêmes cycles. Le bootstrap par cycle en tient compte, mais 36 stratégies ne valent pas 36 observations indépendantes.
- **Gains concentrés** : 34 à 68 % du P&L des gardés vient de 10 trades (billets gagnants). Un seul billet de plus ou de moins change le classement.
- **Fantômes** : prix et quantités supposés remplis au carnet affiché ; les gros achats de billets (jusqu'à 1 600 parts) n'auraient peut-être pas été servis entièrement en réel.
- Mise = prix × parts ; pour les quelques stratégies à deux jambes, c'est une approximation.
- Une centaine de trades (sur 12 000, toutes stratégies) ne sont que dans l'archive compacte, sans nombre de parts : pour ceux-là la mise est reprise du trade de base quand il existe.

Script : `etude/bot5min/execution_filtres_live_h1088.py` (lit `bot95/sauvegarde/*.json`, aucune modification du bot).
