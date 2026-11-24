-- Solamente se almacenan métricas anónimas, nunca el texto comparado.
CREATE TABLE IF NOT EXISTS analyses (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  score REAL NOT NULL CHECK (score BETWEEN 0 AND 100),
  words_a INTEGER NOT NULL,
  words_b INTEGER NOT NULL,
  matched_a INTEGER NOT NULL,
  matched_b INTEGER NOT NULL,
  window_size INTEGER NOT NULL,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_analyses_created ON analyses(created_at DESC);
