ALTER TABLE stats ADD COLUMN px_sniper REAL DEFAULT 0;
ALTER TABLE stats ADD COLUMN g_sniper INTEGER DEFAULT 0;
ALTER TABLE stats ADD COLUMN px_loterie REAL DEFAULT 0;
ALTER TABLE stats ADD COLUMN g_loterie INTEGER DEFAULT 0;
ALTER TABLE stats ADD COLUMN px_dir REAL DEFAULT 0;
-- Les nouveaux indicateurs doivent couvrir tous les marchés : on repart de zéro
DELETE FROM stats;
UPDATE markets SET statut = 0, essais = 0, erreur = NULL WHERE statut IN (1, 2, 9);
