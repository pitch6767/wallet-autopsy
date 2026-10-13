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
couverture partielle et de revente. La collecte continue est fournie par
protected-service.cjs et le service distinct bot95-protected. Les anciennes
archives réduites au carnet Up ne doivent pas être
transformées en un faux carnet Down pour alimenter ce moteur.
Les tests utilisent des événements synthétiques, pas une validation sur un marché.
Un arrêt du simulateur ne restaure pas ses files d'attente ni ses jobs en cours ;
une reprise doit recommencer un nouveau cycle, jamais recoller silencieusement
des résultats. Le journal PositionAccount restaure, lui, les événements comptables.
Les frais et latences restent des hypothèses non calibrées ;
le déploiement du service séparé a été explicitement autorisé par Pitch.

## Service séparé sur le VPS

Le service bot95-protected utilise son propre utilisateur, son propre dossier
/opt/bot95-protected et une copie privée de Node. Il n'écoute sur aucun port.
Il ne modifie pas bot95-rapide, Limitless Pulse, Caddy, le pare-feu ou le Worker.
Les carnets des DEUX jetons et les transactions viennent du WebSocket public CLOB.
Les marchés et résolutions viennent de GET Gamma ; aucun secret n'est chargé.
Les mises à jour des carnets sont ordonnées par niveau de prix et non par un
horodatage global : les niveaux distincts peuvent arriver dans un ordre différent.
Les snapshots conservent les mises à jour de niveaux plus récentes qu'eux.
La connexion est maintenue par un PING toutes les 10 secondes.
Tests complémentaires : node --test public-books.test.cjs.

Le barème crypto_fees_v2 est reconnu explicitement ; un autre barème bloque.
Source consultée : https://docs.polymarket.com/trading/fees, formule
quantité × 0,07 × prix × (1 − prix), maker sans frais. Aucun rebate inventé.
Le délai de 100 ms reste une hypothèse, pas une latence d'ordre mesurée.

data/latest.json : état courant. data/report.json : bilan des cycles réglés
complets seulement, avec les incomplets exclus et les règlements en attente.
Le PnL est null, et non artificiellement zéro, tant qu'aucun cycle n'est admissible.
Chaque cycle conserve son journal comptable et ses événements normalisés,
compressés après clôture et conservés 48 h. Les résumés comptables sont conservés.
L'exposition avant règlement, sa durée et les parts-secondes restent distinctes
du solde final après paiement.

Un démarrage en cours de cycle, une interruption du flux, une rupture de chronologie
ou un print tardif ambigu après annulation exclut le cycle du bilan validé.
« Complet » signifie complet pour ce modèle, jamais preuve d'exécution réelle.

Contrôles : systemctl status bot95-protected ;
journalctl -u bot95-protected --no-pager -n 20.
Arrêt de ce seul fantôme : systemctl stop bot95-protected.
