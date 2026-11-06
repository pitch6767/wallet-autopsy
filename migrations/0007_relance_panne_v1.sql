-- Marchés en échec définitif pendant la panne de l'API Polymarket v1 (02.11 → 07.11.2026, réponse 410) : on les remet en file
UPDATE markets SET statut = 0, essais = 0, erreur = NULL WHERE statut = 9 AND erreur LIKE '%410%';
