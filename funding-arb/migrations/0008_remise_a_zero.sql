-- 18.11.2026 : correction du suivi des écarts permanents (toutes les paires de plateformes) — le faux trade LIT validé par erreur est effacé
DELETE FROM comptant;
DELETE FROM comptant_pos;
DELETE FROM ecarts_suspects;
