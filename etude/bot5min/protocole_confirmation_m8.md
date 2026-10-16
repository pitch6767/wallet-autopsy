# Bot95 — protocole de confirmation M8 (figé le 16.10.2026, accord de Pitch « fait comme tu dis »)

**Pourquoi** : au verdict hors échantillon complet (13.10 → 16.10, rapport_verdict_hors_echantillon_bot95_complet.md), M8 hybride est la seule variante dont l'IC 90 % du P&L net est au-dessus de 0 (+10 647 $, IC [+738 ; +20 788]). Mais une quinzaine de variantes étaient jugées ensemble et M8 perdait avant le 13.10 : il faut une confirmation sur des cycles jamais vus.

**Période de confirmation** : cycles BTC 5 min commençant entre le 16.10.2026 08:00 UTC (1792137600) et le 19.10.2026 08:00 UTC (1792396800), exclu.

**Données et calcul** : exactement ceux du verdict complet — offres de bot95/rapide_maker.json(.gz) (sauvegarde), mêmes fonctions de simulation prudente, IC 90 % par blocs, sélection adverse et creux (etude/bot5min/verdict_hors_echantillon_bot95.py, groupes exacts), aucun paramètre changé.

**Critère (décidé maintenant)** : M8 est confirmé si son P&L net sur la période a un IC 90 % par blocs entièrement > 0. Sont aussi rapportés, sans critère : M8b, M0 (témoin), FAST, HYBRID, C.

**Décisions prises en même temps (16.10.2026)** : makers passifs arrêtés (M1, M2, M3, M4 a/b/c, M5, M6, M10) ; M0, M8, M8b, M9, M21 continuent ; FAST, HYBRID, C observés sans argent ; aucun argent réel ; un ordre test de 1 $ seulement sur autorisation de Pitch.
