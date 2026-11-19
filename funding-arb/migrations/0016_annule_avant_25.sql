-- Pitch, 19.11.2026 : annuler les 4 positions ouvertes avant la règle « entrée ≥ 25 $ » (PEPE et PUMP)
UPDATE comptant_pos SET statut='annulé', ferme=CAST(strftime('%s','now') AS INTEGER)*1000, raison='avant règle 25 $' WHERE id IN (96,97,98,99) AND statut='ouvert';
