# Bot95 — verdict de la confirmation M8 (protocole figé le 16.10.2026)

Période figée : cycles BTC 5 min du 16.10.2026 08:00 au 19.10.2026 08:00 UTC (809 cycles avec offres réglées, dernier cycle 19.10 07:55 UTC). Données : sauvegarde bot95/rapide_maker.json du 19.10, fonctions de verdict_hors_echantillon_bot95.py inchangées (résultat prudent, IC 90 % par blocs de cycles). Remplissages simulés, aucun ordre réel, aucun fantôme modifié.

> **Critère décidé le 16.10 : M8 est confirmé si l'IC 90 % de son P&L net est entièrement au-dessus de 0. Verdict : NON confirmé.** M8 perd −12 185 $, IC 90 % [−23 030 ; −339] : la perte est même démontrée sur cette période.

## Résultats (période de confirmation)

| Variante | Remplissages | Résultat prudent | IC 90 % | Creux |
|---|---|---|---|---|
| **M8 hybride (critère)** | 1 874 | **−12 185 $** | [−23 030 ; −339] | −12 768 $ |
| M8b routeur corrigé (info) | 1 853 | −12 233 $ | [−23 011 ; −463] | −13 391 $ |
| M0 témoin aléatoire (info) | 1 024 | −5 389 $ | [−9 503 ; −1 087] | −5 902 $ |
| FAST preneur (info) | 2 429 trades | −10 092 $ | [−20 029 ; −113] | −12 143 $ |
| HYBRID preneur (info) | 2 468 trades | −11 043 $ | [−20 795 ; −1 109] | −13 028 $ |
| SLOW preneur (info) | 1 621 trades | −14 421 $ | [−22 858 ; −4 780] | −15 864 $ |
| Moteur C, exécution 300 ms (info) | 213 trades | +1 845 $ | [+38 ; +3 796] | −620 $ |

Les makers arrêtés le 16.10 (M1–M6, M10) ont posé leur dernière offre le **16.10 à 10:09:05 UTC** et **aucune depuis 10:30 UTC** : l'arrêt fonctionne. Leurs quelques remplissages de la période (M1 45, M2 133+139, M4 171, M5 315, M10 247…) datent tous de 08:00–10:09 UTC le 16.10.

## Lecture

- **M8** gagnait +10 647 $ du 13 au 16.10 ; sur les 3 jours suivants, jamais vus, il perd −12 185 $. L'avantage n'a pas tenu : **il ne faut pas passer M8 en argent réel.**
- **M8b, FAST, HYBRID, SLOW** perdent aussi nettement sur la période.
- **Moteur C** est le seul positif (+1 845 $, IC juste au-dessus de 0). Ce n'était pas le critère du protocole et plusieurs variantes étaient regardées en même temps : c'est un candidat à confirmer avec son propre protocole figé, pas une preuve.
