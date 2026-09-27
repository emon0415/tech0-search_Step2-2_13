

CREATE TABLE IF NOT EXISTS pages (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    url     TEXT NOT NULL UNIQUE,
    title   TEXT NOT NULL,
    description     TEXT,
    full_text       TEXT,
    author          TEXT,
    category        TEXT,
    keywords        TEXT,
    word_count      INTEGER DEFAULT 0,
    crawled_at      DATETIME,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_at       DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS keywords(
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    page_id INTEGER NOT NULL,
    keyword TEXT NOT NULL,
    te_score   REAL DEFAULT 0.0,
    tfidf_score REAL DEFAULT 0.0,
    FOREIGN KEY (page_id) REFERENCES pages(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_keyword ON keywords(keyword);
CREATE INDEX IF NOT EXISTS idx_page_id ON keywords(page_id);

