-- Repart de zéro avec le code qui calcule tous les indicateurs
DELETE FROM stats;
UPDATE markets SET statut = 0, essais = 0, erreur = NULL;
UPDATE meta SET v = '0' WHERE k = 'verrou';
