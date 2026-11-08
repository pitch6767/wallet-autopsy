# Bot95 — H1093 : divergence du delta cumulé (CVD) du perp Bybit sur 60 s

08.11.2026. Idée tirée de zadescoxp/order-flow-screener (« CVD and price change with a divergence flag »). Aucun ordre, production inchangée.

**Hypothèse (écrite avant calcul)** : quand, sur les 60 s avant la décision, le delta cumulé du perp Bybit (achats agressifs − ventes agressives)
part à l'opposé du prix Bybit, et qu'il est fort (|CVD| ≥ médiane de l'apprentissage, ≈ 241 000 $), acheter sur Polymarket le côté indiqué
par le flux rapporte après frais.

**Données** : signaux seconde par seconde de bot95 (07.10 → 08.11, 2,57 M secondes), achat au meilleur vendeur Polymarket à la seconde
de décision (taille disponible respectée, écart > 1 c = pas d'achat), mise 50 $, frais 0,072·p·(1−p) par part, règlement officiel Polymarket
(base Wallet Autopsy, identique à officiels.json sur 2 271 marchés). Apprentissage 07–12.10 (seuil seulement), jugement 13.10 → 08.11.
Essais : 2 (T−60 s principal, T−30 s secondaire). Script : h1093_divergence_delta.py ; chiffres : h1093_resultat.json.

| Variante | Trades | Gain net $ | Gain/jour $ | Creux max $ | Mise max par cycle $ | IC 95 % (par jours) | Tient sur les périodes inédites ? | Go / Non |
|---|---|---|---|---|---|---|---|---|
| H T−60 s : divergence, côté du flux | 349 | +1 217 | +47 | −1 253 | 50 | −2 665 ; +6 550 | non : −141 / +252 / +1 662 / −556 | **Non** |
| H T−30 s : divergence, côté du flux | 91 | +103 | +4 | −870 | 50 | −1 178 ; +2 215 | non : −263 / −101 / +487 / −20 | **Non** |
| nul A T−60 : divergence, côté du prix | 346 | +22 | +1 | −1 018 | 50 | −2 157 ; +2 384 | — | — |
| nul C T−60 : flux fort et prix d'accord | 887 | −2 750 | −103 | −3 382 | 50 | −5 469 ; +73 | — | — |

Côté tiré au hasard sur les mêmes moments (500 tirages) : fait au moins aussi bien que H dans 46 %, 44 %, 38 % et 67 % des cas selon la période.

**Échelon atteint : « ne bat pas le hasard ».** Le gain de T−60 vient presque entièrement de la période 27.10–02.11 (quelques billets bon marché
gagnants) ; deux périodes sur quatre sont négatives, l'intervalle de confiance contient zéro, et un côté choisi au hasard fait aussi bien.
Note : la version « dans le sens du flux quand le prix est d'accord » (nul C) perd (−2 750 $), ce qui confirme que l'élan du perp
déjà retenu dans bot95 ne vaut qu'avec ses propres filtres.
