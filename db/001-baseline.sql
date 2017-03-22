CREATE TABLE IF NOT EXISTS expenditure_application(
  id INTEGER PRIMARY KEY,
  title TEXT NOT NULL,
  subtotal INTEGER NOT NULL,
  freight INTEGER NOT NULL,
  comment TEXT,
  created_at INTEGER NOT NULL,
  approved_at INTEGER,
  rejected_at INTEGER,
  ps TEXT
);

CREATE TABLE IF NOT EXISTS expenditure_application_item(
  id INTEGER PRIMARY KEY,
  application_id INTEGER NOT NULL REFERENCES expenditure_application,
  title TEXT NOT NULL,
  link TEXT,
  price INTEGER NOT NULL,
  quantity INTEGER NOT NULL,
  discount INTEGER NOT NULL DEFAULT 0,
  total INTEGER NOT NULL
);