-- 18.11.2026 : Pitch « Oui » (A + B + remise à zéro) et deux stratégies : 1) achat/vente instantanés, 2) achat/vente puis clôture quand l'écart s'inverse de 5 ou 10 $
DELETE FROM comptant;
DELETE FROM etat WHERE id IN (2,3);
ALTER TABLE comptant ADD COLUMN statut TEXT DEFAULT 'validé';
CREATE TABLE IF NOT EXISTS ecarts_suspects (cle TEXT PRIMARY KEY, depuis INTEGER);
CREATE TABLE IF NOT EXISTS comptant_pos (id INTEGER PRIMARY KEY AUTOINCREMENT, variante INTEGER, cle TEXT, base TEXT, quote TEXT,
  achat_ex TEXT, vente_ex TEXT, qte REAL, px_achat REAL, px_vente REAL, ouvert INTEGER, entree REAL, frais REAL,
  statut TEXT, ferme INTEGER, px_sortie_vente REAL, px_sortie_achat REAL, net REAL);
