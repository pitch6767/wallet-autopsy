# BOT95 V3 — audit des données (hors ligne)

928 cycles BTC 5 min réglés (07.10 08:00 → 10.10 13:45, heure suisse). Apprentissage 455 cycles (< 08.10 22:00) · validation 433 (→ 10.10 10:25) · test inédit 40 cycles seulement (après 10.10 10:25) — le test est minuscule, aucun verdict ne peut s'y appuyer seul.

## 1. Lignes enregistrées `bot95/donnees/<jour>/rec_BTC.json.gz`

| Jour (fichier) | Lignes | Première ligne | Dernière ligne | Intervalle médian | Trous > 5 s (nombre · durée totale) |
|---|---|---|---|---|---|
| 2026-10-07 | 190463 | 07.10 08:01:47 | 08.10 01:59:59 | 0.30 s | 272 · 127 min |
| 2026-10-08 | 251766 | 08.10 02:00:00 | 09.10 01:59:59 | 0.30 s | 344 · 183 min |
| 2026-10-09 | 234530 | 09.10 02:00:00 | 10.10 01:59:59 | 0.30 s | 215 · 267 min |
| 2026-10-10 | 147915 | 10.10 02:00:03 | 10.10 14:35:59 | 0.30 s | 10 · 13 min |

Total après dédoublonnage : 824674 lignes, 07.10 08:01:47 → 10.10 14:35:59. Intervalle entre lignes : 5 % 0.30 s · médiane 0.30 s · 95 % 0.30 s · 99 % 0.31 s. **La résolution temporelle réelle des carnets est donc d'environ 0,3 s (pas 0,25 s)** : un délai demandé de 0,25 s devient 0,3 s, 0,5 s devient ~0,6 s, 1 s devient ~1,2 s.

| Colonne | Champ | Valeurs manquantes |
|---|---|---|
| r[0] | t | 0 (0.0 %) |
| r[1] | début du cycle | 0 (0.0 %) |
| r[2] | proba Up du modèle du bot (0,08 %) | 38892 (4.7 %) |
| r[3] | Up meilleur acheteur | 103867 (12.6 %) |
| r[4] | Up meilleur vendeur | 100373 (12.2 %) |
| r[5] | Down meilleur acheteur | 100373 (12.2 %) |
| r[6] | Down meilleur vendeur | 103867 (12.6 %) |
| r[7] | taille Up acheteur | 103867 (12.6 %) |
| r[8] | taille Up vendeur | 100373 (12.2 %) |
| r[9] | taille Down acheteur | 100373 (12.2 %) |
| r[10] | taille Down vendeur | 103867 (12.6 %) |
| r[11] | Bybit perp | 795 (0.1 %) |
| r[12] | OKX perp | 829 (0.1 %) |
| r[13] | Coinbase | 346 (0.0 %) |
| r[14] | Binance spot | 804 (0.1 %) |
| r[15] | Chainlink | 794 (0.1 %) |
| r[16] | prix d'exercice | 0 (0.0 %) |

Champs **absents** des lignes : profondeur au-delà du meilleur niveau Polymarket (seul le meilleur prix et sa taille), transactions Polymarket (qui a acheté, à quel prix), position dans la file d'attente, intérêt ouvert (open interest), horodatage des bourses à la source (seule l'heure de réception par le bot est connue).

Cycles présents dans les lignes : 939 ; avec résultat officiel et lignes complètes (modèle + 4 prix Polymarket) : 928.

Règlements officiels `officiels.json` : 933 cycles BTC, 07.10 08:00 → 10.10 13:45, sans trou. Les lignes vont jusqu'à 10.10 14:35:59 : les cycles après 10.10 13:45 n'ont pas encore de résultat officiel et sont exclus.

| Période | Cycles | De | À |
|---|---|---|---|
| apprentissage | 455 | 07.10 08:00 | 08.10 22:00 |
| validation | 433 | 08.10 22:00 | 10.10 10:25 |
| inédit | 40 | 10.10 10:25 | 10.10 13:45 |

## 2. Signaux rejoués des 7 stratégies principales (un par cycle au plus)

| Stratégie | app. | valid. | inédit | Définition |
|---|---|---|---|---|
| V2-F original (O8) | 339 | 380 | 40 | écart ≥ 0,20 (modèle du bot 0,08 %) qui a grandi de 3 c en 3 s, vendeur 0,03-0,97 |
| V2-F 0,01 % (H1) | 234 | 244 | 31 | même règle, modèle du bot ramené à 0,01 % (= fantôme réel « V2-F incertitude 0,01 % ») |
| V2-D perp 120-269 s | 215 | 287 | 38 | écart ≥ 0,20, 120-269 s restantes, perp Bybit dans notre sens sur 5 s |
| V2-G jury des bourses | 294 | 346 | 40 | écart ≥ 0,20, les 4 bourses dans notre sens sur 3 s, modèle monte plus vite que Polymarket (3 c) |
| désaccord 30 | 219 | 283 | 40 | premier écart ≥ 0,30 du cycle, vendeur 0,02-0,98 |
| désaccord 20 60-180 s | 310 | 365 | 38 | premier écart ≥ 0,20 entre 60 et 180 s restantes |
| désaccord 20 jeton 0,35-0,65 | 61 | 36 | 1 | premier écart ≥ 0,20 avec vendeur 0,35-0,65 |

## 3. Photos « qui a bougé en premier » `bot95/lead.json.gz`

- 1543 photos : 790 « avant » (10 s avant le premier désaccord ≥ 0,20 du cycle vu par le bot en direct) et 753 « après » (10 s après), 07.10 15:43:23 → 10.10 15:00:11.
- 748 cycles distincts ; 42 cycles ont deux photos « avant » (on garde la première) ; 17 cycles sans photo « après ».
- 732 cycles photographiés ont un résultat officiel (16 sans résultat : après 10.10 13:45).
- Échantillonnage : une ligne toutes les 100 ms (intervalle 0,09-0,11 s). **Mais les prix des bourses ne changent pas toutes les 100 ms** : intervalle médian entre deux changements = Bybit 0,4 s, OKX 0,4 s, Coinbase 0,5 s, Binance 0,4 s, Chainlink 0,9 s ; le carnet Polymarket change à chaque ligne. La résolution effective de l'ordre « qui bouge en premier » est donc de 100 ms au mieux, souvent 0,4-0,5 s pour les bourses.
- Les horodatages sont l'heure de RÉCEPTION par le bot (Cloudflare), pas l'heure de l'événement à la bourse : la latence réseau propre à chaque source est mélangée à l'avance réelle.
- Colonnes : 5 prix (Bybit perp, OKX perp, Coinbase, Binance spot, Chainlink), carnet Bybit (meilleurs prix, profondeurs 1/3/5/10 pb), flux perp, liquidations, 3 meilleurs niveaux acheteurs/vendeurs Up et Down Polymarket, flux Polymarket agrégés (retraits/ajouts/échanges, sans prix ni position en file).

  - apprentissage : 298 cycles photographiés
  - validation : 394 cycles photographiés
  - inédit : 56 cycles photographiés

## 4. Autres fichiers

- `twap_carnets.json` : 218 carnets à 8 niveaux aux signaux TWAP (10.10 01:33:43 → 10.10 14:08:30), aux délais 0 / 0,25 / 1 / 2 / 5 s. Stratégies TWAP seulement : hors du périmètre des 7 stratégies, non utilisé.
- `vitesse.json` : 12 signaux (10.10 14:17:23 → 10.10 14:22:22) avec carnets à 0,1 / 0,25 / 0,5 / 1 / 2 s : trop peu pour une mesure.
- Intérêt ouvert (open interest) Polymarket : **absent de toutes les données**.

## 5. Fantômes réels (`bot95/sauvegarde`) contre rejeu de l'étude — exécution théorique ou simulée ?

Le fantôme réel « achète » au meilleur vendeur vu par le bot en direct ; le rejeu achète au meilleur vendeur de la ligne enregistrée au même instant (délai 0). Comparaison sur les cycles réglés où les deux existent.

| Fantôme réel | Rejeu | Trades réels (cycles réglés) | Période couverte | Cycles communs | Même côté | Résultat réel (communs) | Résultat rejeu délai 0 (communs) | Rejeu délai 0,5 s demandé (~0,6 s réel) (communs) |
|---|---|---|---|---|---|---|---|---|
| V2-F ecart qui grandit BTC | V2-F original (O8) | 381 | 09.10 01:55 → 10.10 13:40 | 374 | 367 | −1 738 $ | −1 891 $ | −2 734 $ |
| V2-F incertitude 0,01 % BTC | V2-F 0,01 % (H1) | 11 | 10.10 12:40 → 10.10 13:40 | 10 | 9 | +114 $ | −0 $ | −228 $ |
| V2-D perp 120-269 s BTC | V2-D perp 120-269 s | 320 | 09.10 00:45 → 10.10 13:40 | 300 | 299 | +358 $ | −1 405 $ | −1 013 $ |
| V2-G jury des bourses BTC | V2-G jury des bourses | 362 | 09.10 01:30 → 10.10 13:40 | 347 | 340 | +416 $ | +1 338 $ | −109 $ |

**Le rejeu ne reproduit pas le fantôme réel** sur V2-D et V2-G (écarts de 1 000 à 1 800 $ sur les mêmes cycles) : instants et prix de décision différents entre le bot en direct et les lignes enregistrées 0,3 s. Toute conclusion de rejeu est donc une SIMULATION, pas le résultat du bot.
Les fantômes réels ne couvrent que le 09.10-10.10 (le fichier V2-F 0,01 % seulement le 10.10 de 12:40 à 13:45, 11 trades) : ils servent de contrôle, pas d'échantillon. Désaccord 30 / désaccord 20 60-180 s / jeton 0,35-0,65 n'ont pas de fantôme réel avec exactement la même règle.
