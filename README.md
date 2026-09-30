# Wallet Autopsy

Profilage de portefeuilles Polymarket, en lecture seule (API publiques, aucune clé).

En ligne : https://wallet-autopsy.pitch67.workers.dev/

- **Portefeuille** : adresse 0x… (+ filtre facultatif sur le titre, ex. « Bitcoin Up or Down »). Par marché : parts et prix moyen de chaque côté, prix combiné des paires, marge figée, fusions, remboursements, rythme des trades.
- **Détenteurs d'un marché** : lien d'une page Polymarket → principaux détenteurs, avec un bouton pour analyser chacun sur ce marché.

Déploiement automatique sur Cloudflare Workers à chaque envoi sur `main`.
