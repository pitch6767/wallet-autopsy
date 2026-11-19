-- Pitch, 19.11.2026 : « tu les supprimes » — retirer complètement les 4 positions d'avant la règle 25 $ (sinon elles restent affichées en tête des positions fermées)
DELETE FROM comptant_pos WHERE id IN (96,97,98,99) AND statut='annulé' AND raison='avant règle 25 $';
