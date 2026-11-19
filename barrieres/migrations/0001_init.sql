CREATE TABLE IF NOT EXISTS releves (
  t INTEGER, actif TEXT, sens TEXT, niveau REAL, fin INTEGER, token_yes TEXT,
  yes_bid REAL, yes_ask REAL, no_ask REAL, spot REAL, echeance TEXT, decalage_h REAL,
  k_bas REAL, k_haut REAL, iv REAL, p_modele REAL, p_options REAL, cout_couv REAL,
  net_achat REAL, net_vente REAL
);
CREATE INDEX IF NOT EXISTS releves_t ON releves(t);
CREATE TABLE IF NOT EXISTS positions (
  id INTEGER PRIMARY KEY AUTOINCREMENT, ouvert INTEGER, actif TEXT, sens TEXT, niveau REAL, fin INTEGER,
  token_yes TEXT, cote TEXT, parts REAL, px_poly REAL, frais_poly REAL,
  echeance TEXT, k_bas REAL, k_haut REAL, contrats REAL, prime_couv REAL, frais_couv REAL,
  net_attendu REAL, statut TEXT DEFAULT 'ouverte', ferme INTEGER, raison TEXT,
  poly_sortie REAL, couv_sortie REAL, net REAL, retard_min REAL, spot_entree REAL, spot_sortie REAL
);
CREATE TABLE IF NOT EXISTS etat (cle TEXT PRIMARY KEY, valeur TEXT);
