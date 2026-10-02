CREATE TABLE IF NOT EXISTS etudes (
  wallet TEXT PRIMARY KEY, ts INTEGER, copiable INTEGER DEFAULT 0, titre TEXT, marches INTEGER,
  pnl REAL, roi REAL, marge REAL, roi_cible REAL, n_cible INTEGER, score REAL, json TEXT
);
CREATE INDEX IF NOT EXISTS etudes_copiable ON etudes(copiable, score);
