-- 19.11.2026 : « Oui remet tous à 0 » (Pitch) — tous les trades et positions du comptant effacés, anciennes positions bloquées comprises
DELETE FROM comptant;
DELETE FROM comptant_pos;
DELETE FROM ecarts_suspects;
