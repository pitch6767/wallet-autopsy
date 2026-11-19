-- 19.11.2026 : cartes de positions — résultat si on fermait maintenant
ALTER TABLE comptant_pos ADD COLUMN sortie_now REAL;
ALTER TABLE comptant_pos ADD COLUMN maj INTEGER;
