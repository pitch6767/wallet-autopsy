-- 18.11.2026 : un trade LIT validé à tort (l'écart était revenu) est annulé ; règle corrigée : validation seulement si l'écart a disparu et après 5 min
UPDATE comptant SET statut='annulé' WHERE base='LIT' AND statut='validé';
