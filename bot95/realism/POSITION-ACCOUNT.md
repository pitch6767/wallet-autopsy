# Comptabilité et protection d'un fantôme distinct

Code hors ligne, sans accès réseau, portefeuille, clé ou envoi d'ordre.
Il ne remplace pas le bot officiel et n'est pas branché sur le lanceur du VPS.

## Ce qui est fonctionnel

Une instance PositionAccount correspond à UNE stratégie indépendante et UN cycle.
Les événements order, fill, cancel-request, cancelled et settlement sont journalisés
avant mutation, avec synchronisation disque. Un journal tronqué bloque la reprise.
Les identifiants d'exécution sont idempotents, les conflits bloquent.

Chaque achat consomme le budget de 50 $ du côté concerné, frais inclus. Les ordres
en attente réservent aussi leur coût et leurs frais ; une demande d'annulation
ne libère rien avant confirmation. Les remplissages pendant cette attente comptent.
Les nouvelles entrées sont refusées tant que les quantités sont déséquilibrées.

La protection annule d'abord les entrées encore ouvertes et attend confirmation.
Ensuite elle compare une revente au bid avec un achat du côté opposé à l'ask,
frais explicitement renseignés, profondeur et budget disponibles. Elle ne traite
que la quantité excédentaire. Elle attend les remplissages d'une protection déjà
ouverte au lieu de la remplacer en boucle. Une revente ne recrée pas le budget
d'entrée du cycle.

Le résultat du planificateur est une INTENTION. Seul un événement fill diminue
l'exposition ; une couverture partielle laisse son reliquat visible. Carnet périmé,
frais inconnus ou profondeur absente => position déclarée non couverte.

Le règlement exige closed=true, resolved=true, une preuve et aucun ordre ouvert.
Le résultat inclut achats, ventes, frais et paiement du jeton gagnant. Avant
règlement, netCash est un flux de trésorerie, PAS un PnL valorisé.

## Exécution

node --test position-account.test.cjs position-replay.test.cjs protected-shadow.test.cjs
node position-replay.cjs events.jsonl
node protected-shadow.cjs market-events.jsonl 0

La dernière commande lance la stratégie autonome hors ligne, avec frais maker
explicitement supposés nuls dans cet exemple (pas une affirmation sur les frais
réels). Elle pose une seule paire de quotes de quantités égales, maximum 10 $
par côté à l'entrée, puis recalcule annulation et protection à partir des fills.
Le budget cumulé achats + frais reste plafonné à 50 $ par côté. Les frais taker
doivent figurer dans chaque niveau de carnet ; leur absence bloque.

Ce simulateur utilise des événements book complets Up ET Down, trade
(at, sourceAt, token Up/Down, side SELL/BUY, price, quantity, id facultatif),
clock et settlement. Les arrivées et annulations sont simulées à +100 ms.
Les fills maker utilisent seulement les ventes au prix exact après la file
affichée. Les protections sont des IOC simulés sur un carnet frais à l'arrivée,
avec quantité visible décrémentée. Un passage sous notre prix ne remplit jamais
automatiquement la totalité. Les décisions sont recalculées après chaque événement.

Le fichier JSONL contient des événements chronologiques d'un seul compte.
Les événements book ont at, Up/Down, bid/ask et price, quantity, feePerShare.
Les ordres portent id, side, action buy/sell, quantity, limit, feeReserve, at,
et purpose entry/hedge/exit. Les fills portent id, orderId, quantity, price,
fee, at et evidence.kind simulation ou execution-confirmed.

## Limites importantes

Ce moteur ne génère pas de faux accusés d'exécution. Le moteur de simulation
ou l'import de confirmations doit fournir les événements fill et cancelled,
dans l'ordre de traitement. Les hypothèses de prix/latence/file ne sont pas
calibrées ici. Le journal ne doit être écrit que par un processus.

execution-confirmed est une déclaration de l'importateur, pas une vérification
cryptographique. Une confirmation tardive après cancelled ou settlement exige
une réconciliation : l'import est arrêté, pas silencieusement corrigé.

Ce livrable rend testable la chaîne complète de comptabilité et de décisions.
Il ne signifie PAS que le bot officiel est corrigé ou que son PnL est fiable.
Le moteur est raccordé au fantôme séparé protected-shadow.cjs, avec tests de
couverture partielle et de revente. Le branchement de la collecte continue reste
à effectuer. Les anciennes archives réduites au carnet Up ne doivent pas être
transformées en un faux carnet Down pour alimenter ce moteur.
Les tests utilisent des événements synthétiques, pas une validation sur un marché.
Un arrêt du simulateur ne restaure pas ses files d'attente ni ses jobs en cours ;
une reprise doit recommencer un nouveau cycle, jamais recoller silencieusement
des résultats. Le journal PositionAccount restaure, lui, les événements comptables.
Les frais et latences restent des hypothèses non calibrées ;
aucun déploiement n'est autorisé par ce document.
