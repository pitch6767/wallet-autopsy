# BOT95 HEDGE LAB V1 — 24 couvertures contre GARDER, deux cohortes, trois scénarios d'exécution

Étude hors ligne du 11.10.2026 — aucun bot, aucun workflow, aucun fichier du bot modifié ; rien n'est publié. 1146 cycles BTC 5 min réglés (07.10 08:00 → 11.10 07:55, heure suisse). Apprentissage 455 cycles (< 08.10 22:00) · validation 433 (→ 10.10 10:25) · test inédit 258 cycles seulement (après 10.10 10:25).

## Verdict (en tête)

- **Audit / teneur d'ordre** : une simulation passive crédible n'est **pas possible** — position dans la file non observable, transactions seulement agrégées (1 s partout, 100 ms dans ~20 s de photo par cycle), pas d'horodatage Polymarket. Selon l'hypothèse, 28,9 % (pessimiste) à 41,3 % (idéal) des ordres passifs de sauvetage seraient servis : les résultats passifs sont des bornes, pas des mesures. Latence Dublin : pas encore de données.
- **Structure décisive** : les carnets Up et Down sont miroirs (vendeur opposé = 1 − acheteur de notre côté, même taille) et les frais sont symétriques. Acheter l'opposé = vendre sa position au même prix, en immobilisant le capital jusqu'au règlement. Toute couverture « au marché » est une sortie partielle déguisée : elle ne crée pas d'espérance, elle échange du gain potentiel (jackpots) contre une perte plus petite. Une « paire < 1 » n'existe que quand notre côté a déjà monté : c'est une prise de bénéfice.
- **A · désaccord 30 zone + modèle monte** — GARDER prudent (délai 0,3 s) : validation −293 $ sur 37 positions, test −411 $ sur 34 (idéal : +753 $ / +273 $). Portefeuille 250 $ : ruiné en validation après 21 positions et en test après 30 — le classement 250 $ imposé (top 5 : H01 +108 $, H06 +108 $, H24 +69 $, H14 +1 $, H12 +1 $) ne mesure que la date de la ruine. Classement 50 $ indépendants (top 5, Δ valid. [IC 90 %] → test) : H24 +112 $ [−54 $ ; +291 $] → −30 $ ; H09 +5 $ [−100 $ ; +110 $] → −5 $ ; H18 +0 $ [+0 $ ; +0 $] → +0 $ ; H02 −4 $ [−146 $ ; +129 $] → −3 $ ; H03 −14 $ [−311 $ ; +264 $] → −6 $. **Aucune couverture ne bat GARDER de façon démontrée** (IC 90 % validation entièrement > 0 ET test > 0), ni en 250 $ ni en 50 $ indépendants.
- **B · V2-F corrigé 0,015 %** — GARDER prudent (délai 0,3 s) : validation −70 $ sur 144 positions, test −1 583 $ sur 112 (idéal : +926 $ / −304 $). Portefeuille 250 $ : ruiné en validation après 141 positions et en test après 16 — le classement 250 $ imposé (top 5 : H23 +0 $, H19 +0 $, H08 +0 $, H18 +0 $, H09 +0 $) ne mesure que la date de la ruine. Classement 50 $ indépendants (top 5, Δ valid. [IC 90 %] → test) : H18 +0 $ [+0 $ ; +0 $] → +0 $ ; H11 −242 $ [−548 $ ; +57 $] → −8 $ ; H02 −245 $ [−547 $ ; +41 $] → +182 $ ; H24 −288 $ [−780 $ ; +198 $] → −56 $ ; H05 −304 $ [−727 $ ; +81 $] → +244 $. **Aucune couverture ne bat GARDER de façon démontrée** (IC 90 % validation entièrement > 0 ET test > 0), ni en 250 $ ni en 50 $ indépendants.
- **Les quatre candidates (prudent, 50 $ indépendants, Δ vs GARDER valid. → test)** : H10 A −35 $ → −28 $, B −954 $ → +902 $ ; H17 A −35 $ → −28 $, B −948 $ → +908 $ ; H21 A −47 $ → −30 $, B −833 $ → +843 $ ; H23 A −24 $ → −166 $, B −364 $ → +280 $. H10 = vendre (miroir) ; H17 et H21 retombent presque toujours sur l'immédiat (= vendre au déclencheur) ; H23 = prise de bénéfice puis pari sur le retour. Détail section 4.
- Sorties après « modèle −10 » (H10, H12-H17, H20-H22) : négatives sur la validation, positives sur le test pour B — le signe s'inverse d'une période à l'autre : rien de stable. Ne jamais lire une baisse du creux comme une victoire : chaque ligne donne aussi les jackpots gardés et le profit sacrifié.

## 1. Audit des données et de la simulation « teneur d'ordre » (maker)

| Donnée | État | Période | Résolution / détail |
|---|---|---|---|
| Carnets Up + Down synchronisés (même ligne) | **disponible** | 07.10 08:00 → 11.10 07:55 | 750788 lignes ; intervalle 5 % 0,30 s · médiane 0,30 s · 95 % 0,30 s · 99 % 0,31 s. Up et Down sont dans la MÊME ligne (même horodatage de réception). |
| Meilleur acheteur / meilleur vendeur | **disponible** | idem | r[3]-r[6], à chaque ligne. Carnets **miroirs** : vendeur Down = 1 − acheteur Up et même taille sur 100,0 % des 750788 lignes vérifiées (miroir fait par Polymarket ou par l'enregistreur : non distinguable ; toutes les couvertures en dépendent). |
| Quantité au meilleur niveau | **disponible** | idem | r[7]-r[10] (parts). |
| Profondeur par niveau | **partielle** | photos 100 ms : 748 cycles, 07.10 15:40 → 10.10 15:05 ; carnets 8 niveaux : 601 signaux TWAP, 10.10 01:33 → 11.10 08:38 | 3 meilleurs niveaux des deux côtés seulement dans les photos 100 ms (~10 s avant → 10 s après le premier désaccord de chaque cycle) ; 8 niveaux seulement aux signaux TWAP (autres stratégies). Au-delà du meilleur niveau : **absent** pour nos positions. |
| Transactions et annulations | **partielles (agrégées)** | flux 1 s : 07.10 10:49 → 11.10 07:50 (sig_BTC) ; flux 100 ms : photos | Sommes en $ par jeton et par intervalle : retraits / ajouts côté acheteur et vendeur, échanges côté « achat » et « vente » (côté du message last_trade_price). **Ni prix, ni taille individuelle, ni identité de l'ordre**. On peut en déduire : qu'il y a eu des échanges (et combien de $) dans la seconde ou les 100 ms ; si un niveau a été vidé par des retraits plutôt que par des échanges. On ne peut PAS en déduire : à quel prix l'échange a eu lieu, s'il a touché NOTRE niveau, la position dans la file, ni si un ordre précis a été servi. Seulement 57,5 % des secondes ont un échange côté Up (médiane des secondes non nulles : 14 $) ; photos 100 ms : 30,8 % des pas ont un échange. |
| Horodatage de réception local | **disponible** | tout | heure de réception par le bot (Cloudflare), pour toutes les sources. |
| Horodatage de l'échange (bourse / Polymarket) | **absent** | — | non enregistré dans les lignes ; impossible de séparer latence réseau et mouvement réel. |
| Frais preneur | **connus** | — | 0,072 · p · (1 − p) par part, à l'achat ET à la vente au meilleur acheteur (symétrique : identique pour p et 1 − p). |
| Frais teneur d'ordre | **non vérifiés** | — | supposés 0 (hypothèse de Pitch) ; non vérifiés sur les marchés crypto 5 min. |
| Remplissages initiaux (exécution réelle) | **absents** | — | les fantômes réels « achètent » au prix vu ; aucun remplissage réel sur le carnet. |
| Résultats officiels | **disponibles** | 1146 cycles | officiels.json (cycles sans résultat exclus). |
| Fusion Up + Down → 1 $ (merge) | **non observable** | — | transaction on-chain CTF, absente des données ; comptée 1 $ au règlement ; capital libéré plus tôt seulement dans le scénario idéal. |
| Historique des prix des bourses | **disponible** | tout | Bybit, OKX, Coinbase, Binance, Chainlink à chaque ligne 0,3 s (100 ms dans les photos ; changements réels tous les ~0,4-0,9 s). |
| Probabilités du modèle corrigé (0,015 %) | **reconstruites** | tout | X15 = modèle reconstruit (méthode X d'attribution_001, sdRel = 1,5e-4) ; le fantôme réel calcule H15 (moteur du bot, même sdRel) ; accord ci-dessous. |
| Latence VPS Dublin (bot95/rapide.json) | **pas encore** | — | fichier présent mais vide (0 signal, état None). |

**Accord de la cohorte B avec le fantôme réel « corrige : V2-F ecart qui grandit » BTC** (cycles réglés 09.10 08:45 → 11.10 08:30) :

| Reconstruction | Cycles de la période | Achats fantôme réel | Achats rejeu | Cycles communs | Même côté | Même côté à 1 s près | Décalage médian (rejeu − réel) |
|---|---|---|---|---|---|---|---|
| B (reconstruit X15) | 563 | 430 | 346 | 342 | 307 | 146 | 0,17 s |
| moteur du bot ramené à 0,015 % (H15) | 563 | 430 | 384 | 381 | 360 | 244 | 0,13 s |

La cohorte B (X15, définition imposée) ne recoupe le fantôme réel qu'en partie : le fantôme réel déclenche dans plus de cycles et souvent à un autre instant ; le moteur du bot ramené à 0,015 % (H15) est plus proche. B est donc une **simulation** de la règle corrigée, pas le relevé du fantôme réel.

### Une simulation « teneur d'ordre » crédible est-elle possible ? **Non — seulement des bornes.**

- La position dans la file n'est **pas observable** (aucun événement d'ordre individuel, seulement des sommes agrégées). Les échanges sont petits (voir ci-dessus) : la plupart des mouvements du meilleur niveau viennent d'ajouts / retraits de teneurs d'ordre, pas d'échanges.
- Modèle de file **pessimiste** utilisé (nous sommes DERNIERS dans la file) : l'ordre passif d'achat du côté opposé à L n'est rempli que si le meilleur vendeur opposé passe **strictement sous L** (≤ L − 1 c) sur une ligne (prudent), pour la taille affichée de cette ligne ; pessimiste : il doit y rester au moins 2 lignes de suite, moitié de la taille. Idéal (borne haute, jamais atteignable) : rempli dès que le vendeur touche L, quantité entière.
- Variante « file agrégée » (diagnostic seulement, étiquetée) : rempli si la somme des échanges du jeton opposé pendant la vie de l'ordre ≥ (taille affichée devant nous + notre quantité). Elle surestime : les échanges agrégés peuvent avoir eu lieu à d'autres prix que le nôtre.

Ordres passifs « sauvetage » (vendeur opposé − 1 c, 10 s, au déclencheur modèle −10 ; cohortes A + B, validation + test ; 201 ordres) — part qui aurait été remplie :

| Règle | Ordres | Remplis |
|---|---|---|
| idéal : le vendeur touche notre prix | 201 | 41,3 % |
| prudent : le vendeur passe 1 c sous notre prix | 201 | 32,8 % |
| pessimiste : 1 c sous notre prix, 2 lignes de suite | 201 | 28,9 % |
| file agrégée 1 s (échanges « vente » du jeton opposé ≥ file + nous) | 201 | 13,9 % |
| file agrégée 1 s (tous échanges du jeton opposé) — borne très optimiste | 201 | 51,7 % |
| sous-ensemble couvert par une photo 100 ms : traversée à 100 ms | 4 | 0,0 % |
| sous-ensemble photo 100 ms : file agrégée 100 ms (échanges « vente ») | 4 | 0,0 % |

L'écart entre ces lignes EST l'incertitude sur le remplissage passif : aucune n'est une mesure. Tous les résultats « passifs » ci-dessous sont donnés pour les trois scénarios ; seul le prudent sert au classement.

## 2. Définitions (fixées avant les calculs)

**Entrées** (inchangées, identiques pour GARDER et pour chaque couverture) : premier signal du cycle, achat au seul meilleur vendeur, quantité affichée, au plus 50 $ frais compris (scénario prudent : décision exécutée sur la première ligne ≥ signal + 0,3 s, au prix vu ou mieux, sinon pas d'entrée ; pessimiste : + 0,6 s et moitié de la quantité affichée ; idéal : 0 s).

- **A · désaccord 30 zone + modèle monte** : > 60 s restantes, vendeur de notre côté dans [0,15 ; 0,35), modèle du bot (r[2]) − vendeur ≥ 0,30, modèle de notre côté monté d'au moins 3 c en 3 s.
- **B · V2-F corrigé 0,015 %** : vendeur 0,03-0,97, écart ≥ 0,20 qui a grandi d'au moins 3 c en 3 s, avec le modèle reconstruit à sdRel = 1,5e-4.
- **C · V2-F original** (diagnostic) : même règle avec r[2].

| Cohorte | apprentissage | validation | test inédit |
|---|---|---|---|
| A · désaccord 30 zone + modèle monte | 51 | 62 | 47 |
| B · V2-F corrigé 0,015 % | 239 | 239 | 178 |
| C · V2-F original (diagnostic) | 339 | 380 | 258 |

**Scénarios d'exécution** (frais preneur sur chaque achat / vente au marché) :

- **idéal** (borne haute, JAMAIS atteignable) : délai 0, meilleur niveau disponible en quantité illimitée pour les couvertures, ordre passif rempli dès que le prix touche, fusion des paires (capital libéré tout de suite).
- **prudent** (classement) : délai 0,3 s, quantité affichée de la ligne d'exécution, ordre passif rempli seulement sur traversée (vendeur ≤ limite − 1 c).
- **pessimiste** : délai 0,6 s, moitié de la quantité affichée, ordre passif seulement si la traversée dure ≥ 2 lignes.
- Ordre preneur = ordre à cours limité au prix vu à la décision, exécuté sur la ligne décision + délai ; s'il est parti, la couverture réessaie à la ligne suivante au nouveau prix tant que sa condition tient.

**Capital** : un portefeuille de 250 $ par cohorte et par période, rejoué dans l'ordre chronologique. Un signal par cycle et des cycles successifs : une seule position ouverte à la fois. Entrée ≤ min(50 $, capital) ; chaque couverture doit tenir dans le capital libre (capital − argent engagé − ordres passifs posés), sinon elle est réduite (comptée). Le capital revient au règlement (fusion anticipée seulement en idéal). Classement sur cette version ; la version « 50 $ indépendants » (capital illimité) est donnée à côté.

**Déclencheurs** : *modèle −10* = première ligne où le modèle de la cohorte, de notre côté, est ≥ 10 points sous sa valeur au signal (≥ 2 s avant la fin) ; *paire < 1* = prix d'entrée + frais + vendeur opposé + frais < 1 ; *perte latente* = parts × meilleur acheteur de notre côté − coût ≤ −25 $ / −10 $.

| Couverture | Déclencheur | Règle |
|---|---|---|
| H01 verrouillage paire complète (coût < 1) | paire < 1 | achète l'opposé jusqu'à autant de parts que la position, tant que la paire coûte < 1 |
| H02 verrouillage partiel 25 % | paire < 1 | idem jusqu'à 25 % de la position |
| H03 verrouillage partiel 50 % | paire < 1 | idem jusqu'à 50 % |
| H04 plancher de profit (les 2 issues ≥ 0) | paire < 1 | plus petite quantité opposée qui rend les deux issues ≥ 0 (si le carnet et le capital le permettent) |
| H05 réserve jackpot (≥ 70 % gardé) | paire < 1 | x = min(position, 0,3 × jackpot théorique / coût unitaire) : garde ≥ 70 % du jackpot, la pire issue s'améliore |
| H06 échelle de paires (4 tranches) | paire < 1 | tranches de 25 % quand la paire coûte < 1,00 / 0,98 / 0,96 / 0,94 |
| H07 pire perte limitée à −25 $ | perte latente −25 $ | achète l'opposé pour que la pire issue ≥ −25 $ (au plus la paire complète) |
| H08 pire perte limitée à −10 $ | perte latente −10 $ | idem −10 $ |
| H09 pire issue à 0 dans le budget (après modèle −10) | modèle −10 | après modèle −10 : rend la pire issue ≥ 0 si c'est faisable dans le budget (sinon rien — « infaisable ») |
| H10 couvrir ou vendre (avantage net) | modèle −10 | avantage net = (1 − vendeur opposé − frais) − (acheteur de notre côté − frais) ; > 0 → acheter l'opposé, sinon vendre la position au meilleur acheteur |
| H11 alerte précoce (2 signaux sur 3) 25 % | 2 alertes sur 3 | 2 des 3 alertes sur 3 s (baisse du modèle, perp contre nous, acheteur de notre côté qui baisse ; seuils = 90e centile de l'apprentissage) → opposé 25 % |
| H12 horloge de risque (immédiat / attendre 3 s) | modèle −10 | P(vendeur opposé + 2 c en 3 s) ≥ seuil → immédiat, sinon attendre 3 s puis acheter |
| H13 prédictive 1 s | modèle −10 | P(baisse ≥ 1 c en 1 s) > seuil → attendre 1 s, sinon immédiat |
| H14 prédictive 3 s | modèle −10 | idem 3 s |
| H15 prédictive 5 s | modèle −10 | idem 5 s |
| H16 prédictive 10 s | modèle −10 | idem 10 s |
| H17 premier passage (limite si EV > immédiat) | modèle −10 | pour k = 1, 2, 3, 5 c : EV = P(traversée de vendeur − k en 10 s) × (k + frais évités) − (1 − P) × hausse moyenne si non rempli (app.) ; meilleure EV > 0 → ordre passif 10 s puis immédiat, sinon immédiat |
| H18 fenêtre de conversion prédite (paire ≤ 0,95) — inactive si seuil appris = jamais | à l'entrée (prédiction) | à l'entrée : P(paire ≤ 0,95 frais compris avant la fin) > seuil → ordre passif opposé au prix qui fait 0,95, jusqu'à la fin − 5 s |
| H19 sauvetage passif (vendeur − 1 c, 10 s) | modèle −10 | ordre passif opposé à vendeur − 1 c pendant 10 s, pas de repli |
| H20 prédicteur de file (traversée) passif sinon immédiat | modèle −10 | P(traversée de vendeur − 1 c en 10 s) > seuil → passif 10 s puis immédiat, sinon immédiat |
| H21 recharge du carnet | modèle −10 | si le vendeur opposé vient de sauter ≥ 2 c (dernière seconde) : attendre ≤ 5 s qu'il revienne au niveau d'avant, sinon immédiat ; pas de saut → immédiat |
| H22 hybride 50 % immédiat + 50 % passif | modèle −10 | 50 % immédiat + 50 % passif à vendeur − 1 c (10 s), puis immédiat |
| H23 boomerang (revente de l'opposé +5 c) | paire < 1 | comme H01, puis revend l'opposé au meilleur acheteur s'il monte de 5 c (garde la 1re jambe) |
| H24 moteur d'inventaire deux jambes | oscillation ±5 c | achète 25 % d'opposé à chaque baisse de 5 c du vendeur opposé (2 tranches) et 25 % de notre côté à chaque baisse de 5 c de notre vendeur (2 tranches) ; ≤ 50 $ de plus, exposition nette ≤ 1,5 × |

**Comparaisons** : VENDRE 50 % / 100 % = vente de la première jambe au meilleur acheteur au MÊME instant que le premier déclenchement de la couverture (mêmes délais, mêmes frais). Toutes les positions comptent dans tous les totaux, couvertes ou non. Jackpot = gain ≥ 4 × la mise en gardant.

**Appris sur l'apprentissage seulement** (scénario prudent, 3 cohortes réunies) : H12 seuil 0,25 ; H13 seuil 0,50 ; H14 seuil 0,10 ; H15 seuil 0,30 ; H16 seuil 0,60 ; H18 seuil 1,01 ; H20 seuil 0,40 ; H11 seuils : baisse du modèle 0,038, perp contre nous 1.0 pb, acheteur qui baisse 0,050. Seuil 1,01 = « jamais » (la règle retombe sur l'immédiat).

Grille des seuils (Σ P&L apprentissage, prudent, 3 cohortes) : H12 : 0,05 → +26 $, 0,10 → −19 $, 0,15 → −14 $, 0,20 → −15 $, 0,25 → +44 $, 0,30 → +24 $, 0,40 → −10 $, 0,50 → −26 $, 0,60 → −32 $, 0,80 → −25 $, 1,01 → −25 $ · H13 : 0,05 → −66 $, 0,10 → −15 $, 0,15 → −34 $, 0,20 → −14 $, 0,25 → −13 $, 0,30 → −13 $, 0,40 → −13 $, 0,50 → −12 $, 0,60 → −12 $, 0,80 → −12 $, 1,01 → −12 $ · H14 : 0,05 → −76 $, 0,10 → +10 $, 0,15 → −51 $, 0,20 → −14 $, 0,25 → −11 $, 0,30 → −14 $, 0,40 → −13 $, 0,50 → −12 $, 0,60 → −12 $, 0,80 → −12 $, 1,01 → −12 $ · H15 : 0,05 → −63 $, 0,10 → −112 $, 0,15 → −36 $, 0,20 → +10 $, 0,25 → +29 $, 0,30 → +38 $, 0,40 → −10 $, 0,50 → −11 $, 0,60 → −17 $, 0,80 → −12 $, 1,01 → −12 $ · H16 : 0,05 → −197 $, 0,10 → −214 $, 0,15 → −136 $, 0,20 → −72 $, 0,25 → −174 $, 0,30 → −72 $, 0,40 → −48 $, 0,50 → −21 $, 0,60 → −4 $, 0,80 → −12 $, 1,01 → −12 $ · H18 : 0,05 → −4 184 $, 0,10 → −4 184 $, 0,15 → −4 184 $, 0,20 → −4 184 $, 0,25 → −4 184 $, 0,30 → −4 271 $, 0,40 → −3 929 $, 0,50 → −2 672 $, 0,60 → −1 205 $, 0,80 → +546 $, 1,01 → +1 642 $ · H20 : 0,05 → −452 $, 0,10 → −401 $, 0,15 → −317 $, 0,20 → −188 $, 0,25 → −122 $, 0,30 → −88 $, 0,40 → −3 $, 0,50 → −5 $, 0,60 → −9 $, 0,80 → −12 $, 1,01 → −12 $.

Qualité des modèles figés (AUC) : validation : baisse ≥ 1 c en 1 s (H13-H16) 0,70, baisse ≥ 1 c en 3 s (H13-H16) 0,71, baisse ≥ 1 c en 5 s (H13-H16) 0,72, baisse ≥ 1 c en 10 s (H13-H16) 0,73, hausse ≥ 2 c en 3 s (H12) 0,73, traversée de vendeur − 1 c en 10 s (H17/H20) 0,72, traversée de vendeur − 2 c en 10 s (H17/H20) 0,71, traversée de vendeur − 3 c en 10 s (H17/H20) 0,71, traversée de vendeur − 5 c en 10 s (H17/H20) 0,69, paire ≤ 0,95 avant la fin (H18) 0,63 · inédit : baisse ≥ 1 c en 1 s (H13-H16) 0,67, baisse ≥ 1 c en 3 s (H13-H16) 0,68, baisse ≥ 1 c en 5 s (H13-H16) 0,70, baisse ≥ 1 c en 10 s (H13-H16) 0,72, hausse ≥ 2 c en 3 s (H12) 0,71, traversée de vendeur − 1 c en 10 s (H17/H20) 0,71, traversée de vendeur − 2 c en 10 s (H17/H20) 0,69, traversée de vendeur − 3 c en 10 s (H17/H20) 0,68, traversée de vendeur − 5 c en 10 s (H17/H20) 0,67, paire ≤ 0,95 avant la fin (H18) 0,64.

## 3. Classement — Δ P&L contre GARDER, scénario prudent (validation puis test)

Classé par Δ sur la validation (prudent). Un Δ positif dont l'IC 90 % contient 0 n'est PAS démontré. Le taux de réussite n'entre pas dans le classement.

**Attention — le portefeuille de 250 $ est ruiné.** Avec un délai de 0,3 s, GARDER perd plus de 250 $ (creux) sur la validation comme sur le test pour A et B : le portefeuille tombe à 0 et les entrées suivantes sont refusées. Le classement « 250 $ » imposé ne mesure alors presque que le moment de la ruine (Δ ≈ 0 quand les deux finissent à −250 $). Le classement « 50 $ indépendants » est donné juste après : c'est lui qui porte l'information sur les couvertures.

### A · désaccord 30 zone + modèle monte — portefeuille 250 $ (classement imposé)

| Rang | Couverture | Δ vs GARDER valid. prudent [IC 90 %] | positions jouées / refusées faute de capital (valid.) | Δ test prudent [IC 90 %] | positions jouées / refusées (test) | valid. idéal | valid. pessimiste | test idéal | test pessimiste | Jackpots gardés valid. |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | H01 verrouillage paire complète (coût < 1) | **+108 $** [−396 $ ; +644 $] | 37 / 0 | **+0 $** [−363 $ ; +323 $] | 25 / 15 | −972 $ | +75 $ | −309 $ | +0 $ | 0/1 |
| 2 | H06 échelle de paires (4 tranches) | **+108 $** [−400 $ ; +717 $] | 37 / 0 | **−0 $** [−309 $ ; +293 $] | 31 / 5 | −949 $ | −28 $ | −271 $ | +0 $ | 0/1 |
| 3 | H24 moteur d'inventaire deux jambes | **+69 $** [−448 $ ; +670 $] | 37 / 0 | **+0 $** [−109 $ ; +103 $] | 29 / 7 | −63 $ | +62 $ | −89 $ | +0 $ | 0/1 |
| 4 | H14 prédictive 3 s | **+1 $** [−433 $ ; +387 $] | 10 / 44 | **+0 $** [−81 $ ; +75 $] | 28 / 9 | +163 $ | −68 $ | −106 $ | +0 $ | 1/1 |
| 5 | H12 horloge de risque (immédiat / attendre 3 s) | **+1 $** [−430 $ ; +391 $] | 10 / 44 | **+1 $** [−83 $ ; +72 $] | 28 / 9 | +185 $ | −68 $ | −101 $ | +0 $ | 1/1 |
| 6 | H13 prédictive 1 s | **+1 $** [−416 $ ; +380 $] | 10 / 44 | **+1 $** [−81 $ ; +74 $] | 28 / 9 | +222 $ | −68 $ | −102 $ | +0 $ | 1/1 |
| 7 | H16 prédictive 10 s | **+1 $** [−426 $ ; +386 $] | 10 / 44 | **+1 $** [−81 $ ; +70 $] | 28 / 9 | +220 $ | −68 $ | −102 $ | +0 $ | 1/1 |
| 8 | H17 premier passage (limite si EV > immédiat) | **+1 $** [−418 $ ; +396 $] | 10 / 44 | **+1 $** [−82 $ ; +72 $] | 28 / 9 | +222 $ | −68 $ | −102 $ | +0 $ | 1/1 |
| 9 | H21 recharge du carnet | **+1 $** [−419 $ ; +390 $] | 10 / 44 | **+0 $** [−83 $ ; +71 $] | 28 / 9 | +119 $ | −68 $ | −79 $ | +0 $ | 1/1 |
| 10 | H22 hybride 50 % immédiat + 50 % passif | **+1 $** [−413 $ ; +386 $] | 10 / 44 | **+0 $** [−83 $ ; +70 $] | 29 / 7 | +137 $ | −68 $ | −124 $ | +0 $ | 1/1 |
| 11 | H15 prédictive 5 s | **+0 $** [−418 $ ; +387 $] | 10 / 44 | **+1 $** [−86 $ ; +71 $] | 28 / 9 | +217 $ | −68 $ | −133 $ | +0 $ | 1/1 |
| 12 | H20 prédicteur de file (traversée) passif sinon immédiat | **+0 $** [−420 $ ; +398 $] | 10 / 44 | **+1 $** [−83 $ ; +74 $] | 28 / 9 | +224 $ | −68 $ | −102 $ | +0 $ | 1/1 |
| 13 | H04 plancher de profit (les 2 issues ≥ 0) | **+0 $** [−267 $ ; +246 $] | 25 / 15 | **−0 $** [−412 $ ; +399 $] | 18 / 27 | −747 $ | +34 $ | −266 $ | +0 $ | 1/1 |
| 14 | H07 pire perte limitée à −25 $ | **+0 $** [−393 $ ; +374 $] | 11 / 42 | **+0 $** [−363 $ ; +351 $] | 18 / 27 | −409 $ | −68 $ | −523 $ | +0 $ | 1/1 |
| 15 | H08 pire perte limitée à −10 $ | **+0 $** [−258 $ ; +185 $] | 17 / 31 | **+158 $** [−170 $ ; +464 $] | 34 / 0 | −502 $ | −41 $ | −239 $ | +0 $ | 1/1 |
| 16 | H10 couvrir ou vendre (avantage net) | **+0 $** [−311 $ ; +284 $] | 14 / 38 | **+0 $** [−89 $ ; +75 $] | 29 / 7 | +222 $ | −67 $ | −101 $ | −0 $ | 1/1 |
| 17 | H11 alerte précoce (2 signaux sur 3) 25 % | **+0 $** [−92 $ ; +69 $] | 18 / 30 | **+0 $** [−49 $ ; +47 $] | 30 / 6 | −170 $ | −68 $ | +42 $ | −0 $ | 1/1 |
| 18 | H03 verrouillage partiel 50 % | **+0 $** [−397 $ ; +433 $] | 37 / 0 | **−0 $** [−179 $ ; +142 $] | 30 / 6 | −507 $ | +42 $ | −153 $ | +0 $ | 0/1 |
| 19 | H19 sauvetage passif (vendeur − 1 c, 10 s) | **+0 $** [−414 $ ; +382 $] | 10 / 44 | **+0 $** [−88 $ ; +71 $] | 29 / 7 | −85 $ | −68 $ | −158 $ | +0 $ | 1/1 |
| 20 | H23 boomerang (revente de l'opposé +5 c) | **+0 $** [−163 $ ; +133 $] | 17 / 31 | **−0 $** [−155 $ ; +154 $] | 31 / 5 | −843 $ | −46 $ | +29 $ | −0 $ | 0/1 |
| 21 | H05 réserve jackpot (≥ 70 % gardé) | **−0 $** [−250 $ ; +309 $] | 33 / 6 | **+0 $** [−126 $ ; +111 $] | 29 / 7 | −360 $ | +6 $ | −130 $ | +0 $ | 0/1 |
| 22 | H09 pire issue à 0 dans le budget (après modèle −10) | **−0 $** [−100 $ ; +86 $] | 17 / 31 | **−0 $** [−10 $ ; +10 $] | 30 / 6 | +73 $ | −10 $ | +8 $ | +0 $ | 1/1 |
| 23 | H02 verrouillage partiel 25 % | **−0 $** [−279 $ ; +284 $] | 34 / 4 | **+0 $** [−112 $ ; +99 $] | 29 / 7 | −253 $ | +13 $ | −76 $ | −0 $ | 1/1 |
| 24 | H18 fenêtre de conversion prédite (paire ≤ 0,95) — inactive si seuil appris = jamais | **−0 $** [+0 $ ; +0 $] | 21 / 21 | **+0 $** [+0 $ ; +0 $] | 30 / 6 | −0 $ | +0 $ | +0 $ | +0 $ | 1/1 |

Référence GARDER (prudent, 250 $) : validation 21 positions jouées, 21 refusées faute de capital, −250 $, creux −312 $ · test 30 jouées, 6 refusées, −250 $, creux −362 $.

### A · désaccord 30 zone + modèle monte — 50 $ indépendants (chaque position seule, capital illimité ; informatif)

| Rang | Couverture | Δ vs GARDER valid. prudent [IC 90 %] | Δ test prudent [IC 90 %] | Δ app. prudent | valid. idéal | valid. pessimiste | test idéal | test pessimiste | Δ vs VENDRE 50 % (valid. / test) | Δ vs VENDRE 100 % (valid. / test) | Jackpots gardés (valid.) | Profit sacrifié jackpots (valid.) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | H24 moteur d'inventaire deux jambes | **+112 $** [−54 $ ; +291 $] | **−30 $** [−127 $ ; +64 $] | +43 $ | −63 $ | +62 $ | −89 $ | −78 $ | +166 $ / −89 $ | +241 $ / −137 $ | 2/5 | −33 $ |
| 2 | H09 pire issue à 0 dans le budget (après modèle −10) | **+5 $** [−100 $ ; +110 $] | **−5 $** [−15 $ ; +0 $] | −284 $ | +73 $ | +12 $ | +8 $ | +0 $ | +21 $ / +9 $ | +40 $ / +23 $ | 5/5 | +0 $ |
| 3 | H18 fenêtre de conversion prédite (paire ≤ 0,95) — inactive si seuil appris = jamais | **+0 $** [+0 $ ; +0 $] | **+0 $** [+0 $ ; +0 $] | +0 $ | −0 $ | +0 $ | +0 $ | +0 $ | +0 $ / +0 $ | +0 $ / +0 $ | 5/5 | +0 $ |
| 4 | H02 verrouillage partiel 25 % | **−4 $** [−146 $ ; +129 $] | **−3 $** [−144 $ ; +125 $] | −191 $ | −253 $ | −23 $ | −76 $ | −20 $ | +75 $ / −65 $ | +165 $ / −125 $ | 4/5 | +78 $ |
| 5 | H03 verrouillage partiel 50 % | **−14 $** [−311 $ ; +264 $] | **−6 $** [−313 $ ; +251 $] | −382 $ | −507 $ | −44 $ | −153 $ | −5 $ | +64 $ / −68 $ | +154 $ / −128 $ | 0/5 | +156 $ |
| 6 | H01 verrouillage paire complète (coût < 1) | **−24 $** [−633 $ ; +522 $] | **+7 $** [−593 $ ; +510 $] | −762 $ | −1 013 $ | −105 $ | −306 $ | +50 $ | +54 $ / −55 $ | +144 $ / −115 $ | 0/5 | +313 $ |
| 7 | H23 boomerang (revente de l'opposé +5 c) | **−24 $** [−207 $ ; +134 $] | **−166 $** [−650 $ ; +163 $] | −809 $ | −699 $ | +11 $ | +24 $ | −140 $ | +54 $ / −228 $ | +144 $ / −288 $ | 2/5 | +41 $ |
| 8 | H05 réserve jackpot (≥ 70 % gardé) | **−27 $** [−218 $ ; +150 $] | **+0 $** [−196 $ ; +164 $] | −236 $ | −360 $ | −48 $ | −130 $ | −21 $ | +51 $ / −62 $ | +141 $ / −122 $ | 0/5 | +115 $ |
| 9 | H13 prédictive 1 s | **−35 $** [−311 $ ; +138 $] | **−28 $** [−107 $ ; +22 $] | −323 $ | +222 $ | −36 $ | −101 $ | +6 $ | −18 $ / −14 $ | +0 $ / +0 $ | 5/5 | +0 $ |
| 10 | H17 premier passage (limite si EV > immédiat) | **−35 $** [−322 $ ; +138 $] | **−28 $** [−110 $ ; +22 $] | −323 $ | +222 $ | −36 $ | −101 $ | +6 $ | −18 $ / −14 $ | +0 $ / +0 $ | 5/5 | +0 $ |
| 11 | H10 couvrir ou vendre (avantage net) | **−35 $** [−308 $ ; +142 $] | **−28 $** [−111 $ ; +22 $] | −323 $ | +222 $ | −36 $ | −101 $ | +6 $ | −18 $ / −14 $ | −0 $ / +0 $ | 5/5 | +0 $ |
| 12 | H16 prédictive 10 s | **−35 $** [−315 $ ; +144 $] | **−28 $** [−113 $ ; +22 $] | −323 $ | +220 $ | −36 $ | −101 $ | +6 $ | −19 $ / −14 $ | −1 $ / +0 $ | 5/5 | +0 $ |
| 13 | H20 prédicteur de file (traversée) passif sinon immédiat | **−37 $** [−325 $ ; +137 $] | **−28 $** [−113 $ ; +22 $] | −323 $ | +224 $ | −38 $ | −101 $ | +6 $ | −21 $ / −14 $ | −2 $ / +0 $ | 5/5 | +0 $ |
| 14 | H15 prédictive 5 s | **−37 $** [−314 $ ; +140 $] | **−28 $** [−113 $ ; +22 $] | −323 $ | +217 $ | −36 $ | −132 $ | +6 $ | −21 $ / −14 $ | −2 $ / +0 $ | 5/5 | +0 $ |
| 15 | H06 échelle de paires (4 tranches) | **−42 $** [−596 $ ; +494 $] | **+39 $** [−477 $ ; +482 $] | −704 $ | −984 $ | −144 $ | −240 $ | +39 $ | +36 $ / −23 $ | +126 $ / −83 $ | 0/5 | +264 $ |
| 16 | H21 recharge du carnet | **−47 $** [−311 $ ; +131 $] | **−30 $** [−116 $ ; +20 $] | −324 $ | +119 $ | −41 $ | −79 $ | +4 $ | −31 $ / −16 $ | −12 $ / −1 $ | 5/5 | +0 $ |
| 17 | H14 prédictive 3 s | **−48 $** [−354 $ ; +141 $] | **−32 $** [−115 $ ; +15 $] | −323 $ | +163 $ | −36 $ | −106 $ | +6 $ | −32 $ / −18 $ | −13 $ / −4 $ | 5/5 | +0 $ |
| 18 | H12 horloge de risque (immédiat / attendre 3 s) | **−55 $** [−360 $ ; +137 $] | **−28 $** [−110 $ ; +22 $] | −323 $ | +185 $ | −38 $ | −101 $ | +6 $ | −39 $ / −14 $ | −20 $ / +0 $ | 5/5 | +0 $ |
| 19 | H22 hybride 50 % immédiat + 50 % passif | **−56 $** [−340 $ ; +122 $] | **−29 $** [−110 $ ; +21 $] | −325 $ | +137 $ | −49 $ | −124 $ | +5 $ | −40 $ / −15 $ | −22 $ / −0 $ | 5/5 | +0 $ |
| 20 | H04 plancher de profit (les 2 issues ≥ 0) | **−60 $** [−517 $ ; +330 $] | **−35 $** [−533 $ ; +399 $] | −618 $ | −747 $ | −105 $ | −265 $ | +5 $ | +18 $ / −98 $ | +108 $ / −158 $ | 3/5 | +210 $ |
| 21 | H11 alerte précoce (2 signaux sur 3) 25 % | **−78 $** [−232 $ ; +48 $] | **+31 $** [−6 $ ; +70 $] | −128 $ | −170 $ | −78 $ | +42 $ | +29 $ | +85 $ / −30 $ | +260 $ / −85 $ | 3/5 | +90 $ |
| 22 | H19 sauvetage passif (vendeur − 1 c, 10 s) | **−142 $** [−434 $ ; +9 $] | **−31 $** [−103 $ ; +18 $] | +0 $ | −77 $ | −120 $ | −158 $ | +2 $ | −125 $ / −17 $ | −107 $ / −3 $ | 5/5 | +0 $ |
| 23 | H08 pire perte limitée à −10 $ | **−143 $** [−825 $ ; +421 $] | **+152 $** [−454 $ ; +731 $] | −562 $ | −502 $ | −133 $ | −235 $ | +25 $ | −73 $ / +71 $ | +0 $ / −9 $ | 3/5 | +365 $ |
| 24 | H07 pire perte limitée à −25 $ | **−391 $** [−1 082 $ ; +152 $] | **−182 $** [−797 $ ; +311 $] | −504 $ | −410 $ | −308 $ | −49 $ | −187 $ | −198 $ / −100 $ | −0 $ / −10 $ | 4/5 | +298 $ |

Référence GARDER (50 $ indépendants) : validation prudent 37 positions −293 $ (idéal 62 positions +753 $, pessimiste 31 positions −182 $) · test prudent 34 positions −411 $ (idéal +273 $, pessimiste −269 $).

### B · V2-F corrigé 0,015 % — portefeuille 250 $ (classement imposé)

| Rang | Couverture | Δ vs GARDER valid. prudent [IC 90 %] | positions jouées / refusées faute de capital (valid.) | Δ test prudent [IC 90 %] | positions jouées / refusées (test) | valid. idéal | valid. pessimiste | test idéal | test pessimiste | Jackpots gardés valid. |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | H23 boomerang (revente de l'opposé +5 c) | **+0 $** [−363 $ ; +326 $] | 141 / 3 | **−0 $** [−119 $ ; +103 $] | 14 / 148 | −1 176 $ | −0 $ | −0 $ | −0 $ | 5/5 |
| 2 | H19 sauvetage passif (vendeur − 1 c, 10 s) | **+0 $** [−891 $ ; +973 $] | 126 / 22 | **−0 $** [−135 $ ; +119 $] | 14 / 148 | −1 176 $ | −0 $ | +0 $ | −0 $ | 3/5 |
| 3 | H08 pire perte limitée à −10 $ | **+0 $** [−1 350 $ ; +1 370 $] | 61 / 133 | **+0 $** [−366 $ ; +384 $] | 19 / 142 | −1 176 $ | −0 $ | −0 $ | −0 $ | 1/5 |
| 4 | H18 fenêtre de conversion prédite (paire ≤ 0,95) — inactive si seuil appris = jamais | **+0 $** [+0 $ ; +0 $] | 141 / 3 | **−0 $** [+0 $ ; +0 $] | 16 / 145 | −0 $ | +0 $ | +0 $ | +0 $ | 5/5 |
| 5 | H09 pire issue à 0 dans le budget (après modèle −10) | **+0 $** [−720 $ ; +827 $] | 127 / 20 | **−0 $** [−128 $ ; +121 $] | 16 / 145 | −946 $ | +0 $ | +0 $ | +0 $ | 3/5 |
| 6 | H07 pire perte limitée à −25 $ | **+0 $** [−775 $ ; +781 $] | 135 / 9 | **−0 $** [−148 $ ; +145 $] | 17 / 144 | −908 $ | −0 $ | −0 $ | +0 $ | 4/5 |
| 7 | H11 alerte précoce (2 signaux sur 3) 25 % | **+0 $** [−349 $ ; +378 $] | 137 / 7 | **−0 $** [−69 $ ; +57 $] | 16 / 145 | −168 $ | −0 $ | −0 $ | +0 $ | 5/5 |
| 8 | H20 prédicteur de file (traversée) passif sinon immédiat | **+0 $** [−1 057 $ ; +1 125 $] | 113 / 46 | **+0 $** [−132 $ ; +116 $] | 16 / 145 | −696 $ | +0 $ | +953 $ | +0 $ | 2/5 |
| 9 | H02 verrouillage partiel 25 % | **−0 $** [−368 $ ; +387 $] | 137 / 7 | **+0 $** [−137 $ ; +152 $] | 17 / 144 | −359 $ | +0 $ | −0 $ | +0 $ | 5/5 |
| 10 | H24 moteur d'inventaire deux jambes | **−0 $** [−521 $ ; +559 $] | 136 / 8 | **−0 $** [−88 $ ; +83 $] | 14 / 148 | −461 $ | +0 $ | +0 $ | −0 $ | 4/5 |
| 11 | H03 verrouillage partiel 50 % | **−0 $** [−1 311 $ ; +1 248 $] | 67 / 124 | **−0 $** [−297 $ ; +303 $] | 20 / 141 | −713 $ | −0 $ | −0 $ | −0 $ | 1/5 |
| 12 | H15 prédictive 5 s | **−0 $** [−1 393 $ ; +1 436 $] | 36 / 177 | **+0 $** [−126 $ ; +110 $] | 16 / 145 | −731 $ | +0 $ | +898 $ | −0 $ | 1/5 |
| 13 | H13 prédictive 1 s | **−0 $** [−1 318 $ ; +1 386 $] | 36 / 177 | **+0 $** [−129 $ ; +118 $] | 16 / 145 | −649 $ | +0 $ | +1 077 $ | +0 $ | 1/5 |
| 14 | H16 prédictive 10 s | **−0 $** [−1 323 $ ; +1 396 $] | 36 / 177 | **+0 $** [−129 $ ; +118 $] | 16 / 145 | −655 $ | +0 $ | +1 092 $ | +0 $ | 1/5 |
| 15 | H17 premier passage (limite si EV > immédiat) | **−0 $** [−1 308 $ ; +1 295 $] | 36 / 177 | **+0 $** [−131 $ ; +124 $] | 16 / 145 | −648 $ | +0 $ | +1 065 $ | +0 $ | 1/5 |
| 16 | H21 recharge du carnet | **−0 $** [−1 489 $ ; +1 426 $] | 22 / 204 | **+0 $** [−126 $ ; +97 $] | 16 / 145 | −875 $ | −0 $ | +894 $ | −0 $ | 0/5 |
| 17 | H22 hybride 50 % immédiat + 50 % passif | **−0 $** [−1 116 $ ; +1 074 $] | 113 / 46 | **−0 $** [−142 $ ; +115 $] | 16 / 145 | −1 053 $ | −0 $ | +843 $ | −0 $ | 2/5 |
| 18 | H12 horloge de risque (immédiat / attendre 3 s) | **−0 $** [−1 321 $ ; +1 346 $] | 37 / 176 | **+0 $** [−86 $ ; +89 $] | 17 / 144 | −941 $ | −0 $ | +1 035 $ | −0 $ | 1/5 |
| 19 | H01 verrouillage paire complète (coût < 1) | **−0 $** [−1 409 $ ; +1 391 $] | 62 / 132 | **+0 $** [−304 $ ; +313 $] | 21 / 140 | −1 176 $ | +0 $ | +197 $ | +0 $ | 1/5 |
| 20 | H04 plancher de profit (les 2 issues ≥ 0) | **−0 $** [−1 368 $ ; +1 373 $] | 61 / 133 | **−0 $** [−285 $ ; +290 $] | 19 / 142 | −1 024 $ | −0 $ | +0 $ | −0 $ | 1/5 |
| 21 | H05 réserve jackpot (≥ 70 % gardé) | **−0 $** [−522 $ ; +547 $] | 136 / 8 | **+0 $** [−179 $ ; +184 $] | 18 / 143 | −514 $ | −0 $ | −0 $ | −0 $ | 5/5 |
| 22 | H06 échelle de paires (4 tranches) | **−0 $** [−1 471 $ ; +1 465 $] | 62 / 132 | **+0 $** [−417 $ ; +464 $] | 23 / 138 | −1 176 $ | +0 $ | +147 $ | −0 $ | 0/5 |
| 23 | H10 couvrir ou vendre (avantage net) | **−0 $** [−1 256 $ ; +1 291 $] | 109 / 56 | **−0 $** [−152 $ ; +147 $] | 23 / 138 | −666 $ | −0 $ | +1 195 $ | +0 $ | 2/5 |
| 24 | H14 prédictive 3 s | **−0 $** [−1 030 $ ; +1 181 $] | 113 / 46 | **+0 $** [−85 $ ; +77 $] | 17 / 144 | −1 042 $ | −0 $ | +799 $ | −0 $ | 3/5 |

Référence GARDER (prudent, 250 $) : validation 141 positions jouées, 3 refusées faute de capital, −250 $, creux −873 $ · test 16 jouées, 145 refusées, −250 $, creux −267 $.

### B · V2-F corrigé 0,015 % — 50 $ indépendants (chaque position seule, capital illimité ; informatif)

| Rang | Couverture | Δ vs GARDER valid. prudent [IC 90 %] | Δ test prudent [IC 90 %] | Δ app. prudent | valid. idéal | valid. pessimiste | test idéal | test pessimiste | Δ vs VENDRE 50 % (valid. / test) | Δ vs VENDRE 100 % (valid. / test) | Jackpots gardés (valid.) | Profit sacrifié jackpots (valid.) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | H18 fenêtre de conversion prédite (paire ≤ 0,95) — inactive si seuil appris = jamais | **+0 $** [+0 $ ; +0 $] | **+0 $** [+0 $ ; +0 $] | +0 $ | −0 $ | −0 $ | +0 $ | +0 $ | +0 $ / +0 $ | +0 $ / +0 $ | 5/5 | +0 $ |
| 2 | H11 alerte précoce (2 signaux sur 3) 25 % | **−242 $** [−548 $ ; +57 $] | **−8 $** [−230 $ ; +223 $] | −287 $ | −168 $ | −123 $ | +26 $ | +37 $ | +249 $ / +7 $ | +738 $ / +41 $ | 5/5 | +284 $ |
| 3 | H02 verrouillage partiel 25 % | **−245 $** [−547 $ ; +41 $] | **+182 $** [−108 $ ; +499 $] | −317 $ | −359 $ | −50 $ | +41 $ | +124 $ | +218 $ / −305 $ | +687 $ / −791 $ | 5/5 | +264 $ |
| 4 | H24 moteur d'inventaire deux jambes | **−288 $** [−780 $ ; +198 $] | **−56 $** [−367 $ ; +253 $] | −293 $ | −461 $ | −245 $ | −311 $ | −97 $ | +109 $ / −518 $ | +511 $ / −978 $ | 4/5 | +160 $ |
| 5 | H05 réserve jackpot (≥ 70 % gardé) | **−304 $** [−727 $ ; +81 $] | **+244 $** [−145 $ ; +638 $] | −443 $ | −515 $ | −71 $ | −18 $ | +176 $ | +159 $ / −243 $ | +628 $ / −729 $ | 5/5 | +345 $ |
| 6 | H23 boomerang (revente de l'opposé +5 c) | **−364 $** [−1 016 $ ; +207 $] | **+280 $** [+30 $ ; +544 $] | −444 $ | −1 494 $ | −96 $ | −205 $ | +176 $ | +99 $ / −207 $ | +569 $ / −693 $ | 4/5 | +235 $ |
| 7 | H19 sauvetage passif (vendeur − 1 c, 10 s) | **−373 $** [−1 127 $ ; +321 $] | **+34 $** [−439 $ ; +459 $] | −656 $ | −858 $ | −9 $ | −56 $ | −16 $ | +106 $ / −417 $ | +581 $ / −868 $ | 3/5 | +507 $ |
| 8 | H03 verrouillage partiel 50 % | **−495 $** [−1 062 $ ; +60 $] | **+352 $** [−257 $ ; +1 018 $] | −637 $ | −718 $ | −102 $ | +82 $ | +254 $ | −32 $ / −134 $ | +438 $ / −621 $ | 2/5 | +525 $ |
| 9 | H08 pire perte limitée à −10 $ | **−506 $** [−1 759 $ ; +730 $] | **+475 $** [−563 $ ; +1 534 $] | −768 $ | −921 $ | −62 $ | +113 $ | +524 $ | −256 $ / +214 $ | −3 $ / −38 $ | 3/5 | +670 $ |
| 10 | H09 pire issue à 0 dans le budget (après modèle −10) | **−510 $** [−1 087 $ ; +53 $] | **+611 $** [+172 $ ; +1 062 $] | −965 $ | −946 $ | −326 $ | +810 $ | +391 $ | −31 $ / +161 $ | +444 $ / −291 $ | 3/5 | +451 $ |
| 11 | H04 plancher de profit (les 2 issues ≥ 0) | **−598 $** [−1 428 $ ; +249 $] | **+519 $** [−540 $ ; +1 554 $] | −1 068 $ | −1 145 $ | −68 $ | +205 $ | +300 $ | −135 $ / +31 $ | +335 $ / −456 $ | 2/5 | +601 $ |
| 12 | H07 pire perte limitée à −25 $ | **−764 $** [−1 867 $ ; +289 $] | **+264 $** [−567 $ ; +995 $] | −568 $ | −907 $ | −575 $ | +15 $ | +299 $ | −401 $ / +122 $ | −21 $ / −9 $ | 3/5 | +684 $ |
| 13 | H21 recharge du carnet | **−833 $** [−2 062 $ ; +314 $] | **+843 $** [+327 $ ; +1 366 $] | −986 $ | −875 $ | −638 $ | +1 100 $ | +844 $ | −354 $ / +392 $ | +121 $ / −59 $ | 3/5 | +774 $ |
| 14 | H14 prédictive 3 s | **−887 $** [−2 108 $ ; +311 $] | **+930 $** [+416 $ ; +1 411 $] | −979 $ | −1 042 $ | −615 $ | +989 $ | +830 $ | −407 $ / +479 $ | +67 $ / +28 $ | 2/5 | +853 $ |
| 15 | H12 horloge de risque (immédiat / attendre 3 s) | **−914 $** [−2 084 $ ; +248 $] | **+890 $** [+389 $ ; +1 409 $] | −896 $ | −941 $ | −614 $ | +1 220 $ | +815 $ | −434 $ / +439 $ | +40 $ / −13 $ | 2/5 | +860 $ |
| 16 | H16 prédictive 10 s | **−921 $** [−2 090 $ ; +200 $] | **+901 $** [+344 $ ; +1 426 $] | −974 $ | −655 $ | −598 $ | +1 281 $ | +867 $ | −441 $ / +450 $ | +33 $ / −1 $ | 2/5 | +843 $ |
| 17 | H17 premier passage (limite si EV > immédiat) | **−948 $** [−2 175 $ ; +232 $] | **+908 $** [+374 $ ; +1 447 $] | −987 $ | −648 $ | −602 $ | +1 252 $ | +873 $ | −468 $ / +458 $ | +7 $ / +6 $ | 2/5 | +843 $ |
| 18 | H15 prédictive 5 s | **−949 $** [−2 135 $ ; +135 $] | **+906 $** [+362 $ ; +1 427 $] | −1 034 $ | −731 $ | −618 $ | +1 093 $ | +876 $ | −469 $ / +456 $ | +5 $ / +4 $ | 2/5 | +843 $ |
| 19 | H13 prédictive 1 s | **−954 $** [−2 193 $ ; +156 $] | **+905 $** [+325 $ ; +1 426 $] | −997 $ | −649 $ | −602 $ | +1 264 $ | +869 $ | −474 $ / +454 $ | +0 $ / +3 $ | 2/5 | +843 $ |
| 20 | H10 couvrir ou vendre (avantage net) | **−954 $** [−2 110 $ ; +133 $] | **+902 $** [+364 $ ; +1 445 $] | −997 $ | −666 $ | −602 $ | +1 248 $ | +870 $ | −474 $ / +452 $ | +0 $ / +0 $ | 2/5 | +843 $ |
| 21 | H20 prédicteur de file (traversée) passif sinon immédiat | **−961 $** [−2 043 $ ; +114 $] | **+916 $** [+352 $ ; +1 445 $] | −989 $ | −696 $ | −636 $ | +1 141 $ | +877 $ | −481 $ / +465 $ | −6 $ / +13 $ | 2/5 | +843 $ |
| 22 | H06 échelle de paires (4 tranches) | **−965 $** [−2 171 $ ; +57 $] | **+822 $** [−269 $ ; +1 976 $] | −1 188 $ | −1 312 $ | −377 $ | +168 $ | +566 $ | −502 $ / +335 $ | −32 $ / −151 $ | 0/5 | +1 044 $ |
| 23 | H01 verrouillage paire complète (coût < 1) | **−988 $** [−2 195 $ ; +111 $] | **+698 $** [−497 $ ; +1 905 $] | −1 283 $ | −1 437 $ | −215 $ | +164 $ | +521 $ | −525 $ / +211 $ | −56 $ / −275 $ | 0/5 | +1 048 $ |
| 24 | H22 hybride 50 % immédiat + 50 % passif | **−1 009 $** [−2 216 $ ; +93 $] | **+854 $** [+321 $ ; +1 389 $] | −1 087 $ | −1 053 $ | −632 $ | +942 $ | +796 $ | −530 $ / +403 $ | −55 $ / −49 $ | 2/5 | +840 $ |

Référence GARDER (50 $ indépendants) : validation prudent 144 positions −70 $ (idéal 237 positions +926 $, pessimiste 120 positions −593 $) · test prudent 112 positions −1 583 $ (idéal −304 $, pessimiste −1 304 $).

### C · V2-F original (diagnostic) — portefeuille 250 $ (classement imposé)

| Rang | Couverture | Δ vs GARDER valid. prudent [IC 90 %] | positions jouées / refusées faute de capital (valid.) | Δ test prudent [IC 90 %] | positions jouées / refusées (test) | valid. idéal | valid. pessimiste | test idéal | test pessimiste | Jackpots gardés valid. |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | H04 plancher de profit (les 2 issues ≥ 0) | **+0 $** [−871 $ ; +1 013 $] | 136 / 206 | **+0 $** [−32 $ ; +32 $] | 17 / 238 | −0 $ | +0 $ | +0 $ | +0 $ | 0/0 |
| 2 | H08 pire perte limitée à −10 $ | **+0 $** [−259 $ ; +224 $] | 22 / 350 | **−0 $** [−249 $ ; +226 $] | 19 / 234 | −0 $ | +0 $ | −0 $ | +0 $ | 0/0 |
| 3 | H10 couvrir ou vendre (avantage net) | **+0 $** [−1 358 $ ; +1 449 $] | 138 / 200 | **+0 $** [−66 $ ; +66 $] | 17 / 238 | +1 $ | −0 $ | +0 $ | +0 $ | 0/0 |
| 4 | H07 pire perte limitée à −25 $ | **+0 $** [+0 $ ; +0 $] | 7 / 370 | **+0 $** [−169 $ ; +165 $] | 18 / 235 | −0 $ | +0 $ | +0 $ | +0 $ | 0/0 |
| 5 | H12 horloge de risque (immédiat / attendre 3 s) | **+0 $** [+0 $ ; +0 $] | 7 / 370 | **+0 $** [−66 $ ; +66 $] | 15 / 241 | −0 $ | +0 $ | +0 $ | +0 $ | 0/0 |
| 6 | H13 prédictive 1 s | **+0 $** [+0 $ ; +0 $] | 7 / 370 | **+0 $** [−66 $ ; +66 $] | 15 / 241 | −0 $ | −0 $ | +0 $ | +0 $ | 0/0 |
| 7 | H14 prédictive 3 s | **+0 $** [+0 $ ; +0 $] | 7 / 370 | **+0 $** [−70 $ ; +70 $] | 15 / 241 | −0 $ | +0 $ | −0 $ | +0 $ | 0/0 |
| 8 | H16 prédictive 10 s | **+0 $** [+0 $ ; +0 $] | 7 / 370 | **+0 $** [−66 $ ; +66 $] | 15 / 241 | −0 $ | −0 $ | +0 $ | +0 $ | 0/0 |
| 9 | H17 premier passage (limite si EV > immédiat) | **+0 $** [+0 $ ; +0 $] | 7 / 370 | **+0 $** [−66 $ ; +66 $] | 15 / 241 | +1 $ | −0 $ | +0 $ | +0 $ | 0/0 |
| 10 | H22 hybride 50 % immédiat + 50 % passif | **+0 $** [+0 $ ; +0 $] | 7 / 370 | **+0 $** [−66 $ ; +66 $] | 15 / 241 | −0 $ | −0 $ | +0 $ | −0 $ | 0/0 |
| 11 | H24 moteur d'inventaire deux jambes | **+0 $** [+0 $ ; +0 $] | 7 / 370 | **−0 $** [−36 $ ; +36 $] | 10 / 246 | +0 $ | −0 $ | −0 $ | +0 $ | 0/0 |
| 12 | H01 verrouillage paire complète (coût < 1) | **+0 $** [−256 $ ; +256 $] | 22 / 350 | **+0 $** [−53 $ ; +53 $] | 17 / 238 | +0 $ | +0 $ | +0 $ | −0 $ | 0/0 |
| 13 | H02 verrouillage partiel 25 % | **+0 $** [−0 $ ; +0 $] | 7 / 370 | **+0 $** [−15 $ ; +15 $] | 14 / 242 | +0 $ | −0 $ | −0 $ | −0 $ | 0/0 |
| 14 | H03 verrouillage partiel 50 % | **+0 $** [−324 $ ; +309 $] | 39 / 329 | **−0 $** [−28 $ ; +28 $] | 15 / 241 | −0 $ | −0 $ | +0 $ | +0 $ | 0/0 |
| 15 | H09 pire issue à 0 dans le budget (après modèle −10) | **+0 $** [+0 $ ; +0 $] | 7 / 370 | **+0 $** [−100 $ ; +100 $] | 17 / 238 | −0 $ | −0 $ | +0 $ | +0 $ | 0/0 |
| 16 | H15 prédictive 5 s | **+0 $** [+0 $ ; +0 $] | 7 / 370 | **−0 $** [−66 $ ; +66 $] | 15 / 241 | +0 $ | +0 $ | +0 $ | +0 $ | 0/0 |
| 17 | H18 fenêtre de conversion prédite (paire ≤ 0,95) — inactive si seuil appris = jamais | **+0 $** [+0 $ ; +0 $] | 7 / 370 | **+0 $** [+0 $ ; +0 $] | 13 / 243 | +0 $ | −0 $ | +0 $ | +0 $ | 0/0 |
| 18 | H19 sauvetage passif (vendeur − 1 c, 10 s) | **+0 $** [+0 $ ; +0 $] | 7 / 370 | **−0 $** [−8 $ ; +8 $] | 14 / 242 | +0 $ | −0 $ | +0 $ | +0 $ | 0/0 |
| 19 | H20 prédicteur de file (traversée) passif sinon immédiat | **+0 $** [+0 $ ; +0 $] | 7 / 370 | **−0 $** [−67 $ ; +67 $] | 15 / 241 | −0 $ | −0 $ | +0 $ | +0 $ | 0/0 |
| 20 | H21 recharge du carnet | **+0 $** [+0 $ ; +0 $] | 7 / 370 | **+0 $** [−66 $ ; +66 $] | 15 / 241 | −0 $ | +0 $ | +0 $ | +0 $ | 0/0 |
| 21 | H23 boomerang (revente de l'opposé +5 c) | **+0 $** [−0 $ ; +0 $] | 7 / 370 | **+0 $** [−159 $ ; +159 $] | 9 / 248 | −0 $ | −0 $ | −0 $ | +0 $ | 0/0 |
| 22 | H05 réserve jackpot (≥ 70 % gardé) | **−0 $** [+0 $ ; +0 $] | 9 / 368 | **+0 $** [−19 $ ; +19 $] | 15 / 241 | +0 $ | −0 $ | +0 $ | +0 $ | 0/0 |
| 23 | H06 échelle de paires (4 tranches) | **−0 $** [−278 $ ; +278 $] | 22 / 350 | **+0 $** [−81 $ ; +81 $] | 17 / 238 | −0 $ | −0 $ | +0 $ | +0 $ | 0/0 |
| 24 | H11 alerte précoce (2 signaux sur 3) 25 % | **−0 $** [−0 $ ; +0 $] | 7 / 370 | **+0 $** [−30 $ ; +30 $] | 15 / 241 | +0 $ | +0 $ | +0 $ | −0 $ | 0/0 |

Référence GARDER (prudent, 250 $) : validation 7 positions jouées, 370 refusées faute de capital, −250 $, creux −250 $ · test 13 jouées, 243 refusées, −250 $, creux −352 $.

### C · V2-F original (diagnostic) — 50 $ indépendants (chaque position seule, capital illimité ; informatif)

| Rang | Couverture | Δ vs GARDER valid. prudent [IC 90 %] | Δ test prudent [IC 90 %] | Δ app. prudent | valid. idéal | valid. pessimiste | test idéal | test pessimiste | Δ vs VENDRE 50 % (valid. / test) | Δ vs VENDRE 100 % (valid. / test) | Jackpots gardés (valid.) | Profit sacrifié jackpots (valid.) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | H23 boomerang (revente de l'opposé +5 c) | **+3 $** [−1 093 $ ; +1 009 $] | **−660 $** [−1 474 $ ; +43 $] | −1 337 $ | −1 598 $ | +109 $ | −565 $ | −141 $ | +188 $ / −1 100 $ | +385 $ / −1 526 $ | 9/14 | +790 $ |
| 2 | H18 fenêtre de conversion prédite (paire ≤ 0,95) — inactive si seuil appris = jamais | **−0 $** [+0 $ ; +0 $] | **+0 $** [+0 $ ; +0 $] | −0 $ | −0 $ | +0 $ | −0 $ | +0 $ | −0 $ / +0 $ | −0 $ / +0 $ | 14/14 | +0 $ |
| 3 | H02 verrouillage partiel 25 % | **−67 $** [−742 $ ; +544 $] | **+192 $** [−198 $ ; +570 $] | −548 $ | −355 $ | −39 $ | +10 $ | +203 $ | +117 $ / −248 $ | +314 $ / −674 $ | 8/14 | +711 $ |
| 4 | H05 réserve jackpot (≥ 70 % gardé) | **−102 $** [−950 $ ; +677 $] | **+230 $** [−240 $ ; +698 $] | −702 $ | −483 $ | −56 $ | −33 $ | +256 $ | +83 $ / −210 $ | +280 $ / −636 $ | 7/14 | +906 $ |
| 5 | H19 sauvetage passif (vendeur − 1 c, 10 s) | **−149 $** [−938 $ ; +441 $] | **−193 $** [−658 $ ; +176 $] | −114 $ | −635 $ | +228 $ | −223 $ | −200 $ | +530 $ / −143 $ | +1 220 $ / −81 $ | 13/14 | +315 $ |
| 6 | H03 verrouillage partiel 50 % | **−163 $** [−1 450 $ ; +994 $] | **+373 $** [−411 $ ; +1 119 $] | −1 067 $ | −711 $ | −81 $ | +19 $ | +379 $ | +21 $ / −67 $ | +218 $ / −493 $ | 4/14 | +1 423 $ |
| 7 | H11 alerte précoce (2 signaux sur 3) 25 % | **−166 $** [−714 $ ; +363 $] | **+249 $** [−53 $ ; +530 $] | −468 $ | +21 $ | −116 $ | +374 $ | +235 $ | +179 $ / −241 $ | +531 $ / −702 $ | 8/14 | +766 $ |
| 8 | H24 moteur d'inventaire deux jambes | **−229 $** [−750 $ ; +292 $] | **−565 $** [−1 009 $ ; −134 $] | −398 $ | −522 $ | −321 $ | −844 $ | −494 $ | +188 $ / −1 056 $ | +583 $ / −1 518 $ | 10/14 | +12 $ |
| 9 | H04 plancher de profit (les 2 issues ≥ 0) | **−332 $** [−2 264 $ ; +1 539 $] | **+677 $** [−620 $ ; +1 982 $] | −1 497 $ | −1 313 $ | −119 $ | +38 $ | +628 $ | −147 $ / +237 $ | +50 $ / −189 $ | 2/14 | +2 298 $ |
| 10 | H06 échelle de paires (4 tranches) | **−348 $** [−2 739 $ ; +1 970 $] | **+524 $** [−898 $ ; +1 859 $] | −2 017 $ | −1 209 $ | −28 $ | −40 $ | +374 $ | −164 $ / +84 $ | +34 $ / −342 $ | 0/14 | +2 739 $ |
| 11 | H01 verrouillage paire complète (coût < 1) | **−367 $** [−2 888 $ ; +2 012 $] | **+698 $** [−856 $ ; +2 226 $] | −2 083 $ | −1 421 $ | −193 $ | +38 $ | +669 $ | −182 $ / +258 $ | +15 $ / −168 $ | 0/14 | +2 832 $ |
| 12 | H08 pire perte limitée à −10 $ | **−454 $** [−2 730 $ ; +1 639 $] | **+941 $** [−825 $ ; +2 469 $] | −2 708 $ | −1 141 $ | −552 $ | +699 $ | +984 $ | −260 $ / +454 $ | −38 $ / −10 $ | 7/14 | +2 143 $ |
| 13 | H09 pire issue à 0 dans le budget (après modèle −10) | **−630 $** [−1 574 $ ; +292 $] | **+214 $** [+29 $ ; +429 $] | −590 $ | −1 031 $ | −426 $ | +236 $ | +97 $ | +49 $ / +265 $ | +738 $ / +327 $ | 11/14 | +855 $ |
| 14 | H07 pire perte limitée à −25 $ | **−921 $** [−2 945 $ ; +914 $] | **+225 $** [−916 $ ; +1 302 $] | −340 $ | −1 184 $ | −1 251 $ | +326 $ | +115 $ | −487 $ / +95 $ | −22 $ / −21 $ | 8/14 | +2 058 $ |
| 15 | H21 recharge du carnet | **−1 334 $** [−3 066 $ ; +118 $] | **−30 $** [−573 $ ; +477 $] | −228 $ | −1 219 $ | −965 $ | +144 $ | −103 $ | −655 $ / +20 $ | +34 $ / +83 $ | 10/14 | +1 464 $ |
| 16 | H16 prédictive 10 s | **−1 358 $** [−3 069 $ ; +103 $] | **−143 $** [−793 $ ; +431 $] | −349 $ | −1 059 $ | −984 $ | +101 $ | −210 $ | −679 $ / −93 $ | +11 $ / −31 $ | 10/14 | +1 450 $ |
| 17 | H17 premier passage (limite si EV > immédiat) | **−1 367 $** [−3 035 $ ; +74 $] | **−112 $** [−743 $ ; +463 $] | −334 $ | −1 075 $ | −984 $ | +144 $ | −197 $ | −688 $ / −62 $ | +1 $ / +1 $ | 10/14 | +1 450 $ |
| 18 | H13 prédictive 1 s | **−1 368 $** [−3 083 $ ; +108 $] | **−112 $** [−757 $ ; +441 $] | −334 $ | −1 055 $ | −984 $ | +145 $ | −196 $ | −690 $ / −62 $ | −0 $ / +1 $ | 10/14 | +1 450 $ |
| 19 | H10 couvrir ou vendre (avantage net) | **−1 368 $** [−3 041 $ ; +81 $] | **−113 $** [−761 $ ; +448 $] | −334 $ | −1 055 $ | −984 $ | +135 $ | −197 $ | −690 $ / −63 $ | −0 $ / −0 $ | 10/14 | +1 450 $ |
| 20 | H15 prédictive 5 s | **−1 397 $** [−3 075 $ ; +41 $] | **−44 $** [−551 $ ; +462 $] | −247 $ | −1 196 $ | −1 019 $ | +160 $ | −101 $ | −718 $ / +6 $ | −28 $ / +69 $ | 10/14 | +1 448 $ |
| 21 | H14 prédictive 3 s | **−1 397 $** [−3 032 $ ; +33 $] | **−83 $** [−625 $ ; +437 $] | −330 $ | −1 383 $ | −999 $ | +24 $ | −115 $ | −719 $ / −33 $ | −29 $ / +30 $ | 10/14 | +1 450 $ |
| 22 | H20 prédicteur de file (traversée) passif sinon immédiat | **−1 406 $** [−3 052 $ ; +84 $] | **−123 $** [−752 $ ; +430 $] | −333 $ | −1 155 $ | −1 041 $ | +91 $ | −196 $ | −728 $ / −73 $ | −38 $ / −11 $ | 10/14 | +1 455 $ |
| 23 | H22 hybride 50 % immédiat + 50 % passif | **−1 410 $** [−3 092 $ ; +1 $] | **−122 $** [−743 $ ; +435 $] | −448 $ | −1 263 $ | −1 019 $ | +71 $ | −192 $ | −731 $ / −72 $ | −41 $ / −9 $ | 10/14 | +1 443 $ |
| 24 | H12 horloge de risque (immédiat / attendre 3 s) | **−1 419 $** [−3 196 $ ; +34 $] | **−123 $** [−750 $ ; +434 $] | −378 $ | −1 135 $ | −1 016 $ | +111 $ | −204 $ | −740 $ / −72 $ | −50 $ / −10 $ | 10/14 | +1 450 $ |

Référence GARDER (50 $ indépendants) : validation prudent 299 positions −1 567 $ (idéal 379 positions −669 $, pessimiste 277 positions −1 215 $) · test prudent 196 positions −2 394 $ (idéal −1 974 $, pessimiste −2 121 $).

## 4. Les quatre candidates de Pitch : pourquoi elles gagnent ou perdent (mécanique, chiffres)

Chiffres en « 50 $ indépendants » (le portefeuille de 250 $ est ruiné, section 3), scénario prudent sauf mention.

### H10 — couvrir ou vendre

- Sur 920 déclenchements (A + B + C, toutes périodes), l'avantage brut 1 − vendeur opposé − acheteur de notre côté vaut **exactement 0** dans 100,0 % des cas (médiane 0,000, min −0,000, max 0,000) : le carnet Down est le miroir du carnet Up (vendeur Down = 1 − acheteur Up, même taille). Les frais sont symétriques (0,072·p·(1−p) est le même pour p et 1 − p) : l'avantage net est nul aussi. Acheter l'opposé = vendre sa position au même prix, mêmes frais, même quantité disponible — mais en immobilisant le capital jusqu'au règlement. La règle « neutraliser seulement si c'est mieux » choisit donc (presque) toujours **vendre**, et à égalité vendre est meilleur (capital libéré).
- Vérification : H10 et VENDRE 100 % au même instant donnent le même P&L (Δ vs VENDRE 100 % : A valid. −0 $, test +0 $ · B valid. +0 $, test +0 $) ; la couverture immédiate au marché (H13 avec seuil « jamais attendre » ou H20 branche immédiate) donne aussi le même P&L à la ligne près.
- Ce qui décide du résultat n'est donc pas « couvrir ou vendre » mais « sortir ou garder » après modèle −10 : A Δ vs GARDER valid. −35 $ [−308 $ ; +142 $], test −28 $ [−111 $ ; +22 $], jackpots gardés valid. 5/5 · B Δ vs GARDER valid. −954 $ [−2 110 $ ; +133 $], test +902 $ [+364 $ ; +1 445 $], jackpots gardés valid. 2/5. Le signe change entre validation et test : pas d'avantage stable.

### H17 — premier passage (ordre passif seulement si son espérance bat l'achat immédiat)

Hausse moyenne du vendeur opposé 10 s après la décision quand l'ordre n'est pas rempli (apprentissage) : −1 c : 4,13 c, −2 c : 3,90 c, −3 c : 3,70 c, −5 c : 3,35 c.
- A validation : 18 déclenchements ; décisions {'immédiat': 18} ; ordres passifs posés 0, remplis (au moins en partie) 0 ; prix moyen opposé 0,95 ; Δ vs GARDER −35 $ [−322 $ ; +138 $] ; Δ vs VENDRE 100 % au même instant +0 $ ; idéal +222 $, pessimiste −36 $.
- A inédit : 5 déclenchements ; décisions {'immédiat': 5} ; ordres passifs posés 0, remplis (au moins en partie) 0 ; prix moyen opposé 0,98 ; Δ vs GARDER −28 $ [−110 $ ; +22 $] ; Δ vs VENDRE 100 % au même instant +0 $ ; idéal −101 $, pessimiste +6 $.
- B validation : 104 déclenchements ; décisions {'immédiat': 103, 'limite −3 c': 1} ; ordres passifs posés 1, remplis (au moins en partie) 0 ; prix moyen opposé 0,86 ; Δ vs GARDER −948 $ [−2 175 $ ; +232 $] ; Δ vs VENDRE 100 % au même instant +7 $ ; idéal −648 $, pessimiste −602 $.
- B inédit : 78 déclenchements ; décisions {'immédiat': 74, 'limite −3 c': 2, 'limite −5 c': 2} ; ordres passifs posés 4, remplis (au moins en partie) 2 ; prix moyen opposé 0,86 ; Δ vs GARDER +908 $ [+374 $ ; +1 447 $] ; Δ vs VENDRE 100 % au même instant +6 $ ; idéal +1 252 $, pessimiste +873 $.
- Mécanique : l'EV n'est positive que si P(traversée) est élevée, or juste après le déclencheur modèle −10 le vendeur opposé a tendance à **monter** (notre côté baisse) : la règle choisit presque toujours l'immédiat, donc H17 ≈ vendre au déclencheur. Les rares ordres passifs posés ne sont pas servis assez souvent (file inconnue, traversée exigée) pour compenser la hausse payée au repli.

### H21 — recharge du carnet

- Photos 100 ms (toutes les photos, les deux jetons) : 3777 sauts ≥ 2 c du meilleur vendeur ; retour au niveau d'avant en 0,5 s : 7,8 %, 1 s : 13,4 %, 2 s : 21,7 %, 5 s : 36,8 %. Les lignes 0,3 s ne voient pas les recharges plus rapides que ~0,3 s.
- A validation : 18 déclenchements, saut ≥ 2 c dans la seconde précédente dans 9 cas, retour au niveau d'avant dans les 5 s dans 1 ; prix moyen opposé 0,94 ; Δ vs GARDER −47 $ [−311 $ ; +131 $] ; Δ vs VENDRE 100 % au même instant −12 $ ; idéal +119 $.
- A inédit : 5 déclenchements, saut ≥ 2 c dans la seconde précédente dans 4 cas, retour au niveau d'avant dans les 5 s dans 0 ; prix moyen opposé 0,96 ; Δ vs GARDER −30 $ [−116 $ ; +20 $] ; Δ vs VENDRE 100 % au même instant −1 $ ; idéal −79 $.
- B validation : 104 déclenchements, saut ≥ 2 c dans la seconde précédente dans 51 cas, retour au niveau d'avant dans les 5 s dans 4 ; prix moyen opposé 0,85 ; Δ vs GARDER −833 $ [−2 062 $ ; +314 $] ; Δ vs VENDRE 100 % au même instant +121 $ ; idéal −875 $.
- B inédit : 78 déclenchements, saut ≥ 2 c dans la seconde précédente dans 40 cas, retour au niveau d'avant dans les 5 s dans 6 ; prix moyen opposé 0,86 ; Δ vs GARDER +843 $ [+327 $ ; +1 366 $] ; Δ vs VENDRE 100 % au même instant −59 $ ; idéal +1 100 $.
- Mécanique : sans saut, H21 EST la couverture immédiate, donc une vente au prix miroir. Juste après le déclencheur modèle −10, un saut du vendeur opposé ne revient presque jamais au niveau d'avant dans les 5 s (chiffres ci-dessus), alors qu'au hasard des photos 100 ms il revient dans ~37 % des cas : à ce moment-là le saut est un vrai mouvement du marché (notre côté baisse), pas un trou de liquidité. Attendre la recharge revient donc à vendre plus tard, souvent plus bas ; et la cadence 0,3 s + délai ne permet pas de saisir les recharges à 100 ms.

### H23 — boomerang

- A validation : paire < 1 atteinte dans 20 positions ; opposé acheté dans 20 ; revendu (+5 c) dans 15 ; P&L −318 $ contre −317 $ en gardant la couverture (H01) et −293 $ en gardant sans couvrir ; Δ vs GARDER −24 $ [−207 $ ; +134 $] ; Δ vs VENDRE 100 % au même instant +144 $ ; jackpots gardés 2/5.
- A inédit : paire < 1 atteinte dans 22 positions ; opposé acheté dans 19 ; revendu (+5 c) dans 14 ; P&L −577 $ contre −404 $ en gardant la couverture (H01) et −411 $ en gardant sans couvrir ; Δ vs GARDER −166 $ [−650 $ ; +163 $] ; Δ vs VENDRE 100 % au même instant −288 $ ; jackpots gardés 1/5.
- B validation : paire < 1 atteinte dans 95 positions ; opposé acheté dans 91 ; revendu (+5 c) dans 71 ; P&L −434 $ contre −1 058 $ en gardant la couverture (H01) et −70 $ en gardant sans couvrir ; Δ vs GARDER −364 $ [−1 016 $ ; +207 $] ; Δ vs VENDRE 100 % au même instant +569 $ ; jackpots gardés 4/5.
- B inédit : paire < 1 atteinte dans 78 positions ; opposé acheté dans 69 ; revendu (+5 c) dans 63 ; P&L −1 303 $ contre −884 $ en gardant la couverture (H01) et −1 583 $ en gardant sans couvrir ; Δ vs GARDER +280 $ [+30 $ ; +544 $] ; Δ vs VENDRE 100 % au même instant −693 $ ; jackpots gardés 4/5.
- Mécanique : la paire < 1 n'arrive que quand notre côté a monté (miroir : paire < 1 ⇔ acheteur de notre côté > prix d'entrée + frais) — c'est une prise de bénéfice. La revente de l'opposé à +5 c redonne l'exposition au moment où notre côté redescend : le boomerang est un pari sur le retour de notre côté, pas une couverture ; il récupère une partie des jackpots que H01 sacrifie, mais paie deux fois l'écart et les frais.

## 5. Tableaux complets (portefeuille 250 $, chronologique)

Δ vs GARDER : somme sur TOUTES les positions (couvertes ou non) du P&L avec la couverture − P&L en gardant, frais compris ; IC 90 % par bootstrap de blocs d'une heure. Δ vs VENDRE : P&L couverture − P&L de la vente (50 % ou 100 %) au même instant ; positif = la couverture fait mieux que vendre. Quantité couverte = (parts opposées achetées + parts vendues) / parts d'entrée, sur les positions où la couverture a exécuté. Entrées réduites / refusées = faute de capital dans le portefeuille de 250 $.

### A · désaccord 30 zone + modèle monte — idéal — validation

| Couverture | Positions | Tentées | Exécutées | Taux d'exécution | Prix moyen opposé | Quantité couverte moy. | P&L net | Δ vs GARDER [IC 90 %] | Δ vs VENDRE 50 % | Δ vs VENDRE 100 % | Creux max | Perte max (1 position) | Plus longue série perdante | Jackpots gardés | Profit sacrifié (jackpots) | Profit verrouillé (paires) | P&L des positions non couvertes | Capital immobilisé max | Entrées réduites / refusées |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| GARDER (référence) | 62 | — | — | — | — | — | +753 $ | 0 | — | — | −219 $ | −50 $ | 5 | 14/14 | 0 $ | 0 $ | +753 $ | +50 $ | 0/0 |
| H01 verrouillage paire complète (coût < 1) | 62 | 44 | 44 | 100,0 % | 0,69 | 100,0 % | −219 $ | **−972 $** [−1 785 $ ; −115 $] | −466 $ | +31 $ | −337 $ | −50 $ | 3 | 0/14 | +1 173 $ | +489 $ | −708 $ | +50 $ | 2/0 |
| H02 verrouillage partiel 25 % | 62 | 44 | 44 | 100,0 % | 0,70 | 25,0 % | +500 $ | **−253 $** [−463 $ ; −54 $] | +253 $ | +750 $ | −218 $ | −50 $ | 5 | 8/14 | +293 $ | +112 $ | −708 $ | +50 $ | 0/0 |
| H03 verrouillage partiel 50 % | 62 | 44 | 44 | 100,0 % | 0,70 | 50,0 % | +247 $ | **−507 $** [−943 $ ; −122 $] | +0 $ | +497 $ | −223 $ | −50 $ | 4 | 0/14 | +586 $ | +224 $ | −708 $ | +50 $ | 0/0 |
| H04 plancher de profit (les 2 issues ≥ 0) | 62 | 44 | 44 | 100,0 % | 0,73 | 70,9 % | +6 $ | **−747 $** [−1 497 $ ; −83 $] | −240 $ | +256 $ | −263 $ | −50 $ | 3 | 3/14 | +929 $ | +237 $ | −708 $ | +50 $ | 0/0 |
| H05 réserve jackpot (≥ 70 % gardé) | 62 | 44 | 44 | 100,0 % | 0,65 | 38,9 % | +394 $ | **−360 $** [−639 $ ; −91 $] | +147 $ | +644 $ | −236 $ | −50 $ | 5 | 0/14 | +398 $ | +242 $ | −708 $ | +50 $ | 0/0 |
| H06 échelle de paires (4 tranches) | 62 | 44 | 44 | 100,0 % | 0,65 | 92,0 % | −196 $ | **−949 $** [−1 829 $ ; −150 $] | −443 $ | +54 $ | −271 $ | −50 $ | 3 | 0/14 | +1 119 $ | +649 $ | −708 $ | +50 $ | 0/0 |
| H07 pire perte limitée à −25 $ | 62 | 29 | 29 | 100,0 % | 0,93 | 100,0 % | +344 $ | **−409 $** [−1 093 $ ; +152 $] | −204 $ | +1 $ | −243 $ | −50 $ | 6 | 13/14 | +294 $ | −886 $ | +1 230 $ | +50 $ | 0/0 |
| H08 pire perte limitée à −10 $ | 62 | 39 | 39 | 100,0 % | 0,87 | 100,0 % | +251 $ | **−502 $** [−1 336 $ ; +192 $] | −251 $ | −0 $ | −179 $ | −26 $ | 8 | 10/14 | +875 $ | −583 $ | +835 $ | +50 $ | 0/0 |
| H09 pire issue à 0 dans le budget (après modèle −10) | 62 | 25 | 6 | 24,0 % | 0,66 | 75,4 % | +826 $ | **+73 $** [−56 $ ; +213 $] | −38 $ | −149 $ | −219 $ | −50 $ | 4 | 14/14 | +0 $ | +50 $ | +756 $ | +50 $ | 0/0 |
| H10 couvrir ou vendre (avantage net) | 62 | 25 | 25 | 100,0 % | — | 100,0 % | +975 $ | **+222 $** [−69 $ ; +492 $] | +111 $ | +0 $ | −192 $ | −50 $ | 5 | 14/14 | +0 $ | +0 $ | +1 466 $ | +50 $ | 0/0 |
| H11 alerte précoce (2 signaux sur 3) 25 % | 62 | 47 | 47 | 100,0 % | 0,82 | 25,0 % | +583 $ | **−170 $** [−384 $ ; +32 $] | +170 $ | +511 $ | −209 $ | −50 $ | 5 | 9/14 | +212 $ | −63 $ | +326 $ | +50 $ | 0/0 |
| H12 horloge de risque (immédiat / attendre 3 s) | 62 | 25 | 22 | 88,0 % | 0,89 | 100,0 % | +939 $ | **+185 $** [−129 $ ; +428 $] | +74 $ | −36 $ | −192 $ | −50 $ | 5 | 14/14 | +0 $ | −379 $ | +1 317 $ | +50 $ | 0/0 |
| H13 prédictive 1 s | 62 | 25 | 25 | 100,0 % | 0,90 | 100,0 % | +975 $ | **+222 $** [−81 $ ; +485 $] | +111 $ | −0 $ | −192 $ | −50 $ | 5 | 14/14 | +0 $ | −491 $ | +1 466 $ | +50 $ | 0/0 |
| H14 prédictive 3 s | 62 | 25 | 25 | 100,0 % | 0,92 | 100,0 % | +917 $ | **+163 $** [−125 $ ; +391 $] | +53 $ | −58 $ | −199 $ | −50 $ | 5 | 14/14 | +0 $ | −549 $ | +1 466 $ | +50 $ | 0/0 |
| H15 prédictive 5 s | 62 | 25 | 25 | 100,0 % | 0,90 | 100,0 % | +970 $ | **+217 $** [−68 $ ; +478 $] | +106 $ | −5 $ | −192 $ | −50 $ | 5 | 14/14 | +0 $ | −496 $ | +1 466 $ | +50 $ | 0/0 |
| H16 prédictive 10 s | 62 | 25 | 25 | 100,0 % | 0,90 | 100,0 % | +973 $ | **+220 $** [−90 $ ; +479 $] | +109 $ | −2 $ | −192 $ | −50 $ | 5 | 14/14 | +0 $ | −493 $ | +1 466 $ | +50 $ | 0/0 |
| H17 premier passage (limite si EV > immédiat) | 62 | 25 | 25 | 100,0 % | 0,90 | 100,0 % | +975 $ | **+222 $** [−61 $ ; +491 $] | +111 $ | −0 $ | −192 $ | −50 $ | 5 | 14/14 | +0 $ | −491 $ | +1 466 $ | +50 $ | 0/0 |
| H18 fenêtre de conversion prédite (paire ≤ 0,95) — inactive si seuil appris = jamais | 62 | 0 | 0 | — | — | — | +753 $ | **−0 $** [+0 $ ; +0 $] | −0 $ | −0 $ | −219 $ | −50 $ | 5 | 14/14 | +0 $ | +0 $ | +753 $ | +50 $ | 0/0 |
| H19 sauvetage passif (vendeur − 1 c, 10 s) | 62 | 25 | 5 | 20,0 % | 0,89 | 94,3 % | +668 $ | **−85 $** [−394 $ ; +116 $] | −196 $ | −307 $ | −218 $ | −50 $ | 5 | 14/14 | +0 $ | −90 $ | +772 $ | +50 $ | 0/0 |
| H20 prédicteur de file (traversée) passif sinon immédiat | 62 | 25 | 25 | 100,0 % | 0,90 | 100,0 % | +978 $ | **+224 $** [−71 $ ; +490 $] | +113 $ | +3 $ | −192 $ | −50 $ | 5 | 14/14 | +0 $ | −488 $ | +1 466 $ | +50 $ | 0/0 |
| H21 recharge du carnet | 62 | 25 | 22 | 88,0 % | 0,91 | 100,0 % | +872 $ | **+119 $** [−146 $ ; +338 $] | +8 $ | −103 $ | −194 $ | −50 $ | 5 | 14/14 | +0 $ | −455 $ | +1 327 $ | +50 $ | 0/0 |
| H22 hybride 50 % immédiat + 50 % passif | 62 | 25 | 25 | 100,0 % | 0,91 | 84,0 % | +890 $ | **+137 $** [−132 $ ; +362 $] | +26 $ | −85 $ | −198 $ | −50 $ | 5 | 14/14 | +0 $ | −452 $ | +1 466 $ | +50 $ | 0/0 |
| H23 boomerang (revente de l'opposé +5 c) | 62 | 44 | 42 | 95,5 % | 0,69 | 100,0 % | −90 $ | **−843 $** [−1 475 $ ; −302 $] | −337 $ | +160 $ | −383 $ | −50 $ | 5 | 5/14 | +620 $ | +271 $ | −523 $ | +50 $ | 2/0 |
| H24 moteur d'inventaire deux jambes | 62 | 62 | 62 | 100,0 % | 0,63 | 27,7 % | +690 $ | **−63 $** [−315 $ ; +184 $] | +392 $ | +847 $ | −258 $ | −66 $ | 5 | 5/14 | +106 $ | +241 $ | +0 $ | +68 $ | 0/0 |

### A · désaccord 30 zone + modèle monte — idéal — inédit

| Couverture | Positions | Tentées | Exécutées | Taux d'exécution | Prix moyen opposé | Quantité couverte moy. | P&L net | Δ vs GARDER [IC 90 %] | Δ vs VENDRE 50 % | Δ vs VENDRE 100 % | Creux max | Perte max (1 position) | Plus longue série perdante | Jackpots gardés | Profit sacrifié (jackpots) | Profit verrouillé (paires) | P&L des positions non couvertes | Capital immobilisé max | Entrées réduites / refusées |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| GARDER (référence) | 47 | — | — | — | — | — | +273 $ | 0 | — | — | −318 $ | −50 $ | 6 | 8/8 | 0 $ | 0 $ | +273 $ | +50 $ | 0/0 |
| H01 verrouillage paire complète (coût < 1) | 47 | 33 | 33 | 100,0 % | 0,72 | 100,0 % | −36 $ | **−309 $** [−945 $ ; +243 $] | −157 $ | −4 $ | −120 $ | −50 $ | 3 | 0/8 | +641 $ | +370 $ | −406 $ | +50 $ | 0/0 |
| H02 verrouillage partiel 25 % | 47 | 33 | 33 | 100,0 % | 0,71 | 25,0 % | +197 $ | **−76 $** [−237 $ ; +67 $] | +76 $ | +229 $ | −256 $ | −50 $ | 6 | 2/8 | +160 $ | +93 $ | −406 $ | +50 $ | 0/0 |
| H03 verrouillage partiel 50 % | 47 | 33 | 33 | 100,0 % | 0,71 | 50,0 % | +120 $ | **−153 $** [−464 $ ; +145 $] | +0 $ | +153 $ | −195 $ | −50 $ | 6 | 1/8 | +320 $ | +187 $ | −406 $ | +50 $ | 0/0 |
| H04 plancher de profit (les 2 issues ≥ 0) | 47 | 33 | 33 | 100,0 % | 0,74 | 78,1 % | +7 $ | **−266 $** [−878 $ ; +280 $] | −113 $ | +40 $ | −110 $ | −50 $ | 3 | 1/8 | +521 $ | +198 $ | −406 $ | +50 $ | 0/0 |
| H05 réserve jackpot (≥ 70 % gardé) | 47 | 33 | 33 | 100,0 % | 0,68 | 36,3 % | +143 $ | **−130 $** [−329 $ ; +59 $] | +23 $ | +176 $ | −250 $ | −50 $ | 6 | 0/8 | +216 $ | +188 $ | −406 $ | +50 $ | 0/0 |
| H06 échelle de paires (4 tranches) | 47 | 33 | 33 | 100,0 % | 0,64 | 86,6 % | +2 $ | **−271 $** [−685 $ ; +114 $] | −119 $ | +34 $ | −145 $ | −50 $ | 5 | 0/8 | +553 $ | +597 $ | −406 $ | +50 $ | 0/0 |
| H07 pire perte limitée à −25 $ | 10 | 5 | 4 | 80,0 % | 0,92 | 100,0 % | −250 $ | **−523 $** [−1 258 $ ; +183 $] | −499 $ | −133 $ | −250 $ | −50 $ | 10 | 0/8 | +0 $ | −117 $ | −133 $ | +50 $ | 38/37 |
| H08 pire perte limitée à −10 $ | 47 | 30 | 30 | 100,0 % | 0,87 | 100,0 % | +34 $ | **−239 $** [−1 072 $ ; +446 $] | −121 $ | −4 $ | −177 $ | −50 $ | 11 | 5/8 | +493 $ | −427 $ | +462 $ | +50 $ | 0/0 |
| H09 pire issue à 0 dans le budget (après modèle −10) | 47 | 10 | 5 | 50,0 % | 0,49 | 55,4 % | +281 $ | **+8 $** [−84 $ ; +111 $] | +58 $ | +108 $ | −264 $ | −50 $ | 6 | 7/8 | +44 $ | +69 $ | +19 $ | +50 $ | 0/0 |
| H10 couvrir ou vendre (avantage net) | 47 | 10 | 10 | 100,0 % | — | 100,0 % | +172 $ | **−101 $** [−336 $ ; +121 $] | −50 $ | +0 $ | −275 $ | −50 $ | 6 | 6/8 | +178 $ | +0 $ | +172 $ | +50 $ | 0/0 |
| H11 alerte précoce (2 signaux sur 3) 25 % | 47 | 20 | 20 | 100,0 % | 0,79 | 25,0 % | +315 $ | **+42 $** [−44 $ ; +121 $] | −42 $ | −125 $ | −256 $ | −50 $ | 6 | 7/8 | +43 $ | +6 $ | +416 $ | +50 $ | 0/0 |
| H12 horloge de risque (immédiat / attendre 3 s) | 47 | 10 | 10 | 100,0 % | 0,78 | 100,0 % | +172 $ | **−101 $** [−335 $ ; +105 $] | −50 $ | −0 $ | −254 $ | −50 $ | 6 | 6/8 | +156 $ | +1 $ | +172 $ | +50 $ | 0/0 |
| H13 prédictive 1 s | 47 | 10 | 10 | 100,0 % | 0,78 | 100,0 % | +171 $ | **−102 $** [−338 $ ; +120 $] | −52 $ | −1 $ | −275 $ | −50 $ | 6 | 6/8 | +178 $ | −0 $ | +172 $ | +50 $ | 0/0 |
| H14 prédictive 3 s | 47 | 10 | 10 | 100,0 % | 0,79 | 100,0 % | +167 $ | **−106 $** [−345 $ ; +97 $] | −55 $ | −5 $ | −259 $ | −50 $ | 6 | 6/8 | +156 $ | −4 $ | +172 $ | +50 $ | 0/0 |
| H15 prédictive 5 s | 47 | 10 | 10 | 100,0 % | 0,80 | 100,0 % | +140 $ | **−133 $** [−404 $ ; +90 $] | −83 $ | −32 $ | −274 $ | −50 $ | 6 | 6/8 | +178 $ | −32 $ | +172 $ | +50 $ | 0/0 |
| H16 prédictive 10 s | 47 | 10 | 10 | 100,0 % | 0,78 | 100,0 % | +171 $ | **−102 $** [−345 $ ; +100 $] | −52 $ | −1 $ | −275 $ | −50 $ | 6 | 6/8 | +178 $ | −0 $ | +172 $ | +50 $ | 0/0 |
| H17 premier passage (limite si EV > immédiat) | 47 | 10 | 10 | 100,0 % | 0,78 | 100,0 % | +171 $ | **−102 $** [−361 $ ; +129 $] | −52 $ | −1 $ | −275 $ | −50 $ | 6 | 6/8 | +178 $ | −0 $ | +172 $ | +50 $ | 0/0 |
| H18 fenêtre de conversion prédite (paire ≤ 0,95) — inactive si seuil appris = jamais | 47 | 0 | 0 | — | — | — | +273 $ | **+0 $** [+0 $ ; +0 $] | +0 $ | +0 $ | −318 $ | −50 $ | 6 | 8/8 | +0 $ | +0 $ | +273 $ | +50 $ | 0/0 |
| H19 sauvetage passif (vendeur − 1 c, 10 s) | 47 | 10 | 5 | 50,0 % | 0,84 | 100,0 % | +115 $ | **−158 $** [−383 $ ; +18 $] | −108 $ | −57 $ | −335 $ | −50 $ | 6 | 6/8 | +173 $ | −13 $ | +128 $ | +50 $ | 0/0 |
| H20 prédicteur de file (traversée) passif sinon immédiat | 47 | 10 | 10 | 100,0 % | 0,78 | 100,0 % | +171 $ | **−102 $** [−352 $ ; +100 $] | −52 $ | −1 $ | −275 $ | −50 $ | 6 | 6/8 | +178 $ | −0 $ | +172 $ | +50 $ | 0/0 |
| H21 recharge du carnet | 47 | 10 | 9 | 90,0 % | 0,71 | 100,0 % | +194 $ | **−79 $** [−300 $ ; +88 $] | −29 $ | +22 $ | −259 $ | −50 $ | 6 | 7/8 | +135 $ | +72 $ | +122 $ | +50 $ | 0/0 |
| H22 hybride 50 % immédiat + 50 % passif | 47 | 10 | 10 | 100,0 % | 0,77 | 90,0 % | +149 $ | **−124 $** [−361 $ ; +70 $] | −74 $ | −24 $ | −288 $ | −50 $ | 6 | 6/8 | +176 $ | +16 $ | +172 $ | +50 $ | 0/0 |
| H23 boomerang (revente de l'opposé +5 c) | 47 | 33 | 33 | 100,0 % | 0,71 | 100,0 % | +303 $ | **+29 $** [−180 $ ; +243 $] | +182 $ | +335 $ | −243 $ | −50 $ | 6 | 5/8 | +38 $ | +140 $ | −406 $ | +50 $ | 0/0 |
| H24 moteur d'inventaire deux jambes | 47 | 46 | 46 | 100,0 % | 0,65 | 26,2 % | +184 $ | **−89 $** [−258 $ ; +106 $] | +51 $ | +191 $ | −328 $ | −63 $ | 6 | 3/8 | +133 $ | +207 $ | −50 $ | +65 $ | 0/0 |

### A · désaccord 30 zone + modèle monte — prudent — validation

| Couverture | Positions | Tentées | Exécutées | Taux d'exécution | Prix moyen opposé | Quantité couverte moy. | P&L net | Δ vs GARDER [IC 90 %] | Δ vs VENDRE 50 % | Δ vs VENDRE 100 % | Creux max | Perte max (1 position) | Plus longue série perdante | Jackpots gardés | Profit sacrifié (jackpots) | Profit verrouillé (paires) | P&L des positions non couvertes | Capital immobilisé max | Entrées réduites / refusées |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| GARDER (référence) | 21 | — | — | — | — | — | −250 $ | 0 | — | — | −312 $ | −50 $ | 9 | 1/1 | 0 $ | 0 $ | −250 $ | +50 $ | 31/21 |
| H01 verrouillage paire complète (coût < 1) | 37 | 20 | 20 | 100,0 % | 0,62 | 79,2 % | −142 $ | **+108 $** [−396 $ ; +644 $] | +108 $ | +108 $ | −207 $ | −50 $ | 5 | 0/1 | +2 $ | +317 $ | −602 $ | +203 $ | 0/0 |
| H02 verrouillage partiel 25 % | 34 | 20 | 19 | 95,0 % | 0,66 | 23,3 % | −250 $ | **−0 $** [−279 $ ; +284 $] | −0 $ | −0 $ | −295 $ | −50 $ | 9 | 1/1 | +1 $ | +71 $ | −341 $ | +95 $ | 20/4 |
| H03 verrouillage partiel 50 % | 37 | 20 | 19 | 95,0 % | 0,64 | 44,6 % | −250 $ | **+0 $** [−397 $ ; +433 $] | +0 $ | −0 $ | −273 $ | −50 $ | 9 | 0/1 | +1 $ | +155 $ | −386 $ | +142 $ | 13/0 |
| H04 plancher de profit (les 2 issues ≥ 0) | 25 | 16 | 15 | 93,8 % | 0,69 | 52,0 % | −250 $ | **+0 $** [−267 $ ; +246 $] | +0 $ | +0 $ | −267 $ | −50 $ | 5 | 1/1 | +1 $ | +78 $ | −225 $ | +202 $ | 27/15 |
| H05 réserve jackpot (≥ 70 % gardé) | 33 | 20 | 19 | 95,0 % | 0,64 | 35,1 % | −250 $ | **−0 $** [−250 $ ; +309 $] | −0 $ | −0 $ | −281 $ | −50 $ | 9 | 0/1 | +1 $ | +98 $ | −304 $ | +105 $ | 21/6 |
| H06 échelle de paires (4 tranches) | 37 | 20 | 20 | 100,0 % | 0,59 | 72,2 % | −142 $ | **+108 $** [−400 $ ; +717 $] | +108 $ | +108 $ | −207 $ | −50 $ | 5 | 0/1 | +2 $ | +320 $ | −602 $ | +202 $ | 0/0 |
| H07 pire perte limitée à −25 $ | 11 | 5 | 5 | 100,0 % | 0,90 | 45,1 % | −250 $ | **+0 $** [−393 $ ; +374 $] | −0 $ | −1 $ | −250 $ | −50 $ | 5 | 1/1 | +0 $ | −62 $ | −74 $ | +231 $ | 45/42 |
| H08 pire perte limitée à −10 $ | 17 | 14 | 12 | 85,7 % | 0,89 | 61,2 % | −250 $ | **+0 $** [−258 $ ; +185 $] | +0 $ | +0 $ | −250 $ | −50 $ | 5 | 1/1 | +0 $ | −136 $ | +104 $ | +235 $ | 36/31 |
| H09 pire issue à 0 dans le budget (après modèle −10) | 17 | 8 | 2 | 25,0 % | 0,62 | 52,7 % | −250 $ | **−0 $** [−100 $ ; +86 $] | −1 $ | −0 $ | −290 $ | −50 $ | 5 | 1/1 | +0 $ | +26 $ | −304 $ | +137 $ | 35/31 |
| H10 couvrir ou vendre (avantage net) | 14 | 5 | 4 | 80,0 % | — | 100,0 % | −250 $ | **+0 $** [−311 $ ; +284 $] | −1 $ | +0 $ | −250 $ | −50 $ | 5 | 1/1 | +0 $ | +0 $ | −135 $ | +50 $ | 40/38 |
| H11 alerte précoce (2 signaux sur 3) 25 % | 18 | 14 | 12 | 85,7 % | 0,91 | 22,8 % | −250 $ | **+0 $** [−92 $ ; +69 $] | −1 $ | −1 $ | −307 $ | −50 $ | 6 | 1/1 | +0 $ | −66 $ | +17 $ | +124 $ | 31/30 |
| H12 horloge de risque (immédiat / attendre 3 s) | 10 | 2 | 2 | 100,0 % | 0,83 | 45,6 % | −249 $ | **+1 $** [−430 $ ; +391 $] | −0 $ | +1 $ | −249 $ | −50 $ | 5 | 1/1 | +0 $ | −20 $ | −195 $ | +181 $ | 46/44 |
| H13 prédictive 1 s | 10 | 2 | 2 | 100,0 % | 0,76 | 49,5 % | −249 $ | **+1 $** [−416 $ ; +380 $] | −0 $ | +1 $ | −249 $ | −50 $ | 5 | 1/1 | +0 $ | −10 $ | −195 $ | +181 $ | 46/44 |
| H14 prédictive 3 s | 10 | 2 | 2 | 100,0 % | 0,83 | 45,6 % | −249 $ | **+1 $** [−433 $ ; +387 $] | +0 $ | +1 $ | −249 $ | −50 $ | 5 | 1/1 | +0 $ | −20 $ | −195 $ | +181 $ | 46/44 |
| H15 prédictive 5 s | 10 | 2 | 2 | 100,0 % | 0,76 | 49,5 % | −250 $ | **+0 $** [−418 $ ; +387 $] | −0 $ | +0 $ | −250 $ | −50 $ | 5 | 1/1 | +0 $ | −10 $ | −195 $ | +181 $ | 46/44 |
| H16 prédictive 10 s | 10 | 2 | 2 | 100,0 % | 0,76 | 49,5 % | −249 $ | **+1 $** [−426 $ ; +386 $] | −0 $ | +1 $ | −249 $ | −50 $ | 5 | 1/1 | +0 $ | −10 $ | −195 $ | +181 $ | 46/44 |
| H17 premier passage (limite si EV > immédiat) | 10 | 2 | 2 | 100,0 % | 0,76 | 49,5 % | −249 $ | **+1 $** [−418 $ ; +396 $] | −0 $ | +1 $ | −249 $ | −50 $ | 5 | 1/1 | +0 $ | −10 $ | −195 $ | +181 $ | 46/44 |
| H18 fenêtre de conversion prédite (paire ≤ 0,95) — inactive si seuil appris = jamais | 21 | 0 | 0 | — | — | — | −250 $ | **−0 $** [+0 $ ; +0 $] | −0 $ | −0 $ | −312 $ | −50 $ | 9 | 1/1 | +0 $ | +0 $ | −250 $ | +50 $ | 31/21 |
| H19 sauvetage passif (vendeur − 1 c, 10 s) | 10 | 2 | 1 | 50,0 % | 0,83 | 89,8 % | −250 $ | **+0 $** [−414 $ ; +382 $] | −1 $ | −0 $ | −250 $ | −50 $ | 5 | 1/1 | +0 $ | −18 $ | −245 $ | +181 $ | 46/44 |
| H20 prédicteur de file (traversée) passif sinon immédiat | 10 | 2 | 2 | 100,0 % | 0,76 | 49,5 % | −250 $ | **+0 $** [−420 $ ; +398 $] | −0 $ | +0 $ | −250 $ | −50 $ | 5 | 1/1 | +0 $ | −10 $ | −195 $ | +181 $ | 46/44 |
| H21 recharge du carnet | 10 | 2 | 2 | 100,0 % | 0,76 | 49,5 % | −249 $ | **+1 $** [−419 $ ; +390 $] | −0 $ | +1 $ | −249 $ | −50 $ | 5 | 1/1 | +0 $ | −10 $ | −195 $ | +181 $ | 46/44 |
| H22 hybride 50 % immédiat + 50 % passif | 10 | 2 | 2 | 100,0 % | 0,80 | 47,9 % | −249 $ | **+1 $** [−413 $ ; +386 $] | −0 $ | +1 $ | −249 $ | −50 $ | 5 | 1/1 | +0 $ | −14 $ | −195 $ | +181 $ | 46/44 |
| H23 boomerang (revente de l'opposé +5 c) | 17 | 12 | 11 | 91,7 % | 0,62 | 63,3 % | −250 $ | **+0 $** [−163 $ ; +133 $] | +0 $ | −0 $ | −250 $ | −50 $ | 5 | 0/1 | +2 $ | +52 $ | −232 $ | +183 $ | 35/31 |
| H24 moteur d'inventaire deux jambes | 37 | 37 | 37 | 100,0 % | 0,61 | 18,4 % | −181 $ | **+69 $** [−448 $ ; +670 $] | +69 $ | +68 $ | −353 $ | −65 $ | 9 | 0/1 | +1 $ | +141 $ | +0 $ | +100 $ | 0/0 |

### A · désaccord 30 zone + modèle monte — prudent — inédit

| Couverture | Positions | Tentées | Exécutées | Taux d'exécution | Prix moyen opposé | Quantité couverte moy. | P&L net | Δ vs GARDER [IC 90 %] | Δ vs VENDRE 50 % | Δ vs VENDRE 100 % | Creux max | Perte max (1 position) | Plus longue série perdante | Jackpots gardés | Profit sacrifié (jackpots) | Profit verrouillé (paires) | P&L des positions non couvertes | Capital immobilisé max | Entrées réduites / refusées |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| GARDER (référence) | 30 | — | — | — | — | — | −250 $ | 0 | — | — | −362 $ | −50 $ | 9 | 5/5 | 0 $ | 0 $ | −250 $ | +50 $ | 9/6 |
| H01 verrouillage paire complète (coût < 1) | 25 | 17 | 13 | 76,5 % | 0,70 | 72,4 % | −250 $ | **+0 $** [−363 $ ; +323 $] | +0 $ | −0 $ | −287 $ | −50 $ | 5 | 1/5 | +172 $ | +84 $ | −225 $ | +248 $ | 20/15 |
| H02 verrouillage partiel 25 % | 29 | 20 | 16 | 80,0 % | 0,74 | 21,7 % | −250 $ | **+0 $** [−112 $ ; +99 $] | +0 $ | −0 $ | −327 $ | −50 $ | 8 | 3/5 | +74 $ | +31 $ | −490 $ | +109 $ | 9/7 |
| H03 verrouillage partiel 50 % | 30 | 20 | 17 | 85,0 % | 0,72 | 38,2 % | −250 $ | **−0 $** [−179 $ ; +142 $] | −0 $ | −0 $ | −327 $ | −50 $ | 9 | 2/5 | +100 $ | +61 $ | −484 $ | +151 $ | 9/6 |
| H04 plancher de profit (les 2 issues ≥ 0) | 18 | 11 | 8 | 72,7 % | 0,72 | 47,5 % | −250 $ | **−0 $** [−412 $ ; +399 $] | −0 $ | −0 $ | −272 $ | −50 $ | 5 | 2/5 | +144 $ | +39 $ | −166 $ | +231 $ | 29/27 |
| H05 réserve jackpot (≥ 70 % gardé) | 29 | 20 | 16 | 80,0 % | 0,73 | 27,6 % | −250 $ | **+0 $** [−126 $ ; +111 $] | +0 $ | −0 $ | −327 $ | −50 $ | 8 | 2/5 | +83 $ | +40 $ | −492 $ | +119 $ | 9/7 |
| H06 échelle de paires (4 tranches) | 31 | 21 | 17 | 81,0 % | 0,66 | 73,4 % | −250 $ | **−0 $** [−309 $ ; +293 $] | −0 $ | −0 $ | −325 $ | −50 $ | 5 | 1/5 | +116 $ | +209 $ | −567 $ | +248 $ | 6/5 |
| H07 pire perte limitée à −25 $ | 18 | 11 | 10 | 90,9 % | 0,92 | 43,5 % | −250 $ | **+0 $** [−363 $ ; +351 $] | +0 $ | +0 $ | −250 $ | −50 $ | 5 | 3/5 | +140 $ | −119 $ | +58 $ | +237 $ | 29/27 |
| H08 pire perte limitée à −10 $ | 34 | 26 | 25 | 96,2 % | 0,88 | 83,2 % | −92 $ | **+158 $** [−170 $ ; +464 $] | +157 $ | +154 $ | −245 $ | −50 $ | 13 | 5/5 | +18 $ | −297 $ | +371 $ | +332 $ | 1/0 |
| H09 pire issue à 0 dans le budget (après modèle −10) | 30 | 4 | 1 | 25,0 % | 0,31 | 35,9 % | −250 $ | **−0 $** [−10 $ ; +10 $] | −0 $ | −0 $ | −362 $ | −50 $ | 9 | 5/5 | +5 $ | +8 $ | −281 $ | +50 $ | 9/6 |
| H10 couvrir ou vendre (avantage net) | 29 | 4 | 4 | 100,0 % | — | 100,0 % | −250 $ | **+0 $** [−89 $ ; +75 $] | −0 $ | +0 $ | −365 $ | −50 $ | 8 | 4/5 | +41 $ | +0 $ | −152 $ | +50 $ | 9/7 |
| H11 alerte précoce (2 signaux sur 3) 25 % | 30 | 11 | 11 | 100,0 % | 0,91 | 24,6 % | −250 $ | **+0 $** [−49 $ ; +47 $] | −0 $ | −0 $ | −371 $ | −50 $ | 9 | 4/5 | +17 $ | −44 $ | −9 $ | +123 $ | 7/6 |
| H12 horloge de risque (immédiat / attendre 3 s) | 28 | 4 | 4 | 100,0 % | 0,98 | 80,6 % | −249 $ | **+1 $** [−83 $ ; +72 $] | +1 $ | +1 $ | −363 $ | −50 $ | 7 | 4/5 | +41 $ | −64 $ | −149 $ | +214 $ | 9/9 |
| H13 prédictive 1 s | 28 | 4 | 4 | 100,0 % | 0,98 | 80,6 % | −249 $ | **+1 $** [−81 $ ; +74 $] | +1 $ | +1 $ | −363 $ | −50 $ | 7 | 4/5 | +41 $ | −64 $ | −149 $ | +214 $ | 9/9 |
| H14 prédictive 3 s | 28 | 4 | 4 | 100,0 % | 0,98 | 80,4 % | −250 $ | **+0 $** [−81 $ ; +75 $] | −0 $ | +0 $ | −363 $ | −50 $ | 7 | 4/5 | +41 $ | −66 $ | −147 $ | +214 $ | 12/9 |
| H15 prédictive 5 s | 28 | 4 | 4 | 100,0 % | 0,98 | 80,6 % | −249 $ | **+1 $** [−86 $ ; +71 $] | +1 $ | +1 $ | −363 $ | −50 $ | 7 | 4/5 | +41 $ | −64 $ | −149 $ | +214 $ | 9/9 |
| H16 prédictive 10 s | 28 | 4 | 4 | 100,0 % | 0,98 | 80,6 % | −249 $ | **+1 $** [−81 $ ; +70 $] | +1 $ | +1 $ | −363 $ | −50 $ | 7 | 4/5 | +41 $ | −64 $ | −149 $ | +214 $ | 9/9 |
| H17 premier passage (limite si EV > immédiat) | 28 | 4 | 4 | 100,0 % | 0,98 | 80,6 % | −249 $ | **+1 $** [−82 $ ; +72 $] | +1 $ | +1 $ | −363 $ | −50 $ | 7 | 4/5 | +41 $ | −64 $ | −149 $ | +214 $ | 9/9 |
| H18 fenêtre de conversion prédite (paire ≤ 0,95) — inactive si seuil appris = jamais | 30 | 0 | 0 | — | — | — | −250 $ | **+0 $** [+0 $ ; +0 $] | +0 $ | +0 $ | −362 $ | −50 $ | 9 | 5/5 | +0 $ | +0 $ | −250 $ | +50 $ | 9/6 |
| H19 sauvetage passif (vendeur − 1 c, 10 s) | 29 | 4 | 2 | 50,0 % | 0,96 | 88,8 % | −250 $ | **+0 $** [−88 $ ; +71 $] | −0 $ | −0 $ | −362 $ | −50 $ | 8 | 4/5 | +40 $ | −30 $ | −211 $ | +214 $ | 9/7 |
| H20 prédicteur de file (traversée) passif sinon immédiat | 28 | 4 | 4 | 100,0 % | 0,98 | 80,6 % | −249 $ | **+1 $** [−83 $ ; +74 $] | +1 $ | +1 $ | −363 $ | −50 $ | 7 | 4/5 | +41 $ | −64 $ | −149 $ | +214 $ | 9/9 |
| H21 recharge du carnet | 28 | 4 | 2 | 50,0 % | 0,96 | 88,4 % | −250 $ | **+0 $** [−83 $ ; +71 $] | +0 $ | +0 $ | −362 $ | −50 $ | 7 | 4/5 | +41 $ | −31 $ | −209 $ | +213 $ | 9/9 |
| H22 hybride 50 % immédiat + 50 % passif | 29 | 4 | 4 | 100,0 % | 0,97 | 68,3 % | −250 $ | **+0 $** [−83 $ ; +70 $] | −0 $ | +0 $ | −363 $ | −50 $ | 8 | 4/5 | +41 $ | −58 $ | −150 $ | +215 $ | 9/7 |
| H23 boomerang (revente de l'opposé +5 c) | 31 | 21 | 17 | 81,0 % | 0,72 | 81,1 % | −250 $ | **−0 $** [−155 $ ; +154 $] | −0 $ | −0 $ | −393 $ | −50 $ | 9 | 2/5 | +51 $ | +26 $ | −554 $ | +252 $ | 6/5 |
| H24 moteur d'inventaire deux jambes | 29 | 28 | 27 | 96,4 % | 0,67 | 18,0 % | −250 $ | **+0 $** [−109 $ ; +103 $] | −1 $ | −1 $ | −405 $ | −65 $ | 8 | 3/5 | −16 $ | +79 $ | −54 $ | +100 $ | 9/7 |

### A · désaccord 30 zone + modèle monte — pessimiste — validation

| Couverture | Positions | Tentées | Exécutées | Taux d'exécution | Prix moyen opposé | Quantité couverte moy. | P&L net | Δ vs GARDER [IC 90 %] | Δ vs VENDRE 50 % | Δ vs VENDRE 100 % | Creux max | Perte max (1 position) | Plus longue série perdante | Jackpots gardés | Profit sacrifié (jackpots) | Profit verrouillé (paires) | P&L des positions non couvertes | Capital immobilisé max | Entrées réduites / refusées |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| GARDER (référence) | 31 | — | — | — | — | — | −182 $ | 0 | — | — | −253 $ | −50 $ | 9 | 3/3 | 0 $ | 0 $ | −182 $ | +50 $ | 0/0 |
| H01 verrouillage paire complète (coût < 1) | 31 | 17 | 16 | 94,1 % | 0,63 | 82,2 % | −107 $ | **+75 $** [−285 $ ; +451 $] | +143 $ | +143 $ | −215 $ | −50 $ | 5 | 1/3 | +82 $ | +297 $ | −567 $ | +218 $ | 0/0 |
| H02 verrouillage partiel 25 % | 31 | 17 | 16 | 94,1 % | 0,65 | 22,9 % | −169 $ | **+13 $** [−89 $ ; +118 $] | +81 $ | +81 $ | −233 $ | −50 $ | 9 | 3/3 | +46 $ | +79 $ | −567 $ | +99 $ | 0/0 |
| H03 verrouillage partiel 50 % | 31 | 17 | 16 | 94,1 % | 0,64 | 44,0 % | −140 $ | **+42 $** [−151 $ ; +257 $] | +110 $ | +110 $ | −204 $ | −50 $ | 8 | 2/3 | +65 $ | +160 $ | −567 $ | +142 $ | 0/0 |
| H04 plancher de profit (les 2 issues ≥ 0) | 31 | 17 | 16 | 94,1 % | 0,69 | 59,8 % | −148 $ | **+34 $** [−220 $ ; +254 $] | +102 $ | +102 $ | −212 $ | −50 $ | 5 | 3/3 | +48 $ | +132 $ | −567 $ | +209 $ | 0/0 |
| H05 réserve jackpot (≥ 70 % gardé) | 31 | 17 | 16 | 94,1 % | 0,62 | 32,3 % | −176 $ | **+6 $** [−115 $ ; +147 $] | +74 $ | +74 $ | −240 $ | −50 $ | 8 | 2/3 | +61 $ | +125 $ | −567 $ | +109 $ | 0/0 |
| H06 échelle de paires (4 tranches) | 31 | 17 | 15 | 88,2 % | 0,57 | 59,9 % | −210 $ | **−28 $** [−335 $ ; +271 $] | +40 $ | +40 $ | −215 $ | −50 $ | 7 | 1/3 | +112 $ | +244 $ | −366 $ | +165 $ | 11/0 |
| H07 pire perte limitée à −25 $ | 19 | 8 | 8 | 100,0 % | 0,92 | 57,1 % | −250 $ | **−68 $** [−634 $ ; +387 $] | −0 $ | −0 $ | −313 $ | −50 $ | 9 | 1/3 | +256 $ | −139 $ | −35 $ | +237 $ | 31/16 |
| H08 pire perte limitée à −10 $ | 31 | 24 | 23 | 95,8 % | 0,90 | 57,8 % | −223 $ | **−41 $** [−343 $ ; +193 $] | +26 $ | +27 $ | −223 $ | −50 $ | 9 | 3/3 | +111 $ | −217 $ | +244 $ | +238 $ | 11/0 |
| H09 pire issue à 0 dans le budget (après modèle −10) | 31 | 16 | 2 | 12,5 % | 0,62 | 51,1 % | −192 $ | **−10 $** [−77 $ ; +52 $] | +58 $ | +57 $ | −253 $ | −50 $ | 9 | 3/3 | +3 $ | +24 $ | −240 $ | +140 $ | 1/0 |
| H10 couvrir ou vendre (avantage net) | 13 | 6 | 4 | 66,7 % | — | 100,0 % | −249 $ | **−67 $** [−699 $ ; +445 $] | +1 $ | +0 $ | −249 $ | −50 $ | 7 | 0/3 | +0 $ | +0 $ | −169 $ | +50 $ | 39/35 |
| H11 alerte précoce (2 signaux sur 3) 25 % | 31 | 23 | 19 | 82,6 % | 0,93 | 24,4 % | −250 $ | **−68 $** [−215 $ ; +52 $] | −1 $ | −0 $ | −300 $ | −50 $ | 9 | 2/3 | +79 $ | −110 $ | +177 $ | +121 $ | 4/0 |
| H12 horloge de risque (immédiat / attendre 3 s) | 9 | 2 | 2 | 100,0 % | 0,82 | 50,3 % | −250 $ | **−68 $** [−748 $ ; +517 $] | +0 $ | −1 $ | −250 $ | −50 $ | 7 | 0/3 | +0 $ | −17 $ | −183 $ | +164 $ | 46/44 |
| H13 prédictive 1 s | 7 | 2 | 1 | 50,0 % | 0,83 | 100,0 % | −250 $ | **−68 $** [−761 $ ; +524 $] | +0 $ | −0 $ | −250 $ | −50 $ | 7 | 0/3 | +0 $ | −18 $ | −232 $ | +165 $ | 46/46 |
| H14 prédictive 3 s | 9 | 2 | 2 | 100,0 % | 0,82 | 50,3 % | −250 $ | **−68 $** [−740 $ ; +514 $] | +0 $ | −1 $ | −250 $ | −50 $ | 7 | 0/3 | +0 $ | −17 $ | −183 $ | +164 $ | 46/44 |
| H15 prédictive 5 s | 7 | 2 | 1 | 50,0 % | 0,83 | 100,0 % | −250 $ | **−68 $** [−737 $ ; +508 $] | +0 $ | −0 $ | −250 $ | −50 $ | 7 | 0/3 | +0 $ | −18 $ | −232 $ | +165 $ | 46/46 |
| H16 prédictive 10 s | 7 | 2 | 1 | 50,0 % | 0,83 | 100,0 % | −250 $ | **−68 $** [−751 $ ; +552 $] | +0 $ | −0 $ | −250 $ | −50 $ | 7 | 0/3 | +0 $ | −18 $ | −232 $ | +165 $ | 46/46 |
| H17 premier passage (limite si EV > immédiat) | 7 | 2 | 1 | 50,0 % | 0,83 | 100,0 % | −250 $ | **−68 $** [−752 $ ; +528 $] | +0 $ | −0 $ | −250 $ | −50 $ | 7 | 0/3 | +0 $ | −18 $ | −232 $ | +165 $ | 46/46 |
| H18 fenêtre de conversion prédite (paire ≤ 0,95) — inactive si seuil appris = jamais | 31 | 0 | 0 | — | — | — | −182 $ | **+0 $** [+0 $ ; +0 $] | +0 $ | +0 $ | −253 $ | −50 $ | 9 | 3/3 | +0 $ | +0 $ | −182 $ | +50 $ | 0/0 |
| H19 sauvetage passif (vendeur − 1 c, 10 s) | 9 | 2 | 1 | 50,0 % | 0,83 | 100,0 % | −250 $ | **−68 $** [−776 $ ; +532 $] | +0 $ | −1 $ | −250 $ | −50 $ | 7 | 0/3 | +0 $ | −17 $ | −233 $ | +164 $ | 46/44 |
| H20 prédicteur de file (traversée) passif sinon immédiat | 7 | 2 | 1 | 50,0 % | 0,83 | 100,0 % | −250 $ | **−68 $** [−758 $ ; +503 $] | +0 $ | −0 $ | −250 $ | −50 $ | 7 | 0/3 | +0 $ | −18 $ | −232 $ | +165 $ | 46/46 |
| H21 recharge du carnet | 7 | 2 | 1 | 50,0 % | 0,83 | 100,0 % | −250 $ | **−68 $** [−735 $ ; +514 $] | +0 $ | −0 $ | −250 $ | −50 $ | 7 | 0/3 | +0 $ | −18 $ | −232 $ | +165 $ | 46/46 |
| H22 hybride 50 % immédiat + 50 % passif | 10 | 3 | 2 | 66,7 % | 0,82 | 50,7 % | −250 $ | **−68 $** [−745 $ ; +518 $] | +0 $ | −1 $ | −250 $ | −50 $ | 7 | 0/3 | +0 $ | −16 $ | −185 $ | +162 $ | 46/42 |
| H23 boomerang (revente de l'opposé +5 c) | 31 | 17 | 16 | 94,1 % | 0,61 | 75,6 % | −228 $ | **−46 $** [−208 $ ; +90 $] | +22 $ | +22 $ | −297 $ | −50 $ | 9 | 1/3 | +70 $ | +136 $ | −567 $ | +208 $ | 0/0 |
| H24 moteur d'inventaire deux jambes | 31 | 31 | 31 | 100,0 % | 0,59 | 14,5 % | −120 $ | **+62 $** [−89 $ ; +228 $] | +127 $ | +129 $ | −317 $ | −65 $ | 9 | 3/3 | −14 $ | +132 $ | +0 $ | +100 $ | 0/0 |

### A · désaccord 30 zone + modèle monte — pessimiste — inédit

| Couverture | Positions | Tentées | Exécutées | Taux d'exécution | Prix moyen opposé | Quantité couverte moy. | P&L net | Δ vs GARDER [IC 90 %] | Δ vs VENDRE 50 % | Δ vs VENDRE 100 % | Creux max | Perte max (1 position) | Plus longue série perdante | Jackpots gardés | Profit sacrifié (jackpots) | Profit verrouillé (paires) | P&L des positions non couvertes | Capital immobilisé max | Entrées réduites / refusées |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| GARDER (référence) | 9 | — | — | — | — | — | −250 $ | 0 | — | — | −250 $ | −50 $ | 5 | 0/0 | 0 $ | 0 $ | −250 $ | +50 $ | 38/37 |
| H01 verrouillage paire complète (coût < 1) | 9 | 5 | 3 | 60,0 % | 0,71 | 100,0 % | −250 $ | **+0 $** [−208 $ ; +194 $] | +0 $ | +0 $ | −283 $ | −50 $ | 5 | 0/0 | +0 $ | +35 $ | −285 $ | +248 $ | 38/37 |
| H02 verrouillage partiel 25 % | 9 | 5 | 3 | 60,0 % | 0,71 | 25,0 % | −250 $ | **−0 $** [−55 $ ; +50 $] | −0 $ | −0 $ | −250 $ | −50 $ | 5 | 0/0 | +0 $ | +9 $ | −296 $ | +100 $ | 38/37 |
| H03 verrouillage partiel 50 % | 9 | 5 | 3 | 60,0 % | 0,71 | 50,0 % | −250 $ | **+0 $** [−109 $ ; +98 $] | −0 $ | −0 $ | −250 $ | −50 $ | 5 | 0/0 | +0 $ | +18 $ | −292 $ | +149 $ | 38/37 |
| H04 plancher de profit (les 2 issues ≥ 0) | 9 | 5 | 3 | 60,0 % | 0,71 | 72,9 % | −250 $ | **+0 $** [−197 $ ; +183 $] | −0 $ | −0 $ | −250 $ | −50 $ | 5 | 0/0 | +0 $ | +23 $ | −257 $ | +176 $ | 38/37 |
| H05 réserve jackpot (≥ 70 % gardé) | 9 | 5 | 3 | 60,0 % | 0,71 | 32,1 % | −250 $ | **+0 $** [−63 $ ; +59 $] | −0 $ | −0 $ | −250 $ | −50 $ | 5 | 0/0 | +0 $ | +11 $ | −296 $ | +111 $ | 38/37 |
| H06 échelle de paires (4 tranches) | 9 | 5 | 3 | 60,0 % | 0,68 | 100,0 % | −250 $ | **+0 $** [−193 $ ; +182 $] | −0 $ | −0 $ | −283 $ | −50 $ | 5 | 0/0 | +0 $ | +46 $ | −296 $ | +248 $ | 38/37 |
| H07 pire perte limitée à −25 $ | 7 | 5 | 4 | 80,0 % | 0,93 | 54,3 % | −250 $ | **+0 $** [−248 $ ; +248 $] | −0 $ | +0 $ | −250 $ | −50 $ | 7 | 0/0 | +0 $ | −60 $ | −106 $ | +244 $ | 40/39 |
| H08 pire perte limitée à −10 $ | 9 | 8 | 7 | 87,5 % | 0,87 | 53,0 % | −250 $ | **+0 $** [−241 $ ; +241 $] | −1 $ | −15 $ | −250 $ | −48 $ | 9 | 0/0 | +0 $ | −60 $ | −26 $ | +244 $ | 38/37 |
| H09 pire issue à 0 dans le budget (après modèle −10) | 9 | 1 | 0 | 0,0 % | — | — | −250 $ | **+0 $** [+0 $ ; +0 $] | −1 $ | +0 $ | −250 $ | −50 $ | 5 | 0/0 | +0 $ | +0 $ | −250 $ | +50 $ | 38/37 |
| H10 couvrir ou vendre (avantage net) | 12 | 1 | 1 | 100,0 % | — | 100,0 % | −250 $ | **−0 $** [−4 $ ; +4 $] | −1 $ | +0 $ | −250 $ | −50 $ | 5 | 0/0 | +0 $ | +0 $ | −203 $ | +50 $ | 37/34 |
| H11 alerte précoce (2 signaux sur 3) 25 % | 12 | 2 | 2 | 100,0 % | 0,92 | 21,1 % | −250 $ | **−0 $** [−9 $ ; +9 $] | −0 $ | −0 $ | −254 $ | −50 $ | 5 | 0/0 | +0 $ | −5 $ | −199 $ | +104 $ | 37/34 |
| H12 horloge de risque (immédiat / attendre 3 s) | 9 | 1 | 1 | 100,0 % | 0,99 | 15,8 % | −250 $ | **+0 $** [+0 $ ; +0 $] | −1 $ | +0 $ | −250 $ | −50 $ | 5 | 0/0 | +0 $ | −7 $ | −200 $ | +99 $ | 38/37 |
| H13 prédictive 1 s | 9 | 1 | 1 | 100,0 % | 0,99 | 15,8 % | −250 $ | **+0 $** [+0 $ ; +0 $] | −1 $ | +0 $ | −250 $ | −50 $ | 5 | 0/0 | +0 $ | −7 $ | −200 $ | +99 $ | 38/37 |
| H14 prédictive 3 s | 9 | 1 | 1 | 100,0 % | 0,99 | 15,8 % | −250 $ | **+0 $** [+0 $ ; +0 $] | −1 $ | +0 $ | −250 $ | −50 $ | 5 | 0/0 | +0 $ | −7 $ | −200 $ | +99 $ | 38/37 |
| H15 prédictive 5 s | 9 | 1 | 1 | 100,0 % | 0,99 | 15,8 % | −250 $ | **+0 $** [+0 $ ; +0 $] | −1 $ | +0 $ | −250 $ | −50 $ | 5 | 0/0 | +0 $ | −7 $ | −200 $ | +99 $ | 38/37 |
| H16 prédictive 10 s | 9 | 1 | 1 | 100,0 % | 0,99 | 15,8 % | −250 $ | **+0 $** [+0 $ ; +0 $] | −1 $ | +0 $ | −250 $ | −50 $ | 5 | 0/0 | +0 $ | −7 $ | −200 $ | +99 $ | 38/37 |
| H17 premier passage (limite si EV > immédiat) | 9 | 1 | 1 | 100,0 % | 0,99 | 15,8 % | −250 $ | **+0 $** [+0 $ ; +0 $] | −1 $ | +0 $ | −250 $ | −50 $ | 5 | 0/0 | +0 $ | −7 $ | −200 $ | +99 $ | 38/37 |
| H18 fenêtre de conversion prédite (paire ≤ 0,95) — inactive si seuil appris = jamais | 9 | 0 | 0 | — | — | — | −250 $ | **+0 $** [+0 $ ; +0 $] | +0 $ | +0 $ | −250 $ | −50 $ | 5 | 0/0 | +0 $ | +0 $ | −250 $ | +50 $ | 38/37 |
| H19 sauvetage passif (vendeur − 1 c, 10 s) | 9 | 1 | 0 | 0,0 % | — | — | −250 $ | **+0 $** [+0 $ ; +0 $] | −1 $ | +0 $ | −250 $ | −50 $ | 5 | 0/0 | +0 $ | +0 $ | −250 $ | +50 $ | 38/37 |
| H20 prédicteur de file (traversée) passif sinon immédiat | 9 | 1 | 1 | 100,0 % | 0,99 | 15,8 % | −250 $ | **+0 $** [+0 $ ; +0 $] | −1 $ | +0 $ | −250 $ | −50 $ | 5 | 0/0 | +0 $ | −7 $ | −200 $ | +99 $ | 38/37 |
| H21 recharge du carnet | 9 | 1 | 0 | 0,0 % | — | — | −250 $ | **+0 $** [+0 $ ; +0 $] | −1 $ | +0 $ | −250 $ | −50 $ | 5 | 0/0 | +0 $ | +0 $ | −250 $ | +50 $ | 38/37 |
| H22 hybride 50 % immédiat + 50 % passif | 9 | 1 | 1 | 100,0 % | 0,99 | 15,8 % | −250 $ | **+0 $** [+0 $ ; +0 $] | −1 $ | +0 $ | −250 $ | −50 $ | 5 | 0/0 | +0 $ | −7 $ | −200 $ | +99 $ | 38/37 |
| H23 boomerang (revente de l'opposé +5 c) | 27 | 19 | 12 | 63,2 % | 0,73 | 78,9 % | −250 $ | **−0 $** [−299 $ ; +378 $] | −0 $ | −0 $ | −286 $ | −50 $ | 8 | 0/0 | +0 $ | +3 $ | −299 $ | +247 $ | 8/5 |
| H24 moteur d'inventaire deux jambes | 9 | 8 | 7 | 87,5 % | 0,70 | 17,1 % | −250 $ | **+0 $** [−42 $ ; +46 $] | −5 $ | −3 $ | −257 $ | −63 $ | 5 | 0/0 | +0 $ | +14 $ | −58 $ | +100 $ | 38/37 |

### B · V2-F corrigé 0,015 % — idéal — validation

| Couverture | Positions | Tentées | Exécutées | Taux d'exécution | Prix moyen opposé | Quantité couverte moy. | P&L net | Δ vs GARDER [IC 90 %] | Δ vs VENDRE 50 % | Δ vs VENDRE 100 % | Creux max | Perte max (1 position) | Plus longue série perdante | Jackpots gardés | Profit sacrifié (jackpots) | Profit verrouillé (paires) | P&L des positions non couvertes | Capital immobilisé max | Entrées réduites / refusées |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| GARDER (référence) | 237 | — | — | — | — | — | +926 $ | 0 | — | — | −848 $ | −50 $ | 12 | 11/11 | 0 $ | 0 $ | +926 $ | +50 $ | 0/0 |
| H01 verrouillage paire complète (coût < 1) | 195 | 153 | 152 | 99,3 % | 0,67 | 99,8 % | −250 $ | **−1 176 $** [−2 850 $ ; +414 $] | −457 $ | +0 $ | −369 $ | −50 $ | 4 | 0/11 | +1 667 $ | +1 319 $ | −1 556 $ | +50 $ | 44/43 |
| H02 verrouillage partiel 25 % | 237 | 181 | 180 | 99,4 % | 0,68 | 25,0 % | +567 $ | **−359 $** [−757 $ ; +24 $] | +359 $ | +817 $ | −739 $ | −50 $ | 12 | 8/11 | +480 $ | +390 $ | −2 069 $ | +50 $ | 0/0 |
| H03 verrouillage partiel 50 % | 237 | 181 | 181 | 100,0 % | 0,67 | 50,0 % | +212 $ | **−713 $** [−1 576 $ ; +77 $] | +5 $ | +462 $ | −655 $ | −50 $ | 10 | 4/11 | +955 $ | +784 $ | −2 070 $ | +50 $ | 0/0 |
| H04 plancher de profit (les 2 issues ≥ 0) | 237 | 181 | 181 | 100,0 % | 0,68 | 79,7 % | −98 $ | **−1 024 $** [−2 265 $ ; +117 $] | −306 $ | +152 $ | −651 $ | −50 $ | 4 | 3/11 | +1 287 $ | +883 $ | −2 070 $ | +50 $ | 0/0 |
| H05 réserve jackpot (≥ 70 % gardé) | 237 | 181 | 180 | 99,4 % | 0,65 | 34,9 % | +412 $ | **−514 $** [−1 044 $ ; +15 $] | +205 $ | +662 $ | −729 $ | −50 $ | 12 | 8/11 | +627 $ | +731 $ | −2 069 $ | +50 $ | 0/0 |
| H06 échelle de paires (4 tranches) | 233 | 179 | 178 | 99,4 % | 0,63 | 90,7 % | −250 $ | **−1 176 $** [−2 829 $ ; +377 $] | −457 $ | +0 $ | −395 $ | −50 $ | 5 | 0/11 | +1 833 $ | +2 096 $ | −1 907 $ | +50 $ | 6/4 |
| H07 pire perte limitée à −25 $ | 237 | 104 | 104 | 100,0 % | 0,90 | 100,0 % | +18 $ | **−908 $** [−2 278 $ ; +254 $] | −455 $ | −2 $ | −699 $ | −50 $ | 14 | 9/11 | +683 $ | −3 138 $ | +3 156 $ | +50 $ | 0/0 |
| H08 pire perte limitée à −10 $ | 63 | 37 | 36 | 97,3 % | 0,85 | 99,7 % | −250 $ | **−1 176 $** [−2 980 $ ; +486 $] | −715 $ | −1 $ | −489 $ | −45 $ | 8 | 1/11 | +378 $ | −603 $ | +307 $ | +50 $ | 177/176 |
| H09 pire issue à 0 dans le budget (après modèle −10) | 237 | 167 | 74 | 44,3 % | 0,66 | 80,7 % | −20 $ | **−946 $** [−1 903 $ ; +8 $] | −612 $ | −279 $ | −1 161 $ | −50 $ | 8 | 6/11 | +966 $ | +467 $ | −927 $ | +50 $ | 0/0 |
| H10 couvrir ou vendre (avantage net) | 237 | 167 | 167 | 100,0 % | — | 100,0 % | +260 $ | **−666 $** [−1 996 $ ; +591 $] | −333 $ | +0 $ | −1 033 $ | −50 $ | 14 | 6/11 | +1 220 $ | +0 $ | +2 019 $ | +50 $ | 0/0 |
| H11 alerte précoce (2 signaux sur 3) 25 % | 237 | 191 | 190 | 99,5 % | 0,73 | 25,0 % | +757 $ | **−168 $** [−612 $ ; +240 $] | +169 $ | +506 $ | −715 $ | −50 $ | 12 | 10/11 | +370 $ | +53 $ | +42 $ | +50 $ | 0/0 |
| H12 horloge de risque (immédiat / attendre 3 s) | 237 | 167 | 163 | 97,6 % | 0,84 | 100,0 % | −15 $ | **−941 $** [−2 308 $ ; +437 $] | −608 $ | −275 $ | −1 192 $ | −50 $ | 14 | 6/11 | +1 229 $ | −1 937 $ | +1 922 $ | +50 $ | 0/0 |
| H13 prédictive 1 s | 237 | 167 | 167 | 100,0 % | 0,83 | 100,0 % | +277 $ | **−649 $** [−2 021 $ ; +661 $] | −316 $ | +17 $ | −1 033 $ | −50 $ | 14 | 6/11 | +1 220 $ | −1 742 $ | +2 019 $ | +50 $ | 0/0 |
| H14 prédictive 3 s | 237 | 167 | 167 | 100,0 % | 0,85 | 100,0 % | −116 $ | **−1 042 $** [−2 371 $ ; +248 $] | −709 $ | −376 $ | −1 160 $ | −50 $ | 14 | 6/11 | +1 222 $ | −2 135 $ | +2 019 $ | +50 $ | 0/0 |
| H15 prédictive 5 s | 237 | 167 | 167 | 100,0 % | 0,83 | 100,0 % | +195 $ | **−731 $** [−2 111 $ ; +536 $] | −398 $ | −65 $ | −993 $ | −50 $ | 14 | 6/11 | +1 220 $ | −1 824 $ | +2 019 $ | +50 $ | 0/0 |
| H16 prédictive 10 s | 237 | 167 | 167 | 100,0 % | 0,83 | 100,0 % | +271 $ | **−655 $** [−1 992 $ ; +659 $] | −322 $ | +11 $ | −989 $ | −50 $ | 14 | 6/11 | +1 220 $ | −1 748 $ | +2 019 $ | +50 $ | 0/0 |
| H17 premier passage (limite si EV > immédiat) | 237 | 167 | 167 | 100,0 % | 0,83 | 100,0 % | +278 $ | **−648 $** [−2 038 $ ; +630 $] | −315 $ | +18 $ | −1 021 $ | −50 $ | 14 | 6/11 | +1 220 $ | −1 741 $ | +2 019 $ | +50 $ | 0/0 |
| H18 fenêtre de conversion prédite (paire ≤ 0,95) — inactive si seuil appris = jamais | 237 | 0 | 0 | — | — | — | +926 $ | **−0 $** [+0 $ ; +0 $] | −0 $ | −0 $ | −848 $ | −50 $ | 12 | 11/11 | +0 $ | +0 $ | +926 $ | +50 $ | 0/0 |
| H19 sauvetage passif (vendeur − 1 c, 10 s) | 35 | 23 | 9 | 39,1 % | 0,80 | 90,0 % | −250 $ | **−1 176 $** [−2 953 $ ; +529 $] | −843 $ | −510 $ | −301 $ | −50 $ | 6 | 1/11 | +0 $ | −52 $ | −161 $ | +50 $ | 205/204 |
| H20 prédicteur de file (traversée) passif sinon immédiat | 237 | 167 | 167 | 100,0 % | 0,83 | 100,0 % | +230 $ | **−696 $** [−2 012 $ ; +606 $] | −363 $ | −30 $ | −1 043 $ | −50 $ | 14 | 6/11 | +1 220 $ | −1 789 $ | +2 019 $ | +50 $ | 0/0 |
| H21 recharge du carnet | 237 | 167 | 165 | 98,8 % | 0,84 | 100,0 % | +51 $ | **−875 $** [−2 219 $ ; +386 $] | −542 $ | −209 $ | −1 110 $ | −50 $ | 14 | 6/11 | +1 142 $ | −1 949 $ | +2 000 $ | +50 $ | 0/0 |
| H22 hybride 50 % immédiat + 50 % passif | 237 | 167 | 167 | 100,0 % | 0,84 | 95,2 % | −127 $ | **−1 053 $** [−2 391 $ ; +186 $] | −720 $ | −387 $ | −1 180 $ | −50 $ | 14 | 6/11 | +1 216 $ | −1 983 $ | +2 019 $ | +50 $ | 0/0 |
| H23 boomerang (revente de l'opposé +5 c) | 35 | 26 | 26 | 100,0 % | 0,66 | 100,0 % | −250 $ | **−1 176 $** [−3 066 $ ; +467 $] | −457 $ | +0 $ | −259 $ | −50 $ | 4 | 0/11 | +42 $ | +79 $ | −265 $ | +50 $ | 205/204 |
| H24 moteur d'inventaire deux jambes | 237 | 231 | 231 | 100,0 % | 0,60 | 31,6 % | +465 $ | **−461 $** [−936 $ ; +23 $] | +124 $ | +715 $ | −944 $ | −70 $ | 12 | 7/11 | +270 $ | +882 $ | −81 $ | +71 $ | 0/0 |

### B · V2-F corrigé 0,015 % — idéal — inédit

| Couverture | Positions | Tentées | Exécutées | Taux d'exécution | Prix moyen opposé | Quantité couverte moy. | P&L net | Δ vs GARDER [IC 90 %] | Δ vs VENDRE 50 % | Δ vs VENDRE 100 % | Creux max | Perte max (1 position) | Plus longue série perdante | Jackpots gardés | Profit sacrifié (jackpots) | Profit verrouillé (paires) | P&L des positions non couvertes | Capital immobilisé max | Entrées réduites / refusées |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| GARDER (référence) | 14 | — | — | — | — | — | −250 $ | 0 | — | — | −250 $ | −50 $ | 7 | 0/0 | 0 $ | 0 $ | −250 $ | +50 $ | 169/164 |
| H01 verrouillage paire complète (coût < 1) | 178 | 141 | 141 | 100,0 % | 0,67 | 100,0 % | −53 $ | **+197 $** [−329 $ ; +737 $] | +197 $ | +86 $ | −324 $ | −50 $ | 3 | 0/0 | +0 $ | +1 201 $ | −1 253 $ | +50 $ | 0/0 |
| H02 verrouillage partiel 25 % | 38 | 29 | 28 | 96,6 % | 0,65 | 25,0 % | −250 $ | **−0 $** [−455 $ ; +390 $] | −0 $ | −111 $ | −251 $ | −50 $ | 7 | 0/0 | +0 $ | +78 $ | −309 $ | +50 $ | 142/140 |
| H03 verrouillage partiel 50 % | 39 | 30 | 29 | 96,7 % | 0,70 | 50,0 % | −250 $ | **−0 $** [−442 $ ; +344 $] | −0 $ | −111 $ | −250 $ | −50 $ | 8 | 0/0 | +0 $ | +111 $ | −324 $ | +50 $ | 140/139 |
| H04 plancher de profit (les 2 issues ≥ 0) | 37 | 28 | 27 | 96,4 % | 0,67 | 80,7 % | −250 $ | **+0 $** [−263 $ ; +231 $] | +0 $ | −113 $ | −250 $ | −50 $ | 3 | 0/0 | +0 $ | +124 $ | −303 $ | +50 $ | 142/141 |
| H05 réserve jackpot (≥ 70 % gardé) | 38 | 29 | 28 | 96,6 % | 0,67 | 34,8 % | −250 $ | **−0 $** [−431 $ ; +354 $] | +0 $ | −111 $ | −250 $ | −50 $ | 7 | 0/0 | +0 $ | +75 $ | −308 $ | +50 $ | 141/140 |
| H06 échelle de paires (4 tranches) | 178 | 141 | 141 | 100,0 % | 0,62 | 87,9 % | −103 $ | **+147 $** [−517 $ ; +783 $] | +147 $ | +37 $ | −361 $ | −50 $ | 9 | 0/0 | +0 $ | +1 654 $ | −1 253 $ | +50 $ | 0/0 |
| H07 pire perte limitée à −25 $ | 22 | 7 | 7 | 100,0 % | 0,92 | 100,0 % | −250 $ | **−0 $** [−148 $ ; +148 $] | −0 $ | −1 $ | −250 $ | −32 $ | 7 | 0/0 | +0 $ | −205 $ | −45 $ | +50 $ | 163/156 |
| H08 pire perte limitée à −10 $ | 30 | 17 | 16 | 94,1 % | 0,86 | 100,0 % | −250 $ | **−0 $** [−298 $ ; +257 $] | −0 $ | −1 $ | −250 $ | −45 $ | 9 | 0/0 | +0 $ | −272 $ | +22 $ | +50 $ | 149/148 |
| H09 pire issue à 0 dans le budget (après modèle −10) | 39 | 27 | 11 | 40,7 % | 0,67 | 72,2 % | −250 $ | **+0 $** [−497 $ ; +419 $] | −567 $ | −1 195 $ | −342 $ | −50 $ | 6 | 0/0 | +0 $ | +85 $ | −233 $ | +50 $ | 140/139 |
| H10 couvrir ou vendre (avantage net) | 178 | 117 | 117 | 100,0 % | — | 100,0 % | +945 $ | **+1 195 $** [+162 $ ; +2 158 $] | +628 $ | +0 $ | −325 $ | −50 $ | 14 | 0/0 | +0 $ | +0 $ | +1 859 $ | +50 $ | 0/0 |
| H11 alerte précoce (2 signaux sur 3) 25 % | 38 | 25 | 24 | 96,0 % | 0,77 | 25,0 % | −250 $ | **−0 $** [−459 $ ; +387 $] | −0 $ | +0 $ | −266 $ | −50 $ | 7 | 0/0 | +0 $ | −17 $ | +103 $ | +50 $ | 141/140 |
| H12 horloge de risque (immédiat / attendre 3 s) | 178 | 117 | 114 | 97,4 % | 0,81 | 100,0 % | +785 $ | **+1 035 $** [−14 $ ; +1 995 $] | +468 $ | −160 $ | −336 $ | −50 $ | 14 | 0/0 | +0 $ | −967 $ | +1 752 $ | +50 $ | 0/0 |
| H13 prédictive 1 s | 178 | 117 | 117 | 100,0 % | 0,82 | 100,0 % | +827 $ | **+1 077 $** [+116 $ ; +2 033 $] | +510 $ | −118 $ | −325 $ | −50 $ | 14 | 0/0 | +0 $ | −1 033 $ | +1 859 $ | +50 $ | 0/0 |
| H14 prédictive 3 s | 178 | 117 | 117 | 100,0 % | 0,83 | 100,0 % | +549 $ | **+799 $** [−187 $ ; +1 784 $] | +233 $ | −395 $ | −377 $ | −50 $ | 14 | 0/0 | +0 $ | −1 310 $ | +1 859 $ | +50 $ | 2/0 |
| H15 prédictive 5 s | 178 | 117 | 117 | 100,0 % | 0,83 | 100,0 % | +648 $ | **+898 $** [−138 $ ; +1 891 $] | +331 $ | −297 $ | −352 $ | −50 $ | 14 | 0/0 | +0 $ | −1 211 $ | +1 859 $ | +50 $ | 0/0 |
| H16 prédictive 10 s | 178 | 117 | 117 | 100,0 % | 0,82 | 100,0 % | +842 $ | **+1 092 $** [+68 $ ; +2 037 $] | +526 $ | −102 $ | −306 $ | −50 $ | 14 | 0/0 | +0 $ | −1 017 $ | +1 859 $ | +50 $ | 0/0 |
| H17 premier passage (limite si EV > immédiat) | 178 | 117 | 117 | 100,0 % | 0,82 | 100,0 % | +815 $ | **+1 065 $** [+36 $ ; +2 052 $] | +498 $ | −130 $ | −315 $ | −50 $ | 14 | 0/0 | +0 $ | −1 045 $ | +1 859 $ | +50 $ | 0/0 |
| H18 fenêtre de conversion prédite (paire ≤ 0,95) — inactive si seuil appris = jamais | 14 | 0 | 0 | — | — | — | −250 $ | **+0 $** [+0 $ ; +0 $] | +0 $ | +0 $ | −250 $ | −50 $ | 7 | 0/0 | +0 $ | +0 $ | −250 $ | +50 $ | 169/164 |
| H19 sauvetage passif (vendeur − 1 c, 10 s) | 17 | 11 | 4 | 36,4 % | 0,91 | 90,8 % | −250 $ | **+0 $** [−81 $ ; +72 $] | −567 $ | −1 195 $ | −250 $ | −50 $ | 7 | 0/0 | +0 $ | −22 $ | −213 $ | +50 $ | 165/161 |
| H20 prédicteur de file (traversée) passif sinon immédiat | 178 | 117 | 117 | 100,0 % | 0,83 | 100,0 % | +703 $ | **+953 $** [−49 $ ; +1 919 $] | +387 $ | −241 $ | −352 $ | −50 $ | 14 | 0/0 | +0 $ | −1 156 $ | +1 859 $ | +50 $ | 0/0 |
| H21 recharge du carnet | 178 | 117 | 115 | 98,3 % | 0,83 | 100,0 % | +644 $ | **+894 $** [−143 $ ; +1 902 $] | +327 $ | −301 $ | −361 $ | −50 $ | 14 | 0/0 | +0 $ | −1 163 $ | +1 807 $ | +50 $ | 0/0 |
| H22 hybride 50 % immédiat + 50 % passif | 178 | 117 | 117 | 100,0 % | 0,83 | 97,4 % | +593 $ | **+843 $** [−125 $ ; +1 845 $] | +276 $ | −352 $ | −348 $ | −50 $ | 14 | 0/0 | +0 $ | −1 200 $ | +1 859 $ | +50 $ | 0/0 |
| H23 boomerang (revente de l'opposé +5 c) | 24 | 18 | 16 | 88,9 % | 0,67 | 100,0 % | −250 $ | **−0 $** [−212 $ ; +186 $] | +0 $ | −111 $ | −250 $ | −50 $ | 7 | 0/0 | +0 $ | +19 $ | −112 $ | +50 $ | 156/154 |
| H24 moteur d'inventaire deux jambes | 14 | 14 | 12 | 85,7 % | 0,70 | 23,9 % | −250 $ | **+0 $** [−35 $ ; +35 $] | −1 $ | −86 $ | −250 $ | −66 $ | 7 | 0/0 | +0 $ | +28 $ | −2 $ | +66 $ | 168/164 |

### B · V2-F corrigé 0,015 % — prudent — validation

| Couverture | Positions | Tentées | Exécutées | Taux d'exécution | Prix moyen opposé | Quantité couverte moy. | P&L net | Δ vs GARDER [IC 90 %] | Δ vs VENDRE 50 % | Δ vs VENDRE 100 % | Creux max | Perte max (1 position) | Plus longue série perdante | Jackpots gardés | Profit sacrifié (jackpots) | Profit verrouillé (paires) | P&L des positions non couvertes | Capital immobilisé max | Entrées réduites / refusées |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| GARDER (référence) | 141 | — | — | — | — | — | −250 $ | 0 | — | — | −873 $ | −50 $ | 10 | 5/5 | 0 $ | 0 $ | −250 $ | +50 $ | 7/3 |
| H01 verrouillage paire complète (coût < 1) | 62 | 45 | 43 | 95,6 % | 0,62 | 97,8 % | −250 $ | **−0 $** [−1 409 $ ; +1 391 $] | −0 $ | +0 $ | −387 $ | −50 $ | 5 | 1/5 | +172 $ | +448 $ | −727 $ | +290 $ | 133/132 |
| H02 verrouillage partiel 25 % | 137 | 92 | 84 | 91,3 % | 0,64 | 24,9 % | −250 $ | **−0 $** [−368 $ ; +387 $] | −0 $ | +0 $ | −709 $ | −50 $ | 9 | 5/5 | +228 $ | +240 $ | −1 874 $ | +151 $ | 13/7 |
| H03 verrouillage partiel 50 % | 67 | 50 | 45 | 90,0 % | 0,64 | 49,0 % | −250 $ | **−0 $** [−1 311 $ ; +1 248 $] | −0 $ | +0 $ | −362 $ | −50 $ | 6 | 1/5 | +113 $ | +231 $ | −709 $ | +248 $ | 130/124 |
| H04 plancher de profit (les 2 issues ≥ 0) | 61 | 45 | 43 | 95,6 % | 0,64 | 81,6 % | −250 $ | **−0 $** [−1 368 $ ; +1 373 $] | −0 $ | +0 $ | −384 $ | −50 $ | 4 | 1/5 | +108 $ | +287 $ | −673 $ | +333 $ | 134/133 |
| H05 réserve jackpot (≥ 70 % gardé) | 136 | 91 | 87 | 95,6 % | 0,61 | 34,0 % | −250 $ | **−0 $** [−522 $ ; +547 $] | −0 $ | +0 $ | −655 $ | −50 $ | 9 | 5/5 | +324 $ | +391 $ | −1 883 $ | +177 $ | 9/8 |
| H06 échelle de paires (4 tranches) | 62 | 45 | 43 | 95,6 % | 0,57 | 92,3 % | −250 $ | **−0 $** [−1 471 $ ; +1 465 $] | −0 $ | −0 $ | −396 $ | −50 $ | 5 | 0/5 | +213 $ | +606 $ | −730 $ | +272 $ | 133/132 |
| H07 pire perte limitée à −25 $ | 135 | 77 | 75 | 97,4 % | 0,89 | 82,0 % | −250 $ | **+0 $** [−775 $ ; +781 $] | −1 $ | −1 $ | −649 $ | −50 $ | 14 | 4/5 | +190 $ | −1 854 $ | +1 681 $ | +368 $ | 23/9 |
| H08 pire perte limitée à −10 $ | 61 | 48 | 47 | 97,9 % | 0,81 | 85,7 % | −250 $ | **+0 $** [−1 350 $ ; +1 370 $] | −0 $ | +0 $ | −333 $ | −48 $ | 15 | 1/5 | +0 $ | −634 $ | +607 $ | +314 $ | 135/133 |
| H09 pire issue à 0 dans le budget (après modèle −10) | 127 | 89 | 36 | 40,4 % | 0,60 | 69,2 % | −250 $ | **+0 $** [−720 $ ; +827 $] | −0 $ | +0 $ | −644 $ | −50 $ | 7 | 3/5 | +427 $ | +360 $ | −1 091 $ | +243 $ | 22/20 |
| H10 couvrir ou vendre (avantage net) | 109 | 75 | 75 | 100,0 % | — | 98,9 % | −250 $ | **−0 $** [−1 256 $ ; +1 291 $] | −0 $ | −0 $ | −364 $ | −50 $ | 11 | 2/5 | +891 $ | +0 $ | +1 010 $ | +50 $ | 66/56 |
| H11 alerte précoce (2 signaux sur 3) 25 % | 137 | 116 | 113 | 97,4 % | 0,78 | 24,6 % | −250 $ | **+0 $** [−349 $ ; +378 $] | −1 $ | −1 $ | −720 $ | −50 $ | 9 | 5/5 | +232 $ | −193 $ | −155 $ | +158 $ | 14/7 |
| H12 horloge de risque (immédiat / attendre 3 s) | 37 | 23 | 22 | 95,7 % | 0,83 | 89,0 % | −250 $ | **−0 $** [−1 321 $ ; +1 346 $] | −0 $ | +0 $ | −269 $ | −50 $ | 9 | 1/5 | +140 $ | −294 $ | +109 $ | +262 $ | 178/176 |
| H13 prédictive 1 s | 36 | 22 | 22 | 100,0 % | 0,82 | 83,7 % | −250 $ | **−0 $** [−1 318 $ ; +1 386 $] | −0 $ | +0 $ | −269 $ | −50 $ | 8 | 1/5 | +167 $ | −269 $ | +128 $ | +234 $ | 183/177 |
| H14 prédictive 3 s | 113 | 77 | 77 | 100,0 % | 0,84 | 87,7 % | −250 $ | **−0 $** [−1 030 $ ; +1 181 $] | −0 $ | −0 $ | −438 $ | −50 $ | 11 | 3/5 | +612 $ | −1 068 $ | +840 $ | +289 $ | 53/46 |
| H15 prédictive 5 s | 36 | 22 | 22 | 100,0 % | 0,83 | 82,7 % | −250 $ | **−0 $** [−1 393 $ ; +1 436 $] | −0 $ | +0 $ | −269 $ | −50 $ | 8 | 1/5 | +167 $ | −282 $ | +133 $ | +231 $ | 183/177 |
| H16 prédictive 10 s | 36 | 22 | 22 | 100,0 % | 0,83 | 83,3 % | −250 $ | **−0 $** [−1 323 $ ; +1 396 $] | −0 $ | +0 $ | −269 $ | −50 $ | 8 | 1/5 | +167 $ | −279 $ | +128 $ | +234 $ | 183/177 |
| H17 premier passage (limite si EV > immédiat) | 36 | 22 | 22 | 100,0 % | 0,82 | 83,7 % | −250 $ | **−0 $** [−1 308 $ ; +1 295 $] | −0 $ | +0 $ | −269 $ | −50 $ | 8 | 1/5 | +167 $ | −269 $ | +128 $ | +234 $ | 183/177 |
| H18 fenêtre de conversion prédite (paire ≤ 0,95) — inactive si seuil appris = jamais | 141 | 0 | 0 | — | — | — | −250 $ | **+0 $** [+0 $ ; +0 $] | +0 $ | +0 $ | −873 $ | −50 $ | 10 | 5/5 | +0 $ | +0 $ | −250 $ | +50 $ | 7/3 |
| H19 sauvetage passif (vendeur − 1 c, 10 s) | 126 | 88 | 24 | 27,3 % | 0,77 | 98,4 % | −250 $ | **+0 $** [−891 $ ; +973 $] | −0 $ | +0 $ | −710 $ | −50 $ | 11 | 3/5 | +507 $ | −155 $ | −78 $ | +365 $ | 24/22 |
| H20 prédicteur de file (traversée) passif sinon immédiat | 113 | 77 | 77 | 100,0 % | 0,85 | 92,5 % | −250 $ | **+0 $** [−1 057 $ ; +1 125 $] | −0 $ | +0 $ | −455 $ | −50 $ | 11 | 2/5 | +671 $ | −1 208 $ | +983 $ | +377 $ | 48/46 |
| H21 recharge du carnet | 22 | 14 | 12 | 85,7 % | 0,81 | 92,8 % | −250 $ | **−0 $** [−1 489 $ ; +1 426 $] | −0 $ | +0 $ | −269 $ | −50 $ | 6 | 0/5 | +0 $ | −187 $ | −92 $ | +202 $ | 205/204 |
| H22 hybride 50 % immédiat + 50 % passif | 113 | 77 | 77 | 100,0 % | 0,85 | 87,4 % | −250 $ | **−0 $** [−1 116 $ ; +1 074 $] | −0 $ | +0 $ | −434 $ | −50 $ | 11 | 2/5 | +631 $ | −1 183 $ | +986 $ | +378 $ | 49/46 |
| H23 boomerang (revente de l'opposé +5 c) | 141 | 93 | 88 | 94,6 % | 0,61 | 89,5 % | −250 $ | **+0 $** [−363 $ ; +326 $] | +0 $ | +0 $ | −787 $ | −50 $ | 9 | 5/5 | +30 $ | +299 $ | −2 012 $ | +336 $ | 11/3 |
| H24 moteur d'inventaire deux jambes | 136 | 132 | 131 | 99,2 % | 0,56 | 27,3 % | −250 $ | **−0 $** [−521 $ ; +559 $] | −1 $ | −0 $ | −775 $ | −69 $ | 9 | 4/5 | +157 $ | +575 $ | −55 $ | +100 $ | 11/8 |

### B · V2-F corrigé 0,015 % — prudent — inédit

| Couverture | Positions | Tentées | Exécutées | Taux d'exécution | Prix moyen opposé | Quantité couverte moy. | P&L net | Δ vs GARDER [IC 90 %] | Δ vs VENDRE 50 % | Δ vs VENDRE 100 % | Creux max | Perte max (1 position) | Plus longue série perdante | Jackpots gardés | Profit sacrifié (jackpots) | Profit verrouillé (paires) | P&L des positions non couvertes | Capital immobilisé max | Entrées réduites / refusées |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| GARDER (référence) | 16 | — | — | — | — | — | −250 $ | 0 | — | — | −267 $ | −50 $ | 6 | 0/0 | 0 $ | 0 $ | −250 $ | +50 $ | 148/145 |
| H01 verrouillage paire complète (coût < 1) | 21 | 15 | 13 | 86,7 % | 0,56 | 73,6 % | −250 $ | **+0 $** [−304 $ ; +313 $] | +0 $ | +0 $ | −250 $ | −50 $ | 4 | 0/0 | +0 $ | +182 $ | −340 $ | +150 $ | 141/140 |
| H02 verrouillage partiel 25 % | 17 | 13 | 11 | 84,6 % | 0,62 | 24,7 % | −250 $ | **+0 $** [−137 $ ; +152 $] | +0 $ | +0 $ | −250 $ | −50 $ | 6 | 0/0 | +0 $ | +44 $ | −235 $ | +113 $ | 145/144 |
| H03 verrouillage partiel 50 % | 20 | 14 | 12 | 85,7 % | 0,59 | 46,7 % | −250 $ | **−0 $** [−297 $ ; +303 $] | −0 $ | −0 $ | −250 $ | −50 $ | 6 | 0/0 | +0 $ | +113 $ | −303 $ | +156 $ | 142/141 |
| H04 plancher de profit (les 2 issues ≥ 0) | 19 | 13 | 12 | 92,3 % | 0,59 | 59,9 % | −250 $ | **−0 $** [−285 $ ; +290 $] | +0 $ | +0 $ | −250 $ | −50 $ | 3 | 0/0 | +0 $ | +113 $ | −250 $ | +144 $ | 143/142 |
| H05 réserve jackpot (≥ 70 % gardé) | 18 | 13 | 12 | 92,3 % | 0,60 | 31,6 % | −250 $ | **+0 $** [−179 $ ; +184 $] | +0 $ | +0 $ | −250 $ | −50 $ | 6 | 0/0 | +0 $ | +70 $ | −238 $ | +124 $ | 144/143 |
| H06 échelle de paires (4 tranches) | 23 | 17 | 15 | 88,2 % | 0,56 | 70,3 % | −250 $ | **+0 $** [−417 $ ; +464 $] | +0 $ | +0 $ | −256 $ | −50 $ | 6 | 0/0 | +0 $ | +242 $ | −329 $ | +163 $ | 139/138 |
| H07 pire perte limitée à −25 $ | 17 | 10 | 10 | 100,0 % | 0,91 | 59,2 % | −250 $ | **−0 $** [−148 $ ; +145 $] | −0 $ | −1 $ | −250 $ | −49 $ | 6 | 0/0 | +0 $ | −184 $ | +31 $ | +214 $ | 146/144 |
| H08 pire perte limitée à −10 $ | 19 | 15 | 14 | 93,3 % | 0,83 | 81,1 % | −250 $ | **+0 $** [−366 $ ; +384 $] | −0 $ | −1 $ | −250 $ | −50 $ | 6 | 0/0 | +0 $ | −185 $ | +19 $ | +228 $ | 142/142 |
| H09 pire issue à 0 dans le budget (après modèle −10) | 16 | 10 | 3 | 30,0 % | 0,56 | 79,3 % | −250 $ | **−0 $** [−128 $ ; +121 $] | −0 $ | +0 $ | −250 $ | −50 $ | 6 | 0/0 | +0 $ | +48 $ | −276 $ | +158 $ | 148/145 |
| H10 couvrir ou vendre (avantage net) | 23 | 16 | 16 | 100,0 % | — | 100,0 % | −250 $ | **−0 $** [−152 $ ; +147 $] | −0 $ | −0 $ | −250 $ | −50 $ | 14 | 0/0 | +0 $ | +0 $ | −27 $ | +50 $ | 144/138 |
| H11 alerte précoce (2 signaux sur 3) 25 % | 16 | 9 | 8 | 88,9 % | 0,86 | 22,8 % | −250 $ | **−0 $** [−69 $ ; +57 $] | −1 $ | −1 $ | −250 $ | −50 $ | 6 | 0/0 | +0 $ | −33 $ | −96 $ | +125 $ | 148/145 |
| H12 horloge de risque (immédiat / attendre 3 s) | 17 | 11 | 9 | 81,8 % | 0,80 | 81,7 % | −250 $ | **+0 $** [−86 $ ; +89 $] | −0 $ | +0 $ | −266 $ | −50 $ | 8 | 0/0 | +0 $ | −78 $ | −90 $ | +251 $ | 145/144 |
| H13 prédictive 1 s | 16 | 10 | 9 | 90,0 % | 0,82 | 82,6 % | −250 $ | **+0 $** [−129 $ ; +118 $] | −0 $ | +0 $ | −250 $ | −50 $ | 7 | 0/0 | +0 $ | −105 $ | −66 $ | +222 $ | 148/145 |
| H14 prédictive 3 s | 17 | 11 | 10 | 90,9 % | 0,81 | 75,7 % | −250 $ | **+0 $** [−85 $ ; +77 $] | −0 $ | +0 $ | −261 $ | −50 $ | 8 | 0/0 | +0 $ | −96 $ | −33 $ | +245 $ | 145/144 |
| H15 prédictive 5 s | 16 | 10 | 9 | 90,0 % | 0,83 | 81,8 % | −250 $ | **+0 $** [−126 $ ; +110 $] | −0 $ | +0 $ | −250 $ | −50 $ | 7 | 0/0 | +0 $ | −108 $ | −60 $ | +217 $ | 148/145 |
| H16 prédictive 10 s | 16 | 10 | 9 | 90,0 % | 0,82 | 82,6 % | −250 $ | **+0 $** [−129 $ ; +118 $] | −0 $ | +0 $ | −250 $ | −50 $ | 7 | 0/0 | +0 $ | −105 $ | −67 $ | +222 $ | 148/145 |
| H17 premier passage (limite si EV > immédiat) | 16 | 10 | 9 | 90,0 % | 0,82 | 82,6 % | −250 $ | **+0 $** [−131 $ ; +124 $] | −0 $ | +0 $ | −250 $ | −50 $ | 7 | 0/0 | +0 $ | −105 $ | −67 $ | +222 $ | 148/145 |
| H18 fenêtre de conversion prédite (paire ≤ 0,95) — inactive si seuil appris = jamais | 16 | 0 | 0 | — | — | — | −250 $ | **−0 $** [+0 $ ; +0 $] | −0 $ | −0 $ | −267 $ | −50 $ | 6 | 0/0 | +0 $ | +0 $ | −250 $ | +50 $ | 148/145 |
| H19 sauvetage passif (vendeur − 1 c, 10 s) | 14 | 8 | 2 | 25,0 % | 0,73 | 76,6 % | −250 $ | **−0 $** [−135 $ ; +119 $] | −0 $ | +0 $ | −250 $ | −50 $ | 6 | 0/0 | +0 $ | −16 $ | −210 $ | +149 $ | 149/148 |
| H20 prédicteur de file (traversée) passif sinon immédiat | 16 | 10 | 9 | 90,0 % | 0,82 | 82,6 % | −250 $ | **+0 $** [−132 $ ; +116 $] | −0 $ | +0 $ | −250 $ | −50 $ | 7 | 0/0 | +0 $ | −105 $ | −67 $ | +222 $ | 148/145 |
| H21 recharge du carnet | 16 | 10 | 8 | 80,0 % | 0,84 | 86,3 % | −250 $ | **+0 $** [−126 $ ; +97 $] | −0 $ | +0 $ | −250 $ | −50 $ | 6 | 0/0 | +0 $ | −110 $ | −100 $ | +211 $ | 148/145 |
| H22 hybride 50 % immédiat + 50 % passif | 16 | 10 | 9 | 90,0 % | 0,84 | 81,0 % | −250 $ | **−0 $** [−142 $ ; +115 $] | −0 $ | +0 $ | −250 $ | −50 $ | 7 | 0/0 | +0 $ | −114 $ | −51 $ | +209 $ | 148/145 |
| H23 boomerang (revente de l'opposé +5 c) | 14 | 10 | 8 | 80,0 % | 0,60 | 68,9 % | −250 $ | **−0 $** [−119 $ ; +103 $] | −0 $ | −0 $ | −250 $ | −50 $ | 6 | 0/0 | +0 $ | +9 $ | −219 $ | +169 $ | 149/148 |
| H24 moteur d'inventaire deux jambes | 14 | 14 | 13 | 92,9 % | 0,59 | 21,7 % | −250 $ | **−0 $** [−88 $ ; +83 $] | −1 $ | −0 $ | −250 $ | −66 $ | 6 | 0/0 | +0 $ | +52 $ | −38 $ | +100 $ | 149/148 |

### B · V2-F corrigé 0,015 % — pessimiste — validation

| Couverture | Positions | Tentées | Exécutées | Taux d'exécution | Prix moyen opposé | Quantité couverte moy. | P&L net | Δ vs GARDER [IC 90 %] | Δ vs VENDRE 50 % | Δ vs VENDRE 100 % | Creux max | Perte max (1 position) | Plus longue série perdante | Jackpots gardés | Profit sacrifié (jackpots) | Profit verrouillé (paires) | P&L des positions non couvertes | Capital immobilisé max | Entrées réduites / refusées |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| GARDER (référence) | 65 | — | — | — | — | — | −250 $ | 0 | — | — | −492 $ | −50 $ | 6 | 2/2 | 0 $ | 0 $ | −250 $ | +50 $ | 97/96 |
| H01 verrouillage paire complète (coût < 1) | 56 | 40 | 38 | 95,0 % | 0,61 | 97,1 % | −250 $ | **+0 $** [−619 $ ; +552 $] | +0 $ | +0 $ | −351 $ | −50 $ | 6 | 1/2 | +170 $ | +378 $ | −616 $ | +269 $ | 132/127 |
| H02 verrouillage partiel 25 % | 65 | 46 | 44 | 95,7 % | 0,63 | 24,7 % | −250 $ | **+0 $** [−165 $ ; +151 $] | +0 $ | +0 $ | −425 $ | −50 $ | 6 | 2/2 | +61 $ | +105 $ | −659 $ | +141 $ | 97/96 |
| H03 verrouillage partiel 50 % | 65 | 46 | 44 | 95,7 % | 0,63 | 48,8 % | −250 $ | **−0 $** [−337 $ ; +307 $] | −0 $ | −0 $ | −358 $ | −50 $ | 6 | 1/2 | +122 $ | +205 $ | −637 $ | +235 $ | 97/96 |
| H04 plancher de profit (les 2 issues ≥ 0) | 56 | 40 | 38 | 95,0 % | 0,63 | 81,3 % | −250 $ | **−0 $** [−553 $ ; +496 $] | −0 $ | +0 $ | −361 $ | −50 $ | 6 | 1/2 | +164 $ | +265 $ | −599 $ | +273 $ | 132/127 |
| H05 réserve jackpot (≥ 70 % gardé) | 67 | 47 | 45 | 95,7 % | 0,63 | 32,7 % | −250 $ | **−0 $** [−219 $ ; +187 $] | −0 $ | −0 $ | −409 $ | −50 $ | 7 | 2/2 | +74 $ | +152 $ | −634 $ | +164 $ | 96/93 |
| H06 échelle de paires (4 tranches) | 54 | 39 | 38 | 97,4 % | 0,56 | 86,8 % | −250 $ | **+0 $** [−638 $ ; +586 $] | +0 $ | +0 $ | −357 $ | −50 $ | 4 | 0/2 | +179 $ | +443 $ | −513 $ | +192 $ | 134/133 |
| H07 pire perte limitée à −25 $ | 64 | 33 | 32 | 97,0 % | 0,88 | 86,9 % | −250 $ | **−0 $** [−476 $ ; +418 $] | −0 $ | −0 $ | −425 $ | −50 $ | 6 | 2/2 | +0 $ | −821 $ | +770 $ | +369 $ | 110/97 |
| H08 pire perte limitée à −10 $ | 56 | 39 | 39 | 100,0 % | 0,81 | 86,2 % | −250 $ | **−0 $** [−510 $ ; +494 $] | −1 $ | +0 $ | −386 $ | −45 $ | 11 | 1/2 | +0 $ | −586 $ | +529 $ | +355 $ | 132/127 |
| H09 pire issue à 0 dans le budget (après modèle −10) | 65 | 45 | 16 | 35,6 % | 0,58 | 72,2 % | −250 $ | **+0 $** [−256 $ ; +244 $] | −1 $ | +0 $ | −527 $ | −50 $ | 6 | 1/2 | +29 $ | +118 $ | −437 $ | +209 $ | 97/96 |
| H10 couvrir ou vendre (avantage net) | 77 | 53 | 52 | 98,1 % | — | 100,0 % | −250 $ | **−0 $** [−544 $ ; +511 $] | −1 $ | −0 $ | −419 $ | −50 $ | 14 | 1/2 | +51 $ | +0 $ | +497 $ | +50 $ | 94/75 |
| H11 alerte précoce (2 signaux sur 3) 25 % | 65 | 62 | 61 | 98,4 % | 0,78 | 24,7 % | −250 $ | **−0 $** [−191 $ ; +159 $] | −1 $ | −1 $ | −391 $ | −50 $ | 6 | 2/2 | +68 $ | −94 $ | +79 $ | +146 $ | 97/96 |
| H12 horloge de risque (immédiat / attendre 3 s) | 64 | 44 | 43 | 97,7 % | 0,83 | 82,7 % | −250 $ | **−0 $** [−493 $ ; +432 $] | −1 $ | −0 $ | −383 $ | −50 $ | 11 | 1/2 | +25 $ | −509 $ | +445 $ | +372 $ | 115/97 |
| H13 prédictive 1 s | 64 | 44 | 43 | 97,7 % | 0,83 | 83,4 % | −250 $ | **+0 $** [−523 $ ; +430 $] | −1 $ | −0 $ | −383 $ | −50 $ | 11 | 1/2 | +38 $ | −514 $ | +446 $ | +372 $ | 115/97 |
| H14 prédictive 3 s | 64 | 44 | 43 | 97,7 % | 0,83 | 81,3 % | −250 $ | **−0 $** [−513 $ ; +446 $] | −1 $ | −0 $ | −377 $ | −50 $ | 11 | 2/2 | +9 $ | −501 $ | +448 $ | +366 $ | 115/97 |
| H15 prédictive 5 s | 46 | 28 | 25 | 89,3 % | 0,82 | 79,1 % | −250 $ | **+0 $** [−611 $ ; +568 $] | −1 $ | +0 $ | −322 $ | −50 $ | 9 | 1/2 | +41 $ | −308 $ | +262 $ | +303 $ | 162/149 |
| H16 prédictive 10 s | 64 | 44 | 43 | 97,7 % | 0,84 | 79,0 % | −250 $ | **+0 $** [−494 $ ; +446 $] | −1 $ | +0 $ | −367 $ | −50 $ | 11 | 2/2 | +3 $ | −516 $ | +448 $ | +356 $ | 115/97 |
| H17 premier passage (limite si EV > immédiat) | 64 | 44 | 43 | 97,7 % | 0,83 | 83,4 % | −250 $ | **+0 $** [−487 $ ; +437 $] | −1 $ | −0 $ | −383 $ | −50 $ | 11 | 1/2 | +38 $ | −514 $ | +446 $ | +372 $ | 115/97 |
| H18 fenêtre de conversion prédite (paire ≤ 0,95) — inactive si seuil appris = jamais | 65 | 0 | 0 | — | — | — | −250 $ | **+0 $** [+0 $ ; +0 $] | +0 $ | +0 $ | −492 $ | −50 $ | 6 | 2/2 | +0 $ | +0 $ | −250 $ | +50 $ | 97/96 |
| H19 sauvetage passif (vendeur − 1 c, 10 s) | 94 | 65 | 16 | 24,6 % | 0,73 | 89,4 % | −250 $ | **−0 $** [−637 $ ; +646 $] | −1 $ | −0 $ | −544 $ | −50 $ | 10 | 2/2 | +0 $ | −72 $ | −102 $ | +212 $ | 45/41 |
| H20 prédicteur de file (traversée) passif sinon immédiat | 18 | 10 | 9 | 90,0 % | 0,81 | 93,5 % | −250 $ | **+0 $** [−837 $ ; +746 $] | −0 $ | +0 $ | −301 $ | −50 $ | 8 | 0/2 | +0 $ | −157 $ | −63 $ | +212 $ | 204/204 |
| H21 recharge du carnet | 55 | 37 | 34 | 91,9 % | 0,82 | 74,9 % | −250 $ | **−0 $** [−498 $ ; +458 $] | −1 $ | −0 $ | −313 $ | −50 $ | 10 | 1/2 | +85 $ | −391 $ | +409 $ | +257 $ | 142/132 |
| H22 hybride 50 % immédiat + 50 % passif | 18 | 10 | 9 | 90,0 % | 0,81 | 93,1 % | −250 $ | **−0 $** [−809 $ ; +764 $] | −1 $ | −0 $ | −308 $ | −50 $ | 8 | 0/2 | +0 $ | −162 $ | −57 $ | +207 $ | 205/204 |
| H23 boomerang (revente de l'opposé +5 c) | 55 | 39 | 38 | 97,4 % | 0,60 | 91,6 % | −250 $ | **−0 $** [−394 $ ; +346 $] | −0 $ | +0 $ | −426 $ | −50 $ | 6 | 1/2 | −4 $ | +148 $ | −534 $ | +336 $ | 133/132 |
| H24 moteur d'inventaire deux jambes | 56 | 54 | 53 | 98,1 % | 0,53 | 30,0 % | −250 $ | **+0 $** [−322 $ ; +333 $] | −1 $ | −0 $ | −418 $ | −69 $ | 6 | 1/2 | +50 $ | +254 $ | −63 $ | +100 $ | 132/127 |

### B · V2-F corrigé 0,015 % — pessimiste — inédit

| Couverture | Positions | Tentées | Exécutées | Taux d'exécution | Prix moyen opposé | Quantité couverte moy. | P&L net | Δ vs GARDER [IC 90 %] | Δ vs VENDRE 50 % | Δ vs VENDRE 100 % | Creux max | Perte max (1 position) | Plus longue série perdante | Jackpots gardés | Profit sacrifié (jackpots) | Profit verrouillé (paires) | P&L des positions non couvertes | Capital immobilisé max | Entrées réduites / refusées |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| GARDER (référence) | 17 | — | — | — | — | — | −250 $ | 0 | — | — | −250 $ | −50 $ | 6 | 0/0 | 0 $ | 0 $ | −250 $ | +50 $ | 145/143 |
| H01 verrouillage paire complète (coût < 1) | 45 | 34 | 31 | 91,2 % | 0,64 | 81,3 % | −250 $ | **+0 $** [−391 $ ; +436 $] | +0 $ | +0 $ | −303 $ | −50 $ | 4 | 0/0 | +0 $ | +260 $ | −543 $ | +203 $ | 90/89 |
| H02 verrouillage partiel 25 % | 19 | 15 | 12 | 80,0 % | 0,61 | 25,0 % | −250 $ | **+0 $** [−102 $ ; +117 $] | +0 $ | +0 $ | −250 $ | −50 $ | 6 | 0/0 | +0 $ | +43 $ | −219 $ | +87 $ | 142/141 |
| H03 verrouillage partiel 50 % | 21 | 17 | 15 | 88,2 % | 0,63 | 47,0 % | −250 $ | **−0 $** [−198 $ ; +214 $] | +0 $ | +0 $ | −250 $ | −50 $ | 6 | 0/0 | +0 $ | +88 $ | −249 $ | +127 $ | 140/139 |
| H04 plancher de profit (les 2 issues ≥ 0) | 21 | 17 | 15 | 88,2 % | 0,64 | 72,7 % | −250 $ | **−0 $** [−262 $ ; +298 $] | −0 $ | +0 $ | −250 $ | −50 $ | 2 | 0/0 | +0 $ | +94 $ | −229 $ | +146 $ | 140/139 |
| H05 réserve jackpot (≥ 70 % gardé) | 20 | 16 | 13 | 81,2 % | 0,59 | 32,2 % | −250 $ | **−0 $** [−131 $ ; +135 $] | +0 $ | +0 $ | −250 $ | −50 $ | 6 | 0/0 | +0 $ | +63 $ | −246 $ | +98 $ | 142/140 |
| H06 échelle de paires (4 tranches) | 45 | 34 | 30 | 88,2 % | 0,58 | 74,0 % | −250 $ | **−0 $** [−371 $ ; +434 $] | +0 $ | +0 $ | −340 $ | −50 $ | 7 | 0/0 | +0 $ | +369 $ | −531 $ | +202 $ | 90/89 |
| H07 pire perte limitée à −25 $ | 20 | 8 | 8 | 100,0 % | 0,90 | 67,8 % | −250 $ | **+0 $** [−115 $ ; +94 $] | −1 $ | −0 $ | −261 $ | −47 $ | 6 | 0/0 | +0 $ | −164 $ | +42 $ | +216 $ | 142/140 |
| H08 pire perte limitée à −10 $ | 25 | 16 | 15 | 93,8 % | 0,85 | 81,1 % | −250 $ | **−0 $** [−244 $ ; +246 $] | −1 $ | −0 $ | −288 $ | −47 $ | 8 | 0/0 | +0 $ | −193 $ | +78 $ | +253 $ | 136/133 |
| H09 pire issue à 0 dans le budget (après modèle −10) | 16 | 10 | 5 | 50,0 % | 0,60 | 82,3 % | −250 $ | **+0 $** [−94 $ ; +94 $] | −1 $ | −0 $ | −250 $ | −50 $ | 3 | 0/0 | +0 $ | +32 $ | −280 $ | +99 $ | 148/145 |
| H10 couvrir ou vendre (avantage net) | 22 | 15 | 15 | 100,0 % | — | 99,9 % | −250 $ | **+0 $** [−104 $ ; +87 $] | −1 $ | +0 $ | −250 $ | −48 $ | 13 | 0/0 | +0 $ | +0 $ | −68 $ | +50 $ | 142/137 |
| H11 alerte précoce (2 signaux sur 3) 25 % | 18 | 10 | 9 | 90,0 % | 0,80 | 25,0 % | −250 $ | **+0 $** [−39 $ ; +38 $] | +0 $ | −1 $ | −250 $ | −50 $ | 6 | 0/0 | +0 $ | −18 $ | −15 $ | +98 $ | 143/142 |
| H12 horloge de risque (immédiat / attendre 3 s) | 17 | 11 | 9 | 81,8 % | 0,80 | 89,9 % | −250 $ | **−0 $** [−79 $ ; +63 $] | −1 $ | −0 $ | −250 $ | −50 $ | 8 | 0/0 | +0 $ | −53 $ | −153 $ | +204 $ | 145/143 |
| H13 prédictive 1 s | 17 | 11 | 10 | 90,9 % | 0,81 | 85,8 % | −250 $ | **+0 $** [−114 $ ; +81 $] | −1 $ | −0 $ | −250 $ | −49 $ | 8 | 0/0 | +0 $ | −76 $ | −104 $ | +204 $ | 145/143 |
| H14 prédictive 3 s | 17 | 11 | 10 | 90,9 % | 0,82 | 85,3 % | −250 $ | **−0 $** [−83 $ ; +61 $] | −1 $ | −0 $ | −250 $ | −49 $ | 8 | 0/0 | +0 $ | −77 $ | −100 $ | +201 $ | 145/143 |
| H15 prédictive 5 s | 17 | 11 | 10 | 90,9 % | 0,81 | 85,7 % | −250 $ | **−0 $** [−107 $ ; +83 $] | −1 $ | −0 $ | −250 $ | −49 $ | 8 | 0/0 | +0 $ | −77 $ | −102 $ | +203 $ | 145/143 |
| H16 prédictive 10 s | 17 | 11 | 10 | 90,9 % | 0,81 | 86,0 % | −250 $ | **+0 $** [−108 $ ; +87 $] | −1 $ | −0 $ | −250 $ | −49 $ | 8 | 0/0 | +0 $ | −76 $ | −104 $ | +204 $ | 145/143 |
| H17 premier passage (limite si EV > immédiat) | 17 | 11 | 10 | 90,9 % | 0,81 | 86,0 % | −250 $ | **+0 $** [−107 $ ; +86 $] | −1 $ | −0 $ | −250 $ | −49 $ | 8 | 0/0 | +0 $ | −76 $ | −104 $ | +204 $ | 145/143 |
| H18 fenêtre de conversion prédite (paire ≤ 0,95) — inactive si seuil appris = jamais | 17 | 0 | 0 | — | — | — | −250 $ | **+0 $** [+0 $ ; +0 $] | +0 $ | +0 $ | −250 $ | −50 $ | 6 | 0/0 | +0 $ | +0 $ | −250 $ | +50 $ | 145/143 |
| H19 sauvetage passif (vendeur − 1 c, 10 s) | 16 | 10 | 2 | 20,0 % | 0,76 | 86,9 % | −250 $ | **−0 $** [−148 $ ; +147 $] | −1 $ | −0 $ | −250 $ | −50 $ | 6 | 0/0 | +0 $ | −21 $ | −215 $ | +187 $ | 148/145 |
| H20 prédicteur de file (traversée) passif sinon immédiat | 17 | 11 | 10 | 90,9 % | 0,81 | 86,0 % | −250 $ | **+0 $** [−103 $ ; +82 $] | −1 $ | −0 $ | −250 $ | −49 $ | 8 | 0/0 | +0 $ | −76 $ | −104 $ | +204 $ | 145/143 |
| H21 recharge du carnet | 17 | 11 | 9 | 81,8 % | 0,81 | 88,8 % | −250 $ | **−0 $** [−107 $ ; +81 $] | −1 $ | −0 $ | −250 $ | −50 $ | 8 | 0/0 | +0 $ | −65 $ | −136 $ | +203 $ | 145/143 |
| H22 hybride 50 % immédiat + 50 % passif | 17 | 11 | 10 | 90,9 % | 0,83 | 83,9 % | −250 $ | **−0 $** [−120 $ ; +92 $] | −1 $ | −0 $ | −250 $ | −49 $ | 8 | 0/0 | +0 $ | −85 $ | −84 $ | +203 $ | 145/143 |
| H23 boomerang (revente de l'opposé +5 c) | 16 | 14 | 12 | 85,7 % | 0,68 | 79,5 % | −250 $ | **−0 $** [−138 $ ; +130 $] | −0 $ | +0 $ | −250 $ | −50 $ | 5 | 0/0 | +0 $ | +2 $ | −156 $ | +143 $ | 148/145 |
| H24 moteur d'inventaire deux jambes | 19 | 19 | 17 | 89,5 % | 0,54 | 30,7 % | −250 $ | **−0 $** [−135 $ ; +166 $] | −0 $ | +0 $ | −250 $ | −68 $ | 5 | 0/0 | +0 $ | +113 $ | −7 $ | +100 $ | 142/141 |

### C · V2-F original (diagnostic) — prudent — validation

| Couverture | Positions | Tentées | Exécutées | Taux d'exécution | Prix moyen opposé | Quantité couverte moy. | P&L net | Δ vs GARDER [IC 90 %] | Δ vs VENDRE 50 % | Δ vs VENDRE 100 % | Creux max | Perte max (1 position) | Plus longue série perdante | Jackpots gardés | Profit sacrifié (jackpots) | Profit verrouillé (paires) | P&L des positions non couvertes | Capital immobilisé max | Entrées réduites / refusées |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| GARDER (référence) | 7 | — | — | — | — | — | −250 $ | 0 | — | — | −250 $ | −50 $ | 7 | 0/0 | 0 $ | 0 $ | −250 $ | +50 $ | 371/370 |
| H01 verrouillage paire complète (coût < 1) | 22 | 14 | 13 | 92,9 % | 0,69 | 69,4 % | −250 $ | **+0 $** [−256 $ ; +256 $] | −0 $ | +0 $ | −250 $ | −50 $ | 4 | 0/0 | +0 $ | +122 $ | −361 $ | +250 $ | 354/350 |
| H02 verrouillage partiel 25 % | 7 | 4 | 4 | 100,0 % | 0,86 | 22,6 % | −250 $ | **+0 $** [−0 $ ; +0 $] | −0 $ | +0 $ | −250 $ | −46 $ | 7 | 0/0 | +0 $ | +5 $ | −128 $ | +250 $ | 371/370 |
| H03 verrouillage partiel 50 % | 39 | 27 | 19 | 70,4 % | 0,73 | 35,6 % | −250 $ | **+0 $** [−324 $ ; +309 $] | −0 $ | +0 $ | −300 $ | −50 $ | 7 | 0/0 | +0 $ | +63 $ | −114 $ | +250 $ | 339/329 |
| H04 plancher de profit (les 2 issues ≥ 0) | 136 | 95 | 93 | 97,9 % | 0,72 | 76,0 % | −250 $ | **+0 $** [−871 $ ; +1 013 $] | −0 $ | +0 $ | −758 $ | −50 $ | 4 | 0/0 | +0 $ | +638 $ | −1 558 $ | +355 $ | 208/206 |
| H05 réserve jackpot (≥ 70 % gardé) | 9 | 6 | 4 | 66,7 % | 0,85 | 26,7 % | −250 $ | **−0 $** [+0 $ ; +0 $] | −0 $ | +0 $ | −250 $ | −50 $ | 7 | 0/0 | +0 $ | +6 $ | −135 $ | +250 $ | 370/368 |
| H06 échelle de paires (4 tranches) | 22 | 14 | 13 | 92,9 % | 0,67 | 63,8 % | −250 $ | **−0 $** [−278 $ ; +278 $] | −0 $ | +0 $ | −250 $ | −50 $ | 5 | 0/0 | +0 $ | +141 $ | −355 $ | +250 $ | 354/350 |
| H07 pire perte limitée à −25 $ | 7 | 6 | 5 | 83,3 % | 0,94 | 44,3 % | −250 $ | **+0 $** [+0 $ ; +0 $] | −0 $ | −0 $ | −250 $ | −46 $ | 7 | 0/0 | +0 $ | −62 $ | −54 $ | +250 $ | 371/370 |
| H08 pire perte limitée à −10 $ | 22 | 17 | 16 | 94,1 % | 0,88 | 50,9 % | −250 $ | **+0 $** [−259 $ ; +224 $] | −0 $ | +0 $ | −250 $ | −46 $ | 7 | 0/0 | +0 $ | −121 $ | +166 $ | +250 $ | 355/350 |
| H09 pire issue à 0 dans le budget (après modèle −10) | 7 | 4 | 0 | 0,0 % | — | — | −250 $ | **+0 $** [+0 $ ; +0 $] | +0 $ | −0 $ | −250 $ | −50 $ | 7 | 0/0 | +0 $ | +0 $ | −250 $ | +50 $ | 371/370 |
| H10 couvrir ou vendre (avantage net) | 138 | 65 | 64 | 98,5 % | — | 99,0 % | −250 $ | **+0 $** [−1 358 $ ; +1 449 $] | +0 $ | +0 $ | −712 $ | −50 $ | 18 | 0/0 | +0 $ | +0 $ | +1 314 $ | +50 $ | 207/200 |
| H11 alerte précoce (2 signaux sur 3) 25 % | 7 | 7 | 6 | 85,7 % | 0,94 | 19,1 % | −250 $ | **−0 $** [−0 $ ; +0 $] | −1 $ | −0 $ | −250 $ | −48 $ | 7 | 0/0 | +0 $ | −21 $ | −28 $ | +250 $ | 371/370 |
| H12 horloge de risque (immédiat / attendre 3 s) | 7 | 4 | 3 | 75,0 % | 0,89 | 64,3 % | −250 $ | **+0 $** [+0 $ ; +0 $] | +0 $ | −0 $ | −250 $ | −50 $ | 7 | 0/0 | +0 $ | −50 $ | −148 $ | +187 $ | 371/370 |
| H13 prédictive 1 s | 7 | 4 | 3 | 75,0 % | 0,89 | 64,3 % | −250 $ | **+0 $** [+0 $ ; +0 $] | +0 $ | −0 $ | −250 $ | −50 $ | 7 | 0/0 | +0 $ | −50 $ | −148 $ | +187 $ | 371/370 |
| H14 prédictive 3 s | 7 | 4 | 3 | 75,0 % | 0,89 | 64,3 % | −250 $ | **+0 $** [+0 $ ; +0 $] | +0 $ | −0 $ | −250 $ | −50 $ | 7 | 0/0 | +0 $ | −50 $ | −148 $ | +187 $ | 371/370 |
| H15 prédictive 5 s | 7 | 4 | 3 | 75,0 % | 0,89 | 63,7 % | −250 $ | **+0 $** [+0 $ ; +0 $] | +0 $ | −0 $ | −250 $ | −50 $ | 7 | 0/0 | +0 $ | −51 $ | −147 $ | +187 $ | 371/370 |
| H16 prédictive 10 s | 7 | 4 | 3 | 75,0 % | 0,89 | 64,3 % | −250 $ | **+0 $** [+0 $ ; +0 $] | +0 $ | −0 $ | −250 $ | −50 $ | 7 | 0/0 | +0 $ | −50 $ | −148 $ | +187 $ | 371/370 |
| H17 premier passage (limite si EV > immédiat) | 7 | 4 | 3 | 75,0 % | 0,89 | 64,3 % | −250 $ | **+0 $** [+0 $ ; +0 $] | +0 $ | −0 $ | −250 $ | −50 $ | 7 | 0/0 | +0 $ | −50 $ | −148 $ | +187 $ | 371/370 |
| H18 fenêtre de conversion prédite (paire ≤ 0,95) — inactive si seuil appris = jamais | 7 | 0 | 0 | — | — | — | −250 $ | **+0 $** [+0 $ ; +0 $] | +0 $ | +0 $ | −250 $ | −50 $ | 7 | 0/0 | +0 $ | +0 $ | −250 $ | +50 $ | 371/370 |
| H19 sauvetage passif (vendeur − 1 c, 10 s) | 7 | 4 | 1 | 25,0 % | 0,97 | 2,6 % | −250 $ | **+0 $** [+0 $ ; +0 $] | +0 $ | −0 $ | −250 $ | −50 $ | 7 | 0/0 | +0 $ | −1 $ | −200 $ | +55 $ | 371/370 |
| H20 prédicteur de file (traversée) passif sinon immédiat | 7 | 4 | 3 | 75,0 % | 0,89 | 63,7 % | −250 $ | **+0 $** [+0 $ ; +0 $] | +0 $ | −0 $ | −250 $ | −50 $ | 7 | 0/0 | +0 $ | −51 $ | −147 $ | +187 $ | 371/370 |
| H21 recharge du carnet | 7 | 4 | 3 | 75,0 % | 0,89 | 63,7 % | −250 $ | **+0 $** [+0 $ ; +0 $] | +0 $ | −0 $ | −250 $ | −50 $ | 7 | 0/0 | +0 $ | −51 $ | −147 $ | +187 $ | 371/370 |
| H22 hybride 50 % immédiat + 50 % passif | 7 | 4 | 3 | 75,0 % | 0,89 | 64,0 % | −250 $ | **+0 $** [+0 $ ; +0 $] | +0 $ | −0 $ | −250 $ | −50 $ | 7 | 0/0 | +0 $ | −50 $ | −147 $ | +187 $ | 371/370 |
| H23 boomerang (revente de l'opposé +5 c) | 7 | 4 | 4 | 100,0 % | 0,80 | 58,3 % | −250 $ | **+0 $** [−0 $ ; +0 $] | −0 $ | +0 $ | −250 $ | −49 $ | 7 | 0/0 | +0 $ | +1 $ | −105 $ | +250 $ | 371/370 |
| H24 moteur d'inventaire deux jambes | 7 | 5 | 4 | 80,0 % | 0,68 | 26,9 % | −250 $ | **+0 $** [+0 $ ; +0 $] | −1 $ | +0 $ | −250 $ | −50 $ | 7 | 0/0 | +0 $ | +9 $ | −129 $ | +100 $ | 371/370 |

### C · V2-F original (diagnostic) — prudent — inédit

| Couverture | Positions | Tentées | Exécutées | Taux d'exécution | Prix moyen opposé | Quantité couverte moy. | P&L net | Δ vs GARDER [IC 90 %] | Δ vs VENDRE 50 % | Δ vs VENDRE 100 % | Creux max | Perte max (1 position) | Plus longue série perdante | Jackpots gardés | Profit sacrifié (jackpots) | Profit verrouillé (paires) | P&L des positions non couvertes | Capital immobilisé max | Entrées réduites / refusées |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| GARDER (référence) | 13 | — | — | — | — | — | −250 $ | 0 | — | — | −352 $ | −50 $ | 8 | 0/0 | 0 $ | 0 $ | −250 $ | +50 $ | 245/243 |
| H01 verrouillage paire complète (coût < 1) | 17 | 9 | 7 | 77,8 % | 0,74 | 77,0 % | −250 $ | **+0 $** [−53 $ ; +53 $] | +0 $ | +0 $ | −250 $ | −50 $ | 6 | 0/0 | +0 $ | +24 $ | −336 $ | +234 $ | 242/238 |
| H02 verrouillage partiel 25 % | 14 | 7 | 6 | 85,7 % | 0,73 | 25,0 % | −250 $ | **+0 $** [−15 $ ; +15 $] | +0 $ | +0 $ | −324 $ | −50 $ | 8 | 0/0 | +0 $ | +8 $ | −174 $ | +91 $ | 244/242 |
| H03 verrouillage partiel 50 % | 15 | 7 | 7 | 100,0 % | 0,73 | 43,0 % | −250 $ | **−0 $** [−28 $ ; +28 $] | −0 $ | +0 $ | −296 $ | −50 $ | 8 | 0/0 | +0 $ | +16 $ | −321 $ | +132 $ | 243/241 |
| H04 plancher de profit (les 2 issues ≥ 0) | 17 | 9 | 7 | 77,8 % | 0,74 | 71,1 % | −250 $ | **+0 $** [−32 $ ; +32 $] | +0 $ | +0 $ | −250 $ | −50 $ | 6 | 0/0 | +0 $ | +22 $ | −336 $ | +219 $ | 242/238 |
| H05 réserve jackpot (≥ 70 % gardé) | 15 | 7 | 6 | 85,7 % | 0,73 | 30,8 % | −250 $ | **+0 $** [−19 $ ; +19 $] | +0 $ | +0 $ | −318 $ | −50 $ | 8 | 0/0 | +0 $ | +10 $ | −183 $ | +102 $ | 243/241 |
| H06 échelle de paires (4 tranches) | 17 | 9 | 7 | 77,8 % | 0,68 | 75,4 % | −250 $ | **+0 $** [−81 $ ; +81 $] | +0 $ | +0 $ | −262 $ | −50 $ | 4 | 0/0 | +0 $ | +78 $ | −368 $ | +188 $ | 241/238 |
| H07 pire perte limitée à −25 $ | 18 | 12 | 11 | 91,7 % | 0,89 | 77,5 % | −250 $ | **+0 $** [−169 $ ; +165 $] | −0 $ | +0 $ | −352 $ | −48 $ | 8 | 0/0 | +0 $ | −261 $ | +135 $ | +243 $ | 238/235 |
| H08 pire perte limitée à −10 $ | 19 | 16 | 15 | 93,8 % | 0,84 | 84,5 % | −250 $ | **−0 $** [−249 $ ; +226 $] | −1 $ | −1 $ | −353 $ | −42 $ | 17 | 0/0 | +0 $ | −190 $ | +56 $ | +250 $ | 235/234 |
| H09 pire issue à 0 dans le budget (après modèle −10) | 17 | 7 | 2 | 28,6 % | 0,73 | 88,9 % | −250 $ | **+0 $** [−100 $ ; +100 $] | +0 $ | +0 $ | −352 $ | −50 $ | 6 | 0/0 | +0 $ | +11 $ | −250 $ | +211 $ | 241/238 |
| H10 couvrir ou vendre (avantage net) | 17 | 7 | 7 | 100,0 % | — | 100,0 % | −250 $ | **+0 $** [−66 $ ; +66 $] | +0 $ | +0 $ | −356 $ | −50 $ | 8 | 0/0 | +0 $ | +0 $ | −62 $ | +50 $ | 241/238 |
| H11 alerte précoce (2 signaux sur 3) 25 % | 15 | 12 | 11 | 91,7 % | 0,86 | 24,2 % | −250 $ | **+0 $** [−30 $ ; +30 $] | −1 $ | −1 $ | −354 $ | −50 $ | 8 | 0/0 | +0 $ | −48 $ | +137 $ | +98 $ | 242/241 |
| H12 horloge de risque (immédiat / attendre 3 s) | 15 | 7 | 7 | 100,0 % | 0,90 | 68,8 % | −250 $ | **+0 $** [−66 $ ; +66 $] | +0 $ | +0 $ | −356 $ | −50 $ | 8 | 0/0 | +0 $ | −103 $ | −38 $ | +239 $ | 242/241 |
| H13 prédictive 1 s | 15 | 7 | 7 | 100,0 % | 0,90 | 68,9 % | −250 $ | **+0 $** [−66 $ ; +66 $] | +0 $ | +0 $ | −356 $ | −50 $ | 8 | 0/0 | +0 $ | −103 $ | −38 $ | +239 $ | 242/241 |
| H14 prédictive 3 s | 15 | 7 | 7 | 100,0 % | 0,90 | 69,4 % | −250 $ | **+0 $** [−70 $ ; +70 $] | +0 $ | +0 $ | −356 $ | −50 $ | 8 | 0/0 | +0 $ | −103 $ | −40 $ | +237 $ | 242/241 |
| H15 prédictive 5 s | 15 | 7 | 7 | 100,0 % | 0,90 | 68,5 % | −250 $ | **−0 $** [−66 $ ; +66 $] | +0 $ | +0 $ | −356 $ | −50 $ | 8 | 0/0 | +0 $ | −103 $ | −37 $ | +239 $ | 242/241 |
| H16 prédictive 10 s | 15 | 7 | 7 | 100,0 % | 0,91 | 66,8 % | −250 $ | **+0 $** [−66 $ ; +66 $] | +0 $ | +0 $ | −356 $ | −50 $ | 8 | 0/0 | +0 $ | −103 $ | −30 $ | +239 $ | 242/241 |
| H17 premier passage (limite si EV > immédiat) | 15 | 7 | 7 | 100,0 % | 0,90 | 68,9 % | −250 $ | **+0 $** [−66 $ ; +66 $] | +0 $ | +0 $ | −356 $ | −50 $ | 8 | 0/0 | +0 $ | −103 $ | −38 $ | +239 $ | 242/241 |
| H18 fenêtre de conversion prédite (paire ≤ 0,95) — inactive si seuil appris = jamais | 13 | 0 | 0 | — | — | — | −250 $ | **+0 $** [+0 $ ; +0 $] | +0 $ | +0 $ | −352 $ | −50 $ | 8 | 0/0 | +0 $ | +0 $ | −250 $ | +50 $ | 245/243 |
| H19 sauvetage passif (vendeur − 1 c, 10 s) | 14 | 7 | 3 | 42,9 % | 0,91 | 45,9 % | −250 $ | **−0 $** [−8 $ ; +8 $] | +0 $ | +0 $ | −356 $ | −50 $ | 8 | 0/0 | +0 $ | −20 $ | −149 $ | +105 $ | 244/242 |
| H20 prédicteur de file (traversée) passif sinon immédiat | 15 | 7 | 7 | 100,0 % | 0,91 | 67,1 % | −250 $ | **−0 $** [−67 $ ; +67 $] | +0 $ | −0 $ | −356 $ | −50 $ | 8 | 0/0 | +0 $ | −103 $ | −32 $ | +239 $ | 242/241 |
| H21 recharge du carnet | 15 | 7 | 7 | 100,0 % | 0,90 | 68,7 % | −250 $ | **+0 $** [−66 $ ; +66 $] | +0 $ | +0 $ | −356 $ | −50 $ | 8 | 0/0 | +0 $ | −103 $ | −37 $ | +239 $ | 242/241 |
| H22 hybride 50 % immédiat + 50 % passif | 15 | 7 | 7 | 100,0 % | 0,90 | 68,4 % | −250 $ | **+0 $** [−66 $ ; +66 $] | +0 $ | +0 $ | −356 $ | −50 $ | 8 | 0/0 | +0 $ | −103 $ | −37 $ | +239 $ | 242/241 |
| H23 boomerang (revente de l'opposé +5 c) | 9 | 4 | 4 | 100,0 % | 0,75 | 99,4 % | −250 $ | **+0 $** [−159 $ ; +159 $] | +0 $ | +0 $ | −250 $ | −50 $ | 7 | 0/0 | +0 $ | +2 $ | −159 $ | +234 $ | 249/248 |
| H24 moteur d'inventaire deux jambes | 10 | 10 | 9 | 90,0 % | 0,68 | 15,0 % | −250 $ | **−0 $** [−36 $ ; +36 $] | −0 $ | −1 $ | −304 $ | −67 $ | 8 | 0/0 | +0 $ | +21 $ | −4 $ | +100 $ | 248/246 |

### Exposition après couverture (prudent, validation) — moyennes par position

| Couverture | A pire issue moy. | A gain max restant moy. | A exposition nette finale (× entrée) | A positions avec paires | B pire issue moy. | B gain max restant moy. | B exposition nette | B positions avec paires |
|---|---|---|---|---|---|---|---|---|
| GARDER | −32 $ | +127 $ | 1,00 | 0 | −37 $ | +112 $ | 1,00 | 0 |
| H01 | −13 $ | +106 $ | 0,57 | 20 | −7 $ | +69 $ | 0,32 | 43 |
| H02 | −25 $ | +117 $ | 0,87 | 19 | −30 $ | +100 $ | 0,85 | 84 |
| H03 | −21 $ | +115 $ | 0,77 | 19 | −22 $ | +89 $ | 0,67 | 45 |
| H04 | −17 $ | +89 $ | 0,69 | 15 | −13 $ | +72 $ | 0,42 | 43 |
| H05 | −23 $ | +114 $ | 0,80 | 19 | −26 $ | +96 $ | 0,78 | 87 |
| H06 | −14 $ | +112 $ | 0,61 | 20 | −7 $ | +79 $ | 0,36 | 43 |
| H07 | −28 $ | +80 $ | 0,79 | 5 | −28 $ | +41 $ | 0,54 | 75 |
| H08 | −29 $ | +74 $ | 0,57 | 12 | −20 $ | +39 $ | 0,34 | 47 |
| H09 | −34 $ | +145 $ | 0,94 | 2 | −27 $ | +99 $ | 0,80 | 36 |
| H10 | −29 $ | +68 $ | 0,71 | 0 | −22 $ | +27 $ | 0,32 | 0 |
| H11 | −34 $ | +118 $ | 0,85 | 12 | −30 $ | +90 $ | 0,80 | 113 |
| H12 | −30 $ | +101 $ | 0,91 | 2 | −24 $ | +53 $ | 0,47 | 22 |
| H13 | −29 $ | +101 $ | 0,90 | 2 | −24 $ | +55 $ | 0,49 | 22 |
| H14 | −30 $ | +101 $ | 0,91 | 2 | −24 $ | +45 $ | 0,40 | 77 |
| H15 | −29 $ | +101 $ | 0,90 | 2 | −24 $ | +55 $ | 0,49 | 22 |
| H16 | −29 $ | +101 $ | 0,90 | 2 | −24 $ | +55 $ | 0,49 | 22 |
| H17 | −29 $ | +101 $ | 0,90 | 2 | −24 $ | +55 $ | 0,49 | 22 |
| H18 | −32 $ | +127 $ | 1,00 | 0 | −37 $ | +112 $ | 1,00 | 0 |
| H19 | −30 $ | +100 $ | 0,91 | 1 | −31 $ | +95 $ | 0,81 | 24 |
| H20 | −29 $ | +101 $ | 0,90 | 2 | −24 $ | +38 $ | 0,37 | 77 |
| H21 | −29 $ | +101 $ | 0,90 | 2 | −26 $ | +70 $ | 0,49 | 12 |
| H22 | −29 $ | +101 $ | 0,90 | 2 | −24 $ | +43 $ | 0,40 | 77 |
| H23 | −28 $ | +143 $ | 0,82 | 3 | −29 $ | +108 $ | 0,89 | 19 |
| H24 | −31 $ | +192 $ | 1,22 | 19 | −33 $ | +136 $ | 1,07 | 84 |

### Apprentissage (pour mémoire, prudent, Δ vs GARDER)

| Couverture | A | B | C |
|---|---|---|---|
| H01 verrouillage paire complète (coût < 1) | −767 $ | −710 $ | −486 $ |
| H02 verrouillage partiel 25 % | −191 $ | −710 $ | −486 $ |
| H03 verrouillage partiel 50 % | −382 $ | −710 $ | −486 $ |
| H04 plancher de profit (les 2 issues ≥ 0) | −634 $ | −710 $ | −486 $ |
| H05 réserve jackpot (≥ 70 % gardé) | −236 $ | −710 $ | −486 $ |
| H06 échelle de paires (4 tranches) | −704 $ | −710 $ | −486 $ |
| H07 pire perte limitée à −25 $ | −507 $ | −710 $ | −486 $ |
| H08 pire perte limitée à −10 $ | −574 $ | −710 $ | −486 $ |
| H09 pire issue à 0 dans le budget (après modèle −10) | −284 $ | −710 $ | −486 $ |
| H10 couvrir ou vendre (avantage net) | −323 $ | −709 $ | −486 $ |
| H11 alerte précoce (2 signaux sur 3) 25 % | −128 $ | −195 $ | −486 $ |
| H12 horloge de risque (immédiat / attendre 3 s) | −323 $ | −710 $ | −486 $ |
| H13 prédictive 1 s | −323 $ | −710 $ | −486 $ |
| H14 prédictive 3 s | −323 $ | −710 $ | −486 $ |
| H15 prédictive 5 s | −323 $ | −710 $ | −275 $ |
| H16 prédictive 10 s | −323 $ | −710 $ | −486 $ |
| H17 premier passage (limite si EV > immédiat) | −323 $ | −710 $ | −486 $ |
| H18 fenêtre de conversion prédite (paire ≤ 0,95) — inactive si seuil appris = jamais | +0 $ | +0 $ | −0 $ |
| H19 sauvetage passif (vendeur − 1 c, 10 s) | +0 $ | −710 $ | −114 $ |
| H20 prédicteur de file (traversée) passif sinon immédiat | −323 $ | −710 $ | −486 $ |
| H21 recharge du carnet | −324 $ | −710 $ | −245 $ |
| H22 hybride 50 % immédiat + 50 % passif | −325 $ | −710 $ | −486 $ |
| H23 boomerang (revente de l'opposé +5 c) | −727 $ | −710 $ | −486 $ |
| H24 moteur d'inventaire deux jambes | +43 $ | −710 $ | −486 $ |

## 6. Stabilité par jour (prudent, Δ vs GARDER, validation + test, portefeuille 250 $ par période)

### A · désaccord 30 zone + modèle monte

| Couverture | 08.10 | 09.10 | 10.10 | 11.10 | jours positifs |
|---|---|---|---|---|---|
| H01 | +0 $ | +95 $ | −155 $ | +167 $ | 2/4 |
| H06 | +0 $ | +75 $ | +34 $ | −2 $ | 2/4 |
| H24 | −4 $ | +133 $ | −67 $ | +7 $ | 2/4 |
| H14 | +0 $ | +1 $ | −40 $ | +40 $ | 2/4 |
| H12 | +0 $ | +1 $ | −40 $ | +40 $ | 2/4 |
| H13 | +0 $ | +1 $ | −40 $ | +40 $ | 2/4 |
| H16 | +0 $ | +1 $ | −40 $ | +40 $ | 2/4 |
| H17 | +0 $ | +1 $ | −40 $ | +40 $ | 2/4 |
| H21 | +0 $ | +1 $ | −41 $ | +42 $ | 2/4 |
| H22 | +0 $ | +1 $ | −39 $ | +39 $ | 2/4 |
| H15 | +0 $ | +0 $ | −40 $ | +40 $ | 1/4 |
| H20 | +0 $ | +0 $ | −40 $ | +40 $ | 1/4 |
| H04 | +0 $ | +10 $ | −264 $ | +254 $ | 2/4 |
| H07 | +0 $ | +0 $ | −254 $ | +254 $ | 1/4 |
| H08 | +4 $ | −4 $ | +133 $ | +25 $ | 3/4 |
| H10 | +0 $ | +0 $ | −38 $ | +38 $ | 1/4 |
| H11 | +0 $ | +0 $ | −3 $ | +3 $ | 1/4 |
| H03 | +0 $ | +36 $ | −74 $ | +37 $ | 2/4 |
| H19 | +0 $ | −0 $ | −40 $ | +40 $ | 1/4 |
| H23 | +0 $ | −0 $ | +41 $ | −41 $ | 1/4 |
| H05 | +0 $ | +25 $ | −61 $ | +36 $ | 2/4 |
| H09 | +0 $ | +0 $ | −5 $ | +5 $ | 1/4 |
| H02 | +0 $ | +24 $ | −60 $ | +36 $ | 2/4 |
| H18 | +0 $ | −0 $ | +0 $ | +0 $ | 0/4 |

### B · V2-F corrigé 0,015 %

| Couverture | 08.10 | 09.10 | 10.10 | 11.10 | jours positifs |
|---|---|---|---|---|---|
| H23 | −4 $ | +25 $ | −21 $ | +0 $ | 1/4 |
| H19 | +0 $ | −163 $ | +163 $ | +0 $ | 1/4 |
| H08 | +109 $ | −770 $ | +661 $ | +0 $ | 2/4 |
| H18 | +0 $ | −0 $ | +0 $ | +0 $ | 0/4 |
| H09 | +25 $ | −244 $ | +219 $ | +0 $ | 2/4 |
| H07 | +56 $ | −136 $ | +80 $ | +0 $ | 2/4 |
| H11 | −6 $ | −107 $ | +113 $ | +0 $ | 1/4 |
| H20 | +13 $ | −264 $ | +251 $ | +0 $ | 2/4 |
| H02 | −13 $ | −121 $ | +134 $ | +0 $ | 1/4 |
| H24 | −41 $ | −135 $ | +176 $ | +0 $ | 1/4 |
| H03 | −26 $ | −635 $ | +661 $ | +0 $ | 1/4 |
| H15 | +14 $ | −676 $ | +661 $ | +0 $ | 2/4 |
| H13 | +24 $ | −685 $ | +661 $ | +0 $ | 2/4 |
| H16 | +14 $ | −675 $ | +661 $ | +0 $ | 2/4 |
| H17 | +24 $ | −685 $ | +661 $ | +0 $ | 2/4 |
| H21 | +24 $ | −685 $ | +661 $ | +0 $ | 2/4 |
| H22 | +10 $ | −269 $ | +259 $ | +0 $ | 2/4 |
| H12 | +24 $ | −685 $ | +661 $ | +0 $ | 2/4 |
| H01 | −53 $ | −608 $ | +661 $ | +0 $ | 1/4 |
| H04 | −50 $ | −611 $ | +661 $ | +0 $ | 1/4 |
| H05 | −17 $ | −159 $ | +176 $ | +0 $ | 1/4 |
| H06 | −32 $ | −629 $ | +661 $ | +0 $ | 1/4 |
| H10 | +24 $ | −468 $ | +444 $ | +0 $ | 2/4 |
| H14 | +26 $ | −282 $ | +256 $ | +0 $ | 2/4 |

## 7. Non testable ou testable seulement en partie

- **H20 prédicteur de file (traversée) passif sinon immédiat** — partiellement : la vraie position dans la file n'est pas observable (aucun événement d'ordre individuel) ; testé seulement comme prédicteur de « traversée » du prix.
- **H21 recharge du carnet** — partiellement : recharge mesurée sur les lignes 0,3 s (meilleur niveau) ; à 100 ms seulement dans les photos (~20 s par cycle).
- **Fusion anticipée** (capital libéré avant le règlement) — non observable : seulement dans le scénario idéal.
- **Remplissage passif réel** — non observable (file d'attente) : toutes les couvertures passives (H17-H20, H22) sont des bornes selon le scénario, pas des mesures.
- **Latence réelle Dublin** — pas encore de données (rapide.json vide).
Aucune couverture n'a été déclarée « non testable » en entier : toutes ont des résultats, avec les réserves ci-dessus.

Durée de calcul : 110 s.