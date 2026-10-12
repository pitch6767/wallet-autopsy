# Bot95 — synthèse complète (état au 12.10.2026, 08:15 heure suisse)

Ce fichier est **le point d'entrée unique** : tout ce qui a été fait sur Bot95 y est résumé, avec un lien vers le détail.
- Les 143 études : [INDEX_ETUDES.md](INDEX_ETUDES.md)
- Les résultats de tous les fantômes : [RESULTATS_FANTOMES_12-10.md](RESULTATS_FANTOMES_12-10.md)
- Les rapports envoyés à Pitch et les PDF : [archives/](archives/)

**Mode : argent fictif uniquement. MODE_REEL = non. Aucun ordre réel n'a jamais été passé.**

---

## 1. Le bot en deux phrases

Bot95 cherche à gagner sur les marchés Polymarket « BTC monte ou baisse en 5 minutes ». Il compare sa propre probabilité (calculée à partir des prix des bourses et de Chainlink) au prix Polymarket, et simule un achat quand l'écart est grand. Tout se fait en **fantôme** : chaque stratégie note ce qu'elle aurait acheté, au vrai prix et dans la vraie quantité affichés, frais compris, puis le résultat au règlement.

**Règlement d'un marché.** Le prix à battre est la moyenne Chainlink des 60 s avant le début. Le prix final est la moyenne Chainlink des 60 dernières secondes.

## 2. Les deux parties du bot

| Partie | Où | Rôle |
|---|---|---|
| **Bot Cloudflare** (bot95) | Cloudflare Workers, dépôt pitch6767/wallet-autopsy, dossier bot95/ | Le bot « historique » : 127 stratégies fantômes, pages de suivi. Achats fantômes de 50 $ au maximum. |
| **Laboratoire de Dublin** (rapide.js) | VPS de Dublin, 107.174.203.201 (installé par Replit) | Version rapide (~9 ms de Polymarket). Mesure ce qu'on aurait vraiment pu acheter 1 ms à 2 s après chaque signal. Fantômes R4, makers M1 à M21, cohortes A/B. Se met à jour tout seul depuis le dépôt. |

Le 11.10, Pitch a décidé de garder Cloudflare comme bot existant et Dublin comme laboratoire : aucune modification de stratégie en production.

## 3. Liens

**Pages du bot**
- Page principale : https://bot95.pitch67.workers.dev/
- Tous les fantômes, classés : https://bot95.pitch67.workers.dev/nouveaux
- Rapport : https://bot95.pitch67.workers.dev/rapport
- État (données brutes) : https://bot95.pitch67.workers.dev/api/etat
- Fantômes (données brutes) : https://bot95.pitch67.workers.dev/api/nouveaux
- Laboratoire de Dublin (données brutes) : https://bot95.pitch67.workers.dev/api/rapide
- Serveur de Dublin : https://107.174.203.201.sslip.io/bot

**Dépôt GitHub**
- Code et études : https://github.com/pitch6767/wallet-autopsy/tree/main/etude/bot5min
- Code du bot : https://github.com/pitch6767/wallet-autopsy/tree/main/bot95
- Données de Dublin (carnets cycle par cycle) : https://github.com/pitch6767/wallet-autopsy/tree/donnees-rapide
- Données des makers : https://github.com/pitch6767/wallet-autopsy/tree/donnees-makers
- Tâches automatiques : https://github.com/pitch6767/wallet-autopsy/actions

## 4. Règles posées par Pitch (toujours en vigueur)

**Sécurité**
1. Aucun ordre réel. MODE_REEL reste « non ».
2. Ne modifier aucun bot actif ni fantôme gelé (R4, H816, fantômes).
3. Aucun nouveau fantôme sans l'accord de Pitch. Aucun déploiement automatique.
4. Les clés de portefeuille vivent seulement dans les secrets GitHub, jamais dans le dépôt.

**Méthode** (posée le 10.10)
5. Une hypothèse précise, un test rigoureux, un verdict chiffré sur des journées inédites.
6. Ce qui compte : le bénéfice net, avec un creux supportable et une exécution réaliste.
7. Pré-enregistrer protocole et code sur GitHub avant tout calcul de validation.
8. Découpage chronologique. Intervalles de confiance par cycle. Correction pour comparaisons multiples.
9. Ne jamais annoncer une rentabilité démontrée si l'intervalle contient zéro.
10. **Période réservée** : les cycles à partir du 13.10.2026 00:00 UTC ne servent jamais à choisir une règle, seulement au verdict.

**Données et fonctionnement**
11. On n'invente aucun prix : tous les prix viennent de Polymarket. Le prix d'exercice est celui publié par Polymarket.
12. Claude propose, Pitch décide. Ordre d'escalade : Claude, puis Replit, puis Pitch.

## 5. Chronologie

| Date | Étape |
|---|---|
| 04.10 | Idée de départ : acheter le favori à 95–99 c dans les dernières secondes. Sur 14 jours simulés, 99 % de réussite. Avec les achats réellement vus : +34 $ seulement. La couverture Limitless est abandonnée. |
| 05.10 | V1 (paires, élan) : très positive en simulation sans retard, beaucoup moins avec 1–2 s de retard. Arbitrage 15 min / 5 min : quelques $ par jour. Kronos : aucun apport. |
| 06–07.10 | Famille « désaccord » : le modèle dépasse le prix de 10, 20 ou 30 points. Moteurs V2 (B à H), V5, V6. ETH abandonné le 07.10. Autopsie de portefeuilles (stingo43). |
| 08.10 | « Zone » : désaccord ≥ 30 points sur un jeton entre 0,15 et 0,35, avec filtres Binance/perp et sortie −10. C'est la famille la plus stable. |
| 09.10 | Prix à battre exact (moyenne Chainlink), moteur « TWAP fin ». Audit du modèle : **le prix Polymarket est mieux calibré que notre modèle**. |
| 10.10 | Remise à zéro de tous les fantômes à 13:50. V3 : aucune piste ne survit en exécution réaliste. Les signaux « morts à l'arrivée » (41 % à 1 s) expliquent la chute des gains. |
| 11.10 | Laboratoire de Dublin (164 ms mesurés). Études H724 à H821 : latence, relances R4, makers, sauvetage, exécution, calibration. Protocoles H816 et H821 figés. |
| 12.10 | Cette synthèse. |
| **14.10** | **Verdicts sur la période réservée** (voir §8). |

## 6. Ce qu'on sait — les conclusions qui comptent

**Démontré**
- **Notre modèle est moins bien calibré que le prix Polymarket.** Ses erreurs de prévision sont plus grandes (Brier 0,217 contre 0,206 sur 144 décisions ; 0,201 contre 0,152 en V3). Il surestime ses chances de 13 à 20 points, surtout à moins de 2 minutes de la fin (il annonce 45 %, on gagne 14 %).
- **La vitesse est décisive.** À 1 s, 41 % des signaux sont déjà morts. Les offres qui disparaissent sont celles qui auraient gagné : +20 points de taux de gain, IC [+12 ; +28].
- **L'avantage fond en une seconde**, et c'est le prix du marché qui rejoint le modèle (99 %).
- **Chainlink suit les bourses avec retard** : il rattrape 24 % de l'écart en 1 s, 80 % en 5 s, 95 % en 10 s.
- **Le prix à battre affiché par Polymarket est faux** dans 11 % des cycles (erreur médiane de 10 $). Le bot recalcule le vrai.
- **Les longues séries de pertes sont normales** : une série de 25 pertes arrive dans 10 % des simulations quand on gagne 24 % des trades.
- **Couvrir avec la jambe inverse revient exactement à vendre** (carnets miroirs).

**Le meilleur résultat, mais pas démontré**
- **H816** : une décision par cycle et par côté, prix de 0,20 à 0,50, 20 $ par décision, exécution à 164 ms. Avant le 13.10 : 64 décisions, +283 $ (+28 % par $ engagé), IC [−9 % ; +67 %]. Sans ses 5 meilleurs trades, le test est négatif.
- **H821** (H816 sans les signaux où Chainlink est déjà du bon côté) : +139 $ sur le test et 0 jackpot perdu. La règle a été choisie parmi 38.

**Abandonné (négatif ou rien de mieux)**
- Identité des portefeuilles comme signal : veto des 3 wallets, Bot95 inversé.
- Toute la piste maker (M1 à M21) : tous négatifs, même avec une annulation rapide.
- Relances R4 : en direct, elles ne font pas mieux que l'achat immédiat (§7).
- Sauvetage, stop, ventes par paliers, couverture : rien ne bat le fait de garder jusqu'au règlement.
- Routeurs, méta-modèles, Kronos, arbitrage 15/5 min, paires, filtres d'exécution H818.
- Supports, résistances et figures de liquidité (H822–H832, 12.10) : les anciens sommets et creux rejettent même moins que des niveaux fictifs, les figures n'ajoutent rien au modèle de règlement, et le meilleur veto n'est pas démontré. Marge de sécurité utile : environ 1,9 σ pour 90 % de victoires et 2,6 σ pour 95 %.

**Où se perd l'argent.** Ce n'est pas l'exécution : 94 % des ordres passent, sans remplissage toxique, et la profondeur suffit jusqu'à 100 $. C'est **le choix des billets** : le gain moyen repose sur quelques jackpots, et la médiane est négative.

## 7. Résultats actuels des fantômes (12.10, ~08:00)

Le détail complet est dans [RESULTATS_FANTOMES_12-10.md](RESULTATS_FANTOMES_12-10.md).

**Bot Cloudflare, depuis la remise à zéro du 10.10 13:50**
- 49 stratégies, total **−15 641 $**, 19 positives.
- Sur toutes les 127 stratégies, anciennes comprises : total −102 668 $.
- Les meilleures ci-dessous ne prouvent donc rien : sur 49 stratégies, le hasard en fait gagner plusieurs.

| Stratégie | Trades | Gagnés | Résultat |
|---|---|---|---|
| désaccord 30 | 402 | 65 | +1 548 $ |
| désaccord 20 Binance ou perp avec nous | 65 | 25 | +1 224 $ |
| désaccord 30 zone + modèle monte | 107 | 37 | +940 $ |
| corrigé : zone + Binance et perp + sortie −10 | 109 | 33 | +773 $ |
| V2-F incertitude 0,01 % | 356 | 122 | +748 $ |

Le désaccord 20 fait +1 998 $ sur 761 trades, mais il compte depuis le 06.10.

Lecture des colonnes de la page /nouveaux :
- **« Pertes totales »** : la somme de tous les trades perdants, pas une série.
- **« Creux max »** : la plus grosse baisse depuis un sommet. C'est ce chiffre qui mesure le risque.
- **« Capital conseillé »** : 2 × le creux + 2 mises.

**Laboratoire de Dublin, 11.10 08:50 → 12.10 04:50** (achat 250 ms après le signal)

| Fantôme | Signaux | Gagnés | Résultat |
|---|---|---|---|
| désaccord 30 | 158 | 30 | +1 525 $ |
| désaccord 20 60–180 s | 185 | 40 | +1 051 $ |
| V2-F écart qui grandit | 191 | 50 | +997 $ |
| cohorte B : V2-F corrigé 0,015 % | 130 | 57 | +695 $ |

**Fantôme R4 (relances), 11.10 17:35 → 12.10 04:50, sans doublons**

| Variante | Trades | Capital engagé | Résultat |
|---|---|---|---|
| Achat immédiat, sans relance | 212 | 7 249 $ | +1 093 $ |
| R4 | 224 | 10 279 $ | +1 086 $ |
| R4 au prix initial | 219 | 9 162 $ | +259 $ |

## 8. Protocoles figés et calendrier

| Quand (heure suisse) | Quoi | Protocole |
|---|---|---|
| 12.10, 20:00 | Diagnostic FAST / maker / Chainlink (pas un verdict) | — |
| 14.10, 08:00 | Verdict sur journées inédites : combinaison D, robustesse E, variantes V2-F | — |
| **14.10, 09:30** | **Verdicts H816, H816 + H821, calibration** sur la période réservée, lancés une seule fois | commits 56ef5e2 et 9f2eabf |
| 14.10, 10:00 | Queue Race phases 3 à 6 | — |
| 15.10, 19:00 | Verdict makers / FAST sur la période réservée | — |

**Critères validés par Pitch le 11.10 à 22:06**
- **H821** : la différence de P&L avec H816 doit avoir un IC 90 % par cycle entièrement positif.
  - Seuil figé à −0,0904552. Un signal exclu n'est pas remplacé. Une donnée manquante exclut le signal, et ces cas sont comptés à part.
  - En cas d'échec : abandon, sans retoucher le seuil.
- **Calibration** : une calibration apprise avant le 13.10 doit battre le prix du marché (Brier, IC corrigé pour 3 essais).
- **Le rapport donnera** :
  - les décisions conservées et exclues, et le P&L des exclues ;
  - le P&L marginal avec son IC ;
  - les jackpots et les gagnants supprimés, et les exclusions dues à des données manquantes ;
  - les résultats à 164, 200, 250 et 500 ms ;
  - le Brier et la log loss ;
  - deux conclusions séparées : qualité des probabilités, puis rentabilité.

## 9. Pistes en attente

- H717, M22 et M23 ne sont pas terminés. Pour M23, l'activité du portefeuille 0x56f609c6 n'a pas été collectée.
- **Source Chainlink** : changer CHAINLINK_SOURCE avant le ~23.10, sur proposition et avec l'accord de Pitch.
- Correctif du mode cache du bot Cloudflare : à appliquer seulement avec l'accord de Pitch.
- Validation en direct B0/B1 : elle tourne chaque heure. À ce jour, aucune amélioration n'est retenue.
- Idée pour plus tard : partir du prix du marché comme probabilité, puisqu'il est mieux calibré, dans un protocole nouveau et séparé.

## 10. Données et outils

**Données**
- Branche `donnees-rapide` : un fichier par cycle (cycles/AAAA-MM-JJ/<début>.json.gz). Il contient le carnet complet Up toutes les 10 s, les changements à ±3 c, les transactions des deux côtés, les prix perp / OKX / Binance / Coinbase / Chainlink toutes les 50 ms et le prix à battre.
- `bot95/rapide.json` : tous les signaux de Dublin, avec ce qui était achetable de 1 ms à 2 s et le résultat.
- `bot95/sauvegarde/` : un fichier par stratégie Cloudflare, avec tous ses trades. Sauvegarde toutes les 30 min (le cron GitHub est irrégulier ; on peut la lancer à la main).

**Briques de calcul** (dans etude/bot5min/)
- `latence_h766.py` : rejouer le carnet à n'importe quelle milliseconde.
- `modele_dublin.py` : recalculer la probabilité du bot.
- `robustesse_bot95.py` : H816.
- `validation_h821.py` : H821.
- `calibration_bot95.py` : calibration.

**Exécution.** Délai preneur Polymarket : 150 ms selon le changelog du 04.09.2026 ; une page de la documentation dit encore 250 ms. Nous utilisons 164 ms (150 + 14 ms de trajet). Un ordre preneur ne peut pas être annulé pendant ce délai. Frais preneur : 0,07 × p × (1 − p).

## 11. Archives

- [archives/rapports/](archives/rapports/) : les 51 rapports en français envoyés à Pitch (états du bot, H724 à H821, TWAP, V2-F, V3…).
- [archives/pdf/](archives/pdf/) : les 53 PDF envoyés pour ChatGPT.
- [archives/outils/md2pdf.py](archives/outils/md2pdf.py) : le convertisseur des rapports en PDF.
