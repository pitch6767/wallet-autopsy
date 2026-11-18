-- 18.11.2026 : un écart suspect n'est effacé que si les 2 plateformes ont été lues et qu'il a disparu depuis 60 s (défaut relevé par le contrôleur)
ALTER TABLE ecarts_suspects ADD COLUMN vu INTEGER;
