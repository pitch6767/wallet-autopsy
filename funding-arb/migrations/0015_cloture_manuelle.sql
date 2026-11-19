-- 19.11.2026 : bouton « Clôturer maintenant » et frais de sortie affichés
ALTER TABLE comptant_pos ADD COLUMN frais_sortie_now REAL;
ALTER TABLE comptant_pos ADD COLUMN raison TEXT;
