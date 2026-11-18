-- 18.11.2026 : arbitrage au comptant (fantôme), à côté des perpétuels (choix de Pitch : D, garder les deux)
CREATE TABLE IF NOT EXISTS comptant (id INTEGER PRIMARY KEY AUTOINCREMENT, t INTEGER, cle TEXT, base TEXT, quote TEXT,
  achat_ex TEXT, vente_ex TEXT, qte REAL, px_achat REAL, px_vente REAL, frais REAL, net REAL);
CREATE INDEX IF NOT EXISTS comptant_t ON comptant (t);
