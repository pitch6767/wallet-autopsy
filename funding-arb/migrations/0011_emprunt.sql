-- 19.11.2026 : Pitch « go » — vente à découvert au comptant : la crypto vendue doit être empruntable, intérêts d'emprunt déduits (règles 3)
ALTER TABLE comptant ADD COLUMN interet REAL DEFAULT 0;
ALTER TABLE comptant ADD COLUMN taux REAL;
ALTER TABLE comptant ADD COLUMN regles TEXT;
ALTER TABLE comptant_pos ADD COLUMN interet REAL DEFAULT 0;
ALTER TABLE comptant_pos ADD COLUMN taux REAL;
ALTER TABLE comptant_pos ADD COLUMN regles TEXT;
