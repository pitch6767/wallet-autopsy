# Bot95 — Penchant de l'inventaire des makers (H712, H714, H718) — PRÉLIMINAIRE

Généré le 11.10.2026 14:15 UTC. FAITS : exécutions de l'API Data. INFÉRENCES : interprétation. Aucune valeur future n'entre dans le penchant ni dans le prix de référence.

## 1. Audit des données collectées

- Marchés collectés (avant la période réservée) : **300**, du 10.10 12:25 au 11.10 13:20 UTC.
- Marchés complets (< 10 000 exécutions) : **212** ; encore tronqués (≥ 10 000, plafond de l'API) : **88** — isolés, exclus des résultats.
- Dont marchés entre 4 000 et 10 000 exécutions (récupérés grâce au nouveau plafond) : 0.
- Exécutions : 987482 ; doublons exacts : 63712 ; valeurs incohérentes (prix, taille, issue, côté) : 0 ; horodatages hors du marché (±10 min) : 728.
- Rôles : 328093 lignes preneur, 659389 lignes maker (un même preneur peut être servi par plusieurs makers).
- Horodatages : à la seconde (API Data). Jetons : issue « Up » / « Down » lue dans chaque exécution ; gagnant lu dans Gamma (prix final 1).
- Activité (fusions, séparations, règlements, récompenses) : pas encore lue dans ce fichier.
- Au-delà de 10 000 exécutions : aucune pagination supplémentaire de l'API Data ; seule une reconstruction par la blockchain (sous-graphe OrderFilled, refusé pour l'instant : 429) le permettrait.
- Une réponse de 10 000 lignes n'est jamais supposée complète (marché marqué tronqué).

## 2. Penchant de l'inventaire au fil du cycle (H712)

Makers retenus (≥ 10 marchés complets, ≥ 70 % de volume maker, ≥ 2 500 $ sur la 1re moitié) : 103 ; gagnants (≥ +1 %/$) : 55 ; perdants (≤ −0,5 %/$) : 21. **Classement fait sur la 1re moitié chronologique des marchés (avant le 11.10 01:45 UTC), penchant mesuré sur la 2e moitié uniquement** (sinon « gagnant » et « bon penchant » seraient la même chose).

Précision = part des cycles où le côté surpondéré à t est le gagnant final. Valeur au-delà du marché = Σ résiduel × (résultat − prix implicite à t) / Σ capital résiduel au prix de t (0 attendu sans information ; >0 = le penchant anticipe mieux que le prix du marché à ce moment).

| Groupe | 30 s | 60 s | 90 s | 120 s | 150 s | 180 s | 210 s | 240 s | 270 s | 299 s |
|---|---|---|---|---|---|---|---|---|---|---|
| gagnants | 54 % / -1.1 % | 54 % / +1.1 % | 57 % / +2.4 % | 59 % / +2.5 % | 62 % / +0.8 % | 64 % / +2.5 % | 66 % / +0.2 % | 68 % / +0.1 % | 69 % / +0.5 % | 70 % / +0.4 % |
| perdants | 41 % / -18.4 % | 42 % / -14.8 % | 42 % / -13.7 % | 42 % / -11.2 % | 43 % / -7.7 % | 43 % / -5.8 % | 43 % / -4.2 % | 44 % / +1.5 % | 44 % / -1.3 % | 44 % / -0.6 % |
| autres makers | 52 % / -6.4 % | 50 % / -4.4 % | 54 % / -5.1 % | 52 % / -5.1 % | 52 % / +0.3 % | 52 % / -1.5 % | 53 % / -1.9 % | 49 % / +3.2 % | 49 % / -1.0 % | 49 % / -0.4 % |
| témoin (sens au hasard) | 51 % / -1.3 % | 49 % / -1.9 % | 49 % / -3.0 % | 50 % / -1.4 % | 49 % / -1.0 % | 50 % / +0.4 % | 51 % / -0.4 % | 51 % / -0.0 % | 50 % / +0.0 % | 51 % / +0.0 % |

(chaque case : précision / valeur au-delà du marché par $ de résiduel)

**Valeur au-delà du marché pondérée par le capital, intervalles à 90 % (rééchantillonnage) à 60, 120 et 240 s** :

- gagnants : 60 s : +1.1 % [-2.8 ; +5.1] ; 120 s : +2.5 % [-0.2 ; +5.1] ; 240 s : +0.1 % [-1.1 ; +1.4]
- perdants : 60 s : -14.8 % [-22.0 ; -7.2] ; 120 s : -11.2 % [-17.3 ; -5.1] ; 240 s : +1.5 % [-2.0 ; +5.2]
- témoin (sens au hasard) : 60 s : -1.9 % [-4.9 ; +1.3] ; 120 s : -1.4 % [-3.7 ; +1.0] ; 240 s : -0.0 % [-1.3 ; +1.2]

## 3. Avance du penchant sur le marché (H714)

Délai = premier instant où le penchant (|tilt| ≥ 0,2) est du côté gagnant − premier instant où le favori du marché (prix implicite > 0,5) est le gagnant. Négatif = le portefeuille était du bon côté AVANT que le marché le donne favori. Distribution (p10 / p25 / médiane / p75 / p90) en secondes.

- gagnants (3073 portefeuille-marchés) : -30 / 0 / 0 / 0 / 60 ; part négative (avance) 15 %, nulle 66 %
- perdants (718 portefeuille-marchés) : -60 / 0 / 0 / 0 / 30 ; part négative (avance) 24 %, nulle 63 %
- autres makers (1472 portefeuille-marchés) : -60 / 0 / 0 / 0 / 60 ; part négative (avance) 16 %, nulle 64 %

Limite : seuls le prix Polymarket et le résultat sont disponibles pour tous les marchés ; la probabilité Bot95, la distance Chainlink et le BTC ne le sont que pour les cycles enregistrés à Dublin (étude séparée).
