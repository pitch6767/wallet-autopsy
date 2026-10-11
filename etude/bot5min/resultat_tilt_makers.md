# Bot95 — Penchant de l'inventaire des makers (H712, H714, H718) — PRÉLIMINAIRE

Généré le 11.10.2026 16:51 UTC. FAITS : exécutions de l'API Data. INFÉRENCES : interprétation. Aucune valeur future n'entre dans le penchant ni dans le prix de référence.

## 1. Audit des données collectées

- Marchés collectés (avant la période réservée) : **600**, du 09.10 13:40 au 11.10 15:35 UTC.
- Marchés complets (< 10 000 exécutions) : **595** ; encore tronqués (≥ 10 000, plafond de l'API) : **5** — isolés, exclus des résultats.
- Dont marchés entre 4 000 et 10 000 exécutions (récupérés grâce au nouveau plafond) : 211.
- Exécutions : 2322355 ; doublons exacts : 136625 ; valeurs incohérentes (prix, taille, issue, côté) : 0 ; horodatages hors du marché (±10 min) : 1826.
- Rôles : 776997 lignes preneur, 1545358 lignes maker (un même preneur peut être servi par plusieurs makers).
- Horodatages : à la seconde (API Data). Jetons : issue « Up » / « Down » lue dans chaque exécution ; gagnant lu dans Gamma (prix final 1).
- Activité lue pour 38 portefeuilles : TRADE 144290, REDEEM 12167, MERGE 1702, MAKER_REBATE 37, TAKER_REBATE 17.
- Au-delà de 10 000 exécutions : aucune pagination supplémentaire de l'API Data ; seule une reconstruction par la blockchain (sous-graphe OrderFilled, refusé pour l'instant : 429) le permettrait.
- Une réponse de 10 000 lignes n'est jamais supposée complète (marché marqué tronqué).

## 2. Penchant de l'inventaire au fil du cycle (H712)

Makers retenus (≥ 10 marchés complets, ≥ 70 % de volume maker, ≥ 2 500 $ sur la 1re moitié) : 213 ; gagnants (≥ +1 %/$) : 62 ; perdants (≤ −0,5 %/$) : 109. **Classement fait sur la 1re moitié chronologique des marchés (avant le 10.10 14:30 UTC), penchant mesuré sur la 2e moitié uniquement** (sinon « gagnant » et « bon penchant » seraient la même chose).

Précision = part des cycles où le côté surpondéré à t est le gagnant final. Valeur au-delà du marché = Σ résiduel × (résultat − prix implicite à t) / Σ capital résiduel au prix de t (0 attendu sans information ; >0 = le penchant anticipe mieux que le prix du marché à ce moment).

| Groupe | 30 s | 60 s | 90 s | 120 s | 150 s | 180 s | 210 s | 240 s | 270 s | 299 s |
|---|---|---|---|---|---|---|---|---|---|---|
| gagnants | 54 % / -4.0 % | 53 % / -4.8 % | 54 % / -2.2 % | 55 % / -4.1 % | 56 % / -4.3 % | 58 % / -3.8 % | 58 % / -2.6 % | 59 % / +0.1 % | 61 % / -0.3 % | 62 % / +0.3 % |
| perdants | 48 % / -1.4 % | 48 % / -0.1 % | 49 % / +0.8 % | 49 % / +0.4 % | 51 % / +0.7 % | 52 % / +0.0 % | 52 % / -1.1 % | 54 % / -0.5 % | 54 % / -0.2 % | 54 % / +0.1 % |
| autres makers | 56 % / +5.7 % | 52 % / -1.5 % | 54 % / -0.2 % | 53 % / -0.8 % | 55 % / +0.5 % | 56 % / -0.0 % | 55 % / -0.5 % | 56 % / +0.6 % | 57 % / +0.6 % | 59 % / +0.6 % |
| témoin (sens au hasard) | 50 % / -0.1 % | 49 % / -2.1 % | 50 % / -1.4 % | 50 % / -1.2 % | 50 % / -1.3 % | 49 % / -0.7 % | 50 % / +0.4 % | 50 % / -0.4 % | 49 % / +0.3 % | 50 % / +0.0 % |

(chaque case : précision / valeur au-delà du marché par $ de résiduel)

**Valeur au-delà du marché pondérée par le capital, intervalles à 90 % (rééchantillonnage) à 60, 120 et 240 s** :

- gagnants : 60 s : -4.8 % [-8.0 ; -1.9] ; 120 s : -4.1 % [-7.0 ; -1.3] ; 240 s : +0.1 % [-1.4 ; +1.4]
- perdants : 60 s : -0.1 % [-3.6 ; +3.6] ; 120 s : +0.4 % [-2.4 ; +3.0] ; 240 s : -0.5 % [-1.6 ; +0.6]
- témoin (sens au hasard) : 60 s : -2.1 % [-4.5 ; +0.2] ; 120 s : -1.2 % [-3.1 ; +0.6] ; 240 s : -0.4 % [-1.2 ; +0.5]

## 3. Avance du penchant sur le marché (H714)

Délai = premier instant où le penchant (|tilt| ≥ 0,2) est du côté gagnant − premier instant où le favori du marché (prix implicite > 0,5) est le gagnant. Négatif = le portefeuille était du bon côté AVANT que le marché le donne favori. Distribution (p10 / p25 / médiane / p75 / p90) en secondes.

- gagnants (6736 portefeuille-marchés) : -60 / 0 / 0 / 0 / 60 ; part négative (avance) 18 %, nulle 65 %
- perdants (9110 portefeuille-marchés) : -90 / 0 / 0 / 0 / 33 ; part négative (avance) 22 %, nulle 63 %
- autres makers (4927 portefeuille-marchés) : -90 / 0 / 0 / 0 / 60 ; part négative (avance) 19 %, nulle 63 %

Limite : seuls le prix Polymarket et le résultat sont disponibles pour tous les marchés ; la probabilité Bot95, la distance Chainlink et le BTC ne le sont que pour les cycles enregistrés à Dublin (étude séparée).
