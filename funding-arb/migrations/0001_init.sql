CREATE TABLE IF NOT EXISTS paires (base TEXT PRIMARY KEY, short TEXT, long TEXT, depuis INTEGER, maj INTEGER);
CREATE TABLE IF NOT EXISTS positions (
  id INTEGER PRIMARY KEY AUTOINCREMENT, base TEXT, short TEXT, long TEXT, notional REAL,
  ouvert INTEGER, ferme INTEGER, px_s_in REAL, px_l_in REAL, px_s_out REAL, px_l_out REAL,
  fund REAL DEFAULT 0, frais REAL DEFAULT 0, rate_s REAL, rate_l REAL, next_s INTEGER, next_l INTEGER,
  cont_s INTEGER, cont_l INTEGER, dernier INTEGER, cout_est REAL, spread_in REAL, net REAL,
  statut TEXT, raison TEXT, last_s_bid REAL, last_s_ask REAL, last_l_bid REAL, last_l_ask REAL, vu INTEGER);
CREATE TABLE IF NOT EXISTS etat (id INTEGER PRIMARY KEY, t INTEGER, json TEXT);
