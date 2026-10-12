# Bot95 — H986 à H993 (première priorité) : flux forcés, liquidations, base perp/spot — rapport du 12.10.2026

**Cadre**
- Étude hors ligne uniquement. Aucun ordre réel, aucun abonnement acheté.
- Aucune stratégie, aucun fantôme modifié ; H816, H821 et R4 sont inchangés. La période réservée n'a pas été lue.
- Protocole enregistré sur GitHub **avant tout calcul** (commit cd833a5).

**Données et échantillons**
- Laboratoire de Dublin, du 11.10 au 12.10 à 14:05 UTC (350 cycles).
- Liquidations Bybit BTCUSDT enregistrées depuis le 11.10, avec les heures de réception.
- Découpage :
  - apprentissage ;
  - validation ;
  - test : 12.10, 06:00–12:00 UTC ;
  - nouveau : 12.10 à partir de 12:00 UTC.

## 0. Nouveaux enregistrements à Dublin (ton accord de 15:25)

Ils sont actifs depuis 14:06 UTC, vérifiés sur le premier cycle complet :

| Ajout | Contenu vérifié |
|---|---|
| Open interest des options BTC Deribit par prix d'exercice | une photo par minute, 178 options (échéance < 8 jours, à moins de 10 % du prix) |
| Transactions d'options Deribit en direct | avec heure de réception |
| Carnet Coinbase BTC/USD (level2) | toutes les 100 ms et photo à 10 niveaux chaque seconde |
| ETH et SOL | carnet Binance toutes les 100 ms ; transactions Binance spot et Bybit perp |

**Petit défaut connu.** L'enregistreur signale à tort des « trous de séquence » Coinbase : le numéro de séquence Coinbase est commun à tous les canaux. Ces alertes sont à ignorer ; je le corrigerai au prochain déploiement.

**Incident réparé.** Mon déploiement de 13:27 avait échoué (Cloudflare indisponible), puis le déploiement de Replit de 11:33 avait laissé une migration inconnue de GitHub. J'ai repris cette migration dans GitHub, sans effacer de données. **GitHub est de nouveau la seule source du Worker** (déploiement réussi à 14:03 UTC).

## 1. Audit des données pour cette série

| Donnée | Disponible ? |
|---|---|
| Liquidations Bybit (agrégées, environ 500 ms) | oui, depuis le 11.10 : 3,0 M$ de ventes forcées, 5,8 M$ d'achats forcés |
| Mark price, index price, open interest, funding Bybit à haute fréquence | **non** : à enregistrer, gratuit |
| Mark price, liquidations, transactions Binance perp | **non** : à enregistrer, gratuit |
| Open interest Binance | toutes les 5 min seulement, trop grossier |
| Open interest Deribit par prix d'exercice, Coinbase L2, ETH/SOL | depuis 14:06 UTC seulement |
| Options IBIT (OPRA), CME, ETF | **non**, payant, non acheté |

## 2. H993 — Flux forcé contre flux volontaire

**Définitions**
- Une vague = forte pression agressive (même définition que H941).
- Elle est « contrainte » si au moins 10 000 $ de liquidations Bybit **du même sens** ont eu lieu dans les 5 s précédentes.

| Échantillon | Vagues contraintes | Continuation à 30 s | Continuation à 120 s | Vagues volontaires : 30 s / 120 s |
|---|---|---|---|---|
| Apprentissage | 13 | **+21,5 $** [+5,4 ; +38,3] | **+46,5 $** [+10,0 ; +73,6] | +5,1 / +5,8 $ |
| Validation | 1 | — | — | +7,1 / +5,2 $ |
| Test | 4 | — | — | +4,5 / +6,1 $ |
| Nouveau | 7 | +38,8 $ | **+76,7 $** [+47,6 ; +105,9] | +7,2 / +2,2 $ |

Sur l'apprentissage, après appariement (même intensité, même volatilité, même temps restant ; 6 paires), l'écart est de **+53 $ à 120 s** [+21 ; +77].

**Lecture**
- Les vagues accompagnées de liquidations **continuent beaucoup plus longtemps** : 20 à 75 $ sur 30 à 120 s, contre environ 5 $ pour un flux ordinaire. C'est cohérent avec l'hypothèse des flux contraints.
- **Mais elles sont rares** : 25 en 29 h, dont seulement 1 sur la validation et 4 sur le test. **Rien ne peut être démontré hors échantillon** pour l'instant.

**H992 — Prix Polymarket réellement payable** (achat de 20 $ dans le sens de la vague contrainte, à 164 ms)

| Échantillon | Achats | Victoire | Prix payé moyen | P&L |
|---|---|---|---|---|
| Apprentissage | 9 | 100 % | **0,90** | +21 $ [+10 ; +32] |
| Validation, test | 0 | — | — | — |
| Nouveau | 2 | 100 % | 0,92 | +4 $ |

Polymarket a **déjà en grande partie intégré** le mouvement : on paie 0,90 pour un billet qui rapporte 1. Le gain par achat est d'environ 2 $ pour 20 $ misés, sur très peu de cas.

## 3. H990 — Une salve de liquidations en déclenche-t-elle une autre ?

Une salve = au moins 50 000 $ de liquidations du même côté en 5 s. **36 salves en 29 h.**

| Échantillon | Salves | Nouvelle salve dans 1 / 5 / 30 s | Témoins (même mouvement de prix, sans salve) |
|---|---|---|---|
| Apprentissage | 16 | 25 / 31 / 50 % | 0 / 9 / 9 % |
| Validation | 4 | 0 / 50 / 50 % | 0 / 0 / 0 % |
| Test | 6 | 17 / 17 / 17 % | 0 / 7 / 7 % |
| Nouveau | 10 | 10 / 20 / 20 % | 0 / 0 / 8 % |

**Les liquidations arrivent en grappes** : après une salve, la probabilité d'une nouvelle salve est 2 à 5 fois plus élevée qu'après un mouvement de prix comparable. L'effet est cohérent sur les 4 échantillons, mais les effectifs sont très faibles. Le sens du prix après la salve n'est pas stable (positif sur l'apprentissage et le nouveau, négatif sur le test).

## 4. H988 (partiel) — Une base perp/spot extrême annonce-t-elle des liquidations ?

Sans mark price ni index price, seul l'écart perp Bybit − spot Binance est testable. Une base extrême (|z| ≥ 2) **n'augmente pas** la fréquence des salves dans les 30 s suivantes : 0,9 % contre 0,9 % sur le test. **Rien à ce stade** : il faut le vrai mark price.

## 5. Non testables aujourd'hui

| Expérience | Raison |
|---|---|
| H986 options IBIT | données OPRA payantes, non achetées |
| H991 IBIT / CME / Deribit | idem pour IBIT et CME |
| H987 régimes gamma | open interest par prix d'exercice enregistré seulement depuis 14:06 UTC ; il faut plusieurs jours, dont des expirations |
| H988 complet, H989 | mark price, index price et open interest Bybit/Binance à haute fréquence non enregistrés |

## 6. Verdict et recommandation

| Piste | Verdict |
|---|---|
| H993 Flux forcé (liquidations) | **Le plus prometteur de la journée** : continuation de 20 à 75 $ sur 30 à 120 s, cohérente avec l'horizon d'un marché de 5 minutes. **Non démontré** : trop peu d'événements, et Polymarket paie déjà environ 0,90. |
| H990 Cascades | Grappes réelles mais rares : **à approfondir** |
| H988 Base perp/spot | rien sans mark price : **à refaire** avec les données ci-dessous |
| H986, H987, H989, H991 | non testables aujourd'hui |

**Pour décider de H993, H988 et H989, il faut plus d'événements et les bons champs.** Je propose, avec ton accord, d'ajouter à l'enregistreur de Dublin, en lecture seule et gratuitement :
1. le **ticker Bybit BTCUSDT** : mark price, index price, open interest, funding, environ toutes les 100 ms ;
2. **Binance perp BTCUSDT** : mark price chaque seconde, liquidations (flux forceOrder) et transactions agressives.

Puis laisser tourner plusieurs jours avant de rejuger H993, H990 et H988/H989 sur des données nouvelles, avec protocole figé.

**IBIT et CME** : je ne recommande aucun achat tant que les pistes gratuites ne montrent pas d'avantage exécutable face au prix Polymarket.

Fichiers :
- https://github.com/pitch6767/wallet-autopsy/blob/main/etude/bot5min/resultat_liq_h993.md
- https://github.com/pitch6767/wallet-autopsy/blob/main/etude/bot5min/liq_h993.py
