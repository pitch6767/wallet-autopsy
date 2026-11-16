-- 16.11.2026 : règles 2.1 (même quantité de pièces sur les 2 jambes) — les positions ouvertes sous les anciennes règles gardent leurs quantités d'origine
ALTER TABLE positions ADD COLUMN qte_l REAL;
ALTER TABLE positions ADD COLUMN qte_s REAL;
ALTER TABLE positions ADD COLUMN regles TEXT;
UPDATE positions SET qte_l = notional / px_l_in, qte_s = notional / px_s_in WHERE qte_l IS NULL;
