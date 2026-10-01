CREATE TABLE IF NOT EXISTS meta (k TEXT PRIMARY KEY, v TEXT);
INSERT OR IGNORE INTO meta(k,v) VALUES ('verrou','0');
CREATE TABLE IF NOT EXISTS markets (
  cid TEXT PRIMARY KEY, slug TEXT, type TEXT, end_ts INTEGER, gagnant INTEGER,
  statut INTEGER DEFAULT 0, claim_ts INTEGER DEFAULT 0, essais INTEGER DEFAULT 0, erreur TEXT,
  n_trades INTEGER, n_wallets INTEGER, tronque INTEGER DEFAULT 0, traite_ts INTEGER
);
CREATE INDEX IF NOT EXISTS markets_file ON markets(statut, end_ts);
CREATE TABLE IF NOT EXISTS stats (
  wallet TEXT NOT NULL, type TEXT NOT NULL, nom TEXT,
  n_marches INTEGER, n_gagnes INTEGER, cout REAL, pnl REAL, sum_roi REAL, sum_roi2 REAL,
  best_roi REAL, best_pnl REAL, worst_pnl REAL, trades INTEGER,
  deux INTEGER, deux_sous1 INTEGER, sum_combine REAL, n_combine INTEGER,
  sniper INTEGER, loterie INTEGER, dir INTEGER, dir_gagne INTEGER, split INTEGER, last_ts INTEGER,
  PRIMARY KEY (wallet, type)
);
